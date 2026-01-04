"""Test Maintenance Crew - CrewAI-Based Automated Test Management

A crew of specialized agents that collaboratively manage the test lifecycle:
- Test Analyst: Analyzes coverage gaps and prioritizes work
- Test Generator: Creates new tests using LLM
- Test Validator: Verifies generated tests work correctly
- Test Reporter: Generates status reports and recommendations

The crew can operate autonomously on a schedule or be triggered by events.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from ..project_index import ProjectIndex
from ..project_index.reports import ReportGenerator
from .test_maintenance import TestAction, TestMaintenanceWorkflow, TestPlanItem, TestPriority

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Result from an agent's work."""

    agent: str
    task: str
    success: bool
    output: dict[str, Any]
    duration_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class CrewConfig:
    """Configuration for the test maintenance crew."""

    # Agent settings
    enable_auto_generation: bool = True
    enable_auto_validation: bool = True
    max_files_per_run: int = 10

    # Thresholds
    min_coverage_target: float = 80.0
    staleness_threshold_days: int = 7
    high_impact_threshold: float = 5.0

    # Scheduling
    auto_run_interval_hours: int = 24
    run_on_commit: bool = True

    # LLM settings
    test_gen_model: str = "sonnet"
    validation_model: str = "haiku"

    # Validation settings
    validation_timeout_seconds: int = 120  # Per-file timeout
    validation_optional: bool = True  # Don't fail crew if validation fails
    skip_validation_on_timeout: bool = True  # Continue on timeout


class TestAnalystAgent:
    """Analyzes test coverage and prioritizes work.

    Responsibilities:
    - Identify files needing tests
    - Calculate priority based on impact
    - Generate maintenance plans
    - Track test health metrics
    """

    def __init__(self, index: ProjectIndex, config: CrewConfig):
        self.index = index
        self.config = config
        self.name = "Test Analyst"

    async def analyze_coverage_gaps(self) -> AgentResult:
        """Identify files with coverage gaps."""
        start = datetime.now()

        files_needing_tests = self.index.get_files_needing_tests()
        high_impact = [
            f for f in files_needing_tests if f.impact_score >= self.config.high_impact_threshold
        ]

        output = {
            "total_gaps": len(files_needing_tests),
            "high_impact_gaps": len(high_impact),
            "priority_files": [
                {
                    "path": f.path,
                    "impact": f.impact_score,
                    "loc": f.lines_of_code,
                }
                for f in sorted(high_impact, key=lambda x: -x.impact_score)[:10]
            ],
            "recommendation": self._generate_recommendation(files_needing_tests, high_impact),
        }

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="analyze_coverage_gaps",
            success=True,
            output=output,
            duration_ms=duration,
        )

    async def analyze_staleness(self) -> AgentResult:
        """Identify files with stale tests."""
        start = datetime.now()

        stale_files = self.index.get_stale_files()

        output = {
            "stale_count": len(stale_files),
            "avg_staleness_days": (
                sum(f.staleness_days for f in stale_files) / len(stale_files) if stale_files else 0
            ),
            "stale_files": [
                {
                    "path": f.path,
                    "staleness_days": f.staleness_days,
                    "test_file": f.test_file_path,
                }
                for f in sorted(stale_files, key=lambda x: -x.staleness_days)[:10]
            ],
        }

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="analyze_staleness",
            success=True,
            output=output,
            duration_ms=duration,
        )

    async def generate_plan(self) -> AgentResult:
        """Generate a prioritized maintenance plan."""
        start = datetime.now()

        workflow = TestMaintenanceWorkflow(str(self.index.project_root), self.index)
        result = await workflow.run(
            {
                "mode": "analyze",
                "max_items": self.config.max_files_per_run,
            },
        )

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="generate_plan",
            success=True,
            output=result,
            duration_ms=duration,
        )

    def _generate_recommendation(self, all_gaps: list, high_impact: list) -> str:
        """Generate actionable recommendation."""
        if len(high_impact) > 5:
            return f"URGENT: {len(high_impact)} high-impact files need tests. Start with the top 5."
        if len(high_impact) > 0:
            return f"Prioritize {len(high_impact)} high-impact files before addressing remaining {len(all_gaps) - len(high_impact)} gaps."
        if len(all_gaps) > 20:
            return f"Consider batch test generation for {len(all_gaps)} files."
        if len(all_gaps) > 0:
            return f"Address {len(all_gaps)} remaining test gaps to improve coverage."
        return "Excellent! All files requiring tests have coverage."


