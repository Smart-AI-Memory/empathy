#!/usr/bin/env python3
"""Example 1: Bug Pattern Correlation
==================================

Demonstrates how persistent memory enables AI to correlate current bugs
with historical patterns—something that wasn't possible before.

BEFORE: Every debugging session starts from zero.
AFTER:  "This bug looks like one we fixed 3 months ago—here's what worked."

Run this example:
    pip install empathy-framework
    python 01_bug_correlation.py

What it shows:
    1. Store historical bug resolutions in git-based pattern storage
    2. Analyze a new bug and find similar past issues
    3. Get fix recommendations based on historical data
    4. Estimate resolution time from team experience

Copyright 2025 Smart AI Memory, LLC
"""

import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path

from empathy_software_plugin.wizards import MemoryEnhancedDebuggingWizard


def seed_historical_bugs(pattern_path: Path):
    """Simulate historical bug patterns from past sessions"""
    pattern_path.mkdir(parents=True, exist_ok=True)

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
    ]

    for bug in historical_bugs:
        pattern_file = pattern_path / f"{bug['bug_id']}.json"
        with open(pattern_file, "w") as f:
            json.dump(bug, f, indent=2)


async def main():
    # Initialize the wizard with pattern storage location
    pattern_path = Path("./patterns/debugging")
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    # -------------------------------------------------------------------------
    # STEP 1: Seed historical bugs (simulating past sessions)
    # -------------------------------------------------------------------------
    print("Recording historical bug patterns...")

    # In real usage, these would accumulate over time as your team fixes bugs
    seed_historical_bugs(pattern_path)

    print("  ✓ Stored 2 bug patterns from @sarah and @mike")

    # -------------------------------------------------------------------------
    # STEP 2: Analyze a new bug
    # -------------------------------------------------------------------------
    print("\nAnalyzing new bug...")

    result = await wizard.analyze(
        {
            "error_message": "TypeError: Cannot read property 'map' of undefined",
            "file_path": "src/components/OrderList.tsx",
            "line_number": 47,
            "correlate_with_history": True,  # Enable historical matching
        },
    )

    # -------------------------------------------------------------------------
    # STEP 3: See the power of persistent memory
    # -------------------------------------------------------------------------
    print("\n" + "=" * 60)
    print("RESULTS: Bug Pattern Correlation")
    print("=" * 60)

    print(f"\nError Type: {result['error_classification']['error_type']}")
    print(f"Historical Matches: {result['matches_found']}")

    if result["historical_matches"]:
        print("\n📚 HISTORICAL MATCH FOUND:")
        match = result["historical_matches"][0]
        print(f"   Similarity: {match['similarity_score']:.0%}")
        print(f"   Root Cause: {match['root_cause']}")
        print(f"   Fix Applied: {match['fix_applied']}")
        print(f"   Resolution Time: {match['resolution_time_minutes']} minutes")

    if result["recommended_fix"]:
        print("\n💡 RECOMMENDED FIX:")
        fix = result["recommended_fix"]
        print(f"   {fix['original_fix']}")
        if fix.get("fix_code"):
            print(f"   Code: {fix['fix_code']}")

    print("\n📊 MEMORY BENEFIT:")
    benefit = result["memory_benefit"]
    print(f"   {benefit['value_statement']}")

    print("\n" + "=" * 60)
    print("Without persistent memory, you'd start from zero every time.")
    print("With Empathy Framework, your AI remembers and learns.")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())


# =============================================================================
# EXPECTED OUTPUT:
# =============================================================================
#
# Recording historical bug patterns...
#   ✓ Stored bug pattern from @sarah
#
# Analyzing new bug...
#
# ============================================================
# RESULTS: Bug Pattern Correlation
# ============================================================
#
# Error Type: null_reference
# Historical Matches: 1
#
# 📚 HISTORICAL MATCH FOUND:
#    Similarity: 85%
#    Root Cause: API returned null instead of empty array
#    Fix Applied: Added default empty array fallback: data?.items ?? []
#    Resolution Time: 15 minutes
#
# 💡 RECOMMENDED FIX:
#    Added default empty array fallback: data?.items ?? []
#    Code: const items = data?.items ?? [];
#
# 📊 MEMORY BENEFIT:
#    Persistent memory found 1 similar bugs. Without memory, you'd start from zero.
#
# ============================================================
# Without persistent memory, you'd start from zero every time.
# With Empathy Framework, your AI remembers and learns.
# ============================================================
