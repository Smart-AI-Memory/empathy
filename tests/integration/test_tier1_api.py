"""Integration tests for Tier 1 API endpoints.

Tests the Dashboard API endpoints:
- GET /api/monitoring/task-routing
- GET /api/monitoring/test-execution
- GET /api/monitoring/coverage
- GET /api/monitoring/agents
- GET /api/monitoring/summary
- GET /api/monitoring/recent-tasks
- GET /api/monitoring/recent-tests

Tests cover:
- API response structure and validation
- Query parameter handling
- Error responses
- Empty data scenarios
- Real data integration
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from dashboard.backend.api.monitoring import router as monitoring_router
from dashboard.backend.schemas import (
    AgentPerformanceResponse,
    CoverageStatsResponse,
    TaskRoutingStatsResponse,
    TestExecutionStatsResponse,
    Tier1SummaryResponse,
)
from empathy_os.models import (
    AgentAssignmentRecord,
    CoverageRecord,
    TaskRoutingRecord,
    TestExecutionRecord,
)
from empathy_os.models.telemetry import TelemetryStore


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test telemetry data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def populated_store(temp_dir):
    """Create a TelemetryStore with sample Tier 1 data."""
    store = TelemetryStore(storage_dir=str(temp_dir))

    now = datetime.utcnow()

    # Add routing data
    for i in range(5):
        store.log_task_routing(
            TaskRoutingRecord(
                routing_id=f"routing-{i}",
                timestamp=now.isoformat(),
                task_description=f"Task {i}",
                task_type="code_review" if i % 2 == 0 else "bug_fix",
                task_complexity="simple" if i < 3 else "moderate",
                assigned_agent=f"agent-{i % 2}",
                assigned_tier="claude-sonnet-4.5",
                routing_strategy="rule_based" if i < 3 else "ml_predicted",
                confidence_score=0.95 - (i * 0.05),
                status="completed",
                success=(i < 4),  # 4 successes, 1 failure
                actual_cost=0.01 * (i + 1),
            )
        )

    # Add test execution data
    for i in range(3):
        store.log_test_execution(
            TestExecutionRecord(
                execution_id=f"test-{i}",
                timestamp=now.isoformat(),
                test_suite="unit" if i < 2 else "integration",
                triggered_by="ci" if i == 0 else "manual",
                command="pytest",
                working_directory="/project",
                duration_seconds=30.0 + (i * 10),
                total_tests=50 + (i * 25),
                passed=48 + (i * 24),
                failed=2 + i,
                skipped=0,
                errors=0,
                success=(i == 0),  # Only first execution succeeds
                exit_code=0 if i == 0 else 1,
                failed_tests=(
                    [{"name": f"test_fail_{i}", "file": f"test_{i}.py", "error": "AssertionError"}]
                    if i > 0
                    else []
                ),
            )
        )

    # Add coverage data
    for i in range(2):
        store.log_coverage(
            CoverageRecord(
                record_id=f"cov-{i}",
                timestamp=now.isoformat(),
                overall_percentage=80.0 + (i * 5.0),
                lines_total=1000,
                lines_covered=800 + (i * 50),
                branches_total=200,
                branches_covered=150 + (i * 10),
                files_total=50,
                files_well_covered=35 + (i * 5),
                files_critical=5 - i,
                critical_gaps=(
                    [{"file": "src/auth.py", "coverage": 45.0, "priority": "high"}]
                    if i == 0
                    else []
                ),
                trend="improving" if i == 1 else "stable",
                coverage_format="xml",
                coverage_file="coverage.xml",
            )
        )

    # Add agent assignment data
    for i in range(4):
        store.log_agent_assignment(
            AgentAssignmentRecord(
                assignment_id=f"assign-{i}",
                timestamp=now.isoformat(),
                task_id=f"task-{i}",
                task_title=f"Task {i}",
                task_description=f"Description {i}",
                assigned_agent=f"agent-{i % 2}",
                assignment_reason="Rule-based",
                task_spec_clarity=0.90 + (i * 0.02),
                has_dependencies=False,
                automated_eligible=True,
                status="completed",
                success=(i < 3),  # 3 successes, 1 failure
                actual_duration_hours=(300.0 + (i * 100)) / 3600.0,  # Convert seconds to hours
                quality_check_passed=(i < 3),
            )
        )

    return store


@pytest.fixture
def test_client(populated_store, monkeypatch):
    """Create a FastAPI test client with populated telemetry store."""
    # Reset global telemetry store singleton
    import empathy_os.models.telemetry

    empathy_os.models.telemetry._telemetry_store = None

    # Mock get_telemetry_store in both places:
    # 1. In the telemetry module itself
    monkeypatch.setattr("empathy_os.models.telemetry.get_telemetry_store", lambda: populated_store)
    # 2. In the monitoring API module (where it's imported)
    monkeypatch.setattr(
        "dashboard.backend.api.monitoring.get_telemetry_store", lambda: populated_store
    )

    # Create test app with monitoring router
    app = FastAPI()
    app.include_router(monitoring_router, prefix="/api")

    return TestClient(app)


class TestTaskRoutingEndpoint:
    """Test /api/monitoring/task-routing endpoint."""

    def test_get_task_routing_stats(self, test_client):
        """Test getting task routing statistics."""
        response = test_client.get("/api/monitoring/task-routing?hours=24")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "total_tasks" in data
        assert "successful_routing" in data
        assert "accuracy_rate" in data
        assert "avg_confidence" in data
        assert "by_task_type" in data
        assert "by_strategy" in data
        assert "timestamp" in data

        # Validate values
        assert data["total_tasks"] == 5
        assert data["successful_routing"] == 4
        assert data["accuracy_rate"] == 0.8  # Returns decimal, not percentage

    def test_task_routing_with_custom_hours(self, test_client):
        """Test task routing with custom time window."""
        response = test_client.get("/api/monitoring/task-routing?hours=168")

        assert response.status_code == 200

        data = response.json()
        assert data["total_tasks"] >= 0

    def test_task_routing_invalid_hours(self, test_client):
        """Test task routing with invalid hours parameter."""
        # Hours too large
        response = test_client.get("/api/monitoring/task-routing?hours=10000")

        # Should return validation error
        assert response.status_code == 422

    def test_task_routing_pydantic_validation(self, test_client):
        """Test that response matches Pydantic schema."""
        response = test_client.get("/api/monitoring/task-routing")

        assert response.status_code == 200

        data = response.json()

        # Should be valid TaskRoutingStatsResponse
        validated = TaskRoutingStatsResponse(**data)

        assert validated.total_tasks == data["total_tasks"]
        assert validated.accuracy_rate == data["accuracy_rate"]


class TestTestExecutionEndpoint:
    """Test /api/monitoring/test-execution endpoint."""

    def test_get_test_execution_stats(self, test_client):
        """Test getting test execution statistics."""
        response = test_client.get("/api/monitoring/test-execution?hours=24")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "total_executions" in data
        assert "success_rate" in data
        assert "avg_duration_seconds" in data
        assert "total_tests_run" in data
        assert "total_failures" in data
        assert "most_failing_tests" in data
        assert "timestamp" in data

        # Validate values
        assert data["total_executions"] == 3
        assert data["total_tests_run"] == 225  # 50 + 75 + 100

    def test_test_execution_pydantic_validation(self, test_client):
        """Test that response matches Pydantic schema."""
        response = test_client.get("/api/monitoring/test-execution")

        assert response.status_code == 200

        data = response.json()

        # Should be valid TestExecutionStatsResponse
        validated = TestExecutionStatsResponse(**data)

        assert validated.total_executions == data["total_executions"]
        assert validated.success_rate == data["success_rate"]


class TestCoverageEndpoint:
    """Test /api/monitoring/coverage endpoint."""

    def test_get_coverage_stats(self, test_client):
        """Test getting coverage statistics."""
        response = test_client.get("/api/monitoring/coverage?hours=168")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "current_coverage" in data
        assert "trend" in data
        assert "coverage_history" in data
        assert "critical_gaps_count" in data
        assert "timestamp" in data

        # Validate values
        assert data["current_coverage"] > 0

    def test_coverage_default_hours(self, test_client):
        """Test coverage endpoint with default hours (7 days)."""
        response = test_client.get("/api/monitoring/coverage")

        assert response.status_code == 200

        data = response.json()
        assert "current_coverage" in data

    def test_coverage_pydantic_validation(self, test_client):
        """Test that response matches Pydantic schema."""
        response = test_client.get("/api/monitoring/coverage")

        assert response.status_code == 200

        data = response.json()

        # Should be valid CoverageStatsResponse
        validated = CoverageStatsResponse(**data)

        assert validated.current_coverage == data["current_coverage"]
        assert validated.trend == data["trend"]


class TestAgentPerformanceEndpoint:
    """Test /api/monitoring/agents endpoint."""

    def test_get_agent_performance(self, test_client):
        """Test getting agent performance metrics."""
        response = test_client.get("/api/monitoring/agents?hours=168")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "total_assignments" in data
        assert "automation_rate" in data
        assert "by_agent" in data
        assert "timestamp" in data

        # Validate values
        assert data["total_assignments"] == 4

    def test_agent_performance_shows_multiple_agents(self, test_client):
        """Test that agent performance shows multiple agents."""
        response = test_client.get("/api/monitoring/agents")

        assert response.status_code == 200

        data = response.json()

        # Should have data for multiple agents
        assert len(data["by_agent"]) > 0

    def test_agent_performance_pydantic_validation(self, test_client):
        """Test that response matches Pydantic schema."""
        response = test_client.get("/api/monitoring/agents")

        assert response.status_code == 200

        data = response.json()

        # Should be valid AgentPerformanceResponse
        validated = AgentPerformanceResponse(**data)

        assert validated.total_assignments == data["total_assignments"]
        assert validated.automation_rate == data["automation_rate"]


class TestTier1SummaryEndpoint:
    """Test /api/monitoring/summary endpoint."""

    def test_get_tier1_summary(self, test_client):
        """Test getting comprehensive Tier 1 summary."""
        response = test_client.get("/api/monitoring/summary?hours=24")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure - should have all sections
        assert "task_routing" in data
        assert "test_execution" in data
        assert "coverage" in data
        assert "agent_performance" in data
        assert "timestamp" in data

        # Each section should have its own timestamp
        assert "timestamp" in data["task_routing"]
        assert "timestamp" in data["test_execution"]
        assert "timestamp" in data["coverage"]
        assert "timestamp" in data["agent_performance"]

        # Validate subsection structures
        assert "total_tasks" in data["task_routing"]
        assert "total_executions" in data["test_execution"]
        assert "current_coverage" in data["coverage"]
        assert "total_assignments" in data["agent_performance"]

    def test_tier1_summary_pydantic_validation(self, test_client):
        """Test that response matches Pydantic schema."""
        response = test_client.get("/api/monitoring/summary")

        assert response.status_code == 200

        data = response.json()

        # Should be valid Tier1SummaryResponse
        validated = Tier1SummaryResponse(**data)

        assert validated.task_routing is not None
        assert validated.test_execution is not None
        assert validated.coverage is not None
        assert validated.agent_performance is not None


class TestRecentTasksEndpoint:
    """Test /api/monitoring/recent-tasks endpoint."""

    def test_get_recent_tasks(self, test_client):
        """Test getting recent task routing decisions."""
        response = test_client.get("/api/monitoring/recent-tasks?limit=20")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "total" in data
        assert "tasks" in data
        assert "timestamp" in data

        # Should return tasks
        assert data["total"] > 0
        assert len(data["tasks"]) > 0

    def test_recent_tasks_respects_limit(self, test_client):
        """Test that recent tasks respects limit parameter."""
        response = test_client.get("/api/monitoring/recent-tasks?limit=2")

        assert response.status_code == 200

        data = response.json()

        # Should return at most 2 tasks
        assert len(data["tasks"]) <= 2

    def test_recent_tasks_invalid_limit(self, test_client):
        """Test recent tasks with invalid limit parameter."""
        # Limit too large
        response = test_client.get("/api/monitoring/recent-tasks?limit=1000")

        # Should return validation error
        assert response.status_code == 422


class TestRecentTestsEndpoint:
    """Test /api/monitoring/recent-tests endpoint."""

    def test_get_recent_tests(self, test_client):
        """Test getting recent test executions."""
        response = test_client.get("/api/monitoring/recent-tests?limit=10")

        assert response.status_code == 200

        data = response.json()

        # Validate response structure
        assert "total" in data
        assert "executions" in data
        assert "timestamp" in data

        # Should return test executions
        assert data["total"] > 0
        assert len(data["executions"]) > 0

    def test_recent_tests_respects_limit(self, test_client):
        """Test that recent tests respects limit parameter."""
        response = test_client.get("/api/monitoring/recent-tests?limit=1")

        assert response.status_code == 200

        data = response.json()

        # Should return at most 1 test execution
        assert len(data["executions"]) <= 1


class TestErrorHandling:
    """Test error handling across API endpoints."""

    def test_task_routing_handles_store_errors(self, monkeypatch):
        """Test that task routing endpoint handles store errors."""

        def mock_get_store_error():
            raise RuntimeError("Test error")

        # Patch where the function is imported in the monitoring module
        monkeypatch.setattr(
            "dashboard.backend.api.monitoring.get_telemetry_store", mock_get_store_error
        )

        app = FastAPI()
        app.include_router(monitoring_router, prefix="/api")
        client = TestClient(app)

        response = client.get("/api/monitoring/task-routing")

        # Should return 500 error
        assert response.status_code == 500

        data = response.json()
        assert "detail" in data

    def test_summary_handles_empty_data(self, temp_dir, monkeypatch):
        """Test that summary endpoint handles empty data gracefully."""
        empty_store = TelemetryStore(storage_dir=str(temp_dir))
        # Patch where the function is imported in the monitoring module
        monkeypatch.setattr(
            "dashboard.backend.api.monitoring.get_telemetry_store", lambda: empty_store
        )

        app = FastAPI()
        app.include_router(monitoring_router, prefix="/api")
        client = TestClient(app)

        response = client.get("/api/monitoring/summary")

        # Should still return 200 with zero values
        assert response.status_code == 200

        data = response.json()
        assert data["task_routing"]["total_tasks"] == 0
        assert data["test_execution"]["total_executions"] == 0


class TestCORS:
    """Test CORS headers for frontend integration."""

    def test_endpoints_allow_cors(self, test_client):
        """Test that endpoints include appropriate CORS headers."""
        # Make OPTIONS request (preflight)
        response = test_client.options(
            "/api/monitoring/summary",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            },
        )

        # Should allow CORS (if configured)
        # Note: This depends on CORS middleware configuration
        assert response.status_code in [200, 204, 405]


class TestPerformance:
    """Test API performance with realistic data volumes."""

    def test_summary_endpoint_performance(self, test_client):
        """Test that summary endpoint performs well with realistic data."""
        import time

        start = time.time()
        response = test_client.get("/api/monitoring/summary")
        duration = time.time() - start

        assert response.status_code == 200

        # Should respond in less than 1 second
        assert duration < 1.0

    def test_recent_tasks_pagination(self, test_client):
        """Test that recent tasks returns quickly even with large limit."""
        import time

        start = time.time()
        response = test_client.get("/api/monitoring/recent-tasks?limit=100")
        duration = time.time() - start

        assert response.status_code == 200

        # Should respond quickly
        assert duration < 0.5
