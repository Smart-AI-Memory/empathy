"""Cache Statistics and Performance Reporting

Provides comprehensive reporting on cache performance metrics and recommendations.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass
from typing import Any

from empathy_os.cache_monitor import CacheMonitor, CacheStats


@dataclass
class CacheHealthScore:
    """Health assessment for a cache."""

    cache_name: str
    hit_rate: float
    health: str  # "excellent", "good", "fair", "poor"
    confidence: str  # "high", "medium", "low"
    recommendation: str
    reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "cache_name": self.cache_name,
            "hit_rate": round(self.hit_rate, 4),
            "health": self.health,
            "confidence": self.confidence,
            "recommendation": self.recommendation,
            "reasons": self.reasons,
        }


class CacheAnalyzer:
    """Analyzes cache performance and provides recommendations.

    Evaluates cache effectiveness based on hit rates, request patterns,
    and memory usage, then provides actionable recommendations.

    Example:
        >>> analyzer = CacheAnalyzer()
        >>> health = analyzer.analyze_cache("ast_parse")
        >>> print(f"Health: {health.health}")
        >>> print(f"Recommendation: {health.recommendation}")
    """

    @staticmethod
    def analyze_cache(cache_name: str) -> CacheHealthScore | None:
        """Analyze health of a specific cache.

        Args:
            cache_name: Name of cache to analyze

        Returns:
            CacheHealthScore with assessment and recommendations
        """
        monitor = CacheMonitor.get_instance()
        stats = monitor.get_stats(cache_name)

        if not stats:
            return None

        return CacheAnalyzer._calculate_health(stats)

    @staticmethod
    def analyze_all() -> dict[str, CacheHealthScore]:
        """Analyze health of all caches.

        Returns:
            Dictionary mapping cache names to CacheHealthScore
        """
        monitor = CacheMonitor.get_instance()
        all_stats = monitor.get_all_stats()

        return {name: CacheAnalyzer._calculate_health(stats) for name, stats in all_stats.items()}

    @staticmethod
    def _calculate_health(stats: CacheStats) -> CacheHealthScore:
        """Calculate health score for cache statistics.

        Args:
            stats: CacheStats to analyze

        Returns:
            CacheHealthScore with health assessment
        """
        hit_rate = stats.hit_rate
        total_requests = stats.total_requests
        utilization = stats.utilization

        # Determine health based on hit rate and request count
        if total_requests < 10:
            # Low request count - low confidence
            confidence = "low"
            if hit_rate >= 0.8:
                health = "excellent"
            elif hit_rate >= 0.6:
                health = "good"
            else:
                health = "fair"
        elif total_requests < 100:
            # Medium request count - medium confidence
            confidence = "medium"
            if hit_rate >= 0.7:
                health = "excellent"
            elif hit_rate >= 0.5:
                health = "good"
            elif hit_rate >= 0.3:
                health = "fair"
            else:
                health = "poor"
        else:
            # High request count - high confidence
            confidence = "high"
            if hit_rate >= 0.6:
                health = "excellent"
            elif hit_rate >= 0.4:
                health = "good"
            elif hit_rate >= 0.2:
                health = "fair"
            else:
                health = "poor"

        # Generate reasons and recommendations
        reasons = []
        recommendation = ""

        if hit_rate > 0.7:
            reasons.append("Strong hit rate indicates good cache effectiveness")
            if total_requests >= 100:
                recommendation = (
                    "Cache is performing well. Consider monitoring for memory usage as it grows."
                )
            else:
                recommendation = "Cache shows promise with limited data. Continue monitoring."
        elif hit_rate > 0.5:
            reasons.append("Moderate hit rate suggests cache is somewhat effective")
            recommendation = "Monitor for patterns. May benefit from adjusted cache key strategy."
        elif hit_rate > 0.2:
            reasons.append("Low hit rate indicates cache may not be effective for this pattern")
            recommendation = "Review cache invalidation strategy or consider disabling if overhead exceeds benefit."
        else:
            reasons.append("Very low hit rate suggests cache is ineffective")
            recommendation = "Strongly consider disabling this cache or redesigning cache key."

        if utilization > 0.9 and stats.max_size > 0:
            reasons.append("Cache is nearly full - may be evicting useful entries")
            recommendation = (
                f"{recommendation} Consider increasing cache size to {int(stats.max_size * 1.5)}."
            )
        elif utilization < 0.1 and stats.max_size > 0 and total_requests > 50:
            reasons.append("Cache is underutilized - may be oversized")
            recommendation = f"{recommendation} Consider reducing cache size to {max(1, int(stats.max_size * 0.5))}."

        if total_requests > 1000 and hit_rate < 0.3:
            reasons.append("High request volume with low hit rate suggests cache thrashing")
            recommendation = "Cache invalidation may be too aggressive. Review cache lifetime."

        return CacheHealthScore(
            cache_name=stats.name,
            hit_rate=hit_rate,
            health=health,
            confidence=confidence,
            recommendation=recommendation,
            reasons=reasons,
        )


class CacheReporter:
    """Generates formatted cache performance reports.

    Creates human-readable reports on cache metrics, health scores,
    and recommendations for optimization.

    Example:
        >>> reporter = CacheReporter()
        >>> print(reporter.generate_health_report())
    """

    @staticmethod
    def generate_health_report(verbose: bool = False) -> str:
        """Generate cache health report.

        Args:
            verbose: Include detailed metrics

        Returns:
            Formatted health report
        """
        analyzer = CacheAnalyzer()
        health_scores = analyzer.analyze_all()

        if not health_scores:
            return "No caches registered for monitoring"

        # Sort by health (excellent -> poor)
        health_order = {"excellent": 0, "good": 1, "fair": 2, "poor": 3}
        sorted_scores = sorted(
            health_scores.values(),
            key=lambda s: (health_order.get(s.health, 99), -s.hit_rate),
        )

        lines = ["=" * 80, "CACHE HEALTH REPORT", "=" * 80, ""]

        for score in sorted_scores:
            lines.append(f"Cache: {score.cache_name}")
            lines.append("-" * 80)
            lines.append(f"  Health:        {score.health.upper()}")
            lines.append(f"  Confidence:    {score.confidence.upper()}")
            lines.append(f"  Hit Rate:      {score.hit_rate:.1%}")
            lines.append(f"  Recommendation: {score.recommendation}")

            if verbose:
                for reason in score.reasons:
                    lines.append(f"    - {reason}")

            lines.append("")

        # Summary
        excellent = sum(1 for s in health_scores.values() if s.health == "excellent")
        good = sum(1 for s in health_scores.values() if s.health == "good")
        fair = sum(1 for s in health_scores.values() if s.health == "fair")
        poor = sum(1 for s in health_scores.values() if s.health == "poor")

        lines.append("=" * 80)
        lines.append("SUMMARY")
        lines.append("=" * 80)
        lines.append(f"  Total Caches:    {len(health_scores)}")
        lines.append(f"  Excellent:       {excellent}")
        lines.append(f"  Good:            {good}")
        lines.append(f"  Fair:            {fair}")
        lines.append(f"  Poor:            {poor}")
        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def generate_optimization_report() -> str:
        """Generate cache optimization recommendations.

        Returns:
            Formatted optimization report
        """
        monitor = CacheMonitor.get_instance()
        analyzer = CacheAnalyzer()

        lines = ["=" * 80, "CACHE OPTIMIZATION OPPORTUNITIES", "=" * 80, ""]

        underperformers = monitor.get_underperformers(threshold=0.3)
        if underperformers:
            lines.append("LOW-PERFORMING CACHES (hit rate < 30%):")
            lines.append("-" * 80)
            for stats in underperformers:
                health = analyzer.analyze_cache(stats.name)
                if health:
                    lines.append(f"  {stats.name}: {health.recommendation}")
            lines.append("")

        high_performers = monitor.get_high_performers(threshold=0.7)
        if high_performers:
            lines.append("HIGH-PERFORMING CACHES (hit rate > 70%):")
            lines.append("-" * 80)
            for stats in high_performers:
                lines.append(f"  {stats.name}: Performing well ({stats.hit_rate:.1%} hit rate)")
            lines.append("")

        lines.append("=" * 80)

        return "\n".join(lines)

    @staticmethod
    def generate_full_report() -> str:
        """Generate comprehensive cache report.

        Returns:
            Formatted comprehensive report
        """
        monitor = CacheMonitor.get_instance()

        report_parts = [
            "=" * 80,
            "COMPREHENSIVE CACHE ANALYSIS REPORT",
            "=" * 80,
            "",
            monitor.get_report(verbose=True),
            "",
            monitor.get_size_report(),
            "",
            CacheReporter.generate_health_report(verbose=True),
            "",
            CacheReporter.generate_optimization_report(),
        ]

        return "\n".join(report_parts)
