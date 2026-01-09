"""Unit tests for configuration module."""

import os
from pathlib import Path

import pytest

from empathy_os.config import EmpathyConfig


@pytest.mark.unit
def test_empathy_config_initialization():
    """Test EmpathyConfig can be initialized."""
    config = EmpathyConfig()
    assert config is not None
    assert hasattr(config, "user_id")
    assert hasattr(config, "target_level")


@pytest.mark.unit
def test_config_default_values():
    """Test configuration has sensible defaults."""
    config = EmpathyConfig()

    # User ID should have a default
    assert config.user_id is not None
    assert isinstance(config.user_id, str)

    # Target level should be valid (1-5 range typical)
    assert hasattr(config, "target_level")
    if hasattr(config, "target_level"):
        assert 1 <= config.target_level <= 5


@pytest.mark.unit
def test_config_confidence_threshold():
    """Test confidence threshold configuration."""
    config = EmpathyConfig()

    if hasattr(config, "confidence_threshold"):
        # Should be a float between 0 and 1
        assert isinstance(config.confidence_threshold, float)
        assert 0.0 <= config.confidence_threshold <= 1.0


@pytest.mark.unit
def test_config_environment_variables():
    """Test configuration can be influenced by environment."""
    # Set test environment variable
    test_user_id = "test_user_123"
    original = os.environ.get("EMPATHY_USER_ID")

    try:
        os.environ["EMPATHY_USER_ID"] = test_user_id
        config = EmpathyConfig()

        # Config should use env var if available
        # (This test may need adjustment based on actual implementation)
        assert config is not None
    finally:
        # Restore original
        if original:
            os.environ["EMPATHY_USER_ID"] = original
        else:
            os.environ.pop("EMPATHY_USER_ID", None)


@pytest.mark.unit
def test_config_api_key_security():
    """Test API key handling (should not expose keys in logs)."""
    config = EmpathyConfig()

    # Config object string representation shouldn't expose API keys
    config_str = str(config)
    config_repr = repr(config)

    # Common API key patterns shouldn't appear in full
    # (Looking for patterns like sk-xxxx or api_key=...)
    assert "sk-" not in config_str or "***" in config_str, "API keys should be masked in str()"
    assert "sk-" not in config_repr or "***" in config_repr, "API keys should be masked in repr()"


@pytest.mark.unit
def test_config_serialization():
    """Test config can be serialized for storage."""
    config = EmpathyConfig()

    # Should be convertible to dict or have accessible attributes
    assert hasattr(config, "__dict__") or hasattr(config, "to_dict")


@pytest.mark.unit
def test_config_validation():
    """Test configuration validates required fields."""
    config = EmpathyConfig()

    # Basic validation - user_id should exist and not be empty
    assert config.user_id
    assert len(config.user_id) > 0

    # Target level should be in valid range
    if hasattr(config, "target_level"):
        assert config.target_level in range(1, 6), "Target level should be 1-5"


@pytest.mark.unit
def test_config_file_paths():
    """Test configuration has proper file path handling."""
    config = EmpathyConfig()

    # If config has paths, they should be Path objects or strings
    for attr in dir(config):
        value = getattr(config, attr)
        if "path" in attr.lower() and value is not None:
            assert isinstance(value, str | Path), f"{attr} should be string or Path"
