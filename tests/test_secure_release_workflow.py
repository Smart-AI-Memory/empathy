"""Tests for SecureReleasePipeline.

Tests the comprehensive security pipeline that composes multiple workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_os.workflows.secure_release import (
    SecureReleasePipeline,
    SecureReleaseResult,
    format_secure_release_report,
)


class TestSecureReleaseResult:
    """Tests for SecureReleaseResult dataclass."""

    def test_default_creation(self):
        """Test creating result with defaults."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
        )

        assert result.success is True
        assert result.go_no_go == "GO"
        assert result.crew_report is None
        assert result.combined_risk_score == 0.0
        assert result.total_findings == 0
        assert result.blockers == []
        assert result.warnings == []

    def test_full_creation(self):
        """Test creating result with all fields."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            combined_risk_score=75.5,
            total_findings=10,
            critical_count=2,
            high_count=5,
            total_cost=0.15,
            total_duration_ms=5000,
            blockers=["Critical vuln found"],
            warnings=["High risk area"],
            recommendations=["Fix before release"],
            mode="full",
            crew_enabled=True,
        )

        assert result.success is False
        assert result.go_no_go == "NO_GO"
        assert result.combined_risk_score == 75.5
        assert result.critical_count == 2
        assert len(result.blockers) == 1

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="CONDITIONAL",
            combined_risk_score=50.0,
            total_findings=5,
            critical_count=0,
            high_count=3,
            total_cost=0.10,
            total_duration_ms=3000,
            blockers=[],
            warnings=["Review warning"],
            recommendations=["Document risks"],
            mode="standard",
            crew_enabled=False,
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["go_no_go"] == "CONDITIONAL"
        assert data["combined_risk_score"] == 50.0
        assert data["mode"] == "standard"
        assert data["crew_enabled"] is False

    def test_formatted_report_property(self):
        """Test formatted report property calls format function."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
        )

        report = result.formatted_report

        assert "SECURE RELEASE REPORT" in report
        assert "GO" in report


class TestSecureReleasePipelineInit:
    """Tests for SecureReleasePipeline initialization."""

    def test_default_init(self):
        """Test default initialization."""
        pipeline = SecureReleasePipeline()

        assert pipeline.mode == "full"
        assert pipeline.use_crew is True
        assert pipeline.parallel_crew is True
        assert pipeline.crew_config == {}

    def test_standard_mode(self):
        """Test standard mode initialization."""
        pipeline = SecureReleasePipeline(mode="standard")

        assert pipeline.mode == "standard"
        assert pipeline.use_crew is False  # standard mode disables crew

    def test_standard_mode_duplicate(self):
        """Test standard mode initialization (duplicate check)."""
        # This is a duplicate of test_standard_mode above - keeping for backwards compatibility
        pipeline = SecureReleasePipeline(mode="standard")

        assert pipeline.mode == "standard"
        assert pipeline.use_crew is False

    def test_override_crew_setting(self):
        """Test overriding crew setting."""
        pipeline = SecureReleasePipeline(mode="standard", use_crew=True)

        assert pipeline.use_crew is True

    def test_custom_crew_config(self):
        """Test custom crew configuration."""
        config = {"scan_depth": "thorough", "timeout": 600}
        pipeline = SecureReleasePipeline(crew_config=config)

        assert pipeline.crew_config == config

    def test_parallel_crew_disabled(self):
        """Test disabling parallel crew."""
        pipeline = SecureReleasePipeline(parallel_crew=False)

        assert pipeline.parallel_crew is False


class TestCalculateCombinedRisk:
    """Tests for risk calculation."""

    def test_no_results(self):
        """Test with no results."""
        pipeline = SecureReleasePipeline()

        risk = pipeline._calculate_combined_risk(None, None, None, None)

        assert risk == 0.0

    def test_crew_only(self):
        """Test with crew report only."""
        pipeline = SecureReleasePipeline()
        crew_report = {"risk_score": 60}

        risk = pipeline._calculate_combined_risk(crew_report, None, None, None)

        assert risk == 60.0  # Only crew score with weight 1.5

    def test_security_audit_only(self):
        """Test with security audit only."""
        pipeline = SecureReleasePipeline()
        security_result = MagicMock()
        security_result.final_output = {"assessment": {"risk_score": 40}}

        risk = pipeline._calculate_combined_risk(None, security_result, None, None)

        assert risk == 40.0

    def test_combined_weighted_average(self):
        """Test weighted average calculation."""
        pipeline = SecureReleasePipeline()
        crew_report = {"risk_score": 60}  # weight 1.5
        security_result = MagicMock()
        security_result.final_output = {"assessment": {"risk_score": 40}}  # weight 1.0

        risk = pipeline._calculate_combined_risk(crew_report, security_result, None, None)

        # (60 * 1.5 + 40 * 1.0) / (1.5 + 1.0) = (90 + 40) / 2.5 = 52
        assert abs(risk - 52.0) < 0.1

    def test_code_review_converts_security_score(self):
        """Test code review converts security score to risk."""
        pipeline = SecureReleasePipeline()
        code_review_result = MagicMock()
        code_review_result.final_output = {"security_score": 80}  # 100 - 80 = 20 risk

        risk = pipeline._calculate_combined_risk(None, None, code_review_result, None)

        assert risk == 20.0

    def test_risk_capped_at_100(self):
        """Test risk score is capped at 100."""
        pipeline = SecureReleasePipeline()
        crew_report = {"risk_score": 150}  # Invalid high score

        risk = pipeline._calculate_combined_risk(crew_report, None, None, None)

        assert risk <= 100.0


