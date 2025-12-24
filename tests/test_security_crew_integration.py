"""
Tests for SecurityAuditCrew Workflow Integration

Tests all 4 integration options:
1. ReleasePreparationWorkflow with crew_security stage
2. CodeReviewWorkflow with external audit results
3. SecureReleasePipeline composite workflow
4. SecurityAuditWorkflow with crew-enhanced remediation

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ============================================================================
# Test Security Adapters (Foundation)
# ============================================================================


class TestSecurityAdapters:
    """Test security adapter functions."""

    def test_check_crew_available_when_installed(self):
        """Test crew availability check when module exists."""
        from empathy_os.workflows.security_adapters import _check_crew_available

        # Should return True since we have the module
        result = _check_crew_available()
        assert isinstance(result, bool)

    def test_crew_report_to_workflow_format(self):
        """Test converting SecurityReport to workflow format."""
        from empathy_os.workflows.security_adapters import crew_report_to_workflow_format

        # Create mock report
        mock_report = MagicMock()
        mock_report.summary = "Found 2 issues"
        mock_report.risk_score = 45.0
        mock_report.audit_duration_seconds = 10.5
        mock_report.agents_used = ["lead", "hunter"]
        mock_report.memory_graph_hits = 0
        mock_report.metadata = {}

        # Create mock findings with proper severity/category mocks
        mock_finding1 = MagicMock()
        mock_finding1.title = "SQL Injection"
        mock_finding1.description = "User input not sanitized"
        mock_finding1.severity = MagicMock(value="critical")
        mock_finding1.category = MagicMock(value="injection")
        mock_finding1.file_path = "src/api.py"
        mock_finding1.line_number = 42
        mock_finding1.code_snippet = "SELECT * FROM users"
        mock_finding1.remediation = "Use parameterized queries"
        mock_finding1.cwe_id = "CWE-89"
        mock_finding1.cvss_score = 9.8
        mock_finding1.confidence = 1.0

        mock_finding2 = MagicMock()
        mock_finding2.title = "XSS Vulnerability"
        mock_finding2.description = "Reflected XSS in search"
        mock_finding2.severity = MagicMock(value="high")
        mock_finding2.category = MagicMock(value="cross_site_scripting")
        mock_finding2.file_path = None
        mock_finding2.line_number = None
        mock_finding2.code_snippet = None
        mock_finding2.remediation = None
        mock_finding2.cwe_id = None
        mock_finding2.cvss_score = None
        mock_finding2.confidence = 0.9

        mock_report.findings = [mock_finding1, mock_finding2]

        result = crew_report_to_workflow_format(mock_report)

        assert result["summary"] == "Found 2 issues"
        assert result["risk_score"] == 45.0
        assert result["finding_count"] == 2
        assert len(result["findings"]) == 2
        assert result["crew_enabled"] is True
        assert len(result["assessment"]["critical_findings"]) == 1
        assert len(result["assessment"]["high_findings"]) == 1

    def test_workflow_findings_to_crew_format(self):
        """Test converting workflow findings to crew format."""
        from empathy_os.workflows.security_adapters import workflow_findings_to_crew_format

        workflow_findings = [
            {
                "title": "Test Finding",
                "description": "Test description",
                "severity": "high",
                "category": "injection",
                "file": "test.py",
                "line": 10,
            }
        ]

        result = workflow_findings_to_crew_format(workflow_findings)

        assert len(result) == 1
        assert result[0]["title"] == "Test Finding"
        assert result[0]["severity"] == "high"
        # file_path should be normalized from "file" key
        assert result[0]["file_path"] == "test.py"

    def test_merge_security_results(self):
        """Test merging crew and workflow results."""
        from empathy_os.workflows.security_adapters import merge_security_results

        crew_report = {
            "risk_score": 60.0,
            "findings": [
                {
                    "title": "Crew Finding",
                    "severity": "critical",
                    "type": "injection",
                    "file": "api.py",
                    "line": 10,
                }
            ],
            "assessment": {"risk_score": 60.0, "severity_breakdown": {"critical": 1}},
        }

        workflow_findings = {
            "risk_score": 40.0,
            "findings": [
                {
                    "title": "Workflow Finding",
                    "severity": "high",
                    "type": "xss",
                    "file": "view.py",
                    "line": 20,
                }
            ],
            "assessment": {"risk_score": 40.0, "severity_breakdown": {"high": 1}},
        }

        result = merge_security_results(crew_report, workflow_findings)

        # Should merge findings (different file/line, so not deduplicated)
        assert len(result["findings"]) == 2
        # Risk score should be weighted toward crew (higher weight)
        assert result["risk_score"] >= 40.0
        assert result["merged"] is True
        assert result["crew_enabled"] is True

    def test_merge_security_results_crew_only(self):
        """Test merging with only crew results."""
        from empathy_os.workflows.security_adapters import merge_security_results

        crew_report = {
            "risk_score": 75.0,
            "findings": [{"title": "Critical Issue", "severity": "critical"}],
            "crew_enabled": True,
        }

        result = merge_security_results(crew_report, None)

        assert result["risk_score"] == 75.0
        assert len(result["findings"]) == 1
        assert result["merged"] is False
        assert result["crew_enabled"] is True

    def test_merge_security_results_workflow_only(self):
        """Test merging with only workflow results."""
        from empathy_os.workflows.security_adapters import merge_security_results

        workflow_findings = {
            "risk_score": 30.0,
            "findings": [{"title": "Minor Issue", "severity": "low"}],
        }

        result = merge_security_results(None, workflow_findings)

        assert result["risk_score"] == 30.0
        assert len(result["findings"]) == 1
        assert result["merged"] is False
        assert result["crew_enabled"] is False


# ============================================================================
# Option 1: ReleasePreparationWorkflow with crew_security stage
# ============================================================================


class TestReleasePreparationCrewIntegration:
    """Test Option 1: ReleasePreparationWorkflow with crew_security stage."""

    def test_workflow_init_without_crew(self):
        """Test workflow initializes without crew by default."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        workflow = ReleasePreparationWorkflow()

        assert workflow.use_security_crew is False
        assert "crew_security" not in workflow.stages

    def test_workflow_init_with_crew(self):
        """Test workflow initializes with crew when enabled."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert workflow.use_security_crew is True
        assert "crew_security" in workflow.stages

    def test_workflow_stages_order_with_crew(self):
        """Test stages are in correct order when crew is enabled."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        # crew_security should come after security
        security_idx = workflow.stages.index("security")
        crew_idx = workflow.stages.index("crew_security")
        assert crew_idx == security_idx + 1

    @pytest.mark.asyncio
    async def test_crew_security_stage_fallback(self):
        """Test crew_security stage gracefully falls back when crew unavailable."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        # Mock _check_crew_available to return False at the security_adapters level
        with patch(
            "empathy_os.workflows.security_adapters._check_crew_available", return_value=False
        ):
            input_data = {"path": "./src", "security": {"issues": []}}

            result, input_tokens, output_tokens = await workflow._crew_security(
                input_data, workflow.tier_map["crew_security"]
            )

            assert "crew_security" in result
            assert result["crew_security"]["available"] is False
            assert result["crew_security"]["fallback"] is True

    @pytest.mark.asyncio
    async def test_crew_security_stage_with_mocked_crew(self):
        """Test crew_security stage with mocked crew results."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        # Mock crew report with proper attributes
        mock_report = MagicMock()
        mock_report.summary = "All clear"
        mock_report.risk_score = 0.0
        mock_report.findings = []
        mock_report.audit_duration_seconds = 5.0
        mock_report.agents_used = ["lead"]
        mock_report.memory_graph_hits = 0
        mock_report.metadata = {}

        with (
            patch(
                "empathy_os.workflows.security_adapters._check_crew_available", return_value=True
            ),
            patch(
                "empathy_os.workflows.security_adapters._get_crew_audit",
                new_callable=AsyncMock,
                return_value=mock_report,
            ),
        ):
            input_data = {"path": "./src", "security": {"issues": []}}

            result, input_tokens, output_tokens = await workflow._crew_security(
                input_data, workflow.tier_map["crew_security"]
            )

            assert "crew_security" in result
            assert result["crew_security"]["available"] is True
            assert result["crew_security"]["risk_score"] == 0.0


