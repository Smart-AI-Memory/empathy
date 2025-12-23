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
import os
import re
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier

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
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        self._load_debt_history()

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the model name for a given tier."""
        provider = ModelProvider.ANTHROPIC
        return PROVIDER_MODELS.get(provider, {}).get(tier, "claude-sonnet-4-20250514")

    async def _call_llm(
        self, tier: ModelTier, system: str, user_message: str, max_tokens: int = 4096
    ) -> tuple[str, int, int]:
        """Make an actual LLM call using the Anthropic API."""
        client = self._get_client()
        if not client:
            return (
                "[Simulated - set ANTHROPIC_API_KEY for real results]",
                len(user_message) // 4,
                100,
            )

        model = self._get_model_for_tier(tier)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            return f"Error calling LLM: {e}", 0, 0

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
        Generate prioritized refactoring roadmap using LLM.

        Creates actionable refactoring plan based on priorities.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        high_priority = input_data.get("high_priority", [])
        medium_priority = input_data.get("medium_priority", [])
        analysis = input_data.get("analysis", {})
        target = input_data.get("target", "")

        # Build high priority summary for LLM
        high_summary = []
        for item in high_priority[:15]:
            high_summary.append(
                f"- {item.get('file')}:{item.get('line')} [{item.get('marker')}] "
                f"{item.get('message', '')[:50]}"
            )

        # Build input payload for prompt
        input_payload = f"""Target: {target or 'codebase'}

Total Debt Items: {input_data.get('total_debt', 0)}
Trajectory: {analysis.get('trajectory', 'unknown')}
Velocity: {analysis.get('velocity', 0)} items/snapshot

High Priority Items ({len(high_priority)}):
{chr(10).join(high_summary) if high_summary else 'None'}

Medium Priority Items: {len(medium_priority)}
Hotspot Files: {json.dumps([h.get('file') for h in analysis.get('hotspots', [])[:5]], indent=2)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="software architect specializing in technical debt management",
                goal="Generate a prioritized refactoring roadmap to reduce technical debt",
                instructions=[
                    "Analyze the debt trajectory and identify root causes",
                    "Create a phased roadmap with clear milestones",
                    "Prioritize items by impact and effort",
                    "Provide specific refactoring strategies for each phase",
                    "Include prevention measures to stop new debt accumulation",
                ],
                constraints=[
                    "Be specific about which files to refactor",
                    "Include effort estimates (high/medium/low)",
                    "Focus on sustainable debt reduction",
                ],
                input_type="tech_debt_analysis",
                input_payload=input_payload,
                extra={
                    "total_debt": input_data.get("total_debt", 0),
                    "trajectory": analysis.get("trajectory", "unknown"),
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a software architect specializing in technical debt management.
Create a prioritized refactoring roadmap based on the debt analysis.

For each phase:
1. Define clear goals and milestones
2. Prioritize by impact and effort
3. Provide specific refactoring strategies
4. Include prevention measures

Be specific and actionable."""

            user_message = f"""Generate a refactoring roadmap for this tech debt:

{input_payload}

Create a phased approach to reduce debt sustainably."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=3000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        # Summary
        summary = {
            "total_debt": input_data.get("total_debt", 0),
            "trajectory": analysis.get("trajectory", "unknown"),
            "high_priority_count": len(high_priority),
        }

        result = {
            "refactoring_plan": response,
            "summary": summary,
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "plan_summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )

        return (
            result,
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
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        summary = result.final_output.get("summary", {})
        print(f"Total Debt: {summary.get('total_debt', 0)} items")
        print(f"Trajectory: {summary.get('trajectory', 'N/A')}")
        print(f"High Priority: {summary.get('high_priority_count', 0)}")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
