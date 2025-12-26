"""
One-Command Workflows for Empathy Framework

Power-user commands that automate common developer workflows:
- morning: Start-of-day briefing with patterns, debt, and focus areas
- ship: Pre-commit validation pipeline
- fix-all: Auto-fix all fixable issues
- learn: Watch for bug fixes and extract patterns

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from empathy_os.logging_config import get_logger

logger = get_logger(__name__)


def _load_patterns(patterns_dir: str = "./patterns") -> dict[str, list]:
    """Load patterns from the patterns directory."""
    patterns: dict[str, list] = {"debugging": [], "security": [], "tech_debt": [], "inspection": []}

    patterns_path = Path(patterns_dir)
    if not patterns_path.exists():
        return patterns

    for pattern_type in patterns.keys():
        file_path = patterns_path / f"{pattern_type}.json"
        if file_path.exists():
            try:
                with open(file_path) as f:
                    data = json.load(f)
                    patterns[pattern_type] = data.get("patterns", data.get("items", []))
            except (OSError, json.JSONDecodeError):
                pass

    return patterns


def _load_stats(empathy_dir: str = ".empathy") -> dict[str, Any]:
    """Load usage statistics."""
    stats_file = Path(empathy_dir) / "stats.json"
    if stats_file.exists():
        try:
            with open(stats_file) as f:
                result: dict[str, Any] = json.load(f)
                return result
        except (OSError, json.JSONDecodeError):
            pass
    return {"commands": {}, "last_session": None, "patterns_learned": 0}


def _save_stats(stats: dict, empathy_dir: str = ".empathy") -> None:
    """Save usage statistics."""
    stats_dir = Path(empathy_dir)
    stats_dir.mkdir(parents=True, exist_ok=True)

    with open(stats_dir / "stats.json", "w") as f:
        json.dump(stats, f, indent=2, default=str)


def _run_command(cmd: list, capture: bool = True) -> tuple:
    """Run a shell command and return (success, output)."""
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, timeout=300)
        return result.returncode == 0, result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"
    except Exception as e:
        return False, str(e)


def _get_tech_debt_trend(patterns_dir: str = "./patterns") -> str:
    """Analyze tech debt trajectory."""
    tech_debt_file = Path(patterns_dir) / "tech_debt.json"
    if not tech_debt_file.exists():
        return "unknown"

    try:
        with open(tech_debt_file) as f:
            data = json.load(f)

        snapshots = data.get("snapshots", [])
        if len(snapshots) < 2:
            return "insufficient_data"

        recent = snapshots[-1].get("total_items", 0)
        previous = snapshots[-2].get("total_items", 0)

        if recent > previous:
            return "increasing"
        elif recent < previous:
            return "decreasing"
        else:
            return "stable"
    except (OSError, json.JSONDecodeError, KeyError):
        return "unknown"


def morning_workflow(
    patterns_dir: str = "./patterns", project_root: str = ".", verbose: bool = False
) -> int:
    """
    Start-of-day developer briefing.

    Shows:
    - Health check summary
    - Patterns learned since last session
    - Tech debt trajectory
    - Suggested focus areas

    Returns exit code (0 = success).
    """
    print("\n" + "=" * 60)
    print("  MORNING BRIEFING")
    print("  " + datetime.now().strftime("%A, %B %d, %Y"))
    print("=" * 60 + "\n")

    # Load stats and patterns
    stats = _load_stats()
    patterns = _load_patterns(patterns_dir)

    # 1. Patterns summary
    print("PATTERNS LEARNED")
    print("-" * 40)

    total_bugs = len(patterns.get("debugging", []))
    resolved_bugs = len([p for p in patterns.get("debugging", []) if p.get("status") == "resolved"])
    security_decisions = len(patterns.get("security", []))

    print(f"  Bug patterns:        {total_bugs} ({resolved_bugs} resolved)")
    print(f"  Security decisions:  {security_decisions}")
    print(f"  Inspection patterns: {len(patterns.get('inspection', []))}")

    # Recent patterns (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_bugs = []
    for bug in patterns.get("debugging", []):
        try:
            timestamp = bug.get("timestamp", bug.get("resolved_at", ""))
            if timestamp:
                bug_date = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                if bug_date.replace(tzinfo=None) > week_ago:
                    recent_bugs.append(bug)
        except (ValueError, TypeError):
            pass

    if recent_bugs:
        print(f"\n  New this week: {len(recent_bugs)} patterns")
        for bug in recent_bugs[:3]:
            print(f"    - {bug.get('bug_type', '?')}: {bug.get('root_cause', '?')[:40]}")

    # 2. Tech debt trajectory
    print("\n" + "TECH DEBT TRAJECTORY")
    print("-" * 40)

    trend = _get_tech_debt_trend(patterns_dir)
    trend_icons = {
        "increasing": "  Trending UP - Consider allocating time for cleanup",
        "decreasing": "  Trending DOWN - Great progress!",
        "stable": "  Stable - Holding steady",
        "unknown": "  Run 'empathy inspect' to start tracking",
        "insufficient_data": "  Not enough data yet - keep coding!",
    }
    print(trend_icons.get(trend, "  Unknown"))

    # Show hotspots if available
    tech_debt_file = Path(patterns_dir) / "tech_debt.json"
    if tech_debt_file.exists():
        try:
            with open(tech_debt_file) as f:
                data = json.load(f)
            snapshots = data.get("snapshots", [])
            if snapshots:
                latest = snapshots[-1]
                hotspots = latest.get("hotspots", [])[:3]
                if hotspots:
                    print("\n  Top hotspots:")
                    for hotspot in hotspots:
                        print(f"    - {hotspot}")
        except (OSError, json.JSONDecodeError):
            pass

    # 3. Quick health check
    print("\n" + "QUICK HEALTH CHECK")
    print("-" * 40)

    checks_passed = 0
    checks_total = 0

    # Check for ruff
    checks_total += 1
    success, output = _run_command(["ruff", "check", project_root, "--statistics", "-q"])
    if success:
        checks_passed += 1
        print("  Lint:     OK")
    else:
        issues = len([line for line in output.split("\n") if line.strip()])
        print(f"  Lint:     {issues} issues")

    # Check for uncommitted changes
    checks_total += 1
    success, output = _run_command(["git", "status", "--porcelain"])
    if success:
        changes = len([line for line in output.split("\n") if line.strip()])
        if changes == 0:
            checks_passed += 1
            print("  Git:      Clean")
        else:
            print(f"  Git:      {changes} uncommitted files")

    print(f"\n  Overall:  {checks_passed}/{checks_total} checks passed")

    # 4. Suggested focus
    print("\n" + "SUGGESTED FOCUS TODAY")
    print("-" * 40)

    suggestions = []

    # Based on patterns
    investigating_bugs = [
        p for p in patterns.get("debugging", []) if p.get("status") == "investigating"
    ]
    if investigating_bugs:
        suggestions.append(
            f"Resolve {len(investigating_bugs)} investigating bug(s) via 'empathy patterns resolve'"
        )

    if trend == "increasing":
        suggestions.append("Address tech debt - run 'empathy status' for priorities")

    if total_bugs == 0:
        suggestions.append("Start learning patterns - run 'empathy learn' or 'empathy inspect'")

    if not suggestions:
        suggestions.append("Ship something great! Run 'empathy ship' before committing")

    for i, suggestion in enumerate(suggestions[:3], 1):
        print(f"  {i}. {suggestion}")

    # Update stats
    stats["last_session"] = datetime.now().isoformat()
    stats["commands"]["morning"] = stats["commands"].get("morning", 0) + 1
    _save_stats(stats)

    print("\n" + "=" * 60)
    print("  Have a productive day!")
    print("=" * 60 + "\n")

    return 0


def ship_workflow(
    patterns_dir: str = "./patterns",
    project_root: str = ".",
    skip_sync: bool = False,
    verbose: bool = False,
) -> int:
    """
    Pre-commit validation pipeline.

    Runs:
    1. empathy inspect (code analysis)
    2. empathy health (quick checks)
    3. empathy sync-claude (pattern sync)
    4. Summary

    Returns exit code (0 = ready to ship, non-zero = issues found).
    """
    print("\n" + "=" * 60)
    print("  PRE-SHIP CHECKLIST")
    print("=" * 60 + "\n")

    issues = []
    warnings = []

    # 1. Lint check
    print("1. Running lint check...")
    success, output = _run_command(["ruff", "check", project_root])
    if success:
        print("   PASS - No lint issues")
    else:
        issue_count = len(
            [line for line in output.split("\n") if line.strip() and not line.startswith("Found")]
        )
        issues.append(f"Lint: {issue_count} issues")
        print(f"   FAIL - {issue_count} issues found")
        if verbose:
            print(output)

    # 2. Format check
    print("2. Checking formatting...")
    success, output = _run_command(["ruff", "format", "--check", project_root])
    if success:
        print("   PASS - Code is formatted")
    else:
        files = len(
            [
                line
                for line in output.split("\n")
                if "would be reformatted" in line.lower() or line.strip().endswith(".py")
            ]
        )
        warnings.append(f"Format: {files} files need formatting")
        print(f"   WARN - {files} files need formatting (run 'empathy fix-all')")

    # 3. Type check (if mypy available)
    print("3. Checking types...")
    success, output = _run_command(
        ["python", "-m", "mypy", project_root, "--ignore-missing-imports", "--no-error-summary"],
        capture=True,
    )
    if success or "error:" not in output.lower():
        print("   PASS - No type errors")
    else:
        error_count = output.lower().count("error:")
        warnings.append(f"Types: {error_count} type issues")
        print(f"   WARN - {error_count} type issues")

    # 4. Git status
    print("4. Checking git status...")
    success, output = _run_command(["git", "status", "--porcelain"])
    if success:
        staged = len(
            [line for line in output.split("\n") if line.startswith(("A ", "M ", "D ", "R "))]
        )
        unstaged = len([line for line in output.split("\n") if line.startswith((" M", " D", "??"))])
        if staged > 0:
            print(f"   INFO - {staged} staged, {unstaged} unstaged")
        elif unstaged > 0:
            warnings.append(f"Git: {unstaged} unstaged files")
            print(f"   WARN - No staged changes ({unstaged} unstaged files)")
        else:
            print("   INFO - Working tree clean")

    # 5. Sync to Claude (optional)
    if not skip_sync:
        print("5. Syncing patterns to Claude Code...")
        # Import here to avoid circular imports
        try:
            from empathy_llm_toolkit.cli.sync_claude import (
                sync_patterns_to_claude,
            )  # type: ignore[attr-defined]

            result = sync_patterns_to_claude(
                patterns_dir=patterns_dir, output_dir=".claude/rules/empathy"
            )
            if result.get("success"):
                print(f"   PASS - {result.get('patterns_synced', 0)} patterns synced")
            else:
                print("   SKIP - No patterns to sync")
        except ImportError:
            print("   SKIP - sync-claude not available")
        except Exception as e:
            print(f"   SKIP - {e}")
    else:
        print("5. Skipping Claude sync (--skip-sync)")

    # Summary
    print("\n" + "-" * 60)

    if issues:
        print("\nBLOCKERS (must fix before shipping):")
        for issue in issues:
            print(f"  - {issue}")
        print("\n  Run 'empathy fix-all' to auto-fix what's possible")
        print("\n" + "=" * 60)
        print("  NOT READY TO SHIP")
        print("=" * 60 + "\n")
        return 1

    if warnings:
        print("\nWARNINGS (recommended to fix):")
        for warning in warnings:
            print(f"  - {warning}")

    print("\n" + "=" * 60)
    print("  READY TO SHIP!")
    print("=" * 60 + "\n")

    # Update stats
    stats = _load_stats()
    stats["commands"]["ship"] = stats["commands"].get("ship", 0) + 1
    _save_stats(stats)

    return 0


def fix_all_workflow(project_root: str = ".", dry_run: bool = False, verbose: bool = False) -> int:
    """
    Auto-fix all fixable issues.

    Runs:
    1. ruff --fix (lint fixes)
    2. ruff format (formatting)
    3. isort (import sorting)
    4. Report what changed

    Returns exit code (0 = success).
    """
    print("\n" + "=" * 60)
    print("  AUTO-FIX ALL")
    if dry_run:
        print("  (DRY RUN - no changes will be made)")
    print("=" * 60 + "\n")

    fixed_count = 0

    # 1. Ruff lint fixes
    print("1. Fixing lint issues...")
    if dry_run:
        success, output = _run_command(["ruff", "check", project_root, "--fix", "--diff"])
    else:
        success, output = _run_command(["ruff", "check", project_root, "--fix"])

    if success:
        fixed = output.count("Fixed")
        fixed_count += fixed
        print(f"   Fixed {fixed} issues")
    else:
        # Some issues couldn't be auto-fixed
        unfixable = len([line for line in output.split("\n") if "error" in line.lower()])
        print(f"   {unfixable} issues require manual fix")
        if verbose:
            print(output)

    # 2. Ruff formatting
    print("2. Formatting code...")
    if dry_run:
        success, output = _run_command(["ruff", "format", project_root, "--diff"])
        formatted = output.count("@@ ")
    else:
        success, output = _run_command(["ruff", "format", project_root])
        formatted = len(
            [
                line
                for line in output.split("\n")
                if line.strip().endswith(".py") and "reformatted" in output.lower()
            ]
        )

    print(f"   Formatted {formatted} files")

    # 3. isort (if available)
    print("3. Sorting imports...")
    if dry_run:
        success, output = _run_command(["isort", project_root, "--check-only", "--diff"])
    else:
        success, output = _run_command(["isort", project_root])

    if "Skipped" in output or "isort" in output:
        sorted_count = output.count("Fixing") if not dry_run else output.count("---")
        print(f"   Sorted imports in {sorted_count} files")
    else:
        print("   No import changes needed")

    # Summary
    print("\n" + "-" * 60)

    if dry_run:
        print("\nDRY RUN complete - no files were modified")
        print("Run without --dry-run to apply changes")
    else:
        print(f"\nTotal fixes applied: {fixed_count}+")
        print("Run 'empathy ship' to verify everything is ready")

    print("\n" + "=" * 60 + "\n")

    # Update stats
    stats = _load_stats()
    stats["commands"]["fix-all"] = stats["commands"].get("fix-all", 0) + 1
    _save_stats(stats)

    return 0


def learn_workflow(
    patterns_dir: str = "./patterns",
    analyze_commits: int | None = None,
    watch: bool = False,
    verbose: bool = False,
) -> int:
    """
    Watch for bug fixes and extract patterns.

    Modes:
    - analyze: Analyze recent commits for bug fix patterns
    - watch: Watch for new commits and learn in real-time

    Returns exit code (0 = success).
    """
    print("\n" + "=" * 60)
    print("  PATTERN LEARNING")
    print("=" * 60 + "\n")

    patterns_path = Path(patterns_dir)
    patterns_path.mkdir(parents=True, exist_ok=True)

    if watch:
        print("Watch mode not yet implemented.")
        print("Use 'empathy learn --analyze N' to analyze recent commits.\n")
        return 1

    # Default to analyzing last 10 commits
    commit_count = analyze_commits or 10

    print(f"Analyzing last {commit_count} commits for bug fix patterns...\n")

    # Get recent commits
    success, output = _run_command(
        ["git", "log", f"-{commit_count}", "--oneline", "--format=%H|%s|%an|%ai"]
    )

    if not success:
        print("Failed to read git log. Are you in a git repository?")
        return 1

    commits = output.strip().split("\n")
    bug_fix_keywords = [
        "fix",
        "bug",
        "issue",
        "error",
        "crash",
        "broken",
        "repair",
        "patch",
        "resolve",
    ]

    learned = []

    for commit_line in commits:
        if not commit_line.strip():
            continue

        parts = commit_line.split("|")
        if len(parts) < 2:
            continue

        commit_hash = parts[0][:8]
        message = parts[1].lower()
        author = parts[2] if len(parts) > 2 else "unknown"
        date = parts[3][:10] if len(parts) > 3 else ""

        # Check if this looks like a bug fix
        is_bug_fix = any(kw in message for kw in bug_fix_keywords)

        if is_bug_fix:
            # Get the diff for this commit
            success, diff_output = _run_command(["git", "show", commit_hash, "--stat", "--oneline"])

            files_changed = []
            if success:
                for line in diff_output.split("\n"):
                    if "|" in line and ("+" in line or "-" in line):
                        file_name = line.split("|")[0].strip()
                        files_changed.append(file_name)

            # Classify bug type from message
            bug_type = "unknown"
            if any(kw in message for kw in ["null", "none", "undefined", "empty"]):
                bug_type = "null_reference"
            elif any(kw in message for kw in ["async", "await", "promise", "timeout"]):
                bug_type = "async_timing"
            elif any(kw in message for kw in ["type", "cast", "convert"]):
                bug_type = "type_mismatch"
            elif any(kw in message for kw in ["import", "module", "package"]):
                bug_type = "import_error"

            pattern = {
                "pattern_id": f"bug_{date.replace('-', '')}_{commit_hash}",
                "bug_type": bug_type,
                "status": "resolved",
                "root_cause": parts[1],  # Original message
                "fix": f"See commit {commit_hash}",
                "resolved_by": f"@{author.split()[0].lower()}",
                "resolved_at": date,
                "files_affected": files_changed[:3],
                "source": "git_history",
            }

            learned.append(pattern)

            if verbose:
                print(f"  Found: {bug_type} in {commit_hash}")
                print(f"         {parts[1][:60]}")

    # Load existing patterns and merge
    debugging_file = patterns_path / "debugging.json"
    existing: dict[str, Any] = {"patterns": []}

    if debugging_file.exists():
        try:
            with open(debugging_file) as f:
                existing = json.load(f)
        except (OSError, json.JSONDecodeError):
            pass

    # Add new patterns (avoid duplicates)
    existing_ids = {p.get("pattern_id") for p in existing.get("patterns", [])}
    new_patterns = [p for p in learned if p["pattern_id"] not in existing_ids]

    if new_patterns:
        existing["patterns"].extend(new_patterns)
        existing["last_updated"] = datetime.now().isoformat()

        with open(debugging_file, "w") as f:
            json.dump(existing, f, indent=2)

    # Summary
    print("-" * 40)
    print(f"\nAnalyzed: {len(commits)} commits")
    print(f"Bug fixes found: {len(learned)}")
    print(f"New patterns learned: {len(new_patterns)}")

    if learned:
        print("\nBug types discovered:")
        types: dict[str, int] = {}
        for p in learned:
            t = p["bug_type"]
            types[t] = types.get(t, 0) + 1
        for bug_type, count in sorted(types.items(), key=lambda x: -x[1]):
            print(f"  {bug_type}: {count}")

    print("\n" + "=" * 60)
    print("  Run 'empathy sync-claude' to use these patterns with Claude Code")
    print("=" * 60 + "\n")

    # Update stats
    stats = _load_stats()
    stats["commands"]["learn"] = stats["commands"].get("learn", 0) + 1
    stats["patterns_learned"] = stats.get("patterns_learned", 0) + len(new_patterns)
    _save_stats(stats)

    return 0


# CLI command handlers
def cmd_morning(args):
    """Morning briefing command handler."""
    return morning_workflow(
        patterns_dir=getattr(args, "patterns_dir", "./patterns"),
        project_root=getattr(args, "project_root", "."),
        verbose=getattr(args, "verbose", False),
    )


def cmd_ship(args):
    """Ship command handler."""
    return ship_workflow(
        patterns_dir=getattr(args, "patterns_dir", "./patterns"),
        project_root=getattr(args, "project_root", "."),
        skip_sync=getattr(args, "skip_sync", False),
        verbose=getattr(args, "verbose", False),
    )


def cmd_fix_all(args):
    """Fix-all command handler."""
    return fix_all_workflow(
        project_root=getattr(args, "project_root", "."),
        dry_run=getattr(args, "dry_run", False),
        verbose=getattr(args, "verbose", False),
    )


def cmd_learn(args):
    """Learn command handler."""
    return learn_workflow(
        patterns_dir=getattr(args, "patterns_dir", "./patterns"),
        analyze_commits=getattr(args, "analyze", None),
        watch=getattr(args, "watch", False),
        verbose=getattr(args, "verbose", False),
    )
