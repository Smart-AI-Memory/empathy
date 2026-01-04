"""Session Status Assistant

Proactive briefing system that greets developers when they return to an
Empathy-enhanced project, providing a prioritized status report with
actionable items.

Usage:
    from empathy_llm_toolkit.session_status import SessionStatusCollector

    collector = SessionStatusCollector("./patterns")

    # Check if status should be shown
    if collector.should_show():
        status = collector.collect()
        print(collector.format_output(status))
        collector.record_interaction()

CLI:
    python -m empathy_llm_toolkit.session_status
    empathy status [--full] [--json]

Author: Empathy Framework Team
Version: 2.1.5
License: Fair Source 0.9
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Priority weights for different item types
PRIORITY_WEIGHTS = {
    "security_pending": 100,  # P0: Immediate risk
    "bugs_high": 80,  # P1: Runtime failures
    "bugs_investigating": 60,  # P2: Unresolved work
    "tech_debt_increasing": 40,  # P3: Trajectory matters
    "roadmap_unchecked": 30,  # P4: Planned work
    "commits_wip": 20,  # P5: Nice-to-know
}

# Default configuration
DEFAULT_CONFIG = {
    "inactivity_minutes": 60,
    "max_display_items": 5,
    "show_wins": True,
}


@dataclass
class StatusItem:
    """A single item in the status report."""

    category: str
    priority: int
    icon: str
    title: str
    description: str
    action_prompt: str = ""
    details: dict = field(default_factory=dict)

    @property
    def weight(self) -> int:
        """Get priority weight for sorting."""
        return PRIORITY_WEIGHTS.get(self.category, 0)


@dataclass
class SessionStatus:
    """Complete session status report."""

    items: list[StatusItem] = field(default_factory=list)
    wins: list[str] = field(default_factory=list)
    total_attention_items: int = 0
    generated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def add_item(self, item: StatusItem) -> None:
        """Add an item to the status."""
        self.items.append(item)
        self.total_attention_items += 1

    def get_sorted_items(self) -> list[StatusItem]:
        """Get items sorted by priority weight (highest first)."""
        return sorted(self.items, key=lambda x: x.weight, reverse=True)


class SessionStatusCollector:
    """Aggregates project status from all data sources.

    Scans patterns directories, roadmap docs, and git history
    to build a prioritized status report for developers.
    """

    def __init__(
        self,
        patterns_dir: str = "./patterns",
        project_root: str = ".",
        config: dict[str, Any] | None = None,
    ):
        self.patterns_dir = Path(patterns_dir)
        self.project_root = Path(project_root)
        self.empathy_dir = self.project_root / ".empathy"
        self.state_file = self.empathy_dir / "session_state.json"
        self.history_dir = self.empathy_dir / "status_history"

        # Merge config with defaults
        self.config = {**DEFAULT_CONFIG, **(config or {})}

        # Cached state
        self._state: dict[str, Any] | None = None

    def should_show(self) -> bool:
        """Check if status should be shown based on inactivity.

        Returns True if:
        - First interaction after inactivity_minutes of no activity
        - First interaction of a new calendar day
        - No previous state exists (first time)
        """
        state = self._load_state()

        # First time - always show
        if not state.get("last_interaction"):
            return True

        last_interaction = datetime.fromisoformat(state["last_interaction"])
        now = datetime.now()

        # New calendar day
        if last_interaction.date() < now.date():
            logger.debug("New day detected - showing status")
            return True

        # Inactivity threshold
        minutes_inactive = (now - last_interaction).total_seconds() / 60
        threshold = self.config["inactivity_minutes"]

        if minutes_inactive >= threshold:
            logger.debug(
                "Inactivity threshold reached (%.0f min >= %d min)",
                minutes_inactive,
                threshold,
            )
            return True

        return False

    def record_interaction(self) -> None:
        """Update last interaction timestamp."""
        state = self._load_state()
        state["last_interaction"] = datetime.now().isoformat()
        state["interaction_count"] = state.get("interaction_count", 0) + 1
        self._save_state(state)
        logger.debug("Recorded interaction at %s", state["last_interaction"])

    def collect(self) -> SessionStatus:
        """Collect and prioritize status items from all data sources.

        Returns:
            SessionStatus with prioritized items and wins

        """
        status = SessionStatus()

        # Collect from each data source
        self._collect_security_items(status)
        self._collect_bug_items(status)
        self._collect_tech_debt_items(status)
        self._collect_roadmap_items(status)
        self._collect_git_items(status)

        # Detect wins (improvements since last session)
        if self.config["show_wins"]:
            self._detect_wins(status)

        # Save daily snapshot
        self._save_daily_snapshot(status)

        return status

    def _collect_security_items(self, status: SessionStatus) -> None:
        """Collect pending security decisions."""
        security_dirs = ["security", "security_demo", "repo_test/security"]

        pending_count = 0
        pending_items = []

        for sec_dir in security_dirs:
            decisions_file = self.patterns_dir / sec_dir / "team_decisions.json"
            if not decisions_file.exists():
                continue

            try:
                with open(decisions_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for decision in data.get("decisions", []):
                        if decision.get("decision", "").lower() == "pending":
                            pending_count += 1
                            pending_items.append(decision)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load security decisions: %s", e)

        if pending_count > 0:
            first_item = pending_items[0] if pending_items else {}
            finding = first_item.get("finding_hash", "unknown")

            status.add_item(
                StatusItem(
                    category="security_pending",
                    priority=100,
                    icon="🔴",
                    title=f"Security: {pending_count} decision(s) pending review",
                    description=f"Review {finding} finding",
                    action_prompt=f"Review security finding: {finding}. "
                    f"Provide analysis and recommend: ACCEPTED, DEFERRED, or FALSE_POSITIVE.",
                    details={"pending_count": pending_count, "items": pending_items[:3]},
                ),
            )

    def _collect_bug_items(self, status: SessionStatus) -> None:
        """Collect investigating and high-severity bugs."""
        bug_dirs = ["debugging", "debugging_demo", "repo_test/debugging"]

        investigating = []
        high_severity = []

        for bug_dir in bug_dirs:
            dir_path = self.patterns_dir / bug_dir
            if not dir_path.exists():
                continue

            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        bug = json.load(f)
                        bug_status = bug.get("status", "").lower()

                        if bug_status == "investigating":
                            investigating.append(bug)
                        elif bug.get("severity", "").lower() == "high":
                            high_severity.append(bug)

                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Failed to load bug pattern %s: %s", json_file, e)

        # Add high-severity bugs (P1)
        if high_severity:
            first_bug = high_severity[0]
            status.add_item(
                StatusItem(
                    category="bugs_high",
                    priority=80,
                    icon="🔴",
                    title=f"Bugs: {len(high_severity)} high-severity",
                    description=f"Fix {first_bug.get('error_type', '?')} in {first_bug.get('file_path', '?')[:40]}",
                    action_prompt=f"Fix high-severity bug {first_bug.get('bug_id', 'unknown')}: "
                    f"{first_bug.get('error_message', 'No description')}. "
                    f"File: {first_bug.get('file_path', 'unknown')}",
                    details={"count": len(high_severity), "bugs": high_severity[:3]},
                ),
            )

        # Add investigating bugs (P2)
        if investigating:
            first_bug = investigating[0]
            status.add_item(
                StatusItem(
                    category="bugs_investigating",
                    priority=60,
                    icon="🟡",
                    title=f"Bugs: {len(investigating)} investigating",
                    description=f"Resolve {first_bug.get('bug_id', 'unknown')}",
                    action_prompt=f"Continue investigating {first_bug.get('bug_id', '?')}: "
                    f"{first_bug.get('error_message', 'No description')}. "
                    f"Use: empathy patterns resolve {first_bug.get('bug_id', '')} "
                    f"--root-cause '<cause>' --fix '<fix>'",
                    details={"count": len(investigating), "bugs": investigating[:5]},
                ),
            )

    def _collect_tech_debt_items(self, status: SessionStatus) -> None:
        """Collect tech debt trajectory information."""
        debt_dirs = ["tech_debt", "tech_debt_demo", "repo_test/tech_debt"]

        snapshots = []

        for debt_dir in debt_dirs:
            history_file = self.patterns_dir / debt_dir / "debt_history.json"
            if not history_file.exists():
                continue

            try:
                with open(history_file, encoding="utf-8") as f:
                    data = json.load(f)
                    snapshots.extend(data.get("snapshots", []))
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Failed to load tech debt history: %s", e)

        if len(snapshots) < 2:
            return

        # Sort by date and compare recent to older
        sorted_snapshots = sorted(snapshots, key=lambda s: s.get("date", ""), reverse=True)
        current = sorted_snapshots[0]
        previous = sorted_snapshots[1]

        current_total = current.get("total_items", 0)
        previous_total = previous.get("total_items", 0)
        change = current_total - previous_total

        if change > 0:
            # Tech debt increasing - add warning
            status.add_item(
                StatusItem(
                    category="tech_debt_increasing",
                    priority=40,
                    icon="🟡",
                    title=f"Tech Debt: Increasing (+{change} items)",
                    description=f"Total: {current_total} items",
                    action_prompt="Review tech debt trajectory. "
                    f"Total increased from {previous_total} to {current_total}. "
                    "Consider addressing high-priority debt items.",
                    details={
                        "current_total": current_total,
                        "previous_total": previous_total,
                        "change": change,
                        "hotspots": current.get("hotspots", [])[:3],
                    },
                ),
            )
        elif change < 0:
            # Tech debt decreasing - this is a win
            status.wins.append(f"Tech debt decreased by {abs(change)} items")
        else:
            # Stable - just note it
            logger.debug("Tech debt stable at %d items", current_total)

    def _collect_roadmap_items(self, status: SessionStatus) -> None:
        """Collect unchecked items from PLAN_*.md files."""
        docs_dir = self.project_root / "docs"
        if not docs_dir.exists():
            return

        unchecked_tasks = []

        for plan_file in docs_dir.glob("PLAN_*.md"):
            try:
                content = plan_file.read_text(encoding="utf-8")

                # Find unchecked markdown checkboxes
                unchecked = re.findall(r"- \[ \] (.+?)(?:\n|$)", content)
                for task in unchecked[:5]:  # Limit per file
                    unchecked_tasks.append(
                        {
                            "task": task.strip(),
                            "file": plan_file.name,
                        },
                    )
            except OSError as e:
                logger.warning("Failed to read plan file %s: %s", plan_file, e)

        if unchecked_tasks:
            first_task = unchecked_tasks[0]
            status.add_item(
                StatusItem(
                    category="roadmap_unchecked",
                    priority=30,
                    icon="🔵",
                    title=f"Roadmap: {len(unchecked_tasks)} unchecked items",
                    description=f"Continue: {first_task['task'][:50]}...",
                    action_prompt=f"Continue roadmap item from {first_task['file']}: "
                    f"{first_task['task']}",
                    details={"count": len(unchecked_tasks), "tasks": unchecked_tasks[:5]},
                ),
            )

    def _collect_git_items(self, status: SessionStatus) -> None:
        """Collect WIP/TODO commits from git log."""
        try:
            result = subprocess.run(
                ["git", "log", "-10", "--format=%h|%s", "--since=7.days"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
                cwd=self.project_root,
            )

            if result.returncode != 0:
                return

            wip_commits = []
            todo_keywords = ["wip", "todo", "fixme", "hack", "temp", "xxx"]

            for line in result.stdout.strip().split("\n"):
                if not line or "|" not in line:
                    continue

                commit_hash, message = line.split("|", 1)
                message_lower = message.lower()

                if any(kw in message_lower for kw in todo_keywords):
                    wip_commits.append(
                        {
                            "hash": commit_hash,
                            "message": message,
                        },
                    )

            if wip_commits:
                first_commit = wip_commits[0]
                status.add_item(
                    StatusItem(
                        category="commits_wip",
                        priority=20,
                        icon="⚪",
                        title=f"Commits: {len(wip_commits)} WIP/TODO",
                        description=f"Follow up: {first_commit['message'][:40]}...",
                        action_prompt=f"Review WIP commit {first_commit['hash']}: "
                        f"{first_commit['message']}. "
                        "This commit may need follow-up work.",
                        details={"count": len(wip_commits), "commits": wip_commits[:5]},
                    ),
                )

        except Exception as e:
            logger.debug("Git log check failed: %s", e)

    def _detect_wins(self, status: SessionStatus) -> None:
        """Detect improvements since last session."""
        previous_snapshot = self._load_previous_snapshot()
        if not previous_snapshot:
            return

        # Compare bug counts
        prev_investigating = previous_snapshot.get("bugs_investigating", 0)
        curr_investigating = sum(
            1 for item in status.items if item.category == "bugs_investigating"
        )
        # Get actual count from details
        for item in status.items:
            if item.category == "bugs_investigating":
                curr_investigating = item.details.get("count", 0)
                break

        resolved = prev_investigating - curr_investigating
        if resolved > 0:
            status.wins.append(f"{resolved} bug(s) resolved since last session")

    def _load_state(self) -> dict[str, Any]:
        """Load session state from disk."""
        if self._state is not None:
            return self._state

        if self.state_file.exists():
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    self._state = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._state = {}
        else:
            self._state = {}

        return self._state

    def _save_state(self, state: dict[str, Any]) -> None:
        """Save session state to disk."""
        self.empathy_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(self.state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, default=str)
            self._state = state
        except OSError as e:
            logger.error("Failed to save session state: %s", e)

    def _save_daily_snapshot(self, status: SessionStatus) -> None:
        """Save daily status snapshot for history."""
        self.history_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime("%Y-%m-%d")
        snapshot_file = self.history_dir / f"{today}.json"

        snapshot = {
            "date": today,
            "generated_at": status.generated_at,
            "total_attention_items": status.total_attention_items,
            "bugs_investigating": sum(
                item.details.get("count", 0)
                for item in status.items
                if item.category == "bugs_investigating"
            ),
            "security_pending": sum(
                item.details.get("pending_count", 0)
                for item in status.items
                if item.category == "security_pending"
            ),
            "wins": status.wins,
            "categories": [item.category for item in status.items],
        }

        try:
            with open(snapshot_file, "w", encoding="utf-8") as f:
                json.dump(snapshot, f, indent=2, default=str)
        except OSError as e:
            logger.warning("Failed to save daily snapshot: %s", e)

    def _load_previous_snapshot(self) -> dict[str, Any] | None:
        """Load the most recent previous snapshot."""
        if not self.history_dir.exists():
            return None

        snapshots = sorted(self.history_dir.glob("*.json"), reverse=True)

        # Skip today's snapshot, get yesterday's
        today = datetime.now().strftime("%Y-%m-%d")

        for snapshot_file in snapshots:
            if snapshot_file.stem != today:
                try:
                    with open(snapshot_file, encoding="utf-8") as f:
                        data = json.load(f)
                        return dict(data) if isinstance(data, dict) else None
                except (json.JSONDecodeError, OSError):
                    continue

        return None

    def format_output(
        self,
        status: SessionStatus,
        max_items: int | None = None,
    ) -> str:
        """Format status for terminal output.

        Args:
            status: The SessionStatus to format
            max_items: Maximum items to display (default from config)

        Returns:
            Formatted markdown string

        """
        max_items = max_items or self.config["max_display_items"]
        sorted_items = status.get_sorted_items()

        lines = [
            f"📊 Project Status ({status.total_attention_items} items need attention)",
            "",
        ]

        # Show wins first if any
        if status.wins:
            lines.append("🎉 Wins since last session:")
            for win in status.wins:
                lines.append(f"   • {win}")
            lines.append("")

        # Group items by severity for display
        for item in sorted_items[:max_items]:
            lines.append(f"{item.icon} {item.title}")
            lines.append(f"   → {item.description}")
            lines.append("")

        # Add selection footer
        if sorted_items:
            lines.append("━" * 40)
            selection_items = []
            for i, item in enumerate(sorted_items[:3], 1):
                # Create short label
                if item.category == "security_pending":
                    label = "Review security"
                elif item.category.startswith("bugs"):
                    label = "Fix bug"
                elif item.category == "tech_debt_increasing":
                    label = "Address debt"
                elif item.category == "roadmap_unchecked":
                    label = "Continue roadmap"
                else:
                    label = "Follow up"
                selection_items.append(f"[{i}] {label}")

            selection_items.append(f"[{len(sorted_items[:3]) + 1}] See full status")
            lines.append("  ".join(selection_items))

        return "\n".join(lines)

    def format_json(self, status: SessionStatus) -> str:
        """Format status as JSON."""
        data = {
            "generated_at": status.generated_at,
            "total_attention_items": status.total_attention_items,
            "wins": status.wins,
            "items": [
                {
                    "category": item.category,
                    "priority": item.priority,
                    "icon": item.icon,
                    "title": item.title,
                    "description": item.description,
                    "action_prompt": item.action_prompt,
                    "details": item.details,
                }
                for item in status.get_sorted_items()
            ],
        }
        return json.dumps(data, indent=2, default=str)

    def get_action_prompt(self, status: SessionStatus, selection: int) -> str | None:
        """Get the action prompt for a selected item.

        Args:
            status: The SessionStatus
            selection: 1-indexed selection number

        Returns:
            Action prompt string, or None if invalid selection

        """
        sorted_items = status.get_sorted_items()

        if selection < 1 or selection > len(sorted_items):
            return None

        item = sorted_items[selection - 1]
        return item.action_prompt


def main():
    """CLI entry point for session status."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Session status assistant for Empathy Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show status (if enough time has passed)
  python -m empathy_llm_toolkit.session_status

  # Force show status
  python -m empathy_llm_toolkit.session_status --force

  # Show full status as JSON
  python -m empathy_llm_toolkit.session_status --full --json

  # Select an item to get action prompt
  python -m empathy_llm_toolkit.session_status --select 1
        """,
    )

    parser.add_argument(
        "--patterns-dir",
        default="./patterns",
        help="Path to patterns directory",
    )
    parser.add_argument(
        "--project-root",
        default=".",
        help="Project root directory",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force show status regardless of inactivity",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Show all items (no limit)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--select",
        type=int,
        help="Select an item to get its action prompt",
    )
    parser.add_argument(
        "--inactivity",
        type=int,
        default=60,
        help="Inactivity threshold in minutes (default: 60)",
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    # Create collector
    config = {"inactivity_minutes": args.inactivity}
    collector = SessionStatusCollector(
        patterns_dir=args.patterns_dir,
        project_root=args.project_root,
        config=config,
    )

    # Check if should show (unless forced)
    if not args.force and not collector.should_show():
        print("No status update needed (recent activity detected).")
        print("Use --force to show status anyway.")
        return

    # Collect status
    status = collector.collect()

    # Handle selection
    if args.select:
        prompt = collector.get_action_prompt(status, args.select)
        if prompt:
            print(f"\nAction prompt for selection {args.select}:\n")
            print(prompt)
        else:
            print(f"Invalid selection: {args.select}")
        return

    # Output
    if args.json:
        print(collector.format_json(status))
    else:
        max_items = None if args.full else 5
        print()
        print(collector.format_output(status, max_items=max_items))
        print()

    # Record interaction
    collector.record_interaction()


if __name__ == "__main__":
    main()
