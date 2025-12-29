"""
Tests for Book Production Pipeline Agents

Tests the multi-agent system for book production including:
- State management
- ResearchAgent
- WriterAgent
- Agent coordination

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
import tempfile
from unittest.mock import AsyncMock, MagicMock

import pytest

from agents.book_production import (
    AgentConfig,
    AgentPhase,
    ChapterSpec,
    Draft,
    MemDocsConfig,
    OpusAgent,
    RedisConfig,
    ResearchAgent,
    ResearchResult,
    SonnetAgent,
    SourceDocument,
    WriterAgent,
    create_initial_state,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_source_doc():
    """Create a sample source document for testing."""
    content = """# Multi-Agent Coordination

Enable multiple AI agents to work together on complex tasks.

## Overview

**Multi-agent systems** allow specialized AI agents to collaborate:

- **Code Review Agent** - Reviews PRs for bugs
- **Test Generation Agent** - Creates tests
- **Security Agent** - Scans for vulnerabilities

**Result**: **80% faster feature delivery** through parallel work.

## Architecture

```
┌─────────────────────────────────────────┐
│         Shared Pattern Library          │
└─────────────────────────────────────────┘
```

## Quick Start

```python
from empathy_os import EmpathyOS
from empathy_os.pattern_library import PatternLibrary

# Shared pattern library for all agents
shared_library = PatternLibrary(name="team_library")

# Create specialized agents
code_reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,
    shared_library=shared_library
)
```

## Performance Benefits

Before: **8 hours** for full workflow
After: **4 hours** with parallel agents
Improvement: **50% time reduction**

## Best Practices

Example: When using multi-agent systems, always define clear boundaries.

For example, the Security Agent should focus only on security concerns.
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(content)
        return f.name


@pytest.fixture
def mock_llm_provider():
    """Create a mock LLM provider for testing."""
    provider = MagicMock()
    provider.generate = AsyncMock(
        return_value=(
            "# Chapter 23: Test Chapter\n\n"
            "This is test content with **key concepts**.\n\n"
            "```python\nprint('hello')\n```\n\n"
            "## Key Takeaways\n\n1. First point\n2. Second point"
        )
    )
    return provider


@pytest.fixture
def research_agent(mock_llm_provider):
    """Create ResearchAgent with mock LLM."""
    config = AgentConfig(model="claude-sonnet-4-20250514")
    memdocs_config = MemDocsConfig(enabled=False)
    redis_config = RedisConfig(enabled=False)

    return ResearchAgent(
        config=config,
        memdocs_config=memdocs_config,
        redis_config=redis_config,
        llm_provider=mock_llm_provider,
    )


@pytest.fixture
def writer_agent(mock_llm_provider):
    """Create WriterAgent with mock LLM."""
    config = AgentConfig(model="claude-opus-4-5-20250514", max_tokens=12000)
    memdocs_config = MemDocsConfig(enabled=False)
    redis_config = RedisConfig(enabled=False)

    return WriterAgent(
        config=config,
        memdocs_config=memdocs_config,
        redis_config=redis_config,
        llm_provider=mock_llm_provider,
    )


# =============================================================================
# State Management Tests
# =============================================================================


class TestStateManagement:
    """Test state management functionality."""

    def test_create_initial_state(self):
        """Test creating initial pipeline state."""
        state = create_initial_state(
            chapter_number=23,
            chapter_title="Distributed Memory Networks",
            book_title="Persistent Memory for AI",
            book_context="Part 6 of the book",
            target_word_count=4000,
        )

        assert state["chapter_number"] == 23
        assert state["chapter_title"] == "Distributed Memory Networks"
        assert state["book_title"] == "Persistent Memory for AI"
        assert state["target_word_count"] == 4000
        assert state["current_phase"] == AgentPhase.RESEARCH.value
        assert state["completed_phases"] == []
        assert state["current_version"] == 0
        assert state["approved_for_publication"] is False

    def test_initial_state_has_execution_id(self):
        """Test that initial state has unique execution ID."""
        state1 = create_initial_state(chapter_number=1, chapter_title="Test")
        state2 = create_initial_state(chapter_number=1, chapter_title="Test")

        assert state1["execution_id"] != state2["execution_id"]
        assert state1["execution_id"].startswith("chapter_1_")

    def test_quality_score_initialization(self):
        """Test quality scores are initialized to zero."""
        state = create_initial_state(chapter_number=1, chapter_title="Test")

        assert state["quality_scores"]["overall"] == 0.0
        assert state["quality_scores"]["structure"] == 0.0
        assert state["quality_scores"]["code_quality"] == 0.0


