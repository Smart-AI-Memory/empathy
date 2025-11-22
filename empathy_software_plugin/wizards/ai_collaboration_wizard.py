"""
AI Collaboration Pattern Wizard - Level 4 Anticipatory Empathy

Alerts developers when their AI integration patterns will become problematic.

In our experience developing the Empathy Framework itself, we discovered
that the WAY you collaborate with AI matters as much as WHAT you ask it to do.
This wizard learned to recognize when reactive patterns will limit effectiveness.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class AICollaborationWizard(BaseWizard):
    """
    Level 4 Anticipatory: Analyzes HOW developers work with AI.

    Meta-insight: This wizard applies the Empathy Framework to itself.
    It helps developers progress from Level 1 (reactive AI usage) to
    Level 4 (anticipatory AI partnership).

    What We Learned Building This Framework:
    - Most developers start at Level 1 (ask AI, get answer, done)
    - Level 3 patterns (proactive AI) require structural changes
    - Level 4 patterns (anticipatory AI) transform productivity
    - Early pattern adoption prevents later refactoring
    """

    def __init__(self):
        super().__init__(
            name="AI Collaboration Pattern Wizard",
            domain="software",
            empathy_level=4,
            category="ai_development",
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "ai_integration_files",  # Files with AI API calls
            "project_path",  # Project root
            "ai_usage_patterns",  # How AI is currently used
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze AI collaboration patterns and predict limitations.

        Meta: This wizard helps developers build systems like the
        Empathy Framework itself - systems that transcend reactive AI.
        """
        self.validate_context(context)

        integration_files = context["ai_integration_files"]
        usage_patterns = context.get("ai_usage_patterns", [])

        # Analyze current patterns
        issues = await self._analyze_collaboration_maturity(integration_files, usage_patterns)

        # Level 4: Predict when current patterns will limit growth
        predictions = await self._predict_collaboration_bottlenecks(
            integration_files, usage_patterns, context
        )

        recommendations = self._generate_recommendations(issues, predictions)
        patterns = self._extract_patterns(issues, predictions)

        return {
            "issues": issues,
            "predictions": predictions,
            "recommendations": recommendations,
            "patterns": patterns,
            "confidence": 0.90,  # High confidence - we lived this
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "current_maturity_level": self._assess_maturity_level(issues),
                "files_analyzed": len(integration_files),
            },
        }

    async def _analyze_collaboration_maturity(
        self, integration_files: list[str], usage_patterns: list[dict]
    ) -> list[dict[str, Any]]:
        """
        Assess current AI collaboration maturity level.

        Maps observed patterns to Empathy Framework levels 1-5.
        """
        issues = []

        # Check for Level 1 patterns (Reactive)
        reactive_patterns = self._detect_reactive_patterns(integration_files)
        if reactive_patterns > len(integration_files) * 0.7:
            issues.append(
                {
                    "severity": "info",
                    "type": "level_1_reactive",
                    "message": (
                        f"{reactive_patterns}/{len(integration_files)} AI integrations "
                        "are purely reactive (Level 1). In our experience, this limits "
                        "AI to being a Q&A tool rather than a collaborative partner."
                    ),
                    "current_level": 1,
                    "suggestion": (
                        "Consider Level 2 (Guided): Use calibrated questions to refine "
                        "AI understanding before generating responses"
                    ),
                }
            )

        # Check for missing context accumulation (Level 2 → 3 transition)
        if not self._has_context_accumulation(integration_files):
            issues.append(
                {
                    "severity": "warning",
                    "type": "no_context_accumulation",
                    "message": (
                        "AI calls don't accumulate context across interactions. "
                        "In our experience, this prevents progression to Level 3 "
                        "(Proactive) patterns where AI learns from history."
                    ),
                    "current_level": 1,
                    "suggestion": (
                        "Implement CollaborationState tracking: trust levels, patterns, "
                        "shared context (see Empathy Framework core)"
                    ),
                }
            )

        # Check for pattern detection capability (Level 3 requirement)
        if not self._has_pattern_detection(integration_files):
            issues.append(
                {
                    "severity": "info",
                    "type": "no_pattern_detection",
                    "message": (
                        "No pattern detection found. Level 3 (Proactive) AI requires "
                        "recognizing user patterns to act before being asked."
                    ),
                    "current_level": 2,
                    "suggestion": (
                        "Add pattern library: track user workflows, detect sequences, "
                        "enable proactive suggestions"
                    ),
                }
            )

        # Check for trajectory analysis (Level 4 requirement)
        if not self._has_trajectory_analysis(integration_files):
            issues.append(
                {
                    "severity": "info",
                    "type": "no_trajectory_analysis",
                    "message": (
                        "No system trajectory analysis detected. Level 4 (Anticipatory) "
                        "requires analyzing where the system is headed, not just where it is."
                    ),
                    "current_level": 3,
                    "suggestion": (
                        "Implement trajectory analysis: growth rates, bottleneck prediction, "
                        "leverage point identification"
                    ),
                }
            )

        return issues

    async def _predict_collaboration_bottlenecks(
        self, integration_files: list[str], usage_patterns: list[dict], full_context: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """
        Level 4: Predict when current collaboration patterns will limit growth.

        This is meta-Level 4: using anticipatory empathy to help developers
        build anticipatory empathy systems.
        """
        predictions = []

        current_level = self._assess_maturity_level_numeric(integration_files)

        # Pattern 1: Stuck at Level 1 (Reactive)
        if current_level == 1 and len(integration_files) > 5:
            predictions.append(
                {
                    "type": "reactive_pattern_limitation",
                    "alert": (
                        f"You have {len(integration_files)} AI integrations, all at Level 1 "
                        "(Reactive). In our experience building the Empathy Framework, "
                        "reactive AI becomes a burden as integration grows. Alert: Design "
                        "for higher levels now, before you have dozens of integrations to refactor."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Start with Level 2 for new integrations (add calibrated questions)",
                        "Implement CollaborationState tracking (trust, context, patterns)",
                        "Design pattern library for cross-integration learning",
                        "Create abstraction layer (makes refactoring easier later)",
                    ],
                    "reasoning": (
                        "We refactored from Level 1 to Level 4 mid-project. "
                        "It took 2 months. Starting with Level 2-3 architecture "
                        "would have saved significant rework."
                    ),
                    "personal_experience": (
                        "When we built our 16th Coach wizard, we realized we weren't "
                        "writing wizards anymore - we were teaching the system to recognize "
                        "patterns. That shift only happened because we'd built the "
                        "infrastructure for higher-level collaboration."
                    ),
                }
            )

        # Pattern 2: No feedback loops
        if not self._has_feedback_loops(integration_files):
            predictions.append(
                {
                    "type": "missing_feedback_loops",
                    "alert": (
                        "No feedback loops detected between AI outputs and system state. "
                        "In our experience, this prevents AI from learning and improving. "
                        "Alert: Design feedback mechanisms before AI quality plateaus."
                    ),
                    "probability": "medium-high",
                    "impact": "high",
                    "prevention_steps": [
                        "Track AI output quality (user accepts/rejects/modifies)",
                        "Implement trust building (successful outputs increase confidence)",
                        "Add pattern reinforcement (reward accurate predictions)",
                        "Create quality metrics dashboard",
                    ],
                    "reasoning": (
                        "Feedback loops enable self-improvement. Without them, "
                        "AI quality is static. We've seen quality improve 2-3x "
                        "with proper feedback integration."
                    ),
                }
            )

        # Pattern 3: No cross-integration learning
        if len(integration_files) > 3 and not self._has_pattern_sharing(integration_files):
            predictions.append(
                {
                    "type": "siloed_ai_integrations",
                    "alert": (
                        f"You have {len(integration_files)} AI integrations with no pattern "
                        "sharing. In our experience, this is a missed opportunity. "
                        "Alert: Implement Level 5 (Systems) pattern library before "
                        "you miss cross-domain insights."
                    ),
                    "probability": "medium",
                    "impact": "medium",
                    "prevention_steps": [
                        "Create shared PatternLibrary (see Empathy Framework)",
                        "Enable cross-integration pattern discovery",
                        "Implement pattern abstraction (domain-agnostic patterns)",
                        "Add pattern contribution hooks to all AI integrations",
                    ],
                    "reasoning": (
                        "Pattern from software development: 'testing bottleneck'. "
                        "Same pattern applies to healthcare documentation burden. "
                        "Shared pattern library enables this insight."
                    ),
                    "personal_experience": (
                        "We discovered the 'growth trajectory alert' pattern in software "
                        "testing, then applied it to healthcare compliance. Same pattern, "
                        "different domain. That only worked because we'd built Level 5 "
                        "cross-domain learning."
                    ),
                }
            )

        # Pattern 4: AI as tool, not partner
        if self._ai_used_as_tool(integration_files):
            predictions.append(
                {
                    "type": "ai_tool_mindset",
                    "alert": (
                        "AI is being used as a tool (call, get response, done) rather than "
                        "a collaborative partner. In our experience, this mental model "
                        "prevents breakthrough productivity gains. Alert: Shift to partnership "
                        "model before you plateau."
                    ),
                    "probability": "medium",
                    "impact": "high",
                    "prevention_steps": [
                        "Implement persistent AI context (conversation memory)",
                        "Add AI initiative (proactive suggestions)",
                        "Design for AI-driven insights (not just AI-answered questions)",
                        "Create bidirectional feedback (AI learns from you, you learn from AI)",
                    ],
                    "reasoning": (
                        "Mental model shift: Tool → Partner. "
                        "This unlocks anticipatory capabilities. "
                        "In our experience, the impact was more profound than anticipated."
                    ),
                    "personal_experience": (
                        "I had a theory: AI collaboration through empathy levels. "
                        "When it worked, the impact exceeded expectations. "
                        "Not because AI wrote more code, but because it anticipated "
                        "structural issues before they became costly."
                    ),
                }
            )

        # Pattern 5: No architecture for growth
        if len(integration_files) > 2 and not self._has_collaboration_architecture(
            integration_files
        ):
            predictions.append(
                {
                    "type": "collaboration_architecture_gap",
                    "alert": (
                        "Multiple AI integrations without unified collaboration architecture. "
                        "In our experience, this leads to inconsistent AI quality and "
                        "difficult maintenance. Alert: Design collaboration framework "
                        "before technical debt compounds."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention_steps": [
                        "Adopt or design collaboration framework (like Empathy Framework)",
                        "Create standard abstractions (EmpathyOS, CollaborationState, etc.)",
                        "Implement consistent empathy levels across integrations",
                        "Build pattern library infrastructure",
                    ],
                    "reasoning": (
                        "Ad-hoc AI integration scales poorly. "
                        "Framework-based approach scales well. "
                        "We learned this by building both ways."
                    ),
                }
            )

        return predictions

    def _generate_recommendations(self, issues: list[dict], predictions: list[dict]) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Start with maturity assessment
        current_level = self._assess_maturity_level(issues)
        recommendations.append(f"Current AI Collaboration Maturity: Level {current_level}")
        recommendations.append("")

        # High-impact predictions
        for pred in predictions:
            if pred.get("impact") == "high":
                recommendations.append(f"[ALERT] {pred['alert']}")
                recommendations.append("")
                recommendations.append("Recommended path forward:")
                for i, step in enumerate(pred["prevention_steps"], 1):
                    recommendations.append(f"  {i}. {step}")

                # Add personal experience if available
                if "personal_experience" in pred:
                    recommendations.append("")
                    recommendations.append(f"Experience: {pred['personal_experience']}")
                recommendations.append("")

        # Growth path
        recommendations.append("Growth Path:")
        if current_level < 2:
            recommendations.append("  Next: Implement Level 2 (Guided) - Add calibrated questions")
        elif current_level < 3:
            recommendations.append("  Next: Implement Level 3 (Proactive) - Add pattern detection")
        elif current_level < 4:
            recommendations.append(
                "  Next: Implement Level 4 (Anticipatory) - Add trajectory analysis"
            )
        else:
            recommendations.append(
                "  Next: Implement Level 5 (Systems) - Add cross-domain learning"
            )

        return recommendations

    def _extract_patterns(
        self, issues: list[dict], predictions: list[dict]
    ) -> list[dict[str, Any]]:
        """Extract cross-domain patterns"""
        return [
            {
                "pattern_type": "collaboration_maturity_model",
                "description": (
                    "Systems that progress through collaboration maturity levels "
                    "(Reactive → Guided → Proactive → Anticipatory → Systems) "
                    "achieve exponential gains in effectiveness"
                ),
                "domain_agnostic": True,
                "applicable_to": [
                    "AI-human collaboration",
                    "Team collaboration",
                    "Tool adoption",
                    "Process improvement",
                    "Learning systems",
                ],
                "levels": [
                    "1: Reactive (help after asked)",
                    "2: Guided (collaborative exploration)",
                    "3: Proactive (act before asked)",
                    "4: Anticipatory (predict and design relief)",
                    "5: Systems (build scalable structures)",
                ],
            }
        ]

    # Assessment methods

    def _assess_maturity_level(self, issues: list[dict]) -> int:
        """Assess overall maturity level from issues"""
        levels = [issue.get("current_level", 1) for issue in issues]
        return max(levels) if levels else 1

    def _assess_maturity_level_numeric(self, integration_files: list[str]) -> int:
        """Assess maturity level numerically"""
        if self._has_trajectory_analysis(integration_files):
            return 4
        if self._has_pattern_detection(integration_files):
            return 3
        if self._has_context_accumulation(integration_files):
            return 2
        return 1

    # Detection helper methods

    def _detect_reactive_patterns(self, files: list[str]) -> int:
        """Count files with purely reactive AI patterns"""
        reactive_count = 0
        for filepath in files:
            try:
                with open(filepath) as f:
                    content = f.read()
                    # Simple heuristic: one-off AI calls with no context
                    if "ai.generate" in content or "openai." in content or "anthropic." in content:
                        if "context" not in content.lower() and "history" not in content.lower():
                            reactive_count += 1
            except OSError:
                pass
        return reactive_count

    def _has_context_accumulation(self, files: list[str]) -> bool:
        """Check if codebase accumulates context"""
        keywords = ["CollaborationState", "context_history", "conversation_memory", "session_state"]
        return self._has_any_keyword(files, keywords)

    def _has_pattern_detection(self, files: list[str]) -> bool:
        """Check if codebase has pattern detection"""
        keywords = ["PatternLibrary", "pattern_detection", "detect_patterns", "pattern_analysis"]
        return self._has_any_keyword(files, keywords)

    def _has_trajectory_analysis(self, files: list[str]) -> bool:
        """Check if codebase analyzes trajectory"""
        keywords = ["trajectory", "growth_rate", "predict_bottleneck", "anticipatory"]
        return self._has_any_keyword(files, keywords)

    def _has_feedback_loops(self, files: list[str]) -> bool:
        """Check for feedback loop implementation"""
        keywords = ["feedback", "trust_level", "quality_metric", "outcome_tracking"]
        return self._has_any_keyword(files, keywords)

    def _has_pattern_sharing(self, files: list[str]) -> bool:
        """Check for cross-integration pattern sharing"""
        keywords = ["PatternLibrary", "shared_patterns", "cross_domain", "contribute_patterns"]
        return self._has_any_keyword(files, keywords)

    def _ai_used_as_tool(self, files: list[str]) -> bool:
        """Check if AI is used as tool vs partner"""
        # Heuristic: tool usage has no context, no feedback, one-shot calls
        has_context = self._has_context_accumulation(files)
        has_feedback = self._has_feedback_loops(files)
        return not (has_context and has_feedback)

    def _has_collaboration_architecture(self, files: list[str]) -> bool:
        """Check for unified collaboration architecture"""
        keywords = ["EmpathyOS", "CollaborationFramework", "AIOrchestrator", "BaseWizard"]
        return self._has_any_keyword(files, keywords)

    def _has_any_keyword(self, files: list[str], keywords: list[str]) -> bool:
        """Check if any file contains any keyword"""
        for filepath in files:
            try:
                with open(filepath) as f:
                    content = f.read()
                    if any(kw in content for kw in keywords):
                        return True
            except OSError:
                pass
        return False