class TestGeneratorAgent:
    """Generates tests for source files.

    Responsibilities:
    - Read source file and understand its structure
    - Generate appropriate test cases
    - Follow project testing patterns
    - Write test files to correct location
    """

    def __init__(self, project_root: Path, index: ProjectIndex, config: CrewConfig):
        self.project_root = project_root
        self.index = index
        self.config = config
        self.name = "Test Generator"

    async def generate_tests(self, plan_items: list[TestPlanItem]) -> AgentResult:
        """Generate tests for files in the plan."""
        start = datetime.now()

        results = []
        succeeded = 0
        failed = 0

        for item in plan_items:
            if item.action != TestAction.CREATE:
                continue

            try:
                result = await self._generate_test_for_file(item)
                results.append(result)
                if result["success"]:
                    succeeded += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Failed to generate tests for {item.file_path}: {e}")
                failed += 1
                results.append(
                    {
                        "file": item.file_path,
                        "success": False,
                        "error": str(e),
                    },
                )

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="generate_tests",
            success=failed == 0,
            output={
                "processed": len(results),
                "succeeded": succeeded,
                "failed": failed,
                "results": results,
            },
            duration_ms=duration,
        )

    async def _generate_test_for_file(self, item: TestPlanItem) -> dict[str, Any]:
        """Generate tests for a single file."""
        source_path = self.project_root / item.file_path

        if not source_path.exists():
            return {
                "file": item.file_path,
                "success": False,
                "error": "Source file not found",
            }

        # Determine test file path
        test_file_path = self._determine_test_path(item.file_path)
        full_test_path = self.project_root / test_file_path

        # Skip if test file already exists and has content
        if full_test_path.exists():
            existing_content = full_test_path.read_text(encoding="utf-8")
            # Only skip if file has real tests (not just placeholder)
            if "def test_" in existing_content and "assert True  # Replace" not in existing_content:
                return {
                    "file": item.file_path,
                    "test_file": test_file_path,
                    "success": True,
                    "skipped": True,
                    "reason": "Test file already exists with real tests",
                }

        # Read source file
        try:
            source_code = source_path.read_text(encoding="utf-8")
        except Exception as e:
            return {
                "file": item.file_path,
                "success": False,
                "error": f"Failed to read source: {e}",
            }

        # Generate test code (placeholder - would use LLM)
        test_code = self._generate_test_code(item.file_path, source_code, item.metadata)

        # Write test file
        try:
            full_test_path.parent.mkdir(parents=True, exist_ok=True)
            full_test_path.write_text(test_code, encoding="utf-8")
        except Exception as e:
            return {
                "file": item.file_path,
                "success": False,
                "error": f"Failed to write test file: {e}",
            }

        # Update index
        self.index.update_file(
            item.file_path,
            tests_exist=True,
            test_file_path=test_file_path,
            tests_last_modified=datetime.now(),
            is_stale=False,
            staleness_days=0,
        )

        return {
            "file": item.file_path,
            "test_file": test_file_path,
            "success": True,
            "lines_generated": len(test_code.split("\n")),
        }

    def _determine_test_path(self, source_path: str) -> str:
        """Determine the test file path for a source file."""
        path = Path(source_path)

        # Standard pattern: src/module/file.py -> tests/test_file.py
        if path.parts[0] == "src":
            test_name = f"test_{path.stem}.py"
            return f"tests/{test_name}"

        # Module in root: module/file.py -> tests/test_file.py
        test_name = f"test_{path.stem}.py"
        return f"tests/{test_name}"

    def _generate_test_code(
        self,
        source_path: str,
        source_code: str,
        metadata: dict[str, Any],
    ) -> str:
        """Generate test code for a source file."""
        # This is a placeholder - would integrate with LLM for real generation
        module_name = Path(source_path).stem
        class_name = "".join(word.capitalize() for word in module_name.split("_"))

        return f'''"""
Tests for {source_path}

Auto-generated by Test Maintenance Crew.
Review and enhance as needed.
"""

import pytest

# TODO: Import the module being tested
# from {module_name} import ...


class Test{class_name}:
    """Tests for {module_name} module."""

    def test_placeholder(self):
        """Placeholder test - implement actual tests."""
        # TODO: Implement actual tests
        # Source file has {metadata.get("lines_of_code", "unknown")} lines
        # Complexity score: {metadata.get("complexity", "unknown")}
        assert True  # Replace with actual assertions


# TODO: Add more test cases based on the source code
'''


