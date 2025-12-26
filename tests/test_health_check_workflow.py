"""
Tests for HealthCheckWorkflow.

Tests the workflow wrapper for project health diagnosis and fixing.
"""

import json
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.health_check import HealthCheckResult, HealthCheckWorkflow


class TestHealthCheckResult:
    """Tests for HealthCheckResult dataclass."""

    def test_create_result(self):
        """Test creating a HealthCheckResult."""
        result = HealthCheckResult(
            success=True,
            health_score=85.0,
            is_healthy=True,
            issues=[],
            fixes=[],
            checks_run={"lint": {"passed": True}},
            agents_used=["lint_fixer"],
            critical_count=0,
            high_count=0,
            applied_fixes_count=0,
            duration_seconds=1.5,
            cost=0.01,
        )

        assert result.success is True
        assert result.health_score == 85.0
        assert result.is_healthy is True
        assert result.issues == []
        assert result.fixes == []
        assert result.critical_count == 0
        assert result.duration_seconds == 1.5
        assert result.metadata == {}

    def test_result_with_issues(self):
        """Test result with issues."""
        issues = [
            {"title": "Lint error", "category": "lint", "severity": "medium"},
            {"title": "Type error", "category": "types", "severity": "high"},
            {"title": "Critical bug", "category": "tests", "severity": "critical"},
        ]

        result = HealthCheckResult(
            success=True,
            health_score=60.0,
            is_healthy=False,
            issues=issues,
            fixes=[],
            checks_run={},
            agents_used=[],
            critical_count=1,
            high_count=1,
            applied_fixes_count=0,
            duration_seconds=2.0,
            cost=0.02,
        )

        assert len(result.issues) == 3
        assert result.critical_count == 1
        assert result.high_count == 1
        assert result.is_healthy is False

    def test_result_with_metadata(self):
        """Test result with custom metadata."""
        result = HealthCheckResult(
            success=True,
            health_score=100.0,
            is_healthy=True,
            issues=[],
            fixes=[],
            checks_run={},
            agents_used=[],
            critical_count=0,
            high_count=0,
            applied_fixes_count=0,
            duration_seconds=0.5,
            cost=0.0,
            metadata={"crew_available": True, "auto_fix": False},
        )

        assert result.metadata["crew_available"] is True
        assert result.metadata["auto_fix"] is False


