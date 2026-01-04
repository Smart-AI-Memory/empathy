"""Research/Academic Wizard - Research Data Privacy Compliant AI Assistant

Specialized wizard for research and academic work with research participant PII protection,
IRB compliance, and comprehensive audit logging.

Key Features:
- Research participant PII detection and protection
- IRB compliance support
- Grant and publication data handling
- Comprehensive audit trail
- Research ethics compliance
- Automatic classification as SENSITIVE

Reference:
- IRB regulations (45 CFR 46)
- HIPAA for research (45 CFR 164.512)
- Research data privacy best practices

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Research PII patterns
RESEARCH_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # Research-specific
    "participant_id",
    "subject_id",
    "protocol_number",
    "grant_id",
]


class ResearchWizard(BaseWizard):
    """Research data privacy compliant academic AI assistant

    Implements PII protection for research operations:
    1. Research participant PII detection and scrubbing
    2. IRB compliance support
    3. Encryption for sensitive research data
    4. Comprehensive audit logging
    5. 7-year retention (research data requirements)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import ResearchWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = ResearchWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me analyze this research dataset",
        ...     user_id="researcher@university.edu"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize research wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional institution-specific PII patterns

        """
        pii_patterns = RESEARCH_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Research & Academic Assistant",
            description="Research data privacy compliant AI assistant for academic research",
            domain="research",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for research data
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "ResearchWizard initialized with security DISABLED. "
                "IRB compliance requires enable_security=True in EmpathyLLM.",
            )

        logger.info(
            f"ResearchWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build research/academic system prompt"""
        return """You are a research data privacy compliant AI academic assistant.

**Domain**: Research / Academic / Scientific Investigation

**Your Role**:
- Assist researchers with study design and methodology
- Support data analysis and interpretation
- Help with grant writing and publication preparation
- Provide guidance on research ethics and compliance

**Research Privacy**:
- All participant information is automatically de-identified before you see it
- Never request or display participant names, IDs, or identifying data
- Maintain strict confidentiality of research data
- All interactions comply with IRB regulations

**Research Guidelines**:
- Base recommendations on scientific method and evidence
- Acknowledge ethical considerations and IRB requirements
- Provide rigorous methodological guidance
- Follow research integrity and data privacy best practices

**Communication Style**:
- Academic and precise
- Evidence-based
- Methodologically rigorous
- Ethically aware

**Important Disclaimers**:
- You are a research support tool, not a replacement for researcher judgment
- Cannot make IRB approval or study design decisions
- Not a substitute for peer review or expert consultation
- Always defer to IRB and senior researchers for final decisions

Remember: Research participant privacy and ethical compliance are paramount. All interactions are logged for IRB compliance and data integrity.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of research PII patterns being detected"""
        return self.config.pii_patterns.copy()
