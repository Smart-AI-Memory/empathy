"""Redis Short-Term Memory for Empathy Framework

Per EMPATHY_PHILOSOPHY.md v1.1.0:
- Implements fast, TTL-based working memory for agent coordination
- Role-based access tiers for data integrity
- Pattern staging before validation
- Principled negotiation support

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


# Import AccessTier from the canonical location to avoid duplicate enums
from .memory.short_term import AccessTier


class TTLStrategy(Enum):
    """TTL strategies for different memory types

    Per EMPATHY_PHILOSOPHY.md Section 9.3:
    - Working results: 1 hour
    - Staged patterns: 24 hours
    - Coordination signals: 5 minutes
    - Conflict context: Until resolution
    """

    WORKING_RESULTS = 3600  # 1 hour
    STAGED_PATTERNS = 86400  # 24 hours
    COORDINATION = 300  # 5 minutes
    CONFLICT_CONTEXT = 604800  # 7 days (fallback for unresolved)
    SESSION = 1800  # 30 minutes


@dataclass
class AgentCredentials:
    """Agent identity and access permissions"""

    agent_id: str
    tier: AccessTier
    roles: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)

    def can_read(self) -> bool:
        """All tiers can read"""
        return True

    def can_stage(self) -> bool:
        """Contributor+ can stage patterns"""
        return self.tier.value >= AccessTier.CONTRIBUTOR.value

    def can_validate(self) -> bool:
        """Validator+ can promote patterns"""
        return self.tier.value >= AccessTier.VALIDATOR.value

    def can_administer(self) -> bool:
        """Only Stewards have full admin access"""
        return self.tier.value >= AccessTier.STEWARD.value


@dataclass
class StagedPattern:
    """Pattern awaiting validation"""

    pattern_id: str
    agent_id: str
    pattern_type: str
    name: str
    description: str
    code: str | None = None
    context: dict = field(default_factory=dict)
    confidence: float = 0.5
    staged_at: datetime = field(default_factory=datetime.now)
    interests: list[str] = field(default_factory=list)  # For negotiation

    def to_dict(self) -> dict:
        return {
            "pattern_id": self.pattern_id,
            "agent_id": self.agent_id,
            "pattern_type": self.pattern_type,
            "name": self.name,
            "description": self.description,
            "code": self.code,
            "context": self.context,
            "confidence": self.confidence,
            "staged_at": self.staged_at.isoformat(),
            "interests": self.interests,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "StagedPattern":
        return cls(
            pattern_id=data["pattern_id"],
            agent_id=data["agent_id"],
            pattern_type=data["pattern_type"],
            name=data["name"],
            description=data["description"],
            code=data.get("code"),
            context=data.get("context", {}),
            confidence=data.get("confidence", 0.5),
            staged_at=datetime.fromisoformat(data["staged_at"]),
            interests=data.get("interests", []),
        )


@dataclass
class ConflictContext:
    """Context for principled negotiation

    Per Getting to Yes framework:
    - Positions: What each party says they want
    - Interests: Why they want it (underlying needs)
    - BATNA: Best Alternative to Negotiated Agreement
    """

    conflict_id: str
    positions: dict[str, Any]  # agent_id -> stated position
    interests: dict[str, list[str]]  # agent_id -> underlying interests
    batna: str | None = None  # Fallback strategy
    created_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution: str | None = None

    def to_dict(self) -> dict:
        return {
            "conflict_id": self.conflict_id,
            "positions": self.positions,
            "interests": self.interests,
            "batna": self.batna,
            "created_at": self.created_at.isoformat(),
            "resolved": self.resolved,
            "resolution": self.resolution,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ConflictContext":
        return cls(
            conflict_id=data["conflict_id"],
            positions=data["positions"],
            interests=data["interests"],
            batna=data.get("batna"),
            created_at=datetime.fromisoformat(data["created_at"]),
            resolved=data.get("resolved", False),
            resolution=data.get("resolution"),
        )


class RedisShortTermMemory:
    """Redis-backed short-term memory for agent coordination

    Features:
    - Fast read/write with automatic TTL expiration
    - Role-based access control
    - Pattern staging workflow
    - Conflict negotiation context
    - Agent working memory

    Example:
        >>> memory = RedisShortTermMemory()
        >>> creds = AgentCredentials("agent_1", AccessTier.CONTRIBUTOR)
        >>> memory.stash("analysis_results", {"issues": 3}, creds)
        >>> data = memory.retrieve("analysis_results", creds)

    """

    # Key prefixes for namespacing
    PREFIX_WORKING = "empathy:working:"
    PREFIX_STAGED = "empathy:staged:"
    PREFIX_CONFLICT = "empathy:conflict:"
    PREFIX_COORDINATION = "empathy:coord:"
    PREFIX_SESSION = "empathy:session:"

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        use_mock: bool = False,
    ):
        """Initialize Redis connection

        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            use_mock: Use in-memory mock for testing

        """
        self.use_mock = use_mock or not REDIS_AVAILABLE

        if self.use_mock:
            self._mock_storage: dict[str, tuple[Any, float | None]] = {}
            self._client = None
        else:
            self._client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,
            )

    def _get(self, key: str) -> str | None:
        """Get value from Redis or mock"""
        if self.use_mock:
            if key in self._mock_storage:
                value, expires = self._mock_storage[key]
                if expires is None or datetime.now().timestamp() < expires:
                    return str(value) if value is not None else None
                del self._mock_storage[key]
            return None
        if self._client is None:
            return None
        result = self._client.get(key)
        return str(result) if result else None

    def _set(self, key: str, value: str, ttl: int | None = None) -> bool:
        """Set value in Redis or mock"""
        if self.use_mock:
            expires = datetime.now().timestamp() + ttl if ttl else None
            self._mock_storage[key] = (value, expires)
            return True
        if self._client is None:
            return False
        if ttl:
            self._client.setex(key, ttl, value)
            return True
        result = self._client.set(key, value)
        return bool(result)

    def _delete(self, key: str) -> bool:
        """Delete key from Redis or mock"""
        if self.use_mock:
            if key in self._mock_storage:
                del self._mock_storage[key]
                return True
            return False
        if self._client is None:
            return False
        return self._client.delete(key) > 0

    def _keys(self, pattern: str) -> list[str]:
        """Get keys matching pattern"""
        if self.use_mock:
            import fnmatch

            return [k for k in self._mock_storage.keys() if fnmatch.fnmatch(k, pattern)]
        if self._client is None:
            return []
        keys = self._client.keys(pattern)
        return [k.decode() if isinstance(k, bytes) else str(k) for k in keys]

    # === Working Memory (Stash/Retrieve) ===

    def stash(
        self,
        key: str,
        data: Any,
        credentials: AgentCredentials,
        ttl: TTLStrategy = TTLStrategy.WORKING_RESULTS,
    ) -> bool:
        """Stash data in short-term memory

        Args:
            key: Unique key for the data
            data: Data to store (will be JSON serialized)
            credentials: Agent credentials
            ttl: Time-to-live strategy

        Returns:
            True if successful

        Example:
            >>> memory.stash("analysis_v1", {"findings": [...]}, creds)

        """
        if not credentials.can_stage():
            raise PermissionError(
                f"Agent {credentials.agent_id} (Tier {credentials.tier.name}) "
                "cannot write to memory. Requires CONTRIBUTOR or higher.",
            )

        full_key = f"{self.PREFIX_WORKING}{credentials.agent_id}:{key}"
        payload = {
            "data": data,
            "agent_id": credentials.agent_id,
            "stashed_at": datetime.now().isoformat(),
        }
        return self._set(full_key, json.dumps(payload), ttl.value)

    def retrieve(
        self,
        key: str,
        credentials: AgentCredentials,
        agent_id: str | None = None,
    ) -> Any | None:
        """Retrieve data from short-term memory

        Args:
            key: Key to retrieve
            credentials: Agent credentials
            agent_id: Owner agent ID (defaults to credentials agent)

        Returns:
            Retrieved data or None if not found

        Example:
            >>> data = memory.retrieve("analysis_v1", creds)

        """
        owner = agent_id or credentials.agent_id
        full_key = f"{self.PREFIX_WORKING}{owner}:{key}"
        raw = self._get(full_key)

        if raw is None:
            return None

        payload = json.loads(raw)
        return payload.get("data")

    def clear_working_memory(self, credentials: AgentCredentials) -> int:
        """Clear all working memory for an agent

        Args:
            credentials: Agent credentials (must own the memory or be Steward)

        Returns:
            Number of keys deleted

        """
        pattern = f"{self.PREFIX_WORKING}{credentials.agent_id}:*"
        keys = self._keys(pattern)
        count = 0
        for key in keys:
            if self._delete(key):
                count += 1
        return count

    # === Pattern Staging ===

    def stage_pattern(
        self,
        pattern: StagedPattern,
        credentials: AgentCredentials,
    ) -> bool:
        """Stage a pattern for validation

        Per EMPATHY_PHILOSOPHY.md: Patterns must be staged before
        being promoted to the active library.

        Args:
            pattern: Pattern to stage
            credentials: Must be CONTRIBUTOR or higher

        Returns:
            True if staged successfully

        """
        if not credentials.can_stage():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot stage patterns. "
                "Requires CONTRIBUTOR tier or higher.",
            )

        key = f"{self.PREFIX_STAGED}{pattern.pattern_id}"
        return self._set(
            key,
            json.dumps(pattern.to_dict()),
            TTLStrategy.STAGED_PATTERNS.value,
        )

    def get_staged_pattern(
        self,
        pattern_id: str,
        credentials: AgentCredentials,
    ) -> StagedPattern | None:
        """Retrieve a staged pattern

        Args:
            pattern_id: Pattern ID
            credentials: Any tier can read

        Returns:
            StagedPattern or None

        """
        key = f"{self.PREFIX_STAGED}{pattern_id}"
        raw = self._get(key)

        if raw is None:
            return None

        return StagedPattern.from_dict(json.loads(raw))

    def list_staged_patterns(
        self,
        credentials: AgentCredentials,
    ) -> list[StagedPattern]:
        """List all staged patterns awaiting validation

        Args:
            credentials: Any tier can read

        Returns:
            List of staged patterns

        """
        pattern = f"{self.PREFIX_STAGED}*"
        keys = self._keys(pattern)
        patterns = []

        for key in keys:
            raw = self._get(key)
            if raw:
                patterns.append(StagedPattern.from_dict(json.loads(raw)))

        return patterns

    def promote_pattern(
        self,
        pattern_id: str,
        credentials: AgentCredentials,
    ) -> StagedPattern | None:
        """Promote staged pattern (remove from staging for library add)

        Args:
            pattern_id: Pattern to promote
            credentials: Must be VALIDATOR or higher

        Returns:
            The promoted pattern (for adding to PatternLibrary)

        """
        if not credentials.can_validate():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot promote patterns. "
                "Requires VALIDATOR tier or higher.",
            )

        pattern = self.get_staged_pattern(pattern_id, credentials)
        if pattern:
            key = f"{self.PREFIX_STAGED}{pattern_id}"
            self._delete(key)
        return pattern

    def reject_pattern(
        self,
        pattern_id: str,
        credentials: AgentCredentials,
        reason: str = "",
    ) -> bool:
        """Reject a staged pattern

        Args:
            pattern_id: Pattern to reject
            credentials: Must be VALIDATOR or higher
            reason: Rejection reason (for audit)

        Returns:
            True if rejected

        """
        if not credentials.can_validate():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot reject patterns. "
                "Requires VALIDATOR tier or higher.",
            )

        key = f"{self.PREFIX_STAGED}{pattern_id}"
        return self._delete(key)

    # === Conflict Negotiation ===

    def create_conflict_context(
        self,
        conflict_id: str,
        positions: dict[str, Any],
        interests: dict[str, list[str]],
        credentials: AgentCredentials,
        batna: str | None = None,
    ) -> ConflictContext:
        """Create context for principled negotiation

        Per Getting to Yes framework:
        - Separate positions from interests
        - Define BATNA before negotiating

        Args:
            conflict_id: Unique conflict identifier
            positions: agent_id -> their stated position
            interests: agent_id -> underlying interests
            credentials: Must be CONTRIBUTOR or higher
            batna: Best Alternative to Negotiated Agreement

        Returns:
            ConflictContext for resolution

        """
        if not credentials.can_stage():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot create conflict context. "
                "Requires CONTRIBUTOR tier or higher.",
            )

        context = ConflictContext(
            conflict_id=conflict_id,
            positions=positions,
            interests=interests,
            batna=batna,
        )

        key = f"{self.PREFIX_CONFLICT}{conflict_id}"
        self._set(
            key,
            json.dumps(context.to_dict()),
            TTLStrategy.CONFLICT_CONTEXT.value,
        )

        return context

    def get_conflict_context(
        self,
        conflict_id: str,
        credentials: AgentCredentials,
    ) -> ConflictContext | None:
        """Retrieve conflict context

        Args:
            conflict_id: Conflict identifier
            credentials: Any tier can read

        Returns:
            ConflictContext or None

        """
        key = f"{self.PREFIX_CONFLICT}{conflict_id}"
        raw = self._get(key)

        if raw is None:
            return None

        return ConflictContext.from_dict(json.loads(raw))

    def resolve_conflict(
        self,
        conflict_id: str,
        resolution: str,
        credentials: AgentCredentials,
    ) -> bool:
        """Mark conflict as resolved

        Args:
            conflict_id: Conflict to resolve
            resolution: How it was resolved
            credentials: Must be VALIDATOR or higher

        Returns:
            True if resolved

        """
        if not credentials.can_validate():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot resolve conflicts. "
                "Requires VALIDATOR tier or higher.",
            )

        context = self.get_conflict_context(conflict_id, credentials)
        if context is None:
            return False

        context.resolved = True
        context.resolution = resolution

        key = f"{self.PREFIX_CONFLICT}{conflict_id}"
        # Keep resolved conflicts longer for audit
        self._set(key, json.dumps(context.to_dict()), TTLStrategy.CONFLICT_CONTEXT.value)
        return True

    # === Coordination Signals ===

    def send_signal(
        self,
        signal_type: str,
        data: Any,
        credentials: AgentCredentials,
        target_agent: str | None = None,
    ) -> bool:
        """Send coordination signal to other agents

        Args:
            signal_type: Type of signal (e.g., "ready", "blocking", "complete")
            data: Signal payload
            credentials: Must be CONTRIBUTOR or higher
            target_agent: Specific agent to signal (None = broadcast)

        Returns:
            True if sent

        """
        if not credentials.can_stage():
            raise PermissionError(
                f"Agent {credentials.agent_id} cannot send signals. "
                "Requires CONTRIBUTOR tier or higher.",
            )

        target = target_agent or "broadcast"
        key = f"{self.PREFIX_COORDINATION}{signal_type}:{credentials.agent_id}:{target}"
        payload = {
            "signal_type": signal_type,
            "from_agent": credentials.agent_id,
            "to_agent": target_agent,
            "data": data,
            "sent_at": datetime.now().isoformat(),
        }
        return self._set(key, json.dumps(payload), TTLStrategy.COORDINATION.value)

    def receive_signals(
        self,
        credentials: AgentCredentials,
        signal_type: str | None = None,
    ) -> list[dict]:
        """Receive coordination signals

        Args:
            credentials: Agent receiving signals
            signal_type: Filter by signal type (optional)

        Returns:
            List of signals

        """
        if signal_type:
            pattern = f"{self.PREFIX_COORDINATION}{signal_type}:*:{credentials.agent_id}"
        else:
            pattern = f"{self.PREFIX_COORDINATION}*:{credentials.agent_id}"

        # Also get broadcasts
        broadcast_pattern = f"{self.PREFIX_COORDINATION}*:*:broadcast"

        keys = set(self._keys(pattern)) | set(self._keys(broadcast_pattern))
        signals = []

        for key in keys:
            raw = self._get(key)
            if raw:
                signals.append(json.loads(raw))

        return signals

    # === Session Management ===

    def create_session(
        self,
        session_id: str,
        credentials: AgentCredentials,
        metadata: dict | None = None,
    ) -> bool:
        """Create a collaboration session

        Args:
            session_id: Unique session identifier
            credentials: Session creator
            metadata: Optional session metadata

        Returns:
            True if created

        """
        key = f"{self.PREFIX_SESSION}{session_id}"
        payload = {
            "session_id": session_id,
            "created_by": credentials.agent_id,
            "created_at": datetime.now().isoformat(),
            "participants": [credentials.agent_id],
            "metadata": metadata or {},
        }
        return self._set(key, json.dumps(payload), TTLStrategy.SESSION.value)

    def join_session(
        self,
        session_id: str,
        credentials: AgentCredentials,
    ) -> bool:
        """Join an existing session

        Args:
            session_id: Session to join
            credentials: Joining agent

        Returns:
            True if joined

        """
        key = f"{self.PREFIX_SESSION}{session_id}"
        raw = self._get(key)

        if raw is None:
            return False

        payload = json.loads(raw)
        if credentials.agent_id not in payload["participants"]:
            payload["participants"].append(credentials.agent_id)

        return self._set(key, json.dumps(payload), TTLStrategy.SESSION.value)

    def get_session(
        self,
        session_id: str,
        credentials: AgentCredentials,
    ) -> dict | None:
        """Get session information

        Args:
            session_id: Session identifier
            credentials: Any participant can read

        Returns:
            Session data or None

        """
        key = f"{self.PREFIX_SESSION}{session_id}"
        raw = self._get(key)

        if raw is None:
            return None

        result: dict = json.loads(raw)
        return result

    # === Health Check ===

    def ping(self) -> bool:
        """Check Redis connection health

        Returns:
            True if connected and responsive

        """
        if self.use_mock:
            return True
        if self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get_stats(self) -> dict:
        """Get memory statistics

        Returns:
            Dict with memory stats

        """
        if self.use_mock:
            return {
                "mode": "mock",
                "total_keys": len(self._mock_storage),
                "working_keys": len(
                    [k for k in self._mock_storage if k.startswith(self.PREFIX_WORKING)],
                ),
                "staged_keys": len(
                    [k for k in self._mock_storage if k.startswith(self.PREFIX_STAGED)],
                ),
                "conflict_keys": len(
                    [k for k in self._mock_storage if k.startswith(self.PREFIX_CONFLICT)],
                ),
            }

        if self._client is None:
            return {"mode": "disconnected", "error": "No Redis client"}
        info = self._client.info("memory")
        return {
            "mode": "redis",
            "used_memory": info.get("used_memory_human"),
            "peak_memory": info.get("used_memory_peak_human"),
            "total_keys": self._client.dbsize(),
            "working_keys": len(self._keys(f"{self.PREFIX_WORKING}*")),
            "staged_keys": len(self._keys(f"{self.PREFIX_STAGED}*")),
            "conflict_keys": len(self._keys(f"{self.PREFIX_CONFLICT}*")),
        }
