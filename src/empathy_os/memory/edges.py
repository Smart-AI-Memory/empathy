"""
Memory Graph Edge Types

Defines edge types for connecting nodes in the knowledge graph.
Edges represent relationships between entities discovered by wizards.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class EdgeType(Enum):
    """Types of relationships between nodes."""

    # Causal relationships
    CAUSES = "causes"  # bug causes another bug
    CAUSED_BY = "caused_by"  # reverse of causes
    LEADS_TO = "leads_to"  # issue leads to another issue

    # Resolution relationships
    FIXED_BY = "fixed_by"  # bug fixed by a fix
    FIXES = "fixes"  # fix fixes a bug
    MITIGATES = "mitigates"  # partial fix

    # Similarity relationships
    SIMILAR_TO = "similar_to"  # similar issues
    RELATED_TO = "related_to"  # general relation
    DUPLICATE_OF = "duplicate_of"  # same issue

    # Structural relationships
    CONTAINS = "contains"  # file contains function
    CONTAINED_IN = "contained_in"  # reverse
    DEPENDS_ON = "depends_on"  # code dependency
    IMPORTED_BY = "imported_by"  # reverse
    AFFECTS = "affects"  # issue affects code
    AFFECTED_BY = "affected_by"  # code affected by issue

    # Testing relationships
    TESTED_BY = "tested_by"  # code tested by test
    TESTS = "tests"  # test tests code
    COVERS = "covers"  # test covers code path

    # Documentation relationships
    DOCUMENTS = "documents"  # doc documents code
    DOCUMENTED_BY = "documented_by"  # reverse

    # Sequence relationships
    PRECEDED_BY = "preceded_by"  # temporal order
    FOLLOWED_BY = "followed_by"  # reverse

    # Derivation relationships
    DERIVED_FROM = "derived_from"  # pattern derived from code
    REFACTORED_TO = "refactored_to"  # code refactored


@dataclass
class Edge:
    """
    An edge connecting two nodes in the memory graph.

    Represents a relationship between entities.
    """

    source_id: str
    target_id: str
    type: EdgeType

    # Edge metadata
    weight: float = 1.0  # Strength of relationship (0.0 - 1.0)
    confidence: float = 1.0  # How confident we are in this edge

    # Context
    description: str = ""
    source_wizard: str = ""

    # Additional data
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict[str, Any]:
        """Convert edge to dictionary for JSON serialization."""
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type.value,
            "weight": self.weight,
            "confidence": self.confidence,
            "description": self.description,
            "source_wizard": self.source_wizard,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Edge":
        """Create edge from dictionary."""
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            type=EdgeType(data["type"]),
            weight=data.get("weight", 1.0),
            confidence=data.get("confidence", 1.0),
            description=data.get("description", ""),
            source_wizard=data.get("source_wizard", ""),
            metadata=data.get("metadata", {}),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if "created_at" in data
                else datetime.now()
            ),
        )

    @property
    def id(self) -> str:
        """Generate unique edge ID."""
        return f"{self.source_id}-{self.type.value}-{self.target_id}"


# Common edge patterns for wizard findings
WIZARD_EDGE_PATTERNS = {
    "security-audit": [
        (EdgeType.CAUSES, "vulnerability → vulnerability"),
        (EdgeType.FIXED_BY, "vulnerability → fix"),
        (EdgeType.AFFECTS, "vulnerability → file"),
    ],
    "bug-predict": [
        (EdgeType.CAUSES, "bug → bug"),
        (EdgeType.SIMILAR_TO, "bug → bug"),
        (EdgeType.FIXED_BY, "bug → fix"),
    ],
    "perf-audit": [
        (EdgeType.CAUSES, "performance_issue → performance_issue"),
        (EdgeType.LEADS_TO, "code_smell → performance_issue"),
        (EdgeType.MITIGATES, "refactor → performance_issue"),
    ],
    "code-review": [
        (EdgeType.CONTAINS, "file → function"),
        (EdgeType.RELATED_TO, "code_smell → pattern"),
        (EdgeType.REFACTORED_TO, "function → function"),
    ],
    "test-gen": [
        (EdgeType.TESTS, "test → function"),
        (EdgeType.COVERS, "test → file"),
        (EdgeType.TESTS, "test_case → bug"),
    ],
    "dependency-check": [
        (EdgeType.DEPENDS_ON, "file → dependency"),
        (EdgeType.CAUSES, "dependency → vulnerability"),
    ],
}


# Reverse edge type mapping
REVERSE_EDGE_TYPES = {
    EdgeType.CAUSES: EdgeType.CAUSED_BY,
    EdgeType.CAUSED_BY: EdgeType.CAUSES,
    EdgeType.FIXED_BY: EdgeType.FIXES,
    EdgeType.FIXES: EdgeType.FIXED_BY,
    EdgeType.CONTAINS: EdgeType.CONTAINED_IN,
    EdgeType.CONTAINED_IN: EdgeType.CONTAINS,
    EdgeType.DEPENDS_ON: EdgeType.IMPORTED_BY,
    EdgeType.IMPORTED_BY: EdgeType.DEPENDS_ON,
    EdgeType.TESTED_BY: EdgeType.TESTS,
    EdgeType.TESTS: EdgeType.TESTED_BY,
    EdgeType.DOCUMENTS: EdgeType.DOCUMENTED_BY,
    EdgeType.DOCUMENTED_BY: EdgeType.DOCUMENTS,
    EdgeType.PRECEDED_BY: EdgeType.FOLLOWED_BY,
    EdgeType.FOLLOWED_BY: EdgeType.PRECEDED_BY,
    EdgeType.SIMILAR_TO: EdgeType.SIMILAR_TO,  # Symmetric
    EdgeType.RELATED_TO: EdgeType.RELATED_TO,  # Symmetric
    EdgeType.DUPLICATE_OF: EdgeType.DUPLICATE_OF,  # Symmetric
    EdgeType.AFFECTS: EdgeType.AFFECTED_BY,
    EdgeType.AFFECTED_BY: EdgeType.AFFECTS,
}
