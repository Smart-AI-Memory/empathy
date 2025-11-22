"""
Shared Learning System for Coach Wizards

Enables wizards to learn from each other's patterns and improve over time.
Implements multi-agent learning using the Empathy Framework's PatternLibrary.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from empathy_os import Pattern, PatternLibrary


@dataclass
class WizardInsight:
    """Insight learned by a wizard"""

    wizard_name: str
    insight_type: str  # "success_pattern", "failure_pattern", "optimization"
    description: str
    context: dict[str, Any]
    confidence: float
    timestamp: datetime = field(default_factory=datetime.now)
    usage_count: int = 0
    success_rate: float = 0.0


class SharedLearningSystem:
    """
    Multi-agent learning system for Coach wizards

    Wizards contribute patterns and insights that other wizards can learn from.
    Uses Empathy Framework's PatternLibrary for storage and retrieval.
    """

    def __init__(self):
        """Initialize shared learning system"""
        self.pattern_library = PatternLibrary()
        self.insights: dict[str, list[WizardInsight]] = {}
        self.wizard_collaborations: dict[str, int] = {}  # Track wizard-to-wizard learning

    def contribute_pattern(
        self,
        wizard_name: str,
        pattern_type: str,
        description: str,
        code: str,
        tags: list[str],
        context: dict[str, Any] | None = None,
    ) -> Pattern:
        """
        Wizard contributes a learned pattern

        Args:
            wizard_name: Name of contributing wizard
            pattern_type: Type of pattern (debugging, testing, etc.)
            description: Pattern description
            code: Code or template for the pattern
            tags: Tags for categorization
            context: Additional context

        Returns:
            Created Pattern object
        """
        pattern = Pattern(
            id=f"{wizard_name}_{pattern_type}_{datetime.now().timestamp()}",
            agent_id=wizard_name,
            pattern_type=pattern_type,
            name=f"{wizard_name} {pattern_type} pattern",
            description=description,
            context=context or {},
            code=code,
            tags=tags,
        )

        self.pattern_library.contribute_pattern(wizard_name, pattern)

        return pattern

    def query_patterns(
        self,
        pattern_type: str | None = None,
        tags: list[str] | None = None,
        min_confidence: float = 0.5,
    ) -> list[Pattern]:
        """
        Query patterns from the shared library

        Args:
            pattern_type: Filter by pattern type
            tags: Filter by tags
            min_confidence: Minimum confidence threshold

        Returns:
            List of matching patterns
        """
        # Manual filtering since PatternLibrary.query_patterns has different signature
        results = []

        for _pattern_id, pattern in self.pattern_library.patterns.items():
            # Filter by confidence
            if pattern.confidence < min_confidence:
                continue

            # Filter by pattern_type
            if pattern_type and pattern.pattern_type != pattern_type:
                continue

            # Filter by tags
            if tags:
                if not any(tag in pattern.tags for tag in tags):
                    continue

            results.append(pattern)

        return results

    def record_insight(self, wizard_name: str, insight: WizardInsight):
        """
        Record an insight from a wizard

        Args:
            wizard_name: Name of wizard
            insight: WizardInsight object
        """
        if wizard_name not in self.insights:
            self.insights[wizard_name] = []

        self.insights[wizard_name].append(insight)

    def get_insights_for_wizard(
        self, wizard_name: str, insight_type: str | None = None
    ) -> list[WizardInsight]:
        """
        Get insights relevant to a wizard

        Args:
            wizard_name: Name of wizard
            insight_type: Filter by insight type

        Returns:
            List of relevant insights
        """
        all_insights = []

        # Get insights from all wizards (cross-pollination)
        for insights in self.insights.values():
            if insight_type:
                all_insights.extend([i for i in insights if i.insight_type == insight_type])
            else:
                all_insights.extend(insights)

        # Sort by confidence and usage
        all_insights.sort(key=lambda x: (x.confidence, x.success_rate, x.usage_count), reverse=True)

        return all_insights

    def record_collaboration(self, wizard1: str, wizard2: str):
        """
        Record that two wizards collaborated on a task

        Args:
            wizard1: First wizard name
            wizard2: Second wizard name
        """
        key = f"{wizard1}->{wizard2}"
        self.wizard_collaborations[key] = self.wizard_collaborations.get(key, 0) + 1

    def get_collaboration_stats(self) -> dict[str, int]:
        """Get collaboration statistics between wizards"""
        return self.wizard_collaborations.copy()

    def get_top_patterns(self, limit: int = 10) -> list[Pattern]:
        """
        Get top patterns by usage and success rate

        Args:
            limit: Maximum number of patterns to return

        Returns:
            List of top patterns
        """
        all_patterns = []

        for _pattern_id, pattern in self.pattern_library.patterns.items():
            all_patterns.append(pattern)

        # Sort by success rate and usage
        all_patterns.sort(key=lambda p: (p.success_rate, p.usage_count, p.confidence), reverse=True)

        return all_patterns[:limit]

    def analyze_wizard_strengths(self) -> dict[str, dict[str, Any]]:
        """
        Analyze each wizard's strengths based on contributed patterns

        Returns:
            Dict mapping wizard names to strength analysis
        """
        analysis = {}

        for wizard_name, pattern_ids in self.pattern_library.agent_contributions.items():
            patterns = [self.pattern_library.patterns[pid] for pid in pattern_ids]

            if not patterns:
                continue

            avg_confidence = sum(p.confidence for p in patterns) / len(patterns)
            avg_success_rate = sum(p.success_rate for p in patterns) / len(patterns)
            total_usage = sum(p.usage_count for p in patterns)

            # Identify specialization (most common pattern type)
            pattern_types = {}
            for p in patterns:
                pattern_types[p.pattern_type] = pattern_types.get(p.pattern_type, 0) + 1

            specialization = (
                max(pattern_types.items(), key=lambda x: x[1])[0] if pattern_types else "general"
            )

            analysis[wizard_name] = {
                "total_patterns": len(patterns),
                "avg_confidence": avg_confidence,
                "avg_success_rate": avg_success_rate,
                "total_usage": total_usage,
                "specialization": specialization,
                "pattern_diversity": len(pattern_types),
            }

        return analysis

    def recommend_wizard_for_task(self, task_type: str) -> str | None:
        """
        Recommend which wizard is best for a task type based on learned patterns

        Args:
            task_type: Type of task

        Returns:
            Recommended wizard name or None
        """
        # Query patterns of this type
        patterns = self.query_patterns(pattern_type=task_type, min_confidence=0.6)

        if not patterns:
            return None

        # Count contributions by wizard
        wizard_contributions = {}
        for pattern in patterns:
            wizard_contributions[pattern.agent_id] = (
                wizard_contributions.get(pattern.agent_id, 0) + 1
            )

        # Return wizard with most high-quality contributions
        if wizard_contributions:
            return max(wizard_contributions.items(), key=lambda x: x[1])[0]

        return None

    def get_learning_summary(self) -> str:
        """Generate summary of shared learning"""
        total_patterns = len(self.pattern_library.patterns)
        total_wizards = len(self.pattern_library.agent_contributions)
        total_insights = sum(len(insights) for insights in self.insights.values())

        summary = f"""# Shared Learning System Summary

