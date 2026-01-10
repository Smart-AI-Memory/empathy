"""Meta-orchestration system for dynamic agent composition.

This package provides the infrastructure for dynamically composing
agent teams based on task requirements. It enables intelligent task
analysis, agent spawning, and execution strategy selection.

Example:
    >>> from empathy_os.orchestration import AgentTemplate, get_template
    >>> template = get_template("test_coverage_analyzer")
    >>> print(template.role)
    Test Coverage Expert
"""

from empathy_os.orchestration.agent_templates import (
    AgentCapability,
    AgentTemplate,
    ResourceRequirements,
    get_all_templates,
    get_template,
    get_templates_by_capability,
    get_templates_by_tier,
)

__all__ = [
    "AgentTemplate",
    "AgentCapability",
    "ResourceRequirements",
    "get_template",
    "get_all_templates",
    "get_templates_by_capability",
    "get_templates_by_tier",
]
