"""Tests for empathy_llm_toolkit/agent_factory/crews/health_check.py

Tests the health check crew including:
- HealthCategory enum
- IssueSeverity enum
- FixStatus enum
- HealthIssue dataclass
- HealthFix dataclass
- HealthCheckReport dataclass
- HealthCheckConfig dataclass
"""

from empathy_llm_toolkit.agent_factory.crews.health_check import (
    FixStatus,
    HealthCategory,
    HealthCheckConfig,
    HealthCheckReport,
    HealthFix,
    HealthIssue,
    IssueSeverity,
)


class TestHealthCategoryEnum:
    """Tests for HealthCategory enum."""

    def test_lint_value(self):
        """Test LINT category value."""
        assert HealthCategory.LINT.value == "lint"

    def test_types_value(self):
        """Test TYPES category value."""
        assert HealthCategory.TYPES.value == "types"

    def test_tests_value(self):
        """Test TESTS category value."""
        assert HealthCategory.TESTS.value == "tests"

    def test_dependencies_value(self):
        """Test DEPENDENCIES category value."""
        assert HealthCategory.DEPENDENCIES.value == "dependencies"

    def test_security_value(self):
        """Test SECURITY category value."""
        assert HealthCategory.SECURITY.value == "security"

    def test_general_value(self):
        """Test GENERAL category value."""
        assert HealthCategory.GENERAL.value == "general"

    def test_all_categories_count(self):
        """Test total number of categories."""
        assert len(HealthCategory) == 6

    def test_category_from_string(self):
        """Test creating HealthCategory from string."""
        assert HealthCategory("lint") == HealthCategory.LINT
        assert HealthCategory("types") == HealthCategory.TYPES
        assert HealthCategory("tests") == HealthCategory.TESTS


class TestIssueSeverityEnum:
    """Tests for IssueSeverity enum."""

    def test_critical_value(self):
        """Test CRITICAL severity value."""
        assert IssueSeverity.CRITICAL.value == "critical"

    def test_high_value(self):
        """Test HIGH severity value."""
        assert IssueSeverity.HIGH.value == "high"

    def test_medium_value(self):
        """Test MEDIUM severity value."""
        assert IssueSeverity.MEDIUM.value == "medium"

    def test_low_value(self):
        """Test LOW severity value."""
        assert IssueSeverity.LOW.value == "low"

    def test_info_value(self):
        """Test INFO severity value."""
        assert IssueSeverity.INFO.value == "info"

    def test_all_severities_count(self):
        """Test total number of severities."""
        assert len(IssueSeverity) == 5

    def test_severity_from_string(self):
        """Test creating IssueSeverity from string."""
        assert IssueSeverity("critical") == IssueSeverity.CRITICAL
        assert IssueSeverity("high") == IssueSeverity.HIGH


class TestFixStatusEnum:
    """Tests for FixStatus enum."""

    def test_applied_value(self):
        """Test APPLIED status value."""
        assert FixStatus.APPLIED.value == "applied"

    def test_suggested_value(self):
        """Test SUGGESTED status value."""
        assert FixStatus.SUGGESTED.value == "suggested"

    def test_failed_value(self):
        """Test FAILED status value."""
        assert FixStatus.FAILED.value == "failed"

    def test_skipped_value(self):
        """Test SKIPPED status value."""
        assert FixStatus.SKIPPED.value == "skipped"

    def test_all_statuses_count(self):
        """Test total number of statuses."""
        assert len(FixStatus) == 4

    def test_status_from_string(self):
        """Test creating FixStatus from string."""
        assert FixStatus("applied") == FixStatus.APPLIED
        assert FixStatus("suggested") == FixStatus.SUGGESTED


