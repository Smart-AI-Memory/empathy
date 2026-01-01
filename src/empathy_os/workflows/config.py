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

Model configurations are sourced from the unified registry at
empathy_os.models.MODEL_REGISTRY.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Import from unified registry
from empathy_os.models import MODEL_REGISTRY, ModelInfo
from empathy_os.models.registry import ModelProvider, ModelTier

# Try to import yaml, fall back gracefully
try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# Re-export for backward compatibility
__all__ = [
    "ModelTier",
    "ModelProvider",
    "ModelConfig",
    "WorkflowConfig",
    "DEFAULT_MODELS",
    "get_model",
]


@dataclass
class ModelConfig:
    """
    Configuration for a specific model.

    Note: This class is kept for backward compatibility. New code should
    use empathy_os.models.ModelInfo from the unified registry.
    """

    name: str
    provider: str
    tier: str
    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_tools: bool = True

    @classmethod
    def from_model_info(cls, info: ModelInfo) -> "ModelConfig":
        """Create ModelConfig from unified ModelInfo."""
        return cls(
            name=info.id,
            provider=info.provider,
            tier=info.tier,
            input_cost_per_million=info.input_cost_per_million,
            output_cost_per_million=info.output_cost_per_million,
            max_tokens=info.max_tokens,
            supports_vision=info.supports_vision,
            supports_tools=info.supports_tools,
        )


