"""Advanced Composition Patterns

This file demonstrates advanced meta-orchestration techniques:
- Custom agent templates
- Strategy comparison and selection
- Performance optimization
- Complex multi-pattern workflows

For experienced users who want to push the system to its limits.

Run:
    python advanced_composition.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from empathy_os.orchestration.agent_templates import (
    AgentTemplate,
    ResourceRequirements,
    get_template,
)
from empathy_os.orchestration.execution_strategies import (
    AdaptiveStrategy,
    DebateStrategy,
    ParallelStrategy,
    RefinementStrategy,
    SequentialStrategy,
    TeachingStrategy,
    get_strategy,
)
from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator
from empathy_os.orchestration.config_store import ConfigurationStore


# =============================================================================
# Example 1: Custom Agent Template
# =============================================================================


def example1_custom_agent_template():
    """Create and use a custom agent template."""
    print("\n" + "=" * 60)
    print("Example 1: Custom Agent Template")
    print("=" * 60)

    # Define custom agent template
    custom_template = AgentTemplate(
        id="data_pipeline_expert",
        role="Data Pipeline Specialist",
        capabilities=[
            "pipeline_design",
            "data_validation",
            "performance_tuning",
            "fault_tolerance",
        ],
        tier_preference="CAPABLE",
        tools=["spark", "airflow", "dbt", "great_expectations"],
        default_instructions="""
You are a data pipeline expert specializing in production-ready ETL systems.

Your responsibilities:
1. Design scalable, fault-tolerant data pipelines
2. Implement comprehensive data quality validation
3. Optimize pipeline performance and resource usage
4. Ensure proper monitoring, alerting, and observability

Focus on:
- Production readiness and reliability
- Data quality and integrity
- Performance and cost optimization
- Maintainability and documentation

