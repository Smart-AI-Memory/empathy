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


@dataclass
class LLMResponse:
    """
    Standardized response from an LLM execution.

    Contains the response content along with token counts, cost information,
    and metadata about the execution.

    Attributes:
        content: The LLM response text
        model_id: Model identifier (e.g., "claude-sonnet-4-20250514")
        provider: Provider name (e.g., "anthropic", "openai")
        tier: Model tier ("cheap", "capable", "premium")
        tokens_input: Number of input tokens used
        tokens_output: Number of output tokens generated
        cost_estimate: Estimated cost in USD
        latency_ms: Response time in milliseconds
        metadata: Additional response metadata
    """

    content: str
    model_id: str
    provider: str
    tier: str
    tokens_input: int = 0
    tokens_output: int = 0
    cost_estimate: float = 0.0
    latency_ms: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)

    # Backwards compatibility aliases
    @property
    def input_tokens(self) -> int:
        """Alias for tokens_input (backwards compatibility)."""
        return self.tokens_input

    @property
    def output_tokens(self) -> int:
        """Alias for tokens_output (backwards compatibility)."""
        return self.tokens_output

    @property
    def model_used(self) -> str:
        """Alias for model_id (backwards compatibility)."""
        return self.model_id

    @property
    def cost(self) -> float:
        """Alias for cost_estimate (backwards compatibility)."""
        return self.cost_estimate

    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.tokens_input + self.tokens_output


@dataclass
class ExecutionContext:
    """
    Context for an LLM execution.

    Provides additional information that may be used for routing,
    logging, or cost tracking.

    Attributes:
        user_id: User identifier for tracking
        workflow_name: Name of the workflow (e.g., "security-audit")
        step_name: Name of the current step (e.g., "scan")
        task_type: Task type for routing (e.g., "summarize", "fix_bug")
        provider_hint: Override default provider selection
        tier_hint: Override tier selection (cheap/capable/premium)
        timeout_seconds: Timeout for this execution
        session_id: Session identifier
        metadata: Additional context (can include retry_policy, fallback_policy)
    """

    user_id: str | None = None
    workflow_name: str | None = None
    step_name: str | None = None
    task_type: str | None = None
    provider_hint: str | None = None
    tier_hint: str | None = None
    timeout_seconds: int | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


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
            model_id=self.default_model,
            provider="mock",
            tier=tier.value if hasattr(tier, "value") else str(tier),
            tokens_input=len(prompt.split()) * 4,  # Rough estimate
            tokens_output=len(self.default_response.split()) * 4,
            cost_estimate=0.0,
            latency_ms=10,
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
