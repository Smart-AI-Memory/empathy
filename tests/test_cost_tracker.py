"""Tests for empathy_os.cost_tracker module.

Tests cover:
- CostTracker initialization and storage
- Request logging and cost calculation
- Daily totals tracking
- Summary generation
- Report formatting
- Tier detection
- CLI command handler
"""

import json
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from empathy_os.cost_tracker import (
    BASELINE_MODEL,
    MODEL_PRICING,
    CostTracker,
    _build_model_pricing,
    cmd_costs,
    get_tracker,
    log_request,
)


class TestCostTrackerInit:
    """Test CostTracker initialization."""

    def test_creates_storage_directory(self, tmp_path):
        """Test that storage directory is created if it doesn't exist."""
        storage_dir = tmp_path / "new_empathy_dir"
        tracker = CostTracker(storage_dir=str(storage_dir))
        assert storage_dir.exists()
        assert tracker.storage_dir == storage_dir

    def test_loads_existing_data(self, tmp_path):
        """Test loading existing cost data from file."""
        storage_dir = tmp_path / ".empathy"
        storage_dir.mkdir()
        costs_file = storage_dir / "costs.json"

        existing_data = {
            "requests": [{"model": "test", "timestamp": "2025-01-01T00:00:00"}],
            "daily_totals": {"2025-01-01": {"requests": 1}},
            "created_at": "2025-01-01T00:00:00",
            "last_updated": "2025-01-01T00:00:00",
        }
        with open(costs_file, "w") as f:
            json.dump(existing_data, f)

        tracker = CostTracker(storage_dir=str(storage_dir))
        assert len(tracker.data["requests"]) == 1
        assert "2025-01-01" in tracker.data["daily_totals"]

    def test_handles_corrupted_file(self, tmp_path):
        """Test handling of corrupted JSON file."""
        storage_dir = tmp_path / ".empathy"
        storage_dir.mkdir()
        costs_file = storage_dir / "costs.json"

        with open(costs_file, "w") as f:
            f.write("not valid json {{{")

        tracker = CostTracker(storage_dir=str(storage_dir))
        assert tracker.data["requests"] == []

    def test_default_data_structure(self, tmp_path):
        """Test default data structure is created."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        assert "requests" in tracker.data
        assert "daily_totals" in tracker.data
        assert "created_at" in tracker.data
        assert "last_updated" in tracker.data


class TestCostCalculation:
    """Test cost calculation logic."""

    def test_calculate_cost_known_model(self, tmp_path):
        """Test cost calculation for known model."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        # 1M input tokens, 1M output tokens for claude-3-haiku
        cost = tracker._calculate_cost("claude-3-haiku-20240307", 1_000_000, 1_000_000)
        # Haiku: $0.25/M input + $1.25/M output = $1.50
        assert cost == pytest.approx(1.50, rel=0.01)

    def test_calculate_cost_unknown_model_defaults(self, tmp_path):
        """Test that unknown models default to capable tier pricing."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        cost = tracker._calculate_cost("unknown-model-xyz", 1_000_000, 1_000_000)
        # Should use capable tier pricing
        assert cost > 0

    def test_calculate_cost_tier_alias(self, tmp_path):
        """Test cost calculation using tier aliases."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        cheap_cost = tracker._calculate_cost("cheap", 1_000_000, 1_000_000)
        capable_cost = tracker._calculate_cost("capable", 1_000_000, 1_000_000)
        premium_cost = tracker._calculate_cost("premium", 1_000_000, 1_000_000)

        # Cheap should be less than capable, which should be less than premium
        assert cheap_cost < capable_cost < premium_cost


