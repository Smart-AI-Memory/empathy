"""
Tests for Core EmpathyOS Module

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest

from empathy_os.core import CollaborationState, EmpathyOS
from empathy_os.exceptions import ValidationError


class TestCollaborationState:
    """Test CollaborationState stock & flow model"""

    def test_initialization(self):
        """Test collaboration state initializes correctly"""
        state = CollaborationState()

        assert state.trust_level == 0.5  # Start neutral
        assert isinstance(state.shared_context, dict)
        assert state.successful_interventions == 0
        assert state.failed_interventions == 0
        assert state.total_interactions == 0

    def test_update_trust_success(self):
        """Test trust updates on successful interaction"""
        state = CollaborationState()

        initial_trust = state.trust_level
        state.update_trust("success")

        assert state.trust_level > initial_trust
        assert state.successful_interventions == 1
        assert state.failed_interventions == 0
        assert state.total_interactions == 1

    def test_update_trust_failure(self):
        """Test trust updates on failed interaction"""
        state = CollaborationState()

        initial_trust = state.trust_level
        state.update_trust("failure")

        assert state.trust_level < initial_trust
        assert state.successful_interventions == 0
        assert state.failed_interventions == 1
        assert state.total_interactions == 1

    def test_update_trust_multiple_successes(self):
        """Test trust builds with multiple successes"""
        state = CollaborationState()

        for _ in range(5):
            state.update_trust("success")

        assert state.trust_level > 0.5
        assert state.successful_interventions == 5
        assert state.total_interactions == 5

    def test_update_trust_multiple_failures(self):
        """Test trust erodes with multiple failures"""
        state = CollaborationState()

        for _ in range(5):
            state.update_trust("failure")

        assert state.trust_level < 0.5
        assert state.failed_interventions == 5

    def test_trust_clamped_at_maximum(self):
        """Test trust cannot exceed 1.0"""
        state = CollaborationState()

        # Max out trust
        for _ in range(20):
            state.update_trust("success")

        assert state.trust_level == 1.0
        assert state.trust_level <= 1.0

    def test_trust_clamped_at_minimum(self):
        """Test trust cannot go below 0.0"""
        state = CollaborationState()

        # Drive trust to zero
        for _ in range(20):
            state.update_trust("failure")

        assert state.trust_level == 0.0
        assert state.trust_level >= 0.0

    def test_trust_flow_rates(self):
        """Test trust erosion is faster than building (asymmetry)"""
        state = CollaborationState()

        # Erosion should be faster
        assert state.trust_erosion_rate > state.trust_building_rate

    def test_mixed_outcomes(self):
        """Test trust with mixed success/failure outcomes"""
        state = CollaborationState()

        state.update_trust("success")
        state.update_trust("success")
        state.update_trust("failure")

        assert state.successful_interventions == 2
        assert state.failed_interventions == 1
        assert state.total_interactions == 3
        # Net should be slight increase (2 success - 1 failure)
        assert state.trust_level > 0.5

    def test_unknown_outcome_ignored(self):
        """Test unknown outcome doesn't affect trust"""
        state = CollaborationState()

        initial_trust = state.trust_level
        state.update_trust("unknown")

        assert state.trust_level == initial_trust
        assert state.successful_interventions == 0
        assert state.failed_interventions == 0
        assert state.total_interactions == 1  # Still counts interaction


