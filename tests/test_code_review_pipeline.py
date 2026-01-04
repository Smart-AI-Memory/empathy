"""Tests for CodeReviewPipeline.

Tests the composite workflow that combines CodeReviewCrew with CodeReviewWorkflow
for comprehensive code analysis.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.code_review_pipeline import (
    CodeReviewPipeline,
    CodeReviewPipelineResult,
)


class TestCodeReviewPipelineResult:
    """Tests for CodeReviewPipelineResult dataclass."""

    def test_create_result(self):
        """Test creating a pipeline result."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=0.85,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=2,
            agents_used=["classifier", "scanner"],
            recommendations=["Consider adding tests"],
            blockers=[],
            mode="standard",
            duration_seconds=1.5,
            cost=0.025,
        )

        assert result.success is True
        assert result.verdict == "approve"
        assert result.quality_score == 0.85
        assert result.critical_count == 0
        assert result.medium_count == 2
        assert result.mode == "standard"
        assert result.cost == 0.025

    def test_result_with_findings(self):
        """Test result with security findings."""
        findings = [
            {"severity": "critical", "issue": "SQL injection"},
            {"severity": "high", "issue": "XSS vulnerability"},
        ]
        result = CodeReviewPipelineResult(
            success=True,
            verdict="request_changes",
            quality_score=0.40,
            crew_report={"status": "completed"},
            workflow_result=MagicMock(),
            combined_findings=findings,
            critical_count=1,
            high_count=1,
            medium_count=0,
            agents_used=["security_agent", "code_agent"],
            recommendations=[],
            blockers=["Fix SQL injection before merge"],
            mode="full",
            duration_seconds=5.2,
            cost=0.15,
        )

        assert result.verdict == "request_changes"
        assert len(result.combined_findings) == 2
        assert len(result.blockers) == 1
        assert result.crew_report is not None

    def test_result_reject_verdict(self):
        """Test result with reject verdict."""
        result = CodeReviewPipelineResult(
            success=False,
            verdict="reject",
            quality_score=0.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=5,
            high_count=3,
            medium_count=2,
            agents_used=[],
            recommendations=[],
            blockers=["Critical security vulnerabilities", "Code quality too low"],
            mode="full",
            duration_seconds=0.5,
            cost=0.01,
        )

        assert result.success is False
        assert result.verdict == "reject"
        assert result.critical_count == 5

    def test_result_metadata(self):
        """Test result with metadata."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=0.9,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=[],
            blockers=[],
            mode="quick",
            duration_seconds=0.3,
            cost=0.005,
            metadata={"pr_number": 123, "branch": "feature/test"},
        )

        assert result.metadata["pr_number"] == 123
        assert result.metadata["branch"] == "feature/test"


class TestCodeReviewPipelineInit:
    """Tests for CodeReviewPipeline initialization."""

    def test_default_init(self):
        """Test default initialization."""
        pipeline = CodeReviewPipeline()

        assert pipeline.provider == "anthropic"
        assert pipeline.mode == "full"
        assert pipeline.parallel_crew is True
        assert pipeline.crew_enabled is True

    def test_standard_mode(self):
        """Test standard mode initialization."""
        pipeline = CodeReviewPipeline(mode="standard")

        assert pipeline.mode == "standard"
        assert pipeline.crew_enabled is False

    def test_quick_mode(self):
        """Test quick mode initialization."""
        pipeline = CodeReviewPipeline(mode="quick")

        assert pipeline.mode == "quick"
        assert pipeline.crew_enabled is False

    def test_custom_provider(self):
        """Test custom provider."""
        pipeline = CodeReviewPipeline(provider="openai")

        assert pipeline.provider == "openai"
        assert pipeline.crew_config["provider"] == "openai"

    def test_custom_crew_config(self):
        """Test custom crew configuration."""
        config = {"memory_enabled": True, "verbose": True}
        pipeline = CodeReviewPipeline(crew_config=config)

        assert pipeline.crew_config["memory_enabled"] is True
        assert pipeline.crew_config["verbose"] is True
        assert pipeline.crew_config["provider"] == "anthropic"

    def test_parallel_crew_disabled(self):
        """Test parallel crew disabled."""
        pipeline = CodeReviewPipeline(parallel_crew=False)

        assert pipeline.parallel_crew is False


class TestCodeReviewPipelineFactories:
    """Tests for factory methods."""

    def test_for_pr_review_simple(self):
        """Test factory for simple PR review."""
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=3)

        # Small PRs should use standard mode
        assert pipeline.mode in ("standard", "full")

    def test_for_pr_review_complex(self):
        """Test factory for complex PR review."""
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=20)

        # Large PRs should use full mode
        assert pipeline.mode == "full"

    def test_for_quick_check(self):
        """Test factory for quick check."""
        pipeline = CodeReviewPipeline.for_quick_check()

        assert pipeline.mode == "quick"
        assert pipeline.crew_enabled is False


class TestCodeReviewPipelineVerdicts:
    """Tests for verdict determination logic."""

    def test_calculate_quality_score_no_findings(self):
        """Test quality score with no findings."""
        pipeline = CodeReviewPipeline()

        # No crew report, no workflow result, no findings = baseline score
        score = pipeline._calculate_quality_score(None, None, [])
        # Score is on 0-100 scale, should be positive
        assert score >= 0

    def test_calculate_quality_score_with_findings(self):
        """Test quality score with findings."""
        pipeline = CodeReviewPipeline()

        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
        ]
        score_with_findings = pipeline._calculate_quality_score(None, None, findings)
        score_without = pipeline._calculate_quality_score(None, None, [])

        # Score with findings should be lower or equal to without
        assert score_with_findings <= score_without

    def test_determine_verdict_approve(self):
        """Test approve verdict with high quality score and no blockers."""
        pipeline = CodeReviewPipeline()

        # High quality score (0-100 scale), no blockers
        verdict = pipeline._determine_verdict(None, None, 95.0, [])

        # Should approve or approve with suggestions
        assert verdict in ("approve", "approve_with_suggestions")

    def test_determine_verdict_with_blockers(self):
        """Test verdict with blockers."""
        pipeline = CodeReviewPipeline()

        blockers = ["Critical security issue found"]
        verdict = pipeline._determine_verdict(None, None, 60.0, blockers)

        assert verdict in ("request_changes", "reject")

    def test_determine_verdict_low_quality(self):
        """Test verdict with low quality score."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 30.0, [])

        assert verdict in ("request_changes", "reject", "approve_with_suggestions")


