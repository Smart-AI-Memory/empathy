"""Orchestrated Release Preparation Workflow

Uses the meta-orchestration system to coordinate multiple validation agents
in parallel for comprehensive release readiness assessment.

This is the first production use case of the meta-orchestration system,
demonstrating parallel agent composition with quality gates.

Architecture:
    - MetaOrchestrator analyzes task and selects agents
    - ParallelStrategy runs validation agents simultaneously
    - Quality gates enforce release standards
    - Results aggregated into consolidated report

Agents:
    - Security Auditor: Vulnerability scan and compliance check
    - Test Coverage Analyzer: Gap analysis and coverage validation
    - Code Quality Reviewer: Code review and best practices
    - Documentation Writer: Documentation completeness check

Quality Gates:
    - No critical security issues
    - Test coverage ≥ 80%
    - Code quality score ≥ 7
    - Documentation coverage ≥ 100%

Example:
    >>> workflow = OrchestCreatedReleasePrepWorkflow()
    >>> result = await workflow.execute(path=".")
    >>> print(result.approved)
    True

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..orchestration.agent_templates import AgentTemplate, get_template
from ..orchestration.execution_strategies import ParallelStrategy, StrategyResult
from ..orchestration.meta_orchestrator import MetaOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class QualityGate:
    """Quality gate threshold for release readiness.

    Attributes:
        name: Gate identifier (e.g., "security", "coverage")
        threshold: Minimum acceptable value
        actual: Actual measured value
        passed: Whether gate passed
        critical: Whether failure blocks release
        message: Human-readable status message
    """

    name: str
    threshold: float
    actual: float = 0.0
    passed: bool = False
    critical: bool = True
    message: str = ""

    def __post_init__(self):
        """Validate and compute pass/fail status."""
        if not self.name:
            raise ValueError("name must be non-empty")
        if self.threshold < 0:
            raise ValueError("threshold must be non-negative")

        # Note: passed field is computed externally based on gate semantics
        # (some gates use >=, others use <=)

        # Generate message if not provided
        if not self.message:
            status = "✅ PASS" if self.passed else "❌ FAIL"
            self.message = (
                f"{self.name}: {status} "
                f"(actual: {self.actual:.1f}, threshold: {self.threshold:.1f})"
            )


@dataclass
class ReleaseReadinessReport:
    """Consolidated release readiness assessment.

    Attributes:
        approved: Overall release approval status
        confidence: Confidence level ("high", "medium", "low")
        quality_gates: List of quality gate results
        agent_results: Individual agent outputs
        blockers: Critical issues blocking release
        warnings: Non-critical issues to address
        summary: Executive summary of readiness
        timestamp: Report generation time
        total_duration: Total execution time in seconds
    """

    approved: bool
    confidence: str
    quality_gates: list[QualityGate] = field(default_factory=list)
    agent_results: dict[str, dict] = field(default_factory=dict)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    total_duration: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary format.

        Returns:
            Dictionary representation suitable for JSON serialization
        """
        return {
            "approved": self.approved,
            "confidence": self.confidence,
            "quality_gates": [
                {
                    "name": gate.name,
                    "threshold": gate.threshold,
                    "actual": gate.actual,
                    "passed": gate.passed,
                    "critical": gate.critical,
                    "message": gate.message,
                }
                for gate in self.quality_gates
            ],
            "agent_results": self.agent_results,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "summary": self.summary,
            "timestamp": self.timestamp,
            "total_duration": self.total_duration,
        }

    def format_console_output(self) -> str:
        """Format report for console display.

        Returns:
            Human-readable formatted report
        """
        lines = []

        # Header
        lines.append("=" * 70)
        lines.append("RELEASE READINESS REPORT (Meta-Orchestrated)")
        lines.append("=" * 70)
        lines.append("")

        # Status
        status_icon = "✅" if self.approved else "❌"
        lines.append(
            f"Status: {status_icon} {'READY FOR RELEASE' if self.approved else 'NOT READY'}"
        )
        lines.append(f"Confidence: {self.confidence.upper()}")
        lines.append(f"Generated: {self.timestamp}")
        lines.append(f"Duration: {self.total_duration:.2f}s")
        lines.append("")

        # Quality Gates
        lines.append("-" * 70)
        lines.append("QUALITY GATES")
        lines.append("-" * 70)
        for gate in self.quality_gates:
            icon = "✅" if gate.passed else ("🔴" if gate.critical else "⚠️")
            lines.append(f"{icon} {gate.message}")
        lines.append("")

        # Blockers
        if self.blockers:
            lines.append("-" * 70)
            lines.append("🚫 RELEASE BLOCKERS")
            lines.append("-" * 70)
            for blocker in self.blockers:
                lines.append(f"  • {blocker}")
            lines.append("")

        # Warnings
        if self.warnings:
            lines.append("-" * 70)
            lines.append("⚠️  WARNINGS")
            lines.append("-" * 70)
            for warning in self.warnings:
                lines.append(f"  • {warning}")
            lines.append("")

        # Summary
        if self.summary:
            lines.append("-" * 70)
            lines.append("EXECUTIVE SUMMARY")
            lines.append("-" * 70)
            lines.append(self.summary)
            lines.append("")

        # Agent Results Summary
        lines.append("-" * 70)
        lines.append(f"AGENTS EXECUTED ({len(self.agent_results)})")
        lines.append("-" * 70)
        for agent_id, result in self.agent_results.items():
            success = result.get("success", False)
            icon = "✅" if success else "❌"
            duration = result.get("duration", 0.0)
            lines.append(f"{icon} {agent_id}: {duration:.2f}s")
        lines.append("")

        lines.append("=" * 70)

        return "\n".join(lines)


