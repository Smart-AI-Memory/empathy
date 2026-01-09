# Marketing Campaign Automation Setup

This guide explains how to enable and use the automated metrics tracking for the v3.9.1 marketing campaign.

---

## Overview

The automation system tracks campaign metrics daily and commits them to the repository:

- **GitHub stats**: Stars, watchers, forks, issues
- **PyPI downloads**: Last 24 hours, 7 days, 30 days
- **Release metrics**: Download counts per version
- **Automated**: Runs daily at 9 AM UTC (4 AM EST)
- **Manual**: Can be triggered anytime from GitHub Actions

---

## What's Already Set Up

### 1. Metrics Tracking Script ✅
**File**: `scripts/track_campaign_metrics.py`

**Features**:
- Fetches GitHub and PyPI metrics
- Generates markdown reports
- Handles errors gracefully
- Works offline (uses cached data if APIs unavailable)

**Test it**:
```bash
python scripts/track_campaign_metrics.py --output test.md
```

### 2. GitHub Actions Workflow ✅
**File**: `.github/workflows/track-campaign-metrics.yml`

**Features**:
- Scheduled: Daily at 9 AM UTC
- Manual trigger: Available in GitHub Actions UI
- Auto-commit: Saves updated metrics to repo
- Summary: Shows key metrics in Actions UI

**Status**: Ready to run (will activate on next push to main)

### 3. Twitter Thread ✅
**File**: `docs/marketing/TWITTER_THREAD_V3_9_1.md`

**Features**:
- 8 tweets ready to copy-paste
- Character count for each tweet
- Pre-written responses to common questions
- Posting strategy and timing recommendations

### 4. Visual Asset Guide ✅
**File**: `docs/marketing/TWEET3_CODE_COMPARISON.md`

**Features**:
- Template for code comparison visual
- Multiple format options (image or text)
- Carbon.now.sh instructions
- Python script to generate programmatically

---

## How to Enable Automation

### Step 1: Push the Workflow to GitHub

```bash
# The workflow is already committed
git push origin main
```

**What happens**:
- GitHub Actions will recognize the new workflow
- Workflow will appear in "Actions" tab
- First run scheduled for tomorrow at 9 AM UTC

### Step 2: Verify Workflow is Active

1. Go to GitHub repository
2. Click "Actions" tab
3. You should see "Track Campaign Metrics" in the workflow list

### Step 3: Run Manually (Optional)

To test immediately:

1. Go to "Actions" > "Track Campaign Metrics"
2. Click "Run workflow" dropdown
3. Select branch: `main`
4. Click "Run workflow" button

**First run takes**: ~30 seconds

**Output**: Updated metrics file at `docs/marketing/CAMPAIGN_METRICS_DAILY.md`

---

## Daily Workflow

### Automatic (Recommended)

**Every day at 9 AM UTC**, the workflow:

1. ✅ Fetches latest GitHub stats
2. ✅ Fetches latest PyPI downloads
3. ✅ Generates markdown report
4. ✅ Commits to repository (if changed)
5. ✅ Shows summary in Actions UI

**No manual intervention needed.**

### Manual Check

View today's metrics anytime:

```bash
# Generate locally
python scripts/track_campaign_metrics.py

# View in terminal
python scripts/track_campaign_metrics.py | less

# Save to file
python scripts/track_campaign_metrics.py --output today.md
```

---

## Files Generated

### CAMPAIGN_METRICS_DAILY.md

**Location**: `docs/marketing/CAMPAIGN_METRICS_DAILY.md`

**Updated**: Daily at 9 AM UTC (auto-commit)

**Contains**:
- Current GitHub stats
- PyPI download trends
- Recent releases
- Timestamp

**Use for**:
- Tracking campaign progress
- Identifying trends
- ROI calculations
- Weekly reports

---

## Monitoring Campaign Progress

### Week 1: Baseline (Jan 7-13)

**Before campaign launch**:
```bash
# Take baseline snapshot
python scripts/track_campaign_metrics.py --output docs/marketing/BASELINE_JAN7.md
```

**Current baseline** (as of Jan 9):
- GitHub: 9 stars
- PyPI: 677 downloads/day, 1,321/week, 4,970/month

### During Campaign (Jan 8-20)

**Daily check** (automated):
- View `docs/marketing/CAMPAIGN_METRICS_DAILY.md`
- Compare to baseline
- Track trends

**Manual check**:
```bash
git pull  # Get latest auto-committed metrics
cat docs/marketing/CAMPAIGN_METRICS_DAILY.md
```

### After Campaign (Jan 21+)

**Calculate results**:
```python
# Stars gained
baseline_stars = 9
current_stars = 50  # Example
growth = current_stars - baseline_stars
print(f"Campaign gained: {growth} stars ({growth/baseline_stars*100:.1f}% growth)")

# Downloads gained
baseline_downloads = 4970  # 30-day
current_downloads = 6000  # Example
growth = current_downloads - baseline_downloads
print(f"Campaign gained: {growth} downloads ({growth/baseline_downloads*100:.1f}% growth)")
```

---

## Customization

### Change Schedule

