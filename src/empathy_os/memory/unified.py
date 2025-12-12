"""
Unified Memory Interface for Empathy Framework

Provides a single API for both short-term (Redis) and long-term (persistent) memory,
with automatic pattern promotion and environment-aware storage backend selection.

Usage:
    from empathy_os.memory import UnifiedMemory

    memory = UnifiedMemory(
        user_id="agent@company.com",
        environment="production",  # or "staging", "development"
    )

    # Short-term operations
    memory.stash("working_data", {"key": "value"})
    data = memory.retrieve("working_data")

    # Long-term operations
    result = memory.persist_pattern(content, pattern_type="algorithm")
    pattern = memory.recall_pattern(pattern_id)

    # Pattern promotion
    memory.promote_pattern(staged_pattern_id)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

from .claude_memory import ClaudeMemoryConfig
from .config import get_redis_memory
from .long_term import Classification, SecureMemDocsIntegration
from .redis_bootstrap import RedisStartMethod, RedisStatus, ensure_redis
from .short_term import (
    AccessTier,
    AgentCredentials,
    RedisShortTermMemory,
    StagedPattern,
    TTLStrategy,
)

logger = structlog.get_logger(__name__)


class Environment(Enum):
    """Deployment environment for storage configuration."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


@dataclass
class MemoryConfig:
    """Configuration for unified memory system."""

    # Environment
    environment: Environment = Environment.DEVELOPMENT

    # Short-term memory settings
    redis_url: str | None = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_mock: bool = False
    redis_auto_start: bool = True  # Auto-start Redis if not running
    default_ttl_seconds: int = 3600  # 1 hour

    # Long-term memory settings
    storage_dir: str = "./memdocs_storage"
    encryption_enabled: bool = True

    # Claude memory settings
    claude_memory_enabled: bool = True
    load_enterprise_memory: bool = True
    load_project_memory: bool = True
    load_user_memory: bool = True

    # Pattern promotion settings
    auto_promote_threshold: float = 0.8  # Confidence threshold for auto-promotion

    @classmethod
    def from_environment(cls) -> "MemoryConfig":
        """
        Create configuration from environment variables.

        Environment Variables:
            EMPATHY_ENV: Environment (development/staging/production)
            REDIS_URL: Redis connection URL
            EMPATHY_REDIS_MOCK: Use mock Redis (true/false)
            EMPATHY_STORAGE_DIR: Long-term storage directory
            EMPATHY_ENCRYPTION: Enable encryption (true/false)
        """
        env_str = os.getenv("EMPATHY_ENV", "development").lower()
        environment = (
            Environment(env_str)
            if env_str in [e.value for e in Environment]
            else Environment.DEVELOPMENT
        )

        return cls(
            environment=environment,
            redis_url=os.getenv("REDIS_URL"),
            redis_host=os.getenv("EMPATHY_REDIS_HOST", "localhost"),
            redis_port=int(os.getenv("EMPATHY_REDIS_PORT", "6379")),
            redis_mock=os.getenv("EMPATHY_REDIS_MOCK", "").lower() == "true",
            redis_auto_start=os.getenv("EMPATHY_REDIS_AUTO_START", "true").lower() == "true",
            storage_dir=os.getenv("EMPATHY_STORAGE_DIR", "./memdocs_storage"),
            encryption_enabled=os.getenv("EMPATHY_ENCRYPTION", "true").lower() == "true",
            claude_memory_enabled=os.getenv("EMPATHY_CLAUDE_MEMORY", "true").lower() == "true",
        )


