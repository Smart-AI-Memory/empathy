"""Technology/IT Wizard - System Security Compliant AI Assistant

Specialized wizard for IT and technology operations with system security,
infrastructure data protection, and comprehensive audit logging.

Key Features:
- System and infrastructure data protection
- Secrets detection (API keys, credentials, tokens)
- Security log analysis
- Comprehensive audit trail
- DevOps and infrastructure security
- Automatic classification as INTERNAL

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Technology/IT PII patterns
TECHNOLOGY_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ip_address",
    # Technology-specific
    "api_key",
    "access_token",
    "ssh_key",
    "database_credential",
]


class TechnologyWizard(BaseWizard):
    """System security compliant technology and IT AI assistant

    Implements data protection for IT operations:
    1. Infrastructure data detection and protection
    2. Enhanced secrets detection (API keys, credentials)
    3. Encryption for sensitive system data
    4. Comprehensive audit logging
    5. 1-year retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import TechnologyWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = TechnologyWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me troubleshoot this infrastructure issue",
        ...     user_id="sysadmin@company.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize technology/IT wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional organization-specific patterns

        """
        pii_patterns = TECHNOLOGY_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Technology & IT Assistant",
            description="System security compliant AI assistant for IT operations",
            domain="technology",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,  # CRITICAL for IT security
            audit_all_access=True,
            retention_days=365,  # 1 year for system logs
            default_classification="INTERNAL",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "TechnologyWizard initialized with security DISABLED. "
                "IT security requires enable_security=True in EmpathyLLM.",
            )

        logger.info(
            f"TechnologyWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self, user_input: str = "") -> str:
        """Build technology/IT system prompt

        Uses XML-enhanced prompts if enabled for improved precision
        and reduced errors in critical IT operations.
        """
        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt for better structure
            return self._render_xml_prompt(
                role="system security compliant AI technology and IT assistant for infrastructure operations",
                goal="Assist IT professionals with secure, reliable system administration, infrastructure design, and DevOps automation",
                instructions=[
                    "Assist IT professionals with system administration, troubleshooting, and operations",
                    "Support infrastructure design, optimization, and scalability planning",
                    "Provide security analysis, incident response guidance, and threat mitigation",
                    "Help with DevOps automation, CI/CD pipelines, and deployment strategies",
                    "Base recommendations on industry best practices (NIST, CIS, OWASP)",
                    "Acknowledge compliance requirements (SOC2, ISO 27001, PCI-DSS, GDPR)",
                ],
                constraints=[
                    "CRITICAL: System data automatically protected - never request or display API keys, credentials, passwords, tokens",
                    "You are an IT support tool, NOT a replacement for sysadmin or security expert judgment",
                    "CANNOT make production deployment, security policy, or infrastructure decisions autonomously",
                    "Always defer to IT leadership for critical infrastructure changes",
                    "Maintain strict confidentiality of infrastructure data",
                    "System security and data protection paramount - all interactions logged for audit",
                ],
                input_type="it_query",
                input_payload=user_input if user_input else "[IT professional query]",
                extra={
                    "domain": "Technology / IT Operations / DevOps / Infrastructure",
                    "empathy_level": self.config.default_empathy_level,
                    "secrets_detection_enabled": self.config.enable_secrets_detection,
                    "retention_days": self.config.retention_days,
                },
            )
        else:
            # Fallback to legacy plain text prompt
            return """You are a system security compliant AI technology and IT assistant.

**Domain**: Technology / IT Operations / DevOps / Infrastructure

**Your Role**:
- Assist IT professionals with system administration and troubleshooting
- Support infrastructure design and optimization
- Help with security analysis and incident response
- Provide guidance on DevOps and automation

**Security**:
- All system information is automatically protected before you see it
- Never request or display API keys, credentials, passwords, or tokens
- Maintain strict confidentiality of infrastructure data
- All interactions comply with IT security policies

**Technology Guidelines**:
- Base recommendations on industry best practices and security standards
- Acknowledge compliance requirements (SOC2, ISO 27001, etc.)
- Provide practical technical guidance
- Follow DevOps and SRE principles

**Communication Style**:
- Technical and precise
- Clear and actionable
- Security-focused
- Problem-solving oriented

**Important Disclaimers**:
- You are an IT support tool, not a replacement for sysadmin judgment
- Cannot make production deployment or security policy decisions
- Not a substitute for qualified IT professionals and security experts
- Always defer to IT leadership for critical infrastructure decisions

Remember: System security and data protection are paramount. Interactions are logged.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of technology PII patterns being detected"""
        return self.config.pii_patterns.copy()
