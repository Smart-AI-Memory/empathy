"""
Test Quality Adapter

Wraps empathy_software_plugin.wizards.testing.quality_analyzer
and converts its output to the unified ToolResult format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from pathlib import Path
from typing import Any

from ..state import ToolResult


class TestQualityAdapter:
    """
    Adapter for the Test Quality Analyzer.

    Detects flaky tests, weak assertions, slow tests, and test anti-patterns.
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
        test_dirs: list[str] | None = None,
    ):
        """
        Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides
            test_dirs: Directories to scan for tests (defaults to ["tests"])
        """
        self.project_root = Path(project_root)
        self.config = config or {}
        self.test_dirs = test_dirs or ["tests", "test"]

    async def analyze(self) -> ToolResult:
        """
        Run test quality analysis and return unified result.

        Returns:
            ToolResult with test quality findings
        """
        start_time = time.time()

        try:
            # Import here to handle optional dependency
            from empathy_software_plugin.wizards.testing.quality_analyzer import TestQualityAnalyzer

            analyzer = TestQualityAnalyzer()

            # Collect all findings
            findings = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }
            files_analyzed = 0

            # Find test files
            for test_dir in self.test_dirs:
                test_path = self.project_root / test_dir
                if not test_path.exists():
                    continue

                for test_file in test_path.rglob("test_*.py"):
                    files_analyzed += 1
                    try:
                        report = analyzer.analyze_test_file(str(test_file))

                        for issue in report.issues:
                            severity = self._map_severity(issue.severity)
                            findings_by_severity[severity] += 1

                            finding = {
                                "finding_id": f"tq_{len(findings)}",
                                "tool": "test_quality",
                                "category": "tests",
                                "severity": severity,
                                "file_path": str(test_file.relative_to(self.project_root)),
                                "line_number": issue.line_number,
                                "code": issue.issue_type,
                                "message": issue.description,
                                "evidence": issue.code_snippet or "",
                                "confidence": issue.confidence,
                                "fixable": False,
                                "fix_command": None,
                                "remediation": issue.suggestion or "",
                            }
                            findings.append(finding)
                    except Exception:
                        # Skip files that can't be analyzed
                        continue

            # Calculate score
            score = self._calculate_score(findings_by_severity, files_analyzed)
            status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                tool_name="test_quality",
                status=status,
                score=score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "files_analyzed": files_analyzed,
                    "test_dirs_searched": self.test_dirs,
                },
                error_message="",
            )

        except ImportError:
            return self._create_skip_result("quality_analyzer module not available", start_time)
        except Exception as e:
            return self._create_error_result(str(e), start_time)

    def _map_severity(self, severity: str) -> str:
        """Map analyzer severity to unified severity."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "warning": "medium",
        }
        return mapping.get(severity.lower(), "medium")

    def _calculate_score(self, by_severity: dict[str, int], files_analyzed: int) -> int:
        """Calculate test quality score."""
        if files_analyzed == 0:
            return 100  # No test files to analyze

        # Penalties per issue
        penalties = {
            "critical": 20,
            "high": 10,
            "medium": 3,
            "low": 1,
            "info": 0,
        }

        total_penalty = sum(
            count * penalties.get(severity, 0) for severity, count in by_severity.items()
        )

        return max(0, 100 - total_penalty)

    def _create_skip_result(self, reason: str, start_time: float) -> ToolResult:
        """Create a skip result."""
        return ToolResult(
            tool_name="test_quality",
            status="skip",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={"skip_reason": reason},
            error_message="",
        )

    def _create_error_result(self, error: str, start_time: float) -> ToolResult:
        """Create an error result."""
        return ToolResult(
            tool_name="test_quality",
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
