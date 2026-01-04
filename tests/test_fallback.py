"""Tests for Multi-Model Fallback and Resilience Module

Tests the fallback policies, circuit breaker, and retry logic:
- FallbackPolicy and FallbackStrategy
- CircuitBreaker state management
- RetryPolicy with exponential backoff
- ResilientExecutor integration

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime, timedelta
from unittest.mock import AsyncMock

import pytest

from empathy_os.models.fallback import (
    DEFAULT_FALLBACK_POLICY,
    DEFAULT_RETRY_POLICY,
    CircuitBreaker,
    FallbackPolicy,
    FallbackStep,
    FallbackStrategy,
    ResilientExecutor,
    RetryPolicy,
)


class TestFallbackStrategy:
    """Tests for FallbackStrategy enum."""

    def test_strategy_values(self):
        """Test all strategy values exist."""
        assert FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER.value == "same_tier_different_provider"
        assert FallbackStrategy.CHEAPER_TIER_SAME_PROVIDER.value == "cheaper_tier_same_provider"
        assert FallbackStrategy.DIFFERENT_PROVIDER_ANY_TIER.value == "different_provider_any_tier"
        assert FallbackStrategy.CUSTOM.value == "custom"


class TestFallbackStep:
    """Tests for FallbackStep dataclass."""

    def test_create_step(self):
        """Test creating a fallback step."""
        step = FallbackStep(
            provider="anthropic",
            tier="capable",
            description="Primary capable tier",
        )

        assert step.provider == "anthropic"
        assert step.tier == "capable"

    def test_model_id_property(self):
        """Test model_id property retrieval."""
        step = FallbackStep(
            provider="anthropic",
            tier="cheap",
        )

        # Should return model ID from registry
        assert step.model_id == "claude-3-5-haiku-20241022"


class TestFallbackPolicy:
    """Tests for FallbackPolicy configuration."""

    def test_default_policy(self):
        """Test default policy values."""
        policy = FallbackPolicy()

        assert policy.primary_provider == "anthropic"
        assert policy.primary_tier == "capable"
        assert policy.strategy == FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER
        assert policy.max_retries == 2

    def test_same_tier_different_provider_chain(self):
        """Test SAME_TIER_DIFFERENT_PROVIDER strategy."""
        policy = FallbackPolicy(
            primary_provider="anthropic",
            primary_tier="capable",
            strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
        )

        chain = policy.get_fallback_chain()

        # Should include openai and ollama at capable tier
        assert len(chain) >= 2
        providers = [step.provider for step in chain]
        assert "anthropic" not in providers  # Primary not in fallback
        assert "openai" in providers
        assert all(step.tier == "capable" for step in chain)

    def test_cheaper_tier_same_provider_chain(self):
        """Test CHEAPER_TIER_SAME_PROVIDER strategy."""
        policy = FallbackPolicy(
            primary_provider="anthropic",
            primary_tier="premium",
            strategy=FallbackStrategy.CHEAPER_TIER_SAME_PROVIDER,
        )

        chain = policy.get_fallback_chain()

        # Should go premium -> capable -> cheap
        assert len(chain) == 2
        assert chain[0].tier == "capable"
        assert chain[1].tier == "cheap"
        assert all(step.provider == "anthropic" for step in chain)

    def test_different_provider_any_tier_chain(self):
        """Test DIFFERENT_PROVIDER_ANY_TIER strategy."""
        policy = FallbackPolicy(
            primary_provider="anthropic",
            primary_tier="capable",
            strategy=FallbackStrategy.DIFFERENT_PROVIDER_ANY_TIER,
        )

        chain = policy.get_fallback_chain()

        # Should include other providers with same tier first, then cheaper
        assert len(chain) >= 2
        # First entries should be same tier on different providers
        assert chain[0].tier == "capable"

    def test_custom_chain(self):
        """Test CUSTOM strategy with explicit chain."""
        custom_chain = [
            FallbackStep("openai", "capable", "OpenAI first"),
            FallbackStep("ollama", "cheap", "Local fallback"),
        ]

        policy = FallbackPolicy(
            strategy=FallbackStrategy.CUSTOM,
            custom_chain=custom_chain,
        )

        chain = policy.get_fallback_chain()
        assert chain == custom_chain

    def test_global_default_policy(self):
        """Test the global default policy."""
        assert DEFAULT_FALLBACK_POLICY.primary_provider == "anthropic"
        assert DEFAULT_FALLBACK_POLICY.primary_tier == "capable"


class TestCircuitBreaker:
    """Tests for CircuitBreaker state management."""

    def test_initial_state_available(self):
        """Test that providers start available."""
        breaker = CircuitBreaker()

        assert breaker.is_available("anthropic") is True
        assert breaker.is_available("openai") is True

    def test_record_failures_opens_circuit(self):
        """Test that failures open the circuit."""
        breaker = CircuitBreaker(failure_threshold=3)

        # Record failures
        for _ in range(3):
            breaker.record_failure("anthropic")

        # Circuit should now be open
        assert breaker.is_available("anthropic") is False

    def test_below_threshold_stays_closed(self):
        """Test circuit stays closed below threshold."""
        breaker = CircuitBreaker(failure_threshold=5)

        for _ in range(4):
            breaker.record_failure("anthropic")

        # Still below threshold
        assert breaker.is_available("anthropic") is True

    def test_success_resets_failure_count(self):
        """Test success resets the failure counter."""
        breaker = CircuitBreaker(failure_threshold=3)

        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")
        breaker.record_success("anthropic")
        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")

        # Should still be available (only 2 consecutive failures)
        assert breaker.is_available("anthropic") is True

    def test_recovery_after_timeout(self):
        """Test circuit recovers after timeout."""
        breaker = CircuitBreaker(
            failure_threshold=2,
            recovery_timeout_seconds=1,
        )

        # Open the circuit
        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")
        assert breaker.is_available("anthropic") is False

        # Manually set opened_at to past
        state = breaker._get_state("anthropic")
        state.opened_at = datetime.now() - timedelta(seconds=2)

        # Should now be available (half-open)
        assert breaker.is_available("anthropic") is True

    def test_get_status(self):
        """Test getting circuit breaker status."""
        breaker = CircuitBreaker(failure_threshold=2)

        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")

        status = breaker.get_status()

        assert "anthropic" in status
        assert status["anthropic"]["failure_count"] == 2
        assert status["anthropic"]["is_open"] is True

    def test_reset_single_provider(self):
        """Test resetting a single provider."""
        breaker = CircuitBreaker(failure_threshold=2)

        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")
        breaker.record_failure("openai")

        breaker.reset("anthropic")

        assert breaker.is_available("anthropic") is True
        status = breaker.get_status()
        assert status.get("anthropic", {}).get("failure_count", 0) == 0

    def test_reset_all_providers(self):
        """Test resetting all providers."""
        breaker = CircuitBreaker(failure_threshold=2)

        breaker.record_failure("anthropic")
        breaker.record_failure("anthropic")
        breaker.record_failure("openai")
        breaker.record_failure("openai")

        breaker.reset()

        # After reset, providers are available again
        assert breaker.is_available("anthropic") is True
        assert breaker.is_available("openai") is True
        # After reset, the states dict is cleared
        status = breaker.get_status()
        # Either empty dict or all providers show 0 failures
        assert len(status) == 0 or all(s["failure_count"] == 0 for s in status.values())


class TestRetryPolicy:
    """Tests for RetryPolicy configuration."""

    def test_default_policy(self):
        """Test default retry policy values."""
        policy = RetryPolicy()

        assert policy.max_retries == 3
        assert policy.initial_delay_ms == 1000
        assert policy.exponential_backoff is True

    def test_constant_delay(self):
        """Test constant delay without backoff."""
        policy = RetryPolicy(
            initial_delay_ms=500,
            exponential_backoff=False,
        )

        assert policy.get_delay_ms(1) == 500
        assert policy.get_delay_ms(2) == 500
        assert policy.get_delay_ms(3) == 500

    def test_exponential_backoff(self):
        """Test exponential backoff delays."""
        policy = RetryPolicy(
            initial_delay_ms=1000,
            exponential_backoff=True,
            backoff_multiplier=2.0,
        )

        assert policy.get_delay_ms(1) == 1000
        assert policy.get_delay_ms(2) == 2000
        assert policy.get_delay_ms(3) == 4000

    def test_max_delay_cap(self):
        """Test delay is capped at max."""
        policy = RetryPolicy(
            initial_delay_ms=10000,
            max_delay_ms=15000,
            exponential_backoff=True,
            backoff_multiplier=2.0,
        )

        # Third attempt would be 40000 without cap
        assert policy.get_delay_ms(3) == 15000

    def test_should_retry_on_retryable_error(self):
        """Test retry decision for retryable errors."""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry("rate_limit", 1) is True
        assert policy.should_retry("timeout", 2) is True
        assert policy.should_retry("connection_error", 1) is True
        assert policy.should_retry("server_error", 1) is True

    def test_should_not_retry_on_max_attempts(self):
        """Test no retry after max attempts."""
        policy = RetryPolicy(max_retries=3)

        assert policy.should_retry("rate_limit", 3) is False
        assert policy.should_retry("timeout", 4) is False

    def test_should_not_retry_unknown_errors(self):
        """Test no retry for unknown error types."""
        policy = RetryPolicy()

        assert policy.should_retry("authentication_error", 1) is False
        assert policy.should_retry("invalid_request", 1) is False

    def test_global_default_policy(self):
        """Test the global default retry policy."""
        assert DEFAULT_RETRY_POLICY.max_retries == 3
        assert DEFAULT_RETRY_POLICY.exponential_backoff is True


class TestResilientExecutor:
    """Tests for ResilientExecutor integration."""

    @pytest.fixture
    def executor(self):
        """Create a resilient executor with default policies."""
        return ResilientExecutor()

    @pytest.mark.asyncio
    async def test_successful_primary_call(self, executor):
        """Test successful call to primary provider."""
        mock_fn = AsyncMock(return_value="success")

        result, metadata = await executor.execute_with_fallback(mock_fn, "test prompt")

        assert result == "success"
        assert metadata["fallback_used"] is False
        assert metadata["attempts"] == 1

    @pytest.mark.asyncio
    async def test_fallback_on_primary_failure(self, executor):
        """Test fallback when primary fails."""
        call_count = 0

        async def failing_then_success(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if kwargs.get("provider") == "anthropic":
                raise Exception("Primary failed")
            return "fallback success"

        result, metadata = await executor.execute_with_fallback(failing_then_success)

        assert result == "fallback success"
        assert metadata["fallback_used"] is True
        assert metadata["final_provider"] != "anthropic"

    @pytest.mark.asyncio
    async def test_circuit_breaker_skip(self, executor):
        """Test that open circuits are skipped."""
        # Open the circuit for anthropic:capable (the primary tier)
        # CircuitBreaker now tracks per provider:tier combination
        executor.circuit_breaker.record_failure("anthropic", "capable")
        executor.circuit_breaker.record_failure("anthropic", "capable")
        executor.circuit_breaker.record_failure("anthropic", "capable")
        executor.circuit_breaker.record_failure("anthropic", "capable")
        executor.circuit_breaker.record_failure("anthropic", "capable")

        mock_fn = AsyncMock(return_value="success")

        result, metadata = await executor.execute_with_fallback(mock_fn)

        # Should have skipped anthropic:capable
        assert any(
            step.get("skipped") and step.get("reason") == "circuit_breaker_open"
            for step in metadata.get("fallback_chain", [])
        )

    @pytest.mark.asyncio
    async def test_all_fallbacks_exhausted(self, executor):
        """Test error when all fallbacks fail."""

        async def always_fail(*args, **kwargs):
            raise Exception("Always fails")

        with pytest.raises(Exception) as exc_info:
            await executor.execute_with_fallback(always_fail)

        assert "All fallback options exhausted" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test retry behavior on transient errors."""
        executor = ResilientExecutor(
            retry_policy=RetryPolicy(max_retries=2, initial_delay_ms=10),
        )

        attempt_count = 0

        async def fail_then_succeed(*args, **kwargs):
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 2:
                raise Exception("rate limit exceeded")
            return "success after retry"

        result, metadata = await executor.execute_with_fallback(fail_then_succeed)

        assert result == "success after retry"
        assert attempt_count == 2

    def test_error_classification(self, executor):
        """Test error type classification."""
        assert executor._classify_error(Exception("rate limit exceeded")) == "rate_limit"
        assert executor._classify_error(Exception("request timeout")) == "timeout"
        assert executor._classify_error(Exception("connection refused")) == "connection_error"
        assert executor._classify_error(Exception("500 internal error")) == "server_error"
        assert executor._classify_error(Exception("unknown issue")) == "unknown"

    @pytest.mark.asyncio
    async def test_metadata_tracking(self, executor):
        """Test that metadata is properly tracked."""
        mock_fn = AsyncMock(return_value="result")

        result, metadata = await executor.execute_with_fallback(mock_fn)

        assert "original_provider" in metadata
        assert "final_provider" in metadata
        assert "final_tier" in metadata
        assert "attempts" in metadata
        assert metadata["attempts"] >= 1
