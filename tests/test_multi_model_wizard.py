"""
Comprehensive tests for MultiModelWizard.

Tests cover:
- Initialization and configuration
- Context validation
- Model coordination analysis
- Level 4 anticipatory predictions
- Recommendation generation
- Pattern extraction
- Helper methods
- Edge cases and error handling

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.multi_model_wizard import MultiModelWizard


class TestMultiModelWizardInitialization:
    """Test MultiModelWizard initialization."""

    def test_initialization(self):
        """Test wizard initializes correctly."""
        wizard = MultiModelWizard()

        assert wizard.name == "Multi-Model Coordination Wizard"
        assert wizard.domain == "software"
        assert wizard.empathy_level == 4
        assert wizard.category == "ai_development"

    def test_required_context(self):
        """Test get_required_context returns expected fields."""
        wizard = MultiModelWizard()
        required = wizard.get_required_context()

        assert "model_usage" in required
        assert "model_count" in required
        assert "routing_logic" in required
        assert "project_path" in required
        assert len(required) == 4


class TestMultiModelWizardAnalyze:
    """Test the main analyze method."""

    @pytest.fixture
    def wizard(self):
        """Create wizard instance."""
        return MultiModelWizard()

    @pytest.fixture
    def minimal_context(self):
        """Minimal valid context."""
        return {
            "model_usage": [],
            "model_count": 0,
            "routing_logic": [],
            "project_path": "/tmp/test",
        }

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self, wizard, minimal_context):
        """Test analyze returns expected output structure."""
        result = await wizard.analyze(minimal_context)

        assert "issues" in result
        assert "predictions" in result
        assert "recommendations" in result
        assert "patterns" in result
        assert "confidence" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_analyze_metadata_contains_wizard_info(self, wizard, minimal_context):
        """Test metadata contains wizard information."""
        result = await wizard.analyze(minimal_context)

        assert result["metadata"]["wizard"] == "Multi-Model Coordination Wizard"
        assert result["metadata"]["empathy_level"] == 4
        assert result["metadata"]["model_count"] == 0

    @pytest.mark.asyncio
    async def test_analyze_with_single_model(self, wizard):
        """Test analyze with single model (should have few/no issues)."""
        context = {
            "model_usage": [{"model": "gpt-4", "uses_template_system": True}],
            "model_count": 1,
            "routing_logic": [],
            "project_path": "/tmp/test",
        }

        result = await wizard.analyze(context)

        # Single model should have minimal coordination issues
        assert result["confidence"] == 0.85
        assert isinstance(result["issues"], list)

    @pytest.mark.asyncio
    async def test_analyze_with_many_models_triggers_warnings(self, wizard):
        """Test that 5+ models triggers coordination complexity warning."""
        context = {
            "model_usage": [
                {"model": f"model-{i}", "uses_template_system": False} for i in range(5)
            ],
            "model_count": 5,
            "routing_logic": [],
            "project_path": "/tmp/test",
        }

        result = await wizard.analyze(context)

        # Should have predictions about coordination complexity
        prediction_types = [p["type"] for p in result["predictions"]]
        assert "coordination_complexity" in prediction_types

    @pytest.mark.asyncio
    async def test_analyze_with_missing_optional_context(self, wizard):
        """Test analyze handles missing optional context gracefully."""
        context = {
            "model_usage": [],
            "model_count": 3,
            "routing_logic": [],
            "project_path": "/tmp/test",
        }

        result = await wizard.analyze(context)

        # Should not raise, should return valid structure
        assert "issues" in result
        assert "predictions" in result


class TestModelCoordinationAnalysis:
    """Test _analyze_model_coordination method."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_no_issues_with_minimal_models(self, wizard):
        """Test no issues with 1-2 models."""
        issues = await wizard._analyze_model_coordination(
            model_usage=[],
            model_count=1,
            routing=[],
        )

        # With just 1 model, should have minimal issues
        abstraction_issues = [i for i in issues if i["type"] == "no_model_abstraction"]
        assert len(abstraction_issues) == 0

    @pytest.mark.asyncio
    async def test_abstraction_warning_with_many_models(self, wizard):
        """Test abstraction warning with 3+ models."""
        issues = await wizard._analyze_model_coordination(
            model_usage=[],
            model_count=4,
            routing=[],
        )

        issue_types = [i["type"] for i in issues]
        assert "no_model_abstraction" in issue_types

    @pytest.mark.asyncio
    async def test_fallback_warning_with_multiple_models(self, wizard):
        """Test fallback warning when using multiple models without fallback."""
        issues = await wizard._analyze_model_coordination(
            model_usage=[],
            model_count=2,
            routing=[],
        )

        issue_types = [i["type"] for i in issues]
        assert "no_fallback_strategy" in issue_types

    @pytest.mark.asyncio
    async def test_cost_tracking_warning(self, wizard):
        """Test cost tracking warning with 3+ models."""
        issues = await wizard._analyze_model_coordination(
            model_usage=[],
            model_count=3,
            routing=[],
        )

        issue_types = [i["type"] for i in issues]
        assert "no_cost_tracking" in issue_types

    @pytest.mark.asyncio
    async def test_inconsistent_prompts_warning(self, wizard):
        """Test warning when prompts are inconsistent."""
        issues = await wizard._analyze_model_coordination(
            model_usage=[
                {"model": "gpt-4", "uses_template_system": False},
                {"model": "claude", "uses_template_system": False},
            ],
            model_count=2,
            routing=[],
        )

        issue_types = [i["type"] for i in issues]
        assert "inconsistent_prompts" in issue_types


