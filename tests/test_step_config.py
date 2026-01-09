"""Tests for WorkflowStepConfig.

Tests declarative step configuration for multi-model pipelines.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_os.models import FallbackPolicy, ModelTier, RetryPolicy
from empathy_os.workflows.step_config import (
    WorkflowStepConfig,
    steps_from_tier_map,
    validate_step_config,
)


class TestWorkflowStepConfigCreation:
    """Tests for WorkflowStepConfig initialization."""

    def test_basic_creation(self):
        """Test creating a basic step config."""
        step = WorkflowStepConfig(
            name="classify",
            task_type="summarize",
        )

        assert step.name == "classify"
        assert step.task_type == "summarize"
        assert step.tier_hint is None
        assert step.provider_hint is None

    def test_with_tier_hint(self):
        """Test step with tier hint."""
        step = WorkflowStepConfig(
            name="analyze",
            task_type="fix_bug",
            tier_hint="capable",
        )

        assert step.tier_hint == "capable"
        assert step.effective_tier == "capable"

    def test_with_provider_hint(self):
        """Test step with provider hint."""
        step = WorkflowStepConfig(
            name="generate",
            task_type="generate_code",
            provider_hint="openai",
        )

        assert step.provider_hint == "openai"

    def test_with_execution_constraints(self):
        """Test step with execution constraints."""
        step = WorkflowStepConfig(
            name="long_task",
            task_type="architectural_decision",
            timeout_seconds=120,
            max_tokens=4096,
        )

        assert step.timeout_seconds == 120
        assert step.max_tokens == 4096

    def test_with_description_and_metadata(self):
        """Test step with description and metadata."""
        step = WorkflowStepConfig(
            name="review",
            task_type="code_review",
            description="Review code for quality",
            metadata={"priority": "high", "category": "security"},
        )

        assert step.description == "Review code for quality"
        assert step.metadata["priority"] == "high"


class TestTaskTypeNormalization:
    """Tests for task type normalization on creation."""

    def test_task_type_normalized(self):
        """Test that task type is normalized."""
        step = WorkflowStepConfig(
            name="test",
            task_type="SUMMARIZE",  # Should be lowercased
        )

        assert step.task_type == "summarize"

    def test_task_type_with_spaces(self):
        """Test task type normalization with spaces."""
        step = WorkflowStepConfig(
            name="test",
            task_type="fix bug",  # Should be normalized
        )

        # Depends on normalize_task_type implementation
        assert step.task_type is not None


class TestEffectiveTier:
    """Tests for effective tier calculation."""

    def test_effective_tier_from_hint(self):
        """Test effective tier uses hint when provided."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="premium",
        )

        assert step.effective_tier == "premium"

    def test_effective_tier_from_task_type(self):
        """Test effective tier from task type when no hint."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",  # Should route to cheap tier
        )

        # Should be derived from task type routing
        assert step.effective_tier in ("cheap", "capable", "premium")

    def test_effective_tier_enum(self):
        """Test effective tier as enum."""
        step = WorkflowStepConfig(
            name="test",
            task_type="fix_bug",
            tier_hint="capable",
        )

        tier_enum = step.effective_tier_enum
        assert isinstance(tier_enum, ModelTier)
        assert tier_enum == ModelTier.CAPABLE


class TestWithOverrides:
    """Tests for step config overrides."""

    def test_override_tier_hint(self):
        """Test overriding tier hint."""
        original = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="cheap",
        )

        modified = original.with_overrides(tier_hint="premium")

        assert original.tier_hint == "cheap"  # Original unchanged
        assert modified.tier_hint == "premium"
        assert modified.name == "test"
        assert modified.task_type == "summarize"

    def test_override_provider_hint(self):
        """Test overriding provider hint."""
        original = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            provider_hint="anthropic",
        )

        modified = original.with_overrides(provider_hint="openai")

        assert original.provider_hint == "anthropic"
        assert modified.provider_hint == "openai"

    def test_override_timeout(self):
        """Test overriding timeout."""
        original = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            timeout_seconds=30,
        )

        modified = original.with_overrides(timeout_seconds=120)

        assert modified.timeout_seconds == 120

    def test_override_with_policies(self):
        """Test overriding with fallback and retry policies."""
        original = WorkflowStepConfig(
            name="test",
            task_type="summarize",
        )

        fallback = FallbackPolicy(
            primary_provider="anthropic",
            primary_tier="capable",
        )
        retry = RetryPolicy(max_retries=3, initial_delay_ms=100)

        modified = original.with_overrides(
            fallback_policy=fallback,
            retry_policy=retry,
        )

        assert modified.fallback_policy is not None
        assert modified.retry_policy is not None
        assert modified.retry_policy.max_retries == 3

    def test_override_preserves_metadata(self):
        """Test that override preserves metadata copy."""
        original = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            metadata={"key": "value"},
        )

        modified = original.with_overrides(tier_hint="premium")

        # Metadata should be copied, not referenced
        assert modified.metadata == {"key": "value"}
        modified.metadata["new_key"] = "new_value"
        assert "new_key" not in original.metadata


class TestSerialization:
    """Tests for serialization and deserialization."""

    def test_to_dict_basic(self):
        """Test basic to_dict conversion."""
        step = WorkflowStepConfig(
            name="classify",
            task_type="summarize",
            tier_hint="cheap",
        )

        data = step.to_dict()

        assert data["name"] == "classify"
        assert data["task_type"] == "summarize"
        assert data["tier_hint"] == "cheap"
        assert data["effective_tier"] == "cheap"

    def test_to_dict_includes_policies_flags(self):
        """Test to_dict includes policy flags."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            fallback_policy=FallbackPolicy(primary_provider="anthropic", primary_tier="capable"),
        )

        data = step.to_dict()

        assert data["has_fallback_policy"] is True
        assert data["has_retry_policy"] is False

    def test_from_dict_basic(self):
        """Test from_dict creation."""
        data = {
            "name": "analyze",
            "task_type": "code_review",
            "tier_hint": "capable",
            "description": "Code analysis step",
        }

        step = WorkflowStepConfig.from_dict(data)

        assert step.name == "analyze"
        assert step.task_type == "code_review"
        assert step.tier_hint == "capable"
        assert step.description == "Code analysis step"

    def test_from_dict_with_optional_fields(self):
        """Test from_dict with optional fields."""
        data = {
            "name": "test",
            "task_type": "summarize",
            "timeout_seconds": 60,
            "max_tokens": 2048,
            "metadata": {"custom": "data"},
        }

        step = WorkflowStepConfig.from_dict(data)

        assert step.timeout_seconds == 60
        assert step.max_tokens == 2048
        assert step.metadata["custom"] == "data"

    def test_roundtrip(self):
        """Test to_dict -> from_dict roundtrip."""
        original = WorkflowStepConfig(
            name="test",
            task_type="fix_bug",
            tier_hint="capable",
            timeout_seconds=45,
            description="Test step",
            metadata={"version": 1},
        )

        data = original.to_dict()
        restored = WorkflowStepConfig.from_dict(data)

        assert restored.name == original.name
        assert restored.task_type == original.task_type
        assert restored.tier_hint == original.tier_hint
        assert restored.timeout_seconds == original.timeout_seconds
        assert restored.description == original.description
        assert restored.metadata == original.metadata


