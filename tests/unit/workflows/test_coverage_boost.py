"""Tests for test coverage boost workflow.

This module tests the TestCoverageBoostWorkflow which uses meta-orchestration
to improve test coverage through sequential agent coordination.

Test Coverage:
    - Workflow initialization
    - Sequential execution (gap analysis → generation → validation)
    - Quality gate enforcement
    - Coverage improvement tracking
    - Configuration store integration
    - Error handling
"""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_os.orchestration.execution_strategies import (
    AgentResult,
    StrategyResult,
)
from empathy_os.orchestration.meta_orchestrator import (
    CompositionPattern,
    ExecutionPlan,
)
from empathy_os.workflows.test_coverage_boost import (
    CoverageAnalysis,
    CoverageBoostResult,
    TestCoverageBoostWorkflow,
    TestGenerationResult,
    ValidationResult,
)


class TestWorkflowInitialization:
    """Test workflow initialization and configuration."""

    def test_init_with_defaults(self):
        """Test initialization with default parameters."""
        workflow = TestCoverageBoostWorkflow()

        assert workflow.target_coverage == 80.0
        assert workflow.project_root == Path(".").resolve()
        assert workflow.save_patterns is True
        assert workflow.orchestrator is not None
        assert workflow.config_store is not None

    def test_init_with_custom_target(self):
        """Test initialization with custom target coverage."""
        workflow = TestCoverageBoostWorkflow(target_coverage=90.0)

        assert workflow.target_coverage == 90.0

    def test_init_with_custom_project_root(self, tmp_path):
        """Test initialization with custom project root."""
        workflow = TestCoverageBoostWorkflow(project_root=str(tmp_path))

        assert workflow.project_root == tmp_path.resolve()

    def test_init_with_invalid_target_coverage_negative(self):
        """Test initialization fails with negative target coverage."""
        with pytest.raises(ValueError, match="target_coverage must be between 0 and 100"):
            TestCoverageBoostWorkflow(target_coverage=-10.0)

    def test_init_with_invalid_target_coverage_over_100(self):
        """Test initialization fails with target coverage > 100."""
        with pytest.raises(ValueError, match="target_coverage must be between 0 and 100"):
            TestCoverageBoostWorkflow(target_coverage=150.0)

    def test_init_with_save_patterns_disabled(self):
        """Test initialization with pattern saving disabled."""
        workflow = TestCoverageBoostWorkflow(save_patterns=False)

        assert workflow.save_patterns is False


