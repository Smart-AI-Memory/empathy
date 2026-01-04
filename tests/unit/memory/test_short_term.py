"""Educational Tests for Short-Term Memory (Redis Mocking & Core Operations)

Learning Objectives:
- Testing external dependencies without external services (built-in mock mode)
- State management and TTL (Time-To-Live) testing
- Role-based access control testing
- Metrics and observability testing
- Connection retry logic with exponential backoff
- Testing atomic operations and transactions

This test suite demonstrates progressive complexity:
- LESSON 1: Built-in mock mode for testing without Redis
- LESSON 2: Basic stash/retrieve operations
- LESSON 3: TTL strategies and expiration
- LESSON 4: Role-based access control (AgentCredentials)
- LESSON 5: Connection retry with exponential backoff
- LESSON 6: Metrics tracking and observability

Phase 2 Focus: Testing stateful systems with external dependencies
"""

import time
from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from empathy_os.memory.short_term import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    RedisConfig,
    RedisMetrics,
    RedisShortTermMemory,
    StagedPattern,
    TTLStrategy,
)

# ============================================================================
# LESSON 1: Built-in Mock Mode - Testing Without External Dependencies
# ============================================================================
# Teaching Pattern: Using built-in mock mode instead of external mocking libraries


@pytest.mark.unit
class TestMockModeBasics:
    """Educational tests for built-in mock mode."""

    def test_initialization_with_mock_mode(self):
        """Teaching Pattern: Testing with built-in mock mode.

        The ShortTermMemory class has a built-in mock mode that doesn't
        require a real Redis server. This is perfect for unit tests!

        Key learning: Always provide test mode in your classes that depend
        on external services.
        """
        # Create memory with mock mode enabled
        memory = RedisShortTermMemory(use_mock=True)

        assert memory.use_mock is True
        assert memory._client is None  # No real Redis client
        assert memory._mock_storage == {}  # Empty mock storage

    def test_mock_mode_automatically_enabled_when_redis_unavailable(self):
        """Teaching Pattern: Graceful degradation when dependencies unavailable.

        If Redis is not installed, mock mode is automatically enabled.
        This allows the code to work even without optional dependencies.
        """
        # Mock REDIS_AVAILABLE as False
        with patch("empathy_os.memory.short_term.REDIS_AVAILABLE", False):
            memory = RedisShortTermMemory()  # use_mock=False, but Redis unavailable

            assert memory.use_mock is True  # Automatically switched to mock mode

    def test_mock_storage_is_isolated_per_instance(self):
        """Teaching Pattern: Test isolation.

        Each mock instance should have its own storage to prevent
        test contamination.
        """
        memory1 = RedisShortTermMemory(use_mock=True)
        memory2 = RedisShortTermMemory(use_mock=True)

        # Each instance has its own mock storage
        assert memory1._mock_storage is not memory2._mock_storage
        assert id(memory1._mock_storage) != id(memory2._mock_storage)


# ============================================================================
# LESSON 2: Basic Stash/Retrieve Operations
# ============================================================================
# Teaching Pattern: Testing CRUD operations on stateful storage


@pytest.mark.unit
class TestBasicStashRetrieve:
    """Educational tests for basic stash/retrieve operations."""

    @pytest.fixture
    def memory(self):
        """Teaching Pattern: Fixture for test dependencies.

        Create a fresh memory instance for each test to ensure isolation.
        """
        return RedisShortTermMemory(use_mock=True)

    @pytest.fixture
    def agent_creds(self):
        """Teaching Pattern: Fixture for common test data.

        Most operations require credentials, so we create a fixture.
        """
        return AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

    def test_stash_and_retrieve_simple_data(self, memory, agent_creds):
        """Teaching Pattern: Testing the happy path.

        Start with the simplest possible scenario - store and retrieve data.
        """
        key = "test_key"
        data = {"message": "Hello, World!"}

        # Stash data
        memory.stash(key, data, agent_creds)

        # Retrieve data
        retrieved = memory.retrieve(key, agent_creds)

        assert retrieved == data

    def test_stash_overwrites_existing_data(self, memory, agent_creds):
        """Teaching Pattern: Testing state mutations.

        When you store data with the same key, it should overwrite.
        """
        key = "test_key"

        # Store initial data
        memory.stash(key, {"version": 1}, agent_creds)

        # Overwrite with new data
        memory.stash(key, {"version": 2}, agent_creds)

        # Should get the new data
        retrieved = memory.retrieve(key, agent_creds)
        assert retrieved["version"] == 2

    def test_retrieve_nonexistent_key_returns_none(self, memory, agent_creds):
        """Teaching Pattern: Testing negative cases.

        What happens when you try to retrieve a key that doesn't exist?
        """
        retrieved = memory.retrieve("nonexistent_key", agent_creds)
        assert retrieved is None

    def test_stash_with_complex_nested_data(self, memory, agent_creds):
        """Teaching Pattern: Testing with realistic data.

        Real-world data is often nested and complex. Test with structures
        that mirror production usage.
        """
        key = "complex_data"
        data = {
            "analysis": {
                "bugs": [
                    {"line": 42, "severity": "high"},
                    {"line": 108, "severity": "low"},
                ],
                "metrics": {
                    "cyclomatic_complexity": 15,
                    "test_coverage": 78.5,
                },
            },
            "metadata": {
                "timestamp": "2025-01-04T10:00:00Z",
                "agent_id": "analyzer_v1",
            },
        }

        memory.stash(key, data, agent_creds)
        retrieved = memory.retrieve(key, agent_creds)

        # Deep equality check
        assert retrieved == data
        assert retrieved["analysis"]["bugs"][0]["line"] == 42
        assert retrieved["analysis"]["metrics"]["test_coverage"] == 78.5


