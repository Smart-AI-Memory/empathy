"""Tests for Multi-Model Configuration Validation Module

Tests the schema validation functionality:
- ValidationError and ValidationResult
- ConfigValidator for workflow configs
- Provider/tier validation
- YAML file validation

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile

import pytest

from empathy_os.models.validation import (
    ConfigValidator,
    ValidationError,
    ValidationResult,
    validate_config,
    validate_yaml_file,
)


class TestValidationError:
    """Tests for ValidationError dataclass."""

    def test_create_error(self):
        """Test creating a validation error."""
        error = ValidationError(
            path="stages[0].tier",
            message="Unknown tier 'super'",
            severity="error",
        )

        assert error.path == "stages[0].tier"
        assert error.message == "Unknown tier 'super'"
        assert error.severity == "error"

    def test_str_representation(self):
        """Test string representation."""
        error = ValidationError(
            path="name",
            message="Required field is missing",
        )

        assert "[ERROR] name:" in str(error)
        assert "Required field is missing" in str(error)

    def test_warning_severity(self):
        """Test warning severity."""
        warning = ValidationError(
            path="provider",
            message="Provider may not support this tier",
            severity="warning",
        )

        assert "[WARNING]" in str(warning)


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_initial_valid(self):
        """Test result starts valid."""
        result = ValidationResult(valid=True)

        assert result.valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error_invalidates(self):
        """Test adding error invalidates result."""
        result = ValidationResult(valid=True)
        result.add_error("field", "Error message")

        assert result.valid is False
        assert len(result.errors) == 1

    def test_add_warning_keeps_valid(self):
        """Test adding warning keeps result valid."""
        result = ValidationResult(valid=True)
        result.add_warning("field", "Warning message")

        assert result.valid is True
        assert len(result.warnings) == 1

    def test_str_representation_valid(self):
        """Test string output for valid result."""
        result = ValidationResult(valid=True)

        assert "valid" in str(result).lower()

    def test_str_representation_with_errors(self):
        """Test string output with errors."""
        result = ValidationResult(valid=True)
        result.add_error("name", "Missing required field")
        result.add_warning("tier", "Unknown tier")

        output = str(result)
        assert "errors" in output.lower()
        assert "name" in output
        assert "tier" in output


class TestConfigValidator:
    """Tests for ConfigValidator."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ConfigValidator()

    def test_valid_providers(self, validator):
        """Test valid providers list."""
        assert "anthropic" in validator.VALID_PROVIDERS
        assert "openai" in validator.VALID_PROVIDERS
        assert "ollama" in validator.VALID_PROVIDERS

    def test_valid_tiers(self, validator):
        """Test valid tiers list."""
        assert "cheap" in validator.VALID_TIERS
        assert "capable" in validator.VALID_TIERS
        assert "premium" in validator.VALID_TIERS

    def test_valid_minimal_config(self, validator):
        """Test validation of minimal valid config."""
        config = {"name": "test_workflow"}

        result = validator.validate_workflow_config(config)

        assert result.valid is True

    def test_valid_full_config(self, validator):
        """Test validation of full config."""
        config = {
            "name": "code_review",
            "description": "Reviews code for issues",
            "default_provider": "anthropic",
            "stages": [
                {
                    "name": "triage",
                    "tier": "cheap",
                    "timeout_ms": 30000,
                },
                {
                    "name": "analysis",
                    "tier": "capable",
                    "provider": "anthropic",
                    "max_retries": 3,
                },
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is True
        assert len(result.errors) == 0

    def test_missing_required_name(self, validator):
        """Test error on missing name field."""
        config = {"description": "No name"}

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("name" in e.path for e in result.errors)

    def test_invalid_provider(self, validator):
        """Test error on invalid provider."""
        config = {
            "name": "test",
            "default_provider": "invalid_provider",
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("provider" in e.path for e in result.errors)

    def test_invalid_stage_tier(self, validator):
        """Test error on invalid stage tier."""
        config = {
            "name": "test",
            "stages": [
                {"name": "step1", "tier": "super_premium"},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("tier" in e.path for e in result.errors)

    def test_missing_stage_name(self, validator):
        """Test error on missing stage name."""
        config = {
            "name": "test",
            "stages": [
                {"tier": "capable"},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("name" in e.path for e in result.errors)

    def test_missing_stage_tier(self, validator):
        """Test error on missing stage tier."""
        config = {
            "name": "test",
            "stages": [
                {"name": "step1"},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("tier" in e.path for e in result.errors)

    def test_invalid_timeout_negative(self, validator):
        """Test error on negative timeout."""
        config = {
            "name": "test",
            "stages": [
                {"name": "step1", "tier": "capable", "timeout_ms": -1000},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("timeout" in e.path for e in result.errors)

    def test_invalid_timeout_too_large(self, validator):
        """Test error on too large timeout."""
        config = {
            "name": "test",
            "stages": [
                {"name": "step1", "tier": "capable", "timeout_ms": 1000000},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("timeout" in e.path for e in result.errors)

    def test_invalid_max_retries(self, validator):
        """Test error on invalid max_retries."""
        config = {
            "name": "test",
            "stages": [
                {"name": "step1", "tier": "capable", "max_retries": 100},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert any("retries" in e.path for e in result.errors)

    def test_invalid_type_name(self, validator):
        """Test error on wrong type for name."""
        config = {"name": 123}

        result = validator.validate_workflow_config(config)

        assert result.valid is False

    def test_invalid_stages_not_list(self, validator):
        """Test error when stages is not a list."""
        config = {
            "name": "test",
            "stages": "not a list",
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False

    def test_multiple_errors(self, validator):
        """Test multiple validation errors."""
        config = {
            "default_provider": "invalid",
            "stages": [
                {"tier": "super"},
            ],
        }

        result = validator.validate_workflow_config(config)

        assert result.valid is False
        assert len(result.errors) >= 2  # Missing name + invalid provider + invalid tier


class TestValidateProviderTier:
    """Tests for provider/tier validation."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ConfigValidator()

    def test_valid_combination(self, validator):
        """Test valid provider/tier combination."""
        result = validator.validate_provider_tier("anthropic", "capable")

        assert result.valid is True

    def test_invalid_provider(self, validator):
        """Test invalid provider."""
        result = validator.validate_provider_tier("unknown", "capable")

        assert result.valid is False

    def test_invalid_tier(self, validator):
        """Test invalid tier."""
        result = validator.validate_provider_tier("anthropic", "ultra")

        assert result.valid is False


class TestValidateConfig:
    """Tests for validate_config convenience function."""

    def test_valid_config(self):
        """Test validating a valid config."""
        config = {
            "name": "test",
            "stages": [{"name": "s1", "tier": "capable"}],
        }

        result = validate_config(config)

        assert result.valid is True

    def test_invalid_config(self):
        """Test validating an invalid config."""
        config = {"stages": [{"name": "s1"}]}  # Missing name and tier

        result = validate_config(config)

        assert result.valid is False


class TestValidateYamlFile:
    """Tests for YAML file validation."""

    def test_valid_yaml_file(self):
        """Test validating a valid YAML file."""
        yaml_content = """
name: code_review
description: Review code
default_provider: anthropic
stages:
  - name: triage
    tier: cheap
  - name: analysis
    tier: capable
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = validate_yaml_file(f.name)

        assert result.valid is True

    def test_invalid_yaml_syntax(self):
        """Test error on invalid YAML syntax."""
        yaml_content = """
name: test
stages:
  - name: step1
    tier: [invalid yaml
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = validate_yaml_file(f.name)

        assert result.valid is False
        assert any("yaml" in e.path.lower() for e in result.errors)

    def test_file_not_found(self):
        """Test error on missing file."""
        result = validate_yaml_file("/nonexistent/path/config.yaml")

        assert result.valid is False
        assert any("file" in e.path.lower() for e in result.errors)

    def test_empty_yaml_file(self):
        """Test error on empty YAML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("")
            f.flush()

            result = validate_yaml_file(f.name)

        assert result.valid is False

    def test_invalid_config_in_yaml(self):
        """Test validation errors in YAML config."""
        yaml_content = """
name: test
default_provider: invalid_provider
stages:
  - name: step1
    tier: super_tier
"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            result = validate_yaml_file(f.name)

        assert result.valid is False
        assert len(result.errors) >= 2  # Invalid provider + invalid tier
