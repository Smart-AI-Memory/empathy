"""
Tests for Unified Model Registry

Verifies:
- All providers and tiers are present
- Pricing properties work correctly (per-1k and per-million)
- Helper functions return expected results
- Compatibility methods for ModelRouter and WorkflowConfig

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_os.models import (
    MODEL_REGISTRY,
    ModelInfo,
    ModelProvider,
    ModelTier,
    get_all_models,
    get_model,
    get_pricing_for_model,
)
from empathy_os.models.registry import TIER_PRICING, get_supported_providers, get_tiers


class TestModelTierEnum:
    """Tests for ModelTier enum."""

    def test_tier_values(self):
        """Verify tier enum values."""
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"

    def test_tier_count(self):
        """Verify we have exactly 3 tiers."""
        assert len(ModelTier) == 3


class TestModelProviderEnum:
    """Tests for ModelProvider enum."""

    def test_provider_values(self):
        """Verify provider enum values."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.OLLAMA.value == "ollama"
        assert ModelProvider.HYBRID.value == "hybrid"
        assert ModelProvider.CUSTOM.value == "custom"


class TestModelInfo:
    """Tests for ModelInfo dataclass."""

    def test_model_info_creation(self):
        """Test creating a ModelInfo instance."""
        info = ModelInfo(
            id="test-model",
            provider="test",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
            max_tokens=4096,
        )
        assert info.id == "test-model"
        assert info.provider == "test"
        assert info.tier == "cheap"

    def test_compatibility_properties(self):
        """Test model_id and name aliases."""
        info = ModelInfo(
            id="claude-test",
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.0,
            output_cost_per_million=15.0,
        )
        assert info.model_id == "claude-test"
        assert info.name == "claude-test"

    def test_pricing_conversion_per_1k(self):
        """Test per-million to per-1k conversion."""
        info = ModelInfo(
            id="test",
            provider="test",
            tier="cheap",
            input_cost_per_million=0.80,  # $0.80 per million
            output_cost_per_million=4.00,  # $4.00 per million
        )
        # Per-1k should be per-million / 1000
        assert info.cost_per_1k_input == pytest.approx(0.0008)
        assert info.cost_per_1k_output == pytest.approx(0.004)

    def test_to_router_config(self):
        """Test conversion to ModelRouter format."""
        info = ModelInfo(
            id="claude-haiku",
            provider="anthropic",
            tier="cheap",
            input_cost_per_million=0.80,
            output_cost_per_million=4.00,
            max_tokens=8192,
            supports_tools=True,
        )
        config = info.to_router_config()
        assert config["model_id"] == "claude-haiku"
        assert config["cost_per_1k_input"] == pytest.approx(0.0008)
        assert config["cost_per_1k_output"] == pytest.approx(0.004)
        assert config["max_tokens"] == 8192
        assert config["supports_tools"] is True

    def test_to_workflow_config(self):
        """Test conversion to WorkflowConfig format."""
        info = ModelInfo(
            id="claude-sonnet",
            provider="anthropic",
            tier="capable",
            input_cost_per_million=3.00,
            output_cost_per_million=15.00,
            max_tokens=8192,
            supports_vision=True,
            supports_tools=True,
        )
        config = info.to_workflow_config()
        assert config["name"] == "claude-sonnet"
        assert config["provider"] == "anthropic"
        assert config["tier"] == "capable"
        assert config["input_cost_per_million"] == 3.00
        assert config["output_cost_per_million"] == 15.00
        assert config["supports_vision"] is True

    def test_to_cost_tracker_pricing(self):
        """Test conversion to cost_tracker format."""
        info = ModelInfo(
            id="test",
            provider="test",
            tier="cheap",
            input_cost_per_million=0.80,
            output_cost_per_million=4.00,
        )
        pricing = info.to_cost_tracker_pricing()
        assert pricing["input"] == 0.80
        assert pricing["output"] == 4.00

    def test_frozen_dataclass(self):
        """Verify ModelInfo is immutable."""
        info = ModelInfo(
            id="test",
            provider="test",
            tier="cheap",
            input_cost_per_million=1.0,
            output_cost_per_million=5.0,
        )
        with pytest.raises(AttributeError):
            info.id = "modified"  # type: ignore


