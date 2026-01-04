"""Writer Agent - Chapter Draft Creation

The creative powerhouse of the book production pipeline. Responsible for:
1. Transforming research into narrative prose
2. Applying voice patterns consistently
3. Generating code examples
4. Creating exercises and takeaways

Uses Claude Opus 4.5 for highest quality creative output.

Key Insight from Experience:
The magic happens when technical accuracy meets engaging narrative.
Good chapters teach and entertain simultaneously.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from datetime import datetime
from typing import Any

from .base import OpusAgent
from .state import AgentPhase, ChapterSpec, Draft, DraftVersion, ResearchResult


class WriterAgent(OpusAgent):
    """Transforms research into polished chapter drafts.

    Model: Claude Opus 4.5 (highest quality for creative writing)

    Responsibilities:
    - Transform technical documentation to narrative
    - Apply voice patterns consistently
    - Generate code examples that teach
    - Create exercises and key takeaways
    - Maintain book continuity (callbacks, foreshadowing)
    """

    name = "WriterAgent"
    description = "Creates polished chapter drafts from research material"
    empathy_level = 4

    # Chapter structure (what makes successful chapters)
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

    def get_system_prompt(self) -> str:
        """System prompt for chapter writing"""
        return """You are an expert technical writer creating book chapters for
"Persistent Memory for AI" - a book about MemDocs and the Empathy Framework.

## Your Writing Voice

- **Authority**: State facts confidently. "MemDocs stores patterns" not "MemDocs might store patterns"
- **Practicality**: Every concept needs working code. Readers learn by doing.
- **Progression**: Build from simple to complex. Don't assume knowledge.
- **Callbacks**: Reference earlier chapters: "As we saw in Chapter 5..."
- **Foreshadowing**: Hint at what's coming: "We'll explore this further in Chapter 12..."

## Chapter Structure

Every chapter must include:

1. **Opening Quote** - Memorable, thematic quote (real or appropriately attributed)

2. **Introduction** (300-400 words)
   - Hook: Why this topic matters RIGHT NOW
   - What You'll Learn: 3-5 bullet points
   - Context: Connection to previous chapters

3. **Main Sections** (5-7 sections, 400-600 words each)
   - Each section: Concept → Code → Real-world application
   - Use tables for comparisons
   - Include 5-8 total code examples

4. **Key Takeaways** (5-6 bullets)
   - Actionable, memorable points
   - Start with verbs: "Use...", "Remember...", "Implement..."

5. **Try It Yourself** (hands-on exercise)
   - 3-5 concrete steps
   - Expected outcome clearly stated
   - Builds on chapter content

6. **Navigation**
   - Link to next chapter

## Code Examples

