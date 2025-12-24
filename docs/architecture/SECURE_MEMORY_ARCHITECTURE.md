# Secure Memory Architecture for Enterprise Deployment
**Empathy Framework v1.8.0-alpha**

Integration of Claude Memory (CLAUDE.md) + MemDocs with enterprise security controls.

## Table of Contents
1. [Security Principles](#security-principles)
2. [Architecture Overview](#architecture-overview)
3. [Memory Hierarchy & Trust Boundaries](#memory-hierarchy--trust-boundaries)
4. [CLAUDE.md Security Prompts](#claudemd-security-prompts)
5. [MemDocs Integration Patterns](#memdocs-integration-patterns)
6. [Audit Trail Implementation](#audit-trail-implementation)
7. [Compliance Mapping](#compliance-mapping)

---

## Security Principles

### 1. Defense in Depth
- Multiple layers of security controls
- Each layer assumes previous layers may fail
- No single point of failure

### 2. Principle of Least Privilege
- Memory access based on minimum required permissions
- Enterprise > User > Project hierarchy enforces boundaries
- MemDocs patterns tagged with sensitivity levels

### 3. Data Minimization (GDPR Article 5)
- Only store patterns necessary for learning
- PII scrubbed before MemDocs storage
- Retention policies enforced

### 4. Auditability (SOC2, HIPAA)
- All memory access logged
- MemDocs pattern creation/retrieval tracked
- Tamper-evident audit logs

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    CLAUDE.md Memory Layer                    │
│  (Instructions, Security Policies, Privacy Rules)           │
│                                                              │
│  Enterprise ──▶ User ──▶ Project                            │
│  (Org policy)   (Personal) (Team rules)                     │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   EmpathyLLM (5 Levels)                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Security Controls (enforced via memory prompts)     │  │
│  │  - PII scrubbing                                     │  │
│  │  - Secret detection                                  │  │
│  │  - Audit logging                                     │  │
│  │  - Access controls                                   │  │
│  └──────────────────────────────────────────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      MemDocs Layer                          │
│  (Long-term Pattern Storage with Privacy Controls)          │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │  PUBLIC        │  │  INTERNAL      │  │  SENSITIVE   │  │
│  │  patterns      │  │  patterns      │  │  patterns    │  │
│  │  (shareable)   │  │  (team only)   │  │  (encrypted) │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## Memory Hierarchy & Trust Boundaries

### Enterprise Level (`/etc/claude/CLAUDE.md`)
**Purpose:** Organization-wide security policies
**Trust Boundary:** Highest - affects all users and projects
**Managed By:** Security team / IT administrators
**Cannot be overridden by:** User or Project memory

**Example Use Cases:**
- GDPR/HIPAA compliance requirements
- PII scrubbing rules
- Approved LLM providers
- Secrets scanning patterns
- Audit logging requirements

### User Level (`~/.claude/CLAUDE.md`)
**Purpose:** Personal preferences and workflows
**Trust Boundary:** Medium - user-specific settings
**Managed By:** Individual developer
**Cannot override:** Enterprise security policies
**Can customize:** Non-security preferences

**Example Use Cases:**
- Code style preferences
- Communication preferences
- Personal workflow shortcuts
- Learning style preferences

### Project Level (`./.claude/CLAUDE.md`)
**Purpose:** Team/project-specific rules
**Trust Boundary:** Lowest - project context
**Managed By:** Project team / tech leads
**Cannot override:** Enterprise or user security policies
**Can customize:** Project conventions, architecture patterns

**Example Use Cases:**
- Project architecture decisions
- Team coding standards
- Framework-specific guidelines
- Project-specific security rules (additive only)

---

## CLAUDE.md Security Prompts

### Enterprise Level Template

```markdown
# Enterprise Security Policy
# Location: /etc/claude/CLAUDE.md
# Managed by: Security Team
# Version: 1.0.0
# Last Updated: 2025-11-24

## CRITICAL: Security Controls (CANNOT BE OVERRIDDEN)

### 1. PII Protection (GDPR Article 5, HIPAA §164.514)

**BEFORE** sending ANY data to external LLM APIs, you MUST:

1. Scan for and redact PII:
   - Email addresses (replace with [EMAIL])
   - Phone numbers (replace with [PHONE])
   - Social Security Numbers (replace with [SSN])
   - Credit card numbers (replace with [CC])
   - IP addresses (replace with [IP])
   - Names (replace with [NAME])
   - Addresses (replace with [ADDRESS])

2. Use these regex patterns:
   ```python
   PII_PATTERNS = {
       "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
       "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
       "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
       "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
       "ipv4": r'\b(?:\d{1,3}\.){3}\d{1,3}\b',
   }
   ```

3. Log all PII detections (count only, not content) to audit trail

### 2. Secrets Detection (OWASP A02:2021)

**NEVER** send these to external APIs:
- API keys (e.g., `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`)
- Passwords or credentials
- Private keys (RSA, SSH, TLS)
- Database connection strings
- OAuth tokens
- JWT tokens

**Detection patterns:**
```python
SECRET_PATTERNS = {
    "api_key": r'(?i)(api[_-]?key|apikey|access[_-]?token)\s*[=:]\s*["\']?([a-zA-Z0-9_-]{20,})',
    "password": r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)["\']',
    "private_key": r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----',
    "aws_key": r'(?i)aws[_-]?(access[_-]?key[_-]?id|secret[_-]?access[_-]?key)',
}
```

### 3. Audit Logging (SOC2 CC7.2, HIPAA §164.312(b))

Log EVERY interaction with structured data:
```json
{
  "timestamp": "2025-11-24T03:30:00Z",
  "user_id": "user@company.com",
  "action": "llm_request",
  "empathy_level": 3,
  "provider": "anthropic",
  "model": "claude-sonnet-4",
  "pii_detected": 0,
  "secrets_detected": 0,
  "request_size_bytes": 1234,
  "response_size_bytes": 5678,
  "memory_sources": ["enterprise", "user", "project"],
  "memdocs_patterns_used": ["pattern_id_1", "pattern_id_2"],
  "sanitization_applied": true
}
```

### 4. MemDocs Privacy Controls

**Classification Required:** Every pattern stored in MemDocs MUST be tagged:
- `PUBLIC`: Can be shared across organization (anonymized)
- `INTERNAL`: Team/project only (no PII, no secrets)
- `SENSITIVE`: Encrypted at rest, access-controlled (healthcare, finance)

**Before storing in MemDocs:**
1. Apply PII scrubbing
2. Apply secrets detection
3. Classify sensitivity level
4. Add metadata: `created_by`, `created_at`, `classification`, `retention_days`
5. Log to audit trail

**Storage Rules:**
```python
MEMDOCS_RULES = {
    "PUBLIC": {
        "encryption": "not_required",
        "retention_days": 365,
        "access": "all_users"
    },
    "INTERNAL": {
        "encryption": "not_required",
        "retention_days": 180,
        "access": "project_team"
    },
    "SENSITIVE": {
        "encryption": "AES-256-GCM",
        "retention_days": 90,
        "access": "explicit_permission",
        "audit_all_access": true
    }
}
```

### 5. Air-Gapped Mode (Optional)

When `AIR_GAPPED_MODE=true`:
- NO external LLM API calls
- Use local models only (Ollama)
- MemDocs storage: local filesystem only
- Audit logs: local filesystem only
- Memory: local CLAUDE.md files only

### 6. Compliance Verification

On EVERY LLM request:
- [ ] PII scrubbing completed
- [ ] Secrets scanning completed
- [ ] Audit log entry created
- [ ] MemDocs classification verified
- [ ] Memory sources validated
- [ ] Retention policy enforced

---

## ENFORCEMENT

These policies are MANDATORY and CANNOT be overridden by:
- User-level CLAUDE.md
- Project-level CLAUDE.md
- Runtime configuration
- Code modifications (audit fails if attempted)

**Violation Response:**
1. Block the request
2. Log security violation with full context
3. Alert security team
4. Increment user's violation counter
5. Trigger review after 3 violations

---

**Version History:**
- v1.0.0 (2025-11-24): Initial enterprise security policy
```

---

### User Level Template

```markdown
# User Preferences
# Location: ~/.claude/CLAUDE.md
# User: developer@company.com

## Communication Style
- Prefer concise, technical responses
- Use bullet points for lists
- Include code examples
- Highlight security concerns with ⚠️

## Coding Standards
- Language: Python 3.10+
- Style: Black + Ruff
- Testing: pytest with 90%+ coverage
- Type hints: Required

## Work Context
- Team: Backend Platform Engineering
- Focus: API design, database optimization, security
- Timezone: US Pacific (PST/PDT)

## Learning Preferences
- Start with "why" before "how"
- Link to documentation when relevant
- Concrete examples before theory

## MemDocs Preferences
- Classify my patterns as INTERNAL by default
- Retention: 180 days (team standard)
- Review my patterns monthly

---

**Note:** These preferences do NOT override enterprise security policies.
I acknowledge all security controls from enterprise CLAUDE.md apply.
```

---

### Project Level Template

```markdown
# Project Memory: Empathy Framework
# Location: ./.claude/CLAUDE.md
# Project: empathy-framework
# Team: AI Platform

## Project Context
Empathy Framework - Five-level AI collaboration system with anticipatory empathy.

**Security Classification:** INTERNAL (some SENSITIVE patterns for healthcare)

## Architecture
- Framework: Python async/await
- LLM Integration: Anthropic Claude, OpenAI, Local (Ollama)
- Memory: CLAUDE.md (instructions) + MemDocs (patterns)
- Privacy: 3-tier system (Fully Local / Hybrid / Full Integration)

## Security-Specific Guidelines

### MemDocs Classification
- Healthcare patterns: SENSITIVE (HIPAA)
- Software patterns: INTERNAL (general dev patterns)
- Public examples: PUBLIC (sanitized, anonymized)

### Pattern Storage Rules
```python
# Before storing any pattern
if contains_health_data(pattern):
    classification = "SENSITIVE"
    encrypt = True
    retention_days = 90  # HIPAA minimum
elif contains_proprietary_logic(pattern):
    classification = "INTERNAL"
    retention_days = 180
else:
    classification = "PUBLIC"
    retention_days = 365
```

### Required Scrubbing
In addition to enterprise PII rules:
- Patient identifiers (for healthcare examples)
- Company proprietary algorithms
- Internal system architecture details

## Code Organization
```
empathy_llm_toolkit/    # Core LLM wrapper with memory
empathy_os/             # OS layer
coach_wizards/          # 16 wizards
memdocs_integration/    # MemDocs with privacy
```

## Testing Requirements
- 90%+ coverage (current: 90.71%)
- All security controls tested
- PII scrubbing tests with real patterns
- MemDocs classification tests

## Git Workflow
- Branch: feature/claude-memory-integration
- Commits: Conventional commits
- PR: Tests pass, security review approved

---

**Security Acknowledgment:**
This project adheres to enterprise security policy in /etc/claude/CLAUDE.md.
All team members have completed security training.
```

---

## MemDocs Integration Patterns

### Pattern Storage with Security

```python
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig
from memdocs import MemDocs
import re
import json
from datetime import datetime, timedelta

class SecureMemDocsIntegration:
    """
    Secure integration between Claude Memory and MemDocs.

    Enforces enterprise security policies from CLAUDE.md.
    """

    def __init__(self, claude_memory_config: ClaudeMemoryConfig):
        self.claude_memory_config = claude_memory_config
        self.memdocs = MemDocs()
        self.audit_log = []

        # Load security policies from enterprise CLAUDE.md
        self.security_policies = self._load_security_policies()

    def _load_security_policies(self) -> dict:
        """Extract security policies from enterprise memory"""
        from empathy_llm_toolkit.claude_memory import ClaudeMemoryLoader

        loader = ClaudeMemoryLoader(self.claude_memory_config)
        memory = loader.load_all_memory()

        # Parse PII patterns, secret patterns, etc. from memory
        # This ensures policies are centrally managed in CLAUDE.md
        return {
            "pii_patterns": self._extract_pii_patterns(memory),
            "secret_patterns": self._extract_secret_patterns(memory),
            "classification_rules": self._extract_classification_rules(memory),
        }

    def store_pattern(
        self,
        pattern_content: str,
        pattern_type: str,
        user_id: str,
        auto_classify: bool = True
    ) -> dict:
        """
        Store a pattern in MemDocs with security controls.

        Returns:
            dict with pattern_id, classification, sanitization_report
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": "store_pattern",
            "pattern_type": pattern_type,
        }

        try:
            # Step 1: PII Scrubbing (GDPR, HIPAA)
            sanitized_content, pii_found = self._scrub_pii(pattern_content)
            audit_entry["pii_detections"] = len(pii_found)

            # Step 2: Secrets Detection (OWASP)
            secrets_found = self._detect_secrets(sanitized_content)
            if secrets_found:
                raise SecurityError(
                    f"Secrets detected in pattern. Cannot store. "
                    f"Found: {[s['type'] for s in secrets_found]}"
                )
            audit_entry["secrets_detected"] = 0

            # Step 3: Classification
            if auto_classify:
                classification = self._classify_pattern(
                    sanitized_content,
                    pattern_type
                )
            else:
                # Manual classification required for SENSITIVE
                classification = input("Classification (PUBLIC/INTERNAL/SENSITIVE): ")

            audit_entry["classification"] = classification

            # Step 4: Apply classification-specific controls
            storage_config = self.security_policies["classification_rules"][classification]

            if storage_config["encryption"]:
                sanitized_content = self._encrypt_content(sanitized_content)

            # Step 5: Store in MemDocs with metadata
            pattern_id = self.memdocs.store(
                content=sanitized_content,
                metadata={
                    "created_by": user_id,
                    "created_at": datetime.utcnow().isoformat(),
                    "classification": classification,
                    "retention_days": storage_config["retention_days"],
                    "encryption": storage_config["encryption"],
                    "pattern_type": pattern_type,
                    "sanitization_applied": True,
                    "pii_removed": len(pii_found),
                }
            )

            audit_entry["pattern_id"] = pattern_id
            audit_entry["status"] = "success"

            # Step 6: Log to audit trail
            self._log_audit(audit_entry)

            return {
                "pattern_id": pattern_id,
                "classification": classification,
                "sanitization_report": {
                    "pii_removed": pii_found,
                    "secrets_detected": secrets_found,
                },
            }

        except Exception as e:
            audit_entry["status"] = "failed"
            audit_entry["error"] = str(e)
            self._log_audit(audit_entry)
            raise

    def retrieve_pattern(
        self,
        pattern_id: str,
        user_id: str,
        check_permissions: bool = True
    ) -> dict:
        """
        Retrieve a pattern from MemDocs with access control.

        Returns:
            dict with pattern content and metadata
        """
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": "retrieve_pattern",
            "pattern_id": pattern_id,
        }

        try:
            # Step 1: Retrieve from MemDocs
            pattern = self.memdocs.get(pattern_id)

            # Step 2: Check access permissions
            if check_permissions:
                classification = pattern["metadata"]["classification"]
                if not self._check_access(user_id, classification, pattern["metadata"]):
                    raise PermissionError(
                        f"User {user_id} does not have access to {classification} pattern"
                    )

            # Step 3: Decrypt if needed
            content = pattern["content"]
            if pattern["metadata"]["encryption"]:
                content = self._decrypt_content(content)

            # Step 4: Check retention policy
            created_at = datetime.fromisoformat(pattern["metadata"]["created_at"])
            retention_days = pattern["metadata"]["retention_days"]
            if datetime.utcnow() > created_at + timedelta(days=retention_days):
                # Pattern expired, should have been purged
                raise ValueError(f"Pattern {pattern_id} has expired retention period")

            audit_entry["classification"] = pattern["metadata"]["classification"]
            audit_entry["status"] = "success"
            self._log_audit(audit_entry)

            return {
                "content": content,
                "metadata": pattern["metadata"],
            }

        except Exception as e:
            audit_entry["status"] = "failed"
            audit_entry["error"] = str(e)
            self._log_audit(audit_entry)
            raise

    def _scrub_pii(self, content: str) -> tuple[str, list]:
        """Remove PII according to enterprise policy"""
        pii_found = []
        sanitized = content

        for pii_type, pattern in self.security_policies["pii_patterns"].items():
            matches = re.findall(pattern, content)
            if matches:
                pii_found.extend([(pii_type, match) for match in matches])
                replacement = f"[{pii_type.upper()}]"
                sanitized = re.sub(pattern, replacement, sanitized)

        return sanitized, pii_found

    def _detect_secrets(self, content: str) -> list:
        """Detect secrets according to enterprise policy"""
        secrets_found = []

        for secret_type, pattern in self.security_policies["secret_patterns"].items():
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                secrets_found.append({
                    "type": secret_type,
                    "count": len(matches),
                    # Never log actual secret values
                })

        return secrets_found

    def _classify_pattern(self, content: str, pattern_type: str) -> str:
        """Auto-classify pattern based on content and type"""
        # Check for health data keywords (HIPAA)
        health_keywords = ["patient", "medical", "diagnosis", "treatment", "healthcare"]
        if any(keyword in content.lower() for keyword in health_keywords):
            return "SENSITIVE"

        # Check for proprietary indicators
        proprietary_keywords = ["proprietary", "confidential", "internal"]
        if any(keyword in content.lower() for keyword in proprietary_keywords):
            return "INTERNAL"

        # Default to PUBLIC for general patterns
        return "PUBLIC"

    def _check_access(self, user_id: str, classification: str, metadata: dict) -> bool:
        """Check if user has access to pattern based on classification"""
        if classification == "PUBLIC":
            return True

        if classification == "INTERNAL":
            # Check if user is on project team
            return self._user_on_team(user_id, metadata.get("project_team"))

        if classification == "SENSITIVE":
            # Explicit permission required
            return self._has_explicit_permission(user_id, metadata)

        return False

    def _log_audit(self, audit_entry: dict):
        """Log to audit trail (file, database, or SIEM)"""
        self.audit_log.append(audit_entry)

        # Write to audit log file
        with open("/var/log/empathy/audit.jsonl", "a") as f:
            f.write(json.dumps(audit_entry) + "\n")

    # Additional methods for encryption, decryption, etc.
    # ...


class SecurityError(Exception):
    """Raised when security policy is violated"""
    pass
```

---

## Audit Trail Implementation

### Audit Log Format

```json
{
  "version": "1.0",
  "timestamp": "2025-11-24T03:30:00.123Z",
  "event_id": "evt_1a2b3c4d",
  "event_type": "llm_request",
  "user": {
    "id": "user@company.com",
    "ip_address": "[IP]",
    "session_id": "sess_xyz"
  },
  "llm": {
    "provider": "anthropic",
    "model": "claude-sonnet-4",
    "empathy_level": 3,
    "temperature": 0.7
  },
  "memory": {
    "sources": ["enterprise", "user", "project"],
    "total_chars": 2500,
    "security_policies_applied": true
  },
  "memdocs": {
    "patterns_retrieved": ["pattern_abc", "pattern_def"],
    "patterns_stored": [],
    "classifications": ["INTERNAL", "PUBLIC"]
  },
  "security": {
    "pii_detected": 0,
    "pii_scrubbed": 0,
    "secrets_detected": 0,
    "sanitization_applied": true,
    "classification_verified": true
  },
  "request": {
    "size_bytes": 1234,
    "duration_ms": 2500
  },
  "response": {
    "size_bytes": 5678,
    "status": "success"
  },
  "compliance": {
    "gdpr_compliant": true,
    "hipaa_compliant": true,
    "soc2_compliant": true
  }
}
```

### Audit Query Examples

```python
# Query 1: Find all SENSITIVE pattern accesses
sensitive_accesses = audit_log.query(
    event_type="retrieve_pattern",
    classification="SENSITIVE",
    date_range="last_30_days"
)

# Query 2: Find PII detections by user
pii_detections = audit_log.query(
    security__pii_detected__gt=0,
    group_by="user_id"
)

# Query 3: Find failed authentication attempts
auth_failures = audit_log.query(
    event_type="auth",
    status="failed",
    date_range="last_24_hours"
)
```

---

## Compliance Mapping

### GDPR (General Data Protection Regulation)

| Requirement | Implementation | CLAUDE.md Location |
|-------------|----------------|-------------------|
| Article 5(1)(c) - Data Minimization | PII scrubbing before storage | Enterprise § 1 |
| Article 5(1)(e) - Storage Limitation | Retention policies per classification | Enterprise § 4 |
| Article 25 - Data Protection by Design | Default deny + explicit classification | Enterprise § 4 |
| Article 30 - Records of Processing | Audit log with full traceability | Enterprise § 3 |
| Article 32 - Security of Processing | Encryption for SENSITIVE data | Enterprise § 4 |

### HIPAA (Health Insurance Portability and Accountability Act)

| Requirement | Implementation | CLAUDE.md Location |
|-------------|----------------|-------------------|
| §164.312(a)(1) - Access Control | Classification-based access | Enterprise § 4 |
| §164.312(b) - Audit Controls | Comprehensive audit logging | Enterprise § 3 |
| §164.312(c)(1) - Integrity | Tamper-evident logs | Enterprise § 3 |
| §164.312(e)(1) - Transmission Security | TLS 1.3 for API calls | (Infrastructure) |
| §164.514 - De-identification | PII scrubbing patterns | Enterprise § 1 |

### SOC2 (Service Organization Control 2)

| Control | Implementation | CLAUDE.md Location |
|---------|----------------|-------------------|
| CC6.1 - Logical Access | User authentication + authorization | Enterprise § 4 |
| CC6.6 - Encryption | AES-256-GCM for SENSITIVE | Enterprise § 4 |
| CC7.2 - System Monitoring | Audit logging with alerting | Enterprise § 3 |
| CC7.3 - Environmental Protection | Air-gapped mode option | Enterprise § 5 |

---

## Implementation Checklist

### Phase 1: Memory Integration (v1.8.0-alpha) ✅
- [x] ClaudeMemoryLoader with hierarchical loading
- [x] @import directive support
- [x] Integration with EmpathyLLM
- [x] Example CLAUDE.md templates

### Phase 2: Security Controls (v1.8.0-beta) ⏳
- [ ] PII scrubbing implementation
- [ ] Secrets detection implementation
- [ ] Audit logging framework
- [ ] Classification system for MemDocs

### Phase 3: Enterprise Features (v1.8.0) ⏳
- [ ] Air-gapped mode
- [ ] Encryption at rest for SENSITIVE patterns
- [ ] Access control enforcement
- [ ] Retention policy automation

### Phase 4: Compliance Certification ⏳
- [ ] GDPR compliance verification
- [ ] HIPAA compliance verification
- [ ] SOC2 audit preparation
- [ ] Penetration testing
- [ ] Security documentation

---

## Testing & Validation

```python
# Test 1: PII Scrubbing
def test_pii_scrubbing():
    integration = SecureMemDocsIntegration(config)
    content = "Contact John Doe at john.doe@email.com or 555-123-4567"
    sanitized, pii = integration._scrub_pii(content)

    assert "john.doe@email.com" not in sanitized
    assert "[EMAIL]" in sanitized
    assert "[PHONE]" in sanitized
    assert len(pii) == 2

# Test 2: Secrets Detection
def test_secrets_detection():
    integration = SecureMemDocsIntegration(config)
    content = "api_key = 'sk_live_abc123xyz789'"
    secrets = integration._detect_secrets(content)

    assert len(secrets) > 0
    assert secrets[0]["type"] == "api_key"

# Test 3: Classification
def test_pattern_classification():
    integration = SecureMemDocsIntegration(config)

    health_pattern = "Patient diagnosis: diabetes type 2"
    assert integration._classify_pattern(health_pattern, "medical") == "SENSITIVE"

    internal_pattern = "Our proprietary algorithm for scoring"
    assert integration._classify_pattern(internal_pattern, "code") == "INTERNAL"

    public_pattern = "Standard sorting algorithm implementation"
    assert integration._classify_pattern(public_pattern, "code") == "PUBLIC"
```

---

## Summary

This architecture provides:

1. **Defense in Depth**: Multiple security layers (memory policies, PII scrubbing, secrets detection, classification, encryption, access control)

2. **Auditability**: Complete audit trail for compliance (GDPR, HIPAA, SOC2)

3. **Flexibility**: Three deployment models (Fully Local, Hybrid, Full Integration)

4. **Maintainability**: Centralized policies in CLAUDE.md files

5. **Enterprise-Ready**: Built for security audits and regulatory compliance

**Next Steps:**
1. Review and customize enterprise CLAUDE.md template
2. Implement PII scrubbing and secrets detection (Phase 2)
3. Deploy audit logging infrastructure
4. Test with sample patterns
5. Prepare for security audit

---

**Document Version:** 1.0.0
**Last Updated:** 2025-11-24
**Author:** Empathy Framework Team
**License:** Fair Source 0.9
