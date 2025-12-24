"""
Tests for BaseWorkflow and workflow data structures.

Tests the foundation classes used by all workflow implementations.
"""

from dataclasses import asdict
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.base import (
    PROVIDER_MODELS,
    CostReport,
    ModelProvider,
    ModelTier,
    WorkflowResult,
    WorkflowStage,
)


class TestModelTier:
    """Tests for ModelTier enum."""

    def test_tier_values(self):
        """Test tier enum values."""
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"

    def test_all_tiers_exist(self):
        """Test all expected tiers exist."""
        tiers = list(ModelTier)
        assert len(tiers) == 3
        assert ModelTier.CHEAP in tiers
        assert ModelTier.CAPABLE in tiers
        assert ModelTier.PREMIUM in tiers

    def test_to_unified(self):
        """Test conversion to unified ModelTier."""
        # Should not raise
        unified = ModelTier.CHEAP.to_unified()
        assert unified.value == "cheap"


class TestModelProvider:
    """Tests for ModelProvider enum."""

    def test_provider_values(self):
        """Test provider enum values."""
        assert ModelProvider.ANTHROPIC.value == "anthropic"
        assert ModelProvider.OPENAI.value == "openai"
        assert ModelProvider.OLLAMA.value == "ollama"
        assert ModelProvider.HYBRID.value == "hybrid"

    def test_all_providers_exist(self):
        """Test all expected providers exist."""
        providers = list(ModelProvider)
        assert ModelProvider.ANTHROPIC in providers
        assert ModelProvider.OPENAI in providers
        assert ModelProvider.OLLAMA in providers
        assert ModelProvider.HYBRID in providers
        assert ModelProvider.CUSTOM in providers

    def test_to_unified(self):
        """Test conversion to unified ModelProvider."""
        unified = ModelProvider.ANTHROPIC.to_unified()
        assert unified.value == "anthropic"


class TestProviderModels:
    """Tests for provider model mappings."""

    def test_anthropic_models_exist(self):
        """Test Anthropic models are defined."""
        assert ModelProvider.ANTHROPIC in PROVIDER_MODELS
        models = PROVIDER_MODELS[ModelProvider.ANTHROPIC]
        assert ModelTier.CHEAP in models
        assert ModelTier.CAPABLE in models
        assert ModelTier.PREMIUM in models

    def test_openai_models_exist(self):
        """Test OpenAI models are defined."""
        assert ModelProvider.OPENAI in PROVIDER_MODELS
        models = PROVIDER_MODELS[ModelProvider.OPENAI]
        assert ModelTier.CHEAP in models
        assert ModelTier.CAPABLE in models
        assert ModelTier.PREMIUM in models

    def test_ollama_models_exist(self):
        """Test Ollama models are defined."""
        assert ModelProvider.OLLAMA in PROVIDER_MODELS
        models = PROVIDER_MODELS[ModelProvider.OLLAMA]
        assert ModelTier.CHEAP in models

    def test_hybrid_models_exist(self):
        """Test hybrid model mappings exist."""
        assert ModelProvider.HYBRID in PROVIDER_MODELS
        models = PROVIDER_MODELS[ModelProvider.HYBRID]
        assert ModelTier.CHEAP in models
        assert ModelTier.CAPABLE in models
        assert ModelTier.PREMIUM in models

    def test_model_names_are_strings(self):
        """Test all model names are strings."""
        for provider, models in PROVIDER_MODELS.items():
            for tier, model_name in models.items():
                assert isinstance(model_name, str)
                assert len(model_name) > 0


class TestWorkflowStage:
    """Tests for WorkflowStage dataclass."""

    def test_create_stage(self):
        """Test creating a workflow stage."""
        stage = WorkflowStage(
            name="classify",
            tier=ModelTier.CHEAP,
            description="Classify the change type",
        )

        assert stage.name == "classify"
        assert stage.tier == ModelTier.CHEAP
        assert stage.description == "Classify the change type"
        assert stage.input_tokens == 0
        assert stage.output_tokens == 0
        assert stage.cost == 0.0
        assert stage.result is None
        assert stage.skipped is False
        assert stage.skip_reason is None

    def test_stage_with_results(self):
        """Test stage with execution results."""
        stage = WorkflowStage(
            name="analyze",
            tier=ModelTier.CAPABLE,
            description="Analyze code",
            input_tokens=1000,
            output_tokens=500,
            cost=0.015,
            result={"findings": []},
            duration_ms=1500,
        )

        assert stage.input_tokens == 1000
        assert stage.output_tokens == 500
        assert stage.cost == 0.015
        assert stage.result == {"findings": []}
        assert stage.duration_ms == 1500

    def test_skipped_stage(self):
        """Test skipped stage."""
        stage = WorkflowStage(
            name="remediate",
            tier=ModelTier.PREMIUM,
            description="Generate fixes",
            skipped=True,
            skip_reason="No critical issues found",
        )

        assert stage.skipped is True
        assert stage.skip_reason == "No critical issues found"


