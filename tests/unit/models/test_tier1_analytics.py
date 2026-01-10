"""Unit tests for Tier 1 analytics methods.

Tests the five analytics methods in TelemetryAnalytics:
- task_routing_accuracy()
- test_execution_trends()
- coverage_progress()
- agent_performance()
- tier1_summary()

Tests cover:
- Calculations with various data scenarios
- Date range filtering
- Empty data handling
- Edge cases (single record, no data, etc.)
- Aggregation accuracy
"""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from empathy_os.models import (
    AgentAssignmentRecord,
    CoverageRecord,
    TaskRoutingRecord,
    TestExecutionRecord,
)
from empathy_os.models.telemetry import TelemetryAnalytics, TelemetryStore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test telemetry data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def store(temp_dir):
    """Create a TelemetryStore instance with temporary directory."""
    return TelemetryStore(storage_dir=str(temp_dir))


@pytest.fixture
def analytics(store):
    """Create a TelemetryAnalytics instance."""
    return TelemetryAnalytics(store)


class TestTaskRoutingAccuracy:
    """Test suite for task_routing_accuracy analytics method."""

    def test_empty_data(self, analytics):
        """Test analytics with no routing data."""
        stats = analytics.task_routing_accuracy()

        assert stats["total_tasks"] == 0
        assert stats["successful_routing"] == 0
        assert stats["accuracy_rate"] == 0.0
        assert stats["avg_confidence"] == 0.0
        assert stats["by_task_type"] == {}
        assert stats["by_strategy"] == {}

    def test_single_successful_routing(self, store, analytics):
        """Test analytics with single successful routing."""
        record = TaskRoutingRecord(
            routing_id="routing-1",
            timestamp=datetime.utcnow().isoformat(),
            task_description="Test task",
            task_type="code_review",
            task_complexity="simple",
            assigned_agent="review-agent",
            assigned_tier="claude-sonnet-4.5",
            routing_strategy="rule_based",
            confidence_score=0.95,
            status="completed",
            success=True,
        )
        store.log_task_routing(record)

        stats = analytics.task_routing_accuracy()

        assert stats["total_tasks"] == 1
        assert stats["successful_routing"] == 1
        assert stats["accuracy_rate"] == 1.0  # Returns decimal, not percentage
        assert stats["avg_confidence"] == 0.95

    def test_multiple_routings_mixed_success(self, store, analytics):
        """Test analytics with multiple routings (some successful, some failed)."""
        # Successful routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-1",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Task 1",
                task_type="code_review",
                task_complexity="simple",
                assigned_agent="review-agent",
                assigned_tier="claude-sonnet-4.5",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )

        # Failed routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-2",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Task 2",
                task_type="bug_fix",
                task_complexity="moderate",
                assigned_agent="bug-agent",
                assigned_tier="claude-sonnet-4.5",
                routing_strategy="ml_predicted",
                confidence_score=0.70,
                status="failed",
                success=False,
            )
        )

        # Another successful routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-3",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Task 3",
                task_type="testing",
                task_complexity="simple",
                assigned_agent="test-agent",
                assigned_tier="claude-haiku-4",
                routing_strategy="rule_based",
                confidence_score=0.88,
                status="completed",
                success=True,
            )
        )

        stats = analytics.task_routing_accuracy()

        assert stats["total_tasks"] == 3
        assert stats["successful_routing"] == 2
        assert stats["accuracy_rate"] == pytest.approx(0.6667, rel=0.01)  # Returns decimal
        assert stats["avg_confidence"] == pytest.approx(0.843, rel=0.01)

    def test_breakdown_by_task_type(self, store, analytics):
        """Test that results are broken down by task type."""
        # Code review tasks
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-1",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Review 1",
                task_type="code_review",
                task_complexity="simple",
                assigned_agent="review-agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-2",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Review 2",
                task_type="code_review",
                task_complexity="moderate",
                assigned_agent="review-agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.90,
                status="completed",
                success=True,
            )
        )

        # Bug fix task
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-3",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Bug 1",
                task_type="bug_fix",
                task_complexity="simple",
                assigned_agent="bug-agent",
                assigned_tier="tier",
                routing_strategy="ml_predicted",
                confidence_score=0.75,
                status="failed",
                success=False,
            )
        )

        stats = analytics.task_routing_accuracy()

        assert "code_review" in stats["by_task_type"]
        assert "bug_fix" in stats["by_task_type"]
        # Analytics returns "total" not "count", and "rate" not "success_rate"
        assert stats["by_task_type"]["code_review"]["total"] == 2
        assert stats["by_task_type"]["code_review"]["rate"] == 1.0  # Decimal, not percentage
        assert stats["by_task_type"]["bug_fix"]["total"] == 1
        assert stats["by_task_type"]["bug_fix"]["rate"] == 0.0

    def test_breakdown_by_strategy(self, store, analytics):
        """Test that results are broken down by routing strategy."""
        # Rule-based routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-1",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Task 1",
                task_type="test",
                task_complexity="simple",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )

        # ML predicted routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-2",
                timestamp=datetime.utcnow().isoformat(),
                task_description="Task 2",
                task_type="test",
                task_complexity="moderate",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="ml_predicted",
                confidence_score=0.80,
                status="completed",
                success=True,
            )
        )

        stats = analytics.task_routing_accuracy()

        assert "rule_based" in stats["by_strategy"]
        assert "ml_predicted" in stats["by_strategy"]
        # Analytics returns "total" not "count"
        assert stats["by_strategy"]["rule_based"]["total"] == 1
        assert stats["by_strategy"]["ml_predicted"]["total"] == 1

    def test_date_filtering(self, store, analytics):
        """Test that since parameter filters by date correctly."""
        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=10)).isoformat()
        recent_timestamp = (now - timedelta(hours=1)).isoformat()

        # Old routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-old",
                timestamp=old_timestamp,
                task_description="Old task",
                task_type="test",
                task_complexity="simple",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )

        # Recent routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-recent",
                timestamp=recent_timestamp,
                task_description="Recent task",
                task_type="test",
                task_complexity="simple",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.90,
                status="completed",
                success=True,
            )
        )

        # Filter to last 24 hours
        since = now - timedelta(hours=24)
        stats = analytics.task_routing_accuracy(since=since)

        # Should only include recent routing
        assert stats["total_tasks"] == 1