class TestModelRegistry:
    """Tests for MODEL_REGISTRY."""

    def test_all_providers_present(self):
        """Verify all expected providers are in registry."""
        expected = {"anthropic", "openai", "ollama", "hybrid"}
        assert set(MODEL_REGISTRY.keys()) == expected

    def test_all_tiers_present_for_each_provider(self):
        """Verify each provider has all three tiers."""
        expected_tiers = {"cheap", "capable", "premium"}
        for provider, tiers in MODEL_REGISTRY.items():
            assert set(tiers.keys()) == expected_tiers, f"Missing tiers for {provider}"

    def test_anthropic_models(self):
        """Verify Anthropic model configurations."""
        cheap = MODEL_REGISTRY["anthropic"]["cheap"]
        assert "haiku" in cheap.id.lower()
        assert cheap.input_cost_per_million == 0.80

        capable = MODEL_REGISTRY["anthropic"]["capable"]
        assert "sonnet" in capable.id.lower()
        assert capable.input_cost_per_million == 3.00

        premium = MODEL_REGISTRY["anthropic"]["premium"]
        assert "opus" in premium.id.lower()
        assert premium.input_cost_per_million == 15.00

    def test_openai_models(self):
        """Verify OpenAI model configurations."""
        cheap = MODEL_REGISTRY["openai"]["cheap"]
        assert cheap.id == "gpt-4o-mini"
        assert cheap.input_cost_per_million == 0.15

        capable = MODEL_REGISTRY["openai"]["capable"]
        assert capable.id == "gpt-4o"

        premium = MODEL_REGISTRY["openai"]["premium"]
        assert premium.id == "o1"
        assert premium.supports_tools is False  # o1 doesn't support tools

    def test_ollama_zero_cost(self):
        """Verify Ollama models have zero cost."""
        for _tier, info in MODEL_REGISTRY["ollama"].items():
            assert info.input_cost_per_million == 0.0
            assert info.output_cost_per_million == 0.0

    def test_hybrid_uses_best_models(self):
        """Verify hybrid uses cheapest/best from each provider."""
        cheap = MODEL_REGISTRY["hybrid"]["cheap"]
        assert cheap.id == "gpt-4o-mini"  # OpenAI for cheap
        assert cheap.provider == "openai"

        capable = MODEL_REGISTRY["hybrid"]["capable"]
        assert "sonnet" in capable.id.lower()  # Anthropic for capable
        assert capable.provider == "anthropic"

        premium = MODEL_REGISTRY["hybrid"]["premium"]
        assert "opus" in premium.id.lower()  # Anthropic for premium


class TestHelperFunctions:
    """Tests for registry helper functions."""

    def test_get_model_success(self):
        """Test getting a valid model."""
        model = get_model("anthropic", "cheap")
        assert model is not None
        assert model.id == "claude-3-5-haiku-20241022"

    def test_get_model_case_insensitive(self):
        """Test case insensitivity."""
        model1 = get_model("ANTHROPIC", "CHEAP")
        model2 = get_model("anthropic", "cheap")
        assert model1 == model2

    def test_get_model_invalid_provider(self):
        """Test getting model with invalid provider."""
        model = get_model("invalid", "cheap")
        assert model is None

    def test_get_model_invalid_tier(self):
        """Test getting model with invalid tier."""
        model = get_model("anthropic", "invalid")
        assert model is None

    def test_get_all_models(self):
        """Test get_all_models returns full registry."""
        all_models = get_all_models()
        assert all_models == MODEL_REGISTRY

    def test_get_pricing_for_model_found(self):
        """Test getting pricing for existing model."""
        pricing = get_pricing_for_model("claude-3-5-haiku-20241022")
        assert pricing is not None
        assert pricing["input"] == 0.80
        assert pricing["output"] == 4.00

    def test_get_pricing_for_model_not_found(self):
        """Test getting pricing for non-existent model."""
        pricing = get_pricing_for_model("non-existent-model")
        assert pricing is None

    def test_get_supported_providers(self):
        """Test getting supported providers list."""
        providers = get_supported_providers()
        assert "anthropic" in providers
        assert "openai" in providers
        assert "ollama" in providers
        assert "hybrid" in providers

    def test_get_tiers(self):
        """Test getting tiers list."""
        tiers = get_tiers()
        assert tiers == ["cheap", "capable", "premium"]


class TestTierPricing:
    """Tests for tier pricing aliases."""

    def test_tier_pricing_values(self):
        """Verify tier pricing matches Anthropic defaults."""
        assert TIER_PRICING["cheap"]["input"] == 0.80
        assert TIER_PRICING["cheap"]["output"] == 4.00

        assert TIER_PRICING["capable"]["input"] == 3.00
        assert TIER_PRICING["capable"]["output"] == 15.00

        assert TIER_PRICING["premium"]["input"] == 15.00
        assert TIER_PRICING["premium"]["output"] == 75.00

    def test_tier_pricing_matches_anthropic_models(self):
        """Verify tier pricing matches Anthropic model pricing."""
        for tier in ["cheap", "capable", "premium"]:
            model = MODEL_REGISTRY["anthropic"][tier]
            assert TIER_PRICING[tier]["input"] == model.input_cost_per_million
            assert TIER_PRICING[tier]["output"] == model.output_cost_per_million


class TestBackwardCompatibility:
    """Tests ensuring backward compatibility with existing code."""

    def test_model_router_compatibility(self):
        """Verify registry can be used by ModelRouter."""
        model = get_model("anthropic", "capable")
        assert model is not None

        # These are the fields ModelRouter.ModelConfig expects
        config = model.to_router_config()
        assert "model_id" in config
        assert "cost_per_1k_input" in config
        assert "cost_per_1k_output" in config
        assert "max_tokens" in config
        assert "supports_tools" in config

    def test_workflow_config_compatibility(self):
        """Verify registry can be used by WorkflowConfig."""
        model = get_model("anthropic", "capable")
        assert model is not None

        # These are the fields WorkflowConfig.ModelConfig expects
        config = model.to_workflow_config()
        assert "name" in config
        assert "provider" in config
        assert "tier" in config
        assert "input_cost_per_million" in config
        assert "output_cost_per_million" in config
        assert "max_tokens" in config
        assert "supports_vision" in config
        assert "supports_tools" in config

    def test_cost_tracker_compatibility(self):
        """Verify registry can be used by cost_tracker."""
        model = get_model("anthropic", "capable")
        assert model is not None

        pricing = model.to_cost_tracker_pricing()
        assert "input" in pricing
        assert "output" in pricing
        assert pricing["input"] == model.input_cost_per_million
        assert pricing["output"] == model.output_cost_per_million
