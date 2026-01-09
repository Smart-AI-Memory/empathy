"""Tests for health check workflow exception handling.

Verifies that health checks use graceful degradation patterns:
- Specific handlers for timeout, missing tools, subprocess errors
- Broad Exception as fallback with logger.exception()
- Health data save failures never crash health checks

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from empathy_os.workflows.health_check import HealthCheckWorkflow


class TestBasicHealthCheckExceptions:
    """Test exception handling in _basic_health_check() method."""

    @pytest.fixture
    def workflow(self):
        """Create health check workflow instance."""
        return HealthCheckWorkflow(auto_fix=False)

    @pytest.mark.asyncio
    async def test_lint_check_timeout_logs_and_skips(self, workflow, caplog):
        """Lint check timeout should log warning and skip check gracefully."""
        with caplog.at_level(logging.WARNING):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ruff", 60)):
                result = await workflow._basic_health_check(".")

        assert "Lint check timed out" in caplog.text
        assert result["checks_run"]["lint"]["skipped"] is True
        assert result["checks_run"]["lint"]["reason"] == "timeout"
        assert result["health_score"] == 100  # No penalty for skipped checks

    @pytest.mark.asyncio
    async def test_lint_check_missing_tool_logs_and_skips(self, workflow, caplog):
        """Missing ruff should log info and skip check gracefully."""
        with caplog.at_level(logging.INFO):
            with patch("subprocess.run", side_effect=FileNotFoundError("ruff not found")):
                result = await workflow._basic_health_check(".")

        assert "Ruff not installed" in caplog.text
        assert result["checks_run"]["lint"]["skipped"] is True
        assert result["checks_run"]["lint"]["reason"] == "tool_missing"

    @pytest.mark.asyncio
    async def test_lint_check_subprocess_error_logs_and_skips(self, workflow, caplog):
        """Subprocess errors should log error and skip check gracefully."""
        with caplog.at_level(logging.ERROR):
            with patch(
                "subprocess.run",
                side_effect=subprocess.CalledProcessError(1, "ruff"),
            ):
                result = await workflow._basic_health_check(".")

        assert "Lint check subprocess error" in caplog.text
        assert result["checks_run"]["lint"]["skipped"] is True
        assert result["checks_run"]["lint"]["reason"] == "subprocess_error"

    @pytest.mark.asyncio
    async def test_lint_check_unexpected_error_logs_and_skips(self, workflow, caplog):
        """Unexpected errors should log exception and skip check gracefully."""
        with caplog.at_level(logging.ERROR):
            with patch("subprocess.run", side_effect=RuntimeError("Unexpected error")):
                result = await workflow._basic_health_check(".")

        # Check for exception logging (includes traceback)
        assert any("Unexpected error in lint check" in record.message for record in caplog.records)
        assert result["checks_run"]["lint"]["skipped"] is True
        assert result["checks_run"]["lint"]["reason"] == "unexpected_error"

    @pytest.mark.asyncio
    async def test_type_check_timeout_logs_and_skips(self, workflow, caplog):
        """Type check timeout should log warning and skip check gracefully."""
        with caplog.at_level(logging.WARNING):
            with patch("subprocess.run") as mock_run:
                # First call (lint) succeeds, second call (types) times out
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),  # lint success
                    subprocess.TimeoutExpired("mypy", 120),  # types timeout
                ]
                result = await workflow._basic_health_check(".")

        assert "Type check timed out" in caplog.text
        assert result["checks_run"]["types"]["skipped"] is True
        assert result["checks_run"]["types"]["reason"] == "timeout"

    @pytest.mark.asyncio
    async def test_type_check_missing_tool_logs_and_skips(self, workflow, caplog):
        """Missing mypy should log info and skip check gracefully."""
        with caplog.at_level(logging.INFO):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),  # lint success
                    FileNotFoundError("mypy not found"),  # types missing
                ]
                result = await workflow._basic_health_check(".")

        assert "Mypy not installed" in caplog.text
        assert result["checks_run"]["types"]["skipped"] is True
        assert result["checks_run"]["types"]["reason"] == "tool_missing"

    @pytest.mark.asyncio
    async def test_test_check_timeout_logs_and_skips(self, workflow, caplog):
        """Test check timeout should log warning and skip check gracefully."""
        with caplog.at_level(logging.WARNING):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),  # lint success
                    MagicMock(returncode=0, stdout=""),  # types success
                    subprocess.TimeoutExpired("pytest", 180),  # tests timeout
                ]
                result = await workflow._basic_health_check(".")

        assert "Test check timed out" in caplog.text
        assert result["checks_run"]["tests"]["skipped"] is True
        assert result["checks_run"]["tests"]["reason"] == "timeout"

    @pytest.mark.asyncio
    async def test_test_check_missing_tool_logs_and_skips(self, workflow, caplog):
        """Missing pytest should log info and skip check gracefully."""
        with caplog.at_level(logging.INFO):
            with patch("subprocess.run") as mock_run:
                mock_run.side_effect = [
                    MagicMock(returncode=0, stdout=""),  # lint success
                    MagicMock(returncode=0, stdout=""),  # types success
                    FileNotFoundError("pytest not found"),  # tests missing
                ]
                result = await workflow._basic_health_check(".")

        assert "Pytest not installed" in caplog.text
        assert result["checks_run"]["tests"]["skipped"] is True
        assert result["checks_run"]["tests"]["reason"] == "tool_missing"


class TestAutoFixExceptions:
    """Test exception handling in _fix() method."""

    @pytest.fixture
    def workflow(self):
        """Create health check workflow with auto-fix enabled."""
        return HealthCheckWorkflow(auto_fix=True)

    @pytest.mark.asyncio
    async def test_ruff_autofix_timeout_logs_warning(self, workflow, caplog):
        """Ruff auto-fix timeout should log warning and continue."""
        workflow._crew_available = False  # Force fallback to basic auto-fix

        with caplog.at_level(logging.WARNING):
            with patch("subprocess.run", side_effect=subprocess.TimeoutExpired("ruff", 60)):
                result, _, _ = await workflow._fix({"path": "."}, workflow.tier_map["fix"])

        assert "Ruff auto-fix timed out" in caplog.text
        assert result["fixes"] == []  # No fixes applied
        assert result["auto_fix_enabled"] is True

    @pytest.mark.asyncio
    async def test_ruff_autofix_missing_tool_logs_info(self, workflow, caplog):
        """Missing ruff should log info and continue."""
        workflow._crew_available = False

        with caplog.at_level(logging.INFO):
            with patch("subprocess.run", side_effect=FileNotFoundError("ruff not found")):
                result, _, _ = await workflow._fix({"path": "."}, workflow.tier_map["fix"])

        assert "Ruff not installed" in caplog.text
        assert result["fixes"] == []

    @pytest.mark.asyncio
    async def test_ruff_autofix_subprocess_error_logs_error(self, workflow, caplog):
        """Subprocess errors should log error and continue."""
        workflow._crew_available = False

        with caplog.at_level(logging.ERROR):
            with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "ruff")):
                result, _, _ = await workflow._fix({"path": "."}, workflow.tier_map["fix"])

        assert "Ruff auto-fix subprocess error" in caplog.text
        assert result["fixes"] == []

    @pytest.mark.asyncio
    async def test_ruff_autofix_unexpected_error_logs_exception(self, workflow, caplog):
        """Unexpected errors should log exception and continue."""
        workflow._crew_available = False

        with caplog.at_level(logging.ERROR):
            with patch("subprocess.run", side_effect=RuntimeError("Unexpected error")):
                result, _, _ = await workflow._fix({"path": "."}, workflow.tier_map["fix"])

        assert any(
            "Unexpected error in ruff auto-fix" in record.message for record in caplog.records
        )
        assert result["fixes"] == []


class TestSaveHealthDataExceptions:
    """Test exception handling in _save_health_data() method."""

    @pytest.fixture
    def workflow(self):
        """Create health check workflow instance."""
        return HealthCheckWorkflow()

    @pytest.fixture
    def health_result(self):
        """Create mock health result."""
        from empathy_os.workflows.health_check import HealthCheckResult

        return HealthCheckResult(
            success=True,
            health_score=85.0,
            is_healthy=True,
            issues=[],
            fixes=[],
            checks_run={"lint": {"passed": True}},
            agents_used=[],
            critical_count=0,
            high_count=0,
            applied_fixes_count=0,
            duration_seconds=1.5,
            cost=0.01,
        )

    def test_save_health_data_file_system_error_logs_warning(
        self, workflow, health_result, caplog, tmp_path
    ):
        """File system errors should log warning and not crash."""
        with caplog.at_level(logging.WARNING):
            with patch("os.makedirs", side_effect=PermissionError("Permission denied")):
                # Should not raise
                workflow._save_health_data(health_result, str(tmp_path))

        assert "Failed to save health data (file system error)" in caplog.text

    def test_save_health_data_serialization_error_logs_error(
        self, workflow, health_result, caplog, tmp_path
    ):
        """JSON serialization errors should log error and not crash."""
        with caplog.at_level(logging.ERROR):
            with patch("json.dump", side_effect=TypeError("Object not JSON serializable")):
                # Should not raise
                workflow._save_health_data(health_result, str(tmp_path))

        assert "Failed to save health data (serialization error)" in caplog.text

    def test_save_health_data_unexpected_error_logs_warning(
        self, workflow, health_result, caplog, tmp_path
    ):
        """Unexpected errors should log warning (noqa: BLE001) and not crash."""
        with caplog.at_level(logging.WARNING):
            with patch("os.makedirs", side_effect=RuntimeError("Unexpected error")):
                # Should not raise
                workflow._save_health_data(health_result, str(tmp_path))

        assert "Failed to save health data (unexpected error)" in caplog.text


class TestSuccessfulHealthCheck:
    """Test that successful health checks still work correctly."""

    @pytest.fixture
    def workflow(self):
        """Create health check workflow instance."""
        return HealthCheckWorkflow(auto_fix=False)

    @pytest.mark.asyncio
    async def test_successful_lint_check_reports_issues(self, workflow):
        """Successful lint check with issues should report them."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stdout="file.py:1:1: E501 line too long\nfile.py:2:1: W291 trailing whitespace\n",
            )
            result = await workflow._basic_health_check(".")

        assert result["checks_run"]["lint"]["passed"] is False
        assert len(result["issues"]) > 0
        assert result["issues"][0]["category"] == "lint"
        assert result["health_score"] < 100

    @pytest.mark.asyncio
    async def test_successful_type_check_reports_issues(self, workflow):
        """Successful type check with errors should report them."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = [
                MagicMock(returncode=0, stdout=""),  # lint passes
                MagicMock(
                    returncode=1, stdout="file.py:10: error: Name 'foo' is not defined\n"
                ),  # types fail
            ]
            result = await workflow._basic_health_check(".")

        assert result["checks_run"]["types"]["passed"] is False
        assert any(i["category"] == "types" for i in result["issues"])
        assert result["health_score"] < 100

    @pytest.mark.asyncio
    async def test_all_checks_pass_health_score_100(self, workflow):
        """All checks passing should give health score 100."""
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="")
            result = await workflow._basic_health_check(".")

        assert result["health_score"] == 100.0
        assert result["is_healthy"] is True
        assert len(result["issues"]) == 0
