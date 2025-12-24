"""
Resilient Agent Wrapper

Applies production-ready resilience patterns (circuit breaker, retry, timeout,
fallback) to any agent created by the Agent Factory.

Usage:
    from empathy_llm_toolkit.agent_factory import AgentFactory
    from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent, ResilienceConfig

    factory = AgentFactory()
    agent = factory.create_agent(name="researcher", role="researcher")

    # Wrap with resilience
    resilient_agent = ResilientAgent(agent, ResilienceConfig(
        enable_circuit_breaker=True,
        failure_threshold=3,
        enable_retry=True,
        max_attempts=3
    ))

    result = await resilient_agent.invoke("Research AI trends")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import functools
import logging
from dataclasses import dataclass, field
from typing import Any

from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent

logger = logging.getLogger(__name__)


@dataclass
class ResilienceConfig:
    """Configuration for resilience patterns."""

    # Circuit Breaker
    enable_circuit_breaker: bool = True
    failure_threshold: int = 3
    reset_timeout: float = 60.0
    half_open_max_calls: int = 3

    # Retry
    enable_retry: bool = True
    max_attempts: int = 2
    initial_delay: float = 1.0
    backoff_factor: float = 2.0
    max_delay: float = 30.0
    jitter: bool = True

    # Timeout
    enable_timeout: bool = True
    timeout_seconds: float = 30.0

    # Fallback
    enable_fallback: bool = False
    fallback_value: Any = field(
        default_factory=lambda: {
            "output": "Service temporarily unavailable",
            "metadata": {"fallback": True},
        }
    )

    @classmethod
    def from_agent_config(cls, config: AgentConfig) -> "ResilienceConfig":
        """Create ResilienceConfig from AgentConfig resilience fields."""
        return cls(
            enable_circuit_breaker=getattr(config, "resilience_enabled", False),
            failure_threshold=getattr(config, "circuit_breaker_threshold", 3),
            enable_retry=getattr(config, "resilience_enabled", False),
            max_attempts=getattr(config, "retry_max_attempts", 2),
            enable_timeout=getattr(config, "resilience_enabled", False),
            timeout_seconds=getattr(config, "timeout_seconds", 30.0),
        )


class ResilientAgent(BaseAgent):
    """
    Agent wrapper that applies resilience patterns.

    Wraps any BaseAgent implementation with:
    - Circuit breaker: Prevents cascading failures
    - Retry with backoff: Handles transient errors
    - Timeout: Prevents hanging operations
    - Fallback: Graceful degradation

    The wrapper preserves the underlying agent's interface while adding
    fault tolerance capabilities.
    """

    def __init__(self, agent: BaseAgent, config: ResilienceConfig | None = None):
        """
        Initialize resilient agent wrapper.

        Args:
            agent: The underlying agent to wrap
            config: Resilience configuration (uses defaults if not provided)
        """
        # Initialize with wrapped agent's config
        super().__init__(agent.config)
        self._wrapped = agent
        self._resilience_config = config or ResilienceConfig()
        self._circuit_breaker: Any = None
        self._setup_resilience()

    def _setup_resilience(self) -> None:
        """Set up resilience decorators based on config."""
        config = self._resilience_config

        # Set up circuit breaker if enabled
        if config.enable_circuit_breaker:
            try:
                from empathy_os.resilience import CircuitBreaker

                self._circuit_breaker = CircuitBreaker(
                    name=f"agent_{self.name}",
                    failure_threshold=config.failure_threshold,
                    reset_timeout=config.reset_timeout,
                    half_open_max_calls=config.half_open_max_calls,
                )
            except ImportError:
                logger.warning("empathy_os.resilience not available, circuit breaker disabled")

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """
        Invoke the agent with resilience patterns applied.

        Args:
            input_data: User input or structured data
            context: Optional context (previous results, shared state)

        Returns:
            Dict with at least {"output": str, "metadata": dict}

        Raises:
            CircuitOpenError: If circuit breaker is open
            asyncio.TimeoutError: If operation times out and no fallback
            Exception: If all retries exhausted and no fallback
        """
        config = self._resilience_config

        # Build the resilient call chain
        async def _call():
            return await self._wrapped.invoke(input_data, context)

        # Apply timeout
        if config.enable_timeout:
            _call = self._with_timeout(_call, config.timeout_seconds)

        # Apply retry
        if config.enable_retry:
            _call = self._with_retry(
                _call,
                config.max_attempts,
                config.initial_delay,
                config.backoff_factor,
                config.max_delay,
                config.jitter,
            )

        # Apply circuit breaker
        if config.enable_circuit_breaker and self._circuit_breaker:
            _call = self._with_circuit_breaker(_call)

        # Execute with optional fallback
        try:
            result = await _call()
            # Add resilience metadata
            if "metadata" in result:
                result["metadata"]["resilience"] = {
                    "circuit_breaker_enabled": config.enable_circuit_breaker,
                    "retry_enabled": config.enable_retry,
                    "timeout_enabled": config.enable_timeout,
                }
            return dict(result)
        except Exception as e:
            if config.enable_fallback:
                logger.warning(f"Agent {self.name} failed, using fallback: {e}")
                fallback = config.fallback_value
                if callable(fallback):
                    return dict(fallback(input_data, context, e))
                return dict(fallback) if isinstance(fallback, dict) else {"output": fallback}
            raise

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """
        Stream agent response with resilience patterns.

        Note: Streaming has limited resilience support (timeout only).
        Circuit breaker and retry work at the full response level.
        """
        config = self._resilience_config

        async def _stream():
            async for chunk in self._wrapped.stream(input_data, context):
                yield chunk

        # Apply timeout to entire stream
        if config.enable_timeout:
            try:
                async with asyncio.timeout(config.timeout_seconds):  # type: ignore[attr-defined]
                    async for chunk in _stream():
                        yield chunk
            except asyncio.TimeoutError:
                if config.enable_fallback:
                    yield {"output": "Stream timed out", "metadata": {"fallback": True}}
                else:
                    raise
        else:
            async for chunk in _stream():
                yield chunk

    def _with_timeout(self, func, timeout_seconds: float):
        """Wrap function with timeout."""

        @functools.wraps(func)
        async def wrapper():
            return await asyncio.wait_for(func(), timeout=timeout_seconds)

        return wrapper

    def _with_retry(
        self,
        func,
        max_attempts: int,
        initial_delay: float,
        backoff_factor: float,
        max_delay: float,
        jitter: bool,
    ):
        """Wrap function with retry logic."""
        import random

        @functools.wraps(func)
        async def wrapper():
            last_exception = None
            delay = initial_delay

            for attempt in range(max_attempts):
                try:
                    return await func()
                except asyncio.TimeoutError:
                    # Don't retry timeouts by default
                    raise
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        actual_delay = delay
                        if jitter:
                            actual_delay = delay * (0.5 + random.random())
                        actual_delay = min(actual_delay, max_delay)
                        logger.debug(
                            f"Agent {self.name} attempt {attempt + 1} failed, "
                            f"retrying in {actual_delay:.2f}s: {e}"
                        )
                        await asyncio.sleep(actual_delay)
                        delay = min(delay * backoff_factor, max_delay)

            raise last_exception

        return wrapper

    def _with_circuit_breaker(self, func):
        """Wrap function with circuit breaker."""

        @functools.wraps(func)
        async def wrapper():
            from empathy_os.resilience import CircuitOpenError

            # Check if circuit is open (failing fast)
            if self._circuit_breaker.is_open:
                reset_time = self._circuit_breaker.get_time_until_reset()
                raise CircuitOpenError(
                    name=f"agent_{self.name}",
                    reset_time=reset_time,
                )

            try:
                result = await func()
                self._circuit_breaker.record_success()
                return result
            except Exception as e:
                self._circuit_breaker.record_failure(e)
                raise

        return wrapper

    # Delegate other methods to wrapped agent
    def add_tool(self, tool: Any) -> None:
        """Add a tool to the wrapped agent."""
        self._wrapped.add_tool(tool)

    def get_conversation_history(self) -> list[dict]:
        """Get conversation history from wrapped agent."""
        return self._wrapped.get_conversation_history()

    def clear_history(self) -> None:
        """Clear conversation history in wrapped agent."""
        self._wrapped.clear_history()

    @property
    def model(self) -> str:
        """Get the model being used by wrapped agent."""
        return self._wrapped.model

    @property
    def circuit_state(self) -> str | None:
        """Get current circuit breaker state."""
        if self._circuit_breaker:
            return str(self._circuit_breaker.state.value)
        return None

    def reset_circuit_breaker(self) -> None:
        """Manually reset the circuit breaker."""
        if self._circuit_breaker:
            self._circuit_breaker.reset()
            logger.info(f"Circuit breaker reset for agent {self.name}")
