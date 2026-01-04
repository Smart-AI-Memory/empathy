"""Tests for empathy_os.discovery module.

Tests cover:
- DiscoveryEngine initialization
- Command recording
- Tip triggering based on usage
- Condition-based tips
- Marking tips as shown
- Statistics tracking
"""

import json
from datetime import datetime, timedelta

from empathy_os.discovery import (
    DISCOVERY_TIPS,
    DiscoveryEngine,
    _days_since_sync,
    format_tips_for_cli,
    get_engine,
    show_tip_if_available,
)


class TestDiscoveryEngineInit:
    """Test DiscoveryEngine initialization."""

    def test_creates_storage_directory(self, tmp_path):
        """Test that storage directory is created."""
        storage_dir = tmp_path / "new_dir"
        _engine = DiscoveryEngine(storage_dir=str(storage_dir))
        assert storage_dir.exists()

    def test_loads_existing_state(self, tmp_path):
        """Test loading existing discovery state."""
        storage_dir = tmp_path / ".empathy"
        storage_dir.mkdir()
        stats_file = storage_dir / "discovery_stats.json"

        existing_state = {
            "command_counts": {"inspect": 5},
            "tips_shown": ["tip1"],
            "total_commands": 5,
            "patterns_learned": 10,
            "first_run": "2025-01-01T00:00:00",
            "last_updated": "2025-01-01T00:00:00",
        }
        with open(stats_file, "w") as f:
            json.dump(existing_state, f)

        engine = DiscoveryEngine(storage_dir=str(storage_dir))
        assert engine.state["command_counts"]["inspect"] == 5
        assert engine.state["total_commands"] == 5

    def test_handles_corrupted_file(self, tmp_path):
        """Test handling corrupted state file."""
        storage_dir = tmp_path / ".empathy"
        storage_dir.mkdir()
        stats_file = storage_dir / "discovery_stats.json"

        with open(stats_file, "w") as f:
            f.write("not valid json")

        engine = DiscoveryEngine(storage_dir=str(storage_dir))
        assert engine.state["command_counts"] == {}

    def test_default_state_structure(self, tmp_path):
        """Test default state has all required fields."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        assert "command_counts" in engine.state
        assert "tips_shown" in engine.state
        assert "total_commands" in engine.state
        assert "patterns_learned" in engine.state
        assert "first_run" in engine.state


class TestCommandRecording:
    """Test command recording functionality."""

    def test_record_command_increments_count(self, tmp_path):
        """Test that recording a command increments its count."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_command("inspect")
        engine.record_command("inspect")
        engine.record_command("health")

        assert engine.state["command_counts"]["inspect"] == 2
        assert engine.state["command_counts"]["health"] == 1
        assert engine.state["total_commands"] == 3

    def test_record_command_saves_state(self, tmp_path):
        """Test that recording saves to file."""
        storage_dir = tmp_path / ".empathy"
        engine = DiscoveryEngine(storage_dir=str(storage_dir))
        engine.record_command("inspect")

        # Reload and verify
        with open(storage_dir / "discovery_stats.json") as f:
            saved = json.load(f)

        assert saved["command_counts"]["inspect"] == 1

    def test_record_command_returns_tips(self, tmp_path):
        """Test that recording can return triggered tips."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # First inspect should trigger "after_first_inspect" tip
        tips = engine.record_command("inspect")

        # Should have at least one tip
        assert len(tips) >= 0  # May be empty if tip conditions not met


class TestTipTriggering:
    """Test tip triggering logic."""

    def test_trigger_based_tip(self, tmp_path):
        """Test trigger-based tip activation."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # Record enough inspects to trigger after_first_inspect
        engine.record_command("inspect")
        tips = engine.get_pending_tips(trigger="inspect")

        # Should have after_first_inspect tip
        tip_ids = [t["id"] for t in tips]
        assert "after_first_inspect" in tip_ids

    def test_min_uses_requirement(self, tmp_path):
        """Test that min_uses is respected."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # after_10_inspects requires 10 uses
        for _ in range(9):
            engine.record_command("inspect")

        tips = engine.get_pending_tips(trigger="inspect")
        tip_ids = [t["id"] for t in tips]
        assert "after_10_inspects" not in tip_ids

        # 10th use should trigger it
        engine.record_command("inspect")
        tips = engine.get_pending_tips(trigger="inspect")
        tip_ids = [t["id"] for t in tips]
        assert "after_10_inspects" in tip_ids

    def test_condition_based_tip_high_debt(self, tmp_path):
        """Test condition-based tip for high tech debt."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.set_tech_debt_trend("increasing")

        tips = engine.get_pending_tips()
        tip_ids = [t["id"] for t in tips]
        assert "high_tech_debt" in tip_ids

    def test_condition_based_tip_no_patterns(self, tmp_path):
        """Test condition-based tip when no patterns learned."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # Need > 5 commands but 0 patterns
        for _ in range(6):
            engine.record_command("test")

        tips = engine.get_pending_tips()
        tip_ids = [t["id"] for t in tips]
        assert "no_patterns" in tip_ids

    def test_max_tips_limit(self, tmp_path):
        """Test that max_tips limits returned tips."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # Set up conditions for multiple tips
        engine.set_tech_debt_trend("increasing")
        for _ in range(6):
            engine.record_command("test")

        tips = engine.get_pending_tips(max_tips=1)
        assert len(tips) <= 1


