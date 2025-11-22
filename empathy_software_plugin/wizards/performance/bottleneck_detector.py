"""
Bottleneck Detector

Identifies performance bottlenecks in code.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .profiler_parsers import FunctionProfile


class BottleneckType(str, Enum):
    """Types of performance bottlenecks (str-based enum for easy comparison)"""

    HOT_PATH = "hot_path"  # Function taking most total time
    CPU_BOUND = "cpu_bound"  # Heavy computation
    IO_BOUND = "io_bound"  # Waiting for I/O
    N_PLUS_ONE = "n_plus_one"  # Database N+1 query pattern
    MEMORY_LEAK = "memory_leak"  # Growing memory usage
    SYNCHRONOUS_IO = "synchronous_io"  # Blocking I/O operations


@dataclass
class Bottleneck:
    """Identified performance bottleneck"""

    type: BottleneckType
    function_name: str
    file_path: str
    line_number: int
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    time_cost: float  # seconds
    percent_total: float
    reasoning: str
    fix_suggestion: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.type.value,
            "function_name": self.function_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "severity": self.severity,
            "time_cost": self.time_cost,
            "percent_total": self.percent_total,
            "reasoning": self.reasoning,
            "fix_suggestion": self.fix_suggestion,
            "metadata": self.metadata,
        }


class BottleneckDetector:
    """
    Detects performance bottlenecks from profiling data.
    """

    def __init__(self):
        # Patterns indicating different bottleneck types
        self.io_patterns = [
            "read",
            "write",
            "open",
            "close",
            "socket",
            "request",
            "query",
            "execute",
            "fetch",
            "select",
            "insert",
            "update",
        ]

        self.computation_patterns = [
            "sort",
            "calculate",
            "compute",
            "process",
            "transform",
            "encode",
            "decode",
            "compress",
            "encrypt",
            "hash",
        ]

    def detect_bottlenecks(
        self, profiles: list[FunctionProfile], threshold_percent: float = 5.0
    ) -> list[Bottleneck]:
        """
        Detect bottlenecks from profiling data.

        Args:
            profiles: List of function profiles
            threshold_percent: Min percentage of total time to consider

        Returns:
            List of detected bottlenecks
        """
        bottlenecks = []

        # Sort by total time
        sorted_profiles = sorted(profiles, key=lambda p: p.total_time, reverse=True)

        for profile in sorted_profiles:
            # Skip if below threshold
            if profile.percent_total < threshold_percent:
                continue

            # Detect hot paths (top time consumers >= 20%)
            if profile.percent_total >= 20:
                bottlenecks.append(
                    Bottleneck(
                        type=BottleneckType.HOT_PATH,
                        function_name=profile.function_name,
                        file_path=profile.file_path,
                        line_number=profile.line_number,
                        severity=self._determine_severity(profile.percent_total),
                        time_cost=profile.total_time,
                        percent_total=profile.percent_total,
                        reasoning=f"Consumes {profile.percent_total:.1f}% of total execution time",
                        fix_suggestion=self._suggest_hot_path_fix(profile),
                        metadata={"call_count": profile.call_count},
                    )
                )

            # Detect I/O bound operations
            if self._is_io_bound(profile):
                bottlenecks.append(
                    Bottleneck(
                        type=BottleneckType.IO_BOUND,
                        function_name=profile.function_name,
                        file_path=profile.file_path,
                        line_number=profile.line_number,
                        severity=self._determine_severity(profile.percent_total),
                        time_cost=profile.total_time,
                        percent_total=profile.percent_total,
                        reasoning=f"I/O operation taking {profile.total_time:.2f}s",
                        fix_suggestion=self._suggest_io_fix(profile),
                        metadata={"call_count": profile.call_count},
                    )
                )

            # Detect potential N+1 queries
            if self._is_n_plus_one(profile):
                bottlenecks.append(
                    Bottleneck(
                        type=BottleneckType.N_PLUS_ONE,
                        function_name=profile.function_name,
                        file_path=profile.file_path,
                        line_number=profile.line_number,
                        severity="HIGH",
                        time_cost=profile.total_time,
                        percent_total=profile.percent_total,
                        reasoning=f"Database query called {profile.call_count} times - potential N+1",
                        fix_suggestion="Add eager loading or batch queries",
                        metadata={"call_count": profile.call_count},
                    )
                )

        # Sort by severity and time cost
        severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        bottlenecks.sort(key=lambda b: (severity_order.get(b.severity, 4), -b.time_cost))

        return bottlenecks

    def _is_io_bound(self, profile: FunctionProfile) -> bool:
        """Check if function is I/O bound"""
        func_name_lower = profile.function_name.lower()
        return any(pattern in func_name_lower for pattern in self.io_patterns)

    def _is_cpu_bound(self, profile: FunctionProfile) -> bool:
        """Check if function is CPU bound"""
        func_name_lower = profile.function_name.lower()
        return any(pattern in func_name_lower for pattern in self.computation_patterns)

    def _is_n_plus_one(self, profile: FunctionProfile) -> bool:
        """Detect potential N+1 query pattern"""
        func_name_lower = profile.function_name.lower()

        # Database query patterns
        is_query = any(p in func_name_lower for p in ["query", "select", "fetch", "get"])

        # High call count suggests N+1
        high_call_count = profile.call_count > 50

        return is_query and high_call_count

    def _determine_severity(self, percent_total: float) -> str:
        """Determine bottleneck severity"""
        if percent_total > 30:
            return "CRITICAL"
        elif percent_total > 20:
            return "HIGH"
        elif percent_total > 10:
            return "MEDIUM"
        else:
            return "LOW"

    def _suggest_hot_path_fix(self, profile: FunctionProfile) -> str:
        """Suggest fix for hot path"""
        if self._is_cpu_bound(profile):
            return "Optimize algorithm or consider caching results"
        elif self._is_io_bound(profile):
            return "Use async I/O or connection pooling"
        else:
            return "Profile function internally to identify specific bottleneck"

    def _suggest_io_fix(self, profile: FunctionProfile) -> str:
        """Suggest fix for I/O bottleneck"""
        if "query" in profile.function_name.lower() or "select" in profile.function_name.lower():
            return "Add database indexes, use query optimization, or implement caching"
        elif "request" in profile.function_name.lower():
            return "Implement request batching, caching, or use async HTTP client"
        elif "file" in profile.function_name.lower() or "read" in profile.function_name.lower():
            return "Use buffered I/O, async file operations, or caching"
        else:
            return "Consider async I/O operations or connection pooling"
