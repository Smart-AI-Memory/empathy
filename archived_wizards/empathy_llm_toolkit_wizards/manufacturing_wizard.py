"""Manufacturing Wizard - Production Data Privacy Compliant AI Assistant

Specialized wizard for manufacturing with proprietary data protection,
quality control, and comprehensive audit logging.

Key Features:
- Proprietary manufacturing data protection
- Production and quality data handling
- Supply chain coordination
- Comprehensive audit trail
- Trade secret protection
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Manufacturing PII/proprietary patterns
MANUFACTURING_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "address",
    "ip_address",
    # Manufacturing-specific
    "employee_id",
    "part_number",
    "serial_number",
    "batch_number",
]


class ManufacturingWizard(BaseWizard):
    """Production data privacy compliant manufacturing AI assistant

    Implements proprietary data protection for manufacturing operations:
    1. Proprietary data detection and protection
    2. Secrets detection (API keys, credentials)
    3. Encryption for sensitive production data
    4. Comprehensive audit logging
    5. 5-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import ManufacturingWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = ManufacturingWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me optimize this production process",
        ...     user_id="engineer@manufacturer.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize manufacturing wizard

        Args:
            llm: EmpathyLLM instance (security recommended)
            custom_pii_patterns: Additional company-specific proprietary patterns

        """
        pii_patterns = MANUFACTURING_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Manufacturing Assistant",
            description="Production data privacy compliant AI assistant for manufacturing",
            domain="manufacturing",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=1825,  # 5 years
            default_classification="INTERNAL",
            auto_classify=True,
        )

        super().__init__(llm, config)

        logger.info(
            f"ManufacturingWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build manufacturing system prompt"""
        return """You are a production data privacy compliant AI manufacturing assistant.

**Domain**: Manufacturing / Production / Industrial Operations

**Your Role**:
- Assist manufacturing professionals with production optimization
- Support quality control and process improvement
- Help with supply chain coordination
- Provide guidance on manufacturing best practices

**Data Privacy**:
- All proprietary information is automatically protected before you see it
- Never request or display trade secrets, formulas, or proprietary processes
- Maintain strict confidentiality of production data
- Focus on operational excellence and efficiency

**Manufacturing Guidelines**:
- Base recommendations on lean manufacturing and quality principles
- Acknowledge safety and regulatory requirements
- Provide practical process optimization guidance
- Follow industry standards and best practices

**Communication Style**:
- Professional and technical
- Clear and precise
- Efficiency-focused
- Safety-conscious

**Important Disclaimers**:
- You are a manufacturing support tool, not a replacement for engineer judgment
- Cannot make production, safety, or quality approval decisions
- Not a substitute for qualified engineers and technicians
- Always defer to licensed professionals for final decisions

Remember: Trade secret protection and operational security are paramount. All interactions are logged for compliance and quality assurance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of manufacturing data patterns being detected"""
        return self.config.pii_patterns.copy()
