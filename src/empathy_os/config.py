"""
Configuration Management for Empathy Framework

Supports:
- YAML configuration files
- JSON configuration files
- Environment variables
- Default configuration

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class EmpathyConfig:
    """
    Configuration for EmpathyOS instance

    Can be loaded from:
    - YAML file (.empathy.yml, empathy.config.yml)
    - JSON file (.empathy.json, empathy.config.json)
    - Environment variables (EMPATHY_*)
    - Direct instantiation
    """

    # Core settings
    user_id: str = "default_user"
    target_level: int = 3
    confidence_threshold: float = 0.75

    # Trust settings
    trust_building_rate: float = 0.05
    trust_erosion_rate: float = 0.10

    # Persistence settings
    persistence_enabled: bool = True
    persistence_backend: str = "sqlite"  # "sqlite", "json", "none"
    persistence_path: str = "./empathy_data"

    # State management
    state_persistence: bool = True
    state_path: str = "./empathy_state"

    # Metrics settings
    metrics_enabled: bool = True
    metrics_path: str = "./metrics.db"

    # Logging settings
    log_level: str = "INFO"
    log_file: Optional[str] = None
    structured_logging: bool = True

    # Pattern library settings
    pattern_library_enabled: bool = True
    pattern_sharing: bool = True
    pattern_confidence_threshold: float = 0.3

    # Advanced settings
    async_enabled: bool = True
    feedback_loop_monitoring: bool = True
    leverage_point_analysis: bool = True

    # Custom metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_yaml(cls, filepath: str) -> "EmpathyConfig":
        """
        Load configuration from YAML file

        Args:
            filepath: Path to YAML configuration file

        Returns:
            EmpathyConfig instance

        Raises:
            ImportError: If PyYAML is not installed
            FileNotFoundError: If file doesn't exist

        Example:
            >>> config = EmpathyConfig.from_yaml("empathy.config.yml")
            >>> empathy = EmpathyOS(config=config)
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for YAML configuration. " "Install with: pip install pyyaml"
            )

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_json(cls, filepath: str) -> "EmpathyConfig":
        """
        Load configuration from JSON file

        Args:
            filepath: Path to JSON configuration file

        Returns:
            EmpathyConfig instance

        Example:
            >>> config = EmpathyConfig.from_json("empathy.config.json")
            >>> empathy = EmpathyOS(config=config)
        """
        with open(filepath, "r") as f:
            data = json.load(f)

        return cls(**data)

    @classmethod
    def from_env(cls, prefix: str = "EMPATHY_") -> "EmpathyConfig":
        """
        Load configuration from environment variables

        Environment variables should be prefixed with EMPATHY_
        and match config field names in uppercase.

        Example:
            EMPATHY_USER_ID=alice
            EMPATHY_TARGET_LEVEL=4
            EMPATHY_CONFIDENCE_THRESHOLD=0.8

        Args:
            prefix: Environment variable prefix (default: "EMPATHY_")

        Returns:
            EmpathyConfig instance

        Example:
            >>> os.environ["EMPATHY_USER_ID"] = "alice"
            >>> config = EmpathyConfig.from_env()
            >>> print(config.user_id)  # "alice"
        """
        data = {}

        # Get all environment variables with prefix
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # Convert EMPATHY_USER_ID -> user_id
                field_name = key[len(prefix) :].lower()

                # Type conversion based on field name
                if field_name in ("target_level",):
                    data[field_name] = int(value)
                elif field_name in (
                    "confidence_threshold",
                    "trust_building_rate",
                    "trust_erosion_rate",
                    "pattern_confidence_threshold",
                ):
                    data[field_name] = float(value)
                elif field_name in (
                    "persistence_enabled",
                    "state_persistence",
                    "metrics_enabled",
                    "structured_logging",
                    "pattern_library_enabled",
                    "pattern_sharing",
                    "async_enabled",
                    "feedback_loop_monitoring",
                    "leverage_point_analysis",
                ):
                    data[field_name] = value.lower() in ("true", "1", "yes")
                else:
                    data[field_name] = value

        return cls(**data)

    @classmethod
    def from_file(cls, filepath: Optional[str] = None) -> "EmpathyConfig":
        """
        Automatically detect and load configuration from file

        Looks for configuration files in this order:
        1. Provided filepath
        2. .empathy.yml
        3. .empathy.yaml
        4. empathy.config.yml
        5. empathy.config.yaml
        6. .empathy.json
        7. empathy.config.json

        Args:
            filepath: Optional explicit path to config file

        Returns:
            EmpathyConfig instance, or default if no file found

        Example:
            >>> config = EmpathyConfig.from_file()  # Auto-detect
            >>> config = EmpathyConfig.from_file("my-config.yml")
        """
        search_paths = [
            filepath,
            ".empathy.yml",
            ".empathy.yaml",
            "empathy.config.yml",
            "empathy.config.yaml",
            ".empathy.json",
            "empathy.config.json",
        ]

        for path in search_paths:
            if path and Path(path).exists():
                if path.endswith((".yml", ".yaml")):
                    return cls.from_yaml(path)
                elif path.endswith(".json"):
                    return cls.from_json(path)

        # No config file found - return default
        return cls()

    def to_yaml(self, filepath: str):
        """
        Save configuration to YAML file

        Args:
            filepath: Path to save YAML file

        Example:
            >>> config = EmpathyConfig(user_id="alice", target_level=4)
            >>> config.to_yaml("my-config.yml")
        """
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for YAML export. " "Install with: pip install pyyaml"
            )

        data = asdict(self)

        with open(filepath, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def to_json(self, filepath: str, indent: int = 2):
        """
        Save configuration to JSON file

        Args:
            filepath: Path to save JSON file
            indent: JSON indentation (default: 2)

        Example:
            >>> config = EmpathyConfig(user_id="alice", target_level=4)
            >>> config.to_json("my-config.json")
        """
        data = asdict(self)

        with open(filepath, "w") as f:
            json.dump(data, f, indent=indent)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary"""
        return asdict(self)

    def update(self, **kwargs):
        """
        Update configuration fields

        Args:
            **kwargs: Fields to update

        Example:
            >>> config = EmpathyConfig()
            >>> config.update(user_id="bob", target_level=5)
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def merge(self, other: "EmpathyConfig") -> "EmpathyConfig":
        """
        Merge with another configuration (other takes precedence)

        Args:
            other: Configuration to merge

        Returns:
            New merged configuration

        Example:
            >>> base = EmpathyConfig(user_id="alice")
            >>> override = EmpathyConfig(target_level=5)
            >>> merged = base.merge(override)
        """
        # Start with base values
        base_dict = self.to_dict()
        other_dict = other.to_dict()

        # Get default values for comparison
        defaults = EmpathyConfig().to_dict()

        # Only update fields from 'other' that differ from defaults
        for key, value in other_dict.items():
            if value != defaults.get(key):
                base_dict[key] = value

        return EmpathyConfig(**base_dict)

    def validate(self) -> bool:
        """
        Validate configuration values

        Returns:
            True if valid, raises ValueError if invalid

        Raises:
            ValueError: If configuration is invalid
        """
        if self.target_level not in range(1, 6):
            raise ValueError(f"target_level must be 1-5, got {self.target_level}")

        if not 0.0 <= self.confidence_threshold <= 1.0:
            raise ValueError(
                f"confidence_threshold must be 0.0-1.0, got {self.confidence_threshold}"
            )

        if not 0.0 <= self.pattern_confidence_threshold <= 1.0:
            raise ValueError(
                f"pattern_confidence_threshold must be 0.0-1.0, got {self.pattern_confidence_threshold}"
            )

        if self.persistence_backend not in ("sqlite", "json", "none"):
            raise ValueError(
                f"persistence_backend must be 'sqlite', 'json', or 'none', got {self.persistence_backend}"
            )

        return True

    def __repr__(self) -> str:
        """String representation"""
        return (
            f"EmpathyConfig(user_id={self.user_id!r}, target_level={self.target_level}, "
            f"confidence_threshold={self.confidence_threshold})"
        )


def load_config(
    filepath: Optional[str] = None, use_env: bool = True, defaults: Optional[Dict[str, Any]] = None
) -> EmpathyConfig:
    """
    Load configuration with flexible precedence

    Precedence (highest to lowest):
    1. Environment variables (if use_env=True)
    2. Configuration file (if provided/found)
    3. Defaults (if provided)
    4. Built-in defaults

    Args:
        filepath: Optional path to config file
        use_env: Whether to check environment variables (default: True)
        defaults: Optional default values

    Returns:
        EmpathyConfig instance

    Example:
        >>> # Load from file, override with env vars
        >>> config = load_config("empathy.yml", use_env=True)

        >>> # Load with custom defaults
        >>> config = load_config(defaults={"target_level": 4})
    """
    # Start with built-in defaults
    config = EmpathyConfig()

    # Apply custom defaults
    if defaults:
        config.update(**defaults)

    # Load from file if provided/found
    # First check if a file actually exists
    file_found = False
    if filepath and Path(filepath).exists():
        file_found = True
    else:
        # Check default config file locations
        for default_path in [
            ".empathy.yml",
            ".empathy.yaml",
            "empathy.config.yml",
            "empathy.config.yaml",
            ".empathy.json",
            "empathy.config.json",
        ]:
            if Path(default_path).exists():
                file_found = True
                break

    if file_found:
        try:
            file_config = EmpathyConfig.from_file(filepath)
            config = config.merge(file_config)
        except (FileNotFoundError, json.JSONDecodeError):
            pass  # Use defaults

    # Override with environment variables
    if use_env:
        try:
            env_config = EmpathyConfig.from_env()
            config = config.merge(env_config)
        except Exception:
            pass  # Use current config if environment parsing fails

    # Validate final configuration
    config.validate()

    return config
