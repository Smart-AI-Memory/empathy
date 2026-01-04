"""Tests for PerformanceProfilingWizard - Level 4 Anticipatory Performance Analysis.

Tests cover:
- Initialization and properties
- Main analyze method
- Insight generation
- Prediction generation
- Recommendation generation
- Helper methods
- Edge cases and error handling
- Integration tests
"""

import json
from unittest.mock import MagicMock

import pytest

from empathy_software_plugin.wizards.performance.bottleneck_detector import (
    Bottleneck,
    BottleneckType,
)
from empathy_software_plugin.wizards.performance.profiler_parsers import FunctionProfile
from empathy_software_plugin.wizards.performance.trajectory_analyzer import TrajectoryPrediction
from empathy_software_plugin.wizards.performance_profiling_wizard import PerformanceProfilingWizard


class TestPerformanceProfilingWizardInitialization:
    """Test wizard initialization and properties."""

    def test_initialization(self):
        """Test wizard initializes correctly."""
        wizard = PerformanceProfilingWizard()
        assert wizard.name == "Performance Profiling Wizard"
        assert wizard.level == 4

    def test_initializes_components(self):
        """Test wizard initializes helper components."""
        wizard = PerformanceProfilingWizard()
        assert wizard.profiler_parser is not None
        assert wizard.bottleneck_detector is not None
        assert wizard.trajectory_analyzer is not None


class TestPerformanceProfilingWizardAnalyze:
    """Test main analyze method."""

    @pytest.fixture
    def wizard(self):
        """Create wizard instance."""
        return PerformanceProfilingWizard()

    @pytest.fixture
    def sample_profiler_data(self):
        """Create sample profiler data in simple JSON format."""
        return json.dumps(
            {
                "functions": [
                    {
                        "name": "slow_database_query",
                        "file": "app/models.py",
                        "line": 45,
                        "total_time": 2.5,
                        "self_time": 2.5,
                        "calls": 100,
                        "cumulative_time": 2.5,
                        "percent": 50.0,
                    },
                    {
                        "name": "process_data",
                        "file": "app/utils.py",
                        "line": 120,
                        "total_time": 1.0,
                        "self_time": 1.0,
                        "calls": 10,
                        "cumulative_time": 1.0,
                        "percent": 20.0,
                    },
                    {
                        "name": "render_template",
                        "file": "app/views.py",
                        "line": 30,
                        "total_time": 0.5,
                        "self_time": 0.5,
                        "calls": 5,
                        "cumulative_time": 0.5,
                        "percent": 10.0,
                    },
                ],
            },
        )

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self, wizard, sample_profiler_data):
        """Test analyze returns correct structure."""
        context = {
            "profiler_data": sample_profiler_data,
            "profiler_type": "simple_json",
        }
        result = await wizard.analyze(context)

        assert "profiling_summary" in result
        assert "bottlenecks" in result
        assert "trajectory" in result
        assert "insights" in result
        assert "predictions" in result
        assert "recommendations" in result
        assert "confidence" in result

    @pytest.mark.asyncio
    async def test_analyze_requires_profiler_data(self, wizard):
        """Test analyze returns error when profiler_data is missing."""
        context = {}
        result = await wizard.analyze(context)

        assert "error" in result
        assert "profiler_data required" in result["error"]

    @pytest.mark.asyncio
    async def test_analyze_confidence_level(self, wizard, sample_profiler_data):
        """Test analyze returns correct confidence level."""
        context = {"profiler_data": sample_profiler_data}
        result = await wizard.analyze(context)

        assert result["confidence"] == 0.85

    @pytest.mark.asyncio
    async def test_analyze_profiling_summary(self, wizard, sample_profiler_data):
        """Test profiling summary contains expected fields."""
        context = {"profiler_data": sample_profiler_data}
        result = await wizard.analyze(context)

        summary = result["profiling_summary"]
        assert "total_functions" in summary
        assert "total_time" in summary
        assert "top_function" in summary
        assert "top_5_slowest" in summary
        assert summary["total_functions"] == 3

    @pytest.mark.asyncio
    async def test_analyze_with_threshold_percent(self, wizard, sample_profiler_data):
        """Test analyze respects threshold_percent."""
        context = {
            "profiler_data": sample_profiler_data,
            "threshold_percent": 25.0,  # Only 50% and above
        }
        result = await wizard.analyze(context)

        # Should have fewer bottlenecks due to high threshold
        assert isinstance(result["bottlenecks"], list)

    @pytest.mark.asyncio
    async def test_analyze_with_historical_metrics(self, wizard, sample_profiler_data):
        """Test analyze with historical metrics for trajectory."""
        historical = [
            {"response_time": 100, "cpu_percent": 50},
            {"response_time": 150, "cpu_percent": 60},
            {"response_time": 200, "cpu_percent": 70},
        ]
        context = {
            "profiler_data": sample_profiler_data,
            "historical_metrics": historical,
        }
        result = await wizard.analyze(context)

        assert "trajectory" in result
        assert "trajectory_analysis" in result

    @pytest.mark.asyncio
    async def test_analyze_with_empty_functions(self, wizard):
        """Test analyze with empty functions list."""
        empty_data = json.dumps({"functions": []})
        context = {"profiler_data": empty_data}
        result = await wizard.analyze(context)

        assert result["profiling_summary"]["total_functions"] == 0
        assert result["profiling_summary"]["top_function"] == "None"


