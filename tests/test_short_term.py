"""
Tests for src/empathy_os/memory/short_term.py

Tests the Redis-backed short-term memory system including:
- AccessTier enum and role-based permissions
- TTLStrategy enum values
- RedisConfig dataclass
- RedisMetrics tracking
- AgentCredentials permissions
- StagedPattern serialization
- ConflictContext for negotiation
- RedisShortTermMemory operations (mock mode)
"""

from datetime import datetime

from empathy_os.memory.short_term import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    PaginatedResult,
    RedisConfig,
    RedisMetrics,
    RedisShortTermMemory,
    StagedPattern,
    TimeWindowQuery,
    TTLStrategy,
)


class TestAccessTier:
    """Tests for AccessTier enum."""

    def test_observer_tier_value(self):
        """Test OBSERVER tier has value 1."""
        assert AccessTier.OBSERVER.value == 1

    def test_contributor_tier_value(self):
        """Test CONTRIBUTOR tier has value 2."""
        assert AccessTier.CONTRIBUTOR.value == 2

    def test_validator_tier_value(self):
        """Test VALIDATOR tier has value 3."""
        assert AccessTier.VALIDATOR.value == 3

    def test_steward_tier_value(self):
        """Test STEWARD tier has value 4."""
        assert AccessTier.STEWARD.value == 4

    def test_tier_ordering(self):
        """Test tier values are ordered correctly."""
        assert AccessTier.OBSERVER.value < AccessTier.CONTRIBUTOR.value
        assert AccessTier.CONTRIBUTOR.value < AccessTier.VALIDATOR.value
        assert AccessTier.VALIDATOR.value < AccessTier.STEWARD.value


class TestTTLStrategy:
    """Tests for TTLStrategy enum."""

    def test_working_results_ttl(self):
        """Test WORKING_RESULTS is 1 hour."""
        assert TTLStrategy.WORKING_RESULTS.value == 3600

    def test_staged_patterns_ttl(self):
        """Test STAGED_PATTERNS is 24 hours."""
        assert TTLStrategy.STAGED_PATTERNS.value == 86400

    def test_coordination_ttl(self):
        """Test COORDINATION is 5 minutes."""
        assert TTLStrategy.COORDINATION.value == 300

    def test_conflict_context_ttl(self):
        """Test CONFLICT_CONTEXT is 7 days."""
        assert TTLStrategy.CONFLICT_CONTEXT.value == 604800

    def test_session_ttl(self):
        """Test SESSION is 30 minutes."""
        assert TTLStrategy.SESSION.value == 1800

    def test_stream_entry_ttl(self):
        """Test STREAM_ENTRY is 7 days."""
        assert TTLStrategy.STREAM_ENTRY.value == 86400 * 7

    def test_task_queue_ttl(self):
        """Test TASK_QUEUE is 4 hours."""
        assert TTLStrategy.TASK_QUEUE.value == 3600 * 4


