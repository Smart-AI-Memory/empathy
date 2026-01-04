#!/usr/bin/env python3
"""Full Repository Test
====================

Runs all three memory-enhanced wizards against the actual Empathy Framework repo.
This is a robust real-world test of persistent memory features.

Usage:
    python examples/full_repo_test.py
"""

import asyncio
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from empathy_software_plugin.wizards import (
    MemoryEnhancedDebuggingWizard,
    SecurityLearningWizard,
    TechDebtWizard,
)


def print_header(title: str) -> None:
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_section(title: str) -> None:
    print(f"\n--- {title} ---\n")


# =============================================================================
# STAGE 1: BUG CORRELATION WITH REAL PATTERNS
# =============================================================================


async def stage1_bug_correlation():
    """Stage 1: Test bug correlation by:
    1. Seeding realistic bug patterns
    2. Simulating a new bug
    3. Finding historical matches
    """
    print_header("STAGE 1: Bug Pattern Correlation")

    pattern_path = Path("./patterns/repo_test/debugging")
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    # Seed realistic bugs from common Python/TypeScript patterns
    print_section("1.1 Seeding Historical Bug Patterns")

    historical_bugs = [
        {
            "bug_id": "bug_py_import_001",
            "date": (datetime.now() - timedelta(days=60)).isoformat(),
            "file_path": "empathy_os/core.py",
            "error_type": "import_error",
            "error_message": "ModuleNotFoundError: No module named 'redis'",
            "root_cause": "Redis not installed in environment",
            "fix_applied": "Added redis to requirements.txt and installed",
            "fix_code": "pip install redis",
            "resolution_time_minutes": 5,
            "resolved_by": "@developer",
            "status": "resolved",
        },
        {
            "bug_id": "bug_async_001",
            "date": (datetime.now() - timedelta(days=45)).isoformat(),
            "file_path": "empathy_os/memory/unified.py",
            "error_type": "async_timing",
            "error_message": "RuntimeWarning: coroutine was never awaited",
            "root_cause": "Missing await on async function call",
            "fix_applied": "Added await keyword to async memory operation",
            "fix_code": "result = await memory.store(pattern)",
            "resolution_time_minutes": 10,
            "resolved_by": "@developer",
            "status": "resolved",
        },
        {
            "bug_id": "bug_null_001",
            "date": (datetime.now() - timedelta(days=30)).isoformat(),
            "file_path": "empathy_software_plugin/wizards/base_wizard.py",
            "error_type": "null_reference",
            "error_message": "AttributeError: 'NoneType' object has no attribute 'get'",
            "root_cause": "Config not initialized before access",
            "fix_applied": "Added None check before accessing config",
            "fix_code": "if config is not None: value = config.get('key')",
            "resolution_time_minutes": 8,
            "resolved_by": "@developer",
            "status": "resolved",
        },
        {
            "bug_id": "bug_type_001",
            "date": (datetime.now() - timedelta(days=20)).isoformat(),
            "file_path": "empathy_llm_toolkit/security/pii_scrubber.py",
            "error_type": "type_mismatch",
            "error_message": "TypeError: expected str, got bytes",
            "root_cause": "File read in binary mode instead of text",
            "fix_applied": "Changed file open mode to 'r' with encoding",
            "fix_code": "with open(file, 'r', encoding='utf-8') as f:",
            "resolution_time_minutes": 12,
            "resolved_by": "@developer",
            "status": "resolved",
        },
    ]

    pattern_path.mkdir(parents=True, exist_ok=True)
    for bug in historical_bugs:
        with open(pattern_path / f"{bug['bug_id']}.json", "w") as f:
            json.dump(bug, f, indent=2)
    print(f"  ✓ Seeded {len(historical_bugs)} historical bug patterns")

    # Test correlation with different error types
    print_section("1.2 Testing Bug Correlation")

    test_bugs = [
        {
            "name": "Import Error",
            "error_message": "ModuleNotFoundError: No module named 'structlog'",
            "file_path": "src/empathy_os/logging_config.py",
        },
        {
            "name": "Async Issue",
            "error_message": "RuntimeWarning: coroutine 'analyze' was never awaited",
            "file_path": "empathy_software_plugin/wizards/security_analysis_wizard.py",
        },
        {
            "name": "Null Reference",
            "error_message": "AttributeError: 'NoneType' object has no attribute 'items'",
            "file_path": "empathy_os/pattern_library.py",
        },
    ]

    results = []
    for test in test_bugs:
        result = await wizard.analyze(
            {
                "error_message": test["error_message"],
                "file_path": test["file_path"],
                "correlate_with_history": True,
            },
        )

        results.append(
            {
                "test": test["name"],
                "matches": result["matches_found"],
                "confidence": result["confidence"],
                "recommended_fix": result.get("recommended_fix", {}).get("original_fix", "N/A"),
            },
        )

        print(f"\n  Test: {test['name']}")
        print(f"  Error: {test['error_message'][:50]}...")
        print(f"  Matches Found: {result['matches_found']}")
        if result["historical_matches"]:
            best = result["historical_matches"][0]
            print(f"  Best Match: {best['similarity_score']:.0%} similarity")
            print(f"  Recommended: {best['fix_applied'][:60]}...")

    print_section("1.3 Stage 1 Summary")
    total_matches = sum(r["matches"] for r in results)
    print(f"  Total historical correlations: {total_matches}")
    print(f"  Memory working: {'✓ YES' if total_matches > 0 else '✗ NO'}")

    return {"stage": 1, "total_matches": total_matches, "tests": results}


