"""
Advanced Debugging Wizard - Live Demonstration

Shows how to use the protocol-based debugging wizard.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio
import json

# Mock ESLint output for demonstration
MOCK_ESLINT_OUTPUT = json.dumps(
    [
        {
            "filePath": "/project/src/api.js",
            "messages": [
                {
                    "line": 42,
                    "column": 8,
                    "severity": 2,
                    "message": "'fetchData' is not defined",
                    "ruleId": "no-undef",
                },
                {
                    "line": 108,
                    "column": 15,
                    "severity": 2,
                    "message": "Expected '===' and instead saw '=='",
                    "ruleId": "eqeqeq",
                },
                {
                    "line": 200,
                    "column": 5,
                    "severity": 1,
                    "message": "'unusedVariable' is assigned a value but never used",
                    "ruleId": "no-unused-vars",
                },
                {
                    "line": 303,
                    "column": 12,
                    "severity": 1,
                    "message": "Missing semicolon",
                    "ruleId": "semi",
                    "fix": {"range": [1234, 1234], "text": ";"},
                },
            ],
        }
    ]
)

# Mock Pylint output
MOCK_PYLINT_OUTPUT = json.dumps(
    [
        {
            "path": "/project/src/utils.py",
            "line": 25,
            "column": 4,
            "type": "error",
            "message": "Undefined variable 'database_connection'",
            "message-id": "E0602",
            "symbol": "undefined-variable",
        },
        {
            "path": "/project/src/utils.py",
            "line": 67,
            "column": 8,
            "type": "warning",
            "message": "Dangerous default value [] as argument",
            "message-id": "W0102",
            "symbol": "dangerous-default-value",
        },
        {
            "path": "/project/src/models.py",
            "line": 12,
            "column": 0,
            "type": "convention",
            "message": "Missing module docstring",
            "message-id": "C0114",
            "symbol": "missing-docstring",
        },
    ]
)


async def demo_basic_analysis():
    """Demo 1: Basic linter analysis"""
    print("=" * 70)
    print("DEMO 1: Basic Linter Analysis")
    print("=" * 70)

    from empathy_software_plugin.wizards.advanced_debugging_wizard import AdvancedDebuggingWizard

    wizard = AdvancedDebuggingWizard()

    # Analyze with mock linter outputs
    result = await wizard.analyze(
        {
            "project_path": "/project",
            "linters": {"eslint": MOCK_ESLINT_OUTPUT, "pylint": MOCK_PYLINT_OUTPUT},
        }
    )

    print(f"\n📊 Issues Found: {result['issues_found']}")
    print("\nLinters:")
    for linter, data in result["linters"].items():
        print(f"  - {linter}: {data['total_issues']} issues")

    print("\n⚠️  Risk Assessment:")
    risk = result["risk_assessment"]
    print(f"  Alert Level: {risk['alert_level']}")
    print(f"  Critical: {risk['by_risk_level']['critical']}")
    print(f"  High: {risk['by_risk_level']['high']}")
    print(f"  Medium: {risk['by_risk_level']['medium']}")

    print("\n💡 Recommendation:")
    print(f"  {risk['recommendation']}")

    print("\n" + "=" * 70)


async def demo_risk_analysis():
    """Demo 2: Level 4 Risk Analysis"""
    print("\n" + "=" * 70)
    print("DEMO 2: Level 4 - Risk Analysis & Predictions")
    print("=" * 70)

    from empathy_software_plugin.wizards.advanced_debugging_wizard import AdvancedDebuggingWizard

    wizard = AdvancedDebuggingWizard()

    result = await wizard.analyze(
        {
            "project_path": "/project",
            "linters": {"eslint": MOCK_ESLINT_OUTPUT, "pylint": MOCK_PYLINT_OUTPUT},
        }
    )

    print("\n🔮 Predictions:")
    for i, prediction in enumerate(result["predictions"], 1):
        print(f"\n  {i}. {prediction['type'].upper()}")
        print(f"     Severity: {prediction['severity']}")
        print(f"     {prediction['description']}")
        print("     Prevention:")
        for step in prediction["prevention_steps"]:
            print(f"       - {step}")

    print("\n📈 Trajectory Analysis:")
    trajectory = result["trajectory"]
    print(f"  State: {trajectory['state']}")
    print(f"  Total Issues: {trajectory['total_issues']}")
    print(f"  Critical: {trajectory['critical_issues']}")
    if trajectory["concern"]:
        print(f"  ⚠️  Concern: {trajectory['concern']}")
    print(f"  Recommendation: {trajectory['recommendation']}")

    print("\n" + "=" * 70)


async def demo_cross_language_patterns():
    """Demo 3: Level 5 Cross-Language Patterns"""
    print("\n" + "=" * 70)
    print("DEMO 3: Level 5 - Cross-Language Pattern Learning")
    print("=" * 70)

    from empathy_software_plugin.wizards.debugging.language_patterns import get_pattern_library

    pattern_lib = get_pattern_library()

    # Show pattern library summary
    summary = pattern_lib.generate_pattern_summary()

    print("\n📚 Pattern Library:")
    print(f"  Total Patterns: {summary['total_patterns']}")
    print(f"  Languages Covered: {summary['languages_covered']}")

    print("\n🌍 Universal Patterns:")
    for pattern_info in summary["patterns"][:3]:
        print(f"\n  {pattern_info['name']}")
        print(f"    Category: {pattern_info['category']}")
        print(f"    Languages: {', '.join(pattern_info['languages'])}")
        print(f"    Why it matters: {pattern_info['why_it_matters']}")

    # Show cross-language insight
    print("\n🔗 Cross-Language Insight Example:")
    insight = pattern_lib.suggest_cross_language_insight(
        from_language="javascript", to_language="python", pattern_name="undefined_reference"
    )

    if insight:
        print(f"\n{insight}")

    print("\n" + "=" * 70)


async def demo_fixability_analysis():
    """Demo 4: Fixability Analysis"""
    print("\n" + "=" * 70)
    print("DEMO 4: Fixability Analysis")
    print("=" * 70)

    from empathy_software_plugin.wizards.advanced_debugging_wizard import AdvancedDebuggingWizard

    wizard = AdvancedDebuggingWizard()

    result = await wizard.analyze(
        {
            "project_path": "/project",
            "linters": {"eslint": MOCK_ESLINT_OUTPUT, "pylint": MOCK_PYLINT_OUTPUT},
        }
    )

    print("\n🔧 Fixability by Linter:")
    for linter, fixability in result["fixability"].items():
        print(f"\n  {linter}:")
        print(f"    ✅ Auto-fixable: {fixability['auto_fixable']}")
        print(f"    ✋ Manual: {fixability['manual']}")

    print("\n📝 Recommendations:")
    for rec in result["recommendations"]:
        print(f"  {rec}")

    print("\n" + "=" * 70)


async def demo_complete_workflow():
    """Demo 5: Complete Workflow (Dry Run)"""
    print("\n" + "=" * 70)
    print("DEMO 5: Complete Workflow (Dry Run)")
    print("=" * 70)

    from empathy_software_plugin.wizards.advanced_debugging_wizard import AdvancedDebuggingWizard

    wizard = AdvancedDebuggingWizard()

    print("\n1️⃣  Parsing linter outputs...")
    print("2️⃣  Loading configurations...")
    print("3️⃣  Analyzing bug risks (Level 4)...")
    print("4️⃣  Grouping by fixability...")
    print("5️⃣  Identifying cross-language patterns (Level 5)...")
    print("6️⃣  Analyzing trajectory...")

    result = await wizard.analyze(
        {
            "project_path": "/project",
            "linters": {"eslint": MOCK_ESLINT_OUTPUT, "pylint": MOCK_PYLINT_OUTPUT},
            "auto_fix": False,  # Dry run
            "verify": False,
        }
    )

    print("\n✅ Analysis Complete!\n")

    print("📊 Summary:")
    print(f"  Total Issues: {result['issues_found']}")
    print(f"  Alert Level: {result['risk_assessment']['alert_level']}")
    print(f"  Trajectory: {result['trajectory']['state']}")

    auto_fixable = sum(f["auto_fixable"] for f in result["fixability"].values())
    print(f"  Auto-fixable: {auto_fixable}")

    print("\n🎯 Top Risk Issues:")
    for risk in result["risk_assessment"]["top_risks"][:3]:
        issue = risk["issue"]
        print(f"  - {issue['file_path']}:{issue['line']}")
        print(f"    Rule: {issue['rule']}")
        print(f"    Risk: {risk['risk_level'].upper()}")
        print(f"    Impact: {risk['impact']}")

    print("\n" + "=" * 70)


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 10 + "ADVANCED DEBUGGING WIZARD - DEMONSTRATIONS" + " " * 16 + "║")
    print("║" + " " * 20 + "Protocol-Based Debugging" + " " * 24 + "║")
    print("╚" + "=" * 68 + "╝")

    await demo_basic_analysis()
    await demo_risk_analysis()
    await demo_cross_language_patterns()
    await demo_fixability_analysis()
    await demo_complete_workflow()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Protocol-based debugging (linting pattern)")
    print("  ✅ Level 4: Anticipatory risk analysis")
    print("  ✅ Level 4: Trajectory prediction")
    print("  ✅ Level 5: Cross-language pattern learning")
    print("  ✅ Systematic fix workflow")
    print("\nIn our experience, this approach transforms debugging from")
    print("reactive firefighting to proactive quality management.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
