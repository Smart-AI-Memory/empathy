"""Code Health Assistant Module

A comprehensive system for running health checks, tracking trends,
and auto-fixing common issues in codebases.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import json
import logging
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class HealthStatus(Enum):
    """Health check result status."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


class CheckCategory(Enum):
    """Categories of health checks."""

    LINT = "lint"
    FORMAT = "format"
    TYPES = "types"
    TESTS = "tests"
    COVERAGE = "coverage"
    SECURITY = "security"
    DEPS = "deps"


# Priority weights for health check categories
CHECK_WEIGHTS = {
    CheckCategory.SECURITY: 100,
    CheckCategory.TYPES: 90,
    CheckCategory.TESTS: 85,
    CheckCategory.LINT: 70,
    CheckCategory.FORMAT: 50,
    CheckCategory.COVERAGE: 40,
    CheckCategory.DEPS: 30,
}

# Default thresholds
DEFAULT_THRESHOLDS = {
    "good": 85,
    "warning": 70,
    "critical": 50,
}

# Default configuration
DEFAULT_CONFIG = {
    "checks": {
        "lint": {"enabled": True, "tool": "ruff", "weight": 70},
        "format": {"enabled": True, "tool": "black", "weight": 50},
        "types": {"enabled": True, "tool": "pyright", "weight": 90},
        "tests": {"enabled": True, "tool": "pytest", "weight": 85, "coverage_target": 80},
        "security": {"enabled": True, "tool": "bandit", "weight": 100},
        "deps": {"enabled": True, "tool": "pip-audit", "weight": 30},
    },
    "thresholds": DEFAULT_THRESHOLDS,
    "auto_fix": {
        "safe_fixes": True,
        "prompt_fixes": True,
        "categories": ["lint", "format"],
    },
}


@dataclass
class HealthIssue:
    """A single health check issue."""

    category: CheckCategory
    file_path: str
    line: int | None
    code: str
    message: str
    severity: str = "warning"  # warning, error
    fixable: bool = False
    fix_command: str | None = None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "file_path": self.file_path,
            "line": self.line,
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
            "fixable": self.fixable,
            "fix_command": self.fix_command,
        }


@dataclass
class CheckResult:
    """Result of a single health check."""

    category: CheckCategory
    status: HealthStatus
    score: int  # 0-100
    issues: list[HealthIssue] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)
    duration_ms: int = 0
    tool_used: str = ""

    @property
    def issue_count(self) -> int:
        """Return total issue count."""
        return len(self.issues)

    @property
    def fixable_count(self) -> int:
        """Return fixable issue count."""
        return sum(1 for i in self.issues if i.fixable)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "category": self.category.value,
            "status": self.status.value,
            "score": self.score,
            "issue_count": self.issue_count,
            "fixable_count": self.fixable_count,
            "issues": [i.to_dict() for i in self.issues],
            "details": self.details,
            "duration_ms": self.duration_ms,
            "tool_used": self.tool_used,
        }


@dataclass
class HealthReport:
    """Complete health report from all checks."""

    results: list[CheckResult] = field(default_factory=list)
    overall_score: int = 100
    status: HealthStatus = HealthStatus.PASS
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    project_root: str = "."

    def add_result(self, result: CheckResult) -> None:
        """Add a check result to the report."""
        self.results.append(result)
        self._recalculate_score()

    def _recalculate_score(self) -> None:
        """Recalculate overall score based on weighted results."""
        if not self.results:
            self.overall_score = 100
            self.status = HealthStatus.PASS
            return

        total_weight = 0
        weighted_score = 0

        for result in self.results:
            if result.status != HealthStatus.SKIP:
                weight = CHECK_WEIGHTS.get(result.category, 50)
                weighted_score += result.score * weight
                total_weight += weight

        if total_weight > 0:
            self.overall_score = int(weighted_score / total_weight)
        else:
            self.overall_score = 100

        # Determine overall status
        if self.overall_score >= DEFAULT_THRESHOLDS["good"]:
            self.status = HealthStatus.PASS
        elif self.overall_score >= DEFAULT_THRESHOLDS["warning"]:
            self.status = HealthStatus.WARN
        else:
            self.status = HealthStatus.FAIL

    @property
    def total_issues(self) -> int:
        """Return total issues across all checks."""
        return sum(r.issue_count for r in self.results)

    @property
    def total_fixable(self) -> int:
        """Return total fixable issues."""
        return sum(r.fixable_count for r in self.results)

    def get_result(self, category: CheckCategory) -> CheckResult | None:
        """Get result for a specific category."""
        for result in self.results:
            if result.category == category:
                return result
        return None

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "overall_score": self.overall_score,
            "status": self.status.value,
            "total_issues": self.total_issues,
            "total_fixable": self.total_fixable,
            "generated_at": self.generated_at,
            "project_root": self.project_root,
            "results": [r.to_dict() for r in self.results],
        }


