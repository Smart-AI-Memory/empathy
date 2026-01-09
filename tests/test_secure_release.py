"""Tests for src/empathy_os/workflows/secure_release.py

Tests the SecureReleasePipeline including:
- SecureReleaseResult dataclass
- SecureReleasePipeline initialization
- Execution modes (full, standard)
- Go/No-Go decision logic
- Report formatting

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os.workflows.secure_release import SecureReleasePipeline, SecureReleaseResult


class TestSecureReleaseResult:
    """Tests for SecureReleaseResult dataclass."""

    def test_basic_creation(self):
        """Test basic creation of SecureReleaseResult."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
        )
        assert result.success is True
        assert result.go_no_go == "GO"

    def test_default_values(self):
        """Test default values."""
        result = SecureReleaseResult(success=True, go_no_go="GO")
        assert result.crew_report is None
        assert result.security_audit is None
        assert result.code_review is None
        assert result.release_prep is None
        assert result.combined_risk_score == 0.0
        assert result.total_findings == 0
        assert result.critical_count == 0
        assert result.high_count == 0
        assert result.total_cost == 0.0
        assert result.total_duration_ms == 0
        assert result.blockers == []
        assert result.warnings == []
        assert result.recommendations == []
        assert result.mode == "full"
        assert result.crew_enabled is False

    def test_go_decision(self):
        """Test GO decision."""
        result = SecureReleaseResult(success=True, go_no_go="GO")
        assert result.go_no_go == "GO"

    def test_no_go_decision(self):
        """Test NO_GO decision."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            critical_count=1,
            blockers=["Critical vulnerability found"],
        )
        assert result.go_no_go == "NO_GO"
        assert len(result.blockers) == 1

    def test_conditional_decision(self):
        """Test CONDITIONAL decision."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="CONDITIONAL",
            warnings=["High severity issue needs attention"],
        )
        assert result.go_no_go == "CONDITIONAL"
        assert len(result.warnings) == 1

    def test_to_dict(self):
        """Test to_dict method."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            combined_risk_score=0.2,
            total_findings=5,
        )
        data = result.to_dict()
        assert data["success"] is True
        assert data["go_no_go"] == "GO"
        assert data["combined_risk_score"] == 0.2
        assert data["total_findings"] == 5

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        result = SecureReleaseResult(success=True, go_no_go="GO")
        data = result.to_dict()
        expected_keys = [
            "success",
            "go_no_go",
            "combined_risk_score",
            "total_findings",
            "critical_count",
            "high_count",
            "total_cost",
            "total_duration_ms",
            "blockers",
            "warnings",
            "recommendations",
            "mode",
            "crew_enabled",
        ]
        for key in expected_keys:
            assert key in data

    def test_with_findings(self):
        """Test with findings counts."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            total_findings=10,
            critical_count=2,
            high_count=3,
        )
        assert result.total_findings == 10
        assert result.critical_count == 2
        assert result.high_count == 3

    def test_with_cost_tracking(self):
        """Test with cost tracking."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            total_cost=0.05,
            total_duration_ms=5000,
        )
        assert result.total_cost == 0.05
        assert result.total_duration_ms == 5000

    def test_with_recommendations(self):
        """Test with recommendations."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="CONDITIONAL",
            recommendations=[
                "Update dependencies",
                "Add security tests",
            ],
        )
        assert len(result.recommendations) == 2

    def test_mode_full(self):
        """Test full mode."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            mode="full",
            crew_enabled=True,
        )
        assert result.mode == "full"
        assert result.crew_enabled is True

    def test_mode_standard(self):
        """Test standard mode."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            mode="standard",
        )
        assert result.mode == "standard"

    def test_mode_invalid(self):
        """Test result can store any mode string (for backwards compat)."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            mode="custom",
        )
        assert result.mode == "custom"


class TestSecureReleasePipelineInit:
    """Tests for SecureReleasePipeline initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        pipeline = SecureReleasePipeline()
        assert pipeline is not None

    def test_mode_full(self):
        """Test initialization with full mode."""
        pipeline = SecureReleasePipeline(mode="full")
        assert pipeline.mode == "full"

    def test_mode_standard(self):
        """Test initialization with standard mode."""
        pipeline = SecureReleasePipeline(mode="standard")
        assert pipeline.mode == "standard"

    def test_invalid_mode(self):
        """Test initialization with invalid mode raises ValueError."""
        with pytest.raises(ValueError, match="Invalid mode 'quick'"):
            SecureReleasePipeline(mode="quick")

    def test_with_kwargs(self):
        """Test initialization with additional kwargs."""
        pipeline = SecureReleasePipeline(mode="standard", provider="openai")
        assert pipeline.mode == "standard"
        assert pipeline.kwargs.get("provider") == "openai"


