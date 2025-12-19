"""
Debugging Adapter

Wraps both memory_enhanced_debugging_wizard and advanced_debugging_wizard
and converts their output to the unified ToolResult format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from pathlib import Path
from typing import Any

from ..state import HistoricalMatch, ToolResult


class DebuggingAdapter:
    """
    Adapter for the Debugging Wizards.

    Combines memory-enhanced debugging (historical bug correlation) and
    advanced debugging (systematic linter-based debugging).
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
    ):
        """
        Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides
        """
        self.project_root = Path(project_root)
        self.config = config or {}

    async def analyze_memory_enhanced(self) -> ToolResult:
        """
        Analyze historical bug patterns in the patterns directory.

        Note: The MemoryEnhancedDebuggingWizard is designed for analyzing
        specific bugs with error_message, stack_trace, etc. For code inspection,
        we scan the patterns directory for unresolved bug patterns instead.

        Returns:
            ToolResult with historical matches and recommendations
        """
        import json

        start_time = time.time()

        findings = []
        findings_by_severity: dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        historical_matches: list[HistoricalMatch] = []

        # Scan patterns directory for unresolved bugs
        patterns_dir = self.project_root / "patterns" / "debugging"
        patterns_checked = 0

        if patterns_dir.exists():
            for pattern_file in patterns_dir.glob("bug_*.json"):
                patterns_checked += 1
                try:
                    with open(pattern_file) as f:
                        pattern = json.load(f)

                    # Only include unresolved patterns as findings
                    status_val = pattern.get("status", "investigating")
                    if status_val == "resolved":
                        continue

                    severity = self._get_severity_from_match(pattern)
                    findings_by_severity[severity] += 1

                    finding = {
                        "finding_id": f"md_{len(findings)}",
                        "tool": "memory_debugging",
                        "category": "debugging",
                        "severity": severity,
                        "file_path": pattern.get("file_path", ""),
                        "line_number": pattern.get("line_number"),
                        "code": pattern.get("error_type", "UNRESOLVED_BUG"),
                        "message": f"Unresolved bug: {pattern.get('error_type', 'unknown')}",
                        "evidence": pattern.get("error_message", ""),
                        "confidence": 0.9,
                        "fixable": False,
                        "fix_command": None,
                        "remediation": pattern.get("suggested_fix", ""),
                    }
                    findings.append(finding)

                    historical_matches.append(
                        HistoricalMatch(
                            pattern_id=pattern_file.stem,
                            error_type=pattern.get("error_type", ""),
                            similarity_score=0.9,
                            file_path=pattern.get("file_path", ""),
                            matched_code=pattern.get("error_message", ""),
                            historical_fix=pattern.get("suggested_fix", ""),
                            resolution_time_minutes=0,
                        )
                    )
                except (json.JSONDecodeError, KeyError, OSError):
                    continue

        # Calculate score - 100 if no unresolved bugs
        score = self._calculate_score(findings_by_severity)
        status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

        duration_ms = int((time.time() - start_time) * 1000)

        return ToolResult(
            tool_name="memory_debugging",
            status=status,
            score=score,
            findings_count=len(findings),
            findings=findings,
            findings_by_severity=findings_by_severity,
            duration_ms=duration_ms,
            metadata={
                "historical_matches": [dict(m) for m in historical_matches],
                "patterns_checked": patterns_checked,
                "patterns_dir": str(patterns_dir),
                "mode": "inspection",
            },
            error_message="",
        )

    async def analyze_advanced(self) -> ToolResult:
        """
        Run advanced debugging (systematic linter-based).

        Returns:
            ToolResult with systematic debugging findings
        """
        start_time = time.time()

        try:
            from empathy_software_plugin.wizards.advanced_debugging_wizard import (
                AdvancedDebuggingWizard,
            )

            wizard = AdvancedDebuggingWizard()

            # Run analysis - wizard expects 'project_path', not 'project_root'
            report = await wizard.analyze(
                {
                    "project_path": str(self.project_root),
                    "linters": {},  # Will use defaults
                    "auto_fix": False,
                    "verify": False,
                }
            )

            # Convert to unified format
            findings = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            for issue in report.get("issues", []):
                severity = self._map_severity(issue.get("severity", "medium"))
                findings_by_severity[severity] += 1

                finding = {
                    "finding_id": f"ad_{len(findings)}",
                    "tool": "advanced_debugging",
                    "category": "debugging",
                    "severity": severity,
                    "file_path": issue.get("file_path", ""),
                    "line_number": issue.get("line_number"),
                    "code": issue.get("rule_id", "DEBUG"),
                    "message": issue.get("message", ""),
                    "evidence": issue.get("code_snippet", ""),
                    "confidence": issue.get("confidence", 0.8),
                    "fixable": issue.get("fixable", False),
                    "fix_command": issue.get("fix_command"),
                    "remediation": issue.get("recommendation", ""),
                }
                findings.append(finding)

            # Calculate score
            score = self._calculate_score(findings_by_severity)
            status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                tool_name="advanced_debugging",
                status=status,
                score=score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "linters_used": report.get("linters_used", []),
                    "risk_assessments": report.get("risk_assessments", []),
                },
                error_message="",
            )

        except ImportError:
            return self._create_skip_result(
                "advanced_debugging_wizard not available",
                start_time,
                "advanced_debugging",
            )
        except Exception as e:
            return self._create_error_result(str(e), start_time, "advanced_debugging")

    def _get_severity_from_match(self, match: dict) -> str:
        """Determine severity based on historical match data."""
        similarity = match.get("similarity_score", 0.5)
        error_type = match.get("error_type", "").lower()

        # High severity for known critical patterns
        if any(critical in error_type for critical in ["null", "security", "crash", "injection"]):
            return "high"

        # Medium for high-similarity matches
        if similarity >= 0.8:
            return "medium"

        return "low"

    def _map_severity(self, severity: str) -> str:
        """Map wizard severity to unified severity."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "warning": "medium",
        }
        return mapping.get(severity.lower(), "medium")

    def _calculate_score(self, by_severity: dict[str, int]) -> int:
        """Calculate debugging score."""
        penalties = {
            "critical": 20,
            "high": 12,
            "medium": 5,
            "low": 1,
            "info": 0,
        }

        total_penalty = sum(
            count * penalties.get(severity, 0) for severity, count in by_severity.items()
        )

        return max(0, 100 - total_penalty)

    def _create_skip_result(self, reason: str, start_time: float, tool_name: str) -> ToolResult:
        """Create a skip result."""
        return ToolResult(
            tool_name=tool_name,
            status="skip",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={"skip_reason": reason},
            error_message="",
        )

    def _create_error_result(self, error: str, start_time: float, tool_name: str) -> ToolResult:
        """Create an error result."""
        return ToolResult(
            tool_name=tool_name,
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
