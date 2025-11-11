"""
Base Wizard Class

All wizards inherit from this base class and leverage the Empathy Framework
to provide empathetic, context-aware assistance.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from empathy_os import EmpathyConfig, EmpathyOS


@dataclass
class WizardTask:
    """Task input for a wizard"""

    role: str  # developer, architect, pm, team_lead
    task: str  # Short description
    context: str  # Links, code, constraints
    preferences: str = ""  # Format/style constraints
    risk_tolerance: str = "medium"  # low, medium, high
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WizardArtifact:
    """Output artifact from a wizard"""

    type: str  # doc, code, checklist, adr
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class WizardRisk:
    """Identified risk with mitigation"""

    risk: str
    mitigation: str
    severity: str = "medium"  # low, medium, high


@dataclass
class WizardHandoff:
    """Handoff to another person/role"""

    owner: str  # Role or person name
    what: str  # Deliverable
    when: str  # Timeframe


@dataclass
class EmpathyChecks:
    """Empathy framework validation"""

    cognitive: str  # Whose constraints were considered?
    emotional: str  # Acknowledged pressures/morale?
    anticipatory: str  # What proactive relief provided?


@dataclass
class WizardOutput:
    """Complete wizard output"""

    wizard_name: str
    diagnosis: str
    plan: list[str]
    artifacts: list[WizardArtifact]
    risks: list[WizardRisk]
    handoffs: list[WizardHandoff]
    next_actions: list[str]
    empathy_checks: EmpathyChecks
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)


class BaseWizard(ABC):
    """
    Base class for all Coach wizards

    Each wizard leverages the Empathy Framework to provide context-aware,
    empathetic assistance for specific types of tasks.
    """

    def __init__(self, config: EmpathyConfig | None = None):
        """
        Initialize wizard with Empathy Framework

        Args:
            config: Optional EmpathyConfig for customization
        """
        self.config = config or EmpathyConfig()
        self.empathy = EmpathyOS(
            user_id=self.config.user_id,
            target_level=self.config.target_level,
            confidence_threshold=self.config.confidence_threshold,
        )
        self.name = self.__class__.__name__

    @abstractmethod
    def can_handle(self, task: WizardTask) -> float:
        """
        Determine if this wizard can handle the task

        Args:
            task: WizardTask to evaluate

        Returns:
            Confidence score 0.0-1.0
        """
        pass

    @abstractmethod
    def execute(self, task: WizardTask) -> WizardOutput:
        """
        Execute the wizard's primary function

        Args:
            task: WizardTask to execute

        Returns:
            WizardOutput with results
        """
        pass

    def _apply_empathy_level(self, task: WizardTask, content: str) -> str:
        """
        Apply appropriate empathy level based on task complexity

        Args:
            task: Current task
            content: Content to process

        Returns:
            Empathy-enhanced content
        """
        # Determine appropriate empathy level based on risk and role
        if task.risk_tolerance == "low" or task.role in ["pm", "team_lead"]:
            # High-stakes: Use Level 4 (Anticipatory)
            result = self.empathy.level4_anticipatory(
                content, context={"role": task.role, "risk": task.risk_tolerance}
            )
        elif "bug" in task.task.lower() or "error" in task.task.lower():
            # Problem-solving: Use Level 3 (Proactive)
            result = self.empathy.level3_proactive(content, context={"issue": task.task})
        else:
            # Standard: Use Level 2 (Guided)
            result = self.empathy.level2_guided(content)

        return result["response"]

    def _extract_constraints(self, task: WizardTask) -> dict[str, Any]:
        """
        Extract constraints from task (cognitive empathy)

        Args:
            task: Task to analyze

        Returns:
            Dict of identified constraints
        """
        constraints = {
            "role": task.role,
            "risk_tolerance": task.risk_tolerance,
            "preferences": task.preferences,
        }

        # Parse preferences for additional constraints
        if "concise" in task.preferences.lower():
            constraints["output_style"] = "concise"
        if "patch" in task.preferences.lower():
            constraints["code_changes"] = "minimal"

        return constraints

    def _assess_emotional_state(self, task: WizardTask) -> dict[str, Any]:
        """
        Assess emotional context (emotional empathy)

        Args:
            task: Task to analyze

        Returns:
            Dict with emotional assessment
        """
        emotional_state = {"pressure": "normal", "urgency": "normal", "stress_indicators": []}

        # Detect high-pressure situations
        urgent_keywords = ["blocks", "urgent", "critical", "asap", "hotfix", "prod"]
        stress_keywords = ["frustrated", "confused", "stuck", "struggling"]

        task_lower = task.task.lower()
        context_lower = task.context.lower()

        for keyword in urgent_keywords:
            if keyword in task_lower or keyword in context_lower:
                emotional_state["urgency"] = "high"
                emotional_state["stress_indicators"].append(keyword)

        for keyword in stress_keywords:
            if keyword in task_lower or keyword in context_lower:
                emotional_state["pressure"] = "high"
                emotional_state["stress_indicators"].append(keyword)

        return emotional_state

    def _generate_anticipatory_actions(self, task: WizardTask) -> list[str]:
        """
        Generate proactive suggestions (anticipatory empathy)

        Args:
            task: Task to analyze

        Returns:
            List of anticipatory actions
        """
        actions = []

        # Based on role
        if task.role == "team_lead":
            actions.append("Pre-draft status update for stakeholders")
        if task.role == "pm":
            actions.append("Create timeline impact assessment")

        # Based on task type
        if "bug" in task.task.lower():
            actions.append("Add regression test to prevent recurrence")
        if "release" in task.task.lower():
            actions.append("Pre-fill release notes template")
        if "docs" in task.task.lower():
            actions.append("Create handoff checklist")

        # Based on risk
        if task.risk_tolerance == "low":
            actions.append("Include rollback plan in deliverable")

        return actions
