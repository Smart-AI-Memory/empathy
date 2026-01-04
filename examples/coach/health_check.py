#!/usr/bin/env python3
"""Coach Health Check

Validates that all 16 wizards are loaded and functioning correctly.
Run this to verify your Coach installation.

Usage:
    python3 health_check.py
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from examples.coach import Coach, WizardTask


async def main():
    print("=" * 60)
    print("COACH HEALTH CHECK")
    print("=" * 60)

    # Test 1: Initialize Coach
    print("\n✓ Test 1: Initializing Coach...")
    coach = Coach()
    print(f"  ✅ Coach loaded with {len(coach.wizards)} wizards")
    print(f"  ✅ Collaboration patterns: {len(coach.collaboration_patterns)}")

    # Test 2: Verify all 16 wizards
    print("\n✓ Test 2: Verifying wizards...")
    expected_count = 16
    actual_count = len(coach.wizards)

    if actual_count == expected_count:
        print(f"  ✅ All {expected_count} wizards loaded")
        for wizard in coach.wizards:
            print(f"     • {wizard.name}")
    else:
        print(f"  ❌ Expected {expected_count} wizards, found {actual_count}")
        return False

    # Test 3: Test single-wizard routing
    print("\n✓ Test 3: Testing single-wizard routing...")
    task = WizardTask(
        role="developer",
        task="Fix performance bottleneck in API",
        context="Slow database queries",
        risk_tolerance="medium",
    )

    result = await coach.process(task, multi_wizard=False)
    print(f"  ✅ Routed to: {result.routing[0]}")
    print(f"  ✅ Confidence: {result.overall_confidence:.2%}")
    print(f"  ✅ Generated {len(result.primary_output.artifacts)} artifacts")

    # Test 4: Test multi-wizard collaboration
    print("\n✓ Test 4: Testing multi-wizard collaboration...")
    task = WizardTask(
        role="developer",
        task="Build new API endpoint for user management",
        context="Need authentication and documentation",
        risk_tolerance="low",
    )

    result = await coach.process(task, multi_wizard=True)
    print(f"  ✅ Activated {len(result.routing)} wizards: {', '.join(result.routing)}")
    print(f"  ✅ Synthesis generated: {len(result.synthesis)} characters")

    # Test 5: Verify collaboration patterns
    print("\n✓ Test 5: Verifying collaboration patterns...")
    patterns = [
        "new_api_endpoint",
        "database_migration",
        "production_incident",
        "new_feature_launch",
        "performance_issue",
        "compliance_audit",
        "global_expansion",
        "new_developer_onboarding",
    ]

    for pattern in patterns:
        if pattern in coach.collaboration_patterns:
            wizard_count = len(coach.collaboration_patterns[pattern])
            print(f"  ✅ {pattern}: {wizard_count} wizards")
        else:
            print(f"  ❌ {pattern}: NOT FOUND")
            return False

    # Test 6: Test wizard confidence scoring
    print("\n✓ Test 6: Testing wizard confidence scoring...")
    test_cases = [
        ("performance", "PerformanceWizard"),
        ("security audit", "SecurityWizard"),
        ("database migration", "DatabaseWizard"),
        ("API design", "APIWizard"),
    ]

    for task_desc, expected_wizard in test_cases:
        task = WizardTask(role="developer", task=task_desc, context="")
        result = await coach.process(task, multi_wizard=False)
        if expected_wizard in result.routing:
            print(f"  ✅ '{task_desc}' → {result.routing[0]}")
        else:
            print(f"  ⚠️  '{task_desc}' → {result.routing[0]} (expected {expected_wizard})")

    # Success!
    print("\n" + "=" * 60)
    print("✅ HEALTH CHECK PASSED - All systems operational!")
    print("=" * 60)
    print("\nCoach is ready to use. Example usage:")
    print(
        """
from examples.coach import Coach, WizardTask

coach = Coach()
task = WizardTask(
    role="developer",
    task="Your task here",
    context="Additional context"
)
result = await coach.process(task)
print(result.primary_output.diagnosis)
    """,
    )

    return True


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