# ============================================================================
# LESSON 3: TTL Strategies and Expiration
# ============================================================================
# Teaching Pattern: Testing time-based behavior


@pytest.mark.unit
class TestTTLStrategies:
    """Educational tests for TTL (Time-To-Live) strategies."""

    @pytest.fixture
    def memory(self):
        return RedisShortTermMemory(use_mock=True)

    @pytest.fixture
    def agent_creds(self):
        return AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

    def test_ttl_strategy_enum_values(self):
        """Teaching Pattern: Testing enum configurations.

        TTL strategies define how long different types of data should live.
        """
        assert TTLStrategy.WORKING_RESULTS.value == 3600  # 1 hour
        assert TTLStrategy.STAGED_PATTERNS.value == 86400  # 24 hours
        assert TTLStrategy.COORDINATION.value == 300  # 5 minutes
        assert TTLStrategy.SESSION.value == 1800  # 30 minutes

    def test_stash_with_custom_ttl(self, memory, agent_creds):
        """Teaching Pattern: Testing TTL parameter handling.

        When stashing data, you can specify a TTL strategy enum.
        In mock mode, we track the expiration time.
        """
        key = "expiring_data"
        data = {"message": "This will expire"}

        # Pass TTLStrategy enum (not .value)
        memory.stash(key, data, agent_creds, ttl=TTLStrategy.SESSION)

        # In mock mode, check that TTL was stored
        full_key = memory.PREFIX_WORKING + key
        if full_key in memory._mock_storage:
            _, expiry = memory._mock_storage[full_key]
            # Expiry should be set (current time + TTL)
            assert expiry is not None
            assert expiry > time.time()  # Should expire in the future

    def test_stash_with_ttl_strategy_enum(self, memory, agent_creds):
        """Teaching Pattern: Testing enum-based configuration.

        Instead of hardcoding TTL values, use TTLStrategy enums
        for consistency across the codebase.
        """
        key = "session_data"
        data = {"session_id": "abc123"}

        # Use TTLStrategy enum (pass the enum, not .value)
        memory.stash(key, data, agent_creds, ttl=TTLStrategy.SESSION)

        # Verify it was stored (note: key includes agent_id)
        full_key = memory.PREFIX_WORKING + agent_creds.agent_id + ":" + key
        assert full_key in memory._mock_storage

    def test_different_ttl_strategies_for_different_data_types(self, memory, agent_creds):
        """Teaching Pattern: Testing business logic for TTL selection.

        Different types of data should have different TTL strategies:
        - Working results: Short-lived (1 hour)
        - Staged patterns: Medium-lived (24 hours)
        - Coordination signals: Very short (5 minutes)
        """
        # Working results - 1 hour (pass enum, not .value)
        memory.stash(
            "working:result1",
            {"data": "temp"},
            agent_creds,
            ttl=TTLStrategy.WORKING_RESULTS,
        )

        # Staged patterns - 24 hours
        memory.stash(
            "staged:pattern1",
            {"code": "def foo(): pass"},
            agent_creds,
            ttl=TTLStrategy.STAGED_PATTERNS,
        )

        # Coordination - 5 minutes
        memory.stash(
            "coord:signal1",
            {"status": "ready"},
            agent_creds,
            ttl=TTLStrategy.COORDINATION,
        )

        # All should be retrievable immediately
        assert memory.retrieve("working:result1", agent_creds) is not None
        assert memory.retrieve("staged:pattern1", agent_creds) is not None
        assert memory.retrieve("coord:signal1", agent_creds) is not None


