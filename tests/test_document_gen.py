"""Tests for src/empathy_os/workflows/document_gen.py

Tests the document generation workflow including:
- TOKEN_COSTS configuration
- DOC_GEN_STEPS configuration
- DocumentGenerationWorkflow class
- Cost estimation and tracking
- Configuration options
"""

from pathlib import Path

import pytest

from empathy_os.workflows.base import ModelTier
from empathy_os.workflows.document_gen import DOC_GEN_STEPS, TOKEN_COSTS, DocumentGenerationWorkflow


class TestTokenCosts:
    """Tests for TOKEN_COSTS configuration."""

    def test_has_cheap_tier(self):
        """Test TOKEN_COSTS has CHEAP tier."""
        assert ModelTier.CHEAP in TOKEN_COSTS

    def test_has_capable_tier(self):
        """Test TOKEN_COSTS has CAPABLE tier."""
        assert ModelTier.CAPABLE in TOKEN_COSTS

    def test_has_premium_tier(self):
        """Test TOKEN_COSTS has PREMIUM tier."""
        assert ModelTier.PREMIUM in TOKEN_COSTS

    def test_cheap_has_input_cost(self):
        """Test CHEAP tier has input cost."""
        assert "input" in TOKEN_COSTS[ModelTier.CHEAP]
        assert TOKEN_COSTS[ModelTier.CHEAP]["input"] > 0

    def test_cheap_has_output_cost(self):
        """Test CHEAP tier has output cost."""
        assert "output" in TOKEN_COSTS[ModelTier.CHEAP]
        assert TOKEN_COSTS[ModelTier.CHEAP]["output"] > 0

    def test_capable_costs_higher_than_cheap(self):
        """Test CAPABLE costs more than CHEAP."""
        assert TOKEN_COSTS[ModelTier.CAPABLE]["input"] > TOKEN_COSTS[ModelTier.CHEAP]["input"]
        assert TOKEN_COSTS[ModelTier.CAPABLE]["output"] > TOKEN_COSTS[ModelTier.CHEAP]["output"]

    def test_premium_costs_higher_than_capable(self):
        """Test PREMIUM costs more than CAPABLE."""
        assert TOKEN_COSTS[ModelTier.PREMIUM]["input"] > TOKEN_COSTS[ModelTier.CAPABLE]["input"]
        assert TOKEN_COSTS[ModelTier.PREMIUM]["output"] > TOKEN_COSTS[ModelTier.CAPABLE]["output"]

    def test_output_costs_higher_than_input(self):
        """Test output costs are higher than input costs for all tiers."""
        for tier in [ModelTier.CHEAP, ModelTier.CAPABLE, ModelTier.PREMIUM]:
            assert TOKEN_COSTS[tier]["output"] > TOKEN_COSTS[tier]["input"]


class TestDocGenSteps:
    """Tests for DOC_GEN_STEPS configuration."""

    def test_has_polish_step(self):
        """Test DOC_GEN_STEPS has polish step."""
        assert "polish" in DOC_GEN_STEPS

    def test_polish_step_name(self):
        """Test polish step name is correct."""
        assert DOC_GEN_STEPS["polish"].name == "polish"

    def test_polish_task_type(self):
        """Test polish step has final_review task type."""
        assert DOC_GEN_STEPS["polish"].task_type == "final_review"

    def test_polish_tier_hint(self):
        """Test polish step has premium tier hint."""
        assert DOC_GEN_STEPS["polish"].tier_hint == "premium"

    def test_polish_has_description(self):
        """Test polish step has a description."""
        assert DOC_GEN_STEPS["polish"].description
        assert len(DOC_GEN_STEPS["polish"].description) > 10

    def test_polish_max_tokens(self):
        """Test polish step has reasonable max_tokens."""
        assert DOC_GEN_STEPS["polish"].max_tokens >= 1000


