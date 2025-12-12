"""
Comprehensive tests for Unified Memory Module

Tests cover:
- UnifiedMemory initialization
- Environment-based configuration
- Short-term memory operations (stash/retrieve)
- Long-term memory operations (persist/recall)
- Pattern staging and promotion
- Health checks
- Error handling and edge cases
- Mock and real Redis scenarios

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import tempfile
from unittest.mock import Mock, patch

from empathy_os.memory.long_term import Classification
from empathy_os.memory.redis_bootstrap import RedisStartMethod, RedisStatus
from empathy_os.memory.short_term import AccessTier
from empathy_os.memory.unified import (
    Environment,
    MemoryConfig,
    UnifiedMemory,
)


class TestEnvironment:
    """Test Environment enum"""

    def test_environment_values(self):
        """Test environment enum values"""
        assert Environment.DEVELOPMENT.value == "development"
        assert Environment.STAGING.value == "staging"
        assert Environment.PRODUCTION.value == "production"


class TestMemoryConfig:
    """Test MemoryConfig dataclass"""

    def test_memory_config_defaults(self):
        """Test default configuration values"""
        config = MemoryConfig()
        assert config.environment == Environment.DEVELOPMENT
        assert config.redis_host == "localhost"
        assert config.redis_port == 6379
        assert config.redis_mock is False
        assert config.redis_auto_start is True
        assert config.encryption_enabled is True
        assert config.claude_memory_enabled is True

    def test_memory_config_custom_values(self):
        """Test custom configuration values"""
        config = MemoryConfig(
            environment=Environment.PRODUCTION,
            redis_host="redis.example.com",
            redis_port=6380,
            redis_mock=True,
            storage_dir="/custom/storage",
            encryption_enabled=False,
        )
        assert config.environment == Environment.PRODUCTION
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380
        assert config.redis_mock is True
        assert config.encryption_enabled is False

    @patch.dict(
        os.environ,
        {
            "EMPATHY_ENV": "production",
            "REDIS_URL": "redis://example.com:6379",
            "EMPATHY_REDIS_HOST": "custom-host",
            "EMPATHY_REDIS_PORT": "6380",
            "EMPATHY_REDIS_MOCK": "true",
            "EMPATHY_STORAGE_DIR": "/tmp/storage",
            "EMPATHY_ENCRYPTION": "false",
            "EMPATHY_CLAUDE_MEMORY": "false",
        },
    )
    def test_from_environment(self):
        """Test creating config from environment variables"""
        config = MemoryConfig.from_environment()

        assert config.environment == Environment.PRODUCTION
        assert config.redis_url == "redis://example.com:6379"
        assert config.redis_host == "custom-host"
        assert config.redis_port == 6380
        assert config.redis_mock is True
        assert config.storage_dir == "/tmp/storage"
        assert config.encryption_enabled is False
        assert config.claude_memory_enabled is False

    @patch.dict(os.environ, {"EMPATHY_ENV": "invalid"})
    def test_from_environment_invalid_env(self):
        """Test from_environment with invalid environment value"""
        config = MemoryConfig.from_environment()
        # Should fallback to DEVELOPMENT
        assert config.environment == Environment.DEVELOPMENT

    @patch.dict(os.environ, {})
    def test_from_environment_defaults(self):
        """Test from_environment with no env vars set"""
        config = MemoryConfig.from_environment()
        assert config.environment == Environment.DEVELOPMENT
        assert config.redis_host == "localhost"
        assert config.redis_mock is False


class TestUnifiedMemoryInit:
    """Test UnifiedMemory initialization"""

    def test_init_with_defaults(self):
        """Test initialization with default config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(
                storage_dir=tmpdir, redis_mock=True  # Use mock to avoid Redis dependency
            )
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory.user_id == "test_user"
            assert memory.config == config
            assert memory.access_tier == AccessTier.CONTRIBUTOR
            assert memory._initialized is True

    def test_init_with_custom_access_tier(self):
        """Test initialization with custom access tier"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(
                user_id="admin_user",
                config=config,
                access_tier=AccessTier.STEWARD,
            )

            assert memory.access_tier == AccessTier.STEWARD

    def test_credentials_property(self):
        """Test credentials property"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            creds = memory.credentials
            assert creds.agent_id == "test_user"
            assert creds.tier == AccessTier.CONTRIBUTOR


