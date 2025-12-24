"""
Secure Release Pipeline

A comprehensive security pipeline that composes multiple security workflows
for maximum coverage before release approval.

Orchestrates:
1. SecurityAuditCrew (optional, parallel) - 5-agent multi-agent security crew
2. SecurityAuditWorkflow - OWASP-focused vulnerability scanning
3. CodeReviewWorkflow - Security-aware code review (optional)
4. ReleasePreparationWorkflow - Pre-release quality gate

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from .base import WorkflowResult

logger = logging.getLogger(__name__)


@dataclass
class SecureReleaseResult:
    """Result from SecureReleasePipeline execution."""

    success: bool
    go_no_go: str  # "GO", "NO_GO", "CONDITIONAL"

    # Individual workflow results
    crew_report: dict | None = None
    security_audit: WorkflowResult | None = None
    code_review: WorkflowResult | None = None
    release_prep: WorkflowResult | None = None

    # Unified metrics
    combined_risk_score: float = 0.0
    total_findings: int = 0
    critical_count: int = 0
    high_count: int = 0

    # Cost tracking
    total_cost: float = 0.0
    total_duration_ms: int = 0

    # Recommendations
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    # Metadata
    mode: str = "full"
    crew_enabled: bool = False

    def to_dict(self) -> dict:
        """Convert result to dictionary."""
        return {
            "success": self.success,
            "go_no_go": self.go_no_go,
            "combined_risk_score": self.combined_risk_score,
            "total_findings": self.total_findings,
            "critical_count": self.critical_count,
            "high_count": self.high_count,
            "total_cost": self.total_cost,
            "total_duration_ms": self.total_duration_ms,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "recommendations": self.recommendations,
            "mode": self.mode,
            "crew_enabled": self.crew_enabled,
        }


class SecureReleasePipeline:
    """
    Comprehensive security pipeline for release preparation.

    This pipeline composes multiple security workflows to provide
    maximum coverage before release approval.

    Execution modes:
    - "full": Run all workflows (SecurityAuditCrew + all workflows)
    - "standard": Skip crew, run all workflows
    - "quick": Only SecurityAuditWorkflow + ReleasePreparation

    Usage:
        pipeline = SecureReleasePipeline(mode="full")
        result = await pipeline.execute(
            path="./src",
            diff="...",
            files_changed=[...]
        )

        if result.go_no_go == "GO":
            print("Ready for release!")
        else:
            for blocker in result.blockers:
                print(f"BLOCKER: {blocker}")
    """

    name = "secure-release"
    description = "Comprehensive security pipeline composing multiple workflows"

    def __init__(
        self,
        mode: str = "full",  # "full", "standard", "quick"
        use_crew: bool | None = None,  # Override mode's crew setting
        parallel_crew: bool = True,  # Run crew in parallel with first workflow
        crew_config: dict | None = None,
        **kwargs: Any,
    ):
        """
        Initialize secure release pipeline.

        Args:
            mode: Execution mode ("full", "standard", "quick")
            use_crew: Override crew setting (None uses mode default)
            parallel_crew: Run SecurityAuditCrew in parallel with first workflow
            crew_config: Configuration for SecurityAuditCrew
            **kwargs: Additional arguments passed to child workflows
        """
        self.mode = mode
        self.use_crew = use_crew if use_crew is not None else (mode == "full")
        self.parallel_crew = parallel_crew
        self.crew_config = crew_config or {}
        self.kwargs = kwargs

    async def execute(
        self,
        path: str = ".",
        diff: str = "",
        files_changed: list[str] | None = None,
        since: str = "1 week ago",
        **kwargs: Any,
    ) -> SecureReleaseResult:
        """
        Execute the secure release pipeline.

        Args:
            path: Path to codebase to analyze
            diff: Git diff for code review (optional)
            files_changed: List of changed files (optional)
            since: Period for changelog generation
            **kwargs: Additional arguments

        Returns:
            SecureReleaseResult with combined analysis
        """
        from .security_adapters import (
            _check_crew_available,
            _get_crew_audit,
            crew_report_to_workflow_format,
        )

        started_at = datetime.now()

        crew_report = None
        security_result = None
        code_review_result = None
        release_result = None

        total_cost = 0.0
        blockers: list[str] = []
        warnings: list[str] = []
        recommendations: list[str] = []

        try:
            # Step 1: SecurityAuditCrew (parallel or first)
            crew_task = None
            crew_enabled = self.use_crew and _check_crew_available()

            if crew_enabled:
                if self.parallel_crew:
                    # Start crew in parallel
                    crew_task = asyncio.create_task(_get_crew_audit(path, self.crew_config))
                else:
                    # Run crew first, then proceed
                    crew_report_obj = await _get_crew_audit(path, self.crew_config)
                    if crew_report_obj:
                        crew_report = crew_report_to_workflow_format(crew_report_obj)

            # Step 2: SecurityAuditWorkflow
            from .security_audit import SecurityAuditWorkflow

            security_workflow = SecurityAuditWorkflow(**self.kwargs)
            security_result = await security_workflow.execute(path=path)
            total_cost += security_result.cost_report.total_cost

            # Collect crew results if running in parallel
            if crew_task:
                try:
                    crew_report_obj = await asyncio.wait_for(crew_task, timeout=300.0)
                    if crew_report_obj:
                        crew_report = crew_report_to_workflow_format(crew_report_obj)
                except asyncio.TimeoutError:
                    logger.warning("SecurityAuditCrew timed out")
                    warnings.append("SecurityAuditCrew timed out - results not included")

            # Step 3: CodeReviewWorkflow (if not quick mode and diff provided)
            if self.mode != "quick" and diff:
                from .code_review import CodeReviewWorkflow

                code_workflow = CodeReviewWorkflow(**self.kwargs)

                # Pass crew findings as external audit if available
                code_input: dict = {
                    "diff": diff,
                    "files_changed": files_changed or [],
                }
                if crew_report:
                    code_input["external_audit_results"] = crew_report

                code_review_result = await code_workflow.execute(**code_input)
                total_cost += code_review_result.cost_report.total_cost

            # Step 4: ReleasePreparationWorkflow
            from .release_prep import ReleasePreparationWorkflow

            release_workflow = ReleasePreparationWorkflow(**self.kwargs)
            release_result = await release_workflow.execute(path=path, since=since)
            total_cost += release_result.cost_report.total_cost

            # Aggregate results
            combined_risk_score = self._calculate_combined_risk(
                crew_report, security_result, code_review_result, release_result
            )

            findings = self._aggregate_findings(crew_report, security_result, code_review_result)

            # Determine go/no-go
            go_no_go = self._determine_go_no_go(combined_risk_score, findings, release_result)

            blockers, warnings, recommendations = self._generate_recommendations(
                crew_report, security_result, code_review_result, release_result
            )

        except Exception as e:
            logger.error(f"Secure release pipeline failed: {e}")
            blockers.append(f"Pipeline failed: {str(e)}")
            go_no_go = "NO_GO"
            combined_risk_score = 100.0
            findings = {"critical": 0, "high": 0, "total": 0}

        completed_at = datetime.now()
        duration_ms = int((completed_at - started_at).total_seconds() * 1000)

        return SecureReleaseResult(
            success=go_no_go != "NO_GO",
            go_no_go=go_no_go,
            crew_report=crew_report,
            security_audit=security_result,
            code_review=code_review_result,
            release_prep=release_result,
            combined_risk_score=combined_risk_score,
            total_findings=findings.get("total", 0),
            critical_count=findings.get("critical", 0),
            high_count=findings.get("high", 0),
            total_cost=total_cost,
            total_duration_ms=duration_ms,
            blockers=blockers,
            warnings=warnings,
            recommendations=recommendations,
            mode=self.mode,
            crew_enabled=crew_report is not None,
        )

    def _calculate_combined_risk(
        self,
        crew_report: dict | None,
        security_result: WorkflowResult | None,
        code_review_result: WorkflowResult | None,
        release_result: WorkflowResult | None,
    ) -> float:
        """Calculate combined risk score from all sources."""
        scores = []
        weights = []

        if crew_report:
            scores.append(crew_report.get("risk_score", 0))
            weights.append(1.5)  # Crew gets higher weight

        if security_result and security_result.final_output:
            assessment = security_result.final_output.get("assessment", {})
            scores.append(assessment.get("risk_score", 0))
            weights.append(1.0)

        if code_review_result and code_review_result.final_output:
            security_score = code_review_result.final_output.get("security_score", 90)
            # Convert to risk (100 - security_score)
            scores.append(100 - security_score)
            weights.append(0.8)

        if not scores:
            return 0.0

        weighted_sum = sum(s * w for s, w in zip(scores, weights, strict=False))
        return float(min(100.0, weighted_sum / sum(weights)))

    def _aggregate_findings(
        self,
        crew_report: dict | None,
        security_result: WorkflowResult | None,
        code_review_result: WorkflowResult | None,
    ) -> dict:
        """Aggregate findings from all sources."""
        critical = 0
        high = 0
        total = 0

        if crew_report:
            assessment = crew_report.get("assessment", {})
            critical += len(assessment.get("critical_findings", []))
            high += len(assessment.get("high_findings", []))
            total += crew_report.get("finding_count", 0)

        if security_result and security_result.final_output:
            assessment = security_result.final_output.get("assessment", {})
            severity = assessment.get("severity_breakdown", {})
            critical = max(critical, severity.get("critical", 0))
            high = max(high, severity.get("high", 0))
            total = max(
                total,
                sum(severity.values()) if severity else 0,
            )

        if code_review_result and code_review_result.final_output:
            if code_review_result.final_output.get("has_critical_issues"):
                critical = max(critical, 1)

        return {"critical": critical, "high": high, "total": total}

    def _determine_go_no_go(
        self,
        risk_score: float,
        findings: dict,
        release_result: WorkflowResult | None,
    ) -> str:
        """Determine go/no-go decision."""
        # Critical findings = immediate NO_GO
        if findings.get("critical", 0) > 0:
            return "NO_GO"

        # Very high risk = NO_GO
        if risk_score >= 75:
            return "NO_GO"

        # High findings or elevated risk = CONDITIONAL
        if findings.get("high", 0) > 3 or risk_score >= 50:
            return "CONDITIONAL"

        # Release workflow not approved = CONDITIONAL
        if release_result and release_result.final_output:
            if not release_result.final_output.get("approved", True):
                return "CONDITIONAL"

        return "GO"

    def _generate_recommendations(
        self,
        crew_report: dict | None,
        security_result: WorkflowResult | None,
        code_review_result: WorkflowResult | None,
        release_result: WorkflowResult | None,
    ) -> tuple[list[str], list[str], list[str]]:
        """Generate blockers, warnings, and recommendations."""
        blockers = []
        warnings = []
        recommendations = []

        # Crew findings
        if crew_report:
            critical = crew_report.get("assessment", {}).get("critical_findings", [])
            for f in critical:
                blockers.append(f"Critical: {f.get('title', 'Unknown issue')}")

            high = crew_report.get("assessment", {}).get("high_findings", [])
            for f in high[:3]:  # Top 3
                warnings.append(f"High: {f.get('title', 'Unknown issue')}")

        # Security audit findings
        if security_result and security_result.final_output:
            assessment = security_result.final_output.get("assessment", {})
            if assessment.get("risk_level") == "critical":
                blockers.append("Security audit identified critical risk level")
            elif assessment.get("risk_level") == "high":
                warnings.append("Security audit identified high risk level")

        # Code review verdict
        if code_review_result and code_review_result.final_output:
            verdict = code_review_result.final_output.get("verdict", "")
            if verdict == "reject":
                blockers.append("Code review: Changes rejected")
            elif verdict == "request_changes":
                warnings.append("Code review: Changes requested")

        # Release prep blockers
        if release_result and release_result.final_output:
            for b in release_result.final_output.get("blockers", []):
                blockers.append(f"Release: {b}")
            for w in release_result.final_output.get("warnings", []):
                warnings.append(f"Release: {w}")

        # General recommendations
        if not blockers and not warnings:
            recommendations.append("All checks passed - ready for release")
        elif blockers:
            recommendations.append("Address all blockers before release")
            recommendations.append("Consider running security audit on fixes")
        elif warnings:
            recommendations.append("Review warnings before release")
            recommendations.append("Document accepted risks if proceeding")

        return blockers, warnings, recommendations

    @classmethod
    def for_pr_review(cls, files_changed: int = 0) -> "SecureReleasePipeline":
        """Create pipeline optimized for PR review."""
        return cls(
            mode="standard" if files_changed < 10 else "full",
            parallel_crew=True,
        )

    @classmethod
    def for_release(cls) -> "SecureReleasePipeline":
        """Create pipeline for release preparation."""
        return cls(
            mode="full",
            crew_config={"scan_depth": "thorough"},
        )

    @classmethod
    def for_quick_check(cls) -> "SecureReleasePipeline":
        """Create pipeline for quick security check."""
        return cls(
            mode="quick",
            use_crew=False,
        )
