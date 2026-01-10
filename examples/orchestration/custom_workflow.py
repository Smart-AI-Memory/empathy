"""Custom Workflow Examples

This file shows how to build custom meta-orchestrated workflows from scratch.

Learn how to:
- Create custom workflows using meta-orchestration
- Integrate with configuration store for learning
- Define custom quality gates
- Build multi-stage workflows

Run:
    python custom_workflow.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from empathy_os.orchestration.meta_orchestrator import MetaOrchestrator
from empathy_os.orchestration.execution_strategies import (
    get_strategy,
    StrategyResult,
)
from empathy_os.orchestration.config_store import (
    AgentConfiguration,
    ConfigurationStore,
)
from empathy_os.orchestration.agent_templates import get_template


# =============================================================================
# Example 1: Simple Custom Workflow
# =============================================================================


@dataclass
class SimpleWorkflowResult:
    """Result from simple workflow."""

    success: bool
    quality_score: float
    duration: float
    outputs: dict[str, Any] = field(default_factory=dict)


class SimpleCustomWorkflow:
    """Simple custom workflow using meta-orchestration.

    This workflow demonstrates the basic pattern:
    1. Analyze task
    2. Execute agents
    3. Evaluate results
    4. Return structured output
    """

    def __init__(self, task_description: str):
        """Initialize workflow.

        Args:
            task_description: Task for meta-orchestrator to analyze
        """
        self.task_description = task_description
        self.orchestrator = MetaOrchestrator()

    async def execute(self, context: dict[str, Any]) -> SimpleWorkflowResult:
        """Execute workflow.

        Args:
            context: Execution context

        Returns:
            SimpleWorkflowResult with outcomes
        """
        print(f"\n🚀 Executing: {self.task_description}")

        # Step 1: Analyze task and create plan
        plan = self.orchestrator.analyze_and_compose(
            task=self.task_description,
            context=context,
        )

        print(f"  Strategy: {plan.strategy.value}")
        print(f"  Agents: {[a.id for a in plan.agents]}")

        # Step 2: Execute plan
        start_time = asyncio.get_event_loop().time()

        strategy = get_strategy(plan.strategy.value)
        result = await strategy.execute(plan.agents, context)

        duration = asyncio.get_event_loop().time() - start_time

        # Step 3: Calculate quality score
        quality_score = self._calculate_quality(result)

        # Step 4: Return results
        return SimpleWorkflowResult(
            success=result.success,
            quality_score=quality_score,
            duration=duration,
            outputs={r.agent_id: r.output for r in result.outputs},
        )

    def _calculate_quality(self, result: StrategyResult) -> float:
        """Calculate quality score from strategy result.

        Args:
            result: Strategy execution result

        Returns:
            Quality score (0-100)
        """
        # Simple scoring: average agent confidence * 100
        if not result.outputs:
            return 0.0

        avg_confidence = sum(r.confidence for r in result.outputs) / len(result.outputs)
        return avg_confidence * 100


async def example1_simple_workflow():
    """Demonstrate simple custom workflow."""
    print("\n" + "=" * 60)
    print("Example 1: Simple Custom Workflow")
    print("=" * 60)

    workflow = SimpleCustomWorkflow(
        task_description="Analyze code quality and suggest improvements"
    )

    result = await workflow.execute(
        context={
            "project_root": "./src",
            "focus_areas": ["maintainability", "performance"],
        }
    )

    print(f"\n✅ Workflow Complete!")
    print(f"  Success: {result.success}")
    print(f"  Quality Score: {result.quality_score:.1f}/100")
    print(f"  Duration: {result.duration:.2f}s")
    print(f"  Agents Used: {len(result.outputs)}")


# =============================================================================
# Example 2: Workflow with Configuration Store
# =============================================================================


class LearningWorkflow:
    """Workflow that learns from outcomes using configuration store.

    This workflow:
    1. Checks for proven compositions in store
    2. Reuses if found (faster, more reliable)
    3. Falls back to meta-orchestrator if needed
    4. Records outcomes for future learning
    """

    def __init__(self, task_pattern: str):
        """Initialize learning workflow.

        Args:
            task_pattern: Pattern identifier for configuration store
        """
        self.task_pattern = task_pattern
        self.orchestrator = MetaOrchestrator()
        self.config_store = ConfigurationStore()

    async def execute(self, context: dict[str, Any]) -> SimpleWorkflowResult:
        """Execute workflow with learning.

        Args:
            context: Execution context

        Returns:
            SimpleWorkflowResult
        """
        print(f"\n🧠 Learning Workflow: {self.task_pattern}")

        # Step 1: Check for proven composition
        best = self.config_store.get_best_for_task(self.task_pattern)

        if best and best.success_rate >= 0.8:
            print(f"  ♻️  Reusing proven composition (success rate: {best.success_rate:.1%})")

            # Reconstruct agents from saved config
            agents = []
            for agent_config in best.agents:
                template = get_template(agent_config["role"])
                if template:
                    agents.append(template)

            strategy = get_strategy(best.strategy)

        else:
            print(f"  🆕 Creating new composition")

            # Create new composition
            plan = self.orchestrator.analyze_and_compose(
                task=f"Execute {self.task_pattern}",
                context=context,
            )

            agents = plan.agents
            strategy = get_strategy(plan.strategy.value)

            # Save as new configuration
            best = AgentConfiguration(
                id=f"comp_{self.task_pattern}_{self._generate_id()}",
                task_pattern=self.task_pattern,
                agents=[{"role": a.id, "tier": a.tier_preference} for a in agents],
                strategy=strategy.__class__.__name__.replace("Strategy", "").lower(),
                quality_gates={},
            )

        # Step 2: Execute
        start_time = asyncio.get_event_loop().time()
        result = await strategy.execute(agents, context)
        duration = asyncio.get_event_loop().time() - start_time

        # Step 3: Calculate quality and record outcome
        quality_score = sum(r.confidence for r in result.outputs) / len(result.outputs) * 100

        best.record_outcome(result.success, quality_score)
        self.config_store.save(best)

        print(f"  📊 Recorded outcome: {quality_score:.1f}/100")

        return SimpleWorkflowResult(
            success=result.success,
            quality_score=quality_score,
            duration=duration,
            outputs={r.agent_id: r.output for r in result.outputs},
        )

    def _generate_id(self) -> str:
        """Generate unique ID."""
        return str(uuid.uuid4())[:8]


async def example2_learning_workflow():
    """Demonstrate workflow with configuration store."""
    print("\n" + "=" * 60)
    print("Example 2: Learning Workflow")
    print("=" * 60)

    workflow = LearningWorkflow(task_pattern="code_quality_analysis")

    # First execution: creates new composition
    print("\n📝 First Execution (new composition):")
    result1 = await workflow.execute({"project_root": "."})

    # Second execution: reuses if successful
    print("\n📝 Second Execution (reuse if successful):")
    result2 = await workflow.execute({"project_root": "."})

    print(f"\n✅ Both executions complete!")
    print(f"  First:  {result1.quality_score:.1f}/100 in {result1.duration:.2f}s")
    print(f"  Second: {result2.quality_score:.1f}/100 in {result2.duration:.2f}s")


# =============================================================================
# Example 3: Multi-Stage Workflow
# =============================================================================


class MultiStageWorkflow:
    """Workflow with multiple orchestration stages.

    Demonstrates:
    - Different strategies per stage
    - Context passing between stages
    - Progressive refinement
    """

    def __init__(self):
        self.orchestrator = MetaOrchestrator()

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute multi-stage workflow.

        Args:
            context: Initial context

        Returns:
            Results from all stages
        """
        print("\n🎭 Multi-Stage Workflow")

        results = {}

        # Stage 1: Parallel Analysis
        print("\n  Stage 1: Parallel Analysis")
        stage1_plan = self.orchestrator.analyze_and_compose(
            task="Analyze codebase for issues",
            context=context,
        )
        stage1_strategy = get_strategy("parallel")
        stage1_result = await stage1_strategy.execute(stage1_plan.agents, context)
        results["analysis"] = stage1_result.aggregated_output

        # Stage 2: Sequential Fixes
        print("\n  Stage 2: Sequential Fixes")
        stage2_context = {
            **context,
            "analysis_findings": stage1_result.aggregated_output,
        }
        stage2_plan = self.orchestrator.analyze_and_compose(
            task="Fix identified issues",
            context=stage2_context,
        )
        stage2_strategy = get_strategy("sequential")
        stage2_result = await stage2_strategy.execute(stage2_plan.agents, stage2_context)
        results["fixes"] = stage2_result.aggregated_output

        # Stage 3: Parallel Validation
        print("\n  Stage 3: Parallel Validation")
        stage3_context = {
            **stage2_context,
            "applied_fixes": stage2_result.aggregated_output,
        }
        stage3_plan = self.orchestrator.analyze_and_compose(
            task="Validate all fixes",
            context=stage3_context,
        )
        stage3_strategy = get_strategy("parallel")
        stage3_result = await stage3_strategy.execute(stage3_plan.agents, stage3_context)
        results["validation"] = stage3_result.aggregated_output

        return results


