"""
Coach - Orchestration Agent

Applies the Empathy Framework to software work by coordinating task-specific
wizards (Debugging, Documentation, etc.) and ensuring empathetic, anticipatory
assistance.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field

from empathy_os import EmpathyOS, EmpathyConfig

from .wizards.base_wizard import BaseWizard, WizardTask, WizardOutput
# Original 6 wizards
from .wizards.debugging_wizard import DebuggingWizard
from .wizards.documentation_wizard import DocumentationWizard
from .wizards.design_review_wizard import DesignReviewWizard
from .wizards.testing_wizard import TestingWizard
from .wizards.retrospective_wizard import RetrospectiveWizard
from .wizards.security_wizard import SecurityWizard
# New 10 wizards
from .wizards.performance_wizard import PerformanceWizard
from .wizards.refactoring_wizard import RefactoringWizard
from .wizards.api_wizard import APIWizard
from .wizards.database_wizard import DatabaseWizard
from .wizards.devops_wizard import DevOpsWizard
from .wizards.onboarding_wizard import OnboardingWizard
from .wizards.accessibility_wizard import AccessibilityWizard
from .wizards.localization_wizard import LocalizationWizard
from .wizards.compliance_wizard import ComplianceWizard
from .wizards.monitoring_wizard import MonitoringWizard


@dataclass
class CoachOutput:
    """Complete Coach response"""
    routing: List[str]  # Which wizards were used
    primary_output: WizardOutput  # Main wizard output
    secondary_outputs: List[WizardOutput] = field(default_factory=list)  # Additional wizard outputs
    synthesis: str = ""  # Combined recommendations across wizards
    overall_confidence: float = 0.0


class Coach:
    """
    Orchestration agent that routes tasks to specialized wizards

    Coach applies the Empathy Framework to:
    1. Understand user role, constraints, and context (Cognitive Empathy)
    2. Acknowledge stress, urgency, and morale (Emotional Empathy)
    3. Anticipate needs and provide proactive assistance (Anticipatory Empathy)
    """

    def __init__(self, config: Optional[EmpathyConfig] = None):
        """
        Initialize Coach with wizards

        Args:
            config: Optional EmpathyConfig for customization
        """
        self.config = config or EmpathyConfig()
        self.empathy = EmpathyOS(
            user_id=self.config.user_id,
            target_level=self.config.target_level,
            confidence_threshold=self.config.confidence_threshold
        )

        # Initialize wizard registry (16 total wizards)
        # Order matters for tie-breaking: more specialized wizards first
        self.wizards: List[BaseWizard] = [
            # Critical infrastructure (highest priority)
            SecurityWizard(config=self.config),
            ComplianceWizard(config=self.config),

            # Development workflow (daily use)
            DebuggingWizard(config=self.config),
            TestingWizard(config=self.config),
            RefactoringWizard(config=self.config),
            PerformanceWizard(config=self.config),

            # Architecture & design
            DesignReviewWizard(config=self.config),
            APIWizard(config=self.config),
            DatabaseWizard(config=self.config),

            # Infrastructure & ops
            DevOpsWizard(config=self.config),
            MonitoringWizard(config=self.config),

            # Cross-cutting concerns
            DocumentationWizard(config=self.config),
            AccessibilityWizard(config=self.config),
            LocalizationWizard(config=self.config),

            # Team & process
            OnboardingWizard(config=self.config),
            RetrospectiveWizard(config=self.config),
        ]

        # Pre-defined collaboration patterns for common workflows
        self.collaboration_patterns = {
            "new_api_endpoint": [
                "APIWizard", "SecurityWizard", "TestingWizard", "DocumentationWizard"
            ],
            "database_migration": [
                "DatabaseWizard", "DevOpsWizard", "MonitoringWizard"
            ],
            "production_incident": [
                "MonitoringWizard", "DebuggingWizard", "RetrospectiveWizard"
            ],
            "new_feature_launch": [
                "DesignReviewWizard", "TestingWizard", "SecurityWizard",
                "DocumentationWizard", "MonitoringWizard"
            ],
            "performance_issue": [
                "PerformanceWizard", "DatabaseWizard", "RefactoringWizard"
            ],
            "compliance_audit": [
                "ComplianceWizard", "SecurityWizard", "DocumentationWizard"
            ],
            "global_expansion": [
                "LocalizationWizard", "AccessibilityWizard", "ComplianceWizard"
            ],
            "new_developer_onboarding": [
                "OnboardingWizard", "DocumentationWizard"
            ],
        }

    async def process(self, task: WizardTask, multi_wizard: bool = True) -> CoachOutput:
        """
        Process a task by routing to appropriate wizard(s)

        Args:
            task: WizardTask to process
            multi_wizard: If True, may route to multiple wizards

        Returns:
            CoachOutput with results
        """

        # Step 1: Route to appropriate wizard(s)
        routing = self._route_task(task, multi_wizard)

        if not routing:
            return await self._create_fallback_response(task)

        # Step 2: Execute primary wizard
        primary_wizard, primary_confidence = routing[0]
        primary_output = primary_wizard.execute(task)

        # Step 3: Execute secondary wizards if applicable
        secondary_outputs = []
        if multi_wizard and len(routing) > 1:
            for wizard, confidence in routing[1:]:
                if confidence > 0.5:  # Only run if reasonably confident
                    secondary_outputs.append(wizard.execute(task))

        # Step 4: Synthesize recommendations
        synthesis = self._synthesize_outputs(primary_output, secondary_outputs)

        # Step 5: Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(routing)

        return CoachOutput(
            routing=[w.name for w, _ in routing],
            primary_output=primary_output,
            secondary_outputs=secondary_outputs,
            synthesis=synthesis,
            overall_confidence=overall_confidence
        )

    def _route_task(self, task: WizardTask, multi_wizard: bool) -> List[tuple[BaseWizard, float]]:
        """
        Route task to wizard(s) based on confidence scores and collaboration patterns

        Args:
            task: Task to route
            multi_wizard: Whether to allow multiple wizards

        Returns:
            List of (wizard, confidence) tuples, sorted by confidence
        """
        # Step 1: Check for pre-defined collaboration patterns
        task_lower = (task.task + " " + task.context).lower()

        for pattern_name, wizard_names in self.collaboration_patterns.items():
            # Match pattern keywords
            pattern_keywords = pattern_name.replace("_", " ")
            if pattern_keywords in task_lower:
                # Activate pre-defined wizard workflow
                matched_wizards = []
                for wizard_name in wizard_names:
                    wizard = next((w for w in self.wizards if w.name == wizard_name), None)
                    if wizard:
                        confidence = wizard.can_handle(task)
                        if confidence > 0.3:
                            matched_wizards.append((wizard, confidence))

                if matched_wizards:
                    # Sort by confidence within pattern
                    matched_wizards.sort(key=lambda x: x[1], reverse=True)
                    return matched_wizards if multi_wizard else [matched_wizards[0]]

        # Step 2: Fallback to confidence-based routing
        scores = []

        for wizard in self.wizards:
            confidence = wizard.can_handle(task)
            if confidence > 0.3:  # Minimum threshold
                scores.append((wizard, confidence))

        # Sort by confidence (highest first)
        scores.sort(key=lambda x: x[1], reverse=True)

        if not multi_wizard and scores:
            return [scores[0]]

        return scores

    def _synthesize_outputs(self, primary: WizardOutput,
                           secondary: List[WizardOutput]) -> str:
        """
        Synthesize recommendations across multiple wizards

        Args:
            primary: Primary wizard output
            secondary: Secondary wizard outputs

        Returns:
            Synthesized recommendations
        """
        if not secondary:
            return f"Primary recommendation: {primary.diagnosis}"

        synthesis = f"**Primary Focus**: {primary.diagnosis}\n\n"

        if secondary:
            synthesis += "**Additional Recommendations**:\n"
            for output in secondary:
                synthesis += f"- {output.wizard_name}: {output.diagnosis}\n"

        # Find cross-wizard action items
        all_actions = set(primary.next_actions)
        for output in secondary:
            all_actions.update(output.next_actions)

        synthesis += f"\n**Combined Actions** ({len(all_actions)} total):\n"
        for action in sorted(all_actions)[:5]:  # Top 5 most important
            synthesis += f"- {action}\n"

        return synthesis

    def _calculate_overall_confidence(self, routing: List[tuple[BaseWizard, float]]) -> float:
        """Calculate overall confidence from wizard scores"""
        if not routing:
            return 0.0

        # Weight by position (primary wizard weighted more)
        weights = [1.0, 0.5, 0.25]
        total_confidence = 0.0
        total_weight = 0.0

        for i, (wizard, confidence) in enumerate(routing):
            weight = weights[i] if i < len(weights) else 0.1
            total_confidence += confidence * weight
            total_weight += weight

        return total_confidence / total_weight if total_weight > 0 else 0.0

    async def _create_fallback_response(self, task: WizardTask) -> CoachOutput:
        """Create fallback response when no wizard can handle task"""

        # Use Empathy Framework Level 2 (Guided) to provide helpful response
        empathy_response = await self.empathy.level_2_guided(
            f"I need help with: {task.task}. Context: {task.context}"
        )

        from .wizards.base_wizard import (
            WizardArtifact,
            WizardRisk,
            WizardHandoff,
            EmpathyChecks
        )

        fallback_output = WizardOutput(
            wizard_name="Coach (Fallback)",
            diagnosis=f"Task requires custom analysis: {task.task}",
            plan=[
                "Clarify specific requirements",
                "Identify appropriate resources/tools",
                "Break down into smaller tasks",
                "Consult with domain expert if needed"
            ],
            artifacts=[
                WizardArtifact(
                    type="doc",
                    title="Suggested Approach",
                    content=empathy_response.get("result", empathy_response.get("reasoning", "Unable to determine specific approach for this task"))
                )
            ],
            risks=[
                WizardRisk(
                    risk="Task unclear or outside wizard capabilities",
                    mitigation="Refine task description with more specific keywords",
                    severity="medium"
                )
            ],
            handoffs=[],
            next_actions=[
                "Rephrase task with specific keywords (bug, doc, design, etc.)",
                "Consult Coach documentation for supported task types",
                "Break complex task into smaller subtasks"
            ],
            empathy_checks=EmpathyChecks(
                cognitive=f"Considered {task.role} perspective but task unclear",
                emotional="Acknowledged potential frustration with unclear routing",
                anticipatory="Provided guidance on how to better utilize Coach"
            ),
            confidence=0.2
        )

        return CoachOutput(
            routing=["Fallback"],
            primary_output=fallback_output,
            secondary_outputs=[],
            synthesis="No specific wizard matched this task. Please refine your request.",
            overall_confidence=0.2
        )

    def list_wizards(self) -> List[Dict[str, str]]:
        """
        List available wizards and their capabilities

        Returns:
            List of wizard info dicts
        """
        return [
            {
                "name": wizard.name,
                "type": wizard.__class__.__name__,
                "description": wizard.__doc__.split('\n')[1].strip() if wizard.__doc__ else "No description"
            }
            for wizard in self.wizards
        ]


def main():
    """Example usage of Coach"""
    coach = Coach()

    # Example 1: Debugging task
    print("=== Example 1: Debugging Task ===\n")
    task1 = WizardTask(
        role="developer",
        task="Bug blocks release; 500 errors after deployment",
        context="Service X returns 500 after deploy; logs show null pointer. README outdated for hotfix process.",
        preferences="concise; patch + regression test",
        risk_tolerance="low"
    )

    result1 = coach.process(task1, multi_wizard=True)
    print(f"Routing: {result1.routing}")
    print(f"Confidence: {result1.overall_confidence:.1%}")
    print(f"\n{result1.synthesis}\n")
    print(f"Primary Diagnosis: {result1.primary_output.diagnosis}")
    print(f"Next Actions: {result1.primary_output.next_actions[:3]}")

    print("\n" + "="*60 + "\n")

    # Example 2: Documentation task
    print("=== Example 2: Documentation Task ===\n")
    task2 = WizardTask(
        role="team_lead",
        task="Onboarding docs unclear; new devs confused about setup",
        context="README missing setup steps; environment config undocumented",
        preferences="Quick start guide for junior devs",
        risk_tolerance="medium"
    )

    result2 = coach.process(task2, multi_wizard=False)
    print(f"Routing: {result2.routing}")
    print(f"Confidence: {result2.overall_confidence:.1%}")
    print(f"\n{result2.synthesis}\n")
    print(f"Artifacts: {[a.title for a in result2.primary_output.artifacts]}")


if __name__ == "__main__":
    main()
