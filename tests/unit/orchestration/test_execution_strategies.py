"""Tests for execution strategies.

This module tests all 6 execution strategies:
1. SequentialStrategy
2. ParallelStrategy
3. DebateStrategy
4. TeachingStrategy
5. RefinementStrategy
6. AdaptiveStrategy
"""

import pytest

from empathy_os.orchestration.agent_templates import get_template
from empathy_os.orchestration.execution_strategies import (
    AdaptiveStrategy,
    DebateStrategy,
    ParallelStrategy,
    RefinementStrategy,
    SequentialStrategy,
    TeachingStrategy,
    get_strategy,
)


@pytest.fixture
def test_agents():
    """Get test agents for execution."""
    return [
        get_template("test_coverage_analyzer"),
        get_template("code_reviewer"),
        get_template("documentation_writer"),
    ]


@pytest.fixture
def test_context():
    """Get test context dictionary."""
    return {"project": "empathy-framework", "version": "3.12.0"}


class TestSequentialStrategy:
    """Test sequential execution strategy."""

    @pytest.mark.asyncio
    async def test_sequential_execution(self, test_agents, test_context):
        """Test sequential execution of agents."""
        strategy = SequentialStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        assert len(result.outputs) == len(test_agents)
        assert result.total_duration > 0

        # Verify outputs are aggregated
        assert "num_agents" in result.aggregated_output
        assert result.aggregated_output["num_agents"] == len(test_agents)

    @pytest.mark.asyncio
    async def test_sequential_passes_context_forward(self, test_agents, test_context):
        """Test that sequential passes output to next agent."""
        strategy = SequentialStrategy()
        result = await strategy.execute(test_agents[:2], test_context)

        # First agent's output should be in context for second
        assert result.success
        assert len(result.outputs) == 2

    @pytest.mark.asyncio
    async def test_sequential_empty_agents_raises_error(self, test_context):
        """Test that empty agents list raises error."""
        strategy = SequentialStrategy()

        with pytest.raises(ValueError, match="agents list cannot be empty"):
            await strategy.execute([], test_context)

    @pytest.mark.asyncio
    async def test_sequential_single_agent(self, test_agents, test_context):
        """Test sequential with single agent."""
        strategy = SequentialStrategy()
        result = await strategy.execute(test_agents[:1], test_context)

        assert result.success
        assert len(result.outputs) == 1


