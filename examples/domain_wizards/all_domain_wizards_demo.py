#!/usr/bin/env python
"""Complete Domain Wizards Demo - All 16 Industry-Specific AI Assistants

Demonstrates all 16 production-ready, security-integrated domain wizards:
- Healthcare, Finance, Legal, Education (HIPAA, SOX, FERPA compliant)
- Customer Support, HR, Sales, Real Estate
- Insurance, Accounting, Research, Government
- Retail, Manufacturing, Logistics, Technology

Each wizard provides:
- Industry-specific PII protection
- Compliance features (HIPAA, SOX, PCI-DSS, FERPA, FISMA, etc.)
- Domain expertise with security built-in
- Automatic classification and encryption
- Comprehensive audit logging

Usage:
    export ANTHROPIC_API_KEY="your-api-key"
    python examples/domain_wizards/all_domain_wizards_demo.py
"""

import asyncio
import os

from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.wizards import (
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


def print_section(title: str, subtitle: str = ""):
    """Print formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    if subtitle:
        print(f"{subtitle:^80}")
    print(f"{'=' * 80}\n")


def print_wizard_info(wizard, result):
    """Print wizard result summary"""
    wizard_info = result.get("wizard", {})
    print(f"🧙 Wizard: {wizard_info.get('name', 'Unknown')}")
    print(f"🏢 Domain: {wizard_info.get('domain', 'Unknown')}")
    print(f"❤️  Empathy Level: {wizard_info.get('empathy_level', 3)}")

    compliance = result.get("hipaa_compliance") or result.get("compliance", {})
    if compliance:
        print(f"🔒 Classification: {compliance.get('classification', 'N/A')}")
        print(
            f"🛡️  PII Detected: {compliance.get('phi_detected', False) or compliance.get('pii_detected', False)}",
        )
        print(f"📋 Retention: {compliance.get('retention_days', 'N/A')} days")
    print()


async def demo_1_healthcare():
    """Demo 1: Healthcare Wizard - HIPAA-Compliant Clinical Assistant"""
    print_section("1. HEALTHCARE WIZARD", "HIPAA §164.312 - Clinical Decision Support")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,  # HIPAA requirement
    )

    wizard = HealthcareWizard(llm)

    query = """
    What are the current evidence-based guidelines for managing a patient
    with newly diagnosed Type 2 Diabetes? Include medication options and
    lifestyle modifications according to ADA standards.
    """

    print("📝 Query: Type 2 Diabetes management guidelines")
    result = await wizard.process(
        user_input=query,
        user_id="doctor@hospital.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_2_finance():
    """Demo 2: Finance Wizard - SOX/PCI-DSS Compliant Banking"""
    print_section("2. FINANCE WIZARD", "SOX §802, PCI-DSS v4.0 - Financial Analysis")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = FinanceWizard(llm)

    query = """
    Analyze the risk profile for a diversified investment portfolio with:
    - 60% equities (S&P 500 index)
    - 30% bonds (treasury and corporate)
    - 10% alternative assets
    What are the key risks and mitigation strategies?
    """

    print("📝 Query: Portfolio risk analysis")
    result = await wizard.process(
        user_input=query,
        user_id="advisor@bank.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_3_legal():
    """Demo 3: Legal Wizard - Attorney-Client Privilege"""
    print_section("3. LEGAL WIZARD", "Fed. Rules 502 - Legal Research")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = LegalWizard(llm)

    query = """
    What are the key considerations for drafting a non-compete agreement
    in California? Include enforceability concerns and best practices.
    """

    print("📝 Query: Non-compete agreement guidance")
    result = await wizard.process(
        user_input=query,
        user_id="attorney@lawfirm.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_4_education():
    """Demo 4: Education Wizard - FERPA-Compliant Academic"""
    print_section("4. EDUCATION WIZARD", "FERPA 20 U.S.C. § 1232g - Academic Support")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = EducationWizard(llm)

    query = """
    Design a rubric for evaluating student research papers in an
    undergraduate psychology course. Include criteria for thesis clarity,
    research methodology, and citation quality.
    """

    print("📝 Query: Research paper rubric design")
    result = await wizard.process(
        user_input=query,
        user_id="professor@university.edu",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_5_customer_support():
    """Demo 5: Customer Support Wizard - Level 4 Anticipatory"""
    print_section("5. CUSTOMER SUPPORT WIZARD", "Privacy-Compliant Help Desk")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = CustomerSupportWizard(llm)

    query = """
    Customer reports: "My order hasn't arrived and tracking shows 'delivery exception'.
    I need it by tomorrow for an important event."

    Provide resolution steps and empathetic response template.
    """

    print("📝 Query: Urgent delivery exception handling")
    result = await wizard.process(
        user_input=query,
        user_id="support@company.com",
        empathy_level=4,  # Anticipatory empathy
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_6_hr():
    """Demo 6: HR Wizard - Employee Privacy Compliant"""
    print_section("6. HR WIZARD", "EEOC - Recruiting & Retention")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = HRWizard(llm)

    query = """
    Create a structured interview guide for hiring a Senior Software Engineer.
    Include behavioral questions, technical screening topics, and DEI considerations.
    """

    print("📝 Query: Interview guide development")
    result = await wizard.process(
        user_input=query,
        user_id="recruiter@company.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_7_sales():
    """Demo 7: Sales Wizard - CRM Privacy Compliant"""
    print_section("7. SALES WIZARD", "CAN-SPAM, GDPR - Sales Forecasting")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = SalesWizard(llm)

    query = """
    Analyze this sales pipeline:
    - 50 leads in discovery
    - 25 in proposal stage
    - 15 in negotiation
    - Average deal size: $50K
    - Sales cycle: 90 days

    Forecast Q1 revenue and identify bottlenecks.
    """

    print("📝 Query: Sales pipeline forecasting")
    result = await wizard.process(
        user_input=query,
        user_id="sales_manager@company.com",
        empathy_level=4,  # Anticipatory
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_8_real_estate():
    """Demo 8: Real Estate Wizard - Property Data Privacy"""
    print_section("8. REAL ESTATE WIZARD", "Fair Housing Act - Market Analysis")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = RealEstateWizard(llm)

    query = """
    Comparative market analysis for:
    - Property: 3-bed, 2-bath single-family home
    - Location: Suburban neighborhood
    - Square footage: 2,100 sq ft
    - Recent upgrades: Kitchen, bathrooms

    What pricing strategy would you recommend?
    """

    print("📝 Query: Pricing strategy recommendation")
    result = await wizard.process(
        user_input=query,
        user_id="agent@realty.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_9_insurance():
    """Demo 9: Insurance Wizard - Policy Data Privacy"""
    print_section("9. INSURANCE WIZARD", "State Regulations - Claims Processing")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = InsuranceWizard(llm)

    query = """
    Guide me through the claims process for a vehicle collision:
    - Damage: Front-end collision
    - Liability: Third party at fault
    - Coverage: Full coverage policy

    What documentation is needed and what's the typical timeline?
    """

    print("📝 Query: Auto insurance claims guidance")
    result = await wizard.process(
        user_input=query,
        user_id="adjuster@insurance.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_10_accounting():
    """Demo 10: Accounting Wizard - SOX/IRS Compliant"""
    print_section("10. ACCOUNTING WIZARD", "SOX §802, IRS - Tax Compliance")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = AccountingWizard(llm)

    query = """
    Explain the tax implications for a small business choosing between:
    1. LLC taxed as S-Corp
    2. C-Corporation

    For a business with $500K annual revenue and 2 owners.
    """

    print("📝 Query: Entity structure tax analysis")
    result = await wizard.process(
        user_input=query,
        user_id="cpa@accounting.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_11_research():
    """Demo 11: Research Wizard - IRB-Compliant Academic Research"""
    print_section("11. RESEARCH WIZARD", "IRB 45 CFR 46 - Research Protocol")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = ResearchWizard(llm)

    query = """
    I'm designing a psychology study on cognitive load and decision-making.
    Help me structure the methodology and identify IRB considerations for:
    - 100 university student participants
    - Online survey with reaction time measurements
    - Minimal risk study
    """

    print("📝 Query: Research methodology and IRB compliance")
    result = await wizard.process(
        user_input=query,
        user_id="researcher@university.edu",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_12_government():
    """Demo 12: Government Wizard - FISMA-Compliant Public Sector"""
    print_section("12. GOVERNMENT WIZARD", "FISMA, Privacy Act - Policy Analysis")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = GovernmentWizard(llm)

    query = """
    Analyze the policy considerations for implementing a new digital services
    platform for citizen interactions. Include:
    - Privacy Act compliance
    - Accessibility (Section 508)
    - Security (FISMA)
    - Public engagement
    """

    print("📝 Query: Digital services policy analysis")
    result = await wizard.process(
        user_input=query,
        user_id="analyst@agency.gov",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_13_retail():
    """Demo 13: Retail Wizard - PCI-DSS E-commerce"""
    print_section("13. RETAIL WIZARD", "PCI-DSS v4.0 - Demand Forecasting")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = RetailWizard(llm)

    query = """
    Holiday season inventory planning:
    - Historical data: 40% increase in Nov-Dec
    - Top sellers: Electronics, toys, home goods
    - Supply chain lead time: 6 weeks
    - Budget: $500K

    Recommend inventory allocation strategy.
    """

    print("📝 Query: Holiday inventory planning")
    result = await wizard.process(
        user_input=query,
        user_id="buyer@retail.com",
        empathy_level=4,  # Anticipatory demand forecasting
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_14_manufacturing():
    """Demo 14: Manufacturing Wizard - Production Data Privacy"""
    print_section("14. MANUFACTURING WIZARD", "ISO Standards - Quality Control")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = ManufacturingWizard(llm)

    query = """
    Our production line is experiencing a 5% defect rate on a new component.
    Root cause analysis shows:
    - Temperature variance in curing process
    - Inconsistent material batch quality
    - Operator training gaps

    Recommend corrective actions using Six Sigma methodology.
    """

    print("📝 Query: Quality control root cause analysis")
    result = await wizard.process(
        user_input=query,
        user_id="qa_engineer@manufacturing.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_15_logistics():
    """Demo 15: Logistics Wizard - Shipment Data Privacy"""
    print_section("15. LOGISTICS WIZARD", "Transportation Security - Route Optimization")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = LogisticsWizard(llm)

    query = """
    Optimize delivery routes for:
    - 50 daily deliveries
    - 3 delivery vehicles
    - Service area: 30-mile radius
    - Time windows: 9am-5pm
    - Priority deliveries: 10%

    Minimize fuel costs and maximize on-time delivery.
    """

    print("📝 Query: Multi-stop route optimization")
    result = await wizard.process(
        user_input=query,
        user_id="dispatcher@logistics.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def demo_16_technology():
    """Demo 16: Technology Wizard - SOC2/ISO 27001 Compliant"""
    print_section("16. TECHNOLOGY WIZARD", "SOC2, ISO 27001 - DevOps Security")

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
    )

    wizard = TechnologyWizard(llm)

    query = """
    Design a CI/CD pipeline security strategy including:
    - Secret management (API keys, credentials)
    - Container scanning
    - SAST/DAST integration
    - Deployment approvals
    - Audit logging

    For a microservices architecture on Kubernetes.
    """

    print("📝 Query: Secure CI/CD pipeline design")
    result = await wizard.process(
        user_input=query,
        user_id="devops@company.com",
    )

    print("💡 Response Preview:")
    print(result.get("response", "No response")[:300] + "...\n")
    print_wizard_info(wizard, result)


async def main():
    """Run all domain wizard demos"""
    print_section("EMPATHY FRAMEWORK", "16 Domain-Specific AI Wizards Demo")

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set. Running in demo mode.\n")
        print("To run with live API:")
        print("  export ANTHROPIC_API_KEY='your-api-key'\n")

    try:
        # Run all demos
        await demo_1_healthcare()
        await demo_2_finance()
        await demo_3_legal()
        await demo_4_education()
        await demo_5_customer_support()
        await demo_6_hr()
        await demo_7_sales()
        await demo_8_real_estate()
        await demo_9_insurance()
        await demo_10_accounting()
        await demo_11_research()
        await demo_12_government()
        await demo_13_retail()
        await demo_14_manufacturing()
        await demo_15_logistics()
        await demo_16_technology()

        # Summary
        print_section("SUMMARY", "16 Domain Wizards Complete")

        print("✅ All domain wizards demonstrated successfully!\n")

        print("📊 Compliance Coverage:")
        print("   • HIPAA §164.312 - Healthcare")
        print("   • SOX §802, PCI-DSS - Finance, Accounting")
        print("   • FERPA - Education")
        print("   • Fed. Rules 502 - Legal")
        print("   • FISMA, Privacy Act - Government")
        print("   • IRB 45 CFR 46 - Research")
        print("   • State regulations - Insurance, Real Estate\n")

        print("🔒 Security Features (All Wizards):")
        print("   • Domain-specific PII detection")
        print("   • Automatic de-identification")
        print("   • AES-256-GCM encryption for SENSITIVE data")
        print("   • Comprehensive audit logging")
        print("   • Configurable retention policies")
        print("   • Compliance verification\n")

        print("❤️  Empathy Levels Demonstrated:")
        print("   • Level 3 (Proactive): Most wizards")
        print("   • Level 4 (Anticipatory): Customer Support, Sales, Retail\n")

        print("🏢 Industry Coverage:")
        print("   ✓ Healthcare      ✓ Finance         ✓ Legal          ✓ Education")
        print("   ✓ Customer Svc    ✓ HR              ✓ Sales          ✓ Real Estate")
        print("   ✓ Insurance       ✓ Accounting      ✓ Research       ✓ Government")
        print("   ✓ Retail          ✓ Manufacturing   ✓ Logistics      ✓ Technology\n")

        print("📚 Next Steps:")
        print("   1. Review individual wizard examples in domain_wizards/")
        print("   2. Check compliance status: wizard.get_[compliance]_status()")
        print("   3. Customize PII patterns for your organization")
        print("   4. Configure retention policies per compliance requirements")
        print("   5. Enable audit logging for production deployments\n")

        print("🔗 Related Examples:")
        print("   • Coach Wizards: examples/coach/demo_all_wizards.py")
        print("   • AI Wizards: examples/ai_wizards/all_ai_wizards_demo.py")
        print("   • Healthcare Deep Dive: examples/domain_wizards/healthcare_example.py\n")

    except Exception as e:
        print(f"\n❌ Error during demos: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
