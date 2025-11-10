"""
Tests for individual empathy level classes

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from datetime import datetime

from empathy_os import (
    Level1Reactive,
    Level2Guided,
    Level3Proactive,
    Level4Anticipatory,
    Level5Systems,
)
from empathy_os.levels import EmpathyAction, get_level_class


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
        response = level1.respond({"request": "status", "subject": "project"})

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
        response = level2.respond({"request": "improve system", "ambiguity": "high"})

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
        response = level3.respond({"observed_need": "failing_tests", "confidence": 0.9})

        assert response["level"] == 3
        assert response["action"] == "proactive_assistance"
        assert response["initiative"] == "proactive"
        assert response["confidence"] == 0.9

    def test_proactive_low_confidence(self):
        """Test Level 3 asks permission with low confidence"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "potential_issue", "confidence": 0.6})

        proactive_offer = response["proactive_offer"]
        assert proactive_offer["permission_needed"] is True


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
        response = level4.respond(
            {
                "current_state": {"compliance": 0.7},
                "trajectory": "declining",
                "prediction_horizon": "30_days",
            }
        )

        assert response["level"] == 4
        assert response["action"] == "anticipatory_preparation"
        assert response["initiative"] == "anticipatory"
        assert "predicted_needs" in response
        assert "preventive_actions" in response
        assert len(response["predicted_needs"]) > 0

    def test_prediction_confidence(self):
        """Test Level 4 includes confidence in predictions"""
        level4 = Level4Anticipatory()
        response = level4.respond(
            {"current_state": {}, "trajectory": "test", "prediction_horizon": "7_days"}
        )

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
        response = level5.respond(
            {
                "problem_class": "documentation_burden",
                "instances": 18,
                "pattern": "repetitive_structure",
            }
        )

        assert response["level"] == 5
        assert response["action"] == "systems_level_solution"
        assert response["initiative"] == "systems_thinking"
        assert "system_created" in response
        assert "leverage_point" in response
        assert "compounding_value" in response

    def test_ai_ai_cooperation(self):
        """Test Level 5 enables AI-AI cooperation"""
        level5 = Level5Systems()
        response = level5.respond({"problem_class": "test_problem", "instances": 10})

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
            Level5Systems(),
        ]

        level_numbers = [lvl.level_number for lvl in levels]
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


class TestEmpathyAction:
    """Test EmpathyAction dataclass"""

    def test_empathy_action_creation(self):
        """Test creating an EmpathyAction"""
        action = EmpathyAction(level=1, action_type="test_action", description="Test description")
        assert action.level == 1
        assert action.action_type == "test_action"
        assert action.description == "Test description"
        assert action.context == {}
        assert action.outcome is None
        assert isinstance(action.timestamp, datetime)

    def test_empathy_action_with_context(self):
        """Test EmpathyAction with context"""
        context = {"user": "test_user", "priority": "high"}
        action = EmpathyAction(
            level=2,
            action_type="guided_response",
            description="Collaborative exploration",
            context=context,
            outcome="success",
        )
        assert action.context == context
        assert action.outcome == "success"

    def test_empathy_action_timestamp_auto_generated(self):
        """Test that timestamp is auto-generated"""
        action1 = EmpathyAction(level=1, action_type="test", description="desc")
        action2 = EmpathyAction(level=1, action_type="test", description="desc")
        # Both should have timestamps (even if very close)
        assert action1.timestamp is not None
        assert action2.timestamp is not None


