"""
Dynamic Analysis Node - Phase 2

Runs conditional dynamic analysis based on Phase 1 results.
Can skip if critical issues found, or deep-dive if patterns match.

Tools:
- Code Review (anti-pattern detection)
- Memory-Enhanced Debugging (historical bug correlation)
- Advanced Debugging (systematic linter-based)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import logging
from datetime import datetime

from ..adapters import CodeReviewAdapter, DebuggingAdapter
from ..state import CodeInspectionState, InspectionPhase, add_audit_entry

logger = logging.getLogger(__name__)


async def run_dynamic_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """
    Phase 2: Run conditional dynamic analysis.

    Args:
        state: Current inspection state

    Returns:
        Updated state with dynamic analysis results
    """
    logger.info(f"[Phase 2] Starting dynamic analysis for {state['project_path']}")

    state["current_phase"] = InspectionPhase.DYNAMIC_ANALYSIS.value
    add_audit_entry(state, "dynamic_analysis", "Starting Phase 2: Dynamic Analysis")

    project_path = state["project_path"]
    enabled_tools = state["enabled_tools"]

    # Get security context from Phase 1 for informed review
    security_context = []
    if state.get("security_scan_result"):
        security_context = state["security_scan_result"].get("findings", [])

    # Build list of tasks
    tasks = []
    task_names = []

    if enabled_tools.get("code_review", True):
        adapter = CodeReviewAdapter(
            project_root=project_path,
            config=state["tool_configs"].get("code_review"),
            security_context=security_context,
        )
        tasks.append(adapter.analyze(security_informed=bool(security_context)))
        task_names.append("code_review")

    if enabled_tools.get("memory_debugging", True):
        adapter = DebuggingAdapter(
            project_root=project_path,
            config=state["tool_configs"].get("memory_debugging"),
        )
        tasks.append(adapter.analyze_memory_enhanced())
        task_names.append("memory_debugging")

    if not tasks:
        logger.warning("No dynamic analysis tools enabled")
        state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
        return state

    # Run tasks (can be parallel or sequential)
    if state.get("parallel_mode", True) and len(tasks) > 1:
        logger.info(f"Running {len(tasks)} dynamic tools in parallel: {task_names}")
        results = await asyncio.gather(*tasks, return_exceptions=True)
    else:
        logger.info(f"Running {len(tasks)} dynamic tools: {task_names}")
        results = []
        for task in tasks:
            try:
                result = await task
                results.append(result)
            except Exception as e:
                results.append(e)

    # Process results
    total_findings = 0
    historical_matches = []

    for i, result in enumerate(results):
        tool_name = task_names[i]

        if isinstance(result, Exception):
            logger.error(f"Tool {tool_name} failed: {result}")
            state["errors"].append(f"{tool_name}: {str(result)}")
            continue

        # Store result
        state["dynamic_analysis_results"][tool_name] = result

        # Also store in individual fields
        if tool_name == "code_review":
            state["code_review_result"] = result
        elif tool_name == "memory_debugging":
            state["memory_debugging_result"] = result
            # Extract historical matches
            historical_matches.extend(result.get("metadata", {}).get("historical_matches", []))
        elif tool_name == "advanced_debugging":
            state["advanced_debugging_result"] = result

        total_findings += result.get("findings_count", 0)

        logger.info(
            f"{tool_name}: status={result.get('status')}, "
            f"score={result.get('score')}, "
            f"findings={result.get('findings_count')}"
        )

    # Update state
    state["historical_patterns_matched"] = historical_matches
    state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
    state["last_updated"] = datetime.now().isoformat()

    add_audit_entry(
        state,
        "dynamic_analysis",
        "Phase 2 complete",
        {
            "tools_run": task_names,
            "total_findings": total_findings,
            "historical_matches": len(historical_matches),
        },
    )

    logger.info(f"[Phase 2] Complete: {total_findings} findings")

    return state


async def run_deep_dive_analysis(state: CodeInspectionState) -> CodeInspectionState:
    """
    Deep-dive analysis triggered by historical pattern matches.

    Runs additional advanced debugging for files with pattern matches.

    Args:
        state: Current inspection state

    Returns:
        Updated state with deep-dive results
    """
    logger.info("[Phase 2+] Starting deep-dive analysis")

    state["deep_dive_triggered"] = True
    state["deep_dive_reason"] = "Historical pattern matches found"
    add_audit_entry(state, "deep_dive", "Starting deep-dive analysis")

    project_path = state["project_path"]

    # Run advanced debugging for more thorough analysis
    adapter = DebuggingAdapter(
        project_root=project_path,
        config=state["tool_configs"].get("advanced_debugging"),
    )

    try:
        result = await adapter.analyze_advanced()
        state["dynamic_analysis_results"]["advanced_debugging"] = result
        state["advanced_debugging_result"] = result

        logger.info(
            f"Deep-dive: status={result.get('status')}, findings={result.get('findings_count')}"
        )
    except Exception as e:
        logger.error(f"Deep-dive analysis failed: {e}")
        state["errors"].append(f"deep_dive: {str(e)}")

    # Also run standard dynamic analysis
    state = await run_dynamic_analysis(state)

    add_audit_entry(
        state,
        "deep_dive",
        "Deep-dive complete",
        {"advanced_debugging_run": True},
    )

    return state


async def handle_skip_dynamic(state: CodeInspectionState) -> CodeInspectionState:
    """
    Handle skipping dynamic analysis due to critical issues.

    Args:
        state: Current inspection state

    Returns:
        Updated state with skip information
    """
    logger.info(f"[Phase 2] Skipping dynamic analysis: {state.get('skip_reason', 'unknown')}")

    state["dynamic_analysis_skipped"] = True
    state["completed_phases"].append(InspectionPhase.DYNAMIC_ANALYSIS.value)
    state["skipped_phases"].append(f"dynamic_analysis: {state.get('skip_reason', 'unknown')}")

    add_audit_entry(
        state,
        "dynamic_analysis",
        "Phase 2 skipped",
        {"reason": state.get("skip_reason", "unknown")},
    )

    return state
