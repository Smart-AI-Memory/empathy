"""Core pattern models for the Wizard Factory Pattern Library.

This module provides the base classes and enums used by all wizard patterns.
Patterns are extracted from 78 existing wizards and encoded as Pydantic models
for type safety, validation, and code generation.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class PatternCategory(str, Enum):
    """Categories of wizard patterns."""

    STRUCTURAL = "structural"
    INPUT = "input"
    VALIDATION = "validation"
    BEHAVIOR = "behavior"
    EMPATHY = "empathy"


class BasePattern(BaseModel):
    """Base class for all wizard patterns.

    All wizard patterns inherit from this base class, providing:
    - Unique identification
    - Categorization
    - Reusability metrics
    - Examples of usage in existing wizards
    """

    id: str = Field(..., description="Unique pattern identifier (e.g., 'linear_flow')")
    name: str = Field(..., description="Human-readable pattern name")
    category: PatternCategory = Field(..., description="Pattern category")
    description: str = Field(..., description="Detailed pattern description")
    frequency: int = Field(..., description="Number of wizards using this pattern", ge=0)
    reusability_score: float = Field(
        ...,
        description="Reusability score (0.0-1.0)",
        ge=0.0,
        le=1.0,
    )
    examples: list[str] = Field(
        default_factory=list,
        description="List of wizard IDs using this pattern",
    )

    class Config:
        """Pydantic config."""

        use_enum_values = True

    def to_dict(self) -> dict[str, Any]:
        """Convert pattern to dictionary."""
        return self.model_dump()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BasePattern":
        """Create pattern from dictionary."""
        return cls(**data)


class CodeGeneratorMixin:
    """Mixin for patterns that can generate code."""

    def generate_code(self) -> str:
        """Generate code from this pattern.

        Returns:
            Generated code as a string

        Raises:
            NotImplementedError: If code generation is not implemented

        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement code generation")


class ValidationMixin:
    """Mixin for patterns that can validate wizard configurations."""

    def validate_config(self, config: dict[str, Any]) -> tuple[bool, list[str]]:
        """Validate a wizard configuration against this pattern.

        Args:
            config: Wizard configuration to validate

        Returns:
            Tuple of (is_valid, list_of_errors)

        """
        raise NotImplementedError(f"{self.__class__.__name__} does not implement validation")