# =============================================================================
# STAGE 2: TECH DEBT SCAN OF FULL REPO
# =============================================================================


async def stage2_tech_debt():
    """Stage 2: Scan entire repo for technical debt"""
    print_header("STAGE 2: Tech Debt Trajectory Analysis")

    pattern_path = Path("./patterns/repo_test/tech_debt")
    wizard = TechDebtWizard(pattern_storage_path=str(pattern_path))

    # Seed historical data to enable trajectory
    print_section("2.1 Seeding Historical Snapshots")

    history_data = {
        "snapshots": [
            {
                "date": (datetime.now() - timedelta(days=90)).isoformat(),
                "total_items": 200,
                "by_type": {"todo": 120, "fixme": 40, "hack": 25, "temporary": 15},
                "by_severity": {"low": 80, "medium": 90, "high": 25, "critical": 5},
                "hotspots": [],
            },
            {
                "date": (datetime.now() - timedelta(days=60)).isoformat(),
                "total_items": 250,
                "by_type": {"todo": 150, "fixme": 50, "hack": 30, "temporary": 20},
                "by_severity": {"low": 100, "medium": 110, "high": 32, "critical": 8},
                "hotspots": [],
            },
            {
                "date": (datetime.now() - timedelta(days=30)).isoformat(),
                "total_items": 300,
                "by_type": {"todo": 180, "fixme": 60, "hack": 35, "temporary": 25},
                "by_severity": {"low": 120, "medium": 130, "high": 40, "critical": 10},
                "hotspots": [],
            },
        ],
    }

    pattern_path.mkdir(parents=True, exist_ok=True)
    with open(pattern_path / "debt_history.json", "w") as f:
        json.dump(history_data, f, indent=2)
    print("  ✓ Seeded 3 historical snapshots (90, 60, 30 days ago)")

    # Scan actual repo
    print_section("2.2 Scanning Full Repository")

    result = await wizard.analyze(
        {
            "project_path": ".",
            "track_history": True,
            "exclude_patterns": [
                "node_modules",
                "venv",
                ".git",
                "__pycache__",
                "patterns",
                "dist",
                "build",
                ".pytest_cache",
                "archived_wizards",
                "salvaged",
            ],
        },
    )

    print("\n  📊 CURRENT DEBT:")
    current = result["current_debt"]
    print(f"     Total Items: {current['total_items']}")
    print("\n     By Type:")
    for dtype, count in sorted(current["by_type"].items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"       {dtype}: {count}")
    print("\n     By Severity:")
    for sev, count in current["by_severity"].items():
        if count > 0:
            emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}.get(sev, "•")
            print(f"       {emoji} {sev}: {count}")

    if result["trajectory"]:
        traj = result["trajectory"]
        print("\n  📈 TRAJECTORY:")
        print(f"     Previous (30 days): {traj['previous_total']}")
        print(f"     Current: {traj['current_total']}")
        print(f"     Change: {traj['change_percent']:+.1f}%")
        print(f"     Trend: {traj['trend'].upper()}")
        print("\n  🔮 PROJECTIONS:")
        print(f"     30 days: {traj['projection_30_days']} items")
        print(f"     90 days: {traj['projection_90_days']} items")
        if traj["days_until_critical"]:
            print(f"     ⚠️ Days until 2x: {traj['days_until_critical']}")

    print_section("2.3 Top Hotspots")
    for i, hotspot in enumerate(result["hotspots"][:5], 1):
        print(f"  #{i}: {hotspot['file']}")
        print(f"      Items: {hotspot['debt_count']}, Score: {hotspot['severity_score']}")

    print_section("2.4 Stage 2 Summary")
    print(f"  Files scanned: {len(result.get('debt_items', []))} debt items found")
    print(f"  Trajectory enabled: {'✓ YES' if result['trajectory'] else '✗ NO'}")
    print(f"  History snapshots: {result['history_snapshots']}")

    return {
        "stage": 2,
        "total_items": current["total_items"],
        "trajectory": result["trajectory"],
        "hotspots": len(result["hotspots"]),
    }