class HealthCheckRunner:
    """Run configurable health checks and aggregate results."""

    def __init__(
        self,
        project_root: str = ".",
        config: dict | None = None,
    ):
        """Initialize the health check runner.

        Args:
            project_root: Root directory of the project
            config: Configuration dictionary (uses defaults if not provided)

        """
        self.project_root = Path(project_root).resolve()
        self.config = {**DEFAULT_CONFIG, **(config or {})}
        self._check_handlers = {
            CheckCategory.LINT: self._run_lint_check,
            CheckCategory.FORMAT: self._run_format_check,
            CheckCategory.TYPES: self._run_type_check,
            CheckCategory.TESTS: self._run_test_check,
            CheckCategory.SECURITY: self._run_security_check,
            CheckCategory.DEPS: self._run_deps_check,
        }

    def _is_tool_available(self, tool: str) -> bool:
        """Check if a tool is available on the system."""
        return shutil.which(tool) is not None

    async def run_all(self) -> HealthReport:
        """Run all enabled health checks."""
        report = HealthReport(project_root=str(self.project_root))

        tasks = []
        for category in CheckCategory:
            check_config = self.config["checks"].get(category.value, {})
            if check_config.get("enabled", False):
                handler = self._check_handlers.get(category)
                if handler:
                    tasks.append(self._run_check_async(category, handler, check_config))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, CheckResult):
                report.add_result(result)
            elif isinstance(result, Exception):
                # Log error but continue with other checks
                pass

        return report

    async def run_quick(self) -> HealthReport:
        """Run fast checks only (lint, format, types)."""
        report = HealthReport(project_root=str(self.project_root))

        quick_checks = [CheckCategory.LINT, CheckCategory.FORMAT, CheckCategory.TYPES]
        tasks = []

        for category in quick_checks:
            check_config = self.config["checks"].get(category.value, {})
            if check_config.get("enabled", False):
                handler = self._check_handlers.get(category)
                if handler:
                    tasks.append(self._run_check_async(category, handler, check_config))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, CheckResult):
                report.add_result(result)

        return report

    async def run_check(self, category: CheckCategory) -> CheckResult:
        """Run a specific health check."""
        check_config = self.config["checks"].get(category.value, {})
        handler = self._check_handlers.get(category)

        if not handler:
            return CheckResult(
                category=category,
                status=HealthStatus.ERROR,
                score=0,
                details={"error": f"No handler for {category.value}"},
            )

        return await self._run_check_async(category, handler, check_config)

    async def _run_check_async(
        self,
        category: CheckCategory,
        handler,
        config: dict,
    ) -> CheckResult:
        """Run a check handler asynchronously.

        This uses broad exception handling intentionally for graceful degradation.
        Health checks are optional features - the system should continue even if some checks fail.

        Note:
            Full exception context is preserved via logger.exception() for debugging.
        """
        start_time = datetime.now()
        try:
            result: CheckResult = await asyncio.to_thread(handler, config)
            result.duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return result
        except Exception as e:
            # INTENTIONAL: Broad exception handler for graceful degradation of optional checks
            # Full traceback preserved for debugging
            logger.exception(f"Health check failed for {category.value}: {e}")
            return CheckResult(
                category=category,
                status=HealthStatus.ERROR,
                score=0,
                details={"error": str(e)},
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
            )

    def _run_lint_check(self, config: dict) -> CheckResult:
        """Run linting check using ruff or flake8."""
        tool = config.get("tool", "ruff")
        issues = []

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.LINT,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            if tool == "ruff":
                result = subprocess.run(
                    ["ruff", "check", "--output-format=json", str(self.project_root)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )
                if result.stdout:
                    ruff_issues = json.loads(result.stdout)
                    for item in ruff_issues:
                        issues.append(
                            HealthIssue(
                                category=CheckCategory.LINT,
                                file_path=item.get("filename", ""),
                                line=item.get("location", {}).get("row"),
                                code=item.get("code", ""),
                                message=item.get("message", ""),
                                severity=(
                                    "warning" if item.get("code", "").startswith("W") else "error"
                                ),
                                fixable=item.get("fix") is not None,
                                fix_command="ruff check --fix" if item.get("fix") else None,
                            ),
                        )
            else:
                # Fallback to flake8
                result = subprocess.run(
                    ["flake8", "--format=json", str(self.project_root)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )
                # Parse flake8 output...

            # Calculate score based on issues
            score = max(0, 100 - len(issues) * 5)  # -5 per issue
            status = HealthStatus.PASS if not issues else HealthStatus.WARN

            return CheckResult(
                category=CheckCategory.LINT,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={"total_files_checked": len({i.file_path for i in issues}) or "all"},
            )

        except json.JSONDecodeError as e:
            # Tool output not in expected JSON format
            logger.warning(f"Lint check JSON parse error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.LINT,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to parse {tool} output: {e}"},
            )
        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Lint check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.LINT,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in lint check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.LINT,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _run_format_check(self, config: dict) -> CheckResult:
        """Run formatting check using black or prettier."""
        tool = config.get("tool", "black")
        issues = []

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.FORMAT,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            if tool == "black":
                result = subprocess.run(
                    ["black", "--check", "--diff", str(self.project_root)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )

                if result.returncode != 0:
                    # Parse diff output to find files needing formatting
                    lines = result.stdout.split("\n") if result.stdout else []
                    current_file = None
                    for line in lines:
                        if line.startswith("--- "):
                            current_file = line[4:].split("\t")[0]
                        elif current_file and line.startswith("would reformat"):
                            issues.append(
                                HealthIssue(
                                    category=CheckCategory.FORMAT,
                                    file_path=current_file,
                                    line=None,
                                    code="FORMAT",
                                    message="File needs reformatting",
                                    severity="warning",
                                    fixable=True,
                                    fix_command=f"black {current_file}",
                                ),
                            )

                    # Also check stderr for files that would be reformatted
                    if result.stderr:
                        for line in result.stderr.split("\n"):
                            if "would reformat" in line:
                                file_path = line.replace("would reformat ", "").strip()
                                if file_path and not any(i.file_path == file_path for i in issues):
                                    issues.append(
                                        HealthIssue(
                                            category=CheckCategory.FORMAT,
                                            file_path=file_path,
                                            line=None,
                                            code="FORMAT",
                                            message="File needs reformatting",
                                            severity="warning",
                                            fixable=True,
                                            fix_command=f"black {file_path}",
                                        ),
                                    )

            score = max(0, 100 - len(issues) * 10)  # -10 per file
            status = HealthStatus.PASS if not issues else HealthStatus.WARN

            return CheckResult(
                category=CheckCategory.FORMAT,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={"files_need_formatting": len(issues)},
            )

        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Format check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.FORMAT,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in format check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.FORMAT,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _run_type_check(self, config: dict) -> CheckResult:
        """Run type checking using pyright or mypy."""
        tool = config.get("tool", "pyright")
        issues = []

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.TYPES,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            if tool == "pyright":
                result = subprocess.run(
                    ["pyright", "--outputjson"],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )

                if result.stdout:
                    try:
                        data = json.loads(result.stdout)
                        diagnostics = data.get("generalDiagnostics", [])
                        for diag in diagnostics:
                            issues.append(
                                HealthIssue(
                                    category=CheckCategory.TYPES,
                                    file_path=diag.get("file", ""),
                                    line=diag.get("range", {}).get("start", {}).get("line"),
                                    code=diag.get("rule", "TYPE"),
                                    message=diag.get("message", ""),
                                    severity="error" if diag.get("severity") == 1 else "warning",
                                    fixable=False,
                                ),
                            )
                    except json.JSONDecodeError:
                        pass

            elif tool == "mypy":
                result = subprocess.run(
                    ["mypy", "--show-error-codes", "--no-error-summary", str(self.project_root)],
                    check=False,
                    capture_output=True,
                    text=True,
                    cwd=str(self.project_root),
                )

                if result.stdout:
                    for line in result.stdout.split("\n"):
                        if ": error:" in line or ": note:" in line:
                            parts = line.split(":", 3)
                            if len(parts) >= 4:
                                issues.append(
                                    HealthIssue(
                                        category=CheckCategory.TYPES,
                                        file_path=parts[0],
                                        line=int(parts[1]) if parts[1].isdigit() else None,
                                        code="TYPE",
                                        message=parts[3].strip() if len(parts) > 3 else "",
                                        severity="error",
                                        fixable=False,
                                    ),
                                )

            score = max(0, 100 - len(issues) * 10)  # -10 per type error
            status = (
                HealthStatus.PASS
                if not issues
                else (HealthStatus.FAIL if len(issues) > 5 else HealthStatus.WARN)
            )

            return CheckResult(
                category=CheckCategory.TYPES,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={"type_errors": len(issues)},
            )

        except json.JSONDecodeError as e:
            # Tool output not in expected JSON format (pyright specific)
            logger.warning(f"Type check JSON parse error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.TYPES,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to parse {tool} output: {e}"},
            )
        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Type check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.TYPES,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in type check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.TYPES,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _run_test_check(self, config: dict) -> CheckResult:
        """Run test suite using pytest."""
        tool = config.get("tool", "pytest")

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.TESTS,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            result = subprocess.run(
                ["pytest", "--tb=no", "-q", "--co", "-q"],  # Collect only, quiet
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )

            # Count collected tests
            test_count = 0
            for line in result.stdout.split("\n"):
                if "test" in line.lower() and "::" in line:
                    test_count += 1

            # Run actual tests
            result = subprocess.run(
                ["pytest", "--tb=short", "-q"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
                timeout=300,  # 5 minute timeout
            )

            passed = 0
            failed = 0
            issues = []

            # Parse pytest output
            for line in result.stdout.split("\n"):
                if " passed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "passed" and i > 0:
                            try:
                                passed = int(parts[i - 1])
                            except ValueError:
                                pass
                if " failed" in line:
                    parts = line.split()
                    for i, part in enumerate(parts):
                        if part == "failed" and i > 0:
                            try:
                                failed = int(parts[i - 1])
                            except ValueError:
                                pass

            # Create issues for failed tests
            if result.returncode != 0 and result.stdout:
                lines = result.stdout.split("\n")
                for line in lines:
                    if "FAILED" in line:
                        # Extract test name and file
                        if "::" in line:
                            test_path = (
                                line.split("FAILED")[1].strip() if "FAILED" in line else line
                            )
                            test_path = test_path.split(" -")[0].strip()
                            file_part = test_path.split("::")[0] if "::" in test_path else test_path
                            issues.append(
                                HealthIssue(
                                    category=CheckCategory.TESTS,
                                    file_path=file_part,
                                    line=None,
                                    code="TEST_FAIL",
                                    message=f"Test failed: {test_path}",
                                    severity="error",
                                    fixable=False,
                                ),
                            )

            total = passed + failed
            score = int((passed / total) * 100) if total > 0 else 100
            status = HealthStatus.PASS if failed == 0 else HealthStatus.FAIL

            return CheckResult(
                category=CheckCategory.TESTS,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={
                    "passed": passed,
                    "failed": failed,
                    "total": total,
                },
            )

        except subprocess.TimeoutExpired:
            # Tests took too long - specific timeout error
            logger.error(f"Test check timeout ({tool}): Tests took longer than 5 minutes")
            return CheckResult(
                category=CheckCategory.TESTS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": "Test suite timed out after 5 minutes"},
            )
        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Test check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.TESTS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in test check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.TESTS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _run_security_check(self, config: dict) -> CheckResult:
        """Run security check using bandit."""
        tool = config.get("tool", "bandit")
        issues = []

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.SECURITY,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            result = subprocess.run(
                ["bandit", "-r", "-f", "json", str(self.project_root)],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data.get("results", []):
                        severity = item.get("issue_severity", "LOW")
                        issues.append(
                            HealthIssue(
                                category=CheckCategory.SECURITY,
                                file_path=item.get("filename", ""),
                                line=item.get("line_number"),
                                code=item.get("test_id", ""),
                                message=item.get("issue_text", ""),
                                severity="error" if severity in ["HIGH", "MEDIUM"] else "warning",
                                fixable=False,
                            ),
                        )
                except json.JSONDecodeError:
                    pass

            # Weight by severity
            high_count = sum(1 for i in issues if i.severity == "error")
            low_count = len(issues) - high_count
            score = max(0, 100 - high_count * 20 - low_count * 5)
            status = (
                HealthStatus.PASS
                if not issues
                else (HealthStatus.FAIL if high_count > 0 else HealthStatus.WARN)
            )

            return CheckResult(
                category=CheckCategory.SECURITY,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={
                    "high_severity": high_count,
                    "low_severity": low_count,
                },
            )

        except json.JSONDecodeError as e:
            # Tool output not in expected JSON format
            logger.warning(f"Security check JSON parse error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.SECURITY,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to parse {tool} output: {e}"},
            )
        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Security check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.SECURITY,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in security check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.SECURITY,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _run_deps_check(self, config: dict) -> CheckResult:
        """Run dependency check using pip-audit."""
        tool = config.get("tool", "pip-audit")
        issues = []

        if not self._is_tool_available(tool):
            return CheckResult(
                category=CheckCategory.DEPS,
                status=HealthStatus.SKIP,
                score=100,
                tool_used=tool,
                details={"skip_reason": f"{tool} not available"},
            )

        try:
            result = subprocess.run(
                ["pip-audit", "--format=json"],
                check=False,
                capture_output=True,
                text=True,
                cwd=str(self.project_root),
            )

            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for item in data:
                        issues.append(
                            HealthIssue(
                                category=CheckCategory.DEPS,
                                file_path="requirements.txt",
                                line=None,
                                code=item.get("id", "VULN"),
                                message=f"{item.get('name')}: {item.get('description', 'Vuln')}",
                                severity="error" if item.get("fix_versions") else "warning",
                                fixable=bool(item.get("fix_versions")),
                                fix_command=self._get_fix_cmd(item),
                            ),
                        )
                except json.JSONDecodeError:
                    pass

            score = max(0, 100 - len(issues) * 15)
            status = HealthStatus.PASS if not issues else HealthStatus.WARN

            return CheckResult(
                category=CheckCategory.DEPS,
                status=status,
                score=score,
                issues=issues,
                tool_used=tool,
                details={"vulnerable_packages": len(issues)},
            )

        except json.JSONDecodeError as e:
            # Tool output not in expected JSON format
            logger.warning(f"Dependency check JSON parse error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.DEPS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to parse {tool} output: {e}"},
            )
        except subprocess.SubprocessError as e:
            # Tool execution failed
            logger.error(f"Dependency check subprocess error ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.DEPS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": f"Failed to run {tool}: {e}"},
            )
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional check
            logger.exception(f"Unexpected error in dependency check ({tool}): {e}")
            return CheckResult(
                category=CheckCategory.DEPS,
                status=HealthStatus.ERROR,
                score=0,
                tool_used=tool,
                details={"error": str(e)},
            )

    def _get_fix_cmd(self, item: dict) -> str | None:
        """Get pip install command to fix a vulnerable package."""
        fix_versions = item.get("fix_versions")
        if fix_versions:
            return f"pip install {item.get('name')}=={fix_versions[0]}"
        return None


