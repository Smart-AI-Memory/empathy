"""Clinical Protocol Monitor (Level 4)

Main monitoring system that combines protocol checking and trajectory analysis.

This is the healthcare equivalent of the Advanced Debugging Wizard.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from datetime import datetime
from typing import Any

from .monitoring.protocol_checker import ProtocolChecker, ProtocolCheckResult
from .monitoring.protocol_loader import ClinicalProtocol, ProtocolLoader
from .monitoring.sensor_parsers import normalize_vitals, parse_sensor_data
from .monitoring.trajectory_analyzer import TrajectoryAnalyzer, TrajectoryPrediction

logger = logging.getLogger(__name__)


class ClinicalProtocolMonitor:
    """Clinical Protocol Monitoring System.

    Monitors patient sensor data against clinical protocols using
    the same systematic approach as linting configuration:

    1. Load protocol (the "config")
    2. Parse sensor data (the "code state")
    3. Check compliance (run the "linter")
    4. Predict trajectory (Level 4 - anticipatory)
    5. Generate alerts and documentation
    """

    def __init__(self, protocol_directory: str | None = None):
        self.protocol_loader = ProtocolLoader(protocol_directory)
        self.protocol_checker = ProtocolChecker()
        self.trajectory_analyzer = TrajectoryAnalyzer()

        # Active protocols per patient
        self.active_protocols: dict[str, ClinicalProtocol] = {}

        # Historical data per patient
        self.patient_history: dict[str, list[dict[str, Any]]] = {}

    def load_protocol(
        self,
        patient_id: str,
        protocol_name: str,
        patient_context: dict[str, Any] | None = None,
    ) -> ClinicalProtocol:
        """Load and activate protocol for patient.

        Args:
            patient_id: Patient identifier
            protocol_name: Name of protocol to load
            patient_context: Additional patient context

        Returns:
            Loaded protocol

        Example:
            >>> monitor = ClinicalProtocolMonitor()
            >>> protocol = monitor.load_protocol(
            ...     patient_id="12345",
            ...     protocol_name="sepsis",
            ...     patient_context={"age": 65, "post_op_day": 2}
            ... )

        """
        protocol = self.protocol_loader.load_protocol(protocol_name)
        self.active_protocols[patient_id] = protocol

        logger.info(f"Loaded {protocol.name} v{protocol.version} for patient {patient_id}")

        return protocol

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Main analysis method - unified interface.

        Context expects:
            - patient_id: Patient identifier
            - sensor_data: Current sensor readings (JSON string or dict)
            - sensor_format: "simple_json" or "fhir" (default: simple_json)
            - protocol_name: Protocol to check (optional if already loaded)
            - intervention_status: Status of interventions (optional)

        Returns:
            Comprehensive analysis with alerts, predictions, recommendations

        """
        patient_id = context.get("patient_id")
        sensor_data = context.get("sensor_data")
        sensor_format = context.get("sensor_format", "simple_json")
        protocol_name = context.get("protocol_name")
        intervention_status = context.get("intervention_status", {})

        if not patient_id:
            return {"error": "patient_id required"}

        if not sensor_data:
            return {"error": "sensor_data required"}

        # Load protocol if not already active
        if patient_id not in self.active_protocols and protocol_name:
            self.load_protocol(patient_id, protocol_name)

        if patient_id not in self.active_protocols:
            return {"error": f"No active protocol for patient {patient_id}"}

        protocol = self.active_protocols[patient_id]

        # Parse sensor data
        if isinstance(sensor_data, str):
            readings = parse_sensor_data(sensor_data, sensor_format)
            normalized_data = normalize_vitals(readings)
        else:
            normalized_data = sensor_data

        # Store in history
        if patient_id not in self.patient_history:
            self.patient_history[patient_id] = []

        historical_entry = {"timestamp": datetime.now().isoformat(), **normalized_data}
        self.patient_history[patient_id].append(historical_entry)

        # Keep last 24 hours only
        if len(self.patient_history[patient_id]) > 144:  # 24hrs at 10min intervals
            self.patient_history[patient_id] = self.patient_history[patient_id][-144:]

        # Phase 1: Check protocol compliance
        compliance_result = self.protocol_checker.check_compliance(
            protocol,
            normalized_data,
            intervention_status,
        )

        # Phase 2: Analyze trajectory (Level 4)
        trajectory_prediction = self.trajectory_analyzer.analyze_trajectory(
            normalized_data,
            self.patient_history[patient_id][:-1],  # Exclude current reading
        )

        # Phase 3: Generate alerts
        alerts = self._generate_alerts(compliance_result, trajectory_prediction)

        # Phase 4: Generate recommendations
        recommendations = self._generate_recommendations(
            compliance_result,
            trajectory_prediction,
            protocol,
        )

        # Phase 5: Generate predictions (Level 4)
        predictions = self._generate_predictions(trajectory_prediction, compliance_result)

        return {
            "patient_id": patient_id,
            "protocol": {"name": protocol.name, "version": protocol.version},
            "current_vitals": normalized_data,
            # Protocol compliance (like linter output)
            "protocol_compliance": {
                "activated": compliance_result.protocol_activated,
                "score": compliance_result.activation_score,
                "threshold": compliance_result.threshold,
                "alert_level": compliance_result.alert_level,
                "deviations": [
                    {
                        "action": d.intervention.action,
                        "status": d.status.value,
                        "due": d.intervention.timing,
                        "reasoning": d.reasoning,
                    }
                    for d in compliance_result.deviations
                ],
                "compliant": compliance_result.compliant_items,
            },
            # Trajectory analysis (Level 4)
            "trajectory": {
                "state": trajectory_prediction.trajectory_state,
                "estimated_time_to_critical": trajectory_prediction.estimated_time_to_critical,
                "trends": [
                    {
                        "parameter": t.parameter,
                        "current": t.current_value,
                        "change": t.change,
                        "direction": t.direction,
                        "concerning": t.concerning,
                        "reasoning": t.reasoning,
                    }
                    for t in trajectory_prediction.vital_trends
                ],
                "assessment": trajectory_prediction.overall_assessment,
                "confidence": trajectory_prediction.confidence,
            },
            # Alerts
            "alerts": alerts,
            # Standard wizard outputs
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": trajectory_prediction.confidence,
        }

    def _generate_alerts(
        self,
        compliance: ProtocolCheckResult,
        trajectory: TrajectoryPrediction,
    ) -> list[dict[str, Any]]:
        """Generate alerts based on compliance and trajectory"""
        alerts = []

        # Protocol activation alert
        if compliance.protocol_activated:
            alerts.append(
                {
                    "type": "protocol_activated",
                    "severity": "high",
                    "message": compliance.recommendation,
                },
            )

        # Overdue intervention alerts
        overdue = [d for d in compliance.deviations if d.status.value == "overdue"]
        if overdue:
            alerts.append(
                {
                    "type": "intervention_overdue",
                    "severity": "critical",
                    "message": f"{len(overdue)} interventions overdue",
                    "details": [d.intervention.action for d in overdue],
                },
            )

        # Trajectory alerts (Level 4 - early warning)
        if trajectory.trajectory_state == "critical":
            alerts.append(
                {
                    "type": "trajectory_critical",
                    "severity": "critical",
                    "message": trajectory.overall_assessment,
                },
            )
        elif trajectory.trajectory_state == "concerning":
            alerts.append(
                {
                    "type": "trajectory_concerning",
                    "severity": "warning",
                    "message": trajectory.overall_assessment,
                    "time_to_critical": trajectory.estimated_time_to_critical,
                },
            )

        return alerts

    def _generate_recommendations(
        self,
        compliance: ProtocolCheckResult,
        trajectory: TrajectoryPrediction,
        protocol: ClinicalProtocol,
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # From protocol compliance
        if compliance.recommendation:
            recommendations.append(compliance.recommendation)

        # From trajectory analysis
        recommendations.extend(trajectory.recommendations)

        # From protocol-specific guidance
        if compliance.protocol_activated:
            recommendations.append(
                f"Follow {protocol.name} monitoring frequency: {protocol.monitoring_frequency}",
            )

        return list(set(recommendations))  # Deduplicate

    def _generate_predictions(
        self,
        trajectory: TrajectoryPrediction,
        compliance: ProtocolCheckResult,
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions"""
        predictions = []

        # Trajectory-based predictions
        if trajectory.trajectory_state in ["concerning", "critical"]:
            predictions.append(
                {
                    "type": "patient_deterioration",
                    "severity": "high" if trajectory.trajectory_state == "critical" else "medium",
                    "description": trajectory.overall_assessment,
                    "time_horizon": trajectory.estimated_time_to_critical,
                    "confidence": trajectory.confidence,
                    "prevention_steps": trajectory.recommendations,
                },
            )

        # Compliance-based predictions
        if compliance.protocol_activated and compliance.deviations:
            predictions.append(
                {
                    "type": "protocol_deviation_risk",
                    "severity": "high",
                    "description": "In our experience, protocol deviations correlate with adverse outcomes",
                    "prevention_steps": [
                        "Complete pending interventions",
                        "Document deviations and rationale",
                    ],
                },
            )

        return predictions