class TestEmpathyLevel:
    """Test EmpathyLevel abstract base class"""

    def test_empathy_level_initialization(self):
        """Test that EmpathyLevel initializes with empty action history"""
        level1 = Level1Reactive()
        assert level1.actions_taken == []
        assert isinstance(level1.actions_taken, list)

    def test_record_action(self):
        """Test recording actions"""
        level = Level1Reactive()
        level.record_action(action_type="test", description="Test action", context={"key": "value"})
        assert len(level.actions_taken) == 1
        assert level.actions_taken[0].action_type == "test"
        assert level.actions_taken[0].description == "Test action"
        assert level.actions_taken[0].context == {"key": "value"}

    def test_record_action_with_outcome(self):
        """Test recording action with outcome"""
        level = Level2Guided()
        level.record_action(
            action_type="guidance",
            description="Provided guidance",
            context={},
            outcome="User understood",
        )
        assert level.actions_taken[0].outcome == "User understood"

    def test_get_action_history(self):
        """Test retrieving action history"""
        level = Level3Proactive()
        # Record multiple actions
        level.record_action("action1", "desc1", {})
        level.record_action("action2", "desc2", {})
        level.record_action("action3", "desc3", {})

        history = level.get_action_history()
        assert len(history) == 3
        assert history[0].action_type == "action1"
        assert history[1].action_type == "action2"
        assert history[2].action_type == "action3"

    def test_multiple_actions_preserve_order(self):
        """Test that multiple actions preserve order"""
        level = Level4Anticipatory()
        for i in range(5):
            level.record_action(f"action_{i}", f"description_{i}", {})

        history = level.get_action_history()
        assert len(history) == 5
        for i, action in enumerate(history):
            assert action.action_type == f"action_{i}"


class TestLevel1ReactiveEdgeCases:
    """Test Level 1 edge cases"""

    def test_respond_with_empty_context(self):
        """Test Level 1 responds with empty context"""
        level1 = Level1Reactive()
        response = level1.respond({})
        assert response["level"] == 1
        assert response["action"] == "provide_requested_information"
        assert "request" in response["description"]

    def test_respond_with_missing_subject(self):
        """Test Level 1 handles missing subject gracefully"""
        level1 = Level1Reactive()
        response = level1.respond({"request": "help"})
        assert response["level"] == 1
        # Should handle empty string subject gracefully
        assert "help" in response["description"]

    def test_multiple_responses(self):
        """Test Level 1 can handle multiple sequential responses"""
        level1 = Level1Reactive()
        for i in range(3):
            response = level1.respond({"request": f"request_{i}"})
            assert response["level"] == 1

        assert len(level1.get_action_history()) == 3

    def test_no_additional_offers(self):
        """Test Level 1 never makes additional offers"""
        level1 = Level1Reactive()
        response = level1.respond({"request": "complex_task", "urgency": "high"})
        assert len(response["additional_offers"]) == 0


class TestLevel2GuidedEdgeCases:
    """Test Level 2 edge cases"""

    def test_low_ambiguity_questions(self):
        """Test Level 2 with low ambiguity"""
        level2 = Level2Guided()
        response = level2.respond({"request": "help", "ambiguity": "low"})
        # Should still have base questions
        assert len(response["clarifying_questions"]) >= 3

    def test_medium_ambiguity_questions(self):
        """Test Level 2 with medium ambiguity (default)"""
        level2 = Level2Guided()
        response = level2.respond({"request": "improve"})
        # Default ambiguity is medium
        assert len(response["clarifying_questions"]) == 3

    def test_high_ambiguity_questions(self):
        """Test Level 2 adds extra question for high ambiguity"""
        level2 = Level2Guided()
        response = level2.respond({"request": "help", "ambiguity": "high"})
        # Should have extra question for high ambiguity
        assert len(response["clarifying_questions"]) == 4
        assert any("broader context" in q.lower() for q in response["clarifying_questions"])

    def test_exploration_paths_always_present(self):
        """Test Level 2 always suggests exploration paths"""
        level2 = Level2Guided()
        response = level2.respond({"request": "anything"})
        assert "suggested_options" in response
        assert len(response["suggested_options"]) == 3

    def test_empty_request(self):
        """Test Level 2 handles empty request"""
        level2 = Level2Guided()
        response = level2.respond({"request": ""})
        assert response["level"] == 2
        assert len(response["clarifying_questions"]) > 0