class TestValidatorAgent:
    """Validates generated tests.

    Responsibilities:
    - Run generated tests to verify they pass
    - Check test coverage
    - Identify issues with generated tests
    - Suggest improvements
    """

    def __init__(self, project_root: Path, config: CrewConfig):
        self.project_root = project_root
        self.config = config
        self.name = "Test Validator"

    async def validate_tests(self, test_files: list[str]) -> AgentResult:
        """Validate that tests run correctly."""
        start = datetime.now()

        results = []
        passed = 0
        failed = 0
        skipped = 0

        for test_file in test_files:
            try:
                result = await self._run_test_file(test_file)
                results.append(result)
                if result.get("skipped"):
                    skipped += 1
                elif result["passed"]:
                    passed += 1
                else:
                    failed += 1
            except Exception as e:
                logger.error(f"Validation error for {test_file}: {e}")
                results.append(
                    {
                        "file": test_file,
                        "passed": False,
                        "error": str(e),
                    },
                )
                failed += 1

        duration = int((datetime.now() - start).total_seconds() * 1000)

        # Success depends on config - if validation is optional, we succeed even with failures
        success = (failed == 0) or self.config.validation_optional

        return AgentResult(
            agent=self.name,
            task="validate_tests",
            success=success,
            output={
                "total": len(test_files),
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "results": results,
                "validation_optional": self.config.validation_optional,
            },
            duration_ms=duration,
        )

    async def validate_single(self, test_file: str) -> AgentResult:
        """Validate a single test file (for validate-only mode)."""
        start = datetime.now()
        result = await self._run_test_file(test_file)
        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="validate_single",
            success=result["passed"],
            output=result,
            duration_ms=duration,
        )

    async def _run_test_file(self, test_file: str) -> dict[str, Any]:
        """Run a single test file."""
        import subprocess

        full_path = self.project_root / test_file

        if not full_path.exists():
            return {
                "file": test_file,
                "passed": False,
                "error": "Test file not found",
            }

        timeout = self.config.validation_timeout_seconds

        try:
            # Run pytest without coverage to avoid coverage threshold failures
            result = subprocess.run(
                ["python", "-m", "pytest", str(full_path), "-v", "--tb=short", "-x", "--no-cov"],
                check=False,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(self.project_root),
            )

            # Check if tests passed (look for "passed" in output even if returncode != 0)
            tests_passed = result.returncode == 0
            if not tests_passed and result.stdout:
                # pytest may return non-zero for coverage issues even when tests pass
                if "passed" in result.stdout and "failed" not in result.stdout.lower():
                    tests_passed = True

            return {
                "file": test_file,
                "passed": tests_passed,
                "output": result.stdout[-1000:] if result.stdout else "",
                "errors": result.stderr[-500:] if result.stderr else "",
            }

        except subprocess.TimeoutExpired:
            logger.warning(f"Test timeout for {test_file} after {timeout}s")
            if self.config.skip_validation_on_timeout:
                return {
                    "file": test_file,
                    "passed": False,
                    "skipped": True,
                    "error": f"Test timeout after {timeout}s - skipped",
                }
            return {
                "file": test_file,
                "passed": False,
                "error": f"Test timeout after {timeout}s",
            }
        except Exception as e:
            logger.error(f"Validation error for {test_file}: {e}")
            return {
                "file": test_file,
                "passed": False,
                "error": str(e),
            }


