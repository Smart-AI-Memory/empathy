"""Tests for Healthcare Wizard - HIPAA Compliance

Verifies:
- PHI detection and scrubbing
- Mandatory encryption
- Comprehensive audit logging
- 90-day retention
- HIPAA compliance checks

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import os

import pytest

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.wizards import HealthcareWizard


class TestHealthcareWizardConfiguration:
    """Test Healthcare Wizard configuration and initialization"""

    def test_wizard_initialization_with_security(self):
        """Test wizard initializes correctly with security enabled"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key="test-key",
            enable_security=True,
        )

        wizard = HealthcareWizard(llm)

        assert wizard.config.name == "Healthcare Assistant"
        assert wizard.config.domain == "healthcare"
        assert wizard.config.default_empathy_level == 3  # Proactive
        assert wizard.config.enable_security is True
        assert wizard.config.audit_all_access is True
        assert wizard.config.retention_days == 90
        assert wizard.config.default_classification == "SENSITIVE"

    def test_wizard_initialization_without_security_warns(self, caplog):
        """Test wizard warns when initialized without security"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key="test-key",
            enable_security=False,  # Not HIPAA compliant
        )

        HealthcareWizard(llm)

        # Should log warning about security not enabled
        assert any(
            "security disabled" in record.message.lower() or "hipaa" in record.message.lower()
            for record in caplog.records
        )

    def test_phi_patterns_include_healthcare_specific(self):
        """Test PHI patterns include healthcare-specific identifiers"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=True)
        wizard = HealthcareWizard(llm)

        phi_patterns = wizard.get_phi_patterns()

        # Standard PII
        assert "email" in phi_patterns
        assert "phone" in phi_patterns
        assert "ssn" in phi_patterns

        # Healthcare PHI
        assert "mrn" in phi_patterns  # Medical Record Number
        assert "patient_id" in phi_patterns
        assert "dob" in phi_patterns  # Date of birth
        assert "insurance_id" in phi_patterns
        assert "provider_npi" in phi_patterns

    def test_custom_phi_patterns(self):
        """Test adding custom facility-specific PHI patterns"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=True)

        wizard = HealthcareWizard(
            llm,
            custom_phi_patterns=["facility_id", "employee_id"],
        )

        phi_patterns = wizard.get_phi_patterns()
        assert "facility_id" in phi_patterns
        assert "employee_id" in phi_patterns


class TestHealthcareWizardHIPAACompliance:
    """Test HIPAA compliance features"""

    def test_hipaa_compliance_status_with_security(self):
        """Test HIPAA compliance when all features enabled"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key="test-key",
            enable_security=True,
        )

        wizard = HealthcareWizard(llm)
        status = wizard.get_hipaa_compliance_status()

        assert status["compliant"] is True
        assert status["checks"]["security_enabled"] is True
        assert status["checks"]["audit_logging"] is True
        assert status["checks"]["phi_detection"] is True
        assert status["checks"]["retention_policy"] is True

    def test_hipaa_compliance_status_without_security(self):
        """Test HIPAA compliance status when security disabled"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key="test-key",
            enable_security=False,
        )

        wizard = HealthcareWizard(llm)
        status = wizard.get_hipaa_compliance_status()

        assert status["compliant"] is False
        assert status["checks"]["security_enabled"] is False
        assert len(status["recommendations"]) > 0
        assert any("enable security" in rec.lower() for rec in status["recommendations"])

    @pytest.mark.asyncio
    async def test_phi_detection_in_processing(self):
        """Test PHI is detected and scrubbed during processing"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
            enable_security=True,
        )

        wizard = HealthcareWizard(llm)

        # Input with PHI
        user_input = """
        Patient John Doe (MRN: 123456) presented with chest pain.
        Contact: doctor@hospital.com
        Phone: 555-123-4567
        """

        result = await wizard.process(
            user_input=user_input,
            user_id="doctor@hospital.com",
            patient_id="patient_123456",
        )

        # Verify HIPAA compliance metadata
        assert "hipaa_compliance" in result
        hipaa = result["hipaa_compliance"]

        assert hipaa["phi_detected"] is True  # PHI was detected
        assert hipaa["phi_scrubbed"] is True  # PHI was scrubbed
        assert hipaa["audit_logged"] is True  # Interaction logged
        assert hipaa["classification"] == "SENSITIVE"
        assert hipaa["retention_days"] == 90

    @pytest.mark.asyncio
    async def test_audit_logging_for_phi_access(self, caplog):
        """Test all PHI access is logged"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
            enable_security=True,
        )

        wizard = HealthcareWizard(llm)

        await wizard.process(
            user_input="Patient status update needed",
            user_id="nurse@hospital.com",
            patient_id="patient_789",
        )

        # Verify PHI access was logged
        assert any("phi_access" in record.message.lower() for record in caplog.records)
        assert any("patient_789" in str(record) for record in caplog.records)

    def test_minimum_90_day_retention(self):
        """Test wizard enforces 90-day minimum retention (HIPAA requirement)"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=True)
        wizard = HealthcareWizard(llm)

        assert wizard.config.retention_days >= 90

    def test_sensitive_classification_enforced(self):
        """Test all healthcare data classified as SENSITIVE"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=True)
        wizard = HealthcareWizard(llm)

        assert wizard.config.default_classification == "SENSITIVE"
        assert wizard.config.auto_classify is True


class TestHealthcareWizardSystemPrompt:
    """Test HIPAA-aware system prompt"""

    def test_system_prompt_includes_hipaa_guidance(self):
        """Test system prompt includes HIPAA compliance guidance"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key")
        wizard = HealthcareWizard(llm)

        prompt = wizard._build_system_prompt()

        # Should include HIPAA keywords
        assert "HIPAA" in prompt
        assert "confidential" in prompt.lower() or "privacy" in prompt.lower()
        assert "healthcare" in prompt.lower() or "clinical" in prompt.lower()

    def test_system_prompt_includes_clinical_guidelines(self):
        """Test system prompt includes clinical communication standards"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key")
        wizard = HealthcareWizard(llm)

        prompt = wizard._build_system_prompt()

        # Should mention clinical standards
        assert "evidence-based" in prompt.lower()
        assert any(std in prompt for std in ["SBAR", "SOAP", "clinical"])

    def test_system_prompt_emphasizes_deidentification(self):
        """Test system prompt explains PHI is de-identified"""
        llm = EmpathyLLM(provider="anthropic", api_key="test-key")
        wizard = HealthcareWizard(llm)

        prompt = wizard._build_system_prompt()

        assert "de-identified" in prompt.lower() or "deidentified" in prompt.lower()
        assert "patient" in prompt.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
