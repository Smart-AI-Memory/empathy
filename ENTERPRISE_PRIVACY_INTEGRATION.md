# Enterprise Privacy Integration Plan
## Claude Memory + MemDocs with Privacy Controls

**Version**: 1.0
**Date**: 2025-11-22
**Status**: Design Phase

---

## Executive Summary

This document outlines the integration of Claude's memory features with the Empathy Framework's MemDocs system, designed specifically for enterprise software developers who require strict privacy controls.

**Key Principles:**
1. **Privacy by Default**: Most restrictive settings out of the box
2. **Explicit Opt-in**: Cloud features require conscious enablement
3. **Audit Everything**: Complete transparency of data flow
4. **Local First**: All sensitive data stays on-premises by default
5. **Compliance Ready**: Built for GDPR, HIPAA, SOC2 requirements

---

## Privacy Tier System

### Tier 1: Fully Local (Air-Gapped) 🔒

**Use Case**: Maximum security environments (finance, healthcare, defense)

**Configuration:**
```python
config = EnterprisePrivacyConfig(
    privacy_tier="fully_local",

    # Memory & Storage
    memory_backend="local_only",  # SQLite, no cloud
    memdocs_storage_path="./memdocs_private/",
    pattern_sharing="disabled",

    # LLM Provider
    llm_provider="ollama",  # Local Ollama instance
    llm_model="codellama:13b",
    external_api_calls="forbidden",

    # Data Handling
    scrub_pii=True,
    scrub_secrets=True,
    scrub_code_snippets=True,

    # Audit
    audit_logging="verbose",
    audit_log_path="./audit/privacy.log"
)
```

**Features:**
- ✅ Local LLM (Ollama) for all analysis
- ✅ MemDocs patterns stored in encrypted SQLite
- ✅ No network calls (air-gapped compatible)
- ✅ Pattern matching and Level 4 predictions work offline
- ❌ No cross-domain pattern enrichment from cloud
- ❌ Slower inference than cloud LLMs

**Data Flow:**
```
User Code → MemDocs (Local) → Ollama (Local) → Results (Local)
    ↓                                               ↓
Audit Log                                    Pattern Library
(Local)                                         (Local)
```

---

### Tier 2: Hybrid (Cloud LLM, Local Memory) ⚖️

**Use Case**: Most enterprises - balance of security and capability

**Configuration:**
```python
config = EnterprisePrivacyConfig(
    privacy_tier="hybrid",

    # Memory & Storage
    memory_backend="local_only",  # Still local
    memdocs_storage_path="./memdocs_private/",
    pattern_sharing="local_only",

    # LLM Provider
    llm_provider="anthropic",
    llm_model="claude-sonnet-4-5",
    api_key_source="env",  # Never hardcoded
    zero_data_retention=True,  # Enterprise API feature

    # Data Handling
    scrub_pii=True,
    scrub_secrets=True,
    scrub_code_snippets=False,  # Send code for analysis
    max_context_size=50000,  # Limit context sent to API

    # Privacy Controls
    send_to_claude=[
        "code_structure",  # Safe: file structure, dependencies
        "error_messages",  # Safe: error text
        "analysis_requests"  # Safe: user queries
    ],
    never_send_to_claude=[
        "api_keys",
        "passwords",
        "credentials",
        "pii",
        "customer_data",
        "connection_strings"
    ],

    # Audit
    audit_logging="verbose",
    audit_log_path="./audit/privacy.log",
    audit_include_api_responses=True
)
```

**Features:**
- ✅ Fast Claude API inference
- ✅ All patterns stay local (no sync to Claude)
- ✅ Automatic PII/secret scrubbing before API calls
- ✅ Zero data retention with enterprise API
- ✅ Comprehensive audit logging
- ✅ Pattern library remains proprietary
- ❌ No persistent Claude memory across sessions

**Data Flow:**
```
User Code → PII Scrubber → Claude API (Stateless)
    ↓                           ↓
Audit Log                   Results
    ↓                           ↓
MemDocs (Local) ← Pattern Extractor
```

**Scrubbing Pipeline:**
```python
class PIIScrubber:
    """Removes sensitive data before sending to external APIs"""

    PATTERNS = {
        'api_key': r'(api[_-]?key|apikey|api-token)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-]{20,})',
        'aws_key': r'(AKIA[0-9A-Z]{16})',
        'password': r'(password|passwd|pwd)\s*[:=]\s*[\'"]?([^\s\'"]+)',
        'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'ssn': r'\b\d{3}-\d{2}-\d{4}\b',
        'credit_card': r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',
        'ip_address': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        'connection_string': r'(mongodb|postgresql|mysql):\/\/[^\s]+',
    }

    def scrub(self, text: str) -> tuple[str, list[dict]]:
        """
        Returns: (scrubbed_text, redactions)
        redactions = [{"type": "api_key", "location": "line 42", "replacement": "[REDACTED_API_KEY]"}]
        """
```