# =============================================================================
# STAGE 3: SECURITY SCAN WITH LEARNING
# =============================================================================


async def stage3_security():
    """Stage 3: Security scan with false positive learning"""
    print_header("STAGE 3: Security Scan with Learning")

    pattern_path = Path("./patterns/repo_test/security")
    wizard = SecurityLearningWizard(pattern_storage_path=str(pattern_path))

    # Seed team decisions
    print_section("3.1 Seeding Team Security Decisions")

    decisions_data = {
        "decisions": [
            {
                "finding_hash": "hardcoded_secret",
                "decision": "false_positive",
                "reason": "Test fixtures and demo files - not real credentials",
                "decided_by": "@security_team",
                "decided_at": (datetime.now() - timedelta(days=30)).isoformat(),
                "applies_to": "all",
            },
            {
                "finding_hash": "insecure_random",
                "decision": "accepted",
                "reason": "Used for non-cryptographic purposes (IDs, sampling)",
                "decided_by": "@tech_lead",
                "decided_at": (datetime.now() - timedelta(days=45)).isoformat(),
                "applies_to": "all",
            },
            {
                "finding_hash": "eval",
                "decision": "false_positive",
                "reason": "Only in test code for dynamic assertions",
                "decided_by": "@security_team",
                "decided_at": (datetime.now() - timedelta(days=20)).isoformat(),
                "applies_to": "pattern",
            },
        ],
    }

    pattern_path.mkdir(parents=True, exist_ok=True)
    with open(pattern_path / "team_decisions.json", "w") as f:
        json.dump(decisions_data, f, indent=2)
    print(f"  ✓ Seeded {len(decisions_data['decisions'])} team decisions")

    # First scan WITHOUT learning
    print_section("3.2 Scan WITHOUT Learning (baseline)")

    result_without = await wizard.analyze(
        {
            "project_path": ".",
            "apply_learned_patterns": False,
            "exclude_patterns": [
                "node_modules",
                "venv",
                ".git",
                "__pycache__",
                "patterns",
                "dist",
                "build",
                ".pytest_cache",
                "archived_wizards",
                "salvaged",
            ],
            "scan_depth": "standard",
        },
    )

    print(f"  Raw findings: {result_without['raw_findings_count']}")
    print("  By severity:")
    for sev, count in result_without["summary"]["by_severity"].items():
        if count > 0:
            print(f"    {sev}: {count}")

    # Second scan WITH learning
    print_section("3.3 Scan WITH Learning (memory-enhanced)")

    result_with = await wizard.analyze(
        {
            "project_path": ".",
            "apply_learned_patterns": True,
            "exclude_patterns": [
                "node_modules",
                "venv",
                ".git",
                "__pycache__",
                "patterns",
                "dist",
                "build",
                ".pytest_cache",
                "archived_wizards",
                "salvaged",
            ],
            "scan_depth": "standard",
        },
    )

    print(f"  Raw findings: {result_with['raw_findings_count']}")
    print(f"  After learning: {result_with['summary']['total_after_learning']}")

    learning = result_with["learning_applied"]
    if learning["enabled"]:
        print("\n  🧠 LEARNING APPLIED:")
        print(f"     Suppressed: {learning['suppressed_count']} findings")
        print(f"     Noise reduction: {learning['noise_reduction_percent']}%")

        if learning["suppression_details"]:
            print("\n     Suppression details:")
            for detail in learning["suppression_details"][:5]:
                print(f"       • {detail['type']}: {detail['reason'][:40]}...")

    print("\n  Remaining findings by severity:")
    for sev, count in result_with["summary"]["by_severity"].items():
        if count > 0:
            emoji = {"critical": "🚨", "high": "⚠️", "medium": "📋", "low": "ℹ️"}.get(sev, "•")
            print(f"    {emoji} {sev}: {count}")

    print_section("3.4 Stage 3 Summary")
    raw = result_without["raw_findings_count"]
    after = result_with["summary"]["total_after_learning"]
    reduction = ((raw - after) / raw * 100) if raw > 0 else 0

    print(f"  Before learning: {raw} findings")
    print(f"  After learning: {after} findings")
    print(f"  Total noise reduction: {reduction:.1f}%")
    print(f"  Learning working: {'✓ YES' if learning['suppressed_count'] > 0 else '✗ NO'}")

    return {
        "stage": 3,
        "raw_findings": raw,
        "after_learning": after,
        "noise_reduction_percent": reduction,
        "suppressed": learning["suppressed_count"],
    }


