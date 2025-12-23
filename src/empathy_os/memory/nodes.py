"""
Memory Graph Node Types

Defines node types for the cross-wizard knowledge graph.
Each node represents an entity discovered by a wizard.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class NodeType(Enum):
    """Types of nodes in the memory graph."""

    # Code entities
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"

    # Issues and findings
    BUG = "bug"
    VULNERABILITY = "vulnerability"
    PERFORMANCE_ISSUE = "performance_issue"
    CODE_SMELL = "code_smell"
    TECH_DEBT = "tech_debt"

    # Solutions and patterns
    PATTERN = "pattern"
    FIX = "fix"
    REFACTOR = "refactor"

    # Testing
    TEST = "test"
    TEST_CASE = "test_case"
    COVERAGE_GAP = "coverage_gap"

    # Documentation
    DOC = "doc"
    API_ENDPOINT = "api_endpoint"

    # Dependencies
    DEPENDENCY = "dependency"
    LICENSE = "license"


@dataclass
class Node:
    """
    A node in the memory graph.

    Represents any entity that wizards discover or create.
    """

    id: str
    type: NodeType
    name: str
    description: str = ""

    # Where this node came from
    source_wizard: str = ""
    source_file: str = ""
    source_line: int | None = None

    # Classification
    severity: str = ""  # critical, high, medium, low, info
    confidence: float = 1.0  # 0.0 - 1.0

    # Metadata
    metadata: dict[str, Any] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    # Status tracking
    status: str = "open"  # open, investigating, resolved, wontfix

    def to_dict(self) -> dict[str, Any]:
        """Convert node to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "type": self.type.value,
            "name": self.name,
            "description": self.description,
            "source_wizard": self.source_wizard,
            "source_file": self.source_file,
            "source_line": self.source_line,
            "severity": self.severity,
            "confidence": self.confidence,
            "metadata": self.metadata,
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Node":
        """Create node from dictionary."""
        return cls(
            id=data["id"],
            type=NodeType(data["type"]),
            name=data["name"],
            description=data.get("description", ""),
            source_wizard=data.get("source_wizard", ""),
            source_file=data.get("source_file", ""),
            source_line=data.get("source_line"),
            severity=data.get("severity", ""),
            confidence=data.get("confidence", 1.0),
            metadata=data.get("metadata", {}),
            tags=data.get("tags", []),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.now()
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if "updated_at" in data
                else datetime.now()
            ),
            status=data.get("status", "open"),
        )


@dataclass
class BugNode(Node):
    """Specialized node for bugs."""

    root_cause: str = ""
    fix_suggestion: str = ""
    reproduction_steps: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.BUG


@dataclass
class VulnerabilityNode(Node):
    """Specialized node for security vulnerabilities."""

    cwe_id: str = ""
    cvss_score: float = 0.0
    attack_vector: str = ""
    remediation: str = ""

    def __post_init__(self):
        self.type = NodeType.VULNERABILITY


@dataclass
class PerformanceNode(Node):
    """Specialized node for performance issues."""

    metric: str = ""  # latency, memory, cpu, etc.
    current_value: float = 0.0
    target_value: float = 0.0
    optimization_suggestion: str = ""

    def __post_init__(self):
        self.type = NodeType.PERFORMANCE_ISSUE


@dataclass
class PatternNode(Node):
    """Specialized node for code patterns."""

    pattern_type: str = ""  # anti-pattern, best-practice, idiom
    language: str = ""
    example_code: str = ""
    applies_to: list[str] = field(default_factory=list)

    def __post_init__(self):
        self.type = NodeType.PATTERN
