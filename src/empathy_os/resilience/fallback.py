"""
Fallback Pattern Implementation

Provides graceful degradation when primary operations fail.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


@dataclass
class Fallback:
    """
    Fallback chain for graceful degradation.

    Tries each function in order until one succeeds.
    """

    name: str
    functions: list[Callable] = field(default_factory=list)
    default_value: Any | None = None

    def add(self, func: Callable) -> "Fallback":
        """Add a fallback function to the chain."""
        self.functions.append(func)
        return self

    async def execute(self, *args: Any, **kwargs: Any) -> Any:
        """Execute fallback chain until success."""
        last_exception: Exception | None = None

        for i, func in enumerate(self.functions):
            try:
                logger.debug(f"Fallback '{self.name}': trying function {i + 1}")
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Fallback '{self.name}': function {i + 1} failed: {e}")
                continue

        # All functions failed
        if self.default_value is not None:
            logger.info(f"Fallback '{self.name}': using default value")
            return self.default_value

        if last_exception:
            raise last_exception
        raise RuntimeError(f"Fallback '{self.name}': no functions to execute")


def fallback(
    *fallback_funcs: Callable,
    default: Any | None = None,
    log_failures: bool = True,
) -> Callable:
    """
    Decorator to add fallback behavior to a function.

    Args:
        *fallback_funcs: Functions to try if primary fails
        default: Default value if all functions fail
        log_failures: Whether to log failed attempts

    Example:
        def get_from_cache():
            return cache.get("key")

        def get_from_db():
            return db.query("SELECT ...")

        @fallback(get_from_cache, default=None)
        async def get_data():
            return await api.fetch()
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> T:
            # Try primary function
            try:
                if asyncio.iscoroutinefunction(func):
                    result: T = await func(*args, **kwargs)
                    return result
                return func(*args, **kwargs)
            except Exception as e:
                if log_failures:
                    logger.warning(f"Primary function {func.__name__} failed: {e}")

            # Try fallback functions
            for fallback_func in fallback_funcs:
                try:
                    if asyncio.iscoroutinefunction(fallback_func):
                        result = await fallback_func(*args, **kwargs)
                        return result
                    return fallback_func(*args, **kwargs)  # type: ignore[no-any-return]
                except Exception as e:
                    if log_failures:
                        logger.warning(f"Fallback {fallback_func.__name__} failed: {e}")
                    continue

            # All failed, use default
            if default is not None:
                return default  # type: ignore[no-any-return]

            raise RuntimeError(f"All fallbacks failed for {func.__name__}")

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_failures:
                    logger.warning(f"Primary function {func.__name__} failed: {e}")

            for fallback_func in fallback_funcs:
                try:
                    return fallback_func(*args, **kwargs)  # type: ignore[no-any-return]
                except Exception as e:
                    if log_failures:
                        logger.warning(f"Fallback {fallback_func.__name__} failed: {e}")
                    continue

            if default is not None:
                return default  # type: ignore[no-any-return]

            raise RuntimeError(f"All fallbacks failed for {func.__name__}")

        if asyncio.iscoroutinefunction(func):
            return async_wrapper  # type: ignore[return-value]
        return sync_wrapper

    return decorator


def with_fallback(
    primary: Callable[..., T],
    fallbacks: list[Callable[..., T]],
    default: T | None = None,
) -> Callable[..., T]:
    """
    Create a function that tries primary then fallbacks.

    Args:
        primary: Primary function to try
        fallbacks: List of fallback functions
        default: Default value if all fail

    Returns:
        Wrapped function with fallback behavior

    Example:
        get_user = with_fallback(
            get_user_from_api,
            [get_user_from_cache, get_user_from_db],
            default={"id": "unknown"}
        )
        user = await get_user(user_id)
    """
    fb = Fallback(name=primary.__name__, default_value=default)
    fb.add(primary)
    for f in fallbacks:
        fb.add(f)

    async def wrapper(*args: Any, **kwargs: Any) -> T:
        result: T = await fb.execute(*args, **kwargs)
        return result

    return wrapper  # type: ignore[return-value]
