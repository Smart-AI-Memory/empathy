"""Integration Tests for Redis Short-Term Memory

These tests run against a REAL Redis instance, not the mock.
They verify that all features work correctly with actual Redis.

Prerequisites:
    - Redis running on localhost:6379
    - Run: docker-compose up redis -d

Usage:
    pytest tests/test_redis_integration.py -v
    pytest tests/test_redis_integration.py -v -k "test_stash"

Skip these tests if Redis is not available:
    pytest tests/test_redis_integration.py -v --ignore-glob="*integration*"

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os.redis_config import get_redis_memory
from empathy_os.redis_memory import AccessTier, AgentCredentials, StagedPattern, TTLStrategy


def redis_available() -> bool:
    """Check if Redis is available (respects REDIS_URL env var)"""
    try:
        memory = get_redis_memory()
        if memory.use_mock:
            return False  # Mock mode doesn't count as "available"
        return memory.ping()
    except Exception:
        return False


# Skip all tests in this module if Redis is not available
pytestmark = pytest.mark.skipif(
    not redis_available(),
    reason="Redis not available. Run: docker-compose up redis -d",
)


@pytest.fixture
def memory():
    """Create real Redis memory instance (respects REDIS_URL env var)"""
    mem = get_redis_memory()
    yield mem
    # Cleanup: Clear all empathy keys after each test
    if mem._client:
        for prefix in [
            mem.PREFIX_WORKING,
            mem.PREFIX_STAGED,
            mem.PREFIX_CONFLICT,
            mem.PREFIX_COORDINATION,
            mem.PREFIX_SESSION,
        ]:
            keys = mem._client.keys(f"{prefix}*")
            if keys:
                mem._client.delete(*keys)


@pytest.fixture
def contributor():
    """Create contributor credentials"""
    return AgentCredentials("integration_test_contributor", AccessTier.CONTRIBUTOR)


@pytest.fixture
def validator():
    """Create validator credentials"""
    return AgentCredentials("integration_test_validator", AccessTier.VALIDATOR)


class TestRedisConnection:
    """Test basic Redis connectivity"""

    def test_ping(self, memory):
        """Test Redis responds to ping"""
        assert memory.ping() is True

    def test_mode_is_redis(self, memory):
        """Test we're using real Redis, not mock"""
        stats = memory.get_stats()
        assert stats["mode"] == "redis"

    def test_get_stats(self, memory):
        """Test stats retrieval from real Redis"""
        stats = memory.get_stats()
        assert "used_memory" in stats
        assert "total_keys" in stats


class TestWorkingMemoryIntegration:
    """Test working memory with real Redis"""

    def test_stash_and_retrieve_simple(self, memory, contributor):
        """Test basic stash and retrieve"""
        data = {"test": "value", "number": 42}
        memory.stash("test_key", data, contributor)

        retrieved = memory.retrieve("test_key", contributor)
        assert retrieved == data

    def test_stash_and_retrieve_complex(self, memory, contributor):
        """Test complex nested data"""
        data = {
            "analysis": {
                "files": ["a.py", "b.py"],
                "metrics": {"complexity": 7.5, "coverage": 0.85},
            },
            "recommendations": ["refactor", "add_tests"],
        }
        memory.stash("complex_data", data, contributor)

        retrieved = memory.retrieve("complex_data", contributor)
        assert retrieved == data
        assert retrieved["analysis"]["metrics"]["complexity"] == 7.5

    def test_stash_overwrites_existing(self, memory, contributor):
        """Test that stashing same key overwrites"""
        memory.stash("overwrite_key", {"version": 1}, contributor)
        memory.stash("overwrite_key", {"version": 2}, contributor)

        retrieved = memory.retrieve("overwrite_key", contributor)
        assert retrieved["version"] == 2

    def test_retrieve_nonexistent_returns_none(self, memory, contributor):
        """Test retrieving nonexistent key"""
        result = memory.retrieve("nonexistent_key_12345", contributor)
        assert result is None

    def test_clear_working_memory(self, memory, contributor):
        """Test clearing all working memory for an agent"""
        # Stash multiple items
        for i in range(5):
            memory.stash(f"clear_test_{i}", {"index": i}, contributor)

        # Clear
        cleared = memory.clear_working_memory(contributor)
        assert cleared == 5

        # Verify all gone
        for i in range(5):
            assert memory.retrieve(f"clear_test_{i}", contributor) is None


