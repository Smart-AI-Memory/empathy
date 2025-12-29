"""
Tests for empathy_llm_toolkit/agent_factory/crews/code_review.py

Tests the code review crew including:
- Severity enum
- FindingCategory enum
- Verdict enum
- ReviewFinding dataclass
- CodeReviewReport dataclass
"""

from empathy_llm_toolkit.agent_factory.crews.code_review import (
    CodeReviewReport,
    FindingCategory,
    ReviewFinding,
    Severity,
    Verdict,
)


class TestSeverityEnum:
    """Tests for Severity enum."""

    def test_critical_value(self):
        """Test CRITICAL severity value."""
        assert Severity.CRITICAL.value == "critical"

    def test_high_value(self):
        """Test HIGH severity value."""
        assert Severity.HIGH.value == "high"

    def test_medium_value(self):
        """Test MEDIUM severity value."""
        assert Severity.MEDIUM.value == "medium"

    def test_low_value(self):
        """Test LOW severity value."""
        assert Severity.LOW.value == "low"

    def test_info_value(self):
        """Test INFO severity value."""
        assert Severity.INFO.value == "info"

    def test_severity_ordering(self):
        """Test that severities can be compared via their index."""
        severities = [
            Severity.CRITICAL,
            Severity.HIGH,
            Severity.MEDIUM,
            Severity.LOW,
            Severity.INFO,
        ]
        assert len(severities) == 5


class TestFindingCategoryEnum:
    """Tests for FindingCategory enum."""

    def test_security_value(self):
        """Test SECURITY category value."""
        assert FindingCategory.SECURITY.value == "security"

    def test_architecture_value(self):
        """Test ARCHITECTURE category value."""
        assert FindingCategory.ARCHITECTURE.value == "architecture"

    def test_quality_value(self):
        """Test QUALITY category value."""
        assert FindingCategory.QUALITY.value == "quality"

    def test_performance_value(self):
        """Test PERFORMANCE category value."""
        assert FindingCategory.PERFORMANCE.value == "performance"

    def test_maintainability_value(self):
        """Test MAINTAINABILITY category value."""
        assert FindingCategory.MAINTAINABILITY.value == "maintainability"

    def test_testing_value(self):
        """Test TESTING category value."""
        assert FindingCategory.TESTING.value == "testing"

    def test_documentation_value(self):
        """Test DOCUMENTATION category value."""
        assert FindingCategory.DOCUMENTATION.value == "documentation"

    def test_style_value(self):
        """Test STYLE category value."""
        assert FindingCategory.STYLE.value == "style"

    def test_bug_value(self):
        """Test BUG category value."""
        assert FindingCategory.BUG.value == "bug"

    def test_other_value(self):
        """Test OTHER category value."""
        assert FindingCategory.OTHER.value == "other"

    def test_all_categories_count(self):
        """Test total number of categories."""
        assert len(FindingCategory) == 10


class TestVerdictEnum:
    """Tests for Verdict enum."""

    def test_approve_value(self):
        """Test APPROVE verdict value."""
        assert Verdict.APPROVE.value == "approve"

    def test_approve_with_suggestions_value(self):
        """Test APPROVE_WITH_SUGGESTIONS verdict value."""
        assert Verdict.APPROVE_WITH_SUGGESTIONS.value == "approve_with_suggestions"

    def test_request_changes_value(self):
        """Test REQUEST_CHANGES verdict value."""
        assert Verdict.REQUEST_CHANGES.value == "request_changes"

    def test_reject_value(self):
        """Test REJECT verdict value."""
        assert Verdict.REJECT.value == "reject"


