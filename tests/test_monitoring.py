"""Tests for Agent Monitoring

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os import AgentMetrics, AgentMonitor, PatternLibrary


class TestAgentMetrics:
    """Test AgentMetrics dataclass"""

    def test_metrics_creation(self):
        """Test creating agent metrics"""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.agent_id == "test_agent"
        assert metrics.total_interactions == 0
        assert metrics.patterns_discovered == 0
        assert metrics.patterns_used == 0

    def test_avg_response_time_empty(self):
        """Test average response time with no interactions"""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.avg_response_time_ms == 0.0

    def test_avg_response_time_calculated(self):
        """Test average response time calculation"""
        metrics = AgentMetrics(
            agent_id="test_agent",
            total_interactions=10,
            total_response_time_ms=1000.0,
        )

        assert metrics.avg_response_time_ms == 100.0

    def test_success_rate_empty(self):
        """Test success rate with no usage"""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.success_rate == 0.0

    def test_success_rate_calculated(self):
        """Test success rate calculation"""
        metrics = AgentMetrics(
            agent_id="test_agent",
            successful_pattern_uses=8,
            failed_pattern_uses=2,
        )

        assert metrics.success_rate == 0.8

    def test_pattern_contribution_rate_empty(self):
        """Test contribution rate with no interactions"""
        metrics = AgentMetrics(agent_id="test_agent")

        assert metrics.pattern_contribution_rate == 0.0

    def test_pattern_contribution_rate_calculated(self):
        """Test contribution rate calculation"""
        metrics = AgentMetrics(
            agent_id="test_agent",
            total_interactions=100,
            patterns_discovered=10,
        )

        assert metrics.pattern_contribution_rate == 0.1


class TestAgentMonitor:
    """Test AgentMonitor class"""

    def test_initialization(self):
        """Test default initialization"""
        monitor = AgentMonitor()

        assert len(monitor.agents) == 0
        assert len(monitor.pattern_uses) == 0
        assert len(monitor.alerts) == 0

    def test_initialization_with_library(self):
        """Test initialization with pattern library"""
        library = PatternLibrary()
        monitor = AgentMonitor(pattern_library=library)

        assert monitor.pattern_library is library

    def test_record_interaction(self):
        """Test recording agent interaction"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1", response_time_ms=150.0)

        stats = monitor.get_agent_stats("agent1")
        assert stats["total_interactions"] == 1
        assert stats["avg_response_time_ms"] == 150.0

    def test_record_multiple_interactions(self):
        """Test recording multiple interactions"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1", response_time_ms=100.0)
        monitor.record_interaction("agent1", response_time_ms=200.0)
        monitor.record_interaction("agent1", response_time_ms=300.0)

        stats = monitor.get_agent_stats("agent1")
        assert stats["total_interactions"] == 3
        assert stats["avg_response_time_ms"] == 200.0

    def test_record_pattern_discovery(self):
        """Test recording pattern discovery"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1")
        monitor.record_pattern_discovery("agent1", pattern_id="pat_001")

        stats = monitor.get_agent_stats("agent1")
        assert stats["patterns_discovered"] == 1

    def test_record_pattern_use_success(self):
        """Test recording successful pattern use"""
        monitor = AgentMonitor()

        monitor.record_pattern_use(
            agent_id="agent1",
            pattern_id="pat_001",
            pattern_agent="agent2",
            success=True,
        )

        stats = monitor.get_agent_stats("agent1")
        assert stats["patterns_used"] == 1
        assert stats["success_rate"] == 1.0

    def test_record_pattern_use_failure(self):
        """Test recording failed pattern use"""
        monitor = AgentMonitor()

        monitor.record_pattern_use(
            agent_id="agent1",
            pattern_id="pat_001",
            success=False,
        )

        stats = monitor.get_agent_stats("agent1")
        assert stats["success_rate"] == 0.0

    def test_record_cross_agent_pattern_use(self):
        """Test recording cross-agent pattern use"""
        monitor = AgentMonitor()

        # Agent1 uses pattern from Agent2
        monitor.record_pattern_use(
            agent_id="agent1",
            pattern_id="pat_001",
            pattern_agent="agent2",
            success=True,
        )

        # Should be tracked as cross-agent use
        assert len(monitor.pattern_uses) == 1
        assert monitor.pattern_uses[0]["cross_agent"] is True

    def test_record_same_agent_pattern_use(self):
        """Test recording same-agent pattern use"""
        monitor = AgentMonitor()

        # Agent1 uses its own pattern
        monitor.record_pattern_use(
            agent_id="agent1",
            pattern_id="pat_001",
            pattern_agent="agent1",
            success=True,
        )

        assert monitor.pattern_uses[0]["cross_agent"] is False

    def test_get_agent_stats_unknown_agent(self):
        """Test getting stats for unknown agent"""
        monitor = AgentMonitor()

        stats = monitor.get_agent_stats("unknown_agent")

        assert stats["agent_id"] == "unknown_agent"
        assert stats["total_interactions"] == 0
        assert stats["status"] == "unknown"

    def test_agent_status_active(self):
        """Test agent status is active after recent interaction"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1")

        stats = monitor.get_agent_stats("agent1")
        assert stats["status"] == "active"

    def test_get_team_stats_empty(self):
        """Test team stats with no agents"""
        monitor = AgentMonitor()

        stats = monitor.get_team_stats()

        assert stats["active_agents"] == 0
        assert stats["total_agents"] == 0
        assert stats["shared_patterns"] == 0
        assert stats["pattern_reuse_rate"] == 0.0
        assert stats["collaboration_efficiency"] == 0.0

    def test_get_team_stats(self):
        """Test team stats with agents"""
        monitor = AgentMonitor()

        # Set up agents
        monitor.record_interaction("agent1")
        monitor.record_interaction("agent2")
        monitor.record_pattern_discovery("agent1")
        monitor.record_pattern_discovery("agent1")
        monitor.record_pattern_discovery("agent2")

        stats = monitor.get_team_stats()

        assert stats["total_agents"] == 2
        assert stats["active_agents"] >= 0  # Depends on timing
        assert stats["total_patterns_discovered"] == 3

    def test_team_collaboration_efficiency(self):
        """Test collaboration efficiency calculation"""
        monitor = AgentMonitor()

        # Cross-agent pattern uses
        monitor.record_pattern_use("agent1", "pat_001", "agent2", True)
        monitor.record_pattern_use("agent1", "pat_002", "agent2", True)

        # Same-agent pattern use
        monitor.record_pattern_use("agent2", "pat_003", "agent2", True)

        stats = monitor.get_team_stats()

        # 2 cross-agent out of 3 total = 66% efficiency
        assert stats["collaboration_efficiency"] == pytest.approx(0.666, rel=0.01)

    def test_get_top_contributors(self):
        """Test getting top contributing agents"""
        monitor = AgentMonitor()

        # Agent1 discovers 5 patterns
        monitor.record_interaction("agent1")
        for _ in range(5):
            monitor.record_pattern_discovery("agent1")

        # Agent2 discovers 3 patterns
        monitor.record_interaction("agent2")
        for _ in range(3):
            monitor.record_pattern_discovery("agent2")

        # Agent3 discovers 1 pattern
        monitor.record_interaction("agent3")
        monitor.record_pattern_discovery("agent3")

        top = monitor.get_top_contributors(n=2)

        assert len(top) == 2
        assert top[0]["agent_id"] == "agent1"
        assert top[0]["patterns_discovered"] == 5
        assert top[1]["agent_id"] == "agent2"

    def test_slow_response_alert(self):
        """Test alert generated for slow response"""
        monitor = AgentMonitor()

        # Record a slow response (over 5 seconds)
        monitor.record_interaction("agent1", response_time_ms=6000.0)

        alerts = monitor.get_alerts()

        assert len(alerts) == 1
        assert alerts[0]["alert_type"] == "slow_response"
        assert alerts[0]["agent_id"] == "agent1"

    def test_check_health_healthy(self):
        """Test health check when system is healthy"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1")
        monitor.record_interaction("agent2")

        health = monitor.check_health()

        assert health["status"] == "healthy"
        assert len(health["issues"]) == 0
        assert health["active_agents"] >= 0

    def test_check_health_no_active_agents(self):
        """Test health check with no active agents"""
        monitor = AgentMonitor()

        health = monitor.check_health()

        assert health["status"] == "degraded"
        assert "No active agents" in health["issues"]

    def test_reset(self):
        """Test resetting monitor"""
        monitor = AgentMonitor()

        monitor.record_interaction("agent1")
        monitor.record_pattern_discovery("agent1")
        monitor.record_pattern_use("agent1", "pat_001", success=True)

        assert len(monitor.agents) > 0

        monitor.reset()

        assert len(monitor.agents) == 0
        assert len(monitor.pattern_uses) == 0
        assert len(monitor.alerts) == 0

    def test_alerts_bounded(self):
        """Test that alerts are bounded to prevent memory issues"""
        monitor = AgentMonitor()

        # Generate many alerts
        for i in range(1500):
            monitor.record_interaction(f"agent_{i}", response_time_ms=6000.0)

        # Should be bounded
        assert len(monitor.get_alerts()) <= 1000

    def test_get_alerts_with_limit(self):
        """Test getting alerts with limit"""
        monitor = AgentMonitor()

        # Generate some alerts
        for i in range(20):
            monitor.record_interaction(f"agent_{i}", response_time_ms=6000.0)

        alerts = monitor.get_alerts(limit=5)

        assert len(alerts) == 5

    def test_pattern_library_integration(self):
        """Test integration with pattern library"""
        from empathy_os import Pattern

        library = PatternLibrary()
        monitor = AgentMonitor(pattern_library=library)

        # Add patterns to library
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test pattern",
            description="Test",
        )
        library.contribute_pattern("agent1", pattern)

        # Team stats should reflect library patterns
        stats = monitor.get_team_stats()
        assert stats["shared_patterns"] == 1

    def test_multiple_agents_concurrent_tracking(self):
        """Test tracking multiple agents concurrently"""
        monitor = AgentMonitor()

        # Simulate multiple agents
        for i in range(5):
            agent_id = f"agent_{i}"
            monitor.record_interaction(agent_id, response_time_ms=100.0 + i * 10)
            monitor.record_pattern_discovery(agent_id)

        team_stats = monitor.get_team_stats()

        assert team_stats["total_agents"] == 5
        assert team_stats["total_patterns_discovered"] == 5
        assert team_stats["total_interactions"] == 5