class TestChapterSpec:
    """Test ChapterSpec dataclass."""

    def test_chapter_spec_creation(self):
        """Test creating a chapter specification."""
        spec = ChapterSpec(
            number=23,
            title="Distributed Memory Networks",
            source_paths=["docs/multi-agent.md"],
            topic="multi-agent coordination",
            book_context="Part 6",
            target_word_count=4000,
        )

        assert spec.number == 23
        assert spec.title == "Distributed Memory Networks"
        assert len(spec.source_paths) == 1

    def test_chapter_spec_defaults(self):
        """Test default values in ChapterSpec."""
        spec = ChapterSpec(number=1, title="Introduction")

        assert spec.source_paths == []
        assert spec.target_word_count == 4000
        assert spec.previous_chapter_summary == ""


# =============================================================================
# Base Agent Tests
# =============================================================================


class TestBaseAgent:
    """Test BaseAgent functionality."""

    def test_agent_config_defaults(self):
        """Test AgentConfig default values."""
        config = AgentConfig()

        assert config.model == "claude-sonnet-4-20250514"
        assert config.max_tokens == 8000
        assert config.temperature == 0.7
        assert config.retry_attempts == 3

    def test_memdocs_config_collections(self):
        """Test MemDocsConfig collection defaults."""
        config = MemDocsConfig()

        assert config.enabled is True
        assert "patterns" in config.collections
        assert "exemplars" in config.collections
        assert config.project == "book-production"

    def test_redis_config_defaults(self):
        """Test RedisConfig default values."""
        config = RedisConfig()

        assert config.enabled is True
        assert config.host == "localhost"
        assert config.port == 6379
        assert config.prefix == "book_production"

    def test_opus_agent_default_model(self):
        """Test OpusAgent uses Opus model by default."""
        assert OpusAgent.DEFAULT_MODEL == "claude-opus-4-5-20250514"

    def test_sonnet_agent_default_model(self):
        """Test SonnetAgent uses Sonnet model by default."""
        assert SonnetAgent.DEFAULT_MODEL == "claude-sonnet-4-20250514"


# =============================================================================
# Research Agent Tests
# =============================================================================


