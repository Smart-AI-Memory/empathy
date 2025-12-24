"""
Customer Support Wizard - Privacy-Compliant AI Assistant

Specialized wizard for customer support with PII protection, ticket management,
and comprehensive audit logging.

Key Features:
- Customer PII detection and protection
- Automatic de-identification before LLM processing
- Ticket and case number tracking
- Comprehensive audit trail
- Support escalation handling
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Customer support PII patterns
SUPPORT_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "address",
    "credit_card",
    "ip_address",
    # Support-specific
    "customer_id",
    "ticket_number",
    "order_number",
    "account_number",
]


class CustomerSupportWizard(BaseWizard):
    """
    Privacy-compliant customer support AI assistant

    Implements customer PII protection for support operations:
    1. Customer PII detection and scrubbing
    2. Ticket tracking and management
    3. Encryption for sensitive customer data
    4. Comprehensive audit logging
    5. 2-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import CustomerSupportWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = CustomerSupportWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help resolve customer issue with order #12345",
        ...     user_id="agent@company.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize customer support wizard

        Args:
            llm: EmpathyLLM instance (security recommended)
            custom_pii_patterns: Additional company-specific PII patterns
        """
        pii_patterns = SUPPORT_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Customer Support Assistant",
            description="Privacy-compliant AI assistant for customer support teams",
            domain="customer_support",
            default_empathy_level=4,  # Anticipatory - predicts customer needs
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
            f"CustomerSupportWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    def _build_system_prompt(self) -> str:
        """Build customer support system prompt"""
        return """You are a privacy-compliant AI customer support assistant.

**Domain**: Customer Support / Help Desk

**Your Role**:
- Assist support agents with customer inquiries and issues
- Provide product knowledge and troubleshooting guidance
- Help draft customer communications
- Support ticket resolution and escalation

**Customer Privacy**:
- All customer PII is automatically de-identified before you see it
- Never request or display customer names, emails, or account numbers
- Maintain customer confidentiality at all times
- Focus on issue resolution and service excellence

**Support Guidelines**:
- Prioritize customer satisfaction and issue resolution
- Provide clear, actionable solutions
- Escalate complex issues appropriately
- Follow company policies and procedures

**Communication Style**:
- Empathetic and patient
- Clear and helpful
- Solution-oriented
- Professional yet friendly

**Important Disclaimers**:
- You are a support tool to assist agents, not a replacement for human judgment
- Cannot make refund, replacement, or policy exception decisions
- Always defer to supervisors for complex or sensitive cases
- Recommendations should be reviewed by support agents

Remember: Customer satisfaction and privacy are paramount. Interactions are logged.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of customer support PII patterns being detected"""
        return self.config.pii_patterns.copy()