class TestUnifiedMemoryBackendInit:
    """Test backend initialization scenarios"""

    def test_init_with_mock_redis_explicit(self):
        """Test initialization with explicit mock Redis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory._short_term is not None
            assert memory._redis_status is not None
            assert memory._redis_status.method == RedisStartMethod.MOCK

    @patch("empathy_os.memory.unified.get_redis_memory")
    def test_init_with_redis_url(self, mock_get_redis):
        """Test initialization with Redis URL"""
        mock_memory = Mock()
        mock_get_redis.return_value = mock_memory

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_url="redis://localhost:6379")
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory._short_term is not None
            assert memory._redis_status.method == RedisStartMethod.ALREADY_RUNNING

    @patch("empathy_os.memory.unified.ensure_redis")
    def test_init_with_auto_start_success(self, mock_ensure):
        """Test initialization with auto-start success"""
        mock_ensure.return_value = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_auto_start=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory._redis_status.available is True
            assert memory._redis_status.method == RedisStartMethod.HOMEBREW

    @patch("empathy_os.memory.unified.ensure_redis")
    def test_init_with_auto_start_failure(self, mock_ensure):
        """Test initialization with auto-start failure falls back to mock"""
        mock_ensure.return_value = RedisStatus(available=False, method=RedisStartMethod.MOCK)

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_auto_start=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Should fallback to mock
            assert memory._short_term is not None

    def test_init_long_term_memory(self):
        """Test long-term memory initialization"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory._long_term is not None
            assert memory.has_long_term is True

    @patch(
        "empathy_os.memory.unified.SecureMemDocsIntegration",
        side_effect=Exception("Failed to init"),
    )
    def test_init_long_term_memory_failure(self, mock_secure):
        """Test long-term memory initialization failure"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory._long_term is None
            assert memory.has_long_term is False


class TestUnifiedMemoryShortTermOps:
    """Test short-term memory operations"""

    def test_stash_and_retrieve(self):
        """Test stashing and retrieving data"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Stash data
            data = {"key": "value", "count": 42}
            result = memory.stash("test_key", data)
            assert result is True

            # Retrieve data
            retrieved = memory.retrieve("test_key")
            assert retrieved == data

    def test_stash_with_custom_ttl(self):
        """Test stashing with custom TTL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.stash("test_key", {"data": "test"}, ttl_seconds=300)
            assert result is True

    def test_retrieve_nonexistent_key(self):
        """Test retrieving non-existent key returns None"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            retrieved = memory.retrieve("nonexistent_key")
            assert retrieved is None

    def test_stash_without_short_term(self):
        """Test stash when short-term memory is unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._short_term = None

            result = memory.stash("test_key", {"data": "test"})
            assert result is False

    def test_retrieve_without_short_term(self):
        """Test retrieve when short-term memory is unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._short_term = None

            result = memory.retrieve("test_key")
            assert result is None