class AutoFixer:
    """Apply automatic fixes to code health issues."""

    def __init__(self, config: dict[str, Any] | None = None):
        """Initialize the auto-fixer."""
        self.config: dict[str, Any] = config or DEFAULT_CONFIG.get("auto_fix", {})  # type: ignore[assignment]
        self.safe_fixes = self.config.get("safe_fixes", True)
        self.prompt_fixes = self.config.get("prompt_fixes", True)

    def preview_fixes(self, report: HealthReport) -> list[dict]:
        """Show what would be fixed without applying."""
        fixes = []
        for result in report.results:
            for issue in result.issues:
                if issue.fixable and issue.fix_command:
                    fixes.append(
                        {
                            "category": issue.category.value,
                            "file": issue.file_path,
                            "issue": issue.message,
                            "fix_command": issue.fix_command,
                            "safe": self._is_safe_fix(issue),
                        },
                    )
        return fixes

    def _is_safe_fix(self, issue: HealthIssue) -> bool:
        """Determine if a fix is safe to apply automatically."""
        safe_codes = ["FORMAT", "W291", "W292", "W293", "I001"]  # Whitespace, imports
        return issue.code in safe_codes or issue.category == CheckCategory.FORMAT

    async def fix_all(self, report: HealthReport, interactive: bool = False) -> dict[str, Any]:
        """Apply all safe fixes, optionally prompt for others."""
        results: dict[str, Any] = {
            "fixed": [],
            "skipped": [],
            "failed": [],
        }

        for result in report.results:
            for issue in result.issues:
                if issue.fixable and issue.fix_command:
                    if self._is_safe_fix(issue):
                        success = await self._apply_fix(issue)
                        if success:
                            results["fixed"].append(issue.to_dict())
                        else:
                            results["failed"].append(issue.to_dict())
                    elif interactive and self.prompt_fixes:
                        # In interactive mode, we'd prompt here
                        results["skipped"].append(issue.to_dict())
                    else:
                        results["skipped"].append(issue.to_dict())

        return results

    async def fix_category(self, report: HealthReport, category: CheckCategory) -> dict[str, Any]:
        """Fix issues in a specific category."""
        results: dict[str, Any] = {
            "fixed": [],
            "skipped": [],
            "failed": [],
        }

        result = report.get_result(category)
        if not result:
            return results

        for issue in result.issues:
            if issue.fixable and issue.fix_command:
                success = await self._apply_fix(issue)
                if success:
                    results["fixed"].append(issue.to_dict())
                else:
                    results["failed"].append(issue.to_dict())

        return results

    async def _apply_fix(self, issue: HealthIssue) -> bool:
        """Apply a single fix.

        This uses broad exception handling intentionally for graceful degradation.
        Auto-fixes are optional - the system should continue even if some fixes fail.

        Note:
            Full exception context is preserved via logger.exception() for debugging.
        """
        if not issue.fix_command:
            return False

        try:
            result = await asyncio.to_thread(
                subprocess.run,
                issue.fix_command.split(),
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except subprocess.SubprocessError as e:
            # Fix command execution failed
            logger.error(f"Auto-fix subprocess error for {issue.file_path}: {e}")
            return False
        except Exception as e:
            # Unexpected errors - preserve full context for debugging
            # INTENTIONAL: Broad handler for graceful degradation of optional auto-fix
            logger.exception(f"Unexpected error applying fix to {issue.file_path}: {e}")
            return False


class HealthTrendTracker:
    """Track code health trends and identify patterns."""

    def __init__(self, project_root: str = "."):
        """Initialize the trend tracker."""
        self.project_root = Path(project_root)
        self.history_dir = self.project_root / ".empathy" / "health_history"
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def record_check(self, report: HealthReport) -> None:
        """Save health check to history."""
        today = datetime.now().strftime("%Y-%m-%d")
        filepath = self.history_dir / f"{today}.json"

        # Load existing or create new
        history = []
        if filepath.exists():
            try:
                history = json.loads(filepath.read_text())
            except json.JSONDecodeError:
                history = []

        # Add new entry
        history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "overall_score": report.overall_score,
                "status": report.status.value,
                "total_issues": report.total_issues,
                "results": {r.category.value: r.score for r in report.results},
            },
        )

        filepath.write_text(json.dumps(history, indent=2))

    def get_trends(self, days: int = 30) -> dict[str, Any]:
        """Analyze health trends over time."""
        trends: dict[str, Any] = {
            "period_days": days,
            "data_points": [],
            "average_score": 0,
            "trend_direction": "stable",
            "score_change": 0,
        }

        scores = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            filepath = self.history_dir / f"{date}.json"

            if filepath.exists():
                try:
                    data = json.loads(filepath.read_text())
                    if data:
                        # Get last entry of the day
                        entry = data[-1]
                        scores.append(entry.get("overall_score", 0))
                        trends["data_points"].append(
                            {
                                "date": date,
                                "score": entry.get("overall_score", 0),
                            },
                        )
                except json.JSONDecodeError:
                    pass

        if scores:
            trends["average_score"] = int(sum(scores) / len(scores))

            if len(scores) >= 2:
                recent = scores[:7] if len(scores) >= 7 else scores[: len(scores) // 2]
                older = scores[7:] if len(scores) >= 7 else scores[len(scores) // 2 :]

                recent_avg = sum(recent) / len(recent) if recent else 0
                older_avg = sum(older) / len(older) if older else 0

                trends["score_change"] = int(recent_avg - older_avg)

                if trends["score_change"] > 5:
                    trends["trend_direction"] = "improving"
                elif trends["score_change"] < -5:
                    trends["trend_direction"] = "declining"
                else:
                    trends["trend_direction"] = "stable"

        return trends

    def identify_hotspots(self) -> list[dict]:
        """Find files that consistently have issues."""
        file_issues: dict[str, int] = {}

        for filepath in self.history_dir.glob("*.json"):
            try:
                data = json.loads(filepath.read_text())
                for entry in data:
                    for result in entry.get("results", {}).values():
                        if isinstance(result, dict):
                            for issue in result.get("issues", []):
                                file_path = issue.get("file_path", "")
                                if file_path:
                                    file_issues[file_path] = file_issues.get(file_path, 0) + 1
            except (json.JSONDecodeError, KeyError):
                pass

        # Sort by issue count
        sorted_files = sorted(file_issues.items(), key=lambda x: x[1], reverse=True)

        return [{"file": f, "issue_count": c} for f, c in sorted_files[:10]]


def format_health_output(
    report: HealthReport,
    level: int = 1,
    thresholds: dict | None = None,
) -> str:
    """Format health report for display.

    Args:
        report: The health report to format
        level: Detail level (1=summary, 2=details, 3=full)
        thresholds: Score thresholds for status icons

    """
    thresholds = thresholds or DEFAULT_THRESHOLDS
    lines = []

    # Overall score
    score = report.overall_score
    if score >= thresholds["good"]:
        status_word = "Good"
        status_icon = "🟢"
    elif score >= thresholds["warning"]:
        status_word = "Warning"
        status_icon = "🟡"
    else:
        status_word = "Critical"
        status_icon = "🔴"

    lines.append(f"{status_icon} Code Health: {status_word} ({score}/100)")
    lines.append("")

    # Level 1: Summary
    for result in report.results:
        if result.status == HealthStatus.SKIP:
            continue

        if result.score >= thresholds["good"]:
            icon = "🟢"
        elif result.score >= thresholds["warning"]:
            icon = "🟡"
        else:
            icon = "🔴"

        category_name = result.category.value.capitalize()

        if result.category == CheckCategory.TESTS:
            details = result.details
            lines.append(
                f"{icon} {category_name}: {details.get('passed', 0)}P/{details.get('failed', 0)}F",
            )
        elif result.category == CheckCategory.LINT:
            lines.append(f"{icon} {category_name}: {result.issue_count} warnings")
        elif result.category == CheckCategory.TYPES:
            lines.append(f"{icon} {category_name}: {result.issue_count} errors")
        elif result.category == CheckCategory.SECURITY:
            details = result.details
            high = details.get("high_severity", 0)
            low = details.get("low_severity", 0)
            if high or low:
                lines.append(f"{icon} {category_name}: {high} high, {low} low severity")
            else:
                lines.append(f"{icon} {category_name}: No vulnerabilities")
        elif result.category == CheckCategory.FORMAT:
            if result.issue_count:
                lines.append(f"{icon} {category_name}: {result.issue_count} files need formatting")
            else:
                lines.append(f"{icon} {category_name}: All files formatted")
        elif result.category == CheckCategory.DEPS:
            if result.issue_count:
                lines.append(f"{icon} {category_name}: {result.issue_count} vulnerable packages")
            else:
                lines.append(f"{icon} {category_name}: All dependencies secure")

    # Level 2: Details
    if level >= 2:
        lines.append("")
        lines.append("━" * 40)
        lines.append("Details:")
        lines.append("")

        for result in report.results:
            if result.issues:
                lines.append(f"  {result.category.value.upper()} ({len(result.issues)} issues)")
                for issue in result.issues[:5]:  # Show first 5
                    loc = f":{issue.line}" if issue.line else ""
                    lines.append(f"    {issue.file_path}{loc}")
                    lines.append(f"      {issue.code}: {issue.message}")
                if len(result.issues) > 5:
                    lines.append(f"    ... and {len(result.issues) - 5} more")
                lines.append("")

    # Level 3: Full report
    if level >= 3:
        lines.append("")
        lines.append("━" * 40)
        lines.append("Full Report")
        lines.append(f"Generated: {report.generated_at}")
        lines.append(f"Project: {report.project_root}")
        lines.append("")

        for result in report.results:
            lines.append(f"## {result.category.value.capitalize()} (Score: {result.score}/100)")
            lines.append(f"   Tool: {result.tool_used}")
            lines.append(f"   Duration: {result.duration_ms}ms")
            if result.details:
                for key, value in result.details.items():
                    lines.append(f"   {key}: {value}")
            lines.append("")

    # Action prompt
    if report.total_fixable > 0:
        lines.append("")
        lines.append("━" * 40)
        lines.append(
            f"[1] Fix {report.total_fixable} auto-fixable issues  [2] See details  [3] Full report",
        )

    return "\n".join(lines)
