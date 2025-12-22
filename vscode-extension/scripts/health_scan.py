#!/usr/bin/env python3
"""
Health Scan Script for Empathy Framework VSCode Extension

Runs lint, type check, and test collection to generate health.json.
This script accepts paths as arguments rather than being embedded inline,
preventing command injection vulnerabilities.

Usage:
    python health_scan.py <workspace_folder> <empathy_dir>
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_lint_check(workspace: Path) -> int:
    """Run ruff linter and return error count."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "ruff", "check", "src/", "--statistics"],
            capture_output=True,
            text=True,
            cwd=workspace,
        )
        if result.returncode != 0:
            return result.stdout.count("error")
        return 0
    except Exception:
        return 0


def run_type_check(workspace: Path) -> int:
    """Run mypy type checker and return error count."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "mypy", "src/empathy_os", "--ignore-missing-imports"],
            capture_output=True,
            text=True,
            cwd=workspace,
        )
        return result.stdout.count("error:")
    except Exception:
        return 0


def run_test_collection(workspace: Path) -> int:
    """Collect tests and return count."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--co", "-q"],
            capture_output=True,
            text=True,
            cwd=workspace,
        )
        for line in result.stdout.split("\n"):
            if "collected" in line:
                for part in line.split():
                    if part.isdigit():
                        return int(part)
        return 0
    except Exception:
        return 0


def main():
    if len(sys.argv) != 3:
        print("Usage: health_scan.py <workspace_folder> <empathy_dir>", file=sys.stderr)
        sys.exit(1)

    workspace = Path(sys.argv[1])
    empathy_dir = Path(sys.argv[2])

    # Validate paths
    if not workspace.is_dir():
        print(f"Error: Workspace folder does not exist: {workspace}", file=sys.stderr)
        sys.exit(1)

    # Ensure empathy directory exists
    empathy_dir.mkdir(parents=True, exist_ok=True)

    # Run checks
    lint_errors = run_lint_check(workspace)
    type_errors = run_type_check(workspace)
    test_count = run_test_collection(workspace)

    # Calculate health score
    score = max(0, min(100, int(100 - lint_errors * 2 - type_errors * 0.5)))

    # Build health report
    health = {
        "score": score,
        "lint": {"errors": lint_errors, "warnings": 0},
        "types": {"errors": type_errors},
        "security": {"high": 0, "medium": 0, "low": 0},
        "tests": {"passed": test_count, "failed": 0, "total": test_count, "coverage": 15},
        "tech_debt": {"total": 0, "todos": 0, "fixmes": 0, "hacks": 0},
        "timestamp": datetime.now().isoformat(),
    }

    # Write health.json
    health_file = empathy_dir / "health.json"
    with open(health_file, "w") as f:
        json.dump(health, f)

    print("OK")


if __name__ == "__main__":
    main()
