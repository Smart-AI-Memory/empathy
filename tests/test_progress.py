"""Tests for Progress Tracking System.

Tests real-time progress tracking for workflow execution.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from datetime import datetime
from unittest.mock import MagicMock

from src.empathy_os.workflows.progress import (
    ConsoleProgressReporter,
    JsonLinesProgressReporter,
    ProgressStatus,
    ProgressTracker,
    ProgressUpdate,
    StageProgress,
    create_progress_tracker,
)


class TestProgressStatus:
    """Tests for ProgressStatus enum."""

    def test_status_values(self):
        """Test status enum values."""
        assert ProgressStatus.PENDING.value == "pending"
        assert ProgressStatus.RUNNING.value == "running"
        assert ProgressStatus.COMPLETED.value == "completed"
        assert ProgressStatus.FAILED.value == "failed"
        assert ProgressStatus.SKIPPED.value == "skipped"
        assert ProgressStatus.FALLBACK.value == "fallback"
        assert ProgressStatus.RETRYING.value == "retrying"

    def test_all_statuses_exist(self):
        """Test all expected statuses exist."""
        statuses = list(ProgressStatus)
        assert len(statuses) == 7


class TestStageProgress:
    """Tests for StageProgress dataclass."""

    def test_create_stage(self):
        """Test creating a stage progress."""
        stage = StageProgress(
            name="analyze",
            status=ProgressStatus.PENDING,
        )

        assert stage.name == "analyze"
        assert stage.status == ProgressStatus.PENDING
        assert stage.tier == "capable"
        assert stage.cost == 0.0
        assert stage.error is None

    def test_stage_with_details(self):
        """Test stage with execution details."""
        stage = StageProgress(
            name="analyze",
            status=ProgressStatus.COMPLETED,
            tier="premium",
            model="claude-opus-4-5",
            duration_ms=1500,
            cost=0.05,
            tokens_in=1000,
            tokens_out=500,
        )

        assert stage.model == "claude-opus-4-5"
        assert stage.duration_ms == 1500
        assert stage.cost == 0.05

    def test_stage_to_dict(self):
        """Test stage serialization to dict."""
        now = datetime.now()
        stage = StageProgress(
            name="analyze",
            status=ProgressStatus.COMPLETED,
            tier="capable",
            started_at=now,
            completed_at=now,
        )

        data = stage.to_dict()

        assert data["name"] == "analyze"
        assert data["status"] == "completed"
        assert data["tier"] == "capable"
        assert data["started_at"] is not None

    def test_stage_with_error(self):
        """Test stage with error."""
        stage = StageProgress(
            name="analyze",
            status=ProgressStatus.FAILED,
            error="API timeout",
        )

        assert stage.error == "API timeout"

    def test_stage_with_fallback(self):
        """Test stage with fallback info."""
        stage = StageProgress(
            name="analyze",
            status=ProgressStatus.FALLBACK,
            fallback_info="claude-opus-4-5 → claude-sonnet-4-5 (rate limit)",
        )

        assert "claude-opus-4-5" in stage.fallback_info


class TestProgressUpdate:
    """Tests for ProgressUpdate dataclass."""

    def test_create_update(self):
        """Test creating a progress update."""
        update = ProgressUpdate(
            workflow="code-review",
            workflow_id="abc123",
            current_stage="analyze",
            stage_index=1,
            total_stages=3,
            status=ProgressStatus.RUNNING,
            message="Running analyze...",
        )

        assert update.workflow == "code-review"
        assert update.workflow_id == "abc123"
        assert update.current_stage == "analyze"
        assert update.stage_index == 1
        assert update.total_stages == 3

    def test_update_to_dict(self):
        """Test update serialization to dict."""
        update = ProgressUpdate(
            workflow="code-review",
            workflow_id="abc123",
            current_stage="analyze",
            stage_index=1,
            total_stages=3,
            status=ProgressStatus.RUNNING,
            message="Running...",
            cost_so_far=0.05,
            percent_complete=33.33,
        )

        data = update.to_dict()

        assert data["workflow"] == "code-review"
        assert data["status"] == "running"
        assert data["cost_so_far"] == 0.05
        assert data["percent_complete"] == 33.33
        assert "timestamp" in data

    def test_update_to_json(self):
        """Test update serialization to JSON."""
        update = ProgressUpdate(
            workflow="code-review",
            workflow_id="abc123",
            current_stage="analyze",
            stage_index=1,
            total_stages=3,
            status=ProgressStatus.RUNNING,
            message="Running...",
        )

        json_str = update.to_json()
        data = json.loads(json_str)

        assert data["workflow"] == "code-review"
        assert data["status"] == "running"

    def test_update_with_stages(self):
        """Test update with stage details."""
        stages = [
            StageProgress(name="classify", status=ProgressStatus.COMPLETED),
            StageProgress(name="analyze", status=ProgressStatus.RUNNING),
            StageProgress(name="report", status=ProgressStatus.PENDING),
        ]

        update = ProgressUpdate(
            workflow="code-review",
            workflow_id="abc123",
            current_stage="analyze",
            stage_index=1,
            total_stages=3,
            status=ProgressStatus.RUNNING,
            message="Running...",
            stages=stages,
        )

        data = update.to_dict()
        assert len(data["stages"]) == 3
        assert data["stages"][0]["status"] == "completed"
        assert data["stages"][1]["status"] == "running"


class TestProgressTracker:
    """Tests for ProgressTracker class."""

    def test_create_tracker(self):
        """Test creating a progress tracker."""
        tracker = ProgressTracker(
            workflow_name="code-review",
            workflow_id="test123",
            stage_names=["classify", "analyze", "report"],
        )

        assert tracker.workflow == "code-review"
        assert tracker.workflow_id == "test123"
        assert len(tracker.stages) == 3
        assert tracker.current_index == 0

    def test_stages_initialized_as_pending(self):
        """Test all stages start as pending."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b", "c"],
        )

        for stage in tracker.stages:
            assert stage.status == ProgressStatus.PENDING

    def test_add_callback(self):
        """Test adding a callback."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)

        assert callback in tracker._callbacks

    def test_remove_callback(self):
        """Test removing a callback."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.remove_callback(callback)

        assert callback not in tracker._callbacks

    def test_start_workflow(self):
        """Test starting a workflow."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.start_workflow()

        callback.assert_called_once()
        update = callback.call_args[0][0]
        assert update.status == ProgressStatus.RUNNING

    def test_start_stage(self):
        """Test starting a stage."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.start_stage("a", tier="cheap", model="haiku")

        assert tracker.stages[0].status == ProgressStatus.RUNNING
        assert tracker.stages[0].tier == "cheap"
        assert tracker.stages[0].model == "haiku"
        assert tracker.current_index == 0

    def test_complete_stage(self):
        """Test completing a stage."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b"],
        )

        tracker.start_stage("a")
        tracker.complete_stage("a", cost=0.01, tokens_in=100, tokens_out=50)

        assert tracker.stages[0].status == ProgressStatus.COMPLETED
        assert tracker.stages[0].cost == 0.01
        assert tracker.cost_accumulated == 0.01
        assert tracker.tokens_accumulated == 150
        assert tracker.current_index == 1

    def test_fail_stage(self):
        """Test failing a stage."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        tracker.start_stage("a")
        tracker.fail_stage("a", error="API error")

        assert tracker.stages[0].status == ProgressStatus.FAILED
        assert tracker.stages[0].error == "API error"

    def test_skip_stage(self):
        """Test skipping a stage."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.skip_stage("a", reason="Not needed")

        assert tracker.stages[0].status == ProgressStatus.SKIPPED
        callback.assert_called()

    def test_fallback_occurred(self):
        """Test recording a fallback."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        tracker.start_stage("a")
        tracker.fallback_occurred(
            "a",
            original_model="opus",
            fallback_model="sonnet",
            reason="rate limit",
        )

        assert tracker.stages[0].status == ProgressStatus.FALLBACK
        assert "opus → sonnet" in tracker.stages[0].fallback_info

    def test_retry_occurred(self):
        """Test recording a retry."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        tracker.start_stage("a")
        tracker.retry_occurred("a", attempt=2, max_attempts=3)

        assert tracker.stages[0].status == ProgressStatus.RETRYING
        assert tracker.stages[0].retry_count == 2

    def test_complete_workflow(self):
        """Test completing a workflow."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.complete_workflow()

        callback.assert_called()
        update = callback.call_args[0][0]
        assert update.status == ProgressStatus.COMPLETED

    def test_fail_workflow(self):
        """Test failing a workflow."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        callback = MagicMock()
        tracker.add_callback(callback)
        tracker.fail_workflow(error="Fatal error")

        callback.assert_called()
        update = callback.call_args[0][0]
        assert update.status == ProgressStatus.FAILED
        assert update.error == "Fatal error"

    def test_percent_complete_calculation(self):
        """Test percent complete calculation."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b", "c", "d"],
        )

        tracker.start_stage("a")
        tracker.complete_stage("a")
        tracker.start_stage("b")
        tracker.complete_stage("b")

        percent = tracker._calculate_percent_complete()
        assert percent == 50.0  # 2 of 4 completed

    def test_callback_error_handling(self):
        """Test callback errors don't crash tracker."""
        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )

        def bad_callback(update):
            raise Exception("Callback error")

        tracker.add_callback(bad_callback)

        # Should not raise
        tracker.start_workflow()


