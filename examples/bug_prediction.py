"""
Bug Prediction - Level 4 Anticipatory Empathy Example

Demonstrates how to use Level 4 Anticipatory Empathy to predict bugs
BEFORE they occur, based on code trajectories and anti-patterns.

**Empathy Level**: Level 4 (Anticipatory)
- Analyzes code trajectories
- Predicts future bugs before they manifest
- Prepares preventive solutions
- Prevents debugging sessions from happening

**Inspired by**: AI Nurse Florence's compliance prediction (30 days ahead)

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from typing import Any, Dict, List

from empathy_os import (
    EmpathyOS,
    FeedbackLoopDetector,
    Level4Anticipatory,
    LeveragePointAnalyzer,
    Pattern,
    PatternLibrary,
)


class BugPredictor:
    """
    Level 4 Anticipatory bug prediction system

    Predicts bugs before they occur by analyzing:
    - Code complexity trends
    - Anti-pattern accumulation
    - Technical debt trajectory
    - Team velocity patterns
    """

    def __init__(self, team_id: str):
        """Initialize bug predictor"""
        self.team_id = team_id
        self.empathy = EmpathyOS(user_id=team_id, target_level=4)
        self.level4 = Level4Anticipatory()
        self.leverage_analyzer = LeveragePointAnalyzer()
        self.pattern_library = PatternLibrary()
        self.feedback_detector = FeedbackLoopDetector()

        # Load anti-patterns
        self._initialize_antipatterns()

    def _initialize_antipatterns(self):
        """Initialize known anti-patterns that predict bugs"""

        # Anti-pattern 1: Growing god classes
        ap1 = Pattern(
            id="ap_god_class",
            agent_id="bug_predictor",
            pattern_type="temporal",
            name="Growing god class",
            description="Classes growing beyond 500 lines predict future maintenance bugs",
            confidence=0.85,
            tags=["complexity", "architecture", "maintenance"]
        )
        self.pattern_library.contribute_pattern("bug_predictor", ap1)

        # Anti-pattern 2: Untested complex logic
        ap2 = Pattern(
            id="ap_untested_complexity",
            agent_id="bug_predictor",
            pattern_type="conditional",
            name="Complex logic without tests",
            description="Cyclomatic complexity >10 without tests predicts logic bugs",
            confidence=0.90,
            tags=["testing", "complexity", "reliability"]
        )
        self.pattern_library.contribute_pattern("bug_predictor", ap2)

        # Anti-pattern 3: Increasing coupling
        ap3 = Pattern(
            id="ap_coupling_increase",
            agent_id="bug_predictor",
            pattern_type="temporal",
            name="Increasing module coupling",
            description="Rising import counts predict integration bugs",
            confidence=0.80,
            tags=["architecture", "coupling", "integration"]
        )
        self.pattern_library.contribute_pattern("bug_predictor", ap3)

    def predict_bugs(
        self,
        current_code_metrics: Dict[str, Any],
        historical_metrics: List[Dict[str, Any]],
        prediction_horizon: str = "30_days"
    ) -> Dict[str, Any]:
        """
        Predict bugs before they occur (Level 4 Anticipatory)

        Args:
            current_code_metrics: Current state of codebase
            historical_metrics: Historical metrics showing trajectory
            prediction_horizon: How far ahead to predict

        Returns:
            Predictions with preventive actions
        """

        # Analyze trajectory
        trajectory_analysis = self._analyze_trajectory(
            current_code_metrics,
            historical_metrics
        )

        # Use Level 4 to predict future state
        prediction_response = self.level4.respond({
            "current_state": current_code_metrics,
            "trajectory": trajectory_analysis["trend"],
            "prediction_horizon": prediction_horizon
        })

        # Identify specific bug risks
        bug_risks = self._identify_bug_risks(
            current_code_metrics,
            trajectory_analysis
        )

        # Find leverage points for prevention
        leverage_points = self._find_prevention_leverage(bug_risks)

        # Compile comprehensive prediction
        prediction = {
            "prediction_horizon": prediction_horizon,
            "current_state": current_code_metrics,
            "trajectory": trajectory_analysis,
            "predicted_bugs": bug_risks,
            "preventive_actions": self._generate_preventive_actions(bug_risks),
            "leverage_points": leverage_points,
            "confidence": prediction_response["confidence"],
            "level4_analysis": prediction_response
        }

        return prediction

    def _analyze_trajectory(
        self,
        current: Dict[str, Any],
        historical: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze code metrics trajectory"""

        if not historical or len(historical) < 2:
            return {"trend": "unknown", "velocity": 0, "concerning": False}

        # Analyze key metrics over time
        complexity_trend = self._calculate_metric_trend(
            historical,
            "avg_complexity"
        )

        test_coverage_trend = self._calculate_metric_trend(
            historical,
            "test_coverage"
        )

        bug_rate_trend = self._calculate_metric_trend(
            historical,
            "bugs_per_week"
        )

        # Determine overall trend
        concerning_signals = []

        if complexity_trend > 0.1:  # Complexity increasing
            concerning_signals.append("Rising complexity")

        if test_coverage_trend < -0.05:  # Coverage decreasing
            concerning_signals.append("Declining test coverage")

        if bug_rate_trend > 0.2:  # Bugs increasing
            concerning_signals.append("Accelerating bug rate")

        return {
            "trend": "concerning" if concerning_signals else "stable",
            "complexity_velocity": complexity_trend,
            "coverage_velocity": test_coverage_trend,
            "bug_velocity": bug_rate_trend,
            "concerning_signals": concerning_signals,
            "concerning": len(concerning_signals) > 0
        }

    def _calculate_metric_trend(
        self,
        historical: List[Dict[str, Any]],
        metric_name: str
    ) -> float:
        """Calculate trend for a specific metric (simple linear regression)"""

        values = [h.get(metric_name, 0) for h in historical]

        if len(values) < 2:
            return 0.0

        # Simple slope calculation
        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _identify_bug_risks(
        self,
        current: Dict[str, Any],
        trajectory: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Identify specific bug risks based on current state and trajectory"""

        risks = []

        # Risk 1: Complexity explosion
        if current.get("avg_complexity", 0) > 8 and trajectory["complexity_velocity"] > 0:
            risks.append({
                "type": "complexity_explosion",
                "severity": "high",
                "description": "Code complexity growing unsustainably",
                "predicted_manifestation": "7-14 days",
                "evidence": {
                    "current_complexity": current.get("avg_complexity"),
                    "trend": "increasing",
                    "velocity": trajectory["complexity_velocity"]
                },
                "likely_symptoms": [
                    "Logic bugs in complex functions",
                    "Difficulty understanding code",
                    "Longer debugging sessions"
                ]
            })

        # Risk 2: Test coverage gaps
        if current.get("test_coverage", 100) < 70 and trajectory["coverage_velocity"] < 0:
            risks.append({
                "type": "test_coverage_gaps",
                "severity": "high",
                "description": "Test coverage declining while complexity grows",
                "predicted_manifestation": "14-21 days",
                "evidence": {
                    "current_coverage": current.get("test_coverage"),
                    "trend": "declining",
                    "velocity": trajectory["coverage_velocity"]
                },
                "likely_symptoms": [
                    "Bugs escaping to production",
                    "Regression bugs in existing features",
                    "Fear of refactoring"
                ]
            })

        # Risk 3: Integration bugs
        if current.get("module_coupling", 0) > 20 and trajectory.get("concerning", False):
            risks.append({
                "type": "integration_bugs",
                "severity": "medium",
                "description": "High coupling predicts integration failures",
                "predicted_manifestation": "21-30 days",
                "evidence": {
                    "coupling_score": current.get("module_coupling"),
                    "interdependencies": current.get("cross_module_calls", "unknown")
                },
                "likely_symptoms": [
                    "Cascading failures",
                    "Difficulty isolating bugs",
                    "Fragile builds"
                ]
            })

        # Risk 4: Technical debt accumulation
        if len(trajectory.get("concerning_signals", [])) >= 2:
            risks.append({
                "type": "technical_debt_crisis",
                "severity": "critical",
                "description": "Multiple concerning trends indicate approaching crisis",
                "predicted_manifestation": "30-60 days",
                "evidence": {
                    "concerning_signals": trajectory["concerning_signals"],
                    "trend": "multiple negative trajectories"
                },
                "likely_symptoms": [
                    "Development velocity collapse",
                    "Exponentially increasing bug rate",
                    "Developer frustration and burnout"
                ]
            })

        return risks

    def _generate_preventive_actions(
        self,
        bug_risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Generate preventive actions for predicted bugs"""

        actions = []

        for risk in bug_risks:
            if risk["type"] == "complexity_explosion":
                actions.append({
                    "risk": risk["type"],
                    "action": "Refactor complex functions",
                    "priority": "immediate",
                    "effort": "2-4 hours",
                    "impact": "Prevents logic bugs in 7-14 days",
                    "specific_steps": [
                        "Identify functions with complexity >10",
                        "Break down into smaller, single-purpose functions",
                        "Add unit tests for each extracted function",
                        "Document complex algorithms"
                    ]
                })

            elif risk["type"] == "test_coverage_gaps":
                actions.append({
                    "risk": risk["type"],
                    "action": "Increase test coverage to 75%",
                    "priority": "high",
                    "effort": "1-2 days",
                    "impact": "Prevents regression bugs in 14-21 days",
                    "specific_steps": [
                        "Identify untested critical paths",
                        "Write tests for high-risk areas first",
                        "Add coverage reporting to CI/CD",
                        "Block PRs with coverage decrease"
                    ]
                })

            elif risk["type"] == "integration_bugs":
                actions.append({
                    "risk": risk["type"],
                    "action": "Reduce module coupling",
                    "priority": "medium",
                    "effort": "3-5 days",
                    "impact": "Prevents integration failures in 21-30 days",
                    "specific_steps": [
                        "Identify highly coupled modules",
                        "Introduce abstraction layers",
                        "Apply dependency inversion",
                        "Add integration tests"
                    ]
                })

            elif risk["type"] == "technical_debt_crisis":
                actions.append({
                    "risk": risk["type"],
                    "action": "Declare tech debt sprint",
                    "priority": "critical",
                    "effort": "1-2 weeks",
                    "impact": "Prevents development velocity collapse",
                    "specific_steps": [
                        "Stop new feature development temporarily",
                        "Address all high-severity risks",
                        "Establish sustainable quality metrics",
                        "Implement continuous improvement practices"
                    ]
                })

        return actions

    def _find_prevention_leverage(
        self,
        bug_risks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find high-leverage intervention points for bug prevention"""

        leverage_points = []

        for risk in bug_risks:
            # Analyze leverage points for this problem class
            problem = {
                "class": risk["type"],
                "description": risk["description"],
                "severity": risk["severity"]
            }

            points = self.leverage_analyzer.find_leverage_points(problem)

            # Get top 2 leverage points
            top_points = self.leverage_analyzer.rank_by_effectiveness(points)[:2]

            for point in top_points:
                feasibility = self.leverage_analyzer.analyze_intervention_feasibility(point)
                leverage_points.append({
                    "risk": risk["type"],
                    "leverage_level": point.level.name,
                    "description": point.description,
                    "feasibility": feasibility
                })

        return leverage_points


def main():
    """Demonstrate bug prediction with Level 4 Anticipatory Empathy"""

    try:
        print("=" * 70)
        print("Bug Prediction - Level 4 Anticipatory Empathy")
        print("=" * 70)

        # Initialize predictor
        predictor = BugPredictor(team_id="team_backend")

        print(f"\n✓ Bug predictor initialized for team: team_backend")
        print(f"  Empathy Level: {predictor.empathy.target_level} (Anticipatory)")
        print(f"  Anti-patterns loaded: {len(predictor.pattern_library.patterns)}")

        # ========================================
        # Scenario: Analyze codebase trajectory
        # ========================================
        print("\n" + "=" * 70)
        print("Analyzing Codebase Trajectory")
        print("=" * 70)

    # Current state
    current_metrics = {
        "avg_complexity": 9.5,
        "test_coverage": 65,
        "module_coupling": 25,
        "bugs_per_week": 4.2,
        "lines_of_code": 15000
    }

    # Historical data (last 4 weeks)
    historical_metrics = [
        {"avg_complexity": 7.2, "test_coverage": 78, "bugs_per_week": 2.1},
        {"avg_complexity": 8.0, "test_coverage": 74, "bugs_per_week": 2.8},
        {"avg_complexity": 8.8, "test_coverage": 69, "bugs_per_week": 3.5},
        {"avg_complexity": 9.5, "test_coverage": 65, "bugs_per_week": 4.2}
    ]

    print("\n📊 Current State:")
    print(f"  Average Complexity: {current_metrics['avg_complexity']}")
    print(f"  Test Coverage: {current_metrics['test_coverage']}%")
    print(f"  Module Coupling: {current_metrics['module_coupling']}")
    print(f"  Bugs/Week: {current_metrics['bugs_per_week']}")

    print("\n📈 Historical Trend (4 weeks):")
    for i, metrics in enumerate(historical_metrics, 1):
        print(f"  Week {i}: Complexity={metrics['avg_complexity']}, "
              f"Coverage={metrics['test_coverage']}%, "
              f"Bugs={metrics['bugs_per_week']}")

    # ========================================
    # Make Prediction (30 days ahead)
    # ========================================
    print("\n" + "=" * 70)
    print("Level 4 Prediction: 30 Days Ahead")
    print("=" * 70)

    prediction = predictor.predict_bugs(
        current_code_metrics=current_metrics,
        historical_metrics=historical_metrics,
        prediction_horizon="30_days"
    )

    print(f"\n🔮 Prediction Confidence: {prediction['confidence']:.2f}")
    print(f"   Trajectory: {prediction['trajectory']['trend'].upper()}")

    if prediction['trajectory']['concerning_signals']:
        print(f"\n   ⚠️  Concerning Signals:")
        for signal in prediction['trajectory']['concerning_signals']:
            print(f"      - {signal}")

    # ========================================
    # Predicted Bug Risks
    # ========================================
    print("\n" + "=" * 70)
    print("Predicted Bug Risks (Before They Occur)")
    print("=" * 70)

    for i, risk in enumerate(prediction['predicted_bugs'], 1):
        print(f"\n🔴 Risk {i}: {risk['type'].replace('_', ' ').title()}")
        print(f"   Severity: {risk['severity'].upper()}")
        print(f"   Description: {risk['description']}")
        print(f"   Will manifest in: {risk['predicted_manifestation']}")
        print(f"   Evidence:")
        for key, value in risk['evidence'].items():
            print(f"      - {key}: {value}")
        print(f"   Likely symptoms:")
        for symptom in risk['likely_symptoms']:
            print(f"      • {symptom}")

    # ========================================
    # Preventive Actions
    # ========================================
    print("\n" + "=" * 70)
    print("Preventive Actions (Stop Bugs Before They Happen)")
    print("=" * 70)

    for i, action in enumerate(prediction['preventive_actions'], 1):
        print(f"\n✅ Action {i}: {action['action']}")
        print(f"   Priority: {action['priority'].upper()}")
        print(f"   Effort: {action['effort']}")
        print(f"   Impact: {action['impact']}")
        print(f"   Steps:")
        for step in action['specific_steps']:
            print(f"      {step}")

    # ========================================
    # Leverage Points
    # ========================================
    print("\n" + "=" * 70)
    print("High-Leverage Intervention Points")
    print("=" * 70)

    print("\nWhere to intervene for maximum impact:")
    for i, lp in enumerate(prediction['leverage_points'][:3], 1):
        print(f"\n{i}. {lp['leverage_level']} (Meadows)")
        print(f"   Risk: {lp['risk'].replace('_', ' ').title()}")
        print(f"   Intervention: {lp['description']}")
        print(f"   Feasibility: {lp['feasibility']['recommendation']}")

    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 70)
    print("Summary: Level 4 Anticipatory Bug Prevention")
    print("=" * 70)

    print("\n" + "Key Capabilities Demonstrated:")
    print("  ✓ Trajectory analysis (where is code heading?)")
    print("  ✓ Predictive bug identification (before bugs occur)")
    print("  ✓ Preventive action generation (stop bugs proactively)")
    print("  ✓ Leverage point analysis (maximum impact interventions)")
    print("  ✓ Evidence-based confidence (not guessing)")

    print("\nLevel 4 Anticipatory Empathy means:")
    print("  • Predict needs before they arise")
    print("  • Prevent problems instead of reacting to them")
    print("  • Analyze trajectories, not just current state")
    print("  • Prepare solutions in advance")
    print("  • See around corners")

    print("\n💡 Real-world Analogy:")
    print("   Just like AI Nurse Florence predicts CMS compliance gaps")
    print("   30 days before audit, this system predicts bugs 30 days")
    print("   before they manifest - giving developers time to prevent them.")

        print("\n" + "=" * 70)

    except ValueError as e:
        print(f"\n❌ Validation Error: {e}")
        print("Please check your input parameters and try again.")
        return 1
    except KeyError as e:
        print(f"\n❌ Missing Required Field: {e}")
        print("Check that all required fields are present in the data.")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected Error: {type(e).__name__}: {e}")
        print("Please check the documentation or file an issue.")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
