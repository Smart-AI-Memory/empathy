# Reddit Follow-up: Security Learning

**Subreddit:** r/Python (or r/netsec, r/devops)

**Title:** Our security scanner flags 108 issues every time. We taught it to remember team decisions. Now it's 23.

---

**TL;DR:** Security tools flag the same false positives forever. We built learning: record team decisions ("this is a false positive because X"), apply them automatically on future scans. Result: 108 findings → 23 findings. 78.7% noise reduction. Same codebase, same scanner, but now it knows your team's policies.

---

Security alert fatigue is real.

Every scan flags:
- "Hardcoded secret" in test fixtures (it's `test_api_key_12345`)
- "SQL injection" in ORM code (the ORM handles escaping)
- "Insecure random" for UI animations (not cryptographic)

You know these are false positives. Your team decided months ago. But the scanner doesn't remember.

So you review the same 108 findings. Every. Single. Time.

Eventually you stop paying attention. That's when real vulnerabilities slip through.

## The Fix

Record team decisions:

```python
await wizard.record_decision({
    "finding_hash": "hardcoded_secret",
    "decision": "false_positive",
    "reason": "Test fixtures - not real credentials",
    "decided_by": "@sarah",
    "applies_to": "all",  # All findings of this type
})
```

Apply on future scans:

```python
result = await wizard.analyze({
    "project_path": ".",
    "apply_learned_patterns": True,
})
```

## Our Results

```
WITHOUT learning:
  Raw findings: 108
  critical: 99
  high: 6
  medium: 3

WITH learning:
  Raw findings: 108
  After learning: 23
  Suppressed: 85
  Noise reduction: 78.7%
```

## What Got Suppressed

| Type | Before | After | Why |
|------|--------|-------|-----|
| hardcoded_secret | 45 | 0 | Test fixtures |
| sql_injection | 23 | 0 | ORM escaping |
| insecure_random | 18 | 1 | Non-crypto use |
| xss | 12 | 12 | Needs review |
| command_injection | 8 | 8 | Needs review |

The 23 remaining findings are real issues that need attention.

## Decision Granularity

You can scope decisions:

```python
# Suppress all of this type
{"applies_to": "all"}

# Only in files matching pattern
{"applies_to": "pattern", "pattern": "test_*.py"}

# Only this specific instance
{"applies_to": "instance", "file": "tests/fixtures.py", "line": 42}
```

This prevents over-suppression. A hardcoded secret in test fixtures is fine. The same finding in production code should still alert.

## Audit Trail

Every suppression is logged:

```json
{
  "timestamp": "2025-12-12T10:30:00Z",
  "action": "finding_suppressed",
  "finding_type": "hardcoded_secret",
  "file": "tests/fixtures/api_keys.py",
  "suppression_reason": "false_positive",
  "decision_by": "@sarah",
  "decision_date": "2025-10-15T14:30:00Z"
}
```

Compliance teams love this.

## Storage

JSON in your repo:

```json
{
  "decisions": [
    {
      "finding_hash": "hardcoded_secret",
      "decision": "false_positive",
      "reason": "Test fixtures - not real credentials",
      "decided_by": "@sarah",
      "decided_at": "2025-10-15T14:30:00Z",
      "applies_to": "all"
    }
  ]
}
```

Version controlled. Reviewable in PRs. No external database.

## Code

```python
from empathy_software_plugin.wizards import SecurityLearningWizard

wizard = SecurityLearningWizard(
    pattern_storage_path="./patterns/security"
)

result = await wizard.analyze({
    "project_path": ".",
    "apply_learned_patterns": True,
})

print(f"Before: {result['raw_findings_count']}")
print(f"After: {result['summary']['total_after_learning']}")
print(f"Noise reduction: {result['learning_applied']['noise_reduction_percent']}%")
```

Full example: https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/03_security_learning.py

---

What's the worst false positive fatigue you've dealt with? Curious how other teams handle this.
