# Tutorial: Automating Campaign Metrics Tracking

**Level:** Intermediate
**Time:** 30 minutes
**Prerequisites:** Basic Python knowledge, GitHub account, published package (PyPI, npm, etc.)

---

## What You'll Learn

- Fetch real-time metrics from GitHub and PyPI APIs
- Automate metric tracking with Python scripts
- Visualize campaign progress with markdown reports
- Set up daily automated tracking with GitHub Actions

---

## Why Track Metrics?

Marketing campaigns need measurable outcomes. This tutorial shows you how to:

✅ Track GitHub stars, forks, watchers automatically
✅ Monitor package downloads (PyPI, npm, etc.)
✅ Generate beautiful reports with real data
✅ Automate tracking with GitHub Actions (run daily)
✅ Adapt for any open-source project

**Real example:** We use this for Empathy Framework's v3.9.1 campaign. [See live metrics](../marketing/CAMPAIGN_METRICS_LIVE.md)

---

## Step 1: Understanding the APIs

### GitHub API (No Auth Required for Basic Stats)

**Endpoint:**
```
GET https://api.github.com/repos/{owner}/{repo}
```

**Returns:**
- `stargazers_count` - GitHub stars
- `subscribers_count` - Watchers
- `forks_count` - Forks
- `open_issues_count` - Open issues/PRs

**Example:**
```bash
curl https://api.github.com/repos/Smart-AI-Memory/empathy-framework
```

**Rate limit:** 60 requests/hour (unauthenticated), 5000/hour (authenticated)

---

### PyPI API (No Auth Required)

**Endpoint:**
```
GET https://pypistats.org/api/packages/{package}/recent
```

**Returns:**
- `last_day` - Downloads in last 24 hours
- `last_week` - Downloads in last 7 days
- `last_month` - Downloads in last 30 days

**Example:**
```bash
curl https://pypistats.org/api/packages/empathy-framework/recent
```