class TestResearchAgent:
    """Test ResearchAgent functionality."""

    def test_agent_initialization(self, research_agent):
        """Test ResearchAgent initializes correctly."""
        assert research_agent.name == "ResearchAgent"
        assert research_agent.empathy_level == 4
        assert research_agent.config.model == "claude-sonnet-4-20250514"

    def test_system_prompt(self, research_agent):
        """Test ResearchAgent has proper system prompt."""
        prompt = research_agent.get_system_prompt()

        assert "research" in prompt.lower()
        assert "extract" in prompt.lower()
        assert "code" in prompt.lower()

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_process_updates_state(self, research_agent, sample_source_doc):
        """Test process() updates state correctly."""
        state = create_initial_state(
            chapter_number=23,
            chapter_title="Multi-Agent Coordination",
        )
        state["source_paths"] = [sample_source_doc]

        result = await research_agent.process(state)

        assert result["current_phase"] == AgentPhase.RESEARCH.value
        assert len(result["source_documents"]) > 0
        assert result["research_confidence"] > 0
        assert AgentPhase.RESEARCH.value in result["completed_phases"]

        # Cleanup
        os.unlink(sample_source_doc)

    @pytest.mark.asyncio
    async def test_extract_headings(self, research_agent):
        """Test heading extraction from markdown."""
        content = """# Title
## Section 1
### Subsection
## Section 2
"""
        headings = research_agent._extract_headings(content)

        assert len(headings) == 4
        assert headings[0]["level"] == 1
        assert headings[0]["text"] == "Title"
        assert headings[1]["level"] == 2

    @pytest.mark.asyncio
    async def test_extract_code_blocks(self, research_agent):
        """Test code block extraction."""
        content = """```python
def hello():
    print("Hello")
```

```javascript
console.log("Hi");
```
"""
        blocks = research_agent._extract_code_blocks(content)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert blocks[1]["language"] == "javascript"

    @pytest.mark.asyncio
    async def test_extract_concepts(self, research_agent):
        """Test key concept extraction."""
        content = """
**Multi-agent systems** are important.
Use **pattern libraries** for sharing.
The **confidence score** matters.
"""
        concepts = research_agent._extract_concepts(content)

        assert "Multi-agent systems" in concepts
        assert "pattern libraries" in concepts
        assert "confidence score" in concepts

    @pytest.mark.asyncio
    async def test_extract_metrics(self, research_agent):
        """Test metric extraction."""
        content = """
Achieved 80% faster delivery.
Saw 2.5x improvement.
Coverage went from 32% to 90%.
"""
        metrics = research_agent._extract_metrics(content)

        assert any("80%" in m for m in metrics)
        assert any("32%" in m for m in metrics)
        assert any("90%" in m for m in metrics)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_research_result_creation(self, research_agent, sample_source_doc):
        """Test ResearchResult is properly created."""
        spec = ChapterSpec(
            number=23,
            title="Multi-Agent Coordination",
            source_paths=[sample_source_doc],
        )

        result = await research_agent.research(spec)

        assert isinstance(result, ResearchResult)
        assert len(result.sources) > 0
        assert result.confidence > 0
        assert len(result.key_concepts) > 0

        # Cleanup
        os.unlink(sample_source_doc)


# =============================================================================
# Writer Agent Tests
# =============================================================================


class TestWriterAgent:
    """Test WriterAgent functionality."""

    def test_agent_initialization(self, writer_agent):
        """Test WriterAgent initializes correctly."""
        assert writer_agent.name == "WriterAgent"
        assert writer_agent.empathy_level == 4
        assert writer_agent.config.model == "claude-opus-4-5-20250514"
        assert writer_agent.config.max_tokens == 12000

    def test_system_prompt_includes_voice_patterns(self, writer_agent):
        """Test WriterAgent system prompt includes voice patterns."""
        prompt = writer_agent.get_system_prompt()

        assert "authority" in prompt.lower()
        assert "practicality" in prompt.lower()
        assert "callbacks" in prompt.lower()

    def test_system_prompt_includes_chapter_structure(self, writer_agent):
        """Test system prompt includes chapter structure requirements."""
        prompt = writer_agent.get_system_prompt()

        assert "opening quote" in prompt.lower()
        assert "introduction" in prompt.lower()
        assert "key takeaways" in prompt.lower()
        assert "try it yourself" in prompt.lower()

    def test_chapter_structure_template(self, writer_agent):
        """Test chapter structure template is defined."""
        structure = writer_agent.CHAPTER_STRUCTURE

        assert "opening_quote" in structure
        assert "introduction" in structure
        assert "sections" in structure
        assert "key_takeaways" in structure
        assert "exercise" in structure

    def test_voice_patterns_defined(self, writer_agent):
        """Test voice patterns are defined."""
        patterns = writer_agent.VOICE_PATTERNS

        assert "authority" in patterns
        assert "practicality" in patterns
        assert "progression" in patterns
        assert "callbacks" in patterns
        assert "foreshadowing" in patterns

    @pytest.mark.asyncio
    async def test_process_creates_draft(self, writer_agent):
        """Test process() creates a draft."""
        state = create_initial_state(
            chapter_number=23,
            chapter_title="Multi-Agent Coordination",
        )
        state["source_documents"] = [
            SourceDocument(
                path="test.md",
                content="Test content about **multi-agent systems**",
                word_count=100,
                headings=[{"level": 1, "text": "Test"}],
                code_blocks=[{"language": "python", "code": "print('test')", "lines": 1}],
                key_concepts=["multi-agent systems"],
                metrics=["80%"],
                relevance_score=0.9,
            )
        ]
        state["research_summary"] = "Research summary for testing"
        state["key_concepts_extracted"] = ["multi-agent systems", "coordination"]
        state["code_examples_found"] = 1
        state["research_confidence"] = 0.85

        result = await writer_agent.process(state)

        assert result["current_draft"] != ""
        assert result["current_version"] == 1
        assert len(result["draft_versions"]) == 1
        assert AgentPhase.WRITING.value in result["completed_phases"]

    @pytest.mark.asyncio
    async def test_write_standalone_method(self, writer_agent):
        """Test standalone write() method."""
        research = ResearchResult(
            sources=[
                SourceDocument(
                    path="test.md",
                    content="Test content",
                    word_count=100,
                    headings=[],
                    code_blocks=[],
                    key_concepts=["concept1"],
                    metrics=[],
                    relevance_score=0.8,
                )
            ],
            summary="Test summary",
            key_concepts=["concept1", "concept2"],
            code_examples=0,
            confidence=0.8,
        )

        spec = ChapterSpec(
            number=23,
            title="Test Chapter",
            target_word_count=3000,
        )

        draft = await writer_agent.write(research, spec)

        assert isinstance(draft, Draft)
        assert draft.version == 1
        assert draft.content != ""


