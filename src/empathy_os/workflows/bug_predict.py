"""
Bug Prediction Workflow

Analyzes code against learned bug patterns to predict likely issues
before they manifest in production.

Stages:
1. scan (CHEAP) - Scan codebase for code patterns and structures
2. correlate (CAPABLE) - Match against historical bug patterns
3. predict (CAPABLE) - Identify high-risk areas based on correlation
4. recommend (PREMIUM) - Generate actionable fix recommendations

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import os
from pathlib import Path
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier


class BugPredictionWorkflow(BaseWorkflow):
    """
    Predict bugs by correlating current code with learned patterns.

    Uses pattern library integration to identify code that matches
    historical bug patterns and generates preventive recommendations.
    """

    name = "bug-predict"
    description = "Predict bugs by analyzing code against learned patterns"
    stages = ["scan", "correlate", "predict", "recommend"]
    tier_map = {
        "scan": ModelTier.CHEAP,
        "correlate": ModelTier.CAPABLE,
        "predict": ModelTier.CAPABLE,
        "recommend": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        risk_threshold: float = 0.7,
        patterns_dir: str = "./patterns",
        **kwargs: Any,
    ):
        """
        Initialize bug prediction workflow.

        Args:
            risk_threshold: Minimum risk score to trigger premium recommendations
            patterns_dir: Directory containing learned patterns
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.risk_threshold = risk_threshold
        self.patterns_dir = patterns_dir
        self._risk_score: float = 0.0
        self._bug_patterns: list[dict] = []
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")
        self._load_patterns()

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

    def _load_patterns(self) -> None:
        """Load bug patterns from the pattern library."""
        debugging_file = Path(self.patterns_dir) / "debugging.json"
        if debugging_file.exists():
            try:
                with open(debugging_file) as f:
                    data = json.load(f)
                    self._bug_patterns = data.get("patterns", [])
            except (json.JSONDecodeError, OSError):
                self._bug_patterns = []

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Conditionally downgrade recommend stage based on risk score.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "recommend":
            if self._risk_score < self.risk_threshold:
                # Downgrade to CAPABLE instead of skipping
                self.tier_map["recommend"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """
        Route to specific stage implementation.

        Args:
            stage_name: Name of the stage to run
            tier: Model tier to use
            input_data: Input data for the stage

        Returns:
            Tuple of (output_data, input_tokens, output_tokens)
        """
        if stage_name == "scan":
            return await self._scan(input_data, tier)
        elif stage_name == "correlate":
            return await self._correlate(input_data, tier)
        elif stage_name == "predict":
            return await self._predict(input_data, tier)
        elif stage_name == "recommend":
            return await self._recommend(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _scan(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Scan codebase for code patterns and structures.

        In production, this would analyze source files for patterns
        that historically correlate with bugs.
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py", ".ts", ".tsx", ".js"])

        # Simulate scanning for code patterns
        scanned_files: list[dict] = []
        patterns_found: list[dict] = []

        # Walk directory and collect file info
        target = Path(target_path)
        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    if ".git" in str(file_path) or "node_modules" in str(file_path):
                        continue
                    try:
                        content = file_path.read_text(errors="ignore")
                        scanned_files.append(
                            {
                                "path": str(file_path),
                                "lines": len(content.splitlines()),
                                "size": len(content),
                            }
                        )

                        # Look for common bug-prone patterns
                        if "except:" in content or "except Exception:" in content:
                            patterns_found.append(
                                {
                                    "file": str(file_path),
                                    "pattern": "broad_exception",
                                    "severity": "medium",
                                }
                            )
                        if "# TODO" in content or "# FIXME" in content:
                            patterns_found.append(
                                {
                                    "file": str(file_path),
                                    "pattern": "incomplete_code",
                                    "severity": "low",
                                }
                            )
                        if "eval(" in content or "exec(" in content:
                            patterns_found.append(
                                {
                                    "file": str(file_path),
                                    "pattern": "dangerous_eval",
                                    "severity": "high",
                                }
                            )
                    except OSError:
                        continue

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(scanned_files)) // 4 + len(str(patterns_found)) // 4

        return (
            {
                "scanned_files": scanned_files[:100],  # Limit for efficiency
                "patterns_found": patterns_found,
                "file_count": len(scanned_files),
                "pattern_count": len(patterns_found),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _correlate(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Match current code patterns against historical bug patterns.

        Correlates findings from scan stage with patterns stored in
        the debugging.json pattern library.
        """
        patterns_found = input_data.get("patterns_found", [])
        correlations: list[dict] = []

        # Match against known bug patterns
        for pattern in patterns_found:
            pattern_type = pattern.get("pattern", "")

            # Check against historical patterns
            for bug_pattern in self._bug_patterns:
                bug_type = bug_pattern.get("bug_type", "")
                if self._patterns_correlate(pattern_type, bug_type):
                    correlations.append(
                        {
                            "current_pattern": pattern,
                            "historical_bug": {
                                "type": bug_type,
                                "root_cause": bug_pattern.get("root_cause", ""),
                                "fix": bug_pattern.get("fix", ""),
                            },
                            "confidence": 0.75,
                        }
                    )

        # Add correlations for patterns without direct matches
        for pattern in patterns_found:
            if not any(c["current_pattern"] == pattern for c in correlations):
                correlations.append(
                    {
                        "current_pattern": pattern,
                        "historical_bug": None,
                        "confidence": 0.3,
                    }
                )

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(correlations)) // 4

        return (
            {
                "correlations": correlations,
                "correlation_count": len(correlations),
                "high_confidence_count": len([c for c in correlations if c["confidence"] > 0.6]),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _patterns_correlate(self, current: str, historical: str) -> bool:
        """Check if current pattern correlates with historical bug type."""
        correlation_map = {
            "broad_exception": ["null_reference", "type_mismatch", "unknown"],
            "incomplete_code": ["async_timing", "null_reference"],
            "dangerous_eval": ["import_error", "type_mismatch"],
        }
        return historical in correlation_map.get(current, [])

    async def _predict(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Identify high-risk areas based on correlation scores.

        Calculates risk scores for each file and identifies
        the most likely locations for bugs to occur.
        """
        correlations = input_data.get("correlations", [])
        patterns_found = input_data.get("patterns_found", [])

        # Calculate file risk scores
        file_risks: dict[str, float] = {}
        for corr in correlations:
            file_path = corr["current_pattern"].get("file", "")
            confidence = corr.get("confidence", 0.3)
            severity_weight = {
                "high": 1.0,
                "medium": 0.6,
                "low": 0.3,
            }.get(corr["current_pattern"].get("severity", "low"), 0.3)

            risk = confidence * severity_weight
            file_risks[file_path] = file_risks.get(file_path, 0) + risk

        # Normalize and sort
        max_risk = max(file_risks.values()) if file_risks else 1.0
        predictions = [
            {
                "file": f,
                "risk_score": round(r / max_risk, 2),
                "patterns": [p for p in patterns_found if p.get("file") == f],
            }
            for f, r in sorted(file_risks.items(), key=lambda x: -x[1])
        ]

        # Calculate overall risk score
        self._risk_score = (
            sum(p["risk_score"] for p in predictions[:5]) / 5
            if len(predictions) >= 5
            else sum(p["risk_score"] for p in predictions) / max(len(predictions), 1)
        )

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(predictions)) // 4

        return (
            {
                "predictions": predictions[:20],  # Top 20 risky files
                "overall_risk_score": round(self._risk_score, 2),
                "high_risk_files": len([p for p in predictions if p["risk_score"] > 0.7]),
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    async def _recommend(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate actionable fix recommendations using LLM.

        Uses premium tier (or capable if downgraded) to generate
        specific recommendations for addressing predicted bugs.
        """
        predictions = input_data.get("predictions", [])
        target = input_data.get("target", "")

        # Build context for LLM
        top_risks = predictions[:10]
        issues_summary = []
        for pred in top_risks:
            file_path = pred.get("file", "")
            patterns = pred.get("patterns", [])
            for p in patterns:
                issues_summary.append(
                    f"- {file_path}: {p.get('pattern')} (severity: {p.get('severity')})"
                )

        system = """You are a senior software engineer specializing in bug prevention and code quality.
Analyze the identified code patterns and generate actionable recommendations.

For each issue:
1. Explain why this pattern is risky
2. Provide a specific fix with code example if applicable
3. Suggest preventive measures

Be specific and actionable. Prioritize by severity."""

        user_message = f"""Analyze these bug-prone patterns and provide recommendations:

Target: {target or 'codebase'}

Issues Found:
{chr(10).join(issues_summary) if issues_summary else 'No specific issues identified'}

Historical Bug Patterns:
{json.dumps(self._bug_patterns[:5], indent=2) if self._bug_patterns else 'No historical patterns available'}

Risk Score: {input_data.get('overall_risk_score', 0):.2f}

Provide detailed recommendations for preventing bugs."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=2000
        )

        return (
            {
                "recommendations": response,
                "recommendation_count": len(top_risks),
                "model_tier_used": tier.value,
                "overall_risk_score": input_data.get("overall_risk_score", 0),
            },
            input_tokens,
            output_tokens,
        )


def main():
    """CLI entry point for bug prediction workflow."""
    import asyncio

    async def run():
        workflow = BugPredictionWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nBug Prediction Results")
        print("=" * 50)
        print(f"Success: {result.success}")
        print(f"Risk Score: {result.final_output.get('overall_risk_score', 0)}")
        print(f"Recommendations: {result.final_output.get('recommendation_count', 0)}")
        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        print(
            f"  Savings: ${result.cost_report.savings:.4f} ({result.cost_report.savings_percent:.1f}%)"
        )

    asyncio.run(run())


if __name__ == "__main__":
    main()
