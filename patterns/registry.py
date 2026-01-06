"""Pattern Registry for the Wizard Factory.

The Pattern Registry is the central system for discovering, searching, and
recommending wizard patterns. It loads all extracted patterns and provides
intelligent pattern matching for new wizard creation.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from .behavior import (
    AIEnhancementPattern,
    FixApplicationPattern,
    PredictionPattern,
    RiskAssessmentPattern,
    RiskLevel,
)
from .core import BasePattern, PatternCategory
from .empathy import EducationalBannerPattern, EmpathyLevelPattern, UserGuidancePattern
from .input import (
    CodeAnalysisPattern,
    ContextBasedPattern,
    FieldDefinition,
    StructuredFieldsPattern,
)
from .structural import (
    LinearFlowPattern,
    PhaseConfig,
    PhasedProcessingPattern,
    SessionBasedPattern,
    StepConfig,
)
from .validation import ApprovalPattern, ConfigValidationPattern, StepValidationPattern

logger = logging.getLogger(__name__)


class PatternRegistry:
    """Central registry for all wizard patterns.

    The registry provides:
    - Pattern storage and retrieval by ID
    - Search by category, name, or description
    - Pattern recommendation based on wizard type and domain
    - Statistics on pattern usage
    """

    def __init__(self):
        """Initialize empty registry."""
        self._patterns: dict[str, BasePattern] = {}
        self._by_category: dict[PatternCategory, list[BasePattern]] = {
            cat: [] for cat in PatternCategory
        }

    def register(self, pattern: BasePattern) -> None:
        """Register a pattern in the registry.

        Args:
            pattern: Pattern to register

        Raises:
            ValueError: If pattern ID already exists

        """
        if pattern.id in self._patterns:
            raise ValueError(f"Pattern with ID '{pattern.id}' already registered")

        self._patterns[pattern.id] = pattern
        self._by_category[pattern.category].append(pattern)

        logger.debug(f"Registered pattern: {pattern.id} ({pattern.name})")

    def get(self, pattern_id: str) -> BasePattern | None:
        """Get pattern by ID.

        Args:
            pattern_id: Unique pattern identifier

        Returns:
            Pattern if found, None otherwise

        """
        return self._patterns.get(pattern_id)

    def list_all(self) -> list[BasePattern]:
        """List all registered patterns.

        Returns:
            List of all patterns

        """
        return list(self._patterns.values())

    def list_by_category(self, category: PatternCategory) -> list[BasePattern]:
        """List all patterns in a category.

        Args:
            category: Pattern category

        Returns:
            List of patterns in that category

        """
        return self._by_category[category].copy()

    def search(self, query: str, case_sensitive: bool = False) -> list[BasePattern]:
        """Search patterns by name or description.

        Args:
            query: Search query string
            case_sensitive: Whether search is case-sensitive

        Returns:
            List of matching patterns

        """
        if not case_sensitive:
            query = query.lower()

        results = []
        for pattern in self._patterns.values():
            name = pattern.name if case_sensitive else pattern.name.lower()
            desc = pattern.description if case_sensitive else pattern.description.lower()

            if query in name or query in desc:
                results.append(pattern)

        return results

    def recommend_for_wizard(
        self,
        wizard_type: str,
        domain: str | None = None,
    ) -> list[BasePattern]:
        """Recommend patterns for a new wizard.

        This uses a rule-based recommendation system based on:
        - Wizard type (domain, coach, ai)
        - Domain (healthcare, finance, legal, etc.)
        - Pattern frequency and reusability scores

        Args:
            wizard_type: Type of wizard (domain, coach, ai)
            domain: Optional domain (healthcare, finance, etc.)

        Returns:
            List of recommended patterns ordered by relevance

        """
        recommendations = []

        # Universal patterns (always recommended)
        recommendations.extend(
            [
                self.get("empathy_level"),
                self.get("user_guidance"),
            ]
        )

        # Healthcare domain patterns
        if domain == "healthcare":
            recommendations.extend(
                [
                    self.get("linear_flow"),
                    self.get("structured_fields"),
                    self.get("step_validation"),
                    self.get("approval"),
                    self.get("educational_banner"),
                    self.get("ai_enhancement"),
                ]
            )

        # Legal/Finance domains patterns
        elif domain in ["legal", "finance", "insurance"]:
            recommendations.extend(
                [
                    self.get("linear_flow"),
                    self.get("structured_fields"),
                    self.get("approval"),
                    self.get("educational_banner"),
                    self.get("config_validation"),
                ]
            )

        # Coach wizard patterns
        if wizard_type == "coach":
            recommendations.extend(
                [
                    self.get("code_analysis_input"),
                    self.get("risk_assessment"),
                    self.get("prediction"),
                    self.get("config_validation"),
                ]
            )

        # AI wizard patterns
        elif wizard_type == "ai":
            recommendations.extend(
                [
                    self.get("phased_processing"),
                    self.get("context_based_input"),
                    self.get("risk_assessment"),
                    self.get("fix_application"),
                ]
            )

        # Domain wizard patterns
        elif wizard_type == "domain":
            recommendations.extend(
                [
                    self.get("config_validation"),
                    self.get("session_based"),
                ]
            )

        # Filter out None values and duplicates
        recommendations = [p for p in recommendations if p is not None]
        seen = set()
        unique_recommendations = []
        for pattern in recommendations:
            if pattern.id not in seen:
                seen.add(pattern.id)
                unique_recommendations.append(pattern)

        return unique_recommendations

    def get_statistics(self) -> dict[str, Any]:
        """Get registry statistics.

        Returns:
            Dictionary with statistics

        """
        total_patterns = len(self._patterns)
        by_category = {cat.value: len(patterns) for cat, patterns in self._by_category.items()}

        # Calculate average reusability
        avg_reusability = (
            sum(p.reusability_score for p in self._patterns.values()) / total_patterns
            if total_patterns > 0
            else 0.0
        )

        # Get most frequently used patterns
        top_patterns = sorted(self._patterns.values(), key=lambda p: p.frequency, reverse=True)[:5]

        return {
            "total_patterns": total_patterns,
            "by_category": by_category,
            "average_reusability": avg_reusability,
            "top_patterns": [
                {"id": p.id, "name": p.name, "frequency": p.frequency} for p in top_patterns
            ],
        }


# Global registry instance
_registry: PatternRegistry | None = None


def get_pattern_registry() -> PatternRegistry:
    """Get the global pattern registry.

    Returns:
        Global PatternRegistry instance

    """
    global _registry
    if _registry is None:
        _registry = PatternRegistry()
        load_patterns(_registry)
    return _registry


def load_patterns(registry: PatternRegistry) -> None:
    """Load all extracted patterns into registry.

    This function loads all 15 patterns extracted from the 78 existing wizards.

    Args:
        registry: Pattern registry to load patterns into

    """
    logger.info("Loading patterns from existing wizards...")

    # =========================================================================
    # Structural Patterns (3)
    # =========================================================================

    # Linear Flow Pattern
    registry.register(
        LinearFlowPattern(
            id="linear_flow",
            name="Linear Flow",
            description="Step-by-step wizard with review and approval",
            frequency=16,
            reusability_score=0.9,
            examples=["soap_note", "sbar", "shift_handoff", "care_plan"],
            total_steps=5,
            steps={
                1: StepConfig(
                    step=1,
                    title="Step 1",
                    prompt="Complete step 1",
                    fields=["field1", "field2"],
                    help_text="Help for step 1",
                ),
                2: StepConfig(
                    step=2,
                    title="Step 2",
                    prompt="Complete step 2",
                    fields=["field3", "field4"],
                    help_text="Help for step 2",
                ),
                3: StepConfig(
                    step=3,
                    title="Step 3",
                    prompt="Complete step 3",
                    fields=["field5"],
                    help_text="Help for step 3",
                ),
                4: StepConfig(
                    step=4,
                    title="Step 4",
                    prompt="Complete step 4",
                    fields=["field6", "field7"],
                    help_text="Help for step 4",
                ),
                5: StepConfig(
                    step=5,
                    title="Review & Finalize",
                    prompt="Review and approve",
                    fields=["review_complete", "user_approved"],
                    help_text="Review all sections before finalizing",
                    is_review_step=True,
                ),
            },
            requires_approval=True,
            session_storage="redis",
        )
    )

    # Phased Processing Pattern
    registry.register(
        PhasedProcessingPattern(
            id="phased_processing",
            name="Phased Processing",
            description="Multi-phase analysis pipeline",
            frequency=12,
            reusability_score=0.85,
            examples=["advanced_debugging", "security_analysis", "performance_profiling"],
            phases=[
                PhaseConfig(
                    name="parse",
                    description="Parse and extract structured data from input",
                    required=True,
                ),
                PhaseConfig(
                    name="load_config",
                    description="Load wizard and tool configuration",
                    required=True,
                ),
                PhaseConfig(
                    name="analyze",
                    description="Perform core analysis",
                    required=True,
                ),
                PhaseConfig(
                    name="fix",
                    description="Apply fixes or transformations",
                    required=False,
                ),
                PhaseConfig(
                    name="verify",
                    description="Verify results and confirm success",
                    required=False,
                ),
            ],
        )
    )

    # Session-Based Pattern
    registry.register(
        SessionBasedPattern(
            id="session_based",
            name="Session-Based",
            description="State management with session storage",
            frequency=16,
            reusability_score=0.95,
            examples=["soap_note", "sbar", "care_plan"],
            session_ttl_seconds=7200,
            storage_backend="both",
        )
    )

    # =========================================================================
    # Input Patterns (3)
    # =========================================================================

    # Structured Fields Pattern
    registry.register(
        StructuredFieldsPattern(
            id="structured_fields",
            name="Structured Fields",
            description="Predefined fields per step with validation",
            frequency=16,
            reusability_score=0.9,
            examples=["soap_note", "care_plan", "admission_assessment"],
            fields_by_step={
                1: [
                    FieldDefinition(
                        name="chief_complaint",
                        field_type="str",
                        required=True,
                        description="Primary complaint",
                    ),
                    FieldDefinition(
                        name="history_present_illness",
                        field_type="str",
                        required=True,
                        description="History of present illness",
                    ),
                ],
                2: [
                    FieldDefinition(
                        name="vital_signs",
                        field_type="str",
                        required=True,
                        description="Vital signs measurement",
                    ),
                ],
            },
        )
    )

    # Code Analysis Pattern
    registry.register(
        CodeAnalysisPattern(
            id="code_analysis_input",
            name="Code Analysis Input",
            description="Standard code analysis input (code, file_path, language)",
            frequency=16,
            reusability_score=0.9,
            examples=["debugging", "testing", "security", "refactoring"],
            supported_languages=["python", "javascript", "typescript", "java", "go", "rust"],
            returns_issues=True,
        )
    )

    # Context-Based Pattern
    registry.register(
        ContextBasedPattern(
            id="context_based_input",
            name="Context-Based Input",
            description="Flexible dictionary-based input",
            frequency=12,
            reusability_score=0.8,
            examples=["advanced_debugging", "multi_model", "rag_pattern"],
            required_keys=["project_path"],
            optional_keys=["linters", "configs", "auto_fix", "verify"],
            key_descriptions={
                "project_path": "Path to project root",
                "linters": "Linter outputs to analyze",
                "auto_fix": "Whether to apply auto-fixes",
            },
        )
    )

    # =========================================================================
    # Validation Patterns (3)
    # =========================================================================

    # Config Validation Pattern
    registry.register(
        ConfigValidationPattern(
            id="config_validation",
            name="Config Validation",
            description="Validate wizard configuration on initialization",
            frequency=16,
            reusability_score=0.9,
            examples=["healthcare", "finance", "legal"],
            validation_rules=["empathy_level", "classification", "api_keys"],
            fail_fast=True,
        )
    )

    # Step Validation Pattern
    registry.register(
        StepValidationPattern(
            id="step_validation",
            name="Step Validation",
            description="Ensure steps are completed in order",
            frequency=16,
            reusability_score=0.9,
            examples=["soap_note", "sbar", "care_plan"],
            allow_step_skipping=False,
            allow_step_revisiting=True,
        )
    )

    # Approval Pattern
    registry.register(
        ApprovalPattern(
            id="approval",
            name="User Approval",
            description="Preview → Explicit Approval → Finalize",
            frequency=16,
            reusability_score=0.95,
            examples=["soap_note", "sbar", "discharge_summary"],
            requires_preview=True,
            approval_field="user_approved",
            allow_edits_after_preview=True,
        )
    )

    # =========================================================================
    # Behavior Patterns (4)
    # =========================================================================

    # Risk Assessment Pattern
    registry.register(
        RiskAssessmentPattern(
            id="risk_assessment",
            name="Risk Assessment",
            description="Level 4 Anticipatory risk analysis",
            frequency=16,
            reusability_score=0.8,
            examples=["debugging", "security", "testing"],
            risk_levels=[
                RiskLevel(
                    name="critical",
                    threshold=1,
                    alert_message="Critical issues detected",
                ),
                RiskLevel(
                    name="high",
                    threshold=5,
                    alert_message="High-risk issues accumulating",
                ),
                RiskLevel(
                    name="medium",
                    threshold=20,
                    alert_message="Medium issues detected",
                ),
            ],
        )
    )

    # AI Enhancement Pattern
    registry.register(
        AIEnhancementPattern(
            id="ai_enhancement",
            name="AI Enhancement",
            description="Improve user input with AI",
            frequency=16,
            reusability_score=0.7,
            examples=["soap_note", "sbar", "care_plan"],
            enhancement_guidelines=[
                "Use appropriate terminology",
                "Clear and concise language",
                "Maintain professional tone",
            ],
        )
    )

    # Prediction Pattern
    registry.register(
        PredictionPattern(
            id="prediction",
            name="Prediction",
            description="Level 4 Anticipatory prediction of future issues",
            frequency=16,
            reusability_score=0.8,
            examples=["debugging", "testing", "security"],
            timeline_days=90,
            prediction_types=[
                "production_failure_risk",
                "bug_density_increase",
                "technical_debt_accumulation",
            ],
        )
    )

    # Fix Application Pattern
    registry.register(
        FixApplicationPattern(
            id="fix_application",
            name="Fix Application",
            description="Automatically fix detected issues",
            frequency=8,
            reusability_score=0.75,
            examples=["advanced_debugging", "code_review"],
            auto_fix_enabled=False,
            dry_run_by_default=True,
            supported_fix_types=["lint", "format", "import", "refactor"],
        )
    )

    # =========================================================================
    # Empathy Patterns (2)
    # =========================================================================

    # Empathy Level Pattern
    registry.register(
        EmpathyLevelPattern(
            id="empathy_level",
            name="Empathy Level",
            description="0-4 empathy level configuration",
            frequency=16,
            reusability_score=1.0,
            examples=["healthcare", "finance", "legal"],
            default_level=2,
            level_descriptions={
                0: "Pure data/computation",
                1: "Reactive",
                2: "Responsive",
                3: "Proactive",
                4: "Anticipatory",
            },
            allow_user_override=True,
        )
    )

    # Educational Banner Pattern
    registry.register(
        EducationalBannerPattern(
            id="educational_banner",
            name="Educational Banner",
            description="Safety notices and educational content",
            frequency=16,
            reusability_score=1.0,
            examples=["soap_note", "sbar", "care_plan"],
            banner_text=(
                "This wizard is an educational tool. "
                "All output should be reviewed by qualified professionals."
            ),
            banner_type="educational",
            display_locations=["start", "report", "preview"],
            can_dismiss=False,
        )
    )

    # User Guidance Pattern (not registered - docs only)
    registry.register(
        UserGuidancePattern(
            id="user_guidance",
            name="User Guidance",
            description="Help text, examples, and prompts",
            frequency=78,  # All wizards should have this
            reusability_score=1.0,
            examples=["all wizards"],
            help_text_per_step={},
            field_examples={},
            contextual_prompts=False,
        )
    )

    logger.info(f"Loaded {len(registry.list_all())} patterns")
