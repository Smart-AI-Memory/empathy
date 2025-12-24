"""
Shared Task-Type Schema for Empathy Framework

Provides a unified vocabulary for task types across:
- empathy_llm_toolkit.routing.ModelRouter
- src/empathy_os/workflows.WorkflowBase
- empathy_software_plugin.wizards.MultiModelWizard

This module defines:
- TaskType enum with canonical task names
- Task-to-tier mappings
- Task normalization and lookup functions

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from dataclasses import dataclass
from enum import Enum

from .registry import ModelTier


class TaskType(Enum):
    """
    Canonical task types for model routing.

    Tasks are organized by their typical tier:
    - CHEAP tier: Simple, fast tasks
    - CAPABLE tier: Standard development work
    - PREMIUM tier: Complex reasoning and coordination
    """

    # =========================================================================
    # CHEAP TIER TASKS (~$0.15-1.00/M input)
    # Fast models for simple, well-defined tasks
    # =========================================================================
    SUMMARIZE = "summarize"
    CLASSIFY = "classify"
    TRIAGE = "triage"
    MATCH_PATTERN = "match_pattern"
    EXTRACT_TOPICS = "extract_topics"
    LINT_CHECK = "lint_check"
    FORMAT_CODE = "format_code"
    SIMPLE_QA = "simple_qa"
    CATEGORIZE = "categorize"

    # =========================================================================
    # CAPABLE TIER TASKS (~$2.50-3.00/M input)
    # Balanced models for standard development work
    # =========================================================================
    GENERATE_CODE = "generate_code"
    FIX_BUG = "fix_bug"
    REVIEW_SECURITY = "review_security"
    ANALYZE_PERFORMANCE = "analyze_performance"
    WRITE_TESTS = "write_tests"
    REFACTOR = "refactor"
    EXPLAIN_CODE = "explain_code"
    DOCUMENT_CODE = "document_code"
    ANALYZE_ERROR = "analyze_error"
    SUGGEST_FIX = "suggest_fix"

    # =========================================================================
    # PREMIUM TIER TASKS (~$15.00/M input)
    # Highest capability for complex reasoning
    # =========================================================================
    COORDINATE = "coordinate"
    SYNTHESIZE_RESULTS = "synthesize_results"
    ARCHITECTURAL_DECISION = "architectural_decision"
    NOVEL_PROBLEM = "novel_problem"
    FINAL_REVIEW = "final_review"
    COMPLEX_REASONING = "complex_reasoning"
    MULTI_STEP_PLANNING = "multi_step_planning"
    CRITICAL_DECISION = "critical_decision"


@dataclass(frozen=True)
class TaskInfo:
    """Information about a task type."""

    task_type: TaskType
    tier: ModelTier
    description: str


# =============================================================================
# TASK-TO-TIER MAPPINGS
# =============================================================================

# Cheap tier tasks
CHEAP_TASKS: frozenset[str] = frozenset(
    [
        TaskType.SUMMARIZE.value,
        TaskType.CLASSIFY.value,
        TaskType.TRIAGE.value,
        TaskType.MATCH_PATTERN.value,
        TaskType.EXTRACT_TOPICS.value,
        TaskType.LINT_CHECK.value,
        TaskType.FORMAT_CODE.value,
        TaskType.SIMPLE_QA.value,
        TaskType.CATEGORIZE.value,
    ]
)

# Capable tier tasks
CAPABLE_TASKS: frozenset[str] = frozenset(
    [
        TaskType.GENERATE_CODE.value,
        TaskType.FIX_BUG.value,
        TaskType.REVIEW_SECURITY.value,
        TaskType.ANALYZE_PERFORMANCE.value,
        TaskType.WRITE_TESTS.value,
        TaskType.REFACTOR.value,
        TaskType.EXPLAIN_CODE.value,
        TaskType.DOCUMENT_CODE.value,
        TaskType.ANALYZE_ERROR.value,
        TaskType.SUGGEST_FIX.value,
    ]
)

# Premium tier tasks
PREMIUM_TASKS: frozenset[str] = frozenset(
    [
        TaskType.COORDINATE.value,
        TaskType.SYNTHESIZE_RESULTS.value,
        TaskType.ARCHITECTURAL_DECISION.value,
        TaskType.NOVEL_PROBLEM.value,
        TaskType.FINAL_REVIEW.value,
        TaskType.COMPLEX_REASONING.value,
        TaskType.MULTI_STEP_PLANNING.value,
        TaskType.CRITICAL_DECISION.value,
    ]
)

# Complete mapping for lookup
TASK_TIER_MAP: dict[str, ModelTier] = {
    **dict.fromkeys(CHEAP_TASKS, ModelTier.CHEAP),
    **dict.fromkeys(CAPABLE_TASKS, ModelTier.CAPABLE),
    **dict.fromkeys(PREMIUM_TASKS, ModelTier.PREMIUM),
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


def normalize_task_type(task_type: str) -> str:
    """
    Normalize a task type string for lookup.

    Converts to lowercase and normalizes separators to underscores.

    Args:
        task_type: Task type string (e.g., "Fix-Bug", "fix bug", "FIX_BUG")

    Returns:
        Normalized task type (e.g., "fix_bug")
    """
    return task_type.lower().replace("-", "_").replace(" ", "_")


def get_tier_for_task(task_type: str | TaskType) -> ModelTier:
    """
    Get the appropriate tier for a task type.

    Args:
        task_type: Task type string or TaskType enum

    Returns:
        ModelTier for the task (defaults to CAPABLE for unknown tasks)

    Example:
        >>> get_tier_for_task("summarize")
        ModelTier.CHEAP
        >>> get_tier_for_task("fix_bug")
        ModelTier.CAPABLE
        >>> get_tier_for_task("coordinate")
        ModelTier.PREMIUM
        >>> get_tier_for_task("unknown_task")
        ModelTier.CAPABLE
    """
    # Handle TaskType enum
    if isinstance(task_type, TaskType):
        task_str = task_type.value
    else:
        task_str = normalize_task_type(task_type)

    # Lookup in mapping
    return TASK_TIER_MAP.get(task_str, ModelTier.CAPABLE)


def get_tasks_for_tier(tier: ModelTier) -> list[str]:
    """
    Get all task types for a given tier.

    Args:
        tier: ModelTier to get tasks for

    Returns:
        List of task type strings
    """
    if tier == ModelTier.CHEAP:
        return list(CHEAP_TASKS)
    elif tier == ModelTier.CAPABLE:
        return list(CAPABLE_TASKS)
    elif tier == ModelTier.PREMIUM:
        return list(PREMIUM_TASKS)
    return []


def get_all_tasks() -> dict[str, list[str]]:
    """
    Get all known task types organized by tier.

    Returns:
        Dict mapping tier name to list of task types
    """
    return {
        "cheap": list(CHEAP_TASKS),
        "capable": list(CAPABLE_TASKS),
        "premium": list(PREMIUM_TASKS),
    }


def is_known_task(task_type: str) -> bool:
    """
    Check if a task type is known/defined.

    Args:
        task_type: Task type string

    Returns:
        True if task is defined, False otherwise
    """
    normalized = normalize_task_type(task_type)
    return normalized in TASK_TIER_MAP


# =============================================================================
# TASK INFO REGISTRY
# =============================================================================
# Detailed information about each task type

TASK_INFO: dict[TaskType, TaskInfo] = {
    # Cheap tasks
    TaskType.SUMMARIZE: TaskInfo(
        TaskType.SUMMARIZE,
        ModelTier.CHEAP,
        "Summarize text or code into concise form",
    ),
    TaskType.CLASSIFY: TaskInfo(
        TaskType.CLASSIFY,
        ModelTier.CHEAP,
        "Classify input into predefined categories",
    ),
    TaskType.TRIAGE: TaskInfo(
        TaskType.TRIAGE,
        ModelTier.CHEAP,
        "Quick assessment and prioritization",
    ),
    TaskType.SIMPLE_QA: TaskInfo(
        TaskType.SIMPLE_QA,
        ModelTier.CHEAP,
        "Answer simple, factual questions",
    ),
    # Capable tasks
    TaskType.GENERATE_CODE: TaskInfo(
        TaskType.GENERATE_CODE,
        ModelTier.CAPABLE,
        "Generate new code from requirements",
    ),
    TaskType.FIX_BUG: TaskInfo(
        TaskType.FIX_BUG,
        ModelTier.CAPABLE,
        "Identify and fix bugs in code",
    ),
    TaskType.REVIEW_SECURITY: TaskInfo(
        TaskType.REVIEW_SECURITY,
        ModelTier.CAPABLE,
        "Review code for security vulnerabilities",
    ),
    TaskType.WRITE_TESTS: TaskInfo(
        TaskType.WRITE_TESTS,
        ModelTier.CAPABLE,
        "Write unit or integration tests",
    ),
    # Premium tasks
    TaskType.COORDINATE: TaskInfo(
        TaskType.COORDINATE,
        ModelTier.PREMIUM,
        "Coordinate multi-agent workflows",
    ),
    TaskType.ARCHITECTURAL_DECISION: TaskInfo(
        TaskType.ARCHITECTURAL_DECISION,
        ModelTier.PREMIUM,
        "Make complex architectural decisions",
    ),
    TaskType.COMPLEX_REASONING: TaskInfo(
        TaskType.COMPLEX_REASONING,
        ModelTier.PREMIUM,
        "Handle complex multi-step reasoning",
    ),
}
