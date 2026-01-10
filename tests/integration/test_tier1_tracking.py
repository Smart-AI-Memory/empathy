"""Integration tests for Tier 1 tracking.

Tests end-to-end flows:
- Workflow automatic routing tracking
- Explicit test execution tracking
- Coverage tracking from coverage.xml
- Data persistence and retrieval

These tests verify that the complete Tier 1 system works together.
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from empathy_os.models import get_telemetry_store
from empathy_os.models.telemetry import TelemetryAnalytics
from empathy_os.workflows.base import BaseWorkflow, WorkflowStage
from empathy_os.workflows.test_runner import run_tests_with_tracking, track_coverage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test telemetry data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_telemetry_dir(temp_dir, monkeypatch):
    """Mock the telemetry directory for testing."""
    monkeypatch.setenv("EMPATHY_TELEMETRY_DIR", str(temp_dir))
    return temp_dir


class TestWorkflowRoutingTracking:
    """Test automatic routing tracking in workflows."""

    def test_workflow_tracks_routing_automatically(self, mock_telemetry_dir):
        """Test that workflows automatically track routing records."""

        # Create a simple workflow
        class SimpleWorkflow(BaseWorkflow):
            def __init__(self):
                super().__init__(
                    name="simple-test-workflow",
                    description="Test workflow for routing tracking",
                    version="1.0.0",
                )

            async def _execute_impl(self, **kwargs):
                # Simple workflow that just returns success
                return {"result": "success", "data": kwargs.get("data", "test")}

        # Run workflow (this should track routing automatically)
        workflow = SimpleWorkflow()

        # Execute workflow (need to use asyncio)
        import asyncio

        result = asyncio.run(workflow.execute(data="test input"))

        # Workflow should succeed
        assert result.success is True

        # Check that routing was tracked
        store = get_telemetry_store()
        routings = store.get_task_routings(limit=10)

        # Should have at least one routing record
        assert len(routings) > 0

        # Most recent routing should be for our workflow
        latest_routing = routings[0]
        assert latest_routing.task_type == "simple-test-workflow"
        assert latest_routing.assigned_agent == "simple-test-workflow"
        assert latest_routing.status in ["completed", "running"]

    def test_workflow_routing_includes_complexity(self, mock_telemetry_dir):
        """Test that routing includes complexity assessment."""

        class ComplexWorkflow(BaseWorkflow):
            def __init__(self):
                super().__init__(
                    name="complex-workflow",
                    description="Complex workflow with multiple stages",
                    version="1.0.0",
                )

                # Add multiple stages to increase complexity
                self.stages = [
                    WorkflowStage(name="stage1", description="Stage 1"),
                    WorkflowStage(name="stage2", description="Stage 2"),
                    WorkflowStage(name="stage3", description="Stage 3"),
                ]

            async def _execute_impl(self, **kwargs):
                return {"result": "success"}

        workflow = ComplexWorkflow()

        import asyncio

        result = asyncio.run(workflow.execute())

        assert result.success is True

        # Check routing complexity
        store = get_telemetry_store()
        routings = store.get_task_routings(limit=1)

        assert len(routings) > 0
        latest_routing = routings[0]

        # Should assess complexity based on stages
        assert latest_routing.task_complexity in ["simple", "moderate", "complex"]

    def test_workflow_routing_tracks_success_and_cost(self, mock_telemetry_dir):
        """Test that routing tracks success status and actual cost."""

        class SuccessfulWorkflow(BaseWorkflow):
            def __init__(self):
                super().__init__(
                    name="successful-workflow",
                    description="Workflow that succeeds",
                    version="1.0.0",
                )

            async def _execute_impl(self, **kwargs):
                return {"result": "success"}

        workflow = SuccessfulWorkflow()

        import asyncio

        result = asyncio.run(workflow.execute())

        assert result.success is True

        # Check routing record
        store = get_telemetry_store()
        routings = store.get_task_routings(limit=1)

        assert len(routings) > 0
        latest_routing = routings[0]

        # Should track success
        assert latest_routing.success is True
        assert latest_routing.status == "completed"


class TestExplicitTestTracking:
    """Test explicit opt-in test execution tracking."""

    def test_run_tests_with_tracking_creates_record(self, mock_telemetry_dir, monkeypatch):
        """Test that run_tests_with_tracking creates a test execution record."""
        # Mock subprocess.run to simulate pytest
        import subprocess

        def mock_run(*args, **kwargs):
            # Simulate successful pytest run
            class MockResult:
                returncode = 0
                stdout = "===== 10 passed in 2.5s ====="
                stderr = ""

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Run tests with tracking
        record = run_tests_with_tracking(
            test_suite="unit",
            test_files=["tests/unit/test_sample.py"],
            triggered_by="manual",
        )

        # Should return a record
        assert record is not None
        assert record.test_suite == "unit"
        assert record.triggered_by == "manual"
        assert record.success is True

        # Should be logged to telemetry store
        store = get_telemetry_store()
        executions = store.get_test_executions(limit=10)

        assert len(executions) > 0
        latest_execution = executions[0]
        assert latest_execution.test_suite == "unit"

    def test_run_tests_with_tracking_handles_failures(self, mock_telemetry_dir, monkeypatch):
        """Test that run_tests_with_tracking handles test failures."""
        import subprocess

        def mock_run(*args, **kwargs):
            # Simulate failed pytest run
            class MockResult:
                returncode = 1
                stdout = """