Best practices:
- Idempotent operations
- Proper error handling and retry logic
- Data lineage tracking
- Cost-effective resource allocation
        """.strip(),
        quality_gates={
            "min_data_quality_score": 99.0,
            "max_pipeline_latency_seconds": 60,
            "min_fault_tolerance_score": 95.0,
        },
        resource_requirements=ResourceRequirements(
            min_tokens=3000,
            max_tokens=25000,
            timeout_seconds=900,
            memory_mb=2048,
        ),
    )

    print(f"\n✅ Custom Agent Created:")
    print(f"  ID: {custom_template.id}")
    print(f"  Role: {custom_template.role}")
    print(f"  Tier: {custom_template.tier_preference}")
    print(f"  Capabilities: {', '.join(custom_template.capabilities)}")
    print(f"  Tools: {', '.join(custom_template.tools)}")
    print(f"\n  Quality Gates:")
    for gate, threshold in custom_template.quality_gates.items():
        print(f"    • {gate}: {threshold}")
    print(f"\n  Resources:")
    print(
        f"    • Tokens: {custom_template.resource_requirements.min_tokens}-{custom_template.resource_requirements.max_tokens}"
    )
    print(f"    • Timeout: {custom_template.resource_requirements.timeout_seconds}s")
    print(f"    • Memory: {custom_template.resource_requirements.memory_mb}MB")

    return custom_template


# =============================================================================
# Example 2: Strategy Comparison
# =============================================================================


async def example2_strategy_comparison():
    """Compare all 6 composition strategies."""
    print("\n" + "=" * 60)
    print("Example 2: Strategy Comparison")
    print("=" * 60)

    # Get agents
    agents = [
        get_template("test_coverage_analyzer"),
        get_template("code_reviewer"),
        get_template("documentation_writer"),
    ]

    context = {"project_root": ".", "mode": "analysis"}

    strategies = [
        ("Sequential", SequentialStrategy()),
        ("Parallel", ParallelStrategy()),
        ("Debate", DebateStrategy()),
        ("Teaching", TeachingStrategy(quality_threshold=0.7)),
        ("Refinement", RefinementStrategy()),
        ("Adaptive", AdaptiveStrategy()),
    ]

    print(f"\n🤖 Testing with {len(agents)} agents\n")

    results = []

    for name, strategy in strategies:
        print(f"⚡ {name} Strategy:")

        # Adjust agents for strategies with specific requirements
        if name == "Teaching":
            # Teaching requires exactly 2 agents
            test_agents = agents[:2]
        elif name == "Adaptive":
            # Adaptive requires classifier + specialists
            test_agents = agents
        else:
            test_agents = agents

        start_time = time.perf_counter()

        try:
            result = await strategy.execute(test_agents, context)
            duration = time.perf_counter() - start_time

            results.append(
                {
                    "strategy": name,
                    "success": result.success,
                    "duration": duration,
                    "agents": len(result.outputs),
                }
            )

            print(f"  Duration: {duration:.2f}s")
            print(f"  Success: {result.success}")
            print(f"  Agents: {len(result.outputs)}")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append(
                {
                    "strategy": name,
                    "success": False,
                    "duration": 0.0,
                    "agents": 0,
                }
            )

        print()

    # Summary
    print("📊 Summary:")
    for r in results:
        status = "✅" if r["success"] else "❌"
        print(f"  {status} {r['strategy']:12s}: {r['duration']:.2f}s")

    # Fastest
    successful = [r for r in results if r["success"]]
    if successful:
        fastest = min(successful, key=lambda x: x["duration"])
        print(f"\n⚡ Fastest: {fastest['strategy']} ({fastest['duration']:.2f}s)")


# =============================================================================
# Example 3: Hybrid Strategy Workflow
# =============================================================================


async def example3_hybrid_strategy_workflow():
    """Workflow using multiple strategies in sequence."""
    print("\n" + "=" * 60)
    print("Example 3: Hybrid Strategy Workflow")
    print("=" * 60)

    context = {"project_root": ".", "phase": 1}

    # Phase 1: Parallel exploration
    print("\n  Phase 1: PARALLEL - Explore multiple approaches")
    parallel_agents = [
        get_template("architecture_analyst"),
        get_template("performance_optimizer"),
        get_template("security_auditor"),
    ]

    parallel_strategy = ParallelStrategy()
    phase1_result = await parallel_strategy.execute(parallel_agents, context)

    print(f"    Duration: {phase1_result.total_duration:.2f}s")
    print(f"    Success: {phase1_result.success}")

    # Phase 2: Debate on best approach
    print("\n  Phase 2: DEBATE - Synthesize findings")

    debate_agents = [
        get_template("architecture_analyst"),
        get_template("architecture_analyst"),  # Different perspectives
    ]

    debate_context = {
        **context,
        "phase1_findings": phase1_result.aggregated_output,
    }

    debate_strategy = DebateStrategy()
    phase2_result = await debate_strategy.execute(debate_agents, debate_context)

    print(f"    Duration: {phase2_result.total_duration:.2f}s")
    print(f"    Consensus: {phase2_result.aggregated_output['consensus']['consensus_reached']}")

    # Phase 3: Sequential implementation
    print("\n  Phase 3: SEQUENTIAL - Implement chosen approach")

    sequential_agents = [
        get_template("refactoring_specialist"),
        get_template("test_coverage_analyzer"),
        get_template("code_reviewer"),
    ]

    sequential_context = {
        **debate_context,
        "phase2_decision": phase2_result.aggregated_output,
    }

    sequential_strategy = SequentialStrategy()
    phase3_result = await sequential_strategy.execute(sequential_agents, sequential_context)

    print(f"    Duration: {phase3_result.total_duration:.2f}s")
    print(f"    Success: {phase3_result.success}")

    # Summary
    total_duration = (
        phase1_result.total_duration + phase2_result.total_duration + phase3_result.total_duration
    )

    print(f"\n✅ Hybrid Workflow Complete!")
    print(f"  Total Duration: {total_duration:.2f}s")
    print(f"  Phases: 3")
    print(f"  Total Agents: {len(parallel_agents) + len(debate_agents) + len(sequential_agents)}")


# =============================================================================
# Example 4: Cost-Optimized Workflow
# =============================================================================


async def example4_cost_optimized_workflow():
    """Workflow optimized for cost using tier selection."""
    print("\n" + "=" * 60)
    print("Example 4: Cost-Optimized Workflow")
    print("=" * 60)

    orchestrator = MetaOrchestrator()

    # Scenario 1: Simple task → Use cheap agents
    print("\n  Scenario 1: Simple task (documentation)")

    simple_plan = orchestrator.analyze_and_compose(
        task="Generate API documentation", context={"complexity": "low"}
    )

    print(f"    Agents: {[a.id for a in simple_plan.agents]}")
    print(f"    Tiers: {[a.tier_preference for a in simple_plan.agents]}")
    print(f"    Estimated Cost: {simple_plan.estimated_cost:.2f} units")

    # Scenario 2: Complex task → Use premium agents
    print("\n  Scenario 2: Complex task (security audit)")

    complex_plan = orchestrator.analyze_and_compose(
        task="Comprehensive security audit for production release",
        context={"complexity": "high", "criticality": "production"},
    )

    print(f"    Agents: {[a.id for a in complex_plan.agents]}")
    print(f"    Tiers: {[a.tier_preference for a in complex_plan.agents]}")
    print(f"    Estimated Cost: {complex_plan.estimated_cost:.2f} units")

    # Scenario 3: Teaching strategy for cost optimization
    print("\n  Scenario 3: Teaching strategy (junior + expert)")

    teaching_agents = [
        get_template("documentation_writer"),  # CHEAP
        get_template("code_reviewer"),  # CAPABLE (expert)
    ]

    teaching_strategy = TeachingStrategy(quality_threshold=0.7)
    teaching_result = await teaching_strategy.execute(
        teaching_agents, {"task": "Document API endpoints"}
    )

    outcome = teaching_result.aggregated_output["outcome"]
    print(f"    Outcome: {outcome}")

    if outcome == "junior_success":
        print(f"    💰 Cost Saved: ~70% (junior succeeded)")
    else:
        print(f"    💰 Cost: Full (expert intervention required)")

    # Cost comparison
    print(f"\n💰 Cost Analysis:")
    print(f"  Simple task:  {simple_plan.estimated_cost:.2f} units")
    print(f"  Complex task: {complex_plan.estimated_cost:.2f} units")
    print(f"  Savings (teaching): Up to 70% when junior succeeds")


# =============================================================================
# Example 5: Configuration Store Deep Dive
# =============================================================================


async def example5_configuration_store():
    """Advanced configuration store usage."""
    print("\n" + "=" * 60)
    print("Example 5: Configuration Store Deep Dive")
    print("=" * 60)

    store = ConfigurationStore()

    # Search configurations
    print("\n  Searching configurations:")

    all_configs = store.list_all()
    print(f"    Total configurations: {len(all_configs)}")

    if all_configs:
        print(f"\n  Recent configurations:")
        for config in all_configs[:5]:
            print(f"    • {config.id}")
            print(f"      Pattern: {config.task_pattern}")
            print(f"      Success Rate: {config.success_rate:.1%}")
            print(f"      Quality Score: {config.avg_quality_score:.1f}/100")
            print(f"      Uses: {config.usage_count}")

    # Search by criteria
    print(f"\n  High-performing configurations (>80% success):")

    high_performers = store.search(min_success_rate=0.8, min_quality_score=75.0, limit=5)

    for config in high_performers:
        print(f"    • {config.id}: {config.success_rate:.1%} @ {config.avg_quality_score:.1f}")

    # Task-specific search
    print(f"\n  Release preparation configurations:")

    release_configs = store.search(task_pattern="release_preparation", limit=3)

    for config in release_configs:
        print(f"    • {config.id}")
        print(f"      Strategy: {config.strategy}")
        print(f"      Agents: {len(config.agents)}")


# =============================================================================
# Example 6: Performance Monitoring
# =============================================================================


@dataclass
class PerformanceMetrics:
    """Performance metrics for workflow execution."""

    strategy_name: str
    agent_count: int
    total_duration: float
    avg_agent_duration: float
    parallelization_factor: float = 1.0
    success_rate: float = 0.0


async def example6_performance_monitoring():
    """Monitor and analyze performance metrics."""
    print("\n" + "=" * 60)
    print("Example 6: Performance Monitoring")
    print("=" * 60)

    agents = [
        get_template("test_coverage_analyzer"),
        get_template("code_reviewer"),
        get_template("security_auditor"),
    ]

    context = {"project_root": "."}

    metrics: list[PerformanceMetrics] = []

    # Test sequential
    print("\n  Testing SEQUENTIAL:")
    sequential = SequentialStrategy()
    result = await sequential.execute(agents, context)

    seq_avg_duration = sum(r.duration_seconds for r in result.outputs) / len(result.outputs)

    metrics.append(
        PerformanceMetrics(
            strategy_name="Sequential",
            agent_count=len(agents),
            total_duration=result.total_duration,
            avg_agent_duration=seq_avg_duration,
            parallelization_factor=1.0,
            success_rate=sum(1 for r in result.outputs if r.success) / len(result.outputs),
        )
    )

    print(f"    Total: {result.total_duration:.2f}s")
    print(f"    Avg per agent: {seq_avg_duration:.2f}s")

    # Test parallel
    print("\n  Testing PARALLEL:")
    parallel = ParallelStrategy()
    result = await parallel.execute(agents, context)

    par_avg_duration = sum(r.duration_seconds for r in result.outputs) / len(result.outputs)

    # Calculate speedup
    speedup = seq_avg_duration * len(agents) / result.total_duration

    metrics.append(
        PerformanceMetrics(
            strategy_name="Parallel",
            agent_count=len(agents),
            total_duration=result.total_duration,
            avg_agent_duration=par_avg_duration,
            parallelization_factor=speedup,
            success_rate=sum(1 for r in result.outputs if r.success) / len(result.outputs),
        )
    )

    print(f"    Total: {result.total_duration:.2f}s")
    print(f"    Avg per agent: {par_avg_duration:.2f}s")
    print(f"    Speedup: {speedup:.2f}x")

    # Summary
    print(f"\n📊 Performance Summary:")
    for m in metrics:
        print(f"\n  {m.strategy_name}:")
        print(f"    Agents: {m.agent_count}")
        print(f"    Total Duration: {m.total_duration:.2f}s")
        print(f"    Avg Agent Duration: {m.avg_agent_duration:.2f}s")
        print(f"    Speedup: {m.parallelization_factor:.2f}x")
        print(f"    Success Rate: {m.success_rate:.1%}")


# =============================================================================
# Example 7: Dynamic Agent Selection
# =============================================================================


async def example7_dynamic_agent_selection():
    """Dynamically select agents based on runtime conditions."""
    print("\n" + "=" * 60)
    print("Example 7: Dynamic Agent Selection")
    print("=" * 60)

    # Simulate runtime conditions
    conditions = {
        "code_quality_issues": 15,
        "security_alerts": 2,
        "test_coverage": 65.0,
        "performance_issues": 8,
    }

    print(f"\n  Runtime Conditions:")
    for key, value in conditions.items():
        print(f"    • {key}: {value}")

    # Dynamic agent selection
    selected_agents = []

    if conditions["security_alerts"] > 0:
        print(f"\n  → Security alerts detected → Adding Security Auditor")
        selected_agents.append(get_template("security_auditor"))

    if conditions["test_coverage"] < 80.0:
        print(f"  → Low coverage ({conditions['test_coverage']}%) → Adding Coverage Analyzer")
        selected_agents.append(get_template("test_coverage_analyzer"))

    if conditions["code_quality_issues"] > 10:
        print(f"  → Quality issues ({conditions['code_quality_issues']}) → Adding Code Reviewer")
        selected_agents.append(get_template("code_reviewer"))

    if conditions["performance_issues"] > 5:
        print(
            f"  → Performance issues ({conditions['performance_issues']}) → Adding Performance Optimizer"
        )
        selected_agents.append(get_template("performance_optimizer"))

    # Execute with selected agents
    print(f"\n  Selected {len(selected_agents)} agents dynamically")

    strategy = ParallelStrategy()
    result = await strategy.execute(selected_agents, {"conditions": conditions})

    print(f"\n✅ Execution Complete!")
    print(f"  Agents: {len(result.outputs)}")
    print(f"  Duration: {result.total_duration:.2f}s")
    print(f"  Success: {result.success}")


# =============================================================================
# Main Runner
# =============================================================================


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Advanced Composition Patterns")
    print("=" * 60)

    example1_custom_agent_template()
    await example2_strategy_comparison()
    await example3_hybrid_strategy_workflow()
    await example4_cost_optimized_workflow()
    await example5_configuration_store()
    await example6_performance_monitoring()
    await example7_dynamic_agent_selection()

    print("\n" + "=" * 60)
    print("All Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
