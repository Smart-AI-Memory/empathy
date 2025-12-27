#!/usr/bin/env python3
"""
Cross-Platform Compatibility Checker for Empathy Framework

Scans the codebase for common cross-platform issues:
- Hardcoded Unix paths (/var/log, /tmp, etc.)
- open() calls without encoding specified
- asyncio.run() without setup_asyncio_policy()
- os.path operations that should use pathlib

Usage:
    python scripts/check_platform_compat.py [--fix] [--strict]

Options:
    --fix       Show suggested fixes (doesn't modify files)
    --strict    Exit with error code if issues found
    --json      Output results as JSON

Can be integrated into CI:
    - Run as pre-commit hook
    - Add to GitHub Actions workflow
    - Run as part of pytest

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Issue:
    """Represents a cross-platform compatibility issue."""

    file: str
    line: int
    category: str
    message: str
    severity: str  # "error", "warning", "info"
    suggestion: str = ""


@dataclass
class ScanResult:
    """Results of a compatibility scan."""

    issues: list[Issue] = field(default_factory=list)
    files_scanned: int = 0
    errors: int = 0
    warnings: int = 0
    info: int = 0

    def add_issue(self, issue: Issue) -> None:
        """Add an issue and update counts."""
        self.issues.append(issue)
        if issue.severity == "error":
            self.errors += 1
        elif issue.severity == "warning":
            self.warnings += 1
        else:
            self.info += 1


# Patterns to detect
HARDCODED_PATHS = [
    (r'["\']\/var\/log\/', "Hardcoded /var/log path"),
    (r'["\']\/tmp\/', "Hardcoded /tmp path"),
    (r'["\']\/etc\/', "Hardcoded /etc path"),
    (r'["\']\/home\/', "Hardcoded /home path"),
    (r'["\']~\/', "Hardcoded home directory path"),
]

OPEN_WITHOUT_ENCODING = re.compile(
    r"\bopen\s*\([^)]*\)\s*(?:as\s+\w+)?(?!\s*#.*encoding)", re.MULTILINE
)

ASYNCIO_RUN = re.compile(r"\basyncio\.run\s*\(")

OS_PATH_OPERATIONS = [
    (r"\bos\.path\.join\s*\(", "Consider using pathlib.Path instead of os.path.join"),
    (r"\bos\.path\.exists\s*\(", "Consider using Path.exists() instead"),
    (r"\bos\.path\.dirname\s*\(", "Consider using Path.parent instead"),
    (r"\bos\.path\.basename\s*\(", "Consider using Path.name instead"),
]


def scan_file(filepath: Path, result: ScanResult) -> None:
    """Scan a single Python file for compatibility issues."""
    try:
        content = filepath.read_text(encoding="utf-8")
        lines = content.split("\n")
        relative_path = str(filepath)

        # Check for hardcoded paths
        for line_num, line in enumerate(lines, 1):
            for pattern, message in HARDCODED_PATHS:
                if re.search(pattern, line):
                    result.add_issue(
                        Issue(
                            file=relative_path,
                            line=line_num,
                            category="hardcoded_path",
                            message=message,
                            severity="warning",
                            suggestion="Use empathy_os.platform_utils for platform-appropriate paths",
                        )
                    )

        # Check for open() without encoding
        for line_num, line in enumerate(lines, 1):
            if "open(" in line and "encoding" not in line:
                # Skip binary mode opens
                if "'rb'" in line or '"rb"' in line or "'wb'" in line or '"wb"' in line:
                    continue
                # Skip if it's a comment
                if line.strip().startswith("#"):
                    continue
                # Check if it's a text mode open
                if (
                    "'r'" in line
                    or '"r"' in line
                    or "'w'" in line
                    or '"w"' in line
                    or "'a'" in line
                    or '"a"' in line
                ):
                    result.add_issue(
                        Issue(
                            file=relative_path,
                            line=line_num,
                            category="missing_encoding",
                            message="open() without encoding specified",
                            severity="warning",
                            suggestion='Add encoding="utf-8" parameter',
                        )
                    )

        # Check for asyncio.run() usage
        for line_num, line in enumerate(lines, 1):
            if ASYNCIO_RUN.search(line):
                # Check if setup_asyncio_policy is called nearby
                start = max(0, line_num - 20)
                context = "\n".join(lines[start:line_num])
                if "setup_asyncio_policy" not in context:
                    result.add_issue(
                        Issue(
                            file=relative_path,
                            line=line_num,
                            category="asyncio_policy",
                            message="asyncio.run() without setup_asyncio_policy()",
                            severity="info",
                            suggestion="Call setup_asyncio_policy() before asyncio.run() for Windows compatibility",
                        )
                    )

        # Check for os.path operations
        for line_num, line in enumerate(lines, 1):
            for pattern, message in OS_PATH_OPERATIONS:
                if re.search(pattern, line):
                    result.add_issue(
                        Issue(
                            file=relative_path,
                            line=line_num,
                            category="os_path",
                            message=message,
                            severity="info",
                            suggestion="Use pathlib.Path for cross-platform path handling",
                        )
                    )

        result.files_scanned += 1

    except Exception as e:
        result.add_issue(
            Issue(
                file=str(filepath),
                line=0,
                category="scan_error",
                message=f"Could not scan file: {e}",
                severity="error",
            )
        )


def scan_directory(
    directory: Path,
    exclude_dirs: list[str] | None = None,
) -> ScanResult:
    """Scan a directory for cross-platform compatibility issues."""
    result = ScanResult()
    exclude_dirs = exclude_dirs or [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        "*.egg-info",
    ]

    for filepath in directory.rglob("*.py"):
        # Skip excluded directories
        skip = False
        for exclude in exclude_dirs:
            if exclude in str(filepath):
                skip = True
                break
        if skip:
            continue

        scan_file(filepath, result)

    return result


def format_text_report(result: ScanResult, show_suggestions: bool = False) -> str:
    """Format scan results as text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("Cross-Platform Compatibility Report")
    lines.append("=" * 60)
    lines.append(f"Files scanned: {result.files_scanned}")
    lines.append(f"Errors: {result.errors}")
    lines.append(f"Warnings: {result.warnings}")
    lines.append(f"Info: {result.info}")
    lines.append("")

    if result.issues:
        # Group by file
        by_file: dict[str, list[Issue]] = {}
        for issue in result.issues:
            if issue.file not in by_file:
                by_file[issue.file] = []
            by_file[issue.file].append(issue)

        for filepath, issues in sorted(by_file.items()):
            lines.append(f"\n{filepath}:")
            for issue in sorted(issues, key=lambda x: x.line):
                icon = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(issue.severity, "•")
                lines.append(f"  {icon} Line {issue.line}: {issue.message}")
                if show_suggestions and issue.suggestion:
                    lines.append(f"      → {issue.suggestion}")
    else:
        lines.append("\n✅ No cross-platform compatibility issues found!")

    lines.append("")
    lines.append("=" * 60)
    return "\n".join(lines)