class TestAggregateFindings:
    """Tests for findings aggregation."""

    def test_no_findings(self):
        """Test with no findings."""
        pipeline = SecureReleasePipeline()

        findings = pipeline._aggregate_findings(None, None, None)

        assert findings["critical"] == 0
        assert findings["high"] == 0
        assert findings["total"] == 0

    def test_crew_findings(self):
        """Test aggregating crew findings."""
        pipeline = SecureReleasePipeline()
        crew_report = {
            "assessment": {
                "critical_findings": [{"title": "SQL Injection"}],
                "high_findings": [{"title": "XSS"}, {"title": "CSRF"}],
            },
            "finding_count": 5,
        }

        findings = pipeline._aggregate_findings(crew_report, None, None)

        assert findings["critical"] == 1
        assert findings["high"] == 2
        assert findings["total"] == 5

    def test_security_audit_findings(self):
        """Test aggregating security audit findings."""
        pipeline = SecureReleasePipeline()
        security_result = MagicMock()
        security_result.final_output = {
            "assessment": {"severity_breakdown": {"critical": 2, "high": 3, "medium": 5}},
        }

        findings = pipeline._aggregate_findings(None, security_result, None)

        assert findings["critical"] == 2
        assert findings["high"] == 3
        assert findings["total"] == 10

    def test_code_review_critical_issues(self):
        """Test code review critical issues flag."""
        pipeline = SecureReleasePipeline()
        code_review_result = MagicMock()
        code_review_result.final_output = {"has_critical_issues": True}

        findings = pipeline._aggregate_findings(None, None, code_review_result)

        assert findings["critical"] >= 1

    def test_takes_max_of_sources(self):
        """Test takes maximum from multiple sources."""
        pipeline = SecureReleasePipeline()
        crew_report = {
            "assessment": {
                "critical_findings": [{"title": "Issue1"}],
                "high_findings": [],
            },
            "finding_count": 3,
        }
        security_result = MagicMock()
        security_result.final_output = {
            "assessment": {"severity_breakdown": {"critical": 3, "high": 5}},
        }

        findings = pipeline._aggregate_findings(crew_report, security_result, None)

        # Should take max(1, 3) = 3 for critical
        assert findings["critical"] == 3
        assert findings["high"] == 5


