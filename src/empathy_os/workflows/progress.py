"""Progress Tracking System

Real-time progress tracking for workflow execution with WebSocket support.
Enables live UI updates during workflow runs.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from __future__ import annotations

import asyncio
import json
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Protocol


class ProgressStatus(Enum):
    """Status of a workflow or stage."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    FALLBACK = "fallback"  # Using fallback model
    RETRYING = "retrying"  # Retrying after error


@dataclass
class StageProgress:
    """Progress information for a single stage."""

    name: str
    status: ProgressStatus
    tier: str = "capable"
    model: str = ""
    started_at: datetime | None = None
    completed_at: datetime | None = None
    duration_ms: int = 0
    cost: float = 0.0
    tokens_in: int = 0
    tokens_out: int = 0
    error: str | None = None
    fallback_info: str | None = None
    retry_count: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "status": self.status.value,
            "tier": self.tier,
            "model": self.model,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "cost": self.cost,
            "tokens_in": self.tokens_in,
            "tokens_out": self.tokens_out,
            "error": self.error,
            "fallback_info": self.fallback_info,
            "retry_count": self.retry_count,
        }


@dataclass
class ProgressUpdate:
    """A progress update to be broadcast."""

    workflow: str
    workflow_id: str
    current_stage: str
    stage_index: int
    total_stages: int
    status: ProgressStatus
    message: str
    cost_so_far: float = 0.0
    tokens_so_far: int = 0
    percent_complete: float = 0.0
    estimated_remaining_ms: int | None = None
    stages: list[StageProgress] = field(default_factory=list)
    fallback_info: str | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "workflow": self.workflow,
            "workflow_id": self.workflow_id,
            "current_stage": self.current_stage,
            "stage_index": self.stage_index,
            "total_stages": self.total_stages,
            "status": self.status.value,
            "message": self.message,
            "cost_so_far": self.cost_so_far,
            "tokens_so_far": self.tokens_so_far,
            "percent_complete": self.percent_complete,
            "estimated_remaining_ms": self.estimated_remaining_ms,
            "stages": [s.to_dict() for s in self.stages],
            "fallback_info": self.fallback_info,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


# Type for progress callbacks
ProgressCallback = Callable[[ProgressUpdate], None]
AsyncProgressCallback = Callable[[ProgressUpdate], Coroutine[Any, Any, None]]


