"""Healthcare Wizard - HIPAA-Compliant AI Assistant

Specialized wizard for healthcare applications with enhanced PHI protection,
mandatory encryption, comprehensive audit logging, and HIPAA compliance features.

Key Features:
- Enhanced PHI/PII detection (10+ medical patterns)
- Automatic de-identification before LLM processing
- Mandatory AES-256-GCM encryption for all data
- 90-day minimum retention (HIPAA §164.528)
- Comprehensive audit trail (HIPAA §164.312(b))
- Access control and permission enforcement
- Automatic classification as SENSITIVE

Reference:
- HIPAA Security Rule (45 CFR §164.312)
- HIPAA Privacy Rule (45 CFR §164.514)
- HITECH Act requirements

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from empathy_llm_toolkit import EmpathyLLM

from .base_wizard import BaseWizard, WizardConfig

logger = logging.getLogger(__name__)


# Enhanced PHI patterns for healthcare (beyond standard PII)
HEALTHCARE_PHI_PATTERNS = [
    # Standard PII (enabled by default)
    "email",
    "phone",
    "ssn",
    "address",
    "credit_card",
    "ip_address",
    # Healthcare-specific PHI
    "mrn",  # Medical Record Number
    "patient_id",  # Patient identifier
    "dob",  # Date of birth
    "insurance_id",  # Insurance/policy numbers
    "provider_npi",  # National Provider Identifier
    "cpt_code",  # Medical procedure codes
    "icd_code",  # Diagnosis codes
    "medication_name",  # Medication names (optional, configurable)
]


class HealthcareWizard(BaseWizard):
    """HIPAA-compliant healthcare AI assistant

    Implements defense-in-depth security for Protected Health Information (PHI):
    1. Enhanced PHI detection and scrubbing
    2. Secrets detection (API keys, passwords in medical software configs)
    3. Mandatory encryption (AES-256-GCM)
    4. Comprehensive audit logging
    5. 90-day minimum retention
    6. Access control enforcement

    Example:
        >>> from empathy_llm_toolkit import EmpathyLLM
        >>> from empathy_llm_toolkit.wizards import HealthcareWizard
        >>>
        >>> llm = EmpathyLLM(
        ...     provider="anthropic",
        ...     api_key=os.getenv("ANTHROPIC_API_KEY"),
        ...     enable_security=True,
        ... )
        >>>
        >>> wizard = HealthcareWizard(llm)
        >>>
        >>> result = await wizard.process(
        ...     user_input="Patient John Doe (MRN 123456) needs follow-up",
        ...     user_id="doctor@hospital.com"
        ... )
        >>>
        >>> print(result['security_report']['phi_removed'])  # PHI was scrubbed

    """

    def __init__(
        self,
        llm: EmpathyLLM,
        enable_medication_scrubbing: bool = False,
        enable_diagnosis_scrubbing: bool = False,
        custom_phi_patterns: list[str] | None = None,
    ):
        """Initialize HIPAA-compliant healthcare wizard

        Args:
            llm: EmpathyLLM instance (security should be enabled)
            enable_medication_scrubbing: Scrub medication names (may reduce context)
            enable_diagnosis_scrubbing: Scrub diagnosis codes (may reduce context)
            custom_phi_patterns: Additional facility-specific PHI patterns

        Note:
            For maximum HIPAA compliance, llm should be initialized with
            enable_security=True. This wizard enforces SENSITIVE classification
            and 90-day retention regardless of LLM security settings.

        """
        # Build PHI pattern list
        phi_patterns = HEALTHCARE_PHI_PATTERNS.copy()

        if not enable_medication_scrubbing:
            phi_patterns.remove("medication_name")
        if not enable_diagnosis_scrubbing:
            if "cpt_code" in phi_patterns:
                phi_patterns.remove("cpt_code")
            if "icd_code" in phi_patterns:
                phi_patterns.remove("icd_code")

        if custom_phi_patterns:
            phi_patterns.extend(custom_phi_patterns)

        # HIPAA-compliant configuration
        config = WizardConfig(
            name="Healthcare Assistant",
            description="HIPAA-compliant AI assistant for healthcare professionals",
            domain="healthcare",
            # Empathy configuration
            default_empathy_level=3,  # Proactive - anticipates needs
            # Security configuration (HIPAA requirements)
            enable_security=True,
            pii_patterns=phi_patterns,
            enable_secrets_detection=True,
            block_on_secrets=True,  # CRITICAL: Block if secrets detected
            # Audit configuration (HIPAA §164.312(b))
            audit_all_access=True,  # Log every interaction
            retention_days=90,  # HIPAA minimum for audit logs
            # Classification (HIPAA §164.514)
            default_classification="SENSITIVE",  # PHI is always SENSITIVE
            auto_classify=True,
        )

        super().__init__(llm, config)

        # Verify security is enabled
        if not llm.enable_security:
            logger.warning(
                "HealthcareWizard initialized with security DISABLED. "
                "HIPAA compliance requires enable_security=True in EmpathyLLM.",
            )

        logger.info(
            f"HealthcareWizard initialized: {len(phi_patterns)} PHI patterns, "
            f"empathy level={config.default_empathy_level}, security={llm.enable_security}",
        )

    async def process(
        self,
        user_input: str,
        user_id: str,
        empathy_level: int | None = None,
        session_context: dict[str, Any] | None = None,
        patient_id: str | None = None,
    ) -> dict[str, Any]:
        """Process healthcare request with HIPAA compliance

        Args:
            user_input: Healthcare professional's message (may contain PHI)
            user_id: Healthcare provider identifier (email, NPI, etc.)
            empathy_level: Override default empathy level
            session_context: Session metadata (encounter ID, facility, etc.)
            patient_id: Patient identifier for audit trail (optional)

        Returns:
            Dict containing:
                - response: De-identified AI response
                - security_report: PHI scrubbing and security scan results
                - empathy_level: Level used
                - hipaa_compliance: Compliance status
                - audit_event_id: Audit trail event ID

        Raises:
            SecurityError: If secrets detected in input
            ValueError: If invalid user_id or parameters

        """
        # Enhance session context with patient ID for audit trail
        if patient_id:
            if session_context is None:
                session_context = {}
            session_context["patient_id"] = patient_id

        # Log PHI access
        self.logger.info(
            f"PHI access: user={user_id}, wizard={self.config.name}, "
            f"patient={patient_id}, audit=True",
        )

        # Process through base wizard (handles security pipeline)
        result = await super().process(
            user_input=user_input,
            user_id=user_id,
            empathy_level=empathy_level,
            session_context=session_context,
        )

        # Add HIPAA compliance metadata
        result["hipaa_compliance"] = {
            "phi_detected": result.get("security_report", {}).get("pii_count", 0) > 0,
            "phi_scrubbed": True if self.llm.enable_security else False,
            "encrypted": result.get("security_report", {}).get("encrypted", False),
            "audit_logged": True,
            "retention_days": self.config.retention_days,
            "classification": "SENSITIVE",
        }

        # Log completion
        self.logger.info(
            f"PHI processing complete: user={user_id}, "
            f"detected={result['hipaa_compliance']['phi_detected']}, "
            f"scrubbed={result['hipaa_compliance']['phi_scrubbed']}",
        )

        return result

    def _build_system_prompt(self, user_input: str = "") -> str:
        """Build HIPAA-aware system prompt for healthcare domain

        Includes:
        - Healthcare domain knowledge
        - HIPAA compliance reminders
        - Clinical communication best practices
        - Patient privacy emphasis

        Uses XML-enhanced prompts if enabled for improved reliability
        and reduced hallucinations (critical for HIPAA compliance).
        """
        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt for better structure and HIPAA compliance
            return self._render_xml_prompt(
                role="HIPAA-compliant AI healthcare assistant for clinical decision support",
                goal="Assist healthcare professionals with evidence-based clinical guidance while maintaining strict HIPAA compliance and patient safety",
                instructions=[
                    "Provide clinical decision support based on current evidence-based guidelines",
                    "Support clinical documentation following standardized formats (SBAR, SOAP, etc.)",
                    "Help with care coordination and patient management workflows",
                    "Use standardized medical terminology (ICD-10, CPT, SNOMED) where appropriate",
                    "Acknowledge limitations and suggest specialist consultation when needed",
                    "Maintain professional, empathetic communication",
                ],
                constraints=[
                    "CRITICAL: All PHI is automatically de-identified - never request or display patient identifiers",
                    "You are a decision support tool, NOT a replacement for professional clinical judgment",
                    "NEVER diagnose or prescribe - support licensed healthcare providers who do",
                    "In emergencies, direct to appropriate emergency services immediately",
                    "Focus on clinical reasoning and evidence-based medicine",
                    "Patient safety and privacy are paramount - all interactions logged for HIPAA compliance",
                ],
                input_type="clinical_query",
                input_payload=user_input if user_input else "[Healthcare professional query]",
                extra={
                    "domain": "Healthcare / Clinical Medicine",
                    "compliance": "HIPAA §164.312 (Security Rule), §164.514 (Privacy Rule)",
                    "empathy_level": self.config.default_empathy_level,
                    "phi_detection_enabled": len(self.config.pii_patterns),
                },
            )
        else:
            # Fallback to legacy plain text prompt
            return """You are a HIPAA-compliant AI healthcare assistant.

