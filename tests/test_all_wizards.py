"""
Comprehensive Test Suite for All 16 Wizards

Tests configuration, security integration, compliance verification,
and PII pattern detection for all domain-specific wizards.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from unittest.mock import MagicMock, patch

import pytest

# Import from archived wizards location
from archived_wizards.empathy_llm_toolkit_wizards import (
    AccountingWizard,
    CustomerSupportWizard,
    EducationWizard,
    FinanceWizard,
    GovernmentWizard,
    HealthcareWizard,
    HRWizard,
    InsuranceWizard,
    LegalWizard,
    LogisticsWizard,
    ManufacturingWizard,
    RealEstateWizard,
    ResearchWizard,
    RetailWizard,
    SalesWizard,
    TechnologyWizard,
)
from empathy_llm_toolkit import EmpathyLLM


# Mock anthropic package for tests
@pytest.fixture
def mock_anthropic():
    """Mock anthropic module so tests don't require actual package"""
    mock_module = MagicMock()
    mock_client = MagicMock()
    mock_module.Anthropic.return_value = mock_client
    with patch.dict("sys.modules", {"anthropic": mock_module}):
        yield mock_module


# Test fixtures
@pytest.fixture
def llm_with_security(mock_anthropic):
    """EmpathyLLM instance with security enabled"""
    return EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=True)  # pragma: allowlist secret


@pytest.fixture
def llm_without_security(mock_anthropic):
    """EmpathyLLM instance without security"""
    return EmpathyLLM(provider="anthropic", api_key="test-key", enable_security=False)  # pragma: allowlist secret