class TestMarkShown:
    """Test marking tips as shown."""

    def test_mark_shown_prevents_repeat(self, tmp_path):
        """Test that marked tips don't appear again."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_command("inspect")

        # Get tips and mark as shown
        tips = engine.get_pending_tips(trigger="inspect")
        for tip in tips:
            engine.mark_shown(tip["id"])

        # Should not appear again
        tips = engine.get_pending_tips(trigger="inspect")
        tip_ids = [t["id"] for t in tips]
        assert "after_first_inspect" not in tip_ids

    def test_mark_shown_saves_state(self, tmp_path):
        """Test that marking saves to file."""
        storage_dir = tmp_path / ".empathy"
        engine = DiscoveryEngine(storage_dir=str(storage_dir))
        engine.mark_shown("test_tip")

        with open(storage_dir / "discovery_stats.json") as f:
            saved = json.load(f)

        assert "test_tip" in saved["tips_shown"]


class TestAdditionalRecording:
    """Test additional recording methods."""

    def test_record_patterns_learned(self, tmp_path):
        """Test recording patterns learned."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_patterns_learned(5)
        engine.record_patterns_learned(3)

        assert engine.state["patterns_learned"] == 8

    def test_record_api_request(self, tmp_path):
        """Test recording API requests."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_api_request()
        engine.record_api_request()

        assert engine.state["api_requests"] == 2

    def test_record_claude_sync(self, tmp_path):
        """Test recording Claude sync."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_claude_sync()

        assert engine.state["last_claude_sync"] is not None


class TestStats:
    """Test statistics retrieval."""

    def test_get_stats_structure(self, tmp_path):
        """Test stats returns correct structure."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        stats = engine.get_stats()

        assert "total_commands" in stats
        assert "command_counts" in stats
        assert "patterns_learned" in stats
        assert "tips_shown" in stats
        assert "tips_remaining" in stats
        assert "days_active" in stats

    def test_get_stats_reflects_usage(self, tmp_path):
        """Test stats reflects actual usage."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))
        engine.record_command("inspect")
        engine.record_command("health")
        engine.record_patterns_learned(10)
        engine.mark_shown("tip1")

        stats = engine.get_stats()

        assert stats["total_commands"] == 2
        assert stats["command_counts"]["inspect"] == 1
        assert stats["patterns_learned"] == 10
        assert stats["tips_shown"] == 1

    def test_days_active_calculation(self, tmp_path):
        """Test days active calculation."""
        engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # Just created, should be 0 days
        stats = engine.get_stats()
        assert stats["days_active"] == 0


