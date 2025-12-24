# Book Production Pipeline: Multi-Agent + Long-Term Memory Architecture

**Status:** Implementation Plan
**Created:** December 2025
**Author:** Patrick Roebuck + Claude Opus 4.5

---

## Executive Summary

This plan details the implementation of a **Multi-Agent Book Production Pipeline** (Option C) integrated with **Long-Term Memory-Powered Learning** (Option D). The goal is to systematize the rapid, high-quality content generation demonstrated during the creation of "Persistent Memory for AI" book.

**Key Achievement to Replicate:** 5 chapters + 5 appendices written in ~2 hours with consistent quality.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     BOOK PRODUCTION PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐   ┌─────────────┐    │
│  │  Research   │ → │   Writer    │ → │   Editor    │ → │  Reviewer   │    │
│  │   Agent     │   │   Agent     │   │   Agent     │   │   Agent     │    │
│  │  (Claude)   │   │  (Opus 4.5) │   │  (Sonnet)   │   │  (Opus 4.5) │    │
│  └──────┬──────┘   └──────┬──────┘   └──────┬──────┘   └──────┬──────┘    │
│         │                 │                 │                 │            │
│         └─────────────────┼─────────────────┼─────────────────┘            │
│                           │                 │                              │
│                           ▼                 ▼                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    SHARED PATTERN LIBRARY                            │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐   │  │
│  │  │   Chapter   │ │    Voice    │ │  Structure  │ │   Quality   │   │  │
│  │  │  Templates  │ │   Patterns  │ │   Rules     │ │   Metrics   │   │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘   │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                           │                                                │
│                           ▼                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                         PATTERN_STORAGE                                      │  │
│  │  - Successful chapter patterns                                       │  │
│  │  - Transformation examples                                           │  │
│  │  - Quality feedback loops                                            │  │
│  │  - Cross-book learning                                               │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      REDIS STATE STORE                               │  │
│  │  - Draft versions                                                    │  │
│  │  - Agent progress                                                    │  │
│  │  - Review feedback                                                   │  │
│  │  - Quality scores                                                    │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Research Agent

**Purpose:** Gather and organize source material for chapter creation.

**Model:** Claude Sonnet (fast, cost-effective for research)

```python
class ResearchAgent(BaseAgent):
    """
    Gathers source material for chapter production.

    Capabilities:
    - Find relevant docs in codebase
    - Extract key concepts
    - Identify code examples
    - Map source to chapter structure
    """

    model = "claude-sonnet-4-20250514"

    async def research(self, chapter_spec: ChapterSpec) -> ResearchResult:
        # 1. Find source documents
        sources = await self._find_sources(chapter_spec.topic)

        # 2. Extract elements using BookChapterWizard
        wizard = BookChapterWizard()
        elements = []
        for source in sources:
            result = await wizard.analyze({
                "source_document": source,
                "chapter_number": chapter_spec.number,
                "chapter_title": chapter_spec.title,
                "book_context": chapter_spec.book_context,
            })
            elements.append(result)

        # 3. Store in Redis for Writer Agent
        await self.redis.set(
            f"research:{chapter_spec.id}",
            json.dumps({"sources": sources, "elements": elements})
        )

        return ResearchResult(sources=sources, elements=elements)
```

### 2. Writer Agent

**Purpose:** Transform research into polished chapter drafts.

**Model:** Claude Opus 4.5 (highest quality for creative writing)

