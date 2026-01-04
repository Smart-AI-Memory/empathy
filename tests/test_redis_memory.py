"""Tests for Redis Short-Term Memory

Tests cover:
- Role-based access control
- Working memory (stash/retrieve)
- Pattern staging workflow
- Conflict negotiation context
- Coordination signals
- Session management

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os.redis_memory import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    RedisShortTermMemory,
    StagedPattern,
    TTLStrategy,
)


class TestAccessTier:
    """Test AccessTier enum"""

    def test_tier_values(self):
        """Test tier numeric values"""
        assert AccessTier.OBSERVER.value == 1
        assert AccessTier.CONTRIBUTOR.value == 2
        assert AccessTier.VALIDATOR.value == 3
        assert AccessTier.STEWARD.value == 4

    def test_tier_ordering(self):
        """Test tiers are properly ordered"""
        assert AccessTier.OBSERVER.value < AccessTier.CONTRIBUTOR.value
        assert AccessTier.CONTRIBUTOR.value < AccessTier.VALIDATOR.value
        assert AccessTier.VALIDATOR.value < AccessTier.STEWARD.value


class TestAgentCredentials:
    """Test AgentCredentials dataclass"""

    def test_observer_permissions(self):
        """Observer can only read"""
        creds = AgentCredentials("observer_1", AccessTier.OBSERVER)
        assert creds.can_read() is True
        assert creds.can_stage() is False
        assert creds.can_validate() is False
        assert creds.can_administer() is False

    def test_contributor_permissions(self):
        """Contributor can read and stage"""
        creds = AgentCredentials("contributor_1", AccessTier.CONTRIBUTOR)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is False
        assert creds.can_administer() is False

    def test_validator_permissions(self):
        """Validator can read, stage, and validate"""
        creds = AgentCredentials("validator_1", AccessTier.VALIDATOR)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is True
        assert creds.can_administer() is False

    def test_steward_permissions(self):
        """Steward has full access"""
        creds = AgentCredentials("steward_1", AccessTier.STEWARD)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is True
        assert creds.can_administer() is True


class TestStagedPattern:
    """Test StagedPattern dataclass"""

    def test_to_dict(self):
        """Test serialization to dict"""
        pattern = StagedPattern(
            pattern_id="pat_123",
            agent_id="agent_1",
            pattern_type="coding",
            name="Error Handler",
            description="Standard error handling pattern",
            interests=["reliability", "maintainability"],
        )
        data = pattern.to_dict()

        assert data["pattern_id"] == "pat_123"
        assert data["agent_id"] == "agent_1"
        assert data["interests"] == ["reliability", "maintainability"]
        assert "staged_at" in data

    def test_from_dict(self):
        """Test deserialization from dict"""
        data = {
            "pattern_id": "pat_456",
            "agent_id": "agent_2",
            "pattern_type": "architecture",
            "name": "Service Layer",
            "description": "Service layer pattern",
            "confidence": 0.85,
            "staged_at": "2025-01-01T10:00:00",
            "interests": ["separation", "testability"],
        }
        pattern = StagedPattern.from_dict(data)

        assert pattern.pattern_id == "pat_456"
        assert pattern.confidence == 0.85
        assert pattern.interests == ["separation", "testability"]


class TestConflictContext:
    """Test ConflictContext dataclass"""

    def test_conflict_creation(self):
        """Test creating conflict context"""
        context = ConflictContext(
            conflict_id="conf_1",
            positions={
                "agent_1": "Use null checks everywhere",
                "agent_2": "Skip validation for performance",
            },
            interests={
                "agent_1": ["reliability", "crash prevention"],
                "agent_2": ["speed", "reduced latency"],
            },
            batna="team_priority",
        )

        assert context.conflict_id == "conf_1"
        assert len(context.positions) == 2
        assert context.batna == "team_priority"
        assert context.resolved is False

    def test_to_dict_and_back(self):
        """Test serialization round-trip"""
        original = ConflictContext(
            conflict_id="conf_2",
            positions={"a": "pos_a", "b": "pos_b"},
            interests={"a": ["int_1"], "b": ["int_2"]},
        )
        data = original.to_dict()
        restored = ConflictContext.from_dict(data)

        assert restored.conflict_id == original.conflict_id
        assert restored.positions == original.positions
        assert restored.interests == original.interests


class TestRedisShortTermMemory:
    """Test RedisShortTermMemory class"""

    @pytest.fixture
    def memory(self):
        """Create mock memory instance"""
        return RedisShortTermMemory(use_mock=True)

    @pytest.fixture
    def contributor(self):
        """Create contributor credentials"""
        return AgentCredentials("contributor_1", AccessTier.CONTRIBUTOR)

    @pytest.fixture
    def observer(self):
        """Create observer credentials"""
        return AgentCredentials("observer_1", AccessTier.OBSERVER)

    @pytest.fixture
    def validator(self):
        """Create validator credentials"""
        return AgentCredentials("validator_1", AccessTier.VALIDATOR)

    @pytest.fixture
    def steward(self):
        """Create steward credentials"""
        return AgentCredentials("steward_1", AccessTier.STEWARD)

    # === Working Memory Tests ===

    def test_stash_and_retrieve(self, memory, contributor):
        """Test basic stash and retrieve"""
        data = {"analysis": "complete", "issues": 3}
        memory.stash("results", data, contributor)
        retrieved = memory.retrieve("results", contributor)

        assert retrieved == data

    def test_stash_requires_contributor(self, memory, observer):
        """Test that observers cannot stash"""
        with pytest.raises(PermissionError):
            memory.stash("data", {"test": 1}, observer)

    def test_retrieve_nonexistent_returns_none(self, memory, contributor):
        """Test retrieving nonexistent key"""
        result = memory.retrieve("nonexistent", contributor)
        assert result is None

    def test_clear_working_memory(self, memory, contributor):
        """Test clearing working memory"""
        memory.stash("key1", "val1", contributor)
        memory.stash("key2", "val2", contributor)

        cleared = memory.clear_working_memory(contributor)
        assert cleared == 2

        assert memory.retrieve("key1", contributor) is None
        assert memory.retrieve("key2", contributor) is None

    # === Pattern Staging Tests ===

    def test_stage_pattern(self, memory, contributor):
        """Test staging a pattern"""
        pattern = StagedPattern(
            pattern_id="pat_test",
            agent_id=contributor.agent_id,
            pattern_type="coding",
            name="Test Pattern",
            description="A test pattern",
        )

        result = memory.stage_pattern(pattern, contributor)
        assert result is True

        retrieved = memory.get_staged_pattern("pat_test", contributor)
        assert retrieved is not None
        assert retrieved.name == "Test Pattern"

    def test_stage_pattern_requires_contributor(self, memory, observer):
        """Test that observers cannot stage patterns"""
        pattern = StagedPattern(
            pattern_id="pat_fail",
            agent_id=observer.agent_id,
            pattern_type="coding",
            name="Fail",
            description="Should fail",
        )

        with pytest.raises(PermissionError):
            memory.stage_pattern(pattern, observer)

    def test_list_staged_patterns(self, memory, contributor):
        """Test listing staged patterns"""
        for i in range(3):
            pattern = StagedPattern(
                pattern_id=f"pat_{i}",
                agent_id=contributor.agent_id,
                pattern_type="coding",
                name=f"Pattern {i}",
                description=f"Description {i}",
            )
            memory.stage_pattern(pattern, contributor)

        patterns = memory.list_staged_patterns(contributor)
        assert len(patterns) == 3

    def test_promote_pattern(self, memory, contributor, validator):
        """Test promoting a staged pattern"""
        pattern = StagedPattern(
            pattern_id="pat_promote",
            agent_id=contributor.agent_id,
            pattern_type="coding",
            name="To Promote",
            description="Will be promoted",
        )
        memory.stage_pattern(pattern, contributor)

        promoted = memory.promote_pattern("pat_promote", validator)
        assert promoted is not None
        assert promoted.name == "To Promote"

        # Should be removed from staging
        assert memory.get_staged_pattern("pat_promote", validator) is None

    def test_promote_requires_validator(self, memory, contributor):
        """Test that contributors cannot promote"""
        pattern = StagedPattern(
            pattern_id="pat_blocked",
            agent_id=contributor.agent_id,
            pattern_type="coding",
            name="Blocked",
            description="Should not promote",
        )
        memory.stage_pattern(pattern, contributor)

        with pytest.raises(PermissionError):
            memory.promote_pattern("pat_blocked", contributor)

    def test_reject_pattern(self, memory, contributor, validator):
        """Test rejecting a staged pattern"""
        pattern = StagedPattern(
            pattern_id="pat_reject",
            agent_id=contributor.agent_id,
            pattern_type="coding",
            name="To Reject",
            description="Will be rejected",
        )
        memory.stage_pattern(pattern, contributor)

        result = memory.reject_pattern("pat_reject", validator, "Not up to standards")
        assert result is True
        assert memory.get_staged_pattern("pat_reject", validator) is None

    # === Conflict Negotiation Tests ===

    def test_create_conflict_context(self, memory, contributor):
        """Test creating conflict context"""
        context = memory.create_conflict_context(
            conflict_id="conflict_1",
            positions={
                "agent_a": "Add null checks",
                "agent_b": "Skip for performance",
            },
            interests={
                "agent_a": ["reliability", "safety"],
                "agent_b": ["speed", "simplicity"],
            },
            credentials=contributor,
            batna="team_priority",
        )

        assert context.conflict_id == "conflict_1"
        assert context.batna == "team_priority"

    def test_get_conflict_context(self, memory, contributor, observer):
        """Test retrieving conflict context"""
        memory.create_conflict_context(
            conflict_id="conflict_2",
            positions={"a": "pos_a"},
            interests={"a": ["int_a"]},
            credentials=contributor,
        )

        # Even observers can read
        retrieved = memory.get_conflict_context("conflict_2", observer)
        assert retrieved is not None
        assert retrieved.positions == {"a": "pos_a"}

    def test_resolve_conflict(self, memory, contributor, validator):
        """Test resolving a conflict"""
        memory.create_conflict_context(
            conflict_id="conflict_3",
            positions={"a": "pos_a", "b": "pos_b"},
            interests={"a": ["int_a"], "b": ["int_b"]},
            credentials=contributor,
        )

        result = memory.resolve_conflict(
            "conflict_3",
            resolution="Synthesis: null check with early return",
            credentials=validator,
        )
        assert result is True

        context = memory.get_conflict_context("conflict_3", validator)
        assert context.resolved is True
        assert "Synthesis" in context.resolution

    def test_resolve_requires_validator(self, memory, contributor):
        """Test that contributors cannot resolve conflicts"""
        memory.create_conflict_context(
            conflict_id="conflict_4",
            positions={"a": "pos_a"},
            interests={"a": ["int_a"]},
            credentials=contributor,
        )

        with pytest.raises(PermissionError):
            memory.resolve_conflict("conflict_4", "resolution", contributor)

    # === Coordination Signal Tests ===

    def test_send_and_receive_signal(self, memory, contributor):
        """Test sending and receiving signals"""
        other_creds = AgentCredentials("other_agent", AccessTier.CONTRIBUTOR)

        memory.send_signal(
            signal_type="ready",
            data={"status": "analysis_complete"},
            credentials=contributor,
            target_agent="other_agent",
        )

        signals = memory.receive_signals(other_creds, signal_type="ready")
        assert len(signals) == 1
        assert signals[0]["data"]["status"] == "analysis_complete"

    def test_broadcast_signal(self, memory, contributor):
        """Test broadcast signals"""
        memory.send_signal(
            signal_type="announcement",
            data={"message": "New pattern available"},
            credentials=contributor,
            target_agent=None,  # Broadcast
        )

        # Any agent should receive broadcasts
        receiver = AgentCredentials("any_agent", AccessTier.OBSERVER)
        signals = memory.receive_signals(receiver)
        assert len(signals) >= 1

    # === Session Management Tests ===

    def test_create_and_join_session(self, memory, contributor):
        """Test session creation and joining"""
        memory.create_session("session_1", contributor, {"task": "code_review"})

        other = AgentCredentials("joiner", AccessTier.CONTRIBUTOR)
        result = memory.join_session("session_1", other)
        assert result is True

        session = memory.get_session("session_1", contributor)
        assert "contributor_1" in session["participants"]
        assert "joiner" in session["participants"]

    def test_get_nonexistent_session(self, memory, contributor):
        """Test getting nonexistent session"""
        result = memory.get_session("fake_session", contributor)
        assert result is None

    # === Health and Stats Tests ===

    def test_ping(self, memory):
        """Test health check"""
        assert memory.ping() is True

    def test_get_stats(self, memory, contributor):
        """Test statistics collection"""
        # Add some data
        memory.stash("test_key", {"data": 1}, contributor)
        pattern = StagedPattern(
            pattern_id="stat_test",
            agent_id=contributor.agent_id,
            pattern_type="test",
            name="Stats Test",
            description="For stats",
        )
        memory.stage_pattern(pattern, contributor)

        stats = memory.get_stats()
        assert stats["mode"] == "mock"
        assert stats["total_keys"] >= 2
        assert stats["working_keys"] >= 1
        assert stats["staged_keys"] >= 1


class TestTTLStrategy:
    """Test TTL strategy values"""

    def test_ttl_values(self):
        """Test TTL values are reasonable"""
        assert TTLStrategy.WORKING_RESULTS.value == 3600  # 1 hour
        assert TTLStrategy.STAGED_PATTERNS.value == 86400  # 24 hours
        assert TTLStrategy.COORDINATION.value == 300  # 5 minutes
        assert TTLStrategy.SESSION.value == 1800  # 30 minutes

    def test_conflict_context_ttl_longer(self):
        """Conflict context should have longer TTL for audit"""
        assert TTLStrategy.CONFLICT_CONTEXT.value > TTLStrategy.WORKING_RESULTS.value


class TestIntegrationWorkflow:
    """Integration tests for complete workflows"""

    @pytest.fixture
    def memory(self):
        return RedisShortTermMemory(use_mock=True)

    def test_pattern_staging_workflow(self, memory):
        """Test complete pattern staging workflow"""
        # Step 1: Contributor discovers pattern
        contributor = AgentCredentials("analyst", AccessTier.CONTRIBUTOR)
        pattern = StagedPattern(
            pattern_id="workflow_pat",
            agent_id="analyst",
            pattern_type="architecture",
            name="Repository Pattern",
            description="Data access abstraction",
            interests=["maintainability", "testability"],
            confidence=0.75,
        )
        memory.stage_pattern(pattern, contributor)

        # Step 2: Validator reviews staged patterns
        validator = AgentCredentials("reviewer", AccessTier.VALIDATOR)
        staged = memory.list_staged_patterns(validator)
        assert len(staged) == 1

        # Step 3: Validator promotes pattern
        promoted = memory.promote_pattern("workflow_pat", validator)
        assert promoted.interests == ["maintainability", "testability"]

        # Step 4: Staging is now empty
        remaining = memory.list_staged_patterns(validator)
        assert len(remaining) == 0

    def test_conflict_resolution_workflow(self, memory):
        """Test complete conflict resolution with principled negotiation"""
        # Step 1: Identify conflict
        mediator = AgentCredentials("mediator", AccessTier.CONTRIBUTOR)
        memory.create_conflict_context(
            conflict_id="security_vs_perf",
            positions={
                "security_agent": "Validate all inputs before processing",
                "perf_agent": "Skip validation for trusted internal calls",
            },
            interests={
                "security_agent": ["data integrity", "attack prevention", "compliance"],
                "perf_agent": ["low latency", "throughput", "resource efficiency"],
            },
            credentials=mediator,
            batna="security_wins",  # Default: safety first
        )

        # Step 2: Analyze interests to find synthesis
        # Both care about: system reliability (security via integrity, perf via uptime)

        # Step 3: Validator resolves with synthesis
        validator = AgentCredentials("arbiter", AccessTier.VALIDATOR)
        memory.resolve_conflict(
            "security_vs_perf",
            resolution=(
                "Synthesis: Validate at system boundaries only. "
                "Internal calls between trusted services skip validation. "
                "Satisfies security (boundary protection) and performance (internal speed)."
            ),
            credentials=validator,
        )

        # Step 4: Verify resolution
        resolved = memory.get_conflict_context("security_vs_perf", validator)
        assert resolved.resolved is True
        assert "Synthesis" in resolved.resolution
        assert "boundary" in resolved.resolution.lower()

    def test_multi_agent_coordination(self, memory):
        """Test multi-agent coordination using signals"""
        # Create agents
        analyzer = AgentCredentials("analyzer", AccessTier.CONTRIBUTOR)
        reviewer = AgentCredentials("reviewer", AccessTier.CONTRIBUTOR)

        # Analyzer stashes results and signals completion
        memory.stash(
            "analysis_results",
            {"files_analyzed": 50, "issues_found": 3},
            analyzer,
        )
        memory.send_signal(
            signal_type="task_complete",
            data={"task": "analysis", "output_key": "analysis_results"},
            credentials=analyzer,
            target_agent="reviewer",
        )

        # Reviewer receives signal
        signals = memory.receive_signals(reviewer, signal_type="task_complete")
        assert len(signals) == 1
        assert signals[0]["data"]["task"] == "analysis"

        # Reviewer gets analyzer's results
        results = memory.retrieve(
            "analysis_results",
            reviewer,
            agent_id="analyzer",  # Get from analyzer's namespace
        )
        assert results["issues_found"] == 3
