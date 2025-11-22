"""
Collaboration State Management

Tracks AI-human collaboration over time to enable Level 3+ empathy.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class PatternType(Enum):
    """Types of patterns that can be detected"""

    SEQUENTIAL = "sequential"  # User always does X then Y
    TEMPORAL = "temporal"  # User does X at specific time
    CONDITIONAL = "conditional"  # When Z happens, user does X
    PREFERENCE = "preference"  # User prefers format/style X


@dataclass
class UserPattern:
    """
    A detected pattern in user behavior.

    Enables Level 3 (Proactive) empathy.
    """

    pattern_type: PatternType
    trigger: str  # What triggers this pattern
    action: str  # What user typically does
    confidence: float  # 0.0 to 1.0
    occurrences: int  # How many times observed
    last_seen: datetime
    context: dict[str, Any] = field(default_factory=dict)

    def should_act(self, trust_level: float) -> bool:
        """
        Determine if we should act proactively on this pattern.

        Requires both high confidence and sufficient trust.
        """
        return self.confidence > 0.7 and trust_level > 0.6


@dataclass
class Interaction:
    """Single interaction in conversation history"""

    timestamp: datetime
    role: str  # "user" or "assistant"
    content: str
    empathy_level: int  # Which level was used
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationState:
    """
    Tracks AI-human collaboration state over time.

    This is the foundation for Level 2+ empathy:
    - Level 2: Uses conversation history for context
    - Level 3: Detects patterns, builds trust
    - Level 4: Analyzes trajectory
    - Level 5: Contributes to shared pattern library
    """

    user_id: str
    session_start: datetime = field(default_factory=datetime.now)

    # Conversation tracking
    interactions: list[Interaction] = field(default_factory=list)

    # Pattern detection (Level 3)
    detected_patterns: list[UserPattern] = field(default_factory=list)

    # Trust building
    trust_level: float = 0.5  # 0.0 to 1.0, starts neutral
    successful_actions: int = 0
    failed_actions: int = 0
    trust_trajectory: list[float] = field(default_factory=list)

    # Empathy level progression
    current_level: int = 1  # Start at Level 1
    level_history: list[int] = field(default_factory=list)

    # User preferences learned over time
    preferences: dict[str, Any] = field(default_factory=dict)

    # Context that persists across interactions
    shared_context: dict[str, Any] = field(default_factory=dict)

    def add_interaction(
        self, role: str, content: str, empathy_level: int, metadata: dict | None = None
    ):
        """Add interaction to history"""
        self.interactions.append(
            Interaction(
                timestamp=datetime.now(),
                role=role,
                content=content,
                empathy_level=empathy_level,
                metadata=metadata or {},
            )
        )

        # Track level history
        if role == "assistant":
            self.level_history.append(empathy_level)

    def update_trust(self, outcome: str, magnitude: float = 1.0):
        """
        Update trust level based on action outcome.

        Args:
            outcome: "success" or "failure"
            magnitude: How much to adjust (0.0 to 1.0)
        """
        if outcome == "success":
            adjustment = 0.05 * magnitude
            self.trust_level = min(1.0, self.trust_level + adjustment)
            self.successful_actions += 1
        elif outcome == "failure":
            adjustment = 0.10 * magnitude  # Trust erodes faster
            self.trust_level = max(0.0, self.trust_level - adjustment)
            self.failed_actions += 1

        # Track trajectory
        self.trust_trajectory.append(self.trust_level)

    def add_pattern(self, pattern: UserPattern):
        """Add or update a detected pattern"""
        # Check if pattern already exists
        for existing in self.detected_patterns:
            if (
                existing.pattern_type == pattern.pattern_type
                and existing.trigger == pattern.trigger
            ):
                # Update existing
                existing.occurrences = pattern.occurrences
                existing.confidence = pattern.confidence
                existing.last_seen = pattern.last_seen
                return

        # Add new pattern
        self.detected_patterns.append(pattern)

    def find_matching_pattern(self, trigger_text: str) -> UserPattern | None:
        """
        Find pattern that matches current input.

        Returns pattern with highest confidence if found.
        """
        matches = [
            p
            for p in self.detected_patterns
            if p.trigger.lower() in trigger_text.lower() and p.should_act(self.trust_level)
        ]

        if matches:
            # Return highest confidence match
            return max(matches, key=lambda p: p.confidence)

        return None

    def get_conversation_history(
        self, max_turns: int = 10, include_metadata: bool = False
    ) -> list[dict[str, str]]:
        """
        Get recent conversation history in LLM format.

        Args:
            max_turns: Maximum number of turns to include
            include_metadata: Whether to include interaction metadata

        Returns:
            List of {"role": "user/assistant", "content": "..."}
        """
        recent = self.interactions[-max_turns:] if max_turns else self.interactions

        if include_metadata:
            return [{"role": i.role, "content": i.content, "metadata": i.metadata} for i in recent]
        else:
            return [{"role": i.role, "content": i.content} for i in recent]

    def should_progress_to_level(self, level: int) -> bool:
        """
        Determine if system should progress to higher empathy level.

        Progression criteria:
        - Level 2: Immediate (guided questions always helpful)
        - Level 3: Trust > 0.6, patterns detected
        - Level 4: Trust > 0.7, sufficient history
        - Level 5: Trust > 0.8, cross-domain patterns available
        """
        if level <= 2:
            return True  # Level 2 always appropriate

        if level == 3:
            return self.trust_level > 0.6 and len(self.detected_patterns) > 0

        if level == 4:
            return (
                self.trust_level > 0.7
                and len(self.interactions) > 10
                and len(self.detected_patterns) > 2
            )

        if level == 5:
            return self.trust_level > 0.8

        return False

    def get_statistics(self) -> dict[str, Any]:
        """Get collaboration statistics"""
        total_interactions = len(self.interactions)
        success_rate = (
            self.successful_actions / (self.successful_actions + self.failed_actions)
            if (self.successful_actions + self.failed_actions) > 0
            else 0.0
        )

        return {
            "user_id": self.user_id,
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "total_interactions": total_interactions,
            "trust_level": self.trust_level,
            "success_rate": success_rate,
            "patterns_detected": len(self.detected_patterns),
            "current_level": self.current_level,
            "average_level": (
                sum(self.level_history) / len(self.level_history) if self.level_history else 1
            ),
        }
