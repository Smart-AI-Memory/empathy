"""Behavior patterns for wizard capabilities.

Behavior patterns define what wizards can do beyond basic data collection:
- Risk Assessment: Level 4 Anticipatory risk analysis
- AI Enhancement: Improve user input with AI
- Prediction: Predict future issues (Level 4)
- Fix Application: Automatically fix detected issues

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Literal

from pydantic import BaseModel, Field

from .core import BasePattern, CodeGeneratorMixin, PatternCategory


class RiskLevel(BaseModel):
    """Definition of a risk level."""

    name: str = Field(..., description="Risk level name (e.g., 'critical', 'high')")
    threshold: int = Field(..., description="Issue count threshold for this level", ge=0)
    alert_message: str = Field(..., description="Alert message when threshold exceeded")


class RiskAssessmentPattern(BasePattern, CodeGeneratorMixin):
    """Level 4 Anticipatory risk assessment pattern.

    **Description:**
    Wizards that analyze issues and predict which ones will cause problems.
    This implements Level 4 Anticipatory Empathy by forecasting future failures.

    **Usage:** 16 wizards (all coach wizards)
    **Reusability:** 0.8

    **Risk Levels:**
    - CRITICAL: Will cause production failures (>0 critical issues)
    - HIGH: High probability of bugs (>5 high-risk issues)
    - MEDIUM: Moderate concern (>20 medium issues)
    - LOW: Minor issues

    **Output:**
    {
        "alert_level": "CRITICAL",
        "by_risk_level": {"critical": 5, "high": 12, "medium": 8},
        "predictions": [...],
        "recommendations": [...],
    }
    """

    category: Literal[PatternCategory.BEHAVIOR] = PatternCategory.BEHAVIOR
    risk_levels: list[RiskLevel] = Field(
        default_factory=lambda: [
            RiskLevel(
                name="critical",
                threshold=1,
                alert_message="Critical issues detected - production failure likely",
            ),
            RiskLevel(
                name="high",
                threshold=5,
                alert_message="High-risk issues accumulating - bugs probable",
            ),
            RiskLevel(
                name="medium",
                threshold=20,
                alert_message="Medium issues detected - quality degrading",
            ),
        ],
        description="Risk level definitions with thresholds",
    )

    def generate_code(self) -> str:
        """Generate risk assessment code."""
        return '''
class RiskAnalyzer:
    """Analyze issues for risk levels"""

    def __init__(self):
        self.risk_levels = ["critical", "high", "medium", "low"]

    def analyze(self, issues: list) -> dict[str, Any]:
        """Analyze issues and assess risk.

        Args:
            issues: List of issues to analyze

        Returns:
            Risk assessment with alert level and breakdown
        """
        # Count by risk level
        by_level = {level: 0 for level in self.risk_levels}

        for issue in issues:
            severity = issue.get("severity", "low")
            if severity in by_level:
                by_level[severity] += 1

        # Determine alert level
        alert_level = self._determine_alert_level(by_level)

        return {
            "alert_level": alert_level,
            "by_risk_level": by_level,
            "total_issues": len(issues),
        }

    def _determine_alert_level(self, by_level: dict[str, int]) -> str:
        """Determine overall alert level"""
        if by_level["critical"] > 0:
            return "CRITICAL"
        elif by_level["high"] > 5:
            return "HIGH"
        elif by_level["medium"] > 20:
            return "MEDIUM"
        else:
            return "LOW"
'''


class AIEnhancementPattern(BasePattern, CodeGeneratorMixin):
    """AI text enhancement pattern.

    **Description:**
    Wizards that use AI to improve user-provided text. Common in healthcare
    wizards where users provide rough notes and AI enhances them with:
    - Professional medical terminology
    - Proper formatting
    - Clarity improvements
    - Grammar/spelling fixes

    **Usage:** 16 wizards (all healthcare wizards)
    **Reusability:** 0.7

    **Endpoint:**
    POST /{wizard_id}/enhance
    Body: {"text": "...", "field": "chief_complaint"}

    **Enhancement Guidelines:**
    - Preserve original meaning
    - Use domain-appropriate terminology
    - Maintain professional tone
    - Follow documentation standards
    """

    category: Literal[PatternCategory.BEHAVIOR] = PatternCategory.BEHAVIOR
    enhancement_guidelines: list[str] = Field(
        default_factory=lambda: [
            "Use appropriate clinical terminology",
            "Clear and concise language",
            "Maintain professional tone",
            "Preserve all key information",
            "Follow documentation standards",
        ],
        description="Guidelines for AI enhancement",
    )

    def generate_code(self) -> str:
        """Generate AI enhancement endpoint."""
        guidelines = "\n".join(f"- {g}" for g in self.enhancement_guidelines)

        return f'''
@router.post("/{{wizard_id}}/enhance")
async def enhance_text(wizard_id: str, text_data: dict[str, Any]):
    """Enhance user text with AI

    Args:
        wizard_id: Wizard session ID
        text_data: {{"text": "...", "field": "field_name"}}

    Returns:
        Enhanced text
    """
    session = await _get_session(wizard_id)
    if not session:
        raise HTTPException(404, "Wizard session not found")

    original_text = text_data.get("text", "")
    field_name = text_data.get("field", "text")

    if not original_text:
        raise HTTPException(422, "No text provided for enhancement")

    # Get chat service
    chat_service = get_service("chat")

    # Enhancement prompt
    prompt = f"""