@dataclass
class UnifiedMemory:
    """
    Unified interface for short-term and long-term memory.

    Provides:
    - Short-term memory (Redis): Fast, TTL-based working memory
    - Long-term memory (Persistent): Cross-session pattern storage
    - Pattern promotion: Move validated patterns from short to long-term
    - Environment-aware configuration: Auto-detect storage backends
    """

    user_id: str
    config: MemoryConfig = field(default_factory=MemoryConfig.from_environment)
    access_tier: AccessTier = AccessTier.CONTRIBUTOR

    # Internal state
    _short_term: RedisShortTermMemory | None = field(default=None, init=False)
    _long_term: SecureMemDocsIntegration | None = field(default=None, init=False)
    _redis_status: RedisStatus | None = field(default=None, init=False)
    _initialized: bool = field(default=False, init=False)

    def __post_init__(self):
        """Initialize memory backends based on configuration."""
        self._initialize_backends()

    def _initialize_backends(self):
        """Initialize short-term and long-term memory backends."""
        if self._initialized:
            return

        # Initialize short-term memory (Redis)
        try:
            if self.config.redis_mock:
                self._short_term = RedisShortTermMemory(use_mock=True)
                self._redis_status = RedisStatus(
                    available=False,
                    method=RedisStartMethod.MOCK,
                    message="Mock mode explicitly enabled",
                )
            elif self.config.redis_url:
                self._short_term = get_redis_memory(url=self.config.redis_url)
                self._redis_status = RedisStatus(
                    available=True,
                    method=RedisStartMethod.ALREADY_RUNNING,
                    message="Connected via REDIS_URL",
                )
            else:
                # Use auto-start if enabled
                if self.config.redis_auto_start:
                    self._redis_status = ensure_redis(
                        host=self.config.redis_host,
                        port=self.config.redis_port,
                        auto_start=True,
                        verbose=True,
                    )
                    if self._redis_status.available:
                        self._short_term = RedisShortTermMemory(
                            host=self.config.redis_host,
                            port=self.config.redis_port,
                            use_mock=False,
                        )
                    else:
                        self._short_term = RedisShortTermMemory(use_mock=True)
                else:
                    self._short_term = get_redis_memory()
                    self._redis_status = RedisStatus(
                        available=True,
                        method=RedisStartMethod.ALREADY_RUNNING,
                        message="Connected to existing Redis",
                    )

            logger.info(
                "short_term_memory_initialized",
                mock_mode=self.config.redis_mock or not self._redis_status.available,
                redis_method=self._redis_status.method.value if self._redis_status else "unknown",
                environment=self.config.environment.value,
            )
        except Exception as e:
            logger.warning("short_term_memory_failed", error=str(e))
            self._short_term = RedisShortTermMemory(use_mock=True)
            self._redis_status = RedisStatus(
                available=False,
                method=RedisStartMethod.MOCK,
                message=f"Failed to initialize: {e}",
            )

        # Initialize long-term memory (SecureMemDocs)
        try:
            claude_config = ClaudeMemoryConfig(
                enabled=self.config.claude_memory_enabled,
                load_enterprise=self.config.load_enterprise_memory,
                load_project=self.config.load_project_memory,
                load_user=self.config.load_user_memory,
            )
            self._long_term = SecureMemDocsIntegration(
                claude_memory_config=claude_config,
                storage_dir=self.config.storage_dir,
                enable_encryption=self.config.encryption_enabled,
            )

            logger.info(
                "long_term_memory_initialized",
                storage_dir=self.config.storage_dir,
                encryption=self.config.encryption_enabled,
            )
        except Exception as e:
            logger.error("long_term_memory_failed", error=str(e))
            self._long_term = None

        self._initialized = True

    @property
    def credentials(self) -> AgentCredentials:
        """Get agent credentials for short-term memory operations."""
        return AgentCredentials(agent_id=self.user_id, tier=self.access_tier)

    # =========================================================================
    # SHORT-TERM MEMORY OPERATIONS
    # =========================================================================

    def stash(self, key: str, value: Any, ttl_seconds: int | None = None) -> bool:
        """
        Store data in short-term memory with TTL.

        Args:
            key: Storage key
            value: Data to store (must be JSON-serializable)
            ttl_seconds: Time-to-live in seconds (default from config)

        Returns:
            True if stored successfully
        """
        if not self._short_term:
            logger.warning("short_term_memory_unavailable")
            return False

        # Map ttl_seconds to TTLStrategy (use WORKING_RESULTS as default)
        ttl_strategy = TTLStrategy.WORKING_RESULTS
        if ttl_seconds is not None:
            # Find closest TTL strategy or use working results
            if ttl_seconds <= TTLStrategy.COORDINATION.value:
                ttl_strategy = TTLStrategy.COORDINATION
            elif ttl_seconds <= TTLStrategy.SESSION.value:
                ttl_strategy = TTLStrategy.SESSION
            elif ttl_seconds <= TTLStrategy.WORKING_RESULTS.value:
                ttl_strategy = TTLStrategy.WORKING_RESULTS
            elif ttl_seconds <= TTLStrategy.STAGED_PATTERNS.value:
                ttl_strategy = TTLStrategy.STAGED_PATTERNS
            else:
                ttl_strategy = TTLStrategy.CONFLICT_CONTEXT

        return self._short_term.stash(key, value, self.credentials, ttl_strategy)

    def retrieve(self, key: str) -> Any | None:
        """
        Retrieve data from short-term memory.

        Args:
            key: Storage key

        Returns:
            Stored data or None if not found
        """
        if not self._short_term:
            return None

        return self._short_term.retrieve(key, self.credentials)

    def stage_pattern(
        self,
        pattern_data: dict[str, Any],
        pattern_type: str = "general",
        ttl_hours: int = 24,
    ) -> str | None:
        """
        Stage a pattern for validation before long-term storage.

        Args:
            pattern_data: Pattern content and metadata
            pattern_type: Type of pattern (algorithm, protocol, etc.)
            ttl_hours: Hours before staged pattern expires (not used in current impl)

        Returns:
            Staged pattern ID or None if failed
        """
        if not self._short_term:
            logger.warning("short_term_memory_unavailable")
            return None

        # Create a StagedPattern object from the pattern_data dict
        pattern_id = f"staged_{uuid.uuid4().hex[:12]}"
        staged_pattern = StagedPattern(
            pattern_id=pattern_id,
            agent_id=self.user_id,
            pattern_type=pattern_type,
            name=pattern_data.get("name", f"Pattern {pattern_id[:8]}"),
            description=pattern_data.get("description", ""),
            code=pattern_data.get("code"),
            context=pattern_data.get("context", {}),
            confidence=pattern_data.get("confidence", 0.5),
            staged_at=datetime.now(),
            interests=pattern_data.get("interests", []),
        )
        # Store content in context if provided
        if "content" in pattern_data:
            staged_pattern.context["content"] = pattern_data["content"]

        success = self._short_term.stage_pattern(staged_pattern, self.credentials)
        return pattern_id if success else None

    def get_staged_patterns(self) -> list[dict]:
        """
        Get all staged patterns awaiting validation.

        Returns:
            List of staged patterns with metadata
        """
        if not self._short_term:
            return []

        staged_list = self._short_term.list_staged_patterns(self.credentials)
        return [p.to_dict() for p in staged_list]

    # =========================================================================
    # LONG-TERM MEMORY OPERATIONS
    # =========================================================================

    def persist_pattern(
        self,
        content: str,
        pattern_type: str,
        classification: Classification | str | None = None,
        auto_classify: bool = True,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """
        Store a pattern in long-term memory with security controls.

        Args:
            content: Pattern content
            pattern_type: Type of pattern (algorithm, protocol, etc.)
            classification: Security classification (PUBLIC/INTERNAL/SENSITIVE)
            auto_classify: Auto-detect classification from content
            metadata: Additional metadata to store

        Returns:
            Storage result with pattern_id and classification, or None if failed
        """
        if not self._long_term:
            logger.error("long_term_memory_unavailable")
            return None

        try:
            # Convert string classification to enum if needed
            explicit_class = None
            if classification is not None:
                if isinstance(classification, str):
                    explicit_class = Classification[classification.upper()]
                else:
                    explicit_class = classification

            result = self._long_term.store_pattern(
                content=content,
                pattern_type=pattern_type,
                user_id=self.user_id,
                explicit_classification=explicit_class,
                auto_classify=auto_classify,
                custom_metadata=metadata,
            )
            logger.info(
                "pattern_persisted",
                pattern_id=result.get("pattern_id"),
                classification=result.get("classification"),
            )
            return result
        except Exception as e:
            logger.error("persist_pattern_failed", error=str(e))
            return None

    def recall_pattern(
        self,
        pattern_id: str,
        check_permissions: bool = True,
    ) -> dict[str, Any] | None:
        """
        Retrieve a pattern from long-term memory.

        Args:
            pattern_id: ID of pattern to retrieve
            check_permissions: Verify user has access to pattern

        Returns:
            Pattern data with content and metadata, or None if not found
        """
        if not self._long_term:
            logger.error("long_term_memory_unavailable")
            return None

        try:
            return self._long_term.retrieve_pattern(
                pattern_id=pattern_id,
                user_id=self.user_id,
                check_permissions=check_permissions,
            )
        except Exception as e:
            logger.error("recall_pattern_failed", pattern_id=pattern_id, error=str(e))
            return None

    def search_patterns(
        self,
        query: str | None = None,
        pattern_type: str | None = None,
        classification: Classification | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Search patterns in long-term memory.

        Args:
            query: Text to search for in pattern content
            pattern_type: Filter by pattern type
            classification: Filter by classification level
            limit: Maximum results to return

        Returns:
            List of matching patterns
        """
        if not self._long_term:
            return []

        # Note: Full search implementation depends on storage backend
        # For now, return patterns matching type/classification
        patterns = []
        # This would be implemented based on the storage backend
        return patterns

    # =========================================================================
    # PATTERN PROMOTION (SHORT-TERM → LONG-TERM)
    # =========================================================================

    def promote_pattern(
        self,
        staged_pattern_id: str,
        classification: Classification | str | None = None,
        auto_classify: bool = True,
    ) -> dict[str, Any] | None:
        """
        Promote a staged pattern from short-term to long-term memory.

        Args:
            staged_pattern_id: ID of staged pattern to promote
            classification: Override classification (or auto-detect)
            auto_classify: Auto-detect classification from content

        Returns:
            Long-term storage result, or None if failed
        """
        if not self._short_term or not self._long_term:
            logger.error("memory_backends_unavailable")
            return None

        # Retrieve staged pattern
        staged_patterns = self.get_staged_patterns()
        staged = next(
            (p for p in staged_patterns if p.get("pattern_id") == staged_pattern_id), None
        )

        if not staged:
            logger.warning("staged_pattern_not_found", pattern_id=staged_pattern_id)
            return None

        # Persist to long-term storage
        result = self.persist_pattern(
            content=staged.get("content", ""),
            pattern_type=staged.get("pattern_type", "general"),
            classification=classification,
            auto_classify=auto_classify,
            metadata=staged.get("metadata"),
        )

        if result:
            # Remove from staging (clear from short-term)
            self._short_term.delete(self.credentials, f"staged:{staged_pattern_id}")
            logger.info(
                "pattern_promoted",
                staged_id=staged_pattern_id,
                long_term_id=result.get("pattern_id"),
            )

        return result

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    @property
    def has_short_term(self) -> bool:
        """Check if short-term memory is available."""
        return self._short_term is not None

    @property
    def has_long_term(self) -> bool:
        """Check if long-term memory is available."""
        return self._long_term is not None

    @property
    def redis_status(self) -> RedisStatus | None:
        """Get Redis connection status."""
        return self._redis_status

    @property
    def using_real_redis(self) -> bool:
        """Check if using real Redis (not mock)."""
        return (
            self._redis_status is not None
            and self._redis_status.available
            and self._redis_status.method != RedisStartMethod.MOCK
        )

    def health_check(self) -> dict[str, Any]:
        """
        Check health of memory backends.

        Returns:
            Status of each memory backend
        """
        redis_info = {
            "available": self.has_short_term,
            "mock_mode": not self.using_real_redis,
        }
        if self._redis_status:
            redis_info["method"] = self._redis_status.method.value
            redis_info["host"] = self._redis_status.host
            redis_info["port"] = self._redis_status.port

        return {
            "short_term": redis_info,
            "long_term": {
                "available": self.has_long_term,
                "storage_dir": self.config.storage_dir,
                "encryption": self.config.encryption_enabled,
            },
            "environment": self.config.environment.value,
        }
