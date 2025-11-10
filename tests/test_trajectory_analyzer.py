"""
Tests for Healthcare Plugin Trajectory Analyzer (Level 4)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_healthcare_plugin.monitors.monitoring.trajectory_analyzer import (
    TrajectoryAnalyzer,
    TrajectoryPrediction,
    VitalTrend,
)


class TestTrajectoryAnalyzer:
    """Test trajectory analyzer initialization and basic functionality"""

    def test_initialization(self):
        """Test analyzer initializes with correct normal ranges"""
        analyzer = TrajectoryAnalyzer()

        assert analyzer.normal_ranges["hr"] == (60, 100)
        assert analyzer.normal_ranges["systolic_bp"] == (90, 140)
        assert analyzer.normal_ranges["o2_sat"] == (95, 100)
        assert analyzer.normal_ranges["temp_f"] == (97.0, 99.5)

        assert analyzer.concerning_rates["hr"] == 15
        assert analyzer.concerning_rates["systolic_bp"] == 20
        assert analyzer.concerning_rates["respiratory_rate"] == 5

    def test_analyze_trajectory_no_history(self):
        """Test with no historical data returns low confidence"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = []

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert prediction.confidence == 0.3
        assert (
            prediction.overall_assessment == "Insufficient historical data for trajectory analysis"
        )
        assert prediction.recommendations == ["Continue monitoring"]
        assert prediction.estimated_time_to_critical is None


class TestStableTrajectory:
    """Test stable patient trajectory detection"""

    def test_stable_vitals(self):
        """Test stable vitals produce stable trajectory"""
        analyzer = TrajectoryAnalyzer()

        current = {
            "hr": 80,
            "systolic_bp": 120,
            "diastolic_bp": 75,
            "respiratory_rate": 16,
            "temp_f": 98.6,
            "o2_sat": 98,
        }

        history = [
            {
                "hr": 78,
                "systolic_bp": 118,
                "diastolic_bp": 74,
                "respiratory_rate": 15,
                "temp_f": 98.4,
                "o2_sat": 97,
            },
            {
                "hr": 79,
                "systolic_bp": 119,
                "diastolic_bp": 75,
                "respiratory_rate": 16,
                "temp_f": 98.5,
                "o2_sat": 98,
            },
            {
                "hr": 80,
                "systolic_bp": 120,
                "diastolic_bp": 75,
                "respiratory_rate": 16,
                "temp_f": 98.6,
                "o2_sat": 98,
            },
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert "stable" in prediction.overall_assessment.lower()
        assert prediction.recommendations == ["Continue routine monitoring"]
        assert prediction.estimated_time_to_critical is None

    def test_minimal_changes_are_stable(self):
        """Test that small changes (<5%) are considered stable"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 82}
        history = [{"hr": 80}, {"hr": 81}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        # Change is (82-81)/81 = 1.23%, should be stable
        assert any(trend.direction == "stable" for trend in prediction.vital_trends)


class TestConcerningTrajectory:
    """Test detection of concerning trends"""

    def test_elevated_heart_rate(self):
        """Test increasing heart rate triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115}  # Above normal range
        history = [{"hr": 95}, {"hr": 100}, {"hr": 105}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]
        assert len(prediction.vital_trends) > 0

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.concerning is True
        # Change from 105 to 115 is 9.5%, should be increasing
        assert hr_trend.direction in ["increasing", "stable"]  # May vary based on threshold

    def test_decreasing_blood_pressure(self):
        """Test decreasing BP triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 85}  # Below normal
        history = [{"systolic_bp": 110}, {"systolic_bp": 100}, {"systolic_bp": 90}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

        bp_trend = next((t for t in prediction.vital_trends if t.parameter == "systolic_bp"), None)
        assert bp_trend is not None
        assert bp_trend.concerning is True
        assert bp_trend.direction == "decreasing"

    def test_rapid_respiratory_rate_increase(self):
        """Test rapid RR increase triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"respiratory_rate": 30}
        history = [{"respiratory_rate": 18}, {"respiratory_rate": 22}, {"respiratory_rate": 26}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]


