"""
Tests for Performance Profiling Wizard

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import json

import pytest

from empathy_software_plugin.wizards.performance_profiling_wizard import (
    PerformanceProfilingWizard,
)


class TestPerformanceProfilingWizard:
    """Test Performance Profiling Wizard"""

    @pytest.mark.asyncio
    async def test_basic_initialization(self):
        """Test wizard initializes correctly"""
        wizard = PerformanceProfilingWizard()

        assert wizard.name == "Performance Profiling Wizard"
        assert wizard.level == 4
        assert wizard.profiler_parser is not None
        assert wizard.bottleneck_detector is not None
        assert wizard.trajectory_analyzer is not None

    @pytest.mark.asyncio
    async def test_simple_json_profiling_data(self):
        """Test parsing simple JSON profiling format"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "slow_function",
                        "file": "module.py",
                        "line": 10,
                        "total_time": 5.0,
                        "self_time": 4.5,
                        "calls": 100,
                        "cumulative_time": 5.0,
                        "percent": 50.0,
                    },
                    {
                        "name": "fast_function",
                        "file": "module.py",
                        "line": 20,
                        "total_time": 0.5,
                        "self_time": 0.5,
                        "calls": 100,
                        "cumulative_time": 0.5,
                        "percent": 5.0,
                    },
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        # Check profiling summary
        summary = result["profiling_summary"]
        assert summary["total_functions"] == 2
        assert summary["total_time"] == 5.5
        assert "slow_function" in summary["top_function"]

    @pytest.mark.asyncio
    async def test_hot_path_detection(self):
        """Test detection of hot paths (functions consuming >20% of time)"""
        wizard = PerformanceProfilingWizard()

        # Function consuming 45% of time = hot path
        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "hot_path_function",
                        "file": "api.py",
                        "line": 15,
                        "total_time": 4.5,
                        "self_time": 4.5,
                        "calls": 10,
                        "cumulative_time": 4.5,
                        "percent": 45.0,
                    },
                    {
                        "name": "normal_function",
                        "file": "api.py",
                        "line": 25,
                        "total_time": 0.5,
                        "self_time": 0.5,
                        "calls": 10,
                        "cumulative_time": 0.5,
                        "percent": 5.0,
                    },
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        bottlenecks = result["bottlenecks"]

        # Should detect hot path
        hot_path_bottlenecks = [b for b in bottlenecks if b["type"] == "hot_path"]
        assert len(hot_path_bottlenecks) > 0
        assert hot_path_bottlenecks[0]["function_name"] == "hot_path_function"
        assert hot_path_bottlenecks[0]["severity"] == "CRITICAL"

    @pytest.mark.asyncio
    async def test_n_plus_one_detection(self):
        """Test detection of N+1 query patterns"""
        wizard = PerformanceProfilingWizard()

        # Database query called 1000 times = N+1 pattern
        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "fetch_user",
                        "file": "database.py",
                        "line": 42,
                        "total_time": 3.0,
                        "self_time": 0.003,
                        "calls": 1000,  # Many calls!
                        "cumulative_time": 3.0,
                        "percent": 30.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        bottlenecks = result["bottlenecks"]

        # Should detect N+1 pattern
        n_plus_one = [b for b in bottlenecks if b["type"] == "n_plus_one"]
        assert len(n_plus_one) > 0
        assert n_plus_one[0]["function_name"] == "fetch_user"
        assert (
            "eager loading" in n_plus_one[0]["fix_suggestion"].lower()
            or "batch" in n_plus_one[0]["fix_suggestion"].lower()
        )

    @pytest.mark.asyncio
    async def test_io_bound_detection(self):
        """Test detection of I/O bound operations"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "read_file",
                        "file": "io.py",
                        "line": 10,
                        "total_time": 2.5,
                        "self_time": 2.5,
                        "calls": 100,
                        "cumulative_time": 2.5,
                        "percent": 25.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        bottlenecks = result["bottlenecks"]

        # Should detect I/O bound operation
        io_bound = [b for b in bottlenecks if b["type"] == "io_bound"]
        assert len(io_bound) > 0

    @pytest.mark.asyncio
    async def test_trajectory_analysis(self):
        """Test Level 4 trajectory prediction"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "api_endpoint",
                        "file": "api.py",
                        "line": 20,
                        "total_time": 0.8,
                        "self_time": 0.8,
                        "calls": 100,
                        "cumulative_time": 0.8,
                        "percent": 80.0,
                    }
                ]
            }
        )

        # Include historical metrics showing degradation
        historical_metrics = [
            {"timestamp": "2024-01-01T10:00:00", "response_time": 0.2},
            {"timestamp": "2024-01-02T10:00:00", "response_time": 0.45},
            {"timestamp": "2024-01-03T10:00:00", "response_time": 0.8},
        ]

        result = await wizard.analyze(
            {
                "profiler_data": profile_data,
                "profiler_type": "simple_json",
                "historical_metrics": historical_metrics,
            }
        )

        trajectory = result["trajectory_analysis"]

        # Should detect degrading trend
        assert trajectory["trajectory_state"] in ["degrading", "critical"]
        assert len(trajectory["trends"]) > 0

        # Check for response_time trend
        response_trends = [t for t in trajectory["trends"] if t["metric_name"] == "response_time"]
        if response_trends:
            assert response_trends[0]["direction"] == "degrading"
            assert response_trends[0]["rate_of_change"] > 0

    @pytest.mark.asyncio
    async def test_predictions_generated(self):
        """Test Level 4 predictions"""
        wizard = PerformanceProfilingWizard()

        # Critical hot path
        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "critical_function",
                        "file": "api.py",
                        "line": 10,
                        "total_time": 5.0,
                        "self_time": 5.0,
                        "calls": 1000,
                        "cumulative_time": 5.0,
                        "percent": 50.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        predictions = result["predictions"]

        assert len(predictions) > 0

        # Should have performance degradation prediction
        perf_preds = [
            p
            for p in predictions
            if "performance" in p["type"].lower() or "bottleneck" in p["type"].lower()
        ]
        assert len(perf_preds) > 0

        # Check prediction structure
        pred = perf_preds[0]
        assert "severity" in pred
        assert "description" in pred
        assert "prevention_steps" in pred

    @pytest.mark.asyncio
    async def test_recommendations_generated(self):
        """Test recommendations are actionable"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "slow_query",
                        "file": "db.py",
                        "line": 100,
                        "total_time": 3.0,
                        "self_time": 3.0,
                        "calls": 500,
                        "cumulative_time": 3.0,
                        "percent": 60.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        recommendations = result["recommendations"]

        assert len(recommendations) > 0
        # Should have specific recommendations for bottlenecks
        assert any(
            "optimize" in r.lower() or "cache" in r.lower() or "batch" in r.lower()
            for r in recommendations
        )

    @pytest.mark.asyncio
    async def test_insights_generation(self):
        """Test insight generation"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "database_query",
                        "file": "db.py",
                        "line": 50,
                        "total_time": 4.0,
                        "self_time": 4.0,
                        "calls": 200,
                        "cumulative_time": 4.0,
                        "percent": 80.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        insights = result["insights"]

        assert "dominant_pattern" in insights
        assert "optimization_potential" in insights
        # High optimization potential for 80% hot path
        assert isinstance(insights["optimization_potential"], dict)
        assert insights["optimization_potential"]["assessment"] in ["HIGH", "MEDIUM"]

    @pytest.mark.asyncio
    async def test_standard_wizard_interface(self):
        """Test wizard follows BaseWizard interface"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "test_func",
                        "file": "test.py",
                        "line": 1,
                        "total_time": 1.0,
                        "self_time": 1.0,
                        "calls": 10,
                        "cumulative_time": 1.0,
                        "percent": 100.0,
                    }
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        # Check standard wizard outputs
        assert "predictions" in result
        assert "recommendations" in result
        assert "confidence" in result

        # Confidence should be between 0 and 1
        assert 0 <= result["confidence"] <= 1

    @pytest.mark.asyncio
    async def test_empty_profiling_data(self):
        """Test handling of empty profiling data"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps({"functions": []})

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        # Should handle gracefully
        assert "profiling_summary" in result
        assert "bottlenecks" in result
        assert "predictions" in result
        assert result["profiling_summary"]["total_functions"] == 0

    @pytest.mark.asyncio
    async def test_multiple_bottleneck_types(self):
        """Test detection of multiple bottleneck types"""
        wizard = PerformanceProfilingWizard()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "hot_path",
                        "file": "api.py",
                        "line": 10,
                        "total_time": 3.0,
                        "self_time": 3.0,
                        "calls": 10,
                        "cumulative_time": 3.0,
                        "percent": 30.0,
                    },
                    {
                        "name": "fetch_user",
                        "file": "db.py",
                        "line": 50,
                        "total_time": 2.0,
                        "self_time": 0.002,
                        "calls": 1000,
                        "cumulative_time": 2.0,
                        "percent": 20.0,
                    },
                    {
                        "name": "read_file",
                        "file": "io.py",
                        "line": 30,
                        "total_time": 1.5,
                        "self_time": 1.5,
                        "calls": 50,
                        "cumulative_time": 1.5,
                        "percent": 15.0,
                    },
                ]
            }
        )

        result = await wizard.analyze(
            {"profiler_data": profile_data, "profiler_type": "simple_json"}
        )

        bottlenecks = result["bottlenecks"]

        # Should detect multiple types
        bottleneck_types = {b["type"] for b in bottlenecks}
        assert len(bottleneck_types) >= 2  # At least hot_path and n_plus_one


