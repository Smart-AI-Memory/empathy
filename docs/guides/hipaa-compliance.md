# HIPAA Compliance Guide

Complete guide to achieving HIPAA compliance when using Empathy Framework for healthcare applications.

---

## Overview

The **Health Insurance Portability and Accountability Act (HIPAA)** requires specific protections for Protected Health Information (PHI). This guide covers how to configure Empathy Framework for HIPAA compliance.

!!! warning "Legal Disclaimer"
    This guide provides technical implementation guidance. Consult with legal counsel and HIPAA compliance experts for your specific use case. Empathy Framework provides tools to help achieve compliance but does not guarantee compliance on its own.

---

## HIPAA Requirements

### Privacy Rule (45 CFR Part 160, Part 164 Subparts A & E)

Protects individually identifiable health information:

- **Who**: Covered entities (healthcare providers, health plans, clearinghouses)
- **What**: PHI in any form (electronic, paper, oral)
- **How**: Minimum necessary access, patient consent

### Security Rule (45 CFR Part 164 Subparts A & C)

Requires safeguards for electronic PHI (ePHI):

1. **Administrative Safeguards** - Policies, procedures, training
2. **Physical Safeguards** - Facility access controls, workstation security
3. **Technical Safeguards** - Access controls, audit logs, encryption

### Breach Notification Rule (45 CFR Part 164 Subpart D)

Requires notification within **60 days** of discovering a breach affecting 500+ individuals.

---

## PHI vs PII

### Protected Health Information (PHI)

Any of the 18 HIPAA identifiers when combined with health information:

| Identifier | Example | Empathy Detection |
|------------|---------|-------------------|
| Names | `John Doe` | ✅ Name pattern |
| SSN | `123-45-6789` | ✅ SSN pattern |
| Medical Record Number | `MRN: 987654` | ✅ MRN pattern |
| Health Plan Number | `INS12345678` | ✅ Insurance ID pattern |
| Account Numbers | `ACCT-999888` | ✅ Account pattern |
| Certificate/License Numbers | `RN-123456` | ✅ License pattern |
| Device Identifiers | `DEVICE-XYZ` | ⚠️ Custom pattern |
| URLs/IPs | `192.168.1.1` | ✅ IP address pattern |
| Biometric Identifiers | Fingerprint, retina | ⚠️ Custom handling |
| Photos/Images | Patient photos | ⚠️ Custom handling |
| Dates (except year) | `01/15/2024` | ✅ DOB pattern |
| Phone Numbers | `555-123-4567` | ✅ Phone pattern |
| Fax Numbers | `555-987-6543` | ✅ Phone pattern |
| Email Addresses | `patient@email.com` | ✅ Email pattern |
| Geographic Subdivisions | Street address | ✅ Address pattern |
| Provider NPI | `1234567890` | ✅ NPI validation |

---

## Configuration for HIPAA Compliance

### 1. Enable Healthcare Mode

```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.wizards import HealthcareWizard

# HIPAA-compliant configuration
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_security=True,  # Required: Enable PII/PHI scrubbing
    classification="SENSITIVE",  # Required: PHI is sensitive data
    encryption_key=os.getenv("ENCRYPTION_KEY"),  # Required: AES-256-GCM
    audit_logging=True,  # Required: HIPAA §164.312(b)
    retention_days=90  # Minimum: HIPAA §164.528
)

# Use Healthcare Wizard for enhanced PHI protection
wizard = HealthcareWizard(llm)
```

### 2. Enhanced PHI Patterns

Healthcare Wizards include 10+ additional PHI patterns:

```python
HEALTHCARE_PII_PATTERNS = {
    "mrn": r'\bMRN:?\s*\d{6,10}\b',
    "patient_id": r'\bPT\d{6,10}\b',
    "dob": r'\b\d{1,2}/\d{1,2}/\d{4}\b',
    "insurance_id": r'\bINS\d{8,12}\b',
    "provider_npi": r'\b\d{10}\b',  # Validated against checksum
    "cpt_code": r'\b\d{5}\b',  # Medical procedure codes
    "icd_code": r'\b[A-Z]\d{2}(\.\d{1,2})?\b',  # Diagnosis codes
    "prescription": r'\bRX\d{6,10}\b',
    "lab_result": r'\bLAB\d{6,10}\b',
    "medication": MEDICATION_LIST  # Optional: configurable
}
```

### 3. Mandatory Encryption

All PHI must be encrypted at rest:

```python
from empathy_llm_toolkit.security import encrypt_phi

# Encrypt before storing
encrypted_record = encrypt_phi(
    data={
        "patient_id": "PT123456",
        "diagnosis": "Diabetes Type 2",
        "mrn": "MRN-987654"
    },
    encryption_key=os.getenv("ENCRYPTION_KEY"),  # 32-byte AES key
    algorithm="AES-256-GCM"  # NIST-approved
)

# Store encrypted data
database.store_encrypted(encrypted_record)
```

---

## Business Associate Agreement (BAA)

### LLM Provider BAAs

