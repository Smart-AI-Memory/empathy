"""
Reviewer Agent - Quality Assessment

The final quality gate in the book production pipeline. Responsible for:
1. Assessing overall chapter quality against exemplars
2. Checking technical accuracy
3. Evaluating reader experience
4. Scoring against publication benchmarks
5. Deciding approval for publication

Uses Claude Opus 4.5 for nuanced quality assessment.

Key Insight from Experience:
Quality assessment requires judgment, not just rule-checking.
Opus 4.5's nuanced reasoning makes it ideal for this role.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import re
from typing import Any

from .base import OpusAgent
from .state import AgentPhase, Draft, QualityScore, ReviewResult


class ReviewerAgent(OpusAgent):
    """
    Final quality gate for chapters.

    Model: Claude Opus 4.5 (nuanced quality assessment)

    Responsibilities:
    - Assess overall quality against exemplar chapters
    - Check technical accuracy of code and concepts
    - Evaluate reader experience (flow, engagement)
    - Score against multiple quality dimensions
    - Make publication approval decision
    """

    name = "ReviewerAgent"
    description = "Final quality assessment for publication approval"
    empathy_level = 4

    # Quality dimensions and their weights
    QUALITY_DIMENSIONS = {
        "structure": {
            "weight": 0.15,
            "description": "Chapter structure and organization",
            "criteria": [
                "Opening quote present and relevant",
                "Clear introduction with learning objectives",
                "Logical section progression",
                "Key takeaways summarize main points",
                "Exercise reinforces learning",
            ],
        },
        "voice_consistency": {
            "weight": 0.15,
            "description": "Consistent authorial voice throughout",
            "criteria": [
                "Authoritative tone (no hedging)",
                "Practical focus (theory connected to code)",
                "Progressive complexity (simple to advanced)",
                "Appropriate callbacks to earlier chapters",
                "Foreshadowing of future topics",
            ],
        },
        "code_quality": {
            "weight": 0.25,
            "description": "Quality and correctness of code examples",
            "criteria": [
                "Syntactically correct code",
                "Clear comments on non-obvious lines",
                "Complete, runnable examples",
                "Realistic, production-quality patterns",
                "Appropriate variety of languages/techniques",
            ],
        },
        "reader_engagement": {
            "weight": 0.20,
            "description": "How engaging the chapter is for readers",
            "criteria": [
                "Compelling opening hook",
                "Clear 'why this matters' context",
                "Real-world applications shown",
                "Appropriate pacing (not too fast/slow)",
                "Actionable takeaways",
            ],
        },
        "technical_accuracy": {
            "weight": 0.25,
            "description": "Accuracy of technical content",
            "criteria": [
                "Correct terminology usage",
                "Accurate code behavior descriptions",
                "Valid architectural patterns",
                "Up-to-date best practices",
                "No misleading simplifications",
            ],
        },
    }

    # Approval thresholds
    APPROVAL_THRESHOLD = 0.80  # 80% overall score required
    MINIMUM_DIMENSION_SCORE = 0.60  # No dimension below 60%

    def get_system_prompt(self) -> str:
        """System prompt for quality review"""
        return """You are a senior technical reviewer assessing book chapters for publication.

Your role is the final quality gate before a chapter is published.

## Review Dimensions

Assess each chapter on these dimensions (0.0 to 1.0):

1. **Structure** (15%)
   - Opening quote present and thematically relevant
   - Introduction hooks the reader and sets expectations
   - Sections flow logically from simple to complex
   - Key takeaways capture essential learnings
   - Exercise provides meaningful practice

2. **Voice Consistency** (15%)
   - Authoritative tone without hedging
   - Every concept connected to practical code
   - Complexity builds progressively
   - References to earlier chapters where relevant
   - Hints at upcoming topics

3. **Code Quality** (25%)
   - All code is syntactically correct
   - Comments explain non-obvious logic
   - Examples are complete and runnable
   - Patterns reflect production best practices
   - Appropriate variety of techniques shown

4. **Reader Engagement** (20%)
   - Opening hook captures attention
   - Clear "why this matters" context
   - Real-world applications demonstrated
   - Pacing keeps readers engaged
   - Takeaways are actionable

