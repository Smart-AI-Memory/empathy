"""Real Estate Wizard - Property Data Privacy Compliant AI Assistant

Specialized wizard for real estate with property and client PII protection,
MLS data handling, and comprehensive audit logging.

Key Features:
- Property and client PII detection
- MLS data protection
- Transaction tracking
- Comprehensive audit trail
- Real estate compliance
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Real estate PII patterns
REAL_ESTATE_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # Real estate-specific
    "mls_number",
    "parcel_id",
    "property_address",
    "client_id",
    "transaction_id",
]


class RealEstateWizard(BaseWizard):
    """Property data privacy compliant real estate AI assistant

    Implements PII protection for real estate operations:
    1. Property and client PII detection and scrubbing
    2. MLS data protection
    3. Encryption for sensitive data
    4. Comprehensive audit logging
    5. 7-year retention (transaction records)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import RealEstateWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = RealEstateWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me prepare a market analysis for this property",
        ...     user_id="agent@realty.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize real estate wizard

        Args:
            llm: EmpathyLLM instance (security recommended)
            custom_pii_patterns: Additional brokerage-specific PII patterns

        """
        pii_patterns = REAL_ESTATE_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Real Estate Assistant",
            description="Property data privacy compliant AI assistant for real estate",
            domain="real_estate",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for transaction records
            default_classification="INTERNAL",
            auto_classify=True,
        )

        super().__init__(llm, config)

        logger.info(
            f"RealEstateWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build real estate system prompt"""
        return """You are a property data privacy compliant AI real estate assistant.

**Domain**: Real Estate / Property Management

**Your Role**:
- Assist real estate professionals with property listings and marketing
- Support market analysis and valuation
- Help with transaction coordination
- Provide guidance on real estate regulations and best practices

**Privacy**:
- All client and property information is automatically de-identified before you see it
- Never request or display client names, addresses, or property details
- Maintain confidentiality of transaction information
- Focus on professional service and market insights

**Real Estate Guidelines**:
- Base recommendations on market data and industry standards
- Acknowledge local regulations and fair housing requirements
- Provide accurate property information
- Follow MLS rules and real estate law

**Communication Style**:
- Professional and knowledgeable
- Clear and informative
- Market-focused
- Client-oriented

**Important Disclaimers**:
- You are a real estate support tool, not a replacement for agent judgment
- Cannot make pricing, offer, or transaction decisions
- Not a licensed appraiser or inspector
- Always defer to licensed professionals for final decisions

Remember: Client confidentiality and fair housing compliance are paramount. All interactions are logged for compliance and quality assurance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of real estate PII patterns being detected"""
        return self.config.pii_patterns.copy()
