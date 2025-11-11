"""
Base Coach Wizard - Foundation for all Coach wizards

Level 4 Anticipatory Empathy implementation using the Empathy Framework.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class WizardIssue:
    """Represents an issue found by a wizard"""

    severity: str  # 'error', 'warning', 'info'
    message: str
    file_path: str
    line_number: int | None
    code_snippet: str | None
    fix_suggestion: str | None
    category: str
    confidence: float  # 0.0 to 1.0


@dataclass
class WizardPrediction:
    """Level 4 Anticipatory: Predicts future issues"""

    predicted_date: datetime
    issue_type: str
    probability: float
    impact: str  # 'low', 'medium', 'high', 'critical'
    prevention_steps: list[str]
    reasoning: str


@dataclass
class WizardResult:
    """Result from running a wizard"""

    wizard_name: str
    issues: list[WizardIssue]
    predictions: list[WizardPrediction]
    summary: str
    analyzed_files: int
    analysis_time: float
    recommendations: list[str]


class BaseCoachWizard(ABC):
    """
    Base class for all Coach wizards

    Implements Level 4 Anticipatory Empathy:
    - Analyzes current code
    - Predicts future issues (30-90 days ahead)
    - Provides prevention strategies
    """

    def __init__(self, name: str, category: str, languages: list[str]):
        self.name = name
        self.category = category
        self.languages = languages
        self.logger = logging.getLogger(f"coach.{name}")

    @abstractmethod
    def analyze_code(self, code: str, file_path: str, language: str) -> list[WizardIssue]:
        """
        Analyze code for current issues

        Args:
            code: Source code to analyze
            file_path: Path to the file being analyzed
            language: Programming language

        Returns:
            List of issues found
        """
        pass

    @abstractmethod
    def predict_future_issues(
        self, code: str, file_path: str, project_context: dict[str, Any], timeline_days: int = 90
    ) -> list[WizardPrediction]:
        """
        Level 4 Anticipatory: Predict issues 30-90 days ahead

        Args:
            code: Source code to analyze
            file_path: Path to the file
            project_context: Project metadata (size, team, deployment frequency, etc.)
            timeline_days: How far ahead to predict (default 90 days)

        Returns:
            List of predicted future issues
        """
        pass

    @abstractmethod
    def suggest_fixes(self, issue: WizardIssue) -> str:
        """
        Suggest how to fix an issue

        Args:
            issue: The issue to fix

        Returns:
            Fix suggestion with code examples
        """
        pass

    def run_full_analysis(
        self,
        code: str,
        file_path: str,
        language: str,
        project_context: dict[str, Any] | None = None,
    ) -> WizardResult:
        """
        Run complete analysis: current issues + future predictions

        Args:
            code: Source code to analyze
            file_path: Path to the file
            language: Programming language
            project_context: Optional project context for predictions

        Returns:
            Complete wizard result
        """
        start_time = datetime.now()

        # Analyze current code
        issues = self.analyze_code(code, file_path, language)

        # Predict future issues (Level 4)
        predictions = []
        if project_context:
            predictions = self.predict_future_issues(
                code, file_path, project_context, timeline_days=90
            )

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, predictions)

        # Calculate summary
        summary = self._generate_summary(issues, predictions)

        analysis_time = (datetime.now() - start_time).total_seconds()

        return WizardResult(
            wizard_name=self.name,
            issues=issues,
            predictions=predictions,
            summary=summary,
            analyzed_files=1,
            analysis_time=analysis_time,
            recommendations=recommendations,
        )

    def _generate_recommendations(
        self, issues: list[WizardIssue], predictions: list[WizardPrediction]
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Address current critical issues
        critical_issues = [i for i in issues if i.severity == "error"]
        if critical_issues:
            recommendations.append(f"Fix {len(critical_issues)} critical issues immediately")

        # Address predictions
        high_probability_predictions = [p for p in predictions if p.probability > 0.7]
        if high_probability_predictions:
            recommendations.append(
                f"Prevent {len(high_probability_predictions)} predicted issues with high probability"
            )

        return recommendations

    def _generate_summary(
        self, issues: list[WizardIssue], predictions: list[WizardPrediction]
    ) -> str:
        """Generate human-readable summary"""
        error_count = len([i for i in issues if i.severity == "error"])
        warning_count = len([i for i in issues if i.severity == "warning"])
        prediction_count = len(predictions)

        summary = f"{self.name} Analysis: "
        summary += f"{error_count} errors, {warning_count} warnings found. "

        if prediction_count > 0:
            summary += f"{prediction_count} future issues predicted (Level 4 Anticipatory)."

        return summary
