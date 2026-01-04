"""Tests for Session Status Assistant Module

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import shutil
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest

from empathy_llm_toolkit.session_status import (
    DEFAULT_CONFIG,
    PRIORITY_WEIGHTS,
    SessionStatus,
    SessionStatusCollector,
    StatusItem,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture
def patterns_dir(temp_dir):
    """Create patterns directory with test data."""
    patterns = Path(temp_dir) / "patterns"
    patterns.mkdir()

    # Create debugging directory with test bugs
    debugging = patterns / "debugging"
    debugging.mkdir()

    # Investigating bug
    bug1 = {
        "bug_id": "bug_test_001",
        "status": "investigating",
        "error_type": "null_reference",
        "file_path": "src/test.py",
        "error_message": "Test null reference error",
    }
    (debugging / "bug_test_001.json").write_text(json.dumps(bug1))

    # High severity bug
    bug2 = {
        "bug_id": "bug_test_002",
        "status": "open",
        "severity": "high",
        "error_type": "runtime_error",
        "file_path": "src/critical.py",
        "error_message": "Critical runtime error",
    }
    (debugging / "bug_test_002.json").write_text(json.dumps(bug2))

    # Resolved bug (should not appear in status)
    bug3 = {
        "bug_id": "bug_test_003",
        "status": "resolved",
        "error_type": "type_error",
        "file_path": "src/fixed.py",
    }
    (debugging / "bug_test_003.json").write_text(json.dumps(bug3))

    # Create security directory with decisions
    security = patterns / "security"
    security.mkdir()

    decisions = {
        "decisions": [
            {
                "finding_hash": "xss_finding_001",
                "decision": "pending",
                "reason": "Needs review",
            },
            {
                "finding_hash": "sql_injection_001",
                "decision": "false_positive",
                "decided_by": "@dev",
            },
        ],
    }
    (security / "team_decisions.json").write_text(json.dumps(decisions))

    # Create tech_debt directory
    tech_debt = patterns / "tech_debt"
    tech_debt.mkdir()

    debt_history = {
        "snapshots": [
            {"date": "2025-12-10", "total_items": 100, "hotspots": ["file1.py"]},
            {"date": "2025-12-15", "total_items": 120, "hotspots": ["file2.py"]},
        ],
    }
    (tech_debt / "debt_history.json").write_text(json.dumps(debt_history))

    return str(patterns)


@pytest.fixture
def project_dir(temp_dir):
    """Create project directory with roadmap docs."""
    project = Path(temp_dir)

    # Create docs directory with plan files
    docs = project / "docs"
    docs.mkdir()

    plan_content = """# Test Plan

## Tasks

