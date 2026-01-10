"""Unit tests for Tier 1 record types.

Tests the four Tier 1 telemetry record types:
- TaskRoutingRecord
- TestExecutionRecord
- CoverageRecord
- AgentAssignmentRecord

Tests cover:
- Record creation and validation
- Serialization to dict (to_dict)
- Deserialization from dict (from_dict)
- Edge cases (empty values, optional fields, invalid data)
- Field defaults and required fields
"""

import json

from empathy_os.models import (
    AgentAssignmentRecord,
    CoverageRecord,
    TaskRoutingRecord,
    TestExecutionRecord,
)


class TestTaskRoutingRecord:
    """Test suite for TaskRoutingRecord."""

    def test_create_minimal_record(self):
        """Test creating record with minimal required fields."""
        record = TaskRoutingRecord(
            routing_id="routing-123",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Test task",
            task_type="code_review",
            task_complexity="simple",
            assigned_agent="code-review-agent",
            assigned_tier="claude-sonnet-4.5",
            routing_strategy="rule_based",
            confidence_score=0.95,
        )

        assert record.routing_id == "routing-123"
        assert record.task_description == "Test task"
        assert record.task_complexity == "simple"
        assert record.confidence_score == 0.95

    def test_create_full_record(self):
        """Test creating record with all fields populated."""
        record = TaskRoutingRecord(
            routing_id="routing-456",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Complex refactoring task",
            task_type="refactoring",
            task_complexity="complex",
            assigned_agent="refactor-agent",
            assigned_tier="claude-opus-4.5",
            routing_strategy="ml_predicted",
            confidence_score=0.87,
            metadata={"priority": "high", "tags": ["refactor", "performance"]},
            task_dependencies=["task-1", "task-2"],
            estimated_cost=0.15,
            status="completed",
            started_at="2026-01-09T10:00:00Z",
            completed_at="2026-01-09T10:05:00Z",
            success=True,
            actual_cost=0.12,
            error_message=None,
        )

        assert record.routing_strategy == "ml_predicted"
        assert record.confidence_score == 0.87
        assert record.metadata == {"priority": "high", "tags": ["refactor", "performance"]}
        assert record.task_dependencies == ["task-1", "task-2"]
        assert record.estimated_cost == 0.15
        assert record.actual_cost == 0.12
        assert record.success is True

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        record = TaskRoutingRecord(
            routing_id="routing-789",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Test serialization",
            task_type="testing",
            task_complexity="moderate",
            assigned_agent="test-agent",
            assigned_tier="claude-sonnet-4.5",
            routing_strategy="rule_based",
            confidence_score=0.92,
            metadata={"env": "test"},
            status="running",
        )

        data = record.to_dict()

        assert isinstance(data, dict)
        assert data["routing_id"] == "routing-789"
        assert data["task_description"] == "Test serialization"
        assert data["task_complexity"] == "moderate"
        assert data["confidence_score"] == 0.92
        assert data["metadata"] == {"env": "test"}
        assert data["status"] == "running"

    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data = {
            "routing_id": "routing-abc",
            "timestamp": "2026-01-09T10:00:00Z",
            "task_description": "Test deserialization",
            "task_type": "testing",
            "task_complexity": "simple",
            "assigned_agent": "test-agent",
            "assigned_tier": "claude-sonnet-4.5",
            "routing_strategy": "manual_override",
            "confidence_score": 1.0,
            "metadata": {"source": "manual"},
            "status": "pending",
        }

        record = TaskRoutingRecord.from_dict(data)

        assert record.routing_id == "routing-abc"
        assert record.task_description == "Test deserialization"
        assert record.routing_strategy == "manual_override"
        assert record.confidence_score == 1.0
        assert record.metadata == {"source": "manual"}
        assert record.status == "pending"

    def test_round_trip_serialization(self):
        """Test that to_dict -> from_dict preserves all data."""
        original = TaskRoutingRecord(
            routing_id="routing-round-trip",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Round trip test",
            task_type="testing",
            task_complexity="complex",
            assigned_agent="test-agent",
            assigned_tier="claude-opus-4.5",
            routing_strategy="ml_predicted",
            confidence_score=0.85,
            metadata={"test": True, "round_trip": 1},
            task_dependencies=["dep1", "dep2", "dep3"],
            estimated_cost=0.25,
            status="completed",
            success=True,
            actual_cost=0.20,
        )

        data = original.to_dict()
        restored = TaskRoutingRecord.from_dict(data)

        assert restored.routing_id == original.routing_id
        assert restored.task_description == original.task_description
        assert restored.task_complexity == original.task_complexity
        assert restored.confidence_score == original.confidence_score
        assert restored.metadata == original.metadata
        assert restored.task_dependencies == original.task_dependencies
        assert restored.estimated_cost == original.estimated_cost
        assert restored.actual_cost == original.actual_cost
        assert restored.status == original.status
        assert restored.success == original.success

    def test_default_values(self):
        """Test that optional fields have correct defaults."""
        record = TaskRoutingRecord(
            routing_id="routing-defaults",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Test defaults",
            task_type="testing",
            task_complexity="simple",
            assigned_agent="test-agent",
            assigned_tier="claude-sonnet-4.5",
            routing_strategy="rule_based",
            confidence_score=0.90,
        )

        # Check defaults
        assert record.metadata == {}
        assert record.task_dependencies == []
        assert record.estimated_cost == 0.0
        assert record.status == "pending"
        assert record.started_at is None
        assert record.completed_at is None
        assert record.success is False
        assert record.actual_cost is None
        assert record.error_message is None

    def test_json_serializable(self):
        """Test that record can be serialized to JSON."""
        record = TaskRoutingRecord(
            routing_id="routing-json",
            timestamp="2026-01-09T10:00:00Z",
            task_description="JSON test",
            task_type="testing",
            task_complexity="simple",
            assigned_agent="test-agent",
            assigned_tier="claude-sonnet-4.5",
            routing_strategy="rule_based",
            confidence_score=0.95,
        )

        json_str = json.dumps(record.to_dict())
        assert isinstance(json_str, str)

        # Can deserialize back
        data = json.loads(json_str)
        restored = TaskRoutingRecord.from_dict(data)
        assert restored.routing_id == record.routing_id


