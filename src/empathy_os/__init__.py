"""
Empathy Framework - AI-Human Collaboration Library

A five-level maturity model for building AI systems that progress from
reactive responses to anticipatory problem prevention.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

__version__ = "1.0.0-beta"
__author__ = "Patrick Roebuck"
__email__ = "hello@deepstudy.ai"

from .config import EmpathyConfig, load_config
from .coordination import ConflictResolver, ResolutionResult, ResolutionStrategy, TeamPriorities
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
from .monitoring import AgentMetrics, AgentMonitor, TeamMetrics
from .pattern_library import Pattern, PatternLibrary, PatternMatch
from .persistence import MetricsCollector, PatternPersistence, StateManager
from .redis_memory import (
    AccessTier,
    AgentCredentials,
    ConflictContext,
    RedisShortTermMemory,
    StagedPattern,
    TTLStrategy,
)
from .trust_building import TrustBuildingBehaviors

__all__ = [
    "EmpathyOS",
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
]
