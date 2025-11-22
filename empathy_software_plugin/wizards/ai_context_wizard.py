"""
AI Context Window Management Wizard - Level 4 Anticipatory Empathy

Alerts developers when context window usage patterns will become problematic.

In our experience building AI Nurse Florence with complex multi-step agents,
context window management became critical. This wizard learned to detect
when context strategies that work today will fail tomorrow as complexity grows.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class AIContextWindowWizard(BaseWizard):
    """
    Level 4 Anticipatory: Predicts context window issues before they occur.

    What We Learned:
    - Context needs grow non-linearly with feature complexity
    - Naive concatenation fails at ~60% of window capacity
    - Chunking strategies need planning before you hit limits
    - Early refactoring prevents emergency rewrites
    """

    def __init__(self):
        super().__init__(
            name="AI Context Window Management Wizard",
            domain="software",
            empathy_level=4,
            category="ai_development",
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "ai_calls",  # List of AI API calls in codebase
            "context_sources",  # Where context comes from (DB, files, etc.)
            "ai_provider",  # openai, anthropic, etc.
            "model_name",  # gpt-4, claude-3, etc.
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze context window usage and predict future issues.

        In our experience: Context limits sneak up on you. By the time
        you hit the limit, you're forced into emergency refactoring.
        """
        self.validate_context(context)

        ai_calls = context["ai_calls"]
        context_sources = context["context_sources"]
        ai_provider = context.get("ai_provider", "unknown")
        model_name = context.get("model_name", "unknown")

        # Get model limits
        model_limits = self._get_model_limits(ai_provider, model_name)

        # Current issues
        issues = await self._analyze_current_usage(ai_calls, context_sources, model_limits)

        # Level 4: Predict future problems
        predictions = await self._predict_context_issues(
            ai_calls, context_sources, model_limits, context
        )

        recommendations = self._generate_recommendations(issues, predictions)
        patterns = self._extract_patterns(issues, predictions)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": recommendations,
            "patterns": patterns,
            "confidence": 0.85,
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "ai_calls_analyzed": len(ai_calls),
                "model_limit_tokens": model_limits.get("max_tokens", "unknown"),
            },
        }

    async def _analyze_current_usage(
        self, ai_calls: list[dict], context_sources: list[dict], model_limits: dict
    ) -> list[dict[str, Any]]:
        """Analyze current context window usage"""
        issues = []
        max_tokens = model_limits.get("max_tokens", 128000)

        for call in ai_calls:
            estimated_tokens = self._estimate_context_tokens(call, context_sources)
            usage_percent = (estimated_tokens / max_tokens) * 100

            # Current issues
            if usage_percent > 80:
                issues.append(
                    {
                        "severity": "warning",
                        "type": "high_context_usage",
                        "call_location": call.get("location", "unknown"),
                        "message": (
                            f"Context window at {usage_percent:.0f}% capacity. "
                            "In our experience, operations above 80% become unreliable."
                        ),
                        "estimated_tokens": estimated_tokens,
                        "suggestion": "Implement context pruning or chunking strategy",
                    }
                )

            # Check for naive concatenation
            if self._uses_naive_concatenation(call):
                issues.append(
                    {
                        "severity": "info",
                        "type": "naive_concatenation",
                        "call_location": call.get("location", "unknown"),
                        "message": (
                            "Detected simple string concatenation for context building. "
                            "This pattern fails unpredictably as data grows."
                        ),
                        "suggestion": "Use structured context builders with size limits",
                    }
                )

            # Check for missing token counting
            if not self._has_token_counting(call):
                issues.append(
                    {
                        "severity": "info",
                        "type": "missing_token_tracking",
                        "call_location": call.get("location", "unknown"),
                        "message": (
                            "No token counting detected. In our experience, blind context "
                            "injection leads to unpredictable failures."
                        ),
                        "suggestion": "Add token estimation before AI calls",
                    }
                )

        return issues

    async def _predict_context_issues(
        self,
        ai_calls: list[dict],
        context_sources: list[dict],
        model_limits: dict,
        full_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Level 4: Predict future context window problems.

        Based on our experience with multi-agent systems that started simple
        and grew complex.
        """
        predictions = []
        max_tokens = model_limits.get("max_tokens", 128000)

        # Pattern 1: Context growth trajectory
        growth_rate = self._estimate_context_growth_rate(ai_calls, full_context)
        current_avg = self._calculate_avg_context_size(ai_calls, context_sources)

        if growth_rate > 1.2:  # 20% growth
            projected_size = current_avg * (growth_rate**3)  # 3 months out
            projected_percent = (projected_size / max_tokens) * 100

            if projected_percent > 70:
                predictions.append(
                    {
                        "type": "context_capacity_limit",
                        "alert": (
                            f"Context usage growing at {(growth_rate-1)*100:.0f}% rate. "
                            f"Current average: {current_avg:.0f} tokens. "
                            "In our experience, this trajectory leads to context window "
                            "limits. Alert: Implement chunking strategy before you hit the wall."
                        ),
                        "probability": "high",
                        "impact": "high",
                        "prevention_steps": [
                            "Design semantic chunking strategy (split by meaning, not char count)",
                            "Implement context prioritization (keep most relevant)",
                            "Add context summarization for older messages",
                            "Consider retrieval-augmented generation (RAG) pattern",
                            "Implement token budget system with hard limits",
                        ],
                        "reasoning": (
                            f"Growth trajectory: {current_avg:.0f} → {projected_size:.0f} tokens. "
                            "We've seen this pattern require emergency refactoring. "
                            "Proactive design prevents crisis."
                        ),
                    }
                )

        # Pattern 2: Multi-turn conversation growth
        multi_turn_calls = [c for c in ai_calls if self._is_multi_turn(c)]
        if len(multi_turn_calls) > 3:
            predictions.append(
                {
                    "type": "conversation_memory_burden",
                    "alert": (
                        f"Detected {len(multi_turn_calls)} multi-turn conversations. "
                        "In our experience, conversation history grows faster than expected. "
                        "Alert: Implement conversation pruning before memory becomes unwieldy."
                    ),
                    "probability": "medium-high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Implement sliding window (keep last N messages)",
                        "Add conversation summarization (compress old context)",
                        "Design conversation checkpointing (restart with summary)",
                        "Create context budget per conversation turn",
                    ],
                    "reasoning": (
                        "Multi-turn conversations accumulate context linearly. "
                        "Without pruning, they hit limits within 10-20 turns. "
                        "We learned to design for this early."
                    ),
                }
            )

        # Pattern 3: Dynamic context sources
        dynamic_sources = [s for s in context_sources if s.get("type") == "dynamic"]
        if len(dynamic_sources) > 2:
            predictions.append(
                {
                    "type": "dynamic_context_unpredictability",
                    "alert": (
                        f"Found {len(dynamic_sources)} dynamic context sources "
                        "(database queries, API calls, file reads). "
                        "In our experience, dynamic context size is unpredictable. "
                        "Alert: Add size constraints before data growth causes failures."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Add LIMIT clauses to all database queries for context",
                        "Implement pagination for large result sets",
                        "Add size validation before context injection",
                        "Create fallback behavior when context exceeds budget",
                        "Log context size metrics for monitoring",
                    ],
                    "reasoning": (
                        "Dynamic sources return variable amounts of data. "
                        "User has 10 records today, 10,000 tomorrow. "
                        "We've seen this break production systems."
                    ),
                }
            )

        # Pattern 4: Lack of context strategy
        if not self._has_context_strategy(ai_calls):
            predictions.append(
                {
                    "type": "missing_context_architecture",
                    "alert": (
                        "No centralized context management detected. "
                        "In our experience, ad-hoc context building becomes unmaintainable "
                        "as AI integration grows. Alert: Design context architecture now "
                        "while refactoring is still manageable."
                    ),
                    "probability": "medium",
                    "impact": "high",
                    "prevention_steps": [
                        "Create ContextBuilder abstraction",
                        "Implement context templates with variable injection",
                        "Design context caching layer (reuse expensive computations)",
                        "Add context versioning (track what context produced what output)",
                        "Build context testing framework",
                    ],
                    "reasoning": (
                        "We refactored context management 3 times before finding the right "
                        "pattern. Starting with good architecture saves months of rework."
                    ),
                }
            )

        # Pattern 5: Cost implications
        total_estimated_tokens = sum(
            self._estimate_context_tokens(c, context_sources) for c in ai_calls
        )
        if total_estimated_tokens > 50000:  # Arbitrary threshold
            predictions.append(
                {
                    "type": "context_cost_scaling",
                    "alert": (
                        f"Estimated {total_estimated_tokens:,} tokens across all calls. "
                        "In our experience, context costs scale faster than expected. "
                        "Alert: Optimize context efficiency before costs compound."
                    ),
                    "probability": "high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Implement context caching (reuse system prompts)",
                        "Remove redundant context (deduplicate instructions)",
                        "Use prompt compression techniques",
                        "Consider smaller models for simple tasks",
                        "Add cost monitoring and alerting",
                    ],
                    "reasoning": (
                        "Context costs are proportional to token count. "
                        "We've reduced costs 40-60% through context optimization."
                    ),
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Prioritize high-impact predictions
        high_impact = sorted(
            predictions,
            key=lambda p: {"high": 3, "medium": 2, "low": 1}.get(p.get("impact"), 0),
            reverse=True,
        )

        for pred in high_impact[:2]:  # Top 2
            recommendations.append(f"[ALERT] {pred['alert']}")
            recommendations.append("  Immediate actions:")
            for step in pred["prevention_steps"][:3]:
                recommendations.append(f"    - {step}")
            recommendations.append("")

        return recommendations

    def _extract_patterns(
        self, issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """Extract cross-domain patterns"""
        patterns = []

        if any(p["type"] == "dynamic_context_unpredictability" for p in predictions):
            patterns.append(
                {
                    "pattern_type": "unbounded_dynamic_data",
                    "description": (
                        "When system depends on external data sources with unbounded size, "
                        "implement constraints before data growth causes failures"
                    ),
                    "domain_agnostic": True,
                    "applicable_to": [
                        "AI context management",
                        "API responses",
                        "Database queries",
                        "File processing",
                        "Healthcare record retrieval",
                    ],
                    "detection": "Identify dynamic data sources without size limits",
                    "prevention": "Add LIMIT, pagination, size validation",
                }
            )

        return patterns

    # Helper methods

    def _get_model_limits(self, provider: str, model: str) -> dict:
        """Get token limits for AI model"""
        limits = {
            "openai": {
                "gpt-4": {"max_tokens": 8192},
                "gpt-4-32k": {"max_tokens": 32768},
                "gpt-4-turbo": {"max_tokens": 128000},
            },
            "anthropic": {
                "claude-3-opus": {"max_tokens": 200000},
                "claude-3-sonnet": {"max_tokens": 200000},
                "claude-3-haiku": {"max_tokens": 200000},
            },
        }

        return limits.get(provider, {}).get(model, {"max_tokens": 128000})

    def _estimate_context_tokens(self, call: dict, context_sources: list[dict]) -> int:
        """Estimate tokens for an AI call"""
        # Simplified: ~4 chars per token
        base_prompt = call.get("prompt_size", 1000)
        dynamic_context = sum(
            source.get("estimated_size", 0)
            for source in context_sources
            if source.get("call_id") == call.get("id")
        )
        return (base_prompt + dynamic_context) // 4

    def _uses_naive_concatenation(self, call: dict) -> bool:
        """Check if call uses naive string concatenation"""
        # Heuristic: look for patterns like f"prompt + {data}"
        code = call.get("code_snippet", "")
        return "+" in code or "concat" in code.lower()

    def _has_token_counting(self, call: dict) -> bool:
        """Check if call includes token counting"""
        code = call.get("code_snippet", "")
        return "token" in code.lower() and ("count" in code.lower() or "len" in code.lower())

    def _estimate_context_growth_rate(self, ai_calls: list[dict], full_context: dict) -> float:
        """Estimate how fast context is growing"""
        # Simplified: check version history or feature count
        version_history = full_context.get("version_history", [])
        if len(version_history) > 1:
            # Rough heuristic
            return 1.3  # 30% growth
        return 1.1  # Default 10% growth

    def _calculate_avg_context_size(
        self, ai_calls: list[dict], context_sources: list[dict]
    ) -> float:
        """Calculate average context size"""
        if not ai_calls:
            return 0
        total = sum(self._estimate_context_tokens(call, context_sources) for call in ai_calls)
        return total / len(ai_calls)

    def _is_multi_turn(self, call: dict) -> bool:
        """Check if call is part of multi-turn conversation"""
        return call.get("conversation_id") is not None

    def _has_context_strategy(self, ai_calls: list[dict]) -> bool:
        """Check if codebase has centralized context management"""
        # Heuristic: look for context builder classes
        code_snippets = [call.get("code_snippet", "") for call in ai_calls]
        return any(
            "ContextBuilder" in code or "context_manager" in code.lower() for code in code_snippets
        )
