# Reddit Follow-up: Bug Correlation

**Subreddit:** r/Python (or r/programming)

**Title:** Built a system that matches new bugs against your team's debugging history. Here's how similarity scoring works.

---

**TL;DR:** When Sarah fixes a bug in September, the fix gets stored with context. When Mike hits a similar error in December, the system finds the match and recommends the proven fix. We use weighted similarity scoring: error type (40%), message pattern (30%), file context (20%), other factors (10%). Threshold of 40% catches useful matches without too many false positives.

---

Follow-up to my earlier post about memory-enhanced dev tools. A few people asked how the bug correlation actually works, so here's the breakdown.

## The Problem

Every debugging session with AI starts from zero. Your team's collective debugging knowledge doesn't persist.

## The Solution

Store bug resolutions as patterns:

```python
{
    "bug_id": "bug_20250915_abc123",
    "error_type": "import_error",
    "error_message": "ModuleNotFoundError: No module named 'redis'",
    "root_cause": "Missing dependency in requirements.txt",
    "fix_applied": "Added redis to requirements.txt",
    "resolution_time_minutes": 5,
    "resolved_by": "@sarah"
}
```

## Similarity Scoring

When a new error comes in, we calculate similarity:

```python
def calculate_similarity(new_bug, historical):
    score = 0.0

    # Error type match (40% weight)
    if new_bug["error_type"] == historical["error_type"]:
        score += 0.4

    # Message similarity (30% weight)
    message_sim = fuzzy_match(
        new_bug["error_message"],
        historical["error_message"]
    )
    score += message_sim * 0.3

    # File pattern match (20% weight)
    if same_file_type(new_bug["file"], historical["file"]):
        score += 0.2

    # Context (10% weight)
    score += context_similarity(new_bug, historical) * 0.1

    return score
```

## Why These Weights?

- **Error type (40%)**: Most predictive. Same type = likely same fix.
- **Message (30%)**: Fuzzy matching catches "No module named 'redis'" ≈ "No module named 'structlog'"
- **File pattern (20%)**: Bugs in similar files often have similar causes
- **Context (10%)**: Stack trace, surrounding code, etc.

## Threshold: 40%

We landed on 40% as the cutoff after testing:

- **Below 40%**: Too many false positives
- **40-60%**: "Similar pattern" suggestions worth reviewing
- **60-80%**: Strong match, high confidence
- **Above 80%**: Near-identical, fix almost certainly applies

## Real Results

Tested on our codebase with 4 seeded historical patterns:

```
New: ModuleNotFoundError: structlog
  → 100% match to redis import error
  → Recommended: Add to requirements.txt

New: RuntimeWarning: coroutine not awaited
  → 40% match to async timing bug
  → Recommended: Add await keyword
```

## Storage

Just JSON files in your repo:

```
./patterns/debugging/
├── bug_20250915_abc123.json
├── bug_20251001_def456.json
└── ...
```

Version controlled. No database needed.

## Code

```python
from empathy_software_plugin.wizards import MemoryEnhancedDebuggingWizard

wizard = MemoryEnhancedDebuggingWizard(
    pattern_storage_path="./patterns/debugging"
)

result = await wizard.analyze({
    "error_message": "Your error here",
    "correlate_with_history": True,
})
```

Full example: https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/01_bug_correlation.py

---

Questions? Curious how others approach institutional debugging knowledge.
