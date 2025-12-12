"""
Comprehensive tests for Memory Control Panel Module

Tests cover:
- Control panel initialization
- Status checking
- Redis lifecycle management
- Statistics collection
- Pattern management
- Export/import capabilities
- Health checks
- CLI interface

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from empathy_os.memory.control_panel import (
    ControlPanelConfig,
    MemoryControlPanel,
    MemoryStats,
    main,
    print_health,
    print_stats,
    print_status,
)
from empathy_os.memory.redis_bootstrap import RedisStartMethod, RedisStatus


class TestMemoryStats:
    """Test MemoryStats dataclass"""

    def test_memory_stats_creation(self):
        """Test creating MemoryStats with all fields"""
        stats = MemoryStats(
            redis_available=True,
            redis_method="homebrew",
            redis_keys_total=100,
            redis_keys_working=50,
            redis_keys_staged=10,
            redis_memory_used="1.5MB",
            long_term_available=True,
            patterns_total=25,
            patterns_public=10,
            patterns_internal=10,
            patterns_sensitive=5,
            patterns_encrypted=5,
            collected_at="2025-01-01T00:00:00Z",
        )
        assert stats.redis_available is True
        assert stats.redis_keys_total == 100
        assert stats.patterns_total == 25

    def test_memory_stats_defaults(self):
        """Test MemoryStats default values"""
        stats = MemoryStats()
        assert stats.redis_available is False
        assert stats.redis_keys_total == 0
        assert stats.patterns_total == 0
        assert stats.collected_at == ""


class TestControlPanelConfig:
    """Test ControlPanelConfig dataclass"""

    def test_control_panel_config_defaults(self):
        """Test default configuration values"""
        config = ControlPanelConfig()
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.storage_dir == "./memdocs_storage"
        assert config.audit_dir == "./logs"
        assert config.auto_start_redis is True

    def test_control_panel_config_custom(self):
        """Test custom configuration values"""
        config = ControlPanelConfig(
            redis_host="192.168.1.100",
            redis_port=6380,
            storage_dir="/custom/storage",
            audit_dir="/custom/logs",
            auto_start_redis=False,
        )
        assert config.redis_host == "192.168.1.100"
        assert config.redis_port == 6380
        assert config.storage_dir == "/custom/storage"
        assert config.auto_start_redis is False


class TestMemoryControlPanelInit:
    """Test MemoryControlPanel initialization"""

    def test_init_with_default_config(self):
        """Test initialization with default config"""
        panel = MemoryControlPanel()
        assert panel.config is not None
        assert panel.config.redis_host == "localhost"
        assert panel._redis_status is None
        assert panel._short_term is None
        assert panel._long_term is None

    def test_init_with_custom_config(self):
        """Test initialization with custom config"""
        config = ControlPanelConfig(redis_host="custom-host", redis_port=6380)
        panel = MemoryControlPanel(config)
        assert panel.config.redis_host == "custom-host"
        assert panel.config.redis_port == 6380


class TestMemoryControlPanelStatus:
    """Test status() method"""

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_status_redis_running(self, mock_path, mock_check):
        """Test status when Redis is running"""
        mock_check.return_value = True
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()
        panel._redis_status = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        with patch.object(panel, "_count_patterns", return_value=10):
            status = panel.status()

        assert status["redis"]["status"] == "running"
        assert status["redis"]["method"] == "homebrew"
        assert status["long_term"]["pattern_count"] == 10

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_status_redis_stopped(self, mock_path, mock_check):
        """Test status when Redis is stopped"""
        mock_check.return_value = False
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()
        status = panel.status()

        assert status["redis"]["status"] == "stopped"
        assert status["long_term"]["status"] == "not_initialized"

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_status_includes_timestamp(self, mock_path, mock_check):
        """Test status includes timestamp"""
        mock_check.return_value = False
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()
        status = panel.status()

        assert "timestamp" in status
        assert status["timestamp"].endswith("Z")


class TestMemoryControlPanelRedis:
    """Test Redis lifecycle management"""

    @patch("empathy_os.memory.control_panel.ensure_redis")
    def test_start_redis_success(self, mock_ensure):
        """Test successful Redis start"""
        mock_status = RedisStatus(
            available=True,
            method=RedisStartMethod.HOMEBREW,
            message="Started successfully",
        )
        mock_ensure.return_value = mock_status

        panel = MemoryControlPanel()
        status = panel.start_redis(verbose=False)

        assert status.available is True
        assert status.method == RedisStartMethod.HOMEBREW
        assert panel._redis_status == mock_status

    @patch("empathy_os.memory.control_panel.ensure_redis")
    def test_start_redis_failure(self, mock_ensure):
        """Test Redis start failure"""
        mock_status = RedisStatus(
            available=False, method=RedisStartMethod.MOCK, message="Failed to start"
        )
        mock_ensure.return_value = mock_status

        panel = MemoryControlPanel()
        status = panel.start_redis(verbose=False)

        assert status.available is False
        assert status.method == RedisStartMethod.MOCK

    @patch("empathy_os.memory.control_panel.stop_redis")
    def test_stop_redis_success(self, mock_stop):
        """Test successful Redis stop"""
        mock_stop.return_value = True

        panel = MemoryControlPanel()
        panel._redis_status = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        result = panel.stop_redis()
        assert result is True
        mock_stop.assert_called_once_with(RedisStartMethod.HOMEBREW)

    @patch("empathy_os.memory.control_panel.stop_redis")
    def test_stop_redis_already_running(self, mock_stop):
        """Test stop Redis that was already running"""
        panel = MemoryControlPanel()
        panel._redis_status = RedisStatus(available=True, method=RedisStartMethod.ALREADY_RUNNING)

        result = panel.stop_redis()
        assert result is False
        mock_stop.assert_not_called()

    def test_stop_redis_no_status(self):
        """Test stop Redis when status is None"""
        panel = MemoryControlPanel()
        result = panel.stop_redis()
        assert result is False


class TestMemoryControlPanelStatistics:
    """Test get_statistics() method"""

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_statistics_redis_available(self, mock_check):
        """Test statistics with Redis available"""
        mock_check.return_value = True

        panel = MemoryControlPanel()
        mock_short_term = Mock()
        mock_short_term.get_stats.return_value = {
            "mode": "redis",
            "total_keys": 100,
            "working_keys": 50,
            "staged_keys": 10,
            "used_memory": "2.5MB",
        }
        panel._short_term = mock_short_term

        with tempfile.TemporaryDirectory() as tmpdir:
            panel.config.storage_dir = tmpdir
            mock_long_term = Mock()
            mock_long_term.get_statistics.return_value = {
                "total_patterns": 25,
                "by_classification": {"PUBLIC": 10, "INTERNAL": 10, "SENSITIVE": 5},
                "encrypted_count": 5,
            }
            panel._long_term = mock_long_term

            stats = panel.get_statistics()

        assert stats.redis_available is True
        assert stats.redis_keys_total == 100
        assert stats.patterns_total == 25
        assert stats.patterns_sensitive == 5

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_statistics_redis_unavailable(self, mock_check):
        """Test statistics with Redis unavailable"""
        mock_check.return_value = False

        panel = MemoryControlPanel()
        stats = panel.get_statistics()

        assert stats.redis_available is False
        assert stats.redis_keys_total == 0

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_statistics_handles_redis_exception(self, mock_check):
        """Test statistics handles Redis exception gracefully"""
        mock_check.return_value = True

        panel = MemoryControlPanel()
        mock_short_term = Mock()
        mock_short_term.get_stats.side_effect = Exception("Redis error")
        panel._short_term = mock_short_term

        stats = panel.get_statistics()
        # Should continue despite error
        assert stats is not None


class TestMemoryControlPanelPatterns:
    """Test pattern management methods"""

    def test_list_patterns(self):
        """Test listing patterns"""
        panel = MemoryControlPanel()
        mock_long_term = Mock()
        mock_long_term.list_patterns.return_value = [
            {"pattern_id": "pat_1", "classification": "PUBLIC"},
            {"pattern_id": "pat_2", "classification": "INTERNAL"},
        ]
        panel._long_term = mock_long_term

        patterns = panel.list_patterns()
        assert len(patterns) == 2
        assert patterns[0]["pattern_id"] == "pat_1"

    def test_list_patterns_with_classification_filter(self):
        """Test listing patterns with classification filter"""
        panel = MemoryControlPanel()
        mock_long_term = Mock()
        mock_long_term.list_patterns.return_value = [
            {"pattern_id": "pat_1", "classification": "PUBLIC"}
        ]
        panel._long_term = mock_long_term

        panel.list_patterns(classification="PUBLIC")
        mock_long_term.list_patterns.assert_called_once()

    def test_list_patterns_with_limit(self):
        """Test listing patterns with limit"""
        panel = MemoryControlPanel()
        mock_long_term = Mock()
        mock_long_term.list_patterns.return_value = [{"pattern_id": f"pat_{i}"} for i in range(200)]
        panel._long_term = mock_long_term

        patterns = panel.list_patterns(limit=50)
        assert len(patterns) == 50

    def test_delete_pattern_success(self):
        """Test successful pattern deletion"""
        panel = MemoryControlPanel()
        mock_long_term = Mock()
        mock_long_term.delete_pattern.return_value = True
        panel._long_term = mock_long_term

        result = panel.delete_pattern("pat_123", "user@test.com")
        assert result is True

    def test_delete_pattern_failure(self):
        """Test pattern deletion failure"""
        panel = MemoryControlPanel()
        mock_long_term = Mock()
        mock_long_term.delete_pattern.side_effect = Exception("Delete failed")
        panel._long_term = mock_long_term

        result = panel.delete_pattern("pat_123", "user@test.com")
        assert result is False

    def test_clear_short_term(self):
        """Test clearing short-term memory"""
        panel = MemoryControlPanel()
        mock_short_term = Mock()
        mock_short_term.clear_working_memory.return_value = 10
        panel._short_term = mock_short_term

        count = panel.clear_short_term(agent_id="test_agent")
        assert count == 10


class TestMemoryControlPanelExport:
    """Test export functionality"""

    def test_export_patterns(self):
        """Test exporting patterns to JSON"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_path = f.name

        try:
            panel = MemoryControlPanel()
            mock_long_term = Mock()
            mock_long_term.list_patterns.return_value = [
                {"pattern_id": "pat_1", "classification": "PUBLIC"},
                {"pattern_id": "pat_2", "classification": "INTERNAL"},
            ]
            panel._long_term = mock_long_term

            count = panel.export_patterns(output_path)
            assert count == 2

            # Verify file contents
            with open(output_path) as f:
                data = json.load(f)
                assert data["pattern_count"] == 2
                assert "exported_at" in data
                assert len(data["patterns"]) == 2

        finally:
            Path(output_path).unlink(missing_ok=True)

    def test_export_patterns_with_classification_filter(self):
        """Test exporting patterns with classification filter"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            output_path = f.name

        try:
            panel = MemoryControlPanel()
            mock_long_term = Mock()
            mock_long_term.list_patterns.return_value = [
                {"pattern_id": "pat_1", "classification": "PUBLIC"}
            ]
            panel._long_term = mock_long_term

            count = panel.export_patterns(output_path, classification="PUBLIC")
            assert count == 1

            with open(output_path) as f:
                data = json.load(f)
                assert data["classification_filter"] == "PUBLIC"

        finally:
            Path(output_path).unlink(missing_ok=True)


class TestMemoryControlPanelHealthCheck:
    """Test health_check() method"""

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_health_check_all_healthy(self, mock_path, mock_check):
        """Test health check when everything is healthy"""
        mock_check.return_value = True
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()
        panel._redis_status = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        with patch.object(panel, "_count_patterns", return_value=10):
            with patch.object(
                panel,
                "get_statistics",
                return_value=MemoryStats(
                    redis_available=True,
                    long_term_available=True,
                    patterns_total=10,
                    patterns_sensitive=5,
                    patterns_encrypted=5,
                ),
            ):
                health = panel.health_check()

        assert health["overall"] == "healthy"
        assert len(health["checks"]) > 0
        assert all(c["status"] in ["pass", "info"] for c in health["checks"])

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_health_check_redis_down(self, mock_path, mock_check):
        """Test health check when Redis is down"""
        mock_check.return_value = False
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()

        with patch.object(panel, "_count_patterns", return_value=0):
            with patch.object(
                panel,
                "get_statistics",
                return_value=MemoryStats(redis_available=False),
            ):
                health = panel.health_check()

        assert health["overall"] == "degraded"
        assert any("redis" in c["name"] for c in health["checks"])
        assert len(health["recommendations"]) > 0

    @patch("empathy_os.memory.control_panel._check_redis_running")
    @patch("empathy_os.memory.control_panel.Path")
    def test_health_check_encryption_issue(self, mock_path, mock_check):
        """Test health check when sensitive patterns aren't encrypted"""
        mock_check.return_value = True
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance

        panel = MemoryControlPanel()
        panel._redis_status = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        with patch.object(panel, "_count_patterns", return_value=10):
            with patch.object(
                panel,
                "get_statistics",
                return_value=MemoryStats(
                    redis_available=True,
                    long_term_available=True,
                    patterns_total=10,
                    patterns_sensitive=5,
                    patterns_encrypted=0,  # Not encrypted!
                ),
            ):
                health = panel.health_check()

        assert health["overall"] == "unhealthy"
        assert any(c["status"] == "fail" for c in health["checks"])


