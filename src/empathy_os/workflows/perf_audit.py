"""
Performance Audit Workflow

Identifies performance bottlenecks and optimization opportunities
through static analysis.

Stages:
1. profile (CHEAP) - Static analysis for common perf anti-patterns
2. analyze (CAPABLE) - Deep analysis of algorithmic complexity
3. hotspots (CAPABLE) - Identify performance hotspots
4. optimize (PREMIUM) - Generate optimization recommendations (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
import re
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier

# Performance anti-patterns to detect
PERF_PATTERNS = {
    "n_plus_one": {
        "patterns": [
            r"for\s+\w+\s+in\s+\w+:.*?\.get\(",
            r"for\s+\w+\s+in\s+\w+:.*?\.query\(",
            r"for\s+\w+\s+in\s+\w+:.*?\.fetch\(",
        ],
        "description": "Potential N+1 query pattern",
        "impact": "high",
    },
    "sync_in_async": {
        "patterns": [
            r"async\s+def.*?time\.sleep\(",
            r"async\s+def.*?requests\.get\(",
            r"async\s+def.*?open\([^)]+\)\.read\(",
        ],
        "description": "Synchronous operation in async context",
        "impact": "high",
    },
    "list_comprehension_in_loop": {
        "patterns": [
            r"for\s+\w+\s+in\s+\[.*for.*\]:",
        ],
        "description": "List comprehension recreated in loop",
        "impact": "medium",
    },
    "string_concat_loop": {
        "patterns": [
            r'for\s+.*:\s*\n\s*\w+\s*\+=\s*["\']',
            r'for\s+.*:\s*\n\s*\w+\s*=\s*\w+\s*\+\s*["\']',
        ],
        "description": "String concatenation in loop (use join)",
        "impact": "medium",
    },
    "global_import": {
        "patterns": [
            r"^from\s+\w+\s+import\s+\*",
        ],
        "description": "Wildcard import may slow startup",
        "impact": "low",
    },
    "large_list_copy": {
        "patterns": [
            r"list\(\w+\)",
            r"\w+\[:\]",
        ],
        "description": "Full list copy (may be inefficient for large lists)",
        "impact": "low",
    },
    "repeated_regex": {
        "patterns": [
            r're\.(search|match|findall)\s*\(["\'][^"\']+["\']',
        ],
        "description": "Regex pattern not pre-compiled",
        "impact": "medium",
    },
    "nested_loops": {
        "patterns": [
            r"for\s+\w+\s+in\s+\w+:\s*\n\s+for\s+\w+\s+in\s+\w+:\s*\n\s+for",
        ],
        "description": "Triple nested loop (O(n³) complexity)",
        "impact": "high",
    },
}


class PerformanceAuditWorkflow(BaseWorkflow):
    """
    Identify performance bottlenecks and optimization opportunities.

    Uses static analysis to find common performance anti-patterns
    and algorithmic complexity issues.
    """

    name = "perf-audit"
    description = "Identify performance bottlenecks and optimization opportunities"
    stages = ["profile", "analyze", "hotspots", "optimize"]
    tier_map = {
        "profile": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "hotspots": ModelTier.CAPABLE,
        "optimize": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        min_hotspots_for_premium: int = 3,
        **kwargs: Any,
    ):
        """
        Initialize performance audit workflow.

        Args:
            min_hotspots_for_premium: Minimum hotspots to trigger premium optimization
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.min_hotspots_for_premium = min_hotspots_for_premium
        self._hotspot_count: int = 0
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

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

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Downgrade optimize stage if few hotspots.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "optimize":
            if self._hotspot_count < self.min_hotspots_for_premium:
                self.tier_map["optimize"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "profile":
            return await self._profile(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "hotspots":
            return await self._hotspots(input_data, tier)
        elif stage_name == "optimize":
            return await self._optimize(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _profile(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Static analysis for common performance anti-patterns.

        Scans code for known performance issues.
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py"])

        findings: list[dict] = []
        files_scanned = 0

        target = Path(target_path)
        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    if any(
                        skip in str(file_path)
                        for skip in [".git", "node_modules", "__pycache__", "venv", "test"]
                    ):
                        continue

                    try:
                        content = file_path.read_text(errors="ignore")
                        files_scanned += 1

                        for pattern_name, pattern_info in PERF_PATTERNS.items():
                            for pattern in pattern_info["patterns"]:
                                matches = list(re.finditer(pattern, content, re.MULTILINE))
                                for match in matches:
                                    line_num = content[: match.start()].count("\n") + 1
                                    findings.append(
                                        {
                                            "type": pattern_name,
                                            "file": str(file_path),
                                            "line": line_num,
                                            "description": pattern_info["description"],
                                            "impact": pattern_info["impact"],
                                            "match": match.group()[:80],
                                        }
                                    )
                    except OSError:
                        continue

        # Group by impact
        by_impact: dict[str, list] = {"high": [], "medium": [], "low": []}
        for f in findings:
            impact = f.get("impact", "low")
            by_impact[impact].append(f)

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(findings)) // 4

        return (
            {
                "findings": findings,
                "finding_count": len(findings),
                "files_scanned": files_scanned,
                "by_impact": {k: len(v) for k, v in by_impact.items()},
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Deep analysis of algorithmic complexity.

        Examines code structure for complexity issues.
        """
        findings = input_data.get("findings", [])

        # Group findings by file
        by_file: dict[str, list] = {}
        for f in findings:
            file_path = f.get("file", "")
            if file_path not in by_file:
                by_file[file_path] = []
            by_file[file_path].append(f)

        # Analyze each file
        analysis: list[dict] = []
        for file_path, file_findings in by_file.items():
            # Calculate file complexity score
            high_count = len([f for f in file_findings if f["impact"] == "high"])
            medium_count = len([f for f in file_findings if f["impact"] == "medium"])
            low_count = len([f for f in file_findings if f["impact"] == "low"])

            complexity_score = high_count * 10 + medium_count * 5 + low_count * 1

            # Identify primary concerns
            concerns = list({f["type"] for f in file_findings})

            analysis.append(
                {
                    "file": file_path,
                    "complexity_score": complexity_score,
                    "finding_count": len(file_findings),
                    "high_impact": high_count,
                    "concerns": concerns[:5],
                }
            )

        # Sort by complexity score
        analysis.sort(key=lambda x: -x["complexity_score"])

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(analysis)) // 4

        return (
            {
                "analysis": analysis,
                "analyzed_files": len(analysis),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _hotspots(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Identify performance hotspots.

        Pinpoints files and areas requiring immediate attention.
        """
        analysis = input_data.get("analysis", [])

        # Top hotspots (highest complexity scores)
        hotspots = [a for a in analysis if a["complexity_score"] >= 10 or a["high_impact"] >= 2]

        self._hotspot_count = len(hotspots)

        # Categorize hotspots
        critical = [h for h in hotspots if h["complexity_score"] >= 20]
        moderate = [h for h in hotspots if 10 <= h["complexity_score"] < 20]

        # Calculate overall perf score (inverse of problems)
        total_score = sum(a["complexity_score"] for a in analysis)
        max_score = len(analysis) * 30  # Max possible score
        perf_score = max(0, 100 - int((total_score / max(max_score, 1)) * 100))

        hotspot_result = {
            "hotspots": hotspots[:15],  # Top 15
            "hotspot_count": self._hotspot_count,
            "critical_count": len(critical),
            "moderate_count": len(moderate),
            "perf_score": perf_score,
            "perf_level": (
                "critical" if perf_score < 50 else "warning" if perf_score < 75 else "good"
            ),
        }

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(hotspot_result)) // 4

        return (
            {
                "hotspot_result": hotspot_result,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _optimize(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate optimization recommendations using LLM.

        Creates actionable recommendations for performance improvements.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        hotspot_result = input_data.get("hotspot_result", {})
        hotspots = hotspot_result.get("hotspots", [])
        findings = input_data.get("findings", [])
        target = input_data.get("target", "")

        # Build hotspots summary for LLM
        hotspots_summary = []
        for h in hotspots[:10]:
            hotspots_summary.append(
                f"- {h.get('file')}: score={h.get('complexity_score', 0)}, "
                f"concerns={', '.join(h.get('concerns', []))}"
            )

        # Summary of most common issues
        issue_counts: dict[str, int] = {}
        for f in findings:
            t = f.get("type", "unknown")
            issue_counts[t] = issue_counts.get(t, 0) + 1
        top_issues = sorted(issue_counts.items(), key=lambda x: -x[1])[:5]

        # Build input payload for prompt
        input_payload = f"""Target: {target or "codebase"}

Performance Score: {hotspot_result.get("perf_score", 0)}/100
Performance Level: {hotspot_result.get("perf_level", "unknown")}

Hotspots:
{chr(10).join(hotspots_summary) if hotspots_summary else "No hotspots identified"}

Top Issues:
{json.dumps([{"type": t, "count": c} for t, c in top_issues], indent=2)}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="performance engineer specializing in optimization",
                goal="Generate comprehensive optimization recommendations for performance issues",
                instructions=[
                    "Analyze each performance hotspot and its concerns",
                    "Provide specific optimization strategies with code examples",
                    "Estimate the impact of each optimization (high/medium/low)",
                    "Prioritize recommendations by potential performance gain",
                    "Include before/after code patterns where helpful",
                ],
                constraints=[
                    "Be specific about which files and patterns to optimize",
                    "Include actionable code changes",
                    "Focus on high-impact optimizations first",
                ],
                input_type="performance_hotspots",
                input_payload=input_payload,
                extra={
                    "perf_score": hotspot_result.get("perf_score", 0),
                    "hotspot_count": len(hotspots),
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a performance engineer specializing in code optimization.
Analyze the identified performance hotspots and generate actionable recommendations.

For each hotspot:
1. Explain why the pattern causes performance issues
2. Provide specific optimization strategies with code examples
3. Estimate the impact of the optimization

Prioritize by potential performance gain."""

            user_message = f"""Generate optimization recommendations for these performance issues:

{input_payload}

Provide detailed optimization strategies."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=3000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        result = {
            "optimization_plan": response,
            "recommendation_count": len(hotspots),
            "top_issues": [{"type": t, "count": c} for t, c in top_issues],
            "perf_score": hotspot_result.get("perf_score", 0),
            "perf_level": hotspot_result.get("perf_level", "unknown"),
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )

        return (result, input_tokens, output_tokens)

    def _get_optimization_action(self, concern: str) -> dict | None:
        """Generate specific optimization action for a concern type."""
        actions = {
            "n_plus_one": {
                "action": "Batch database queries",
                "description": "Use prefetch_related/select_related or batch queries",
                "estimated_impact": "high",
            },
            "sync_in_async": {
                "action": "Use async alternatives",
                "description": "Replace sync operations with async versions",
                "estimated_impact": "high",
            },
            "string_concat_loop": {
                "action": "Use str.join()",
                "description": "Build list of strings and join at the end instead of concatenating",
                "estimated_impact": "medium",
            },
            "repeated_regex": {
                "action": "Pre-compile regex",
                "description": "Use re.compile() and reuse the compiled pattern",
                "estimated_impact": "medium",
            },
            "nested_loops": {
                "action": "Optimize algorithm",
                "description": "Consider using sets, dicts, or itertools to reduce complexity",
                "estimated_impact": "high",
            },
            "list_comprehension_in_loop": {
                "action": "Move comprehension outside loop",
                "description": "Create the list once before the loop",
                "estimated_impact": "medium",
            },
            "large_list_copy": {
                "action": "Use iterators",
                "description": "Consider using iterators instead of copying entire lists",
                "estimated_impact": "low",
            },
            "global_import": {
                "action": "Use specific imports",
                "description": "Import only needed names to reduce memory and startup time",
                "estimated_impact": "low",
            },
        }
        return actions.get(concern)


def main():
    """CLI entry point for performance audit workflow."""
    import asyncio

    async def run():
        workflow = PerformanceAuditWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nPerformance Audit Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")

        output = result.final_output
        print(f"Performance Level: {output.get('perf_level', 'N/A')}")
        print(f"Performance Score: {output.get('perf_score', 0)}/100")
        print(f"Recommendations: {output.get('recommendation_count', 0)}")

        if output.get("top_issues"):
            print("\nTop Issues:")
            for issue in output["top_issues"]:
                print(f"  - {issue['type']}: {issue['count']} occurrences")

        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
