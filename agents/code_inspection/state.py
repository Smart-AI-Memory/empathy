"""
Code Inspection Pipeline - State Management

Defines the shared state structure for the multi-agent code inspection pipeline.
Follows the pattern from compliance_anticipation_agent.py and book_production/state.py
using TypedDict for LangGraph compatibility.

Key Insight: Agent state should answer questions clearly.
"What are we inspecting?" "What did static analysis find?" "How do findings relate?"

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import operator
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Annotated, Any, TypedDict

# Optional LangChain integration
try:
    from langchain_core.messages import BaseMessage
except ImportError:
    # Fallback: Use simple dict-based messages when LangChain not available
    BaseMessage = dict  # type: ignore


# =============================================================================
# Enums and Constants
# =============================================================================


class InspectionPhase(Enum):
    """Phases of code inspection pipeline"""

    INITIALIZATION = "initialization"
    STATIC_ANALYSIS = "static_analysis"  # Phase 1: Parallel
    DYNAMIC_ANALYSIS = "dynamic_analysis"  # Phase 2: Conditional
    CROSS_ANALYSIS = "cross_analysis"  # Phase 3: Correlation
    LEARNING = "learning"  # Phase 4: Pattern extraction
    REPORTING = "reporting"
    COMPLETE = "complete"
    ERROR = "error"


class FindingSeverity(Enum):
    """Severity levels aligned with existing code_health.py"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class HealthStatus(Enum):
    """Overall health status"""

    PASS = "pass"  # Score >= 85
    WARN = "warn"  # Score 70-84
    FAIL = "fail"  # Score < 70


# Weighted scores for health calculation (aligned with code_health.py)
CHECK_WEIGHTS = {
    "security": 100,
    "types": 90,
    "tests": 85,
    "lint": 70,
    "format": 50,
    "debt": 40,
    "deps": 30,
}


# =============================================================================
# Finding Structures
# =============================================================================


@dataclass
class InspectionFinding:
    """Unified finding structure across all tools"""

    finding_id: str
    tool: str  # code_health, test_quality, security, code_review, debugging, tech_debt
    category: str  # lint, format, types, security, test, debt, review
    severity: str  # critical, high, medium, low, info
    file_path: str
    line_number: int | None
    code: str  # Rule code (e.g., "W291", "CWE-89", "B001")
    message: str
    evidence: str  # Code snippet
    confidence: float  # 0.0-1.0
    fixable: bool
    fix_command: str | None = None
    # Cross-references
    related_findings: list[str] = field(default_factory=list)
    historical_matches: list[str] = field(default_factory=list)
    # Metadata
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    remediation: str = ""
    priority_score: int = 50  # 0-100, adjusted by cross-analysis
    priority_boost: bool = False
    boost_reason: str = ""


class ToolResult(TypedDict):
    """Result from a single inspection tool"""

    tool_name: str
    status: str  # pass, warn, fail, skip, error
    score: int  # 0-100
    findings_count: int
    findings: list[dict]  # InspectionFinding as dicts
    findings_by_severity: dict[str, int]  # {severity: count}
    duration_ms: int
    metadata: dict[str, Any]
    error_message: str  # Empty if no error


class CrossToolInsight(TypedDict):
    """Insight derived from correlating multiple tools"""

    insight_id: str
    insight_type: str  # security_informs_review, bugs_inform_tests, debt_trajectory
    source_tools: list[str]
    description: str
    affected_files: list[str]
    recommendations: list[str]
    confidence: float


class HistoricalMatch(TypedDict):
    """Match to a historical bug pattern"""

    pattern_id: str
    error_type: str
    similarity_score: float
    file_path: str
    matched_code: str
    historical_fix: str
    resolution_time_minutes: int


# =============================================================================
# Main State Definition
# =============================================================================


