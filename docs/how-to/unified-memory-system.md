# Unified Memory System

*A single API for short-term (Redis) and long-term (persistent) memory*

---

## Overview

The Empathy Framework provides a **two-tier memory architecture** that mirrors how humans think:

| Memory Tier | Purpose | Backend | Lifetime |
|-------------|---------|---------|----------|
| **Short-Term** | Working memory, task coordination | Redis | Minutes to hours (TTL-based) |
| **Long-Term** | Cross-session patterns, validated knowledge | Persistent storage | Months to years |

The `UnifiedMemory` class provides a single interface to both tiers, with automatic environment detection and pattern promotion workflows.

---

## Quick Start

### Basic Usage

```python
from empathy_os import EmpathyOS

# Create an agent with unified memory (auto-configured)
empathy = EmpathyOS(user_id="analyst@company.com")

# Short-term memory (working data, expires)
empathy.stash("current_task", {"files": ["api.py"], "status": "analyzing"})
task = empathy.retrieve("current_task")

# Long-term memory (persistent patterns)
result = empathy.persist_pattern(
    content="When handling API errors, always include request_id for tracing",
    pattern_type="best_practice"
)
pattern = empathy.recall_pattern(result["pattern_id"])
```

### Direct Memory Access

```python
# Access the unified memory interface directly
memory = empathy.memory

# Check health of both tiers
health = memory.health_check()
print(f"Short-term available: {health['short_term']['available']}")
print(f"Long-term available: {health['long_term']['available']}")
print(f"Environment: {health['environment']}")
```

---

## Environment Configuration

The memory system auto-detects its environment and configures storage accordingly:

### Automatic Detection

```python
from empathy_os.memory import UnifiedMemory, MemoryConfig

# Auto-detect from environment variables
memory = UnifiedMemory(user_id="agent@company.com")
# Checks: REDIS_URL, EMPATHY_ENV, EMPATHY_STORAGE_DIR
```

### Manual Configuration

```python
from empathy_os.memory import UnifiedMemory, MemoryConfig, Environment

# Development (mock Redis, local storage)
dev_config = MemoryConfig(
    environment=Environment.DEVELOPMENT,
    redis_mock=True,
    storage_dir="./dev_storage",
    encryption_enabled=False
)

# Production (real Redis, encrypted storage)
prod_config = MemoryConfig(
    environment=Environment.PRODUCTION,
    redis_url="redis://user:pass@host:6379",
    storage_dir="/var/empathy/patterns",
    encryption_enabled=True
)

memory = UnifiedMemory(user_id="agent@company.com", config=prod_config)
```

### Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `EMPATHY_ENV` | Environment tier | `development`, `staging`, `production` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379` |
| `EMPATHY_REDIS_MOCK` | Force mock mode | `true` |
| `EMPATHY_STORAGE_DIR` | Long-term storage | `./patterns` |
| `EMPATHY_ENCRYPTION` | Enable encryption | `true` |
| `EMPATHY_CLAUDE_MEMORY` | Load Claude memory | `true` |

---

## Short-Term Memory Operations

Short-term memory is for **working data** that expires automatically.

### Stash and Retrieve

```python
# Store with default TTL (1 hour)
empathy.stash("analysis_results", {
    "files_reviewed": 10,
    "issues_found": 3,
    "timestamp": "2025-12-10T10:00:00"
})

# Store with custom TTL (24 hours)
empathy.memory.stash("weekly_summary", summary_data, ttl_seconds=86400)

# Retrieve
results = empathy.retrieve("analysis_results")
```

### Stage Patterns for Validation

Before committing patterns to long-term memory, stage them for review:

```python
# Stage a discovered pattern
staged_id = empathy.memory.stage_pattern(
    pattern_data={
        "content": "Always validate user input at API boundaries",
        "code_example": "def validate(input): ...",
        "metadata": {"discovered_in": "pr_review_42"}
    },
    pattern_type="security",
    ttl_hours=24  # Auto-expires if not promoted
)

# View all staged patterns
staged = empathy.memory.get_staged_patterns()
for p in staged:
    print(f"Pattern: {p['pattern_type']} - Confidence: {p.get('confidence', 'N/A')}")
```

