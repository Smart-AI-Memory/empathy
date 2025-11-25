# LLM Toolkit

Enterprise-grade LLM integration with security controls and compliance features.

## Overview

The LLM Toolkit provides:

- **Unified LLM Interface**: Single API for multiple providers (Anthropic, OpenAI, Ollama)
- **Security Controls**: PII scrubbing, secrets detection, content filtering
- **Compliance**: HIPAA, GDPR, SOC2 audit logging
- **Claude Memory Integration**: CLAUDE.md support with MemDocs pattern storage
- **Healthcare Wizards**: FHIR, HL7, clinical protocol support

## Key Features

### Multi-Provider Support

```python
from empathy_llm_toolkit import EmpathyLLM

# Anthropic Claude (recommended)
claude = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-sonnet-4"
)

# OpenAI GPT
openai = EmpathyLLM(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4"
)

# Local Ollama
local = EmpathyLLM(
    provider="ollama",
    model="llama2"
)
```

### Automatic Security Controls

- **PII Scrubbing**: Removes SSN, credit cards, phone numbers, addresses
- **Secrets Detection**: Flags API keys, tokens, passwords
- **Audit Logging**: JSONL audit trail for compliance

## Class Reference

### EmpathyLLM

::: empathy_llm_toolkit.core.EmpathyLLM
    options:
      show_root_heading: false
      show_source: false
      heading_level: 4

Main LLM interface with empathy integration.

**Example:**
```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_os import EmpathyOS

# Initialize with security controls
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_pii_scrubbing=True,
    enable_secrets_detection=True,
    enable_audit_logging=True
)

# Integrate with EmpathyOS
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    llm_provider=llm
)

# Secure interaction
response = empathy.interact(
    user_id="user_123",
    user_input="Help me debug this API issue",
    context={}
)
```

### PIIScrubber

**Note**: Security features are being implemented. Full documentation coming soon.

Detect and scrub personally identifiable information.

**Detects:**
- SSN (Social Security Numbers)
- Credit card numbers
- Phone numbers (US and international)
- Email addresses
- Physical addresses
- Names (when configured)
- Healthcare identifiers (MRN, Patient ID)

**Example:**
```python
from empathy_llm_toolkit.security import PIIScrubber

scrubber = PIIScrubber()

# Text with PII
text = """
Patient John Doe (SSN: 123-45-6789)
called from 555-123-4567 about his
credit card ending in 4532.
"""

# Scrub PII
scrubbed = scrubber.scrub(text)
print(scrubbed)
# Output:
# Patient [NAME_REDACTED] (SSN: [SSN_REDACTED])
# called from [PHONE_REDACTED] about his
# credit card ending in [CREDIT_CARD_REDACTED].

# Get scrubbed items
items = scrubber.get_scrubbed_items(text)
for item in items:
    print(f"Found {item['type']}: {item['value']}")
```

### SecretsDetector

**Note**: Security features are being implemented. Full documentation coming soon.

Detect API keys, tokens, and credentials.

**Detects:**
- API keys (AWS, Stripe, GitHub, etc.)
- OAuth tokens
- Private keys
- Database connection strings
- JWT tokens

**Example:**
```python
from empathy_llm_toolkit.security import SecretsDetector

detector = SecretsDetector()

# Code with secrets
code = """
# Config
STRIPE_KEY = "sk_live_51HxJ..."
AWS_SECRET = "wJalrXUtnFEMI/K7MDENG..."
DB_CONN = "postgresql://user:pass@localhost/db"
"""

# Check for secrets
secrets = detector.detect(code)
if secrets:
    print("⚠️  Secrets detected!")
    for secret in secrets:
        print(f"  {secret['type']}: {secret['value'][:20]}...")
        print(f"  Line {secret['line']}, position {secret['position']}")
else:
    print("✓ No secrets detected")
```

### AuditLogger

**Note**: Security features are being implemented. Full documentation coming soon.

Compliance audit logging (HIPAA, GDPR, SOC2).

**Logs:**
- All LLM interactions
- PII scrubbing events
- Secrets detection events
- Security policy violations
- User access patterns