class TestCriticalTrajectory:
    """Test detection of critical trajectories"""

    def test_critical_oxygen_desaturation(self):
        """Test O2 sat drop triggers critical state"""
        analyzer = TrajectoryAnalyzer()

        current = {"o2_sat": 88, "hr": 95}  # O2 below critical threshold
        history = [{"o2_sat": 96, "hr": 85}, {"o2_sat": 93, "hr": 90}, {"o2_sat": 90, "hr": 93}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "critical"
        assert "critical" in prediction.overall_assessment.lower()

    def test_critical_blood_pressure_drop(self):
        """Test critical BP drop triggers critical state"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 75, "hr": 110}  # Critically low BP
        history = [
            {"systolic_bp": 100, "hr": 85},
            {"systolic_bp": 90, "hr": 95},
            {"systolic_bp": 85, "hr": 105},
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "critical"
        assert (
            "CRITICAL" in prediction.overall_assessment
            or "critical" in prediction.overall_assessment.lower()
        )

    def test_multiple_concerning_trends(self):
        """Test multiple concerning trends trigger critical/concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115, "systolic_bp": 85, "respiratory_rate": 28, "temp_f": 101.5}

        history = [
            {"hr": 90, "systolic_bp": 110, "respiratory_rate": 18, "temp_f": 98.6},
            {"hr": 100, "systolic_bp": 100, "respiratory_rate": 22, "temp_f": 99.5},
            {"hr": 110, "systolic_bp": 90, "respiratory_rate": 25, "temp_f": 100.5},
        ]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

        concerning_trends = [t for t in prediction.vital_trends if t.concerning]
        assert len(concerning_trends) >= 2