class TestMultiModelPredictions:
    """Test _predict_multi_model_issues method."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_coordination_complexity_prediction(self, wizard):
        """Test coordination complexity prediction for 4-7 models."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=5,
            routing=[],
            full_context={"project_path": "/tmp"},
        )

        pred_types = [p["type"] for p in predictions]
        assert "coordination_complexity" in pred_types

        # Verify prediction structure
        complexity_pred = next(p for p in predictions if p["type"] == "coordination_complexity")
        assert "alert" in complexity_pred
        assert "probability" in complexity_pred
        assert "impact" in complexity_pred
        assert "prevention_steps" in complexity_pred
        assert len(complexity_pred["prevention_steps"]) > 0

    @pytest.mark.asyncio
    async def test_cost_optimization_prediction(self, wizard):
        """Test cost optimization prediction."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=3,
            routing=[],
            full_context={},
        )

        pred_types = [p["type"] for p in predictions]
        assert "cost_optimization_needed" in pred_types

    @pytest.mark.asyncio
    async def test_output_inconsistency_prediction(self, wizard):
        """Test output inconsistency prediction."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=3,
            routing=[],
            full_context={},
        )

        pred_types = [p["type"] for p in predictions]
        assert "output_inconsistency" in pred_types

    @pytest.mark.asyncio
    async def test_version_drift_prediction(self, wizard):
        """Test model version drift prediction."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=2,
            routing=[],
            full_context={},
        )

        pred_types = [p["type"] for p in predictions]
        assert "model_version_drift" in pred_types

    @pytest.mark.asyncio
    async def test_smart_routing_prediction_with_many_models(self, wizard):
        """Test smart routing prediction with 4+ models."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=4,
            routing=[],
            full_context={},
        )

        pred_types = [p["type"] for p in predictions]
        assert "suboptimal_routing" in pred_types

    @pytest.mark.asyncio
    async def test_no_predictions_with_single_model(self, wizard):
        """Test minimal predictions with single model."""
        predictions = await wizard._predict_multi_model_issues(
            model_usage=[],
            model_count=1,
            routing=[],
            full_context={},
        )

        # Single model shouldn't trigger multi-model predictions
        assert len(predictions) == 0


