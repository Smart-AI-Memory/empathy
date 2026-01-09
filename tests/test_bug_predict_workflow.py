"""Tests for BugPredictionWorkflow.

Tests bug prediction workflow stages and pattern correlation.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_os.workflows.base import ModelTier
from empathy_os.workflows.bug_predict import (
    BUG_PREDICT_STEPS,
    BugPredictionWorkflow,
    format_bug_predict_report,
)


class TestBugPredictSteps:
    """Tests for BUG_PREDICT_STEPS configuration."""

    def test_recommend_step_exists(self):
        """Test that recommend step is configured."""
        assert "recommend" in BUG_PREDICT_STEPS

    def test_recommend_step_is_premium(self):
        """Test that recommend step has premium tier hint."""
        step = BUG_PREDICT_STEPS["recommend"]
        assert step.tier_hint == "premium"

    def test_recommend_step_has_max_tokens(self):
        """Test that recommend step has max tokens set."""
        step = BUG_PREDICT_STEPS["recommend"]
        assert step.max_tokens == 2000


class TestBugPredictionWorkflowInit:
    """Tests for BugPredictionWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = BugPredictionWorkflow()

        assert workflow.name == "bug-predict"
        assert workflow.risk_threshold == 0.7
        assert workflow.patterns_dir == "./patterns"
        assert workflow._risk_score == 0.0

    def test_custom_risk_threshold(self):
        """Test initialization with custom risk threshold."""
        workflow = BugPredictionWorkflow(risk_threshold=0.5)

        assert workflow.risk_threshold == 0.5

    def test_custom_patterns_dir(self):
        """Test initialization with custom patterns directory."""
        workflow = BugPredictionWorkflow(patterns_dir="/custom/patterns")

        assert workflow.patterns_dir == "/custom/patterns"

    def test_stages_defined(self):
        """Test that all stages are defined."""
        workflow = BugPredictionWorkflow()

        assert workflow.stages == ["scan", "correlate", "predict", "recommend"]

    def test_tier_map_defined(self):
        """Test that tier map is properly defined."""
        workflow = BugPredictionWorkflow()

        assert workflow.tier_map["scan"] == ModelTier.CHEAP
        assert workflow.tier_map["correlate"] == ModelTier.CAPABLE
        assert workflow.tier_map["predict"] == ModelTier.CAPABLE
        assert workflow.tier_map["recommend"] == ModelTier.PREMIUM

    def test_load_patterns_empty_dir(self):
        """Test pattern loading with nonexistent directory."""
        workflow = BugPredictionWorkflow(patterns_dir="/nonexistent")

        assert workflow._bug_patterns == []


