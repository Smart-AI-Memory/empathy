# Bug Correlation: How AI Learns From Your Team's Debugging History

**Date:** December 12, 2025
**Author:** Patrick Roebuck
**Series:** Memory-Enhanced Development (Part 2 of 4)

---

## TL;DR

Bug correlation uses persistent memory to match new errors against historical patterns your team has already solved. In our test: 4 matches found, each with proven fixes and estimated resolution times. Here's exactly how it works.

---

## The Problem With Stateless Debugging

Every debugging session with current AI tools starts from zero.

Sarah fixes a tricky `ModuleNotFoundError` in September. She figures out the dependency issue, updates requirements.txt, and moves on. Three months later, Mike hits the exact same pattern—different module name, same root cause.

Mike's AI assistant has no idea Sarah already solved this. So Mike spends another 15 minutes figuring out what Sarah already knew.

**Multiply this across a team, across a year.** That's hundreds of hours lost to re-solving solved problems.

---

## How Bug Correlation Works

### Step 1: Record Resolutions

When bugs get fixed, we store the pattern:

```python
historical_bugs = [
    {
        "bug_id": "bug_20250915_abc123",
        "error_type": "import_error",
        "error_message": "ModuleNotFoundError: No module named 'redis'",
        "root_cause": "Missing dependency in requirements.txt",
        "fix_applied": "Added redis to requirements.txt and installed",
        "resolution_time_minutes": 5,
        "resolved_by": "@sarah",
    },
    {
        "bug_id": "bug_20251001_def456",
        "error_type": "async_timing",
        "error_message": "RuntimeWarning: coroutine was never awaited",
        "root_cause": "Missing await keyword on async function call",
        "fix_applied": "Added await keyword to async memory operation",
        "resolution_time_minutes": 10,
        "resolved_by": "@mike",
    },
]
```

These patterns live in `./patterns/debugging/`—version-controlled JSON files in your repo. No external database required.

### Step 2: Classify New Bugs

When a new error appears, we classify it:

```python
result = await wizard.analyze({
    "error_message": "ModuleNotFoundError: No module named 'structlog'",
    "file_path": "src/logging/handler.py",
    "correlate_with_history": True,
})
```

The wizard extracts:
- **Error type**: `import_error`
- **Module involved**: `structlog`
- **File context**: logging handler

### Step 3: Calculate Similarity

Here's the actual similarity calculation:

```python
def _calculate_similarity(self, new_bug: dict, historical: dict) -> float:
    """
    Calculate how similar two bugs are.

    Factors:
    - Same error type (40% weight)
    - Similar error message (30% weight)
    - Same file pattern (20% weight)
    - Similar context (10% weight)
    """
    score = 0.0

    # Error type match (most important)
    if new_bug["error_type"] == historical["error_type"]:
        score += 0.4

    # Message similarity (fuzzy matching)
    message_sim = self._fuzzy_match(
        new_bug["error_message"],
        historical["error_message"]
    )
    score += message_sim * 0.3

    # File pattern match
    if self._same_file_type(new_bug["file_path"], historical["file_path"]):
        score += 0.2

    # Context similarity
    context_sim = self._context_match(new_bug, historical)
    score += context_sim * 0.1

    return score
```

### Step 4: Return Matches With Fixes

If similarity exceeds the threshold (default 40%), we return the match:

```
HISTORICAL MATCH FOUND:
  Similarity: 100%
  Root Cause: Missing dependency in requirements.txt
  Fix Applied: Added redis to requirements.txt and installed
  Resolution Time: 5 minutes
  Resolved By: @sarah

RECOMMENDED FIX:
  Add structlog to requirements.txt and install
```

---

## Real Results From Our Codebase

We ran this against the Empathy Framework repository with 4 seeded historical patterns:

| Test Bug | Matches | Best Match | Recommended Fix |
|----------|---------|------------|-----------------|
| `ModuleNotFoundError: structlog` | 2 | 100% | Add to requirements.txt |
| `RuntimeWarning: coroutine not awaited` | 1 | 40% | Add await keyword |
| `AttributeError: NoneType has no 'items'` | 1 | 78% | Add None check |

