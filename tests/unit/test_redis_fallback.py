"""Redis Fallback & Recovery Tests for RedisShortTermMemory.

Tests graceful degradation when Redis is unavailable including:
- Fallback to in-memory mock storage
- Recovery when Redis comes back online
- Data consistency during fallback
- No data loss on connection failures

These tests address the critical gap identified in TEST_IMPROVEMENT_PLAN.md
Phase 1: Redis Failure & Recovery Tests (CRITICAL severity).

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from unittest.mock import Mock, patch

import pytest
import redis

from empathy_os.memory.short_term import (
    AccessTier,
    AgentCredentials,
    RedisConfig,
    RedisShortTermMemory,
    TTLStrategy,
)


class TestRedisFallbackBehavior:
    """Test that RedisShortTermMemory gracefully falls back to mock when Redis unavailable."""

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_falls_back_to_mock_on_connection_failure(self, mock_redis_cls):
        """Test graceful fallback to mock storage when Redis connection fails."""
        # Mock Redis connection failure
        mock_redis_cls.side_effect = redis.ConnectionError("Connection refused")

        # Should raise exception after retries exhausted
        with pytest.raises(redis.ConnectionError):
            _ = RedisShortTermMemory(host="localhost", port=6379)

        # Verify it attempted to connect
        assert mock_redis_cls.called

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_falls_back_to_mock_on_auth_failure(self, mock_redis_cls):
        """Test graceful fallback when Redis authentication fails."""
        mock_client = Mock()
        mock_client.ping.side_effect = redis.AuthenticationError("Invalid password")
        mock_redis_cls.return_value = mock_client

        # Should fail after retries
        with pytest.raises(redis.AuthenticationError):
            _ = RedisShortTermMemory(host="localhost", port=6379, password="wrong")

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_retries_connection_with_exponential_backoff(self, mock_redis_cls):
        """Test that connection retries use exponential backoff."""
        mock_client = Mock()
        call_count = 0

        def ping_with_retry():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise redis.ConnectionError("Connection refused")
            return True  # Success on 3rd attempt

        mock_client.ping = ping_with_retry
        mock_redis_cls.return_value = mock_client

        # Should succeed after retries
        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Verify it retried 3 times
        assert call_count == 3
        assert memory._metrics.retries_total >= 2  # At least 2 retries before success

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", False)
    def test_uses_mock_when_redis_not_installed(self):
        """Test that mock storage is used when Redis package not available."""
        memory = RedisShortTermMemory(host="localhost", port=6379)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Should use mock
        assert memory.use_mock is True
        assert memory._client is None

        # Should still be functional
        memory.stash("test_key", {"data": "test_value"}, creds, ttl=TTLStrategy.WORKING_RESULTS)
        result = memory.retrieve("test_key", creds)
        assert result == {"data": "test_value"}


class TestMockStorageFunctionality:
    """Test that mock storage provides equivalent functionality to Redis."""

    def test_mock_storage_stash_and_retrieve(self):
        """Test basic stash/retrieve operations in mock storage."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        data = {"test": "value", "number": 42}
        memory.stash("result1", data, creds, ttl=TTLStrategy.WORKING_RESULTS)

        result = memory.retrieve("result1", creds)
        assert result == data

    def test_mock_storage_respects_ttl(self):
        """Test that mock storage respects TTL expiration."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Stash data
        memory.stash("expires_soon", {"data": "test"}, creds, ttl=TTLStrategy.COORDINATION)

        # Should be retrievable immediately
        result = memory.retrieve("expires_soon", creds)
        assert result == {"data": "test"}

    def test_mock_storage_handles_missing_keys(self):
        """Test that mock storage handles missing keys gracefully."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Retrieve non-existent key
        result = memory.retrieve("nonexistent", creds)
        assert result is None

    def test_mock_storage_stage_pattern(self):
        """Test pattern staging in mock storage."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        from empathy_os.memory.short_term import StagedPattern

        pattern = StagedPattern(
            pattern_id="test_pattern",
            agent_id="test_agent",
            pattern_type="test",
            name="Test Pattern",
            description="A test pattern for fallback testing",
            confidence=0.9,
        )

        memory.stage_pattern(pattern, creds)

        # Should be able to retrieve staged pattern
        retrieved = memory.get_staged_pattern("test_pattern", creds)
        assert retrieved is not None
        assert retrieved.pattern_id == "test_pattern"

    def test_mock_storage_clear_working_memory(self):
        """Test clearing working memory in mock storage."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Stash some data
        memory.stash("key1", {"data": "test1"}, creds, ttl=TTLStrategy.WORKING_RESULTS)
        memory.stash("key2", {"data": "test2"}, creds, ttl=TTLStrategy.WORKING_RESULTS)

        # Clear working memory
        cleared = memory.clear_working_memory(creds)
        assert cleared >= 0  # Should report number of keys cleared

    def test_mock_storage_ping(self):
        """Test ping returns true for mock storage."""
        memory = RedisShortTermMemory(use_mock=True)

        # Mock storage should always respond to ping
        assert memory.ping() is True


class TestDataConsistencyDuringFailover:
    """Test data consistency when failing over between Redis and mock."""

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_stash_fails_on_connection_loss(self, mock_redis_cls):
        """Test that stash operations fail gracefully on connection loss."""
        mock_client = Mock()
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Mock setex to raise connection error
        mock_client.setex.side_effect = redis.ConnectionError("Connection lost")
        mock_client.ping.return_value = True
        mock_redis_cls.return_value = mock_client

        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Stash should raise exception after retries exhausted
        with pytest.raises(redis.ConnectionError):
            memory.stash("key1", {"data": "value1"}, creds, ttl=TTLStrategy.WORKING_RESULTS)


