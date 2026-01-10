#!/usr/bin/env python3
"""Meta-Orchestrator Demo.

This script demonstrates how the MetaOrchestrator analyzes tasks and
composes agent teams with different execution strategies.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator


def demo_task_analysis():
    """Demonstrate task analysis and agent composition."""
    orchestrator = MetaOrchestrator()

    # Example tasks
    tasks = [
        {
            "description": "Boost test coverage to 90%",
            "context": {"current_coverage": 75},
        },
        {
            "description": "Perform comprehensive security audit",
            "context": {"version": "3.12.0"},
        },
        {
            "description": "Prepare for v3.12.0 release",
            "context": {"quality_gates": {"min_coverage": 80}},
        },
        {
            "description": "Update API documentation",
            "context": {},
        },
        {
            "description": "Refactor code to reduce complexity",
            "context": {"max_complexity": 10},
        },
    ]

    print("=" * 80)
    print("META-ORCHESTRATOR DEMO")
    print("=" * 80)
    print()

    for i, task_info in enumerate(tasks, 1):
        print(f"\n{i}. Task: {task_info['description']}")
        print("-" * 80)

        # Analyze and compose
        plan = orchestrator.analyze_and_compose(
            task=task_info["description"], context=task_info["context"]
        )

        # Print results
        print(f"   Strategy: {plan.strategy.value}")
        print(f"   Agents ({len(plan.agents)}):")
        for agent in plan.agents:
            print(f"      - {agent.role} ({agent.tier_preference})")
        print(f"   Estimated Cost: ${plan.estimated_cost:.2f}")
        print(f"   Estimated Duration: {plan.estimated_duration}s")
        if plan.quality_gates:
            print(f"   Quality Gates: {plan.quality_gates}")


def demo_composition_patterns():
    """Demonstrate different composition patterns."""
    orchestrator = MetaOrchestrator()

    patterns = {
        "Sequential": "improve test coverage for authentication module",
        "Parallel": "prepare for production release with full validation",
        "Teaching": "create comprehensive API documentation",
        "Refinement": "refactor legacy code to improve maintainability",
    }

    print("\n" + "=" * 80)
    print("COMPOSITION PATTERNS DEMO")
    print("=" * 80)
    print()

    for pattern_name, task in patterns.items():
        print(f"\n{pattern_name} Pattern")
        print("-" * 80)
        print(f"Task: {task}")

        plan = orchestrator.analyze_and_compose(task)

        print(f"Selected Strategy: {plan.strategy.value}")
        print(
            f"Agent Team: {', '.join([a.role for a in plan.agents[:3]])}{'...' if len(plan.agents) > 3 else ''}"
        )


if __name__ == "__main__":
    demo_task_analysis()
    demo_composition_patterns()

    print("\n" + "=" * 80)
    print("Demo complete!")
    print("=" * 80)