===== FAILURES =====
_____ test_sample _____
FAILED tests/unit/test_sample.py::test_sample - AssertionError
===== 5 passed, 1 failed in 2.5s =====
"""
                stderr = ""

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Run tests with tracking
        record = run_tests_with_tracking(
            test_suite="unit",
            triggered_by="ci",
        )

        # Should return a record with failure info
        assert record is not None
        assert record.success is False
        assert record.failed > 0
        assert len(record.failed_tests) > 0

    def test_run_tests_with_tracking_handles_timeout(self, mock_telemetry_dir, monkeypatch):
        """Test that run_tests_with_tracking handles timeouts."""
        import subprocess

        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd="pytest", timeout=600)

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Run tests with tracking
        record = run_tests_with_tracking(test_suite="integration", triggered_by="ci")

        # Should return a record with timeout error
        assert record is not None
        assert record.success is False
        assert record.exit_code == 124  # Timeout exit code
        assert len(record.failed_tests) > 0
        assert "timeout" in record.failed_tests[0]["name"].lower()


class TestCoverageTracking:
    """Test coverage tracking from coverage.xml."""

    def test_track_coverage_parses_xml(self, mock_telemetry_dir, tmp_path):
        """Test that track_coverage parses coverage.xml correctly."""
        # Create a sample coverage.xml file
        coverage_xml = tmp_path / "coverage.xml"
        coverage_content = """<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1704800000000" lines-valid="1000" lines-covered="850" line-rate="0.85" branches-valid="200" branches-covered="150" branch-rate="0.75">
    <packages>
        <package name="src" line-rate="0.85" branch-rate="0.75" complexity="0">
            <classes>
                <class name="module1.py" filename="src/module1.py" line-rate="0.90" branch-rate="0.80" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                        <line number="3" hits="0"/>
                    </lines>
                </class>
                <class name="module2.py" filename="src/module2.py" line-rate="0.45" branch-rate="0.40" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="0"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
        coverage_xml.write_text(coverage_content)

        # Track coverage
        record = track_coverage(coverage_file=str(coverage_xml))

        # Should parse correctly
        assert record is not None
        assert record.overall_percentage == 85.0
        assert record.lines_total == 1000
        assert record.lines_covered == 850
        assert record.branches_total == 200
        assert record.branches_covered == 150

        # Should be logged to telemetry store
        store = get_telemetry_store()
        coverage_records = store.get_coverage_history(limit=10)

        assert len(coverage_records) > 0
        latest_coverage = coverage_records[0]
        assert latest_coverage.overall_percentage == 85.0

    def test_track_coverage_identifies_critical_gaps(self, mock_telemetry_dir, tmp_path):
        """Test that track_coverage identifies files with low coverage."""
        # Create coverage.xml with critical gap
        coverage_xml = tmp_path / "coverage.xml"
        coverage_content = """<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1704800000000" lines-valid="500" lines-covered="400" line-rate="0.80" branches-valid="100" branches-covered="80" branch-rate="0.80">
    <packages>
        <package name="src" line-rate="0.80" branch-rate="0.80" complexity="0">
            <classes>
                <class name="auth.py" filename="src/auth.py" line-rate="0.30" branch-rate="0.20" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="0"/>
                        <line number="3" hits="0"/>
                    </lines>
                </class>
                <class name="utils.py" filename="src/utils.py" line-rate="0.95" branch-rate="0.90" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                        <line number="2" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
        coverage_xml.write_text(coverage_content)

        # Track coverage
        record = track_coverage(coverage_file=str(coverage_xml))

        # Should identify critical gaps (files with <50% coverage)
        assert record is not None
        assert record.files_critical > 0
        assert len(record.critical_gaps) > 0

        # auth.py should be in critical gaps (30% coverage)
        critical_files = [gap["file"] for gap in record.critical_gaps]
        assert any("auth.py" in f for f in critical_files)

    def test_track_coverage_determines_trend(self, mock_telemetry_dir, tmp_path):
        """Test that track_coverage determines coverage trend."""
        # Create coverage.xml
        coverage_xml = tmp_path / "coverage.xml"
        coverage_content = """<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1704800000000" lines-valid="1000" lines-covered="900" line-rate="0.90" branches-valid="200" branches-covered="180" branch-rate="0.90">
    <packages>
        <package name="src" line-rate="0.90" branch-rate="0.90" complexity="0">
            <classes>
                <class name="module.py" filename="src/module.py" line-rate="0.90" branch-rate="0.90" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
        coverage_xml.write_text(coverage_content)

        # First coverage record (85%)
        store = get_telemetry_store()

        # Track first coverage (manually create with lower percentage)
        from empathy_os.models import CoverageRecord

        old_record = CoverageRecord(
            record_id="cov-old",
            timestamp=datetime.utcnow().isoformat() + "Z",
            overall_percentage=85.0,
            lines_total=1000,
            lines_covered=850,
            branches_total=200,
            branches_covered=170,
            files_total=10,
            files_well_covered=8,
            files_critical=2,
            trend="stable",
            coverage_format="xml",
            coverage_file="coverage.xml",
        )
        store.log_coverage(old_record)

        # Track new coverage (90%)
        record = track_coverage(coverage_file=str(coverage_xml))

        # Should detect improving trend (85% -> 90%)
        assert record is not None
        assert record.overall_percentage == 90.0
        assert record.trend == "improving"

    def test_track_coverage_raises_on_missing_file(self, mock_telemetry_dir):
        """Test that track_coverage raises error for missing coverage file."""
        with pytest.raises(FileNotFoundError):
            track_coverage(coverage_file="nonexistent_coverage.xml")