@dataclass
class WorkflowConfig:
    """Configuration for workflow model selection and XML prompts."""

    # Default provider for all workflows
    default_provider: str = "anthropic"

    # Per-workflow provider overrides
    workflow_providers: dict[str, str] = field(default_factory=dict)

    # Custom model mappings (provider -> tier -> model)
    custom_models: dict[str, dict[str, str]] = field(default_factory=dict)

    # Model pricing overrides
    pricing_overrides: dict[str, dict[str, float]] = field(default_factory=dict)

    # XML prompt configuration - global defaults
    xml_prompt_defaults: dict[str, Any] = field(default_factory=dict)

    # Per-workflow XML prompt configuration overrides
    workflow_xml_configs: dict[str, dict[str, Any]] = field(default_factory=dict)

    # ==========================================================================
    # Compliance and Feature Flags
    # ==========================================================================

    # Compliance mode: "standard" (default) or "hipaa" (healthcare)
    # - standard: PII scrubbing disabled, test-gen disabled
    # - hipaa: PII scrubbing enabled, test-gen enabled, stricter auditing
    compliance_mode: str = "standard"

    # Explicitly enabled workflows (added to defaults)
    # Use this to opt-in to workflows like "test-gen"
    enabled_workflows: list[str] = field(default_factory=list)

    # Explicitly disabled workflows (removed from defaults)
    disabled_workflows: list[str] = field(default_factory=list)

    # PII scrubbing - auto-enabled in hipaa mode, opt-in otherwise
    pii_scrubbing_enabled: bool | None = None  # None = use compliance_mode default

    # Audit logging level - "standard", "enhanced", or "hipaa"
    audit_level: str = "standard"

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
                Path("empathy.config.yml"),  # Main config file
                Path("empathy.config.yaml"),
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
            xml_prompt_defaults=config_data.get("xml_prompt_defaults", {}),
            workflow_xml_configs=config_data.get("workflow_xml_configs", {}),
            # Compliance and feature flags
            compliance_mode=config_data.get("compliance_mode", "standard"),
            enabled_workflows=config_data.get("enabled_workflows", []),
            disabled_workflows=config_data.get("disabled_workflows", []),
            pii_scrubbing_enabled=config_data.get("pii_scrubbing_enabled"),
            audit_level=config_data.get("audit_level", "standard"),
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

        result: dict[str, Any] = {}

        # Handle root-level provider from empathy.config.yml
        if "provider" in data:
            result["default_provider"] = data["provider"]

        # Handle model_preferences as custom_models
        if "model_preferences" in data:
            provider = data.get("provider", "anthropic")
            result["custom_models"] = {provider: data["model_preferences"]}

        # Handle nested 'workflows' key from empathy.config.yaml
        if "workflows" in data and isinstance(data["workflows"], dict):
            result.update(data["workflows"])
        elif "workflows" not in data and "provider" not in data:
            # Legacy format: entire file is workflow config
            result = dict(data)

        return result

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

    def get_xml_config_for_workflow(self, workflow_name: str) -> dict[str, Any]:
        """
        Get XML prompt configuration for a specific workflow.

        Merges global defaults with workflow-specific overrides.

        Args:
            workflow_name: The workflow name (e.g., "security-audit").

        Returns:
            Dictionary with XML prompt configuration.
        """
        # Start with defaults
        config = dict(self.xml_prompt_defaults)

        # Apply workflow-specific overrides
        if workflow_name in self.workflow_xml_configs:
            config.update(self.workflow_xml_configs[workflow_name])

        return config

    def is_xml_enabled_for_workflow(self, workflow_name: str) -> bool:
        """
        Check if XML prompts are enabled for a workflow.

        Args:
            workflow_name: The workflow name.

        Returns:
            True if XML prompts are enabled.
        """
        config = self.get_xml_config_for_workflow(workflow_name)
        return bool(config.get("enabled", False))

    # ==========================================================================
    # Compliance and Feature Flag Methods
    # ==========================================================================

    def is_hipaa_mode(self) -> bool:
        """Check if HIPAA compliance mode is enabled."""
        return self.compliance_mode.lower() == "hipaa"

    def is_pii_scrubbing_enabled(self) -> bool:
        """
        Check if PII scrubbing is enabled.

        Returns True if:
        - Explicitly enabled via pii_scrubbing_enabled=True
        - OR compliance_mode is "hipaa" (and not explicitly disabled)

        Returns:
            True if PII scrubbing should be active
        """
        # Explicit setting takes precedence
        if self.pii_scrubbing_enabled is not None:
            return self.pii_scrubbing_enabled

        # Default based on compliance mode
        return self.is_hipaa_mode()

    def is_workflow_enabled(self, workflow_name: str) -> bool | None:
        """
        Check if a specific workflow is enabled.

        Args:
            workflow_name: Name of the workflow (e.g., "test-gen")

        Returns:
            True if workflow is enabled, False if disabled, None for default behavior
        """
        # Explicitly disabled takes precedence
        if workflow_name in self.disabled_workflows:
            return False

        # Explicitly enabled
        if workflow_name in self.enabled_workflows:
            return True

        # HIPAA mode enables healthcare-specific workflows
        if self.is_hipaa_mode():
            hipaa_workflows = {"test-gen"}  # Workflows auto-enabled in HIPAA mode
            if workflow_name in hipaa_workflows:
                return True

        # Default: workflow must be in standard registry (handled by __init__.py)
        return None  # None means "use default registry behavior"

    def get_effective_audit_level(self) -> str:
        """
        Get the effective audit level based on compliance mode.

        Returns:
            Audit level string: "standard", "enhanced", or "hipaa"
        """
        # Explicit setting takes precedence
        if self.audit_level != "standard":
            return self.audit_level

        # HIPAA mode defaults to hipaa audit level
        if self.is_hipaa_mode():
            return "hipaa"

        return "standard"

    def save(self, path: str | Path) -> None:
        """Save configuration to file."""
        path = Path(path)
        data = {
            "default_provider": self.default_provider,
            "workflow_providers": self.workflow_providers,
            "custom_models": self.custom_models,
            "pricing_overrides": self.pricing_overrides,
            "xml_prompt_defaults": self.xml_prompt_defaults,
            "workflow_xml_configs": self.workflow_xml_configs,
            # Compliance and feature flags
            "compliance_mode": self.compliance_mode,
            "enabled_workflows": self.enabled_workflows,
            "disabled_workflows": self.disabled_workflows,
            "pii_scrubbing_enabled": self.pii_scrubbing_enabled,
            "audit_level": self.audit_level,
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


# =============================================================================
# DEFAULT_MODELS - Built from unified registry
# =============================================================================
# This is now populated from empathy_os.models.MODEL_REGISTRY for consistency
# across the framework.


def _build_default_models() -> dict[str, dict[str, ModelConfig]]:
    """Build DEFAULT_MODELS from the unified registry."""
    result: dict[str, dict[str, ModelConfig]] = {}
    for provider, tiers in MODEL_REGISTRY.items():
        result[provider] = {}
        for tier, info in tiers.items():
            result[provider][tier] = ModelConfig.from_model_info(info)
    return result


# Lazy initialization - built on first access
_default_models_cache: dict[str, dict[str, ModelConfig]] | None = None


def _get_default_models() -> dict[str, dict[str, ModelConfig]]:
    """Get DEFAULT_MODELS, building from registry if needed."""
    global _default_models_cache
    if _default_models_cache is None:
        _default_models_cache = _build_default_models()
    return _default_models_cache


# For backward compatibility, DEFAULT_MODELS is now a property-like access
# Users should access via get_default_models() or directly use MODEL_REGISTRY
DEFAULT_MODELS: dict[str, dict[str, ModelConfig]] = {}  # Populated below


def _ensure_default_models() -> None:
    """Ensure DEFAULT_MODELS is populated."""
    global DEFAULT_MODELS
    if not DEFAULT_MODELS:
        DEFAULT_MODELS.update(_get_default_models())


def get_model(provider: str, tier: str, config: WorkflowConfig | None = None) -> str:
    """
    Get the model name for a provider/tier combination.

    Args:
        provider: Model provider (anthropic, openai, ollama, hybrid)
        tier: Model tier (cheap, capable, premium)
        config: Optional WorkflowConfig for custom overrides

    Returns:
        Model name string
    """
    # Ensure DEFAULT_MODELS is populated from registry
    _ensure_default_models()

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
# - ollama:    Local models (llama3.2:3b → llama3.1:8b → llama3.1:70b)
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
    capable: llama3.1:8b
    premium: llama3.1:70b
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
# XML PROMPT CONFIGURATION
# =============================================================================
# Enable structured XML prompts for consistent LLM interactions.
# XML prompts improve parsing reliability for dashboards and automation.

# Global defaults for all workflows
xml_prompt_defaults:
  enabled: false          # Set to true to enable XML prompts globally
  schema_version: "1.0"   # XML schema version
  enforce_response_xml: false  # Require XML in responses
  fallback_on_parse_error: true  # Fall back to raw text if XML fails

# Per-workflow XML configuration (overrides defaults)
workflow_xml_configs:
  security-audit:
    enabled: true
    enforce_response_xml: true
    template_name: "security-audit"
  code-review:
    enabled: true
    enforce_response_xml: true
    template_name: "code-review"
  research:
    enabled: true
    enforce_response_xml: false  # More flexible for research
    template_name: "research"
    bug-predict:
        enabled: true
        enforce_response_xml: true
        template_name: "bug-analysis"
    perf-audit:
        enabled: true
        enforce_response_xml: true
        template_name: "perf-audit"
    test-gen:
        enabled: true
        enforce_response_xml: true
        template_name: "test-gen"
    doc-gen:
        enabled: true
        enforce_response_xml: true
        template_name: "doc-gen"
    release-prep:
        enabled: true
        enforce_response_xml: true
        template_name: "release-prep"
    dependency-check:
        enabled: true
        enforce_response_xml: true
        template_name: "dependency-check"
    refactor-plan:
        enabled: true
        enforce_response_xml: true
        template_name: "refactor-plan"

# =============================================================================
# ENVIRONMENT VARIABLE OVERRIDES
# =============================================================================
# EMPATHY_WORKFLOW_PROVIDER=hybrid             # Default provider
# EMPATHY_WORKFLOW_RESEARCH_PROVIDER=anthropic # Per-workflow
# EMPATHY_MODEL_CHEAP=gpt-4o-mini              # Tier model override
# EMPATHY_MODEL_CAPABLE=claude-sonnet-4-20250514
# EMPATHY_MODEL_PREMIUM=claude-opus-4-5-20251101
"""