class TestReviewFinding:
    """Tests for ReviewFinding dataclass."""

    def test_basic_creation(self):
        """Test basic finding creation."""
        finding = ReviewFinding(
            title="SQL Injection Risk",
            description="User input used directly in SQL query",
            severity=Severity.CRITICAL,
            category=FindingCategory.SECURITY,
        )
        assert finding.title == "SQL Injection Risk"
        assert finding.severity == Severity.CRITICAL
        assert finding.category == FindingCategory.SECURITY

    def test_optional_fields_default_none(self):
        """Test optional fields default to None."""
        finding = ReviewFinding(
            title="Test",
            description="Test description",
            severity=Severity.LOW,
            category=FindingCategory.STYLE,
        )
        assert finding.file_path is None
        assert finding.line_number is None
        assert finding.code_snippet is None
        assert finding.suggestion is None
        assert finding.before_code is None
        assert finding.after_code is None

    def test_confidence_defaults_to_one(self):
        """Test confidence defaults to 1.0."""
        finding = ReviewFinding(
            title="Test",
            description="Test",
            severity=Severity.INFO,
            category=FindingCategory.OTHER,
        )
        assert finding.confidence == 1.0

    def test_metadata_defaults_to_empty_dict(self):
        """Test metadata defaults to empty dict."""
        finding = ReviewFinding(
            title="Test",
            description="Test",
            severity=Severity.LOW,
            category=FindingCategory.STYLE,
        )
        assert finding.metadata == {}

    def test_full_finding_creation(self):
        """Test finding with all fields populated."""
        finding = ReviewFinding(
            title="Hardcoded API Key",
            description="API key should be in environment variable",
            severity=Severity.HIGH,
            category=FindingCategory.SECURITY,
            file_path="src/config.py",
            line_number=42,
            code_snippet='API_KEY = "sk_live_..."',
            suggestion="Use os.getenv('API_KEY')",
            before_code='API_KEY = "sk_live_abc123"',
            after_code='API_KEY = os.getenv("API_KEY")',
            confidence=0.95,
            metadata={"detector": "secrets_scanner"},
        )
        assert finding.file_path == "src/config.py"
        assert finding.line_number == 42
        assert finding.confidence == 0.95
        assert finding.metadata["detector"] == "secrets_scanner"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        finding = ReviewFinding(
            title="Missing Error Handler",
            description="API call lacks error handling",
            severity=Severity.MEDIUM,
            category=FindingCategory.QUALITY,
            file_path="src/api.py",
            line_number=100,
        )
        data = finding.to_dict()
        assert data["title"] == "Missing Error Handler"
        assert data["severity"] == "medium"
        assert data["category"] == "quality"
        assert data["file_path"] == "src/api.py"
        assert data["line_number"] == 100

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        finding = ReviewFinding(
            title="Test",
            description="Test",
            severity=Severity.LOW,
            category=FindingCategory.STYLE,
        )
        data = finding.to_dict()
        expected_keys = [
            "title",
            "description",
            "severity",
            "category",
            "file_path",
            "line_number",
            "code_snippet",
            "suggestion",
            "before_code",
            "after_code",
            "confidence",
            "metadata",
        ]
        for key in expected_keys:
            assert key in data


class TestCodeReviewReport:
    """Tests for CodeReviewReport dataclass."""

    def test_basic_creation(self):
        """Test basic report creation."""
        report = CodeReviewReport(
            target="feature/new-api",
            findings=[],
            verdict=Verdict.APPROVE,
        )
        assert report.target == "feature/new-api"
        assert report.findings == []
        assert report.verdict == Verdict.APPROVE

    def test_default_values(self):
        """Test default values."""
        report = CodeReviewReport(
            target="test",
            findings=[],
            verdict=Verdict.APPROVE,
        )
        assert report.summary == ""
        assert report.review_duration_seconds == 0.0
        assert report.agents_used == []
        assert report.memory_graph_hits == 0
        assert report.metadata == {}

    def test_critical_findings_property(self):
        """Test critical_findings property filters correctly."""
        findings = [
            ReviewFinding("Critical 1", "Desc", Severity.CRITICAL, FindingCategory.SECURITY),
            ReviewFinding("High 1", "Desc", Severity.HIGH, FindingCategory.QUALITY),
            ReviewFinding("Critical 2", "Desc", Severity.CRITICAL, FindingCategory.BUG),
            ReviewFinding("Low 1", "Desc", Severity.LOW, FindingCategory.STYLE),
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.REQUEST_CHANGES,
        )
        critical = report.critical_findings
        assert len(critical) == 2
        assert all(f.severity == Severity.CRITICAL for f in critical)

    def test_high_findings_property(self):
        """Test high_findings property filters correctly."""
        findings = [
            ReviewFinding("Critical 1", "Desc", Severity.CRITICAL, FindingCategory.SECURITY),
            ReviewFinding("High 1", "Desc", Severity.HIGH, FindingCategory.QUALITY),
            ReviewFinding("High 2", "Desc", Severity.HIGH, FindingCategory.PERFORMANCE),
            ReviewFinding("Medium 1", "Desc", Severity.MEDIUM, FindingCategory.STYLE),
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.REQUEST_CHANGES,
        )
        high = report.high_findings
        assert len(high) == 2
        assert all(f.severity == Severity.HIGH for f in high)

    def test_findings_by_category_property(self):
        """Test findings_by_category groups correctly."""
        findings = [
            ReviewFinding("Sec 1", "Desc", Severity.HIGH, FindingCategory.SECURITY),
            ReviewFinding("Sec 2", "Desc", Severity.MEDIUM, FindingCategory.SECURITY),
            ReviewFinding("Qual 1", "Desc", Severity.LOW, FindingCategory.QUALITY),
            ReviewFinding("Perf 1", "Desc", Severity.MEDIUM, FindingCategory.PERFORMANCE),
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.APPROVE_WITH_SUGGESTIONS,
        )
        by_cat = report.findings_by_category
        assert len(by_cat["security"]) == 2
        assert len(by_cat["quality"]) == 1
        assert len(by_cat["performance"]) == 1

    def test_quality_score_perfect(self):
        """Test quality score is 100 with no findings."""
        report = CodeReviewReport(
            target="test",
            findings=[],
            verdict=Verdict.APPROVE,
        )
        assert report.quality_score == 100.0

    def test_quality_score_with_findings(self):
        """Test quality score deducts based on severity."""
        findings = [
            ReviewFinding("Critical", "Desc", Severity.CRITICAL, FindingCategory.SECURITY),
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.REQUEST_CHANGES,
        )
        # CRITICAL deducts 25 points
        assert report.quality_score == 75.0

    def test_quality_score_multiple_findings(self):
        """Test quality score with multiple findings."""
        findings = [
            ReviewFinding("High", "Desc", Severity.HIGH, FindingCategory.SECURITY),
            ReviewFinding("Medium", "Desc", Severity.MEDIUM, FindingCategory.QUALITY),
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.REQUEST_CHANGES,
        )
        # HIGH = -15, MEDIUM = -5, total = 100 - 20 = 80
        assert report.quality_score == 80.0

    def test_quality_score_minimum_zero(self):
        """Test quality score doesn't go below 0."""
        # 5 critical findings = 5 * 25 = 125 deductions, but score floors at 0
        findings = [
            ReviewFinding(f"Critical {i}", "Desc", Severity.CRITICAL, FindingCategory.BUG)
            for i in range(5)
        ]
        report = CodeReviewReport(
            target="test",
            findings=findings,
            verdict=Verdict.REJECT,
        )
        assert report.quality_score >= 0.0

    def test_report_with_agents_and_metadata(self):
        """Test report with agents and metadata."""
        report = CodeReviewReport(
            target="feature/api-v2",
            findings=[],
            verdict=Verdict.APPROVE,
            summary="Clean implementation with good test coverage",
            review_duration_seconds=45.5,
            agents_used=["security_agent", "quality_agent", "style_agent"],
            memory_graph_hits=3,
            metadata={"reviewer": "automated", "version": "1.0"},
        )
        assert len(report.agents_used) == 3
        assert report.memory_graph_hits == 3
        assert report.review_duration_seconds == 45.5
        assert report.metadata["reviewer"] == "automated"