async def example3_multistage_workflow():
    """Demonstrate multi-stage workflow."""
    print("\n" + "=" * 60)
    print("Example 3: Multi-Stage Workflow")
    print("=" * 60)

    workflow = MultiStageWorkflow()

    results = await workflow.execute(context={"project_root": ".", "strict_mode": True})

    print(f"\n✅ All stages complete!")
    print(f"  Stages executed: {len(results)}")
    for stage_name in results.keys():
        print(f"    • {stage_name}")


# =============================================================================
# Example 4: Workflow with Custom Quality Gates
# =============================================================================


@dataclass
class QualityGate:
    """Custom quality gate definition."""

    name: str
    threshold: float
    actual: float = 0.0

    @property
    def passed(self) -> bool:
        return self.actual >= self.threshold


class QualityGatedWorkflow:
    """Workflow with enforced quality gates.

    Demonstrates:
    - Custom quality gate definition
    - Quality evaluation
    - Conditional execution
    """

    def __init__(self, quality_gates: list[QualityGate]):
        """Initialize workflow with quality gates.

        Args:
            quality_gates: List of quality gates to enforce
        """
        self.quality_gates = quality_gates
        self.orchestrator = MetaOrchestrator()

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute workflow with quality gates.

        Args:
            context: Execution context

        Returns:
            Results with quality gate outcomes
        """
        print("\n🚪 Quality-Gated Workflow")

        # Execute main workflow
        plan = self.orchestrator.analyze_and_compose(
            task="Improve code quality",
            context=context,
        )

        strategy = get_strategy(plan.strategy.value)
        result = await strategy.execute(plan.agents, context)

        # Evaluate quality gates
        self._evaluate_gates(result)

        # Check if all gates passed
        passed_gates = sum(1 for g in self.quality_gates if g.passed)
        all_passed = passed_gates == len(self.quality_gates)

        print(f"\n  Quality Gates: {passed_gates}/{len(self.quality_gates)} passed")
        for gate in self.quality_gates:
            status = "✅" if gate.passed else "❌"
            print(f"    {status} {gate.name}: {gate.actual:.1f} >= {gate.threshold:.1f}")

        return {
            "success": result.success and all_passed,
            "gates_passed": all_passed,
            "quality_gates": self.quality_gates,
            "outputs": result.aggregated_output,
        }

    def _evaluate_gates(self, result: StrategyResult) -> None:
        """Evaluate quality gates from result.

        Args:
            result: Strategy execution result
        """
        # Simple evaluation: average confidence as quality metric
        avg_confidence = sum(r.confidence for r in result.outputs) / len(result.outputs) * 100

        for gate in self.quality_gates:
            if gate.name == "overall_quality":
                gate.actual = avg_confidence
            elif gate.name == "agent_success_rate":
                success_rate = (
                    sum(1 for r in result.outputs if r.success) / len(result.outputs) * 100
                )
                gate.actual = success_rate


async def example4_quality_gated_workflow():
    """Demonstrate quality-gated workflow."""
    print("\n" + "=" * 60)
    print("Example 4: Quality-Gated Workflow")
    print("=" * 60)

    # Define quality gates
    gates = [
        QualityGate(name="overall_quality", threshold=80.0),
        QualityGate(name="agent_success_rate", threshold=100.0),
    ]

    workflow = QualityGatedWorkflow(quality_gates=gates)

    result = await workflow.execute({"project_root": "."})

    if result["gates_passed"]:
        print(f"\n✅ All quality gates PASSED")
    else:
        print(f"\n❌ Some quality gates FAILED")


# =============================================================================
# Example 5: Conditional Workflow
# =============================================================================


class ConditionalWorkflow:
    """Workflow with conditional logic based on intermediate results.

    Demonstrates:
    - Decision-making between stages
    - Adaptive execution paths
    - Context-aware routing
    """

    def __init__(self):
        self.orchestrator = MetaOrchestrator()

    async def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Execute workflow with conditional logic.

        Args:
            context: Execution context

        Returns:
            Results with execution path taken
        """
        print("\n🔀 Conditional Workflow")

        # Stage 1: Assessment
        print("\n  Stage 1: Assessing complexity")

        assessment_plan = self.orchestrator.analyze_and_compose(
            task="Assess code complexity",
            context=context,
        )

        strategy = get_strategy("sequential")
        assessment = await strategy.execute(assessment_plan.agents, context)

        # Calculate complexity score (simulated)
        complexity_score = sum(r.confidence for r in assessment.outputs) / len(assessment.outputs)

        print(f"    Complexity Score: {complexity_score:.2f}")

        # Stage 2: Conditional execution
        if complexity_score > 0.7:
            # High complexity → Use premium agents
            print(f"\n  Stage 2: High complexity → Premium agents")

            plan = self.orchestrator.analyze_and_compose(
                task="Complex refactoring required",
                context={**context, "complexity": "high"},
            )

            execution_path = "premium"

        else:
            # Low complexity → Use cheap agents
            print(f"\n  Stage 2: Low complexity → Cheap agents")

            plan = self.orchestrator.analyze_and_compose(
                task="Simple cleanup required",
                context={**context, "complexity": "low"},
            )

            execution_path = "cheap"

        strategy = get_strategy(plan.strategy.value)
        result = await strategy.execute(plan.agents, context)

        return {
            "execution_path": execution_path,
            "complexity_score": complexity_score,
            "result": result.aggregated_output,
        }


async def example5_conditional_workflow():
    """Demonstrate conditional workflow."""
    print("\n" + "=" * 60)
    print("Example 5: Conditional Workflow")
    print("=" * 60)

    workflow = ConditionalWorkflow()

    result = await workflow.execute({"project_root": "."})

    print(f"\n✅ Workflow complete!")
    print(f"  Execution Path: {result['execution_path']}")
    print(f"  Complexity Score: {result['complexity_score']:.2f}")


# =============================================================================
# Main Runner
# =============================================================================


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Custom Workflow Examples")
    print("=" * 60)

    await example1_simple_workflow()
    await example2_learning_workflow()
    await example3_multistage_workflow()
    await example4_quality_gated_workflow()
    await example5_conditional_workflow()

    print("\n" + "=" * 60)
    print("All Examples Complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
