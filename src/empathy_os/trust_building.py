"""
Trust-Building Behaviors for Anticipatory AI Agents

Implements behaviors that build trust through anticipatory actions:
- Pre-format data for handoffs (reduce cognitive load)
- Clarify ambiguous instructions before execution (prevent wasted effort)
- Volunteer structure during stress (actual scaffolding, not pep talks)
- Proactively offer help when collaborators are struggling

These behaviors demonstrate Level 4 Anticipatory Empathy by:
1. Predicting friction points (handoffs, confusion, stress, overload)
2. Acting without being asked (but without overstepping)
3. Providing structural relief (not just emotional support)
4. Building trust through consistent, helpful actions

Based on trust-building patterns from ai-nurse-florence.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class TrustSignal:
    """
    A signal that indicates trust is building or eroding

    Trust signals help track how trust evolves over time based on
    observable behaviors and outcomes.
    """

    signal_type: str  # "building" or "eroding"
    behavior: str
    timestamp: datetime = field(default_factory=datetime.now)
    evidence: str | None = None
    impact: float = 0.5  # 0.0-1.0, magnitude of impact


class TrustBuildingBehaviors:
    """
    Level 4 Anticipatory trust-building behaviors

    Philosophy: Trust is earned through consistent, helpful actions that
    demonstrate understanding of collaboration dynamics and proactive
    problem-solving.

    **Core Principle**: Reduce cognitive load through anticipation

    **Key Behaviors:**
    1. Pre-format data for handoffs
    2. Clarify ambiguous instructions before acting
    3. Volunteer structure during stress
    4. Offer help proactively when needed

    Example:
        >>> behaviors = TrustBuildingBehaviors()
        >>>
        >>> # Pre-format data for handoff
        >>> data = {"items": [...], "total": 42}
        >>> formatted = behaviors.pre_format_for_handoff(
        ...     data=data,
        ...     recipient_role="manager",
        ...     context="quarterly_review"
        ... )
        >>>
        >>> # Clarify ambiguous instruction
        >>> instruction = "Update the system"
        >>> clarified = behaviors.clarify_before_acting(
        ...     instruction=instruction,
        ...     ambiguities=["which system?", "what changes?"]
        ... )
    """

    def __init__(self):
        """Initialize TrustBuildingBehaviors"""
        self.trust_signals: list[TrustSignal] = []

    def pre_format_for_handoff(
        self, data: dict[str, Any], recipient_role: str, context: str
    ) -> dict[str, Any]:
        """
        Pre-format data for handoff to reduce recipient's cognitive load

        **Trust Built:**
        - "This AI understands my workflow"
        - "I don't have to translate data myself"
        - "My time is valued"

        Args:
            data: Raw data to be handed off
            recipient_role: Role of the person receiving the data
            context: Context of the handoff (e.g., "meeting_prep", "report")

        Returns:
            Formatted data optimized for recipient's workflow

        Example:
            >>> data = {"tasks": [...], "metrics": {...}}
            >>> formatted = behaviors.pre_format_for_handoff(
            ...     data=data,
            ...     recipient_role="executive",
            ...     context="board_meeting"
            ... )
            >>> # Returns: executive summary format with key highlights
        """
        logger.info(f"Pre-formatting data for handoff to {recipient_role} (context: {context})")

        formatted = {
            "original_data": data,
            "format": self._determine_format(recipient_role, context),
            "timestamp": datetime.now().isoformat(),
            "reasoning": f"Pre-formatted for {recipient_role} workflow",
        }

        # Format based on recipient role and context
        if recipient_role in ["executive", "manager", "director"]:
            formatted["summary"] = self._create_executive_summary(data, context)

        elif recipient_role in ["developer", "engineer", "analyst"]:
            formatted["summary"] = self._create_technical_summary(data, context)

        elif recipient_role in ["team_lead", "coordinator", "supervisor"]:
            formatted["summary"] = self._create_action_oriented_summary(data, context)

        else:
            # Generic format for unknown roles
            formatted["summary"] = self._create_generic_summary(data, context)

        # Record trust signal
        self._record_trust_signal(
            signal_type="building",
            behavior="pre_format_handoff",
            evidence=f"Formatted data for {recipient_role}",
        )

        return formatted

    def clarify_before_acting(
        self,
        instruction: str,
        detected_ambiguities: list[str],
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Clarify ambiguous instructions before execution to prevent wasted effort

        **Trust Built:**
        - "This AI doesn't make dangerous assumptions"
        - "It asks when uncertain (intelligent caution)"
        - "My intent is understood, not just command followed"

        Args:
            instruction: The instruction received
            detected_ambiguities: List of ambiguous aspects
            context: Optional additional context

        Returns:
            Clarification request with specific questions

        Example:
            >>> instruction = "Deploy the changes"
            >>> ambiguities = ["which environment?", "which changes?", "when?"]
            >>> clarification = behaviors.clarify_before_acting(
            ...     instruction=instruction,
            ...     detected_ambiguities=ambiguities
            ... )
        """
        logger.info(f"Clarifying ambiguous instruction: {instruction}")

        clarification = {
            "original_instruction": instruction,
            "status": "needs_clarification",
            "ambiguities_detected": detected_ambiguities,
            "clarifying_questions": [],
            "reasoning": (
                "Detected ambiguities in instruction. Clarifying before acting "
                "to prevent wasted effort or incorrect execution."
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # Generate specific clarifying questions
        for ambiguity in detected_ambiguities:
            question = self._generate_clarifying_question(instruction, ambiguity, context)
            clarification["clarifying_questions"].append(question)

        # Record trust signal
        self._record_trust_signal(
            signal_type="building",
            behavior="clarify_ambiguity",
            evidence=f"Asked for clarification on {len(detected_ambiguities)} ambiguities",
        )

        return clarification

    def volunteer_structure_during_stress(
        self, stress_indicators: dict[str, Any], available_scaffolding: list[str]
    ) -> dict[str, Any]:
        """
        Volunteer structure/scaffolding during stressful situations

        **Not pep talks, actual structural help:**
        - Break down overwhelming tasks
        - Provide templates
        - Create checklists
        - Suggest prioritization frameworks

        **Trust Built:**
        - "This AI provides real help, not platitudes"
        - "It understands when I'm overwhelmed"
        - "It offers structure, not just encouragement"

        Args:
            stress_indicators: Dict of detected stress signals
            available_scaffolding: List of support types available

        Returns:
            Structured support offer

        Example:
            >>> stress = {"task_count": 15, "deadline_proximity": "24h"}
            >>> scaffolding = ["prioritization", "templates", "breakdown"]
            >>> support = behaviors.volunteer_structure_during_stress(
            ...     stress_indicators=stress,
            ...     available_scaffolding=scaffolding
            ... )
        """
        logger.info("Volunteering structure during detected stress")

        stress_level = self._assess_stress_level(stress_indicators)

        support = {
            "stress_assessment": {"level": stress_level, "indicators": stress_indicators},
            "offered_support": [],
            "reasoning": (
                f"Detected {stress_level} stress. Volunteering structural support "
                "to reduce cognitive load and provide actionable scaffolding."
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # Offer appropriate scaffolding based on stress level
        if stress_level in ["high", "critical"]:
            if "prioritization" in available_scaffolding:
                support["offered_support"].append(
                    {
                        "type": "prioritization",
                        "description": "Help prioritize tasks using urgency-importance matrix",
                        "immediate": True,
                    }
                )

            if "breakdown" in available_scaffolding:
                support["offered_support"].append(
                    {
                        "type": "task_breakdown",
                        "description": "Break overwhelming tasks into smaller, manageable steps",
                        "immediate": True,
                    }
                )

        if "templates" in available_scaffolding:
            support["offered_support"].append(
                {
                    "type": "templates",
                    "description": "Provide templates to reduce creation effort",
                    "immediate": False,
                }
            )

        # Record trust signal
        self._record_trust_signal(
            signal_type="building",
            behavior="volunteer_structure",
            evidence=f"Offered {len(support['offered_support'])} types of structural support",
        )

        return support

    def offer_proactive_help(
        self, struggle_indicators: dict[str, Any], available_help: list[str]
    ) -> dict[str, Any]:
        """
        Proactively offer help when collaborator is struggling

        **Trust Built:**
        - "This AI notices when I'm stuck"
        - "It offers help without waiting to be asked"
        - "It doesn't overstep, but is ready to assist"

        Args:
            struggle_indicators: Signals that someone is struggling
            available_help: Types of help available

        Returns:
            Help offer tailored to situation

        Example:
            >>> indicators = {"repeated_errors": 3, "time_on_task": 45}
            >>> help_types = ["debugging", "explanation", "examples"]
            >>> offer = behaviors.offer_proactive_help(
            ...     struggle_indicators=indicators,
            ...     available_help=help_types
            ... )
        """
        logger.info("Offering proactive help based on struggle indicators")

        struggle_type = self._classify_struggle(struggle_indicators)

        offer = {
            "struggle_assessment": {"type": struggle_type, "indicators": struggle_indicators},
            "help_offered": [],
            "tone": "supportive_not_condescending",
            "reasoning": (
                f"Detected {struggle_type} struggle pattern. Offering relevant help "
                "proactively while respecting autonomy."
            ),
            "timestamp": datetime.now().isoformat(),
        }

        # Offer appropriate help based on struggle type
        if struggle_type == "comprehension":
            if "explanation" in available_help:
                offer["help_offered"].append(
                    {"type": "explanation", "description": "Provide clearer explanation of concept"}
                )
            if "examples" in available_help:
                offer["help_offered"].append(
                    {"type": "examples", "description": "Show concrete examples"}
                )

        elif struggle_type == "execution":
            if "debugging" in available_help:
                offer["help_offered"].append(
                    {"type": "debugging", "description": "Help debug the issue"}
                )
            if "guidance" in available_help:
                offer["help_offered"].append(
                    {"type": "step_by_step", "description": "Provide step-by-step guidance"}
                )

        # Record trust signal
        self._record_trust_signal(
            signal_type="building",
            behavior="proactive_help",
            evidence=f"Offered help for {struggle_type} struggle",
        )

        return offer

    def get_trust_trajectory(self) -> dict[str, Any]:
        """
        Get trust trajectory based on recorded signals

        Returns:
            Analysis of trust evolution over time
        """
        if not self.trust_signals:
            return {"status": "insufficient_data", "trajectory": "unknown", "signal_count": 0}

        building_count = sum(1 for s in self.trust_signals if s.signal_type == "building")
        eroding_count = sum(1 for s in self.trust_signals if s.signal_type == "eroding")

        total = len(self.trust_signals)
        building_ratio = building_count / total if total > 0 else 0

        if building_ratio > 0.7:
            trajectory = "strongly_building"
        elif building_ratio > 0.5:
            trajectory = "building"
        elif building_ratio > 0.3:
            trajectory = "mixed"
        else:
            trajectory = "eroding"

        return {
            "status": "active",
            "trajectory": trajectory,
            "signal_count": total,
            "building_signals": building_count,
            "eroding_signals": eroding_count,
            "building_ratio": building_ratio,
            "recent_behaviors": [s.behavior for s in self.trust_signals[-5:]],
        }

    # Helper methods

    def _determine_format(self, role: str, context: str) -> str:
        """Determine appropriate format based on role and context"""
        if role in ["executive", "manager", "director"]:
            return "executive_summary"
        elif role in ["developer", "engineer", "analyst"]:
            return "technical_detail"
        elif role in ["team_lead", "coordinator"]:
            return "action_oriented"
        else:
            return "general"

    def _create_executive_summary(self, data: dict, context: str) -> dict:
        """Create executive summary format"""
        return {
            "type": "executive_summary",
            "key_metrics": self._extract_key_metrics(data),
            "highlights": self._extract_highlights(data),
            "recommendations": self._extract_recommendations(data),
            "context": context,
        }

    def _create_technical_summary(self, data: dict, context: str) -> dict:
        """Create technical summary format"""
        return {
            "type": "technical_detail",
            "details": data,
            "technical_notes": self._extract_technical_notes(data),
            "context": context,
        }

    def _create_action_oriented_summary(self, data: dict, context: str) -> dict:
        """Create action-oriented summary format"""
        return {
            "type": "action_oriented",
            "immediate_actions": self._extract_immediate_actions(data),
            "priorities": self._extract_priorities(data),
            "context": context,
        }

    def _create_generic_summary(self, data: dict, context: str) -> dict:
        """Create generic summary format"""
        return {"type": "general", "summary": str(data), "context": context}

    def _extract_key_metrics(self, data: dict) -> list[str]:
        """Extract key metrics from data"""
        metrics = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                metrics.append(f"{key}: {value}")
        return metrics[:5]  # Top 5 metrics

    def _extract_highlights(self, data: dict) -> list[str]:
        """Extract highlights from data"""
        return [f"Data contains {len(data)} fields"]

    def _extract_recommendations(self, data: dict) -> list[str]:
        """Extract recommendations from data"""
        return ["Review detailed data for full context"]

    def _extract_technical_notes(self, data: dict) -> list[str]:
        """Extract technical notes"""
        return [f"Data structure: {type(data).__name__}"]

    def _extract_immediate_actions(self, data: dict) -> list[str]:
        """Extract immediate actions"""
        if "actions" in data:
            return data["actions"][:5]
        return ["Review data and determine next steps"]

    def _extract_priorities(self, data: dict) -> list[str]:
        """Extract priorities"""
        if "priorities" in data:
            return data["priorities"]
        return []

    def _generate_clarifying_question(
        self, instruction: str, ambiguity: str, context: dict | None
    ) -> dict[str, str]:
        """Generate a specific clarifying question"""
        return {
            "ambiguity": ambiguity,
            "question": f"Could you clarify: {ambiguity}",
            "context": str(context) if context else "none",
        }

    def _assess_stress_level(self, indicators: dict) -> str:
        """Assess stress level from indicators"""
        # Simple heuristic: count stress indicators
        stress_score = len(indicators)

        if stress_score >= 4:
            return "critical"
        elif stress_score >= 3:
            return "high"
        elif stress_score >= 2:
            return "moderate"
        else:
            return "low"

    def _classify_struggle(self, indicators: dict) -> str:
        """Classify type of struggle"""
        if "repeated_errors" in indicators:
            return "execution"
        elif "time_on_task" in indicators:
            return "comprehension"
        else:
            return "general"

    def _record_trust_signal(self, signal_type: str, behavior: str, evidence: str | None = None):
        """Record a trust signal"""
        signal = TrustSignal(signal_type=signal_type, behavior=behavior, evidence=evidence)
        self.trust_signals.append(signal)

    def reset(self):
        """Reset trust tracking"""
        self.trust_signals = []
