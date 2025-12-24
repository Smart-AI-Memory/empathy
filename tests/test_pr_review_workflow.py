"""
Tests for PRReviewWorkflow.

Tests the combined code review + security audit workflow for
comprehensive PR analysis.
"""

import tempfile
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.pr_review import (
    PRReviewResult,
    PRReviewWorkflow,
)


class TestPRReviewResult:
    """Tests for PRReviewResult dataclass."""

    def test_create_result(self):
        """Test creating a PRReviewResult."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=90.0,
            security_risk_score=15.0,
            combined_score=88.0,
            code_review={"findings": []},
            security_audit={"findings": []},
            all_findings=[],
            code_findings=[],
            security_findings=[],
            critical_count=0,
            high_count=0,
            blockers=[],
            warnings=[],
            recommendations=[],
            summary="PR is ready to merge.",
            agents_used=["code_reviewer"],
            duration_seconds=2.5,
        )

        assert result.success is True
        assert result.verdict == "approve"
        assert result.code_quality_score == 90.0
        assert result.security_risk_score == 15.0
        assert result.combined_score == 88.0
        assert result.critical_count == 0
        assert result.metadata == {}

    def test_result_with_findings(self):
        """Test result with findings."""
        findings = [
            {"type": "code_smell", "severity": "medium", "file": "main.py"},
            {"type": "sql_injection", "severity": "critical", "file": "db.py"},
            {"type": "unused_import", "severity": "low", "file": "utils.py"},
        ]

        result = PRReviewResult(
            success=True,
            verdict="request_changes",
            code_quality_score=70.0,
            security_risk_score=60.0,
            combined_score=55.0,
            code_review=None,
            security_audit=None,
            all_findings=findings,
            code_findings=findings[:2],
            security_findings=findings[2:],
            critical_count=1,
            high_count=0,
            blockers=["1 critical issue(s) must be fixed"],
            warnings=[],
            recommendations=["Fix SQL injection"],
            summary="PR requires changes.",
            agents_used=[],
            duration_seconds=3.0,
        )

        assert len(result.all_findings) == 3
        assert result.critical_count == 1
        assert len(result.blockers) == 1
        assert result.verdict == "request_changes"

    def test_result_with_metadata(self):
        """Test result with custom metadata."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=95.0,
            security_risk_score=10.0,
            combined_score=92.0,
            code_review=None,
            security_audit=None,
            all_findings=[],
            code_findings=[],
            security_findings=[],
            critical_count=0,
            high_count=0,
            blockers=[],
            warnings=[],
            recommendations=[],
            summary="Clean PR",
            agents_used=[],
            duration_seconds=1.0,
            metadata={"parallel_execution": True, "files_changed": 3},
        )

        assert result.metadata["parallel_execution"] is True
        assert result.metadata["files_changed"] == 3


