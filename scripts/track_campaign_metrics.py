#!/usr/bin/env python3
"""Campaign Metrics Tracker

Fetches real metrics from GitHub, PyPI, and other sources to populate
the campaign tracking template with live data.

Usage:
    python scripts/track_campaign_metrics.py
    python scripts/track_campaign_metrics.py --output docs/marketing/CAMPAIGN_METRICS_LIVE.md
    python scripts/track_campaign_metrics.py --format json

Example for tutorial:
    This script demonstrates how to track marketing campaign metrics
    using public APIs. Adapt for your own project by changing the
    repo_owner, repo_name, and package_name variables.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    import requests
except ImportError:
    print("Error: requests library required")
    print("Install: pip install requests")
    sys.exit(1)


class CampaignMetricsTracker:
    """Track marketing campaign metrics from various sources."""

    def __init__(
        self,
        repo_owner: str = "Smart-AI-Memory",
        repo_name: str = "empathy-framework",
        package_name: str = "empathy-framework",
    ):
        """Initialize tracker with repository and package info."""
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.package_name = package_name
        self.github_api = "https://api.github.com"
        self.pypi_api = "https://pypistats.org/api"

    def get_github_stats(self) -> dict[str, Any]:
        """Fetch GitHub repository statistics.

        Returns:
            Dict with stars, watchers, forks, open_issues
        """
        url = f"{self.github_api}/repos/{self.repo_owner}/{self.repo_name}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            return {
                "stars": data.get("stargazers_count", 0),
                "watchers": data.get("subscribers_count", 0),
                "forks": data.get("forks_count", 0),
                "open_issues": data.get("open_issues_count", 0),
                "fetched_at": datetime.now().isoformat(),
            }
        except requests.RequestException as e:
            print(f"Warning: Could not fetch GitHub stats: {e}")
            return {
                "stars": 0,
                "watchers": 0,
                "forks": 0,
                "open_issues": 0,
                "error": str(e),
            }

    def get_github_traffic(self) -> dict[str, Any]:
        """Fetch GitHub traffic statistics (requires authentication).

        Note: Traffic stats require repo owner authentication.
        Returns empty dict if not authenticated.

        Returns:
            Dict with views, unique_visitors, clones
        """
        # Traffic endpoint requires authentication
        # For public demonstration, return placeholder
        return {
            "views_14d": "Requires authentication",
            "unique_visitors_14d": "Requires authentication",
            "note": "Use GitHub personal access token for traffic stats",
        }

    def get_pypi_downloads(self, period: str = "recent") -> dict[str, Any]:
        """Fetch PyPI download statistics.

        Args:
            period: 'recent' (last 7 days) or 'overall'

        Returns:
            Dict with download counts
        """
        url = f"{self.pypi_api}/packages/{self.package_name}/{period}"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()

            if period == "recent":
                # Recent endpoint returns last 7 days
                return {
                    "last_day": data["data"]["last_day"],
                    "last_week": data["data"]["last_week"],
                    "last_month": data["data"]["last_month"],
                    "fetched_at": datetime.now().isoformat(),
                }
            else:
                return data

        except requests.RequestException as e:
            print(f"Warning: Could not fetch PyPI stats: {e}")
            return {
                "last_day": 0,
                "last_week": 0,
                "last_month": 0,
                "error": str(e),
            }

    def get_github_releases(self) -> list[dict[str, Any]]:
        """Fetch recent GitHub releases.

        Returns:
            List of recent releases with tag, date, downloads
        """
        url = f"{self.github_api}/repos/{self.repo_owner}/{self.repo_name}/releases"

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            releases = response.json()

            return [
                {
                    "tag": release["tag_name"],
                    "name": release["name"],
                    "published": release["published_at"],
                    "downloads": sum(
                        asset.get("download_count", 0) for asset in release.get("assets", [])
                    ),
                }
                for release in releases[:5]  # Last 5 releases
            ]

        except requests.RequestException as e:
            print(f"Warning: Could not fetch releases: {e}")
            return []

    def get_all_metrics(self) -> dict[str, Any]:
        """Fetch all available metrics.

        Returns:
            Dict with all metrics combined
        """
        print("Fetching GitHub stats...")
        github_stats = self.get_github_stats()

        print("Fetching PyPI downloads...")
        pypi_stats = self.get_pypi_downloads()

        print("Fetching releases...")
        releases = self.get_github_releases()

        return {
            "campaign_date": datetime.now().strftime("%Y-%m-%d"),
            "github": github_stats,
            "pypi": pypi_stats,
            "releases": releases,
            "traffic": self.get_github_traffic(),
        }

    def format_as_markdown(self, metrics: dict[str, Any]) -> str:
        """Format metrics as markdown report.

        Args:
            metrics: Dict of metrics from get_all_metrics()

        Returns:
            Markdown formatted report
        """
        github = metrics["github"]
        pypi = metrics["pypi"]
        releases = metrics["releases"]

        md = f"""# Campaign Metrics - Live Data

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Repository:** {self.repo_owner}/{self.repo_name}
**Package:** {self.package_name}

