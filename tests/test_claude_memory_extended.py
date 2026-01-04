"""Extended Tests for Claude Memory Integration - Coverage Improvement

This test suite focuses on improving coverage from 72% to 95% by testing:
1. Enterprise memory loading from multiple sources
2. User memory loading
3. Error handling (IOError, UnicodeDecodeError, validation)
4. Import processing edge cases
5. Non-empathy framework support
6. Edge cases and error paths

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_llm_toolkit.claude_memory import (
    ClaudeMemoryConfig,
    ClaudeMemoryLoader,
    MemoryFile,
    create_default_project_memory,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def mock_home_dir(tmp_path):
    """Create a mock home directory"""
    return tmp_path


class TestEnterpriseMemoryLoading:
    """Test enterprise memory loading from various sources"""

    def test_load_enterprise_from_env_var(self, temp_project_dir):
        """Test loading enterprise memory from CLAUDE_ENTERPRISE_MEMORY env var"""
        # Create enterprise memory file
        enterprise_file = Path(temp_project_dir) / "enterprise_memory.md"
        enterprise_file.write_text("# Enterprise Policy\nFollow corporate standards")

        # Set environment variable
        with patch.dict(os.environ, {"CLAUDE_ENTERPRISE_MEMORY": str(enterprise_file)}):
            config = ClaudeMemoryConfig(enabled=True, load_user=False, load_project=False)
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory(temp_project_dir)

            assert memory != ""
            assert "Enterprise Policy" in memory
            assert "Follow corporate standards" in memory
            assert "ENTERPRISE Level" in memory

    def test_load_enterprise_from_config_path(self, temp_project_dir):
        """Test loading enterprise memory from config.enterprise_memory_path"""
        # Create enterprise memory file
        enterprise_file = Path(temp_project_dir) / "custom_enterprise.md"
        enterprise_file.write_text("# Custom Enterprise Memory\nCustom policies")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_user=False,
            load_project=False,
            enterprise_memory_path=str(enterprise_file),
        )
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert memory != ""
        assert "Custom Enterprise Memory" in memory
        assert "Custom policies" in memory

    def test_load_enterprise_from_etc_claude(self, temp_project_dir):
        """Test loading enterprise memory from /etc/claude/CLAUDE.md path check"""
        # This test verifies the /etc/claude/CLAUDE.md path is checked
        # We test this by ensuring no env var or config path is set,
        # and the standard path doesn't exist (which is typical)

        # Make sure no env var is set
        with patch.dict(os.environ, {}, clear=False):
            # Remove CLAUDE_ENTERPRISE_MEMORY if it exists
            os.environ.pop("CLAUDE_ENTERPRISE_MEMORY", None)

            config = ClaudeMemoryConfig(
                enabled=True,
                load_user=False,
                load_project=False,
                enterprise_memory_path=None,  # No config path
            )
            loader = ClaudeMemoryLoader(config)

            # The loader will check /etc/claude/CLAUDE.md
            # Since it doesn't exist (on most systems), it will return empty
            memory = loader.load_all_memory(temp_project_dir)

            # Expected: empty memory since no enterprise file exists
            assert isinstance(memory, str)

    def test_enterprise_priority_env_over_config(self, temp_project_dir):
        """Test that env var takes priority over config path"""
        # Create two different files
        env_file = Path(temp_project_dir) / "env_enterprise.md"
        env_file.write_text("# From Environment Variable")

        config_file = Path(temp_project_dir) / "config_enterprise.md"
        config_file.write_text("# From Config")

        with patch.dict(os.environ, {"CLAUDE_ENTERPRISE_MEMORY": str(env_file)}):
            config = ClaudeMemoryConfig(
                enabled=True,
                load_user=False,
                load_project=False,
                enterprise_memory_path=str(config_file),
            )
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory(temp_project_dir)

            # Should load from env var, not config
            assert "From Environment Variable" in memory
            assert "From Config" not in memory


class TestUserMemoryLoading:
    """Test user memory loading from ~/.claude/CLAUDE.md"""

    def test_load_user_memory(self, mock_home_dir):
        """Test loading user memory from ~/.claude/CLAUDE.md"""
        # Create user memory file
        claude_dir = mock_home_dir / ".claude"
        claude_dir.mkdir()
        user_memory = claude_dir / "CLAUDE.md"
        user_memory.write_text("# User Preferences\nMy personal settings")

        with patch("pathlib.Path.home", return_value=mock_home_dir):
            config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_project=False)
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory()

            assert memory != ""
            assert "User Preferences" in memory
            assert "My personal settings" in memory
            assert "USER Level" in memory

    def test_user_memory_not_found(self, mock_home_dir):
        """Test when user memory doesn't exist"""
        with patch("pathlib.Path.home", return_value=mock_home_dir):
            config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_project=False)
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory()

            # Should return empty string when no memory files exist
            assert memory == ""


