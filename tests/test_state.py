"""
Comprehensive tests for Collaboration State Management

Tests cover:
- UserPattern class and should_act method
- Interaction dataclass
- CollaborationState initialization
- add_interaction method
- update_trust method
- add_pattern method (both new and update)
- find_matching_pattern method
- get_conversation_history method
- should_progress_to_level method
- get_statistics method
"""

from datetime import datetime

import pytest

from empathy_llm_toolkit.state import CollaborationState, Interaction, PatternType, UserPattern


class TestUserPattern:
    """Test UserPattern dataclass and methods"""

    def test_user_pattern_creation(self):
        """Test UserPattern dataclass creation"""
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="after commit",
            action="run tests",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
            context={"language": "python"},
        )

        assert pattern.pattern_type == PatternType.SEQUENTIAL
        assert pattern.trigger == "after commit"
        assert pattern.action == "run tests"
        assert pattern.confidence == 0.85
        assert pattern.occurrences == 5
        assert pattern.context["language"] == "python"

    def test_should_act_high_confidence_high_trust(self):
        """Test should_act returns True with high confidence and trust"""
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )

        assert pattern.should_act(trust_level=0.7) is True

    def test_should_act_low_confidence(self):
        """Test should_act returns False with low confidence"""
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.6,
            occurrences=2,
            last_seen=datetime.now(),
        )

        assert pattern.should_act(trust_level=0.8) is False

    def test_should_act_low_trust(self):
        """Test should_act returns False with low trust"""
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )

        assert pattern.should_act(trust_level=0.5) is False

    def test_should_act_boundary_values(self):
        """Test should_act with boundary values"""
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.71,
            occurrences=3,
            last_seen=datetime.now(),
        )

        # Just above threshold
        assert pattern.should_act(trust_level=0.61) is True

        # Just below threshold
        pattern.confidence = 0.69
        assert pattern.should_act(trust_level=0.7) is False


class TestInteraction:
    """Test Interaction dataclass"""

    def test_interaction_creation(self):
        """Test Interaction dataclass creation"""
        interaction = Interaction(
            timestamp=datetime.now(),
            role="user",
            content="Hello AI",
            empathy_level=2,
            metadata={"context": "greeting"},
        )

        assert interaction.role == "user"
        assert interaction.content == "Hello AI"
        assert interaction.empathy_level == 2
        assert interaction.metadata["context"] == "greeting"

    def test_interaction_with_empty_metadata(self):
        """Test Interaction with empty metadata"""
        interaction = Interaction(
            timestamp=datetime.now(),
            role="assistant",
            content="Hello human",
            empathy_level=1,
            metadata={},
        )

        assert interaction.role == "assistant"
        assert interaction.metadata == {}


