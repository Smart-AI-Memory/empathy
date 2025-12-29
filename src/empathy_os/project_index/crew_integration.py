"""
Crew Integration for Project Index

Enables CrewAI crews and agents to maintain the project index.

Key features:
- Index Maintainer Crew: Automatic index updates
- Agent tools for querying and updating index
- Scheduled maintenance tasks
- Integration with existing workflows

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from collections.abc import Callable
from datetime import datetime
from typing import Any

from .index import ProjectIndex
from .models import FileRecord
from .reports import ReportGenerator


class ProjectIndexTools:
    """
    Tools for agents to interact with the project index.

    These can be registered with CrewAI or LangChain agents.
    """

    def __init__(self, index: ProjectIndex):
        self.index = index

    def get_tools(self) -> list[dict[str, Any]]:
        """Get tool definitions for agent registration."""
        return [
            {
                "name": "query_project_index",
                "description": "Query the project index for file information. Returns files matching criteria.",
                "func": self.query_index,
                "parameters": {
                    "query_type": "string (one of: needing_tests, stale, high_impact, by_path)",
                    "filter_value": "string (optional path pattern or category)",
                },
            },
            {
                "name": "get_file_info",
                "description": "Get detailed information about a specific file.",
                "func": self.get_file_info,
                "parameters": {
                    "file_path": "string (relative path to file)",
                },
            },
            {
                "name": "update_file_metadata",
                "description": "Update metadata for a file in the index.",
                "func": self.update_file_metadata,
                "parameters": {
                    "file_path": "string (relative path to file)",
                    "updates": "dict (key-value pairs to update)",
                },
            },
            {
                "name": "get_project_summary",
                "description": "Get overall project health summary.",
                "func": self.get_project_summary,
                "parameters": {},
            },
            {
                "name": "generate_report",
                "description": "Generate a specific report (health, test_gap, staleness, sprint_planning).",
                "func": self.generate_report,
                "parameters": {
                    "report_type": "string (one of: health, test_gap, staleness, sprint_planning)",
                },
            },
            {
                "name": "refresh_index",
                "description": "Refresh the entire project index by re-scanning files.",
                "func": self.refresh_index,
                "parameters": {},
            },
            {
                "name": "mark_tests_updated",
                "description": "Mark that tests have been updated for a file.",
                "func": self.mark_tests_updated,
                "parameters": {
                    "file_path": "string (relative path to source file)",
                    "test_file_path": "string (relative path to test file)",
                },
            },
        ]

    def query_index(self, query_type: str, filter_value: str = "") -> list[dict[str, Any]]:
        """Query the index for files."""
        if query_type == "needing_tests":
            files = self.index.get_files_needing_tests()
        elif query_type == "stale":
            files = self.index.get_stale_files()
        elif query_type == "high_impact":
            files = self.index.get_high_impact_files()
        elif query_type == "by_path" and filter_value:
            files = self.index.search_files(filter_value)
        elif query_type == "attention":
            files = self.index.get_files_needing_attention()
        else:
            files = []

        return [f.to_dict() for f in files[:20]]

    def get_file_info(self, file_path: str) -> dict[str, Any] | None:
        """Get info for a specific file."""
        record = self.index.get_file(file_path)
        return record.to_dict() if record else None

    def update_file_metadata(self, file_path: str, updates: dict[str, Any]) -> bool:
        """Update file metadata."""
        return self.index.update_file(file_path, **updates)

    def get_project_summary(self) -> dict[str, Any]:
        """Get project summary."""
        return self.index.get_summary().to_dict()

    def generate_report(self, report_type: str) -> dict[str, Any]:
        """Generate a report."""
        generator = ReportGenerator(
            self.index.get_summary(),
            self.index.get_all_files(),
        )

        if report_type == "health":
            return generator.health_report()
        elif report_type == "test_gap":
            return generator.test_gap_report()
        elif report_type == "staleness":
            return generator.staleness_report()
        elif report_type == "sprint_planning":
            return generator.sprint_planning_report()
        elif report_type == "coverage":
            return generator.coverage_report()
        else:
            return generator.health_report()

    def refresh_index(self) -> dict[str, Any]:
        """Refresh the index."""
        self.index.refresh()
        return {
            "status": "refreshed",
            "file_count": len(self.index.get_all_files()),
            "timestamp": datetime.now().isoformat(),
        }

    def mark_tests_updated(self, file_path: str, test_file_path: str) -> bool:
        """Mark tests as updated for a file."""
        return self.index.update_file(
            file_path,
            tests_exist=True,
            test_file_path=test_file_path,
            tests_last_modified=datetime.now(),
            is_stale=False,
            staleness_days=0,
        )


class IndexMaintenanceTasks:
    """
    Maintenance tasks that can be run by agents or scheduled.

    These tasks keep the index accurate and up-to-date.
    """

    def __init__(self, index: ProjectIndex):
        self.index = index

    def daily_refresh(self) -> dict[str, Any]:
        """
        Daily index refresh.

        - Re-scans all files
        - Updates staleness calculations
        - Generates summary
        """
        self.index.refresh()

        return {
            "task": "daily_refresh",
            "completed_at": datetime.now().isoformat(),
            "files_indexed": len(self.index.get_all_files()),
            "files_needing_attention": self.index.get_summary().files_needing_attention,
        }

    def coverage_sync(self, coverage_xml_path: str) -> dict[str, Any]:
        """
        Sync coverage data from coverage.xml.

        Should be run after test runs.
        """
        import defusedxml.ElementTree as ET

        try:
            tree = ET.parse(coverage_xml_path)
            root = tree.getroot()

            coverage_data: dict[str, float] = {}

            for package in root.findall(".//package"):
                for cls in package.findall("classes/class"):
                    filename = cls.get("filename", "")
                    line_rate = float(cls.get("line-rate", 0))
                    coverage_data[filename] = line_rate * 100

            updated = self.index.update_coverage(coverage_data)

            return {
                "task": "coverage_sync",
                "completed_at": datetime.now().isoformat(),
                "files_updated": updated,
            }

        except Exception as e:
            return {
                "task": "coverage_sync",
                "error": str(e),
            }

    def identify_test_opportunities(self) -> dict[str, Any]:
        """
        Identify files that are good candidates for test generation.

        Prioritizes by impact and ease of testing.
        """
        needing_tests = self.index.get_files_needing_tests()

        opportunities = []
        for record in needing_tests[:20]:
            opportunity = {
                "path": record.path,
                "priority": "high" if record.impact_score >= 5.0 else "medium",
                "estimated_effort": self._estimate_test_effort(record),
                "reason": self._test_reason(record),
            }
            opportunities.append(opportunity)

        return {
            "task": "identify_test_opportunities",
            "completed_at": datetime.now().isoformat(),
            "opportunities": opportunities,
        }

    def _estimate_test_effort(self, record: FileRecord) -> str:
        """Estimate effort to write tests."""
        if record.lines_of_code < 50:
            return "small"
        elif record.lines_of_code < 200:
            return "medium"
        else:
            return "large"

    def _test_reason(self, record: FileRecord) -> str:
        """Generate reason for testing."""
        reasons = []
        if record.impact_score >= 5.0:
            reasons.append(f"high impact ({record.impact_score:.1f})")
        if record.imported_by_count > 3:
            reasons.append(f"used by {record.imported_by_count} files")
        if not reasons:
            reasons.append("untested source file")
        return ", ".join(reasons)

    def stale_test_alert(self) -> dict[str, Any]:
        """
        Check for stale tests and generate alerts.
        """
        stale = self.index.get_stale_files()

        alerts = []
        for record in stale:
            if record.staleness_days > 30:
                severity = "high"
            elif record.staleness_days > 14:
                severity = "medium"
            else:
                severity = "low"

            alerts.append(
                {
                    "path": record.path,
                    "staleness_days": record.staleness_days,
                    "severity": severity,
                    "test_file": record.test_file_path,
                }
            )

        return {
            "task": "stale_test_alert",
            "completed_at": datetime.now().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts,
        }


def create_index_maintainer_crew_config() -> dict[str, Any]:
    """
    Generate CrewAI crew configuration for index maintenance.

    This crew can be instantiated to automatically maintain the index.
    """
    return {
        "name": "Project Index Maintainer Crew",
        "description": "Maintains the project index for code intelligence",
        "agents": [
            {
                "name": "Index Scanner Agent",
                "role": "File Discovery and Analysis",
                "goal": "Keep the project index accurate and up-to-date",
                "backstory": (
                    "You are responsible for scanning the codebase and maintaining "
                    "accurate metadata about every file. You track which files need "
                    "tests, which tests are stale, and overall project health."
                ),
                "tools": ["refresh_index", "query_project_index", "get_file_info"],
            },
            {
                "name": "Test Gap Analyst Agent",
                "role": "Test Coverage Analysis",
                "goal": "Identify and prioritize files needing tests",
                "backstory": (
                    "You analyze test coverage and identify the most critical "
                    "gaps. You prioritize files by impact score and recommend "
                    "which files to test first for maximum value."
                ),
                "tools": ["query_project_index", "generate_report", "get_project_summary"],
            },
            {
                "name": "Report Generator Agent",
                "role": "Project Health Reporting",
                "goal": "Generate actionable reports for project management",
                "backstory": (
                    "You create comprehensive reports about project health, "
                    "test coverage, and areas needing attention. Your reports "
                    "help teams prioritize work and track progress."
                ),
                "tools": ["generate_report", "get_project_summary"],
            },
        ],
        "tasks": [
            {
                "name": "daily_index_refresh",
                "description": "Refresh the project index daily",
                "agent": "Index Scanner Agent",
                "schedule": "daily",
            },
            {
                "name": "weekly_test_gap_analysis",
                "description": "Analyze test gaps and prioritize opportunities",
                "agent": "Test Gap Analyst Agent",
                "schedule": "weekly",
            },
            {
                "name": "weekly_health_report",
                "description": "Generate weekly project health report",
                "agent": "Report Generator Agent",
                "schedule": "weekly",
            },
        ],
    }


def integrate_with_workflow(index: ProjectIndex, workflow_name: str) -> dict[str, Any]:
    """
    Get index context for a specific workflow.

    Workflows can call this to get relevant index data.
    """
    return index.get_context_for_workflow(workflow_name)


class IndexEventHooks:
    """
    Event hooks for automatic index updates.

    Can be triggered by CI/CD, git hooks, or file watchers.
    """

    def __init__(self, index: ProjectIndex):
        self.index = index
        self.callbacks: dict[str, list[Callable]] = {
            "on_file_changed": [],
            "on_test_run_complete": [],
            "on_commit": [],
        }

    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for an event."""
        if event in self.callbacks:
            self.callbacks[event].append(callback)

    def on_file_changed(self, file_path: str) -> None:
        """
        Called when a file is modified.

        Can be triggered by file watcher or git hook.
        """
        # Update the specific file record
        record = self.index.get_file(file_path)
        if record:
            self.index.update_file(file_path, last_modified=datetime.now())

            # Check if this file has tests that might now be stale
            if record.test_file_path:
                self.index.update_file(
                    file_path,
                    is_stale=True,
                )

        # Trigger callbacks
        for callback in self.callbacks["on_file_changed"]:
            callback(file_path)

    def on_test_run_complete(self, coverage_xml_path: str | None = None) -> None:
        """
        Called after a test run completes.

        Updates coverage data if provided.
        """
        if coverage_xml_path:
            tasks = IndexMaintenanceTasks(self.index)
            tasks.coverage_sync(coverage_xml_path)

        # Trigger callbacks
        for callback in self.callbacks["on_test_run_complete"]:
            callback(coverage_xml_path)

    def on_commit(self, changed_files: list[str]) -> None:
        """
        Called after a git commit.

        Updates index for changed files.
        """
        for file_path in changed_files:
            self.on_file_changed(file_path)

        # Trigger callbacks
        for callback in self.callbacks["on_commit"]:
            callback(changed_files)
