"""Tests for Trust Circuit Breaker

Validates the cross-domain transfer from reliability circuit breaker
to trust management.
"""

from datetime import datetime, timedelta

from empathy_os.trust import (
    TrustCircuitBreaker,
    TrustConfig,
    TrustDamageEvent,
    TrustDamageType,
    TrustState,
)

# =============================================================================
# Basic State Tests
# =============================================================================


class TestTrustStates:
    """Test trust state transitions mirror circuit breaker behavior."""

    def test_initial_state_is_full_autonomy(self):
        """New users start with full trust (CLOSED circuit)."""
        breaker = TrustCircuitBreaker(user_id="user_1")
        assert breaker.state == TrustState.FULL_AUTONOMY
        assert breaker.can_act_freely is True

    def test_damage_transitions_to_reduced_autonomy(self):
        """Multiple damage events open the circuit."""
        config = TrustConfig(damage_threshold=3)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        # Record damage events
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        assert breaker.state == TrustState.FULL_AUTONOMY  # Not yet

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        assert breaker.state == TrustState.FULL_AUTONOMY  # Not yet

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        assert breaker.state == TrustState.REDUCED_AUTONOMY  # Circuit opened!
        assert breaker.can_act_freely is False

    def test_high_severity_triggers_faster(self):
        """High severity events can trigger state change faster."""
        config = TrustConfig(damage_threshold=3)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        # One repetitive error (2x weight) + one ignored preference (1.5x)
        breaker.record_damage(TrustDamageType.REPETITIVE_ERROR)  # 2.0
        breaker.record_damage(TrustDamageType.IGNORED_PREFERENCE)  # 1.5
        # Total: 3.5 > threshold 3

        assert breaker.state == TrustState.REDUCED_AUTONOMY


# =============================================================================
# Confirmation Requirements
# =============================================================================


class TestConfirmationRequirements:
    """Test should_require_confirmation logic."""

    def test_full_autonomy_no_confirmation(self):
        """In full autonomy, no confirmation needed."""
        breaker = TrustCircuitBreaker(user_id="user_1")
        assert breaker.should_require_confirmation("file_write") is False
        assert breaker.should_require_confirmation("suggest") is False

    def test_reduced_autonomy_all_confirmation(self):
        """In reduced autonomy, all actions need confirmation."""
        config = TrustConfig(damage_threshold=1)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        assert breaker.state == TrustState.REDUCED_AUTONOMY
        assert breaker.should_require_confirmation("file_write") is True
        assert breaker.should_require_confirmation("suggest") is True
        assert breaker.should_require_confirmation("anything") is True

    def test_supervised_only_high_impact(self):
        """In supervised mode, only high-impact actions need confirmation."""
        config = TrustConfig(
            damage_threshold=1,
            recovery_period_hours=0,  # Immediate transition for test
            high_impact_actions=["file_write", "git_commit"],
        )
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        # Force transition to supervised
        breaker._transition_to_supervised()

        assert breaker.state == TrustState.SUPERVISED
        assert breaker.should_require_confirmation("file_write") is True
        assert breaker.should_require_confirmation("git_commit") is True
        assert breaker.should_require_confirmation("suggest") is False


# =============================================================================
# Recovery Tests
# =============================================================================


class TestTrustRecovery:
    """Test trust recovery (circuit closing)."""

    def test_supervised_successes_restore_trust(self):
        """Successful interactions in supervised mode restore trust."""
        config = TrustConfig(
            damage_threshold=1,
            supervised_successes_required=3,
        )
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        # Damage trust and move to supervised
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        breaker._transition_to_supervised()

        assert breaker.state == TrustState.SUPERVISED

        # Record successes
        breaker.record_success("Good answer")
        breaker.record_success("Good answer")
        assert breaker.state == TrustState.SUPERVISED  # Not yet

        breaker.record_success("Good answer")
        assert breaker.state == TrustState.FULL_AUTONOMY  # Recovered!

    def test_damage_in_supervised_resets_progress(self):
        """Damage during supervised mode sets back recovery."""
        config = TrustConfig(
            damage_threshold=1,
            supervised_successes_required=5,
        )
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        breaker._transition_to_supervised()

        # Build up successes
        breaker.record_success()
        breaker.record_success()
        breaker.record_success()
        assert breaker._supervised_successes == 3

        # Damage resets progress
        breaker.record_damage(TrustDamageType.WRONG_ANSWER, severity=0.5)
        assert breaker._supervised_successes == 1  # Reset by 2

    def test_manual_reset(self):
        """Manual reset restores full trust immediately."""
        config = TrustConfig(damage_threshold=1)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        assert breaker.state == TrustState.REDUCED_AUTONOMY

        breaker.reset()
        assert breaker.state == TrustState.FULL_AUTONOMY
        assert len(breaker._damage_events) == 0


# =============================================================================
# Damage Score Tests
# =============================================================================