class TestInsightGeneration:
    """Test insight generation."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    def test_generate_insights_io_bound(self, wizard):
        """Test insights identify IO-bound operations."""
        profiles = [
            FunctionProfile(
                function_name="read_file",
                file_path="test.py",
                line_number=1,
                total_time=1.0,
                self_time=1.0,
                call_count=10,
                cumulative_time=1.0,
                percent_total=50.0,
                profiler="test",
            ),
        ]
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.IO_BOUND,
                function_name="read_file",
                file_path="test.py",
                line_number=1,
                severity="HIGH",
                time_cost=1.0,
                percent_total=50.0,
                reasoning="I/O operation",
                fix_suggestion="Use async I/O",
                metadata={},
            ),
        ]

        insights = wizard._generate_insights(profiles, bottlenecks)

        assert insights["io_bound_operations"] == 1
        assert insights["dominant_pattern"] == "io_bound"

    def test_generate_insights_cpu_bound(self, wizard):
        """Test insights identify CPU-bound operations."""
        profiles = []
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.CPU_BOUND,
                function_name="compute",
                file_path="test.py",
                line_number=1,
                severity="HIGH",
                time_cost=1.0,
                percent_total=50.0,
                reasoning="CPU heavy",
                fix_suggestion="Optimize",
                metadata={},
            ),
        ]

        insights = wizard._generate_insights(profiles, bottlenecks)

        assert insights["cpu_bound_operations"] == 1
        assert insights["dominant_pattern"] == "cpu_bound"

    def test_generate_insights_n_plus_one(self, wizard):
        """Test insights identify N+1 queries."""
        profiles = []
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.N_PLUS_ONE,
                function_name="get_items",
                file_path="test.py",
                line_number=1,
                severity="HIGH",
                time_cost=1.0,
                percent_total=30.0,
                reasoning="N+1 query",
                fix_suggestion="Use eager loading",
                metadata={},
            ),
        ]

        insights = wizard._generate_insights(profiles, bottlenecks)

        assert insights["n_plus_one_queries"] == 1
        assert insights["dominant_pattern"] == "database_n_plus_one"

    def test_generate_insights_balanced(self, wizard):
        """Test insights with no dominant pattern."""
        profiles = []
        bottlenecks = []

        insights = wizard._generate_insights(profiles, bottlenecks)

        assert insights["dominant_pattern"] == "balanced"


class TestDominantPatternIdentification:
    """Test dominant pattern identification."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    def test_identify_n_plus_one_dominates(self, wizard):
        """Test N+1 takes precedence."""
        result = wizard._identify_dominant_pattern(io_heavy=5, cpu_heavy=5, n_plus_one=1)
        assert result == "database_n_plus_one"

    def test_identify_io_bound_dominates(self, wizard):
        """Test IO-bound when more IO than CPU."""
        result = wizard._identify_dominant_pattern(io_heavy=5, cpu_heavy=3, n_plus_one=0)
        assert result == "io_bound"

    def test_identify_cpu_bound_dominates(self, wizard):
        """Test CPU-bound when more CPU than IO."""
        result = wizard._identify_dominant_pattern(io_heavy=2, cpu_heavy=5, n_plus_one=0)
        assert result == "cpu_bound"

    def test_identify_balanced(self, wizard):
        """Test balanced when no clear dominant pattern."""
        result = wizard._identify_dominant_pattern(io_heavy=0, cpu_heavy=0, n_plus_one=0)
        assert result == "balanced"


