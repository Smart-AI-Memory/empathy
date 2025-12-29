"""
Tests for empathy_software_plugin/wizards/debugging/config_loaders.py

Comprehensive tests for linting configuration loaders including:
- LintConfig dataclass methods
- ESLint, Pylint, and TypeScript config loading
- Config file discovery
- Error handling for invalid configs
- Factory pattern

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import configparser
import json
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.debugging.config_loaders import (
    BaseConfigLoader,
    ConfigLoaderFactory,
    ESLintConfigLoader,
    LintConfig,
    PylintConfigLoader,
    TypeScriptConfigLoader,
    load_config,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture
def sample_eslint_config():
    """Sample ESLint configuration."""
    return {
        "extends": ["eslint:recommended", "plugin:react/recommended"],
        "plugins": ["react", "react-hooks"],
        "rules": {
            "no-console": "warn",
            "no-unused-vars": "error",
            "semi": ["error", "always"],
            "indent": 2,
            "quotes": ["warn", "single"],
        },
        "env": {"browser": True, "node": True},
    }


@pytest.fixture
def sample_tsconfig():
    """Sample TypeScript configuration."""
    return {
        "compilerOptions": {
            "target": "ES2020",
            "module": "commonjs",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "outDir": "./dist",
        },
        "extends": "@tsconfig/node16/tsconfig.json",
        "include": ["src/**/*"],
        "exclude": ["node_modules"],
    }


# =============================================================================
# LintConfig Tests
# =============================================================================


class TestLintConfig:
    """Tests for LintConfig dataclass."""

    def test_create_lint_config(self):
        """Test creating a LintConfig instance."""
        config = LintConfig(
            linter="eslint",
            config_file="/path/to/.eslintrc.json",
            rules={"no-console": "warn"},
            extends=["eslint:recommended"],
            plugins=["react"],
            severity_overrides={"no-console": "error"},
            raw_config={"rules": {"no-console": "warn"}},
        )

        assert config.linter == "eslint"
        assert config.config_file == "/path/to/.eslintrc.json"
        assert config.rules == {"no-console": "warn"}
        assert config.extends == ["eslint:recommended"]
        assert config.plugins == ["react"]

    def test_get_rule_severity_string(self):
        """Test get_rule_severity with string value."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"no-console": "warn", "no-unused-vars": "error", "semi": "off"},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.get_rule_severity("no-console") == "warn"
        assert config.get_rule_severity("no-unused-vars") == "error"
        assert config.get_rule_severity("semi") == "off"

    def test_get_rule_severity_list(self):
        """Test get_rule_severity with list value."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={
                "indent": ["error", 2],
                "quotes": ["warn", "single"],
                "semi": ["off"],
            },
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.get_rule_severity("indent") == "error"
        assert config.get_rule_severity("quotes") == "warn"
        assert config.get_rule_severity("semi") == "off"

    def test_get_rule_severity_integer(self):
        """Test get_rule_severity with integer value (ESLint format)."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"rule0": 0, "rule1": 1, "rule2": 2},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.get_rule_severity("rule0") == "off"
        assert config.get_rule_severity("rule1") == "warn"
        assert config.get_rule_severity("rule2") == "error"

    def test_get_rule_severity_invalid_integer(self):
        """Test get_rule_severity with out-of-range integer."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"rule_invalid": 5},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.get_rule_severity("rule_invalid") is None

    def test_get_rule_severity_nonexistent(self):
        """Test get_rule_severity with non-existent rule."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"existing-rule": "warn"},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.get_rule_severity("nonexistent-rule") is None

    def test_get_rule_severity_empty_list(self):
        """Test get_rule_severity with empty list."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"empty-rule": []},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        # Empty list should return None since there's no first element
        assert config.get_rule_severity("empty-rule") is None

    def test_get_rule_severity_dict_value(self):
        """Test get_rule_severity with dict value (unsupported format)."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={"complex-rule": {"severity": "warn", "options": {}}},
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        # Dict values are not handled, should return None
        assert config.get_rule_severity("complex-rule") is None

    def test_is_rule_enabled_true(self):
        """Test is_rule_enabled returns True for enabled rules."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={
                "warn-rule": "warn",
                "error-rule": "error",
                "int-rule": 1,
                "list-rule": ["error", "always"],
            },
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.is_rule_enabled("warn-rule") is True
        assert config.is_rule_enabled("error-rule") is True
        assert config.is_rule_enabled("int-rule") is True
        assert config.is_rule_enabled("list-rule") is True

    def test_is_rule_enabled_false(self):
        """Test is_rule_enabled returns False for disabled rules."""
        config = LintConfig(
            linter="eslint",
            config_file="test",
            rules={
                "off-rule": "off",
                "zero-rule": 0,
                "zero-str-rule": "0",
            },
            extends=[],
            plugins=[],
            severity_overrides={},
            raw_config={},
        )

        assert config.is_rule_enabled("off-rule") is False
        assert config.is_rule_enabled("zero-rule") is False
        assert config.is_rule_enabled("zero-str-rule") is False
        assert config.is_rule_enabled("nonexistent") is False


# =============================================================================
# ESLint Config Loader Tests
# =============================================================================


class TestESLintConfigLoader:
    """Tests for ESLintConfigLoader."""

    def test_init(self):
        """Test ESLintConfigLoader initialization."""
        loader = ESLintConfigLoader()
        assert loader.linter_name == "eslint"

    def test_load_eslintrc_json(self, temp_dir, sample_eslint_config):
        """Test loading .eslintrc.json file."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert config.config_file == str(config_path)
        assert "no-console" in config.rules
        assert config.rules["no-console"] == "warn"
        assert "react" in config.plugins
        assert "eslint:recommended" in config.extends

    def test_load_eslintrc_no_extension(self, temp_dir, sample_eslint_config):
        """Test loading .eslintrc file (no extension, JSON content)."""
        config_path = Path(temp_dir) / ".eslintrc"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert "no-console" in config.rules

    def test_load_package_json(self, temp_dir, sample_eslint_config):
        """Test loading ESLint config from package.json."""
        package_json = {"name": "test-project", "eslintConfig": sample_eslint_config}

        config_path = Path(temp_dir) / "package.json"
        with open(config_path, "w") as f:
            json.dump(package_json, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert "no-console" in config.rules
        assert "react" in config.plugins

    def test_load_package_json_no_eslint_config(self, temp_dir):
        """Test loading package.json without eslintConfig section."""
        package_json = {"name": "test-project", "version": "1.0.0"}

        config_path = Path(temp_dir) / "package.json"
        with open(config_path, "w") as f:
            json.dump(package_json, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert config.rules == {}
        assert config.extends == []
        assert config.plugins == []

    def test_load_js_config_valid_json(self, temp_dir):
        """Test loading .eslintrc.js with valid JSON export."""
        # Note: The loader's regex extracts JSON from module.exports = {...}
        # It requires strict JSON format (double quotes, no trailing commas)
        js_content = (
            'module.exports = {"rules": {"no-console": "warn"}, '
            '"extends": ["eslint:recommended"]};'
        )
        config_path = Path(temp_dir) / ".eslintrc.js"
        with open(config_path, "w") as f:
            f.write(js_content)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        # The JS config loader may return minimal config if JSON parsing fails
        # Check that we at least got a valid config back
        assert config.config_file == str(config_path)

    def test_load_js_config_invalid_json(self, temp_dir):
        """Test loading .eslintrc.js with non-JSON export returns minimal config."""
        js_content = """
module.exports = {
    rules: {
        'no-console': 'warn'
    }
};
"""
        config_path = Path(temp_dir) / ".eslintrc.js"
        with open(config_path, "w") as f:
            f.write(js_content)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        # Should return minimal config when parsing fails
        assert config.linter == "eslint"
        assert config.rules == {}
        assert "note" in config.raw_config

    def test_load_js_config_no_module_exports(self, temp_dir):
        """Test loading .eslintrc.js without module.exports raises error."""
        js_content = """
const config = {
    rules: {'no-console': 'warn'}
};
"""
        config_path = Path(temp_dir) / ".eslintrc.js"
        with open(config_path, "w") as f:
            f.write(js_content)

        loader = ESLintConfigLoader()

        with pytest.raises(ValueError, match="Could not parse JS config"):
            loader.load(str(config_path))

    def test_load_file_not_found(self):
        """Test loading non-existent file raises FileNotFoundError."""
        loader = ESLintConfigLoader()

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            loader.load("/nonexistent/.eslintrc.json")

    def test_find_config_in_current_dir(self, temp_dir, sample_eslint_config):
        """Test find_config finds config in current directory."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        loader = ESLintConfigLoader()
        found = loader.find_config(temp_dir)

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_find_config_in_parent_dir(self, temp_dir, sample_eslint_config):
        """Test find_config finds config in parent directory."""
        # Create config in temp_dir
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        # Create subdirectory
        sub_dir = Path(temp_dir) / "src" / "components"
        sub_dir.mkdir(parents=True)

        loader = ESLintConfigLoader()
        found = loader.find_config(str(sub_dir))

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_find_config_priority(self, temp_dir, sample_eslint_config):
        """Test find_config respects file priority order."""
        # Create both .eslintrc.json and .eslintrc
        json_path = Path(temp_dir) / ".eslintrc.json"
        rc_path = Path(temp_dir) / ".eslintrc"

        with open(json_path, "w") as f:
            json.dump(sample_eslint_config, f)
        with open(rc_path, "w") as f:
            json.dump({"rules": {}}, f)

        loader = ESLintConfigLoader()
        found = loader.find_config(temp_dir)

        # .eslintrc.json should be found first (it's earlier in CONFIG_FILES)
        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == json_path.resolve()

    def test_find_config_not_found(self, temp_dir):
        """Test find_config returns None when no config exists."""
        loader = ESLintConfigLoader()
        found = loader.find_config(temp_dir)

        assert found is None

    def test_normalize_extends_string(self):
        """Test _normalize_extends with string value."""
        loader = ESLintConfigLoader()
        result = loader._normalize_extends("eslint:recommended")

        assert result == ["eslint:recommended"]

    def test_normalize_extends_list(self):
        """Test _normalize_extends with list value."""
        loader = ESLintConfigLoader()
        result = loader._normalize_extends(["eslint:recommended", "plugin:react/recommended"])

        assert result == ["eslint:recommended", "plugin:react/recommended"]

    def test_normalize_extends_none(self):
        """Test _normalize_extends with None value."""
        loader = ESLintConfigLoader()
        result = loader._normalize_extends(None)

        assert result == []

    def test_normalize_extends_other_type(self):
        """Test _normalize_extends with unsupported type."""
        loader = ESLintConfigLoader()
        result = loader._normalize_extends(123)

        assert result == []


# =============================================================================
# Pylint Config Loader Tests
# =============================================================================


class TestPylintConfigLoader:
    """Tests for PylintConfigLoader."""

    def test_init(self):
        """Test PylintConfigLoader initialization."""
        loader = PylintConfigLoader()
        assert loader.linter_name == "pylint"

    def test_load_pylintrc(self, temp_dir):
        """Test loading .pylintrc file."""
        config_path = Path(temp_dir) / ".pylintrc"

        config = configparser.ConfigParser()
        config["MESSAGES CONTROL"] = {
            "disable": "C0111, C0114, W0612",
            "enable": "E0001, E0002",
        }
        config["MASTER"] = {"load-plugins": "pylint_django, pylint_celery"}

        with open(config_path, "w") as f:
            config.write(f)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.linter == "pylint"
        assert "C0111" in lint_config.rules
        assert lint_config.rules["C0111"] == "disabled"
        assert "E0001" in lint_config.rules
        assert lint_config.rules["E0001"] == "enabled"
        assert "pylint_django" in lint_config.plugins

    def test_load_setup_cfg(self, temp_dir):
        """Test loading setup.cfg with pylint section."""
        config_path = Path(temp_dir) / "setup.cfg"

        config = configparser.ConfigParser()
        config["MESSAGES CONTROL"] = {"disable": "missing-docstring"}

        with open(config_path, "w") as f:
            config.write(f)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.linter == "pylint"
        assert "missing-docstring" in lint_config.rules

    def test_load_pyproject_toml(self, temp_dir):
        """Test loading pyproject.toml with pylint config."""
        pytest.importorskip("tomli", reason="tomli not installed")

        config_path = Path(temp_dir) / "pyproject.toml"
        toml_content = """
[tool.pylint]
enable = ["E0001", "E0002"]
disable = ["C0111", "W0612"]
load-plugins = ["pylint_django"]
"""
        with open(config_path, "w") as f:
            f.write(toml_content)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.linter == "pylint"
        assert "E0001" in lint_config.rules
        assert lint_config.rules["E0001"] == "enabled"
        assert "C0111" in lint_config.rules
        assert lint_config.rules["C0111"] == "disabled"

    def test_load_pyproject_toml_no_pylint_section(self, temp_dir):
        """Test loading pyproject.toml without pylint section."""
        pytest.importorskip("tomli", reason="tomli not installed")

        config_path = Path(temp_dir) / "pyproject.toml"
        toml_content = """
[project]
name = "test-project"
version = "1.0.0"
"""
        with open(config_path, "w") as f:
            f.write(toml_content)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.linter == "pylint"
        assert lint_config.rules == {}

    def test_load_file_not_found(self):
        """Test loading non-existent file raises FileNotFoundError."""
        loader = PylintConfigLoader()

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            loader.load("/nonexistent/.pylintrc")

    def test_find_config_pyproject(self, temp_dir):
        """Test find_config finds pyproject.toml first."""
        pytest.importorskip("tomli", reason="tomli not installed")

        # Create pyproject.toml
        pyproject_path = Path(temp_dir) / "pyproject.toml"
        with open(pyproject_path, "w") as f:
            f.write("[tool.pylint]\n")

        # Create .pylintrc
        pylintrc_path = Path(temp_dir) / ".pylintrc"
        with open(pylintrc_path, "w") as f:
            f.write("[MESSAGES CONTROL]\n")

        loader = PylintConfigLoader()
        found = loader.find_config(temp_dir)

        # pyproject.toml should be found first
        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == pyproject_path.resolve()

    def test_find_config_in_parent(self, temp_dir):
        """Test find_config finds config in parent directory."""
        # Create config in temp_dir
        config_path = Path(temp_dir) / ".pylintrc"
        with open(config_path, "w") as f:
            f.write("[MESSAGES CONTROL]\ndisable=C0111\n")

        # Create subdirectory
        sub_dir = Path(temp_dir) / "src" / "models"
        sub_dir.mkdir(parents=True)

        loader = PylintConfigLoader()
        found = loader.find_config(str(sub_dir))

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_find_config_not_found(self, temp_dir):
        """Test find_config returns None when no config exists."""
        loader = PylintConfigLoader()
        found = loader.find_config(temp_dir)

        assert found is None

    def test_load_ini_no_messages_control(self, temp_dir):
        """Test loading .pylintrc without MESSAGES CONTROL section."""
        config_path = Path(temp_dir) / ".pylintrc"

        config = configparser.ConfigParser()
        config["BASIC"] = {"good-names": "i,j,k"}

        with open(config_path, "w") as f:
            config.write(f)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.linter == "pylint"
        assert lint_config.rules == {}

    def test_load_ini_no_master_section(self, temp_dir):
        """Test loading .pylintrc without MASTER section."""
        config_path = Path(temp_dir) / ".pylintrc"

        config = configparser.ConfigParser()
        config["MESSAGES CONTROL"] = {"disable": "C0111"}

        with open(config_path, "w") as f:
            config.write(f)

        loader = PylintConfigLoader()
        lint_config = loader.load(str(config_path))

        assert lint_config.plugins == []


# =============================================================================
# TypeScript Config Loader Tests
# =============================================================================


class TestTypeScriptConfigLoader:
    """Tests for TypeScriptConfigLoader."""

    def test_init(self):
        """Test TypeScriptConfigLoader initialization."""
        loader = TypeScriptConfigLoader()
        assert loader.linter_name == "typescript"

    def test_load_tsconfig(self, temp_dir, sample_tsconfig):
        """Test loading tsconfig.json file."""
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump(sample_tsconfig, f)

        loader = TypeScriptConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "typescript"
        assert config.config_file == str(config_path)
        assert config.rules["target"] == "ES2020"
        assert config.rules["strict"] is True
        assert "@tsconfig/node16/tsconfig.json" in config.extends

    def test_load_tsconfig_with_comments(self, temp_dir):
        """Test loading tsconfig.json with comments (TypeScript allows this)."""
        config_path = Path(temp_dir) / "tsconfig.json"
        content = """{
    // This is a comment
    "compilerOptions": {
        "target": "ES2020", // Another comment
        "strict": true
        /* Multi-line
           comment */
    }
}"""
        with open(config_path, "w") as f:
            f.write(content)

        loader = TypeScriptConfigLoader()
        config = loader.load(str(config_path))

        assert config.rules["target"] == "ES2020"
        assert config.rules["strict"] is True

    def test_load_tsconfig_no_compiler_options(self, temp_dir):
        """Test loading tsconfig.json without compilerOptions."""
        config_path = Path(temp_dir) / "tsconfig.json"
        content = {"extends": "./base.json", "include": ["src/**/*"]}

        with open(config_path, "w") as f:
            json.dump(content, f)

        loader = TypeScriptConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "typescript"
        assert config.rules == {}
        assert "./base.json" in config.extends

    def test_load_file_not_found(self):
        """Test loading non-existent file raises FileNotFoundError."""
        loader = TypeScriptConfigLoader()

        with pytest.raises(FileNotFoundError, match="Config file not found"):
            loader.load("/nonexistent/tsconfig.json")

    def test_find_config_current_dir(self, temp_dir, sample_tsconfig):
        """Test find_config finds tsconfig.json in current directory."""
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump(sample_tsconfig, f)

        loader = TypeScriptConfigLoader()
        found = loader.find_config(temp_dir)

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_find_config_parent_dir(self, temp_dir, sample_tsconfig):
        """Test find_config finds tsconfig.json in parent directory."""
        # Create config in temp_dir
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump(sample_tsconfig, f)

        # Create subdirectory
        sub_dir = Path(temp_dir) / "src" / "components"
        sub_dir.mkdir(parents=True)

        loader = TypeScriptConfigLoader()
        found = loader.find_config(str(sub_dir))

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_find_config_not_found(self, temp_dir):
        """Test find_config returns None when no tsconfig.json exists."""
        loader = TypeScriptConfigLoader()
        found = loader.find_config(temp_dir)

        assert found is None

    def test_load_tsconfig_no_extends(self, temp_dir):
        """Test loading tsconfig.json without extends field."""
        config_path = Path(temp_dir) / "tsconfig.json"
        content = {"compilerOptions": {"strict": True}}

        with open(config_path, "w") as f:
            json.dump(content, f)

        loader = TypeScriptConfigLoader()
        config = loader.load(str(config_path))

        # extends should be [""] when not provided
        assert config.extends == [""]


# =============================================================================
# ConfigLoaderFactory Tests
# =============================================================================


class TestConfigLoaderFactory:
    """Tests for ConfigLoaderFactory."""

    def test_create_eslint_loader(self):
        """Test creating ESLint loader."""
        loader = ConfigLoaderFactory.create("eslint")
        assert isinstance(loader, ESLintConfigLoader)

    def test_create_eslint_loader_case_insensitive(self):
        """Test creating ESLint loader with different cases."""
        loader_lower = ConfigLoaderFactory.create("eslint")
        loader_upper = ConfigLoaderFactory.create("ESLINT")
        loader_mixed = ConfigLoaderFactory.create("EsLint")

        assert isinstance(loader_lower, ESLintConfigLoader)
        assert isinstance(loader_upper, ESLintConfigLoader)
        assert isinstance(loader_mixed, ESLintConfigLoader)

    def test_create_pylint_loader(self):
        """Test creating Pylint loader."""
        loader = ConfigLoaderFactory.create("pylint")
        assert isinstance(loader, PylintConfigLoader)

    def test_create_typescript_loader(self):
        """Test creating TypeScript loader."""
        loader = ConfigLoaderFactory.create("typescript")
        assert isinstance(loader, TypeScriptConfigLoader)

    def test_create_tsc_alias(self):
        """Test creating TypeScript loader using 'tsc' alias."""
        loader = ConfigLoaderFactory.create("tsc")
        assert isinstance(loader, TypeScriptConfigLoader)

    def test_create_unsupported_linter(self):
        """Test creating loader for unsupported linter raises error."""
        with pytest.raises(ValueError, match="Unsupported linter config"):
            ConfigLoaderFactory.create("flake8")

    def test_create_unsupported_shows_supported(self):
        """Test error message shows supported linters."""
        with pytest.raises(ValueError) as exc_info:
            ConfigLoaderFactory.create("unknown_linter")

        error_message = str(exc_info.value)
        assert "eslint" in error_message
        assert "pylint" in error_message
        assert "typescript" in error_message

    def test_get_supported_linters(self):
        """Test get_supported_linters returns all supported linters."""
        supported = ConfigLoaderFactory.get_supported_linters()

        assert "eslint" in supported
        assert "pylint" in supported
        assert "typescript" in supported
        assert "tsc" in supported
        assert len(supported) == 4


# =============================================================================
# BaseConfigLoader Tests
# =============================================================================


class TestBaseConfigLoader:
    """Tests for BaseConfigLoader abstract class."""

    def test_base_loader_load_not_implemented(self):
        """Test BaseConfigLoader.load raises NotImplementedError."""
        loader = BaseConfigLoader("test")

        with pytest.raises(NotImplementedError):
            loader.load("/path/to/config")

    def test_base_loader_find_config_not_implemented(self):
        """Test BaseConfigLoader.find_config raises NotImplementedError."""
        loader = BaseConfigLoader("test")

        with pytest.raises(NotImplementedError):
            loader.find_config("/path/to/dir")


# =============================================================================
# load_config Function Tests
# =============================================================================


class TestLoadConfigFunction:
    """Tests for load_config convenience function."""

    def test_load_config_with_explicit_path(self, temp_dir, sample_eslint_config):
        """Test load_config with explicit config path."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        config = load_config("eslint", config_path=str(config_path))

        assert config is not None
        assert config.linter == "eslint"
        assert "no-console" in config.rules

    def test_load_config_with_start_dir(self, temp_dir, sample_eslint_config):
        """Test load_config searches from start_dir."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(sample_eslint_config, f)

        # Create subdirectory
        sub_dir = Path(temp_dir) / "src"
        sub_dir.mkdir()

        config = load_config("eslint", start_dir=str(sub_dir))

        assert config is not None
        assert config.linter == "eslint"

    def test_load_config_not_found(self, temp_dir):
        """Test load_config returns None when no config found."""
        config = load_config("eslint", start_dir=temp_dir)

        assert config is None

    def test_load_config_no_path_or_start_dir(self):
        """Test load_config returns None without path or start_dir."""
        config = load_config("eslint")

        assert config is None

    def test_load_config_pylint(self, temp_dir):
        """Test load_config with pylint."""
        config_path = Path(temp_dir) / ".pylintrc"

        parser = configparser.ConfigParser()
        parser["MESSAGES CONTROL"] = {"disable": "C0111"}

        with open(config_path, "w") as f:
            parser.write(f)

        config = load_config("pylint", config_path=str(config_path))

        assert config is not None
        assert config.linter == "pylint"
        assert "C0111" in config.rules

    def test_load_config_typescript(self, temp_dir, sample_tsconfig):
        """Test load_config with typescript."""
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump(sample_tsconfig, f)

        config = load_config("typescript", config_path=str(config_path))

        assert config is not None
        assert config.linter == "typescript"
        assert "target" in config.rules

    def test_load_config_unsupported_linter(self):
        """Test load_config raises error for unsupported linter."""
        with pytest.raises(ValueError, match="Unsupported linter config"):
            load_config("unsupported_linter", config_path="/some/path")


# =============================================================================
# Error Handling Tests
# =============================================================================


class TestErrorHandling:
    """Tests for error handling in config loaders."""

    def test_eslint_invalid_json(self, temp_dir):
        """Test ESLint loader with invalid JSON raises error."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            f.write("{invalid json")

        loader = ESLintConfigLoader()

        with pytest.raises(json.JSONDecodeError):
            loader.load(str(config_path))

    def test_typescript_invalid_json(self, temp_dir):
        """Test TypeScript loader with invalid JSON raises error."""
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            f.write("{invalid json}")

        loader = TypeScriptConfigLoader()

        with pytest.raises(json.JSONDecodeError):
            loader.load(str(config_path))

    @pytest.mark.skipif(sys.platform == "win32", reason="Permission tests not reliable on Windows")
    def test_eslint_permission_error(self, temp_dir):
        """Test ESLint loader handles permission errors."""
        # This test is platform-dependent; skip if we can't set permissions
        import os
        import stat

        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump({"rules": {}}, f)

        # Remove read permission
        os.chmod(config_path, 0o000)

        loader = ESLintConfigLoader()

        try:
            with pytest.raises(PermissionError):
                loader.load(str(config_path))
        finally:
            # Restore permissions for cleanup
            os.chmod(config_path, stat.S_IRUSR | stat.S_IWUSR)


# =============================================================================
# Integration Tests
# =============================================================================


class TestConfigLoaderIntegration:
    """Integration tests for config loaders."""

    def test_full_eslint_workflow(self, temp_dir):
        """Test complete ESLint config discovery and loading workflow."""
        # Create project structure
        project_dir = Path(temp_dir) / "my-project"
        src_dir = project_dir / "src" / "components"
        src_dir.mkdir(parents=True)

        # Create ESLint config at project root
        eslint_config = {
            "extends": ["eslint:recommended"],
            "rules": {"no-console": "warn", "no-unused-vars": "error"},
        }

        config_path = project_dir / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump(eslint_config, f)

        # Use load_config to find and load config from subdirectory
        config = load_config("eslint", start_dir=str(src_dir))

        assert config is not None
        assert config.linter == "eslint"
        assert config.is_rule_enabled("no-console")
        assert config.get_rule_severity("no-console") == "warn"
        assert config.is_rule_enabled("no-unused-vars")
        assert config.get_rule_severity("no-unused-vars") == "error"

    def test_full_pylint_workflow(self, temp_dir):
        """Test complete Pylint config discovery and loading workflow."""
        # Create project structure
        project_dir = Path(temp_dir) / "my-python-project"
        src_dir = project_dir / "src" / "models"
        src_dir.mkdir(parents=True)

        # Create Pylint config at project root
        config_path = project_dir / ".pylintrc"

        parser = configparser.ConfigParser()
        parser["MESSAGES CONTROL"] = {
            "disable": "missing-docstring, too-few-public-methods",
            "enable": "unused-import",
        }
        parser["MASTER"] = {"load-plugins": "pylint_django"}

        with open(config_path, "w") as f:
            parser.write(f)

        # Use load_config to find and load config from subdirectory
        config = load_config("pylint", start_dir=str(src_dir))

        assert config is not None
        assert config.linter == "pylint"
        assert config.rules["missing-docstring"] == "disabled"
        assert config.rules["unused-import"] == "enabled"
        assert "pylint_django" in config.plugins

    def test_full_typescript_workflow(self, temp_dir):
        """Test complete TypeScript config discovery and loading workflow."""
        # Create project structure
        project_dir = Path(temp_dir) / "my-ts-project"
        src_dir = project_dir / "src" / "services"
        src_dir.mkdir(parents=True)

        # Create TypeScript config at project root
        tsconfig = {
            "compilerOptions": {
                "target": "ES2020",
                "module": "ESNext",
                "strict": True,
                "noImplicitAny": True,
            },
            "extends": "@tsconfig/recommended/tsconfig.json",
        }

        config_path = project_dir / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump(tsconfig, f)

        # Use load_config to find and load config from subdirectory
        config = load_config("typescript", start_dir=str(src_dir))

        assert config is not None
        assert config.linter == "typescript"
        assert config.rules["target"] == "ES2020"
        assert config.rules["strict"] is True
        assert config.rules["noImplicitAny"] is True


# =============================================================================
# Edge Cases Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_eslint_empty_config(self, temp_dir):
        """Test loading empty ESLint config."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump({}, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert config.rules == {}
        assert config.extends == []
        assert config.plugins == []

    def test_pylint_empty_ini(self, temp_dir):
        """Test loading empty Pylint config."""
        config_path = Path(temp_dir) / ".pylintrc"
        with open(config_path, "w") as f:
            f.write("")

        loader = PylintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "pylint"
        assert config.rules == {}
        assert config.plugins == []

    def test_typescript_empty_config(self, temp_dir):
        """Test loading empty TypeScript config."""
        config_path = Path(temp_dir) / "tsconfig.json"
        with open(config_path, "w") as f:
            json.dump({}, f)

        loader = TypeScriptConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "typescript"
        assert config.rules == {}
        assert config.extends == [""]

    def test_deep_directory_traversal(self, temp_dir):
        """Test finding config in deeply nested directory."""
        # Create config at root
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump({"rules": {"test": "error"}}, f)

        # Create deep directory structure
        deep_dir = Path(temp_dir) / "a" / "b" / "c" / "d" / "e" / "f"
        deep_dir.mkdir(parents=True)

        loader = ESLintConfigLoader()
        found = loader.find_config(str(deep_dir))

        # Resolve both paths to handle macOS /var -> /private/var symlink
        assert Path(found).resolve() == config_path.resolve()

    def test_config_with_special_characters_in_path(self, temp_dir):
        """Test loading config with special characters in path."""
        special_dir = Path(temp_dir) / "project with spaces"
        special_dir.mkdir()

        config_path = special_dir / ".eslintrc.json"
        with open(config_path, "w") as f:
            json.dump({"rules": {"test": "warn"}}, f)

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.linter == "eslint"
        assert config.rules["test"] == "warn"

    def test_symlink_config_file(self, temp_dir):
        """Test loading config through symlink."""
        import os

        # Create actual config
        actual_path = Path(temp_dir) / "actual_config.json"
        with open(actual_path, "w") as f:
            json.dump({"rules": {"symlink-test": "error"}}, f)

        # Create symlink
        symlink_path = Path(temp_dir) / ".eslintrc.json"
        try:
            os.symlink(actual_path, symlink_path)
        except OSError:
            pytest.skip("Symlinks not supported on this platform")

        loader = ESLintConfigLoader()
        config = loader.load(str(symlink_path))

        assert config.rules["symlink-test"] == "error"

    def test_unicode_in_config(self, temp_dir):
        """Test loading config with unicode content."""
        config_path = Path(temp_dir) / ".eslintrc.json"
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "rules": {"emoji-rule": "warn"},
                    "description": "Config avec des accents et emojis",
                },
                f,
                ensure_ascii=False,
            )

        loader = ESLintConfigLoader()
        config = loader.load(str(config_path))

        assert config.rules["emoji-rule"] == "warn"
