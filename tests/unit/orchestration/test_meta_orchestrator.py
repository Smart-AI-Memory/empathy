"""Tests for meta-orchestrator.

This module tests the MetaOrchestrator class, including:
- Task analysis and requirement extraction
- Agent selection based on capabilities
- Composition pattern selection
- End-to-end orchestration
"""

import pytest

from empathy_os.orchestration.meta_orchestrator import (
    CompositionPattern,
    ExecutionPlan,
    MetaOrchestrator,
    TaskComplexity,
    TaskDomain,
    TaskRequirements,
)


class TestTaskRequirements:
    """Test TaskRequirements dataclass."""

    def test_task_requirements_creation(self):
        """Test creating TaskRequirements."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.MODERATE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["analyze_gaps", "suggest_tests"],
            parallelizable=False,
            quality_gates={"min_coverage": 80},
            context={"current_coverage": 75},
        )

        assert requirements.complexity == TaskComplexity.MODERATE
        assert requirements.domain == TaskDomain.TESTING
        assert len(requirements.capabilities_needed) == 2
        assert not requirements.parallelizable
        assert requirements.quality_gates["min_coverage"] == 80

    def test_task_requirements_defaults(self):
        """Test TaskRequirements with defaults."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["test"],
        )

        assert not requirements.parallelizable
        assert requirements.quality_gates == {}
        assert requirements.context == {}


class TestMetaOrchestratorInit:
    """Test MetaOrchestrator initialization."""

    def test_initialization(self):
        """Test that orchestrator initializes successfully."""
        orchestrator = MetaOrchestrator()
        assert orchestrator is not None

    def test_keyword_patterns_defined(self):
        """Test that keyword patterns are defined."""
        orchestrator = MetaOrchestrator()

        # Check complexity keywords
        assert TaskComplexity.SIMPLE in orchestrator.COMPLEXITY_KEYWORDS
        assert TaskComplexity.MODERATE in orchestrator.COMPLEXITY_KEYWORDS
        assert TaskComplexity.COMPLEX in orchestrator.COMPLEXITY_KEYWORDS

        # Check domain keywords
        assert TaskDomain.TESTING in orchestrator.DOMAIN_KEYWORDS
        assert TaskDomain.SECURITY in orchestrator.DOMAIN_KEYWORDS
        assert TaskDomain.CODE_QUALITY in orchestrator.DOMAIN_KEYWORDS