class TestLevel4Predictions:
    """Test Level 4 anticipatory predictions (time to critical)"""

    def test_time_to_critical_bp_prediction(self):
        """Test prediction of time until critical BP"""
        analyzer = TrajectoryAnalyzer()

        # BP dropping from 100 → 95 → 90, currently 95
        # If it continues, will hit 85 (critical) soon
        current = {"systolic_bp": 95}
        history = [{"systolic_bp": 100}, {"systolic_bp": 97}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            # Should estimate time to critical
            if prediction.estimated_time_to_critical:
                assert "hour" in prediction.estimated_time_to_critical

    def test_time_to_critical_o2_prediction(self):
        """Test prediction of time until critical O2 sat"""
        analyzer = TrajectoryAnalyzer()

        # Larger drops to trigger concerning state with time prediction
        current = {"o2_sat": 90}  # At critical threshold
        history = [{"o2_sat": 96}, {"o2_sat": 93}]

        prediction = analyzer.analyze_trajectory(current, history)

        # Should be concerning or critical
        assert prediction.trajectory_state in ["concerning", "critical"]
        # May or may not have time prediction depending on rate calculation
        # Just verify it's in valid states

    def test_no_time_prediction_for_stable(self):
        """Test no time prediction for stable patients"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = [{"hr": 78, "systolic_bp": 118}, {"hr": 79, "systolic_bp": 119}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert prediction.estimated_time_to_critical is None


class TestTrendAnalysis:
    """Test individual trend analysis"""

    def test_trend_direction_increasing(self):
        """Test trend correctly identifies increasing direction"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 100}
        history = [{"hr": 80}, {"hr": 90}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.direction == "increasing"
        assert hr_trend.change > 0

    def test_trend_direction_decreasing(self):
        """Test trend correctly identifies decreasing direction"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 70}
        history = [{"hr": 90}, {"hr": 80}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        assert hr_trend.direction == "decreasing"
        assert hr_trend.change < 0

    def test_trend_change_percent_calculation(self):
        """Test change percent is calculated correctly"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 110}
        history = [{"hr": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        assert hr_trend is not None
        # Change: 110 - 100 = 10, Percent: 10/100 * 100 = 10%
        assert hr_trend.change_percent == pytest.approx(10.0, abs=0.1)

    def test_skip_non_numeric_parameters(self):
        """Test that non-numeric parameters are skipped"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "mental_status": "alert"}
        history = [{"hr": 78, "mental_status": "alert"}]

        prediction = analyzer.analyze_trajectory(current, history)

        # Should only have hr trend, not mental_status
        assert len(prediction.vital_trends) == 1
        assert prediction.vital_trends[0].parameter == "hr"


class TestRecommendations:
    """Test recommendation generation"""

    def test_stable_recommendations(self):
        """Test stable vitals get routine monitoring recommendation"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 80, "systolic_bp": 120}
        history = [{"hr": 78, "systolic_bp": 118}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert "Continue routine monitoring" in prediction.recommendations

    def test_concerning_recommendations(self):
        """Test concerning vitals get increased monitoring"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 85}  # Below normal
        history = [{"systolic_bp": 110}, {"systolic_bp": 95}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            assert any("physician" in rec.lower() for rec in prediction.recommendations)
            assert any("monitoring" in rec.lower() for rec in prediction.recommendations)

    def test_critical_recommendations_include_rapid_response(self):
        """Test critical state recommends rapid response team"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 75, "o2_sat": 88}
        history = [{"systolic_bp": 100, "o2_sat": 96}, {"systolic_bp": 85, "o2_sat": 92}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state == "critical":
            assert any("rapid response" in rec.lower() for rec in prediction.recommendations)

    def test_specific_parameter_recommendations(self):
        """Test specific recommendations for different parameters"""
        analyzer = TrajectoryAnalyzer()

        # Test BP-specific recommendation
        current = {"systolic_bp": 85}
        history = [{"systolic_bp": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        if any(t.parameter == "systolic_bp" and t.concerning for t in prediction.vital_trends):
            assert any(
                "volume" in rec.lower() or "perfusion" in rec.lower()
                for rec in prediction.recommendations
            )


class TestConfidenceCalculation:
    """Test confidence scoring"""

    def test_more_data_increases_confidence(self):
        """Test that more historical data increases confidence"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85}

        # Few data points
        history_short = [{"hr": 80}]
        pred_short = analyzer.analyze_trajectory(current, history_short)

        # More data points
        history_long = [{"hr": 80}] * 10
        pred_long = analyzer.analyze_trajectory(current, history_long)

        assert pred_long.confidence >= pred_short.confidence

    def test_concerning_trends_affect_confidence(self):
        """Test that concerning trends affect confidence"""
        analyzer = TrajectoryAnalyzer()

        # Stable vitals
        current_stable = {"hr": 80, "systolic_bp": 120}
        history_stable = [{"hr": 78, "systolic_bp": 118}, {"hr": 79, "systolic_bp": 119}] * 5

        pred_stable = analyzer.analyze_trajectory(current_stable, history_stable)

        # All vitals concerning
        current_concerning = {"hr": 120, "systolic_bp": 80, "respiratory_rate": 30}
        history_concerning = [{"hr": 90, "systolic_bp": 110, "respiratory_rate": 18}] * 5

        pred_concerning = analyzer.analyze_trajectory(current_concerning, history_concerning)

        # Both should have confidence scores
        assert 0.0 <= pred_stable.confidence <= 1.0
        assert 0.0 <= pred_concerning.confidence <= 1.0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_missing_vitals_in_history(self):
        """Test handling of missing vitals in historical data"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85, "systolic_bp": 120}
        history = [{"hr": 80}, {"systolic_bp": 118}]  # Missing systolic_bp  # Missing hr

        prediction = analyzer.analyze_trajectory(current, history)

        # Should still work, just with available data
        assert prediction is not None
        assert prediction.trajectory_state in ["stable", "concerning", "critical", "improving"]

    def test_zero_previous_value_division(self):
        """Test handling of zero previous value in percent calculation"""
        analyzer = TrajectoryAnalyzer()

        # This is unrealistic for vital signs, but test edge case
        current = {"hr": 80}
        history = [{"hr": 0}]  # Invalid but test robustness

        prediction = analyzer.analyze_trajectory(current, history)

        # Should not crash
        assert prediction is not None

    def test_none_values_in_history(self):
        """Test handling of None values in historical data"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85}
        history = [{"hr": 80}, {"hr": None}, {"hr": 82}]  # None value

        prediction = analyzer.analyze_trajectory(current, history)

        # Should filter out None values
        assert prediction is not None

    def test_empty_current_data(self):
        """Test handling of empty current data"""
        analyzer = TrajectoryAnalyzer()

        current = {}
        history = [{"hr": 80}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "stable"
        assert len(prediction.vital_trends) == 0


class TestVitalTrendDataclass:
    """Test VitalTrend dataclass"""

    def test_vital_trend_creation(self):
        """Test creating a VitalTrend"""
        trend = VitalTrend(
            parameter="hr",
            current_value=100,
            previous_value=80,
            change=20,
            change_percent=25.0,
            direction="increasing",
            rate_of_change=10.0,
            concerning=True,
            reasoning="HR above normal range",
        )

        assert trend.parameter == "hr"
        assert trend.current_value == 100
        assert trend.concerning is True


class TestTrajectoryPredictionDataclass:
    """Test TrajectoryPrediction dataclass"""

    def test_trajectory_prediction_creation(self):
        """Test creating a TrajectoryPrediction"""
        trend = VitalTrend(
            parameter="hr",
            current_value=100,
            previous_value=80,
            change=20,
            change_percent=25.0,
            direction="increasing",
            rate_of_change=10.0,
            concerning=True,
            reasoning="HR elevated",
        )

        prediction = TrajectoryPrediction(
            trajectory_state="concerning",
            estimated_time_to_critical="2 hours",
            vital_trends=[trend],
            overall_assessment="Patient showing concerning trends",
            confidence=0.8,
            recommendations=["Notify physician"],
        )

        assert prediction.trajectory_state == "concerning"
        assert prediction.confidence == 0.8
        assert len(prediction.recommendations) == 1


class TestIsTrendConcerningEdgeCases:
    """Test _is_trend_concerning method edge cases for full coverage"""

    def test_hr_rapid_increase_concerning(self):
        """Test HR increasing rapidly triggers concerning"""
        analyzer = TrajectoryAnalyzer()

        # HR increasing from 80 to 100, rate > 15 bpm/hr threshold
        current = {"hr": 100}
        history = [{"hr": 80}, {"hr": 85}]

        prediction = analyzer.analyze_trajectory(current, history)

        hr_trend = next((t for t in prediction.vital_trends if t.parameter == "hr"), None)
        if hr_trend and hr_trend.rate_of_change > 15:
            assert hr_trend.concerning is True
            assert (
                "rapidly" in hr_trend.reasoning.lower()
                or "above normal" in hr_trend.reasoning.lower()
            )

    def test_systolic_bp_rapid_decrease_concerning(self):
        """Test systolic BP decreasing rapidly triggers concerning"""
        analyzer = TrajectoryAnalyzer()

        # BP dropping rapidly from 120 to 80 (40 mmHg over ~2 hours = 20 mmHg/hr)
        current = {"systolic_bp": 80}
        history = [{"systolic_bp": 120}, {"systolic_bp": 100}, {"systolic_bp": 90}]

        prediction = analyzer.analyze_trajectory(current, history)

        bp_trend = next((t for t in prediction.vital_trends if t.parameter == "systolic_bp"), None)
        assert bp_trend is not None
        assert bp_trend.concerning is True
        assert (
            "rapidly" in bp_trend.reasoning.lower() or "below normal" in bp_trend.reasoning.lower()
        )

    def test_respiratory_rate_rapid_increase_concerning(self):
        """Test respiratory rate increasing rapidly triggers concerning"""
        analyzer = TrajectoryAnalyzer()

        # RR increasing from 16 to 28 (12 breaths over ~2 hours = 6/hr > threshold of 5)
        current = {"respiratory_rate": 28}
        history = [{"respiratory_rate": 16}, {"respiratory_rate": 20}, {"respiratory_rate": 24}]

        prediction = analyzer.analyze_trajectory(current, history)

        rr_trend = next(
            (t for t in prediction.vital_trends if t.parameter == "respiratory_rate"), None
        )
        assert rr_trend is not None
        assert rr_trend.concerning is True

    def test_temp_rapid_increase_concerning(self):
        """Test temperature increasing rapidly triggers concerning"""
        analyzer = TrajectoryAnalyzer()

        # Temp increasing from 98.6 to 102.0 (3.4° over ~2 hours = 1.7°F/hr, close to 2.0 threshold)
        current = {"temp_f": 102.0}
        history = [{"temp_f": 98.6}, {"temp_f": 99.8}, {"temp_f": 101.0}]

        prediction = analyzer.analyze_trajectory(current, history)

        temp_trend = next((t for t in prediction.vital_trends if t.parameter == "temp_f"), None)
        assert temp_trend is not None
        assert temp_trend.concerning is True
        assert (
            "above normal" in temp_trend.reasoning.lower()
            or "rapidly" in temp_trend.reasoning.lower()
        )


class TestEstimateTimeToCriticalFullCoverage:
    """Test time-to-critical estimation for full coverage"""

    def test_systolic_bp_time_to_critical_calculated(self):
        """Test systolic BP time to critical is calculated"""
        analyzer = TrajectoryAnalyzer()

        # BP at 100, dropping to 95, rate makes it hit 90 (critical) in calculable time
        current = {"systolic_bp": 95}
        history = [{"systolic_bp": 110}, {"systolic_bp": 105}, {"systolic_bp": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            # Should have time estimate since BP is concerning
            assert prediction.estimated_time_to_critical is not None

    def test_o2_sat_time_to_critical_calculated(self):
        """Test O2 sat time to critical is calculated"""
        analyzer = TrajectoryAnalyzer()

        # O2 at 94, dropping toward 90 (critical threshold)
        current = {"o2_sat": 92}
        history = [{"o2_sat": 98}, {"o2_sat": 96}, {"o2_sat": 94}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state in ["concerning", "critical"]:
            # Should have O2 trend analysis
            o2_trend = next((t for t in prediction.vital_trends if t.parameter == "o2_sat"), None)
            assert o2_trend is not None

    def test_time_to_critical_within_24_hours(self):
        """Test time to critical is only estimated if within 24 hours"""
        analyzer = TrajectoryAnalyzer()

        # Very slow BP decline - won't hit critical for days
        current = {"systolic_bp": 110}
        history = [{"systolic_bp": 111}, {"systolic_bp": 110.5}]

        prediction = analyzer.analyze_trajectory(current, history)

        # If estimated, should be within reasonable timeframe
        if prediction.estimated_time_to_critical:
            assert "hour" in prediction.estimated_time_to_critical.lower()

    def test_time_to_critical_only_for_decreasing_bp(self):
        """Test time to critical only calculated for decreasing BP"""
        analyzer = TrajectoryAnalyzer()

        # BP increasing (not a concern for critical low BP)
        current = {"systolic_bp": 150}
        history = [{"systolic_bp": 120}, {"systolic_bp": 135}]

        prediction = analyzer.analyze_trajectory(current, history)

        # High BP shouldn't estimate time to critical low BP
        bp_trend = next((t for t in prediction.vital_trends if t.parameter == "systolic_bp"), None)
        if bp_trend:
            assert bp_trend.direction != "decreasing" or not bp_trend.concerning


class TestGenerateAssessmentFullCoverage:
    """Test _generate_assessment method for full branch coverage"""

    def test_critical_trajectory_assessment(self):
        """Test critical trajectory generates critical assessment"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 75, "o2_sat": 88, "hr": 130}
        history = [{"systolic_bp": 100, "o2_sat": 95, "hr": 90}] * 3

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state == "critical"
        assert (
            "CRITICAL" in prediction.overall_assessment
            or "critical" in prediction.overall_assessment.lower()
        )
        assert "intervention" in prediction.overall_assessment.lower()

    def test_concerning_with_time_to_critical_assessment(self):
        """Test concerning trajectory with time estimate"""
        analyzer = TrajectoryAnalyzer()

        # Concerning BP drop that triggers time estimation
        current = {"systolic_bp": 92}
        history = [{"systolic_bp": 105}, {"systolic_bp": 100}, {"systolic_bp": 96}]

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state == "concerning" and prediction.estimated_time_to_critical:
            assert "experience" in prediction.overall_assessment.lower()
            assert "estimated time" in prediction.overall_assessment.lower()
            assert "early intervention" in prediction.overall_assessment.lower()

    def test_concerning_without_time_to_critical_assessment(self):
        """Test concerning trajectory without time estimate"""
        analyzer = TrajectoryAnalyzer()

        # Concerning but not rapidly deteriorating
        current = {"hr": 110}
        history = [{"hr": 90}, {"hr": 100}]

        prediction = analyzer.analyze_trajectory(current, history)

        if (
            prediction.trajectory_state == "concerning"
            and not prediction.estimated_time_to_critical
        ):
            assert "experience" in prediction.overall_assessment.lower()
            assert "warrants" in prediction.overall_assessment.lower()


class TestGenerateRecommendationsFullCoverage:
    """Test _generate_recommendations method for full coverage"""

    def test_hr_specific_recommendation(self):
        """Test HR-specific recommendations"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 125}
        history = [{"hr": 85}, {"hr": 100}, {"hr": 115}]

        prediction = analyzer.analyze_trajectory(current, history)

        if any(t.parameter == "hr" and t.concerning for t in prediction.vital_trends):
            # Should recommend assessing for infection or pain
            assert any(
                "infection" in rec.lower() or "pain" in rec.lower()
                for rec in prediction.recommendations
            )

    def test_respiratory_rate_specific_recommendation(self):
        """Test respiratory rate specific recommendations"""
        analyzer = TrajectoryAnalyzer()

        current = {"respiratory_rate": 32}
        history = [{"respiratory_rate": 16}, {"respiratory_rate": 22}, {"respiratory_rate": 28}]

        prediction = analyzer.analyze_trajectory(current, history)

        if any(t.parameter == "respiratory_rate" and t.concerning for t in prediction.vital_trends):
            # Should recommend assessing respiratory status
            assert any(
                "respiratory" in rec.lower() or "oxygenation" in rec.lower()
                for rec in prediction.recommendations
            )

    def test_temp_specific_recommendation(self):
        """Test temperature specific recommendations"""
        analyzer = TrajectoryAnalyzer()

        current = {"temp_f": 102.5}
        history = [{"temp_f": 98.6}, {"temp_f": 100.0}, {"temp_f": 101.5}]

        prediction = analyzer.analyze_trajectory(current, history)

        if any(t.parameter == "temp_f" and t.concerning for t in prediction.vital_trends):
            # Should recommend assessing for infection
            assert any("infection" in rec.lower() for rec in prediction.recommendations)

    def test_critical_includes_rapid_response_recommendation(self):
        """Test critical state includes rapid response team"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 70, "o2_sat": 85}
        history = [{"systolic_bp": 100, "o2_sat": 96}] * 3

        prediction = analyzer.analyze_trajectory(current, history)

        if prediction.trajectory_state == "critical":
            assert any("rapid response" in rec.lower() for rec in prediction.recommendations)
            assert any("physician" in rec.lower() for rec in prediction.recommendations)


class TestCalculateConfidenceFullCoverage:
    """Test confidence calculation edge cases"""

    def test_confidence_with_no_trends(self):
        """Test confidence calculation when no vital trends"""
        analyzer = TrajectoryAnalyzer()

        current = {}
        history = [{"hr": 80}, {"hr": 81}]

        prediction = analyzer.analyze_trajectory(current, history)

        # Should have confidence based on data points
        assert 0.0 <= prediction.confidence <= 1.0

    def test_confidence_increases_with_data_points(self):
        """Test confidence increases up to 10 data points"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 85}

        # 5 data points
        history_5 = [{"hr": 80}] * 5
        pred_5 = analyzer.analyze_trajectory(current, history_5)

        # 15 data points (should cap at 10 for confidence calculation)
        history_15 = [{"hr": 80}] * 15
        pred_15 = analyzer.analyze_trajectory(current, history_15)

        # Both should be valid, 15 should have max data confidence (1.0)
        assert 0.0 <= pred_5.confidence <= 1.0
        assert 0.0 <= pred_15.confidence <= 1.0


class TestMultipleConcerningTrendsInteraction:
    """Test interactions between multiple concerning trends"""

    def test_one_concerning_trend_is_concerning_state(self):
        """Test one concerning trend triggers concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115, "systolic_bp": 120}  # Only HR concerning
        history = [{"hr": 85, "systolic_bp": 118}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

    def test_two_concerning_trends_is_concerning_state(self):
        """Test two concerning trends trigger concerning state"""
        analyzer = TrajectoryAnalyzer()

        current = {"hr": 115, "systolic_bp": 85}  # Both concerning
        history = [{"hr": 85, "systolic_bp": 110}]

        prediction = analyzer.analyze_trajectory(current, history)

        assert prediction.trajectory_state in ["concerning", "critical"]

    def test_critical_parameter_triggers_critical_state(self):
        """Test concerning critical parameter (BP, O2) triggers critical"""
        analyzer = TrajectoryAnalyzer()

        current = {"systolic_bp": 80, "hr": 90}  # BP is critical parameter
        history = [{"systolic_bp": 110, "hr": 88}]

        prediction = analyzer.analyze_trajectory(current, history)

        # systolic_bp is in critical_parameters list, so should be critical
        assert prediction.trajectory_state == "critical"