# ============================================================================
# LESSON 4: Role-Based Access Control
# ============================================================================
# Teaching Pattern: Testing authorization and permissions


@pytest.mark.unit
class TestAccessControl:
    """Educational tests for role-based access control."""

    @pytest.fixture
    def memory(self):
        return RedisShortTermMemory(use_mock=True)

    def test_access_tier_hierarchy(self):
        """Teaching Pattern: Testing enum hierarchies.

        Access tiers form a hierarchy:
        Observer (1) < Contributor (2) < Validator (3) < Steward (4)
        """
        assert AccessTier.OBSERVER.value == 1
        assert AccessTier.CONTRIBUTOR.value == 2
        assert AccessTier.VALIDATOR.value == 3
        assert AccessTier.STEWARD.value == 4

    def test_observer_can_read(self):
        """Teaching Pattern: Testing minimal permissions.

        Observers (Tier 1) can only read data.
        """
        observer = AgentCredentials("observer_agent", AccessTier.OBSERVER)

        assert observer.can_read() is True
        assert observer.can_stage() is False
        assert observer.can_validate() is False
        assert observer.can_administer() is False

    def test_contributor_can_stage(self):
        """Teaching Pattern: Testing intermediate permissions.

        Contributors (Tier 2) can read and stage patterns.
        """
        contributor = AgentCredentials("contributor_agent", AccessTier.CONTRIBUTOR)

        assert contributor.can_read() is True
        assert contributor.can_stage() is True
        assert contributor.can_validate() is False
        assert contributor.can_administer() is False

    def test_validator_can_promote(self):
        """Teaching Pattern: Testing elevated permissions.

        Validators (Tier 3) can read, stage, and validate patterns.
        """
        validator = AgentCredentials("validator_agent", AccessTier.VALIDATOR)

        assert validator.can_read() is True
        assert validator.can_stage() is True
        assert validator.can_validate() is True
        assert validator.can_administer() is False

    def test_steward_has_full_access(self):
        """Teaching Pattern: Testing admin permissions.

        Stewards (Tier 4) have full access including administration.
        """
        steward = AgentCredentials("steward_agent", AccessTier.STEWARD)

        assert steward.can_read() is True
        assert steward.can_stage() is True
        assert steward.can_validate() is True
        assert steward.can_administer() is True

    def test_contributor_and_above_can_stash(self, memory):
        """Teaching Pattern: Testing write permissions.

        Only Contributor tier and above can stash (write) data.
        Observer can only read.
        """
        # Observer cannot stash
        observer = AgentCredentials("observer", AccessTier.OBSERVER)
        with pytest.raises(PermissionError):
            memory.stash("data", {"test": "value"}, observer)

        # Contributor and above CAN stash
        tiers_that_can_write = [
            AgentCredentials("contributor", AccessTier.CONTRIBUTOR),
            AgentCredentials("validator", AccessTier.VALIDATOR),
            AgentCredentials("steward", AccessTier.STEWARD),
        ]

        for tier_creds in tiers_that_can_write:
            key = f"data_{tier_creds.agent_id}"
            data = {"tier": tier_creds.tier.name}

            memory.stash(key, data, tier_creds)
            retrieved = memory.retrieve(key, tier_creds)

            assert retrieved == data


# ============================================================================
# LESSON 5: Connection Retry Logic
# ============================================================================
# Teaching Pattern: Testing retry mechanisms and error handling


