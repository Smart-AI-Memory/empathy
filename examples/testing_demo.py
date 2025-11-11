"""
Enhanced Testing Wizard - Live Demonstration

Shows test quality analysis and bug-risk prediction.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio

# Mock coverage data for demonstration
MOCK_COVERAGE_DATA = {
    "/project/src/api.py": {
        "lines_total": 150,
        "lines_covered": 90,
        "branches_total": 30,
        "branches_covered": 15,
    },
    "/project/src/auth.py": {
        "lines_total": 200,
        "lines_covered": 0,  # NO TESTS!
        "branches_total": 40,
        "branches_covered": 0,
    },
    "/project/src/utils.py": {
        "lines_total": 100,
        "lines_covered": 80,
        "branches_total": 20,
        "branches_covered": 18,
    },
}

# Mock source files with high-risk patterns
MOCK_AUTH_FILE = '''
def authenticate_user(username, password):
    """Authenticate user - CRITICAL: No tests for this!"""
    try:
        # High-risk: Database operation + auth logic
        user = db.query(f"SELECT * FROM users WHERE username = '{username}'")
        if user and user.password == password:
            return create_session(user)
    except Exception as e:
        # High-risk: Error handling
        return None
'''

MOCK_PAYMENT_FILE = '''
def calculate_total(items):
    """Calculate order total"""
    total = 0
    for item in items:
        # High-risk: Financial calculation
        price = item.price
        quantity = item.quantity
        total = total + (price * quantity)

    # High-risk: Rounding money
    return round(total, 2)

def process_payment(amount, card_number):
    """Process payment - user input!"""
    # High-risk: User input + financial transaction
    result = payment_gateway.charge(card_number, amount)
    return result
'''


async def demo_basic_analysis():
    """Demo 1: Basic Test Analysis"""
    print("=" * 70)
    print("DEMO 1: Basic Test Coverage & Quality Analysis")
    print("=" * 70)

    from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

    wizard = EnhancedTestingWizard()

    # Simulate project analysis
    result = await wizard.analyze(
        {
            "project_path": "/project",
            "coverage_report": MOCK_COVERAGE_DATA,
            "test_files": ["/project/tests/test_api.py", "/project/tests/test_utils.py"],
            "source_files": [
                "/project/src/api.py",
                "/project/src/auth.py",  # NO TESTS!
                "/project/src/utils.py",
                "/project/src/payment.py",  # NO TESTS!
            ],
        }
    )

    print("\n📊 Coverage Analysis:")
    coverage = result["coverage"]
    print(f"  Overall Coverage: {coverage['overall_coverage']:.1f}%")
    print(f"  Line Coverage: {coverage['line_coverage']:.1f}%")
    print(f"  Branch Coverage: {coverage['branch_coverage']:.1f}%")
    print(f"  Uncovered Lines: {coverage['uncovered_lines']}")

    print("\n📈 Test Quality:")
    quality = result["test_quality"]
    print(f"  Total Test Files: {quality['total_test_files']}")
    print(f"  Tests with Assertions: {quality['tests_with_assertions']}")
    print(f"  Quality Score: {quality['quality_score']:.1f}/100")
    print(f"  Test-to-Source Ratio: {quality['test_to_source_ratio']:.2f}:1")

    print("\n" + "=" * 70)


async def demo_risk_analysis():
    """Demo 2: Level 4 - Bug Risk Prediction"""
    print("\n" + "=" * 70)
    print("DEMO 2: Level 4 - Bug Risk Prediction for Untested Code")
    print("=" * 70)

    from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

    wizard = EnhancedTestingWizard()

    # Create temporary files for analysis
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        # Write mock files
        auth_file = os.path.join(tmpdir, "auth.py")
        payment_file = os.path.join(tmpdir, "payment.py")

        with open(auth_file, "w") as f:
            f.write(MOCK_AUTH_FILE)

        with open(payment_file, "w") as f:
            f.write(MOCK_PAYMENT_FILE)

        result = await wizard.analyze(
            {
                "project_path": tmpdir,
                "coverage_report": {},  # No coverage = untested
                "source_files": [auth_file, payment_file],
            }
        )

        print("\n⚠️  HIGH-RISK GAPS DETECTED:")
        print("\nIn our experience, these untested code patterns cause production bugs:\n")

        for gap in result["risk_gaps"][:5]:
            print(f"  [{gap['risk_level']}] {gap['file'].split('/')[-1]}")
            print(f"      Pattern: {gap['pattern']}")
            print(f"      Reason: {gap['reason']}")
            print(f"      Prediction: {gap['prediction']}")
            print()

    print("=" * 70)


async def demo_smart_suggestions():
    """Demo 3: Smart Test Suggestions"""
    print("\n" + "=" * 70)
    print("DEMO 3: Smart Test Suggestions Based on Risk")
    print("=" * 70)

    from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

    wizard = EnhancedTestingWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = os.path.join(tmpdir, "auth.py")
        with open(auth_file, "w") as f:
            f.write(MOCK_AUTH_FILE)

        result = await wizard.analyze(
            {"project_path": tmpdir, "coverage_report": {}, "source_files": [auth_file]}
        )

        print("\n🎯 SMART TEST SUGGESTIONS:\n")

        for suggestion in result["test_suggestions"][:3]:
            print(f"  Priority: {suggestion['priority']}")
            print(f"  File: {suggestion['file'].split('/')[-1]}")
            print(f"  Test Type: {suggestion['test_type']}")
            print(f"  Rationale: {suggestion['rationale']}")
            print("\n  Suggested Tests:")
            for test in suggestion["suggested_tests"]:
                print(f"    - {test}")
            print()

    print("=" * 70)


async def demo_predictions():
    """Demo 4: Level 4 Predictions"""
    print("\n" + "=" * 70)
    print("DEMO 4: Level 4 - Production Bug Predictions")
    print("=" * 70)

    from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

    wizard = EnhancedTestingWizard()

    with tempfile.TemporaryDirectory() as tmpdir:
        auth_file = os.path.join(tmpdir, "auth.py")
        payment_file = os.path.join(tmpdir, "payment.py")

        with open(auth_file, "w") as f:
            f.write(MOCK_AUTH_FILE)
        with open(payment_file, "w") as f:
            f.write(MOCK_PAYMENT_FILE)

        result = await wizard.analyze(
            {
                "project_path": tmpdir,
                "coverage_report": {},
                "source_files": [auth_file, payment_file],
            }
        )

        print("\n🔮 PREDICTIONS:\n")

        for pred in result["predictions"]:
            print(f"  Type: {pred['type'].upper()}")
            print(f"  Severity: {pred['severity'].upper()}")
            print(f"  {pred['description']}")

            if "affected_files" in pred:
                print("\n  Affected Files:")
                for file in pred["affected_files"][:3]:
                    print(f"    - {file.split('/')[-1]}")

            if "prevention_steps" in pred:
                print("\n  Prevention Steps:")
                for step in pred["prevention_steps"][:3]:
                    print(f"    - {step}")
            print()

    print("=" * 70)


async def demo_recommendations():
    """Demo 5: Actionable Recommendations"""
    print("\n" + "=" * 70)
    print("DEMO 5: Actionable Recommendations")
    print("=" * 70)

    from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard

    wizard = EnhancedTestingWizard()

    result = await wizard.analyze(
        {
            "project_path": "/project",
            "coverage_report": MOCK_COVERAGE_DATA,
            "test_files": ["/project/tests/test_api.py"],
            "source_files": [
                "/project/src/api.py",
                "/project/src/auth.py",
                "/project/src/utils.py",
            ],
        }
    )

    print("\n📝 RECOMMENDATIONS:\n")

    for rec in result["recommendations"]:
        print(f"  • {rec}")

    print("\n" + "=" * 70)


async def demo_the_value():
    """Demo 6: Show the Value"""
    print("\n" + "=" * 70)
    print("DEMO 6: The Value - Beyond Coverage Metrics")
    print("=" * 70)

    print("\n" + "TRADITIONAL TESTING METRICS".center(70))
    print("-" * 70)
    print("✓ Line coverage: 60%")
    print("✓ Branch coverage: 50%")
    print("")
    print("Status: PASSING ✓")
    print("")
    print("...but does this actually mean the code is safe?")

    print("\n" + "ENHANCED TESTING WIZARD".center(70))
    print("-" * 70)
    print("✓ Line coverage: 60%")
    print("✓ Branch coverage: 50%")
    print("✓ Test quality score: 45/100")
    print("")
    print("⚠️  CRITICAL: Authentication code has 0% coverage")
    print("⚠️  CRITICAL: Payment processing has 0% coverage")
    print("⚠️  HIGH: Error handling paths untested")
    print("")
    print("In our experience, untested authentication and payment")
    print("code causes the majority of production security incidents.")
    print("")
    print("Status: HIGH RISK - Not ready for production")

    print("\n" + "THE DIFFERENCE".center(70))
    print("-" * 70)
    print("Coverage tells you WHAT is tested.")
    print("Enhanced Testing tells you WHAT MATTERS is tested.")
    print("")
    print("It predicts which untested code will actually cause bugs.")

    print("\n" + "=" * 70)


async def main():
    """Run all demos"""

    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "ENHANCED TESTING WIZARD - DEMONSTRATIONS" + " " * 15 + "║")
    print("║" + " " * 16 + "Test Quality & Bug-Risk Prediction" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")

    await demo_basic_analysis()
    await demo_risk_analysis()
    await demo_smart_suggestions()
    await demo_predictions()
    await demo_recommendations()
    await demo_the_value()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Test coverage AND quality analysis")
    print("  ✅ Level 4: Predicts which untested code causes bugs")
    print("  ✅ High-risk pattern detection (auth, payments, errors)")
    print("  ✅ Smart test suggestions based on risk")
    print("  ✅ Beyond simple metrics - actual bug prevention")
    print("\nIn our experience, untested error handling and input validation")
    print("cause the majority of production incidents. This wizard helps you")
    print("focus testing effort where it matters most.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
