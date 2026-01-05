"""Tests for XML configuration system.

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json

from empathy_os.config import (
    AdaptiveConfig,
    EmpathyXMLConfig,
    I18nConfig,
    MetricsConfig,
    OptimizationConfig,
    XMLConfig,
    get_config,
    set_config,
)


def test_xml_config_defaults():
    """Test XMLConfig default values."""
    config = XMLConfig()

    assert config.use_xml_structure is True
    assert config.validate_schemas is False
    assert config.schema_dir == ".empathy/schemas"
    assert config.strict_validation is False


def test_optimization_config_defaults():
    """Test OptimizationConfig default values."""
    config = OptimizationConfig()

    assert config.compression_level == "moderate"
    assert config.use_short_tags is True
    assert config.strip_whitespace is True
    assert config.cache_system_prompts is True
    assert config.max_context_tokens == 8000


def test_adaptive_config_defaults():
    """Test AdaptiveConfig default values."""
    config = AdaptiveConfig()

    assert config.enable_adaptation is True
    assert "simple" in config.model_tier_mapping
    assert "moderate" in config.model_tier_mapping
    assert config.model_tier_mapping["simple"] == "gpt-3.5-turbo"
    assert config.complexity_thresholds["simple_tokens"] == 100


def test_i18n_config_defaults():
    """Test I18nConfig default values."""
    config = I18nConfig()

    assert config.default_language == "en"
    assert config.translate_tags is False
    assert config.translate_content is True
    assert config.fallback_to_english is True


def test_metrics_config_defaults():
    """Test MetricsConfig default values."""
    config = MetricsConfig()

    assert config.enable_tracking is True
    assert config.metrics_file == ".empathy/prompt_metrics.json"
    assert config.track_token_usage is True
    assert config.track_latency is True


def test_empathy_xml_config_creation():
    """Test EmpathyXMLConfig creation."""
    config = EmpathyXMLConfig()

    assert isinstance(config.xml, XMLConfig)
    assert isinstance(config.optimization, OptimizationConfig)
    assert isinstance(config.adaptive, AdaptiveConfig)
    assert isinstance(config.i18n, I18nConfig)
    assert isinstance(config.metrics, MetricsConfig)


def test_empathy_xml_config_custom():
    """Test EmpathyXMLConfig with custom sub-configs."""
    config = EmpathyXMLConfig(
        xml=XMLConfig(validate_schemas=True),
        metrics=MetricsConfig(enable_tracking=False),
    )

    assert config.xml.validate_schemas is True
    assert config.metrics.enable_tracking is False
    assert config.xml.use_xml_structure is True  # Default still applies


def test_save_and_load_config(tmp_path):
    """Test saving and loading config from file."""
    config_file = tmp_path / "test_config.json"

    # Create custom config
    config = EmpathyXMLConfig(
        xml=XMLConfig(validate_schemas=True, strict_validation=True),
        optimization=OptimizationConfig(compression_level="aggressive"),
        metrics=MetricsConfig(enable_tracking=False),
    )

    # Save to file
    config.save_to_file(str(config_file))

    # Verify file exists and has content
    assert config_file.exists()
    with open(config_file) as f:
        data = json.load(f)
        assert data["xml"]["validate_schemas"] is True
        assert data["optimization"]["compression_level"] == "aggressive"

    # Load from file
    loaded_config = EmpathyXMLConfig.load_from_file(str(config_file))

    assert loaded_config.xml.validate_schemas is True
    assert loaded_config.xml.strict_validation is True
    assert loaded_config.optimization.compression_level == "aggressive"
    assert loaded_config.metrics.enable_tracking is False


def test_load_nonexistent_config():
    """Test loading config when file doesn't exist."""
    config = EmpathyXMLConfig.load_from_file("/nonexistent/config.json")

    # Should return default config
    assert isinstance(config, EmpathyXMLConfig)
    assert config.xml.use_xml_structure is True


def test_load_from_env(monkeypatch):
    """Test loading config from environment variables."""
    monkeypatch.setenv("EMPATHY_XML_ENABLED", "false")
    monkeypatch.setenv("EMPATHY_VALIDATION_ENABLED", "true")
    monkeypatch.setenv("EMPATHY_METRICS_ENABLED", "false")
    monkeypatch.setenv("EMPATHY_OPTIMIZATION_LEVEL", "aggressive")
    monkeypatch.setenv("EMPATHY_ADAPTIVE_ENABLED", "false")

    config = EmpathyXMLConfig.from_env()

    assert config.xml.use_xml_structure is False
    assert config.xml.validate_schemas is True
    assert config.metrics.enable_tracking is False
    assert config.optimization.compression_level == "aggressive"
    assert config.adaptive.enable_adaptation is False


def test_global_config():
    """Test global config getter/setter."""
    # Create custom config
    config = EmpathyXMLConfig(xml=XMLConfig(validate_schemas=True))

    # Set global config
    set_config(config)

    # Get global config
    global_config = get_config()

    assert global_config.xml.validate_schemas is True


def test_config_file_creation_with_parent_dirs(tmp_path):
    """Test that save_to_file creates parent directories."""
    nested_path = tmp_path / "level1" / "level2" / "config.json"

    config = EmpathyXMLConfig()
    config.save_to_file(str(nested_path))

    assert nested_path.exists()
    assert nested_path.parent.exists()
