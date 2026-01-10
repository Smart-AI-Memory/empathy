"""Meta-orchestrator for intelligent agent composition.

This module implements the core orchestration logic that analyzes tasks,
selects appropriate agents, and chooses composition patterns.

Security:
    - All inputs validated before processing
    - No eval() or exec() usage
    - Agent selection based on whitelisted templates

Example:
    >>> orchestrator = MetaOrchestrator()
    >>> plan = orchestrator.analyze_and_compose(
    ...     task="Boost test coverage to 90%",
    ...     context={"current_coverage": 75}
    ... )
    >>> print(plan.strategy)
    sequential
    >>> print([a.role for a in plan.agents])
    ['Test Coverage Expert', 'Test Generation Specialist', 'Quality Assurance Validator']
"""

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from .agent_templates import AgentTemplate, get_template, get_templates_by_capability

logger = logging.getLogger(__name__)


class TaskComplexity(Enum):
    """Task complexity classification."""

    SIMPLE = "simple"  # Single agent, straightforward
    MODERATE = "moderate"  # 2-3 agents, some coordination
    COMPLEX = "complex"  # 4+ agents, multi-phase execution


class TaskDomain(Enum):
    """Task domain classification."""

    TESTING = "testing"
    SECURITY = "security"
    CODE_QUALITY = "code_quality"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"
    ARCHITECTURE = "architecture"
    REFACTORING = "refactoring"
    GENERAL = "general"


class CompositionPattern(Enum):
    """Available composition patterns (grammar rules)."""

    SEQUENTIAL = "sequential"  # A → B → C
    PARALLEL = "parallel"  # A || B || C
    DEBATE = "debate"  # A ⇄ B ⇄ C → Synthesis
    TEACHING = "teaching"  # Junior → Expert validation
    REFINEMENT = "refinement"  # Draft → Review → Polish
    ADAPTIVE = "adaptive"  # Classifier → Specialist


@dataclass
class TaskRequirements:
    """Extracted requirements from task analysis.

    Attributes:
        complexity: Task complexity level
        domain: Primary task domain
        capabilities_needed: List of capabilities required
        parallelizable: Whether task can be parallelized
        quality_gates: Quality thresholds to enforce
        context: Additional context for customization
    """

    complexity: TaskComplexity
    domain: TaskDomain
    capabilities_needed: list[str]
    parallelizable: bool = False
    quality_gates: dict[str, Any] = field(default_factory=dict)
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    """Plan for agent execution.

    Attributes:
        agents: List of agents to execute
        strategy: Composition pattern to use
        quality_gates: Quality thresholds to enforce
        estimated_cost: Estimated execution cost
        estimated_duration: Estimated time in seconds
    """

    agents: list[AgentTemplate]
    strategy: CompositionPattern
    quality_gates: dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_duration: int = 0


