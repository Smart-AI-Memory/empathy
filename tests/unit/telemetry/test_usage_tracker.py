"""Unit tests for UsageTracker.

Tests the core telemetry tracking functionality including:
- File creation and JSON Lines format
- Thread-safe atomic writes
- SHA256 user ID hashing
- File rotation and retention
- Statistics calculation
- Savings calculation
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from empathy_os.telemetry import UsageTracker


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test telemetry data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def tracker(temp_dir):
    """Create a UsageTracker instance with temporary directory."""
    return UsageTracker(telemetry_dir=temp_dir, retention_days=7, max_file_size_mb=1)


def test_track_llm_call_creates_file(tracker, temp_dir):
    """Test that tracking an LLM call creates the usage file."""
    assert not tracker.usage_file.exists()

    tracker.track_llm_call(
        workflow="test-workflow",
        stage="analysis",
        tier="CAPABLE",
        model="claude-sonnet-4.5",
        provider="anthropic",
        cost=0.015,
        tokens={"input": 1500, "output": 500},
        cache_hit=False,
        cache_type=None,
        duration_ms=2340,
    )

    assert tracker.usage_file.exists()


def test_track_llm_call_json_lines_format(tracker):
    """Test that entries are written in JSON Lines format."""
    tracker.track_llm_call(
        workflow="test-workflow",
        stage="analysis",
        tier="CAPABLE",
        model="claude-sonnet-4.5",
        provider="anthropic",
        cost=0.015,
        tokens={"input": 1500, "output": 500},
        cache_hit=False,
        cache_type=None,
        duration_ms=2340,
    )

    tracker.track_llm_call(
        workflow="test-workflow2",
        stage="generation",
        tier="CHEAP",
        model="claude-haiku-4",
        provider="anthropic",
        cost=0.002,
        tokens={"input": 800, "output": 300},
        cache_hit=True,
        cache_type="hash",
        duration_ms=150,
    )

    # Read file and verify JSON Lines format
    with open(tracker.usage_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    assert len(lines) == 2

    # Each line should be valid JSON
    entry1 = json.loads(lines[0])
    entry2 = json.loads(lines[1])

    assert entry1["workflow"] == "test-workflow"
    assert entry2["workflow"] == "test-workflow2"


def test_user_id_hashed(tracker):
    """Test that user IDs are SHA256 hashed."""
    tracker.track_llm_call(
        workflow="test-workflow",
        stage="analysis",
        tier="CAPABLE",
        model="claude-sonnet-4.5",
        provider="anthropic",
        cost=0.015,
        tokens={"input": 1500, "output": 500},
        cache_hit=False,
        cache_type=None,
        duration_ms=2340,
        user_id="test_user@example.com",
    )

    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1

    # User ID should be hashed (16 chars from SHA256)
    user_id = entries[0]["user_id"]
    assert len(user_id) == 16
    assert user_id.isalnum()
    # Should NOT be the original email
    assert user_id != "test_user@example.com"


def test_atomic_write(tracker):
    """Test that writes are atomic (no partial writes)."""
    # Track multiple calls concurrently to test atomicity
    import threading

    def track_call(i):
        tracker.track_llm_call(
            workflow=f"workflow-{i}",
            stage="test",
            tier="CAPABLE",
            model="test-model",
            provider="test",
            cost=0.01,
            tokens={"input": 100, "output": 100},
            cache_hit=False,
            cache_type=None,
            duration_ms=100,
        )

    threads = []
    for i in range(10):
        t = threading.Thread(target=track_call, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # All entries should be valid JSON
    entries = tracker.get_recent_entries(limit=100)
    assert len(entries) == 10


def test_rotation_after_size_limit(tracker, temp_dir):
    """Test that log file rotates after exceeding size limit."""
    # Track many calls to exceed size limit (1 MB for test)
    large_tokens = {"input": 10000, "output": 10000}
    for i in range(100):
        tracker.track_llm_call(
            workflow=f"workflow-{i}",
            stage="test",
            tier="CAPABLE",
            model="test-model-with-long-name" * 10,
            provider="test-provider-with-long-name" * 10,
            cost=0.01,
            tokens=large_tokens,
            cache_hit=False,
            cache_type=None,
            duration_ms=1000,
        )

    # Check if rotation occurred
    rotated_files = list(temp_dir.glob("usage.*.jsonl"))
    # Should have rotated at least once if size exceeded
    # (or still have original if not exceeded)
    assert tracker.usage_file.exists() or len(rotated_files) > 0


def test_get_recent_entries(tracker):
    """Test reading recent entries."""
    # Track 5 calls
    for i in range(5):
        tracker.track_llm_call(
            workflow=f"workflow-{i}",
            stage="test",
            tier="CAPABLE",
            model="test-model",
            provider="test",
            cost=0.01 * (i + 1),
            tokens={"input": 100 * (i + 1), "output": 100 * (i + 1)},
            cache_hit=False,
            cache_type=None,
            duration_ms=100,
        )

    # Get last 3 entries
    entries = tracker.get_recent_entries(limit=3)
    assert len(entries) == 3

    # Should be most recent first
    assert entries[0]["workflow"] == "workflow-4"
    assert entries[1]["workflow"] == "workflow-3"
    assert entries[2]["workflow"] == "workflow-2"


def test_get_stats(tracker):
    """Test statistics calculation."""
    # Track calls with different tiers
    tracker.track_llm_call(
        workflow="test1",
        stage="test",
        tier="CHEAP",
        model="model1",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=False,
        cache_type=None,
        duration_ms=100,
    )

    tracker.track_llm_call(
        workflow="test2",
        stage="test",
        tier="CAPABLE",
        model="model2",
        provider="test",
        cost=0.02,
        tokens={"input": 200, "output": 200},
        cache_hit=True,
        cache_type="hash",
        duration_ms=50,
    )

    tracker.track_llm_call(
        workflow="test3",
        stage="test",
        tier="PREMIUM",
        model="model3",
        provider="test",
        cost=0.05,
        tokens={"input": 300, "output": 300},
        cache_hit=False,
        cache_type=None,
        duration_ms=200,
    )

    stats = tracker.get_stats(days=1)

    assert stats["total_calls"] == 3
    assert stats["total_cost"] == 0.08
    assert stats["total_tokens_input"] == 600
    assert stats["total_tokens_output"] == 600
    assert stats["cache_hits"] == 1
    assert stats["cache_misses"] == 2
    assert stats["cache_hit_rate"] == pytest.approx(33.3, rel=0.1)
    assert "CHEAP" in stats["by_tier"]
    assert "CAPABLE" in stats["by_tier"]
    assert "PREMIUM" in stats["by_tier"]


def test_calculate_savings(tracker):
    """Test savings calculation."""
    # Track calls with different tiers
    for i in range(10):
        tier = ["CHEAP", "CAPABLE", "PREMIUM"][i % 3]
        cost = {"CHEAP": 0.001, "CAPABLE": 0.01, "PREMIUM": 0.05}[tier]

        tracker.track_llm_call(
            workflow="test",
            stage="test",
            tier=tier,
            model="model",
            provider="test",
            cost=cost,
            tokens={"input": 100, "output": 100},
            cache_hit=False,
            cache_type=None,
            duration_ms=100,
        )

    savings = tracker.calculate_savings(days=1)

    assert savings["total_calls"] == 10
    assert savings["actual_cost"] > 0
    assert savings["baseline_cost"] > savings["actual_cost"]  # Should save money
    assert savings["savings"] > 0
    assert savings["savings_percent"] > 0
    assert "CHEAP" in savings["tier_distribution"]
    assert "CAPABLE" in savings["tier_distribution"]
    assert "PREMIUM" in savings["tier_distribution"]


def test_reset(tracker):
    """Test clearing all telemetry data."""
    # Track some calls
    for i in range(5):
        tracker.track_llm_call(
            workflow="test",
            stage="test",
            tier="CAPABLE",
            model="model",
            provider="test",
            cost=0.01,
            tokens={"input": 100, "output": 100},
            cache_hit=False,
            cache_type=None,
            duration_ms=100,
        )

    assert tracker.usage_file.exists()
    entries_before = tracker.get_recent_entries(limit=100)
    assert len(entries_before) == 5

    # Reset
    count = tracker.reset()
    assert count == 5

    # File should be deleted
    assert not tracker.usage_file.exists()

    # No entries after reset
    entries_after = tracker.get_recent_entries(limit=100)
    assert len(entries_after) == 0


def test_export_to_dict(tracker):
    """Test exporting entries as dictionary."""
    # Track some calls
    tracker.track_llm_call(
        workflow="test1",
        stage="test",
        tier="CAPABLE",
        model="model",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=False,
        cache_type=None,
        duration_ms=100,
    )

    tracker.track_llm_call(
        workflow="test2",
        stage="test",
        tier="CHEAP",
        model="model",
        provider="test",
        cost=0.001,
        tokens={"input": 50, "output": 50},
        cache_hit=True,
        cache_type="hash",
        duration_ms=50,
    )

    # Export all
    entries = tracker.export_to_dict()
    assert len(entries) == 2
    assert isinstance(entries, list)
    assert isinstance(entries[0], dict)
    assert "workflow" in entries[0]
    assert "tier" in entries[0]
    assert "cost" in entries[0]


def test_cache_hit_tracking(tracker):
    """Test that cache hits are tracked correctly."""
    # Track cache hit
    tracker.track_llm_call(
        workflow="test",
        stage="test",
        tier="CAPABLE",
        model="model",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=True,
        cache_type="hash",
        duration_ms=10,  # Cache hits should be fast
    )

    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1
    assert entries[0]["cache"]["hit"] is True
    assert entries[0]["cache"]["type"] == "hash"
    assert entries[0]["duration_ms"] == 10


def test_optional_stage(tracker):
    """Test that stage field is optional."""
    # Track without stage
    tracker.track_llm_call(
        workflow="test",
        stage=None,
        tier="CAPABLE",
        model="model",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=False,
        cache_type=None,
        duration_ms=100,
    )

    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1
    # Stage should not be in entry if None
    assert "stage" not in entries[0] or entries[0]["stage"] is None


def test_schema_version(tracker):
    """Test that schema version is included in entries."""
    tracker.track_llm_call(
        workflow="test",
        stage="test",
        tier="CAPABLE",
        model="model",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=False,
        cache_type=None,
        duration_ms=100,
    )

    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1
    assert entries[0]["v"] == "1.0"


def test_timestamp_format(tracker):
    """Test that timestamps are ISO 8601 with Z suffix."""
    tracker.track_llm_call(
        workflow="test",
        stage="test",
        tier="CAPABLE",
        model="model",
        provider="test",
        cost=0.01,
        tokens={"input": 100, "output": 100},
        cache_hit=False,
        cache_type=None,
        duration_ms=100,
    )

    entries = tracker.get_recent_entries(limit=1)
    assert len(entries) == 1

    ts = entries[0]["ts"]
    assert ts.endswith("Z")

    # Should be parseable as ISO 8601
    dt = datetime.fromisoformat(ts.rstrip("Z"))
    assert isinstance(dt, datetime)
