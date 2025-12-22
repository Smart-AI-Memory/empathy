"""
Workflow Step Configuration for Multi-Model Pipelines

Provides declarative step configuration that integrates with:
- empathy_os.models.registry for model lookup
- empathy_os.models.tasks for task-type routing
- empathy_os.models.fallback for resilience policies

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass, field
from typing import Any

from empathy_os.models import (
    FallbackPolicy,
    ModelTier,
    RetryPolicy,
    get_tier_for_task,
    normalize_task_type,
)


@dataclass
class WorkflowStepConfig:
    """
    Configuration for a single workflow step.

    Combines declarative routing configuration with optional overrides
    for provider, tier, and resilience policies.

    Example:
        >>> step = WorkflowStepConfig(
        ...     name="triage",
        ...     task_type="classify",
        ...     tier_hint="cheap",
        ...     timeout_seconds=30,
        ... )
        >>> step.effective_tier
        'cheap'

        >>> step2 = WorkflowStepConfig(
        ...     name="analysis",
        ...     task_type="fix_bug",
        ...     # tier_hint not specified, uses task_type routing
        ... )
        >>> step2.effective_tier
        'capable'
    """

    # Required fields
    name: str
    task_type: str  # Canonical task type (e.g., "summarize", "fix_bug", "coordinate")

    # Optional routing hints (override task-based routing)
    tier_hint: str | None = None  # "cheap" | "capable" | "premium"
    provider_hint: str | None = None  # "anthropic" | "openai" | "ollama"

    # Optional resilience configuration
    fallback_policy: FallbackPolicy | None = None
    retry_policy: RetryPolicy | None = None

    # Optional execution constraints
    timeout_seconds: int | None = None
    max_tokens: int | None = None

    # Optional metadata
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Normalize task_type on creation."""
        self.task_type = normalize_task_type(self.task_type)

    @property
    def effective_tier(self) -> str:
        """
        Get the effective tier for this step.

        Priority:
        1. tier_hint if specified
        2. Tier derived from task_type routing

        Returns:
            Tier name ("cheap", "capable", or "premium")
        """
        if self.tier_hint:
            return self.tier_hint

        tier = get_tier_for_task(self.task_type)
        return tier.value

    @property
    def effective_tier_enum(self) -> ModelTier:
        """Get effective tier as ModelTier enum."""
        return ModelTier(self.effective_tier)

    def with_overrides(
        self,
        tier_hint: str | None = None,
        provider_hint: str | None = None,
        fallback_policy: FallbackPolicy | None = None,
        retry_policy: RetryPolicy | None = None,
        timeout_seconds: int | None = None,
    ) -> "WorkflowStepConfig":
        """
        Create a new step config with overrides applied.

        Useful for runtime customization without mutating the original.

        Returns:
            New WorkflowStepConfig with overrides applied
        """
        return WorkflowStepConfig(
            name=self.name,
            task_type=self.task_type,
            tier_hint=tier_hint if tier_hint is not None else self.tier_hint,
            provider_hint=provider_hint if provider_hint is not None else self.provider_hint,
            fallback_policy=(
                fallback_policy if fallback_policy is not None else self.fallback_policy
            ),
            retry_policy=retry_policy if retry_policy is not None else self.retry_policy,
            timeout_seconds=(
                timeout_seconds if timeout_seconds is not None else self.timeout_seconds
            ),
            max_tokens=self.max_tokens,
            description=self.description,
            metadata=self.metadata.copy(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "task_type": self.task_type,
            "tier_hint": self.tier_hint,
            "provider_hint": self.provider_hint,
            "effective_tier": self.effective_tier,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
            "description": self.description,
            "metadata": self.metadata,
            "has_fallback_policy": self.fallback_policy is not None,
            "has_retry_policy": self.retry_policy is not None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WorkflowStepConfig":
        """
        Create from dictionary.

        Note: fallback_policy and retry_policy are not restored from dict
        (they should be configured programmatically).
        """
        return cls(
            name=data["name"],
            task_type=data["task_type"],
            tier_hint=data.get("tier_hint"),
            provider_hint=data.get("provider_hint"),
            timeout_seconds=data.get("timeout_seconds"),
            max_tokens=data.get("max_tokens"),
            description=data.get("description", ""),
            metadata=data.get("metadata", {}),
        )


def validate_step_config(step: WorkflowStepConfig) -> list[str]:
    """
    Validate a step configuration.

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    if not step.name:
        errors.append("Step name is required")

    if not step.task_type:
        errors.append("Step task_type is required")

    if step.tier_hint and step.tier_hint not in ("cheap", "capable", "premium"):
        errors.append(f"Invalid tier_hint: {step.tier_hint}")

    if step.provider_hint and step.provider_hint not in ("anthropic", "openai", "ollama", "hybrid"):
        errors.append(f"Invalid provider_hint: {step.provider_hint}")

    if step.timeout_seconds is not None and step.timeout_seconds <= 0:
        errors.append(f"timeout_seconds must be positive: {step.timeout_seconds}")

    if step.max_tokens is not None and step.max_tokens <= 0:
        errors.append(f"max_tokens must be positive: {step.max_tokens}")

    return errors


def steps_from_tier_map(
    stages: list[str],
    tier_map: dict[str, str],
    task_type_default: str = "generate_code",
) -> list[WorkflowStepConfig]:
    """
    Convert legacy stages/tier_map to WorkflowStepConfig list.

    Useful for migrating existing workflows.

    Args:
        stages: List of stage names
        tier_map: Mapping of stage name to tier
        task_type_default: Default task type if not inferrable

    Returns:
        List of WorkflowStepConfig
    """
    steps = []
    for stage_name in stages:
        tier = tier_map.get(stage_name, "capable")
        # Handle both string and enum tier values
        if hasattr(tier, "value"):
            tier = tier.value

        steps.append(
            WorkflowStepConfig(
                name=stage_name,
                task_type=task_type_default,
                tier_hint=tier,
            )
        )
    return steps