class TestDetermineGoNoGo:
    """Tests for go/no-go decision logic."""

    def test_go_with_no_issues(self):
        """Test GO decision with no issues."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 0, "high": 0, "total": 0}

        decision = pipeline._determine_go_no_go(20.0, findings, None)

        assert decision == "GO"

    def test_no_go_with_critical(self):
        """Test NO_GO with critical findings."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 1, "high": 0, "total": 1}

        decision = pipeline._determine_go_no_go(20.0, findings, None)

        assert decision == "NO_GO"

    def test_no_go_with_very_high_risk(self):
        """Test NO_GO with very high risk score."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 0, "high": 0, "total": 5}

        decision = pipeline._determine_go_no_go(80.0, findings, None)

        assert decision == "NO_GO"

    def test_conditional_with_many_high_findings(self):
        """Test CONDITIONAL with many high findings."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 0, "high": 5, "total": 10}

        decision = pipeline._determine_go_no_go(30.0, findings, None)

        assert decision == "CONDITIONAL"

    def test_conditional_with_elevated_risk(self):
        """Test CONDITIONAL with elevated risk score."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 0, "high": 1, "total": 5}

        decision = pipeline._determine_go_no_go(55.0, findings, None)

        assert decision == "CONDITIONAL"

    def test_conditional_release_not_approved(self):
        """Test CONDITIONAL when release workflow not approved."""
        pipeline = SecureReleasePipeline()
        findings = {"critical": 0, "high": 0, "total": 2}
        release_result = MagicMock()
        release_result.final_output = {"approved": False}

        decision = pipeline._determine_go_no_go(30.0, findings, release_result)

        assert decision == "CONDITIONAL"


class TestGenerateRecommendations:
    """Tests for recommendation generation."""

    def test_no_issues_recommendations(self):
        """Test recommendations with no issues."""
        pipeline = SecureReleasePipeline()

        blockers, warnings, recs = pipeline._generate_recommendations(None, None, None, None)

        assert len(blockers) == 0
        assert len(warnings) == 0
        assert "All checks passed" in recs[0]

    def test_crew_critical_findings_as_blockers(self):
        """Test crew critical findings become blockers."""
        pipeline = SecureReleasePipeline()
        crew_report = {
            "assessment": {
                "critical_findings": [{"title": "SQL Injection"}],
                "high_findings": [],
            },
        }

        blockers, warnings, recs = pipeline._generate_recommendations(crew_report, None, None, None)

        assert len(blockers) >= 1
        assert "SQL Injection" in blockers[0]

    def test_crew_high_findings_as_warnings(self):
        """Test crew high findings become warnings."""
        pipeline = SecureReleasePipeline()
        crew_report = {
            "assessment": {
                "critical_findings": [],
                "high_findings": [{"title": "XSS Vulnerability"}],
            },
        }

        blockers, warnings, recs = pipeline._generate_recommendations(crew_report, None, None, None)

        assert len(warnings) >= 1
        assert "XSS Vulnerability" in warnings[0]

    def test_security_audit_critical_risk(self):
        """Test security audit critical risk becomes blocker."""
        pipeline = SecureReleasePipeline()
        security_result = MagicMock()
        security_result.final_output = {"assessment": {"risk_level": "critical"}}

        blockers, warnings, recs = pipeline._generate_recommendations(
            None,
            security_result,
            None,
            None,
        )

        assert any("critical risk" in b.lower() for b in blockers)

    def test_code_review_reject_as_blocker(self):
        """Test code review rejection becomes blocker."""
        pipeline = SecureReleasePipeline()
        code_review_result = MagicMock()
        code_review_result.final_output = {"verdict": "reject"}

        blockers, warnings, recs = pipeline._generate_recommendations(
            None,
            None,
            code_review_result,
            None,
        )

        assert any("rejected" in b.lower() for b in blockers)

    def test_code_review_changes_requested_as_warning(self):
        """Test code review changes requested becomes warning."""
        pipeline = SecureReleasePipeline()
        code_review_result = MagicMock()
        code_review_result.final_output = {"verdict": "request_changes"}

        blockers, warnings, recs = pipeline._generate_recommendations(
            None,
            None,
            code_review_result,
            None,
        )

        assert any("changes requested" in w.lower() for w in warnings)

    def test_release_prep_blockers_propagated(self):
        """Test release prep blockers are propagated."""
        pipeline = SecureReleasePipeline()
        release_result = MagicMock()
        release_result.final_output = {
            "blockers": ["Missing changelog"],
            "warnings": ["Version outdated"],
        }

        blockers, warnings, recs = pipeline._generate_recommendations(
            None,
            None,
            None,
            release_result,
        )

        assert any("Missing changelog" in b for b in blockers)
        assert any("Version outdated" in w for w in warnings)


class TestFactoryMethods:
    """Tests for factory methods."""

    def test_for_pr_review_small_pr(self):
        """Test factory for small PR review."""
        pipeline = SecureReleasePipeline.for_pr_review(files_changed=5)

        assert pipeline.mode == "standard"
        assert pipeline.parallel_crew is True

    def test_for_pr_review_large_pr(self):
        """Test factory for large PR review."""
        pipeline = SecureReleasePipeline.for_pr_review(files_changed=20)

        assert pipeline.mode == "full"

    def test_for_release(self):
        """Test factory for release."""
        pipeline = SecureReleasePipeline.for_release()

        assert pipeline.mode == "full"
        assert pipeline.crew_config.get("scan_depth") == "thorough"

    def test_for_standard_check(self):
        """Test factory for standard check."""
        # Note: for_quick_check() was removed - use mode="standard" instead
        pipeline = SecureReleasePipeline(mode="standard")

        assert pipeline.mode == "standard"
        assert pipeline.use_crew is False


class TestFormatSecureReleaseReport:
    """Tests for report formatting function."""

    def test_format_go_report(self):
        """Test formatting GO report."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            combined_risk_score=25.0,
            total_findings=2,
            critical_count=0,
            high_count=0,
            total_cost=0.05,
            total_duration_ms=2000,
            mode="standard",
            crew_enabled=False,
        )

        report = format_secure_release_report(result)

        assert "SECURE RELEASE REPORT" in report
        assert "GO" in report
        assert "READY FOR RELEASE" in report
        assert "25.0/100" in report

    def test_format_conditional_report(self):
        """Test formatting CONDITIONAL report."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="CONDITIONAL",
            combined_risk_score=55.0,
            total_findings=5,
            critical_count=0,
            high_count=3,
            warnings=["Review high findings"],
            mode="full",
            crew_enabled=True,
        )

        report = format_secure_release_report(result)

        assert "CONDITIONAL" in report
        assert "CONDITIONAL APPROVAL" in report
        assert "Review high findings" in report

    def test_format_no_go_report(self):
        """Test formatting NO_GO report."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            combined_risk_score=85.0,
            total_findings=10,
            critical_count=3,
            high_count=5,
            blockers=["Critical vulnerability found"],
            recommendations=["Address all blockers"],
            mode="full",
            crew_enabled=True,
        )

        report = format_secure_release_report(result)

        assert "NO_GO" in report
        assert "RELEASE BLOCKED" in report
        assert "Critical vulnerability found" in report
        assert "BLOCKERS" in report

    def test_format_with_workflow_results(self):
        """Test formatting includes workflow summaries."""
        security_result = MagicMock()
        security_result.final_output = {"assessment": {"risk_score": 40, "risk_level": "medium"}}

        code_review_result = MagicMock()
        code_review_result.final_output = {"verdict": "approve"}

        release_prep_result = MagicMock()
        release_prep_result.final_output = {"approved": True, "confidence": "high"}

        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            security_audit=security_result,
            code_review=code_review_result,
            release_prep=release_prep_result,
            mode="standard",
        )

        report = format_secure_release_report(result)

        assert "WORKFLOW RESULTS" in report
        assert "SecurityAudit" in report
        assert "CodeReview" in report
        assert "ReleasePrep" in report

    def test_format_with_crew_report(self):
        """Test formatting includes crew report."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            crew_report={"risk_score": 30, "finding_count": 2},
            crew_enabled=True,
            mode="full",
        )

        report = format_secure_release_report(result)

        assert "SecurityAuditCrew" in report
        assert "2 findings" in report

    def test_format_includes_cost_and_duration(self):
        """Test formatting includes cost and duration."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            total_cost=0.1234,
            total_duration_ms=5500,
        )

        report = format_secure_release_report(result)

        assert "EXECUTION DETAILS" in report
        assert "$0.1234" in report
        assert "5500ms" in report