You are assisting with documentation. Please enhance the following text:

Field: {{field_name}}
Original: {{original_text}}

Enhancement guidelines:
{guidelines}

Enhanced text:"""

    response = await chat_service.chat(
        message=prompt,
        conversation_id=f"enhance_{{wizard_id}}",
        context={{"wizard_id": wizard_id, "field": field_name}},
    )

    return {{
        "original_text": original_text,
        "enhanced_text": response.get("response", original_text),
        "field": field_name,
    }}
'''


class PredictionPattern(BasePattern):
    """Level 4 Anticipatory prediction pattern.

    **Description:**
    Wizards that predict future issues before they occur. This implements
    Level 4 Anticipatory Empathy by forecasting problems.

    **Usage:** 16 wizards (all coach wizards)
    **Reusability:** 0.8

    **Prediction Types:**
    - production_failure_risk: Critical issues → runtime errors
    - bug_density_increase: High-risk accumulation → more bugs
    - technical_debt_accumulation: Code quality degradation
    - test_maintenance_burden: Flaky tests → maintenance overhead

    **Signature:**
    def predict_future_issues(
        self,
        code: str,
        file_path: str,
        project_context: dict,
        timeline_days: int = 90
    ) -> list[WizardPrediction]
    """

    category: Literal[PatternCategory.BEHAVIOR] = PatternCategory.BEHAVIOR
    timeline_days: int = Field(
        default=90,
        description="Prediction timeline in days",
        ge=1,
        le=365,
    )
    prediction_types: list[str] = Field(
        default_factory=lambda: [
            "production_failure_risk",
            "bug_density_increase",
            "technical_debt_accumulation",
        ],
        description="Types of predictions this wizard makes",
    )


class FixApplicationPattern(BasePattern):
    """Automatic fix application pattern.

    **Description:**
    Wizards that can automatically fix detected issues. Issues are grouped
    into auto-fixable and manual categories.

    **Usage:** 8 wizards (AI wizards with code modification)
    **Reusability:** 0.75

    **Workflow:**
    1. Detect issues
    2. Group by fixability (auto vs manual)
    3. Apply auto-fixes if enabled
    4. Track success/failure per fix

    **Auto-Fixable Examples:**
    - Linting issues (ruff --fix)
    - Import sorting (isort)
    - Code formatting (black)
    - Simple refactorings

    **Manual-Only Examples:**
    - Architecture changes
    - Logic bugs
    - Security vulnerabilities
    """

    category: Literal[PatternCategory.BEHAVIOR] = PatternCategory.BEHAVIOR
    auto_fix_enabled: bool = Field(
        default=False,
        description="Whether auto-fix is enabled by default",
    )
    dry_run_by_default: bool = Field(
        default=True,
        description="Whether to dry-run fixes before applying",
    )
    supported_fix_types: list[str] = Field(
        default_factory=lambda: ["lint", "format", "import", "refactor"],
        description="Types of fixes this wizard supports",
    )
