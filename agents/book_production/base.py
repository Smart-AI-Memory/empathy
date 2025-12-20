"""
Book Production Pipeline - Base Agent

Provides the foundation for all book production agents (Research, Writer, Editor, Reviewer).
Integrates with Redis for state management and MemDocs for pattern storage.

Design Philosophy:
- Each agent is a specialist with a clear role
- Agents share state through a common state structure
- Patterns are learned and reused across chapters via MemDocs
- Model selection optimizes quality vs. cost (Opus for creative, Sonnet for structured)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
import os
import warnings
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from empathy_llm_toolkit.config.unified import (
    MemDocsConfig as UnifiedMemDocsConfig,
)
from empathy_llm_toolkit.config.unified import (
    RedisConfig as UnifiedRedisConfig,
)

# Import unified configuration (preferred)
from empathy_llm_toolkit.config.unified import (
    UnifiedAgentConfig,
)

logger = logging.getLogger(__name__)


# =============================================================================
# Legacy Configuration (Deprecated - use unified config instead)
# =============================================================================


@dataclass
class AgentConfig:
    """
    Legacy configuration for book production agent.

    DEPRECATED: Use UnifiedAgentConfig or BookProductionConfig instead.
    This class is maintained for backward compatibility.

    Migration example:
        # Old way
        config = AgentConfig(model="claude-opus-4-20250514")

        # New way
        from empathy_llm_toolkit.config import UnifiedAgentConfig, ModelTier
        config = UnifiedAgentConfig(
            name="writer",
            model_tier=ModelTier.PREMIUM
        )
    """

    model: str = "claude-sonnet-4-20250514"
    max_tokens: int = 8000
    temperature: float = 0.7
    timeout: int = 120
    retry_attempts: int = 3
    retry_delay: float = 1.0

    def __post_init__(self):
        warnings.warn(
            "AgentConfig is deprecated. Use UnifiedAgentConfig from "
            "empathy_llm_toolkit.config instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def to_unified(self, name: str = "book_agent") -> UnifiedAgentConfig:
        """Convert to UnifiedAgentConfig."""
        # Determine tier from model name
        if "opus" in self.model.lower():
            tier = "premium"
        elif "haiku" in self.model.lower():
            tier = "cheap"
        else:
            tier = "capable"

        return UnifiedAgentConfig(
            name=name,
            model_tier=tier,
            model_override=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            timeout=self.timeout,
            retry_attempts=self.retry_attempts,
            retry_delay=self.retry_delay,
        )


@dataclass
class MemDocsConfig:
    """
    Legacy MemDocs configuration.

    DEPRECATED: Use empathy_llm_toolkit.config.MemDocsConfig instead.
    """

    enabled: bool = True
    project: str = "book-production"
    collections: dict[str, str] = field(
        default_factory=lambda: {
            "patterns": "book_patterns",
            "exemplars": "exemplar_chapters",
            "transformations": "transformation_examples",
            "feedback": "quality_feedback",
        }
    )

    def to_unified(self) -> UnifiedMemDocsConfig:
        """Convert to unified MemDocsConfig."""
        return UnifiedMemDocsConfig(
            enabled=self.enabled,
            project=self.project,
            collections=self.collections,
        )


@dataclass
class RedisConfig:
    """
    Legacy Redis configuration.

    DEPRECATED: Use empathy_llm_toolkit.config.RedisConfig instead.
    """

    enabled: bool = True
    host: str = "localhost"
    port: int = 6379
    db: int = 0
    prefix: str = "book_production"
    ttl: int = 86400  # 24 hours

    def to_unified(self) -> UnifiedRedisConfig:
        """Convert to unified RedisConfig."""
        return UnifiedRedisConfig(
            enabled=self.enabled,
            host=self.host,
            port=self.port,
            db=self.db,
            prefix=self.prefix,
            ttl=self.ttl,
        )


class BaseAgent(ABC):
    """
    Base class for all book production agents.

    Provides common functionality:
    - LLM interaction with model selection
    - Redis state management (abstracted)
    - MemDocs pattern retrieval and storage
    - Audit trail logging
    - Error handling with retries

    Key Insight from Experience:
    Multi-agent book production succeeds when:
    1. Each agent has a clear, focused responsibility
    2. State is shared explicitly through a common structure
    3. Patterns learned from one chapter improve the next
    4. Model selection matches task complexity (Opus for creative, Sonnet for structured)
    """

    # Default model - subclasses override based on role
    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    # Agent metadata
    name: str = "BaseAgent"
    description: str = "Base agent for book production"
    empathy_level: int = 4  # Level 4 Anticipatory

    def __init__(
        self,
        config: AgentConfig | None = None,
        memdocs_config: MemDocsConfig | None = None,
        redis_config: RedisConfig | None = None,
        llm_provider: Any | None = None,
    ):
        """
        Initialize the agent.

        Args:
            config: Agent configuration (model, tokens, etc.)
            memdocs_config: MemDocs integration configuration
            redis_config: Redis state management configuration
            llm_provider: Optional LLM provider (for testing/injection)
        """
        self.config = config or AgentConfig(model=self.DEFAULT_MODEL)
        self.memdocs_config = memdocs_config or MemDocsConfig()
        self.redis_config = redis_config or RedisConfig()
        self.llm_provider = llm_provider

        self.logger = logging.getLogger(f"agent.{self.name}")

        # State stores (initialized lazily)
        self._redis_client = None
        self._memdocs_client = None

    # =========================================================================
    # Abstract Methods - Subclasses must implement
    # =========================================================================

    @abstractmethod
    async def process(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Process the state and return updated state.

        This is the main entry point for the agent. Each agent type
        implements this with its specific logic.

        Args:
            state: Current pipeline state (ChapterProductionState)

        Returns:
            Updated state with agent's contributions
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Return the system prompt for this agent.

        The system prompt defines the agent's personality, capabilities,
        and constraints. It should encode the patterns that make for
        successful book chapters.
        """
        pass

    # =========================================================================
    # LLM Interaction
    # =========================================================================

    async def generate(
        self,
        prompt: str,
        system: str | None = None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> str:
        """
        Generate text using the configured LLM.

        Args:
            prompt: User prompt
            system: System prompt (uses agent default if not provided)
            max_tokens: Max tokens (uses config default if not provided)
            temperature: Temperature (uses config default if not provided)

        Returns:
            Generated text content
        """
        system = system or self.get_system_prompt()
        max_tokens = max_tokens or self.config.max_tokens
        temperature = temperature or self.config.temperature

        self.logger.info(
            f"Generating with {self.config.model} (max_tokens={max_tokens}, temp={temperature})"
        )

        # If we have an injected provider, use it
        if self.llm_provider:
            return await self._generate_with_provider(prompt, system, max_tokens, temperature)

        # Otherwise, use Anthropic directly
        return await self._generate_with_anthropic(prompt, system, max_tokens, temperature)

    async def _generate_with_provider(
        self,
        prompt: str,
        system: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate using injected provider (for testing)"""
        if hasattr(self.llm_provider, "generate"):
            return await self.llm_provider.generate(
                prompt=prompt,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )
        raise ValueError("LLM provider must have generate() method")

    async def _generate_with_anthropic(
        self,
        prompt: str,
        system: str,
        max_tokens: int,
        temperature: float,
    ) -> str:
        """Generate using Anthropic API directly"""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package required: pip install anthropic")

        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")

        client = anthropic.Anthropic(api_key=api_key)

        # Retry logic
        last_error = None
        for attempt in range(self.config.retry_attempts):
            try:
                response = client.messages.create(
                    model=self.config.model,
                    max_tokens=max_tokens,
                    system=system,
                    messages=[{"role": "user", "content": prompt}],
                )

                return response.content[0].text

            except Exception as e:
                last_error = e
                self.logger.warning(
                    f"LLM call failed (attempt {attempt + 1}/{self.config.retry_attempts}): {e}"
                )
                if attempt < self.config.retry_attempts - 1:
                    import asyncio

                    await asyncio.sleep(self.config.retry_delay)

        raise RuntimeError(
            f"LLM generation failed after {self.config.retry_attempts} attempts: {last_error}"
        )

    # =========================================================================
    # Redis State Management
    # =========================================================================

    async def get_state(self, key: str) -> dict[str, Any] | None:
        """
        Retrieve state from Redis.

        Args:
            key: State key

        Returns:
            State dictionary or None if not found
        """
        if not self.redis_config.enabled:
            return None

        client = await self._get_redis_client()
        if not client:
            return None

        full_key = f"{self.redis_config.prefix}:{key}"
        data = await client.get(full_key)

        if data:
            return json.loads(data)
        return None

    async def set_state(
        self,
        key: str,
        state: dict[str, Any],
        ttl: int | None = None,
    ) -> bool:
        """
        Store state in Redis.

        Args:
            key: State key
            state: State dictionary
            ttl: Time to live in seconds (uses config default if not provided)

        Returns:
            True if successful
        """
        if not self.redis_config.enabled:
            return False

        client = await self._get_redis_client()
        if not client:
            return False

        full_key = f"{self.redis_config.prefix}:{key}"
        ttl = ttl or self.redis_config.ttl

        await client.set(full_key, json.dumps(state), ex=ttl)
        return True

    async def _get_redis_client(self):
        """Get or create Redis client"""
        if self._redis_client:
            return self._redis_client

        try:
            import redis.asyncio as redis
        except ImportError:
            self.logger.warning("redis package not available - state management disabled")
            return None

        try:
            self._redis_client = redis.Redis(
                host=self.redis_config.host,
                port=self.redis_config.port,
                db=self.redis_config.db,
                decode_responses=True,
            )
            return self._redis_client
        except Exception as e:
            self.logger.warning(f"Redis connection failed: {e}")
            return None

    # =========================================================================
    # MemDocs Pattern Management
    # =========================================================================

    async def search_patterns(
        self,
        query: str,
        collection: str = "patterns",
        limit: int = 5,
        min_confidence: float = 0.7,
    ) -> list[dict[str, Any]]:
        """
        Search for patterns in MemDocs.

        Args:
            query: Search query
            collection: Collection to search (default: patterns)
            limit: Maximum results to return
            min_confidence: Minimum confidence threshold

        Returns:
            List of matching patterns
        """
        if not self.memdocs_config.enabled:
            return []

        collection_name = self.memdocs_config.collections.get(collection, collection)

        self.logger.debug(f"Searching MemDocs collection '{collection_name}' for: {query}")

        # TODO: Integrate with actual MemDocs client
        # For now, return from local pattern cache
        return await self._search_local_patterns(query, collection_name, limit)

    async def store_pattern(
        self,
        pattern: dict[str, Any],
        collection: str = "patterns",
    ) -> str:
        """
        Store a pattern in MemDocs.

        Args:
            pattern: Pattern dictionary with content and metadata
            collection: Collection to store in

        Returns:
            Pattern ID
        """
        if not self.memdocs_config.enabled:
            return ""

        collection_name = self.memdocs_config.collections.get(collection, collection)

        # Add metadata
        pattern["stored_at"] = datetime.now().isoformat()
        pattern["stored_by"] = self.name
        pattern["agent_version"] = "1.0.0"

        self.logger.info(f"Storing pattern in MemDocs collection '{collection_name}'")

        # TODO: Integrate with actual MemDocs client
        # For now, store locally
        return await self._store_local_pattern(pattern, collection_name)

    async def _search_local_patterns(
        self,
        query: str,
        collection: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Search local pattern cache (fallback when MemDocs not available)"""
        # Local pattern storage path
        pattern_dir = Path(__file__).parent / "patterns" / collection

        if not pattern_dir.exists():
            return []

        patterns = []
        for pattern_file in pattern_dir.glob("*.json"):
            try:
                with open(pattern_file) as f:
                    pattern = json.load(f)
                    # Simple keyword matching
                    content = json.dumps(pattern).lower()
                    if any(term.lower() in content for term in query.split()):
                        patterns.append(pattern)
            except Exception as e:
                self.logger.warning(f"Failed to load pattern {pattern_file}: {e}")

        return patterns[:limit]

    async def _store_local_pattern(
        self,
        pattern: dict[str, Any],
        collection: str,
    ) -> str:
        """Store pattern locally (fallback when MemDocs not available)"""
        pattern_dir = Path(__file__).parent / "patterns" / collection
        pattern_dir.mkdir(parents=True, exist_ok=True)

        # Generate pattern ID
        pattern_id = f"pat_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(json.dumps(pattern)) % 10000:04d}"
        pattern["pattern_id"] = pattern_id

        pattern_file = pattern_dir / f"{pattern_id}.json"
        with open(pattern_file, "w") as f:
            json.dump(pattern, f, indent=2)

        return pattern_id

    # =========================================================================
    # Audit Trail
    # =========================================================================

    def add_audit_entry(
        self,
        state: dict[str, Any],
        action: str,
        details: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Add an entry to the audit trail.

        Args:
            state: Current state
            action: Description of action taken
            details: Additional details

        Returns:
            Updated state with audit entry
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "action": action,
            "details": details or {},
        }

        audit_trail = list(state.get("audit_trail", []))
        audit_trail.append(entry)

        return {**state, "audit_trail": audit_trail, "last_updated": datetime.now().isoformat()}

    # =========================================================================
    # Utility Methods
    # =========================================================================

    def read_file(self, path: str) -> str:
        """Read content from a file"""
        try:
            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            self.logger.error(f"Failed to read file {path}: {e}")
            return ""

    def count_words(self, text: str) -> int:
        """Count words in text"""
        return len(text.split())


class OpusAgent(BaseAgent):
    """
    Base class for agents that use Claude Opus 4.5.

    Use Opus for:
    - Creative writing (Writer Agent)
    - Nuanced quality assessment (Reviewer Agent)
    - Complex reasoning tasks
    """

    DEFAULT_MODEL = "claude-opus-4-5-20250514"


class SonnetAgent(BaseAgent):
    """
    Base class for agents that use Claude Sonnet.

    Use Sonnet for:
    - Structured extraction (Research Agent)
    - Rule-based processing (Editor Agent)
    - Fast iteration tasks
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"