- [x] Completed task 1
- [ ] Unchecked task 1
- [ ] Unchecked task 2
- [x] Completed task 2
"""
    (docs / "PLAN_TEST.md").write_text(plan_content)

    return str(project)


class TestStatusItem:
    """Tests for StatusItem dataclass."""

    def test_status_item_creation(self):
        """Test creating a status item."""
        item = StatusItem(
            category="bugs_investigating",
            priority=60,
            icon="🟡",
            title="Test Bug",
            description="Test description",
        )

        assert item.category == "bugs_investigating"
        assert item.priority == 60
        assert item.icon == "🟡"
        assert item.weight == PRIORITY_WEIGHTS["bugs_investigating"]

    def test_status_item_weight_unknown_category(self):
        """Test weight for unknown category."""
        item = StatusItem(
            category="unknown_category",
            priority=0,
            icon="⚪",
            title="Unknown",
            description="Test",
        )

        assert item.weight == 0


class TestSessionStatus:
    """Tests for SessionStatus dataclass."""

    def test_session_status_creation(self):
        """Test creating session status."""
        status = SessionStatus()

        assert status.items == []
        assert status.wins == []
        assert status.total_attention_items == 0
        assert status.generated_at is not None

    def test_add_item(self):
        """Test adding items to status."""
        status = SessionStatus()
        item = StatusItem(
            category="security_pending",
            priority=100,
            icon="🔴",
            title="Security Issue",
            description="Test",
        )

        status.add_item(item)

        assert len(status.items) == 1
        assert status.total_attention_items == 1

    def test_get_sorted_items(self):
        """Test items are sorted by weight."""
        status = SessionStatus()

        # Add items in wrong order
        status.add_item(StatusItem("commits_wip", 20, "⚪", "WIP", "Test"))
        status.add_item(StatusItem("security_pending", 100, "🔴", "Security", "Test"))
        status.add_item(StatusItem("bugs_investigating", 60, "🟡", "Bug", "Test"))

        sorted_items = status.get_sorted_items()

        assert sorted_items[0].category == "security_pending"
        assert sorted_items[1].category == "bugs_investigating"
        assert sorted_items[2].category == "commits_wip"


class TestSessionStatusCollector:
    """Tests for SessionStatusCollector class."""

    def test_collector_initialization(self, temp_dir):
        """Test collector initialization with defaults."""
        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            project_root=temp_dir,
        )

        assert collector.patterns_dir == Path(temp_dir)
        assert collector.project_root == Path(temp_dir)
        assert collector.config == DEFAULT_CONFIG

    def test_collector_custom_config(self, temp_dir):
        """Test collector with custom config."""
        custom_config = {"inactivity_minutes": 30, "max_display_items": 10}

        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            config=custom_config,
        )

        assert collector.config["inactivity_minutes"] == 30
        assert collector.config["max_display_items"] == 10

    def test_should_show_first_time(self, temp_dir):
        """Test should_show returns True on first run."""
        collector = SessionStatusCollector(patterns_dir=temp_dir, project_root=temp_dir)

        assert collector.should_show() is True

    def test_should_show_after_inactivity(self, temp_dir):
        """Test should_show after inactivity threshold."""
        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            project_root=temp_dir,
            config={"inactivity_minutes": 1},
        )

        # Record interaction
        collector.record_interaction()

        # Immediately should not show
        assert collector.should_show() is False

        # Mock time passed
        two_mins_ago = (datetime.now() - timedelta(minutes=2)).isoformat()
        state = collector._load_state()
        state["last_interaction"] = two_mins_ago
        collector._save_state(state)

        # After inactivity should show
        assert collector.should_show() is True

    def test_should_show_new_day(self, temp_dir):
        """Test should_show on new calendar day."""
        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            project_root=temp_dir,
        )

        # Set last interaction to yesterday
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()
        state = {"last_interaction": yesterday}
        collector._save_state(state)

        assert collector.should_show() is True

    def test_record_interaction(self, temp_dir):
        """Test recording interaction updates state."""
        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            project_root=temp_dir,
        )

        collector.record_interaction()

        state = collector._load_state()
        assert "last_interaction" in state
        assert state.get("interaction_count", 0) == 1

        # Record again
        collector.record_interaction()
        state = collector._load_state()
        assert state.get("interaction_count", 0) == 2

    def test_collect_security_items(self, patterns_dir, temp_dir):
        """Test collecting security pending items."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=temp_dir,
        )

        status = SessionStatus()
        collector._collect_security_items(status)

        # Should find 1 pending security decision
        assert status.total_attention_items == 1
        assert status.items[0].category == "security_pending"
        assert "pending" in status.items[0].title.lower()

    def test_collect_bug_items(self, patterns_dir, temp_dir):
        """Test collecting bug items."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=temp_dir,
        )

        status = SessionStatus()
        collector._collect_bug_items(status)

        # Should find both investigating and high-severity bugs
        categories = [item.category for item in status.items]
        assert "bugs_investigating" in categories
        assert "bugs_high" in categories

    def test_collect_tech_debt_items(self, patterns_dir, temp_dir):
        """Test collecting tech debt items."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=temp_dir,
        )

        status = SessionStatus()
        collector._collect_tech_debt_items(status)

        # Tech debt increased from 100 to 120, should have warning
        assert status.total_attention_items == 1
        assert status.items[0].category == "tech_debt_increasing"

    def test_collect_roadmap_items(self, patterns_dir, project_dir):
        """Test collecting roadmap unchecked items."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=project_dir,
        )

        status = SessionStatus()
        collector._collect_roadmap_items(status)

        # Should find 2 unchecked items in PLAN_TEST.md
        assert status.total_attention_items == 1
        assert status.items[0].category == "roadmap_unchecked"
        assert "2" in status.items[0].title  # 2 unchecked items

    def test_collect_full_status(self, patterns_dir, project_dir):
        """Test full status collection."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=project_dir,
        )

        status = collector.collect()

        # Should have items from multiple sources
        assert status.total_attention_items >= 3
        categories = {item.category for item in status.items}
        assert "security_pending" in categories or "bugs_investigating" in categories

    def test_detect_wins_bugs_resolved(self, patterns_dir, temp_dir):
        """Test detecting wins when bugs are resolved."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=temp_dir,
        )

        # Create a previous snapshot with more investigating bugs
        history_dir = Path(temp_dir) / ".empathy" / "status_history"
        history_dir.mkdir(parents=True)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        prev_snapshot = {
            "date": yesterday,
            "bugs_investigating": 5,
        }
        (history_dir / f"{yesterday}.json").write_text(json.dumps(prev_snapshot))

        status = SessionStatus()
        status.add_item(
            StatusItem(
                category="bugs_investigating",
                priority=60,
                icon="🟡",
                title="Bugs: 1 investigating",
                description="Test",
                details={"count": 1},
            ),
        )

        collector._detect_wins(status)

        # Should detect 4 bugs resolved (5 - 1)
        assert len(status.wins) > 0
        assert any("resolved" in win.lower() for win in status.wins)


class TestOutputFormatting:
    """Tests for output formatting methods."""

    def test_format_output_basic(self, temp_dir):
        """Test basic output formatting."""
        collector = SessionStatusCollector(patterns_dir=temp_dir)

        status = SessionStatus()
        status.add_item(
            StatusItem(
                category="bugs_investigating",
                priority=60,
                icon="🟡",
                title="Bugs: 2 investigating",
                description="Fix bug_001",
            ),
        )

        output = collector.format_output(status)

        assert "Project Status" in output
        assert "1 items need attention" in output
        assert "🟡" in output
        assert "Fix bug_001" in output

    def test_format_output_with_wins(self, temp_dir):
        """Test output formatting with wins."""
        collector = SessionStatusCollector(patterns_dir=temp_dir)

        status = SessionStatus()
        status.wins = ["2 bugs resolved since last session"]

        output = collector.format_output(status)

        assert "Wins since last session" in output
        assert "2 bugs resolved" in output

    def test_format_json(self, temp_dir):
        """Test JSON output formatting."""
        collector = SessionStatusCollector(patterns_dir=temp_dir)

        status = SessionStatus()
        status.add_item(
            StatusItem(
                category="security_pending",
                priority=100,
                icon="🔴",
                title="Security: 1 pending",
                description="Review finding",
                action_prompt="Review the security finding",
            ),
        )

        json_output = collector.format_json(status)
        data = json.loads(json_output)

        assert data["total_attention_items"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["category"] == "security_pending"
        assert data["items"][0]["action_prompt"] == "Review the security finding"

    def test_get_action_prompt(self, temp_dir):
        """Test getting action prompt for selection."""
        collector = SessionStatusCollector(patterns_dir=temp_dir)

        status = SessionStatus()
        status.add_item(
            StatusItem(
                category="bugs_investigating",
                priority=60,
                icon="🟡",
                title="Bug",
                description="Test",
                action_prompt="Fix the bug in src/test.py",
            ),
        )

        prompt = collector.get_action_prompt(status, 1)
        assert prompt == "Fix the bug in src/test.py"

        # Invalid selection
        assert collector.get_action_prompt(status, 0) is None
        assert collector.get_action_prompt(status, 99) is None


class TestPriorityWeights:
    """Tests for priority weight constants."""

    def test_priority_weights_order(self):
        """Test that priority weights are in correct order."""
        weights = PRIORITY_WEIGHTS

        assert weights["security_pending"] > weights["bugs_high"]
        assert weights["bugs_high"] > weights["bugs_investigating"]
        assert weights["bugs_investigating"] > weights["tech_debt_increasing"]
        assert weights["tech_debt_increasing"] > weights["roadmap_unchecked"]
        assert weights["roadmap_unchecked"] > weights["commits_wip"]

    def test_security_highest_priority(self):
        """Test that security has highest priority."""
        assert PRIORITY_WEIGHTS["security_pending"] == 100


class TestDailySnapshots:
    """Tests for daily snapshot functionality."""

    def test_save_daily_snapshot(self, patterns_dir, temp_dir):
        """Test saving daily status snapshot."""
        collector = SessionStatusCollector(
            patterns_dir=patterns_dir,
            project_root=temp_dir,
        )

        collector.collect()  # This triggers snapshot creation

        # Check snapshot was created
        today = datetime.now().strftime("%Y-%m-%d")
        snapshot_file = Path(temp_dir) / ".empathy" / "status_history" / f"{today}.json"

        assert snapshot_file.exists()

        snapshot = json.loads(snapshot_file.read_text())
        assert snapshot["date"] == today
        assert "total_attention_items" in snapshot


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_patterns_directory(self, temp_dir):
        """Test with empty patterns directory."""
        patterns = Path(temp_dir) / "empty_patterns"
        patterns.mkdir()

        collector = SessionStatusCollector(
            patterns_dir=str(patterns),
            project_root=temp_dir,
        )

        status = collector.collect()

        # Should not crash, just have no items
        assert status.total_attention_items == 0

    def test_nonexistent_patterns_directory(self, temp_dir):
        """Test with non-existent patterns directory."""
        collector = SessionStatusCollector(
            patterns_dir=str(Path(temp_dir) / "nonexistent"),
            project_root=temp_dir,
        )

        status = collector.collect()

        # Should not crash
        assert status is not None

    def test_malformed_json_file(self, temp_dir):
        """Test handling of malformed JSON files."""
        patterns = Path(temp_dir) / "patterns" / "debugging"
        patterns.mkdir(parents=True)

        # Create malformed JSON
        (patterns / "bug_bad.json").write_text("{ invalid json }")

        collector = SessionStatusCollector(
            patterns_dir=str(Path(temp_dir) / "patterns"),
            project_root=temp_dir,
        )

        # Should not crash, just skip bad file
        status = collector.collect()
        assert status is not None

    def test_git_not_available(self, temp_dir):
        """Test when git is not available or fails."""
        collector = SessionStatusCollector(
            patterns_dir=temp_dir,
            project_root="/nonexistent/path",
        )

        status = SessionStatus()

        # Should handle git failure gracefully
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = Exception("Git not found")
            collector._collect_git_items(status)

        # Should not crash or add items
        assert status.total_attention_items == 0