---

### Tier 3: Full Integration (Opt-in Cloud Memory) ☁️

**Use Case**: Teams wanting maximum Claude integration (startups, open-source projects)

**Configuration:**
```python
config = EnterprisePrivacyConfig(
    privacy_tier="full_integration",

    # Memory & Storage
    memory_backend="hybrid",  # Local + Claude.md
    memdocs_storage_path="./memdocs_private/",
    pattern_sharing="opt_in_cloud",  # Explicit consent

    # Claude Memory Integration
    claude_memory_enabled=True,
    claude_memory_scope="project",  # project, team, or enterprise
    claude_memory_file="./.claude/CLAUDE.md",
    sync_patterns_to_claude_memory=False,  # Default: no sync

    # LLM Provider
    llm_provider="anthropic",
    llm_model="claude-sonnet-4-5",
    zero_data_retention=True,  # Still use enterprise API

    # Data Handling (still strict)
    scrub_pii=True,
    scrub_secrets=True,
    scrub_code_snippets=False,

    # Audit
    audit_logging="verbose",
    audit_log_path="./audit/privacy.log"
)
```

**Features:**
- ✅ Persistent context via Claude Code's CLAUDE.md
- ✅ Cross-session continuity without re-sending context
- ✅ Optional: Sync non-sensitive patterns to project memory
- ✅ Team collaboration via shared project memory
- ✅ Still maintains PII scrubbing
- ⚠️ More data sent to Claude (with consent)

**Data Flow:**
```
User Code → PII Scrubber → Claude API
    ↓                           ↓
Audit Log                   Results + Memory Updates
    ↓                           ↓
MemDocs (Local) ← Pattern Extractor → CLAUDE.md (Opt-in)
```

---

## Configuration API

### Python Configuration

```python
from empathy_framework import EnterprisePrivacyConfig, EmpathyLLM

# Example 1: Hybrid tier (recommended for most enterprises)
config = EnterprisePrivacyConfig.from_tier("hybrid")

# Example 2: Custom configuration
config = EnterprisePrivacyConfig(
    privacy_tier="hybrid",

    # Override specific settings
    scrub_code_snippets=True,  # More restrictive
    max_context_size=20000,  # Smaller context

    # Custom scrubbing patterns
    custom_scrub_patterns=[
        r'INTERNAL_SECRET_\w+',  # Company-specific
        r'ACME_API_\d+',
    ],

    # Allowlist for safe data
    allow_send_to_claude=[
        "public_documentation",
        "error_stack_traces",
    ]
)

# Initialize with config
llm = EmpathyLLM(
    provider="anthropic",
    config=config
)

# Use normally - privacy handled automatically
result = await llm.interact(
    user_id="dev_123",
    user_input="Analyze this code for security issues",
    context={"file_path": "app.py", "content": code}
)
# → Code automatically scrubbed before sending to Claude
# → Audit log entry created
# → Results stored locally in MemDocs
```

### VSCode Extension Configuration

```json
{
  "coach.enterprise.privacyTier": "hybrid",
  "coach.enterprise.memoryBackend": "local_only",
  "coach.enterprise.scrubPII": true,
  "coach.enterprise.scrubSecrets": true,
  "coach.enterprise.zeroDataRetention": true,
  "coach.enterprise.auditLogging": "verbose",
  "coach.enterprise.auditLogPath": "./audit/coach-privacy.log",

  "coach.claude.memoryEnabled": false,
  "coach.claude.memoryFile": "./.claude/CLAUDE.md",
  "coach.claude.syncPatterns": false,

  "coach.privacy.neverSendToCloud": [
    "*.env",
    "*.key",
    "*.pem",
    "*secret*",
    "*credential*",
    "config/database.yml"
  ],

  "coach.privacy.customScrubPatterns": [
    "INTERNAL_\\w+_KEY",
    "COMPANY_SECRET_\\d+"
  ]
}
```

### Environment Variables

