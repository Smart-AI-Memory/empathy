"""Book Production Pipeline - Multi-Agent System

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
from .learning import (  # Pattern Extraction; Feedback Loop; Quality Gap Detection; SBAR Handoffs
                   ExtractedPattern,
                   FeedbackEntry,
                   FeedbackLoop,
                   GapSeverity,
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
    # Configuration
    "AgentConfig",
    "AgentPhase",
    # Base classes
    "BaseAgent",
    # Pipeline
    "BookProductionPipeline",
    "Chapter",
    # State management
    "ChapterProductionState",
    # Data structures
    "ChapterSpec",
    "Draft",
    "DraftVersion",
    "EditResult",
    "EditorAgent",
    # Learning System - Pattern Extraction
    "ExtractedPattern",
    # Learning System - Feedback Loop
    "FeedbackEntry",
    "FeedbackLoop",
    # Learning System - Quality Gap Detection
    "GapSeverity",
    # Learning System - SBAR Handoffs
    "HandoffType",
    "MemDocsConfig",
    "OpusAgent",
    "PatternExtractor",
    "PipelineConfig",
    "QualityGap",
    "QualityGapDetector",
    "QualityScore",
    "RedisConfig",
    # Agents
    "ResearchAgent",
    "ResearchResult",
    "ReviewResult",
    "ReviewerAgent",
    "SBARHandoff",
    "SonnetAgent",
    "SourceDocument",
    "WriterAgent",
    "create_editor_to_reviewer_handoff",
    "create_initial_state",
    "create_research_to_writer_handoff",
    "create_reviewer_to_writer_handoff",
    "create_writer_to_editor_handoff",
    "produce_chapter",
]

__version__ = "1.0.0"
