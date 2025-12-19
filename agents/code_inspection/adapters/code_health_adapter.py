"""
Code Health Adapter

Wraps empathy_llm_toolkit.code_health.HealthCheckRunner and converts
its output to the unified ToolResult format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from typing import Any

from ..state import ToolResult


class CodeHealthAdapter:
    """
    Adapter for the Code Health System.

    Wraps the HealthCheckRunner to provide lint, format, types, and security
    checks in a unified format.
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
        target_paths: list[str] | None = None,
    ):
        """
        Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides for health checks
            target_paths: Specific file paths to check (for staged/changed mode)
        """
        self.project_root = project_root
        self.config = config or {}
        self.target_paths = set(target_paths) if target_paths else None

    async def analyze(self) -> ToolResult:
        """
        Run code health checks and return unified result.

        Returns:
            ToolResult with aggregated findings
        """
        start_time = time.time()

        try:
            # Import here to handle optional dependency
            from empathy_llm_toolkit.code_health import HealthCheckRunner

            runner = HealthCheckRunner(
                project_root=self.project_root,
                config=self.config if self.config else None,
            )

            report = await runner.run_all()

            # Convert findings to unified format
            findings = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            for check_result in report.results:
                for issue in check_result.issues:
                    # Filter by target_paths if specified
                    if self.target_paths:
                        # Check if file is in target_paths (handle relative paths)
                        file_path = issue.file_path or ""
                        if not any(
                            file_path.endswith(tp) or tp in file_path for tp in self.target_paths
                        ):
                            continue

                    # Map severity
                    severity = self._map_severity(issue.severity)
                    findings_by_severity[severity] = findings_by_severity.get(severity, 0) + 1

                    finding = {
                        "finding_id": f"ch_{check_result.category.value}_{len(findings)}",
                        "tool": "code_health",
                        "category": check_result.category.value,
                        "severity": severity,
                        "file_path": issue.file_path,
                        "line_number": issue.line,
                        "code": issue.code,
                        "message": issue.message,
                        "evidence": "",
                        "confidence": 1.0,
                        "fixable": issue.fixable,
                        "fix_command": issue.fix_command,
                    }
                    findings.append(finding)

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                tool_name="code_health",
                status=report.status.value,
                score=report.overall_score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "total_fixable": report.total_fixable,
                    "results_by_category": {
                        r.category.value: {
                            "status": r.status.value,
                            "score": r.score,
                            "issue_count": r.issue_count,
                        }
                        for r in report.results
                    },
                },
                error_message="",
            )

        except ImportError:
            return self._create_skip_result("code_health module not available", start_time)
        except Exception as e:
            return self._create_error_result(str(e), start_time)

    def _map_severity(self, severity: str) -> str:
        """Map code_health severity to unified severity."""
        mapping = {
            "error": "high",
            "warning": "medium",
            "info": "info",
            "hint": "low",
        }
        return mapping.get(severity.lower(), "medium")

    def _create_skip_result(self, reason: str, start_time: float) -> ToolResult:
        """Create a skip result."""
        return ToolResult(
            tool_name="code_health",
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
            tool_name="code_health",
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
