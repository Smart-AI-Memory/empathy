"""Tests for src/empathy_os/workflows/pr_review.py

Tests the PRReviewWorkflow and PRReviewResult classes.
"""

import sys
from unittest.mock import AsyncMock, patch

import pytest

from empathy_os.workflows.pr_review import PRReviewResult, PRReviewWorkflow, format_pr_review_report


class TestPRReviewResult:
    """Tests for PRReviewResult dataclass."""

    def test_basic_creation(self):
        """Test basic PRReviewResult creation."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=90.0,
            security_risk_score=10.0,
            combined_score=85.0,
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
            summary="PR is ready to merge",
            agents_used=[],
            duration_seconds=5.0,
        )
        assert result.success is True
        assert result.verdict == "approve"
        assert result.code_quality_score == 90.0
        assert result.security_risk_score == 10.0
        assert result.combined_score == 85.0

    def test_default_cost(self):
        """Test cost defaults to 0.0."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=85.0,
            security_risk_score=15.0,
            combined_score=80.0,
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
            summary="Test",
            agents_used=[],
            duration_seconds=1.0,
        )
        assert result.cost == 0.0

    def test_default_metadata(self):
        """Test metadata defaults to empty dict."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=85.0,
            security_risk_score=15.0,
            combined_score=80.0,
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
            summary="Test",
            agents_used=[],
            duration_seconds=1.0,
        )
        assert result.metadata == {}

    def test_with_findings(self):
        """Test PRReviewResult with findings."""
        findings = [
            {"title": "SQL Injection", "severity": "critical", "source": "security_audit"},
            {"title": "Missing Tests", "severity": "high", "source": "code_review"},
        ]
        result = PRReviewResult(
            success=True,
            verdict="request_changes",
            code_quality_score=70.0,
            security_risk_score=60.0,
            combined_score=55.0,
            code_review={"quality_score": 70.0},
            security_audit={"risk_score": 60.0},
            all_findings=findings,
            code_findings=[findings[1]],
            security_findings=[findings[0]],
            critical_count=1,
            high_count=1,
            blockers=["1 critical issue(s) must be fixed"],
            warnings=[],
            recommendations=["Fix SQL injection", "Add tests"],
            summary="PR requires changes",
            agents_used=["security_agent", "code_agent"],
            duration_seconds=10.0,
        )
        assert len(result.all_findings) == 2
        assert result.critical_count == 1
        assert result.high_count == 1
        assert len(result.blockers) == 1

    def test_with_custom_cost(self):
        """Test PRReviewResult with custom cost."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=95.0,
            security_risk_score=5.0,
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
            agents_used=["analyzer"],
            duration_seconds=3.0,
            cost=0.0025,
        )
        assert result.cost == 0.0025


