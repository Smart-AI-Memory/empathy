"""Project Index Reports - Generate actionable reports from index data.

Reports for project management, sprint planning, and architecture decisions.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from datetime import datetime
from typing import Any

from .models import FileRecord, ProjectSummary, TestRequirement


class ReportGenerator:
    """Generates reports from project index data.

    Reports are designed for:
    - Human consumption (markdown)
    - Agent/crew consumption (structured data)
    - Dashboard display (summary metrics)
    """

    def __init__(self, summary: ProjectSummary, records: list[FileRecord]):
        self.summary = summary
        self.records = records
        self._source_records = [r for r in records if r.category.value == "source"]

    # ===== Test Gap Reports =====

    def test_gap_report(self) -> dict[str, Any]:
        """Generate comprehensive test gap report.

        Used by test-gen workflow and agents.
        """
        needing_tests = [
            r
            for r in self._source_records
            if r.test_requirement == TestRequirement.REQUIRED and not r.tests_exist
        ]

        # Prioritize by impact
        prioritized = sorted(needing_tests, key=lambda r: -r.impact_score)

        return {
            "report_type": "test_gap",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_files_needing_tests": len(needing_tests),
                "total_loc_untested": sum(r.lines_of_code for r in needing_tests),
                "high_impact_untested": len([r for r in needing_tests if r.impact_score >= 5.0]),
            },
            "priority_files": [
                {
                    "path": r.path,
                    "impact_score": r.impact_score,
                    "lines_of_code": r.lines_of_code,
                    "imported_by_count": r.imported_by_count,
                    "reason": f"High impact ({r.impact_score:.1f}), {r.lines_of_code} LOC",
                }
                for r in prioritized[:20]
            ],
            "by_directory": self._group_by_directory(needing_tests),
            "recommendations": self._test_recommendations(needing_tests),
        }

    def _test_recommendations(self, needing_tests: list[FileRecord]) -> list[str]:
        """Generate test recommendations."""
        recommendations = []

        high_impact = [r for r in needing_tests if r.impact_score >= 5.0]
        if high_impact:
            recommendations.append(
                f"PRIORITY: {len(high_impact)} high-impact files need tests. "
                f"Start with: {', '.join(r.name for r in high_impact[:3])}",
            )

        if len(needing_tests) > 50:
            recommendations.append(
                f"Consider batch test generation - {len(needing_tests)} files need tests",
            )

        return recommendations

    # ===== Staleness Reports =====

    def staleness_report(self) -> dict[str, Any]:
        """Generate test staleness report.

        Identifies files where code changed but tests didn't update.
        """
        stale = [r for r in self._source_records if r.is_stale]
        stale_sorted = sorted(stale, key=lambda r: -r.staleness_days)

        return {
            "report_type": "staleness",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "stale_file_count": len(stale),
                "avg_staleness_days": (
                    sum(r.staleness_days for r in stale) / len(stale) if stale else 0
                ),
                "max_staleness_days": max((r.staleness_days for r in stale), default=0),
            },
            "stale_files": [
                {
                    "path": r.path,
                    "staleness_days": r.staleness_days,
                    "last_modified": r.last_modified.isoformat() if r.last_modified else None,
                    "test_file": r.test_file_path,
                    "tests_last_modified": (
                        r.tests_last_modified.isoformat() if r.tests_last_modified else None
                    ),
                }
                for r in stale_sorted[:20]
            ],
            "recommendations": [
                f"Update tests for: {r.path} ({r.staleness_days} days stale)"
                for r in stale_sorted[:5]
            ],
        }

    # ===== Coverage Reports =====

    def coverage_report(self) -> dict[str, Any]:
        """Generate coverage analysis report."""
        with_coverage = [r for r in self._source_records if r.coverage_percent > 0]
        low_coverage = [r for r in with_coverage if r.coverage_percent < 50]

        return {
            "report_type": "coverage",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "avg_coverage": self.summary.test_coverage_avg,
                "files_with_data": len(with_coverage),
                "files_below_50pct": len(low_coverage),
            },
            "low_coverage_files": [
                {
                    "path": r.path,
                    "coverage_percent": r.coverage_percent,
                    "impact_score": r.impact_score,
                }
                for r in sorted(low_coverage, key=lambda r: r.coverage_percent)[:20]
            ],
            "coverage_by_directory": self._coverage_by_directory(),
        }

    def _coverage_by_directory(self) -> dict[str, float]:
        """Calculate average coverage by directory."""
        dir_coverage: dict[str, list[float]] = {}

        for r in self._source_records:
            if r.coverage_percent > 0:
                parts = r.path.split("/")
                dir_name = parts[0] if len(parts) > 1 else "."
                if dir_name not in dir_coverage:
                    dir_coverage[dir_name] = []
                dir_coverage[dir_name].append(r.coverage_percent)

        return {
            dir_name: sum(coverages) / len(coverages)
            for dir_name, coverages in dir_coverage.items()
        }

    # ===== Project Health Report =====

    def health_report(self) -> dict[str, Any]:
        """Generate overall project health report.

        Comprehensive view for project managers and architects.
        """
        health_score = self._calculate_health_score()

        return {
            "report_type": "health",
            "generated_at": datetime.now().isoformat(),
            "health_score": health_score,
            "health_grade": self._health_grade(health_score),
            "summary": {
                "total_files": self.summary.total_files,
                "source_files": self.summary.source_files,
                "test_files": self.summary.test_files,
                "test_coverage_avg": self.summary.test_coverage_avg,
                "test_to_code_ratio": self.summary.test_to_code_ratio,
                "stale_file_count": self.summary.stale_file_count,
                "files_needing_attention": self.summary.files_needing_attention,
            },
            "strengths": self._identify_strengths(),
            "concerns": self._identify_concerns(),
            "action_items": self._generate_action_items(),
        }

    def _calculate_health_score(self) -> float:
        """Calculate overall health score (0-100)."""
        score = 50.0  # Base score

        # Coverage bonus/penalty (up to +/- 25 points)
        if self.summary.test_coverage_avg >= 80:
            score += 25
        elif self.summary.test_coverage_avg >= 60:
            score += 15
        elif self.summary.test_coverage_avg >= 40:
            score += 5
        elif self.summary.test_coverage_avg < 20:
            score -= 15

        # Test existence bonus/penalty (up to +/- 15 points)
        if self.summary.files_requiring_tests > 0:
            test_ratio = self.summary.files_with_tests / self.summary.files_requiring_tests
            score += (test_ratio - 0.5) * 30  # 0% = -15, 50% = 0, 100% = +15

        # Staleness penalty (up to -10 points)
        if self.summary.source_files > 0:
            stale_ratio = self.summary.stale_file_count / self.summary.source_files
            score -= stale_ratio * 20

        # Documentation bonus (up to +10 points)
        if self.summary.files_with_docstrings_pct >= 80:
            score += 10
        elif self.summary.files_with_docstrings_pct >= 50:
            score += 5

        return max(0, min(100, score))

    def _health_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90:
            return "A"
        if score >= 80:
            return "B"
        if score >= 70:
            return "C"
        if score >= 60:
            return "D"
        return "F"

    def _identify_strengths(self) -> list[str]:
        """Identify project strengths."""
        strengths = []

        if self.summary.test_coverage_avg >= 70:
            strengths.append(f"Good test coverage ({self.summary.test_coverage_avg:.1f}%)")

        if self.summary.files_with_docstrings_pct >= 70:
            strengths.append(
                f"Well documented ({self.summary.files_with_docstrings_pct:.1f}% with docstrings)",
            )

        if self.summary.files_with_type_hints_pct >= 70:
            strengths.append(
                f"Strong typing ({self.summary.files_with_type_hints_pct:.1f}% with type hints)",
            )

        if self.summary.stale_file_count == 0:
            strengths.append("All tests are up to date")

        return strengths

    def _identify_concerns(self) -> list[str]:
        """Identify project concerns."""
        concerns = []

        if self.summary.test_coverage_avg < 50:
            concerns.append(f"Low test coverage ({self.summary.test_coverage_avg:.1f}%)")

        if self.summary.files_without_tests > 10:
            concerns.append(f"{self.summary.files_without_tests} source files without tests")

        if self.summary.stale_file_count > 5:
            concerns.append(f"{self.summary.stale_file_count} files have stale tests")

        if self.summary.critical_untested_files:
            concerns.append(
                f"{len(self.summary.critical_untested_files)} high-impact files lack tests",
            )

        return concerns

    def _generate_action_items(self) -> list[dict[str, Any]]:
        """Generate prioritized action items."""
        items = []

        # Critical untested files
        for path in self.summary.critical_untested_files[:3]:
            items.append(
                {
                    "priority": "high",
                    "action": f"Add tests for {path}",
                    "reason": "High-impact file without tests",
                },
            )

        # Stale tests
        for path in self.summary.most_stale_files[:3]:
            items.append(
                {
                    "priority": "medium",
                    "action": f"Update tests for {path}",
                    "reason": "Tests are stale",
                },
            )

        return items

    # ===== Sprint Planning Report =====

    def sprint_planning_report(self, sprint_capacity: int = 10) -> dict[str, Any]:
        """Generate sprint planning report.

        Suggests files to address based on priority and capacity.
        """
        attention_files = [r for r in self._source_records if r.needs_attention]
        prioritized = sorted(attention_files, key=lambda r: -r.impact_score)

        # Select files up to sprint capacity
        sprint_files = prioritized[:sprint_capacity]

        return {
            "report_type": "sprint_planning",
            "generated_at": datetime.now().isoformat(),
            "sprint_capacity": sprint_capacity,
            "suggested_work": [
                {
                    "path": r.path,
                    "impact_score": r.impact_score,
                    "reasons": r.attention_reasons,
                    "estimated_effort": self._estimate_effort(r),
                }
                for r in sprint_files
            ],
            "backlog": [
                {"path": r.path, "reasons": r.attention_reasons}
                for r in prioritized[sprint_capacity : sprint_capacity + 10]
            ],
            "metrics_to_track": [
                "Test coverage change",
                "Files needing attention (before/after)",
                "Staleness reduction",
            ],
        }

    def _estimate_effort(self, record: FileRecord) -> str:
        """Estimate effort to address file."""
        loc = record.lines_of_code

        if not record.tests_exist:
            if loc < 50:
                return "small (1-2 hours)"
            if loc < 200:
                return "medium (2-4 hours)"
            return "large (4+ hours)"
        if record.is_stale:
            return "small (update existing tests)"
        return "varies"

    # ===== Markdown Reports =====

    def to_markdown(self, report_type: str = "health") -> str:
        """Generate markdown formatted report.

        For human consumption or documentation.
        """
        if report_type == "health":
            return self._health_markdown()
        if report_type == "test_gap":
            return self._test_gap_markdown()
        if report_type == "staleness":
            return self._staleness_markdown()
        return self._health_markdown()

    def _health_markdown(self) -> str:
        """Generate health report in markdown."""
        report = self.health_report()

        lines = [
            "# Project Health Report",
            "",
            f"**Generated:** {report['generated_at']}",
            f"**Health Score:** {report['health_score']:.1f}/100 ({report['health_grade']})",
            "",
            "## Summary",
            "",
            f"- **Total Files:** {report['summary']['total_files']}",
            f"- **Source Files:** {report['summary']['source_files']}",
            f"- **Test Files:** {report['summary']['test_files']}",
            f"- **Average Coverage:** {report['summary']['test_coverage_avg']:.1f}%",
            f"- **Files Needing Attention:** {report['summary']['files_needing_attention']}",
            "",
        ]

        if report["strengths"]:
            lines.extend(["## Strengths", ""])
            for strength in report["strengths"]:
                lines.append(f"- {strength}")
            lines.append("")

        if report["concerns"]:
            lines.extend(["## Concerns", ""])
            for concern in report["concerns"]:
                lines.append(f"- {concern}")
            lines.append("")

        if report["action_items"]:
            lines.extend(["## Action Items", ""])
            for item in report["action_items"]:
                lines.append(f"- [{item['priority'].upper()}] {item['action']}")
            lines.append("")

        return "\n".join(lines)

    def _test_gap_markdown(self) -> str:
        """Generate test gap report in markdown."""
        report = self.test_gap_report()

        lines = [
            "# Test Gap Report",
            "",
            f"**Generated:** {report['generated_at']}",
            "",
            "## Summary",
            "",
            f"- **Files Needing Tests:** {report['summary']['total_files_needing_tests']}",
            f"- **Lines of Code Untested:** {report['summary']['total_loc_untested']}",
            f"- **High Impact Untested:** {report['summary']['high_impact_untested']}",
            "",
            "## Priority Files",
            "",
        ]

        for i, f in enumerate(report["priority_files"][:10], 1):
            lines.append(f"{i}. `{f['path']}` - {f['reason']}")

        lines.append("")

        return "\n".join(lines)

    def _staleness_markdown(self) -> str:
        """Generate staleness report in markdown."""
        report = self.staleness_report()

        lines = [
            "# Test Staleness Report",
            "",
            f"**Generated:** {report['generated_at']}",
            "",
            "## Summary",
            "",
            f"- **Stale Files:** {report['summary']['stale_file_count']}",
            f"- **Average Staleness:** {report['summary']['avg_staleness_days']:.1f} days",
            f"- **Maximum Staleness:** {report['summary']['max_staleness_days']} days",
            "",
            "## Stale Files",
            "",
        ]

        for f in report["stale_files"][:10]:
            lines.append(f"- `{f['path']}` - {f['staleness_days']} days stale")

        lines.append("")

        return "\n".join(lines)

    # ===== Utility =====

    def _group_by_directory(self, records: list[FileRecord]) -> dict[str, int]:
        """Group records by top-level directory."""
        counts: dict[str, int] = {}
        for r in records:
            parts = r.path.split("/")
            dir_name = parts[0] if len(parts) > 1 else "."
            counts[dir_name] = counts.get(dir_name, 0) + 1
        return counts
