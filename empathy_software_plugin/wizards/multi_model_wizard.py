"""
Multi-Model Coordination Wizard - Level 4 Anticipatory Empathy

Alerts developers when multi-model strategies will create complexity or cost issues.

In our experience, using multiple AI models seems like optimization (pick best
model for each task). But we learned: model coordination overhead, prompt
consistency, and cost tracking become complex fast. This wizard alerts before
those issues compound.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class MultiModelWizard(BaseWizard):
    """
    Level 4 Anticipatory: Predicts multi-model coordination issues.

    What We Learned About Multi-Model Systems:
    - Using "best model for task" sounds smart, adds complexity
    - Inconsistent outputs across models confuse users
    - Cost tracking becomes nightmare without abstraction
    - Fallback strategies essential (model outages happen)
    """

    def __init__(self):
        super().__init__(
            name="Multi-Model Coordination Wizard",
            domain="software",
            empathy_level=4,
            category="ai_development",
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "model_usage",  # Which models are used where
            "model_count",  # Number of different models
            "routing_logic",  # How requests route to models
            "project_path",  # Project root
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze multi-model coordination and predict issues.

        In our experience: Multi-model complexity grows non-linearly.
        2 models = manageable. 4+ models = coordination nightmare without framework.
        """
        self.validate_context(context)

        model_usage = context.get("model_usage", [])
        model_count = context.get("model_count", 0)
        routing = context.get("routing_logic", [])

        # Current issues
        issues = await self._analyze_model_coordination(model_usage, model_count, routing)

        # Level 4: Predict coordination breakdown
        predictions = await self._predict_multi_model_issues(
            model_usage, model_count, routing, context
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
                "model_count": model_count,
            },
        }

    async def _analyze_model_coordination(
        self, model_usage: list[dict], model_count: int, routing: list[str]
    ) -> list[dict[str, Any]]:
        """Analyze current multi-model coordination"""
        issues = []

        # Issue: Many models without abstraction
        if model_count > 2 and not self._has_model_abstraction(routing):
            issues.append(
                {
                    "severity": "warning",
                    "type": "no_model_abstraction",
                    "message": (
                        f"Using {model_count} models without abstraction layer. "
                        "In our experience, direct model calls become unmaintainable "
                        "beyond 2 models."
                    ),
                    "suggestion": (
                        "Create model abstraction layer (unified interface, "
                        "routing logic, fallback handling)"
                    ),
                }
            )

        # Issue: No fallback strategy
        if model_count > 1 and not self._has_fallback_strategy(routing):
            issues.append(
                {
                    "severity": "warning",
                    "type": "no_fallback_strategy",
                    "message": (
                        "Multiple models but no fallback strategy. When primary model "
                        "fails or is rate-limited, entire feature breaks."
                    ),
                    "suggestion": "Implement model fallback chain (primary → secondary → cached)",
                }
            )

        # Issue: Inconsistent prompt templates
        if not self._has_consistent_prompts(model_usage):
            issues.append(
                {
                    "severity": "info",
                    "type": "inconsistent_prompts",
                    "message": (
                        "Different prompt templates per model. In our experience, "
                        "this causes output inconsistency across models."
                    ),
                    "suggestion": (
                        "Use model-agnostic prompt templates with model-specific adaptations"
                    ),
                }
            )

        # Issue: No cost tracking per model
        if model_count > 2 and not self._has_cost_tracking(routing):
            issues.append(
                {
                    "severity": "warning",
                    "type": "no_cost_tracking",
                    "message": (
                        f"{model_count} models without per-model cost tracking. "
                        "Impossible to optimize spend without visibility."
                    ),
                    "suggestion": "Add cost tracking middleware (log tokens/costs per model)",
                }
            )

        # Issue: No performance monitoring
        if not self._has_performance_monitoring(routing):
            issues.append(
                {
                    "severity": "info",
                    "type": "no_performance_monitoring",
                    "message": (
                        "No performance monitoring across models. Can't identify "
                        "which models are slow, failing, or degrading."
                    ),
                    "suggestion": "Add per-model metrics (latency, errors, quality)",
                }
            )

        return issues

    async def _predict_multi_model_issues(
        self,
        model_usage: list[dict],
        model_count: int,
        routing: list[str],
        full_context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Level 4: Predict multi-model coordination breakdown.

        Based on our experience: Coordination complexity = O(n) × configuration.
        """
        predictions = []

        # Pattern 1: Model count approaching complexity threshold
        if 4 <= model_count <= 7:
            predictions.append(
                {
                    "type": "coordination_complexity",
                    "alert": (
                        f"You're using {model_count} different models. In our experience, "
                        "multi-model systems become difficult to manage beyond 5 models "
                        "without formal coordination framework. Alert: Design model "
                        "orchestration layer before complexity compounds."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Create model registry (centralized model configuration)",
                        "Implement routing layer (smart model selection)",
                        "Add model health monitoring",
                        "Build unified API (abstract model differences)",
                        "Create model testing framework",
                    ],
                    "reasoning": (
                        f"{model_count} models × configuration × prompts × monitoring = "
                        "high coordination overhead. Formal framework reduces complexity."
                    ),
                    "personal_experience": (
                        "We started with GPT-4 for everything. Added Claude for long context. "
                        "Added GPT-3.5 for cheap tasks. Added Gemini for... "
                        "By model #5, configuration chaos. Should have built framework at #3."
                    ),
                }
            )

        # Pattern 2: Cost optimization will become critical
        if model_count > 2 and not self._has_cost_optimization(routing):
            predictions.append(
                {
                    "type": "cost_optimization_needed",
                    "alert": (
                        f"Using {model_count} models without cost optimization. "
                        "In our experience, multi-model costs grow unpredictably. "
                        "Alert: Implement cost controls before bills surprise you."
                    ),
                    "probability": "high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Add per-request cost calculation",
                        "Implement cost-based routing (use cheaper model when possible)",
                        "Create cost budgets and alerts",
                        "Add caching layer (avoid repeated expensive calls)",
                        "Build cost analytics dashboard",
                    ],
                    "reasoning": (
                        "GPT-4: $30/1M tokens. GPT-3.5: $1/1M tokens. Claude Haiku: $0.25/1M. "
                        "Routing all requests to GPT-4 wastes money. Smart routing saves 60-80%."
                    ),
                    "personal_experience": (
                        "Our first multi-model bill: 3x expected. Turns out 90% of requests "
                        "went to most expensive model. Added smart routing, costs dropped 70%."
                    ),
                }
            )

        # Pattern 3: Output consistency issues
        if model_count > 2 and not self._has_output_validation(routing):
            predictions.append(
                {
                    "type": "output_inconsistency",
                    "alert": (
                        "Multiple models without output validation. In our experience, "
                        "different models return different formats, causing downstream errors. "
                        "Alert: Add output validation before inconsistency creates bugs."
                    ),
                    "probability": "medium-high",
                    "impact": "medium",
                    "prevention_steps": [
                        "Define output schemas (Pydantic, JSON Schema)",
                        "Implement validation layer (all models must conform)",
                        "Add output normalization (convert to standard format)",
                        "Create model-specific adapters",
                        "Build output quality tests",
                    ],
                    "reasoning": (
                        'GPT returns {"answer": "..."}. Claude returns {"result": "..."}. '
                        "Your code expects one format. Random failures ensue."
                    ),
                }
            )

        # Pattern 4: Model version drift
        if model_count > 1 and not self._has_version_tracking(routing):
            predictions.append(
                {
                    "type": "model_version_drift",
                    "alert": (
                        "No model version tracking. In our experience, providers update models "
                        "(GPT-4 → GPT-4-turbo), changing behavior silently. Alert: Track versions "
                        "before updates break your system."
                    ),
                    "probability": "medium",
                    "impact": "high",
                    "prevention_steps": [
                        "Pin model versions (gpt-4-0613, not gpt-4)",
                        "Log model version with each request",
                        "Monitor for version changes",
                        "Test before upgrading versions",
                        "Create version migration path",
                    ],
                    "reasoning": (
                        "OpenAI updates GPT-4. Your carefully tuned prompts stop working. "
                        "No logs = can't diagnose. Version tracking = control."
                    ),
                    "personal_experience": (
                        "Provider updated model, our outputs changed format. Took 2 days to "
                        "realize it wasn't our code. Now we pin versions and test upgrades explicitly."
                    ),
                }
            )

        # Pattern 5: Lack of routing intelligence
        if model_count > 3 and not self._has_smart_routing(routing):
            predictions.append(
                {
                    "type": "suboptimal_routing",
                    "alert": (
                        f"With {model_count} models, you need intelligent routing. "
                        "In our experience, static routing wastes money and quality. "
                        "Alert: Implement smart routing before inefficiency compounds."
                    ),
                    "probability": "medium",
                    "impact": "medium",
                    "prevention_steps": [
                        "Classify requests (simple vs complex, short vs long)",
                        "Route based on requirements (cost, speed, quality)",
                        "Implement adaptive routing (learn from outcomes)",
                        "Add A/B testing (compare routing strategies)",
                        "Create routing analytics",
                    ],
                    "reasoning": (
                        "Simple question → expensive model = waste. "
                        "Complex task → cheap model = bad quality. "
                        "Smart routing = right model for right task."
                    ),
                    "personal_experience": (
                        "We route: Simple Q&A → Haiku. Long context → Claude. Code → GPT-4. "
                        "Same quality, 65% cost reduction. Should have done this from day one."
                    ),
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # High-impact predictions
        for pred in predictions:
            if pred.get("impact") in ["high", "medium"]:
                recommendations.append(f"\n[ALERT] {pred['alert']}")
                if "personal_experience" in pred:
                    recommendations.append(f"Experience: {pred['personal_experience']}")
                recommendations.append("Prevention steps:")
                for i, step in enumerate(pred["prevention_steps"][:3], 1):
                    recommendations.append(f"  {i}. {step}")

        return recommendations

    def _extract_patterns(
        self, issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """Extract cross-domain patterns"""
        return [
            {
                "pattern_type": "multi_provider_coordination",
                "description": (
                    "Systems using multiple providers/services hit coordination "
                    "complexity around 4-5 providers. Abstraction layer becomes essential."
                ),
                "domain_agnostic": True,
                "applicable_to": [
                    "Multi-model AI systems",
                    "Multi-cloud infrastructure",
                    "Multi-vendor integrations",
                    "Payment processors (healthcare, finance)",
                    "Any system with provider diversity",
                ],
                "threshold": "4-5 providers",
                "solution": "Build abstraction layer + unified interface",
            }
        ]

    # Helper methods

    def _has_model_abstraction(self, routing: list[str]) -> bool:
        """Check for model abstraction layer"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content
                        for kw in ["ModelRouter", "ModelRegistry", "AbstractModel", "UnifiedAPI"]
                    ):
                        return True
            except:
                pass
        return False

    def _has_fallback_strategy(self, routing: list[str]) -> bool:
        """Check for fallback/retry logic"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if "fallback" in content.lower() or "retry" in content.lower():
                        return True
            except:
                pass
        return False

    def _has_consistent_prompts(self, model_usage: list[dict]) -> bool:
        """Check for consistent prompt templates"""
        # Simplified - would need actual analysis
        return any(usage.get("uses_template_system") for usage in model_usage)

    def _has_cost_tracking(self, routing: list[str]) -> bool:
        """Check for cost tracking"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if "cost" in content.lower() and (
                        "track" in content.lower() or "log" in content.lower()
                    ):
                        return True
            except:
                pass
        return False

    def _has_performance_monitoring(self, routing: list[str]) -> bool:
        """Check for performance monitoring"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower()
                        for kw in ["latency", "metrics", "monitoring", "telemetry"]
                    ):
                        return True
            except:
                pass
        return False

    def _has_cost_optimization(self, routing: list[str]) -> bool:
        """Check for cost optimization strategies"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if "cache" in content.lower() or "budget" in content.lower():
                        return True
            except:
                pass
        return False

    def _has_output_validation(self, routing: list[str]) -> bool:
        """Check for output validation"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(kw in content for kw in ["Pydantic", "validate", "schema", "BaseModel"]):
                        return True
            except:
                pass
        return False

    def _has_version_tracking(self, routing: list[str]) -> bool:
        """Check for model version tracking"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    # Look for specific version strings
                    if "gpt-4-" in content or "claude-3" in content or "version" in content.lower():
                        return True
            except:
                pass
        return False

    def _has_smart_routing(self, routing: list[str]) -> bool:
        """Check for intelligent routing logic"""
        for file_path in routing:
            try:
                with open(file_path) as f:
                    content = f.read()
                    if any(
                        kw in content.lower()
                        for kw in [
                            "classify",
                            "route_by",
                            "select_model",
                            "intelligent",
                            "adaptive",
                        ]
                    ):
                        return True
            except:
                pass
        return False