class TestEndToEndIntegration:
    """Test complete end-to-end integration scenarios."""

    def test_workflow_with_test_tracking(self, mock_telemetry_dir, monkeypatch):
        """Test workflow that includes test execution tracking."""
        import subprocess

        def mock_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "===== 50 passed in 10.5s ====="
                stderr = ""

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Create workflow
        class TestRunnerWorkflow(BaseWorkflow):
            def __init__(self):
                super().__init__(
                    name="test-runner",
                    description="Runs tests with tracking",
                    version="1.0.0",
                )

            async def _execute_impl(self, **kwargs):
                # Run tests with tracking
                test_record = run_tests_with_tracking(
                    test_suite="unit",
                    triggered_by="workflow",
                    workflow_id=self._run_id,
                )
                return {"test_record": test_record, "success": test_record.success}

        workflow = TestRunnerWorkflow()

        import asyncio

        result = asyncio.run(workflow.execute())

        # Workflow should succeed
        assert result.success is True

        # Should have both routing and test execution records
        store = get_telemetry_store()

        routings = store.get_task_routings(limit=10)
        assert len(routings) > 0

        executions = store.get_test_executions(limit=10)
        assert len(executions) > 0

        # Test execution should be linked to workflow
        latest_execution = executions[0]
        assert latest_execution.workflow_id is not None

    def test_complete_tier1_data_flow(self, mock_telemetry_dir, monkeypatch, tmp_path):
        """Test complete Tier 1 data flow: routing + tests + coverage."""
        import subprocess

        def mock_run(*args, **kwargs):
            class MockResult:
                returncode = 0
                stdout = "===== 25 passed in 5.0s ====="
                stderr = ""

            return MockResult()

        monkeypatch.setattr(subprocess, "run", mock_run)

        # Create coverage.xml
        coverage_xml = tmp_path / "coverage.xml"
        coverage_content = """<?xml version="1.0" ?>
<coverage version="7.0" timestamp="1704800000000" lines-valid="500" lines-covered="425" line-rate="0.85" branches-valid="100" branches-covered="85" branch-rate="0.85">
    <packages>
        <package name="src" line-rate="0.85" branch-rate="0.85" complexity="0">
            <classes>
                <class name="module.py" filename="src/module.py" line-rate="0.85" branch-rate="0.85" complexity="0">
                    <methods/>
                    <lines>
                        <line number="1" hits="1"/>
                    </lines>
                </class>
            </classes>
        </package>
    </packages>
</coverage>
"""
        coverage_xml.write_text(coverage_content)

        # Create workflow that does everything
        class CompleteWorkflow(BaseWorkflow):
            def __init__(self):
                super().__init__(
                    name="complete-test-workflow",
                    description="Complete test workflow with tracking",
                    version="1.0.0",
                )

            async def _execute_impl(self, **kwargs):
                # Run tests
                test_record = run_tests_with_tracking(
                    test_suite="unit", triggered_by="workflow", workflow_id=self._run_id
                )

                # Track coverage
                coverage_record = track_coverage(
                    coverage_file=str(coverage_xml), workflow_id=self._run_id
                )

                return {
                    "test_success": test_record.success,
                    "coverage": coverage_record.overall_percentage,
                }

        workflow = CompleteWorkflow()

        import asyncio

        result = asyncio.run(workflow.execute())

        assert result.success is True

        # Should have all three types of records
        store = get_telemetry_store()
        analytics = TelemetryAnalytics(store)

        routings = store.get_task_routings(limit=10)
        assert len(routings) > 0

        executions = store.get_test_executions(limit=10)
        assert len(executions) > 0

        coverage_records = store.get_coverage_history(limit=10)
        assert len(coverage_records) > 0

        # Analytics should work
        summary = analytics.tier1_summary()

        assert summary["task_routing"]["total_tasks"] > 0
        assert summary["test_execution"]["total_executions"] > 0
        assert summary["coverage"]["current_coverage"] > 0