**Example:**
```python
from empathy_llm_toolkit.security import AuditLogger

logger = AuditLogger(
    log_path="logs/audit.jsonl",
    include_phi=False  # HIPAA: Don't log PHI
)

# Log LLM interaction
logger.log_llm_request(
    user_id="user_123",
    prompt="Help with deployment",
    model="claude-sonnet-4",
    tokens=1500
)

# Log security event
logger.log_pii_scrubbed(
    user_id="user_123",
    items_scrubbed=["ssn", "phone"],
    count=2
)

# Log access event
logger.log_access(
    user_id="user_123",
    resource="patient_records",
    action="read",
    success=True
)
```

## Security Features

### PII Scrubbing Patterns

```python
from empathy_llm_toolkit.security import PIIScrubber

# Default patterns
scrubber = PIIScrubber()

# Add custom patterns
scrubber.add_pattern(
    name="employee_id",
    pattern=r'\bEMP\d{6}\b',
    replacement="[EMP_ID_REDACTED]"
)

# Healthcare-specific patterns
scrubber.add_pattern(
    name="mrn",
    pattern=r'\bMRN:?\s*\d{6,10}\b',
    replacement="[MRN_REDACTED]"
)

text = "Employee EMP123456 accessed MRN: 987654"
scrubbed = scrubber.scrub(text)
print(scrubbed)
# Output: Employee [EMP_ID_REDACTED] accessed [MRN_REDACTED]
```

### Secrets Detection Configuration

```python
from empathy_llm_toolkit.security import SecretsDetector

detector = SecretsDetector(
    entropy_threshold=4.5,  # Lower = more sensitive
    allow_test_keys=True    # Allow obvious test keys
)

# Custom secret patterns
detector.add_pattern(
    name="internal_api_key",
    pattern=r'INTERNAL_[A-Za-z0-9]{32}',
    severity="high"
)

# Check code before committing
with open("config.py") as f:
    code = f.read()
    secrets = detector.detect(code)

    if secrets:
        print("⚠️  Do not commit! Secrets detected:")
        for secret in secrets:
            print(f"  Line {secret['line']}: {secret['type']}")
        exit(1)
```

### Audit Logging Format

```json
{
  "timestamp": "2025-01-20T15:30:00Z",
  "event_id": "evt_abc123",
  "event_type": "llm_request",
  "user_id": "user_123",
  "action": "interact",

  "request": {
    "provider": "anthropic",
    "model": "claude-sonnet-4",
    "prompt_length": 245,
    "tokens_used": 1500
  },

  "security": {
    "pii_scrubbed": 2,
    "secrets_detected": 0,
    "classification": "INTERNAL"
  },

  "empathy": {
    "level": 4,
    "confidence": 0.88,
    "predictions_count": 3
  },

  "performance": {
    "duration_ms": 1234,
    "trust_level": 0.72
  }
}
```

## Claude Memory Integration

### CLAUDE.md Support

```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig

# Configure Claude Memory
memory_config = ClaudeMemoryConfig(
    enabled=True,
    load_enterprise=True,  # /etc/claude/CLAUDE.md
    load_user=True,        # ~/.claude/CLAUDE.md
    load_project=True      # ./.claude/CLAUDE.md
)

# Initialize with memory
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    claude_memory_config=memory_config
)

# Memory is automatically loaded and included in context
response = llm.interact(
    user_id="user_123",
    prompt="Help with deployment",
    context={}
)

# Memory instructions from CLAUDE.md are automatically followed
```

### MemDocs Pattern Storage

```python
from empathy_llm_toolkit.secure_memdocs import SecureMemDocsIntegration

# Initialize with classification
memdocs = SecureMemDocsIntegration(
    claude_memory_config=memory_config,
    classification_mode="auto"  # or "PUBLIC", "INTERNAL", "SENSITIVE"
)

# Store pattern with automatic classification
pattern_data = """
# Deployment Best Practice

Always deploy on Monday mornings:
- Full team available
- Time to fix issues
- Avoid weekend emergencies
"""

result = memdocs.store_pattern(
    pattern_content=pattern_data,
    pattern_type="best_practice",
    user_id="user_123",
    auto_classify=True
)

print(f"Pattern stored: {result['pattern_id']}")
print(f"Classification: {result['classification']}")
# Output: Classification: PUBLIC
```

## Healthcare Wizards

### Clinical Protocol Monitor

