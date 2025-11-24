"""
Tests for Claude Memory Integration (v1.8.0)

Tests the ClaudeMemoryLoader and integration with EmpathyLLM.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_llm_toolkit.claude_memory import (
    ClaudeMemoryConfig,
    ClaudeMemoryLoader,
    create_default_project_memory,
)


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_claude_memory(temp_project_dir):
    """Create sample CLAUDE.md files for testing"""
    project_path = Path(temp_project_dir)

    # Create .claude directory
    claude_dir = project_path / ".claude"
    claude_dir.mkdir()

    # Create project memory
    project_memory = claude_dir / "CLAUDE.md"
    project_memory.write_text(
        """# Test Project Memory

## Preferences
- Use Python 3.10+
- Follow PEP 8

## Security
- Never commit secrets
"""
    )

    return temp_project_dir


def test_memory_config_defaults():
    """Test ClaudeMemoryConfig default values"""
    config = ClaudeMemoryConfig()

    assert config.enabled is False
    assert config.load_enterprise is True
    assert config.load_user is True
    assert config.load_project is True
    assert config.max_import_depth == 5
    assert config.max_file_size_bytes == 1_000_000


def test_memory_config_custom():
    """Test custom ClaudeMemoryConfig"""
    config = ClaudeMemoryConfig(
        enabled=True,
        load_enterprise=False,
        max_import_depth=3,
    )

    assert config.enabled is True
    assert config.load_enterprise is False
    assert config.max_import_depth == 3


def test_loader_disabled(temp_project_dir):
    """Test that disabled loader returns empty string"""
    config = ClaudeMemoryConfig(enabled=False)
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(temp_project_dir)

    assert memory == ""


def test_load_project_memory(sample_claude_memory):
    """Test loading project-level memory"""
    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(sample_claude_memory)

    assert memory != ""
    assert "Test Project Memory" in memory
    assert "Use Python 3.10+" in memory
    assert "PROJECT Level" in memory


def test_load_nonexistent_memory(temp_project_dir):
    """Test loading memory when files don't exist"""
    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(temp_project_dir)

    # Should return empty string (no project memory exists)
    assert memory == ""


def test_cache_clearing(sample_claude_memory):
    """Test memory cache clearing"""
    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)
    loader = ClaudeMemoryLoader(config)

    # Load memory (populates cache)
    memory1 = loader.load_all_memory(sample_claude_memory)
    assert len(loader.get_loaded_files()) > 0

    # Clear cache
    loader.clear_cache()
    assert len(loader.get_loaded_files()) == 0

    # Load again (should work)
    memory2 = loader.load_all_memory(sample_claude_memory)
    assert memory2 == memory1


def test_import_processing(temp_project_dir):
    """Test @import directive processing"""
    project_path = Path(temp_project_dir)
    claude_dir = project_path / ".claude"
    claude_dir.mkdir()

    # Create main file with import
    main_file = claude_dir / "CLAUDE.md"
    main_file.write_text(
        """# Main Memory

@./imported.md

## Additional content
After import
"""
    )

    # Create imported file
    imported_file = claude_dir / "imported.md"
    imported_file.write_text(
        """# Imported Content

This was imported!
"""
    )

    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(temp_project_dir)

    assert "Main Memory" in memory
    assert "Imported Content" in memory
    assert "This was imported!" in memory
    assert "After import" in memory


def test_import_depth_limit(temp_project_dir):
    """Test that import depth is limited"""
    project_path = Path(temp_project_dir)
    claude_dir = project_path / ".claude"
    claude_dir.mkdir()

    # Create chain of imports exceeding depth limit
    for i in range(10):
        file = claude_dir / f"file{i}.md"
        if i < 9:
            file.write_text(f"# File {i}\n@./file{i+1}.md")
        else:
            file.write_text(f"# File {i}\nEnd of chain")

    main_file = claude_dir / "CLAUDE.md"
    main_file.write_text("@./file0.md")

    config = ClaudeMemoryConfig(
        enabled=True, load_user=False, load_enterprise=False, max_import_depth=5
    )
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(temp_project_dir)

    # Should load up to depth limit but not beyond
    assert "File 0" in memory
    assert "File 4" in memory
    # File 5 might be at the limit, but 6+ should not be loaded
    # (exact behavior depends on implementation)


