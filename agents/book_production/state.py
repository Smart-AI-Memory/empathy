"""
Book Production Pipeline - State Management

Defines the shared state structure for multi-agent book production.
Follows the pattern from compliance_anticipation_agent.py using TypedDict
for LangGraph compatibility.

Key Insight: Agent state should answer questions clearly.
"What chapter?" "What sources?" "What draft?" "What feedback?"

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import operator
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, TypedDict

# Optional LangChain integration
try:
    from langchain_core.messages import BaseMessage
except ImportError:
    # Fallback: Use simple dict-based messages when LangChain not available
    BaseMessage = dict  # type: ignore


class AgentPhase(Enum):
    """Phases of chapter production"""

    RESEARCH = "research"
    WRITING = "writing"
    EDITING = "editing"
    REVIEW = "review"
    COMPLETE = "complete"
    ERROR = "error"


class DraftVersion(TypedDict):
    """A single draft version"""

    version: int
    content: str
    word_count: int
    created_at: str
    created_by: str  # Agent that created this version
    changes_summary: str


class SourceDocument(TypedDict):
    """A source document for research"""

    path: str
    content: str
    word_count: int
    headings: list[dict]
    code_blocks: list[dict]
    key_concepts: list[str]
    metrics: list[str]
    relevance_score: float


class QualityScore(TypedDict):
    """Quality assessment scores"""

    overall: float
    structure: float
    voice_consistency: float
    code_quality: float
    reader_engagement: float
    technical_accuracy: float


class ChapterProductionState(TypedDict):
    """
    Shared state for chapter production pipeline.

    Design Philosophy (following compliance_anticipation_agent.py):
    - Each field answers a specific question
    - All operations are traceable via audit trail
    - State is immutable-style (return new state, don't mutate)
    """

    # =========================================================================
    # Chapter Specification - Answers: "What are we building?"
    # =========================================================================
    chapter_number: int
    chapter_title: str
    book_title: str
    book_context: str
    target_word_count: int
    chapter_spec_id: str  # Unique identifier for this chapter

    # =========================================================================
    # Progress Tracking - Answers: "Where are we in the process?"
    # =========================================================================
    current_phase: str  # AgentPhase value
    completed_phases: list[str]
    current_agent: str  # Which agent is active
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # =========================================================================
    # Research Results (Phase 1) - Answers: "What sources inform this chapter?"
    # =========================================================================
    source_documents: list[SourceDocument]
    research_summary: str
    total_source_words: int
    key_concepts_extracted: list[str]
    code_examples_found: int
    research_confidence: float

    # =========================================================================
    # Writing Results (Phase 2) - Answers: "What draft do we have?"
    # =========================================================================
    current_draft: str
    draft_versions: list[DraftVersion]
    current_version: int
    outline: str
    writing_patterns_applied: list[str]

    # =========================================================================
    # Editing Results (Phase 3) - Answers: "What issues were fixed?"
    # =========================================================================
    editing_issues_found: list[dict]
    editing_issues_fixed: int
    style_consistency_score: float
    code_verified: bool

    # =========================================================================
    # Review Results (Phase 4) - Answers: "Is this ready for publication?"
    # =========================================================================
    quality_scores: QualityScore
    review_feedback: list[str]
    approved_for_publication: bool
    reviewer_confidence: float

    # =========================================================================
    # MemDocs Integration - Answers: "What patterns are we using/storing?"
    # =========================================================================
    patterns_retrieved: list[str]  # Pattern IDs from MemDocs
    patterns_to_store: list[dict]  # New patterns to save
    exemplar_chapters_used: list[str]

    # =========================================================================
    # Error Handling & Audit Trail
    # =========================================================================
    errors: list[str]
    warnings: list[str]
    audit_trail: list[dict]

    # =========================================================================
    # Metadata
    # =========================================================================
    pipeline_version: str
    execution_id: str
    created_at: str
    last_updated: str
    total_llm_calls: int
    total_tokens_used: int


def create_initial_state(
    chapter_number: int,
    chapter_title: str,
    book_title: str = "Persistent Memory for AI",
    book_context: str = "",
    target_word_count: int = 4000,
) -> ChapterProductionState:
    """
    Create initial state for chapter production.

    Args:
        chapter_number: Chapter number (e.g., 23)
        chapter_title: Chapter title
        book_title: Name of the book
        book_context: Context about the book for continuity
        target_word_count: Target word count for chapter

    Returns:
        Initialized ChapterProductionState
    """
    import uuid

    now = datetime.now()
    # Include microseconds and random suffix for uniqueness
    execution_id = (
        f"chapter_{chapter_number}_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
    )

    return ChapterProductionState(
        # Chapter Specification
        chapter_number=chapter_number,
        chapter_title=chapter_title,
        book_title=book_title,
        book_context=book_context,
        target_word_count=target_word_count,
        chapter_spec_id=execution_id,
        # Progress
        current_phase=AgentPhase.RESEARCH.value,
        completed_phases=[],
        current_agent="",
        messages=[],
        # Research
        source_documents=[],
        research_summary="",
        total_source_words=0,
        key_concepts_extracted=[],
        code_examples_found=0,
        research_confidence=0.0,
        # Writing
        current_draft="",
        draft_versions=[],
        current_version=0,
        outline="",
        writing_patterns_applied=[],
        # Editing
        editing_issues_found=[],
        editing_issues_fixed=0,
        style_consistency_score=0.0,
        code_verified=False,
        # Review
        quality_scores=QualityScore(
            overall=0.0,
            structure=0.0,
            voice_consistency=0.0,
            code_quality=0.0,
            reader_engagement=0.0,
            technical_accuracy=0.0,
        ),
        review_feedback=[],
        approved_for_publication=False,
        reviewer_confidence=0.0,
        # MemDocs
        patterns_retrieved=[],
        patterns_to_store=[],
        exemplar_chapters_used=[],
        # Errors
        errors=[],
        warnings=[],
        audit_trail=[],
        # Metadata
        pipeline_version="1.0.0",
        execution_id=execution_id,
        created_at=now.isoformat(),
        last_updated=now.isoformat(),
        total_llm_calls=0,
        total_tokens_used=0,
    )


@dataclass
class ChapterSpec:
    """Specification for a chapter to be produced"""

    number: int
    title: str
    source_paths: list[str] = field(default_factory=list)
    topic: str = ""
    book_context: str = ""
    target_word_count: int = 4000
    previous_chapter_summary: str = ""
    next_chapter_hint: str = ""


@dataclass
class ResearchResult:
    """Result from research phase"""

    sources: list[SourceDocument]
    summary: str
    key_concepts: list[str]
    code_examples: int
    confidence: float


@dataclass
class Draft:
    """A chapter draft"""

    content: str
    version: int
    word_count: int
    patterns_applied: list[str]


@dataclass
class EditResult:
    """Result from editing phase"""

    draft: Draft
    issues_found: int
    issues_fixed: int
    style_score: float


@dataclass
class ReviewResult:
    """Result from review phase"""

    approved: bool
    scores: QualityScore
    feedback: list[str]
    confidence: float


@dataclass
class Chapter:
    """A completed chapter"""

    content: str
    quality_score: float
    metadata: dict[str, Any]