**Rate limit:** Reasonable usage (don't hammer it)

---

## Step 2: The Tracking Script

We've created a production-ready script you can use.

**Location:** `scripts/track_campaign_metrics.py`

**Features:**
- Fetches GitHub and PyPI stats
- Formats as markdown or JSON
- Handles errors gracefully
- Easy to adapt for your project

### Quick Start

```bash
# Install dependencies
pip install requests

# Run for Empathy Framework (example)
python scripts/track_campaign_metrics.py

# Run for YOUR project
python scripts/track_campaign_metrics.py \
    --repo your-username/your-repo \
    --package your-package-name \
    --output metrics.md
```

---

## Step 3: Adapt for Your Project

### Basic Adaptation

```python
from scripts.track_campaign_metrics import CampaignMetricsTracker

# Initialize with YOUR repo/package
tracker = CampaignMetricsTracker(
    repo_owner="your-github-username",
    repo_name="your-repository",
    package_name="your-pypi-package"
)

# Fetch all metrics
metrics = tracker.get_all_metrics()

# Generate markdown report
report = tracker.format_as_markdown(metrics)
print(report)
```

### Add Custom Metrics

Want to track additional metrics? Extend the class:

```python
class MyMetricsTracker(CampaignMetricsTracker):
    """Extended tracker with custom metrics."""

    def get_twitter_followers(self) -> dict:
        """Fetch Twitter follower count.

        Requires Twitter API credentials.
        """
        # Your Twitter API code here
        return {"followers": 1234}

    def get_website_analytics(self) -> dict:
        """Fetch website analytics.

        Could use Google Analytics API, Plausible, etc.
        """
        # Your analytics code here
        return {"monthly_visitors": 5000}

    def get_all_metrics(self) -> dict:
        """Fetch all metrics including custom ones."""
        metrics = super().get_all_metrics()

        # Add custom metrics
        metrics["twitter"] = self.get_twitter_followers()
        metrics["website"] = self.get_website_analytics()

        return metrics
```

---

## Step 4: Track Campaign Progress

### Daily Tracking Workflow

**Morning routine (5 minutes):**

```bash
# Generate today's metrics
python scripts/track_campaign_metrics.py \
    --output metrics/$(date +%Y-%m-%d).md

# Compare to yesterday
python scripts/compare_metrics.py \
    metrics/$(date -d yesterday +%Y-%m-%d).md \
    metrics/$(date +%Y-%m-%d).md
```

**Output example:**
```
📊 Campaign Progress (Jan 7 → Jan 8)

GitHub:
  Stars: 245 → 312 (+67, +27%)
  Forks: 18 → 23 (+5, +28%)

PyPI:
  Daily downloads: 156 → 289 (+133, +85%)
  Weekly downloads: 892 → 1,247 (+355, +40%)

🎯 Trending up! Great progress.
```

### Weekly Analysis

```python
import glob
from pathlib import Path
import json

# Load all daily metrics
metric_files = sorted(Path("metrics").glob("*.json"))
metrics_history = [json.loads(f.read_text()) for f in metric_files]

# Calculate weekly growth
first_day = metrics_history[0]
last_day = metrics_history[-1]

stars_growth = last_day["github"]["stars"] - first_day["github"]["stars"]
downloads_growth = last_day["pypi"]["last_week"] - first_day["pypi"]["last_week"]

print(f"Week 1 Results:")
print(f"  Stars gained: {stars_growth:,}")
print(f"  Download increase: {downloads_growth:,} (+{downloads_growth/first_day['pypi']['last_week']*100:.1f}%)")
```

---

## Step 5: Automate with GitHub Actions

Never manually track metrics again!

### Create `.github/workflows/track-metrics.yml`

```yaml
name: Track Campaign Metrics

on:
  schedule:
    # Run every day at 9 AM UTC
    - cron: '0 9 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  track-metrics:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install requests

      - name: Generate metrics report
        run: |
          python scripts/track_campaign_metrics.py \
            --output docs/marketing/CAMPAIGN_METRICS_LIVE.md

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add docs/marketing/CAMPAIGN_METRICS_LIVE.md
          git commit -m "chore: Update campaign metrics [skip ci]" || exit 0
          git push
```

**What this does:**
- Runs every day at 9 AM UTC
- Fetches latest metrics
- Updates CAMPAIGN_METRICS_LIVE.md
- Commits and pushes automatically

**Result:** Always-current metrics on your repo!

---

## Step 6: Visualize Trends

### Generate Charts with Python

```python
import matplotlib.pyplot as plt
from datetime import datetime
import json
from pathlib import Path

# Load historical metrics
metrics_files = sorted(Path("metrics").glob("2026-01-*.json"))
data = [json.loads(f.read_text()) for f in metrics_files]

# Extract data
dates = [datetime.fromisoformat(m["campaign_date"]) for m in data]
stars = [m["github"]["stars"] for m in data]
downloads = [m["pypi"]["last_week"] for m in data]

# Create chart
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# GitHub stars over time
ax1.plot(dates, stars, marker='o', linewidth=2, markersize=6)
ax1.set_title('GitHub Stars - Campaign Growth', fontsize=14, fontweight='bold')
ax1.set_ylabel('Total Stars')
ax1.grid(True, alpha=0.3)

# PyPI downloads over time
ax2.plot(dates, downloads, marker='s', linewidth=2, markersize=6, color='green')
ax2.set_title('PyPI Weekly Downloads', fontsize=14, fontweight='bold')
ax2.set_ylabel('Downloads')
ax2.set_xlabel('Date')
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('campaign_metrics.png', dpi=150, bbox_inches='tight')
print("✅ Chart saved to campaign_metrics.png")
```

### Generate Markdown Tables

```python
def format_metrics_table(metrics_history: list) -> str:
    """Format metrics as markdown table."""
    md = "| Date | Stars | Forks | Downloads (7d) |\n"
    md += "|------|-------|-------|----------------|\n"

    for m in metrics_history:
        date = m["campaign_date"]
        stars = m["github"]["stars"]
        forks = m["github"]["forks"]
        downloads = m["pypi"]["last_week"]

        md += f"| {date} | {stars:,} | {forks:,} | {downloads:,} |\n"

    return md
```

---

## Step 7: Calculate ROI

### Time Investment vs Growth

```python
def calculate_campaign_roi(
    hours_invested: float,
    stars_gained: int,
    downloads_gained: int,
    commercial_inquiries: int = 0
) -> dict:
    """Calculate campaign return on investment.

    Args:
        hours_invested: Total time spent on campaign
        stars_gained: GitHub stars gained
        downloads_gained: Package downloads gained
        commercial_inquiries: Number of business inquiries

    Returns:
        Dict with ROI metrics
    """
    # Value assumptions (adjust for your context)
    value_per_star = 10  # $10 value per GitHub star (visibility)
    value_per_download = 1  # $1 value per download (adoption)
    value_per_inquiry = 5000  # $5000 potential per commercial inquiry

    total_value = (
        (stars_gained * value_per_star) +
        (downloads_gained * value_per_download) +
        (commercial_inquiries * value_per_inquiry)
    )

    roi_ratio = total_value / (hours_invested * 50) if hours_invested > 0 else 0  # Assuming $50/hour

    return {
        "hours_invested": hours_invested,
        "stars_gained": stars_gained,
        "downloads_gained": downloads_gained,
        "commercial_inquiries": commercial_inquiries,
        "estimated_value": total_value,
        "roi_ratio": roi_ratio,
        "roi_percentage": (roi_ratio - 1) * 100,
    }

# Example usage
roi = calculate_campaign_roi(
    hours_invested=20,  # 20 hours spent on campaign
    stars_gained=150,
    downloads_gained=1000,
    commercial_inquiries=2
)

print(f"Campaign ROI Analysis:")
print(f"  Time invested: {roi['hours_invested']} hours")
print(f"  Estimated value: ${roi['estimated_value']:,}")
print(f"  ROI: {roi['roi_percentage']:.1f}%")
```

---

## Real Example: Empathy Framework v3.9.1 Campaign

### Campaign Setup

**Date:** January 7-13, 2026
**Focus:** Security hardening + Level 5 empathy story
**Platforms:** Reddit (r/Python, r/ClaudeAI), Twitter, Dev.to

**Baseline (Jan 7):**
- GitHub Stars: [See live metrics](../marketing/CAMPAIGN_METRICS_LIVE.md)
- PyPI Downloads: [See live metrics](../marketing/CAMPAIGN_METRICS_LIVE.md)

**Tracking:**
```bash
# Daily metrics (automated via GitHub Actions)
python scripts/track_campaign_metrics.py \
    --output docs/marketing/CAMPAIGN_METRICS_LIVE.md
```

**View live results:** [CAMPAIGN_METRICS_LIVE.md](../marketing/CAMPAIGN_METRICS_LIVE.md)

---

## Best Practices

### ✅ Do

- **Track consistently** - Same time every day
- **Automate** - Use GitHub Actions, cron jobs
- **Version control** - Commit metrics to git
- **Calculate growth** - Week-over-week, not absolute numbers
- **Context matters** - Note what you posted when metrics spike

### ❌ Don't

- **Don't obsess** - Check once daily, not hourly
- **Don't game metrics** - Artificial inflation hurts long-term
- **Don't ignore quality** - 100 engaged users > 1000 casual
- **Don't track alone** - Correlate with qualitative feedback

---

## Troubleshooting

### Rate Limits

**Problem:** "API rate limit exceeded"

**Solution:**
```python
# Add GitHub token for higher rate limit
import os

headers = {}
if github_token := os.getenv("GITHUB_TOKEN"):
    headers["Authorization"] = f"token {github_token}"

response = requests.get(url, headers=headers)
```

**In GitHub Actions:**
```yaml
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Missing PyPI Stats

**Problem:** Package not on PyPI stats yet

**Solution:** PyPI stats need 24-48 hours after first publish. For new packages, track manually:

```python
# Alternative: Check PyPI JSON API
response = requests.get(f"https://pypi.org/pypi/{package}/json")
data = response.json()
print(f"Latest version: {data['info']['version']}")
print(f"Released: {data['releases'][version][0]['upload_time']}")
```

---

## Next Steps

1. **Copy the script** - `scripts/track_campaign_metrics.py` to your project
2. **Adapt for your repo** - Change owner/name/package
3. **Run manually** - Test that it works
4. **Set up automation** - Add GitHub Actions workflow
5. **Track for 30 days** - See what works

**Questions?** [Open an issue](https://github.com/Smart-AI-Memory/empathy-framework/issues) or [start a discussion](https://github.com/Smart-AI-Memory/empathy-framework/discussions).

---

## Related Resources

- [Campaign Metrics Template](../marketing/METRICS_TRACKING.md) - Manual tracking template
- [Live Metrics Example](../marketing/CAMPAIGN_METRICS_LIVE.md) - Real Empathy Framework data
- [v3.9.1 Campaign Plan](../marketing/V3_9_1_CAMPAIGN.md) - Full campaign strategy

---

**Last Updated:** January 7, 2026
**Difficulty:** Intermediate
**Time to Complete:** 30 minutes