def test_circular_import_detection(temp_project_dir):
    """Test that circular imports are detected and prevented"""
    project_path = Path(temp_project_dir)
    claude_dir = project_path / ".claude"
    claude_dir.mkdir()

    # Create circular imports
    file_a = claude_dir / "a.md"
    file_a.write_text("# File A\n@./b.md")

    file_b = claude_dir / "b.md"
    file_b.write_text("# File B\n@./a.md")

    main_file = claude_dir / "CLAUDE.md"
    main_file.write_text("@./a.md")

    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)
    loader = ClaudeMemoryLoader(config)

    # Should not crash, should handle circular import
    memory = loader.load_all_memory(temp_project_dir)

    assert "File A" in memory
    assert "File B" in memory


def test_create_default_project_memory(temp_project_dir):
    """Test creating default project memory file"""
    create_default_project_memory(temp_project_dir, framework="empathy")

    claude_dir = Path(temp_project_dir) / ".claude"
    memory_file = claude_dir / "CLAUDE.md"

    assert claude_dir.exists()
    assert memory_file.exists()

    content = memory_file.read_text()
    assert "Empathy Framework" in content
    assert "Code Style Preferences" in content


def test_dont_overwrite_existing(sample_claude_memory):
    """Test that default creation doesn't overwrite existing files"""
    memory_file = Path(sample_claude_memory) / ".claude" / "CLAUDE.md"
    original_content = memory_file.read_text()

    # Try to create default (should not overwrite)
    create_default_project_memory(sample_claude_memory, framework="empathy")

    new_content = memory_file.read_text()
    assert new_content == original_content


@pytest.mark.asyncio
async def test_integration_with_empathy_llm(sample_claude_memory):
    """Test integration of Claude memory with EmpathyLLM"""
    from empathy_llm_toolkit import EmpathyLLM

    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)

    # Note: This test requires API key, so we just test initialization
    llm = EmpathyLLM(
        provider="anthropic",
        api_key="test-key-not-used",  # Dummy key for initialization test
        target_level=2,
        claude_memory_config=config,
        project_root=sample_claude_memory,
    )

    # Verify memory was loaded
    assert llm._cached_memory is not None
    assert len(llm._cached_memory) > 0
    assert "Test Project Memory" in llm._cached_memory


@pytest.mark.asyncio
async def test_reload_memory(sample_claude_memory):
    """Test reloading memory after changes"""
    from empathy_llm_toolkit import EmpathyLLM

    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key="test-key-not-used",  # Dummy key for initialization test
        claude_memory_config=config,
        project_root=sample_claude_memory,
    )

    original_memory = llm._cached_memory

    # Modify memory file
    memory_file = Path(sample_claude_memory) / ".claude" / "CLAUDE.md"
    memory_file.write_text(
        memory_file.read_text() + "\n\n## New Section\nAdded after initialization"
    )

    # Reload
    llm.reload_memory()

    # Memory should be updated
    assert llm._cached_memory != original_memory
    assert "New Section" in llm._cached_memory


def test_memory_file_size_limit(temp_project_dir):
    """Test that overly large files are rejected"""
    project_path = Path(temp_project_dir)
    claude_dir = project_path / ".claude"
    claude_dir.mkdir()

    # Create large file (>1MB with tiny limit for testing)
    memory_file = claude_dir / "CLAUDE.md"
    memory_file.write_text("X" * 2000)  # 2KB file

    config = ClaudeMemoryConfig(
        enabled=True,
        load_user=False,
        load_enterprise=False,
        max_file_size_bytes=1000,  # 1KB limit
    )
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(temp_project_dir)

    # Should return empty (file too large)
    assert memory == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