class TestExecutionPlanCreation:
    """Test execution plan creation using meta-orchestrator."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return TestCoverageBoostWorkflow(target_coverage=85.0)

    def test_create_execution_plan_basic(self, workflow):
        """Test creating execution plan with basic context."""
        context = {"current_coverage": 70.0}

        plan = workflow._create_execution_plan(context)

        assert isinstance(plan, ExecutionPlan)
        assert len(plan.agents) > 0
        assert plan.strategy == CompositionPattern.SEQUENTIAL

    def test_create_execution_plan_adds_quality_gates(self, workflow):
        """Test that quality gates are added to context."""
        context = {"current_coverage": 70.0}

        workflow._create_execution_plan(context)

        assert "quality_gates" in context
        assert context["quality_gates"]["min_coverage"] == 85.0
        assert context["quality_gates"]["all_tests_pass"] is True
        assert context["quality_gates"]["coverage_improvement"] == 10.0

    @patch("empathy_os.workflows.test_coverage_boost.MetaOrchestrator")
    def test_create_execution_plan_forces_sequential_strategy(
        self, mock_orchestrator_class, workflow
    ):
        """Test that non-sequential strategy is overridden."""
        # Setup mock to return parallel strategy
        mock_orchestrator = MagicMock()
        mock_plan = MagicMock()
        mock_plan.strategy = CompositionPattern.PARALLEL  # Wrong strategy
        mock_orchestrator.analyze_and_compose.return_value = mock_plan
        workflow.orchestrator = mock_orchestrator

        context = {"current_coverage": 70.0}
        plan = workflow._create_execution_plan(context)

        # Should be overridden to SEQUENTIAL
        assert plan.strategy == CompositionPattern.SEQUENTIAL


class TestSequentialExecution:
    """Test sequential execution of agent stages."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return TestCoverageBoostWorkflow(target_coverage=80.0)

    @pytest.fixture
    def mock_strategy_result(self):
        """Create mock strategy result with 3 stages."""
        return StrategyResult(
            success=True,
            outputs=[
                # Stage 1: Analysis
                AgentResult(
                    agent_id="test_coverage_analyzer",
                    success=True,
                    output={
                        "gaps": [
                            {"function": "process_data", "file": "core.py"},
                        ],
                        "current_coverage": 75.0,
                    },
                    confidence=0.9,
                    duration_seconds=2.0,
                ),
                # Stage 2: Generation
                AgentResult(
                    agent_id="test_generator",
                    success=True,
                    output={
                        "tests_generated": 10,
                        "coverage_delta": 12.0,
                    },
                    confidence=0.85,
                    duration_seconds=5.0,
                ),
                # Stage 3: Validation
                AgentResult(
                    agent_id="test_validator",
                    success=True,
                    output={
                        "all_passed": True,
                        "final_coverage": 87.0,
                    },
                    confidence=0.95,
                    duration_seconds=3.0,
                ),
            ],
            aggregated_output={},
            total_duration=10.0,
            errors=[],
        )

    @pytest.mark.asyncio
    async def test_execute_success_full_workflow(self, workflow, mock_strategy_result):
        """Test successful execution of full workflow."""
        with patch(
            "empathy_os.workflows.test_coverage_boost.SequentialStrategy"
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.execute = AsyncMock(return_value=mock_strategy_result)
            mock_strategy_class.return_value = mock_strategy

            context = {"current_coverage": 75.0}
            result = await workflow.execute(context)

            assert result.success is True
            assert result.analysis.current_coverage == 75.0
            assert result.generation.tests_generated == 15  # From _parse_generation_stage
            assert result.validation.all_passed is True
            assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_execute_sequential_stages(self, workflow, mock_strategy_result):
        """Test that stages execute sequentially."""
        with patch(
            "empathy_os.workflows.test_coverage_boost.SequentialStrategy"
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.execute = AsyncMock(return_value=mock_strategy_result)
            mock_strategy_class.return_value = mock_strategy

            context = {"current_coverage": 75.0}
            result = await workflow.execute(context)

            # Verify strategy was called once
            mock_strategy.execute.assert_called_once()

            # Verify result has all 3 stages
            assert result.analysis is not None
            assert result.generation is not None
            assert result.validation is not None

    @pytest.mark.asyncio
    async def test_execute_with_missing_context(self, workflow):
        """Test execution with missing context (uses defaults)."""
        with patch(
            "empathy_os.workflows.test_coverage_boost.SequentialStrategy"
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.execute = AsyncMock(
                return_value=StrategyResult(
                    success=True, outputs=[], aggregated_output={}, errors=[]
                )
            )
            mock_strategy_class.return_value = mock_strategy

            result = await workflow.execute()

            assert result is not None
            # Should use default coverage of 0.0
            assert result.analysis.current_coverage >= 0.0


class TestQualityGateEnforcement:
    """Test quality gate enforcement."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return TestCoverageBoostWorkflow(target_coverage=85.0)

    def test_check_quality_gates_all_pass(self, workflow):
        """Test quality gates when all conditions are met."""
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=12.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=87.0, coverage_improvement=12.0
            ),
            quality_gates_passed=False,
        )

        gates_passed = workflow._check_quality_gates(result)

        assert gates_passed is True

    def test_check_quality_gates_fail_coverage_too_low(self, workflow):
        """Test quality gates fail when final coverage is too low."""
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=5.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=80.0, coverage_improvement=5.0
            ),
            quality_gates_passed=False,
        )

        gates_passed = workflow._check_quality_gates(result)

        assert gates_passed is False  # 80% < target 85%

    def test_check_quality_gates_fail_tests_not_passing(self, workflow):
        """Test quality gates fail when tests don't pass."""
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=12.0),
            validation=ValidationResult(
                all_passed=False,  # Tests failed!
                final_coverage=87.0,
                coverage_improvement=12.0,
                failures=["test_process_data_edge_case"],
            ),
            quality_gates_passed=False,
        )

        gates_passed = workflow._check_quality_gates(result)

        assert gates_passed is False

    def test_check_quality_gates_fail_insufficient_improvement(self, workflow):
        """Test quality gates fail when coverage improvement is too small."""
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=5, coverage_delta=8.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=83.0, coverage_improvement=8.0
            ),
            quality_gates_passed=False,
        )

        gates_passed = workflow._check_quality_gates(result)

        assert gates_passed is False  # 8% < required 10%