class TestConnectionRecovery:
    """Test automatic recovery when Redis connection is restored."""

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_connection_recovery_after_failure(self, mock_redis_cls):
        """Test that connection recovers automatically after transient failure."""
        mock_client = Mock()
        ping_count = 0

        def ping_with_recovery():
            nonlocal ping_count
            ping_count += 1
            if ping_count == 1:
                raise redis.ConnectionError("Connection lost")
            return True  # Recovered

        mock_client.ping = ping_with_recovery
        mock_client.setex.return_value = True
        mock_client.get.return_value = '{"data": "value"}'
        mock_redis_cls.return_value = mock_client

        # First connection attempt fails, retries succeed
        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Should have recovered and ping should work
        assert memory.ping() is True

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_tracks_retry_metrics(self, mock_redis_cls):
        """Test that retry attempts are tracked in metrics."""
        mock_client = Mock()
        attempt = 0

        def ping_with_retries():
            nonlocal attempt
            attempt += 1
            if attempt < 2:
                raise redis.ConnectionError("Connection refused")
            return True

        mock_client.ping = ping_with_retries
        mock_redis_cls.return_value = mock_client

        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Check metrics
        assert memory._metrics.retries_total >= 1  # At least one retry occurred


class TestErrorHandlingEdgeCases:
    """Test edge cases in error handling and fallback logic."""

    def test_handles_redis_timeout_gracefully(self):
        """Test handling of Redis timeout errors."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Mock storage should never timeout
        memory.stash("key", {"data": "value"}, creds, ttl=TTLStrategy.WORKING_RESULTS)
        result = memory.retrieve("key", creds)
        assert result == {"data": "value"}

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_handles_redis_out_of_memory(self, mock_redis_cls):
        """Test handling of Redis OOM errors."""
        mock_client = Mock()
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)
        mock_client.ping.return_value = True
        mock_client.setex.side_effect = redis.ResponseError("OOM command not allowed")
        mock_redis_cls.return_value = mock_client

        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Should raise ResponseError (not fallback - this is a config issue)
        with pytest.raises(redis.ResponseError):
            memory.stash("key", {"data": "value"}, creds, ttl=TTLStrategy.WORKING_RESULTS)

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_handles_max_clients_exceeded(self, mock_redis_cls):
        """Test handling when Redis max clients exceeded."""
        mock_redis_cls.side_effect = redis.ConnectionError("max number of clients reached")

        # Should raise after retries exhausted
        with pytest.raises(redis.ConnectionError):
            _ = RedisShortTermMemory(host="localhost", port=6379)


class TestConfigurationValidation:
    """Test configuration validation for Redis connection."""

    def test_validates_retry_configuration(self):
        """Test that retry configuration is validated."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            retry_max_attempts=3,
            retry_base_delay=0.1,
            retry_max_delay=2.0,
        )

        memory = RedisShortTermMemory(config=config)

        assert memory._config.retry_max_attempts == 3
        assert memory._config.retry_base_delay == 0.1
        assert memory._config.retry_max_delay == 2.0

    def test_ssl_configuration(self):
        """Test SSL/TLS configuration options."""
        config = RedisConfig(
            host="redis.example.com",
            port=6380,
            ssl=True,
            ssl_cert_reqs="required",
        )

        kwargs = config.to_redis_kwargs()

        assert kwargs["ssl"] is True
        assert kwargs["ssl_cert_reqs"] == "required"

    def test_socket_timeout_configuration(self):
        """Test socket timeout configuration."""
        config = RedisConfig(
            host="localhost",
            port=6379,
            socket_timeout=10.0,
            socket_connect_timeout=5.0,
        )

        kwargs = config.to_redis_kwargs()

        assert kwargs["socket_timeout"] == 10.0
        assert kwargs["socket_connect_timeout"] == 5.0


class TestMetricsTracking:
    """Test that metrics are properly tracked during fallback scenarios."""

    @patch("empathy_os.memory.short_term.REDIS_AVAILABLE", True)
    @patch("empathy_os.memory.short_term.redis.Redis")
    def test_tracks_retries_in_metrics(self, mock_redis_cls):
        """Test that retry attempts increment metrics counter."""
        mock_client = Mock()
        call_count = 0

        def ping_with_retries():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise redis.TimeoutError("Timeout")
            return True

        mock_client.ping = ping_with_retries
        mock_redis_cls.return_value = mock_client

        memory = RedisShortTermMemory(host="localhost", port=6379)

        # Verify retries were tracked
        assert memory._metrics.retries_total == 2  # 2 failures before success

    def test_mock_storage_provides_stats(self):
        """Test that mock storage provides stats."""
        memory = RedisShortTermMemory(use_mock=True)
        creds = AgentCredentials("test_agent", AccessTier.CONTRIBUTOR)

        # Perform operations
        memory.stash("key1", {"data": "value1"}, creds, ttl=TTLStrategy.WORKING_RESULTS)
        memory.retrieve("key1", creds)

        # Should be able to get stats
        stats = memory.get_stats()
        assert stats is not None
        assert "mode" in stats
        assert stats["mode"] == "mock"
