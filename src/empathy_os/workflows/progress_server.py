"""WebSocket Progress Server

Real-time progress streaming for workflow execution.
Enables live UI updates in VS Code and other clients.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from __future__ import annotations

import asyncio
import json
import logging
import signal
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

from .progress import ProgressCallback, ProgressTracker, ProgressUpdate

# Try to import websockets, provide helpful error if not available
WebSocketServerProtocol: Any = None
WEBSOCKETS_AVAILABLE = False
try:
    import websockets

    # Try new name first (websockets 11+), fall back to old name
    try:
        from websockets.server import ServerProtocol

        WebSocketServerProtocol = ServerProtocol
    except ImportError:
        from websockets.server import WebSocketServerProtocol as _WS  # type: ignore[attr-defined]

        WebSocketServerProtocol = _WS
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    pass

logger = logging.getLogger(__name__)


@dataclass
class ProgressServerConfig:
    """Configuration for the progress WebSocket server."""

    host: str = "localhost"
    port: int = 8766
    ping_interval: float = 20.0
    ping_timeout: float = 20.0
    max_connections: int = 100


class ProgressServer:
    """WebSocket server for broadcasting workflow progress.

    Clients connect and receive real-time progress updates for all
    running workflows. Supports multiple concurrent connections.
    """

    def __init__(self, config: ProgressServerConfig | None = None):
        if not WEBSOCKETS_AVAILABLE:
            raise ImportError(
                "websockets package is required for ProgressServer. "
                "Install with: pip install websockets",
            )

        self.config = config or ProgressServerConfig()
        self._clients: set[WebSocketServerProtocol] = set()
        self._server: Any = None
        self._running = False
        self._trackers: dict[str, ProgressTracker] = {}

    async def start(self) -> None:
        """Start the WebSocket server."""
        self._running = True

        self._server = await websockets.serve(
            self._handle_connection,
            self.config.host,
            self.config.port,
            ping_interval=self.config.ping_interval,
            ping_timeout=self.config.ping_timeout,
        )

        logger.info(f"Progress server started on ws://{self.config.host}:{self.config.port}")

    async def stop(self) -> None:
        """Stop the WebSocket server."""
        self._running = False

        # Close all client connections
        if self._clients:
            await asyncio.gather(
                *[client.close(1001, "Server shutting down") for client in self._clients],
                return_exceptions=True,
            )
            self._clients.clear()

        # Close server
        if self._server:
            self._server.close()
            await self._server.wait_closed()

        logger.info("Progress server stopped")

    async def _handle_connection(self, websocket: WebSocketServerProtocol) -> None:
        """Handle a new client connection."""
        if len(self._clients) >= self.config.max_connections:
            await websocket.close(1013, "Maximum connections reached")
            return

        self._clients.add(websocket)
        client_id = id(websocket)
        logger.debug(f"Client {client_id} connected. Total clients: {len(self._clients)}")

        try:
            # Send welcome message with current state
            await websocket.send(
                json.dumps(
                    {
                        "type": "connected",
                        "message": "Connected to Empathy progress server",
                        "active_workflows": list(self._trackers.keys()),
                    },
                ),
            )

            # Handle incoming messages (subscriptions, etc.)
            async for message in websocket:
                await self._handle_message(websocket, message)

        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            self._clients.discard(websocket)
            logger.debug(f"Client {client_id} disconnected. Total clients: {len(self._clients)}")

    async def _handle_message(self, websocket: WebSocketServerProtocol, message: str) -> None:
        """Handle incoming message from client."""
        try:
            data = json.loads(message)
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong"}))

            elif msg_type == "subscribe":
                # Client wants updates for specific workflow
                workflow_id = data.get("workflow_id")
                if workflow_id:
                    # Could track per-client subscriptions here
                    await websocket.send(
                        json.dumps({"type": "subscribed", "workflow_id": workflow_id}),
                    )

            elif msg_type == "get_status":
                # Client wants current status of all workflows
                await websocket.send(
                    json.dumps(
                        {
                            "type": "status",
                            "active_workflows": list(self._trackers.keys()),
                            "client_count": len(self._clients),
                        },
                    ),
                )

        except json.JSONDecodeError:
            await websocket.send(json.dumps({"type": "error", "message": "Invalid JSON"}))

    async def broadcast(self, update: ProgressUpdate) -> None:
        """Broadcast a progress update to all connected clients."""
        if not self._clients:
            return

        message = json.dumps({"type": "progress", **update.to_dict()})

        # Broadcast to all clients
        await asyncio.gather(
            *[self._send_safe(client, message) for client in self._clients],
            return_exceptions=True,
        )

    async def _send_safe(self, client: WebSocketServerProtocol, message: str) -> None:
        """Send message to client with error handling."""
        try:
            await client.send(message)
        except websockets.exceptions.ConnectionClosed:
            self._clients.discard(client)

    def create_tracker(
        self,
        workflow_name: str,
        workflow_id: str,
        stage_names: list[str],
    ) -> ProgressTracker:
        """Create a progress tracker that broadcasts to this server.

        Args:
            workflow_name: Name of the workflow
            workflow_id: Unique ID for this run
            stage_names: List of stage names

        Returns:
            ProgressTracker configured to broadcast updates

        """
        tracker = ProgressTracker(
            workflow_name=workflow_name,
            workflow_id=workflow_id,
            stage_names=stage_names,
        )

        # Store tracker
        self._trackers[workflow_id] = tracker

        # Add async callback to broadcast updates
        async def broadcast_callback(update: ProgressUpdate) -> None:
            await self.broadcast(update)

        tracker.add_async_callback(broadcast_callback)

        return tracker

    def remove_tracker(self, workflow_id: str) -> None:
        """Remove a tracker when workflow completes."""
        self._trackers.pop(workflow_id, None)

    def get_callback(self) -> ProgressCallback:
        """Get a synchronous callback that queues broadcasts.

        Useful for integration with sync code that can't await.
        """

        def callback(update: ProgressUpdate) -> None:
            # Schedule broadcast in event loop
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    asyncio.create_task(self.broadcast(update))
                else:
                    loop.run_until_complete(self.broadcast(update))
            except RuntimeError:
                # No event loop, skip
                pass

        return callback


# Global server instance for singleton pattern
_server_instance: ProgressServer | None = None


def get_progress_server(config: ProgressServerConfig | None = None) -> ProgressServer:
    """Get or create the global progress server instance."""
    global _server_instance

    if _server_instance is None:
        _server_instance = ProgressServer(config)

    return _server_instance


@asynccontextmanager
async def progress_server_context(config: ProgressServerConfig | None = None):
    """Context manager for running the progress server.

    Usage:
        async with progress_server_context() as server:
            tracker = server.create_tracker(...)
            # Run workflow with tracker
    """
    server = get_progress_server(config)

    try:
        await server.start()
        yield server
    finally:
        await server.stop()


async def run_server(host: str = "localhost", port: int = 8766) -> None:
    """Run the progress server standalone.

    Can be run as: python -m empathy_os.workflows.progress_server
    """
    config = ProgressServerConfig(host=host, port=port)
    server = ProgressServer(config)

    # Handle shutdown signals
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(server.stop()))

    try:
        await server.start()
        print(f"Progress server running on ws://{host}:{port}")
        print("Press Ctrl+C to stop")

        # Keep running until stopped
        while server._running:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        pass
    finally:
        await server.stop()


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Empathy Progress WebSocket Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8766, help="Port to listen on")

    args = parser.parse_args()

    asyncio.run(run_server(host=args.host, port=args.port))
