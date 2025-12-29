"""
Tests for BookChapterWizard

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import sys
import tempfile

import pytest

from empathy_software_plugin.wizards.book_chapter_wizard import BookChapterWizard


@pytest.fixture
def wizard():
    """Create BookChapterWizard instance."""
    return BookChapterWizard()


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


class TestBookChapterWizard:
    """Test suite for BookChapterWizard."""

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly."""
        assert wizard.name == "Book Chapter Wizard"
        assert wizard.empathy_level == 4
        assert wizard.domain == "documentation"

    def test_required_context(self, wizard):
        """Test required context fields."""
        required = wizard.get_required_context()
        assert "source_document" in required
        assert "chapter_number" in required
        assert "chapter_title" in required

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_analyze_basic(self, wizard, sample_source_doc):
        """Test basic analysis of source document."""
        context = {
            "source_document": sample_source_doc,
            "chapter_number": 23,
            "chapter_title": "Multi-Agent Coordination",
            "book_context": "AI Memory Systems book",
        }

        result = await wizard.analyze(context)

        assert "source_analysis" in result
        assert "transformation_plan" in result
        assert "outline" in result
        assert "draft" in result
        assert result["confidence"] > 0.5

        # Cleanup
        os.unlink(sample_source_doc)

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_extract_elements(self, wizard, sample_source_doc):
        """Test element extraction from source."""
        with open(sample_source_doc) as f:
            content = f.read()

        elements = await wizard._extract_elements(content)

        assert "headings" in elements
        assert "code_blocks" in elements
        assert "key_concepts" in elements
        assert "metrics" in elements
        assert len(elements["headings"]) > 0
        assert len(elements["code_blocks"]) > 0

        # Cleanup
        os.unlink(sample_source_doc)

    def test_extract_headings(self, wizard):
        """Test heading extraction."""
        content = """# Title
## Section 1
### Subsection
## Section 2
"""
        headings = wizard._extract_headings(content)

        assert len(headings) == 4
        assert headings[0]["level"] == 1
        assert headings[0]["text"] == "Title"
        assert headings[1]["level"] == 2

    def test_extract_code_blocks(self, wizard):
        """Test code block extraction."""
        content = """```python
def hello():
    print("Hello")
```

```javascript
console.log("Hi");
```
"""
        blocks = wizard._extract_code_blocks(content)

        assert len(blocks) == 2
        assert blocks[0]["language"] == "python"
        assert blocks[1]["language"] == "javascript"

    def test_extract_concepts(self, wizard):
        """Test key concept extraction."""
        content = """
**Multi-agent systems** are important.
Use **pattern libraries** for sharing.
The **confidence score** matters.
"""
        concepts = wizard._extract_concepts(content)

        assert "Multi-agent systems" in concepts
        assert "pattern libraries" in concepts
        assert "confidence score" in concepts

    def test_extract_metrics(self, wizard):
        """Test metric extraction."""
        content = """
Achieved 80% faster delivery.
Saw 2.5x improvement.
Coverage went from 32% to 90%.
"""
        metrics = wizard._extract_metrics(content)

        assert any("80%" in m for m in metrics)
        assert any("32%" in m for m in metrics)
        assert any("90%" in m for m in metrics)

    def test_assess_complexity(self, wizard):
        """Test complexity assessment."""
        # High code content
        code_heavy = "```python\n" * 10 + "test " * 50
        assert wizard._assess_complexity(code_heavy) == "high_code"

        # Architectural content
        arch_content = "The system architecture uses components and structure " * 20
        assert wizard._assess_complexity(arch_content) == "architectural"

        # Brief content
        brief = "Short content here."
        assert wizard._assess_complexity(brief) == "brief"

    @pytest.mark.asyncio
    async def test_predictions(self, wizard):
        """Test issue prediction."""
        elements = {
            "code_blocks": [{"language": "python", "code": "x=1", "lines": 1}],
            "metrics": [],
            "key_concepts": ["concept"] * 20,
            "examples": [],
        }
        plan = {}

        predictions = await wizard._predict_transformation_issues(elements, plan)

        # Should predict insufficient code
        assert any(p["type"] == "insufficient_code" for p in predictions)
        # Should predict missing metrics
        assert any(p["type"] == "missing_metrics" for p in predictions)
        # Should predict concept overload
        assert any(p["type"] == "concept_overload" for p in predictions)

    def test_generate_outline(self, wizard):
        """Test outline generation."""
        elements = {
            "headings": [
                {"level": 1, "text": "Main Title"},
                {"level": 2, "text": "Section One"},
                {"level": 2, "text": "Section Two"},
            ],
            "key_concepts": ["Concept A", "Concept B"],
        }

        outline = wizard._generate_outline(elements, 23, "Test Chapter")

        assert "Chapter 23: Test Chapter" in outline
        assert "Introduction" in outline
        assert "Key Takeaways" in outline
        assert "Try It Yourself" in outline

    @pytest.mark.asyncio
    async def test_missing_source_error(self, wizard):
        """Test error handling for missing source."""
        context = {
            "source_document": "/nonexistent/file.md",
            "chapter_number": 1,
            "chapter_title": "Test",
            "book_context": "Test book",
        }

        result = await wizard.analyze(context)

        assert "error" in result
        assert result["confidence"] == 0.0

    def test_chapter_structure_template(self, wizard):
        """Test chapter structure template is complete."""
        structure = wizard.CHAPTER_STRUCTURE

        assert "opening_quote" in structure
        assert "introduction" in structure
        assert "sections" in structure
        assert "key_takeaways" in structure
        assert "exercise" in structure
        assert "navigation" in structure

    def test_voice_patterns(self, wizard):
        """Test voice patterns are defined."""
        patterns = wizard.VOICE_PATTERNS

        assert "authority" in patterns
        assert "practicality" in patterns
        assert "progression" in patterns


class TestBookChapterWizardIntegration:
    """Integration tests for BookChapterWizard."""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        sys.platform == "win32", reason="UnicodeEncodeError with charmap codec on Windows"
    )
    async def test_full_transformation_flow(self, wizard, sample_source_doc):
        """Test complete transformation workflow."""
        context = {
            "source_document": sample_source_doc,
            "chapter_number": 23,
            "chapter_title": "Distributed Memory Networks",
            "book_context": "MemDocs and Empathy Framework book",
        }

        result = await wizard.analyze(context)

        # Verify all outputs present
        assert result["source_analysis"]["word_count"] > 0
        assert len(result["transformation_plan"]["additions_needed"]) > 0
        assert "Chapter 23" in result["outline"]
        assert "Chapter 23" in result["draft"]
        assert len(result["recommendations"]) > 0

        # Verify metadata
        assert result["metadata"]["wizard"] == "Book Chapter Wizard"
        assert result["metadata"]["empathy_level"] == 4

        # Cleanup
        os.unlink(sample_source_doc)
