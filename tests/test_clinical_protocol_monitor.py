"""Comprehensive tests for ClinicalProtocolMonitor

Tests cover:
- Monitor initialization
- Protocol loading
- Async analysis workflow
- Alert generation
- Recommendations
- Predictions (Level 4)
"""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from empathy_healthcare_plugin.monitors.clinical_protocol_monitor import ClinicalProtocolMonitor
from empathy_healthcare_plugin.monitors.monitoring.protocol_checker import (
    ComplianceStatus,
    CriterionResult,
    ProtocolCheckResult,
    ProtocolDeviation,
    ProtocolIntervention,
)
from empathy_healthcare_plugin.monitors.monitoring.protocol_loader import (
    ClinicalProtocol,
    ProtocolCriterion,
)
from empathy_healthcare_plugin.monitors.monitoring.protocol_loader import (
    ProtocolIntervention as LoaderIntervention,
)
from empathy_healthcare_plugin.monitors.monitoring.trajectory_analyzer import (
    TrajectoryPrediction,
    VitalTrend,
)


@pytest.fixture
def mock_protocol():
    """Mock clinical protocol"""
    criterion = ProtocolCriterion(parameter="heart_rate", condition=">=90", value=90.0, points=1)

    intervention = LoaderIntervention(
        order=1,
        action="Blood cultures",
        timing="within 1 hour",
        required=True,
    )

    return ClinicalProtocol(
        name="sepsis",
        version="2.0",
        applies_to=["adult", "pediatric"],
        screening_criteria=[criterion],
        screening_threshold=2,
        interventions=[intervention],
        monitoring_frequency="every 1 hour",
        reassessment_timing="every 6 hours",
    )


@pytest.fixture
def mock_compliance_result():
    """Mock protocol check result"""
    intervention = ProtocolIntervention(
        order=1,
        action="Blood cultures",
        timing="within 1 hour",
        required=True,
    )

    deviation = ProtocolDeviation(
        intervention=intervention,
        status=ComplianceStatus.OVERDUE,
        reasoning="Blood cultures not drawn within 1 hour",
    )

    criterion_result = CriterionResult(
        criterion=ProtocolCriterion(parameter="heart_rate", condition=">=90", value=90.0, points=1),
        met=True,
        actual_value=105.0,
        points_awarded=1,
        reasoning="Heart rate elevated",
    )

    return ProtocolCheckResult(
        protocol_activated=True,
        activation_score=2,
        threshold=2,
        criteria_results=[criterion_result],
        alert_level="high",
        deviations=[deviation],
        compliant_items=["Vitals monitoring"],
        recommendation="Initiate sepsis protocol immediately",
    )


@pytest.fixture
def mock_trajectory_prediction():
    """Mock trajectory prediction"""
    trend = VitalTrend(
        parameter="heart_rate",
        current_value=105.0,
        previous_value=90.0,
        change=15.0,
        change_percent=16.67,
        direction="increasing",
        rate_of_change=2.5,
        concerning=True,
        reasoning="Heart rate trending upward, may indicate worsening sepsis",
    )

    return TrajectoryPrediction(
        trajectory_state="concerning",
        estimated_time_to_critical="2-4 hours",
        vital_trends=[trend],
        overall_assessment="Patient condition deteriorating - early sepsis indicators",
        confidence=0.85,
        recommendations=["Increase monitoring frequency", "Notify attending physician"],
    )


class TestClinicalProtocolMonitorInit:
    """Test monitor initialization"""

    def test_init_default(self):
        """Test initialization with default parameters"""
        monitor = ClinicalProtocolMonitor()

        assert monitor.protocol_loader is not None
        assert monitor.protocol_checker is not None
        assert monitor.trajectory_analyzer is not None
        assert monitor.active_protocols == {}
        assert monitor.patient_history == {}

    def test_init_with_directory(self):
        """Test initialization with custom protocol directory"""
        monitor = ClinicalProtocolMonitor(protocol_directory="/custom/protocols")

        assert monitor.protocol_loader is not None
        assert monitor.active_protocols == {}
        assert monitor.patient_history == {}


