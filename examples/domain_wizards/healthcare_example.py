#!/usr/bin/env python
"""Healthcare Wizard Example - HIPAA-Compliant Clinical Assistant

Demonstrates the Healthcare Wizard with HIPAA++ features:
- Enhanced PHI detection and de-identification
- Mandatory encryption for all healthcare data
- Comprehensive audit logging
- 90-day retention enforcement
- HIPAA compliance verification

Usage:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/healthcare_wizard_example.py
"""

import asyncio
import os

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.wizards import HealthcareWizard


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"{title:^70}")
    print(f"{'=' * 70}\n")


async def example_1_basic_clinical_query():
    """Example 1: Basic clinical decision support query"""
    print_section("Example 1: Clinical Decision Support")

    # Initialize LLM with security enabled (HIPAA requirement)
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,  # CRITICAL for HIPAA compliance
    )

    # Initialize Healthcare Wizard
    wizard = HealthcareWizard(llm)

    # Clinical query (no PHI)
    query = """
    What are the evidence-based guidelines for managing a patient with
    newly diagnosed Type 2 Diabetes? Please include medication options
    and lifestyle modifications.
    """

    print("Query (no PHI):")
    print(query)

    result = await wizard.process(
        user_input=query,
        user_id="doctor@hospital.com",
    )

    print("\nAI Response:")
    print(result.get("response", "No response"))

    print("\nHIPAA Compliance Status:")
    compliance = result.get("hipaa_compliance", {})
    print(f"  PHI Detected: {compliance.get('phi_detected', False)}")
    print(f"  PHI Scrubbed: {compliance.get('phi_scrubbed', False)}")
    print(f"  Encrypted: {compliance.get('encrypted', False)}")
    print(f"  Audit Logged: {compliance.get('audit_logged', False)}")
    print(f"  Classification: {compliance.get('classification', 'N/A')}")


async def example_2_phi_deidentification():
    """Example 2: Automatic PHI de-identification"""
    print_section("Example 2: Automatic PHI De-identification")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = HealthcareWizard(llm)

    # Query with PHI (will be automatically scrubbed)
    query_with_phi = """
    Patient John Doe (MRN: 123456, DOB: 01/15/1980) presented to the ED
    with chest pain. Contact info: john.doe@email.com, 555-123-4567.

    Vital signs: BP 145/92, HR 88, RR 16, Temp 98.6°F

    What initial workup would you recommend for possible ACS?
    """

    print("Original Query (contains PHI):")
    print(query_with_phi)

    result = await wizard.process(
        user_input=query_with_phi,
        user_id="emergency@hospital.com",
        patient_id="MRN_123456",  # For audit trail
    )

    print("\nAI Response (PHI removed before processing):")
    print(result.get("response", "No response"))

    print("\nSecurity Report:")
    security = result.get("security_report", {})
    print(f"  PII/PHI Detected: {security.get('pii_count', 0)} instances")
    print(f"  Secrets Detected: {security.get('secrets_count', 0)}")

    print("\nHIPAA Compliance:")
    compliance = result.get("hipaa_compliance", {})
    print(f"  PHI Detected: {compliance.get('phi_detected')}")
    print(f"  PHI Scrubbed: {compliance.get('phi_scrubbed')}")
    print(f"  Data Classification: {compliance.get('classification')}")
    print(f"  Retention Days: {compliance.get('retention_days')}")


async def example_3_compliance_verification():
    """Example 3: HIPAA compliance verification"""
    print_section("Example 3: HIPAA Compliance Verification")

    # Test WITH security enabled (compliant)
    print("Configuration 1: Security ENABLED (HIPAA Compliant)")
    llm_secure = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        enable_security=True,
    )
    wizard_secure = HealthcareWizard(llm_secure)
    status_secure = wizard_secure.get_hipaa_compliance_status()

    print(f"  Overall Compliant: {status_secure['compliant']}")
    print("  Compliance Checks:")
    for check, passed in status_secure["checks"].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"    {check}: {status}")

    if status_secure["recommendations"]:
        print("  Recommendations:")
        for rec in status_secure["recommendations"]:
            print(f"    - {rec}")
    else:
        print("  ✅ No recommendations - fully compliant!")

    print("\n" + "-" * 70 + "\n")

    # Test WITHOUT security enabled (non-compliant)
    print("Configuration 2: Security DISABLED (Not HIPAA Compliant)")
    llm_insecure = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        enable_security=False,  # ⚠️ NOT HIPAA COMPLIANT
    )
    wizard_insecure = HealthcareWizard(llm_insecure)
    status_insecure = wizard_insecure.get_hipaa_compliance_status()

    print(f"  Overall Compliant: {status_insecure['compliant']}")
    print("  Compliance Checks:")
    for check, passed in status_insecure["checks"].items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"    {check}: {status}")

    if status_insecure["recommendations"]:
        print("  ⚠️  Recommendations for HIPAA Compliance:")
        for rec in status_insecure["recommendations"]:
            print(f"    - {rec}")


