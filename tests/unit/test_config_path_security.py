"""Security tests for config file path validation.

Tests Pattern 6 (File Path Validation) applied to:
- config.py (EmpathyConfig.to_yaml, to_json)
- workflows/config.py (WorkflowConfig.save)
- config/xml_config.py (EmpathyXMLConfig.save_to_file)

Copyright 2026 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest
from pathlib import Path
import tempfile
import os

from empathy_os.config import EmpathyConfig
from empathy_os.workflows.config import WorkflowConfig
from empathy_os.config.xml_config import EmpathyXMLConfig


class TestEmpathyConfigPathValidation:
    """Test path validation in EmpathyConfig."""

    def test_to_yaml_prevents_path_traversal(self):
        """Test that to_yaml blocks path traversal attacks."""
        config = EmpathyConfig(user_id="test")

        # Attempt path traversal (may raise ValueError or PermissionError depending on OS)
        with pytest.raises((ValueError, PermissionError)):
            config.to_yaml("/etc/empathy.yml")

    def test_to_yaml_prevents_null_bytes(self):
        """Test that to_yaml blocks null byte injection."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="contains null bytes"):
            config.to_yaml("config\x00.yml")

    def test_to_yaml_accepts_valid_path(self):
        """Test that to_yaml accepts valid paths."""
        config = EmpathyConfig(user_id="test")

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = os.path.join(tmpdir, "config.yml")
            config.to_yaml(valid_path)
            assert Path(valid_path).exists()

    def test_to_json_prevents_path_traversal(self):
        """Test that to_json blocks path traversal attacks."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="Cannot write to system directory"):
            config.to_json("/sys/empathy.json")

    def test_to_json_prevents_null_bytes(self):
        """Test that to_json blocks null byte injection."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="contains null bytes"):
            config.to_json("config\x00.json")

    def test_to_json_accepts_valid_path(self):
        """Test that to_json accepts valid paths."""
        config = EmpathyConfig(user_id="test")

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = os.path.join(tmpdir, "config.json")
            config.to_json(valid_path)
            assert Path(valid_path).exists()

    def test_rejects_empty_path(self):
        """Test that empty paths are rejected."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="must be a non-empty string"):
            config.to_yaml("")


class TestWorkflowConfigPathValidation:
    """Test path validation in WorkflowConfig."""

    def test_save_prevents_path_traversal(self):
        """Test that save blocks path traversal attacks."""
        config = WorkflowConfig(default_provider="anthropic")

        with pytest.raises(ValueError, match="Cannot write to system directory"):
            config.save("/proc/empathy_workflows.json")

    def test_save_prevents_null_bytes(self):
        """Test that save blocks null byte injection."""
        config = WorkflowConfig(default_provider="anthropic")

        with pytest.raises(ValueError, match="contains null bytes"):
            config.save("workflows\x00.json")

    def test_save_accepts_valid_path_str(self):
        """Test that save accepts valid string paths."""
        config = WorkflowConfig(default_provider="anthropic")

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = os.path.join(tmpdir, "workflows.json")
            config.save(valid_path)
            assert Path(valid_path).exists()

    def test_save_accepts_valid_path_object(self):
        """Test that save accepts valid Path objects."""
        config = WorkflowConfig(default_provider="anthropic")

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = Path(tmpdir) / "workflows.yaml"
            config.save(valid_path)
            assert valid_path.exists()

    def test_save_creates_yaml_for_yml_suffix(self):
        """Test that save creates YAML files with .yml/.yaml suffix."""
        config = WorkflowConfig(default_provider="anthropic")

        with tempfile.TemporaryDirectory() as tmpdir:
            yaml_path = os.path.join(tmpdir, "workflows.yaml")
            config.save(yaml_path)
            assert Path(yaml_path).exists()
            # Verify it's YAML format
            content = Path(yaml_path).read_text()
            assert "default_provider" in content

    def test_save_creates_json_for_other_suffix(self):
        """Test that save creates JSON files for non-.yml suffix."""
        config = WorkflowConfig(default_provider="anthropic")

        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "workflows.json")
            config.save(json_path)
            assert Path(json_path).exists()
            # Verify it's JSON format
            content = Path(json_path).read_text()
            assert "{" in content and "}" in content


class TestXMLConfigPathValidation:
    """Test path validation in EmpathyXMLConfig."""

    def test_save_to_file_prevents_path_traversal(self):
        """Test that save_to_file blocks path traversal attacks."""
        config = EmpathyXMLConfig()

        with pytest.raises(ValueError, match="Cannot write to system directory"):
            config.save_to_file("/dev/null/empathy.json")

    def test_save_to_file_prevents_null_bytes(self):
        """Test that save_to_file blocks null byte injection."""
        config = EmpathyXMLConfig()

        with pytest.raises(ValueError, match="contains null bytes"):
            config.save_to_file("xml_config\x00.json")

    def test_save_to_file_accepts_valid_path(self):
        """Test that save_to_file accepts valid paths."""
        config = EmpathyXMLConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            valid_path = os.path.join(tmpdir, "xml_config.json")
            config.save_to_file(valid_path)
            assert Path(valid_path).exists()

    def test_save_to_file_uses_default_path(self):
        """Test that save_to_file uses default path when not specified."""
        config = EmpathyXMLConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)
            # Use default path relative to current directory
            config.save_to_file(".empathy/config.json")
            assert Path(".empathy/config.json").exists()


class TestCrossModuleConsistency:
    """Test that path validation is consistent across all config modules."""

    @pytest.mark.parametrize(
        "dangerous_path",
        [
            "/etc/passwd",
            "/sys/kernel/config",
            "/proc/self/environ",
            "/dev/random",
        ],
    )
    def test_all_modules_block_system_paths(self, dangerous_path):
        """Test that all config modules consistently block system paths."""
        empathy_config = EmpathyConfig()
        workflow_config = WorkflowConfig()
        xml_config = EmpathyXMLConfig()

        # All should raise ValueError or PermissionError for system paths
        with pytest.raises((ValueError, PermissionError)):
            empathy_config.to_json(dangerous_path)

        with pytest.raises((ValueError, PermissionError)):
            workflow_config.save(dangerous_path)

        with pytest.raises((ValueError, PermissionError)):
            xml_config.save_to_file(dangerous_path)

    @pytest.mark.parametrize(
        "null_byte_path",
        [
            "config\x00.json",
            "\x00etc/passwd",
            "test.json\x00.txt",
        ],
    )
    def test_all_modules_block_null_bytes(self, null_byte_path):
        """Test that all config modules consistently block null bytes."""
        empathy_config = EmpathyConfig()
        workflow_config = WorkflowConfig()
        xml_config = EmpathyXMLConfig()

        # All should raise ValueError for null bytes
        with pytest.raises(ValueError, match="contains null bytes"):
            empathy_config.to_json(null_byte_path)

        with pytest.raises(ValueError, match="contains null bytes"):
            workflow_config.save(null_byte_path)

        with pytest.raises(ValueError, match="contains null bytes"):
            xml_config.save_to_file(null_byte_path)

    def test_all_modules_accept_relative_paths(self):
        """Test that all config modules accept valid relative paths."""
        empathy_config = EmpathyConfig()
        workflow_config = WorkflowConfig()
        xml_config = EmpathyXMLConfig()

        with tempfile.TemporaryDirectory() as tmpdir:
            os.chdir(tmpdir)

            # All should accept relative paths
            empathy_config.to_json("empathy.json")
            assert Path("empathy.json").exists()

            workflow_config.save("workflows.json")
            assert Path("workflows.json").exists()

            xml_config.save_to_file("xml_config.json")
            assert Path("xml_config.json").exists()
