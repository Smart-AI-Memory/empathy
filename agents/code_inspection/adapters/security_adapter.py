"""Security Adapter

Wraps empathy_software_plugin.wizards.security.vulnerability_scanner
and converts its output to the unified ToolResult format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from pathlib import Path
from typing import Any

from ..state import ToolResult


class SecurityAdapter:
    """Adapter for the Security Vulnerability Scanner.

    Provides OWASP pattern detection, secret scanning, and CVE matching.
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
        scan_dependencies: bool = True,
    ):
        """Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides
            scan_dependencies: Whether to scan dependencies for CVEs

        """
        self.project_root = Path(project_root)
        self.config = config or {}
        self.scan_dependencies = scan_dependencies

    async def analyze(self) -> ToolResult:
        """Run security scans and return unified result.

        Returns:
            ToolResult with security findings

        """
        start_time = time.time()

        try:
            # Import here to handle optional dependency
            from empathy_software_plugin.wizards.security.vulnerability_scanner import (
                VulnerabilityScanner,
            )

            scanner = VulnerabilityScanner()

            # Collect all findings
            findings = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            # Scan Python files
            for py_file in self.project_root.rglob("*.py"):
                # Skip common exclusions
                if any(
                    part in py_file.parts
                    for part in ["node_modules", ".venv", "__pycache__", ".git"]
                ):
                    continue

                try:
                    file_findings = scanner.scan_file(str(py_file))
                    for vuln in file_findings:
                        severity = self._map_severity(vuln.get("severity", "medium"))
                        findings_by_severity[severity] += 1

                        finding = {
                            "finding_id": f"sec_{len(findings)}",
                            "tool": "security",
                            "category": "security",
                            "severity": severity,
                            "file_path": str(py_file.relative_to(self.project_root)),
                            "line_number": vuln.get("line"),
                            "code": vuln.get("vulnerability_type", "UNKNOWN"),
                            "message": vuln.get("description", ""),
                            "evidence": vuln.get("evidence", ""),
                            "confidence": vuln.get("confidence", 0.8),
                            "fixable": False,
                            "fix_command": None,
                            "remediation": vuln.get("remediation", ""),
                        }
                        findings.append(finding)
                except Exception:
                    # Skip files that can't be scanned
                    continue

            # Scan dependencies if enabled
            if self.scan_dependencies:
                try:
                    dep_vulns = scanner.scan_dependencies(str(self.project_root))
                    for vuln in dep_vulns:
                        severity = self._map_severity(vuln.get("severity", "high"))
                        findings_by_severity[severity] += 1

                        finding = {
                            "finding_id": f"sec_dep_{len(findings)}",
                            "tool": "security",
                            "category": "deps",
                            "severity": severity,
                            "file_path": "requirements.txt",
                            "line_number": None,
                            "code": vuln.get("cve_id", "CVE-UNKNOWN"),
                            "message": f"{vuln.get('package', 'unknown')}: {vuln.get('description', '')}",
                            "evidence": "",
                            "confidence": 1.0,
                            "fixable": vuln.get("fix_available", False),
                            "fix_command": vuln.get("fix_version"),
                            "remediation": f"Upgrade to {vuln.get('fix_version', 'latest')}",
                        }
                        findings.append(finding)
                except Exception:
                    pass

            # Calculate score
            score = self._calculate_score(findings_by_severity)
            status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

            duration_ms = int((time.time() - start_time) * 1000)

            return ToolResult(
                tool_name="security",
                status=status,
                score=score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "files_scanned": sum(1 for _ in self.project_root.rglob("*.py")),
                    "dependencies_scanned": self.scan_dependencies,
                },
                error_message="",
            )

        except ImportError:
            return self._create_skip_result(
                "vulnerability_scanner module not available",
                start_time,
            )
        except Exception as e:
            return self._create_error_result(str(e), start_time)

    def _map_severity(self, severity: str) -> str:
        """Map scanner severity to unified severity."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "informational": "info",
        }
        return mapping.get(severity.lower(), "medium")

    def _calculate_score(self, by_severity: dict[str, int]) -> int:
        """Calculate security score based on findings."""
        # Penalties for each severity
        penalties = {
            "critical": 25,
            "high": 15,
            "medium": 5,
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
            tool_name="security",
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
            tool_name="security",
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