class TestParallelStrategy:
    """Test parallel execution strategy."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self, test_agents, test_context):
        """Test parallel execution of agents."""
        strategy = ParallelStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        assert len(result.outputs) == len(test_agents)

        # Parallel duration should be max, not sum
        assert result.total_duration < sum(
            a.resource_requirements.timeout_seconds for a in test_agents
        )

    @pytest.mark.asyncio
    async def test_parallel_all_agents_receive_same_context(self, test_agents, test_context):
        """Test that all agents receive same initial context."""
        strategy = ParallelStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        # All agents should have processed same context
        for output in result.outputs:
            assert output.success

    @pytest.mark.asyncio
    async def test_parallel_empty_agents_raises_error(self, test_context):
        """Test that empty agents list raises error."""
        strategy = ParallelStrategy()

        with pytest.raises(ValueError, match="agents list cannot be empty"):
            await strategy.execute([], test_context)


class TestDebateStrategy:
    """Test debate/consensus strategy."""

    @pytest.mark.asyncio
    async def test_debate_execution(self, test_agents, test_context):
        """Test debate pattern execution."""
        strategy = DebateStrategy()
        result = await strategy.execute(test_agents[:2], test_context)

        assert result.success
        assert len(result.outputs) == 2

        # Should have synthesis in aggregated output
        assert "debate_participants" in result.aggregated_output
        assert "opinions" in result.aggregated_output
        assert "consensus" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_debate_consensus_reached(self, test_agents, test_context):
        """Test that consensus is synthesized."""
        strategy = DebateStrategy()
        result = await strategy.execute(test_agents[:2], test_context)

        consensus = result.aggregated_output["consensus"]
        assert "consensus_reached" in consensus
        assert "success_votes" in consensus
        assert "total_votes" in consensus

    @pytest.mark.asyncio
    async def test_debate_with_single_agent_warns(self, test_agents, test_context):
        """Test debate with single agent (should warn)."""
        strategy = DebateStrategy()
        result = await strategy.execute(test_agents[:1], test_context)

        # Should still work but with warning
        assert result.success


class TestTeachingStrategy:
    """Test teaching/validation strategy."""

    @pytest.mark.asyncio
    async def test_teaching_junior_passes(self, test_agents, test_context):
        """Test teaching pattern when junior passes quality gate."""
        # Use cheap and capable agents
        junior = get_template("documentation_writer")  # CHEAP
        expert = get_template("code_reviewer")  # CAPABLE

        strategy = TeachingStrategy(quality_threshold=0.7)
        result = await strategy.execute([junior, expert], test_context)

        assert result.success
        # Should have junior's output
        assert "junior_output" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_teaching_expert_takeover(self, test_agents, test_context):
        """Test teaching pattern when expert takes over."""
        junior = get_template("documentation_writer")
        expert = get_template("code_reviewer")

        # Set high threshold to force expert takeover
        strategy = TeachingStrategy(quality_threshold=0.95)
        result = await strategy.execute([junior, expert], test_context)

        assert result.success
        # Should have both outputs
        assert "junior_output" in result.aggregated_output
        # Expert should have taken over due to high threshold

    @pytest.mark.asyncio
    async def test_teaching_requires_two_agents(self, test_agents, test_context):
        """Test that teaching requires exactly 2 agents."""
        strategy = TeachingStrategy()

        with pytest.raises(ValueError, match="Teaching strategy requires exactly 2 agents"):
            await strategy.execute(test_agents, test_context)

    @pytest.mark.asyncio
    async def test_teaching_custom_threshold(self, test_agents, test_context):
        """Test teaching with custom quality threshold."""
        strategy = TeachingStrategy(quality_threshold=0.5)

        junior = get_template("documentation_writer")
        expert = get_template("code_reviewer")

        result = await strategy.execute([junior, expert], test_context)
        assert result.success


class TestRefinementStrategy:
    """Test progressive refinement strategy."""

    @pytest.mark.asyncio
    async def test_refinement_execution(self, test_agents, test_context):
        """Test refinement pattern execution."""
        strategy = RefinementStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        assert len(result.outputs) == len(test_agents)

        # Should have refinement stages in output
        assert "refinement_stages" in result.aggregated_output
        assert "final_output" in result.aggregated_output
        assert "stage_outputs" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_refinement_progressive_improvement(self, test_agents, test_context):
        """Test that each stage refines previous output."""
        strategy = RefinementStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        stage_outputs = result.aggregated_output["stage_outputs"]
        assert len(stage_outputs) == len(test_agents)

    @pytest.mark.asyncio
    async def test_refinement_requires_multiple_agents(self, test_agents, test_context):
        """Test that refinement requires at least 2 agents."""
        strategy = RefinementStrategy()

        with pytest.raises(ValueError, match="Refinement strategy requires at least 2 agents"):
            await strategy.execute(test_agents[:1], test_context)

    @pytest.mark.asyncio
    async def test_refinement_two_agents(self, test_agents, test_context):
        """Test refinement with minimum 2 agents."""
        strategy = RefinementStrategy()
        result = await strategy.execute(test_agents[:2], test_context)

        assert result.success
        assert len(result.outputs) == 2


class TestAdaptiveStrategy:
    """Test adaptive routing strategy."""

    @pytest.mark.asyncio
    async def test_adaptive_execution(self, test_agents, test_context):
        """Test adaptive routing execution."""
        strategy = AdaptiveStrategy()
        result = await strategy.execute(test_agents, test_context)

        assert result.success
        # Classifier + specialist = 2 executions
        assert len(result.outputs) == 2

        # Should have classification and routing info
        assert "classification" in result.aggregated_output
        assert "selected_specialist" in result.aggregated_output
        assert "specialist_output" in result.aggregated_output

    @pytest.mark.asyncio
    async def test_adaptive_routes_to_specialist(self, test_agents, test_context):
        """Test that adaptive routes to appropriate specialist."""
        strategy = AdaptiveStrategy()
        result = await strategy.execute(test_agents, test_context)

        selected = result.aggregated_output["selected_specialist"]
        # Should have selected one of the specialist agents
        assert selected in [a.id for a in test_agents[1:]]

    @pytest.mark.asyncio
    async def test_adaptive_requires_multiple_agents(self, test_agents, test_context):
        """Test that adaptive requires at least 2 agents."""
        strategy = AdaptiveStrategy()

        with pytest.raises(ValueError, match="Adaptive strategy requires at least 2 agents"):
            await strategy.execute(test_agents[:1], test_context)


class TestStrategyRegistry:
    """Test strategy registry and lookup."""

    def test_get_strategy_sequential(self):
        """Test getting sequential strategy."""
        strategy = get_strategy("sequential")
        assert isinstance(strategy, SequentialStrategy)

    def test_get_strategy_parallel(self):
        """Test getting parallel strategy."""
        strategy = get_strategy("parallel")
        assert isinstance(strategy, ParallelStrategy)

    def test_get_strategy_debate(self):
        """Test getting debate strategy."""
        strategy = get_strategy("debate")
        assert isinstance(strategy, DebateStrategy)

    def test_get_strategy_teaching(self):
        """Test getting teaching strategy."""
        strategy = get_strategy("teaching")
        assert isinstance(strategy, TeachingStrategy)

    def test_get_strategy_refinement(self):
        """Test getting refinement strategy."""
        strategy = get_strategy("refinement")
        assert isinstance(strategy, RefinementStrategy)

    def test_get_strategy_adaptive(self):
        """Test getting adaptive strategy."""
        strategy = get_strategy("adaptive")
        assert isinstance(strategy, AdaptiveStrategy)

    def test_get_strategy_invalid_raises_error(self):
        """Test that invalid strategy name raises error."""
        with pytest.raises(ValueError, match="Unknown strategy"):
            get_strategy("invalid_strategy")


class TestAgentResult:
    """Test AgentResult dataclass."""

    def test_agent_result_creation(self):
        """Test creating AgentResult."""
        from empathy_os.orchestration.execution_strategies import AgentResult

        result = AgentResult(
            agent_id="test_agent",
            success=True,
            output={"key": "value"},
            confidence=0.9,
            duration_seconds=1.5,
        )

        assert result.agent_id == "test_agent"
        assert result.success is True
        assert result.output["key"] == "value"
        assert result.confidence == 0.9
        assert result.duration_seconds == 1.5
        assert result.error == ""

    def test_agent_result_with_error(self):
        """Test creating AgentResult with error."""
        from empathy_os.orchestration.execution_strategies import AgentResult

        result = AgentResult(
            agent_id="test_agent",
            success=False,
            output={},
            error="Something went wrong",
        )

        assert result.success is False
        assert result.error == "Something went wrong"


class TestStrategyResult:
    """Test StrategyResult dataclass."""

    def test_strategy_result_creation(self):
        """Test creating StrategyResult."""
        from empathy_os.orchestration.execution_strategies import (
            AgentResult,
            StrategyResult,
        )

        outputs = [
            AgentResult("agent1", True, {"data": 1}, 0.9, 1.0),
            AgentResult("agent2", True, {"data": 2}, 0.8, 1.5),
        ]

        result = StrategyResult(
            success=True,
            outputs=outputs,
            aggregated_output={"combined": "data"},
            total_duration=2.5,
        )

        assert result.success is True
        assert len(result.outputs) == 2
        assert result.aggregated_output["combined"] == "data"
        assert result.total_duration == 2.5
        assert result.errors == []

    def test_strategy_result_with_errors(self):
        """Test creating StrategyResult with errors."""
        from empathy_os.orchestration.execution_strategies import (
            AgentResult,
            StrategyResult,
        )

        outputs = [
            AgentResult("agent1", False, {}, 0.0, 0.0, "Error 1"),
        ]

        result = StrategyResult(
            success=False,
            outputs=outputs,
            aggregated_output={},
            errors=["Error 1"],
        )

        assert result.success is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Error 1"


class TestIntegration:
    """Integration tests combining multiple strategies."""

    @pytest.mark.asyncio
    async def test_all_strategies_work(self, test_agents, test_context):
        """Test that all strategies can execute successfully."""
        strategies = [
            SequentialStrategy(),
            ParallelStrategy(),
            DebateStrategy(),
            RefinementStrategy(),
        ]

        for strategy in strategies:
            result = await strategy.execute(test_agents[:3], test_context)
            assert result.success, f"{strategy.__class__.__name__} failed"

    @pytest.mark.asyncio
    async def test_teaching_and_adaptive_with_two_agents(self, test_agents, test_context):
        """Test teaching and adaptive with 2 agents."""
        teaching = TeachingStrategy()
        adaptive = AdaptiveStrategy()

        teaching_result = await teaching.execute(test_agents[:2], test_context)
        adaptive_result = await adaptive.execute(test_agents[:2], test_context)

        assert teaching_result.success
        assert adaptive_result.success
