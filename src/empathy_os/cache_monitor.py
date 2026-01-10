"""Cache Performance Monitoring

Tracks cache hit rates, memory usage, and performance metrics for all caches
in the Empathy Framework.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class CacheStats:
    """Statistics for a single cache.

    Tracks hits, misses, evictions, and calculates derived metrics like hit rate.
    """

    name: str
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def total_requests(self) -> int:
        """Total cache requests (hits + misses)."""
        return self.hits + self.misses

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0.0-1.0)."""
        if self.total_requests == 0:
            return 0.0
        return self.hits / self.total_requests

    @property
    def miss_rate(self) -> float:
        """Cache miss rate (0.0-1.0)."""
        return 1.0 - self.hit_rate

    @property
    def utilization(self) -> float:
        """Cache utilization (0.0-1.0)."""
        if self.max_size == 0:
            return 0.0
        return self.size / self.max_size

    def record_hit(self) -> None:
        """Record a cache hit."""
        self.hits += 1
        self.last_updated = datetime.now()

    def record_miss(self) -> None:
        """Record a cache miss."""
        self.misses += 1
        self.last_updated = datetime.now()

    def record_eviction(self) -> None:
        """Record a cache eviction."""
        self.evictions += 1
        self.last_updated = datetime.now()

    def update_size(self, size: int, max_size: int | None = None) -> None:
        """Update cache size metrics."""
        self.size = size
        if max_size is not None:
            self.max_size = max_size
        self.last_updated = datetime.now()

    def to_dict(self) -> dict[str, Any]:
        """Export statistics as dictionary."""
        return {
            "name": self.name,
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "total_requests": self.total_requests,
            "hit_rate": round(self.hit_rate, 4),
            "miss_rate": round(self.miss_rate, 4),
            "size": self.size,
            "max_size": self.max_size,
            "utilization": round(self.utilization, 4),
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class CacheMonitor:
    """Global cache monitoring system.

    Tracks performance of all caches in the framework. Provides centralized
    reporting and analysis of cache effectiveness.

    Example:
        >>> monitor = CacheMonitor.get_instance()
        >>> monitor.register_cache("ast_parse", max_size=500)
        >>>
        >>> # Record cache operations
        >>> monitor.record_hit("ast_parse")
        >>> monitor.record_miss("ast_parse")
        >>>
        >>> # Get statistics
        >>> stats = monitor.get_stats("ast_parse")
        >>> print(f"Hit rate: {stats.hit_rate:.1%}")
        >>>
        >>> # Generate report
        >>> print(monitor.get_report())
    """

    _instance: "CacheMonitor | None" = None

    def __init__(self):
        """Initialize cache monitor."""
        self._caches: dict[str, CacheStats] = {}

    @classmethod
    def get_instance(cls) -> "CacheMonitor":
        """Get or create singleton instance."""
        if cls._instance is None:
            cls._instance = CacheMonitor()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (for testing)."""
        cls._instance = None

    def register_cache(
        self,
        name: str,
        max_size: int = 0,
    ) -> CacheStats:
        """Register a new cache for monitoring.

        Args:
            name: Unique cache identifier
            max_size: Maximum cache size (0 = unlimited)

        Returns:
            CacheStats object for this cache

        Raises:
            ValueError: If cache name already exists
        """
        if name in self._caches:
            raise ValueError(f"Cache '{name}' already registered")

        stats = CacheStats(name=name, max_size=max_size)
        self._caches[name] = stats
        return stats

    def get_stats(self, name: str) -> CacheStats | None:
        """Get statistics for a specific cache.

        Args:
            name: Cache identifier

        Returns:
            CacheStats object or None if not found
        """
        return self._caches.get(name)

    def record_hit(self, name: str) -> None:
        """Record a cache hit.

        Args:
            name: Cache identifier
        """
        if stats := self._caches.get(name):
            stats.record_hit()

    def record_miss(self, name: str) -> None:
        """Record a cache miss.

        Args:
            name: Cache identifier
        """
        if stats := self._caches.get(name):
            stats.record_miss()

    def record_eviction(self, name: str) -> None:
        """Record a cache eviction.

        Args:
            name: Cache identifier
        """
        if stats := self._caches.get(name):
            stats.record_eviction()

    def update_size(self, name: str, size: int, max_size: int | None = None) -> None:
        """Update cache size.

        Args:
            name: Cache identifier
            size: Current cache size
            max_size: Maximum cache size (optional)
        """
        if stats := self._caches.get(name):
            stats.update_size(size, max_size)

    def get_all_stats(self) -> dict[str, CacheStats]:
        """Get statistics for all registered caches.

        Returns:
            Dict mapping cache names to CacheStats
        """
        return dict(self._caches)

    def get_report(self, verbose: bool = False) -> str:
        """Generate human-readable cache performance report.

        Args:
            verbose: Include detailed metrics

        Returns:
            Formatted report string
        """
        if not self._caches:
            return "No caches registered"

        lines = ["=" * 70, "CACHE PERFORMANCE REPORT", "=" * 70, ""]

        # Sort by hit rate (descending)
        sorted_caches = sorted(
            self._caches.values(),
            key=lambda s: s.hit_rate,
            reverse=True,
        )

        for stats in sorted_caches:
            lines.append(f"Cache: {stats.name}")
            lines.append("-" * 70)
            lines.append(f"  Hit Rate:        {stats.hit_rate:>6.1%}")
            lines.append(f"  Total Requests:  {stats.total_requests:>8,}")
            lines.append(f"  Hits:            {stats.hits:>8,}")
            lines.append(f"  Misses:          {stats.misses:>8,}")

            if verbose:
                lines.append(f"  Evictions:       {stats.evictions:>8,}")
                lines.append(f"  Size:            {stats.size:>8,}/{stats.max_size:<8,}")
                lines.append(f"  Utilization:     {stats.utilization:>6.1%}")
                lines.append(f"  Created:         {stats.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                lines.append(
                    f"  Last Updated:    {stats.last_updated.strftime('%Y-%m-%d %H:%M:%S')}"
                )

            lines.append("")

        # Summary
        total_requests = sum(s.total_requests for s in sorted_caches)
        total_hits = sum(s.hits for s in sorted_caches)
        overall_hit_rate = total_hits / total_requests if total_requests > 0 else 0.0

        lines.append("=" * 70)
        lines.append("SUMMARY")
        lines.append("=" * 70)
        lines.append(f"  Total Caches:    {len(self._caches)}")
        lines.append(f"  Total Requests:  {total_requests:,}")
        lines.append(f"  Overall Hit Rate: {overall_hit_rate:.1%}")
        lines.append("=" * 70)

        return "\n".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """Export all statistics as dictionary.

        Returns:
            Dict with all cache statistics
        """
        return {
            "caches": {name: stats.to_dict() for name, stats in self._caches.items()},
            "summary": {
                "total_caches": len(self._caches),
                "total_requests": sum(s.total_requests for s in self._caches.values()),
                "total_hits": sum(s.hits for s in self._caches.values()),
                "total_misses": sum(s.misses for s in self._caches.values()),
                "overall_hit_rate": (
                    sum(s.hits for s in self._caches.values())
                    / sum(s.total_requests for s in self._caches.values())
                    if sum(s.total_requests for s in self._caches.values()) > 0
                    else 0.0
                ),
            },
        }

    def reset(self) -> None:
        """Reset all cache statistics."""
        self._caches.clear()

    def get_high_performers(self, threshold: float = 0.6) -> list[CacheStats]:
        """Get caches with hit rate above threshold.

        Args:
            threshold: Minimum hit rate (0.0-1.0)

        Returns:
            List of CacheStats with hit rate >= threshold, sorted by hit rate
        """
        return sorted(
            [s for s in self._caches.values() if s.hit_rate >= threshold],
            key=lambda s: s.hit_rate,
            reverse=True,
        )

    def get_underperformers(self, threshold: float = 0.3) -> list[CacheStats]:
        """Get caches with hit rate below threshold.

        Args:
            threshold: Maximum hit rate (0.0-1.0)

        Returns:
            List of CacheStats with hit rate <= threshold, sorted by hit rate
        """
        return sorted(
            [s for s in self._caches.values() if s.hit_rate <= threshold],
            key=lambda s: s.hit_rate,
        )

    def get_size_report(self) -> str:
        """Generate report on cache memory usage.

        Returns:
            Formatted string with memory usage details
        """
        lines = ["=" * 70, "CACHE SIZE REPORT", "=" * 70, ""]

        total_used = 0
        total_capacity = 0

        for stats in sorted(self._caches.values(), key=lambda s: s.size, reverse=True):
            used_pct = stats.utilization * 100
            lines.append(
                f"{stats.name:<30} {stats.size:>8,} / {stats.max_size:>8,}  ({used_pct:>5.1f}%)"
            )
            total_used += stats.size
            total_capacity += stats.max_size

        lines.append("=" * 70)
        if total_capacity > 0:
            lines.append(
                f"{'TOTAL':<30} {total_used:>8,} / {total_capacity:>8,}  ({total_used/total_capacity*100:>5.1f}%)"
            )
        else:
            lines.append(f"{'TOTAL':<30} {total_used:>8,} / unlimited")
        lines.append("=" * 70)

        return "\n".join(lines)