You **must** sign a Business Associate Agreement with your LLM provider:

| Provider | BAA Available | Notes |
|----------|---------------|-------|
| **Anthropic** | ✅ Yes | Enterprise plan required |
| **OpenAI** | ✅ Yes | Contact sales team |
| **Google** | ✅ Yes | Vertex AI for Healthcare |
| **Azure OpenAI** | ✅ Yes | Azure compliance tools |
| **AWS Bedrock** | ✅ Yes | HIPAA-eligible services |

!!! danger "Critical Requirement"
    **DO NOT** send PHI to LLM providers without a signed BAA. Doing so violates HIPAA and can result in fines up to **$1.5 million per year** per violation category.

### BAA Checklist

Before using Empathy Framework in production:

- [ ] Sign BAA with LLM provider
- [ ] Enable PHI scrubbing (`enable_security=True`)
- [ ] Configure encryption at rest
- [ ] Enable audit logging with 90-day retention
- [ ] Implement access controls
- [ ] Train staff on PHI handling procedures
- [ ] Document security policies
- [ ] Conduct risk assessment
- [ ] Test PHI scrubbing before go-live

---

## Audit Logging Requirements

### HIPAA §164.312(b) - Audit Controls

All access to ePHI must be logged:

```python
from empathy_llm_toolkit.security import AuditLogger

logger = AuditLogger(
    log_file="/var/log/empathy/hipaa_audit.jsonl",
    retention_days=90,  # Minimum retention
    encryption=True,  # Encrypt audit logs
    tamper_proof=True  # Prevent log deletion
)

# Automatically logs:
# - User ID (who accessed)
# - Timestamp (when)
# - Action (what was done)
# - PHI elements (which identifiers)
# - Success/failure
# - Source IP address
```

### Audit Log Format

```json
{
  "timestamp": "2025-11-25T14:30:00Z",
  "event_id": "evt_hipaa_123",
  "event_type": "phi_access",
  "user_id": "doctor@hospital.com",
  "user_role": "physician",
  "patient_id": "PT123456",  // Encrypted
  "action": "view_patient_record",
  "phi_elements": ["name", "dob", "mrn", "diagnosis"],
  "authorization": "patient_consent_2025-11-20",
  "source_ip": "10.0.1.50",
  "success": true,
  "classification": "PHI",
  "encryption": {
    "algorithm": "AES-256-GCM",
    "key_id": "key_2025_11"
  },
  "hipaa_compliance": {
    "minimum_necessary": true,
    "patient_consent": true,
    "baa_signed": true
  }
}
```

### Audit Log Review

Review logs **at least weekly** for:

- ❌ Unauthorized access attempts
- ❌ After-hours access without justification
- ❌ Bulk PHI downloads
- ❌ Access to records of VIP patients
- ❌ Multiple failed login attempts
- ✅ Successful access for patient care
- ✅ Authorized research access

---

## Minimum Necessary Standard

### HIPAA §164.502(b)

Only access the **minimum necessary** PHI to accomplish the task:

```python
from empathy_llm_toolkit.wizards import HealthcareWizard

wizard = HealthcareWizard(llm)

# Good: Request only what's needed
result = await wizard.generate_handoff(
    patient_id="PT123456",  # System looks up only handoff-relevant data
    protocol="SBAR",
    fields=["situation", "background", "assessment", "recommendation"]
)

# Bad: Requesting entire medical record
# result = await wizard.get_full_patient_record("PT123456")  # ❌ Not minimum necessary
```

---

## Patient Rights

### Right to Access (HIPAA §164.524)

Patients can request access to their records within **30 days**:

```python
# Generate patient-accessible summary (de-identified clinician notes)
summary = await wizard.generate_patient_summary(
    patient_id="PT123456",
    format="patient_friendly",  # Plain language, no medical jargon
    include_phi=True  # Patient has right to their own PHI
)
```

### Right to Amend (HIPAA §164.526)

Patients can request amendments:

```python
# Log amendment request
logger.log_amendment(
    patient_id="PT123456",
    requested_by="patient@email.com",
    field_to_amend="diagnosis",
    current_value="Type 1 Diabetes",
    requested_value="Type 2 Diabetes",
    status="pending_physician_review"
)
```

### Right to Accounting of Disclosures (HIPAA §164.528)

Patients can request 6-year history of PHI disclosures:

```python
# Query all PHI disclosures
disclosures = logger.query_disclosures(
    patient_id="PT123456",
    start_date="2019-11-25",  # 6 years back
    end_date="2025-11-25"
)

# Generate accounting report
report = generate_disclosure_report(disclosures)
```

---

## Breach Notification

### What Constitutes a Breach?

Unauthorized acquisition, access, use, or disclosure of PHI that compromises security or privacy.

### Response Plan

