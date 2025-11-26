# Industry Wizards

Domain-specific AI assistants with built-in security, compliance, and industry best practices.

## Overview

**Empathy Framework includes industry-specific wizards** that provide:

- :material-shield-check: **Built-in Security** - PII scrubbing, secrets detection, audit logging
- :material-file-document: **Domain Knowledge** - Industry-specific prompts and workflows
- :material-clipboard-check: **Compliance Ready** - HIPAA, SOC2, GDPR, industry regulations
- :material-puzzle: **Easy Integration** - Drop-in components for any application

---

## Quick Start

!!! tip "Choose Your Industry"
    Click the tab for your industry to see the specialized wizard documentation.

=== ":fontawesome-solid-hospital: Healthcare"

    ## Healthcare Wizards

    **20+ HIPAA-compliant AI assistants** for medical applications with enhanced PHI protection.

    ### Key Features

    - :material-shield-lock: **Enhanced PHI Protection** - 10+ medical patterns (MRN, Patient ID, DOB, etc.)
    - :material-key: **Mandatory Encryption** - AES-256-GCM for all PHI
    - :material-file-document-check: **90-Day Retention** - HIPAA §164.528 compliance
    - :material-clipboard-list: **Comprehensive Audit Trail** - HIPAA §164.312(b) compliant
    - :material-star: **$2M+ Annual ROI** - For 100-bed hospitals

    ### Quick Example

    ```python
    from empathy_llm_toolkit import EmpathyLLM
    from empathy_llm_toolkit.wizards import HealthcareWizard

    # Initialize with security enabled
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True
    )

    # Create HIPAA-compliant wizard
    wizard = HealthcareWizard(llm)

    # Process patient information (PHI is automatically scrubbed)
    result = await wizard.process(
        user_input="Patient John Doe (MRN 123456) needs follow-up for diabetes",
        user_id="doctor@hospital.com"
    )

    # PHI was removed before sending to LLM
    print(result['security_report']['phi_removed'])  # ['mrn', 'name']
    ```

    ??? info "What PHI Patterns Are Detected?"

        **Standard PII:**
        - Email addresses
        - Phone numbers
        - SSN
        - Physical addresses
        - Credit card numbers
        - IP addresses

        **Healthcare-Specific PHI:**
        - **MRN** - Medical Record Numbers
        - **Patient IDs** - Patient identifiers
        - **DOB** - Dates of birth
        - **Insurance IDs** - Insurance/policy numbers
        - **Provider NPI** - National Provider Identifiers
        - **CPT Codes** - Medical procedure codes
        - **ICD Codes** - Diagnosis codes
        - **Medications** - Drug names (optional, configurable)

    ??? example "Clinical Handoff (SBAR Protocol)"

        ```python
        wizard = HealthcareWizard(llm)

        # Generate SBAR handoff report
        result = await wizard.generate_handoff(
            patient_id="PT123456",
            protocol="SBAR",  # Situation, Background, Assessment, Recommendation
            handoff_type="shift_change"
        )

        print(result['sbar_report'])
        # Output:
        # **Situation:** 65yo male, chest pain x2h, vitals stable
        # **Background:** Hx of MI 2018, on aspirin, metoprolol
        # **Assessment:** Possible STEMI, EKG shows ST elevation
        # **Recommendation:** Activate cath lab, continue monitoring
        ```

    !!! warning "HIPAA Compliance Requirements"
        To maintain HIPAA compliance:

        1. ✅ Enable security: `EmpathyLLM(enable_security=True)`
        2. ✅ Use encryption at rest for stored data
        3. ✅ Review audit logs daily
        4. ✅ Implement access controls
        5. ✅ Sign Business Associate Agreement with LLM provider

    **See Also:** [SBAR Clinical Handoff Example](../examples/sbar-clinical-handoff.md)

