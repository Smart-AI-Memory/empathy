"""
Tests for CLI Module

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from empathy_os import EmpathyConfig, Pattern, PatternLibrary
from empathy_os.cli import (
    cmd_info,
    cmd_init,
    cmd_metrics_show,
    cmd_patterns_export,
    cmd_patterns_list,
    cmd_state_list,
    cmd_validate,
    cmd_version,
)
from empathy_os.core import CollaborationState
from empathy_os.persistence import MetricsCollector, PatternPersistence, StateManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


class MockArgs:
    """Mock argparse.Namespace for testing"""

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TestCLIVersion:
    """Test version command"""

    def test_version_output(self, capsys):
        """Test version command output"""
        args = MockArgs()
        cmd_version(args)

        captured = capsys.readouterr()
        assert "Empathy Framework v1.0.0" in captured.out
        assert "Copyright 2025 Deep Study AI, LLC" in captured.out
        assert "Apache License" in captured.out


class TestCLIInit:
    """Test init command"""

    def test_init_yaml(self, temp_dir, capsys):
        """Test creating YAML config"""
        output_path = Path(temp_dir) / "test.yml"
        args = MockArgs(format="yaml", output=str(output_path))

        cmd_init(args)

        assert output_path.exists()
        captured = capsys.readouterr()
        assert "Created YAML configuration" in captured.out

    def test_init_json(self, temp_dir, capsys):
        """Test creating JSON config"""
        output_path = Path(temp_dir) / "test.json"
        args = MockArgs(format="json", output=str(output_path))

        cmd_init(args)

        assert output_path.exists()
        captured = capsys.readouterr()
        assert "Created JSON configuration" in captured.out

    def test_init_default_filename(self, temp_dir, capsys, monkeypatch):
        """Test default filename generation"""
        monkeypatch.chdir(temp_dir)
        args = MockArgs(format="yaml", output=None)

        cmd_init(args)

        assert Path(temp_dir, "empathy.config.yaml").exists()


class TestCLIValidate:
    """Test validate command"""

    def test_validate_valid_config(self, temp_dir, capsys):
        """Test validating a valid config"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="test_user", target_level=4)
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_validate(args)

        captured = capsys.readouterr()
        assert "Configuration valid" in captured.out
        assert "test_user" in captured.out

    def test_validate_invalid_config(self, temp_dir):
        """Test validating an invalid config"""
        config_path = Path(temp_dir) / "config.json"

        # Create invalid config (target_level out of range)
        with open(config_path, "w") as f:
            json.dump({"target_level": 10}, f)

        args = MockArgs(config=str(config_path))

        with pytest.raises(SystemExit):
            cmd_validate(args)