```python
from empathy_llm_toolkit.security import BreachDetector

detector = BreachDetector()

# Detect potential breaches
if detector.detect_breach(event):
    # 1. Contain the breach
    detector.contain_breach()

    # 2. Assess risk
    risk = detector.assess_risk(event)

    if risk.affected_individuals >= 500:
        # 3. Notify HHS immediately
        notify_hhs(event)

    if risk.severity == "high":
        # 4. Notify affected individuals within 60 days
        notify_patients(event)

    # 5. Notify media if 500+ individuals in same state
    if risk.affected_individuals >= 500 and risk.same_state:
        notify_media(event)

    # 6. Document breach and response
    logger.log_breach(event)
```

---

## Testing HIPAA Compliance

### PHI Scrubbing Test

```python
def test_phi_scrubbing_comprehensive():
    from empathy_llm_toolkit.wizards import HealthcareWizard

    wizard = HealthcareWizard(llm)

    # Test input with multiple PHI elements
    input_text = """
    Patient: John Doe
    DOB: 01/15/1980
    SSN: 123-45-6789
    MRN: 987654
    Phone: 555-123-4567
    Insurance: INS12345678
    Provider NPI: 1234567890
    Diagnosis: ICD-10 E11.9 (Type 2 Diabetes)
    """

    result = await wizard.process(
        user_input=input_text,
        user_id="test@hospital.com"
    )

    # Verify ALL PHI was scrubbed
    assert "John Doe" not in result['llm_input']
    assert "123-45-6789" not in result['llm_input']
    assert "987654" not in result['llm_input']
    assert "555-123-4567" not in result['llm_input']
    assert "INS12345678" not in result['llm_input']

    # Verify audit log
    assert len(result['security_report']['phi_removed']) >= 8
```

### Encryption Test

```python
def test_encryption_aes_256_gcm():
    from empathy_llm_toolkit.security import encrypt_phi, decrypt_phi

    phi_data = {"patient_id": "PT123456", "diagnosis": "Diabetes"}

    # Encrypt
    encrypted = encrypt_phi(phi_data, os.getenv("ENCRYPTION_KEY"))

    # Verify encryption
    assert encrypted['algorithm'] == "AES-256-GCM"
    assert encrypted['encrypted_data'] != str(phi_data)

    # Decrypt
    decrypted = decrypt_phi(encrypted, os.getenv("ENCRYPTION_KEY"))

    assert decrypted == phi_data
```

---

## Compliance Checklist

### Before Production

- [ ] **BAA signed** with LLM provider
- [ ] **Security enabled**: `enable_security=True`
- [ ] **Encryption configured**: AES-256-GCM at rest
- [ ] **Audit logging enabled**: 90-day retention minimum
- [ ] **Access controls**: Role-based access (RBAC)
- [ ] **PHI testing**: 100% scrubbing accuracy verified
- [ ] **Staff training**: HIPAA awareness, PHI handling
- [ ] **Policies documented**: Security, privacy, breach response
- [ ] **Risk assessment**: Completed and documented
- [ ] **Incident response plan**: Tested and ready

### Ongoing Compliance

- [ ] **Weekly audit log review**
- [ ] **Quarterly security assessments**
- [ ] **Annual HIPAA training** for all staff
- [ ] **Annual risk assessment** update
- [ ] **Breach response drills** (semi-annual)
- [ ] **Vendor BAA renewals** (as needed)
- [ ] **Software updates** for security patches

---

## Common Violations & How to Avoid

| Violation | Fine Range | How to Avoid |
|-----------|------------|--------------|
| Sending PHI without BAA | $100 - $50,000 per violation | Sign BAA with LLM provider before production |
| No encryption at rest | $1,000 - $50,000 per violation | Configure `encryption_key` in EmpathyLLM |
| Inadequate audit logs | $1,000 - $50,000 per violation | Enable `audit_logging=True` with 90-day retention |
| Unauthorized access | $50,000 per violation | Implement RBAC, review access logs |
| Breach notification delay | $100 - $50,000 per violation | Test incident response plan |
| No patient consent | $100 - $50,000 per violation | Implement consent workflow |

**Maximum penalty**: $1.5 million per year per violation category

---

## ROI of HIPAA Compliance

For a **100-bed hospital**:

| Cost Item | Annual Cost |
|-----------|-------------|
| HIPAA violation (average) | -$2.5M |
| Empathy Framework (compliance) | $10K |
| **Net Savings** | **$2.49M** |

**Additional benefits**:
- ✅ Avoid breach notification costs ($200+ per patient)
- ✅ Maintain patient trust and reputation
- ✅ Enable AI innovation with confidence
- ✅ Reduce documentation time by 60%

---

## See Also

- [Security Architecture](security-architecture.md) - Technical implementation details
- [Healthcare Wizards](../api-reference/wizards.md) - PHI-aware AI assistants
- [SBAR Example](../examples/sbar-clinical-handoff.md) - HIPAA-compliant handoff protocol
- [LLM Toolkit](../api-reference/llm-toolkit.md) - Security API reference

---

## External Resources

- [HHS HIPAA Portal](https://www.hhs.gov/hipaa/index.html)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)
- [Breach Notification Rule](https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html)
- [OCR Audit Protocol](https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/audit/protocol/index.html)
