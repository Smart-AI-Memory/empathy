#!/usr/bin/env python3
"""
Persistent Memory Showcase
==========================

Demonstrates 3 things that weren't possible before persistent memory:

1. Bug Pattern Correlation - AI remembers past bugs and how they were fixed
2. Tech Debt Trajectory - AI tracks debt over time and predicts critical points
3. Security False Positive Learning - AI learns from team decisions

Run this demo to see the power of memory-enhanced development tools.

Usage:
    python examples/persistent_memory_showcase.py
    python examples/persistent_memory_showcase.py --demo debugging
    python examples/persistent_memory_showcase.py --demo tech_debt
    python examples/persistent_memory_showcase.py --demo security

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from empathy_software_plugin.wizards.memory_enhanced_debugging_wizard import (
    MemoryEnhancedDebuggingWizard,
)
from empathy_software_plugin.wizards.security_learning_wizard import SecurityLearningWizard
from empathy_software_plugin.wizards.tech_debt_wizard import TechDebtWizard

# ============================================================================
# DISPLAY HELPERS
# ============================================================================


def print_header(title: str) -> None:
    """Print a formatted header"""
    width = 70
    print("\n" + "=" * width)
    print(f"  {title}")
    print("=" * width)


def print_section(title: str) -> None:
    """Print a section header"""
    print(f"\n--- {title} ---\n")


def print_comparison(before: str, after: str) -> None:
    """Print before/after comparison"""
    print(f"  WITHOUT MEMORY: {before}")
    print(f"  WITH MEMORY:    {after}")


def print_json(data: dict, indent: int = 2) -> None:
    """Print formatted JSON"""
    print(json.dumps(data, indent=indent, default=str))


# ============================================================================
# DEMO 1: BUG PATTERN CORRELATION
# ============================================================================


async def demo_bug_correlation() -> None:
    """
    Demonstrate bug pattern correlation.

    Shows how persistent memory enables:
    - Finding similar bugs from the past
    - Recommending proven fixes
    - Estimating resolution time
    """
    print_header("DEMO 1: Bug Pattern Correlation")

    print(
        """
What's now possible that wasn't before:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    )
    print_comparison(
        "Every debugging session starts from zero",
        '"This bug looks like one we fixed 3 months ago—here\'s what worked"',
    )

    # Initialize wizard
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path="./patterns/debugging_demo")

    # First, seed some historical bug patterns
    print_section("Step 1: Seeding Historical Bug Data")
    print("Adding 3 historical bug resolutions to memory...")

    await seed_historical_bugs(wizard)

    # Now analyze a "new" bug that matches a historical pattern
    print_section("Step 2: Analyzing New Bug")

    new_bug = {
        "error_message": "TypeError: Cannot read property 'map' of undefined",
        "file_path": "src/components/OrderList.tsx",
        "stack_trace": "at OrderList (OrderList.tsx:47)\n  at renderWithHooks",
        "line_number": 47,
        "correlate_with_history": True,
    }

    print(f"Error: {new_bug['error_message']}")
    print(f"File:  {new_bug['file_path']}:{new_bug['line_number']}")

    result = await wizard.analyze(new_bug)

    print_section("Step 3: Results - Historical Correlation")

    print(f"Error Classification: {result['error_classification']['error_type']}")
    print(f"Historical Matches Found: {result['matches_found']}")

    if result["historical_matches"]:
        print("\n📚 HISTORICAL MATCHES:")
        for i, match in enumerate(result["historical_matches"][:3], 1):
            print(f"\n  Match #{i} (Similarity: {match['similarity_score']:.0%})")
            print(f"  Date: {match['date']}")
            print(f"  File: {match['file']}")
            print(f"  Root Cause: {match['root_cause']}")
            print(f"  Fix Applied: {match['fix_applied']}")
            print(f"  Resolution Time: {match['resolution_time_minutes']} minutes")
            print(f"  Matching Factors: {', '.join(match['matching_factors'])}")

    if result["recommended_fix"]:
        print("\n💡 RECOMMENDED FIX:")
        print(f"  Based on: {result['recommended_fix']['based_on']}")
        print(f"  Fix: {result['recommended_fix']['original_fix']}")
        print(f"  Expected Time: {result['recommended_fix']['expected_resolution_time']}")

    print_section("Memory Benefit")
    benefit = result["memory_benefit"]
    print(f"  {benefit['value_statement']}")
    print(f"  Estimated time saved: {benefit.get('time_saved_estimate', 'N/A')}")