class TestHealthIssue:
    """Tests for HealthIssue dataclass."""

    def test_basic_creation(self):
        """Test basic HealthIssue creation."""
        issue = HealthIssue(
            title="Lint Error",
            description="Unused import",
            category=HealthCategory.LINT,
            severity=IssueSeverity.LOW,
        )
        assert issue.title == "Lint Error"
        assert issue.description == "Unused import"
        assert issue.category == HealthCategory.LINT
        assert issue.severity == IssueSeverity.LOW

    def test_optional_fields_default_none(self):
        """Test optional fields default to None."""
        issue = HealthIssue(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            severity=IssueSeverity.INFO,
        )
        assert issue.file_path is None
        assert issue.line_number is None
        assert issue.code_snippet is None
        assert issue.tool is None
        assert issue.rule_id is None

    def test_metadata_defaults_to_empty_dict(self):
        """Test metadata defaults to empty dict."""
        issue = HealthIssue(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            severity=IssueSeverity.INFO,
        )
        assert issue.metadata == {}

    def test_full_issue_creation(self):
        """Test issue with all fields populated."""
        issue = HealthIssue(
            title="Type Error",
            description="Argument type mismatch",
            category=HealthCategory.TYPES,
            severity=IssueSeverity.HIGH,
            file_path="src/main.py",
            line_number=42,
            code_snippet="foo(123)",
            tool="mypy",
            rule_id="arg-type",
            metadata={"function": "foo"},
        )
        assert issue.file_path == "src/main.py"
        assert issue.line_number == 42
        assert issue.tool == "mypy"
        assert issue.rule_id == "arg-type"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        issue = HealthIssue(
            title="Security Issue",
            description="SQL injection",
            category=HealthCategory.SECURITY,
            severity=IssueSeverity.CRITICAL,
            file_path="src/db.py",
            line_number=100,
        )
        data = issue.to_dict()
        assert data["title"] == "Security Issue"
        assert data["category"] == "security"
        assert data["severity"] == "critical"
        assert data["file_path"] == "src/db.py"
        assert data["line_number"] == 100

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        issue = HealthIssue(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            severity=IssueSeverity.INFO,
        )
        data = issue.to_dict()
        expected_keys = [
            "title",
            "description",
            "category",
            "severity",
            "file_path",
            "line_number",
            "code_snippet",
            "tool",
            "rule_id",
            "metadata",
        ]
        for key in expected_keys:
            assert key in data


class TestHealthFix:
    """Tests for HealthFix dataclass."""

    def test_basic_creation(self):
        """Test basic HealthFix creation."""
        fix = HealthFix(
            title="Auto-fix lint",
            description="Removed unused import",
            category=HealthCategory.LINT,
            status=FixStatus.APPLIED,
        )
        assert fix.title == "Auto-fix lint"
        assert fix.status == FixStatus.APPLIED

    def test_optional_fields_default_none(self):
        """Test optional fields default to None."""
        fix = HealthFix(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            status=FixStatus.SUGGESTED,
        )
        assert fix.file_path is None
        assert fix.before_code is None
        assert fix.after_code is None
        assert fix.patch is None

    def test_related_issues_defaults_to_empty_list(self):
        """Test related_issues defaults to empty list."""
        fix = HealthFix(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            status=FixStatus.SUGGESTED,
        )
        assert fix.related_issues == []

    def test_metadata_defaults_to_empty_dict(self):
        """Test metadata defaults to empty dict."""
        fix = HealthFix(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            status=FixStatus.SUGGESTED,
        )
        assert fix.metadata == {}

    def test_full_fix_creation(self):
        """Test fix with all fields populated."""
        fix = HealthFix(
            title="Fix type error",
            description="Added type annotation",
            category=HealthCategory.TYPES,
            status=FixStatus.APPLIED,
            file_path="src/utils.py",
            before_code="def foo(x):",
            after_code="def foo(x: int) -> str:",
            patch="@@ -1 +1 @@\n-def foo(x):\n+def foo(x: int) -> str:",
            related_issues=["Type error on line 10"],
            metadata={"auto_fix": True},
        )
        assert fix.file_path == "src/utils.py"
        assert fix.before_code == "def foo(x):"
        assert fix.after_code == "def foo(x: int) -> str:"
        assert "Type error" in fix.related_issues[0]

    def test_to_dict(self):
        """Test serialization to dictionary."""
        fix = HealthFix(
            title="Fix",
            description="Fixed",
            category=HealthCategory.TESTS,
            status=FixStatus.APPLIED,
            file_path="tests/test_foo.py",
        )
        data = fix.to_dict()
        assert data["title"] == "Fix"
        assert data["category"] == "tests"
        assert data["status"] == "applied"
        assert data["file_path"] == "tests/test_foo.py"

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        fix = HealthFix(
            title="Test",
            description="Test",
            category=HealthCategory.GENERAL,
            status=FixStatus.SUGGESTED,
        )
        data = fix.to_dict()
        expected_keys = [
            "title",
            "description",
            "category",
            "status",
            "file_path",
            "before_code",
            "after_code",
            "patch",
            "related_issues",
            "metadata",
        ]
        for key in expected_keys:
            assert key in data