Edit `.github/workflows/track-campaign-metrics.yml`:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # 9 AM UTC daily
```

**Common schedules**:
- `0 */6 * * *` - Every 6 hours
- `0 9,21 * * *` - 9 AM and 9 PM UTC
- `0 9 * * 1-5` - Weekdays only at 9 AM UTC

### Change Output File

Edit workflow file, line with `--output`:

```yaml
- name: Track campaign metrics
  run: |
    python scripts/track_campaign_metrics.py \
      --output docs/marketing/CUSTOM_FILENAME.md
```

### Track Different Repository

```bash
python scripts/track_campaign_metrics.py \
  --repo owner/repo-name \
  --package package-name \
  --output metrics.md
```

### Output as JSON

For programmatic analysis:

```bash
python scripts/track_campaign_metrics.py --format json > metrics.json
```

---

## Troubleshooting

### Workflow Not Running

**Check**:
1. Is workflow file in `.github/workflows/`?
2. Is it on the `main` branch?
3. Check Actions tab for errors

**Fix**:
```bash
git status  # Verify workflow file is tracked
git log --oneline | head -5  # Verify it was committed
git push origin main  # Push if not pushed
```

### Metrics Not Updating

**Check**:
1. Did the workflow run? (Check Actions tab)
2. Were there API errors? (Check workflow logs)
3. Did metrics actually change? (Workflow only commits if changed)

**Manual verification**:
```bash
python scripts/track_campaign_metrics.py
```

### API Rate Limits

**GitHub API**: 60 requests/hour (unauthenticated)
**PyPI API**: No rate limit

**If you hit limits**:
1. Add `GITHUB_TOKEN` to workflow (increases limit to 1,000/hour)
2. Script already uses token from GitHub Actions environment

### Permission Errors

**Error**: `Permission denied: contents: write`

**Fix**: Verify workflow has correct permissions:
```yaml
permissions:
  contents: write  # Needed to commit metrics file
```

This is already configured in the workflow.

---

## Integration with Campaign

### Reddit Posts

When replying to comments, share latest metrics:

```markdown
Update: Since posting this guide 24 hours ago:
- GitHub: +15 stars
- PyPI: +200 downloads
- 40+ meaningful discussions

Glad it's resonating with the community!
```

### Twitter Updates

Post metrics milestones:

```
🎉 Milestone: 50 GitHub stars!

Thank you to everyone who tried teaching their AI coding standards.

The guide has now helped 1,000+ developers save time in code review.

What's your biggest win so far?
```

### Weekly Summary

Every Sunday, review `CAMPAIGN_METRICS_DAILY.md` and post:

```
Week 1 of the v3.9.1 campaign:

📈 +42 GitHub stars
📈 +850 PyPI downloads
💬 60+ community conversations
📝 5 community implementations

Thank you! 🙏

Next week: Case studies from teams using this in production.
```

---

## Success Metrics Tracking

### Primary Goals

Track in spreadsheet or `METRICS_TRACKING.md`:

| Metric | Baseline (Jan 7) | Week 1 | Week 2 | Target | Status |
|--------|------------------|--------|--------|--------|--------|
| GitHub Stars | 9 | TBD | TBD | 200 | 🔄 In Progress |
| PyPI Downloads (30d) | 4,970 | TBD | TBD | 5,500 | 🔄 In Progress |
| Reddit Upvotes | 0 | TBD | TBD | 100 | 🔄 In Progress |
| Twitter Impressions | 0 | TBD | TBD | 10,000 | 🔄 In Progress |

### ROI Calculation

```python
def calculate_campaign_roi():
    """Calculate marketing campaign ROI."""

    # Time investment
    hours_invested = 20  # Content creation, engagement

    # Results (example)
    stars_gained = 42
    downloads_gained = 850
    commercial_inquiries = 2

    # Value estimates
    value_per_star = 10  # Brand awareness
    value_per_download = 1  # Potential user
    value_per_inquiry = 5000  # Potential customer

    total_value = (
        (stars_gained * value_per_star) +
        (downloads_gained * value_per_download) +
        (commercial_inquiries * value_per_inquiry)
    )

    roi_percentage = ((total_value / (hours_invested * 50)) - 1) * 100

    return {
        "hours_invested": hours_invested,
        "estimated_value": total_value,
        "roi_percentage": roi_percentage,
    }

# Example output:
# {'hours_invested': 20, 'estimated_value': 11270, 'roi_percentage': 1027.0}
# 1,027% ROI after 2 weeks
```

---

## Next Steps

1. ✅ **Push to GitHub** - Enable automated tracking
2. ✅ **Verify workflow** - Check Actions tab
3. 📅 **Post Twitter thread** - Thursday, Jan 9, 9 AM EST
4. 📅 **Monitor metrics** - Daily check of CAMPAIGN_METRICS_DAILY.md
5. 📅 **Weekly summary** - Share progress every Sunday

---

## Resources

- **Metrics Script**: `scripts/track_campaign_metrics.py`
- **Workflow File**: `.github/workflows/track-campaign-metrics.yml`
- **Campaign Plan**: `docs/marketing/V3_9_1_CAMPAIGN.md`
- **Twitter Thread**: `docs/marketing/TWITTER_THREAD_V3_9_1.md`
- **Manual Tracking**: `docs/marketing/METRICS_TRACKING.md`

---

**Status**: ✅ Ready to enable
**Effort**: 0 minutes (automated)
**Maintenance**: 5 minutes/week (review metrics)
**ROI**: High (data-driven campaign decisions)