class TestRequestLogging:
    """Test request logging functionality."""

    def test_log_request_creates_record(self, tmp_path):
        """Test that log_request creates a proper record."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        result = tracker.log_request(
            model="claude-3-haiku-20240307",
            input_tokens=1000,
            output_tokens=500,
            task_type="summarize",
        )

        assert result["model"] == "claude-3-haiku-20240307"
        assert result["input_tokens"] == 1000
        assert result["output_tokens"] == 500
        assert result["task_type"] == "summarize"
        assert result["tier"] == "cheap"
        assert "actual_cost" in result
        assert "baseline_cost" in result
        assert "savings" in result
        assert result["savings"] > 0  # Haiku saves vs Opus

    def test_log_request_updates_daily_totals(self, tmp_path):
        """Test that logging updates daily totals."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "test")
        tracker.log_request("claude-3-haiku-20240307", 2000, 1000, "test")

        today = datetime.now().strftime("%Y-%m-%d")
        daily = tracker.data["daily_totals"][today]
        assert daily["requests"] == 2
        assert daily["input_tokens"] == 3000
        assert daily["output_tokens"] == 1500

    def test_log_request_saves_to_file(self, tmp_path):
        """Test that logging saves data to file."""
        storage_dir = tmp_path / ".empathy"
        tracker = CostTracker(storage_dir=str(storage_dir))
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "test")

        # Reload from file
        with open(storage_dir / "costs.json") as f:
            saved_data = json.load(f)

        assert len(saved_data["requests"]) == 1

    def test_log_request_limits_stored_requests(self, tmp_path):
        """Test that only last 1000 requests are kept."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))

        # Log 1050 requests
        for i in range(1050):
            tracker.log_request("claude-3-haiku-20240307", 100, 50, f"task_{i}")

        assert len(tracker.data["requests"]) == 1000

    def test_log_request_with_tier_override(self, tmp_path):
        """Test logging with explicit tier override."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        result = tracker.log_request(
            model="some-model",
            input_tokens=1000,
            output_tokens=500,
            task_type="test",
            tier="premium",
        )
        assert result["tier"] == "premium"


