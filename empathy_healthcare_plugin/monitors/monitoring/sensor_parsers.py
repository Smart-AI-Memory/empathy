"""
Sensor Data Parsers

Parses sensor data from various formats (HL7, FHIR, manual entry).

This is like parsing linter output - converting various formats to standard structure.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class VitalSignType(Enum):
    """Types of vital signs"""

    HEART_RATE = "heart_rate"
    BLOOD_PRESSURE = "blood_pressure"
    RESPIRATORY_RATE = "respiratory_rate"
    TEMPERATURE = "temperature"
    OXYGEN_SATURATION = "oxygen_saturation"
    MENTAL_STATUS = "mental_status"
    PAIN_SCORE = "pain_score"


@dataclass
class VitalSignReading:
    """
    Standardized vital sign reading.

    This is the universal format - all parsers convert to this.
    """

    vital_type: VitalSignType
    value: Any
    unit: str
    timestamp: datetime
    source: str  # "bedside_monitor", "manual_entry", "wearable"
    patient_id: str
    quality: str | None = None  # "good", "poor", "artifact"
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "vital_type": self.vital_type.value,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "patient_id": self.patient_id,
            "quality": self.quality,
            "metadata": self.metadata or {},
        }


class BaseSensorParser:
    """Base class for sensor data parsers"""

    def parse(self, data: str) -> list[VitalSignReading]:
        """Parse sensor data into standardized readings"""
        raise NotImplementedError


class FHIRObservationParser(BaseSensorParser):
    """
    Parse FHIR Observation resources.

    FHIR is standard for healthcare data exchange.
    """

    # LOINC codes for common vitals
    LOINC_MAPPINGS = {
        "8867-4": VitalSignType.HEART_RATE,
        "8480-6": VitalSignType.BLOOD_PRESSURE,  # Systolic
        "8462-4": VitalSignType.BLOOD_PRESSURE,  # Diastolic
        "9279-1": VitalSignType.RESPIRATORY_RATE,
        "8310-5": VitalSignType.TEMPERATURE,
        "2708-6": VitalSignType.OXYGEN_SATURATION,
        "38208-5": VitalSignType.PAIN_SCORE,
    }

    def parse(self, data: str) -> list[VitalSignReading]:
        """Parse FHIR Observation JSON"""

        try:
            observation = json.loads(data)
        except json.JSONDecodeError:
            return []

        if observation.get("resourceType") != "Observation":
            return []

        readings = []

        # Extract LOINC code
        code = observation.get("code", {})
        loinc_code = None

        for coding in code.get("coding", []):
            if coding.get("system") == "http://loinc.org":
                loinc_code = coding.get("code")
                break

        if not loinc_code or loinc_code not in self.LOINC_MAPPINGS:
            return []

        vital_type = self.LOINC_MAPPINGS[loinc_code]

        # Extract value
        value_qty = observation.get("valueQuantity", {})
        value = value_qty.get("value")
        unit = value_qty.get("unit", "")

        # Extract timestamp
        timestamp_str = observation.get("effectiveDateTime")
        timestamp = (
            datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if timestamp_str
            else datetime.now()
        )

        # Extract patient ID
        subject = observation.get("subject", {})
        patient_id = subject.get("reference", "").split("/")[-1]

        reading = VitalSignReading(
            vital_type=vital_type,
            value=value,
            unit=unit,
            timestamp=timestamp,
            source="fhir_observation",
            patient_id=patient_id,
            metadata={"loinc_code": loinc_code},
        )

        readings.append(reading)

        return readings


class SimpleJSONParser(BaseSensorParser):
    """
    Parse simple JSON format for manual entry or simulation.

    Example:
    {
        "patient_id": "12345",
        "timestamp": "2024-01-20T14:30:00Z",
        "vitals": {
            "hr": 110,
            "systolic_bp": 95,
            "diastolic_bp": 60,
            "respiratory_rate": 24,
            "temp_f": 101.5,
            "o2_sat": 94
        }
    }
    """

    VITAL_MAPPINGS = {
        "hr": (VitalSignType.HEART_RATE, "bpm"),
        "heart_rate": (VitalSignType.HEART_RATE, "bpm"),
        "systolic_bp": (VitalSignType.BLOOD_PRESSURE, "mmHg"),
        "diastolic_bp": (VitalSignType.BLOOD_PRESSURE, "mmHg"),
        "bp": (VitalSignType.BLOOD_PRESSURE, "mmHg"),
        "respiratory_rate": (VitalSignType.RESPIRATORY_RATE, "/min"),
        "rr": (VitalSignType.RESPIRATORY_RATE, "/min"),
        "temp_f": (VitalSignType.TEMPERATURE, "°F"),
        "temp_c": (VitalSignType.TEMPERATURE, "°C"),
        "temperature": (VitalSignType.TEMPERATURE, "°F"),
        "o2_sat": (VitalSignType.OXYGEN_SATURATION, "%"),
        "spo2": (VitalSignType.OXYGEN_SATURATION, "%"),
        "mental_status": (VitalSignType.MENTAL_STATUS, "text"),
        "pain": (VitalSignType.PAIN_SCORE, "0-10"),
    }

    def parse(self, data: str) -> list[VitalSignReading]:
        """Parse simple JSON format"""

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            return []

        patient_id = parsed.get("patient_id", "unknown")
        timestamp_str = parsed.get("timestamp")
        timestamp = (
            datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            if timestamp_str
            else datetime.now()
        )

        vitals = parsed.get("vitals", {})

        readings = []

        for key, value in vitals.items():
            if key in self.VITAL_MAPPINGS:
                vital_type, unit = self.VITAL_MAPPINGS[key]

                reading = VitalSignReading(
                    vital_type=vital_type,
                    value=value,
                    unit=unit,
                    timestamp=timestamp,
                    source="manual_entry",
                    patient_id=patient_id,
                )

                readings.append(reading)

        return readings


class SensorParserFactory:
    """Factory for creating appropriate sensor parser"""

    _parsers = {"fhir": FHIRObservationParser, "simple_json": SimpleJSONParser}

    @classmethod
    def create(cls, format_type: str) -> BaseSensorParser:
        """Create parser for specified format"""
        parser_class = cls._parsers.get(format_type)

        if not parser_class:
            raise ValueError(
                f"Unsupported sensor format: {format_type}. "
                f"Supported: {', '.join(cls._parsers.keys())}"
            )

        return parser_class()


def parse_sensor_data(data: str, format_type: str = "simple_json") -> list[VitalSignReading]:
    """
    Convenience function to parse sensor data.

    Args:
        data: Raw sensor data (JSON string)
        format_type: "fhir" or "simple_json"

    Returns:
        List of VitalSignReading objects

    Example:
        >>> data = '{"patient_id": "12345", "vitals": {"hr": 110}}'
        >>> readings = parse_sensor_data(data, "simple_json")
        >>> print(f"HR: {readings[0].value} {readings[0].unit}")
    """
    parser = SensorParserFactory.create(format_type)
    return parser.parse(data)


def normalize_vitals(readings: list[VitalSignReading]) -> dict[str, Any]:
    """
    Normalize vital sign readings into protocol-checkable format.

    Takes list of VitalSignReading and converts to dict for protocol checker.

    Args:
        readings: List of vital sign readings

    Returns:
        Dictionary with normalized values for protocol checking

    Example:
        >>> normalized = normalize_vitals(readings)
        >>> # Returns: {"hr": 110, "systolic_bp": 95, "respiratory_rate": 24}
    """
    normalized = {}

    for reading in readings:
        if reading.vital_type == VitalSignType.HEART_RATE:
            normalized["hr"] = reading.value

        elif reading.vital_type == VitalSignType.BLOOD_PRESSURE:
            # Determine if systolic or diastolic based on value
            if reading.value > 60:  # Likely systolic
                normalized["systolic_bp"] = reading.value
            else:  # Likely diastolic
                normalized["diastolic_bp"] = reading.value

        elif reading.vital_type == VitalSignType.RESPIRATORY_RATE:
            normalized["respiratory_rate"] = reading.value

        elif reading.vital_type == VitalSignType.TEMPERATURE:
            if reading.unit == "°F":
                normalized["temp_f"] = reading.value
            elif reading.unit == "°C":
                normalized["temp_c"] = reading.value

        elif reading.vital_type == VitalSignType.OXYGEN_SATURATION:
            normalized["o2_sat"] = reading.value

        elif reading.vital_type == VitalSignType.MENTAL_STATUS:
            normalized["mental_status"] = reading.value

        elif reading.vital_type == VitalSignType.PAIN_SCORE:
            normalized["pain_score"] = reading.value

    return normalized
