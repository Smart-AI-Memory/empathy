"""Tests for Advanced Debugging Wizard

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json

import pytest

from empathy_software_plugin.wizards.advanced_debugging_wizard import AdvancedDebuggingWizard
from empathy_software_plugin.wizards.debugging import (
    BugRisk,
    BugRiskAnalyzer,
    LintIssue,
    Severity,
    get_pattern_library,
    parse_linter_output,
)

# Mock data
MOCK_ESLINT_JSON = json.dumps(
    [
        {
            "filePath": "/test/file.js",
            "messages": [
                {
                    "line": 10,
                    "column": 5,
                    "severity": 2,
                    "message": "'foo' is not defined",
                    "ruleId": "no-undef",
                },
                {
                    "line": 20,
                    "column": 8,
                    "severity": 1,
                    "message": "Missing semicolon",
                    "ruleId": "semi",
                },
            ],
        },
    ],
)

MOCK_PYLINT_JSON = json.dumps(
    [
        {
            "path": "/test/file.py",
            "line": 15,
            "column": 4,
            "type": "error",
            "message": "Undefined variable 'bar'",
            "message-id": "E0602",
            "symbol": "undefined-variable",
        },
    ],
)


class TestLinterParsers:
    """Test linter output parsing"""

    def test_eslint_json_parsing(self):
        """Test ESLint JSON parsing"""
        issues = parse_linter_output("eslint", MOCK_ESLINT_JSON, "json")

        assert len(issues) == 2
        assert issues[0].rule == "no-undef"
        assert issues[0].severity == Severity.ERROR
        assert issues[0].line == 10

    def test_pylint_json_parsing(self):
        """Test Pylint JSON parsing"""
        issues = parse_linter_output("pylint", MOCK_PYLINT_JSON, "json")

        assert len(issues) == 1
        # Pylint parser uses symbol field if available, otherwise message-id
        assert issues[0].rule in ["undefined-variable", "E0602"]
        assert issues[0].line == 15

    def test_standardized_format(self):
        """Test that all parsers produce standardized LintIssue"""
        eslint_issues = parse_linter_output("eslint", MOCK_ESLINT_JSON, "json")
        pylint_issues = parse_linter_output("pylint", MOCK_PYLINT_JSON, "json")

        # Both should be LintIssue objects
        assert isinstance(eslint_issues[0], LintIssue)
        assert isinstance(pylint_issues[0], LintIssue)

        # Both should have required fields
        assert hasattr(eslint_issues[0], "file_path")
        assert hasattr(eslint_issues[0], "line")
        assert hasattr(eslint_issues[0], "rule")
        assert hasattr(pylint_issues[0], "severity")


class TestBugRiskAnalyzer:
    """Test Level 4 bug risk analysis"""

    def test_critical_risk_detection(self):
        """Test detection of critical risk issues"""
        analyzer = BugRiskAnalyzer()

        # Create critical issue
        issue = LintIssue(
            file_path="/test.js",
            line=10,
            column=5,
            rule="no-undef",
            message="'foo' is not defined",
            severity=Severity.ERROR,
            linter="eslint",
        )

        assessments = analyzer.analyze([issue])

        assert len(assessments) == 1
        assert assessments[0].risk_level == BugRisk.CRITICAL
        assert assessments[0].likelihood == 1.0

    def test_style_issue_detection(self):
        """Test detection of style-only issues"""
        analyzer = BugRiskAnalyzer()

        issue = LintIssue(
            file_path="/test.js",
            line=20,
            column=8,
            rule="semi",
            message="Missing semicolon",
            severity=Severity.WARNING,
            linter="eslint",
        )

        assessments = analyzer.analyze([issue])

        assert len(assessments) == 1
        assert assessments[0].risk_level == BugRisk.STYLE
        assert assessments[0].likelihood == 0.0

    def test_risk_summary_generation(self):
        """Test risk summary generation"""
        analyzer = BugRiskAnalyzer()

        issues = [
            LintIssue(
                file_path="/test.js",
                line=10,
                column=5,
                rule="no-undef",
                message="'foo' is not defined",
                severity=Severity.ERROR,
                linter="eslint",
            ),
            LintIssue(
                file_path="/test.js",
                line=20,
                column=8,
                rule="eqeqeq",
                message="Use ===",
                severity=Severity.WARNING,
                linter="eslint",
            ),
        ]

        assessments = analyzer.analyze(issues)
        summary = analyzer.generate_summary(assessments)

        assert summary["total_issues"] == 2
        assert summary["by_risk_level"]["critical"] == 1
        assert summary["by_risk_level"]["high"] == 1
        assert summary["alert_level"] == "CRITICAL"


class TestCrossLanguagePatterns:
    """Test Level 5 cross-language pattern library"""

    def test_pattern_library_exists(self):
        """Test that pattern library is accessible"""
        lib = get_pattern_library()

        assert lib is not None
        patterns = lib.get_all_patterns()
        assert len(patterns) > 0

    def test_undefined_reference_pattern(self):
        """Test that undefined reference pattern exists across languages"""
        lib = get_pattern_library()

        pattern = lib.patterns.get("undefined_reference")

        assert pattern is not None
        assert "javascript" in pattern.language_manifestations
        assert "python" in pattern.language_manifestations
        assert "typescript" in pattern.language_manifestations

    def test_find_pattern_for_rule(self):
        """Test finding pattern by linter rule"""
        lib = get_pattern_library()

        # Find pattern for JavaScript no-undef
        pattern = lib.find_pattern_for_rule("javascript", "no-undef")

        assert pattern is not None
        assert pattern.name == "Undefined Reference"

    def test_cross_language_insight(self):
        """Test generating cross-language insight"""
        lib = get_pattern_library()

        insight = lib.suggest_cross_language_insight(
            from_language="javascript",
            to_language="python",
            pattern_name="undefined_reference",
        )

        assert insight is not None
        assert "javascript" in insight.lower()
        assert "python" in insight.lower()


class TestAdvancedDebuggingWizard:
    """Test the main wizard"""

    @pytest.mark.asyncio
    async def test_basic_analysis(self):
        """Test basic wizard analysis"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {
                "project_path": "/test",
                "linters": {"eslint": MOCK_ESLINT_JSON, "pylint": MOCK_PYLINT_JSON},
            },
        )

        # Check standard outputs
        assert "issues_found" in result
        assert "linters" in result
        assert "risk_assessment" in result
        assert "predictions" in result
        assert "recommendations" in result

        # Check issue count
        assert result["issues_found"] == 3  # 2 from ESLint + 1 from Pylint

    @pytest.mark.asyncio
    async def test_risk_assessment_output(self):
        """Test that risk assessment is included"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        risk = result["risk_assessment"]

        assert "alert_level" in risk
        assert "by_risk_level" in risk
        assert "recommendation" in risk

    @pytest.mark.asyncio
    async def test_trajectory_analysis(self):
        """Test Level 4 trajectory analysis"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        trajectory = result["trajectory"]

        assert "state" in trajectory
        assert "total_issues" in trajectory
        assert "recommendation" in trajectory

    @pytest.mark.asyncio
    async def test_predictions_generated(self):
        """Test that Level 4 predictions are generated"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        predictions = result["predictions"]

        assert isinstance(predictions, list)
        # Should have at least one prediction for critical issue
        assert len(predictions) > 0

    @pytest.mark.asyncio
    async def test_fixability_analysis(self):
        """Test fixability grouping"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        fixability = result["fixability"]

        assert "eslint" in fixability
        assert "auto_fixable" in fixability["eslint"]
        assert "manual" in fixability["eslint"]

    @pytest.mark.asyncio
    async def test_recommendations_generated(self):
        """Test that actionable recommendations are generated"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        recommendations = result["recommendations"]

        assert isinstance(recommendations, list)
        assert len(recommendations) > 0

    @pytest.mark.asyncio
    async def test_standard_wizard_interface(self):
        """Test that wizard follows BaseWizard interface"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": MOCK_ESLINT_JSON}},
        )

        # Check standard wizard outputs
        assert "predictions" in result
        assert "recommendations" in result
        assert "patterns" in result
        assert "confidence" in result

        # Confidence should be between 0 and 1
        assert 0 <= result["confidence"] <= 1


class TestIntegration:
    """Integration tests"""

    @pytest.mark.asyncio
    async def test_multi_linter_analysis(self):
        """Test analyzing multiple linters at once"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {
                "project_path": "/test",
                "linters": {"eslint": MOCK_ESLINT_JSON, "pylint": MOCK_PYLINT_JSON},
            },
        )

        # Should process both linters
        assert "eslint" in result["linters"]
        assert "pylint" in result["linters"]

        # Total issues should be sum of both
        eslint_count = result["linters"]["eslint"]["total_issues"]
        pylint_count = result["linters"]["pylint"]["total_issues"]
        assert result["issues_found"] == eslint_count + pylint_count

    @pytest.mark.asyncio
    async def test_empty_linter_output(self):
        """Test handling empty linter output"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze(
            {"project_path": "/test", "linters": {"eslint": json.dumps([])}},
        )

        assert result["issues_found"] == 0
        assert result["risk_assessment"]["alert_level"] == "NONE"

    @pytest.mark.asyncio
    async def test_missing_linters_parameter(self):
        """Test error handling when linters not provided"""
        wizard = AdvancedDebuggingWizard()

        result = await wizard.analyze({"project_path": "/test"})

        assert "error" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
