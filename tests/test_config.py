"""
Tests for Configuration Module

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import json
import os
import shutil
import tempfile
from pathlib import Path

import pytest

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
        config = EmpathyConfig(user_id="alice", target_level=4, confidence_threshold=0.8)

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
            target_level=4, confidence_threshold=0.8, pattern_confidence_threshold=0.5
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
        with open(filepath) as f:
            data = json.load(f)

        assert data["user_id"] == "alice"
        assert data["target_level"] == 4

    def test_load_from_json(self, temp_dir):
        """Test loading config from JSON"""
        filepath = Path(temp_dir) / "config.json"

        data = {"user_id": "bob", "target_level": 5, "confidence_threshold": 0.9}

        with open(filepath, "w") as f:
            json.dump(data, f)

        config = EmpathyConfig.from_json(str(filepath))

        assert config.user_id == "bob"
        assert config.target_level == 5
        assert config.confidence_threshold == 0.9

    def test_round_trip_json(self, temp_dir):
        """Test save and load preserves config"""
        filepath = Path(temp_dir) / "config.json"

        original = EmpathyConfig(
            user_id="charlie", target_level=3, confidence_threshold=0.7, metrics_enabled=False
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
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        config = EmpathyConfig(user_id="alice", target_level=4)
        filepath = Path(temp_dir) / "config.yml"

        config.to_yaml(str(filepath))

        assert filepath.exists()

    def test_load_from_yaml(self, temp_dir):
        """Test loading config from YAML"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        filepath = Path(temp_dir) / "config.yml"

        yaml_content = """
user_id: bob
target_level: 5
confidence_threshold: 0.9
metrics_enabled: false
"""

        with open(filepath, "w") as f:
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
        config = load_config(defaults={"user_id": "custom", "target_level": 5}, use_env=False)

        assert config.user_id == "custom"
        assert config.target_level == 5

    def test_load_config_from_json(self, temp_dir):
        """Test loading from JSON file"""
        filepath = Path(temp_dir) / "test.json"

        data = {"user_id": "json_user", "target_level": 4}

        with open(filepath, "w") as f:
            json.dump(data, f)

        config = load_config(filepath=str(filepath), use_env=False)

        assert config.user_id == "json_user"
        assert config.target_level == 4

    def test_load_config_precedence(self, temp_dir):
        """Test configuration precedence"""
        # Create config file
        filepath = Path(temp_dir) / "test.json"
        with open(filepath, "w") as f:
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

        with open(filepath, "w") as f:
            json.dump({"user_id": "json_test"}, f)

        config = EmpathyConfig.from_file(str(filepath))

        assert config.user_id == "json_test"

    def test_from_file_yaml(self, temp_dir):
        """Test from_file detects YAML"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        filepath = Path(temp_dir) / "config.yml"

        yaml_content = """
user_id: yaml_test
target_level: 4
"""
        with open(filepath, "w") as f:
            f.write(yaml_content)

        config = EmpathyConfig.from_file(str(filepath))

        assert config.user_id == "yaml_test"
        assert config.target_level == 4

    def test_from_file_yaml_extension(self, temp_dir):
        """Test from_file with .yaml extension"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        filepath = Path(temp_dir) / "config.yaml"

        yaml_content = """
user_id: yaml_ext_test
"""
        with open(filepath, "w") as f:
            f.write(yaml_content)

        config = EmpathyConfig.from_file(str(filepath))

        assert config.user_id == "yaml_ext_test"

    def test_from_file_auto_detect_empathy_yml(self, temp_dir):
        """Test auto-detection of .empathy.yml"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        # Change to temp dir
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            filepath = Path(".empathy.yml")
            yaml_content = """