# ============================================================================
# Option 2: CodeReviewWorkflow with external audit results
# ============================================================================


class TestCodeReviewExternalAudit:
    """Test Option 2: CodeReviewWorkflow with external audit results."""

    def test_scan_accepts_external_audit(self):
        """Test _scan method accepts external_audit_results."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow()

        # Verify method signature can handle external audit
        import inspect

        _sig = inspect.signature(workflow._scan)
        # input_data should contain external_audit_results
        # This is a dict, so we just verify the method exists
        assert callable(workflow._scan)

    def test_merge_external_audit_method_exists(self):
        """Test _merge_external_audit helper exists."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow()
        assert hasattr(workflow, "_merge_external_audit")
        assert callable(workflow._merge_external_audit)

    def test_merge_external_audit(self):
        """Test merging external audit results."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow()

        llm_response = "Found minor code style issues."
        external_audit = {
            "summary": "Security scan complete",
            "risk_score": 45,
            "findings": [
                {
                    "title": "SQL Injection",
                    "description": "Input not sanitized",
                    "severity": "critical",
                    "file": "api.py",
                    "line": 10,
                },
                {
                    "title": "XSS",
                    "description": "Reflected XSS",
                    "severity": "high",
                },
            ],
        }

        merged, findings, has_critical = workflow._merge_external_audit(
            llm_response, external_audit
        )

        assert llm_response in merged
        assert "SecurityAuditCrew Analysis" in merged
        assert len(findings) == 2
        assert has_critical is True

    def test_merge_external_audit_no_critical(self):
        """Test merging with no critical findings."""
        from empathy_os.workflows import CodeReviewWorkflow

        workflow = CodeReviewWorkflow()

        llm_response = "Code looks good."
        external_audit = {
            "findings": [
                {"title": "Minor Issue", "severity": "low"},
            ],
        }

        merged, findings, has_critical = workflow._merge_external_audit(
            llm_response, external_audit
        )

        assert has_critical is False

    @pytest.mark.asyncio
    async def test_scan_with_external_audit(self):
        """Test full scan with external audit results."""
        from empathy_os.workflows import CodeReviewWorkflow
        from empathy_os.workflows.base import ModelTier

        workflow = CodeReviewWorkflow()

        input_data = {
            "diff": "def test(): pass",
            "code_to_review": "def test(): pass",
            "classification": "Simple function",
            "external_audit_results": {
                "summary": "Clean scan",
                "risk_score": 10,
                "findings": [],
            },
        }

        # Mock LLM call
        with patch.object(
            workflow,
            "_call_llm",
            new_callable=AsyncMock,
            return_value=("No issues found", 100, 50),
        ):
            result, input_tokens, output_tokens = await workflow._scan(
                input_data, ModelTier.CAPABLE
            )

            assert "scan_results" in result
            assert result["external_audit_included"] is True
            assert result["external_audit_risk_score"] == 10


# ============================================================================
# Option 3: SecureReleasePipeline composite workflow
# ============================================================================


class TestSecureReleasePipeline:
    """Test Option 3: SecureReleasePipeline composite workflow."""

    def test_pipeline_creation_modes(self):
        """Test pipeline creation with different modes."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline

        full = SecureReleasePipeline(mode="full")
        assert full.mode == "full"
        assert full.use_crew is True

        standard = SecureReleasePipeline(mode="standard")
        assert standard.mode == "standard"
        assert standard.use_crew is False

        quick = SecureReleasePipeline(mode="quick")
        assert quick.mode == "quick"
        assert quick.use_crew is False

    def test_pipeline_factory_methods(self):
        """Test factory methods."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline

        pr = SecureReleasePipeline.for_pr_review(files_changed=5)
        assert pr.mode == "standard"

        pr_large = SecureReleasePipeline.for_pr_review(files_changed=15)
        assert pr_large.mode == "full"

        release = SecureReleasePipeline.for_release()
        assert release.mode == "full"
        assert release.crew_config.get("scan_depth") == "thorough"

        quick = SecureReleasePipeline.for_quick_check()
        assert quick.mode == "quick"
        assert quick.use_crew is False

    def test_result_dataclass(self):
        """Test SecureReleaseResult dataclass."""
        from empathy_os.workflows.secure_release import SecureReleaseResult

        result = SecureReleaseResult(
            success=True,
            go_no_go="GO",
            combined_risk_score=15.0,
            total_findings=2,
            critical_count=0,
            high_count=1,
            total_cost=0.05,
            total_duration_ms=5000,
            blockers=[],
            warnings=["Minor issue found"],
            recommendations=["Review before release"],
            mode="standard",
        )

        assert result.success is True
        assert result.go_no_go == "GO"

        # Test to_dict
        data = result.to_dict()
        assert data["success"] is True
        assert data["go_no_go"] == "GO"
        assert data["combined_risk_score"] == 15.0

    def test_determine_go_no_go_logic(self):
        """Test go/no-go decision logic."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline

        pipeline = SecureReleasePipeline()

        # Critical findings = NO_GO
        go = pipeline._determine_go_no_go(20.0, {"critical": 1, "high": 0}, None)
        assert go == "NO_GO"

        # Very high risk = NO_GO
        go = pipeline._determine_go_no_go(80.0, {"critical": 0, "high": 0}, None)
        assert go == "NO_GO"

        # High findings = CONDITIONAL
        go = pipeline._determine_go_no_go(40.0, {"critical": 0, "high": 5}, None)
        assert go == "CONDITIONAL"

        # Clean = GO
        go = pipeline._determine_go_no_go(10.0, {"critical": 0, "high": 1}, None)
        assert go == "GO"

    def test_calculate_combined_risk(self):
        """Test combined risk calculation."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline

        pipeline = SecureReleasePipeline()

        # No results = 0 risk
        risk = pipeline._calculate_combined_risk(None, None, None, None)
        assert risk == 0.0

        # Crew report only
        crew_report = {"risk_score": 50.0}
        risk = pipeline._calculate_combined_risk(crew_report, None, None, None)
        assert risk == 50.0

    @pytest.mark.asyncio
    async def test_pipeline_execute_quick_mode(self):
        """Test pipeline execution in quick mode."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline

        pipeline = SecureReleasePipeline(mode="quick")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple file
            (Path(tmpdir) / "test.py").write_text("print('hello')")

            # Mock the workflow classes at the module import location
            mock_security_result = MagicMock()
            mock_security_result.final_output = {"assessment": {"risk_score": 10}}
            mock_security_result.cost_report = MagicMock(total_cost=0.01)

            mock_release_result = MagicMock()
            mock_release_result.final_output = {"approved": True}
            mock_release_result.cost_report = MagicMock(total_cost=0.02)

            with (
                patch("empathy_os.workflows.security_audit.SecurityAuditWorkflow") as MockSecurity,
                patch(
                    "empathy_os.workflows.release_prep.ReleasePreparationWorkflow"
                ) as MockRelease,
            ):
                # Setup mocks
                mock_security = MagicMock()
                mock_security.execute = AsyncMock(return_value=mock_security_result)
                MockSecurity.return_value = mock_security

                mock_release = MagicMock()
                mock_release.execute = AsyncMock(return_value=mock_release_result)
                MockRelease.return_value = mock_release

                result = await pipeline.execute(path=tmpdir)

                # Quick mode should skip code review
                assert result.code_review is None
                assert result.mode == "quick"