=== ":fontawesome-solid-building-columns: Finance"

    ## Finance Wizard

    **SOC2-compliant AI assistant** for financial services with enhanced PII/PCI protection.

    ### Key Features

    - :material-credit-card: **PCI DSS Compliance** - Credit card detection and masking
    - :material-bank: **Financial PII** - Account numbers, routing numbers, SSN
    - :material-chart-line: **Risk Analysis** - AML, fraud detection, compliance checks
    - :material-file-document: **Audit Trail** - SOC2 Type II compliant logging

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import FinanceWizard

    wizard = FinanceWizard(llm)

    # Analyze transaction for compliance
    result = await wizard.analyze_transaction(
        transaction_data={
            "amount": 15000,
            "source_account": "****1234",
            "destination_account": "****5678",
            "country": "US"
        },
        check_aml=True,
        check_fraud=True
    )

    if result['flags']:
        print(f"⚠️  Compliance flags: {result['flags']}")
    ```

    ??? info "What Financial PII Is Protected?"

        - **Credit Card Numbers** - Full card number detection and masking
        - **Account Numbers** - Bank account numbers
        - **Routing Numbers** - ABA routing numbers
        - **SSN** - Social Security Numbers
        - **ITIN** - Individual Taxpayer Identification Numbers
        - **EIN** - Employer Identification Numbers
        - **Investment Account IDs** - Brokerage account numbers

    !!! tip "Risk Analysis Features"
        The Finance Wizard includes built-in risk analysis:

        - **AML (Anti-Money Laundering)** - Flags suspicious transactions
        - **Fraud Detection** - Pattern-based fraud indicators
        - **Sanctions Screening** - OFAC compliance checks
        - **KYC Validation** - Know Your Customer verification

=== ":fontawesome-solid-scale-balanced: Legal"

    ## Legal Wizard

    **AI assistant** for legal practices with document classification and privilege protection.

    ### Key Features

    - :material-gavel: **Attorney-Client Privilege** - Automatic privilege detection
    - :material-file-document-multiple: **Document Classification** - Contract, brief, discovery types
    - :material-text-search: **Legal Citation** - Find relevant case law
    - :material-shield-lock: **Confidentiality** - Work product protection

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import LegalWizard

    wizard = LegalWizard(llm)

    # Analyze legal document
    result = await wizard.analyze_document(
        document_text="...",
        document_type="contract",
        jurisdiction="CA"
    )

    print(result['risk_factors'])
    print(result['suggested_clauses'])
    ```

    ??? example "Contract Review"

        ```python
        # Review contract for risks
        result = await wizard.review_contract(
            contract_text="...",
            contract_type="employment",
            jurisdiction="CA",
            check_for=[
                "non_compete",
                "indemnification",
                "termination",
                "ip_assignment"
            ]
        )

        # Get risk assessment
        for risk in result['risks']:
            print(f"{risk['severity']}: {risk['description']}")
            print(f"Suggested fix: {risk['remediation']}")
        ```

=== ":fontawesome-solid-cart-shopping: Retail"

    ## Retail Wizard

    **AI assistant** for e-commerce and retail operations.

    ### Key Features

    - :material-cart: **Inventory Management** - Stock optimization suggestions
    - :material-tag: **Pricing Strategy** - Dynamic pricing recommendations
    - :material-account-group: **Customer Service** - Support automation
    - :material-chart-box: **Sales Analytics** - Trend analysis

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import RetailWizard

    wizard = RetailWizard(llm)

    # Optimize inventory
    result = await wizard.optimize_inventory(
        product_data={
            "sku": "PROD123",
            "current_stock": 50,
            "sales_last_30d": 120,
            "season": "winter"
        }
    )

    print(result['reorder_quantity'])
    print(result['optimal_price'])
    ```

=== ":fontawesome-solid-graduation-cap: Education"

    ## Education Wizard

    **FERPA-compliant AI assistant** for educational institutions.

    ### Key Features

    - :material-school: **Student Privacy** - FERPA compliance (20 U.S.C. § 1232g)
    - :material-account-student: **Student PII Protection** - Student IDs, grades, records
    - :material-calendar-check: **Assignment Grading** - Automated assessment assistance
    - :material-book-open: **Curriculum Support** - Lesson plan generation

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import EducationWizard

    wizard = EducationWizard(llm)

    # Generate lesson plan (no student PII exposed)
    result = await wizard.generate_lesson_plan(
        subject="Mathematics",
        grade_level=8,
        topic="Linear Equations",
        duration_minutes=45
    )

    print(result['lesson_plan'])
    print(result['assessment_questions'])
    ```