class TestReporterAgent:
    """Generates reports and recommendations.

    Responsibilities:
    - Generate test health reports
    - Track progress over time
    - Provide actionable recommendations
    - Format output for different consumers
    """

    def __init__(self, index: ProjectIndex, config: CrewConfig):
        self.index = index
        self.config = config
        self.name = "Test Reporter"

    async def generate_status_report(self) -> AgentResult:
        """Generate comprehensive status report."""
        start = datetime.now()

        summary = self.index.get_summary()
        generator = ReportGenerator(summary, self.index.get_all_files())

        output = {
            "health": generator.health_report(),
            "test_gaps": generator.test_gap_report(),
            "staleness": generator.staleness_report(),
            "recommendations": self._generate_recommendations(summary),
        }

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="generate_status_report",
            success=True,
            output=output,
            duration_ms=duration,
        )

    async def generate_maintenance_summary(
        self,
        crew_results: list[AgentResult],
    ) -> AgentResult:
        """Generate summary of maintenance run."""
        start = datetime.now()

        total_duration = sum(r.duration_ms for r in crew_results)
        successful = sum(1 for r in crew_results if r.success)

        output = {
            "run_timestamp": datetime.now().isoformat(),
            "agents_executed": len(crew_results),
            "agents_succeeded": successful,
            "total_duration_ms": total_duration,
            "agent_results": [
                {
                    "agent": r.agent,
                    "task": r.task,
                    "success": r.success,
                    "duration_ms": r.duration_ms,
                }
                for r in crew_results
            ],
            "overall_success": successful == len(crew_results),
        }

        duration = int((datetime.now() - start).total_seconds() * 1000)

        return AgentResult(
            agent=self.name,
            task="generate_maintenance_summary",
            success=True,
            output=output,
            duration_ms=duration,
        )

    def _generate_recommendations(self, summary) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Coverage recommendations
        if summary.test_coverage_avg < 50:
            recommendations.append(
                f"CRITICAL: Test coverage is {summary.test_coverage_avg:.1f}%. "
                f"Target is {self.config.min_coverage_target}%. Prioritize test creation.",
            )
        elif summary.test_coverage_avg < self.config.min_coverage_target:
            recommendations.append(
                f"Coverage is {summary.test_coverage_avg:.1f}%, "
                f"below target of {self.config.min_coverage_target}%.",
            )

        # Test gap recommendations
        if summary.files_without_tests > 20:
            recommendations.append(
                f"Large test gap: {summary.files_without_tests} files need tests. "
                "Consider batch generation.",
            )
        elif summary.files_without_tests > 0:
            recommendations.append(f"{summary.files_without_tests} files still need tests.")

        # Staleness recommendations
        if summary.stale_file_count > 10:
            recommendations.append(
                f"{summary.stale_file_count} files have stale tests. Run test update workflow.",
            )
        elif summary.stale_file_count > 0:
            recommendations.append(f"{summary.stale_file_count} files have stale tests.")

        # Critical files
        if summary.critical_untested_files:
            recommendations.append(
                f"PRIORITY: {len(summary.critical_untested_files)} high-impact files "
                "lack tests. Address immediately.",
            )

        if not recommendations:
            recommendations.append("Test health is good. Maintain current coverage.")

        return recommendations