5. **Technical Accuracy** (25%)
   - Terminology used correctly
   - Code behavior described accurately
   - Architectural patterns are valid
   - Best practices are current
   - No oversimplifications that mislead

## Scoring Guidelines

- 0.9-1.0: Exceptional - ready for immediate publication
- 0.8-0.89: Good - minor polish may help but publishable
- 0.7-0.79: Acceptable - some improvements recommended
- 0.6-0.69: Needs work - significant issues to address
- Below 0.6: Not ready - major revision required

## Output Format

Provide:
1. Score for each dimension with brief justification
2. Overall weighted score
3. Specific feedback (2-3 sentences per dimension)
4. Publication recommendation (approve/revise)
5. If revising: prioritized list of improvements

Be thorough but constructive. The goal is publication success."""

    async def process(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Review the edited draft for publication approval.

        Args:
            state: Current pipeline state with edited draft

        Returns:
            Updated state with review results
        """
        self.logger.info(
            f"Starting review for Chapter {state['chapter_number']}: {state['chapter_title']}"
        )

        # Update state
        state = self.add_audit_entry(
            state,
            action="review_started",
            details={"chapter": state["chapter_number"], "version": state["current_version"]},
        )
        state["current_agent"] = self.name
        state["current_phase"] = AgentPhase.REVIEW.value

        draft = state.get("current_draft", "")
        if not draft:
            state["errors"].append("No draft to review")
            return state

        # Retrieve exemplar chapters for comparison
        exemplars = await self.search_patterns(
            query=state["chapter_title"],
            collection="exemplars",
            limit=3,
        )

        # Phase 1: Automated quality checks
        automated_scores = self._automated_quality_check(draft)

        # Phase 2: LLM-based nuanced review
        llm_review = await self._llm_quality_review(
            draft,
            state["chapter_title"],
            exemplars,
        )

        # Phase 3: Combine scores
        final_scores = self._combine_scores(automated_scores, llm_review["scores"])

        # Phase 4: Make approval decision
        approved, feedback = self._make_approval_decision(final_scores, llm_review["feedback"])

        # Calculate confidence
        confidence = self._calculate_confidence(automated_scores, llm_review["scores"])

        # Update state
        state["quality_scores"] = QualityScore(
            overall=final_scores["overall"],
            structure=final_scores["structure"],
            voice_consistency=final_scores["voice_consistency"],
            code_quality=final_scores["code_quality"],
            reader_engagement=final_scores["reader_engagement"],
            technical_accuracy=final_scores["technical_accuracy"],
        )
        state["review_feedback"] = feedback
        state["approved_for_publication"] = approved
        state["reviewer_confidence"] = confidence

        if exemplars:
            state["exemplar_chapters_used"].extend([e.get("pattern_id", "") for e in exemplars])

        # Store as exemplar if high quality
        if approved and final_scores["overall"] >= 0.85:
            await self._store_as_exemplar(state, final_scores)

        # Mark phase complete
        completed = list(state.get("completed_phases", []))
        completed.append(AgentPhase.REVIEW.value)
        state["completed_phases"] = completed

        # Mark overall complete if approved
        if approved:
            state["current_phase"] = AgentPhase.COMPLETE.value
            completed.append(AgentPhase.COMPLETE.value)
            state["completed_phases"] = completed

        # Add audit entry
        state = self.add_audit_entry(
            state,
            action="review_completed",
            details={
                "overall_score": final_scores["overall"],
                "approved": approved,
                "confidence": confidence,
                "feedback_count": len(feedback),
            },
        )

        self.logger.info(
            f"Review complete: score={final_scores['overall']:.2f}, "
            f"approved={approved}, confidence={confidence:.2f}"
        )

        return state

    async def review(self, draft: Draft, chapter_title: str) -> ReviewResult:
        """
        Standalone review method for direct use.

        Args:
            draft: Draft to review
            chapter_title: Chapter title for context

        Returns:
            ReviewResult with scores and feedback
        """
        from .state import create_initial_state

        # Create minimal state
        state = create_initial_state(
            chapter_number=0,
            chapter_title=chapter_title,
        )
        state["current_draft"] = draft.content
        state["current_version"] = draft.version

        # Process
        result_state = await self.process(state)

        return ReviewResult(
            approved=result_state["approved_for_publication"],
            scores=result_state["quality_scores"],
            feedback=result_state["review_feedback"],
            confidence=result_state["reviewer_confidence"],
        )

    def _automated_quality_check(self, draft: str) -> dict[str, float]:
        """Perform automated quality checks"""
        scores = {}

        # Structure check
        structure_elements = [
            r'^>\s*"',  # Opening quote
            r"##\s*(Introduction|Overview)",  # Introduction
            r"\*\*What You'll Learn\*\*",  # Learning objectives
            r"##\s*Key Takeaways",  # Takeaways
            r"##\s*Try It Yourself",  # Exercise
        ]
        found = sum(1 for p in structure_elements if re.search(p, draft, re.MULTILINE))
        scores["structure"] = found / len(structure_elements)

        # Voice consistency (check for hedging)
        hedging_patterns = [r"\bmight\b", r"\bperhaps\b", r"\bpossibly\b", r"\bcould be\b"]
        hedging_count = sum(len(re.findall(p, draft, re.IGNORECASE)) for p in hedging_patterns)
        word_count = len(draft.split())
        hedging_ratio = hedging_count / max(1, word_count / 100)
        scores["voice_consistency"] = max(0, 1.0 - hedging_ratio * 0.1)

        # Code quality (basic checks)
        code_blocks = re.findall(r"```(\w+)\n(.*?)```", draft, re.DOTALL)
        if code_blocks:
            labeled = sum(1 for lang, _ in code_blocks if lang)
            valid_python = 0
            for lang, code in code_blocks:
                if lang == "python":
                    try:
                        compile(code, "<string>", "exec")
                        valid_python += 1
                    except SyntaxError:
                        pass

            python_blocks = sum(1 for lang, _ in code_blocks if lang == "python")
            python_valid_ratio = valid_python / max(1, python_blocks)
            labeled_ratio = labeled / len(code_blocks)
            scores["code_quality"] = (labeled_ratio + python_valid_ratio) / 2
        else:
            scores["code_quality"] = 0.5  # No code to evaluate

        # Reader engagement (check for engagement elements)
        engagement_elements = [
            r"##.*\?",  # Questions in headings
            r"For example",  # Examples
            r"In practice",  # Practical applications
            r"Real-world",  # Real-world context
            r"\*\*Key\*\*|\*\*Important\*\*",  # Emphasis
        ]
        engagement_found = sum(1 for p in engagement_elements if re.search(p, draft, re.IGNORECASE))
        scores["reader_engagement"] = min(1.0, engagement_found / 3)

        # Technical accuracy (basic: check for common errors)
        # This is limited without actual execution
        scores["technical_accuracy"] = 0.75  # Default, will be refined by LLM

        return scores

    async def _llm_quality_review(
        self,
        draft: str,
        chapter_title: str,
        exemplars: list[dict],
    ) -> dict[str, Any]:
        """Use LLM for nuanced quality review"""
        # Build context from exemplars
        exemplar_context = ""
        if exemplars:
            exemplar_context = "\n\n## Reference Exemplar Chapters\n"
            for ex in exemplars[:2]:
                if ex.get("content"):
                    exemplar_context += f"\n### {ex.get('chapter_title', 'Exemplar')}\n"
                    exemplar_context += ex["content"][:1000] + "...\n"

        prompt = f"""Review this chapter for publication quality.

## Chapter: {chapter_title}

{draft[:10000]}

{exemplar_context}

## Required Output

Provide a JSON-formatted review with:

```json
{{
  "scores": {{
    "structure": 0.85,
    "voice_consistency": 0.80,
    "code_quality": 0.90,
    "reader_engagement": 0.75,
    "technical_accuracy": 0.85
  }},
  "feedback": [
    "Strength: Clear progression from basic to advanced concepts",
    "Improvement: Add more real-world application examples in Section 3",
    "Note: Code examples are excellent and production-ready"
  ],
  "recommendation": "approve"
}}
```

Score each dimension 0.0-1.0 based on the criteria in your training.
Provide 3-5 specific feedback items (mix of strengths and improvements).
Recommendation: "approve" if overall >= 0.80, else "revise"."""

        try:
            response = await self.generate(prompt, max_tokens=2000)

            # Parse JSON from response
            import json

            # Find JSON block
            json_match = re.search(r"```json\s*(.*?)\s*```", response, re.DOTALL)
            if json_match:
                review_data = json.loads(json_match.group(1))
            else:
                # Try parsing entire response as JSON
                review_data = json.loads(response)

            return {
                "scores": review_data.get("scores", {}),
                "feedback": review_data.get("feedback", []),
                "recommendation": review_data.get("recommendation", "revise"),
            }

        except Exception as e:
            self.logger.warning(f"LLM review parsing failed: {e}")
            # Return neutral scores
            return {
                "scores": {dim: 0.75 for dim in self.QUALITY_DIMENSIONS},
                "feedback": ["LLM review unavailable - using automated checks only"],
                "recommendation": "revise",
            }

    def _combine_scores(
        self,
        automated: dict[str, float],
        llm_scores: dict[str, float],
    ) -> dict[str, float]:
        """Combine automated and LLM scores"""
        combined = {}

        for dimension in self.QUALITY_DIMENSIONS:
            auto_score = automated.get(dimension, 0.5)
            llm_score = llm_scores.get(dimension, 0.5)

            # Weight: 40% automated, 60% LLM (LLM is more nuanced)
            combined[dimension] = auto_score * 0.4 + llm_score * 0.6

        # Calculate weighted overall
        overall = sum(
            combined[dim] * self.QUALITY_DIMENSIONS[dim]["weight"]
            for dim in self.QUALITY_DIMENSIONS
        )
        combined["overall"] = overall

        return combined

    def _make_approval_decision(
        self,
        scores: dict[str, float],
        llm_feedback: list[str],
    ) -> tuple[bool, list[str]]:
        """Make final approval decision"""
        feedback = list(llm_feedback)

        # Check overall threshold
        if scores["overall"] < self.APPROVAL_THRESHOLD:
            feedback.insert(
                0,
                f"Overall score {scores['overall']:.2f} below threshold {self.APPROVAL_THRESHOLD}",
            )
            return False, feedback

        # Check minimum dimension scores
        for dimension, score in scores.items():
            if dimension != "overall" and score < self.MINIMUM_DIMENSION_SCORE:
                feedback.insert(
                    0,
                    f"{dimension} score {score:.2f} below minimum {self.MINIMUM_DIMENSION_SCORE}",
                )
                return False, feedback

        # Approved
        feedback.insert(0, f"Approved for publication with score {scores['overall']:.2f}")
        return True, feedback

    def _calculate_confidence(
        self,
        automated: dict[str, float],
        llm_scores: dict[str, float],
    ) -> float:
        """Calculate confidence in the review"""
        # Confidence based on agreement between automated and LLM
        agreements = []
        for dimension in self.QUALITY_DIMENSIONS:
            auto = automated.get(dimension, 0.5)
            llm = llm_scores.get(dimension, 0.5)
            # Agreement = 1 - difference
            agreements.append(1.0 - abs(auto - llm))

        return sum(agreements) / len(agreements) if agreements else 0.5

    async def _store_as_exemplar(
        self,
        state: dict[str, Any],
        scores: dict[str, float],
    ) -> None:
        """Store high-quality chapter as exemplar for future reference"""
        exemplar = {
            "chapter_title": state["chapter_title"],
            "chapter_number": state["chapter_number"],
            "content": state["current_draft"][:5000],  # Store excerpt
            "quality_scores": scores,
            "patterns_used": state.get("writing_patterns_applied", []),
        }

        await self.store_pattern(exemplar, collection="exemplars")
        state["patterns_to_store"].append(exemplar)

        self.logger.info(f"Stored chapter as exemplar with score {scores['overall']:.2f}")