class TestPipelineExecution:
    """Tests for pipeline execution."""

    @pytest.mark.asyncio
    async def test_execute_standard_mode(self):
        """Test execute in standard mode."""
        pipeline = SecureReleasePipeline(mode="standard", use_crew=False)

        mock_security_result = MagicMock()
        mock_security_result.cost_report.total_cost = 0.05
        mock_security_result.final_output = {
            "assessment": {"risk_score": 30, "severity_breakdown": {}},
        }

        mock_release_result = MagicMock()
        mock_release_result.cost_report.total_cost = 0.03
        mock_release_result.final_output = {"approved": True}

        # Patch at the module where the classes are imported from
        with (
            patch("src.empathy_os.workflows.security_audit.SecurityAuditWorkflow") as mock_sec_cls,
            patch(
                "src.empathy_os.workflows.release_prep.ReleasePreparationWorkflow",
            ) as mock_rel_cls,
            patch(
                "src.empathy_os.workflows.security_adapters._check_crew_available",
                return_value=False,
            ),
        ):
            mock_sec_cls.return_value.execute = AsyncMock(return_value=mock_security_result)
            mock_rel_cls.return_value.execute = AsyncMock(return_value=mock_release_result)

            result = await pipeline.execute(path=".")

            assert result.success is True
            assert result.go_no_go == "GO"
            assert result.mode == "standard"
            assert result.crew_enabled is False

    @pytest.mark.asyncio
    async def test_execute_handles_failure(self):
        """Test execute handles workflow failure."""
        pipeline = SecureReleasePipeline(mode="standard", use_crew=False)

        # Patch at the module where the class is imported from
        with (
            patch("src.empathy_os.workflows.security_audit.SecurityAuditWorkflow") as mock_cls,
            patch(
                "src.empathy_os.workflows.security_adapters._check_crew_available",
                return_value=False,
            ),
        ):
            mock_cls.return_value.execute = AsyncMock(side_effect=Exception("Workflow failed"))

            result = await pipeline.execute(path=".")

            assert result.success is False
            assert result.go_no_go == "NO_GO"
            assert any("Pipeline failed" in b for b in result.blockers)
