"""
Base Workflow Class for Multi-Model Pipelines

Provides a framework for creating cost-optimized workflows that
route tasks to the appropriate model tier.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from empathy_os.cost_tracker import MODEL_PRICING, CostTracker

if TYPE_CHECKING:
    from .config import WorkflowConfig

# Default path for workflow run history
WORKFLOW_HISTORY_FILE = ".empathy/workflow_runs.json"


class ModelTier(Enum):
    """Model tier for cost optimization."""

    CHEAP = "cheap"  # Haiku/GPT-4o-mini - $0.25-1.25/M tokens
    CAPABLE = "capable"  # Sonnet/GPT-4o - $3-15/M tokens
    PREMIUM = "premium"  # Opus/o1 - $15-75/M tokens


class ModelProvider(Enum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    HYBRID = "hybrid"  # Mix of best models from different providers
    CUSTOM = "custom"  # User-defined custom models


# Model mappings by provider and tier
PROVIDER_MODELS: dict[ModelProvider, dict[ModelTier, str]] = {
    ModelProvider.ANTHROPIC: {
        ModelTier.CHEAP: "claude-3-5-haiku-20241022",
        ModelTier.CAPABLE: "claude-sonnet-4-20250514",
        ModelTier.PREMIUM: "claude-opus-4-5-20251101",  # Opus 4.5
    },
    ModelProvider.OPENAI: {
        ModelTier.CHEAP: "gpt-4o-mini",
        ModelTier.CAPABLE: "gpt-4o",
        ModelTier.PREMIUM: "gpt-5.2",  # Latest GPT-5.2
    },
    ModelProvider.OLLAMA: {
        ModelTier.CHEAP: "llama3.2:3b",
        ModelTier.CAPABLE: "llama3.2:latest",
        ModelTier.PREMIUM: "llama3.2:latest",  # Ollama doesn't have premium tier
    },
    # Hybrid: Mix best models from different providers for optimal cost/quality
    ModelProvider.HYBRID: {
        ModelTier.CHEAP: "gpt-4o-mini",  # OpenAI - cheapest per token
        ModelTier.CAPABLE: "claude-sonnet-4-20250514",  # Anthropic - best code/reasoning
        ModelTier.PREMIUM: "claude-opus-4-5-20251101",  # Anthropic - best overall
    },
}


@dataclass
class WorkflowStage:
    """Represents a single stage in a workflow."""

    name: str
    tier: ModelTier
    description: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost: float = 0.0
    result: Any = None
    duration_ms: int = 0
    skipped: bool = False
    skip_reason: str | None = None


@dataclass
class CostReport:
    """Cost breakdown for a workflow execution."""

    total_cost: float
    baseline_cost: float  # If all stages used premium
    savings: float
    savings_percent: float
    by_stage: dict[str, float] = field(default_factory=dict)
    by_tier: dict[str, float] = field(default_factory=dict)


@dataclass
class WorkflowResult:
    """Result of a workflow execution."""

    success: bool
    stages: list[WorkflowStage]
    final_output: Any
    cost_report: CostReport
    started_at: datetime
    completed_at: datetime
    total_duration_ms: int
    error: str | None = None


def _load_workflow_history(history_file: str = WORKFLOW_HISTORY_FILE) -> list[dict]:
    """Load workflow run history from disk."""
    path = Path(history_file)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return []


def _save_workflow_run(
    workflow_name: str,
    provider: str,
    result: WorkflowResult,
    history_file: str = WORKFLOW_HISTORY_FILE,
    max_history: int = 100,
) -> None:
    """Save a workflow run to history."""
    path = Path(history_file)
    path.parent.mkdir(parents=True, exist_ok=True)

    history = _load_workflow_history(history_file)

    # Create run record
    run = {
        "workflow": workflow_name,
        "provider": provider,
        "success": result.success,
        "started_at": result.started_at.isoformat(),
        "completed_at": result.completed_at.isoformat(),
        "duration_ms": result.total_duration_ms,
        "cost": result.cost_report.total_cost,
        "baseline_cost": result.cost_report.baseline_cost,
        "savings": result.cost_report.savings,
        "savings_percent": result.cost_report.savings_percent,
        "stages": [
            {
                "name": s.name,
                "tier": s.tier.value,
                "skipped": s.skipped,
                "cost": s.cost,
                "duration_ms": s.duration_ms,
            }
            for s in result.stages
        ],
        "error": result.error,
    }

    # Add to history and trim
    history.append(run)
    history = history[-max_history:]

    with open(path, "w") as f:
        json.dump(history, f, indent=2)


def get_workflow_stats(history_file: str = WORKFLOW_HISTORY_FILE) -> dict:
    """
    Get workflow statistics for dashboard.

    Returns:
        Dictionary with workflow stats including:
        - total_runs: Total workflow runs
        - by_workflow: Per-workflow stats
        - by_provider: Per-provider stats
        - recent_runs: Last 10 runs
        - total_savings: Total cost savings
    """
    history = _load_workflow_history(history_file)

    if not history:
        return {
            "total_runs": 0,
            "by_workflow": {},
            "by_provider": {},
            "by_tier": {"cheap": 0, "capable": 0, "premium": 0},
            "recent_runs": [],
            "total_cost": 0.0,
            "total_savings": 0.0,
            "avg_savings_percent": 0.0,
        }

    # Aggregate stats
    by_workflow: dict[str, dict] = {}
    by_provider: dict[str, dict] = {}
    by_tier: dict[str, float] = {"cheap": 0.0, "capable": 0.0, "premium": 0.0}
    total_cost = 0.0
    total_savings = 0.0
    successful_runs = 0

    for run in history:
        wf_name = run.get("workflow", "unknown")
        provider = run.get("provider", "unknown")
        cost = run.get("cost", 0.0)
        savings = run.get("savings", 0.0)

        # By workflow
        if wf_name not in by_workflow:
            by_workflow[wf_name] = {"runs": 0, "cost": 0.0, "savings": 0.0, "success": 0}
        by_workflow[wf_name]["runs"] += 1
        by_workflow[wf_name]["cost"] += cost
        by_workflow[wf_name]["savings"] += savings
        if run.get("success"):
            by_workflow[wf_name]["success"] += 1

        # By provider
        if provider not in by_provider:
            by_provider[provider] = {"runs": 0, "cost": 0.0}
        by_provider[provider]["runs"] += 1
        by_provider[provider]["cost"] += cost

        # By tier (from stages)
        for stage in run.get("stages", []):
            if not stage.get("skipped"):
                tier = stage.get("tier", "capable")
                by_tier[tier] = by_tier.get(tier, 0.0) + stage.get("cost", 0.0)

        total_cost += cost
        total_savings += savings
        if run.get("success"):
            successful_runs += 1

    # Calculate average savings percent
    avg_savings_percent = 0.0
    if history:
        savings_percents = [r.get("savings_percent", 0) for r in history if r.get("success")]
        if savings_percents:
            avg_savings_percent = sum(savings_percents) / len(savings_percents)

    return {
        "total_runs": len(history),
        "successful_runs": successful_runs,
        "by_workflow": by_workflow,
        "by_provider": by_provider,
        "by_tier": by_tier,
        "recent_runs": history[-10:][::-1],  # Last 10, most recent first
        "total_cost": total_cost,
        "total_savings": total_savings,
        "avg_savings_percent": avg_savings_percent,
    }


class BaseWorkflow(ABC):
    """
    Base class for multi-model workflows.

    Subclasses define stages and tier mappings:

        class MyWorkflow(BaseWorkflow):
            name = "my-workflow"
            description = "Does something useful"
            stages = ["stage1", "stage2", "stage3"]
            tier_map = {
                "stage1": ModelTier.CHEAP,
                "stage2": ModelTier.CAPABLE,
                "stage3": ModelTier.PREMIUM,
            }

            async def run_stage(self, stage_name, tier, input_data):
                # Implement stage logic
                return output_data
    """

    name: str = "base-workflow"
    description: str = "Base workflow template"
    stages: list[str] = []
    tier_map: dict[str, ModelTier] = {}

    def __init__(
        self,
        cost_tracker: CostTracker | None = None,
        provider: ModelProvider | str | None = None,
        config: WorkflowConfig | None = None,
    ):
        """
        Initialize workflow with optional cost tracker, provider, and config.

        Args:
            cost_tracker: CostTracker instance for logging costs
            provider: Model provider (anthropic, openai, ollama) or ModelProvider enum.
                     If None, uses config or defaults to anthropic.
            config: WorkflowConfig for model customization. If None, loads from
                   .empathy/workflows.yaml or uses defaults.
        """
        from .config import WorkflowConfig

        self.cost_tracker = cost_tracker or CostTracker()
        self._stages_run: list[WorkflowStage] = []

        # Load config if not provided
        self._config = config or WorkflowConfig.load()

        # Determine provider (priority: arg > config > default)
        if provider is None:
            provider = self._config.get_provider_for_workflow(self.name)

        # Handle string provider input
        if isinstance(provider, str):
            provider_str = provider.lower()
            try:
                provider = ModelProvider(provider_str)
                self._provider_str = provider_str
            except ValueError:
                # Custom provider, keep as string
                self._provider_str = provider_str
                provider = ModelProvider.CUSTOM
        else:
            self._provider_str = provider.value

        self.provider = provider

    def get_tier_for_stage(self, stage_name: str) -> ModelTier:
        """Get the model tier for a stage."""
        return self.tier_map.get(stage_name, ModelTier.CAPABLE)

    def get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the model for a tier based on configured provider and config."""
        from .config import get_model

        provider_str = getattr(self, "_provider_str", self.provider.value)

        # Use config-aware model lookup
        model = get_model(provider_str, tier.value, self._config)
        return model

    def _calculate_cost(self, tier: ModelTier, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost for a stage."""
        tier_name = tier.value
        pricing = MODEL_PRICING.get(tier_name, MODEL_PRICING["capable"])
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def _calculate_baseline_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate what the cost would be using premium tier."""
        pricing = MODEL_PRICING["premium"]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def _generate_cost_report(self) -> CostReport:
        """Generate cost report from completed stages."""
        total_cost = 0.0
        baseline_cost = 0.0
        by_stage: dict[str, float] = {}
        by_tier: dict[str, float] = {}

        for stage in self._stages_run:
            if stage.skipped:
                continue

            total_cost += stage.cost
            by_stage[stage.name] = stage.cost

            tier_name = stage.tier.value
            by_tier[tier_name] = by_tier.get(tier_name, 0.0) + stage.cost

            # Calculate what this would cost at premium tier
            baseline_cost += self._calculate_baseline_cost(stage.input_tokens, stage.output_tokens)

        savings = baseline_cost - total_cost
        savings_percent = (savings / baseline_cost * 100) if baseline_cost > 0 else 0.0

        return CostReport(
            total_cost=total_cost,
            baseline_cost=baseline_cost,
            savings=savings,
            savings_percent=savings_percent,
            by_stage=by_stage,
            by_tier=by_tier,
        )

    @abstractmethod
    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """
        Execute a single workflow stage.

        Args:
            stage_name: Name of the stage to run
            tier: Model tier to use
            input_data: Input for this stage

        Returns:
            Tuple of (output_data, input_tokens, output_tokens)
        """
        pass

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Determine if a stage should be skipped.

        Override in subclasses for conditional stage execution.

        Args:
            stage_name: Name of the stage
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        return False, None

    async def execute(self, **kwargs: Any) -> WorkflowResult:
        """
        Execute the full workflow.

        Args:
            **kwargs: Initial input data for the workflow

        Returns:
            WorkflowResult with stages, output, and cost report
        """
        started_at = datetime.now()
        self._stages_run = []
        current_data = kwargs
        error = None

        try:
            for stage_name in self.stages:
                tier = self.get_tier_for_stage(stage_name)
                stage_start = datetime.now()

                # Check if stage should be skipped
                should_skip, skip_reason = self.should_skip_stage(stage_name, current_data)

                if should_skip:
                    stage = WorkflowStage(
                        name=stage_name,
                        tier=tier,
                        description=f"Stage: {stage_name}",
                        skipped=True,
                        skip_reason=skip_reason,
                    )
                    self._stages_run.append(stage)
                    continue

                # Run the stage
                output, input_tokens, output_tokens = await self.run_stage(
                    stage_name, tier, current_data
                )

                stage_end = datetime.now()
                duration_ms = int((stage_end - stage_start).total_seconds() * 1000)
                cost = self._calculate_cost(tier, input_tokens, output_tokens)

                stage = WorkflowStage(
                    name=stage_name,
                    tier=tier,
                    description=f"Stage: {stage_name}",
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cost=cost,
                    result=output,
                    duration_ms=duration_ms,
                )
                self._stages_run.append(stage)

                # Log to cost tracker
                self.cost_tracker.log_request(
                    model=self.get_model_for_tier(tier),
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    task_type=f"workflow:{self.name}:{stage_name}",
                )

                # Pass output to next stage
                current_data = output if isinstance(output, dict) else {"result": output}

        except Exception as e:
            error = str(e)

        completed_at = datetime.now()
        total_duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Get final output from last non-skipped stage
        final_output = None
        for stage in reversed(self._stages_run):
            if not stage.skipped and stage.result is not None:
                final_output = stage.result
                break

        result = WorkflowResult(
            success=error is None,
            stages=self._stages_run,
            final_output=final_output,
            cost_report=self._generate_cost_report(),
            started_at=started_at,
            completed_at=completed_at,
            total_duration_ms=total_duration_ms,
            error=error,
        )

        # Save to workflow history for dashboard
        try:
            provider_str = getattr(self, "_provider_str", "unknown")
            _save_workflow_run(self.name, provider_str, result)
        except Exception:
            pass  # Don't fail workflow if history save fails

        return result

    def describe(self) -> str:
        """Get a human-readable description of the workflow."""
        lines = [
            f"Workflow: {self.name}",
            f"Description: {self.description}",
            "",
            "Stages:",
        ]

        for stage_name in self.stages:
            tier = self.get_tier_for_stage(stage_name)
            model = self.get_model_for_tier(tier)
            lines.append(f"  {stage_name}: {tier.value} ({model})")

        return "\n".join(lines)