class TestProfilerParsers:
    """Test profiler parsing functionality"""

    @pytest.mark.asyncio
    async def test_simple_json_parser(self):
        """Test SimpleJSONProfilerParser"""
        from empathy_software_plugin.wizards.performance.profiler_parsers import (
            SimpleJSONProfilerParser,
        )

        parser = SimpleJSONProfilerParser()

        profile_data = json.dumps(
            {
                "functions": [
                    {
                        "name": "test_function",
                        "file": "test.py",
                        "line": 42,
                        "total_time": 1.5,
                        "self_time": 1.0,
                        "calls": 100,
                        "cumulative_time": 1.5,
                        "percent": 15.0,
                    }
                ]
            }
        )

        profiles = parser.parse(profile_data)

        assert len(profiles) == 1
        profile = profiles[0]
        assert profile.function_name == "test_function"
        assert profile.file_path == "test.py"
        assert profile.line_number == 42
        assert profile.total_time == 1.5
        assert profile.call_count == 100


class TestBottleneckDetector:
    """Test bottleneck detection logic"""

    @pytest.mark.asyncio
    async def test_hot_path_threshold(self):
        """Test hot path detection at 20% threshold"""
        from empathy_software_plugin.wizards.performance.bottleneck_detector import (
            BottleneckDetector,
        )
        from empathy_software_plugin.wizards.performance.profiler_parsers import (
            FunctionProfile,
        )

        detector = BottleneckDetector()

        # Function at exactly 20% - should be detected
        profiles = [
            FunctionProfile(
                function_name="critical_func",
                file_path="api.py",
                line_number=10,
                total_time=2.0,
                self_time=2.0,
                call_count=100,
                cumulative_time=2.0,
                percent_total=20.0,
                profiler="test",
            )
        ]

        bottlenecks = detector.detect_bottlenecks(profiles)

        hot_paths = [b for b in bottlenecks if b.type == "hot_path"]
        assert len(hot_paths) > 0


