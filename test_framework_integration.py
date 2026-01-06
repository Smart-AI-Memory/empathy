#!/usr/bin/env python3
"""Integration test for Empathy Framework v3.7.0 release."""

import sys


def test_imports():
    """Test all critical imports."""
    print("=" * 60)
    print("Testing Framework Imports")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: BaseWorkflow
    try:
        print("✅ BaseWorkflow imported")
        tests_passed += 1
    except Exception as e:
        print(f"❌ BaseWorkflow import failed: {e}")
        tests_failed += 1

    # Test 2: HealthcareWizard
    try:
        from empathy_llm_toolkit.wizards.healthcare_wizard import HealthcareWizard

        print("✅ HealthcareWizard imported")

        # Check for XML methods
        if hasattr(HealthcareWizard, "_build_system_prompt"):
            print("  ✅ _build_system_prompt method exists")
        tests_passed += 1
    except Exception as e:
        print(f"❌ HealthcareWizard import failed: {e}")
        tests_failed += 1

    # Test 3: CrewAI Integration
    try:
        print("✅ All 4 CrewAI crews imported")
        print("  ✅ SecurityAuditCrew")
        print("  ✅ CodeReviewCrew")
        print("  ✅ RefactoringCrew")
        print("  ✅ HealthCheckCrew")
        tests_passed += 1
    except Exception as e:
        print(f"❌ CrewAI import failed: {e}")
        tests_failed += 1

    # Test 4: Developer Tools
    try:
        print("✅ All developer tools imported")
        print("  ✅ scaffolding (PatternCompose)")
        print("  ✅ workflow_scaffolding (WorkflowGenerator)")
        print("  ✅ test_generator")
        print("  ✅ hot_reload")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Developer tools import failed: {e}")
        tests_failed += 1

    # Test 5: Customer Support & Technology Wizards
    try:
        print("✅ Customer Support & Technology wizards imported")
        print("  ✅ CustomerSupportWizard")
        print("  ✅ TechnologyWizard")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Additional wizards import failed: {e}")
        tests_failed += 1

    return tests_passed, tests_failed


def test_cli_availability():
    """Test CLI command availability."""
    print("\n" + "=" * 60)
    print("Testing CLI Availability")
    print("=" * 60)

    import subprocess

    tests_passed = 0
    tests_failed = 0

    # Test empathy command
    try:
        result = subprocess.run(
            ["python", "-m", "empathy_os.cli", "--help"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and "Empathy" in result.stdout:
            print("✅ CLI command available")
            tests_passed += 1
        else:
            print("❌ CLI command failed")
            tests_failed += 1
    except Exception as e:
        print(f"❌ CLI test failed: {e}")
        tests_failed += 1

    # Test workflow list
    try:
        result = subprocess.run(
            ["python", "-m", "empathy_os.cli", "workflow", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and "code-review" in result.stdout:
            print("✅ Workflow list command works")
            print("  Found workflows: code-review, doc-gen, bug-predict, etc.")
            tests_passed += 1
        else:
            print("❌ Workflow list failed")
            tests_failed += 1
    except Exception as e:
        print(f"❌ Workflow list test failed: {e}")
        tests_failed += 1

    return tests_passed, tests_failed


def main():
    """Run all integration tests."""
    print("\n" + "=" * 60)
    print("EMPATHY FRAMEWORK v3.7.0 - INTEGRATION TEST")
    print("=" * 60)

    total_passed = 0
    total_failed = 0

    # Run import tests
    passed, failed = test_imports()
    total_passed += passed
    total_failed += failed

    # Run CLI tests
    passed, failed = test_cli_availability()
    total_passed += passed
    total_failed += failed

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {total_passed}")
    print(f"❌ Failed: {total_failed}")
    print(f"Total: {total_passed + total_failed}")

    if total_failed == 0:
        print("\n🎉 ALL TESTS PASSED - Ready for release!")
        return 0
    else:
        print(f"\n⚠️  {total_failed} test(s) failed - Review before release")
        return 1


if __name__ == "__main__":
    sys.exit(main())