class TestLevel3ProactiveEdgeCases:
    """Test Level 3 edge cases"""

    def test_confidence_threshold_at_0_8(self):
        """Test Level 3 threshold at exactly 0.8"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "test", "confidence": 0.8})
        proactive_offer = response["proactive_offer"]
        assert proactive_offer["permission_needed"] is False
        assert "automatically" in proactive_offer["action_plan"].lower()

    def test_confidence_just_below_threshold(self):
        """Test Level 3 with confidence just below threshold"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "test", "confidence": 0.79})
        proactive_offer = response["proactive_offer"]
        assert proactive_offer["permission_needed"] is True

    def test_confidence_just_above_threshold(self):
        """Test Level 3 with confidence just above threshold"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "test", "confidence": 0.81})
        proactive_offer = response["proactive_offer"]
        assert proactive_offer["permission_needed"] is False

    def test_default_confidence(self):
        """Test Level 3 with default confidence (0.5)"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "test"})
        assert response["confidence"] == 0.5
        assert response["proactive_offer"]["permission_needed"] is True

    def test_very_high_confidence(self):
        """Test Level 3 with very high confidence"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "critical_fix", "confidence": 0.99})
        assert response["confidence"] == 0.99
        assert response["proactive_offer"]["permission_needed"] is False

    def test_observed_need_included(self):
        """Test Level 3 includes observed need in response"""
        level3 = Level3Proactive()
        response = level3.respond({"observed_need": "failing_tests", "confidence": 0.9})
        assert response["observed_need"] == "failing_tests"
        assert "failing_tests" in response["proactive_offer"]["need_identified"]


class TestLevel4AnticipatorEdgeCases:
    """Test Level 4 edge cases"""

    def test_empty_current_state(self):
        """Test Level 4 with empty current state"""
        level4 = Level4Anticipatory()
        response = level4.respond(
            {"current_state": {}, "trajectory": "unknown", "prediction_horizon": "unknown"}
        )
        assert response["level"] == 4
        assert len(response["predicted_needs"]) > 0

    def test_different_prediction_horizons(self):
        """Test Level 4 with various prediction horizons"""
        level4 = Level4Anticipatory()
        horizons = ["7_days", "30_days", "90_days", "1_year"]

        for horizon in horizons:
            response = level4.respond(
                {
                    "current_state": {"status": "good"},
                    "trajectory": "stable",
                    "prediction_horizon": horizon,
                }
            )
            assert response["prediction_horizon"] == horizon
            assert horizon in response["description"]

    def test_prediction_confidence_always_present(self):
        """Test Level 4 always includes confidence"""
        level4 = Level4Anticipatory()
        response = level4.respond(
            {"current_state": {}, "trajectory": "test", "prediction_horizon": "test"}
        )
        assert "confidence" in response
        assert response["confidence"] == 0.85  # Default from implementation

    def test_predicted_needs_structure(self):
        """Test Level 4 predicted needs have correct structure"""
        level4 = Level4Anticipatory()
        response = level4.respond(
            {
                "current_state": {"compliance": 0.8},
                "trajectory": "declining",
                "prediction_horizon": "30_days",
            }
        )
        # Check structure of predictions
        assert len(response["predicted_needs"]) == 3
        assert len(response["preventive_actions"]) == 3
        assert all(isinstance(need, str) for need in response["predicted_needs"])

    def test_different_trajectories(self):
        """Test Level 4 with different trajectories"""
        level4 = Level4Anticipatory()
        trajectories = ["improving", "declining", "stable", "volatile"]

        for trajectory in trajectories:
            response = level4.respond(
                {"current_state": {}, "trajectory": trajectory, "prediction_horizon": "30_days"}
            )
            assert trajectory in response["predicted_needs"][0]


class TestLevel5SystemsEdgeCases:
    """Test Level 5 edge cases"""

    def test_zero_instances(self):
        """Test Level 5 with zero instances"""
        level5 = Level5Systems()
        response = level5.respond({"problem_class": "new_problem", "instances": 0})
        assert response["instances_addressed"] == 0
        assert response["level"] == 5

    def test_single_instance(self):
        """Test Level 5 with single instance"""
        level5 = Level5Systems()
        response = level5.respond({"problem_class": "rare_issue", "instances": 1})
        assert response["instances_addressed"] == 1

    def test_many_instances(self):
        """Test Level 5 with many instances"""
        level5 = Level5Systems()
        response = level5.respond({"problem_class": "common_issue", "instances": 100})
        assert response["instances_addressed"] == 100
        assert "100" in str(response["compounding_value"]["immediate"])

    def test_with_pattern(self):
        """Test Level 5 with explicit pattern"""
        level5 = Level5Systems()
        response = level5.respond(
            {"problem_class": "test_problem", "instances": 10, "pattern": "repetitive_structure"}
        )
        assert response["level"] == 5

    def test_without_pattern(self):
        """Test Level 5 without explicit pattern (None)"""
        level5 = Level5Systems()
        response = level5.respond(
            {
                "problem_class": "test_problem",
                "instances": 10,
                # pattern is optional, defaults to None
            }
        )
        assert response["level"] == 5

    def test_system_design_structure(self):
        """Test Level 5 system design has expected structure"""
        level5 = Level5Systems()
        response = level5.respond(
            {"problem_class": "documentation", "instances": 20, "pattern": "repetitive"}
        )

        system = response["system_created"]
        assert "name" in system
        assert "description" in system
        assert "components" in system
        assert len(system["components"]) == 3

        # Check compounding value structure
        value = response["compounding_value"]
        assert "immediate" in value
        assert "compounding" in value
        assert "multiplier" in value

        # Check AI-AI sharing structure
        sharing = response["ai_ai_sharing"]
        assert "mechanism" in sharing
        assert "scope" in sharing
        assert "benefit" in sharing


class TestGetLevelClassFunction:
    """Test get_level_class factory function"""

    def test_get_all_valid_levels(self):
        """Test getting all 5 valid level classes"""
        for i in range(1, 6):
            level_class = get_level_class(i)
            assert level_class is not None
            instance = level_class()
            assert instance.level_number == i

    def test_get_invalid_level_returns_level1(self):
        """Test that invalid level numbers return Level1"""
        invalid_levels = [0, -1, 6, 10, 999, -999]
        for invalid in invalid_levels:
            level_class = get_level_class(invalid)
            assert level_class == Level1Reactive

    def test_level_class_instances_work(self):
        """Test that classes from get_level_class can be instantiated"""
        for i in range(1, 6):
            LevelClass = get_level_class(i)
            instance = LevelClass()
            # Should be able to respond
            response = instance.respond({})
            assert response["level"] == i


class TestCrossLevelBehavior:
    """Test behavior across multiple levels"""

    def test_all_levels_record_actions(self):
        """Test that all levels record actions when responding"""
        levels = [
            (Level1Reactive(), {"request": "help"}),
            (Level2Guided(), {"request": "help"}),
            (Level3Proactive(), {"observed_need": "test", "confidence": 0.8}),
            (
                Level4Anticipatory(),
                {"current_state": {}, "trajectory": "t", "prediction_horizon": "1d"},
            ),
            (Level5Systems(), {"problem_class": "test", "instances": 1}),
        ]

        for level, context in levels:
            level.respond(context)
            assert len(level.get_action_history()) == 1

    def test_all_levels_return_consistent_structure(self):
        """Test that all levels return responses with consistent base structure"""
        levels = [
            (Level1Reactive(), {"request": "help"}),
            (Level2Guided(), {"request": "help"}),
            (Level3Proactive(), {"observed_need": "test", "confidence": 0.8}),
            (
                Level4Anticipatory(),
                {"current_state": {}, "trajectory": "t", "prediction_horizon": "1d"},
            ),
            (Level5Systems(), {"problem_class": "test", "instances": 1}),
        ]

        for level, context in levels:
            response = level.respond(context)
            # All should have these common fields
            assert "level" in response
            assert "level_name" in response
            assert "action" in response
            assert "description" in response
            assert "initiative" in response
            assert "reasoning" in response

    def test_level_names_match_numbers(self):
        """Test that level names correspond to numbers"""
        expected_names = {
            1: "Reactive Empathy",
            2: "Guided Empathy",
            3: "Proactive Empathy",
            4: "Anticipatory Empathy",
            5: "Systems Empathy",
        }

        for num, name in expected_names.items():
            LevelClass = get_level_class(num)
            instance = LevelClass()
            assert instance.level_name == name

    def test_initiative_progression(self):
        """Test that initiative types progress logically"""
        expected_initiatives = {
            1: "none",
            2: "guided",
            3: "proactive",
            4: "anticipatory",
            5: "systems_thinking",
        }

        contexts = [
            {"request": "help"},
            {"request": "help"},
            {"observed_need": "test", "confidence": 0.8},
            {"current_state": {}, "trajectory": "t", "prediction_horizon": "1d"},
            {"problem_class": "test", "instances": 1},
        ]

        for level_num, expected_initiative in expected_initiatives.items():
            LevelClass = get_level_class(level_num)
            instance = LevelClass()
            response = instance.respond(contexts[level_num - 1])
            assert response["initiative"] == expected_initiative
