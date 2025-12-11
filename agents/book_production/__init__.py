"""
Book Production Pipeline - Multi-Agent System

A multi-agent system for transforming technical documentation into
polished book chapters. Implements Phase 2 of the Book Production
Pipeline Plan (Options C & D).

Agents:
- ResearchAgent: Gathers source material (Sonnet - fast extraction)
- WriterAgent: Creates chapter drafts (Opus 4.5 - creative quality)
- EditorAgent: Polishes drafts (Sonnet - rule-based editing)
- ReviewerAgent: Quality assessment (Opus 4.5 - nuanced evaluation)

Key Achievement Being Systematized:
- 5 chapters + 5 appendices written in ~2 hours
- Consistent quality through shared patterns
- MemDocs learning for continuous improvement

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .base import AgentConfig, BaseAgent, MemDocsConfig, OpusAgent, RedisConfig, SonnetAgent
from .editor_agent import EditorAgent
from .learning import (
    # Pattern Extraction
    ExtractedPattern,
    # Feedback Loop
    FeedbackEntry,
    FeedbackLoop,
    # Quality Gap Detection
    GapSeverity,
    # SBAR Handoffs
    HandoffType,
    PatternExtractor,
    QualityGap,
    QualityGapDetector,
    SBARHandoff,
    create_editor_to_reviewer_handoff,
    create_research_to_writer_handoff,
    create_reviewer_to_writer_handoff,
    create_writer_to_editor_handoff,
)
from .pipeline import BookProductionPipeline, PipelineConfig, produce_chapter
from .research_agent import ResearchAgent
from .reviewer_agent import ReviewerAgent
from .state import (
    AgentPhase,
    Chapter,
    ChapterProductionState,
    ChapterSpec,
    Draft,
    DraftVersion,
    EditResult,
    QualityScore,
    ResearchResult,
    ReviewResult,
    SourceDocument,
    create_initial_state,
)
from .writer_agent import WriterAgent

__all__ = [
    # Pipeline
    "BookProductionPipeline",
    "PipelineConfig",
    "produce_chapter",
    # Agents
    "ResearchAgent",
    "WriterAgent",
    "EditorAgent",
    "ReviewerAgent",
    # Base classes
    "BaseAgent",
    "OpusAgent",
    "SonnetAgent",
    # Configuration
    "AgentConfig",
    "MemDocsConfig",
    "RedisConfig",
    # State management
    "ChapterProductionState",
    "AgentPhase",
    "create_initial_state",
    # Data structures
    "ChapterSpec",
    "SourceDocument",
    "DraftVersion",
    "QualityScore",
    "ResearchResult",
    "Draft",
    "EditResult",
    "ReviewResult",
    "Chapter",
    # Learning System - SBAR Handoffs
    "HandoffType",
    "SBARHandoff",
    "create_research_to_writer_handoff",
    "create_writer_to_editor_handoff",
    "create_editor_to_reviewer_handoff",
    "create_reviewer_to_writer_handoff",
    # Learning System - Quality Gap Detection
    "GapSeverity",
    "QualityGap",
    "QualityGapDetector",
    # Learning System - Pattern Extraction
    "ExtractedPattern",
    "PatternExtractor",
    # Learning System - Feedback Loop
    "FeedbackEntry",
    "FeedbackLoop",
]

__version__ = "1.0.0"
