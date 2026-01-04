"""CLI for Project Index

Commands for generating, querying, and reporting on the project index.

Usage:
    python -m empathy_os.project_index.cli refresh
    python -m empathy_os.project_index.cli report health
    python -m empathy_os.project_index.cli query needing_tests
    python -m empathy_os.project_index.cli summary

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import json
import sys
from pathlib import Path

from .index import ProjectIndex
from .reports import ReportGenerator


def main() -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Project Index - Codebase Intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Generate/refresh the index
    python -m empathy_os.project_index.cli refresh

    # View project summary
    python -m empathy_os.project_index.cli summary

    # Generate health report
    python -m empathy_os.project_index.cli report health

    # Find files needing tests
    python -m empathy_os.project_index.cli query needing_tests

    # Find stale test files
    python -m empathy_os.project_index.cli query stale
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

    # refresh command
    refresh_parser = subparsers.add_parser("refresh", help="Refresh the project index")
    refresh_parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        help="Force full re-scan even if index exists",
    )

    # summary command
    subparsers.add_parser("summary", help="Show project summary")

    # report command
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument(
        "report_type",
        choices=["health", "test_gap", "staleness", "coverage", "sprint"],
        help="Type of report to generate",
    )
    report_parser.add_argument(
        "--markdown",
        "-m",
        action="store_true",
        help="Output in markdown format",
    )

    # query command
    query_parser = subparsers.add_parser("query", help="Query the index")
    query_parser.add_argument(
        "query_type",
        choices=["needing_tests", "stale", "high_impact", "attention", "all"],
        help="Type of query",
    )
    query_parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=20,
        help="Maximum number of results",
    )

    # file command
    file_parser = subparsers.add_parser("file", help="Get info about a specific file")
    file_parser.add_argument("path", help="Path to the file")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Initialize index
    project_root = Path(args.project).resolve()
    index = ProjectIndex(str(project_root))

    # Execute command
    if args.command == "refresh":
        return cmd_refresh(index, args)
    if args.command == "summary":
        return cmd_summary(index, args)
    if args.command == "report":
        return cmd_report(index, args)
    if args.command == "query":
        return cmd_query(index, args)
    if args.command == "file":
        return cmd_file(index, args)

    return 0


def cmd_refresh(index: ProjectIndex, args: argparse.Namespace) -> int:
    """Refresh the index."""
    print(f"Refreshing index for: {index.project_root}")
    print()

    index.refresh()

    summary = index.get_summary()

    print("Index refreshed successfully!")
    print(f"  Files indexed: {summary.total_files}")
    print(f"  Source files: {summary.source_files}")
    print(f"  Test files: {summary.test_files}")
    print(f"  Files needing tests: {summary.files_without_tests}")
    print(f"  Files needing attention: {summary.files_needing_attention}")
    print()
    print(f"Index saved to: {index._index_path}")

    return 0


def cmd_summary(index: ProjectIndex, args: argparse.Namespace) -> int:
    """Show project summary."""
    if not index.load():
        print("No index found. Run 'refresh' first.")
        return 1

    summary = index.get_summary()

    if args.json:
        print(json.dumps(summary.to_dict(), indent=2))
        return 0

    print("=" * 60)
    print("PROJECT INDEX SUMMARY")
    print("=" * 60)
    print()
    print("FILE COUNTS")
    print(f"  Total files:     {summary.total_files}")
    print(f"  Source files:    {summary.source_files}")
    print(f"  Test files:      {summary.test_files}")
    print(f"  Config files:    {summary.config_files}")
    print(f"  Doc files:       {summary.doc_files}")
    print()
    print("TEST HEALTH")
    print(f"  Files requiring tests: {summary.files_requiring_tests}")
    print(f"  Files with tests:      {summary.files_with_tests}")
    print(f"  Files WITHOUT tests:   {summary.files_without_tests}")
    print(f"  Average coverage:      {summary.test_coverage_avg:.1f}%")
    print(f"  Test-to-code ratio:    {summary.test_to_code_ratio:.2f}")
    print()
    print("ATTENTION NEEDED")
    print(f"  Stale test count:      {summary.stale_file_count}")
    print(f"  Files need attention:  {summary.files_needing_attention}")
    print()

    if summary.critical_untested_files:
        print("CRITICAL UNTESTED FILES (high impact)")
        for f in summary.critical_untested_files[:5]:
            print(f"  - {f}")
        print()

    return 0


def cmd_report(index: ProjectIndex, args: argparse.Namespace) -> int:
    """Generate a report."""
    if not index.load():
        print("No index found. Run 'refresh' first.")
        return 1

    generator = ReportGenerator(index.get_summary(), index.get_all_files())

    report_type = args.report_type
    if report_type == "sprint":
        report_type = "sprint_planning"

    # Generate report
    if args.markdown:
        print(generator.to_markdown(report_type))
    elif args.json:
        if report_type == "health":
            print(json.dumps(generator.health_report(), indent=2))
        elif report_type == "test_gap":
            print(json.dumps(generator.test_gap_report(), indent=2))
        elif report_type == "staleness":
            print(json.dumps(generator.staleness_report(), indent=2))
        elif report_type == "coverage":
            print(json.dumps(generator.coverage_report(), indent=2))
        elif report_type == "sprint_planning":
            print(json.dumps(generator.sprint_planning_report(), indent=2))
    else:
        # Human-readable format
        print(generator.to_markdown(report_type))

    return 0


def cmd_query(index: ProjectIndex, args: argparse.Namespace) -> int:
    """Query the index."""
    if not index.load():
        print("No index found. Run 'refresh' first.")
        return 1

    query_type = args.query_type
    limit = args.limit

    # Execute query
    if query_type == "needing_tests":
        files = index.get_files_needing_tests()[:limit]
        title = "FILES NEEDING TESTS"
    elif query_type == "stale":
        files = index.get_stale_files()[:limit]
        title = "STALE TEST FILES"
    elif query_type == "high_impact":
        files = index.get_high_impact_files()[:limit]
        title = "HIGH IMPACT FILES"
    elif query_type == "attention":
        files = index.get_files_needing_attention()[:limit]
        title = "FILES NEEDING ATTENTION"
    elif query_type == "all":
        files = index.get_all_files()[:limit]
        title = "ALL FILES"
    else:
        files = []
        title = "RESULTS"

    if args.json:
        print(json.dumps([f.to_dict() for f in files], indent=2))
        return 0

    print(f"\n{title} ({len(files)} results)")
    print("=" * 60)

    for f in files:
        print(f"\n{f.path}")
        print(f"  Category: {f.category.value}")
        print(f"  Impact Score: {f.impact_score:.1f}")
        print(f"  Has Tests: {f.tests_exist}")
        print(f"  Coverage: {f.coverage_percent:.1f}%")
        if f.is_stale:
            print(f"  STALE: {f.staleness_days} days")
        if f.attention_reasons:
            print(f"  Attention: {', '.join(f.attention_reasons)}")

    print()
    return 0


def cmd_file(index: ProjectIndex, args: argparse.Namespace) -> int:
    """Get info about a specific file."""
    if not index.load():
        print("No index found. Run 'refresh' first.")
        return 1

    record = index.get_file(args.path)

    if not record:
        print(f"File not found in index: {args.path}")
        return 1

    if args.json:
        print(json.dumps(record.to_dict(), indent=2))
        return 0

    print(f"\nFILE: {record.path}")
    print("=" * 60)
    print(f"  Name:         {record.name}")
    print(f"  Category:     {record.category.value}")
    print(f"  Language:     {record.language}")
    print()
    print("TESTING")
    print(f"  Requires Tests: {record.test_requirement.value}")
    print(f"  Has Tests:      {record.tests_exist}")
    print(f"  Test File:      {record.test_file_path or 'None'}")
    print(f"  Coverage:       {record.coverage_percent:.1f}%")
    print(f"  Test Count:     {record.test_count}")
    print()
    print("METRICS")
    print(f"  Lines of Code:  {record.lines_of_code}")
    print(f"  Complexity:     {record.complexity_score:.1f}")
    print(f"  Has Docstrings: {record.has_docstrings}")
    print(f"  Has Type Hints: {record.has_type_hints}")
    print()
    print("DEPENDENCIES")
    print(f"  Imports:        {record.import_count} modules")
    print(f"  Imported By:    {record.imported_by_count} files")
    print(f"  Impact Score:   {record.impact_score:.1f}")
    print()
    print("STATUS")
    print(f"  Needs Attention: {record.needs_attention}")
    if record.attention_reasons:
        print(f"  Reasons:         {', '.join(record.attention_reasons)}")
    if record.is_stale:
        print(f"  STALE:           {record.staleness_days} days")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