class TestTestExecutionTrends:
    """Test suite for test_execution_trends analytics method."""

    def test_empty_data(self, analytics):
        """Test analytics with no test execution data."""
        stats = analytics.test_execution_trends()

        assert stats["total_executions"] == 0
        assert stats["success_rate"] == 0.0
        assert stats["avg_duration_seconds"] == 0.0
        assert stats["total_tests_run"] == 0
        assert stats["total_failures"] == 0
        assert stats["most_failing_tests"] == []

    def test_single_successful_execution(self, store, analytics):
        """Test analytics with single successful test execution."""
        record = TestExecutionRecord(
            execution_id="test-1",
            timestamp=datetime.utcnow().isoformat(),
            test_suite="unit",
            triggered_by="manual",
            command="pytest tests/unit/",
            working_directory="/project",
            duration_seconds=45.2,
            total_tests=100,
            passed=100,
            failed=0,
            skipped=0,
            errors=0,
            success=True,
            exit_code=0,
        )
        store.log_test_execution(record)

        stats = analytics.test_execution_trends()

        assert stats["total_executions"] == 1
        assert stats["success_rate"] == 1.0  # Returns decimal, not percentage
        assert stats["avg_duration_seconds"] == 45.2
        assert stats["total_tests_run"] == 100
        assert stats["total_failures"] == 0

    def test_multiple_executions_mixed_results(self, store, analytics):
        """Test analytics with multiple test executions."""
        # Successful execution
        store.log_test_execution(
            TestExecutionRecord(
                execution_id="test-1",
                timestamp=datetime.utcnow().isoformat(),
                test_suite="unit",
                triggered_by="manual",
                command="pytest",
                working_directory="/project",
                duration_seconds=30.0,
                total_tests=50,
                passed=50,
                failed=0,
                skipped=0,
                errors=0,
                success=True,
                exit_code=0,
            )
        )

        # Failed execution
        store.log_test_execution(
            TestExecutionRecord(
                execution_id="test-2",
                timestamp=datetime.utcnow().isoformat(),
                test_suite="integration",
                triggered_by="ci",
                command="pytest",
                working_directory="/project",
                duration_seconds=90.0,
                total_tests=25,
                passed=20,
                failed=5,
                skipped=0,
                errors=0,
                success=False,
                exit_code=1,
                failed_tests=[{"name": "test_api", "file": "test_api.py", "error": "Timeout"}],
            )
        )

        stats = analytics.test_execution_trends()

        assert stats["total_executions"] == 2
        assert stats["success_rate"] == 0.5  # Returns decimal, not percentage
        assert stats["avg_duration_seconds"] == 60.0
        assert stats["total_tests_run"] == 75
        assert stats["total_failures"] == 5

    def test_most_failing_tests(self, store, analytics):
        """Test that most failing tests are identified."""
        # Multiple executions with same failing test
        for i in range(3):
            store.log_test_execution(
                TestExecutionRecord(
                    execution_id=f"test-{i}",
                    timestamp=datetime.utcnow().isoformat(),
                    test_suite="unit",
                    triggered_by="ci",
                    command="pytest",
                    working_directory="/project",
                    duration_seconds=10.0,
                    total_tests=10,
                    passed=9,
                    failed=1,
                    skipped=0,
                    errors=0,
                    success=False,
                    exit_code=1,
                    failed_tests=[
                        {"name": "test_flaky", "file": "test_unit.py", "error": "AssertionError"}
                    ],
                )
            )

        stats = analytics.test_execution_trends()

        assert len(stats["most_failing_tests"]) > 0
        # Most failing test should be test_flaky
        most_failing = stats["most_failing_tests"][0]
        assert most_failing["name"] == "test_flaky"
        # Analytics returns "failures" not "failure_count"
        assert most_failing["failures"] == 3