user_id: auto_detect_test
"""
            with open(filepath, "w") as f:
                f.write(yaml_content)

            config = EmpathyConfig.from_file()

            assert config.user_id == "auto_detect_test"
        finally:
            os.chdir(original_cwd)

    def test_from_file_auto_detect_empathy_json(self, temp_dir):
        """Test auto-detection of .empathy.json"""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            filepath = Path(".empathy.json")
            with open(filepath, "w") as f:
                json.dump({"user_id": "json_auto_test"}, f)

            config = EmpathyConfig.from_file()

            assert config.user_id == "json_auto_test"
        finally:
            os.chdir(original_cwd)


class TestConfigErrorHandling:
    """Test error handling and edge cases"""

    def test_from_json_file_not_found(self):
        """Test from_json raises FileNotFoundError"""
        with pytest.raises(FileNotFoundError):
            EmpathyConfig.from_json("nonexistent.json")

    def test_from_json_invalid_json(self, temp_dir):
        """Test from_json with invalid JSON"""
        filepath = Path(temp_dir) / "invalid.json"

        with open(filepath, "w") as f:
            f.write("{invalid json")

        with pytest.raises(json.JSONDecodeError):
            EmpathyConfig.from_json(str(filepath))

    def test_from_yaml_file_not_found(self):
        """Test from_yaml raises FileNotFoundError"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        with pytest.raises(FileNotFoundError):
            EmpathyConfig.from_yaml("nonexistent.yml")

    def test_from_yaml_no_pyyaml(self, monkeypatch):
        """Test from_yaml raises ImportError without PyYAML"""
        # Temporarily make YAML unavailable
        import empathy_os.config as config_module

        original_yaml_available = config_module.YAML_AVAILABLE

        try:
            monkeypatch.setattr(config_module, "YAML_AVAILABLE", False)

            with pytest.raises(ImportError, match="PyYAML is required"):
                EmpathyConfig.from_yaml("test.yml")
        finally:
            monkeypatch.setattr(config_module, "YAML_AVAILABLE", original_yaml_available)

    def test_to_yaml_no_pyyaml(self, monkeypatch, temp_dir):
        """Test to_yaml raises ImportError without PyYAML"""
        import empathy_os.config as config_module

        original_yaml_available = config_module.YAML_AVAILABLE

        try:
            monkeypatch.setattr(config_module, "YAML_AVAILABLE", False)

            config = EmpathyConfig()
            filepath = Path(temp_dir) / "test.yml"

            with pytest.raises(ImportError, match="PyYAML is required"):
                config.to_yaml(str(filepath))
        finally:
            monkeypatch.setattr(config_module, "YAML_AVAILABLE", original_yaml_available)

    def test_validate_target_level_boundary_low(self):
        """Test validation with target_level=0"""
        config = EmpathyConfig(target_level=0)

        with pytest.raises(ValueError, match="target_level must be 1-5"):
            config.validate()

    def test_validate_target_level_boundary_high(self):
        """Test validation with target_level=6"""
        config = EmpathyConfig(target_level=6)

        with pytest.raises(ValueError, match="target_level must be 1-5"):
            config.validate()

    def test_validate_target_level_valid_boundaries(self):
        """Test validation with valid boundary values"""
        for level in [1, 2, 3, 4, 5]:
            config = EmpathyConfig(target_level=level)
            assert config.validate() is True

    def test_validate_confidence_negative(self):
        """Test validation with negative confidence"""
        config = EmpathyConfig(confidence_threshold=-0.1)

        with pytest.raises(ValueError, match="confidence_threshold must be 0.0-1.0"):
            config.validate()

    def test_validate_confidence_valid_boundaries(self):
        """Test validation with valid confidence boundaries"""
        for threshold in [0.0, 0.5, 1.0]:
            config = EmpathyConfig(confidence_threshold=threshold)
            assert config.validate() is True

    def test_validate_pattern_confidence_invalid(self):
        """Test validation with invalid pattern_confidence_threshold"""
        config = EmpathyConfig(pattern_confidence_threshold=1.5)

        with pytest.raises(ValueError, match="pattern_confidence_threshold must be 0.0-1.0"):
            config.validate()

    def test_validate_pattern_confidence_valid_boundaries(self):
        """Test validation with valid pattern confidence boundaries"""
        for threshold in [0.0, 0.3, 1.0]:
            config = EmpathyConfig(pattern_confidence_threshold=threshold)
            assert config.validate() is True

    def test_update_nonexistent_field(self):
        """Test update with non-existent field (should be ignored)"""
        config = EmpathyConfig(user_id="alice")
        config.update(nonexistent_field="value", user_id="bob")

        assert config.user_id == "bob"
        assert not hasattr(config, "nonexistent_field")


