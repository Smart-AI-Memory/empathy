"""
Empathy Framework - Quickstart Example

A simple demonstration of the Empathy Framework showing:
- Initializing EmpathyOS
- Progressing through empathy levels 1-5
- Using systems thinking components
- Pattern detection and sharing

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from empathy_os import (
    EmpathyOS,
    Level1Reactive,
    Level2Guided,
    Level3Proactive,
    Level4Anticipatory,
    Level5Systems,
    PatternLibrary,
    Pattern,
    FeedbackLoopDetector,
    ValidationError,
    EmpathyFrameworkError,
)


def main():
    """Run quickstart demonstration"""

    try:
        print("=" * 60)
        print("Empathy Framework - Quickstart Example")
        print("=" * 60)

    # ========================================
    # Part 1: Initialize EmpathyOS
    # ========================================
    print("\n[Part 1] Initializing EmpathyOS")
    print("-" * 60)

    empathy = EmpathyOS(
        user_id="quickstart_user",
        target_level=4,
        confidence_threshold=0.75
    )

    print(f"✓ Created EmpathyOS instance")
    print(f"  - User ID: {empathy.user_id}")
    print(f"  - Target Level: {empathy.target_level}")
    print(f"  - Initial Trust: {empathy.collaboration_state.trust_level:.2f}")

    # ========================================
    # Part 2: Demonstrate Five Empathy Levels
    # ========================================
    print("\n[Part 2] Demonstrating Five Empathy Levels")
    print("-" * 60)

    # Level 1: Reactive
    print("\nLevel 1: Reactive Empathy (Help after being asked)")
    level1 = Level1Reactive()
    response1 = level1.respond({"request": "status", "subject": "project"})
    print(f"  Action: {response1['action']}")
    print(f"  Initiative: {response1['initiative']}")
    print(f"  Description: {response1['description']}")

    # Level 2: Guided
    print("\nLevel 2: Guided Empathy (Collaborative exploration)")
    level2 = Level2Guided()
    response2 = level2.respond({"request": "improve system", "ambiguity": "high"})
    print(f"  Action: {response2['action']}")
    print(f"  Initiative: {response2['initiative']}")
    print(f"  Questions: {len(response2['clarifying_questions'])} clarifying questions")

    # Level 3: Proactive
    print("\nLevel 3: Proactive Empathy (Act before being asked)")
    level3 = Level3Proactive()
    response3 = level3.respond({"observed_need": "failing_tests", "confidence": 0.9})
    print(f"  Action: {response3['action']}")
    print(f"  Initiative: {response3['initiative']}")
    print(f"  Confidence: {response3['confidence']:.2f}")

    # Level 4: Anticipatory
    print("\nLevel 4: Anticipatory Empathy (Predict future needs)")
    level4 = Level4Anticipatory()
    response4 = level4.respond({
        "current_state": {"compliance": 0.7},
        "trajectory": "declining",
        "prediction_horizon": "30_days"
    })
    print(f"  Action: {response4['action']}")
    print(f"  Initiative: {response4['initiative']}")
    print(f"  Predicted Needs: {len(response4['predicted_needs'])}")
    for i, need in enumerate(response4['predicted_needs'], 1):
        print(f"    {i}. {need}")

    # Level 5: Systems
    print("\nLevel 5: Systems Empathy (Build structures at scale)")
    level5 = Level5Systems()
    response5 = level5.respond({
        "problem_class": "documentation_burden",
        "instances": 18,
        "pattern": "repetitive_structure"
    })
    print(f"  Action: {response5['action']}")
    print(f"  Initiative: {response5['initiative']}")
    print(f"  System Created: {response5['system_created']['name']}")
    print(f"  Leverage Point: {response5['leverage_point']}")

    # ========================================
    # Part 3: Pattern Library (Level 5)
    # ========================================
    print("\n[Part 3] Pattern Library - AI-AI Cooperation")
    print("-" * 60)

    library = PatternLibrary()

    # Agent 1 contributes a pattern
    print("\nAgent 1: Contributing pattern to library")
    pattern1 = Pattern(
        id="pat_001",
        agent_id="agent_1",
        pattern_type="sequential",
        name="Post-deployment documentation",
        description="After deployments, users need help finding changed features",
        confidence=0.85,
        tags=["deployment", "documentation"]
    )
    library.contribute_pattern("agent_1", pattern1)
    print(f"  ✓ Pattern '{pattern1.name}' contributed")
    print(f"  Confidence: {pattern1.confidence:.2f}")

    # Agent 2 queries for relevant patterns
    print("\nAgent 2: Querying library for deployment-related patterns")
    context = {
        "recent_event": "deployment",
        "user_confusion": True,
        "tags": ["deployment"]
    }
    matches = library.query_patterns("agent_2", context, min_confidence=0.7)
    print(f"  ✓ Found {len(matches)} relevant patterns")

    if matches:
        match = matches[0]
        print(f"  Pattern: {match.pattern.name}")
        print(f"  Relevance: {match.relevance_score:.2f}")
        print(f"  Matching Factors: {', '.join(match.matching_factors)}")

    # Record pattern usage
    print("\nAgent 2: Using pattern and recording outcome")
    library.record_pattern_outcome("pat_001", success=True)
    pattern1_updated = library.get_pattern("pat_001")
    print(f"  ✓ Pattern usage recorded")
    print(f"  Usage count: {pattern1_updated.usage_count}")
    print(f"  Success rate: {pattern1_updated.success_rate:.2f}")

    # Library stats
    stats = library.get_library_stats()
    print("\nLibrary Statistics:")
    print(f"  Total patterns: {stats['total_patterns']}")
    print(f"  Total agents: {stats['total_agents']}")
    print(f"  Average confidence: {stats['average_confidence']:.2f}")

    # ========================================
    # Part 4: Feedback Loops
    # ========================================
    print("\n[Part 4] Feedback Loop Detection")
    print("-" * 60)

    detector = FeedbackLoopDetector()

    # Simulate a virtuous cycle (trust building)
    print("\nDetecting feedback loops in collaboration history:")
    history = [
        {"trust": 0.5, "success": True},
        {"trust": 0.6, "success": True},
        {"trust": 0.7, "success": True},
        {"trust": 0.8, "success": True}
    ]

    result = detector.detect_active_loop(history)
    print(f"  Dominant Loop: {result['dominant_loop']}")
    print(f"  Loop Type: {result['loop_type']}")
    print(f"  Trend: {result['trend']}")
    print(f"  Recommendation: {result['recommendation']}")

    is_virtuous = detector.detect_virtuous_cycle(history)
    print(f"\n  Virtuous Cycle Detected: {is_virtuous}")

    # ========================================
    # Part 5: Trust Tracking
    # ========================================
    print("\n[Part 5] Trust Tracking Over Time")
    print("-" * 60)

    print("\nSimulating collaboration sessions:")
    print(f"  Initial trust: {empathy.collaboration_state.trust_level:.2f}")

    # Successful interactions
    for i in range(3):
        empathy.collaboration_state.update_trust("success")
        print(f"  After success {i+1}: {empathy.collaboration_state.trust_level:.2f}")

    print(f"\n  Final trust level: {empathy.collaboration_state.trust_level:.2f}")
    print(f"  Successful interventions: {empathy.collaboration_state.successful_interventions}")
    print(f"  Total interactions: {empathy.collaboration_state.total_interactions}")

    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 60)
    print("Quickstart Complete!")
    print("=" * 60)
    print("\nYou've learned:")
    print("  ✓ How to initialize EmpathyOS")
    print("  ✓ The five empathy levels (1-5)")
    print("  ✓ Pattern library for AI-AI cooperation")
    print("  ✓ Feedback loop detection")
    print("  ✓ Trust tracking")
    print("\nNext Steps:")
    print("  - Explore individual modules in more detail")
    print("  - Build custom agents using the framework")
    print("  - Integrate with your AI applications")
    print("  - Contribute patterns to the library")
        print("\nDocumentation: https://github.com/Deep-Study-AI/Empathy")
        print("=" * 60)

    except ValidationError as e:
        print(f"\n❌ Validation Error: {e}")
        print("Please check your input parameters and try again.")
        return 1
    except EmpathyFrameworkError as e:
        print(f"\n❌ Empathy Framework Error: {type(e).__name__}: {e}")
        print("Check the error message above for details.")
        return 1
    except KeyError as e:
        print(f"\n❌ Missing Required Field: {e}")
        print("Check that all required fields are present in the data.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}: {e}")
        print("Please check the documentation or file an issue.")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
