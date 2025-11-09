"""
Tests for Sensor Data Parsers

Tests the healthcare data parsers that convert various sensor formats
(FHIR, simple JSON) into standardized vital sign readings.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
from datetime import datetime

import pytest

from empathy_healthcare_plugin.monitors.monitoring.sensor_parsers import (
    BaseSensorParser,
    FHIRObservationParser,
    SensorParserFactory,
    SimpleJSONParser,
    VitalSignReading,
    VitalSignType,
    normalize_vitals,
    parse_sensor_data,
)


class TestVitalSignReading:
    """Test VitalSignReading dataclass"""

    def test_vital_sign_reading_creation(self):
        """Test creating a VitalSignReading"""
        timestamp = datetime.now()
        reading = VitalSignReading(
            vital_type=VitalSignType.HEART_RATE,
            value=85,
            unit="bpm",
            timestamp=timestamp,
            source="bedside_monitor",
            patient_id="12345",
            quality="good",
            metadata={"device_id": "MON-001"},
        )

        assert reading.vital_type == VitalSignType.HEART_RATE
        assert reading.value == 85
        assert reading.unit == "bpm"
        assert reading.timestamp == timestamp
        assert reading.source == "bedside_monitor"
        assert reading.patient_id == "12345"
        assert reading.quality == "good"
        assert reading.metadata["device_id"] == "MON-001"

    def test_vital_sign_reading_to_dict(self):
        """Test converting VitalSignReading to dictionary"""
        timestamp = datetime(2024, 1, 20, 14, 30, 0)
        reading = VitalSignReading(
            vital_type=VitalSignType.OXYGEN_SATURATION,
            value=95,
            unit="%",
            timestamp=timestamp,
            source="pulse_oximeter",
            patient_id="54321",
            quality="good",
        )

        result = reading.to_dict()

        assert result["vital_type"] == "oxygen_saturation"
        assert result["value"] == 95
        assert result["unit"] == "%"
        assert result["timestamp"] == timestamp.isoformat()
        assert result["source"] == "pulse_oximeter"
        assert result["patient_id"] == "54321"
        assert result["quality"] == "good"
        assert result["metadata"] == {}

    def test_vital_sign_reading_optional_fields(self):
        """Test VitalSignReading with optional fields None"""
        reading = VitalSignReading(
            vital_type=VitalSignType.TEMPERATURE,
            value=98.6,
            unit="°F",
            timestamp=datetime.now(),
            source="thermometer",
            patient_id="99999",
        )

        assert reading.quality is None
        assert reading.metadata is None

        result = reading.to_dict()
        assert result["quality"] is None
        assert result["metadata"] == {}


class TestFHIRObservationParser:
    """Test FHIR Observation parser"""

    def test_parse_fhir_heart_rate(self):
        """Test parsing FHIR heart rate observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {
                "coding": [
                    {"system": "http://loinc.org", "code": "8867-4", "display": "Heart rate"}
                ]
            },
            "valueQuantity": {"value": 72, "unit": "beats/min"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/12345"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        reading = readings[0]
        assert reading.vital_type == VitalSignType.HEART_RATE
        assert reading.value == 72
        assert reading.unit == "beats/min"
        assert reading.patient_id == "12345"
        assert reading.source == "fhir_observation"
        assert reading.metadata["loinc_code"] == "8867-4"

    def test_parse_fhir_blood_pressure_systolic(self):
        """Test parsing FHIR systolic BP observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8480-6"}]},
            "valueQuantity": {"value": 120, "unit": "mmHg"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/67890"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.BLOOD_PRESSURE
        assert readings[0].value == 120
        assert readings[0].unit == "mmHg"

    def test_parse_fhir_respiratory_rate(self):
        """Test parsing FHIR respiratory rate observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "9279-1"}]},
            "valueQuantity": {"value": 16, "unit": "/min"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/11111"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.RESPIRATORY_RATE
        assert readings[0].value == 16

    def test_parse_fhir_temperature(self):
        """Test parsing FHIR temperature observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8310-5"}]},
            "valueQuantity": {"value": 37.0, "unit": "°C"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/22222"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.TEMPERATURE
        assert readings[0].value == 37.0
        assert readings[0].unit == "°C"

    def test_parse_fhir_oxygen_saturation(self):
        """Test parsing FHIR oxygen saturation observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "2708-6"}]},
            "valueQuantity": {"value": 98, "unit": "%"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/33333"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.OXYGEN_SATURATION
        assert readings[0].value == 98

    def test_parse_fhir_pain_score(self):
        """Test parsing FHIR pain score observation"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "38208-5"}]},
            "valueQuantity": {"value": 3, "unit": "0-10"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/44444"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.PAIN_SCORE
        assert readings[0].value == 3

    def test_parse_fhir_invalid_json(self):
        """Test parsing invalid JSON returns empty list"""
        parser = FHIRObservationParser()
        readings = parser.parse("not valid json{}")

        assert readings == []

    def test_parse_fhir_wrong_resource_type(self):
        """Test parsing wrong resource type returns empty list"""
        fhir_data = {"resourceType": "Patient", "name": [{"family": "Doe"}]}

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert readings == []

    def test_parse_fhir_unknown_loinc_code(self):
        """Test parsing unknown LOINC code returns empty list"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "99999-9"}]},
            "valueQuantity": {"value": 100},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/12345"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert readings == []

    def test_parse_fhir_no_loinc_coding(self):
        """Test parsing observation without LOINC coding"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://snomed.info/sct", "code": "12345"}]},
            "valueQuantity": {"value": 100},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/12345"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert readings == []

    def test_parse_fhir_missing_timestamp(self):
        """Test parsing FHIR without timestamp uses current time"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4"}]},
            "valueQuantity": {"value": 75, "unit": "bpm"},
            "subject": {"reference": "Patient/12345"},
        }

        parser = FHIRObservationParser()
        readings = parser.parse(json.dumps(fhir_data))

        assert len(readings) == 1
        # Timestamp should be set to current time
        assert isinstance(readings[0].timestamp, datetime)


