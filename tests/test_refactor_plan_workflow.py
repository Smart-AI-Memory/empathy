"""Tests for RefactorPlanWorkflow.

Tests the tech debt prioritization workflow with:
- Debt marker scanning
- Trajectory analysis
- Priority scoring
- Refactoring roadmap generation

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from empathy_os.workflows.base import ModelTier
from empathy_os.workflows.refactor_plan import (
    DEBT_MARKERS,
    RefactorPlanWorkflow,
    format_refactor_plan_report,
)


class TestDebtMarkers:
    """Tests for debt marker constants."""

    def test_debt_markers_exist(self):
        """Test that debt markers are defined."""
        assert len(DEBT_MARKERS) > 0
        assert "TODO" in DEBT_MARKERS
        assert "FIXME" in DEBT_MARKERS
        assert "HACK" in DEBT_MARKERS

    def test_debt_marker_structure(self):
        """Test that markers have required fields."""
        for marker, info in DEBT_MARKERS.items():
            assert "severity" in info, f"{marker} missing severity"
            assert "weight" in info, f"{marker} missing weight"

    def test_severity_values(self):
        """Test that severities are valid values."""
        valid_severities = {"high", "medium", "low"}
        for _marker, info in DEBT_MARKERS.items():
            assert info["severity"] in valid_severities

    def test_weights_are_positive(self):
        """Test that weights are positive integers."""
        for _marker, info in DEBT_MARKERS.items():
            assert info["weight"] > 0
            assert isinstance(info["weight"], int)


class TestRefactorPlanWorkflowInit:
    """Tests for RefactorPlanWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = RefactorPlanWorkflow()

        assert workflow.name == "refactor-plan"
        assert workflow.patterns_dir == "./patterns"
        assert workflow.min_debt_for_premium == 50
        assert workflow._total_debt == 0

    def test_custom_patterns_dir(self):
        """Test custom patterns directory."""
        workflow = RefactorPlanWorkflow(patterns_dir="/custom/path")

        assert workflow.patterns_dir == "/custom/path"

    def test_custom_min_debt(self):
        """Test custom minimum debt threshold."""
        workflow = RefactorPlanWorkflow(min_debt_for_premium=100)

        assert workflow.min_debt_for_premium == 100

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = RefactorPlanWorkflow()

        assert workflow.tier_map["scan"] == ModelTier.CHEAP
        assert workflow.tier_map["analyze"] == ModelTier.CAPABLE
        assert workflow.tier_map["prioritize"] == ModelTier.CAPABLE
        assert workflow.tier_map["plan"] == ModelTier.PREMIUM

    def test_stages(self):
        """Test workflow stages."""
        workflow = RefactorPlanWorkflow()

        assert workflow.stages == ["scan", "analyze", "prioritize", "plan"]


class TestDebtHistoryLoading:
    """Tests for debt history loading."""

    def test_load_history_file_not_exists(self):
        """Test loading when file doesn't exist."""
        workflow = RefactorPlanWorkflow(patterns_dir="/nonexistent")

        assert workflow._debt_history == []

    def test_load_history_from_file(self):
        """Test loading history from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history = {
                "snapshots": [
                    {"total_items": 50, "date": "2024-01-01"},
                    {"total_items": 60, "date": "2024-02-01"},
                ],
            }

            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                json.dump(history, f)

            workflow = RefactorPlanWorkflow(patterns_dir=tmpdir)

            assert len(workflow._debt_history) == 2

    def test_load_history_invalid_json(self):
        """Test loading invalid JSON doesn't crash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with open(Path(tmpdir) / "tech_debt.json", "w") as f:
                f.write("not valid json")

            workflow = RefactorPlanWorkflow(patterns_dir=tmpdir)

            assert workflow._debt_history == []


class TestRefactorPlanSkipStage:
    """Tests for stage skipping logic."""

    def test_should_not_skip_scan(self):
        """Test scan stage is never skipped."""
        workflow = RefactorPlanWorkflow()

        skip, reason = workflow.should_skip_stage("scan", {})

        assert skip is False

    def test_should_downgrade_plan_low_debt(self):
        """Test plan stage is downgraded with low debt."""
        workflow = RefactorPlanWorkflow(min_debt_for_premium=50)
        workflow._total_debt = 10

        skip, reason = workflow.should_skip_stage("plan", {})

        assert skip is False
        assert workflow.tier_map["plan"] == ModelTier.CAPABLE

    def test_should_not_downgrade_plan_high_debt(self):
        """Test plan stage not downgraded with high debt."""
        workflow = RefactorPlanWorkflow(min_debt_for_premium=50)
        workflow._total_debt = 100
        # Ensure tier is premium before check
        workflow.tier_map["plan"] = ModelTier.PREMIUM

        skip, reason = workflow.should_skip_stage("plan", {})

        assert skip is False
        # With high debt, tier should remain PREMIUM
        assert workflow.tier_map["plan"] == ModelTier.PREMIUM


class TestRefactorPlanStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_scan(self):
        """Test scan stage routing."""
        workflow = RefactorPlanWorkflow()

        with patch.object(workflow, "_scan", new_callable=AsyncMock) as mock:
            mock.return_value = ({"debt_items": []}, 100, 50)

            await workflow.run_stage("scan", ModelTier.CHEAP, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_analyze(self):
        """Test analyze stage routing."""
        workflow = RefactorPlanWorkflow()

        with patch.object(workflow, "_analyze", new_callable=AsyncMock) as mock:
            mock.return_value = ({"analysis": {}}, 200, 100)

            await workflow.run_stage("analyze", ModelTier.CAPABLE, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_prioritize(self):
        """Test prioritize stage routing."""
        workflow = RefactorPlanWorkflow()

        with patch.object(workflow, "_prioritize", new_callable=AsyncMock) as mock:
            mock.return_value = ({"prioritized_items": []}, 150, 75)

            await workflow.run_stage("prioritize", ModelTier.CAPABLE, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_plan(self):
        """Test plan stage routing."""
        workflow = RefactorPlanWorkflow()

        with patch.object(workflow, "_plan", new_callable=AsyncMock) as mock:
            mock.return_value = ({"refactoring_plan": ""}, 300, 200)

            await workflow.run_stage("plan", ModelTier.PREMIUM, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = RefactorPlanWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CHEAP, {})


class TestRefactorPlanScan:
    """Tests for scan stage."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self):
        """Test scan on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["debt_items"] == []
            assert result["total_debt"] == 0

    @pytest.mark.asyncio
    async def test_scan_detects_todo(self):
        """Test scan detects TODO markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# TODO: Fix this bug")

            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["total_debt"] >= 1
            assert any(item["marker"] == "TODO" for item in result["debt_items"])

    @pytest.mark.asyncio
    async def test_scan_detects_fixme(self):
        """Test scan detects FIXME markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# FIXME: Memory leak here")

            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert any(item["marker"] == "FIXME" for item in result["debt_items"])

    @pytest.mark.asyncio
    async def test_scan_detects_hack(self):
        """Test scan detects HACK markers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# HACK: Temporary workaround")

            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert any(item["marker"] == "HACK" for item in result["debt_items"])

    @pytest.mark.asyncio
    async def test_scan_skips_git_directory(self):
        """Test scan skips .git directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            (git_dir / "hooks.py").write_text("# TODO: Git hook todo")

            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert all(".git" not in item["file"] for item in result["debt_items"])

    @pytest.mark.asyncio
    async def test_scan_groups_by_file(self):
        """Test scan groups items by file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text("# TODO: First\n# TODO: Second")
            (Path(tmpdir) / "utils.py").write_text("# TODO: Third")

            workflow = RefactorPlanWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert len(result["by_file"]) == 2
            assert "by_marker" in result


class TestRefactorPlanAnalyze:
    """Tests for analyze stage."""

    @pytest.mark.asyncio
    async def test_analyze_stable_trajectory(self):
        """Test trajectory analysis with stable data."""
        workflow = RefactorPlanWorkflow()
        workflow._debt_history = [
            {"total_items": 50},
            {"total_items": 52},
        ]

        result, _, _ = await workflow._analyze(
            {"total_debt": 50, "by_file": {"app.py": 5}},
            ModelTier.CAPABLE,
        )

        assert result["analysis"]["trajectory"] == "stable"

    @pytest.mark.asyncio
    async def test_analyze_increasing_trajectory(self):
        """Test trajectory analysis with increasing debt."""
        workflow = RefactorPlanWorkflow()
        workflow._debt_history = [
            {"total_items": 10},
            {"total_items": 50},
        ]

        result, _, _ = await workflow._analyze(
            {"total_debt": 50, "by_file": {"app.py": 5}},
            ModelTier.CAPABLE,
        )

        assert result["analysis"]["trajectory"] == "increasing"
        assert result["analysis"]["velocity"] > 0

    @pytest.mark.asyncio
    async def test_analyze_decreasing_trajectory(self):
        """Test trajectory analysis with decreasing debt."""
        workflow = RefactorPlanWorkflow()
        workflow._debt_history = [
            {"total_items": 100},
            {"total_items": 50},
        ]

        result, _, _ = await workflow._analyze(
            {"total_debt": 50, "by_file": {}},
            ModelTier.CAPABLE,
        )

        assert result["analysis"]["trajectory"] == "decreasing"
        assert result["analysis"]["velocity"] < 0

    @pytest.mark.asyncio
    async def test_analyze_identifies_hotspots(self):
        """Test that hotspots are identified."""
        workflow = RefactorPlanWorkflow()

        by_file = {
            "big_file.py": 20,
            "medium_file.py": 10,
            "small_file.py": 2,
        }

        result, _, _ = await workflow._analyze(
            {"total_debt": 32, "by_file": by_file},
            ModelTier.CAPABLE,
        )

        assert len(result["analysis"]["hotspots"]) > 0
        # Hotspots should be sorted by debt count
        assert result["analysis"]["hotspots"][0]["debt_count"] == 20


class TestRefactorPlanPrioritize:
    """Tests for prioritize stage."""

    @pytest.mark.asyncio
    async def test_prioritize_by_weight(self):
        """Test prioritization by weight."""
        workflow = RefactorPlanWorkflow()

        debt_items = [
            {"file": "a.py", "line": 1, "marker": "TODO", "severity": "low", "weight": 1},
            {"file": "b.py", "line": 1, "marker": "HACK", "severity": "high", "weight": 5},
        ]

        result, _, _ = await workflow._prioritize(
            {"debt_items": debt_items, "analysis": {"hotspots": []}},
            ModelTier.CAPABLE,
        )

        prioritized = result["prioritized_items"]
        assert prioritized[0]["marker"] == "HACK"  # Higher weight first

    @pytest.mark.asyncio
    async def test_prioritize_hotspot_bonus(self):
        """Test hotspot files get priority bonus."""
        workflow = RefactorPlanWorkflow()

        debt_items = [
            {"file": "normal.py", "line": 1, "marker": "TODO", "severity": "low", "weight": 1},
            {"file": "hotspot.py", "line": 1, "marker": "TODO", "severity": "low", "weight": 1},
        ]
        hotspots = [{"file": "hotspot.py", "debt_count": 10}]

        result, _, _ = await workflow._prioritize(
            {"debt_items": debt_items, "analysis": {"hotspots": hotspots}},
            ModelTier.CAPABLE,
        )

        prioritized = result["prioritized_items"]
        hotspot_item = next(p for p in prioritized if p["file"] == "hotspot.py")
        normal_item = next(p for p in prioritized if p["file"] == "normal.py")

        assert hotspot_item["priority_score"] > normal_item["priority_score"]
        assert hotspot_item["is_hotspot"] is True

    @pytest.mark.asyncio
    async def test_prioritize_groups_by_tier(self):
        """Test items are grouped into priority tiers."""
        workflow = RefactorPlanWorkflow()

        debt_items = [
            {"file": "a.py", "line": 1, "marker": "HACK", "severity": "high", "weight": 5},
            {"file": "b.py", "line": 1, "marker": "TODO", "severity": "low", "weight": 1},
        ]

        result, _, _ = await workflow._prioritize(
            {"debt_items": debt_items, "analysis": {"hotspots": []}},
            ModelTier.CAPABLE,
        )

        assert "high_priority" in result
        assert "medium_priority" in result
        assert "low_priority_count" in result


class TestRefactorPlanPlan:
    """Tests for plan stage."""

    @pytest.mark.asyncio
    async def test_plan_calls_llm(self):
        """Test plan stage calls LLM."""
        workflow = RefactorPlanWorkflow()
        workflow._api_key = None  # Use simulation

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("# Refactoring Roadmap\n\n...", 300, 200)

            result, _, _ = await workflow._plan(
                {
                    "high_priority": [
                        {"file": "a.py", "line": 1, "marker": "HACK", "message": "Fix me"},
                    ],
                    "medium_priority": [],
                    "analysis": {"trajectory": "increasing", "hotspots": []},
                    "total_debt": 50,
                },
                ModelTier.PREMIUM,
            )

            mock.assert_called_once()
            assert "refactoring_plan" in result

    @pytest.mark.asyncio
    async def test_plan_generates_formatted_report(self):
        """Test plan generates formatted report."""
        workflow = RefactorPlanWorkflow()
        workflow._api_key = None

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("Roadmap here", 100, 50)

            result, _, _ = await workflow._plan(
                {
                    "high_priority": [],
                    "medium_priority": [],
                    "analysis": {"trajectory": "stable"},
                    "total_debt": 10,
                },
                ModelTier.PREMIUM,
            )

            assert "formatted_report" in result
            assert "REFACTOR PLAN REPORT" in result["formatted_report"]


class TestFormatRefactorPlanReport:
    """Tests for report formatting."""

    def test_format_report_basic(self):
        """Test basic report formatting."""
        result = {
            "summary": {
                "total_debt": 50,
                "trajectory": "increasing",
                "high_priority_count": 5,
            },
            "refactoring_plan": "Phase 1: Fix critical issues...",
            "model_tier_used": "premium",
        }
        input_data = {
            "by_marker": {"TODO": 30, "FIXME": 15, "HACK": 5},
            "files_scanned": 100,
            "analysis": {"velocity": 2.5, "historical_snapshots": 5, "hotspots": []},
            "high_priority": [],
        }

        report = format_refactor_plan_report(result, input_data)

        assert "REFACTOR PLAN REPORT" in report
        assert "Total Tech Debt Items: 50" in report
        assert "INCREASING" in report

    def test_format_report_with_hotspots(self):
        """Test report with hotspot files."""
        result = {
            "summary": {
                "total_debt": 100,
                "trajectory": "stable",
                "high_priority_count": 10,
            },
            "refactoring_plan": "",
            "model_tier_used": "capable",
        }
        input_data = {
            "by_marker": {},
            "files_scanned": 50,
            "analysis": {
                "velocity": 0,
                "historical_snapshots": 0,
                "hotspots": [
                    {"file": "bad_file.py", "debt_count": 25},
                    {"file": "worse_file.py", "debt_count": 20},
                ],
            },
            "high_priority": [],
        }

        report = format_refactor_plan_report(result, input_data)

        assert "HOTSPOT FILES" in report
        assert "bad_file.py" in report

    def test_format_report_with_high_priority(self):
        """Test report with high priority items."""
        result = {
            "summary": {
                "total_debt": 20,
                "trajectory": "decreasing",
                "high_priority_count": 2,
            },
            "refactoring_plan": "",
            "model_tier_used": "capable",
        }
        input_data = {
            "by_marker": {"HACK": 2},
            "files_scanned": 10,
            "analysis": {"velocity": -1, "historical_snapshots": 3, "hotspots": []},
            "high_priority": [
                {
                    "file": "urgent.py",
                    "line": 42,
                    "marker": "HACK",
                    "message": "Critical workaround",
                    "priority_score": 15,
                    "is_hotspot": True,
                },
            ],
        }

        report = format_refactor_plan_report(result, input_data)

        assert "HIGH PRIORITY ITEMS" in report
        assert "urgent.py" in report
        assert "HACK" in report


class TestRefactorPlanIntegration:
    """Integration tests for RefactorPlanWorkflow."""

    @pytest.mark.asyncio
    async def test_full_workflow_simulation(self):
        """Test simulated full workflow execution."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with debt
            (Path(tmpdir) / "app.py").write_text(
                """
# TODO: Add input validation
def process(data):
    # HACK: Quick fix for deadline
    return data.upper()

# FIXME: Memory leak when processing large files
""",
            )

            workflow = RefactorPlanWorkflow(patterns_dir=tmpdir)
            workflow._api_key = None

            with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
                mock.return_value = ("Phase 1: Fix memory leak...", 200, 100)

                # Run scan
                scan_result, _, _ = await workflow._scan(
                    {"path": tmpdir, "file_types": [".py"]},
                    ModelTier.CHEAP,
                )

                # Run analyze
                analyze_result, _, _ = await workflow._analyze(
                    scan_result,
                    ModelTier.CAPABLE,
                )

                # Run prioritize
                prioritize_result, _, _ = await workflow._prioritize(
                    analyze_result,
                    ModelTier.CAPABLE,
                )

                # Run plan
                plan_result, _, _ = await workflow._plan(
                    prioritize_result,
                    ModelTier.PREMIUM,
                )

                assert plan_result["summary"]["total_debt"] >= 3
                assert "formatted_report" in plan_result
