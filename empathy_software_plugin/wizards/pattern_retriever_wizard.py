"""Pattern Retriever Wizard

Retrieves relevant patterns from storage based on context.
Level 3 (Proactive) - anticipates pattern needs.

Example Usage:
    from empathy_software_plugin.wizards import PatternRetrieverWizard

    wizard = PatternRetrieverWizard()
    result = await wizard.analyze({
        "query": "null reference",
        "pattern_type": "debugging",
        "limit": 5
    })

    for pattern in result["matching_patterns"]:
        print(f"{pattern['id']}: {pattern['relevance_score']:.0%}")

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


class PatternRetrieverWizard(BaseWizard):
    """Pattern Retriever Wizard - Level 3 (Proactive)

    Retrieves relevant patterns from storage for given context.
    Searches across bug patterns, security decisions, and tech debt history.

    Features:
    - Full-text search across all pattern types
    - Relevance ranking
    - Type and classification filtering
    - Pattern metadata enrichment
    """

    @property
    def name(self) -> str:
        return "Pattern Retriever Wizard"

    @property
    def level(self) -> int:
        return 3  # Proactive - anticipates pattern needs

    def __init__(
        self,
        pattern_storage_path: str = "./patterns",
        **kwargs,
    ):
        """Initialize Pattern Retriever Wizard.

        Args:
            pattern_storage_path: Path to patterns directory
            **kwargs: Passed to BaseWizard

        """
        super().__init__(**kwargs)
        self.pattern_storage_path = Path(pattern_storage_path)
        self.pattern_storage_path.mkdir(parents=True, exist_ok=True)

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Retrieve relevant patterns for given context.

        Args:
            context: Dictionary with:
                - query: Search query string
                - pattern_type: Optional filter (debugging, security, tech_debt)
                - limit: Max results (default 10)
                - include_metadata: Include full pattern data (default True)

        Returns:
            Dictionary with:
                - query: Original query
                - matching_patterns: List of matching patterns with relevance
                - summary: Count and distribution stats
                - predictions: Level 3 predictions
                - recommendations: Usage recommendations
                - confidence: Retrieval confidence

        """
        query = context.get("query", "")
        pattern_type = context.get("pattern_type")
        limit = context.get("limit", 10)
        include_metadata = context.get("include_metadata", True)

        # Load all patterns
        all_patterns = self._load_all_patterns()

        # Filter by type if specified
        if pattern_type:
            all_patterns = [p for p in all_patterns if p.get("_type") == pattern_type]

        # Search and rank
        if query:
            matching = self._search_patterns(query, all_patterns)
            ranked = self._rank_by_relevance(query, matching)
        else:
            ranked = all_patterns

        # Limit results
        limited = ranked[:limit]

        # Generate predictions and recommendations
        predictions = self._generate_predictions(limited, context)
        recommendations = self._generate_recommendations(limited, query)

        # Format output
        formatted_patterns = []
        for p in limited:
            formatted = {
                "id": p.get("_id", "unknown"),
                "type": p.get("_type", "unknown"),
                "relevance_score": p.get("_relevance_score", 0.0),
                "summary": p.get("_summary", ""),
            }
            if include_metadata:
                formatted["data"] = {k: v for k, v in p.items() if not k.startswith("_")}
            formatted_patterns.append(formatted)

        return {
            "query": query,
            "matching_patterns": formatted_patterns,
            "summary": {
                "total_available": len(all_patterns),
                "total_matched": len(ranked),
                "returned": len(limited),
                "by_type": self._count_by_type(ranked),
            },
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(limited, query),
            "metadata": {
                "wizard": self.name,
                "level": self.level,
                "timestamp": datetime.now().isoformat(),
            },
        }

    def _load_all_patterns(self) -> list[dict[str, Any]]:
        """Load all patterns from storage."""
        patterns = []

        # Load bug patterns
        for bug_dir in ["debugging", "debugging_demo", "repo_test/debugging"]:
            dir_path = self.pattern_storage_path / bug_dir
            if not dir_path.exists():
                continue

            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        data["_type"] = "debugging"
                        data["_id"] = data.get("bug_id", json_file.stem)
                        # fmt: off
                        data["_summary"] = (
                            f"{data.get('error_type', 'unknown')}: {data.get('root_cause', 'N/A')}"
                        )
                        # fmt: on
                        patterns.append(data)
                except (json.JSONDecodeError, OSError):
                    pass

        # Load security decisions
        for sec_dir in ["security", "security_demo", "repo_test/security"]:
            decisions_file = self.pattern_storage_path / sec_dir / "team_decisions.json"
            if not decisions_file.exists():
                continue

            try:
                with open(decisions_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for decision in data.get("decisions", []):
                        decision["_type"] = "security"
                        decision["_id"] = f"sec_{decision.get('finding_hash', 'unknown')}"
                        # fmt: off
                        decision["_summary"] = (
                            f"{decision.get('finding_hash', 'unknown')}: {decision.get('decision', 'N/A')}"
                        )
                        # fmt: on
                        patterns.append(decision)
            except (json.JSONDecodeError, OSError):
                pass

        # Load tech debt snapshots
        for debt_dir in ["tech_debt", "tech_debt_demo", "repo_test/tech_debt"]:
            history_file = self.pattern_storage_path / debt_dir / "debt_history.json"
            if not history_file.exists():
                continue

            try:
                with open(history_file, encoding="utf-8") as f:
                    data = json.load(f)
                    # Only include most recent snapshot as a pattern
                    snapshots = data.get("snapshots", [])
                    if snapshots:
                        latest = max(snapshots, key=lambda s: s.get("date", ""))
                        latest["_type"] = "tech_debt"
                        latest["_id"] = f"debt_{latest.get('date', 'latest')[:10]}"
                        # fmt: off
                        latest["_summary"] = (
                            f"{latest.get('total_items', 0)} items, hotspots: {', '.join(latest.get('hotspots', [])[:2])}"
                        )
                        # fmt: on
                        patterns.append(latest)
            except (json.JSONDecodeError, OSError):
                pass

        return patterns

    def _search_patterns(self, query: str, patterns: list[dict]) -> list[dict]:
        """Search patterns by query text."""
        query_lower = query.lower()
        results = []

        for pattern in patterns:
            # Search across all string fields
            searchable_text = self._extract_searchable_text(pattern)

            if query_lower in searchable_text.lower():
                results.append(pattern)

        return results

    def _extract_searchable_text(self, pattern: dict) -> str:
        """Extract searchable text from a pattern."""
        parts = []

        # Common fields to search
        search_fields = [
            "error_type",
            "error_message",
            "root_cause",
            "fix_applied",
            "finding_hash",
            "decision",
            "reason",
            "hotspots",
            "_summary",
        ]

        for field in search_fields:
            value = pattern.get(field)
            if isinstance(value, str):
                parts.append(value)
            elif isinstance(value, list):
                parts.extend(str(v) for v in value)

        return " ".join(parts)

    def _rank_by_relevance(self, query: str, patterns: list[dict]) -> list[dict]:
        """Rank patterns by relevance to query."""
        query_lower = query.lower()
        query_terms = query_lower.split()

        for pattern in patterns:
            score = 0.0
            searchable = self._extract_searchable_text(pattern).lower()

            # Exact phrase match
            if query_lower in searchable:
                score += 0.5

            # Term matches
            for term in query_terms:
                if term in searchable:
                    score += 0.2

            # Type-specific boosts
            if pattern.get("_type") == "debugging" and any(
                t in query_lower for t in ["bug", "error", "fix"]
            ):
                score += 0.1
            if pattern.get("_type") == "security" and any(
                t in query_lower for t in ["security", "vulnerability"]
            ):
                score += 0.1

            pattern["_relevance_score"] = min(score, 1.0)

        # Sort by relevance
        return sorted(patterns, key=lambda p: p.get("_relevance_score", 0), reverse=True)

    def _count_by_type(self, patterns: list[dict]) -> dict[str, int]:
        """Count patterns by type."""
        counts: dict[str, int] = {}
        for p in patterns:
            pt = p.get("_type", "unknown")
            counts[pt] = counts.get(pt, 0) + 1
        return counts

    def _calculate_confidence(self, patterns: list[dict], query: str) -> float:
        """Calculate confidence in retrieval results."""
        if not patterns:
            return 0.3

        if not query:
            return 0.5

        # Average relevance score
        avg_relevance = sum(p.get("_relevance_score", 0) for p in patterns) / len(patterns)

        # Boost if high relevance matches
        if patterns and patterns[0].get("_relevance_score", 0) > 0.7:
            avg_relevance += 0.2

        return float(min(avg_relevance + 0.3, 1.0))

    def _generate_predictions(self, patterns: list[dict], context: dict) -> list[dict]:
        """Generate Level 3 predictions about pattern utility."""
        predictions = []

        if not patterns:
            predictions.append(
                {
                    "type": "no_matches",
                    "severity": "info",
                    "description": f"No patterns match query '{context.get('query')}'. Consider storing relevant patterns.",
                },
            )
            return predictions

        # Check for low relevance
        if patterns and patterns[0].get("_relevance_score", 0) < 0.4:
            predictions.append(
                {
                    "type": "low_relevance",
                    "severity": "info",
                    "description": "Top results have low relevance. Consider refining your query.",
                },
            )

        # Check pattern age (if dates available)
        for p in patterns[:3]:
            if "date" in p:
                try:
                    pattern_date = datetime.fromisoformat(p["date"].replace("Z", "+00:00"))
                    age_days = (datetime.now(pattern_date.tzinfo) - pattern_date).days
                    if age_days > 90:
                        predictions.append(
                            {
                                "type": "stale_pattern",
                                "severity": "warning",
                                "description": f"Pattern '{p.get('_id')}' is {age_days} days old. Verify it's still relevant.",
                            },
                        )
                        break
                except (ValueError, TypeError):
                    pass

        return predictions

    def _generate_recommendations(self, patterns: list[dict], query: str) -> list[str]:
        """Generate recommendations for using patterns."""
        recommendations = []

        if not patterns:
            recommendations.append("No patterns found. Run the relevant wizard to store patterns.")
            return recommendations

        recommendations.append(f"Found {len(patterns)} relevant pattern(s)")

        # Recommend based on top match type
        top_type = patterns[0].get("_type") if patterns else None

        if top_type == "debugging":
            recommendations.append("Review bug fixes before implementing similar code")
        elif top_type == "security":
            recommendations.append("Check if security finding matches team decisions")
        elif top_type == "tech_debt":
            recommendations.append("Consider debt hotspots when planning changes")

        return recommendations


# CLI support
if __name__ == "__main__":
    import asyncio

    async def main():
        wizard = PatternRetrieverWizard()
        result = await wizard.analyze(
            {
                "query": "null reference",
                "limit": 5,
            },
        )
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(main())