- Always include language identifier: ```python
- Add comments explaining key lines
- Use realistic, production-quality code
- Show complete, runnable examples when possible

## Formatting

- Use --- for section breaks
- Bold **key terms** on first use
- Use tables for comparisons (| Header | Header |)
- Include ASCII diagrams for architecture

Write with clarity, enthusiasm, and deep technical knowledge.
Your goal: Readers finish the chapter excited to implement what they learned."""

    async def process(self, state: dict[str, Any]) -> dict[str, Any]:
        """Create chapter draft from research.

        Args:
            state: Current pipeline state with research results

        Returns:
            Updated state with draft content

        """
        self.logger.info(
            f"Starting writing for Chapter {state['chapter_number']}: {state['chapter_title']}",
        )

        # Update state
        state = self.add_audit_entry(
            state,
            action="writing_started",
            details={"chapter": state["chapter_number"]},
        )
        state["current_agent"] = self.name
        state["current_phase"] = AgentPhase.WRITING.value

        # Retrieve patterns from MemDocs
        writing_patterns = await self.search_patterns(
            query=f"chapter writing {state['chapter_title']} voice structure",
            collection="patterns",
            limit=5,
        )

        # Retrieve exemplar chapters
        exemplars = await self.search_patterns(
            query=state["chapter_title"],
            collection="exemplars",
            limit=2,
        )

        # Generate outline first
        outline = await self._generate_outline(state)
        state["outline"] = outline

        # Generate full chapter draft
        draft_content = await self._generate_draft(state, outline, writing_patterns)

        # Create draft version
        draft_version = DraftVersion(
            version=1,
            content=draft_content,
            word_count=self.count_words(draft_content),
            created_at=datetime.now().isoformat(),
            created_by=self.name,
            changes_summary="Initial draft from research material",
        )

        # Update state
        state["current_draft"] = draft_content
        state["draft_versions"] = [draft_version]
        state["current_version"] = 1
        state["writing_patterns_applied"] = [
            p.get("pattern_id", "voice_authority") for p in writing_patterns
        ] or ["voice_authority", "code_first", "progressive_complexity"]

        if exemplars:
            state["exemplar_chapters_used"] = [e.get("pattern_id", "") for e in exemplars]

        # Mark phase complete
        completed = list(state.get("completed_phases", []))
        completed.append(AgentPhase.WRITING.value)
        state["completed_phases"] = completed

        # Store successful patterns
        if self.count_words(draft_content) >= state.get("target_word_count", 4000) * 0.8:
            await self._store_writing_patterns(state, draft_content)

        # Add audit entry
        state = self.add_audit_entry(
            state,
            action="writing_completed",
            details={
                "word_count": self.count_words(draft_content),
                "sections": draft_content.count("## "),
                "code_blocks": draft_content.count("```"),
                "patterns_applied": len(state["writing_patterns_applied"]),
            },
        )

        self.logger.info(
            f"Writing complete: {self.count_words(draft_content)} words, "
            f"{draft_content.count('## ')} sections, "
            f"{draft_content.count('```')} code blocks",
        )

        return state

    async def write(
        self,
        research: ResearchResult,
        spec: ChapterSpec,
    ) -> Draft:
        """Standalone write method for direct use.

        Args:
            research: Research results from ResearchAgent
            spec: Chapter specification

        Returns:
            Draft with chapter content

        """
        from .state import create_initial_state

        # Create state from research and spec
        state = create_initial_state(
            chapter_number=spec.number,
            chapter_title=spec.title,
            book_context=spec.book_context,
            target_word_count=spec.target_word_count,
        )

        # Add research results
        state["source_documents"] = research.sources
        state["research_summary"] = research.summary
        state["key_concepts_extracted"] = research.key_concepts
        state["code_examples_found"] = research.code_examples
        state["research_confidence"] = research.confidence

        # Process
        result_state = await self.process(state)

        return Draft(
            content=result_state["current_draft"],
            version=result_state["current_version"],
            word_count=self.count_words(result_state["current_draft"]),
            patterns_applied=result_state["writing_patterns_applied"],
        )

    async def _generate_outline(self, state: dict[str, Any]) -> str:
        """Generate chapter outline from research"""
        # Build outline prompt
        concepts = state.get("key_concepts_extracted", [])[:10]
        code_count = state.get("code_examples_found", 0)

        prompt = f"""Create a detailed outline for Chapter {state["chapter_number"]}: {state["chapter_title"]}

## Research Summary
{state.get("research_summary", "No research summary available")}

## Key Concepts to Cover
{chr(10).join(f"- {c}" for c in concepts)}

## Available Code Examples: {code_count}

## Book Context
{state.get("book_context", "Part of a book about AI memory systems")}

Create an outline following this structure:
1. Opening Quote (suggest a relevant quote)
2. Introduction with hook and learning objectives
3. 5-7 main sections (each with concept + code + application)
4. Key Takeaways (5-6 bullets)
5. Try It Yourself exercise
6. Next chapter navigation

For each main section, include:
- Section title
- Key concept to explain
- Suggested code example
- Real-world application

Output the outline in Markdown format."""

        outline = await self.generate(prompt)
        return outline

    async def _generate_draft(
        self,
        state: dict[str, Any],
        outline: str,
        patterns: list[dict],
    ) -> str:
        """Generate full chapter draft"""
        # Build comprehensive writing prompt
        sources = state.get("source_documents", [])
        concepts = state.get("key_concepts_extracted", [])

        # Extract source content for context
        source_content = ""
        for source in sources[:3]:  # Top 3 sources
            if source.get("content"):
                source_content += f"\n\n### Source: {source['path']}\n"
                # Include first 2000 chars
                source_content += source["content"][:2000]

        prompt = f"""Write Chapter {state["chapter_number"]}: {state["chapter_title"]}

## Outline
{outline}

## Key Concepts to Explain
{chr(10).join(f"- **{c}**" for c in concepts[:10])}

## Source Material for Reference
{source_content if source_content else "No source content available - use your knowledge"}

## Requirements
- Target word count: {state.get("target_word_count", 4000)} words
- Include 5-8 code examples
- Follow the chapter structure exactly
- Apply voice patterns: authority, practicality, progression
- Include callbacks to earlier chapters where appropriate
- Add foreshadowing for upcoming chapters

## Book Context
{state.get("book_context", "")}

Previous chapter summary: {state.get("previous_chapter_summary", "Not provided")}
Next chapter hint: {state.get("next_chapter_hint", "To be determined")}

Write the complete chapter now. Start with the opening quote and work through
each section of the outline. Make it engaging, technically accurate, and actionable."""

        # Use higher token limit for full chapter
        draft = await self.generate(
            prompt=prompt,
            max_tokens=12000,
            temperature=0.7,
        )

        return draft

    async def _store_writing_patterns(
        self,
        state: dict[str, Any],
        draft: str,
    ) -> None:
        """Store successful writing patterns in MemDocs"""
        # Extract patterns from successful draft
        patterns_to_store = []

        # Pattern: Chapter structure
        section_count = draft.count("## ")
        code_count = draft.count("```")
        word_count = self.count_words(draft)

        if section_count >= 5 and code_count >= 5:
            patterns_to_store.append(
                {
                    "pattern_type": "chapter_structure",
                    "description": f"Successful chapter with {section_count} sections, {code_count} code blocks",
                    "metrics": {
                        "sections": section_count,
                        "code_blocks": code_count,
                        "word_count": word_count,
                    },
                    "chapter_title": state["chapter_title"],
                    "chapter_number": state["chapter_number"],
                },
            )

        # Store patterns
        for pattern in patterns_to_store:
            await self.store_pattern(pattern, collection="patterns")
            state["patterns_to_store"].append(pattern)