class TestDocumentGenerationWorkflowInit:
    """Tests for DocumentGenerationWorkflow initialization."""

    def test_default_initialization(self):
        """Test workflow initializes with defaults."""
        workflow = DocumentGenerationWorkflow()
        assert workflow is not None

    def test_default_skip_polish_threshold(self):
        """Test default skip_polish_threshold."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.skip_polish_threshold == 1000

    def test_custom_skip_polish_threshold(self):
        """Test custom skip_polish_threshold."""
        workflow = DocumentGenerationWorkflow(skip_polish_threshold=2000)
        assert workflow.skip_polish_threshold == 2000

    def test_default_max_sections(self):
        """Test default max_sections."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.max_sections == 10

    def test_custom_max_sections(self):
        """Test custom max_sections."""
        workflow = DocumentGenerationWorkflow(max_sections=5)
        assert workflow.max_sections == 5

    def test_default_max_write_tokens_none(self):
        """Test max_write_tokens defaults to auto-scale value."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.max_write_tokens == 16000

    def test_custom_max_write_tokens(self):
        """Test custom max_write_tokens."""
        workflow = DocumentGenerationWorkflow(max_write_tokens=8000)
        assert workflow.max_write_tokens == 8000

    def test_default_section_focus_none(self):
        """Test section_focus defaults to None."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.section_focus is None

    def test_custom_section_focus(self):
        """Test custom section_focus."""
        focus = ["API Reference", "Testing Guide"]
        workflow = DocumentGenerationWorkflow(section_focus=focus)
        assert workflow.section_focus == focus

    def test_default_chunked_generation(self):
        """Test chunked_generation defaults to True."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.chunked_generation is True

    def test_disable_chunked_generation(self):
        """Test disabling chunked_generation."""
        workflow = DocumentGenerationWorkflow(chunked_generation=False)
        assert workflow.chunked_generation is False

    def test_default_sections_per_chunk(self):
        """Test default sections_per_chunk."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.sections_per_chunk == 3

    def test_custom_sections_per_chunk(self):
        """Test custom sections_per_chunk."""
        workflow = DocumentGenerationWorkflow(sections_per_chunk=5)
        assert workflow.sections_per_chunk == 5

    def test_default_max_cost(self):
        """Test default max_cost."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.max_cost == 5.0

    def test_custom_max_cost(self):
        """Test custom max_cost."""
        workflow = DocumentGenerationWorkflow(max_cost=10.0)
        assert workflow.max_cost == 10.0

    def test_zero_max_cost_disables_limits(self):
        """Test max_cost=0 disables cost limits."""
        workflow = DocumentGenerationWorkflow(max_cost=0)
        assert workflow.max_cost == 0

    def test_default_cost_warning_threshold(self):
        """Test default cost_warning_threshold."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.cost_warning_threshold == 0.8

    def test_custom_cost_warning_threshold(self):
        """Test custom cost_warning_threshold."""
        workflow = DocumentGenerationWorkflow(cost_warning_threshold=0.5)
        assert workflow.cost_warning_threshold == 0.5

    def test_default_graceful_degradation(self):
        """Test graceful_degradation defaults to True."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.graceful_degradation is True

    def test_disable_graceful_degradation(self):
        """Test disabling graceful_degradation."""
        workflow = DocumentGenerationWorkflow(graceful_degradation=False)
        assert workflow.graceful_degradation is False

    def test_default_export_path_none(self):
        """Test export_path defaults to None."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.export_path is None

    def test_custom_export_path_string(self):
        """Test custom export_path from string."""
        workflow = DocumentGenerationWorkflow(export_path="docs/generated")
        assert workflow.export_path == Path("docs/generated")

    def test_custom_export_path_path(self):
        """Test custom export_path from Path."""
        path = Path("docs/output")
        workflow = DocumentGenerationWorkflow(export_path=path)
        assert workflow.export_path == path

    def test_default_max_display_chars(self):
        """Test default max_display_chars."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.max_display_chars == 45000

    def test_custom_max_display_chars(self):
        """Test custom max_display_chars."""
        workflow = DocumentGenerationWorkflow(max_display_chars=30000)
        assert workflow.max_display_chars == 30000


class TestWorkflowClassAttributes:
    """Tests for workflow class attributes."""

    def test_workflow_name(self):
        """Test workflow name attribute."""
        assert DocumentGenerationWorkflow.name == "doc-gen"

    def test_workflow_description(self):
        """Test workflow description attribute."""
        assert "documentation" in DocumentGenerationWorkflow.description.lower()

    def test_workflow_stages(self):
        """Test workflow stages."""
        assert DocumentGenerationWorkflow.stages == ["outline", "write", "polish"]

    def test_workflow_tier_map(self):
        """Test workflow tier map."""
        tier_map = DocumentGenerationWorkflow.tier_map
        assert tier_map["outline"] == ModelTier.CHEAP
        assert tier_map["write"] == ModelTier.CAPABLE
        assert tier_map["polish"] == ModelTier.PREMIUM

    def test_outline_uses_cheap_tier(self):
        """Test outline stage uses CHEAP tier."""
        assert DocumentGenerationWorkflow.tier_map["outline"] == ModelTier.CHEAP

    def test_write_uses_capable_tier(self):
        """Test write stage uses CAPABLE tier."""
        assert DocumentGenerationWorkflow.tier_map["write"] == ModelTier.CAPABLE

    def test_polish_uses_premium_tier(self):
        """Test polish stage uses PREMIUM tier."""
        assert DocumentGenerationWorkflow.tier_map["polish"] == ModelTier.PREMIUM


class TestEstimateCost:
    """Tests for _estimate_cost method."""

    def test_estimate_cost_cheap_tier(self):
        """Test cost estimation for CHEAP tier."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.CHEAP, 1000, 1000)
        expected = (
            1000 / 1000 * TOKEN_COSTS[ModelTier.CHEAP]["input"]
            + 1000 / 1000 * TOKEN_COSTS[ModelTier.CHEAP]["output"]
        )
        assert cost == expected

    def test_estimate_cost_capable_tier(self):
        """Test cost estimation for CAPABLE tier."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.CAPABLE, 1000, 1000)
        expected = (
            1000 / 1000 * TOKEN_COSTS[ModelTier.CAPABLE]["input"]
            + 1000 / 1000 * TOKEN_COSTS[ModelTier.CAPABLE]["output"]
        )
        assert cost == expected

    def test_estimate_cost_premium_tier(self):
        """Test cost estimation for PREMIUM tier."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.PREMIUM, 1000, 1000)
        expected = (
            1000 / 1000 * TOKEN_COSTS[ModelTier.PREMIUM]["input"]
            + 1000 / 1000 * TOKEN_COSTS[ModelTier.PREMIUM]["output"]
        )
        assert cost == expected

    def test_estimate_cost_scales_with_tokens(self):
        """Test cost scales linearly with tokens."""
        workflow = DocumentGenerationWorkflow()
        cost_1k = workflow._estimate_cost(ModelTier.CAPABLE, 1000, 1000)
        cost_2k = workflow._estimate_cost(ModelTier.CAPABLE, 2000, 2000)
        assert cost_2k == pytest.approx(cost_1k * 2)

    def test_estimate_cost_zero_tokens(self):
        """Test cost is zero for zero tokens."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.CAPABLE, 0, 0)
        assert cost == 0.0

    def test_estimate_cost_input_only(self):
        """Test cost with only input tokens."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.CAPABLE, 1000, 0)
        expected = 1000 / 1000 * TOKEN_COSTS[ModelTier.CAPABLE]["input"]
        assert cost == expected

    def test_estimate_cost_output_only(self):
        """Test cost with only output tokens."""
        workflow = DocumentGenerationWorkflow()
        cost = workflow._estimate_cost(ModelTier.CAPABLE, 0, 1000)
        expected = 1000 / 1000 * TOKEN_COSTS[ModelTier.CAPABLE]["output"]
        assert cost == expected


