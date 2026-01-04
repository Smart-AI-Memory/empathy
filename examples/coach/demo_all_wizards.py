"""Comprehensive Coach Demo - All 6 Wizards + Multi-Agent Learning

Demonstrates all wizards and how they learn from each other.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from examples.coach import Coach, WizardTask
from examples.coach.shared_learning import get_shared_learning


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_wizard_output(result, show_artifacts=False):
    """Print formatted wizard output"""
    print(f"🎯 Routing: {' + '.join(result.routing)}")
    print(f"📊 Confidence: {result.overall_confidence:.1%}\n")
    print(f"💡 Diagnosis: {result.primary_output.diagnosis}\n")

    if show_artifacts:
        print(f"📦 Artifacts ({len(result.primary_output.artifacts)}):")
        for artifact in result.primary_output.artifacts:
            print(f"   • {artifact.type.upper()}: {artifact.title}")
        print()

    print("🎬 Top Next Actions:")
    for action in result.primary_output.next_actions[:3]:
        print(f"   ✓ {action}")
    print()


def demo_1_debugging():
    """Demo 1: Debugging Wizard"""
    print_section("WIZARD 1: Debugging - Production Bug")

    task = WizardTask(
        role="developer",
        task="Critical bug: Users cannot log in, 500 errors",
        context="Authentication service throwing NullPointerException. Logs show config value is null. Production down.",
        preferences="Urgent fix needed",
        risk_tolerance="low",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern in shared learning
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="DebuggingWizard",
        pattern_type="null_pointer_fix",
        description="Add null guard and default config value",
        code="if config is None: config = get_default()",
        tags=["debugging", "null", "config"],
        context={"severity": "critical", "type": "auth"},
    )

    print("✓ DebuggingWizard contributed pattern to shared learning\n")


def demo_2_documentation():
    """Demo 2: Documentation Wizard"""
    print_section("WIZARD 2: Documentation - Onboarding Gap")

    task = WizardTask(
        role="team_lead",
        task="New developers taking 3 days to get set up instead of 1",
        context="README missing database setup, environment config unclear, no local dev guide",
        preferences="Quick start for beginners",
        risk_tolerance="medium",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="DocumentationWizard",
        pattern_type="setup_guide",
        description="Step-by-step setup guide with prerequisites and verification",
        code="# Prerequisites\n# Installation\n# Configuration\n# Verify",
        tags=["documentation", "onboarding", "setup"],
        context={"audience": "beginners"},
    )

    print("✓ DocumentationWizard contributed pattern to shared learning\n")


def demo_3_design_review():
    """Demo 3: Design Review Wizard"""
    print_section("WIZARD 3: Design Review - Microservices Architecture")

    task = WizardTask(
        role="architect",
        task="Architecture review needed for new microservices design",
        context="Planning to split monolith into microservices. Need to evaluate trade-offs, scalability, and operational complexity.",
        preferences="Detailed analysis of trade-offs",
        risk_tolerance="low",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="DesignReviewWizard",
        pattern_type="architecture_decision",
        description="Microservices trade-off analysis with ADR",
        code="ADR template with context, decision, consequences",
        tags=["architecture", "microservices", "tradeoffs"],
        context={"pattern": "microservices"},
    )

    print("✓ DesignReviewWizard contributed pattern to shared learning\n")


def demo_4_testing():
    """Demo 4: Testing Wizard"""
    print_section("WIZARD 4: Testing - Low Coverage")

    task = WizardTask(
        role="developer",
        task="Test coverage is only 40%, need to improve to 80%",
        context="Authentication module untested. No integration tests. Missing edge case tests.",
        preferences="Prioritized test plan",
        risk_tolerance="medium",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="TestingWizard",
        pattern_type="test_plan",
        description="Coverage improvement plan with prioritized scenarios",
        code="def test_authentication(): # AAA pattern",
        tags=["testing", "coverage", "test_plan"],
        context={"coverage_target": 80},
    )

    print("✓ TestingWizard contributed pattern to shared learning\n")


def demo_5_retrospective():
    """Demo 5: Retrospective Wizard"""
    print_section("WIZARD 5: Retrospective - Team Process Improvement")

    task = WizardTask(
        role="team_lead",
        task="Team retrospective needed after tough sprint",
        context="Team stressed from deadline pressure. Communication issues. Some technical debt accumulated.",
        preferences="Mad Sad Glad format",
        risk_tolerance="low",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="RetrospectiveWizard",
        pattern_type="retro_format",
        description="Mad Sad Glad format for processing team emotions",
        code="# Mad: frustrations\n# Sad: disappointments\n# Glad: wins",
        tags=["retrospective", "team", "morale"],
        context={"team_health": "stressed"},
    )

    print("✓ RetrospectiveWizard contributed pattern to shared learning\n")


def demo_6_security():
    """Demo 6: Security Wizard"""
    print_section("WIZARD 6: Security - Security Review")

    task = WizardTask(
        role="developer",
        task="Security audit needed before launch",
        context="Web application with user authentication, payment processing, personal data storage. Need OWASP review.",
        preferences="Comprehensive security checklist",
        risk_tolerance="low",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_wizard_output(result, show_artifacts=True)

    # Record pattern
    learning = get_shared_learning()
    learning.contribute_pattern(
        wizard_name="SecurityWizard",
        pattern_type="threat_model",
        description="STRIDE threat modeling for web applications",
        code="# Spoofing\n# Tampering\n# Repudiation\n# Info Disclosure\n# DoS\n# Elevation",
        tags=["security", "threat_model", "STRIDE"],
        context={"compliance": ["PCI-DSS", "GDPR"]},
    )

    print("✓ SecurityWizard contributed pattern to shared learning\n")


def demo_7_multi_wizard():
    """Demo 7: Multi-Wizard Collaboration"""
    print_section("WIZARD 7: Multi-Wizard - Complex Incident")

    task = WizardTask(
        role="team_lead",
        task="Production incident: Security breach via SQL injection",
        context="Attacker exploited SQL injection in search endpoint. Need to fix bug, document incident, improve testing, review security.",
        preferences="Comprehensive incident response",
        risk_tolerance="low",
    )

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print(f"🎯 Multi-Wizard Routing: {' → '.join(result.routing)}")
    print(f"📊 Overall Confidence: {result.overall_confidence:.1%}\n")

    print("🔄 Wizard Collaboration:\n")
    print(f"  Primary: {result.primary_output.wizard_name}")
    print(f"    → {result.primary_output.diagnosis}\n")

    if result.secondary_outputs:
        print(f"  Secondary Wizards ({len(result.secondary_outputs)}):")
        for output in result.secondary_outputs:
            print(f"    → {output.wizard_name}: {output.diagnosis}")
        print()

    print("💡 Synthesized Recommendations:")
    print(f"{result.synthesis}\n")

    # Record collaborations
    learning = get_shared_learning()
    if len(result.routing) > 1:
        learning.record_collaboration(result.routing[0], result.routing[1])
        print(f"✓ Recorded collaboration: {result.routing[0]} ↔ {result.routing[1]}\n")


def demo_8_learning_summary():
    """Demo 8: Show Shared Learning"""
    print_section("MULTI-AGENT LEARNING SUMMARY")

    learning = get_shared_learning()

    # Show learning summary
    summary = learning.get_learning_summary()
    print(summary)

    # Show collaboration stats
    print("\n## Collaboration Network")
    collab_stats = learning.get_collaboration_stats()
    for pair, count in collab_stats.items():
        print(f"  {pair}: {count} collaborations")

    # Demonstrate pattern query
    print("\n## Pattern Query Example")
    print("Querying for 'security' patterns...\n")

    security_patterns = learning.query_patterns(tags=["security"])
    for pattern in security_patterns[:3]:
        print(f"  • {pattern.name}")
        print(f"    Type: {pattern.pattern_type}")
        print(f"    By: {pattern.agent_id}")
        print(f"    Success: {pattern.success_rate:.1%}\n")


def main():
    """Run all demos"""
    print("\n" + "🤖 " * 30)
    print("  COACH - Complete Wizard Collection + Multi-Agent Learning")
    print("  Demonstrating 6 Specialized Wizards with Shared Intelligence")
    print("🤖 " * 30)

    demos = [
        ("1. Debugging Wizard", demo_1_debugging),
        ("2. Documentation Wizard", demo_2_documentation),
        ("3. Design Review Wizard", demo_3_design_review),
        ("4. Testing Wizard", demo_4_testing),
        ("5. Retrospective Wizard", demo_5_retrospective),
        ("6. Security Wizard", demo_6_security),
        ("7. Multi-Wizard Collaboration", demo_7_multi_wizard),
        ("8. Learning Summary", demo_8_learning_summary),
    ]

    for name, demo_func in demos:
        demo_func()
        if demo_func != demo_8_learning_summary:
            input(
                f"\n{'─' * 80}\n Press Enter for next demo: {demos[demos.index((name, demo_func)) + 1][0] if demos.index((name, demo_func)) < len(demos) - 1 else 'Summary'}...",
            )

    print_section("DEMO COMPLETE")
    print("Coach now demonstrates:")
    print("  ✓ 6 specialized wizards (Debugging, Docs, Design, Testing, Retro, Security)")
    print("  ✓ Multi-wizard collaboration on complex tasks")
    print("  ✓ Shared pattern library for cross-wizard learning")
    print("  ✓ Cognitive, emotional, and anticipatory empathy at every level")
    print("  ✓ Production-ready artifacts for real development work")
    print("\nBuilt on the Empathy Framework - Production-ready anticipatory AI collaboration! 🚀")


if __name__ == "__main__":
    main()
