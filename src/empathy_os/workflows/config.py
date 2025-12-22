"""
Workflow Configuration

Provides flexible configuration for workflow model selection:
- YAML/JSON config file support
- Environment variable overrides
- Per-workflow provider and model customization
- Easy extension for new models/providers

Configuration priority (highest to lowest):
1. Constructor arguments
2. Environment variables (EMPATHY_WORKFLOW_PROVIDER, etc.)
3. Config file (.empathy/workflows.yaml)
4. Built-in defaults

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

# Try to import yaml, fall back gracefully
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class ModelTier(Enum):
    """Model tier for cost optimization."""

    CHEAP = "cheap"
    CAPABLE = "capable"
    PREMIUM = "premium"


class ModelProvider(Enum):
    """Supported model providers."""

    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"
    CUSTOM = "custom"


@dataclass
class ModelConfig:
    """Configuration for a specific model."""

    name: str
    provider: str
    tier: str
    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_tools: bool = True


@dataclass
class WorkflowConfig:
    """Configuration for workflow model selection."""

    # Default provider for all workflows
    default_provider: str = "anthropic"

    # Per-workflow provider overrides
    workflow_providers: dict[str, str] = field(default_factory=dict)

    # Custom model mappings (provider -> tier -> model)
    custom_models: dict[str, dict[str, str]] = field(default_factory=dict)

    # Model pricing overrides
    pricing_overrides: dict[str, dict[str, float]] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: str | Path | None = None) -> "WorkflowConfig":
        """
        Load workflow configuration from file and environment.

        Args:
            config_path: Optional path to config file. If None, searches:
                1. .empathy/workflows.yaml
                2. .empathy/workflows.json
                3. empathy.config.yaml (workflows section)

        Returns:
            WorkflowConfig instance
        """
        config_data: dict[str, Any] = {}

        # Search for config file
        if config_path is None:
            search_paths = [
                Path(".empathy/workflows.yaml"),
                Path(".empathy/workflows.yml"),
                Path(".empathy/workflows.json"),
            ]
            for path in search_paths:
                if path.exists():
                    config_path = path
                    break

        # Load from file if found
        if config_path is not None:
            config_path = Path(config_path)
            if config_path.exists():
                config_data = cls._load_file(config_path)

        # Apply environment variable overrides
        config_data = cls._apply_env_overrides(config_data)

        return cls(
            default_provider=config_data.get("default_provider", "anthropic"),
            workflow_providers=config_data.get("workflow_providers", {}),
            custom_models=config_data.get("custom_models", {}),
            pricing_overrides=config_data.get("pricing_overrides", {}),
        )

    @staticmethod
    def _load_file(path: Path) -> dict[str, Any]:
        """Load config from YAML or JSON file."""
        content = path.read_text()

        if path.suffix in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML required for YAML config. Install: pip install pyyaml")
            data = yaml.safe_load(content)
        else:
            data = json.loads(content)

        # Handle nested 'workflows' key from empathy.config.yaml
        if "workflows" in data:
            return data["workflows"]
        return data

    @staticmethod
    def _apply_env_overrides(config: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides."""
        # Ensure nested dicts exist (YAML may load them as None)
        if config.get("workflow_providers") is None:
            config["workflow_providers"] = {}
        if config.get("custom_models") is None:
            config["custom_models"] = {}
        if config.get("pricing_overrides") is None:
            config["pricing_overrides"] = {}

        # EMPATHY_WORKFLOW_PROVIDER - default provider
        env_provider = os.environ.get("EMPATHY_WORKFLOW_PROVIDER")
        if env_provider:
            config["default_provider"] = env_provider.lower()

        # EMPATHY_WORKFLOW_<NAME>_PROVIDER - per-workflow provider
        for key, value in os.environ.items():
            if key.startswith("EMPATHY_WORKFLOW_") and key.endswith("_PROVIDER"):
                workflow_name = key[17:-9].lower().replace("_", "-")
                config["workflow_providers"][workflow_name] = value.lower()

        # EMPATHY_MODEL_<TIER> - tier model overrides
        for tier in ["CHEAP", "CAPABLE", "PREMIUM"]:
            env_model = os.environ.get(f"EMPATHY_MODEL_{tier}")
            if env_model:
                if "env" not in config["custom_models"]:
                    config["custom_models"]["env"] = {}
                config["custom_models"]["env"][tier.lower()] = env_model

        return config

    def get_provider_for_workflow(self, workflow_name: str) -> str:
        """Get the provider for a specific workflow."""
        return self.workflow_providers.get(workflow_name, self.default_provider)

    def get_model_for_tier(self, provider: str, tier: str) -> str | None:
        """Get custom model for a provider/tier, or None for default."""
        # Check for env overrides first
        if "env" in self.custom_models:
            if tier in self.custom_models["env"]:
                return self.custom_models["env"][tier]

        # Check provider-specific overrides
        if provider in self.custom_models:
            if tier in self.custom_models[provider]:
                return self.custom_models[provider][tier]

        return None

    def get_pricing(self, model: str) -> dict[str, float] | None:
        """Get custom pricing for a model, or None for default."""
        return self.pricing_overrides.get(model)

    def save(self, path: str | Path) -> None:
        """Save configuration to file."""
        path = Path(path)
        data = {
            "default_provider": self.default_provider,
            "workflow_providers": self.workflow_providers,
            "custom_models": self.custom_models,
            "pricing_overrides": self.pricing_overrides,
        }

        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix in (".yaml", ".yml"):
            if not YAML_AVAILABLE:
                raise ImportError("PyYAML required for YAML config")
            with open(path, "w") as f:
                yaml.dump(data, f, default_flow_style=False)
        else:
            with open(path, "w") as f:
                json.dump(data, f, indent=2)