class TestTierDetection:
    """Test tier detection from model names."""

    def test_detects_haiku_as_cheap(self, tmp_path):
        """Test that haiku models are detected as cheap tier."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        assert tracker._get_tier("claude-3-haiku-20240307") == "cheap"
        assert tracker._get_tier("claude-3-5-haiku-20241022") == "cheap"

    def test_detects_opus_as_premium(self, tmp_path):
        """Test that opus models are detected as premium tier."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        assert tracker._get_tier("claude-opus-4-5-20251101") == "premium"
        assert tracker._get_tier("claude-3-opus-20240229") == "premium"

    def test_detects_other_as_capable(self, tmp_path):
        """Test that other models default to capable tier."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        assert tracker._get_tier("claude-3-sonnet-20240229") == "capable"
        assert tracker._get_tier("gpt-4") == "capable"


class TestSummary:
    """Test summary generation."""

    def test_get_summary_empty(self, tmp_path):
        """Test summary with no data."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        summary = tracker.get_summary(days=7)

        assert summary["requests"] == 0
        assert summary["actual_cost"] == 0
        assert summary["savings_percent"] == 0

    def test_get_summary_with_data(self, tmp_path):
        """Test summary with logged requests."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "summarize")
        tracker.log_request("claude-3-5-sonnet-20241022", 2000, 1000, "generate")

        summary = tracker.get_summary(days=7)

        assert summary["requests"] == 2
        assert summary["input_tokens"] == 3000
        assert summary["output_tokens"] == 1500
        assert summary["actual_cost"] > 0
        assert summary["by_task"]["summarize"] == 1
        assert summary["by_task"]["generate"] == 1

    def test_get_summary_respects_days_filter(self, tmp_path):
        """Test that summary respects the days filter."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))

        # Add data for today
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "today_task")

        # Manually add old data
        old_date = (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d")
        tracker.data["daily_totals"][old_date] = {
            "requests": 100,
            "input_tokens": 100000,
            "output_tokens": 50000,
            "actual_cost": 1.0,
            "baseline_cost": 10.0,
            "savings": 9.0,
        }

        summary = tracker.get_summary(days=7)
        assert summary["requests"] == 1  # Only today's request


class TestReport:
    """Test report generation."""

    def test_get_report_format(self, tmp_path):
        """Test report formatting."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "summarize")

        report = tracker.get_report(days=7)

        assert "COST TRACKING REPORT" in report
        assert "SUMMARY" in report
        assert "COSTS" in report
        assert "BY MODEL TIER" in report
        assert "BY TASK TYPE" in report

    def test_get_report_shows_savings(self, tmp_path):
        """Test that report shows savings percentage."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        tracker.log_request("claude-3-haiku-20240307", 100000, 50000, "test")

        report = tracker.get_report(days=7)
        assert "You saved:" in report
        assert "%" in report


class TestGetToday:
    """Test get_today functionality."""

    def test_get_today_empty(self, tmp_path):
        """Test get_today with no data for today."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        today = tracker.get_today()

        assert today["requests"] == 0
        assert today["actual_cost"] == 0

    def test_get_today_with_data(self, tmp_path):
        """Test get_today returns today's data."""
        tracker = CostTracker(storage_dir=str(tmp_path / ".empathy"))
        tracker.log_request("claude-3-haiku-20240307", 1000, 500, "test")

        today = tracker.get_today()
        assert today["requests"] == 1
        assert today["input_tokens"] == 1000


class TestGlobalTracker:
    """Test global tracker functionality."""

    def test_get_tracker_singleton(self, tmp_path):
        """Test that get_tracker returns same instance."""
        import empathy_os.cost_tracker as ct

        # Reset singleton
        ct._tracker = None

        tracker1 = get_tracker(storage_dir=str(tmp_path / ".empathy"))
        tracker2 = get_tracker(storage_dir=str(tmp_path / ".empathy"))

        assert tracker1 is tracker2

        # Cleanup
        ct._tracker = None

    def test_log_request_convenience_function(self, tmp_path):
        """Test log_request convenience function."""
        import empathy_os.cost_tracker as ct

        ct._tracker = None

        with patch.object(ct, "_tracker", None):
            with patch.object(ct, "get_tracker") as mock_get:
                mock_tracker = MagicMock()
                mock_get.return_value = mock_tracker

                log_request("model", 100, 50, "task")
                mock_tracker.log_request.assert_called_once()

        ct._tracker = None


class TestCLICommand:
    """Test CLI command handler."""

    def test_cmd_costs_text_output(self, tmp_path, capsys):
        """Test cmd_costs with text output."""
        args = MagicMock()
        args.empathy_dir = str(tmp_path / ".empathy")
        args.days = 7
        args.json = False

        result = cmd_costs(args)

        assert result == 0
        captured = capsys.readouterr()
        assert "COST TRACKING REPORT" in captured.out

    def test_cmd_costs_json_output(self, tmp_path, capsys):
        """Test cmd_costs with JSON output."""
        args = MagicMock()
        args.empathy_dir = str(tmp_path / ".empathy")
        args.days = 7
        args.json = True

        result = cmd_costs(args)

        assert result == 0
        captured = capsys.readouterr()
        data = json.loads(captured.out)
        assert "requests" in data
        assert "savings_percent" in data


class TestModelPricing:
    """Test model pricing configuration."""

    def test_model_pricing_has_tiers(self):
        """Test that MODEL_PRICING has tier aliases."""
        assert "cheap" in MODEL_PRICING
        assert "capable" in MODEL_PRICING
        assert "premium" in MODEL_PRICING

    def test_model_pricing_has_legacy_models(self):
        """Test that MODEL_PRICING includes legacy models."""
        assert "claude-3-haiku-20240307" in MODEL_PRICING
        assert "gpt-4-turbo" in MODEL_PRICING

    def test_baseline_model_defined(self):
        """Test that BASELINE_MODEL is defined and valid."""
        assert BASELINE_MODEL is not None
        assert "opus" in BASELINE_MODEL.lower()

    def test_build_model_pricing_returns_dict(self):
        """Test _build_model_pricing returns valid dict."""
        pricing = _build_model_pricing()
        assert isinstance(pricing, dict)
        assert len(pricing) > 0

        # Each entry should have input and output costs
        for _model, costs in pricing.items():
            assert "input" in costs
            assert "output" in costs
            assert costs["input"] >= 0
            assert costs["output"] >= 0