=== ":fontawesome-solid-users: HR"

    ## HR Wizard

    **AI assistant** for human resources with employee PII protection.

    ### Key Features

    - :material-account-box: **Employee PII Protection** - SSN, DOB, salary, benefits
    - :material-clipboard-text: **Job Descriptions** - Generate JD from requirements
    - :material-account-search: **Resume Screening** - Bias-free candidate evaluation
    - :material-shield-account: **Compliance** - EEOC, ADA, FLSA guidance

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import HRWizard

    wizard = HRWizard(llm)

    # Generate job description
    result = await wizard.generate_job_description(
        title="Senior Software Engineer",
        department="Engineering",
        level="Senior",
        requirements=["Python", "AWS", "5+ years experience"]
    )

    print(result['job_description'])
    ```

=== ":fontawesome-solid-microchip: Technology"

    ## Technology Wizard

    **AI assistant** for software development and IT operations.

    ### Key Features

    - :material-bug: **Bug Analysis** - Root cause identification
    - :material-code-tags: **Code Review** - Security and quality checks
    - :material-cloud: **Cloud Architecture** - AWS/Azure/GCP design patterns
    - :material-security: **Security Scanning** - Vulnerability detection

    ### Quick Example

    ```python
    from empathy_llm_toolkit.wizards import TechnologyWizard

    wizard = TechnologyWizard(llm)

    # Analyze code for security issues
    result = await wizard.review_code(
        code=code_snippet,
        language="python",
        check_for=["sql_injection", "xss", "secrets"]
    )

    for issue in result['security_issues']:
        print(f"{issue['severity']}: {issue['description']}")
    ```

=== ":fontawesome-solid-briefcase: More Industries"

    ## Additional Wizards

    ### Accounting Wizard
    **AI assistant for accounting and bookkeeping**
    - GAAP/IFRS compliance
    - Financial statement analysis
    - Tax preparation assistance

    ### Customer Support Wizard
    **AI assistant for customer service operations**
    - Ticket classification
    - Response templates
    - Sentiment analysis

    ### Government Wizard
    **AI assistant for government agencies**
    - FOIA compliance
    - Public records management
    - Citizen service automation

    ### Insurance Wizard
    **AI assistant for insurance operations**
    - Claims processing
    - Underwriting assistance
    - Risk assessment

    ### Logistics Wizard
    **AI assistant for supply chain and logistics**
    - Route optimization
    - Inventory forecasting
    - Shipment tracking

    ### Manufacturing Wizard
    **AI assistant for manufacturing operations**
    - Production scheduling
    - Quality control
    - Equipment maintenance

    ### Real Estate Wizard
    **AI assistant for real estate professionals**
    - Property valuation
    - Lease generation
    - Market analysis

    ### Research Wizard
    **AI assistant for academic and scientific research**
    - Literature review
    - Citation management
    - Data analysis

    ### Sales Wizard
    **AI assistant for sales teams**
    - Lead qualification
    - Proposal generation
    - CRM integration

---

## Base Wizard API

All wizards extend the `BaseWizard` class with common functionality:

::: empathy_llm_toolkit.wizards.BaseWizard
    options:
      show_root_heading: false
      show_source: false
      heading_level: 3

### WizardConfig

::: empathy_llm_toolkit.wizards.WizardConfig
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Configuration options:**

- `name` (str): Wizard identifier
- `domain` (str): Industry domain (healthcare, finance, legal, etc.)
- `default_empathy_level` (int): Empathy level 0-4 (default: 2)
- `enable_security` (bool): Enable PII/secrets detection
- `pii_patterns` (list): Custom PII patterns to detect
- `enable_secrets_detection` (bool): Scan for API keys, passwords
- `audit_all_access` (bool): Log all wizard interactions
- `retention_days` (int): Audit log retention (default: 180 days)
- `default_classification` (str): Data classification (PUBLIC, INTERNAL, SENSITIVE)

---

## Creating Custom Wizards

!!! tip "Build Your Own Domain-Specific Wizard"

    You can create custom wizards for your specific industry:

```python
from empathy_llm_toolkit.wizards import BaseWizard, WizardConfig
from empathy_llm_toolkit import EmpathyLLM

class MyIndustryWizard(BaseWizard):
    """Custom wizard for my industry"""

    def __init__(self, llm: EmpathyLLM):
        config = WizardConfig(
            name="my_industry",
            domain="custom",
            description="AI assistant for my industry",
            enable_security=True,
            pii_patterns=["custom_pattern"],
            default_classification="INTERNAL"
        )
        super().__init__(llm, config)

    async def process(self, user_input: str, user_id: str):
        """Custom processing logic"""

        # Add domain-specific prompts
        enhanced_prompt = f"""
        You are an AI assistant specialized in {self.config.domain}.

        User request: {user_input}
        """

        # Use parent LLM with security enabled
        response = await self.llm.interact(
            user_id=user_id,
            prompt=enhanced_prompt,
            context={"wizard": self.config.name}
        )

        return response

# Use your custom wizard
llm = EmpathyLLM(provider="anthropic", api_key="...")
wizard = MyIndustryWizard(llm)

result = await wizard.process(
    user_input="Help me with industry-specific task",
    user_id="user@company.com"
)
```

---

## Security Best Practices

!!! warning "Production Security Checklist"

    **For all wizards in production:**

    - [ ] Enable security features: `enable_security=True`
    - [ ] Configure appropriate PII patterns for your industry
    - [ ] Enable secrets detection: `enable_secrets_detection=True`
    - [ ] Enable audit logging: `audit_all_access=True`
    - [ ] Set correct data classification
    - [ ] Review audit logs regularly
    - [ ] Test PII scrubbing before production
    - [ ] Implement access controls
    - [ ] Encrypt data at rest
    - [ ] Sign appropriate compliance agreements (BAA for HIPAA, DPA for GDPR)

!!! info "Classification Levels"

    **PUBLIC** - No PII, can be shared publicly

    **INTERNAL** - Internal business data, PII scrubbed

    **SENSITIVE** - PHI, financial data, legal privileged - requires encryption

---

## See Also

- [LLM Toolkit](llm-toolkit.md) - Core LLM functionality
- [Security Architecture](../guides/security-architecture.md) - Security implementation details
- [SBAR Example](../examples/sbar-clinical-handoff.md) - Healthcare wizard in action
- [Configuration](config.md) - Wizard configuration options
