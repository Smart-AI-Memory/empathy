"""
Agent Monitoring for Distributed Memory Networks

Provides monitoring and metrics collection for multi-agent systems.
Tracks individual agent performance, pattern contributions, and
team-wide collaboration metrics.

Key metrics tracked:
- Agent interaction counts and response times
- Pattern discovery and reuse rates
- Cross-agent collaboration efficiency
- System health and performance

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .pattern_library import PatternLibrary


@dataclass
class AgentMetrics:
    """Metrics for a single agent"""

    agent_id: str
    total_interactions: int = 0
    total_response_time_ms: float = 0.0
    patterns_discovered: int = 0
    patterns_used: int = 0
    successful_pattern_uses: int = 0
    failed_pattern_uses: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)

    @property
    def avg_response_time_ms(self) -> float:
        """Average response time in milliseconds"""
        if self.total_interactions == 0:
            return 0.0
        return self.total_response_time_ms / self.total_interactions

    @property
    def success_rate(self) -> float:
        """Pattern usage success rate"""
        total = self.successful_pattern_uses + self.failed_pattern_uses
        if total == 0:
            return 0.0
        return self.successful_pattern_uses / total

    @property
    def pattern_contribution_rate(self) -> float:
        """Rate of pattern discovery per interaction"""
        if self.total_interactions == 0:
            return 0.0
        return self.patterns_discovered / self.total_interactions


@dataclass
class TeamMetrics:
    """Aggregated metrics for an agent team"""

    active_agents: int = 0
    total_agents: int = 0
    shared_patterns: int = 0
    total_interactions: int = 0
    pattern_reuse_count: int = 0
    cross_agent_reuses: int = 0

    @property
    def pattern_reuse_rate(self) -> float:
        """Rate at which patterns are reused"""
        if self.shared_patterns == 0:
            return 0.0
        return self.pattern_reuse_count / self.shared_patterns

    @property
    def collaboration_efficiency(self) -> float:
        """
        Measure of how effectively agents collaborate.

        Higher values indicate more cross-agent pattern reuse,
        meaning agents are learning from each other.
        """
        if self.pattern_reuse_count == 0:
            return 0.0
        return self.cross_agent_reuses / self.pattern_reuse_count


class AgentMonitor:
    """
    Monitors and tracks metrics for multi-agent systems.

    Provides insights into:
    - Individual agent performance
    - Pattern discovery and sharing
    - Team collaboration effectiveness
    - System health

    Example:
        >>> monitor = AgentMonitor()
        >>>
        >>> # Record agent activity
        >>> monitor.record_interaction("code_reviewer", response_time_ms=150.0)
        >>> monitor.record_pattern_discovery("code_reviewer")
        >>> monitor.record_pattern_use("test_gen", pattern_agent="code_reviewer", success=True)
        >>>
        >>> # Get individual stats
        >>> stats = monitor.get_agent_stats("code_reviewer")
        >>> print(f"Interactions: {stats['total_interactions']}")
        >>> print(f"Patterns discovered: {stats['patterns_discovered']}")
        >>>
        >>> # Get team stats
        >>> team = monitor.get_team_stats()
        >>> print(f"Collaboration efficiency: {team['collaboration_efficiency']:.0%}")
    """

    def __init__(self, pattern_library: PatternLibrary | None = None):
        """
        Initialize the AgentMonitor.

        Args:
            pattern_library: Optional pattern library to track for shared patterns
        """
        self.agents: dict[str, AgentMetrics] = {}
        self.pattern_library = pattern_library

        # Track pattern reuse events
        self.pattern_uses: list[dict[str, Any]] = []

        # Track alerts
        self.alerts: list[dict[str, Any]] = []

    def record_interaction(
        self,
        agent_id: str,
        response_time_ms: float = 0.0,
    ):
        """
        Record an agent interaction.

        Args:
            agent_id: ID of the agent
            response_time_ms: Response time in milliseconds
        """
        agent = self._get_or_create_agent(agent_id)
        agent.total_interactions += 1
        agent.total_response_time_ms += response_time_ms
        agent.last_active = datetime.now()

        # Check for performance alerts
        if response_time_ms > 5000:  # Over 5 seconds
            self._add_alert(
                agent_id=agent_id,
                alert_type="slow_response",
                message=f"Agent {agent_id} response time: {response_time_ms:.0f}ms",
            )

    def record_pattern_discovery(self, agent_id: str, pattern_id: str | None = None):
        """
        Record that an agent discovered a new pattern.

        Args:
            agent_id: ID of the agent that discovered the pattern
            pattern_id: Optional pattern ID for tracking
        """
        agent = self._get_or_create_agent(agent_id)
        agent.patterns_discovered += 1
        agent.last_active = datetime.now()

    def record_pattern_use(
        self,
        agent_id: str,
        pattern_id: str | None = None,
        pattern_agent: str | None = None,
        success: bool = True,
    ):
        """
        Record that an agent used a pattern.

        Args:
            agent_id: ID of the agent using the pattern
            pattern_id: ID of the pattern being used
            pattern_agent: ID of the agent that contributed the pattern
            success: Whether the pattern use was successful
        """
        agent = self._get_or_create_agent(agent_id)
        agent.patterns_used += 1

        if success:
            agent.successful_pattern_uses += 1
        else:
            agent.failed_pattern_uses += 1

        agent.last_active = datetime.now()

        # Track cross-agent pattern reuse
        is_cross_agent = pattern_agent is not None and pattern_agent != agent_id
        self.pattern_uses.append(
            {
                "user_agent": agent_id,
                "pattern_agent": pattern_agent,
                "pattern_id": pattern_id,
                "cross_agent": is_cross_agent,
                "success": success,
                "timestamp": datetime.now(),
            }
        )

    def get_agent_stats(self, agent_id: str) -> dict[str, Any]:
        """
        Get statistics for a specific agent.

        Args:
            agent_id: ID of the agent

        Returns:
            Dictionary with agent statistics
        """
        agent = self.agents.get(agent_id)

        if agent is None:
            return {
                "agent_id": agent_id,
                "total_interactions": 0,
                "avg_response_time_ms": 0.0,
                "patterns_discovered": 0,
                "patterns_used": 0,
                "success_rate": 0.0,
                "status": "unknown",
            }

        # Determine agent status
        inactive_threshold = 3600  # 1 hour
        seconds_inactive = (datetime.now() - agent.last_active).total_seconds()
        status = "active" if seconds_inactive < inactive_threshold else "inactive"

        return {
            "agent_id": agent_id,
            "total_interactions": agent.total_interactions,
            "avg_response_time_ms": agent.avg_response_time_ms,
            "patterns_discovered": agent.patterns_discovered,
            "patterns_used": agent.patterns_used,
            "success_rate": agent.success_rate,
            "pattern_contribution_rate": agent.pattern_contribution_rate,
            "first_seen": agent.first_seen.isoformat(),
            "last_active": agent.last_active.isoformat(),
            "status": status,
        }

    def get_team_stats(self) -> dict[str, Any]:
        """
        Get aggregated statistics for the entire agent team.

        Returns:
            Dictionary with team-wide statistics
        """
        if not self.agents:
            # Get shared patterns count from library even if no agents
            shared_patterns = 0
            if self.pattern_library:
                shared_patterns = len(self.pattern_library.patterns)

            return {
                "active_agents": 0,
                "total_agents": 0,
                "shared_patterns": shared_patterns,
                "total_interactions": 0,
                "total_patterns_discovered": 0,
                "pattern_reuse_count": 0,
                "cross_agent_reuses": 0,
                "pattern_reuse_rate": 0.0,
                "collaboration_efficiency": 0.0,
            }

        # Count active agents (active in last hour)
        inactive_threshold = 3600
        now = datetime.now()
        active_count = sum(
            1
            for agent in self.agents.values()
            if (now - agent.last_active).total_seconds() < inactive_threshold
        )

        # Calculate totals
        total_interactions = sum(a.total_interactions for a in self.agents.values())
        total_patterns_discovered = sum(a.patterns_discovered for a in self.agents.values())

        # Calculate pattern reuse metrics
        pattern_reuse_count = len(self.pattern_uses)
        cross_agent_reuses = sum(1 for use in self.pattern_uses if use["cross_agent"])

        # Get shared patterns count from library if available
        shared_patterns = 0
        if self.pattern_library:
            shared_patterns = len(self.pattern_library.patterns)
        else:
            shared_patterns = total_patterns_discovered

        # Calculate rates
        reuse_rate = pattern_reuse_count / shared_patterns if shared_patterns > 0 else 0.0
        collab_efficiency = (
            cross_agent_reuses / pattern_reuse_count if pattern_reuse_count > 0 else 0.0
        )

        return {
            "active_agents": active_count,
            "total_agents": len(self.agents),
            "shared_patterns": shared_patterns,
            "total_interactions": total_interactions,
            "total_patterns_discovered": total_patterns_discovered,
            "pattern_reuse_count": pattern_reuse_count,
            "cross_agent_reuses": cross_agent_reuses,
            "pattern_reuse_rate": reuse_rate,
            "collaboration_efficiency": collab_efficiency,
        }

    def get_top_contributors(self, n: int = 5) -> list[dict[str, Any]]:
        """
        Get the top pattern-contributing agents.

        Args:
            n: Number of agents to return

        Returns:
            List of agent stats, sorted by patterns discovered
        """
        sorted_agents = sorted(
            self.agents.values(), key=lambda a: a.patterns_discovered, reverse=True
        )

        return [self.get_agent_stats(agent.agent_id) for agent in sorted_agents[:n]]

    def get_alerts(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent alerts.

        Args:
            limit: Maximum number of alerts to return

        Returns:
            List of alert dictionaries
        """
        return self.alerts[-limit:]

    def check_health(self) -> dict[str, Any]:
        """
        Check overall system health.

        Returns:
            Health status dictionary
        """
        team_stats = self.get_team_stats()
        recent_alerts = [
            a for a in self.alerts if (datetime.now() - a["timestamp"]).total_seconds() < 3600
        ]

        # Determine health status
        issues = []
        if team_stats["active_agents"] == 0:
            issues.append("No active agents")
        if team_stats["collaboration_efficiency"] < 0.1 and team_stats["pattern_reuse_count"] > 10:
            issues.append("Low collaboration efficiency")
        if len(recent_alerts) > 10:
            issues.append("High alert volume")

        status = "healthy"
        if issues:
            status = "degraded" if len(issues) == 1 else "unhealthy"

        return {
            "status": status,
            "issues": issues,
            "active_agents": team_stats["active_agents"],
            "recent_alerts": len(recent_alerts),
            "timestamp": datetime.now().isoformat(),
        }

    def _get_or_create_agent(self, agent_id: str) -> AgentMetrics:
        """Get existing agent metrics or create new"""
        if agent_id not in self.agents:
            self.agents[agent_id] = AgentMetrics(agent_id=agent_id)
        return self.agents[agent_id]

    def _add_alert(
        self,
        agent_id: str,
        alert_type: str,
        message: str,
        severity: str = "warning",
    ):
        """Add an alert to the monitoring system"""
        self.alerts.append(
            {
                "agent_id": agent_id,
                "alert_type": alert_type,
                "message": message,
                "severity": severity,
                "timestamp": datetime.now(),
            }
        )

        # Keep alerts bounded
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-500:]

    def reset(self):
        """Reset all monitoring data"""
        self.agents = {}
        self.pattern_uses = []
        self.alerts = []
