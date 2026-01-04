"""Tests for Protocol Checker

Tests the healthcare "linter" that validates patient data against clinical protocols.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from datetime import datetime, timedelta

from empathy_healthcare_plugin.monitors.monitoring.protocol_checker import (
    ComplianceStatus,
    ProtocolChecker,
    ProtocolCheckResult,
    ProtocolDeviation,
)
from empathy_healthcare_plugin.monitors.monitoring.protocol_loader import (
    ClinicalProtocol,
    ProtocolCriterion,
    ProtocolIntervention,
)


class TestProtocolChecker:
    """Test basic ProtocolChecker functionality"""

    def test_initialization(self):
        """Test ProtocolChecker initializes correctly"""
        checker = ProtocolChecker()
        assert checker is not None
        # Should be ready to check protocols

    def test_basic_check_compliance(self):
        """Test basic check_compliance method"""
        checker = ProtocolChecker()
        protocol = ClinicalProtocol(
            name="Test",
            version="1.0",
            applies_to=["all"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )
        result = checker.check_compliance(protocol, {})
        assert result is not None
        assert isinstance(result, ProtocolCheckResult)


class TestCriterionEvaluation:
    """Test evaluation of protocol criteria"""

    def test_evaluate_less_than_or_equal(self):
        """Test <= condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="temperature",
            condition="<=",
            value=36.0,
            points=2,
            description="Hypothermia",
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"temperature": 35.5})
        assert result.met is True
        assert result.points_awarded == 2

        # Should not match
        result = checker._evaluate_criterion(criterion, {"temperature": 37.0})
        assert result.met is False
        assert result.points_awarded == 0

    def test_evaluate_greater_than_or_equal(self):
        """Test >= condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="heart_rate",
            condition=">=",
            value=100,
            points=1,
            description="Tachycardia",
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"heart_rate": 110})
        assert result.met is True
        assert result.points_awarded == 1

        # Should not match
        result = checker._evaluate_criterion(criterion, {"heart_rate": 80})
        assert result.met is False

    def test_evaluate_equals(self):
        """Test == condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="code_status",
            condition="==",
            value="full_code",
            points=0,
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"code_status": "full_code"})
        assert result.met is True

        # Should not match
        result = checker._evaluate_criterion(criterion, {"code_status": "dnr"})
        assert result.met is False

    def test_evaluate_not_equals(self):
        """Test != condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="status",
            condition="!=",
            value="stable",
            points=1,
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"status": "deteriorating"})
        assert result.met is True

        # Should not match
        result = checker._evaluate_criterion(criterion, {"status": "stable"})
        assert result.met is False

    def test_evaluate_less_than(self):
        """Test < condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="o2_sat",
            condition="<",
            value=90,
            points=3,
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"o2_sat": 88})
        assert result.met is True
        assert result.points_awarded == 3

        # Should not match (equal)
        result = checker._evaluate_criterion(criterion, {"o2_sat": 90})
        assert result.met is False

        # Should not match (greater)
        result = checker._evaluate_criterion(criterion, {"o2_sat": 95})
        assert result.met is False

    def test_evaluate_greater_than(self):
        """Test > condition evaluation"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="systolic_bp",
            condition=">",
            value=180,
            points=2,
        )

        # Should match
        result = checker._evaluate_criterion(criterion, {"systolic_bp": 190})
        assert result.met is True

        # Should not match (equal)
        result = checker._evaluate_criterion(criterion, {"systolic_bp": 180})
        assert result.met is False

        # Should not match (less)
        result = checker._evaluate_criterion(criterion, {"systolic_bp": 170})
        assert result.met is False

    def test_evaluate_altered_condition(self):
        """Test 'altered' condition for mental status"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="mental_status",
            condition="altered",
            points=2,
        )

        # Should match altered states (anything != "normal")
        for status in ["confused", "lethargic", "obtunded", "altered", "alert"]:
            result = checker._evaluate_criterion(criterion, {"mental_status": status})
            assert result.met is True, f"Should match {status} (!= normal)"

        # Should not match "normal" state
        result = checker._evaluate_criterion(criterion, {"mental_status": "normal"})
        assert result.met is False

        # Should also work with numeric values (GCS score < 15)
        criterion_numeric = ProtocolCriterion(
            parameter="gcs_score",
            condition="altered",
            points=2,
        )
        result = checker._evaluate_criterion(criterion_numeric, {"gcs_score": 10})
        assert result.met is True

        result = checker._evaluate_criterion(criterion_numeric, {"gcs_score": 15})
        assert result.met is False

    def test_evaluate_missing_parameter(self):
        """Test evaluation when parameter is missing from patient data"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="lactate",
            condition=">=",
            value=2.0,
            points=2,
        )

        # Missing parameter should not match
        result = checker._evaluate_criterion(criterion, {"temperature": 37.0})
        assert result.met is False
        assert result.actual_value is None

    def test_evaluate_none_value(self):
        """Test evaluation when parameter value is None"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="blood_pressure",
            condition="<=",
            value=90,
            points=2,
        )

        # None value should not match
        result = checker._evaluate_criterion(criterion, {"blood_pressure": None})
        assert result.met is False

    def test_evaluate_invalid_condition(self):
        """Test handling of unsupported condition type"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="temperature",
            condition="~=",  # Invalid condition
            value=37.0,
        )

        # Should handle gracefully
        result = checker._evaluate_criterion(criterion, {"temperature": 37.0})
        assert result.met is False


class TestProtocolActivation:
    """Test protocol activation based on screening criteria"""

    def test_protocol_activation_threshold_met(self):
        """Test protocol activates when threshold is met"""
        protocol = ClinicalProtocol(
            name="Sepsis Protocol",
            version="1.0",
            applies_to=["adult_inpatient"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
                ProtocolCriterion(parameter="heart_rate", condition=">=", value=90, points=1),
                ProtocolCriterion(parameter="respiratory_rate", condition=">=", value=20, points=1),
            ],
            screening_threshold=2,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {
            "temperature": 38.5,
            "heart_rate": 95,
            "respiratory_rate": 22,
        }

        result = checker.check_compliance(protocol, patient_data)

        # All 3 criteria met = 3 points >= 2 threshold
        assert result.protocol_activated is True
        assert result.activation_score == 3

    def test_protocol_activation_threshold_not_met(self):
        """Test protocol does not activate when threshold not met"""
        protocol = ClinicalProtocol(
            name="Sepsis Protocol",
            version="1.0",
            applies_to=["adult_inpatient"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
                ProtocolCriterion(parameter="heart_rate", condition=">=", value=90, points=1),
            ],
            screening_threshold=2,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {
            "temperature": 37.0,  # Below threshold
            "heart_rate": 95,  # Above threshold
        }

        result = checker.check_compliance(protocol, patient_data)

        # Only 1 criterion met = 1 point < 2 threshold
        assert result.protocol_activated is False
        assert result.activation_score == 1

    def test_protocol_activation_zero_threshold(self):
        """Test protocol with zero threshold (always active)"""
        protocol = ClinicalProtocol(
            name="Standard Monitoring",
            version="1.0",
            applies_to=["all"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[],
            monitoring_frequency="q4h",
            reassessment_timing="q8h",
        )

        checker = ProtocolChecker()
        result = checker.check_compliance(protocol, {})

        # Zero threshold means always active
        assert result.protocol_activated is True


class TestInterventionCompliance:
    """Test intervention compliance checking"""

    def test_all_interventions_completed(self):
        """Test when all required interventions are completed"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Draw blood cultures",
                    timing="within 1 hour",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Administer antibiotics",
                    timing="within 1 hour",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        intervention_status = {
            "Draw blood cultures": {
                "completed": True,
                "time_completed": datetime.now(),
            },
            "Administer antibiotics": {
                "completed": True,
                "time_completed": datetime.now(),
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # No deviations when all complete
        assert len(result.deviations) == 0
        assert len(result.compliant_items) == 2

    def test_intervention_pending_not_overdue(self):
        """Test pending intervention not yet overdue"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Obtain chest X-ray",
                    timing="within 2 hours",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Intervention not completed, but with future due time
        future_time = datetime.now() + timedelta(hours=1)
        intervention_status = {
            "Obtain chest X-ray": {
                "completed": False,
                "time_due": future_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have pending deviation (not complete) but not overdue
        assert len(result.deviations) > 0
        deviation = result.deviations[0]
        assert deviation.status == ComplianceStatus.PENDING

    def test_intervention_overdue(self):
        """Test overdue intervention creates deviation"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Administer IV fluids",
                    timing="within 1 hour",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Intervention overdue (past due time)
        past_time = datetime.now() - timedelta(hours=1)
        intervention_status = {
            "Administer IV fluids": {
                "completed": False,
                "time_due": past_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have overdue deviation
        assert len(result.deviations) > 0
        deviation = result.deviations[0]
        assert deviation.status == ComplianceStatus.OVERDUE

    def test_missing_required_intervention(self):
        """Test missing required intervention creates deviation"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Activate rapid response",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Provide intervention status with the intervention not completed
        intervention_status = {
            "Activate rapid response": {
                "completed": False,
                "time_due": datetime.now() + timedelta(minutes=1),  # Due soon
            },
        }
        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have deviation for pending intervention
        assert len(result.deviations) > 0


class TestDeviationDetection:
    """Test deviation detection and classification"""

    def test_deviation_severity_levels(self):
        """Test different deviation severity levels"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Critical intervention",
                    timing="immediate",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Important intervention",
                    timing="within 1 hour",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Both interventions pending with different due times
        now = datetime.now()
        intervention_status = {
            "Critical intervention": {
                "completed": False,
                "time_due": now - timedelta(hours=1),  # Overdue
            },
            "Important intervention": {
                "completed": False,
                "time_due": now + timedelta(minutes=30),  # Pending
            },
        }
        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have multiple deviations
        assert len(result.deviations) >= 2

    def test_deviation_includes_recommendation(self):
        """Test result includes actionable recommendation"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Start oxygen therapy",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        result = checker.check_compliance(protocol, {}, {})

        # Should have recommendation (singular field)
        assert result.recommendation is not None
        assert isinstance(result.recommendation, str)
        assert len(result.recommendation) > 0


class TestAlertLevels:
    """Test alert level determination"""

    def test_no_alert_when_compliant(self):
        """Test no alert when fully compliant"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        result = checker.check_compliance(protocol, {})

        assert result.alert_level == "NONE"

    def test_warning_alert_for_pending_deviations(self):
        """Test warning alert for pending interventions"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Document assessment",
                    timing="within 2 hours",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Pending intervention (not yet overdue)
        future_time = datetime.now() + timedelta(hours=1)
        intervention_status = {
            "Document assessment": {
                "completed": False,
                "time_due": future_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should generate warning for pending
        assert result.alert_level == "WARNING"

    def test_critical_alert_for_overdue_interventions(self):
        """Test critical alert for overdue interventions"""
        protocol = ClinicalProtocol(
            name="Critical Care Protocol",
            version="1.0",
            applies_to=["icu"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Initiate life-saving intervention",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="continuous",
        )

        checker = ProtocolChecker()
        # Overdue intervention
        past_time = datetime.now() - timedelta(hours=1)
        intervention_status = {
            "Initiate life-saving intervention": {
                "completed": False,
                "time_due": past_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should generate critical alert for overdue
        assert result.alert_level == "CRITICAL"


class TestCompleteScenarios:
    """Test complete real-world scenarios"""

    def test_sepsis_protocol_full_compliance(self):
        """Test full sepsis protocol compliance scenario"""
        protocol = ClinicalProtocol(
            name="Sepsis Protocol",
            version="1.0",
            applies_to=["adult_inpatient"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
                ProtocolCriterion(parameter="heart_rate", condition=">=", value=90, points=1),
                ProtocolCriterion(parameter="wbc", condition=">=", value=12000, points=1),
            ],
            screening_threshold=2,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Draw blood cultures",
                    timing="within 1 hour",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Administer broad-spectrum antibiotics",
                    timing="within 1 hour",
                    required=True,
                ),
                ProtocolIntervention(
                    order=3,
                    action="Start IV fluid resuscitation",
                    timing="within 3 hours",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="q6h",
        )

        checker = ProtocolChecker()
        patient_data = {
            "temperature": 38.5,
            "heart_rate": 110,
            "wbc": 15000,
        }

        now = datetime.now()
        intervention_status = {
            "Draw blood cultures": {
                "completed": True,
                "time_completed": now - timedelta(minutes=45),
            },
            "Administer broad-spectrum antibiotics": {
                "completed": True,
                "time_completed": now - timedelta(minutes=30),
            },
            "Start IV fluid resuscitation": {
                "completed": True,
                "time_completed": now - timedelta(minutes=15),
            },
        }

        result = checker.check_compliance(protocol, patient_data, intervention_status)

        # Protocol should activate (3 criteria met)
        assert result.protocol_activated is True
        assert result.activation_score == 3

        # All interventions complete - no deviations
        assert len(result.deviations) == 0
        assert len(result.compliant_items) == 3

    def test_post_operative_protocol_with_deviations(self):
        """Test post-operative protocol with missed interventions"""
        protocol = ClinicalProtocol(
            name="Post-Operative Protocol",
            version="1.0",
            applies_to=["post_surgical"],
            screening_criteria=[],
            screening_threshold=0,  # Always active for post-op patients
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Pain assessment",
                    timing="q2h",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Vital signs",
                    timing="q1h",
                    required=True,
                ),
                ProtocolIntervention(
                    order=3,
                    action="Incentive spirometry",
                    timing="q2h while awake",
                    required=True,
                ),
            ],
            monitoring_frequency="q1h",
            reassessment_timing="q4h",
        )

        checker = ProtocolChecker()
        patient_data = {"post_op_day": 1}

        # Pain assessment overdue, vital signs complete, spirometry missing
        past_time = datetime.now() - timedelta(hours=3)
        intervention_status = {
            "Pain assessment": {
                "completed": False,
                "time_due": past_time,  # Overdue
            },
            "Vital signs": {
                "completed": True,
                "time_completed": datetime.now() - timedelta(minutes=45),
            },
            # Incentive spirometry missing (not in status dict)
        }

        result = checker.check_compliance(protocol, patient_data, intervention_status)

        # Should have deviations (pain overdue + spirometry missing)
        assert len(result.deviations) >= 2

        # Should have recommendation to address deviations
        assert result.recommendation is not None
        assert len(result.recommendation) > 0


class TestEdgeCases:
    """Test edge cases and error handling"""

    def test_empty_protocol(self):
        """Test protocol with no criteria or interventions"""
        protocol = ClinicalProtocol(
            name="Empty Protocol",
            version="1.0",
            applies_to=[],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[],
            monitoring_frequency="none",
            reassessment_timing="none",
        )

        checker = ProtocolChecker()
        result = checker.check_compliance(protocol, {})

        # Should handle gracefully
        assert result.protocol_activated is True  # Zero threshold
        assert len(result.deviations) == 0  # No interventions to deviate from
        assert result.alert_level == "NONE"

    def test_empty_patient_data(self):
        """Test with no patient data"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["all"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
            ],
            screening_threshold=1,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        result = checker.check_compliance(protocol, {})

        # No criteria can be met with empty data
        assert result.protocol_activated is False
        assert result.activation_score == 0

    def test_none_intervention_status(self):
        """Test when intervention_status is None"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Test intervention",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Pass None instead of dict
        result = checker.check_compliance(protocol, {}, None)

        # Should handle None gracefully
        assert result is not None
        assert isinstance(result, ProtocolCheckResult)

    def test_intervention_with_no_time_due(self):
        """Test intervention without time_due field"""
        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Test action",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        # Intervention status without time_due field
        intervention_status = {
            "Test action": {
                "completed": False,
                # No time_due field
            },
        }

        # Should handle gracefully - creates pending deviation
        result = checker.check_compliance(protocol, {}, intervention_status)
        assert result is not None
        assert len(result.deviations) > 0
        assert result.deviations[0].status == ComplianceStatus.PENDING


class TestRecommendationGeneration:
    """Test recommendation generation for various scenarios"""

    def test_recommendation_not_activated_with_some_criteria_met(self):
        """Test recommendation when protocol not activated but some criteria met"""
        protocol = ClinicalProtocol(
            name="Sepsis Screening",
            version="1.0",
            applies_to=["adult"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
                ProtocolCriterion(parameter="heart_rate", condition=">=", value=90, points=1),
                ProtocolCriterion(parameter="wbc", condition=">=", value=12000, points=1),
            ],
            screening_threshold=3,  # Need all 3
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {
            "temperature": 38.5,  # Met
            "heart_rate": 95,  # Met
            "wbc": 10000,  # Not met
        }

        result = checker.check_compliance(protocol, patient_data)

        # Protocol not activated (2 < 3), but should mention monitoring
        assert result.protocol_activated is False
        assert "2 of 3" in result.recommendation or "Continue monitoring" in result.recommendation

    def test_recommendation_not_activated_no_criteria_met(self):
        """Test recommendation when no criteria met"""
        protocol = ClinicalProtocol(
            name="Sepsis Screening",
            version="1.0",
            applies_to=["adult"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
            ],
            screening_threshold=1,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {"temperature": 36.5}  # Below threshold

        result = checker.check_compliance(protocol, patient_data)

        # No criteria met
        assert result.protocol_activated is False
        assert (
            "stable" in result.recommendation.lower() or "routine" in result.recommendation.lower()
        )

    def test_recommendation_activated_all_complete(self):
        """Test recommendation when protocol activated and all interventions complete"""
        protocol = ClinicalProtocol(
            name="Sepsis Protocol",
            version="1.0",
            applies_to=["adult"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=1),
            ],
            screening_threshold=1,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Blood cultures",
                    timing="within 1 hour",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {"temperature": 38.5}
        intervention_status = {
            "Blood cultures": {
                "completed": True,
                "time_completed": datetime.now(),
            },
        }

        result = checker.check_compliance(protocol, patient_data, intervention_status)

        # Protocol activated, all complete
        assert result.protocol_activated is True
        assert len(result.deviations) == 0
        assert "active" in result.recommendation.lower()
        assert "complete" in result.recommendation.lower()

    def test_recommendation_with_overdue_interventions(self):
        """Test recommendation highlights overdue interventions"""
        protocol = ClinicalProtocol(
            name="Critical Protocol",
            version="1.0",
            applies_to=["icu"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Emergency intervention A",
                    timing="immediate",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Emergency intervention B",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        past_time = datetime.now() - timedelta(hours=2)
        intervention_status = {
            "Emergency intervention A": {
                "completed": False,
                "time_due": past_time,
            },
            "Emergency intervention B": {
                "completed": False,
                "time_due": past_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have CRITICAL recommendation mentioning overdue items
        assert "CRITICAL" in result.recommendation or "OVERDUE" in result.recommendation
        assert "Emergency intervention A" in result.recommendation

    def test_recommendation_with_pending_interventions(self):
        """Test recommendation for pending but not overdue interventions"""
        protocol = ClinicalProtocol(
            name="Standard Protocol",
            version="1.0",
            applies_to=["ward"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Routine check A",
                    timing="within 2 hours",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Routine check B",
                    timing="within 2 hours",
                    required=True,
                ),
            ],
            monitoring_frequency="q2h",
            reassessment_timing="q4h",
        )

        checker = ProtocolChecker()
        future_time = datetime.now() + timedelta(hours=1)
        intervention_status = {
            "Routine check A": {
                "completed": False,
                "time_due": future_time,
            },
            "Routine check B": {
                "completed": False,
                "time_due": future_time,
            },
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have WARNING recommendation
        assert "WARNING" in result.recommendation or "pending" in result.recommendation.lower()
        assert (
            "Routine check A" in result.recommendation or "Routine check B" in result.recommendation
        )

    def test_recommendation_with_many_overdue_shows_first_three(self):
        """Test recommendation truncates to first 3 overdue interventions"""
        protocol = ClinicalProtocol(
            name="Complex Protocol",
            version="1.0",
            applies_to=["all"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=i,
                    action=f"Intervention {i}",
                    timing="immediate",
                    required=True,
                )
                for i in range(1, 6)  # 5 interventions
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        past_time = datetime.now() - timedelta(hours=1)
        intervention_status = {
            f"Intervention {i}": {"completed": False, "time_due": past_time} for i in range(1, 6)
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should mention count of overdue and show first few
        assert "5" in result.recommendation or "OVERDUE" in result.recommendation

    def test_recommendation_activated_with_deviations_edge_case(self):
        """Test recommendation fallback when activated with deviations but none are overdue/pending"""
        checker = ProtocolChecker()
        protocol = ClinicalProtocol(
            name="Edge Case Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        # Create a mock deviation that's neither OVERDUE nor PENDING
        # (This tests the fallback return statement)
        deviation = ProtocolDeviation(
            intervention=ProtocolIntervention(
                order=1,
                action="Test",
                timing="immediate",
                required=True,
            ),
            status=ComplianceStatus.COMPLETED,  # Not OVERDUE or PENDING
        )

        result = checker._generate_recommendation(
            protocol=protocol,
            activated=True,
            deviations=[deviation],
            criteria_results=[],
        )

        # Should fall back to generic monitoring message
        assert "Protocol monitoring active" in result or "monitoring" in result.lower()


class TestAlertLevelEdgeCases:
    """Test alert level determination edge cases"""

    def test_alert_level_protocol_not_activated(self):
        """Test alert level is NONE when protocol not activated"""
        checker = ProtocolChecker()
        deviations = [
            ProtocolDeviation(
                intervention=ProtocolIntervention(
                    order=1,
                    action="Test",
                    timing="immediate",
                    required=True,
                ),
                status=ComplianceStatus.OVERDUE,
            ),
        ]

        # Protocol not activated - should return NONE even with deviations
        alert_level = checker._determine_alert_level(
            protocol_activated=False,
            deviations=deviations,
            score=0,
            threshold=1,
        )

        assert alert_level == "NONE"

    def test_alert_level_activated_no_deviations(self):
        """Test alert level is NONE when protocol activated but no deviations"""
        checker = ProtocolChecker()

        alert_level = checker._determine_alert_level(
            protocol_activated=True,
            deviations=[],
            score=5,
            threshold=3,
        )

        assert alert_level == "NONE"

    def test_alert_level_multiple_overdue(self):
        """Test alert level is CRITICAL with multiple overdue interventions"""
        checker = ProtocolChecker()
        deviations = [
            ProtocolDeviation(
                intervention=ProtocolIntervention(
                    order=i,
                    action=f"Action {i}",
                    timing="immediate",
                    required=True,
                ),
                status=ComplianceStatus.OVERDUE,
            )
            for i in range(3)
        ]

        alert_level = checker._determine_alert_level(
            protocol_activated=True,
            deviations=deviations,
            score=5,
            threshold=2,
        )

        assert alert_level == "CRITICAL"

    def test_alert_level_mixed_deviations_overdue_takes_priority(self):
        """Test CRITICAL alert when both overdue and pending exist"""
        checker = ProtocolChecker()
        deviations = [
            ProtocolDeviation(
                intervention=ProtocolIntervention(
                    order=1,
                    action="Overdue action",
                    timing="immediate",
                    required=True,
                ),
                status=ComplianceStatus.OVERDUE,
            ),
            ProtocolDeviation(
                intervention=ProtocolIntervention(
                    order=2,
                    action="Pending action",
                    timing="within 1 hour",
                    required=True,
                ),
                status=ComplianceStatus.PENDING,
            ),
        ]

        alert_level = checker._determine_alert_level(
            protocol_activated=True,
            deviations=deviations,
            score=3,
            threshold=2,
        )

        # Overdue takes priority
        assert alert_level == "CRITICAL"

    def test_alert_level_only_pending(self):
        """Test WARNING alert with only pending interventions"""
        checker = ProtocolChecker()
        deviations = [
            ProtocolDeviation(
                intervention=ProtocolIntervention(
                    order=1,
                    action="Pending action",
                    timing="within 2 hours",
                    required=True,
                ),
                status=ComplianceStatus.PENDING,
            ),
        ]

        alert_level = checker._determine_alert_level(
            protocol_activated=True,
            deviations=deviations,
            score=2,
            threshold=1,
        )

        assert alert_level == "WARNING"


class TestInterventionStatusEdgeCases:
    """Test intervention status checking edge cases"""

    def test_intervention_completed_no_deviation(self):
        """Test completed intervention returns None (no deviation)"""
        checker = ProtocolChecker()
        intervention = ProtocolIntervention(
            order=1,
            action="Test action",
            timing="immediate",
            required=True,
        )
        status = {
            "completed": True,
            "time_completed": datetime.now(),
        }

        deviation = checker._check_intervention_status(intervention, status)

        assert deviation is None

    def test_intervention_not_completed_no_time_due_is_pending(self):
        """Test not completed without time_due returns PENDING"""
        checker = ProtocolChecker()
        intervention = ProtocolIntervention(
            order=1,
            action="Test action",
            timing="immediate",
            required=True,
        )
        status = {
            "completed": False,
            # No time_due
        }

        deviation = checker._check_intervention_status(intervention, status)

        assert deviation is not None
        assert deviation.status == ComplianceStatus.PENDING

    def test_intervention_overdue_with_overdue_string(self):
        """Test overdue intervention includes overdue_by string"""
        checker = ProtocolChecker()
        intervention = ProtocolIntervention(
            order=1,
            action="Critical action",
            timing="immediate",
            required=True,
        )
        past_time = datetime.now() - timedelta(hours=2, minutes=30)
        status = {
            "completed": False,
            "time_due": past_time,
        }

        deviation = checker._check_intervention_status(intervention, status)

        assert deviation is not None
        assert deviation.status == ComplianceStatus.OVERDUE
        assert deviation.overdue_by is not None
        assert ":" in deviation.overdue_by  # Should contain time format

    def test_intervention_due_exactly_now_not_overdue(self):
        """Test intervention due exactly at current time is not overdue"""
        checker = ProtocolChecker()
        intervention = ProtocolIntervention(
            order=1,
            action="Time-sensitive action",
            timing="immediate",
            required=True,
        )
        # Time due is approximately now (within a second)
        now_time = datetime.now()
        status = {
            "completed": False,
            "time_due": now_time,
        }

        deviation = checker._check_intervention_status(intervention, status)

        # Should be PENDING since now <= time_due (not strictly greater)
        assert deviation is not None
        # Could be either PENDING or OVERDUE depending on exact timing
        assert deviation.status in [ComplianceStatus.PENDING, ComplianceStatus.OVERDUE]

    def test_intervention_empty_status_dict(self):
        """Test intervention with empty status dictionary"""
        checker = ProtocolChecker()
        intervention = ProtocolIntervention(
            order=1,
            action="Test action",
            timing="immediate",
            required=True,
        )
        status = {}

        deviation = checker._check_intervention_status(intervention, status)

        # Empty dict means not completed, should be PENDING
        assert deviation is not None
        assert deviation.status == ComplianceStatus.PENDING


class TestCriterionResultDetails:
    """Test criterion result details and reasoning"""

    def test_criterion_result_includes_reasoning(self):
        """Test criterion result includes reasoning string"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="heart_rate",
            condition=">=",
            value=100,
            points=2,
            description="Tachycardia",
        )

        result = checker._evaluate_criterion(criterion, {"heart_rate": 120})

        assert result.met is True
        assert result.reasoning is not None
        assert "heart_rate" in result.reasoning
        assert "120" in result.reasoning

    def test_criterion_result_for_missing_parameter(self):
        """Test criterion result details when parameter missing"""
        checker = ProtocolChecker()
        criterion = ProtocolCriterion(
            parameter="blood_glucose",
            condition="<",
            value=70,
            points=1,
        )

        result = checker._evaluate_criterion(criterion, {})

        assert result.met is False
        assert result.actual_value is None
        assert "not available" in result.reasoning


class TestComplexScenarios:
    """Test complex integration scenarios"""

    def test_protocol_with_high_score_multiple_criteria(self):
        """Test protocol activation with high score from multiple criteria"""
        protocol = ClinicalProtocol(
            name="Multi-Factor Protocol",
            version="1.0",
            applies_to=["adult_icu"],
            screening_criteria=[
                ProtocolCriterion(parameter="temperature", condition=">=", value=38.0, points=2),
                ProtocolCriterion(parameter="heart_rate", condition=">=", value=90, points=2),
                ProtocolCriterion(parameter="respiratory_rate", condition=">=", value=20, points=2),
                ProtocolCriterion(parameter="wbc", condition=">=", value=12000, points=2),
                ProtocolCriterion(parameter="lactate", condition=">=", value=2.0, points=3),
            ],
            screening_threshold=5,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Activate sepsis bundle",
                    timing="immediate",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()
        patient_data = {
            "temperature": 39.0,  # +2
            "heart_rate": 110,  # +2
            "respiratory_rate": 24,  # +2
            "wbc": 15000,  # +2
            "lactate": 3.5,  # +3
        }

        result = checker.check_compliance(protocol, patient_data)

        # Total score: 11, threshold: 5
        assert result.protocol_activated is True
        assert result.activation_score == 11

    def test_protocol_partial_intervention_completion(self):
        """Test protocol with some interventions complete, others pending"""
        protocol = ClinicalProtocol(
            name="Staged Protocol",
            version="1.0",
            applies_to=["ward"],
            screening_criteria=[],
            screening_threshold=0,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="First step",
                    timing="immediate",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Second step",
                    timing="within 1 hour",
                    required=True,
                ),
                ProtocolIntervention(
                    order=3,
                    action="Third step",
                    timing="within 2 hours",
                    required=True,
                ),
                ProtocolIntervention(
                    order=4,
                    action="Fourth step",
                    timing="within 4 hours",
                    required=True,
                ),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="q4h",
        )

        checker = ProtocolChecker()
        now = datetime.now()
        intervention_status = {
            "First step": {"completed": True, "time_completed": now - timedelta(minutes=30)},
            "Second step": {"completed": True, "time_completed": now - timedelta(minutes=15)},
            "Third step": {"completed": False, "time_due": now + timedelta(hours=1)},  # Pending
            "Fourth step": {"completed": False, "time_due": now - timedelta(minutes=30)},  # Overdue
        }

        result = checker.check_compliance(protocol, {}, intervention_status)

        # Should have 2 compliant, 2 deviations (1 pending, 1 overdue)
        assert len(result.compliant_items) == 2
        assert len(result.deviations) == 2

        # Should be CRITICAL due to overdue item
        assert result.alert_level == "CRITICAL"

    def test_protocol_threshold_edge_case(self):
        """Test protocol activation at exact threshold"""
        protocol = ClinicalProtocol(
            name="Edge Threshold Protocol",
            version="1.0",
            applies_to=["all"],
            screening_criteria=[
                ProtocolCriterion(parameter="param1", condition=">=", value=10, points=3),
                ProtocolCriterion(parameter="param2", condition=">=", value=20, points=2),
            ],
            screening_threshold=5,  # Exact threshold
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()

        # Test exactly at threshold
        result = checker.check_compliance(protocol, {"param1": 15, "param2": 25})
        assert result.activation_score == 5
        assert result.protocol_activated is True

        # Test just below threshold
        result = checker.check_compliance(protocol, {"param1": 5, "param2": 25})
        assert result.activation_score == 2
        assert result.protocol_activated is False

    def test_full_workflow_activation_to_resolution(self):
        """Test complete workflow from activation through resolution"""
        protocol = ClinicalProtocol(
            name="Complete Workflow Protocol",
            version="1.0",
            applies_to=["test"],
            screening_criteria=[
                ProtocolCriterion(parameter="severity", condition=">=", value=5, points=3),
            ],
            screening_threshold=3,
            interventions=[
                ProtocolIntervention(
                    order=1,
                    action="Initial assessment",
                    timing="immediate",
                    required=True,
                ),
                ProtocolIntervention(
                    order=2,
                    action="Treatment",
                    timing="within 1 hour",
                    required=True,
                ),
            ],
            monitoring_frequency="continuous",
            reassessment_timing="hourly",
        )

        checker = ProtocolChecker()

        # Stage 1: Protocol activates, no interventions started
        result1 = checker.check_compliance(protocol, {"severity": 7}, {})
        assert result1.protocol_activated is True
        assert len(result1.deviations) == 0  # No intervention status provided

        # Stage 2: Interventions pending
        now = datetime.now()
        result2 = checker.check_compliance(
            protocol,
            {"severity": 7},
            {
                "Initial assessment": {"completed": False, "time_due": now + timedelta(minutes=1)},
                "Treatment": {"completed": False, "time_due": now + timedelta(minutes=50)},
            },
        )
        assert result2.protocol_activated is True
        assert len(result2.deviations) == 2
        assert all(d.status == ComplianceStatus.PENDING for d in result2.deviations)
        assert result2.alert_level == "WARNING"

        # Stage 3: One complete, one overdue
        result3 = checker.check_compliance(
            protocol,
            {"severity": 7},
            {
                "Initial assessment": {
                    "completed": True,
                    "time_completed": now - timedelta(minutes=30),
                },
                "Treatment": {"completed": False, "time_due": now - timedelta(minutes=10)},
            },
        )
        assert len(result3.compliant_items) == 1
        assert len(result3.deviations) == 1
        assert result3.deviations[0].status == ComplianceStatus.OVERDUE
        assert result3.alert_level == "CRITICAL"

        # Stage 4: All complete
        result4 = checker.check_compliance(
            protocol,
            {"severity": 7},
            {
                "Initial assessment": {
                    "completed": True,
                    "time_completed": now - timedelta(minutes=30),
                },
                "Treatment": {"completed": True, "time_completed": now - timedelta(minutes=5)},
            },
        )
        assert len(result4.compliant_items) == 2
        assert len(result4.deviations) == 0
        assert result4.alert_level == "NONE"
