"""
Timeout Pattern Implementation

Prevents operations from hanging indefinitely.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
import signal
from collections.abc import Callable
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class TimeoutError(Exception):
    """Raised when an operation times out."""

    def __init__(self, operation: str, timeout: float):
        self.operation = operation
        self.timeout = timeout
        super().__init__(f"Operation '{operation}' timed out after {timeout}s")


def timeout(
    seconds: float,
    error_message: str | None = None,
    fallback: Callable[..., T] | None = None,
) -> Callable:
    """
    Decorator to add timeout to a function.

    Args:
        seconds: Maximum execution time in seconds
        error_message: Custom error message
        fallback: Function to call on timeout

    Example:
        @timeout(30)
        async def slow_operation():
            ...

        @timeout(10, fallback=lambda: "default")
        async def get_data():
            ...
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                coro = func(*args, **kwargs)
                result: T = await asyncio.wait_for(coro, timeout=seconds)  # type: ignore[arg-type]
                return result
            except asyncio.TimeoutError:
                operation = error_message or func.__name__
                logger.warning(f"Timeout after {seconds}s: {operation}")

                if fallback:
                    logger.info(f"Using fallback for {func.__name__}")
                    if asyncio.iscoroutinefunction(fallback):
                        result = await fallback(*args, **kwargs)
                        return result
                    return fallback(*args, **kwargs)

                raise TimeoutError(operation, seconds)

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            # For sync functions, use signal-based timeout (Unix only)
            import platform

            if platform.system() == "Windows":
                # Windows doesn't support SIGALRM, just run without timeout
                logger.warning(
                    f"Timeout not supported on Windows for sync function {func.__name__}"
                )
                return func(*args, **kwargs)

            def timeout_handler(signum: int, frame: Any) -> None:
                raise TimeoutError(func.__name__, seconds)

            old_handler = signal.signal(signal.SIGALRM, timeout_handler)
            signal.setitimer(signal.ITIMER_REAL, seconds)

            try:
                result = func(*args, **kwargs)
                signal.setitimer(signal.ITIMER_REAL, 0)
                return result
            except TimeoutError:
                if fallback:
                    return fallback(*args, **kwargs)
                raise
            finally:
                signal.signal(signal.SIGALRM, old_handler)
                signal.setitimer(signal.ITIMER_REAL, 0)

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper

    return decorator


async def with_timeout(
    coro: Any,
    seconds: float,
    fallback_value: T | None = None,
) -> T:
    """
    Execute a coroutine with a timeout.

    Args:
        coro: Coroutine to execute
        seconds: Maximum execution time
        fallback_value: Value to return on timeout (raises if None)

    Returns:
        Result of coroutine or fallback value

    Example:
        result = await with_timeout(slow_api_call(), 30)
        result = await with_timeout(get_data(), 10, fallback_value={})
    """
    try:
        return await asyncio.wait_for(coro, timeout=seconds)
    except asyncio.TimeoutError:
        if fallback_value is not None:
            return fallback_value
        raise TimeoutError("coroutine", seconds)
