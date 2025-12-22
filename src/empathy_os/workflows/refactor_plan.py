"""
Refactor Planning Workflow

Prioritizes tech debt based on trajectory analysis and impact assessment.
Uses historical tech debt data to identify trends and hotspots.

Stages:
1. scan (CHEAP) - Scan for TODOs, FIXMEs, HACKs, complexity
2. analyze (CAPABLE) - Analyze debt trajectory from patterns
3. prioritize (CAPABLE) - Score by impact, effort, and risk
4. plan (PREMIUM) - Generate prioritized refactoring roadmap (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import re
from pathlib import Path
from typing import Any

from .base import BaseWorkflow, ModelTier

# Debt markers and their severity
DEBT_MARKERS = {
    "TODO": {"severity": "low", "weight": 1},
    "FIXME": {"severity": "medium", "weight": 3},
    "HACK": {"severity": "high", "weight": 5},
    "XXX": {"severity": "medium", "weight": 3},
    "BUG": {"severity": "high", "weight": 5},
    "OPTIMIZE": {"severity": "low", "weight": 2},
    "REFACTOR": {"severity": "medium", "weight": 3},
}


class RefactorPlanWorkflow(BaseWorkflow):
    """
    Prioritize tech debt with trajectory analysis.

    Analyzes tech debt trends over time to identify growing
    problem areas and generate prioritized refactoring plans.
    """

    name = "refactor-plan"
    description = "Prioritize tech debt based on trajectory and impact"
    stages = ["scan", "analyze", "prioritize", "plan"]
    tier_map = {
        "scan": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "prioritize": ModelTier.CAPABLE,
        "plan": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        patterns_dir: str = "./patterns",
        min_debt_for_premium: int = 50,
        **kwargs: Any,
    ):
        """
        Initialize refactor planning workflow.

        Args:
            patterns_dir: Directory containing tech debt history
            min_debt_for_premium: Minimum debt items to use premium planning
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.patterns_dir = patterns_dir
        self.min_debt_for_premium = min_debt_for_premium
        self._total_debt: int = 0
        self._debt_history: list[dict] = []
        self._load_debt_history()

    def _load_debt_history(self) -> None:
        """Load tech debt history from pattern library."""
        debt_file = Path(self.patterns_dir) / "tech_debt.json"
        if debt_file.exists():
            try:
                with open(debt_file) as f:
                    data = json.load(f)
                    self._debt_history = data.get("snapshots", [])
            except (json.JSONDecodeError, OSError):
                pass

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Downgrade plan stage if debt is low.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "plan":
            if self._total_debt < self.min_debt_for_premium:
                self.tier_map["plan"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "scan":
            return await self._scan(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "prioritize":
            return await self._prioritize(input_data, tier)
        elif stage_name == "plan":
            return await self._plan(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _scan(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Scan codebase for tech debt markers.

        Finds TODOs, FIXMEs, HACKs and other debt indicators.
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py", ".ts", ".tsx", ".js"])

        debt_items: list[dict] = []
        files_scanned = 0

        target = Path(target_path)
        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    if any(
                        skip in str(file_path)
                        for skip in [".git", "node_modules", "__pycache__", "venv"]
                    ):
                        continue

                    try:
                        content = file_path.read_text(errors="ignore")
                        files_scanned += 1

                        for marker, info in DEBT_MARKERS.items():
                            pattern = rf"#\s*{marker}[:\s]*(.*?)(?:\n|$)"
                            for match in re.finditer(pattern, content, re.IGNORECASE):
                                line_num = content[: match.start()].count("\n") + 1
                                debt_items.append(
                                    {
                                        "file": str(file_path),
                                        "line": line_num,
                                        "marker": marker,
                                        "message": match.group(1).strip()[:100],
                                        "severity": info["severity"],
                                        "weight": info["weight"],
                                    }
                                )
                    except OSError:
                        continue

        self._total_debt = len(debt_items)

        # Group by file
        by_file: dict[str, int] = {}
        for item in debt_items:
            f = item["file"]
            by_file[f] = by_file.get(f, 0) + 1

        # By marker type
        by_marker: dict[str, int] = {}
        for item in debt_items:
            m = item["marker"]
            by_marker[m] = by_marker.get(m, 0) + 1

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(debt_items)) // 4

        return (
            {
                "debt_items": debt_items,
                "total_debt": self._total_debt,
                "files_scanned": files_scanned,
                "by_file": dict(sorted(by_file.items(), key=lambda x: -x[1])[:20]),
                "by_marker": by_marker,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Analyze debt trajectory from historical data.

        Compares current debt with historical snapshots to
        identify trends and growing problem areas.
        """
        current_total = input_data.get("total_debt", 0)
        by_file = input_data.get("by_file", {})

        # Analyze trajectory
        trajectory = "stable"
        velocity = 0.0

        if self._debt_history and len(self._debt_history) >= 2:
            oldest = self._debt_history[0].get("total_items", 0)
            newest = self._debt_history[-1].get("total_items", 0)

            change = newest - oldest
            if change > 10:
                trajectory = "increasing"
            elif change < -10:
                trajectory = "decreasing"

            # Calculate velocity (items per snapshot)
            velocity = change / len(self._debt_history)

        # Identify hotspots (files with most debt and increasing)
        hotspots: list[dict] = []
        for file_path, count in list(by_file.items())[:10]:
            hotspots.append(
                {
                    "file": file_path,
                    "debt_count": count,
                    "trend": "stable",  # Would compare with history
                }
            )

        analysis = {
            "trajectory": trajectory,
            "velocity": round(velocity, 2),
            "current_total": current_total,
            "historical_snapshots": len(self._debt_history),
            "hotspots": hotspots,
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(analysis)) // 4

        return (
            {
                "analysis": analysis,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _prioritize(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Score debt items by impact, effort, and risk.

        Calculates priority scores considering multiple factors.
        """
        debt_items = input_data.get("debt_items", [])
        analysis = input_data.get("analysis", {})
        hotspots = {h["file"] for h in analysis.get("hotspots", [])}

        prioritized: list[dict] = []
        for item in debt_items:
            # Calculate priority score
            base_weight = item.get("weight", 1)

            # Bonus for hotspot files
            hotspot_bonus = 2 if item["file"] in hotspots else 0

            # Severity factor
            severity_factor = {
                "high": 3,
                "medium": 2,
                "low": 1,
            }.get(item.get("severity", "low"), 1)

            priority_score = (base_weight * severity_factor) + hotspot_bonus

            prioritized.append(
                {
                    **item,
                    "priority_score": priority_score,
                    "is_hotspot": item["file"] in hotspots,
                }
            )

        # Sort by priority
        prioritized.sort(key=lambda x: -x["priority_score"])

        # Group into priority tiers
        high_priority = [p for p in prioritized if p["priority_score"] >= 10]
        medium_priority = [p for p in prioritized if 5 <= p["priority_score"] < 10]
        low_priority = [p for p in prioritized if p["priority_score"] < 5]

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(prioritized)) // 4

        return (
            {
                "prioritized_items": prioritized[:50],  # Top 50
                "high_priority": high_priority[:20],
                "medium_priority": medium_priority[:20],
                "low_priority_count": len(low_priority),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _plan(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate prioritized refactoring roadmap.

        Creates actionable refactoring plan based on priorities.
        """
        high_priority = input_data.get("high_priority", [])
        medium_priority = input_data.get("medium_priority", [])
        analysis = input_data.get("analysis", {})

        # Generate roadmap phases
        roadmap: list[dict] = []

        # Phase 1: Critical items
        if high_priority:
            phase1_files = list({item["file"] for item in high_priority[:10]})
            roadmap.append(
                {
                    "phase": 1,
                    "name": "Critical Debt Reduction",
                    "description": "Address highest priority tech debt items",
                    "files": phase1_files,
                    "item_count": len(high_priority),
                    "estimated_effort": "high",
                }
            )

        # Phase 2: Medium priority
        if medium_priority:
            phase2_files = list({item["file"] for item in medium_priority[:10]})
            roadmap.append(
                {
                    "phase": 2,
                    "name": "Debt Stabilization",
                    "description": "Address medium priority items to prevent escalation",
                    "files": phase2_files,
                    "item_count": len(medium_priority),
                    "estimated_effort": "medium",
                }
            )

        # Phase 3: Ongoing maintenance
        roadmap.append(
            {
                "phase": 3,
                "name": "Continuous Improvement",
                "description": "Address remaining items and prevent new debt",
                "recommendations": [
                    "Add pre-commit hooks to catch new TODOs",
                    "Review debt metrics weekly",
                    "Allocate 10% of sprint capacity to debt reduction",
                ],
            }
        )

        # Summary
        summary = {
            "total_debt": input_data.get("total_debt", 0),
            "trajectory": analysis.get("trajectory", "unknown"),
            "high_priority_count": len(high_priority),
            "phases": len(roadmap),
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(roadmap)) // 4

        return (
            {
                "roadmap": roadmap,
                "summary": summary,
                "model_tier_used": tier.value,
            },
            input_tokens,
            output_tokens,
        )


def main():
    """CLI entry point for refactor planning workflow."""
    import asyncio

    async def run():
        workflow = RefactorPlanWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nRefactor Plan Results")
        print("=" * 50)
        print(f"Success: {result.success}")

        summary = result.final_output.get("summary", {})
        print(f"Total Debt: {summary.get('total_debt', 0)} items")
        print(f"Trajectory: {summary.get('trajectory', 'N/A')}")
        print(f"High Priority: {summary.get('high_priority_count', 0)}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        print(
            f"  Savings: ${result.cost_report.savings:.4f} ({result.cost_report.savings_percent:.1f}%)"
        )

    asyncio.run(run())


if __name__ == "__main__":
    main()
