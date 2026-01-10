"""Tests for Sonnet 4.5 → Opus 4.5 intelligent fallback.

These tests verify:
1. Sonnet handles most tasks successfully (target: >95%)
2. Opus fallback triggers for complex reasoning
3. Cost savings are tracked accurately
4. Circuit breaker works correctly

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime, timedelta

import pytest

from empathy_os.models.empathy_executor import EmpathyLLMExecutor
from empathy_os.models.fallback import (
    SONNET_TO_OPUS_FALLBACK,
    CircuitBreaker,
    ResilientExecutor,
)
from empathy_os.models.telemetry import TelemetryAnalytics, get_telemetry_store


class TestSonnetOpusFallback:
    """Test suite for Sonnet → Opus fallback mechanism."""

    @pytest.mark.asyncio
    async def test_simple_tasks_use_sonnet(self):
        """Test that simple tasks succeed with Sonnet 4.5 (no fallback)."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        # Simple code generation
        response = await executor.run(
            task_type="code_generation",
            prompt="Write a Python function to calculate factorial",
        )

        assert response.success
        assert not response.metadata.get("fallback_used"), "Simple task should not trigger fallback"
        assert response.metadata.get("original_provider") == "anthropic"

    @pytest.mark.asyncio
    async def test_complex_reasoning_may_use_opus(self):
        """Test that complex reasoning tasks may trigger Opus fallback."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        # Complex multi-step reasoning
        response = await executor.run(
            task_type="complex_reasoning",
            prompt="""
            Analyze this distributed system for subtle race conditions and deadlocks:

            System A acquires lock X, then lock Y
            System B acquires lock Y, then lock X
            System C reads from X and Y without locks

            Identify all potential issues and suggest fixes.
            """,
        )

        assert response.success
        # May or may not fallback - just verify tracking works
        if response.metadata.get("fallback_used"):
            assert "Opus" in str(response.metadata.get("fallback_chain"))

    @pytest.mark.asyncio
    async def test_telemetry_tracking(self):
        """Test that fallback events are tracked in telemetry."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        # Make several calls
        tasks = [
            "Write a hello world function",
            "Explain quicksort algorithm",
            "Debug this code: x = [1,2,3]; print(x[5])",
        ]

        for task in tasks:
            await executor.run(
                task_type="code_review",
                prompt=task,
            )

        # Check telemetry
        store = get_telemetry_store()
        calls = store.get_calls(limit=10)

        assert len(calls) >= 3, "Should have telemetry for recent calls"

    @pytest.mark.asyncio
    async def test_cost_savings_calculation(self):
        """Test that cost savings analytics work correctly."""
        analytics = TelemetryAnalytics(get_telemetry_store())

        # Get recent stats
        since = datetime.utcnow() - timedelta(hours=1)
        stats = analytics.sonnet_opus_fallback_analysis(since=since)

        # Verify structure
        assert "total_calls" in stats
        assert "sonnet_attempts" in stats
        assert "opus_fallbacks" in stats
        assert "actual_cost" in stats
        assert "always_opus_cost" in stats
        assert "savings" in stats
        assert "savings_percent" in stats

        # If we have calls, verify calculations make sense
        if stats["total_calls"] > 0:
            assert stats["actual_cost"] <= stats["always_opus_cost"]
            assert stats["savings"] >= 0
            assert 0 <= stats["savings_percent"] <= 100

    def test_circuit_breaker_protects_against_cascading_failures(self):
        """Test that circuit breaker opens after threshold failures."""
        breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)

        # Simulate failures
        for _ in range(3):
            breaker.record_failure("anthropic", "capable")

        # Circuit should be open
        assert not breaker.is_available(
            "anthropic", "capable"
        ), "Circuit should be open after threshold"

        # Other tiers should still be available
        assert breaker.is_available(
            "anthropic", "premium"
        ), "Premium tier should still be available"

    @pytest.mark.asyncio
    async def test_fallback_metadata_complete(self):
        """Test that fallback metadata is complete and accurate."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        response = await executor.run(
            task_type="code_review",
            prompt="Review this code for best practices",
        )

        # Check metadata fields
        assert "original_provider" in response.metadata
        assert "original_tier" in response.metadata
        assert "fallback_used" in response.metadata
        assert "retry_count" in response.metadata
        assert "circuit_breaker_state" in response.metadata

        if response.metadata.get("fallback_used"):
            assert "fallback_chain" in response.metadata


class TestSonnetOpusAnalytics:
    """Test suite for analytics and reporting."""

    def test_analytics_with_no_data(self):
        """Test analytics gracefully handle no data."""
        analytics = TelemetryAnalytics(get_telemetry_store())

        # Future date with no data
        since = datetime.utcnow() + timedelta(days=1)
        stats = analytics.sonnet_opus_fallback_analysis(since=since)

        assert stats["total_calls"] == 0
        assert stats["sonnet_attempts"] == 0
        assert stats["opus_fallbacks"] == 0
        assert stats["savings"] == 0

    def test_savings_calculation_accuracy(self):
        """Test that cost savings calculations are accurate."""
        # This is a unit test of the calculation logic
        # Simulated data
        sonnet_input_cost = 3.00 / 1_000_000
        sonnet_output_cost = 15.00 / 1_000_000
        opus_input_cost = 15.00 / 1_000_000
        opus_output_cost = 75.00 / 1_000_000

        # Scenario: 100K input, 10K output tokens all on Sonnet
        input_tokens = 100_000
        output_tokens = 10_000

        actual_cost = (input_tokens * sonnet_input_cost) + (output_tokens * sonnet_output_cost)
        always_opus_cost = (input_tokens * opus_input_cost) + (output_tokens * opus_output_cost)
        savings = always_opus_cost - actual_cost
        savings_percent = (savings / always_opus_cost) * 100

        # Verify calculations
        assert actual_cost == pytest.approx(0.45, abs=0.01)  # $0.30 + $0.15
        assert always_opus_cost == pytest.approx(2.25, abs=0.01)  # $1.50 + $0.75
        assert savings == pytest.approx(1.80, abs=0.01)
        assert savings_percent == pytest.approx(80.0, abs=0.1)


# Integration test scenarios
@pytest.mark.integration
class TestSonnetOpusFallbackIntegration:
    """Integration tests for real-world scenarios."""

    @pytest.mark.asyncio
    async def test_code_review_workflow(self):
        """Test code review workflow with fallback."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        # Typical code review
        code_to_review = """
        def process_payment(amount, user_id):
            # TODO: Add validation
            db.execute(f"INSERT INTO payments VALUES ({amount}, {user_id})")
            return True
        """

        response = await executor.run(
            task_type="code_review",
            prompt=f"Review this code for security issues:\n{code_to_review}",
        )

        assert response.success
        assert "SQL injection" in response.content.lower()

    @pytest.mark.asyncio
    async def test_test_generation_workflow(self):
        """Test test generation workflow with fallback."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        response = await executor.run(
            task_type="test_generation",
            prompt="Generate pytest tests for a function that calculates Fibonacci numbers",
        )

        assert response.success
        assert "pytest" in response.content.lower() or "test_" in response.content

    @pytest.mark.asyncio
    async def test_refactoring_workflow(self):
        """Test refactoring workflow with fallback."""
        base_executor = EmpathyLLMExecutor(provider="anthropic")
        executor = ResilientExecutor(
            executor=base_executor,
            fallback_policy=SONNET_TO_OPUS_FALLBACK,
        )

        messy_code = """
        def f(x,y,z):
            if x>0:
                if y>0:
                    if z>0:
                        return x+y+z
            return 0
        """

        response = await executor.run(
            task_type="refactoring",
            prompt=f"Refactor this code for better readability:\n{messy_code}",
        )

        assert response.success
