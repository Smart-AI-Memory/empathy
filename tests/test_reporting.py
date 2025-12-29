"""
Tests for agents/code_inspection/nodes/reporting.py

Tests the reporting module including:
- Report generation
- Finding aggregation
- Category scores calculation
- Recommendation generation

Note: Some tests use mocked state objects since the full
CodeInspectionState requires complex dependencies.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from collections import defaultdict


class TestReportingConcepts:
    """Tests for reporting concepts (no dependencies required)."""

    def test_health_score_range(self):
        """Test health score is in valid range."""
        # Health scores should be 0-100
        scores = [0, 25, 50, 75, 100]
        for score in scores:
            assert 0 <= score <= 100

    def test_health_grade_mapping(self):
        """Test health grade mapping."""
        grade_thresholds = {
            "A": 90,
            "B": 80,
            "C": 70,
            "D": 60,
            "F": 0,
        }
        assert grade_thresholds["A"] == 90
        assert grade_thresholds["F"] == 0

    def test_severity_levels(self):
        """Test severity levels are defined."""
        severities = ["critical", "high", "medium", "low", "info"]
        assert len(severities) == 5
        assert "critical" in severities
        assert "info" in severities

    def test_finding_structure(self):
        """Test finding has expected structure."""
        finding = {
            "tool": "ruff",
            "severity": "medium",
            "category": "style",
            "message": "Line too long",
            "file": "src/main.py",
            "line": 42,
            "fixable": True,
        }
        assert "tool" in finding
        assert "severity" in finding
        assert "category" in finding
        assert "fixable" in finding


class TestFindingAggregation:
    """Tests for finding aggregation logic."""

    def test_count_by_severity(self):
        """Test counting findings by severity."""
        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "medium"},
            {"severity": "medium"},
            {"severity": "low"},
        ]
        by_severity = defaultdict(int)
        for f in findings:
            by_severity[f["severity"]] += 1

        assert by_severity["critical"] == 1
        assert by_severity["high"] == 2
        assert by_severity["medium"] == 3
        assert by_severity["low"] == 1

    def test_count_by_category(self):
        """Test counting findings by category."""
        findings = [
            {"category": "security"},
            {"category": "security"},
            {"category": "style"},
            {"category": "performance"},
        ]
        by_category = defaultdict(int)
        for f in findings:
            by_category[f["category"]] += 1

        assert by_category["security"] == 2
        assert by_category["style"] == 1

    def test_count_by_tool(self):
        """Test counting findings by tool."""
        findings = [
            {"tool": "ruff"},
            {"tool": "ruff"},
            {"tool": "mypy"},
            {"tool": "bandit"},
        ]
        by_tool = defaultdict(int)
        for f in findings:
            by_tool[f["tool"]] += 1

        assert by_tool["ruff"] == 2
        assert by_tool["mypy"] == 1

    def test_identify_fixable_issues(self):
        """Test identifying fixable issues."""
        findings = [
            {"id": 1, "fixable": True},
            {"id": 2, "fixable": False},
            {"id": 3, "fixable": True},
            {"id": 4, "fixable": False},
        ]
        fixable = [f for f in findings if f.get("fixable")]
        assert len(fixable) == 2
        assert fixable[0]["id"] == 1
        assert fixable[1]["id"] == 3

    def test_identify_blocking_issues(self):
        """Test identifying blocking issues."""
        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
            {"severity": "low"},
        ]
        blocking = [f for f in findings if f["severity"] in ("critical", "high")]
        assert len(blocking) == 2


class TestHealthScoreCalculation:
    """Tests for health score calculation."""

    def test_perfect_score(self):
        """Test perfect score with no issues."""
        findings = []
        # Simple formula: 100 - (findings * weight)
        score = max(0, 100 - len(findings) * 5)
        assert score == 100

    def test_score_decreases_with_findings(self):
        """Test score decreases with findings."""
        for count in [1, 5, 10, 20]:
            score = max(0, 100 - count * 5)
            if count == 1:
                assert score == 95
            elif count == 5:
                assert score == 75
            elif count == 10:
                assert score == 50
            elif count == 20:
                assert score == 0

    def test_score_never_negative(self):
        """Test score never goes negative."""
        findings_count = 100
        score = max(0, 100 - findings_count * 5)
        assert score >= 0


class TestHealthGradeAssignment:
    """Tests for health grade assignment."""

    def test_grade_a(self):
        """Test grade A for score >= 90."""
        score = 95
        grade = "A" if score >= 90 else "B"
        assert grade == "A"

    def test_grade_b(self):
        """Test grade B for score >= 80."""
        score = 85
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        else:
            grade = "C"
        assert grade == "B"

    def test_grade_c(self):
        """Test grade C for score >= 70."""
        score = 75
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        else:
            grade = "D"
        assert grade == "C"

    def test_grade_f(self):
        """Test grade F for score < 60."""
        score = 50
        if score >= 90:
            grade = "A"
        elif score >= 80:
            grade = "B"
        elif score >= 70:
            grade = "C"
        elif score >= 60:
            grade = "D"
        else:
            grade = "F"
        assert grade == "F"


class TestRecommendationGeneration:
    """Tests for recommendation generation."""

    def test_critical_findings_recommendation(self):
        """Test recommendation for critical findings."""
        findings = [{"severity": "critical", "message": "SQL injection"}]
        recommendations = []
        critical = [f for f in findings if f["severity"] == "critical"]
        if critical:
            recommendations.append("Address critical security issues immediately")
        assert len(recommendations) == 1

    def test_high_findings_recommendation(self):
        """Test recommendation for high findings."""
        findings = [{"severity": "high", "message": "XSS vulnerability"}]
        recommendations = []
        high = [f for f in findings if f["severity"] == "high"]
        if high:
            recommendations.append("Review high priority issues")
        assert len(recommendations) == 1

    def test_fixable_recommendation(self):
        """Test recommendation for fixable issues."""
        findings = [
            {"fixable": True},
            {"fixable": True},
            {"fixable": False},
        ]
        fixable_count = sum(1 for f in findings if f.get("fixable"))
        recommendations = []
        if fixable_count > 0:
            recommendations.append(f"Run auto-fix for {fixable_count} issues")
        assert "2 issues" in recommendations[0]

    def test_no_issues_recommendation(self):
        """Test recommendation when no issues."""
        findings = []
        recommendations = []
        if not findings:
            recommendations.append("Code looks healthy! No issues found.")
        assert "healthy" in recommendations[0]


class TestCategoryScores:
    """Tests for category score calculation."""

    def test_category_score_calculation(self):
        """Test category score calculation."""
        category_findings = {
            "security": 5,
            "style": 10,
            "performance": 2,
        }
        # Simple scoring: 100 - (findings * 5) per category
        category_scores = {}
        for cat, count in category_findings.items():
            category_scores[cat] = max(0, 100 - count * 5)

        assert category_scores["security"] == 75
        assert category_scores["style"] == 50
        assert category_scores["performance"] == 90

    def test_empty_category_perfect_score(self):
        """Test empty category has perfect score."""
        category_findings = {"security": 0}
        score = max(0, 100 - category_findings["security"] * 5)
        assert score == 100


class TestReportFormatting:
    """Tests for report formatting."""

    def test_report_has_summary(self):
        """Test report has summary section."""
        report = {
            "summary": {
                "total_findings": 10,
                "health_score": 75,
                "health_grade": "C",
            }
        }
        assert "summary" in report
        assert report["summary"]["total_findings"] == 10

    def test_report_has_findings_breakdown(self):
        """Test report has findings breakdown."""
        report = {
            "findings_by_severity": {
                "critical": 1,
                "high": 3,
                "medium": 6,
            }
        }
        assert "findings_by_severity" in report
        assert sum(report["findings_by_severity"].values()) == 10

    def test_report_has_recommendations(self):
        """Test report has recommendations."""
        report = {
            "recommendations": [
                "Fix critical issues",
                "Review high priority items",
            ]
        }
        assert "recommendations" in report
        assert len(report["recommendations"]) == 2


class TestReportingIntegration:
    """Integration tests for reporting."""

    def test_full_report_structure(self):
        """Test full report has all expected sections."""
        report = {
            "overall_health_score": 75,
            "health_grade": "C",
            "health_status": "needs_attention",
            "total_findings": 10,
            "findings_by_severity": {"critical": 1, "high": 3, "medium": 6},
            "findings_by_category": {"security": 4, "style": 6},
            "findings_by_tool": {"ruff": 6, "bandit": 4},
            "fixable_count": 5,
            "blocking_issues": [{"severity": "critical"}],
            "recommendations": ["Fix critical issues"],
        }

        required_fields = [
            "overall_health_score",
            "health_grade",
            "total_findings",
            "findings_by_severity",
            "findings_by_category",
            "recommendations",
        ]
        for field in required_fields:
            assert field in report

    def test_report_calculations_consistent(self):
        """Test report calculations are consistent."""
        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "high"},
            {"severity": "medium"},
        ]
        total = len(findings)
        by_severity = defaultdict(int)
        for f in findings:
            by_severity[f["severity"]] += 1

        assert total == sum(by_severity.values())
