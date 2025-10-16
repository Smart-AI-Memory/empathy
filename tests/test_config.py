"""
Tests for Configuration Module

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path

from empathy_os import EmpathyConfig, load_config


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


class TestEmpathyConfig:
    """Test EmpathyConfig class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = EmpathyConfig()

        assert config.user_id == "default_user"
        assert config.target_level == 3
        assert config.confidence_threshold == 0.75
        assert config.persistence_enabled is True
        assert config.metrics_enabled is True

    def test_custom_config(self):
        """Test creating config with custom values"""
        config = EmpathyConfig(
            user_id="alice",
            target_level=4,
            confidence_threshold=0.8
        )

        assert config.user_id == "alice"
        assert config.target_level == 4
        assert config.confidence_threshold == 0.8

    def test_to_dict(self):
        """Test converting config to dictionary"""
        config = EmpathyConfig(user_id="bob", target_level=5)
        data = config.to_dict()

        assert isinstance(data, dict)
        assert data["user_id"] == "bob"
        assert data["target_level"] == 5

    def test_update(self):
        """Test updating config fields"""
        config = EmpathyConfig()
        config.update(user_id="charlie", target_level=2)

        assert config.user_id == "charlie"
        assert config.target_level == 2

    def test_merge(self):
        """Test merging two configurations"""
        base = EmpathyConfig(user_id="alice", target_level=3)
        override = EmpathyConfig(target_level=5, confidence_threshold=0.9)

        merged = base.merge(override)

        assert merged.user_id == "alice"  # From base
        assert merged.target_level == 5  # From override
        assert merged.confidence_threshold == 0.9  # From override

    def test_validate_success(self):
        """Test validation with valid config"""
        config = EmpathyConfig(
            target_level=4,
            confidence_threshold=0.8,
            pattern_confidence_threshold=0.5
        )

        assert config.validate() is True

    def test_validate_invalid_target_level(self):
        """Test validation fails with invalid target level"""
        config = EmpathyConfig(target_level=10)

        with pytest.raises(ValueError, match="target_level must be 1-5"):
            config.validate()

    def test_validate_invalid_confidence(self):
        """Test validation fails with invalid confidence"""
        config = EmpathyConfig(confidence_threshold=1.5)

        with pytest.raises(ValueError, match="confidence_threshold must be 0.0-1.0"):
            config.validate()

    def test_validate_invalid_backend(self):
        """Test validation fails with invalid backend"""
        config = EmpathyConfig(persistence_backend="invalid")

        with pytest.raises(ValueError, match="persistence_backend must be"):
            config.validate()


class TestConfigJSON:
    """Test JSON configuration"""

    def test_save_to_json(self, temp_dir):
        """Test saving config to JSON"""
        config = EmpathyConfig(user_id="alice", target_level=4)
        filepath = Path(temp_dir) / "config.json"

        config.to_json(str(filepath))

        assert filepath.exists()

        # Verify content
        with open(filepath, 'r') as f:
            data = json.load(f)

        assert data["user_id"] == "alice"
        assert data["target_level"] == 4

    def test_load_from_json(self, temp_dir):
        """Test loading config from JSON"""
        filepath = Path(temp_dir) / "config.json"

        data = {
            "user_id": "bob",
            "target_level": 5,
            "confidence_threshold": 0.9
        }

        with open(filepath, 'w') as f:
            json.dump(data, f)

        config = EmpathyConfig.from_json(str(filepath))

        assert config.user_id == "bob"
        assert config.target_level == 5
        assert config.confidence_threshold == 0.9

    def test_round_trip_json(self, temp_dir):
        """Test save and load preserves config"""
        filepath = Path(temp_dir) / "config.json"

        original = EmpathyConfig(
            user_id="charlie",
            target_level=3,
            confidence_threshold=0.7,
            metrics_enabled=False
        )

        original.to_json(str(filepath))
        loaded = EmpathyConfig.from_json(str(filepath))

        assert loaded.user_id == original.user_id
        assert loaded.target_level == original.target_level
        assert loaded.confidence_threshold == original.confidence_threshold
        assert loaded.metrics_enabled == original.metrics_enabled