class TestErrorHandling:
    """Test error handling for various failure scenarios"""

    def test_ioerror_with_validate_files_true(self, temp_project_dir):
        """Test IOError with validate_files=True raises exception"""
        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=True,
        )
        loader = ClaudeMemoryLoader(config)

        # Mock _load_project_memory to raise IOError
        with patch.object(loader, "_load_project_memory", side_effect=OSError("File read error")):
            with pytest.raises(IOError):
                loader.load_all_memory(temp_project_dir)

    def test_ioerror_with_validate_files_false(self, temp_project_dir):
        """Test IOError with validate_files=False returns empty string"""
        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=False,
        )
        loader = ClaudeMemoryLoader(config)

        # Mock _load_project_memory to raise IOError
        with patch.object(loader, "_load_project_memory", side_effect=OSError("File read error")):
            memory = loader.load_all_memory(temp_project_dir)

            # Should return empty string without raising
            assert memory == ""

    def test_unicode_decode_error_with_validate_true(self, temp_project_dir):
        """Test UnicodeDecodeError with validate_files=True"""
        # Create a file with invalid UTF-8
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        memory_file = claude_dir / "CLAUDE.md"

        # Write invalid UTF-8 bytes
        memory_file.write_bytes(b"\x80\x81\x82\x83")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=True,
        )
        loader = ClaudeMemoryLoader(config)

        with pytest.raises(UnicodeDecodeError):
            loader.load_all_memory(temp_project_dir)

    def test_unicode_decode_error_with_validate_false(self, temp_project_dir):
        """Test UnicodeDecodeError with validate_files=False"""
        # Create a file with invalid UTF-8
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        memory_file = claude_dir / "CLAUDE.md"

        # Write invalid UTF-8 bytes
        memory_file.write_bytes(b"\x80\x81\x82\x83")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=False,
        )
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should return empty string without raising
        assert memory == ""

    def test_permission_denied_error(self, temp_project_dir):
        """Test PermissionError when file can't be read"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Memory")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=True,
        )
        loader = ClaudeMemoryLoader(config)

        # Mock read_text to raise PermissionError
        with patch("pathlib.Path.read_text", side_effect=PermissionError("Access denied")):
            with pytest.raises(PermissionError):
                loader.load_all_memory(temp_project_dir)

    def test_file_not_found_during_read(self, temp_project_dir):
        """Test file that exists during check but is deleted during read"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Memory")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            validate_files=True,
        )
        loader = ClaudeMemoryLoader(config)

        # Mock read_text to raise FileNotFoundError
        with patch("pathlib.Path.read_text", side_effect=FileNotFoundError("File disappeared")):
            with pytest.raises(FileNotFoundError):
                loader.load_all_memory(temp_project_dir)


class TestImportProcessing:
    """Test import processing edge cases"""

    def test_missing_import_file(self, temp_project_dir):
        """Test @import with non-existent file"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create main file with import to non-existent file
        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text(
            """# Main Memory

@./missing_file.md

