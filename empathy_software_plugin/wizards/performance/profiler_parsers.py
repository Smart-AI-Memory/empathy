"""
Profiler Output Parsers

Parses output from various profilers (cProfile, perf, Chrome DevTools, etc.)

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class ProfilerType(Enum):
    """Types of profilers"""

    CPROFILE = "cprofile"
    PYINSTRUMENT = "pyinstrument"
    CHROME_DEVTOOLS = "chrome_devtools"
    NODE_PROFILER = "node_profiler"
    GOLANG_PPROF = "golang_pprof"


@dataclass
class FunctionProfile:
    """
    Standardized function profile data.

    Universal format across all profilers.
    """

    function_name: str
    file_path: str
    line_number: int
    total_time: float  # seconds
    self_time: float  # seconds (excluding called functions)
    call_count: int
    cumulative_time: float  # seconds
    percent_total: float
    profiler: str
    children: list["FunctionProfile"] | None = None
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "function_name": self.function_name,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "total_time": self.total_time,
            "self_time": self.self_time,
            "call_count": self.call_count,
            "cumulative_time": self.cumulative_time,
            "percent_total": self.percent_total,
            "profiler": self.profiler,
            "children": [c.to_dict() for c in (self.children or [])],
            "metadata": self.metadata or {},
        }


class BaseProfilerParser:
    """Base class for profiler parsers"""

    def __init__(self, profiler_name: str):
        self.profiler_name = profiler_name

    def parse(self, data: str) -> list[FunctionProfile]:
        """Parse profiler output"""
        raise NotImplementedError


class CProfileParser(BaseProfilerParser):
    """
    Parse Python cProfile output.

    Handles both text and pstats format.
    """

    def __init__(self):
        super().__init__("cprofile")

    def parse(self, data: str) -> list[FunctionProfile]:
        """Parse cProfile text output"""
        profiles = []

        # Pattern for cProfile text output:
        # ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        pattern = r"(\d+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(.+?):(\d+)\((.+?)\)"

        for line in data.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                (ncalls, tottime, percall_tot, cumtime, percall_cum, filepath, lineno, funcname) = (
                    match.groups()
                )

                profiles.append(
                    FunctionProfile(
                        function_name=funcname,
                        file_path=filepath,
                        line_number=int(lineno),
                        total_time=float(tottime),
                        self_time=float(tottime),  # tottime is self time in cProfile
                        call_count=int(ncalls),
                        cumulative_time=float(cumtime),
                        percent_total=0.0,  # Calculate later
                        profiler=self.profiler_name,
                    )
                )

        # Calculate percentages
        if profiles:
            total_time = sum(p.total_time for p in profiles)
            for profile in profiles:
                profile.percent_total = (
                    (profile.total_time / total_time * 100) if total_time > 0 else 0
                )

        # Sort by total time descending
        profiles.sort(key=lambda p: p.total_time, reverse=True)

        return profiles


class ChromeDevToolsParser(BaseProfilerParser):
    """
    Parse Chrome DevTools Performance profile.

    JSON format from Chrome DevTools Performance tab.
    """

    def __init__(self):
        super().__init__("chrome_devtools")

    def parse(self, data: str) -> list[FunctionProfile]:
        """Parse Chrome DevTools JSON"""
        profiles = []

        try:
            profile_data = json.loads(data)

            # Chrome DevTools format is complex - simplified parsing
            # Look for function calls in trace events
            events = profile_data.get("traceEvents", [])

            function_times = {}

            for event in events:
                if event.get("ph") == "X":  # Complete events
                    name = event.get("name", "unknown")
                    dur = event.get("dur", 0) / 1000000  # Convert microseconds to seconds

                    if name not in function_times:
                        function_times[name] = {"total_time": 0, "call_count": 0}

                    function_times[name]["total_time"] += dur
                    function_times[name]["call_count"] += 1

            # Convert to FunctionProfile
            total_time = sum(data["total_time"] for data in function_times.values())

            for func_name, data in function_times.items():
                profiles.append(
                    FunctionProfile(
                        function_name=func_name,
                        file_path="",  # Chrome doesn't always provide
                        line_number=0,
                        total_time=data["total_time"],
                        self_time=data["total_time"],
                        call_count=data["call_count"],
                        cumulative_time=data["total_time"],
                        percent_total=(
                            (data["total_time"] / total_time * 100) if total_time > 0 else 0
                        ),
                        profiler=self.profiler_name,
                    )
                )

            profiles.sort(key=lambda p: p.total_time, reverse=True)

        except json.JSONDecodeError:
            pass

        return profiles


class SimpleJSONProfilerParser(BaseProfilerParser):
    """
    Parse simple JSON profiler format.

    For custom or simplified profiling data.
    """

    def __init__(self):
        super().__init__("simple_json")

    def parse(self, data: str) -> list[FunctionProfile]:
        """Parse simple JSON format"""
        profiles = []

        try:
            parsed = json.loads(data)

            functions = parsed.get("functions", [])

            for func in functions:
                profiles.append(
                    FunctionProfile(
                        function_name=func.get("name", "unknown"),
                        file_path=func.get("file", ""),
                        line_number=func.get("line", 0),
                        total_time=func.get("total_time", 0.0),
                        self_time=func.get("self_time", 0.0),
                        call_count=func.get("calls", 0),
                        cumulative_time=func.get("cumulative_time", 0.0),
                        percent_total=func.get("percent", 0.0),
                        profiler=self.profiler_name,
                    )
                )

            profiles.sort(key=lambda p: p.total_time, reverse=True)

        except json.JSONDecodeError:
            pass

        return profiles


class ProfilerParserFactory:
    """Factory for creating profiler parsers"""

    _parsers = {
        "cprofile": CProfileParser,
        "chrome_devtools": ChromeDevToolsParser,
        "simple_json": SimpleJSONProfilerParser,
    }

    @classmethod
    def create(cls, profiler_type: str) -> BaseProfilerParser:
        """Create parser for profiler type"""
        parser_class = cls._parsers.get(profiler_type.lower())

        if not parser_class:
            raise ValueError(
                f"Unsupported profiler: {profiler_type}. "
                f"Supported: {', '.join(cls._parsers.keys())}"
            )

        return parser_class()


def parse_profiler_output(profiler_type: str, data: str) -> list[FunctionProfile]:
    """
    Convenience function to parse profiler output.

    Args:
        profiler_type: Type of profiler ("cprofile", "chrome_devtools", etc.)
        data: Raw profiler output

    Returns:
        List of FunctionProfile objects

    Example:
        >>> profiles = parse_profiler_output("cprofile", profile_data)
        >>> for profile in profiles[:5]:  # Top 5 slowest
        ...     print(f"{profile.function_name}: {profile.total_time:.3f}s")
    """
    parser = ProfilerParserFactory.create(profiler_type)
    return parser.parse(data)
