"""Tech Debt Tracking Wizard (Level 4)

Tracks technical debt over time and predicts when it will become critical.
Demonstrates Level 4 Anticipatory Empathy: predicts future problems
before they become urgent.

"At current trajectory, your tech debt will double in 90 days."

Key capabilities enabled by persistent memory:
- Historical debt tracking across sessions
- Trajectory analysis and prediction
- Hotspot identification over time
- Team patterns (who adds debt, who pays it down)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


@dataclass
class DebtItem:
    """A single technical debt item"""

    item_id: str
    file_path: str
    line_number: int
    debt_type: str  # TODO, fixme, hack, temporary, deprecated
    content: str
    severity: str  # low, medium, high, critical
    date_found: str
    age_days: int = 0


@dataclass
class DebtSnapshot:
    """A point-in-time snapshot of technical debt"""

    date: str
    total_items: int
    by_type: dict[str, int] = field(default_factory=dict)
    by_severity: dict[str, int] = field(default_factory=dict)
    by_file: dict[str, int] = field(default_factory=dict)
    hotspots: list[str] = field(default_factory=list)


@dataclass
class DebtTrajectory:
    """Trajectory analysis of technical debt over time"""

    current_total: int
    previous_total: int
    change_percent: float
    trend: str  # decreasing, stable, increasing, exploding
    projection_30_days: int
    projection_90_days: int
    critical_threshold_days: int | None  # Days until critical if continuing


class TechDebtWizard(BaseWizard):
    """Tech Debt Tracking Wizard - Level 4 Anticipatory

    What's now possible that wasn't before:

    WITHOUT PERSISTENT MEMORY (Before):
    - Debt count is just a number (no context)
    - No visibility into trends over time
    - Surprises when debt becomes unmanageable
    - No data to justify cleanup time

    WITH PERSISTENT MEMORY (After):
    - Track debt trajectory over months
    - Predict when debt will become critical
    - Identify hotspots that accumulate debt
    - Justify cleanup with historical trends

    Example:
        >>> wizard = TechDebtWizard()
        >>> result = await wizard.analyze({
        ...     "project_path": ".",
        ...     "track_history": True
        ... })
        >>> print(result["trajectory"]["projection_90_days"])
        # Shows predicted debt count in 90 days

    """

    @property
    def name(self) -> str:
        return "Tech Debt Wizard"

    @property
    def level(self) -> int:
        return 4  # Anticipatory

    def __init__(self, pattern_storage_path: str = "./patterns/tech_debt"):
        """Initialize the tech debt tracking wizard.

        Args:
            pattern_storage_path: Path to git-based pattern storage for history

        """
        super().__init__()
        self.pattern_storage_path = Path(pattern_storage_path)
        self.pattern_storage_path.mkdir(parents=True, exist_ok=True)

        # Debt detection patterns
        self.debt_patterns = {
            "todo": [
                r"#\s*TODO[:\s]",
                r"//\s*TODO[:\s]",
                r"/\*\s*TODO",
                r"<!--\s*TODO",
            ],
            "fixme": [
                r"#\s*FIXME[:\s]",
                r"//\s*FIXME[:\s]",
                r"/\*\s*FIXME",
            ],
            "hack": [
                r"#\s*HACK[:\s]",
                r"//\s*HACK[:\s]",
                r"/\*\s*HACK",
                r"#\s*XXX[:\s]",
                r"//\s*XXX[:\s]",
            ],
            "temporary": [
                r"#\s*TEMP[:\s]",
                r"//\s*TEMP[:\s]",
                r"temporary",
                r"workaround",
            ],
            "deprecated": [
                r"@deprecated",
                r"#\s*DEPRECATED",
                r"//\s*DEPRECATED",
            ],
        }

        # Severity keywords
        self.severity_indicators = {
            "critical": ["urgent", "critical", "breaking", "security", "must fix"],
            "high": ["important", "asap", "soon", "refactor needed"],
            "medium": ["should", "consider", "improve"],
            "low": ["nice to have", "someday", "maybe", "cleanup"],
        }

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze technical debt with trajectory tracking.

        Context expects:
            - project_path: Path to the project
            - track_history: Enable historical tracking (default True)
            - exclude_patterns: Patterns to exclude (default: tests, node_modules, etc.)

        Returns:
            Analysis with:
            - current_debt: Current debt snapshot
            - trajectory: Historical trajectory analysis
            - hotspots: Files with most debt
            - predictions: Level 4 predictions
            - recommendations: Actionable steps

        """
        project_path = Path(context.get("project_path", "."))
        track_history = context.get("track_history", True)
        exclude_patterns = context.get(
            "exclude_patterns",
            ["node_modules", "venv", ".git", "__pycache__", "dist", "build", "test"],
        )

        # Step 1: Scan for current debt
        debt_items = await self._scan_for_debt(project_path, exclude_patterns)

        # Step 2: Create current snapshot
        current_snapshot = self._create_snapshot(debt_items)

        # Step 3: Load historical data and calculate trajectory
        trajectory = None
        history = []

        if track_history:
            history = self._load_history()
            trajectory = self._calculate_trajectory(current_snapshot, history)

            # Store current snapshot for future tracking
            self._store_snapshot(current_snapshot)

        # Step 4: Identify hotspots
        hotspots = self._identify_hotspots(debt_items)

        # Step 5: Generate predictions (Level 4)
        predictions = self._generate_predictions(current_snapshot, trajectory, hotspots, history)

        # Step 6: Generate recommendations
        recommendations = self._generate_recommendations(current_snapshot, trajectory, hotspots)

        return {
            "current_debt": {
                "total_items": current_snapshot.total_items,
                "by_type": current_snapshot.by_type,
                "by_severity": current_snapshot.by_severity,
                "scan_date": current_snapshot.date,
            },
            "debt_items": [
                {
                    "file": d.file_path,
                    "line": d.line_number,
                    "type": d.debt_type,
                    "content": d.content[:100],  # Truncate
                    "severity": d.severity,
                    "age_days": d.age_days,
                }
                for d in debt_items[:20]  # Top 20
            ],
            "hotspots": hotspots,
            "trajectory": (
                {
                    "current_total": trajectory.current_total,
                    "previous_total": trajectory.previous_total,
                    "change_percent": trajectory.change_percent,
                    "trend": trajectory.trend,
                    "projection_30_days": trajectory.projection_30_days,
                    "projection_90_days": trajectory.projection_90_days,
                    "days_until_critical": trajectory.critical_threshold_days,
                }
                if trajectory
                else None
            ),
            "history_available": len(history) > 0,
            "history_snapshots": len(history),
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85 if trajectory else 0.5,
            "memory_benefit": self._calculate_memory_benefit(history, trajectory),
        }

    async def _scan_for_debt(
        self,
        project_path: Path,
        exclude_patterns: list[str],
    ) -> list[DebtItem]:
        """Scan project for technical debt markers"""
        debt_items = []

        # File extensions to scan
        extensions = [
            "*.py",
            "*.js",
            "*.ts",
            "*.tsx",
            "*.jsx",
            "*.java",
            "*.go",
            "*.rb",
            "*.rs",
            "*.cpp",
            "*.c",
            "*.h",
        ]

        for ext in extensions:
            for file_path in project_path.rglob(ext):
                # Skip excluded patterns
                if any(exclude in str(file_path) for exclude in exclude_patterns):
                    continue

                try:
                    debt_items.extend(self._scan_file(file_path))
                except (OSError, UnicodeDecodeError) as e:
                    logger.debug(f"Could not scan {file_path}: {e}")
                    continue

        return debt_items

    def _scan_file(self, file_path: Path) -> list[DebtItem]:
        """Scan a single file for debt markers"""
        items = []

        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            for debt_type, patterns in self.debt_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        item = DebtItem(
                            item_id=f"{file_path}:{line_num}",
                            file_path=str(file_path),
                            line_number=line_num,
                            debt_type=debt_type,
                            content=line.strip(),
                            severity=self._assess_severity(line),
                            date_found=datetime.now().isoformat(),
                        )
                        items.append(item)
                        break  # Only count once per line

        return items

    def _assess_severity(self, content: str) -> str:
        """Assess severity of a debt item based on keywords"""
        content_lower = content.lower()

        for severity, keywords in self.severity_indicators.items():
            if any(keyword in content_lower for keyword in keywords):
                return severity

        return "medium"  # Default

    def _create_snapshot(self, debt_items: list[DebtItem]) -> DebtSnapshot:
        """Create a point-in-time snapshot of debt"""
        by_type: dict[str, int] = {}
        by_severity: dict[str, int] = {}
        by_file: dict[str, int] = {}

        for item in debt_items:
            by_type[item.debt_type] = by_type.get(item.debt_type, 0) + 1
            by_severity[item.severity] = by_severity.get(item.severity, 0) + 1

            # Normalize file path (handle both absolute and relative)
            try:
                file_path = Path(item.file_path)
                if file_path.is_absolute():
                    file_key = str(file_path.relative_to(Path.cwd()))
                else:
                    file_key = str(file_path)
            except ValueError:
                # Path not relative to cwd, use as-is
                file_key = str(item.file_path)
            by_file[file_key] = by_file.get(file_key, 0) + 1

        # Identify top hotspots
        hotspots = sorted(by_file.items(), key=lambda x: x[1], reverse=True)[:5]

        return DebtSnapshot(
            date=datetime.now().isoformat(),
            total_items=len(debt_items),
            by_type=by_type,
            by_severity=by_severity,
            by_file=by_file,
            hotspots=[h[0] for h in hotspots],
        )

    def _load_history(self) -> list[DebtSnapshot]:
        """Load historical snapshots from pattern storage"""
        history = []
        history_file = self.pattern_storage_path / "debt_history.json"

        if history_file.exists():
            try:
                with open(history_file, encoding="utf-8") as f:
                    data = json.load(f)

                for snapshot_data in data.get("snapshots", []):
                    history.append(
                        DebtSnapshot(
                            date=snapshot_data["date"],
                            total_items=snapshot_data["total_items"],
                            by_type=snapshot_data.get("by_type", {}),
                            by_severity=snapshot_data.get("by_severity", {}),
                            by_file=snapshot_data.get("by_file", {}),
                            hotspots=snapshot_data.get("hotspots", []),
                        ),
                    )
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not load debt history: {e}")

        return history

    def _store_snapshot(self, snapshot: DebtSnapshot) -> None:
        """Store snapshot to history"""
        history_file = self.pattern_storage_path / "debt_history.json"

        # Load existing history
        history_data: dict[str, list[dict]] = {"snapshots": []}
        if history_file.exists():
            try:
                with open(history_file, encoding="utf-8") as f:
                    history_data = json.load(f)
            except json.JSONDecodeError:
                pass

        # Add new snapshot
        history_data["snapshots"].append(
            {
                "date": snapshot.date,
                "total_items": snapshot.total_items,
                "by_type": snapshot.by_type,
                "by_severity": snapshot.by_severity,
                "by_file": snapshot.by_file,
                "hotspots": snapshot.hotspots,
            },
        )

        # Keep last 100 snapshots
        history_data["snapshots"] = history_data["snapshots"][-100:]

        # Store
        try:
            with open(history_file, "w", encoding="utf-8") as f:
                json.dump(history_data, f, indent=2)
        except OSError as e:
            logger.warning(f"Could not store debt snapshot: {e}")

    def _calculate_trajectory(
        self,
        current: DebtSnapshot,
        history: list[DebtSnapshot],
    ) -> DebtTrajectory:
        """Calculate debt trajectory from historical data"""
        if not history:
            # No history - can't calculate trajectory
            return DebtTrajectory(
                current_total=current.total_items,
                previous_total=current.total_items,
                change_percent=0.0,
                trend="unknown",
                projection_30_days=current.total_items,
                projection_90_days=current.total_items,
                critical_threshold_days=None,
            )

        # Get comparison point (30 days ago if available, otherwise earliest)
        comparison_snapshot = None
        thirty_days_ago = datetime.now() - timedelta(days=30)

        for snapshot in reversed(history):
            snapshot_date = datetime.fromisoformat(snapshot.date.replace("Z", ""))
            if snapshot_date <= thirty_days_ago:
                comparison_snapshot = snapshot
                break

        if not comparison_snapshot and history:
            comparison_snapshot = history[0]  # Use earliest available

        previous_total = (
            comparison_snapshot.total_items if comparison_snapshot else current.total_items
        )

        # Calculate change
        if previous_total > 0:
            change_percent = ((current.total_items - previous_total) / previous_total) * 100
        else:
            change_percent = 0.0 if current.total_items == 0 else 100.0

        # Determine trend
        if change_percent < -10:
            trend = "decreasing"
        elif change_percent < 5:
            trend = "stable"
        elif change_percent < 25:
            trend = "increasing"
        else:
            trend = "exploding"

        # Calculate daily growth rate for projections
        if len(history) >= 2 and previous_total > 0 and comparison_snapshot is not None:
            days_between = max(
                1,
                (
                    datetime.fromisoformat(current.date.replace("Z", ""))
                    - datetime.fromisoformat(comparison_snapshot.date.replace("Z", ""))
                ).days,
            )
            daily_growth_rate = (current.total_items - previous_total) / days_between
        else:
            daily_growth_rate = 0

        # Project future debt
        projection_30 = int(current.total_items + (daily_growth_rate * 30))
        projection_90 = int(current.total_items + (daily_growth_rate * 90))

        # Calculate days until critical (define critical as 2x current)
        critical_threshold = current.total_items * 2
        if daily_growth_rate > 0:
            days_until_critical = int(
                (critical_threshold - current.total_items) / daily_growth_rate,
            )
        else:
            days_until_critical = None

        return DebtTrajectory(
            current_total=current.total_items,
            previous_total=previous_total,
            change_percent=round(change_percent, 1),
            trend=trend,
            projection_30_days=max(0, projection_30),
            projection_90_days=max(0, projection_90),
            critical_threshold_days=days_until_critical,
        )

    def _identify_hotspots(self, debt_items: list[DebtItem]) -> list[dict[str, Any]]:
        """Identify files with the most technical debt"""
        by_file: dict[str, list[DebtItem]] = {}

        for item in debt_items:
            if item.file_path not in by_file:
                by_file[item.file_path] = []
            by_file[item.file_path].append(item)

        hotspots = []
        for file_path, items in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
            # Calculate severity score
            severity_scores = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            total_severity = sum(severity_scores.get(i.severity, 1) for i in items)

            # Normalize file path for display
            try:
                fp = Path(file_path)
                if fp.is_absolute():
                    display_path = str(fp.relative_to(Path.cwd()))
                else:
                    display_path = str(fp)
            except ValueError:
                display_path = str(file_path)

            hotspots.append(
                {
                    "file": display_path,
                    "debt_count": len(items),
                    "severity_score": total_severity,
                    "types": list({i.debt_type for i in items}),
                    "oldest_item": min((i.date_found for i in items), default="unknown"),
                },
            )

        return hotspots

    def _generate_predictions(
        self,
        current: DebtSnapshot,
        trajectory: DebtTrajectory | None,
        hotspots: list[dict[str, Any]],
        history: list[DebtSnapshot],
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions based on trajectory"""
        predictions = []

        if trajectory:
            # Prediction 1: Debt explosion warning
            if trajectory.trend == "exploding":
                predictions.append(
                    {
                        "type": "debt_explosion",
                        "severity": "critical",
                        "description": (
                            f"Technical debt increased {trajectory.change_percent}% recently. "
                            f"At current trajectory: {trajectory.projection_30_days} items in 30 days, "
                            f"{trajectory.projection_90_days} in 90 days."
                        ),
                        "prevention_steps": [
                            "Allocate dedicated cleanup sprints",
                            "Add debt ceiling to Definition of Done",
                            "Block new features until debt stabilizes",
                        ],
                    },
                )

            # Prediction 2: Critical threshold warning
            if trajectory.critical_threshold_days and trajectory.critical_threshold_days < 180:
                predictions.append(
                    {
                        "type": "critical_threshold",
                        "severity": "high",
                        "description": (
                            f"At current growth rate, debt will double in "
                            f"{trajectory.critical_threshold_days} days. "
                            "Major refactoring will be required."
                        ),
                        "prevention_steps": [
                            "Start addressing high-severity items now",
                            "Review root causes of debt accumulation",
                            "Consider architectural improvements",
                        ],
                    },
                )

            # Prediction 3: Healthy trend acknowledgment
            if trajectory.trend == "decreasing":
                predictions.append(
                    {
                        "type": "positive_trend",
                        "severity": "info",
                        "description": (
                            f"Debt decreased {abs(trajectory.change_percent)}%. "
                            "Team is successfully paying down technical debt."
                        ),
                        "prevention_steps": ["Continue current practices"],
                    },
                )

        # Prediction 4: Hotspot warnings
        critical_hotspots = [h for h in hotspots if h["debt_count"] >= 10]
        if critical_hotspots:
            predictions.append(
                {
                    "type": "hotspot_concentration",
                    "severity": "medium",
                    "description": (
                        f"{len(critical_hotspots)} files have 10+ debt items. "
                        "Concentrated debt often indicates need for refactoring."
                    ),
                    "affected_files": [h["file"] for h in critical_hotspots[:3]],
                    "prevention_steps": [
                        "Prioritize refactoring hotspot files",
                        "Consider splitting large files",
                        "Review why debt accumulates in these areas",
                    ],
                },
            )

        # Prediction 5: Type-based pattern
        if current.by_type.get("hack", 0) >= 5:
            predictions.append(
                {
                    "type": "hack_accumulation",
                    "severity": "high",
                    "description": (
                        f"{current.by_type['hack']} HACK/XXX markers detected. "
                        "These often indicate shortcuts that need proper solutions."
                    ),
                    "prevention_steps": [
                        "Convert hacks to tracked issues",
                        "Estimate effort to replace each hack",
                        "Prioritize hacks in critical paths",
                    ],
                },
            )

        return predictions

    def _generate_recommendations(
        self,
        current: DebtSnapshot,
        trajectory: DebtTrajectory | None,
        hotspots: list[dict[str, Any]],
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Severity-based recommendations
        critical_count = current.by_severity.get("critical", 0)
        high_count = current.by_severity.get("high", 0)

        if critical_count > 0:
            recommendations.append(
                f"🚨 {critical_count} CRITICAL debt items need immediate attention",
            )

        if high_count > 3:
            recommendations.append(
                f"⚠️  {high_count} HIGH severity items - schedule for next sprint",
            )

        # Trajectory-based recommendations
        if trajectory and trajectory.trend in ["increasing", "exploding"]:
            recommendations.append(
                f"📈 Debt is {trajectory.trend} ({trajectory.change_percent:+.1f}%) - "
                "consider adding cleanup tasks to each sprint",
            )

        # Hotspot recommendations
        if hotspots and hotspots[0]["debt_count"] >= 5:
            recommendations.append(
                f"🔥 Top hotspot: {hotspots[0]['file']} "
                f"({hotspots[0]['debt_count']} items) - candidate for refactoring",
            )

        # Type-based recommendations
        if current.by_type.get("todo", 0) > 20:
            recommendations.append(
                f"📝 {current.by_type['todo']} TODOs - consider converting to tracked issues",
            )

        # History benefit reminder
        if trajectory:
            recommendations.append("📊 Trajectory analysis enabled - track progress over time")
        else:
            recommendations.append(
                "💡 Run regularly to build historical data for trajectory analysis",
            )

        return recommendations

    def _calculate_memory_benefit(
        self,
        history: list[DebtSnapshot],
        trajectory: DebtTrajectory | None,
    ) -> dict[str, Any]:
        """Calculate the benefit provided by persistent memory"""
        if not history:
            return {
                "history_available": False,
                "value_statement": (
                    "No historical data yet. Run regularly to enable trajectory analysis."
                ),
                "trajectory_enabled": False,
            }

        return {
            "history_available": True,
            "snapshots_stored": len(history),
            "earliest_record": history[0].date if history else None,
            "trajectory_enabled": trajectory is not None,
            "value_statement": (
                f"Persistent memory enables trajectory analysis with {len(history)} historical snapshots. "
                "Without memory, you'd only see a point-in-time count—no trends, no predictions."
            ),
            "insight": (
                f"Current trend: {trajectory.trend} ({trajectory.change_percent:+.1f}%)"
                if trajectory
                else "Building history..."
            ),
        }
