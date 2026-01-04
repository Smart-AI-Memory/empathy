"""Book Chapter Wizard - Level 4 Anticipatory Empathy

Transforms technical documentation into polished book chapters.

This wizard encodes the patterns discovered during the creation of
"Persistent Memory for AI" book, where 5 chapters + 5 appendices
were written in ~2 hours through systematic transformation of
existing documentation.

Key Insight: Technical docs contain the knowledge, but not the
narrative structure. This wizard bridges that gap.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import os
import re
import sys
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from empathy_os.plugins import BaseWizard


class BookChapterWizard(BaseWizard):
    """Level 4 Anticipatory: Transforms technical docs into book chapters.

    Key Insight from Experience:
    When writing the MemDocs/Empathy book, we discovered that existing
    documentation could be transformed into high-quality book chapters
    in minutes rather than hours by following consistent patterns.

    This wizard automates that transformation process.
    """

    # Chapter structure template (what made our chapters successful)
    CHAPTER_STRUCTURE = {
        "opening_quote": "Memorable quote setting the theme",
        "introduction": {
            "hook": "Why this topic matters",
            "preview": "What you'll learn (bullet points)",
            "context": "How this connects to previous chapters",
        },
        "sections": {
            "count": "5-7 substantive sections",
            "structure": {
                "concept": "Explain the idea",
                "code_example": "Show it in action",
                "real_world": "Connect to practical use",
            },
        },
        "key_takeaways": "5-6 bullet points summarizing chapter",
        "exercise": "Hands-on 'Try It Yourself' activity",
        "navigation": "Next chapter link",
    }

    # Voice patterns (extracted from successful chapters)
    VOICE_PATTERNS = {
        "authority": "State facts confidently without hedging",
        "practicality": "Every concept should have code",
        "progression": "Build complexity gradually",
        "callbacks": "Reference earlier chapters",
        "foreshadowing": "Hint at upcoming topics",
    }

    def __init__(self):
        super().__init__(
            name="Book Chapter Wizard",
            domain="documentation",
            empathy_level=4,
            category="content_transformation",
        )

    def get_required_context(self) -> list[str]:
        """Required context for analysis"""
        return [
            "source_document",  # Path to source technical doc
            "chapter_number",  # Target chapter number
            "chapter_title",  # Target chapter title
            "book_context",  # Brief context about the book
        ]

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze source document and generate transformation plan.

        Returns a complete blueprint for chapter creation.
        """
        self.validate_context(context)

        source_doc = context["source_document"]
        chapter_num = context["chapter_number"]
        chapter_title = context["chapter_title"]
        book_context = context.get("book_context", "")

        # Read and analyze source document
        source_content = self._read_source(source_doc)
        if not source_content:
            return self._error_result(f"Could not read source: {source_doc}")

        # Extract key elements from source
        elements = await self._extract_elements(source_content)

        # Generate transformation plan
        transformation_plan = await self._create_transformation_plan(
            elements,
            chapter_num,
            chapter_title,
            book_context,
        )

        # Level 4: Predict potential issues
        predictions = await self._predict_transformation_issues(elements, transformation_plan)

        # Generate chapter outline
        outline = self._generate_outline(elements, chapter_num, chapter_title)

        # Generate draft content
        draft = await self._generate_draft(
            elements,
            outline,
            chapter_num,
            chapter_title,
            book_context,
        )

        return {
            "source_analysis": elements,
            "transformation_plan": transformation_plan,
            "predictions": predictions,
            "outline": outline,
            "draft": draft,
            "recommendations": self._generate_recommendations(predictions),
            "confidence": 0.88,
            "metadata": {
                "wizard": self.name,
                "empathy_level": self.empathy_level,
                "source_words": len(source_content.split()),
                "estimated_chapter_words": len(draft.split()) if draft else 0,
            },
        }

    def _read_source(self, source_path: str) -> str:
        """Read source document content."""
        try:
            with open(source_path, encoding="utf-8") as f:
                return f.read()
        except OSError:
            return ""

    async def _extract_elements(self, content: str) -> dict[str, Any]:
        """Extract key elements from source document."""
        return {
            "headings": self._extract_headings(content),
            "code_blocks": self._extract_code_blocks(content),
            "key_concepts": self._extract_concepts(content),
            "metrics": self._extract_metrics(content),
            "examples": self._extract_examples(content),
            "word_count": len(content.split()),
            "complexity": self._assess_complexity(content),
        }

    def _extract_headings(self, content: str) -> list[dict]:
        """Extract markdown headings with levels."""
        headings = []
        for match in re.finditer(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE):
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                },
            )
        return headings

    def _extract_code_blocks(self, content: str) -> list[dict]:
        """Extract code blocks with language hints."""
        blocks = []
        pattern = r"```(\w*)\n(.*?)```"
        for match in re.finditer(pattern, content, re.DOTALL):
            blocks.append(
                {
                    "language": match.group(1) or "text",
                    "code": match.group(2).strip(),
                    "lines": len(match.group(2).strip().split("\n")),
                },
            )
        return blocks

    def _extract_concepts(self, content: str) -> list[str]:
        """Extract key concepts (bold text, definitions)."""
        concepts = []
        # Bold text often indicates key concepts
        for match in re.finditer(r"\*\*([^*]+)\*\*", content):
            concept = match.group(1).strip()
            if len(concept) < 50:  # Reasonable concept length
                concepts.append(concept)
        return list(set(concepts))[:20]  # Dedupe, limit

    def _extract_metrics(self, content: str) -> list[str]:
        """Extract metrics and numbers (good for book credibility)."""
        metrics = []
        # Look for percentage patterns
        for match in re.finditer(r"\d+\.?\d*%", content):
            metrics.append(match.group(0))
        # Look for multiplier patterns
        for match in re.finditer(r"\d+\.?\d*x\s+\w+", content):
            metrics.append(match.group(0))
        return list(set(metrics))[:10]

    def _extract_examples(self, content: str) -> list[str]:
        """Extract example scenarios."""
        examples = []
        # Look for "Example:" or "For example" sections
        pattern = r"(?:Example|For example)[:\s]+([^\n]+(?:\n(?!\n)[^\n]+)*)"
        for match in re.finditer(pattern, content, re.IGNORECASE):
            examples.append(match.group(1).strip()[:200])
        return examples[:5]

    def _assess_complexity(self, content: str) -> str:
        """Assess content complexity."""
        code_ratio = content.count("```") / max(1, len(content.split()) / 100)
        if code_ratio > 2:
            return "high_code"
        if "architecture" in content.lower() or "system" in content.lower():
            return "architectural"
        if len(content.split()) < 500:
            return "brief"
        return "standard"

    async def _create_transformation_plan(
        self,
        elements: dict,
        chapter_num: int,
        chapter_title: str,
        book_context: str,
    ) -> dict[str, Any]:
        """Create a plan for transforming source to chapter."""
        return {
            "approach": self._determine_approach(elements),
            "structure_mapping": {
                "source_headings_to_sections": self._map_headings(elements["headings"]),
                "code_integration": f"{len(elements['code_blocks'])} blocks to integrate",
                "concepts_to_define": elements["key_concepts"][:10],
                "metrics_to_highlight": elements["metrics"],
            },
            "additions_needed": [
                "Opening quote",
                "Introduction with learning objectives",
                "Key takeaways section",
                "Try It Yourself exercise",
                "Next chapter navigation",
            ],
            "voice_adjustments": [
                "Convert technical jargon to accessible language",
                "Add narrative flow between sections",
                "Include 'why this matters' context",
                "Add real-world analogies where appropriate",
            ],
            "estimated_expansion": self._estimate_expansion(elements),
        }

    def _determine_approach(self, elements: dict) -> str:
        """Determine transformation approach based on content."""
        if elements["complexity"] == "high_code":
            return "code_first: Lead with examples, explain after"
        if elements["complexity"] == "architectural":
            return "concept_first: Explain architecture, then show implementation"
        if elements["complexity"] == "brief":
            return "expansion: Significantly expand with examples and context"
        return "balanced: Mix concepts and code throughout"

    def _map_headings(self, headings: list) -> list[dict]:
        """Map source headings to chapter sections."""
        mapped = []
        section_num = 1
        for h in headings:
            if h["level"] <= 2:
                mapped.append(
                    {
                        "source": h["text"],
                        "target_section": f"Section {section_num}: {h['text']}",
                        "recommendation": "Keep and expand",
                    },
                )
                section_num += 1
        return mapped

    def _estimate_expansion(self, elements: dict) -> str:
        """Estimate how much expansion is needed."""
        source_words = elements["word_count"]
        if source_words < 500:
            return f"High expansion needed: {source_words} → ~3000 words (6x)"
        if source_words < 1500:
            return f"Moderate expansion: {source_words} → ~3500 words (2-3x)"
        return f"Light expansion: {source_words} → ~4000 words (1.5x)"

    async def _predict_transformation_issues(
        self,
        elements: dict,
        plan: dict,
    ) -> list[dict[str, Any]]:
        """Level 4: Predict issues before they occur."""
        predictions = []

        # Check for missing code examples
        if len(elements["code_blocks"]) < 3:
            predictions.append(
                {
                    "type": "insufficient_code",
                    "alert": (
                        "Source has fewer than 3 code examples. "
                        "Book chapters benefit from 5-8 code blocks for engagement."
                    ),
                    "probability": "high",
                    "impact": "medium",
                    "prevention": "Add additional examples during transformation",
                },
            )

        # Check for missing metrics
        if not elements["metrics"]:
            predictions.append(
                {
                    "type": "missing_metrics",
                    "alert": (
                        "No metrics found in source. "
                        "Readers trust content more with concrete numbers."
                    ),
                    "probability": "high",
                    "impact": "medium",
                    "prevention": "Add relevant metrics from project data",
                },
            )

        # Check for concept density
        if len(elements["key_concepts"]) > 15:
            predictions.append(
                {
                    "type": "concept_overload",
                    "alert": (
                        f"Found {len(elements['key_concepts'])} key concepts. "
                        "Consider splitting into multiple chapters or prioritizing."
                    ),
                    "probability": "medium",
                    "impact": "high",
                    "prevention": "Focus on 8-10 core concepts, defer others",
                },
            )

        # Check for missing examples
        if len(elements["examples"]) < 2:
            predictions.append(
                {
                    "type": "insufficient_examples",
                    "alert": (
                        "Few practical examples found. "
                        "Book chapters need real-world scenarios to resonate."
                    ),
                    "probability": "high",
                    "impact": "high",
                    "prevention": "Create 2-3 relatable use cases",
                },
            )

        return predictions

    def _generate_outline(
        self,
        elements: dict,
        chapter_num: int,
        chapter_title: str,
    ) -> str:
        """Generate chapter outline."""
        outline = f"""# Chapter {chapter_num}: {chapter_title}

> "Opening quote here"

## Introduction

- Why this topic matters
- What you'll learn:
  - Learning objective 1
  - Learning objective 2
  - Learning objective 3
- Connection to previous chapters

---

"""
        # Add sections from source headings
        for _i, h in enumerate(elements["headings"][:7], 1):
            if h["level"] <= 2:
                outline += f"""## {h["text"]}

[Transform content from source]
[Add code example]
[Add practical application]

---

"""

        outline += """## Key Takeaways

1. Takeaway 1
2. Takeaway 2
3. Takeaway 3
4. Takeaway 4
5. Takeaway 5

---

## Try It Yourself

**Exercise: [Title]**

1. Step 1
2. Step 2
3. Step 3

**Expected outcome**: [Description]

---

**Next:** [Chapter N+1: Title](./next-chapter.md)
"""
        return outline

    async def _generate_draft(
        self,
        elements: dict,
        outline: str,
        chapter_num: int,
        chapter_title: str,
        book_context: str,
    ) -> str:
        """Generate draft chapter content."""
        # This would ideally call an LLM for full generation
        # For now, return enhanced outline with guidance
        draft = f"""# Chapter {chapter_num}: {chapter_title}

> "Quote to be selected based on chapter theme"

## Introduction

[Opening hook connecting to reader's experience]

Throughout this book, we've explored [previous context]. Now we turn to {chapter_title.lower()}, which [significance].

**What You'll Learn:**
"""
        # Add learning objectives from concepts
        for _i, concept in enumerate(elements["key_concepts"][:4], 1):
            draft += f"- {concept}\n"

        draft += "\n---\n\n"

        # Add sections with code blocks
        for i, h in enumerate(elements["headings"][:6], 1):
            if h["level"] <= 2:
                draft += f"## {h['text']}\n\n"
                draft += "[Expand this section with narrative and examples]\n\n"

                # Add relevant code block if available
                if i <= len(elements["code_blocks"]):
                    block = elements["code_blocks"][i - 1]
                    draft += f"```{block['language']}\n{block['code']}\n```\n\n"

                draft += "---\n\n"

        # Add key takeaways
        draft += """## Key Takeaways

"""
        for i, concept in enumerate(elements["key_concepts"][:5], 1):
            draft += f"{i}. **{concept}** - [Expand with one-sentence summary]\n"

        draft += """
---

## Try It Yourself

**Exercise: Apply What You've Learned**

1. [First step based on chapter content]
2. [Second step building on first]
3. [Third step completing the exercise]

**Expected outcome**: [What success looks like]

---

**Next:** [Next Chapter Title](./next-chapter.md)
"""
        return draft

    def _generate_recommendations(self, predictions: list) -> list[str]:
        """Generate actionable recommendations."""
        recs = []

        for pred in predictions:
            if pred.get("impact") in ["high", "medium"]:
                recs.append(f"[{pred['type'].upper()}] {pred['alert']}")
                recs.append(f"  → Prevention: {pred['prevention']}")

        if not recs:
            recs.append("Source document is well-suited for transformation.")
            recs.append("Proceed with standard chapter structure.")

        return recs

    def _error_result(self, message: str) -> dict[str, Any]:
        """Return error result."""
        return {
            "error": message,
            "confidence": 0.0,
            "metadata": {"wizard": self.name},
        }
