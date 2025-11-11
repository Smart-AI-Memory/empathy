"""
Protocol Loader

Loads clinical pathway protocols from JSON files.

This is like loading linting configs - protocols define the rules.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class ProtocolCriterion:
    """A single criterion in a protocol"""

    parameter: str
    condition: str  # "<=", ">=", "==", "!=", "altered", etc.
    value: Any | None = None
    points: int = 0
    description: str | None = None


@dataclass
class ProtocolIntervention:
    """A required intervention"""

    order: int
    action: str
    timing: str
    required: bool = True
    parameters: dict[str, Any] | None = None


@dataclass
class ClinicalProtocol:
    """
    Clinical pathway protocol.

    This is the "linting config" for healthcare - defines the rules.
    """

    name: str
    version: str
    applies_to: list[str]

    # Screening criteria (when to activate protocol)
    screening_criteria: list[ProtocolCriterion]
    screening_threshold: int

    # Required interventions (what to do)
    interventions: list[ProtocolIntervention]

    # Monitoring requirements
    monitoring_frequency: str
    reassessment_timing: str

    # Escalation criteria (when to call for help)
    escalation_criteria: list[str] | None = None

    # Documentation requirements
    documentation_requirements: list[str] | None = None

    # Raw protocol data
    raw_protocol: dict[str, Any] | None = None


class ProtocolLoader:
    """
    Loads clinical protocols from JSON files.

    Similar to loading .eslintrc or pyproject.toml - we're loading
    the protocol configuration.
    """

    def __init__(self, protocol_directory: str | None = None):
        if protocol_directory:
            self.protocol_dir = Path(protocol_directory)
        else:
            # Default to protocols directory in plugin
            plugin_dir = Path(__file__).parent.parent.parent
            self.protocol_dir = plugin_dir / "protocols"

    def load_protocol(self, protocol_name: str) -> ClinicalProtocol:
        """
        Load protocol by name.

        Args:
            protocol_name: Name of protocol (e.g., "sepsis", "post_operative")

        Returns:
            ClinicalProtocol object

        Example:
            >>> loader = ProtocolLoader()
            >>> protocol = loader.load_protocol("sepsis")
            >>> print(f"Loaded: {protocol.name} v{protocol.version}")
        """
        protocol_file = self.protocol_dir / f"{protocol_name}.json"

        if not protocol_file.exists():
            raise FileNotFoundError(
                f"Protocol not found: {protocol_name}\n" f"Looked in: {self.protocol_dir}"
            )

        with open(protocol_file) as f:
            data = json.load(f)

        return self._parse_protocol(data)

    def _parse_protocol(self, data: dict[str, Any]) -> ClinicalProtocol:
        """Parse protocol JSON into ClinicalProtocol object"""

        # Parse screening criteria
        screening_data = data.get("screening_criteria", {})
        criteria = []

        for crit in screening_data.get("criteria", []):
            criteria.append(
                ProtocolCriterion(
                    parameter=crit["parameter"],
                    condition=crit["condition"],
                    value=crit.get("value"),
                    points=crit.get("points", 0),
                    description=crit.get("description"),
                )
            )

        # Parse interventions
        interventions = []
        for interv in data.get("interventions", []):
            interventions.append(
                ProtocolIntervention(
                    order=interv["order"],
                    action=interv["action"],
                    timing=interv["timing"],
                    required=interv.get("required", True),
                    parameters=interv.get("parameters"),
                )
            )

        # Parse monitoring requirements
        monitoring = data.get("monitoring_requirements", {})

        return ClinicalProtocol(
            name=data["protocol_name"],
            version=data["protocol_version"],
            applies_to=data.get("applies_to", []),
            screening_criteria=criteria,
            screening_threshold=screening_data.get("threshold", 0),
            interventions=interventions,
            monitoring_frequency=monitoring.get("vitals_frequency", "hourly"),
            reassessment_timing=monitoring.get("reassessment", "hourly"),
            escalation_criteria=data.get("escalation_criteria", {}).get("if", []),
            documentation_requirements=data.get("documentation_requirements", []),
            raw_protocol=data,
        )

    def list_available_protocols(self) -> list[str]:
        """List all available protocols"""
        if not self.protocol_dir.exists():
            return []

        protocols = []
        for file in self.protocol_dir.glob("*.json"):
            protocols.append(file.stem)

        return sorted(protocols)

    def validate_protocol(self, protocol: ClinicalProtocol) -> list[str]:
        """
        Validate protocol structure.

        Returns list of validation errors (empty if valid)
        """
        errors = []

        if not protocol.name:
            errors.append("Protocol must have a name")

        if not protocol.version:
            errors.append("Protocol must have a version")

        if not protocol.screening_criteria:
            errors.append("Protocol must have screening criteria")

        if not protocol.interventions:
            errors.append("Protocol must have interventions")

        # Check intervention order
        orders = [i.order for i in protocol.interventions]
        if len(orders) != len(set(orders)):
            errors.append("Intervention orders must be unique")

        return errors


def load_protocol(protocol_name: str, protocol_dir: str | None = None) -> ClinicalProtocol:
    """
    Convenience function to load a protocol.

    Args:
        protocol_name: Name of protocol
        protocol_dir: Optional custom protocol directory

    Returns:
        ClinicalProtocol object

    Example:
        >>> protocol = load_protocol("sepsis")
        >>> print(f"{protocol.name}: {len(protocol.interventions)} interventions")
    """
    loader = ProtocolLoader(protocol_dir)
    return loader.load_protocol(protocol_name)
