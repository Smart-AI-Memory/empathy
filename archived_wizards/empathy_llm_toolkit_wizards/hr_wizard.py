"""
HR/Recruiting Wizard - Employee Privacy Compliant AI Assistant

Specialized wizard for human resources with enhanced employee PII protection,
employment law compliance, and comprehensive audit logging.

Key Features:
- Enhanced employee PII detection (employee IDs, compensation, benefits)
- Automatic de-identification before LLM processing
- Mandatory encryption for all employee data
- 7-year retention for employment records
- Comprehensive audit trail
- EEOC and employment law compliance
- Automatic classification as SENSITIVE

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# HR/employee PII patterns
HR_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # HR-specific PII
    "employee_id",
    "salary_info",
    "compensation",
    "benefits_id",
    "performance_review",
    "disciplinary_record",
]


class HRWizard(BaseWizard):
    """
    Employee privacy compliant HR AI assistant

    Implements defense-in-depth security for employee records:
    1. Enhanced employee PII detection and scrubbing
    2. Secrets detection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import HRWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = HRWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me draft a job description for software engineer",
        ...     user_id="hr@company.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize employee privacy compliant HR wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional company-specific PII patterns
        """
        pii_patterns = HR_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="HR Assistant",
            description="Employee privacy compliant AI assistant for human resources",
            domain="hr",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for employment records
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "HRWizard initialized with security DISABLED. "
                "Employee privacy compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"HRWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build employee privacy aware system prompt"""
        return """You are an employee privacy compliant AI HR assistant.

**Domain**: Human Resources / Talent Management

**Your Role**:
- Assist HR professionals with recruiting and talent acquisition
- Support employee relations and performance management
- Help with policy development and compliance
- Provide guidance on benefits and compensation

**Employee Privacy**:
- All employee information is automatically de-identified before you see it
- Never request or display employee names, IDs, salaries, or performance data
- Maintain strict confidentiality of personnel records
- All interactions comply with employment privacy laws

**HR Guidelines**:
- Base recommendations on employment law and best practices
- Acknowledge EEOC and anti-discrimination requirements
- Suggest inclusive and equitable approaches
- Follow company policies and legal requirements

**Communication Style**:
- Professional and confidential
- Clear and compliant
- Fair and equitable
- Employee-focused

**Important Disclaimers**:
- You are an HR support tool, not a replacement for HR professional judgment
- Cannot make hiring, termination, or compensation decisions
- Always defer to HR professionals and legal counsel for final decisions
- Recommendations should comply with employment laws and company policies

Remember: Employee privacy and employment law compliance are paramount. All interactions are logged for compliance and audit purposes.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of HR PII patterns being detected"""
        return self.config.pii_patterns.copy()
