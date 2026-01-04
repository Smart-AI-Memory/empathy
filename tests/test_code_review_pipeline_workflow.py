"""Tests for CodeReviewPipeline.

Tests the composite workflow combining CodeReviewCrew with CodeReviewWorkflow.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.code_review_pipeline import (
    CodeReviewPipeline,
    CodeReviewPipelineResult,
    format_code_review_pipeline_report,
)


class TestCodeReviewPipelineResult:
    """Tests for CodeReviewPipelineResult dataclass."""

    def test_basic_creation(self):
        """Test creating a basic result."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=95.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=[],
            blockers=[],
            mode="standard",
            duration_seconds=1.5,
            cost=0.05,
        )

        assert result.success is True
        assert result.verdict == "approve"
        assert result.quality_score == 95.0
        assert result.mode == "standard"

    def test_full_creation(self):
        """Test creating result with all fields."""
        result = CodeReviewPipelineResult(
            success=False,
            verdict="reject",
            quality_score=30.0,
            crew_report={"findings": [], "verdict": "reject"},
            workflow_result=MagicMock(),
            combined_findings=[{"severity": "critical", "title": "Issue"}],
            critical_count=1,
            high_count=3,
            medium_count=5,
            agents_used=["architect", "security"],
            recommendations=["Fix critical issue"],
            blockers=["Critical vulnerability found"],
            mode="full",
            duration_seconds=5.0,
            cost=0.15,
            metadata={"files_reviewed": 10},
        )

        assert result.success is False
        assert result.critical_count == 1
        assert len(result.blockers) == 1
        assert result.metadata["files_reviewed"] == 10


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
        config = {"scan_depth": "thorough", "timeout": 300}
        pipeline = CodeReviewPipeline(crew_config=config)

        assert pipeline.crew_config["scan_depth"] == "thorough"
        assert pipeline.crew_config["timeout"] == 300

    def test_parallel_crew_disabled(self):
        """Test disabling parallel crew."""
        pipeline = CodeReviewPipeline(parallel_crew=False)

        assert pipeline.parallel_crew is False


class TestFactoryMethods:
    """Tests for factory methods."""

    def test_for_pr_review_small_pr(self):
        """Test factory for small PR (<=5 files)."""
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=3)

        assert pipeline.mode == "standard"
        assert pipeline.parallel_crew is True

    def test_for_pr_review_large_pr(self):
        """Test factory for large PR (>5 files)."""
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=10)

        assert pipeline.mode == "full"

    def test_for_pr_review_boundary(self):
        """Test factory at boundary (5 files)."""
        pipeline = CodeReviewPipeline.for_pr_review(files_changed=5)

        assert pipeline.mode == "standard"

    def test_for_quick_check(self):
        """Test factory for quick check."""
        pipeline = CodeReviewPipeline.for_quick_check()

        assert pipeline.mode == "quick"
        assert pipeline.parallel_crew is False

    def test_for_full_review(self):
        """Test factory for full review."""
        pipeline = CodeReviewPipeline.for_full_review()

        assert pipeline.mode == "full"
        assert pipeline.parallel_crew is True


class TestDeduplicateFindings:
    """Tests for findings deduplication."""

    def test_no_duplicates(self):
        """Test with no duplicates."""
        pipeline = CodeReviewPipeline()
        findings = [
            {"file": "a.py", "line": 10, "type": "error"},
            {"file": "b.py", "line": 20, "type": "warning"},
        ]

        result = pipeline._deduplicate_findings(findings)

        assert len(result) == 2

    def test_with_duplicates(self):
        """Test removing duplicates."""
        pipeline = CodeReviewPipeline()
        findings = [
            {"file": "a.py", "line": 10, "type": "error"},
            {"file": "a.py", "line": 10, "type": "error"},  # Duplicate
            {"file": "a.py", "line": 11, "type": "error"},  # Different line
        ]

        result = pipeline._deduplicate_findings(findings)

        assert len(result) == 2

    def test_empty_findings(self):
        """Test with empty findings."""
        pipeline = CodeReviewPipeline()

        result = pipeline._deduplicate_findings([])

        assert result == []