class TestSimpleJSONParser:
    """Test Simple JSON parser"""

    def test_parse_simple_json_heart_rate(self):
        """Test parsing simple JSON with heart rate"""
        data = {
            "patient_id": "12345",
            "timestamp": "2024-01-20T14:30:00Z",
            "vitals": {"hr": 85},
        }

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 1
        reading = readings[0]
        assert reading.vital_type == VitalSignType.HEART_RATE
        assert reading.value == 85
        assert reading.unit == "bpm"
        assert reading.patient_id == "12345"
        assert reading.source == "manual_entry"

    def test_parse_simple_json_multiple_vitals(self):
        """Test parsing simple JSON with multiple vitals"""
        data = {
            "patient_id": "67890",
            "timestamp": "2024-01-20T14:30:00Z",
            "vitals": {
                "hr": 72,
                "systolic_bp": 120,
                "diastolic_bp": 80,
                "respiratory_rate": 16,
                "temp_f": 98.6,
                "o2_sat": 98,
            },
        }

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 6

        # Check heart rate
        hr_reading = next(r for r in readings if r.vital_type == VitalSignType.HEART_RATE)
        assert hr_reading.value == 72
        assert hr_reading.unit == "bpm"

        # Check BP readings
        bp_readings = [r for r in readings if r.vital_type == VitalSignType.BLOOD_PRESSURE]
        assert len(bp_readings) == 2
        assert any(r.value == 120 for r in bp_readings)  # Systolic
        assert any(r.value == 80 for r in bp_readings)  # Diastolic

        # Check temperature
        temp_reading = next(r for r in readings if r.vital_type == VitalSignType.TEMPERATURE)
        assert temp_reading.value == 98.6
        assert temp_reading.unit == "°F"

        # Check O2 sat
        o2_reading = next(r for r in readings if r.vital_type == VitalSignType.OXYGEN_SATURATION)
        assert o2_reading.value == 98
        assert o2_reading.unit == "%"

    def test_parse_simple_json_alternate_keys(self):
        """Test parsing simple JSON with alternate key names"""
        data = {
            "patient_id": "11111",
            "timestamp": "2024-01-20T14:30:00Z",
            "vitals": {
                "heart_rate": 80,  # Alternate for 'hr'
                "rr": 18,  # Alternate for 'respiratory_rate'
                "spo2": 97,  # Alternate for 'o2_sat'
                "temp_c": 37.2,  # Celsius instead of Fahrenheit
            },
        }

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 4

        hr_reading = next(r for r in readings if r.vital_type == VitalSignType.HEART_RATE)
        assert hr_reading.value == 80

        rr_reading = next(r for r in readings if r.vital_type == VitalSignType.RESPIRATORY_RATE)
        assert rr_reading.value == 18

        temp_reading = next(r for r in readings if r.vital_type == VitalSignType.TEMPERATURE)
        assert temp_reading.value == 37.2
        assert temp_reading.unit == "°C"

    def test_parse_simple_json_pain_and_mental_status(self):
        """Test parsing mental status and pain score"""
        data = {
            "patient_id": "99999",
            "timestamp": "2024-01-20T14:30:00Z",
            "vitals": {"mental_status": "alert", "pain": 2},
        }

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 2

        mental_reading = next(r for r in readings if r.vital_type == VitalSignType.MENTAL_STATUS)
        assert mental_reading.value == "alert"
        assert mental_reading.unit == "text"

        pain_reading = next(r for r in readings if r.vital_type == VitalSignType.PAIN_SCORE)
        assert pain_reading.value == 2
        assert pain_reading.unit == "0-10"

    def test_parse_simple_json_invalid_json(self):
        """Test parsing invalid JSON returns empty list"""
        parser = SimpleJSONParser()
        readings = parser.parse("not valid json")

        assert readings == []

    def test_parse_simple_json_missing_patient_id(self):
        """Test parsing without patient_id uses 'unknown'"""
        data = {"timestamp": "2024-01-20T14:30:00Z", "vitals": {"hr": 75}}

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 1
        assert readings[0].patient_id == "unknown"

    def test_parse_simple_json_missing_timestamp(self):
        """Test parsing without timestamp uses current time"""
        data = {"patient_id": "12345", "vitals": {"hr": 75}}

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert len(readings) == 1
        assert isinstance(readings[0].timestamp, datetime)

    def test_parse_simple_json_unknown_vital_keys(self):
        """Test parsing with unknown vital keys ignores them"""
        data = {
            "patient_id": "12345",
            "vitals": {"hr": 75, "unknown_vital": 999, "another_unknown": "test"},
        }

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        # Should only parse the known 'hr' vital
        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.HEART_RATE

    def test_parse_simple_json_empty_vitals(self):
        """Test parsing with empty vitals dict"""
        data = {"patient_id": "12345", "timestamp": "2024-01-20T14:30:00Z", "vitals": {}}

        parser = SimpleJSONParser()
        readings = parser.parse(json.dumps(data))

        assert readings == []


