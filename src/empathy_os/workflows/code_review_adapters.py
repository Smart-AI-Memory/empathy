"""
Code Review Adapters for CodeReviewCrew Integration

Provides format conversion functions between CodeReviewCrew output
and workflow dict formats used by existing workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from empathy_llm_toolkit.agent_factory.crews import CodeReviewReport

logger = logging.getLogger(__name__)


def _check_crew_available() -> bool:
    """
    Check if CodeReviewCrew is available.

    Returns:
        True if the crew module can be imported, False otherwise.
    """
    try:
        from empathy_llm_toolkit.agent_factory.crews import CodeReviewCrew  # noqa: F401

        return True
    except ImportError:
        return False


async def _get_crew_review(
    diff: str,
    files_changed: list[str] | None = None,
    config: dict | None = None,
    timeout: float = 300.0,
) -> "CodeReviewReport | None":
    """
    Get CodeReviewCrew review results with graceful fallback.

    Args:
        diff: Git diff or code to review
        files_changed: List of changed files
        config: Optional CodeReviewConfig parameters as dict
        timeout: Maximum time to wait for review (default 5 minutes)

    Returns:
        CodeReviewReport if successful, None if crew unavailable or failed.
    """
    if not _check_crew_available():
        logger.debug("CodeReviewCrew not available, returning None")
        return None

    try:
        from empathy_llm_toolkit.agent_factory.crews import CodeReviewConfig, CodeReviewCrew

        # Build config from dict
        crew_config = CodeReviewConfig(**(config or {}))
        crew = CodeReviewCrew(config=crew_config)

        # Run with timeout
        report = await asyncio.wait_for(
            crew.review(diff=diff, files_changed=files_changed or []),
            timeout=timeout,
        )
        return report

    except asyncio.TimeoutError:
        logger.warning(f"CodeReviewCrew review timed out after {timeout}s")
        return None
    except Exception as e:
        logger.warning(f"CodeReviewCrew review failed: {e}")
        return None


def crew_report_to_workflow_format(report: "CodeReviewReport") -> dict:
    """
    Convert CodeReviewReport to workflow dict format.

    This converts the crew's structured output to the format expected
    by existing workflows (matching CodeReviewWorkflow output).

    Args:
        report: CodeReviewReport from CodeReviewCrew

    Returns:
        Dict in workflow format with findings, verdict, etc.
    """
    findings = []
    for finding in report.findings:
        finding_dict = {
            "type": finding.category.value if finding.category else "other",
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity.value if finding.severity else "medium",
            "file": finding.file_path,
            "line": finding.line_number,
            "code_snippet": finding.code_snippet,
            "suggestion": finding.suggestion,
            "before_code": finding.before_code,
            "after_code": finding.after_code,
            "confidence": finding.confidence,
        }
        findings.append(finding_dict)

    # Build severity breakdown
    severity_counts = {
        "critical": len([f for f in report.findings if f.severity.value == "critical"]),
        "high": len([f for f in report.findings if f.severity.value == "high"]),
        "medium": len([f for f in report.findings if f.severity.value == "medium"]),
        "low": len([f for f in report.findings if f.severity.value == "low"]),
        "info": len([f for f in report.findings if f.severity.value == "info"]),
    }

    # Build category breakdown
    by_category: dict[str, int] = {}
    for finding in report.findings:
        cat = finding.category.value
        by_category[cat] = by_category.get(cat, 0) + 1

    return {
        "crew_enabled": True,
        "findings": findings,
        "finding_count": len(findings),
        "verdict": report.verdict.value,
        "quality_score": report.quality_score,
        "has_blocking_issues": report.has_blocking_issues,
        "summary": report.summary,
        "assessment": {
            "quality_score": report.quality_score,
            "verdict": report.verdict.value,
            "severity_breakdown": severity_counts,
            "by_category": by_category,
            "critical_findings": [f for f in findings if f["severity"] == "critical"],
            "high_findings": [f for f in findings if f["severity"] == "high"],
        },
        "agents_used": report.agents_used,
        "memory_graph_hits": report.memory_graph_hits,
        "review_duration_seconds": report.review_duration_seconds,
        "metadata": report.metadata,
    }


def workflow_findings_to_crew_format(findings: list[dict]) -> list[dict]:
    """
    Convert workflow findings to ReviewFinding-compatible dicts.

    This is useful when passing workflow findings to CodeReviewCrew
    for enhanced analysis.

    Args:
        findings: List of finding dicts from workflow

    Returns:
        List of dicts that can be used with CodeReviewCrew context.
    """
    crew_findings = []
    for finding in findings:
        crew_finding = {
            "title": finding.get("title", finding.get("type", "Unknown")),
            "description": finding.get("description", finding.get("match", "")),
            "severity": finding.get("severity", "medium"),
            "category": _map_type_to_category(finding.get("type", "other")),
            "file_path": finding.get("file"),
            "line_number": finding.get("line"),
            "code_snippet": finding.get("code_snippet") or finding.get("match"),
            "suggestion": finding.get("suggestion") or finding.get("remediation"),
            "confidence": finding.get("confidence", 1.0),
        }
        crew_findings.append(crew_finding)
    return crew_findings


def merge_code_review_results(
    crew_report: dict | None,
    workflow_findings: dict | None,
) -> dict:
    """
    Merge CodeReviewCrew and workflow code review results.

    Combines findings from both sources, deduplicating where possible,
    and provides a unified assessment.

    Args:
        crew_report: Crew results in workflow format (from crew_report_to_workflow_format)
        workflow_findings: Workflow code review results

    Returns:
        Merged dict with combined findings and assessment.
    """
    # Handle None cases
    if crew_report is None and workflow_findings is None:
        return {
            "findings": [],
            "quality_score": 100,
            "verdict": "approve",
            "merged": False,
        }

    if crew_report is None and workflow_findings is not None:
        return {**workflow_findings, "merged": False, "crew_enabled": False}

    if workflow_findings is None and crew_report is not None:
        return {**crew_report, "merged": False}

    # At this point, both should be non-None
    assert crew_report is not None
    assert workflow_findings is not None

    # Merge findings (prefer crew findings for duplicates)
    crew_findings = crew_report.get("findings", [])
    wf_findings = workflow_findings.get("findings", [])

    # Build set of crew finding keys for deduplication
    crew_keys = set()
    for f in crew_findings:
        key = (f.get("file"), f.get("line"), f.get("type"))
        crew_keys.add(key)

    # Add non-duplicate workflow findings
    merged_findings = list(crew_findings)
    for f in wf_findings:
        key = (f.get("file"), f.get("line"), f.get("type"))
        if key not in crew_keys:
            merged_findings.append(f)

    # Calculate merged quality score (weighted average)
    crew_score = crew_report.get("quality_score", 100)
    wf_score = workflow_findings.get("security_score", 90)
    # Give crew score higher weight (more comprehensive)
    merged_score = (crew_score * 0.7 + wf_score * 0.3) if wf_score else crew_score

    # Determine verdict (take more severe)
    crew_verdict = crew_report.get("verdict", "approve")
    wf_verdict = workflow_findings.get("verdict", "approve")
    verdict = _merge_verdicts(crew_verdict, wf_verdict)

    # Merge severity counts
    crew_severity = crew_report.get("assessment", {}).get("severity_breakdown", {})
    wf_severity = workflow_findings.get("assessment", {}).get("severity_breakdown", {})
    merged_severity = {
        "critical": max(crew_severity.get("critical", 0), wf_severity.get("critical", 0)),
        "high": max(crew_severity.get("high", 0), wf_severity.get("high", 0)),
        "medium": max(crew_severity.get("medium", 0), wf_severity.get("medium", 0)),
        "low": max(crew_severity.get("low", 0), wf_severity.get("low", 0)),
    }

    return {
        "merged": True,
        "crew_enabled": True,
        "findings": merged_findings,
        "finding_count": len(merged_findings),
        "quality_score": merged_score,
        "verdict": verdict,
        "has_blocking_issues": (
            merged_severity.get("critical", 0) > 0 or merged_severity.get("high", 0) > 3
        ),
        "assessment": {
            "quality_score": merged_score,
            "verdict": verdict,
            "severity_breakdown": merged_severity,
            "critical_findings": [f for f in merged_findings if f.get("severity") == "critical"],
            "high_findings": [f for f in merged_findings if f.get("severity") == "high"],
        },
        "crew_summary": crew_report.get("summary", ""),
        "agents_used": crew_report.get("agents_used", []),
    }


def _merge_verdicts(verdict1: str, verdict2: str) -> str:
    """Merge two verdicts, taking the more severe one."""
    severity_order = ["reject", "request_changes", "approve_with_suggestions", "approve"]

    # Normalize verdicts
    v1 = verdict1.lower().replace("-", "_")
    v2 = verdict2.lower().replace("-", "_")

    idx1 = severity_order.index(v1) if v1 in severity_order else 3
    idx2 = severity_order.index(v2) if v2 in severity_order else 3

    # Return more severe (lower index)
    return severity_order[min(idx1, idx2)]


def _map_type_to_category(vuln_type: str) -> str:
    """Map workflow vulnerability type to crew category."""
    mapping = {
        "sql_injection": "security",
        "xss": "security",
        "command_injection": "security",
        "path_traversal": "security",
        "hardcoded_secret": "security",
        "insecure_random": "security",
        "code_smell": "quality",
        "complexity": "quality",
        "duplicate": "quality",
        "performance": "performance",
        "n_plus_one": "performance",
        "architecture": "architecture",
        "design": "architecture",
        "solid": "architecture",
        "test": "testing",
        "coverage": "testing",
    }
    return mapping.get(vuln_type.lower(), "other")
