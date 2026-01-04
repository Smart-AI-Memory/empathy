"""Tech Debt Adapter

Wraps empathy_software_plugin.wizards.tech_debt_wizard
and converts its output to the unified ToolResult format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from pathlib import Path
from typing import Any

from ..state import ToolResult


class TechDebtAdapter:
    """Adapter for the Tech Debt Wizard.

    Scans for TODOs, FIXMEs, tech debt markers, and tracks trajectory.
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
    ):
        """Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides

        """
        self.project_root = Path(project_root)
        self.config = config or {}

    async def analyze(self) -> ToolResult:
        """Run tech debt analysis and return unified result.

        Returns:
            ToolResult with tech debt findings

        """
        start_time = time.time()

        try:
            # Import here to handle optional dependency
            from empathy_software_plugin.wizards.tech_debt_wizard import TechDebtWizard

            wizard = TechDebtWizard()

            # Run analysis - wizard expects dict with project_path
            report = await wizard.analyze(
                {
                    "project_path": str(self.project_root),
                    "track_history": True,
                },
            )

            # Convert findings to unified format
            findings = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            for item in report.get("debt_items", []):
                severity = self._map_severity(item.get("severity", "medium"))
                findings_by_severity[severity] += 1

                finding = {
                    "finding_id": f"td_{len(findings)}",
                    "tool": "tech_debt",
                    "category": "debt",
                    "severity": severity,
                    "file_path": item.get("file_path", ""),
                    "line_number": item.get("line_number"),
                    "code": item.get("debt_type", "TODO"),
                    "message": item.get("content", ""),
                    "evidence": item.get("context", ""),
                    "confidence": 1.0,
                    "fixable": False,
                    "fix_command": None,
                }
                findings.append(finding)

            # Calculate score
            score = report.get("health_score", self._calculate_score(findings_by_severity))
            status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                tool_name="tech_debt",
                status=status,
                score=score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "trajectory": report.get("trajectory", {}),
                    "hotspots": report.get("hotspots", []),
                    "by_type": report.get("by_type", {}),
                },
                error_message="",
            )

        except ImportError:
            # Fallback: Simple pattern scanning
            return await self._fallback_analyze(start_time)
        except Exception as e:
            return self._create_error_result(str(e), start_time)

    async def _fallback_analyze(self, start_time: float) -> ToolResult:
        """Simple fallback analysis when wizard not available."""
        import re

        patterns = {
            "TODO": re.compile(r"#\s*TODO[:\s](.*)$", re.IGNORECASE | re.MULTILINE),
            "FIXME": re.compile(r"#\s*FIXME[:\s](.*)$", re.IGNORECASE | re.MULTILINE),
            "HACK": re.compile(r"#\s*HACK[:\s](.*)$", re.IGNORECASE | re.MULTILINE),
            "XXX": re.compile(r"#\s*XXX[:\s](.*)$", re.IGNORECASE | re.MULTILINE),
        }

        findings = []
        findings_by_severity: dict[str, int] = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }

        for py_file in self.project_root.rglob("*.py"):
            if any(
                part in py_file.parts for part in ["node_modules", ".venv", "__pycache__", ".git"]
            ):
                continue

            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.split("\n")

                for line_num, line in enumerate(lines, 1):
                    for debt_type, pattern in patterns.items():
                        match = pattern.search(line)
                        if match:
                            severity = self._get_debt_severity(debt_type)
                            findings_by_severity[severity] += 1

                            finding = {
                                "finding_id": f"td_{len(findings)}",
                                "tool": "tech_debt",
                                "category": "debt",
                                "severity": severity,
                                "file_path": str(py_file.relative_to(self.project_root)),
                                "line_number": line_num,
                                "code": debt_type,
                                "message": match.group(1).strip() if match.group(1) else debt_type,
                                "evidence": line.strip(),
                                "confidence": 1.0,
                                "fixable": False,
                                "fix_command": None,
                            }
                            findings.append(finding)
            except Exception:
                continue

        score = self._calculate_score(findings_by_severity)
        status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"
        duration_ms = int((time.time() - start_time) * 1000)

        return ToolResult(
            tool_name="tech_debt",
            status=status,
            score=score,
            findings_count=len(findings),
            findings=findings,
            findings_by_severity=findings_by_severity,
            duration_ms=duration_ms,
            metadata={"mode": "fallback"},
            error_message="",
        )

    def _map_severity(self, severity: str) -> str:
        """Map debt severity to unified severity."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
        }
        return mapping.get(severity.lower(), "medium")

    def _get_debt_severity(self, debt_type: str) -> str:
        """Get severity based on debt type."""
        mapping = {
            "FIXME": "high",
            "HACK": "high",
            "XXX": "medium",
            "TODO": "low",
        }
        return mapping.get(debt_type, "low")

    def _calculate_score(self, by_severity: dict[str, int]) -> int:
        """Calculate tech debt score."""
        penalties = {
            "critical": 15,
            "high": 8,
            "medium": 3,
            "low": 0.5,
            "info": 0,
        }

        total_penalty = sum(
            count * penalties.get(severity, 0) for severity, count in by_severity.items()
        )

        return max(0, int(100 - total_penalty))

    def _create_error_result(self, error: str, start_time: float) -> ToolResult:
        """Create an error result."""
        return ToolResult(
            tool_name="tech_debt",
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