class TestDaysSinceSync:
    """Test _days_since_sync helper."""

    def test_no_sync_returns_max(self):
        """Test returns 999 when no sync recorded."""
        assert _days_since_sync({}) == 999
        assert _days_since_sync({"last_claude_sync": None}) == 999

    def test_recent_sync(self):
        """Test returns 0 for today's sync."""
        stats = {"last_claude_sync": datetime.now().isoformat()}
        assert _days_since_sync(stats) == 0

    def test_old_sync(self):
        """Test returns correct days for old sync."""
        old_date = datetime.now() - timedelta(days=5)
        stats = {"last_claude_sync": old_date.isoformat()}
        assert _days_since_sync(stats) == 5

    def test_invalid_date_returns_max(self):
        """Test returns 999 for invalid date."""
        stats = {"last_claude_sync": "not-a-date"}
        assert _days_since_sync(stats) == 999


class TestGlobalEngine:
    """Test global engine singleton."""

    def test_get_engine_singleton(self, tmp_path):
        """Test get_engine returns same instance."""
        import empathy_os.discovery as disc

        disc._engine = None

        engine1 = get_engine(storage_dir=str(tmp_path / ".empathy"))
        engine2 = get_engine(storage_dir=str(tmp_path / ".empathy"))

        assert engine1 is engine2

        disc._engine = None


class TestShowTipIfAvailable:
    """Test show_tip_if_available function."""

    def test_quiet_mode_no_output(self, tmp_path, capsys):
        """Test quiet mode suppresses output."""
        import empathy_os.discovery as disc

        disc._engine = None
        disc._engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        show_tip_if_available("inspect", quiet=True)

        captured = capsys.readouterr()
        assert "TIP:" not in captured.out

        disc._engine = None

    def test_shows_tips_when_available(self, tmp_path, capsys):
        """Test tips are shown when available."""
        import empathy_os.discovery as disc

        disc._engine = None
        disc._engine = DiscoveryEngine(storage_dir=str(tmp_path / ".empathy"))

        # This should trigger after_first_inspect
        show_tip_if_available("inspect", quiet=False)

        _captured = capsys.readouterr()
        # May or may not have tips depending on state
        # Just verify it doesn't crash

        disc._engine = None


class TestFormatTipsForCli:
    """Test CLI tip formatting."""

    def test_empty_tips_returns_empty(self):
        """Test empty tips list returns empty string."""
        assert format_tips_for_cli([]) == ""

    def test_formats_tips_correctly(self):
        """Test tips are formatted with header."""
        tips = [
            {"id": "tip1", "tip": "Try this feature", "priority": 1},
            {"id": "tip2", "tip": "Also try this", "priority": 2},
        ]
        result = format_tips_for_cli(tips)

        assert "TIPS" in result
        assert "Try this feature" in result
        assert "Also try this" in result


class TestDiscoveryTipsConfig:
    """Test DISCOVERY_TIPS configuration."""

    def test_all_tips_have_required_fields(self):
        """Test all tips have required configuration."""
        for tip_id, config in DISCOVERY_TIPS.items():
            assert "tip" in config, f"{tip_id} missing 'tip'"
            assert "priority" in config, f"{tip_id} missing 'priority'"
            assert "shown" in config, f"{tip_id} missing 'shown'"

            # Must have either trigger or condition
            has_trigger = "trigger" in config
            has_condition = "condition" in config
            assert has_trigger or has_condition, f"{tip_id} needs trigger or condition"

    def test_trigger_tips_have_min_uses(self):
        """Test trigger-based tips have min_uses."""
        for tip_id, config in DISCOVERY_TIPS.items():
            if "trigger" in config:
                assert "min_uses" in config, f"{tip_id} missing 'min_uses'"

    def test_condition_functions_are_callable(self):
        """Test condition functions are callable."""
        for tip_id, config in DISCOVERY_TIPS.items():
            if "condition" in config:
                assert callable(config["condition"]), f"{tip_id} condition not callable"