class OrchestratedReleasePrepWorkflow:
    """Release preparation workflow using meta-orchestration.

    This workflow demonstrates the meta-orchestration system's capabilities
    by coordinating multiple validation agents in parallel to assess release
    readiness.

    The workflow:
    1. Uses MetaOrchestrator to analyze task and select agents
    2. Executes agents in parallel using ParallelStrategy
    3. Aggregates results and enforces quality gates
    4. Produces consolidated release readiness report

    Quality Gates:
        - no_critical_security_issues: No critical vulnerabilities
        - min_test_coverage: Test coverage ≥ 80%
        - min_code_quality: Quality score ≥ 7
        - complete_documentation: All public APIs documented

    Example:
        >>> workflow = OrchestratedReleasePrepWorkflow()
        >>> report = await workflow.execute(path=".")
        >>> if report.approved:
        ...     print("Ready for release!")
    """

    # Default quality gate thresholds
    DEFAULT_QUALITY_GATES = {
        "min_coverage": 80.0,
        "min_quality_score": 7.0,
        "max_critical_issues": 0.0,
        "min_doc_coverage": 100.0,
    }

    def __init__(
        self,
        quality_gates: dict[str, float] | None = None,
        agent_ids: list[str] | None = None,
    ):
        """Initialize orchestrated release prep workflow.

        Args:
            quality_gates: Custom quality gate thresholds
            agent_ids: Specific agent IDs to use (defaults to domain defaults)

        Raises:
            ValueError: If quality gates are invalid
        """
        self.quality_gates = {**self.DEFAULT_QUALITY_GATES}
        if quality_gates:
            self.quality_gates.update(quality_gates)

        # Validate quality gates
        for name, threshold in self.quality_gates.items():
            if not isinstance(threshold, int | float):
                raise ValueError(f"Quality gate '{name}' must be numeric")
            if threshold < 0:
                raise ValueError(f"Quality gate '{name}' must be non-negative")

        self.orchestrator = MetaOrchestrator()
        self.agent_ids = agent_ids

        logger.info(f"OrchestratedReleasePrepWorkflow initialized with gates: {self.quality_gates}")

    async def execute(
        self, path: str = ".", context: dict[str, Any] | None = None
    ) -> ReleaseReadinessReport:
        """Execute release preparation workflow.

        Args:
            path: Path to codebase to analyze (default: ".")
            context: Additional context for agents

        Returns:
            ReleaseReadinessReport with consolidated results

        Raises:
            ValueError: If path is invalid
        """
        if not path or not isinstance(path, str):
            raise ValueError("path must be a non-empty string")

        logger.info(f"Starting orchestrated release prep for: {path}")
        start_time = asyncio.get_event_loop().time()

        # Prepare context
        full_context = {
            "path": path,
            "quality_gates": self.quality_gates,
            **(context or {}),
        }

        # Step 1: Analyze task and compose agents
        task = (
            "Prepare for release: validate security, test coverage, code quality, and documentation"
        )
        execution_plan = self.orchestrator.analyze_and_compose(task, full_context)

        logger.info(
            f"Execution plan: {len(execution_plan.agents)} agents, "
            f"strategy={execution_plan.strategy.value}"
        )

        # Override agents if specific IDs provided
        if self.agent_ids:
            agents = []
            for agent_id in self.agent_ids:
                template = get_template(agent_id)
                if template:
                    agents.append(template)
                else:
                    logger.warning(f"Agent template not found: {agent_id}")

            if not agents:
                raise ValueError(f"No valid agents found from: {self.agent_ids}")

            execution_plan.agents = agents

        # Step 2: Execute agents in parallel
        strategy = ParallelStrategy()
        strategy_result = await strategy.execute(execution_plan.agents, full_context)

        # Step 3: Process results and evaluate quality gates
        report = await self._create_report(strategy_result, execution_plan.agents, full_context)

        # Set duration
        end_time = asyncio.get_event_loop().time()
        report.total_duration = end_time - start_time

        logger.info(
            f"Release prep completed: approved={report.approved}, "
            f"duration={report.total_duration:.2f}s"
        )

        return report

    async def _create_report(
        self,
        strategy_result: StrategyResult,
        agents: list[AgentTemplate],
        context: dict[str, Any],
    ) -> ReleaseReadinessReport:
        """Create consolidated release readiness report.

        Args:
            strategy_result: Results from parallel execution
            agents: Agents that were executed
            context: Execution context

        Returns:
            ReleaseReadinessReport with all findings
        """
        # Extract agent results
        agent_results: dict[str, dict] = {}
        for result in strategy_result.outputs:
            agent_results[result.agent_id] = {
                "success": result.success,
                "output": result.output,
                "confidence": result.confidence,
                "duration": result.duration_seconds,
                "error": result.error,
            }

        # Evaluate quality gates
        quality_gates = self._evaluate_quality_gates(agent_results)

        # Identify blockers and warnings
        blockers, warnings = self._identify_issues(quality_gates, agent_results)

        # Determine approval
        critical_failures = [g for g in quality_gates if g.critical and not g.passed]
        approved = len(critical_failures) == 0 and len(blockers) == 0

        # Determine confidence
        if approved and len(warnings) == 0:
            confidence = "high"
        elif approved:
            confidence = "medium"
        else:
            confidence = "low"

        # Generate summary
        summary = self._generate_summary(approved, quality_gates, agent_results)

        return ReleaseReadinessReport(
            approved=approved,
            confidence=confidence,
            quality_gates=quality_gates,
            agent_results=agent_results,
            blockers=blockers,
            warnings=warnings,
            summary=summary,
            total_duration=strategy_result.total_duration,
        )

    def _evaluate_quality_gates(self, agent_results: dict[str, dict]) -> list[QualityGate]:
        """Evaluate all quality gates based on agent results.

        Args:
            agent_results: Results from all agents

        Returns:
            List of QualityGate results
        """
        gates = []

        # Security gate: no critical issues
        security_result = agent_results.get("security_auditor", {}).get("output", {})
        critical_issues = security_result.get("critical_issues", 0)

        gates.append(
            QualityGate(
                name="Security",
                threshold=self.quality_gates["max_critical_issues"],
                actual=float(critical_issues),
                critical=True,
                passed=critical_issues <= self.quality_gates["max_critical_issues"],
            )
        )

        # Coverage gate: minimum test coverage
        coverage_result = agent_results.get("test_coverage_analyzer", {}).get("output", {})
        coverage_percent = coverage_result.get("coverage_percent", 0.0)

        gates.append(
            QualityGate(
                name="Test Coverage",
                threshold=self.quality_gates["min_coverage"],
                actual=coverage_percent,
                passed=coverage_percent >= self.quality_gates["min_coverage"],
                critical=True,
            )
        )

        # Quality gate: minimum code quality score
        quality_result = agent_results.get("code_reviewer", {}).get("output", {})
        quality_score = quality_result.get("quality_score", 0.0)

        gates.append(
            QualityGate(
                name="Code Quality",
                threshold=self.quality_gates["min_quality_score"],
                actual=quality_score,
                passed=quality_score >= self.quality_gates["min_quality_score"],
                critical=True,
            )
        )

        # Documentation gate: completeness
        docs_result = agent_results.get("documentation_writer", {}).get("output", {})
        doc_coverage = docs_result.get("coverage_percent", 0.0)

        gates.append(
            QualityGate(
                name="Documentation",
                threshold=self.quality_gates["min_doc_coverage"],
                actual=doc_coverage,
                passed=doc_coverage >= self.quality_gates["min_doc_coverage"],
                critical=False,  # Non-critical - warning only
            )
        )

        return gates

    def _identify_issues(
        self, quality_gates: list[QualityGate], agent_results: dict[str, dict]
    ) -> tuple[list[str], list[str]]:
        """Identify blockers and warnings from quality gates and agent results.

        Args:
            quality_gates: Evaluated quality gates
            agent_results: Agent execution results

        Returns:
            Tuple of (blockers, warnings)
        """
        blockers = []
        warnings = []

        # Check quality gates
        for gate in quality_gates:
            if not gate.passed:
                if gate.critical:
                    blockers.append(f"{gate.name} failed: {gate.message}")
                else:
                    warnings.append(f"{gate.name} below threshold: {gate.message}")

        # Check agent errors
        for agent_id, result in agent_results.items():
            if not result["success"]:
                error = result.get("error", "Unknown error")
                blockers.append(f"Agent {agent_id} failed: {error}")

        return blockers, warnings

    def _generate_summary(
        self,
        approved: bool,
        quality_gates: list[QualityGate],
        agent_results: dict[str, dict],
    ) -> str:
        """Generate executive summary of release readiness.

        Args:
            approved: Overall approval status
            quality_gates: Quality gate results
            agent_results: Agent execution results

        Returns:
            Executive summary text
        """
        lines = []

        if approved:
            lines.append("✅ RELEASE APPROVED")
            lines.append("")
            lines.append("All quality gates passed. The codebase is ready for release.")
        else:
            lines.append("❌ RELEASE NOT APPROVED")
            lines.append("")
            lines.append("Critical quality gates failed. Address blockers before release.")

        lines.append("")
        lines.append("Quality Gate Summary:")

        passed_count = sum(1 for g in quality_gates if g.passed)
        total_count = len(quality_gates)
        lines.append(f"  Passed: {passed_count}/{total_count}")

        failed_gates = [g for g in quality_gates if not g.passed]
        if failed_gates:
            lines.append("  Failed:")
            for gate in failed_gates:
                lines.append(f"    • {gate.name}: {gate.actual:.1f} < {gate.threshold:.1f}")

        lines.append("")
        lines.append(f"Agents Executed: {len(agent_results)}")

        successful_agents = sum(1 for r in agent_results.values() if r["success"])
        lines.append(f"  Successful: {successful_agents}/{len(agent_results)}")

        return "\n".join(lines)


async def main():
    """CLI entry point for orchestrated release preparation."""
    import sys

    workflow = OrchestratedReleasePrepWorkflow()

    # Get path from args or use current directory
    path = sys.argv[1] if len(sys.argv) > 1 else "."

    # Execute workflow
    report = await workflow.execute(path=path)

    # Print formatted report
    print(report.format_console_output())

    # Exit with appropriate code
    sys.exit(0 if report.approved else 1)


if __name__ == "__main__":
    asyncio.run(main())