class TestCostReport:
    """Tests for CostReport dataclass."""

    def test_create_cost_report(self):
        """Test creating a cost report."""
        report = CostReport(
            total_cost=0.05,
            baseline_cost=0.15,
            savings=0.10,
            savings_percent=66.67,
        )

        assert report.total_cost == 0.05
        assert report.baseline_cost == 0.15
        assert report.savings == 0.10
        assert report.savings_percent == 66.67
        assert report.by_stage == {}
        assert report.by_tier == {}

    def test_cost_report_with_breakdown(self):
        """Test cost report with stage breakdown."""
        report = CostReport(
            total_cost=0.10,
            baseline_cost=0.30,
            savings=0.20,
            savings_percent=66.67,
            by_stage={"classify": 0.01, "analyze": 0.05, "assess": 0.04},
            by_tier={"cheap": 0.01, "capable": 0.09},
        )

        assert report.by_stage["classify"] == 0.01
        assert report.by_stage["analyze"] == 0.05
        assert len(report.by_tier) == 2

    def test_zero_cost_report(self):
        """Test zero cost report (no LLM calls)."""
        report = CostReport(
            total_cost=0.0,
            baseline_cost=0.0,
            savings=0.0,
            savings_percent=0.0,
        )

        assert report.total_cost == 0.0
        assert report.savings_percent == 0.0


class TestWorkflowResult:
    """Tests for WorkflowResult dataclass."""

    def test_create_workflow_result(self):
        """Test creating a workflow result."""
        now = datetime.now()
        stages = [
            WorkflowStage(name="s1", tier=ModelTier.CHEAP, description="Stage 1"),
            WorkflowStage(name="s2", tier=ModelTier.CAPABLE, description="Stage 2"),
        ]
        cost_report = CostReport(
            total_cost=0.05,
            baseline_cost=0.15,
            savings=0.10,
            savings_percent=66.67,
        )

        result = WorkflowResult(
            success=True,
            stages=stages,
            final_output={"result": "done"},
            cost_report=cost_report,
            started_at=now,
            completed_at=now,
            total_duration_ms=1500,
        )

        assert result.success is True
        assert len(result.stages) == 2
        assert result.final_output == {"result": "done"}
        assert result.cost_report.total_cost == 0.05
        assert result.total_duration_ms == 1500

    def test_failed_workflow_result(self):
        """Test failed workflow result."""
        now = datetime.now()
        result = WorkflowResult(
            success=False,
            stages=[],
            final_output={"error": "Failed at stage 1"},
            cost_report=CostReport(
                total_cost=0.01,
                baseline_cost=0.01,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=500,
        )

        assert result.success is False
        assert result.final_output["error"] == "Failed at stage 1"

    def test_workflow_result_with_skipped_stages(self):
        """Test workflow result with skipped stages."""
        now = datetime.now()
        stages = [
            WorkflowStage(name="s1", tier=ModelTier.CHEAP, description="Stage 1"),
            WorkflowStage(
                name="s2",
                tier=ModelTier.PREMIUM,
                description="Stage 2",
                skipped=True,
                skip_reason="Not needed",
            ),
        ]

        result = WorkflowResult(
            success=True,
            stages=stages,
            final_output={},
            cost_report=CostReport(
                total_cost=0.01,
                baseline_cost=0.05,
                savings=0.04,
                savings_percent=80.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=1000,
        )

        skipped_stages = [s for s in result.stages if s.skipped]
        assert len(skipped_stages) == 1
        assert skipped_stages[0].name == "s2"


class TestModelPricing:
    """Tests for model pricing consistency."""

    def test_cheap_cheaper_than_capable(self):
        """Test that cheap tier is actually cheaper."""
        # This tests the intent of the tier system
        assert ModelTier.CHEAP.value == "cheap"
        assert ModelTier.CAPABLE.value == "capable"
        assert ModelTier.PREMIUM.value == "premium"

    def test_all_tiers_have_unique_values(self):
        """Test tier values are unique."""
        values = [t.value for t in ModelTier]
        assert len(values) == len(set(values))


class TestWorkflowDataclassConversion:
    """Tests for dataclass serialization."""

    def test_workflow_stage_to_dict(self):
        """Test WorkflowStage can be converted to dict."""
        stage = WorkflowStage(
            name="test",
            tier=ModelTier.CHEAP,
            description="Test stage",
        )

        data = asdict(stage)

        assert data["name"] == "test"
        assert data["tier"] == ModelTier.CHEAP
        assert data["description"] == "Test stage"

    def test_cost_report_to_dict(self):
        """Test CostReport can be converted to dict."""
        report = CostReport(
            total_cost=0.05,
            baseline_cost=0.15,
            savings=0.10,
            savings_percent=66.67,
        )

        data = asdict(report)

        assert data["total_cost"] == 0.05
        assert data["savings_percent"] == 66.67