class TestLoadProtocol:
    """Test protocol loading"""

    def test_load_protocol_basic(self, mock_protocol):
        """Test basic protocol loading"""
        monitor = ClinicalProtocolMonitor()

        with patch.object(monitor.protocol_loader, "load_protocol", return_value=mock_protocol):
            protocol = monitor.load_protocol(patient_id="12345", protocol_name="sepsis")

            assert protocol == mock_protocol
            assert "12345" in monitor.active_protocols
            assert monitor.active_protocols["12345"] == mock_protocol

    def test_load_protocol_with_context(self, mock_protocol):
        """Test protocol loading with patient context"""
        monitor = ClinicalProtocolMonitor()

        with patch.object(monitor.protocol_loader, "load_protocol", return_value=mock_protocol):
            protocol = monitor.load_protocol(
                patient_id="12345",
                protocol_name="sepsis",
                patient_context={"age": 65, "post_op_day": 2},
            )

            assert protocol == mock_protocol
            assert "12345" in monitor.active_protocols


@pytest.mark.asyncio
class TestAnalyzeMethod:
    """Test main analysis method"""

    async def test_analyze_missing_patient_id(self):
        """Test analysis with missing patient_id"""
        monitor = ClinicalProtocolMonitor()

        context = {"sensor_data": {"heart_rate": 90}}
        result = await monitor.analyze(context)

        assert "error" in result
        assert "patient_id required" in result["error"]

    async def test_analyze_missing_sensor_data(self):
        """Test analysis with missing sensor data"""
        monitor = ClinicalProtocolMonitor()

        context = {"patient_id": "12345"}
        result = await monitor.analyze(context)

        assert "error" in result
        assert "sensor_data required" in result["error"]

    async def test_analyze_no_active_protocol(self):
        """Test analysis with no active protocol"""
        monitor = ClinicalProtocolMonitor()

        context = {"patient_id": "12345", "sensor_data": {"heart_rate": 90}}
        result = await monitor.analyze(context)

        assert "error" in result
        assert "No active protocol" in result["error"]

    async def test_analyze_load_protocol_on_demand(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test that analyze loads protocol if not active"""
        monitor = ClinicalProtocolMonitor()

        with (
            patch.object(monitor.protocol_loader, "load_protocol", return_value=mock_protocol),
            patch.object(
                monitor.protocol_checker,
                "check_compliance",
                return_value=mock_compliance_result,
            ),
            patch.object(
                monitor.trajectory_analyzer,
                "analyze_trajectory",
                return_value=mock_trajectory_prediction,
            ),
        ):
            context = {
                "patient_id": "12345",
                "sensor_data": {"heart_rate": 105, "temperature": 38.5},
                "protocol_name": "sepsis",
            }

            result = await monitor.analyze(context)

            assert "patient_id" in result
            assert result["patient_id"] == "12345"
            assert "12345" in monitor.active_protocols

    async def test_analyze_with_string_sensor_data(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test analysis with string sensor data (JSON)"""
        monitor = ClinicalProtocolMonitor()
        monitor.active_protocols["12345"] = mock_protocol

        with (
            patch(
                "empathy_healthcare_plugin.monitors.clinical_protocol_monitor.parse_sensor_data",
                return_value={"heart_rate": 105},
            ),
            patch(
                "empathy_healthcare_plugin.monitors.clinical_protocol_monitor.normalize_vitals",
                return_value={"heart_rate": 105},
            ),
            patch.object(
                monitor.protocol_checker,
                "check_compliance",
                return_value=mock_compliance_result,
            ),
            patch.object(
                monitor.trajectory_analyzer,
                "analyze_trajectory",
                return_value=mock_trajectory_prediction,
            ),
        ):
            context = {
                "patient_id": "12345",
                "sensor_data": '{"heart_rate": 105}',
                "sensor_format": "simple_json",
            }

            result = await monitor.analyze(context)

            assert "patient_id" in result
            assert "current_vitals" in result

    async def test_analyze_full_workflow(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test complete analysis workflow"""
        monitor = ClinicalProtocolMonitor()
        monitor.active_protocols["12345"] = mock_protocol

        with (
            patch.object(
                monitor.protocol_checker,
                "check_compliance",
                return_value=mock_compliance_result,
            ),
            patch.object(
                monitor.trajectory_analyzer,
                "analyze_trajectory",
                return_value=mock_trajectory_prediction,
            ),
        ):
            context = {
                "patient_id": "12345",
                "sensor_data": {"heart_rate": 105, "temperature": 38.5},
                "intervention_status": {"blood_cultures": "pending"},
            }

            result = await monitor.analyze(context)

            # Verify structure
            assert result["patient_id"] == "12345"
            assert "protocol" in result
            assert result["protocol"]["name"] == "sepsis"
            assert result["protocol"]["version"] == "2.0"

            # Verify vitals stored
            assert "current_vitals" in result

            # Verify compliance section
            assert "protocol_compliance" in result
            compliance = result["protocol_compliance"]
            assert compliance["activated"] is True
            assert "score" in compliance
            assert "deviations" in compliance

            # Verify trajectory section
            assert "trajectory" in result
            trajectory = result["trajectory"]
            assert trajectory["state"] == "concerning"
            assert "trends" in trajectory

            # Verify alerts, predictions, recommendations
            assert "alerts" in result
            assert "predictions" in result
            assert "recommendations" in result
            assert "confidence" in result

    async def test_analyze_patient_history_storage(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test that patient history is stored correctly"""
        monitor = ClinicalProtocolMonitor()
        monitor.active_protocols["12345"] = mock_protocol

        with (
            patch.object(
                monitor.protocol_checker,
                "check_compliance",
                return_value=mock_compliance_result,
            ),
            patch.object(
                monitor.trajectory_analyzer,
                "analyze_trajectory",
                return_value=mock_trajectory_prediction,
            ),
        ):
            # First reading
            context1 = {"patient_id": "12345", "sensor_data": {"heart_rate": 90}}
            await monitor.analyze(context1)

            assert "12345" in monitor.patient_history
            assert len(monitor.patient_history["12345"]) == 1

            # Second reading
            context2 = {"patient_id": "12345", "sensor_data": {"heart_rate": 95}}
            await monitor.analyze(context2)

            assert len(monitor.patient_history["12345"]) == 2

    async def test_analyze_history_truncation(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test that history is truncated to 24 hours"""
        monitor = ClinicalProtocolMonitor()
        monitor.active_protocols["12345"] = mock_protocol

        # Pre-fill with 150 entries (more than 144 limit)
        monitor.patient_history["12345"] = [
            {"timestamp": datetime.now().isoformat(), "heart_rate": 80} for _ in range(150)
        ]

        with (
            patch.object(
                monitor.protocol_checker,
                "check_compliance",
                return_value=mock_compliance_result,
            ),
            patch.object(
                monitor.trajectory_analyzer,
                "analyze_trajectory",
                return_value=mock_trajectory_prediction,
            ),
        ):
            context = {"patient_id": "12345", "sensor_data": {"heart_rate": 90}}
            await monitor.analyze(context)

            # Should be truncated to last 144 entries
            assert len(monitor.patient_history["12345"]) == 144


class TestGenerateAlerts:
    """Test alert generation"""

    def test_generate_alerts_protocol_activated(
        self,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test alert generation when protocol is activated"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "stable"

        alerts = monitor._generate_alerts(mock_compliance_result, mock_trajectory_prediction)

        # Should have protocol activation alert
        protocol_alerts = [a for a in alerts if a["type"] == "protocol_activated"]
        assert len(protocol_alerts) == 1
        assert protocol_alerts[0]["severity"] == "high"

    def test_generate_alerts_overdue_interventions(
        self,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test alert generation for overdue interventions"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "stable"

        alerts = monitor._generate_alerts(mock_compliance_result, mock_trajectory_prediction)

        # Should have overdue intervention alert
        overdue_alerts = [a for a in alerts if a["type"] == "intervention_overdue"]
        assert len(overdue_alerts) == 1
        assert overdue_alerts[0]["severity"] == "critical"
        assert "Blood cultures" in overdue_alerts[0]["details"]

    def test_generate_alerts_trajectory_critical(self, mock_trajectory_prediction):
        """Test alert generation for critical trajectory"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "critical"

        # Mock compliance with no overdue
        compliance = Mock()
        compliance.protocol_activated = False
        compliance.deviations = []

        alerts = monitor._generate_alerts(compliance, mock_trajectory_prediction)

        critical_alerts = [a for a in alerts if a["type"] == "trajectory_critical"]
        assert len(critical_alerts) == 1
        assert critical_alerts[0]["severity"] == "critical"

    def test_generate_alerts_trajectory_concerning(self, mock_trajectory_prediction):
        """Test alert generation for concerning trajectory"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "concerning"

        compliance = Mock()
        compliance.protocol_activated = False
        compliance.deviations = []

        alerts = monitor._generate_alerts(compliance, mock_trajectory_prediction)

        concerning_alerts = [a for a in alerts if a["type"] == "trajectory_concerning"]
        assert len(concerning_alerts) == 1
        assert concerning_alerts[0]["severity"] == "warning"
        assert "time_to_critical" in concerning_alerts[0]


class TestGenerateRecommendations:
    """Test recommendation generation"""

    def test_generate_recommendations_from_compliance(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test recommendations from compliance check"""
        monitor = ClinicalProtocolMonitor()

        recommendations = monitor._generate_recommendations(
            mock_compliance_result,
            mock_trajectory_prediction,
            mock_protocol,
        )

        assert len(recommendations) > 0
        assert mock_compliance_result.recommendation in recommendations

    def test_generate_recommendations_from_trajectory(
        self,
        mock_protocol,
        mock_trajectory_prediction,
    ):
        """Test recommendations from trajectory analysis"""
        monitor = ClinicalProtocolMonitor()

        compliance = Mock()
        compliance.protocol_activated = False
        compliance.recommendation = None

        recommendations = monitor._generate_recommendations(
            compliance,
            mock_trajectory_prediction,
            mock_protocol,
        )

        # Should include trajectory recommendations
        for rec in mock_trajectory_prediction.recommendations:
            assert rec in recommendations

    def test_generate_recommendations_protocol_monitoring(
        self,
        mock_protocol,
        mock_compliance_result,
        mock_trajectory_prediction,
    ):
        """Test protocol-specific monitoring recommendations"""
        monitor = ClinicalProtocolMonitor()

        recommendations = monitor._generate_recommendations(
            mock_compliance_result,
            mock_trajectory_prediction,
            mock_protocol,
        )

        # Should include protocol monitoring frequency
        monitoring_recs = [r for r in recommendations if "every 1 hour" in r]
        assert len(monitoring_recs) > 0

    def test_generate_recommendations_deduplication(
        self,
        mock_protocol,
        mock_trajectory_prediction,
    ):
        """Test that duplicate recommendations are removed"""
        monitor = ClinicalProtocolMonitor()

        # Create compliance with duplicate recommendation
        compliance = Mock()
        compliance.protocol_activated = True
        compliance.recommendation = "Increase monitoring frequency"

        # Trajectory also has this recommendation
        mock_trajectory_prediction.recommendations = [
            "Increase monitoring frequency",
            "Other recommendation",
        ]

        recommendations = monitor._generate_recommendations(
            compliance,
            mock_trajectory_prediction,
            mock_protocol,
        )

        # Should not have duplicates
        assert len(recommendations) == len(set(recommendations))


class TestGeneratePredictions:
    """Test Level 4 prediction generation"""

    def test_generate_predictions_concerning_trajectory(
        self,
        mock_trajectory_prediction,
        mock_compliance_result,
    ):
        """Test predictions for concerning trajectory"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "concerning"
        mock_compliance_result.protocol_activated = False
        mock_compliance_result.deviations = []

        predictions = monitor._generate_predictions(
            mock_trajectory_prediction,
            mock_compliance_result,
        )

        deterioration_preds = [p for p in predictions if p["type"] == "patient_deterioration"]
        assert len(deterioration_preds) == 1
        assert deterioration_preds[0]["severity"] == "medium"

    def test_generate_predictions_critical_trajectory(
        self,
        mock_trajectory_prediction,
        mock_compliance_result,
    ):
        """Test predictions for critical trajectory"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "critical"
        mock_compliance_result.protocol_activated = False
        mock_compliance_result.deviations = []

        predictions = monitor._generate_predictions(
            mock_trajectory_prediction,
            mock_compliance_result,
        )

        deterioration_preds = [p for p in predictions if p["type"] == "patient_deterioration"]
        assert len(deterioration_preds) == 1
        assert deterioration_preds[0]["severity"] == "high"

    def test_generate_predictions_protocol_deviation(
        self,
        mock_trajectory_prediction,
        mock_compliance_result,
    ):
        """Test predictions for protocol deviations"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "stable"
        mock_compliance_result.protocol_activated = True
        # mock_compliance_result.deviations already has one deviation

        predictions = monitor._generate_predictions(
            mock_trajectory_prediction,
            mock_compliance_result,
        )

        deviation_preds = [p for p in predictions if p["type"] == "protocol_deviation_risk"]
        assert len(deviation_preds) == 1
        assert deviation_preds[0]["severity"] == "high"
        assert "prevention_steps" in deviation_preds[0]

    def test_generate_predictions_stable_no_deviations(self, mock_trajectory_prediction):
        """Test predictions when everything is stable"""
        monitor = ClinicalProtocolMonitor()
        mock_trajectory_prediction.trajectory_state = "stable"

        compliance = Mock()
        compliance.protocol_activated = False
        compliance.deviations = []

        predictions = monitor._generate_predictions(mock_trajectory_prediction, compliance)

        # Should have no predictions when stable
        assert len(predictions) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