# Default built-in model configurations
DEFAULT_MODELS: dict[str, dict[str, ModelConfig]] = {
    "anthropic": {
        "cheap": ModelConfig(
            name="claude-3-5-haiku-20241022",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=0.80,
            output_cost_per_million=4.00,
            max_tokens=8192,
        ),
        "capable": ModelConfig(
            name="claude-sonnet-4-20250514",
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.00,
            output_cost_per_million=15.00,
            max_tokens=8192,
            supports_vision=True,
        ),
        "premium": ModelConfig(
            name="claude-opus-4-5-20251101",
            provider="anthropic",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=75.00,
            max_tokens=8192,
            supports_vision=True,
        ),
    },
    "openai": {
        "cheap": ModelConfig(
            name="gpt-4o-mini",
            provider="openai",
            tier="cheap",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            max_tokens=4096,
        ),
        "capable": ModelConfig(
            name="gpt-4o",
            provider="openai",
            tier="capable",
            input_cost_per_million=2.50,
            output_cost_per_million=10.00,
            max_tokens=4096,
            supports_vision=True,
        ),
        "premium": ModelConfig(
            name="gpt-5.2",
            provider="openai",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=60.00,
            max_tokens=8192,
            supports_vision=True,
        ),
    },
    "ollama": {
        "cheap": ModelConfig(
            name="llama3.2:3b",
            provider="ollama",
            tier="cheap",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
        ),
        "capable": ModelConfig(
            name="llama3.2:latest",
            provider="ollama",
            tier="capable",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
        ),
        "premium": ModelConfig(
            name="llama3.2:latest",
            provider="ollama",
            tier="premium",
            input_cost_per_million=0.0,
            output_cost_per_million=0.0,
            max_tokens=4096,
        ),
    },
    # Hybrid: Mix best models from different providers
    "hybrid": {
        "cheap": ModelConfig(
            name="gpt-4o-mini",  # OpenAI - cheapest per token
            provider="openai",
            tier="cheap",
            input_cost_per_million=0.15,
            output_cost_per_million=0.60,
            max_tokens=4096,
        ),
        "capable": ModelConfig(
            name="claude-sonnet-4-20250514",  # Anthropic - best code/reasoning
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.00,
            output_cost_per_million=15.00,
            max_tokens=8192,
            supports_vision=True,
        ),
        "premium": ModelConfig(
            name="claude-opus-4-5-20251101",  # Anthropic - best overall
            provider="anthropic",
            tier="premium",
            input_cost_per_million=15.00,
            output_cost_per_million=75.00,
            max_tokens=8192,
            supports_vision=True,
        ),
    },
}