class TestConsoleProgressReporter:
    """Tests for ConsoleProgressReporter."""

    def test_create_reporter(self):
        """Test creating a console reporter."""
        reporter = ConsoleProgressReporter()
        assert reporter.verbose is False

        verbose_reporter = ConsoleProgressReporter(verbose=True)
        assert verbose_reporter.verbose is True

    def test_report(self, capsys):
        """Test reporting to console."""
        reporter = ConsoleProgressReporter()

        update = ProgressUpdate(
            workflow="test",
            workflow_id="123",
            current_stage="a",
            stage_index=0,
            total_stages=2,
            status=ProgressStatus.RUNNING,
            message="Running stage a",
            percent_complete=50.0,
            cost_so_far=0.01,
        )

        reporter.report(update)

        captured = capsys.readouterr()
        assert "50%" in captured.out
        assert "Running stage a" in captured.out
        assert "$0.01" in captured.out

    def test_verbose_shows_fallback(self, capsys):
        """Test verbose mode shows fallback info."""
        reporter = ConsoleProgressReporter(verbose=True)

        update = ProgressUpdate(
            workflow="test",
            workflow_id="123",
            current_stage="a",
            stage_index=0,
            total_stages=1,
            status=ProgressStatus.FALLBACK,
            message="Fallback",
            fallback_info="opus → sonnet",
        )

        reporter.report(update)

        captured = capsys.readouterr()
        assert "Fallback" in captured.out
        assert "opus → sonnet" in captured.out


