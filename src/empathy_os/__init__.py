"""
Empathy Framework - AI-Human Collaboration Library

A five-level maturity model for building AI systems that progress from
reactive responses to anticipatory problem prevention.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

__version__ = "1.0.0-beta"
__author__ = "Patrick Roebuck"
__email__ = "hello@deepstudy.ai"

from .core import EmpathyOS
from .emergence import EmergenceDetector
from .exceptions import (
    EmpathyFrameworkError,
    ValidationError,
    PatternNotFoundError,
    TrustThresholdError,
    ConfidenceThresholdError,
    EmpathyLevelError,
    LeveragePointError,
    FeedbackLoopError,
    CollaborationStateError,
)
from .feedback_loops import FeedbackLoopDetector
from .levels import (
    Level1Reactive,
    Level2Guided,
    Level3Proactive,
    Level4Anticipatory,
    Level5Systems,
)
from .leverage_points import LeveragePointAnalyzer
from .pattern_library import Pattern, PatternLibrary
from .persistence import PatternPersistence, StateManager, MetricsCollector
from .trust_building import TrustBuildingBehaviors
from .config import EmpathyConfig, load_config

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
