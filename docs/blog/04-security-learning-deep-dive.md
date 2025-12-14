# Security Learning: Teaching AI Your Team's Security Policies

**Date:** December 12, 2025
**Author:** Patrick Roebuck
**Series:** Memory-Enhanced Development (Part 4 of 4)

---

## TL;DR

Security scanners flag the same false positives every time. With persistent memory, your AI learns from team decisions and suppresses known acceptable risks. In our test: 108 raw findings → 23 after learning. That's 78.7% noise reduction.

---

## The Problem: Alert Fatigue

Security tools are thorough. Maybe too thorough.

Every scan flags:
- "Hardcoded secret" in test fixtures
- "SQL injection" in ORM code that handles escaping
- "Insecure random" for UI animations
- "XSS vulnerability" in React (which auto-escapes)

You know these are false positives. Your team reviewed them months ago. But the scanner doesn't remember.

**So every scan, you review the same findings. Mark the same things as acceptable. Ignore the same noise.**

Eventually, you stop paying attention. That's when real vulnerabilities slip through.

---

## How Security Learning Works

### Step 1: Initial Scan

First scan returns raw findings:

```
SECURITY SCAN RESULTS:
  Total findings: 108

  By severity:
    critical: 99
    high: 6
    medium: 3

  By type:
    hardcoded_secret: 45
    sql_injection: 23
    insecure_random: 18
    xss: 12
    command_injection: 8
    path_traversal: 2
```

108 findings. Most of them false positives you've seen before.

### Step 2: Record Team Decisions

When a human reviews a finding, we record the decision:

```python
await wizard.record_decision({
    "finding_hash": "hardcoded_secret",
    "decision": "false_positive",
    "reason": "Test fixtures and demo files - not real credentials",
    "decided_by": "@sarah",
    "applies_to": "all",  # Apply to all hardcoded_secret findings
})
```

Decision types:
- **false_positive**: Not actually a vulnerability
- **accepted**: Real risk, but accepted for business reasons
- **deferred**: Will fix later, suppress for now
- **escalated**: Needs immediate attention

### Step 3: Store Decisions

Decisions persist in `./patterns/security/team_decisions.json`:

```json
{
  "decisions": [
    {
      "finding_hash": "hardcoded_secret",
      "decision": "false_positive",
      "reason": "Test fixtures and demo files - not real credentials",
      "decided_by": "@sarah",
      "decided_at": "2025-10-15T14:30:00Z",
      "applies_to": "all"
    },
    {
      "finding_hash": "insecure_random",
      "decision": "accepted",
      "reason": "Used for non-cryptographic purposes (IDs, sampling)",
      "decided_by": "@mike",
      "decided_at": "2025-11-01T09:15:00Z",
      "applies_to": "all"
    },
    {
      "finding_hash": "sql_injection",
      "decision": "false_positive",
      "reason": "Using SQLAlchemy ORM which handles SQL escaping",
      "decided_by": "@tech_lead",
      "decided_at": "2025-09-20T11:00:00Z",
      "applies_to": "pattern"
    }
  ]
}
```

### Step 4: Apply Learning

Next scan applies learned patterns:

```python
result = await wizard.analyze({
    "project_path": ".",
    "apply_learned_patterns": True,  # Enable learning
})
```

The wizard:
1. Runs the security scan (108 findings)
2. Checks each finding against team decisions
3. Suppresses findings that match decisions
4. Returns only findings that need attention

```
SCAN WITH LEARNING:
  Raw findings: 108
  After learning: 23

  LEARNING APPLIED:
    Suppressed: 85 findings
    Noise reduction: 78.7%

    Suppression details:
    - hardcoded_secret: 45 suppressed
      Decision: false_positive by @sarah
      Reason: "Test fixtures and demo files"

    - sql_injection: 23 suppressed
      Decision: false_positive by @tech_lead
      Reason: "ORM handles escaping"

    - insecure_random: 17 suppressed
      Decision: accepted by @mike
      Reason: "Non-cryptographic use"
```

---

## Real Results From Our Codebase

We ran security learning on the Empathy Framework repository:

```
--- Scan WITHOUT Learning ---
  Raw findings: 108
  By severity:
    critical: 99
    high: 6
    medium: 3

--- Scan WITH Learning ---
  Raw findings: 108
  After learning: 23

  LEARNING APPLIED:
    Suppressed: 85 findings
    Noise reduction: 78.7%
```

### What Got Suppressed

| Finding Type | Raw Count | After Learning | Suppression |
|-------------|-----------|----------------|-------------|
| hardcoded_secret | 45 | 0 | 100% (test fixtures) |
| sql_injection | 23 | 0 | 100% (ORM escaping) |
| insecure_random | 18 | 1 | 94% (non-crypto use) |
| xss | 12 | 12 | 0% (needs review) |
| command_injection | 8 | 8 | 0% (needs review) |
| path_traversal | 2 | 2 | 0% (needs review) |

