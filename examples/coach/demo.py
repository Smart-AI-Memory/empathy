"""
Coach Demo - Comprehensive Examples

Demonstrates Coach orchestration agent with various software development tasks.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from examples.coach import Coach, WizardTask


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_output(result):
    """Print formatted wizard output"""
    print(f"🎯 Routing: {' → '.join(result.routing)}")
    print(f"📊 Confidence: {result.overall_confidence:.1%}\n")

    print(f"📋 Diagnosis:")
    print(f"   {result.primary_output.diagnosis}\n")

    print(f"📝 Plan ({len(result.primary_output.plan)} steps):")
    for i, step in enumerate(result.primary_output.plan[:5], 1):
        print(f"   {i}. {step}")
    if len(result.primary_output.plan) > 5:
        print(f"   ... and {len(result.primary_output.plan) - 5} more steps")
    print()

    print(f"📦 Artifacts ({len(result.primary_output.artifacts)}):")
    for artifact in result.primary_output.artifacts:
        print(f"   • {artifact.type.upper()}: {artifact.title}")
    print()

    print(f"⚠️  Risks ({len(result.primary_output.risks)}):")
    for risk in result.primary_output.risks[:3]:
        print(f"   • {risk.risk}")
        print(f"     → Mitigation: {risk.mitigation}")
    print()

    print(f"🎬 Next Actions:")
    for action in result.primary_output.next_actions[:5]:
        print(f"   ✓ {action}")
    print()

    print(f"💙 Empathy Checks:")
    print(f"   🧠 Cognitive: {result.primary_output.empathy_checks.cognitive}")
    print(f"   💚 Emotional: {result.primary_output.empathy_checks.emotional}")
    print(f"   🎯 Anticipatory: {result.primary_output.empathy_checks.anticipatory}")


def demo_1_critical_bug():
    """Demo 1: Critical production bug"""
    print_section("DEMO 1: Critical Production Bug")

    task = WizardTask(
        role="developer",
        task="Critical bug blocks release; users reporting 500 errors",
        context="Service X returns 500 after deployment to production. Logs show NullPointerException in user authentication. README doesn't document hotfix process. PM asking for ETA.",
        preferences="Urgent; need patch and hotfix deployment guide",
        risk_tolerance="low"
    )

    print("👤 Role: Developer")
    print("📝 Task: Critical bug blocks release")
    print("⏰ Urgency: HIGH")
    print("🎲 Risk Tolerance: LOW\n")

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print_output(result)

    if result.secondary_outputs:
        print(f"\n🔄 Secondary Wizards ({len(result.secondary_outputs)}):")
        for output in result.secondary_outputs:
            print(f"   • {output.wizard_name}: {output.diagnosis}")


def demo_2_onboarding_docs():
    """Demo 2: Onboarding documentation"""
    print_section("DEMO 2: Onboarding Documentation Gap")

    task = WizardTask(
        role="team_lead",
        task="New developers struggling with setup; onboarding taking 3 days instead of 1",
        context="README missing environment configuration steps. No setup guide for local development. Junior devs confused about dependencies and database setup.",
        preferences="Quick start guide for beginners",
        risk_tolerance="medium"
    )

    print("👤 Role: Team Lead")
    print("📝 Task: Improve onboarding docs")
    print("⏰ Urgency: NORMAL")
    print("🎲 Risk Tolerance: MEDIUM\n")

    coach = Coach()
    result = coach.process(task, multi_wizard=False)

    print_output(result)


def demo_3_performance_issue():
    """Demo 3: Performance/timeout issue"""
    print_section("DEMO 3: Performance Issue")

    task = WizardTask(
        role="architect",
        task="Database queries timing out under load",
        context="Users experiencing 30+ second page loads. Database shows N+1 query problem in user dashboard. Needs investigation and optimization.",
        preferences="Root cause analysis and optimization plan",
        risk_tolerance="medium"
    )

    print("👤 Role: Architect")
    print("📝 Task: Investigate performance issue")
    print("⏰ Urgency: NORMAL")
    print("🎲 Risk Tolerance: MEDIUM\n")

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print_output(result)


def demo_4_handoff_scenario():
    """Demo 4: Urgent handoff"""
    print_section("DEMO 4: Urgent Handoff Scenario")

    task = WizardTask(
        role="developer",
        task="Emergency handoff - going on leave, feature half-done",
        context="Authentication refactor 60% complete. PR open but not reviewed. Database migration pending. Documentation exists but may be out of date.",
        preferences="Comprehensive handoff documentation",
        risk_tolerance="low"
    )

    print("👤 Role: Developer")
    print("📝 Task: Emergency handoff")
    print("⏰ Urgency: HIGH")
    print("🎲 Risk Tolerance: LOW\n")

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print_output(result)


def demo_5_fallback():
    """Demo 5: Unhandled task (fallback)"""
    print_section("DEMO 5: Fallback (Unknown Task Type)")

    task = WizardTask(
        role="pm",
        task="Need to schedule team retrospective",
        context="Team has been working on project for 3 months. Want to gather feedback and identify improvements.",
        preferences="Structured retrospective format",
        risk_tolerance="low"
    )

    print("👤 Role: PM")
    print("📝 Task: Schedule retrospective")
    print("⏰ Urgency: NORMAL")
    print("🎲 Risk Tolerance: LOW\n")

    coach = Coach()
    result = coach.process(task, multi_wizard=True)

    print_output(result)

    print("\n💡 Note: This task doesn't match any specific wizard (no 'Retrospective Wizard' yet)")
    print("   Coach provides fallback guidance using Empathy Framework Level 2.")


def main():
    """Run all demos"""
    print("\n" + "🤖 " * 20)
    print("  COACH - Empathy Framework Orchestration Agent")
    print("  Demonstration of Empathetic Software Development Assistance")
    print("🤖 " * 20)

    demos = [
        demo_1_critical_bug,
        demo_2_onboarding_docs,
        demo_3_performance_issue,
        demo_4_handoff_scenario,
        demo_5_fallback,
    ]

    for demo in demos:
        demo()
        input("\n Press Enter to continue to next demo...")

    print_section("DEMO COMPLETE")
    print("Coach demonstrates:")
    print("  ✓ Multi-wizard routing (debugging + docs)")
    print("  ✓ Cognitive empathy (role-aware responses)")
    print("  ✓ Emotional empathy (stress/urgency detection)")
    print("  ✓ Anticipatory empathy (proactive suggestions)")
    print("  ✓ Production-ready artifacts (patches, tests, checklists)")
    print("\nBuilt on the Empathy Framework - 5 levels of anticipatory AI collaboration.")


if __name__ == "__main__":
    main()