class TestMemoryControlPanelInternalMethods:
    """Test internal/private methods"""

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_short_term_creates_instance(self, mock_check):
        """Test _get_short_term creates instance on first call"""
        mock_check.return_value = True

        panel = MemoryControlPanel()
        assert panel._short_term is None

        memory = panel._get_short_term()
        assert memory is not None
        assert panel._short_term is not None

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_short_term_reuses_instance(self, mock_check):
        """Test _get_short_term reuses existing instance"""
        mock_check.return_value = True

        panel = MemoryControlPanel()
        memory1 = panel._get_short_term()
        memory2 = panel._get_short_term()
        assert memory1 is memory2

    def test_get_long_term_creates_instance(self):
        """Test _get_long_term creates instance on first call"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ControlPanelConfig(storage_dir=tmpdir)
            panel = MemoryControlPanel(config)
            assert panel._long_term is None

            memory = panel._get_long_term()
            assert memory is not None
            assert panel._long_term is not None

    def test_count_patterns(self):
        """Test _count_patterns counts JSON files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = ControlPanelConfig(storage_dir=tmpdir)
            panel = MemoryControlPanel(config)

            # Create some test pattern files
            Path(tmpdir, "pat_1.json").write_text("{}")
            Path(tmpdir, "pat_2.json").write_text("{}")
            Path(tmpdir, "not_pattern.txt").write_text("")

            count = panel._count_patterns()
            assert count == 2

    def test_count_patterns_no_storage(self):
        """Test _count_patterns when storage doesn't exist"""
        config = ControlPanelConfig(storage_dir="/nonexistent/path")
        panel = MemoryControlPanel(config)

        count = panel._count_patterns()
        assert count == 0


