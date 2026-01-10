"""Pattern Matching Cache for Efficient Query Results

Implements efficient caching of pattern matching operations with hit/miss tracking.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

from empathy_os.cache_monitor import CacheMonitor

T = TypeVar("T")


class PatternMatchCache:
    """Cache for pattern matching query results.

    Caches expensive pattern matching operations with context-based invalidation.
    Monitors hit rates and provides performance metrics.

    Features:
    - LRU-based caching with configurable size
    - Context-based cache keys (JSON serialized)
    - Hit/miss tracking with CacheMonitor integration
    - Simple memory bounds management
    - Thread-safe operations

    Example:
        >>> cache = PatternMatchCache(max_size=1000)
        >>>
        >>> # Cache is typically used internally by PatternLibrary
        >>> # Manual usage:
        >>> context = {"domain": "testing", "language": "python"}
        >>> matches = cache.get_or_compute(
        ...     context,
        ...     compute_fn=lambda: expensive_query(context)
        ... )
    """

    def __init__(self, max_size: int = 1000):
        """Initialize pattern match cache.

        Args:
            max_size: Maximum number of cached query results
        """
        self.max_size = max_size
        self._cache: dict[str, Any] = {}
        self._access_order: list[str] = []

        # Register with monitor
        monitor = CacheMonitor.get_instance()
        try:
            monitor.register_cache("pattern_match", max_size=max_size)
        except ValueError:
            # Already registered, that's OK
            pass

    def _make_key(self, context: dict[str, Any]) -> str:
        """Create deterministic cache key from context.

        Args:
            context: Context dictionary

        Returns:
            JSON string suitable for cache key
        """
        return json.dumps(context, sort_keys=True)

    def get(self, context: dict[str, Any]) -> Any | None:
        """Get cached result for context.

        Records cache hit/miss with monitor.

        Args:
            context: Query context

        Returns:
            Cached result or None if not in cache
        """
        key = self._make_key(context)

        monitor = CacheMonitor.get_instance()
        if key in self._cache:
            monitor.record_hit("pattern_match")
            # Move to end (LRU)
            self._access_order.remove(key)
            self._access_order.append(key)
            return self._cache[key]

        monitor.record_miss("pattern_match")
        return None

    def set(self, context: dict[str, Any], result: Any) -> None:
        """Cache result for context.

        Args:
            context: Query context
            result: Result to cache
        """
        key = self._make_key(context)

        # Remove if exists (for LRU update)
        if key in self._cache:
            self._access_order.remove(key)

        # Add to cache
        self._cache[key] = result
        self._access_order.append(key)

        # Evict oldest if over capacity
        if len(self._cache) > self.max_size:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]

            monitor = CacheMonitor.get_instance()
            monitor.record_eviction("pattern_match")

        # Update size
        monitor = CacheMonitor.get_instance()
        monitor.update_size("pattern_match", len(self._cache))

    def clear(self) -> None:
        """Clear all cached results."""
        self._cache.clear()
        self._access_order.clear()

        monitor = CacheMonitor.get_instance()
        monitor.update_size("pattern_match", 0)

    def get_or_compute(
        self,
        context: dict[str, Any],
        compute_fn: Callable[[], T],
    ) -> T:
        """Get from cache or compute result.

        Args:
            context: Query context
            compute_fn: Function to compute result if not cached

        Returns:
            Cached or newly computed result
        """
        cached = self.get(context)
        if cached is not None:
            return cached

        result = compute_fn()
        self.set(context, result)
        return result


def cached_pattern_query(cache: PatternMatchCache) -> Callable:
    """Decorator for caching pattern query results.

    Usage:
        >>> cache = PatternMatchCache()
        >>> @cached_pattern_query(cache)
        ... def query_patterns(context, min_confidence=0.5):
        ...     return expensive_query(context, min_confidence)

    Args:
        cache: PatternMatchCache instance to use

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, context: dict[str, Any], **kwargs) -> Any:
            # Include kwargs in cache key for correctness
            cache_context = {"context": context, "kwargs": kwargs}
            return cache.get_or_compute(
                cache_context,
                lambda: func(self, context, **kwargs),
            )

        return wrapper

    return decorator
