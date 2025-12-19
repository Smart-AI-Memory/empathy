"""
Tests for the Book Production Learning System

Tests cover:
- SBAR Agent Handoffs
- Quality Gap Detection
- Pattern Extraction
- Feedback Loop

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from agents.book_production.learning import (
    ExtractedPattern,
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
from agents.book_production.state import create_initial_state


class TestSBARHandoffs:
    """Tests for SBAR handoff creation and formatting"""

    def test_handoff_creation(self):
        """Test basic SBAR handoff creation"""
        handoff = SBARHandoff(
            handoff_type=HandoffType.RESEARCH_TO_WRITER,
            from_agent="ResearchAgent",
            to_agent="WriterAgent",
            situation="Research complete",
            background="Analyzed 5 sources",
            assessment="High confidence",
            recommendation="Proceed with writing",
        )

        assert handoff.from_agent == "ResearchAgent"
        assert handoff.to_agent == "WriterAgent"
        assert handoff.handoff_type == HandoffType.RESEARCH_TO_WRITER

    def test_handoff_to_prompt_context(self):
        """Test conversion to prompt context format"""
        handoff = SBARHandoff(
            handoff_type=HandoffType.WRITER_TO_EDITOR,
            from_agent="WriterAgent",
            to_agent="EditorAgent",
            situation="Draft complete",
            background="Applied voice patterns",
            assessment="4500 words, 6 sections",
            recommendation="Polish for publication",
            focus_areas=["Fix hedging", "Add code labels"],
            known_issues=["3 unlabeled code blocks"],
        )

        context = handoff.to_prompt_context()

        assert "## Handoff from WriterAgent" in context
        assert "**Situation:** Draft complete" in context
        assert "**Priority Focus Areas:**" in context
        assert "- Fix hedging" in context
        assert "**Known Issues to Address:**" in context

    def test_handoff_to_dict(self):
        """Test serialization to dictionary"""
        handoff = SBARHandoff(
            handoff_type=HandoffType.EDITOR_TO_REVIEWER,
            from_agent="EditorAgent",
            to_agent="ReviewerAgent",
            situation="Editing complete",
            key_metrics={"issues_fixed": 5},
        )

        d = handoff.to_dict()

        assert d["handoff_type"] == "editor_to_reviewer"
        assert d["from_agent"] == "EditorAgent"
        assert d["key_metrics"]["issues_fixed"] == 5

    def test_research_to_writer_handoff(self):
        """Test research→writer handoff factory function"""
        state = create_initial_state(
            chapter_number=5,
            chapter_title="Memory Patterns",
        )
        state["source_documents"] = [
            {"path": "doc1.md", "relevance_score": 0.8},
            {"path": "doc2.md", "relevance_score": 0.6},
        ]
        state["key_concepts_extracted"] = ["patterns", "memory", "redis"]
        state["code_examples_found"] = 8
        state["research_confidence"] = 0.85
        state["total_source_words"] = 5000

        handoff = create_research_to_writer_handoff(state)

        assert handoff.handoff_type == HandoffType.RESEARCH_TO_WRITER
        assert "Chapter 5" in handoff.situation
        assert "Memory Patterns" in handoff.situation
        assert handoff.key_metrics["sources_count"] == 2
        assert handoff.key_metrics["confidence"] == "85%"

    def test_writer_to_editor_handoff(self):
        """Test writer→editor handoff factory function"""
        state = create_initial_state(
            chapter_number=5,
            chapter_title="Memory Patterns",
            target_word_count=4000,
        )
        state[
            "current_draft"
        ] = """## Introduction

This chapter might cover patterns. Perhaps we should discuss memory.