## Overview
- **Total Patterns**: {total_patterns}
- **Contributing Wizards**: {total_wizards}
- **Total Insights**: {total_insights}
- **Collaborations**: {len(self.wizard_collaborations)}

## Top Patterns
"""

        top_patterns = self.get_top_patterns(limit=5)
        for i, pattern in enumerate(top_patterns, 1):
            summary += f"{i}. **{pattern.name}** (by {pattern.agent_id})\n"
            summary += f"   - Success Rate: {pattern.success_rate:.1%}\n"
            summary += f"   - Usage: {pattern.usage_count} times\n"
            summary += f"   - Confidence: {pattern.confidence:.1%}\n\n"

        summary += "## Wizard Strengths\n"
        strengths = self.analyze_wizard_strengths()
        for wizard_name, stats in strengths.items():
            summary += f"- **{wizard_name}**: {stats['total_patterns']} patterns"
            summary += f" (specialization: {stats['specialization']},"
            summary += f" avg success: {stats['avg_success_rate']:.1%})\n"

        return summary


# Global shared learning system (singleton)
_shared_learning = None


def get_shared_learning() -> SharedLearningSystem:
    """Get or create global shared learning system"""
    global _shared_learning
    if _shared_learning is None:
        _shared_learning = SharedLearningSystem()
    return _shared_learning
