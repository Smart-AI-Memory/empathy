"""Tests for Multi-Agent Coordination (ConflictResolver)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from datetime import datetime, timedelta

import pytest

from empathy_os import ConflictResolver, Pattern, ResolutionStrategy, TeamPriorities


class TestConflictResolver:
    """Test ConflictResolver class"""

    def test_initialization_default(self):
        """Test default initialization"""
        resolver = ConflictResolver()

        assert resolver.default_strategy == ResolutionStrategy.WEIGHTED_SCORE
        assert resolver.team_priorities is not None
        assert len(resolver.resolution_history) == 0

    def test_initialization_custom_strategy(self):
        """Test initialization with custom strategy"""
        resolver = ConflictResolver(default_strategy=ResolutionStrategy.HIGHEST_CONFIDENCE)

        assert resolver.default_strategy == ResolutionStrategy.HIGHEST_CONFIDENCE

    def test_initialization_custom_priorities(self):
        """Test initialization with custom team priorities"""
        priorities = TeamPriorities(
            readability_weight=0.5,
            performance_weight=0.1,
            security_weight=0.3,
            maintainability_weight=0.1,
        )
        resolver = ConflictResolver(team_priorities=priorities)

        assert resolver.team_priorities.readability_weight == 0.5

    def test_resolve_requires_two_patterns(self):
        """Test that resolve requires at least 2 patterns"""
        resolver = ConflictResolver()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="Single pattern",
            description="Only one",
            confidence=0.8,
        )

        with pytest.raises(ValueError, match="at least 2 patterns"):
            resolver.resolve_patterns([pattern])

    def test_resolve_highest_confidence(self):
        """Test resolution by highest confidence"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="High confidence",
            description="Test",
            confidence=0.95,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Low confidence",
            description="Test",
            confidence=0.60,
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
        )

        assert result.winning_pattern.id == "pat_001"
        assert result.strategy_used == ResolutionStrategy.HIGHEST_CONFIDENCE
        assert len(result.losing_patterns) == 1
        assert result.losing_patterns[0].id == "pat_002"

    def test_resolve_most_recent(self):
        """Test resolution by most recent"""
        resolver = ConflictResolver()

        old_date = datetime.now() - timedelta(days=100)
        recent_date = datetime.now() - timedelta(days=1)

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="Old pattern",
            description="Test",
            confidence=0.95,
            discovered_at=old_date,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Recent pattern",
            description="Test",
            confidence=0.60,
            discovered_at=recent_date,
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            strategy=ResolutionStrategy.MOST_RECENT,
        )

        assert result.winning_pattern.id == "pat_002"
        assert result.strategy_used == ResolutionStrategy.MOST_RECENT

    def test_resolve_with_context(self):
        """Test resolution with context match"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="Python pattern",
            description="Test",
            confidence=0.80,
            context={"language": "python", "domain": "testing"},
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Java pattern",
            description="Test",
            confidence=0.80,
            context={"language": "java", "domain": "enterprise"},
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            context={"language": "python", "domain": "testing"},
            strategy=ResolutionStrategy.BEST_CONTEXT_MATCH,
        )

        assert result.winning_pattern.id == "pat_001"

    def test_resolve_team_priority(self):
        """Test resolution with team priorities"""
        resolver = ConflictResolver()

        # Security pattern
        pattern1 = Pattern(
            id="pat_001",
            agent_id="security_agent",
            pattern_type="security",
            name="Security pattern",
            description="Test",
            confidence=0.80,
        )

        # Style pattern
        pattern2 = Pattern(
            id="pat_002",
            agent_id="style_agent",
            pattern_type="style",
            name="Style pattern",
            description="Test",
            confidence=0.85,
        )

        # With team priority on security
        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            context={"team_priority": "security"},
            strategy=ResolutionStrategy.TEAM_PRIORITY,
        )

        # Security pattern should win due to team priority
        assert result.winning_pattern.pattern_type == "security"

    def test_resolve_weighted_score(self):
        """Test resolution with weighted scoring"""
        resolver = ConflictResolver()

        # Pattern with high confidence but old
        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="Old but confident",
            description="Test",
            confidence=0.95,
            discovered_at=datetime.now() - timedelta(days=300),
        )

        # Pattern with medium confidence but recent and used successfully
        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Recent with usage",
            description="Test",
            confidence=0.80,
            discovered_at=datetime.now() - timedelta(days=10),
        )

        # Add successful usage to pattern2
        for _ in range(10):
            pattern2.record_usage(success=True)

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            strategy=ResolutionStrategy.WEIGHTED_SCORE,
        )

        # Weighted score considers multiple factors
        assert result.strategy_used == ResolutionStrategy.WEIGHTED_SCORE
        assert result.factors is not None
        assert "confidence" in result.factors
        assert "recency" in result.factors

    def test_resolve_with_tags(self):
        """Test resolution considering tags"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="best_practice",
            name="Tagged pattern",
            description="Test",
            confidence=0.80,
            tags=["python", "testing", "best-practices"],
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Untagged pattern",
            description="Test",
            confidence=0.80,
            tags=[],
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            context={"tags": ["python", "testing"]},
        )

        # Tagged pattern should have higher context match
        assert result.winning_pattern.id == "pat_001"

    def test_resolution_result_has_reasoning(self):
        """Test that resolution result includes reasoning"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="Pattern A",
            description="Test",
            confidence=0.90,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Pattern B",
            description="Test",
            confidence=0.60,
        )

        result = resolver.resolve_patterns([pattern1, pattern2])

        assert result.reasoning is not None
        assert len(result.reasoning) > 0
        assert "Pattern A" in result.reasoning

    def test_resolution_history_tracked(self):
        """Test that resolution history is tracked"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="P1",
            description="Test",
            confidence=0.90,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="P2",
            description="Test",
            confidence=0.60,
        )

        assert len(resolver.resolution_history) == 0

        resolver.resolve_patterns([pattern1, pattern2])

        assert len(resolver.resolution_history) == 1

    def test_get_resolution_stats(self):
        """Test getting resolution statistics"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="P1",
            description="Test",
            confidence=0.90,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="P2",
            description="Test",
            confidence=0.60,
        )

        # Perform multiple resolutions
        resolver.resolve_patterns([pattern1, pattern2])
        resolver.resolve_patterns(
            [pattern1, pattern2],
            strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
        )

        stats = resolver.get_resolution_stats()

        assert stats["total_resolutions"] == 2
        assert "strategies_used" in stats
        assert stats["average_confidence"] > 0

    def test_get_resolution_stats_empty(self):
        """Test stats when no resolutions have been made"""
        resolver = ConflictResolver()

        stats = resolver.get_resolution_stats()

        assert stats["total_resolutions"] == 0
        assert stats["average_confidence"] == 0.0

    def test_clear_history(self):
        """Test clearing resolution history"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="P1",
            description="Test",
            confidence=0.90,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="P2",
            description="Test",
            confidence=0.60,
        )

        resolver.resolve_patterns([pattern1, pattern2])
        assert len(resolver.resolution_history) == 1

        resolver.clear_history()

        assert len(resolver.resolution_history) == 0

    def test_resolve_three_patterns(self):
        """Test resolving conflict between three patterns"""
        resolver = ConflictResolver()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="style",
            name="P1",
            description="Test",
            confidence=0.70,
        )

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="P2",
            description="Test",
            confidence=0.90,
        )

        pattern3 = Pattern(
            id="pat_003",
            agent_id="agent3",
            pattern_type="style",
            name="P3",
            description="Test",
            confidence=0.60,
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2, pattern3],
            strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
        )

        assert result.winning_pattern.id == "pat_002"
        assert len(result.losing_patterns) == 2

    def test_resolution_confidence_varies_by_factors(self):
        """Test that resolution confidence reflects the scores"""
        resolver = ConflictResolver()

        # Clear winner
        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="security",
            name="Clear winner",
            description="Test",
            confidence=0.95,
        )

        # Weak competitor
        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="style",
            name="Weak",
            description="Test",
            confidence=0.30,
        )

        result = resolver.resolve_patterns(
            [pattern1, pattern2],
            strategy=ResolutionStrategy.HIGHEST_CONFIDENCE,
        )

        # High confidence resolution since winner is much better
        assert result.confidence == pytest.approx(0.95, rel=0.01)