class TestCollaborationState:
    """Test CollaborationState class and methods"""

    def test_collaboration_state_initialization(self):
        """Test CollaborationState initialization"""
        state = CollaborationState(user_id="user123")

        assert state.user_id == "user123"
        assert isinstance(state.session_start, datetime)
        assert state.interactions == []
        assert state.detected_patterns == []
        assert state.trust_level == 0.5
        assert state.successful_actions == 0
        assert state.failed_actions == 0
        assert state.trust_trajectory == []
        assert state.current_level == 1
        assert state.level_history == []
        assert state.preferences == {}
        assert state.shared_context == {}

    def test_add_interaction_user(self):
        """Test adding user interaction"""
        state = CollaborationState(user_id="user123")

        state.add_interaction(
            role="user", content="Can you help me?", empathy_level=1, metadata={"type": "question"}
        )

        assert len(state.interactions) == 1
        assert state.interactions[0].role == "user"
        assert state.interactions[0].content == "Can you help me?"
        assert state.interactions[0].empathy_level == 1
        assert state.interactions[0].metadata["type"] == "question"
        # User interactions don't add to level_history
        assert len(state.level_history) == 0

    def test_add_interaction_assistant(self):
        """Test adding assistant interaction"""
        state = CollaborationState(user_id="user123")

        state.add_interaction(
            role="assistant",
            content="Yes, I can help!",
            empathy_level=2,
            metadata={"type": "response"},
        )

        assert len(state.interactions) == 1
        assert state.interactions[0].role == "assistant"
        # Assistant interactions add to level_history
        assert len(state.level_history) == 1
        assert state.level_history[0] == 2

    def test_add_interaction_without_metadata(self):
        """Test adding interaction without metadata"""
        state = CollaborationState(user_id="user123")

        state.add_interaction(role="user", content="Hello", empathy_level=1)

        assert len(state.interactions) == 1
        assert state.interactions[0].metadata == {}

    def test_update_trust_success(self):
        """Test updating trust with success outcome"""
        state = CollaborationState(user_id="user123")
        initial_trust = state.trust_level

        state.update_trust(outcome="success", magnitude=1.0)

        assert state.trust_level > initial_trust
        assert state.successful_actions == 1
        assert state.failed_actions == 0
        assert len(state.trust_trajectory) == 1
        assert state.trust_trajectory[0] == state.trust_level

    def test_update_trust_failure(self):
        """Test updating trust with failure outcome"""
        state = CollaborationState(user_id="user123")
        initial_trust = state.trust_level

        state.update_trust(outcome="failure", magnitude=1.0)

        assert state.trust_level < initial_trust
        assert state.successful_actions == 0
        assert state.failed_actions == 1
        assert len(state.trust_trajectory) == 1

    def test_update_trust_multiple_updates(self):
        """Test multiple trust updates"""
        state = CollaborationState(user_id="user123")

        state.update_trust(outcome="success", magnitude=1.0)
        state.update_trust(outcome="success", magnitude=1.0)
        state.update_trust(outcome="failure", magnitude=0.5)

        assert state.successful_actions == 2
        assert state.failed_actions == 1
        assert len(state.trust_trajectory) == 3

    def test_update_trust_bounds_maximum(self):
        """Test trust level cannot exceed 1.0"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.99

        state.update_trust(outcome="success", magnitude=5.0)

        assert state.trust_level == 1.0

    def test_update_trust_bounds_minimum(self):
        """Test trust level cannot go below 0.0"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.05

        state.update_trust(outcome="failure", magnitude=5.0)

        assert state.trust_level == 0.0

    def test_update_trust_unknown_outcome(self):
        """Test trust update with unknown outcome (no change to counters)"""
        state = CollaborationState(user_id="user123")
        initial_trust = state.trust_level

        # Call with an unknown outcome
        state.update_trust(outcome="unknown", magnitude=1.0)

        # Trust level should remain the same
        assert state.trust_level == initial_trust
        assert state.successful_actions == 0
        assert state.failed_actions == 0
        # Trajectory should still be updated
        assert len(state.trust_trajectory) == 1

    def test_add_pattern_new(self):
        """Test adding a new pattern"""
        state = CollaborationState(user_id="user123")

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )

        state.add_pattern(pattern)

        assert len(state.detected_patterns) == 1
        assert state.detected_patterns[0].trigger == "commit"

    def test_add_pattern_update_existing(self):
        """Test updating an existing pattern"""
        state = CollaborationState(user_id="user123")

        # Add initial pattern
        pattern1 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.7,
            occurrences=3,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern1)

        # Add updated pattern with same type and trigger
        pattern2 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern2)

        # Should still have only one pattern
        assert len(state.detected_patterns) == 1
        # But with updated values
        assert state.detected_patterns[0].confidence == 0.85
        assert state.detected_patterns[0].occurrences == 5

    def test_add_pattern_different_triggers(self):
        """Test adding patterns with different triggers"""
        state = CollaborationState(user_id="user123")

        pattern1 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )

        pattern2 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="deploy",
            action="monitor",
            confidence=0.75,
            occurrences=3,
            last_seen=datetime.now(),
        )

        state.add_pattern(pattern1)
        state.add_pattern(pattern2)

        assert len(state.detected_patterns) == 2

    def test_find_matching_pattern_found(self):
        """Test finding a matching pattern"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.7

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        result = state.find_matching_pattern("I just made a commit")

        assert result is not None
        assert result.trigger == "commit"
        assert result.action == "test"

    def test_find_matching_pattern_not_found(self):
        """Test finding pattern when none match"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.7

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        result = state.find_matching_pattern("I want to deploy")

        assert result is None

    def test_find_matching_pattern_low_trust(self):
        """Test pattern not returned when trust is too low"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.5  # Below threshold

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="commit",
            action="test",
            confidence=0.85,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        result = state.find_matching_pattern("I just made a commit")

        assert result is None

    def test_find_matching_pattern_highest_confidence(self):
        """Test that highest confidence pattern is returned"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.7

        # Add first pattern
        pattern1 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="testing",
            action="action1",
            confidence=0.75,
            occurrences=3,
            last_seen=datetime.now(),
        )

        # Add second pattern with higher confidence but different trigger
        pattern2 = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action2",
            confidence=0.90,
            occurrences=5,
            last_seen=datetime.now(),
        )

        state.add_pattern(pattern1)
        state.add_pattern(pattern2)

        # Both patterns should match since "I need to test this" contains both "test" and "testing"
        # But highest confidence should be returned
        result = state.find_matching_pattern("I need to test this for testing")

        assert result is not None
        assert result.confidence == 0.90
        assert result.action == "action2"

    def test_get_conversation_history_basic(self):
        """Test getting conversation history without metadata"""
        state = CollaborationState(user_id="user123")

        state.add_interaction("user", "Hello", 1, {"context": "greeting"})
        state.add_interaction("assistant", "Hi there", 1, {"context": "greeting"})
        state.add_interaction("user", "How are you?", 2, {"context": "question"})

        history = state.get_conversation_history()

        assert len(history) == 3
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert "metadata" not in history[0]

    def test_get_conversation_history_with_metadata(self):
        """Test getting conversation history with metadata"""
        state = CollaborationState(user_id="user123")

        state.add_interaction("user", "Hello", 1, {"context": "greeting"})
        state.add_interaction("assistant", "Hi there", 1, {"context": "greeting"})

        history = state.get_conversation_history(include_metadata=True)

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Hello"
        assert "metadata" in history[0]
        assert history[0]["metadata"]["context"] == "greeting"

    def test_get_conversation_history_max_turns(self):
        """Test limiting conversation history to max turns"""
        state = CollaborationState(user_id="user123")

        for i in range(15):
            state.add_interaction("user", f"Message {i}", 1)

        history = state.get_conversation_history(max_turns=5)

        assert len(history) == 5
        # Should get the last 5 messages
        assert history[0]["content"] == "Message 10"
        assert history[-1]["content"] == "Message 14"

    def test_get_conversation_history_no_limit(self):
        """Test getting all conversation history"""
        state = CollaborationState(user_id="user123")

        for i in range(15):
            state.add_interaction("user", f"Message {i}", 1)

        history = state.get_conversation_history(max_turns=0)

        assert len(history) == 15

    def test_should_progress_to_level_2(self):
        """Test progression to level 2 (always allowed)"""
        state = CollaborationState(user_id="user123")

        assert state.should_progress_to_level(2) is True

    def test_should_progress_to_level_3_success(self):
        """Test progression to level 3 with sufficient trust and patterns"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.65

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        assert state.should_progress_to_level(3) is True

    def test_should_progress_to_level_3_no_patterns(self):
        """Test progression to level 3 fails without patterns"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.8

        assert state.should_progress_to_level(3) is False

    def test_should_progress_to_level_3_low_trust(self):
        """Test progression to level 3 fails with low trust"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.5

        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        assert state.should_progress_to_level(3) is False

    def test_should_progress_to_level_4_success(self):
        """Test progression to level 4 with sufficient criteria"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.75

        # Add sufficient interactions
        for i in range(15):
            state.add_interaction("user", f"Message {i}", 1)

        # Add sufficient patterns
        for i in range(3):
            pattern = UserPattern(
                pattern_type=PatternType.SEQUENTIAL,
                trigger=f"trigger{i}",
                action="action",
                confidence=0.8,
                occurrences=5,
                last_seen=datetime.now(),
            )
            state.add_pattern(pattern)

        assert state.should_progress_to_level(4) is True

    def test_should_progress_to_level_4_insufficient_interactions(self):
        """Test progression to level 4 fails with few interactions"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.75

        # Only 5 interactions
        for i in range(5):
            state.add_interaction("user", f"Message {i}", 1)

        # Add sufficient patterns
        for i in range(3):
            pattern = UserPattern(
                pattern_type=PatternType.SEQUENTIAL,
                trigger=f"trigger{i}",
                action="action",
                confidence=0.8,
                occurrences=5,
                last_seen=datetime.now(),
            )
            state.add_pattern(pattern)

        assert state.should_progress_to_level(4) is False

    def test_should_progress_to_level_4_insufficient_patterns(self):
        """Test progression to level 4 fails with few patterns"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.75

        # Add sufficient interactions
        for i in range(15):
            state.add_interaction("user", f"Message {i}", 1)

        # Only 1 pattern
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        assert state.should_progress_to_level(4) is False

    def test_should_progress_to_level_5_success(self):
        """Test progression to level 5 with high trust"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.85

        assert state.should_progress_to_level(5) is True

    def test_should_progress_to_level_5_insufficient_trust(self):
        """Test progression to level 5 fails with low trust"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 0.75

        assert state.should_progress_to_level(5) is False

    def test_should_progress_to_level_invalid_level(self):
        """Test progression to invalid level returns False"""
        state = CollaborationState(user_id="user123")
        state.trust_level = 1.0

        # Test with level higher than supported
        assert state.should_progress_to_level(6) is False
        assert state.should_progress_to_level(10) is False
        assert state.should_progress_to_level(100) is False

    def test_get_statistics_empty_state(self):
        """Test getting statistics from empty state"""
        state = CollaborationState(user_id="user123")

        stats = state.get_statistics()

        assert stats["user_id"] == "user123"
        assert stats["total_interactions"] == 0
        assert stats["trust_level"] == 0.5
        assert stats["success_rate"] == 0.0
        assert stats["patterns_detected"] == 0
        assert stats["current_level"] == 1
        assert stats["average_level"] == 1

    def test_get_statistics_with_data(self):
        """Test getting statistics with actual data"""
        state = CollaborationState(user_id="user123")

        # Add interactions
        for i in range(5):
            state.add_interaction("user", f"Message {i}", 1)
            state.add_interaction("assistant", f"Response {i}", 2)

        # Update trust
        state.update_trust("success")
        state.update_trust("success")
        state.update_trust("failure")

        # Add patterns
        pattern = UserPattern(
            pattern_type=PatternType.SEQUENTIAL,
            trigger="test",
            action="action",
            confidence=0.8,
            occurrences=5,
            last_seen=datetime.now(),
        )
        state.add_pattern(pattern)

        stats = state.get_statistics()

        assert stats["total_interactions"] == 10
        assert stats["trust_level"] > 0.5  # Increased from successes
        assert stats["success_rate"] > 0.5  # 2 successes, 1 failure
        assert stats["patterns_detected"] == 1
        assert stats["average_level"] == 2  # All assistant messages used level 2
        assert "session_duration" in stats

    def test_get_statistics_success_rate_calculation(self):
        """Test success rate calculation in statistics"""
        state = CollaborationState(user_id="user123")

        state.update_trust("success")
        state.update_trust("success")
        state.update_trust("success")
        state.update_trust("failure")

        stats = state.get_statistics()

        assert stats["success_rate"] == 0.75  # 3/4


class TestPatternType:
    """Test PatternType enum"""

    def test_pattern_type_values(self):
        """Test PatternType enum values"""
        assert PatternType.SEQUENTIAL.value == "sequential"
        assert PatternType.TEMPORAL.value == "temporal"
        assert PatternType.CONDITIONAL.value == "conditional"
        assert PatternType.PREFERENCE.value == "preference"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
