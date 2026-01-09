"""Tests for One-Command Workflows.

Tests the power-user workflow commands including morning briefing,
pre-ship validation, and pattern learning.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from pathlib import Path

from empathy_os.workflow_commands import (
    _get_tech_debt_trend,
    _load_patterns,
    _load_stats,
    _run_command,
    _save_stats,
)


class TestLoadPatterns:
    """Tests for _load_patterns function."""

    def test_load_patterns_empty_dir(self):
        """Test loading patterns from non-existent directory."""
        patterns = _load_patterns("/nonexistent/path")

        assert patterns == {
            "debugging": [],
            "security": [],
            "tech_debt": [],
            "inspection": [],
        }

    def test_load_patterns_with_data(self):
        """Test loading patterns from directory with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create debugging.json
            debugging_data = {
                "patterns": [
                    {"id": "1", "description": "Bug fix pattern"},
                    {"id": "2", "description": "Another pattern"},
                ],
            }
            with open(Path(tmpdir) / "debugging.json", "w") as f:
                json.dump(debugging_data, f)

            patterns = _load_patterns(tmpdir)

            assert len(patterns["debugging"]) == 2
            assert patterns["debugging"][0]["id"] == "1"

    def test_load_patterns_with_items_key(self):
        """Test loading patterns with 'items' key instead of 'patterns'."""
        with tempfile.TemporaryDirectory() as tmpdir:
            security_data = {
                "items": [
                    {"id": "sec1", "type": "vulnerability"},
                ],
            }
            with open(Path(tmpdir) / "security.json", "w") as f:
                json.dump(security_data, f)

            patterns = _load_patterns(tmpdir)

            assert len(patterns["security"]) == 1
            assert patterns["security"][0]["id"] == "sec1"

    def test_load_patterns_invalid_json(self):
        """Test loading patterns with invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create invalid JSON
            with open(Path(tmpdir) / "debugging.json", "w") as f:
                f.write("not valid json {{{")

            patterns = _load_patterns(tmpdir)

            # Should return empty list for that type
            assert patterns["debugging"] == []


class TestLoadStats:
    """Tests for _load_stats function."""

    def test_load_stats_no_file(self):
        """Test loading stats when file doesn't exist."""
        stats = _load_stats("/nonexistent/.empathy")

        assert stats == {
            "commands": {},
            "last_session": None,
            "patterns_learned": 0,
        }

    def test_load_stats_with_data(self):
        """Test loading stats from existing file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empathy_dir = Path(tmpdir) / ".empathy"
            empathy_dir.mkdir()

            stats_data = {
                "commands": {"morning": 5, "ship": 3},
                "last_session": "2025-01-01",
                "patterns_learned": 42,
            }
            with open(empathy_dir / "stats.json", "w") as f:
                json.dump(stats_data, f)

            stats = _load_stats(str(empathy_dir))

            assert stats["commands"]["morning"] == 5
            assert stats["patterns_learned"] == 42

    def test_load_stats_invalid_json(self):
        """Test loading stats with invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empathy_dir = Path(tmpdir) / ".empathy"
            empathy_dir.mkdir()

            with open(empathy_dir / "stats.json", "w") as f:
                f.write("invalid json")

            stats = _load_stats(str(empathy_dir))

            # Should return defaults
            assert stats == {
                "commands": {},
                "last_session": None,
                "patterns_learned": 0,
            }