def get_model(provider: str, tier: str, config: WorkflowConfig | None = None) -> str:
    """
    Get the model name for a provider/tier combination.

    Args:
        provider: Model provider (anthropic, openai, ollama)
        tier: Model tier (cheap, capable, premium)
        config: Optional WorkflowConfig for custom overrides

    Returns:
        Model name string
    """
    # Check config overrides first
    if config:
        custom = config.get_model_for_tier(provider, tier)
        if custom:
            return custom

    # Fall back to defaults
    if provider in DEFAULT_MODELS and tier in DEFAULT_MODELS[provider]:
        return DEFAULT_MODELS[provider][tier].name

    # Ultimate fallback
    return DEFAULT_MODELS["anthropic"]["capable"].name


def create_example_config() -> str:
    """Generate an example configuration file content."""
    return """# Empathy Framework - Workflow Configuration
# Place this file at: .empathy/workflows.yaml

# =============================================================================
# PROVIDER SELECTION
# =============================================================================
# Choose from: anthropic, openai, ollama, hybrid
#
# - anthropic: All Claude models (Haiku → Sonnet → Opus 4.5)
# - openai:    All OpenAI models (GPT-4o-mini → GPT-4o → GPT-5.2)
# - ollama:    Local models (llama3.2:3b → llama3.2:latest)
# - hybrid:    Mix of best models from different providers:
#              cheap: gpt-4o-mini (cheapest)
#              capable: claude-sonnet-4 (best reasoning)
#              premium: claude-opus-4.5 (best overall)

default_provider: anthropic

# =============================================================================
# PER-WORKFLOW PROVIDER OVERRIDES
# =============================================================================
# Use different providers for specific workflows
workflow_providers:
  # research: hybrid    # Use hybrid for research
  # code-review: anthropic
  # doc-gen: openai

# =============================================================================
# CUSTOM MODEL MAPPINGS
# =============================================================================
# Override default models for specific provider/tier combinations
custom_models:
  anthropic:
    cheap: claude-3-5-haiku-20241022
    capable: claude-sonnet-4-20250514
    premium: claude-opus-4-5-20251101
  openai:
    cheap: gpt-4o-mini
    capable: gpt-4o
    premium: gpt-5.2
  ollama:
    cheap: llama3.2:3b
    capable: llama3.2:latest
    premium: mixtral:latest
  # Create your own hybrid mix:
  hybrid:
    cheap: gpt-4o-mini           # OpenAI - cheapest per token
    capable: claude-sonnet-4-20250514   # Anthropic - best code/reasoning
    premium: claude-opus-4-5-20251101   # Anthropic - best overall

# =============================================================================
# CUSTOM PRICING (per million tokens)
# =============================================================================
# Add pricing for models not in the default list
pricing_overrides:
  mixtral:latest:
    input: 0.0
    output: 0.0
  my-custom-model:
    input: 1.00
    output: 5.00

# =============================================================================
# ENVIRONMENT VARIABLE OVERRIDES
# =============================================================================
# EMPATHY_WORKFLOW_PROVIDER=hybrid             # Default provider
# EMPATHY_WORKFLOW_RESEARCH_PROVIDER=anthropic # Per-workflow
# EMPATHY_MODEL_CHEAP=gpt-4o-mini              # Tier model override
# EMPATHY_MODEL_CAPABLE=claude-sonnet-4-20250514
# EMPATHY_MODEL_PREMIUM=claude-opus-4-5-20251101
"""
