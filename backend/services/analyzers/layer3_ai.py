"""
Layer 3 AI Analyzer - Proactive Intelligence
Notices patterns and offers improvements using AI assistance.
"""

from typing import Any

from .base_analyzer import BaseAnalyzer, Issue, IssueSeverity


class AIAnalyzer(BaseAnalyzer):
    """Level 3 AI-powered analyzer for proactive code analysis."""

    @property
    def name(self) -> str:
        return "AI Proactive Analyzer"

    @property
    def level(self) -> int:
        return 3  # Level 3: Proactive

    async def analyze(self, context: dict[str, Any]) -> list[Issue]:
        """
        Perform AI-powered proactive analysis.

        Args:
            context: Analysis context including code, patterns, and metrics

        Returns:
            List of detected issues with recommendations
        """
        issues = []

        # Analyze code patterns
        if "code" in context:
            issues.extend(await self._analyze_code_patterns(context["code"]))

        # Analyze for improvements
        if "metrics" in context:
            issues.extend(await self._analyze_metrics(context["metrics"]))

        # Check for anti-patterns
        if "patterns" in context:
            issues.extend(await self._check_antipatterns(context["patterns"]))

        return issues

    async def _analyze_code_patterns(self, code: str) -> list[Issue]:
        """Analyze code for patterns and potential improvements."""
        issues = []

        # Check for common issues
        if "try:" in code and "except:" in code:
            if "except Exception:" in code or "except:" in code:
                issues.append(
                    self._create_issue(
                        title="Overly broad exception handling",
                        description="Using broad exception catching can hide errors. Consider catching specific exceptions.",
                        severity=IssueSeverity.MEDIUM,
                        category="error_handling",
                        recommendations=[
                            "Catch specific exception types",
                            "Log exceptions appropriately",
                            "Consider letting critical exceptions propagate",
                        ],
                        confidence=0.85,
                    )
                )

        # Check for potential performance issues
        if "for " in code and ".append(" in code and "[]" in code:
            issues.append(
                self._create_issue(
                    title="Potential inefficient list building",
                    description="Consider using list comprehension for better performance.",
                    severity=IssueSeverity.LOW,
                    category="performance",
                    recommendations=[
                        "Use list comprehension instead of append in loop",
                        "Consider generator expressions for large datasets",
                    ],
                    confidence=0.70,
                )
            )

        return issues

    async def _analyze_metrics(self, metrics: dict[str, Any]) -> list[Issue]:
        """Analyze code metrics for potential issues."""
        issues = []

        # Check complexity metrics
        if "complexity" in metrics:
            complexity = metrics["complexity"]
            if complexity > 10:
                issues.append(
                    self._create_issue(
                        title="High code complexity detected",
                        description=f"Cyclomatic complexity of {complexity} exceeds recommended threshold of 10.",
                        severity=IssueSeverity.HIGH if complexity > 20 else IssueSeverity.MEDIUM,
                        category="complexity",
                        recommendations=[
                            "Break down complex functions into smaller units",
                            "Extract conditional logic into separate functions",
                            "Consider using strategy or state patterns",
                        ],
                        confidence=0.95,
                    )
                )

        # Check for duplicate code
        if "duplication" in metrics:
            duplication_pct = metrics["duplication"]
            if duplication_pct > 5:
                issues.append(
                    self._create_issue(
                        title="Code duplication detected",
                        description=f"{duplication_pct}% of code is duplicated.",
                        severity=IssueSeverity.MEDIUM,
                        category="duplication",
                        recommendations=[
                            "Extract common code into reusable functions",
                            "Consider inheritance or composition patterns",
                            "Create utility modules for shared functionality",
                        ],
                        confidence=0.90,
                    )
                )

        return issues

    async def _check_antipatterns(self, patterns: list[str]) -> list[Issue]:
        """Check for known anti-patterns."""
        issues = []

        antipattern_checks = {
            "god_object": {
                "title": "God Object anti-pattern detected",
                "description": "Class has too many responsibilities and dependencies.",
                "severity": IssueSeverity.HIGH,
                "recommendations": [
                    "Apply Single Responsibility Principle",
                    "Extract cohesive groups of methods into new classes",
                    "Use composition over inheritance",
                ],
            },
            "magic_numbers": {
                "title": "Magic numbers in code",
                "description": "Hard-coded numeric values without context.",
                "severity": IssueSeverity.LOW,
                "recommendations": [
                    "Define named constants",
                    "Use configuration files for values",
                    "Add comments explaining numeric values",
                ],
            },
            "deep_nesting": {
                "title": "Deep nesting detected",
                "description": "Code has excessive nesting levels reducing readability.",
                "severity": IssueSeverity.MEDIUM,
                "recommendations": [
                    "Use early returns to reduce nesting",
                    "Extract nested blocks into separate functions",
                    "Apply guard clauses",
                ],
            },
        }

        for pattern in patterns:
            if pattern in antipattern_checks:
                check = antipattern_checks[pattern]
                issues.append(
                    self._create_issue(
                        title=check["title"],
                        description=check["description"],
                        severity=check["severity"],
                        category="antipattern",
                        recommendations=check["recommendations"],
                        confidence=0.80,
                    )
                )

        return issues
