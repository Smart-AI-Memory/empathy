"""
Trajectory Analyzer (Level 4)

Analyzes vital sign trends to predict patient deterioration BEFORE critical.

This is Level 4 Anticipatory Empathy - alerting before the patient meets full crisis criteria.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class VitalTrend:
    """Trend analysis for a single vital sign"""

    parameter: str
    current_value: float
    previous_value: float
    change: float
    change_percent: float
    direction: str  # "increasing", "decreasing", "stable"
    rate_of_change: float  # units per hour
    concerning: bool
    reasoning: str


@dataclass
class TrajectoryPrediction:
    """
    Prediction of patient trajectory.

    This is Level 4 - predicting BEFORE criteria met.
    """

    trajectory_state: str  # "stable", "improving", "concerning", "critical"
    estimated_time_to_critical: str | None
    vital_trends: list[VitalTrend]
    overall_assessment: str
    confidence: float
    recommendations: list[str]


class TrajectoryAnalyzer:
    """
    Analyzes vital sign trajectory to predict deterioration.

    This implements Level 4 Anticipatory Empathy.
    """

    def __init__(self):
        # Define normal ranges
        self.normal_ranges = {
            "hr": (60, 100),
            "systolic_bp": (90, 140),
            "diastolic_bp": (60, 90),
            "respiratory_rate": (12, 20),
            "temp_f": (97.0, 99.5),
            "o2_sat": (95, 100),
        }

        # Define concerning rates of change
        self.concerning_rates = {
            "hr": 15,  # bpm increase over 2 hours
            "systolic_bp": 20,  # mmHg decrease
            "respiratory_rate": 5,  # breaths/min increase
            "temp_f": 2.0,  # degrees increase
        }

    def analyze_trajectory(
        self, current_data: dict[str, float], historical_data: list[dict[str, Any]]
    ) -> TrajectoryPrediction:
        """
        Analyze patient trajectory from historical vitals.

        Args:
            current_data: Current vital signs
            historical_data: List of previous readings (last 6-12 hours)

        Returns:
            TrajectoryPrediction with assessment

        Example:
            >>> history = [
            ...     {"timestamp": "12:00", "hr": 95, "systolic_bp": 120},
            ...     {"timestamp": "13:00", "hr": 105, "systolic_bp": 110},
            ...     {"timestamp": "14:00", "hr": 112, "systolic_bp": 95}
            ... ]
            >>> prediction = analyzer.analyze_trajectory(current_vitals, history)
            >>> if prediction.trajectory_state == "concerning":
            ...     print(f"ALERT: {prediction.overall_assessment}")
        """

        if not historical_data:
            return TrajectoryPrediction(
                trajectory_state="stable",
                estimated_time_to_critical=None,
                vital_trends=[],
                overall_assessment="Insufficient historical data for trajectory analysis",
                confidence=0.3,
                recommendations=["Continue monitoring"],
            )

        # Analyze trends for each vital sign
        vital_trends = []

        for parameter, current_value in current_data.items():
            if parameter in ["mental_status"]:  # Skip non-numeric
                continue

            trend = self._analyze_parameter_trend(parameter, current_value, historical_data)

            if trend:
                vital_trends.append(trend)

        # Determine overall trajectory state
        trajectory_state = self._determine_trajectory_state(vital_trends)

        # Estimate time to critical (if concerning)
        time_to_critical = None
        if trajectory_state in ["concerning", "critical"]:
            time_to_critical = self._estimate_time_to_critical(vital_trends, current_data)

        # Generate overall assessment
        assessment = self._generate_assessment(trajectory_state, vital_trends, time_to_critical)

        # Generate recommendations
        recommendations = self._generate_recommendations(trajectory_state, vital_trends)

        # Calculate confidence
        confidence = self._calculate_confidence(historical_data, vital_trends)

        return TrajectoryPrediction(
            trajectory_state=trajectory_state,
            estimated_time_to_critical=time_to_critical,
            vital_trends=vital_trends,
            overall_assessment=assessment,
            confidence=confidence,
            recommendations=recommendations,
        )

    def _analyze_parameter_trend(
        self, parameter: str, current_value: float, historical_data: list[dict[str, Any]]
    ) -> VitalTrend | None:
        """Analyze trend for single parameter"""

        # Extract historical values
        historical_values = []
        for entry in historical_data:
            if parameter in entry and entry[parameter] is not None:
                historical_values.append(entry[parameter])

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
            direction = "increasing"
        else:
            direction = "decreasing"

        # Calculate rate of change (per hour)
        # Assuming historical data spans 2-6 hours
        hours_elapsed = len(historical_values) / 2  # Rough estimate
        rate_of_change = abs(change) / hours_elapsed if hours_elapsed > 0 else 0

        # Determine if concerning
        concerning, reasoning = self._is_trend_concerning(
            parameter, current_value, change, rate_of_change, direction
        )

        return VitalTrend(
            parameter=parameter,
            current_value=current_value,
            previous_value=previous_value,
            change=change,
            change_percent=change_percent,
            direction=direction,
            rate_of_change=rate_of_change,
            concerning=concerning,
            reasoning=reasoning,
        )

    def _is_trend_concerning(
        self,
        parameter: str,
        current_value: float,
        change: float,
        rate_of_change: float,
        direction: str,
    ) -> tuple[bool, str]:
        """Determine if trend is concerning"""

        # Check if currently out of normal range
        if parameter in self.normal_ranges:
            min_val, max_val = self.normal_ranges[parameter]

            if current_value < min_val:
                return True, f"{parameter} below normal range ({min_val}-{max_val})"
            elif current_value > max_val:
                return True, f"{parameter} above normal range ({min_val}-{max_val})"

        # Check rate of change
        if parameter in self.concerning_rates:
            threshold = self.concerning_rates[parameter]

            if parameter == "hr" and direction == "increasing" and rate_of_change > threshold:
                return True, f"HR increasing rapidly (+{change:.0f} bpm)"

            if (
                parameter == "systolic_bp"
                and direction == "decreasing"
                and rate_of_change > threshold
            ):
                return True, f"BP decreasing rapidly (-{abs(change):.0f} mmHg)"

            if (
                parameter == "respiratory_rate"
                and direction == "increasing"
                and rate_of_change > threshold
            ):
                return True, f"RR increasing rapidly (+{change:.0f} /min)"

            if parameter == "temp_f" and direction == "increasing" and rate_of_change > threshold:
                return True, f"Temp increasing rapidly (+{change:.1f}°F)"

        return False, "Within normal trajectory"

    def _determine_trajectory_state(self, vital_trends: list[VitalTrend]) -> str:
        """Determine overall trajectory state"""

        concerning_trends = [t for t in vital_trends if t.concerning]

        if not concerning_trends:
            return "stable"

        # Count concerning trends by severity
        critical_parameters = ["systolic_bp", "o2_sat"]
        critical_concerning = sum(
            1 for t in concerning_trends if t.parameter in critical_parameters
        )

        if critical_concerning >= 1:
            return "critical"

        if len(concerning_trends) >= 2:
            return "concerning"

        if len(concerning_trends) == 1:
            return "concerning"

        return "stable"

    def _estimate_time_to_critical(
        self, vital_trends: list[VitalTrend], current_data: dict[str, float]
    ) -> str | None:
        """
        Estimate time until patient meets critical criteria.

        This is core Level 4 - predicting the future.
        """

        # Example: If BP dropping at 10 mmHg/hour, currently 95, critical is 85
        # Time to critical = (95 - 85) / 10 = 1 hour

        for trend in vital_trends:
            if not trend.concerning:
                continue

            if trend.parameter == "systolic_bp" and trend.direction == "decreasing":
                critical_threshold = 90
                current = trend.current_value
                rate = trend.rate_of_change

                if rate > 0:
                    hours_to_critical = (current - critical_threshold) / rate
                    if 0 < hours_to_critical < 24:
                        return f"~{int(hours_to_critical)} hours"

            if trend.parameter == "o2_sat" and trend.direction == "decreasing":
                critical_threshold = 90
                current = trend.current_value
                rate = trend.rate_of_change

                if rate > 0:
                    hours_to_critical = (current - critical_threshold) / rate
                    if 0 < hours_to_critical < 24:
                        return f"~{int(hours_to_critical)} hours"

        return None

    def _generate_assessment(
        self, trajectory_state: str, vital_trends: list[VitalTrend], time_to_critical: str | None
    ) -> str:
        """Generate overall assessment"""

        if trajectory_state == "stable":
            return "Patient vitals stable. Continue routine monitoring."

        concerning = [t for t in vital_trends if t.concerning]

        if trajectory_state == "critical":
            trends_desc = ", ".join(f"{t.parameter} {t.direction}" for t in concerning[:3])
            return (
                f"CRITICAL trajectory detected: {trends_desc}. "
                "Immediate intervention recommended."
            )

        if trajectory_state == "concerning":
            trends_desc = ", ".join(f"{t.parameter} {t.direction}" for t in concerning[:3])

            if time_to_critical:
                return (
                    f"Concerning trajectory: {trends_desc}. "
                    f"In our experience, this pattern suggests deterioration. "
                    f"Estimated time to critical: {time_to_critical}. "
                    "Early intervention may prevent escalation."
                )

            return (
                f"Concerning trajectory: {trends_desc}. "
                "In our experience, this pattern warrants closer monitoring."
            )

        return "Patient trajectory under assessment."

    def _generate_recommendations(
        self, trajectory_state: str, vital_trends: list[VitalTrend]
    ) -> list[str]:
        """Generate actionable recommendations"""

        if trajectory_state == "stable":
            return ["Continue routine monitoring"]

        recommendations = []

        if trajectory_state in ["concerning", "critical"]:
            recommendations.append("Notify physician of trajectory")
            recommendations.append("Increase monitoring frequency")

        concerning = [t for t in vital_trends if t.concerning]

        for trend in concerning:
            if trend.parameter == "systolic_bp":
                recommendations.append("Assess volume status and perfusion")
            elif trend.parameter == "hr":
                recommendations.append("Assess for infection or pain")
            elif trend.parameter == "respiratory_rate":
                recommendations.append("Assess respiratory status and oxygenation")
            elif trend.parameter == "temp_f":
                recommendations.append("Assess for infection")

        if trajectory_state == "critical":
            recommendations.append("Consider rapid response team activation")

        return recommendations

    def _calculate_confidence(
        self, historical_data: list[dict[str, Any]], vital_trends: list[VitalTrend]
    ) -> float:
        """Calculate confidence in prediction"""

        # More data = higher confidence
        data_points = len(historical_data)
        data_confidence = min(data_points / 10, 1.0)

        # More consistent trends = higher confidence
        if vital_trends:
            concerning_count = sum(1 for t in vital_trends if t.concerning)
            trend_confidence = concerning_count / len(vital_trends)
        else:
            trend_confidence = 0.5

        return (data_confidence + trend_confidence) / 2
