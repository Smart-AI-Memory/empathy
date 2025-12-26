"""
EmpathyLLM Executor Implementation

Default LLMExecutor implementation that wraps EmpathyLLM for use
in workflows with automatic model routing and cost tracking.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from .executor import ExecutionContext, LLMResponse
from .registry import get_model
from .tasks import get_tier_for_task
from .telemetry import LLMCallRecord, TelemetryStore

logger = logging.getLogger(__name__)


class EmpathyLLMExecutor:
    """
    Default executor wrapping EmpathyLLM with routing.

    This executor provides a unified interface for workflows to call LLMs
    with automatic tier-based model routing and cost tracking.

    Example:
        >>> executor = EmpathyLLMExecutor(provider="anthropic")
        >>> response = await executor.run(
        ...     task_type="summarize",
        ...     prompt="Summarize this document...",
        ... )
        >>> print(f"Model used: {response.model_used}")
        >>> print(f"Cost: ${response.cost:.4f}")
    """

    def __init__(
        self,
        empathy_llm: Any | None = None,
        provider: str = "anthropic",
        api_key: str | None = None,
        telemetry_store: TelemetryStore | None = None,
        **llm_kwargs: Any,
    ):
        """
        Initialize the EmpathyLLM executor.

        Args:
            empathy_llm: Optional pre-configured EmpathyLLM instance.
            provider: LLM provider (anthropic, openai, ollama).
            api_key: Optional API key for the provider.
            telemetry_store: Optional telemetry store for recording calls.
            **llm_kwargs: Additional arguments for EmpathyLLM.
        """
        self._provider = provider
        self._api_key = api_key
        self._llm_kwargs = llm_kwargs
        self._llm = empathy_llm
        self._telemetry = telemetry_store

    def _get_llm(self) -> Any:
        """Lazy initialization of EmpathyLLM."""
        if self._llm is None:
            try:
                from empathy_llm_toolkit import EmpathyLLM

                kwargs = {
                    "provider": self._provider,
                    "enable_model_routing": True,
                    **self._llm_kwargs,
                }
                if self._api_key:
                    kwargs["api_key"] = self._api_key

                self._llm = EmpathyLLM(**kwargs)
            except ImportError as e:
                raise ImportError(
                    "empathy_llm_toolkit is required for EmpathyLLMExecutor. "
                    "Install it or use MockLLMExecutor for testing."
                ) from e
        return self._llm

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
            task_type: Type of task for routing (e.g., "summarize", "fix_bug").
            prompt: The user prompt to send.
            system: Optional system prompt (passed as context).
            context: Optional execution context for tracking.
            **kwargs: Additional arguments for EmpathyLLM.interact().

        Returns:
            LLMResponse with content, tokens, cost, and metadata.
        """
        llm = self._get_llm()
        start_time = time.time()
        call_id = str(uuid.uuid4())

        # Use task_type from context if provided
        effective_task_type = task_type
        if context and context.task_type:
            effective_task_type = context.task_type

        # Build context dict
        full_context: dict[str, Any] = kwargs.pop("existing_context", {})
        if system:
            full_context["system_prompt"] = system
        if context:
            if context.workflow_name:
                full_context["workflow_name"] = context.workflow_name
            if context.step_name:
                full_context["step_name"] = context.step_name
            if context.session_id:
                full_context["session_id"] = context.session_id
            if context.metadata:
                full_context.update(context.metadata)

        # Determine user_id
        user_id = "workflow"
        if context and context.user_id:
            user_id = context.user_id

        # Use provider hint if provided
        provider = context.provider_hint if context and context.provider_hint else self._provider

        # Call EmpathyLLM with task_type routing
        result = await llm.interact(
            user_id=user_id,
            user_input=prompt,
            context=full_context if full_context else None,
            task_type=effective_task_type,
            **kwargs,
        )

        # Calculate latency
        latency_ms = int((time.time() - start_time) * 1000)

        # Extract routing metadata
        metadata = result.get("metadata", {})
        tier = get_tier_for_task(effective_task_type)
        tier_str = tier.value if hasattr(tier, "value") else str(tier)

        # Get token counts
        tokens_input = metadata.get("tokens_used", 0)
        tokens_output = metadata.get("output_tokens", 0)

        # Get model info
        model_info = get_model(provider, tier_str)
        model_id = metadata.get("routed_model", metadata.get("model", ""))
        if not model_id and model_info:
            model_id = model_info.id

        # Calculate cost
        cost_estimate = 0.0
        if model_info:
            cost_estimate = (tokens_input / 1_000_000) * model_info.input_cost_per_million + (
                tokens_output / 1_000_000
            ) * model_info.output_cost_per_million

        # Build response
        response = LLMResponse(
            content=result.get("content", ""),
            model_id=model_id,
            provider=provider,
            tier=tier_str,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            cost_estimate=cost_estimate,
            latency_ms=latency_ms,
            metadata={
                "call_id": call_id,
                "level_used": result.get("level_used"),
                "level_description": result.get("level_description"),
                "proactive": result.get("proactive"),
                "task_type": effective_task_type,
                "model_routing_enabled": metadata.get("model_routing_enabled", False),
                "routed_tier": metadata.get("routed_tier"),
                **metadata,
            },
        )

        # Record telemetry (silent failure)
        if self._telemetry:
            try:
                record = LLMCallRecord(
                    call_id=call_id,
                    timestamp=datetime.now().isoformat(),
                    workflow_name=context.workflow_name if context else None,
                    step_name=context.step_name if context else None,
                    user_id=user_id,
                    session_id=context.session_id if context else None,
                    task_type=effective_task_type,
                    provider=provider,
                    tier=tier_str,
                    model_id=model_id,
                    input_tokens=tokens_input,
                    output_tokens=tokens_output,
                    estimated_cost=cost_estimate,
                    latency_ms=latency_ms,
                    success=True,
                )
                self._telemetry.log_call(record)
            except Exception as e:
                logger.warning("Failed to record telemetry: %s", e)

        return response

    def get_model_for_task(self, task_type: str) -> str:
        """
        Get the model that would be used for a task type.

        Args:
            task_type: Type of task to route

        Returns:
            Model identifier string
        """
        tier = get_tier_for_task(task_type)
        model_info = get_model(self._provider, tier.value)
        return model_info.id if model_info else ""

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
        tier = get_tier_for_task(task_type)
        model_info = get_model(self._provider, tier.value)

        if not model_info:
            return 0.0

        return (input_tokens / 1_000_000) * model_info.input_cost_per_million + (
            output_tokens / 1_000_000
        ) * model_info.output_cost_per_million