# =============================================================================
# Agent Coordination Tests
# =============================================================================


class TestAgentCoordination:
    """Test agents working together."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_research_to_writer_flow(self, research_agent, writer_agent, sample_source_doc):
        """Test data flows correctly from Research to Writer."""
        # Research phase
        spec = ChapterSpec(
            number=23,
            title="Multi-Agent Coordination",
            source_paths=[sample_source_doc],
        )

        research_result = await research_agent.research(spec)

        assert research_result.confidence > 0
        assert len(research_result.sources) > 0

        # Writing phase
        draft = await writer_agent.write(research_result, spec)

        assert draft.content != ""
        assert draft.version == 1

        # Cleanup
        os.unlink(sample_source_doc)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_audit_trail_accumulates(self, research_agent, sample_source_doc):
        """Test audit trail entries are added correctly."""
        state = create_initial_state(
            chapter_number=23,
            chapter_title="Test Chapter",
        )
        state["source_paths"] = [sample_source_doc]

        result = await research_agent.process(state)

        assert len(result["audit_trail"]) >= 2  # start and complete entries
        assert any(e["action"] == "research_started" for e in result["audit_trail"])
        assert any(e["action"] == "research_completed" for e in result["audit_trail"])

        # Cleanup
        os.unlink(sample_source_doc)


# =============================================================================
# Integration Tests (require external services)
# =============================================================================


class TestIntegration:
    """Integration tests - skipped by default."""

    @pytest.mark.skip(reason="Requires Redis")
    @pytest.mark.asyncio
    async def test_redis_state_storage(self, research_agent):
        """Test Redis state storage."""
        research_agent.redis_config.enabled = True

        await research_agent.set_state("test_key", {"data": "test"})
        result = await research_agent.get_state("test_key")

        assert result["data"] == "test"

    @pytest.mark.skip(reason="Requires MemDocs")
    @pytest.mark.asyncio
    async def test_memdocs_pattern_storage(self, research_agent):
        """Test MemDocs pattern storage."""
        research_agent.memdocs_config.enabled = True

        pattern_id = await research_agent.store_pattern(
            {"pattern_type": "test", "content": "test pattern"},
            collection="patterns",
        )

        assert pattern_id != ""

    @pytest.mark.skip(reason="Requires Anthropic API key")
    @pytest.mark.asyncio
    async def test_real_llm_generation(self):
        """Test actual LLM generation."""
        agent = WriterAgent()
        response = await agent.generate("Say hello in one word.")

        assert "hello" in response.lower() or "hi" in response.lower()