class TestDamageScore:
    """Test damage score calculation."""

    def test_damage_score_accumulates(self):
        """Damage score is sum of weighted events."""
        breaker = TrustCircuitBreaker(user_id="user_1")

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)  # 1.0
        score1 = breaker.damage_score
        assert 0.9 < score1 < 1.1  # ~1.0 with recency factor

        breaker.record_damage(TrustDamageType.SLOW_RESPONSE)  # 0.3
        score2 = breaker.damage_score
        assert score2 > score1

    def test_old_events_decay(self):
        """Old events have less impact (time decay)."""
        config = TrustConfig(damage_window_hours=24)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        # Add an "old" event
        old_event = TrustDamageEvent(
            event_type=TrustDamageType.WRONG_ANSWER,
            timestamp=datetime.now() - timedelta(hours=20),
        )
        breaker._damage_events.append(old_event)

        # Add a recent event
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        # Recent event should have higher contribution
        # Old event at 20h in 24h window = 0.5 recency factor
        # New event at 0h = 1.0 recency factor
        score = breaker.damage_score
        assert 1.0 < score < 2.0


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Test state persistence."""

    def test_round_trip_serialization(self):
        """State survives serialization round-trip."""
        config = TrustConfig(damage_threshold=3)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config, domain="code_review")

        breaker.record_damage(TrustDamageType.WRONG_ANSWER, context="Bad code review")
        breaker.record_damage(TrustDamageType.IGNORED_PREFERENCE)

        # Serialize
        data = breaker.to_dict()

        # Restore
        restored = TrustCircuitBreaker.from_dict(data)

        assert restored.user_id == breaker.user_id
        assert restored.domain == breaker.domain
        assert restored.state == breaker.state
        assert len(restored._damage_events) == len(breaker._damage_events)
        assert restored._damage_events[0].event_type == TrustDamageType.WRONG_ANSWER
        assert restored._damage_events[0].context == "Bad code review"


# =============================================================================
# Callback Tests
# =============================================================================


class TestCallbacks:
    """Test state change callbacks."""

    def test_callback_on_state_change(self):
        """Callback is invoked when state changes."""
        config = TrustConfig(damage_threshold=1)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)

        transitions = []

        def on_change(old: TrustState, new: TrustState):
            transitions.append((old, new))

        breaker.on_state_change(on_change)

        breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        assert len(transitions) == 1
        assert transitions[0] == (TrustState.FULL_AUTONOMY, TrustState.REDUCED_AUTONOMY)


# =============================================================================
# Autonomy Level Info Tests
# =============================================================================


class TestAutonomyLevelInfo:
    """Test get_autonomy_level information."""

    def test_full_autonomy_info(self):
        """Full autonomy returns correct info."""
        breaker = TrustCircuitBreaker(user_id="user_1")
        info = breaker.get_autonomy_level()

        assert info["state"] == "full_autonomy"
        assert info["can_act_freely"] is True
        assert info["damage_score"] == 0
        assert info["recovery_progress"]["status"] == "full_trust"

    def test_reduced_autonomy_info(self):
        """Reduced autonomy shows cooling off progress."""
        config = TrustConfig(damage_threshold=1, recovery_period_hours=24)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        info = breaker.get_autonomy_level()

        assert info["state"] == "reduced_autonomy"
        assert info["can_act_freely"] is False
        assert info["recovery_progress"]["status"] == "cooling_off"
        assert "time_remaining_hours" in info["recovery_progress"]

    def test_supervised_info(self):
        """Supervised mode shows success progress."""
        config = TrustConfig(damage_threshold=1, supervised_successes_required=5)
        breaker = TrustCircuitBreaker(user_id="user_1", config=config)
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        breaker._transition_to_supervised()
        breaker.record_success()
        breaker.record_success()

        info = breaker.get_autonomy_level()

        assert info["state"] == "supervised"
        assert info["recovery_progress"]["status"] == "supervised_testing"
        assert info["recovery_progress"]["successes"] == 2
        assert info["recovery_progress"]["required"] == 5


# =============================================================================
# Integration Example Tests
# =============================================================================


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""

    def test_developer_onboarding_journey(self):
        """Simulate a developer's trust journey over time."""
        config = TrustConfig(
            damage_threshold=3,
            recovery_period_hours=0,  # Immediate transition for test
            supervised_successes_required=3,
        )
        breaker = TrustCircuitBreaker(user_id="dev_1", config=config)

        # Week 1: Some mistakes while learning
        breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        breaker.record_damage(TrustDamageType.MISUNDERSTOOD_INTENT)
        assert breaker.state == TrustState.FULL_AUTONOMY  # Still OK

        # Big mistake - triggers transition
        breaker.record_damage(TrustDamageType.REPETITIVE_ERROR)  # 2x weight
        # With 0 recovery period, accessing state immediately transitions to supervised
        assert breaker.state == TrustState.SUPERVISED  # Immediately in supervised mode

        # Build trust back
        breaker.record_success("Fixed the bug correctly")
        breaker.record_success("Good code review")
        breaker.record_success("Helpful documentation")
        assert breaker.state == TrustState.FULL_AUTONOMY  # Trust restored!

    def test_domain_specific_trust(self):
        """Different domains can have different trust states."""
        code_breaker = TrustCircuitBreaker(
            user_id="dev_1",
            domain="code_review",
            config=TrustConfig(damage_threshold=2),
        )
        doc_breaker = TrustCircuitBreaker(
            user_id="dev_1",
            domain="documentation",
            config=TrustConfig(damage_threshold=2),
        )

        # Damage trust in code review
        code_breaker.record_damage(TrustDamageType.WRONG_ANSWER)
        code_breaker.record_damage(TrustDamageType.WRONG_ANSWER)

        assert code_breaker.state == TrustState.REDUCED_AUTONOMY
        assert doc_breaker.state == TrustState.FULL_AUTONOMY  # Unaffected