class TestUnifiedMemoryPatternStaging:
    """Test pattern staging operations"""

    def test_stage_pattern(self):
        """Test staging a pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            pattern_data = {
                "content": "Test pattern content",
                "metadata": {"key": "value"},
            }
            pattern_id = memory.stage_pattern(pattern_data, pattern_type="test")

            assert pattern_id is not None
            assert isinstance(pattern_id, str)

    def test_stage_pattern_with_custom_ttl(self):
        """Test staging pattern with custom TTL"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            pattern_data = {"content": "Test pattern"}
            pattern_id = memory.stage_pattern(pattern_data, ttl_hours=48)

            assert pattern_id is not None

    def test_get_staged_patterns(self):
        """Test retrieving all staged patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Stage multiple patterns
            memory.stage_pattern({"content": "Pattern 1"})
            memory.stage_pattern({"content": "Pattern 2"})

            patterns = memory.get_staged_patterns()
            assert len(patterns) >= 2

    def test_stage_pattern_without_short_term(self):
        """Test staging when short-term memory unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._short_term = None

            pattern_id = memory.stage_pattern({"content": "Test"})
            assert pattern_id is None

    def test_get_staged_patterns_without_short_term(self):
        """Test get_staged_patterns when short-term unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._short_term = None

            patterns = memory.get_staged_patterns()
            assert patterns == []


class TestUnifiedMemoryLongTermOps:
    """Test long-term memory operations"""

    def test_persist_pattern(self):
        """Test persisting a pattern to long-term storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.persist_pattern(
                content="Test pattern content",
                pattern_type="algorithm",
                classification=Classification.PUBLIC,
            )

            assert result is not None
            assert "pattern_id" in result
            assert "classification" in result

    def test_persist_pattern_with_auto_classify(self):
        """Test persisting with auto-classification"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.persist_pattern(
                content="General pattern content",
                pattern_type="general",
                auto_classify=True,
            )

            assert result is not None
            assert result["classification"] in ["PUBLIC", "INTERNAL", "SENSITIVE"]

    def test_persist_pattern_with_string_classification(self):
        """Test persisting with string classification"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.persist_pattern(
                content="Test content",
                pattern_type="test",
                classification="INTERNAL",
                auto_classify=False,
            )

            assert result is not None
            assert result["classification"] == "INTERNAL"

    def test_persist_pattern_with_metadata(self):
        """Test persisting pattern with custom metadata"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            metadata = {"custom_field": "custom_value", "version": "1.0"}
            result = memory.persist_pattern(
                content="Test content",
                pattern_type="test",
                metadata=metadata,
            )

            assert result is not None

    def test_persist_pattern_without_long_term(self):
        """Test persist when long-term memory unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._long_term = None

            result = memory.persist_pattern(content="Test content", pattern_type="test")
            assert result is None

    @patch("empathy_os.memory.unified.SecureMemDocsIntegration")
    def test_persist_pattern_exception_handling(self, mock_secure):
        """Test persist_pattern handles exceptions"""
        mock_secure.return_value.store_pattern.side_effect = Exception("Storage error")

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.persist_pattern(content="Test content", pattern_type="test")
            # Should handle exception and return None
            assert result is None

    def test_recall_pattern(self):
        """Test recalling a pattern from long-term storage"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # First persist a pattern
            persist_result = memory.persist_pattern(content="Test content", pattern_type="test")
            pattern_id = persist_result["pattern_id"]

            # Then recall it
            pattern = memory.recall_pattern(pattern_id)
            assert pattern is not None
            assert "content" in pattern
            assert "metadata" in pattern

    def test_recall_pattern_with_permissions(self):
        """Test recalling pattern with permission check"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            persist_result = memory.persist_pattern(content="Test content", pattern_type="test")
            pattern_id = persist_result["pattern_id"]

            pattern = memory.recall_pattern(pattern_id, check_permissions=True)
            assert pattern is not None

    def test_recall_pattern_without_permissions(self):
        """Test recalling pattern without permission check"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            persist_result = memory.persist_pattern(content="Test content", pattern_type="test")
            pattern_id = persist_result["pattern_id"]

            pattern = memory.recall_pattern(pattern_id, check_permissions=False)
            assert pattern is not None

    def test_recall_pattern_nonexistent(self):
        """Test recalling non-existent pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            pattern = memory.recall_pattern("nonexistent_pattern_id")
            assert pattern is None

    def test_recall_pattern_without_long_term(self):
        """Test recall when long-term memory unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._long_term = None

            pattern = memory.recall_pattern("some_id")
            assert pattern is None

    def test_search_patterns(self):
        """Test searching patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Note: Current implementation returns empty list
            # This test documents the API
            patterns = memory.search_patterns(query="test", limit=10)
            assert isinstance(patterns, list)

    def test_search_patterns_without_long_term(self):
        """Test search when long-term memory unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._long_term = None

            patterns = memory.search_patterns()
            assert patterns == []


class TestUnifiedMemoryPatternPromotion:
    """Test pattern promotion from short to long-term"""

    def test_promote_pattern_success(self):
        """Test successful pattern promotion"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Stage a pattern
            pattern_data = {
                "content": "Test pattern",
                "pattern_type": "test",
                "metadata": {"key": "value"},
            }
            staged_id = memory.stage_pattern(pattern_data)

            # Promote it
            result = memory.promote_pattern(staged_id)
            assert result is not None
            assert "pattern_id" in result

    def test_promote_pattern_with_classification(self):
        """Test promotion with explicit classification"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            pattern_data = {"content": "Test pattern", "pattern_type": "test"}
            staged_id = memory.stage_pattern(pattern_data)

            result = memory.promote_pattern(staged_id, classification=Classification.INTERNAL)
            assert result is not None
            assert result["classification"] == "INTERNAL"

    def test_promote_pattern_nonexistent(self):
        """Test promoting non-existent pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            result = memory.promote_pattern("nonexistent_id")
            assert result is None

    def test_promote_pattern_without_backends(self):
        """Test promotion when backends unavailable"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)
            memory._short_term = None
            memory._long_term = None

            result = memory.promote_pattern("some_id")
            assert result is None


class TestUnifiedMemoryUtilities:
    """Test utility methods and properties"""

    def test_has_short_term(self):
        """Test has_short_term property"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory.has_short_term is True

            memory._short_term = None
            assert memory.has_short_term is False

    def test_has_long_term(self):
        """Test has_long_term property"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory.has_long_term is True

            memory._long_term = None
            assert memory.has_long_term is False

    def test_redis_status_property(self):
        """Test redis_status property"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            status = memory.redis_status
            assert status is not None
            assert isinstance(status, RedisStatus)

    def test_using_real_redis(self):
        """Test using_real_redis property"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Mock Redis, so should be False
            assert memory.using_real_redis is False

    @patch("empathy_os.memory.unified.ensure_redis")
    def test_using_real_redis_true(self, mock_ensure):
        """Test using_real_redis when using actual Redis"""
        mock_ensure.return_value = RedisStatus(available=True, method=RedisStartMethod.HOMEBREW)

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=False, redis_auto_start=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            assert memory.using_real_redis is True

    def test_health_check(self):
        """Test health_check method"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            health = memory.health_check()

            assert "short_term" in health
            assert "long_term" in health
            assert "environment" in health
            assert health["short_term"]["available"] is True
            assert health["long_term"]["available"] is True

    def test_health_check_detailed_info(self):
        """Test health check includes detailed information"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            health = memory.health_check()

            assert "mock_mode" in health["short_term"]
            assert "method" in health["short_term"]
            assert "storage_dir" in health["long_term"]
            assert "encryption" in health["long_term"]


class TestUnifiedMemoryEdgeCases:
    """Test edge cases and error scenarios"""

    def test_double_initialization_prevented(self):
        """Test that backends are not reinitialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Store reference to backends
            short_term_ref = memory._short_term
            long_term_ref = memory._long_term

            # Try to reinitialize
            memory._initialize_backends()

            # Should be the same instances
            assert memory._short_term is short_term_ref
            assert memory._long_term is long_term_ref

    @patch("empathy_os.memory.unified.RedisShortTermMemory")
    def test_short_term_init_exception_fallback(self, mock_redis):
        """Test fallback to mock when short-term init fails"""
        mock_redis.side_effect = Exception("Connection failed")

        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=False)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Should fallback to mock despite exception
            assert memory._short_term is not None

    def test_empty_user_id(self):
        """Test with empty user_id"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="", config=config)

            assert memory.user_id == ""
            assert memory.credentials.agent_id == ""

    def test_stash_complex_data_types(self):
        """Test stashing complex data structures"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            complex_data = {
                "list": [1, 2, 3],
                "nested": {"key": "value"},
                "string": "test",
                "number": 42,
                "boolean": True,
                "null": None,
            }

            result = memory.stash("complex", complex_data)
            assert result is True

            retrieved = memory.retrieve("complex")
            assert retrieved == complex_data

    def test_persist_empty_content(self):
        """Test persisting empty content"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Should handle empty content gracefully or raise error
            try:
                memory.persist_pattern(content="", pattern_type="test")
                # If it succeeds, that's also valid behavior
            except Exception:
                # Or it might raise an exception, which is also valid
                pass

    @patch.dict(os.environ, {"EMPATHY_ENV": "production"})
    def test_from_environment_production_config(self):
        """Test production environment configuration"""
        config = MemoryConfig.from_environment()
        assert config.environment == Environment.PRODUCTION

    def test_multiple_memory_instances(self):
        """Test multiple UnifiedMemory instances for different users"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)

            memory1 = UnifiedMemory(user_id="user1", config=config)
            memory2 = UnifiedMemory(user_id="user2", config=config)

            # Each should have their own credentials
            assert memory1.credentials.agent_id == "user1"
            assert memory2.credentials.agent_id == "user2"

            # Stash data in different namespaces
            memory1.stash("key", {"user": "user1"})
            memory2.stash("key", {"user": "user2"})

            # Retrieve should get their own data
            assert memory1.retrieve("key")["user"] == "user1"
            assert memory2.retrieve("key")["user"] == "user2"


