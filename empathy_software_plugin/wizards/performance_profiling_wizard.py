"""Performance Profiling Wizard (Level 4)

Predicts performance bottlenecks BEFORE they become critical.

Level 4: Anticipatory - alerts to performance degradation trajectory.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from .base_wizard import BaseWizard
from .performance.bottleneck_detector import Bottleneck, BottleneckDetector
from .performance.profiler_parsers import (
    FunctionProfile,
    SimpleJSONProfilerParser,
    parse_profiler_output,
)
from .performance.trajectory_analyzer import PerformanceTrajectoryAnalyzer, TrajectoryPrediction

logger = logging.getLogger(__name__)


class PerformanceProfilingWizard(BaseWizard):
    """Performance Profiling Wizard - Level 4

    Beyond identifying current bottlenecks:
    - Predicts future performance degradation
    - Analyzes performance trajectory
    - Suggests optimizations based on impact
    - Cross-language performance patterns
    """

    @property
    def name(self) -> str:
        return "Performance Profiling Wizard"

    @property
    def level(self) -> int:
        return 4

    def __init__(self):
        super().__init__()

        self.profiler_parser = SimpleJSONProfilerParser()  # Default parser
        self.bottleneck_detector = BottleneckDetector()
        self.trajectory_analyzer = PerformanceTrajectoryAnalyzer()

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze performance and predict bottlenecks.

        Context expects:
            - profiler_data: Profiling output (string or dict)
            - profiler_type: "cprofile", "chrome_devtools", etc.
            - current_metrics: Current performance metrics (optional)
            - historical_metrics: Historical performance data (optional)
            - threshold_percent: Min % of time to consider (default: 5.0)

        Returns:
            Analysis with bottlenecks, trajectory, predictions, recommendations

        """
        profiler_data = context.get("profiler_data")
        profiler_type = context.get("profiler_type", "simple_json")
        current_metrics = context.get("current_metrics", {})
        historical_metrics = context.get("historical_metrics", [])
        threshold_percent = context.get("threshold_percent", 5.0)

        if not profiler_data:
            return {
                "error": "profiler_data required",
                "help": "Provide profiling output from cProfile, Chrome DevTools, etc.",
            }

        # Phase 1: Parse profiler output
        profiles = parse_profiler_output(profiler_type, profiler_data)

        # Phase 2: Detect bottlenecks
        bottlenecks = self.bottleneck_detector.detect_bottlenecks(profiles, threshold_percent)

        # Phase 3: Analyze trajectory (Level 4)
        trajectory_prediction = None
        if historical_metrics:
            # If no current_metrics provided, analyzer will extract from last historical entry
            trajectory_prediction = self.trajectory_analyzer.analyze_trajectory(
                current_metrics if current_metrics else historical_metrics,
                historical_metrics if current_metrics else None,
            )

        # Phase 4: Generate insights
        insights = self._generate_insights(profiles, bottlenecks)

        # Phase 5: Predictions (Level 4)
        predictions = self._generate_predictions(bottlenecks, trajectory_prediction, profiles)

        # Phase 6: Recommendations
        recommendations = self._generate_recommendations(
            bottlenecks,
            trajectory_prediction,
            insights,
        )

        # Get top function
        top_func = profiles[0] if profiles else None
        top_function_str = (
            f"{top_func.function_name} ({top_func.percent_total:.1f}% of time)"
            if top_func
            else "None"
        )

        return {
            "profiling_summary": {
                "total_functions": len(profiles),
                "total_time": sum(p.total_time for p in profiles),
                "top_function": top_function_str,
                "top_5_slowest": [
                    {"function": p.function_name, "time": p.total_time, "percent": p.percent_total}
                    for p in profiles[:5]
                ],
            },
            "bottlenecks": [b.to_dict() for b in bottlenecks],
            "trajectory": trajectory_prediction.to_dict() if trajectory_prediction else None,
            "trajectory_analysis": (
                trajectory_prediction.to_dict()
                if trajectory_prediction
                else {"state": "unknown", "trends": []}
            ),
            "insights": insights,
            # Standard wizard outputs
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85,
        }

    def _generate_insights(
        self,
        profiles: list[FunctionProfile],
        bottlenecks: list[Bottleneck],
    ) -> dict[str, Any]:
        """Generate performance insights"""
        # Identify patterns
        io_heavy = sum(1 for b in bottlenecks if b.type.value == "io_bound")
        cpu_heavy = sum(1 for b in bottlenecks if b.type.value == "cpu_bound")
        n_plus_one = sum(1 for b in bottlenecks if b.type.value == "n_plus_one")

        insights = {
            "dominant_pattern": self._identify_dominant_pattern(io_heavy, cpu_heavy, n_plus_one),
            "io_bound_operations": io_heavy,
            "cpu_bound_operations": cpu_heavy,
            "n_plus_one_queries": n_plus_one,
            "optimization_potential": self._estimate_optimization_potential(bottlenecks),
        }

        return insights

    def _identify_dominant_pattern(self, io_heavy: int, cpu_heavy: int, n_plus_one: int) -> str:
        """Identify dominant performance pattern"""
        if n_plus_one > 0:
            return "database_n_plus_one"
        if io_heavy > cpu_heavy:
            return "io_bound"
        if cpu_heavy > 0:
            return "cpu_bound"
        return "balanced"

    def _estimate_optimization_potential(self, bottlenecks: list[Bottleneck]) -> dict[str, Any]:
        """Estimate potential time savings from optimizations"""
        if not bottlenecks:
            return {"potential_savings": 0.0, "percentage": 0.0, "assessment": "LOW"}

        # Sum time from all bottlenecks
        total_bottleneck_time = sum(b.time_cost for b in bottlenecks)

        # Assume we can optimize 50% of bottleneck time
        potential_savings = total_bottleneck_time * 0.5

        # Calculate percentage of total
        total_time = (
            bottlenecks[0].time_cost / (bottlenecks[0].percent_total / 100) if bottlenecks else 1
        )
        percentage = (potential_savings / total_time * 100) if total_time > 0 else 0

        return {
            "potential_savings": potential_savings,
            "percentage": percentage,
            "assessment": self._assess_optimization_potential(percentage),
        }

    def _assess_optimization_potential(self, percentage: float) -> str:
        """Assess optimization potential"""
        if percentage > 30:
            return "HIGH"
        if percentage > 15:
            return "MEDIUM"
        if percentage > 5:
            return "LOW"
        return "MINIMAL"

    def _generate_predictions(
        self,
        bottlenecks: list[Bottleneck],
        trajectory: TrajectoryPrediction | None,
        profiles: list[FunctionProfile],
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions"""
        predictions = []

        # Prediction 1: Critical bottlenecks
        critical_bottlenecks = [b for b in bottlenecks if b.severity == "CRITICAL"]
        if critical_bottlenecks:
            predictions.append(
                {
                    "type": "performance_degradation_risk",
                    "severity": "critical",
                    "description": (
                        f"{len(critical_bottlenecks)} critical bottlenecks detected. "
                        f"In our experience, functions consuming >30% of execution time "
                        "cause timeout errors under load."
                    ),
                    "affected_functions": [b.function_name for b in critical_bottlenecks[:3]],
                    "prevention_steps": [b.fix_suggestion for b in critical_bottlenecks[:3]],
                },
            )

        # Prediction 2: N+1 query pattern
        n_plus_one = [b for b in bottlenecks if b.type.value == "n_plus_one"]
        if n_plus_one:
            predictions.append(
                {
                    "type": "scalability_risk",
                    "severity": "high",
                    "description": (
                        f"{len(n_plus_one)} potential N+1 query patterns detected. "
                        "In our experience, these cause exponential slowdown as data grows."
                    ),
                    "prevention_steps": [
                        "Implement eager loading or query batching",
                        "Add database query monitoring",
                        "Review ORM usage patterns",
                    ],
                },
            )

        # Prediction 3: Trajectory-based prediction
        if trajectory and trajectory.trajectory_state in ["degrading", "critical"]:
            predictions.append(
                {
                    "type": "performance_trajectory",
                    "severity": "high" if trajectory.trajectory_state == "critical" else "medium",
                    "description": trajectory.overall_assessment,
                    "time_horizon": trajectory.estimated_time_to_critical,
                    "confidence": trajectory.confidence,
                    "prevention_steps": trajectory.recommendations,
                },
            )

        return predictions

    def _generate_recommendations(
        self,
        bottlenecks: list[Bottleneck],
        trajectory: TrajectoryPrediction | None,
        insights: dict[str, Any],
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Pattern-based recommendations
        dominant_pattern = insights.get("dominant_pattern", "balanced")

        if dominant_pattern == "database_n_plus_one":
            recommendations.append(
                "⚠️  CRITICAL: Fix N+1 database queries with eager loading or batching",
            )

        if dominant_pattern == "io_bound":
            recommendations.append(
                "Optimize I/O operations: Use async I/O, connection pooling, or caching",
            )

        if dominant_pattern == "cpu_bound":
            recommendations.append(
                "Optimize CPU-heavy operations: Review algorithms, consider caching results",
            )

        # Bottleneck-specific recommendations
        for bottleneck in bottlenecks[:3]:  # Top 3
            recommendations.append(
                f"{bottleneck.severity}: {bottleneck.function_name} - {bottleneck.fix_suggestion}",
            )

        # Trajectory recommendations
        if trajectory and trajectory.trajectory_state != "optimal":
            recommendations.extend(trajectory.recommendations)

        # Optimization potential
        opt_potential = insights.get("optimization_potential", "LOW")
        if opt_potential in ["HIGH", "MEDIUM"]:
            recommendations.append(
                f"{opt_potential} optimization potential - significant performance gains possible",
            )

        return list(set(recommendations))  # Deduplicate
