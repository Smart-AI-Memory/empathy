"""Circuit Breaker Pattern Implementation

Prevents cascading failures by stopping calls to failing services.

States:
- CLOSED: Normal operation, calls pass through
- OPEN: Failures exceeded threshold, calls fail immediately
- HALF_OPEN: Testing if service recovered

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing fast
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""

    def __init__(self, name: str, reset_time: float):
        self.name = name
        self.reset_time = reset_time
        super().__init__(f"Circuit breaker '{name}' is open. Resets in {reset_time:.1f}s")


@dataclass
class CircuitBreaker:
    """Circuit breaker implementation.

    Tracks failures and opens circuit when threshold is exceeded.
    """

    name: str
    failure_threshold: int = 5
    reset_timeout: float = 60.0
    half_open_max_calls: int = 3
    excluded_exceptions: tuple[type[Exception], ...] = field(default_factory=tuple)

    # State tracking
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _success_count: int = field(default=0, init=False)
    _last_failure_time: float | None = field(default=None, init=False)
    _half_open_calls: int = field(default=0, init=False)

    @property
    def state(self) -> CircuitState:
        """Get current circuit state, checking for timeout."""
        if self._state == CircuitState.OPEN:
            if self._should_reset():
                self._transition_to_half_open()
        return self._state

    @property
    def is_open(self) -> bool:
        """Check if circuit is open (failing fast)."""
        return self.state == CircuitState.OPEN

    @property
    def is_closed(self) -> bool:
        """Check if circuit is closed (normal operation)."""
        return self.state == CircuitState.CLOSED

    def _should_reset(self) -> bool:
        """Check if enough time has passed to try recovery."""
        if self._last_failure_time is None:
            return True
        return time.time() - self._last_failure_time >= self.reset_timeout

    def _transition_to_half_open(self) -> None:
        """Move to half-open state to test recovery."""
        logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")
        self._state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._success_count = 0  # Reset success counter for recovery tracking

    def _transition_to_open(self) -> None:
        """Open the circuit after too many failures."""
        logger.warning(f"Circuit breaker '{self.name}' OPEN after {self._failure_count} failures")
        self._state = CircuitState.OPEN
        self._last_failure_time = time.time()

    def _transition_to_closed(self) -> None:
        """Close the circuit after successful recovery."""
        logger.info(f"Circuit breaker '{self.name}' CLOSED - service recovered")
        self._state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0

    def record_success(self) -> None:
        """Record a successful call."""
        # Use property to trigger OPEN -> HALF_OPEN transition if timeout elapsed
        current_state = self.state
        if current_state == CircuitState.HALF_OPEN:
            self._success_count += 1
            if self._success_count >= self.half_open_max_calls:
                self._transition_to_closed()
        elif current_state == CircuitState.CLOSED:
            # Reset failure count on success
            self._failure_count = 0

    def record_failure(self, exception: Exception) -> None:
        """Record a failed call."""
        # Don't count excluded exceptions
        if isinstance(exception, self.excluded_exceptions):
            return

        self._failure_count += 1
        self._last_failure_time = time.time()

        # Use property to trigger OPEN -> HALF_OPEN transition if timeout elapsed
        current_state = self.state
        if current_state == CircuitState.HALF_OPEN:
            # Any failure in half-open immediately opens
            self._transition_to_open()
        elif current_state == CircuitState.CLOSED:
            if self._failure_count >= self.failure_threshold:
                self._transition_to_open()

    def get_time_until_reset(self) -> float:
        """Get seconds until circuit might reset."""
        if self._last_failure_time is None:
            return 0.0
        elapsed = time.time() - self._last_failure_time
        return max(0.0, self.reset_timeout - elapsed)

    def reset(self) -> None:
        """Manually reset the circuit breaker."""
        self._transition_to_closed()

    def get_stats(self) -> dict[str, Any]:
        """Get circuit breaker statistics."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "time_until_reset": self.get_time_until_reset(),
        }


# Global registry of circuit breakers
_circuit_breakers: dict[str, CircuitBreaker] = {}


def get_circuit_breaker(name: str) -> CircuitBreaker | None:
    """Get a circuit breaker by name."""
    return _circuit_breakers.get(name)


def circuit_breaker(
    name: str | None = None,
    failure_threshold: int = 5,
    reset_timeout: float = 60.0,
    half_open_max_calls: int = 3,
    excluded_exceptions: tuple[type[Exception], ...] | None = None,
    fallback: Callable[..., T] | None = None,
) -> Callable:
    """Decorator to wrap a function with circuit breaker protection.

    Args:
        name: Circuit breaker name (defaults to function name)
        failure_threshold: Number of failures before opening
        reset_timeout: Seconds before attempting recovery
        half_open_max_calls: Successful calls needed to close
        excluded_exceptions: Exceptions that don't count as failures
        fallback: Function to call when circuit is open

    Example:
        @circuit_breaker(failure_threshold=3, reset_timeout=30)
        async def call_external_api():
            ...

        @circuit_breaker(fallback=lambda: {"status": "degraded"})
        async def get_status():
            ...

    """
    if excluded_exceptions is None:
        excluded_exceptions = ()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        cb_name = name or func.__name__

        # Create or get existing circuit breaker
        if cb_name not in _circuit_breakers:
            _circuit_breakers[cb_name] = CircuitBreaker(
                name=cb_name,
                failure_threshold=failure_threshold,
                reset_timeout=reset_timeout,
                half_open_max_calls=half_open_max_calls,
                excluded_exceptions=excluded_exceptions,
            )

        cb = _circuit_breakers[cb_name]

        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            if cb.is_open:
                if fallback:
                    logger.info(f"Circuit '{cb_name}' open, using fallback")
                    if asyncio.iscoroutinefunction(fallback):
                        fb_result: T = await fallback(*args, **kwargs)
                        return fb_result
                    return fallback(*args, **kwargs)
                raise CircuitOpenError(cb_name, cb.get_time_until_reset())

            try:
                result: T = await func(*args, **kwargs)  # type: ignore[misc]
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure(e)
                raise

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            if cb.is_open:
                if fallback:
                    logger.info(f"Circuit '{cb_name}' open, using fallback")
                    return fallback(*args, **kwargs)
                raise CircuitOpenError(cb_name, cb.get_time_until_reset())

            try:
                result = func(*args, **kwargs)
                cb.record_success()
                return result
            except Exception as e:
                cb.record_failure(e)
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper

    return decorator
