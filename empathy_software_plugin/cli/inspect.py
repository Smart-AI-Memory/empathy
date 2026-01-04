"""Code Inspection CLI

Command-line interface for the Code Inspection Agent Pipeline.

Usage:
    empathy-inspect [path] [options]

Examples:
    empathy-inspect .                    # Inspect current directory
    empathy-inspect ./src --parallel     # Parallel mode
    empathy-inspect . --format json      # JSON output
    empathy-inspect . --staged           # Only staged changes
    empathy-inspect . --fix              # Auto-fix safe issues

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9

"""

import argparse
import asyncio
import sys
from pathlib import Path


async def run_auto_fix(project_path: str, verbose: bool = False) -> int:
    """Run auto-fix using ruff.

    Args:
        project_path: Path to project to fix
        verbose: Whether to show verbose output

    Returns:
        Number of issues fixed

    """
    import subprocess

    fixed_count = 0

    # Run ruff check with --fix
    try:
        print("\nRunning ruff --fix...")
        result = subprocess.run(
            ["ruff", "check", project_path, "--fix", "--exit-zero"],
            check=False,
            capture_output=True,
            text=True,
        )

        if verbose and result.stdout:
            print(result.stdout)

        # Count fixes from output
        if "Fixed" in result.stdout:
            # Parse "Fixed X errors" or similar
            import re

            match = re.search(r"Fixed (\d+)", result.stdout)
            if match:
                fixed_count += int(match.group(1))

    except FileNotFoundError:
        print("Warning: ruff not found. Install with: pip install ruff")
    except Exception as e:
        print(f"Warning: ruff fix failed: {e}")

    # Run ruff format for formatting fixes
    try:
        print("Running ruff format...")
        result = subprocess.run(
            ["ruff", "format", project_path],
            check=False,
            capture_output=True,
            text=True,
        )

        if verbose and result.stdout:
            print(result.stdout)

        # Count formatted files
        if "file" in result.stderr.lower():
            import re

            match = re.search(r"(\d+) file", result.stderr)
            if match:
                fixed_count += int(match.group(1))

    except FileNotFoundError:
        pass  # Already warned above
    except Exception as e:
        if verbose:
            print(f"Warning: ruff format failed: {e}")

    # Run isort for import sorting
    try:
        print("Running isort...")
        result = subprocess.run(
            ["isort", project_path, "--profile", "black"],
            check=False,
            capture_output=True,
            text=True,
        )

        if verbose and result.stdout:
            print(result.stdout)

        # isort shows "Fixing" for each file
        if "Fixing" in result.stdout:
            fixed_count += result.stdout.count("Fixing")

    except FileNotFoundError:
        if verbose:
            print("Note: isort not found. Install with: pip install isort")
    except Exception as e:
        if verbose:
            print(f"Warning: isort failed: {e}")

    return fixed_count


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="empathy-inspect",
        description="Code Inspection Agent Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  empathy-inspect .                    Inspect current directory
  empathy-inspect ./src --parallel     Run static checks in parallel
  empathy-inspect . --format json      Output as JSON
  empathy-inspect . --staged           Inspect staged git changes only
  empathy-inspect . --quick            Quick mode (skip slow checks)
        """,
    )

    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to inspect (default: current directory)",
    )

    parser.add_argument(
        "--parallel",
        action="store_true",
        default=True,
        help="Run Phase 1 tools in parallel (default: True)",
    )

    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel execution",
    )

    parser.add_argument(
        "--learning",
        action="store_true",
        default=True,
        help="Enable pattern learning (default: True)",
    )

    parser.add_argument(
        "--no-learning",
        action="store_true",
        help="Disable pattern learning",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["terminal", "json", "markdown", "sarif", "html"],
        default="terminal",
        help="Output format (default: terminal). Use 'sarif' for GitHub Actions.",
    )

    parser.add_argument(
        "--staged",
        action="store_true",
        help="Only inspect staged git changes",
    )

    parser.add_argument(
        "--changed",
        action="store_true",
        help="Only inspect changed files (vs HEAD)",
    )

    parser.add_argument(
        "--quick",
        "-q",
        action="store_true",
        help="Quick mode (skip slow checks like deep debugging)",
    )

    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix safe issues (formatting, imports)",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        help="Write report to file",
    )

    parser.add_argument(
        "--exclude",
        "-e",
        type=str,
        action="append",
        default=[],
        help="Glob patterns to exclude (can be used multiple times)",
    )

    # Baseline/suppression options
    parser.add_argument(
        "--no-baseline",
        action="store_true",
        help="Disable baseline filtering (show all findings)",
    )

    parser.add_argument(
        "--baseline-init",
        action="store_true",
        help="Create an empty .empathy-baseline.json file",
    )

    parser.add_argument(
        "--baseline-cleanup",
        action="store_true",
        help="Remove expired suppressions from baseline",
    )

    return parser.parse_args()


async def run_inspection(args: argparse.Namespace) -> int:
    """Run the inspection and return exit code."""
    # Import here to avoid slow startup
    from agents.code_inspection import CodeInspectionAgent

    # Resolve path
    project_path = str(Path(args.path).resolve())

    # Determine target mode
    if args.staged:
        target_mode = "staged"
    elif args.changed:
        target_mode = "changed"
    else:
        target_mode = "all"

    # Create agent
    agent = CodeInspectionAgent(
        parallel_mode=args.parallel and not args.no_parallel,
        learning_enabled=args.learning and not args.no_learning,
        baseline_enabled=not args.no_baseline,
    )

    # Configure verbose logging
    if args.verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)

    # Run inspection
    state = await agent.inspect(
        project_path=project_path,
        target_mode=target_mode,
        exclude_patterns=args.exclude if args.exclude else None,
    )

    # Format report
    report = agent.format_report(state, args.format)

    # Output
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(report)
        print(f"Report written to {output_path}")
    else:
        print(report)

    # Auto-fix if requested
    if args.fix:
        fixed_count = await run_auto_fix(project_path, args.verbose)
        if fixed_count > 0:
            print(f"\nAuto-fixed {fixed_count} issues. Run inspection again to verify.")

    # Return exit code based on health status
    if state["health_status"] == "fail":
        return 1
    if state["health_status"] == "warn":
        return 0  # Warn but don't fail
    return 0


def handle_baseline_commands(args: argparse.Namespace) -> bool:
    """Handle baseline-specific commands.

    Returns:
        True if a baseline command was handled (and should exit)

    """
    from agents.code_inspection.baseline import BaselineManager, create_baseline_file

    project_path = str(Path(args.path).resolve())

    if args.baseline_init:
        baseline_path = create_baseline_file(project_path)
        print(f"Created baseline file: {baseline_path}")
        return True

    if args.baseline_cleanup:
        manager = BaselineManager(project_path)
        if manager.load():
            removed = manager.cleanup_expired()
            print(f"Removed {removed} expired suppressions")
        else:
            print("No baseline file found")
        return True

    return False


def main():
    """Main entry point for CLI."""
    args = parse_args()

    try:
        # Handle baseline commands first
        if handle_baseline_commands(args):
            sys.exit(0)

        exit_code = asyncio.run(run_inspection(args))
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nInspection cancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
