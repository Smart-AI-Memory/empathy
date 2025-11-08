"""
Five Levels of AI Empathy - Individual Level Classes

Provides concrete implementations for each empathy level:
- Level 1: Reactive Empathy (respond to explicit requests)
- Level 2: Guided Empathy (collaborative exploration)
- Level 3: Proactive Empathy (act before being asked)
- Level 4: Anticipatory Empathy (predict and prepare for future needs)
- Level 5: Systems Empathy (build structures that help at scale)

Each level represents increasing sophistication in understanding and
responding to human needs.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class EmpathyAction:
    """
    An action taken at a specific empathy level

    Records what action was taken, at what level, and the outcome.
    """

    level: int  # 1-5
    action_type: str
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    outcome: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class EmpathyLevel(ABC):
    """
    Abstract base class for empathy levels

    Each level implements specific behaviors appropriate to that
    level of empathy sophistication.
    """

    level_number: int
    level_name: str

    def __init__(self):
        self.actions_taken: List[EmpathyAction] = []

    @abstractmethod
    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond to a situation at this empathy level

        Args:
            context: Situation context

        Returns:
            Response appropriate to this level
        """
        pass

    def record_action(
        self,
        action_type: str,
        description: str,
        context: Dict[str, Any],
        outcome: Optional[str] = None,
    ):
        """Record an action taken at this level"""
        action = EmpathyAction(
            level=self.level_number,
            action_type=action_type,
            description=description,
            context=context,
            outcome=outcome,
        )
        self.actions_taken.append(action)

    def get_action_history(self) -> List[EmpathyAction]:
        """Get history of actions at this level"""
        return self.actions_taken