class TestCalculateQualityScore:
    """Tests for quality score calculation."""

    def test_no_inputs(self):
        """Test with no inputs uses fallback."""
        pipeline = CodeReviewPipeline()

        score = pipeline._calculate_quality_score(None, None, [])

        assert score == 100.0

    def test_crew_only(self):
        """Test with crew report only."""
        pipeline = CodeReviewPipeline()
        crew_report = {"quality_score": 80}

        score = pipeline._calculate_quality_score(crew_report, None, [])

        assert score == 80.0

    def test_workflow_only(self):
        """Test with workflow result only."""
        pipeline = CodeReviewPipeline()
        workflow_result = MagicMock()
        workflow_result.final_output = {"security_score": 75}

        score = pipeline._calculate_quality_score(None, workflow_result, [])

        assert score == 75.0

    def test_combined_weighted_average(self):
        """Test weighted average calculation."""
        pipeline = CodeReviewPipeline()
        crew_report = {"quality_score": 80}  # weight 1.5
        workflow_result = MagicMock()
        workflow_result.final_output = {"security_score": 60}  # weight 1.0

        score = pipeline._calculate_quality_score(crew_report, workflow_result, [])

        # (80 * 1.5 + 60 * 1.0) / (1.5 + 1.0) = (120 + 60) / 2.5 = 72
        assert abs(score - 72.0) < 0.1

    def test_fallback_with_findings(self):
        """Test fallback deduction based on findings."""
        pipeline = CodeReviewPipeline()
        findings = [
            {"severity": "critical"},
            {"severity": "high"},
            {"severity": "medium"},
        ]

        score = pipeline._calculate_quality_score(None, None, findings)

        # 100 - 25 (critical) - 15 (high) - 5 (medium) = 55
        assert score == 55.0

    def test_score_capped_at_zero(self):
        """Test score doesn't go below zero."""
        pipeline = CodeReviewPipeline()
        findings = [{"severity": "critical"}] * 10  # 10 * 25 = 250 deduction

        score = pipeline._calculate_quality_score(None, None, findings)

        assert score == 0.0

    def test_score_capped_at_100(self):
        """Test score doesn't exceed 100."""
        pipeline = CodeReviewPipeline()
        crew_report = {"quality_score": 150}  # Invalid high score

        score = pipeline._calculate_quality_score(crew_report, None, [])

        assert score <= 100.0


class TestDetermineVerdict:
    """Tests for verdict determination."""

    def test_approve_with_high_score(self):
        """Test approve with high quality score."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 95.0, [])

        assert verdict == "approve"

    def test_approve_with_suggestions(self):
        """Test approve with suggestions for good score."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 85.0, [])

        assert verdict == "approve_with_suggestions"

    def test_request_changes_for_moderate_score(self):
        """Test request changes for moderate score."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 60.0, [])

        assert verdict == "request_changes"

    def test_reject_for_low_score(self):
        """Test reject for low quality score."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 40.0, [])

        assert verdict == "reject"

    def test_request_changes_with_blockers(self):
        """Test request changes when blockers present."""
        pipeline = CodeReviewPipeline()

        verdict = pipeline._determine_verdict(None, None, 95.0, ["Critical issue"])

        assert verdict == "request_changes"

    def test_crew_verdict_affects_result(self):
        """Test crew verdict affects final verdict."""
        pipeline = CodeReviewPipeline()
        crew_report = {"verdict": "reject"}

        verdict = pipeline._determine_verdict(crew_report, None, 95.0, [])

        assert verdict == "reject"

    def test_workflow_verdict_affects_result(self):
        """Test workflow verdict affects final verdict."""
        pipeline = CodeReviewPipeline()
        workflow_result = MagicMock()
        workflow_result.final_output = {"verdict": "request_changes"}

        verdict = pipeline._determine_verdict(None, workflow_result, 95.0, [])

        assert verdict == "request_changes"

    def test_most_severe_verdict_wins(self):
        """Test most severe verdict is chosen."""
        pipeline = CodeReviewPipeline()
        crew_report = {"verdict": "approve"}
        workflow_result = MagicMock()
        workflow_result.final_output = {"verdict": "reject"}

        verdict = pipeline._determine_verdict(crew_report, workflow_result, 95.0, [])

        assert verdict == "reject"


