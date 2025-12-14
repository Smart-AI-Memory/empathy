# Reddit Follow-up: Tech Debt Trajectory

**Subreddit:** r/Python (or r/ExperiencedDevs)

**Title:** We tracked our tech debt for 90 days. Here's what trajectory analysis revealed.

---

**TL;DR:** A debt count is useless without context. We built trajectory tracking: store snapshots over time, calculate growth rate, project future values. Our repo: 343 items today, +14.3% monthly growth, projected 472 in 90 days, doubles in 239 days. That's the difference between a metric and actionable intelligence.

---

Every tech debt tool gives you a number. Ours gave us 343.

So what? Is that good? Bad? Getting better? Worse?

The number alone is meaningless. We built trajectory analysis to fix that.

## The Approach

**Step 1: Scan and snapshot**

```python
DEBT_PATTERNS = {
    "todo": r'#\s*TODO[:\s]',
    "fixme": r'#\s*FIXME[:\s]',
    "hack": r'#\s*HACK[:\s]',
    "temporary": r'#\s*TEMP(ORARY)?[:\s]',
}
```

After each scan, store a snapshot with timestamp.

**Step 2: Calculate trajectory**

With multiple snapshots, you can calculate:
- Growth rate (% change per period)
- Trend (increasing/stable/decreasing)
- Projections (where you'll be in 30/90 days)
- Critical threshold (days until 2x)

## Our Results

```
CURRENT: 343 items

HISTORY:
  90 days ago: 200 items
  60 days ago: 250 items
  30 days ago: 300 items
  Today: 343 items

TRAJECTORY:
  Monthly growth: +14.3%
  Trend: INCREASING

PROJECTIONS:
  30 days: 386 items
  90 days: 472 items
  Days until 2x: 239
```

## What We Learned

1. **204 "temporary" markers** — 60% of our debt. These are meant to be removed but haven't been.

2. **+14.3% growth** — We're adding debt faster than removing it.

3. **239 days until 2x** — Not urgent, but not great either.

4. **Top hotspot: test files** — Most debt is in tests, which is less critical than production code.

**Action:** Schedule cleanup sprint targeting `temporary` markers in non-test files.

## The Difference

Without trajectory:
```
Tech debt: 343 items
```

With trajectory:
```
Tech debt: 343 items
  ↑ +14.3% from last month
  → Projected 472 in 90 days
  ⚠️ Doubles in 239 days at current rate
  🎯 Focus: 204 'temporary' markers (60% of total)
```

One is data. The other is intelligence.

## Implementation

Store snapshots as JSON:

```json
{
  "snapshots": [
    {
      "date": "2025-09-12T10:00:00Z",
      "total_items": 200,
      "by_type": {"todo": 120, "fixme": 40, "hack": 25, "temporary": 15}
    },
    ...
  ]
}
```

Calculate projections:

```python
monthly_rate = change_percent / 30
projection_90 = int(current * (1 + monthly_rate * 3))

# Days until 2x
if monthly_rate > 0:
    days_until_2x = int(log(2) / log(1 + monthly_rate/30) * 30)
```

## Code

```python
from empathy_software_plugin.wizards import TechDebtWizard

wizard = TechDebtWizard(pattern_storage_path="./patterns/tech_debt")

result = await wizard.analyze({
    "project_path": ".",
    "track_history": True,
})

print(f"Trend: {result['trajectory']['trend']}")
print(f"Days until 2x: {result['trajectory']['days_until_critical']}")
```

Full example: https://github.com/Smart-AI-Memory/empathy/blob/main/examples/website_examples/02_tech_debt_trajectory.py

---

Do you track debt trends, or just point-in-time counts? Curious how other teams approach this.