---

## Long-Term Memory Operations

Long-term memory is for **validated patterns** that persist across sessions.

### Persist Patterns

```python
# Basic pattern storage
result = empathy.persist_pattern(
    content="Use dependency injection for testable code",
    pattern_type="architecture"
)
print(f"Pattern ID: {result['pattern_id']}")
print(f"Classification: {result['classification']}")  # AUTO-DETECTED

# With explicit classification
result = empathy.persist_pattern(
    content="Patient data handling protocol for HIPAA compliance",
    pattern_type="clinical_protocol",
    classification="SENSITIVE",  # Forces encryption
    metadata={"compliance": ["HIPAA"], "author": "compliance_team"}
)
```

### Recall Patterns

```python
# Retrieve by ID
pattern = empathy.recall_pattern("pat_abc123")
if pattern:
    print(f"Content: {pattern['content']}")
    print(f"Type: {pattern['pattern_type']}")
    print(f"Created: {pattern['created_at']}")
```

### Classification Levels

Patterns are automatically classified based on content:

| Classification | Description | Encryption | Retention |
|----------------|-------------|------------|-----------|
| `PUBLIC` | General patterns, shareable | No | 365 days |
| `INTERNAL` | Proprietary patterns | Optional | 180 days |
| `SENSITIVE` | Healthcare/PII patterns | **Required** (AES-256) | 90 days |

```python
from empathy_os.memory import Classification

# Auto-classification (recommended)
result = empathy.persist_pattern(
    content="JWT refresh pattern for auth tokens",
    pattern_type="security",
    auto_classify=True  # Default
)
# Result: {"classification": "INTERNAL"}

# Explicit classification
result = empathy.persist_pattern(
    content="Patient handoff protocol",
    pattern_type="clinical",
    classification=Classification.SENSITIVE
)
# Result: {"classification": "SENSITIVE", "encrypted": True}
```

---

## Pattern Promotion Workflow

The pattern promotion workflow moves validated patterns from short-term to long-term memory:

```
  ┌─────────────┐         ┌──────────────┐         ┌─────────────┐
  │  Discovery  │───────▶│   Staging    │───────▶│  Long-Term  │
  │  (Agent)    │         │  (Review)    │         │  (Library)  │
  └─────────────┘         └──────────────┘         └─────────────┘
        │                       │                        │
        │                       │                        │
    Contributor            Validator                 Anyone
    discovers              reviews &                can recall
                           promotes
```

### Example Workflow

```python
from empathy_os import EmpathyOS, AccessTier

# 1. Contributor discovers a pattern
contributor = EmpathyOS(
    user_id="code_reviewer",
    access_tier=AccessTier.CONTRIBUTOR
)

staged_id = contributor.memory.stage_pattern(
    pattern_data={
        "content": "Use connection pooling for database access",
        "confidence": 0.92,
        "discovered_in": "performance_review"
    },
    pattern_type="optimization"
)
print(f"Pattern staged: {staged_id}")

# 2. Validator reviews and promotes
validator = EmpathyOS(
    user_id="senior_architect",
    access_tier=AccessTier.VALIDATOR
)

# Review staged patterns
staged = validator.memory.get_staged_patterns()
for p in staged:
    if p.get("confidence", 0) > 0.85:
        # Promote to long-term storage
        result = validator.memory.promote_pattern(
            staged_pattern_id=p["pattern_id"],
            classification="INTERNAL",  # Optional override
        )
        print(f"Promoted: {result['pattern_id']}")
```

---

## Security Integration

The unified memory system includes enterprise-grade security controls.

### PII Scrubbing

Content is automatically scrubbed before storage:

```python
# PII in content is automatically redacted
result = empathy.persist_pattern(
    content="User john.doe@company.com reported issue with SSN 123-45-6789",
    pattern_type="support_pattern"
)
# Stored as: "User [EMAIL] reported issue with SSN [SSN]"
```

### Secrets Detection

Secrets are detected and blocked:

```python
# This will trigger a security warning
result = empathy.persist_pattern(
    content="API key: sk-proj-abc123...",
    pattern_type="api_integration"
)
# Result: {"error": "secrets_detected", "blocked": True}
```

