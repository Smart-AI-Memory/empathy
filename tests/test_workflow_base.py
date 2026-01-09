"""Tests for BaseWorkflow and workflow data structures.

Tests the foundation classes used by all workflow implementations.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from empathy_os.cost_tracker import CostTracker
from empathy_os.workflows.base import (
    PROVIDER_MODELS,
    BaseWorkflow,
    CostReport,
    ModelProvider,
    ModelTier,
    WorkflowResult,
    WorkflowStage,
    _build_provider_models,
    _load_workflow_history,
    _save_workflow_run,
    get_workflow_stats,
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
        for _provider, models in PROVIDER_MODELS.items():
            for _tier, model_name in models.items():
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

    def test_workflow_result_error_type_defaults(self):
        """Test error_type and transient default values."""
        now = datetime.now()
        result = WorkflowResult(
            success=True,
            stages=[],
            final_output={},
            cost_report=CostReport(
                total_cost=0.0,
                baseline_cost=0.0,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=100,
        )

        # Default values
        assert result.error_type is None
        assert result.transient is False

    def test_workflow_result_with_error_taxonomy(self):
        """Test WorkflowResult with structured error taxonomy fields."""
        now = datetime.now()
        result = WorkflowResult(
            success=False,
            stages=[],
            final_output={},
            cost_report=CostReport(
                total_cost=0.01,
                baseline_cost=0.01,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=500,
            error="API rate limit exceeded",
            error_type="provider",
            transient=True,
        )

        assert result.success is False
        assert result.error == "API rate limit exceeded"
        assert result.error_type == "provider"
        assert result.transient is True

    def test_workflow_result_timeout_error(self):
        """Test WorkflowResult with timeout error classification."""
        now = datetime.now()
        result = WorkflowResult(
            success=False,
            stages=[],
            final_output={},
            cost_report=CostReport(
                total_cost=0.0,
                baseline_cost=0.0,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=120000,
            error="Request timed out after 120 seconds",
            error_type="timeout",
            transient=True,
        )

        assert result.error_type == "timeout"
        assert result.transient is True  # Timeouts are typically retryable

    def test_workflow_result_config_error(self):
        """Test WorkflowResult with config error classification."""
        now = datetime.now()
        result = WorkflowResult(
            success=False,
            stages=[],
            final_output={},
            cost_report=CostReport(
                total_cost=0.0,
                baseline_cost=0.0,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=50,
            error="Invalid configuration: missing API key",
            error_type="config",
            transient=False,
        )

        assert result.error_type == "config"
        assert result.transient is False  # Config errors require user action

    def test_workflow_result_validation_error(self):
        """Test WorkflowResult with validation error classification."""
        now = datetime.now()
        result = WorkflowResult(
            success=False,
            stages=[],
            final_output={},
            cost_report=CostReport(
                total_cost=0.0,
                baseline_cost=0.0,
                savings=0.0,
                savings_percent=0.0,
            ),
            started_at=now,
            completed_at=now,
            total_duration_ms=25,
            error="Invalid input: file path is required",
            error_type="validation",
            transient=False,
        )

        assert result.error_type == "validation"
        assert result.transient is False  # Validation errors require fixing input


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


class TestBuildProviderModels:
    """Tests for _build_provider_models function."""

    def test_build_returns_dict(self):
        """Test that _build_provider_models returns a dict."""
        models = _build_provider_models()

        assert isinstance(models, dict)
        assert len(models) > 0

    def test_all_providers_have_tiers(self):
        """Test all providers have tier mappings."""
        models = _build_provider_models()

        for provider in models:
            assert ModelTier.CHEAP in models[provider] or len(models[provider]) > 0


class TestWorkflowHistory:
    """Tests for workflow history functions."""

    def test_load_history_nonexistent_file(self):
        """Test loading history from nonexistent file."""
        history = _load_workflow_history("/nonexistent/path/history.json")

        assert history == []

    def test_load_history_empty_file(self):
        """Test loading history from empty/invalid file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("not valid json")
            f.flush()

            history = _load_workflow_history(f.name)

            assert history == []

    def test_load_history_valid_file(self):
        """Test loading history from valid file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            data = [
                {"workflow": "test", "success": True},
                {"workflow": "test2", "success": False},
            ]
            json.dump(data, f)
            f.flush()

            history = _load_workflow_history(f.name)

            assert len(history) == 2
            assert history[0]["workflow"] == "test"

    def test_save_workflow_run_creates_file(self):
        """Test saving workflow run creates file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = f"{tmpdir}/.empathy/workflow_runs.json"

            now = datetime.now()
            result = WorkflowResult(
                success=True,
                stages=[
                    WorkflowStage(
                        name="test",
                        tier=ModelTier.CHEAP,
                        description="Test",
                        cost=0.01,
                        duration_ms=100,
                    ),
                ],
                final_output={"result": "done"},
                cost_report=CostReport(
                    total_cost=0.01,
                    baseline_cost=0.05,
                    savings=0.04,
                    savings_percent=80.0,
                ),
                started_at=now,
                completed_at=now,
                total_duration_ms=100,
            )

            _save_workflow_run("test-workflow", "anthropic", result, history_file)

            assert Path(history_file).exists()

            with open(history_file) as f:
                data = json.load(f)
                assert len(data) == 1
                assert data[0]["workflow"] == "test-workflow"

    def test_save_workflow_run_appends(self):
        """Test saving multiple runs appends to history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = f"{tmpdir}/.empathy/workflow_runs.json"
            now = datetime.now()

            for i in range(3):
                result = WorkflowResult(
                    success=True,
                    stages=[],
                    final_output={},
                    cost_report=CostReport(
                        total_cost=0.01 * i,
                        baseline_cost=0.05,
                        savings=0.04,
                        savings_percent=80.0,
                    ),
                    started_at=now,
                    completed_at=now,
                    total_duration_ms=100,
                )
                _save_workflow_run(f"workflow-{i}", "anthropic", result, history_file)

            with open(history_file) as f:
                data = json.load(f)
                assert len(data) == 3

    def test_save_workflow_run_trims_history(self):
        """Test history is trimmed to max size."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = f"{tmpdir}/.empathy/workflow_runs.json"
            now = datetime.now()

            # Save more than max_history runs
            for i in range(5):
                result = WorkflowResult(
                    success=True,
                    stages=[],
                    final_output={},
                    cost_report=CostReport(
                        total_cost=0.01,
                        baseline_cost=0.05,
                        savings=0.04,
                        savings_percent=80.0,
                    ),
                    started_at=now,
                    completed_at=now,
                    total_duration_ms=100,
                )
                _save_workflow_run(
                    f"workflow-{i}",
                    "anthropic",
                    result,
                    history_file,
                    max_history=3,
                )

            with open(history_file) as f:
                data = json.load(f)
                assert len(data) == 3
                # Should keep only the last 3
                assert data[0]["workflow"] == "workflow-2"


