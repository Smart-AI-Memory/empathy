"""
Empathy Framework Memory Module

Unified two-tier memory system for AI agent collaboration:

SHORT-TERM MEMORY (Redis):
    - Agent coordination and working memory
    - TTL-based automatic expiration (5 min - 7 days)
    - Role-based access control (Observer → Steward)
    - Pattern staging before validation

LONG-TERM MEMORY (Persistent):
    - Cross-session pattern storage
    - Classification-based access (PUBLIC/INTERNAL/SENSITIVE)
    - PII scrubbing and secrets detection
    - AES-256-GCM encryption for SENSITIVE patterns
    - Compliance: GDPR, HIPAA, SOC2

RECOMMENDED USAGE (Unified API):
    from empathy_os.memory import UnifiedMemory

    # Initialize with environment auto-detection
    memory = UnifiedMemory(user_id="agent@company.com")

    # Short-term operations
    memory.stash("working_data", {"key": "value"})
    data = memory.retrieve("working_data")

    # Long-term operations
    result = memory.persist_pattern(
        content="Algorithm for X",
        pattern_type="algorithm",
    )
    pattern = memory.recall_pattern(result["pattern_id"])

    # Pattern promotion (short-term → long-term)
    staged_id = memory.stage_pattern({"content": "..."})
    memory.promote_pattern(staged_id)

ADVANCED USAGE (Direct Access):
    from empathy_os.memory import (
        # Short-term (Redis)
        RedisShortTermMemory,
        AccessTier,
        get_redis_memory,

        # Long-term (Persistent)
        SecureMemDocsIntegration,
        Classification,

        # Security
        PIIScrubber,
        SecretsDetector,
        AuditLogger,
    )

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

# Short-term memory (Redis)
# Claude Memory integration
from .claude_memory import ClaudeMemoryConfig, ClaudeMemoryLoader

# Memory configuration
from .config import check_redis_connection, get_railway_redis, get_redis_config, get_redis_memory

# Control Panel
from .control_panel import ControlPanelConfig, MemoryControlPanel, MemoryStats

# Memory Graph (Cross-Wizard Intelligence)
from .edges import REVERSE_EDGE_TYPES, WIZARD_EDGE_PATTERNS, Edge, EdgeType
from .graph import MemoryGraph

# Long-term memory (Persistent patterns)
from .long_term import (
    Classification,
    ClassificationRules,
    EncryptionManager,
    MemDocsStorage,
    PatternMetadata,
    SecureMemDocsIntegration,
    SecurePattern,
    SecurityError,
)
from .long_term import PermissionError as MemoryPermissionError
from .nodes import (
    BugNode,
    Node,
    NodeType,
    PatternNode,
    PerformanceNode,
    VulnerabilityNode,
)

# Redis Bootstrap
from .redis_bootstrap import (
    RedisStartMethod,
    RedisStatus,
    ensure_redis,
    get_redis_or_mock,
    stop_redis,
)

# Security components
from .security import (  # Audit Logging; PII Scrubbing; Secrets Detection
    AuditEvent,
    AuditLogger,
    PIIDetection,
    PIIPattern,
    PIIScrubber,
    SecretDetection,
    SecretsDetector,
    SecretType,
    SecurityViolation,
    Severity,
    detect_secrets,
)
from .short_term import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    RedisShortTermMemory,
    StagedPattern,
    TTLStrategy,
)

# Conversation Summary Index
from .summary_index import AgentContext, ConversationSummaryIndex

# Unified memory interface
from .unified import Environment, MemoryConfig, UnifiedMemory

__all__ = [
    # Unified Memory Interface (recommended)
    "UnifiedMemory",
    "MemoryConfig",
    "Environment",
    # Redis Bootstrap
    "ensure_redis",
    "get_redis_or_mock",
    "stop_redis",
    "RedisStartMethod",
    "RedisStatus",
    # Control Panel
    "MemoryControlPanel",
    "ControlPanelConfig",
    "MemoryStats",
    # Short-term Memory
    "RedisShortTermMemory",
    "AccessTier",
    "AgentCredentials",
    "StagedPattern",
    "ConflictContext",
    "TTLStrategy",
    # Configuration
    "get_redis_memory",
    "get_redis_config",
    "get_railway_redis",
    "check_redis_connection",
    # Long-term Memory
    "SecureMemDocsIntegration",
    "Classification",
    "ClassificationRules",
    "PatternMetadata",
    "SecurePattern",
    "MemDocsStorage",
    "EncryptionManager",
    "SecurityError",
    "MemoryPermissionError",
    # Claude Memory
    "ClaudeMemoryConfig",
    "ClaudeMemoryLoader",
    # Security - PII
    "PIIScrubber",
    "PIIDetection",
    "PIIPattern",
    # Security - Secrets
    "SecretsDetector",
    "SecretDetection",
    "SecretType",
    "Severity",
    "detect_secrets",
    # Security - Audit
    "AuditLogger",
    "AuditEvent",
    "SecurityViolation",
    # Conversation Summary Index
    "ConversationSummaryIndex",
    "AgentContext",
    # Memory Graph (Cross-Wizard Intelligence)
    "MemoryGraph",
    "Node",
    "NodeType",
    "BugNode",
    "VulnerabilityNode",
    "PerformanceNode",
    "PatternNode",
    "Edge",
    "EdgeType",
    "REVERSE_EDGE_TYPES",
    "WIZARD_EDGE_PATTERNS",
]