class TestTrackCost:
    """Tests for _track_cost method."""

    def test_track_cost_accumulates(self):
        """Test cost tracking accumulates."""
        workflow = DocumentGenerationWorkflow()
        workflow._accumulated_cost = 0.0

        workflow._track_cost(ModelTier.CAPABLE, 1000, 1000)
        first_cost = workflow._accumulated_cost

        workflow._track_cost(ModelTier.CAPABLE, 1000, 1000)
        assert workflow._accumulated_cost == pytest.approx(first_cost * 2)

    def test_track_cost_returns_tuple(self):
        """Test _track_cost returns tuple of (cost, should_stop)."""
        workflow = DocumentGenerationWorkflow()
        result = workflow._track_cost(ModelTier.CAPABLE, 1000, 1000)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_track_cost_returns_current_cost(self):
        """Test _track_cost returns cost for this call."""
        workflow = DocumentGenerationWorkflow()
        cost, _ = workflow._track_cost(ModelTier.CAPABLE, 1000, 1000)
        expected = workflow._estimate_cost(ModelTier.CAPABLE, 1000, 1000)
        assert cost == pytest.approx(expected)

    def test_track_cost_should_stop_when_limit_exceeded(self):
        """Test should_stop is True when cost limit exceeded."""
        workflow = DocumentGenerationWorkflow(max_cost=0.001)  # Very low limit
        workflow._accumulated_cost = 0.0

        _, should_stop = workflow._track_cost(ModelTier.PREMIUM, 100000, 100000)
        assert should_stop is True

    def test_track_cost_should_not_stop_under_limit(self):
        """Test should_stop is False when under cost limit."""
        workflow = DocumentGenerationWorkflow(max_cost=100.0)  # High limit
        workflow._accumulated_cost = 0.0

        _, should_stop = workflow._track_cost(ModelTier.CHEAP, 1000, 1000)
        assert should_stop is False