class TestPatternLoading:
    """Tests for pattern loading functionality."""

    def test_load_patterns_from_file(self):
        """Test loading patterns from debugging.json."""
        with tempfile.TemporaryDirectory() as tmpdir:
            patterns_data = {
                "patterns": [
                    {"bug_type": "null_reference", "root_cause": "Missing null check"},
                    {"bug_type": "type_mismatch", "root_cause": "Wrong type"},
                ],
            }
            patterns_file = Path(tmpdir) / "debugging.json"
            patterns_file.write_text(json.dumps(patterns_data))

            workflow = BugPredictionWorkflow(patterns_dir=tmpdir)

            assert len(workflow._bug_patterns) == 2
            assert workflow._bug_patterns[0]["bug_type"] == "null_reference"

    def test_load_patterns_invalid_json(self):
        """Test pattern loading with invalid JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            patterns_file = Path(tmpdir) / "debugging.json"
            patterns_file.write_text("not valid json")

            workflow = BugPredictionWorkflow(patterns_dir=tmpdir)

            assert workflow._bug_patterns == []


class TestShouldSkipStage:
    """Tests for stage skipping logic."""

    def test_should_not_skip_non_recommend_stage(self):
        """Test that non-recommend stages are not skipped."""
        workflow = BugPredictionWorkflow()

        skip, reason = workflow.should_skip_stage("scan", {})

        assert skip is False
        assert reason is None

    def test_should_downgrade_recommend_low_risk(self):
        """Test recommend stage downgraded with low risk score."""
        workflow = BugPredictionWorkflow(risk_threshold=0.7)
        workflow._risk_score = 0.3  # Below threshold

        skip, reason = workflow.should_skip_stage("recommend", {})

        assert skip is False
        assert workflow.tier_map["recommend"] == ModelTier.CAPABLE

    def test_should_not_downgrade_recommend_high_risk(self):
        """Test recommend stage not downgraded with high risk score."""
        workflow = BugPredictionWorkflow(risk_threshold=0.7)
        workflow._risk_score = 0.8  # Above threshold
        workflow.tier_map["recommend"] = ModelTier.PREMIUM  # Ensure premium

        skip, reason = workflow.should_skip_stage("recommend", {})

        assert skip is False
        assert workflow.tier_map["recommend"] == ModelTier.PREMIUM


class TestRunStageRouting:
    """Tests for stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_scan(self):
        """Test routing to scan stage."""
        workflow = BugPredictionWorkflow()

        with patch.object(workflow, "_scan", new_callable=AsyncMock) as mock:
            mock.return_value = ({"scanned": True}, 100, 50)

            result, in_tok, out_tok = await workflow.run_stage(
                "scan",
                ModelTier.CHEAP,
                {"path": "."},
            )

            mock.assert_called_once()
            assert result["scanned"] is True

    @pytest.mark.asyncio
    async def test_run_stage_correlate(self):
        """Test routing to correlate stage."""
        workflow = BugPredictionWorkflow()

        with patch.object(workflow, "_correlate", new_callable=AsyncMock) as mock:
            mock.return_value = ({"correlated": True}, 100, 50)

            result, _, _ = await workflow.run_stage(
                "correlate",
                ModelTier.CAPABLE,
                {"patterns_found": []},
            )

            mock.assert_called_once()
            assert result["correlated"] is True

    @pytest.mark.asyncio
    async def test_run_stage_predict(self):
        """Test routing to predict stage."""
        workflow = BugPredictionWorkflow()

        with patch.object(workflow, "_predict", new_callable=AsyncMock) as mock:
            mock.return_value = ({"predicted": True}, 100, 50)

            result, _, _ = await workflow.run_stage(
                "predict",
                ModelTier.CAPABLE,
                {"correlations": []},
            )

            mock.assert_called_once()
            assert result["predicted"] is True

    @pytest.mark.asyncio
    async def test_run_stage_recommend(self):
        """Test routing to recommend stage."""
        workflow = BugPredictionWorkflow()

        with patch.object(workflow, "_recommend", new_callable=AsyncMock) as mock:
            mock.return_value = ({"recommendations": "Fix bugs"}, 100, 50)

            result, _, _ = await workflow.run_stage(
                "recommend",
                ModelTier.PREMIUM,
                {"predictions": []},
            )

            mock.assert_called_once()
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_run_stage_unknown(self):
        """Test error for unknown stage."""
        workflow = BugPredictionWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("unknown", ModelTier.CHEAP, {})


class TestScanStage:
    """Tests for scan stage implementation."""

    @pytest.mark.asyncio
    async def test_scan_empty_directory(self):
        """Test scanning empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = BugPredictionWorkflow()

            result, in_tok, out_tok = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["file_count"] == 0
            assert result["pattern_count"] == 0
            assert result["scanned_files"] == []

    @pytest.mark.asyncio
    async def test_scan_detects_broad_exception(self):
        """Test scanning detects broad exception patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text(
                """
try:
    risky_operation()
except:
    pass
""",
            )

            workflow = BugPredictionWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert result["file_count"] == 1
            assert result["pattern_count"] >= 1
            patterns = result["patterns_found"]
            assert any(p["pattern"] == "broad_exception" for p in patterns)

    @pytest.mark.asyncio
    async def test_scan_detects_todo_fixme(self):
        """Test scanning detects TODO/FIXME comments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text(
                """
def incomplete():
    # TODO: finish this
    # FIXME: broken
    pass
