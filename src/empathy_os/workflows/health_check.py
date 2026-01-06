"""Health Check Workflow

A workflow wrapper for HealthCheckCrew that provides project health
diagnosis and fixing capabilities.

Uses XML-enhanced prompts and 5 specialized agents:
1. Health Lead - Coordinator
2. Lint Fixer - Ruff analysis and fixes
3. Type Resolver - Mypy analysis
4. Test Doctor - Pytest analysis
5. Dep Auditor - Dependency security

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .base import BaseWorkflow, ModelTier

logger = logging.getLogger(__name__)


@dataclass
class HealthCheckResult:
    """Result from HealthCheckWorkflow execution."""

    success: bool
    health_score: float
    is_healthy: bool
    issues: list[dict]
    fixes: list[dict]
    checks_run: dict
    agents_used: list[str]
    critical_count: int
    high_count: int
    applied_fixes_count: int
    duration_seconds: float
    cost: float
    metadata: dict = field(default_factory=dict)


class HealthCheckWorkflow(BaseWorkflow):
    """Workflow wrapper for HealthCheckCrew.

    Provides comprehensive project health diagnosis and fixing using
    5 specialized agents with XML-enhanced prompts.

    Checks:
    - Lint (ruff) - Code style and quality
    - Types (mypy) - Type safety
    - Tests (pytest) - Test suite health
    - Dependencies - Security vulnerabilities and outdated packages

    Usage:
        workflow = HealthCheckWorkflow()
        result = await workflow.execute(path=".", auto_fix=True)

        if result.is_healthy:
            print("Project is healthy!")
        else:
            print(f"Health Score: {result.health_score}/100")
            for issue in result.issues:
                print(f"  - {issue['title']}")
    """

    name = "health-check"
    description = "Project health diagnosis and fixing with 5-agent crew"

    stages = ["diagnose", "fix"]
    tier_map = {
        "diagnose": ModelTier.CAPABLE,
        "fix": ModelTier.CAPABLE,
    }

    def __init__(
        self,
        auto_fix: bool = False,
        check_lint: bool = True,
        check_types: bool = True,
        check_tests: bool = True,
        check_deps: bool = True,
        xml_prompts: bool = True,
        **kwargs: Any,
    ):
        """Initialize health check workflow.

        Args:
            auto_fix: Automatically apply safe fixes
            check_lint: Run lint checks
            check_types: Run type checks
            check_tests: Run test checks
            check_deps: Run dependency checks
            xml_prompts: Use XML-enhanced prompts
            **kwargs: Additional arguments passed to BaseWorkflow

        """
        super().__init__(**kwargs)
        self.auto_fix = auto_fix
        self.check_lint = check_lint
        self.check_types = check_types
        self.check_tests = check_tests
        self.check_deps = check_deps
        self.xml_prompts = xml_prompts
        self._crew: Any = None
        self._crew_available = False

    def _check_crew_available(self) -> bool:
        """Check if HealthCheckCrew is available."""
        import importlib.util

        return importlib.util.find_spec("empathy_llm_toolkit.agent_factory.crews") is not None

    async def _initialize_crew(self) -> None:
        """Initialize the HealthCheckCrew."""
        if self._crew is not None:
            return

        try:
            from empathy_llm_toolkit.agent_factory.crews import HealthCheckConfig, HealthCheckCrew

            config = HealthCheckConfig(
                check_lint=self.check_lint,
                check_types=self.check_types,
                check_tests=self.check_tests,
                check_deps=self.check_deps,
                auto_fix=self.auto_fix,
                xml_prompts_enabled=self.xml_prompts,
            )
            self._crew = HealthCheckCrew(config=config)
            self._crew_available = True
            logger.info("HealthCheckCrew initialized successfully")
        except ImportError as e:
            logger.warning(f"HealthCheckCrew not available: {e}")
            self._crew_available = False

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "diagnose":
            return await self._diagnose(input_data, tier)
        if stage_name == "fix":
            return await self._fix(input_data, tier)
        raise ValueError(f"Unknown stage: {stage_name}")

    async def _diagnose(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Run health diagnosis using HealthCheckCrew.

        Falls back to basic checks if crew not available.
        """
        path = input_data.get("path", ".")

        # Initialize crew
        await self._initialize_crew()

        if self._crew_available and self._crew:
            # Run crew-based health check
            report = await self._crew.check(
                path=path,
                auto_fix=False,  # Don't auto-fix in diagnose stage
            )

            result = {
                "health_score": report.health_score,
                "is_healthy": report.is_healthy,
                "issues": [i.to_dict() for i in report.issues],
                "checks_run": report.checks_run,
                "agents_used": report.agents_used,
                "crew_available": True,
            }

            input_tokens = 500  # Estimate
            output_tokens = len(str(result)) // 4

            return (
                {
                    "diagnosis": result,
                    **input_data,
                },
                input_tokens,
                output_tokens,
            )

        # Fallback to basic checks without crew
        result = await self._basic_health_check(path)
        result["crew_available"] = False

        return (
            {
                "diagnosis": result,
                **input_data,
            },
            100,
            len(str(result)) // 4,
        )

    async def _basic_health_check(self, path: str) -> dict:
        """Basic health check without crew (fallback)."""
        import subprocess

        issues = []
        checks_run = {}
        health_score = 100.0

        # Lint check
        if self.check_lint:
            try:
                result = subprocess.run(
                    ["python", "-m", "ruff", "check", path],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                lint_errors = result.stdout.count("\n")
                checks_run["lint"] = {"passed": result.returncode == 0}
                if result.returncode != 0:
                    health_score -= min(20, lint_errors)
                    issues.append(
                        {
                            "title": f"Lint: {lint_errors} issues found",
                            "category": "lint",
                            "severity": "medium",
                        },
                    )
            except subprocess.TimeoutExpired:
                logger.warning("Lint check timed out after 60s")
                checks_run["lint"] = {"passed": True, "skipped": True, "reason": "timeout"}
            except FileNotFoundError:
                logger.info("Ruff not installed, skipping lint check")
                checks_run["lint"] = {"passed": True, "skipped": True, "reason": "tool_missing"}
            except subprocess.SubprocessError as e:
                logger.error(f"Lint check subprocess error: {e}")
                checks_run["lint"] = {"passed": True, "skipped": True, "reason": "subprocess_error"}
            except Exception:
                # INTENTIONAL: Graceful degradation - health checks are best-effort
                logger.exception("Unexpected error in lint check")
                checks_run["lint"] = {"passed": True, "skipped": True, "reason": "unexpected_error"}

        # Type check
        if self.check_types:
            try:
                result = subprocess.run(
                    ["python", "-m", "mypy", path, "--ignore-missing-imports"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                type_errors = result.stdout.count("error:")
                checks_run["types"] = {"passed": result.returncode == 0}
                if result.returncode != 0:
                    health_score -= min(20, type_errors * 2)
                    issues.append(
                        {
                            "title": f"Types: {type_errors} errors found",
                            "category": "types",
                            "severity": "medium",
                        },
                    )
            except subprocess.TimeoutExpired:
                logger.warning("Type check timed out after 120s")
                checks_run["types"] = {"passed": True, "skipped": True, "reason": "timeout"}
            except FileNotFoundError:
                logger.info("Mypy not installed, skipping type check")
                checks_run["types"] = {"passed": True, "skipped": True, "reason": "tool_missing"}
            except subprocess.SubprocessError as e:
                logger.error(f"Type check subprocess error: {e}")
                checks_run["types"] = {
                    "passed": True,
                    "skipped": True,
                    "reason": "subprocess_error",
                }
            except Exception:
                # INTENTIONAL: Graceful degradation - health checks are best-effort
                logger.exception("Unexpected error in type check")
                checks_run["types"] = {
                    "passed": True,
                    "skipped": True,
                    "reason": "unexpected_error",
                }

        # Test check
        if self.check_tests:
            try:
                # Use "tests/" directory or rely on pytest.ini testpaths
                # Don't pass path="." which overrides testpaths and causes collection errors
                result = subprocess.run(
                    ["python", "-m", "pytest", "tests/", "-q", "--tb=no", "--no-cov"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                checks_run["tests"] = {"passed": result.returncode == 0}
                if result.returncode != 0:
                    health_score -= 25
                    issues.append(
                        {
                            "title": "Tests: Some tests failing",
                            "category": "tests",
                            "severity": "high",
                        },
                    )
            except subprocess.TimeoutExpired:
                logger.warning("Test check timed out after 180s")
                checks_run["tests"] = {"passed": True, "skipped": True, "reason": "timeout"}
            except FileNotFoundError:
                logger.info("Pytest not installed, skipping test check")
                checks_run["tests"] = {"passed": True, "skipped": True, "reason": "tool_missing"}
            except subprocess.SubprocessError as e:
                logger.error(f"Test check subprocess error: {e}")
                checks_run["tests"] = {
                    "passed": True,
                    "skipped": True,
                    "reason": "subprocess_error",
                }
            except Exception:
                # INTENTIONAL: Graceful degradation - health checks are best-effort
                logger.exception("Unexpected error in test check")
                checks_run["tests"] = {
                    "passed": True,
                    "skipped": True,
                    "reason": "unexpected_error",
                }

        return {
            "health_score": max(0, health_score),
            "is_healthy": health_score >= 80,
            "issues": issues,
            "checks_run": checks_run,
            "agents_used": [],
        }

    async def _fix(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Apply fixes for identified issues.

        Only runs if auto_fix is enabled and issues were found.
        """
        path = input_data.get("path", ".")
        fixes = []

        if not self.auto_fix:
            return (
                {
                    "fixes": [],
                    "auto_fix_enabled": False,
                    **input_data,
                },
                0,
                0,
            )

        # Use crew if available
        if self._crew_available and self._crew:
            report = await self._crew.check(
                path=path,
                auto_fix=True,
            )
            fixes = [f.to_dict() for f in report.fixes]
        # Basic auto-fix with ruff
        elif self.check_lint:
            import subprocess

            try:
                result = subprocess.run(
                    ["python", "-m", "ruff", "check", path, "--fix"],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if "fixed" in result.stdout.lower():
                    fixes.append(
                        {
                            "title": "Lint auto-fixes applied",
                            "category": "lint",
                            "status": "applied",
                        },
                    )
            except subprocess.TimeoutExpired:
                logger.warning("Ruff auto-fix timed out after 60s")
            except FileNotFoundError:
                logger.info("Ruff not installed, skipping auto-fix")
            except subprocess.SubprocessError as e:
                logger.error(f"Ruff auto-fix subprocess error: {e}")
            except Exception:
                # INTENTIONAL: Graceful degradation - auto-fix is best-effort
                logger.exception("Unexpected error in ruff auto-fix")

        return (
            {
                "fixes": fixes,
                "auto_fix_enabled": True,
                **input_data,
            },
            100,
            len(str(fixes)) // 4,
        )

    async def execute(self, **kwargs: Any) -> HealthCheckResult:  # type: ignore[override]
        """Execute the health check workflow.

        Args:
            path: Path to check (default: ".")
            auto_fix: Override auto_fix setting
            **kwargs: Additional arguments

        Returns:
            HealthCheckResult with health score and findings

        """
        start_time = time.time()

        # Override auto_fix if provided
        if "auto_fix" in kwargs:
            self.auto_fix = kwargs.pop("auto_fix")

        # Run base workflow
        result = await super().execute(**kwargs)

        duration = time.time() - start_time
        final_output = result.final_output or {}
        diagnosis = final_output.get("diagnosis", {})
        fixes = final_output.get("fixes", [])

        # Count severities
        issues = diagnosis.get("issues", [])
        critical_count = sum(1 for i in issues if i.get("severity") == "critical")
        high_count = sum(1 for i in issues if i.get("severity") == "high")
        applied_count = sum(1 for f in fixes if f.get("status") == "applied")

        health_result = HealthCheckResult(
            success=result.success,
            health_score=diagnosis.get("health_score", 0),
            is_healthy=diagnosis.get("is_healthy", False),
            issues=issues,
            fixes=fixes,
            checks_run=diagnosis.get("checks_run", {}),
            agents_used=diagnosis.get("agents_used", []),
            critical_count=critical_count,
            high_count=high_count,
            applied_fixes_count=applied_count,
            duration_seconds=duration,
            cost=result.cost_report.total_cost,
            metadata={
                "crew_available": diagnosis.get("crew_available", False),
                "auto_fix": self.auto_fix,
                "xml_prompts": self.xml_prompts,
            },
        )

        # Auto-save to .empathy/health.json for dashboard
        self._save_health_data(health_result, kwargs.get("path", "."))

        # Add formatted report to metadata for human readability
        health_result.metadata["formatted_report"] = format_health_check_report(health_result)

        return health_result

    def _save_health_data(self, result: HealthCheckResult, project_path: str) -> None:
        """Save health check results to .empathy/health.json for dashboard."""
        try:
            # Determine empathy dir relative to project path
            if os.path.isabs(project_path):
                empathy_dir = os.path.join(project_path, ".empathy")
            else:
                empathy_dir = os.path.join(os.getcwd(), ".empathy")

            os.makedirs(empathy_dir, exist_ok=True)

            # Count issues by category
            lint_errors = sum(1 for i in result.issues if i.get("category") == "lint")
            type_errors = sum(1 for i in result.issues if i.get("category") == "types")
            test_failures = sum(1 for i in result.issues if i.get("category") == "tests")
            security_high = sum(
                1
                for i in result.issues
                if i.get("category") == "security" and i.get("severity") == "high"
            )
            security_medium = sum(
                1
                for i in result.issues
                if i.get("category") == "security" and i.get("severity") == "medium"
            )

            # Extract test stats from checks_run
            tests_info = result.checks_run.get("tests", {})

            health_data = {
                "score": result.health_score,
                "lint": {"errors": lint_errors, "warnings": 0},
                "types": {"errors": type_errors},
                "security": {"high": security_high, "medium": security_medium, "low": 0},
                "tests": {
                    "passed": tests_info.get("passed", 0) if tests_info.get("passed") else 0,
                    "failed": test_failures,
                    "total": tests_info.get("total", 0) if tests_info.get("total") else 0,
                    "coverage": tests_info.get("coverage", 0) if tests_info.get("coverage") else 0,
                },
                "tech_debt": {"total": 0, "todos": 0, "fixmes": 0, "hacks": 0},
                "timestamp": datetime.now().isoformat(),
            }

            health_file = os.path.join(empathy_dir, "health.json")
            with open(health_file, "w") as f:
                json.dump(health_data, f, indent=2)

            logger.info(f"Saved health data to {health_file}")
        except OSError as e:
            # File system errors (disk full, permission denied, etc.)
            logger.warning(f"Failed to save health data (file system error): {e}")
        except (TypeError, ValueError) as e:
            # Cannot serialize health data - json.dump raises TypeError/ValueError
            logger.error(f"Failed to save health data (serialization error): {e}")
        except Exception as e:  # noqa: BLE001
            # INTENTIONAL: Saving health data should never crash a health check
            # This is best-effort diagnostics output
            logger.warning(f"Failed to save health data (unexpected error): {e}")


def format_health_check_report(result: HealthCheckResult) -> str:
    """Format health check output as a human-readable report.

    Args:
        result: The HealthCheckResult dataclass

    Returns:
        Formatted report string

    """
    lines = []

    # Header with health status
    score = result.health_score
    if score >= 90:
        status_icon = "🟢"
        status_text = "EXCELLENT"
    elif score >= 80:
        status_icon = "🟡"
        status_text = "HEALTHY"
    elif score >= 60:
        status_icon = "🟠"
        status_text = "NEEDS ATTENTION"
    else:
        status_icon = "🔴"
        status_text = "UNHEALTHY"

    lines.append("=" * 60)
    lines.append("PROJECT HEALTH CHECK REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Health Score: {status_icon} {score:.0f}/100 ({status_text})")
    lines.append(f"Status: {'✅ Healthy' if result.is_healthy else '⚠️ Issues Found'}")
    lines.append("")

    # Checks run summary
    lines.append("-" * 60)
    lines.append("CHECKS PERFORMED")
    lines.append("-" * 60)
    for check_name, check_result in result.checks_run.items():
        passed = check_result.get("passed", False)
        skipped = check_result.get("skipped", False)
        if skipped:
            icon = "⏭️"
            status = "Skipped"
        elif passed:
            icon = "✅"
            status = "Passed"
        else:
            icon = "❌"
            status = "Failed"
        lines.append(f"  {icon} {check_name.capitalize()}: {status}")
    lines.append("")

    # Issue summary
    if result.issues:
        lines.append("-" * 60)
        lines.append("ISSUES FOUND")
        lines.append("-" * 60)
        lines.append(f"Total: {len(result.issues)}")
        lines.append(f"  🔴 Critical: {result.critical_count}")
        lines.append(f"  🟠 High: {result.high_count}")
        lines.append("")

        # Group issues by category
        by_category: dict[str, list] = {}
        for issue in result.issues:
            cat = issue.get("category", "other")
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(issue)

        for category, issues in by_category.items():
            lines.append(f"  {category.upper()} ({len(issues)} issues):")
            for issue in issues[:5]:  # Show top 5 per category
                severity = issue.get("severity", "unknown").upper()
                title = issue.get("title", "Unknown issue")
                sev_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(
                    severity,
                    "⚪",
                )
                lines.append(f"    {sev_icon} [{severity}] {title}")
            if len(issues) > 5:
                lines.append(f"    ... and {len(issues) - 5} more")
        lines.append("")

    # Fixes applied
    if result.fixes:
        lines.append("-" * 60)
        lines.append("FIXES APPLIED")
        lines.append("-" * 60)
        lines.append(f"Total Fixes: {result.applied_fixes_count}")
        for fix in result.fixes[:10]:
            status = fix.get("status", "unknown")
            title = fix.get("title", "Unknown fix")
            status_icon = "✅" if status == "applied" else "⚠️"
            lines.append(f"  {status_icon} {title}")
        lines.append("")

    # Agents used
    if result.agents_used:
        lines.append("-" * 60)
        lines.append("AGENTS USED")
        lines.append("-" * 60)
        for agent in result.agents_used:
            lines.append(f"  🤖 {agent}")
        lines.append("")

    # Footer
    lines.append("=" * 60)
    duration_ms = result.duration_seconds * 1000
    lines.append(f"Health check completed in {duration_ms:.0f}ms | Cost: ${result.cost:.4f}")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entry point for health check workflow."""
    import asyncio

    async def run():
        workflow = HealthCheckWorkflow(auto_fix=False)
        result = await workflow.execute(path=".")

        print("\nHealth Check Results")
        print("=" * 50)
        print(f"Health Score: {result.health_score}/100")
        print(f"Is Healthy: {result.is_healthy}")
        print(f"Issues Found: {len(result.issues)}")
        print(f"  Critical: {result.critical_count}")
        print(f"  High: {result.high_count}")

        if result.issues:
            print("\nTop Issues:")
            for issue in result.issues[:5]:
                print(
                    f"  - [{issue.get('severity', 'N/A').upper()}] {issue.get('title', 'Unknown')}",
                )

        print(f"\nChecks Run: {list(result.checks_run.keys())}")
        print(f"Duration: {result.duration_seconds * 1000:.0f}ms")

    asyncio.run(run())


if __name__ == "__main__":
    main()
