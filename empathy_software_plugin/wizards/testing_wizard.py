"""
Testing Wizard - Level 4 Anticipatory Empathy

Alerts developers to testing bottlenecks before they become critical.

In our experience developing the Empathy Framework across multiple projects,
this wizard identified testing scalability issues that would have surfaced
weeks later, enabling us to implement automation frameworks proactively.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class TestingWizard(BaseWizard):
    """
    Wizard that analyzes testing patterns and alerts to bottlenecks.

    Level 4 Anticipatory: Detects when testing burden will become
    unsustainable based on growth trajectory, and suggests automation
    frameworks before the crisis hits.
    """

    def __init__(self):
        super().__init__(
            name="Testing Strategy Wizard",
            domain="software",
            empathy_level=4,  # Anticipatory
            category="quality_assurance",
        )

    def get_required_context(self) -> list[str]:
        """Required context for testing analysis"""
        return [
            "project_path",  # Path to project
            "test_files",  # List of test files
            "test_framework",  # pytest, jest, junit, etc.
            "recent_commits",  # Optional: commit history
            "team_size",  # Optional: for growth analysis
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze testing patterns and predict bottlenecks.

        Args:
            context: Must contain fields from get_required_context()

        Returns:
            Dictionary with:
                - issues: Current testing problems
                - predictions: Future bottlenecks (Level 4)
                - recommendations: Actionable steps
                - patterns: Detected patterns for pattern library
                - confidence: Analysis confidence (0.0-1.0)
        """
        # Validate context
        self.validate_context(context)

        # Extract context
        test_files = context["test_files"]
        test_framework = context.get("test_framework", "unknown")
        team_size = context.get("team_size", 1)

        # Analyze current state
        issues = await self._analyze_current_tests(test_files, test_framework)

        # Level 4: Predict future bottlenecks
        predictions = await self._predict_bottlenecks(test_files, team_size, context)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, predictions)

        # Extract patterns for cross-domain learning
        patterns = self._extract_patterns(test_files, issues, predictions)

        # Calculate confidence
        confidence = self._calculate_confidence(context)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": recommendations,
            "patterns": patterns,
            "confidence": confidence,
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "test_count": len(test_files),
                "framework": test_framework,
            },
        }

    async def _analyze_current_tests(
        self, test_files: list[str], framework: str
    ) -> list[dict[str, Any]]:
        """
        Analyze current testing state (Level 1-3).

        Returns list of current issues.
        """
        issues = []

        # Check test coverage
        if len(test_files) < 5:
            issues.append(
                {
                    "severity": "warning",
                    "type": "low_test_coverage",
                    "message": "Low test count - consider adding more tests",
                    "impact": "medium",
                }
            )

        # Check for test organization
        if not self._has_test_structure(test_files):
            issues.append(
                {
                    "severity": "info",
                    "type": "test_organization",
                    "message": "Tests lack clear organization structure",
                    "impact": "low",
                }
            )

        return issues

    async def _predict_bottlenecks(
        self, test_files: list[str], team_size: int, context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Level 4 Anticipatory: Predict future testing bottlenecks.

        Based on our experience: manual testing becomes unsustainable
        when test count exceeds ~25 or execution time > 15 minutes.
        """
        predictions = []

        test_count = len(test_files)

        # Pattern from experience: Testing burden grows with codebase
        if test_count > 15:
            predictions.append(
                {
                    "type": "testing_bottleneck",
                    "alert": (
                        "Testing burden approaching critical threshold. "
                        "In our experience, manual testing becomes unsustainable "
                        "around 25+ tests. Consider implementing test automation "
                        "framework before this becomes blocking."
                    ),
                    "probability": "medium-high",
                    "impact": "high",
                    "prevention_steps": [
                        "Design test automation framework",
                        "Implement shared test fixtures",
                        "Create parameterized test generation",
                        "Set up CI/CD integration",
                    ],
                    "reasoning": (
                        "Test count trajectory suggests manual testing overhead "
                        "will become bottleneck. Proactive automation prevents "
                        "future crisis."
                    ),
                }
            )

        # Check for test duplication patterns
        if self._detect_test_duplication(test_files):
            predictions.append(
                {
                    "type": "maintenance_burden",
                    "alert": (
                        "Duplicated test patterns detected. These typically lead "
                        "to maintenance burden as codebase evolves."
                    ),
                    "probability": "high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Extract shared test utilities",
                        "Create test base classes",
                        "Implement fixture library",
                    ],
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Address high-impact predictions first
        for prediction in predictions:
            if prediction.get("impact") == "high":
                recommendations.append(f"[ALERT] {prediction['alert']}")
                recommendations.extend(f"  - {step}" for step in prediction["prevention_steps"])

        # Address current issues
        for issue in issues:
            if issue.get("severity") == "warning":
                recommendations.append(f"[WARNING] {issue['message']}")

        return recommendations

    def _extract_patterns(
        self, test_files: list[str], issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """
        Extract patterns for cross-domain learning (Level 5).

        These patterns can be applied across software, healthcare, finance, etc.
        """
        patterns = []

        # Pattern: Growth trajectory alerts
        if predictions:
            patterns.append(
                {
                    "pattern_type": "growth_trajectory_alert",
                    "description": (
                        "When system component count follows growth trajectory, "
                        "alert before threshold is reached rather than after"
                    ),
                    "domain_agnostic": True,
                    "applicable_to": [
                        "software testing",
                        "healthcare documentation",
                        "compliance tracking",
                        "any growing system",
                    ],
                }
            )

        return patterns

    def _calculate_confidence(self, context: dict[str, Any]) -> float:
        """
        Calculate confidence in analysis.

        Higher confidence when we have more context (team size, history, etc.)
        """
        confidence = 0.7  # Base confidence

        if "team_size" in context:
            confidence += 0.1

        if "recent_commits" in context:
            confidence += 0.1

        return min(1.0, confidence)

    def _has_test_structure(self, test_files: list[str]) -> bool:
        """Check if tests follow organizational structure"""
        # Simple heuristic: check for directories
        return any("/" in f for f in test_files)

    def _detect_test_duplication(self, test_files: list[str]) -> bool:
        """Detect if tests have duplication patterns"""
        # Simplified detection - in real implementation, analyze AST
        # For now, heuristic based on similar naming
        names = [f.split("/")[-1] for f in test_files]
        unique_names = set(names)
        return len(unique_names) < len(names) * 0.8  # >20% duplication