### Audit Logging

All operations are logged for compliance:

```python
# Audit events are automatically generated for:
# - Pattern storage/retrieval
# - Classification decisions
# - Access control checks
# - Security violations

# View audit events programmatically
from empathy_os.memory import AuditLogger
logger = AuditLogger(log_file="/var/log/empathy/audit.jsonl")
```

---

## Complete Example: Multi-Agent Knowledge Building

```python
"""
Multi-agent system where agents discover and share patterns.
"""
import asyncio
from empathy_os import EmpathyOS, AccessTier, get_redis_memory

async def knowledge_building_demo():
    # Shared memory for all agents
    memory = get_redis_memory()

    # Specialist agents discover patterns
    security_agent = EmpathyOS(
        user_id="security_specialist",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR
    )

    performance_agent = EmpathyOS(
        user_id="performance_specialist",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR
    )

    # Lead architect validates and promotes
    architect = EmpathyOS(
        user_id="lead_architect",
        short_term_memory=memory,
        access_tier=AccessTier.VALIDATOR
    )

    # 1. Security agent discovers a pattern
    security_agent.memory.stage_pattern(
        pattern_data={
            "content": "Always sanitize SQL inputs using parameterized queries",
            "code": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))",
            "confidence": 0.95,
            "source": "code_review_auth_module"
        },
        pattern_type="security"
    )
    print("Security pattern staged")

    # 2. Performance agent discovers a pattern
    performance_agent.memory.stage_pattern(
        pattern_data={
            "content": "Use bulk operations for batch database updates",
            "code": "session.bulk_insert_mappings(Model, data_list)",
            "confidence": 0.88,
            "source": "performance_analysis_q4"
        },
        pattern_type="optimization"
    )
    print("Performance pattern staged")

    # 3. Architect reviews all staged patterns
    staged = architect.memory.get_staged_patterns()
    print(f"\nPatterns awaiting review: {len(staged)}")

    for p in staged:
        print(f"\n--- {p['pattern_type'].upper()} Pattern ---")
        print(f"Content: {p['content'][:50]}...")
        print(f"Confidence: {p.get('confidence', 'N/A')}")

        # Promote high-confidence patterns
        if p.get('confidence', 0) > 0.85:
            result = architect.memory.promote_pattern(p['pattern_id'])
            print(f"PROMOTED -> Long-term ID: {result['pattern_id']}")
        else:
            print("NEEDS MORE VALIDATION")

    # 4. Check long-term library
    health = architect.memory.health_check()
    print(f"\n=== Memory Health ===")
    print(f"Short-term: {health['short_term']['available']}")
    print(f"Long-term: {health['long_term']['available']}")
    print(f"Environment: {health['environment']}")

if __name__ == "__main__":
    asyncio.run(knowledge_building_demo())
```

---

## Migration from Legacy APIs

### From `short_term_memory` parameter

```python
# OLD (still works, but deprecated)
from empathy_os import EmpathyOS, get_redis_memory
empathy = EmpathyOS(
    user_id="agent",
    short_term_memory=get_redis_memory()  # Manual setup
)
empathy.short_term_memory.stash(...)  # Direct access

# NEW (recommended)
empathy = EmpathyOS(user_id="agent")
empathy.stash(...)  # Convenience method
empathy.memory.stash(...)  # Or via unified interface
```

### From `empathy_llm_toolkit.security`

```python
# OLD (still works via re-exports)
from empathy_llm_toolkit.security import PIIScrubber, SecretsDetector

# NEW (recommended)
from empathy_os.memory import PIIScrubber, SecretsDetector
from empathy_os.memory.security import AuditLogger
```

---

## Next Steps

- **[Short-Term Memory Implementation](./short-term-memory-implementation.md)**: Detailed Redis setup
- **[Security Architecture](./security-architecture.md)**: PII scrubbing, encryption, audit logging
- **[API Reference: Memory](../api-reference/multi-agent.md)**: Complete class documentation

---

*The unified memory system was introduced in v1.10.0 as part of the MemDocs consolidation effort. It combines the best of short-term Redis coordination with long-term pattern persistence.*
