"""Tests for ModelRouter

Tests the smart model routing for cost optimization.
"""

import pytest

from empathy_llm_toolkit.routing import ModelRouter, ModelTier, TaskRouting


class TestModelTier:
    """Tests for ModelTier enum."""

    def test_tier_values(self):
        """Test tier value assignments."""
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"


class TestTaskRouting:
    """Tests for TaskRouting mappings."""

    def test_cheap_tasks(self):
        """Test that cheap tasks route correctly."""
        cheap_tasks = ["summarize", "classify", "triage", "match_pattern"]

        for task in cheap_tasks:
            tier = TaskRouting.get_tier(task)
            assert tier == ModelTier.CHEAP, f"{task} should be CHEAP"

    def test_capable_tasks(self):
        """Test that capable tasks route correctly."""
        capable_tasks = ["generate_code", "fix_bug", "review_security", "write_tests"]

        for task in capable_tasks:
            tier = TaskRouting.get_tier(task)
            assert tier == ModelTier.CAPABLE, f"{task} should be CAPABLE"

    def test_premium_tasks(self):
        """Test that premium tasks route correctly."""
        premium_tasks = ["coordinate", "synthesize_results", "architectural_decision"]

        for task in premium_tasks:
            tier = TaskRouting.get_tier(task)
            assert tier == ModelTier.PREMIUM, f"{task} should be PREMIUM"

    def test_unknown_tasks_default_to_capable(self):
        """Test that unknown tasks default to capable."""
        tier = TaskRouting.get_tier("unknown_task_xyz")
        assert tier == ModelTier.CAPABLE

    def test_case_insensitive(self):
        """Test that routing is case insensitive."""
        assert TaskRouting.get_tier("SUMMARIZE") == ModelTier.CHEAP
        assert TaskRouting.get_tier("Fix_Bug") == ModelTier.CAPABLE
        assert TaskRouting.get_tier("COORDINATE") == ModelTier.PREMIUM

    def test_underscore_handling(self):
        """Test handling of underscores and hyphens."""
        assert TaskRouting.get_tier("fix-bug") == ModelTier.CAPABLE
        assert TaskRouting.get_tier("fix bug") == ModelTier.CAPABLE
        assert TaskRouting.get_tier("fix_bug") == ModelTier.CAPABLE


