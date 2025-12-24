# Security Architecture

Comprehensive security implementation for enterprise AI applications with PII protection, secrets detection, and compliance logging.

---

## Overview

The Empathy Framework implements a **defense-in-depth security model** with multiple layers of protection:

1. **Input Sanitization** - PII scrubbing before LLM processing
2. **Secrets Detection** - Automatic detection of API keys, passwords, tokens
3. **Audit Logging** - JSONL audit trail for compliance (HIPAA, GDPR, SOC2)
4. **Encryption at Rest** - AES-256-GCM for sensitive data
5. **Access Controls** - Role-based access control (RBAC) for wizards

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      User Input                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              1. PII Scrubber                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • SSN, Credit Cards, Phone Numbers                  │    │
│  │ • Healthcare: MRN, Patient ID, DOB, Insurance       │    │
│  │ • Financial: Account Numbers, Routing Numbers       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ (Scrubbed Text)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              2. Secrets Detector                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • API Keys (AWS, Stripe, GitHub, OpenAI)            │    │
│  │ • OAuth Tokens, JWT                                 │    │
│  │ • Private Keys (RSA, SSH)                           │    │
│  │ • Database Connection Strings                       │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ (Validated Text)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              3. Audit Logger                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • User ID, Timestamp, Action                        │    │
│  │ • PII Items Removed, Secrets Detected               │    │
│  │ • JSONL Format for SIEM Integration                 │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ (Logged)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              4. LLM Processing                               │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ • OpenAI, Anthropic, Google, etc.                   │    │
│  │ • Receives ONLY scrubbed, validated text            │    │
│  │ • No PII or secrets sent to external APIs           │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────┬───────────────────────────────────────┘
                      │ (Response)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   User Response                              │
└─────────────────────────────────────────────────────────────┘
```

---

## PII Scrubbing

### Standard PII Patterns

Automatically detected and removed:

| Type | Pattern | Example |
|------|---------|---------|
| SSN | `\b\d{3}-\d{2}-\d{4}\b` | `123-45-6789` |
| Credit Card | Luhn algorithm | `4111-1111-1111-1111` |
| Phone (US) | `\b\d{3}-\d{3}-\d{4}\b` | `555-123-4567` |
| Email | RFC 5322 | `user@example.com` |
| IP Address | IPv4/IPv6 | `192.168.1.1` |

### Healthcare-Specific PHI

For Healthcare Wizards (HIPAA compliance):

| Type | Pattern | Example |
|------|---------|---------|
| MRN | `\bMRN:?\s*\d{6,10}\b` | `MRN: 123456` |
| Patient ID | `\bPT\d{6,10}\b` | `PT123456` |
| DOB | `\b\d{1,2}/\d{1,2}/\d{4}\b` | `01/15/1980` |
| Insurance ID | `\bINS\d{8,12}\b` | `INS12345678` |
| Provider NPI | `\b\d{10}\b` (validated) | `1234567890` |

### Implementation Example

```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.security import PIIScrubber

# Initialize with security enabled
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_security=True  # Enables PII scrubbing
)

# Example with PHI
user_input = """
Patient John Doe (SSN: 123-45-6789, MRN: 987654)
called from 555-123-4567 about diabetes medication.
"""

# Process with automatic PII scrubbing
response = await llm.interact(
    user_id="doctor@hospital.com",
    user_input=user_input,
    context={"classification": "SENSITIVE"}
)

# PHI is automatically removed before sending to LLM
# Audit log records: ['ssn', 'mrn', 'phone', 'name']
```

---

## Secrets Detection

### Supported Secret Types

| Type | Detection Method | Example Pattern |
|------|------------------|-----------------|
| AWS Access Key | `AKIA[0-9A-Z]{16}` | `AKIAIOSFODNN7EXAMPLE` |
| Stripe API Key | `sk_live_[0-9a-zA-Z]{24}` | `sk_live_...` |
| GitHub Token | `ghp_[0-9a-zA-Z]{36}` | `ghp_...` |
| OpenAI API Key | `sk-[0-9a-zA-Z]{48}` | `sk-...` |
| JWT | Base64 + signature validation | `eyJ...` |
| Private Keys | `-----BEGIN PRIVATE KEY-----` | RSA/SSH keys |

### Implementation Example

```python
from empathy_llm_toolkit.security import SecretsDetector

detector = SecretsDetector()

code_snippet = """
import openai
openai.api_key = "sk-XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
"""

# Detect secrets
detections = detector.detect(code_snippet)

for secret in detections:
    print(f"⚠️ {secret.secret_type}: Line {secret.line}")
    print(f"   Severity: {secret.severity}")
    print(f"   Recommendation: {secret.remediation}")

