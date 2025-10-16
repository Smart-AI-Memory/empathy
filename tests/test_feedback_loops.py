"""
Tests for Feedback Loop Detection

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
from empathy_os.feedback_loops import (
    FeedbackLoopDetector,
    FeedbackLoop,
    LoopType,
    LoopPolarity
)


class TestFeedbackLoop:
    """Test FeedbackLoop dataclass"""

    def test_feedback_loop_creation(self):
        """Test creating a feedback loop"""
        loop = FeedbackLoop(
            loop_id="test_loop",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Test virtuous cycle",
            components=["trust", "success"]
        )

        assert loop.loop_id == "test_loop"
        assert loop.loop_type == LoopType.REINFORCING
        assert loop.polarity == LoopPolarity.VIRTUOUS
        assert len(loop.components) == 2
        assert loop.strength == 0.5  # Default


class TestFeedbackLoopDetector:
    """Test FeedbackLoopDetector"""

    def test_initialization(self):
        """Test detector initializes with standard loops"""
        detector = FeedbackLoopDetector()

        assert len(detector.detected_loops) == 3  # R1, R2, B1
        loop_ids = [loop.loop_id for loop in detector.detected_loops]
        assert "R1_trust_building" in loop_ids
        assert "R2_trust_erosion" in loop_ids
        assert "B1_quality_control" in loop_ids

    def test_detect_virtuous_cycle(self):
        """Test detecting virtuous cycle (trust building)"""
        detector = FeedbackLoopDetector()

        # Simulate history with increasing trust and success (need 4+ points for acceleration detection)
        history = [
            {"trust": 0.3, "success": True},
            {"trust": 0.4, "success": True},
            {"trust": 0.55, "success": True},
            {"trust": 0.75, "success": True},  # Accelerating
        ]

        is_virtuous = detector.detect_virtuous_cycle(history)
        assert is_virtuous == True

    def test_detect_virtuous_cycle_insufficient_data(self):
        """Test virtuous cycle detection with insufficient data"""
        detector = FeedbackLoopDetector()

        history = [{"trust": 0.5, "success": True}]
        is_virtuous = detector.detect_virtuous_cycle(history)
        assert is_virtuous == False

    def test_detect_virtuous_cycle_declining_trust(self):
        """Test virtuous cycle detection with declining trust"""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.7, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.5, "success": True},  # Declining
        ]

        is_virtuous = detector.detect_virtuous_cycle(history)
        assert is_virtuous == False

    def test_detect_vicious_cycle(self):
        """Test detecting vicious cycle (trust erosion)"""
        detector = FeedbackLoopDetector()

        # Simulate history with decreasing trust and failures (need 4+ points for acceleration)
        history = [
            {"trust": 0.7, "success": False},
            {"trust": 0.6, "success": False},
            {"trust": 0.4, "success": False},
            {"trust": 0.2, "success": False},  # Accelerating down
        ]

        is_vicious = detector.detect_vicious_cycle(history)
        assert is_vicious == True

    def test_detect_vicious_cycle_insufficient_data(self):
        """Test vicious cycle detection with insufficient data"""
        detector = FeedbackLoopDetector()

        history = [{"trust": 0.5, "success": False}]
        is_vicious = detector.detect_vicious_cycle(history)
        assert is_vicious == False

    def test_detect_vicious_cycle_improving(self):
        """Test vicious cycle detection when things are improving"""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.3, "success": False},
            {"trust": 0.5, "success": True},
            {"trust": 0.7, "success": True},  # Improving
        ]

        is_vicious = detector.detect_vicious_cycle(history)
        assert is_vicious == False

    def test_detect_active_loop_insufficient_data(self):
        """Test active loop detection with insufficient data"""
        detector = FeedbackLoopDetector()

        history = [{"trust": 0.5}]
        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] is None
        assert result["loop_strength"] == 0.0
        assert result["trend"] == "insufficient_data"

    def test_detect_active_loop_virtuous(self):
        """Test active loop detection for virtuous cycle"""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.3, "success": True},
            {"trust": 0.45, "success": True},
            {"trust": 0.65, "success": True},
            {"trust": 0.85, "success": True}  # Strong acceleration
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "R1_trust_building"
        assert result["loop_type"] == "reinforcing_virtuous"
        assert result["trend"] == "amplifying_positive"
        assert result["loop_strength"] > 0

    def test_detect_active_loop_vicious(self):
        """Test active loop detection for vicious cycle"""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.7, "success": False},
            {"trust": 0.5, "success": False},
            {"trust": 0.3, "success": False},
            {"trust": 0.1, "success": False}
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "R2_trust_erosion"
        assert result["loop_type"] == "reinforcing_vicious"
        assert result["trend"] == "amplifying_negative"
        assert "INTERVENTION NEEDED" in result["recommendation"]

    def test_detect_active_loop_balancing(self):
        """Test active loop detection for balancing loop"""
        detector = FeedbackLoopDetector()

        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.55, "success": False},
            {"trust": 0.5, "success": True},
            {"trust": 0.52, "success": True}
        ]

        result = detector.detect_active_loop(history)

        assert result["dominant_loop"] == "B1_quality_control"
        assert result["loop_type"] == "balancing"
        assert result["trend"] == "stabilizing"

    def test_get_intervention_recommendations(self):
        """Test getting intervention recommendations"""
        detector = FeedbackLoopDetector()

        recommendations = detector.get_intervention_recommendations("R1_trust_building")

        assert len(recommendations) > 0
        assert "celebrate_wins" in recommendations or "increase_transparency" in recommendations

    def test_get_intervention_recommendations_invalid_loop(self):
        """Test getting recommendations for invalid loop"""
        detector = FeedbackLoopDetector()

        recommendations = detector.get_intervention_recommendations("invalid_loop")
        assert len(recommendations) == 0

    def test_register_custom_loop(self):
        """Test registering custom feedback loop"""
        detector = FeedbackLoopDetector()

        initial_count = len(detector.detected_loops)

        custom_loop = FeedbackLoop(
            loop_id="custom_loop",
            loop_type=LoopType.REINFORCING,
            polarity=LoopPolarity.VIRTUOUS,
            description="Custom test loop",
            components=["test"]
        )

        detector.register_custom_loop(custom_loop)

        assert len(detector.detected_loops) == initial_count + 1
        assert custom_loop in detector.detected_loops

    def test_get_all_loops(self):
        """Test getting all registered loops"""
        detector = FeedbackLoopDetector()

        all_loops = detector.get_all_loops()

        assert len(all_loops) == 3  # R1, R2, B1
        assert all(isinstance(loop, FeedbackLoop) for loop in all_loops)

    def test_reset(self):
        """Test resetting detector"""
        detector = FeedbackLoopDetector()

        # Add custom loop
        custom_loop = FeedbackLoop(
            loop_id="temp_loop",
            loop_type=LoopType.BALANCING,
            polarity=LoopPolarity.NEUTRAL,
            description="Temporary",
            components=[]
        )
        detector.register_custom_loop(custom_loop)

        assert len(detector.detected_loops) == 4

        # Reset
        detector.reset()

        # Should be back to 3 standard loops
        assert len(detector.detected_loops) == 3
        loop_ids = [loop.loop_id for loop in detector.detected_loops]
        assert "temp_loop" not in loop_ids


class TestTrendCalculation:
    """Test trend calculation helper"""

    def test_increasing_trend(self):
        """Test trend calculation for increasing values"""
        detector = FeedbackLoopDetector()

        values = [1.0, 2.0, 3.0, 4.0]
        trend = detector._calculate_trend(values)

        assert trend > 0  # Positive trend

    def test_decreasing_trend(self):
        """Test trend calculation for decreasing values"""
        detector = FeedbackLoopDetector()

        values = [4.0, 3.0, 2.0, 1.0]
        trend = detector._calculate_trend(values)

        assert trend < 0  # Negative trend

    def test_stable_trend(self):
        """Test trend calculation for stable values"""
        detector = FeedbackLoopDetector()

        values = [2.0, 2.0, 2.0, 2.0]
        trend = detector._calculate_trend(values)

        assert trend == pytest.approx(0.0, abs=0.01)  # Near zero

    def test_trend_insufficient_data(self):
        """Test trend calculation with insufficient data"""
        detector = FeedbackLoopDetector()

        values = [1.0]
        trend = detector._calculate_trend(values)

        assert trend == 0.0

    def test_detect_virtuous_cycle_low_success_rate(self):
        """Test virtuous cycle detection with low success rate (should return False)"""
        detector = FeedbackLoopDetector()

        # History with INCREASING trust but LOW success rate (< 60%)
        # This should pass the trust check but fail on line 253
        history = [
            {"trust": 0.4, "success": True},
            {"trust": 0.5, "success": False},
            {"trust": 0.6, "success": False},
            {"trust": 0.7, "success": False},
        ]

        result = detector.detect_virtuous_cycle(history)

        # Should return False due to low success rate (only 25% success)
        assert result is False

    def test_detect_vicious_cycle_low_failure_rate(self):
        """Test vicious cycle detection with low failure rate (should return False)"""
        detector = FeedbackLoopDetector()

        # History with DECREASING trust but LOW failure rate (< 40%)
        # This should pass the trust check but fail on line 304
        history = [
            {"trust": 0.7, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.5, "success": True},
            {"trust": 0.4, "success": False},
        ]

        result = detector.detect_vicious_cycle(history)

        # Should return False due to low failure rate (only 25% failure)
        assert result is False

    def test_calculate_trend_zero_denominator(self):
        """Test trend calculation with zero denominator (all same x values)"""
        detector = FeedbackLoopDetector()

        # All same values should result in zero slope
        values = [5.0, 5.0]
        trend = detector._calculate_trend(values)

        # Should return 0.0 when denominator is 0
        assert trend == 0.0
