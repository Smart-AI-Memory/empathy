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
from .step_config import WorkflowStepConfig

# Define step configurations for executor-based execution
REFACTOR_PLAN_STEPS = {
    "plan": WorkflowStepConfig(
        name="plan",
        task_type="architectural_decision",  # Premium tier task
        tier_hint="premium",
        description="Generate prioritized refactoring roadmap",
        max_tokens=3000,
    ),
}

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

        # Group into priority tiers (single pass instead of 3 scans)
        high_priority: list[dict] = []
        medium_priority: list[dict] = []
        low_priority: list[dict] = []
        for p in prioritized:
            score = p["priority_score"]
            if score >= 10:
                high_priority.append(p)
            elif score >= 5:
                medium_priority.append(p)
            else:
                low_priority.append(p)

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
        input_payload = f"""Target: {target or "codebase"}

Total Debt Items: {input_data.get("total_debt", 0)}
Trajectory: {analysis.get("trajectory", "unknown")}
Velocity: {analysis.get("velocity", 0)} items/snapshot

High Priority Items ({len(high_priority)}):
{chr(10).join(high_summary) if high_summary else "None"}

Medium Priority Items: {len(medium_priority)}
Hotspot Files: {json.dumps([h.get("file") for h in analysis.get("hotspots", [])[:5]], indent=2)}"""

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

        # Try executor-based execution first (Phase 3 pattern)
        if self._executor is not None or self._api_key:
            try:
                step = REFACTOR_PLAN_STEPS["plan"]
                response, input_tokens, output_tokens, cost = await self.run_step_with_executor(
                    step=step,
                    prompt=user_message,
                    system=system,
                )
            except Exception:
                # Fall back to legacy _call_llm if executor fails
                response, input_tokens, output_tokens = await self._call_llm(
                    tier, system or "", user_message, max_tokens=3000
                )
        else:
            # Legacy path for backward compatibility
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

        result: dict = {
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

        # Add formatted report for human readability
        result["formatted_report"] = format_refactor_plan_report(result, input_data)

        return (
            result,
            input_tokens,
            output_tokens,
        )


def format_refactor_plan_report(result: dict, input_data: dict) -> str:
    """
    Format refactor plan output as a human-readable report.

    Args:
        result: The plan stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string
    """
    lines = []

    # Header with trajectory
    summary = result.get("summary", {})
    total_debt = summary.get("total_debt", 0)
    trajectory = summary.get("trajectory", "unknown")
    high_priority_count = summary.get("high_priority_count", 0)

    # Trajectory icon
    if trajectory == "increasing":
        traj_icon = "📈"
        traj_text = "INCREASING"
    elif trajectory == "decreasing":
        traj_icon = "📉"
        traj_text = "DECREASING"
    else:
        traj_icon = "➡️"
        traj_text = "STABLE"

    lines.append("=" * 60)
    lines.append("REFACTOR PLAN REPORT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Total Tech Debt Items: {total_debt}")
    lines.append(f"Trajectory: {traj_icon} {traj_text}")
    lines.append(f"High Priority Items: {high_priority_count}")
    lines.append("")

    # Scan summary
    by_marker: dict[str, int] = input_data.get("by_marker", {})
    files_scanned = input_data.get("files_scanned", 0)

    lines.append("-" * 60)
    lines.append("DEBT SCAN SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Files Scanned: {files_scanned}")
    if by_marker:
        lines.append("By Marker Type:")
        for marker, count in sorted(by_marker.items(), key=lambda x: -x[1]):
            marker_info = DEBT_MARKERS.get(marker, {"severity": "low", "weight": 1})
            severity = str(marker_info.get("severity", "low"))
            sev_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(severity, "⚪")
            lines.append(f"  {sev_icon} {marker}: {count}")
    lines.append("")

    # Analysis
    analysis = input_data.get("analysis", {})
    if analysis:
        lines.append("-" * 60)
        lines.append("TRAJECTORY ANALYSIS")
        lines.append("-" * 60)
        velocity = analysis.get("velocity", 0)
        snapshots = analysis.get("historical_snapshots", 0)

        lines.append(f"Historical Snapshots: {snapshots}")
        if velocity != 0:
            velocity_text = f"+{velocity}" if velocity > 0 else str(velocity)
            lines.append(f"Velocity: {velocity_text} items/snapshot")
        lines.append("")

    # Hotspots
    hotspots = analysis.get("hotspots", [])
    if hotspots:
        lines.append("-" * 60)
        lines.append("🔥 HOTSPOT FILES")
        lines.append("-" * 60)
        for h in hotspots[:10]:
            file_path = h.get("file", "unknown")
            debt_count = h.get("debt_count", 0)
            lines.append(f"  • {file_path}")
            lines.append(f"      {debt_count} debt items")
        lines.append("")

    # High priority items
    high_priority = input_data.get("high_priority", [])
    if high_priority:
        lines.append("-" * 60)
        lines.append("🔴 HIGH PRIORITY ITEMS")
        lines.append("-" * 60)
        for item in high_priority[:10]:
            file_path = item.get("file", "unknown")
            line = item.get("line", "?")
            marker = item.get("marker", "DEBT")
            message = item.get("message", "")[:50]
            score = item.get("priority_score", 0)
            hotspot = "🔥" if item.get("is_hotspot") else ""
            lines.append(f"  [{marker}] {file_path}:{line} {hotspot}")
            lines.append(f"      {message} (score: {score})")
        if len(high_priority) > 10:
            lines.append(f"  ... and {len(high_priority) - 10} more")
        lines.append("")

    # Refactoring plan from LLM
    refactoring_plan = result.get("refactoring_plan", "")
    if refactoring_plan and not refactoring_plan.startswith("[Simulated"):
        lines.append("-" * 60)
        lines.append("REFACTORING ROADMAP")
        lines.append("-" * 60)
        if len(refactoring_plan) > 2000:
            lines.append(refactoring_plan[:2000] + "...")
        else:
            lines.append(refactoring_plan)
        lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Analyzed {total_debt} debt items using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)


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