# =============================================================================
# MAIN
# =============================================================================


async def main():
    print_header("FULL REPOSITORY TEST: Memory-Enhanced Wizards")
    print(
        """
Testing all three wizards against the actual Empathy Framework repo.
This validates that persistent memory features work with real data.
""",
    )

    results = {}

    # Stage 1: Bug Correlation
    results["bug_correlation"] = await stage1_bug_correlation()

    # Stage 2: Tech Debt
    results["tech_debt"] = await stage2_tech_debt()

    # Stage 3: Security
    results["security"] = await stage3_security()

    # Final Summary
    print_header("FINAL SUMMARY: All Stages Complete")

    print("\n  Stage 1 - Bug Correlation:")
    print(f"    Historical matches found: {results['bug_correlation']['total_matches']}")
    print(
        f"    Memory correlation: {'✓ WORKING' if results['bug_correlation']['total_matches'] > 0 else '✗ FAILED'}",
    )

    print("\n  Stage 2 - Tech Debt Trajectory:")
    print(f"    Debt items found: {results['tech_debt']['total_items']}")
    print(
        f"    Trajectory enabled: {'✓ WORKING' if results['tech_debt']['trajectory'] else '✗ FAILED'}",
    )
    if results["tech_debt"]["trajectory"]:
        print(f"    Current trend: {results['tech_debt']['trajectory']['trend']}")

    print("\n  Stage 3 - Security Learning:")
    print(f"    Raw findings: {results['security']['raw_findings']}")
    print(f"    After learning: {results['security']['after_learning']}")
    print(f"    Noise reduction: {results['security']['noise_reduction_percent']:.1f}%")
    print(
        f"    Learning applied: {'✓ WORKING' if results['security']['suppressed'] > 0 else '✗ FAILED'}",
    )

    # Overall verdict
    all_working = (
        results["bug_correlation"]["total_matches"] > 0
        and results["tech_debt"]["trajectory"] is not None
        and results["security"]["suppressed"] > 0
    )

    print("\n" + "=" * 70)
    if all_working:
        print("  ✅ ALL MEMORY FEATURES VALIDATED SUCCESSFULLY")
    else:
        print("  ⚠️  SOME FEATURES MAY NEED ATTENTION")
    print("=" * 70)

    return results


if __name__ == "__main__":
    asyncio.run(main())