class TestUnifiedMemoryIntegration:
    """Integration tests for end-to-end workflows"""

    def test_full_pattern_lifecycle(self):
        """Test complete pattern lifecycle: stage -> promote -> recall"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Stage a pattern
            pattern_data = {
                "content": "Complete lifecycle test",
                "pattern_type": "integration",
                "metadata": {"test": True},
            }
            staged_id = memory.stage_pattern(pattern_data)
            assert staged_id is not None

            # Verify it's staged
            staged_patterns = memory.get_staged_patterns()
            assert any(p.get("pattern_id") == staged_id for p in staged_patterns)

            # Promote to long-term
            promoted = memory.promote_pattern(staged_id)
            assert promoted is not None
            long_term_id = promoted["pattern_id"]

            # Recall from long-term
            recalled = memory.recall_pattern(long_term_id)
            assert recalled is not None
            assert "Complete lifecycle test" in recalled["content"]

    def test_concurrent_short_and_long_term_ops(self):
        """Test concurrent short-term and long-term operations"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            # Short-term operation
            memory.stash("working_data", {"status": "in_progress"})

            # Long-term operation
            pattern_result = memory.persist_pattern(
                content="Permanent knowledge", pattern_type="knowledge"
            )

            # Both should succeed
            assert memory.retrieve("working_data") is not None
            assert pattern_result is not None

    def test_health_check_reflects_actual_state(self):
        """Test health check accurately reflects system state"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = MemoryConfig(storage_dir=tmpdir, redis_mock=True)
            memory = UnifiedMemory(user_id="test_user", config=config)

            health = memory.health_check()

            # Should reflect mock mode
            assert health["short_term"]["mock_mode"] is True
            assert health["short_term"]["method"] == "mock"
            assert health["environment"] == "development"
