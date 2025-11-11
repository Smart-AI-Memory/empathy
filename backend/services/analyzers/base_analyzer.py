"""
Base analyzer module for the Empathy Framework.
Provides foundational classes for issue detection and analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any


class IssueSeverity(Enum):
    """Severity levels for detected issues."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Issue:
    """Represents a detected issue in code or system."""

    title: str
    description: str
    severity: IssueSeverity
    file_path: str | None = None
    line_number: int | None = None
    category: str | None = None
    recommendations: list[str] = None
    confidence: float = 0.0

    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary format."""
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "category": self.category,
            "recommendations": self.recommendations,
            "confidence": self.confidence,
        }


class BaseAnalyzer(ABC):
    """Abstract base class for all analyzers."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Analyzer name."""
        pass

    @property
    @abstractmethod
    def level(self) -> int:
        """Empathy level (1-5)."""
        pass

    @abstractmethod
    async def analyze(self, context: dict[str, Any]) -> list[Issue]:
        """Perform analysis and return detected issues."""
        pass

    def _create_issue(
        self, title: str, description: str, severity: IssueSeverity, **kwargs
    ) -> Issue:
        """Helper method to create an issue."""
        return Issue(title=title, description=description, severity=severity, **kwargs)