```bash
# Privacy tier
EMPATHY_PRIVACY_TIER=hybrid  # fully_local, hybrid, full_integration

# API Configuration
ANTHROPIC_API_KEY=sk-ant-...  # Enterprise API key
EMPATHY_ZERO_DATA_RETENTION=true

# Memory & Storage
EMPATHY_MEMORY_BACKEND=local_only
MEMDOCS_STORAGE_PATH=./memdocs_private/
EMPATHY_AUDIT_LOG_PATH=./audit/privacy.log

# Claude Memory Integration (Tier 3 only)
CLAUDE_MEMORY_ENABLED=false
CLAUDE_MEMORY_FILE=./.claude/CLAUDE.md
SYNC_PATTERNS_TO_CLAUDE=false

# Scrubbing
EMPATHY_SCRUB_PII=true
EMPATHY_SCRUB_SECRETS=true
EMPATHY_MAX_CONTEXT_SIZE=50000
```

---

## Implementation Roadmap

### Phase 1: Privacy Infrastructure (Week 1-2)

**Tasks:**
1. Create `EnterprisePrivacyConfig` class
2. Implement `PIIScrubber` with regex patterns
3. Add audit logging framework
4. Create privacy tier validation
5. Add configuration validation and warnings

**Files to Create:**
- `/empathy_llm_toolkit/enterprise_privacy.py`
- `/empathy_llm_toolkit/scrubbing.py`
- `/empathy_llm_toolkit/audit.py`
- `/tests/test_enterprise_privacy.py`

**Tests:**
- Verify PII scrubbing works correctly
- Test all three privacy tiers
- Validate audit log format
- Ensure no leakage in error messages

### Phase 2: Memory Integration (Week 3-4)

**Tasks:**
1. Add CLAUDE.md file reading/writing
2. Implement pattern sync logic (opt-in)
3. Create memory mode switching
4. Add Claude API zero-retention flag
5. Implement local-only fallback

**Files to Modify:**
- `/empathy_llm_toolkit/providers.py` (add privacy controls)
- `/src/empathy_os/pattern_library.py` (add sync options)
- `/examples/coach/lsp/server.py` (add config loading)

**Tests:**
- Test CLAUDE.md integration
- Verify pattern sync (when enabled)
- Test local-only mode
- Validate zero-retention API calls

### Phase 3: VSCode Integration (Week 5)

**Tasks:**
1. Add privacy settings UI
2. Create tier selection dropdown
3. Implement audit log viewer
4. Add scrubbing preview (show what will be sent)
5. Create privacy dashboard

**Files to Create:**
- `/examples/coach/vscode-extension/src/views/privacy-dashboard.ts`
- `/examples/coach/vscode-extension/src/privacy-manager.ts`

**UI Components:**
- Privacy tier selector
- Audit log viewer (real-time)
- Scrubbing pattern tester
- Data flow visualization

### Phase 4: Documentation & Compliance (Week 6)

**Tasks:**
1. Create enterprise deployment guide
2. Write compliance mapping (GDPR, HIPAA, SOC2)
3. Create privacy FAQ
4. Write data flow diagrams
5. Create security audit checklist

**Documents to Create:**
- `/docs/ENTERPRISE_DEPLOYMENT.md`
- `/docs/COMPLIANCE_MAPPING.md`
- `/docs/PRIVACY_FAQ.md`
- `/docs/SECURITY_AUDIT_CHECKLIST.md`

---

## Audit Logging Format

### Log Entry Structure

```json
{
  "timestamp": "2025-11-22T10:30:45.123Z",
  "event_type": "llm_api_call",
  "privacy_tier": "hybrid",
  "user_id": "dev_123",
  "session_id": "sess_abc123",

  "request": {
    "provider": "anthropic",
    "model": "claude-sonnet-4-5",
    "tokens_sent": 1250,
    "context_size_bytes": 45000,
    "scrubbed_patterns": ["api_key", "email"],
    "redactions_count": 3
  },

  "response": {
    "tokens_received": 800,
    "response_time_ms": 2340,
    "cached": false
  },

  "privacy": {
    "pii_scrubbed": true,
    "secrets_scrubbed": true,
    "code_sent": true,
    "memdocs_pattern_stored": true,
    "claude_memory_updated": false
  },

  "metadata": {
    "file_path": "src/api/auth.py",
    "task_type": "security_analysis",
    "wizard": "SecurityWizard"
  }
}
```

### Audit Query API

```python
from empathy_framework import AuditLog

# Query recent API calls
calls = AuditLog.query(
    event_type="llm_api_call",
    since="2025-11-22",
    privacy_tier="hybrid"
)

# Check for PII leakage
potential_leaks = AuditLog.query(
    privacy__pii_scrubbed=False,
    privacy__secrets_scrubbed=False
)

# Export for compliance audit
AuditLog.export(
    format="csv",
    output="audit_report_2025_Q4.csv",
    include_fields=["timestamp", "event_type", "privacy", "user_id"]
)
```

