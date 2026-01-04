"""Tests for Code Health Assistant Module

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from empathy_llm_toolkit.code_health import (
    CHECK_WEIGHTS,
    DEFAULT_CONFIG,
    AutoFixer,
    CheckCategory,
    CheckResult,
    HealthCheckRunner,
    HealthIssue,
    HealthReport,
    HealthStatus,
    HealthTrendTracker,
    format_health_output,
)


@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    tmp = tempfile.mkdtemp()
    yield tmp
    shutil.rmtree(tmp)


@pytest.fixture
def sample_report():
    """Create a sample health report for testing."""
    report = HealthReport()

    # Add lint result with issues
    lint_issues = [
        HealthIssue(
            category=CheckCategory.LINT,
            file_path="src/test.py",
            line=10,
            code="W291",
            message="trailing whitespace",
            severity="warning",
            fixable=True,
            fix_command="ruff check --fix src/test.py",
        ),
        HealthIssue(
            category=CheckCategory.LINT,
            file_path="src/test.py",
            line=20,
            code="F841",
            message="unused variable 'x'",
            severity="warning",
            fixable=True,
        ),
    ]
    report.add_result(
        CheckResult(
            category=CheckCategory.LINT,
            status=HealthStatus.WARN,
            score=80,
            issues=lint_issues,
            tool_used="ruff",
        ),
    )

    # Add passing test result
    report.add_result(
        CheckResult(
            category=CheckCategory.TESTS,
            status=HealthStatus.PASS,
            score=100,
            issues=[],
            tool_used="pytest",
            details={"passed": 50, "failed": 0, "total": 50},
        ),
    )

    return report


class TestHealthIssue:
    """Tests for HealthIssue dataclass."""

    def test_issue_creation(self):
        """Test creating a health issue."""
        issue = HealthIssue(
            category=CheckCategory.LINT,
            file_path="src/test.py",
            line=42,
            code="F401",
            message="unused import",
            severity="warning",
            fixable=True,
        )

        assert issue.category == CheckCategory.LINT
        assert issue.file_path == "src/test.py"
        assert issue.line == 42
        assert issue.code == "F401"
        assert issue.fixable is True

    def test_issue_to_dict(self):
        """Test converting issue to dictionary."""
        issue = HealthIssue(
            category=CheckCategory.SECURITY,
            file_path="src/auth.py",
            line=100,
            code="B301",
            message="hardcoded password",
            severity="error",
        )

        data = issue.to_dict()
        assert data["category"] == "security"
        assert data["file_path"] == "src/auth.py"
        assert data["severity"] == "error"


class TestCheckResult:
    """Tests for CheckResult dataclass."""

    def test_result_creation(self):
        """Test creating a check result."""
        result = CheckResult(
            category=CheckCategory.TESTS,
            status=HealthStatus.PASS,
            score=100,
            tool_used="pytest",
        )

        assert result.category == CheckCategory.TESTS
        assert result.status == HealthStatus.PASS
        assert result.score == 100
        assert result.issue_count == 0

    def test_result_with_issues(self):
        """Test check result with issues."""
        issues = [
            HealthIssue(
                category=CheckCategory.LINT,
                file_path="test.py",
                line=1,
                code="E501",
                message="line too long",
                fixable=True,
            ),
            HealthIssue(
                category=CheckCategory.LINT,
                file_path="test.py",
                line=2,
                code="F841",
                message="unused var",
                fixable=False,
            ),
        ]

        result = CheckResult(
            category=CheckCategory.LINT,
            status=HealthStatus.WARN,
            score=70,
            issues=issues,
        )

        assert result.issue_count == 2
        assert result.fixable_count == 1


class TestHealthReport:
    """Tests for HealthReport dataclass."""

    def test_empty_report(self):
        """Test creating an empty report."""
        report = HealthReport()

        assert report.overall_score == 100
        assert report.status == HealthStatus.PASS
        assert report.total_issues == 0

    def test_add_result(self):
        """Test adding results to report."""
        report = HealthReport()

        result = CheckResult(
            category=CheckCategory.LINT,
            status=HealthStatus.WARN,
            score=70,
            issues=[],
        )
        report.add_result(result)

        assert len(report.results) == 1
        assert report.overall_score < 100

    def test_score_calculation(self):
        """Test weighted score calculation."""
        report = HealthReport()

        # Add high-weight failing check (security)
        report.add_result(
            CheckResult(
                category=CheckCategory.SECURITY,
                status=HealthStatus.FAIL,
                score=50,
            ),
        )

        # Add low-weight passing check (deps)
        report.add_result(
            CheckResult(
                category=CheckCategory.DEPS,
                status=HealthStatus.PASS,
                score=100,
            ),
        )

        # Security has higher weight, should pull score down significantly
        assert report.overall_score < 80
        assert report.status == HealthStatus.WARN or report.status == HealthStatus.FAIL

    def test_get_result(self):
        """Test getting specific result by category."""
        report = HealthReport()
        report.add_result(
            CheckResult(category=CheckCategory.LINT, status=HealthStatus.PASS, score=100),
        )

        lint_result = report.get_result(CheckCategory.LINT)
        assert lint_result is not None
        assert lint_result.category == CheckCategory.LINT

        # Non-existent category
        types_result = report.get_result(CheckCategory.TYPES)
        assert types_result is None


class TestHealthCheckRunner:
    """Tests for HealthCheckRunner class."""

    def test_runner_initialization(self, temp_dir):
        """Test runner initialization."""
        runner = HealthCheckRunner(project_root=temp_dir)

        assert runner.project_root == Path(temp_dir).resolve()
        assert runner.config == DEFAULT_CONFIG

    def test_runner_custom_config(self, temp_dir):
        """Test runner with custom config."""
        custom_config = {
            "checks": {
                "lint": {"enabled": True, "tool": "flake8"},
                "tests": {"enabled": False},
            },
        }
        runner = HealthCheckRunner(project_root=temp_dir, config=custom_config)

        assert runner.config["checks"]["lint"]["tool"] == "flake8"

    def test_tool_availability_check(self, temp_dir):
        """Test tool availability checking."""
        runner = HealthCheckRunner(project_root=temp_dir)

        # python should always be available
        assert runner._is_tool_available("python") is True
        # nonsense tool should not be available
        assert runner._is_tool_available("nonexistent_tool_xyz") is False

    @patch("subprocess.run")
    def test_lint_check_skip_when_tool_unavailable(self, mock_run, temp_dir):
        """Test lint check skips when tool unavailable."""
        runner = HealthCheckRunner(project_root=temp_dir)

        with patch.object(runner, "_is_tool_available", return_value=False):
            result = runner._run_lint_check({"tool": "ruff"})

        assert result.status == HealthStatus.SKIP
        assert result.score == 100

    @patch("subprocess.run")
    def test_lint_check_parses_ruff_output(self, mock_run, temp_dir):
        """Test lint check parses ruff JSON output."""
        runner = HealthCheckRunner(project_root=temp_dir)

        # Mock ruff output
        mock_run.return_value = MagicMock(
            stdout=json.dumps(
                [
                    {
                        "filename": "test.py",
                        "location": {"row": 10},
                        "code": "W291",
                        "message": "trailing whitespace",
                        "fix": {"applicability": "safe"},
                    },
                ],
            ),
            returncode=1,
        )

        with patch.object(runner, "_is_tool_available", return_value=True):
            result = runner._run_lint_check({"tool": "ruff"})

        assert result.status == HealthStatus.WARN
        assert result.issue_count == 1
        assert result.issues[0].code == "W291"


class TestAutoFixer:
    """Tests for AutoFixer class."""

    def test_fixer_initialization(self):
        """Test auto-fixer initialization."""
        fixer = AutoFixer()

        assert fixer.safe_fixes is True
        assert fixer.prompt_fixes is True

    def test_preview_fixes(self, sample_report):
        """Test previewing fixes."""
        fixer = AutoFixer()

        fixes = fixer.preview_fixes(sample_report)

        assert len(fixes) > 0
        assert all("category" in f for f in fixes)
        assert all("safe" in f for f in fixes)

    def test_is_safe_fix(self):
        """Test safe fix detection."""
        fixer = AutoFixer()

        # Format fixes are safe
        format_issue = HealthIssue(
            category=CheckCategory.FORMAT,
            file_path="test.py",
            line=None,
            code="FORMAT",
            message="needs formatting",
            fixable=True,
        )
        assert fixer._is_safe_fix(format_issue) is True

        # Whitespace fixes are safe
        whitespace_issue = HealthIssue(
            category=CheckCategory.LINT,
            file_path="test.py",
            line=10,
            code="W291",
            message="trailing whitespace",
            fixable=True,
        )
        assert fixer._is_safe_fix(whitespace_issue) is True


class TestHealthTrendTracker:
    """Tests for HealthTrendTracker class."""

    def test_tracker_initialization(self, temp_dir):
        """Test trend tracker initialization."""
        tracker = HealthTrendTracker(project_root=temp_dir)

        assert tracker.project_root == Path(temp_dir)
        assert tracker.history_dir.exists()

    def test_record_check(self, temp_dir, sample_report):
        """Test recording a health check."""
        tracker = HealthTrendTracker(project_root=temp_dir)

        tracker.record_check(sample_report)

        today = datetime.now().strftime("%Y-%m-%d")
        filepath = tracker.history_dir / f"{today}.json"

        assert filepath.exists()

        data = json.loads(filepath.read_text())
        assert len(data) == 1
        assert "overall_score" in data[0]

    def test_get_trends_empty(self, temp_dir):
        """Test getting trends with no history."""
        tracker = HealthTrendTracker(project_root=temp_dir)

        trends = tracker.get_trends(days=7)

        assert trends["period_days"] == 7
        assert len(trends["data_points"]) == 0
        assert trends["trend_direction"] == "stable"

    def test_identify_hotspots_empty(self, temp_dir):
        """Test identifying hotspots with no history."""
        tracker = HealthTrendTracker(project_root=temp_dir)

        hotspots = tracker.identify_hotspots()

        assert len(hotspots) == 0


class TestFormatHealthOutput:
    """Tests for output formatting."""

    def test_format_summary(self, sample_report):
        """Test summary format (level 1)."""
        output = format_health_output(sample_report, level=1)

        assert "Code Health:" in output
        assert "Lint:" in output
        assert "Tests:" in output

    def test_format_details(self, sample_report):
        """Test details format (level 2)."""
        output = format_health_output(sample_report, level=2)

        assert "Details:" in output
        assert "LINT" in output

    def test_format_full(self, sample_report):
        """Test full format (level 3)."""
        output = format_health_output(sample_report, level=3)

        assert "Full Report" in output
        assert "Generated:" in output
        assert "Duration:" in output

    def test_status_icons(self):
        """Test correct status icons for different scores."""
        # Good score
        good_report = HealthReport()
        good_report.add_result(
            CheckResult(category=CheckCategory.LINT, status=HealthStatus.PASS, score=90),
        )
        output = format_health_output(good_report)
        assert "Good" in output

        # Warning score
        warn_report = HealthReport()
        warn_report.add_result(
            CheckResult(category=CheckCategory.LINT, status=HealthStatus.WARN, score=75),
        )
        output = format_health_output(warn_report)
        assert "Warning" in output


class TestCheckWeights:
    """Tests for check weight constants."""

    def test_weights_defined(self):
        """Test all categories have weights."""
        for category in CheckCategory:
            assert category in CHECK_WEIGHTS

    def test_security_highest(self):
        """Test security has highest weight."""
        assert CHECK_WEIGHTS[CheckCategory.SECURITY] == 100

    def test_deps_lowest(self):
        """Test deps has lowest weight."""
        min_weight = min(CHECK_WEIGHTS.values())
        assert CHECK_WEIGHTS[CheckCategory.DEPS] == min_weight


class TestCheckCategories:
    """Tests for check category enumeration."""

    def test_all_categories_exist(self):
        """Test all expected categories exist."""
        expected = ["lint", "format", "types", "tests", "coverage", "security", "deps"]
        for name in expected:
            assert CheckCategory(name) is not None

    def test_category_values(self):
        """Test category values are lowercase strings."""
        for category in CheckCategory:
            assert category.value == category.value.lower()


class TestHealthStatus:
    """Tests for health status enumeration."""

    def test_all_statuses_exist(self):
        """Test all expected statuses exist."""
        expected = ["pass", "warn", "fail", "skip", "error"]
        for name in expected:
            assert HealthStatus(name) is not None
