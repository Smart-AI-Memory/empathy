"""
Linting Configuration Loaders

Reads linting configuration files to understand project standards.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class LintConfig:
    """
    Standardized linting configuration.

    Unified format across all linters.
    """

    linter: str
    config_file: str
    rules: dict[str, Any]
    extends: list[str]
    plugins: list[str]
    severity_overrides: dict[str, str]
    raw_config: dict[str, Any]

    def get_rule_severity(self, rule_name: str) -> str | None:
        """Get configured severity for rule"""
        rule_config = self.rules.get(rule_name)

        if rule_config is None:
            return None

        # Handle different config formats
        if isinstance(rule_config, str):
            return rule_config
        elif isinstance(rule_config, list) and len(rule_config) > 0:
            return str(rule_config[0])
        elif isinstance(rule_config, int):
            # ESLint: 0=off, 1=warn, 2=error
            return ["off", "warn", "error"][rule_config] if 0 <= rule_config <= 2 else None

        return None

    def is_rule_enabled(self, rule_name: str) -> bool:
        """Check if rule is enabled"""
        severity = self.get_rule_severity(rule_name)
        return severity not in [None, "off", "0", 0]


class BaseConfigLoader:
    """Base class for configuration loaders"""

    def __init__(self, linter_name: str):
        self.linter_name = linter_name

    def load(self, config_path: str) -> LintConfig:
        """Load configuration from file"""
        raise NotImplementedError

    def find_config(self, start_dir: str) -> str | None:
        """Find config file starting from directory"""
        raise NotImplementedError


class ESLintConfigLoader(BaseConfigLoader):
    """
    Load ESLint configuration.

    Supports:
    - .eslintrc.json
    - .eslintrc.js (limited - JSON portion only)
    - .eslintrc.yml (via JSON-compatible subset)
    - package.json (eslintConfig section)
    """

    CONFIG_FILES = [
        ".eslintrc.json",
        ".eslintrc",
        ".eslintrc.js",
        ".eslintrc.yml",
        ".eslintrc.yaml",
        "package.json",
    ]

    def __init__(self):
        super().__init__("eslint")

    def find_config(self, start_dir: str) -> str | None:
        """Find ESLint config file"""
        current = Path(start_dir).resolve()

        while True:
            for config_file in self.CONFIG_FILES:
                config_path = current / config_file
                if config_path.exists():
                    return str(config_path)

            # Stop at root
            if current.parent == current:
                break

            current = current.parent

        return None

    def load(self, config_path: str) -> LintConfig:
        """Load ESLint configuration"""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        # Handle package.json
        if path.name == "package.json":
            return self._load_package_json(path)

        # Handle .js files (try to extract JSON)
        if path.suffix == ".js":
            return self._load_js_config(path)

        # Handle JSON files
        with open(path) as f:
            config_data = json.load(f)

        return self._parse_config(config_data, str(path))

    def _load_package_json(self, path: Path) -> LintConfig:
        """Load ESLint config from package.json"""
        with open(path) as f:
            package_data = json.load(f)

        eslint_config = package_data.get("eslintConfig", {})
        return self._parse_config(eslint_config, str(path))

    def _load_js_config(self, path: Path) -> LintConfig:
        """
        Load ESLint config from .js file.

        Limited support - extracts JSON-like objects.
        """
        with open(path) as f:
            content = f.read()

        # Try to find module.exports = { ... }
        match = re.search(r"module\.exports\s*=\s*(\{[\s\S]*?\})\s*;?", content)

        if match:
            json_str = match.group(1)
            # Try to convert JS object to JSON
            # This is a simplified approach - may not work for complex configs
            try:
                config_data = json.loads(json_str)
                return self._parse_config(config_data, str(path))
            except json.JSONDecodeError:
                # Return minimal config
                return LintConfig(
                    linter=self.linter_name,
                    config_file=str(path),
                    rules={},
                    extends=[],
                    plugins=[],
                    severity_overrides={},
                    raw_config={"note": "JS config - limited parsing"},
                )

        raise ValueError(f"Could not parse JS config: {path}") from None

    def _parse_config(self, config_data: dict, config_file: str) -> LintConfig:
        """Parse ESLint config data"""
        return LintConfig(
            linter=self.linter_name,
            config_file=config_file,
            rules=config_data.get("rules", {}),
            extends=self._normalize_extends(config_data.get("extends")),
            plugins=config_data.get("plugins", []),
            severity_overrides={},
            raw_config=config_data,
        )

    def _normalize_extends(self, extends_value: Any) -> list[str]:
        """Normalize extends to list"""
        if extends_value is None:
            return []
        elif isinstance(extends_value, str):
            return [extends_value]
        elif isinstance(extends_value, list):
            return extends_value
        return []


class PylintConfigLoader(BaseConfigLoader):
    """
    Load Pylint configuration.

    Supports:
    - pyproject.toml (tool.pylint section)
    - .pylintrc
    - pylintrc
    - setup.cfg
    """

    def __init__(self):
        super().__init__("pylint")

    def find_config(self, start_dir: str) -> str | None:
        """Find Pylint config file"""
        current = Path(start_dir).resolve()

        config_files = ["pyproject.toml", ".pylintrc", "pylintrc", "setup.cfg"]

        while True:
            for config_file in config_files:
                config_path = current / config_file
                if config_path.exists():
                    return str(config_path)

            if current.parent == current:
                break

            current = current.parent

        return None

    def load(self, config_path: str) -> LintConfig:
        """Load Pylint configuration"""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        if path.name == "pyproject.toml":
            return self._load_pyproject(path)
        else:
            return self._load_ini_style(path)

    def _load_pyproject(self, path: Path) -> LintConfig:
        """Load from pyproject.toml"""
        try:
            import tomli
        except ImportError:
            # Fallback for Python 3.11+
            try:
                import tomllib as tomli
            except ImportError as e:
                raise ImportError("tomli or tomllib required for pyproject.toml") from e

        with open(path, "rb") as f:
            data = tomli.load(f)

        pylint_config = data.get("tool", {}).get("pylint", {})

        # Extract rules
        rules = {}
        if "enable" in pylint_config:
            for rule in pylint_config["enable"]:
                rules[rule] = "enabled"
        if "disable" in pylint_config:
            for rule in pylint_config["disable"]:
                rules[rule] = "disabled"

        # Get messages control
        messages_control = pylint_config.get("MESSAGES CONTROL", {})
        if "disable" in messages_control:
            for rule in messages_control["disable"].split(","):
                rules[rule.strip()] = "disabled"

        return LintConfig(
            linter=self.linter_name,
            config_file=str(path),
            rules=rules,
            extends=[],
            plugins=pylint_config.get("load-plugins", []),
            severity_overrides={},
            raw_config=pylint_config,
        )

    def _load_ini_style(self, path: Path) -> LintConfig:
        """Load from .pylintrc or setup.cfg"""
        import configparser

        config = configparser.ConfigParser()
        config.read(path)

        rules = {}

        # Check for disabled rules
        if config.has_option("MESSAGES CONTROL", "disable"):
            disabled = config.get("MESSAGES CONTROL", "disable")
            for rule in disabled.split(","):
                rules[rule.strip()] = "disabled"

        if config.has_option("MESSAGES CONTROL", "enable"):
            enabled = config.get("MESSAGES CONTROL", "enable")
            for rule in enabled.split(","):
                rules[rule.strip()] = "enabled"

        plugins = []
        if config.has_option("MASTER", "load-plugins"):
            plugins = config.get("MASTER", "load-plugins").split(",")

        return LintConfig(
            linter=self.linter_name,
            config_file=str(path),
            rules=rules,
            extends=[],
            plugins=[p.strip() for p in plugins],
            severity_overrides={},
            raw_config=dict(config.items()) if hasattr(config, "items") else {},
        )


class TypeScriptConfigLoader(BaseConfigLoader):
    """
    Load TypeScript configuration.

    Supports tsconfig.json
    """

    def __init__(self):
        super().__init__("typescript")

    def find_config(self, start_dir: str) -> str | None:
        """Find tsconfig.json"""
        current = Path(start_dir).resolve()

        while True:
            tsconfig = current / "tsconfig.json"
            if tsconfig.exists():
                return str(tsconfig)

            if current.parent == current:
                break

            current = current.parent

        return None

    def load(self, config_path: str) -> LintConfig:
        """Load TypeScript configuration"""
        path = Path(config_path)

        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(path) as f:
            # TypeScript allows comments in JSON
            content = f.read()
            # Remove comments (simplified)
            content = re.sub(r"//.*?\n", "\n", content)
            content = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

            config_data = json.loads(content)

        compiler_options = config_data.get("compilerOptions", {})

        # Convert compiler options to "rules"
        rules = {}
        for option, value in compiler_options.items():
            rules[option] = value

        return LintConfig(
            linter=self.linter_name,
            config_file=str(path),
            rules=rules,
            extends=[config_data.get("extends", "")],
            plugins=[],
            severity_overrides={},
            raw_config=config_data,
        )


class ConfigLoaderFactory:
    """Factory for creating config loaders"""

    _loaders = {
        "eslint": ESLintConfigLoader,
        "pylint": PylintConfigLoader,
        "typescript": TypeScriptConfigLoader,
        "tsc": TypeScriptConfigLoader,
    }

    @classmethod
    def create(cls, linter_name: str) -> BaseConfigLoader:
        """Create config loader for linter"""
        loader_class = cls._loaders.get(linter_name.lower())

        if not loader_class:
            raise ValueError(
                f"Unsupported linter config: {linter_name}. "
                f"Supported: {', '.join(cls._loaders.keys())}"
            )

        return loader_class()

    @classmethod
    def get_supported_linters(cls) -> list[str]:
        """Get supported linters"""
        return list(cls._loaders.keys())


def load_config(
    linter_name: str, config_path: str | None = None, start_dir: str | None = None
) -> LintConfig | None:
    """
    Load linting configuration.

    Args:
        linter_name: Name of linter
        config_path: Explicit config path (optional)
        start_dir: Directory to start search from (optional)

    Returns:
        LintConfig or None if not found

    Example:
        >>> config = load_config("eslint", start_dir="/path/to/project")
        >>> if config:
        ...     print(f"Rules: {len(config.rules)}")
    """
    loader = ConfigLoaderFactory.create(linter_name)

    # If explicit path provided
    if config_path:
        return loader.load(config_path)

    # Otherwise, search for config
    if start_dir:
        found_config = loader.find_config(start_dir)
        if found_config:
            return loader.load(found_config)

    return None