class TestPrintFunctions:
    """Test CLI print functions"""

    def test_print_status(self, capsys):
        """Test print_status function"""
        panel = Mock()
        panel.status.return_value = {
            "timestamp": "2025-01-01T00:00:00Z",
            "redis": {
                "status": "running",
                "host": "localhost",
                "port": 6379,
                "method": "homebrew",
            },
            "long_term": {
                "status": "available",
                "storage_dir": "./storage",
                "pattern_count": 10,
            },
            "config": {"auto_start_redis": True, "audit_dir": "./logs"},
        }

        print_status(panel)
        captured = capsys.readouterr()
        assert "EMPATHY MEMORY STATUS" in captured.out
        assert "Redis: RUNNING" in captured.out

    def test_print_stats(self, capsys):
        """Test print_stats function"""
        panel = Mock()
        stats = MemoryStats(
            redis_available=True,
            redis_keys_total=100,
            patterns_total=25,
            patterns_sensitive=5,
        )
        panel.get_statistics.return_value = stats

        print_stats(panel)
        captured = capsys.readouterr()
        assert "EMPATHY MEMORY STATISTICS" in captured.out
        assert "Total patterns: 25" in captured.out

    def test_print_health(self, capsys):
        """Test print_health function"""
        panel = Mock()
        panel.health_check.return_value = {
            "overall": "healthy",
            "checks": [{"name": "redis", "status": "pass", "message": "Redis is running"}],
            "recommendations": [],
        }

        print_health(panel)
        captured = capsys.readouterr()
        assert "EMPATHY MEMORY HEALTH CHECK" in captured.out
        assert "HEALTHY" in captured.out


