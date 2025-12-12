"""
API routes for Empathy Memory Dashboard.

This package contains all API endpoint definitions organized by domain:
- memory: Memory system operations (status, Redis control)
- patterns: Pattern management (list, export, delete)
- websocket: Real-time metrics streaming
"""

from fastapi import APIRouter

from .memory import router as memory_router
from .patterns import router as patterns_router
from .websocket import router as websocket_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(memory_router, prefix="/api", tags=["Memory"])
api_router.include_router(patterns_router, prefix="/api", tags=["Patterns"])
api_router.include_router(websocket_router, tags=["WebSocket"])

__all__ = ["api_router"]
