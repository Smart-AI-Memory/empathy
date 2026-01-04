"""Trust Circuit Breaker

A cross-domain transfer of the circuit breaker pattern from reliability engineering
to human-AI trust management. Just as circuit breakers protect systems from cascading
failures, trust circuit breakers protect the AI-user relationship from trust erosion.

Pattern Origin: src/empathy_os/resilience/circuit_breaker.py
Transfer Documentation: patterns/cross-domain/circuit-breaker-to-trust.md

Level: 5 (Systems Thinking) - Applying patterns across domains
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# =============================================================================
# Trust States (mapped from circuit breaker states)
# =============================================================================


class TrustState(Enum):
    """Trust states mapped from circuit breaker states.

    Circuit Breaker → Trust Mapping:
    - CLOSED (normal) → FULL_AUTONOMY (AI acts freely)
    - OPEN (failing fast) → REDUCED_AUTONOMY (require confirmation)
    - HALF_OPEN (testing) → SUPERVISED (monitored recovery)
    """

    FULL_AUTONOMY = "full_autonomy"
    """AI can act without confirmation. User trusts AI decisions."""

    REDUCED_AUTONOMY = "reduced_autonomy"
    """AI must confirm significant actions. Trust has been damaged."""

    SUPERVISED = "supervised"
    """AI is being tested for trust recovery. Partial confirmation needed."""


# =============================================================================
# Trust Events
# =============================================================================


class TrustDamageType(Enum):
    """Types of events that damage trust."""

    WRONG_ANSWER = "wrong_answer"
    """AI provided incorrect information."""

    IGNORED_PREFERENCE = "ignored_preference"
    """AI acted against user's stated preferences."""

    UNEXPECTED_ACTION = "unexpected_action"
    """AI did something user didn't expect or want."""

    SLOW_RESPONSE = "slow_response"
    """AI was too slow, breaking flow."""

    MISUNDERSTOOD_INTENT = "misunderstood_intent"
    """AI misinterpreted what user wanted."""

    REPETITIVE_ERROR = "repetitive_error"
    """AI made the same mistake again."""


@dataclass
class TrustDamageEvent:
    """Record of an event that damaged trust."""

    event_type: TrustDamageType
    timestamp: datetime = field(default_factory=datetime.now)
    context: str = ""
    severity: float = 1.0  # 0.0 to 1.0, higher = more damage
    user_explicit: bool = False  # User explicitly indicated damage

    def __post_init__(self):
        if isinstance(self.event_type, str):
            self.event_type = TrustDamageType(self.event_type)


@dataclass
class TrustRecoveryEvent:
    """Record of an event that builds trust."""

    timestamp: datetime = field(default_factory=datetime.now)
    context: str = ""
    user_explicit: bool = False  # User explicitly praised AI


# =============================================================================
# Configuration
# =============================================================================


@dataclass
class TrustConfig:
    """Configuration for trust circuit breaker.

    Mapped from circuit breaker config with trust-specific adaptations.
    """

    # Damage thresholds (mapped from failure_threshold)
    damage_threshold: int = 3
    """Number of trust-damaging events before reducing autonomy."""

    damage_window_hours: float = 24.0
    """Time window for counting damage events (recent damage matters more)."""

    # Recovery settings (mapped from reset_timeout)
    recovery_period_hours: float = 24.0
    """Minimum time in reduced autonomy before testing recovery."""

    supervised_successes_required: int = 5
    """Successful interactions in supervised mode before full recovery."""

    # Severity weights
    severity_weights: dict[TrustDamageType, float] = field(
        default_factory=lambda: {
            TrustDamageType.WRONG_ANSWER: 1.0,
            TrustDamageType.IGNORED_PREFERENCE: 1.5,  # Preferences are important
            TrustDamageType.UNEXPECTED_ACTION: 1.2,
            TrustDamageType.SLOW_RESPONSE: 0.3,  # Minor
            TrustDamageType.MISUNDERSTOOD_INTENT: 0.8,
            TrustDamageType.REPETITIVE_ERROR: 2.0,  # Very damaging
        },
    )

    # Domain-specific settings
    domain_isolation: bool = True
    """If True, trust is tracked per-domain (code review vs documentation)."""

    # Actions requiring confirmation in each state
    high_impact_actions: list[str] = field(
        default_factory=lambda: [
            "file_write",
            "file_delete",
            "git_commit",
            "external_api_call",
            "code_execution",
        ],
    )


