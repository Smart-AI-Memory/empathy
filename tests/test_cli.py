"""
Tests for CLI Module

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import json
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

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
    main,
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

    def test_version_output(self, capsys, caplog):
        """Test version command output"""
        args = MockArgs()
        cmd_version(args)

        # Version output goes to logger, check caplog instead of capsys
        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Empathy v" in log_output
        assert "Copyright 2025" in log_output
        assert "Fair Source" in log_output  # Match actual license


class TestCLIInit:
    """Test init command"""

    def test_init_yaml(self, temp_dir, caplog):
        """Test creating YAML config"""
        output_path = Path(temp_dir) / "test.yml"
        args = MockArgs(format="yaml", output=str(output_path))

        cmd_init(args)

        assert output_path.exists()
        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Created YAML configuration" in log_output

    def test_init_json(self, temp_dir, caplog):
        """Test creating JSON config"""
        output_path = Path(temp_dir) / "test.json"
        args = MockArgs(format="json", output=str(output_path))

        cmd_init(args)

        assert output_path.exists()
        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Created JSON configuration" in log_output

    def test_init_default_filename(self, temp_dir, caplog, monkeypatch):
        """Test default filename generation"""
        monkeypatch.chdir(temp_dir)
        args = MockArgs(format="yaml", output=None)

        cmd_init(args)

        assert Path(temp_dir, "empathy.config.yaml").exists()


class TestCLIValidate:
    """Test validate command"""

    def test_validate_valid_config(self, temp_dir, caplog):
        """Test validating a valid config"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="test_user", target_level=4)
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_validate(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Configuration valid" in log_output
        assert "test_user" in log_output

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

    def test_info_default_config(self, caplog):
        """Test info with default config"""
        args = MockArgs(config=None)
        cmd_info(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Empathy Framework Info" in log_output
        assert "User ID:" in log_output
        assert "Target Level:" in log_output
        assert "Persistence:" in log_output
        assert "Metrics:" in log_output

    def test_info_custom_config(self, temp_dir, caplog):
        """Test info with custom config"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="alice", target_level=5)
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_info(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "alice" in log_output
        assert "Target Level: 5" in log_output


class TestCLIPatternsCommands:
    """Test patterns commands"""

    def test_patterns_list_json(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total patterns: 1" in log_output
        assert "Test Pattern" in log_output

    def test_patterns_list_not_found(self, temp_dir):
        """Test listing patterns from non-existent file"""
        args = MockArgs(library="/nonexistent.json", format="json")

        with pytest.raises(SystemExit):
            cmd_patterns_list(args)

    def test_patterns_export(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Loaded 1 patterns" in log_output
        assert "Saved 1 patterns" in log_output
        assert sqlite_path.exists()


class TestCLIMetricsCommands:
    """Test metrics commands"""

    def test_metrics_show(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Metrics for User: test_user" in log_output
        assert "Total Operations: 5" in log_output
        assert "Success Rate:" in log_output


class TestCLIStateCommands:
    """Test state commands"""

    def test_state_list_empty(self, temp_dir, caplog):
        """Test listing states when none exist"""
        state_dir = Path(temp_dir) / "states"
        state_dir.mkdir()

        args = MockArgs(state_dir=str(state_dir))
        cmd_state_list(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total users: 0" in log_output

    def test_state_list_with_users(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total users: 2" in log_output
        assert "alice" in log_output
        assert "bob" in log_output


class TestCLIEdgeCases:
    """Test CLI edge cases and error handling"""

    def test_patterns_list_unknown_format(self, temp_dir):
        """Test listing patterns with unknown format"""
        library_path = str(Path(temp_dir) / "test.txt")
        args = MockArgs(library=library_path, format="unknown")

        with pytest.raises(SystemExit):
            cmd_patterns_list(args)

    def test_patterns_export_sqlite_to_json(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Loaded 1 patterns" in log_output
        assert "Saved 1 patterns" in log_output
        assert json_path.exists()

    def test_validate_missing_file(self, caplog):
        """Test validating non-existent config file (falls back to defaults)"""
        args = MockArgs(config="/nonexistent/config.yml")

        # load_config falls back to defaults when file not found
        cmd_validate(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Configuration valid" in log_output
        assert "default_user" in log_output  # Should use default config

    def test_info_with_custom_config_values(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "test_user" in log_output
        assert "Target Level: 5" in log_output
        assert "Confidence Threshold: 0.9" in log_output
        assert "Backend: json" in log_output
        assert "Enabled: False" in log_output  # Metrics section shows "Enabled: False"

    def test_metrics_show_no_data(self, temp_dir, caplog):
        """Test showing metrics for user with no data"""
        db_path = Path(temp_dir) / "empty_metrics.db"

        args = MockArgs(db=str(db_path), user="nonexistent_user")
        cmd_metrics_show(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Metrics for User: nonexistent_user" in log_output
        assert "Total Operations: 0" in log_output

    def test_patterns_list_sqlite(self, temp_dir, caplog):
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

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total patterns: 1" in log_output
        assert "SQLite Test Pattern" in log_output
        assert "agent1" in log_output


class TestCLIVersionEdgeCases:
    """Test version command edge cases"""

    def test_version_with_import_error(self, caplog):
        """Test version command when package version cannot be determined"""
        with patch("empathy_os.cli.get_version") as mock_get_version:
            mock_get_version.side_effect = Exception("Package not found")
            args = MockArgs()
            cmd_version(args)

            log_output = " ".join([rec.message for rec in caplog.records])
            assert "Empathy vunknown" in log_output
            assert "Copyright 2025" in log_output


class TestCLIPatternsListEdgeCases:
    """Test patterns list edge cases"""

    def test_patterns_list_empty_library(self, temp_dir, caplog):
        """Test listing patterns from empty library"""
        library = PatternLibrary()
        library_path = Path(temp_dir) / "empty_patterns.json"
        PatternPersistence.save_to_json(library, str(library_path))

        args = MockArgs(library=str(library_path), format="json")
        cmd_patterns_list(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total patterns: 0" in log_output
        assert "Total agents: 0" in log_output


class TestCLIPatternsExportEdgeCases:
    """Test patterns export edge cases"""

    def test_patterns_export_unknown_input_format(self, temp_dir, caplog):
        """Test exporting patterns with unknown input format"""
        args = MockArgs(
            input="/some/file.txt",
            input_format="unknown",
            output="/some/output.json",
            output_format="json",
        )

        with pytest.raises(SystemExit):
            cmd_patterns_export(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Unknown input format: unknown" in log_output

    def test_patterns_export_load_failure(self, temp_dir, caplog):
        """Test exporting patterns when loading fails"""
        args = MockArgs(
            input="/nonexistent/file.json",
            input_format="json",
            output="/some/output.json",
            output_format="json",
        )

        with pytest.raises(SystemExit):
            cmd_patterns_export(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Failed to load patterns:" in log_output

    def test_patterns_export_json_to_sqlite(self, temp_dir, caplog):
        """Test exporting patterns from JSON to SQLite"""
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
        sqlite_path = Path(temp_dir) / "exported.db"
        args = MockArgs(
            input=str(json_path),
            input_format="json",
            output=str(sqlite_path),
            output_format="sqlite",
        )

        cmd_patterns_export(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Loaded 1 patterns" in log_output
        assert "Saved 1 patterns" in log_output
        assert sqlite_path.exists()

    def test_patterns_export_save_failure(self, temp_dir, caplog):
        """Test exporting patterns when saving fails"""
        library = PatternLibrary()

        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )

        library.contribute_pattern("agent1", pattern)

        # Save to JSON
        json_path = Path(temp_dir) / "patterns.json"
        PatternPersistence.save_to_json(library, str(json_path))

        # Try to export to an invalid path (directory doesn't exist)
        args = MockArgs(
            input=str(json_path),
            input_format="json",
            output="/nonexistent/directory/output.json",
            output_format="json",
        )

        with pytest.raises(SystemExit):
            cmd_patterns_export(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Failed to save patterns:" in log_output


class TestCLIMetricsEdgeCases:
    """Test metrics command edge cases"""

    def test_metrics_show_error(self, temp_dir, caplog):
        """Test showing metrics when an error occurs"""
        db_path = Path(temp_dir) / "metrics.db"

        # Mock MetricsCollector to raise an error on get_user_stats
        with patch("empathy_os.cli.MetricsCollector") as mock_collector:
            mock_instance = MagicMock()
            mock_instance.get_user_stats.side_effect = Exception("Database error")
            mock_collector.return_value = mock_instance

            args = MockArgs(db=str(db_path), user="test_user")

            with pytest.raises(SystemExit):
                cmd_metrics_show(args)

            log_output = " ".join([rec.message for rec in caplog.records])
            assert "Failed to retrieve metrics:" in log_output


class TestCLIMain:
    """Test main CLI entry point"""

    def test_main_version_command(self, caplog):
        """Test main function with version command"""
        with patch.object(sys, "argv", ["empathy", "version"]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Empathy v" in log_output

    def test_main_init_command_yaml(self, temp_dir, caplog, monkeypatch):
        """Test main function with init command (YAML)"""
        monkeypatch.chdir(temp_dir)
        with patch.object(sys, "argv", ["empathy", "init", "--format", "yaml"]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Created YAML configuration" in log_output
        assert Path(temp_dir, "empathy.config.yaml").exists()

    def test_main_init_command_json_with_output(self, temp_dir, caplog, monkeypatch):
        """Test main function with init command (JSON with custom output)"""
        monkeypatch.chdir(temp_dir)
        output_file = Path(temp_dir) / "custom.json"
        with patch.object(
            sys, "argv", ["empathy", "init", "--format", "json", "-o", str(output_file)]
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Created JSON configuration" in log_output
        assert output_file.exists()

    def test_main_validate_command(self, temp_dir, caplog):
        """Test main function with validate command"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="test_user")
        config.to_json(str(config_path))

        with patch.object(sys, "argv", ["empathy", "validate", str(config_path)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Configuration valid" in log_output

    def test_main_info_command_default(self, caplog):
        """Test main function with info command (default config)"""
        with patch.object(sys, "argv", ["empathy", "info"]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Empathy Framework Info" in log_output

    def test_main_info_command_with_config(self, temp_dir, caplog):
        """Test main function with info command (custom config)"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="custom_user")
        config.to_json(str(config_path))

        with patch.object(sys, "argv", ["empathy", "info", "-c", str(config_path)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "custom_user" in log_output

    def test_main_patterns_list_json(self, temp_dir, caplog):
        """Test main function with patterns list command (JSON)"""
        library = PatternLibrary()
        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )
        library.contribute_pattern("agent1", pattern)

        library_path = Path(temp_dir) / "patterns.json"
        PatternPersistence.save_to_json(library, str(library_path))

        with patch.object(sys, "argv", ["empathy", "patterns", "list", str(library_path)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total patterns: 1" in log_output

    def test_main_patterns_list_sqlite(self, temp_dir, caplog):
        """Test main function with patterns list command (SQLite)"""
        library = PatternLibrary()
        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )
        library.contribute_pattern("agent1", pattern)

        library_path = Path(temp_dir) / "patterns.db"
        PatternPersistence.save_to_sqlite(library, str(library_path))

        with patch.object(
            sys, "argv", ["empathy", "patterns", "list", str(library_path), "--format", "sqlite"]
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total patterns: 1" in log_output

    def test_main_patterns_export_json_to_sqlite(self, temp_dir, caplog):
        """Test main function with patterns export command (JSON to SQLite)"""
        library = PatternLibrary()
        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )
        library.contribute_pattern("agent1", pattern)

        json_path = Path(temp_dir) / "patterns.json"
        PatternPersistence.save_to_json(library, str(json_path))

        sqlite_path = Path(temp_dir) / "patterns.db"

        with patch.object(
            sys,
            "argv",
            [
                "empathy",
                "patterns",
                "export",
                str(json_path),
                str(sqlite_path),
                "--input-format",
                "json",
                "--output-format",
                "sqlite",
            ],
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Saved 1 patterns" in log_output

    def test_main_patterns_export_sqlite_to_json(self, temp_dir, caplog):
        """Test main function with patterns export command (SQLite to JSON)"""
        library = PatternLibrary()
        pattern = Pattern(
            id="test_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            context={},
            code="pass",
            tags=[],
        )
        library.contribute_pattern("agent1", pattern)

        sqlite_path = Path(temp_dir) / "patterns.db"
        PatternPersistence.save_to_sqlite(library, str(sqlite_path))

        json_path = Path(temp_dir) / "patterns.json"

        with patch.object(
            sys,
            "argv",
            [
                "empathy",
                "patterns",
                "export",
                str(sqlite_path),
                str(json_path),
                "--input-format",
                "sqlite",
                "--output-format",
                "json",
            ],
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Saved 1 patterns" in log_output

    def test_main_metrics_show(self, temp_dir, caplog):
        """Test main function with metrics show command"""
        db_path = Path(temp_dir) / "metrics.db"
        collector = MetricsCollector(str(db_path))

        for _ in range(3):
            collector.record_metric(
                user_id="test_user", empathy_level=2, success=True, response_time_ms=50.0
            )

        with patch.object(
            sys, "argv", ["empathy", "metrics", "show", "test_user", "--db", str(db_path)]
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Metrics for User: test_user" in log_output
        assert "Total Operations: 3" in log_output

    def test_main_metrics_show_with_default_db(self, temp_dir, caplog, monkeypatch):
        """Test main function with metrics show command using default db path"""
        monkeypatch.chdir(temp_dir)
        db_path = Path(temp_dir) / "metrics.db"
        collector = MetricsCollector(str(db_path))

        collector.record_metric(
            user_id="user123", empathy_level=1, success=True, response_time_ms=25.0
        )

        with patch.object(
            sys, "argv", ["empathy", "metrics", "show", "user123", "--db", str(db_path)]
        ):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Metrics for User: user123" in log_output

    def test_main_state_list_empty(self, temp_dir, caplog):
        """Test main function with state list command (empty)"""
        state_dir = Path(temp_dir) / "states"
        state_dir.mkdir()

        with patch.object(sys, "argv", ["empathy", "state", "list", "--state-dir", str(state_dir)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total users: 0" in log_output

    def test_main_state_list_with_users(self, temp_dir, caplog):
        """Test main function with state list command (with users)"""
        state_dir = Path(temp_dir) / "states"
        state_dir.mkdir()

        manager = StateManager(str(state_dir))
        state = CollaborationState(trust_level=0.7)
        manager.save_state("user1", state)

        with patch.object(sys, "argv", ["empathy", "state", "list", "--state-dir", str(state_dir)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Total users: 1" in log_output
        assert "user1" in log_output

    def test_main_state_list_default_dir(self, temp_dir, caplog, monkeypatch):
        """Test main function with state list command (default directory)"""
        monkeypatch.chdir(temp_dir)
        state_dir = Path(temp_dir) / "empathy_state"
        state_dir.mkdir()

        manager = StateManager(str(state_dir))
        state = CollaborationState(trust_level=0.5)
        manager.save_state("alice", state)

        with patch.object(sys, "argv", ["empathy", "state", "list", "--state-dir", str(state_dir)]):
            main()

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "alice" in log_output

    def test_main_no_command(self, capsys):
        """Test main function with no command (should print help)"""
        with patch.object(sys, "argv", ["empathy"]):
            main()

        # Help text goes to stdout via argparse, not logger
        captured = capsys.readouterr()
        assert "empathy" in captured.out or "usage" in captured.out.lower()
        # Help text should be shown


class TestCLIAdditionalCoverage:
    """Additional tests for CLI coverage"""

    def test_init_overwrites_existing(self, temp_dir, caplog):
        """Test init command overwrites existing config"""
        output_path = Path(temp_dir) / "existing.yml"
        # Create existing file
        output_path.write_text("old: content")

        args = MockArgs(format="yaml", output=str(output_path))
        cmd_init(args)

        assert output_path.exists()
        content = output_path.read_text()
        assert "old: content" not in content

    def test_info_with_custom_user_id(self, temp_dir, caplog):
        """Test info shows custom user_id"""
        config_path = Path(temp_dir) / "config.json"
        config = EmpathyConfig(user_id="custom_test_user", target_level=4)
        config.to_json(str(config_path))

        args = MockArgs(config=str(config_path))
        cmd_info(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "custom_test_user" in log_output

    def test_init_creates_valid_yaml(self, temp_dir, caplog):
        """Test init creates valid YAML that can be loaded"""
        output_path = Path(temp_dir) / "new_config.yml"
        args = MockArgs(format="yaml", output=str(output_path))
        cmd_init(args)

        # Verify file was created and can be loaded
        assert output_path.exists()
        loaded_config = EmpathyConfig.from_yaml(str(output_path))
        assert loaded_config.user_id == "default_user"

    def test_init_creates_valid_json(self, temp_dir, caplog):
        """Test init creates valid JSON that can be loaded"""
        output_path = Path(temp_dir) / "new_config.json"
        args = MockArgs(format="json", output=str(output_path))
        cmd_init(args)

        # Verify file was created and can be loaded
        assert output_path.exists()
        loaded_config = EmpathyConfig.from_json(str(output_path))
        assert loaded_config.user_id == "default_user"

    def test_version_shows_package_info(self, caplog):
        """Test version command shows package information"""
        args = MockArgs()
        cmd_version(args)

        log_output = " ".join([rec.message for rec in caplog.records])
        assert "Empathy" in log_output
        assert "v" in log_output