class TestPRReviewWorkflowInit:
    """Tests for PRReviewWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = PRReviewWorkflow()

        assert workflow.provider == "anthropic"
        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is True
        assert workflow.parallel is True

    def test_custom_init(self):
        """Test custom initialization."""
        workflow = PRReviewWorkflow(
            provider="openai",
            use_code_crew=False,
            use_security_crew=True,
            parallel=False,
        )

        assert workflow.provider == "openai"
        assert workflow.use_code_crew is False
        assert workflow.use_security_crew is True
        assert workflow.parallel is False

    def test_crew_configs(self):
        """Test crew configuration injection."""
        code_config = {"verbose": True}
        security_config = {"strict_mode": True}

        workflow = PRReviewWorkflow(
            provider="anthropic",
            code_crew_config=code_config,
            security_crew_config=security_config,
        )

        assert workflow.code_crew_config["provider"] == "anthropic"
        assert workflow.code_crew_config["verbose"] is True
        assert workflow.security_crew_config["strict_mode"] is True


class TestPRReviewWorkflowFactories:
    """Tests for factory methods."""

    def test_for_comprehensive_review(self):
        """Test comprehensive review factory."""
        workflow = PRReviewWorkflow.for_comprehensive_review()

        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is True
        assert workflow.parallel is True

    def test_for_security_focused(self):
        """Test security-focused factory."""
        workflow = PRReviewWorkflow.for_security_focused()

        assert workflow.use_code_crew is False
        assert workflow.use_security_crew is True
        assert workflow.parallel is False

    def test_for_code_quality_focused(self):
        """Test code quality-focused factory."""
        workflow = PRReviewWorkflow.for_code_quality_focused()

        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is False
        assert workflow.parallel is False


class TestPRReviewWorkflowScoring:
    """Tests for scoring methods."""

    def test_get_code_quality_score_with_review(self):
        """Test extracting code quality score from review."""
        workflow = PRReviewWorkflow()
        review = {"quality_score": 82.5}

        score = workflow._get_code_quality_score(review)

        assert score == 82.5

    def test_get_code_quality_score_no_review(self):
        """Test default code quality score without review."""
        workflow = PRReviewWorkflow()

        score = workflow._get_code_quality_score(None)

        assert score == 85.0

    def test_get_security_risk_score_with_audit(self):
        """Test extracting security risk score from audit."""
        workflow = PRReviewWorkflow()
        audit = {"risk_score": 35.0}

        score = workflow._get_security_risk_score(audit)

        assert score == 35.0

    def test_get_security_risk_score_no_audit(self):
        """Test default security risk score without audit."""
        workflow = PRReviewWorkflow()

        score = workflow._get_security_risk_score(None)

        assert score == 20.0

    def test_calculate_combined_score(self):
        """Test combined score calculation."""
        workflow = PRReviewWorkflow()

        # Perfect scores
        score = workflow._calculate_combined_score(100.0, 0.0)
        assert score == 100.0

        # Low quality, high risk
        score = workflow._calculate_combined_score(50.0, 80.0)
        assert score == 33.5  # (50 * 0.45) + (20 * 0.55)

        # High quality, low risk
        score = workflow._calculate_combined_score(90.0, 20.0)
        assert score == 84.5  # (90 * 0.45) + (80 * 0.55)


class TestPRReviewWorkflowVerdict:
    """Tests for verdict determination."""

    def test_verdict_approve(self):
        """Test approve verdict."""
        workflow = PRReviewWorkflow()

        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 10},
            combined_score=90,
            blockers=[],
        )

        assert verdict == "approve"

    def test_verdict_reject_high_risk(self):
        """Test reject verdict due to high risk."""
        workflow = PRReviewWorkflow()

        verdict = workflow._determine_verdict(
            code_review=None,
            security_audit={"risk_score": 75},
            combined_score=40,
            blockers=[],
        )

        assert verdict == "reject"

    def test_verdict_request_changes_blockers(self):
        """Test request_changes verdict due to blockers."""
        workflow = PRReviewWorkflow()

        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 10},
            combined_score=90,
            blockers=["Critical issue found"],
        )

        assert verdict == "request_changes"

    def test_verdict_approve_with_suggestions(self):
        """Test approve_with_suggestions verdict."""
        workflow = PRReviewWorkflow()

        verdict = workflow._determine_verdict(
            code_review=None,
            security_audit={"risk_score": 40},
            combined_score=80,
            blockers=[],
        )

        assert verdict == "approve_with_suggestions"


class TestPRReviewWorkflowMerge:
    """Tests for findings merge functionality."""

    def test_merge_findings_empty(self):
        """Test merging empty findings."""
        workflow = PRReviewWorkflow()

        merged = workflow._merge_findings([], [])

        assert merged == []

    def test_merge_findings_tags_source(self):
        """Test that findings are tagged with source."""
        workflow = PRReviewWorkflow()

        code = [{"type": "bug", "file": "a.py", "line": 1}]
        security = [{"type": "vuln", "file": "b.py", "line": 2}]

        merged = workflow._merge_findings(code, security)

        assert merged[0]["source"] in ["code_review", "security_audit"]
        assert merged[1]["source"] in ["code_review", "security_audit"]

    def test_merge_findings_deduplicates(self):
        """Test deduplication of findings."""
        workflow = PRReviewWorkflow()

        # Same file, line, type should be deduplicated
        code = [{"type": "issue", "file": "a.py", "line": 10}]
        security = [{"type": "issue", "file": "a.py", "line": 10}]

        merged = workflow._merge_findings(code, security)

        assert len(merged) == 1

    def test_merge_findings_sorts_by_severity(self):
        """Test that findings are sorted by severity."""
        workflow = PRReviewWorkflow()

        code = [
            {"type": "low", "file": "a.py", "line": 1, "severity": "low"},
            {"type": "critical", "file": "b.py", "line": 2, "severity": "critical"},
        ]
        security = [
            {"type": "medium", "file": "c.py", "line": 3, "severity": "medium"},
        ]

        merged = workflow._merge_findings(code, security)

        assert merged[0]["severity"] == "critical"
        assert merged[1]["severity"] == "medium"
        assert merged[2]["severity"] == "low"


class TestPRReviewWorkflowSummary:
    """Tests for summary generation."""

    def test_generate_summary_approve(self):
        """Test summary for approved PR."""
        workflow = PRReviewWorkflow()

        summary = workflow._generate_summary(
            verdict="approve",
            code_quality=95,
            security_risk=5,
            total_findings=0,
            critical_count=0,
            high_count=0,
        )

        assert "ready to merge" in summary
        assert "Code quality: 95/100" in summary
        assert "Security risk: 5/100" in summary

    def test_generate_summary_with_findings(self):
        """Test summary with findings."""
        workflow = PRReviewWorkflow()

        summary = workflow._generate_summary(
            verdict="request_changes",
            code_quality=70,
            security_risk=40,
            total_findings=5,
            critical_count=1,
            high_count=2,
        )

        assert "requires changes" in summary
        assert "5 finding(s)" in summary
        assert "1 critical" in summary


class TestPRReviewWorkflowExecution:
    """Tests for workflow execution."""

    @pytest.mark.asyncio
    async def test_execute_no_crews(self):
        """Test execution when no crews are enabled."""
        workflow = PRReviewWorkflow(
            use_code_crew=False,
            use_security_crew=False,
        )

        result = await workflow.execute(
            diff="test diff",
            files_changed=["test.py"],
        )

        assert result.success is True
        assert result.code_review is None
        assert result.security_audit is None

    @pytest.mark.asyncio
    async def test_execute_with_git_diff(self):
        """Test execution with auto-generated git diff."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = PRReviewWorkflow(
                use_code_crew=False,
                use_security_crew=False,
            )

            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock(
                    stdout="diff --git a/file.py",
                    returncode=0,
                )

                result = await workflow.execute(
                    target_path=tmpdir,
                )

                assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_parallel_mode(self):
        """Test parallel execution mode."""
        workflow = PRReviewWorkflow(
            use_code_crew=True,
            use_security_crew=True,
            parallel=True,
        )

        with patch.object(workflow, "_run_parallel", new_callable=AsyncMock) as mock:
            mock.return_value = (
                {"findings": [], "quality_score": 90, "agents_used": []},
                {"findings": [], "risk_score": 10, "agents_used": []},
            )

            result = await workflow.execute(
                diff="test diff",
                files_changed=["test.py"],
            )

            mock.assert_called_once()
            assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_sequential_mode(self):
        """Test sequential execution mode."""
        workflow = PRReviewWorkflow(
            use_code_crew=True,
            use_security_crew=True,
            parallel=False,
        )

        with patch.object(workflow, "_run_code_review", new_callable=AsyncMock) as mock_code:
            with patch.object(workflow, "_run_security_audit", new_callable=AsyncMock) as mock_sec:
                mock_code.return_value = {"findings": [], "quality_score": 90, "agents_used": []}
                mock_sec.return_value = {"findings": [], "risk_score": 10, "agents_used": []}

                result = await workflow.execute(
                    diff="test diff",
                    files_changed=["test.py"],
                )

                mock_code.assert_called_once()
                mock_sec.assert_called_once()
                assert result.success is True

    @pytest.mark.asyncio
    async def test_execute_handles_exception(self):
        """Test execution handles exceptions gracefully."""
        workflow = PRReviewWorkflow()

        with patch.object(workflow, "_run_parallel", new_callable=AsyncMock) as mock:
            mock.side_effect = Exception("Test error")

            result = await workflow.execute(
                diff="test diff",
            )

            assert result.success is False
            assert result.verdict == "reject"
            assert "Test error" in result.blockers[0]

    @pytest.mark.asyncio
    async def test_execute_collects_recommendations(self):
        """Test that recommendations are collected from findings."""
        workflow = PRReviewWorkflow(
            use_code_crew=True,
            use_security_crew=True,
            parallel=False,
        )

        code_review = {
            "findings": [
                {"suggestion": "Use type hints"},
                {"suggestion": "Add docstring"},
            ],
            "quality_score": 80,
            "agents_used": [],
        }
        security_audit = {
            "findings": [
                {"remediation": "Escape user input"},
            ],
            "risk_score": 30,
            "agents_used": [],
        }

        with patch.object(workflow, "_run_code_review", new_callable=AsyncMock) as mock_code:
            with patch.object(workflow, "_run_security_audit", new_callable=AsyncMock) as mock_sec:
                mock_code.return_value = code_review
                mock_sec.return_value = security_audit

                result = await workflow.execute(
                    diff="test diff",
                )

                assert "Use type hints" in result.recommendations
                assert "Escape user input" in result.recommendations


