"""
Empathy Framework - AI-Human Collaboration Library

A five-level maturity model for building AI systems that progress from
reactive responses to anticipatory problem prevention.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

__version__ = "1.0.0-beta"
__author__ = "Smart AI Memory"
__email__ = "patrick.roebuck@smartaimemory.com"

from .config import EmpathyConfig, load_config
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
from .pattern_library import Pattern, PatternLibrary
from .persistence import MetricsCollector, PatternPersistence, StateManager
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
    "PatternLibrary",
    "Pattern",
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