class TestSensorParserFactory:
    """Test SensorParserFactory"""

    def test_create_fhir_parser(self):
        """Test creating FHIR parser"""
        parser = SensorParserFactory.create("fhir")
        assert isinstance(parser, FHIRObservationParser)

    def test_create_simple_json_parser(self):
        """Test creating simple JSON parser"""
        parser = SensorParserFactory.create("simple_json")
        assert isinstance(parser, SimpleJSONParser)

    def test_create_unsupported_format(self):
        """Test creating parser with unsupported format raises error"""
        with pytest.raises(ValueError) as exc_info:
            SensorParserFactory.create("hl7")

        assert "Unsupported sensor format: hl7" in str(exc_info.value)
        assert "fhir" in str(exc_info.value)
        assert "simple_json" in str(exc_info.value)


class TestParseSensorDataFunction:
    """Test parse_sensor_data convenience function"""

    def test_parse_sensor_data_simple_json(self):
        """Test parse_sensor_data with simple_json format"""
        data = {
            "patient_id": "12345",
            "timestamp": "2024-01-20T14:30:00Z",
            "vitals": {"hr": 85, "o2_sat": 95},
        }

        readings = parse_sensor_data(json.dumps(data), "simple_json")

        assert len(readings) == 2
        assert any(r.vital_type == VitalSignType.HEART_RATE for r in readings)
        assert any(r.vital_type == VitalSignType.OXYGEN_SATURATION for r in readings)

    def test_parse_sensor_data_fhir(self):
        """Test parse_sensor_data with FHIR format"""
        fhir_data = {
            "resourceType": "Observation",
            "code": {"coding": [{"system": "http://loinc.org", "code": "8867-4"}]},
            "valueQuantity": {"value": 72, "unit": "bpm"},
            "effectiveDateTime": "2024-01-20T14:30:00Z",
            "subject": {"reference": "Patient/12345"},
        }

        readings = parse_sensor_data(json.dumps(fhir_data), "fhir")

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.HEART_RATE

    def test_parse_sensor_data_default_format(self):
        """Test parse_sensor_data defaults to simple_json"""
        data = {"patient_id": "12345", "vitals": {"hr": 75}}

        readings = parse_sensor_data(json.dumps(data))

        assert len(readings) == 1
        assert readings[0].vital_type == VitalSignType.HEART_RATE