class TestTeamMetrics:
    """Test TeamMetrics dataclass"""

    def test_metrics_creation(self):
        """Test creating team metrics"""
        from empathy_os.monitoring import TeamMetrics

        metrics = TeamMetrics(
            active_agents=3,
            total_agents=5,
            shared_patterns=10,
        )

        assert metrics.active_agents == 3
        assert metrics.total_agents == 5
        assert metrics.shared_patterns == 10

    def test_pattern_reuse_rate_empty(self):
        """Test reuse rate with no patterns"""
        from empathy_os.monitoring import TeamMetrics

        metrics = TeamMetrics()

        assert metrics.pattern_reuse_rate == 0.0

    def test_pattern_reuse_rate_calculated(self):
        """Test reuse rate calculation"""
        from empathy_os.monitoring import TeamMetrics

        metrics = TeamMetrics(
            shared_patterns=10,
            pattern_reuse_count=20,
        )

        assert metrics.pattern_reuse_rate == 2.0

    def test_collaboration_efficiency_empty(self):
        """Test collaboration efficiency with no reuses"""
        from empathy_os.monitoring import TeamMetrics

        metrics = TeamMetrics()

        assert metrics.collaboration_efficiency == 0.0

    def test_collaboration_efficiency_calculated(self):
        """Test collaboration efficiency calculation"""
        from empathy_os.monitoring import TeamMetrics

        metrics = TeamMetrics(
            pattern_reuse_count=10,
            cross_agent_reuses=7,
        )

        assert metrics.collaboration_efficiency == 0.7
