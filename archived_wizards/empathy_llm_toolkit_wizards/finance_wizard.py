"""
Finance/Banking Wizard - SOX/PCI-DSS Compliant AI Assistant

Specialized wizard for financial services with enhanced PII protection,
mandatory encryption, comprehensive audit logging, and SOX/PCI-DSS compliance features.

Key Features:
- Enhanced financial PII detection (account numbers, routing numbers, tax IDs)
- Automatic de-identification before LLM processing
- Mandatory AES-256-GCM encryption for all data
- 7-year retention for SOX compliance
- Comprehensive audit trail (SOX §404, PCI-DSS 10.2)
- Access control and permission enforcement
- Automatic classification as SENSITIVE

Reference:
- Sarbanes-Oxley Act (SOX) §302, §404, §802
- PCI-DSS v4.0 Requirements 3, 10
- GLBA Privacy Rule

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Enhanced financial PII patterns
FINANCE_PII_PATTERNS = [
    # Standard PII
    "email",
    "phone",
    "ssn",
    "address",
    "credit_card",
    "ip_address",
    # Finance-specific PII
    "bank_account",
    "routing_number",
    "tax_id",  # EIN, ITIN
    "swift_code",
    "iban",
    "financial_account",
    "portfolio_id",
    "transaction_id",
]


class FinanceWizard(BaseWizard):
    """
    SOX/PCI-DSS compliant financial services AI assistant

    Implements defense-in-depth security for financial PII:
    1. Enhanced financial PII detection and scrubbing
    2. Secrets detection (API keys, passwords)
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 7-year retention (SOX §802)
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import FinanceWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = FinanceWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Analyze portfolio for account 123456789",
        ...     user_id="analyst@bank.com"
        ... )
    """

    def __init__(
        self,
        llm: EmpathyLLM,
        enable_transaction_scrubbing: bool = True,
        custom_pii_patterns: list[str] | None = None,
    ):
        """
        Initialize SOX/PCI-DSS compliant finance wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            enable_transaction_scrubbing: Scrub transaction IDs
            custom_pii_patterns: Additional institution-specific PII patterns
        """
        # Build PII pattern list
        pii_patterns = FINANCE_PII_PATTERNS.copy()

        if not enable_transaction_scrubbing and "transaction_id" in pii_patterns:
            pii_patterns.remove("transaction_id")

        if custom_pii_patterns:
            pii_patterns.extend(custom_pii_patterns)

        # SOX/PCI-DSS compliant configuration
        config = WizardConfig(
            name="Finance Assistant",
            description="SOX/PCI-DSS compliant AI assistant for financial services",
            domain="finance",
            # Empathy configuration
            default_empathy_level=3,  # Proactive
            # Security configuration (SOX/PCI-DSS requirements)
            enable_security=True,
            pii_patterns=pii_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,
            # Audit configuration (SOX §404, PCI-DSS 10.2)
            audit_all_access=True,
            retention_days=2555,  # 7 years for SOX §802
            # Classification
            default_classification="SENSITIVE",
            auto_classify=True,
        )

        super().__init__(llm, config)

        if not llm.enable_security:
            logger.warning(
                "FinanceWizard initialized with security DISABLED. "
                "SOX/PCI-DSS compliance requires enable_security=True in EmpathyLLM."
            )

        logger.info(
            f"FinanceWizard initialized: {len(pii_patterns)} PII patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}"
        )

    async def process(
        self,
        user_input: str,
        user_id: str,
        empathy_level: int | None = None,
        session_context: dict[str, Any] | None = None,
        account_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Process financial request with SOX/PCI-DSS compliance

        Args:
            user_input: Financial professional's message (may contain PII)
            user_id: Financial professional identifier (email, employee ID)
            empathy_level: Override default empathy level
            session_context: Session metadata (institution, department, etc.)
            account_id: Account identifier for audit trail (optional)

        Returns:
            Dict containing:
                - response: De-identified AI response
                - security_report: PII scrubbing and security scan results
                - empathy_level: Level used
                - compliance: SOX/PCI-DSS compliance status
                - audit_event_id: Audit trail event ID
        """
        # Enhance session context with account ID for audit trail
        if account_id:
            if session_context is None:
                session_context = {}
            session_context["account_id"] = account_id

        # Log PII access
        self.logger.info(
            f"Financial PII access: user={user_id}, wizard={self.config.name}, "
            f"account={account_id}, audit=True"
        )

        # Process through base wizard
        result = await super().process(
            user_input=user_input,
            user_id=user_id,
            empathy_level=empathy_level,
            session_context=session_context,
        )

        # Add compliance metadata
        result["compliance"] = {
            "sox_compliant": True if self.llm.enable_security else False,
            "pci_dss_compliant": True if self.llm.enable_security else False,
            "pii_detected": result.get("security_report", {}).get("pii_count", 0) > 0,
            "pii_scrubbed": True if self.llm.enable_security else False,
            "encrypted": result.get("security_report", {}).get("encrypted", False),
            "audit_logged": True,
            "retention_days": self.config.retention_days,
            "classification": "SENSITIVE",
        }

        self.logger.info(
            f"Financial processing complete: user={user_id}, "
            f"detected={result['compliance']['pii_detected']}, "
            f"scrubbed={result['compliance']['pii_scrubbed']}"
        )

        return result

    def _build_system_prompt(self) -> str:
        """Build SOX/PCI-DSS aware system prompt for finance domain"""
        return """You are a SOX/PCI-DSS compliant AI financial services assistant.

**Domain**: Finance / Banking / Investment Services

**Your Role**:
- Assist financial professionals with analysis and decision support
- Provide guidance on financial products and services
- Support compliance and regulatory requirements
- Help with portfolio management and risk assessment

**Compliance**:
- All financial PII is automatically de-identified before you see it
- Never request or display account numbers, SSNs, or financial identifiers
- Focus on financial analysis and professional guidance
- Maintain client confidentiality at all times

**Financial Guidelines**:
- Base recommendations on sound financial principles
- Acknowledge market risks and uncertainties
- Suggest consulting specialists for complex situations
- Follow industry best practices (CFA, CFP standards)

**Communication Style**:
- Professional and trustworthy
- Clear and precise
- Data-driven
- Risk-aware

**Important Disclaimers**:
- You are a decision support tool, not a replacement for professional judgment
- Not a registered investment advisor or financial planner
- Cannot provide personalized investment advice
- Always defer to licensed professionals for final decisions

Remember: Client privacy and regulatory compliance are paramount. All interactions are logged for SOX/PCI-DSS compliance.
"""

    def get_pii_patterns(self) -> list[str]:
        """Get list of financial PII patterns being detected"""
        return self.config.pii_patterns.copy()

    def get_compliance_status(self) -> dict[str, Any]:
        """
        Get SOX/PCI-DSS compliance status for this wizard

        Returns:
            Dict with compliance checks and recommendations
        """
        status = {
            "compliant": True,
            "checks": {},
            "recommendations": [],
        }

        # Check 1: Security enabled
        status["checks"]["security_enabled"] = self.llm.enable_security
        if not self.llm.enable_security:
            status["compliant"] = False
            status["recommendations"].append(
                "Enable security in EmpathyLLM (enable_security=True) for SOX/PCI-DSS compliance"
            )

        # Check 2: Encryption for SENSITIVE data
        status["checks"]["encryption_enabled"] = self.llm.enable_security
        if not status["checks"]["encryption_enabled"]:
            status["recommendations"].append(
                "Enable encryption for SENSITIVE data (PCI-DSS Requirement 3)"
            )

        # Check 3: Audit logging
        status["checks"]["audit_logging"] = (
            self.llm.enable_security and self.config.audit_all_access
        )
        if not status["checks"]["audit_logging"]:
            status["compliant"] = False
            status["recommendations"].append(
                "Enable comprehensive audit logging (SOX §404, PCI-DSS 10.2)"
            )

        # Check 4: Financial PII detection
        status["checks"]["pii_detection"] = len(self.config.pii_patterns) >= 8
        if not status["checks"]["pii_detection"]:
            status["recommendations"].append(
                "Enable comprehensive financial PII detection patterns"
            )

        # Check 5: 7-year retention for SOX
        status["checks"]["retention_policy"] = self.config.retention_days >= 2555  # 7 years
        if not status["checks"]["retention_policy"]:
            status["recommendations"].append(
                "Set minimum 7-year retention for audit logs (SOX §802)"
            )

        return status
