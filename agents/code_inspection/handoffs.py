"""SBAR Handoffs for Code Inspection Pipeline

Structured handoffs between pipeline phases using healthcare-inspired
SBAR (Situation, Background, Assessment, Recommendation) format.

Following the pattern from agents/book_production/learning.py.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class HandoffType(Enum):
    """Types of handoffs in the inspection pipeline."""

    STATIC_TO_DYNAMIC = "static_to_dynamic"
    DYNAMIC_TO_CROSS = "dynamic_to_cross"
    CROSS_TO_LEARNING = "cross_to_learning"
    LEARNING_TO_REPORTING = "learning_to_reporting"
    SKIP_DYNAMIC = "skip_dynamic"


@dataclass
class SBARHandoff:
    """Structured handoff between pipeline phases.

    Based on healthcare SBAR format:
    - Situation: Current state of inspection
    - Background: What was done, decisions made
    - Assessment: Quality metrics, concerns
    - Recommendation: Specific guidance for next phase
    """

    handoff_type: HandoffType
    from_phase: str
    to_phase: str

    # SBAR Fields
    situation: str
    background: str
    assessment: str
    recommendation: str

    # Metrics
    key_metrics: dict[str, Any] = field(default_factory=dict)
    focus_areas: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)

    # Metadata
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


def create_static_to_dynamic_handoff(
    state: dict[str, Any],
) -> SBARHandoff:
    """Create handoff from Phase 1 (Static Analysis) to Phase 2 (Dynamic Analysis).

    Communicates static analysis findings to inform dynamic analysis focus.
    """
    # Situation
    findings_count = state.get("static_findings_count", 0)
    critical_count = state.get("static_critical_count", 0)
    situation = (
        f"Static analysis complete. Found {findings_count} findings ({critical_count} critical)."
    )

    # Background
    tools_run = list(state.get("static_analysis_results", {}).keys())
    scores = {
        name: result.get("score", 0)
        for name, result in state.get("static_analysis_results", {}).items()
    }
    background = f"Ran {len(tools_run)} tools: {', '.join(tools_run)}. Scores: {scores}."

    # Assessment
    security_score = state.get("security_scan_result", {}).get("score", 100)
    health_score = state.get("code_health_result", {}).get("score", 100)
    assessment = f"Security score: {security_score}/100. Code health score: {health_score}/100. "
    if critical_count > 0:
        assessment += "CRITICAL ISSUES REQUIRE IMMEDIATE ATTENTION."

    # Recommendation
    if critical_count > 0:
        recommendation = (
            "Focus dynamic analysis on files with critical findings. "
            "Consider skipping dynamic analysis until critical issues resolved."
        )
    elif security_score < 70:
        recommendation = (
            "Prioritize security-informed code review. Focus on files flagged by security scanner."
        )
    else:
        recommendation = (
            "Proceed with standard dynamic analysis. No special focus areas identified."
        )

    # Focus areas from security findings
    security_findings = state.get("security_scan_result", {}).get("findings", [])
    focus_files = list({f.get("file_path") for f in security_findings[:5]})

    return SBARHandoff(
        handoff_type=HandoffType.STATIC_TO_DYNAMIC,
        from_phase="static_analysis",
        to_phase="dynamic_analysis",
        situation=situation,
        background=background,
        assessment=assessment,
        recommendation=recommendation,
        key_metrics={
            "total_findings": findings_count,
            "critical_count": critical_count,
            "security_score": security_score,
            "health_score": health_score,
        },
        focus_areas=focus_files,
        known_issues=[
            f["message"][:100]
            for f in security_findings
            if f.get("severity") in ("critical", "high")
        ][:5],
    )


def create_dynamic_to_cross_handoff(
    state: dict[str, Any],
) -> SBARHandoff:
    """Create handoff from Phase 2 (Dynamic Analysis) to Phase 3 (Cross-Analysis).

    Communicates dynamic findings for cross-tool correlation.
    """
    dynamic_results = state.get("dynamic_analysis_results", {})
    historical_matches = state.get("historical_patterns_matched", [])

    # Situation
    if state.get("dynamic_analysis_skipped"):
        situation = f"Dynamic analysis skipped: {state.get('skip_reason', 'unknown')}"
    else:
        findings = sum(r.get("findings_count", 0) for r in dynamic_results.values())
        situation = f"Dynamic analysis complete. Found {findings} additional findings."

    # Background
    tools_run = list(dynamic_results.keys())
    background = (
        f"Ran tools: {', '.join(tools_run) or 'none'}. "
        f"Matched {len(historical_matches)} historical patterns."
    )

    # Assessment
    review_score = state.get("code_review_result", {}).get("score", 100)
    assessment = f"Code review score: {review_score}/100. "
    if historical_matches:
        assessment += f"{len(historical_matches)} files match historical bug patterns."

    # Recommendation
    if historical_matches:
        recommendation = (
            "Correlate historical matches with test quality findings. "
            "Generate test recommendations for matched patterns."
        )
    else:
        recommendation = (
            "Proceed with standard cross-analysis. Focus on security-review correlation."
        )

    return SBARHandoff(
        handoff_type=HandoffType.DYNAMIC_TO_CROSS,
        from_phase="dynamic_analysis",
        to_phase="cross_analysis",
        situation=situation,
        background=background,
        assessment=assessment,
        recommendation=recommendation,
        key_metrics={
            "tools_run": len(tools_run),
            "historical_matches": len(historical_matches),
            "review_score": review_score,
            "skipped": state.get("dynamic_analysis_skipped", False),
        },
        focus_areas=[m.get("file_path", "") for m in historical_matches[:5]],
        known_issues=[
            f"Historical: {m.get('error_type', 'unknown')}" for m in historical_matches[:5]
        ],
    )


def create_cross_to_learning_handoff(
    state: dict[str, Any],
) -> SBARHandoff:
    """Create handoff from Phase 3 (Cross-Analysis) to Phase 4 (Learning).

    Communicates insights for pattern extraction.
    """
    insights = state.get("cross_tool_insights", [])

    # Situation
    situation = f"Cross-analysis complete. Generated {len(insights)} insights."

    # Background
    insight_types = list({i.get("insight_type", "") for i in insights})
    background = f"Insight types: {', '.join(insight_types) or 'none'}."

    # Assessment
    high_confidence = [i for i in insights if i.get("confidence", 0) >= 0.7]
    assessment = f"{len(high_confidence)} high-confidence insights suitable for learning."

    # Recommendation
    if high_confidence:
        recommendation = (
            "Extract patterns from high-confidence insights. "
            "Store security-review correlations for future use."
        )
    else:
        recommendation = (
            "Skip pattern extraction due to low confidence. Proceed directly to reporting."
        )

    return SBARHandoff(
        handoff_type=HandoffType.CROSS_TO_LEARNING,
        from_phase="cross_analysis",
        to_phase="learning",
        situation=situation,
        background=background,
        assessment=assessment,
        recommendation=recommendation,
        key_metrics={
            "total_insights": len(insights),
            "high_confidence": len(high_confidence),
            "insight_types": insight_types,
        },
        focus_areas=[],
        known_issues=[],
    )


def format_handoff_for_log(handoff: SBARHandoff) -> str:
    """Format handoff for logging/audit trail."""
    return (
        f"\n{'=' * 60}\n"
        f"HANDOFF: {handoff.from_phase} → {handoff.to_phase}\n"
        f"{'=' * 60}\n"
        f"SITUATION: {handoff.situation}\n"
        f"BACKGROUND: {handoff.background}\n"
        f"ASSESSMENT: {handoff.assessment}\n"
        f"RECOMMENDATION: {handoff.recommendation}\n"
        f"{'=' * 60}\n"
    )