# =============================================================================
# Trust Circuit Breaker
# =============================================================================


class TrustCircuitBreaker:
    """Circuit breaker for AI autonomy based on user trust.

    Cross-domain transfer: Uses the same state machine as reliability
    circuit breakers, but applied to trust management.

    State Transitions:
    ```
    FULL_AUTONOMY ──(damage threshold)──→ REDUCED_AUTONOMY
         ↑                                       │
         │                              (recovery period)
         │                                       ↓
         └──(supervised successes)─── SUPERVISED
    ```
    """

    def __init__(
        self,
        user_id: str,
        config: TrustConfig | None = None,
        domain: str = "general",
    ):
        self.user_id = user_id
        self.config = config or TrustConfig()
        self.domain = domain

        # State tracking
        self._state = TrustState.FULL_AUTONOMY
        self._damage_events: list[TrustDamageEvent] = []
        self._recovery_events: list[TrustRecoveryEvent] = []
        self._state_changed_at: datetime = datetime.now()
        self._supervised_successes: int = 0

        # Callbacks
        self._on_state_change: Callable[[TrustState, TrustState], None] | None = None

    # =========================================================================
    # State Properties
    # =========================================================================

    @property
    def state(self) -> TrustState:
        """Get current trust state, checking for recovery eligibility."""
        self._check_recovery_eligibility()
        return self._state

    @property
    def damage_score(self) -> float:
        """Calculate current damage score (weighted sum of recent events).

        Higher score = more damage. Threshold triggers state change.
        """
        window_start = datetime.now() - timedelta(hours=self.config.damage_window_hours)
        recent_events = [e for e in self._damage_events if e.timestamp > window_start]

        score = 0.0
        for event in recent_events:
            weight = self.config.severity_weights.get(event.event_type, 1.0)
            # More recent events count more (time decay)
            age_hours = (datetime.now() - event.timestamp).total_seconds() / 3600
            recency_factor = max(0.5, 1.0 - (age_hours / self.config.damage_window_hours))
            score += event.severity * weight * recency_factor

        return score

    @property
    def can_act_freely(self) -> bool:
        """Check if AI can act without confirmation."""
        return self.state == TrustState.FULL_AUTONOMY

    @property
    def time_in_current_state(self) -> timedelta:
        """How long we've been in the current state."""
        return datetime.now() - self._state_changed_at

    # =========================================================================
    # Decision Methods
    # =========================================================================

    def should_require_confirmation(self, action: str) -> bool:
        """Check if an action requires user confirmation.

        Args:
            action: The action being considered (e.g., "file_write", "suggest")

        Returns:
            True if confirmation should be requested

        """
        current_state = self.state

        if current_state == TrustState.FULL_AUTONOMY:
            return False

        if current_state == TrustState.REDUCED_AUTONOMY:
            return True  # All actions need confirmation

        if current_state == TrustState.SUPERVISED:
            # Only high-impact actions need confirmation
            return action in self.config.high_impact_actions

        return True  # Default to safe

    def get_autonomy_level(self) -> dict[str, Any]:
        """Get detailed autonomy level information for UI display.

        Returns dict with state, allowed actions, and recovery progress.
        """
        state = self.state

        return {
            "state": state.value,
            "can_act_freely": state == TrustState.FULL_AUTONOMY,
            "damage_score": round(self.damage_score, 2),
            "damage_threshold": self.config.damage_threshold,
            "time_in_state_hours": round(self.time_in_current_state.total_seconds() / 3600, 1),
            "recovery_progress": self._get_recovery_progress(),
            "recent_damage_count": len(
                [
                    e
                    for e in self._damage_events
                    if e.timestamp > datetime.now() - timedelta(hours=24)
                ],
            ),
        }

    def _get_recovery_progress(self) -> dict[str, Any]:
        """Get progress toward trust recovery."""
        if self._state == TrustState.FULL_AUTONOMY:
            return {"status": "full_trust", "progress": 1.0}

        if self._state == TrustState.REDUCED_AUTONOMY:
            time_remaining = (
                timedelta(hours=self.config.recovery_period_hours) - self.time_in_current_state
            )
            if time_remaining.total_seconds() > 0:
                return {
                    "status": "cooling_off",
                    "progress": self.time_in_current_state.total_seconds()
                    / (self.config.recovery_period_hours * 3600),
                    "time_remaining_hours": round(time_remaining.total_seconds() / 3600, 1),
                }
            return {"status": "ready_for_supervised", "progress": 0.5}

        if self._state == TrustState.SUPERVISED:
            return {
                "status": "supervised_testing",
                "progress": 0.5
                + (0.5 * self._supervised_successes / self.config.supervised_successes_required),
                "successes": self._supervised_successes,
                "required": self.config.supervised_successes_required,
            }

        return {"status": "unknown", "progress": 0.0}

    # =========================================================================
    # Event Recording
    # =========================================================================

    def record_damage(
        self,
        event_type: TrustDamageType | str,
        context: str = "",
        severity: float = 1.0,
        user_explicit: bool = False,
    ) -> TrustState:
        """Record an event that damaged trust.

        This is analogous to recording a failure in the reliability circuit breaker.

        Args:
            event_type: Type of trust damage
            context: Description of what happened
            severity: 0.0-1.0, how severe the damage was
            user_explicit: True if user explicitly indicated damage

        Returns:
            The new trust state after recording

        """
        if isinstance(event_type, str):
            event_type = TrustDamageType(event_type)

        event = TrustDamageEvent(
            event_type=event_type,
            context=context,
            severity=severity,
            user_explicit=user_explicit,
        )
        self._damage_events.append(event)

        logger.info(
            f"Trust damage recorded for user {self.user_id}: "
            f"{event_type.value} (severity={severity})",
        )

        # Check if we should transition to reduced autonomy
        # Use small epsilon for floating point comparison (recency factor can cause tiny errors)
        if self._state == TrustState.FULL_AUTONOMY:
            if self.damage_score >= (self.config.damage_threshold - 0.01):
                self._transition_to_reduced_autonomy()

        # If in supervised mode, a damage event resets progress
        elif self._state == TrustState.SUPERVISED:
            self._supervised_successes = max(0, self._supervised_successes - 2)
            logger.info(
                f"Trust damage in supervised mode, successes reset to {self._supervised_successes}",
            )

        return self._state

    def record_success(self, context: str = "", user_explicit: bool = False) -> TrustState:
        """Record a successful/positive interaction.

        This is analogous to recording a success in the reliability circuit breaker.

        Args:
            context: Description of the positive interaction
            user_explicit: True if user explicitly praised the AI

        Returns:
            The new trust state after recording

        """
        event = TrustRecoveryEvent(
            context=context,
            user_explicit=user_explicit,
        )
        self._recovery_events.append(event)

        # In supervised mode, successes count toward recovery
        if self._state == TrustState.SUPERVISED:
            self._supervised_successes += 1
            logger.info(
                f"Trust success in supervised mode: "
                f"{self._supervised_successes}/{self.config.supervised_successes_required}",
            )

            if self._supervised_successes >= self.config.supervised_successes_required:
                self._transition_to_full_autonomy()

        return self._state

    # =========================================================================
    # State Transitions
    # =========================================================================

    def _check_recovery_eligibility(self) -> None:
        """Check if we should transition from reduced to supervised."""
        if self._state != TrustState.REDUCED_AUTONOMY:
            return

        time_in_state = self.time_in_current_state
        recovery_period = timedelta(hours=self.config.recovery_period_hours)

        if time_in_state >= recovery_period:
            self._transition_to_supervised()

    def _transition_to_reduced_autonomy(self) -> None:
        """Transition to reduced autonomy (circuit opens)."""
        old_state = self._state
        self._state = TrustState.REDUCED_AUTONOMY
        self._state_changed_at = datetime.now()
        self._supervised_successes = 0

        logger.warning(
            f"Trust circuit opened for user {self.user_id}: {old_state.value} → {self._state.value}",
        )

        if self._on_state_change:
            self._on_state_change(old_state, self._state)

    def _transition_to_supervised(self) -> None:
        """Transition to supervised mode (circuit half-opens)."""
        old_state = self._state
        self._state = TrustState.SUPERVISED
        self._state_changed_at = datetime.now()
        self._supervised_successes = 0

        logger.info(
            f"Trust circuit half-opened for user {self.user_id}: "
            f"{old_state.value} → {self._state.value}",
        )

        if self._on_state_change:
            self._on_state_change(old_state, self._state)

    def _transition_to_full_autonomy(self) -> None:
        """Transition to full autonomy (circuit closes)."""
        old_state = self._state
        self._state = TrustState.FULL_AUTONOMY
        self._state_changed_at = datetime.now()

        # Clear old damage events
        cutoff = datetime.now() - timedelta(hours=self.config.damage_window_hours * 2)
        self._damage_events = [e for e in self._damage_events if e.timestamp > cutoff]

        logger.info(
            f"Trust circuit closed for user {self.user_id}: {old_state.value} → {self._state.value}",
        )

        if self._on_state_change:
            self._on_state_change(old_state, self._state)

    # =========================================================================
    # Manual Controls
    # =========================================================================

    def reset(self) -> None:
        """Manually reset trust to full autonomy.

        Use with caution - this skips the normal recovery process.
        """
        old_state = self._state
        self._state = TrustState.FULL_AUTONOMY
        self._state_changed_at = datetime.now()
        self._damage_events.clear()
        self._supervised_successes = 0

        logger.info(f"Trust manually reset for user {self.user_id}")

        if self._on_state_change:
            self._on_state_change(old_state, self._state)

    def on_state_change(self, callback: Callable[[TrustState, TrustState], None]) -> None:
        """Register a callback for state changes."""
        self._on_state_change = callback

    # =========================================================================
    # Serialization
    # =========================================================================

    def to_dict(self) -> dict[str, Any]:
        """Serialize state for persistence."""
        return {
            "user_id": self.user_id,
            "domain": self.domain,
            "state": self._state.value,
            "state_changed_at": self._state_changed_at.isoformat(),
            "supervised_successes": self._supervised_successes,
            "damage_events": [
                {
                    "event_type": e.event_type.value,
                    "timestamp": e.timestamp.isoformat(),
                    "context": e.context,
                    "severity": e.severity,
                    "user_explicit": e.user_explicit,
                }
                for e in self._damage_events
            ],
            "config": {
                "damage_threshold": self.config.damage_threshold,
                "recovery_period_hours": self.config.recovery_period_hours,
                "supervised_successes_required": self.config.supervised_successes_required,
            },
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> TrustCircuitBreaker:
        """Restore from serialized state."""
        config = TrustConfig(
            damage_threshold=data["config"]["damage_threshold"],
            recovery_period_hours=data["config"]["recovery_period_hours"],
            supervised_successes_required=data["config"]["supervised_successes_required"],
        )

        instance = cls(
            user_id=data["user_id"],
            config=config,
            domain=data.get("domain", "general"),
        )

        instance._state = TrustState(data["state"])
        instance._state_changed_at = datetime.fromisoformat(data["state_changed_at"])
        instance._supervised_successes = data.get("supervised_successes", 0)

        for e in data.get("damage_events", []):
            instance._damage_events.append(
                TrustDamageEvent(
                    event_type=TrustDamageType(e["event_type"]),
                    timestamp=datetime.fromisoformat(e["timestamp"]),
                    context=e.get("context", ""),
                    severity=e.get("severity", 1.0),
                    user_explicit=e.get("user_explicit", False),
                ),
            )

        return instance


# =============================================================================
# Convenience Functions
# =============================================================================


def create_trust_breaker(
    user_id: str,
    domain: str = "general",
    strict: bool = False,
) -> TrustCircuitBreaker:
    """Create a trust circuit breaker with preset configurations.

    Args:
        user_id: User identifier
        domain: Domain for trust tracking (if domain_isolation enabled)
        strict: If True, use stricter thresholds (fewer mistakes allowed)

    Returns:
        Configured TrustCircuitBreaker instance

    """
    if strict:
        config = TrustConfig(
            damage_threshold=2,
            recovery_period_hours=48.0,
            supervised_successes_required=10,
        )
    else:
        config = TrustConfig()  # Defaults

    return TrustCircuitBreaker(user_id=user_id, config=config, domain=domain)