class TestEmpathyOSCore:
    """Test EmpathyOS core functionality"""

    def test_initialization_defaults(self):
        """Test EmpathyOS initializes with defaults"""
        empathy = EmpathyOS(user_id="test_user")

        assert empathy.user_id == "test_user"
        assert empathy.target_level == 3  # Default proactive
        assert empathy.confidence_threshold == 0.75
        assert isinstance(empathy.collaboration_state, CollaborationState)

    def test_initialization_custom_level(self):
        """Test initialization with custom target level"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy.target_level == 4

    def test_initialization_custom_confidence(self):
        """Test initialization with custom confidence threshold"""
        empathy = EmpathyOS(user_id="test_user", target_level=3, confidence_threshold=0.85)

        assert empathy.confidence_threshold == 0.85

    def test_systems_thinking_components_initialized(self):
        """Test that all systems thinking components are initialized"""
        empathy = EmpathyOS(user_id="test_user")

        # Check feedback detector
        assert hasattr(empathy, "feedback_detector")
        assert empathy.feedback_detector is not None

        # Check emergence detector
        assert hasattr(empathy, "emergence_detector")
        assert empathy.emergence_detector is not None

        # Check leverage analyzer
        assert hasattr(empathy, "leverage_analyzer")
        assert empathy.leverage_analyzer is not None

    def test_collaboration_state_accessible(self):
        """Test collaboration state is accessible"""
        empathy = EmpathyOS(user_id="test_user")

        state = empathy.collaboration_state
        assert state.trust_level == 0.5
        assert state.total_interactions == 0

    def test_trust_level_property(self):
        """Test accessing trust level"""
        empathy = EmpathyOS(user_id="test_user")

        # Initial trust
        assert empathy.collaboration_state.trust_level == 0.5

        # Update trust
        empathy.collaboration_state.update_trust("success")
        assert empathy.collaboration_state.trust_level > 0.5

    def test_multiple_users_independent(self):
        """Test multiple users have independent states"""
        user1 = EmpathyOS(user_id="user1")
        user2 = EmpathyOS(user_id="user2")

        # Update user1 trust
        user1.collaboration_state.update_trust("success")
        user1.collaboration_state.update_trust("success")

        # User2 should be unaffected
        assert user1.collaboration_state.trust_level > 0.5
        assert user2.collaboration_state.trust_level == 0.5

    def test_target_levels_valid_range(self):
        """Test different valid target levels"""
        for level in [1, 2, 3, 4, 5]:
            empathy = EmpathyOS(user_id="test", target_level=level)
            assert empathy.target_level == level

    def test_confidence_threshold_valid_range(self):
        """Test confidence threshold in valid range"""
        empathy = EmpathyOS(user_id="test", confidence_threshold=0.9)

        assert 0.0 <= empathy.confidence_threshold <= 1.0

    def test_shared_context_tracking(self):
        """Test shared context can be tracked"""
        empathy = EmpathyOS(user_id="test_user")

        # Add to shared context
        empathy.collaboration_state.shared_context["project"] = "empathy-framework"
        empathy.collaboration_state.shared_context["role"] = "developer"

        assert empathy.collaboration_state.shared_context["project"] == "empathy-framework"
        assert len(empathy.collaboration_state.shared_context) == 2

    def test_success_rate_calculation(self):
        """Test calculating success rate from collaboration state"""
        empathy = EmpathyOS(user_id="test_user")

        # Simulate interactions
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.update_trust("failure")

        total = empathy.collaboration_state.total_interactions
        successes = empathy.collaboration_state.successful_interventions

        success_rate = successes / total if total > 0 else 0
        assert success_rate == 0.75  # 3/4

    def test_session_start_timestamp(self):
        """Test session start timestamp is set"""
        empathy = EmpathyOS(user_id="test_user")

        assert empathy.collaboration_state.session_start is not None

    def test_integration_feedback_detection(self):
        """Test integration with feedback loop detector"""
        empathy = EmpathyOS(user_id="test_user")

        # Create history
        history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.7, "success": True},
        ]

        # Use feedback detector
        result = empathy.feedback_detector.detect_active_loop(history)

        assert "dominant_loop" in result

    def test_integration_emergence_detection(self):
        """Test integration with emergence detector"""
        empathy = EmpathyOS(user_id="test_user")

        baseline = {"trust": 0.3, "interactions": 10}
        current = {"trust": 0.8, "interactions": 50, "patterns": 5}

        # Use emergence detector
        score = empathy.emergence_detector.measure_emergence(baseline, current)

        assert 0.0 <= score <= 1.0

    def test_integration_leverage_analysis(self):
        """Test integration with leverage point analyzer"""
        empathy = EmpathyOS(user_id="test_user")

        problem = {"class": "trust_deficit", "description": "Low trust in AI"}

        # Use leverage analyzer
        points = empathy.leverage_analyzer.find_leverage_points(problem)

        assert len(points) > 0

    def test_trust_building_workflow(self):
        """Test complete trust building workflow"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Start with neutral trust
        assert empathy.collaboration_state.trust_level == 0.5

        # Series of successful interactions
        for _i in range(8):
            empathy.collaboration_state.update_trust("success")

        # Trust should have built up
        assert empathy.collaboration_state.trust_level > 0.7
        assert empathy.collaboration_state.successful_interventions == 8

        # Check for virtuous cycle
        history = [{"trust": 0.5 + (i * 0.05), "success": True} for i in range(8)]

        is_virtuous = empathy.feedback_detector.detect_virtuous_cycle(history)
        assert is_virtuous

    def test_trust_erosion_workflow(self):
        """Test trust erosion workflow"""
        empathy = EmpathyOS(user_id="test_user")

        # Series of failures
        for _ in range(5):
            empathy.collaboration_state.update_trust("failure")

        # Trust should have eroded
        assert empathy.collaboration_state.trust_level < 0.5
        assert empathy.collaboration_state.failed_interventions == 5

    def test_recovery_from_trust_erosion(self):
        """Test recovering from trust erosion"""
        empathy = EmpathyOS(user_id="test_user")

        # Erode trust
        for _ in range(3):
            empathy.collaboration_state.update_trust("failure")

        trust_after_erosion = empathy.collaboration_state.trust_level

        # Rebuild trust
        for _ in range(6):
            empathy.collaboration_state.update_trust("success")

        # Should have recovered
        assert empathy.collaboration_state.trust_level > trust_after_erosion
        # May not be back to 0.5 due to asymmetry (erosion faster than building)

    def test_long_term_collaboration_tracking(self):
        """Test tracking long-term collaboration"""
        empathy = EmpathyOS(user_id="test_user")

        # Simulate 50 interactions with 80% success rate
        for i in range(50):
            if i % 5 == 0:  # Every 5th is failure
                empathy.collaboration_state.update_trust("failure")
            else:
                empathy.collaboration_state.update_trust("success")

        assert empathy.collaboration_state.total_interactions == 50
        assert empathy.collaboration_state.successful_interventions == 40
        assert empathy.collaboration_state.failed_interventions == 10

        # Trust should be high
        assert empathy.collaboration_state.trust_level > 0.6


