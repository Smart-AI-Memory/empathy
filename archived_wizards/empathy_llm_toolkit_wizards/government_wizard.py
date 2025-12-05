"""
Government/Compliance Wizard - Regulatory Compliance AI Assistant

Specialized wizard for government and regulatory work with citizen PII protection,
FISMA compliance, and comprehensive audit logging.

Key Features:
- Citizen PII detection and protection
- FISMA and FedRAMP compliance
- Regulatory data handling
- Comprehensive audit trail
- Government security requirements
- Automatic classification as SENSITIVE

Reference:
- FISMA (Federal Information Security Management Act)
- Privacy Act of 1974
- FedRAMP requirements

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Government PII patterns
GOVERNMENT_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # Government-specific
    "agency_id",
    "case_number",
    "permit_number",
    "license_number",
]


class GovernmentWizard(BaseWizard):
    """
    FISMA-compliant government and regulatory AI assistant

    Implements defense-in-depth security for government data:
    1. Citizen PII detection and scrubbing
    2. Secrets detection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention (government records)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import GovernmentWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = GovernmentWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me analyze this regulatory compliance issue",
        ...     user_id="analyst@agency.gov"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize government/compliance wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional agency-specific PII patterns
        """
        pii_patterns = GOVERNMENT_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Government & Compliance Assistant",
            description="FISMA-compliant AI assistant for government and regulatory work",
            domain="government",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for government records
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "GovernmentWizard initialized with security DISABLED. "
                "FISMA compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"GovernmentWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build government/compliance system prompt"""
        return """You are a FISMA-compliant AI government and regulatory assistant.

**Domain**: Government / Public Sector / Regulatory Compliance

**Your Role**:
- Assist government professionals with policy analysis and compliance
- Support regulatory enforcement and investigation
- Help with citizen services and case management
- Provide guidance on government regulations and procedures

**Privacy**:
- All citizen information is automatically de-identified before you see it
- Never request or display citizen names, SSNs, or case numbers
- Maintain strict confidentiality of government data
- All interactions comply with Privacy Act and FISMA

**Government Guidelines**:
- Base recommendations on applicable laws and regulations
- Acknowledge jurisdictional requirements and precedents
- Provide accurate regulatory interpretation
- Follow government security and privacy standards

**Communication Style**:
- Professional and authoritative
- Clear and compliant
- Public service-oriented
- Transparent

**Important Disclaimers**:
- You are a government support tool, not a replacement for official decisions
- Cannot make enforcement, permitting, or adjudication decisions
- Not a substitute for legal counsel or agency authority
- Always defer to authorized officials for final decisions

Remember: Citizen privacy and government security are paramount. All interactions are logged for FISMA compliance and audit requirements.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of government PII patterns being detected"""
        return self.config.pii_patterns.copy()
