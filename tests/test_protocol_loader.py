"""
Test Protocol Loader

Tests the clinical protocol loader that reads JSON protocol definitions.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from pathlib import Path

import pytest

from empathy_healthcare_plugin.monitors.monitoring.protocol_loader import (
    ClinicalProtocol,
    ProtocolCriterion,
    ProtocolIntervention,
    ProtocolLoader,
    load_protocol,
)


class TestProtocolDataclasses:
    """Test dataclass structures"""

    def test_protocol_criterion_creation(self):
        """Test creating a protocol criterion"""
        criterion = ProtocolCriterion(
            parameter="heart_rate",
            condition=">=",
            value=100,
            points=1,
            description="Tachycardia",
        )

        assert criterion.parameter == "heart_rate"
        assert criterion.condition == ">="
        assert criterion.value == 100
        assert criterion.points == 1
        assert criterion.description == "Tachycardia"

    def test_protocol_criterion_defaults(self):
        """Test protocol criterion default values"""
        criterion = ProtocolCriterion(parameter="temp", condition=">=")

        assert criterion.value is None
        assert criterion.points == 0
        assert criterion.description is None

    def test_protocol_intervention_creation(self):
        """Test creating a protocol intervention"""
        intervention = ProtocolIntervention(
            order=1,
            action="Administer oxygen",
            timing="immediately",
            required=True,
            parameters={"flow_rate": "2-4 L/min"},
        )

        assert intervention.order == 1
        assert intervention.action == "Administer oxygen"
        assert intervention.timing == "immediately"
        assert intervention.required is True
        assert intervention.parameters == {"flow_rate": "2-4 L/min"}

    def test_protocol_intervention_defaults(self):
        """Test protocol intervention default values"""
        intervention = ProtocolIntervention(order=1, action="Monitor vitals", timing="hourly")

        assert intervention.required is True
        assert intervention.parameters is None

    def test_clinical_protocol_creation(self):
        """Test creating a clinical protocol"""
        criteria = [ProtocolCriterion(parameter="hr", condition=">=", value=100, points=1)]
        interventions = [ProtocolIntervention(order=1, action="Check vitals", timing="now")]

        protocol = ClinicalProtocol(
            name="Test Protocol",
            version="1.0",
            applies_to=["adult"],
            screening_criteria=criteria,
            screening_threshold=1,
            interventions=interventions,
            monitoring_frequency="hourly",
            reassessment_timing="every 4 hours",
        )

        assert protocol.name == "Test Protocol"
        assert protocol.version == "1.0"
        assert protocol.applies_to == ["adult"]
        assert len(protocol.screening_criteria) == 1
        assert protocol.screening_threshold == 1
        assert len(protocol.interventions) == 1
        assert protocol.monitoring_frequency == "hourly"
        assert protocol.reassessment_timing == "every 4 hours"


class TestProtocolLoader:
    """Test protocol loading functionality"""

    @pytest.fixture
    def temp_protocol_dir(self):
        """Create temporary directory for test protocols"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_protocol_json(self):
        """Sample protocol JSON data"""
        return {
            "protocol_name": "test_protocol",
            "protocol_version": "1.0",
            "applies_to": ["test"],
            "screening_criteria": {
                "criteria": [
                    {
                        "parameter": "heart_rate",
                        "condition": ">=",
                        "value": 100,
                        "points": 1,
                        "description": "Tachycardia",
                    },
                    {
                        "parameter": "systolic_bp",
                        "condition": "<=",
                        "value": 90,
                        "points": 1,
                        "description": "Hypotension",
                    },
                ],
                "threshold": 2,
            },
            "interventions": [
                {
                    "order": 1,
                    "action": "Check vitals",
                    "timing": "immediately",
                    "required": True,
                },
                {
                    "order": 2,
                    "action": "Call physician",
                    "timing": "within 15 minutes",
                    "required": True,
                    "parameters": {"urgency": "high"},
                },
            ],
            "monitoring_requirements": {
                "vitals_frequency": "every 15 minutes",
                "reassessment": "hourly",
            },
            "escalation_criteria": {"if": ["condition_worsens", "no_improvement"]},
            "documentation_requirements": ["vital_signs", "interventions"],
        }

    def test_loader_default_directory(self):
        """Test loader with default protocol directory"""
        loader = ProtocolLoader()

        # Should default to empathy_healthcare_plugin/protocols
        assert loader.protocol_dir.name == "protocols"
        assert "empathy_healthcare_plugin" in str(loader.protocol_dir)

    def test_loader_custom_directory(self, temp_protocol_dir):
        """Test loader with custom protocol directory"""
        loader = ProtocolLoader(str(temp_protocol_dir))

        assert loader.protocol_dir == temp_protocol_dir

    def test_load_protocol_success(self, temp_protocol_dir, sample_protocol_json):
        """Test successfully loading a protocol"""
        # Create protocol file
        protocol_file = temp_protocol_dir / "test_protocol.json"
        with open(protocol_file, "w") as f:
            json.dump(sample_protocol_json, f)

        loader = ProtocolLoader(str(temp_protocol_dir))
        protocol = loader.load_protocol("test_protocol")

        assert protocol.name == "test_protocol"
        assert protocol.version == "1.0"
        assert protocol.applies_to == ["test"]
        assert len(protocol.screening_criteria) == 2
        assert protocol.screening_threshold == 2
        assert len(protocol.interventions) == 2
        assert protocol.monitoring_frequency == "every 15 minutes"
        assert protocol.reassessment_timing == "hourly"
        assert protocol.escalation_criteria == ["condition_worsens", "no_improvement"]
        assert protocol.documentation_requirements == ["vital_signs", "interventions"]

    def test_load_protocol_file_not_found(self, temp_protocol_dir):
        """Test loading non-existent protocol raises FileNotFoundError"""
        loader = ProtocolLoader(str(temp_protocol_dir))

        with pytest.raises(FileNotFoundError) as exc_info:
            loader.load_protocol("nonexistent")

        assert "Protocol not found: nonexistent" in str(exc_info.value)
        assert str(temp_protocol_dir) in str(exc_info.value)

    def test_parse_protocol_criteria(self, sample_protocol_json):
        """Test parsing protocol screening criteria"""
        loader = ProtocolLoader()
        protocol = loader._parse_protocol(sample_protocol_json)

        assert len(protocol.screening_criteria) == 2

        # Check first criterion
        criterion1 = protocol.screening_criteria[0]
        assert criterion1.parameter == "heart_rate"
        assert criterion1.condition == ">="
        assert criterion1.value == 100
        assert criterion1.points == 1
        assert criterion1.description == "Tachycardia"

        # Check second criterion
        criterion2 = protocol.screening_criteria[1]
        assert criterion2.parameter == "systolic_bp"
        assert criterion2.condition == "<="
        assert criterion2.value == 90

    def test_parse_protocol_interventions(self, sample_protocol_json):
        """Test parsing protocol interventions"""
        loader = ProtocolLoader()
        protocol = loader._parse_protocol(sample_protocol_json)

        assert len(protocol.interventions) == 2

        # Check first intervention
        interv1 = protocol.interventions[0]
        assert interv1.order == 1
        assert interv1.action == "Check vitals"
        assert interv1.timing == "immediately"
        assert interv1.required is True
        assert interv1.parameters is None

        # Check second intervention
        interv2 = protocol.interventions[1]
        assert interv2.order == 2
        assert interv2.action == "Call physician"
        assert interv2.parameters == {"urgency": "high"}

    def test_parse_protocol_with_defaults(self):
        """Test parsing protocol with missing optional fields"""
        minimal_protocol = {
            "protocol_name": "minimal",
            "protocol_version": "1.0",
            "screening_criteria": {"criteria": []},
            "interventions": [],
            "monitoring_requirements": {},
        }

        loader = ProtocolLoader()
        protocol = loader._parse_protocol(minimal_protocol)

        assert protocol.name == "minimal"
        assert protocol.version == "1.0"
        assert protocol.applies_to == []
        assert protocol.screening_criteria == []
        assert protocol.screening_threshold == 0
        assert protocol.interventions == []
        assert protocol.monitoring_frequency == "hourly"
        assert protocol.reassessment_timing == "hourly"
        assert protocol.escalation_criteria == []
        assert protocol.documentation_requirements == []

    def test_parse_protocol_saves_raw_data(self, sample_protocol_json):
        """Test that raw protocol data is saved"""
        loader = ProtocolLoader()
        protocol = loader._parse_protocol(sample_protocol_json)

        assert protocol.raw_protocol == sample_protocol_json

    def test_list_available_protocols_empty(self, temp_protocol_dir):
        """Test listing protocols when directory is empty"""
        loader = ProtocolLoader(str(temp_protocol_dir))
        protocols = loader.list_available_protocols()

        assert protocols == []

    def test_list_available_protocols_nonexistent_dir(self):
        """Test listing protocols when directory doesn't exist"""
        loader = ProtocolLoader("/nonexistent/directory")
        protocols = loader.list_available_protocols()

        assert protocols == []

    def test_list_available_protocols(self, temp_protocol_dir, sample_protocol_json):
        """Test listing available protocols"""
        # Create multiple protocol files
        for name in ["protocol_a", "protocol_b", "protocol_c"]:
            protocol_file = temp_protocol_dir / f"{name}.json"
            with open(protocol_file, "w") as f:
                json.dump(sample_protocol_json, f)

        # Create a non-JSON file (should be ignored)
        (temp_protocol_dir / "readme.txt").write_text("Not a protocol")

        loader = ProtocolLoader(str(temp_protocol_dir))
        protocols = loader.list_available_protocols()

        assert len(protocols) == 3
        assert "protocol_a" in protocols
        assert "protocol_b" in protocols
        assert "protocol_c" in protocols
        # Should be sorted
        assert protocols == ["protocol_a", "protocol_b", "protocol_c"]

    def test_validate_protocol_valid(self):
        """Test validating a valid protocol"""
        protocol = ClinicalProtocol(
            name="Valid Protocol",
            version="1.0",
            applies_to=["adult"],
            screening_criteria=[
                ProtocolCriterion(parameter="hr", condition=">=", value=100, points=1)
            ],
            screening_threshold=1,
            interventions=[ProtocolIntervention(order=1, action="Check vitals", timing="now")],
            monitoring_frequency="hourly",
            reassessment_timing="every 4 hours",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert errors == []

    def test_validate_protocol_no_name(self):
        """Test validating protocol without name"""
        protocol = ClinicalProtocol(
            name="",
            version="1.0",
            applies_to=[],
            screening_criteria=[ProtocolCriterion(parameter="hr", condition=">=", value=100)],
            screening_threshold=1,
            interventions=[ProtocolIntervention(order=1, action="Check vitals", timing="now")],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert "Protocol must have a name" in errors

    def test_validate_protocol_no_version(self):
        """Test validating protocol without version"""
        protocol = ClinicalProtocol(
            name="Test",
            version="",
            applies_to=[],
            screening_criteria=[ProtocolCriterion(parameter="hr", condition=">=", value=100)],
            screening_threshold=1,
            interventions=[ProtocolIntervention(order=1, action="Check vitals", timing="now")],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert "Protocol must have a version" in errors

    def test_validate_protocol_no_criteria(self):
        """Test validating protocol without screening criteria"""
        protocol = ClinicalProtocol(
            name="Test",
            version="1.0",
            applies_to=[],
            screening_criteria=[],
            screening_threshold=1,
            interventions=[ProtocolIntervention(order=1, action="Check vitals", timing="now")],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert "Protocol must have screening criteria" in errors

    def test_validate_protocol_no_interventions(self):
        """Test validating protocol without interventions"""
        protocol = ClinicalProtocol(
            name="Test",
            version="1.0",
            applies_to=[],
            screening_criteria=[ProtocolCriterion(parameter="hr", condition=">=", value=100)],
            screening_threshold=1,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert "Protocol must have interventions" in errors

    def test_validate_protocol_duplicate_intervention_orders(self):
        """Test validating protocol with duplicate intervention orders"""
        protocol = ClinicalProtocol(
            name="Test",
            version="1.0",
            applies_to=[],
            screening_criteria=[ProtocolCriterion(parameter="hr", condition=">=", value=100)],
            screening_threshold=1,
            interventions=[
                ProtocolIntervention(order=1, action="First", timing="now"),
                ProtocolIntervention(order=1, action="Duplicate", timing="now"),
                ProtocolIntervention(order=2, action="Second", timing="later"),
            ],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        assert "Intervention orders must be unique" in errors

    def test_validate_protocol_multiple_errors(self):
        """Test validating protocol with multiple errors"""
        protocol = ClinicalProtocol(
            name="",
            version="",
            applies_to=[],
            screening_criteria=[],
            screening_threshold=1,
            interventions=[],
            monitoring_frequency="hourly",
            reassessment_timing="hourly",
        )

        loader = ProtocolLoader()
        errors = loader.validate_protocol(protocol)

        # Should have 4 errors
        assert len(errors) == 4
        assert "Protocol must have a name" in errors
        assert "Protocol must have a version" in errors
        assert "Protocol must have screening criteria" in errors
        assert "Protocol must have interventions" in errors


class TestLoadProtocolConvenienceFunction:
    """Test the standalone load_protocol convenience function"""

    @pytest.fixture
    def temp_protocol_dir(self):
        """Create temporary directory for test protocols"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_protocol_json(self):
        """Sample protocol JSON data"""
        return {
            "protocol_name": "convenience_test",
            "protocol_version": "1.0",
            "applies_to": ["test"],
            "screening_criteria": {
                "criteria": [{"parameter": "hr", "condition": ">=", "value": 100, "points": 1}],
                "threshold": 1,
            },
            "interventions": [
                {"order": 1, "action": "Test action", "timing": "now", "required": True}
            ],
            "monitoring_requirements": {
                "vitals_frequency": "hourly",
                "reassessment": "hourly",
            },
        }

    def test_load_protocol_with_custom_dir(self, temp_protocol_dir, sample_protocol_json):
        """Test convenience function with custom directory"""
        # Create protocol file
        protocol_file = temp_protocol_dir / "convenience_test.json"
        with open(protocol_file, "w") as f:
            json.dump(sample_protocol_json, f)

        protocol = load_protocol("convenience_test", str(temp_protocol_dir))

        assert protocol.name == "convenience_test"
        assert protocol.version == "1.0"
        assert len(protocol.screening_criteria) == 1
        assert len(protocol.interventions) == 1

    def test_load_protocol_default_dir(self):
        """Test convenience function with default directory"""
        # This will use the actual protocols directory
        # We can test with the sepsis protocol that exists
        protocol = load_protocol("sepsis")

        assert protocol.name == "sepsis_screening_and_management"
        assert protocol.version == "2024.1"
        assert len(protocol.screening_criteria) > 0
        assert len(protocol.interventions) > 0


class TestRealProtocolFiles:
    """Test loading actual protocol files from the project"""

    def test_load_sepsis_protocol(self):
        """Test loading the actual sepsis protocol"""
        loader = ProtocolLoader()
        protocol = loader.load_protocol("sepsis")

        assert protocol.name == "sepsis_screening_and_management"
        assert protocol.version == "2024.1"
        assert "adult_inpatient" in protocol.applies_to

        # Check screening criteria (qSOFA)
        assert len(protocol.screening_criteria) == 3
        assert protocol.screening_threshold == 2

        # Should have criteria for BP, RR, and mental status
        params = [c.parameter for c in protocol.screening_criteria]
        assert "systolic_bp" in params
        assert "respiratory_rate" in params
        assert "mental_status" in params

        # Check interventions
        assert len(protocol.interventions) >= 5
        # Should have blood cultures, antibiotics, lactate, fluids
        actions = [i.action for i in protocol.interventions]
        assert "obtain_blood_cultures" in actions
        assert "administer_broad_spectrum_antibiotics" in actions
        assert "measure_lactate" in actions

        # Check monitoring requirements
        assert protocol.monitoring_frequency == "every_15_minutes"

        # Validate the protocol
        errors = loader.validate_protocol(protocol)
        assert errors == []

    def test_list_all_real_protocols(self):
        """Test listing all available real protocols"""
        loader = ProtocolLoader()
        protocols = loader.list_available_protocols()

        # Should have at least sepsis, respiratory, cardiac, post_operative
        assert len(protocols) >= 4
        assert "sepsis" in protocols
        assert "respiratory" in protocols
        assert "cardiac" in protocols
        assert "post_operative" in protocols

    def test_all_real_protocols_are_valid(self):
        """Test that all real protocol files are valid"""
        loader = ProtocolLoader()
        protocols = loader.list_available_protocols()

        for protocol_name in protocols:
            protocol = loader.load_protocol(protocol_name)
            errors = loader.validate_protocol(protocol)
            assert errors == [], f"Protocol {protocol_name} has validation errors: {errors}"