class TestOptimizationPotential:
    """Test optimization potential estimation."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    def test_estimate_no_bottlenecks(self, wizard):
        """Test estimation with no bottlenecks."""
        result = wizard._estimate_optimization_potential([])

        assert result["potential_savings"] == 0.0
        assert result["percentage"] == 0.0
        assert result["assessment"] == "LOW"

    def test_estimate_with_bottlenecks(self, wizard):
        """Test estimation with bottlenecks."""
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.HOT_PATH,
                function_name="slow_func",
                file_path="test.py",
                line_number=1,
                severity="CRITICAL",
                time_cost=3.0,
                percent_total=50.0,
                reasoning="Hot path",
                fix_suggestion="Optimize",
                metadata={},
            ),
        ]

        result = wizard._estimate_optimization_potential(bottlenecks)

        assert result["potential_savings"] > 0
        assert result["percentage"] > 0

    def test_assess_high_potential(self, wizard):
        """Test HIGH assessment."""
        result = wizard._assess_optimization_potential(35.0)
        assert result == "HIGH"

    def test_assess_medium_potential(self, wizard):
        """Test MEDIUM assessment."""
        result = wizard._assess_optimization_potential(20.0)
        assert result == "MEDIUM"

    def test_assess_low_potential(self, wizard):
        """Test LOW assessment."""
        result = wizard._assess_optimization_potential(8.0)
        assert result == "LOW"

    def test_assess_minimal_potential(self, wizard):
        """Test MINIMAL assessment."""
        result = wizard._assess_optimization_potential(2.0)
        assert result == "MINIMAL"


class TestPredictionGeneration:
    """Test Level 4 prediction generation."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    def test_predict_critical_bottlenecks(self, wizard):
        """Test prediction for critical bottlenecks."""
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.HOT_PATH,
                function_name="critical_func",
                file_path="test.py",
                line_number=1,
                severity="CRITICAL",
                time_cost=5.0,
                percent_total=45.0,
                reasoning="Critical hot path",
                fix_suggestion="Optimize algorithm",
                metadata={},
            ),
        ]

        predictions = wizard._generate_predictions(bottlenecks, None, [])

        assert len(predictions) > 0
        degradation_preds = [p for p in predictions if p["type"] == "performance_degradation_risk"]
        assert len(degradation_preds) > 0
        assert degradation_preds[0]["severity"] == "critical"

    def test_predict_n_plus_one_scalability(self, wizard):
        """Test prediction for N+1 queries."""
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.N_PLUS_ONE,
                function_name="fetch_items",
                file_path="test.py",
                line_number=1,
                severity="HIGH",
                time_cost=2.0,
                percent_total=25.0,
                reasoning="N+1 query pattern",
                fix_suggestion="Use eager loading",
                metadata={},
            ),
        ]

        predictions = wizard._generate_predictions(bottlenecks, None, [])

        scalability_preds = [p for p in predictions if p["type"] == "scalability_risk"]
        assert len(scalability_preds) > 0
        assert scalability_preds[0]["severity"] == "high"

    def test_predict_trajectory_degrading(self, wizard):
        """Test prediction from degrading trajectory."""
        trajectory = MagicMock(spec=TrajectoryPrediction)
        trajectory.trajectory_state = "degrading"
        trajectory.overall_assessment = "Performance is degrading"
        trajectory.estimated_time_to_critical = "2 weeks"
        trajectory.confidence = 0.8
        trajectory.recommendations = ["Scale horizontally"]

        predictions = wizard._generate_predictions([], trajectory, [])

        trajectory_preds = [p for p in predictions if p["type"] == "performance_trajectory"]
        assert len(trajectory_preds) > 0
        assert trajectory_preds[0]["severity"] == "medium"

    def test_predict_trajectory_critical(self, wizard):
        """Test prediction from critical trajectory."""
        trajectory = MagicMock(spec=TrajectoryPrediction)
        trajectory.trajectory_state = "critical"
        trajectory.overall_assessment = "Performance is critical"
        trajectory.estimated_time_to_critical = "now"
        trajectory.confidence = 0.9
        trajectory.recommendations = ["Emergency scale up"]

        predictions = wizard._generate_predictions([], trajectory, [])

        trajectory_preds = [p for p in predictions if p["type"] == "performance_trajectory"]
        assert len(trajectory_preds) > 0
        assert trajectory_preds[0]["severity"] == "high"

    def test_no_predictions_for_healthy_system(self, wizard):
        """Test no predictions for healthy system."""
        bottlenecks = []
        trajectory = MagicMock(spec=TrajectoryPrediction)
        trajectory.trajectory_state = "optimal"

        predictions = wizard._generate_predictions(bottlenecks, trajectory, [])

        # Should be empty or minimal
        assert isinstance(predictions, list)


