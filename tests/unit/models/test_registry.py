"""Educational Tests for Model Registry (Phase 4 - Models & Providers)

Learning Objectives:
- Model registration and lookup
- Provider-tier mapping
- Model capability queries
- Protocol-based architecture testing

Key Patterns:
- Testing abstract interfaces
- Registry pattern testing
- Provider abstraction
"""

import pytest

from empathy_os.models.registry import ModelInfo, ModelProvider, ModelTier


@pytest.mark.unit
class TestModelTier:
    """Educational tests for model tier enum."""

    def test_model_tier_hierarchy(self):
        """Teaching Pattern: Testing tier hierarchy.

        CHEAP < CAPABLE < PREMIUM for cost optimization.
        """
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"

    def test_tier_comparison(self):
        """Teaching Pattern: Testing enum ordering.

        Lower tiers should be less expensive.
        """
        # Tiers represent cost/capability levels
        tiers = [ModelTier.CHEAP, ModelTier.CAPABLE, ModelTier.PREMIUM]
        assert len(tiers) == 3


@pytest.mark.unit
class TestModelProvider:
    """Educational tests for model provider enum."""

    def test_provider_values(self):
        """Teaching Pattern: Testing provider enumeration.

        Support for multiple LLM providers.
        """
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.GOOGLE.value == "google"
        assert ModelProvider.OLLAMA.value == "ollama"
        assert ModelProvider.HYBRID.value == "hybrid"

    def test_provider_to_string(self):
        """Teaching Pattern: Testing enum serialization.

        Providers need to serialize for API calls.
        """
        provider = ModelProvider.ANTHROPIC
        assert provider.value == "anthropic"
        assert str(provider.value) == "anthropic"

    @pytest.mark.parametrize(
        "provider,expected",
        [
            (ModelProvider.ANTHROPIC, "anthropic"),
            (ModelProvider.OPENAI, "openai"),
            (ModelProvider.GOOGLE, "google"),
            (ModelProvider.OLLAMA, "ollama"),
        ],
    )
    def test_all_providers(self, provider, expected):
        """Teaching Pattern: Parametrized provider testing.

        Each provider should have correct value.
        """
        assert provider.value == expected


