"""Book Production Pipeline - Orchestrator

Orchestrates the full chapter production workflow:
Research → Write → Edit → Review

Supports both sequential and parallel chapter production.
Designed for LangGraph compatibility but works standalone.

Key Insight from Experience:
The pipeline is only as good as its weakest agent.
But with good agents, orchestration is straightforward.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .base import AgentConfig, MemDocsConfig, RedisConfig
from .editor_agent import EditorAgent
from .learning import (
    FeedbackLoop,
    PatternExtractor,
    QualityGapDetector,
    SBARHandoff,
    create_editor_to_reviewer_handoff,
    create_research_to_writer_handoff,
    create_reviewer_to_writer_handoff,
    create_writer_to_editor_handoff,
)
from .research_agent import ResearchAgent
from .reviewer_agent import ReviewerAgent
from .state import AgentPhase, Chapter, ChapterSpec, create_initial_state
from .writer_agent import WriterAgent

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for the book production pipeline"""

    # Agent configurations
    research_config: AgentConfig | None = None
    writer_config: AgentConfig | None = None
    editor_config: AgentConfig | None = None
    reviewer_config: AgentConfig | None = None

    # Shared configurations
    memdocs_config: MemDocsConfig | None = None
    redis_config: RedisConfig | None = None

    # Pipeline behavior
    max_iterations: int = 3  # Max revision cycles
    auto_retry_on_failure: bool = True
    store_intermediate_drafts: bool = True
    parallel_chapter_limit: int = 3  # Max chapters to process in parallel

    # Learning system configuration
    enable_sbar_handoffs: bool = True  # Use SBAR format for agent handoffs
    enable_pattern_extraction: bool = True  # Extract patterns from successful chapters
    enable_quality_gap_detection: bool = True  # Detect and track quality gaps
    enable_feedback_loop: bool = True  # Update pattern effectiveness scores
    pattern_extraction_threshold: float = 0.85  # Min score to extract patterns