class TestRecommendations:
    """Test _generate_recommendations method."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    def test_recommendations_from_high_impact_predictions(self, wizard):
        """Test recommendations are generated from high-impact predictions."""
        predictions = [
            {
                "type": "test_prediction",
                "alert": "Test alert message",
                "impact": "high",
                "prevention_steps": ["Step 1", "Step 2", "Step 3"],
                "personal_experience": "We learned this the hard way.",
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        assert len(recommendations) > 0
        assert any("Test alert message" in r for r in recommendations)
        assert any("Step 1" in r for r in recommendations)

    def test_recommendations_include_experience(self, wizard):
        """Test personal experience is included in recommendations."""
        predictions = [
            {
                "type": "test",
                "alert": "Alert",
                "impact": "high",
                "prevention_steps": ["Step 1"],
                "personal_experience": "Our personal learning",
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        assert any("Our personal learning" in r for r in recommendations)

    def test_low_impact_predictions_excluded(self, wizard):
        """Test low-impact predictions don't generate recommendations."""
        predictions = [
            {
                "type": "test",
                "alert": "Low impact alert",
                "impact": "low",
                "prevention_steps": ["Step"],
            }
        ]

        recommendations = wizard._generate_recommendations([], predictions)

        # Low impact should not appear
        assert not any("Low impact alert" in r for r in recommendations)


