"""
Empathy LLM Toolkit - Demonstration

Shows progression from Level 1 to Level 4 empathy with an LLM.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import asyncio
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from empathy_llm_toolkit import EmpathyLLM, PatternType, UserPattern


async def demo_level_progression():
    """
    Demonstrate automatic progression through empathy levels.

    Shows how LLM behavior changes as trust builds and patterns emerge.
    """
    print("=" * 80)
    print("Empathy LLM Toolkit - Level Progression Demo")
    print("=" * 80)

    # Initialize (requires API key in environment or pass directly)
    llm = EmpathyLLM(
        provider="anthropic",
        target_level=4,  # Target: Anticipatory
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022",
    )

    user_id = "demo_developer"

    # INTERACTION 1: Level 1 (Reactive)
    print("\n" + "─" * 80)
    print("INTERACTION 1: Level 1 (Reactive)")
    print("─" * 80)

    response = await llm.interact(user_id=user_id, user_input="What is a REST API?")

    print(f"Level Used: {response['level_used']} - {response['level_description']}")
    print(f"Proactive: {response['proactive']}")
    print(f"\nResponse:\n{response['content'][:500]}...")

    # Mark as successful
    llm.update_trust(user_id, "success")

    # INTERACTION 2: Level 2 (Guided)
    print("\n" + "─" * 80)
    print("INTERACTION 2: Level 2 (Guided)")
    print("─" * 80)

    response = await llm.interact(
        user_id=user_id, user_input="Help me build a user authentication system"
    )

    print(f"Level Used: {response['level_used']} - {response['level_description']}")
    print(f"Proactive: {response['proactive']}")
    print(f"\nResponse:\n{response['content'][:500]}...")

    llm.update_trust(user_id, "success")

    # Add pattern manually (normally detected automatically)
    print("\n" + "─" * 80)
    print("ADDING PATTERN: User always requests tests after writing code")
    print("─" * 80)

    llm.add_pattern(
        user_id=user_id,
        pattern=UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="wrote code",
            action="requests tests",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        ),
    )

    # Build trust to enable Level 3
    for _ in range(3):
        llm.update_trust(user_id, "success")

    # INTERACTION 3: Level 3 (Proactive)
    print("\n" + "─" * 80)
    print("INTERACTION 3: Level 3 (Proactive)")
    print("─" * 80)

    response = await llm.interact(user_id=user_id, user_input="I just wrote the login function")

    print(f"Level Used: {response['level_used']} - {response['level_description']}")
    print(f"Proactive: {response['proactive']}")
    if response["metadata"].get("pattern"):
        print(f"Pattern Detected: {response['metadata']['pattern']}")
    print(f"\nResponse:\n{response['content'][:500]}...")

    llm.update_trust(user_id, "success")

    # Continue building trust for Level 4
    for _ in range(5):
        # Simulate more interactions
        await llm.interact(user_id, f"Test question {_}")
        llm.update_trust(user_id, "success")

    # INTERACTION 4: Level 4 (Anticipatory)
    print("\n" + "─" * 80)
    print("INTERACTION 4: Level 4 (Anticipatory)")
    print("─" * 80)

    response = await llm.interact(
        user_id=user_id, user_input="I'm adding my 15th API endpoint to this service"
    )

    print(f"Level Used: {response['level_used']} - {response['level_description']}")
    print(f"Proactive: {response['proactive']}")
    print(f"Trajectory Analyzed: {response['metadata'].get('trajectory_analyzed', False)}")
    print(f"\nResponse:\n{response['content'][:800]}...")

    # STATISTICS
    print("\n" + "=" * 80)
    print("COLLABORATION STATISTICS")
    print("=" * 80)

    stats = llm.get_statistics(user_id)
    print(
        f"""
User: {stats['user_id']}
Session Duration: {stats['session_duration']:.0f}s
Total Interactions: {stats['total_interactions']}
Trust Level: {stats['trust_level']:.0%}
Success Rate: {stats['success_rate']:.0%}
Patterns Detected: {stats['patterns_detected']}
Current Level: {stats['current_level']}
Average Level: {stats['average_level']:.1f}
    """
    )


async def demo_forced_levels():
    """
    Demonstrate forcing specific levels for comparison.

    Shows how the same question gets different treatment at each level.
    """
    print("\n" + "=" * 80)
    print("Empathy LLM Toolkit - Forced Level Comparison Demo")
    print("=" * 80)

    llm = EmpathyLLM(provider="anthropic", target_level=4, api_key=os.getenv("ANTHROPIC_API_KEY"))

    user_input = "How should I structure my Python project?"

    for level in [1, 2, 3, 4]:
        print("\n" + "─" * 80)
        print(f"LEVEL {level}: {EmpathyLevel.get_description(level)}")
        print("─" * 80)

        response = await llm.interact(
            user_id="comparison_user", user_input=user_input, force_level=level
        )

        print(f"\nResponse:\n{response['content'][:400]}...")
        print(f"\nTokens Used: {response['metadata']['tokens_used']}")


async def demo_healthcare_use_case():
    """
    Demonstrate healthcare application with Level 4 anticipatory.

    Shows clinical documentation automation progressing to compliance monitoring.
    """
    print("\n" + "=" * 80)
    print("Healthcare Use Case - Clinical Documentation")
    print("=" * 80)

    llm = EmpathyLLM(provider="anthropic", target_level=4, api_key=os.getenv("ANTHROPIC_API_KEY"))

    clinician_id = "clinician_dr_smith"

    # Build up context and trust
    print("\nBuilding collaboration context...")

    # Simulate several successful documentation sessions
    for i in range(10):
        await llm.interact(
            clinician_id,
            f"Document patient visit {i}",
            context={"patient_id": f"patient_{i}", "chief_complaint": "routine checkup"},
        )
        llm.update_trust(clinician_id, "success")

    # Add pattern: clinician always documents vitals, allergies, meds
    llm.add_pattern(
        clinician_id,
        UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="patient visit",
            action="documents vitals, allergies, medications",
            confidence=0.90,
            occurrences=10,
            last_seen=datetime.now(),
            context={"domain": "clinical_documentation"},
        ),
    )

    # Level 3: Proactive pre-population
    print("\n" + "─" * 80)
    print("LEVEL 3: Proactive Pre-population")
    print("─" * 80)

    response = await llm.interact(clinician_id, "Seeing patient John Doe for follow-up")

    print(f"Response:\n{response['content'][:500]}...")

    # Continue building trust for Level 4
    for _ in range(5):
        llm.update_trust(clinician_id, "success")

    # Level 4: Anticipatory compliance monitoring
    print("\n" + "─" * 80)
    print("LEVEL 4: Anticipatory Compliance Monitoring")
    print("─" * 80)

    response = await llm.interact(
        clinician_id,
        "How am I doing on documentation quality?",
        context={
            "total_notes": 50,
            "last_audit": "2024-01-15",
            "next_audit_expected": "approximately 90 days",
        },
    )

    print(f"Response:\n{response['content'][:800]}...")


async def main():
    """Run all demos"""
    print("\nEmpathy LLM Toolkit Demonstrations\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY not set. Set it to run demos.")
        print("Export ANTHROPIC_API_KEY=your-key-here")
        return

    try:
        # Demo 1: Level progression
        await demo_level_progression()

        # Demo 2: Forced level comparison
        # await demo_forced_levels()

        # Demo 3: Healthcare use case
        # await demo_healthcare_use_case()

    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Import EmpathyLevel for demo
    from empathy_llm_toolkit.levels import EmpathyLevel

    asyncio.run(main())
