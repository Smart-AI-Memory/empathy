"""
Multi-Model Workflow Templates for Empathy Framework

Cost-optimized workflow patterns that leverage 3-tier model routing:
- Haiku (cheap): Summarization, classification, triage
- Sonnet (capable): Analysis, code generation, security review
- Opus (premium): Synthesis, architectural decisions, coordination

Usage:
    from empathy_os.workflows import ResearchSynthesisWorkflow

    workflow = ResearchSynthesisWorkflow()
    result = await workflow.execute(
        sources=["doc1.md", "doc2.md"],
        question="What are the key patterns?"
    )

    print(f"Cost: ${result.cost_report.total_cost:.4f}")
    print(f"Saved: {result.cost_report.savings_percent:.1f}% vs premium-only")

Workflow Discovery:
    Workflows can be discovered via entry points (pyproject.toml):

    [project.entry-points."empathy.workflows"]
    my-workflow = "my_package.workflows:MyWorkflow"

    Then call discover_workflows() to load all registered workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import importlib.metadata
import importlib.util
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseWorkflow

from .base import (
    PROVIDER_MODELS,
    BaseWorkflow,
    CostReport,
    ModelProvider,
    ModelTier,
    WorkflowResult,
    WorkflowStage,
    get_workflow_stats,
)

# New high-value workflows
from .bug_predict import BugPredictionWorkflow
from .code_review import CodeReviewWorkflow

# Code review crew integration (v3.1)
from .code_review_pipeline import CodeReviewPipeline, CodeReviewPipelineResult
from .config import DEFAULT_MODELS, ModelConfig, WorkflowConfig, create_example_config, get_model
from .dependency_check import DependencyCheckWorkflow
from .document_gen import DocumentGenerationWorkflow
from .health_check import HealthCheckWorkflow
from .perf_audit import PerformanceAuditWorkflow
from .pr_review import PRReviewResult, PRReviewWorkflow
from .refactor_plan import RefactorPlanWorkflow
from .release_prep import ReleasePreparationWorkflow
from .research_synthesis import ResearchSynthesisWorkflow

# Security crew integration (v3.0)
from .secure_release import SecureReleasePipeline, SecureReleaseResult
from .security_audit import SecurityAuditWorkflow
from .step_config import WorkflowStepConfig, steps_from_tier_map, validate_step_config
from .test_gen import TestGenerationWorkflow

# Re-export CLI commands from workflow_commands.py
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_workflows_module_path = os.path.join(_parent_dir, "workflow_commands.py")

# Initialize to None for type checking
cmd_morning = None
cmd_ship = None
cmd_fix_all = None
cmd_learn = None

if os.path.exists(_workflows_module_path):
    _spec = importlib.util.spec_from_file_location("_workflows_cli", _workflows_module_path)
    if _spec is not None and _spec.loader is not None:
        _workflows_cli = importlib.util.module_from_spec(_spec)
        _spec.loader.exec_module(_workflows_cli)

        # Re-export CLI commands
        cmd_morning = _workflows_cli.cmd_morning
        cmd_ship = _workflows_cli.cmd_ship
        cmd_fix_all = _workflows_cli.cmd_fix_all
        cmd_learn = _workflows_cli.cmd_learn

# Default workflow registry (statically defined for backwards compatibility)
_DEFAULT_WORKFLOWS: dict[str, type[BaseWorkflow]] = {
    # Core workflows
    "code-review": CodeReviewWorkflow,
    "doc-gen": DocumentGenerationWorkflow,
    # Analysis workflows
    "bug-predict": BugPredictionWorkflow,
    "security-audit": SecurityAuditWorkflow,
    "perf-audit": PerformanceAuditWorkflow,
    # Generation workflows
    "test-gen": TestGenerationWorkflow,
    "refactor-plan": RefactorPlanWorkflow,
    # Operational workflows
    "dependency-check": DependencyCheckWorkflow,
    "release-prep": ReleasePreparationWorkflow,
    # Composite security pipeline (v3.0)
    "secure-release": SecureReleasePipeline,
    # Code review crew integration (v3.1)
    "pro-review": CodeReviewPipeline,
    "pr-review": PRReviewWorkflow,
    # Health check crew integration (v3.1)
    "health-check": HealthCheckWorkflow,
}

# Workflow registry populated at module load
WORKFLOW_REGISTRY: dict[str, type[BaseWorkflow]] = {}


def discover_workflows(include_defaults: bool = True) -> dict[str, type[BaseWorkflow]]:
    """
    Discover workflows via entry points.

    This function loads workflows registered as entry points under the
    'empathy.workflows' group. This allows third-party packages to register
    custom workflows that integrate with the Empathy Framework.

    Args:
        include_defaults: Whether to include default built-in workflows

    Returns:
        Dictionary mapping workflow names to workflow classes

    Example:
        # In your pyproject.toml:
        [project.entry-points."empathy.workflows"]
        my-workflow = "my_package.workflows:MyCustomWorkflow"

        # In your code:
        from empathy_os.workflows import discover_workflows
        workflows = discover_workflows()
        MyWorkflow = workflows.get("my-workflow")
    """
    discovered: dict[str, type[BaseWorkflow]] = {}

    # Include default workflows if requested
    if include_defaults:
        discovered.update(_DEFAULT_WORKFLOWS)

    # Discover via entry points
    try:
        eps = importlib.metadata.entry_points(group="empathy.workflows")
        for ep in eps:
            try:
                workflow_cls = ep.load()
                # Validate it's a proper workflow class
                if isinstance(workflow_cls, type) and hasattr(workflow_cls, "execute"):
                    discovered[ep.name] = workflow_cls
            except Exception:
                # Skip invalid entry points silently
                pass
    except Exception:
        # If entry point discovery fails, just use defaults
        pass

    return discovered


def refresh_workflow_registry() -> None:
    """
    Refresh the global WORKFLOW_REGISTRY by re-discovering all workflows.

    Call this after installing new packages that register workflows.
    """
    global WORKFLOW_REGISTRY
    WORKFLOW_REGISTRY.clear()
    WORKFLOW_REGISTRY.update(discover_workflows())


# Initialize registry on module load
WORKFLOW_REGISTRY.update(discover_workflows())


def get_workflow(name: str) -> type[BaseWorkflow]:
    """
    Get a workflow class by name.

    Args:
        name: Workflow name (e.g., "research", "code-review", "doc-gen")

    Returns:
        Workflow class

    Raises:
        KeyError: If workflow not found
    """
    if name not in WORKFLOW_REGISTRY:
        available = ", ".join(WORKFLOW_REGISTRY.keys())
        raise KeyError(f"Unknown workflow: {name}. Available: {available}")
    return WORKFLOW_REGISTRY[name]


def list_workflows() -> list[dict]:
    """
    List all available workflows with descriptions.

    Returns:
        List of workflow info dicts
    """
    workflows = []
    for name, cls in WORKFLOW_REGISTRY.items():
        # Handle both BaseWorkflow subclasses and composite pipelines
        stages = getattr(cls, "stages", [])
        tier_map = getattr(cls, "tier_map", {})
        description = getattr(cls, "description", "No description")

        workflows.append(
            {
                "name": name,
                "class": cls.__name__,
                "description": description,
                "stages": stages,
                "tier_map": {k: v.value for k, v in tier_map.items()} if tier_map else {},
            }
        )
    return workflows


__all__ = [
    # Base classes
    "BaseWorkflow",
    "ModelTier",
    "ModelProvider",
    "PROVIDER_MODELS",
    "WorkflowStage",
    "CostReport",
    "WorkflowResult",
    # Step configuration (new)
    "WorkflowStepConfig",
    "validate_step_config",
    "steps_from_tier_map",
    # Configuration
    "WorkflowConfig",
    "ModelConfig",
    "DEFAULT_MODELS",
    "get_model",
    "create_example_config",
    # Workflow implementations
    "ResearchSynthesisWorkflow",
    "CodeReviewWorkflow",
    "DocumentGenerationWorkflow",
    # New high-value workflows
    "BugPredictionWorkflow",
    "SecurityAuditWorkflow",
    "TestGenerationWorkflow",
    "RefactorPlanWorkflow",
    "DependencyCheckWorkflow",
    "ReleasePreparationWorkflow",
    "PerformanceAuditWorkflow",
    # Security crew integration (v3.0)
    "SecureReleasePipeline",
    "SecureReleaseResult",
    # Code review crew integration (v3.1)
    "CodeReviewPipeline",
    "CodeReviewPipelineResult",
    "PRReviewWorkflow",
    "PRReviewResult",
    # Health check crew integration (v3.1)
    "HealthCheckWorkflow",
    # Registry and discovery
    "WORKFLOW_REGISTRY",
    "get_workflow",
    "list_workflows",
    "discover_workflows",
    "refresh_workflow_registry",
    # Stats for dashboard
    "get_workflow_stats",
    # CLI commands (re-exported from workflow_commands.py)
    "cmd_morning",
    "cmd_ship",
    "cmd_fix_all",
    "cmd_learn",
]
