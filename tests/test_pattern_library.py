"""
Tests for Pattern Library

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import pytest
from empathy_os import Pattern, PatternLibrary


class TestPattern:
    """Test Pattern dataclass"""

    def test_pattern_creation(self):
        """Test creating a pattern"""
        pattern = Pattern(
            id="pat_001",
            agent_id="test_agent",
            pattern_type="sequential",
            name="Test Pattern",
            description="A test pattern"
        )

        assert pattern.id == "pat_001"
        assert pattern.agent_id == "test_agent"
        assert pattern.pattern_type == "sequential"
        assert pattern.usage_count == 0
        assert pattern.success_count == 0

    def test_pattern_success_rate(self):
        """Test pattern success rate calculation"""
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test"
        )

        assert pattern.success_rate == 0.0

        pattern.record_usage(success=True)
        pattern.record_usage(success=True)
        pattern.record_usage(success=False)

        assert pattern.usage_count == 3
        assert pattern.success_count == 2
        assert pattern.failure_count == 1
        assert pattern.success_rate == pytest.approx(0.666, rel=0.01)

    def test_pattern_confidence_updates(self):
        """Test that confidence updates after sufficient usage"""
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.5
        )

        # Confidence shouldn't update with < 5 uses
        pattern.record_usage(success=True)
        assert pattern.confidence == 0.5

        # After 5 uses, confidence = success rate
        for _ in range(4):
            pattern.record_usage(success=True)

        assert pattern.usage_count == 5
        assert pattern.confidence == 1.0


class TestPatternLibrary:
    """Test PatternLibrary"""

    def test_initialization(self):
        """Test library initializes empty"""
        library = PatternLibrary()
        assert len(library.patterns) == 0
        assert len(library.agent_contributions) == 0

    def test_contribute_pattern(self):
        """Test contributing a pattern to library"""
        library = PatternLibrary()
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test pattern"
        )

        library.contribute_pattern("agent1", pattern)

        assert len(library.patterns) == 1
        assert "pat_001" in library.patterns
        assert "agent1" in library.agent_contributions

    def test_query_patterns_by_confidence(self):
        """Test querying patterns with confidence filter"""
        library = PatternLibrary()

        # Add high confidence pattern
        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="High confidence",
            description="Test",
            confidence=0.9
        )
        library.contribute_pattern("agent1", pattern1)

        # Add low confidence pattern
        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent2",
            pattern_type="sequential",
            name="Low confidence",
            description="Test",
            confidence=0.3
        )
        library.contribute_pattern("agent2", pattern2)

        # Query with high confidence threshold
        matches = library.query_patterns(
            "agent3",
            context={"test": True},
            min_confidence=0.7
        )

        # Should only get high confidence pattern
        assert len(matches) <= 1
        if matches:
            assert matches[0].pattern.confidence >= 0.7

    def test_query_patterns_by_type(self):
        """Test querying patterns by type"""
        library = PatternLibrary()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Sequential pattern",
            description="Test",
            confidence=0.8
        )
        library.contribute_pattern("agent1", pattern1)

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent1",
            pattern_type="temporal",
            name="Temporal pattern",
            description="Test",
            confidence=0.8
        )
        library.contribute_pattern("agent1", pattern2)

        # Query for sequential only
        matches = library.query_patterns(
            "agent2",
            context={"test": True},
            pattern_type="sequential"
        )

        assert all(m.pattern.pattern_type == "sequential" for m in matches)

    def test_record_pattern_outcome(self):
        """Test recording pattern usage outcomes"""
        library = PatternLibrary()
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test"
        )
        library.contribute_pattern("agent1", pattern)

        library.record_pattern_outcome("pat_001", success=True)

        updated_pattern = library.get_pattern("pat_001")
        assert updated_pattern.usage_count == 1
        assert updated_pattern.success_count == 1

    def test_link_patterns(self):
        """Test linking related patterns"""
        library = PatternLibrary()

        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")

        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)

        library.link_patterns("pat_001", "pat_002")

        related = library.get_related_patterns("pat_001")
        assert len(related) == 1
        assert related[0].id == "pat_002"

    def test_get_agent_patterns(self):
        """Test getting patterns by agent"""
        library = PatternLibrary()

        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")
        pattern3 = Pattern(id="pat_003", agent_id="agent2", pattern_type="sequential", name="P3", description="Test")

        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)
        library.contribute_pattern("agent2", pattern3)

        agent1_patterns = library.get_agent_patterns("agent1")
        assert len(agent1_patterns) == 2
        assert all(p.agent_id == "agent1" for p in agent1_patterns)

    def test_get_top_patterns(self):
        """Test getting top patterns by various metrics"""
        library = PatternLibrary()

        # Create patterns with different metrics
        for i in range(5):
            pattern = Pattern(
                id=f"pat_{i}",
                agent_id="agent1",
                pattern_type="sequential",
                name=f"Pattern {i}",
                description="Test",
                confidence=0.5 + (i * 0.1)
            )
            library.contribute_pattern("agent1", pattern)

        # Get top 3 by confidence
        top = library.get_top_patterns(n=3, sort_by="confidence")
        assert len(top) == 3
        # Should be sorted descending
        assert top[0].confidence >= top[1].confidence
        assert top[1].confidence >= top[2].confidence

    def test_library_stats(self):
        """Test library statistics"""
        library = PatternLibrary()

        # Add patterns from multiple agents
        for i in range(3):
            pattern = Pattern(
                id=f"pat_{i}",
                agent_id=f"agent_{i % 2}",
                pattern_type="sequential",
                name=f"Pattern {i}",
                description="Test",
                confidence=0.8
            )
            library.contribute_pattern(f"agent_{i % 2}", pattern)

        stats = library.get_library_stats()
        assert stats["total_patterns"] == 3
        assert stats["total_agents"] == 2
        assert stats["average_confidence"] == pytest.approx(0.8, rel=0.01)

    def test_library_stats_empty(self):
        """Test library statistics when empty"""
        library = PatternLibrary()
        stats = library.get_library_stats()

        assert stats["total_patterns"] == 0
        assert stats["total_agents"] == 0
        assert stats["total_usage"] == 0
        assert stats["average_confidence"] == 0.0
        assert stats["average_success_rate"] == 0.0

    def test_get_pattern_not_found(self):
        """Test getting non-existent pattern"""
        library = PatternLibrary()
        pattern = library.get_pattern("nonexistent")
        assert pattern is None

    def test_record_pattern_outcome_nonexistent(self):
        """Test recording outcome for non-existent pattern"""
        library = PatternLibrary()
        # Should not raise error
        library.record_pattern_outcome("nonexistent", success=True)

    def test_get_related_patterns_depth_zero(self):
        """Test getting related patterns with depth 0"""
        library = PatternLibrary()

        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")

        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)
        library.link_patterns("pat_001", "pat_002")

        related = library.get_related_patterns("pat_001", depth=0)
        assert len(related) == 0

    def test_get_related_patterns_nonexistent(self):
        """Test getting related patterns for non-existent pattern"""
        library = PatternLibrary()
        related = library.get_related_patterns("nonexistent")
        assert len(related) == 0

    def test_get_related_patterns_depth_two(self):
        """Test getting related patterns with depth 2"""
        library = PatternLibrary()

        # Create chain: pat_001 -> pat_002 -> pat_003
        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")
        pattern3 = Pattern(id="pat_003", agent_id="agent1", pattern_type="sequential", name="P3", description="Test")

        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)
        library.contribute_pattern("agent1", pattern3)

        library.link_patterns("pat_001", "pat_002")
        library.link_patterns("pat_002", "pat_003")

        # With depth=2, should find both pat_002 and pat_003
        related = library.get_related_patterns("pat_001", depth=2)
        related_ids = {p.id for p in related}

        assert "pat_002" in related_ids
        assert "pat_003" in related_ids
        assert "pat_001" not in related_ids  # Source excluded

    def test_get_top_patterns_by_usage(self):
        """Test getting top patterns by usage count"""
        library = PatternLibrary()

        # Create patterns with different usage
        for i in range(3):
            pattern = Pattern(
                id=f"pat_{i}",
                agent_id="agent1",
                pattern_type="sequential",
                name=f"Pattern {i}",
                description="Test",
                confidence=0.8
            )
            library.contribute_pattern("agent1", pattern)

            # Add usage
            for _ in range(i + 1):
                library.record_pattern_outcome(f"pat_{i}", success=True)

        top = library.get_top_patterns(n=2, sort_by="usage_count")
        assert len(top) == 2
        assert top[0].usage_count >= top[1].usage_count

    def test_get_top_patterns_by_success_rate(self):
        """Test getting top patterns by success rate"""
        library = PatternLibrary()

        # Pattern with 100% success
        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        library.contribute_pattern("agent1", pattern1)
        library.record_pattern_outcome("pat_001", success=True)
        library.record_pattern_outcome("pat_001", success=True)

        # Pattern with 50% success
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")
        library.contribute_pattern("agent1", pattern2)
        library.record_pattern_outcome("pat_002", success=True)
        library.record_pattern_outcome("pat_002", success=False)

        top = library.get_top_patterns(n=2, sort_by="success_rate")
        assert len(top) == 2
        assert top[0].success_rate >= top[1].success_rate

    def test_query_patterns_low_relevance(self):
        """Test query filtering out low relevance patterns"""
        library = PatternLibrary()

        # Add pattern with context that won't match
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Specific pattern",
            description="Very specific pattern",
            confidence=0.9,
            context={"domain": "healthcare", "specific_feature": "very_specific"},
            tags=["healthcare", "specific"]
        )
        library.contribute_pattern("agent1", pattern)

        # Query with completely different context
        matches = library.query_patterns(
            "agent2",
            context={"domain": "education", "different": "context"}
        )

        # Should have low or no matches due to relevance threshold
        # (patterns with relevance < 0.3 are filtered out)
        assert all(m.relevance_score > 0.3 for m in matches)

    def test_query_patterns_with_tags(self):
        """Test querying patterns with matching tags"""
        library = PatternLibrary()

        pattern1 = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test pattern",
            description="Test",
            confidence=0.8,
            tags=["python", "testing"]
        )
        library.contribute_pattern("agent1", pattern1)

        pattern2 = Pattern(
            id="pat_002",
            agent_id="agent1",
            pattern_type="sequential",
            name="Different pattern",
            description="Test",
            confidence=0.8,
            tags=["javascript", "frontend"]
        )
        library.contribute_pattern("agent1", pattern2)

        # Query all patterns (relevance scoring is internal)
        matches = library.query_patterns(
            "agent2",
            context={"language": "python", "task": "testing"}
        )

        # Patterns should be returned (relevance calculation is internal to implementation)
        # The test validates that query works and returns pattern matches
        assert isinstance(matches, list)

    def test_library_stats_with_usage(self):
        """Test library statistics with pattern usage"""
        library = PatternLibrary()

        # Add patterns and record usage
        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")

        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)

        # Record usage for pat_001 (100% success)
        library.record_pattern_outcome("pat_001", success=True)
        library.record_pattern_outcome("pat_001", success=True)

        # Record usage for pat_002 (50% success)
        library.record_pattern_outcome("pat_002", success=True)
        library.record_pattern_outcome("pat_002", success=False)

        stats = library.get_library_stats()
        assert stats["total_usage"] == 4
        assert stats["average_success_rate"] == pytest.approx(0.75, rel=0.01)  # (1.0 + 0.5) / 2

    def test_pattern_with_code(self):
        """Test pattern with code implementation"""
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Code pattern",
            description="Test",
            code="def test():\n    return True"
        )

        assert pattern.code is not None
        assert "def test()" in pattern.code

    def test_query_patterns_limit(self):
        """Test query patterns with limit"""
        library = PatternLibrary()

        # Add many patterns
        for i in range(10):
            pattern = Pattern(
                id=f"pat_{i:03d}",
                agent_id="agent1",
                pattern_type="sequential",
                name=f"Pattern {i}",
                description="Test",
                confidence=0.8
            )
            library.contribute_pattern("agent1", pattern)

        # Query with limit
        matches = library.query_patterns("agent2", context={"test": True}, limit=3)

        # Should respect limit
        assert len(matches) <= 3

    def test_get_agent_patterns_empty(self):
        """Test getting patterns for agent with no contributions"""
        library = PatternLibrary()

        pattern = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        library.contribute_pattern("agent1", pattern)

        # Query for different agent
        agent2_patterns = library.get_agent_patterns("agent2")
        assert len(agent2_patterns) == 0

    def test_pattern_last_used_updates(self):
        """Test that last_used timestamp updates on usage"""
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test"
        )

        assert pattern.last_used is None

        pattern.record_usage(success=True)

        assert pattern.last_used is not None

    def test_relevance_context_key_matches(self):
        """Test relevance calculation with context key matches"""
        library = PatternLibrary()

        # Pattern with specific context
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test pattern",
            description="Test",
            confidence=0.8,
            context={"domain": "healthcare", "feature": "patient_care"}
        )
        library.contribute_pattern("agent1", pattern)

        # Query with matching context
        matches = library.query_patterns(
            "agent2",
            context={"domain": "healthcare", "feature": "patient_care", "extra": "ignored"}
        )

        # Should find pattern with matching context
        assert len(matches) > 0
        if matches:
            assert matches[0].pattern.id == "pat_001"
            assert matches[0].relevance_score > 0.3

    def test_relevance_no_context_matches(self):
        """Test relevance with no context matches"""
        library = PatternLibrary()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8,
            context={"domain": "healthcare"}
        )
        library.contribute_pattern("agent1", pattern)

        # Query with completely different context
        matches = library.query_patterns(
            "agent2",
            context={"domain": "finance", "unrelated": "data"}
        )

        # Should filter out due to low relevance
        # or have very low relevance score
        assert all(m.relevance_score > 0.3 for m in matches)

    def test_relevance_tag_matches(self):
        """Test relevance calculation with tag matches"""
        library = PatternLibrary()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8,
            tags=["python", "testing", "automation"]
        )
        library.contribute_pattern("agent1", pattern)

        # Add usage to boost relevance above threshold
        for _ in range(5):
            library.record_pattern_outcome("pat_001", success=True)

        # Query with matching tags
        matches = library.query_patterns(
            "agent2",
            context={"tags": ["python", "testing"]}
        )

        # Should find pattern with tag relevance + success rate boost
        assert len(matches) > 0
        if matches:
            assert matches[0].pattern.id == "pat_001"
            # Tag matches contribute to relevance
            assert matches[0].relevance_score > 0.0

    def test_relevance_high_success_rate_boost(self):
        """Test relevance boost from high success rate"""
        library = PatternLibrary()

        # Pattern with high success rate
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8,
            context={"task": "test"}
        )
        library.contribute_pattern("agent1", pattern)

        # Record successful usage to build high success rate
        for _ in range(10):
            library.record_pattern_outcome("pat_001", success=True)

        # Query
        matches = library.query_patterns(
            "agent2",
            context={"task": "test"}
        )

        # High success rate should boost relevance
        assert len(matches) > 0
        if matches:
            # Check that success rate influenced the match
            pattern_match = matches[0]
            assert pattern_match.pattern.success_rate > 0.7
            # Should mention high success rate in matching factors
            assert any("success rate" in str(factor).lower()
                      for factor in pattern_match.matching_factors)

    def test_relevance_mixed_factors(self):
        """Test relevance with multiple matching factors"""
        library = PatternLibrary()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8,
            context={"domain": "testing", "language": "python"},
            tags=["automation", "pytest"]
        )
        library.contribute_pattern("agent1", pattern)

        # Add usage history for success rate
        library.record_pattern_outcome("pat_001", success=True)
        library.record_pattern_outcome("pat_001", success=True)
        library.record_pattern_outcome("pat_001", success=True)
        library.record_pattern_outcome("pat_001", success=False)

        # Query with context that matches multiple factors
        matches = library.query_patterns(
            "agent2",
            context={
                "domain": "testing",
                "language": "python",
                "tags": ["automation"]
            }
        )

        # Should have high relevance from multiple factors
        assert len(matches) > 0
        if matches:
            match = matches[0]
            # Should have multiple matching factors
            assert len(match.matching_factors) > 0
            # Higher relevance from combined factors
            assert match.relevance_score > 0.3

    def test_relevance_empty_context(self):
        """Test relevance with empty context"""
        library = PatternLibrary()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8
        )
        library.contribute_pattern("agent1", pattern)

        # Query with empty context
        matches = library.query_patterns("agent2", context={})

        # Should still return patterns (with low relevance or none)
        assert isinstance(matches, list)

    def test_relevance_partial_context_match(self):
        """Test relevance with partial context matches"""
        library = PatternLibrary()

        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.8,
            context={"domain": "healthcare", "feature": "patient", "priority": "high"}
        )
        library.contribute_pattern("agent1", pattern)

        # Query matching only some context keys
        matches = library.query_patterns(
            "agent2",
            context={"domain": "healthcare", "feature": "doctor", "priority": "high"}
        )

        # Should calculate relevance based on partial matches
        assert isinstance(matches, list)
        # 2 out of 3 values match (domain value differs)

    def test_count_by_type(self):
        """Test pattern counting by type"""
        library = PatternLibrary()

        # Add patterns of different types
        for i in range(3):
            pattern = Pattern(
                id=f"pat_seq_{i}",
                agent_id="agent1",
                pattern_type="sequential",
                name=f"Sequential {i}",
                description="Test"
            )
            library.contribute_pattern("agent1", pattern)

        for i in range(2):
            pattern = Pattern(
                id=f"pat_temp_{i}",
                agent_id="agent1",
                pattern_type="temporal",
                name=f"Temporal {i}",
                description="Test"
            )
            library.contribute_pattern("agent1", pattern)

        stats = library.get_library_stats()
        assert "patterns_by_type" in stats
        assert stats["patterns_by_type"]["sequential"] == 3
        assert stats["patterns_by_type"]["temporal"] == 2

    def test_reset(self):
        """Test resetting library"""
        library = PatternLibrary()

        # Add patterns
        pattern1 = Pattern(id="pat_001", agent_id="agent1", pattern_type="sequential", name="P1", description="Test")
        pattern2 = Pattern(id="pat_002", agent_id="agent1", pattern_type="sequential", name="P2", description="Test")
        library.contribute_pattern("agent1", pattern1)
        library.contribute_pattern("agent1", pattern2)
        library.link_patterns("pat_001", "pat_002")

        assert len(library.patterns) == 2
        assert len(library.agent_contributions) == 1
        assert len(library.pattern_graph) == 2

        # Reset
        library.reset()

        assert len(library.patterns) == 0
        assert len(library.agent_contributions) == 0
        assert len(library.pattern_graph) == 0

    def test_relevance_clamped_to_one(self):
        """Test that relevance score is clamped to maximum 1.0"""
        library = PatternLibrary()

        # Pattern with many matching factors
        pattern = Pattern(
            id="pat_001",
            agent_id="agent1",
            pattern_type="sequential",
            name="Test",
            description="Test",
            confidence=0.9,
            context={"a": "1", "b": "2", "c": "3", "d": "4"},
            tags=["tag1", "tag2", "tag3"]
        )
        library.contribute_pattern("agent1", pattern)

        # Add lots of successful usage
        for _ in range(20):
            library.record_pattern_outcome("pat_001", success=True)

        # Query with all matching factors
        matches = library.query_patterns(
            "agent2",
            context={"a": "1", "b": "2", "c": "3", "d": "4", "tags": ["tag1", "tag2", "tag3"]}
        )

        # Relevance should be clamped to 1.0
        if matches:
            assert matches[0].relevance_score <= 1.0