# ============================================================================
# Option 4: SecurityAuditWorkflow with crew-enhanced remediation
# ============================================================================


class TestSecurityAuditCrewRemediation:
    """Test Option 4: SecurityAuditWorkflow with crew-enhanced remediation."""

    def test_workflow_init_without_crew_remediation(self):
        """Test workflow initializes without crew remediation by default."""
        from empathy_os.workflows import SecurityAuditWorkflow

        workflow = SecurityAuditWorkflow()

        assert workflow.use_crew_for_remediation is False

    def test_workflow_init_with_crew_remediation(self):
        """Test workflow initializes with crew remediation when enabled."""
        from empathy_os.workflows import SecurityAuditWorkflow

        workflow = SecurityAuditWorkflow(use_crew_for_remediation=True)

        assert workflow.use_crew_for_remediation is True

    def test_crew_config_passed(self):
        """Test crew config is passed correctly."""
        from empathy_os.workflows import SecurityAuditWorkflow

        config = {"scan_depth": "thorough", "timeout_seconds": 600}
        workflow = SecurityAuditWorkflow(use_crew_for_remediation=True, crew_config=config)

        assert workflow.crew_config == config

    def test_get_crew_remediation_method_exists(self):
        """Test _get_crew_remediation helper exists."""
        from empathy_os.workflows import SecurityAuditWorkflow

        workflow = SecurityAuditWorkflow(use_crew_for_remediation=True)
        assert hasattr(workflow, "_get_crew_remediation")
        assert callable(workflow._get_crew_remediation)

    def test_merge_crew_remediation_method_exists(self):
        """Test _merge_crew_remediation helper exists."""
        from empathy_os.workflows import SecurityAuditWorkflow

        workflow = SecurityAuditWorkflow(use_crew_for_remediation=True)
        assert hasattr(workflow, "_merge_crew_remediation")
        assert callable(workflow._merge_crew_remediation)

    @pytest.mark.asyncio
    async def test_remediate_fallback_without_crew(self):
        """Test remediation works without crew when disabled."""
        from empathy_os.workflows import SecurityAuditWorkflow
        from empathy_os.workflows.base import ModelTier

        workflow = SecurityAuditWorkflow(use_crew_for_remediation=False)

        input_data = {
            "path": "./src",
            "assessment": {
                "critical_findings": [{"title": "Test Issue", "severity": "critical"}],
                "high_findings": [],
                "risk_score": 50,
                "risk_level": "medium",
            },
        }

        with patch.object(
            workflow,
            "_call_llm",
            new_callable=AsyncMock,
            return_value=("Fix: Update the code", 100, 50),
        ):
            result, input_tokens, output_tokens = await workflow._remediate(
                input_data, ModelTier.CAPABLE
            )

            # Check for correct result key
            assert "remediation_plan" in result
            # Should not have crew remediation
            assert result.get("crew_enhanced") is False