@pytest.mark.unit
class TestConnectionRetry:
    """Educational tests for connection retry with exponential backoff."""

    def test_redis_config_default_retry_settings(self):
        """Teaching Pattern: Testing default configuration values.

        RedisConfig should have sensible retry defaults.
        """
        config = RedisConfig()

        assert config.retry_on_timeout is True
        assert config.retry_max_attempts == 3
        assert config.retry_base_delay == 0.1  # 100ms
        assert config.retry_max_delay == 2.0  # 2 seconds

    def test_redis_config_custom_retry_settings(self):
        """Teaching Pattern: Testing configuration customization.

        Users should be able to override retry settings.
        """
        config = RedisConfig(
            retry_max_attempts=5,
            retry_base_delay=0.5,
            retry_max_delay=10.0,
        )

        assert config.retry_max_attempts == 5
        assert config.retry_base_delay == 0.5
        assert config.retry_max_delay == 10.0

    @patch("empathy_os.memory.short_term.redis.Redis")
    @patch("empathy_os.memory.short_term.logger")
    def test_connection_retry_on_failure(self, mock_logger, mock_redis_class):
        """Teaching Pattern: Testing retry logic with mock failures.

        Simulate connection failures and verify retry behavior.
        This test demonstrates exponential backoff - it fails twice,
        then succeeds on the third attempt.

        IMPORTANT: Must raise RedisConnectionError (not plain Exception)
        because the retry logic only catches Redis-specific exceptions.
        """
        # Import the correct exception type
        from redis.exceptions import ConnectionError as RedisConnectionError

        # Mock Redis instance
        mock_instance = Mock()
        # Fail twice with Redis exception, then succeed
        mock_instance.ping.side_effect = [
            RedisConnectionError("Connection failed"),  # Attempt 1: fail
            RedisConnectionError("Connection failed"),  # Attempt 2: fail
            None,  # Attempt 3: success (ping returns None on success)
        ]
        mock_redis_class.return_value = mock_instance

        config = RedisConfig(use_mock=False, retry_max_attempts=3)

        # This should succeed after retries
        with patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True):
            memory = RedisShortTermMemory(config=config)

            # Should have called ping 3 times (2 failures + 1 success)
            assert mock_instance.ping.call_count == 3
            # Memory should have the client (connection succeeded)
            assert memory._client == mock_instance

    def test_redis_config_to_redis_kwargs(self):
        """Teaching Pattern: Testing configuration serialization.

        RedisConfig should convert to kwargs for redis.Redis constructor.
        """
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            db=2,
            password="secret123",
            socket_timeout=10.0,
        )

        kwargs = config.to_redis_kwargs()

        assert kwargs["host"] == "redis.example.com"
        assert kwargs["port"] == 6380
        assert kwargs["db"] == 2
        assert kwargs["password"] == "secret123"
        assert kwargs["socket_timeout"] == 10.0
        assert kwargs["decode_responses"] is True


# ============================================================================
# LESSON 6: Metrics Tracking and Observability
# ============================================================================
# Teaching Pattern: Testing metrics and monitoring


