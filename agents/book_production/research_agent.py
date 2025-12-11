"""
Research Agent - Source Material Gathering

The first agent in the book production pipeline. Responsible for:
1. Finding relevant source documents
2. Extracting key elements (headings, code, concepts, metrics)
3. Creating a research summary for the Writer Agent
4. Assessing source material adequacy

Uses Claude Sonnet for fast, structured extraction.

Key Insight:
Good research makes writing faster. Spending time on thorough
extraction pays dividends in the writing phase.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import re
from pathlib import Path
from typing import Any

from .base import SonnetAgent
from .state import AgentPhase, ChapterSpec, ResearchResult, SourceDocument


class ResearchAgent(SonnetAgent):
    """
    Gathers and analyzes source material for chapter production.

    Model: Claude Sonnet (fast, good at structured extraction)

    Responsibilities:
    - Find relevant documentation files
    - Extract headings, code blocks, concepts, metrics
    - Assess source adequacy for target chapter
    - Identify gaps that need filling
    - Create research summary for Writer Agent
    """

    name = "ResearchAgent"
    description = "Gathers and analyzes source material for book chapters"
    empathy_level = 4

    def get_system_prompt(self) -> str:
        """System prompt for research extraction"""
        return """You are a research assistant specializing in technical documentation analysis.

Your task is to extract and organize key elements from source documents that will
be used to write a book chapter.

For each source document, identify:
1. **Headings**: All section headers with their hierarchy
2. **Code Blocks**: All code examples with their languages
3. **Key Concepts**: Important terms and definitions (in bold)
4. **Metrics**: Numbers, percentages, and quantifiable claims
5. **Examples**: Real-world use cases and scenarios
6. **Diagrams**: ASCII diagrams or references to visuals

Output your analysis in a structured format that the Writer Agent can use.

