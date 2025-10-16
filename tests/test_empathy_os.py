"""
Tests for core EmpathyOS functionality

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
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
        empathy = EmpathyOS(
            user_id="test_user",
            target_level=4,
            confidence_threshold=0.9
        )

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

        assert hasattr(empathy, 'feedback_detector')
        assert hasattr(empathy, 'emergence_detector')
        assert hasattr(empathy, 'leverage_analyzer')

    def test_multiple_users(self):
        """Test multiple EmpathyOS instances for different users"""
        user1 = EmpathyOS(user_id="user1", target_level=3)
        user2 = EmpathyOS(user_id="user2", target_level=4)

        assert user1.user_id != user2.user_id
        assert user1.target_level != user2.target_level

        # Verify independence
        user1.collaboration_state.update_trust("success")
        assert user1.collaboration_state.trust_level != user2.collaboration_state.trust_level
