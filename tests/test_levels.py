"""
Tests for individual empathy level classes

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
from empathy_os import (
    Level1Reactive,
    Level2Guided,
    Level3Proactive,
    Level4Anticipatory,
    Level5Systems
)


class TestLevel1Reactive:
    """Test Level 1: Reactive Empathy"""

    def test_initialization(self):
        """Test Level 1 initializes correctly"""
        level1 = Level1Reactive()
        assert level1.level_number == 1
        assert level1.level_name == "Reactive Empathy"

    def test_reactive_response(self):
        """Test Level 1 responds reactively"""
        level1 = Level1Reactive()
        response = level1.respond({
            "request": "status",
            "subject": "project"
        })

        assert response["level"] == 1
        assert response["action"] == "provide_requested_information"
        assert response["initiative"] == "none"
        assert len(response["additional_offers"]) == 0

    def test_action_recording(self):
        """Test actions are recorded"""
        level1 = Level1Reactive()
        level1.respond({"request": "help"})

        history = level1.get_action_history()
        assert len(history) == 1
        assert history[0].level == 1


class TestLevel2Guided:
    """Test Level 2: Guided Empathy"""

    def test_initialization(self):
        """Test Level 2 initializes correctly"""
        level2 = Level2Guided()
        assert level2.level_number == 2
        assert level2.level_name == "Guided Empathy"

    def test_collaborative_exploration(self):
        """Test Level 2 asks clarifying questions"""
        level2 = Level2Guided()
        response = level2.respond({
            "request": "improve system",
            "ambiguity": "high"
        })

        assert response["level"] == 2
        assert response["action"] == "collaborative_exploration"
        assert response["initiative"] == "guided"
        assert "clarifying_questions" in response
        assert len(response["clarifying_questions"]) > 0

    def test_exploration_paths(self):
        """Test Level 2 suggests exploration paths"""
        level2 = Level2Guided()
        response = level2.respond({"request": "help"})

        assert "suggested_options" in response
        assert len(response["suggested_options"]) > 0


class TestLevel3Proactive:
    """Test Level 3: Proactive Empathy"""

    def test_initialization(self):
        """Test Level 3 initializes correctly"""
        level3 = Level3Proactive()
        assert level3.level_number == 3
        assert level3.level_name == "Proactive Empathy"

    def test_proactive_high_confidence(self):
        """Test Level 3 acts proactively with high confidence"""
        level3 = Level3Proactive()
        response = level3.respond({
            "observed_need": "failing_tests",
            "confidence": 0.9
        })

        assert response["level"] == 3
        assert response["action"] == "proactive_assistance"
        assert response["initiative"] == "proactive"
        assert response["confidence"] == 0.9

    def test_proactive_low_confidence(self):
        """Test Level 3 asks permission with low confidence"""
        level3 = Level3Proactive()
        response = level3.respond({
            "observed_need": "potential_issue",
            "confidence": 0.6
        })

        proactive_offer = response["proactive_offer"]
        assert proactive_offer["permission_needed"] == True


class TestLevel4Anticipatory:
    """Test Level 4: Anticipatory Empathy"""

    def test_initialization(self):
        """Test Level 4 initializes correctly"""
        level4 = Level4Anticipatory()
        assert level4.level_number == 4
        assert level4.level_name == "Anticipatory Empathy"

    def test_future_prediction(self):
        """Test Level 4 predicts future needs"""
        level4 = Level4Anticipatory()
        response = level4.respond({
            "current_state": {"compliance": 0.7},
            "trajectory": "declining",
            "prediction_horizon": "30_days"
        })

        assert response["level"] == 4
        assert response["action"] == "anticipatory_preparation"
        assert response["initiative"] == "anticipatory"
        assert "predicted_needs" in response
        assert "preventive_actions" in response
        assert len(response["predicted_needs"]) > 0

    def test_prediction_confidence(self):
        """Test Level 4 includes confidence in predictions"""
        level4 = Level4Anticipatory()
        response = level4.respond({
            "current_state": {},
            "trajectory": "test",
            "prediction_horizon": "7_days"
        })

        assert "confidence" in response
        assert 0.0 <= response["confidence"] <= 1.0


class TestLevel5Systems:
    """Test Level 5: Systems Empathy"""

    def test_initialization(self):
        """Test Level 5 initializes correctly"""
        level5 = Level5Systems()
        assert level5.level_number == 5
        assert level5.level_name == "Systems Empathy"

    def test_systems_solution(self):
        """Test Level 5 creates system-level solutions"""
        level5 = Level5Systems()
        response = level5.respond({
            "problem_class": "documentation_burden",
            "instances": 18,
            "pattern": "repetitive_structure"
        })

        assert response["level"] == 5
        assert response["action"] == "systems_level_solution"
        assert response["initiative"] == "systems_thinking"
        assert "system_created" in response
        assert "leverage_point" in response
        assert "compounding_value" in response

    def test_ai_ai_cooperation(self):
        """Test Level 5 enables AI-AI cooperation"""
        level5 = Level5Systems()
        response = level5.respond({
            "problem_class": "test_problem",
            "instances": 10
        })

        assert "ai_ai_sharing" in response
        sharing = response["ai_ai_sharing"]
        assert "mechanism" in sharing
        assert "scope" in sharing
        assert "benefit" in sharing


class TestLevelProgression:
    """Test progression through empathy levels"""

    def test_increasing_initiative(self):
        """Test that initiative increases through levels"""
        level1 = Level1Reactive()
        level2 = Level2Guided()
        level3 = Level3Proactive()
        level4 = Level4Anticipatory()
        level5 = Level5Systems()

        r1 = level1.respond({"request": "help"})
        r2 = level2.respond({"request": "help"})
        r3 = level3.respond({"observed_need": "help", "confidence": 0.8})
        r4 = level4.respond({"current_state": {}, "trajectory": "test", "prediction_horizon": "1d"})
        r5 = level5.respond({"problem_class": "test", "instances": 5})

        # Verify initiative increases
        assert r1["initiative"] == "none"
        assert r2["initiative"] == "guided"
        assert r3["initiative"] == "proactive"
        assert r4["initiative"] == "anticipatory"
        assert r5["initiative"] == "systems_thinking"

    def test_all_levels_have_unique_numbers(self):
        """Test all levels have unique level numbers"""
        levels = [
            Level1Reactive(),
            Level2Guided(),
            Level3Proactive(),
            Level4Anticipatory(),
            Level5Systems()
        ]

        level_numbers = [l.level_number for l in levels]
        assert len(level_numbers) == len(set(level_numbers))
        assert level_numbers == [1, 2, 3, 4, 5]

    def test_get_level_class_factory(self):
        """Test get_level_class factory function"""
        from empathy_os.levels import get_level_class

        # Test each level
        level1_class = get_level_class(1)
        assert level1_class == Level1Reactive
        level1 = level1_class()
        assert isinstance(level1, Level1Reactive)

        level2_class = get_level_class(2)
        assert level2_class == Level2Guided

        level3_class = get_level_class(3)
        assert level3_class == Level3Proactive

        level4_class = get_level_class(4)
        assert level4_class == Level4Anticipatory

        level5_class = get_level_class(5)
        assert level5_class == Level5Systems

        # Test default (invalid level returns Level1)
        default_class = get_level_class(99)
        assert default_class == Level1Reactive
