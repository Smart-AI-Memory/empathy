"""Pattern Library for Multi-Agent Collaboration

Enables AI agents to share discovered patterns with each other, accelerating
learning across the agent collective (Level 5: Systems Empathy).

One agent's discovery benefits all agents through pattern sharing.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Pattern:
    """A discovered pattern that can be shared across AI agents

    Patterns represent reusable solutions, common behaviors, or
    learned heuristics that one agent discovered and others can benefit from.

    Examples:
    - Sequential patterns: "After action X, users typically need Y"
    - Temporal patterns: "On Mondays, prioritize Z"
    - Conditional patterns: "If context A, then approach B works best"

    """

    id: str
    agent_id: str
    pattern_type: str  # "sequential", "temporal", "conditional", "behavioral"
    name: str
    description: str
    context: dict[str, Any] = field(default_factory=dict)
    code: str | None = None  # Optional code implementation
    confidence: float = 0.5  # 0.0-1.0, how confident in pattern
    usage_count: int = 0
    success_count: int = 0
    failure_count: int = 0
    discovered_at: datetime = field(default_factory=datetime.now)
    last_used: datetime | None = None
    tags: list[str] = field(default_factory=list)

    @property
    def success_rate(self) -> float:
        """Calculate success rate of pattern usage"""
        total_uses = self.success_count + self.failure_count
        if total_uses == 0:
            return 0.0
        return self.success_count / total_uses

    def record_usage(self, success: bool):
        """Record pattern usage outcome"""
        self.usage_count += 1
        if success:
            self.success_count += 1
        else:
            self.failure_count += 1
        self.last_used = datetime.now()

        # Update confidence based on success rate
        if self.usage_count >= 5:
            self.confidence = self.success_rate


@dataclass
class PatternMatch:
    """Result of pattern matching against current context"""

    pattern: Pattern
    relevance_score: float  # 0.0-1.0, how relevant to current context
    matching_factors: list[str]  # What made this pattern match


class PatternLibrary:
    """Shared library for multi-agent pattern discovery and sharing

    Enables Level 5 Systems Empathy: AI-AI cooperation where one agent's
    discovery benefits all agents in the collective.

    **Key Concepts:**
    - **Pattern Discovery**: Agents detect patterns in their interactions
    - **Pattern Contribution**: Agents share patterns with the library
    - **Pattern Querying**: Agents query for relevant patterns before acting
    - **Collective Learning**: All agents benefit from each discovery

    **Pattern Types:**
    1. **Sequential**: "After X, users typically need Y"
    2. **Temporal**: "On Mondays at 9am, prioritize Z"
    3. **Conditional**: "If context A, approach B works best"
    4. **Behavioral**: "Users with trait X prefer style Y"

    Example:
        >>> library = PatternLibrary()
        >>>
        >>> # Agent 1 contributes a pattern
        >>> pattern = Pattern(
        ...     id="pat_001",
        ...     agent_id="compliance_agent",
        ...     pattern_type="sequential",
        ...     name="Post-update documentation pattern",
        ...     description="After system updates, users need help finding changed features",
        ...     confidence=0.85
        ... )
        >>> library.contribute_pattern("compliance_agent", pattern)
        >>>
        >>> # Agent 2 queries for relevant patterns
        >>> context = {"recent_event": "system_update", "user_confusion": True}
        >>> matches = library.query_patterns("documentation_agent", context)
        >>> print(f"Found {len(matches)} relevant patterns")

    """

    def __init__(self):
        """Initialize PatternLibrary with optimized index structures.

        Performance optimizations:
        - patterns_by_type: O(1) lookup by pattern type
        - patterns_by_tag: O(1) lookup by tag
        - Reduces query_patterns from O(n) to O(k) where k = matching patterns
        """
        self.patterns: dict[str, Pattern] = {}  # pattern_id -> Pattern
        self.agent_contributions: dict[str, list[str]] = {}  # agent_id -> pattern_ids
        self.pattern_graph: dict[str, list[str]] = {}  # pattern_id -> related_pattern_ids

        # Performance optimization: Index structures for fast lookups
        self._patterns_by_type: dict[str, list[str]] = {}  # pattern_type -> pattern_ids
        self._patterns_by_tag: dict[str, list[str]] = {}  # tag -> pattern_ids

    def contribute_pattern(self, agent_id: str, pattern: Pattern) -> None:
        """Agent contributes a discovered pattern to the library

        Args:
            agent_id: ID of contributing agent
            pattern: Pattern to contribute

        Raises:
            ValueError: If agent_id is empty or pattern.id already exists

        Example:
            >>> pattern = Pattern(
            ...     id="pat_002",
            ...     agent_id="agent_1",
            ...     pattern_type="conditional",
            ...     name="High-stakes decision pattern",
            ...     description="For high-stakes decisions, provide options with tradeoffs",
            ...     confidence=0.9
            ... )
            >>> library.contribute_pattern("agent_1", pattern)

        """
        # Validate inputs
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id cannot be empty")

        if pattern.id in self.patterns:
            raise ValueError(
                f"Pattern '{pattern.id}' already exists. "
                f"Use a different ID or remove the existing pattern first."
            )

        # Store pattern
        self.patterns[pattern.id] = pattern

        # Track agent contribution
        if agent_id not in self.agent_contributions:
            self.agent_contributions[agent_id] = []
        self.agent_contributions[agent_id].append(pattern.id)

        # Initialize pattern graph entry
        if pattern.id not in self.pattern_graph:
            self.pattern_graph[pattern.id] = []

        # Update index structures for O(1) lookups
        if pattern.pattern_type not in self._patterns_by_type:
            self._patterns_by_type[pattern.pattern_type] = []
        self._patterns_by_type[pattern.pattern_type].append(pattern.id)

        for tag in pattern.tags:
            if tag not in self._patterns_by_tag:
                self._patterns_by_tag[tag] = []
            self._patterns_by_tag[tag].append(pattern.id)

    def query_patterns(
        self,
        agent_id: str,
        context: dict[str, Any],
        pattern_type: str | None = None,
        min_confidence: float = 0.5,
        limit: int = 10,
    ) -> list[PatternMatch]:
        """Query relevant patterns for current context

        Args:
            agent_id: ID of querying agent
            context: Current context dictionary
            pattern_type: Optional filter by pattern type
            min_confidence: Minimum confidence threshold (0-1)
            limit: Maximum patterns to return

        Returns:
            List of PatternMatch objects, sorted by relevance

        Raises:
            ValueError: If agent_id is empty, min_confidence out of range, or limit < 1
            TypeError: If context is not a dictionary

        Example:
            >>> context = {
            ...     "user_role": "developer",
            ...     "task_type": "debugging",
            ...     "time_of_day": "morning"
            ... }
            >>> matches = library.query_patterns("debug_agent", context, min_confidence=0.7)

        """
        # Validate inputs
        if not agent_id or not agent_id.strip():
            raise ValueError("agent_id cannot be empty")

        if not isinstance(context, dict):
            raise TypeError(f"context must be dict, got {type(context).__name__}")

        if not 0.0 <= min_confidence <= 1.0:
            raise ValueError(f"min_confidence must be 0-1, got {min_confidence}")

        if limit < 1:
            raise ValueError(f"limit must be positive, got {limit}")

        matches: list[PatternMatch] = []

        # Performance optimization: Use index for pattern_type filter (O(1) vs O(n))
        if pattern_type:
            # Only check patterns of the requested type
            # Use generator to avoid creating intermediate list
            pattern_ids = self._patterns_by_type.get(pattern_type, [])
            patterns_to_check = (self.patterns[pid] for pid in pattern_ids)
        else:
            # Check all patterns - use generator to avoid materializing all patterns
            patterns_to_check = (p for p in self.patterns.values())

        for pattern in patterns_to_check:
            # Apply confidence filter
            if pattern.confidence < min_confidence:
                continue

            # Calculate relevance
            relevance_score, matching_factors = self._calculate_relevance(pattern, context)

            if relevance_score > 0.3:  # Minimum relevance threshold
                matches.append(
                    PatternMatch(
                        pattern=pattern,
                        relevance_score=relevance_score,
                        matching_factors=matching_factors,
                    ),
                )

        # Sort by relevance and limit
        matches.sort(key=lambda m: m.relevance_score, reverse=True)
        return matches[:limit]

    def get_pattern(self, pattern_id: str) -> Pattern | None:
        """Get a specific pattern by ID

        Args:
            pattern_id: Pattern identifier

        Returns:
            Pattern if found, None otherwise

        """
        return self.patterns.get(pattern_id)

    def get_patterns_by_tag(self, tag: str) -> list[Pattern]:
        """Get all patterns with a specific tag (O(1) lookup).

        Args:
            tag: Tag to search for

        Returns:
            List of patterns with the given tag

        Performance:
            O(1) index lookup instead of O(n) linear scan.

        Example:
            >>> patterns = library.get_patterns_by_tag("debugging")
        """
        pattern_ids = self._patterns_by_tag.get(tag, [])
        # Generator expression for memory efficiency, converted to list for return type
        return [
            self.patterns[pid] for pid in pattern_ids if pid in self.patterns
        ]  # Keep list comp: API returns list, typically small result set

    def get_patterns_by_type(self, pattern_type: str) -> list[Pattern]:
        """Get all patterns of a specific type (O(1) lookup).

        Args:
            pattern_type: Type of patterns to retrieve

        Returns:
            List of patterns of the given type

        Performance:
            O(1) index lookup instead of O(n) linear scan.

        Example:
            >>> patterns = library.get_patterns_by_type("conditional")
        """
        pattern_ids = self._patterns_by_type.get(pattern_type, [])
        return [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]

    def record_pattern_outcome(self, pattern_id: str, success: bool):
        """Record outcome of using a pattern

        Updates pattern statistics to improve future recommendations.

        Args:
            pattern_id: ID of pattern that was used
            success: Whether using the pattern was successful

        Raises:
            ValueError: If pattern_id does not exist

        """
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            raise ValueError(f"Pattern '{pattern_id}' not found. Cannot record outcome.")
        pattern.record_usage(success)

    def link_patterns(self, pattern_id_1: str, pattern_id_2: str):
        """Create a link between related patterns

        Helps agents discover complementary patterns.

        Args:
            pattern_id_1: First pattern ID
            pattern_id_2: Second pattern ID

        Raises:
            ValueError: If either pattern ID doesn't exist or IDs are the same

        """
        # Validate patterns exist
        if pattern_id_1 not in self.patterns:
            raise ValueError(f"Pattern '{pattern_id_1}' does not exist")

        if pattern_id_2 not in self.patterns:
            raise ValueError(f"Pattern '{pattern_id_2}' does not exist")

        if pattern_id_1 == pattern_id_2:
            raise ValueError("Cannot link a pattern to itself")

        # Create bidirectional link
        if pattern_id_1 in self.pattern_graph:
            if pattern_id_2 not in self.pattern_graph[pattern_id_1]:
                self.pattern_graph[pattern_id_1].append(pattern_id_2)

        if pattern_id_2 in self.pattern_graph:
            if pattern_id_1 not in self.pattern_graph[pattern_id_2]:
                self.pattern_graph[pattern_id_2].append(pattern_id_1)

    def get_related_patterns(
        self, pattern_id: str, depth: int = 1, _visited: set[str] | None = None
    ) -> list[Pattern]:
        """Get patterns related to a given pattern

        Args:
            pattern_id: Source pattern ID
            depth: How many hops to traverse (1 = immediate neighbors)
            _visited: Internal tracking to prevent cycles (do not use directly)

        Returns:
            List of related patterns (no duplicates, cycle-safe)

        """
        # Initialize visited set on first call
        if _visited is None:
            _visited = {pattern_id}

        if depth <= 0 or pattern_id not in self.pattern_graph:
            return []

        related_ids = set(self.pattern_graph[pattern_id])

        if depth > 1:
            # Traverse deeper (avoiding cycles)
            for related_id in list(related_ids):
                if related_id not in _visited:
                    _visited.add(related_id)
                    deeper = self.get_related_patterns(related_id, depth - 1, _visited)
                    related_ids.update(p.id for p in deeper)

        # Remove source pattern
        related_ids.discard(pattern_id)

        return [self.patterns[pid] for pid in related_ids if pid in self.patterns]

    def get_agent_patterns(self, agent_id: str) -> list[Pattern]:
        """Get all patterns contributed by a specific agent

        Args:
            agent_id: Agent identifier

        Returns:
            List of patterns from this agent

        """
        pattern_ids = self.agent_contributions.get(agent_id, [])
        return [self.patterns[pid] for pid in pattern_ids if pid in self.patterns]

    def get_top_patterns(self, n: int = 10, sort_by: str = "success_rate") -> list[Pattern]:
        """Get top N patterns by specified metric

        Args:
            n: Number of patterns to return
            sort_by: Metric to sort by ("success_rate", "usage_count", "confidence")

        Returns:
            Top N patterns

        """
        patterns = list(self.patterns.values())

        if sort_by == "success_rate":
            patterns.sort(key=lambda p: p.success_rate, reverse=True)
        elif sort_by == "usage_count":
            patterns.sort(key=lambda p: p.usage_count, reverse=True)
        elif sort_by == "confidence":
            patterns.sort(key=lambda p: p.confidence, reverse=True)

        return patterns[:n]

    def get_library_stats(self) -> dict[str, Any]:
        """Get statistics about the pattern library

        Returns:
            Dict with library statistics

        """
        if not self.patterns:
            return {
                "total_patterns": 0,
                "total_agents": 0,
                "total_usage": 0,
                "average_confidence": 0.0,
                "average_success_rate": 0.0,
            }

        patterns = list(self.patterns.values())
        total_usage = sum(p.usage_count for p in patterns)
        avg_confidence = sum(p.confidence for p in patterns) / len(patterns)

        # Calculate average success rate (only for used patterns)
        used_patterns = [p for p in patterns if p.usage_count > 0]
        avg_success_rate = (
            sum(p.success_rate for p in used_patterns) / len(used_patterns)
            if used_patterns
            else 0.0
        )

        return {
            "total_patterns": len(self.patterns),
            "total_agents": len(self.agent_contributions),
            "total_usage": total_usage,
            "average_confidence": avg_confidence,
            "average_success_rate": avg_success_rate,
            "patterns_by_type": self._count_by_type(),
        }

    def _calculate_relevance(
        self,
        pattern: Pattern,
        context: dict[str, Any],
    ) -> tuple[float, list[str]]:
        """Calculate how relevant a pattern is to current context

        Args:
            pattern: Pattern to evaluate
            context: Current context to match against

        Returns:
            tuple: (relevance_score, matching_factors)
                - relevance_score (float): 0.0-1.0 relevance score
                - matching_factors (list[str]): Human-readable reasons for match

        Algorithm:
            - 50% weight: Context key/value matches
            - 30% weight: Tag matches
            - 20% weight: Pattern success rate boost

        """
        relevance = 0.0
        matching_factors = []

        # Check for direct key matches
        pattern_context_keys = set(pattern.context.keys())
        current_context_keys = set(context.keys())
        common_keys = pattern_context_keys & current_context_keys

        if common_keys:
            # Calculate how many context values match
            matches = sum(1 for key in common_keys if pattern.context.get(key) == context.get(key))
            if common_keys:
                key_match_ratio = matches / len(common_keys)
                relevance += key_match_ratio * 0.5
                if matches > 0:
                    matching_factors.append(f"{matches} context matches")

        # Check for tag matches
        context_tags = context.get("tags", [])
        if context_tags and pattern.tags:
            tag_matches = len(set(context_tags) & set(pattern.tags))
            if tag_matches > 0:
                relevance += min(tag_matches / len(pattern.tags), 1.0) * 0.3
                matching_factors.append(f"{tag_matches} tag matches")

        # Boost by pattern success rate
        if pattern.usage_count > 0:
            relevance += pattern.success_rate * 0.2
            if pattern.success_rate > 0.7:
                matching_factors.append(f"high success rate ({pattern.success_rate:.2f})")

        return min(relevance, 1.0), matching_factors

    def _count_by_type(self) -> dict[str, int]:
        """Count patterns by type"""
        counts: dict[str, int] = {}
        for pattern in self.patterns.values():
            counts[pattern.pattern_type] = counts.get(pattern.pattern_type, 0) + 1
        return counts

    def reset(self):
        """Reset library to empty state"""
        self.patterns = {}
        self.agent_contributions = {}
        self.pattern_graph = {}
        self._patterns_by_type = {}
        self._patterns_by_tag = {}