class TestFormatReport:
    """Tests for report formatting function."""

    def test_format_approve_report(self):
        """Test formatting approve report."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=95.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=[],
            blockers=[],
            mode="standard",
            duration_seconds=1.5,
            cost=0.05,
            metadata={"files_reviewed": 5},
        )

        report = format_code_review_pipeline_report(result)

        assert "CODE REVIEW REPORT" in report
        assert "APPROVE" in report
        assert "95/100" in report
        assert "EXCELLENT" in report

    def test_format_reject_report(self):
        """Test formatting reject report."""
        result = CodeReviewPipelineResult(
            success=False,
            verdict="reject",
            quality_score=30.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[{"severity": "critical", "title": "SQL Injection"}],
            critical_count=1,
            high_count=2,
            medium_count=3,
            agents_used=["security"],
            recommendations=["Fix SQL injection"],
            blockers=["Critical vulnerability"],
            mode="full",
            duration_seconds=3.0,
            cost=0.10,
        )

        report = format_code_review_pipeline_report(result)

        assert "REJECT" in report
        assert "30/100" in report
        assert "POOR" in report
        assert "Critical vulnerability" in report
        assert "BLOCKERS" in report

    def test_format_with_crew_summary(self):
        """Test formatting includes crew summary."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve_with_suggestions",
            quality_score=80.0,
            crew_report={"summary": "Code looks good with minor issues"},
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=2,
            agents_used=["architect", "security"],
            recommendations=["Add unit tests"],
            blockers=[],
            mode="full",
            duration_seconds=2.0,
            cost=0.08,
        )

        report = format_code_review_pipeline_report(result)

        assert "SUMMARY" in report
        assert "Code looks good" in report

    def test_format_with_agents(self):
        """Test formatting includes agents used."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=90.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=["architect", "security", "performance"],
            recommendations=[],
            blockers=[],
            mode="full",
            duration_seconds=4.0,
            cost=0.12,
        )

        report = format_code_review_pipeline_report(result)

        assert "AGENTS USED" in report
        assert "architect" in report
        assert "security" in report

    def test_format_with_recommendations(self):
        """Test formatting includes recommendations."""
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve_with_suggestions",
            quality_score=85.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=["Add error handling", "Improve documentation", "Add tests"],
            blockers=[],
            mode="standard",
            duration_seconds=2.0,
            cost=0.06,
        )

        report = format_code_review_pipeline_report(result)

        assert "RECOMMENDATIONS" in report
        assert "Add error handling" in report

    def test_format_quality_labels(self):
        """Test quality score labels."""
        # Test GOOD label
        result = CodeReviewPipelineResult(
            success=True,
            verdict="approve",
            quality_score=75.0,
            crew_report=None,
            workflow_result=None,
            combined_findings=[],
            critical_count=0,
            high_count=0,
            medium_count=0,
            agents_used=[],
            recommendations=[],
            blockers=[],
            mode="standard",
            duration_seconds=1.0,
            cost=0.03,
        )

        report = format_code_review_pipeline_report(result)
        assert "GOOD" in report

        # Test NEEDS WORK label
        result.quality_score = 55.0
        report = format_code_review_pipeline_report(result)
        assert "NEEDS WORK" in report


class TestPipelineExecution:
    """Tests for pipeline execution."""

    @pytest.mark.asyncio
    async def test_execute_standard_mode(self):
        """Test execute in standard mode."""
        pipeline = CodeReviewPipeline(mode="standard")

        mock_workflow_result = MagicMock()
        mock_workflow_result.final_output = {"security_score": 85}
        mock_workflow_result.cost_report.total_cost = 0.05

        with patch("src.empathy_os.workflows.code_review.CodeReviewWorkflow") as mock_cls:
            mock_cls.return_value.execute = AsyncMock(return_value=mock_workflow_result)

            result = await pipeline.execute(diff="def hello(): pass")

            assert result.success is True
            assert result.mode == "standard"

    @pytest.mark.asyncio
    async def test_execute_handles_error(self):
        """Test execute handles errors gracefully."""
        pipeline = CodeReviewPipeline(mode="standard")

        with patch("src.empathy_os.workflows.code_review.CodeReviewWorkflow") as mock_cls:
            mock_cls.return_value.execute = AsyncMock(side_effect=Exception("Review failed"))

            result = await pipeline.execute(diff="def hello(): pass")

            assert result.success is False
            assert result.verdict == "reject"
            assert any("Pipeline error" in b for b in result.blockers)

    @pytest.mark.asyncio
    async def test_execute_aggregates_findings(self):
        """Test execute aggregates findings correctly."""
        pipeline = CodeReviewPipeline(mode="standard")

        mock_workflow_result = MagicMock()
        mock_workflow_result.final_output = {
            "security_score": 70,
            "security_findings": [
                {"severity": "high", "file": "a.py", "line": 10, "type": "sql"},
                {"severity": "medium", "file": "b.py", "line": 20, "type": "xss"},
            ],
        }
        mock_workflow_result.cost_report.total_cost = 0.05

        with patch("src.empathy_os.workflows.code_review.CodeReviewWorkflow") as mock_cls:
            mock_cls.return_value.execute = AsyncMock(return_value=mock_workflow_result)

            result = await pipeline.execute(diff="code here")

            assert len(result.combined_findings) == 2
            assert result.high_count == 1
            assert result.medium_count == 1

    @pytest.mark.asyncio
    async def test_execute_creates_blockers_for_critical(self):
        """Test execute creates blockers for critical issues."""
        pipeline = CodeReviewPipeline(mode="standard")

        mock_workflow_result = MagicMock()
        mock_workflow_result.final_output = {
            "security_score": 50,
            "security_findings": [
                {"severity": "critical", "file": "a.py", "line": 10, "type": "rce"},
            ],
        }
        mock_workflow_result.cost_report.total_cost = 0.05

        with patch("src.empathy_os.workflows.code_review.CodeReviewWorkflow") as mock_cls:
            mock_cls.return_value.execute = AsyncMock(return_value=mock_workflow_result)

            result = await pipeline.execute(diff="code here")

            assert result.critical_count == 1
            assert any("critical" in b.lower() for b in result.blockers)

    @pytest.mark.asyncio
    async def test_execute_adds_formatted_report(self):
        """Test execute adds formatted report to metadata."""
        pipeline = CodeReviewPipeline(mode="standard")

        mock_workflow_result = MagicMock()
        mock_workflow_result.final_output = {"security_score": 90}
        mock_workflow_result.cost_report.total_cost = 0.05

        with patch("src.empathy_os.workflows.code_review.CodeReviewWorkflow") as mock_cls:
            mock_cls.return_value.execute = AsyncMock(return_value=mock_workflow_result)

            result = await pipeline.execute(diff="code")

            assert "formatted_report" in result.metadata
            assert "CODE REVIEW REPORT" in result.metadata["formatted_report"]
