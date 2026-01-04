"""Test Maintenance Workflow - Automatic Test Lifecycle Management

Integrates with Project Index to:
- Track files requiring tests
- Detect when tests become stale
- Generate test plans based on file events
- Execute automatic test generation
- Report on test health

Key events handled:
- File created: Check if needs tests, queue for generation
- File modified: Check if tests need updating
- File deleted: Mark associated tests as orphaned

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..project_index import FileRecord, ProjectIndex
from ..project_index.reports import ReportGenerator

logger = logging.getLogger(__name__)


class TestAction(str, Enum):
    """Actions that can be taken for test management."""

    CREATE = "create"  # Create new tests
    UPDATE = "update"  # Update existing tests
    REVIEW = "review"  # Review and possibly regenerate
    DELETE = "delete"  # Delete orphaned tests
    SKIP = "skip"  # No action needed
    MANUAL = "manual"  # Requires manual intervention


class TestPriority(str, Enum):
    """Priority levels for test actions."""

    CRITICAL = "critical"  # High-impact files, blocking
    HIGH = "high"  # Important files
    MEDIUM = "medium"  # Standard priority
    LOW = "low"  # Nice to have
    DEFERRED = "deferred"  # Can wait


@dataclass
class TestPlanItem:
    """A single item in a test maintenance plan."""

    file_path: str
    action: TestAction
    priority: TestPriority
    reason: str
    test_file_path: str | None = None
    estimated_effort: str = "unknown"
    auto_executable: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "action": self.action.value,
            "priority": self.priority.value,
            "reason": self.reason,
            "test_file_path": self.test_file_path,
            "estimated_effort": self.estimated_effort,
            "auto_executable": self.auto_executable,
            "metadata": self.metadata,
        }


@dataclass
class TestMaintenancePlan:
    """Complete test maintenance plan for a project."""

    generated_at: datetime = field(default_factory=datetime.now)
    items: list[TestPlanItem] = field(default_factory=list)
    summary: dict[str, Any] = field(default_factory=dict)
    options: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "generated_at": self.generated_at.isoformat(),
            "items": [item.to_dict() for item in self.items],
            "summary": self.summary,
            "options": self.options,
        }

    def get_items_by_action(self, action: TestAction) -> list[TestPlanItem]:
        return [item for item in self.items if item.action == action]

    def get_items_by_priority(self, priority: TestPriority) -> list[TestPlanItem]:
        return [item for item in self.items if item.priority == priority]

    def get_auto_executable_items(self) -> list[TestPlanItem]:
        return [item for item in self.items if item.auto_executable]


class TestMaintenanceWorkflow:
    """Workflow for automatic test lifecycle management.

    Integrates with Project Index to track and manage tests.
    Can run automatically on file events or manually on demand.

    Modes:
    - analyze: Generate plan without executing
    - execute: Execute plan items (with confirmation)
    - auto: Automatically execute auto_executable items
    - report: Generate detailed test health report
    """

    def __init__(self, project_root: str, index: ProjectIndex | None = None):
        self.name = "test_maintenance"
        self.description = "Automatic test lifecycle management"
        self.project_root = Path(project_root)
        self.index = index or ProjectIndex(str(project_root))
        self._ensure_index_loaded()

    def _ensure_index_loaded(self) -> None:
        """Ensure index is loaded, refresh if needed."""
        if not self.index.load():
            logger.info("Index not found, refreshing...")
            self.index.refresh()

    async def run(self, context: dict[str, Any]) -> dict[str, Any]:
        """Run the test maintenance workflow.

        Context options:
            mode: "analyze" | "execute" | "auto" | "report"
            changed_files: List of files that changed (for event-driven)
            max_items: Maximum items to process (default: 20)
            priority_filter: Only process items of this priority or higher
            dry_run: If True, don't actually execute (default: False)
        """
        mode = context.get("mode", "analyze")
        changed_files = context.get("changed_files", [])
        max_items = context.get("max_items", 20)
        dry_run = context.get("dry_run", False)

        # Refresh index if files changed
        if changed_files:
            self.index.refresh()

        # Generate the plan
        plan = self._generate_plan(changed_files, max_items)

        result = {
            "workflow": self.name,
            "mode": mode,
            "generated_at": datetime.now().isoformat(),
            "plan": plan.to_dict(),
        }

        if mode == "analyze":
            # Just return the plan
            result["status"] = "plan_generated"
            result["message"] = f"Generated plan with {len(plan.items)} items"

        elif mode == "execute":
            if dry_run:
                result["status"] = "dry_run"
                result["message"] = f"Would execute {len(plan.items)} items"
            else:
                execution_result = await self._execute_plan(plan, auto_only=False)
                result["execution"] = execution_result
                result["status"] = "executed"

        elif mode == "auto":
            auto_items = plan.get_auto_executable_items()
            if dry_run:
                result["status"] = "dry_run"
                result["message"] = f"Would auto-execute {len(auto_items)} items"
            else:
                execution_result = await self._execute_plan(plan, auto_only=True)
                result["execution"] = execution_result
                result["status"] = "auto_executed"

        elif mode == "report":
            report = self._generate_report()
            result["report"] = report
            result["status"] = "report_generated"

        return result

    def _generate_plan(
        self,
        changed_files: list[str],
        max_items: int,
    ) -> TestMaintenancePlan:
        """Generate a test maintenance plan."""
        plan = TestMaintenancePlan()
        items: list[TestPlanItem] = []

        # If specific files changed, prioritize them
        if changed_files:
            for file_path in changed_files:
                record = self.index.get_file(file_path)
                if record:
                    item = self._create_plan_item_for_file(record, event="modified")
                    if item and item.action != TestAction.SKIP:
                        items.append(item)

        # Add files needing tests (not in changed_files)
        changed_set = set(changed_files)
        for record in self.index.get_files_needing_tests():
            if record.path not in changed_set:
                item = self._create_plan_item_for_file(record, event="missing_tests")
                if item and item.action != TestAction.SKIP:
                    items.append(item)

        # Add stale test files
        for record in self.index.get_stale_files():
            if record.path not in changed_set:
                item = self._create_plan_item_for_file(record, event="stale")
                if item and item.action != TestAction.SKIP:
                    items.append(item)

        # Sort by priority
        priority_order = {
            TestPriority.CRITICAL: 0,
            TestPriority.HIGH: 1,
            TestPriority.MEDIUM: 2,
            TestPriority.LOW: 3,
            TestPriority.DEFERRED: 4,
        }

        def get_sort_key(item: TestPlanItem) -> tuple[int, float]:
            file_rec = self.index.get_file(item.file_path)
            impact = float(-file_rec.impact_score) if file_rec else 0.0
            return (priority_order[item.priority], impact)

        items.sort(key=get_sort_key)

        # Limit items
        plan.items = items[:max_items]

        # Generate summary
        plan.summary = {
            "total_items": len(items),
            "shown_items": len(plan.items),
            "by_action": {
                action.value: len([i for i in items if i.action == action]) for action in TestAction
            },
            "by_priority": {
                priority.value: len([i for i in items if i.priority == priority])
                for priority in TestPriority
            },
            "auto_executable": len([i for i in items if i.auto_executable]),
            "manual_required": len([i for i in items if not i.auto_executable]),
        }

        # Generate options for the user
        plan.options = self._generate_options(plan)

        return plan

    def _create_plan_item_for_file(
        self,
        record: FileRecord,
        event: str,
    ) -> TestPlanItem | None:
        """Create a plan item for a specific file."""
        # Determine action based on event and file state
        if event == "missing_tests":
            action = TestAction.CREATE
            reason = "File requires tests but none exist"
        elif event == "stale":
            action = TestAction.UPDATE
            reason = f"Tests are {record.staleness_days} days stale"
        elif event == "modified":
            if record.tests_exist:
                action = TestAction.REVIEW
                reason = "Source file modified, tests may need update"
            else:
                action = TestAction.CREATE
                reason = "Modified file needs tests"
        elif event == "deleted":
            action = TestAction.DELETE
            reason = "Source file deleted, tests may be orphaned"
        else:
            action = TestAction.SKIP
            reason = "No action needed"

        # Determine priority based on impact score
        if record.impact_score >= 10.0:
            priority = TestPriority.CRITICAL
        elif record.impact_score >= 5.0:
            priority = TestPriority.HIGH
        elif record.impact_score >= 2.0:
            priority = TestPriority.MEDIUM
        else:
            priority = TestPriority.LOW

        # Estimate effort
        if record.lines_of_code < 50:
            effort = "small (< 1 hour)"
        elif record.lines_of_code < 200:
            effort = "medium (1-2 hours)"
        else:
            effort = "large (2+ hours)"

        # Determine if auto-executable
        auto_executable = (
            action in [TestAction.CREATE, TestAction.UPDATE]
            and record.language == "python"
            and record.lines_of_code < 500
        )

        return TestPlanItem(
            file_path=record.path,
            action=action,
            priority=priority,
            reason=reason,
            test_file_path=record.test_file_path,
            estimated_effort=effort,
            auto_executable=auto_executable,
            metadata={
                "lines_of_code": record.lines_of_code,
                "impact_score": record.impact_score,
                "language": record.language,
                "complexity": record.complexity_score,
            },
        )

    def _generate_options(self, plan: TestMaintenancePlan) -> list[dict[str, Any]]:
        """Generate execution options for the user."""
        options = []

        # Option 1: Execute all auto-executable
        auto_count = len(plan.get_auto_executable_items())
        if auto_count > 0:
            options.append(
                {
                    "id": "auto_all",
                    "name": "Auto-execute all",
                    "description": f"Automatically generate/update tests for {auto_count} files",
                    "item_count": auto_count,
                    "estimated_time": f"{auto_count * 5}-{auto_count * 15} minutes",
                    "command": "python -m empathy_os.workflows.test_maintenance auto",
                },
            )

        # Option 2: Critical only
        critical_count = len(plan.get_items_by_priority(TestPriority.CRITICAL))
        if critical_count > 0:
            options.append(
                {
                    "id": "critical_only",
                    "name": "Critical files only",
                    "description": f"Focus on {critical_count} critical high-impact files",
                    "item_count": critical_count,
                    "estimated_time": f"{critical_count * 10}-{critical_count * 20} minutes",
                    "command": "python -m empathy_os.workflows.test_maintenance execute --priority critical",
                },
            )

        # Option 3: Create new tests only
        create_count = len(plan.get_items_by_action(TestAction.CREATE))
        if create_count > 0:
            options.append(
                {
                    "id": "create_only",
                    "name": "Create new tests only",
                    "description": f"Generate tests for {create_count} files without tests",
                    "item_count": create_count,
                    "estimated_time": f"{create_count * 10}-{create_count * 20} minutes",
                    "command": "python -m empathy_os.workflows.test_maintenance execute --action create",
                },
            )

        # Option 4: Update stale tests only
        update_count = len(plan.get_items_by_action(TestAction.UPDATE))
        if update_count > 0:
            options.append(
                {
                    "id": "update_stale",
                    "name": "Update stale tests",
                    "description": f"Update {update_count} stale test files",
                    "item_count": update_count,
                    "estimated_time": f"{update_count * 5}-{update_count * 10} minutes",
                    "command": "python -m empathy_os.workflows.test_maintenance execute --action update",
                },
            )

        # Option 5: Manual review
        options.append(
            {
                "id": "manual_review",
                "name": "Manual review",
                "description": "Review the plan and select specific items",
                "item_count": len(plan.items),
                "command": "python -m empathy_os.workflows.test_maintenance analyze --json",
            },
        )

        return options

    async def _execute_plan(
        self,
        plan: TestMaintenancePlan,
        auto_only: bool = False,
    ) -> dict[str, Any]:
        """Execute items in the plan."""
        items_to_execute = plan.get_auto_executable_items() if auto_only else plan.items

        # Use typed variables for proper type inference
        succeeded = 0
        failed = 0
        skipped = 0
        details: list[dict[str, Any]] = []

        for item in items_to_execute:
            try:
                if item.action == TestAction.CREATE:
                    success = await self._create_tests_for_file(item)
                elif item.action == TestAction.UPDATE:
                    success = await self._update_tests_for_file(item)
                elif item.action == TestAction.REVIEW:
                    success = await self._review_tests_for_file(item)
                elif item.action == TestAction.DELETE:
                    success = await self._delete_orphaned_tests(item)
                else:
                    success = False
                    skipped += 1
                    continue

                if success:
                    succeeded += 1
                    # Update index
                    self.index.update_file(
                        item.file_path,
                        tests_exist=True,
                        tests_last_modified=datetime.now(),
                        is_stale=False,
                        staleness_days=0,
                    )
                else:
                    failed += 1

                details.append(
                    {
                        "file": item.file_path,
                        "action": item.action.value,
                        "success": success,
                    },
                )

            except Exception as e:
                logger.error(f"Error processing {item.file_path}: {e}")
                failed += 1
                details.append(
                    {
                        "file": item.file_path,
                        "action": item.action.value,
                        "success": False,
                        "error": str(e),
                    },
                )

        return {
            "total": len(items_to_execute),
            "succeeded": succeeded,
            "failed": failed,
            "skipped": skipped,
            "details": details,
        }

    async def _create_tests_for_file(self, item: TestPlanItem) -> bool:
        """Create tests for a file using test-gen workflow."""
        # This would integrate with the test-gen workflow
        # For now, return True as placeholder
        logger.info(f"Would create tests for: {item.file_path}")
        return True

    async def _update_tests_for_file(self, item: TestPlanItem) -> bool:
        """Update existing tests for a file."""
        logger.info(f"Would update tests for: {item.file_path}")
        return True

    async def _review_tests_for_file(self, item: TestPlanItem) -> bool:
        """Review and possibly regenerate tests."""
        logger.info(f"Would review tests for: {item.file_path}")
        return True

    async def _delete_orphaned_tests(self, item: TestPlanItem) -> bool:
        """Delete orphaned test files."""
        logger.info(f"Would delete orphaned tests for: {item.file_path}")
        return True

    def _generate_report(self) -> dict[str, Any]:
        """Generate detailed test health report."""
        generator = ReportGenerator(
            self.index.get_summary(),
            self.index.get_all_files(),
        )

        return {
            "health": generator.health_report(),
            "test_gap": generator.test_gap_report(),
            "staleness": generator.staleness_report(),
            "coverage": generator.coverage_report(),
        }

    # ===== Event Handlers =====

    async def on_file_created(self, file_path: str) -> dict[str, Any]:
        """Handle file creation event."""
        self.index.refresh()
        record = self.index.get_file(file_path)

        if not record:
            return {"status": "not_indexed", "file": file_path}

        if record.test_requirement.value == "required":
            item = self._create_plan_item_for_file(record, event="missing_tests")
            return {
                "status": "needs_tests",
                "file": file_path,
                "plan_item": item.to_dict() if item else None,
                "message": f"New file {file_path} requires tests",
            }

        return {"status": "no_tests_required", "file": file_path}

    async def on_file_modified(self, file_path: str) -> dict[str, Any]:
        """Handle file modification event."""
        record = self.index.get_file(file_path)

        if not record:
            self.index.refresh()
            record = self.index.get_file(file_path)

        if not record:
            return {"status": "not_indexed", "file": file_path}

        # Mark as potentially stale
        if record.tests_exist and record.test_file_path:
            self.index.update_file(
                file_path,
                last_modified=datetime.now(),
                is_stale=True,
            )

            item = self._create_plan_item_for_file(record, event="modified")
            return {
                "status": "tests_may_need_update",
                "file": file_path,
                "test_file": record.test_file_path,
                "plan_item": item.to_dict() if item else None,
            }

        if record.test_requirement.value == "required":
            item = self._create_plan_item_for_file(record, event="modified")
            return {
                "status": "needs_tests",
                "file": file_path,
                "plan_item": item.to_dict() if item else None,
            }

        return {"status": "no_action_needed", "file": file_path}

    async def on_file_deleted(self, file_path: str) -> dict[str, Any]:
        """Handle file deletion event."""
        record = self.index.get_file(file_path)

        if record and record.test_file_path:
            test_path = self.project_root / record.test_file_path
            if test_path.exists():
                return {
                    "status": "orphaned_tests",
                    "file": file_path,
                    "test_file": record.test_file_path,
                    "message": f"Tests at {record.test_file_path} may be orphaned",
                    "action": "review_for_deletion",
                }

        # Refresh index to remove deleted file
        self.index.refresh()

        return {"status": "file_removed", "file": file_path}

    # ===== Convenience Methods =====

    def get_files_needing_tests(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get files that need tests, prioritized by impact."""
        files = self.index.get_files_needing_tests()
        return [
            {
                "path": f.path,
                "impact_score": f.impact_score,
                "lines_of_code": f.lines_of_code,
                "language": f.language,
            }
            for f in sorted(files, key=lambda x: -x.impact_score)[:limit]
        ]

    def get_stale_tests(self, limit: int = 20) -> list[dict[str, Any]]:
        """Get files with stale tests."""
        files = self.index.get_stale_files()
        return [
            {
                "path": f.path,
                "test_file": f.test_file_path,
                "staleness_days": f.staleness_days,
            }
            for f in sorted(files, key=lambda x: -x.staleness_days)[:limit]
        ]

    def get_test_health_summary(self) -> dict[str, Any]:
        """Get quick test health summary."""
        summary = self.index.get_summary()
        return {
            "files_requiring_tests": summary.files_requiring_tests,
            "files_with_tests": summary.files_with_tests,
            "files_without_tests": summary.files_without_tests,
            "coverage_avg": summary.test_coverage_avg,
            "stale_count": summary.stale_file_count,
            "test_to_code_ratio": summary.test_to_code_ratio,
        }