### What Remained

The 23 remaining findings are:
- **Real vulnerabilities** that need fixing
- **New finding types** the team hasn't reviewed yet
- **Edge cases** that don't match suppression patterns

These are the ones worth your time.

---

## Decision Granularity

Decisions can apply at different levels:

```python
# Apply to ALL findings of this type
{
    "finding_hash": "hardcoded_secret",
    "applies_to": "all"
}

# Apply only to findings matching a pattern
{
    "finding_hash": "hardcoded_secret",
    "applies_to": "pattern",
    "pattern": "test_*.py"  # Only in test files
}

# Apply only to this specific instance
{
    "finding_hash": "hardcoded_secret",
    "applies_to": "instance",
    "file": "tests/fixtures/demo_config.py",
    "line": 42
}
```

This prevents over-suppression. A `hardcoded_secret` in test fixtures is fine. The same finding in production code should still alert.

---

## The Audit Trail

Every suppression is logged:

```json
{
  "timestamp": "2025-12-12T10:30:00Z",
  "action": "finding_suppressed",
  "finding_type": "hardcoded_secret",
  "file": "tests/fixtures/api_keys.py",
  "line": 15,
  "suppression_reason": "false_positive",
  "decision_by": "@sarah",
  "decision_date": "2025-10-15T14:30:00Z"
}
```

This provides:
- **Compliance evidence**: Decisions are documented and traceable
- **Review capability**: Audit past decisions
- **Accountability**: Who decided what and when

---

## Re-evaluating Decisions

Decisions aren't permanent. You can:

**Review all decisions:**
```python
decisions = await wizard.list_decisions()
for d in decisions:
    print(f"{d['finding_hash']}: {d['decision']} by {d['decided_by']}")
```

**Revoke a decision:**
```python
await wizard.revoke_decision(
    finding_hash="sql_injection",
    reason="Upgraded to raw SQL queries, need to re-evaluate"
)
```

**Set expiration:**
```python
await wizard.record_decision({
    "finding_hash": "insecure_random",
    "decision": "accepted",
    "expires_at": "2026-01-01T00:00:00Z",  # Re-review after this date
})
```

---

## The Memory Benefit

Without persistent memory:

```
Security Scan Results:
  108 findings

  critical: 99
  high: 6
  medium: 3

Please review all findings.
```

Every scan. Every time. Same 108 findings.

With persistent memory:

```
Security Scan Results:
  108 findings detected
  85 suppressed (team decisions)
  23 require attention

  Suppressed by team policy:
    - 45 hardcoded_secret (test fixtures)
    - 23 sql_injection (ORM escaping)
    - 17 insecure_random (non-crypto)

  Remaining critical issues:
    - command_injection: 8 findings
    - path_traversal: 2 findings
```

**You review 23 findings instead of 108. And those 23 are the ones that actually matter.**

---

## Try It Yourself

```python
from empathy_software_plugin.wizards import SecurityLearningWizard

wizard = SecurityLearningWizard(
    pattern_storage_path="./patterns/security"
)

# Scan with learning
result = await wizard.analyze({
    "project_path": ".",
    "apply_learned_patterns": True,
})

print(f"Raw: {result['raw_findings_count']}")
print(f"After learning: {result['summary']['total_after_learning']}")
print(f"Noise reduction: {result['learning_applied']['noise_reduction_percent']}%")

# Record a decision
await wizard.record_decision({
    "finding_hash": "some_finding",
    "decision": "false_positive",
    "reason": "Your reason here",
    "decided_by": "@your_name",
    "applies_to": "all",
})
```

Full example: [03_security_learning.py](https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/03_security_learning.py)

---

## Series Conclusion

This completes our 4-part series on memory-enhanced development:

1. **[Full Repo Test](01-we-tested-memory-on-our-own-codebase.md)** — Validated results on our own codebase
2. **[Bug Correlation](02-bug-correlation-deep-dive.md)** — Learning from debugging history
3. **[Tech Debt Trajectory](03-tech-debt-trajectory-deep-dive.md)** — Predicting the future from the past
4. **[Security Learning](04-security-learning-deep-dive.md)** — Teaching AI team policies

**The common thread:** Scanning is easy. Learning is hard. And learning requires remembering.

Memory changes everything.

---

## Links

- **GitHub:** [github.com/Smart-AI-Memory/empathy](https://github.com/Smart-AI-Memory/empathy)
- **Full Test Script:** [examples/full_repo_test.py](https://github.com/Smart-AI-Memory/empathy/blob/main/examples/full_repo_test.py)
- **Documentation:** [docs/](https://github.com/Smart-AI-Memory/empathy/tree/main/docs)

---

*Built by [Smart AI Memory](https://smartaimemory.com) — The AI collaboration framework that remembers.*