class BookProductionPipeline:
    """Orchestrates multi-agent book production.

    Workflow:
    1. Research - Gather and analyze source material
    2. Write - Create chapter draft from research
    3. Edit - Polish draft for consistency and quality
    4. Review - Assess quality and approve for publication

    If review fails, iterate with feedback until approved or max iterations.
    """

    def __init__(self, config: PipelineConfig | None = None):
        """Initialize the pipeline.

        Args:
            config: Pipeline configuration (uses defaults if not provided)

        """
        self.config = config or PipelineConfig()
        self.logger = logging.getLogger("pipeline.book_production")

        # Initialize agents
        self._init_agents()

        # Initialize learning system components
        self._init_learning_system()

        # Track statistics
        self.stats = {
            "chapters_produced": 0,
            "total_iterations": 0,
            "approval_rate": 0.0,
            "average_quality_score": 0.0,
        }

        # Track handoffs for audit trail
        self.handoff_history: list[SBARHandoff] = []

    def _init_agents(self):
        """Initialize all agents with configuration"""
        memdocs = self.config.memdocs_config or MemDocsConfig()
        redis = self.config.redis_config or RedisConfig()

        self.research_agent = ResearchAgent(
            config=self.config.research_config,
            memdocs_config=memdocs,
            redis_config=redis,
        )

        self.writer_agent = WriterAgent(
            config=self.config.writer_config,
            memdocs_config=memdocs,
            redis_config=redis,
        )

        self.editor_agent = EditorAgent(
            config=self.config.editor_config,
            memdocs_config=memdocs,
            redis_config=redis,
        )

        self.reviewer_agent = ReviewerAgent(
            config=self.config.reviewer_config,
            memdocs_config=memdocs,
            redis_config=redis,
        )

    def _init_learning_system(self):
        """Initialize learning system components"""
        # Quality gap detector for structured issue identification
        self.gap_detector = (
            QualityGapDetector() if self.config.enable_quality_gap_detection else None
        )

        # Pattern extractor for successful chapters
        self.pattern_extractor = (
            PatternExtractor() if self.config.enable_pattern_extraction else None
        )

        # Feedback loop for continuous improvement
        self.feedback_loop = FeedbackLoop() if self.config.enable_feedback_loop else None

        self.logger.info(
            f"Learning system initialized: "
            f"handoffs={self.config.enable_sbar_handoffs}, "
            f"gaps={self.config.enable_quality_gap_detection}, "
            f"patterns={self.config.enable_pattern_extraction}, "
            f"feedback={self.config.enable_feedback_loop}",
        )

    async def produce_chapter(
        self,
        spec: ChapterSpec,
        source_paths: list[str] | None = None,
    ) -> Chapter:
        """Produce a complete chapter through the full pipeline.

        Args:
            spec: Chapter specification
            source_paths: Optional list of source document paths

        Returns:
            Completed Chapter with content and metadata

        """
        self.logger.info(f"Starting production for Chapter {spec.number}: {spec.title}")
        start_time = datetime.now()

        # Initialize state
        state = create_initial_state(
            chapter_number=spec.number,
            chapter_title=spec.title,
            book_context=spec.book_context,
            target_word_count=spec.target_word_count,
        )

        if source_paths:
            state["source_paths"] = source_paths
        elif spec.source_paths:
            state["source_paths"] = spec.source_paths

        iteration = 0
        approved = False

        while not approved and iteration < self.config.max_iterations:
            iteration += 1
            self.logger.info(f"Pipeline iteration {iteration}/{self.config.max_iterations}")

            # Phase 1: Research (only on first iteration)
            if iteration == 1:
                state = await self.research_agent.process(state)
                if state.get("errors"):
                    self.logger.error(f"Research failed: {state['errors']}")
                    break

                # Create SBAR handoff: Research → Writer
                if self.config.enable_sbar_handoffs:
                    handoff = create_research_to_writer_handoff(state)
                    state["handoff_context"] = handoff.to_prompt_context()
                    self.handoff_history.append(handoff)
                    self.logger.debug(f"Created handoff: {handoff.handoff_type.value}")

            # Phase 2: Write
            state = await self.writer_agent.process(state)
            if state.get("errors"):
                self.logger.error(f"Writing failed: {state['errors']}")
                break

            # Create SBAR handoff: Writer → Editor
            if self.config.enable_sbar_handoffs:
                handoff = create_writer_to_editor_handoff(state)
                state["handoff_context"] = handoff.to_prompt_context()
                self.handoff_history.append(handoff)
                self.logger.debug(f"Created handoff: {handoff.handoff_type.value}")

            # Phase 3: Edit
            state = await self.editor_agent.process(state)

            # Create SBAR handoff: Editor → Reviewer
            if self.config.enable_sbar_handoffs:
                handoff = create_editor_to_reviewer_handoff(state)
                state["handoff_context"] = handoff.to_prompt_context()
                self.handoff_history.append(handoff)
                self.logger.debug(f"Created handoff: {handoff.handoff_type.value}")

            # Phase 4: Review
            state = await self.reviewer_agent.process(state)

            approved = state.get("approved_for_publication", False)
            quality_scores = state.get("quality_scores", {})

            # Detect quality gaps for structured tracking
            if self.gap_detector and isinstance(quality_scores, dict):
                gaps = self.gap_detector.detect_gaps(
                    quality_scores,
                    state.get("current_draft", ""),
                    state["chapter_title"],
                )
                state["quality_gaps"] = [g.to_dict() for g in gaps]
                gap_summary = self.gap_detector.summarize_gaps(gaps)
                self.logger.info(
                    f"Quality gaps: {gap_summary['total_gaps']} total, "
                    f"{gap_summary['blocking_count']} blocking",
                )

            if not approved and iteration < self.config.max_iterations:
                self.logger.info(
                    f"Review rejected (score: {quality_scores.get('overall', 0):.2f}). "
                    f"Iterating with feedback...",
                )

                # Create SBAR handoff: Reviewer → Writer (revision)
                if self.config.enable_sbar_handoffs:
                    handoff = create_reviewer_to_writer_handoff(state)
                    state["handoff_context"] = handoff.to_prompt_context()
                    self.handoff_history.append(handoff)
                    self.logger.debug(f"Created revision handoff: {handoff.handoff_type.value}")

                # Record feedback for pattern improvement
                if self.feedback_loop:
                    self.feedback_loop.record_review_feedback(
                        chapter_number=spec.number,
                        chapter_title=spec.title,
                        quality_scores=quality_scores if isinstance(quality_scores, dict) else {},
                        patterns_used=state.get("writing_patterns_applied", []),
                        approved=False,
                    )

                # Inject feedback into state for next iteration
                state = self._prepare_for_revision(state)

        # Calculate production time
        duration = (datetime.now() - start_time).total_seconds()

        # Update statistics
        self._update_stats(state, approved, iteration)

        # Get quality scores (handle both dict and dataclass)
        quality_scores = state.get("quality_scores", {})
        if hasattr(quality_scores, "overall"):
            overall_score = quality_scores.overall
            scores_dict = {
                "overall": quality_scores.overall,
                "structure": quality_scores.structure,
                "voice_consistency": quality_scores.voice_consistency,
                "code_quality": quality_scores.code_quality,
                "reader_engagement": quality_scores.reader_engagement,
                "technical_accuracy": quality_scores.technical_accuracy,
            }
        else:
            overall_score = quality_scores.get("overall", 0.0)
            scores_dict = quality_scores

        # Learning system post-processing for successful chapters
        extracted_patterns = []
        if approved and self.pattern_extractor:
            if overall_score >= self.config.pattern_extraction_threshold:
                extracted_patterns = self.pattern_extractor.extract_patterns(
                    draft=state.get("current_draft", ""),
                    chapter_number=spec.number,
                    chapter_title=spec.title,
                    quality_scores=scores_dict,
                )
                self.logger.info(
                    f"Extracted {len(extracted_patterns)} patterns from successful chapter",
                )

        # Record feedback for approved chapter
        if self.feedback_loop:
            self.feedback_loop.record_review_feedback(
                chapter_number=spec.number,
                chapter_title=spec.title,
                quality_scores=scores_dict,
                patterns_used=state.get("writing_patterns_applied", []),
                approved=approved,
            )
            # Update pattern effectiveness scores
            self.feedback_loop.update_pattern_scores()

        # Create final chapter with learning metadata
        chapter = Chapter(
            content=state["current_draft"],
            quality_score=overall_score,
            metadata={
                "chapter_number": spec.number,
                "chapter_title": spec.title,
                "iterations": iteration,
                "approved": approved,
                "production_time_seconds": duration,
                "quality_scores": scores_dict,
                "feedback": state.get("review_feedback", []),
                "execution_id": state["execution_id"],
                "pipeline_version": state["pipeline_version"],
                # Learning system metadata
                "handoffs_created": len([h for h in self.handoff_history if h.to_agent]),
                "patterns_extracted": len(extracted_patterns),
                "quality_gaps": state.get("quality_gaps", []),
                "patterns_used": state.get("writing_patterns_applied", []),
            },
        )

        self.logger.info(
            f"Chapter {spec.number} complete: approved={approved}, "
            f"score={chapter.quality_score:.2f}, time={duration:.1f}s, "
            f"iterations={iteration}, patterns_extracted={len(extracted_patterns)}",
        )

        return chapter

    async def produce_book(
        self,
        chapters: list[ChapterSpec],
        parallel: bool = True,
    ) -> list[Chapter]:
        """Produce multiple chapters, optionally in parallel.

        Args:
            chapters: List of chapter specifications
            parallel: Whether to produce chapters in parallel

        Returns:
            List of completed chapters

        """
        self.logger.info(f"Starting book production: {len(chapters)} chapters")
        start_time = datetime.now()

        if parallel:
            # Process in batches to avoid overload
            results = []
            batch_size = self.config.parallel_chapter_limit

            for i in range(0, len(chapters), batch_size):
                batch = chapters[i : i + batch_size]
                self.logger.info(
                    f"Processing batch {i // batch_size + 1}: "
                    f"chapters {i + 1}-{min(i + batch_size, len(chapters))}",
                )

                batch_results = await asyncio.gather(
                    *[self.produce_chapter(spec) for spec in batch],
                    return_exceptions=True,
                )

                for j, result in enumerate(batch_results):
                    if isinstance(result, Exception):
                        self.logger.error(f"Chapter {batch[j].number} failed: {result}")
                        # Create error chapter
                        results.append(
                            Chapter(
                                content="",
                                quality_score=0.0,
                                metadata={"error": str(result)},
                            ),
                        )
                    else:
                        results.append(result)
        else:
            # Sequential processing
            results = []
            for spec in chapters:
                try:
                    chapter = await self.produce_chapter(spec)
                    results.append(chapter)
                except Exception as e:
                    self.logger.error(f"Chapter {spec.number} failed: {e}")
                    results.append(
                        Chapter(
                            content="",
                            quality_score=0.0,
                            metadata={"error": str(e)},
                        ),
                    )

        duration = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"Book production complete: {len(results)} chapters in {duration:.1f}s")

        return results

    def _prepare_for_revision(self, state: dict[str, Any]) -> dict[str, Any]:
        """Prepare state for revision iteration"""
        # Reset phase tracking for new iteration
        state["current_phase"] = AgentPhase.WRITING.value

        # Remove WRITING and later phases from completed
        phases_to_keep = [AgentPhase.RESEARCH.value]
        state["completed_phases"] = [p for p in state["completed_phases"] if p in phases_to_keep]

        # Add revision context
        feedback = state.get("review_feedback", [])
        state["book_context"] = (
            state.get("book_context", "")
            + "\n\nRevision feedback:\n"
            + "\n".join(f"- {f}" for f in feedback)
        )

        return state

    def _update_stats(
        self,
        state: dict[str, Any],
        approved: bool,
        iterations: int,
    ):
        """Update pipeline statistics"""
        self.stats["chapters_produced"] += 1
        self.stats["total_iterations"] += iterations

        # Update approval rate (running average)
        n = self.stats["chapters_produced"]
        old_rate = self.stats["approval_rate"]
        self.stats["approval_rate"] = old_rate + (1.0 if approved else 0.0 - old_rate) / n

        # Update average quality score
        old_avg = self.stats["average_quality_score"]
        quality_scores = state.get("quality_scores", {})
        if hasattr(quality_scores, "overall"):
            new_score = quality_scores.overall
        else:
            new_score = quality_scores.get("overall", 0.0)
        self.stats["average_quality_score"] = old_avg + (new_score - old_avg) / n

    def get_stats(self) -> dict[str, Any]:
        """Get pipeline statistics including learning system metrics"""
        base_stats = {
            **self.stats,
            "average_iterations_per_chapter": (
                self.stats["total_iterations"] / max(1, self.stats["chapters_produced"])
            ),
        }

        # Add learning system statistics
        learning_stats = {
            "handoffs_total": len(self.handoff_history),
        }

        if self.feedback_loop:
            learning_stats.update(self.feedback_loop.get_feedback_summary())

        return {
            **base_stats,
            "learning": learning_stats,
        }

    def get_handoff_history(self) -> list[dict[str, Any]]:
        """Get the history of all SBAR handoffs created during production"""
        return [h.to_dict() for h in self.handoff_history]

    def get_pattern_effectiveness(self) -> dict[str, float]:
        """Get pattern effectiveness scores from the feedback loop"""
        if self.feedback_loop:
            return self.feedback_loop.pattern_scores
        return {}


# Convenience function for simple usage
async def produce_chapter(
    chapter_number: int,
    chapter_title: str,
    source_paths: list[str] | None = None,
    book_context: str = "",
) -> Chapter:
    """Convenience function to produce a single chapter.

    Args:
        chapter_number: Chapter number
        chapter_title: Chapter title
        source_paths: Optional source document paths
        book_context: Optional context about the book

    Returns:
        Completed Chapter

    """
    pipeline = BookProductionPipeline()

    spec = ChapterSpec(
        number=chapter_number,
        title=chapter_title,
        source_paths=source_paths or [],
        book_context=book_context,
    )

    return await pipeline.produce_chapter(spec)