class TestCLIInfo:
    """Test info command"""

    def test_info_default_config(self, capsys):
        """Test info with default config"""
        args = MockArgs(config=None)
        cmd_info(args)

        captured = capsys.readouterr()
        assert "Empathy Framework Info" in captured.out
        assert "User ID:" in captured.out
        assert "Target Level:" in captured.out
        assert "Persistence:" in captured.out
        assert "Metrics:" in captured.out

    def test_info_custom_config(self, temp_dir, capsys):
        """Test info with custom config"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="alice", target_level=5)
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_info(args)

        captured = capsys.readouterr()
        assert "alice" in captured.out
        assert "Target Level: 5" in captured.out


class TestCLIPatternsCommands:
    """Test patterns commands"""

    def test_patterns_list_json(self, temp_dir, capsys):
        """Test listing patterns from JSON"""
        library = PatternLibrary()

        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test Pattern",
            description="A test pattern",
            context={"test": True},
            code="def test(): pass",
            tags=["test"],
        )

        library.contribute_pattern("agent1", pattern)

        library_path = Path(temp_dir) / "patterns.json"
        PatternPersistence.save_to_json(library, str(library_path))

        args = MockArgs(library=str(library_path), format="json")
        cmd_patterns_list(args)

        captured = capsys.readouterr()
        assert "Total patterns: 1" in captured.out
        assert "Test Pattern" in captured.out

    def test_patterns_list_not_found(self, temp_dir):
        """Test listing patterns from non-existent file"""
        args = MockArgs(library="/nonexistent.json", format="json")

        with pytest.raises(SystemExit):
            cmd_patterns_list(args)

    def test_patterns_export(self, temp_dir, capsys):
        """Test exporting patterns between formats"""
        library = PatternLibrary()

        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Export Test",
            description="Test pattern export",
            context={},
            code="pass",
            tags=[],
        )

        library.contribute_pattern("agent1", pattern)

        # Save to JSON
        json_path = Path(temp_dir) / "patterns.json"
        PatternPersistence.save_to_json(library, str(json_path))

        # Export to SQLite
        sqlite_path = Path(temp_dir) / "patterns.db"
        args = MockArgs(
            input=str(json_path),
            input_format="json",
            output=str(sqlite_path),
            output_format="sqlite",
        )

        cmd_patterns_export(args)

        captured = capsys.readouterr()
        assert "Loaded 1 patterns" in captured.out
        assert "Saved 1 patterns" in captured.out
        assert sqlite_path.exists()


class TestCLIMetricsCommands:
    """Test metrics commands"""

    def test_metrics_show(self, temp_dir, capsys):
        """Test showing user metrics"""
        db_path = Path(temp_dir) / "metrics.db"
        collector = MetricsCollector(str(db_path))

        # Record some metrics
        for i in range(5):
            collector.record_metric(
                user_id="test_user", empathy_level=3, success=True, response_time_ms=100.0 + i * 10
            )

        args = MockArgs(db=str(db_path), user="test_user")

        cmd_metrics_show(args)

        captured = capsys.readouterr()
        assert "Metrics for User: test_user" in captured.out
        assert "Total Operations: 5" in captured.out
        assert "Success Rate:" in captured.out


class TestCLIStateCommands:
    """Test state commands"""

    def test_state_list_empty(self, temp_dir, capsys):
        """Test listing states when none exist"""
        state_dir = Path(temp_dir) / "states"
        state_dir.mkdir()

        args = MockArgs(state_dir=str(state_dir))
        cmd_state_list(args)

        captured = capsys.readouterr()
        assert "Total users: 0" in captured.out

    def test_state_list_with_users(self, temp_dir, capsys):
        """Test listing states with saved users"""
        state_dir = Path(temp_dir) / "states"
        state_dir.mkdir()

        manager = StateManager(str(state_dir))

        # Save some states
        state1 = CollaborationState(trust_level=0.8)
        state2 = CollaborationState(trust_level=0.6)

        manager.save_state("alice", state1)
        manager.save_state("bob", state2)

        args = MockArgs(state_dir=str(state_dir))
        cmd_state_list(args)

        captured = capsys.readouterr()
        assert "Total users: 2" in captured.out
        assert "alice" in captured.out
        assert "bob" in captured.out


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling"""

    def test_patterns_list_unknown_format(self, temp_dir):
        """Test listing patterns with unknown format"""
        library_path = str(Path(temp_dir) / "test.txt")
        args = MockArgs(library=library_path, format="unknown")

        with pytest.raises(SystemExit):
            cmd_patterns_list(args)

    def test_patterns_export_sqlite_to_json(self, temp_dir, capsys):
        """Test exporting from SQLite to JSON"""
        library = PatternLibrary()

        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="SQLite Export Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )

        library.contribute_pattern("agent1", pattern)

        # Save to SQLite
        sqlite_path = Path(temp_dir) / "patterns.db"
        PatternPersistence.save_to_sqlite(library, str(sqlite_path))

        # Export to JSON
        json_path = Path(temp_dir) / "exported.json"
        args = MockArgs(
            input=str(sqlite_path),
            input_format="sqlite",
            output=str(json_path),
            output_format="json",
        )

        cmd_patterns_export(args)

        captured = capsys.readouterr()
        assert "Loaded 1 patterns" in captured.out
        assert "Saved 1 patterns" in captured.out
        assert json_path.exists()

    def test_validate_missing_file(self, capsys):
        """Test validating non-existent config file (falls back to defaults)"""
        args = MockArgs(config="/nonexistent/config.yml")

        # load_config falls back to defaults when file not found
        cmd_validate(args)

        captured = capsys.readouterr()
        assert "Configuration valid" in captured.out
        assert "default_user" in captured.out  # Should use default config

    def test_info_with_custom_config_values(self, temp_dir, capsys):
        """Test info displays custom configuration values"""
        config_path = Path(temp_dir) / "custom.json"
        config = EmpathyConfig(
            user_id="test_user",
            target_level=5,
            confidence_threshold=0.9,
            persistence_backend="json",
            metrics_enabled=False,
        )
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_info(args)

        captured = capsys.readouterr()
        assert "test_user" in captured.out
        assert "Target Level: 5" in captured.out
        assert "Confidence Threshold: 0.9" in captured.out
        assert "Backend: json" in captured.out
        assert "Enabled: False" in captured.out  # Metrics section shows "Enabled: False"

    def test_metrics_show_no_data(self, temp_dir, capsys):
        """Test showing metrics for user with no data"""
        db_path = Path(temp_dir) / "empty_metrics.db"
        collector = MetricsCollector(str(db_path))

        args = MockArgs(db=str(db_path), user="nonexistent_user")
        cmd_metrics_show(args)

        captured = capsys.readouterr()
        assert "Metrics for User: nonexistent_user" in captured.out
        assert "Total Operations: 0" in captured.out

    def test_patterns_list_sqlite(self, temp_dir, capsys):
        """Test listing patterns from SQLite"""
        library = PatternLibrary()

        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="SQLite Test Pattern",
            description="A test pattern in SQLite",
            context={"test": True},
            code="def test(): pass",
            tags=["test", "sqlite"],
        )

        library.contribute_pattern("agent1", pattern)

        library_path = Path(temp_dir) / "patterns.db"
        PatternPersistence.save_to_sqlite(library, str(library_path))

        args = MockArgs(library=str(library_path), format="sqlite")
        cmd_patterns_list(args)

        captured = capsys.readouterr()
        assert "Total patterns: 1" in captured.out
        assert "SQLite Test Pattern" in captured.out
        assert "agent1" in captured.out
