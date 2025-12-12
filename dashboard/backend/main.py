"""
Empathy Memory Dashboard API

FastAPI backend for managing and monitoring Empathy Framework memory system.
Provides REST API and WebSocket endpoints for real-time monitoring.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import sys
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from .api import api_router
from .config import get_settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup/shutdown events.

    Startup:
    - Log configuration
    - Initialize memory service (lazy)

    Shutdown:
    - Log shutdown
    - Cleanup connections
    """
    settings = get_settings()
    logger.info(
        "api_starting",
        environment=settings.environment,
        redis_host=settings.redis_host,
        redis_port=settings.redis_port,
        auth_enabled=settings.auth_enabled,
    )

    yield

    logger.info("api_shutting_down")


# Create FastAPI app
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_credentials,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "path": str(request.url.path),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors."""
    logger.error("internal_server_error", error=str(exc), path=str(request.url.path))
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": str(exc) if settings.debug else "An error occurred",
        },
    )


# Health check endpoint (no prefix)
@app.get("/", tags=["System"])
async def root():
    """
    Root endpoint - API information.

    Returns basic API info and health status.
    """
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "status": "running",
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "disabled",
    }


@app.get("/ping", tags=["System"])
async def ping():
    """
    Simple ping endpoint for health checks.

    Returns:
        pong message with timestamp
    """
    from datetime import datetime

    return {
        "message": "pong",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }


# Include API routes
app.include_router(api_router)


def main():
    """
    Main entry point for running the API server.

    Usage:
        python -m dashboard.backend.main
        or
        uvicorn dashboard.backend.main:app --reload
    """
    settings = get_settings()

    uvicorn_config = {
        "app": "dashboard.backend.main:app",
        "host": "0.0.0.0",
        "port": 8000,
        "log_level": "info",
    }

    if settings.environment == "development":
        uvicorn_config["reload"] = True
        uvicorn_config["log_level"] = "debug"

    logger.info("starting_uvicorn_server", **uvicorn_config)

    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