class TestTrajectoryAnalyzer:
    """Test trajectory analysis for Level 4 predictions"""

    @pytest.mark.asyncio
    async def test_degrading_trajectory_detection(self):
        """Test detection of degrading performance"""
        from empathy_software_plugin.wizards.performance.trajectory_analyzer import (
            TrajectoryAnalyzer,
        )

        analyzer = TrajectoryAnalyzer()

        # Response time increasing
        historical_metrics = [
            {"timestamp": "2024-01-01T10:00:00", "response_time": 0.2},
            {"timestamp": "2024-01-02T10:00:00", "response_time": 0.5},
            {"timestamp": "2024-01-03T10:00:00", "response_time": 0.8},
        ]

        current_metrics = {"response_time": 0.8}

        trajectory = analyzer.analyze_trajectory(historical_metrics, current_metrics)

        assert trajectory["trajectory_state"] in ["degrading", "critical"]

        # Should identify degrading trend
        trends = trajectory["trends"]
        response_trends = [t for t in trends if t["metric_name"] == "response_time"]
        assert len(response_trends) > 0
        assert response_trends[0]["direction"] == "degrading"

    @pytest.mark.asyncio
    async def test_optimal_trajectory(self):
        """Test detection of optimal/stable performance"""
        from empathy_software_plugin.wizards.performance.trajectory_analyzer import (
            TrajectoryAnalyzer,
        )

        analyzer = TrajectoryAnalyzer()

        # Response time stable
        historical_metrics = [
            {"timestamp": "2024-01-01T10:00:00", "response_time": 0.2},
            {"timestamp": "2024-01-02T10:00:00", "response_time": 0.21},
            {"timestamp": "2024-01-03T10:00:00", "response_time": 0.19},
        ]

        current_metrics = {"response_time": 0.2}

        trajectory = analyzer.analyze_trajectory(historical_metrics, current_metrics)

        assert trajectory["trajectory_state"] == "optimal"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
