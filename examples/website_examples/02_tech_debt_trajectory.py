#!/usr/bin/env python3
"""Example 2: Tech Debt Trajectory Tracking
========================================

Demonstrates how persistent memory enables AI to track technical debt
over time and predict when it will become critical.

BEFORE: Debt count is just a number—no context, no trends.
AFTER:  "At current trajectory, your debt will double in 90 days."

Run this example:
    pip install empathy-framework
    python 02_tech_debt_trajectory.py

What it shows:
    1. Scan project for TODO, FIXME, HACK markers
    2. Store snapshots over time in git-based pattern storage
    3. Calculate trajectory and growth rate
    4. Predict future debt levels and critical thresholds

Copyright 2025 Smart AI Memory, LLC
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from empathy_software_plugin.wizards import TechDebtWizard


def seed_historical_data(wizard: TechDebtWizard):
    """Simulate 3 months of historical snapshots"""
    history_data = {
        "snapshots": [
            # 90 days ago: 25 items
            {
                "date": (datetime.now() - timedelta(days=90)).isoformat(),
                "total_items": 25,
                "by_type": {"todo": 15, "fixme": 5, "hack": 3, "temporary": 2},
                "by_severity": {"low": 10, "medium": 10, "high": 4, "critical": 1},
                "hotspots": ["src/legacy/importer.py"],
            },
            # 60 days ago: 35 items (+40%)
            {
                "date": (datetime.now() - timedelta(days=60)).isoformat(),
                "total_items": 35,
                "by_type": {"todo": 20, "fixme": 8, "hack": 4, "temporary": 3},
                "by_severity": {"low": 12, "medium": 15, "high": 6, "critical": 2},
                "hotspots": ["src/legacy/importer.py", "src/api/endpoints.py"],
            },
            # 30 days ago: 47 items (+34%)
            {
                "date": (datetime.now() - timedelta(days=30)).isoformat(),
                "total_items": 47,
                "by_type": {"todo": 28, "fixme": 10, "hack": 5, "temporary": 4},
                "by_severity": {"low": 15, "medium": 20, "high": 9, "critical": 3},
                "hotspots": ["src/legacy/importer.py", "src/api/endpoints.py"],
            },
        ],
    }

    # Store in pattern storage
    history_file = wizard.pattern_storage_path / "debt_history.json"
    history_file.parent.mkdir(parents=True, exist_ok=True)
    with open(history_file, "w") as f:
        json.dump(history_data, f, indent=2)


async def main():
    # Initialize the wizard
    wizard = TechDebtWizard(pattern_storage_path="./patterns/tech_debt")

    # -------------------------------------------------------------------------
    # STEP 1: Seed historical data (simulating past scans)
    # -------------------------------------------------------------------------
    print("Loading 3 months of historical debt snapshots...")
    seed_historical_data(wizard)
    print("  ✓ Loaded historical data")

    # -------------------------------------------------------------------------
    # STEP 2: Scan current project for debt
    # -------------------------------------------------------------------------
    print("\nScanning project for technical debt markers...")

    # Create a sample project to scan
    sample_dir = Path("./sample_project")
    sample_dir.mkdir(exist_ok=True)

    # Create sample file with debt markers
    sample_file = sample_dir / "example.py"
    sample_file.write_text(
        """
# TODO: Refactor this function to be more efficient
def process_data(data):
    # FIXME: This doesn't handle edge cases
    result = []
    for item in data:
        # HACK: Temporary workaround for API bug
        if item is not None:
            result.append(item)
    # TODO: Add proper error handling
    # TODO: Add logging
    return result

# DEPRECATED: Use process_data_v2 instead
def old_function():
    pass

# XXX: This needs review before production
def risky_function():
    # TEMP: Remove after migration
    pass
""",
    )

    result = await wizard.analyze(
        {
            "project_path": str(sample_dir),
            "track_history": True,
        },
    )

    # Clean up sample
    sample_file.unlink()
    sample_dir.rmdir()

    # -------------------------------------------------------------------------
    # STEP 3: See the power of trajectory analysis
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RESULTS: Tech Debt Trajectory Analysis")
    print("=" * 60)

    current = result["current_debt"]
    print("\n📊 CURRENT DEBT:")
    print(f"   Total Items: {current['total_items']}")
    print(f"   By Type: {current['by_type']}")

    if result["trajectory"]:
        traj = result["trajectory"]
        print("\n📈 TRAJECTORY:")
        print(f"   Previous (30 days ago): {traj['previous_total']} items")
        print(f"   Current: {traj['current_total']} items")
        print(f"   Change: {traj['change_percent']:+.1f}%")
        print(f"   Trend: {traj['trend'].upper()}")

        print("\n🔮 PROJECTIONS:")
        print(f"   In 30 days: {traj['projection_30_days']} items")
        print(f"   In 90 days: {traj['projection_90_days']} items")

        if traj["days_until_critical"]:
            print(f"   ⚠️  Days until 2x (critical): {traj['days_until_critical']}")

    if result["hotspots"]:
        print("\n🔥 TOP HOTSPOT:")
        hotspot = result["hotspots"][0]
        print(f"   File: {hotspot['file']}")
        print(f"   Debt Items: {hotspot['debt_count']}")

    print("\n📊 MEMORY BENEFIT:")
    benefit = result["memory_benefit"]
    print(f"   {benefit['value_statement']}")

    print("\n" + "=" * 60)
    print("Without persistent memory, debt is just a number.")
    print("With Empathy Framework, you see trends and predictions.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT:
# =============================================================================
#
# Loading 3 months of historical debt snapshots...
#   ✓ Loaded historical data
#
# Scanning project for technical debt markers...
#
# ============================================================
# RESULTS: Tech Debt Trajectory Analysis
# ============================================================
#
# 📊 CURRENT DEBT:
#    Total Items: 8
#    By Type: {'todo': 3, 'fixme': 1, 'hack': 1, 'deprecated': 1, 'temporary': 2}
#
# 📈 TRAJECTORY:
#    Previous (30 days ago): 47 items
#    Current: 8 items
#    Change: -83.0%
#    Trend: DECREASING
#
# 🔮 PROJECTIONS:
#    In 30 days: 0 items
#    In 90 days: 0 items
#
# 🔥 TOP HOTSPOT:
#    File: example.py
#    Debt Items: 8
#
# 📊 MEMORY BENEFIT:
#    Persistent memory enables trajectory analysis with 3 historical snapshots.
#
# ============================================================
# Without persistent memory, debt is just a number.
# With Empathy Framework, you see trends and predictions.
# ============================================================