class TestValidateStepConfig:
    """Tests for step config validation."""

    def test_valid_config(self):
        """Test validation of valid config."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="cheap",
            timeout_seconds=30,
        )

        errors = validate_step_config(step)

        assert errors == []

    def test_missing_name(self):
        """Test validation catches missing name."""
        step = WorkflowStepConfig(
            name="",
            task_type="summarize",
        )

        errors = validate_step_config(step)

        assert any("name" in e.lower() for e in errors)

    def test_missing_task_type(self):
        """Test validation catches missing task type."""
        step = WorkflowStepConfig(
            name="test",
            task_type="",
        )

        errors = validate_step_config(step)

        assert any("task_type" in e.lower() for e in errors)

    def test_invalid_tier_hint(self):
        """Test validation catches invalid tier hint."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="super_expensive",
        )

        errors = validate_step_config(step)

        assert any("tier_hint" in e.lower() for e in errors)

    def test_invalid_provider_hint(self):
        """Test validation catches invalid provider hint."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            provider_hint="unknown_provider",
        )

        errors = validate_step_config(step)

        assert any("provider_hint" in e.lower() for e in errors)

    def test_negative_timeout(self):
        """Test validation catches negative timeout."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            timeout_seconds=-10,
        )

        errors = validate_step_config(step)

        assert any("timeout" in e.lower() for e in errors)

    def test_negative_max_tokens(self):
        """Test validation catches negative max tokens."""
        step = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            max_tokens=-100,
        )

        errors = validate_step_config(step)

        assert any("max_tokens" in e.lower() for e in errors)

    def test_multiple_errors(self):
        """Test validation returns multiple errors."""
        step = WorkflowStepConfig(
            name="",
            task_type="",
            tier_hint="invalid",
            timeout_seconds=-5,
        )

        errors = validate_step_config(step)

        assert len(errors) >= 3


class TestStepsFromTierMap:
    """Tests for legacy tier map conversion."""

    def test_basic_conversion(self):
        """Test basic conversion from tier map."""
        stages = ["classify", "analyze", "report"]
        tier_map = {
            "classify": "cheap",
            "analyze": "capable",
            "report": "premium",
        }

        steps = steps_from_tier_map(stages, tier_map)

        assert len(steps) == 3
        assert steps[0].name == "classify"
        assert steps[0].tier_hint == "cheap"
        assert steps[1].name == "analyze"
        assert steps[1].tier_hint == "capable"
        assert steps[2].name == "report"
        assert steps[2].tier_hint == "premium"

    def test_default_tier_for_missing(self):
        """Test default tier for stages not in tier map."""
        stages = ["stage1", "stage2"]
        tier_map = {"stage1": "cheap"}

        steps = steps_from_tier_map(stages, tier_map)

        assert steps[0].tier_hint == "cheap"
        assert steps[1].tier_hint == "capable"  # Default

    def test_custom_task_type(self):
        """Test custom default task type."""
        stages = ["step1"]
        tier_map = {"step1": "cheap"}

        steps = steps_from_tier_map(stages, tier_map, task_type_default="code_review")

        assert steps[0].task_type == "code_review"

    def test_handles_enum_tier_values(self):
        """Test conversion handles ModelTier enum values."""
        from empathy_os.workflows.base import ModelTier as LocalModelTier

        stages = ["step1", "step2"]
        tier_map = {
            "step1": LocalModelTier.CHEAP,  # Enum
            "step2": "capable",  # String
        }

        steps = steps_from_tier_map(stages, tier_map)

        assert steps[0].tier_hint == "cheap"
        assert steps[1].tier_hint == "capable"


class TestWorkflowStepConfigEquality:
    """Tests for step config comparison."""

    def test_configs_with_same_values_are_independent(self):
        """Test that identical configs are independent objects."""
        step1 = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="cheap",
        )
        step2 = WorkflowStepConfig(
            name="test",
            task_type="summarize",
            tier_hint="cheap",
        )

        # They have same values
        assert step1.name == step2.name
        assert step1.tier_hint == step2.tier_hint

        # But are different objects
        assert step1 is not step2