class TestPRReviewWorkflowInit:
    """Tests for PRReviewWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = PRReviewWorkflow()
        assert workflow.provider == "anthropic"
        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is True
        assert workflow.parallel is True

    def test_custom_provider(self):
        """Test custom provider initialization."""
        workflow = PRReviewWorkflow(provider="openai")
        assert workflow.provider == "openai"
        assert workflow.code_crew_config["provider"] == "openai"
        assert workflow.security_crew_config["provider"] == "openai"

    def test_disable_code_crew(self):
        """Test disabling code crew."""
        workflow = PRReviewWorkflow(use_code_crew=False)
        assert workflow.use_code_crew is False
        assert workflow.use_security_crew is True

    def test_disable_security_crew(self):
        """Test disabling security crew."""
        workflow = PRReviewWorkflow(use_security_crew=False)
        assert workflow.use_code_crew is True
        assert workflow.use_security_crew is False

    def test_disable_parallel(self):
        """Test disabling parallel execution."""
        workflow = PRReviewWorkflow(parallel=False)
        assert workflow.parallel is False

    def test_custom_crew_configs(self):
        """Test custom crew configurations."""
        workflow = PRReviewWorkflow(
            code_crew_config={"depth": "thorough"},
            security_crew_config={"focus": "owasp"},
        )
        assert workflow.code_crew_config["depth"] == "thorough"
        assert workflow.security_crew_config["focus"] == "owasp"


class TestPRReviewWorkflowFactories:
    """Tests for PRReviewWorkflow factory methods."""

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
    """Tests for PRReviewWorkflow scoring methods."""

    def test_get_code_quality_score_with_review(self):
        """Test getting code quality score from review."""
        workflow = PRReviewWorkflow()
        code_review = {"quality_score": 92.5}
        score = workflow._get_code_quality_score(code_review)
        assert score == 92.5

    def test_get_code_quality_score_no_review(self):
        """Test default code quality score when no review."""
        workflow = PRReviewWorkflow()
        score = workflow._get_code_quality_score(None)
        assert score == 85.0  # Default

    def test_get_security_risk_score_with_audit(self):
        """Test getting security risk score from audit."""
        workflow = PRReviewWorkflow()
        security_audit = {"risk_score": 45.0}
        score = workflow._get_security_risk_score(security_audit)
        assert score == 45.0

    def test_get_security_risk_score_no_audit(self):
        """Test default security risk score when no audit."""
        workflow = PRReviewWorkflow()
        score = workflow._get_security_risk_score(None)
        assert score == 20.0  # Default

    def test_calculate_combined_score_perfect(self):
        """Test combined score calculation with perfect scores."""
        workflow = PRReviewWorkflow()
        score = workflow._calculate_combined_score(100.0, 0.0)
        assert score == pytest.approx(100.0)

    def test_calculate_combined_score_worst(self):
        """Test combined score calculation with worst scores."""
        workflow = PRReviewWorkflow()
        score = workflow._calculate_combined_score(0.0, 100.0)
        assert score == pytest.approx(0.0)

    def test_calculate_combined_score_balanced(self):
        """Test combined score calculation with balanced scores."""
        workflow = PRReviewWorkflow()
        score = workflow._calculate_combined_score(80.0, 20.0)
        # 80 * 0.45 + (100 - 20) * 0.55 = 36 + 44 = 80
        assert score == pytest.approx(80.0)

    def test_calculate_combined_score_clamped(self):
        """Test combined score is clamped to 0-100 range."""
        workflow = PRReviewWorkflow()
        # Even with extreme values, should be clamped
        score = workflow._calculate_combined_score(100.0, 0.0)
        assert 0.0 <= score <= 100.0


class TestPRReviewWorkflowVerdict:
    """Tests for PRReviewWorkflow verdict determination."""

    def test_verdict_approve_high_score(self):
        """Test approve verdict with high combined score."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 10},
            combined_score=90.0,
            blockers=[],
        )
        assert verdict == "approve"

    def test_verdict_request_changes_with_blockers(self):
        """Test request_changes verdict with blockers."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 20},
            combined_score=85.0,
            blockers=["1 critical issue"],
        )
        # Blockers force at least request_changes
        assert verdict in ["request_changes", "reject"]

    def test_verdict_reject_low_score(self):
        """Test reject verdict with low combined score."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review=None,
            security_audit={"risk_score": 80},
            combined_score=40.0,
            blockers=[],
        )
        assert verdict == "reject"

    def test_verdict_approve_with_suggestions(self):
        """Test approve_with_suggestions verdict."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 35},
            combined_score=75.0,
            blockers=[],
        )
        assert verdict == "approve_with_suggestions"

    def test_verdict_high_security_risk(self):
        """Test verdict with high security risk."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 75},
            combined_score=60.0,
            blockers=[],
        )
        assert verdict == "reject"

    def test_verdict_priority_ordering(self):
        """Test that most severe verdict is returned."""
        workflow = PRReviewWorkflow()
        verdict = workflow._determine_verdict(
            code_review={"verdict": "approve"},
            security_audit={"risk_score": 55},  # Triggers request_changes
            combined_score=85.0,  # Would be approve
            blockers=[],
        )
        # request_changes from security takes priority over approve
        assert verdict in ["request_changes", "approve_with_suggestions"]


