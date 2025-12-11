# Empathy Framework - Production Security Configuration
# Location: ./.claude/CLAUDE.md
# Project: empathy-framework v1.9.4
# Classification: INTERNAL

## Project Context

**Empathy Framework** - Five-level AI collaboration system with anticipatory empathy and enterprise privacy controls.

**Security Posture:** INTERNAL with SENSITIVE components (healthcare wizards)

**Compliance Requirements:**
- GDPR (EU data protection)
- HIPAA (healthcare wizards)
- SOC2 (enterprise customers)

---

## 🔐 Security Implementation

### Memory + Pattern Storage Integration

**This project demonstrates secure integration of:**
1. Claude Memory (CLAUDE.md) - Instructions and policies
2. Long-Term Memory - Pattern storage with classification
3. Enterprise privacy controls

**When you interact with this codebase:**

The enterprise security policy from `/etc/claude/CLAUDE.md` is ALWAYS enforced first.
Then project-specific rules (this file) apply.

### Project-Specific PII Patterns

**In addition to enterprise PII rules, scrub:**

```python
HEALTHCARE_PII = {
    "mrn": r'\bMRN:?\s*\d{6,10}\b',  # Medical Record Number
    "patient_id": r'\bPT\d{6,10}\b',  # Patient ID
    "insurance_id": r'\bINS\d{8,12}\b',  # Insurance ID
    "dob": r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # Date of birth
}

SOFTWARE_PII = {
    "internal_id": r'\b[A-Z]{2,4}-\d{4,6}\b',  # JIRA tickets, etc.
    "database_conn": r'(postgresql|mysql|mongodb)://[^"\s]+',
}
```

### Pattern Classification Rules

**Code patterns:**

```python
def classify_pattern(content: str, pattern_type: str) -> str:
    """
    Classify patterns for this project.

    Returns: "PUBLIC" | "INTERNAL" | "SENSITIVE"
    """

    # Healthcare-related patterns = SENSITIVE
    healthcare_keywords = [
        "patient", "medical", "diagnosis", "treatment",
        "healthcare", "clinical", "hipaa", "phi"
    ]
    if any(kw in content.lower() for kw in healthcare_keywords):
        return "SENSITIVE"

    # Proprietary empathy algorithms = INTERNAL
    proprietary_keywords = [
        "proprietary", "confidential", "internal",
        "anticipatory prediction", "level 5 systems",
        "trajectory analysis", "leverage points"
    ]
    if any(kw in content.lower() for kw in proprietary_keywords):
        return "INTERNAL"

    # General software patterns = PUBLIC (after PII scrubbing)
    return "PUBLIC"
```

**Storage configuration:**

```python
PATTERN_STORAGE_CONFIG = {
    "PUBLIC": {
        "location": "./patterns/public/",
        "encryption": False,
        "retention_days": 365,
        "description": "General-purpose patterns, shareable"
    },
    "INTERNAL": {
        "location": "./patterns/internal/",
        "encryption": False,  # Optional for INTERNAL
        "retention_days": 180,
        "description": "Empathy Framework proprietary patterns"
    },
    "SENSITIVE": {
        "location": "./patterns/sensitive/",
        "encryption": True,  # AES-256-GCM required
        "retention_days": 90,
        "encryption_key_env": "PATTERN_ENCRYPTION_KEY",
        "description": "Healthcare patterns (HIPAA-regulated)"
    }
}
```

---

## 🧪 Testing Security Controls

**Before committing code:**

```bash
# 1. Run security tests
pytest tests/test_security_controls.py -v

# 2. Test PII scrubbing
pytest tests/test_pii_scrubbing.py -v

# 3. Test secrets detection
pytest tests/test_secrets_detection.py -v

# 4. Test pattern classification
pytest tests/test_pattern_classification.py -v

# 5. Full test suite
pytest tests/test_claude_memory.py -v
```

**Expected results:**
- 100% PII scrubbing accuracy
- 0 false negatives on secrets detection
- Correct classification for all test patterns

---

## 📊 Audit Logging Format

**Project-specific audit fields:**

```json
{
  "timestamp": "2025-11-24T03:30:00Z",
  "event_id": "evt_abc123",
  "project": "empathy-framework",
  "version": "1.9.4",
  "user_id": "developer@company.com",
  "action": "llm_request",

  "empathy_level": 3,
  "wizard_used": "SecurityWizard",

  "memory": {
    "enterprise_loaded": true,
    "user_loaded": true,
    "project_loaded": true,
    "total_bytes": 2500
  },

  "pattern_storage": {
    "patterns_retrieved": ["pattern_xyz_security"],
    "patterns_stored": [],
    "classifications_used": ["INTERNAL", "PUBLIC"]
  },

  "security": {
    "pii_scrubbed": 0,
    "secrets_detected": 0,
    "classification_verified": true,
    "healthcare_pattern_detected": false
  },

  "performance": {
    "duration_ms": 1234,
    "tokens_used": 5000
  }
}
```

**Log location:** `/var/log/empathy/audit.jsonl`

---

## 🏥 Healthcare Wizard Special Rules

**When using healthcare-related wizards:**

```python
HEALTHCARE_WIZARDS = [
    "ClinicalProtocolMonitor",
    "HealthcareComplianceWizard",
    "MedicalDataWizard"
]

# ALWAYS:
# 1. Classify patterns as SENSITIVE
# 2. Encrypt before storing in long-term memory
# 3. Log with healthcare_pattern_detected: true
# 4. Apply 90-day retention policy (HIPAA minimum)
# 5. Audit all accesses
```