class TestPatternStagingIntegration:
    """Test pattern staging with real Redis"""

    def test_stage_and_retrieve_pattern(self, memory, contributor):
        """Test staging a pattern"""
        pattern = StagedPattern(
            pattern_id="int_test_pattern_1",
            agent_id=contributor.agent_id,
            pattern_type="testing",
            name="Integration Test Pattern",
            description="A pattern for integration testing",
            confidence=0.9,
        )

        result = memory.stage_pattern(pattern, contributor)
        assert result is True

        retrieved = memory.get_staged_pattern("int_test_pattern_1", contributor)
        assert retrieved is not None
        assert retrieved.name == "Integration Test Pattern"
        assert retrieved.confidence == 0.9

    def test_list_staged_patterns(self, memory, contributor):
        """Test listing multiple staged patterns"""
        # Stage multiple patterns
        for i in range(3):
            pattern = StagedPattern(
                pattern_id=f"int_list_test_{i}",
                agent_id=contributor.agent_id,
                pattern_type="testing",
                name=f"List Test Pattern {i}",
                description=f"Pattern {i} for list testing",
            )
            memory.stage_pattern(pattern, contributor)

        # List them
        patterns = memory.list_staged_patterns(contributor)
        list_patterns = [p for p in patterns if p.pattern_id.startswith("int_list_test_")]
        assert len(list_patterns) == 3

    def test_promote_pattern(self, memory, contributor, validator):
        """Test promoting a staged pattern"""
        pattern = StagedPattern(
            pattern_id="int_promote_test",
            agent_id=contributor.agent_id,
            pattern_type="testing",
            name="Promote Test Pattern",
            description="To be promoted",
        )
        memory.stage_pattern(pattern, contributor)

        # Promote
        promoted = memory.promote_pattern("int_promote_test", validator)
        assert promoted is not None
        assert promoted.name == "Promote Test Pattern"

        # Verify removed from staging
        assert memory.get_staged_pattern("int_promote_test", validator) is None

    def test_reject_pattern(self, memory, contributor, validator):
        """Test rejecting a staged pattern"""
        pattern = StagedPattern(
            pattern_id="int_reject_test",
            agent_id=contributor.agent_id,
            pattern_type="testing",
            name="Reject Test Pattern",
            description="To be rejected",
        )
        memory.stage_pattern(pattern, contributor)

        # Reject
        result = memory.reject_pattern("int_reject_test", validator, "Not good enough")
        assert result is True
        assert memory.get_staged_pattern("int_reject_test", validator) is None


class TestConflictResolutionIntegration:
    """Test conflict resolution with real Redis"""

    def test_create_and_get_conflict(self, memory, contributor):
        """Test creating and retrieving conflict context"""
        context = memory.create_conflict_context(
            conflict_id="int_conflict_1",
            positions={"agent_a": "Option A", "agent_b": "Option B"},
            interests={"agent_a": ["speed"], "agent_b": ["safety"]},
            credentials=contributor,
            batna="escalate_to_human",
        )

        assert context.conflict_id == "int_conflict_1"

        retrieved = memory.get_conflict_context("int_conflict_1", contributor)
        assert retrieved is not None
        assert retrieved.batna == "escalate_to_human"
        assert retrieved.resolved is False

    def test_resolve_conflict(self, memory, contributor, validator):
        """Test resolving a conflict"""
        memory.create_conflict_context(
            conflict_id="int_conflict_2",
            positions={"a": "pos_a", "b": "pos_b"},
            interests={"a": ["int_a"], "b": ["int_b"]},
            credentials=contributor,
        )

        result = memory.resolve_conflict(
            "int_conflict_2",
            resolution="Synthesis: Combined approach",
            credentials=validator,
        )
        assert result is True

        resolved = memory.get_conflict_context("int_conflict_2", contributor)
        assert resolved.resolved is True
        assert "Synthesis" in resolved.resolution


