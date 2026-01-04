#!/usr/bin/env python3
"""Test Script for Memory-Enhanced Debugging Wizard

Demonstrates the wizard's capabilities:
- Error classification
- Historical pattern matching
- Fix recommendations based on past bugs
- Level 4 predictions

This script shows what's possible with persistent memory:
"This error looks like something we fixed 3 months ago - here's what worked."

Run: python examples/test_debugging_wizard.py

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import json
import sys
from pathlib import Path

# Add src directory to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root / "empathy_software_plugin"))

# Now import the wizard (after sys.path setup)
from wizards.memory_enhanced_debugging_wizard import MemoryEnhancedDebuggingWizard  # noqa: E402


def print_section(title: str, char: str = "=") -> None:
    """Print a formatted section header."""
    print(f"\n{char * 70}")
    print(title)
    print(char * 70)


def print_json(data: dict, indent: int = 2) -> None:
    """Pretty print JSON data."""
    print(json.dumps(data, indent=indent, default=str))


async def test_null_reference_error():
    """Test 1: TypeError - Cannot read property 'map' of undefined

    This should match historical bug bug_20250915_abc123.json
    which had the exact same error type and message.
    """
    print_section("Test 1: Null Reference Error (TypeError)")

    # Initialize wizard with the existing patterns directory
    pattern_path = project_root / "patterns" / "debugging"
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    print(f"\nWizard: {wizard.name}")
    print(f"Level: {wizard.level} (Level 4+ with memory enhancement)")
    print(f"Pattern storage: {wizard.pattern_storage_path}")

    # Count existing patterns
    existing_patterns = list(wizard.pattern_storage_path.glob("*.json"))
    print(f"Historical patterns available: {len(existing_patterns)}")

    # Analyze a similar error to what we've seen before
    context = {
        "error_message": "TypeError: Cannot read property 'map' of undefined",
        "file_path": "src/components/UserList.tsx",
        "stack_trace": """
        at UserList.render (UserList.tsx:45)
        at processChild (react-dom.development.js:1234)
        """,
        "line_number": 45,
        "code_snippet": """
        const UserList = ({ users }) => {
          return users.map(user => <UserCard user={user} />);
        }
        """,
        "correlate_with_history": True,
    }

    print("\n--- Input Context ---")
    print(f"Error: {context['error_message']}")
    print(f"File: {context['file_path']}")
    print(f"Line: {context['line_number']}")

    # Run analysis
    result = await wizard.analyze(context)

    print("\n--- Analysis Results ---")

    # Error Classification
    print("\n[Error Classification]")
    classification = result.get("error_classification", {})
    print(f"  Type: {classification.get('error_type', 'unknown')}")
    print(f"  File Type: {classification.get('file_type', 'unknown')}")

    # Likely Causes
    print("\n  Likely Causes:")
    for cause in classification.get("likely_causes", [])[:3]:
        print(f"    - {cause.get('cause')} (likelihood: {cause.get('likelihood', 0):.0%})")
        print(f"      Check: {cause.get('check')}")

    # Historical Matches (THE KEY FEATURE!)
    print("\n[Historical Matches]")
    matches = result.get("historical_matches", [])
    print(f"  Matches found: {result.get('matches_found', 0)}")

    if matches:
        print("\n  TOP MATCHES FROM MEMORY:")
        for i, match in enumerate(matches[:3], 1):
            print(f"\n  Match #{i} (similarity: {match.get('similarity_score', 0):.0%})")
            print(f"    Date: {match.get('date', 'unknown')}")
            print(f"    File: {match.get('file', 'unknown')}")
            print(f"    Root Cause: {match.get('root_cause', 'unknown')}")
            print(f"    Fix Applied: {match.get('fix_applied', 'unknown')}")
            if match.get("fix_code"):
                print(f"    Fix Code: {match.get('fix_code')}")
            print(f"    Resolution Time: {match.get('resolution_time_minutes', 0)} minutes")
            print(f"    Matching Factors: {', '.join(match.get('matching_factors', []))}")
    else:
        print("  No historical matches found - this is a new type of bug!")

    # Recommended Fix (based on history)
    print("\n[Recommended Fix]")
    rec_fix = result.get("recommended_fix")
    if rec_fix:
        print(f"  Based on: {rec_fix.get('based_on', 'N/A')}")
        print(f"  Original fix: {rec_fix.get('original_fix', 'N/A')}")
        if rec_fix.get("fix_code"):
            print(f"  Code example: {rec_fix.get('fix_code')}")
        print(f"  Expected resolution: {rec_fix.get('expected_resolution_time', 'N/A')}")
        print(f"  Confidence: {rec_fix.get('confidence', 0):.0%}")
        if rec_fix.get("adaptation_notes"):
            print("  Adaptation notes:")
            for note in rec_fix.get("adaptation_notes", []):
                print(f"    - {note}")
    else:
        print("  No recommendation available (insufficient historical data)")

    # Level 4 Predictions
    print("\n[Level 4 Predictions]")
    predictions = result.get("predictions", [])
    for pred in predictions:
        severity = pred.get("severity", "info")
        icon = {"high": "[!]", "medium": "[*]", "info": "[i]"}.get(severity, "[?]")
        print(f"\n  {icon} {pred.get('type', 'unknown')} ({severity})")
        print(f"      {pred.get('description', '')}")
        if pred.get("prevention_steps"):
            print("      Prevention steps:")
            for step in pred.get("prevention_steps", [])[:3]:
                print(f"        - {step}")

    # Recommendations
    print("\n[Recommendations]")
    for rec in result.get("recommendations", []):
        print(f"  {rec}")

    # Memory Benefit
    print("\n[Memory Benefit Analysis]")
    benefit = result.get("memory_benefit", {})
    print(f"  Matches found: {benefit.get('matches_found', 0)}")
    print(f"  Time saved estimate: {benefit.get('time_saved_estimate', 'N/A')}")
    print(f"  Value: {benefit.get('value_statement', 'N/A')}")
    if benefit.get("historical_insight"):
        print(f"  Insight: {benefit.get('historical_insight')}")

    print(f"\n  Overall Confidence: {result.get('confidence', 0):.0%}")

    return result


async def test_async_error():
    """Test 2: Async timing error

    Tests matching against async_timing patterns.
    """
    print_section("Test 2: Async Timing Error")

    pattern_path = project_root / "patterns" / "debugging"
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    context = {
        "error_message": "UnhandledPromiseRejection: await undefined",
        "file_path": "src/services/dataService.ts",
        "stack_trace": "at DataService.fetchData (dataService.ts:23)",
        "code_snippet": """
        async function fetchData() {
          const result = apiClient.getData();  // Missing await!
          return result.items;
        }
        """,
        "correlate_with_history": True,
    }

    print(f"\nError: {context['error_message']}")
    print(f"File: {context['file_path']}")

    result = await wizard.analyze(context)

    print("\n--- Results Summary ---")
    classification = result.get("error_classification", {})
    print(f"Classified as: {classification.get('error_type', 'unknown')}")
    print(f"Historical matches: {result.get('matches_found', 0)}")

    if result.get("recommended_fix"):
        print(f"Recommended: {result['recommended_fix'].get('original_fix', 'N/A')}")

    print(f"Confidence: {result.get('confidence', 0):.0%}")

    return result


async def test_import_error():
    """Test 3: Import/Module Error

    Tests matching against import_error patterns.
    """
    print_section("Test 3: Import Error")

    pattern_path = project_root / "patterns" / "debugging"
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    context = {
        "error_message": "ModuleNotFoundError: No module named 'pandas'",
        "file_path": "scripts/data_analysis.py",
        "stack_trace": "ImportError at line 1",
        "correlate_with_history": True,
    }

    print(f"\nError: {context['error_message']}")
    print(f"File: {context['file_path']}")

    result = await wizard.analyze(context)

    print("\n--- Results Summary ---")
    classification = result.get("error_classification", {})
    print(f"Classified as: {classification.get('error_type', 'unknown')}")
    print(f"Historical matches: {result.get('matches_found', 0)}")

    # Show likely causes for import errors
    print("\nLikely causes:")
    for cause in classification.get("likely_causes", []):
        print(f"  - {cause.get('cause')} ({cause.get('likelihood', 0):.0%})")

    return result


async def test_no_history_mode():
    """Test 4: Analysis without historical correlation

    Shows what the wizard does when you disable history matching.
    """
    print_section("Test 4: Without Historical Correlation")

    pattern_path = project_root / "patterns" / "debugging"
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    context = {
        "error_message": "TypeError: Cannot read property 'length' of undefined",
        "file_path": "src/utils/helpers.ts",
        "correlate_with_history": False,  # Disable history matching
    }

    print(f"\nError: {context['error_message']}")
    print("Historical correlation: DISABLED")

    result = await wizard.analyze(context)

    print("\n--- Results Summary ---")
    print(f"Classified as: {result.get('error_classification', {}).get('error_type', 'unknown')}")
    print(f"Historical matches: {result.get('matches_found', 0)} (disabled)")
    print(f"Confidence: {result.get('confidence', 0):.0%}")

    print("\nWithout memory, you get:")
    print("  - Basic error classification")
    print("  - Generic likely causes")
    print("  - No historical context")
    print("  - Lower confidence in recommendations")

    return result


async def demonstrate_resolution_recording():
    """Test 5: Demonstrate recording a bug resolution

    Shows how to store a fix for future correlation.
    """
    print_section("Test 5: Recording Bug Resolution (Demo)")

    pattern_path = project_root / "patterns" / "debugging"
    wizard = MemoryEnhancedDebuggingWizard(pattern_storage_path=str(pattern_path))

    # First, analyze a new bug
    context = {
        "error_message": "ReferenceError: fetchUser is not defined",
        "file_path": "src/components/Profile.tsx",
        "correlate_with_history": True,
    }

    print("\nStep 1: Analyze the bug")
    print(f"  Error: {context['error_message']}")

    result = await wizard.analyze(context)
    print(f"  Classified as: {result.get('error_classification', {}).get('error_type', 'unknown')}")

    # The bug was stored during analysis (status: "investigating")
    # Now show how you would record the resolution

    print("\nStep 2: After fixing, record the resolution")
    print("  (This would normally be called after you fix the bug)")
    print(
        """
    Example code to record resolution:

    await wizard.record_resolution(
        bug_id="bug_20251216_abc123",  # From analyze result
        root_cause="Function was imported with wrong name",
        fix_applied="Changed import from 'getUser' to 'fetchUser'",
        fix_code="import { fetchUser } from './api'",
        resolution_time_minutes=8,
        resolved_by="@developer"
    )
    """,
    )

    print("\nStep 3: Future benefit")
    print("  Next time someone sees 'is not defined' errors,")
    print("  the wizard will suggest: 'Check import names'")
    print("  and show the fix code from this resolution!")

    return result


async def main():
    """Run all tests demonstrating the Memory-Enhanced Debugging Wizard."""
    print_section("Memory-Enhanced Debugging Wizard - Test Suite", "=")
    print(
        """
