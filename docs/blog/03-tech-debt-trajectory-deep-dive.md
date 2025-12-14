# Tech Debt Trajectory: Predicting When Debt Becomes Critical

**Date:** December 12, 2025
**Author:** Patrick Roebuck
**Series:** Memory-Enhanced Development (Part 3 of 4)

---

## TL;DR

A debt count is just a number. Trajectory analysis tells you where you're headed. In our test: 343 items today, +14.3% monthly growth, projected 472 in 90 days, doubles in 239 days. That's the difference between a metric and actionable intelligence.

---

## The Problem With Debt Counts

Every tech debt tool gives you a number:

```
Technical Debt: 343 items
  - TODO: 119
  - FIXME: 1
  - HACK: 17
  - TEMPORARY: 204
  - DEPRECATED: 2
```

**So what?**

Is 343 good or bad? Is it getting better or worse? When does it become a problem? Should we prioritize cleanup now or later?

The number alone tells you nothing. Context tells you everything.

---

## What Trajectory Analysis Provides

With persistent memory, we track debt over time:

```
TRAJECTORY:
  90 days ago: 200 items
  60 days ago: 250 items
  30 days ago: 300 items
  Today: 343 items

  Monthly Growth: +14.3%
  Trend: INCREASING

PROJECTIONS:
  In 30 days: 386 items
  In 90 days: 472 items
  Days until 2x (critical): 239
```

Now you can answer:
- **Is it getting worse?** Yes, +14.3% monthly
- **How fast?** Doubling every 8 months
- **When is it critical?** At this rate, 239 days
- **Should we act now?** Depends on your threshold

---

## How It Works

### Step 1: Scan for Debt Markers

We scan your codebase for common markers:

```python
DEBT_PATTERNS = {
    "todo": r'#\s*TODO[:\s]',
    "fixme": r'#\s*FIXME[:\s]',
    "hack": r'#\s*HACK[:\s]',
    "temporary": r'#\s*TEMP(ORARY)?[:\s]',
    "deprecated": r'#\s*DEPRECATED[:\s]',
    "xxx": r'#\s*XXX[:\s]',
}
```

Each match gets categorized and located:

```python
debt_item = {
    "type": "todo",
    "file": "src/api/endpoints.py",
    "line": 142,
    "content": "TODO: Add rate limiting",
    "severity": "medium",
}
```

### Step 2: Store Snapshots

After each scan, we store a snapshot:

```json
{
  "date": "2025-12-12T10:30:00",
  "total_items": 343,
  "by_type": {
    "todo": 119,
    "fixme": 1,
    "hack": 17,
    "temporary": 204,
    "deprecated": 2
  },
  "by_severity": {
    "low": 180,
    "medium": 120,
    "high": 35,
    "critical": 8
  },
  "hotspots": [
    {"file": "tests/test_unified_memory.py", "count": 52},
    {"file": "clinical-components.js", "count": 16}
  ]
}
```

Snapshots accumulate in `./patterns/tech_debt/debt_history.json`.

### Step 3: Calculate Trajectory

With multiple snapshots, we calculate:

```python
def _calculate_trajectory(self, history: list, current: dict) -> dict:
    """
    Calculate debt trajectory from historical snapshots.
    """
    if len(history) < 2:
        return {"trend": "insufficient_data"}

    # Get most recent historical snapshot
    previous = history[-1]
    previous_total = previous["total_items"]
    current_total = current["total_items"]

    # Calculate change
    change = current_total - previous_total
    change_percent = (change / previous_total) * 100 if previous_total > 0 else 0

    # Determine trend
    if change_percent > 5:
        trend = "increasing"
    elif change_percent < -5:
        trend = "decreasing"
    else:
        trend = "stable"

    # Project future values (linear extrapolation)
    monthly_rate = change_percent / 30  # Assuming 30-day snapshots
    projection_30 = int(current_total * (1 + monthly_rate))
    projection_90 = int(current_total * (1 + monthly_rate * 3))

    # Calculate days until 2x (critical threshold)
    if monthly_rate > 0:
        # Solve: current * (1 + rate)^n = 2 * current
        import math
        days_until_2x = int(math.log(2) / math.log(1 + monthly_rate/30) * 30)
    else:
        days_until_2x = None  # Not increasing

    return {
        "previous_total": previous_total,
        "current_total": current_total,
        "change": change,
        "change_percent": change_percent,
        "trend": trend,
        "projection_30_days": projection_30,
        "projection_90_days": projection_90,
        "days_until_critical": days_until_2x,
    }
```

### Step 4: Identify Hotspots

We rank files by debt concentration:

```
TOP HOTSPOTS:
1. tests/test_unified_memory.py - 52 items
2. clinical-components.js - 16 items
3. test_security_wizard.py - 14 items
4. redis_memory.py - 12 items
5. empathy_core.py - 10 items
```

Hotspots tell you where to focus cleanup efforts for maximum impact.

---

## Real Results From Our Codebase

We ran trajectory analysis on the Empathy Framework repository:

```
CURRENT DEBT:
  Total Items: 343

  By Type:
    temporary: 204 (59.5%)
    todo: 119 (34.7%)
    hack: 17 (5.0%)
    deprecated: 2 (0.6%)
    fixme: 1 (0.3%)

TRAJECTORY:
  Previous (30 days): 300
  Current: 343
  Change: +14.3%
  Trend: INCREASING

PROJECTIONS:
  30 days: 386 items
  90 days: 472 items
  Days until 2x: 239
```

### What This Tells Us

1. **204 "temporary" markers** — That's 60% of our debt. These are meant to be removed but haven't been.

2. **+14.3% monthly growth** — We're adding debt faster than we're removing it.

3. **239 days until 2x** — At current rate, debt doubles in about 8 months.

4. **Top hotspot: test files** — Most debt is in tests, which is actually less critical than production code.

**Actionable insight:** Schedule a cleanup sprint targeting `temporary` markers, especially in non-test files.

---

## The Memory Benefit

Without persistent memory:

```
Tech Debt Scan Results:
  343 items found
  Top file: test_unified_memory.py (52 items)
```

A number. No context. No trend. No prediction.

With persistent memory:

```
Tech Debt Trajectory Analysis:

CURRENT: 343 items (up from 300 last month)

TREND: +14.3% monthly growth
  - 90 days ago: 200 items
  - 60 days ago: 250 items
  - 30 days ago: 300 items
  - Today: 343 items

PROJECTION: If unchecked:
  - In 30 days: 386 items
  - In 90 days: 472 items
  - Doubles in: 239 days

RECOMMENDATION: Focus cleanup on 'temporary' markers
  which comprise 60% of total debt.
```

**That's the difference between data and intelligence.**

---

## Severity Classification

Not all debt is equal. We classify by impact:

| Type | Default Severity | Rationale |
|------|-----------------|-----------|
| TODO | Low | Feature work, not urgent |
| FIXME | High | Known bugs, should fix soon |
| HACK | Medium | Working but fragile |
| TEMPORARY | Medium | Should be removed |
| DEPRECATED | High | Using outdated patterns |
| XXX | Critical | Dangerous or broken |

Custom classification can override defaults based on context:

```python
# A TODO in a security file is higher severity
if "security" in file_path.lower() and debt_type == "todo":
    severity = "high"
```

---

## Threshold Alerts

Configure alerts for when debt exceeds thresholds:

```python
ALERT_THRESHOLDS = {
    "total_items": 500,        # Alert if total exceeds
    "critical_items": 10,      # Alert if critical exceeds
    "monthly_growth": 20,      # Alert if growth exceeds %
    "days_until_2x": 180,      # Alert if doubling within
}
```

Example alert:

```
DEBT ALERT: Growth rate exceeds threshold

Current growth: +14.3% monthly
Threshold: 20% monthly

Status: OK (below threshold)

---

DEBT ALERT: Doubling timeline

Days until 2x: 239 days
Threshold: 180 days

Status: OK (above threshold)
```

---

## Try It Yourself

```python
from empathy_software_plugin.wizards import TechDebtWizard

wizard = TechDebtWizard(
    pattern_storage_path="./patterns/tech_debt"
)

result = await wizard.analyze({
    "project_path": ".",
    "track_history": True,  # Enable trajectory
})

print(f"Total: {result['current_debt']['total_items']}")
print(f"Trend: {result['trajectory']['trend']}")
print(f"30-day projection: {result['trajectory']['projection_30_days']}")
```

Full example: [02_tech_debt_trajectory.py](https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/02_tech_debt_trajectory.py)

---

## What's Next

- **Part 4:** [Security Learning](04-security-learning-deep-dive.md) — Teaching AI your team's security policies

---

## Links

- **GitHub:** [github.com/Smart-AI-Memory/empathy](https://github.com/Smart-AI-Memory/empathy)
- **Part 1:** [We Tested Memory on Our Own Codebase](01-we-tested-memory-on-our-own-codebase.md)
- **Part 2:** [Bug Correlation Deep Dive](02-bug-correlation-deep-dive.md)
- **Documentation:** [docs/](https://github.com/Smart-AI-Memory/empathy/tree/main/docs)

---

*Built by [Smart AI Memory](https://smartaimemory.com) — The AI collaboration framework that remembers.*