class TestRedisConfig:
    """Tests for RedisConfig dataclass."""

    def test_default_values(self):
        """Test RedisConfig default values."""
        config = RedisConfig()
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.db == 0
        assert config.password is None
        assert config.use_mock is False
        assert config.ssl is False
        assert config.max_connections == 10
        assert config.socket_timeout == 5.0
        assert config.retry_on_timeout is True
        assert config.retry_max_attempts == 3

    def test_custom_values(self):
        """Test RedisConfig with custom values."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=1,
            password="secret",
            ssl=True,
            max_connections=20,
        )
        assert config.host == "redis.example.com"
        assert config.port == 6380
        assert config.db == 1
        assert config.password == "secret"
        assert config.ssl is True
        assert config.max_connections == 20

    def test_to_redis_kwargs_basic(self):
        """Test to_redis_kwargs returns correct dict."""
        config = RedisConfig()
        kwargs = config.to_redis_kwargs()
        assert kwargs["host"] == "localhost"
        assert kwargs["port"] == 6379
        assert kwargs["db"] == 0
        assert kwargs["decode_responses"] is True

    def test_to_redis_kwargs_with_ssl(self):
        """Test to_redis_kwargs includes SSL settings."""
        config = RedisConfig(
            ssl=True,
            ssl_cert_reqs="required",
            ssl_ca_certs="/path/to/ca.crt",
        )
        kwargs = config.to_redis_kwargs()
        assert kwargs["ssl"] is True
        assert kwargs["ssl_cert_reqs"] == "required"
        assert kwargs["ssl_ca_certs"] == "/path/to/ca.crt"

    def test_sentinel_settings(self):
        """Test sentinel configuration."""
        config = RedisConfig(
            sentinel_hosts=[("sentinel1", 26379), ("sentinel2", 26379)],
            sentinel_master_name="mymaster",
        )
        assert len(config.sentinel_hosts) == 2
        assert config.sentinel_master_name == "mymaster"


class TestRedisMetrics:
    """Tests for RedisMetrics dataclass."""

    def test_initial_values(self):
        """Test initial metric values are zero."""
        metrics = RedisMetrics()
        assert metrics.operations_total == 0
        assert metrics.operations_success == 0
        assert metrics.operations_failed == 0
        assert metrics.retries_total == 0
        assert metrics.latency_sum_ms == 0.0
        assert metrics.latency_max_ms == 0.0

    def test_record_operation_success(self):
        """Test recording successful operation."""
        metrics = RedisMetrics()
        metrics.record_operation("stash", 10.5, success=True)
        assert metrics.operations_total == 1
        assert metrics.operations_success == 1
        assert metrics.operations_failed == 0
        assert metrics.latency_sum_ms == 10.5
        assert metrics.stash_count == 1

    def test_record_operation_failure(self):
        """Test recording failed operation."""
        metrics = RedisMetrics()
        metrics.record_operation("retrieve", 5.0, success=False)
        assert metrics.operations_total == 1
        assert metrics.operations_success == 0
        assert metrics.operations_failed == 1
        assert metrics.retrieve_count == 1

    def test_latency_avg_calculation(self):
        """Test average latency calculation."""
        metrics = RedisMetrics()
        metrics.record_operation("stash", 10.0)
        metrics.record_operation("stash", 20.0)
        assert metrics.latency_avg_ms == 15.0

    def test_latency_avg_zero_operations(self):
        """Test average latency with no operations."""
        metrics = RedisMetrics()
        assert metrics.latency_avg_ms == 0.0

    def test_latency_max_tracking(self):
        """Test max latency tracking."""
        metrics = RedisMetrics()
        metrics.record_operation("stash", 10.0)
        metrics.record_operation("stash", 50.0)
        metrics.record_operation("stash", 30.0)
        assert metrics.latency_max_ms == 50.0

    def test_success_rate_all_success(self):
        """Test success rate with all successful ops."""
        metrics = RedisMetrics()
        for _ in range(10):
            metrics.record_operation("stash", 5.0, success=True)
        assert metrics.success_rate == 100.0

    def test_success_rate_mixed(self):
        """Test success rate with mixed results."""
        metrics = RedisMetrics()
        for _ in range(7):
            metrics.record_operation("stash", 5.0, success=True)
        for _ in range(3):
            metrics.record_operation("stash", 5.0, success=False)
        assert metrics.success_rate == 70.0

    def test_success_rate_no_operations(self):
        """Test success rate with no operations returns 100%."""
        metrics = RedisMetrics()
        assert metrics.success_rate == 100.0

    def test_to_dict(self):
        """Test metrics serialization."""
        metrics = RedisMetrics()
        metrics.record_operation("stash", 10.0)
        metrics.record_operation("retrieve", 20.0)
        data = metrics.to_dict()
        assert data["operations_total"] == 2
        assert data["latency_avg_ms"] == 15.0
        assert data["by_operation"]["stash"] == 1
        assert data["by_operation"]["retrieve"] == 1

    def test_operation_type_tracking(self):
        """Test different operation types are tracked."""
        metrics = RedisMetrics()
        metrics.record_operation("stash", 1.0)
        metrics.record_operation("retrieve", 1.0)
        metrics.record_operation("publish", 1.0)
        metrics.record_operation("stream_append", 1.0)
        assert metrics.stash_count == 1
        assert metrics.retrieve_count == 1
        assert metrics.publish_count == 1
        assert metrics.stream_append_count == 1


class TestAgentCredentials:
    """Tests for AgentCredentials dataclass."""

    def test_basic_creation(self):
        """Test basic credential creation."""
        creds = AgentCredentials("agent_001", AccessTier.CONTRIBUTOR)
        assert creds.agent_id == "agent_001"
        assert creds.tier == AccessTier.CONTRIBUTOR
        assert creds.roles == []

    def test_with_roles(self):
        """Test credentials with roles."""
        creds = AgentCredentials(
            "agent_001", AccessTier.VALIDATOR, roles=["code_review", "security"]
        )
        assert len(creds.roles) == 2
        assert "code_review" in creds.roles

    def test_observer_permissions(self):
        """Test OBSERVER tier permissions."""
        creds = AgentCredentials("observer", AccessTier.OBSERVER)
        assert creds.can_read() is True
        assert creds.can_stage() is False
        assert creds.can_validate() is False
        assert creds.can_administer() is False

    def test_contributor_permissions(self):
        """Test CONTRIBUTOR tier permissions."""
        creds = AgentCredentials("contributor", AccessTier.CONTRIBUTOR)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is False
        assert creds.can_administer() is False

    def test_validator_permissions(self):
        """Test VALIDATOR tier permissions."""
        creds = AgentCredentials("validator", AccessTier.VALIDATOR)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is True
        assert creds.can_administer() is False

    def test_steward_permissions(self):
        """Test STEWARD tier has all permissions."""
        creds = AgentCredentials("steward", AccessTier.STEWARD)
        assert creds.can_read() is True
        assert creds.can_stage() is True
        assert creds.can_validate() is True
        assert creds.can_administer() is True

    def test_created_at_defaults_to_now(self):
        """Test created_at defaults to current time."""
        before = datetime.now()
        creds = AgentCredentials("agent", AccessTier.OBSERVER)
        after = datetime.now()
        assert before <= creds.created_at <= after


class TestStagedPattern:
    """Tests for StagedPattern dataclass."""

    def test_basic_creation(self):
        """Test basic staged pattern creation."""
        pattern = StagedPattern(
            pattern_id="pat_001",
            agent_id="agent_001",
            pattern_type="coding",
            name="Error Handling",
            description="Standard error handling pattern",
        )
        assert pattern.pattern_id == "pat_001"
        assert pattern.agent_id == "agent_001"
        assert pattern.confidence == 0.5  # Default

    def test_with_code(self):
        """Test pattern with code snippet."""
        pattern = StagedPattern(
            pattern_id="pat_002",
            agent_id="agent_002",
            pattern_type="coding",
            name="Retry Logic",
            description="Exponential backoff retry",
            code="def retry(fn): pass",
        )
        assert pattern.code == "def retry(fn): pass"

    def test_to_dict(self):
        """Test serialization to dictionary."""
        pattern = StagedPattern(
            pattern_id="pat_001",
            agent_id="agent_001",
            pattern_type="coding",
            name="Test Pattern",
            description="A test pattern",
            confidence=0.8,
            interests=["performance", "reliability"],
        )
        data = pattern.to_dict()
        assert data["pattern_id"] == "pat_001"
        assert data["confidence"] == 0.8
        assert data["interests"] == ["performance", "reliability"]
        assert "staged_at" in data

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "pattern_id": "pat_003",
            "agent_id": "agent_003",
            "pattern_type": "security",
            "name": "Input Validation",
            "description": "Validate all inputs",
            "code": "def validate(x): pass",
            "context": {"source": "review"},
            "confidence": 0.9,
            "staged_at": "2025-01-15T10:30:00",
            "interests": ["security", "compliance"],
        }
        pattern = StagedPattern.from_dict(data)
        assert pattern.pattern_id == "pat_003"
        assert pattern.pattern_type == "security"
        assert pattern.confidence == 0.9
        assert pattern.code == "def validate(x): pass"
        assert pattern.interests == ["security", "compliance"]

    def test_roundtrip_serialization(self):
        """Test to_dict followed by from_dict preserves data."""
        original = StagedPattern(
            pattern_id="pat_rt",
            agent_id="agent_rt",
            pattern_type="refactoring",
            name="Extract Method",
            description="Extract complex logic to methods",
            code="# extract method pattern",
            context={"location": "core.py"},
            confidence=0.75,
            interests=["maintainability"],
        )
        restored = StagedPattern.from_dict(original.to_dict())
        assert restored.pattern_id == original.pattern_id
        assert restored.name == original.name
        assert restored.code == original.code
        assert restored.confidence == original.confidence


class TestConflictContext:
    """Tests for ConflictContext dataclass."""

    def test_basic_creation(self):
        """Test basic conflict context creation."""
        conflict = ConflictContext(
            conflict_id="conf_001",
            positions={"agent_a": "use_cache", "agent_b": "no_cache"},
            interests={"agent_a": ["performance"], "agent_b": ["freshness"]},
        )
        assert conflict.conflict_id == "conf_001"
        assert conflict.resolved is False
        assert conflict.resolution is None

    def test_with_batna(self):
        """Test conflict with BATNA set."""
        conflict = ConflictContext(
            conflict_id="conf_002",
            positions={"agent_a": "approach_1"},
            interests={"agent_a": ["speed"]},
            batna="fallback_to_defaults",
        )
        assert conflict.batna == "fallback_to_defaults"

    def test_to_dict(self):
        """Test serialization."""
        conflict = ConflictContext(
            conflict_id="conf_003",
            positions={"a": "x", "b": "y"},
            interests={"a": ["goal1"], "b": ["goal2"]},
            resolved=True,
            resolution="compromise",
        )
        data = conflict.to_dict()
        assert data["conflict_id"] == "conf_003"
        assert data["resolved"] is True
        assert data["resolution"] == "compromise"

    def test_from_dict(self):
        """Test deserialization."""
        data = {
            "conflict_id": "conf_004",
            "positions": {"x": "pos_x"},
            "interests": {"x": ["int_x"]},
            "batna": "escalate",
            "created_at": "2025-01-15T12:00:00",
            "resolved": False,
        }
        conflict = ConflictContext.from_dict(data)
        assert conflict.conflict_id == "conf_004"
        assert conflict.batna == "escalate"
        assert conflict.resolved is False


class TestTimeWindowQuery:
    """Tests for TimeWindowQuery dataclass."""

    def test_default_values(self):
        """Test default query values."""
        query = TimeWindowQuery()
        assert query.start_time is None
        assert query.end_time is None
        assert query.limit == 100
        assert query.offset == 0

    def test_start_score_none(self):
        """Test start_score with no start_time."""
        query = TimeWindowQuery()
        assert query.start_score == float("-inf")

    def test_end_score_none(self):
        """Test end_score with no end_time."""
        query = TimeWindowQuery()
        assert query.end_score == float("+inf")

    def test_start_score_with_time(self):
        """Test start_score with start_time set."""
        dt = datetime(2025, 1, 15, 12, 0, 0)
        query = TimeWindowQuery(start_time=dt)
        assert query.start_score == dt.timestamp()

    def test_end_score_with_time(self):
        """Test end_score with end_time set."""
        dt = datetime(2025, 1, 15, 18, 0, 0)
        query = TimeWindowQuery(end_time=dt)
        assert query.end_score == dt.timestamp()


class TestPaginatedResult:
    """Tests for PaginatedResult dataclass."""

    def test_basic_creation(self):
        """Test basic paginated result."""
        result = PaginatedResult(
            items=["a", "b", "c"], cursor="next_cursor", has_more=True, total_scanned=10
        )
        assert len(result.items) == 3
        assert result.cursor == "next_cursor"
        assert result.has_more is True
        assert result.total_scanned == 10

    def test_empty_result(self):
        """Test empty paginated result."""
        result = PaginatedResult(items=[], cursor="0", has_more=False)
        assert len(result.items) == 0
        assert result.has_more is False


class TestRedisShortTermMemory:
    """Tests for RedisShortTermMemory class."""

    def test_init_with_mock(self):
        """Test initialization with mock mode."""
        memory = RedisShortTermMemory(use_mock=True)
        assert memory.use_mock is True
        assert memory._client is None

    def test_init_with_config(self):
        """Test initialization with RedisConfig."""
        config = RedisConfig(host="test.redis.io", port=6380, use_mock=True)
        memory = RedisShortTermMemory(config=config)
        assert memory._config.host == "test.redis.io"
        assert memory._config.port == 6380
        assert memory.use_mock is True

    def test_key_prefixes_defined(self):
        """Test all key prefixes are defined."""
        assert RedisShortTermMemory.PREFIX_WORKING == "empathy:working:"
        assert RedisShortTermMemory.PREFIX_STAGED == "empathy:staged:"
        assert RedisShortTermMemory.PREFIX_CONFLICT == "empathy:conflict:"
        assert RedisShortTermMemory.PREFIX_COORDINATION == "empathy:coord:"
        assert RedisShortTermMemory.PREFIX_SESSION == "empathy:session:"
        assert RedisShortTermMemory.PREFIX_PUBSUB == "empathy:pubsub:"
        assert RedisShortTermMemory.PREFIX_STREAM == "empathy:stream:"
        assert RedisShortTermMemory.PREFIX_TIMELINE == "empathy:timeline:"
        assert RedisShortTermMemory.PREFIX_QUEUE == "empathy:queue:"

    def test_metrics_initialized(self):
        """Test metrics are initialized on creation."""
        memory = RedisShortTermMemory(use_mock=True)
        assert memory._metrics is not None
        assert isinstance(memory._metrics, RedisMetrics)
        assert memory._metrics.operations_total == 0

    def test_stash_and_retrieve_mock(self):
        """Test stash and retrieve operations in mock mode."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Stash data
        memory.stash("test_key", {"value": 42}, creds)

        # Retrieve data
        result = memory.retrieve("test_key", creds)
        assert result is not None
        assert result["value"] == 42

    def test_retrieve_nonexistent_key(self):
        """Test retrieving a key that doesn't exist."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.OBSERVER)

        result = memory.retrieve("nonexistent_key", creds)
        assert result is None

    def test_stash_with_ttl(self):
        """Test stash with TTL strategy."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # TTL should be passed as the enum, not the value
        memory.stash("expiring_key", {"data": "temp"}, creds, ttl=TTLStrategy.COORDINATION)
        result = memory.retrieve("expiring_key", creds)
        assert result is not None

    def test_observer_cannot_stash(self):
        """Test OBSERVER tier cannot stash data."""
        RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("observer", AccessTier.OBSERVER)

        # Observer should not be able to stage
        assert creds.can_stage() is False

    def test_stash_batch_mock(self):
        """Test batch stash in mock mode."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        items = [
            ("key1", {"data": 1}),
            ("key2", {"data": 2}),
            ("key3", {"data": 3}),
        ]
        memory.stash_batch(items, creds)

        # Verify all items were stored
        assert memory.retrieve("key1", creds)["data"] == 1
        assert memory.retrieve("key2", creds)["data"] == 2
        assert memory.retrieve("key3", creds)["data"] == 3

    def test_delete_mock(self):
        """Test delete operation in mock mode."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.STEWARD)

        memory.stash("to_delete", {"value": "temp"}, creds)
        assert memory.retrieve("to_delete", creds) is not None

        # Use internal _delete method (delete not exposed publicly)
        # Key format is: PREFIX_WORKING + agent_id + ":" + key
        full_key = f"{RedisShortTermMemory.PREFIX_WORKING}{creds.agent_id}:to_delete"
        memory._delete(full_key)
        assert memory.retrieve("to_delete", creds) is None

    def test_mock_storage_isolation(self):
        """Test that mock storage is instance-specific."""
        memory1 = RedisShortTermMemory(use_mock=True)
        memory2 = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("agent", AccessTier.CONTRIBUTOR)

        memory1.stash("key", {"from": "memory1"}, creds)

        # memory2 should not see memory1's data
        assert memory2.retrieve("key", creds) is None


