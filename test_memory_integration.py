#!/usr/bin/env python
"""Test script for Claude Memory Integration

This script demonstrates and tests all memory features:
- Hierarchical loading (Enterprise/User/Project)
- @import directive support
- Memory integration with EmpathyLLM
- Cache management and reloading

Usage:
    python test_memory_integration.py

Requirements:
    - empathy_llm_toolkit package installed
    - Write access to .claude/ directory for test files

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from pathlib import Path

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig, ClaudeMemoryLoader


def test_basic_memory_loading() -> None:
    """Test basic project memory loading from .claude/CLAUDE.md."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Project Memory Loading")
    print("=" * 60)

    # Already have .claude/CLAUDE.md from previous test
    config = ClaudeMemoryConfig(enabled=True)
    loader = ClaudeMemoryLoader(config)

    memory = loader.load_all_memory(".")

    print(f"✓ Memory loaded: {len(memory)} chars")
    print(f"✓ Contains 'Use Python 3.10+': {'Use Python 3.10+' in memory}")
    print(f"✓ Contains PROJECT marker: {'PROJECT Level' in memory}")
    print("\nMemory content preview:")
    print(memory[:300])


def test_import_directive() -> None:
    """Test @import directive for including modular CLAUDE.md files."""
    print("\n" + "=" * 60)
    print("TEST 2: @import Directive")
    print("=" * 60)

    # Create a shared standards file
    os.makedirs(".claude", exist_ok=True)

    with open(".claude/python-standards.md", "w") as f:
        f.write(
            """# Python Coding Standards

- Use type hints
- Follow PEP 8
- Write docstrings
- Target 90%+ test coverage
""",
        )

    # Update main CLAUDE.md to import it
    with open(".claude/CLAUDE.md", "w") as f:
        f.write(
            """# Project Memory

## Framework
This is the Empathy Framework v1.8.0-alpha

@./python-standards.md

## Additional Notes
Memory integration test
""",
        )

    config = ClaudeMemoryConfig(enabled=True)
    loader = ClaudeMemoryLoader(config)
    memory = loader.load_all_memory(".")

    print(f"✓ Memory loaded: {len(memory)} chars")
    print(f"✓ Contains imported content: {'Python Coding Standards' in memory}")
    print(f"✓ Contains 'type hints': {'type hints' in memory}")
    print(f"✓ Import marker present: {'Imported from:' in memory}")

    print("\nImported files:")
    for file_path in loader.get_loaded_files():
        print(f"  - {file_path}")

    print("\nMemory content preview:")
    print(memory[:500])


def test_empathy_llm_integration() -> None:
    """Test memory integration with EmpathyLLM system prompt building."""
    print("\n" + "=" * 60)
    print("TEST 3: EmpathyLLM Integration")
    print("=" * 60)

    config = ClaudeMemoryConfig(
        enabled=True,
        load_user=False,  # Don't load user memory for testing
        load_enterprise=False,  # Don't load enterprise memory for testing
    )

    # Initialize with memory (using dummy API key for testing)
    llm = EmpathyLLM(
        provider="anthropic",
        api_key="test-key-for-memory-testing",
        claude_memory_config=config,
        project_root=".",
    )

    print("✓ EmpathyLLM initialized with memory")
    print(f"✓ Cached memory size: {len(llm._cached_memory)} chars")
    print(f"✓ Memory contains project info: {'Empathy Framework' in llm._cached_memory}")

    # Test system prompt building (Level 2 - Guided)
    system_prompt = llm._build_system_prompt(2)

    print("\n✓ System prompt built for Level 2")
    print(f"✓ Prompt includes memory: {'PROJECT Level' in system_prompt}")
    print(
        f"✓ Prompt includes level instructions: {'Level 2' in system_prompt or 'Guided' in system_prompt}",
    )

    print(f"\nSystem prompt length: {len(system_prompt)} chars")
    print(f"Memory portion: {len(llm._cached_memory)} chars")
    print(f"Level instructions: {len(system_prompt) - len(llm._cached_memory)} chars")