```python
class WriterAgent(BaseAgent):
    """
    Produces chapter drafts from research material.

    Capabilities:
    - Transform technical docs to narrative
    - Apply voice patterns consistently
    - Generate code examples
    - Create exercises and takeaways
    """

    model = "claude-opus-4-5-20250514"

    async def write(self, research: ResearchResult, spec: ChapterSpec) -> Draft:
        # 1. Retrieve patterns from Long-Term Memory
        patterns = await self.pattern-storage.search(
            collection="book_patterns",
            query=f"chapter transformation {spec.topic}",
            limit=5
        )

        # 2. Generate chapter using template + patterns
        prompt = self._build_writing_prompt(research, spec, patterns)

        draft = await self.llm.generate(
            prompt=prompt,
            system=self._writer_system_prompt(),
            max_tokens=8000
        )

        # 3. Store draft in Redis
        await self.redis.set(
            f"draft:{spec.id}:v1",
            json.dumps({"content": draft, "version": 1})
        )

        return Draft(content=draft, version=1)

    def _writer_system_prompt(self) -> str:
        return """You are an expert technical writer creating book chapters.

Voice Patterns:
- Authority: State facts confidently
- Practicality: Every concept needs code
- Progression: Build complexity gradually
- Callbacks: Reference earlier chapters
- Foreshadowing: Hint at upcoming topics

Chapter Structure:
1. Opening quote (memorable, thematic)
2. Introduction (hook, learning objectives, context)
3. 5-7 substantive sections with code
4. Key takeaways (5-6 bullets)
5. Try It Yourself exercise
6. Next chapter navigation

Write in clear, engaging prose. Use tables for comparisons.
Include 5-8 code examples per chapter."""
```

### 3. Editor Agent

**Purpose:** Polish drafts for consistency and quality.

**Model:** Claude Sonnet (fast iteration on editing)

```python
class EditorAgent(BaseAgent):
    """
    Polishes drafts for publication quality.

    Capabilities:
    - Check voice consistency
    - Verify code correctness
    - Ensure structural compliance
    - Flag missing elements
    """

    model = "claude-sonnet-4-20250514"

    async def edit(self, draft: Draft, spec: ChapterSpec) -> EditResult:
        # 1. Load style guide from Long-Term Memory
        style_guide = await self.pattern-storage.get("style_guide")

        # 2. Check against quality rules
        issues = await self._check_quality(draft, style_guide)

        # 3. Make automated fixes
        edited_draft = await self._apply_fixes(draft, issues)

        # 4. Store edited version
        await self.redis.set(
            f"draft:{spec.id}:v{draft.version + 1}",
            json.dumps({"content": edited_draft, "version": draft.version + 1})
        )

        return EditResult(
            draft=edited_draft,
            issues_found=len(issues),
            issues_fixed=len([i for i in issues if i.auto_fixable])
        )
```

### 4. Reviewer Agent

**Purpose:** Final quality check before publication.

**Model:** Claude Opus 4.5 (nuanced quality assessment)

```python
class ReviewerAgent(BaseAgent):
    """
    Final quality gate for chapters.

    Capabilities:
    - Assess overall quality
    - Check technical accuracy
    - Verify reader experience
    - Score against benchmarks
    """

    model = "claude-opus-4-5-20250514"

    async def review(self, edited_draft: Draft, spec: ChapterSpec) -> ReviewResult:
        # 1. Load successful chapter examples from Long-Term Memory
        exemplars = await self.pattern-storage.search(
            collection="exemplar_chapters",
            query=spec.topic,
            limit=3
        )

        # 2. Score against quality criteria
        scores = await self._score_quality(edited_draft, exemplars)

        # 3. Generate detailed feedback
        feedback = await self._generate_feedback(edited_draft, scores)

        # 4. Store review in Long-Term Memory for learning
        if scores["overall"] > 0.85:
            await self.pattern-storage.store(
                collection="exemplar_chapters",
                content={
                    "chapter": spec.title,
                    "draft": edited_draft.content,
                    "scores": scores,
                    "patterns_used": edited_draft.patterns_applied,
                },
                metadata={"quality": "high"}
            )

        return ReviewResult(
            approved=scores["overall"] > 0.80,
            scores=scores,
            feedback=feedback
        )
```

---

## Pipeline Orchestration

### LangChain Integration

