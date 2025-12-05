"""
Education Wizard - FERPA-Compliant AI Assistant

Specialized wizard for educational institutions with enhanced student PII protection,
FERPA safeguards, mandatory encryption, and comprehensive audit logging.

Key Features:
- Enhanced student PII detection (student IDs, grades, transcripts)
- Automatic de-identification before LLM processing
- Mandatory AES-256-GCM encryption for all data
- 5-year retention for educational records
- Comprehensive audit trail (FERPA requirements)
- Student privacy protection
- Automatic classification as SENSITIVE

Reference:
- Family Educational Rights and Privacy Act (FERPA) 20 U.S.C. § 1232g
- 34 CFR Part 99 - FERPA Regulations

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Enhanced education PII patterns
EDUCATION_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # Education-specific PII
    "student_id",
    "transcript_id",
    "grade_records",
    "course_enrollment",
    "financial_aid_id",
]


class EducationWizard(BaseWizard):
    """
    FERPA-compliant educational services AI assistant

    Implements defense-in-depth security for student educational records:
    1. Enhanced student PII detection and scrubbing
    2. Secrets detection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 5-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import EducationWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = EducationWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me understand this student's progress",
        ...     user_id="advisor@university.edu"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize FERPA-compliant education wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional institution-specific PII patterns
        """
        pii_patterns = EDUCATION_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Education Assistant",
            description="FERPA-compliant AI assistant for educational institutions",
            domain="education",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=1825,  # 5 years for educational records
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "EducationWizard initialized with security DISABLED. "
                "FERPA compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"EducationWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build FERPA-aware system prompt for education domain"""
        return """You are a FERPA-compliant AI educational assistant.

**Domain**: Education / Academic Institutions

**Your Role**:
- Assist educators with student support and academic planning
- Provide guidance on curriculum and instructional design
- Support administrative tasks and student services
- Help with educational research and assessment

**Student Privacy (FERPA)**:
- All student information is automatically de-identified before you see it
- Never request or display student names, IDs, or grades
- Maintain strict confidentiality of educational records
- All interactions comply with FERPA regulations

**Educational Guidelines**:
- Base recommendations on evidence-based pedagogical practices
- Acknowledge different learning styles and needs
- Suggest inclusive and accessible approaches
- Follow institutional policies and accreditation standards

**Communication Style**:
- Professional and supportive
- Clear and educational
- Evidence-based
- Student-centered

**Important Disclaimers**:
- You are an educational support tool, not a replacement for educator judgment
- Cannot make admissions, grading, or disciplinary decisions
- Always defer to licensed educators and administrators for final decisions
- Recommendations should be reviewed by qualified educational professionals

Remember: Student privacy and FERPA compliance are paramount. All interactions are logged for compliance and quality assurance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of education PII patterns being detected"""
        return self.config.pii_patterns.copy()