class TestRedisShortTermMemoryPatterns:
    """Tests for pattern staging operations."""

    def test_stage_pattern(self):
        """Test staging a pattern."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("contributor", AccessTier.CONTRIBUTOR)

        pattern = StagedPattern(
            pattern_id="pat_test",
            agent_id="contributor",
            pattern_type="coding",
            name="Test Pattern",
            description="A test pattern for staging",
        )

        memory.stage_pattern(pattern, creds)
        # Pattern should be retrievable
        staged = memory.get_staged_pattern("pat_test", creds)
        assert staged is not None
        assert staged.name == "Test Pattern"

    def test_list_staged_patterns(self):
        """Test listing all staged patterns."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("contributor", AccessTier.CONTRIBUTOR)

        for i in range(3):
            pattern = StagedPattern(
                pattern_id=f"pat_{i}",
                agent_id="contributor",
                pattern_type="coding",
                name=f"Pattern {i}",
                description=f"Description {i}",
            )
            memory.stage_pattern(pattern, creds)

        patterns = memory.list_staged_patterns(creds)
        assert len(patterns) >= 3


class TestRedisShortTermMemoryConflicts:
    """Tests for conflict context operations."""

    def test_create_conflict_via_stash(self):
        """Test creating a conflict context via stash."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("validator", AccessTier.VALIDATOR)

        conflict = ConflictContext(
            conflict_id="conf_test",
            positions={"agent_a": "option_1", "agent_b": "option_2"},
            interests={"agent_a": ["speed"], "agent_b": ["safety"]},
        )

        # Store conflict data via stash using conflict prefix
        key = f"conflict:{conflict.conflict_id}"
        memory.stash(key, conflict.to_dict(), creds, ttl=TTLStrategy.CONFLICT_CONTEXT)

        # Retrieve and verify
        retrieved_data = memory.retrieve(key, creds)
        assert retrieved_data is not None
        assert retrieved_data["positions"]["agent_a"] == "option_1"

    def test_resolve_conflict_pattern(self):
        """Test conflict resolution pattern via stash/retrieve."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("steward", AccessTier.STEWARD)

        conflict = ConflictContext(
            conflict_id="conf_resolve",
            positions={"a": "x"},
            interests={"a": ["y"]},
        )

        # Store initial conflict
        key = f"conflict:{conflict.conflict_id}"
        memory.stash(key, conflict.to_dict(), creds, ttl=TTLStrategy.CONFLICT_CONTEXT)

        # Resolve conflict by updating the stored data
        resolved_data = memory.retrieve(key, creds)
        resolved_data["resolved"] = True
        resolved_data["resolution"] = "agreed_solution"
        memory.stash(key, resolved_data, creds, ttl=TTLStrategy.CONFLICT_CONTEXT)

        # Verify resolution
        final_data = memory.retrieve(key, creds)
        assert final_data["resolved"] is True
        assert final_data["resolution"] == "agreed_solution"