class TestTaskAnalysis:
    """Test task analysis methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_classify_complexity_simple(self):
        """Test classifying simple tasks."""
        task = "format the code and check style"
        complexity = self.orchestrator._classify_complexity(task)
        assert complexity == TaskComplexity.SIMPLE

    def test_classify_complexity_moderate(self):
        """Test classifying moderate tasks."""
        task = "improve test coverage for the authentication module"
        complexity = self.orchestrator._classify_complexity(task)
        assert complexity == TaskComplexity.MODERATE

    def test_classify_complexity_complex(self):
        """Test classifying complex tasks."""
        task = "prepare for v3.12.0 release with full validation"
        complexity = self.orchestrator._classify_complexity(task)
        assert complexity == TaskComplexity.COMPLEX

    def test_classify_complexity_default(self):
        """Test default complexity classification."""
        task = "do something unspecified"
        complexity = self.orchestrator._classify_complexity(task)
        assert complexity == TaskComplexity.MODERATE

    def test_classify_domain_testing(self):
        """Test classifying testing domain."""
        task = "boost test coverage to 90%"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.TESTING

    def test_classify_domain_security(self):
        """Test classifying security domain."""
        task = "perform security audit and vulnerability scan"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.SECURITY

    def test_classify_domain_code_quality(self):
        """Test classifying code quality domain."""
        task = "code review for maintainability and best practices"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.CODE_QUALITY

    def test_classify_domain_documentation(self):
        """Test classifying documentation domain."""
        task = "update documentation and write a tutorial"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.DOCUMENTATION

    def test_classify_domain_performance(self):
        """Test classifying performance domain."""
        task = "optimize code performance and reduce memory usage"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.PERFORMANCE

    def test_classify_domain_architecture(self):
        """Test classifying architecture domain."""
        task = "review system architecture and design patterns"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.ARCHITECTURE

    def test_classify_domain_refactoring(self):
        """Test classifying refactoring domain."""
        task = "refactor the code to reduce technical debt"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.REFACTORING

    def test_classify_domain_default(self):
        """Test default domain classification."""
        task = "do something generic"
        domain = self.orchestrator._classify_domain(task)
        assert domain == TaskDomain.GENERAL

    def test_extract_capabilities_from_domain(self):
        """Test extracting capabilities from domain."""
        capabilities = self.orchestrator._extract_capabilities(TaskDomain.TESTING, {})
        assert "analyze_gaps" in capabilities
        assert "suggest_tests" in capabilities
        assert "validate_coverage" in capabilities

    def test_extract_capabilities_with_context(self):
        """Test extracting capabilities with context override."""
        context = {"capabilities": ["custom_capability"]}
        capabilities = self.orchestrator._extract_capabilities(TaskDomain.TESTING, context)
        assert "analyze_gaps" in capabilities
        assert "custom_capability" in capabilities

    def test_is_parallelizable_release_task(self):
        """Test that release tasks are parallelizable."""
        task = "prepare for release"
        result = self.orchestrator._is_parallelizable(task, TaskComplexity.COMPLEX)
        assert result is True

    def test_is_parallelizable_sequential_task(self):
        """Test that migration tasks are sequential."""
        task = "migrate database schema"
        result = self.orchestrator._is_parallelizable(task, TaskComplexity.COMPLEX)
        assert result is False

    def test_is_parallelizable_complex_default(self):
        """Test that complex tasks default to parallel."""
        task = "complex operation"
        result = self.orchestrator._is_parallelizable(task, TaskComplexity.COMPLEX)
        assert result is True

    def test_analyze_task_end_to_end(self):
        """Test full task analysis."""
        task = "boost test coverage to 90%"
        context = {"current_coverage": 75}

        requirements = self.orchestrator._analyze_task(task, context)

        assert requirements.complexity == TaskComplexity.MODERATE
        assert requirements.domain == TaskDomain.TESTING
        assert len(requirements.capabilities_needed) > 0
        assert requirements.context["current_coverage"] == 75


class TestAgentSelection:
    """Test agent selection methods."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_select_agents_by_capability(self):
        """Test selecting agents based on capabilities."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.MODERATE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["analyze_gaps", "suggest_tests"],
        )

        agents = self.orchestrator._select_agents(requirements)

        assert len(agents) > 0
        # Should select test coverage analyzer
        assert any("test" in a.id.lower() for a in agents)

    def test_select_agents_security_domain(self):
        """Test selecting agents for security domain."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.SECURITY,
            capabilities_needed=["vulnerability_scan"],
        )

        agents = self.orchestrator._select_agents(requirements)

        assert len(agents) > 0
        assert any("security" in a.id.lower() for a in agents)

    def test_select_agents_no_matches_uses_default(self):
        """Test that default agents are used when no matches."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.CODE_QUALITY,
            capabilities_needed=["nonexistent_capability"],
        )

        agents = self.orchestrator._select_agents(requirements)

        # Should fall back to default for domain
        assert len(agents) > 0

    def test_get_default_agents_testing(self):
        """Test getting default agents for testing domain."""
        agents = self.orchestrator._get_default_agents(TaskDomain.TESTING)
        assert len(agents) > 0
        assert agents[0].id == "test_coverage_analyzer"

    def test_get_default_agents_security(self):
        """Test getting default agents for security domain."""
        agents = self.orchestrator._get_default_agents(TaskDomain.SECURITY)
        assert len(agents) > 0
        assert agents[0].id == "security_auditor"


class TestCompositionPatternSelection:
    """Test composition pattern selection."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_choose_pattern_single_agent_sequential(self):
        """Test that single agent uses sequential pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["analyze_gaps"],
        )
        agents = self.orchestrator._select_agents(requirements)

        # If only 1 agent, should be sequential
        if len(agents) == 1:
            pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
            assert pattern == CompositionPattern.SEQUENTIAL

    def test_choose_pattern_parallelizable_parallel(self):
        """Test that parallelizable tasks use parallel pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.SECURITY,
            capabilities_needed=["vulnerability_scan"],
            parallelizable=True,
        )
        agents = self.orchestrator._select_agents(requirements)

        pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
        assert pattern == CompositionPattern.PARALLEL

    def test_choose_pattern_testing_sequential(self):
        """Test that testing domain uses sequential pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.MODERATE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["analyze_gaps", "suggest_tests"],
            parallelizable=False,
        )
        agents = self.orchestrator._select_agents(requirements)

        pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
        assert pattern == CompositionPattern.SEQUENTIAL

    def test_choose_pattern_security_parallel(self):
        """Test that security domain can use parallel pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.SECURITY,
            capabilities_needed=["vulnerability_scan"],
            parallelizable=False,
        )
        agents = self.orchestrator._select_agents(requirements)

        # Security domain prefers parallel
        pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
        assert pattern == CompositionPattern.PARALLEL

    def test_choose_pattern_documentation_teaching(self):
        """Test that documentation domain uses teaching pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.DOCUMENTATION,
            capabilities_needed=["generate_docs"],
            parallelizable=False,
        )
        agents = self.orchestrator._select_agents(requirements)

        pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
        assert pattern == CompositionPattern.TEACHING

    def test_choose_pattern_refactoring_refinement(self):
        """Test that refactoring domain uses refinement pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.MODERATE,
            domain=TaskDomain.REFACTORING,
            capabilities_needed=["identify_code_smells"],
            parallelizable=False,
        )
        agents = self.orchestrator._select_agents(requirements)

        pattern = self.orchestrator._choose_composition_pattern(requirements, agents)
        assert pattern == CompositionPattern.REFINEMENT