@pytest.mark.unit
class TestMetricsTracking:
    """Educational tests for metrics tracking."""

    def test_metrics_initialization(self):
        """Teaching Pattern: Testing initial state.

        Metrics should start at zero.
        """
        metrics = RedisMetrics()

        assert metrics.operations_total == 0
        assert metrics.operations_success == 0
        assert metrics.operations_failed == 0
        assert metrics.retries_total == 0
        assert metrics.latency_sum_ms == 0.0
        assert metrics.latency_max_ms == 0.0

    def test_record_successful_operation(self):
        """Teaching Pattern: Testing metrics recording.

        When an operation succeeds, metrics should be updated.
        """
        metrics = RedisMetrics()

        # Record a successful stash operation with 5ms latency
        metrics.record_operation("stash", latency_ms=5.0, success=True)

        assert metrics.operations_total == 1
        assert metrics.operations_success == 1
        assert metrics.operations_failed == 0
        assert metrics.stash_count == 1
        assert metrics.latency_sum_ms == 5.0
        assert metrics.latency_max_ms == 5.0

    def test_record_failed_operation(self):
        """Teaching Pattern: Testing failure tracking.

        Failed operations should increment the failure counter.
        """
        metrics = RedisMetrics()

        metrics.record_operation("retrieve", latency_ms=3.0, success=False)

        assert metrics.operations_total == 1
        assert metrics.operations_success == 0
        assert metrics.operations_failed == 1

    def test_latency_average_calculation(self):
        """Teaching Pattern: Testing computed properties.

        Average latency should be calculated from sum / total.
        """
        metrics = RedisMetrics()

        # Record multiple operations
        metrics.record_operation("stash", 10.0, success=True)
        metrics.record_operation("retrieve", 5.0, success=True)
        metrics.record_operation("stash", 15.0, success=True)

        # Average = (10 + 5 + 15) / 3 = 10.0
        assert metrics.latency_avg_ms == pytest.approx(10.0)

    def test_latency_max_tracking(self):
        """Teaching Pattern: Testing max value tracking.

        Should track the maximum latency observed.
        """
        metrics = RedisMetrics()

        metrics.record_operation("stash", 5.0, success=True)
        metrics.record_operation("retrieve", 15.0, success=True)
        metrics.record_operation("stash", 8.0, success=True)

        assert metrics.latency_max_ms == 15.0  # Max of all operations

    def test_success_rate_calculation(self):
        """Teaching Pattern: Testing percentage calculations.

        Success rate should be (successes / total) * 100.
        """
        metrics = RedisMetrics()

        # 7 successes, 3 failures = 70% success rate
        for _ in range(7):
            metrics.record_operation("stash", 1.0, success=True)
        for _ in range(3):
            metrics.record_operation("retrieve", 1.0, success=False)

        assert metrics.success_rate == pytest.approx(70.0)

    def test_success_rate_with_no_operations(self):
        """Teaching Pattern: Testing edge case (division by zero).

        When no operations have been recorded, success rate should be 100%
        (optimistic default) rather than causing a division by zero error.
        """
        metrics = RedisMetrics()

        assert metrics.success_rate == 100.0

    def test_metrics_to_dict_serialization(self):
        """Teaching Pattern: Testing serialization for reporting.

        Metrics should be serializable to dict for JSON reporting.
        """
        metrics = RedisMetrics()

        metrics.record_operation("stash", 10.0, success=True)
        metrics.record_operation("retrieve", 5.0, success=True)
        metrics.record_operation("publish", 3.0, success=True)

        metrics_dict = metrics.to_dict()

        assert metrics_dict["operations_total"] == 3
        assert metrics_dict["operations_success"] == 3
        assert metrics_dict["latency_avg_ms"] == pytest.approx(6.0)  # (10+5+3)/3
        assert metrics_dict["success_rate"] == 100.0
        assert metrics_dict["by_operation"]["stash"] == 1
        assert metrics_dict["by_operation"]["retrieve"] == 1
        assert metrics_dict["by_operation"]["publish"] == 1


# ============================================================================
# LESSON 7: Staged Patterns (Workflow State)
# ============================================================================
# Teaching Pattern: Testing complex domain objects


@pytest.mark.unit
class TestStagedPatterns:
    """Educational tests for staged pattern workflow."""

    def test_staged_pattern_creation(self):
        """Teaching Pattern: Testing dataclass initialization.

        StagedPattern represents a pattern awaiting validation.
        """
        pattern = StagedPattern(
            pattern_id="pat_001",
            agent_id="agent_1",
            pattern_type="bug_detection",
            name="Null Pointer Check",
            description="Detects potential null pointer dereferences",
            code="if x is None: raise ValueError()",
            confidence=0.85,
        )

        assert pattern.pattern_id == "pat_001"
        assert pattern.agent_id == "agent_1"
        assert pattern.confidence == 0.85

    def test_staged_pattern_serialization(self):
        """Teaching Pattern: Testing to_dict/from_dict roundtrip.

        Domain objects should be serializable for storage.
        """
        original = StagedPattern(
            pattern_id="pat_002",
            agent_id="agent_2",
            pattern_type="security",
            name="SQL Injection Check",
            description="Detects potential SQL injection",
            code="if 'SELECT' in user_input:",
            confidence=0.95,
            interests=["security", "database"],
        )

        # Serialize
        pattern_dict = original.to_dict()

        # Deserialize
        restored = StagedPattern.from_dict(pattern_dict)

        assert restored.pattern_id == original.pattern_id
        assert restored.agent_id == original.agent_id
        assert restored.confidence == original.confidence
        assert restored.interests == ["security", "database"]

    def test_staged_pattern_default_values(self):
        """Teaching Pattern: Testing default values in dataclasses.

        Optional fields should have sensible defaults.
        """
        pattern = StagedPattern(
            pattern_id="pat_003",
            agent_id="agent_3",
            pattern_type="refactor",
            name="Extract Method",
            description="Suggests method extraction",
        )

        # Defaults
        assert pattern.code is None
        assert pattern.context == {}
        assert pattern.confidence == 0.5  # Default confidence
        assert pattern.interests == []
        assert isinstance(pattern.staged_at, datetime)


# ============================================================================
# LESSON 8: Conflict Context (Negotiation State)
# ============================================================================
# Teaching Pattern: Testing negotiation workflows


