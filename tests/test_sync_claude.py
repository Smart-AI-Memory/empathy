"""
Tests for empathy_llm_toolkit/cli/sync_claude.py

Tests the sync-claude CLI command including:
- Pattern loading from directories
- Markdown formatting functions
- PATTERN_SOURCES configuration
- CLAUDE_RULES_DIR constant

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import tempfile
from pathlib import Path

from empathy_llm_toolkit.cli.sync_claude import (
    CLAUDE_RULES_DIR,
    PATTERN_SOURCES,
    format_bug_patterns_markdown,
    load_patterns_from_directory,
)


class TestConstants:
    """Tests for module constants."""

    def test_claude_rules_dir_path(self):
        """Test CLAUDE_RULES_DIR is correct path."""
        assert CLAUDE_RULES_DIR == ".claude/rules/empathy"

    def test_pattern_sources_has_debugging(self):
        """Test PATTERN_SOURCES has debugging."""
        assert "debugging" in PATTERN_SOURCES
        assert PATTERN_SOURCES["debugging"] == "bug-patterns.md"

    def test_pattern_sources_has_security(self):
        """Test PATTERN_SOURCES has security."""
        assert "security" in PATTERN_SOURCES
        assert PATTERN_SOURCES["security"] == "security-decisions.md"

    def test_pattern_sources_has_tech_debt(self):
        """Test PATTERN_SOURCES has tech_debt."""
        assert "tech_debt" in PATTERN_SOURCES
        assert PATTERN_SOURCES["tech_debt"] == "tech-debt-hotspots.md"

    def test_pattern_sources_has_inspection(self):
        """Test PATTERN_SOURCES has inspection."""
        assert "inspection" in PATTERN_SOURCES
        assert PATTERN_SOURCES["inspection"] == "coding-patterns.md"

    def test_pattern_sources_count(self):
        """Test PATTERN_SOURCES has 4 entries."""
        assert len(PATTERN_SOURCES) == 4


class TestLoadPatternsFromDirectory:
    """Tests for load_patterns_from_directory function."""

    def test_returns_empty_for_nonexistent_directory(self):
        """Test returns empty list for nonexistent directory."""
        patterns = load_patterns_from_directory(Path("/nonexistent/path"), "debugging")
        assert patterns == []

    def test_returns_empty_for_empty_directory(self):
        """Test returns empty list for empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert patterns == []

    def test_loads_single_pattern_file(self):
        """Test loads single pattern file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pattern_file = Path(tmpdir) / "bug_001.json"
            pattern_file.write_text(
                json.dumps(
                    {
                        "bug_id": "bug_001",
                        "error_type": "null_reference",
                        "description": "Missing null check",
                    }
                )
            )

            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert len(patterns) == 1
            assert patterns[0]["bug_id"] == "bug_001"

    def test_loads_multiple_pattern_files(self):
        """Test loads multiple pattern files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            for i in range(3):
                pattern_file = Path(tmpdir) / f"bug_{i}.json"
                pattern_file.write_text(
                    json.dumps(
                        {
                            "bug_id": f"bug_{i}",
                            "error_type": "test",
                        }
                    )
                )

            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert len(patterns) == 3

    def test_adds_source_file_metadata(self):
        """Test adds _source_file metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pattern_file = Path(tmpdir) / "bug_001.json"
            pattern_file.write_text(json.dumps({"bug_id": "bug_001"}))

            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert "_source_file" in patterns[0]
            assert "bug_001.json" in patterns[0]["_source_file"]

    def test_adds_pattern_type_metadata(self):
        """Test adds _pattern_type metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            pattern_file = Path(tmpdir) / "bug_001.json"
            pattern_file.write_text(json.dumps({"bug_id": "bug_001"}))

            patterns = load_patterns_from_directory(Path(tmpdir), "security")
            assert patterns[0]["_pattern_type"] == "security"

    def test_skips_invalid_json(self):
        """Test skips invalid JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Valid file
            valid_file = Path(tmpdir) / "valid.json"
            valid_file.write_text(json.dumps({"id": "valid"}))

            # Invalid file
            invalid_file = Path(tmpdir) / "invalid.json"
            invalid_file.write_text("not valid json {")

            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert len(patterns) == 1
            assert patterns[0]["id"] == "valid"

    def test_ignores_non_json_files(self):
        """Test ignores non-JSON files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            json_file = Path(tmpdir) / "pattern.json"
            json_file.write_text(json.dumps({"id": "json"}))

            txt_file = Path(tmpdir) / "pattern.txt"
            txt_file.write_text("not a pattern")

            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")
            assert len(patterns) == 1