This test demonstrates what's possible with PERSISTENT MEMORY:

WITHOUT PERSISTENT MEMORY (Before):
  - Every debugging session starts from zero
  - Same bugs diagnosed repeatedly
  - Fix knowledge lost between sessions
  - No learning from team's collective experience

WITH PERSISTENT MEMORY (After):
  - AI remembers past bugs and fixes
  - "This looks like bug #247 from 3 months ago"
  - Recommends proven fixes
  - Team knowledge compounds over time
""",
    )

    # Run tests
    await test_null_reference_error()
    await test_async_error()
    await test_import_error()
    await test_no_history_mode()
    await demonstrate_resolution_recording()

    # Summary
    print_section("Summary", "=")
    print(
        """
Key Takeaways:

1. HISTORICAL MATCHING: The wizard searches stored bug patterns
   and finds similar past bugs with their fixes.

2. SIMILARITY SCORING: Matches are ranked by:
   - Error type (40% weight)
   - File type (15% weight)
   - File location patterns (15% weight)
   - Error message similarity (30% weight)

3. FIX RECOMMENDATIONS: When a match is found, the wizard
   recommends the same fix that worked before.

4. LEVEL 4 PREDICTIONS: The wizard predicts:
   - Related bugs that might occur
   - Estimated resolution time
   - Recurring patterns that need systematic fixes

5. KNOWLEDGE ACCUMULATION: Each resolved bug is stored,
   building team knowledge over time.

Pattern storage location: ./patterns/debugging/
""",
    )

    print("\nTest suite completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())
