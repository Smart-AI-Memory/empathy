"""
Protocol Checker

Checks patient sensor data against clinical protocol criteria.

This is the "linter" for healthcare - runs the protocol rules against current state.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from .protocol_loader import ClinicalProtocol, ProtocolCriterion, ProtocolIntervention


class ComplianceStatus(Enum):
    """Status of protocol compliance"""

    COMPLIANT = "compliant"
    DEVIATION = "deviation"
    OVERDUE = "overdue"
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass
class CriterionResult:
    """Result of evaluating a single criterion"""

    criterion: ProtocolCriterion
    met: bool
    actual_value: Any
    points_awarded: int
    reasoning: str


@dataclass
class ProtocolDeviation:
    """A deviation from protocol (like a linting violation)"""

    intervention: ProtocolIntervention
    status: ComplianceStatus
    time_activated: datetime | None = None
    time_due: datetime | None = None
    time_completed: datetime | None = None
    overdue_by: str | None = None
    reasoning: str = ""


@dataclass
class ProtocolCheckResult:
    """
    Result of checking patient against protocol.

    This is like the output of running a linter.
    """

    protocol_activated: bool
    activation_score: int
    threshold: int
    criteria_results: list[CriterionResult]
    deviations: list[ProtocolDeviation]
    compliant_items: list[str]
    alert_level: str  # "NONE", "WARNING", "CRITICAL"
    recommendation: str


class ProtocolChecker:
    """
    Checks patient state against clinical protocol.

    This is the "linter engine" for healthcare.
    """

    def __init__(self):
        pass

    def check_compliance(
        self,
        protocol: ClinicalProtocol,
        patient_data: dict[str, Any],
        intervention_status: dict[str, Any] | None = None,
    ) -> ProtocolCheckResult:
        """
        Check if patient data meets protocol criteria.

        Args:
            protocol: Clinical protocol to check against
            patient_data: Current patient sensor data
            intervention_status: Status of interventions (if protocol active)

        Returns:
            ProtocolCheckResult with deviations

        Example:
            >>> patient = {"systolic_bp": 95, "respiratory_rate": 24, "hr": 110}
            >>> result = checker.check_compliance(sepsis_protocol, patient)
            >>> if result.protocol_activated:
            ...     print(f"ALERT: {result.recommendation}")
        """

        # Step 1: Evaluate screening criteria
        criteria_results = []
        total_points = 0

        for criterion in protocol.screening_criteria:
            result = self._evaluate_criterion(criterion, patient_data)
            criteria_results.append(result)
            if result.met:
                total_points += result.points_awarded

        # Step 2: Determine if protocol should activate
        protocol_activated = total_points >= protocol.screening_threshold

        # Step 3: If activated, check intervention compliance
        deviations = []
        compliant_items = []

        if protocol_activated and intervention_status:
            for intervention in protocol.interventions:
                status = intervention_status.get(intervention.action, {})
                deviation = self._check_intervention_status(intervention, status)

                if deviation:
                    deviations.append(deviation)
                else:
                    compliant_items.append(intervention.action)

        # Step 4: Determine alert level
        alert_level = self._determine_alert_level(
            protocol_activated, deviations, total_points, protocol.screening_threshold
        )

        # Step 5: Generate recommendation
        recommendation = self._generate_recommendation(
            protocol, protocol_activated, deviations, criteria_results
        )

        return ProtocolCheckResult(
            protocol_activated=protocol_activated,
            activation_score=total_points,
            threshold=protocol.screening_threshold,
            criteria_results=criteria_results,
            deviations=deviations,
            compliant_items=compliant_items,
            alert_level=alert_level,
            recommendation=recommendation,
        )

    def _evaluate_criterion(
        self, criterion: ProtocolCriterion, patient_data: dict[str, Any]
    ) -> CriterionResult:
        """Evaluate a single criterion"""

        actual_value = patient_data.get(criterion.parameter)

        if actual_value is None:
            return CriterionResult(
                criterion=criterion,
                met=False,
                actual_value=None,
                points_awarded=0,
                reasoning=f"{criterion.parameter} not available",
            )

        # Evaluate condition
        met = self._evaluate_condition(actual_value, criterion.condition, criterion.value)

        return CriterionResult(
            criterion=criterion,
            met=met,
            actual_value=actual_value,
            points_awarded=criterion.points if met else 0,
            reasoning=f"{criterion.parameter}={actual_value} {criterion.condition} {criterion.value}",
        )

    def _evaluate_condition(self, actual: Any, condition: str, expected: Any) -> bool:
        """Evaluate a condition (like <=, >=, ==, etc.)"""

        if condition == "<=":
            return actual <= expected
        elif condition == ">=":
            return actual >= expected
        elif condition == "==":
            return actual == expected
        elif condition == "!=":
            return actual != expected
        elif condition == "<":
            return actual < expected
        elif condition == ">":
            return actual > expected
        elif condition == "altered":
            # Special case for mental status
            return actual != "normal" if isinstance(actual, str) else actual < 15
        else:
            return False

    def _check_intervention_status(
        self, intervention: ProtocolIntervention, status: dict[str, Any]
    ) -> ProtocolDeviation | None:
        """Check if intervention has been completed"""

        completed = status.get("completed", False)
        time_completed = status.get("time_completed")
        time_due = status.get("time_due")

        if completed:
            return None  # No deviation - intervention done

        # Check if overdue
        if time_due:
            if isinstance(time_due, datetime) and datetime.now() > time_due:
                return ProtocolDeviation(
                    intervention=intervention,
                    status=ComplianceStatus.OVERDUE,
                    time_due=time_due,
                    overdue_by=str(datetime.now() - time_due),
                    reasoning=f"{intervention.action} overdue (due: {intervention.timing})",
                )

        # Pending but not yet overdue
        return ProtocolDeviation(
            intervention=intervention,
            status=ComplianceStatus.PENDING,
            reasoning=f"{intervention.action} pending (due: {intervention.timing})",
        )

    def _determine_alert_level(
        self,
        protocol_activated: bool,
        deviations: list[ProtocolDeviation],
        score: int,
        threshold: int,
    ) -> str:
        """Determine alert level"""

        if not protocol_activated:
            return "NONE"

        # Check for overdue critical interventions
        overdue_count = sum(1 for d in deviations if d.status == ComplianceStatus.OVERDUE)

        if overdue_count > 0:
            return "CRITICAL"

        # Check for pending interventions
        pending_count = sum(1 for d in deviations if d.status == ComplianceStatus.PENDING)

        if pending_count > 0:
            return "WARNING"

        return "NONE"

    def _generate_recommendation(
        self,
        protocol: ClinicalProtocol,
        activated: bool,
        deviations: list[ProtocolDeviation],
        criteria_results: list[CriterionResult],
    ) -> str:
        """Generate actionable recommendation"""

        if not activated:
            met_criteria = [c for c in criteria_results if c.met]
            if met_criteria:
                return (
                    f"Patient meets {len(met_criteria)} of {protocol.screening_threshold} "
                    f"criteria. Continue monitoring."
                )
            return "Patient stable. Continue routine monitoring."

        # Protocol activated
        if not deviations:
            return (
                f"{protocol.name} protocol active. All interventions complete. "
                f"Continue monitoring per protocol."
            )

        # Has deviations
        overdue = [d for d in deviations if d.status == ComplianceStatus.OVERDUE]
        pending = [d for d in deviations if d.status == ComplianceStatus.PENDING]

        if overdue:
            return (
                f"CRITICAL: {len(overdue)} interventions OVERDUE. "
                f"Immediate action required: {', '.join(d.intervention.action for d in overdue[:3])}"
            )

        if pending:
            return (
                f"WARNING: {protocol.name} activated. "
                f"{len(pending)} interventions pending: "
                f"{', '.join(d.intervention.action for d in pending[:3])}"
            )

        return "Protocol monitoring active."
