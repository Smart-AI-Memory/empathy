"""
WebSocket API for real-time metrics streaming.

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
    """
    Manages WebSocket connections and broadcasts.

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


manager = ConnectionManager()


@router.websocket("/ws/metrics")
async def websocket_metrics(
    websocket: WebSocket,
    service: Annotated[MemoryService, Depends(get_memory_service)],
    settings: Annotated[Settings, Depends(get_settings)],
):
    """
    WebSocket endpoint for real-time metrics streaming.

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
    """
    Periodically send metrics updates to connected client.

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
