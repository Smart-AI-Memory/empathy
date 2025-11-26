"""
Insurance Wizard - Policy Data Privacy Compliant AI Assistant

Specialized wizard for insurance with policyholder PII protection,
claims data handling, and comprehensive audit logging.

Key Features:
- Policyholder PII detection and protection
- Claims and policy data handling
- Underwriting data protection
- Comprehensive audit trail
- Insurance regulatory compliance
- Automatic classification as SENSITIVE

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Insurance PII patterns
INSURANCE_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "credit_card",
    "ip_address",
    # Insurance-specific
    "policy_number",
    "claim_number",
    "policyholder_id",
    "driver_license",
    "vin",  # Vehicle Identification Number
]


class InsuranceWizard(BaseWizard):
    """
    Policy data privacy compliant insurance AI assistant

    Implements PII protection for insurance operations:
    1. Policyholder PII detection and scrubbing
    2. Claims data protection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention (regulatory requirement)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import InsuranceWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = InsuranceWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me review this claim for policy coverage",
        ...     user_id="adjuster@insurance.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize insurance wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional carrier-specific PII patterns
        """
        pii_patterns = INSURANCE_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Insurance Assistant",
            description="Policy data privacy compliant AI assistant for insurance",
            domain="insurance",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for regulatory compliance
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "InsuranceWizard initialized with security DISABLED. "
                "Insurance compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"InsuranceWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build insurance system prompt"""
        return """You are a policy data privacy compliant AI insurance assistant.

**Domain**: Insurance / Risk Management

**Your Role**:
- Assist insurance professionals with policy analysis and underwriting
- Support claims processing and investigation
- Help with risk assessment and pricing
- Provide guidance on insurance regulations and compliance

**Privacy**:
- All policyholder information is automatically de-identified before you see it
- Never request or display policyholder names, policy numbers, or claim details
- Maintain strict confidentiality of insurance data
- All interactions comply with insurance privacy regulations

**Insurance Guidelines**:
- Base recommendations on actuarial principles and industry standards
- Acknowledge regulatory requirements and state variations
- Provide accurate policy interpretation
- Follow claims handling best practices

**Communication Style**:
- Professional and analytical
- Clear and precise
- Risk-aware
- Customer-focused

**Important Disclaimers**:
- You are an insurance support tool, not a replacement for underwriter/adjuster judgment
- Cannot make coverage, pricing, or claims decisions
- Not a licensed insurance professional
- Always defer to licensed professionals for final decisions

Remember: Policyholder privacy and regulatory compliance are paramount. All interactions are logged for compliance and audit purposes.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of insurance PII patterns being detected"""
        return self.config.pii_patterns.copy()