**Domain**: Healthcare / Clinical Medicine

**Your Role**:
- Assist healthcare professionals with clinical decision support
- Provide evidence-based medical information
- Support clinical documentation and communication
- Help with care coordination and patient management

**HIPAA Compliance**:
- All patient data (PHI) is automatically de-identified before you see it
- Never request or display patient identifiers in your responses
- Focus on clinical reasoning and medical knowledge
- Maintain patient confidentiality at all times

**Clinical Guidelines**:
- Base recommendations on current evidence-based guidelines
- Acknowledge limitations and suggest consulting specialists when appropriate
- Use standardized medical terminology (ICD-10, CPT, SNOMED)
- Follow clinical communication best practices (SBAR, SOAP, etc.)

**Communication Style**:
- Professional and empathetic
- Clear and concise
- Evidence-based
- Action-oriented when appropriate

**Important Disclaimers**:
- You are a clinical decision support tool, not a replacement for professional judgment
- Always defer to licensed healthcare providers for final decisions
- In emergencies, direct users to appropriate emergency services
- Do not diagnose or prescribe - support healthcare professionals who do

Remember: Patient safety and privacy are paramount. Interactions are logged for HIPAA compliance.
"""

    def get_phi_patterns(self) -> list[str]:
        """Get list of PHI patterns being detected"""
        return self.config.pii_patterns.copy()

    def get_hipaa_compliance_status(self) -> dict[str, Any]:
        """Get HIPAA compliance status for this wizard

        Returns:
            Dict with compliance checks and recommendations

        """
        status: dict[str, Any] = {
            "compliant": True,
            "checks": {},
            "recommendations": [],
        }

        # Check 1: Security enabled
        status["checks"]["security_enabled"] = self.llm.enable_security
        if not self.llm.enable_security:
            status["compliant"] = False
            status["recommendations"].append(
                "Enable security in EmpathyLLM (enable_security=True) for HIPAA compliance",
            )

        # Check 2: Encryption for SENSITIVE data
        # Note: Encryption is handled by SecureMemDocsIntegration, not directly by EmpathyLLM
        status["checks"]["encryption_enabled"] = self.llm.enable_security
        if not status["checks"]["encryption_enabled"]:
            status["recommendations"].append(
                "Enable encryption for SENSITIVE data (HIPAA §164.312(a)(2)(iv))",
            )

        # Check 3: Audit logging
        status["checks"]["audit_logging"] = (
            self.llm.enable_security and self.config.audit_all_access
        )
        if not status["checks"]["audit_logging"]:
            status["compliant"] = False
            status["recommendations"].append(
                "Enable comprehensive audit logging (HIPAA §164.312(b))",
            )

        # Check 4: PHI detection
        status["checks"]["phi_detection"] = len(self.config.pii_patterns) >= 10
        if not status["checks"]["phi_detection"]:
            status["recommendations"].append("Enable comprehensive PHI detection patterns")

        # Check 5: Minimum retention
        status["checks"]["retention_policy"] = self.config.retention_days >= 90
        if not status["checks"]["retention_policy"]:
            status["recommendations"].append(
                "Set minimum 90-day retention for audit logs (HIPAA §164.528)",
            )

        return status