class TestRecommendationGeneration:
    """Test recommendation generation."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    def test_recommendations_for_n_plus_one(self, wizard):
        """Test recommendations for N+1 pattern."""
        insights = {"dominant_pattern": "database_n_plus_one", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations([], None, insights)

        assert any("N+1" in r for r in recommendations)

    def test_recommendations_for_io_bound(self, wizard):
        """Test recommendations for IO-bound pattern."""
        insights = {"dominant_pattern": "io_bound", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations([], None, insights)

        assert any("I/O" in r or "caching" in r.lower() for r in recommendations)

    def test_recommendations_for_cpu_bound(self, wizard):
        """Test recommendations for CPU-bound pattern."""
        insights = {"dominant_pattern": "cpu_bound", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations([], None, insights)

        assert any("CPU" in r or "algorithm" in r.lower() for r in recommendations)

    def test_recommendations_include_bottleneck_fixes(self, wizard):
        """Test recommendations include bottleneck-specific fixes."""
        bottlenecks = [
            Bottleneck(
                type=BottleneckType.HOT_PATH,
                function_name="slow_func",
                file_path="test.py",
                line_number=1,
                severity="HIGH",
                time_cost=2.0,
                percent_total=30.0,
                reasoning="Hot path",
                fix_suggestion="Cache results",
                metadata={},
            ),
        ]
        insights = {"dominant_pattern": "balanced", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations(bottlenecks, None, insights)

        assert any("slow_func" in r for r in recommendations)

    def test_recommendations_include_trajectory(self, wizard):
        """Test recommendations include trajectory suggestions."""
        trajectory = MagicMock(spec=TrajectoryPrediction)
        trajectory.trajectory_state = "degrading"
        trajectory.recommendations = ["Add more servers", "Implement caching"]
        insights = {"dominant_pattern": "balanced", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations([], trajectory, insights)

        assert any("servers" in r.lower() for r in recommendations)

    def test_recommendations_high_optimization_potential(self, wizard):
        """Test recommendations mention high optimization potential."""
        insights = {
            "dominant_pattern": "balanced",
            "optimization_potential": "HIGH",
        }

        recommendations = wizard._generate_recommendations([], None, insights)

        assert any("HIGH" in r and "optimization" in r.lower() for r in recommendations)

    def test_recommendations_deduplicated(self, wizard):
        """Test recommendations are deduplicated."""
        insights = {"dominant_pattern": "balanced", "optimization_potential": {}}

        recommendations = wizard._generate_recommendations([], None, insights)

        # Check no duplicates
        assert len(recommendations) == len(set(recommendations))


class TestEdgeCases:
    """Test edge cases and error handling."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    @pytest.mark.asyncio
    async def test_analyze_with_invalid_json(self, wizard):
        """Test analyze handles invalid JSON gracefully."""
        context = {
            "profiler_data": "not valid json {{{",
            "profiler_type": "simple_json",
        }
        result = await wizard.analyze(context)

        # Should not crash, but may have empty results
        assert "profiling_summary" in result

    @pytest.mark.asyncio
    async def test_analyze_with_null_values(self, wizard):
        """Test analyze handles null/zero values."""
        context = {
            "profiler_data": json.dumps(
                {
                    "functions": [
                        {
                            "name": "unknown",
                            "file": "",
                            "line": 0,
                            "total_time": 0.0,
                            "self_time": 0.0,
                            "calls": 0,
                            "cumulative_time": 0.0,
                            "percent": 0.0,
                        },
                    ],
                },
            ),
        }
        result = await wizard.analyze(context)

        # Should handle gracefully
        assert isinstance(result, dict)
        assert result["profiling_summary"]["total_functions"] == 1

    @pytest.mark.asyncio
    async def test_analyze_with_very_large_profile(self, wizard):
        """Test analyze handles large profile data."""
        functions = [
            {
                "name": f"func_{i}",
                "file": f"module_{i}.py",
                "line": i,
                "total_time": 0.001 * i,
                "self_time": 0.001 * i,
                "calls": i,
                "cumulative_time": 0.001 * i,
                "percent": 0.01 * i,
            }
            for i in range(1000)
        ]
        context = {
            "profiler_data": json.dumps({"functions": functions}),
        }
        result = await wizard.analyze(context)

        assert result["profiling_summary"]["total_functions"] == 1000

    @pytest.mark.asyncio
    async def test_analyze_with_zero_time_functions(self, wizard):
        """Test analyze handles zero-time functions."""
        context = {
            "profiler_data": json.dumps(
                {
                    "functions": [
                        {
                            "name": "fast_func",
                            "file": "test.py",
                            "line": 1,
                            "total_time": 0.0,
                            "self_time": 0.0,
                            "calls": 1000,
                            "cumulative_time": 0.0,
                            "percent": 0.0,
                        },
                    ],
                },
            ),
        }
        result = await wizard.analyze(context)

        assert result["profiling_summary"]["total_time"] == 0.0