```python
from langchain.agents import AgentExecutor
from langchain.chains import SequentialChain

class BookProductionPipeline:
    """
    Orchestrates multi-agent book production.
    """

    def __init__(self):
        self.redis = Redis()
        self.pattern-storage = Long-Term MemoryClient(project="book-production")

        # Initialize agents
        self.research_agent = ResearchAgent(redis=self.redis, pattern-storage=self.pattern-storage)
        self.writer_agent = WriterAgent(redis=self.redis, pattern-storage=self.pattern-storage)
        self.editor_agent = EditorAgent(redis=self.redis, pattern-storage=self.pattern-storage)
        self.reviewer_agent = ReviewerAgent(redis=self.redis, pattern-storage=self.pattern-storage)

    async def produce_chapter(self, spec: ChapterSpec) -> Chapter:
        """
        Full pipeline: Research → Write → Edit → Review
        """
        # Phase 1: Research
        research = await self.research_agent.research(spec)

        # Phase 2: Write
        draft = await self.writer_agent.write(research, spec)

        # Phase 3: Edit (may iterate)
        edited = await self.editor_agent.edit(draft, spec)

        # Phase 4: Review
        review = await self.reviewer_agent.review(edited.draft, spec)

        if not review.approved:
            # Iterate with feedback
            return await self._iterate_with_feedback(spec, edited, review)

        return Chapter(
            content=edited.draft.content,
            quality_score=review.scores["overall"],
            metadata={"pipeline": "v1", "iterations": 1}
        )

    async def produce_book(self, book_spec: BookSpec) -> Book:
        """
        Parallel chapter production for entire book.
        """
        # Produce chapters in parallel
        tasks = [
            self.produce_chapter(chapter_spec)
            for chapter_spec in book_spec.chapters
        ]

        chapters = await asyncio.gather(*tasks)

        return Book(chapters=chapters, metadata=book_spec.metadata)
```

---

## Long-Term Memory Learning System (Option D)

### Pattern Storage Schema

```python
# Collections for book production learning

PATTERN_STORAGE_COLLECTIONS = {
    "book_patterns": {
        "description": "Successful transformation patterns",
        "schema": {
            "pattern_type": str,  # "chapter_structure", "voice", "code_example"
            "source_type": str,   # "technical_doc", "api_reference", "guide"
            "target_type": str,   # "chapter", "appendix", "exercise"
            "pattern": str,       # The actual pattern
            "success_count": int,
            "quality_scores": list[float],
        }
    },

    "exemplar_chapters": {
        "description": "High-quality chapter examples",
        "schema": {
            "chapter_title": str,
            "content": str,
            "quality_score": float,
            "voice_patterns_used": list[str],
            "structure_patterns_used": list[str],
        }
    },

    "transformation_examples": {
        "description": "Source → Chapter transformations",
        "schema": {
            "source_content": str,
            "result_content": str,
            "transformation_approach": str,
            "quality_score": float,
        }
    },

    "quality_feedback": {
        "description": "Human feedback on outputs",
        "schema": {
            "chapter_id": str,
            "rating": int,  # 1-5
            "feedback": str,
            "improvements_applied": list[str],
        }
    }
}
```

### Learning Loop

```python
class BookProductionLearner:
    """
    Continuous improvement system for book production.
    """

    async def learn_from_success(self, chapter: Chapter, feedback: Feedback):
        """
        Extract patterns from successful chapters.
        """
        if feedback.rating >= 4:
            # Extract what worked
            patterns = await self._extract_patterns(chapter)

            for pattern in patterns:
                await self.pattern-storage.store(
                    collection="book_patterns",
                    content=pattern,
                    metadata={"source_chapter": chapter.id}
                )

    async def learn_from_failure(self, chapter: Chapter, feedback: Feedback):
        """
        Learn from unsuccessful chapters.
        """
        if feedback.rating <= 2:
            # Store anti-patterns
            anti_patterns = await self._extract_anti_patterns(
                chapter, feedback.issues
            )

            await self.pattern-storage.store(
                collection="anti_patterns",
                content=anti_patterns,
                metadata={"avoid": True}
            )

    async def improve_prompts(self):
        """
        Periodically update agent prompts based on learning.
        """
        # Get high-performing patterns
        top_patterns = await self.pattern-storage.search(
            collection="book_patterns",
            query="high quality chapter patterns",
            min_score=0.9
        )

        # Update writer system prompt
        new_prompt = self._generate_improved_prompt(top_patterns)
        await self.update_agent_prompt("writer", new_prompt)
```

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
**Status:** ✅ BookChapterWizard created