class TestPRReviewWorkflowParallel:
    """Tests for parallel execution."""

    @pytest.mark.asyncio
    async def test_run_parallel_success(self):
        """Test successful parallel execution."""
        workflow = PRReviewWorkflow()

        with patch.object(workflow, "_run_code_review", new_callable=AsyncMock) as mock_code:
            with patch.object(workflow, "_run_security_audit", new_callable=AsyncMock) as mock_sec:
                mock_code.return_value = {"findings": []}
                mock_sec.return_value = {"findings": []}

                code_result, sec_result = await workflow._run_parallel(
                    "diff",
                    ["file.py"],
                    ".",
                )

                assert code_result is not None
                assert sec_result is not None

    @pytest.mark.asyncio
    async def test_run_parallel_one_fails(self):
        """Test parallel execution when one task fails."""
        workflow = PRReviewWorkflow()

        with patch.object(workflow, "_run_code_review", new_callable=AsyncMock) as mock_code:
            with patch.object(workflow, "_run_security_audit", new_callable=AsyncMock) as mock_sec:
                mock_code.side_effect = Exception("Code review failed")
                mock_sec.return_value = {"findings": []}

                code_result, sec_result = await workflow._run_parallel(
                    "diff",
                    ["file.py"],
                    ".",
                )

                assert code_result is None  # Failed
                assert sec_result is not None  # Succeeded
