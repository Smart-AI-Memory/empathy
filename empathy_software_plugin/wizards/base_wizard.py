"""Base Wizard for Software Development Plugin

Foundation for all software development wizards.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import hashlib
import json
import logging
from abc import ABC, abstractmethod
from typing import Any

from empathy_os.redis_memory import (
    AccessTier,
    AgentCredentials,
    RedisShortTermMemory,
    StagedPattern,
)

logger = logging.getLogger(__name__)


class BaseWizard(ABC):
    """Base class for all software development wizards.

    All wizards implement Level 4 Anticipatory Empathy:
    - Analyze current state
    - Predict future problems
    - Provide prevention steps

    With Redis short-term memory, wizards can:
    - Cache analysis results for reuse
    - Share context with other wizards
    - Stage discovered patterns for validation
    - Coordinate with multi-agent teams
    """

    def __init__(
        self,
        short_term_memory: RedisShortTermMemory | None = None,
        cache_ttl_seconds: int = 3600,
    ):
        """Initialize base wizard.

        Args:
            short_term_memory: Optional Redis memory for caching/sharing
            cache_ttl_seconds: Cache duration for analysis results (default 1 hour)

        """
        self.logger = logger
        self.short_term_memory = short_term_memory
        self.cache_ttl = cache_ttl_seconds

        # Create credentials for this wizard
        self._credentials = AgentCredentials(
            agent_id=f"wizard_{self.__class__.__name__}",
            tier=AccessTier.CONTRIBUTOR,
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Wizard name"""

    @property
    @abstractmethod
    def level(self) -> int:
        """Empathy level (1-5)"""

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze the given context and return results.

        Args:
            context: Dictionary with wizard-specific inputs

        Returns:
            Dictionary with:
            - predictions: List of Level 4 predictions
            - recommendations: List of actionable steps
            - confidence: Float 0.0-1.0
            - Additional wizard-specific data

        """

    # =========================================================================
    # SHORT-TERM MEMORY (Caching & Sharing)
    # =========================================================================

    def _cache_key(self, context: dict[str, Any]) -> str:
        """Generate a cache key from context."""
        # Create deterministic hash of context
        context_str = json.dumps(context, sort_keys=True, default=str)
        hash_val = hashlib.md5(context_str.encode(), usedforsecurity=False).hexdigest()[:12]
        return f"{self.name}:{hash_val}"

    def has_memory(self) -> bool:
        """Check if short-term memory is available."""
        return self.short_term_memory is not None

    def get_cached_result(self, context: dict[str, Any]) -> dict[str, Any] | None:
        """Get cached analysis result if available.

        Args:
            context: The analysis context (used for cache key)

        Returns:
            Cached result dict, or None if not cached

        """
        if self.short_term_memory is None:
            return None

        key = self._cache_key(context)
        result = self.short_term_memory.retrieve(key, self._credentials)
        return dict(result) if result else None

    def cache_result(self, context: dict[str, Any], result: dict[str, Any]) -> bool:
        """Cache analysis result for future reuse.

        Args:
            context: The analysis context (used for cache key)
            result: The analysis result to cache

        Returns:
            True if cached successfully

        """
        if self.short_term_memory is None:
            return False

        key = self._cache_key(context)
        return bool(self.short_term_memory.stash(key, result, self._credentials))

    async def analyze_with_cache(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze with automatic caching.

        First checks cache for existing result. If not found,
        runs analysis and caches the result.

        Args:
            context: Dictionary with wizard-specific inputs

        Returns:
            Analysis result (from cache or fresh)

        """
        # Try cache first
        cached = self.get_cached_result(context)
        if cached is not None:
            self.logger.debug(f"{self.name}: Using cached result")
            cached["_from_cache"] = True
            return cached

        # Run fresh analysis
        result = await self.analyze(context)
        result["_from_cache"] = False

        # Cache the result
        self.cache_result(context, result)

        return result

    def share_context(self, key: str, data: Any) -> bool:
        """Share context data for other wizards to use.

        Use this to pass intermediate results or discovered insights
        to subsequent wizards in a pipeline.

        Shared context uses a global namespace accessible to all wizards.

        Args:
            key: Unique key for this shared data
            data: Any JSON-serializable data

        Returns:
            True if shared successfully

        """
        if self.short_term_memory is None:
            return False

        # Use global credentials for shared context (accessible to all wizards)
        global_creds = AgentCredentials(
            agent_id="wizard_shared",
            tier=AccessTier.CONTRIBUTOR,
        )
        return bool(
            self.short_term_memory.stash(
                f"shared:{key}",
                data,
                global_creds,
            ),
        )

    def get_shared_context(self, key: str, from_wizard: str | None = None) -> Any | None:
        """Get context data shared by another wizard.

        If from_wizard is specified, looks in that wizard's private namespace.
        Otherwise, looks in the global shared namespace.

        Args:
            key: Key for the shared data
            from_wizard: Specific wizard to get from (e.g., "SecurityAnalysisWizard")
                        If None, uses global shared namespace.

        Returns:
            The shared data, or None if not found

        """
        if self.short_term_memory is None:
            return None

        # Use global shared namespace by default, or specific wizard if requested
        agent_id = f"wizard_{from_wizard}" if from_wizard else "wizard_shared"
        return self.short_term_memory.retrieve(
            f"shared:{key}",
            self._credentials,
            agent_id=agent_id,
        )

    def stage_discovered_pattern(
        self,
        pattern_id: str,
        pattern_type: str,
        name: str,
        description: str,
        confidence: float = 0.5,
        code: str | None = None,
    ) -> bool:
        """Stage a pattern discovered during analysis.

        When a wizard discovers a reusable pattern, it can stage it
        for validation and eventual promotion to the pattern library.

        Args:
            pattern_id: Unique pattern identifier
            pattern_type: Type (e.g., "security", "performance", "testing")
            name: Human-readable name
            description: What this pattern does
            confidence: Discovery confidence (0.0-1.0)
            code: Optional code example

        Returns:
            True if staged successfully

        """
        if self.short_term_memory is None:
            return False

        pattern = StagedPattern(
            pattern_id=pattern_id,
            agent_id=self._credentials.agent_id,
            pattern_type=pattern_type,
            name=name,
            description=description,
            confidence=confidence,
            code=code,
            context={"wizard": self.name, "level": self.level},
        )

        return bool(self.short_term_memory.stage_pattern(pattern, self._credentials))

    def send_signal(self, signal_type: str, data: dict) -> bool:
        """Send a coordination signal.

        Use to notify completion, request help, or broadcast status.

        Args:
            signal_type: Type of signal
            data: Signal payload

        Returns:
            True if sent successfully

        """
        if self.short_term_memory is None:
            return False

        return bool(
            self.short_term_memory.send_signal(
                signal_type=signal_type,
                data={"wizard": self.name, **data},
                credentials=self._credentials,
            ),
        )
