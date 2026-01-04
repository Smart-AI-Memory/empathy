"""Result Cache
Caches wizard results to avoid redundant computations

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging
import time
from typing import Any

logger = logging.getLogger(__name__)


class ResultCache:
    """Simple in-memory cache with TTL"""

    def __init__(self, ttl: int = 300):
        """Initialize cache

        Args:
            ttl: Time-to-live in seconds (default 5 minutes)

        """
        self.ttl = ttl
        self._cache: dict[str, dict[str, Any]] = {}
        logger.info(f"ResultCache initialized with TTL={ttl}s")

    def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if key in self._cache:
            entry = self._cache[key]
            if time.time() - entry["timestamp"] < self.ttl:
                logger.debug(f"Cache hit: {key}")
                return entry["value"]
            # Expired, remove
            logger.debug(f"Cache expired: {key}")
            del self._cache[key]
        return None

    def set(self, key: str, value: Any):
        """Set value in cache"""
        self._cache[key] = {"value": value, "timestamp": time.time()}
        logger.debug(f"Cache set: {key}")

    def clear(self):
        """Clear all cache entries"""
        count = len(self._cache)
        self._cache.clear()
        logger.info(f"Cache cleared: {count} entries removed")

    def clear_file(self, file_uri: str):
        """Clear all cache entries related to a specific file"""
        keys_to_remove = [key for key in self._cache if file_uri in key]
        for key in keys_to_remove:
            del self._cache[key]
        if keys_to_remove:
            logger.debug(f"Cleared {len(keys_to_remove)} cache entries for {file_uri}")

    def cleanup(self):
        """Remove expired entries"""
        now = time.time()
        expired_keys = [
            key for key, entry in self._cache.items() if now - entry["timestamp"] >= self.ttl
        ]
        for key in expired_keys:
            del self._cache[key]
        if expired_keys:
            logger.debug(f"Cleaned up {len(expired_keys)} expired cache entries")

    def stats(self) -> dict[str, Any]:
        """Get cache statistics"""
        return {
            "total_entries": len(self._cache),
            "ttl": self.ttl,
            "oldest_entry_age": min(
                (time.time() - entry["timestamp"] for entry in self._cache.values()),
                default=0,
            ),
        }
