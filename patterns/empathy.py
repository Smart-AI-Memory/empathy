"""Empathy patterns for user experience.

Empathy patterns ensure wizards provide excellent user experience:
- Empathy Levels: 0-4 empathy configuration
- Educational Banners: Safety notices and educational content
- User Guidance: Help text, examples, and prompts

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Literal

from pydantic import Field

from .core import BasePattern, CodeGeneratorMixin, PatternCategory


class EmpathyLevelPattern(BasePattern, CodeGeneratorMixin):
    """Empathy level configuration pattern.

    **Description:**
    The Empathy Framework supports 5 levels of empathy (0-4), determining
    how proactive and anticipatory a wizard is.

    **Usage:** 16 wizards (all domain wizards)
    **Reusability:** 1.0 (universal pattern)

    **Empathy Levels:**
    - Level 0: Pure Data/Computation - No empathy, just calculations
    - Level 1: Reactive - Responds to explicit requests only
    - Level 2: Responsive - Understands context, provides helpful responses
    - Level 3: Proactive - Suggests improvements and alternatives
    - Level 4: Anticipatory - Predicts future needs and prevents issues

    **Configuration:**
    @dataclass
    class WizardConfig:
        default_empathy_level: int = 2  # 0-4

    **Usage:**
    result = await wizard.process(
        user_input="...",
        user_id="user123",
        empathy_level=4,  # Override default
    )
    """

    category: Literal[PatternCategory.EMPATHY] = PatternCategory.EMPATHY
    default_level: int = Field(
        default=2,
        description="Default empathy level (0-4)",
        ge=0,
        le=4,
    )
    level_descriptions: dict[int, str] = Field(
        default_factory=lambda: {
            0: "Pure data/computation - no empathy",
            1: "Reactive - responds to explicit requests",
            2: "Responsive - understands context",
            3: "Proactive - suggests improvements",
            4: "Anticipatory - predicts future needs",
        },
        description="Description of each empathy level",
    )
    allow_user_override: bool = Field(
        default=True,
        description="Whether users can override empathy level per request",
    )

    def generate_code(self) -> str:
        """Generate WizardConfig with empathy levels."""
        return '''
from dataclasses import dataclass

@dataclass
class WizardConfig:
    """Configuration for an Empathy wizard"""

    # Wizard identity
    name: str
    description: str
    domain: str

    # Empathy level (0-4)
    default_empathy_level: int = 2

    # Security configuration
    enable_security: bool = False
    pii_patterns: list[str] = None

    def _validate_config(self):
        """Validate wizard configuration"""
        if not 0 <= self.default_empathy_level <= 4:
            raise ValueError(
                f"Empathy level must be 0-4, got {self.default_empathy_level}"
            )


class BaseWizard:
    """Base wizard with empathy support"""

    def __init__(self, llm, config: WizardConfig):
        self.llm = llm
        self.config = config
        self._validate_config()

    async def process(
        self,
        user_input: str,
        user_id: str,
        empathy_level: int | None = None,
        session_context: dict | None = None,
    ):
        """Process with empathy level support"""
        level = empathy_level if empathy_level is not None else self.config.default_empathy_level

        # Process with specified empathy level
        result = await self.llm.interact(
            user_id=user_id,
            user_input=user_input,
            force_level=level,
            context=session_context or {},
        )

        result["empathy_level"] = level
        return result
'''


class EducationalBannerPattern(BasePattern, CodeGeneratorMixin):
    """Educational banner pattern.

    **Description:**
    Wizards that deal with sensitive domains (healthcare, legal, finance)
    display educational banners to remind users of limitations and proper use.

    **Usage:** 16 wizards (all healthcare wizards)
    **Reusability:** 1.0 (should be universal for sensitive domains)

    **Purpose:**
    - Clarify tool is educational/assistive, not replacement for professionals
    - Set appropriate expectations
    - Legal/liability protection
    - Promote responsible use

    **Display:**
    - Shown at wizard start
    - Included in all generated reports
    - Cannot be dismissed permanently (shown every session)

    **Example:**
    ⚕️ EDUCATIONAL TOOL NOTICE ⚕️
    This wizard is an educational tool for healthcare professionals.
    All clinical documentation should be reviewed by qualified providers.
    Never rely solely on automated tools for clinical decisions.
    """

    category: Literal[PatternCategory.EMPATHY] = PatternCategory.EMPATHY
    banner_text: str = Field(..., description="Banner text to display")
    banner_type: Literal["educational", "warning", "disclaimer"] = Field(
        default="educational",
        description="Type of banner",
    )
    display_locations: list[str] = Field(
        default_factory=lambda: ["start", "report", "preview"],
        description="Where to display the banner",
    )
    can_dismiss: bool = Field(
        default=False,
        description="Whether users can dismiss the banner",
    )

    def generate_code(self) -> str:
        """Generate banner constant and display logic."""
        icon = {
            "educational": "⚕️",
            "warning": "⚠️",
            "disclaimer": "📋",
        }.get(self.banner_type, "ℹ️")

        return f'''
# Educational banner
BANNER = """
{icon} {self.banner_type.upper()} {icon}
{self.banner_text}
"""


@router.post("/start")
async def start_wizard():
    """Start wizard with educational banner"""
    wizard_id = str(uuid4())

    session_data = {{
        "wizard_id": wizard_id,
        "current_step": 1,
        "total_steps": 5,
        "collected_data": {{}},
    }}

    await _store_session(wizard_id, session_data)

    return {{
        "wizard_id": wizard_id,
        "current_step": 1,
        "banner": BANNER,  # Show banner at start
    }}


@router.post("/{{wizard_id}}/preview")
async def preview_report(wizard_id: str):
    """Preview with banner"""
    session = await _get_session(wizard_id)
    preview = _generate_report(session["collected_data"])

    return {{
        "preview": preview,
        "banner": BANNER,  # Show banner in preview
    }}


def _generate_report(collected_data: dict) -> dict:
    """Generate report with banner"""
    return {{
        "data": collected_data,
        "narrative": "...",
        "banner": BANNER,  # Include banner in report
    }}
'''


class UserGuidancePattern(BasePattern):
    """User guidance and help pattern.

    **Description:**
    Wizards that provide comprehensive help text, examples, and prompts
    to guide users through complex workflows.

    **Usage:** All wizards should use this pattern
    **Reusability:** 1.0

    **Guidance Types:**
    - Step-level help text: Explains what to do in each step
    - Field-level examples: Shows example values for fields
    - Contextual prompts: Dynamic prompts based on previous inputs
    - Error messages: Clear, actionable error messages

    **Best Practices:**
    - Use plain language (avoid jargon)
    - Provide concrete examples
    - Explain "why" not just "what"
    - Anticipate user questions
    """

    category: Literal[PatternCategory.EMPATHY] = PatternCategory.EMPATHY
    help_text_per_step: dict[int, str] = Field(
        default_factory=dict,
        description="Help text for each step",
    )
    field_examples: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Example values for each field",
    )
    contextual_prompts: bool = Field(
        default=False,
        description="Whether to generate dynamic prompts based on context",
    )