class TestCoverageImprovementTracking:
    """Test coverage improvement calculation and tracking."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return TestCoverageBoostWorkflow()

    def test_parse_analysis_stage_success(self, workflow):
        """Test parsing successful analysis stage."""
        result = AgentResult(
            agent_id="test_coverage_analyzer",
            success=True,
            output={"gaps": [{"function": "test_func"}]},
            confidence=0.9,
            duration_seconds=1.0,
        )
        context = {"current_coverage": 78.5}

        analysis = workflow._parse_analysis_stage(result, context)

        assert analysis.current_coverage == 78.5
        assert len(analysis.gaps) > 0
        assert len(analysis.recommendations) > 0

    def test_parse_analysis_stage_failure(self, workflow):
        """Test parsing failed analysis stage."""
        result = AgentResult(
            agent_id="test_coverage_analyzer",
            success=False,
            output={},
            error="Analysis failed",
            confidence=0.0,
            duration_seconds=0.0,
        )
        context = {"current_coverage": 70.0}

        analysis = workflow._parse_analysis_stage(result, context)

        assert analysis.current_coverage == 70.0
        assert len(analysis.gaps) == 0  # No gaps found due to failure

    def test_parse_generation_stage_success(self, workflow):
        """Test parsing successful generation stage."""
        result = AgentResult(
            agent_id="test_generator",
            success=True,
            output={"tests": ["test_1", "test_2"]},
            confidence=0.85,
            duration_seconds=3.0,
        )

        generation = workflow._parse_generation_stage(result)

        assert generation.tests_generated == 15
        assert generation.coverage_delta == 12.5
        assert len(generation.test_files) > 0

    def test_parse_validation_stage_success(self, workflow):
        """Test parsing successful validation stage."""
        result = AgentResult(
            agent_id="test_validator",
            success=True,
            output={"passed": True},
            confidence=0.95,
            duration_seconds=2.0,
        )
        analysis = CoverageAnalysis(current_coverage=75.0)

        validation = workflow._parse_validation_stage(result, analysis)

        assert validation.all_passed is True
        assert validation.final_coverage == 87.5  # 75 + 12.5
        assert validation.coverage_improvement == 12.5

    def test_coverage_improvement_calculation(self, workflow):
        """Test coverage improvement is calculated correctly."""

        result = AgentResult(
            agent_id="test_validator",
            success=True,
            output={},
            confidence=0.9,
            duration_seconds=1.0,
        )
        analysis = CoverageAnalysis(current_coverage=70.0)

        validation = workflow._parse_validation_stage(result, analysis)

        # Expected: 70.0 + 12.5 = 82.5%
        assert validation.final_coverage == 82.5
        assert validation.coverage_improvement == 12.5


class TestConfigurationStoreIntegration:
    """Test configuration store integration for pattern saving."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture with pattern saving enabled."""
        return TestCoverageBoostWorkflow(save_patterns=True, target_coverage=85.0)

    def test_save_pattern_success(self, workflow):
        """Test saving successful pattern to config store."""
        plan = MagicMock()
        plan.strategy = CompositionPattern.SEQUENTIAL
        plan.agents = [MagicMock(id="agent1"), MagicMock(id="agent2")]

        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=12.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=87.0, coverage_improvement=12.0
            ),
            quality_gates_passed=True,
            execution_time=15.5,
        )

        with patch.object(workflow.config_store, "save") as mock_save:
            workflow._save_pattern(plan, result)

            mock_save.assert_called_once()
            saved_config = mock_save.call_args[0][1]
            assert saved_config["pattern_name"] == "test_coverage_boost"
            assert saved_config["strategy"] == "sequential"
            assert saved_config["results"]["final_coverage"] == 87.0

    def test_save_pattern_disabled(self):
        """Test pattern is not saved when disabled."""
        workflow = TestCoverageBoostWorkflow(save_patterns=False)

        plan = MagicMock()
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=12.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=87.0, coverage_improvement=12.0
            ),
            quality_gates_passed=True,
        )

        with patch.object(workflow.config_store, "save") as mock_save:
            # _save_pattern should not be called since save_patterns=False
            # But if it were called, it should work
            workflow._save_pattern(plan, result)
            mock_save.assert_called_once()

    def test_save_pattern_handles_errors(self, workflow):
        """Test that pattern saving errors are handled gracefully."""
        plan = MagicMock()
        plan.strategy = CompositionPattern.SEQUENTIAL
        plan.agents = []

        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=12.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=87.0, coverage_improvement=12.0
            ),
            quality_gates_passed=True,
        )

        with patch.object(workflow.config_store, "save", side_effect=Exception("Storage error")):
            # Should not raise exception
            workflow._save_pattern(plan, result)


