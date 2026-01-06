"""Validation patterns for wizard data integrity.

Validation patterns ensure wizard data is correct and authorized:
- Config Validation: Validate wizard configuration on initialization
- Step Validation: Ensure steps are completed in order
- User Approval: Require explicit user consent before finalization

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Literal

from pydantic import Field

from .core import BasePattern, CodeGeneratorMixin, PatternCategory


class ConfigValidationPattern(BasePattern, CodeGeneratorMixin):
    """Configuration validation pattern.

    **Description:**
    Wizards validate their configuration during initialization to fail fast
    if misconfigured.

    **Usage:** 16 wizards (all domain wizards)
    **Reusability:** 0.9

    **Validation Checks:**
    - Empathy level in range (0-4)
    - Classification valid (PUBLIC, INTERNAL, SENSITIVE)
    - Required API keys present
    - File paths exist

    **Example:**
    def _validate_config(self):
        if not 0 <= self.config.empathy_level <= 4:
            raise ValueError("Empathy level must be 0-4")
    """

    category: Literal[PatternCategory.VALIDATION] = PatternCategory.VALIDATION
    validation_rules: list[str] = Field(
        default_factory=list,
        description="List of validation rules to check",
    )
    fail_fast: bool = Field(
        default=True,
        description="Whether to raise immediately on validation failure",
    )

    def generate_code(self) -> str:
        """Generate _validate_config() method."""
        return '''
    def _validate_config(self):
        """Validate wizard configuration.

        Raises:
            ValueError: If configuration is invalid

        """
        if not 0 <= self.config.default_empathy_level <= 4:
            raise ValueError(
                f"Empathy level must be 0-4, got {self.config.default_empathy_level}"
            )

        if self.config.default_classification not in ["PUBLIC", "INTERNAL", "SENSITIVE"]:
            raise ValueError(
                f"Invalid classification: {self.config.default_classification}"
            )

        # Add custom validation rules here
'''


class StepValidationPattern(BasePattern, CodeGeneratorMixin):
    """Step sequence validation pattern.

    **Description:**
    Multi-step wizards validate that steps are completed in the correct order.
    Users cannot skip steps or submit the wrong step.

    **Usage:** 16 wizards (all healthcare wizards)
    **Reusability:** 0.9

    **Validation:**
    - Current step matches submitted step
    - Previous steps completed
    - Step number in valid range

    **HTTP Status Codes:**
    - 422 Unprocessable Entity: Wrong step submitted
    - 400 Bad Request: Step out of range
    """

    category: Literal[PatternCategory.VALIDATION] = PatternCategory.VALIDATION
    allow_step_skipping: bool = Field(
        default=False,
        description="Whether users can skip steps",
    )
    allow_step_revisiting: bool = Field(
        default=True,
        description="Whether users can go back to previous steps",
    )

    def generate_code(self) -> str:
        """Generate step validation code."""
        return """
    # Validate step sequence
    submitted_step = step_data.get("step", current_step)

    if submitted_step != current_step:
        raise HTTPException(
            status_code=422,
            detail=f"Expected step {current_step}, got step {submitted_step}"
        )

    if submitted_step < 1 or submitted_step > total_steps:
        raise HTTPException(
            status_code=400,
            detail=f"Step must be between 1 and {total_steps}"
        )
"""


class ApprovalPattern(BasePattern, CodeGeneratorMixin):
    """User approval before finalization pattern.

    **Description:**
    Critical wizards require explicit user approval before finalizing output.
    This follows a Preview → Approve → Finalize workflow.

    **Usage:** 16 wizards (all healthcare wizards)
    **Reusability:** 0.95

    **Workflow:**
    1. User completes all steps
    2. POST /preview - Generate preview (NOT finalized)
    3. User reviews preview
    4. POST /save with user_approved=True - Finalize

    **Safety Guarantees:**
    - Cannot save without preview
    - Cannot save without explicit approval
    - Preview generation never finalizes
    """

    category: Literal[PatternCategory.VALIDATION] = PatternCategory.VALIDATION
    requires_preview: bool = Field(
        default=True,
        description="Whether preview is required before approval",
    )
    approval_field: str = Field(
        default="user_approved",
        description="Field name for approval boolean",
    )
    allow_edits_after_preview: bool = Field(
        default=True,
        description="Whether user can edit after previewing",
    )

    def generate_code(self) -> str:
        """Generate save endpoint with approval check."""
        return f'''
@router.post("/{{wizard_id}}/save")
async def save_report(wizard_id: str, approval_data: dict[str, Any]):
    """Finalize report with user approval"""
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    # Verify preview was generated
    if "preview_report" not in session:
        raise HTTPException(
            400,
            "Must generate preview before saving. Call /preview endpoint first."
        )

    # Verify user explicitly approved
    if not approval_data.get("{self.approval_field}", False):
        raise HTTPException(
            400,
            "User approval required. Set '{self.approval_field}': true"
        )

    # NOW we mark as complete
    session["completed"] = True
    session["completed_at"] = datetime.now().isoformat()
    session["final_report"] = session["preview_report"]
    session["{self.approval_field}"] = True

    await _store_session(wizard_id, session)

    return {{"report": session["final_report"], "completed": True}}
'''