# Output:
# ⚠️ OPENAI_API_KEY: Line 2
#    Severity: HIGH
#    Recommendation: Remove from code, use environment variables
```

---

## Audit Logging

### Log Format (JSONL)

```json
{
  "timestamp": "2025-11-25T10:30:00Z",
  "event_id": "evt_abc123",
  "user_id": "doctor@hospital.com",
  "action": "llm_interaction",
  "classification": "SENSITIVE",
  "security": {
    "pii_scrubbed": 4,
    "pii_types": ["ssn", "mrn", "phone", "name"],
    "secrets_detected": 0,
    "encryption_used": true
  },
  "performance": {
    "duration_ms": 1234,
    "tokens_used": 500
  },
  "compliance": {
    "hipaa_compliant": true,
    "retention_days": 90
  }
}
```

### Compliance Requirements

| Regulation | Retention | Encryption | Audit Trail |
|------------|-----------|------------|-------------|
| **HIPAA** | 90 days minimum | AES-256-GCM required | All PHI access |
| **GDPR** | Data subject request | At rest + in transit | All processing |
| **SOC2** | 180 days | Recommended | All access |

### Implementation Example

```python
from empathy_llm_toolkit.security import AuditLogger

logger = AuditLogger(
    log_file="/var/log/empathy/audit.jsonl",
    retention_days=90  # HIPAA minimum
)

# Automatically logs all interactions when security is enabled
logger.log_interaction(
    user_id="doctor@hospital.com",
    action="view_patient_record",
    classification="SENSITIVE",
    pii_scrubbed=4,
    secrets_detected=0
)

# Query audit logs
logs = logger.query(
    user_id="doctor@hospital.com",
    start_date="2025-11-01",
    end_date="2025-11-30"
)

print(f"Total interactions: {len(logs)}")
print(f"Total PII scrubbed: {sum(log['security']['pii_scrubbed'] for log in logs)}")
```

---

## Encryption

### Data at Rest

AES-256-GCM encryption for sensitive data:

```python
from empathy_llm_toolkit.security import encrypt_sensitive_data

# Encrypt PHI before storing
encrypted_data = encrypt_sensitive_data(
    data={"patient_id": "PT123456", "diagnosis": "Diabetes Type 2"},
    encryption_key=os.getenv("ENCRYPTION_KEY"),  # 32-byte key
    classification="SENSITIVE"
)

# Store encrypted data
database.store(encrypted_data)

# Decrypt when needed (with authorization)
decrypted = decrypt_sensitive_data(
    encrypted_data,
    encryption_key=os.getenv("ENCRYPTION_KEY")
)
```

### Data in Transit

All API communications use TLS 1.2+:

```python
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_security=True,
    tls_verify=True  # Enforce TLS certificate validation
)
```

---

## Access Controls

### Role-Based Access Control (RBAC)

```python
from empathy_llm_toolkit.wizards import HealthcareWizard
from empathy_llm_toolkit.security import AccessControl

# Define roles
access_control = AccessControl()
access_control.add_role("physician", permissions=["read_phi", "write_phi"])
access_control.add_role("nurse", permissions=["read_phi"])
access_control.add_role("admin", permissions=["read_phi", "write_phi", "view_audit_logs"])

# Check permissions before granting access
if access_control.has_permission(user_role="nurse", permission="read_phi"):
    wizard = HealthcareWizard(llm)
    result = await wizard.process(
        user_input="Patient handoff for bed 312",
        user_id="nurse@hospital.com"
    )
```

---

## Best Practices

### ✅ Do

1. **Always enable security** for production: `enable_security=True`
2. **Use environment variables** for API keys and encryption keys
3. **Review audit logs** daily for suspicious activity
4. **Implement access controls** for sensitive operations
5. **Encrypt data at rest** for SENSITIVE classification
6. **Test PII scrubbing** before production deployment
7. **Sign BAA agreements** with LLM providers (for HIPAA)

### ❌ Don't

1. **Never disable security** in production
2. **Never commit secrets** to version control
3. **Never skip encryption** for healthcare data
4. **Never ignore audit log alerts**
5. **Never share encryption keys** across environments
6. **Never bypass access controls** for convenience

---

## Security Testing

### PII Scrubbing Test

```python
import pytest
from empathy_llm_toolkit.security import PIIScrubber

def test_pii_scrubbing():
    scrubber = PIIScrubber()

    text = "Patient SSN 123-45-6789 called from 555-123-4567"
    scrubbed = scrubber.scrub(text)

    # Verify PII removed
    assert "123-45-6789" not in scrubbed
    assert "555-123-4567" not in scrubbed

    # Verify scrubbed items tracked
    items = scrubber.get_scrubbed_items(text)
    assert len(items) == 2
    assert any(item['type'] == 'ssn' for item in items)
```

### Secrets Detection Test

```python
def test_secrets_detection():
    detector = SecretsDetector()

    code = 'api_key = "sk_live_XXXXXXXXXXXXXXXXXXXXXXXXXXXX"'
    detections = detector.detect(code)

    assert len(detections) > 0
    assert detections[0].secret_type == SecretType.STRIPE_KEY
```

---

## See Also

- [HIPAA Compliance Guide](hipaa-compliance.md) - Healthcare-specific requirements
- [LLM Toolkit API](../reference/llm-toolkit.md) - Security API reference
- [Industry Wizards](../reference/wizards.md) - Domain-specific security
- [SBAR Example](../tutorials/examples/sbar-clinical-handoff.md) - Healthcare security in action
