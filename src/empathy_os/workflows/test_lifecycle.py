"""
Test Lifecycle Manager - Event-Driven Test Management

Monitors file changes and automatically manages test lifecycle:
- Tracks when source files are created/modified/deleted
- Queues test generation tasks
- Schedules maintenance runs
- Integrates with git hooks and CI/CD

Can operate in different modes:
- watch: Monitor file changes in real-time
- hook: Process git hook events
- scheduled: Run periodic maintenance
- manual: User-triggered operations

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from ..project_index import ProjectIndex
from .test_maintenance import TestAction, TestMaintenanceWorkflow, TestPriority

logger = logging.getLogger(__name__)


@dataclass
class TestTask:
    """A queued test management task."""

    id: str
    file_path: str
    action: TestAction
    priority: TestPriority
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_for: datetime | None = None
    status: str = "pending"  # pending, running, completed, failed
    result: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "file_path": self.file_path,
            "action": self.action.value,
            "priority": self.priority.value,
            "created_at": self.created_at.isoformat(),
            "scheduled_for": self.scheduled_for.isoformat() if self.scheduled_for else None,
            "status": self.status,
            "result": self.result,
        }


class TestLifecycleManager:
    """
    Manages the lifecycle of tests based on source file events.

    Key responsibilities:
    - Queue tasks when files change
    - Process tasks based on priority
    - Track task history
    - Generate maintenance reports
    - Integrate with CI/CD pipelines
    """

    def __init__(
        self,
        project_root: str,
        index: ProjectIndex | None = None,
        auto_execute: bool = False,
        queue_file: str | None = None,
    ):
        self.project_root = Path(project_root)
        self.index = index or ProjectIndex(str(project_root))
        self.auto_execute = auto_execute

        # Task queue
        self._queue: list[TestTask] = []
        self._history: list[TestTask] = []
        self._task_counter = 0

        # Queue persistence
        self._queue_file = (
            Path(queue_file) if queue_file else self.project_root / ".empathy" / "test_queue.json"
        )

        # Callbacks
        self._on_task_queued: list[Callable[[TestTask], None]] = []
        self._on_task_completed: list[Callable[[TestTask], None]] = []

        # Load existing queue
        self._load_queue()

    # ===== Event Handlers =====

    async def on_file_created(self, file_path: str) -> TestTask | None:
        """Handle file creation."""
        # Refresh index to include new file
        self.index.refresh()

        record = self.index.get_file(file_path)
        if not record:
            return None

        if record.test_requirement.value != "required":
            logger.debug(f"File {file_path} does not require tests")
            return None

        # Queue test creation
        task = self._create_task(
            file_path=file_path,
            action=TestAction.CREATE,
            priority=self._determine_priority(record),
        )

        logger.info(f"Queued test creation for new file: {file_path}")
        return task

    async def on_file_modified(self, file_path: str) -> TestTask | None:
        """Handle file modification."""
        record = self.index.get_file(file_path)
        if not record:
            return None

        if record.test_requirement.value != "required":
            return None

        # Update index
        self.index.update_file(file_path, last_modified=datetime.now())

        if record.tests_exist:
            # Queue test review/update
            task = self._create_task(
                file_path=file_path,
                action=TestAction.REVIEW,
                priority=self._determine_priority(record),
            )
            logger.info(f"Queued test review for modified file: {file_path}")
        else:
            # Queue test creation
            task = self._create_task(
                file_path=file_path,
                action=TestAction.CREATE,
                priority=self._determine_priority(record),
            )
            logger.info(f"Queued test creation for modified file: {file_path}")

        return task

    async def on_file_deleted(self, file_path: str) -> TestTask | None:
        """Handle file deletion."""
        record = self.index.get_file(file_path)
        if not record or not record.test_file_path:
            return None

        # Queue orphan check
        task = self._create_task(
            file_path=file_path,
            action=TestAction.DELETE,
            priority=TestPriority.LOW,
        )

        logger.info(f"Queued orphan test check for deleted file: {file_path}")

        # Refresh index
        self.index.refresh()

        return task

    async def on_files_changed(self, changed_files: list[str]) -> list[TestTask]:
        """Handle multiple file changes (e.g., from git hook)."""
        tasks = []

        for file_path in changed_files:
            # Determine if file exists
            full_path = self.project_root / file_path
            if full_path.exists():
                # Could be create or modify - check if in index
                if self.index.get_file(file_path):
                    task = await self.on_file_modified(file_path)
                else:
                    task = await self.on_file_created(file_path)
            else:
                task = await self.on_file_deleted(file_path)

            if task:
                tasks.append(task)

        return tasks

    # ===== Task Management =====

    def _create_task(
        self,
        file_path: str,
        action: TestAction,
        priority: TestPriority,
    ) -> TestTask:
        """Create and queue a new task."""
        self._task_counter += 1

        task = TestTask(
            id=f"task_{self._task_counter}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            file_path=file_path,
            action=action,
            priority=priority,
        )

        # Check for duplicate
        existing = self._find_pending_task(file_path, action)
        if existing:
            logger.debug(f"Task already queued for {file_path}")
            return existing

        self._queue.append(task)
        self._save_queue()

        # Notify callbacks
        for callback in self._on_task_queued:
            callback(task)

        # Auto-execute if enabled
        if self.auto_execute:
            asyncio.create_task(self._execute_task(task))

        return task

    def _find_pending_task(self, file_path: str, action: TestAction) -> TestTask | None:
        """Find existing pending task for file."""
        for task in self._queue:
            if task.file_path == file_path and task.action == action and task.status == "pending":
                return task
        return None

    def _determine_priority(self, record) -> TestPriority:
        """Determine task priority based on file impact."""
        if record.impact_score >= 10.0:
            return TestPriority.CRITICAL
        elif record.impact_score >= 5.0:
            return TestPriority.HIGH
        elif record.impact_score >= 2.0:
            return TestPriority.MEDIUM
        else:
            return TestPriority.LOW

    async def _execute_task(self, task: TestTask) -> bool:
        """Execute a single task."""
        task.status = "running"
        self._save_queue()

        try:
            workflow = TestMaintenanceWorkflow(str(self.project_root), self.index)

            # Create a mini-plan with just this task
            result = await workflow.run(
                {
                    "mode": "execute",
                    "changed_files": [task.file_path],
                    "max_items": 1,
                }
            )

            task.status = "completed"
            task.result = result

            # Move to history
            self._queue.remove(task)
            self._history.append(task)

            # Notify callbacks
            for callback in self._on_task_completed:
                callback(task)

            return True

        except Exception as e:
            logger.error(f"Task {task.id} failed: {e}")
            task.status = "failed"
            task.result = {"error": str(e)}
            return False

        finally:
            self._save_queue()

    # ===== Queue Operations =====

    def get_queue(self) -> list[dict[str, Any]]:
        """Get current task queue."""
        return [task.to_dict() for task in self._queue]

    def get_pending_count(self) -> int:
        """Get number of pending tasks."""
        return len([t for t in self._queue if t.status == "pending"])

    def get_queue_by_priority(self, priority: TestPriority) -> list[TestTask]:
        """Get tasks by priority."""
        return [t for t in self._queue if t.priority == priority and t.status == "pending"]

    def clear_queue(self) -> int:
        """Clear all pending tasks. Returns count of cleared tasks."""
        count = len(self._queue)
        self._queue.clear()
        self._save_queue()
        return count

    async def process_queue(
        self,
        max_tasks: int = 10,
        priority_filter: TestPriority | None = None,
    ) -> dict[str, Any]:
        """Process pending tasks in queue."""
        tasks_to_process = [t for t in self._queue if t.status == "pending"]

        if priority_filter:
            priority_order = {
                TestPriority.CRITICAL: 0,
                TestPriority.HIGH: 1,
                TestPriority.MEDIUM: 2,
                TestPriority.LOW: 3,
                TestPriority.DEFERRED: 4,
            }
            filter_level = priority_order[priority_filter]
            tasks_to_process = [
                t for t in tasks_to_process if priority_order[t.priority] <= filter_level
            ]

        # Sort by priority
        tasks_to_process.sort(
            key=lambda t: (
                {"critical": 0, "high": 1, "medium": 2, "low": 3, "deferred": 4}[t.priority.value],
                t.created_at,
            )
        )

        # Limit
        tasks_to_process = tasks_to_process[:max_tasks]

        # Use typed variables for proper type inference
        processed = 0
        succeeded = 0
        failed = 0
        details: list[dict] = []

        for task in tasks_to_process:
            processed += 1
            success = await self._execute_task(task)
            if success:
                succeeded += 1
            else:
                failed += 1
            details.append(task.to_dict())

        return {
            "processed": processed,
            "succeeded": succeeded,
            "failed": failed,
            "details": details,
        }

    # ===== Persistence =====

    def _save_queue(self) -> None:
        """Save queue to file."""
        try:
            self._queue_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "queue": [t.to_dict() for t in self._queue],
                "history": [t.to_dict() for t in self._history[-100:]],  # Keep last 100
                "counter": self._task_counter,
                "saved_at": datetime.now().isoformat(),
            }

            with open(self._queue_file, "w") as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save queue: {e}")

    def _load_queue(self) -> None:
        """Load queue from file."""
        if not self._queue_file.exists():
            return

        try:
            with open(self._queue_file) as f:
                data = json.load(f)

            self._task_counter = data.get("counter", 0)

            # Restore queue
            for task_data in data.get("queue", []):
                task = TestTask(
                    id=task_data["id"],
                    file_path=task_data["file_path"],
                    action=TestAction(task_data["action"]),
                    priority=TestPriority(task_data["priority"]),
                    created_at=datetime.fromisoformat(task_data["created_at"]),
                    status=task_data["status"],
                )
                self._queue.append(task)

            logger.info(f"Loaded {len(self._queue)} tasks from queue")

        except Exception as e:
            logger.error(f"Failed to load queue: {e}")

    # ===== Scheduling =====

    def schedule_maintenance(
        self,
        interval_hours: int = 24,
        auto_execute: bool = False,
    ) -> dict[str, Any]:
        """Schedule periodic maintenance runs."""
        next_run = datetime.now() + timedelta(hours=interval_hours)

        return {
            "scheduled": True,
            "interval_hours": interval_hours,
            "next_run": next_run.isoformat(),
            "auto_execute": auto_execute,
            "command": f"python -m empathy_os.workflows.test_maintenance {'auto' if auto_execute else 'analyze'}",
        }

    async def run_maintenance(self, auto_execute: bool = False) -> dict[str, Any]:
        """Run a full maintenance cycle."""
        # Refresh index
        self.index.refresh()

        # Run workflow
        workflow = TestMaintenanceWorkflow(str(self.project_root), self.index)
        mode = "auto" if auto_execute else "analyze"

        result = await workflow.run({"mode": mode})

        return {
            "maintenance_run": True,
            "timestamp": datetime.now().isoformat(),
            "result": result,
        }

    # ===== Git Hook Integration =====

    async def process_git_pre_commit(self, staged_files: list[str]) -> dict[str, Any]:
        """
        Process git pre-commit hook.

        Returns warnings about files being committed without tests.
        """
        warnings = []
        blocking = []

        for file_path in staged_files:
            record = self.index.get_file(file_path)
            if not record:
                continue

            if record.test_requirement.value == "required" and not record.tests_exist:
                if record.impact_score >= 5.0:
                    blocking.append(
                        {
                            "file": file_path,
                            "reason": f"High-impact file ({record.impact_score:.1f}) without tests",
                        }
                    )
                else:
                    warnings.append(
                        {
                            "file": file_path,
                            "reason": "File requires tests but none exist",
                        }
                    )

        return {
            "hook": "pre-commit",
            "staged_files": len(staged_files),
            "blocking": blocking,
            "warnings": warnings,
            "allow_commit": len(blocking) == 0,
            "message": (
                f"Commit blocked: {len(blocking)} high-impact files need tests"
                if blocking
                else f"Commit allowed with {len(warnings)} test warnings"
            ),
        }

    async def process_git_post_commit(self, changed_files: list[str]) -> dict[str, Any]:
        """Process git post-commit hook."""
        tasks = await self.on_files_changed(changed_files)

        return {
            "hook": "post-commit",
            "changed_files": len(changed_files),
            "tasks_queued": len(tasks),
            "tasks": [t.to_dict() for t in tasks],
        }

    # ===== Callbacks =====

    def on_task_queued(self, callback: Callable[[TestTask], None]) -> None:
        """Register callback for when task is queued."""
        self._on_task_queued.append(callback)

    def on_task_completed(self, callback: Callable[[TestTask], None]) -> None:
        """Register callback for when task completes."""
        self._on_task_completed.append(callback)

    # ===== Status =====

    def get_status(self) -> dict[str, Any]:
        """Get lifecycle manager status."""
        return {
            "queue_size": len(self._queue),
            "pending": len([t for t in self._queue if t.status == "pending"]),
            "running": len([t for t in self._queue if t.status == "running"]),
            "auto_execute": self.auto_execute,
            "by_priority": {
                priority.value: len([t for t in self._queue if t.priority == priority])
                for priority in TestPriority
            },
            "history_size": len(self._history),
        }
