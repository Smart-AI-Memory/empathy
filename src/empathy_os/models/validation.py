"""
Configuration Validation for Multi-Model Workflows

Provides schema validation for workflow configurations:
- Required field validation
- Type checking
- Value range validation
- Provider/tier existence checks

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass, field
from typing import Any

from .registry import MODEL_REGISTRY, ModelTier


@dataclass
class ValidationError:
    """A single validation error."""

    path: str
    message: str
    severity: str = "error"  # "error" | "warning"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] {self.path}: {self.message}"


@dataclass
class ValidationResult:
    """Result of configuration validation."""

    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[ValidationError] = field(default_factory=list)

    def add_error(self, path: str, message: str) -> None:
        """Add an error."""
        self.errors.append(ValidationError(path, message, "error"))
        self.valid = False

    def add_warning(self, path: str, message: str) -> None:
        """Add a warning."""
        self.warnings.append(ValidationError(path, message, "warning"))

    def __str__(self) -> str:
        lines = []
        if self.valid:
            lines.append("Configuration is valid")
        else:
            lines.append("Configuration has errors")

        for error in self.errors:
            lines.append(f"  {error}")
        for warning in self.warnings:
            lines.append(f"  {warning}")

        return "\n".join(lines)


class ConfigValidator:
    """
    Validator for multi-model workflow configurations.

    Validates:
    - Provider names exist in registry
    - Tier names are valid
    - Required fields are present
    - Numeric values are in valid ranges
    """

    # Valid provider names from registry
    VALID_PROVIDERS = set(MODEL_REGISTRY.keys())

    # Valid tier names
    VALID_TIERS = {tier.value for tier in ModelTier}

    # Schema for workflow config
    WORKFLOW_SCHEMA = {
        "name": {"type": str, "required": True},
        "description": {"type": str, "required": False},
        "default_provider": {"type": str, "required": False},
        "stages": {"type": list, "required": False},
    }

    # Schema for stage config
    STAGE_SCHEMA = {
        "name": {"type": str, "required": True},
        "tier": {"type": str, "required": True},
        "provider": {"type": str, "required": False},
        "timeout_ms": {"type": int, "required": False, "min": 0, "max": 600000},
        "max_retries": {"type": int, "required": False, "min": 0, "max": 10},
    }

    def validate_workflow_config(self, config: dict[str, Any]) -> ValidationResult:
        """
        Validate a workflow configuration dictionary.

        Args:
            config: Workflow configuration dict

        Returns:
            ValidationResult with any errors or warnings
        """
        result = ValidationResult(valid=True)

        # Check required fields
        for field_name, spec in self.WORKFLOW_SCHEMA.items():
            if spec.get("required") and field_name not in config:
                result.add_error(field_name, f"Required field '{field_name}' is missing")

        # Validate types
        for field_name, value in config.items():
            if field_name in self.WORKFLOW_SCHEMA:
                spec = self.WORKFLOW_SCHEMA[field_name]
                expected_type = spec.get("type")
                if expected_type is not None:
                    # Cast to type for isinstance check
                    type_cls = (
                        expected_type if isinstance(expected_type, type) else type(expected_type)
                    )
                    if not isinstance(value, type_cls):
                        type_name = getattr(type_cls, "__name__", str(type_cls))
                        result.add_error(
                            field_name,
                            f"Expected {type_name}, got {type(value).__name__}",
                        )

        # Validate default_provider
        if "default_provider" in config:
            provider = config["default_provider"]
            if provider not in self.VALID_PROVIDERS:
                result.add_error(
                    "default_provider",
                    f"Unknown provider '{provider}'. Valid: {sorted(self.VALID_PROVIDERS)}",
                )

        # Validate stages
        if "stages" in config and isinstance(config["stages"], list):
            for i, stage in enumerate(config["stages"]):
                stage_path = f"stages[{i}]"
                self._validate_stage(stage, stage_path, result)

        return result

    def _validate_stage(self, stage: dict[str, Any], path: str, result: ValidationResult) -> None:
        """Validate a single stage configuration."""
        if not isinstance(stage, dict):
            result.add_error(path, "Stage must be a dictionary")
            return

        # Check required fields
        for field_name, spec in self.STAGE_SCHEMA.items():
            if spec.get("required") and field_name not in stage:
                result.add_error(f"{path}.{field_name}", "Required field is missing")

        # Validate tier
        if "tier" in stage:
            tier = stage["tier"]
            if tier not in self.VALID_TIERS:
                result.add_error(
                    f"{path}.tier",
                    f"Unknown tier '{tier}'. Valid: {sorted(self.VALID_TIERS)}",
                )

        # Validate provider
        if "provider" in stage:
            provider = stage["provider"]
            if provider not in self.VALID_PROVIDERS:
                result.add_error(
                    f"{path}.provider",
                    f"Unknown provider '{provider}'. Valid: {sorted(self.VALID_PROVIDERS)}",
                )

        # Validate numeric ranges
        for field_name in ["timeout_ms", "max_retries"]:
            if field_name in stage:
                value = stage[field_name]
                spec = self.STAGE_SCHEMA[field_name]

                if not isinstance(value, int):
                    result.add_error(
                        f"{path}.{field_name}", f"Expected integer, got {type(value).__name__}"
                    )
                else:
                    min_val = spec.get("min")
                    max_val = spec.get("max")
                    if isinstance(min_val, int | float) and value < min_val:
                        result.add_error(
                            f"{path}.{field_name}",
                            f"Value {value} below minimum {min_val}",
                        )
                    if isinstance(max_val, int | float) and value > max_val:
                        result.add_error(
                            f"{path}.{field_name}",
                            f"Value {value} above maximum {max_val}",
                        )

    def validate_provider_tier(self, provider: str, tier: str) -> ValidationResult:
        """
        Validate that a provider/tier combination exists.

        Args:
            provider: Provider name
            tier: Tier name

        Returns:
            ValidationResult
        """
        result = ValidationResult(valid=True)

        if provider not in self.VALID_PROVIDERS:
            result.add_error("provider", f"Unknown provider '{provider}'")
            return result

        if tier not in self.VALID_TIERS:
            result.add_error("tier", f"Unknown tier '{tier}'")
            return result

        # Check if combination exists in registry
        if tier not in MODEL_REGISTRY.get(provider, {}):
            result.add_warning(
                "provider_tier",
                f"Provider '{provider}' may not have tier '{tier}' configured",
            )

        return result


def validate_config(config: dict[str, Any]) -> ValidationResult:
    """
    Convenience function to validate a workflow config.

    Args:
        config: Configuration dictionary

    Returns:
        ValidationResult
    """
    validator = ConfigValidator()
    return validator.validate_workflow_config(config)


def validate_yaml_file(file_path: str) -> ValidationResult:
    """
    Validate a YAML configuration file.

    Args:
        file_path: Path to YAML file

    Returns:
        ValidationResult
    """
    import yaml

    result = ValidationResult(valid=True)

    try:
        with open(file_path) as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        result.add_error("file", f"File not found: {file_path}")
        return result
    except yaml.YAMLError as e:
        result.add_error("yaml", f"Invalid YAML: {e}")
        return result

    if config is None:
        result.add_error("file", "Empty configuration file")
        return result

    return validate_config(config)