class TestTeamPriorities:
    """Test TeamPriorities dataclass"""

    def test_default_priorities(self):
        """Test default priority values"""
        priorities = TeamPriorities()

        assert priorities.readability_weight == 0.3
        assert priorities.performance_weight == 0.2
        assert priorities.security_weight == 0.3
        assert priorities.maintainability_weight == 0.2

    def test_custom_priorities(self):
        """Test custom priority values"""
        priorities = TeamPriorities(
            readability_weight=0.5,
            performance_weight=0.5,
            security_weight=0.0,
            maintainability_weight=0.0,
        )

        assert priorities.readability_weight == 0.5
        assert priorities.performance_weight == 0.5

    def test_type_preferences(self):
        """Test pattern type preferences"""
        priorities = TeamPriorities()

        # Security should have high preference by default
        assert priorities.type_preferences["security"] == 1.0
        assert priorities.type_preferences["style"] < priorities.type_preferences["security"]

    def test_preferred_tags(self):
        """Test preferred tags configuration"""
        priorities = TeamPriorities(preferred_tags=["python", "testing", "automation"])

        assert "python" in priorities.preferred_tags
        assert len(priorities.preferred_tags) == 3


class TestResolutionStrategy:
    """Test ResolutionStrategy enum"""

    def test_all_strategies_exist(self):
        """Test that all expected strategies exist"""
        strategies = [s.value for s in ResolutionStrategy]

        assert "highest_confidence" in strategies
        assert "most_recent" in strategies
        assert "best_context_match" in strategies
        assert "team_priority" in strategies
        assert "weighted_score" in strategies

    def test_strategy_values_are_strings(self):
        """Test that strategy values are strings"""
        for strategy in ResolutionStrategy:
            assert isinstance(strategy.value, str)
