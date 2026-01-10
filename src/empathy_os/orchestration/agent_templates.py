"""Agent template system for meta-orchestration.

This module provides reusable agent archetypes that can be customized
for specific tasks. Templates define agent capabilities, tools, and
quality gates.

Security:
    - All template fields validated on creation
    - No eval() or exec() usage
    - Input sanitization on template lookup

Example:
    >>> template = get_template("test_coverage_analyzer")
    >>> print(template.role)
    Test Coverage Expert

    >>> templates = get_templates_by_capability("analyze_gaps")
    >>> print([t.id for t in templates])
    ['test_coverage_analyzer']
"""

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class AgentCapability:
    """Capability that an agent can perform.

    Attributes:
        name: Capability identifier (e.g., "analyze_gaps")
        description: Human-readable description
        required_tools: List of tools needed for this capability

    Example:
        >>> cap = AgentCapability(
        ...     name="analyze_gaps",
        ...     description="Identify test coverage gaps",
        ...     required_tools=["coverage_analyzer"]
        ... )
    """

    name: str
    description: str
    required_tools: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate capability fields."""
        if not self.name or not isinstance(self.name, str):
            raise ValueError("name must be a non-empty string")
        if not self.description or not isinstance(self.description, str):
            raise ValueError("description must be a non-empty string")
        if not isinstance(self.required_tools, list):
            raise ValueError("required_tools must be a list")


@dataclass(frozen=True)
class ResourceRequirements:
    """Resource requirements for agent execution.

    Attributes:
        min_tokens: Minimum token budget required
        max_tokens: Maximum token budget allowed
        timeout_seconds: Maximum execution time in seconds
        memory_mb: Maximum memory usage in megabytes

    Example:
        >>> req = ResourceRequirements(
        ...     min_tokens=1000,
        ...     max_tokens=10000,
        ...     timeout_seconds=300,
        ...     memory_mb=512
        ... )
    """

    min_tokens: int = 1000
    max_tokens: int = 10000
    timeout_seconds: int = 300
    memory_mb: int = 512

    def __post_init__(self):
        """Validate resource requirements."""
        if self.min_tokens < 0:
            raise ValueError("min_tokens must be non-negative")
        if self.max_tokens < self.min_tokens:
            raise ValueError("max_tokens must be >= min_tokens")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if self.memory_mb <= 0:
            raise ValueError("memory_mb must be positive")


@dataclass(frozen=True)
class AgentTemplate:
    """Reusable agent archetype.

    Templates define agent capabilities, tools, and quality gates.
    They can be customized for specific tasks during agent spawning.

    Attributes:
        id: Unique template identifier
        role: Agent role description
        capabilities: List of capability names
        tier_preference: Preferred tier ("CHEAP", "CAPABLE", "PREMIUM")
        tools: List of tool identifiers
        default_instructions: Default instructions for the agent
        quality_gates: Quality gate thresholds
        resource_requirements: Resource limits and requirements

    Example:
        >>> template = AgentTemplate(
        ...     id="test_coverage_analyzer",
        ...     role="Test Coverage Expert",
        ...     capabilities=["analyze_gaps", "suggest_tests"],
        ...     tier_preference="CAPABLE",
        ...     tools=["coverage_analyzer"],
        ...     default_instructions="Analyze test coverage...",
        ...     quality_gates={"min_coverage": 80}
        ... )

    Security:
        - All fields validated on creation
        - tier_preference restricted to allowed values
        - No user input used in eval/exec
    """

    id: str
    role: str
    capabilities: list[str]
    tier_preference: str
    tools: list[str]
    default_instructions: str
    quality_gates: dict[str, Any]
    resource_requirements: ResourceRequirements = field(default_factory=ResourceRequirements)

    ALLOWED_TIERS = {"CHEAP", "CAPABLE", "PREMIUM"}

    def __post_init__(self):
        """Validate template fields.

        Raises:
            ValueError: If any field is invalid
        """
        # Validate ID
        if not self.id or not isinstance(self.id, str):
            raise ValueError("id must be a non-empty string")

        # Validate role
        if not self.role or not isinstance(self.role, str):
            raise ValueError("role must be a non-empty string")

        # Validate capabilities
        if not isinstance(self.capabilities, list):
            raise ValueError("capabilities must be a list")
        if not self.capabilities:
            raise ValueError("capabilities must not be empty")
        for cap in self.capabilities:
            if not isinstance(cap, str) or not cap:
                raise ValueError("all capabilities must be non-empty strings")

        # Validate tier preference
        if self.tier_preference not in self.ALLOWED_TIERS:
            raise ValueError(f"tier_preference must be one of {self.ALLOWED_TIERS}")

        # Validate tools
        if not isinstance(self.tools, list):
            raise ValueError("tools must be a list")
        for tool in self.tools:
            if not isinstance(tool, str) or not tool:
                raise ValueError("all tools must be non-empty strings")

        # Validate instructions
        if not self.default_instructions or not isinstance(self.default_instructions, str):
            raise ValueError("default_instructions must be a non-empty string")

        # Validate quality gates
        if not isinstance(self.quality_gates, dict):
            raise ValueError("quality_gates must be a dict")

        # Validate resource requirements
        if not isinstance(self.resource_requirements, ResourceRequirements):
            raise ValueError("resource_requirements must be a ResourceRequirements instance")


# Registry of pre-built agent templates
_TEMPLATE_REGISTRY: dict[str, AgentTemplate] = {}


def _register_template(template: AgentTemplate) -> None:
    """Register a template in the global registry.

    Args:
        template: Template to register

    Raises:
        ValueError: If template with same ID already registered
    """
    if template.id in _TEMPLATE_REGISTRY:
        raise ValueError(f"Template '{template.id}' already registered")
    _TEMPLATE_REGISTRY[template.id] = template
    logger.debug(f"Registered template: {template.id}")


def get_template(template_id: str) -> AgentTemplate | None:
    """Retrieve template by ID.

    Args:
        template_id: Template identifier

    Returns:
        Template if found, None otherwise

    Example:
        >>> template = get_template("test_coverage_analyzer")
        >>> print(template.role)
        Test Coverage Expert
    """
    if not template_id or not isinstance(template_id, str):
        logger.warning(f"Invalid template_id: {template_id}")
        return None
    return _TEMPLATE_REGISTRY.get(template_id)


def get_all_templates() -> list[AgentTemplate]:
    """Retrieve all registered templates.

    Returns:
        List of all templates

    Example:
        >>> templates = get_all_templates()
        >>> len(templates) >= 7
        True
    """
    return list(_TEMPLATE_REGISTRY.values())


def get_templates_by_capability(capability: str) -> list[AgentTemplate]:
    """Retrieve templates with a specific capability.

    Args:
        capability: Capability name to search for

    Returns:
        List of templates with that capability

    Example:
        >>> templates = get_templates_by_capability("analyze_gaps")
        >>> any(t.id == "test_coverage_analyzer" for t in templates)
        True
    """
    if not capability or not isinstance(capability, str):
        logger.warning(f"Invalid capability: {capability}")
        return []

    return [
        template for template in _TEMPLATE_REGISTRY.values() if capability in template.capabilities
    ]


def get_templates_by_tier(tier: str) -> list[AgentTemplate]:
    """Retrieve templates preferring a specific tier.

    Args:
        tier: Tier name ("CHEAP", "CAPABLE", "PREMIUM")

    Returns:
        List of templates preferring that tier

    Example:
        >>> templates = get_templates_by_tier("CAPABLE")
        >>> len(templates) > 0
        True
    """
    if tier not in AgentTemplate.ALLOWED_TIERS:
        logger.warning(f"Invalid tier: {tier}")
        return []

    return [
        template for template in _TEMPLATE_REGISTRY.values() if template.tier_preference == tier
    ]


# Pre-built agent templates

# Template 1: Test Coverage Analyzer
_TEST_COVERAGE_ANALYZER = AgentTemplate(
    id="test_coverage_analyzer",
    role="Test Coverage Expert",
    capabilities=["analyze_gaps", "suggest_tests", "validate_coverage"],
    tier_preference="CAPABLE",
    tools=["coverage_analyzer", "ast_parser"],
    default_instructions=(
        "You are a test coverage expert. Analyze the codebase to:\n"
        "1. Identify test coverage gaps\n"
        "2. Suggest specific tests to improve coverage\n"
        "3. Validate that coverage meets quality gates\n"
        "Focus on high-value test cases that improve code quality."
    ),
    quality_gates={"min_coverage": 80, "min_quality_score": 7},
    resource_requirements=ResourceRequirements(
        min_tokens=2000,
        max_tokens=15000,
        timeout_seconds=600,
        memory_mb=1024,
    ),
)

# Template 2: Security Auditor
_SECURITY_AUDITOR = AgentTemplate(
    id="security_auditor",
    role="Security Auditor",
    capabilities=[
        "vulnerability_scan",
        "threat_modeling",
        "compliance_check",
    ],
    tier_preference="PREMIUM",
    tools=["security_scanner", "bandit", "dependency_checker"],
    default_instructions=(
        "You are a security auditor. Perform comprehensive security analysis:\n"
        "1. Scan for common vulnerabilities (OWASP Top 10)\n"
        "2. Perform threat modeling for critical components\n"
        "3. Verify compliance with security standards\n"
        "4. Generate remediation plan for findings\n"
        "Prioritize critical and high-severity issues."
    ),
    quality_gates={
        "max_critical_issues": 0,
        "max_high_issues": 0,
        "min_compliance_score": 90,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=5000,
        max_tokens=30000,
        timeout_seconds=900,
        memory_mb=2048,
    ),
)

# Template 3: Code Reviewer
_CODE_REVIEWER = AgentTemplate(
    id="code_reviewer",
    role="Code Quality Reviewer",
    capabilities=[
        "code_review",
        "quality_assessment",
        "best_practices_check",
    ],
    tier_preference="CAPABLE",
    tools=["ast_parser", "complexity_analyzer", "style_checker"],
    default_instructions=(
        "You are a code quality reviewer. Review code for:\n"
        "1. Code quality and maintainability\n"
        "2. Adherence to best practices\n"
        "3. Potential bugs and edge cases\n"
        "4. Performance considerations\n"
        "Provide actionable feedback with specific examples."
    ),
    quality_gates={
        "min_quality_score": 7,
        "max_complexity": 15,
        "min_test_coverage": 80,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=3000,
        max_tokens=20000,
        timeout_seconds=600,
        memory_mb=1024,
    ),
)

# Template 4: Documentation Writer
_DOCUMENTATION_WRITER = AgentTemplate(
    id="documentation_writer",
    role="Documentation Writer",
    capabilities=[
        "generate_docs",
        "check_completeness",
        "update_examples",
    ],
    tier_preference="CHEAP",
    tools=["ast_parser", "doc_generator"],
    default_instructions=(
        "You are a documentation writer. Create clear, comprehensive docs:\n"
        "1. Generate API documentation from code\n"
        "2. Write usage examples and tutorials\n"
        "3. Update existing documentation for consistency\n"
        "4. Verify all public APIs are documented\n"
        "Focus on clarity and usefulness for developers."
    ),
    quality_gates={
        "min_doc_coverage": 100,
        "min_example_count": 3,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=1000,
        max_tokens=10000,
        timeout_seconds=300,
        memory_mb=512,
    ),
)

# Template 5: Performance Optimizer
_PERFORMANCE_OPTIMIZER = AgentTemplate(
    id="performance_optimizer",
    role="Performance Optimizer",
    capabilities=[
        "profile_code",
        "identify_bottlenecks",
        "suggest_optimizations",
    ],
    tier_preference="CAPABLE",
    tools=["profiler", "complexity_analyzer", "benchmark_runner"],
    default_instructions=(
        "You are a performance optimizer. Analyze and improve performance:\n"
        "1. Profile code to identify bottlenecks\n"
        "2. Analyze time and space complexity\n"
        "3. Suggest specific optimizations\n"
        "4. Validate improvements with benchmarks\n"
        "Focus on high-impact optimizations with measurable results."
    ),
    quality_gates={
        "min_performance_improvement": 20,
        "max_regression_percent": 5,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=2000,
        max_tokens=15000,
        timeout_seconds=900,
        memory_mb=2048,
    ),
)

# Template 6: Architecture Analyst
_ARCHITECTURE_ANALYST = AgentTemplate(
    id="architecture_analyst",
    role="Architecture Analyst",
    capabilities=[
        "analyze_architecture",
        "identify_patterns",
        "suggest_improvements",
    ],
    tier_preference="PREMIUM",
    tools=["dependency_analyzer", "pattern_detector", "metrics_collector"],
    default_instructions=(
        "You are an architecture analyst. Analyze system architecture:\n"
        "1. Map dependencies and component relationships\n"
        "2. Identify architectural patterns and anti-patterns\n"
        "3. Assess scalability and maintainability\n"
        "4. Suggest architectural improvements\n"
        "Focus on long-term maintainability and system evolution."
    ),
    quality_gates={
        "max_circular_dependencies": 0,
        "min_modularity_score": 7,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=5000,
        max_tokens=30000,
        timeout_seconds=900,
        memory_mb=2048,
    ),
)

# Template 7: Refactoring Specialist
_REFACTORING_SPECIALIST = AgentTemplate(
    id="refactoring_specialist",
    role="Refactoring Specialist",
    capabilities=[
        "identify_code_smells",
        "suggest_refactorings",
        "validate_changes",
    ],
    tier_preference="CAPABLE",
    tools=[
        "ast_parser",
        "complexity_analyzer",
        "duplication_detector",
    ],
    default_instructions=(
        "You are a refactoring specialist. Improve code structure:\n"
        "1. Identify code smells and technical debt\n"
        "2. Suggest specific refactorings\n"
        "3. Ensure behavior preservation\n"
        "4. Validate improvements with tests\n"
        "Focus on improving maintainability without changing behavior."
    ),
    quality_gates={
        "max_duplication_percent": 5,
        "max_complexity": 10,
        "min_test_coverage": 90,
    },
    resource_requirements=ResourceRequirements(
        min_tokens=2000,
        max_tokens=15000,
        timeout_seconds=600,
        memory_mb=1024,
    ),
)


# Register all pre-built templates
_register_template(_TEST_COVERAGE_ANALYZER)
_register_template(_SECURITY_AUDITOR)
_register_template(_CODE_REVIEWER)
_register_template(_DOCUMENTATION_WRITER)
_register_template(_PERFORMANCE_OPTIMIZER)
_register_template(_ARCHITECTURE_ANALYST)
_register_template(_REFACTORING_SPECIALIST)


logger.info(f"Registered {len(_TEMPLATE_REGISTRY)} agent templates")
