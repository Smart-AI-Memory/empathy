"""
Comprehensive tests for BaseCoachWizard and related dataclasses

Tests cover:
- WizardIssue, WizardPrediction, WizardResult dataclasses
- BaseCoachWizard initialization
- Full analysis workflow
- Recommendation generation
- Summary generation
"""

from datetime import datetime, timedelta

import pytest

from coach_wizards.base_wizard import (
    BaseCoachWizard,
    WizardIssue,
    WizardPrediction,
    WizardResult,
)


class ConcreteWizard(BaseCoachWizard):
    """Concrete implementation for testing"""

    def analyze_code(self, code: str, file_path: str, language: str):
        """Test implementation returns predefined issues"""
        return [
            WizardIssue(
                severity="error",
                message="Critical bug found",
                file_path=file_path,
                line_number=10,
                code_snippet="buggy_code()",
                fix_suggestion="Use safe_code() instead",
                category="security",
                confidence=0.95,
            ),
            WizardIssue(
                severity="warning",
                message="Code smell detected",
                file_path=file_path,
                line_number=20,
                code_snippet="smelly_code()",
                fix_suggestion="Refactor this section",
                category="maintainability",
                confidence=0.7,
            ),
            WizardIssue(
                severity="info",
                message="Consider optimization",
                file_path=file_path,
                line_number=30,
                code_snippet="slow_code()",
                fix_suggestion="Use faster algorithm",
                category="performance",
                confidence=0.5,
            ),
        ]

    def predict_future_issues(
        self, code: str, file_path: str, project_context: dict, timeline_days: int = 90
    ):
        """Test implementation returns predictions"""
        future_date = datetime.now() + timedelta(days=timeline_days // 2)
        return [
            WizardPrediction(
                predicted_date=future_date,
                issue_type="Technical Debt",
                probability=0.85,
                impact="high",
                prevention_steps=[
                    "Add unit tests",
                    "Refactor complex functions",
                    "Update documentation",
                ],
                reasoning="Code complexity is increasing without test coverage",
            ),
            WizardPrediction(
                predicted_date=future_date,
                issue_type="Performance degradation",
                probability=0.6,
                impact="medium",
                prevention_steps=["Add caching", "Optimize database queries"],
                reasoning="Database queries are not optimized",
            ),
        ]

    def suggest_fixes(self, issue: WizardIssue) -> str:
        """Test implementation returns fix suggestion"""
        return f"To fix {issue.category} issue: {issue.fix_suggestion}"


class TestWizardDataclasses:
    """Test dataclass structures"""

    def test_wizard_issue_creation(self):
        """Test WizardIssue dataclass"""
        issue = WizardIssue(
            severity="error",
            message="Test error",
            file_path="/test/file.py",
            line_number=42,
            code_snippet="bad_code()",
            fix_suggestion="Use good_code()",
            category="security",
            confidence=0.95,
        )

        assert issue.severity == "error"
        assert issue.message == "Test error"
        assert issue.file_path == "/test/file.py"
        assert issue.line_number == 42
        assert issue.code_snippet == "bad_code()"
        assert issue.fix_suggestion == "Use good_code()"
        assert issue.category == "security"
        assert issue.confidence == 0.95

    def test_wizard_issue_optional_fields(self):
        """Test WizardIssue with None values"""
        issue = WizardIssue(
            severity="warning",
            message="Test warning",
            file_path="/test/file.py",
            line_number=None,
            code_snippet=None,
            fix_suggestion=None,
            category="style",
            confidence=0.5,
        )

        assert issue.line_number is None
        assert issue.code_snippet is None
        assert issue.fix_suggestion is None

    def test_wizard_prediction_creation(self):
        """Test WizardPrediction dataclass"""
        future_date = datetime(2025, 12, 31)
        prediction = WizardPrediction(
            predicted_date=future_date,
            issue_type="Memory leak",
            probability=0.75,
            impact="critical",
            prevention_steps=["Add memory profiling", "Fix circular references"],
            reasoning="Increasing memory usage pattern detected",
        )

        assert prediction.predicted_date == future_date
        assert prediction.issue_type == "Memory leak"
        assert prediction.probability == 0.75
        assert prediction.impact == "critical"
        assert len(prediction.prevention_steps) == 2
        assert "memory profiling" in prediction.prevention_steps[0].lower()

    def test_wizard_result_creation(self):
        """Test WizardResult dataclass"""
        issue = WizardIssue(
            severity="error",
            message="Test",
            file_path="/test.py",
            line_number=1,
            code_snippet=None,
            fix_suggestion=None,
            category="test",
            confidence=0.9,
        )

        prediction = WizardPrediction(
            predicted_date=datetime.now(),
            issue_type="Test issue",
            probability=0.8,
            impact="medium",
            prevention_steps=["Test"],
            reasoning="Testing",
        )

        result = WizardResult(
            wizard_name="TestWizard",
            issues=[issue],
            predictions=[prediction],
            summary="1 error found",
            analyzed_files=5,
            analysis_time=1.234,
            recommendations=["Fix the error"],
        )

        assert result.wizard_name == "TestWizard"
        assert len(result.issues) == 1
        assert len(result.predictions) == 1
        assert result.summary == "1 error found"
        assert result.analyzed_files == 5
        assert result.analysis_time == 1.234
        assert len(result.recommendations) == 1


class TestBaseCoachWizard:
    """Test BaseCoachWizard functionality"""

    def test_wizard_initialization(self):
        """Test wizard initialization"""
        wizard = ConcreteWizard(
            name="TestWizard",
            category="testing",
            languages=["python", "javascript"],
        )

        assert wizard.name == "TestWizard"
        assert wizard.category == "testing"
        assert wizard.languages == ["python", "javascript"]
        assert wizard.logger is not None

    def test_full_analysis_without_context(self):
        """Test run_full_analysis without project context"""
        wizard = ConcreteWizard(
            name="SecurityWizard",
            category="security",
            languages=["python"],
        )

        code = "def test():\n    pass"
        result = wizard.run_full_analysis(
            code=code,
            file_path="/test/file.py",
            language="python",
            project_context=None,
        )

        assert isinstance(result, WizardResult)
        assert result.wizard_name == "SecurityWizard"
        assert len(result.issues) == 3  # Our test implementation returns 3
        assert len(result.predictions) == 0  # No predictions without context
        assert result.analyzed_files == 1
        assert result.analysis_time >= 0  # May be 0.0 on fast systems
        assert isinstance(result.summary, str)

    def test_full_analysis_with_context(self):
        """Test run_full_analysis with project context"""
        wizard = ConcreteWizard(
            name="QualityWizard",
            category="quality",
            languages=["python"],
        )

        code = "def test():\n    pass"
        context = {"team_size": 5, "deploy_frequency": "daily"}

        result = wizard.run_full_analysis(
            code=code,
            file_path="/test/file.py",
            language="python",
            project_context=context,
        )

        assert isinstance(result, WizardResult)
        assert len(result.issues) == 3
        assert len(result.predictions) == 2  # Our test implementation returns 2
        assert "Level 4 Anticipatory" in result.summary

    def test_recommendations_with_critical_issues(self):
        """Test _generate_recommendations with critical issues"""
        wizard = ConcreteWizard(
            name="TestWizard",
            category="test",
            languages=["python"],
        )

        issues = [
            WizardIssue(
                severity="error",
                message="Critical 1",
                file_path="/test.py",
                line_number=1,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.9,
            ),
            WizardIssue(
                severity="error",
                message="Critical 2",
                file_path="/test.py",
                line_number=2,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.9,
            ),
            WizardIssue(
                severity="warning",
                message="Warning",
                file_path="/test.py",
                line_number=3,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.7,
            ),
        ]

        predictions = []
        recommendations = wizard._generate_recommendations(issues, predictions)

        assert len(recommendations) > 0
        assert any("2 critical issues" in rec for rec in recommendations)

    def test_recommendations_with_high_probability_predictions(self):
        """Test _generate_recommendations with high probability predictions"""
        wizard = ConcreteWizard(
            name="TestWizard",
            category="test",
            languages=["python"],
        )

        issues = []
        predictions = [
            WizardPrediction(
                predicted_date=datetime.now(),
                issue_type="Test1",
                probability=0.9,  # High probability
                impact="high",
                prevention_steps=["Step1"],
                reasoning="Reason1",
            ),
            WizardPrediction(
                predicted_date=datetime.now(),
                issue_type="Test2",
                probability=0.8,  # High probability
                impact="medium",
                prevention_steps=["Step2"],
                reasoning="Reason2",
            ),
            WizardPrediction(
                predicted_date=datetime.now(),
                issue_type="Test3",
                probability=0.5,  # Low probability
                impact="low",
                prevention_steps=["Step3"],
                reasoning="Reason3",
            ),
        ]

        recommendations = wizard._generate_recommendations(issues, predictions)

        assert len(recommendations) > 0
        assert any("predicted issues" in rec for rec in recommendations)

    def test_summary_generation_no_predictions(self):
        """Test _generate_summary without predictions"""
        wizard = ConcreteWizard(
            name="SummaryWizard",
            category="test",
            languages=["python"],
        )

        issues = [
            WizardIssue(
                severity="error",
                message="Error 1",
                file_path="/test.py",
                line_number=1,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.9,
            ),
            WizardIssue(
                severity="warning",
                message="Warning 1",
                file_path="/test.py",
                line_number=2,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.7,
            ),
            WizardIssue(
                severity="warning",
                message="Warning 2",
                file_path="/test.py",
                line_number=3,
                code_snippet=None,
                fix_suggestion=None,
                category="test",
                confidence=0.7,
            ),
        ]

        predictions = []
        summary = wizard._generate_summary(issues, predictions)

        assert "SummaryWizard" in summary
        assert "1 errors" in summary
        assert "2 warnings" in summary

    def test_summary_generation_with_predictions(self):
        """Test _generate_summary with predictions"""
        wizard = ConcreteWizard(
            name="PredictiveWizard",
            category="test",
            languages=["python"],
        )

        issues = []
        predictions = [
            WizardPrediction(
                predicted_date=datetime.now(),
                issue_type="Test",
                probability=0.8,
                impact="medium",
                prevention_steps=["Step"],
                reasoning="Reason",
            )
        ]

        summary = wizard._generate_summary(issues, predictions)

        assert "0 errors" in summary
        assert "0 warnings" in summary
        assert "1 future issues predicted" in summary
        assert "Level 4 Anticipatory" in summary

    def test_suggest_fixes_abstract_method_implementation(self):
        """Test suggest_fixes implementation"""
        wizard = ConcreteWizard(
            name="FixWizard",
            category="test",
            languages=["python"],
        )

        issue = WizardIssue(
            severity="error",
            message="Security vulnerability",
            file_path="/test.py",
            line_number=42,
            code_snippet="unsafe_code()",
            fix_suggestion="Use safe implementation",
            category="security",
            confidence=0.95,
        )

        fix = wizard.suggest_fixes(issue)

        assert isinstance(fix, str)
        assert "security" in fix
        assert "safe implementation" in fix.lower()

    def test_analysis_time_measurement(self):
        """Test that analysis time is properly measured"""
        wizard = ConcreteWizard(
            name="TimingWizard",
            category="test",
            languages=["python"],
        )

        result = wizard.run_full_analysis(
            code="def test(): pass",
            file_path="/test.py",
            language="python",
            project_context={"test": "context"},
        )

        # Analysis should take some time (even if minimal)
        assert result.analysis_time >= 0
        assert isinstance(result.analysis_time, float)

    def test_empty_issues_and_predictions(self):
        """Test handling of empty issues and predictions lists"""

        class EmptyWizard(BaseCoachWizard):
            def analyze_code(self, code, file_path, language):
                return []

            def predict_future_issues(self, code, file_path, project_context, timeline_days=90):
                return []

            def suggest_fixes(self, issue):
                return "No fixes needed"

        wizard = EmptyWizard(name="EmptyWizard", category="test", languages=["python"])

        result = wizard.run_full_analysis(
            code="pass",
            file_path="/test.py",
            language="python",
            project_context={"test": "context"},
        )

        assert len(result.issues) == 0
        assert len(result.predictions) == 0
        assert "0 errors" in result.summary
        assert "0 warnings" in result.summary
        assert len(result.recommendations) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
