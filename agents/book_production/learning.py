"""
Learning System - MemDocs Pattern Extraction and Feedback Loops

Enables the book production pipeline to learn from successful chapters
and continuously improve quality through structured feedback.

Healthcare-Inspired Patterns Applied:
1. SBAR Handoffs - Structured agent-to-agent communication
2. Quality Gap Detection - Severity-based issue tracking
3. Anticipatory Windows - Predict issues before they occur
4. Trust-Building Behaviors - Pre-format output for recipients

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Literal

logger = logging.getLogger(__name__)


# =============================================================================
# SBAR Agent Handoffs
# =============================================================================


class HandoffType(Enum):
    """Types of agent handoffs in the pipeline"""

    RESEARCH_TO_WRITER = "research_to_writer"
    WRITER_TO_EDITOR = "writer_to_editor"
    EDITOR_TO_REVIEWER = "editor_to_reviewer"
    REVIEWER_TO_WRITER = "reviewer_to_writer"  # Revision feedback


@dataclass
class SBARHandoff:
    """
    SBAR-format handoff between agents.

    Adapted from clinical SBAR (Situation, Background, Assessment, Recommendation)
    for structured agent-to-agent communication.

    Benefits:
    - Standardized format reduces misinterpretation
    - Receiving agent knows exactly what to focus on
    - Audit trail for debugging and improvement
    - Trust-building: each agent pre-formats for the next
    """

    # Handoff metadata
    handoff_type: HandoffType
    from_agent: str
    to_agent: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # SBAR Components
    situation: str = ""  # Current state of the chapter/task
    background: str = ""  # What the sending agent did, key decisions made
    assessment: str = ""  # Quality metrics, confidence, concerns
    recommendation: str = ""  # Specific guidance for receiving agent

    # Structured data for receiving agent
    key_metrics: dict[str, Any] = field(default_factory=dict)
    focus_areas: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    artifacts: dict[str, str] = field(default_factory=dict)  # Named content pieces

    def to_prompt_context(self) -> str:
        """Format handoff as context for the receiving agent's prompt."""
        sections = [
            f"## Handoff from {self.from_agent}",
            "",
            f"**Situation:** {self.situation}",
            "",
            f"**Background:** {self.background}",
            "",
            f"**Assessment:** {self.assessment}",
            "",
            f"**Recommendation:** {self.recommendation}",
        ]

        if self.focus_areas:
            sections.append("")
            sections.append("**Priority Focus Areas:**")
            for area in self.focus_areas:
                sections.append(f"- {area}")

        if self.known_issues:
            sections.append("")
            sections.append("**Known Issues to Address:**")
            for issue in self.known_issues:
                sections.append(f"- {issue}")

        if self.key_metrics:
            sections.append("")
            sections.append("**Key Metrics:**")
            for key, value in self.key_metrics.items():
                sections.append(f"- {key}: {value}")

        return "\n".join(sections)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage/serialization."""
        return {
            "handoff_type": self.handoff_type.value,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "timestamp": self.timestamp,
            "situation": self.situation,
            "background": self.background,
            "assessment": self.assessment,
            "recommendation": self.recommendation,
            "key_metrics": self.key_metrics,
            "focus_areas": self.focus_areas,
            "known_issues": self.known_issues,
            "artifacts": self.artifacts,
        }


def create_research_to_writer_handoff(state: dict[str, Any]) -> SBARHandoff:
    """Create SBAR handoff from ResearchAgent to WriterAgent."""
    sources = state.get("source_documents", [])
    concepts = state.get("key_concepts_extracted", [])
    code_count = state.get("code_examples_found", 0)
    confidence = state.get("research_confidence", 0.0)

    # Determine focus areas based on research gaps
    focus_areas = []
    if confidence < 0.7:
        focus_areas.append("Research coverage is limited - supplement with framework knowledge")
    if code_count < 5:
        focus_areas.append(f"Only {code_count} code examples found - generate additional examples")
    if len(concepts) < 5:
        focus_areas.append("Few key concepts extracted - expand conceptual coverage")

    # Identify known issues
    known_issues = []
    low_relevance = [s for s in sources if s.get("relevance_score", 0) < 0.5]
    if low_relevance:
        known_issues.append(
            f"{len(low_relevance)} sources have low relevance - verify applicability"
        )

    return SBARHandoff(
        handoff_type=HandoffType.RESEARCH_TO_WRITER,
        from_agent="ResearchAgent",
        to_agent="WriterAgent",
        situation=f"Research complete for Chapter {state['chapter_number']}: {state['chapter_title']}. "
        f"Gathered {len(sources)} sources with {state.get('total_source_words', 0):,} words.",
        background=f"Analyzed sources for key concepts ({len(concepts)} found), "
        f"code examples ({code_count} found), and relevance scoring. "
        f"Research summary prepared with structured extraction.",
        assessment=f"Research confidence: {confidence:.0%}. "
        f"{'Adequate' if confidence >= 0.7 else 'Limited'} material for target chapter. "
        f"Top concepts: {', '.join(concepts[:5]) if concepts else 'None identified'}.",
        recommendation="Write chapter following outline structure. "
        + ("Supplement thin areas with framework expertise. " if confidence < 0.7 else "")
        + "Ensure each concept has a code example.",
        key_metrics={
            "sources_count": len(sources),
            "total_words": state.get("total_source_words", 0),
            "concepts_count": len(concepts),
            "code_examples": code_count,
            "confidence": f"{confidence:.0%}",
        },
        focus_areas=focus_areas,
        known_issues=known_issues,
        artifacts={
            "research_summary": state.get("research_summary", ""),
            "outline": state.get("outline", ""),
        },
    )


def create_writer_to_editor_handoff(state: dict[str, Any]) -> SBARHandoff:
    """Create SBAR handoff from WriterAgent to EditorAgent."""
    draft = state.get("current_draft", "")
    word_count = len(draft.split())
    target_count = state.get("target_word_count", 4000)
    sections = draft.count("## ")
    code_blocks = draft.count("```")
    patterns = state.get("writing_patterns_applied", [])

    # Identify areas needing attention
    focus_areas = []
    if word_count < target_count * 0.8:
        focus_areas.append(
            f"Draft is {word_count} words, target is {target_count} - may need expansion"
        )
    elif word_count > target_count * 1.2:
        focus_areas.append(
            f"Draft is {word_count} words, target is {target_count} - consider tightening"
        )

    if sections < 5:
        focus_areas.append(f"Only {sections} sections - verify structure completeness")

    if code_blocks < 5:
        focus_areas.append(f"Only {code_blocks} code blocks - verify technical depth")

    # Check for common issues
    known_issues = []
    hedging_count = len(re.findall(r"\b(might|perhaps|possibly|could be)\b", draft, re.IGNORECASE))
    if hedging_count > 5:
        known_issues.append(f"Found {hedging_count} hedging phrases - needs voice strengthening")

    unlabeled_code = len(re.findall(r"```\n", draft))
    if unlabeled_code > 0:
        known_issues.append(f"{unlabeled_code} unlabeled code blocks - add language identifiers")

    return SBARHandoff(
        handoff_type=HandoffType.WRITER_TO_EDITOR,
        from_agent="WriterAgent",
        to_agent="EditorAgent",
        situation=f"Draft complete for Chapter {state['chapter_number']}: {state['chapter_title']}. "
        f"{word_count:,} words across {sections} sections with {code_blocks} code examples.",
        background=f"Applied writing patterns: {', '.join(patterns[:3]) if patterns else 'standard'}. "
        f"Used research summary and outline as foundation. "
        f"Draft version: {state.get('current_version', 1)}.",
        assessment=f"Word count {'meets' if 0.8 <= word_count / target_count <= 1.2 else 'needs adjustment vs'} "
        f"target ({target_count}). Structure {'complete' if sections >= 5 else 'may be incomplete'}. "
        f"Code coverage {'adequate' if code_blocks >= 5 else 'may need enhancement'}.",
        recommendation="Polish for publication quality. "
        + ("Strengthen authoritative voice - remove hedging. " if hedging_count > 5 else "")
        + ("Add language identifiers to code blocks. " if unlabeled_code > 0 else "")
        + "Verify all required elements present.",
        key_metrics={
            "word_count": word_count,
            "target_word_count": target_count,
            "sections": sections,
            "code_blocks": code_blocks,
            "hedging_phrases": hedging_count,
            "unlabeled_code": unlabeled_code,
        },
        focus_areas=focus_areas,
        known_issues=known_issues,
        artifacts={
            "draft_excerpt": draft[:2000] + "..." if len(draft) > 2000 else draft,
        },
    )


def create_editor_to_reviewer_handoff(state: dict[str, Any]) -> SBARHandoff:
    """Create SBAR handoff from EditorAgent to ReviewerAgent."""
    draft = state.get("current_draft", "")
    edit_result = state.get("edit_result", {})
    issues_found = edit_result.get("issues_found", 0)
    issues_fixed = edit_result.get("issues_fixed", 0)
    remaining_issues = issues_found - issues_fixed

    focus_areas = []
    if remaining_issues > 0:
        focus_areas.append(f"{remaining_issues} issues could not be auto-fixed - verify acceptable")

    missing_elements = edit_result.get("missing_elements", [])
    if missing_elements:
        focus_areas.append(f"Missing required elements: {', '.join(missing_elements)}")

    return SBARHandoff(
        handoff_type=HandoffType.EDITOR_TO_REVIEWER,
        from_agent="EditorAgent",
        to_agent="ReviewerAgent",
        situation=f"Editing complete for Chapter {state['chapter_number']}: {state['chapter_title']}. "
        f"Fixed {issues_fixed} of {issues_found} identified issues.",
        background=f"Applied style rules (hedging removal, code labeling, formatting). "
        f"Verified required chapter elements. "
        f"Word count optimized to {len(draft.split()):,} words.",
        assessment=f"{'All' if remaining_issues == 0 else f'{issues_fixed}/{issues_found}'} "
        f"style issues resolved. "
        f"{'All required elements present.' if not missing_elements else f'Missing: {missing_elements}'}",
        recommendation="Review for publication approval. "
        f"{'Focus on content quality - style is clean.' if remaining_issues == 0 else 'Note unresolved style issues.'} "
        "Assess against quality dimensions.",
        key_metrics={
            "issues_found": issues_found,
            "issues_fixed": issues_fixed,
            "remaining_issues": remaining_issues,
            "word_count": len(draft.split()),
            "missing_elements": len(missing_elements),
        },
        focus_areas=focus_areas,
        known_issues=edit_result.get("unfixed_issues", []),
        artifacts={},
    )


def create_reviewer_to_writer_handoff(state: dict[str, Any]) -> SBARHandoff:
    """Create SBAR handoff from ReviewerAgent back to WriterAgent for revision."""
    scores = state.get("quality_scores", {})
    feedback = state.get("review_feedback", [])
    overall = (
        scores.get("overall", 0.0) if isinstance(scores, dict) else getattr(scores, "overall", 0.0)
    )

    # Identify weakest dimensions
    dimension_scores = {}
    if isinstance(scores, dict):
        dimension_scores = {k: v for k, v in scores.items() if k != "overall"}
    else:
        # QualityScore dataclass
        for dim in [
            "structure",
            "voice_consistency",
            "code_quality",
            "reader_engagement",
            "technical_accuracy",
        ]:
            dimension_scores[dim] = getattr(scores, dim, 0.0)

    # Sort by score to find weakest
    sorted_dims = sorted(dimension_scores.items(), key=lambda x: x[1])
    weakest = sorted_dims[:2] if len(sorted_dims) >= 2 else sorted_dims

    focus_areas = [f"Improve {dim}: {score:.0%}" for dim, score in weakest]

    return SBARHandoff(
        handoff_type=HandoffType.REVIEWER_TO_WRITER,
        from_agent="ReviewerAgent",
        to_agent="WriterAgent",
        situation=f"Revision needed for Chapter {state['chapter_number']}: {state['chapter_title']}. "
        f"Overall score: {overall:.0%} (threshold: 80%).",
        background=f"Reviewed against 5 quality dimensions. "
        f"Lowest scores: {', '.join(f'{d}: {s:.0%}' for d, s in weakest)}. "
        f"Provided {len(feedback)} feedback items.",
        assessment=f"Chapter needs improvement in {len(weakest)} dimensions to meet publication threshold. "
        f"Primary gaps: {weakest[0][0] if weakest else 'none identified'}.",
        recommendation="Revise draft focusing on feedback items. "
        f"Prioritize: {', '.join(f[0] for f in weakest)}. "
        "Maintain strengths while addressing gaps.",
        key_metrics={
            "overall_score": f"{overall:.0%}",
            "threshold": "80%",
            "feedback_count": len(feedback),
            **{f"{k}_score": f"{v:.0%}" for k, v in dimension_scores.items()},
        },
        focus_areas=focus_areas,
        known_issues=feedback[:5],  # Top 5 feedback items
        artifacts={
            "full_feedback": "\n".join(f"- {f}" for f in feedback),
        },
    )


# =============================================================================
# Quality Gap Detection
# =============================================================================


class GapSeverity(Enum):
    """Severity levels for quality gaps"""

    LOW = "low"  # Nice to fix, not blocking
    MEDIUM = "medium"  # Should fix before publication
    HIGH = "high"  # Must fix - blocks publication
    CRITICAL = "critical"  # Requires immediate attention


@dataclass
class QualityGap:
    """
    Structured quality gap with severity and remediation.

    Inspired by healthcare gap detection systems that track
    patient care gaps with severity and follow-up protocols.
    """

    # Gap identification
    gap_id: str
    dimension: str  # Which quality dimension
    category: str  # Specific category within dimension
    description: str

    # Severity and scoring
    severity: GapSeverity
    current_score: float
    target_score: float
    impact_on_overall: float  # How much this gap affects overall score

    # Remediation
    remediation_steps: list[str] = field(default_factory=list)
    estimated_effort_minutes: int = 0
    auto_fixable: bool = False

    # Tracking
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    detected_by: str = ""
    resolved: bool = False
    resolved_at: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "gap_id": self.gap_id,
            "dimension": self.dimension,
            "category": self.category,
            "description": self.description,
            "severity": self.severity.value,
            "current_score": self.current_score,
            "target_score": self.target_score,
            "impact_on_overall": self.impact_on_overall,
            "remediation_steps": self.remediation_steps,
            "estimated_effort_minutes": self.estimated_effort_minutes,
            "auto_fixable": self.auto_fixable,
            "detected_at": self.detected_at,
            "detected_by": self.detected_by,
            "resolved": self.resolved,
            "resolved_at": self.resolved_at,
        }


class QualityGapDetector:
    """
    Detects and categorizes quality gaps in chapter content.

    Uses structured analysis to identify specific issues,
    estimate remediation effort, and prioritize fixes.
    """

    # Dimension weights (same as ReviewerAgent)
    DIMENSION_WEIGHTS = {
        "structure": 0.15,
        "voice_consistency": 0.15,
        "code_quality": 0.25,
        "reader_engagement": 0.20,
        "technical_accuracy": 0.25,
    }

    # Severity thresholds
    THRESHOLDS = {
        "critical": 0.40,  # Below 40% = critical
        "high": 0.60,  # Below 60% = high
        "medium": 0.75,  # Below 75% = medium
        "low": 0.85,  # Below 85% = low (nice to have)
    }

    def detect_gaps(
        self,
        scores: dict[str, float],
        draft: str,
        chapter_title: str,
    ) -> list[QualityGap]:
        """
        Detect all quality gaps in a chapter.

        Args:
            scores: Quality scores by dimension
            draft: Chapter draft content
            chapter_title: Title for context

        Returns:
            List of QualityGap objects, sorted by severity
        """
        gaps = []
        gap_counter = 0

        for dimension, score in scores.items():
            if dimension == "overall":
                continue

            weight = self.DIMENSION_WEIGHTS.get(dimension, 0.15)
            target = 0.80  # Standard approval threshold

            if score < target:
                # Get dimension-specific gaps
                dimension_gaps = self._analyze_dimension(
                    dimension, score, target, weight, draft, gap_counter
                )
                gaps.extend(dimension_gaps)
                gap_counter += len(dimension_gaps)

        # Sort by severity (critical first) then by impact
        severity_order = {
            GapSeverity.CRITICAL: 0,
            GapSeverity.HIGH: 1,
            GapSeverity.MEDIUM: 2,
            GapSeverity.LOW: 3,
        }
        gaps.sort(key=lambda g: (severity_order[g.severity], -g.impact_on_overall))

        return gaps

    def _determine_severity(self, score: float) -> GapSeverity:
        """Determine gap severity based on score."""
        if score < self.THRESHOLDS["critical"]:
            return GapSeverity.CRITICAL
        elif score < self.THRESHOLDS["high"]:
            return GapSeverity.HIGH
        elif score < self.THRESHOLDS["medium"]:
            return GapSeverity.MEDIUM
        else:
            return GapSeverity.LOW

    def _analyze_dimension(
        self,
        dimension: str,
        score: float,
        target: float,
        weight: float,
        draft: str,
        start_id: int,
    ) -> list[QualityGap]:
        """Analyze a specific dimension for gaps."""
        gaps = []
        impact = (target - score) * weight  # Impact on overall score

        if dimension == "structure":
            gaps.extend(self._analyze_structure(draft, score, target, impact, start_id))
        elif dimension == "voice_consistency":
            gaps.extend(self._analyze_voice(draft, score, target, impact, start_id))
        elif dimension == "code_quality":
            gaps.extend(self._analyze_code(draft, score, target, impact, start_id))
        elif dimension == "reader_engagement":
            gaps.extend(self._analyze_engagement(draft, score, target, impact, start_id))
        elif dimension == "technical_accuracy":
            gaps.extend(self._analyze_accuracy(draft, score, target, impact, start_id))

        return gaps

    def _analyze_structure(
        self, draft: str, score: float, target: float, impact: float, start_id: int
    ) -> list[QualityGap]:
        """Analyze structure dimension for specific gaps."""
        gaps = []
        gap_id = start_id

        # Check for opening quote
        if not re.search(r'^>\s*"', draft, re.MULTILINE):
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="structure",
                    category="opening_quote",
                    description="Missing opening quote at chapter start",
                    severity=GapSeverity.MEDIUM,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.2,
                    remediation_steps=[
                        "Add a thematic quote at the beginning",
                        'Format as blockquote: > "Quote" - Attribution',
                    ],
                    estimated_effort_minutes=5,
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )
            gap_id += 1

        # Check for key takeaways
        if not re.search(r"##\s*Key Takeaways", draft, re.IGNORECASE):
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="structure",
                    category="key_takeaways",
                    description="Missing Key Takeaways section",
                    severity=GapSeverity.HIGH,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.3,
                    remediation_steps=[
                        "Add ## Key Takeaways section before exercise",
                        "Include 5-6 actionable bullet points",
                        "Start each with a verb: Use, Remember, Implement",
                    ],
                    estimated_effort_minutes=15,
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )
            gap_id += 1

        # Check for exercise
        if not re.search(r"##\s*Try It Yourself", draft, re.IGNORECASE):
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="structure",
                    category="exercise",
                    description="Missing Try It Yourself exercise",
                    severity=GapSeverity.HIGH,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.3,
                    remediation_steps=[
                        "Add ## Try It Yourself section at end",
                        "Include 3-5 concrete steps",
                        "State expected outcome clearly",
                    ],
                    estimated_effort_minutes=20,
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )
            gap_id += 1

        # Check section count
        section_count = draft.count("## ")
        if section_count < 5:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="structure",
                    category="section_count",
                    description=f"Only {section_count} sections (minimum 5 recommended)",
                    severity=GapSeverity.MEDIUM,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.2,
                    remediation_steps=[
                        f"Add {5 - section_count} more substantive sections",
                        "Each section: concept + code + real-world application",
                    ],
                    estimated_effort_minutes=30 * (5 - section_count),
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )

        return gaps

    def _analyze_voice(
        self, draft: str, score: float, target: float, impact: float, start_id: int
    ) -> list[QualityGap]:
        """Analyze voice consistency for specific gaps."""
        gaps = []
        gap_id = start_id

        # Check for hedging
        hedging_patterns = [r"\bmight\b", r"\bperhaps\b", r"\bpossibly\b", r"\bcould be\b"]
        hedging_count = sum(len(re.findall(p, draft, re.IGNORECASE)) for p in hedging_patterns)

        if hedging_count > 5:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="voice_consistency",
                    category="hedging",
                    description=f"Found {hedging_count} hedging phrases (should be confident/authoritative)",
                    severity=GapSeverity.MEDIUM if hedging_count < 15 else GapSeverity.HIGH,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.5,
                    remediation_steps=[
                        "Replace 'might' with 'will' or 'does'",
                        "Replace 'perhaps' with definitive statements",
                        "State facts confidently without qualification",
                    ],
                    estimated_effort_minutes=hedging_count * 2,
                    auto_fixable=True,
                    detected_by="QualityGapDetector",
                )
            )

        return gaps

    def _analyze_code(
        self, draft: str, score: float, target: float, impact: float, start_id: int
    ) -> list[QualityGap]:
        """Analyze code quality for specific gaps."""
        gaps = []
        gap_id = start_id

        # Count code blocks
        code_blocks = re.findall(r"```(\w*)\n(.*?)```", draft, re.DOTALL)
        code_count = len(code_blocks)

        if code_count < 5:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="code_quality",
                    category="code_count",
                    description=f"Only {code_count} code examples (minimum 5 recommended)",
                    severity=GapSeverity.HIGH,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.4,
                    remediation_steps=[
                        f"Add {5 - code_count} more code examples",
                        "Each concept should have accompanying code",
                        "Include complete, runnable examples",
                    ],
                    estimated_effort_minutes=15 * (5 - code_count),
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )
            gap_id += 1

        # Check for unlabeled code blocks
        unlabeled = sum(1 for lang, _ in code_blocks if not lang)
        if unlabeled > 0:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="code_quality",
                    category="unlabeled_code",
                    description=f"{unlabeled} code blocks missing language identifier",
                    severity=GapSeverity.MEDIUM,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.2,
                    remediation_steps=[
                        "Add language identifier after opening ```",
                        "Common: python, javascript, typescript, bash",
                    ],
                    estimated_effort_minutes=unlabeled * 2,
                    auto_fixable=True,
                    detected_by="QualityGapDetector",
                )
            )
            gap_id += 1

        # Check Python syntax
        python_blocks = [(code, lang) for lang, code in code_blocks if lang == "python"]
        syntax_errors = 0
        for code, _ in python_blocks:
            try:
                compile(code, "<string>", "exec")
            except SyntaxError:
                syntax_errors += 1

        if syntax_errors > 0:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="code_quality",
                    category="syntax_errors",
                    description=f"{syntax_errors} Python code blocks have syntax errors",
                    severity=GapSeverity.CRITICAL,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.4,
                    remediation_steps=[
                        "Review each Python code block for syntax",
                        "Ensure proper indentation",
                        "Check for missing colons, parentheses, quotes",
                    ],
                    estimated_effort_minutes=syntax_errors * 10,
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )

        return gaps

    def _analyze_engagement(
        self, draft: str, score: float, target: float, impact: float, start_id: int
    ) -> list[QualityGap]:
        """Analyze reader engagement for specific gaps."""
        gaps = []
        gap_id = start_id

        # Check for real-world examples
        real_world_patterns = [
            r"real[- ]world",
            r"in practice",
            r"for example",
            r"production",
            r"use case",
        ]
        real_world_count = sum(
            len(re.findall(p, draft, re.IGNORECASE)) for p in real_world_patterns
        )

        if real_world_count < 3:
            gaps.append(
                QualityGap(
                    gap_id=f"gap_{gap_id}",
                    dimension="reader_engagement",
                    category="real_world_examples",
                    description="Insufficient real-world context and examples",
                    severity=GapSeverity.MEDIUM,
                    current_score=score,
                    target_score=target,
                    impact_on_overall=impact * 0.4,
                    remediation_steps=[
                        "Add 'In practice...' explanations after concepts",
                        "Include real-world use cases",
                        "Show production-ready patterns",
                    ],
                    estimated_effort_minutes=20,
                    auto_fixable=False,
                    detected_by="QualityGapDetector",
                )
            )

        return gaps

    def _analyze_accuracy(
        self, draft: str, score: float, target: float, impact: float, start_id: int
    ) -> list[QualityGap]:
        """Analyze technical accuracy for specific gaps."""
        # Technical accuracy is harder to detect automatically
        # This is a placeholder for LLM-based accuracy checking
        return []

    def summarize_gaps(self, gaps: list[QualityGap]) -> dict[str, Any]:
        """Create a summary of detected gaps."""
        if not gaps:
            return {
                "total_gaps": 0,
                "by_severity": {},
                "by_dimension": {},
                "total_effort_minutes": 0,
                "auto_fixable_count": 0,
                "blocking_count": 0,
            }

        return {
            "total_gaps": len(gaps),
            "by_severity": {
                "critical": sum(1 for g in gaps if g.severity == GapSeverity.CRITICAL),
                "high": sum(1 for g in gaps if g.severity == GapSeverity.HIGH),
                "medium": sum(1 for g in gaps if g.severity == GapSeverity.MEDIUM),
                "low": sum(1 for g in gaps if g.severity == GapSeverity.LOW),
            },
            "by_dimension": {
                dim: sum(1 for g in gaps if g.dimension == dim)
                for dim in {g.dimension for g in gaps}
            },
            "total_effort_minutes": sum(g.estimated_effort_minutes for g in gaps),
            "auto_fixable_count": sum(1 for g in gaps if g.auto_fixable),
            "blocking_count": sum(
                1 for g in gaps if g.severity in (GapSeverity.CRITICAL, GapSeverity.HIGH)
            ),
        }


# =============================================================================
# Pattern Extraction
# =============================================================================


@dataclass
class ExtractedPattern:
    """A pattern extracted from a successful chapter."""

    pattern_id: str
    pattern_type: Literal[
        "structure",
        "voice",
        "code",
        "engagement",
        "transition",
        "example",
    ]
    description: str
    content: str  # The actual pattern content/template
    source_chapter: int
    source_title: str
    quality_score: float  # Score when this pattern was used
    extraction_date: str = field(default_factory=lambda: datetime.now().isoformat())
    usage_count: int = 0
    effectiveness_score: float = 0.0  # Updated based on outcomes

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for MemDocs storage."""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type,
            "description": self.description,
            "content": self.content,
            "source_chapter": self.source_chapter,
            "source_title": self.source_title,
            "quality_score": self.quality_score,
            "extraction_date": self.extraction_date,
            "usage_count": self.usage_count,
            "effectiveness_score": self.effectiveness_score,
        }


