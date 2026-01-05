"""Configuration system for XML-enhanced prompting features.

Provides feature flags and settings for all 6 XML enhancement options:
1. Workflow migration settings
2. XML schema validation
3. Prompt metrics tracking
4. Context window optimization
5. Dynamic prompt adaptation
6. Multi-language support

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class XMLConfig:
    """XML prompting configuration.

    Controls XML-enhanced prompt behavior and validation.
    """

    use_xml_structure: bool = True  # Default to XML prompts
    validate_schemas: bool = False  # Feature flag for validation
    schema_dir: str = ".empathy/schemas"
    strict_validation: bool = False  # Fail on validation errors


@dataclass
class OptimizationConfig:
    """Context window optimization configuration.

    Controls prompt compression and token reduction strategies.
    """

    compression_level: str = "moderate"  # none, light, moderate, aggressive
    use_short_tags: bool = True
    strip_whitespace: bool = True
    cache_system_prompts: bool = True
    max_context_tokens: int = 8000


@dataclass
class AdaptiveConfig:
    """Adaptive prompting configuration.

    Controls dynamic model tier and compression selection based on task complexity.
    """

    enable_adaptation: bool = True
    model_tier_mapping: dict[str, str] = field(
        default_factory=lambda: {
            "simple": "gpt-3.5-turbo",
            "moderate": "gpt-4",
            "complex": "gpt-4",
            "very_complex": "gpt-4-turbo-preview",
        }
    )
    complexity_thresholds: dict[str, int] = field(
        default_factory=lambda: {
            "simple_tokens": 100,
            "moderate_tokens": 500,
            "complex_tokens": 2000,
        }
    )


@dataclass
class I18nConfig:
    """Internationalization configuration.

    Controls multi-language support for XML prompts.
    """

    default_language: str = "en"
    translate_tags: bool = False  # Keep tags in English by default
    translate_content: bool = True
    fallback_to_english: bool = True
    translation_dir: str = ".empathy/translations"


@dataclass
class MetricsConfig:
    """Metrics tracking configuration.

    Controls prompt performance metrics collection and storage.
    """

    enable_tracking: bool = True
    metrics_file: str = ".empathy/prompt_metrics.json"
    track_token_usage: bool = True
    track_latency: bool = True
    track_retries: bool = True
    track_parsing_success: bool = True


@dataclass
class EmpathyXMLConfig:
    """Main Empathy XML enhancement configuration.

    Combines all feature configurations with centralized management.

    Usage:
        config = EmpathyXMLConfig.load_from_file()
        if config.xml.use_xml_structure:
            use_xml_prompts()

        # Or create custom config
        config = EmpathyXMLConfig(
            xml=XMLConfig(validate_schemas=True),
            metrics=MetricsConfig(enable_tracking=True)
        )
        config.save_to_file()
    """

    xml: XMLConfig = field(default_factory=XMLConfig)
    optimization: OptimizationConfig = field(default_factory=OptimizationConfig)
    adaptive: AdaptiveConfig = field(default_factory=AdaptiveConfig)
    i18n: I18nConfig = field(default_factory=I18nConfig)
    metrics: MetricsConfig = field(default_factory=MetricsConfig)

    @classmethod
    def load_from_file(cls, config_file: str = ".empathy/config.json") -> "EmpathyXMLConfig":
        """Load configuration from JSON file.

        Args:
            config_file: Path to config file (default: .empathy/config.json)

        Returns:
            EmpathyXMLConfig instance loaded from file, or default config if file doesn't exist
        """
        path = Path(config_file)

        if not path.exists():
            # Return default config if file doesn't exist
            return cls()

        try:
            with open(path) as f:
                data = json.load(f)

            # Reconstruct nested dataclasses
            return cls(
                xml=XMLConfig(**data.get("xml", {})),
                optimization=OptimizationConfig(**data.get("optimization", {})),
                adaptive=AdaptiveConfig(**data.get("adaptive", {})),
                i18n=I18nConfig(**data.get("i18n", {})),
                metrics=MetricsConfig(**data.get("metrics", {})),
            )
        except Exception as e:
            # Return default config on error
            print(f"Warning: Failed to load config from {config_file}: {e}")
            return cls()

    def save_to_file(self, config_file: str = ".empathy/config.json") -> None:
        """Save configuration to JSON file.

        Args:
            config_file: Path to save config (default: .empathy/config.json)
        """
        path = Path(config_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "xml": asdict(self.xml),
            "optimization": asdict(self.optimization),
            "adaptive": asdict(self.adaptive),
            "i18n": asdict(self.i18n),
            "metrics": asdict(self.metrics),
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def from_env(cls) -> "EmpathyXMLConfig":
        """Load configuration from environment variables.

        Environment variables:
            EMPATHY_XML_ENABLED: Enable XML prompts (default: true)
            EMPATHY_VALIDATION_ENABLED: Enable schema validation (default: false)
            EMPATHY_METRICS_ENABLED: Enable metrics tracking (default: true)
            EMPATHY_OPTIMIZATION_LEVEL: Compression level (default: moderate)
            EMPATHY_ADAPTIVE_ENABLED: Enable adaptive prompts (default: true)

        Returns:
            EmpathyXMLConfig with settings from environment variables
        """
        return cls(
            xml=XMLConfig(
                use_xml_structure=os.getenv("EMPATHY_XML_ENABLED", "true").lower() == "true",
                validate_schemas=os.getenv("EMPATHY_VALIDATION_ENABLED", "false").lower() == "true",
            ),
            optimization=OptimizationConfig(
                compression_level=os.getenv("EMPATHY_OPTIMIZATION_LEVEL", "moderate"),
            ),
            adaptive=AdaptiveConfig(
                enable_adaptation=os.getenv("EMPATHY_ADAPTIVE_ENABLED", "true").lower() == "true",
            ),
            metrics=MetricsConfig(
                enable_tracking=os.getenv("EMPATHY_METRICS_ENABLED", "true").lower() == "true",
            ),
        )


# Global default configuration instance
_global_config: EmpathyXMLConfig | None = None


def get_config() -> EmpathyXMLConfig:
    """Get global configuration instance.

    Returns cached config or loads from file if not yet loaded.

    Returns:
        Global EmpathyXMLConfig instance
    """
    global _global_config

    if _global_config is None:
        # Try to load from file, fall back to defaults
        _global_config = EmpathyXMLConfig.load_from_file()

    return _global_config


def set_config(config: EmpathyXMLConfig) -> None:
    """Set global configuration instance.

    Args:
        config: EmpathyXMLConfig to use globally
    """
    global _global_config
    _global_config = config