class ProgressTracker:
    """Tracks and broadcasts workflow progress.

    Maintains state for all stages and emits updates to registered callbacks.
    Supports both sync and async callbacks for flexibility.
    """

    def __init__(
        self,
        workflow_name: str,
        workflow_id: str,
        stage_names: list[str],
    ):
        self.workflow = workflow_name
        self.workflow_id = workflow_id
        self.stage_names = stage_names
        self.current_index = 0
        self.cost_accumulated = 0.0
        self.tokens_accumulated = 0
        self._started_at = datetime.now()
        self._stage_start_times: dict[str, datetime] = {}
        self._stage_durations: list[int] = []

        # Initialize stages
        self.stages: list[StageProgress] = [
            StageProgress(name=name, status=ProgressStatus.PENDING) for name in stage_names
        ]

        # Callbacks
        self._callbacks: list[ProgressCallback] = []
        self._async_callbacks: list[AsyncProgressCallback] = []

    def add_callback(self, callback: ProgressCallback) -> None:
        """Add a synchronous progress callback."""
        self._callbacks.append(callback)

    def add_async_callback(self, callback: AsyncProgressCallback) -> None:
        """Add an asynchronous progress callback."""
        self._async_callbacks.append(callback)

    def remove_callback(self, callback: ProgressCallback) -> None:
        """Remove a synchronous callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def start_workflow(self) -> None:
        """Mark workflow as started."""
        self._started_at = datetime.now()
        self._emit(ProgressStatus.RUNNING, f"Starting {self.workflow}...")

    def start_stage(self, stage_name: str, tier: str = "capable", model: str = "") -> None:
        """Mark a stage as started."""
        stage = self._get_stage(stage_name)
        if stage:
            stage.status = ProgressStatus.RUNNING
            stage.started_at = datetime.now()
            stage.tier = tier
            stage.model = model
            self._stage_start_times[stage_name] = stage.started_at
            self.current_index = self.stage_names.index(stage_name)

        self._emit(ProgressStatus.RUNNING, f"Running {stage_name}...")

    def complete_stage(
        self,
        stage_name: str,
        cost: float = 0.0,
        tokens_in: int = 0,
        tokens_out: int = 0,
    ) -> None:
        """Mark a stage as completed."""
        stage = self._get_stage(stage_name)
        if stage:
            stage.status = ProgressStatus.COMPLETED
            stage.completed_at = datetime.now()
            stage.cost = cost
            stage.tokens_in = tokens_in
            stage.tokens_out = tokens_out

            if stage.started_at:
                duration_ms = int((stage.completed_at - stage.started_at).total_seconds() * 1000)
                stage.duration_ms = duration_ms
                self._stage_durations.append(duration_ms)

        self.cost_accumulated += cost
        self.tokens_accumulated += tokens_in + tokens_out
        self.current_index = self.stage_names.index(stage_name) + 1

        self._emit(ProgressStatus.COMPLETED, f"Completed {stage_name}")

    def fail_stage(self, stage_name: str, error: str) -> None:
        """Mark a stage as failed."""
        stage = self._get_stage(stage_name)
        if stage:
            stage.status = ProgressStatus.FAILED
            stage.completed_at = datetime.now()
            stage.error = error

            if stage.started_at:
                stage.duration_ms = int(
                    (stage.completed_at - stage.started_at).total_seconds() * 1000,
                )

        self._emit(ProgressStatus.FAILED, f"Failed: {stage_name}", error=error)

    def skip_stage(self, stage_name: str, reason: str = "") -> None:
        """Mark a stage as skipped."""
        stage = self._get_stage(stage_name)
        if stage:
            stage.status = ProgressStatus.SKIPPED

        message = f"Skipped {stage_name}"
        if reason:
            message += f": {reason}"
        self._emit(ProgressStatus.SKIPPED, message)

    def update_tier(self, stage_name: str, new_tier: str, reason: str = "") -> None:
        """Update the tier for a stage during tier fallback.

        Args:
            stage_name: Name of the stage
            new_tier: New tier being attempted (CHEAP, CAPABLE, PREMIUM)
            reason: Optional reason for tier change (e.g., "validation_failed")

        """
        stage = self._get_stage(stage_name)
        if stage:
            old_tier = stage.tier
            stage.tier = new_tier

            message = f"Tier upgrade: {stage_name} [{old_tier.upper()} → {new_tier.upper()}]"
            if reason:
                message += f" ({reason})"

            self._emit(ProgressStatus.RUNNING, message)

    def fallback_occurred(
        self,
        stage_name: str,
        original_model: str,
        fallback_model: str,
        reason: str,
    ) -> None:
        """Record that a fallback occurred."""
        stage = self._get_stage(stage_name)
        fallback_info = f"{original_model} → {fallback_model} ({reason})"

        if stage:
            stage.status = ProgressStatus.FALLBACK
            stage.fallback_info = fallback_info

        self._emit(
            ProgressStatus.FALLBACK,
            f"Falling back from {original_model} to {fallback_model}",
            fallback_info=fallback_info,
        )

    def retry_occurred(self, stage_name: str, attempt: int, max_attempts: int) -> None:
        """Record that a retry is occurring."""
        stage = self._get_stage(stage_name)
        if stage:
            stage.status = ProgressStatus.RETRYING
            stage.retry_count = attempt

        self._emit(
            ProgressStatus.RETRYING,
            f"Retrying {stage_name} (attempt {attempt}/{max_attempts})",
        )

    def complete_workflow(self) -> None:
        """Mark workflow as completed."""
        self._emit(
            ProgressStatus.COMPLETED,
            f"Workflow {self.workflow} completed",
        )

    def fail_workflow(self, error: str) -> None:
        """Mark workflow as failed."""
        self._emit(
            ProgressStatus.FAILED,
            f"Workflow {self.workflow} failed",
            error=error,
        )

    def _get_stage(self, stage_name: str) -> StageProgress | None:
        """Get stage by name."""
        for stage in self.stages:
            if stage.name == stage_name:
                return stage
        return None

    def _calculate_percent_complete(self) -> float:
        """Calculate completion percentage."""
        completed = sum(1 for s in self.stages if s.status == ProgressStatus.COMPLETED)
        return (completed / len(self.stages)) * 100 if self.stages else 0.0

    def _estimate_remaining_ms(self) -> int | None:
        """Estimate remaining time based on average stage duration."""
        if not self._stage_durations:
            return None

        avg_duration = sum(self._stage_durations) / len(self._stage_durations)
        remaining_stages = len(self.stages) - self.current_index
        return int(avg_duration * remaining_stages)

    def _emit(
        self,
        status: ProgressStatus,
        message: str,
        fallback_info: str | None = None,
        error: str | None = None,
    ) -> None:
        """Emit a progress update to all callbacks."""
        current_stage = (
            self.stage_names[min(self.current_index, len(self.stage_names) - 1)]
            if self.stage_names
            else ""
        )

        update = ProgressUpdate(
            workflow=self.workflow,
            workflow_id=self.workflow_id,
            current_stage=current_stage,
            stage_index=self.current_index,
            total_stages=len(self.stages),
            status=status,
            message=message,
            cost_so_far=self.cost_accumulated,
            tokens_so_far=self.tokens_accumulated,
            percent_complete=self._calculate_percent_complete(),
            estimated_remaining_ms=self._estimate_remaining_ms(),
            stages=list(self.stages),
            fallback_info=fallback_info,
            error=error,
        )

        # Call sync callbacks
        for callback in self._callbacks:
            try:
                callback(update)
            except Exception as e:
                # Log but don't fail on callback errors
                print(f"Progress callback error: {e}")

        # Call async callbacks
        for async_callback in self._async_callbacks:
            try:
                asyncio.create_task(async_callback(update))
            except RuntimeError:
                # No event loop running, skip async callbacks
                pass


class ProgressReporter(Protocol):
    """Protocol for progress reporting implementations."""

    def report(self, update: ProgressUpdate) -> None:
        """Report a progress update."""
        ...

    async def report_async(self, update: ProgressUpdate) -> None:
        """Report a progress update asynchronously."""
        ...


class ConsoleProgressReporter:
    """Simple console-based progress reporter for CLI usage."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose

    def report(self, update: ProgressUpdate) -> None:
        """Print progress to console."""
        percent = f"{update.percent_complete:.0f}%"
        cost = f"${update.cost_so_far:.4f}"
        status_icon = {
            ProgressStatus.PENDING: "○",
            ProgressStatus.RUNNING: "◐",
            ProgressStatus.COMPLETED: "●",
            ProgressStatus.FAILED: "✗",
            ProgressStatus.SKIPPED: "◌",
            ProgressStatus.FALLBACK: "↩",
            ProgressStatus.RETRYING: "↻",
        }.get(update.status, "?")

        # Get current tier from running stage
        tier_info = ""
        if update.current_stage and update.stages:
            for stage in update.stages:
                if stage.name == update.current_stage and stage.status == ProgressStatus.RUNNING:
                    tier_info = f" [{stage.tier.upper()}]"
                    break

        print(f"[{percent}] {status_icon} {update.message}{tier_info} ({cost})")

        if self.verbose and update.fallback_info:
            print(f"       Fallback: {update.fallback_info}")
        if self.verbose and update.error:
            print(f"       Error: {update.error}")

    async def report_async(self, update: ProgressUpdate) -> None:
        """Async version just calls sync."""
        self.report(update)


class JsonLinesProgressReporter:
    """JSON Lines progress reporter for machine parsing."""

    def __init__(self, output_file: str | None = None):
        self.output_file = output_file

    def report(self, update: ProgressUpdate) -> None:
        """Output progress as JSON line."""
        json_line = update.to_json()

        if self.output_file:
            with open(self.output_file, "a") as f:
                f.write(json_line + "\n")
        else:
            print(json_line)

    async def report_async(self, update: ProgressUpdate) -> None:
        """Async version just calls sync."""
        self.report(update)


def create_progress_tracker(
    workflow_name: str,
    stage_names: list[str],
    reporter: ProgressReporter | None = None,
) -> ProgressTracker:
    """Factory function to create a progress tracker with optional reporter.

    Args:
        workflow_name: Name of the workflow
        stage_names: List of stage names in order
        reporter: Optional progress reporter

    Returns:
        Configured ProgressTracker instance

    """
    import uuid

    tracker = ProgressTracker(
        workflow_name=workflow_name,
        workflow_id=uuid.uuid4().hex[:12],
        stage_names=stage_names,
    )

    if reporter:
        tracker.add_callback(reporter.report)

    return tracker
