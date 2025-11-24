# Enterprise Security Policy - Production Template
# Location: /etc/claude/CLAUDE.md
# Managed by: Security & Compliance Team
# Version: 1.0.0
# Classification: INTERNAL

## 🔒 MANDATORY SECURITY CONTROLS

These policies apply to ALL users, ALL projects, and CANNOT be overridden.

### PII Protection (GDPR Art. 5, HIPAA §164.514)

**BEFORE processing ANY user input or code:**

1. **Scan for PII using these patterns:**
   - Email: `user@domain.com` → `[EMAIL]`
   - Phone: `555-123-4567` → `[PHONE]`
   - SSN: `123-45-6789` → `[SSN]`
   - Credit Card: `4532-1234-5678-9010` → `[CC]`
   - Names: Context-dependent → `[NAME]` (when with PII)
   - Addresses: Full addresses → `[ADDRESS]`

2. **Log PII detection count** (not content) to audit trail

3. **Never store PII in MemDocs** - scrub first, then store

### Secrets Detection (OWASP Top 10 A02:2021)

**BEFORE sending to LLM or storing in MemDocs:**

**BLOCK these patterns:**
```regex
API_KEY_PATTERN = (api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})
PASSWORD_PATTERN = (password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)
PRIVATE_KEY_PATTERN = -----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----
AWS_KEY_PATTERN = (AKIA|ASIA)[A-Z0-9]{16}
GITHUB_TOKEN_PATTERN = ghp_[a-zA-Z0-9]{36}
SLACK_TOKEN_PATTERN = xox[baprs]-[a-zA-Z0-9-]+
```

**Actions on detection:**
1. Block the request immediately
2. Log security violation (pattern type, not value)
3. Alert security team if HIGH severity
4. Return error: "Secrets detected. Cannot proceed. Please remove sensitive data."

### Audit Logging (SOC2 CC7.2)

**Log EVERY interaction with:**
```json
{
  "timestamp": "ISO-8601",
  "event_id": "unique_uuid",
  "user_id": "email or ID",
  "action": "llm_request|store_pattern|retrieve_pattern",
  "empathy_level": 1-5,
  "memory_sources": ["enterprise", "user", "project"],
  "pii_detected": 0,
  "secrets_detected": 0,
  "classification": "PUBLIC|INTERNAL|SENSITIVE",
  "memdocs_patterns": ["pattern_ids"],
  "status": "success|failed|blocked",
  "error": "if failed"
}
```

**Log location:** `/var/log/empathy/audit.jsonl` (append-only)

### MemDocs Classification (Required)

**Every pattern MUST be classified:**

**PUBLIC** (Shareable, anonymized):
- General coding patterns
- Public algorithm implementations
- Open-source examples
- **Retention:** 365 days
- **Encryption:** No
- **Access:** All authenticated users

**INTERNAL** (Company confidential):
- Proprietary algorithms
- Internal architecture patterns
- Team-specific workflows
- **Retention:** 180 days
- **Encryption:** Optional
- **Access:** Project team only

**SENSITIVE** (Regulated data):
- Healthcare patterns (HIPAA)
- Financial patterns (PCI-DSS)
- Personal data patterns (GDPR)
- **Retention:** 90 days
- **Encryption:** AES-256-GCM required
- **Access:** Explicit permission only
- **Audit:** Log all access

**Classification Detection:**
```python
# Auto-classify based on keywords
if any(kw in content.lower() for kw in ["patient", "medical", "health", "diagnosis"]):
    classification = "SENSITIVE"  # HIPAA
elif any(kw in content.lower() for kw in ["credit", "payment", "card"]):
    classification = "SENSITIVE"  # PCI-DSS
elif any(kw in content.lower() for kw in ["proprietary", "confidential", "internal"]):
    classification = "INTERNAL"
else:
    classification = "PUBLIC"
```

### Air-Gapped Mode (Optional)

**When enabled (`EMPATHY_AIR_GAPPED=true`):**
- ✅ Local models only (Ollama)
- ✅ Local MemDocs storage (SQLite)
- ✅ Local CLAUDE.md files only
- ❌ NO external API calls
- ❌ NO cloud storage
- ❌ NO external logging services

**Use cases:**
- Classified government projects
- HIPAA-compliant healthcare
- Financial services (SOX compliance)
- Research with sensitive data

---

## 🎯 IMPLEMENTATION GUIDANCE

### For Developers

**Every LLM call must:**
```python
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig

# 1. Load enterprise security policies
config = ClaudeMemoryConfig(
    enabled=True,
    load_enterprise=True,  # Loads this file
    load_user=True,
    load_project=True
)

# 2. Initialize with memory
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    claude_memory_config=config,
    project_root="."
)

# 3. Security policies from this file are now enforced
# Memory will be prepended to EVERY system prompt
```

### For Security Team

**Monitoring dashboard should track:**
- PII detection rate (by user, by project)
- Secrets detection events
- Classification distribution (PUBLIC/INTERNAL/SENSITIVE)
- MemDocs access patterns
- Policy violations
- Retention policy compliance

**Alert thresholds:**
- Secrets detection: Immediate (HIGH)
- PII detection rate >10%: Review (MEDIUM)
- Policy violation: After 3 violations (HIGH)
- Classification errors: After 5 errors (LOW)

---

## 📋 COMPLIANCE CHECKLIST

**Before deploying to production:**
- [ ] Enterprise CLAUDE.md deployed to `/etc/claude/CLAUDE.md`
- [ ] All users acknowledged security policies
- [ ] Audit logging infrastructure operational
- [ ] Secrets detection tested with known patterns
- [ ] PII scrubbing tested with sample data
- [ ] MemDocs classification rules validated
- [ ] Retention policies automated
- [ ] Access controls enforced
- [ ] Encryption keys rotated (for SENSITIVE)
- [ ] Security team trained on monitoring

---

## 🚨 VIOLATION RESPONSE

**Level 1: Warning** (Secrets detected, PII in MemDocs)
- Block action
- Log violation
- Send warning email to user
- Manager notification after 3 violations

**Level 2: Suspension** (Repeated violations, policy circumvention attempts)
- Temporarily disable user access
- Security team review required
- Mandatory re-training

**Level 3: Termination** (Malicious activity, data exfiltration)
- Permanent access revocation
- Legal review
- Incident response procedure

---

## 📝 VERSION HISTORY

- **v1.0.0** (2025-11-24): Initial enterprise security policy
  - PII protection
  - Secrets detection
  - Audit logging
  - MemDocs classification
  - Air-gapped mode support

---

## 📞 SUPPORT

**Security Questions:** security@company.com
**Policy Updates:** Submit ticket to IT-Security team
**Violations:** Report to security@company.com (anonymous)
**Training:** Monthly security awareness training required

---

**ACKNOWLEDGMENT REQUIRED**

By using Empathy Framework, you acknowledge:
1. You have read and understood these security policies
2. You will comply with all requirements
3. You understand violations may result in disciplinary action
4. You will report security concerns immediately

**Signature:** _________________________ **Date:** __________

---

*This policy is maintained by the Security & Compliance Team.*
*Last reviewed: 2025-11-24*
*Next review: 2026-02-24 (quarterly)*