class TestHealthCheckReport:
    """Tests for HealthCheckReport dataclass."""

    def test_basic_creation(self):
        """Test basic report creation."""
        report = HealthCheckReport(
            target=".",
            issues=[],
            fixes=[],
            health_score=100.0,
        )
        assert report.target == "."
        assert report.issues == []
        assert report.fixes == []
        assert report.health_score == 100.0

    def test_default_values(self):
        """Test default values."""
        report = HealthCheckReport(
            target="test",
            issues=[],
            fixes=[],
            health_score=90.0,
        )
        assert report.check_duration_seconds == 0.0
        assert report.agents_used == []
        assert report.memory_graph_hits == 0
        assert report.checks_run == {}
        assert report.metadata == {}

    def test_critical_issues_property(self):
        """Test critical_issues property filters correctly."""
        issues = [
            HealthIssue("Critical", "Desc", HealthCategory.SECURITY, IssueSeverity.CRITICAL),
            HealthIssue("High", "Desc", HealthCategory.LINT, IssueSeverity.HIGH),
            HealthIssue("Critical2", "Desc", HealthCategory.TESTS, IssueSeverity.CRITICAL),
        ]
        report = HealthCheckReport(
            target="test",
            issues=issues,
            fixes=[],
            health_score=50.0,
        )
        critical = report.critical_issues
        assert len(critical) == 2
        assert all(i.severity == IssueSeverity.CRITICAL for i in critical)

    def test_applied_fixes_property(self):
        """Test applied_fixes property filters correctly."""
        fixes = [
            HealthFix("Fix1", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
            HealthFix("Fix2", "Desc", HealthCategory.TYPES, FixStatus.SUGGESTED),
            HealthFix("Fix3", "Desc", HealthCategory.TESTS, FixStatus.APPLIED),
        ]
        report = HealthCheckReport(
            target="test",
            issues=[],
            fixes=fixes,
            health_score=80.0,
        )
        applied = report.applied_fixes
        assert len(applied) == 2
        assert all(f.status == FixStatus.APPLIED for f in applied)

    def test_issues_by_category_property(self):
        """Test issues_by_category groups correctly."""
        issues = [
            HealthIssue("Lint1", "Desc", HealthCategory.LINT, IssueSeverity.LOW),
            HealthIssue("Lint2", "Desc", HealthCategory.LINT, IssueSeverity.LOW),
            HealthIssue("Type1", "Desc", HealthCategory.TYPES, IssueSeverity.MEDIUM),
        ]
        report = HealthCheckReport(
            target="test",
            issues=issues,
            fixes=[],
            health_score=85.0,
        )
        by_cat = report.issues_by_category
        assert len(by_cat["lint"]) == 2
        assert len(by_cat["types"]) == 1

    def test_is_healthy_true_when_high_score(self):
        """Test is_healthy is True when score >= 80."""
        report = HealthCheckReport(
            target="test",
            issues=[],
            fixes=[],
            health_score=80.0,
        )
        assert report.is_healthy is True

    def test_is_healthy_false_when_low_score(self):
        """Test is_healthy is False when score < 80."""
        report = HealthCheckReport(
            target="test",
            issues=[],
            fixes=[],
            health_score=79.9,
        )
        assert report.is_healthy is False

    def test_is_healthy_boundary(self):
        """Test is_healthy at boundary value."""
        report_80 = HealthCheckReport(target="test", issues=[], fixes=[], health_score=80.0)
        report_79 = HealthCheckReport(target="test", issues=[], fixes=[], health_score=79.0)
        assert report_80.is_healthy is True
        assert report_79.is_healthy is False

    def test_to_dict(self):
        """Test report serialization to dictionary."""
        issues = [HealthIssue("Test", "Desc", HealthCategory.GENERAL, IssueSeverity.INFO)]
        fixes = [HealthFix("Fix", "Desc", HealthCategory.GENERAL, FixStatus.APPLIED)]
        report = HealthCheckReport(
            target="./src",
            issues=issues,
            fixes=fixes,
            health_score=95.0,
            check_duration_seconds=10.5,
            agents_used=["lint_agent"],
        )
        data = report.to_dict()
        assert data["target"] == "./src"
        assert data["health_score"] == 95.0
        assert data["check_duration_seconds"] == 10.5
        assert len(data["issues"]) == 1
        assert len(data["fixes"]) == 1
        assert data["is_healthy"] is True

    def test_to_dict_issue_counts(self):
        """Test to_dict includes issue counts."""
        issues = [
            HealthIssue("Crit", "Desc", HealthCategory.SECURITY, IssueSeverity.CRITICAL),
            HealthIssue("High", "Desc", HealthCategory.LINT, IssueSeverity.HIGH),
        ]
        report = HealthCheckReport(
            target="test",
            issues=issues,
            fixes=[],
            health_score=60.0,
        )
        data = report.to_dict()
        assert data["issue_counts"]["critical"] == 1
        assert data["issue_counts"]["total"] == 2

    def test_to_dict_fix_counts(self):
        """Test to_dict includes fix counts."""
        fixes = [
            HealthFix("Fix1", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
            HealthFix("Fix2", "Desc", HealthCategory.LINT, FixStatus.SUGGESTED),
        ]
        report = HealthCheckReport(
            target="test",
            issues=[],
            fixes=fixes,
            health_score=85.0,
        )
        data = report.to_dict()
        assert data["fix_counts"]["applied"] == 1
        assert data["fix_counts"]["total"] == 2


class TestHealthCheckConfig:
    """Tests for HealthCheckConfig dataclass."""

    def test_default_provider(self):
        """Test default provider is anthropic."""
        config = HealthCheckConfig()
        assert config.provider == "anthropic"

    def test_custom_provider(self):
        """Test custom provider."""
        config = HealthCheckConfig(provider="openai")
        assert config.provider == "openai"

    def test_is_dataclass(self):
        """Test HealthCheckConfig is a dataclass."""
        assert hasattr(HealthCheckConfig, "__dataclass_fields__")


class TestEnumComparisons:
    """Tests for enum comparisons and membership."""

    def test_severity_in_list(self):
        """Test severity can be used in list membership."""
        high_severity = [IssueSeverity.CRITICAL, IssueSeverity.HIGH]
        assert IssueSeverity.CRITICAL in high_severity
        assert IssueSeverity.LOW not in high_severity

    def test_category_equality(self):
        """Test category equality."""
        assert HealthCategory.LINT == HealthCategory.LINT
        assert HealthCategory.LINT != HealthCategory.TYPES

    def test_status_equality(self):
        """Test status equality."""
        assert FixStatus.APPLIED == FixStatus.APPLIED
        assert FixStatus.APPLIED != FixStatus.FAILED


class TestIssueFiltering:
    """Tests for issue filtering scenarios."""

    def test_filter_by_category(self):
        """Test filtering issues by category."""
        issues = [
            HealthIssue("L1", "Desc", HealthCategory.LINT, IssueSeverity.LOW),
            HealthIssue("T1", "Desc", HealthCategory.TYPES, IssueSeverity.MEDIUM),
            HealthIssue("L2", "Desc", HealthCategory.LINT, IssueSeverity.LOW),
        ]
        lint_issues = [i for i in issues if i.category == HealthCategory.LINT]
        assert len(lint_issues) == 2

    def test_filter_by_severity(self):
        """Test filtering issues by severity."""
        issues = [
            HealthIssue("I1", "Desc", HealthCategory.GENERAL, IssueSeverity.CRITICAL),
            HealthIssue("I2", "Desc", HealthCategory.GENERAL, IssueSeverity.LOW),
            HealthIssue("I3", "Desc", HealthCategory.GENERAL, IssueSeverity.CRITICAL),
        ]
        critical = [i for i in issues if i.severity == IssueSeverity.CRITICAL]
        assert len(critical) == 2

    def test_filter_by_file_path(self):
        """Test filtering issues by file path."""
        issues = [
            HealthIssue("I1", "Desc", HealthCategory.LINT, IssueSeverity.LOW, file_path="src/a.py"),
            HealthIssue("I2", "Desc", HealthCategory.LINT, IssueSeverity.LOW, file_path="src/b.py"),
            HealthIssue("I3", "Desc", HealthCategory.LINT, IssueSeverity.LOW, file_path="src/a.py"),
        ]
        a_issues = [i for i in issues if i.file_path == "src/a.py"]
        assert len(a_issues) == 2


class TestFixFiltering:
    """Tests for fix filtering scenarios."""

    def test_filter_by_status(self):
        """Test filtering fixes by status."""
        fixes = [
            HealthFix("F1", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
            HealthFix("F2", "Desc", HealthCategory.LINT, FixStatus.FAILED),
            HealthFix("F3", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
        ]
        applied = [f for f in fixes if f.status == FixStatus.APPLIED]
        assert len(applied) == 2

    def test_filter_by_category(self):
        """Test filtering fixes by category."""
        fixes = [
            HealthFix("F1", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
            HealthFix("F2", "Desc", HealthCategory.TYPES, FixStatus.APPLIED),
        ]
        lint_fixes = [f for f in fixes if f.category == HealthCategory.LINT]
        assert len(lint_fixes) == 1


class TestReportScenarios:
    """Tests for various report scenarios."""

    def test_perfect_health_report(self):
        """Test report with no issues."""
        report = HealthCheckReport(
            target=".",
            issues=[],
            fixes=[],
            health_score=100.0,
        )
        assert report.is_healthy is True
        assert len(report.critical_issues) == 0
        assert len(report.applied_fixes) == 0

    def test_failing_health_report(self):
        """Test report with critical issues."""
        issues = [
            HealthIssue("Critical Bug", "Desc", HealthCategory.TESTS, IssueSeverity.CRITICAL),
            HealthIssue(
                "Another Critical",
                "Desc",
                HealthCategory.SECURITY,
                IssueSeverity.CRITICAL,
            ),
        ]
        report = HealthCheckReport(
            target=".",
            issues=issues,
            fixes=[],
            health_score=30.0,
        )
        assert report.is_healthy is False
        assert len(report.critical_issues) == 2

    def test_report_with_mixed_fixes(self):
        """Test report with mixed fix statuses."""
        fixes = [
            HealthFix("Applied", "Desc", HealthCategory.LINT, FixStatus.APPLIED),
            HealthFix("Suggested", "Desc", HealthCategory.LINT, FixStatus.SUGGESTED),
            HealthFix("Failed", "Desc", HealthCategory.LINT, FixStatus.FAILED),
            HealthFix("Skipped", "Desc", HealthCategory.LINT, FixStatus.SKIPPED),
        ]
        report = HealthCheckReport(
            target=".",
            issues=[],
            fixes=fixes,
            health_score=90.0,
        )
        assert len(report.applied_fixes) == 1
        assert len(report.fixes) == 4
