"""
Cross-Analysis Node - Phase 3

Correlates findings between different tools to generate insights.

Intelligence generated:
- Security findings inform code review focus areas
- Bug patterns inform test recommendations
- Tech debt trajectory affects priority

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from ..state import (
    CodeInspectionState,
    CrossToolInsight,
    InspectionPhase,
    add_audit_entry,
)

logger = logging.getLogger(__name__)


async def run_cross_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """
    Phase 3: Correlate findings between tools.

    Generates cross-tool insights that provide intelligence beyond
    what individual tools can provide.

    Args:
        state: Current inspection state

    Returns:
        Updated state with cross-tool insights
    """
    logger.info("[Phase 3] Starting cross-analysis")

    state["current_phase"] = InspectionPhase.CROSS_ANALYSIS.value
    add_audit_entry(state, "cross_analysis", "Starting Phase 3: Cross-Analysis")

    insights: list[CrossToolInsight] = []

    # 1. Security findings inform code review
    security_informed = await _security_informs_review(state)
    insights.extend(security_informed)
    state["security_informed_review"] = [dict(i) for i in security_informed]

    # 2. Bug patterns inform test recommendations
    bug_informed = await _bugs_inform_tests(state)
    insights.extend(bug_informed)
    state["bug_informed_tests"] = [dict(i) for i in bug_informed]

    # 3. Tech debt trajectory affects priority
    debt_impact = await _apply_debt_trajectory_priority(state)
    state["debt_trajectory_impact"] = debt_impact

    # Store all insights
    state["cross_tool_insights"] = [dict(i) for i in insights]
    state["completed_phases"].append(InspectionPhase.CROSS_ANALYSIS.value)
    state["last_updated"] = datetime.now().isoformat()

    add_audit_entry(
        state,
        "cross_analysis",
        "Phase 3 complete",
        {
            "insights_generated": len(insights),
            "security_informed_count": len(security_informed),
            "bug_informed_count": len(bug_informed),
        },
    )

    logger.info(f"[Phase 3] Complete: {len(insights)} cross-tool insights generated")

    return state


async def _security_informs_review(
    state: CodeInspectionState,
) -> list[CrossToolInsight]:
    """
    Generate insights where security findings inform code review.

    Links security vulnerabilities to related code review findings
    to prioritize review of vulnerable areas.
    """
    insights: list[CrossToolInsight] = []

    security_result = state.get("security_scan_result")
    code_review_result = state.get("code_review_result")

    if not security_result or security_result.get("status") == "skip":
        return insights

    security_findings = security_result.get("findings", [])
    if not security_findings:
        return insights

    # Group security findings by file
    by_file: dict[str, list[dict]] = defaultdict(list)
    for finding in security_findings:
        by_file[finding.get("file_path", "")].append(finding)

    # Create insights for files with security issues
    for file_path, findings in by_file.items():
        vuln_types = list({f.get("code", "UNKNOWN") for f in findings})
        severities = [f.get("severity", "medium") for f in findings]
        has_critical = "critical" in severities
        has_high = "high" in severities

        recommendations = [
            f"Prioritize security review of {file_path}",
            f"Check for {', '.join(vuln_types[:3])} patterns",
        ]

        if has_critical:
            recommendations.append("CRITICAL: Address security issues before other code changes")
        elif has_high:
            recommendations.append("HIGH: Security review should precede feature work")

        insight = CrossToolInsight(
            insight_id=f"sec_rev_{len(insights)}",
            insight_type="security_informs_review",
            source_tools=["security", "code_review"],
            description=f"Security issues in {file_path} correlate with code review focus areas",
            affected_files=[file_path],
            recommendations=recommendations,
            confidence=0.85 if has_critical or has_high else 0.7,
        )
        insights.append(insight)

        # Also check for related code review findings
        if code_review_result:
            review_findings = code_review_result.get("findings", [])
            related = [r for r in review_findings if r.get("file_path") == file_path]
            if related:
                insight["description"] += f" ({len(related)} related review findings)"
                insight["confidence"] = min(1.0, insight["confidence"] + 0.1)

    return insights


async def _bugs_inform_tests(state: CodeInspectionState) -> list[CrossToolInsight]:
    """
    Generate insights where historical bugs inform test recommendations.

    Uses patterns from memory-enhanced debugging to suggest tests
    that could catch similar bugs.
    """
    insights: list[CrossToolInsight] = []

    memory_result = state.get("memory_debugging_result")
    # test_quality_result could be used to check coverage of affected files

    if not memory_result or memory_result.get("status") == "skip":
        return insights

    historical_matches = state.get("historical_patterns_matched", [])
    if not historical_matches:
        return insights

    # Group matches by error type
    by_error_type: dict[str, list[dict]] = defaultdict(list)
    for match in historical_matches:
        error_type = match.get("error_type", "unknown")
        by_error_type[error_type].append(match)

    # Create insights for each error type
    for error_type, matches in by_error_type.items():
        affected_files = list({m.get("file_path", "") for m in matches})
        avg_similarity = sum(m.get("similarity_score", 0) for m in matches) / len(matches)

        recommendations = [
            f"Add tests for {error_type} scenarios in affected files",
            "Consider edge cases that triggered historical bugs",
        ]

        # Get historical fix info
        if matches and matches[0].get("historical_fix"):
            recommendations.append(f"Previous fix pattern: {matches[0]['historical_fix'][:100]}...")

        insight = CrossToolInsight(
            insight_id=f"bug_test_{len(insights)}",
            insight_type="bugs_inform_tests",
            source_tools=["memory_debugging", "test_quality"],
            description=f"Historical {error_type} bugs suggest testing gaps",
            affected_files=affected_files[:5],  # Limit to 5 files
            recommendations=recommendations,
            confidence=avg_similarity,
        )
        insights.append(insight)

    return insights


async def _apply_debt_trajectory_priority(
    state: CodeInspectionState,
) -> dict[str, Any]:
    """
    Adjust finding priorities based on tech debt trajectory.

    If debt is increasing, boost priority of debt-related findings.
    If in hotspot files, boost priority further.
    """
    debt_result = state.get("tech_debt_result")

    if not debt_result or debt_result.get("status") == "skip":
        return {"trajectory": "unknown", "applied": False}

    trajectory = debt_result.get("metadata", {}).get("trajectory", {})
    hotspots = debt_result.get("metadata", {}).get("hotspots", [])

    trend = trajectory.get("trend", "stable")
    change_percent = trajectory.get("change_percent", 0)

    # Collect all findings from all tools
    all_findings = []
    for result_key in ["static_analysis_results", "dynamic_analysis_results"]:
        for result in state.get(result_key, {}).values():
            if result and result.get("findings"):
                all_findings.extend(result["findings"])

    # Apply priority boosts
    boosted_count = 0
    for finding in all_findings:
        original_priority = finding.get("priority_score", 50)
        new_priority = original_priority

        # Boost based on trajectory
        if trend == "exploding":
            new_priority = int(new_priority * 1.5)
        elif trend == "increasing":
            new_priority = int(new_priority * 1.2)
        elif trend == "decreasing":
            new_priority = int(new_priority * 0.9)

        # Boost if in hotspot file
        if finding.get("file_path") in hotspots:
            new_priority = int(new_priority * 1.3)
            finding["priority_boost"] = True
            finding["boost_reason"] = f"Hotspot file, debt trajectory: {trend}"

        finding["priority_score"] = min(100, new_priority)

        if new_priority != original_priority:
            boosted_count += 1

    logger.info(
        f"Applied debt trajectory priority: trend={trend}, boosted={boosted_count} findings"
    )

    return {
        "trajectory": trend,
        "change_percent": change_percent,
        "hotspots": hotspots,
        "findings_boosted": boosted_count,
        "applied": True,
    }
