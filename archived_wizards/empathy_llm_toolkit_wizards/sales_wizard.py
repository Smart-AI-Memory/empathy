"""Sales/Marketing Wizard - CRM Privacy Compliant AI Assistant

Specialized wizard for sales and marketing with customer PII protection,
CRM data handling, and comprehensive audit logging.

Key Features:
- Customer PII detection and protection
- Lead and opportunity tracking
- Campaign data handling
- Comprehensive audit trail
- Sales compliance
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Sales/marketing PII patterns
SALES_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "address",
    "ip_address",
    # Sales-specific
    "customer_id",
    "lead_id",
    "opportunity_id",
    "account_number",
]


class SalesWizard(BaseWizard):
    """CRM privacy compliant sales and marketing AI assistant

    Implements customer PII protection for sales operations:
    1. Customer PII detection and scrubbing
    2. CRM data protection
    3. Encryption for sensitive customer data
    4. Comprehensive audit logging
    5. 3-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import SalesWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = SalesWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me draft an email for this prospect",
        ...     user_id="sales@company.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize sales/marketing wizard

        Args:
            llm: EmpathyLLM instance (security recommended)
            custom_pii_patterns: Additional company-specific PII patterns

        """
        pii_patterns = SALES_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Sales & Marketing Assistant",
            description="CRM privacy compliant AI assistant for sales and marketing",
            domain="sales",
            default_empathy_level=4,  # Anticipatory - predicts customer needs
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=1095,  # 3 years
            default_classification="INTERNAL",
            auto_classify=True,
        )

        super().__init__(llm, config)

        logger.info(
            f"SalesWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build sales/marketing system prompt"""
        return """You are a CRM privacy compliant AI sales and marketing assistant.

**Domain**: Sales / Marketing / Business Development

**Your Role**:
- Assist sales professionals with lead qualification and opportunity management
- Support marketing campaigns and customer engagement
- Help draft communications and proposals
- Provide market insights and competitive intelligence

**Customer Privacy**:
- All customer PII is automatically de-identified before you see it
- Never request or display customer names, emails, or contact information
- Maintain customer confidentiality at all times
- Focus on value creation and relationship building

**Sales & Marketing Guidelines**:
- Prioritize customer value and long-term relationships
- Provide data-driven insights and recommendations
- Follow ethical sales practices
- Comply with CAN-SPAM, GDPR, and marketing regulations

**Communication Style**:
- Professional and persuasive
- Clear and compelling
- Customer-focused
- Results-oriented

**Important Disclaimers**:
- You are a sales support tool, not a replacement for sales judgment
- Cannot make pricing, contract, or deal approval decisions
- Always defer to sales leadership for strategic decisions
- Recommendations should align with company policies and legal requirements

Remember: Customer trust and privacy are paramount. All interactions are logged for compliance and performance tracking.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of sales/marketing PII patterns being detected"""
        return self.config.pii_patterns.copy()
