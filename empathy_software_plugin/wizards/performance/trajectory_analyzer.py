"""
Performance Trajectory Analyzer (Level 4)

Analyzes performance trends to predict future bottlenecks.

This is Level 4 Anticipatory Empathy - predicting performance degradation
BEFORE it becomes critical.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from statistics import mean, stdev


@dataclass
class PerformanceTrend:
    """Trend analysis for a metric"""
    metric_name: str
    current_value: float
    previous_value: float
    change: float
    change_percent: float
    direction: str  # "improving", "degrading", "stable"
    rate_of_change: float  # per day/hour
    concerning: bool
    reasoning: str


@dataclass
class TrajectoryPrediction:
    """
    Performance trajectory prediction.

    This is Level 4 - predicting BEFORE hitting limits.
    """
    trajectory_state: str  # "optimal", "degrading", "critical"
    estimated_time_to_critical: Optional[str]
    trends: List[PerformanceTrend]
    overall_assessment: str
    confidence: float
    recommendations: List[str]


class PerformanceTrajectoryAnalyzer:
    """
    Analyzes performance trajectory to predict degradation.

    Level 4 Anticipatory Empathy implementation.
    """

    def __init__(self):
        # Define acceptable ranges
        self.acceptable_ranges = {
            "response_time": (0, 1.0),  # seconds
            "throughput": (100, float('inf')),  # requests/sec
            "error_rate": (0, 0.01),  # 1%
            "cpu_usage": (0, 0.80),  # 80%
            "memory_usage": (0, 0.85)  # 85%
        }

        # Define concerning growth rates
        self.concerning_rates = {
            "response_time": 0.1,  # 100ms increase per day
            "error_rate": 0.005,  # 0.5% increase
            "memory_usage": 0.05  # 5% increase
        }

    def analyze_trajectory(
        self,
        current_metrics: Dict[str, float],
        historical_metrics: List[Dict[str, Any]]
    ) -> TrajectoryPrediction:
        """
        Analyze performance trajectory.

        Args:
            current_metrics: Current performance metrics
            historical_metrics: Historical data (last N days/hours)

        Returns:
            TrajectoryPrediction with assessment

        Example:
            >>> history = [
            ...     {"time": "day1", "response_time": 0.2, "error_rate": 0.001},
            ...     {"time": "day2", "response_time": 0.45, "error_rate": 0.003},
            ...     {"time": "day3", "response_time": 0.8, "error_rate": 0.007}
            ... ]
            >>> prediction = analyzer.analyze_trajectory(current_metrics, history)
            >>> if prediction.trajectory_state == "degrading":
            ...     print(f"ALERT: {prediction.overall_assessment}")
        """

        if not historical_metrics:
            return TrajectoryPrediction(
                trajectory_state="optimal",
                estimated_time_to_critical=None,
                trends=[],
                overall_assessment="Insufficient historical data for trajectory analysis",
                confidence=0.3,
                recommendations=["Collect performance metrics over time"]
            )

        # Analyze trends for each metric
        trends = []

        for metric_name, current_value in current_metrics.items():
            trend = self._analyze_metric_trend(
                metric_name,
                current_value,
                historical_metrics
            )

            if trend:
                trends.append(trend)

        # Determine overall trajectory state
        trajectory_state = self._determine_trajectory_state(trends)

        # Estimate time to critical (if degrading)
        time_to_critical = None
        if trajectory_state in ["degrading", "critical"]:
            time_to_critical = self._estimate_time_to_critical(
                trends,
                current_metrics
            )

        # Generate assessment
        assessment = self._generate_assessment(
            trajectory_state,
            trends,
            time_to_critical
        )

        # Generate recommendations
        recommendations = self._generate_recommendations(
            trajectory_state,
            trends
        )

        # Calculate confidence
        confidence = self._calculate_confidence(historical_metrics, trends)

        return TrajectoryPrediction(
            trajectory_state=trajectory_state,
            estimated_time_to_critical=time_to_critical,
            trends=trends,
            overall_assessment=assessment,
            confidence=confidence,
            recommendations=recommendations
        )

    def _analyze_metric_trend(
        self,
        metric_name: str,
        current_value: float,
        historical_metrics: List[Dict[str, Any]]
    ) -> Optional[PerformanceTrend]:
        """Analyze trend for single metric"""

        # Extract historical values
        historical_values = []
        for entry in historical_metrics:
            if metric_name in entry and entry[metric_name] is not None:
                historical_values.append(float(entry[metric_name]))

        if not historical_values:
            return None

        # Calculate change from most recent
        previous_value = historical_values[-1]
        change = current_value - previous_value
        change_percent = (change / previous_value * 100) if previous_value != 0 else 0

        # Determine direction
        if abs(change_percent) < 5:
            direction = "stable"
        elif change > 0:
            # For metrics like response_time, error_rate - increase is bad
            if metric_name in ["response_time", "error_rate", "cpu_usage", "memory_usage"]:
                direction = "degrading"
            else:
                direction = "improving"
        else:
            if metric_name in ["response_time", "error_rate", "cpu_usage", "memory_usage"]:
                direction = "improving"
            else:
                direction = "degrading"

        # Calculate rate of change (per time period)
        time_periods = len(historical_values)
        rate_of_change = abs(change) / time_periods if time_periods > 0 else 0

        # Determine if concerning
        concerning, reasoning = self._is_trend_concerning(
            metric_name,
            current_value,
            change,
            rate_of_change,
            direction
        )

        return PerformanceTrend(
            metric_name=metric_name,
            current_value=current_value,
            previous_value=previous_value,
            change=change,
            change_percent=change_percent,
            direction=direction,
            rate_of_change=rate_of_change,
            concerning=concerning,
            reasoning=reasoning
        )

    def _is_trend_concerning(
        self,
        metric_name: str,
        current_value: float,
        change: float,
        rate_of_change: float,
        direction: str
    ) -> tuple[bool, str]:
        """Determine if trend is concerning"""

        # Check if currently out of acceptable range
        if metric_name in self.acceptable_ranges:
            min_val, max_val = self.acceptable_ranges[metric_name]

            if current_value < min_val:
                return True, f"{metric_name} below acceptable range"
            elif current_value > max_val:
                return True, f"{metric_name} above acceptable range ({max_val})"

        # Check rate of change
        if metric_name in self.concerning_rates:
            threshold = self.concerning_rates[metric_name]

            if direction == "degrading" and rate_of_change > threshold:
                return True, f"{metric_name} degrading rapidly ({change:+.3f} per period)"

        return False, "Within acceptable trajectory"

    def _determine_trajectory_state(
        self,
        trends: List[PerformanceTrend]
    ) -> str:
        """Determine overall trajectory state"""

        concerning_trends = [t for t in trends if t.concerning]

        if not concerning_trends:
            return "optimal"

        # Count critical metrics
        critical_metrics = ["response_time", "error_rate"]
        critical_concerning = sum(
            1 for t in concerning_trends
            if t.metric_name in critical_metrics
        )

        if critical_concerning >= 1:
            return "critical"

        if len(concerning_trends) >= 2:
            return "degrading"

        return "degrading"

    def _estimate_time_to_critical(
        self,
        trends: List[PerformanceTrend],
        current_metrics: Dict[str, float]
    ) -> Optional[str]:
        """
        Estimate time until metrics hit critical thresholds.

        Core Level 4 - predicting the future.
        """

        for trend in trends:
            if not trend.concerning:
                continue

            # Response time prediction
            if trend.metric_name == "response_time" and trend.direction == "degrading":
                critical_threshold = 1.0  # 1 second
                current = trend.current_value
                rate = trend.rate_of_change

                if rate > 0 and current < critical_threshold:
                    periods_to_critical = (critical_threshold - current) / rate
                    if 0 < periods_to_critical < 30:  # Within 30 periods
                        return f"~{int(periods_to_critical)} time periods"

            # Memory usage prediction
            if trend.metric_name == "memory_usage" and trend.direction == "degrading":
                critical_threshold = 0.95  # 95%
                current = trend.current_value
                rate = trend.rate_of_change

                if rate > 0 and current < critical_threshold:
                    periods_to_critical = (critical_threshold - current) / rate
                    if 0 < periods_to_critical < 30:
                        return f"~{int(periods_to_critical)} time periods"

        return None

    def _generate_assessment(
        self,
        trajectory_state: str,
        trends: List[PerformanceTrend],
        time_to_critical: Optional[str]
    ) -> str:
        """Generate overall assessment"""

        if trajectory_state == "optimal":
            return "Performance metrics stable. System operating within acceptable ranges."

        concerning = [t for t in trends if t.concerning]

        if trajectory_state == "critical":
            trends_desc = ", ".join(f"{t.metric_name} {t.direction}" for t in concerning[:3])
            return (
                f"CRITICAL performance trajectory: {trends_desc}. "
                "Immediate investigation required."
            )

        if trajectory_state == "degrading":
            trends_desc = ", ".join(f"{t.metric_name} {t.direction}" for t in concerning[:3])

            if time_to_critical:
                return (
                    f"Performance degrading: {trends_desc}. "
                    f"In our experience, this pattern leads to service degradation. "
                    f"Estimated time to critical: {time_to_critical}. "
                    "Early optimization recommended."
                )

            return (
                f"Performance degrading: {trends_desc}. "
                "In our experience, this warrants investigation."
            )

        return "Performance trajectory under assessment."

    def _generate_recommendations(
        self,
        trajectory_state: str,
        trends: List[PerformanceTrend]
    ) -> List[str]:
        """Generate actionable recommendations"""

        if trajectory_state == "optimal":
            return ["Continue monitoring performance metrics"]

        recommendations = []

        if trajectory_state in ["degrading", "critical"]:
            recommendations.append("Investigate performance degradation immediately")
            recommendations.append("Review recent code changes")

        concerning = [t for t in trends if t.concerning]

        for trend in concerning:
            if trend.metric_name == "response_time":
                recommendations.append("Profile slow endpoints to identify bottlenecks")
                recommendations.append("Consider adding caching or database optimization")
            elif trend.metric_name == "memory_usage":
                recommendations.append("Check for memory leaks")
                recommendations.append("Review object lifecycle and garbage collection")
            elif trend.metric_name == "error_rate":
                recommendations.append("Review error logs for patterns")
                recommendations.append("Add error monitoring and alerting")

        if trajectory_state == "critical":
            recommendations.append("Consider scaling resources immediately")

        return list(set(recommendations))  # Deduplicate

    def _calculate_confidence(
        self,
        historical_metrics: List[Dict[str, Any]],
        trends: List[PerformanceTrend]
    ) -> float:
        """Calculate confidence in prediction"""

        # More data = higher confidence
        data_points = len(historical_metrics)
        data_confidence = min(data_points / 10, 1.0)

        # More consistent trends = higher confidence
        if trends:
            concerning_count = sum(1 for t in trends if t.concerning)
            trend_confidence = concerning_count / len(trends) if trends else 0.5
        else:
            trend_confidence = 0.5

        return (data_confidence + trend_confidence) / 2

# Alias for backward compatibility
TrajectoryAnalyzer = PerformanceTrajectoryAnalyzer