class Level1Reactive(EmpathyLevel):
    """
    Level 1: Reactive Empathy

    **Principle**: Help after being asked

    **Characteristics:**
    - Waits for explicit requests
    - Responds to direct questions
    - Provides what was asked for (nothing more)
    - Zero initiative or anticipation

    **Example:**
    - User: "What's the status of the project?"
    - AI: "The project is 60% complete."
    - (Stops there, doesn't volunteer next steps)

    **Appropriate When:**
    - User wants full control
    - Trust hasn't been established yet
    - Task is purely informational
    - Overstepping would be inappropriate

    Example:
        >>> level1 = Level1Reactive()
        >>> response = level1.respond({"request": "status", "subject": "project"})
        >>> print(response["action"])
        'provide_requested_information'
    """

    level_number = 1
    level_name = "Reactive Empathy"

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond reactively to explicit request

        Only provides what was directly asked for.
        """
        request = context.get("request", "unknown")
        subject = context.get("subject", "")

        response = {
            "level": self.level_number,
            "level_name": self.level_name,
            "action": "provide_requested_information",
            "description": f"Responding to request: {request}",
            "initiative": "none",
            "reasoning": "Level 1: Responding only to explicit request",
            "additional_offers": [],  # No proactive offers at Level 1
        }

        self.record_action(
            action_type="reactive_response",
            description=f"Responded to {request} about {subject}",
            context=context,
        )

        return response


class Level2Guided(EmpathyLevel):
    """
    Level 2: Guided Empathy

    **Principle**: Collaborative exploration with user input

    **Characteristics:**
    - Asks clarifying questions
    - Explores user needs together
    - Suggests options (doesn't decide alone)
    - Collaborative, not directive

    **Example:**
    - User: "I need to improve the system."
    - AI: "What aspects are you most concerned about? Performance,
           maintainability, or features? I can help with any of these."
    - (Guides exploration but lets user lead)

    **Appropriate When:**
    - Requirements are unclear
    - Multiple valid approaches exist
    - User expertise should guide direction
    - Building shared understanding

    Example:
        >>> level2 = Level2Guided()
        >>> response = level2.respond({
        ...     "request": "improve system",
        ...     "ambiguity": "high"
        ... })
        >>> print(len(response["clarifying_questions"]))
        3
    """

    level_number = 2
    level_name = "Guided Empathy"

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond with guided exploration

        Asks questions to understand needs and collaboratively explore solutions.
        """
        request = context.get("request", "")
        ambiguity = context.get("ambiguity", "medium")

        clarifying_questions = self._generate_clarifying_questions(request, ambiguity)

        response = {
            "level": self.level_number,
            "level_name": self.level_name,
            "action": "collaborative_exploration",
            "description": "Guiding exploration of needs through clarifying questions",
            "initiative": "guided",
            "clarifying_questions": clarifying_questions,
            "suggested_options": self._suggest_exploration_paths(request),
            "reasoning": "Level 2: Collaboratively exploring to understand needs",
        }

        self.record_action(
            action_type="guided_exploration",
            description=f"Asked {len(clarifying_questions)} clarifying questions",
            context=context,
        )

        return response

    def _generate_clarifying_questions(self, request: str, ambiguity: str) -> List[str]:
        """Generate clarifying questions based on ambiguity"""
        questions = [
            "What specific aspects are most important to you?",
            "What constraints should we consider?",
            "What does success look like for this?",
        ]

        if ambiguity == "high":
            questions.append("Can you help me understand the broader context?")

        return questions

    def _suggest_exploration_paths(self, request: str) -> List[str]:
        """Suggest paths for collaborative exploration"""
        return [
            "We could explore technical approaches",
            "We could focus on user impact",
            "We could analyze risks and tradeoffs",
        ]


class Level3Proactive(EmpathyLevel):
    """
    Level 3: Proactive Empathy

    **Principle**: Act before being asked (when confidence is high)

    **Characteristics:**
    - Takes initiative on obvious needs
    - Acts without explicit request
    - Stays within clear boundaries
    - Volunteers help for common pain points

    **Example:**
    - User commits code with failing tests
    - AI: "I noticed tests are failing. I've identified the 3 broken tests
           and can help fix them. Would you like me to proceed?"
    - (Takes initiative but asks permission for action)

    **Appropriate When:**
    - Need is obvious and low-risk
    - Pattern has been established
    - Action won't overstep boundaries
    - Can save significant time/effort

    Example:
        >>> level3 = Level3Proactive()
        >>> response = level3.respond({
        ...     "observed_need": "failing_tests",
        ...     "confidence": 0.9
        ... })
        >>> print(response["proactive_offer"])
    """

    level_number = 3
    level_name = "Proactive Empathy"

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond proactively to observed needs

        Takes initiative on obvious needs without being asked.
        """
        observed_need = context.get("observed_need", "unknown")
        confidence = context.get("confidence", 0.5)

        proactive_actions = self._identify_proactive_actions(observed_need, confidence)

        response = {
            "level": self.level_number,
            "level_name": self.level_name,
            "action": "proactive_assistance",
            "description": f"Proactively addressing: {observed_need}",
            "initiative": "proactive",
            "observed_need": observed_need,
            "confidence": confidence,
            "proactive_offer": proactive_actions,
            "reasoning": "Level 3: Taking initiative on obvious need",
        }

        self.record_action(
            action_type="proactive_action",
            description=f"Proactively offered help for {observed_need}",
            context=context,
        )

        return response

    def _identify_proactive_actions(self, need: str, confidence: float) -> Dict[str, Any]:
        """Identify appropriate proactive actions"""
        if confidence >= 0.8:
            permission_needed = False
            action = "Will proceed automatically"
        else:
            permission_needed = True
            action = "Offering to help, awaiting permission"

        return {
            "need_identified": need,
            "proposed_action": f"Address {need}",
            "permission_needed": permission_needed,
            "confidence_level": confidence,
            "action_plan": action,
        }


class Level4Anticipatory(EmpathyLevel):
    """
    Level 4: Anticipatory Empathy

    **Principle**: Predict and prepare for future needs

    **Characteristics:**
    - Predicts needs before they arise
    - Analyzes trajectories and trends
    - Prepares solutions in advance
    - Prevents problems proactively

    **Example:**
    - Compliance audit in 30 days
    - AI analyzes current state, predicts gaps that will exist in 30 days
    - Pre-generates compliance documentation
    - Alerts team to preventable issues
    - (Sees around corners, prevents future problems)

    **Appropriate When:**
    - Patterns are predictable
    - Preventing > Reacting
    - Can see trajectory clearly
    - High confidence in prediction

    **Real-world Example:**
    AI Nurse Florence predicts CMS compliance gaps 30 days before audit,
    giving hospital time to remediate (demonstrated Level 4).

    Example:
        >>> level4 = Level4Anticipatory()
        >>> response = level4.respond({
        ...     "current_state": {...},
        ...     "trajectory": "compliance_gap",
        ...     "prediction_horizon": "30_days"
        ... })
        >>> print(response["predicted_needs"])
    """

    level_number = 4
    level_name = "Anticipatory Empathy"

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond anticipatorily to predicted future needs

        Analyzes trajectory and prepares for future needs before they arise.
        """
        current_state = context.get("current_state", {})
        trajectory = context.get("trajectory", "unknown")
        horizon = context.get("prediction_horizon", "unknown")

        predictions = self._predict_future_needs(current_state, trajectory, horizon)

        response = {
            "level": self.level_number,
            "level_name": self.level_name,
            "action": "anticipatory_preparation",
            "description": f"Anticipating needs in {horizon}",
            "initiative": "anticipatory",
            "current_trajectory": trajectory,
            "prediction_horizon": horizon,
            "predicted_needs": predictions["needs"],
            "preventive_actions": predictions["actions"],
            "confidence": predictions["confidence"],
            "reasoning": "Level 4: Predicting and preparing for future needs",
        }

        self.record_action(
            action_type="anticipatory_preparation",
            description=f"Predicted {len(predictions['needs'])} future needs",
            context=context,
        )

        return response

    def _predict_future_needs(
        self, current_state: Dict[str, Any], trajectory: str, horizon: str
    ) -> Dict[str, Any]:
        """Predict future needs based on current trajectory"""
        # Simulate prediction logic
        predicted_needs = [
            f"Based on {trajectory} trajectory, will need X in {horizon}",
            "Current trend suggests Y will become bottleneck",
            "Preparation for Z should begin now",
        ]

        preventive_actions = [
            "Pre-generate required resources",
            "Alert stakeholders to predicted issues",
            "Prepare mitigation strategies",
        ]

        return {
            "needs": predicted_needs,
            "actions": preventive_actions,
            "confidence": 0.85,
            "prediction_basis": "trajectory_analysis",
        }


class Level5Systems(EmpathyLevel):
    """
    Level 5: Systems Empathy

    **Principle**: Build structures that help at scale

    **Characteristics:**
    - Creates reusable frameworks
    - Enables AI-AI cooperation
    - Shares patterns across agents
    - Builds systems that compound value

    **Example:**
    - One agent discovers documentation burden (18 cases)
    - Doesn't just solve each case individually
    - Creates a pattern-detection system
    - Shares pattern with other agents
    - All agents now benefit from discovery
    - (Solves the class of problems, not just instances)

    **Appropriate When:**
    - Pattern repeats across domains
    - Can help beyond current user
    - System-level solution exists
    - Value compounds over time

    **Real-world Example:**
    Instead of manually documenting each compliance gap, create a
    documentation framework that auto-generates from patterns.

    Example:
        >>> level5 = Level5Systems()
        >>> response = level5.respond({
        ...     "problem_class": "documentation_burden",
        ...     "instances": 18,
        ...     "pattern": "repetitive_structure"
        ... })
        >>> print(response["system_created"])
    """

    level_number = 5
    level_name = "Systems Empathy"

    def respond(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Respond with systems-level solution

        Creates reusable structures that help at scale.
        """
        problem_class = context.get("problem_class", "unknown")
        instances = context.get("instances", 0)
        pattern = context.get("pattern", None)

        system_design = self._design_system_solution(problem_class, instances, pattern)

        response = {
            "level": self.level_number,
            "level_name": self.level_name,
            "action": "systems_level_solution",
            "description": f"Creating system to solve {problem_class} at scale",
            "initiative": "systems_thinking",
            "problem_class": problem_class,
            "instances_addressed": instances,
            "system_created": system_design["system"],
            "leverage_point": system_design["leverage"],
            "compounding_value": system_design["value"],
            "ai_ai_sharing": system_design["sharing"],
            "reasoning": "Level 5: Building structures that help at scale",
        }

        self.record_action(
            action_type="systems_solution",
            description=f"Created system solution for {problem_class}",
            context=context,
        )

        return response

    def _design_system_solution(
        self, problem_class: str, instances: int, pattern: Optional[str]
    ) -> Dict[str, Any]:
        """Design a system-level solution"""
        return {
            "system": {
                "name": f"{problem_class}_framework",
                "description": f"Automated system to solve {problem_class}",
                "components": ["Pattern detection", "Auto-generation", "Shared learning library"],
            },
            "leverage": "Self-organization (Meadows Level 9)",
            "value": {
                "immediate": f"Solves {instances} existing instances",
                "compounding": "Each future instance solved automatically",
                "multiplier": "All agents benefit from pattern library",
            },
            "sharing": {
                "mechanism": "Pattern Library",
                "scope": "All agents in collective",
                "benefit": "One agent's discovery helps all",
            },
        }


# Convenience function to get level class by number
def get_level_class(level: int) -> type:
    """
    Get the class for a specific empathy level

    Args:
        level: Level number (1-5)

    Returns:
        Level class

    Example:
        >>> LevelClass = get_level_class(4)
        >>> level4 = LevelClass()
        >>> print(level4.level_name)
        'Anticipatory Empathy'
    """
    levels = {
        1: Level1Reactive,
        2: Level2Guided,
        3: Level3Proactive,
        4: Level4Anticipatory,
        5: Level5Systems,
    }
    return levels.get(level, Level1Reactive)
