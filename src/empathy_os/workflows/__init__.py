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

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import importlib.util
import os

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
from .config import (
    DEFAULT_MODELS,
    ModelConfig,
    WorkflowConfig,
    create_example_config,
    get_model,
)
from .dependency_check import DependencyCheckWorkflow
from .document_gen import DocumentGenerationWorkflow
from .perf_audit import PerformanceAuditWorkflow
from .pr_review import PRReviewResult, PRReviewWorkflow
from .refactor_plan import RefactorPlanWorkflow
from .release_prep import ReleasePreparationWorkflow
from .research_synthesis import ResearchSynthesisWorkflow

# Security crew integration (v3.0)
from .secure_release import SecureReleasePipeline, SecureReleaseResult
from .security_audit import SecurityAuditWorkflow
from .step_config import (
    WorkflowStepConfig,
    steps_from_tier_map,
    validate_step_config,
)
from .test_gen import TestGenerationWorkflow

# Re-export CLI commands from the workflows.py module
# This handles the package shadowing the .py file
_parent_dir = os.path.dirname(os.path.dirname(__file__))
_workflows_module_path = os.path.join(_parent_dir, "empathy_os", "workflows.py")

# Try the parent-level path first
if not os.path.exists(_workflows_module_path):
    _workflows_module_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "workflows.py"
    )

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

# Workflow registry for CLI discovery
WORKFLOW_REGISTRY: dict[str, type[BaseWorkflow]] = {
    # Core workflows
    "research": ResearchSynthesisWorkflow,
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
}


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
        workflows.append(
            {
                "name": name,
                "class": cls.__name__,
                "description": cls.description,
                "stages": cls.stages,
                "tier_map": {k: v.value for k, v in cls.tier_map.items()},
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
    # Registry
    "WORKFLOW_REGISTRY",
    "get_workflow",
    "list_workflows",
    # Stats for dashboard
    "get_workflow_stats",
    # CLI commands (re-exported from workflows.py)
    "cmd_morning",
    "cmd_ship",
    "cmd_fix_all",
    "cmd_learn",
]