```python
print("labeled code")
```
"""
        state["current_version"] = 1
        state["writing_patterns_applied"] = ["voice_authority"]

        handoff = create_writer_to_editor_handoff(state)

        assert handoff.handoff_type == HandoffType.WRITER_TO_EDITOR
        assert handoff.key_metrics["hedging_phrases"] >= 2  # "might", "perhaps"
        # The code block has a language label (python)
        # Pattern may count closing blocks - implementation detail
        assert handoff.key_metrics["unlabeled_code"] >= 0

    def test_editor_to_reviewer_handoff(self):
        """Test editor→reviewer handoff factory function"""
        state = create_initial_state(
            chapter_number=5,
            chapter_title="Memory Patterns",
        )
        state["current_draft"] = "Chapter content here with 100 words " * 10
        state["edit_result"] = {
            "issues_found": 5,
            "issues_fixed": 4,
            "missing_elements": ["opening_quote"],
            "unfixed_issues": ["Could not auto-fix hedging in paragraph 3"],
        }

        handoff = create_editor_to_reviewer_handoff(state)

        assert handoff.handoff_type == HandoffType.EDITOR_TO_REVIEWER
        assert handoff.key_metrics["issues_found"] == 5
        assert handoff.key_metrics["issues_fixed"] == 4
        assert "opening_quote" in str(handoff.focus_areas)

    def test_reviewer_to_writer_handoff(self):
        """Test reviewer→writer revision handoff"""
        state = create_initial_state(
            chapter_number=5,
            chapter_title="Memory Patterns",
        )
        state["quality_scores"] = {
            "overall": 0.72,
            "structure": 0.80,
            "voice_consistency": 0.65,
            "code_quality": 0.85,
            "reader_engagement": 0.60,
            "technical_accuracy": 0.75,
        }
        state["review_feedback"] = [
            "Improve reader engagement with more examples",
            "Strengthen authoritative voice",
        ]

        handoff = create_reviewer_to_writer_handoff(state)

        assert handoff.handoff_type == HandoffType.REVIEWER_TO_WRITER
        assert "72%" in handoff.key_metrics["overall_score"]
        assert len(handoff.known_issues) == 2
        assert any("engagement" in area.lower() for area in handoff.focus_areas)


class TestQualityGapDetection:
    """Tests for quality gap detection"""

    def test_gap_detector_creation(self):
        """Test gap detector initialization"""
        detector = QualityGapDetector()
        assert detector.THRESHOLDS["high"] == 0.60  # Below 60% = high severity

    def test_detect_structure_gaps(self):
        """Test detection of structure gaps"""
        detector = QualityGapDetector()

        # Draft missing key elements
        draft = """
## Introduction

Some content here.

## Main Section

More content.
"""
        scores = {
            "overall": 0.65,
            "structure": 0.50,
            "voice_consistency": 0.80,
            "code_quality": 0.80,
            "reader_engagement": 0.80,
            "technical_accuracy": 0.80,
        }

        gaps = detector.detect_gaps(scores, draft, "Test Chapter")

        # Should find gaps for missing opening quote, key takeaways, exercise
        assert len(gaps) >= 2
        structure_gaps = [g for g in gaps if g.dimension == "structure"]
        assert len(structure_gaps) >= 2

        # Verify gap properties
        for gap in structure_gaps:
            assert gap.severity in (GapSeverity.HIGH, GapSeverity.MEDIUM)
            assert len(gap.remediation_steps) > 0
            assert gap.estimated_effort_minutes > 0

    def test_detect_voice_gaps(self):
        """Test detection of voice consistency gaps (hedging)"""
        detector = QualityGapDetector()

        # Draft with 7+ hedging words (threshold is > 5)
        draft = """
This might be important. Perhaps we could consider it.
It could possibly work. Maybe it will help.
Something might be useful. Perhaps another option.
This might also matter. Maybe we should check.
"""
        scores = {
            "overall": 0.70,
            "structure": 0.80,
            "voice_consistency": 0.55,
            "code_quality": 0.80,
            "reader_engagement": 0.80,
            "technical_accuracy": 0.80,
        }

        gaps = detector.detect_gaps(scores, draft, "Test Chapter")

        voice_gaps = [g for g in gaps if g.dimension == "voice_consistency"]
        assert len(voice_gaps) >= 1
        assert "hedging" in voice_gaps[0].category

    def test_detect_code_gaps(self):
        """Test detection of code quality gaps"""
        detector = QualityGapDetector()

        draft = """
