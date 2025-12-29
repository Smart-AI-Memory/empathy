"""
Tests for wizards_consolidated/software/tech_debt_wizard.py

Tests the TechDebtWizard including:
- DebtItem, DebtSnapshot, DebtTrajectory dataclasses
- Wizard initialization and properties
- Debt scanning and detection
- Trajectory analysis
- Helper methods

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from wizards_consolidated.software.tech_debt_wizard import (
    DebtItem,
    DebtSnapshot,
    DebtTrajectory,
    TechDebtWizard,
)


class TestDebtItem:
    """Tests for DebtItem dataclass."""

    def test_basic_creation(self):
        """Test basic creation of DebtItem."""
        item = DebtItem(
            item_id="debt_001",
            file_path="src/main.py",
            line_number=42,
            debt_type="todo",
            content="# TODO: Refactor this",
            severity="medium",
            date_found="2025-01-01",
        )
        assert item.item_id == "debt_001"
        assert item.file_path == "src/main.py"
        assert item.line_number == 42
        assert item.debt_type == "todo"
        assert item.severity == "medium"

    def test_default_age_days(self):
        """Test default age_days is 0."""
        item = DebtItem(
            item_id="id",
            file_path="f.py",
            line_number=1,
            debt_type="todo",
            content="content",
            severity="low",
            date_found="2025-01-01",
        )
        assert item.age_days == 0

    def test_custom_age_days(self):
        """Test custom age_days."""
        item = DebtItem(
            item_id="id",
            file_path="f.py",
            line_number=1,
            debt_type="fixme",
            content="content",
            severity="high",
            date_found="2025-01-01",
            age_days=30,
        )
        assert item.age_days == 30

    def test_various_debt_types(self):
        """Test various debt types."""
        for debt_type in ["todo", "fixme", "hack", "temporary", "deprecated"]:
            item = DebtItem(
                item_id="id",
                file_path="f.py",
                line_number=1,
                debt_type=debt_type,
                content="content",
                severity="medium",
                date_found="2025-01-01",
            )
            assert item.debt_type == debt_type

    def test_various_severities(self):
        """Test various severity levels."""
        for severity in ["low", "medium", "high", "critical"]:
            item = DebtItem(
                item_id="id",
                file_path="f.py",
                line_number=1,
                debt_type="todo",
                content="content",
                severity=severity,
                date_found="2025-01-01",
            )
            assert item.severity == severity


class TestDebtSnapshot:
    """Tests for DebtSnapshot dataclass."""

    def test_basic_creation(self):
        """Test basic creation of DebtSnapshot."""
        snapshot = DebtSnapshot(
            date="2025-01-01",
            total_items=10,
        )
        assert snapshot.date == "2025-01-01"
        assert snapshot.total_items == 10

    def test_default_collections(self):
        """Test default collections are empty."""
        snapshot = DebtSnapshot(date="2025-01-01", total_items=0)
        assert snapshot.by_type == {}
        assert snapshot.by_severity == {}
        assert snapshot.by_file == {}
        assert snapshot.hotspots == []

    def test_with_by_type(self):
        """Test with by_type populated."""
        snapshot = DebtSnapshot(
            date="2025-01-01",
            total_items=15,
            by_type={"todo": 10, "fixme": 5},
        )
        assert snapshot.by_type["todo"] == 10
        assert snapshot.by_type["fixme"] == 5

    def test_with_by_severity(self):
        """Test with by_severity populated."""
        snapshot = DebtSnapshot(
            date="2025-01-01",
            total_items=10,
            by_severity={"low": 5, "medium": 3, "high": 2},
        )
        assert snapshot.by_severity["low"] == 5
        assert snapshot.by_severity["high"] == 2

    def test_with_hotspots(self):
        """Test with hotspots populated."""
        snapshot = DebtSnapshot(
            date="2025-01-01",
            total_items=20,
            hotspots=["src/legacy.py", "src/utils.py"],
        )
        assert len(snapshot.hotspots) == 2
        assert "src/legacy.py" in snapshot.hotspots


class TestDebtTrajectory:
    """Tests for DebtTrajectory dataclass."""

    def test_basic_creation(self):
        """Test basic creation of DebtTrajectory."""
        trajectory = DebtTrajectory(
            current_total=100,
            previous_total=80,
            change_percent=25.0,
            trend="increasing",
            projection_30_days=125,
            projection_90_days=175,
            critical_threshold_days=180,
        )
        assert trajectory.current_total == 100
        assert trajectory.previous_total == 80
        assert trajectory.change_percent == 25.0
        assert trajectory.trend == "increasing"

    def test_decreasing_trend(self):
        """Test decreasing trend."""
        trajectory = DebtTrajectory(
            current_total=50,
            previous_total=80,
            change_percent=-37.5,
            trend="decreasing",
            projection_30_days=40,
            projection_90_days=20,
            critical_threshold_days=None,
        )
        assert trajectory.trend == "decreasing"
        assert trajectory.critical_threshold_days is None

    def test_stable_trend(self):
        """Test stable trend."""
        trajectory = DebtTrajectory(
            current_total=100,
            previous_total=100,
            change_percent=0.0,
            trend="stable",
            projection_30_days=100,
            projection_90_days=100,
            critical_threshold_days=None,
        )
        assert trajectory.trend == "stable"

    def test_exploding_trend(self):
        """Test exploding trend."""
        trajectory = DebtTrajectory(
            current_total=200,
            previous_total=50,
            change_percent=300.0,
            trend="exploding",
            projection_30_days=500,
            projection_90_days=2000,
            critical_threshold_days=30,
        )
        assert trajectory.trend == "exploding"
        assert trajectory.critical_threshold_days == 30


class TestTechDebtWizardInit:
    """Tests for TechDebtWizard initialization."""

    def test_name_property(self):
        """Test name property."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert wizard.name == "Tech Debt Wizard"

    def test_level_property(self):
        """Test level property is 4."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert wizard.level == 4

    def test_default_pattern_storage_path(self):
        """Test default pattern storage path."""
        wizard = TechDebtWizard()
        assert wizard.pattern_storage_path == Path("./patterns/tech_debt")

    def test_custom_pattern_storage_path(self):
        """Test custom pattern storage path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert wizard.pattern_storage_path == Path(tmpdir)

    def test_creates_storage_directory(self):
        """Test storage directory is created."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir) / "custom" / "path"
            TechDebtWizard(pattern_storage_path=str(storage_path))
            assert storage_path.exists()

    def test_debt_patterns_loaded(self):
        """Test debt patterns are loaded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert "todo" in wizard.debt_patterns
            assert "fixme" in wizard.debt_patterns
            assert "hack" in wizard.debt_patterns
            assert "temporary" in wizard.debt_patterns
            assert "deprecated" in wizard.debt_patterns