class CodeInspectionState(TypedDict):
    """
    Complete state for Code Inspection Agent Pipeline.

    Design Philosophy (following ComplianceAgentState pattern):
    - Each field answers a specific inspection question
    - All predictions include confidence scores
    - Comprehensive audit trail for traceability
    - Actionable outputs with prioritization
    """

    # =========================================================================
    # Inspection Target - Answers: "What are we inspecting?"
    # =========================================================================
    project_path: str
    target_paths: list[str]  # Specific paths to inspect (or empty for all)
    target_mode: str  # "all", "staged", "changed", "paths"
    exclude_patterns: list[str]  # Glob patterns to exclude
    file_count: int
    total_lines: int
    language_distribution: dict[str, int]  # {".py": 5000, ".ts": 2000}

    # =========================================================================
    # Progress Tracking - Answers: "Where are we in the process?"
    # =========================================================================
    current_phase: str  # InspectionPhase value
    completed_phases: list[str]
    skipped_phases: list[str]  # With reasons
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # =========================================================================
    # Tool Configuration - Answers: "What tools are enabled?"
    # =========================================================================
    enabled_tools: dict[str, bool]  # {tool_name: enabled}
    tool_configs: dict[str, dict]  # {tool_name: config}
    parallel_mode: bool
    learning_enabled: bool
    quick_mode: bool  # Skip slow checks
    baseline_enabled: bool  # Apply baseline suppression filtering

    # =========================================================================
    # Phase 1: Static Analysis Results - Answers: "What did static analysis find?"
    # =========================================================================
    static_analysis_results: dict[str, ToolResult]  # {tool_name: result}

    # Individual tool results for easy access
    code_health_result: ToolResult | None
    security_scan_result: ToolResult | None
    test_quality_result: ToolResult | None
    tech_debt_result: ToolResult | None

    # Aggregated static findings
    static_findings_count: int
    static_critical_count: int

    # =========================================================================
    # Phase 2: Dynamic Analysis Results - Answers: "What did deeper analysis find?"
    # =========================================================================
    dynamic_analysis_results: dict[str, ToolResult]

    # Individual tool results
    code_review_result: ToolResult | None
    advanced_debugging_result: ToolResult | None
    memory_debugging_result: ToolResult | None

    # Conditional execution tracking
    dynamic_analysis_skipped: bool
    skip_reason: str
    deep_dive_triggered: bool
    deep_dive_reason: str

    # =========================================================================
    # Phase 3: Cross-Analysis Results - Answers: "How do findings relate?"
    # =========================================================================
    cross_tool_insights: list[CrossToolInsight]
    security_informed_review: list[dict]  # Security findings that inform code review
    bug_informed_tests: list[dict]  # Bug patterns that inform test suggestions
    debt_trajectory_impact: dict[str, Any]  # How debt affects priority
    historical_patterns_matched: list[HistoricalMatch]

    # =========================================================================
    # Phase 4: Learning Results - Answers: "What patterns did we extract?"
    # =========================================================================
    patterns_extracted: list[dict]
    patterns_stored: list[str]  # Pattern IDs stored
    learning_metadata: dict[str, Any]

    # =========================================================================
    # Unified Report - Answers: "What's the overall health?"
    # =========================================================================
    overall_health_score: int  # 0-100 weighted
    health_status: str  # pass, warn, fail
    health_grade: str  # A, B, C, D, F
    category_scores: dict[str, int]  # {category: score}

    # Findings summary
    total_findings: int
    findings_by_severity: dict[str, int]  # {severity: count}
    findings_by_category: dict[str, int]  # {category: count}
    findings_by_tool: dict[str, int]  # {tool_name: count}

    # Actionability
    fixable_count: int
    auto_fixable: list[dict]  # Can be fixed automatically
    manual_fixes: list[dict]  # Require manual intervention
    blocking_issues: list[dict]  # Must fix before deploy (critical + high)

    # =========================================================================
    # Recommendations & Predictions (Level 4 Anticipatory)
    # =========================================================================
    predictions: list[dict]  # Future issue predictions
    recommendations: list[dict]  # Prioritized recommendations
    action_items: list[dict]  # Specific tasks with assignees

    # =========================================================================
    # Error Handling & Audit Trail
    # =========================================================================
    errors: list[str]
    warnings: list[str]
    audit_trail: list[dict]

    # =========================================================================
    # Metadata
    # =========================================================================
    pipeline_version: str
    execution_id: str
    created_at: str
    last_updated: str
    total_duration_ms: int


# =============================================================================
# Git Integration
# =============================================================================