**Example:**

```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig

# Healthcare-specific configuration
config = ClaudeMemoryConfig(
    enabled=True,
    load_enterprise=True,  # Security policies
    load_user=True,
    load_project=True  # This file
)

llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    claude_memory_config=config,
    project_root="."
)

# This interaction will:
# 1. Load all security policies
# 2. Apply healthcare-specific PII scrubbing
# 3. Classify any stored patterns as SENSITIVE
# 4. Log to audit trail with healthcare flag
response = await llm.interact(
    user_id="doctor@hospital.com",
    user_input="Analyze this patient handoff protocol",
    context={
        "wizard": "ClinicalProtocolMonitor",
        "classification": "SENSITIVE"
    }
)
```

---

## 🔍 Code Review Checklist

**For PRs that modify memory/pattern storage integration:**

- [ ] PII scrubbing tests updated
- [ ] Secrets detection patterns reviewed
- [ ] Classification logic verified
- [ ] Audit logging includes all required fields
- [ ] Healthcare patterns encrypted if applicable
- [ ] Retention policies enforced
- [ ] Access controls tested
- [ ] Documentation updated

**Security team review required for:**
- Changes to PII patterns
- Changes to secrets detection
- Changes to classification logic
- Changes to encryption implementation
- New wizard additions (especially healthcare)

---

## 📝 Example: Secure Pattern Storage

```python
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig
from empathy_llm_toolkit.security import SecurePatternStorage

# Initialize with security policies
config = ClaudeMemoryConfig(enabled=True)
storage = SecurePatternStorage(config)

# Example 1: Store PUBLIC pattern
pattern1 = """
# Software Pattern: Error Handling

When handling errors in async code:
1. Use try/except with specific exceptions
2. Log errors with context
3. Return user-friendly messages
"""

result = storage.store_pattern(
    pattern_content=pattern1,
    pattern_type="coding_pattern",
    user_id="dev@company.com",
    auto_classify=True  # Will classify as PUBLIC
)
# Result: {"pattern_id": "pat_123", "classification": "PUBLIC"}


# Example 2: Store INTERNAL pattern
pattern2 = """
# Empathy Framework: Level 4 Prediction

Our proprietary algorithm for 30-90 day predictions:
1. Analyze trajectory using confidence scoring
2. Identify leverage points
3. Generate actionable alerts
"""

result = storage.store_pattern(
    pattern_content=pattern2,
    pattern_type="algorithm",
    user_id="dev@company.com",
    auto_classify=True  # Will classify as INTERNAL
)
# Result: {"pattern_id": "pat_124", "classification": "INTERNAL"}


# Example 3: Store SENSITIVE pattern (healthcare)
pattern3 = """
# Clinical Protocol: Patient Handoff

SBAR communication format for patient handoffs:
S - Situation: Current patient status
B - Background: Medical history
A - Assessment: Clinical evaluation
R - Recommendation: Care plan
"""

# Must explicitly acknowledge SENSITIVE classification
result = storage.store_pattern(
    pattern_content=pattern3,
    pattern_type="clinical_protocol",
    user_id="doctor@hospital.com",
    auto_classify=True  # Will classify as SENSITIVE
)
# Result: {
#   "pattern_id": "pat_125",
#   "classification": "SENSITIVE",
#   "encryption": "AES-256-GCM",
#   "retention_days": 90
# }
```

---

## 🎓 Training Resources

**Required reading for contributors:**
1. `SECURE_MEMORY_ARCHITECTURE.md` - Complete security architecture
2. `ENTERPRISE_PRIVACY_INTEGRATION.md` - Privacy implementation roadmap
3. `examples/claude_memory/enterprise-CLAUDE-secure.md` - Enterprise policies

**Security training:** Monthly sessions with Security Team

**Certifications recommended:**
- HIPAA Privacy & Security (for healthcare wizards)
- GDPR Data Protection (for EU customers)
- Secure Coding Practices

---

## 🔄 Continuous Compliance

**Automated checks (CI/CD):**
```yaml
# .github/workflows/security.yml
- name: PII Detection Test
  run: pytest tests/test_pii_scrubbing.py --strict

- name: Secrets Scanning
  run: pytest tests/test_secrets_detection.py --strict

- name: Classification Verification
  run: pytest tests/test_pattern_classification.py --strict

- name: Audit Log Validation
  run: python scripts/validate_audit_logs.py
```

**Quarterly reviews:**
- Security policy effectiveness
- Classification accuracy
- Audit log completeness
- Retention policy compliance

---

## 📞 Project Contacts

**Security Questions:** security-team@company.com
**HIPAA Compliance:** hipaa-officer@company.com
**Code Review:** tech-lead@company.com
**General:** empathy-framework@company.com

---

## ✅ Acknowledgment

By working on this project, I confirm:
- ✅ I have read the enterprise security policy
- ✅ I understand healthcare data requires SENSITIVE classification
- ✅ I will not commit PII or secrets
- ✅ I will classify all patterns appropriately
- ✅ I will report security concerns immediately

---

*This configuration enforces enterprise security while enabling the five-level empathy system.*
*Last updated: 2025-11-24*
*Empathy Framework v1.9.4*