async def seed_historical_bugs(wizard: MemoryEnhancedDebuggingWizard) -> None:
    """Seed historical bug patterns for demo"""

    historical_bugs = [
        {
            "bug_id": "bug_20250915_abc123",
            "date": (datetime.now() - timedelta(days=90)).isoformat(),
            "file_path": "src/components/ProductList.tsx",
            "error_type": "null_reference",
            "error_message": "TypeError: Cannot read property 'map' of undefined",
            "root_cause": "API returned null instead of empty array",
            "fix_applied": "Added default empty array fallback: data?.items ?? []",
            "fix_code": "const items = data?.items ?? [];",
            "resolution_time_minutes": 15,
            "resolved_by": "@sarah",
            "status": "resolved",
        },
        {
            "bug_id": "bug_20250822_def456",
            "date": (datetime.now() - timedelta(days=110)).isoformat(),
            "file_path": "src/components/UserList.tsx",
            "error_type": "null_reference",
            "error_message": "TypeError: Cannot read property 'map' of null",
            "root_cause": "Component rendered before data fetched",
            "fix_applied": "Added loading state check before rendering list",
            "fix_code": "if (!data) return <Loading />;",
            "resolution_time_minutes": 8,
            "resolved_by": "@mike",
            "status": "resolved",
        },
        {
            "bug_id": "bug_20251101_ghi789",
            "date": (datetime.now() - timedelta(days=40)).isoformat(),
            "file_path": "src/api/orders.ts",
            "error_type": "async_timing",
            "error_message": "Unhandled promise rejection: undefined",
            "root_cause": "Missing await on async function call",
            "fix_applied": "Added await keyword to async call",
            "fix_code": "const result = await fetchOrders();",
            "resolution_time_minutes": 5,
            "resolved_by": "@sarah",
            "status": "resolved",
        },
    ]

    # Store in pattern storage
    for bug in historical_bugs:
        pattern_file = wizard.pattern_storage_path / f"{bug['bug_id']}.json"
        pattern_file.parent.mkdir(parents=True, exist_ok=True)
        with open(pattern_file, "w") as f:
            json.dump(bug, f, indent=2)

    print(f"  ✓ Stored {len(historical_bugs)} historical bug patterns")


# ============================================================================
# DEMO 2: TECH DEBT TRAJECTORY
# ============================================================================