class TestCoverageProgress:
    """Test suite for coverage_progress analytics method."""

    def test_empty_data(self, analytics):
        """Test analytics with no coverage data."""
        stats = analytics.coverage_progress()

        assert stats["current_coverage"] == 0.0
        assert stats["trend"] == "no_data"
        assert stats["coverage_history"] == []
        assert stats["critical_gaps_count"] == 0

    def test_single_coverage_record(self, store, analytics):
        """Test analytics with single coverage record."""
        record = CoverageRecord(
            record_id="cov-1",
            timestamp=datetime.utcnow().isoformat(),
            overall_percentage=85.5,
            lines_total=1000,
            lines_covered=855,
            branches_total=200,
            branches_covered=150,
            files_total=50,
            files_well_covered=35,
            files_critical=5,
            trend="stable",
            coverage_format="xml",
            coverage_file="coverage.xml",
        )
        store.log_coverage(record)

        stats = analytics.coverage_progress()

        assert stats["current_coverage"] == 85.5
        assert stats["trend"] == "stable"
        assert len(stats["coverage_history"]) == 1

    def test_improving_trend(self, store, analytics):
        """Test detection of improving coverage trend."""
        now = datetime.utcnow()

        # Older coverage
        store.log_coverage(
            CoverageRecord(
                record_id="cov-1",
                timestamp=(now - timedelta(days=7)).isoformat(),
                overall_percentage=75.0,
                lines_total=1000,
                lines_covered=750,
                branches_total=200,
                branches_covered=140,
                files_total=50,
                files_well_covered=30,
                files_critical=10,
                trend="stable",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

        # Recent improved coverage
        store.log_coverage(
            CoverageRecord(
                record_id="cov-2",
                timestamp=now.isoformat(),
                overall_percentage=85.0,
                lines_total=1000,
                lines_covered=850,
                branches_total=200,
                branches_covered=170,
                files_total=50,
                files_well_covered=40,
                files_critical=3,
                trend="improving",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

        stats = analytics.coverage_progress()

        assert stats["current_coverage"] == 85.0
        assert stats["trend"] == "improving"
        assert len(stats["coverage_history"]) == 2

    def test_declining_trend(self, store, analytics):
        """Test detection of declining coverage trend."""
        now = datetime.utcnow()

        # Older higher coverage
        store.log_coverage(
            CoverageRecord(
                record_id="cov-1",
                timestamp=(now - timedelta(days=7)).isoformat(),
                overall_percentage=90.0,
                lines_total=1000,
                lines_covered=900,
                branches_total=200,
                branches_covered=180,
                files_total=50,
                files_well_covered=45,
                files_critical=1,
                trend="stable",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

        # Recent declined coverage
        store.log_coverage(
            CoverageRecord(
                record_id="cov-2",
                timestamp=now.isoformat(),
                overall_percentage=75.0,
                lines_total=1000,
                lines_covered=750,
                branches_total=200,
                branches_covered=150,
                files_total=50,
                files_well_covered=35,
                files_critical=8,
                trend="declining",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

        stats = analytics.coverage_progress()

        assert stats["current_coverage"] == 75.0
        assert stats["trend"] == "declining"


class TestAgentPerformance:
    """Test suite for agent_performance analytics method."""

    def test_empty_data(self, analytics):
        """Test analytics with no agent assignment data."""
        stats = analytics.agent_performance()

        assert stats["total_assignments"] == 0
        assert stats["automation_rate"] == 0.0
        assert stats["by_agent"] == {}

    def test_single_agent_assignment(self, store, analytics):
        """Test analytics with single agent assignment."""
        record = AgentAssignmentRecord(
            assignment_id="assign-1",
            timestamp=datetime.utcnow().isoformat(),
            task_id="task-1",
            task_title="Fix bug",
            task_description="Fix authentication bug",
            assigned_agent="bug-fix-agent",
            assignment_reason="Rule-based",
            automated_eligible=True,
            task_spec_clarity=0.95,
            has_dependencies=False,
            status="completed",
            success=True,
            actual_duration_hours=300.0 / 3600.0,
            quality_check_passed=True,
        )
        store.log_agent_assignment(record)

        stats = analytics.agent_performance()

        assert stats["total_assignments"] == 1
        assert "bug-fix-agent" in stats["by_agent"]
        assert stats["by_agent"]["bug-fix-agent"]["assignments"] == 1
        assert stats["by_agent"]["bug-fix-agent"]["success_rate"] == 1.0  # Returns decimal

    def test_multiple_agents(self, store, analytics):
        """Test analytics with multiple agents."""
        # Agent 1: High success rate
        for i in range(5):
            store.log_agent_assignment(
                AgentAssignmentRecord(
                    assignment_id=f"assign-1-{i}",
                    timestamp=datetime.utcnow().isoformat(),
                    task_id=f"task-1-{i}",
                    task_title=f"Task {i}",
                    task_description="Description",
                    assigned_agent="agent-1",
                    assignment_reason="Rule",
                    automated_eligible=True,
                    task_spec_clarity=0.95,
                    has_dependencies=False,
                    status="completed",
                    success=True,
                )
            )

        # Agent 2: Lower success rate
        for i in range(3):
            store.log_agent_assignment(
                AgentAssignmentRecord(
                    assignment_id=f"assign-2-{i}",
                    timestamp=datetime.utcnow().isoformat(),
                    task_id=f"task-2-{i}",
                    task_title=f"Task {i}",
                    task_description="Description",
                    assigned_agent="agent-2",
                    assignment_reason="Rule",
                    automated_eligible=True,
                    task_spec_clarity=0.80,
                    has_dependencies=False,
                    status="completed",
                    success=(i < 2),  # 2 successes, 1 failure
                )
            )

        stats = analytics.agent_performance()

        assert stats["total_assignments"] == 8
        assert "agent-1" in stats["by_agent"]
        assert "agent-2" in stats["by_agent"]
        assert stats["by_agent"]["agent-1"]["success_rate"] == 1.0  # Returns decimal
        assert stats["by_agent"]["agent-2"]["success_rate"] == pytest.approx(
            0.6667, rel=0.01
        )  # Returns decimal


class TestTier1Summary:
    """Test suite for tier1_summary analytics method."""

    def test_empty_data(self, analytics):
        """Test summary with no data."""
        summary = analytics.tier1_summary()

        assert "task_routing" in summary
        assert "test_execution" in summary
        assert "coverage" in summary
        assert "agent_performance" in summary
        assert summary["task_routing"]["total_tasks"] == 0
        assert summary["test_execution"]["total_executions"] == 0

    def test_comprehensive_summary(self, store, analytics):
        """Test summary with all types of data."""
        now = datetime.utcnow()

        # Add routing data
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-1",
                timestamp=now.isoformat(),
                task_description="Task 1",
                task_type="code_review",
                task_complexity="simple",
                assigned_agent="review-agent",
                assigned_tier="claude-sonnet-4.5",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )

        # Add test execution data
        store.log_test_execution(
            TestExecutionRecord(
                execution_id="test-1",
                timestamp=now.isoformat(),
                test_suite="unit",
                triggered_by="manual",
                command="pytest",
                working_directory="/project",
                duration_seconds=30.0,
                total_tests=50,
                passed=50,
                failed=0,
                skipped=0,
                errors=0,
                success=True,
                exit_code=0,
            )
        )

        # Add coverage data
        store.log_coverage(
            CoverageRecord(
                record_id="cov-1",
                timestamp=now.isoformat(),
                overall_percentage=85.0,
                lines_total=1000,
                lines_covered=850,
                branches_total=200,
                branches_covered=170,
                files_total=50,
                files_well_covered=40,
                files_critical=3,
                trend="stable",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

        # Add agent assignment data
        store.log_agent_assignment(
            AgentAssignmentRecord(
                assignment_id="assign-1",
                timestamp=now.isoformat(),
                task_id="task-1",
                task_title="Fix bug",
                task_description="Fix bug",
                assigned_agent="bug-agent",
                assignment_reason="Rule",
                automated_eligible=True,
                task_spec_clarity=0.95,
                has_dependencies=False,
                status="completed",
                success=True,
            )
        )

        summary = analytics.tier1_summary()

        # Verify all sections populated
        assert summary["task_routing"]["total_tasks"] == 1
        assert summary["test_execution"]["total_executions"] == 1
        assert summary["coverage"]["current_coverage"] == 85.0
        assert summary["agent_performance"]["total_assignments"] == 1

    def test_summary_with_date_filtering(self, store, analytics):
        """Test that summary respects since parameter."""
        now = datetime.utcnow()
        old_timestamp = (now - timedelta(days=10)).isoformat()
        recent_timestamp = (now - timedelta(hours=1)).isoformat()

        # Old routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-old",
                timestamp=old_timestamp,
                task_description="Old task",
                task_type="test",
                task_complexity="simple",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.95,
                status="completed",
                success=True,
            )
        )

        # Recent routing
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id="routing-recent",
                timestamp=recent_timestamp,
                task_description="Recent task",
                task_type="test",
                task_complexity="simple",
                assigned_agent="agent",
                assigned_tier="tier",
                routing_strategy="rule_based",
                confidence_score=0.90,
                status="completed",
                success=True,
            )
        )

        # Filter to last 24 hours
        since = now - timedelta(hours=24)
        summary = analytics.tier1_summary(since=since)

        # Should only include recent routing
        assert summary["task_routing"]["total_tasks"] == 1
