"""Wizard Factory Pattern Library.

This package provides a comprehensive pattern library for creating wizards
in the Empathy Framework. Patterns are extracted from 78 existing wizards
and encoded as Pydantic models for type safety and code generation.

**Pattern Categories:**
- Structural: Overall wizard flow and architecture
- Input: Data collection patterns
- Validation: Data validation and approval patterns
- Behavior: Wizard behavior and capabilities
- Empathy: User experience and empathy patterns

**Usage:**
    from patterns import get_pattern_registry, LinearFlowPattern

    # Get pattern registry
    registry = get_pattern_registry()

    # Search for patterns
    patterns = registry.search("linear")

    # Get pattern by ID
    pattern = registry.get("linear_flow")

    # Generate code from pattern
    code = pattern.generate_code()

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .behavior import (
                       AIEnhancementPattern,
                       FixApplicationPattern,
                       PredictionPattern,
                       RiskAssessmentPattern,
                       RiskLevel,
)
from .core import BasePattern, CodeGeneratorMixin, PatternCategory, ValidationMixin
from .empathy import EducationalBannerPattern, EmpathyLevelPattern, UserGuidancePattern
from .input import (
                       CodeAnalysisPattern,
                       ContextBasedPattern,
                       FieldDefinition,
                       StructuredFieldsPattern,
)
from .registry import PatternRegistry, get_pattern_registry, load_patterns
from .structural import (
                       LinearFlowPattern,
                       PhaseConfig,
                       PhasedProcessingPattern,
                       SessionBasedPattern,
                       StepConfig,
)
from .validation import ApprovalPattern, ConfigValidationPattern, StepValidationPattern

__all__ = [
    # Core
    "BasePattern",
    "PatternCategory",
    "CodeGeneratorMixin",
    "ValidationMixin",
    # Structural
    "StepConfig",
    "LinearFlowPattern",
    "PhaseConfig",
    "PhasedProcessingPattern",
    "SessionBasedPattern",
    # Input
    "FieldDefinition",
    "StructuredFieldsPattern",
    "CodeAnalysisPattern",
    "ContextBasedPattern",
    # Validation
    "ConfigValidationPattern",
    "StepValidationPattern",
    "ApprovalPattern",
    # Behavior
    "RiskLevel",
    "RiskAssessmentPattern",
    "AIEnhancementPattern",
    "PredictionPattern",
    "FixApplicationPattern",
    # Empathy
    "EmpathyLevelPattern",
    "EducationalBannerPattern",
    "UserGuidancePattern",
    # Registry
    "PatternRegistry",
    "get_pattern_registry",
    "load_patterns",
]

__version__ = "1.0.0"