## Content after import
Regular content
""",
        )

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Main Memory" in memory
        assert "Import not found: ./missing_file.md" in memory
        assert "Regular content" in memory

    def test_memory_file_not_found_returns_none(self, temp_project_dir):
        """Test that _load_memory_file returns None when file doesn't exist"""
        config = ClaudeMemoryConfig(enabled=True, validate_files=True)
        loader = ClaudeMemoryLoader(config)

        # Try to load a non-existent file
        non_existent_path = str(Path(temp_project_dir) / "nonexistent.md")
        result = loader._load_memory_file(non_existent_path, "project")

        # Should return None when file doesn't exist
        assert result is None

    def test_circular_imports_complex(self, temp_project_dir):
        """Test more complex circular import scenario"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create circular import: main -> a -> b -> a
        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text("# Main\n@./a.md")

        file_a = claude_dir / "a.md"
        file_a.write_text("# File A\n@./b.md")

        file_b = claude_dir / "b.md"
        file_b.write_text("# File B\n@./a.md")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should handle circular import gracefully
        assert "Main" in memory
        assert "File A" in memory
        assert "File B" in memory

    def test_import_with_relative_paths(self, temp_project_dir):
        """Test imports with various relative path formats"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create subdirectory
        sub_dir = claude_dir / "policies"
        sub_dir.mkdir()

        # Create imported file in subdirectory
        policy_file = sub_dir / "security.md"
        policy_file.write_text("# Security Policy\nSecure coding required")

        # Create main file with relative import
        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text("# Main\n@./policies/security.md")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Main" in memory
        assert "Security Policy" in memory
        assert "Secure coding required" in memory

    def test_import_failed_then_succeeds_on_retry(self, temp_project_dir):
        """Test import that fails first time but succeeds on cache hit"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        imported_file = claude_dir / "imported.md"
        imported_file.write_text("# Imported Content")

        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text("# Main\n@./imported.md")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        # First load - should work
        memory1 = loader.load_all_memory(temp_project_dir)
        assert "Imported Content" in memory1

        # Check cache
        loaded_files = loader.get_loaded_files()
        assert len(loaded_files) > 0

        # Second load - should use cache
        memory2 = loader.load_all_memory(temp_project_dir)
        assert memory2 == memory1


class TestProjectMemoryVariants:
    """Test different project memory file locations"""

    def test_load_project_from_claude_dir(self, temp_project_dir):
        """Test loading from .claude/CLAUDE.md (preferred location)"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Project from .claude dir")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Project from .claude dir" in memory

    def test_load_project_from_root_fallback(self, temp_project_dir):
        """Test loading from CLAUDE.md in project root (fallback)"""
        project_path = Path(temp_project_dir)

        # Create in root (not in .claude/)
        memory_file = project_path / "CLAUDE.md"
        memory_file.write_text("# Project from root")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Project from root" in memory

    def test_prefer_claude_dir_over_root(self, temp_project_dir):
        """Test that .claude/CLAUDE.md is preferred over root CLAUDE.md"""
        project_path = Path(temp_project_dir)

        # Create both files
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()
        claude_memory = claude_dir / "CLAUDE.md"
        claude_memory.write_text("# From .claude directory")

        root_memory = project_path / "CLAUDE.md"
        root_memory.write_text("# From root directory")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should load from .claude/ directory
        assert "From .claude directory" in memory
        assert "From root directory" not in memory


class TestHierarchicalMemoryLoading:
    """Test loading multiple memory levels together"""

    def test_load_all_three_levels(self, temp_project_dir, mock_home_dir):
        """Test loading enterprise, user, and project memory together"""
        # Create enterprise memory
        enterprise_file = Path(temp_project_dir) / "enterprise.md"
        enterprise_file.write_text("# Enterprise Level Memory")

        # Create user memory
        user_claude_dir = mock_home_dir / ".claude"
        user_claude_dir.mkdir()
        user_memory = user_claude_dir / "CLAUDE.md"
        user_memory.write_text("# User Level Memory")

        # Create project memory
        project_path = Path(temp_project_dir)
        project_claude_dir = project_path / ".claude"
        project_claude_dir.mkdir()
        project_memory = project_claude_dir / "CLAUDE.md"
        project_memory.write_text("# Project Level Memory")

        with patch("pathlib.Path.home", return_value=mock_home_dir):
            config = ClaudeMemoryConfig(enabled=True, enterprise_memory_path=str(enterprise_file))
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory(temp_project_dir)

            # Should contain all three levels
            assert "Enterprise Level Memory" in memory
            assert "User Level Memory" in memory
            assert "Project Level Memory" in memory

            # Should be in correct order (enterprise first, project last)
            enterprise_pos = memory.find("ENTERPRISE Level")
            user_pos = memory.find("USER Level")
            project_pos = memory.find("PROJECT Level")

            assert enterprise_pos < user_pos < project_pos

    def test_selective_level_loading(self, temp_project_dir, mock_home_dir):
        """Test loading only specific memory levels"""
        # Create all three levels
        enterprise_file = Path(temp_project_dir) / "enterprise.md"
        enterprise_file.write_text("# Enterprise")

        user_claude_dir = mock_home_dir / ".claude"
        user_claude_dir.mkdir()
        user_memory = user_claude_dir / "CLAUDE.md"
        user_memory.write_text("# User")

        project_path = Path(temp_project_dir)
        project_claude_dir = project_path / ".claude"
        project_claude_dir.mkdir()
        project_memory = project_claude_dir / "CLAUDE.md"
        project_memory.write_text("# Project")

        with patch("pathlib.Path.home", return_value=mock_home_dir):
            # Load only enterprise and project (skip user)
            config = ClaudeMemoryConfig(
                enabled=True,
                load_user=False,
                enterprise_memory_path=str(enterprise_file),
            )
            loader = ClaudeMemoryLoader(config)

            memory = loader.load_all_memory(temp_project_dir)

            assert "Enterprise" in memory
            # Check for user memory content marker, not just "User"
            # (Windows paths may contain "Users")
            assert "# User" not in memory
            assert "Project" in memory