- [x] Create BookChapterWizard
- [x] Write comprehensive tests
- [ ] Document wizard API
- [ ] Create example usage scripts

### Phase 2: Agent Framework (Week 2)

- [ ] Create BaseAgent class
- [ ] Implement ResearchAgent
- [ ] Implement WriterAgent
- [ ] Add Redis state management
- [ ] Create agent tests

### Phase 3: Pipeline Integration (Week 3)

- [ ] Implement EditorAgent
- [ ] Implement ReviewerAgent
- [ ] Create pipeline orchestrator
- [ ] Add LangChain integration
- [ ] End-to-end pipeline tests

### Phase 4: Long-Term Memory Learning (Week 4)

- [ ] Define collection schemas
- [ ] Implement pattern extraction
- [ ] Create learning loops
- [ ] Add feedback integration
- [ ] Cross-book learning

### Phase 5: Production Deployment (Week 5)

- [ ] Docker containerization
- [ ] API endpoints for pipeline
- [ ] Monitoring and metrics
- [ ] Documentation
- [ ] Launch

---

## Model Selection Strategy

| Agent | Model | Reasoning |
|-------|-------|-----------|
| **Research** | Sonnet | Fast, good at search/extraction |
| **Writer** | Opus 4.5 | Highest quality creative output |
| **Editor** | Sonnet | Quick iteration, rule-based |
| **Reviewer** | Opus 4.5 | Nuanced quality assessment |

**Cost Optimization:**
- Use Sonnet for high-volume, structured tasks
- Reserve Opus 4.5 for quality-critical steps
- Cache patterns in Long-Term Memory to reduce LLM calls

---

## Integration with Existing Systems

### Empathy Framework Integration

```python
from empathy_os import EmpathyOS
from empathy_software_plugin.wizards import BookChapterWizard

# Book production uses Level 4 Anticipatory Empathy
pipeline = BookProductionPipeline(
    empathy_level=4,
    shared_library=PatternLibrary("book_production")
)

# Each agent inherits Level 4 capabilities
# - Predicts reader confusion points
# - Anticipates missing context
# - Proactively adds clarifications
```

### AI-Nurse-Florence Patterns

Reuse patterns from healthcare wizards:

- **Redis state management** from clinical workflows
- **LangChain orchestration** from multi-step protocols
- **Quality scoring** from SBAR validation

---

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Chapter production time | <30 min | Pipeline timing |
| Quality score | >85% | Reviewer agent |
| Human approval rate | >90% | Feedback loop |
| Pattern reuse rate | >60% | Long-Term Memory analytics |
| Cost per chapter | <$5 | LLM API costs |

---

## Next Steps

1. **Immediate:** Test BookChapterWizard on next documentation task
2. **This Week:** Create BaseAgent class and ResearchAgent
3. **Next Week:** Full pipeline MVP with 2 agents
4. **Month 1:** Production deployment with learning loop

---

## Resources

- **BookChapterWizard:** `empathy_software_plugin/wizards/book_chapter_wizard.py`
- **Tests:** `tests/test_book_chapter_wizard.py`
- **AI-Nurse-Florence Patterns:** `10_9_2025_ai_nurse_florence/`
- **Empathy Framework:** `empathy_os/`
- **Long-Term Memory:** [github.com/Smart-AI-Memory/pattern-storage](https://github.com/Smart-AI-Memory/pattern-storage)

---

*This plan transforms ad-hoc book production into a repeatable, improving system.*
*Estimated development: 5 weeks to production pipeline.*
*ROI: 10x faster book production at consistent quality.*
