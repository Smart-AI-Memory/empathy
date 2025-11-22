"""
LLM Provider Adapters

Unified interface for different LLM providers (OpenAI, Anthropic, local models).

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""

    content: str
    model: str
    tokens_used: int
    finish_reason: str
    metadata: dict[str, Any]


class BaseLLMProvider(ABC):
    """
    Base class for all LLM providers.

    Provides unified interface regardless of backend.
    """

    def __init__(self, api_key: str | None = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs

    @abstractmethod
    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response from LLM.

        Args:
            messages: List of {"role": "user/assistant", "content": "..."}
            system_prompt: Optional system prompt
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response
            **kwargs: Provider-specific options

        Returns:
            LLMResponse with standardized format
        """
        pass

    @abstractmethod
    def get_model_info(self) -> dict[str, Any]:
        """Get information about the model being used"""
        pass

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.

        Rough approximation: ~4 chars per token
        """
        return len(text) // 4


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic (Claude) provider with enhanced features.

    Supports Claude 3 family models with advanced capabilities:
    - Extended context windows (200K tokens)
    - Prompt caching for faster repeated queries
    - Thinking mode for complex reasoning
    - Batch processing for cost optimization
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-5-20250929",
        use_prompt_caching: bool = True,
        use_thinking: bool = False,
        **kwargs,
    ):
        super().__init__(api_key, **kwargs)
        self.model = model
        self.use_prompt_caching = use_prompt_caching
        self.use_thinking = use_thinking

        # Validate API key is provided
        if not api_key or not api_key.strip():
            raise ValueError(
                "API key is required for Anthropic provider. "
                "Provide via api_key parameter or ANTHROPIC_API_KEY environment variable"
            )

        # Lazy import to avoid requiring anthropic if not used
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError as e:
            raise ImportError(
                "anthropic package required. Install with: pip install anthropic"
            ) from e

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """
        Generate response using Anthropic API with enhanced features.

        Claude-specific enhancements:
        - Prompt caching for repeated system prompts (90% cost reduction)
        - Extended context (200K tokens) for large codebase analysis
        - Thinking mode for complex reasoning tasks
        """

        # Build kwargs for Anthropic
        api_kwargs = {
            "model": self.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }

        # Enable prompt caching for system prompts (Claude-specific)
        if system_prompt and self.use_prompt_caching:
            api_kwargs["system"] = [
                {
                    "type": "text",
                    "text": system_prompt,
                    "cache_control": {"type": "ephemeral"},  # Cache for 5 minutes
                }
            ]
        elif system_prompt:
            api_kwargs["system"] = system_prompt

        # Enable extended thinking for complex tasks (Claude-specific)
        if self.use_thinking:
            api_kwargs["thinking"] = {
                "type": "enabled",
                "budget_tokens": 2000,  # Allow 2K tokens for reasoning
            }

        # Add any additional kwargs
        api_kwargs.update(kwargs)

        # Call Anthropic API
        response = self.client.messages.create(**api_kwargs)

        # Extract thinking content if present
        thinking_content = None
        response_content = ""

        for block in response.content:
            if hasattr(block, "type"):
                if block.type == "thinking":
                    thinking_content = block.thinking
                elif block.type == "text":
                    response_content = block.text
            else:
                response_content = block.text

        # Convert to standardized format
        metadata = {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens,
            "provider": "anthropic",
            "model_family": "claude-3",
        }

        # Add cache performance metrics if available
        if hasattr(response.usage, "cache_creation_input_tokens"):
            metadata["cache_creation_tokens"] = response.usage.cache_creation_input_tokens
            metadata["cache_read_tokens"] = response.usage.cache_read_input_tokens

        # Add thinking content if present
        if thinking_content:
            metadata["thinking"] = thinking_content

        return LLMResponse(
            content=response_content,
            model=response.model,
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            finish_reason=response.stop_reason,
            metadata=metadata,
        )

    async def analyze_large_codebase(
        self, codebase_files: list[dict[str, str]], analysis_prompt: str, **kwargs
    ) -> LLMResponse:
        """
        Analyze large codebases using Claude's 200K context window.

        Claude-specific feature: Can process entire repositories in one call.

        Args:
            codebase_files: List of {"path": "...", "content": "..."} dicts
            analysis_prompt: What to analyze for
            **kwargs: Additional generation parameters

        Returns:
            LLMResponse with analysis results
        """
        # Build context from all files
        file_context = "\n\n".join(
            [f"# File: {file['path']}\n{file['content']}" for file in codebase_files]
        )

        # Create system prompt with caching for file context
        system_parts = [
            {
                "type": "text",
                "text": "You are a code analysis expert using the Empathy Framework.",
            },
            {
                "type": "text",
                "text": f"Codebase files:\n\n{file_context}",
                "cache_control": {"type": "ephemeral"},  # Cache the codebase
            },
        ]

        messages = [{"role": "user", "content": analysis_prompt}]

        # Use extended max_tokens for comprehensive analysis
        return await self.generate(
            messages=messages,
            system_prompt=None,  # We'll pass it directly in api_kwargs
            max_tokens=kwargs.pop("max_tokens", 4096),
            **{**kwargs, "system": system_parts},
        )

    def get_model_info(self) -> dict[str, Any]:
        """Get Claude model information with extended context capabilities"""
        model_info = {
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "cost_per_1m_input": 15.00,
                "cost_per_1m_output": 75.00,
                "supports_prompt_caching": True,
                "supports_thinking": True,
                "ideal_for": "Complex reasoning, large codebases",
            },
            "claude-3-5-sonnet-20241022": {
                "max_tokens": 200000,
                "cost_per_1m_input": 3.00,
                "cost_per_1m_output": 15.00,
                "supports_prompt_caching": True,
                "supports_thinking": True,
                "ideal_for": "General development, balanced cost/performance",
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 200000,
                "cost_per_1m_input": 0.25,
                "cost_per_1m_output": 1.25,
                "supports_prompt_caching": True,
                "supports_thinking": False,
                "ideal_for": "Fast responses, simple tasks",
            },
        }

        return model_info.get(
            self.model,
            {
                "max_tokens": 200000,
                "cost_per_1m_input": 3.00,
                "cost_per_1m_output": 15.00,
                "supports_prompt_caching": True,
                "supports_thinking": True,
            },
        )


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider.

    Supports GPT-4, GPT-3.5, and other OpenAI models.
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-4-turbo-preview", **kwargs):
        super().__init__(api_key, **kwargs)
        self.model = model

        # Validate API key is provided
        if not api_key or not api_key.strip():
            raise ValueError(
                "API key is required for OpenAI provider. "
                "Provide via api_key parameter or OPENAI_API_KEY environment variable"
            )

        # Lazy import
        try:
            import openai

            self.client = openai.AsyncOpenAI(api_key=api_key)
        except ImportError as e:
            raise ImportError("openai package required. Install with: pip install openai") from e

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using OpenAI API"""

        # Add system prompt if provided
        if system_prompt:
            messages = [{"role": "system", "content": system_prompt}] + messages

        # Call OpenAI API
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Convert to standardized format
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            tokens_used=response.usage.total_tokens,
            finish_reason=response.choices[0].finish_reason,
            metadata={
                "input_tokens": response.usage.prompt_tokens,
                "output_tokens": response.usage.completion_tokens,
                "provider": "openai",
            },
        )

    def get_model_info(self) -> dict[str, Any]:
        """Get OpenAI model information"""
        model_info = {
            "gpt-4-turbo-preview": {
                "max_tokens": 128000,
                "cost_per_1m_input": 10.00,
                "cost_per_1m_output": 30.00,
            },
            "gpt-4": {"max_tokens": 8192, "cost_per_1m_input": 30.00, "cost_per_1m_output": 60.00},
            "gpt-3.5-turbo": {
                "max_tokens": 16385,
                "cost_per_1m_input": 0.50,
                "cost_per_1m_output": 1.50,
            },
        }

        return model_info.get(
            self.model,
            {"max_tokens": 128000, "cost_per_1m_input": 10.00, "cost_per_1m_output": 30.00},
        )


class LocalProvider(BaseLLMProvider):
    """
    Local model provider (Ollama, LM Studio, etc.).

    For running models locally.
    """

    def __init__(self, endpoint: str = "http://localhost:11434", model: str = "llama2", **kwargs):
        super().__init__(api_key=None, **kwargs)
        self.endpoint = endpoint
        self.model = model

    async def generate(
        self,
        messages: list[dict[str, str]],
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs,
    ) -> LLMResponse:
        """Generate response using local model"""
        import aiohttp

        # Format for Ollama-style API
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }

        if system_prompt:
            payload["system"] = system_prompt

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.endpoint}/api/chat", json=payload) as response:
                result = await response.json()

                return LLMResponse(
                    content=result.get("message", {}).get("content", ""),
                    model=self.model,
                    tokens_used=result.get("eval_count", 0) + result.get("prompt_eval_count", 0),
                    finish_reason="stop",
                    metadata={"provider": "local", "endpoint": self.endpoint},
                )

    def get_model_info(self) -> dict[str, Any]:
        """Get local model information"""
        return {
            "max_tokens": 4096,  # Depends on model
            "cost_per_1m_input": 0.0,  # Free (local)
            "cost_per_1m_output": 0.0,
            "endpoint": self.endpoint,
        }
