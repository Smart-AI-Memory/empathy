"""
Memory service layer wrapping MemoryControlPanel.

Provides async interface for memory operations with proper error handling,
logging, and business logic separation from API routes.
"""

import asyncio
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any

import structlog

# Add parent directory to path to import empathy_os
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from empathy_os.memory.control_panel import (
    ControlPanelConfig,
    MemoryControlPanel,
    MemoryStats,
)

from ..config import Settings, get_settings

logger = structlog.get_logger(__name__)


class MemoryService:
    """
    Service layer for memory operations.

    Wraps MemoryControlPanel with async interface and additional
    business logic for API consumption.
    """

    def __init__(self, settings: Settings):
        """
        Initialize memory service.

        Args:
            settings: Application settings
        """
        self.settings = settings

        # Create control panel config from settings
        config = ControlPanelConfig(
            redis_host=settings.redis_host,
            redis_port=settings.redis_port,
            storage_dir=settings.storage_dir,
            audit_dir=settings.audit_dir,
            auto_start_redis=settings.redis_auto_start,
        )

        self._panel = MemoryControlPanel(config)
        logger.info(
            "memory_service_initialized",
            redis_host=settings.redis_host,
            redis_port=settings.redis_port,
            storage_dir=settings.storage_dir,
        )

    async def get_status(self) -> dict[str, Any]:
        """
        Get system status asynchronously.

        Returns:
            System status dictionary
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._panel.status)

    async def start_redis(self, verbose: bool = True) -> dict[str, Any]:
        """
        Start Redis if not running.

        Args:
            verbose: Enable verbose logging

        Returns:
            Start result with status information
        """
        loop = asyncio.get_event_loop()
        status = await loop.run_in_executor(None, self._panel.start_redis, verbose)

        return {
            "success": status.available,
            "available": status.available,
            "method": status.method.value,
            "message": status.message,
            "host": status.host,
            "port": status.port,
        }

    async def stop_redis(self) -> dict[str, Any]:
        """
        Stop Redis if we started it.

        Returns:
            Stop result
        """
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, self._panel.stop_redis)

        message = (
            "Redis stopped successfully"
            if success
            else "Could not stop Redis (may not have been started by us)"
        )

        return {
            "success": success,
            "message": message,
        }

    async def get_statistics(self) -> MemoryStats:
        """
        Get comprehensive statistics.

        Returns:
            MemoryStats object
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._panel.get_statistics)

    async def health_check(self) -> dict[str, Any]:
        """
        Perform health check.

        Returns:
            Health check results
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._panel.health_check)

    async def list_patterns(
        self,
        classification: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        List patterns in long-term storage.

        Args:
            classification: Filter by classification (PUBLIC/INTERNAL/SENSITIVE)
            limit: Maximum patterns to return

        Returns:
            List of pattern summaries
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._panel.list_patterns,
            classification,
            limit,
        )

    async def delete_pattern(
        self,
        pattern_id: str,
        user_id: str = "admin@system",
    ) -> bool:
        """
        Delete a pattern.

        Args:
            pattern_id: Pattern ID to delete
            user_id: User performing deletion (for audit)

        Returns:
            True if deleted successfully
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self._panel.delete_pattern,
            pattern_id,
            user_id,
        )

    async def export_patterns(
        self,
        output_path: str,
        classification: str | None = None,
    ) -> dict[str, Any]:
        """
        Export patterns to JSON file.

        Args:
            output_path: Output file path
            classification: Filter by classification

        Returns:
            Export result with count and path
        """
        loop = asyncio.get_event_loop()
        count = await loop.run_in_executor(
            None,
            self._panel.export_patterns,
            output_path,
            classification,
        )

        from datetime import datetime

        return {
            "success": True,
            "pattern_count": count,
            "output_path": output_path,
            "exported_at": datetime.utcnow().isoformat() + "Z",
        }

    async def get_real_time_metrics(self) -> dict[str, Any]:
        """
        Get real-time metrics for WebSocket streaming.

        Returns:
            Lightweight metrics dictionary
        """
        stats = await self.get_statistics()

        from datetime import datetime

        return {
            "redis_keys_total": stats.redis_keys_total,
            "redis_keys_working": stats.redis_keys_working,
            "redis_keys_staged": stats.redis_keys_staged,
            "redis_memory_used": stats.redis_memory_used,
            "patterns_total": stats.patterns_total,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }


@lru_cache
def get_memory_service() -> MemoryService:
    """
    Get cached MemoryService instance.

    Returns:
        Singleton MemoryService instance
    """
    settings = get_settings()
    return MemoryService(settings)