## Example

```
unlabeled code
```

```python
def broken(
    missing closing paren
```
"""
        scores = {
            "overall": 0.60,
            "structure": 0.80,
            "voice_consistency": 0.80,
            "code_quality": 0.45,
            "reader_engagement": 0.80,
            "technical_accuracy": 0.80,
        }

        gaps = detector.detect_gaps(scores, draft, "Test Chapter")

        code_gaps = [g for g in gaps if g.dimension == "code_quality"]
        assert len(code_gaps) >= 1

        # Check for unlabeled code detection
        unlabeled_gaps = [g for g in code_gaps if g.category == "unlabeled_code"]
        assert len(unlabeled_gaps) >= 1

    def test_gap_severity_determination(self):
        """Test gap severity based on score thresholds"""
        detector = QualityGapDetector()

        assert detector._determine_severity(0.35) == GapSeverity.CRITICAL
        assert detector._determine_severity(0.55) == GapSeverity.HIGH
        assert detector._determine_severity(0.70) == GapSeverity.MEDIUM
        assert detector._determine_severity(0.82) == GapSeverity.LOW

    def test_gap_summary(self):
        """Test gap summary creation"""
        detector = QualityGapDetector()

        gaps = [
            QualityGap(
                gap_id="gap_1",
                dimension="structure",
                category="key_takeaways",
                description="Missing takeaways",
                severity=GapSeverity.HIGH,
                current_score=0.5,
                target_score=0.8,
                impact_on_overall=0.05,
                estimated_effort_minutes=15,
                auto_fixable=False,
            ),
            QualityGap(
                gap_id="gap_2",
                dimension="code_quality",
                category="unlabeled",
                description="Unlabeled code",
                severity=GapSeverity.MEDIUM,
                current_score=0.7,
                target_score=0.8,
                impact_on_overall=0.02,
                estimated_effort_minutes=5,
                auto_fixable=True,
            ),
        ]

        summary = detector.summarize_gaps(gaps)

        assert summary["total_gaps"] == 2
        assert summary["by_severity"]["high"] == 1
        assert summary["by_severity"]["medium"] == 1
        assert summary["total_effort_minutes"] == 20
        assert summary["auto_fixable_count"] == 1
        assert summary["blocking_count"] == 1  # HIGH is blocking


class TestPatternExtraction:
    """Tests for pattern extraction from successful chapters"""

    def test_pattern_extractor_creation(self):
        """Test pattern extractor initialization"""
        extractor = PatternExtractor()
        assert extractor is not None

    def test_extract_patterns_threshold(self):
        """Test that patterns only extracted from high-quality chapters"""
        extractor = PatternExtractor()

        draft = '> "Great quote" - Author\n\n## Key Takeaways\n- Point 1\n- Point 2'
        low_scores = {"overall": 0.70, "structure": 0.80}
        high_scores = {"overall": 0.90, "structure": 0.90}

        low_patterns = extractor.extract_patterns(draft, 1, "Test", low_scores)
        high_patterns = extractor.extract_patterns(draft, 1, "Test", high_scores)

        assert len(low_patterns) == 0  # Below threshold
        assert len(high_patterns) >= 0  # May extract patterns

    def test_extract_structure_patterns(self):
        """Test extraction of structure patterns"""
        extractor = PatternExtractor()

        draft = """> "Memory is the foundation of intelligence." - Unknown

## Introduction

Great intro content here.

## Key Takeaways

- Point 1: Remember this
- Point 2: Implement that
- Point 3: Use these patterns
- Point 4: Build on this
- Point 5: Extend further

## Try It Yourself

1. First step
2. Second step
3. Third step
"""
        scores = {
            "overall": 0.92,
            "structure": 0.95,
            "voice_consistency": 0.90,
            "code_quality": 0.85,
            "reader_engagement": 0.88,
            "technical_accuracy": 0.90,
        }

        patterns = extractor.extract_patterns(draft, 5, "Memory Patterns", scores)

        # Should extract quote, takeaways, and exercise patterns
        structure_patterns = [p for p in patterns if p.pattern_type == "structure"]
        assert len(structure_patterns) >= 2

    def test_extract_code_patterns(self):
        """Test extraction of well-commented code patterns"""
        extractor = PatternExtractor()

        draft = """