class TestPRReviewWorkflowMergeFindings:
    """Tests for PRReviewWorkflow finding merging."""

    def test_merge_findings_tags_source(self):
        """Test findings are tagged with source."""
        workflow = PRReviewWorkflow()
        code_findings = [{"title": "Code Issue"}]
        security_findings = [{"title": "Security Issue"}]

        merged = workflow._merge_findings(code_findings, security_findings)

        code_finding = next(f for f in merged if f["title"] == "Code Issue")
        security_finding = next(f for f in merged if f["title"] == "Security Issue")

        assert code_finding["source"] == "code_review"
        assert security_finding["source"] == "security_audit"

    def test_merge_findings_deduplication(self):
        """Test duplicate findings are removed."""
        workflow = PRReviewWorkflow()
        code_findings = [{"title": "Duplicate", "file": "a.py", "line": 10, "type": "bug"}]
        security_findings = [{"title": "Duplicate", "file": "a.py", "line": 10, "type": "bug"}]

        merged = workflow._merge_findings(code_findings, security_findings)
        assert len(merged) == 1

    def test_merge_findings_severity_sorting(self):
        """Test findings are sorted by severity."""
        workflow = PRReviewWorkflow()
        code_findings = [
            {"title": "Low", "severity": "low"},
            {"title": "High", "severity": "high"},
        ]
        security_findings = [
            {"title": "Critical", "severity": "critical"},
            {"title": "Medium", "severity": "medium"},
        ]

        merged = workflow._merge_findings(code_findings, security_findings)

        # Critical should be first
        assert merged[0]["severity"] == "critical"
        # Low should be last
        assert merged[-1]["severity"] == "low"


class TestPRReviewWorkflowSummary:
    """Tests for PRReviewWorkflow summary generation."""

    def test_generate_summary_approve(self):
        """Test summary for approve verdict."""
        workflow = PRReviewWorkflow()
        summary = workflow._generate_summary(
            verdict="approve",
            code_quality=95.0,
            security_risk=5.0,
            total_findings=0,
            critical_count=0,
            high_count=0,
        )
        assert "ready to merge" in summary
        assert "95/100" in summary

    def test_generate_summary_with_findings(self):
        """Test summary includes finding counts."""
        workflow = PRReviewWorkflow()
        summary = workflow._generate_summary(
            verdict="request_changes",
            code_quality=70.0,
            security_risk=50.0,
            total_findings=5,
            critical_count=1,
            high_count=2,
        )
        assert "5 finding" in summary
        assert "1 critical" in summary

    def test_generate_summary_reject(self):
        """Test summary for reject verdict."""
        workflow = PRReviewWorkflow()
        summary = workflow._generate_summary(
            verdict="reject",
            code_quality=40.0,
            security_risk=80.0,
            total_findings=10,
            critical_count=3,
            high_count=5,
        )
        assert "critical issues" in summary.lower() or "should not be merged" in summary.lower()