""",
            )

            workflow = BugPredictionWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            patterns = result["patterns_found"]
            incomplete_patterns = [p for p in patterns if p["pattern"] == "incomplete_code"]
            assert len(incomplete_patterns) >= 1

    @pytest.mark.asyncio
    async def test_scan_detects_dangerous_eval(self):
        """Test scanning detects eval/exec usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "app.py").write_text(
                """
def dangerous(code):
    eval(code)
    exec(code)
""",
            )

            workflow = BugPredictionWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            patterns = result["patterns_found"]
            dangerous_patterns = [p for p in patterns if p["pattern"] == "dangerous_eval"]
            assert len(dangerous_patterns) >= 1
            assert dangerous_patterns[0]["severity"] == "high"

    @pytest.mark.asyncio
    async def test_scan_excludes_node_modules(self):
        """Test scanning excludes node_modules directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create node_modules with a file
            node_dir = Path(tmpdir) / "node_modules"
            node_dir.mkdir()
            (node_dir / "lib.js").write_text("eval('dangerous');")

            # Create regular file
            (Path(tmpdir) / "app.py").write_text("print('hello')")

            workflow = BugPredictionWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py", ".js"]},
                ModelTier.CHEAP,
            )

            # Should not scan node_modules
            scanned_paths = [f["path"] for f in result["scanned_files"]]
            assert not any("node_modules" in p for p in scanned_paths)

    @pytest.mark.asyncio
    async def test_scan_limits_file_count(self):
        """Test scanning limits returned files to 100."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create many files
            for i in range(150):
                (Path(tmpdir) / f"file_{i}.py").write_text(f"# File {i}")

            workflow = BugPredictionWorkflow()

            result, _, _ = await workflow._scan(
                {"path": tmpdir, "file_types": [".py"]},
                ModelTier.CHEAP,
            )

            assert len(result["scanned_files"]) <= 100
            assert result["file_count"] == 150  # Total count is preserved