class TestWorkflowState:
    """Tests for internal workflow state."""

    def test_initial_total_content_tokens(self):
        """Test initial _total_content_tokens is 0."""
        workflow = DocumentGenerationWorkflow()
        assert workflow._total_content_tokens == 0

    def test_initial_accumulated_cost(self):
        """Test initial _accumulated_cost is 0."""
        workflow = DocumentGenerationWorkflow()
        assert workflow._accumulated_cost == 0.0

    def test_initial_cost_warning_issued(self):
        """Test initial _cost_warning_issued is False."""
        workflow = DocumentGenerationWorkflow()
        assert workflow._cost_warning_issued is False

    def test_initial_partial_results(self):
        """Test initial _partial_results is empty dict."""
        workflow = DocumentGenerationWorkflow()
        assert workflow._partial_results == {}

    def test_user_max_write_tokens_stored(self):
        """Test user preference for max_write_tokens is stored."""
        workflow = DocumentGenerationWorkflow(max_write_tokens=8000)
        assert workflow._user_max_write_tokens == 8000

    def test_user_max_write_tokens_none_when_default(self):
        """Test _user_max_write_tokens is None when using default."""
        workflow = DocumentGenerationWorkflow()
        assert workflow._user_max_write_tokens is None


class TestCostGuardrails:
    """Tests for cost guardrail functionality."""

    def test_max_cost_default_is_five_dollars(self):
        """Test default max_cost is $5."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.max_cost == 5.0

    def test_cost_warning_at_80_percent(self):
        """Test warning threshold is 80% of max_cost."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.cost_warning_threshold == 0.8

    def test_warning_threshold_applies_to_max(self):
        """Test warning threshold applies to max_cost."""
        workflow = DocumentGenerationWorkflow(max_cost=10.0, cost_warning_threshold=0.5)
        warning_at = workflow.max_cost * workflow.cost_warning_threshold
        assert warning_at == 5.0