class TestConfigYAML:
    """Test YAML configuration"""

    def test_save_to_yaml(self, temp_dir):
        """Test saving config to YAML"""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        config = EmpathyConfig(user_id="alice", target_level=4)
        filepath = Path(temp_dir) / "config.yml"

        config.to_yaml(str(filepath))

        assert filepath.exists()

    def test_load_from_yaml(self, temp_dir):
        """Test loading config from YAML"""
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not installed")

        filepath = Path(temp_dir) / "config.yml"

        yaml_content = """
user_id: bob
target_level: 5
confidence_threshold: 0.9
metrics_enabled: false
"""

        with open(filepath, 'w') as f:
            f.write(yaml_content)

        config = EmpathyConfig.from_yaml(str(filepath))

        assert config.user_id == "bob"
        assert config.target_level == 5
        assert config.confidence_threshold == 0.9
        assert config.metrics_enabled is False


class TestConfigFromEnv:
    """Test environment variable configuration"""

    def test_from_env_basic(self):
        """Test loading from environment variables"""
        os.environ["EMPATHY_USER_ID"] = "env_user"
        os.environ["EMPATHY_TARGET_LEVEL"] = "4"
        os.environ["EMPATHY_CONFIDENCE_THRESHOLD"] = "0.85"

        try:
            config = EmpathyConfig.from_env()

            assert config.user_id == "env_user"
            assert config.target_level == 4
            assert config.confidence_threshold == 0.85
        finally:
            # Cleanup
            del os.environ["EMPATHY_USER_ID"]
            del os.environ["EMPATHY_TARGET_LEVEL"]
            del os.environ["EMPATHY_CONFIDENCE_THRESHOLD"]

    def test_from_env_booleans(self):
        """Test boolean environment variables"""
        os.environ["EMPATHY_METRICS_ENABLED"] = "false"
        os.environ["EMPATHY_PERSISTENCE_ENABLED"] = "true"

        try:
            config = EmpathyConfig.from_env()

            assert config.metrics_enabled is False
            assert config.persistence_enabled is True
        finally:
            del os.environ["EMPATHY_METRICS_ENABLED"]
            del os.environ["EMPATHY_PERSISTENCE_ENABLED"]


class TestLoadConfig:
    """Test load_config helper function"""

    def test_load_config_defaults(self):
        """Test loading with defaults only"""
        config = load_config(use_env=False)

        assert config.user_id == "default_user"
        assert config.target_level == 3

    def test_load_config_with_custom_defaults(self):
        """Test loading with custom defaults"""
        config = load_config(
            defaults={"user_id": "custom", "target_level": 5},
            use_env=False
        )

        assert config.user_id == "custom"
        assert config.target_level == 5

    def test_load_config_from_json(self, temp_dir):
        """Test loading from JSON file"""
        filepath = Path(temp_dir) / "test.json"

        data = {"user_id": "json_user", "target_level": 4}

        with open(filepath, 'w') as f:
            json.dump(data, f)

        config = load_config(filepath=str(filepath), use_env=False)

        assert config.user_id == "json_user"
        assert config.target_level == 4

    def test_load_config_precedence(self, temp_dir):
        """Test configuration precedence"""
        # Create config file
        filepath = Path(temp_dir) / "test.json"
        with open(filepath, 'w') as f:
            json.dump({"user_id": "file_user", "target_level": 3}, f)

        # Set environment variable
        os.environ["EMPATHY_USER_ID"] = "env_user"

        try:
            config = load_config(filepath=str(filepath), use_env=True)

            # Environment should override file
            assert config.user_id == "env_user"
            # File value should be used for target_level
            assert config.target_level == 3
        finally:
            del os.environ["EMPATHY_USER_ID"]


class TestConfigFromFile:
    """Test from_file auto-detection"""

    def test_from_file_not_found(self):
        """Test from_file returns defaults when no file found"""
        config = EmpathyConfig.from_file("nonexistent.yml")

        assert config.user_id == "default_user"

    def test_from_file_json(self, temp_dir):
        """Test from_file detects JSON"""
        filepath = Path(temp_dir) / "config.json"

        with open(filepath, 'w') as f:
            json.dump({"user_id": "json_test"}, f)

        config = EmpathyConfig.from_file(str(filepath))

        assert config.user_id == "json_test"
