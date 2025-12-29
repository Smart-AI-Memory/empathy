"""
Base Workflow Class for Multi-Model Pipelines

Provides a framework for creating cost-optimized workflows that
route tasks to the appropriate model tier.

Integration with empathy_os.models:
- Uses unified ModelTier/ModelProvider from empathy_os.models
- Supports LLMExecutor for abstracted LLM calls
- Supports TelemetryBackend for telemetry storage
- WorkflowStepConfig for declarative step definitions

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

# Load .env file for API keys if python-dotenv is available
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, rely on environment variables

from empathy_os.cost_tracker import MODEL_PRICING, CostTracker

# Import unified types from empathy_os.models
from empathy_os.models import (
    ExecutionContext,
    LLMCallRecord,
    LLMExecutor,
    TelemetryBackend,
    WorkflowRunRecord,
    WorkflowStageRecord,
    get_telemetry_store,
)
from empathy_os.models import ModelProvider as UnifiedModelProvider
from empathy_os.models import ModelTier as UnifiedModelTier

# Import progress tracking
from .progress import ProgressCallback, ProgressTracker

if TYPE_CHECKING:
    from .config import WorkflowConfig
    from .step_config import WorkflowStepConfig

# Default path for workflow run history
WORKFLOW_HISTORY_FILE = ".empathy/workflow_runs.json"


# Local enums for backward compatibility
# New code should use empathy_os.models.ModelTier/ModelProvider
class ModelTier(Enum):
    """Model tier for cost optimization."""

    CHEAP = "cheap"  # Haiku/GPT-4o-mini - $0.25-1.25/M tokens
    CAPABLE = "capable"  # Sonnet/GPT-4o - $3-15/M tokens
    PREMIUM = "premium"  # Opus/o1 - $15-75/M tokens

    def to_unified(self) -> UnifiedModelTier:
        """Convert to unified ModelTier from empathy_os.models."""
        return UnifiedModelTier(self.value)


class ModelProvider(Enum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"  # Google Gemini models
    OLLAMA = "ollama"
    HYBRID = "hybrid"  # Mix of best models from different providers
    CUSTOM = "custom"  # User-defined custom models

    def to_unified(self) -> UnifiedModelProvider:
        """Convert to unified ModelProvider from empathy_os.models."""
        return UnifiedModelProvider(self.value)


# Import unified MODEL_REGISTRY as single source of truth
# This import is placed here intentionally to avoid circular imports
from empathy_os.models import MODEL_REGISTRY  # noqa: E402


def _build_provider_models() -> dict[ModelProvider, dict[ModelTier, str]]:
    """
    Build PROVIDER_MODELS from MODEL_REGISTRY.

    This ensures PROVIDER_MODELS stays in sync with the single source of truth.
    """
    result: dict[ModelProvider, dict[ModelTier, str]] = {}

    # Map string provider names to ModelProvider enum
    provider_map = {
        "anthropic": ModelProvider.ANTHROPIC,
        "openai": ModelProvider.OPENAI,
        "google": ModelProvider.GOOGLE,
        "ollama": ModelProvider.OLLAMA,
        "hybrid": ModelProvider.HYBRID,
    }

    # Map string tier names to ModelTier enum
    tier_map = {
        "cheap": ModelTier.CHEAP,
        "capable": ModelTier.CAPABLE,
        "premium": ModelTier.PREMIUM,
    }

    for provider_str, tiers in MODEL_REGISTRY.items():
        if provider_str not in provider_map:
            continue  # Skip custom providers
        provider_enum = provider_map[provider_str]
        result[provider_enum] = {}
        for tier_str, model_info in tiers.items():
            if tier_str in tier_map:
                result[provider_enum][tier_map[tier_str]] = model_info.id

    return result


# Model mappings by provider and tier (derived from MODEL_REGISTRY)
PROVIDER_MODELS: dict[ModelProvider, dict[ModelTier, str]] = _build_provider_models()


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
    provider: str = "unknown"
    error: str | None = None
    # Structured error taxonomy for reliability
    error_type: str | None = None  # "config" | "runtime" | "provider" | "timeout" | "validation"
    transient: bool = False  # True if retry is reasonable (e.g., provider timeout)


def _load_workflow_history(history_file: str = WORKFLOW_HISTORY_FILE) -> list[dict]:
    """Load workflow run history from disk."""
    path = Path(history_file)
    if not path.exists():
        return []
    try:
        with open(path) as f:
            data = json.load(f)
            return list(data) if isinstance(data, list) else []
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
    run: dict = {
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

    # Extract XML-parsed fields from final_output if present
    if isinstance(result.final_output, dict):
        if result.final_output.get("xml_parsed"):
            run["xml_parsed"] = True
            run["summary"] = result.final_output.get("summary")
            run["findings"] = result.final_output.get("findings", [])
            run["checklist"] = result.final_output.get("checklist", [])

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
        executor: LLMExecutor | None = None,
        telemetry_backend: TelemetryBackend | None = None,
        progress_callback: ProgressCallback | None = None,
    ):
        """
        Initialize workflow with optional cost tracker, provider, and config.

        Args:
            cost_tracker: CostTracker instance for logging costs
            provider: Model provider (anthropic, openai, ollama) or ModelProvider enum.
                     If None, uses config or defaults to anthropic.
            config: WorkflowConfig for model customization. If None, loads from
                   .empathy/workflows.yaml or uses defaults.
            executor: LLMExecutor for abstracted LLM calls (optional).
                     If provided, enables unified execution with telemetry.
            telemetry_backend: TelemetryBackend for storing telemetry records.
                     Defaults to TelemetryStore (JSONL file backend).
            progress_callback: Callback for real-time progress updates.
                     If provided, enables live progress tracking during execution.
        """
        from .config import WorkflowConfig

        self.cost_tracker = cost_tracker or CostTracker()
        self._stages_run: list[WorkflowStage] = []

        # Progress tracking
        self._progress_callback = progress_callback
        self._progress_tracker: ProgressTracker | None = None

        # New: LLMExecutor support
        self._executor = executor
        self._telemetry_backend = telemetry_backend or get_telemetry_store()
        self._run_id: str | None = None  # Set at start of execute()
        self._api_key: str | None = None  # For default executor creation

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

    async def _call_llm(
        self, tier: ModelTier, system: str, user_message: str, max_tokens: int = 4096
    ) -> tuple[str, int, int]:
        """
        Provider-agnostic LLM call using the configured provider.

        This method uses run_step_with_executor internally to make LLM calls
        that respect the configured provider (anthropic, openai, google, etc.).

        Args:
            tier: Model tier to use (CHEAP, CAPABLE, PREMIUM)
            system: System prompt
            user_message: User message/prompt
            max_tokens: Maximum tokens in response

        Returns:
            Tuple of (response_content, input_tokens, output_tokens)
        """
        from .step_config import WorkflowStepConfig

        # Create a step config for this call
        step = WorkflowStepConfig(
            name=f"llm_call_{tier.value}",
            task_type="general",
            tier_hint=tier.value,
            description="LLM call",
            max_tokens=max_tokens,
        )

        try:
            content, in_tokens, out_tokens, _cost = await self.run_step_with_executor(
                step=step,
                prompt=user_message,
                system=system,
            )
            return content, in_tokens, out_tokens
        except Exception as e:
            return f"Error calling LLM: {e}", 0, 0

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
        # Set run ID for telemetry correlation
        self._run_id = str(uuid.uuid4())

        started_at = datetime.now()
        self._stages_run = []
        current_data = kwargs
        error = None

        # Initialize progress tracker if callback provided
        if self._progress_callback:
            self._progress_tracker = ProgressTracker(
                workflow_name=self.name,
                workflow_id=self._run_id,
                stage_names=self.stages,
            )
            self._progress_tracker.add_callback(self._progress_callback)
            self._progress_tracker.start_workflow()

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

                    # Report skip to progress tracker
                    if self._progress_tracker:
                        self._progress_tracker.skip_stage(stage_name, skip_reason or "")

                    continue

                # Report stage start to progress tracker
                model_id = self.get_model_for_tier(tier)
                if self._progress_tracker:
                    self._progress_tracker.start_stage(stage_name, tier.value, model_id)

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

                # Report stage completion to progress tracker
                if self._progress_tracker:
                    self._progress_tracker.complete_stage(
                        stage_name,
                        cost=cost,
                        tokens_in=input_tokens,
                        tokens_out=output_tokens,
                    )

                # Log to cost tracker
                self.cost_tracker.log_request(
                    model=model_id,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    task_type=f"workflow:{self.name}:{stage_name}",
                )

                # Pass output to next stage
                current_data = output if isinstance(output, dict) else {"result": output}

        except Exception as e:
            error = str(e)
            # Report failure to progress tracker
            if self._progress_tracker:
                self._progress_tracker.fail_workflow(error)

        completed_at = datetime.now()
        total_duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        # Get final output from last non-skipped stage
        final_output = None
        for stage in reversed(self._stages_run):
            if not stage.skipped and stage.result is not None:
                final_output = stage.result
                break

        # Classify error type and transient status
        error_type = None
        transient = False
        if error:
            error_lower = error.lower()
            if "timeout" in error_lower or "timed out" in error_lower:
                error_type = "timeout"
                transient = True
            elif "config" in error_lower or "configuration" in error_lower:
                error_type = "config"
                transient = False
            elif "api" in error_lower or "rate limit" in error_lower or "quota" in error_lower:
                error_type = "provider"
                transient = True
            elif "validation" in error_lower or "invalid" in error_lower:
                error_type = "validation"
                transient = False
            else:
                error_type = "runtime"
                transient = False

        provider_str = getattr(self, "_provider_str", "unknown")
        result = WorkflowResult(
            success=error is None,
            stages=self._stages_run,
            final_output=final_output,
            cost_report=self._generate_cost_report(),
            started_at=started_at,
            completed_at=completed_at,
            total_duration_ms=total_duration_ms,
            provider=provider_str,
            error=error,
            error_type=error_type,
            transient=transient,
        )

        # Report workflow completion to progress tracker
        if self._progress_tracker and error is None:
            self._progress_tracker.complete_workflow()

        # Save to workflow history for dashboard
        try:
            _save_workflow_run(self.name, provider_str, result)
        except Exception:
            pass  # Don't fail workflow if history save fails

        # Emit workflow telemetry to backend
        self._emit_workflow_telemetry(result)

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

    # =========================================================================
    # New infrastructure methods (Phase 4)
    # =========================================================================

    def _create_execution_context(
        self,
        step_name: str,
        task_type: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> ExecutionContext:
        """
        Create an ExecutionContext for a step execution.

        Args:
            step_name: Name of the workflow step
            task_type: Task type for routing
            user_id: Optional user ID
            session_id: Optional session ID

        Returns:
            ExecutionContext populated with workflow info
        """
        return ExecutionContext(
            workflow_name=self.name,
            step_name=step_name,
            user_id=user_id,
            session_id=session_id,
            metadata={
                "task_type": task_type,
                "run_id": self._run_id,
                "provider": self._provider_str,
            },
        )

    def _create_default_executor(self) -> LLMExecutor:
        """
        Create a default EmpathyLLMExecutor wrapped in ResilientExecutor.

        This method is called lazily when run_step_with_executor is used
        without a pre-configured executor. The executor is wrapped with
        resilience features (retry, fallback, circuit breaker).

        Returns:
            LLMExecutor instance (ResilientExecutor wrapping EmpathyLLMExecutor)
        """
        from empathy_os.models.empathy_executor import EmpathyLLMExecutor
        from empathy_os.models.fallback import ResilientExecutor

        # Create the base executor
        base_executor = EmpathyLLMExecutor(
            provider=self._provider_str,
            api_key=self._api_key,
            telemetry_store=self._telemetry_backend,
        )
        # Wrap with resilience layer (retry, fallback, circuit breaker)
        return ResilientExecutor(executor=base_executor)

    def _get_executor(self) -> LLMExecutor:
        """
        Get or create the LLM executor.

        Returns the configured executor or creates a default one.

        Returns:
            LLMExecutor instance
        """
        if self._executor is None:
            self._executor = self._create_default_executor()
        return self._executor

    def _emit_call_telemetry(
        self,
        step_name: str,
        task_type: str,
        tier: str,
        model_id: str,
        input_tokens: int,
        output_tokens: int,
        cost: float,
        latency_ms: int,
        success: bool = True,
        error_message: str | None = None,
        fallback_used: bool = False,
    ) -> None:
        """
        Emit an LLMCallRecord to the telemetry backend.

        Args:
            step_name: Name of the workflow step
            task_type: Task type used for routing
            tier: Model tier used
            model_id: Model ID used
            input_tokens: Input token count
            output_tokens: Output token count
            cost: Estimated cost
            latency_ms: Latency in milliseconds
            success: Whether the call succeeded
            error_message: Error message if failed
            fallback_used: Whether fallback was used
        """
        record = LLMCallRecord(
            call_id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            workflow_name=self.name,
            step_name=step_name,
            task_type=task_type,
            provider=self._provider_str,
            tier=tier,
            model_id=model_id,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            estimated_cost=cost,
            latency_ms=latency_ms,
            success=success,
            error_message=error_message,
            fallback_used=fallback_used,
            metadata={"run_id": self._run_id},
        )
        try:
            self._telemetry_backend.log_call(record)
        except Exception:
            pass  # Don't fail workflow if telemetry fails

    def _emit_workflow_telemetry(self, result: WorkflowResult) -> None:
        """
        Emit a WorkflowRunRecord to the telemetry backend.

        Args:
            result: The workflow result to record
        """
        # Build stage records
        stages = [
            WorkflowStageRecord(
                stage_name=s.name,
                tier=s.tier.value,
                model_id=self.get_model_for_tier(s.tier),
                input_tokens=s.input_tokens,
                output_tokens=s.output_tokens,
                cost=s.cost,
                latency_ms=s.duration_ms,
                success=not s.skipped and result.error is None,
                skipped=s.skipped,
                skip_reason=s.skip_reason,
            )
            for s in result.stages
        ]

        record = WorkflowRunRecord(
            run_id=self._run_id or str(uuid.uuid4()),
            workflow_name=self.name,
            started_at=result.started_at.isoformat(),
            completed_at=result.completed_at.isoformat(),
            stages=stages,
            total_input_tokens=sum(s.input_tokens for s in result.stages if not s.skipped),
            total_output_tokens=sum(s.output_tokens for s in result.stages if not s.skipped),
            total_cost=result.cost_report.total_cost,
            baseline_cost=result.cost_report.baseline_cost,
            savings=result.cost_report.savings,
            savings_percent=result.cost_report.savings_percent,
            total_duration_ms=result.total_duration_ms,
            success=result.success,
            error=result.error,
            providers_used=[self._provider_str],
            tiers_used=list(result.cost_report.by_tier.keys()),
        )
        try:
            self._telemetry_backend.log_workflow(record)
        except Exception:
            pass  # Don't fail workflow if telemetry fails

    async def run_step_with_executor(
        self,
        step: WorkflowStepConfig,
        prompt: str,
        system: str | None = None,
        **kwargs: Any,
    ) -> tuple[str, int, int, float]:
        """
        Run a workflow step using the LLMExecutor.

        This method provides a unified interface for executing steps with
        automatic routing, telemetry, and cost tracking. If no executor
        was provided at construction, a default EmpathyLLMExecutor is created.

        Args:
            step: WorkflowStepConfig defining the step
            prompt: The prompt to send
            system: Optional system prompt
            **kwargs: Additional arguments passed to executor

        Returns:
            Tuple of (content, input_tokens, output_tokens, cost)
        """
        executor = self._get_executor()

        context = self._create_execution_context(
            step_name=step.name,
            task_type=step.task_type,
        )

        start_time = datetime.now()
        response = await executor.run(
            task_type=step.task_type,
            prompt=prompt,
            system=system,
            context=context,
            **kwargs,
        )
        end_time = datetime.now()
        latency_ms = int((end_time - start_time).total_seconds() * 1000)

        # Emit telemetry
        self._emit_call_telemetry(
            step_name=step.name,
            task_type=step.task_type,
            tier=response.tier,
            model_id=response.model_id,
            input_tokens=response.tokens_input,
            output_tokens=response.tokens_output,
            cost=response.cost_estimate,
            latency_ms=latency_ms,
            success=True,
        )

        return (
            response.content,
            response.tokens_input,
            response.tokens_output,
            response.cost_estimate,
        )

    # =========================================================================
    # XML Prompt Integration (Phase 4)
    # =========================================================================

    def _get_xml_config(self) -> dict[str, Any]:
        """
        Get XML prompt configuration for this workflow.

        Returns:
            Dictionary with XML configuration settings.
        """
        if self._config is None:
            return {}
        return self._config.get_xml_config_for_workflow(self.name)

    def _is_xml_enabled(self) -> bool:
        """Check if XML prompts are enabled for this workflow."""
        config = self._get_xml_config()
        return bool(config.get("enabled", False))

    def _render_xml_prompt(
        self,
        role: str,
        goal: str,
        instructions: list[str],
        constraints: list[str],
        input_type: str,
        input_payload: str,
        extra: dict[str, Any] | None = None,
    ) -> str:
        """
        Render a prompt using XML template if enabled.

        Args:
            role: The role for the AI (e.g., "security analyst").
            goal: The primary objective.
            instructions: Step-by-step instructions.
            constraints: Rules and guidelines.
            input_type: Type of input ("code", "diff", "document").
            input_payload: The content to process.
            extra: Additional context data.

        Returns:
            Rendered prompt string (XML if enabled, plain text otherwise).
        """
        from empathy_os.prompts import PromptContext, XmlPromptTemplate, get_template

        config = self._get_xml_config()

        if not config.get("enabled", False):
            # Fall back to plain text
            return self._render_plain_prompt(
                role, goal, instructions, constraints, input_type, input_payload
            )

        # Create context
        context = PromptContext(
            role=role,
            goal=goal,
            instructions=instructions,
            constraints=constraints,
            input_type=input_type,
            input_payload=input_payload,
            extra=extra or {},
        )

        # Get template
        template_name = config.get("template_name", self.name)
        template = get_template(template_name)

        if template is None:
            # Create a basic XML template if no built-in found
            template = XmlPromptTemplate(
                name=self.name,
                schema_version=config.get("schema_version", "1.0"),
            )

        return template.render(context)

    def _render_plain_prompt(
        self,
        role: str,
        goal: str,
        instructions: list[str],
        constraints: list[str],
        input_type: str,
        input_payload: str,
    ) -> str:
        """Render a plain text prompt (fallback when XML is disabled)."""
        parts = [f"You are a {role}.", "", f"Goal: {goal}", ""]

        if instructions:
            parts.append("Instructions:")
            for i, inst in enumerate(instructions, 1):
                parts.append(f"{i}. {inst}")
            parts.append("")

        if constraints:
            parts.append("Guidelines:")
            for constraint in constraints:
                parts.append(f"- {constraint}")
            parts.append("")

        if input_payload:
            parts.append(f"Input ({input_type}):")
            parts.append(input_payload)

        return "\n".join(parts)

    def _parse_xml_response(self, response: str) -> dict[str, Any]:
        """
        Parse an XML response if XML enforcement is enabled.

        Args:
            response: The LLM response text.

        Returns:
            Dictionary with parsed fields or raw response data.
        """
        from empathy_os.prompts import XmlResponseParser

        config = self._get_xml_config()

        if not config.get("enforce_response_xml", False):
            # No parsing needed, return as-is
            return {
                "_parsed_response": None,
                "_raw": response,
            }

        fallback = config.get("fallback_on_parse_error", True)
        parser = XmlResponseParser(fallback_on_error=fallback)
        parsed = parser.parse(response)

        return {
            "_parsed_response": parsed,
            "_raw": response,
            "summary": parsed.summary,
            "findings": [f.to_dict() for f in parsed.findings],
            "checklist": parsed.checklist,
            "xml_parsed": parsed.success,
            "parse_errors": parsed.errors,
        }