class TestConfigAdvancedFeatures:
    """Test advanced configuration features"""

    def test_metadata_field(self):
        """Test metadata field with custom data"""
        config = EmpathyConfig(
            user_id="test", metadata={"app_version": "1.0.0", "env": "production"}
        )

        assert config.metadata["app_version"] == "1.0.0"
        assert config.metadata["env"] == "production"

    def test_merge_with_metadata(self):
        """Test merge preserves metadata"""
        base = EmpathyConfig(user_id="alice", metadata={"env": "dev"})
        override = EmpathyConfig(target_level=5, metadata={"version": "2.0"})

        merged = base.merge(override)

        # Override metadata should take precedence
        assert "version" in merged.metadata

    def test_to_json_custom_indent(self, temp_dir):
        """Test to_json with custom indent"""
        config = EmpathyConfig(user_id="indent_test")
        filepath = Path(temp_dir) / "indent.json"

        config.to_json(str(filepath), indent=4)

        with open(filepath) as f:
            content = f.read()

        # Check for 4-space indentation
        assert "    " in content

    def test_to_json_no_indent(self, temp_dir):
        """Test to_json with no indent"""
        config = EmpathyConfig(user_id="compact")
        filepath = Path(temp_dir) / "compact.json"

        config.to_json(str(filepath), indent=0)

        assert filepath.exists()

    def test_repr_method(self):
        """Test __repr__ string representation"""
        config = EmpathyConfig(user_id="test_user", target_level=4, confidence_threshold=0.85)

        repr_str = repr(config)

        assert "EmpathyConfig" in repr_str
        assert "test_user" in repr_str
        assert "4" in repr_str
        assert "0.85" in repr_str