---

## Privacy Dashboard (VSCode Extension)

### Visual Components

```
┌────────────────────────────────────────────────────────┐
│  Coach Privacy Dashboard                               │
├────────────────────────────────────────────────────────┤
│                                                        │
│  Privacy Tier: ⚖️  Hybrid                             │
│  [Change Tier ▼]                                       │
│                                                        │
│  ┌──────────────────────────────────────────────────┐ │
│  │ Data Flow Visualization                          │ │
│  │                                                  │ │
│  │  Your Code → PII Scrubber → Claude API          │ │
│  │      ↓            ↓             ↓                │ │
│  │  MemDocs    Audit Log       Results              │ │
│  │  (Local)     (Local)        (Local)              │ │
│  └──────────────────────────────────────────────────┘ │
│                                                        │
│  📊 Today's Stats:                                     │
│  • API Calls: 42                                       │
│  • PII Scrubbed: 7 instances                          │
│  • Patterns Stored Locally: 3                         │
│  • Audit Log Entries: 42                              │
│                                                        │
│  🔍 Recent Scrubbed Items:                            │
│  • api_key (line 42, auth.py) → [REDACTED]           │
│  • email (line 108, users.py) → [REDACTED]           │
│  • password (line 34, config.py) → [REDACTED]        │
│                                                        │
│  [View Full Audit Log]  [Export Report]  [Settings]  │
└────────────────────────────────────────────────────────┘
```

---

## Compliance Mapping

### GDPR Compliance

| Requirement | Implementation |
|-------------|----------------|
| Right to erasure | `AuditLog.delete(user_id="...")` |
| Data minimization | Tier 1/2: only necessary data sent |
| Purpose limitation | Explicit consent for each privacy tier |
| Data portability | Export audit logs, patterns in JSON |
| Privacy by design | Default to most restrictive tier |

### HIPAA Compliance

| Requirement | Implementation |
|-------------|----------------|
| PHI protection | PII scrubbing includes medical data patterns |
| Audit controls | Comprehensive audit logging |
| Access controls | User-based privacy tiers |
| Transmission security | TLS for all API calls |
| Data at rest encryption | SQLite encryption for Tier 1 |

### SOC 2 Compliance

| Control | Implementation |
|---------|----------------|
| Logical access | API key management, env vars only |
| Change management | Git-tracked CLAUDE.md files |
| Risk mitigation | Privacy tier system |
| Monitoring | Real-time audit logging |

---

## Migration Guide

### From Current Framework to Privacy-Enabled

**Step 1: Install Updated Framework**
```bash
pip install empathy-framework>=1.8.0
```

**Step 2: Add Privacy Configuration**
```python
# Before (no privacy controls)
llm = EmpathyLLM(provider="anthropic")

# After (privacy-enabled)
from empathy_framework import EnterprisePrivacyConfig

config = EnterprisePrivacyConfig.from_tier("hybrid")
llm = EmpathyLLM(provider="anthropic", config=config)
```

**Step 3: Update VSCode Settings**
```json
{
  "coach.enterprise.privacyTier": "hybrid"
}
```

**Step 4: Review Audit Logs**
```bash
tail -f ./audit/privacy.log
```

---

## FAQ

**Q: Does this slow down the framework?**
A: Minimal impact. PII scrubbing adds ~50ms per request. Audit logging is async.

**Q: Can I use Tier 1 with no internet?**
A: Yes! Tier 1 is designed for air-gapped environments with local Ollama.

**Q: What if I accidentally send sensitive data?**
A: Audit log shows exactly what was sent. You can revoke API keys and rotate secrets.

**Q: Does zero-retention really mean zero?**
A: With enterprise API keys configured for zero retention, Claude doesn't store request/response data beyond processing.

**Q: Can I customize scrubbing patterns?**
A: Yes! Add custom regex patterns in config or VSCode settings.

**Q: Does this work with JetBrains IDEs?**
A: Yes, same privacy system applies to all IDE integrations.

---

## Next Steps

1. **Review this design** with your team
2. **Choose target privacy tier** for your organization
3. **Pilot with Tier 2 (Hybrid)** - recommended starting point
4. **Provide feedback** on additional privacy controls needed
5. **Plan rollout** across development teams

---

**Document Status**: Draft for Review
**Last Updated**: 2025-11-22
**Next Review**: After implementation of Phase 1
**Owner**: Empathy Framework Team
