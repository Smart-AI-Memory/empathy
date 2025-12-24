"""
Pattern Summary Generator

Generates a markdown summary of stored patterns for inclusion in CLAUDE.md.
This enables Claude Code sessions to have context about historical patterns.

Usage:
    from empathy_llm_toolkit.pattern_summary import PatternSummaryGenerator

    generator = PatternSummaryGenerator("./patterns")
    summary = generator.generate_markdown()
    generator.write_to_file("./.claude/patterns_summary.md")

CLI:
    python -m empathy_llm_toolkit.pattern_summary --patterns-dir ./patterns --output patterns.md

Author: Empathy Framework Team
Version: 2.1.2
License: Fair Source 0.9
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PatternSummaryGenerator:
    """
    Generates markdown summaries of stored patterns.

    Scans the patterns directory and produces a concise summary
    suitable for inclusion in CLAUDE.md via @import.
    """

    def __init__(self, patterns_dir: str = "./patterns"):
        self.patterns_dir = Path(patterns_dir)
        self._bug_patterns: list[dict[str, Any]] = []
        self._security_decisions: list[dict[str, Any]] = []
        self._tech_debt_history: list[dict[str, Any]] = []

    def load_all_patterns(self) -> None:
        """Load all patterns from storage."""
        self._bug_patterns = self._load_bug_patterns()
        self._security_decisions = self._load_security_decisions()
        self._tech_debt_history = self._load_tech_debt_history()

        logger.info(
            "Patterns loaded: %d bugs, %d security decisions, %d debt snapshots",
            len(self._bug_patterns),
            len(self._security_decisions),
            len(self._tech_debt_history),
        )

    def _load_bug_patterns(self) -> list[dict[str, Any]]:
        """Load bug patterns from debugging directories."""
        patterns = []

        # Check all debugging directories
        for debug_dir in ["debugging", "debugging_demo", "repo_test/debugging"]:
            dir_path = self.patterns_dir / debug_dir
            if not dir_path.exists():
                continue

            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        pattern = json.load(f)
                        pattern["_source_dir"] = debug_dir
                        patterns.append(pattern)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Bug pattern load failed: %s - %s", json_file, e)

        return patterns

    def _load_security_decisions(self) -> list[dict[str, Any]]:
        """Load security team decisions."""
        decisions = []

        # Check all security directories
        for sec_dir in ["security", "security_demo", "repo_test/security"]:
            decisions_file = self.patterns_dir / sec_dir / "team_decisions.json"
            if not decisions_file.exists():
                continue

            try:
                with open(decisions_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for decision in data.get("decisions", []):
                        decision["_source_dir"] = sec_dir
                        decisions.append(decision)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Security decisions load failed: %s - %s", decisions_file, e)

        return decisions

    def _load_tech_debt_history(self) -> list[dict[str, Any]]:
        """Load tech debt history snapshots."""
        snapshots = []

        # Check all tech_debt directories
        for debt_dir in ["tech_debt", "tech_debt_demo", "repo_test/tech_debt"]:
            history_file = self.patterns_dir / debt_dir / "debt_history.json"
            if not history_file.exists():
                continue

            try:
                with open(history_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for snapshot in data.get("snapshots", []):
                        snapshot["_source_dir"] = debt_dir
                        snapshots.append(snapshot)
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("Debt history load failed: %s - %s", history_file, e)

        return snapshots

    def generate_markdown(self) -> str:
        """
        Generate a markdown summary of all patterns.

        Returns:
            Markdown string suitable for CLAUDE.md inclusion
        """
        if not any([self._bug_patterns, self._security_decisions, self._tech_debt_history]):
            self.load_all_patterns()

        lines = [
            "# Pattern Library Summary",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "",
            "This summary is auto-generated from stored patterns.",
            "Use these patterns to inform debugging, security, and code quality decisions.",
            "",
        ]

        # Bug Patterns Section
        lines.extend(self._generate_bug_section())

        # Security Decisions Section
        lines.extend(self._generate_security_section())

        # Tech Debt Section
        lines.extend(self._generate_debt_section())

        # Usage hints
        lines.extend(
            [
                "---",
                "",
                "## How to Use These Patterns",
                "",
                "- **Debugging**: Check if similar bugs have been resolved",
                "- **Security**: Check team decisions for false positives",
                "- **Tech Debt**: Consider debt trajectory when planning refactoring work",
                "",
            ]
        )

        return "\n".join(lines)

    def _generate_bug_section(self) -> list[str]:
        """Generate bug patterns section."""
        lines = [
            f"## Bug Patterns ({len(self._bug_patterns)} stored)",
            "",
        ]

        if not self._bug_patterns:
            lines.append("*No bug patterns stored yet.*")
            lines.append("")
            return lines

        # Group by error type
        by_type: dict[str, list[dict]] = {}
        for bug in self._bug_patterns:
            error_type = bug.get("error_type", "unknown")
            by_type.setdefault(error_type, []).append(bug)

        for error_type, bugs in sorted(by_type.items()):
            lines.append(f"### {error_type} ({len(bugs)} occurrences)")
            lines.append("")

            # Show most recent or notable
            for bug in bugs[:3]:  # Limit to 3 per type
                root_cause = bug.get("root_cause", "Unknown")
                fix = bug.get("fix_applied", "N/A")
                time_mins = bug.get("resolution_time_minutes", 0)
                status = bug.get("status", "unknown")

                lines.append(f"- **{bug.get('bug_id', 'unknown')}** ({status})")
                lines.append(f"  - Root cause: {root_cause}")
                lines.append(f"  - Fix: {fix}")
                if time_mins:
                    lines.append(f"  - Resolution time: {time_mins} min")
                lines.append("")

        return lines

    def _generate_security_section(self) -> list[str]:
        """Generate security decisions section."""
        lines = [
            f"## Security Decisions ({len(self._security_decisions)} stored)",
            "",
        ]

        if not self._security_decisions:
            lines.append("*No security decisions stored yet.*")
            lines.append("")
            return lines

        # Group by decision type
        by_decision: dict[str, list[dict]] = {}
        for decision in self._security_decisions:
            decision_type = decision.get("decision", "unknown")
            by_decision.setdefault(decision_type, []).append(decision)

        for decision_type, decisions in sorted(by_decision.items()):
            lines.append(f"### {decision_type.upper()} ({len(decisions)})")
            lines.append("")

            for d in decisions:
                finding = d.get("finding_hash", "unknown")
                reason = d.get("reason", "N/A")
                decided_by = d.get("decided_by", "unknown")

                lines.append(f"- **{finding}**: {reason}")
                lines.append(f"  - Decided by: {decided_by}")
                lines.append("")

        return lines

    def _generate_debt_section(self) -> list[str]:
        """Generate tech debt section with trajectory analysis."""
        lines = [
            f"## Tech Debt Trajectory ({len(self._tech_debt_history)} snapshots)",
            "",
        ]

        if not self._tech_debt_history:
            lines.append("*No tech debt history stored yet.*")
            lines.append("")
            return lines

        # Sort by date
        sorted_snapshots = sorted(
            self._tech_debt_history, key=lambda s: s.get("date", ""), reverse=True
        )

        # Current state (most recent)
        current = sorted_snapshots[0]
        lines.append(f"### Current State ({current.get('date', 'unknown')[:10]})")
        lines.append("")
        lines.append(f"- Total items: {current.get('total_items', 0)}")

        if by_type := current.get("by_type"):
            type_summary = ", ".join(f"{k}: {v}" for k, v in sorted(by_type.items()))
            lines.append(f"- By type: {type_summary}")

        if by_severity := current.get("by_severity"):
            sev_summary = ", ".join(f"{k}: {v}" for k, v in sorted(by_severity.items()))
            lines.append(f"- By severity: {sev_summary}")

        if hotspots := current.get("hotspots"):
            lines.append(f"- Hotspots: {', '.join(hotspots[:3])}")

        lines.append("")

        # Trajectory analysis
        if len(sorted_snapshots) >= 2:
            oldest = sorted_snapshots[-1]
            current_total = current.get("total_items", 0)
            oldest_total = oldest.get("total_items", 0)

            if current_total < oldest_total:
                trend = "DECREASING"
                change = oldest_total - current_total
            elif current_total > oldest_total:
                trend = "INCREASING"
                change = current_total - oldest_total
            else:
                trend = "STABLE"
                change = 0

            lines.append(f"### Trajectory: {trend}")
            lines.append("")
            lines.append(f"- Change: {change} items over {len(sorted_snapshots)} snapshots")
            lines.append(f"- Oldest snapshot: {oldest_total} items ({oldest.get('date', '')[:10]})")
            lines.append(f"- Current: {current_total} items")
            lines.append("")

        return lines

    def write_to_file(self, output_path: str) -> None:
        """
        Write the markdown summary to a file.

        Args:
            output_path: Path to write the summary
        """
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)

        content = self.generate_markdown()
        output.write_text(content, encoding="utf-8")

        logger.info("Pattern summary written to %s (%d bytes)", output, len(content))


def main():
    """CLI entry point for pattern summary generation."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate pattern summary for CLAUDE.md")
    parser.add_argument(
        "--patterns-dir",
        default="./patterns",
        help="Path to patterns directory (default: ./patterns)",
    )
    parser.add_argument(
        "--output",
        default="./.claude/patterns_summary.md",
        help="Output file path (default: ./.claude/patterns_summary.md)",
    )
    parser.add_argument(
        "--print", action="store_true", help="Print to stdout instead of writing to file"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    generator = PatternSummaryGenerator(args.patterns_dir)
    generator.load_all_patterns()

    if args.print:
        print(generator.generate_markdown())
    else:
        generator.write_to_file(args.output)
        print(f"Pattern summary written to: {args.output}")


if __name__ == "__main__":
    main()