class MetaOrchestrator:
    """Intelligent task analyzer and agent composition engine.

    The meta-orchestrator analyzes tasks to determine requirements,
    selects appropriate agents, and chooses optimal composition patterns.

    Example:
        >>> orchestrator = MetaOrchestrator()
        >>> plan = orchestrator.analyze_and_compose(
        ...     task="Prepare for v3.12.0 release",
        ...     context={"version": "3.12.0"}
        ... )
    """

    # Keyword patterns for task analysis
    COMPLEXITY_KEYWORDS = {
        TaskComplexity.SIMPLE: [
            "format",
            "lint",
            "check",
            "validate",
            "document",
        ],
        TaskComplexity.MODERATE: [
            "improve",
            "refactor",
            "optimize",
            "test",
            "review",
        ],
        TaskComplexity.COMPLEX: [
            "release",
            "migrate",
            "redesign",
            "architecture",
            "prepare",
        ],
    }

    DOMAIN_KEYWORDS = {
        TaskDomain.TESTING: [
            "test",
            "coverage",
            "pytest",
            "unit test",
            "integration test",
        ],
        TaskDomain.SECURITY: [
            "security",
            "vulnerability",
            "audit",
            "penetration",
            "threat",
        ],
        TaskDomain.CODE_QUALITY: [
            "quality",
            "code review",
            "lint",
            "best practices",
            "maintainability",
        ],
        TaskDomain.DOCUMENTATION: [
            "docs",
            "documentation",
            "readme",
            "guide",
            "tutorial",
        ],
        TaskDomain.PERFORMANCE: [
            "performance",
            "optimize",
            "speed",
            "benchmark",
            "profile",
        ],
        TaskDomain.ARCHITECTURE: [
            "architecture",
            "design",
            "structure",
            "pattern",
            "dependency",
        ],
        TaskDomain.REFACTORING: [
            "refactor",
            "cleanup",
            "simplify",
            "restructure",
            "debt",
        ],
    }

    # Capability mapping by domain
    DOMAIN_CAPABILITIES = {
        TaskDomain.TESTING: [
            "analyze_gaps",
            "suggest_tests",
            "validate_coverage",
        ],
        TaskDomain.SECURITY: [
            "vulnerability_scan",
            "threat_modeling",
            "compliance_check",
        ],
        TaskDomain.CODE_QUALITY: [
            "code_review",
            "quality_assessment",
            "best_practices_check",
        ],
        TaskDomain.DOCUMENTATION: [
            "generate_docs",
            "check_completeness",
            "update_examples",
        ],
        TaskDomain.PERFORMANCE: [
            "profile_code",
            "identify_bottlenecks",
            "suggest_optimizations",
        ],
        TaskDomain.ARCHITECTURE: [
            "analyze_architecture",
            "identify_patterns",
            "suggest_improvements",
        ],
        TaskDomain.REFACTORING: [
            "identify_code_smells",
            "suggest_refactorings",
            "validate_changes",
        ],
    }

    def __init__(self):
        """Initialize meta-orchestrator."""
        logger.info("MetaOrchestrator initialized")

    def analyze_and_compose(
        self, task: str, context: dict[str, Any] | None = None
    ) -> ExecutionPlan:
        """Analyze task and create execution plan.

        This is the main entry point for the meta-orchestrator.

        Args:
            task: Task description (e.g., "Boost test coverage to 90%")
            context: Optional context dictionary

        Returns:
            ExecutionPlan with agents and strategy

        Raises:
            ValueError: If task is invalid

        Example:
            >>> orchestrator = MetaOrchestrator()
            >>> plan = orchestrator.analyze_and_compose(
            ...     task="Improve test coverage",
            ...     context={"current_coverage": 75}
            ... )
        """
        if not task or not isinstance(task, str):
            raise ValueError("task must be a non-empty string")

        context = context or {}
        logger.info(f"Analyzing task: {task}")

        # Step 1: Analyze task requirements
        requirements = self._analyze_task(task, context)
        logger.info(
            f"Task analysis: complexity={requirements.complexity.value}, "
            f"domain={requirements.domain.value}, "
            f"capabilities={requirements.capabilities_needed}"
        )

        # Step 2: Select appropriate agents
        agents = self._select_agents(requirements)
        logger.info(f"Selected {len(agents)} agents: {[a.id for a in agents]}")

        # Step 3: Choose composition pattern
        strategy = self._choose_composition_pattern(requirements, agents)
        logger.info(f"Selected strategy: {strategy.value}")

        # Step 4: Create execution plan
        plan = ExecutionPlan(
            agents=agents,
            strategy=strategy,
            quality_gates=requirements.quality_gates,
            estimated_cost=self._estimate_cost(agents),
            estimated_duration=self._estimate_duration(agents, strategy),
        )

        return plan

    def _analyze_task(self, task: str, context: dict[str, Any]) -> TaskRequirements:
        """Analyze task to extract requirements.

        Args:
            task: Task description
            context: Context dictionary

        Returns:
            TaskRequirements with extracted information
        """
        task_lower = task.lower()

        # Determine complexity
        complexity = self._classify_complexity(task_lower)

        # Determine domain
        domain = self._classify_domain(task_lower)

        # Extract needed capabilities
        capabilities = self._extract_capabilities(domain, context)

        # Determine if parallelizable
        parallelizable = self._is_parallelizable(task_lower, complexity)

        # Extract quality gates from context
        quality_gates = context.get("quality_gates", {})

        return TaskRequirements(
            complexity=complexity,
            domain=domain,
            capabilities_needed=capabilities,
            parallelizable=parallelizable,
            quality_gates=quality_gates,
            context=context,
        )

    def _classify_complexity(self, task_lower: str) -> TaskComplexity:
        """Classify task complexity based on keywords.

        Args:
            task_lower: Lowercase task description

        Returns:
            TaskComplexity classification
        """
        # Check for complex keywords first (most specific)
        for keyword in self.COMPLEXITY_KEYWORDS[TaskComplexity.COMPLEX]:
            if keyword in task_lower:
                return TaskComplexity.COMPLEX

        # Check for moderate keywords
        for keyword in self.COMPLEXITY_KEYWORDS[TaskComplexity.MODERATE]:
            if keyword in task_lower:
                return TaskComplexity.MODERATE

        # Check for simple keywords
        for keyword in self.COMPLEXITY_KEYWORDS[TaskComplexity.SIMPLE]:
            if keyword in task_lower:
                return TaskComplexity.SIMPLE

        # Default to moderate if no keywords match
        return TaskComplexity.MODERATE

    def _classify_domain(self, task_lower: str) -> TaskDomain:
        """Classify task domain based on keywords.

        Args:
            task_lower: Lowercase task description

        Returns:
            TaskDomain classification
        """
        # Score each domain based on keyword matches
        domain_scores: dict[TaskDomain, int] = dict.fromkeys(TaskDomain, 0)

        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in task_lower:
                    domain_scores[domain] += 1

        # Return domain with highest score
        max_score = max(domain_scores.values())
        if max_score > 0:
            for domain, score in domain_scores.items():
                if score == max_score:
                    return domain

        # Default to general if no keywords match
        return TaskDomain.GENERAL

    def _extract_capabilities(self, domain: TaskDomain, context: dict[str, Any]) -> list[str]:
        """Extract needed capabilities based on domain.

        Args:
            domain: Task domain
            context: Context dictionary

        Returns:
            List of capability names
        """
        # Get default capabilities for domain
        capabilities = self.DOMAIN_CAPABILITIES.get(domain, []).copy()

        # Add capabilities from context if provided
        if "capabilities" in context:
            additional = context["capabilities"]
            if isinstance(additional, list):
                capabilities.extend(additional)

        return capabilities

    def _is_parallelizable(self, task_lower: str, complexity: TaskComplexity) -> bool:
        """Determine if task can be parallelized.

        Args:
            task_lower: Lowercase task description
            complexity: Task complexity

        Returns:
            True if task can be parallelized
        """
        # Keywords indicating parallel execution
        parallel_keywords = [
            "release",
            "audit",
            "check",
            "validate",
            "review",
        ]

        # Keywords indicating sequential execution
        sequential_keywords = [
            "migrate",
            "refactor",
            "generate",
            "create",
        ]

        # Check for sequential keywords first (higher precedence)
        for keyword in sequential_keywords:
            if keyword in task_lower:
                return False

        # Check for parallel keywords
        for keyword in parallel_keywords:
            if keyword in task_lower:
                return True

        # Complex tasks often benefit from parallel execution
        return complexity == TaskComplexity.COMPLEX

    def _select_agents(self, requirements: TaskRequirements) -> list[AgentTemplate]:
        """Select appropriate agents based on requirements.

        Args:
            requirements: Task requirements

        Returns:
            List of agent templates

        Raises:
            ValueError: If no agents match requirements
        """
        agents: list[AgentTemplate] = []

        # Select agents based on needed capabilities
        for capability in requirements.capabilities_needed:
            templates = get_templates_by_capability(capability)
            if templates:
                # Pick the first template with this capability
                # In future: could rank by success rate, cost, etc.
                agent = templates[0]
                if agent not in agents:
                    agents.append(agent)

        # If no agents found, use domain-appropriate default
        if not agents:
            agents = self._get_default_agents(requirements.domain)

        if not agents:
            raise ValueError(f"No agents available for domain: {requirements.domain.value}")

        return agents

    def _get_default_agents(self, domain: TaskDomain) -> list[AgentTemplate]:
        """Get default agents for a domain.

        Args:
            domain: Task domain

        Returns:
            List of default agent templates
        """
        defaults = {
            TaskDomain.TESTING: ["test_coverage_analyzer"],
            TaskDomain.SECURITY: ["security_auditor"],
            TaskDomain.CODE_QUALITY: ["code_reviewer"],
            TaskDomain.DOCUMENTATION: ["documentation_writer"],
            TaskDomain.PERFORMANCE: ["performance_optimizer"],
            TaskDomain.ARCHITECTURE: ["architecture_analyst"],
            TaskDomain.REFACTORING: ["refactoring_specialist"],
        }

        template_ids = defaults.get(domain, ["code_reviewer"])
        agents = []
        for template_id in template_ids:
            template = get_template(template_id)
            if template:
                agents.append(template)

        return agents

    def _choose_composition_pattern(
        self, requirements: TaskRequirements, agents: list[AgentTemplate]
    ) -> CompositionPattern:
        """Choose optimal composition pattern.

        Args:
            requirements: Task requirements
            agents: Selected agents

        Returns:
            CompositionPattern to use
        """
        num_agents = len(agents)

        # Parallelizable tasks: use parallel strategy (check before single agent)
        if requirements.parallelizable:
            return CompositionPattern.PARALLEL

        # Security/architecture: benefit from multiple perspectives (even with 1 agent)
        if requirements.domain in [TaskDomain.SECURITY, TaskDomain.ARCHITECTURE]:
            return CompositionPattern.PARALLEL

        # Documentation: teaching pattern (cheap → validate → expert if needed)
        if requirements.domain == TaskDomain.DOCUMENTATION:
            return CompositionPattern.TEACHING

        # Refactoring: refinement pattern (identify → refactor → validate)
        if requirements.domain == TaskDomain.REFACTORING:
            return CompositionPattern.REFINEMENT

        # Single agent: sequential (after domain-specific patterns)
        if num_agents == 1:
            return CompositionPattern.SEQUENTIAL

        # Multiple agents with same capability: debate/consensus
        capabilities = [cap for agent in agents for cap in agent.capabilities]
        if len(capabilities) != len(set(capabilities)):
            # Duplicate capabilities detected → debate
            return CompositionPattern.DEBATE

        # Testing domain: typically sequential (analyze → generate → validate)
        if requirements.domain == TaskDomain.TESTING:
            return CompositionPattern.SEQUENTIAL

        # Complex tasks: adaptive routing
        if requirements.complexity == TaskComplexity.COMPLEX:
            return CompositionPattern.ADAPTIVE

        # Default: sequential
        return CompositionPattern.SEQUENTIAL

    def _estimate_cost(self, agents: list[AgentTemplate]) -> float:
        """Estimate execution cost based on agent tiers.

        Args:
            agents: List of agents

        Returns:
            Estimated cost in arbitrary units
        """
        tier_costs = {
            "CHEAP": 1.0,
            "CAPABLE": 3.0,
            "PREMIUM": 10.0,
        }

        total_cost = 0.0
        for agent in agents:
            total_cost += tier_costs.get(agent.tier_preference, 3.0)

        return total_cost

    def _estimate_duration(self, agents: list[AgentTemplate], strategy: CompositionPattern) -> int:
        """Estimate execution duration in seconds.

        Args:
            agents: List of agents
            strategy: Composition pattern

        Returns:
            Estimated duration in seconds
        """
        # Get max timeout from agents
        max_timeout = max(
            (agent.resource_requirements.timeout_seconds for agent in agents),
            default=300,
        )

        # Sequential: sum of timeouts
        if strategy == CompositionPattern.SEQUENTIAL:
            return sum(agent.resource_requirements.timeout_seconds for agent in agents)

        # Parallel: max timeout
        if strategy == CompositionPattern.PARALLEL:
            return max_timeout

        # Debate: multiple rounds, estimate 2x max timeout
        if strategy == CompositionPattern.DEBATE:
            return max_timeout * 2

        # Teaching: initial attempt + possible expert review
        if strategy == CompositionPattern.TEACHING:
            return int(max_timeout * 1.5)

        # Refinement: 3 passes (draft → review → polish)
        if strategy == CompositionPattern.REFINEMENT:
            return max_timeout * 3

        # Adaptive: classification + specialist
        if strategy == CompositionPattern.ADAPTIVE:
            return int(max_timeout * 1.2)

        # Default: max timeout
        return max_timeout