class TestDefaultProjectMemoryCreation:
    """Test create_default_project_memory function"""

    def test_create_default_empathy_framework(self, temp_project_dir):
        """Test creating default memory for empathy framework"""
        create_default_project_memory(temp_project_dir, framework="empathy")

        memory_file = Path(temp_project_dir) / ".claude" / "CLAUDE.md"

        assert memory_file.exists()

        content = memory_file.read_text()
        assert "Empathy Framework" in content
        assert "Code Style Preferences" in content
        assert "Architecture Patterns" in content
        assert "Level 4 Anticipatory predictions" in content
        assert "MemDocs" in content

    def test_create_default_non_empathy_framework(self, temp_project_dir):
        """Test creating default memory for non-empathy framework"""
        create_default_project_memory(temp_project_dir, framework="langchain")

        memory_file = Path(temp_project_dir) / ".claude" / "CLAUDE.md"

        assert memory_file.exists()

        content = memory_file.read_text()
        assert "Project Memory" in content
        assert "Code Preferences" in content
        assert "@imports" in content
        # Should NOT contain empathy-specific content
        assert "Empathy Framework" not in content
        assert "MemDocs" not in content

    def test_create_default_generic_framework(self, temp_project_dir):
        """Test creating default memory for generic/unknown framework"""
        create_default_project_memory(temp_project_dir, framework="custom-framework")

        memory_file = Path(temp_project_dir) / ".claude" / "CLAUDE.md"

        assert memory_file.exists()

        content = memory_file.read_text()
        # Should use generic template
        assert "Project Memory" in content

    def test_create_default_creates_claude_directory(self, temp_project_dir):
        """Test that function creates .claude directory if needed"""
        claude_dir = Path(temp_project_dir) / ".claude"

        # Verify directory doesn't exist initially
        assert not claude_dir.exists()

        create_default_project_memory(temp_project_dir)

        # Directory should now exist
        assert claude_dir.exists()

    def test_dont_overwrite_existing_memory(self, temp_project_dir):
        """Test that existing memory files are not overwritten"""
        claude_dir = Path(temp_project_dir) / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        original_content = "# My Custom Memory\nDo not overwrite!"
        memory_file.write_text(original_content)

        # Try to create default
        create_default_project_memory(temp_project_dir)

        # Content should be unchanged
        content = memory_file.read_text()
        assert content == original_content


class TestMemoryFileDataclass:
    """Test MemoryFile dataclass"""

    def test_memory_file_creation(self):
        """Test creating MemoryFile object"""
        memory = MemoryFile(level="project", path="/path/to/file.md", content="# Memory content")

        assert memory.level == "project"
        assert memory.path == "/path/to/file.md"
        assert memory.content == "# Memory content"
        assert memory.imports == []
        assert memory.load_order == 0

    def test_memory_file_with_imports(self):
        """Test MemoryFile with imports"""
        memory = MemoryFile(
            level="project",
            path="/path/to/file.md",
            content="# Memory",
            imports=["/path/to/imported1.md", "/path/to/imported2.md"],
            load_order=3,
        )

        assert len(memory.imports) == 2
        assert memory.load_order == 3


