"""
Feedback Loop Detection for AI-Human Collaboration

Detects and analyzes reinforcing and balancing feedback loops in AI-human
collaboration based on systems thinking (Meadows, Senge).

Feedback loops are circular causal relationships that either amplify
(reinforcing) or stabilize (balancing) system behaviors.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class LoopType(Enum):
    """Types of feedback loops"""

    REINFORCING = "reinforcing"  # Amplifying, can be virtuous or vicious
    BALANCING = "balancing"  # Stabilizing, seeks equilibrium


class LoopPolarity(Enum):
    """Polarity of reinforcing loops"""

    VIRTUOUS = "virtuous"  # Positive reinforcing loop (good spiral)
    VICIOUS = "vicious"  # Negative reinforcing loop (bad spiral)
    NEUTRAL = "neutral"  # Balancing loops


@dataclass
class FeedbackLoop:
    """
    A detected feedback loop in the system

    Feedback loops are circular causal chains where:
    A -> B -> C -> A (with delays and polarities)
    """

    loop_id: str
    loop_type: LoopType
    polarity: LoopPolarity
    description: str
    components: List[str]  # Variables involved in the loop
    strength: float = 0.5  # 0.0-1.0, how strong is the loop effect
    detected_at: datetime = field(default_factory=datetime.now)
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    intervention_points: List[str] = field(default_factory=list)


class FeedbackLoopDetector:
    """
    Detects reinforcing and balancing feedback loops in AI-human collaboration

    Based on systems thinking (Meadows, Senge):

    **Common Loops:**
    - R1: Trust building loop (virtuous reinforcing)
      - Success → Trust ↑ → Willingness to delegate ↑ → More success
    - R2: Trust erosion loop (vicious reinforcing)
      - Failure → Trust ↓ → Micromanagement ↑ → More failures
    - B1: Quality control loop (balancing)
      - Error rate ↑ → Guardrails ↑ → Error rate ↓

    **Reinforcing Loops (R):**
    - Amplify change (exponential growth or decay)
    - Can be virtuous (good spiral) or vicious (bad spiral)
    - Examples: compound interest, viral growth, panic

    **Balancing Loops (B):**
    - Seek equilibrium
    - Stabilize systems
    - Examples: thermostat, supply-demand, homeostasis

    Example:
        >>> detector = FeedbackLoopDetector()
        >>> history = [
        ...     {"trust": 0.5, "success": True},
        ...     {"trust": 0.6, "success": True},
        ...     {"trust": 0.7, "success": True}
        ... ]
        >>> loops = detector.detect_active_loop(history)
        >>> print(loops["dominant_loop"])
    """

    def __init__(self):
        """Initialize FeedbackLoopDetector"""
        self.detected_loops: List[FeedbackLoop] = []
        self._initialize_standard_loops()

    def _initialize_standard_loops(self):
        """Initialize standard loops from systems thinking literature"""
        # R1: Trust building loop (virtuous)
        trust_building = FeedbackLoop(
            loop_id="R1_trust_building",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Trust building virtuous cycle: Success → Trust ↑ → Delegation ↑ → More Success",
            components=["trust", "success_rate", "delegation_level"],
            intervention_points=["celebrate_wins", "increase_transparency"],
        )

        # R2: Trust erosion loop (vicious)
        trust_erosion = FeedbackLoop(
            loop_id="R2_trust_erosion",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VICIOUS,
            description="Trust erosion vicious cycle: Failure → Trust ↓ → Micromanagement ↑ → More Failures",
            components=["trust", "failure_rate", "oversight_level"],
            intervention_points=["break_cycle", "rebuild_confidence", "adjust_scope"],
        )

        # B1: Quality control loop (balancing)
        quality_control = FeedbackLoop(
            loop_id="B1_quality_control",
            loop_type=LoopType.BALANCING,
            polarity=LoopPolarity.NEUTRAL,
            description="Quality control: Error Rate ↑ → Guardrails ↑ → Error Rate ↓",
            components=["error_rate", "guardrail_strength", "intervention_frequency"],
            intervention_points=["adjust_guardrails", "calibrate_sensitivity"],
        )

        # Add to detected loops
        self.detected_loops.extend([trust_building, trust_erosion, quality_control])

    def detect_active_loop(self, session_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze session history for active feedback loops

        Examines trends in trust, success rate, and collaboration metrics
        to determine which feedback loop is currently dominant.

        Args:
            session_history: List of session state snapshots over time

        Returns:
            Dict with:
            - dominant_loop: The most active loop
            - loop_strength: How strongly the loop is operating (0-1)
            - trend: "amplifying" or "stabilizing"
            - recommendation: Suggested intervention

        Example:
            >>> history = [
            ...     {"trust": 0.5, "success_rate": 0.6},
            ...     {"trust": 0.6, "success_rate": 0.7},
            ...     {"trust": 0.7, "success_rate": 0.8}
            ... ]
            >>> result = detector.detect_active_loop(history)
        """
        if len(session_history) < 2:
            return {
                "dominant_loop": None,
                "loop_strength": 0.0,
                "trend": "insufficient_data",
                "recommendation": "Continue collaboration to gather data",
            }

        # Analyze trust trend
        trust_values = [s.get("trust", 0.5) for s in session_history]
        trust_trend = self._calculate_trend(trust_values)

        # Analyze success rate trend
        success_indicators = [1 if s.get("success", False) else 0 for s in session_history]
        success_rate = (
            sum(success_indicators) / len(success_indicators) if success_indicators else 0.5
        )

        # Determine active loop
        if trust_trend > 0.1 and success_rate > 0.6:
            # Trust building virtuous cycle active
            dominant_loop = self._get_loop_by_id("R1_trust_building")
            return {
                "dominant_loop": "R1_trust_building",
                "loop_type": "reinforcing_virtuous",
                "loop_strength": min(trust_trend * success_rate, 1.0),
                "trend": "amplifying_positive",
                "recommendation": "Maintain momentum. Consider increasing delegation.",
                "details": dominant_loop,
            }

        elif trust_trend < -0.1 and success_rate < 0.4:
            # Trust erosion vicious cycle active
            dominant_loop = self._get_loop_by_id("R2_trust_erosion")
            return {
                "dominant_loop": "R2_trust_erosion",
                "loop_type": "reinforcing_vicious",
                "loop_strength": min(abs(trust_trend) * (1 - success_rate), 1.0),
                "trend": "amplifying_negative",
                "recommendation": "INTERVENTION NEEDED: Break the cycle. Reduce scope, rebuild confidence.",
                "details": dominant_loop,
            }

        else:
            # Quality control balancing loop active
            dominant_loop = self._get_loop_by_id("B1_quality_control")
            return {
                "dominant_loop": "B1_quality_control",
                "loop_type": "balancing",
                "loop_strength": 0.5,
                "trend": "stabilizing",
                "recommendation": "System stable. Monitor for reinforcing loop activation.",
                "details": dominant_loop,
            }

    def detect_virtuous_cycle(self, history: List[Dict[str, Any]]) -> bool:
        """
        Detect reinforcing positive feedback (virtuous cycle)

        A virtuous cycle is present when:
        1. Trust is increasing
        2. Success rate is high (>60%)
        3. Trend is accelerating (not just linear)

        Args:
            history: Session history with trust and success metrics

        Returns:
            True if virtuous cycle detected, False otherwise

        Example:
            >>> history = [
            ...     {"trust": 0.5, "success": True},
            ...     {"trust": 0.6, "success": True},
            ...     {"trust": 0.75, "success": True}  # Accelerating
            ... ]
            >>> detector.detect_virtuous_cycle(history)
            True
        """
        if len(history) < 3:
            return False

        trust_values = [h.get("trust", 0.5) for h in history]
        success_indicators = [1 if h.get("success", False) else 0 for h in history]

        # Check trust is increasing
        trust_trend = self._calculate_trend(trust_values)
        if trust_trend <= 0:
            return False

        # Check success rate is high
        success_rate = sum(success_indicators) / len(success_indicators)
        if success_rate < 0.6:
            return False

        # Check for acceleration (reinforcing behavior)
        recent_trust_trend = self._calculate_trend(trust_values[-3:])
        overall_trust_trend = self._calculate_trend(trust_values)

        is_accelerating = recent_trust_trend > overall_trust_trend

        return is_accelerating

    def detect_vicious_cycle(self, history: List[Dict[str, Any]]) -> bool:
        """
        Detect reinforcing negative feedback (vicious cycle)

        A vicious cycle is present when:
        1. Trust is decreasing
        2. Failure rate is high (>40%)
        3. Trend is accelerating downward

        Args:
            history: Session history with trust and success metrics

        Returns:
            True if vicious cycle detected, False otherwise

        Example:
            >>> history = [
            ...     {"trust": 0.7, "success": False},
            ...     {"trust": 0.5, "success": False},
            ...     {"trust": 0.3, "success": False}  # Accelerating down
            ... ]
            >>> detector.detect_vicious_cycle(history)
            True
        """
        if len(history) < 3:
            return False

        trust_values = [h.get("trust", 0.5) for h in history]
        failure_indicators = [0 if h.get("success", True) else 1 for h in history]

        # Check trust is decreasing
        trust_trend = self._calculate_trend(trust_values)
        if trust_trend >= 0:
            return False

        # Check failure rate is high
        failure_rate = sum(failure_indicators) / len(failure_indicators)
        if failure_rate < 0.4:
            return False

        # Check for acceleration (reinforcing behavior)
        recent_trust_trend = self._calculate_trend(trust_values[-3:])
        overall_trust_trend = self._calculate_trend(trust_values)

        is_accelerating_down = recent_trust_trend < overall_trust_trend

        return is_accelerating_down

    def get_intervention_recommendations(self, loop_id: str) -> List[str]:
        """
        Get recommended interventions for a specific loop

        Args:
            loop_id: ID of the loop (e.g., "R1_trust_building")

        Returns:
            List of intervention recommendations

        Example:
            >>> recommendations = detector.get_intervention_recommendations("R2_trust_erosion")
            >>> print(recommendations)
            ['break_cycle', 'rebuild_confidence', 'adjust_scope']
        """
        loop = self._get_loop_by_id(loop_id)
        if loop:
            return loop.intervention_points
        return []

    def _calculate_trend(self, values: List[float]) -> float:
        """
        Calculate trend direction and magnitude

        Uses simple linear regression slope as trend indicator.

        Returns:
            Positive value: increasing trend
            Negative value: decreasing trend
            Near zero: stable
        """
        if len(values) < 2:
            return 0.0

        n = len(values)
        x = list(range(n))
        x_mean = sum(x) / n
        y_mean = sum(values) / n

        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        slope = numerator / denominator
        return slope

    def _get_loop_by_id(self, loop_id: str) -> Optional[FeedbackLoop]:
        """Get a loop by its ID"""
        for loop in self.detected_loops:
            if loop.loop_id == loop_id:
                return loop
        return None

    def register_custom_loop(self, loop: FeedbackLoop):
        """
        Register a custom feedback loop for detection

        Args:
            loop: FeedbackLoop instance to register
        """
        self.detected_loops.append(loop)

    def get_all_loops(self) -> List[FeedbackLoop]:
        """Get all registered feedback loops"""
        return self.detected_loops

    def reset(self):
        """Reset detector and reinitialize standard loops"""
        self.detected_loops = []
        self._initialize_standard_loops()
