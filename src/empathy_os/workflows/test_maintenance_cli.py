"""
CLI for Test Maintenance Workflow

Commands for managing the test lifecycle:
- analyze: Generate maintenance plan
- execute: Execute plan items
- auto: Auto-execute eligible items
- report: Generate test health report
- queue: Manage task queue
- crew: Run the test maintenance crew

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

from ..project_index import ProjectIndex
from .test_lifecycle import TestLifecycleManager
from .test_maintenance import TestMaintenanceWorkflow
from .test_maintenance_crew import CrewConfig, TestMaintenanceCrew


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Test Maintenance - Automatic Test Lifecycle Management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Analyze test coverage and generate plan
    python -m empathy_os.workflows.test_maintenance_cli analyze

    # Auto-execute eligible test generation
    python -m empathy_os.workflows.test_maintenance_cli auto

    # Run the full maintenance crew
    python -m empathy_os.workflows.test_maintenance_cli crew --mode full

    # View task queue
    python -m empathy_os.workflows.test_maintenance_cli queue list

    # Process git hook
    python -m empathy_os.workflows.test_maintenance_cli hook post-commit
        """,
    )

    parser.add_argument(
        "--project",
        "-p",
        default=".",
        help="Project root directory (default: current directory)",
    )

    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output in JSON format",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze and generate plan")
    analyze_parser.add_argument(
        "--max-items",
        type=int,
        default=20,
        help="Maximum items in plan",
    )

    # execute command
    execute_parser = subparsers.add_parser("execute", help="Execute plan items")
    execute_parser.add_argument(
        "--action",
        choices=["create", "update", "review", "delete"],
        help="Only execute items of this action type",
    )
    execute_parser.add_argument(
        "--priority",
        choices=["critical", "high", "medium", "low"],
        help="Only execute items of this priority or higher",
    )
    execute_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually execute, just show what would be done",
    )

    # auto command
    auto_parser = subparsers.add_parser("auto", help="Auto-execute eligible items")
    auto_parser.add_argument(
        "--max-items",
        type=int,
        default=10,
        help="Maximum items to process",
    )
    auto_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't actually execute",
    )

    # report command
    report_parser = subparsers.add_parser("report", help="Generate test health report")
    report_parser.add_argument(
        "--type",
        choices=["health", "gaps", "staleness", "all"],
        default="all",
        help="Type of report",
    )
    report_parser.add_argument(
        "--markdown",
        "-m",
        action="store_true",
        help="Output in markdown format",
    )

    # queue command
    queue_parser = subparsers.add_parser("queue", help="Manage task queue")
    queue_subparsers = queue_parser.add_subparsers(dest="queue_action")

    queue_subparsers.add_parser("list", help="List queued tasks")
    queue_subparsers.add_parser("status", help="Show queue status")
    queue_subparsers.add_parser("clear", help="Clear the queue")

    queue_process = queue_subparsers.add_parser("process", help="Process queue")
    queue_process.add_argument("--max", type=int, default=10, help="Max tasks to process")

    # crew command
    crew_parser = subparsers.add_parser("crew", help="Run test maintenance crew")
    crew_parser.add_argument(
        "--mode",
        choices=["full", "analyze", "generate", "validate", "validate-only", "report"],
        default="analyze",
        help="Crew operation mode",
    )
    crew_parser.add_argument(
        "--files",
        nargs="*",
        help="Test files for validate-only mode",
    )
    crew_parser.add_argument(
        "--validation-optional",
        action="store_true",
        default=True,
        help="Continue if validation fails (default: True)",
    )
    crew_parser.add_argument(
        "--validation-timeout",
        type=int,
        default=120,
        help="Timeout per test file in seconds (default: 120)",
    )

    # hook command
    hook_parser = subparsers.add_parser("hook", help="Process git hooks")
    hook_parser.add_argument(
        "hook_type",
        choices=["pre-commit", "post-commit"],
        help="Type of hook",
    )
    hook_parser.add_argument(
        "--files",
        nargs="*",
        help="Files involved in the hook",
    )

    # status command
    subparsers.add_parser("status", help="Show test maintenance status")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Run appropriate command
    if args.command == "analyze":
        return asyncio.run(cmd_analyze(args))
    elif args.command == "execute":
        return asyncio.run(cmd_execute(args))
    elif args.command == "auto":
        return asyncio.run(cmd_auto(args))
    elif args.command == "report":
        return asyncio.run(cmd_report(args))
    elif args.command == "queue":
        return asyncio.run(cmd_queue(args))
    elif args.command == "crew":
        return asyncio.run(cmd_crew(args))
    elif args.command == "hook":
        return asyncio.run(cmd_hook(args))
    elif args.command == "status":
        return asyncio.run(cmd_status(args))

    return 0


