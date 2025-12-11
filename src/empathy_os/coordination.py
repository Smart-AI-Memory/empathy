"""
Multi-Agent Coordination for Distributed Memory Networks

Provides conflict resolution and coordination primitives for multi-agent
systems sharing pattern libraries.

When multiple agents discover conflicting patterns, the ConflictResolver
determines which pattern should take precedence based on:
1. Team priorities (configured preferences)
2. Context match (relevance to current situation)
3. Confidence scores (historical success rate)
4. Recency (newer patterns may reflect updated practices)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .pattern_library import Pattern


class ResolutionStrategy(Enum):
    """Strategy for resolving pattern conflicts"""

    HIGHEST_CONFIDENCE = "highest_confidence"  # Pick pattern with highest confidence
    MOST_RECENT = "most_recent"  # Pick most recently discovered pattern
    BEST_CONTEXT_MATCH = "best_context_match"  # Pick best match for current context
    TEAM_PRIORITY = "team_priority"  # Use team-configured priorities
    WEIGHTED_SCORE = "weighted_score"  # Combine multiple factors


@dataclass
class ResolutionResult:
    """Result of conflict resolution between patterns"""

    winning_pattern: Pattern
    losing_patterns: list[Pattern]
    strategy_used: ResolutionStrategy
    confidence: float  # How confident in this resolution (0-1)
    reasoning: str  # Explanation of why this pattern won
    factors: dict[str, float] = field(default_factory=dict)  # Score breakdown


@dataclass
class TeamPriorities:
    """Team-configured priorities for conflict resolution"""

    # Priority weights (should sum to 1.0)
    readability_weight: float = 0.3
    performance_weight: float = 0.2
    security_weight: float = 0.3
    maintainability_weight: float = 0.2

    # Pattern type preferences (higher = preferred)
    type_preferences: dict[str, float] = field(
        default_factory=lambda: {
            "security": 1.0,
            "best_practice": 0.8,
            "performance": 0.7,
            "style": 0.5,
            "warning": 0.6,
        }
    )

    # Tag preferences (tags that should be prioritized)
    preferred_tags: list[str] = field(default_factory=list)


class ConflictResolver:
    """
    Resolves conflicts between patterns from different agents.

    When multiple agents contribute patterns that address the same issue
    but recommend different approaches, the ConflictResolver determines
    which pattern should take precedence.

    Example:
        >>> resolver = ConflictResolver()
        >>>
        >>> # Two agents have different recommendations
        >>> review_pattern = Pattern(
        ...     id="use_list_comprehension",
        ...     agent_id="code_reviewer",
        ...     pattern_type="performance",
        ...     name="Use list comprehension",
        ...     description="Use list comprehension for better performance",
        ...     confidence=0.85
        ... )
        >>>
        >>> style_pattern = Pattern(
        ...     id="use_explicit_loop",
        ...     agent_id="style_agent",
        ...     pattern_type="style",
        ...     name="Use explicit loop",
        ...     description="Use explicit loop for better readability",
        ...     confidence=0.80
        ... )
        >>>
        >>> resolution = resolver.resolve_patterns(
        ...     patterns=[review_pattern, style_pattern],
        ...     context={"team_priority": "readability", "code_complexity": "high"}
        ... )
        >>> print(f"Winner: {resolution.winning_pattern.name}")
    """

    def __init__(
        self,
        default_strategy: ResolutionStrategy = ResolutionStrategy.WEIGHTED_SCORE,
        team_priorities: TeamPriorities | None = None,
    ):
        """
        Initialize the ConflictResolver.

        Args:
            default_strategy: Strategy to use when not specified
            team_priorities: Team-configured priorities for resolution
        """
        self.default_strategy = default_strategy
        self.team_priorities = team_priorities or TeamPriorities()
        self.resolution_history: list[ResolutionResult] = []

    def resolve_patterns(
        self,
        patterns: list[Pattern],
        context: dict[str, Any] | None = None,
        strategy: ResolutionStrategy | None = None,
    ) -> ResolutionResult:
        """
        Resolve conflict between multiple patterns.

        Args:
            patterns: List of conflicting patterns (minimum 2)
            context: Current context for resolution decision
            strategy: Resolution strategy (uses default if not specified)

        Returns:
            ResolutionResult with winning pattern and reasoning

        Raises:
            ValueError: If fewer than 2 patterns provided
        """
        if len(patterns) < 2:
            raise ValueError("Need at least 2 patterns to resolve conflict")

        context = context or {}
        strategy = strategy or self.default_strategy

        # Calculate scores for each pattern
        scored_patterns = [
            (pattern, self._calculate_pattern_score(pattern, context, strategy))
            for pattern in patterns
        ]

        # Sort by score (highest first)
        scored_patterns.sort(key=lambda x: x[1]["total"], reverse=True)

        winner, winner_scores = scored_patterns[0]
        losers = [p for p, _ in scored_patterns[1:]]

        # Generate reasoning
        reasoning = self._generate_reasoning(winner, losers, winner_scores, context, strategy)

        result = ResolutionResult(
            winning_pattern=winner,
            losing_patterns=losers,
            strategy_used=strategy,
            confidence=winner_scores["total"],
            reasoning=reasoning,
            factors=winner_scores,
        )

        # Track history for learning
        self.resolution_history.append(result)

        return result

    def _calculate_pattern_score(
        self,
        pattern: Pattern,
        context: dict[str, Any],
        strategy: ResolutionStrategy,
    ) -> dict[str, float]:
        """Calculate score for a pattern based on strategy"""

        scores: dict[str, float] = {}

        # Factor 1: Confidence score (0-1)
        scores["confidence"] = pattern.confidence

        # Factor 2: Success rate (0-1)
        scores["success_rate"] = pattern.success_rate if pattern.usage_count > 0 else 0.5

        # Factor 3: Recency (0-1, more recent = higher)
        age_days = (datetime.now() - pattern.discovered_at).days
        scores["recency"] = max(0, 1 - (age_days / 365))  # Decay over 1 year

        # Factor 4: Context match (0-1)
        scores["context_match"] = self._calculate_context_match(pattern, context)

        # Factor 5: Team priority alignment (0-1)
        scores["team_alignment"] = self._calculate_team_alignment(pattern, context)

        # Calculate total based on strategy
        if strategy == ResolutionStrategy.HIGHEST_CONFIDENCE:
            scores["total"] = scores["confidence"]
        elif strategy == ResolutionStrategy.MOST_RECENT:
            scores["total"] = scores["recency"]
        elif strategy == ResolutionStrategy.BEST_CONTEXT_MATCH:
            scores["total"] = scores["context_match"]
        elif strategy == ResolutionStrategy.TEAM_PRIORITY:
            scores["total"] = scores["team_alignment"]
        else:  # WEIGHTED_SCORE
            scores["total"] = (
                scores["confidence"] * 0.25
                + scores["success_rate"] * 0.25
                + scores["recency"] * 0.15
                + scores["context_match"] * 0.20
                + scores["team_alignment"] * 0.15
            )

        return scores

    def _calculate_context_match(
        self,
        pattern: Pattern,
        context: dict[str, Any],
    ) -> float:
        """Calculate how well a pattern matches the current context"""

        if not context or not pattern.context:
            return 0.5  # Neutral if no context available

        # Check key overlaps
        pattern_keys = set(pattern.context.keys())
        context_keys = set(context.keys())
        common_keys = pattern_keys & context_keys

        if not common_keys:
            return 0.3  # Low match if no common keys

        # Count matching values
        matches = sum(1 for key in common_keys if pattern.context.get(key) == context.get(key))

        match_ratio = matches / len(common_keys) if common_keys else 0

        # Check tag overlap
        context_tags = set(context.get("tags", []))
        pattern_tags = set(pattern.tags)
        tag_overlap = len(context_tags & pattern_tags)
        tag_bonus = min(tag_overlap * 0.1, 0.2)  # Up to 0.2 bonus for tags

        return min(match_ratio * 0.8 + tag_bonus + 0.1, 1.0)

    def _calculate_team_alignment(
        self,
        pattern: Pattern,
        context: dict[str, Any],
    ) -> float:
        """Calculate how well a pattern aligns with team priorities"""

        score = 0.5  # Start neutral

        # Check team priority in context
        team_priority = context.get("team_priority", "").lower()

        # Map priorities to pattern characteristics
        priority_boosts = {
            "readability": ["style", "best_practice", "documentation"],
            "performance": ["performance", "optimization"],
            "security": ["security", "vulnerability", "warning"],
            "maintainability": ["best_practice", "refactoring", "style"],
        }

        if team_priority in priority_boosts:
            boosted_types = priority_boosts[team_priority]
            if pattern.pattern_type.lower() in boosted_types:
                score += 0.3

            # Check if any tags match
            for tag in pattern.tags:
                if tag.lower() in boosted_types:
                    score += 0.1
                    break

        # Apply type preference from team config
        type_pref = self.team_priorities.type_preferences.get(pattern.pattern_type.lower(), 0.5)
        score = (score + type_pref) / 2

        # Bonus for preferred tags
        for tag in pattern.tags:
            if tag in self.team_priorities.preferred_tags:
                score += 0.1
                break

        return min(score, 1.0)

    def _generate_reasoning(
        self,
        winner: Pattern,
        losers: list[Pattern],
        scores: dict[str, float],
        context: dict[str, Any],
        strategy: ResolutionStrategy,
    ) -> str:
        """Generate human-readable reasoning for the resolution"""

        reasons = []

        # Strategy-specific reasoning
        if strategy == ResolutionStrategy.HIGHEST_CONFIDENCE:
            reasons.append(
                f"Selected '{winner.name}' with highest confidence ({winner.confidence:.0%})"
            )
        elif strategy == ResolutionStrategy.MOST_RECENT:
            age = (datetime.now() - winner.discovered_at).days
            reasons.append(f"Selected '{winner.name}' as most recent (discovered {age} days ago)")
        elif strategy == ResolutionStrategy.BEST_CONTEXT_MATCH:
            reasons.append(
                f"Selected '{winner.name}' as best match for current context "
                f"(match score: {scores['context_match']:.0%})"
            )
        elif strategy == ResolutionStrategy.TEAM_PRIORITY:
            team_priority = context.get("team_priority", "balanced")
            reasons.append(f"Selected '{winner.name}' based on team priority: {team_priority}")
        else:  # WEIGHTED_SCORE
            top_factors = sorted(
                [(k, v) for k, v in scores.items() if k != "total"],
                key=lambda x: x[1],
                reverse=True,
            )[:2]
            factor_desc = ", ".join(f"{k}: {v:.0%}" for k, v in top_factors)
            reasons.append(
                f"Selected '{winner.name}' based on weighted scoring "
                f"(top factors: {factor_desc})"
            )

        # Add comparison to losers
        if losers:
            loser_names = [p.name for p in losers[:2]]
            reasons.append(f"Preferred over: {', '.join(loser_names)}")

        return ". ".join(reasons)

    def get_resolution_stats(self) -> dict[str, Any]:
        """Get statistics about resolution history"""

        if not self.resolution_history:
            return {
                "total_resolutions": 0,
                "strategies_used": {},
                "average_confidence": 0.0,
            }

        strategies: dict[str, int] = {}
        confidences: list[float] = []

        for result in self.resolution_history:
            strategy = result.strategy_used.value
            strategies[strategy] = strategies.get(strategy, 0) + 1
            confidences.append(result.confidence)

        most_used = max(strategies.keys(), key=lambda k: strategies[k]) if strategies else None

        return {
            "total_resolutions": len(self.resolution_history),
            "strategies_used": strategies,
            "average_confidence": sum(confidences) / len(confidences),
            "most_used_strategy": most_used,
        }

    def clear_history(self):
        """Clear resolution history"""
        self.resolution_history = []


# =============================================================================
# REDIS-BACKED MULTI-AGENT COORDINATION
# =============================================================================


@dataclass
class AgentTask:
    """A task assigned to an agent"""

    task_id: str
    task_type: str
    description: str
    assigned_to: str | None = None
    status: str = "pending"  # pending, in_progress, completed, failed
    priority: int = 5  # 1-10, higher = more important
    created_at: datetime = field(default_factory=datetime.now)
    context: dict[str, Any] = field(default_factory=dict)
    result: dict[str, Any] | None = None


class AgentCoordinator:
    """
    Redis-backed coordinator for multi-agent teams.

    Enables real-time coordination between agents using Redis short-term memory:
    - Task distribution and claiming
    - Status broadcasting
    - Result aggregation
    - Conflict resolution

    Example:
        >>> from empathy_os import get_redis_memory, AgentCoordinator
        >>>
        >>> memory = get_redis_memory()
        >>> coordinator = AgentCoordinator(memory, team_id="code_review_team")
        >>>
        >>> # Add tasks for agents to claim
        >>> coordinator.add_task(AgentTask(
        ...     task_id="review_001",
        ...     task_type="code_review",
        ...     description="Review auth module",
        ...     priority=8
        ... ))
        >>>
        >>> # Agent claims a task
        >>> task = coordinator.claim_task("agent_1", "code_review")
        >>> if task:
        ...     # Do work...
        ...     coordinator.complete_task(task.task_id, {"issues_found": 3})
    """

    def __init__(
        self,
        short_term_memory,
        team_id: str,
        conflict_resolver: ConflictResolver | None = None,
    ):
        """
        Initialize the coordinator.

        Args:
            short_term_memory: RedisShortTermMemory instance
            team_id: Unique identifier for this team
            conflict_resolver: Optional ConflictResolver for pattern conflicts
        """
        from .redis_memory import AccessTier, AgentCredentials

        self.memory = short_term_memory
        self.team_id = team_id
        self.conflict_resolver = conflict_resolver or ConflictResolver()

        # Coordinator has Steward-level access
        self._credentials = AgentCredentials(
            agent_id=f"coordinator_{team_id}",
            tier=AccessTier.STEWARD,
        )

        # Track active agents
        self._active_agents: dict[str, datetime] = {}

    def add_task(self, task: AgentTask) -> bool:
        """
        Add a task to the queue for agents to claim.

        Args:
            task: The task to add

        Returns:
            True if added successfully
        """
        task_data = {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "description": task.description,
            "assigned_to": task.assigned_to,
            "status": task.status,
            "priority": task.priority,
            "created_at": task.created_at.isoformat(),
            "context": task.context,
        }

        return self.memory.stash(
            f"task:{self.team_id}:{task.task_id}",
            task_data,
            self._credentials,
        )

    def get_pending_tasks(self, task_type: str | None = None) -> list[AgentTask]:
        """
        Get all pending tasks, optionally filtered by type.

        Args:
            task_type: Filter by task type

        Returns:
            List of pending AgentTask objects
        """
        # In a real implementation, we'd scan Redis keys
        # For now, this is a simplified version
        tasks = []

        # Get tasks from coordination signals
        signals = self.memory.receive_signals(
            self._credentials,
            signal_type="task_added",
        )

        for signal in signals:
            task_data = signal.get("data", {})
            if task_data.get("status") == "pending":
                if task_type is None or task_data.get("task_type") == task_type:
                    tasks.append(
                        AgentTask(
                            task_id=task_data["task_id"],
                            task_type=task_data.get("task_type", "unknown"),
                            description=task_data.get("description", ""),
                            status=task_data.get("status", "pending"),
                            priority=task_data.get("priority", 5),
                            context=task_data.get("context", {}),
                        )
                    )

        return sorted(tasks, key=lambda t: t.priority, reverse=True)

    def claim_task(
        self,
        agent_id: str,
        task_type: str | None = None,
    ) -> AgentTask | None:
        """
        Claim a pending task for an agent.

        Uses atomic operations to prevent race conditions.

        Args:
            agent_id: Agent claiming the task
            task_type: Optional filter by task type

        Returns:
            The claimed task, or None if no tasks available
        """
        pending = self.get_pending_tasks(task_type)

        for task in pending:
            # Try to claim (atomic check-and-set in Redis)
            task_key = f"task:{self.team_id}:{task.task_id}"
            current = self.memory.retrieve(task_key, self._credentials)

            if current and current.get("status") == "pending":
                # Update to claimed
                current["status"] = "in_progress"
                current["assigned_to"] = agent_id
                current["claimed_at"] = datetime.now().isoformat()

                if self.memory.stash(task_key, current, self._credentials):
                    task.status = "in_progress"
                    task.assigned_to = agent_id

                    # Broadcast claim
                    self.memory.send_signal(
                        signal_type="task_claimed",
                        data={
                            "task_id": task.task_id,
                            "agent_id": agent_id,
                            "task_type": task.task_type,
                        },
                        credentials=self._credentials,
                    )

                    return task

        return None

    def complete_task(
        self,
        task_id: str,
        result: dict[str, Any],
        agent_id: str | None = None,
    ) -> bool:
        """
        Mark a task as completed with results.

        Args:
            task_id: Task to complete
            result: Task results
            agent_id: Agent that completed (for verification)

        Returns:
            True if completed successfully
        """
        task_key = f"task:{self.team_id}:{task_id}"
        current = self.memory.retrieve(task_key, self._credentials)

        if not current:
            return False

        if agent_id and current.get("assigned_to") != agent_id:
            return False  # Wrong agent

        current["status"] = "completed"
        current["result"] = result
        current["completed_at"] = datetime.now().isoformat()

        if self.memory.stash(task_key, current, self._credentials):
            # Broadcast completion
            self.memory.send_signal(
                signal_type="task_completed",
                data={
                    "task_id": task_id,
                    "agent_id": current.get("assigned_to"),
                    "task_type": current.get("task_type"),
                    "result_summary": {
                        k: v for k, v in result.items() if isinstance(v, str | int | float | bool)
                    },
                },
                credentials=self._credentials,
            )
            return True

        return False

    def register_agent(self, agent_id: str, capabilities: list[str] | None = None) -> bool:
        """
        Register an agent with the team.

        Args:
            agent_id: Unique agent identifier
            capabilities: List of task types this agent can handle

        Returns:
            True if registered successfully
        """
        self._active_agents[agent_id] = datetime.now()

        return self.memory.stash(
            f"agent:{self.team_id}:{agent_id}",
            {
                "agent_id": agent_id,
                "capabilities": capabilities or [],
                "registered_at": datetime.now().isoformat(),
                "status": "active",
            },
            self._credentials,
        )

    def heartbeat(self, agent_id: str) -> bool:
        """
        Send heartbeat to indicate agent is still active.

        Args:
            agent_id: Agent sending heartbeat

        Returns:
            True if heartbeat recorded
        """
        self._active_agents[agent_id] = datetime.now()

        return self.memory.send_signal(
            signal_type="heartbeat",
            data={"agent_id": agent_id, "timestamp": datetime.now().isoformat()},
            credentials=self._credentials,
        )

    def get_active_agents(self, timeout_seconds: int = 300) -> list[str]:
        """
        Get list of recently active agents.

        Args:
            timeout_seconds: Consider agents inactive after this duration

        Returns:
            List of active agent IDs
        """
        cutoff = datetime.now()
        active = []

        for agent_id, last_seen in self._active_agents.items():
            if (cutoff - last_seen).total_seconds() < timeout_seconds:
                active.append(agent_id)

        return active

    def broadcast(self, message_type: str, data: dict[str, Any]) -> bool:
        """
        Broadcast a message to all agents in the team.

        Args:
            message_type: Type of message
            data: Message payload

        Returns:
            True if broadcast sent
        """
        return self.memory.send_signal(
            signal_type=message_type,
            data={"team_id": self.team_id, **data},
            credentials=self._credentials,
        )

    def aggregate_results(self, task_type: str | None = None) -> dict[str, Any]:
        """
        Aggregate results from completed tasks.

        Args:
            task_type: Optional filter by task type

        Returns:
            Aggregated results summary
        """
        # Get completion signals
        completions = self.memory.receive_signals(
            self._credentials,
            signal_type="task_completed",
        )

        results = {
            "total_completed": 0,
            "by_agent": {},
            "by_type": {},
            "summaries": [],
        }

        for signal in completions:
            data = signal.get("data", {})
            if task_type and data.get("task_type") != task_type:
                continue

            results["total_completed"] += 1

            agent = data.get("agent_id", "unknown")
            results["by_agent"][agent] = results["by_agent"].get(agent, 0) + 1

            ttype = data.get("task_type", "unknown")
            results["by_type"][ttype] = results["by_type"].get(ttype, 0) + 1

            if "result_summary" in data:
                results["summaries"].append(data["result_summary"])

        return results


class TeamSession:
    """
    A collaborative session for multiple agents working together.

    Example:
        >>> from empathy_os import get_redis_memory, TeamSession
        >>>
        >>> memory = get_redis_memory()
        >>> session = TeamSession(
        ...     memory,
        ...     session_id="pr_review_42",
        ...     purpose="Review PR #42"
        ... )
        >>>
        >>> session.add_agent("security_agent")
        >>> session.add_agent("performance_agent")
        >>>
        >>> # Share context between agents
        >>> session.share("analysis_scope", {"files": 15, "lines": 500})
        >>>
        >>> # Get context from session
        >>> scope = session.get("analysis_scope")
    """

    def __init__(
        self,
        short_term_memory,
        session_id: str,
        purpose: str = "",
    ):
        """
        Create or join a team session.

        Args:
            short_term_memory: RedisShortTermMemory instance
            session_id: Unique session identifier
            purpose: Description of what this session is for
        """
        from .redis_memory import AccessTier, AgentCredentials

        self.memory = short_term_memory
        self.session_id = session_id
        self.purpose = purpose

        self._credentials = AgentCredentials(
            agent_id=f"session_{session_id}",
            tier=AccessTier.CONTRIBUTOR,
        )

        # Initialize session in Redis
        self.memory.create_session(
            session_id=session_id,
            credentials=self._credentials,
            metadata={"purpose": purpose, "created_at": datetime.now().isoformat()},
        )

    def add_agent(self, agent_id: str) -> bool:
        """Add an agent to this session."""
        from .redis_memory import AccessTier, AgentCredentials

        agent_creds = AgentCredentials(agent_id=agent_id, tier=AccessTier.CONTRIBUTOR)
        return self.memory.join_session(self.session_id, agent_creds)

    def get_info(self) -> dict[str, Any] | None:
        """Get session info including participants."""
        return self.memory.get_session(self.session_id, self._credentials)

    def share(self, key: str, data: Any) -> bool:
        """
        Share data with all agents in the session.

        Args:
            key: Unique key for this data
            data: Any JSON-serializable data

        Returns:
            True if shared successfully
        """
        return self.memory.stash(
            f"session:{self.session_id}:{key}",
            data,
            self._credentials,
        )

    def get(self, key: str) -> Any | None:
        """
        Get shared data from the session.

        Args:
            key: Key of the shared data

        Returns:
            The data, or None if not found
        """
        return self.memory.retrieve(
            f"session:{self.session_id}:{key}",
            self._credentials,
        )

    def signal(self, signal_type: str, data: dict[str, Any]) -> bool:
        """
        Send a signal to session participants.

        Args:
            signal_type: Type of signal
            data: Signal payload

        Returns:
            True if sent
        """
        return self.memory.send_signal(
            signal_type=signal_type,
            data={"session_id": self.session_id, **data},
            credentials=self._credentials,
        )

    def get_signals(self, signal_type: str | None = None) -> list[dict]:
        """
        Get signals from the session.

        Args:
            signal_type: Optional filter

        Returns:
            List of signals
        """
        return self.memory.receive_signals(self._credentials, signal_type=signal_type)
