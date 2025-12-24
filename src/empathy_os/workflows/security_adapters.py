"""
Security Adapters for SecurityAuditCrew Integration

Provides format conversion functions between SecurityAuditCrew output
and workflow dict formats used by existing workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from empathy_llm_toolkit.agent_factory.crews import SecurityReport

logger = logging.getLogger(__name__)


def _check_crew_available() -> bool:
    """
    Check if SecurityAuditCrew is available.

    Returns:
        True if the crew module can be imported, False otherwise.
    """
    try:
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditCrew  # noqa: F401

        return True
    except ImportError:
        return False


async def _get_crew_audit(
    target: str,
    config: dict | None = None,
    timeout: float = 300.0,
) -> "SecurityReport | None":
    """
    Get SecurityAuditCrew audit results with graceful fallback.

    Args:
        target: Path to codebase to audit
        config: Optional SecurityAuditConfig parameters as dict
        timeout: Maximum time to wait for audit (default 5 minutes)

    Returns:
        SecurityReport if successful, None if crew unavailable or audit failed.
    """
    if not _check_crew_available():
        logger.debug("SecurityAuditCrew not available, returning None")
        return None

    try:
        from empathy_llm_toolkit.agent_factory.crews import SecurityAuditConfig, SecurityAuditCrew

        # Build config from dict
        crew_config = SecurityAuditConfig(**(config or {}))
        crew = SecurityAuditCrew(config=crew_config)

        # Run with timeout
        report = await asyncio.wait_for(crew.audit(target), timeout=timeout)
        return report

    except asyncio.TimeoutError:
        logger.warning(f"SecurityAuditCrew audit timed out after {timeout}s")
        return None
    except Exception as e:
        logger.warning(f"SecurityAuditCrew audit failed: {e}")
        return None


def crew_report_to_workflow_format(report: "SecurityReport") -> dict:
    """
    Convert SecurityReport to workflow dict format.

    This converts the crew's structured output to the format expected
    by existing workflows (matching SecurityAuditWorkflow output).

    Args:
        report: SecurityReport from SecurityAuditCrew

    Returns:
        Dict in workflow format with findings, assessment, etc.
    """
    findings: list[dict] = []
    for finding in report.findings:
        finding_dict = {
            "type": finding.category.value if finding.category else "other",
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity.value if finding.severity else "medium",
            "file": finding.file_path,
            "line": finding.line_number,
            "match": finding.code_snippet[:100] if finding.code_snippet else None,
            "remediation": finding.remediation,
            "cwe_id": finding.cwe_id,
            "cvss_score": finding.cvss_score,
            "confidence": finding.confidence,
            "owasp": _map_category_to_owasp(finding.category.value) if finding.category else None,
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

    # Build OWASP category breakdown
    by_owasp: dict[str, int] = {}
    for f_dict in findings:
        owasp = f_dict.get("owasp", "Other")
        by_owasp[owasp] = by_owasp.get(owasp, 0) + 1

    return {
        "crew_enabled": True,
        "findings": findings,
        "finding_count": len(findings),
        "risk_score": report.risk_score,
        "risk_level": _score_to_level(report.risk_score),
        "summary": report.summary,
        "assessment": {
            "risk_score": report.risk_score,
            "risk_level": _score_to_level(report.risk_score),
            "severity_breakdown": severity_counts,
            "by_owasp_category": by_owasp,
            "critical_findings": [f for f in findings if f["severity"] == "critical"],
            "high_findings": [f for f in findings if f["severity"] == "high"],
        },
        "agents_used": report.agents_used,
        "memory_graph_hits": report.memory_graph_hits,
        "audit_duration_seconds": report.audit_duration_seconds,
        "metadata": report.metadata,
    }


def workflow_findings_to_crew_format(findings: list[dict]) -> list[dict]:
    """
    Convert workflow findings to SecurityFinding-compatible dicts.

    This is useful when passing workflow findings to SecurityAuditCrew
    for enhanced analysis.

    Args:
        findings: List of finding dicts from workflow

    Returns:
        List of dicts that can be used with SecurityAuditCrew context.
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
            "code_snippet": finding.get("match"),
            "cwe_id": finding.get("cwe_id"),
            "confidence": finding.get("confidence", 1.0),
        }
        crew_findings.append(crew_finding)
    return crew_findings


def merge_security_results(
    crew_report: dict | None,
    workflow_findings: dict | None,
) -> dict:
    """
    Merge SecurityAuditCrew and workflow security results.

    Combines findings from both sources, deduplicating where possible,
    and provides a unified assessment.

    Args:
        crew_report: Crew results in workflow format (from crew_report_to_workflow_format)
        workflow_findings: Workflow security results

    Returns:
        Merged dict with combined findings and assessment.
    """
    # Handle None cases
    if crew_report is None and workflow_findings is None:
        return {"findings": [], "risk_score": 0, "merged": False}

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

    # Calculate merged risk score (weighted average)
    crew_score = crew_report.get("risk_score", 0)
    wf_score = workflow_findings.get("assessment", {}).get("risk_score", 0)
    # Give crew score higher weight (more comprehensive)
    merged_score = (crew_score * 0.7 + wf_score * 0.3) if wf_score else crew_score

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
        "risk_score": merged_score,
        "risk_level": _score_to_level(merged_score),
        "assessment": {
            "risk_score": merged_score,
            "risk_level": _score_to_level(merged_score),
            "severity_breakdown": merged_severity,
            "critical_findings": [f for f in merged_findings if f.get("severity") == "critical"],
            "high_findings": [f for f in merged_findings if f.get("severity") == "high"],
        },
        "crew_summary": crew_report.get("summary", ""),
        "agents_used": crew_report.get("agents_used", []),
    }


def _score_to_level(score: float) -> str:
    """Convert risk score to risk level string."""
    if score >= 75:
        return "critical"
    elif score >= 50:
        return "high"
    elif score >= 25:
        return "medium"
    elif score > 0:
        return "low"
    return "none"


def _map_category_to_owasp(category: str) -> str:
    """Map SecurityFinding category to OWASP category string."""
    mapping = {
        "injection": "A03:2021-Injection",
        "broken_authentication": "A07:2021-Identification and Authentication Failures",
        "sensitive_data_exposure": "A02:2021-Cryptographic Failures",
        "xml_external_entities": "A05:2021-Security Misconfiguration",
        "broken_access_control": "A01:2021-Broken Access Control",
        "security_misconfiguration": "A05:2021-Security Misconfiguration",
        "cross_site_scripting": "A03:2021-Injection",
        "insecure_deserialization": "A08:2021-Software and Data Integrity Failures",
        "vulnerable_components": "A06:2021-Vulnerable and Outdated Components",
        "insufficient_logging": "A09:2021-Security Logging and Monitoring Failures",
    }
    return mapping.get(category, "Other")


def _map_type_to_category(vuln_type: str) -> str:
    """Map workflow vulnerability type to crew category."""
    mapping = {
        "sql_injection": "injection",
        "xss": "cross_site_scripting",
        "command_injection": "injection",
        "path_traversal": "broken_access_control",
        "hardcoded_secret": "sensitive_data_exposure",
        "insecure_random": "security_misconfiguration",
    }
    return mapping.get(vuln_type, "other")