class TestFormatPRReviewReport:
    """Tests for format_pr_review_report function."""

    def test_format_report_basic(self):
        """Test basic report formatting."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=90.0,
            security_risk_score=10.0,
            combined_score=85.0,
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
            summary="PR is ready to merge",
            agents_used=["analyzer"],
            duration_seconds=5.0,
            cost=0.001,
        )
        report = format_pr_review_report(result)

        assert "PR REVIEW REPORT" in report
        assert "VERDICT: APPROVE" in report
        assert "Code Quality" in report
        assert "Security Risk" in report

    def test_format_report_with_blockers(self):
        """Test report formatting with blockers."""
        result = PRReviewResult(
            success=True,
            verdict="request_changes",
            code_quality_score=60.0,
            security_risk_score=50.0,
            combined_score=55.0,
            code_review=None,
            security_audit=None,
            all_findings=[],
            code_findings=[],
            security_findings=[],
            critical_count=2,
            high_count=3,
            blockers=["2 critical issues must be fixed"],
            warnings=["Security crew unavailable"],
            recommendations=["Fix injection vulnerability"],
            summary="PR requires changes",
            agents_used=[],
            duration_seconds=10.0,
        )
        report = format_pr_review_report(result)

        assert "BLOCKERS" in report
        assert "critical issues" in report.lower()
        assert "WARNINGS" in report

    def test_format_report_with_findings(self):
        """Test report formatting with findings."""
        result = PRReviewResult(
            success=True,
            verdict="request_changes",
            code_quality_score=70.0,
            security_risk_score=40.0,
            combined_score=65.0,
            code_review=None,
            security_audit=None,
            all_findings=[
                {"title": "SQL Injection", "severity": "critical"},
                {"title": "Missing Validation", "severity": "high"},
            ],
            code_findings=[{"title": "Missing Validation", "severity": "high"}],
            security_findings=[{"title": "SQL Injection", "severity": "critical"}],
            critical_count=1,
            high_count=1,
            blockers=[],
            warnings=[],
            recommendations=[],
            summary="Issues found",
            agents_used=["security_agent", "code_agent"],
            duration_seconds=8.0,
        )
        report = format_pr_review_report(result)

        assert "FINDINGS" in report
        assert "Critical: 1" in report
        assert "High: 1" in report

    def test_format_report_emoji_verdicts(self):
        """Test report uses correct emoji for each verdict."""
        verdicts = ["approve", "approve_with_suggestions", "request_changes", "reject"]
        expected_emojis = ["✅", "🟡", "🟠", "🔴"]

        for verdict, emoji in zip(verdicts, expected_emojis, strict=False):
            result = PRReviewResult(
                success=True,
                verdict=verdict,
                code_quality_score=50.0,
                security_risk_score=50.0,
                combined_score=50.0,
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
                summary="Test",
                agents_used=[],
                duration_seconds=1.0,
            )
            report = format_pr_review_report(result)
            assert emoji in report

    def test_format_report_duration_and_cost(self):
        """Test report includes duration and cost."""
        result = PRReviewResult(
            success=True,
            verdict="approve",
            code_quality_score=90.0,
            security_risk_score=10.0,
            combined_score=85.0,
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
            duration_seconds=5.5,
            cost=0.0025,
        )
        report = format_pr_review_report(result)

        assert "5500ms" in report  # 5.5 * 1000
        assert "$0.0025" in report


class TestPRReviewWorkflowExecute:
    """Tests for PRReviewWorkflow execute method."""

    @pytest.mark.asyncio
    async def test_execute_graceful_crew_failures(self):
        """Test execute handles crew failures gracefully."""
        workflow = PRReviewWorkflow()

        # Mock both crew methods to raise exceptions
        with (
            patch.object(
                workflow,
                "_run_code_review",
                side_effect=Exception("Code review failed"),
            ),
            patch.object(
                workflow,
                "_run_security_audit",
                side_effect=Exception("Audit failed"),
            ),
        ):
            result = await workflow.execute(
                diff="test diff",
                files_changed=["test.py"],
                target_path=".",
            )

        # The workflow is resilient - it returns success even when crews fail
        # but adds warnings about unavailable crews
        assert result.success is True
        assert result.code_review is None
        assert result.security_audit is None
        assert any("unavailable" in w.lower() for w in result.warnings)

    @pytest.mark.asyncio
    async def test_execute_no_crews_enabled(self):
        """Test execute with no crews enabled."""
        workflow = PRReviewWorkflow(
            use_code_crew=False,
            use_security_crew=False,
        )

        result = await workflow.execute(
            diff="test diff",
            files_changed=["test.py"],
            target_path=".",
        )

        # Should still succeed but with default scores
        assert result.success is True
        assert result.code_review is None
        assert result.security_audit is None

    @pytest.mark.asyncio
    async def test_execute_collects_metadata(self):
        """Test execute collects metadata."""
        workflow = PRReviewWorkflow(
            use_code_crew=False,
            use_security_crew=False,
        )

        result = await workflow.execute(
            diff="test diff",
            files_changed=["a.py", "b.py"],
            target_path=".",
        )

        assert "files_changed" in result.metadata
        assert result.metadata["files_changed"] == 2
        assert result.metadata["code_crew_enabled"] is False
        assert result.metadata["security_crew_enabled"] is False

    @pytest.mark.asyncio
    @pytest.mark.skipif(sys.platform == "win32", reason="Duration timing unreliable on Windows")
    async def test_execute_duration_tracked(self):
        """Test execute tracks duration."""
        workflow = PRReviewWorkflow(
            use_code_crew=False,
            use_security_crew=False,
        )

        result = await workflow.execute(
            diff="test",
            files_changed=[],
            target_path=".",
        )

        assert result.duration_seconds > 0

    @pytest.mark.asyncio
    async def test_execute_with_code_crew_only(self):
        """Test execute with only code crew."""
        workflow = PRReviewWorkflow(
            use_code_crew=True,
            use_security_crew=False,
        )

        mock_review = {
            "quality_score": 85.0,
            "findings": [{"title": "Style Issue", "severity": "low"}],
            "verdict": "approve_with_suggestions",
            "agents_used": ["style_agent"],
        }

        with patch.object(
            workflow,
            "_run_code_review",
            new_callable=AsyncMock,
            return_value=mock_review,
        ):
            result = await workflow.execute(
                diff="test diff",
                files_changed=["test.py"],
                target_path=".",
            )

        assert result.code_review is not None
        assert result.security_audit is None
        assert len(result.code_findings) == 1

    @pytest.mark.asyncio
    async def test_execute_with_security_crew_only(self):
        """Test execute with only security crew."""
        workflow = PRReviewWorkflow(
            use_code_crew=False,
            use_security_crew=True,
        )

        mock_audit = {
            "risk_score": 25.0,
            "findings": [{"title": "Weak Hash", "severity": "medium", "remediation": "Use bcrypt"}],
            "agents_used": ["vuln_scanner"],
        }

        with patch.object(
            workflow,
            "_run_security_audit",
            new_callable=AsyncMock,
            return_value=mock_audit,
        ):
            result = await workflow.execute(
                diff="test diff",
                files_changed=["test.py"],
                target_path=".",
            )

        assert result.code_review is None
        assert result.security_audit is not None
        assert len(result.security_findings) == 1
        # Check that bcrypt appears in at least one recommendation
        assert any("bcrypt" in r for r in result.recommendations)


class TestPRReviewWorkflowParallel:
    """Tests for parallel execution."""

    @pytest.mark.asyncio
    async def test_run_parallel_both_succeed(self):
        """Test parallel execution when both crews succeed."""
        workflow = PRReviewWorkflow(parallel=True)

        mock_review = {"quality_score": 80.0, "findings": [], "agents_used": []}
        mock_audit = {"risk_score": 15.0, "findings": [], "agents_used": []}

        with (
            patch.object(
                workflow,
                "_run_code_review",
                new_callable=AsyncMock,
                return_value=mock_review,
            ),
            patch.object(
                workflow,
                "_run_security_audit",
                new_callable=AsyncMock,
                return_value=mock_audit,
            ),
        ):
            code_review, security_audit = await workflow._run_parallel(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert code_review == mock_review
        assert security_audit == mock_audit

    @pytest.mark.asyncio
    async def test_run_parallel_one_fails(self):
        """Test parallel execution when one crew fails."""
        workflow = PRReviewWorkflow(parallel=True)

        mock_review = {"quality_score": 80.0, "findings": [], "agents_used": []}

        with (
            patch.object(
                workflow,
                "_run_code_review",
                new_callable=AsyncMock,
                return_value=mock_review,
            ),
            patch.object(
                workflow,
                "_run_security_audit",
                new_callable=AsyncMock,
                side_effect=Exception("Failed"),
            ),
        ):
            code_review, security_audit = await workflow._run_parallel(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert code_review == mock_review
        assert security_audit is None

    @pytest.mark.asyncio
    async def test_run_parallel_both_fail(self):
        """Test parallel execution when both crews fail."""
        workflow = PRReviewWorkflow(parallel=True)

        with (
            patch.object(
                workflow,
                "_run_code_review",
                new_callable=AsyncMock,
                side_effect=Exception("Code failed"),
            ),
            patch.object(
                workflow,
                "_run_security_audit",
                new_callable=AsyncMock,
                side_effect=Exception("Audit failed"),
            ),
        ):
            code_review, security_audit = await workflow._run_parallel(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert code_review is None
        assert security_audit is None


class TestPRReviewWorkflowWarnings:
    """Tests for warning generation."""

    @pytest.mark.asyncio
    async def test_warning_when_code_crew_unavailable(self):
        """Test warning added when code crew unavailable."""
        workflow = PRReviewWorkflow(use_code_crew=True, use_security_crew=False)

        with patch.object(workflow, "_run_code_review", new_callable=AsyncMock, return_value=None):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert any("CodeReviewCrew unavailable" in w for w in result.warnings)

    @pytest.mark.asyncio
    async def test_warning_when_security_crew_unavailable(self):
        """Test warning added when security crew unavailable."""
        workflow = PRReviewWorkflow(use_code_crew=False, use_security_crew=True)

        with patch.object(
            workflow,
            "_run_security_audit",
            new_callable=AsyncMock,
            return_value=None,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert any("SecurityAuditCrew unavailable" in w for w in result.warnings)


class TestPRReviewWorkflowBlockers:
    """Tests for blocker detection."""

    @pytest.mark.asyncio
    async def test_blocker_for_critical_issues(self):
        """Test blocker added for critical issues."""
        workflow = PRReviewWorkflow(use_code_crew=True, use_security_crew=False)

        mock_review = {
            "quality_score": 50.0,
            "findings": [
                {"title": "Critical Bug", "severity": "critical"},
                {"title": "Another Critical", "severity": "critical"},
            ],
            "agents_used": [],
        }

        with patch.object(
            workflow,
            "_run_code_review",
            new_callable=AsyncMock,
            return_value=mock_review,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert result.critical_count == 2
        assert any("2 critical" in b.lower() for b in result.blockers)

    @pytest.mark.asyncio
    async def test_blocker_for_high_severity_threshold(self):
        """Test blocker when high severity count exceeds threshold."""
        workflow = PRReviewWorkflow(use_code_crew=True, use_security_crew=False)

        mock_review = {
            "quality_score": 60.0,
            "findings": [
                {"title": "High 1", "severity": "high"},
                {"title": "High 2", "severity": "high"},
                {"title": "High 3", "severity": "high"},
                {"title": "High 4", "severity": "high"},
            ],
            "agents_used": [],
        }

        with patch.object(
            workflow,
            "_run_code_review",
            new_callable=AsyncMock,
            return_value=mock_review,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert result.high_count == 4
        assert any("high severity" in b.lower() for b in result.blockers)


class TestPRReviewWorkflowRecommendations:
    """Tests for recommendation collection."""

    @pytest.mark.asyncio
    async def test_recommendations_from_code_review(self):
        """Test recommendations collected from code review suggestions."""
        workflow = PRReviewWorkflow(use_code_crew=True, use_security_crew=False)

        mock_review = {
            "quality_score": 75.0,
            "findings": [
                {"title": "Issue 1", "severity": "low", "suggestion": "Add error handling"},
                {"title": "Issue 2", "severity": "info", "suggestion": "Consider caching"},
            ],
            "agents_used": [],
        }

        with patch.object(
            workflow,
            "_run_code_review",
            new_callable=AsyncMock,
            return_value=mock_review,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert "Add error handling" in result.recommendations
        assert "Consider caching" in result.recommendations

    @pytest.mark.asyncio
    async def test_recommendations_from_security_audit(self):
        """Test recommendations collected from security audit remediations."""
        workflow = PRReviewWorkflow(use_code_crew=False, use_security_crew=True)

        mock_audit = {
            "risk_score": 30.0,
            "findings": [
                {"title": "Weak Crypto", "severity": "medium", "remediation": "Use AES-256"},
            ],
            "agents_used": [],
        }

        with patch.object(
            workflow,
            "_run_security_audit",
            new_callable=AsyncMock,
            return_value=mock_audit,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert "Use AES-256" in result.recommendations

    @pytest.mark.asyncio
    async def test_recommendations_limited_to_15(self):
        """Test recommendations are limited to 15."""
        workflow = PRReviewWorkflow(use_code_crew=True, use_security_crew=False)

        mock_review = {
            "quality_score": 50.0,
            "findings": [
                {"title": f"Issue {i}", "severity": "low", "suggestion": f"Suggestion {i}"}
                for i in range(20)
            ],
            "agents_used": [],
        }

        with patch.object(
            workflow,
            "_run_code_review",
            new_callable=AsyncMock,
            return_value=mock_review,
        ):
            result = await workflow.execute(
                diff="test",
                files_changed=[],
                target_path=".",
            )

        assert len(result.recommendations) <= 15
