"""
Code Review Pipeline

A composite workflow that combines CodeReviewCrew with CodeReviewWorkflow
for comprehensive code analysis.

Modes:
- full: Run CodeReviewCrew (5 agents) + CodeReviewWorkflow
- standard: Run CodeReviewWorkflow only
- quick: Run classify + scan stages only (skip architect review)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


@dataclass
class CodeReviewPipelineResult:
    """Result from CodeReviewPipeline execution."""

    success: bool
    verdict: str  # "approve", "approve_with_suggestions", "request_changes", "reject"
    quality_score: float
    crew_report: dict | None
    workflow_result: Any  # WorkflowResult or None
    combined_findings: list[dict]
    critical_count: int
    high_count: int
    medium_count: int
    agents_used: list[str]
    recommendations: list[str]
    blockers: list[str]
    mode: str
    duration_seconds: float
    cost: float
    metadata: dict = field(default_factory=dict)


class CodeReviewPipeline:
    """
    Composite workflow combining CodeReviewCrew with CodeReviewWorkflow.

    Provides multiple modes for different use cases:
    - full: Most comprehensive (crew + workflow)
    - standard: Balanced (workflow only)
    - quick: Fast check (minimal stages)

    Usage:
        pipeline = CodeReviewPipeline(mode="full")
        result = await pipeline.execute(
            diff="...",
            files_changed=["src/main.py"],
        )

        # Or use factory methods:
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=12)
        pipeline = CodeReviewPipeline.for_quick_check()
    """

    def __init__(
        self,
        provider: str = "anthropic",
        mode: str = "full",
        parallel_crew: bool = True,
        crew_config: dict | None = None,
        **kwargs,
    ):
        """
        Initialize the pipeline.

        Args:
            provider: LLM provider to use (anthropic, openai, etc.)
            mode: Review mode ("full", "standard", "quick")
            parallel_crew: Run crew in parallel with workflow (full mode only)
            crew_config: Configuration for CodeReviewCrew
            **kwargs: Additional arguments (for CLI compatibility)
        """
        self.provider = provider
        self.mode = mode
        self.parallel_crew = parallel_crew
        # Inject provider into crew config
        self.crew_config = {"provider": provider, **(crew_config or {})}
        self.crew_enabled = mode == "full"

    @classmethod
    def for_pr_review(cls, files_changed: int = 0) -> "CodeReviewPipeline":
        """
        Factory for PR review - uses crew for complex PRs.

        Args:
            files_changed: Number of files changed in PR

        Returns:
            Pipeline configured for PR review complexity
        """
        # Use full mode for complex PRs (5+ files)
        mode = "full" if files_changed > 5 else "standard"
        return cls(mode=mode, parallel_crew=True)

    @classmethod
    def for_quick_check(cls) -> "CodeReviewPipeline":
        """Quick code check without crew - minimal analysis."""
        return cls(mode="quick", parallel_crew=False)

    @classmethod
    def for_full_review(cls) -> "CodeReviewPipeline":
        """Full review with all agents and workflow stages."""
        return cls(mode="full", parallel_crew=True)

    async def execute(
        self,
        diff: str = "",
        files_changed: list[str] | None = None,
        target: str = "",
        context: dict | None = None,
    ) -> CodeReviewPipelineResult:
        """
        Execute the code review pipeline.

        Args:
            diff: Code diff to review
            files_changed: List of changed files
            target: Target file/folder path (alternative to diff)
            context: Additional context for review

        Returns:
            CodeReviewPipelineResult with combined analysis
        """
        start_time = time.time()
        files_changed = files_changed or []
        context = context or {}

        # Initialize result collectors
        crew_report: dict | None = None
        workflow_result: Any = None  # WorkflowResult or None
        all_findings: list[dict] = []
        recommendations: list[str] = []
        blockers: list[str] = []
        agents_used: list[str] = []
        total_cost = 0.0

        # Get code to review
        code_to_review = diff or target

        try:
            if self.mode == "full":
                # Run crew and workflow
                crew_report, workflow_result = await self._run_full_mode(
                    code_to_review, files_changed, context
                )
            elif self.mode == "standard":
                # Run workflow only
                workflow_result = await self._run_standard_mode(
                    code_to_review, files_changed, context
                )
            else:  # quick
                # Run minimal workflow
                workflow_result = await self._run_quick_mode(code_to_review, files_changed, context)

            # Aggregate findings
            if crew_report:
                crew_findings = crew_report.get("findings", [])
                all_findings.extend(crew_findings)
                agents_used = crew_report.get("agents_used", [])

                # Extract crew recommendations
                for finding in crew_findings:
                    if finding.get("suggestion"):
                        recommendations.append(finding["suggestion"])

            if workflow_result:
                # Get workflow findings from various stages
                # WorkflowResult is a dataclass, access attributes directly
                wf_output = workflow_result.final_output or {}
                scan_findings = (
                    wf_output.get("security_findings", []) if isinstance(wf_output, dict) else []
                )
                all_findings.extend(scan_findings)

                # Get cost from workflow
                cost_report = workflow_result.cost_report
                if hasattr(cost_report, "total_cost"):
                    total_cost = cost_report.total_cost

            # Deduplicate findings by (file, line, type)
            all_findings = self._deduplicate_findings(all_findings)

            # Count by severity
            critical_count = len([f for f in all_findings if f.get("severity") == "critical"])
            high_count = len([f for f in all_findings if f.get("severity") == "high"])
            medium_count = len([f for f in all_findings if f.get("severity") == "medium"])

            # Determine blockers
            if critical_count > 0:
                blockers.append(f"{critical_count} critical issue(s) found")
            if high_count > 3:
                blockers.append(f"{high_count} high severity issues (threshold: 3)")

            # Calculate combined scores
            quality_score = self._calculate_quality_score(
                crew_report, workflow_result, all_findings
            )

            # Determine verdict
            verdict = self._determine_verdict(crew_report, workflow_result, quality_score, blockers)

            duration = time.time() - start_time

            result = CodeReviewPipelineResult(
                success=True,
                verdict=verdict,
                quality_score=quality_score,
                crew_report=crew_report,
                workflow_result=workflow_result,
                combined_findings=all_findings,
                critical_count=critical_count,
                high_count=high_count,
                medium_count=medium_count,
                agents_used=agents_used,
                recommendations=recommendations[:10],  # Top 10
                blockers=blockers,
                mode=self.mode,
                duration_seconds=duration,
                cost=total_cost,
                metadata={
                    "files_reviewed": len(files_changed),
                    "total_findings": len(all_findings),
                    "crew_enabled": self.crew_enabled,
                    "parallel_crew": self.parallel_crew,
                },
            )

            # Add formatted report for human readability
            result.metadata["formatted_report"] = format_code_review_pipeline_report(result)
            return result

        except Exception as e:
            logger.error(f"CodeReviewPipeline failed: {e}")
            duration = time.time() - start_time
            return CodeReviewPipelineResult(
                success=False,
                verdict="reject",
                quality_score=0.0,
                crew_report=crew_report,
                workflow_result=workflow_result,
                combined_findings=all_findings,
                critical_count=0,
                high_count=0,
                medium_count=0,
                agents_used=agents_used,
                recommendations=[],
                blockers=[f"Pipeline error: {str(e)}"],
                mode=self.mode,
                duration_seconds=duration,
                cost=total_cost,
                metadata={"error": str(e)},
            )

    async def _run_full_mode(
        self,
        code_to_review: str,
        files_changed: list[str],
        context: dict,
    ) -> tuple[dict | None, Any]:  # Second element is WorkflowResult or None
        """Run full mode with crew and workflow."""
        from .code_review import CodeReviewWorkflow
        from .code_review_adapters import (
            _check_crew_available,
            _get_crew_review,
            crew_report_to_workflow_format,
        )

        crew_report: dict | None = None
        workflow_result: Any = None  # WorkflowResult or None

        # Check if crew is available
        crew_available = _check_crew_available()

        if crew_available and self.parallel_crew:
            # Run crew and workflow in parallel
            crew_task = asyncio.create_task(
                _get_crew_review(
                    diff=code_to_review,
                    files_changed=files_changed,
                    config=self.crew_config,
                )
            )

            # Run workflow (without crew - we'll merge results)
            workflow = CodeReviewWorkflow(use_crew=False)
            workflow_task = asyncio.create_task(
                workflow.execute(
                    diff=code_to_review,
                    files_changed=files_changed,
                    **context,
                )
            )

            # Wait for both
            crew_report_obj, workflow_result = await asyncio.gather(
                crew_task, workflow_task, return_exceptions=True
            )

            # Handle crew result
            if isinstance(crew_report_obj, Exception):
                logger.warning(f"Crew review failed: {crew_report_obj}")
            elif crew_report_obj:
                crew_report = crew_report_to_workflow_format(crew_report_obj)

            # Handle workflow result
            if isinstance(workflow_result, Exception):
                logger.warning(f"Workflow failed: {workflow_result}")
                workflow_result = None

        elif crew_available:
            # Run sequentially
            crew_report_obj = await _get_crew_review(
                diff=code_to_review,
                files_changed=files_changed,
                config=self.crew_config,
            )
            if crew_report_obj:
                crew_report = crew_report_to_workflow_format(crew_report_obj)

            workflow = CodeReviewWorkflow(use_crew=False)
            workflow_result = await workflow.execute(
                diff=code_to_review,
                files_changed=files_changed,
                **context,
            )
        else:
            # Crew not available, run workflow only
            logger.info("CodeReviewCrew not available, running workflow only")
            workflow = CodeReviewWorkflow(use_crew=False)
            workflow_result = await workflow.execute(
                diff=code_to_review,
                files_changed=files_changed,
                **context,
            )

        return crew_report, workflow_result

    async def _run_standard_mode(
        self,
        code_to_review: str,
        files_changed: list[str],
        context: dict,
    ) -> Any:  # Returns WorkflowResult
        """Run standard mode with workflow only."""
        from .code_review import CodeReviewWorkflow

        workflow = CodeReviewWorkflow(use_crew=False)
        result = await workflow.execute(
            diff=code_to_review,
            files_changed=files_changed,
            **context,
        )
        return result

    async def _run_quick_mode(
        self,
        code_to_review: str,
        files_changed: list[str],
        context: dict,
    ) -> Any:  # Returns WorkflowResult
        """Run quick mode with minimal stages."""
        from .code_review import CodeReviewWorkflow

        # Use workflow but it will skip architect_review for simple changes
        workflow = CodeReviewWorkflow(
            file_threshold=1000,  # High threshold = skip architect review
            use_crew=False,
        )
        result = await workflow.execute(
            diff=code_to_review,
            files_changed=files_changed,
            is_core_module=False,
            **context,
        )
        return result

    def _deduplicate_findings(self, findings: list[dict]) -> list[dict]:
        """Deduplicate findings by (file, line, type)."""
        seen = set()
        unique = []
        for f in findings:
            key = (f.get("file"), f.get("line"), f.get("type"))
            if key not in seen:
                seen.add(key)
                unique.append(f)
        return unique

    def _calculate_quality_score(
        self,
        crew_report: dict | None,
        workflow_result: Any,  # WorkflowResult or None
        findings: list[dict],
    ) -> float:
        """Calculate combined quality score."""
        scores = []
        weights = []

        # Crew quality score (if available)
        if crew_report:
            crew_score = crew_report.get("quality_score", 100)
            scores.append(crew_score)
            weights.append(1.5)  # Crew gets higher weight

        # Workflow security score (if available)
        if workflow_result:
            wf_output = workflow_result.final_output or {}
            security_score = (
                wf_output.get("security_score", 90) if isinstance(wf_output, dict) else 90
            )
            scores.append(security_score)
            weights.append(1.0)

        # Calculate weighted average
        if scores:
            weighted_sum = sum(s * w for s, w in zip(scores, weights, strict=False))
            quality_score = weighted_sum / sum(weights)
        else:
            # Fallback: deduct based on findings
            quality_score = 100.0
            for f in findings:
                sev = f.get("severity", "medium")
                if sev == "critical":
                    quality_score -= 25
                elif sev == "high":
                    quality_score -= 15
                elif sev == "medium":
                    quality_score -= 5
                elif sev == "low":
                    quality_score -= 2

        return max(0.0, min(100.0, quality_score))

    def _determine_verdict(
        self,
        crew_report: dict | None,
        workflow_result: Any,  # WorkflowResult or None
        quality_score: float,
        blockers: list[str],
    ) -> str:
        """Determine final verdict based on all inputs."""
        # Start with most severe verdict
        verdict_priority = ["reject", "request_changes", "approve_with_suggestions", "approve"]

        verdicts = []

        # Crew verdict
        if crew_report:
            crew_verdict = crew_report.get("verdict", "approve")
            verdicts.append(crew_verdict)

        # Workflow verdict (from architect review)
        if workflow_result:
            wf_output = workflow_result.final_output or {}
            wf_verdict = (
                wf_output.get("verdict", "approve") if isinstance(wf_output, dict) else "approve"
            )
            verdicts.append(wf_verdict)

        # Score-based verdict
        if quality_score < 50:
            verdicts.append("reject")
        elif quality_score < 70:
            verdicts.append("request_changes")
        elif quality_score < 90:
            verdicts.append("approve_with_suggestions")
        else:
            verdicts.append("approve")

        # Blocker-based verdict
        if blockers:
            verdicts.append("request_changes")

        # Take most severe
        for v in verdict_priority:
            if v in verdicts:
                return v

        return "approve"


# CLI entry point
def main():
    """Run CodeReviewPipeline from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Code Review Pipeline")
    parser.add_argument("--diff", "-d", help="Code diff to review")
    parser.add_argument("--file", "-f", help="File to review")
    parser.add_argument(
        "--mode",
        "-m",
        default="full",
        choices=["full", "standard", "quick"],
        help="Review mode",
    )
    parser.add_argument(
        "--parallel/--sequential",
        dest="parallel",
        default=True,
        help="Run crew in parallel",
    )

    args = parser.parse_args()

    async def run():
        pipeline = CodeReviewPipeline(mode=args.mode, parallel_crew=args.parallel)

        diff = args.diff or ""
        if args.file:
            try:
                with open(args.file) as f:
                    diff = f.read()
            except FileNotFoundError:
                print(f"File not found: {args.file}")
                return

        result = await pipeline.execute(diff=diff)

        print("\n" + "=" * 60)
        print("CODE REVIEW PIPELINE RESULTS")
        print("=" * 60)
        print(f"Mode: {result.mode}")
        print(f"Verdict: {result.verdict.upper()}")
        print(f"Quality Score: {result.quality_score:.1f}/100")
        print(f"Duration: {result.duration_seconds:.2f}s")
        print(f"Cost: ${result.cost:.4f}")

        if result.agents_used:
            print(f"\nAgents Used: {', '.join(result.agents_used)}")

        print(f"\nFindings: {len(result.combined_findings)} total")
        print(f"  Critical: {result.critical_count}")
        print(f"  High: {result.high_count}")
        print(f"  Medium: {result.medium_count}")

        if result.blockers:
            print("\nBlockers:")
            for b in result.blockers:
                print(f"  - {b}")

        if result.recommendations[:5]:
            print("\nTop Recommendations:")
            for r in result.recommendations[:5]:
                print(f"  - {r[:100]}...")

    asyncio.run(run())