class TestModelRouter:
    """Tests for ModelRouter."""

    @pytest.fixture
    def router(self):
        """Create router for testing."""
        return ModelRouter()

    def test_default_provider_is_anthropic(self, router):
        """Test default provider."""
        model = router.route("summarize")
        assert "claude" in model.lower() or "haiku" in model.lower()

    def test_route_cheap_task(self, router):
        """Test routing cheap task to cheap model."""
        model = router.route("summarize")
        assert model == "claude-3-5-haiku-20241022"

    def test_route_capable_task(self, router):
        """Test routing capable task to capable model."""
        model = router.route("fix_bug")
        assert model == "claude-sonnet-4-20250514"

    def test_route_premium_task(self, router):
        """Test routing premium task to premium model."""
        model = router.route("coordinate")
        assert model == "claude-opus-4-5-20251101"  # Opus 4.5

    def test_route_with_openai_provider(self, router):
        """Test routing with OpenAI provider."""
        model = router.route("summarize", provider="openai")
        assert model == "gpt-4o-mini"

        model = router.route("fix_bug", provider="openai")
        assert model == "gpt-4o"

        model = router.route("coordinate", provider="openai")
        assert model == "o1"

    def test_route_with_ollama_provider(self, router):
        """Test routing with Ollama provider."""
        model = router.route("summarize", provider="ollama")
        assert model == "llama3.2:3b"

    def test_invalid_provider_raises_error(self, router):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError):
            router.route("summarize", provider="invalid_provider")

    def test_get_config(self, router):
        """Test getting full model config."""
        config = router.get_config("fix_bug")

        assert config.model_id == "claude-sonnet-4-20250514"
        assert config.cost_per_1k_input == 0.003
        assert config.cost_per_1k_output == 0.015
        assert config.max_tokens == 8192
        assert config.supports_tools is True

    def test_estimate_cost_cheap(self, router):
        """Test cost estimation for cheap tier."""
        cost = router.estimate_cost("summarize", input_tokens=10000, output_tokens=2000)

        # Haiku 3.5: $0.80/M input, $4.00/M output (unified registry pricing)
        expected = (10000 / 1000) * 0.0008 + (2000 / 1000) * 0.004
        assert cost == pytest.approx(expected, rel=0.01)

    def test_estimate_cost_capable(self, router):
        """Test cost estimation for capable tier."""
        cost = router.estimate_cost("fix_bug", input_tokens=5000, output_tokens=1000)

        # Sonnet: $3/M input, $15/M output
        expected = (5000 / 1000) * 0.003 + (1000 / 1000) * 0.015
        assert cost == pytest.approx(expected, rel=0.01)

    def test_estimate_cost_premium(self, router):
        """Test cost estimation for premium tier."""
        cost = router.estimate_cost("coordinate", input_tokens=10000, output_tokens=2000)

        # Opus: $15/M input, $75/M output
        expected = (10000 / 1000) * 0.015 + (2000 / 1000) * 0.075
        assert cost == pytest.approx(expected, rel=0.01)

    def test_compare_costs(self, router):
        """Test cost comparison across tiers."""
        costs = router.compare_costs("fix_bug", input_tokens=5000, output_tokens=1000)

        assert "cheap" in costs
        assert "capable" in costs
        assert "premium" in costs

        # Cheap should be cheapest
        assert costs["cheap"] < costs["capable"] < costs["premium"]

    def test_custom_routing(self):
        """Test custom task routing."""
        router = ModelRouter(custom_routing={"my_special_task": ModelTier.PREMIUM})

        tier = router.get_tier("my_special_task")
        assert tier == ModelTier.PREMIUM

        model = router.route("my_special_task")
        assert model == "claude-opus-4-5-20251101"  # Opus 4.5

    def test_add_task_routing(self, router):
        """Test adding custom routing dynamically."""
        router.add_task_routing("new_task", ModelTier.CHEAP)

        tier = router.get_tier("new_task")
        assert tier == ModelTier.CHEAP

    def test_calculate_savings_cheap_task(self, router):
        """Test savings calculation for cheap task."""
        savings = router.calculate_savings("summarize", input_tokens=10000, output_tokens=2000)

        assert savings["task_type"] == "summarize"
        assert savings["routed_tier"] == "cheap"
        assert savings["savings"] > 0
        assert savings["savings_percent"] > 0

    def test_calculate_savings_premium_task(self, router):
        """Test savings for premium task (no savings)."""
        savings = router.calculate_savings("coordinate", input_tokens=10000, output_tokens=2000)

        assert savings["routed_tier"] == "premium"
        assert savings["savings"] == 0
        assert savings["savings_percent"] == 0

    def test_get_supported_providers(self):
        """Test getting supported providers."""
        providers = ModelRouter.get_supported_providers()

        assert "anthropic" in providers
        assert "openai" in providers
        assert "ollama" in providers

    def test_get_all_tasks(self):
        """Test getting all known task types."""
        tasks = ModelRouter.get_all_tasks()

        assert "cheap" in tasks
        assert "capable" in tasks
        assert "premium" in tasks

        assert "summarize" in tasks["cheap"]
        assert "fix_bug" in tasks["capable"]
        assert "coordinate" in tasks["premium"]


class TestCostOptimization:
    """Integration tests for cost optimization scenarios."""

    @pytest.fixture
    def router(self):
        return ModelRouter()

    def test_multi_agent_cost_comparison(self, router):
        """Test cost comparison for multi-agent workflow."""
        # Simulate: 1 coordinator + 4 sub-agents

        # Without optimization (all Opus)
        unoptimized = router.estimate_cost(
            "coordinate",
            50000,
            5000,
        ) + 4 * router.estimate_cost(  # Coordinator
            "coordinate",
            30000,
            3000,
        )  # Sub-agents

        # With optimization (tiered)
        optimized = (
            router.estimate_cost("coordinate", 50000, 5000)  # Coordinator: Opus
            + router.estimate_cost("triage", 2000, 100)  # Triage: Haiku
            + 4 * router.estimate_cost("fix_bug", 30000, 3000)  # Sub-agents: Sonnet
        )

        # Should save significant amount
        savings_percent = (unoptimized - optimized) / unoptimized * 100
        assert savings_percent > 50, "Should save >50% with smart routing"

    def test_ollama_free_routing(self, router):
        """Test that Ollama routing is free."""
        cost = router.estimate_cost("fix_bug", 100000, 10000, provider="ollama")
        assert cost == 0.0, "Ollama should be free"

    def test_batch_task_optimization(self, router):
        """Test optimization for batch of tasks."""
        tasks = [
            ("summarize", 5000, 500),
            ("classify", 2000, 100),
            ("fix_bug", 10000, 2000),
            ("write_tests", 8000, 3000),
            ("coordinate", 20000, 4000),
        ]

        optimized_total = sum(router.estimate_cost(task, inp, out) for task, inp, out in tasks)

        # If all were premium
        premium_total = sum(router.estimate_cost("coordinate", inp, out) for _, inp, out in tasks)

        savings = premium_total - optimized_total
        assert savings > 0, "Batch should save with optimization"