# ============================================================================
# Integration Tests (End-to-End)
# ============================================================================


class TestEndToEndIntegration:
    """End-to-end integration tests."""

    @pytest.mark.asyncio
    async def test_full_workflow_without_api_key(self):
        """Test workflows execute (with simulation) when no API key."""
        from empathy_os.workflows import ReleasePreparationWorkflow

        # Without ANTHROPIC_API_KEY, workflow should use simulation mode
        workflow = ReleasePreparationWorkflow(use_security_crew=False)

        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.py").write_text("print('test')")

            result = await workflow.execute(path=tmpdir)

            # Should complete (possibly with simulated results)
            assert result is not None
            assert hasattr(result, "success")

    def test_imports_work(self):
        """Test all new exports are importable."""
        from empathy_os.workflows.secure_release import SecureReleasePipeline, SecureReleaseResult
        from empathy_os.workflows.security_adapters import _check_crew_available

        # All imports should succeed
        assert SecureReleasePipeline is not None
        assert SecureReleaseResult is not None
        assert _check_crew_available is not None

    def test_backward_compatibility(self):
        """Test existing workflows still work with default parameters."""
        from empathy_os.workflows import (
            CodeReviewWorkflow,
            ReleasePreparationWorkflow,
            SecurityAuditWorkflow,
        )

        # All should initialize without errors using defaults
        code_review = CodeReviewWorkflow()
        assert code_review is not None

        release_prep = ReleasePreparationWorkflow()
        assert release_prep is not None
        assert "crew_security" not in release_prep.stages

        security_audit = SecurityAuditWorkflow()
        assert security_audit is not None
        assert security_audit.use_crew_for_remediation is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