def get_staged_files(project_path: str) -> list[str]:
    """
    Get list of staged files from git.

    Args:
        project_path: Root path of the git repository

    Returns:
        List of staged file paths relative to project root
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        # Filter to only Python files for now
        return [f for f in files if f.endswith(".py")]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


def get_changed_files(project_path: str, base: str = "HEAD") -> list[str]:
    """
    Get list of changed files from git (compared to base).

    Args:
        project_path: Root path of the git repository
        base: Git reference to compare against (default: HEAD)

    Returns:
        List of changed file paths relative to project root
    """
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", base],
            cwd=project_path,
            capture_output=True,
            text=True,
            check=True,
        )
        files = [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        # Filter to only Python files for now
        return [f for f in files if f.endswith(".py")]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []


# =============================================================================
# State Factory
# =============================================================================


def create_initial_state(
    project_path: str,
    target_mode: str = "all",
    target_paths: list[str] | None = None,
    exclude_patterns: list[str] | None = None,
    parallel_mode: bool = True,
    learning_enabled: bool = True,
    quick_mode: bool = False,
    enabled_tools: dict[str, bool] | None = None,
    baseline_enabled: bool = True,
) -> CodeInspectionState:
    """
    Create initial state for code inspection pipeline.

    Args:
        project_path: Root path to inspect
        target_mode: "all", "staged", "changed", or "paths"
        target_paths: Specific paths to inspect (for "paths" mode)
        exclude_patterns: Glob patterns to exclude
        parallel_mode: Run Phase 1 tools in parallel
        learning_enabled: Extract patterns for future use
        quick_mode: Skip slow checks (deep debugging, etc.)
        enabled_tools: Override which tools are enabled
        baseline_enabled: Apply baseline suppression filtering

    Returns:
        Initialized CodeInspectionState
    """
    import uuid

    now = datetime.now()
    execution_id = f"insp_{now.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

    # Default tool configuration
    default_tools = {
        "code_health": True,
        "security": True,
        "test_quality": True,
        "tech_debt": True,
        "code_review": not quick_mode,
        "advanced_debugging": not quick_mode,
        "memory_debugging": not quick_mode,
    }

    if enabled_tools:
        default_tools.update(enabled_tools)

    # Populate target_paths based on mode
    resolved_target_paths = target_paths or []
    if not resolved_target_paths:
        if target_mode == "staged":
            resolved_target_paths = get_staged_files(project_path)
        elif target_mode == "changed":
            resolved_target_paths = get_changed_files(project_path)
        # "all" mode leaves target_paths empty (inspect everything)

    return CodeInspectionState(
        # Target
        project_path=project_path,
        target_paths=resolved_target_paths,
        target_mode=target_mode,
        exclude_patterns=exclude_patterns
        or ["**/node_modules/**", "**/.venv/**", "**/__pycache__/**"],
        file_count=0,
        total_lines=0,
        language_distribution={},
        # Progress
        current_phase=InspectionPhase.INITIALIZATION.value,
        completed_phases=[],
        skipped_phases=[],
        messages=[],
        # Configuration
        enabled_tools=default_tools,
        tool_configs={},
        parallel_mode=parallel_mode,
        learning_enabled=learning_enabled,
        quick_mode=quick_mode,
        baseline_enabled=baseline_enabled,
        # Phase 1: Static Analysis
        static_analysis_results={},
        code_health_result=None,
        security_scan_result=None,
        test_quality_result=None,
        tech_debt_result=None,
        static_findings_count=0,
        static_critical_count=0,
        # Phase 2: Dynamic Analysis
        dynamic_analysis_results={},
        code_review_result=None,
        advanced_debugging_result=None,
        memory_debugging_result=None,
        dynamic_analysis_skipped=False,
        skip_reason="",
        deep_dive_triggered=False,
        deep_dive_reason="",
        # Phase 3: Cross-Analysis
        cross_tool_insights=[],
        security_informed_review=[],
        bug_informed_tests=[],
        debt_trajectory_impact={},
        historical_patterns_matched=[],
        # Phase 4: Learning
        patterns_extracted=[],
        patterns_stored=[],
        learning_metadata={},
        # Report
        overall_health_score=0,
        health_status="pending",
        health_grade="",
        category_scores={},
        total_findings=0,
        findings_by_severity={},
        findings_by_category={},
        findings_by_tool={},
        fixable_count=0,
        auto_fixable=[],
        manual_fixes=[],
        blocking_issues=[],
        # Recommendations
        predictions=[],
        recommendations=[],
        action_items=[],
        # Errors
        errors=[],
        warnings=[],
        audit_trail=[
            {
                "timestamp": now.isoformat(),
                "phase": "initialization",
                "action": "Pipeline initialized",
                "details": {
                    "project_path": project_path,
                    "target_mode": target_mode,
                    "parallel_mode": parallel_mode,
                    "learning_enabled": learning_enabled,
                    "quick_mode": quick_mode,
                },
            }
        ],
        # Metadata
        pipeline_version="1.0.0",
        execution_id=execution_id,
        created_at=now.isoformat(),
        last_updated=now.isoformat(),
        total_duration_ms=0,
    )


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_health_score(results: dict[str, ToolResult]) -> int:
    """
    Calculate weighted health score following code_health.py pattern.

    Args:
        results: Dictionary of tool results

    Returns:
        Weighted health score 0-100
    """
    total_weight = 0
    weighted_score = 0

    tool_to_category = {
        "code_health": "lint",  # Includes lint, format, types
        "security": "security",
        "test_quality": "tests",
        "tech_debt": "debt",
    }

    for tool_name, result in results.items():
        if result and result.get("status") not in ("skip", "pending"):
            category = tool_to_category.get(tool_name, "lint")
            weight = CHECK_WEIGHTS.get(category, 50)
            weighted_score += result.get("score", 0) * weight
            total_weight += weight

    return int(weighted_score / total_weight) if total_weight > 0 else 100


def get_health_status(score: int) -> str:
    """Get health status from score."""
    if score >= 85:
        return HealthStatus.PASS.value
    elif score >= 70:
        return HealthStatus.WARN.value
    else:
        return HealthStatus.FAIL.value


def get_health_grade(score: int) -> str:
    """Get letter grade from score."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def add_audit_entry(
    state: CodeInspectionState,
    phase: str,
    action: str,
    details: dict[str, Any] | None = None,
) -> None:
    """
    Add entry to audit trail (mutates state in place).

    Args:
        state: Current inspection state
        phase: Current phase name
        action: Description of action
        details: Additional details
    """
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "phase": phase,
            "action": action,
            "details": details or {},
        }
    )
    state["last_updated"] = datetime.now().isoformat()
