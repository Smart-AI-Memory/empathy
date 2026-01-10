"""Tests for tier fallback functionality in workflows.

Tests the intelligent tier fallback system that tries CHEAP → CAPABLE → PREMIUM
with automatic tier upgrades when quality gates fail.
"""

import pytest

from empathy_os.workflows.base import BaseWorkflow, ModelTier


class MockTierFallbackWorkflow(BaseWorkflow):
    """Mock workflow for testing tier fallback."""

    name = "test-tier-fallback"
    description = "Test workflow for tier fallback"
    stages = ["stage1", "stage2"]
    tier_map = {
        "stage1": ModelTier.CAPABLE,
        "stage2": ModelTier.CAPABLE,
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validation_results = {}
        self._stage_executions = []

    def validate_output(self, stage_output: dict) -> tuple[bool, str | None]:
        """Return pre-configured validation result for testing."""
        stage = stage_output.get("stage_name")
        tier = stage_output.get("tier")

        # Track execution
        self._stage_executions.append((stage, tier))

        # Return validation result
        validation_key = f"{stage}_{tier}"
        return self._validation_results.get(validation_key, (True, None))

    async def run_stage(self, stage_name: str, tier: ModelTier, input_data: dict):
        """Mock stage execution."""
        # Track execution (works for both fallback and standard mode)
        if not hasattr(self, "_run_stage_calls"):
            self._run_stage_calls = []
        self._run_stage_calls.append((stage_name, tier.value))

        output = {
            "stage_name": stage_name,
            "tier": tier.value,
            "result": f"Output from {stage_name} at {tier.value}",
        }
        return output, 1000, 500  # output, input_tokens, output_tokens


@pytest.mark.asyncio
async def test_tier_fallback_succeeds_with_cheap():
    """Test workflow succeeds on first try with CHEAP tier."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # All stages succeed at CHEAP tier
    workflow._validation_results = {
        "stage1_cheap": (True, None),
        "stage2_cheap": (True, None),
    }

    result = await workflow.execute()

    # Verify success
    assert result.success
    assert len(workflow._tier_progression) == 2
    assert workflow._tier_progression[0] == ("stage1", "cheap", True)
    assert workflow._tier_progression[1] == ("stage2", "cheap", True)

    # Verify only CHEAP was tried
    assert len(workflow._stage_executions) == 2
    assert all(tier == "cheap" for _, tier in workflow._stage_executions)


@pytest.mark.asyncio
async def test_tier_fallback_upgrades_on_failure():
    """Test workflow upgrades tier when validation fails."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # stage1: fails at CHEAP, succeeds at CAPABLE
    # stage2: succeeds at CHEAP
    workflow._validation_results = {
        "stage1_cheap": (False, "quality_low"),
        "stage1_capable": (True, None),
        "stage2_cheap": (True, None),
    }

    result = await workflow.execute()

    # Verify success
    assert result.success

    # Verify tier progression
    assert len(workflow._tier_progression) == 3
    assert workflow._tier_progression[0] == ("stage1", "cheap", False)
    assert workflow._tier_progression[1] == ("stage1", "capable", True)
    assert workflow._tier_progression[2] == ("stage2", "cheap", True)

    # Verify executions
    assert workflow._stage_executions[0] == ("stage1", "cheap")
    assert workflow._stage_executions[1] == ("stage1", "capable")
    assert workflow._stage_executions[2] == ("stage2", "cheap")


@pytest.mark.asyncio
async def test_tier_fallback_all_tiers_exhausted():
    """Test workflow fails when all tiers are exhausted."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # stage1 fails at all tiers
    workflow._validation_results = {
        "stage1_cheap": (False, "quality_low"),
        "stage1_capable": (False, "quality_low"),
        "stage1_premium": (False, "quality_low"),
    }

    result = await workflow.execute()

    # Workflow should fail (error is caught and returned in result)
    assert not result.success
    assert "Stage stage1 failed with all tiers" in result.error

    # Verify all tiers were tried
    assert len(workflow._tier_progression) == 3
    assert workflow._tier_progression[0] == ("stage1", "cheap", False)
    assert workflow._tier_progression[1] == ("stage1", "capable", False)
    assert workflow._tier_progression[2] == ("stage1", "premium", False)


@pytest.mark.asyncio
async def test_tier_fallback_disabled_by_default():
    """Test tier fallback is opt-in (disabled by default)."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=False)

    result = await workflow.execute()

    # Should use configured tier_map (CAPABLE), no fallback attempts
    assert result.success
    assert len(workflow._tier_progression) == 0  # No tracking when disabled

    # Should execute at CAPABLE tier (from tier_map)
    assert len(workflow._run_stage_calls) == 2
    # Both stages should use CAPABLE tier from tier_map
    assert workflow._run_stage_calls[0] == ("stage1", "capable")
    assert workflow._run_stage_calls[1] == ("stage2", "capable")


@pytest.mark.asyncio
async def test_tier_fallback_multiple_upgrades():
    """Test workflow upgrades through multiple tiers (CHEAP → CAPABLE → PREMIUM)."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # stage1: fails at CHEAP and CAPABLE, succeeds at PREMIUM
    workflow._validation_results = {
        "stage1_cheap": (False, "quality_low"),
        "stage1_capable": (False, "quality_medium"),
        "stage1_premium": (True, None),
        "stage2_cheap": (True, None),
    }

    result = await workflow.execute()

    # Verify success
    assert result.success

    # Verify full tier progression
    assert len(workflow._tier_progression) == 4
    assert workflow._tier_progression[0] == ("stage1", "cheap", False)
    assert workflow._tier_progression[1] == ("stage1", "capable", False)
    assert workflow._tier_progression[2] == ("stage1", "premium", True)
    assert workflow._tier_progression[3] == ("stage2", "cheap", True)

    # Verify all attempts were made
    assert len(workflow._stage_executions) == 4
    assert workflow._stage_executions[0] == ("stage1", "cheap")
    assert workflow._stage_executions[1] == ("stage1", "capable")
    assert workflow._stage_executions[2] == ("stage1", "premium")
    assert workflow._stage_executions[3] == ("stage2", "cheap")


@pytest.mark.asyncio
async def test_tier_fallback_with_exception():
    """Test tier fallback handles exceptions during stage execution."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # Mock run_stage to raise exception at CHEAP, succeed at CAPABLE
    original_run_stage = workflow.run_stage
    call_count = [0]

    async def mock_run_stage(stage_name: str, tier: ModelTier, input_data: dict):
        call_count[0] += 1
        if call_count[0] == 1 and tier == ModelTier.CHEAP:
            # First call at CHEAP tier - raise exception
            raise RuntimeError("Simulated API error")
        # Other calls succeed normally
        return await original_run_stage(stage_name, tier, input_data)

    workflow.run_stage = mock_run_stage

    # All tiers succeed validation when they execute
    workflow._validation_results = {
        "stage1_capable": (True, None),
        "stage2_cheap": (True, None),
    }

    result = await workflow.execute()

    # Verify success
    assert result.success

    # Verify tier progression includes the failed CHEAP attempt
    assert len(workflow._tier_progression) == 3
    assert workflow._tier_progression[0] == ("stage1", "cheap", False)  # Exception
    assert workflow._tier_progression[1] == ("stage1", "capable", True)  # Success
    assert workflow._tier_progression[2] == ("stage2", "cheap", True)  # Success


@pytest.mark.asyncio
async def test_tier_fallback_cost_tracking():
    """Test that tier fallback correctly tracks costs for each attempt."""
    workflow = MockTierFallbackWorkflow(enable_tier_fallback=True)

    # stage1: fails at CHEAP, succeeds at CAPABLE
    workflow._validation_results = {
        "stage1_cheap": (False, "quality_low"),
        "stage1_capable": (True, None),
        "stage2_cheap": (True, None),
    }

    result = await workflow.execute()

    # Verify only successful stages are in result.stages
    # (failed attempts are tracked in _tier_progression but not in stages)
    assert result.success
    assert len(result.stages) == 2  # Only successful completions

    # First successful stage should be CAPABLE (not CHEAP)
    assert result.stages[0].tier == ModelTier.CAPABLE
    assert result.stages[1].tier == ModelTier.CHEAP


def test_validate_output_default_implementation():
    """Test BaseWorkflow default validate_output implementation."""

    # Create a minimal workflow to test the base implementation
    class MinimalWorkflow(BaseWorkflow):
        name = "minimal-test"
        description = "Minimal test workflow"
        stages = ["test"]
        tier_map = {"test": ModelTier.CHEAP}

        async def run_stage(self, stage_name: str, tier: ModelTier, input_data: dict):
            return {}, 0, 0

    workflow = MinimalWorkflow()

    # Empty output should fail
    is_valid, reason = workflow.validate_output({})
    assert not is_valid
    assert reason == "output_empty"

    # Output with error should fail
    is_valid, reason = workflow.validate_output({"error": "Something went wrong"})
    assert not is_valid
    assert reason == "execution_error"

    # Valid output should pass
    is_valid, reason = workflow.validate_output({"result": "success", "data": [1, 2, 3]})
    assert is_valid
    assert reason is None
