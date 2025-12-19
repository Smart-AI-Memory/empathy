"""
Code Inspection Agent Pipeline

Multi-agent orchestrated code inspection with parallel execution,
cross-tool intelligence, and pattern learning.

Usage:
    from agents.code_inspection import CodeInspectionAgent, run_inspection

    # Simple usage
    state = await run_inspection("./src")
    print(f"Health Score: {state['overall_health_score']}/100")

    # Advanced usage
    agent = CodeInspectionAgent(
        parallel_mode=True,
        learning_enabled=True
    )
    state = await agent.inspect(
        project_path="./src",
        target_mode="staged"
    )
    print(agent.format_report(state))

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from .agent import CodeInspectionAgent, run_inspection
from .state import (
    CodeInspectionState,
    CrossToolInsight,
    FindingSeverity,
    HealthStatus,
    HistoricalMatch,
    InspectionFinding,
    InspectionPhase,
    ToolResult,
    add_audit_entry,
    calculate_health_score,
    create_initial_state,
    get_health_grade,
    get_health_status,
)

__all__ = [
    # Agent
    "CodeInspectionAgent",
    "run_inspection",
    # State
    "CodeInspectionState",
    "create_initial_state",
    # Types
    "InspectionPhase",
    "FindingSeverity",
    "HealthStatus",
    "InspectionFinding",
    "ToolResult",
    "CrossToolInsight",
    "HistoricalMatch",
    # Utilities
    "calculate_health_score",
    "get_health_status",
    "get_health_grade",
    "add_audit_entry",
]