class PatternExtractor:
    """
    Extracts successful patterns from approved chapters.

    These patterns are stored in MemDocs and used to guide
    future chapter production.
    """

    def __init__(self):
        self.logger = logging.getLogger("learning.pattern_extractor")

    def extract_patterns(
        self,
        draft: str,
        chapter_number: int,
        chapter_title: str,
        quality_scores: dict[str, float],
    ) -> list[ExtractedPattern]:
        """
        Extract patterns from a high-quality chapter.

        Only called for chapters scoring >= 0.85 overall.

        Args:
            draft: The chapter content
            chapter_number: Chapter number
            chapter_title: Chapter title
            quality_scores: Quality scores by dimension

        Returns:
            List of extracted patterns
        """
        patterns = []
        overall = quality_scores.get("overall", 0.0)

        # Only extract from high-quality chapters
        if overall < 0.85:
            self.logger.info(f"Skipping pattern extraction - score {overall:.2f} below threshold")
            return patterns

        self.logger.info(f"Extracting patterns from Chapter {chapter_number}: {chapter_title}")

        # Extract structure patterns
        if quality_scores.get("structure", 0) >= 0.85:
            patterns.extend(
                self._extract_structure_patterns(draft, chapter_number, chapter_title, overall)
            )

        # Extract voice patterns
        if quality_scores.get("voice_consistency", 0) >= 0.85:
            patterns.extend(
                self._extract_voice_patterns(draft, chapter_number, chapter_title, overall)
            )

        # Extract code patterns
        if quality_scores.get("code_quality", 0) >= 0.85:
            patterns.extend(
                self._extract_code_patterns(draft, chapter_number, chapter_title, overall)
            )

        # Extract engagement patterns
        if quality_scores.get("reader_engagement", 0) >= 0.85:
            patterns.extend(
                self._extract_engagement_patterns(draft, chapter_number, chapter_title, overall)
            )

        self.logger.info(f"Extracted {len(patterns)} patterns from Chapter {chapter_number}")
        return patterns

    def _extract_structure_patterns(
        self, draft: str, chapter_number: int, chapter_title: str, score: float
    ) -> list[ExtractedPattern]:
        """Extract successful structure patterns."""
        patterns = []

        # Extract opening quote pattern
        quote_match = re.search(r'^(>\s*"[^"]+"\s*[-–—]\s*.+?)$', draft, re.MULTILINE)
        if quote_match:
            patterns.append(
                ExtractedPattern(
                    pattern_id=f"struct_quote_{chapter_number}",
                    pattern_type="structure",
                    description="Effective opening quote format",
                    content=quote_match.group(1),
                    source_chapter=chapter_number,
                    source_title=chapter_title,
                    quality_score=score,
                )
            )

        # Extract key takeaways pattern
        takeaways_match = re.search(
            r"(##\s*Key Takeaways.*?)(?=##|\Z)",
            draft,
            re.DOTALL | re.IGNORECASE,
        )
        if takeaways_match:
            takeaways = takeaways_match.group(1).strip()
            if len(takeaways) > 100:  # Substantial takeaways
                patterns.append(
                    ExtractedPattern(
                        pattern_id=f"struct_takeaways_{chapter_number}",
                        pattern_type="structure",
                        description="Effective key takeaways section",
                        content=takeaways[:1000],  # Limit size
                        source_chapter=chapter_number,
                        source_title=chapter_title,
                        quality_score=score,
                    )
                )

        # Extract exercise pattern
        exercise_match = re.search(
            r"(##\s*Try It Yourself.*?)(?=##|\Z)",
            draft,
            re.DOTALL | re.IGNORECASE,
        )
        if exercise_match:
            exercise = exercise_match.group(1).strip()
            if len(exercise) > 100:
                patterns.append(
                    ExtractedPattern(
                        pattern_id=f"struct_exercise_{chapter_number}",
                        pattern_type="structure",
                        description="Effective hands-on exercise format",
                        content=exercise[:1000],
                        source_chapter=chapter_number,
                        source_title=chapter_title,
                        quality_score=score,
                    )
                )

        return patterns

    def _extract_voice_patterns(
        self, draft: str, chapter_number: int, chapter_title: str, score: float
    ) -> list[ExtractedPattern]:
        """Extract successful voice/tone patterns."""
        patterns = []

        # Extract authoritative statement patterns
        # Look for sentences that state facts without hedging
        authoritative_sentences = []
        sentences = re.split(r"[.!?]\s+", draft)
        for sentence in sentences:
            if len(sentence) > 50 and len(sentence) < 200:
                # No hedging words
                hedging = ["might", "perhaps", "possibly", "could be", "maybe"]
                if not any(h in sentence.lower() for h in hedging):
                    # Has technical content
                    if any(
                        term in sentence.lower()
                        for term in ["memdocs", "pattern", "agent", "memory", "redis"]
                    ):
                        authoritative_sentences.append(sentence)

        if authoritative_sentences:
            patterns.append(
                ExtractedPattern(
                    pattern_id=f"voice_authoritative_{chapter_number}",
                    pattern_type="voice",
                    description="Authoritative technical statements",
                    content="\n".join(authoritative_sentences[:5]),
                    source_chapter=chapter_number,
                    source_title=chapter_title,
                    quality_score=score,
                )
            )

        return patterns

    def _extract_code_patterns(
        self, draft: str, chapter_number: int, chapter_title: str, score: float
    ) -> list[ExtractedPattern]:
        """Extract successful code example patterns."""
        patterns = []

        # Find well-commented code blocks
        code_blocks = re.findall(r"```(\w+)\n(.*?)```", draft, re.DOTALL)

        for lang, code in code_blocks:
            if lang == "python":
                # Check for good commenting
                lines = code.strip().split("\n")
                comment_lines = sum(1 for line in lines if line.strip().startswith("#"))
                code_lines = len(lines)

                # Good ratio: 1 comment per 3-5 lines of code
                if code_lines >= 5 and 0.15 <= comment_lines / code_lines <= 0.4:
                    patterns.append(
                        ExtractedPattern(
                            pattern_id=f"code_commented_{chapter_number}_{len(patterns)}",
                            pattern_type="code",
                            description="Well-commented Python code example",
                            content=f"```{lang}\n{code}```",
                            source_chapter=chapter_number,
                            source_title=chapter_title,
                            quality_score=score,
                        )
                    )

        return patterns[:3]  # Limit to top 3 code patterns

    def _extract_engagement_patterns(
        self, draft: str, chapter_number: int, chapter_title: str, score: float
    ) -> list[ExtractedPattern]:
        """Extract successful engagement patterns."""
        patterns = []

        # Extract "In practice" examples
        practice_examples = re.findall(
            r"(In practice[,:]?\s+[^.]+\.)",
            draft,
            re.IGNORECASE,
        )
        if practice_examples:
            patterns.append(
                ExtractedPattern(
                    pattern_id=f"engage_practice_{chapter_number}",
                    pattern_type="engagement",
                    description="Effective 'In practice' examples",
                    content="\n".join(practice_examples[:3]),
                    source_chapter=chapter_number,
                    source_title=chapter_title,
                    quality_score=score,
                )
            )

        # Extract real-world context
        real_world = re.findall(
            r"((?:real[- ]world|production|enterprise)[^.]+\.)",
            draft,
            re.IGNORECASE,
        )
        if real_world:
            patterns.append(
                ExtractedPattern(
                    pattern_id=f"engage_realworld_{chapter_number}",
                    pattern_type="engagement",
                    description="Real-world context examples",
                    content="\n".join(real_world[:3]),
                    source_chapter=chapter_number,
                    source_title=chapter_title,
                    quality_score=score,
                )
            )

        return patterns


