"""
Emergence Detection for AI-Human Collaboration

Detects emergent properties in AI-human collaboration - system-level behaviors
that arise from component interactions but aren't properties of components.

Based on systems thinking principles from Donella Meadows and Peter Senge.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class EmergentProperty:
    """
    An emergent property discovered in the system

    Emergent properties are behaviors or patterns that arise from the
    interactions of system components but cannot be predicted from
    the components alone.
    """

    property_type: str  # "norm", "pattern", "behavior", "capability"
    description: str
    first_observed: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0  # 0.0-1.0
    evidence: list[dict[str, Any]] = field(default_factory=list)
    components_involved: list[str] = field(default_factory=list)


class EmergenceDetector:
    """
    Detects emergent properties in AI-human collaboration

    Emergent properties are system-level behaviors that arise from
    component interactions but aren't properties of the components themselves.

    Examples:
    - Team norms that developed organically (not prescribed)
    - Collaboration patterns that emerged from repeated interactions
    - Shared understanding that goes beyond individual knowledge
    - Trust dynamics that affect system behavior

    Based on systems thinking:
    - Whole is greater than sum of parts
    - Properties emerge at system level
    - Cannot reduce to component analysis

    Example:
        >>> detector = EmergenceDetector()
        >>> baseline = {"trust": 0.3, "interactions": 10}
        >>> current = {"trust": 0.8, "interactions": 50, "shared_patterns": 5}
        >>> score = detector.measure_emergence(baseline, current)
        >>> print(f"Emergence score: {score:.2f}")
    """

    def __init__(self):
        """Initialize EmergenceDetector with tracking structures"""
        self.detected_properties: list[EmergentProperty] = []
        self.baseline_metrics: dict[str, Any] = {}

    def detect_emergent_norms(
        self, team_interactions: list[dict[str, Any]]
    ) -> list[EmergentProperty]:
        """
        Detect team norms that emerged organically

        Analyzes interaction history to identify behavioral patterns that:
        1. Were not explicitly programmed or prescribed
        2. Emerged from repeated interactions
        3. Are now consistently followed by team members

        Args:
            team_interactions: List of interaction records with metadata

        Returns:
            List of detected emergent norms

        Example:
            >>> interactions = [
            ...     {"type": "help_request", "response_time": 5},
            ...     {"type": "help_request", "response_time": 3},
            ...     {"type": "help_request", "response_time": 4}
            ... ]
            >>> norms = detector.detect_emergent_norms(interactions)
        """
        norms: list[EmergentProperty] = []

        if not team_interactions:
            return norms

        # Detect response time norms
        response_times = [
            i.get("response_time", 0) for i in team_interactions if "response_time" in i
        ]

        if len(response_times) >= 3:
            avg_response = sum(response_times) / len(response_times)
            consistency = self._calculate_consistency(response_times)

            if consistency > 0.7:  # High consistency indicates norm
                norm = EmergentProperty(
                    property_type="norm",
                    description=f"Response time norm emerged: ~{avg_response:.1f} minutes",
                    confidence=consistency,
                    evidence=[{"response_times": response_times}],
                    components_involved=["ai_agent", "human_user"],
                )
                norms.append(norm)

        # Detect communication style norms
        communication_patterns = self._analyze_communication_patterns(team_interactions)
        if communication_patterns:
            for pattern_name, pattern_data in communication_patterns.items():
                if pattern_data["frequency"] > 0.6:  # Appears in >60% of interactions
                    norm = EmergentProperty(
                        property_type="norm",
                        description=f"Communication pattern emerged: {pattern_name}",
                        confidence=pattern_data["frequency"],
                        evidence=[pattern_data],
                        components_involved=["communication_style"],
                    )
                    norms.append(norm)

        self.detected_properties.extend(norms)
        return norms

    def measure_emergence(self, baseline: dict[str, Any], current: dict[str, Any]) -> float:
        """
        Quantify emergence by comparing baseline to current state

        Measures how much new system-level properties have emerged that
        weren't present in the baseline state.

        Args:
            baseline: Initial system state metrics
            current: Current system state metrics

        Returns:
            Emergence score (0.0-1.0), where:
            - 0.0: No emergence (system unchanged)
            - 0.5: Moderate emergence (some new properties)
            - 1.0: High emergence (significant new system capabilities)

        Example:
            >>> baseline = {"trust": 0.3, "interactions": 10}
            >>> current = {"trust": 0.8, "interactions": 50, "patterns": 5}
            >>> score = detector.measure_emergence(baseline, current)
        """
        emergence_score = 0.0
        max_score = 0.0

        # Measure growth in key metrics
        if "trust" in baseline and "trust" in current:
            trust_growth = (current["trust"] - baseline["trust"]) / max(baseline["trust"], 0.1)
            emergence_score += min(trust_growth, 1.0) * 0.3
            max_score += 0.3

        # Measure new capabilities
        baseline_keys = set(baseline.keys())
        current_keys = set(current.keys())
        new_capabilities = current_keys - baseline_keys

        if new_capabilities:
            capability_score = len(new_capabilities) / max(len(baseline_keys), 1)
            emergence_score += min(capability_score, 1.0) * 0.3
            max_score += 0.3

        # Measure interaction complexity growth
        if "interactions" in baseline and "interactions" in current:
            if baseline["interactions"] > 0:
                interaction_ratio = current["interactions"] / baseline["interactions"]
                complexity_score = min((interaction_ratio - 1.0) / 4.0, 1.0)  # Normalize
                emergence_score += complexity_score * 0.2
                max_score += 0.2

        # Measure pattern development
        if "shared_patterns" in current:
            pattern_score = min(current["shared_patterns"] / 10.0, 1.0)
            emergence_score += pattern_score * 0.2
            max_score += 0.2

        # Normalize to 0-1 range
        if max_score > 0:
            return min(emergence_score / max_score, 1.0)
        return 0.0

    def detect_emergent_capabilities(
        self, historical_states: list[dict[str, Any]]
    ) -> list[EmergentProperty]:
        """
        Detect new capabilities that emerged over time

        Analyzes historical system states to identify capabilities that:
        1. Weren't present initially
        2. Emerged through system evolution
        3. Enable new behaviors

        Args:
            historical_states: List of system states over time

        Returns:
            List of emergent capabilities detected
        """
        if len(historical_states) < 2:
            return []

        capabilities: list[EmergentProperty] = []
        initial_state = historical_states[0]

        # Track capability development
        for state in historical_states[1:]:
            new_keys = set(state.keys()) - set(initial_state.keys())

            for key in new_keys:
                capability = EmergentProperty(
                    property_type="capability",
                    description=f"New capability emerged: {key}",
                    confidence=0.8,
                    evidence=[{"state": state, "timestamp": state.get("timestamp")}],
                    components_involved=["system"],
                )
                capabilities.append(capability)

        self.detected_properties.extend(capabilities)
        return capabilities

    def _calculate_consistency(self, values: list[float]) -> float:
        """
        Calculate consistency of a set of values (0.0-1.0)

        Uses coefficient of variation: lower variation = higher consistency
        """
        if not values or len(values) < 2:
            return 0.0

        mean = sum(values) / len(values)
        if mean == 0:
            return 0.0

        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        cv = std_dev / mean  # Coefficient of variation

        # Convert to consistency score (inverse of variation)
        consistency = max(0.0, 1.0 - min(cv, 1.0))
        return consistency

    def _analyze_communication_patterns(
        self, interactions: list[dict[str, Any]]
    ) -> dict[str, dict[str, Any]]:
        """
        Analyze communication patterns in interactions

        Returns dict of pattern_name -> {frequency, examples}
        """
        patterns: dict[str, dict[str, Any]] = {}
        total_interactions = len(interactions)

        if total_interactions == 0:
            return patterns

        # Detect clarifying questions pattern
        clarifying_count = sum(1 for i in interactions if i.get("type") == "clarifying_question")
        if clarifying_count > 0:
            patterns["clarifying_questions"] = {
                "frequency": clarifying_count / total_interactions,
                "count": clarifying_count,
                "examples": [i for i in interactions if i.get("type") == "clarifying_question"][:3],
            }

        # Detect proactive suggestions pattern
        proactive_count = sum(1 for i in interactions if i.get("type") == "proactive_suggestion")
        if proactive_count > 0:
            patterns["proactive_suggestions"] = {
                "frequency": proactive_count / total_interactions,
                "count": proactive_count,
                "examples": [i for i in interactions if i.get("type") == "proactive_suggestion"][
                    :3
                ],
            }

        return patterns

    def get_detected_properties(self, property_type: str | None = None) -> list[EmergentProperty]:
        """
        Get all detected emergent properties, optionally filtered by type

        Args:
            property_type: Optional filter ("norm", "pattern", "behavior", "capability")

        Returns:
            List of emergent properties
        """
        if property_type:
            return [p for p in self.detected_properties if p.property_type == property_type]
        return self.detected_properties

    def reset(self):
        """Reset detector state"""
        self.detected_properties = []
        self.baseline_metrics = {}