```python
from empathy_llm_toolkit.wizards import ClinicalProtocolMonitor

# Monitor clinical handoffs
monitor = ClinicalProtocolMonitor(
    protocol="SBAR",  # Situation, Background, Assessment, Recommendation
    enable_hipaa_audit=True
)

# Process handoff
handoff_text = """
Situation: 65yo male, chest pain x2h
Background: Hx of MI, on aspirin
Assessment: STEMI suspected, vitals stable
Recommendation: Activate cath lab
"""

result = monitor.process_handoff(handoff_text)

if result.complete:
    print("✓ SBAR protocol complete")
else:
    print("⚠️  Missing components:")
    for component in result.missing:
        print(f"  - {component}")

if result.safety_flags:
    print("🚨 Safety flags:")
    for flag in result.safety_flags:
        print(f"  - {flag}")
```

### Healthcare Compliance Wizard

```python
from empathy_llm_toolkit.wizards import HealthcareComplianceWizard

wizard = HealthcareComplianceWizard(
    frameworks=["HIPAA", "HITECH", "FDA_21CFR11"]
)

# Check compliance of a system
result = wizard.check_compliance(
    system_description="Patient portal with EHR integration",
    features=[
        "patient_authentication",
        "data_encryption",
        "audit_logging",
        "access_controls"
    ]
)

print(f"Compliance score: {result.score:.0%}")

if result.violations:
    print("\n⚠️  Violations:")
    for violation in result.violations:
        print(f"  {violation.framework}: {violation.description}")
        print(f"  Severity: {violation.severity}")
        print(f"  Remediation: {violation.remediation}")
```

## Usage Patterns

### Complete Security Setup

```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.security import (
    PIIScrubber,
    SecretsDetector,
    AuditLogger
)

# Initialize security components
pii_scrubber = PIIScrubber()
secrets_detector = SecretsDetector()
audit_logger = AuditLogger(log_path="logs/audit.jsonl")

# Configure LLM with all security features
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_pii_scrubbing=True,
    enable_secrets_detection=True,
    enable_audit_logging=True,
    pii_scrubber=pii_scrubber,
    secrets_detector=secrets_detector,
    audit_logger=audit_logger
)

# All interactions are automatically secured
response = llm.interact(
    user_id="user_123",
    prompt="Help debug this error",
    context={}
)

# Security audit trail is automatically created
```

### Multi-Provider Fallback

```python
from empathy_llm_toolkit import EmpathyLLM

providers = [
    {"provider": "anthropic", "api_key": os.getenv("ANTHROPIC_API_KEY")},
    {"provider": "openai", "api_key": os.getenv("OPENAI_API_KEY")},
    {"provider": "ollama", "model": "llama2"}  # Local fallback
]

def interact_with_fallback(prompt, context):
    """Try providers in order until one succeeds"""
    for config in providers:
        try:
            llm = EmpathyLLM(**config)
            return llm.interact(
                user_id="user_123",
                prompt=prompt,
                context=context
            )
        except Exception as e:
            print(f"Provider {config['provider']} failed: {e}")
            continue

    raise Exception("All providers failed")
```

## Best Practices

### HIPAA-Compliant Setup

```python
# Healthcare application with HIPAA compliance
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),

    # Security controls
    enable_pii_scrubbing=True,
    enable_secrets_detection=True,
    enable_audit_logging=True,

    # Healthcare-specific
    healthcare_mode=True,
    phi_protection=True,

    # Audit configuration
    audit_config={
        "include_phi": False,  # Never log PHI
        "retention_days": 90,   # HIPAA minimum
        "encryption": "AES-256-GCM"
    }
)
```

### Production Security Checklist

- [ ] Enable PII scrubbing
- [ ] Enable secrets detection
- [ ] Enable audit logging
- [ ] Use encrypted storage (SQLite encryption or PostgreSQL + encryption at rest)
- [ ] Rotate API keys regularly
- [ ] Monitor audit logs daily
- [ ] Set up alerts for security events
- [ ] Test security controls monthly
- [ ] Review access patterns weekly

## See Also

- [EmpathyOS API](empathy-os.md)
- [Configuration API](config.md)
- [Healthcare SBAR Example](../examples/sbar-clinical-handoff.md)
- [Security Architecture](../guides/security-architecture.md)