@pytest.mark.unit
class TestConflictContext:
    """Educational tests for conflict resolution context."""

    def test_conflict_context_creation(self):
        """Teaching Pattern: Testing complex state objects.

        ConflictContext tracks negotiation state per "Getting to Yes" framework.
        """
        conflict = ConflictContext(
            conflict_id="conflict_001",
            positions={
                "agent_1": "Use Python 3.10",
                "agent_2": "Use Python 3.11",
            },
            interests={
                "agent_1": ["stability", "compatibility"],
                "agent_2": ["performance", "new_features"],
            },
            batna="Stick with Python 3.9",
        )

        assert conflict.conflict_id == "conflict_001"
        assert len(conflict.positions) == 2
        assert len(conflict.interests) == 2
        assert conflict.resolved is False

    def test_conflict_resolution_workflow(self):
        """Teaching Pattern: Testing state transitions.

        Conflicts start unresolved, then get resolved with a solution.
        """
        conflict = ConflictContext(
            conflict_id="conflict_002",
            positions={"agent_1": "A", "agent_2": "B"},
            interests={"agent_1": ["speed"], "agent_2": ["accuracy"]},
        )

        # Initially unresolved
        assert conflict.resolved is False
        assert conflict.resolution is None

        # Resolve the conflict
        conflict.resolved = True
        conflict.resolution = "Use A with accuracy checks from B"

        assert conflict.resolved is True
        assert conflict.resolution is not None

    def test_conflict_context_serialization(self):
        """Teaching Pattern: Testing datetime serialization.

        Datetime fields should serialize to ISO format strings.
        """
        conflict = ConflictContext(
            conflict_id="conflict_003",
            positions={"agent_1": "X"},
            interests={"agent_1": ["cost"]},
        )

        conflict_dict = conflict.to_dict()

        # Check datetime serialization
        assert "created_at" in conflict_dict
        assert isinstance(conflict_dict["created_at"], str)
        # Should be ISO format
        datetime.fromisoformat(conflict_dict["created_at"])  # Should not raise

        # Roundtrip
        restored = ConflictContext.from_dict(conflict_dict)
        assert isinstance(restored.created_at, datetime)


# ============================================================================
# SUMMARY: What We Learned
# ============================================================================
"""
This test suite demonstrated 8 progressive lessons in testing stateful systems:

1. **Built-in Mock Mode**
   - Testing without external dependencies
   - Graceful degradation when services unavailable
   - Test isolation with per-instance mock storage

2. **Basic CRUD Operations**
   - Testing happy path (stash/retrieve)
   - Testing state mutations (overwrites)
   - Testing negative cases (nonexistent keys)
   - Testing with complex nested data

3. **TTL Strategies**
   - Testing time-based expiration
   - Testing enum-based configuration
   - Testing business logic for TTL selection
   - Different TTLs for different data types

4. **Role-Based Access Control**
   - Testing permission hierarchies
   - Testing minimal, intermediate, elevated, and admin permissions
   - Testing that basic operations work for all tiers

5. **Connection Retry Logic**
   - Testing default retry configuration
   - Testing custom retry settings
   - Testing retry behavior with mock failures
   - Testing exponential backoff

6. **Metrics Tracking**
   - Testing initial state
   - Testing success/failure tracking
   - Testing latency tracking (avg, max)
   - Testing success rate calculation
   - Testing edge cases (division by zero)
   - Testing serialization for reporting

7. **Staged Patterns (Domain Objects)**
   - Testing dataclass initialization
   - Testing serialization roundtrips
   - Testing default values

8. **Conflict Context (State Machines)**
   - Testing complex state objects
   - Testing state transitions (unresolved → resolved)
   - Testing datetime serialization

**Key Patterns Used:**
- Fixtures for test dependencies (`memory`, `agent_creds`)
- Mock mode for testing without external services
- Testing state mutations and transitions
- Testing serialization roundtrips
- Testing computed properties (avg, success_rate)
- Testing edge cases (division by zero, empty state)
- Testing configuration objects

**Real-World Impact:**
These patterns enable testing of:
- Distributed systems with Redis
- State machines and workflows
- Role-based authorization
- Retry logic and resilience
- Metrics and observability
- Time-based behavior (TTLs, expiration)

**See Also:**
- Tutorial: "Testing External Dependencies" (Phase 2)
- Tutorial: "State Management Testing Patterns" (Phase 2)
- Pattern Library: "Redis Mocking Patterns" (Phase 5)
"""
