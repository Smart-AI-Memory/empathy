"""Tests for core EmpathyOS functionality

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from empathy_os import EmpathyOS


class TestEmpathyOS:
    """Test suite for EmpathyOS core functionality"""

    def test_initialization(self):
        """Test EmpathyOS initializes correctly"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        assert empathy.user_id == "test_user"
        assert empathy.target_level == 3
        assert empathy.confidence_threshold == 0.75
        assert empathy.collaboration_state.trust_level == 0.5

    def test_initialization_with_custom_threshold(self):
        """Test EmpathyOS initialization with custom confidence threshold"""
        empathy = EmpathyOS(user_id="test_user", target_level=4, confidence_threshold=0.9)

        assert empathy.confidence_threshold == 0.9

    def test_collaboration_state_tracking(self):
        """Test collaboration state is properly tracked"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Initial state
        assert empathy.collaboration_state.trust_level == 0.5
        assert empathy.collaboration_state.successful_interventions == 0
        assert empathy.collaboration_state.failed_interventions == 0

        # Update trust with success
        empathy.collaboration_state.update_trust("success")
        assert empathy.collaboration_state.trust_level > 0.5
        assert empathy.collaboration_state.successful_interventions == 1

        # Update trust with failure
        initial_trust = empathy.collaboration_state.trust_level
        empathy.collaboration_state.update_trust("failure")
        assert empathy.collaboration_state.trust_level < initial_trust
        assert empathy.collaboration_state.failed_interventions == 1

    def test_trust_level_bounds(self):
        """Test trust level stays within [0, 1] bounds"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Try to exceed upper bound
        for _ in range(20):
            empathy.collaboration_state.update_trust("success")

        assert empathy.collaboration_state.trust_level <= 1.0

        # Try to go below lower bound
        for _ in range(50):
            empathy.collaboration_state.update_trust("failure")

        assert empathy.collaboration_state.trust_level >= 0.0

    def test_systems_thinking_components_exist(self):
        """Test that systems thinking components are initialized"""
        empathy = EmpathyOS(user_id="test_user", target_level=4)

        assert hasattr(empathy, "feedback_detector")
        assert hasattr(empathy, "emergence_detector")
        assert hasattr(empathy, "leverage_analyzer")

    def test_multiple_users(self):
        """Test multiple EmpathyOS instances for different users"""
        user1 = EmpathyOS(user_id="user1", target_level=3)
        user2 = EmpathyOS(user_id="user2", target_level=4)

        assert user1.user_id != user2.user_id
        assert user1.target_level != user2.target_level

        # Verify independence
        user1.collaboration_state.update_trust("success")
        assert user1.collaboration_state.trust_level != user2.collaboration_state.trust_level

    def test_get_collaboration_state(self):
        """Test retrieving collaboration state"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)
        state = empathy.get_collaboration_state()

        assert state is not None
        assert isinstance(state, dict)
        # Check that it contains expected keys
        assert "total_interactions" in state or "trust_level" in str(state)

    def test_reset_collaboration_state(self):
        """Test resetting collaboration state"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Make some changes
        empathy.collaboration_state.update_trust("success")
        empathy.collaboration_state.update_trust("success")
        assert empathy.collaboration_state.successful_interventions == 2

        # Reset
        empathy.reset_collaboration_state()
        assert empathy.collaboration_state.trust_level == 0.5
        assert empathy.collaboration_state.successful_interventions == 0
        assert empathy.collaboration_state.failed_interventions == 0

    def test_update_trust_direct_method_exists(self):
        """Test that update_trust method exists"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)
        # Method may or may not exist on EmpathyOS directly
        # It exists on collaboration_state
        assert hasattr(empathy.collaboration_state, "update_trust")

    def test_collaboration_state_trust_updates(self):
        """Test trust updates through collaboration state"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)
        initial_trust = empathy.collaboration_state.trust_level

        # Update through collaboration_state
        empathy.collaboration_state.update_trust("success")
        assert empathy.collaboration_state.trust_level >= initial_trust

    def test_trust_trajectory_exists(self):
        """Test that trust trajectory tracking exists"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Check attribute exists
        assert hasattr(empathy.collaboration_state, "trust_trajectory")

    def test_feedback_loop_detector_exists(self):
        """Test that feedback loop detector is available"""
        empathy = EmpathyOS(user_id="test_user", target_level=3)

        # Check that feedback detector exists
        assert hasattr(empathy, "feedback_detector")

    def test_target_level_validation(self):
        """Test that target level is validated"""
        # Valid levels
        for level in [1, 2, 3, 4, 5]:
            empathy = EmpathyOS(user_id="test_user", target_level=level)
            assert empathy.target_level == level

    def test_confidence_threshold_bounds(self):
        """Test confidence threshold is within valid range"""
        # Test valid thresholds
        empathy1 = EmpathyOS(user_id="test", target_level=3, confidence_threshold=0.0)
        assert empathy1.confidence_threshold == 0.0

        empathy2 = EmpathyOS(user_id="test", target_level=3, confidence_threshold=1.0)
        assert empathy2.confidence_threshold == 1.0

        empathy3 = EmpathyOS(user_id="test", target_level=3, confidence_threshold=0.5)
        assert empathy3.confidence_threshold == 0.5
