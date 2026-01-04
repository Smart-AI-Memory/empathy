"""Legal Wizard - Attorney-Client Privilege Compliant AI Assistant

Specialized wizard for legal services with enhanced PII protection,
attorney-client privilege safeguards, mandatory encryption, and comprehensive audit logging.

Key Features:
- Enhanced legal PII detection (case numbers, client IDs, docket numbers)
- Automatic de-identification before LLM processing
- Mandatory AES-256-GCM encryption for all data
- 7-year retention for legal compliance
- Comprehensive audit trail
- Attorney-client privilege protection
- Automatic classification as SENSITIVE

Reference:
- Attorney-client privilege (Federal Rules of Evidence 502)
- ABA Model Rules of Professional Conduct 1.6
- State bar confidentiality requirements

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Enhanced legal PII patterns
LEGAL_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "credit_card",
    "ip_address",
    # Legal-specific PII
    "case_number",
    "docket_number",
    "client_id",
    "matter_id",
    "bar_number",
    "court_file_number",
]


class LegalWizard(BaseWizard):
    """Attorney-client privilege compliant legal services AI assistant

    Implements defense-in-depth security for attorney-client communications:
    1. Enhanced legal PII detection and scrubbing
    2. Secrets detection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import LegalWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = LegalWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Analyze contract for case 2024-CV-1234",
        ...     user_id="attorney@lawfirm.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize attorney-client privilege compliant legal wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional firm-specific PII patterns

        """
        pii_patterns = LEGAL_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Legal Assistant",
            description="Attorney-client privilege compliant AI assistant for legal professionals",
            domain="legal",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "LegalWizard initialized with security DISABLED. "
                "Attorney-client privilege requires enable_security=True in EmpathyLLM.",
            )

        logger.info(
            f"LegalWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build attorney-client privilege aware system prompt"""
        return """You are an attorney-client privilege compliant AI legal assistant.

**Domain**: Legal Services / Law Practice

**Your Role**:
- Assist legal professionals with research and analysis
- Support case preparation and document review
- Help with legal writing and communication
- Provide general legal information and guidance

**Confidentiality**:
- All client information is automatically de-identified before you see it
- Never request or display case numbers, client names, or identifiers
- Maintain strict confidentiality in all communications
- All interactions protected by attorney-client privilege procedures

**Legal Guidelines**:
- Provide general legal information, not specific legal advice
- Base analysis on applicable laws and precedents
- Acknowledge jurisdictional variations
- Suggest consulting specialists for complex matters

**Communication Style**:
- Professional and precise
- Thorough and well-reasoned
- Cite relevant authorities when appropriate
- Clear about limitations and uncertainties

**Important Disclaimers**:
- You are a research and analysis tool, not a replacement for attorney judgment
- Cannot establish attorney-client relationship
- Not admitted to practice in any jurisdiction
- Always defer to licensed attorneys for final legal decisions

Remember: Client confidentiality and attorney-client privilege are paramount. All interactions are logged for compliance and quality assurance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of legal PII patterns being detected"""
        return self.config.pii_patterns.copy()