async def cmd_analyze(args: argparse.Namespace) -> int:
    """Run analysis and generate plan."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    workflow = TestMaintenanceWorkflow(str(project_root), index)
    result = await workflow.run(
        {
            "mode": "analyze",
            "max_items": args.max_items,
        }
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_plan(result)

    return 0


async def cmd_execute(args: argparse.Namespace) -> int:
    """Execute plan items."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    workflow = TestMaintenanceWorkflow(str(project_root), index)
    result = await workflow.run(
        {
            "mode": "execute",
            "dry_run": args.dry_run,
        }
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_execution_result(result)

    return 0


async def cmd_auto(args: argparse.Namespace) -> int:
    """Auto-execute eligible items."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    workflow = TestMaintenanceWorkflow(str(project_root), index)
    result = await workflow.run(
        {
            "mode": "auto",
            "max_items": args.max_items,
            "dry_run": args.dry_run,
        }
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if args.dry_run:
            print("DRY RUN - No changes made")
        _print_execution_result(result)

    return 0


async def cmd_report(args: argparse.Namespace) -> int:
    """Generate test health report."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    workflow = TestMaintenanceWorkflow(str(project_root), index)
    result = await workflow.run({"mode": "report"})

    if args.json:
        print(json.dumps(result.get("report", {}), indent=2))
    else:
        _print_report(result.get("report", {}), args.type, args.markdown)

    return 0


async def cmd_queue(args: argparse.Namespace) -> int:
    """Manage task queue."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    manager = TestLifecycleManager(str(project_root), index)

    if args.queue_action == "list":
        queue = manager.get_queue()
        if args.json:
            print(json.dumps(queue, indent=2))
        else:
            _print_queue(queue)

    elif args.queue_action == "status":
        status = manager.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            _print_queue_status(status)

    elif args.queue_action == "clear":
        count = manager.clear_queue()
        print(f"Cleared {count} tasks from queue")

    elif args.queue_action == "process":
        result = await manager.process_queue(max_tasks=args.max)
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Processed {result['processed']} tasks")
            print(f"  Succeeded: {result['succeeded']}")
            print(f"  Failed: {result['failed']}")

    return 0


async def cmd_crew(args: argparse.Namespace) -> int:
    """Run test maintenance crew."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    # Configure with CLI options
    config = CrewConfig(
        validation_optional=getattr(args, "validation_optional", True),
        validation_timeout_seconds=getattr(args, "validation_timeout", 120),
    )
    crew = TestMaintenanceCrew(str(project_root), index, config)

    print(f"Starting Test Maintenance Crew in {args.mode} mode...")
    print("=" * 60)

    # Handle validate-only mode
    test_files = getattr(args, "files", None)
    if args.mode == "validate-only" and not test_files:
        print("ERROR: validate-only mode requires --files argument")
        return 1

    result = await crew.run(args.mode, test_files=test_files)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        _print_crew_result(result)

    return 0 if result.get("success") else 1


async def cmd_hook(args: argparse.Namespace) -> int:
    """Process git hooks."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    manager = TestLifecycleManager(str(project_root), index)

    files = args.files or []

    if args.hook_type == "pre-commit":
        result = await manager.process_git_pre_commit(files)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            if result.get("blocking"):
                print("COMMIT BLOCKED")
                print("=" * 40)
                for item in result["blocking"]:
                    print(f"  {item['file']}: {item['reason']}")
                return 1
            elif result.get("warnings"):
                print("COMMIT ALLOWED (with warnings)")
                print("=" * 40)
                for item in result["warnings"]:
                    print(f"  WARNING: {item['file']}: {item['reason']}")

    elif args.hook_type == "post-commit":
        result = await manager.process_git_post_commit(files)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Processed {result['changed_files']} changed files")
            print(f"Queued {result['tasks_queued']} test tasks")

    return 0


async def cmd_status(args: argparse.Namespace) -> int:
    """Show test maintenance status."""
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))
    if not index.load():
        index.refresh()

    workflow = TestMaintenanceWorkflow(str(project_root), index)
    manager = TestLifecycleManager(str(project_root), index)

    health = workflow.get_test_health_summary()
    queue_status = manager.get_status()

    if args.json:
        print(
            json.dumps(
                {
                    "health": health,
                    "queue": queue_status,
                },
                indent=2,
            )
        )
    else:
        print("TEST MAINTENANCE STATUS")
        print("=" * 60)
        print()
        print("TEST HEALTH")
        print(f"  Files requiring tests: {health['files_requiring_tests']}")
        print(f"  Files WITH tests:      {health['files_with_tests']}")
        print(f"  Files WITHOUT tests:   {health['files_without_tests']}")
        print(f"  Average coverage:      {health['coverage_avg']:.1f}%")
        print(f"  Stale tests:           {health['stale_count']}")
        print()
        print("TASK QUEUE")
        print(f"  Pending tasks:         {queue_status['pending']}")
        print(f"  Running tasks:         {queue_status['running']}")
        print(f"  Auto-execute:          {queue_status['auto_execute']}")
        print()

    return 0


# ===== Output Formatting =====


def _print_plan(result: dict) -> None:
    """Print maintenance plan."""
    plan = result.get("plan", {})
    summary = plan.get("summary", {})
    items = plan.get("items", [])
    options = plan.get("options", [])

    print("TEST MAINTENANCE PLAN")
    print("=" * 60)
    print()

    print("SUMMARY")
    print(f"  Total items:       {summary.get('total_items', 0)}")
    print(f"  Auto-executable:   {summary.get('auto_executable', 0)}")
    print(f"  Manual required:   {summary.get('manual_required', 0)}")
    print()

    print("BY ACTION")
    for action, count in summary.get("by_action", {}).items():
        if count > 0:
            print(f"  {action}: {count}")
    print()

    print("BY PRIORITY")
    for priority, count in summary.get("by_priority", {}).items():
        if count > 0:
            print(f"  {priority}: {count}")
    print()

    if items:
        print("PLAN ITEMS")
        print("-" * 60)
        for i, item in enumerate(items[:10], 1):
            auto = "[AUTO]" if item.get("auto_executable") else "[MANUAL]"
            print(f"{i}. {auto} [{item['priority']}] {item['file_path']}")
            print(f"   Action: {item['action']} - {item['reason']}")
            print(f"   Effort: {item.get('estimated_effort', 'unknown')}")
            print()

    if options:
        print("EXECUTION OPTIONS")
        print("-" * 60)
        for opt in options:
            print(f"  {opt['name']}")
            print(f"    {opt['description']}")
            print(f"    Command: {opt.get('command', 'N/A')}")
            print()


def _print_execution_result(result: dict) -> None:
    """Print execution result."""
    execution = result.get("execution", {})

    print("EXECUTION RESULT")
    print("=" * 60)
    print(f"  Total:     {execution.get('total', 0)}")
    print(f"  Succeeded: {execution.get('succeeded', 0)}")
    print(f"  Failed:    {execution.get('failed', 0)}")
    print(f"  Skipped:   {execution.get('skipped', 0)}")
    print()

    details = execution.get("details", [])
    if details:
        print("DETAILS")
        for item in details[:10]:
            status = "OK" if item.get("success") else "FAILED"
            print(f"  [{status}] {item['file']} - {item['action']}")


def _print_report(report: dict, report_type: str, markdown: bool) -> None:
    """Print test health report."""
    if report_type in ["all", "health"]:
        health = report.get("health", {})
        print("TEST HEALTH REPORT")
        print("=" * 60)
        print(
            f"  Health Score: {health.get('health_score', 0):.1f}/100 ({health.get('health_grade', 'N/A')})"
        )
        print()

        for concern in health.get("concerns", []):
            print(f"  CONCERN: {concern}")
        print()

        for action in health.get("action_items", []):
            print(f"  [{action['priority'].upper()}] {action['action']}")


def _print_queue(queue: list) -> None:
    """Print task queue."""
    if not queue:
        print("Queue is empty")
        return

    print("TASK QUEUE")
    print("=" * 60)
    for task in queue:
        print(f"  [{task['priority']}] {task['file_path']}")
        print(f"    Action: {task['action']}, Status: {task['status']}")
        print()


def _print_queue_status(status: dict) -> None:
    """Print queue status."""
    print("QUEUE STATUS")
    print("=" * 60)
    print(f"  Queue size:   {status['queue_size']}")
    print(f"  Pending:      {status['pending']}")
    print(f"  Running:      {status['running']}")
    print(f"  Auto-execute: {status['auto_execute']}")
    print()
    print("By Priority:")
    for priority, count in status.get("by_priority", {}).items():
        if count > 0:
            print(f"  {priority}: {count}")


def _print_crew_result(result: dict) -> None:
    """Print crew execution result."""
    summary = result.get("summary", {})

    print()
    print("CREW EXECUTION COMPLETE")
    print("=" * 60)
    print(f"  Mode:             {result.get('mode')}")
    print(f"  Success:          {result.get('success')}")
    print(f"  Agents executed:  {summary.get('agents_executed', 0)}")
    print(f"  Agents succeeded: {summary.get('agents_succeeded', 0)}")
    print(f"  Total duration:   {summary.get('total_duration_ms', 0)}ms")
    print()

    if summary.get("agent_results"):
        print("AGENT RESULTS")
        for agent in summary["agent_results"]:
            status = "OK" if agent["success"] else "FAILED"
            print(f"  [{status}] {agent['agent']}: {agent['task']} ({agent['duration_ms']}ms)")


if __name__ == "__main__":
    sys.exit(main())