class TestNormalizeVitals:
    """Test normalize_vitals function"""

    def test_normalize_heart_rate(self):
        """Test normalizing heart rate reading"""
        reading = VitalSignReading(
            vital_type=VitalSignType.HEART_RATE,
            value=85,
            unit="bpm",
            timestamp=datetime.now(),
            source="monitor",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["hr"] == 85

    def test_normalize_blood_pressure(self):
        """Test normalizing blood pressure readings"""
        systolic = VitalSignReading(
            vital_type=VitalSignType.BLOOD_PRESSURE,
            value=120,
            unit="mmHg",
            timestamp=datetime.now(),
            source="monitor",
            patient_id="12345",
        )

        diastolic = VitalSignReading(
            vital_type=VitalSignType.BLOOD_PRESSURE,
            value=60,  # <= 60 threshold to be treated as diastolic
            unit="mmHg",
            timestamp=datetime.now(),
            source="monitor",
            patient_id="12345",
        )

        normalized = normalize_vitals([systolic, diastolic])

        assert normalized["systolic_bp"] == 120
        assert normalized["diastolic_bp"] == 60

    def test_normalize_respiratory_rate(self):
        """Test normalizing respiratory rate"""
        reading = VitalSignReading(
            vital_type=VitalSignType.RESPIRATORY_RATE,
            value=16,
            unit="/min",
            timestamp=datetime.now(),
            source="monitor",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["respiratory_rate"] == 16

    def test_normalize_temperature_fahrenheit(self):
        """Test normalizing temperature in Fahrenheit"""
        reading = VitalSignReading(
            vital_type=VitalSignType.TEMPERATURE,
            value=98.6,
            unit="°F",
            timestamp=datetime.now(),
            source="thermometer",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["temp_f"] == 98.6

    def test_normalize_temperature_celsius(self):
        """Test normalizing temperature in Celsius"""
        reading = VitalSignReading(
            vital_type=VitalSignType.TEMPERATURE,
            value=37.0,
            unit="°C",
            timestamp=datetime.now(),
            source="thermometer",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["temp_c"] == 37.0

    def test_normalize_oxygen_saturation(self):
        """Test normalizing oxygen saturation"""
        reading = VitalSignReading(
            vital_type=VitalSignType.OXYGEN_SATURATION,
            value=98,
            unit="%",
            timestamp=datetime.now(),
            source="pulse_ox",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["o2_sat"] == 98

    def test_normalize_mental_status(self):
        """Test normalizing mental status"""
        reading = VitalSignReading(
            vital_type=VitalSignType.MENTAL_STATUS,
            value="alert",
            unit="text",
            timestamp=datetime.now(),
            source="assessment",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["mental_status"] == "alert"

    def test_normalize_pain_score(self):
        """Test normalizing pain score"""
        reading = VitalSignReading(
            vital_type=VitalSignType.PAIN_SCORE,
            value=3,
            unit="0-10",
            timestamp=datetime.now(),
            source="assessment",
            patient_id="12345",
        )

        normalized = normalize_vitals([reading])

        assert normalized["pain_score"] == 3

    def test_normalize_multiple_vitals(self):
        """Test normalizing multiple vital readings"""
        readings = [
            VitalSignReading(
                VitalSignType.HEART_RATE, 85, "bpm", datetime.now(), "monitor", "12345"
            ),
            VitalSignReading(
                VitalSignType.OXYGEN_SATURATION, 98, "%", datetime.now(), "monitor", "12345"
            ),
            VitalSignReading(
                VitalSignType.RESPIRATORY_RATE, 16, "/min", datetime.now(), "monitor", "12345"
            ),
            VitalSignReading(
                VitalSignType.TEMPERATURE, 98.6, "°F", datetime.now(), "monitor", "12345"
            ),
        ]

        normalized = normalize_vitals(readings)

        assert normalized["hr"] == 85
        assert normalized["o2_sat"] == 98
        assert normalized["respiratory_rate"] == 16
        assert normalized["temp_f"] == 98.6

    def test_normalize_empty_list(self):
        """Test normalizing empty list returns empty dict"""
        normalized = normalize_vitals([])

        assert normalized == {}


class TestBaseSensorParser:
    """Test BaseSensorParser abstract class"""

    def test_base_parser_not_implemented(self):
        """Test that base parser parse() raises NotImplementedError"""
        parser = BaseSensorParser()

        with pytest.raises(NotImplementedError):
            parser.parse("some data")