class TestCoordinationSignalsIntegration:
    """Test coordination signals with real Redis"""

    def test_send_and_receive_targeted_signal(self, memory, contributor):
        """Test sending targeted signal"""
        receiver = AgentCredentials("int_receiver", AccessTier.CONTRIBUTOR)

        memory.send_signal(
            signal_type="task_complete",
            data={"task_id": "task_123", "status": "done"},
            credentials=contributor,
            target_agent="int_receiver",
        )

        signals = memory.receive_signals(receiver, signal_type="task_complete")
        assert len(signals) >= 1

        our_signal = [s for s in signals if s["data"].get("task_id") == "task_123"]
        assert len(our_signal) == 1
        assert our_signal[0]["data"]["status"] == "done"

    def test_broadcast_signal(self, memory, contributor):
        """Test broadcast signal"""
        memory.send_signal(
            signal_type="announcement",
            data={"message": "System update complete"},
            credentials=contributor,
            target_agent=None,  # Broadcast
        )

        # Any agent should receive broadcasts
        any_agent = AgentCredentials("int_any_agent", AccessTier.OBSERVER)
        signals = memory.receive_signals(any_agent)
        # Should have at least our broadcast
        assert len(signals) >= 1


class TestSessionManagementIntegration:
    """Test session management with real Redis"""

    def test_create_and_join_session(self, memory, contributor):
        """Test session creation and joining"""
        memory.create_session(
            session_id="int_session_1",
            credentials=contributor,
            metadata={"purpose": "integration test"},
        )

        joiner = AgentCredentials("int_joiner", AccessTier.CONTRIBUTOR)
        result = memory.join_session("int_session_1", joiner)
        assert result is True

        session = memory.get_session("int_session_1", contributor)
        assert contributor.agent_id in session["participants"]
        assert "int_joiner" in session["participants"]
        assert session["metadata"]["purpose"] == "integration test"

    def test_get_nonexistent_session(self, memory, contributor):
        """Test getting nonexistent session"""
        result = memory.get_session("nonexistent_session_12345", contributor)
        assert result is None


class TestTTLBehavior:
    """Test TTL (time-to-live) behavior with real Redis"""

    def test_coordination_signal_expires(self, memory, contributor):
        """Test that coordination signals expire (TTL: 5 minutes)

        Note: This test uses a short sleep to verify Redis TTL is set,
        but doesn't wait the full 5 minutes. We verify the TTL is set correctly.
        """
        receiver = AgentCredentials("int_ttl_receiver", AccessTier.CONTRIBUTOR)

        memory.send_signal(
            signal_type="ttl_test",
            data={"test": "ttl"},
            credentials=contributor,
            target_agent="int_ttl_receiver",
        )

        # Verify signal exists
        signals = memory.receive_signals(receiver, signal_type="ttl_test")
        assert len(signals) >= 1

        # Check TTL is set (should be around 300 seconds for coordination)
        keys = memory._client.keys(f"{memory.PREFIX_COORDINATION}ttl_test:*")
        if keys:
            ttl = memory._client.ttl(keys[0])
            assert ttl > 0  # TTL is set
            assert ttl <= TTLStrategy.COORDINATION.value  # Not more than 5 min


class TestConcurrentAccess:
    """Test concurrent access patterns"""

    def test_multiple_agents_same_session(self, memory):
        """Test multiple agents can work in same session"""
        agents = [
            AgentCredentials(f"concurrent_agent_{i}", AccessTier.CONTRIBUTOR) for i in range(5)
        ]

        # Create session with first agent
        memory.create_session("concurrent_session", agents[0])

        # All others join
        for agent in agents[1:]:
            memory.join_session("concurrent_session", agent)

        # Verify all in session
        session = memory.get_session("concurrent_session", agents[0])
        assert len(session["participants"]) == 5

    def test_multiple_agents_stashing(self, memory):
        """Test multiple agents can stash independently"""
        agents = [AgentCredentials(f"stash_agent_{i}", AccessTier.CONTRIBUTOR) for i in range(3)]

        # Each agent stashes their own data
        for i, agent in enumerate(agents):
            memory.stash("my_data", {"agent_index": i}, agent)

        # Each retrieves their own
        for i, agent in enumerate(agents):
            data = memory.retrieve("my_data", agent)
            assert data["agent_index"] == i