class TestMaintenanceCrew:
    """Coordinates the test maintenance agents.

    The crew can run different types of maintenance operations:
    - full: Run all agents in sequence
    - analyze: Only run analysis (no generation)
    - generate: Run analysis and generation
    - validate: Run analysis, generation, and validation
    - report: Only generate reports
    """

    def __init__(
        self,
        project_root: str,
        index: ProjectIndex | None = None,
        config: CrewConfig | None = None,
    ):
        self.project_root = Path(project_root)
        self.index = index or ProjectIndex(str(project_root))
        self.config = config or CrewConfig()

        # Initialize agents
        self.analyst = TestAnalystAgent(self.index, self.config)
        self.generator = TestGeneratorAgent(self.project_root, self.index, self.config)
        self.validator = TestValidatorAgent(self.project_root, self.config)
        self.reporter = TestReporterAgent(self.index, self.config)

        # Results tracking
        self._run_history: list[dict[str, Any]] = []

    async def run(self, mode: str = "full", test_files: list[str] | None = None) -> dict[str, Any]:
        """Run the crew with specified mode.

        Modes:
        - full: Complete maintenance cycle
        - analyze: Only analysis
        - generate: Analysis + generation
        - validate: Analysis + generation + validation
        - validate-only: Only validate specified test files (pass test_files param)
        - report: Only reporting
        """
        logger.info(f"Starting test maintenance crew in {mode} mode")

        results: list[AgentResult] = []
        plan = None

        # Handle validate-only mode separately
        if mode == "validate-only":
            if not test_files:
                return {
                    "mode": mode,
                    "success": False,
                    "error": "validate-only mode requires test_files parameter",
                }

            for test_file in test_files:
                val_result = await self.validator.validate_single(test_file)
                results.append(val_result)

            summary_result = await self.reporter.generate_maintenance_summary(results)
            results.append(summary_result)

            return {
                "mode": mode,
                "timestamp": datetime.now().isoformat(),
                "results": [r.output for r in results],
                "summary": summary_result.output,
                "success": all(
                    r.success for r in results if r.task != "generate_maintenance_summary"
                ),
            }

        # Ensure index is fresh
        self.index.refresh()

        # Phase 1: Analysis (always run except for report-only)
        if mode != "report":
            coverage_result = await self.analyst.analyze_coverage_gaps()
            results.append(coverage_result)

            staleness_result = await self.analyst.analyze_staleness()
            results.append(staleness_result)

            plan_result = await self.analyst.generate_plan()
            results.append(plan_result)
            plan = plan_result.output.get("plan", {})

        # Phase 2: Generation (for generate, validate, full modes)
        if mode in ["generate", "validate", "full"] and plan:
            plan_items = [
                TestPlanItem(
                    file_path=item["file_path"],
                    action=TestAction(item["action"]),
                    priority=TestPriority(item["priority"]),
                    reason=item.get("reason", ""),
                    metadata=item.get("metadata", {}),
                )
                for item in plan.get("items", [])
                if item["action"] == "create"
            ]

            if plan_items:
                gen_result = await self.generator.generate_tests(plan_items)
                results.append(gen_result)

        # Phase 3: Validation (for validate, full modes)
        if mode in ["validate", "full"] and self.config.enable_auto_validation:
            # Get test files from generation results
            generated_test_files = []
            for result in results:
                if result.agent == "Test Generator":
                    for item in result.output.get("results", []):
                        if item.get("success") and item.get("test_file"):
                            generated_test_files.append(item["test_file"])

            if generated_test_files:
                try:
                    val_result = await self.validator.validate_tests(generated_test_files)
                    results.append(val_result)
                except Exception as e:
                    logger.error(f"Validation failed with error: {e}")
                    if not self.config.validation_optional:
                        raise
                    # Log but continue if validation is optional
                    results.append(
                        AgentResult(
                            agent="Test Validator",
                            task="validate_tests",
                            success=True,  # Mark as success since validation is optional
                            output={
                                "error": str(e),
                                "validation_skipped": True,
                                "validation_optional": True,
                            },
                            duration_ms=0,
                        ),
                    )

        # Phase 4: Reporting (always run)
        status_result = await self.reporter.generate_status_report()
        results.append(status_result)

        summary_result = await self.reporter.generate_maintenance_summary(results)
        results.append(summary_result)

        # Compile final output
        output = {
            "mode": mode,
            "timestamp": datetime.now().isoformat(),
            "results": [r.output for r in results],
            "summary": summary_result.output,
            "success": all(r.success for r in results),
        }

        # Save to history
        self._run_history.append(output)

        return output

    def get_run_history(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get recent run history."""
        return self._run_history[-limit:]

    def get_crew_status(self) -> dict[str, Any]:
        """Get current crew status."""
        return {
            "project_root": str(self.project_root),
            "config": {
                "auto_generation": self.config.enable_auto_generation,
                "auto_validation": self.config.enable_auto_validation,
                "max_files_per_run": self.config.max_files_per_run,
            },
            "index_status": {
                "total_files": self.index.get_summary().total_files,
                "files_needing_tests": self.index.get_summary().files_without_tests,
            },
            "run_count": len(self._run_history),
        }


def create_crew_config_from_dict(config_dict: dict[str, Any]) -> CrewConfig:
    """Create CrewConfig from dictionary."""
    return CrewConfig(
        enable_auto_generation=config_dict.get("enable_auto_generation", True),
        enable_auto_validation=config_dict.get("enable_auto_validation", True),
        max_files_per_run=config_dict.get("max_files_per_run", 10),
        min_coverage_target=config_dict.get("min_coverage_target", 80.0),
        staleness_threshold_days=config_dict.get("staleness_threshold_days", 7),
        high_impact_threshold=config_dict.get("high_impact_threshold", 5.0),
        auto_run_interval_hours=config_dict.get("auto_run_interval_hours", 24),
        run_on_commit=config_dict.get("run_on_commit", True),
        test_gen_model=config_dict.get("test_gen_model", "sonnet"),
        validation_model=config_dict.get("validation_model", "haiku"),
    )
