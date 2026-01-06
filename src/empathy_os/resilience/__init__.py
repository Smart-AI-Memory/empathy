"""Empathy Framework Resilience Module

Provides reliability patterns for fault-tolerant wizard operations.

Usage:
    from empathy_os.resilience import retry, circuit_breaker, timeout, fallback

    @retry(max_attempts=3, backoff_factor=2.0)
    async def call_llm(prompt: str) -> str:
        ...

    @circuit_breaker(failure_threshold=5, reset_timeout=60)
    async def external_api_call():
        ...

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .circuit_breaker import (
                              CircuitBreaker,
                              CircuitOpenError,
                              CircuitState,
                              circuit_breaker,
                              get_circuit_breaker,
)
from .fallback import Fallback, fallback, with_fallback
from .health import HealthCheck, HealthStatus, SystemHealth
from .retry import RetryConfig, retry, retry_with_backoff
from .timeout import TimeoutError as ResilienceTimeoutError
from .timeout import timeout, with_timeout

__all__ = [
    "CircuitBreaker",
    "CircuitOpenError",
    "CircuitState",
    "Fallback",
    # Health
    "HealthCheck",
    "HealthStatus",
    "ResilienceTimeoutError",
    "RetryConfig",
    "SystemHealth",
    # Circuit Breaker
    "circuit_breaker",
    # Fallback
    "fallback",
    "get_circuit_breaker",
    # Retry
    "retry",
    "retry_with_backoff",
    # Timeout
    "timeout",
    "with_fallback",
    "with_timeout",
]
