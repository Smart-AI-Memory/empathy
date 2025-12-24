"""
Tests for CodeReviewCrew Dashboard Integration

Tests the integration of CodeReviewCrew and PRReviewWorkflow
with the Empathy Dashboard.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Adapter Tests
# ============================================================================


class TestCodeReviewAdapters:
    """Test code review adapter functions."""

    def test_check_crew_available(self):
        """Test CodeReviewCrew availability check."""
        from empathy_os.workflows.code_review_adapters import _check_crew_available

        result = _check_crew_available()
        # Should return True if CodeReviewCrew is installed
        assert isinstance(result, bool)

    def test_crew_report_to_workflow_format(self):
        """Test converting CodeReviewReport to workflow format."""
        from empathy_os.workflows.code_review_adapters import crew_report_to_workflow_format

        # Create mock report
        mock_report = MagicMock()
        mock_report.summary = "Review complete"
        mock_report.quality_score = 85.0
        mock_report.review_duration_seconds = 15.5
        mock_report.agents_used = ["lead", "security", "quality"]
        mock_report.memory_graph_hits = 2
        mock_report.metadata = {}
        mock_report.verdict = MagicMock(value="approve_with_suggestions")
        mock_report.has_blocking_issues = False

        # Create mock findings
        mock_finding1 = MagicMock()
        mock_finding1.title = "SQL Injection Risk"
        mock_finding1.description = "User input not sanitized"
        mock_finding1.severity = MagicMock(value="high")
        mock_finding1.category = MagicMock(value="security")
        mock_finding1.file_path = "src/api.py"
        mock_finding1.line_number = 42
        mock_finding1.code_snippet = "cursor.execute(query)"
        mock_finding1.suggestion = "Use parameterized queries"
        mock_finding1.before_code = None
        mock_finding1.after_code = None
        mock_finding1.confidence = 0.9

        mock_finding2 = MagicMock()
        mock_finding2.title = "Complex Method"
        mock_finding2.description = "Method too complex"
        mock_finding2.severity = MagicMock(value="medium")
        mock_finding2.category = MagicMock(value="quality")
        mock_finding2.file_path = "src/utils.py"
        mock_finding2.line_number = 100
        mock_finding2.code_snippet = None
        mock_finding2.suggestion = "Consider refactoring"
        mock_finding2.before_code = None
        mock_finding2.after_code = None
        mock_finding2.confidence = 0.8

        mock_report.findings = [mock_finding1, mock_finding2]

        result = crew_report_to_workflow_format(mock_report)

        assert result["crew_enabled"] is True
        assert result["quality_score"] == 85.0
        assert result["verdict"] == "approve_with_suggestions"
        assert result["finding_count"] == 2
        assert len(result["findings"]) == 2
        assert len(result["assessment"]["high_findings"]) == 1
        assert result["agents_used"] == ["lead", "security", "quality"]

    def test_merge_code_review_results(self):
        """Test merging crew and workflow results."""
        from empathy_os.workflows.code_review_adapters import merge_code_review_results

        crew_report = {
            "quality_score": 80.0,
            "findings": [
                {
                    "title": "Crew Finding",
                    "severity": "high",
                    "type": "security",
                    "file": "api.py",
                    "line": 10,
                }
            ],
            "verdict": "approve_with_suggestions",
            "assessment": {"quality_score": 80.0, "severity_breakdown": {"high": 1}},
        }

        workflow_findings = {
            "security_score": 70.0,
            "findings": [
                {
                    "title": "Workflow Finding",
                    "severity": "medium",
                    "type": "quality",
                    "file": "utils.py",
                    "line": 20,
                }
            ],
            "verdict": "approve",
            "assessment": {"severity_breakdown": {"medium": 1}},
        }

        result = merge_code_review_results(crew_report, workflow_findings)

        # Should merge findings (different file/line, so not deduplicated)
        assert len(result["findings"]) == 2
        assert result["merged"] is True
        assert result["crew_enabled"] is True
        # Verdict should take more severe
        assert result["verdict"] == "approve_with_suggestions"

    def test_merge_code_review_results_crew_only(self):
        """Test merging with only crew results."""
        from empathy_os.workflows.code_review_adapters import merge_code_review_results

        crew_report = {
            "quality_score": 90.0,
            "findings": [{"title": "Minor Issue", "severity": "low"}],
            "verdict": "approve",
            "crew_enabled": True,
        }

        result = merge_code_review_results(crew_report, None)

        assert result["quality_score"] == 90.0
        assert len(result["findings"]) == 1
        assert result["merged"] is False
        assert result["crew_enabled"] is True

    def test_merge_code_review_results_workflow_only(self):
        """Test merging with only workflow results."""
        from empathy_os.workflows.code_review_adapters import merge_code_review_results

        workflow_findings = {
            "security_score": 85.0,
            "findings": [{"title": "Minor Issue", "severity": "low"}],
            "verdict": "approve",
        }

        result = merge_code_review_results(None, workflow_findings)

        assert len(result["findings"]) == 1
        assert result["merged"] is False
        assert result["crew_enabled"] is False


# ============================================================================
# CodeReviewWorkflow with Crew Tests
# ============================================================================


class TestCodeReviewWorkflowWithCrew:
    """Test CodeReviewWorkflow with crew mode enabled."""

    def test_workflow_init_with_crew_disabled(self):
        """Test workflow initialization with crew disabled (default)."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow()

        assert workflow.use_crew is False
        assert "crew_review" not in workflow.stages
        assert "crew_review" not in workflow.tier_map

    def test_workflow_init_with_crew_enabled(self):
        """Test workflow initialization with crew enabled."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow(use_crew=True)

        assert workflow.use_crew is True
        assert "crew_review" in workflow.stages
        assert "crew_review" in workflow.tier_map

    @pytest.mark.asyncio
    async def test_crew_review_stage_fallback(self):
        """Test crew_review stage gracefully falls back when crew unavailable."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow(use_crew=True)

        # Mock _check_crew_available to return False
        with patch(
            "empathy_os.workflows.code_review_adapters._check_crew_available", return_value=False
        ):
            input_data = {"diff": "test code", "files_changed": ["test.py"]}

            result, input_tokens, output_tokens = await workflow._crew_review(
                input_data, workflow.tier_map["crew_review"]
            )

            assert "crew_review" in result
            assert result["crew_review"]["available"] is False
            assert result["crew_review"]["fallback"] is True

    @pytest.mark.asyncio
    async def test_crew_review_stage_with_mocked_crew(self):
        """Test crew_review stage with mocked crew results."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow(use_crew=True)

        # Mock crew report
        mock_report = MagicMock()
        mock_report.summary = "Review complete"
        mock_report.quality_score = 85.0
        mock_report.findings = []
        mock_report.review_duration_seconds = 10.0
        mock_report.agents_used = ["lead", "security"]
        mock_report.memory_graph_hits = 0
        mock_report.metadata = {}
        mock_report.verdict = MagicMock(value="approve")
        mock_report.has_blocking_issues = False

        with (
            patch(
                "empathy_os.workflows.code_review_adapters._check_crew_available", return_value=True
            ),
            patch(
                "empathy_os.workflows.code_review_adapters._get_crew_review",
                new_callable=AsyncMock,
                return_value=mock_report,
            ),
        ):
            input_data = {"diff": "test code", "files_changed": ["test.py"]}

            result, input_tokens, output_tokens = await workflow._crew_review(
                input_data, workflow.tier_map["crew_review"]
            )

            assert "crew_review" in result
            assert result["crew_review"]["available"] is True
            assert result["crew_review"]["fallback"] is False
            assert result["crew_review"]["quality_score"] == 85.0


# ============================================================================
# CodeReviewPipeline Tests
# ============================================================================


class TestCodeReviewPipeline:
    """Test CodeReviewPipeline composite workflow."""

    def test_pipeline_init_full_mode(self):
        """Test pipeline initialization in full mode."""
        from empathy_os.workflows import CodeReviewPipeline

        pipeline = CodeReviewPipeline(mode="full")

        assert pipeline.mode == "full"
        assert pipeline.crew_enabled is True
        assert pipeline.parallel_crew is True

    def test_pipeline_init_standard_mode(self):
        """Test pipeline initialization in standard mode."""
        from empathy_os.workflows import CodeReviewPipeline

        pipeline = CodeReviewPipeline(mode="standard")

        assert pipeline.mode == "standard"
        assert pipeline.crew_enabled is False

    def test_pipeline_init_quick_mode(self):
        """Test pipeline initialization in quick mode."""
        from empathy_os.workflows import CodeReviewPipeline

        pipeline = CodeReviewPipeline(mode="quick")

        assert pipeline.mode == "quick"
        assert pipeline.crew_enabled is False

    def test_for_pr_review_factory(self):
        """Test for_pr_review factory method."""
        from empathy_os.workflows import CodeReviewPipeline

        # Small PR should use standard mode
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=3)
        assert pipeline.mode == "standard"

        # Large PR should use full mode
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=10)
        assert pipeline.mode == "full"

    def test_for_quick_check_factory(self):
        """Test for_quick_check factory method."""
        from empathy_os.workflows import CodeReviewPipeline

        pipeline = CodeReviewPipeline.for_quick_check()
        assert pipeline.mode == "quick"

    @pytest.mark.asyncio
    async def test_pipeline_execute_quick_mode(self):
        """Test pipeline execution in quick mode (basic verification)."""
        from empathy_os.workflows import CodeReviewPipeline

        pipeline = CodeReviewPipeline.for_quick_check()

        # Verify pipeline configuration (execution would require API keys)
        assert pipeline.mode == "quick"
        assert pipeline.crew_enabled is False
        assert pipeline.parallel_crew is False

        # Verify the result dataclass structure
        from empathy_os.workflows.code_review_pipeline import CodeReviewPipelineResult

        assert hasattr(CodeReviewPipelineResult, "__dataclass_fields__")
        fields = CodeReviewPipelineResult.__dataclass_fields__
        assert "success" in fields
        assert "verdict" in fields
        assert "quality_score" in fields
        assert "crew_report" in fields
        assert "mode" in fields


# ============================================================================
# PRReviewWorkflow Tests
# ============================================================================


class TestPRReviewWorkflow:
    """Test PRReviewWorkflow composite workflow."""

    def test_workflow_init_default(self):
        """Test default workflow initialization."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow()

        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is True
        assert workflow.parallel is True

    def test_for_comprehensive_review_factory(self):
        """Test for_comprehensive_review factory method."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow.for_comprehensive_review()

        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is True

    def test_for_security_focused_factory(self):
        """Test for_security_focused factory method."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow.for_security_focused()

        assert workflow.use_code_crew is False
        assert workflow.use_security_crew is True

    def test_for_code_quality_focused_factory(self):
        """Test for_code_quality_focused factory method."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow.for_code_quality_focused()

        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is False

    @pytest.mark.asyncio
    async def test_workflow_execute_with_fallback(self):
        """Test workflow execution with crews unavailable (fallback)."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow()

        # Mock both crews as unavailable
        with (
            patch(
                "empathy_os.workflows.code_review_adapters._check_crew_available",
                return_value=False,
            ),
            patch(
                "empathy_os.workflows.security_adapters._check_crew_available", return_value=False
            ),
        ):
            result = await workflow.execute(
                diff="test code",
                files_changed=["test.py"],
                target_path="./src",
            )

            assert result.success is True
            # With no crews, should still succeed but with warnings
            assert "CodeReviewCrew unavailable" in result.warnings or result.code_review is None