class TestTestExecutionRecord:
    """Test suite for TestExecutionRecord."""

    def test_create_minimal_record(self):
        """Test creating record with minimal required fields."""
        record = TestExecutionRecord(
            execution_id="test-123",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="unit",
            triggered_by="manual",
            command="pytest tests/unit/",
            working_directory="/path/to/project",
            duration_seconds=45.2,
            total_tests=100,
            passed=95,
            failed=3,
            skipped=2,
            errors=0,
            success=False,
            exit_code=1,
        )

        assert record.execution_id == "test-123"
        assert record.test_suite == "unit"
        assert record.total_tests == 100
        assert record.passed == 95
        assert record.failed == 3
        assert record.success is False

    def test_create_full_record(self):
        """Test creating record with all fields populated."""
        record = TestExecutionRecord(
            execution_id="test-456",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="integration",
            test_files=["tests/integration/test_api.py", "tests/integration/test_db.py"],
            triggered_by="workflow",
            command="pytest tests/integration/ -v",
            working_directory="/path/to/project",
            duration_seconds=120.5,
            total_tests=50,
            passed=48,
            failed=2,
            skipped=0,
            errors=0,
            success=False,
            exit_code=1,
            failed_tests=[
                {"name": "test_api_timeout", "file": "test_api.py", "error": "Timeout"},
                {"name": "test_db_connection", "file": "test_db.py", "error": "Connection refused"},
            ],
            coverage_percentage=85.5,
            workflow_id="workflow-123",
        )

        assert record.test_files == [
            "tests/integration/test_api.py",
            "tests/integration/test_db.py",
        ]
        assert record.duration_seconds == 120.5
        assert len(record.failed_tests) == 2
        assert record.coverage_percentage == 85.5
        assert record.workflow_id == "workflow-123"

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        record = TestExecutionRecord(
            execution_id="test-789",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="e2e",
            triggered_by="ci",
            command="pytest tests/e2e/",
            working_directory="/path/to/project",
            duration_seconds=300.0,
            total_tests=25,
            passed=25,
            failed=0,
            skipped=0,
            errors=0,
            success=True,
            exit_code=0,
        )

        data = record.to_dict()

        assert isinstance(data, dict)
        assert data["execution_id"] == "test-789"
        assert data["test_suite"] == "e2e"
        assert data["success"] is True
        assert data["exit_code"] == 0

    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data = {
            "execution_id": "test-def",
            "timestamp": "2026-01-09T10:00:00Z",
            "test_suite": "unit",
            "test_files": [],
            "triggered_by": "pre_commit",
            "command": "pytest",
            "working_directory": "/project",
            "duration_seconds": 10.5,
            "total_tests": 10,
            "passed": 10,
            "failed": 0,
            "skipped": 0,
            "errors": 0,
            "success": True,
            "exit_code": 0,
            "failed_tests": [],
            "coverage_percentage": None,
            "workflow_id": None,
        }

        record = TestExecutionRecord.from_dict(data)

        assert record.execution_id == "test-def"
        assert record.triggered_by == "pre_commit"
        assert record.success is True

    def test_default_values(self):
        """Test that optional fields have correct defaults."""
        record = TestExecutionRecord(
            execution_id="test-defaults",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="unit",
            triggered_by="manual",
            command="pytest",
            working_directory="/project",
            duration_seconds=5.0,
            total_tests=5,
            passed=5,
            failed=0,
            skipped=0,
            errors=0,
            success=True,
            exit_code=0,
        )

        assert record.test_files == []
        assert record.failed_tests == []
        assert record.coverage_percentage is None
        assert record.workflow_id is None


