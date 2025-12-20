"""
Empathy Framework - AI-Human Collaboration Library

A five-level maturity model for building AI systems that progress from
reactive responses to anticipatory problem prevention.

QUICK START:
    from empathy_os import EmpathyOS

    # Create an EmpathyOS instance
    empathy = EmpathyOS(user_id="developer@company.com")

    # Use Level 4 (Anticipatory) for predictions
    response = empathy.level_4_anticipatory(
        user_input="How do I optimize database queries?",
        context={"domain": "software"},
        history=[]
    )

    print(f"Response: {response['response']}")
    print(f"Predictions: {response.get('predictions', [])}")

    # Store patterns in memory
    empathy.stash("session_context", {"topic": "database optimization"})
    empathy.persist_pattern(
        content="Query optimization technique",
        pattern_type="technique"
    )

MEMORY OPERATIONS:
    from empathy_os import UnifiedMemory, Classification

    # Initialize unified memory (auto-detects environment)
    memory = UnifiedMemory(user_id="agent@company.com")

    # Short-term (Redis-backed, TTL-based)
    memory.stash("working_data", {"status": "processing"})
    data = memory.retrieve("working_data")

    # Long-term (persistent, classified)
    result = memory.persist_pattern(
        content="Optimization algorithm for X",
        pattern_type="algorithm",
        classification=Classification.INTERNAL,
    )
    pattern = memory.recall_pattern(result["pattern_id"])

KEY EXPORTS:
    - EmpathyOS: Main orchestration class
    - UnifiedMemory: Two-tier memory (short + long term)
    - MemoryConfig, Environment: Memory configuration
    - Classification, AccessTier: Security/access enums
    - Level1-5 classes: Empathy level implementations

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

__version__ = "1.0.0-beta"
__author__ = "Patrick Roebuck"
__email__ = "hello@deepstudy.ai"

from .config import EmpathyConfig, load_config
from .coordination import (
    AgentCoordinator,
    AgentTask,
    ConflictResolver,
    ResolutionResult,
    ResolutionStrategy,
    TeamPriorities,
    TeamSession,
)
from .core import EmpathyOS
from .emergence import EmergenceDetector
from .exceptions import (
    CollaborationStateError,
    ConfidenceThresholdError,
    EmpathyFrameworkError,
    EmpathyLevelError,
    FeedbackLoopError,
    LeveragePointError,
    PatternNotFoundError,
    TrustThresholdError,
    ValidationError,
)
from .feedback_loops import FeedbackLoopDetector
from .levels import Level1Reactive, Level2Guided, Level3Proactive, Level4Anticipatory, Level5Systems
from .leverage_points import LeveragePointAnalyzer
from .logging_config import LoggingConfig, get_logger

# Memory module (unified short-term + long-term + security)
from .memory import (  # Short-term (Redis); Security - Audit; Claude Memory; Security - PII; Security - Secrets; Long-term (Persistent); Unified Memory Interface (recommended); Configuration
    AccessTier,
    AgentCredentials,
    AuditEvent,
    AuditLogger,
    Classification,
    ClassificationRules,
    ClaudeMemoryConfig,
    ClaudeMemoryLoader,
    ConflictContext,
    EncryptionManager,
    Environment,
    MemDocsStorage,
    MemoryConfig,
    MemoryPermissionError,
    PatternMetadata,
    PIIDetection,
    PIIPattern,
    PIIScrubber,
    RedisShortTermMemory,
    SecretDetection,
    SecretsDetector,
    SecretType,
    SecureMemDocsIntegration,
    SecurePattern,
    SecurityError,
    SecurityViolation,
    Severity,
    StagedPattern,
    TTLStrategy,
    UnifiedMemory,
    check_redis_connection,
    detect_secrets,
    get_railway_redis,
    get_redis_config,
    get_redis_memory,
)
from .monitoring import AgentMetrics, AgentMonitor, TeamMetrics
from .pattern_library import Pattern, PatternLibrary, PatternMatch
from .persistence import MetricsCollector, PatternPersistence, StateManager
from .trust_building import TrustBuildingBehaviors

__all__ = [
    "EmpathyOS",
    # Unified Memory Interface
    "UnifiedMemory",
    "MemoryConfig",
    "Environment",
    "Level1Reactive",
    "Level2Guided",
    "Level3Proactive",
    "Level4Anticipatory",
    "Level5Systems",
    "FeedbackLoopDetector",
    "LeveragePointAnalyzer",
    "EmergenceDetector",
    # Pattern Library
    "PatternLibrary",
    "Pattern",
    "PatternMatch",
    # Coordination (Multi-Agent)
    "ConflictResolver",
    "ResolutionResult",
    "ResolutionStrategy",
    "TeamPriorities",
    "AgentCoordinator",
    "AgentTask",
    "TeamSession",
    # Monitoring (Multi-Agent)
    "AgentMonitor",
    "AgentMetrics",
    "TeamMetrics",
    # Redis Short-Term Memory
    "RedisShortTermMemory",
    "AccessTier",
    "AgentCredentials",
    "StagedPattern",
    "ConflictContext",
    "TTLStrategy",
    # Redis Configuration
    "get_redis_memory",
    "get_redis_config",
    "get_railway_redis",
    "check_redis_connection",
    # Trust
    "TrustBuildingBehaviors",
    # Persistence
    "PatternPersistence",
    "StateManager",
    "MetricsCollector",
    # Configuration
    "EmpathyConfig",
    "load_config",
    # Logging
    "get_logger",
    "LoggingConfig",
    # Exceptions
    "EmpathyFrameworkError",
    "ValidationError",
    "PatternNotFoundError",
    "TrustThresholdError",
    "ConfidenceThresholdError",
    "EmpathyLevelError",
    "LeveragePointError",
    "FeedbackLoopError",
    "CollaborationStateError",
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
]
