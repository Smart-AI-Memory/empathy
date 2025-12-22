"""
LLM Executor Protocol for Empathy Framework

Provides a unified interface for LLM execution that can be used by:
- src/empathy_os/workflows.BaseWorkflow
- Custom workflow implementations
- Testing and mocking

This protocol enables:
- Consistent model routing across workflows
- Unified cost tracking
- Easy swapping of LLM implementations

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable

from .registry import ModelTier


@dataclass
class LLMResponse:
    """
    Standardized response from an LLM execution.

    Contains the response content along with token counts, cost information,
    and metadata about the execution.
    """

    content: str
    input_tokens: int
    output_tokens: int
    model_used: str
    tier_used: ModelTier
    cost: float
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens


@dataclass
class ExecutionContext:
    """
    Context for an LLM execution.

    Provides additional information that may be used for routing,
    logging, or cost tracking.
    """

    workflow_name: str | None = None
    step_name: str | None = None
    user_id: str | None = None
    session_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LLMExecutor(Protocol):
    """
    Protocol for unified LLM execution across routing and workflows.

    Implementations of this protocol provide a consistent interface
    for calling LLMs with automatic model routing and cost tracking.

    Example:
        >>> executor = EmpathyLLMExecutor(provider="anthropic")
        >>> response = await executor.run(
        ...     task_type="summarize",
        ...     prompt="Summarize this document...",
        ...     context=ExecutionContext(workflow_name="doc-gen"),
        ... )
        >>> print(f"Cost: ${response.cost:.4f}")
    """

    async def run(
        self,
        task_type: str,
        prompt: str,
        system: str | None = None,
        context: ExecutionContext | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """
        Execute an LLM call with routing and cost tracking.

        Args:
            task_type: Type of task (e.g., "summarize", "fix_bug", "coordinate")
                      Used for model tier routing.
            prompt: The user prompt to send to the LLM.
            system: Optional system prompt.
            context: Optional execution context for tracking.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMResponse with content, tokens, cost, and metadata.
        """
        ...

    def get_model_for_task(self, task_type: str) -> str:
        """
        Get the model that would be used for a task type.

        Args:
            task_type: Type of task to route

        Returns:
            Model identifier string
        """
        ...

    def estimate_cost(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """
        Estimate cost for a task before execution.

        Args:
            task_type: Type of task
            input_tokens: Estimated input tokens
            output_tokens: Estimated output tokens

        Returns:
            Estimated cost in dollars
        """
        ...


class MockLLMExecutor:
    """
    Mock executor for testing.

    Returns configurable responses without making actual LLM calls.
    """

    def __init__(
        self,
        default_response: str = "Mock response",
        default_model: str = "mock-model",
    ):
        """
        Initialize mock executor.

        Args:
            default_response: Default content to return
            default_model: Default model name to report
        """
        self.default_response = default_response
        self.default_model = default_model
        self.call_history: list[dict[str, Any]] = []

    async def run(
        self,
        task_type: str,
        prompt: str,
        system: str | None = None,
        context: ExecutionContext | None = None,
        **kwargs: Any,
    ) -> LLMResponse:
        """Mock LLM execution."""
        from .tasks import get_tier_for_task

        tier = get_tier_for_task(task_type)

        # Record the call
        self.call_history.append(
            {
                "task_type": task_type,
                "prompt": prompt,
                "system": system,
                "context": context,
                "kwargs": kwargs,
            }
        )

        return LLMResponse(
            content=self.default_response,
            input_tokens=len(prompt.split()) * 4,  # Rough estimate
            output_tokens=len(self.default_response.split()) * 4,
            model_used=self.default_model,
            tier_used=tier,
            cost=0.0,
            metadata={"mock": True, "task_type": task_type},
        )

    def get_model_for_task(self, task_type: str) -> str:
        """Return mock model."""
        return self.default_model

    def estimate_cost(
        self,
        task_type: str,
        input_tokens: int,
        output_tokens: int,
    ) -> float:
        """Return zero cost for mock."""
        return 0.0