class TestCostEstimation:
    """Test cost and duration estimation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_estimate_cost_cheap_agent(self):
        """Test cost estimation for cheap tier agent."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.DOCUMENTATION,
            capabilities_needed=["generate_docs"],
        )
        agents = self.orchestrator._select_agents(requirements)

        cost = self.orchestrator._estimate_cost(agents)
        assert cost > 0
        # Documentation writer is CHEAP tier
        assert cost <= 5.0

    def test_estimate_cost_premium_agent(self):
        """Test cost estimation for premium tier agent."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.SECURITY,
            capabilities_needed=["vulnerability_scan"],
        )
        agents = self.orchestrator._select_agents(requirements)

        cost = self.orchestrator._estimate_cost(agents)
        assert cost > 0
        # Security auditor is PREMIUM tier
        assert cost >= 10.0

    def test_estimate_duration_sequential(self):
        """Test duration estimation for sequential pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.MODERATE,
            domain=TaskDomain.TESTING,
            capabilities_needed=["analyze_gaps", "suggest_tests"],
        )
        agents = self.orchestrator._select_agents(requirements)
        strategy = CompositionPattern.SEQUENTIAL

        duration = self.orchestrator._estimate_duration(agents, strategy)
        assert duration > 0
        # Sequential sums all agent timeouts
        total_timeout = sum(a.resource_requirements.timeout_seconds for a in agents)
        assert duration == total_timeout

    def test_estimate_duration_parallel(self):
        """Test duration estimation for parallel pattern."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.COMPLEX,
            domain=TaskDomain.SECURITY,
            capabilities_needed=["vulnerability_scan"],
        )
        agents = self.orchestrator._select_agents(requirements)
        strategy = CompositionPattern.PARALLEL

        duration = self.orchestrator._estimate_duration(agents, strategy)
        assert duration > 0
        # Parallel takes max timeout
        max_timeout = max(a.resource_requirements.timeout_seconds for a in agents)
        assert duration == max_timeout


class TestAnalyzeAndCompose:
    """Test end-to-end orchestration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_analyze_and_compose_basic(self):
        """Test basic analyze and compose."""
        task = "improve test coverage"
        plan = self.orchestrator.analyze_and_compose(task)

        assert isinstance(plan, ExecutionPlan)
        assert len(plan.agents) > 0
        assert isinstance(plan.strategy, CompositionPattern)
        assert plan.estimated_cost > 0
        assert plan.estimated_duration > 0

    def test_analyze_and_compose_with_context(self):
        """Test analyze and compose with context."""
        task = "boost test coverage to 90%"
        context = {
            "current_coverage": 75,
            "quality_gates": {"min_coverage": 90},
        }

        plan = self.orchestrator.analyze_and_compose(task, context)

        assert isinstance(plan, ExecutionPlan)
        assert plan.quality_gates["min_coverage"] == 90

    def test_analyze_and_compose_testing_task(self):
        """Test orchestration for testing task."""
        task = "improve test coverage for authentication module"
        plan = self.orchestrator.analyze_and_compose(task)

        assert len(plan.agents) > 0
        # Should select test-related agents
        assert any("test" in a.id.lower() for a in plan.agents)

    def test_analyze_and_compose_security_task(self):
        """Test orchestration for security task."""
        task = "perform comprehensive security audit"
        plan = self.orchestrator.analyze_and_compose(task)

        assert len(plan.agents) > 0
        # Should select security agent
        assert any("security" in a.id.lower() for a in plan.agents)

    def test_analyze_and_compose_release_task(self):
        """Test orchestration for release preparation."""
        task = "prepare for v3.12.0 release"
        plan = self.orchestrator.analyze_and_compose(task)

        assert len(plan.agents) > 0
        # Complex release task should be parallel
        assert plan.strategy == CompositionPattern.PARALLEL

    def test_analyze_and_compose_documentation_task(self):
        """Test orchestration for documentation task."""
        task = "update API documentation"
        plan = self.orchestrator.analyze_and_compose(task)

        assert len(plan.agents) > 0
        # Documentation should use teaching pattern
        assert plan.strategy == CompositionPattern.TEACHING

    def test_analyze_and_compose_refactoring_task(self):
        """Test orchestration for refactoring task."""
        task = "refactor code to reduce complexity"
        plan = self.orchestrator.analyze_and_compose(task)

        assert len(plan.agents) > 0
        # Refactoring should use refinement pattern
        assert plan.strategy == CompositionPattern.REFINEMENT

    def test_analyze_and_compose_invalid_task(self):
        """Test that invalid task raises error."""
        with pytest.raises(ValueError, match="task must be a non-empty string"):
            self.orchestrator.analyze_and_compose("")

        with pytest.raises(ValueError, match="task must be a non-empty string"):
            self.orchestrator.analyze_and_compose(None)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_empty_capabilities_uses_defaults(self):
        """Test that empty capabilities uses domain defaults."""
        requirements = TaskRequirements(
            complexity=TaskComplexity.SIMPLE,
            domain=TaskDomain.TESTING,
            capabilities_needed=[],
        )

        agents = self.orchestrator._select_agents(requirements)
        assert len(agents) > 0

    def test_general_domain_uses_code_reviewer(self):
        """Test that general domain defaults to code reviewer."""
        agents = self.orchestrator._get_default_agents(TaskDomain.GENERAL)
        assert len(agents) > 0

    def test_multiple_domain_keywords_highest_score(self):
        """Test that multiple keywords score correctly."""
        task = "test security vulnerabilities and check code quality"
        domain = self.orchestrator._classify_domain(task)

        # Should pick domain with most keyword matches
        assert domain in [
            TaskDomain.TESTING,
            TaskDomain.SECURITY,
            TaskDomain.CODE_QUALITY,
        ]