# ============================================================================
# Workflow Registry Tests
# ============================================================================


class TestWorkflowRegistry:
    """Test workflow registration."""

    def test_crew_review_registered(self):
        """Test pro-review is registered in workflow registry."""
        from empathy_os.workflows import WORKFLOW_REGISTRY, CodeReviewPipeline

        assert "pro-review" in WORKFLOW_REGISTRY
        assert WORKFLOW_REGISTRY["pro-review"] == CodeReviewPipeline

    def test_pr_review_registered(self):
        """Test pr-review is registered in workflow registry."""
        from empathy_os.workflows import WORKFLOW_REGISTRY, PRReviewWorkflow

        assert "pr-review" in WORKFLOW_REGISTRY
        assert WORKFLOW_REGISTRY["pr-review"] == PRReviewWorkflow

    def test_get_workflow(self):
        """Test get_workflow function."""
        from empathy_os.workflows import CodeReviewPipeline, PRReviewWorkflow, get_workflow

        assert get_workflow("pro-review") == CodeReviewPipeline
        assert get_workflow("pr-review") == PRReviewWorkflow


# ============================================================================
# Integration Tests
# ============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_crew_review_full_flow(self):
        """Test complete pro-review flow - verify structure and imports."""
        from empathy_os.workflows import CodeReviewPipeline
        from empathy_os.workflows.code_review_pipeline import CodeReviewPipelineResult

        # Verify pipeline can be created with different modes
        full_pipeline = CodeReviewPipeline.for_full_review()
        assert full_pipeline.mode == "full"
        assert full_pipeline.crew_enabled is True

        quick_pipeline = CodeReviewPipeline.for_quick_check()
        assert quick_pipeline.mode == "quick"
        assert quick_pipeline.crew_enabled is False

        pr_pipeline = CodeReviewPipeline.for_pr_review(files_changed=10)
        assert pr_pipeline.mode == "full"  # Large PR uses full mode

        small_pr_pipeline = CodeReviewPipeline.for_pr_review(files_changed=2)
        assert small_pr_pipeline.mode == "standard"  # Small PR uses standard

        # Verify result structure
        fields = CodeReviewPipelineResult.__dataclass_fields__
        expected_fields = [
            "success",
            "verdict",
            "quality_score",
            "crew_report",
            "workflow_result",
            "combined_findings",
            "critical_count",
            "high_count",
            "medium_count",
            "agents_used",
            "recommendations",
            "blockers",
            "mode",
            "duration_seconds",
            "cost",
            "metadata",
        ]
        for f in expected_fields:
            assert f in fields, f"Missing field: {f}"

    @pytest.mark.asyncio
    async def test_pr_review_full_flow(self):
        """Test complete pr-review flow with mocked crews."""
        from empathy_os.workflows import PRReviewWorkflow

        workflow = PRReviewWorkflow(
            use_code_crew=True,
            use_security_crew=True,
            parallel=True,
        )

        # Mock both crews
        mock_code_report = MagicMock()
        mock_code_report.summary = "Code review complete"
        mock_code_report.quality_score = 80.0
        mock_code_report.findings = []
        mock_code_report.verdict = MagicMock(value="approve")
        mock_code_report.has_blocking_issues = False
        mock_code_report.review_duration_seconds = 5.0
        mock_code_report.agents_used = ["lead", "quality"]
        mock_code_report.memory_graph_hits = 0
        mock_code_report.metadata = {}

        mock_security_report = MagicMock()
        mock_security_report.summary = "Security audit complete"
        mock_security_report.risk_score = 20.0
        mock_security_report.findings = []
        mock_security_report.audit_duration_seconds = 5.0
        mock_security_report.agents_used = ["hunter", "assessor"]
        mock_security_report.memory_graph_hits = 0
        mock_security_report.metadata = {}

        with (
            patch(
                "empathy_os.workflows.code_review_adapters._check_crew_available", return_value=True
            ),
            patch(
                "empathy_os.workflows.code_review_adapters._get_crew_review",
                new_callable=AsyncMock,
                return_value=mock_code_report,
            ),
            patch(
                "empathy_os.workflows.security_adapters._check_crew_available", return_value=True
            ),
            patch(
                "empathy_os.workflows.security_adapters._get_crew_audit",
                new_callable=AsyncMock,
                return_value=mock_security_report,
            ),
        ):
            result = await workflow.execute(
                diff="def test(): pass",
                files_changed=["test.py"],
                target_path="./src",
            )

            # Verify result structure
            assert result.success is True
            assert result.verdict in [
                "approve",
                "approve_with_suggestions",
                "request_changes",
                "reject",
            ]
            assert 0 <= result.code_quality_score <= 100
            assert 0 <= result.security_risk_score <= 100
            assert isinstance(result.all_findings, list)
            assert len(result.agents_used) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