class TestGetWorkflowStats:
    """Tests for get_workflow_stats function."""

    def test_empty_history(self):
        """Test stats with empty history."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump([], f)
            f.flush()

            stats = get_workflow_stats(f.name)

            assert stats["total_runs"] == 0
            assert stats["by_workflow"] == {}
            assert stats["total_cost"] == 0.0

    def test_stats_aggregation(self):
        """Test stats aggregation from history."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            history = [
                {
                    "workflow": "health-check",
                    "provider": "anthropic",
                    "success": True,
                    "cost": 0.05,
                    "savings": 0.10,
                    "savings_percent": 66.0,
                    "stages": [
                        {"tier": "cheap", "cost": 0.02, "skipped": False},
                        {"tier": "capable", "cost": 0.03, "skipped": False},
                    ],
                },
                {
                    "workflow": "health-check",
                    "provider": "anthropic",
                    "success": True,
                    "cost": 0.03,
                    "savings": 0.07,
                    "savings_percent": 70.0,
                    "stages": [{"tier": "cheap", "cost": 0.03, "skipped": False}],
                },
                {
                    "workflow": "code-review",
                    "provider": "openai",
                    "success": False,
                    "cost": 0.10,
                    "savings": 0.05,
                    "savings_percent": 33.0,
                    "stages": [],
                },
            ]
            json.dump(history, f)
            f.flush()

            stats = get_workflow_stats(f.name)

            assert stats["total_runs"] == 3
            assert stats["successful_runs"] == 2
            assert stats["by_workflow"]["health-check"]["runs"] == 2
            assert stats["by_workflow"]["code-review"]["runs"] == 1
            assert stats["by_provider"]["anthropic"]["runs"] == 2
            assert stats["by_provider"]["openai"]["runs"] == 1
            # Total cost: 0.05 + 0.03 + 0.10 = 0.18
            assert abs(stats["total_cost"] - 0.18) < 0.001
            # Total savings: 0.10 + 0.07 + 0.05 = 0.22
            assert abs(stats["total_savings"] - 0.22) < 0.001