---

## Current Stats

### GitHub Repository

| Metric | Count |
|--------|-------|
| ⭐ Stars | {github['stars']:,} |
| 👀 Watchers | {github['watchers']:,} |
| 🔱 Forks | {github['forks']:,} |
| 🐛 Open Issues | {github['open_issues']:,} |

**Updated:** {github.get('fetched_at', 'Unknown')}

---

### PyPI Downloads

| Period | Downloads |
|--------|-----------|
| Last 24 hours | {pypi.get('last_day', 0):,} |
| Last 7 days | {pypi.get('last_week', 0):,} |
| Last 30 days | {pypi.get('last_month', 0):,} |

**Updated:** {pypi.get('fetched_at', 'Unknown')}

---

### Recent Releases

"""

        for release in releases:
            published = datetime.fromisoformat(release["published"].replace("Z", "+00:00"))
            days_ago = (datetime.now(published.tzinfo) - published).days

            md += f"""
#### {release['tag']} - {release['name']}
- **Released:** {published.strftime("%Y-%m-%d")} ({days_ago} days ago)
- **Downloads:** {release['downloads']:,}
"""

        md += """
---

## How to Track Your Own Metrics

This report was generated using the `track_campaign_metrics.py` script.

**Setup for your project:**

```python
from scripts.track_campaign_metrics import CampaignMetricsTracker

# Initialize with your repo/package info
tracker = CampaignMetricsTracker(
    repo_owner="your-username",
    repo_name="your-repo",
    package_name="your-package"
)

# Fetch all metrics
metrics = tracker.get_all_metrics()

# Output as markdown
report = tracker.format_as_markdown(metrics)
print(report)
```

**Automate with GitHub Actions:**

See `docs/tutorials/automating-metrics-tracking.md` for a complete guide
on setting up automated daily metric tracking.

---

## API Sources

- **GitHub Stats:** `GET https://api.github.com/repos/{owner}/{repo}`
- **PyPI Stats:** `GET https://pypistats.org/api/packages/{package}/recent`
- **No authentication required** for basic stats (stars, downloads)
- **Authentication required** for traffic stats (views, visitors)

---

**Next Steps:**

1. Track these metrics daily for your campaign
2. Compare week-over-week growth
3. Correlate with marketing activities (posts, launches)
4. Calculate ROI based on time invested vs growth

**Tutorial:** [Campaign Metrics Tracking Guide](../tutorials/campaign-metrics-tracking.md)
"""

        return md


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Track marketing campaign metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate markdown report
  python scripts/track_campaign_metrics.py

  # Save to file
  python scripts/track_campaign_metrics.py --output metrics.md

  # JSON output for automation
  python scripts/track_campaign_metrics.py --format json

  # Custom repo/package
  python scripts/track_campaign_metrics.py --repo owner/repo --package package-name
        """,
    )

    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file (default: stdout)",
    )

    parser.add_argument(
        "--format",
        "-f",
        choices=["markdown", "json"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    parser.add_argument(
        "--repo",
        help="Repository in format owner/name (default: Smart-AI-Memory/empathy-framework)",
    )

    parser.add_argument(
        "--package",
        help="PyPI package name (default: empathy-framework)",
    )

    args = parser.parse_args()

    # Parse repo owner/name if provided
    if args.repo:
        if "/" not in args.repo:
            print("Error: --repo must be in format owner/name")
            sys.exit(1)
        repo_owner, repo_name = args.repo.split("/", 1)
    else:
        repo_owner = "Smart-AI-Memory"
        repo_name = "empathy-framework"

    package_name = args.package or "empathy-framework"

    # Create tracker
    tracker = CampaignMetricsTracker(repo_owner, repo_name, package_name)

    # Fetch metrics
    print(f"Fetching metrics for {repo_owner}/{repo_name}...\n")
    metrics = tracker.get_all_metrics()

    # Format output
    if args.format == "json":
        output = json.dumps(metrics, indent=2)
    else:
        output = tracker.format_as_markdown(metrics)

    # Write output
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(output)
        print(f"\n✅ Metrics saved to {args.output}")
    else:
        print("\n" + "=" * 80)
        print(output)


if __name__ == "__main__":
    main()