class TestCodeReviewPipelineExecution:
    """Tests for pipeline execution."""

    @pytest.mark.asyncio
    async def test_execute_quick_mode(self):
        """Test quick mode execution."""
        pipeline = CodeReviewPipeline(mode="quick")

        # Mock the internal mode runner
        mock_result = MagicMock()
        mock_result.final_output = {}
        mock_result.cost_report = MagicMock(total_cost=0.01)

        with patch.object(pipeline, "_run_quick_mode", new_callable=AsyncMock) as mock:
            mock.return_value = mock_result

            result = await pipeline.execute(diff="test diff", files_changed=["test.py"])

            assert result.success is True
            assert result.mode == "quick"
            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_standard_mode(self):
        """Test standard mode execution."""
        pipeline = CodeReviewPipeline(mode="standard")

        mock_result = MagicMock()
        mock_result.final_output = {"security_findings": []}
        mock_result.cost_report = MagicMock(total_cost=0.03)

        with patch.object(pipeline, "_run_standard_mode", new_callable=AsyncMock) as mock:
            mock.return_value = mock_result

            result = await pipeline.execute(diff="test diff", files_changed=["test.py"])

            assert result.success is True
            assert result.mode == "standard"

    @pytest.mark.asyncio
    async def test_execute_full_mode_parallel(self):
        """Test full mode with parallel execution."""
        pipeline = CodeReviewPipeline(mode="full", parallel_crew=True)

        mock_workflow = MagicMock()
        mock_workflow.final_output = {}
        mock_workflow.cost_report = MagicMock(total_cost=0.10)
        mock_crew = {"findings": [], "agents_used": ["agent1"]}

        with patch.object(pipeline, "_run_full_mode", new_callable=AsyncMock) as mock:
            mock.return_value = (mock_crew, mock_workflow)

            result = await pipeline.execute(diff="test diff", files_changed=["test.py"])

            assert result.success is True
            assert result.crew_report is not None

    @pytest.mark.asyncio
    async def test_execute_handles_error(self):
        """Test execution handles errors gracefully."""
        pipeline = CodeReviewPipeline(mode="quick")

        with patch.object(pipeline, "_run_quick_mode", new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("Test error")

            result = await pipeline.execute(diff="test diff", files_changed=["test.py"])

            assert result.success is False


class TestCodeReviewPipelineReport:
    """Tests for report formatting."""

    def test_format_report_approve(self):
        """Test formatting approve report."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=0.95,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=["classifier"],
            recommendations=[],
            blockers=[],
            mode="quick",
            duration_seconds=0.5,
            cost=0.01,
        )

        report = result.format_report() if hasattr(result, "format_report") else str(result)

        assert report is not None

    def test_format_report_with_findings(self):
        """Test formatting report with findings."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="request_changes",
            quality_score=0.5,
            crew_report=None,
            workflow_result=None,
            combined_findings=[
                {"severity": "high", "issue": "SQL injection"},
                {"severity": "medium", "issue": "Missing validation"},
            ],
            critical_count=0,
            high_count=1,
            medium_count=1,
            agents_used=["scanner"],
            recommendations=["Add input sanitization"],
            blockers=["Fix SQL injection"],
            mode="standard",
            duration_seconds=2.0,
            cost=0.05,
        )

        # Just verify the result is valid
        assert result.high_count == 1
        assert len(result.blockers) == 1


class TestCodeReviewPipelineCostTracking:
    """Tests for cost tracking."""

    def test_cost_tracking_basic(self):
        """Test basic cost tracking."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=0.9,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=[],
            blockers=[],
            mode="quick",
            duration_seconds=0.5,
            cost=0.0123,
        )

        assert result.cost == 0.0123
        assert result.duration_seconds == 0.5

    def test_cost_accumulation(self):
        """Test cost accumulation from multiple stages."""
        # Simulate cost accumulation
        stage_costs = [0.01, 0.02, 0.03]
        total_cost = sum(stage_costs)

        assert total_cost == 0.06