def format_json_report(result: ScanResult) -> str:
    """Format scan results as JSON."""
    return json.dumps(
        {
            "summary": {
                "files_scanned": result.files_scanned,
                "errors": result.errors,
                "warnings": result.warnings,
                "info": result.info,
                "total_issues": len(result.issues),
            },
            "issues": [
                {
                    "file": issue.file,
                    "line": issue.line,
                    "category": issue.category,
                    "message": issue.message,
                    "severity": issue.severity,
                    "suggestion": issue.suggestion,
                }
                for issue in result.issues
            ],
        },
        indent=2,
    )


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check codebase for cross-platform compatibility issues"
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Directory to scan (default: current directory)",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Show suggested fixes",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error if any issues found",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Additional directories to exclude",
    )

    args = parser.parse_args()

    # Determine scan path
    scan_path = Path(args.path)
    if not scan_path.exists():
        print(f"Error: Path '{scan_path}' does not exist", file=sys.stderr)
        return 1

    # Run scan
    exclude_dirs = [
        ".git",
        ".venv",
        "venv",
        "__pycache__",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
    ] + args.exclude

    result = scan_directory(scan_path, exclude_dirs)

    # Output results
    if args.json:
        print(format_json_report(result))
    else:
        print(format_text_report(result, show_suggestions=args.fix))

    # Exit code
    if args.strict and (result.errors > 0 or result.warnings > 0):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