class TestErrorHandling:
    """Test error handling with real Redis"""

    def test_permission_denied_observer_write(self, memory):
        """Test observer cannot write"""
        observer = AgentCredentials("obs", AccessTier.OBSERVER)

        with pytest.raises(PermissionError):
            memory.stash("forbidden", {"test": 1}, observer)

    def test_permission_denied_contributor_promote(self, memory, contributor):
        """Test contributor cannot promote"""
        pattern = StagedPattern(
            pattern_id="permission_test",
            agent_id=contributor.agent_id,
            pattern_type="test",
            name="Test",
            description="Test",
        )
        memory.stage_pattern(pattern, contributor)

        with pytest.raises(PermissionError):
            memory.promote_pattern("permission_test", contributor)


class TestEndToEndWorkflow:
    """End-to-end workflow tests"""

    def test_complete_pattern_lifecycle(self, memory):
        """Test complete pattern lifecycle: discover -> stage -> validate -> promote"""
        # Step 1: Contributor discovers pattern
        contributor = AgentCredentials("discoverer", AccessTier.CONTRIBUTOR)
        pattern = StagedPattern(
            pattern_id="lifecycle_pattern",
            agent_id="discoverer",
            pattern_type="workflow",
            name="Lifecycle Test Pattern",
            description="Tests the complete pattern lifecycle",
            confidence=0.8,
            interests=["testability", "reliability"],
        )
        memory.stage_pattern(pattern, contributor)

        # Step 2: Validator reviews
        validator = AgentCredentials("reviewer", AccessTier.VALIDATOR)
        staged = memory.list_staged_patterns(validator)
        our_pattern = [p for p in staged if p.pattern_id == "lifecycle_pattern"]
        assert len(our_pattern) == 1

        # Step 3: Validator promotes
        promoted = memory.promote_pattern("lifecycle_pattern", validator)
        assert promoted is not None
        assert promoted.confidence == 0.8

        # Step 4: Verify removed from staging
        remaining = memory.list_staged_patterns(validator)
        lifecycle_patterns = [p for p in remaining if p.pattern_id == "lifecycle_pattern"]
        assert len(lifecycle_patterns) == 0

    def test_multi_agent_code_review_simulation(self, memory):
        """Simulate a multi-agent code review workflow"""
        # Agents
        analyzer = AgentCredentials("code_analyzer", AccessTier.CONTRIBUTOR)
        security = AgentCredentials("security_checker", AccessTier.CONTRIBUTOR)
        reviewer = AgentCredentials("lead_reviewer", AccessTier.VALIDATOR)

        # Step 1: Create review session
        memory.create_session(
            "pr_review_42",
            analyzer,
            {"pr_number": 42, "files_changed": 15},
        )
        memory.join_session("pr_review_42", security)
        memory.join_session("pr_review_42", reviewer)

        # Step 2: Analyzer completes analysis
        memory.stash(
            "pr_42_analysis",
            {"complexity": "medium", "test_coverage": 0.75, "issues": 2},
            analyzer,
        )
        memory.send_signal(
            "analysis_complete",
            {"pr": 42, "agent": "code_analyzer"},
            analyzer,
            target_agent="lead_reviewer",
        )

        # Step 3: Security check
        memory.stash(
            "pr_42_security",
            {"vulnerabilities": 0, "warnings": 1, "passed": True},
            security,
        )
        memory.send_signal(
            "security_complete",
            {"pr": 42, "agent": "security_checker"},
            security,
            target_agent="lead_reviewer",
        )

        # Step 4: Reviewer aggregates
        signals = memory.receive_signals(reviewer)
        pr_42_signals = [s for s in signals if s["data"].get("pr") == 42]
        assert len(pr_42_signals) == 2

        analysis = memory.retrieve("pr_42_analysis", reviewer, agent_id="code_analyzer")
        security_check = memory.retrieve("pr_42_security", reviewer, agent_id="security_checker")

        assert analysis["issues"] == 2
        assert security_check["passed"] is True

        # Step 5: Session state
        session = memory.get_session("pr_review_42", reviewer)
        assert len(session["participants"]) == 3