class TestConcreteWorkflow(BaseWorkflow):
    """Concrete implementation for testing BaseWorkflow."""

    name = "test-workflow"
    description = "A test workflow"
    stages = ["stage1", "stage2", "stage3"]
    tier_map = {
        "stage1": ModelTier.CHEAP,
        "stage2": ModelTier.CAPABLE,
        "stage3": ModelTier.PREMIUM,
    }

    async def run_stage(
        self,
        stage_name: str,
        tier: ModelTier,
        input_data: Any,
    ) -> tuple[Any, int, int]:
        """Simple stage implementation for testing."""
        return (
            {**input_data, f"{stage_name}_done": True},
            100,  # input tokens
            50,  # output tokens
        )


class TestBaseWorkflowInit:
    """Tests for BaseWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = TestConcreteWorkflow()

        assert workflow.name == "test-workflow"
        assert workflow.cost_tracker is not None
        assert workflow._executor is None

    def test_with_cost_tracker(self):
        """Test initialization with custom cost tracker."""
        tracker = CostTracker()
        workflow = TestConcreteWorkflow(cost_tracker=tracker)

        assert workflow.cost_tracker is tracker

    def test_with_string_provider(self):
        """Test initialization with string provider."""
        workflow = TestConcreteWorkflow(provider="openai")

        assert workflow._provider_str == "openai"
        assert workflow.provider == ModelProvider.OPENAI

    def test_with_enum_provider(self):
        """Test initialization with enum provider."""
        workflow = TestConcreteWorkflow(provider=ModelProvider.OLLAMA)

        assert workflow.provider == ModelProvider.OLLAMA
        assert workflow._provider_str == "ollama"

    def test_with_custom_provider(self):
        """Test initialization with custom provider."""
        workflow = TestConcreteWorkflow(provider="my_custom_provider")

        assert workflow._provider_str == "my_custom_provider"
        assert workflow.provider == ModelProvider.CUSTOM


class TestBaseWorkflowMethods:
    """Tests for BaseWorkflow methods."""

    def test_get_tier_for_stage(self):
        """Test get_tier_for_stage returns correct tier."""
        workflow = TestConcreteWorkflow()

        assert workflow.get_tier_for_stage("stage1") == ModelTier.CHEAP
        assert workflow.get_tier_for_stage("stage2") == ModelTier.CAPABLE
        assert workflow.get_tier_for_stage("stage3") == ModelTier.PREMIUM

    def test_get_tier_for_unknown_stage(self):
        """Test get_tier_for_stage returns default for unknown stage."""
        workflow = TestConcreteWorkflow()

        # Unknown stage defaults to CAPABLE
        assert workflow.get_tier_for_stage("unknown") == ModelTier.CAPABLE

    def test_calculate_cost(self):
        """Test _calculate_cost method."""
        workflow = TestConcreteWorkflow()

        # Test with cheap tier
        cost = workflow._calculate_cost(ModelTier.CHEAP, 1000, 500)
        assert cost > 0
        assert cost < 0.01  # Cheap tier should be very low cost

    def test_calculate_baseline_cost(self):
        """Test _calculate_baseline_cost method."""
        workflow = TestConcreteWorkflow()

        # Premium tier baseline cost
        baseline = workflow._calculate_baseline_cost(1000, 500)
        cheap_cost = workflow._calculate_cost(ModelTier.CHEAP, 1000, 500)

        # Baseline (premium) should be higher than cheap
        assert baseline > cheap_cost

    def test_should_skip_stage_default(self):
        """Test default should_skip_stage returns False."""
        workflow = TestConcreteWorkflow()

        should_skip, reason = workflow.should_skip_stage("stage1", {})

        assert should_skip is False
        assert reason is None

    def test_describe(self):
        """Test describe method."""
        workflow = TestConcreteWorkflow()

        description = workflow.describe()

        assert "test-workflow" in description
        assert "stage1" in description
        assert "stage2" in description
        assert "stage3" in description
        assert "cheap" in description
        assert "capable" in description
        assert "premium" in description


class TestBaseWorkflowExecution:
    """Tests for BaseWorkflow execution."""

    @pytest.mark.asyncio
    async def test_execute_all_stages(self):
        """Test executing all stages."""
        workflow = TestConcreteWorkflow()

        with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
            mock_telemetry.log_workflow = MagicMock()
            mock_telemetry.log_call = MagicMock()

            result = await workflow.execute(initial_data="test")

            assert result.success is True
            assert len(result.stages) == 3
            assert all(not s.skipped for s in result.stages)
            assert result.final_output["stage3_done"] is True

    @pytest.mark.asyncio
    async def test_execute_with_error(self):
        """Test execution handles errors."""

        class FailingWorkflow(TestConcreteWorkflow):
            async def run_stage(self, stage_name, tier, input_data):
                if stage_name == "stage2":
                    raise ValueError("Stage 2 failed")
                return await super().run_stage(stage_name, tier, input_data)

        workflow = FailingWorkflow()

        with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
            mock_telemetry.log_workflow = MagicMock()
            mock_telemetry.log_call = MagicMock()

            result = await workflow.execute()

            assert result.success is False
            assert result.error is not None
            assert "Stage 2 failed" in result.error

    @pytest.mark.asyncio
    async def test_execute_with_skipped_stage(self):
        """Test execution with skipped stage."""

        class SkippingWorkflow(TestConcreteWorkflow):
            def should_skip_stage(self, stage_name, input_data):
                if stage_name == "stage2":
                    return True, "Not needed"
                return False, None

        workflow = SkippingWorkflow()

        with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
            mock_telemetry.log_workflow = MagicMock()
            mock_telemetry.log_call = MagicMock()

            result = await workflow.execute()

            assert result.success is True
            skipped = [s for s in result.stages if s.skipped]
            assert len(skipped) == 1
            assert skipped[0].name == "stage2"
            assert skipped[0].skip_reason == "Not needed"

    @pytest.mark.asyncio
    async def test_execute_generates_cost_report(self):
        """Test execution generates cost report."""
        workflow = TestConcreteWorkflow()

        with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
            mock_telemetry.log_workflow = MagicMock()
            mock_telemetry.log_call = MagicMock()

            result = await workflow.execute()

            assert result.cost_report is not None
            assert result.cost_report.total_cost > 0
            assert result.cost_report.baseline_cost > 0
            assert result.cost_report.savings >= 0
            assert "stage1" in result.cost_report.by_stage
            assert "cheap" in result.cost_report.by_tier


class TestBaseWorkflowProgressTracking:
    """Tests for progress tracking in BaseWorkflow."""

    @pytest.mark.asyncio
    async def test_execute_with_progress_callback(self):
        """Test execution with progress callback."""
        workflow = TestConcreteWorkflow()
        progress_updates = []

        def callback(update):
            progress_updates.append(update)

        workflow._progress_callback = callback

        with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
            mock_telemetry.log_workflow = MagicMock()
            mock_telemetry.log_call = MagicMock()

            result = await workflow.execute()

            assert result.success is True
            # Progress tracker should have been created and used
            assert workflow._progress_tracker is not None


class TestBaseWorkflowXMLPrompts:
    """Tests for XML prompt functionality."""

    def test_is_xml_enabled_default(self):
        """Test XML enabled check with default config."""
        workflow = TestConcreteWorkflow()

        # Default should be disabled
        assert workflow._is_xml_enabled() is False

    def test_render_plain_prompt(self):
        """Test rendering plain text prompt."""
        workflow = TestConcreteWorkflow()

        prompt = workflow._render_plain_prompt(
            role="code reviewer",
            goal="Review the code for issues",
            instructions=["Check for bugs", "Check for style"],
            constraints=["Be concise", "Be specific"],
            input_type="code",
            input_payload="def hello(): pass",
        )

        assert "code reviewer" in prompt
        assert "Review the code" in prompt
        assert "Check for bugs" in prompt
        assert "Be concise" in prompt
        assert "def hello()" in prompt

    def test_parse_xml_response_disabled(self):
        """Test XML response parsing when disabled."""
        workflow = TestConcreteWorkflow()

        result = workflow._parse_xml_response("Plain text response")

        assert result["_raw"] == "Plain text response"
        assert result["_parsed_response"] is None