class TestPatternExtraction:
    """Test _extract_patterns method."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    def test_extracts_multi_provider_pattern(self, wizard):
        """Test pattern extraction returns expected pattern."""
        patterns = wizard._extract_patterns([], [])

        assert len(patterns) > 0
        assert patterns[0]["pattern_type"] == "multi_provider_coordination"
        assert patterns[0]["domain_agnostic"] is True

    def test_pattern_has_applicable_domains(self, wizard):
        """Test pattern includes applicable domains."""
        patterns = wizard._extract_patterns([], [])

        applicable = patterns[0]["applicable_to"]
        assert "Multi-model AI systems" in applicable
        assert "Multi-cloud infrastructure" in applicable


class TestHelperMethods:
    """Test helper methods that check for features in routing files."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_has_model_abstraction_true(self, wizard, temp_dir):
        """Test detection of model abstraction."""
        test_file = temp_dir / "router.py"
        test_file.write_text("class ModelRouter:\n    pass")

        assert wizard._has_model_abstraction([str(test_file)]) is True

    def test_has_model_abstraction_false(self, wizard, temp_dir):
        """Test no model abstraction detection."""
        test_file = temp_dir / "simple.py"
        test_file.write_text("def call_api():\n    pass")

        assert wizard._has_model_abstraction([str(test_file)]) is False

    def test_has_fallback_strategy_true(self, wizard, temp_dir):
        """Test detection of fallback strategy."""
        test_file = temp_dir / "api.py"
        test_file.write_text("def call_with_fallback():\n    pass")

        assert wizard._has_fallback_strategy([str(test_file)]) is True

    def test_has_fallback_strategy_false(self, wizard, temp_dir):
        """Test no fallback detection."""
        test_file = temp_dir / "simple.py"
        test_file.write_text("def direct_call():\n    pass")

        assert wizard._has_fallback_strategy([str(test_file)]) is False

    def test_has_cost_tracking_true(self, wizard, temp_dir):
        """Test detection of cost tracking."""
        test_file = temp_dir / "billing.py"
        test_file.write_text("def track_cost():\n    log_cost()")

        assert wizard._has_cost_tracking([str(test_file)]) is True

    def test_has_cost_tracking_false(self, wizard):
        """Test no cost tracking detection."""
        assert wizard._has_cost_tracking([]) is False

    def test_has_performance_monitoring_true(self, wizard, temp_dir):
        """Test detection of performance monitoring."""
        test_file = temp_dir / "monitor.py"
        test_file.write_text("def record_latency():\n    pass")

        assert wizard._has_performance_monitoring([str(test_file)]) is True

    def test_has_consistent_prompts_true(self, wizard):
        """Test consistent prompts detection."""
        model_usage = [{"model": "gpt-4", "uses_template_system": True}]

        assert wizard._has_consistent_prompts(model_usage) is True

    def test_has_consistent_prompts_false(self, wizard):
        """Test inconsistent prompts detection."""
        model_usage = [{"model": "gpt-4", "uses_template_system": False}]

        assert wizard._has_consistent_prompts(model_usage) is False

    def test_has_output_validation_true(self, wizard, temp_dir):
        """Test detection of output validation."""
        test_file = temp_dir / "models.py"
        test_file.write_text("from pydantic import BaseModel")

        assert wizard._has_output_validation([str(test_file)]) is True

    def test_has_version_tracking_true(self, wizard, temp_dir):
        """Test detection of version tracking."""
        test_file = temp_dir / "config.py"
        test_file.write_text('MODEL = "gpt-4-0613"')

        assert wizard._has_version_tracking([str(test_file)]) is True

    def test_has_smart_routing_true(self, wizard, temp_dir):
        """Test detection of smart routing."""
        test_file = temp_dir / "router.py"
        test_file.write_text("def classify_request():\n    pass")

        assert wizard._has_smart_routing([str(test_file)]) is True

    def test_helper_handles_missing_file(self, wizard):
        """Test helper methods handle missing files gracefully."""
        result = wizard._has_model_abstraction(["/nonexistent/path.py"])
        assert result is False

    def test_helper_handles_empty_list(self, wizard):
        """Test helper methods handle empty routing list."""
        assert wizard._has_model_abstraction([]) is False
        assert wizard._has_fallback_strategy([]) is False
        assert wizard._has_cost_tracking([]) is False


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def wizard(self):
        return MultiModelWizard()

    @pytest.mark.asyncio
    async def test_analyze_with_empty_context_defaults(self, wizard):
        """Test analyze handles empty context with defaults."""
        context = {
            "model_usage": [],
            "model_count": 0,
            "routing_logic": [],
            "project_path": "",
        }

        result = await wizard.analyze(context)

        assert result is not None
        assert "issues" in result

    @pytest.mark.asyncio
    async def test_analyze_with_large_model_count(self, wizard):
        """Test analyze with unusually large model count."""
        context = {
            "model_usage": [],
            "model_count": 100,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should still work and generate predictions
        assert len(result["predictions"]) > 0

    @pytest.mark.asyncio
    async def test_analyze_with_negative_model_count(self, wizard):
        """Test analyze handles negative model count."""
        context = {
            "model_usage": [],
            "model_count": -1,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        # Should not crash
        assert "issues" in result

    def test_generate_recommendations_empty_predictions(self, wizard):
        """Test recommendations with empty predictions."""
        recommendations = wizard._generate_recommendations([], [])

        assert isinstance(recommendations, list)


class TestIntegration:
    """Integration tests for the full wizard workflow."""

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self):
        """Test complete analysis workflow with realistic context."""
        wizard = MultiModelWizard()

        context = {
            "model_usage": [
                {"model": "gpt-4", "uses_template_system": True},
                {"model": "claude-3", "uses_template_system": True},
                {"model": "gemini-pro", "uses_template_system": False},
            ],
            "model_count": 3,
            "routing_logic": [],
            "project_path": "/path/to/project",
        }

        result = await wizard.analyze(context)

        # Verify complete output
        assert result["confidence"] == 0.85
        assert len(result["issues"]) > 0
        assert len(result["predictions"]) > 0
        assert len(result["patterns"]) > 0
        assert result["metadata"]["model_count"] == 3

    @pytest.mark.asyncio
    async def test_wizard_identifies_all_issue_types(self):
        """Test wizard can identify all types of issues."""
        wizard = MultiModelWizard()

        # Context designed to trigger all warnings
        context = {
            "model_usage": [{"model": f"m{i}", "uses_template_system": False} for i in range(5)],
            "model_count": 5,
            "routing_logic": [],
            "project_path": "/tmp",
        }

        result = await wizard.analyze(context)

        issue_types = {i["type"] for i in result["issues"]}
        prediction_types = {p["type"] for p in result["predictions"]}

        # Should have multiple issue types
        assert len(issue_types) >= 3
        assert len(prediction_types) >= 3