async def example_4_enhanced_phi_detection():
    """Example 4: Enhanced PHI pattern detection"""
    print_section("Example 4: Enhanced PHI Pattern Detection")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        enable_security=True,
    )

    # Test with various PHI pattern configurations
    wizard_default = HealthcareWizard(llm)
    wizard_custom = HealthcareWizard(
        llm,
        enable_medication_scrubbing=True,  # Scrub medication names
        enable_diagnosis_scrubbing=True,  # Scrub diagnosis codes
        custom_phi_patterns=["hospital_id", "department_code"],
    )

    print("Default PHI Patterns:")
    default_patterns = wizard_default.get_phi_patterns()
    print(f"  Total patterns: {len(default_patterns)}")
    print(f"  Patterns: {', '.join(default_patterns[:10])}...")

    print("\nEnhanced PHI Patterns (with medications, diagnoses, custom):")
    custom_patterns = wizard_custom.get_phi_patterns()
    print(f"  Total patterns: {len(custom_patterns)}")
    print("  Includes medication scrubbing: True")
    print("  Includes diagnosis scrubbing: True")
    print("  Custom patterns: hospital_id, department_code")


async def example_5_clinical_documentation():
    """Example 5: Clinical documentation assistance"""
    print_section("Example 5: Clinical Documentation Assistance")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = HealthcareWizard(llm)

    # Request for SOAP note assistance
    documentation_request = """
    I need help structuring a SOAP note for a patient with:
    - Subjective: Patient reports worsening shortness of breath over 3 days
    - Objective: RR 22, O2 sat 88% on room air, crackles bilateral bases
    - Assessment: Likely acute exacerbation of CHF
    - Plan: Need recommendations for initial management

    What would you include in the Plan section?
    """

    print("Documentation Request:")
    print(documentation_request)

    result = await wizard.process(
        user_input=documentation_request,
        user_id="resident@hospital.com",
        session_context={
            "encounter_type": "inpatient",
            "specialty": "internal_medicine",
        },
    )

    print("\nAI Assistance:")
    print(result.get("response", "No response"))

    print("\nWizard Metadata:")
    wizard_info = result.get("wizard", {})
    print(f"  Wizard: {wizard_info.get('name')}")
    print(f"  Domain: {wizard_info.get('domain')}")
    print(f"  Empathy Level: {wizard_info.get('empathy_level')}")


async def main():
    """Run all examples"""
    print(f"\n{'=' * 70}")
    print(f"{'Healthcare Wizard - HIPAA Compliance Demo':^70}")
    print(f"{'=' * 70}\n")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set. Some examples will run in demo mode.\n")

    try:
        # Run examples
        await example_1_basic_clinical_query()
        await example_2_phi_deidentification()
        await example_3_compliance_verification()
        await example_4_enhanced_phi_detection()
        await example_5_clinical_documentation()

        print_section("Summary")
        print("✅ All examples completed successfully!")
        print("\nKey Takeaways:")
        print("1. Healthcare Wizard enforces HIPAA compliance automatically")
        print("2. PHI is detected and scrubbed before LLM processing")
        print("3. All interactions are encrypted and audit logged")
        print("4. 90-day minimum retention for compliance")
        print("5. Compliance status can be verified programmatically")
        print("\nFor production use:")
        print("- Always enable security: enable_security=True")
        print("- Use encryption for all SENSITIVE data")
        print("- Enable comprehensive audit logging")
        print("- Regularly verify HIPAA compliance status")
        print("- Configure appropriate retention policies")

    except Exception as e:
        print(f"\n❌ Error during examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
