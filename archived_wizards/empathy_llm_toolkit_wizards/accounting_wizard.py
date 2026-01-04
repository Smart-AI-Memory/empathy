"""Accounting/Tax Wizard - Financial Data Privacy Compliant AI Assistant

Specialized wizard for accounting and tax services with enhanced financial PII protection,
SOX compliance, and comprehensive audit logging.

Key Features:
- Enhanced financial PII detection (tax IDs, account numbers, financial statements)
- Automatic de-identification before LLM processing
- Mandatory AES-256-GCM encryption for all data
- 7-year retention (IRS and SOX requirements)
- Comprehensive audit trail
- SOX and tax compliance
- Automatic classification as SENSITIVE

Reference:
- Sarbanes-Oxley Act (SOX) §802
- IRS record retention requirements
- AICPA professional standards

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Accounting/tax PII patterns
ACCOUNTING_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "ip_address",
    # Accounting-specific
    "tax_id",  # EIN, ITIN
    "account_number",
    "bank_account",
    "routing_number",
    "financial_statement",
]


class AccountingWizard(BaseWizard):
    """Financial data privacy compliant accounting and tax AI assistant

    Implements defense-in-depth security for financial records:
    1. Enhanced financial PII detection and scrubbing
    2. Secrets detection
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention (SOX/IRS)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import AccountingWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = AccountingWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Help me analyze this financial statement",
        ...     user_id="cpa@firm.com"
        ... )

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        custom_pii_patterns: list[str] | None = None,
    ):
        """Initialize accounting/tax wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            custom_pii_patterns: Additional firm-specific PII patterns

        """
        pii_patterns = ACCOUNTING_PII_PATTERNS.copy()

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        config = WizardConfig(
            name="Accounting & Tax Assistant",
            description="Financial data privacy compliant AI assistant for accounting and tax",
            domain="accounting",
            default_empathy_level=3,  # Proactive
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            audit_all_access=True,
            retention_days=2555,  # 7 years for SOX/IRS
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "AccountingWizard initialized with security DISABLED. "
                "SOX/IRS compliance requires enable_security=True in EmpathyLLM.",
            )

        logger.info(
            f"AccountingWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    def _build_system_prompt(self) -> str:
        """Build accounting/tax system prompt"""
        return """You are a financial data privacy compliant AI accounting and tax assistant.

**Domain**: Accounting / Tax / Financial Reporting

**Your Role**:
- Assist accounting professionals with financial analysis and reporting
- Support tax preparation and compliance
- Help with audit procedures and controls
- Provide guidance on accounting standards and tax regulations

**Privacy**:
- All financial information is automatically de-identified before you see it
- Never request or display tax IDs, account numbers, or financial details
- Maintain strict confidentiality of client financial data
- All interactions comply with SOX and IRS requirements

**Accounting & Tax Guidelines**:
- Base recommendations on GAAP, IFRS, and tax code
- Acknowledge regulatory requirements and standards
- Provide accurate financial and tax guidance
- Follow AICPA professional standards

**Communication Style**:
- Professional and precise
- Clear and analytical
- Compliance-focused
- Detail-oriented

**Important Disclaimers**:
- You are an accounting support tool, not a replacement for CPA judgment
- Cannot make audit opinions or tax filing decisions
- Not a substitute for licensed CPA or tax professional
- Always defer to licensed professionals for final decisions

Remember: Client confidentiality and regulatory compliance are paramount. All interactions are logged for SOX and professional standards compliance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of accounting PII patterns being detected"""
        return self.config.pii_patterns.copy()