async def demo_tech_debt() -> None:
    """
    Demonstrate tech debt trajectory tracking.

    Shows how persistent memory enables:
    - Tracking debt over time
    - Predicting when debt becomes critical
    - Identifying debt hotspots
    """
    print_header("DEMO 2: Tech Debt Trajectory Tracking")

    print(
        """
What's now possible that wasn't before:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    )
    print_comparison(
        "Debt count is just a number (no context)",
        '"At current trajectory, debt will double in 90 days"',
    )

    # Initialize wizard
    wizard = TechDebtWizard(pattern_storage_path="./patterns/tech_debt_demo")

    # Seed historical snapshots
    print_section("Step 1: Seeding Historical Data")
    print("Adding 4 monthly snapshots to simulate history...")

    seed_debt_history(wizard)

    # Analyze current debt
    print_section("Step 2: Analyzing Current Debt")
    print("Scanning project for technical debt markers...")

    result = await wizard.analyze(
        {
            "project_path": ".",
            "track_history": True,
            "exclude_patterns": ["node_modules", "venv", ".git", "__pycache__", "patterns"],
        }
    )

    print_section("Step 3: Results - Current Debt")

    current = result["current_debt"]
    print(f"Total Debt Items: {current['total_items']}")
    print("\nBy Type:")
    for debt_type, count in current["by_type"].items():
        if count > 0:
            print(f"  {debt_type.upper()}: {count}")
    print("\nBy Severity:")
    for severity, count in current["by_severity"].items():
        if count > 0:
            print(f"  {severity}: {count}")

    print_section("Step 4: Results - Trajectory Analysis")

    if result["trajectory"]:
        trajectory = result["trajectory"]
        print(f"Current Total: {trajectory['current_total']}")
        print(f"Previous Total: {trajectory['previous_total']} (30 days ago)")
        print(f"Change: {trajectory['change_percent']:+.1f}%")
        print(f"Trend: {trajectory['trend'].upper()}")
        print("\n📈 PROJECTIONS:")
        print(f"  30 days: {trajectory['projection_30_days']} items")
        print(f"  90 days: {trajectory['projection_90_days']} items")
        if trajectory["days_until_critical"]:
            print(f"  ⚠️  Days until critical (2x): {trajectory['days_until_critical']}")
    else:
        print("No historical data for trajectory analysis yet.")

    print_section("Step 5: Results - Hotspots")

    if result["hotspots"]:
        print("🔥 DEBT HOTSPOTS:")
        for i, hotspot in enumerate(result["hotspots"][:5], 1):
            print(f"\n  #{i}: {hotspot['file']}")
            print(f"      Debt items: {hotspot['debt_count']}")
            print(f"      Types: {', '.join(hotspot['types'])}")
            print(f"      Severity score: {hotspot['severity_score']}")

    print_section("Memory Benefit")
    benefit = result["memory_benefit"]
    print(f"  {benefit['value_statement']}")
    if benefit.get("insight"):
        print(f"  Current insight: {benefit['insight']}")


def seed_debt_history(wizard: TechDebtWizard) -> None:
    """Seed historical debt snapshots for demo"""

    # Create increasing debt trend
    history_data = {
        "snapshots": [
            {
                "date": (datetime.now() - timedelta(days=90)).isoformat(),
                "total_items": 25,
                "by_type": {"todo": 15, "fixme": 5, "hack": 3, "temporary": 2},
                "by_severity": {"low": 10, "medium": 10, "high": 4, "critical": 1},
                "hotspots": ["src/legacy/importer.py", "src/api/v1/endpoints.py"],
            },
            {
                "date": (datetime.now() - timedelta(days=60)).isoformat(),
                "total_items": 35,
                "by_type": {"todo": 20, "fixme": 8, "hack": 4, "temporary": 3},
                "by_severity": {"low": 12, "medium": 15, "high": 6, "critical": 2},
                "hotspots": ["src/legacy/importer.py", "src/api/v1/endpoints.py"],
            },
            {
                "date": (datetime.now() - timedelta(days=30)).isoformat(),
                "total_items": 47,
                "by_type": {"todo": 28, "fixme": 10, "hack": 5, "temporary": 4},
                "by_severity": {"low": 15, "medium": 20, "high": 9, "critical": 3},
                "hotspots": [
                    "src/legacy/importer.py",
                    "src/api/v1/endpoints.py",
                    "src/utils/helpers.py",
                ],
            },
        ]
    }

    history_file = wizard.pattern_storage_path / "debt_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=2)

    print(f"  ✓ Stored {len(history_data['snapshots'])} historical snapshots")


# ============================================================================
# DEMO 3: SECURITY FALSE POSITIVE LEARNING
# ============================================================================


async def demo_security() -> None:
    """
    Demonstrate security false positive learning.

    Shows how persistent memory enables:
    - Learning from team decisions
    - Suppressing known false positives
    - Reducing security alert fatigue
    """
    print_header("DEMO 3: Security False Positive Learning")

    print(
        """
What's now possible that wasn't before:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    )
    print_comparison(
        "Same false positives flagged every scan",
        '"Suppressing 8 warnings you\'ve previously marked as acceptable"',
    )

    # Initialize wizard
    wizard = SecurityLearningWizard(pattern_storage_path="./patterns/security_demo")

    # Seed team decisions
    print_section("Step 1: Seeding Team Security Decisions")
    print("Adding 5 team decisions from past reviews...")

    seed_security_decisions(wizard)

    # Analyze security
    print_section("Step 2: Analyzing Project Security")
    print("Scanning for vulnerabilities...")

    result = await wizard.analyze(
        {
            "project_path": ".",
            "apply_learned_patterns": True,
            "exclude_patterns": ["node_modules", "venv", ".git", "__pycache__", "patterns", "test"],
            "scan_depth": "quick",
        }
    )

    print_section("Step 3: Results - With Learning Applied")

    print(f"Raw Findings: {result['raw_findings_count']}")
    print(f"After Learning: {result['summary']['total_after_learning']}")

    learning = result["learning_applied"]
    if learning["enabled"]:
        print("\n🧠 LEARNING APPLIED:")
        print(f"  Findings suppressed: {learning['suppressed_count']}")
        print(f"  Noise reduction: {learning['noise_reduction_percent']}%")
        print(f"  Team decisions used: {result['team_decisions_count']}")

        if learning["suppression_details"]:
            print("\n  Suppression Details:")
            for detail in learning["suppression_details"][:5]:
                print(f"    • {detail['type']} in {Path(detail['file']).name}")
                print(f"      Decision: {detail['decision']} by {detail['decided_by']}")
                print(f"      Reason: {detail['reason']}")

    print_section("Step 4: Results - Remaining Findings")

    print("\nBy Severity:")
    for severity, count in result["summary"]["by_severity"].items():
        if count > 0:
            emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}.get(severity, "•")
            print(f"  {emoji} {severity}: {count}")

    if result["findings"]:
        print("\n📍 Top Findings (new, not yet reviewed):")
        for finding in result["findings"][:3]:
            print(f"\n  {finding['severity'].upper()}: {finding['type']}")
            print(f"  File: {finding['file']}:{finding['line']}")
            print(f"  Preview: {finding['code_preview'][:60]}...")

    print_section("Memory Benefit")
    benefit = result["memory_benefit"]
    print(f"  {benefit['value_statement']}")
    if benefit.get("noise_reduction_percent"):
        print(f"  Noise reduction: {benefit['noise_reduction_percent']}%")


