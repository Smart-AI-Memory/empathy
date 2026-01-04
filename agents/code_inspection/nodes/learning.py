"""Learning Node - Phase 4

Extracts patterns from inspection results for future use.
Stores patterns in patterns/inspection/ directory.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from ..state import CodeInspectionState, InspectionPhase, add_audit_entry

logger = logging.getLogger(__name__)


async def run_learning_phase(state: CodeInspectionState) -> CodeInspectionState:
    """Phase 4: Extract and store patterns from inspection results.

    Patterns extracted:
    - Recurring findings across files
    - Security patterns that inform review
    - Bug patterns for future detection

    Args:
        state: Current inspection state

    Returns:
        Updated state with learning results

    """
    logger.info("[Phase 4] Starting learning phase")

    state["current_phase"] = InspectionPhase.LEARNING.value
    add_audit_entry(state, "learning", "Starting Phase 4: Learning")

    if not state.get("learning_enabled", True):
        logger.info("Learning disabled, skipping pattern extraction")
        state["completed_phases"].append(InspectionPhase.LEARNING.value)
        return state

    patterns_extracted: list[dict[str, Any]] = []
    patterns_stored: list[str] = []

    # 1. Extract recurring finding patterns
    recurring = await _extract_recurring_patterns(state)
    patterns_extracted.extend(recurring)

    # 2. Extract cross-tool insight patterns
    insights = await _extract_insight_patterns(state)
    patterns_extracted.extend(insights)

    # 3. Store patterns to disk
    storage_path = Path(state["project_path"]) / "patterns" / "inspection"
    storage_path.mkdir(parents=True, exist_ok=True)

    for pattern in patterns_extracted:
        pattern_id = pattern.get("pattern_id", f"pat_{len(patterns_stored)}")
        pattern_file = storage_path / f"{pattern_id}.json"

        try:
            pattern["stored_at"] = datetime.now().isoformat()
            pattern["execution_id"] = state["execution_id"]

            with open(pattern_file, "w") as f:
                json.dump(pattern, f, indent=2)

            patterns_stored.append(pattern_id)
            logger.debug(f"Stored pattern: {pattern_id}")
        except Exception as e:
            logger.error(f"Failed to store pattern {pattern_id}: {e}")
            state["warnings"].append(f"Failed to store pattern {pattern_id}: {e}")

    # Update state
    state["patterns_extracted"] = patterns_extracted
    state["patterns_stored"] = patterns_stored
    state["learning_metadata"] = {
        "patterns_extracted": len(patterns_extracted),
        "patterns_stored": len(patterns_stored),
        "storage_path": str(storage_path),
    }
    state["completed_phases"].append(InspectionPhase.LEARNING.value)
    state["last_updated"] = datetime.now().isoformat()

    add_audit_entry(
        state,
        "learning",
        "Phase 4 complete",
        {
            "patterns_extracted": len(patterns_extracted),
            "patterns_stored": len(patterns_stored),
        },
    )

    logger.info(
        f"[Phase 4] Complete: {len(patterns_extracted)} patterns extracted, "
        f"{len(patterns_stored)} stored",
    )

    return state


async def _extract_recurring_patterns(
    state: CodeInspectionState,
) -> list[dict[str, Any]]:
    """Extract patterns from recurring findings.

    Looks for findings with the same code/rule that appear multiple times.
    """
    patterns: list[dict[str, Any]] = []

    # Collect all findings
    all_findings: list[dict] = []
    for result_key in ["static_analysis_results", "dynamic_analysis_results"]:
        for result in state.get(result_key, {}).values():
            if result and result.get("findings"):
                all_findings.extend(result["findings"])

    # Group by code/rule
    by_code: dict[str, list[dict]] = {}
    for finding in all_findings:
        code = finding.get("code", "UNKNOWN")
        if code not in by_code:
            by_code[code] = []
        by_code[code].append(finding)

    # Create patterns for recurring issues (3+ occurrences)
    for code, findings in by_code.items():
        if len(findings) >= 3:
            files = list({f.get("file_path", "") for f in findings})
            severities = [f.get("severity", "medium") for f in findings]
            most_common_severity = max(set(severities), key=severities.count)

            pattern = {
                "pattern_id": f"recurring_{code.replace('-', '_')}",
                "pattern_type": "recurring_finding",
                "code": code,
                "occurrence_count": len(findings),
                "affected_files": files[:10],  # Limit to 10
                "severity": most_common_severity,
                "description": findings[0].get("message", ""),
                "category": findings[0].get("category", "unknown"),
                "tool": findings[0].get("tool", "unknown"),
                "confidence": min(1.0, len(findings) / 10),  # Higher count = higher confidence
            }
            patterns.append(pattern)

    return patterns


async def _extract_insight_patterns(
    state: CodeInspectionState,
) -> list[dict[str, Any]]:
    """Extract patterns from cross-tool insights.

    Stores insights as reusable patterns for future inspections.
    """
    patterns: list[dict[str, Any]] = []

    for insight in state.get("cross_tool_insights", []):
        if insight.get("confidence", 0) >= 0.7:
            pattern = {
                "pattern_id": f"insight_{insight.get('insight_id', '')}",
                "pattern_type": "cross_tool_insight",
                "insight_type": insight.get("insight_type"),
                "source_tools": insight.get("source_tools", []),
                "description": insight.get("description", ""),
                "recommendations": insight.get("recommendations", []),
                "affected_files": insight.get("affected_files", []),
                "confidence": insight.get("confidence", 0.7),
            }
            patterns.append(pattern)

    return patterns