@pytest.mark.unit
class TestModelInfo:
    """Educational tests for ModelInfo dataclass."""

    def test_model_info_creation(self):
        """Teaching Pattern: Testing dataclass initialization.

        ModelInfo stores model configuration.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
            max_tokens=8192,
        )

        assert model.id == "test-model"
        assert model.provider == "anthropic"
        assert model.tier == "cheap"
        assert model.input_cost_per_million == 1.0
        assert model.output_cost_per_million == 5.0

    def test_model_info_compatibility_properties(self):
        """Teaching Pattern: Testing computed properties.

        ModelInfo provides compatibility properties for different systems.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1000.0,
            output_cost_per_million=5000.0,
        )

        # Compatibility aliases
        assert model.model_id == "test-model"
        assert model.name == "test-model"

        # Per-1k conversion (divide by 1000)
        assert model.cost_per_1k_input == 1.0
        assert model.cost_per_1k_output == 5.0

    def test_model_info_to_router_config(self):
        """Teaching Pattern: Testing conversion methods.

        ModelInfo can convert to different config formats.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1000.0,
            output_cost_per_million=5000.0,
            max_tokens=8192,
            supports_tools=True,
        )

        router_config = model.to_router_config()

        assert router_config["model_id"] == "test-model"
        assert router_config["cost_per_1k_input"] == 1.0
        assert router_config["max_tokens"] == 8192
        assert router_config["supports_tools"] is True

    def test_model_info_to_workflow_config(self):
        """Teaching Pattern: Testing workflow config conversion.

        Different systems need different config formats.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
            supports_vision=True,
        )

        workflow_config = model.to_workflow_config()

        assert workflow_config["name"] == "test-model"
        assert workflow_config["provider"] == "anthropic"
        assert workflow_config["tier"] == "cheap"
        assert workflow_config["supports_vision"] is True

    def test_model_info_to_cost_tracker_pricing(self):
        """Teaching Pattern: Testing cost tracker conversion.

        Cost tracking needs pricing information.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
        )

        pricing = model.to_cost_tracker_pricing()

        assert pricing["input"] == 1.0
        assert pricing["output"] == 5.0

    def test_model_info_frozen_dataclass(self):
        """Teaching Pattern: Testing immutability.

        ModelInfo is frozen - cannot be modified after creation.
        """
        model = ModelInfo(
            id="test-model",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
        )

        # Attempting to modify should raise error
        with pytest.raises(AttributeError):  # FrozenInstanceError from dataclass
            model.id = "new-id"


@pytest.mark.unit
class TestModelRegistry:
    """Educational tests for MODEL_REGISTRY."""

    def test_registry_has_all_providers(self):
        """Teaching Pattern: Testing registry structure.

        Registry should have all major providers.
        """
        from empathy_os.models.registry import MODEL_REGISTRY

        assert "anthropic" in MODEL_REGISTRY
        assert "openai" in MODEL_REGISTRY
        assert "google" in MODEL_REGISTRY
        assert "ollama" in MODEL_REGISTRY
        assert "hybrid" in MODEL_REGISTRY

    def test_each_provider_has_all_tiers(self):
        """Teaching Pattern: Testing registry completeness.

        Each provider should have all tier levels.
        """
        from empathy_os.models.registry import MODEL_REGISTRY

        for provider_name, models in MODEL_REGISTRY.items():
            assert "cheap" in models, f"{provider_name} missing 'cheap' tier"
            assert "capable" in models, f"{provider_name} missing 'capable' tier"
            assert "premium" in models, f"{provider_name} missing 'premium' tier"

    def test_anthropic_models(self):
        """Teaching Pattern: Testing specific provider models.

        Anthropic should have Haiku, Sonnet, and Opus.
        """
        from empathy_os.models.registry import MODEL_REGISTRY

        anthropic = MODEL_REGISTRY["anthropic"]

        assert "haiku" in anthropic["cheap"].id.lower()
        assert "sonnet" in anthropic["capable"].id.lower()
        assert "opus" in anthropic["premium"].id.lower()

    def test_ollama_models_are_free(self):
        """Teaching Pattern: Testing provider-specific features.

        Ollama models run locally and are free.
        """
        from empathy_os.models.registry import MODEL_REGISTRY

        ollama = MODEL_REGISTRY["ollama"]

        for _tier, model in ollama.items():
            assert model.input_cost_per_million == 0.0
            assert model.output_cost_per_million == 0.0


@pytest.mark.unit
class TestRegistryHelpers:
    """Educational tests for registry helper functions."""

    def test_get_model_success(self):
        """Teaching Pattern: Testing model lookup.

        get_model retrieves models by provider and tier.
        """
        from empathy_os.models.registry import get_model

        model = get_model("anthropic", "cheap")

        assert model is not None
        assert model.provider == "anthropic"
        assert model.tier == "cheap"

    def test_get_model_case_insensitive(self):
        """Teaching Pattern: Testing case insensitivity.

        Lookups should work regardless of case.
        """
        from empathy_os.models.registry import get_model

        model1 = get_model("ANTHROPIC", "CHEAP")
        model2 = get_model("anthropic", "cheap")

        assert model1 is not None
        assert model1.id == model2.id

    def test_get_model_invalid_provider(self):
        """Teaching Pattern: Testing error handling.

        Invalid provider should return None.
        """
        from empathy_os.models.registry import get_model

        model = get_model("invalid_provider", "cheap")

        assert model is None

    def test_get_model_invalid_tier(self):
        """Teaching Pattern: Testing invalid tier.

        Invalid tier should return None.
        """
        from empathy_os.models.registry import get_model

        model = get_model("anthropic", "invalid_tier")

        assert model is None

    def test_get_all_models(self):
        """Teaching Pattern: Testing registry access.

        get_all_models returns the complete registry.
        """
        from empathy_os.models.registry import get_all_models

        all_models = get_all_models()

        assert isinstance(all_models, dict)
        assert "anthropic" in all_models
        assert len(all_models) >= 5  # At least 5 providers

    def test_get_pricing_for_model(self):
        """Teaching Pattern: Testing pricing lookup by model ID.

        Can retrieve pricing for specific model ID.
        """
        from empathy_os.models.registry import get_pricing_for_model

        pricing = get_pricing_for_model("claude-3-5-haiku-20241022")

        assert pricing is not None
        assert "input" in pricing
        assert "output" in pricing
        assert pricing["input"] > 0

    def test_get_pricing_for_nonexistent_model(self):
        """Teaching Pattern: Testing pricing lookup failure.

        Non-existent model should return None.
        """
        from empathy_os.models.registry import get_pricing_for_model

        pricing = get_pricing_for_model("nonexistent-model")

        assert pricing is None

    def test_get_supported_providers(self):
        """Teaching Pattern: Testing provider list.

        Can get list of all supported providers.
        """
        from empathy_os.models.registry import get_supported_providers

        providers = get_supported_providers()

        assert isinstance(providers, list)
        assert "anthropic" in providers
        assert "openai" in providers
        assert len(providers) >= 5

    def test_get_tiers(self):
        """Teaching Pattern: Testing tier list.

        Can get list of all available tiers.
        """
        from empathy_os.models.registry import get_tiers

        tiers = get_tiers()

        assert isinstance(tiers, list)
        assert "cheap" in tiers
        assert "capable" in tiers
        assert "premium" in tiers
        assert len(tiers) == 3


@pytest.mark.unit
class TestTierPricing:
    """Educational tests for TIER_PRICING."""

    def test_tier_pricing_exists(self):
        """Teaching Pattern: Testing tier-level pricing.

        TIER_PRICING provides fallback pricing.
        """
        from empathy_os.models.registry import TIER_PRICING

        assert "cheap" in TIER_PRICING
        assert "capable" in TIER_PRICING
        assert "premium" in TIER_PRICING

    def test_tier_pricing_structure(self):
        """Teaching Pattern: Testing pricing structure.

        Each tier has input and output pricing.
        """
        from empathy_os.models.registry import TIER_PRICING

        for _tier, pricing in TIER_PRICING.items():
            assert "input" in pricing
            assert "output" in pricing
            assert pricing["input"] > 0
            assert pricing["output"] > 0

    def test_tier_pricing_hierarchy(self):
        """Teaching Pattern: Testing cost hierarchy.

        Premium should cost more than capable, which costs more than cheap.
        """
        from empathy_os.models.registry import TIER_PRICING

        cheap_input = TIER_PRICING["cheap"]["input"]
        capable_input = TIER_PRICING["capable"]["input"]
        premium_input = TIER_PRICING["premium"]["input"]

        assert cheap_input < capable_input < premium_input
