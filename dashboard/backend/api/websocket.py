"""WebSocket API for real-time metrics streaming.

Provides WebSocket endpoint for streaming:
- Real-time Redis metrics
- Pattern counts
- Memory usage
"""

import asyncio
import json
from datetime import datetime
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..config import Settings, get_settings
from ..services.memory_service import MemoryService, get_memory_service

logger = structlog.get_logger(__name__)

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections and broadcasts.

    Handles multiple concurrent connections and ensures
    graceful cleanup on disconnect.
    """

    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """Accept and register a new connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("websocket_connected", total_connections=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        """Remove a disconnected connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info("websocket_disconnected", total_connections=len(self.active_connections))

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific connection."""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error("websocket_send_failed", error=str(e))
            self.disconnect(websocket)

    async def broadcast(self, message: dict):
        """Broadcast message to all connections."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error("websocket_broadcast_failed", error=str(e))
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_tier1_update(self, update_type: str, data: dict):
        """Broadcast Tier 1 automation monitoring update to all connections.

        Args:
            update_type: Type of update (task_routing, test_execution, coverage, agent_assignment)
            data: Update data to broadcast

        """
        message = {
            "type": "tier1_update",
            "update_type": update_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        await self.broadcast(message)


manager = ConnectionManager()


@router.websocket("/ws/metrics")
async def websocket_metrics(
    websocket: WebSocket,
    service: Annotated[MemoryService, Depends(get_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """WebSocket endpoint for real-time metrics streaming.

    Connection flow:
    1. Client connects to ws://host:port/ws/metrics
    2. Server sends initial metrics immediately
    3. Server sends periodic updates every N seconds (configurable)
    4. Client can send heartbeat/ping messages to keep connection alive

    Message types sent by server:
    - metrics: Real-time metrics update
    - heartbeat: Connection keepalive
    - error: Error notification

    Message types accepted from client:
    - ping: Request immediate metrics update
    - subscribe: Subscribe to specific metric types (future)
    """
    await manager.connect(websocket)

    try:
        # Send initial metrics
        initial_metrics = await service.get_real_time_metrics()
        await manager.send_personal_message(
            {
                "type": "metrics",
                "data": initial_metrics,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            },
            websocket,
        )

        # Start metrics update loop
        update_task = asyncio.create_task(_metrics_update_loop(websocket, service, settings))

        # Listen for client messages
        while True:
            try:
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle client messages
                if message.get("type") == "ping":
                    # Client requested immediate update
                    metrics = await service.get_real_time_metrics()
                    await manager.send_personal_message(
                        {
                            "type": "metrics",
                            "data": metrics,
                            "timestamp": datetime.utcnow().isoformat() + "Z",
                        },
                        websocket,
                    )
                    logger.debug("websocket_ping_received")

            except WebSocketDisconnect:
                logger.info("websocket_client_disconnected")
                break
            except json.JSONDecodeError:
                logger.warning("websocket_invalid_json")
                await manager.send_personal_message(
                    {
                        "type": "error",
                        "message": "Invalid JSON message",
                        "timestamp": datetime.utcnow().isoformat() + "Z",
                    },
                    websocket,
                )
            except Exception as e:
                logger.error("websocket_receive_error", error=str(e))
                break

    except WebSocketDisconnect:
        logger.info("websocket_disconnected_early")
    except Exception as e:
        logger.error("websocket_error", error=str(e))
    finally:
        manager.disconnect(websocket)
        if "update_task" in locals():
            update_task.cancel()


async def _metrics_update_loop(
    websocket: WebSocket,
    service: MemoryService,
    settings: Settings,
):
    """Periodically send metrics updates to connected client.

    Args:
        websocket: WebSocket connection
        service: Memory service instance
        settings: Application settings

    """
    try:
        while True:
            await asyncio.sleep(settings.metrics_update_interval)

            # Get fresh metrics
            metrics = await service.get_real_time_metrics()

            # Send to client
            await manager.send_personal_message(
                {
                    "type": "metrics",
                    "data": metrics,
                    "timestamp": datetime.utcnow().isoformat() + "Z",
                },
                websocket,
            )

            logger.debug("metrics_update_sent")

    except asyncio.CancelledError:
        logger.debug("metrics_update_loop_cancelled")
    except Exception as e:
        logger.error("metrics_update_loop_error", error=str(e))


async def tier1_metrics_updater():
    """Background task to poll and broadcast Tier 1 automation updates.

    Polls for new task routing and test execution records every 5 seconds
    and broadcasts them to all connected WebSocket clients for real-time monitoring.

    """

    from empathy_os.models.telemetry import get_telemetry_store

    logger.info("tier1_metrics_updater_started")

    # Track last seen records to detect new ones
    last_routing_count = 0
    last_test_count = 0

    try:
        while True:
            await asyncio.sleep(5)  # Poll every 5 seconds

            try:
                store = get_telemetry_store()

                # Check for new task routings
                routings = store.get_task_routings(limit=10)
                if len(routings) > last_routing_count:
                    # New routing records detected
                    new_routings = routings[last_routing_count:]
                    for routing in new_routings:
                        await manager.broadcast_tier1_update("task_routing", routing.to_dict())
                    last_routing_count = len(routings)
                    logger.debug("tier1_routing_broadcast", new_count=len(new_routings))

                # Check for new test executions
                executions = store.get_test_executions(limit=10)
                if len(executions) > last_test_count:
                    # New test execution records detected
                    new_executions = executions[last_test_count:]
                    for execution in new_executions:
                        await manager.broadcast_tier1_update("test_execution", execution.to_dict())
                    last_test_count = len(executions)
                    logger.debug("tier1_test_broadcast", new_count=len(new_executions))

            except Exception as e:
                logger.error("tier1_metrics_poll_error", error=str(e))
                # Continue polling even if one iteration fails

    except asyncio.CancelledError:
        logger.info("tier1_metrics_updater_cancelled")
    except Exception as e:
        logger.error("tier1_metrics_updater_error", error=str(e))
