"""Memory system API endpoints.

Provides REST API for:
- System status
- Redis control (start/stop)
- Statistics
- Health checks
"""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, status

from ..schemas import (
    HealthCheckResponse,
    MemoryStatsResponse,
    RedisStartRequest,
    RedisStartResponse,
    RedisStopResponse,
    SystemStatusResponse,
)
from ..services.memory_service import MemoryService, get_memory_service

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/status",
    response_model=SystemStatusResponse,
    summary="Get system status",
    description="Get comprehensive status of memory system including Redis and long-term storage.",
)
async def get_status(
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> SystemStatusResponse:
    """Get system status.

    Returns current state of:
    - Redis (running/stopped, host, port, start method)
    - Long-term storage (available, directory, pattern count)
    - Configuration (auto-start settings, audit directory)
    """
    try:
        status_data = await service.get_status()
        logger.info("status_retrieved", redis_status=status_data["redis"]["status"])
        return SystemStatusResponse(**status_data)
    except Exception as e:
        logger.error("status_retrieval_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve status: {e!s}",
        )


@router.post(
    "/redis/start",
    response_model=RedisStartResponse,
    summary="Start Redis",
    description="Start Redis if not already running. Attempts multiple start methods based on platform.",
)
async def start_redis(
    request: RedisStartRequest,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> RedisStartResponse:
    """Start Redis server.

    Attempts to start Redis using:
    - macOS: Homebrew, Docker, direct
    - Linux: systemd, Docker, direct
    - Windows: Windows Service, Chocolatey, Scoop, WSL, Docker, direct

    Falls back to mock mode if all methods fail.
    """
    try:
        result = await service.start_redis(verbose=request.verbose)

        if result["success"]:
            logger.info("redis_started", method=result["method"])
        else:
            logger.warning("redis_start_failed", message=result["message"])

        return RedisStartResponse(**result)
    except Exception as e:
        logger.error("redis_start_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start Redis: {e!s}",
        )


@router.post(
    "/redis/stop",
    response_model=RedisStopResponse,
    summary="Stop Redis",
    description="Stop Redis if it was started by this system.",
)
async def stop_redis(
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> RedisStopResponse:
    """Stop Redis server.

    Only stops Redis if it was started by this system (not externally running).
    Returns success=False if Redis wasn't started by us.
    """
    try:
        result = await service.stop_redis()

        if result["success"]:
            logger.info("redis_stopped")
        else:
            logger.warning("redis_stop_skipped", reason="not_started_by_us")

        return RedisStopResponse(**result)
    except Exception as e:
        logger.error("redis_stop_error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop Redis: {e!s}",
        )


@router.get(
    "/stats",
    response_model=MemoryStatsResponse,
    summary="Get statistics",
    description="Get detailed statistics about memory usage, patterns, and Redis keys.",
)
async def get_statistics(
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> MemoryStatsResponse:
    """Get comprehensive statistics.

    Returns detailed metrics for:
    - Redis: key counts (total/working/staged), memory usage
    - Long-term: pattern counts by classification, encryption status
    - Timestamps: when stats were collected
    """
    try:
        stats = await service.get_statistics()
        logger.info(
            "stats_retrieved",
            patterns_total=stats.patterns_total,
            redis_keys=stats.redis_keys_total,
        )

        return MemoryStatsResponse(
            redis_available=stats.redis_available,
            redis_method=stats.redis_method,
            redis_keys_total=stats.redis_keys_total,
            redis_keys_working=stats.redis_keys_working,
            redis_keys_staged=stats.redis_keys_staged,
            redis_memory_used=stats.redis_memory_used,
            long_term_available=stats.long_term_available,
            patterns_total=stats.patterns_total,
            patterns_public=stats.patterns_public,
            patterns_internal=stats.patterns_internal,
            patterns_sensitive=stats.patterns_sensitive,
            patterns_encrypted=stats.patterns_encrypted,
            collected_at=stats.collected_at,
        )
    except Exception as e:
        logger.error("stats_retrieval_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {e!s}",
        )


@router.get(
    "/health",
    response_model=HealthCheckResponse,
    summary="Health check",
    description="Perform comprehensive health check of memory system.",
)
async def health_check(
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> HealthCheckResponse:
    """Health check.

    Checks:
    - Redis availability
    - Long-term storage availability
    - Pattern count
    - Encryption status for sensitive patterns

    Returns overall health status (healthy/degraded/unhealthy) with
    specific check results and recommendations.
    """
    try:
        health = await service.health_check()
        logger.info("health_check_completed", overall=health["overall"])
        return HealthCheckResponse(**health)
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Health check failed: {e!s}",
        )
