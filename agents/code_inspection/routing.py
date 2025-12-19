"""
Routing Logic for Code Inspection Pipeline

Conditional routing functions that determine the pipeline path
based on Phase 1 results.

Following the pattern from compliance_anticipation_agent.py.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Literal

from .state import CodeInspectionState

logger = logging.getLogger(__name__)


def should_run_dynamic_analysis(
    state: CodeInspectionState,
) -> Literal["skip_critical_security", "skip_type_errors", "deep_dive", "proceed"]:
    """
    Routing function: Decide whether to proceed with dynamic analysis.

    Routes based on Phase 1 static analysis results:
    - Skip if critical security issues found
    - Skip if type errors prevent analysis
    - Deep-dive if historical patterns match
    - Proceed with standard dynamic analysis

    Args:
        state: Current inspection state after Phase 1

    Returns:
        Route name: skip_critical_security, skip_type_errors, deep_dive, proceed
    """
    # Check for critical security issues
    security_result = state.get("security_scan_result")
    if security_result and security_result.get("status") != "skip":
        critical_count = security_result.get("findings_by_severity", {}).get("critical", 0)
        if critical_count > 0:
            logger.info(f"Routing: skip_critical_security ({critical_count} critical issues)")
            state["skip_reason"] = f"{critical_count} critical security issues found"
            return "skip_critical_security"

    # Check for type errors that prevent analysis
    code_health_result = state.get("code_health_result")
    if code_health_result and code_health_result.get("status") != "skip":
        metadata = code_health_result.get("metadata", {})
        results_by_category = metadata.get("results_by_category", {})
        types_result = results_by_category.get("types", {})

        if types_result.get("status") == "fail":
            logger.info("Routing: skip_type_errors (type check failed)")
            state["skip_reason"] = "Type check failed - syntax/import errors prevent analysis"
            return "skip_type_errors"

    # Check for historical pattern matches (trigger deep-dive)
    historical_matches = state.get("historical_patterns_matched", [])
    if historical_matches:
        high_confidence = [m for m in historical_matches if m.get("similarity_score", 0) >= 0.8]
        if high_confidence:
            logger.info(f"Routing: deep_dive ({len(high_confidence)} high-confidence matches)")
            return "deep_dive"

    # Quick mode skips dynamic analysis
    if state.get("quick_mode", False):
        logger.info("Routing: skip (quick mode enabled)")
        state["skip_reason"] = "Quick mode enabled - skipping dynamic analysis"
        return "skip_critical_security"  # Using same skip path

    # Standard path
    logger.info("Routing: proceed with dynamic analysis")
    return "proceed"


def should_continue_to_learning(
    state: CodeInspectionState,
) -> Literal["learn", "skip_learning"]:
    """
    Routing function: Decide whether to run learning phase.

    Args:
        state: Current inspection state after Phase 3

    Returns:
        Route name: learn or skip_learning
    """
    if not state.get("learning_enabled", True):
        logger.info("Routing: skip_learning (learning disabled)")
        return "skip_learning"

    # Skip learning if too many errors
    if len(state.get("errors", [])) > 5:
        logger.info("Routing: skip_learning (too many errors)")
        return "skip_learning"

    logger.info("Routing: proceed to learning")
    return "learn"


def get_severity_route(
    state: CodeInspectionState,
) -> Literal["critical", "high", "medium", "low"]:
    """
    Get route based on highest severity finding.

    Args:
        state: Current inspection state

    Returns:
        Severity level: critical, high, medium, low
    """
    findings_by_severity = state.get("findings_by_severity", {})

    if findings_by_severity.get("critical", 0) > 0:
        return "critical"
    elif findings_by_severity.get("high", 0) > 0:
        return "high"
    elif findings_by_severity.get("medium", 0) > 0:
        return "medium"
    else:
        return "low"
