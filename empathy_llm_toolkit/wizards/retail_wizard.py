"""
Retail/E-commerce Wizard - Customer Data Privacy Compliant AI Assistant

Specialized wizard for retail and e-commerce with customer PII protection,
PCI-DSS compliance for payment data, and comprehensive audit logging.

Key Features:
- Customer PII detection and protection
- PCI-DSS payment data compliance
- Order and transaction tracking
- Comprehensive audit trail
- E-commerce security requirements
- Automatic classification as SENSITIVE

Reference:
- PCI-DSS v4.0 Requirements
- GDPR for e-commerce
- Consumer privacy regulations

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Retail/e-commerce PII patterns
RETAIL_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "address",
    "credit_card",
    "ip_address",
    # Retail-specific
    "customer_id",
    "order_number",
    "tracking_number",
    "loyalty_id",
]


class RetailWizard(BaseWizard):
    """
    PCI-DSS compliant retail and e-commerce AI assistant

    Implements customer PII protection for retail operations:
    1. Customer PII detection and scrubbing
    2. Payment data protection (PCI-DSS)
    3. Encryption for sensitive customer data
    4. Comprehensive audit logging
    5. 2-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import RetailWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = RetailWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me analyze customer purchasing patterns",
        ...     user_id="analyst@retailer.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize retail/e-commerce wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional retailer-specific PII patterns
        """
        pii_patterns = RETAIL_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Retail & E-commerce Assistant",
            description="PCI-DSS compliant AI assistant for retail and e-commerce",
            domain="retail",
            default_empathy_level=4,  # Anticipatory - predicts customer needs
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=730,  # 2 years
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "RetailWizard initialized with security DISABLED. "
                "PCI-DSS compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"RetailWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build retail/e-commerce system prompt"""
        return """You are a PCI-DSS compliant AI retail and e-commerce assistant.

**Domain**: Retail / E-commerce / Consumer Goods

**Your Role**:
- Assist retail professionals with customer insights and merchandising
- Support inventory management and demand forecasting
- Help with marketing campaigns and promotions
- Provide guidance on e-commerce operations and optimization

**Customer Privacy**:
- All customer information is automatically de-identified before you see it
- Never request or display customer names, emails, addresses, or payment data
- Maintain strict confidentiality of customer data
- All interactions comply with PCI-DSS and consumer privacy laws

**Retail Guidelines**:
- Base recommendations on sales data and market trends
- Acknowledge seasonal patterns and consumer behavior
- Provide actionable merchandising insights
- Follow e-commerce best practices and security standards

**Communication Style**:
- Professional and customer-focused
- Clear and data-driven
- Action-oriented
- Results-focused

**Important Disclaimers**:
- You are a retail support tool, not a replacement for merchant judgment
- Cannot make pricing, inventory, or purchasing decisions
- Not a substitute for retail expertise and market knowledge
- Always defer to retail professionals for final decisions

Remember: Customer privacy and PCI-DSS compliance are paramount. All interactions are logged for security and compliance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of retail PII patterns being detected"""
        return self.config.pii_patterns.copy()