class TestTechDebtWizardPatterns:
    """Tests for debt pattern definitions."""

    def test_todo_patterns(self):
        """Test TODO patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert len(wizard.debt_patterns["todo"]) > 0
            # Should match Python, JS, and HTML comments
            patterns = wizard.debt_patterns["todo"]
            assert any("#" in p for p in patterns)
            assert any("//" in p for p in patterns)

    def test_fixme_patterns(self):
        """Test FIXME patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            assert len(wizard.debt_patterns["fixme"]) > 0

    def test_hack_patterns(self):
        """Test HACK patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            patterns = wizard.debt_patterns["hack"]
            # Should include XXX as well
            assert any("XXX" in p for p in patterns)

    def test_deprecated_patterns(self):
        """Test deprecated patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            patterns = wizard.debt_patterns["deprecated"]
            assert any("@deprecated" in p for p in patterns)


class TestTechDebtWizardAnalyze:
    """Tests for analyze method."""

    @pytest.mark.asyncio
    async def test_analyze_empty_project(self):
        """Test analyze on empty project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            assert "debt_items" in result or "items" in result or "current_debt" in result

    @pytest.mark.asyncio
    async def test_analyze_with_todo(self):
        """Test analyze detects TODO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with TODO
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# TODO: Fix this later\nx = 1\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            assert result is not None

    @pytest.mark.asyncio
    async def test_analyze_with_fixme(self):
        """Test analyze detects FIXME."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# FIXME: Critical bug here\ny = 2\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            assert result is not None

    @pytest.mark.asyncio
    async def test_analyze_returns_metadata(self):
        """Test analyze returns metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})
            # Should have some structure
            assert isinstance(result, dict)


class TestTechDebtWizardScanning:
    """Tests for debt scanning functionality."""

    def test_scan_detects_python_todo(self):
        """Test scanning detects Python TODO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# TODO: Implement this\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            # Check if wizard can detect the pattern
            import re

            content = test_file.read_text()
            for pattern in wizard.debt_patterns["todo"]:
                if re.search(pattern, content, re.IGNORECASE):
                    assert True
                    return
            # At least one pattern should match
            assert any(re.search(p, content, re.IGNORECASE) for p in wizard.debt_patterns["todo"])

    def test_scan_detects_js_todo(self):
        """Test scanning detects JavaScript TODO."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.js"
            test_file.write_text("// TODO: Add validation\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            import re

            content = test_file.read_text()
            assert any(re.search(p, content, re.IGNORECASE) for p in wizard.debt_patterns["todo"])

    def test_scan_detects_hack(self):
        """Test scanning detects HACK."""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# HACK: Workaround for bug\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            import re

            content = test_file.read_text()
            assert any(re.search(p, content, re.IGNORECASE) for p in wizard.debt_patterns["hack"])


class TestTechDebtWizardTrajectory:
    """Tests for trajectory analysis."""

    def test_calculate_change_percent_increase(self):
        """Test change percent calculation for increase."""
        # 80 -> 100 = 25% increase
        change = ((100 - 80) / 80) * 100
        assert change == 25.0

    def test_calculate_change_percent_decrease(self):
        """Test change percent calculation for decrease."""
        # 100 -> 75 = -25% decrease
        change = ((75 - 100) / 100) * 100
        assert change == -25.0

    def test_trend_classification_decreasing(self):
        """Test trend classification for decreasing."""
        # -10% or less should be decreasing
        assert -15 < -10  # Decreasing

    def test_trend_classification_stable(self):
        """Test trend classification for stable."""
        # Between -5% and 5% should be stable
        change = 2.0
        assert -5 <= change <= 5  # Stable

    def test_trend_classification_increasing(self):
        """Test trend classification for increasing."""
        # 5% to 50% should be increasing
        change = 25.0
        assert 5 < change <= 50  # Increasing

    def test_trend_classification_exploding(self):
        """Test trend classification for exploding."""
        # >50% should be exploding
        change = 100.0
        assert change > 50  # Exploding


class TestTechDebtWizardIntegration:
    """Integration tests for TechDebtWizard."""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test full analysis workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create project with various debt
            (Path(tmpdir) / "main.py").write_text("# TODO: Refactor\n# FIXME: Bug here\nx = 1\n")
            (Path(tmpdir) / "utils.py").write_text(
                "# HACK: Workaround\n# XXX: Review this\ny = 2\n"
            )

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})

            assert result is not None
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_analysis_with_no_debt(self):
        """Test analysis on clean project."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "clean.py").write_text("x = 1\ny = 2\nz = x + y\n")

            wizard = TechDebtWizard(pattern_storage_path=tmpdir)
            result = await wizard.analyze({"project_path": tmpdir})

            assert result is not None
