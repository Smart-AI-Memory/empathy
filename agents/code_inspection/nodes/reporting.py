"""Reporting Node - Final Phase

Generates unified health report from all inspection results.
Provides multiple output formats: terminal, JSON, markdown.
Includes baseline/suppression filtering support.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any

from ..baseline import BaselineManager
from ..state import (
    CodeInspectionState,
    InspectionPhase,
    add_audit_entry,
    calculate_health_score,
    get_health_grade,
    get_health_status,
)

logger = logging.getLogger(__name__)


async def generate_unified_report(state: CodeInspectionState) -> CodeInspectionState:
    """Generate unified inspection report.

    Aggregates results from all phases into a single health report
    with categorized findings and prioritized recommendations.

    Args:
        state: Current inspection state

    Returns:
        Updated state with final report

    """
    logger.info("[Reporting] Generating unified report")

    state["current_phase"] = InspectionPhase.REPORTING.value
    add_audit_entry(state, "reporting", "Generating unified report")

    # Calculate overall health score
    all_results = {
        **state.get("static_analysis_results", {}),
        **state.get("dynamic_analysis_results", {}),
    }
    overall_score = calculate_health_score(all_results)
    state["overall_health_score"] = overall_score
    state["health_status"] = get_health_status(overall_score)
    state["health_grade"] = get_health_grade(overall_score)

    # Calculate category scores
    state["category_scores"] = _calculate_category_scores(all_results)

    # Aggregate all findings
    all_findings = _collect_all_findings(state)
    state["total_findings"] = len(all_findings)

    # Count by severity
    by_severity: dict[str, int] = defaultdict(int)
    for finding in all_findings:
        by_severity[finding.get("severity", "medium")] += 1
    state["findings_by_severity"] = dict(by_severity)

    # Count by category
    by_category: dict[str, int] = defaultdict(int)
    for finding in all_findings:
        by_category[finding.get("category", "unknown")] += 1
    state["findings_by_category"] = dict(by_category)

    # Count by tool
    by_tool: dict[str, int] = defaultdict(int)
    for finding in all_findings:
        by_tool[finding.get("tool", "unknown")] += 1
    state["findings_by_tool"] = dict(by_tool)

    # Identify fixable issues
    fixable = [f for f in all_findings if f.get("fixable")]
    state["fixable_count"] = len(fixable)
    state["auto_fixable"] = fixable[:20]  # Top 20 auto-fixable

    # Identify manual fixes
    manual = [f for f in all_findings if not f.get("fixable")]
    state["manual_fixes"] = manual[:20]  # Top 20 manual

    # Identify blocking issues (critical + high)
    blocking = [f for f in all_findings if f.get("severity") in ("critical", "high")]
    state["blocking_issues"] = blocking

    # Generate recommendations
    state["recommendations"] = _generate_recommendations(state, all_findings)

    # Generate predictions (Level 4)
    state["predictions"] = _generate_predictions(state)

    # Calculate total duration
    start_time = datetime.fromisoformat(state["created_at"])
    end_time = datetime.now()
    state["total_duration_ms"] = int((end_time - start_time).total_seconds() * 1000)

    # Mark complete
    state["completed_phases"].append(InspectionPhase.REPORTING.value)
    state["current_phase"] = InspectionPhase.COMPLETE.value
    state["last_updated"] = datetime.now().isoformat()

    add_audit_entry(
        state,
        "reporting",
        "Report complete",
        {
            "overall_score": overall_score,
            "health_status": state["health_status"],
            "total_findings": state["total_findings"],
            "blocking_count": len(blocking),
            "duration_ms": state["total_duration_ms"],
        },
    )

    logger.info(
        f"[Reporting] Complete: Score={overall_score}, "
        f"Status={state['health_status']}, "
        f"Findings={state['total_findings']}",
    )

    return state


def _calculate_category_scores(results: dict[str, Any]) -> dict[str, int]:
    """Calculate scores by category."""
    category_scores: dict[str, int] = {}

    tool_to_category = {
        "code_health": "lint",
        "security": "security",
        "test_quality": "tests",
        "tech_debt": "debt",
        "code_review": "review",
        "memory_debugging": "debugging",
        "advanced_debugging": "debugging",
    }

    for tool_name, result in results.items():
        if result and result.get("status") not in ("skip", "pending"):
            category = tool_to_category.get(tool_name, "other")
            score = result.get("score", 0)

            # Average if multiple tools map to same category
            if category in category_scores:
                category_scores[category] = (category_scores[category] + score) // 2
            else:
                category_scores[category] = score

    return category_scores


def _collect_all_findings(
    state: CodeInspectionState,
    apply_baseline: bool = True,
) -> list[dict]:
    """Collect all findings from all tools.

    Args:
        state: Current inspection state
        apply_baseline: Whether to filter suppressed findings

    Returns:
        List of findings (filtered if apply_baseline is True)

    """
    all_findings: list[dict] = []

    # Collect from static analysis results
    static_results: dict[str, Any] = state.get("static_analysis_results", {})
    for result in static_results.values():
        if result and result.get("findings"):
            all_findings.extend(result["findings"])

    # Collect from dynamic analysis results
    dynamic_results: dict[str, Any] = state.get("dynamic_analysis_results", {})
    for result in dynamic_results.values():
        if result and result.get("findings"):
            all_findings.extend(result["findings"])

    # Apply baseline filtering if enabled (check both parameter and state)
    baseline_from_state = state.get("baseline_enabled", True)
    if apply_baseline and baseline_from_state:
        project_path = state.get("project_path", ".")
        baseline_manager = BaselineManager(project_path)
        baseline_manager.load()

        # Filter and track suppressed findings
        filtered_findings = baseline_manager.filter_findings(all_findings)

        # Store suppression stats in state for reporting
        suppressed_count = len(all_findings) - len(filtered_findings)
        if suppressed_count > 0:
            state["_suppressed_count"] = suppressed_count  # type: ignore
            state["_suppression_stats"] = baseline_manager.get_suppression_stats()  # type: ignore

        all_findings = filtered_findings

    # Sort by priority_score (highest first)
    all_findings.sort(key=lambda f: -f.get("priority_score", 50))

    return all_findings


def _generate_recommendations(
    state: CodeInspectionState,
    findings: list[dict],
) -> list[dict]:
    """Generate prioritized recommendations from findings and insights."""
    recommendations: list[dict] = []

    # 1. Critical issues first
    critical_count = state["findings_by_severity"].get("critical", 0)
    if critical_count > 0:
        recommendations.append(
            {
                "priority": "critical",
                "action": f"Fix {critical_count} critical issues immediately",
                "rationale": "Critical issues may cause security vulnerabilities or system failures",
                "estimated_effort": "high",
            },
        )

    # 2. High severity issues
    high_count = state["findings_by_severity"].get("high", 0)
    if high_count > 0:
        recommendations.append(
            {
                "priority": "high",
                "action": f"Address {high_count} high-severity findings",
                "rationale": "High-severity issues should be fixed before release",
                "estimated_effort": "medium",
            },
        )

    # 3. Add recommendations from cross-tool insights
    for insight in state.get("cross_tool_insights", []):
        if insight.get("confidence", 0) >= 0.7:
            for rec in insight.get("recommendations", [])[:2]:
                recommendations.append(
                    {
                        "priority": "medium",
                        "action": rec,
                        "rationale": insight.get("description", ""),
                        "estimated_effort": "low",
                    },
                )

    # 4. Auto-fix recommendation
    if state.get("fixable_count", 0) > 0:
        recommendations.append(
            {
                "priority": "low",
                "action": f"Auto-fix {state['fixable_count']} issues with `empathy inspect --fix`",
                "rationale": "Quick wins that improve code quality with minimal effort",
                "estimated_effort": "low",
            },
        )

    return recommendations[:10]  # Top 10 recommendations


def _generate_predictions(state: CodeInspectionState) -> list[dict]:
    """Generate Level 4 predictions based on patterns and trends."""
    predictions: list[dict] = []

    # 1. Predict based on tech debt trajectory
    debt_impact = state.get("debt_trajectory_impact", {})
    trend = debt_impact.get("trajectory", "stable")

    if trend == "increasing":
        predictions.append(
            {
                "prediction_type": "tech_debt_growth",
                "description": "Tech debt likely to increase if not addressed",
                "confidence": 0.7,
                "timeframe": "30 days",
                "recommendation": "Allocate 20% of sprint capacity to debt reduction",
            },
        )
    elif trend == "exploding":
        predictions.append(
            {
                "prediction_type": "tech_debt_crisis",
                "description": "Tech debt on unsustainable trajectory",
                "confidence": 0.85,
                "timeframe": "14 days",
                "recommendation": "Schedule dedicated debt reduction sprint",
            },
        )

    # 2. Predict based on historical patterns
    historical_matches = state.get("historical_patterns_matched", [])
    if len(historical_matches) >= 3:
        predictions.append(
            {
                "prediction_type": "recurring_bugs",
                "description": f"{len(historical_matches)} patterns suggest recurring bug types",
                "confidence": 0.75,
                "timeframe": "next release",
                "recommendation": "Add regression tests for matched patterns",
            },
        )

    # 3. Predict based on security findings
    security_result = state.get("security_scan_result")
    if security_result:
        critical = security_result.get("findings_by_severity", {}).get("critical", 0)
        if critical > 0:
            predictions.append(
                {
                    "prediction_type": "security_incident",
                    "description": f"{critical} critical vulnerabilities increase incident risk",
                    "confidence": 0.8,
                    "timeframe": "if deployed",
                    "recommendation": "Do not deploy until critical issues are resolved",
                },
            )

    return predictions


# =============================================================================
# Output Formatters
# =============================================================================


def format_report_terminal(state: CodeInspectionState) -> str:
    """Format report for terminal display."""
    lines = []

    # Header with health score
    score = state["overall_health_score"]
    status = state["health_status"]
    grade = state["health_grade"]

    # Status indicator for visual feedback
    status_indicator = "PASS" if status == "pass" else "WARN" if status == "warn" else "FAIL"

    lines.append("\n" + "=" * 60)
    lines.append("  CODE INSPECTION REPORT")
    lines.append("=" * 60)
    lines.append(f"\n  Health Score: {score}/100 ({grade}) - {status_indicator}")

    # Category breakdown
    lines.append("\n  CATEGORY SCORES:")
    for category, cat_score in state.get("category_scores", {}).items():
        cat_status = "PASS" if cat_score >= 85 else "WARN" if cat_score >= 70 else "FAIL"
        lines.append(f"    {category.capitalize():15} {cat_score:3}/100  [{cat_status}]")

    # Findings summary
    suppressed: int = int(state.get("_suppressed_count", 0) or 0)
    if suppressed > 0:
        lines.append(f"\n  FINDINGS: {state['total_findings']} total ({suppressed} suppressed)")
    else:
        lines.append(f"\n  FINDINGS: {state['total_findings']} total")
    for severity, count in state.get("findings_by_severity", {}).items():
        if count > 0:
            lines.append(f"    {severity.upper():10} {count}")

    # Blocking issues
    blocking = state.get("blocking_issues", [])
    if blocking:
        lines.append(f"\n  BLOCKING ISSUES ({len(blocking)}):")
        for issue in blocking[:5]:
            lines.append(f"    [{issue['severity'].upper()}] {issue['file_path']}")
            lines.append(f"      {issue['message'][:60]}...")

    # Recommendations
    recommendations = state.get("recommendations", [])
    if recommendations:
        lines.append("\n  RECOMMENDATIONS:")
        for i, rec in enumerate(recommendations[:5], 1):
            lines.append(f"    {i}. [{rec['priority'].upper()}] {rec['action']}")

    # Footer
    lines.append("\n" + "=" * 60)
    lines.append(f"  Duration: {state['total_duration_ms']}ms")
    lines.append(f"  Execution ID: {state['execution_id']}")
    lines.append("=" * 60 + "\n")

    return "\n".join(lines)


def format_report_json(state: CodeInspectionState) -> str:
    """Format report as JSON."""
    report = {
        "health_score": state["overall_health_score"],
        "health_status": state["health_status"],
        "health_grade": state["health_grade"],
        "category_scores": state.get("category_scores", {}),
        "total_findings": state["total_findings"],
        "findings_by_severity": state.get("findings_by_severity", {}),
        "findings_by_category": state.get("findings_by_category", {}),
        "blocking_issues": state.get("blocking_issues", []),
        "recommendations": state.get("recommendations", []),
        "predictions": state.get("predictions", []),
        "cross_tool_insights": state.get("cross_tool_insights", []),
        "execution_id": state["execution_id"],
        "duration_ms": state["total_duration_ms"],
        "created_at": state["created_at"],
    }
    return json.dumps(report, indent=2)


def format_report_markdown(state: CodeInspectionState) -> str:
    """Format report as Markdown."""
    lines = []

    score = state["overall_health_score"]
    status = state["health_status"]
    grade = state["health_grade"]

    lines.append("# Code Inspection Report\n")
    lines.append(f"**Health Score:** {score}/100 ({grade})")
    lines.append(f"**Status:** {status.upper()}\n")

    # Category table
    lines.append("## Category Scores\n")
    lines.append("| Category | Score | Status |")
    lines.append("|----------|-------|--------|")
    for category, cat_score in state.get("category_scores", {}).items():
        cat_status = "PASS" if cat_score >= 85 else "WARN" if cat_score >= 70 else "FAIL"
        lines.append(f"| {category.capitalize()} | {cat_score} | {cat_status} |")

    # Findings summary
    lines.append("\n## Findings Summary\n")
    lines.append(f"**Total:** {state['total_findings']}\n")

    if state.get("findings_by_severity"):
        lines.append("| Severity | Count |")
        lines.append("|----------|-------|")
        for severity, count in state["findings_by_severity"].items():
            lines.append(f"| {severity.upper()} | {count} |")

    # Blocking issues
    blocking = state.get("blocking_issues", [])
    if blocking:
        lines.append(f"\n## Blocking Issues ({len(blocking)})\n")
        for issue in blocking[:10]:
            lines.append(f"- **[{issue['severity'].upper()}]** `{issue['file_path']}`")
            lines.append(f"  - {issue['message']}")

    # Recommendations
    if state.get("recommendations"):
        lines.append("\n## Recommendations\n")
        for rec in state["recommendations"]:
            lines.append(f"- **[{rec['priority'].upper()}]** {rec['action']}")

    # Metadata
    lines.append("\n---\n")
    lines.append(f"*Execution ID: {state['execution_id']}*")
    lines.append(f"*Duration: {state['total_duration_ms']}ms*")

    return "\n".join(lines)


def format_report_sarif(state: CodeInspectionState) -> str:
    """Format report as SARIF 2.1.0 for GitHub Actions integration.

    SARIF (Static Analysis Results Interchange Format) enables:
    - GitHub PR annotations showing issues inline
    - Integration with GitHub Code Scanning
    - Standardized format for security tools
    """
    # Collect all findings
    all_findings = _collect_all_findings(state)

    # Build unique rules from finding codes
    rules: list[dict] = []
    rule_ids_seen: set[str] = set()

    for finding in all_findings:
        rule_id = finding.get("code", "unknown")
        if rule_id not in rule_ids_seen:
            rule_ids_seen.add(rule_id)
            rules.append(
                {
                    "id": rule_id,
                    "name": rule_id.replace("_", " ").title(),
                    "shortDescription": {"text": finding.get("message", "")[:100]},
                    "fullDescription": {"text": finding.get("message", "")},
                    "defaultConfiguration": {
                        "level": _severity_to_sarif_level(finding.get("severity", "medium")),
                    },
                    "properties": {
                        "category": finding.get("category", "unknown"),
                        "tool": finding.get("tool", "unknown"),
                    },
                },
            )

    # Build results from findings
    results: list[dict] = []
    for finding in all_findings:
        result: dict[str, Any] = {
            "ruleId": finding.get("code", "unknown"),
            "level": _severity_to_sarif_level(finding.get("severity", "medium")),
            "message": {"text": finding.get("message", "No message")},
        }

        # Add location if available
        if finding.get("file_path"):
            location: dict[str, Any] = {
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": finding["file_path"],
                        "uriBaseId": "%SRCROOT%",
                    },
                },
            }

            # Add line number if available
            if finding.get("line_number"):
                location["physicalLocation"]["region"] = {
                    "startLine": finding["line_number"],
                }

            result["locations"] = [location]

        # Add fix suggestion if available
        if finding.get("remediation"):
            result["fixes"] = [
                {
                    "description": {"text": finding["remediation"]},
                },
            ]

        results.append(result)

    # Build full SARIF document
    sarif = {
        "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "empathy-inspect",
                        "version": "2.2.9",
                        "informationUri": "https://github.com/smart-ai-memory/empathy-framework",
                        "rules": rules,
                    },
                },
                "results": results,
                "invocations": [
                    {
                        "executionSuccessful": state["health_status"] != "fail",
                        "endTimeUtc": state.get("last_updated", datetime.now().isoformat()),
                    },
                ],
            },
        ],
    }

    return json.dumps(sarif, indent=2)


def _severity_to_sarif_level(severity: str) -> str:
    """Map Empathy severity to SARIF level."""
    mapping = {
        "critical": "error",
        "high": "error",
        "medium": "warning",
        "low": "note",
        "info": "note",
    }
    return mapping.get(severity.lower(), "warning")


def format_report_html(state: CodeInspectionState, include_trends: bool = False) -> str:
    """Format report as HTML dashboard.

    Creates a visual dashboard with:
    - Health score gauge
    - Category score cards
    - Findings table
    - Recommendations list
    - Optional trend chart (if historical data available)
    """
    score = state["overall_health_score"]
    status = state["health_status"]
    grade = state["health_grade"]

    # Color based on score
    if score >= 85:
        score_color = "#10b981"  # green
    elif score >= 70:
        score_color = "#f59e0b"  # yellow
    else:
        score_color = "#ef4444"  # red

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Inspection Report</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f3f4f6; color: #1f2937; line-height: 1.5; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 2rem; }}
        .header {{ background: linear-gradient(135deg, #4f46e5, #7c3aed); color: white; padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; }}
        .header h1 {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
        .score-display {{ display: flex; align-items: center; gap: 1rem; margin-top: 1rem; }}
        .score-circle {{ width: 100px; height: 100px; border-radius: 50%; background: rgba(255,255,255,0.2); display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: bold; }}
        .score-details {{ flex: 1; }}
        .status-badge {{ display: inline-block; padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.875rem; font-weight: 600; text-transform: uppercase; }}
        .status-pass {{ background: #10b981; }}
        .status-warn {{ background: #f59e0b; }}
        .status-fail {{ background: #ef4444; }}
        .cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
        .card {{ background: white; padding: 1.25rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .card h3 {{ font-size: 0.875rem; color: #6b7280; text-transform: uppercase; margin-bottom: 0.5rem; }}
        .card .value {{ font-size: 1.75rem; font-weight: bold; }}
        .section {{ background: white; padding: 1.5rem; border-radius: 0.75rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); margin-bottom: 1.5rem; }}
        .section h2 {{ font-size: 1.125rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #e5e7eb; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ padding: 0.75rem; text-align: left; border-bottom: 1px solid #e5e7eb; }}
        th {{ font-size: 0.75rem; text-transform: uppercase; color: #6b7280; }}
        .severity {{ padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .severity-critical {{ background: #fef2f2; color: #991b1b; }}
        .severity-high {{ background: #fef2f2; color: #991b1b; }}
        .severity-medium {{ background: #fffbeb; color: #92400e; }}
        .severity-low {{ background: #ecfdf5; color: #065f46; }}
        .severity-info {{ background: #eff6ff; color: #1e40af; }}
        .recommendations li {{ padding: 0.75rem 0; border-bottom: 1px solid #e5e7eb; }}
        .recommendations li:last-child {{ border-bottom: none; }}
        .priority {{ font-weight: 600; margin-right: 0.5rem; }}
        .footer {{ text-align: center; color: #6b7280; font-size: 0.875rem; margin-top: 2rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Inspection Report</h1>
            <div class="score-display">
                <div class="score-circle" style="border: 4px solid {score_color};">{score}</div>
                <div class="score-details">
                    <div style="font-size: 1.25rem; font-weight: 600;">Health Score: {score}/100 ({grade})</div>
                    <span class="status-badge status-{status}">{status}</span>
                </div>
            </div>
        </div>

        <div class="cards">
"""

    # Category cards
    for category, cat_score in state.get("category_scores", {}).items():
        cat_color = "#10b981" if cat_score >= 85 else "#f59e0b" if cat_score >= 70 else "#ef4444"
        html += f"""            <div class="card">
                <h3>{category.capitalize()}</h3>
                <div class="value" style="color: {cat_color};">{cat_score}%</div>
            </div>
"""

    html += """        </div>

        <div class="section">
            <h2>Findings Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>Count</th>
                    </tr>
                </thead>
                <tbody>
"""

    for severity, count in state.get("findings_by_severity", {}).items():
        html += f"""                    <tr>
                        <td><span class="severity severity-{severity}">{severity}</span></td>
                        <td>{count}</td>
                    </tr>
"""

    html += """                </tbody>
            </table>
        </div>
"""

    # Blocking issues
    blocking = state.get("blocking_issues", [])
    if blocking:
        html += f"""        <div class="section">
            <h2>Blocking Issues ({len(blocking)})</h2>
            <table>
                <thead>
                    <tr>
                        <th>Severity</th>
                        <th>File</th>
                        <th>Message</th>
                    </tr>
                </thead>
                <tbody>
"""
        for issue in blocking[:10]:
            severity = issue.get("severity", "medium")
            html += f"""                    <tr>
                        <td><span class="severity severity-{severity}">{severity}</span></td>
                        <td><code>{issue.get("file_path", "N/A")}</code></td>
                        <td>{issue.get("message", "No message")[:80]}</td>
                    </tr>
"""
        html += """                </tbody>
            </table>
        </div>
"""

    # Recommendations
    recommendations = state.get("recommendations", [])
    if recommendations:
        html += """        <div class="section">
            <h2>Recommendations</h2>
            <ul class="recommendations">
"""
        for rec in recommendations:
            html += f"""                <li>
                    <span class="priority">[{rec["priority"].upper()}]</span>
                    {rec["action"]}
                </li>
"""
        html += """            </ul>
        </div>
"""

    # Footer
    html += f"""        <div class="footer">
            <p>Execution ID: {state["execution_id"]} | Duration: {state.get("total_duration_ms", 0)}ms</p>
            <p>Generated by empathy-inspect v2.2.9</p>
        </div>
    </div>
</body>
</html>"""

    return html