class TestCLIMain:
    """Test CLI main function"""

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "status"])
    def test_cli_status_command(self, mock_panel_class):
        """Test CLI status command"""
        mock_panel = Mock()
        mock_panel.status.return_value = {
            "timestamp": "2025-01-01T00:00:00Z",
            "redis": {
                "status": "running",
                "host": "localhost",
                "port": 6379,
                "method": "homebrew",
            },
            "long_term": {
                "status": "available",
                "storage_dir": "./storage",
                "pattern_count": 10,
            },
            "config": {"auto_start_redis": True, "audit_dir": "./logs"},
        }
        mock_panel_class.return_value = mock_panel

        with patch("empathy_os.memory.control_panel.print_status") as mock_print:
            main()
            mock_print.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "status", "--json"])
    def test_cli_status_json_output(self, mock_panel_class, capsys):
        """Test CLI status command with JSON output"""
        mock_panel = Mock()
        mock_panel.status.return_value = {"redis": {"status": "running"}}
        mock_panel_class.return_value = mock_panel

        main()
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "redis" in data

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "start"])
    def test_cli_start_command_success(self, mock_panel_class):
        """Test CLI start command"""
        mock_panel = Mock()
        mock_panel.start_redis.return_value = RedisStatus(
            available=True, method=RedisStartMethod.HOMEBREW
        )
        mock_panel_class.return_value = mock_panel

        main()
        mock_panel.start_redis.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "start"])
    def test_cli_start_command_failure(self, mock_panel_class):
        """Test CLI start command failure"""
        mock_panel = Mock()
        mock_panel.start_redis.return_value = RedisStatus(
            available=False, method=RedisStartMethod.MOCK, message="Failed"
        )
        mock_panel_class.return_value = mock_panel

        with pytest.raises(SystemExit):
            main()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "stop"])
    def test_cli_stop_command(self, mock_panel_class):
        """Test CLI stop command"""
        mock_panel = Mock()
        mock_panel.stop_redis.return_value = True
        mock_panel_class.return_value = mock_panel

        main()
        mock_panel.stop_redis.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "stats"])
    def test_cli_stats_command(self, mock_panel_class):
        """Test CLI stats command"""
        mock_panel = Mock()
        mock_panel.get_statistics.return_value = MemoryStats()
        mock_panel_class.return_value = mock_panel

        with patch("empathy_os.memory.control_panel.print_stats") as mock_print:
            main()
            mock_print.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "health"])
    def test_cli_health_command(self, mock_panel_class):
        """Test CLI health command"""
        mock_panel = Mock()
        mock_panel.health_check.return_value = {"overall": "healthy", "checks": []}
        mock_panel_class.return_value = mock_panel

        with patch("empathy_os.memory.control_panel.print_health") as mock_print:
            main()
            mock_print.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "patterns"])
    def test_cli_patterns_command(self, mock_panel_class):
        """Test CLI patterns command"""
        mock_panel = Mock()
        mock_panel.list_patterns.return_value = [
            {"pattern_id": "pat_1", "classification": "PUBLIC"}
        ]
        mock_panel_class.return_value = mock_panel

        main()
        mock_panel.list_patterns.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "patterns", "-c", "PUBLIC"])
    def test_cli_patterns_with_filter(self, mock_panel_class):
        """Test CLI patterns command with classification filter"""
        mock_panel = Mock()
        mock_panel.list_patterns.return_value = []
        mock_panel_class.return_value = mock_panel

        main()
        mock_panel.list_patterns.assert_called_once_with(classification="PUBLIC")

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch("sys.argv", ["control_panel.py", "export", "-o", "test.json"])
    def test_cli_export_command(self, mock_panel_class):
        """Test CLI export command"""
        mock_panel = Mock()
        mock_panel.export_patterns.return_value = 5
        mock_panel_class.return_value = mock_panel

        main()
        mock_panel.export_patterns.assert_called_once()

    @patch("empathy_os.memory.control_panel.MemoryControlPanel")
    @patch(
        "sys.argv",
        [
            "control_panel.py",
            "status",
            "--host",
            "custom-host",
            "--port",
            "6380",
            "--storage",
            "/custom/storage",
        ],
    )
    def test_cli_custom_config(self, mock_panel_class):
        """Test CLI with custom configuration"""
        mock_panel = Mock()
        mock_panel.status.return_value = {
            "timestamp": "2025-01-01T00:00:00Z",
            "redis": {"status": "running", "host": "localhost", "port": 6379},
            "long_term": {"status": "available"},
            "config": {},
        }
        mock_panel_class.return_value = mock_panel

        with patch("empathy_os.memory.control_panel.print_status"):
            main()

        # Verify config was created with custom values
        call_args = mock_panel_class.call_args
        config = call_args[0][0] if call_args[0] else None
        assert config is not None
        assert config.redis_host == "custom-host"
        assert config.redis_port == 6380
        assert config.storage_dir == "/custom/storage"


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_control_panel_with_none_config(self):
        """Test control panel handles None config gracefully"""
        panel = MemoryControlPanel(None)
        assert panel.config is not None

    @patch("empathy_os.memory.control_panel._check_redis_running")
    def test_get_short_term_with_mock_fallback(self, mock_check):
        """Test _get_short_term falls back to mock when Redis unavailable"""
        mock_check.return_value = False

        panel = MemoryControlPanel()
        memory = panel._get_short_term()
        assert memory is not None
        # Should use mock mode
        assert memory.use_mock is True

    def test_get_statistics_with_partial_data(self):
        """Test get_statistics handles missing data gracefully"""
        with patch("empathy_os.memory.control_panel._check_redis_running", return_value=True):
            panel = MemoryControlPanel()
            mock_short_term = Mock()
            mock_short_term.get_stats.return_value = {}  # Empty stats
            panel._short_term = mock_short_term

            stats = panel.get_statistics()
            # Should not crash with empty stats
            assert stats is not None