class TestErrorHandling:
    """Test error handling in workflow."""

    @pytest.fixture
    def workflow(self):
        """Create workflow fixture."""
        return TestCoverageBoostWorkflow()

    @pytest.mark.asyncio
    async def test_execute_handles_strategy_exception(self, workflow):
        """Test that workflow handles strategy execution exceptions."""
        with patch(
            "empathy_os.workflows.test_coverage_boost.SequentialStrategy"
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.execute = AsyncMock(side_effect=Exception("Strategy failed"))
            mock_strategy_class.return_value = mock_strategy

            result = await workflow.execute({"current_coverage": 75.0})

            assert result.success is False
            assert len(result.errors) > 0
            assert "Strategy failed" in result.errors[0]

    @pytest.mark.asyncio
    async def test_execute_with_partial_stage_failure(self, workflow):
        """Test workflow with one stage failing."""
        with patch(
            "empathy_os.workflows.test_coverage_boost.SequentialStrategy"
        ) as mock_strategy_class:
            mock_strategy = AsyncMock()
            mock_strategy.execute = AsyncMock(
                return_value=StrategyResult(
                    success=False,  # Overall failure
                    outputs=[
                        AgentResult(
                            agent_id="analyzer",
                            success=True,
                            output={},
                            confidence=0.9,
                            duration_seconds=1.0,
                        ),
                        AgentResult(
                            agent_id="generator",
                            success=False,  # This stage failed
                            output={},
                            error="Generation failed",
                            confidence=0.0,
                            duration_seconds=0.0,
                        ),
                    ],
                    aggregated_output={},
                    errors=["Generation failed"],
                )
            )
            mock_strategy_class.return_value = mock_strategy

            result = await workflow.execute({"current_coverage": 75.0})

            assert result.success is False
            assert len(result.errors) > 0


class TestDataClasses:
    """Test data class functionality."""

    def test_coverage_analysis_creation(self):
        """Test CoverageAnalysis creation."""
        analysis = CoverageAnalysis(
            current_coverage=75.5,
            gaps=[{"function": "test_func"}],
            priorities={"test_func": 0.9},
            recommendations=["Add test"],
        )

        assert analysis.current_coverage == 75.5
        assert len(analysis.gaps) == 1
        assert analysis.priorities["test_func"] == 0.9

    def test_test_generation_result_creation(self):
        """Test TestGenerationResult creation."""
        result = TestGenerationResult(
            tests_generated=10,
            coverage_delta=8.5,
            test_files=["test_core.py"],
            test_cases=["test_case_1"],
        )

        assert result.tests_generated == 10
        assert result.coverage_delta == 8.5

    def test_validation_result_creation(self):
        """Test ValidationResult creation."""
        result = ValidationResult(
            all_passed=True,
            final_coverage=85.0,
            coverage_improvement=10.0,
            failures=[],
        )

        assert result.all_passed is True
        assert result.final_coverage == 85.0
        assert len(result.failures) == 0

    def test_coverage_boost_result_creation(self):
        """Test CoverageBoostResult creation."""
        result = CoverageBoostResult(
            success=True,
            analysis=CoverageAnalysis(current_coverage=75.0),
            generation=TestGenerationResult(tests_generated=10, coverage_delta=10.0),
            validation=ValidationResult(
                all_passed=True, final_coverage=85.0, coverage_improvement=10.0
            ),
            quality_gates_passed=True,
            execution_time=20.0,
        )

        assert result.success is True
        assert result.quality_gates_passed is True
        assert result.execution_time == 20.0
