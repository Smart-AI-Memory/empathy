"""
Unified Model Registry - Single Source of Truth

This module provides a centralized model configuration that is consumed by:
- empathy_llm_toolkit.routing.ModelRouter (via compatibility properties)
- src/empathy_os/workflows.config.WorkflowConfig
- src/empathy_os.cost_tracker

Pricing is stored in per-million tokens (industry standard) with computed
properties for per-1k compatibility with legacy code.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class ModelTier(Enum):
    """
    Model tier classification for routing.

    CHEAP: Fast, low-cost models for simple tasks (~$0.15-1.00/M input)
    CAPABLE: Balanced models for most development work (~$2.50-3.00/M input)
    PREMIUM: Highest capability for complex reasoning (~$15.00/M input)
    """

    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"


class ModelProvider(Enum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    HYBRID = "hybrid"
    CUSTOM = "custom"


@dataclass(frozen=True)
class ModelInfo:
    """
    Unified model information - single source of truth.

    Pricing is stored in per-million tokens format. Use the cost_per_1k_*
    properties for compatibility with code expecting per-1k pricing.

    Attributes:
        id: Model identifier (e.g., "claude-3-5-haiku-20241022")
        provider: Provider name (e.g., "anthropic")
        tier: Tier level (e.g., "cheap")
        input_cost_per_million: Input token cost per million tokens
        output_cost_per_million: Output token cost per million tokens
        max_tokens: Maximum output tokens
        supports_vision: Whether model supports vision/images
        supports_tools: Whether model supports tool/function calling
    """

    id: str
    provider: str
    tier: str
    input_cost_per_million: float
    output_cost_per_million: float
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_tools: bool = True

    # Compatibility properties for toolkit (per-1k pricing)
    @property
    def model_id(self) -> str:
        """Alias for id - compatibility with ModelRouter.ModelConfig."""
        return self.id

    @property
    def name(self) -> str:
        """Alias for id - compatibility with WorkflowConfig.ModelConfig."""
        return self.id

    @property
    def cost_per_1k_input(self) -> float:
        """Input cost per 1k tokens - for ModelRouter compatibility."""
        return self.input_cost_per_million / 1000

    @property
    def cost_per_1k_output(self) -> float:
        """Output cost per 1k tokens - for ModelRouter compatibility."""
        return self.output_cost_per_million / 1000

    def to_router_config(self) -> dict[str, Any]:
        """Convert to ModelRouter.ModelConfig compatible dict."""
        return {
            "model_id": self.id,
            "cost_per_1k_input": self.cost_per_1k_input,
            "cost_per_1k_output": self.cost_per_1k_output,
            "max_tokens": self.max_tokens,
            "supports_tools": self.supports_tools,
        }

    def to_workflow_config(self) -> dict[str, Any]:
        """Convert to WorkflowConfig.ModelConfig compatible dict."""
        return {
            "name": self.id,
            "provider": self.provider,
            "tier": self.tier,
            "input_cost_per_million": self.input_cost_per_million,
            "output_cost_per_million": self.output_cost_per_million,
            "max_tokens": self.max_tokens,
            "supports_vision": self.supports_vision,
            "supports_tools": self.supports_tools,
        }

    def to_cost_tracker_pricing(self) -> dict[str, float]:
        """Convert to cost_tracker MODEL_PRICING format."""
        return {
            "input": self.input_cost_per_million,
            "output": self.output_cost_per_million,
        }


# =============================================================================
# MODEL REGISTRY - Single Source of Truth
# =============================================================================
# All model configurations are defined here. Other modules should import
# from this registry rather than defining their own model configs.

MODEL_REGISTRY: dict[str, dict[str, ModelInfo]] = {
    # -------------------------------------------------------------------------
    # Anthropic Claude Models
    # -------------------------------------------------------------------------
    "anthropic": {
        "cheap": ModelInfo(
            id="claude-3-5-haiku-20241022",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=0.80,
            output_cost_per_million=4.00,
            max_tokens=8192,
            supports_vision=False,
            supports_tools=True,
        ),
        "capable": ModelInfo(
            id="claude-sonnet-4-20250514",
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.00,
            output_cost_per_million=15.00,
            max_tokens=8192,
            supports_vision=True,
            supports_tools=True,
        ),
        "premium": ModelInfo(
            id="claude-opus-4-5-20251101",
            provider="anthropic",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=75.00,
            max_tokens=8192,
            supports_vision=True,
            supports_tools=True,
        ),
    },
    # -------------------------------------------------------------------------
    # OpenAI Models
    # -------------------------------------------------------------------------
    "openai": {
        "cheap": ModelInfo(
            id="gpt-4o-mini",
            provider="openai",
            tier="cheap",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            max_tokens=4096,
            supports_vision=False,
            supports_tools=True,
        ),
        "capable": ModelInfo(
            id="gpt-4o",
            provider="openai",
            tier="capable",
            input_cost_per_million=2.50,
            output_cost_per_million=10.00,
            max_tokens=4096,
            supports_vision=True,
            supports_tools=True,
        ),
        "premium": ModelInfo(
            id="o1",
            provider="openai",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=60.00,
            max_tokens=32768,
            supports_vision=False,
            supports_tools=False,  # o1 doesn't support tools yet
        ),
    },
    # -------------------------------------------------------------------------
    # Ollama (Local) Models - Zero cost
    # -------------------------------------------------------------------------
    "ollama": {
        "cheap": ModelInfo(
            id="llama3.2:3b",
            provider="ollama",
            tier="cheap",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
            supports_vision=False,
            supports_tools=True,
        ),
        "capable": ModelInfo(
            id="llama3.2:latest",
            provider="ollama",
            tier="capable",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
            supports_vision=False,
            supports_tools=True,
        ),
        "premium": ModelInfo(
            id="llama3.2:latest",
            provider="ollama",
            tier="premium",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
            supports_vision=False,
            supports_tools=True,
        ),
    },
    # -------------------------------------------------------------------------
    # Hybrid - Mix of best models from different providers
    # -------------------------------------------------------------------------
    "hybrid": {
        "cheap": ModelInfo(
            id="gpt-4o-mini",  # OpenAI - cheapest per token
            provider="openai",
            tier="cheap",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            max_tokens=4096,
            supports_vision=False,
            supports_tools=True,
        ),
        "capable": ModelInfo(
            id="claude-sonnet-4-20250514",  # Anthropic - best reasoning
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.00,
            output_cost_per_million=15.00,
            max_tokens=8192,
            supports_vision=True,
            supports_tools=True,
        ),
        "premium": ModelInfo(
            id="claude-opus-4-5-20251101",  # Anthropic - best overall
            provider="anthropic",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=75.00,
            max_tokens=8192,
            supports_vision=True,
            supports_tools=True,
        ),
    },
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def get_model(provider: str, tier: str) -> ModelInfo | None:
    """
    Get model info for a provider/tier combination.

    Args:
        provider: Provider name (anthropic, openai, ollama, hybrid)
        tier: Tier level (cheap, capable, premium)

    Returns:
        ModelInfo if found, None otherwise
    """
    provider_models = MODEL_REGISTRY.get(provider.lower())
    if provider_models is None:
        return None
    return provider_models.get(tier.lower())


def get_all_models() -> dict[str, dict[str, ModelInfo]]:
    """Get the complete model registry."""
    return MODEL_REGISTRY


def get_pricing_for_model(model_id: str) -> dict[str, float] | None:
    """
    Get pricing for a model by its ID.

    Args:
        model_id: Model identifier (e.g., "claude-3-5-haiku-20241022")

    Returns:
        Dict with 'input' and 'output' keys (per-million pricing), or None
    """
    for provider_models in MODEL_REGISTRY.values():
        for model_info in provider_models.values():
            if model_info.id == model_id:
                return model_info.to_cost_tracker_pricing()
    return None


def get_supported_providers() -> list[str]:
    """Get list of supported provider names."""
    return list(MODEL_REGISTRY.keys())


def get_tiers() -> list[str]:
    """Get list of available tiers."""
    return [tier.value for tier in ModelTier]


# =============================================================================
# TIER PRICING (for backward compatibility with cost_tracker)
# =============================================================================
# These are tier-level pricing aliases for when specific model isn't known

TIER_PRICING: dict[str, dict[str, float]] = {
    "cheap": {"input": 0.80, "output": 4.00},  # Haiku 3.5 pricing
    "capable": {"input": 3.00, "output": 15.00},  # Sonnet 4 pricing
    "premium": {"input": 15.00, "output": 75.00},  # Opus 4.5 pricing
}