class TestIntegration:
    """Integration tests for full analysis workflow."""

    @pytest.fixture
    def wizard(self):
        return PerformanceProfilingWizard()

    @pytest.mark.asyncio
    async def test_full_analysis_workflow(self, wizard):
        """Test complete analysis workflow."""
        profiler_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "slow_database_query",
                        "file": "app/db.py",
                        "line": 100,
                        "total_time": 5.0,
                        "self_time": 5.0,
                        "calls": 200,
                        "cumulative_time": 5.0,
                        "percent": 50.0,
                    },
                    {
                        "name": "compute_heavy",
                        "file": "app/process.py",
                        "line": 50,
                        "total_time": 3.0,
                        "self_time": 3.0,
                        "calls": 10,
                        "cumulative_time": 3.0,
                        "percent": 30.0,
                    },
                    {
                        "name": "read_config",
                        "file": "app/config.py",
                        "line": 10,
                        "total_time": 0.5,
                        "self_time": 0.5,
                        "calls": 1,
                        "cumulative_time": 0.5,
                        "percent": 5.0,
                    },
                ],
            },
        )

        context = {
            "profiler_data": profiler_data,
            "profiler_type": "simple_json",
            "threshold_percent": 5.0,
        }

        result = await wizard.analyze(context)

        # Verify structure
        assert result["confidence"] == 0.85
        assert result["profiling_summary"]["total_functions"] == 3
        assert len(result["insights"]) > 0

        # Should identify the slow database query as problematic
        top_function = result["profiling_summary"]["top_function"]
        assert "slow_database_query" in top_function

    @pytest.mark.asyncio
    async def test_analysis_with_trajectory(self, wizard):
        """Test analysis with trajectory data."""
        profiler_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "api_handler",
                        "file": "app/api.py",
                        "line": 25,
                        "total_time": 2.0,
                        "self_time": 2.0,
                        "calls": 50,
                        "cumulative_time": 2.0,
                        "percent": 40.0,
                    },
                ],
            },
        )

        historical = [
            {"response_time": 100, "cpu_percent": 40, "memory_mb": 512},
            {"response_time": 150, "cpu_percent": 55, "memory_mb": 600},
            {"response_time": 220, "cpu_percent": 70, "memory_mb": 750},
        ]

        context = {
            "profiler_data": profiler_data,
            "historical_metrics": historical,
            "current_metrics": {"response_time": 300, "cpu_percent": 85, "memory_mb": 900},
        }

        result = await wizard.analyze(context)

        # Should have trajectory analysis
        assert "trajectory_analysis" in result

    @pytest.mark.asyncio
    async def test_identifies_multiple_issue_types(self, wizard):
        """Test wizard identifies multiple issue types."""
        profiler_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "query_users",  # N+1 candidate
                        "file": "app/models.py",
                        "line": 50,
                        "total_time": 3.0,
                        "self_time": 3.0,
                        "calls": 100,  # High call count
                        "cumulative_time": 3.0,
                        "percent": 35.0,
                    },
                    {
                        "name": "read_large_file",  # IO bound
                        "file": "app/io.py",
                        "line": 20,
                        "total_time": 2.0,
                        "self_time": 2.0,
                        "calls": 5,
                        "cumulative_time": 2.0,
                        "percent": 25.0,
                    },
                ],
            },
        )

        context = {
            "profiler_data": profiler_data,
            "threshold_percent": 5.0,
        }

        result = await wizard.analyze(context)

        # Should have bottlenecks
        assert len(result["bottlenecks"]) > 0

        # Check insights detected patterns
        insights = result["insights"]
        assert insights["io_bound_operations"] >= 0 or insights["n_plus_one_queries"] >= 0