def seed_security_decisions(wizard: SecurityLearningWizard) -> None:
    """Seed team security decisions for demo"""

    decisions_data = {
        "decisions": [
            {
                "finding_hash": "sql_injection",  # Applies to all SQL injection findings
                "decision": "false_positive",
                "reason": "Using SQLAlchemy ORM which handles escaping",
                "decided_by": "@sarah",
                "decided_at": (datetime.now() - timedelta(days=45)).isoformat(),
                "applies_to": "all",
            },
            {
                "finding_hash": "insecure_random",
                "decision": "accepted",
                "reason": "Only used for non-security purposes (UI animations)",
                "decided_by": "@mike",
                "decided_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "applies_to": "all",
            },
            {
                "finding_hash": "hardcoded_secret:test_api_key",
                "decision": "false_positive",
                "reason": "Test fixtures only, not real credentials",
                "decided_by": "@sarah",
                "decided_at": (datetime.now() - timedelta(days=60)).isoformat(),
                "applies_to": "pattern",
            },
            {
                "finding_hash": "xss",
                "decision": "accepted",
                "reason": "React's JSX auto-escapes, innerHTML not used",
                "decided_by": "@tech_lead",
                "decided_at": (datetime.now() - timedelta(days=90)).isoformat(),
                "applies_to": "all",
            },
            {
                "finding_hash": "eval",
                "decision": "deferred",
                "reason": "Low risk in dev tooling, will address in Q2",
                "decided_by": "@security_team",
                "decided_at": (datetime.now() - timedelta(days=15)).isoformat(),
                "applies_to": "pattern",
                "expiration": (datetime.now() + timedelta(days=90)).isoformat(),
            },
        ]
    }

    decisions_file = wizard.pattern_storage_path / "team_decisions.json"
    decisions_file.parent.mkdir(parents=True, exist_ok=True)
    with open(decisions_file, "w") as f:
        json.dump(decisions_data, f, indent=2)

    print(f"  ✓ Stored {len(decisions_data['decisions'])} team decisions")


# ============================================================================
# UNIFIED DEMO
# ============================================================================


async def demo_all() -> None:
    """Run all three demos"""

    print_header("PERSISTENT MEMORY SHOWCASE")
    print(
        """
This demo shows 3 things that weren't possible before persistent memory:

  1. Bug Pattern Correlation
     "This bug looks like one we fixed 3 months ago"

  2. Tech Debt Trajectory
     "At current trajectory, debt will double in 90 days"

  3. Security False Positive Learning
     "Suppressing 8 warnings you've previously marked as acceptable"

Each demo shows the BEFORE (stateless) vs AFTER (memory-enhanced) experience.
"""
    )

    input("Press Enter to start Demo 1: Bug Pattern Correlation...")
    await demo_bug_correlation()

    input("\nPress Enter to start Demo 2: Tech Debt Trajectory...")
    await demo_tech_debt()

    input("\nPress Enter to start Demo 3: Security False Positive Learning...")
    await demo_security()

    print_header("SUMMARY: The Power of Persistent Memory")
    print(
        """
What we demonstrated:

1. BUG CORRELATION
   • AI remembers past bugs and their fixes
   • Recommends proven solutions instantly
   • Estimates resolution time from historical data

2. TECH DEBT TRAJECTORY
   • Tracks debt accumulation over time
   • Predicts when debt becomes critical
   • Identifies files that accumulate debt

3. SECURITY LEARNING
   • Learns from team's security decisions
   • Suppresses known false positives automatically
   • Reduces alert fatigue significantly

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The key insight: MEMORY CHANGES EVERYTHING

Without memory, AI tools start from zero every session.
With memory, they compound knowledge over time.

This is what the Empathy Framework enables.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Get started:
    pip install empathy-framework
    empathy-memory serve

GitHub: https://github.com/Smart-AI-Memory/empathy
"""
    )


# ============================================================================
# MAIN
# ============================================================================


def main():
    parser = argparse.ArgumentParser(
        description="Persistent Memory Showcase - 3 things that weren't possible before"
    )
    parser.add_argument(
        "--demo",
        choices=["all", "debugging", "tech_debt", "security"],
        default="all",
        help="Which demo to run (default: all)",
    )

    args = parser.parse_args()

    if args.demo == "debugging":
        asyncio.run(demo_bug_correlation())
    elif args.demo == "tech_debt":
        asyncio.run(demo_tech_debt())
    elif args.demo == "security":
        asyncio.run(demo_security())
    else:
        asyncio.run(demo_all())


if __name__ == "__main__":
    main()