class TestConfigEnvironmentVariables:
    """Extended environment variable tests"""

    def test_from_env_custom_prefix(self):
        """Test from_env with custom prefix"""
        os.environ["CUSTOM_USER_ID"] = "custom_prefix_user"
        os.environ["CUSTOM_TARGET_LEVEL"] = "5"

        try:
            config = EmpathyConfig.from_env(prefix="CUSTOM_")

            assert config.user_id == "custom_prefix_user"
            assert config.target_level == 5
        finally:
            del os.environ["CUSTOM_USER_ID"]
            del os.environ["CUSTOM_TARGET_LEVEL"]

    def test_from_env_boolean_variants(self):
        """Test boolean parsing with different values"""
        test_cases = [
            ("true", True),
            ("True", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("YES", True),
            ("false", False),
            ("False", False),
            ("0", False),
            ("no", False),
        ]

        for value, expected in test_cases:
            os.environ["EMPATHY_METRICS_ENABLED"] = value

            try:
                config = EmpathyConfig.from_env()
                assert config.metrics_enabled == expected, f"Failed for value: {value}"
            finally:
                del os.environ["EMPATHY_METRICS_ENABLED"]

    def test_from_env_float_fields(self):
        """Test parsing float fields from env"""
        os.environ["EMPATHY_TRUST_BUILDING_RATE"] = "0.08"
        os.environ["EMPATHY_TRUST_EROSION_RATE"] = "0.15"
        os.environ["EMPATHY_PATTERN_CONFIDENCE_THRESHOLD"] = "0.4"

        try:
            config = EmpathyConfig.from_env()

            assert config.trust_building_rate == 0.08
            assert config.trust_erosion_rate == 0.15
            assert config.pattern_confidence_threshold == 0.4
        finally:
            del os.environ["EMPATHY_TRUST_BUILDING_RATE"]
            del os.environ["EMPATHY_TRUST_EROSION_RATE"]
            del os.environ["EMPATHY_PATTERN_CONFIDENCE_THRESHOLD"]

    def test_from_env_all_boolean_fields(self):
        """Test all boolean fields from environment"""
        boolean_fields = [
            ("PERSISTENCE_ENABLED", "persistence_enabled"),
            ("STATE_PERSISTENCE", "state_persistence"),
            ("METRICS_ENABLED", "metrics_enabled"),
            ("STRUCTURED_LOGGING", "structured_logging"),
            ("PATTERN_LIBRARY_ENABLED", "pattern_library_enabled"),
            ("PATTERN_SHARING", "pattern_sharing"),
            ("ASYNC_ENABLED", "async_enabled"),
            ("FEEDBACK_LOOP_MONITORING", "feedback_loop_monitoring"),
            ("LEVERAGE_POINT_ANALYSIS", "leverage_point_analysis"),
        ]

        for env_name, _field_name in boolean_fields:
            os.environ[f"EMPATHY_{env_name}"] = "true"

        try:
            config = EmpathyConfig.from_env()

            for _, field_name in boolean_fields:
                assert getattr(config, field_name) is True
        finally:
            for env_name, _ in boolean_fields:
                del os.environ[f"EMPATHY_{env_name}"]

    def test_from_env_string_fields(self):
        """Test string fields from environment"""
        os.environ["EMPATHY_PERSISTENCE_BACKEND"] = "json"
        os.environ["EMPATHY_PERSISTENCE_PATH"] = "/custom/path"
        os.environ["EMPATHY_LOG_LEVEL"] = "DEBUG"
        os.environ["EMPATHY_LOG_FILE"] = "/var/log/empathy.log"

        try:
            config = EmpathyConfig.from_env()

            assert config.persistence_backend == "json"
            assert config.persistence_path == "/custom/path"
            assert config.log_level == "DEBUG"
            assert config.log_file == "/var/log/empathy.log"
        finally:
            del os.environ["EMPATHY_PERSISTENCE_BACKEND"]
            del os.environ["EMPATHY_PERSISTENCE_PATH"]
            del os.environ["EMPATHY_LOG_LEVEL"]
            del os.environ["EMPATHY_LOG_FILE"]


class TestLoadConfigAdvanced:
    """Advanced load_config tests"""

    def test_load_config_with_invalid_json(self, temp_dir):
        """Test load_config handles invalid JSON gracefully"""
        filepath = Path(temp_dir) / "invalid.json"

        with open(filepath, "w") as f:
            f.write("{invalid")

        # Should return defaults without crashing
        config = load_config(filepath=str(filepath), use_env=False)

        assert config.user_id == "default_user"

    def test_load_config_env_override(self):
        """Test environment variables override file config"""
        os.environ["EMPATHY_TARGET_LEVEL"] = "5"

        try:
            config = load_config(use_env=True)

            assert config.target_level == 5
        finally:
            del os.environ["EMPATHY_TARGET_LEVEL"]

    def test_load_config_validation_failure(self):
        """Test load_config validates final config"""
        # This should fail validation
        with pytest.raises(ValueError):
            load_config(defaults={"target_level": 10}, use_env=False)

    def test_load_config_defaults_with_file(self, temp_dir):
        """Test defaults are applied before file config"""
        filepath = Path(temp_dir) / "config.json"

        with open(filepath, "w") as f:
            json.dump({"target_level": 4}, f)

        config = load_config(
            filepath=str(filepath), defaults={"user_id": "default_user_custom"}, use_env=False
        )

        assert config.user_id == "default_user_custom"
        assert config.target_level == 4

    def test_load_config_no_file_with_defaults(self):
        """Test load_config with defaults when no file exists"""
        config = load_config(
            filepath="nonexistent.json",
            defaults={"user_id": "custom_default", "target_level": 4},
            use_env=False,
        )

        assert config.user_id == "custom_default"
        assert config.target_level == 4

    def test_load_config_env_exception_handling(self, monkeypatch):
        """Test load_config handles environment parsing errors"""

        # Mock from_env to raise an exception
        def mock_from_env(prefix="EMPATHY_"):
            raise ValueError("Simulated parsing error")

        monkeypatch.setattr(EmpathyConfig, "from_env", mock_from_env)

        # Should not crash, should use defaults
        config = load_config(use_env=True)

        assert config.user_id == "default_user"


class TestConfigYAMLRoundTrip:
    """Test YAML round-trip with complex data"""

    def test_yaml_with_all_fields(self, temp_dir):
        """Test YAML with all configuration fields"""
        try:
            import yaml  # noqa: F401
        except ImportError:
            pytest.skip("PyYAML not installed")

        filepath = Path(temp_dir) / "complete.yml"

        original = EmpathyConfig(
            user_id="complete_test",
            target_level=4,
            confidence_threshold=0.85,
            trust_building_rate=0.06,
            trust_erosion_rate=0.12,
            persistence_enabled=False,
            persistence_backend="json",
            persistence_path="/custom/persist",
            state_persistence=False,
            state_path="/custom/state",
            metrics_enabled=False,
            metrics_path="/custom/metrics.db",
            log_level="DEBUG",
            log_file="/custom/log.txt",
            structured_logging=False,
            pattern_library_enabled=False,
            pattern_sharing=False,
            pattern_confidence_threshold=0.4,
            async_enabled=False,
            feedback_loop_monitoring=False,
            leverage_point_analysis=False,
            metadata={"custom": "data"},
        )

        original.to_yaml(str(filepath))
        loaded = EmpathyConfig.from_yaml(str(filepath))

        # Verify all fields
        assert loaded.user_id == original.user_id
        assert loaded.target_level == original.target_level
        assert loaded.confidence_threshold == original.confidence_threshold
        assert loaded.trust_building_rate == original.trust_building_rate
        assert loaded.persistence_backend == original.persistence_backend
        assert loaded.log_level == original.log_level
        assert loaded.metadata == original.metadata


class TestConfigJSONRoundTrip:
    """Test JSON round-trip with complex data"""

    def test_json_with_all_boolean_fields(self, temp_dir):
        """Test JSON preserves all boolean fields"""
        filepath = Path(temp_dir) / "all_bool.json"

        original = EmpathyConfig(
            persistence_enabled=False,
            state_persistence=False,
            metrics_enabled=False,
            structured_logging=False,
            pattern_library_enabled=False,
            pattern_sharing=False,
            async_enabled=False,
            feedback_loop_monitoring=False,
            leverage_point_analysis=False,
        )

        original.to_json(str(filepath))
        loaded = EmpathyConfig.from_json(str(filepath))

        assert loaded.persistence_enabled is False
        assert loaded.state_persistence is False
        assert loaded.metrics_enabled is False
        assert loaded.structured_logging is False
        assert loaded.pattern_library_enabled is False

    def test_json_with_metadata(self, temp_dir):
        """Test JSON preserves metadata dictionary"""
        filepath = Path(temp_dir) / "metadata.json"

        original = EmpathyConfig(
            metadata={"version": "1.0.0", "environment": "production", "nested": {"key": "value"}}
        )

        original.to_json(str(filepath))
        loaded = EmpathyConfig.from_json(str(filepath))

        assert loaded.metadata["version"] == "1.0.0"
        assert loaded.metadata["environment"] == "production"
        assert loaded.metadata["nested"]["key"] == "value"


class TestConfigFromFileElif:
    """Test from_file JSON elif branch"""

    def test_from_file_json_explicit_elif(self, temp_dir):
        """Test from_file with .json extension triggers elif branch (line 226)"""
        # This test explicitly covers the elif path.endswith(".json") branch
        filepath = Path(temp_dir) / "test_config.json"

        with open(filepath, "w") as f:
            json.dump({"user_id": "json_elif_test", "target_level": 2}, f)

        # Call from_file with explicit JSON path
        config = EmpathyConfig.from_file(str(filepath))

        assert config.user_id == "json_elif_test"
        assert config.target_level == 2


class TestLoadConfigDefaultPathDetection:
    """Test load_config default path detection"""

    def test_load_config_finds_default_json_file(self, temp_dir):
        """Test load_config finds and uses .empathy.json file (lines 406-407)"""
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)

            # Create .empathy.json in current directory
            with open(".empathy.json", "w") as f:
                json.dump({"user_id": "default_json_user", "target_level": 3}, f)

            # Call load_config without filepath (should find .empathy.json)
            config = load_config(filepath=None, use_env=False)

            assert config.user_id == "default_json_user"
            assert config.target_level == 3

        finally:
            os.chdir(original_cwd)
