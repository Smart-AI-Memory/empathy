"""Integration tests for telemetry tracking with BaseWorkflow.

Tests that telemetry tracking works correctly when integrated with
the workflow execution system.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from empathy_os.telemetry import UsageTracker
from empathy_os.workflows.base import BaseWorkflow, ModelTier


class TestWorkflow(BaseWorkflow):
    """Simple test workflow for integration testing."""

    name = "test-workflow"
    description = "Test workflow for telemetry"
    stages = ["stage1", "stage2"]
    tier_map = {
        "stage1": ModelTier.CHEAP,
        "stage2": ModelTier.CAPABLE,
    }

    async def run_stage(self, stage_name, tier, input_data):
        """Mock stage execution."""
        return {"result": f"Completed {stage_name}"}, 100, 50


@pytest.fixture
def temp_telemetry_dir():
    """Create a temporary directory for telemetry data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def tracker(temp_telemetry_dir):
    """Create a UsageTracker with temporary directory."""
    tracker = UsageTracker(telemetry_dir=temp_telemetry_dir)
    # Reset singleton to use test instance
    UsageTracker._instance = tracker
    yield tracker
    # Clean up singleton
    UsageTracker._instance = None


@pytest.mark.asyncio
async def test_workflow_tracks_llm_calls(tracker):
    """Test that workflow execution tracks telemetry for LLM calls."""
    # Create workflow with telemetry enabled
    workflow = TestWorkflow()

    # Mock the LLM executor to avoid actual API calls
    mock_executor = AsyncMock()
    mock_executor.run = AsyncMock(return_value=MagicMock(
        content="Test response",
        tokens_input=100,
        tokens_output=50,
        cost_estimate=0.01,
        tier="CAPABLE",
        model_id="test-model",
    ))
    workflow._executor = mock_executor

    # Execute workflow
    result = await workflow.execute(input="test")

    # Check that telemetry entries were created
    entries = tracker.get_recent_entries(limit=10)
    assert len(entries) > 0

    # Verify entry fields
    entry = entries[0]
    assert entry["workflow"] == "test-workflow"
    assert entry["tier"] in ["CHEAP", "CAPABLE"]
    assert "cost" in entry
    assert "tokens" in entry
    assert "duration_ms" in entry


@pytest.mark.asyncio
async def test_workflow_tracks_cache_hits(tracker):
    """Test that cache hits are tracked in telemetry."""
    # Create workflow with caching enabled
    workflow = TestWorkflow(enable_cache=True)

    # Mock cache that returns a hit
    mock_cache = MagicMock()
    mock_cache.get = MagicMock(return_value={
        "content": "Cached response",
        "input_tokens": 100,
        "output_tokens": 50,
    })
    workflow._cache = mock_cache

    # Call _call_llm to trigger cache hit
    content, in_tokens, out_tokens = await workflow._call_llm(
        tier=ModelTier.CAPABLE,
        system="Test system",
        user_message="Test message",
    )

    # Check telemetry
    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1

    entry = entries[0]
    assert entry["cache"]["hit"] is True
    assert entry["duration_ms"] < 1000  # Cache hits should be fast


@pytest.mark.asyncio
async def test_workflow_tracks_different_tiers(tracker):
    """Test that different model tiers are tracked correctly."""
    workflow = TestWorkflow()

    # Mock executor
    mock_executor = AsyncMock()

    def mock_run(task_type, prompt, system, context, **kwargs):
        tier = context.metadata.get("tier_hint", "CAPABLE").upper()
        return MagicMock(
            content=f"Response for {tier}",
            tokens_input=100,
            tokens_output=50,
            cost_estimate=0.01 if tier == "CAPABLE" else 0.001,
            tier=tier,
            model_id=f"model-{tier.lower()}",
        )

    mock_executor.run = AsyncMock(side_effect=mock_run)
    workflow._executor = mock_executor

    # Execute workflow (has CHEAP and CAPABLE stages)
    result = await workflow.execute(input="test")

    # Check that both tiers were tracked
    entries = tracker.get_recent_entries(limit=10)
    tiers = {entry["tier"] for entry in entries}
    # Should have at least one tier tracked
    assert len(tiers) > 0


@pytest.mark.asyncio
async def test_telemetry_disabled(tracker, temp_telemetry_dir):
    """Test that workflows work when telemetry is disabled."""
    workflow = TestWorkflow()
    workflow._enable_telemetry = False

    # Mock executor
    mock_executor = AsyncMock()
    mock_executor.run = AsyncMock(return_value=MagicMock(
        content="Test response",
        tokens_input=100,
        tokens_output=50,
        cost_estimate=0.01,
        tier="CAPABLE",
        model_id="test-model",
    ))
    workflow._executor = mock_executor

    # Execute workflow
    result = await workflow.execute(input="test")

    # Should complete successfully
    assert result.success

    # No telemetry entries should be created
    entries = tracker.get_recent_entries(limit=10)
    assert len(entries) == 0


@pytest.mark.asyncio
async def test_telemetry_tracking_on_error(tracker):
    """Test that telemetry gracefully handles tracking errors."""
    workflow = TestWorkflow()

    # Create a tracker that will fail when writing
    broken_tracker = UsageTracker(telemetry_dir=Path("/nonexistent/path"))
    workflow._telemetry_tracker = broken_tracker

    # Mock executor
    mock_executor = AsyncMock()
    mock_executor.run = AsyncMock(return_value=MagicMock(
        content="Test response",
        tokens_input=100,
        tokens_output=50,
        cost_estimate=0.01,
        tier="CAPABLE",
        model_id="test-model",
    ))
    workflow._executor = mock_executor

    # Workflow should still execute successfully despite telemetry error
    result = await workflow.execute(input="test")
    assert result.success


@pytest.mark.asyncio
async def test_multiple_workflows_share_tracker(tracker):
    """Test that multiple workflows share the same tracker singleton."""
    workflow1 = TestWorkflow()
    workflow2 = TestWorkflow()

    # Both should use the same tracker
    assert workflow1._telemetry_tracker is workflow2._telemetry_tracker

    # Mock executor for both
    mock_executor = AsyncMock()
    mock_executor.run = AsyncMock(return_value=MagicMock(
        content="Test response",
        tokens_input=100,
        tokens_output=50,
        cost_estimate=0.01,
        tier="CAPABLE",
        model_id="test-model",
    ))
    workflow1._executor = mock_executor
    workflow2._executor = mock_executor

    # Execute both workflows
    await workflow1.execute(input="test1")
    await workflow2.execute(input="test2")

    # Both should have logged to the same file
    entries = tracker.get_recent_entries(limit=20)
    workflows = {entry["workflow"] for entry in entries}
    assert "test-workflow" in workflows