**Key insight:** The `structlog` error matched both `redis` and another import error pattern because the *error type* and *message structure* were identical—only the module name differed.

---

## Why 40% Threshold?

We calibrated based on real-world testing:

- **Below 40%**: Too many false positives. Unrelated bugs get matched.
- **40-60%**: Good for "similar pattern" suggestions. Worth reviewing.
- **60-80%**: Strong match. High confidence the fix applies.
- **Above 80%**: Near-identical bug. Fix almost certainly works.

The wizard returns matches with confidence scores so developers can judge relevance themselves.

---

## Pattern Storage Architecture

```
./patterns/debugging/
├── bug_20250915_abc123.json
├── bug_20251001_def456.json
├── bug_20251115_ghi789.json
└── ...
```

Each file contains:

```json
{
  "bug_id": "bug_20250915_abc123",
  "date": "2025-09-15T10:30:00",
  "error_type": "import_error",
  "error_message": "ModuleNotFoundError: No module named 'redis'",
  "file_path": "src/cache/redis_client.py",
  "root_cause": "Missing dependency in requirements.txt",
  "fix_applied": "Added redis to requirements.txt and installed",
  "fix_code": "# requirements.txt\nredis>=4.0.0",
  "resolution_time_minutes": 5,
  "resolved_by": "@sarah",
  "status": "resolved",
  "tags": ["dependency", "import", "requirements"]
}
```

**Why JSON files?**
- Version-controlled with your code
- No external database required
- Works offline
- Easy to review and modify
- Portable across environments

---

## The Memory Benefit

Without persistent memory:

```
ERROR: ModuleNotFoundError: No module named 'structlog'

AI: This error means Python can't find the structlog module.
    Try running: pip install structlog
```

Generic advice. No context. No team knowledge.

With persistent memory:

```
ERROR: ModuleNotFoundError: No module named 'structlog'

AI: This matches 2 similar bugs your team fixed before:

    1. @sarah fixed 'redis' import (100% match, 5 min fix)
       → Added to requirements.txt and installed

    2. @mike fixed 'pydantic' import (95% match, 3 min fix)
       → Same pattern - missing from requirements

    RECOMMENDED: Add structlog to requirements.txt
    ESTIMATED TIME: 3-5 minutes based on team history
```

**That's not incremental improvement. That's institutional knowledge made accessible.**

---

## Try It Yourself

```python
from empathy_software_plugin.wizards import MemoryEnhancedDebuggingWizard

wizard = MemoryEnhancedDebuggingWizard(
    pattern_storage_path="./patterns/debugging"
)

# Analyze a new bug
result = await wizard.analyze({
    "error_message": "Your error here",
    "file_path": "path/to/file.py",
    "correlate_with_history": True,
})

# Record a fix for future correlation
await wizard.record_resolution({
    "error_type": "the_type",
    "error_message": "The error message",
    "root_cause": "What caused it",
    "fix_applied": "What fixed it",
    "resolution_time_minutes": 10,
})
```

Full example: [01_bug_correlation.py](https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/01_bug_correlation.py)

---

## What's Next

- **Part 3:** [Tech Debt Trajectory](03-tech-debt-trajectory-deep-dive.md) — Predicting when debt becomes critical
- **Part 4:** [Security Learning](04-security-learning-deep-dive.md) — Teaching AI your team's security policies

---

## Links

- **GitHub:** [github.com/Smart-AI-Memory/empathy](https://github.com/Smart-AI-Memory/empathy)
- **Part 1:** [We Tested Memory on Our Own Codebase](01-we-tested-memory-on-our-own-codebase.md)
- **Documentation:** [docs/](https://github.com/Smart-AI-Memory/empathy/tree/main/docs)

---

*Built by [Smart AI Memory](https://smartaimemory.com) — The AI collaboration framework that remembers.*