class TestReviewFindingCategories:
    """Tests verifying finding categories work with findings."""

    def test_security_finding(self):
        """Test creating security category finding."""
        finding = ReviewFinding(
            title="XSS Vulnerability",
            description="User input not sanitized before rendering",
            severity=Severity.HIGH,
            category=FindingCategory.SECURITY,
            suggestion="Use HTML escaping before rendering",
        )
        assert finding.category == FindingCategory.SECURITY
        assert finding.to_dict()["category"] == "security"

    def test_performance_finding(self):
        """Test creating performance category finding."""
        finding = ReviewFinding(
            title="N+1 Query",
            description="Database query inside loop",
            severity=Severity.MEDIUM,
            category=FindingCategory.PERFORMANCE,
            suggestion="Use eager loading or batch queries",
        )
        assert finding.category == FindingCategory.PERFORMANCE

    def test_testing_finding(self):
        """Test creating testing category finding."""
        finding = ReviewFinding(
            title="Missing Unit Tests",
            description="New function has no test coverage",
            severity=Severity.MEDIUM,
            category=FindingCategory.TESTING,
            suggestion="Add unit tests for edge cases",
        )
        assert finding.category == FindingCategory.TESTING


class TestReviewIntegration:
    """Integration tests for review components working together."""

    def test_complete_review_workflow(self):
        """Test creating a complete review with multiple findings."""
        findings = [
            ReviewFinding(
                title="SQL Injection",
                description="Raw SQL with user input",
                severity=Severity.CRITICAL,
                category=FindingCategory.SECURITY,
                file_path="src/db.py",
                line_number=45,
                suggestion="Use parameterized queries",
            ),
            ReviewFinding(
                title="Missing Docstring",
                description="Function lacks documentation",
                severity=Severity.INFO,
                category=FindingCategory.DOCUMENTATION,
                file_path="src/utils.py",
                line_number=12,
            ),
            ReviewFinding(
                title="Unused Import",
                description="Import not used in file",
                severity=Severity.LOW,
                category=FindingCategory.STYLE,
                file_path="src/main.py",
                line_number=3,
            ),
        ]

        report = CodeReviewReport(
            target="PR #123: Add user authentication",
            findings=findings,
            verdict=Verdict.REQUEST_CHANGES,
            summary="Critical security issue found. Please address before merging.",
            agents_used=["security_agent", "style_agent", "docs_agent"],
        )

        # Verify report structure
        assert len(report.findings) == 3
        assert len(report.critical_findings) == 1
        assert report.verdict == Verdict.REQUEST_CHANGES

        # Verify category grouping
        by_cat = report.findings_by_category
        assert "security" in by_cat
        assert "documentation" in by_cat
        assert "style" in by_cat

        # Quality score should reflect critical finding
        assert report.quality_score < 100.0