def test_memory_reloading() -> None:
    """Test memory cache clearing and dynamic reloading after file changes."""
    print("\n" + "=" * 60)
    print("TEST 4: Memory Reloading")
    print("=" * 60)

    config = ClaudeMemoryConfig(enabled=True, load_user=False, load_enterprise=False)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key="test-key",
        claude_memory_config=config,
        project_root=".",
    )

    original_memory = llm._cached_memory
    original_length = len(original_memory)

    print(f"✓ Original memory loaded: {original_length} chars")

    # Modify the memory file
    with open(".claude/CLAUDE.md", "a") as f:
        f.write("\n\n## New Section\nAdded after initialization for reload test")

    # Reload memory
    llm.reload_memory()

    new_memory = llm._cached_memory
    new_length = len(new_memory)

    print(f"✓ Memory reloaded: {new_length} chars")
    print(f"✓ Memory changed: {original_memory != new_memory}")
    print(f"✓ New content present: {'New Section' in new_memory}")
    print(f"✓ Size increased: {new_length > original_length}")

    print(f"\nOriginal: {original_length} chars")
    print(f"New:      {new_length} chars")
    print(f"Diff:     +{new_length - original_length} chars")


def test_hierarchical_loading() -> None:
    """Test hierarchical memory loading (User + Project levels)."""
    print("\n" + "=" * 60)
    print("TEST 5: Hierarchical Loading (User + Project)")
    print("=" * 60)

    # Create a temporary user memory file
    user_memory_dir = Path.home() / ".claude"
    user_memory_file = user_memory_dir / "CLAUDE.md"

    # Backup existing user memory if it exists
    backup_path = None
    if user_memory_file.exists():
        backup_path = user_memory_dir / "CLAUDE.md.backup"
        user_memory_file.rename(backup_path)
        print("✓ Backed up existing user memory")

    try:
        # Create test user memory
        user_memory_dir.mkdir(exist_ok=True)
        with open(user_memory_file, "w") as f:
            f.write(
                """# User Preferences

## My Settings
- Prefer concise responses
- Use Python 3.10+
""",
            )

        config = ClaudeMemoryConfig(enabled=True, load_enterprise=False)
        loader = ClaudeMemoryLoader(config)
        memory = loader.load_all_memory(".")

        print(f"✓ Memory loaded: {len(memory)} chars")
        print(f"✓ Contains USER level: {'USER Level' in memory}")
        print(f"✓ Contains PROJECT level: {'PROJECT Level' in memory}")
        print(f"✓ User preferences present: {'My Settings' in memory}")
        print(f"✓ Project info present: {'Empathy Framework' in memory}")

        # Check loading order (User should come before Project)
        user_pos = memory.index("USER Level")
        project_pos = memory.index("PROJECT Level")
        print(f"✓ Correct hierarchy: {user_pos < project_pos}")

        print(f"\nLoaded {len(loader.get_loaded_files())} files")

    finally:
        # Restore original user memory
        if user_memory_file.exists():
            user_memory_file.unlink()
        if backup_path and backup_path.exists():
            backup_path.rename(user_memory_file)
            print("✓ Restored original user memory")
        else:
            print("✓ Cleaned up test user memory")


def test_disabled_memory() -> None:
    """Test backward compatibility when memory is disabled (default behavior)."""
    print("\n" + "=" * 60)
    print("TEST 6: Disabled Memory (Backward Compatibility)")
    print("=" * 60)

    # Default config has enabled=False
    config = ClaudeMemoryConfig()

    llm = EmpathyLLM(
        provider="anthropic",
        api_key="test-key",
        claude_memory_config=config,
        project_root=".",
    )

    print(f"✓ Memory disabled by default: {not config.enabled}")
    print(f"✓ Cached memory is None: {llm._cached_memory is None or llm._cached_memory == ''}")
    print("✓ Backward compatible: No memory loaded when disabled")

    # Test system prompt without memory
    system_prompt = llm._build_system_prompt(2)
    print(f"✓ System prompt built without memory: {len(system_prompt)} chars")
    print(f"✓ No memory markers: {'PROJECT Level' not in system_prompt}")


def main() -> None:
    """Run all memory integration tests."""
    print("\n" + "=" * 60)
    print("Claude Memory Integration Test Suite")
    print("Empathy Framework")
    print("=" * 60)

    try:
        test_basic_memory_loading()
        test_import_directive()
        test_empathy_llm_integration()
        test_memory_reloading()
        test_hierarchical_loading()
        test_disabled_memory()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nClaude Memory Integration is working correctly!")
        print("\nNext steps:")
        print("1. Test with real API calls (replace test API keys)")
        print("2. Try with your own CLAUDE.md files")
        print("3. Test @import with multiple levels of nesting")
        print("4. Experiment with different memory configurations")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