Be thorough but focused - extract what's relevant to the chapter topic.
Note any gaps where additional research or examples may be needed."""

    async def process(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Process source documents and extract research.

        Args:
            state: Current pipeline state

        Returns:
            Updated state with research results
        """
        self.logger.info(
            f"Starting research for Chapter {state['chapter_number']}: {state['chapter_title']}"
        )

        # Update state to show we're active
        state = self.add_audit_entry(
            state,
            action="research_started",
            details={"chapter": state["chapter_number"]},
        )
        state["current_agent"] = self.name
        state["current_phase"] = AgentPhase.RESEARCH.value

        # Get source paths from spec or search for them
        source_paths = state.get("source_paths", [])
        if not source_paths:
            source_paths = await self._find_relevant_sources(state)

        # Process each source document
        source_documents = []
        total_words = 0
        all_concepts = []
        code_count = 0

        for path in source_paths:
            self.logger.info(f"Processing source: {path}")

            try:
                source_doc = await self._analyze_source(path, state["chapter_title"])
                source_documents.append(source_doc)
                total_words += source_doc["word_count"]
                all_concepts.extend(source_doc["key_concepts"])
                code_count += len(source_doc["code_blocks"])
            except Exception as e:
                self.logger.warning(f"Failed to process source {path}: {e}")
                state["warnings"].append(f"Could not process source: {path}")

        # Deduplicate concepts
        unique_concepts = list(set(all_concepts))[:20]

        # Create research summary
        summary = await self._create_research_summary(
            source_documents,
            state["chapter_title"],
            state.get("book_context", ""),
        )

        # Assess research adequacy
        confidence = self._assess_research_adequacy(
            source_documents,
            state.get("target_word_count", 4000),
        )

        # Check for patterns in MemDocs
        patterns = await self.search_patterns(
            query=f"chapter research {state['chapter_title']}",
            collection="patterns",
            limit=3,
        )

        # Update state with research results
        state["source_documents"] = source_documents
        state["research_summary"] = summary
        state["total_source_words"] = total_words
        state["key_concepts_extracted"] = unique_concepts
        state["code_examples_found"] = code_count
        state["research_confidence"] = confidence
        state["patterns_retrieved"].extend([p.get("pattern_id", "") for p in patterns])

        # Mark phase complete
        completed = list(state.get("completed_phases", []))
        completed.append(AgentPhase.RESEARCH.value)
        state["completed_phases"] = completed

        # Add audit entry
        state = self.add_audit_entry(
            state,
            action="research_completed",
            details={
                "sources_processed": len(source_documents),
                "total_words": total_words,
                "concepts_extracted": len(unique_concepts),
                "code_examples": code_count,
                "confidence": confidence,
            },
        )

        self.logger.info(
            f"Research complete: {len(source_documents)} sources, "
            f"{total_words} words, {code_count} code examples, "
            f"confidence: {confidence:.2f}"
        )

        return state

    async def research(self, spec: ChapterSpec) -> ResearchResult:
        """
        Standalone research method for direct use.

        Args:
            spec: Chapter specification

        Returns:
            ResearchResult with extracted information
        """
        from .state import create_initial_state

        # Create state from spec
        state = create_initial_state(
            chapter_number=spec.number,
            chapter_title=spec.title,
            book_context=spec.book_context,
            target_word_count=spec.target_word_count,
        )
        state["source_paths"] = spec.source_paths

        # Process
        result_state = await self.process(state)

        return ResearchResult(
            sources=result_state["source_documents"],
            summary=result_state["research_summary"],
            key_concepts=result_state["key_concepts_extracted"],
            code_examples=result_state["code_examples_found"],
            confidence=result_state["research_confidence"],
        )

    async def _find_relevant_sources(self, state: dict[str, Any]) -> list[str]:
        """
        Find relevant source documents for the chapter topic.

        Uses multiple strategies:
        1. Look for files with matching names
        2. Search for topic keywords in docs directory
        3. Check MemDocs for previously used sources
        """
        sources = []
        chapter_title = state["chapter_title"].lower()

        # Strategy 1: Look in common documentation directories
        search_dirs = [
            Path("docs"),
            Path("documentation"),
            Path("README.md").parent,
        ]

        # Extract keywords from title
        keywords = [
            word
            for word in chapter_title.replace("-", " ").replace("_", " ").split()
            if len(word) > 3 and word not in {"chapter", "part", "with", "from", "into"}
        ]

        for search_dir in search_dirs:
            if search_dir.exists() and search_dir.is_dir():
                for md_file in search_dir.rglob("*.md"):
                    file_lower = str(md_file).lower()
                    if any(kw in file_lower for kw in keywords):
                        sources.append(str(md_file))

        self.logger.info(f"Found {len(sources)} potentially relevant sources")
        return sources[:10]  # Limit to top 10

    async def _analyze_source(
        self,
        path: str,
        chapter_title: str,
    ) -> SourceDocument:
        """
        Analyze a single source document.

        Extracts:
        - Headings with hierarchy
        - Code blocks with languages
        - Key concepts (bold text)
        - Metrics (numbers, percentages)
        - Relevance score
        """
        content = self.read_file(path)

        if not content:
            return SourceDocument(
                path=path,
                content="",
                word_count=0,
                headings=[],
                code_blocks=[],
                key_concepts=[],
                metrics=[],
                relevance_score=0.0,
            )

        # Extract elements (reusing patterns from BookChapterWizard)
        headings = self._extract_headings(content)
        code_blocks = self._extract_code_blocks(content)
        concepts = self._extract_concepts(content)
        metrics = self._extract_metrics(content)

        # Calculate relevance score
        relevance = self._calculate_relevance(content, chapter_title)

        return SourceDocument(
            path=path,
            content=content,
            word_count=self.count_words(content),
            headings=headings,
            code_blocks=code_blocks,
            key_concepts=concepts,
            metrics=metrics,
            relevance_score=relevance,
        )

    def _extract_headings(self, content: str) -> list[dict]:
        """Extract markdown headings with levels"""
        headings = []
        for match in re.finditer(r"^(#{1,6})\s+(.+)$", content, re.MULTILINE):
            headings.append(
                {
                    "level": len(match.group(1)),
                    "text": match.group(2).strip(),
                }
            )
        return headings

    def _extract_code_blocks(self, content: str) -> list[dict]:
        """Extract code blocks with language hints"""
        blocks = []
        pattern = r"```(\w*)\n(.*?)```"
        for match in re.finditer(pattern, content, re.DOTALL):
            blocks.append(
                {
                    "language": match.group(1) or "text",
                    "code": match.group(2).strip(),
                    "lines": len(match.group(2).strip().split("\n")),
                }
            )
        return blocks

    def _extract_concepts(self, content: str) -> list[str]:
        """Extract key concepts (bold text)"""
        concepts = []
        for match in re.finditer(r"\*\*([^*]+)\*\*", content):
            concept = match.group(1).strip()
            if len(concept) < 50:  # Reasonable concept length
                concepts.append(concept)
        return list(set(concepts))[:20]

    def _extract_metrics(self, content: str) -> list[str]:
        """Extract metrics and numbers"""
        metrics = []
        # Percentages
        for match in re.finditer(r"\d+\.?\d*%", content):
            metrics.append(match.group(0))
        # Multipliers
        for match in re.finditer(r"\d+\.?\d*x\s+\w+", content):
            metrics.append(match.group(0))
        return list(set(metrics))[:10]

    def _calculate_relevance(self, content: str, chapter_title: str) -> float:
        """Calculate how relevant source is to chapter"""
        content_lower = content.lower()
        title_words = chapter_title.lower().split()

        # Count keyword matches
        matches = sum(1 for word in title_words if word in content_lower and len(word) > 3)

        # Calculate score (0-1)
        if not title_words:
            return 0.5

        score = min(1.0, matches / len(title_words))
        return round(score, 2)

    async def _create_research_summary(
        self,
        sources: list[SourceDocument],
        chapter_title: str,
        book_context: str,
    ) -> str:
        """Create a summary of research findings for the Writer Agent"""
        if not sources:
            return "No source documents found. Manual research required."

        # Build summary
        summary_parts = [
            f"## Research Summary for Chapter: {chapter_title}\n",
            f"**Sources Analyzed:** {len(sources)}\n",
        ]

        # Total stats
        total_words = sum(s["word_count"] for s in sources)
        total_code = sum(len(s["code_blocks"]) for s in sources)
        all_concepts = []
        for s in sources:
            all_concepts.extend(s["key_concepts"])

        summary_parts.append(f"**Total Source Words:** {total_words:,}")
        summary_parts.append(f"**Code Examples Found:** {total_code}")
        summary_parts.append(f"**Key Concepts:** {len(set(all_concepts))}\n")

        # Top sources by relevance
        sorted_sources = sorted(sources, key=lambda s: s["relevance_score"], reverse=True)
        summary_parts.append("### Top Sources by Relevance:\n")
        for i, source in enumerate(sorted_sources[:5], 1):
            summary_parts.append(
                f"{i}. {source['path']} (relevance: {source['relevance_score']:.0%})"
            )

        # Key concepts
        summary_parts.append("\n### Key Concepts to Cover:\n")
        unique_concepts = list(set(all_concepts))[:10]
        for concept in unique_concepts:
            summary_parts.append(f"- {concept}")

        # Code coverage
        if total_code > 0:
            summary_parts.append(f"\n### Code Examples ({total_code} total):\n")
            for source in sources:
                for block in source["code_blocks"][:2]:  # First 2 per source
                    summary_parts.append(f"- {block['language']}: {block['lines']} lines")

        return "\n".join(summary_parts)

    def _assess_research_adequacy(
        self,
        sources: list[SourceDocument],
        target_word_count: int,
    ) -> float:
        """
        Assess if research is adequate for the target chapter.

        Returns confidence score 0-1 based on:
        - Word count coverage
        - Code example count
        - Concept diversity
        - Source relevance
        """
        if not sources:
            return 0.1

        # Factor 1: Word count coverage (target ~1.5x source material)
        total_words = sum(s["word_count"] for s in sources)
        word_coverage = min(1.0, total_words / (target_word_count * 0.75))

        # Factor 2: Code examples (want 5-8 minimum)
        total_code = sum(len(s["code_blocks"]) for s in sources)
        code_coverage = min(1.0, total_code / 5)

        # Factor 3: Concept diversity (want 10+ unique concepts)
        all_concepts = []
        for s in sources:
            all_concepts.extend(s["key_concepts"])
        concept_coverage = min(1.0, len(set(all_concepts)) / 10)

        # Factor 4: Average relevance
        avg_relevance = sum(s["relevance_score"] for s in sources) / len(sources)

        # Weighted average
        confidence = (
            word_coverage * 0.3
            + code_coverage * 0.25
            + concept_coverage * 0.25
            + avg_relevance * 0.2
        )

        return round(confidence, 2)