class TestCoverageRecord:
    """Test suite for CoverageRecord."""

    def test_create_minimal_record(self):
        """Test creating record with minimal required fields."""
        record = CoverageRecord(
            record_id="cov-123",
            timestamp="2026-01-09T10:00:00Z",
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

        assert record.record_id == "cov-123"
        assert record.overall_percentage == 85.5
        assert record.lines_total == 1000
        assert record.lines_covered == 855
        assert record.trend == "stable"

    def test_create_full_record(self):
        """Test creating record with all fields populated."""
        record = CoverageRecord(
            record_id="cov-456",
            timestamp="2026-01-09T10:00:00Z",
            overall_percentage=90.2,
            lines_total=2000,
            lines_covered=1804,
            branches_total=400,
            branches_covered=350,
            files_total=100,
            files_well_covered=80,
            files_critical=3,
            untested_files=["src/unused.py", "src/deprecated.py"],
            critical_gaps=[
                {"file": "src/auth.py", "coverage": 45.0, "priority": "high"},
                {"file": "src/payment.py", "coverage": 38.5, "priority": "high"},
            ],
            previous_percentage=88.5,
            trend="improving",
            coverage_format="xml",
            coverage_file="coverage.xml",
            workflow_id="workflow-789",
        )

        assert record.overall_percentage == 90.2
        assert record.previous_percentage == 88.5
        assert record.trend == "improving"
        assert len(record.untested_files) == 2
        assert len(record.critical_gaps) == 2
        assert record.workflow_id == "workflow-789"

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        record = CoverageRecord(
            record_id="cov-789",
            timestamp="2026-01-09T10:00:00Z",
            overall_percentage=75.0,
            lines_total=500,
            lines_covered=375,
            branches_total=100,
            branches_covered=75,
            files_total=25,
            files_well_covered=15,
            files_critical=7,
            trend="declining",
            coverage_format="xml",
            coverage_file="coverage.xml",
        )

        data = record.to_dict()

        assert isinstance(data, dict)
        assert data["record_id"] == "cov-789"
        assert data["overall_percentage"] == 75.0
        assert data["trend"] == "declining"

    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data = {
            "record_id": "cov-abc",
            "timestamp": "2026-01-09T10:00:00Z",
            "overall_percentage": 92.5,
            "lines_total": 3000,
            "lines_covered": 2775,
            "branches_total": 600,
            "branches_covered": 550,
            "files_total": 150,
            "files_well_covered": 140,
            "files_critical": 2,
            "untested_files": [],
            "critical_gaps": [],
            "previous_percentage": None,
            "trend": "stable",
            "coverage_format": "xml",
            "coverage_file": "coverage.xml",
            "workflow_id": None,
        }

        record = CoverageRecord.from_dict(data)

        assert record.record_id == "cov-abc"
        assert record.overall_percentage == 92.5
        assert record.trend == "stable"

    def test_default_values(self):
        """Test that optional fields have correct defaults."""
        record = CoverageRecord(
            record_id="cov-defaults",
            timestamp="2026-01-09T10:00:00Z",
            overall_percentage=80.0,
            lines_total=1000,
            lines_covered=800,
            branches_total=200,
            branches_covered=160,
            files_total=50,
            files_well_covered=40,
            files_critical=5,
            trend="stable",
            coverage_format="xml",
            coverage_file="coverage.xml",
        )

        assert record.untested_files == []
        assert record.critical_gaps == []
        assert record.previous_percentage is None
        assert record.workflow_id is None


class TestAgentAssignmentRecord:
    """Test suite for AgentAssignmentRecord."""

    def test_create_minimal_record(self):
        """Test creating record with minimal required fields."""
        record = AgentAssignmentRecord(
            assignment_id="assign-123",
            timestamp="2026-01-09T10:00:00Z",
            task_id="task-456",
            task_title="Fix bug in authentication",
            task_description="User cannot login with valid credentials",
            assigned_agent="bug-fix-agent",
            assignment_reason="Rule-based: simple bug fix",
            automated_eligible=True,
            task_spec_clarity=0.95,
            has_dependencies=False,
        )

        assert record.assignment_id == "assign-123"
        assert record.task_id == "task-456"
        assert record.assigned_agent == "bug-fix-agent"
        assert record.automated_eligible is True
        assert record.task_spec_clarity == 0.95

    def test_create_full_record(self):
        """Test creating record with all fields populated."""
        record = AgentAssignmentRecord(
            assignment_id="assign-789",
            timestamp="2026-01-09T10:00:00Z",
            task_id="task-101",
            task_title="Implement new feature",
            task_description="Add dark mode support to UI",
            assigned_agent="feature-agent",
            assignment_reason="ML prediction: feature development",
            automated_eligible=False,
            task_spec_clarity=0.65,
            has_dependencies=True,
            metadata={"priority": "medium", "sprint": "2026-Q1"},
            status="completed",
            started_at="2026-01-09T10:00:00Z",
            completed_at="2026-01-09T12:30:00Z",
            actual_duration_hours=2.5,
            success=True,
            quality_check_passed=True,
            human_review_required=True,
            workflow_id="workflow-555",
        )

        assert record.automated_eligible is False
        assert record.has_dependencies is True
        assert record.status == "completed"
        assert record.success is True
        assert record.quality_check_passed is True
        assert record.human_review_required is True

    def test_to_dict_serialization(self):
        """Test serialization to dictionary."""
        record = AgentAssignmentRecord(
            assignment_id="assign-xyz",
            timestamp="2026-01-09T10:00:00Z",
            task_id="task-202",
            task_title="Refactor module",
            task_description="Improve code quality",
            assigned_agent="refactor-agent",
            assignment_reason="Manual override",
            automated_eligible=True,
            task_spec_clarity=0.88,
            has_dependencies=False,
        )

        data = record.to_dict()

        assert isinstance(data, dict)
        assert data["assignment_id"] == "assign-xyz"
        assert data["task_id"] == "task-202"
        assert data["assigned_agent"] == "refactor-agent"

    def test_from_dict_deserialization(self):
        """Test deserialization from dictionary."""
        data = {
            "assignment_id": "assign-def",
            "timestamp": "2026-01-09T10:00:00Z",
            "task_id": "task-303",
            "task_title": "Write tests",
            "task_description": "Add unit tests for new module",
            "assigned_agent": "test-agent",
            "assignment_reason": "Automated routing",
            "automated_eligible": True,
            "task_spec_clarity": 0.98,
            "has_dependencies": False,
            "metadata": {},
            "status": "assigned",
            "started_at": None,
            "completed_at": None,
            "success": False,
            "actual_duration_hours": None,
            "quality_check_passed": False,
            "human_review_required": False,
            "workflow_id": None,
        }

        record = AgentAssignmentRecord.from_dict(data)

        assert record.assignment_id == "assign-def"
        assert record.task_title == "Write tests"
        assert record.automated_eligible is True

    def test_default_values(self):
        """Test that optional fields have correct defaults."""
        record = AgentAssignmentRecord(
            assignment_id="assign-defaults",
            timestamp="2026-01-09T10:00:00Z",
            task_id="task-404",
            task_title="Test defaults",
            task_description="Testing default values",
            assigned_agent="test-agent",
        )

        assert record.metadata == {}
        assert record.status == "assigned"
        assert record.started_at is None
        assert record.completed_at is None
        assert record.success is False
        assert record.actual_duration_hours is None
        assert record.quality_check_passed is False
        assert record.human_review_required is False
        assert record.workflow_id is None


class TestEdgeCases:
    """Test edge cases across all record types."""

    def test_empty_lists(self):
        """Test that empty lists are handled correctly."""
        record = TestExecutionRecord(
            execution_id="test-empty",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="unit",
            test_files=[],
            triggered_by="manual",
            command="pytest",
            working_directory="/project",
            duration_seconds=0.1,
            total_tests=0,
            passed=0,
            failed=0,
            skipped=0,
            errors=0,
            success=True,
            exit_code=0,
            failed_tests=[],
        )

        assert record.test_files == []
        assert record.failed_tests == []

    def test_empty_dicts(self):
        """Test that empty dicts are handled correctly."""
        record = TaskRoutingRecord(
            routing_id="routing-empty",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Test",
            task_type="test",
            task_complexity="simple",
            assigned_agent="agent",
            assigned_tier="tier",
            routing_strategy="rule",
            confidence_score=1.0,
            metadata={},
        )

        assert record.metadata == {}

    def test_large_values(self):
        """Test handling of large numerical values."""
        record = TestExecutionRecord(
            execution_id="test-large",
            timestamp="2026-01-09T10:00:00Z",
            test_suite="all",
            triggered_by="ci",
            command="pytest",
            working_directory="/project",
            duration_seconds=3600.0,
            total_tests=10000,
            passed=9500,
            failed=500,
            skipped=0,
            errors=0,
            success=False,
            exit_code=1,
        )

        assert record.total_tests == 10000
        assert record.duration_seconds == 3600.0

    def test_unicode_strings(self):
        """Test handling of unicode strings."""
        record = TaskRoutingRecord(
            routing_id="routing-unicode",
            timestamp="2026-01-09T10:00:00Z",
            task_description="Fix bug with emoji 🐛 and unicode ñ café",
            task_type="bug_fix",
            task_complexity="simple",
            assigned_agent="bug-agent",
            assigned_tier="tier",
            routing_strategy="rule",
            confidence_score=0.95,
        )

        assert "🐛" in record.task_description
        assert "café" in record.task_description

        # Ensure serialization works
        data = record.to_dict()
        assert "🐛" in data["task_description"]