# Wizard definitions with expected properties
WIZARD_SPECS = [
    {
        "class": HealthcareWizard,
        "name": "Healthcare Assistant",
        "domain": "healthcare",
        "classification": "SENSITIVE",
        "retention_days": 90,
        "min_pii_patterns": 10,
        "key_patterns": ["mrn", "patient_id", "dob"],
        "compliance_method": "get_hipaa_compliance_status",
        "pii_method": "get_phi_patterns",  # Healthcare uses PHI not PII
    },
    {
        "class": FinanceWizard,
        "name": "Finance Assistant",
        "domain": "finance",
        "classification": "SENSITIVE",
        "retention_days": 2555,  # 7 years
        "min_pii_patterns": 8,
        "key_patterns": ["bank_account", "routing_number", "tax_id"],
        "compliance_method": "get_compliance_status",
    },
    {
        "class": LegalWizard,
        "name": "Legal Assistant",
        "domain": "legal",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 6,
        "key_patterns": ["case_number", "docket_number", "client_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": EducationWizard,
        "name": "Education Assistant",
        "domain": "education",
        "classification": "SENSITIVE",
        "retention_days": 1825,  # 5 years
        "min_pii_patterns": 5,
        "key_patterns": ["student_id", "transcript_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": CustomerSupportWizard,
        "name": "Customer Support Assistant",
        "domain": "customer_support",
        "classification": "INTERNAL",
        "retention_days": 730,  # 2 years
        "min_pii_patterns": 4,
        "key_patterns": ["customer_id", "ticket_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": HRWizard,
        "name": "HR Assistant",
        "domain": "hr",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 6,
        "key_patterns": ["employee_id", "salary_info"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": SalesWizard,
        "name": "Sales & Marketing Assistant",
        "domain": "sales",
        "classification": "INTERNAL",
        "retention_days": 1095,  # 3 years
        "min_pii_patterns": 4,
        "key_patterns": ["lead_id", "opportunity_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": RealEstateWizard,
        "name": "Real Estate Assistant",
        "domain": "real_estate",
        "classification": "INTERNAL",
        "retention_days": 2555,
        "min_pii_patterns": 5,
        "key_patterns": ["mls_number", "parcel_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": InsuranceWizard,
        "name": "Insurance Assistant",
        "domain": "insurance",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 6,
        "key_patterns": ["policy_number", "claim_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": AccountingWizard,
        "name": "Accounting & Tax Assistant",
        "domain": "accounting",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 5,
        "key_patterns": ["tax_id", "account_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": ResearchWizard,
        "name": "Research & Academic Assistant",
        "domain": "research",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 4,
        "key_patterns": ["participant_id", "subject_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": GovernmentWizard,
        "name": "Government & Compliance Assistant",
        "domain": "government",
        "classification": "SENSITIVE",
        "retention_days": 2555,
        "min_pii_patterns": 4,
        "key_patterns": ["agency_id", "case_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": RetailWizard,
        "name": "Retail & E-commerce Assistant",
        "domain": "retail",
        "classification": "SENSITIVE",
        "retention_days": 730,
        "min_pii_patterns": 4,
        "key_patterns": ["customer_id", "order_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": ManufacturingWizard,
        "name": "Manufacturing Assistant",
        "domain": "manufacturing",
        "classification": "INTERNAL",
        "retention_days": 1825,
        "min_pii_patterns": 4,
        "key_patterns": ["part_number", "serial_number"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": LogisticsWizard,
        "name": "Logistics & Supply Chain Assistant",
        "domain": "logistics",
        "classification": "INTERNAL",
        "retention_days": 730,
        "min_pii_patterns": 4,
        "key_patterns": ["tracking_number", "shipment_id"],
        "compliance_method": "get_pii_patterns",
    },
    {
        "class": TechnologyWizard,
        "name": "Technology & IT Assistant",
        "domain": "technology",
        "classification": "INTERNAL",
        "retention_days": 365,
        "min_pii_patterns": 4,
        "key_patterns": ["api_key", "access_token"],
        "compliance_method": "get_pii_patterns",
    },
]


class TestWizardConfiguration:
    """Test configuration for all 16 wizards"""

    @pytest.mark.parametrize("spec", WIZARD_SPECS, ids=lambda s: s["class"].__name__)
    def test_wizard_initialization_with_security(self, llm_with_security, spec):
        """Test wizard initializes correctly with security enabled"""
        wizard = spec["class"](llm_with_security)

        assert wizard.config.name == spec["name"]
        assert wizard.config.domain == spec["domain"]
        assert wizard.config.enable_security is True
        assert wizard.config.default_classification == spec["classification"]
        assert wizard.config.retention_days == spec["retention_days"]

    @pytest.mark.parametrize("spec", WIZARD_SPECS, ids=lambda s: s["class"].__name__)
    def test_wizard_security_settings(self, llm_with_security, spec):
        """Test wizard has correct security settings"""
        wizard = spec["class"](llm_with_security)

        assert wizard.config.enable_security is True
        assert wizard.config.enable_secrets_detection is True
        assert wizard.config.block_on_secrets is True
        assert wizard.config.audit_all_access is True
        assert wizard.config.auto_classify is True

    @pytest.mark.parametrize("spec", WIZARD_SPECS, ids=lambda s: s["class"].__name__)
    def test_wizard_pii_patterns(self, llm_with_security, spec):
        """Test wizard has domain-specific PII patterns"""
        wizard = spec["class"](llm_with_security)

        # Healthcare uses get_phi_patterns, others use get_pii_patterns
        pii_method = spec.get("pii_method", "get_pii_patterns")
        pii_patterns = getattr(wizard, pii_method)()

        # Should have at least minimum patterns
        assert len(pii_patterns) >= spec["min_pii_patterns"]

        # Should have key domain-specific patterns
        for pattern in spec["key_patterns"]:
            assert pattern in pii_patterns

        # Should have standard PII patterns
        assert "email" in pii_patterns
        assert "phone" in pii_patterns

    @pytest.mark.parametrize("spec", WIZARD_SPECS, ids=lambda s: s["class"].__name__)
    def test_wizard_system_prompt(self, llm_with_security, spec):
        """Test wizard has domain-specific system prompt"""
        wizard = spec["class"](llm_with_security)

        system_prompt = wizard._build_system_prompt()

        assert isinstance(system_prompt, str)
        assert len(system_prompt) > 100  # Substantial prompt
        # Check for domain keywords in prompt (case-insensitive)
        prompt_lower = system_prompt.lower()
        domain_keywords = spec["domain"].replace("_", " ").lower()
        assert domain_keywords in prompt_lower or spec["name"].lower() in prompt_lower

    @pytest.mark.parametrize("spec", WIZARD_SPECS, ids=lambda s: s["class"].__name__)
    def test_wizard_has_compliance_method(self, llm_with_security, spec):
        """Test wizard has compliance verification method"""
        wizard = spec["class"](llm_with_security)

        assert hasattr(wizard, spec["compliance_method"])
        compliance_method = getattr(wizard, spec["compliance_method"])
        assert callable(compliance_method)


class TestWizardSecurityWarnings:
    """Test security warnings when security is disabled"""

    @pytest.mark.parametrize(
        "wizard_class",
        [
            HealthcareWizard,
            FinanceWizard,
            LegalWizard,
            EducationWizard,
            HRWizard,
            InsuranceWizard,
            AccountingWizard,
            ResearchWizard,
            GovernmentWizard,
            RetailWizard,
            TechnologyWizard,
        ],
    )
    def test_security_warning_for_sensitive_wizards(
        self, llm_without_security, wizard_class, caplog
    ):
        """Test SENSITIVE wizards warn when security is disabled"""
        _ = wizard_class(llm_without_security)

        # Should log warning for SENSITIVE wizards
        assert any(
            "security disabled" in record.message.lower()
            or "compliance" in record.message.lower()
            or "requires enable_security" in record.message.lower()
            for record in caplog.records
        )


class TestWizardCustomization:
    """Test wizard customization options"""

    def test_healthcare_wizard_custom_phi_patterns(self, llm_with_security):
        """Test HealthcareWizard accepts custom PHI patterns"""
        custom_patterns = ["facility_id", "department_code"]
        wizard = HealthcareWizard(llm_with_security, custom_phi_patterns=custom_patterns)

        phi_patterns = wizard.get_phi_patterns()
        for pattern in custom_patterns:
            assert pattern in phi_patterns

    def test_finance_wizard_transaction_scrubbing(self, llm_with_security):
        """Test FinanceWizard transaction scrubbing option"""
        wizard_with = FinanceWizard(llm_with_security, enable_transaction_scrubbing=True)
        wizard_without = FinanceWizard(llm_with_security, enable_transaction_scrubbing=False)

        patterns_with = wizard_with.get_pii_patterns()
        patterns_without = wizard_without.get_pii_patterns()

        # Both should have standard patterns
        assert "email" in patterns_with
        assert "email" in patterns_without


class TestWizardCompliance:
    """Test compliance verification for wizards"""

    def test_healthcare_hipaa_compliance_status(self, llm_with_security):
        """Test Healthcare wizard HIPAA compliance status"""
        wizard = HealthcareWizard(llm_with_security)
        status = wizard.get_hipaa_compliance_status()

        assert isinstance(status, dict)
        assert "compliant" in status
        assert "checks" in status
        assert "recommendations" in status

        # Should be compliant with security enabled
        assert status["compliant"] is True
        assert isinstance(status["checks"], dict)
        assert len(status["checks"]) >= 5  # Multiple checks

    def test_finance_compliance_status(self, llm_with_security):
        """Test Finance wizard compliance status"""
        wizard = FinanceWizard(llm_with_security)
        status = wizard.get_compliance_status()

        assert isinstance(status, dict)
        assert "compliant" in status
        assert status["compliant"] is True

    def test_healthcare_compliance_recommendations(self, llm_without_security):
        """Test compliance recommendations when security disabled"""
        wizard = HealthcareWizard(llm_without_security)
        status = wizard.get_hipaa_compliance_status()

        assert status["compliant"] is False
        assert len(status["recommendations"]) > 0
        assert any("enable_security" in rec.lower() for rec in status["recommendations"])


class TestWizardEmpathyLevels:
    """Test default empathy levels for wizards"""

    def test_customer_support_anticipatory_empathy(self, llm_with_security):
        """Test Customer Support wizard uses anticipatory empathy (level 4)"""
        wizard = CustomerSupportWizard(llm_with_security)
        assert wizard.config.default_empathy_level == 4

    def test_sales_anticipatory_empathy(self, llm_with_security):
        """Test Sales wizard uses anticipatory empathy (level 4)"""
        wizard = SalesWizard(llm_with_security)
        assert wizard.config.default_empathy_level == 4

    def test_retail_anticipatory_empathy(self, llm_with_security):
        """Test Retail wizard uses anticipatory empathy (level 4)"""
        wizard = RetailWizard(llm_with_security)
        assert wizard.config.default_empathy_level == 4

    def test_most_wizards_proactive_empathy(self, llm_with_security):
        """Test most wizards use proactive empathy (level 3)"""
        proactive_wizards = [
            HealthcareWizard,
            FinanceWizard,
            LegalWizard,
            EducationWizard,
            HRWizard,
            RealEstateWizard,
            InsuranceWizard,
            AccountingWizard,
            ResearchWizard,
            GovernmentWizard,
            ManufacturingWizard,
            LogisticsWizard,
            TechnologyWizard,
        ]

        for wizard_class in proactive_wizards:
            wizard = wizard_class(llm_with_security)
            assert wizard.config.default_empathy_level == 3


class TestWizardRetentionPolicies:
    """Test retention policies match compliance requirements"""

    def test_seven_year_retention_wizards(self, llm_with_security):
        """Test wizards with 7-year retention (SOX, IRS, legal requirements)"""
        seven_year_wizards = [
            (FinanceWizard, "SOX §802"),
            (LegalWizard, "Legal records"),
            (HRWizard, "Employment records"),
            (RealEstateWizard, "Transaction records"),
            (InsuranceWizard, "Regulatory"),
            (AccountingWizard, "SOX/IRS"),
            (ResearchWizard, "Research data"),
            (GovernmentWizard, "Government records"),
        ]

        for wizard_class, reason in seven_year_wizards:
            wizard = wizard_class(llm_with_security)
            assert (
                wizard.config.retention_days == 2555
            ), f"{wizard_class.__name__} should have 7-year retention ({reason})"

    def test_hipaa_retention(self, llm_with_security):
        """Test Healthcare wizard has 90-day minimum HIPAA retention"""
        wizard = HealthcareWizard(llm_with_security)
        assert wizard.config.retention_days == 90

    def test_ferpa_retention(self, llm_with_security):
        """Test Education wizard has 5-year retention"""
        wizard = EducationWizard(llm_with_security)
        assert wizard.config.retention_days == 1825  # 5 years


# Summary test
def test_all_16_wizards_present():
    """Verify all 16 wizards are tested"""
    assert len(WIZARD_SPECS) == 16, "Should have exactly 16 wizard specifications"