class TestIntegration:
    """Integration tests for complete workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.orchestrator = MetaOrchestrator()

    def test_test_coverage_boost_workflow(self):
        """Test complete test coverage boost workflow."""
        task = "boost test coverage from 75% to 90%"
        context = {"current_coverage": 75, "target_coverage": 90}

        plan = self.orchestrator.analyze_and_compose(task, context)

        # Verify plan structure
        assert len(plan.agents) > 0
        assert plan.strategy in [
            CompositionPattern.SEQUENTIAL,
            CompositionPattern.REFINEMENT,
        ]
        assert plan.estimated_cost > 0
        assert plan.estimated_duration > 0

    def test_release_preparation_workflow(self):
        """Test complete release preparation workflow."""
        task = "prepare for v3.12.0 release with full quality checks"
        context = {
            "version": "3.12.0",
            "quality_gates": {
                "min_coverage": 80,
                "max_critical_issues": 0,
            },
        }

        plan = self.orchestrator.analyze_and_compose(task, context)

        # Verify plan structure
        assert len(plan.agents) > 0
        # Release should be parallel for speed
        assert plan.strategy == CompositionPattern.PARALLEL
        assert plan.quality_gates["min_coverage"] == 80

    def test_security_audit_workflow(self):
        """Test complete security audit workflow."""
        task = "perform comprehensive security audit and threat modeling"

        plan = self.orchestrator.analyze_and_compose(task)

        # Verify plan structure
        assert len(plan.agents) > 0
        assert any("security" in a.id.lower() for a in plan.agents)
        # Security auditor is PREMIUM tier
        assert plan.estimated_cost >= 10.0