class TestJsonLinesProgressReporter:
    """Tests for JsonLinesProgressReporter."""

    def test_create_reporter(self):
        """Test creating a JSON Lines reporter."""
        reporter = JsonLinesProgressReporter()
        assert reporter.output_file is None

    def test_report_to_stdout(self, capsys):
        """Test reporting to stdout."""
        reporter = JsonLinesProgressReporter()

        update = ProgressUpdate(
            workflow="test",
            workflow_id="123",
            current_stage="a",
            stage_index=0,
            total_stages=1,
            status=ProgressStatus.RUNNING,
            message="Running",
        )

        reporter.report(update)

        captured = capsys.readouterr()
        data = json.loads(captured.out.strip())
        assert data["workflow"] == "test"
        assert data["status"] == "running"

    def test_report_to_file(self):
        """Test reporting to file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            filename = f.name

        try:
            reporter = JsonLinesProgressReporter(output_file=filename)

            update = ProgressUpdate(
                workflow="test",
                workflow_id="123",
                current_stage="a",
                stage_index=0,
                total_stages=1,
                status=ProgressStatus.COMPLETED,
                message="Done",
            )

            reporter.report(update)

            with open(filename) as f:
                line = f.readline()
                data = json.loads(line)
                assert data["workflow"] == "test"
                assert data["status"] == "completed"
        finally:
            import os

            os.unlink(filename)


class TestCreateProgressTracker:
    """Tests for create_progress_tracker factory function."""

    def test_create_basic_tracker(self):
        """Test creating a basic tracker."""
        tracker = create_progress_tracker(
            workflow_name="code-review",
            stage_names=["a", "b", "c"],
        )

        assert tracker.workflow == "code-review"
        assert len(tracker.stages) == 3
        assert len(tracker.workflow_id) == 12  # UUID hex

    def test_create_with_reporter(self):
        """Test creating tracker with reporter."""
        reporter = ConsoleProgressReporter()

        tracker = create_progress_tracker(
            workflow_name="test",
            stage_names=["a"],
            reporter=reporter,
        )

        # Reporter callback should be added
        assert len(tracker._callbacks) == 1


class TestProgressTrackerIntegration:
    """Integration tests for progress tracking."""

    def test_full_workflow_lifecycle(self):
        """Test a complete workflow lifecycle."""
        updates = []

        def capture_update(update):
            updates.append(update)

        tracker = ProgressTracker(
            workflow_name="code-review",
            workflow_id="test123",
            stage_names=["classify", "analyze", "report"],
        )
        tracker.add_callback(capture_update)

        # Run full workflow
        tracker.start_workflow()
        tracker.start_stage("classify", tier="cheap")
        tracker.complete_stage("classify", cost=0.001)
        tracker.start_stage("analyze", tier="capable")
        tracker.complete_stage("analyze", cost=0.01)
        tracker.start_stage("report", tier="cheap")
        tracker.complete_stage("report", cost=0.001)
        tracker.complete_workflow()

        # Verify updates
        assert len(updates) >= 7  # start + 3*(start+complete) + complete
        assert updates[-1].status == ProgressStatus.COMPLETED
        assert updates[-1].percent_complete == 100.0

    def test_workflow_with_failure(self):
        """Test workflow with stage failure."""
        updates = []

        def capture_update(update):
            updates.append(update)

        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a", "b"],
        )
        tracker.add_callback(capture_update)

        tracker.start_workflow()
        tracker.start_stage("a")
        tracker.fail_stage("a", "Error occurred")
        tracker.fail_workflow("Stage a failed")

        # Should have failure updates
        failed_updates = [u for u in updates if u.status == ProgressStatus.FAILED]
        assert len(failed_updates) >= 2  # stage fail + workflow fail

    def test_workflow_with_fallback_and_retry(self):
        """Test workflow with fallback and retry."""
        updates = []

        def capture_update(update):
            updates.append(update)

        tracker = ProgressTracker(
            workflow_name="test",
            workflow_id="123",
            stage_names=["a"],
        )
        tracker.add_callback(capture_update)

        tracker.start_workflow()
        tracker.start_stage("a")
        tracker.fallback_occurred("a", "opus", "sonnet", "rate limit")
        tracker.retry_occurred("a", 1, 3)
        tracker.complete_stage("a", cost=0.01)
        tracker.complete_workflow()

        statuses = [u.status for u in updates]
        assert ProgressStatus.FALLBACK in statuses
        assert ProgressStatus.RETRYING in statuses
        assert ProgressStatus.COMPLETED in statuses