class TestGracefulDegradation:
    """Tests for graceful degradation settings."""

    def test_graceful_degradation_enabled_by_default(self):
        """Test graceful degradation is enabled by default."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.graceful_degradation is True

    def test_partial_results_stored(self):
        """Test partial results can be stored."""
        workflow = DocumentGenerationWorkflow()
        workflow._partial_results["outline"] = {"sections": ["A", "B"]}
        assert "outline" in workflow._partial_results


class TestExportPath:
    """Tests for export path configuration."""

    def test_export_path_none_by_default(self):
        """Test export_path is None by default."""
        workflow = DocumentGenerationWorkflow()
        assert workflow.export_path is None

    def test_export_path_converts_string_to_path(self):
        """Test string export_path converts to Path."""
        workflow = DocumentGenerationWorkflow(export_path="docs/api")
        assert isinstance(workflow.export_path, Path)

    def test_export_path_preserves_path_object(self):
        """Test Path export_path is preserved."""
        path = Path("docs/generated")
        workflow = DocumentGenerationWorkflow(export_path=path)
        assert workflow.export_path == path


class TestWorkflowInheritance:
    """Tests for workflow inheritance from BaseWorkflow."""

    def test_is_base_workflow_subclass(self):
        """Test DocumentGenerationWorkflow inherits from BaseWorkflow."""
        from empathy_os.workflows.base import BaseWorkflow

        assert issubclass(DocumentGenerationWorkflow, BaseWorkflow)

    def test_has_name_attribute(self):
        """Test workflow has name attribute."""
        assert hasattr(DocumentGenerationWorkflow, "name")

    def test_has_description_attribute(self):
        """Test workflow has description attribute."""
        assert hasattr(DocumentGenerationWorkflow, "description")

    def test_has_stages_attribute(self):
        """Test workflow has stages attribute."""
        assert hasattr(DocumentGenerationWorkflow, "stages")

    def test_has_tier_map_attribute(self):
        """Test workflow has tier_map attribute."""
        assert hasattr(DocumentGenerationWorkflow, "tier_map")


class TestConfigurationCombinations:
    """Tests for various configuration combinations."""

    def test_high_throughput_config(self):
        """Test configuration for high throughput."""
        workflow = DocumentGenerationWorkflow(
            max_sections=20,
            max_write_tokens=32000,
            chunked_generation=True,
            sections_per_chunk=5,
        )
        assert workflow.max_sections == 20
        assert workflow.max_write_tokens == 32000
        assert workflow.sections_per_chunk == 5

    def test_budget_conscious_config(self):
        """Test configuration for budget-conscious usage."""
        workflow = DocumentGenerationWorkflow(
            skip_polish_threshold=500,
            max_cost=1.0,
            graceful_degradation=True,
        )
        assert workflow.skip_polish_threshold == 500
        assert workflow.max_cost == 1.0
        assert workflow.graceful_degradation is True

    def test_focused_section_config(self):
        """Test configuration for focused section generation."""
        workflow = DocumentGenerationWorkflow(
            section_focus=["API Reference"],
            max_sections=3,
        )
        assert workflow.section_focus == ["API Reference"]
        assert workflow.max_sections == 3

    def test_unlimited_cost_config(self):
        """Test configuration with no cost limits."""
        workflow = DocumentGenerationWorkflow(max_cost=0)
        assert workflow.max_cost == 0


class TestTierOrdering:
    """Tests for tier cost ordering."""

    def test_cheap_is_cheapest(self):
        """Test CHEAP tier is the cheapest."""
        cheap = TOKEN_COSTS[ModelTier.CHEAP]
        capable = TOKEN_COSTS[ModelTier.CAPABLE]
        premium = TOKEN_COSTS[ModelTier.PREMIUM]

        cheap_cost = cheap["input"] + cheap["output"]
        capable_cost = capable["input"] + capable["output"]
        premium_cost = premium["input"] + premium["output"]

        assert cheap_cost < capable_cost < premium_cost

    def test_premium_is_most_expensive(self):
        """Test PREMIUM tier is most expensive."""
        cheap = TOKEN_COSTS[ModelTier.CHEAP]
        premium = TOKEN_COSTS[ModelTier.PREMIUM]

        assert premium["input"] > cheap["input"]
        assert premium["output"] > cheap["output"]
