"""Fallback and Resilience Policies for Multi-Model Workflows

Provides abstractions for handling LLM failures gracefully:
- FallbackPolicy: Define fallback chains for providers/tiers
- CircuitBreaker: Temporarily disable failing providers
- RetryPolicy: Configure retry behavior

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, cast

from .registry import get_model


class FallbackStrategy(Enum):
    """Strategies for selecting fallback models."""

    # Try same tier with different provider
    SAME_TIER_DIFFERENT_PROVIDER = "same_tier_different_provider"

    # Try cheaper tier with same provider
    CHEAPER_TIER_SAME_PROVIDER = "cheaper_tier_same_provider"

    # Try different provider, any tier
    DIFFERENT_PROVIDER_ANY_TIER = "different_provider_any_tier"

    # Custom fallback chain
    CUSTOM = "custom"


@dataclass
class FallbackStep:
    """A single step in a fallback chain."""

    provider: str
    tier: str
    description: str = ""

    @property
    def model_id(self) -> str:
        """Get the model ID for this step."""
        model = get_model(self.provider, self.tier)
        return model.id if model else ""


@dataclass
class FallbackPolicy:
    """Policy for handling LLM failures with fallback chains.

    Example:
        >>> policy = FallbackPolicy(
        ...     primary_provider="anthropic",
        ...     primary_tier="capable",
        ...     strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
        ... )
        >>> chain = policy.get_fallback_chain()
        >>> # Returns: [("openai", "capable"), ("ollama", "capable")]

    """

    # Primary configuration
    primary_provider: str = "anthropic"
    primary_tier: str = "capable"

    # Fallback configuration
    strategy: FallbackStrategy = FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER
    custom_chain: list[FallbackStep] = field(default_factory=list)

    # Retry configuration
    max_retries: int = 2
    retry_delay_ms: int = 1000
    exponential_backoff: bool = True

    # Timeout configuration
    timeout_ms: int = 30000

    def get_fallback_chain(self) -> list[FallbackStep]:
        """Get the fallback chain based on strategy.

        Returns:
            List of FallbackStep in order of preference

        """
        if self.strategy == FallbackStrategy.CUSTOM:
            return self.custom_chain

        chain: list[FallbackStep] = []
        all_providers = ["anthropic", "openai", "ollama"]
        all_tiers = ["premium", "capable", "cheap"]

        if self.strategy == FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER:
            # Try same tier with other providers
            for provider in all_providers:
                if provider != self.primary_provider:
                    chain.append(
                        FallbackStep(
                            provider=provider,
                            tier=self.primary_tier,
                            description=f"Same tier ({self.primary_tier}) on {provider}",
                        ),
                    )

        elif self.strategy == FallbackStrategy.CHEAPER_TIER_SAME_PROVIDER:
            # Try cheaper tiers with same provider
            tier_index = all_tiers.index(self.primary_tier) if self.primary_tier in all_tiers else 1
            for tier in all_tiers[tier_index + 1 :]:
                chain.append(
                    FallbackStep(
                        provider=self.primary_provider,
                        tier=tier,
                        description=f"Cheaper tier ({tier}) on {self.primary_provider}",
                    ),
                )

        elif self.strategy == FallbackStrategy.DIFFERENT_PROVIDER_ANY_TIER:
            # Try other providers, preferring same tier then cheaper
            for provider in all_providers:
                if provider != self.primary_provider:
                    # Try same tier first
                    chain.append(
                        FallbackStep(
                            provider=provider,
                            tier=self.primary_tier,
                            description=f"{self.primary_tier} on {provider}",
                        ),
                    )
                    # Then cheaper tiers
                    tier_index = (
                        all_tiers.index(self.primary_tier) if self.primary_tier in all_tiers else 1
                    )
                    for tier in all_tiers[tier_index + 1 :]:
                        chain.append(
                            FallbackStep(
                                provider=provider,
                                tier=tier,
                                description=f"{tier} on {provider}",
                            ),
                        )

        return chain


@dataclass
class CircuitBreakerState:
    """State of a circuit breaker for a provider."""

    failure_count: int = 0
    last_failure: datetime | None = None
    is_open: bool = False
    opened_at: datetime | None = None


class CircuitBreaker:
    """Circuit breaker to temporarily disable failing providers.

    Prevents cascading failures by stopping calls to providers that
    are experiencing issues. Tracks state per provider:tier combination
    for fine-grained control (e.g., Opus rate-limited shouldn't block Haiku).

    Example:
        >>> breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
        >>> if breaker.is_available("anthropic", "capable"):
        ...     try:
        ...         response = call_llm(...)
        ...         breaker.record_success("anthropic", "capable")
        ...     except Exception as e:
        ...         breaker.record_failure("anthropic", "capable")

    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_seconds: int = 60,
        half_open_calls: int = 1,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout_seconds: Time before trying again
            half_open_calls: Calls to allow in half-open state

        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = timedelta(seconds=recovery_timeout_seconds)
        self.half_open_calls = half_open_calls
        self._states: dict[str, CircuitBreakerState] = {}

    def _get_key(self, provider: str, tier: str | None = None) -> str:
        """Get the state key for a provider:tier combination."""
        if tier:
            return f"{provider}:{tier}"
        return provider

    def _get_state(self, provider: str, tier: str | None = None) -> CircuitBreakerState:
        """Get or create state for a provider:tier combination."""
        key = self._get_key(provider, tier)
        if key not in self._states:
            self._states[key] = CircuitBreakerState()
        return self._states[key]

    def is_available(self, provider: str, tier: str | None = None) -> bool:
        """Check if a provider:tier is available.

        Args:
            provider: Provider to check
            tier: Optional tier (if None, checks provider-level)

        Returns:
            True if provider:tier can be called

        """
        state = self._get_state(provider, tier)

        if not state.is_open:
            return True

        # Check if recovery timeout has passed
        if state.opened_at:
            time_since_open = datetime.now() - state.opened_at
            if time_since_open >= self.recovery_timeout:
                # Half-open: allow limited calls
                return True

        return False

    def record_success(self, provider: str, tier: str | None = None) -> None:
        """Record a successful call.

        Args:
            provider: Provider that succeeded
            tier: Optional tier

        """
        state = self._get_state(provider, tier)

        # Reset on success
        state.failure_count = 0
        state.is_open = False
        state.opened_at = None

    def record_failure(self, provider: str, tier: str | None = None) -> None:
        """Record a failed call.

        Args:
            provider: Provider that failed
            tier: Optional tier

        """
        state = self._get_state(provider, tier)

        state.failure_count += 1
        state.last_failure = datetime.now()

        if state.failure_count >= self.failure_threshold:
            state.is_open = True
            state.opened_at = datetime.now()

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all tracked providers."""
        return {
            provider: {
                "failure_count": state.failure_count,
                "is_open": state.is_open,
                "last_failure": state.last_failure.isoformat() if state.last_failure else None,
                "opened_at": state.opened_at.isoformat() if state.opened_at else None,
            }
            for provider, state in self._states.items()
        }

    def reset(self, provider: str | None = None, tier: str | None = None) -> None:
        """Reset circuit breaker state.

        Args:
            provider: Provider to reset (all if None)
            tier: Tier to reset (provider-level if None)

        """
        if provider:
            key = self._get_key(provider, tier)
            if key in self._states:
                self._states[key] = CircuitBreakerState()
        else:
            self._states.clear()


@dataclass
class RetryPolicy:
    """Policy for retrying failed LLM calls.

    Configures how many times to retry and with what delays.
    """

    max_retries: int = 3
    initial_delay_ms: int = 1000
    max_delay_ms: int = 30000
    exponential_backoff: bool = True
    backoff_multiplier: float = 2.0
    retry_on_errors: list[str] = field(
        default_factory=lambda: [
            "rate_limit",
            "timeout",
            "server_error",
            "connection_error",
        ],
    )

    def get_delay_ms(self, attempt: int) -> int:
        """Get delay before retry attempt.

        Args:
            attempt: Current attempt number (1-indexed)

        Returns:
            Delay in milliseconds

        """
        if not self.exponential_backoff:
            return self.initial_delay_ms

        delay = self.initial_delay_ms * (self.backoff_multiplier ** (attempt - 1))
        return min(int(delay), self.max_delay_ms)

    def should_retry(self, error_type: str, attempt: int) -> bool:
        """Check if should retry for this error.

        Args:
            error_type: Type of error encountered
            attempt: Current attempt number

        Returns:
            True if should retry

        """
        if attempt >= self.max_retries:
            return False

        return error_type in self.retry_on_errors


class AllProvidersFailedError(Exception):
    """Raised when all fallback providers have failed."""

    def __init__(self, message: str, attempts: list[dict[str, Any]]):
        super().__init__(message)
        self.attempts = attempts


class ResilientExecutor:
    """Wrapper that adds resilience to LLM execution.

    Combines fallback policies, circuit breakers, and retry logic.
    Implements the LLMExecutor protocol by wrapping another executor.

    Example:
        >>> from empathy_os.models.empathy_executor import EmpathyLLMExecutor
        >>> base_executor = EmpathyLLMExecutor(provider="anthropic")
        >>> resilient = ResilientExecutor(executor=base_executor)
        >>> response = await resilient.run("summarize", "Summarize this...")

    """

    def __init__(
        self,
        executor: Any | None = None,
        fallback_policy: FallbackPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        retry_policy: RetryPolicy | None = None,
    ):
        """Initialize resilient executor.

        Args:
            executor: Inner LLMExecutor to wrap
            fallback_policy: Fallback configuration
            circuit_breaker: Circuit breaker instance
            retry_policy: Retry configuration

        """
        self._executor = executor
        self.fallback_policy = fallback_policy or FallbackPolicy()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.retry_policy = retry_policy or RetryPolicy()

    async def run(
        self,
        task_type: str,
        prompt: str,
        system: str | None = None,
        context: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        """Execute LLM call with retry and fallback support.

        Implements the LLMExecutor protocol. Uses per-call policies from
        context.metadata if provided.

        Args:
            task_type: Type of task for routing
            prompt: The user prompt
            system: Optional system prompt
            context: Optional ExecutionContext (can contain retry_policy, fallback_policy)
            **kwargs: Additional arguments

        Returns:
            LLMResponse from the wrapped executor

        """
        if self._executor is None:
            raise RuntimeError("ResilientExecutor requires an inner executor")

        # Allow per-call policy overrides via context.metadata
        retry_policy = self.retry_policy
        fallback_policy = self.fallback_policy

        if context and hasattr(context, "metadata"):
            if "retry_policy" in context.metadata:
                retry_policy = context.metadata["retry_policy"]
            if "fallback_policy" in context.metadata:
                fallback_policy = context.metadata["fallback_policy"]

        # Build execution chain: primary + fallbacks
        chain = [
            FallbackStep(
                provider=fallback_policy.primary_provider,
                tier=fallback_policy.primary_tier,
                description="Primary",
            ),
        ] + fallback_policy.get_fallback_chain()

        attempts: list[dict[str, Any]] = []
        last_error: Exception | None = None
        total_retries = 0  # Track total retry count across all attempts

        for step in chain:
            # Check circuit breaker (per provider:tier)
            if not self.circuit_breaker.is_available(step.provider, step.tier):
                attempts.append(
                    {
                        "provider": step.provider,
                        "tier": step.tier,
                        "skipped": True,
                        "reason": "circuit_breaker_open",
                        "circuit_breaker_state": "open",
                    },
                )
                continue

            # Try with retries
            for attempt_num in range(1, retry_policy.max_retries + 1):
                try:
                    # Update context with current provider/tier hints
                    if context and hasattr(context, "provider_hint"):
                        context.provider_hint = step.provider
                    if context and hasattr(context, "tier_hint"):
                        context.tier_hint = step.tier

                    response = await self._executor.run(
                        task_type=task_type,
                        prompt=prompt,
                        system=system,
                        context=context,
                        **kwargs,
                    )

                    # Success - record and return
                    self.circuit_breaker.record_success(step.provider, step.tier)

                    # Add resilience metadata to response
                    if hasattr(response, "metadata"):
                        response.metadata["fallback_used"] = step.description != "Primary"
                        response.metadata["attempts"] = attempts
                        response.metadata["retry_count"] = total_retries
                        response.metadata["circuit_breaker_state"] = "closed"
                        response.metadata["original_provider"] = fallback_policy.primary_provider
                        response.metadata["original_tier"] = fallback_policy.primary_tier
                        if step.description != "Primary":
                            response.metadata["fallback_chain"] = [
                                f"{a['provider']}:{a['tier']}" for a in attempts
                            ]

                    return response

                except Exception as e:
                    last_error = e
                    error_type = self._classify_error(e)
                    total_retries += 1  # Increment retry counter

                    if retry_policy.should_retry(error_type, attempt_num):
                        delay = retry_policy.get_delay_ms(attempt_num)
                        time.sleep(delay / 1000)
                        continue

                    # Record failure and move to next fallback
                    self.circuit_breaker.record_failure(step.provider, step.tier)
                    attempts.append(
                        {
                            "provider": step.provider,
                            "tier": step.tier,
                            "skipped": False,
                            "error": str(e),
                            "error_type": error_type,
                            "attempt": attempt_num,
                        },
                    )
                    break

        # All fallbacks exhausted
        raise AllProvidersFailedError(
            f"All fallback options exhausted. Last error: {last_error}",
            attempts=attempts,
        ) from last_error

    def get_model_for_task(self, task_type: str) -> str:
        """Delegate to inner executor."""
        if self._executor and hasattr(self._executor, "get_model_for_task"):
            result: str = cast("str", self._executor.get_model_for_task(task_type))
            return result
        return ""

    def estimate_cost(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Delegate to inner executor."""
        if self._executor and hasattr(self._executor, "estimate_cost"):
            result: float = cast(
                "float",
                self._executor.estimate_cost(task_type, input_tokens, output_tokens),
            )
            return result
        return 0.0

    async def execute_with_fallback(
        self,
        call_fn: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> tuple[Any, dict[str, Any]]:
        """Execute LLM call with fallback support (legacy API).

        Args:
            call_fn: Async function to call (takes provider, model as kwargs)
            *args: Positional arguments for call_fn
            **kwargs: Keyword arguments for call_fn

        Returns:
            Tuple of (result, metadata) where metadata includes fallback info

        """
        metadata: dict[str, Any] = {
            "fallback_used": False,
            "fallback_chain": [],
            "attempts": 0,
            "original_provider": self.fallback_policy.primary_provider,
            "original_model": None,
        }

        # Build execution chain: primary + fallbacks
        chain = [
            FallbackStep(
                provider=self.fallback_policy.primary_provider,
                tier=self.fallback_policy.primary_tier,
                description="Primary",
            ),
        ] + self.fallback_policy.get_fallback_chain()

        last_error: Exception | None = None

        for step in chain:
            # Check circuit breaker (per provider:tier)
            if not self.circuit_breaker.is_available(step.provider, step.tier):
                metadata["fallback_chain"].append(
                    {
                        "provider": step.provider,
                        "tier": step.tier,
                        "skipped": True,
                        "reason": "circuit_breaker_open",
                    },
                )
                continue

            # Try with retries
            for attempt in range(1, self.retry_policy.max_retries + 1):
                metadata["attempts"] += 1

                try:
                    result = await call_fn(
                        *args,
                        provider=step.provider,
                        model=step.model_id,
                        **kwargs,
                    )

                    # Success
                    self.circuit_breaker.record_success(step.provider, step.tier)

                    if step.description != "Primary":
                        metadata["fallback_used"] = True

                    metadata["final_provider"] = step.provider
                    metadata["final_tier"] = step.tier
                    metadata["final_model"] = step.model_id

                    return result, metadata

                except Exception as e:
                    last_error = e
                    error_type = self._classify_error(e)

                    if self.retry_policy.should_retry(error_type, attempt):
                        delay = self.retry_policy.get_delay_ms(attempt)
                        time.sleep(delay / 1000)
                        continue

                    # Record failure and move to next fallback
                    self.circuit_breaker.record_failure(step.provider, step.tier)
                    metadata["fallback_chain"].append(
                        {
                            "provider": step.provider,
                            "tier": step.tier,
                            "skipped": False,
                            "error": str(e),
                            "error_type": error_type,
                        },
                    )
                    break

        # All fallbacks exhausted
        raise AllProvidersFailedError(
            f"All fallback options exhausted. Last error: {last_error}",
            attempts=metadata["fallback_chain"],
        ) from last_error

    def _classify_error(self, error: Exception) -> str:
        """Classify an error for retry decisions."""
        error_str = str(error).lower()

        if "rate" in error_str or "limit" in error_str:
            return "rate_limit"
        if "timeout" in error_str:
            return "timeout"
        if "connection" in error_str:
            return "connection_error"
        if "500" in error_str or "502" in error_str or "503" in error_str:
            return "server_error"
        return "unknown"


# Default policies
DEFAULT_FALLBACK_POLICY = FallbackPolicy(
    primary_provider="anthropic",
    primary_tier="capable",
    strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
    max_retries=2,
)

DEFAULT_RETRY_POLICY = RetryPolicy(
    max_retries=3,
    initial_delay_ms=1000,
    exponential_backoff=True,
)