class TestSaveStats:
    """Tests for _save_stats function."""

    def test_save_stats_creates_dir(self):
        """Test saving stats creates directory if needed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empathy_dir = Path(tmpdir) / ".empathy"

            assert not empathy_dir.exists()

            stats = {"commands": {"test": 1}}
            _save_stats(stats, str(empathy_dir))

            assert empathy_dir.exists()
            assert (empathy_dir / "stats.json").exists()

    def test_save_stats_data_persists(self):
        """Test saved stats can be loaded back."""
        with tempfile.TemporaryDirectory() as tmpdir:
            empathy_dir = Path(tmpdir) / ".empathy"

            stats = {
                "commands": {"morning": 10, "ship": 5},
                "last_session": "2025-01-15",
                "patterns_learned": 100,
            }
            _save_stats(stats, str(empathy_dir))

            # Load it back
            loaded = _load_stats(str(empathy_dir))

            assert loaded["commands"]["morning"] == 10
            assert loaded["patterns_learned"] == 100


class TestRunCommand:
    """Tests for _run_command function."""

    def test_run_command_success(self):
        """Test running a successful command."""
        success, output = _run_command(["echo", "hello"])

        assert success is True
        assert "hello" in output

    def test_run_command_failure(self):
        """Test running a failing command."""
        success, output = _run_command(["false"])

        assert success is False

    def test_run_command_not_found(self):
        """Test running a non-existent command."""
        success, output = _run_command(["nonexistent_command_xyz"])

        assert success is False
        assert "not found" in output.lower() or "error" in output.lower()

    def test_run_command_with_args(self):
        """Test running command with arguments."""
        success, output = _run_command(["echo", "-n", "test"])

        assert success is True
        assert "test" in output


class TestGetTechDebtTrend:
    """Tests for _get_tech_debt_trend function."""

    def test_trend_no_file(self):
        """Test trend when no file exists."""
        trend = _get_tech_debt_trend("/nonexistent/path")

        assert trend == "unknown"

    def test_trend_insufficient_data(self):
        """Test trend with insufficient snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "snapshots": [
                    {"total_items": 10, "date": "2025-01-01"},
                ],
            }
            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                json.dump(data, f)

            trend = _get_tech_debt_trend(tmpdir)

            assert trend == "insufficient_data"

    def test_trend_increasing(self):
        """Test detecting increasing trend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "snapshots": [
                    {"total_items": 10, "date": "2025-01-01"},
                    {"total_items": 15, "date": "2025-01-15"},
                ],
            }
            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                json.dump(data, f)

            trend = _get_tech_debt_trend(tmpdir)

            assert trend == "increasing"

    def test_trend_decreasing(self):
        """Test detecting decreasing trend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "snapshots": [
                    {"total_items": 20, "date": "2025-01-01"},
                    {"total_items": 10, "date": "2025-01-15"},
                ],
            }
            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                json.dump(data, f)

            trend = _get_tech_debt_trend(tmpdir)

            assert trend == "decreasing"

    def test_trend_stable(self):
        """Test detecting stable trend."""
        with tempfile.TemporaryDirectory() as tmpdir:
            data = {
                "snapshots": [
                    {"total_items": 10, "date": "2025-01-01"},
                    {"total_items": 10, "date": "2025-01-15"},
                ],
            }
            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                json.dump(data, f)

            trend = _get_tech_debt_trend(tmpdir)

            assert trend == "stable"


class TestWorkflowCommandsIntegration:
    """Integration tests for workflow commands."""

    def test_patterns_and_stats_workflow(self):
        """Test loading patterns and saving/loading stats."""
        with tempfile.TemporaryDirectory() as tmpdir:
            patterns_dir = Path(tmpdir) / "patterns"
            patterns_dir.mkdir()
            empathy_dir = Path(tmpdir) / ".empathy"

            # Create pattern file
            debugging_data = {"patterns": [{"id": "p1"}]}
            with open(patterns_dir / "debugging.json", "w") as f:
                json.dump(debugging_data, f)

            # Load patterns
            patterns = _load_patterns(str(patterns_dir))
            assert len(patterns["debugging"]) == 1

            # Save stats
            stats = {
                "commands": {"morning": 1},
                "patterns_learned": len(patterns["debugging"]),
            }
            _save_stats(stats, str(empathy_dir))

            # Load stats back
            loaded_stats = _load_stats(str(empathy_dir))
            assert loaded_stats["patterns_learned"] == 1