class TestEmpathyOSAsyncMethods:
    """Test EmpathyOS async methods (Levels 1-5)"""

    @pytest.mark.asyncio
    async def test_level_1_reactive_basic(self):
        """Test Level 1 reactive empathy"""
        empathy = EmpathyOS(user_id="test_user", target_level=1)

        result = await empathy.level_1_reactive("Get system status")

        assert result["level"] == 1
        assert result["type"] == "reactive"
        assert "result" in result
        assert result["empathy_level"] == "Reactive: Help after being asked"
        assert empathy.collaboration_state.total_interactions == 1

    @pytest.mark.asyncio
    async def test_level_2_guided_needs_clarification(self):
        """Test Level 2 guided with ambiguous request"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        # Ambiguous request should trigger clarification
        result = await empathy.level_2_guided("Update the system")

        assert result["level"] == 2
        assert result["type"] == "guided"
        # Should detect ambiguity and ask questions
        assert "action" in result

    @pytest.mark.asyncio
    async def test_level_3_proactive_high_confidence(self):
        """Test Level 3 proactive with high confidence pattern"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        context = {"user_activity": "debugging", "error_count": 5, "time_on_task": 30}

        result = await empathy.level_3_proactive(context)

        assert result["level"] == 3
        assert result["type"] == "proactive"
        assert "patterns_detected" in result
        assert "actions_taken" in result
        assert result["empathy_level"] == "Proactive: Act before being asked"

    @pytest.mark.asyncio
    async def test_level_4_anticipatory_bottleneck_prediction(self):
        """Test Level 4 anticipatory bottleneck prediction"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        trajectory = {
            "feature_count_increasing": True,
            "current_feature_count": 20,
            "growth_rate": 3,
            "threshold": 25,
        }

        result = await empathy.level_4_anticipatory(trajectory)

        assert result["level"] == 4
        assert result["type"] == "anticipatory"
        assert "bottlenecks_predicted" in result
        assert isinstance(result["bottlenecks_predicted"], list)
        assert "interventions_designed" in result
        assert result["empathy_level"] == "Anticipatory: Predict and prevent problems"

    @pytest.mark.asyncio
    async def test_level_5_systems_framework_design(self):
        """Test Level 5 systems thinking with framework"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        problem_pattern = {
            "class": "documentation_burden",
            "instances": 18,
            "time_per_instance": 120,
        }

        result = await empathy.level_5_systems(problem_pattern)

        assert result["level"] == 5
        assert result["type"] == "systems"
        assert "frameworks_designed" in result
        assert "leverage_points" in result
        assert result["empathy_level"] == "Systems: Build structures that help at scale"

    @pytest.mark.asyncio
    async def test_multiple_async_calls_sequentially(self):
        """Test multiple async level calls work correctly"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Call multiple levels sequentially
        r1 = await empathy.level_1_reactive("request 1")
        r2 = await empathy.level_2_guided("request 2")
        r3 = await empathy.level_3_proactive({"user_activity": "coding"})

        # Each should work independently
        assert r1["level"] == 1
        assert r2["level"] == 2
        assert r3["level"] == 3

        # Verify each level was called
        assert empathy.collaboration_state.total_interactions >= 1

    @pytest.mark.asyncio
    async def test_current_empathy_level_tracking(self):
        """Test that current empathy level is tracked"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy.current_empathy_level == 1  # Initial

        await empathy.level_3_proactive({"activity": "test"})
        assert empathy.current_empathy_level == 3

        trajectory = {
            "feature_count_increasing": True,
            "current_feature_count": 20,
            "growth_rate": 3,
            "threshold": 25,
        }
        await empathy.level_4_anticipatory(trajectory)
        assert empathy.current_empathy_level == 4

    @pytest.mark.asyncio
    async def test_level_2_no_clarification_needed(self):
        """Test Level 2 with clear request that doesn't need clarification"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        # Clear specific request
        result = await empathy.level_2_guided("Generate report for patient ID 12345")

        assert result["level"] == 2
        assert result["type"] == "guided"
        # Should either clarify or execute

    @pytest.mark.asyncio
    async def test_level_3_high_confidence_action(self):
        """Test Level 3 proactive action with high confidence pattern"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Context that should trigger high confidence pattern
        context = {
            "user_activity": "debugging",
            "error_count": 10,
            "time_on_task": 60,
            "repeated_pattern": True,
            "error_type": "NullPointerException",
        }

        result = await empathy.level_3_proactive(context)

        assert result["level"] == 3
        assert "patterns_detected" in result
        assert "actions_taken" in result

    @pytest.mark.asyncio
    async def test_level_4_with_interventions(self):
        """Test Level 4 that designs and executes interventions"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        trajectory = {
            "feature_count_increasing": True,
            "current_feature_count": 20,
            "growth_rate": 5,  # Higher growth rate
            "threshold": 25,
            "impact": "high",  # High impact to trigger intervention
        }

        result = await empathy.level_4_anticipatory(trajectory)

        assert result["level"] == 4
        assert "interventions_designed" in result
        assert "results" in result

    @pytest.mark.asyncio
    async def test_level_5_multiple_leverage_points(self):
        """Test Level 5 identifies multiple leverage points"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        domain_context = {
            "class": "testing_burden",
            "instances": 25,
            "time_per_instance": 180,
            "recurring": True,
            "impact": "high",
        }

        result = await empathy.level_5_systems(domain_context)

        assert result["level"] == 5
        assert "leverage_points" in result
        assert isinstance(result["leverage_points"], list)

    @pytest.mark.asyncio
    async def test_trust_updates_on_success(self):
        """Test trust increases with successful interventions"""
        empathy = EmpathyOS(user_id="test_user", target_level=1)

        # Successful interaction
        await empathy.level_1_reactive("Simple request")

        # Trust might increase if marked as success
        assert empathy.collaboration_state.total_interactions >= 1

    @pytest.mark.asyncio
    async def test_confidence_threshold_respected(self):
        """Test that confidence threshold is respected"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.95)

        assert empathy.confidence_threshold == 0.95

        # With very high threshold, fewer interventions should be designed
        trajectory = {
            "feature_count_increasing": True,
            "current_feature_count": 20,
            "growth_rate": 3,
            "threshold": 25,
        }

        result = await empathy.level_4_anticipatory(trajectory)
        assert "interventions_designed" in result

    def test_monitor_feedback_loops(self):
        """Test monitoring feedback loops"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Simulate trust pattern
        session_history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.7, "success": True},
        ]

        result = empathy.monitor_feedback_loops(session_history)

        # Should return feedback detector results
        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_level_1_validation_empty_string(self):
        """Test Level 1 rejects empty string"""
        empathy = EmpathyOS(user_id="test_user", target_level=1)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_1_reactive("")

    @pytest.mark.asyncio
    async def test_level_1_validation_whitespace(self):
        """Test Level 1 rejects whitespace-only string"""
        empathy = EmpathyOS(user_id="test_user", target_level=1)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_1_reactive("   ")

    @pytest.mark.asyncio
    async def test_level_1_validation_wrong_type(self):
        """Test Level 1 rejects non-string input"""
        empathy = EmpathyOS(user_id="test_user", target_level=1)

        with pytest.raises(ValidationError, match="must be a string"):
            await empathy.level_1_reactive(123)

    @pytest.mark.asyncio
    async def test_level_2_validation_empty_string(self):
        """Test Level 2 rejects empty string"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_2_guided("")

    @pytest.mark.asyncio
    async def test_level_2_validation_wrong_type(self):
        """Test Level 2 rejects non-string input"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        with pytest.raises(ValidationError, match="must be a string"):
            await empathy.level_2_guided(None)

    @pytest.mark.asyncio
    async def test_level_3_validation_empty_dict(self):
        """Test Level 3 rejects empty dict"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_3_proactive({})

    @pytest.mark.asyncio
    async def test_level_3_validation_wrong_type(self):
        """Test Level 3 rejects non-dict input"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        with pytest.raises(ValidationError, match="must be a dict"):
            await empathy.level_3_proactive("not a dict")

    @pytest.mark.asyncio
    async def test_level_4_validation_empty_dict(self):
        """Test Level 4 rejects empty dict"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_4_anticipatory({})

    @pytest.mark.asyncio
    async def test_level_4_validation_wrong_type(self):
        """Test Level 4 rejects non-dict input"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        with pytest.raises(ValidationError, match="must be a dict"):
            await empathy.level_4_anticipatory([1, 2, 3])

    @pytest.mark.asyncio
    async def test_level_5_validation_empty_dict(self):
        """Test Level 5 rejects empty dict"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        with pytest.raises(ValidationError, match="cannot be empty"):
            await empathy.level_5_systems({})

    @pytest.mark.asyncio
    async def test_level_5_validation_wrong_type(self):
        """Test Level 5 rejects non-dict input"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        with pytest.raises(ValidationError, match="must be a dict"):
            await empathy.level_5_systems(42)

    @pytest.mark.asyncio
    async def test_level_3_high_confidence_pattern_execution(self):
        """Test Level 3 executes high confidence proactive actions"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Context with repeated_action triggers 0.85 confidence pattern
        context = {"repeated_action": True, "user_activity": "testing"}

        result = await empathy.level_3_proactive(context)

        assert result["level"] == 3
        assert "patterns_detected" in result
        assert "actions_taken" in result
        # Should have executed actions from high confidence pattern
        assert empathy.collaboration_state.total_interactions >= 1

    @pytest.mark.asyncio
    async def test_level_4_high_impact_intervention(self):
        """Test Level 4 designs interventions for high impact bottlenecks"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Trajectory that triggers bottleneck with high impact
        trajectory = {
            "feature_count_increasing": True,
            "current_feature_count": 20,
            "growth_rate": 5,
            "threshold": 25,
            "impact": "high",  # This should pass the _should_anticipate check
        }

        result = await empathy.level_4_anticipatory(trajectory)

        assert result["level"] == 4
        assert "bottlenecks_predicted" in result
        assert len(result["bottlenecks_predicted"]) > 0
        # Should have designed interventions for high impact bottleneck
        assert "interventions_designed" in result

    @pytest.mark.asyncio
    async def test_level_5_with_recurring_problem(self):
        """Test Level 5 identifies problem classes and designs frameworks"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        # Domain context with recurring problem
        domain_context = {
            "recurring_documentation_burden": True,
            "instances": 15,
            "time_per_instance": 120,
        }

        result = await empathy.level_5_systems(domain_context)

        assert result["level"] == 5
        assert "problem_classes" in result
        assert result["problem_classes"] >= 1  # Should identify at least 1 problem class
        assert "leverage_points" in result
        assert "frameworks_designed" in result

    @pytest.mark.asyncio
    async def test_level_2_ambiguous_request_triggers_clarification(self):
        """Test Level 2 with ambiguous request that needs clarification"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        # Ambiguous request with trigger words
        result = await empathy.level_2_guided("Update some things soon")

        assert result["level"] == 2
        assert result["type"] == "guided"
        # Should trigger clarification due to "some" and "soon"
        assert "action" in result

    def test_get_collaboration_state(self):
        """Test getting collaboration state"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Update some state first
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.total_interactions = 5

        state = empathy.get_collaboration_state()

        assert "trust_level" in state
        assert "total_interactions" in state
        assert state["total_interactions"] == 5
        assert "success_rate" in state
        assert "current_empathy_level" in state
        assert "target_empathy_level" in state

    def test_reset_collaboration_state(self):
        """Test resetting collaboration state"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Modify state
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.total_interactions = 10

        # Reset
        empathy.reset_collaboration_state()

        # Should be back to defaults
        assert empathy.collaboration_state.total_interactions == 0
        assert empathy.collaboration_state.successful_interventions == 0
        assert empathy.collaboration_state.trust_level == 0.5  # Default

    def test_monitor_feedback_loops_trust_erosion(self):
        """Test detecting and responding to trust erosion loop"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Create mock session history that will trigger trust erosion detection
        # Need to mock the feedback detector to return R2_trust_erosion
        session_history = [
            {"trust": 0.5, "success": False},
            {"trust": 0.4, "success": False},
            {"trust": 0.3, "success": False},
        ]

        # Temporarily mock the feedback detector response
        original_detect = empathy.feedback_detector.detect_active_loop
        empathy.feedback_detector.detect_active_loop = lambda h: {
            "dominant_loop": "R2_trust_erosion",
            "loop_type": "reinforcing",
            "trend": "negative",
        }

        result = empathy.monitor_feedback_loops(session_history)

        # Should return intervention for breaking trust erosion
        assert "action" in result
        assert result["action"] == "transparency_intervention"
        assert "steps" in result

        # Restore original method
        empathy.feedback_detector.detect_active_loop = original_detect

    def test_monitor_feedback_loops_trust_building(self):
        """Test detecting and responding to trust building loop"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        # Create session history
        session_history = [
            {"trust": 0.5, "success": True},
            {"trust": 0.6, "success": True},
            {"trust": 0.7, "success": True},
        ]

        # Mock to return R1_trust_building
        original_detect = empathy.feedback_detector.detect_active_loop
        empathy.feedback_detector.detect_active_loop = lambda h: {
            "dominant_loop": "R1_trust_building",
            "loop_type": "reinforcing",
            "trend": "positive",
        }

        result = empathy.monitor_feedback_loops(session_history)

        # Should return intervention for maintaining trust building
        assert "action" in result
        assert result["action"] == "maintain_momentum"
        assert "steps" in result

        # Restore
        empathy.feedback_detector.detect_active_loop = original_detect

    @pytest.mark.asyncio
    async def test_async_context_manager(self):
        """Test EmpathyOS async context manager"""
        async with EmpathyOS(user_id="test_user", target_level=3) as empathy:
            assert empathy.user_id == "test_user"
            assert empathy.target_level == 3

            # Use it normally
            result = await empathy.level_1_reactive("Test request")
            assert result["level"] == 1

        # After context exit, empathy should have been cleaned up
        # (cleanup is a no-op currently, but tests the pattern)

    @pytest.mark.asyncio
    async def test_async_context_manager_with_exception(self):
        """Test async context manager handles exceptions"""
        try:
            async with EmpathyOS(user_id="test_user", target_level=3) as empathy:
                # Trigger validation error
                await empathy.level_1_reactive("")
        except ValidationError:
            pass  # Expected

        # Context manager should have exited cleanly despite exception

    def test_refine_request_no_clarification(self):
        """Test _refine_request when no clarification needed"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        clarification = {"needs_clarification": False}
        result = empathy._refine_request("Original request", clarification)

        assert result == "Original request"

    def test_refine_request_with_responses(self):
        """Test _refine_request with clarification responses"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        clarification = {
            "needs_clarification": True,
            "responses": {
                "What is your goal?": "Increase efficiency",
                "When do you need this?": "By Friday",
            },
        }

        result = empathy._refine_request("Update the system", clarification)

        assert "Update the system" in result
        assert "Clarifications:" in result
        assert "Increase efficiency" in result
        assert "By Friday" in result

    def test_refine_request_needs_clarification_no_responses(self):
        """Test _refine_request when clarification needed but no responses yet"""
        empathy = EmpathyOS(user_id="test_user", target_level=2)

        clarification = {
            "needs_clarification": True,
            "questions": ["What is your goal?"],
            # No 'responses' key - questions asked but not answered yet
        }

        result = empathy._refine_request("Update the system", clarification)

        # Should return original since no responses provided yet
        assert result == "Update the system"

    def test_parse_timeframe_days(self):
        """Test parsing timeframe with days"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy._parse_timeframe_to_days("60 days") == 60
        assert empathy._parse_timeframe_to_days("45 day") == 45

    def test_parse_timeframe_weeks(self):
        """Test parsing timeframe with weeks"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy._parse_timeframe_to_days("3 weeks") == 21
        assert empathy._parse_timeframe_to_days("5 week") == 35

    def test_parse_timeframe_months(self):
        """Test parsing timeframe with months"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy._parse_timeframe_to_days("2 months") == 60
        assert empathy._parse_timeframe_to_days("2-3 months") == 75  # midpoint

    def test_parse_timeframe_invalid(self):
        """Test parsing invalid timeframe returns None"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert empathy._parse_timeframe_to_days("") is None
        assert empathy._parse_timeframe_to_days("soon") is None
        assert empathy._parse_timeframe_to_days("unknown") is None

    def test_should_anticipate_low_confidence(self):
        """Test _should_anticipate rejects low confidence"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.75)

        bottleneck = {
            "confidence": 0.5,  # Below threshold
            "timeframe": "60 days",
            "impact": "high",
        }

        assert empathy._should_anticipate(bottleneck) is False

    def test_should_anticipate_short_timeframe(self):
        """Test _should_anticipate rejects too-soon timeframe"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.75)

        bottleneck = {"confidence": 0.85, "timeframe": "15 days", "impact": "high"}  # < 30 days

        assert empathy._should_anticipate(bottleneck) is False

    def test_should_anticipate_long_timeframe(self):
        """Test _should_anticipate rejects too-far timeframe"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.75)

        bottleneck = {"confidence": 0.85, "timeframe": "150 days", "impact": "high"}  # > 120 days

        assert empathy._should_anticipate(bottleneck) is False

    def test_should_anticipate_low_impact(self):
        """Test _should_anticipate rejects low impact"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.75)

        bottleneck = {
            "confidence": 0.85,
            "timeframe": "60 days",
            "impact": "low",  # Not high or critical
        }

        assert empathy._should_anticipate(bottleneck) is False

    def test_should_anticipate_valid(self):
        """Test _should_anticipate accepts valid bottleneck"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.75)

        bottleneck = {"confidence": 0.85, "timeframe": "60 days", "impact": "high"}

        assert empathy._should_anticipate(bottleneck) is True

    @pytest.mark.asyncio
    async def test_execute_proactive_actions_missing_action(self):
        """Test _execute_proactive_actions handles missing action field"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        actions = [{"confidence": 0.9}]  # Missing 'action' field
        results = await empathy._execute_proactive_actions(actions)

        assert len(results) == 1
        assert results[0]["success"] is False
        assert "error" in results[0]

    @pytest.mark.asyncio
    async def test_execute_anticipatory_interventions_missing_type(self):
        """Test _execute_anticipatory_interventions handles missing type field"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        interventions = [{"target": "database"}]  # Missing 'type' field
        results = await empathy._execute_anticipatory_interventions(interventions)

        assert len(results) == 1
        assert results[0]["success"] is False
        assert "error" in results[0]

    @pytest.mark.asyncio
    async def test_implement_frameworks_missing_name(self):
        """Test _implement_frameworks handles missing name field"""
        empathy = EmpathyOS(user_id="test_user", target_level=5)

        frameworks = [{"type": "architectural"}]  # Missing 'name' field
        results = await empathy._implement_frameworks(frameworks)

        assert len(results) == 1
        assert results[0]["deployed"] is False
        assert "error" in results[0]