def format_code_review_pipeline_report(result: CodeReviewPipelineResult) -> str:
    """
    Format code review pipeline result as a human-readable report.

    Args:
        result: The CodeReviewPipelineResult dataclass

    Returns:
        Formatted report string
    """
    lines = []

    # Header with verdict
    verdict_emoji = {
        "approve": "✅",
        "approve_with_suggestions": "🟡",
        "request_changes": "🟠",
        "reject": "🔴",
    }
    emoji = verdict_emoji.get(result.verdict, "⚪")

    lines.append("=" * 60)
    lines.append("CODE REVIEW REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Verdict banner
    lines.append("-" * 60)
    lines.append(f"{emoji} VERDICT: {result.verdict.upper().replace('_', ' ')}")
    lines.append("-" * 60)
    lines.append(f"Mode: {result.mode}")
    lines.append("")

    # Quality score with visual bar
    score = result.quality_score
    bar = "█" * int(score / 10) + "░" * (10 - int(score / 10))
    quality_label = (
        "EXCELLENT"
        if score >= 90
        else "GOOD" if score >= 70 else "NEEDS WORK" if score >= 50 else "POOR"
    )
    lines.append("-" * 60)
    lines.append("QUALITY SCORE")
    lines.append("-" * 60)
    lines.append(f"[{bar}] {score:.0f}/100 ({quality_label})")
    lines.append("")

    # Crew summary (if available)
    if result.crew_report and result.crew_report.get("summary"):
        lines.append("-" * 60)
        lines.append("SUMMARY")
        lines.append("-" * 60)
        summary = result.crew_report["summary"]
        # Word wrap the summary
        words = summary.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 58:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")

    # Findings summary
    total_findings = len(result.combined_findings)
    lines.append("-" * 60)
    lines.append("FINDINGS")
    lines.append("-" * 60)

    # Show files reviewed from metadata
    files_reviewed = result.metadata.get("files_reviewed", 0)
    if files_reviewed > 0:
        lines.append(f"Files Reviewed: {files_reviewed}")

    if total_findings > 0 or result.critical_count > 0 or result.high_count > 0:
        lines.append(f"Issues Found: {total_findings}")
        lines.append(f"  🔴 Critical: {result.critical_count}")
        lines.append(f"  🟠 High: {result.high_count}")
        lines.append(f"  🟡 Medium: {result.medium_count}")
        lines.append("")

        # Show top critical/high findings
        if result.combined_findings:
            critical_high = [
                f for f in result.combined_findings if f.get("severity") in ("critical", "high")
            ][:5]
            if critical_high:
                lines.append("Top Issues:")
                for i, finding in enumerate(critical_high, 1):
                    severity = finding.get("severity", "unknown")
                    title = finding.get(
                        "title", finding.get("message", finding.get("description", "Issue found"))
                    )
                    emoji_f = "🔴" if severity == "critical" else "🟠"
                    if len(str(title)) > 50:
                        title = str(title)[:47] + "..."
                    lines.append(f"  {emoji_f} {i}. {title}")
                lines.append("")
    else:
        lines.append("✅ No issues found!")
        lines.append("")

    # Blockers
    if result.blockers:
        lines.append("-" * 60)
        lines.append("🚫 BLOCKERS")
        lines.append("-" * 60)
        for blocker in result.blockers:
            lines.append(f"  • {blocker}")
        lines.append("")

    # Recommendations
    if result.recommendations:
        lines.append("-" * 60)
        lines.append("RECOMMENDATIONS")
        lines.append("-" * 60)
        for i, rec in enumerate(result.recommendations[:5], 1):
            rec_str = str(rec)
            if len(rec_str) > 55:
                rec_str = rec_str[:52] + "..."
            lines.append(f"  {i}. {rec_str}")
        if len(result.recommendations) > 5:
            lines.append(f"  ... and {len(result.recommendations) - 5} more")
        lines.append("")

    # Agents used
    if result.agents_used:
        lines.append("-" * 60)
        lines.append("AGENTS USED")
        lines.append("-" * 60)
        lines.append(f"  {', '.join(result.agents_used)}")
        lines.append("")

    # Footer
    lines.append("=" * 60)
    lines.append(f"Review completed in {result.duration_seconds:.1f}s | Cost: ${result.cost:.4f}")
    lines.append("=" * 60)

    return "\n".join(lines)


if __name__ == "__main__":
    main()