class TestCorrelateStage:
    """Tests for correlate stage implementation."""

    @pytest.mark.asyncio
    async def test_correlate_no_patterns(self):
        """Test correlate with no patterns found."""
        workflow = BugPredictionWorkflow()

        result, in_tok, out_tok = await workflow._correlate(
            {"patterns_found": []},
            ModelTier.CAPABLE,
        )

        assert result["correlations"] == []
        assert result["correlation_count"] == 0

    @pytest.mark.asyncio
    async def test_correlate_with_matching_patterns(self):
        """Test correlate finds matching historical patterns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            patterns_data = {
                "patterns": [
                    {"bug_type": "null_reference", "root_cause": "Missing null check"},
                    {"bug_type": "type_mismatch", "root_cause": "Wrong type"},
                ],
            }
            patterns_file = Path(tmpdir) / "debugging.json"
            patterns_file.write_text(json.dumps(patterns_data))

            workflow = BugPredictionWorkflow(patterns_dir=tmpdir)

            result, _, _ = await workflow._correlate(
                {
                    "patterns_found": [
                        {"file": "app.py", "pattern": "broad_exception", "severity": "medium"},
                    ],
                },
                ModelTier.CAPABLE,
            )

            # broad_exception correlates with null_reference and type_mismatch
            assert result["correlation_count"] >= 1
            high_conf = [c for c in result["correlations"] if c["confidence"] > 0.6]
            assert len(high_conf) >= 1

    @pytest.mark.asyncio
    async def test_correlate_adds_low_confidence_for_no_match(self):
        """Test correlate adds low confidence for patterns without matches."""
        workflow = BugPredictionWorkflow()

        result, _, _ = await workflow._correlate(
            {
                "patterns_found": [
                    {"file": "app.py", "pattern": "unknown_pattern", "severity": "low"},
                ],
            },
            ModelTier.CAPABLE,
        )

        assert result["correlation_count"] == 1
        assert result["correlations"][0]["confidence"] == 0.3
        assert result["correlations"][0]["historical_bug"] is None


class TestPatternsCorrelate:
    """Tests for pattern correlation logic."""

    def test_broad_exception_correlates_with_null_reference(self):
        """Test broad_exception correlates with null_reference."""
        workflow = BugPredictionWorkflow()

        assert workflow._patterns_correlate("broad_exception", "null_reference") is True

    def test_broad_exception_correlates_with_type_mismatch(self):
        """Test broad_exception correlates with type_mismatch."""
        workflow = BugPredictionWorkflow()

        assert workflow._patterns_correlate("broad_exception", "type_mismatch") is True

    def test_incomplete_code_correlates_with_async_timing(self):
        """Test incomplete_code correlates with async_timing."""
        workflow = BugPredictionWorkflow()

        assert workflow._patterns_correlate("incomplete_code", "async_timing") is True

    def test_dangerous_eval_correlates_with_import_error(self):
        """Test dangerous_eval correlates with import_error."""
        workflow = BugPredictionWorkflow()

        assert workflow._patterns_correlate("dangerous_eval", "import_error") is True

    def test_unknown_pattern_does_not_correlate(self):
        """Test unknown pattern does not correlate."""
        workflow = BugPredictionWorkflow()

        assert workflow._patterns_correlate("unknown", "null_reference") is False


class TestPredictStage:
    """Tests for predict stage implementation."""

    @pytest.mark.asyncio
    async def test_predict_no_correlations(self):
        """Test predict with no correlations."""
        workflow = BugPredictionWorkflow()

        result, in_tok, out_tok = await workflow._predict(
            {"correlations": [], "patterns_found": []},
            ModelTier.CAPABLE,
        )

        assert result["predictions"] == []
        assert result["overall_risk_score"] == 0
        assert result["high_risk_files"] == 0

    @pytest.mark.asyncio
    async def test_predict_calculates_risk_scores(self):
        """Test predict calculates file risk scores."""
        workflow = BugPredictionWorkflow()

        result, _, _ = await workflow._predict(
            {
                "correlations": [
                    {
                        "current_pattern": {
                            "file": "app.py",
                            "pattern": "dangerous_eval",
                            "severity": "high",
                        },
                        "confidence": 0.9,
                    },
                    {
                        "current_pattern": {
                            "file": "utils.py",
                            "pattern": "incomplete_code",
                            "severity": "low",
                        },
                        "confidence": 0.3,
                    },
                ],
                "patterns_found": [
                    {"file": "app.py", "pattern": "dangerous_eval", "severity": "high"},
                    {"file": "utils.py", "pattern": "incomplete_code", "severity": "low"},
                ],
            },
            ModelTier.CAPABLE,
        )

        assert len(result["predictions"]) == 2
        # app.py should have higher risk (high severity * high confidence)
        predictions = {p["file"]: p["risk_score"] for p in result["predictions"]}
        assert predictions["app.py"] > predictions["utils.py"]

    @pytest.mark.asyncio
    async def test_predict_sets_overall_risk_score(self):
        """Test predict sets overall risk score."""
        workflow = BugPredictionWorkflow()

        await workflow._predict(
            {
                "correlations": [
                    {
                        "current_pattern": {
                            "file": "app.py",
                            "pattern": "dangerous_eval",
                            "severity": "high",
                        },
                        "confidence": 1.0,
                    },
                ],
                "patterns_found": [],
            },
            ModelTier.CAPABLE,
        )

        assert workflow._risk_score > 0

    @pytest.mark.asyncio
    async def test_predict_limits_predictions(self):
        """Test predict limits to top 20 files."""
        workflow = BugPredictionWorkflow()

        correlations = [
            {
                "current_pattern": {
                    "file": f"file_{i}.py",
                    "pattern": "broad_exception",
                    "severity": "medium",
                },
                "confidence": 0.5,
            }
            for i in range(30)
        ]

        result, _, _ = await workflow._predict(
            {"correlations": correlations, "patterns_found": []},
            ModelTier.CAPABLE,
        )

        assert len(result["predictions"]) <= 20


class TestRecommendStage:
    """Tests for recommend stage implementation."""

    @pytest.mark.asyncio
    async def test_recommend_generates_recommendations(self):
        """Test recommend stage generates recommendations."""
        workflow = BugPredictionWorkflow()

        result, in_tok, out_tok = await workflow._recommend(
            {
                "predictions": [
                    {
                        "file": "app.py",
                        "risk_score": 0.8,
                        "patterns": [{"pattern": "dangerous_eval", "severity": "high"}],
                    },
                ],
                "overall_risk_score": 0.8,
            },
            ModelTier.PREMIUM,
        )

        assert "recommendations" in result
        assert len(result["recommendations"]) > 0  # Has some recommendations
        assert result["model_tier_used"] == "premium"

    @pytest.mark.asyncio
    async def test_recommend_includes_formatted_report(self):
        """Test recommend includes formatted report."""
        workflow = BugPredictionWorkflow()
        workflow._api_key = None

        result, _, _ = await workflow._recommend(
            {
                "predictions": [],
                "overall_risk_score": 0.5,
            },
            ModelTier.PREMIUM,
        )

        assert "formatted_report" in result
        assert "BUG PREDICTION REPORT" in result["formatted_report"]

    @pytest.mark.asyncio
    async def test_recommend_with_mocked_llm(self):
        """Test recommend with mocked LLM response."""
        workflow = BugPredictionWorkflow()
        workflow._api_key = None

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("## Recommendations\n\n1. Fix eval usage", 500, 200)

            result, in_tok, out_tok = await workflow._recommend(
                {
                    "predictions": [
                        {
                            "file": "app.py",
                            "risk_score": 0.9,
                            "patterns": [{"pattern": "dangerous_eval", "severity": "high"}],
                        },
                    ],
                    "overall_risk_score": 0.9,
                },
                ModelTier.PREMIUM,
            )

            assert "Fix eval usage" in result["recommendations"]


class TestFormatBugPredictReport:
    """Tests for report formatting function."""

    def test_format_high_risk_report(self):
        """Test formatting report with high risk."""
        result = {
            "overall_risk_score": 0.9,
            "recommendations": "Fix all issues",
            "model_tier_used": "premium",
        }
        input_data = {
            "file_count": 10,
            "pattern_count": 5,
            "patterns_found": [
                {"severity": "high", "pattern": "dangerous_eval"},
                {"severity": "medium", "pattern": "broad_exception"},
            ],
            "predictions": [
                {"file": "app.py", "risk_score": 0.9, "patterns": []},
            ],
            "correlations": [],
        }

        report = format_bug_predict_report(result, input_data)

        assert "HIGH RISK" in report
        assert "Files Scanned: 10" in report
        assert "Patterns Found: 5" in report
        assert "Fix all issues" in report

    def test_format_moderate_risk_report(self):
        """Test formatting report with moderate risk."""
        result = {
            "overall_risk_score": 0.6,
            "recommendations": "Some improvements",
            "model_tier_used": "capable",
        }
        input_data = {
            "file_count": 5,
            "pattern_count": 2,
            "patterns_found": [],
            "predictions": [],
            "correlations": [],
        }

        report = format_bug_predict_report(result, input_data)

        assert "MODERATE RISK" in report

    def test_format_low_risk_report(self):
        """Test formatting report with low risk."""
        result = {
            "overall_risk_score": 0.4,
            "recommendations": "",
            "model_tier_used": "cheap",
        }
        input_data = {
            "file_count": 3,
            "pattern_count": 1,
            "patterns_found": [],
            "predictions": [],
            "correlations": [],
        }

        report = format_bug_predict_report(result, input_data)

        assert "LOW RISK" in report

    def test_format_minimal_risk_report(self):
        """Test formatting report with minimal risk."""
        result = {
            "overall_risk_score": 0.1,
            "recommendations": "",
            "model_tier_used": "cheap",
        }
        input_data = {
            "file_count": 1,
            "pattern_count": 0,
            "patterns_found": [],
            "predictions": [],
            "correlations": [],
        }

        report = format_bug_predict_report(result, input_data)

        assert "MINIMAL RISK" in report

    def test_format_report_with_correlations(self):
        """Test formatting report includes historical correlations."""
        result = {
            "overall_risk_score": 0.7,
            "recommendations": "Fix issues",
            "model_tier_used": "capable",
        }
        input_data = {
            "file_count": 5,
            "pattern_count": 2,
            "patterns_found": [],
            "predictions": [],
            "correlations": [
                {
                    "current_pattern": {"pattern": "broad_exception"},
                    "historical_bug": {
                        "type": "null_reference",
                        "root_cause": "Missing null check",
                    },
                    "confidence": 0.8,
                },
            ],
        }

        report = format_bug_predict_report(result, input_data)

        assert "HISTORICAL BUG CORRELATIONS" in report
        assert "null_reference" in report


class TestWorkflowExecution:
    """Tests for full workflow execution."""

    @pytest.mark.asyncio
    async def test_execute_workflow(self):
        """Test executing full workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file with some patterns
            (Path(tmpdir) / "app.py").write_text(
                """
def risky():
    try:
        eval("danger")
    except:
        pass
""",
            )

            workflow = BugPredictionWorkflow(patterns_dir=tmpdir)

            with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
                mock_telemetry.log_workflow = MagicMock()
                mock_telemetry.log_call = MagicMock()

                result = await workflow.execute(path=tmpdir, file_types=[".py"])

                assert result.success is True
                assert len(result.stages) == 4
                assert "overall_risk_score" in result.final_output

    @pytest.mark.asyncio
    async def test_execute_workflow_empty_dir(self):
        """Test executing workflow on empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = BugPredictionWorkflow()

            with patch.object(workflow, "_telemetry_backend") as mock_telemetry:
                mock_telemetry.log_workflow = MagicMock()
                mock_telemetry.log_call = MagicMock()

                result = await workflow.execute(path=tmpdir, file_types=[".py"])

                assert result.success is True
                assert result.final_output.get("overall_risk_score", 0) == 0
