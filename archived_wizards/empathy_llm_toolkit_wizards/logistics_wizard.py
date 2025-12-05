"""
Logistics/Supply Chain Wizard - Shipment Data Privacy Compliant AI Assistant

Specialized wizard for logistics and supply chain with shipment tracking,
customer PII protection, and comprehensive audit logging.

Key Features:
- Customer and shipment data protection
- Tracking and routing data handling
- Warehouse and inventory management
- Comprehensive audit trail
- Supply chain security
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Logistics PII patterns
LOGISTICS_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "address",
    "ip_address",
    # Logistics-specific
    "tracking_number",
    "shipment_id",
    "customer_id",
    "order_number",
]


class LogisticsWizard(BaseWizard):
    """
    Shipment data privacy compliant logistics AI assistant

    Implements data protection for logistics operations:
    1. Customer and shipment data detection and protection
    2. Secrets detection
    3. Encryption for sensitive logistics data
    4. Comprehensive audit logging
    5. 2-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import LogisticsWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = LogisticsWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me optimize this shipping route",
        ...     user_id="logistics@company.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize logistics wizard

        Args:
            llm: EmpathyLLM instance (security recommended)
            custom_pii_patterns: Additional company-specific PII patterns
        """
        pii_patterns = LOGISTICS_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Logistics & Supply Chain Assistant",
            description="Shipment data privacy compliant AI assistant for logistics",
            domain="logistics",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=730,  # 2 years
            default_classification="INTERNAL",
            auto_classify=True,
        )

        super().__init__(llm, config)

        logger.info(
            f"LogisticsWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build logistics/supply chain system prompt"""
        return """You are a shipment data privacy compliant AI logistics assistant.

**Domain**: Logistics / Supply Chain / Distribution

**Your Role**:
- Assist logistics professionals with route optimization and planning
- Support warehouse management and inventory control
- Help with shipment tracking and coordination
- Provide guidance on supply chain efficiency

**Data Privacy**:
- All customer and shipment information is automatically de-identified before you see it
- Never request or display customer addresses, tracking numbers, or shipment details
- Maintain confidentiality of logistics data
- Focus on operational efficiency and service quality

**Logistics Guidelines**:
- Base recommendations on optimization algorithms and best practices
- Acknowledge capacity constraints and service requirements
- Provide practical routing and scheduling guidance
- Follow industry standards and safety regulations

**Communication Style**:
- Professional and efficient
- Clear and actionable
- Detail-oriented
- Service-focused

**Important Disclaimers**:
- You are a logistics support tool, not a replacement for dispatcher judgment
- Cannot make routing, scheduling, or carrier selection decisions
- Not a substitute for logistics expertise and local knowledge
- Always defer to logistics professionals for final decisions

Remember: Customer privacy and shipment security are paramount. All interactions are logged for compliance and quality assurance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of logistics PII patterns being detected"""
        return self.config.pii_patterns.copy()