# =============================================================================
# Feedback Loop
# =============================================================================


@dataclass
class FeedbackEntry:
    """A single feedback entry for pattern improvement."""

    feedback_id: str
    pattern_id: str | None  # Which pattern this relates to
    feedback_type: Literal["positive", "negative", "suggestion"]
    source: Literal["reviewer", "editor", "human", "metric"]
    content: str
    context: dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    processed: bool = False


class FeedbackLoop:
    """
    Manages the feedback loop for continuous pattern improvement.

    Collects feedback from:
    - ReviewerAgent quality assessments
    - EditorAgent issue detection
    - Human review (when available)
    - Production metrics

    Updates pattern effectiveness scores and identifies
    patterns that should be deprecated or improved.
    """

    def __init__(self):
        self.logger = logging.getLogger("learning.feedback_loop")
        self.pending_feedback: list[FeedbackEntry] = []
        self.pattern_scores: dict[str, float] = {}  # pattern_id -> effectiveness

    def record_review_feedback(
        self,
        chapter_number: int,
        chapter_title: str,
        quality_scores: dict[str, float],
        patterns_used: list[str],
        approved: bool,
    ) -> list[FeedbackEntry]:
        """
        Record feedback from a review cycle.

        Args:
            chapter_number: Chapter that was reviewed
            chapter_title: Chapter title
            quality_scores: Quality scores from reviewer
            patterns_used: Pattern IDs that were used
            approved: Whether chapter was approved

        Returns:
            List of feedback entries created
        """
        entries = []
        overall = quality_scores.get("overall", 0.0)

        for pattern_id in patterns_used:
            # Create feedback based on outcome
            if approved and overall >= 0.85:
                entries.append(
                    FeedbackEntry(
                        feedback_id=f"fb_{chapter_number}_{pattern_id}_pos",
                        pattern_id=pattern_id,
                        feedback_type="positive",
                        source="reviewer",
                        content=f"Pattern contributed to high-quality chapter (score: {overall:.2f})",
                        context={
                            "chapter_number": chapter_number,
                            "chapter_title": chapter_title,
                            "quality_scores": quality_scores,
                            "approved": approved,
                        },
                    )
                )
            elif not approved:
                # Determine which dimension failed
                failed_dims = [
                    dim
                    for dim, score in quality_scores.items()
                    if dim != "overall" and score < 0.80
                ]
                entries.append(
                    FeedbackEntry(
                        feedback_id=f"fb_{chapter_number}_{pattern_id}_neg",
                        pattern_id=pattern_id,
                        feedback_type="negative",
                        source="reviewer",
                        content=f"Pattern used in rejected chapter. Failed dimensions: {failed_dims}",
                        context={
                            "chapter_number": chapter_number,
                            "chapter_title": chapter_title,
                            "quality_scores": quality_scores,
                            "failed_dimensions": failed_dims,
                        },
                    )
                )

        self.pending_feedback.extend(entries)
        self.logger.info(f"Recorded {len(entries)} feedback entries for Chapter {chapter_number}")

        return entries

    def record_gap_feedback(
        self,
        chapter_number: int,
        gaps: list[QualityGap],
        patterns_used: list[str],
    ) -> list[FeedbackEntry]:
        """
        Record feedback from quality gap detection.

        If gaps are found, patterns used should be updated
        to prevent similar issues.
        """
        entries = []

        for gap in gaps:
            if gap.severity in (GapSeverity.CRITICAL, GapSeverity.HIGH):
                # Significant gap - create suggestion feedback
                for pattern_id in patterns_used:
                    if gap.dimension in pattern_id:  # Related pattern
                        entries.append(
                            FeedbackEntry(
                                feedback_id=f"fb_{chapter_number}_{gap.gap_id}",
                                pattern_id=pattern_id,
                                feedback_type="suggestion",
                                source="metric",
                                content=f"Pattern may need improvement: {gap.description}",
                                context={
                                    "gap": gap.to_dict(),
                                    "chapter_number": chapter_number,
                                },
                            )
                        )

        self.pending_feedback.extend(entries)
        return entries

    def update_pattern_scores(self) -> dict[str, float]:
        """
        Process pending feedback to update pattern effectiveness scores.

        Returns:
            Updated pattern scores
        """
        for entry in self.pending_feedback:
            if entry.processed or not entry.pattern_id:
                continue

            current_score = self.pattern_scores.get(entry.pattern_id, 0.5)

            # Adjust score based on feedback type
            if entry.feedback_type == "positive":
                # Increase score, but diminishing returns
                adjustment = 0.1 * (1 - current_score)
                new_score = min(1.0, current_score + adjustment)
            elif entry.feedback_type == "negative":
                # Decrease score
                adjustment = 0.15
                new_score = max(0.0, current_score - adjustment)
            else:  # suggestion
                # Small decrease
                adjustment = 0.05
                new_score = max(0.0, current_score - adjustment)

            self.pattern_scores[entry.pattern_id] = new_score
            entry.processed = True

            self.logger.debug(f"Pattern {entry.pattern_id}: {current_score:.2f} -> {new_score:.2f}")

        return self.pattern_scores

    def get_deprecated_patterns(self, threshold: float = 0.3) -> list[str]:
        """Get patterns that should be deprecated due to low effectiveness."""
        return [
            pattern_id for pattern_id, score in self.pattern_scores.items() if score < threshold
        ]

    def get_high_performing_patterns(self, threshold: float = 0.8) -> list[str]:
        """Get patterns that are highly effective."""
        return [
            pattern_id for pattern_id, score in self.pattern_scores.items() if score >= threshold
        ]

    def get_feedback_summary(self) -> dict[str, Any]:
        """Get summary of feedback collected."""
        return {
            "total_entries": len(self.pending_feedback),
            "pending": sum(1 for e in self.pending_feedback if not e.processed),
            "by_type": {
                "positive": sum(1 for e in self.pending_feedback if e.feedback_type == "positive"),
                "negative": sum(1 for e in self.pending_feedback if e.feedback_type == "negative"),
                "suggestion": sum(
                    1 for e in self.pending_feedback if e.feedback_type == "suggestion"
                ),
            },
            "patterns_tracked": len(self.pattern_scores),
            "high_performing": len(self.get_high_performing_patterns()),
            "deprecated": len(self.get_deprecated_patterns()),
        }