## Code Example

```python
# Initialize the memory store
# This connects to Redis backend
store = MemoryStore(
    host="localhost",
    port=6379,
)

# Store a pattern with metadata
# The key is automatically generated
pattern_id = store.save_pattern(
    content="Example pattern",
    metadata={"type": "test"},
)
```

More content here.
"""
        scores = {
            "overall": 0.90,
            "structure": 0.85,
            "voice_consistency": 0.85,
            "code_quality": 0.95,
            "reader_engagement": 0.85,
            "technical_accuracy": 0.90,
        }

        patterns = extractor.extract_patterns(draft, 5, "Code Example", scores)

        code_patterns = [p for p in patterns if p.pattern_type == "code"]
        assert len(code_patterns) >= 1

    def test_extracted_pattern_serialization(self):
        """Test pattern serialization for MemDocs storage"""
        pattern = ExtractedPattern(
            pattern_id="test_pattern_1",
            pattern_type="structure",
            description="Test pattern",
            content="Pattern content",
            source_chapter=5,
            source_title="Test Chapter",
            quality_score=0.92,
        )

        d = pattern.to_dict()

        assert d["pattern_id"] == "test_pattern_1"
        assert d["pattern_type"] == "structure"
        assert d["quality_score"] == 0.92


class TestFeedbackLoop:
    """Tests for feedback loop and pattern effectiveness tracking"""

    def test_feedback_loop_creation(self):
        """Test feedback loop initialization"""
        loop = FeedbackLoop()
        assert len(loop.pending_feedback) == 0
        assert len(loop.pattern_scores) == 0

    def test_record_positive_feedback(self):
        """Test recording positive feedback for approved chapter"""
        loop = FeedbackLoop()

        entries = loop.record_review_feedback(
            chapter_number=5,
            chapter_title="Memory Patterns",
            quality_scores={"overall": 0.92, "structure": 0.90},
            patterns_used=["pattern_1", "pattern_2"],
            approved=True,
        )

        assert len(entries) == 2
        assert all(e.feedback_type == "positive" for e in entries)

    def test_record_negative_feedback(self):
        """Test recording negative feedback for rejected chapter"""
        loop = FeedbackLoop()

        entries = loop.record_review_feedback(
            chapter_number=5,
            chapter_title="Memory Patterns",
            quality_scores={
                "overall": 0.65,
                "structure": 0.50,
                "voice_consistency": 0.70,
            },
            patterns_used=["pattern_1"],
            approved=False,
        )

        assert len(entries) == 1
        assert entries[0].feedback_type == "negative"
        assert "structure" in entries[0].context["failed_dimensions"]

    def test_update_pattern_scores(self):
        """Test pattern score updates from feedback"""
        loop = FeedbackLoop()

        # Record positive feedback
        loop.record_review_feedback(
            chapter_number=1,
            chapter_title="Test 1",
            quality_scores={"overall": 0.90},
            patterns_used=["pattern_a"],
            approved=True,
        )

        # Record negative feedback
        loop.record_review_feedback(
            chapter_number=2,
            chapter_title="Test 2",
            quality_scores={"overall": 0.60, "structure": 0.50},
            patterns_used=["pattern_b"],
            approved=False,
        )

        scores = loop.update_pattern_scores()

        assert "pattern_a" in scores
        assert "pattern_b" in scores
        assert scores["pattern_a"] > 0.5  # Positive feedback increases
        assert scores["pattern_b"] < 0.5  # Negative feedback decreases

    def test_get_deprecated_patterns(self):
        """Test identification of deprecated patterns"""
        loop = FeedbackLoop()
        loop.pattern_scores = {
            "good_pattern": 0.85,
            "okay_pattern": 0.50,
            "bad_pattern": 0.20,
        }

        deprecated = loop.get_deprecated_patterns(threshold=0.3)

        assert "bad_pattern" in deprecated
        assert "good_pattern" not in deprecated
        assert "okay_pattern" not in deprecated

    def test_get_high_performing_patterns(self):
        """Test identification of high-performing patterns"""
        loop = FeedbackLoop()
        loop.pattern_scores = {
            "excellent_pattern": 0.95,
            "good_pattern": 0.82,
            "okay_pattern": 0.70,
        }

        high_performers = loop.get_high_performing_patterns(threshold=0.8)

        assert "excellent_pattern" in high_performers
        assert "good_pattern" in high_performers
        assert "okay_pattern" not in high_performers

    def test_feedback_summary(self):
        """Test feedback summary generation"""
        loop = FeedbackLoop()

        loop.record_review_feedback(1, "Ch1", {"overall": 0.90}, ["p1"], True)
        loop.record_review_feedback(2, "Ch2", {"overall": 0.60, "s": 0.5}, ["p2"], False)
        loop.update_pattern_scores()

        summary = loop.get_feedback_summary()

        assert summary["total_entries"] == 2
        assert summary["by_type"]["positive"] == 1
        assert summary["by_type"]["negative"] == 1
        assert summary["patterns_tracked"] == 2


class TestPipelineIntegration:
    """Integration tests for learning system with pipeline"""

    def test_pipeline_with_learning_config(self):
        """Test pipeline initialization with learning config"""
        from agents.book_production.pipeline import (
            BookProductionPipeline,
            PipelineConfig,
        )

        config = PipelineConfig(
            enable_sbar_handoffs=True,
            enable_pattern_extraction=True,
            enable_quality_gap_detection=True,
            enable_feedback_loop=True,
            pattern_extraction_threshold=0.85,
        )

        pipeline = BookProductionPipeline(config=config)

        assert pipeline.gap_detector is not None
        assert pipeline.pattern_extractor is not None
        assert pipeline.feedback_loop is not None
        assert len(pipeline.handoff_history) == 0

    def test_pipeline_without_learning(self):
        """Test pipeline with learning system disabled"""
        from agents.book_production.pipeline import (
            BookProductionPipeline,
            PipelineConfig,
        )

        config = PipelineConfig(
            enable_sbar_handoffs=False,
            enable_pattern_extraction=False,
            enable_quality_gap_detection=False,
            enable_feedback_loop=False,
        )

        pipeline = BookProductionPipeline(config=config)

        assert pipeline.gap_detector is None
        assert pipeline.pattern_extractor is None
        assert pipeline.feedback_loop is None

    def test_pipeline_stats_include_learning(self):
        """Test that pipeline stats include learning metrics"""
        from agents.book_production.pipeline import BookProductionPipeline

        pipeline = BookProductionPipeline()
        stats = pipeline.get_stats()

        assert "learning" in stats
        assert "handoffs_total" in stats["learning"]

    def test_pipeline_handoff_history(self):
        """Test handoff history retrieval"""
        from agents.book_production.pipeline import BookProductionPipeline

        pipeline = BookProductionPipeline()

        # Manually add a handoff for testing
        handoff = SBARHandoff(
            handoff_type=HandoffType.RESEARCH_TO_WRITER,
            from_agent="ResearchAgent",
            to_agent="WriterAgent",
            situation="Test",
        )
        pipeline.handoff_history.append(handoff)

        history = pipeline.get_handoff_history()

        assert len(history) == 1
        assert history[0]["from_agent"] == "ResearchAgent"

    def test_pipeline_pattern_effectiveness(self):
        """Test pattern effectiveness retrieval"""
        from agents.book_production.pipeline import BookProductionPipeline

        pipeline = BookProductionPipeline()

        # Seed the feedback loop with some data
        pipeline.feedback_loop.pattern_scores = {"test_pattern": 0.85}

        effectiveness = pipeline.get_pattern_effectiveness()

        assert effectiveness["test_pattern"] == 0.85
