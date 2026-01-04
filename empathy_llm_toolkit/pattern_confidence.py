"""Pattern Confidence Scoring

Tracks how often stored fixes resolve similar issues,
building confidence scores over time.

Usage:
    from empathy_llm_toolkit.pattern_confidence import PatternConfidenceTracker

    tracker = PatternConfidenceTracker("./patterns")

    # Record when a pattern is suggested
    tracker.record_suggestion("bug_20250915_abc123")

    # Record when a pattern fix is applied
    tracker.record_application("bug_20250915_abc123", successful=True)

    # Get confidence stats
    stats = tracker.get_pattern_stats("bug_20250915_abc123")
    # Returns: {"times_suggested": 15, "times_applied": 12, "success_rate": 0.92}

Author: Empathy Framework Team
Version: 2.1.3
License: Fair Source 0.9
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class PatternUsageStats:
    """Statistics for a single pattern's usage."""

    pattern_id: str
    times_suggested: int = 0
    times_applied: int = 0
    times_successful: int = 0
    times_unsuccessful: int = 0
    last_suggested: str | None = None
    last_applied: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    feedback: list[dict] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate of applied fixes."""
        total = self.times_successful + self.times_unsuccessful
        if total == 0:
            return 0.0
        return self.times_successful / total

    @property
    def application_rate(self) -> float:
        """Calculate how often suggestions lead to applications."""
        if self.times_suggested == 0:
            return 0.0
        return self.times_applied / self.times_suggested

    @property
    def confidence_score(self) -> float:
        """Calculate overall confidence score (0.0 - 1.0)."""
        # Base confidence from success rate
        base = self.success_rate

        # Boost for high application rate
        if self.application_rate > 0.5:
            base += 0.1

        # Boost for volume
        if self.times_applied >= 5:
            base += 0.1

        # Decay for low usage
        if self.times_suggested < 2:
            base *= 0.8

        return min(max(base, 0.0), 1.0)


class PatternConfidenceTracker:
    """Tracks pattern usage and calculates confidence scores.

    Stores usage data in patterns/confidence/usage_stats.json
    """

    def __init__(self, patterns_dir: str = "./patterns"):
        self.patterns_dir = Path(patterns_dir)
        self.confidence_dir = self.patterns_dir / "confidence"
        self.stats_file = self.confidence_dir / "usage_stats.json"
        self._stats: dict[str, PatternUsageStats] = {}
        self._loaded = False

    def _ensure_loaded(self) -> None:
        """Ensure stats are loaded from disk."""
        if self._loaded:
            return

        self.confidence_dir.mkdir(parents=True, exist_ok=True)

        if self.stats_file.exists():
            try:
                with open(self.stats_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for pattern_id, stats_dict in data.get("patterns", {}).items():
                        self._stats[pattern_id] = PatternUsageStats(
                            pattern_id=pattern_id,
                            **{k: v for k, v in stats_dict.items() if k != "pattern_id"},
                        )
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load usage stats: %s", e)

        self._loaded = True

    def _save(self) -> None:
        """Save stats to disk."""
        self.confidence_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "patterns": {
                pattern_id: {
                    **asdict(stats),
                    "success_rate": stats.success_rate,
                    "application_rate": stats.application_rate,
                    "confidence_score": stats.confidence_score,
                }
                for pattern_id, stats in self._stats.items()
            },
        }

        try:
            with open(self.stats_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        except OSError as e:
            logger.error("Failed to save usage stats: %s", e)

    def _get_or_create_stats(self, pattern_id: str) -> PatternUsageStats:
        """Get or create stats for a pattern."""
        self._ensure_loaded()
        if pattern_id not in self._stats:
            self._stats[pattern_id] = PatternUsageStats(pattern_id=pattern_id)
        return self._stats[pattern_id]

    def record_suggestion(self, pattern_id: str) -> None:
        """Record that a pattern was suggested to the user.

        Call this when a pattern is shown as a potential fix.
        """
        stats = self._get_or_create_stats(pattern_id)
        stats.times_suggested += 1
        stats.last_suggested = datetime.now().isoformat()
        self._save()
        logger.debug("Pattern %s suggested (total: %d)", pattern_id, stats.times_suggested)

    def record_application(
        self,
        pattern_id: str,
        successful: bool = True,
        notes: str | None = None,
    ) -> None:
        """Record that a pattern fix was applied.

        Args:
            pattern_id: The pattern that was applied
            successful: Whether the fix resolved the issue
            notes: Optional feedback notes

        """
        stats = self._get_or_create_stats(pattern_id)
        stats.times_applied += 1
        stats.last_applied = datetime.now().isoformat()

        if successful:
            stats.times_successful += 1
        else:
            stats.times_unsuccessful += 1

        if notes:
            stats.feedback.append(
                {
                    "date": datetime.now().isoformat(),
                    "successful": successful,
                    "notes": notes,
                },
            )

        self._save()
        logger.debug(
            "Pattern %s applied (success=%s, rate=%.0f%%)",
            pattern_id,
            successful,
            stats.success_rate * 100,
        )

    def get_pattern_stats(self, pattern_id: str) -> dict[str, Any]:
        """Get usage statistics for a pattern.

        Returns:
            Dict with usage stats and calculated scores

        """
        stats = self._get_or_create_stats(pattern_id)
        return {
            "pattern_id": pattern_id,
            "times_suggested": stats.times_suggested,
            "times_applied": stats.times_applied,
            "times_successful": stats.times_successful,
            "times_unsuccessful": stats.times_unsuccessful,
            "success_rate": round(stats.success_rate, 2),
            "application_rate": round(stats.application_rate, 2),
            "confidence_score": round(stats.confidence_score, 2),
            "last_suggested": stats.last_suggested,
            "last_applied": stats.last_applied,
            "feedback_count": len(stats.feedback),
        }

    def get_all_stats(self) -> list[dict[str, Any]]:
        """Get stats for all tracked patterns."""
        self._ensure_loaded()
        return [self.get_pattern_stats(pid) for pid in self._stats]

    def get_top_patterns(self, limit: int = 10) -> list[dict[str, Any]]:
        """Get top patterns by confidence score.

        Args:
            limit: Maximum patterns to return

        Returns:
            List of pattern stats, sorted by confidence

        """
        self._ensure_loaded()
        all_stats = self.get_all_stats()
        sorted_stats = sorted(
            all_stats,
            key=lambda s: (s["confidence_score"], s["times_applied"]),
            reverse=True,
        )
        return sorted_stats[:limit]

    def get_stale_patterns(self, days: int = 90) -> list[dict[str, Any]]:
        """Get patterns that haven't been used recently.

        Args:
            days: Number of days to consider stale

        Returns:
            List of stale pattern stats

        """
        self._ensure_loaded()
        stale = []
        cutoff = datetime.now().timestamp() - (days * 86400)

        for pattern_id, stats in self._stats.items():
            last_used = stats.last_applied or stats.last_suggested
            if last_used:
                try:
                    last_ts = datetime.fromisoformat(last_used).timestamp()
                    if last_ts < cutoff:
                        stale.append(self.get_pattern_stats(pattern_id))
                except ValueError:
                    continue

        return stale

    def update_pattern_summary(self) -> bool:
        """Update the patterns_summary.md with confidence scores.

        This adds a confidence section to the generated summary.
        """
        try:
            # Get top patterns
            top_patterns = self.get_top_patterns(5)
            if not top_patterns:
                return False

            # Generate additional markdown
            confidence_section = [
                "## Pattern Confidence (Top 5)",
                "",
            ]

            for p in top_patterns:
                score = p["confidence_score"]
                icon = "🟢" if score >= 0.8 else "🟡" if score >= 0.5 else "🔴"
                confidence_section.append(
                    f"- {icon} **{p['pattern_id']}**: {score:.0%} confidence "
                    f"({p['times_applied']} applied, {p['times_successful']} successful)",
                )

            confidence_section.append("")

            # Read existing summary
            summary_path = Path("./.claude/patterns_summary.md")
            if not summary_path.exists():
                return False

            content = summary_path.read_text(encoding="utf-8")

            # Insert before "How to Use" section
            insert_point = content.find("## How to Use These Patterns")
            if insert_point == -1:
                content += "\n" + "\n".join(confidence_section)
            else:
                content = (
                    content[:insert_point]
                    + "\n".join(confidence_section)
                    + "\n"
                    + content[insert_point:]
                )

            summary_path.write_text(content, encoding="utf-8")
            logger.info("Updated patterns_summary.md with confidence scores")
            return True

        except Exception as e:
            logger.error("Failed to update summary: %s", e)
            return False


def main():
    """CLI entry point for pattern confidence."""
    import argparse

    parser = argparse.ArgumentParser(description="Pattern confidence tracking")
    parser.add_argument("--patterns-dir", default="./patterns", help="Patterns directory")

    subparsers = parser.add_subparsers(dest="command")

    # List command
    list_parser = subparsers.add_parser("list", help="List all pattern stats")
    list_parser.add_argument("--top", type=int, default=10, help="Show top N patterns")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show stats for a pattern")
    stats_parser.add_argument("pattern_id", help="Pattern ID")

    # Record command
    record_parser = subparsers.add_parser("record", help="Record pattern usage")
    record_parser.add_argument("pattern_id", help="Pattern ID")
    record_parser.add_argument("--suggested", action="store_true", help="Record suggestion")
    record_parser.add_argument("--applied", action="store_true", help="Record application")
    record_parser.add_argument("--success", action="store_true", help="Mark as successful")
    record_parser.add_argument("--notes", help="Feedback notes")

    # Stale command
    stale_parser = subparsers.add_parser("stale", help="List stale patterns")
    stale_parser.add_argument("--days", type=int, default=90, help="Days to consider stale")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    tracker = PatternConfidenceTracker(args.patterns_dir)

    if args.command == "list":
        top = tracker.get_top_patterns(args.top)
        if not top:
            print("No pattern usage data recorded yet.")
            return

        print(f"\nTop {len(top)} Patterns by Confidence:\n")
        for i, p in enumerate(top, 1):
            score = p["confidence_score"]
            icon = "🟢" if score >= 0.8 else "🟡" if score >= 0.5 else "🔴"
            print(f"{i}. {icon} {p['pattern_id']}")
            print(f"   Confidence: {score:.0%}")
            print(f"   Applied: {p['times_applied']} times ({p['times_successful']} successful)")
            print(f"   Suggested: {p['times_suggested']} times")
            print()

    elif args.command == "stats":
        stats = tracker.get_pattern_stats(args.pattern_id)
        print(f"\nStats for {args.pattern_id}:\n")
        for key, value in stats.items():
            print(f"  {key}: {value}")

    elif args.command == "record":
        if args.suggested:
            tracker.record_suggestion(args.pattern_id)
            print(f"✓ Recorded suggestion for {args.pattern_id}")

        if args.applied:
            tracker.record_application(
                args.pattern_id,
                successful=args.success,
                notes=args.notes,
            )
            print(f"✓ Recorded application for {args.pattern_id} (success={args.success})")

    elif args.command == "stale":
        stale = tracker.get_stale_patterns(args.days)
        if not stale:
            print(f"No patterns unused in the last {args.days} days.")
            return

        print(f"\nPatterns unused in {args.days}+ days:\n")
        for p in stale:
            print(f"  - {p['pattern_id']} (last used: {p['last_applied'] or p['last_suggested']})")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