class TestHealthCheckWorkflowInit:
    """Tests for HealthCheckWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = HealthCheckWorkflow()

        assert workflow.auto_fix is False
        assert workflow.check_lint is True
        assert workflow.check_types is True
        assert workflow.check_tests is True
        assert workflow.check_deps is True
        assert workflow.xml_prompts is True
        assert workflow.name == "health-check"

    def test_custom_init(self):
        """Test custom initialization."""
        workflow = HealthCheckWorkflow(
            auto_fix=True,
            check_lint=False,
            check_types=True,
            check_tests=False,
            check_deps=False,
            xml_prompts=False,
        )

        assert workflow.auto_fix is True
        assert workflow.check_lint is False
        assert workflow.check_types is True
        assert workflow.check_tests is False
        assert workflow.check_deps is False
        assert workflow.xml_prompts is False

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = HealthCheckWorkflow()

        from src.empathy_os.workflows.base import ModelTier

        assert workflow.tier_map["diagnose"] == ModelTier.CAPABLE
        assert workflow.tier_map["fix"] == ModelTier.CAPABLE

    def test_stages(self):
        """Test workflow stages."""
        workflow = HealthCheckWorkflow()

        assert workflow.stages == ["diagnose", "fix"]


class TestBasicHealthCheck:
    """Tests for basic health check (fallback mode)."""

    @pytest.mark.asyncio
    async def test_basic_health_check_all_pass(self):
        """Test basic health check when all checks pass."""
        workflow = HealthCheckWorkflow()

        with patch("subprocess.run") as mock_run:
            # All checks pass
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            result = await workflow._basic_health_check(".")

        assert result["health_score"] == 100.0
        assert result["is_healthy"] is True
        assert len(result["issues"]) == 0
        assert "lint" in result["checks_run"]

    @pytest.mark.asyncio
    async def test_basic_health_check_lint_errors(self):
        """Test basic health check with lint errors."""
        workflow = HealthCheckWorkflow(check_types=False, check_tests=False)

        with patch("subprocess.run") as mock_run:
            # Lint fails with 5 errors
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="file.py:1:1: E001\nfile.py:2:1: E002\nfile.py:3:1: E003\nfile.py:4:1: E004\nfile.py:5:1: E005\n",
                stderr="",
            )

            result = await workflow._basic_health_check(".")

        assert result["health_score"] < 100
        assert len(result["issues"]) == 1
        assert result["issues"][0]["category"] == "lint"
        assert result["checks_run"]["lint"]["passed"] is False

    @pytest.mark.asyncio
    async def test_basic_health_check_type_errors(self):
        """Test basic health check with type errors."""
        workflow = HealthCheckWorkflow(check_lint=False, check_tests=False)

        with patch("subprocess.run") as mock_run:
            # Type check fails
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="error: Type mismatch\nerror: Missing return",
                stderr="",
            )

            result = await workflow._basic_health_check(".")

        assert result["health_score"] < 100
        assert len(result["issues"]) == 1
        assert result["issues"][0]["category"] == "types"

    @pytest.mark.asyncio
    async def test_basic_health_check_test_failures(self):
        """Test basic health check with test failures."""
        workflow = HealthCheckWorkflow(check_lint=False, check_types=False)

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="FAILED",
                stderr="",
            )

            result = await workflow._basic_health_check(".")

        assert result["health_score"] <= 75  # -25 for test failures
        assert len(result["issues"]) == 1
        assert result["issues"][0]["category"] == "tests"
        assert result["issues"][0]["severity"] == "high"

    @pytest.mark.asyncio
    async def test_basic_health_check_skipped_on_exception(self):
        """Test that checks are skipped gracefully on exception."""
        workflow = HealthCheckWorkflow()

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Command failed")

            result = await workflow._basic_health_check(".")

        # Should complete with skipped checks
        assert result["health_score"] == 100.0
        assert "lint" in result["checks_run"]
        assert result["checks_run"]["lint"].get("skipped") is True


class TestHealthCheckWorkflowStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_diagnose(self):
        """Test diagnose stage routing."""
        workflow = HealthCheckWorkflow()

        with patch.object(workflow, "_diagnose", new_callable=AsyncMock) as mock_diagnose:
            mock_diagnose.return_value = ({"diagnosis": {}}, 100, 50)

            from src.empathy_os.workflows.base import ModelTier

            result = await workflow.run_stage("diagnose", ModelTier.CAPABLE, {"path": "."})

            mock_diagnose.assert_called_once()
            assert result == ({"diagnosis": {}}, 100, 50)

    @pytest.mark.asyncio
    async def test_run_stage_fix(self):
        """Test fix stage routing."""
        workflow = HealthCheckWorkflow()

        with patch.object(workflow, "_fix", new_callable=AsyncMock) as mock_fix:
            mock_fix.return_value = ({"fixes": []}, 50, 25)

            from src.empathy_os.workflows.base import ModelTier

            await workflow.run_stage("fix", ModelTier.CAPABLE, {"path": "."})

            mock_fix.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = HealthCheckWorkflow()

        from src.empathy_os.workflows.base import ModelTier

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CAPABLE, {})


class TestHealthCheckFix:
    """Tests for fix stage."""

    @pytest.mark.asyncio
    async def test_fix_disabled(self):
        """Test fix stage when auto_fix is disabled."""
        workflow = HealthCheckWorkflow(auto_fix=False)

        from src.empathy_os.workflows.base import ModelTier

        result, input_tokens, output_tokens = await workflow._fix({"path": "."}, ModelTier.CAPABLE)

        assert result["auto_fix_enabled"] is False
        assert result["fixes"] == []
        assert input_tokens == 0

    @pytest.mark.asyncio
    async def test_fix_enabled_basic(self):
        """Test fix stage with basic auto-fix."""
        workflow = HealthCheckWorkflow(auto_fix=True, check_lint=True)
        workflow._crew_available = False

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="Fixed 3 issues",
                stderr="",
            )

            from src.empathy_os.workflows.base import ModelTier

            result, _, _ = await workflow._fix({"path": "."}, ModelTier.CAPABLE)

        assert result["auto_fix_enabled"] is True
        assert len(result["fixes"]) == 1
        assert result["fixes"][0]["category"] == "lint"


class TestSaveHealthData:
    """Tests for saving health data."""

    def test_save_health_data(self):
        """Test saving health data to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = HealthCheckWorkflow()

            result = HealthCheckResult(
                success=True,
                health_score=90.0,
                is_healthy=True,
                issues=[
                    {"category": "lint", "severity": "medium"},
                    {"category": "types", "severity": "high"},
                ],
                fixes=[],
                checks_run={"tests": {"passed": True, "total": 100, "coverage": 80}},
                agents_used=[],
                critical_count=0,
                high_count=1,
                applied_fixes_count=0,
                duration_seconds=1.0,
                cost=0.01,
            )

            workflow._save_health_data(result, tmpdir)

            health_file = os.path.join(tmpdir, ".empathy", "health.json")
            assert os.path.exists(health_file)

            with open(health_file) as f:
                data = json.load(f)

            assert data["score"] == 90.0
            assert data["lint"]["errors"] == 1
            assert data["types"]["errors"] == 1
            assert "timestamp" in data

    def test_save_health_data_creates_dir(self):
        """Test that .empathy dir is created if missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = HealthCheckWorkflow()

            result = HealthCheckResult(
                success=True,
                health_score=100.0,
                is_healthy=True,
                issues=[],
                fixes=[],
                checks_run={},
                agents_used=[],
                critical_count=0,
                high_count=0,
                applied_fixes_count=0,
                duration_seconds=0.5,
                cost=0.0,
            )

            # .empathy doesn't exist yet
            empathy_dir = os.path.join(tmpdir, ".empathy")
            assert not os.path.exists(empathy_dir)

            workflow._save_health_data(result, tmpdir)

            assert os.path.exists(empathy_dir)
            assert os.path.exists(os.path.join(empathy_dir, "health.json"))


class TestHealthCheckWorkflowIntegration:
    """Integration tests for HealthCheckWorkflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_fallback_mode(self):
        """Test full workflow execution in fallback mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = HealthCheckWorkflow(
                check_lint=True,
                check_types=False,
                check_tests=False,
                check_deps=False,
            )

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

                # Mock the base workflow execute
                with patch.object(
                    workflow.__class__.__bases__[0],
                    "execute",
                    new_callable=AsyncMock,
                ) as mock_execute:
                    # Create a mock result object
                    mock_result = MagicMock()
                    mock_result.success = True
                    mock_result.final_output = {
                        "diagnosis": {
                            "health_score": 100.0,
                            "is_healthy": True,
                            "issues": [],
                            "checks_run": {"lint": {"passed": True}},
                            "agents_used": [],
                            "crew_available": False,
                        },
                        "fixes": [],
                    }
                    mock_result.cost_report = MagicMock(total_cost=0.01)
                    mock_execute.return_value = mock_result

                    result = await workflow.execute(path=tmpdir)

                    assert isinstance(result, HealthCheckResult)
                    assert result.success is True
                    assert result.health_score == 100.0
                    assert result.is_healthy is True