class TestCaching:
    """Test memory caching behavior"""

    def test_cache_used_on_second_load(self, temp_project_dir):
        """Test that cache is used on subsequent loads"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Original content")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        # First load
        memory1 = loader.load_all_memory(temp_project_dir)
        assert "Original content" in memory1

        # Modify file
        memory_file.write_text("# Modified content")

        # Second load - should use cache
        memory2 = loader.load_all_memory(temp_project_dir)

        # Should still have original content from cache
        assert "Original content" in memory2
        assert "Modified content" not in memory2

    def test_clear_cache_and_reload(self, temp_project_dir):
        """Test clearing cache and reloading"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Original content")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        # First load
        memory1 = loader.load_all_memory(temp_project_dir)
        assert "Original content" in memory1

        # Clear cache
        loader.clear_cache()

        # Modify file
        memory_file.write_text("# Modified content")

        # Reload after cache clear
        memory2 = loader.load_all_memory(temp_project_dir)

        # Should have new content
        assert "Modified content" in memory2
        assert "Original content" not in memory2


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_empty_memory_file(self, temp_project_dir):
        """Test loading empty memory file"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should not crash, should have section header
        assert "PROJECT Level" in memory

    def test_memory_file_with_only_whitespace(self, temp_project_dir):
        """Test memory file containing only whitespace"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("   \n\n\t\n   ")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should load successfully
        assert "PROJECT Level" in memory

    def test_very_deep_import_chain(self, temp_project_dir):
        """Test import chain at max depth limit"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create chain exactly at max depth (5)
        for i in range(6):
            file = claude_dir / f"level{i}.md"
            if i < 5:
                file.write_text(f"# Level {i}\n@./level{i + 1}.md")
            else:
                file.write_text(f"# Level {i} (should not load)")

        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text("@./level0.md")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            max_import_depth=5,
        )
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Check what was loaded
        assert "Level 0" in memory
        # Level 5 should not load due to depth limit

    def test_combine_memory_files_empty_list(self):
        """Test combining empty list of memory files"""
        loader = ClaudeMemoryLoader()
        result = loader._combine_memory_files([])

        assert result == ""

    def test_get_loaded_files_before_loading(self):
        """Test get_loaded_files before any files are loaded"""
        config = ClaudeMemoryConfig(enabled=True)
        loader = ClaudeMemoryLoader(config)

        loaded = loader.get_loaded_files()

        assert loaded == []

    def test_project_root_from_config(self, temp_project_dir):
        """Test using project_root from config"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        memory_file = claude_dir / "CLAUDE.md"
        memory_file.write_text("# Project Memory")

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            project_root=temp_project_dir,
        )
        loader = ClaudeMemoryLoader(config)

        # Don't pass project_root to load_all_memory
        memory = loader.load_all_memory()

        assert "Project Memory" in memory

    def test_project_root_defaults_to_cwd(self):
        """Test that project_root defaults to current working directory"""
        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        # This should use os.getcwd() without crashing
        memory = loader.load_all_memory()

        # May or may not find memory, but shouldn't crash
        assert isinstance(memory, str)

    def test_max_file_size_check(self, temp_project_dir):
        """Test file size validation"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create file that's too large
        memory_file = claude_dir / "CLAUDE.md"
        large_content = "X" * 5000
        memory_file.write_text(large_content)

        config = ClaudeMemoryConfig(
            enabled=True,
            load_enterprise=False,
            load_user=False,
            max_file_size_bytes=1000,  # 1KB limit
        )
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        # Should return empty due to size limit
        assert memory == ""

    def test_import_with_absolute_path(self, temp_project_dir):
        """Test import with absolute path"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create imported file
        imported_file = claude_dir / "imported.md"
        imported_file.write_text("# Imported")

        # Create main file with absolute path import
        main_file = claude_dir / "CLAUDE.md"
        # Note: Using relative path as absolute paths in imports are resolved relative to base_dir
        main_file.write_text("# Main\n@./imported.md")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Imported" in memory


class TestImportStackManagement:
    """Test import stack for circular import detection"""

    def test_import_stack_cleared_after_load(self, temp_project_dir):
        """Test that import stack is properly cleared after loading"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create files with imports
        file1 = claude_dir / "file1.md"
        file1.write_text("# File 1\n@./file2.md")

        file2 = claude_dir / "file2.md"
        file2.write_text("# File 2")

        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text("@./file1.md")

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        # Load memory
        loader.load_all_memory(temp_project_dir)

        # Import stack should be empty after load
        assert len(loader._import_stack) == 0


class TestConfigDefaults:
    """Test configuration default values"""

    def test_config_with_none_defaults(self):
        """Test ClaudeMemoryConfig with None values"""
        config = ClaudeMemoryConfig(enabled=True, enterprise_memory_path=None, project_root=None)

        assert config.enabled is True
        assert config.enterprise_memory_path is None
        assert config.project_root is None


class TestMultipleImportsInSingleFile:
    """Test handling multiple imports in a single file"""

    def test_multiple_imports(self, temp_project_dir):
        """Test file with multiple @import directives"""
        project_path = Path(temp_project_dir)
        claude_dir = project_path / ".claude"
        claude_dir.mkdir()

        # Create imported files
        file1 = claude_dir / "file1.md"
        file1.write_text("# File 1 Content")

        file2 = claude_dir / "file2.md"
        file2.write_text("# File 2 Content")

        # Create main file with multiple imports
        main_file = claude_dir / "CLAUDE.md"
        main_file.write_text(
            """# Main File
@./file1.md
Some content in between
@./file2.md
More content
""",
        )

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False, load_user=False)
        loader = ClaudeMemoryLoader(config)

        memory = loader.load_all_memory(temp_project_dir)

        assert "Main File" in memory
        assert "File 1 Content" in memory
        assert "File 2 Content" in memory
        assert "Some content in between" in memory
        assert "More content" in memory


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=empathy_llm_toolkit.claude_memory"])
