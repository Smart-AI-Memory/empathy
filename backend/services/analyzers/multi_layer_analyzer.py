"""Multi-Layer Analyzer - Orchestrates analysis across different empathy levels.
"""

import asyncio
from typing import Any

from .base_analyzer import Issue
from .layer3_ai import AIAnalyzer


class MultiLayerAnalyzer:
    """Orchestrates analysis across multiple empathy levels.
    Combines results from different analyzers to provide comprehensive insights.
    """

    def __init__(self):
        self.analyzers = []
        self._initialize_analyzers()

    def _initialize_analyzers(self):
        """Initialize all available analyzers."""
        # Level 3: AI Proactive Analyzer
        self.analyzers.append(AIAnalyzer())

        # Additional analyzers can be added here
        # Level 4 and 5 analyzers would go here

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Perform multi-layer analysis.

        Args:
            context: Analysis context with code, metrics, and other data

        Returns:
            Dictionary containing:
                - issues: List of all detected issues
                - summary: Analysis summary
                - level_results: Results grouped by empathy level

        """
        all_issues = []
        level_results = {}

        # Run all analyzers concurrently
        tasks = []
        for analyzer in self.analyzers:
            tasks.append(self._run_analyzer(analyzer, context))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for analyzer, result in zip(self.analyzers, results, strict=False):
            if isinstance(result, Exception):
                # Log error but continue
                print(f"Error in {analyzer.name}: {result!s}")
                continue

            level_results[f"level_{analyzer.level}"] = {
                "analyzer": analyzer.name,
                "issues": [issue.to_dict() for issue in result],
                "count": len(result),
            }
            all_issues.extend(result)

        # Generate summary
        summary = self._generate_summary(all_issues)

        return {
            "issues": [issue.to_dict() for issue in all_issues],
            "summary": summary,
            "level_results": level_results,
            "total_issues": len(all_issues),
        }

    async def _run_analyzer(self, analyzer, context: dict[str, Any]) -> list[Issue]:
        """Run a single analyzer."""
        try:
            return await analyzer.analyze(context)
        except Exception as e:
            print(f"Analyzer {analyzer.name} failed: {e!s}")
            return []

    def _generate_summary(self, issues: list[Issue]) -> dict[str, Any]:
        """Generate analysis summary."""
        if not issues:
            return {"total": 0, "by_severity": {}, "by_category": {}, "top_recommendations": []}

        # Count by severity
        severity_counts = {}
        for issue in issues:
            severity = issue.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        # Count by category
        category_counts = {}
        for issue in issues:
            if issue.category:
                category_counts[issue.category] = category_counts.get(issue.category, 0) + 1

        # Get top recommendations
        all_recommendations = []
        for issue in issues:
            all_recommendations.extend(issue.recommendations)

        # Get unique recommendations with counts
        rec_counts = {}
        for rec in all_recommendations:
            rec_counts[rec] = rec_counts.get(rec, 0) + 1

        top_recommendations = sorted(rec_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total": len(issues),
            "by_severity": severity_counts,
            "by_category": category_counts,
            "top_recommendations": [rec for rec, _ in top_recommendations],
            "average_confidence": sum(i.confidence for i in issues) / len(issues) if issues else 0,
        }