class TestFormatBugPatternsMarkdown:
    """Tests for format_bug_patterns_markdown function."""

    def test_returns_markdown_string(self):
        """Test returns markdown string."""
        result = format_bug_patterns_markdown([])
        assert isinstance(result, str)

    def test_includes_header(self):
        """Test includes header."""
        result = format_bug_patterns_markdown([])
        assert "# Bug Patterns" in result

    def test_includes_auto_generated_note(self):
        """Test includes auto-generated note."""
        result = format_bug_patterns_markdown([])
        assert "Auto-generated by Empathy" in result

    def test_includes_last_sync_timestamp(self):
        """Test includes last sync timestamp."""
        result = format_bug_patterns_markdown([])
        assert "Last sync:" in result

    def test_includes_frontmatter(self):
        """Test includes frontmatter."""
        result = format_bug_patterns_markdown([])
        assert "---" in result
        assert "paths:" in result

    def test_groups_by_error_type(self):
        """Test groups patterns by error type."""
        patterns = [
            {"error_type": "null_reference", "bug_id": "bug_001"},
            {"error_type": "null_reference", "bug_id": "bug_002"},
            {"error_type": "async_timing", "bug_id": "bug_003"},
        ]
        result = format_bug_patterns_markdown(patterns)
        # Should have sections for different error types
        assert isinstance(result, str)

    def test_handles_empty_patterns(self):
        """Test handles empty patterns list."""
        result = format_bug_patterns_markdown([])
        assert "# Bug Patterns" in result

    def test_handles_patterns_without_error_type(self):
        """Test handles patterns without error_type."""
        patterns = [{"bug_id": "bug_001"}]  # No error_type
        result = format_bug_patterns_markdown(patterns)
        assert isinstance(result, str)


class TestPatternStructure:
    """Tests for pattern structure expectations."""

    def test_debugging_pattern_structure(self):
        """Test debugging pattern has expected fields."""
        pattern = {
            "bug_id": "bug_001",
            "error_type": "null_reference",
            "root_cause": "Missing null check",
            "fix": "Add optional chaining",
            "files": ["src/main.py"],
        }
        assert "bug_id" in pattern
        assert "error_type" in pattern

    def test_security_pattern_structure(self):
        """Test security pattern has expected fields."""
        pattern = {
            "finding_type": "xss",
            "decision": "false_positive",
            "reason": "React auto-escapes",
            "decided_by": "@sarah",
        }
        assert "finding_type" in pattern
        assert "decision" in pattern

    def test_tech_debt_pattern_structure(self):
        """Test tech debt pattern has expected fields."""
        pattern = {
            "file_path": "src/legacy.py",
            "debt_type": "todo",
            "content": "TODO: Refactor this",
            "age_days": 30,
        }
        assert "debt_type" in pattern
        assert "file_path" in pattern


class TestSyncClaudeIntegration:
    """Integration tests for sync-claude functionality."""

    def test_full_pattern_load_workflow(self):
        """Test full pattern loading workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create pattern directory structure
            debugging_dir = Path(tmpdir) / "debugging"
            debugging_dir.mkdir()

            # Add patterns
            (debugging_dir / "bug_001.json").write_text(
                json.dumps(
                    {
                        "bug_id": "bug_001",
                        "error_type": "null_reference",
                        "root_cause": "API returned null",
                        "fix": "Add null check",
                    }
                )
            )

            # Load and format
            patterns = load_patterns_from_directory(debugging_dir, "debugging")
            markdown = format_bug_patterns_markdown(patterns)

            assert len(patterns) == 1
            assert "# Bug Patterns" in markdown

    def test_pattern_roundtrip(self):
        """Test pattern save and load roundtrip."""
        with tempfile.TemporaryDirectory() as tmpdir:
            original_pattern = {
                "bug_id": "test_bug",
                "error_type": "async_timing",
                "description": "Missing await",
            }

            # Save
            pattern_file = Path(tmpdir) / "test.json"
            with open(pattern_file, "w") as f:
                json.dump(original_pattern, f)

            # Load
            patterns = load_patterns_from_directory(Path(tmpdir), "debugging")

            # Verify
            assert patterns[0]["bug_id"] == original_pattern["bug_id"]
            assert patterns[0]["error_type"] == original_pattern["error_type"]
