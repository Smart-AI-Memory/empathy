"""
Code Inspection Agent - LangGraph Implementation

Multi-agent orchestrated code inspection pipeline with parallel execution,
cross-tool intelligence, and pattern learning.

Following the pattern from compliance_anticipation_agent.py.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import logging
from typing import Any

from .handoffs import (
    create_cross_to_learning_handoff,
    create_dynamic_to_cross_handoff,
    create_static_to_dynamic_handoff,
    format_handoff_for_log,
)
from .nodes import (
    generate_unified_report,
    run_cross_analysis,
    run_deep_dive_analysis,
    run_dynamic_analysis,
    run_learning_phase,
    run_static_analysis,
)
from .nodes.dynamic_analysis import handle_skip_dynamic
from .nodes.reporting import (
    format_report_html,
    format_report_json,
    format_report_markdown,
    format_report_sarif,
    format_report_terminal,
)
from .routing import should_run_dynamic_analysis
from .state import CodeInspectionState, create_initial_state

logger = logging.getLogger(__name__)

# Try to import LangGraph, but provide fallback
try:
    from langgraph.graph import END, StateGraph

    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not available, using simple sequential pipeline")


class CodeInspectionAgent:
    """
    Code Inspection Agent with parallel execution and cross-tool intelligence.

    Uses LangGraph for orchestration when available, falls back to
    simple sequential execution otherwise.

    Features:
    - Phase 1: Parallel static analysis (lint, security, debt, test quality)
    - Phase 2: Conditional dynamic analysis (code review, debugging)
    - Phase 3: Cross-tool intelligence (correlate findings)
    - Phase 4: Pattern learning (extract for future use)
    - Phase 5: Unified reporting (single health score)
    """

    def __init__(
        self,
        parallel_mode: bool = True,
        learning_enabled: bool = True,
        use_langgraph: bool = True,
        baseline_enabled: bool = True,
    ):
        """
        Initialize the Code Inspection Agent.

        Args:
            parallel_mode: Run Phase 1 tools in parallel
            learning_enabled: Extract patterns for future use
            use_langgraph: Use LangGraph for orchestration (if available)
            baseline_enabled: Apply baseline suppression filtering
        """
        self.parallel_mode = parallel_mode
        self.learning_enabled = learning_enabled
        self.use_langgraph = use_langgraph and LANGGRAPH_AVAILABLE
        self.baseline_enabled = baseline_enabled

        if self.use_langgraph:
            self._agent = self._create_langgraph_agent()
        else:
            self._agent = None

    def _create_langgraph_agent(self) -> Any:
        """
        Create LangGraph StateGraph for pipeline orchestration.

        Following the pattern from compliance_anticipation_agent.py.
        """
        workflow = StateGraph(CodeInspectionState)

        # Add nodes for each phase
        workflow.add_node("static_analysis", run_static_analysis)
        workflow.add_node("dynamic_analysis", run_dynamic_analysis)
        workflow.add_node("deep_dive_analysis", run_deep_dive_analysis)
        workflow.add_node("skip_dynamic", handle_skip_dynamic)
        workflow.add_node("cross_analysis", run_cross_analysis)
        workflow.add_node("learning", run_learning_phase)
        workflow.add_node("reporting", generate_unified_report)

        # Set entry point
        workflow.set_entry_point("static_analysis")

        # Conditional routing after static analysis
        workflow.add_conditional_edges(
            "static_analysis",
            should_run_dynamic_analysis,
            {
                "skip_critical_security": "skip_dynamic",
                "skip_type_errors": "skip_dynamic",
                "deep_dive": "deep_dive_analysis",
                "proceed": "dynamic_analysis",
            },
        )

        # Converge all paths to cross-analysis
        workflow.add_edge("dynamic_analysis", "cross_analysis")
        workflow.add_edge("deep_dive_analysis", "cross_analysis")
        workflow.add_edge("skip_dynamic", "cross_analysis")

        # Cross-analysis to learning to reporting
        workflow.add_edge("cross_analysis", "learning")
        workflow.add_edge("learning", "reporting")
        workflow.add_edge("reporting", END)

        return workflow.compile()

    async def inspect(
        self,
        project_path: str,
        target_mode: str = "all",
        target_paths: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        output_format: str = "terminal",
    ) -> CodeInspectionState:
        """
        Run code inspection pipeline.

        Args:
            project_path: Root path to inspect
            target_mode: "all", "staged", "changed", or "paths"
            target_paths: Specific paths to inspect
            exclude_patterns: Glob patterns to exclude
            output_format: Output format ("terminal", "json", "markdown")

        Returns:
            Final inspection state with all results
        """
        logger.info(f"Starting code inspection for {project_path}")

        # Create initial state
        state = create_initial_state(
            project_path=project_path,
            target_mode=target_mode,
            target_paths=target_paths,
            exclude_patterns=exclude_patterns,
            parallel_mode=self.parallel_mode,
            learning_enabled=self.learning_enabled,
            baseline_enabled=self.baseline_enabled,
        )

        # Run pipeline
        if self.use_langgraph and self._agent:
            final_state = await self._run_langgraph(state)
        else:
            final_state = await self._run_sequential(state)

        # Log summary
        logger.info(
            f"Inspection complete: Score={final_state['overall_health_score']}/100, "
            f"Status={final_state['health_status']}, "
            f"Findings={final_state['total_findings']}"
        )

        return final_state

    async def _run_langgraph(self, state: CodeInspectionState) -> CodeInspectionState:
        """Run pipeline using LangGraph orchestration."""
        logger.info("Running inspection with LangGraph orchestration")
        return await self._agent.ainvoke(state)

    async def _run_sequential(self, state: CodeInspectionState) -> CodeInspectionState:
        """Run pipeline sequentially (fallback when LangGraph unavailable)."""
        logger.info("Running inspection sequentially (LangGraph unavailable)")

        # Phase 1: Static Analysis
        state = await run_static_analysis(state)

        # Log handoff
        handoff = create_static_to_dynamic_handoff(state)
        logger.debug(format_handoff_for_log(handoff))

        # Phase 2: Dynamic Analysis (with routing)
        route = should_run_dynamic_analysis(state)
        if route in ("skip_critical_security", "skip_type_errors"):
            state = await handle_skip_dynamic(state)
        elif route == "deep_dive":
            state = await run_deep_dive_analysis(state)
        else:
            state = await run_dynamic_analysis(state)

        # Log handoff
        handoff = create_dynamic_to_cross_handoff(state)
        logger.debug(format_handoff_for_log(handoff))

        # Phase 3: Cross-Analysis
        state = await run_cross_analysis(state)

        # Log handoff
        handoff = create_cross_to_learning_handoff(state)
        logger.debug(format_handoff_for_log(handoff))

        # Phase 4: Learning
        state = await run_learning_phase(state)

        # Phase 5: Reporting
        state = await generate_unified_report(state)

        return state

    def format_report(
        self,
        state: CodeInspectionState,
        output_format: str = "terminal",
    ) -> str:
        """
        Format inspection report for output.

        Args:
            state: Final inspection state
            output_format: "terminal", "json", "markdown", "sarif", or "html"

        Returns:
            Formatted report string
        """
        if output_format == "json":
            return format_report_json(state)
        elif output_format == "markdown":
            return format_report_markdown(state)
        elif output_format == "sarif":
            return format_report_sarif(state)
        elif output_format == "html":
            return format_report_html(state)
        else:
            return format_report_terminal(state)


# =============================================================================
# Convenience Functions
# =============================================================================


async def run_inspection(
    project_path: str,
    parallel_mode: bool = True,
    learning_enabled: bool = True,
    output_format: str = "terminal",
) -> CodeInspectionState:
    """
    Convenience function to run code inspection.

    Args:
        project_path: Root path to inspect
        parallel_mode: Run Phase 1 tools in parallel
        learning_enabled: Extract patterns for future use
        output_format: Output format

    Returns:
        Final inspection state
    """
    agent = CodeInspectionAgent(
        parallel_mode=parallel_mode,
        learning_enabled=learning_enabled,
    )
    return await agent.inspect(project_path, output_format=output_format)


if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        """Run inspection on current directory."""
        project_path = sys.argv[1] if len(sys.argv) > 1 else "."

        agent = CodeInspectionAgent()
        state = await agent.inspect(project_path)

        print(agent.format_report(state))

        # Exit code based on health
        if state["health_status"] == "fail":
            sys.exit(1)
        sys.exit(0)

    asyncio.run(main())