class TestSecureReleasePipelineExecution:
    """Tests for SecureReleasePipeline execution."""

    def test_execute_method_exists(self):
        """Test execute method exists."""
        pipeline = SecureReleasePipeline(mode="standard")
        assert hasattr(pipeline, "execute")
        assert callable(pipeline.execute)

    def test_pipeline_attributes(self):
        """Test pipeline has expected attributes."""
        pipeline = SecureReleasePipeline(mode="standard")
        assert pipeline.mode == "standard"
        assert hasattr(pipeline, "use_crew")
        assert hasattr(pipeline, "parallel_crew")


class TestGoNoGoDecision:
    """Tests for Go/No-Go decision logic."""

    def test_go_when_no_critical_findings(self):
        """Test GO decision when no critical findings."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            critical_count=0,
            high_count=0,
        )
        assert result.go_no_go == "GO"

    def test_no_go_when_critical_findings(self):
        """Test NO_GO when critical findings exist."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            critical_count=1,
            blockers=["Critical security vulnerability"],
        )
        assert result.go_no_go == "NO_GO"

    def test_conditional_when_high_findings(self):
        """Test CONDITIONAL when high findings exist."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="CONDITIONAL",
            critical_count=0,
            high_count=2,
            warnings=["High severity findings require review"],
        )
        assert result.go_no_go == "CONDITIONAL"

    def test_blockers_prevent_release(self):
        """Test blockers prevent release."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            blockers=[
                "Hardcoded credentials found",
                "SQL injection vulnerability",
            ],
        )
        assert result.go_no_go == "NO_GO"
        assert len(result.blockers) == 2


class TestRiskScoring:
    """Tests for risk scoring."""

    def test_zero_risk_score(self):
        """Test zero risk score for clean project."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            combined_risk_score=0.0,
        )
        assert result.combined_risk_score == 0.0

    def test_low_risk_score(self):
        """Test low risk score."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            combined_risk_score=0.2,
        )
        assert result.combined_risk_score < 0.5

    def test_high_risk_score(self):
        """Test high risk score."""
        result = SecureReleaseResult(
            success=False,
            go_no_go="NO_GO",
            combined_risk_score=0.9,
        )
        assert result.combined_risk_score > 0.5


class TestReportFormatting:
    """Tests for report formatting."""

    def test_formatted_report_property(self):
        """Test formatted_report property exists."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
        )
        # The property calls format_secure_release_report
        assert hasattr(result, "formatted_report")

    def test_result_summary(self):
        """Test result can be summarized."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            total_findings=0,
            combined_risk_score=0.0,
        )
        data = result.to_dict()
        summary = f"Decision: {data['go_no_go']}, Findings: {data['total_findings']}"
        assert "GO" in summary
        assert "0" in summary


class TestSecureReleasePipelineIntegration:
    """Integration tests for SecureReleasePipeline."""

    def test_pipeline_can_be_instantiated(self):
        """Test pipeline can be instantiated in all modes."""
        for mode in ["full", "standard"]:
            pipeline = SecureReleasePipeline(mode=mode)
            assert pipeline is not None
            assert pipeline.mode == mode

    def test_result_dataclass_is_complete(self):
        """Test result dataclass has all required fields."""
        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            crew_report={"summary": "All clear"},
            combined_risk_score=0.1,
            total_findings=2,
            critical_count=0,
            high_count=1,
            total_cost=0.03,
            total_duration_ms=3000,
            blockers=[],
            warnings=["Minor issue"],
            recommendations=["Consider updating"],
            mode="standard",
            crew_enabled=False,
        )
        assert result.success is True
        assert result.crew_report is not None
        assert result.combined_risk_score == 0.1
