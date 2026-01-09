"""Tests for src/empathy_os/workflows/release_prep.py

Comprehensive tests for the release preparation workflow including:
- RELEASE_PREP_STEPS configuration
- ReleasePreparationWorkflow class attributes
- Initialization and configuration
- Conditional approval skipping
- Security crew integration
- Stage skipping logic
- Stage routing and tier mapping
- Integration tests

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from empathy_os.workflows.base import ModelTier
from empathy_os.workflows.release_prep import (
    RELEASE_PREP_STEPS,
    ReleasePreparationWorkflow,
    format_release_prep_report,
)
from empathy_os.workflows.step_config import WorkflowStepConfig

# =============================================================================
# TestReleaseStepsConfig - RELEASE_PREP_STEPS configuration
# =============================================================================


class TestReleaseStepsConfig:
    """Tests for RELEASE_PREP_STEPS configuration."""

    def test_steps_dict_exists(self):
        """Test that RELEASE_PREP_STEPS is defined."""
        assert RELEASE_PREP_STEPS is not None
        assert isinstance(RELEASE_PREP_STEPS, dict)

    def test_approve_step_exists(self):
        """Test that approve step is defined."""
        assert "approve" in RELEASE_PREP_STEPS

    def test_approve_step_is_workflow_step_config(self):
        """Test that approve step is a WorkflowStepConfig."""
        step = RELEASE_PREP_STEPS["approve"]
        assert isinstance(step, WorkflowStepConfig)

    def test_approve_step_name(self):
        """Test approve step name."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.name == "approve"

    def test_approve_step_task_type(self):
        """Test approve step task type."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.task_type == "final_review"

    def test_approve_step_tier_hint(self):
        """Test approve step tier hint is premium."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.tier_hint == "premium"

    def test_approve_step_description(self):
        """Test approve step has a description."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.description is not None
        assert len(step.description) > 0
        assert "release" in step.description.lower() or "go/no-go" in step.description.lower()

    def test_approve_step_max_tokens(self):
        """Test approve step has max_tokens defined."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.max_tokens == 2000

    def test_approve_step_effective_tier(self):
        """Test approve step effective tier computation."""
        step = RELEASE_PREP_STEPS["approve"]
        assert step.effective_tier == "premium"


# =============================================================================
# TestWorkflowClassAttributes - name, description, stages, tier_map
# =============================================================================


class TestWorkflowClassAttributes:
    """Tests for ReleasePreparationWorkflow class attributes."""

    def test_workflow_name(self):
        """Test workflow name attribute."""
        assert ReleasePreparationWorkflow.name == "release-prep"

    def test_workflow_description(self):
        """Test workflow description attribute."""
        assert ReleasePreparationWorkflow.description is not None
        assert "release" in ReleasePreparationWorkflow.description.lower()

    def test_class_stages_default(self):
        """Test class-level stages list."""
        assert ReleasePreparationWorkflow.stages == ["health", "security", "changelog", "approve"]

    def test_class_tier_map_default(self):
        """Test class-level tier_map."""
        tier_map = ReleasePreparationWorkflow.tier_map
        assert tier_map["health"] == ModelTier.CHEAP
        assert tier_map["security"] == ModelTier.CAPABLE
        assert tier_map["changelog"] == ModelTier.CAPABLE
        assert tier_map["approve"] == ModelTier.PREMIUM

    def test_workflow_has_four_stages_by_default(self):
        """Test default stage count."""
        assert len(ReleasePreparationWorkflow.stages) == 4

    def test_all_stages_have_tier_mapping(self):
        """Test all stages have tier mappings."""
        for stage in ReleasePreparationWorkflow.stages:
            assert stage in ReleasePreparationWorkflow.tier_map


# =============================================================================
# TestWorkflowInit - default and custom initialization
# =============================================================================


class TestWorkflowInit:
    """Tests for ReleasePreparationWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.name == "release-prep"
        assert workflow.skip_approve_if_clean is True
        assert workflow.use_security_crew is False
        assert workflow.crew_config == {}
        assert workflow._has_blockers is False

    def test_init_with_skip_approve_false(self):
        """Test initialization with skip_approve_if_clean=False."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=False)

        assert workflow.skip_approve_if_clean is False

    def test_init_with_security_crew_true(self):
        """Test initialization with use_security_crew=True."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert workflow.use_security_crew is True

    def test_init_with_crew_config(self):
        """Test initialization with crew_config."""
        config = {"verbose": True, "timeout": 60}
        workflow = ReleasePreparationWorkflow(crew_config=config)

        assert workflow.crew_config == config

    def test_init_with_null_crew_config(self):
        """Test initialization with None crew_config defaults to empty dict."""
        workflow = ReleasePreparationWorkflow(crew_config=None)

        assert workflow.crew_config == {}

    def test_init_preserves_has_blockers_false(self):
        """Test _has_blockers starts as False."""
        workflow = ReleasePreparationWorkflow()

        assert workflow._has_blockers is False

    def test_init_inherits_base_workflow(self):
        """Test workflow inherits from BaseWorkflow."""
        workflow = ReleasePreparationWorkflow()

        assert hasattr(workflow, "cost_tracker")
        assert hasattr(workflow, "provider")
        assert hasattr(workflow, "_config")


# =============================================================================
# TestSkipApproveIfClean - conditional approval skipping
# =============================================================================


class TestSkipApproveIfClean:
    """Tests for skip_approve_if_clean functionality."""

    def test_skip_approve_default_true(self):
        """Test skip_approve_if_clean defaults to True."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.skip_approve_if_clean is True

    def test_skip_approve_explicit_true(self):
        """Test skip_approve_if_clean can be set True."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=True)

        assert workflow.skip_approve_if_clean is True

    def test_skip_approve_explicit_false(self):
        """Test skip_approve_if_clean can be set False."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=False)

        assert workflow.skip_approve_if_clean is False

    def test_should_skip_approve_when_clean_and_enabled(self):
        """Test approve is skipped when clean and setting enabled."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=True)
        workflow._has_blockers = False

        skip, reason = workflow.should_skip_stage("approve", {})

        assert skip is True
        assert "auto-approved" in reason.lower()

    def test_should_not_skip_approve_when_blockers_exist(self):
        """Test approve is not skipped when blockers exist."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=True)
        workflow._has_blockers = True

        skip, reason = workflow.should_skip_stage("approve", {})

        assert skip is False
        assert reason is None

    def test_should_not_skip_approve_when_setting_disabled(self):
        """Test approve is not skipped when setting disabled."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=False)
        workflow._has_blockers = False

        skip, reason = workflow.should_skip_stage("approve", {})

        assert skip is False
        assert reason is None


# =============================================================================
# TestUseSecurityCrew - dynamic stage configuration
# =============================================================================


class TestUseSecurityCrew:
    """Tests for use_security_crew dynamic stage configuration."""

    def test_default_stages_without_crew(self):
        """Test default stages without security crew."""
        workflow = ReleasePreparationWorkflow(use_security_crew=False)

        assert workflow.stages == ["health", "security", "changelog", "approve"]
        assert len(workflow.stages) == 4

    def test_stages_with_crew_includes_crew_security(self):
        """Test stages include crew_security when enabled."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert "crew_security" in workflow.stages
        assert workflow.stages == ["health", "security", "crew_security", "changelog", "approve"]
        assert len(workflow.stages) == 5

    def test_tier_map_without_crew(self):
        """Test tier map without security crew."""
        workflow = ReleasePreparationWorkflow(use_security_crew=False)

        assert "crew_security" not in workflow.tier_map
        assert len(workflow.tier_map) == 4

    def test_tier_map_with_crew_has_premium_crew_security(self):
        """Test tier map includes crew_security at PREMIUM tier."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert "crew_security" in workflow.tier_map
        assert workflow.tier_map["crew_security"] == ModelTier.PREMIUM

    def test_tier_map_with_crew_preserves_other_tiers(self):
        """Test tier map preserves other stage tiers when crew enabled."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert workflow.tier_map["health"] == ModelTier.CHEAP
        assert workflow.tier_map["security"] == ModelTier.CAPABLE
        assert workflow.tier_map["changelog"] == ModelTier.CAPABLE
        assert workflow.tier_map["approve"] == ModelTier.PREMIUM


# =============================================================================
# TestCrewConfig - configuration dict
# =============================================================================


class TestCrewConfig:
    """Tests for crew_config configuration."""

    def test_crew_config_default_empty(self):
        """Test crew_config defaults to empty dict."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.crew_config == {}
        assert isinstance(workflow.crew_config, dict)

    def test_crew_config_accepts_dict(self):
        """Test crew_config accepts a dictionary."""
        config = {"verbose": True}
        workflow = ReleasePreparationWorkflow(crew_config=config)

        assert workflow.crew_config == config

    def test_crew_config_with_multiple_keys(self):
        """Test crew_config with multiple configuration keys."""
        config = {
            "verbose": True,
            "timeout": 120,
            "max_retries": 3,
        }
        workflow = ReleasePreparationWorkflow(crew_config=config)

        assert workflow.crew_config["verbose"] is True
        assert workflow.crew_config["timeout"] == 120
        assert workflow.crew_config["max_retries"] == 3

    def test_crew_config_none_becomes_empty_dict(self):
        """Test None crew_config becomes empty dict."""
        workflow = ReleasePreparationWorkflow(crew_config=None)

        assert workflow.crew_config == {}

    def test_crew_config_is_stored_by_reference(self):
        """Test crew_config dict is stored directly."""
        config = {"key": "value"}
        workflow = ReleasePreparationWorkflow(crew_config=config)

        assert workflow.crew_config is config


# =============================================================================
# TestShouldSkipStage - skip logic
# =============================================================================


class TestShouldSkipStage:
    """Tests for should_skip_stage method."""

    def test_health_stage_never_skipped(self):
        """Test health stage is never skipped."""
        workflow = ReleasePreparationWorkflow()

        skip, reason = workflow.should_skip_stage("health", {})

        assert skip is False
        assert reason is None

    def test_security_stage_never_skipped(self):
        """Test security stage is never skipped."""
        workflow = ReleasePreparationWorkflow()

        skip, reason = workflow.should_skip_stage("security", {})

        assert skip is False
        assert reason is None

    def test_changelog_stage_never_skipped(self):
        """Test changelog stage is never skipped."""
        workflow = ReleasePreparationWorkflow()

        skip, reason = workflow.should_skip_stage("changelog", {})

        assert skip is False
        assert reason is None

    def test_approve_skip_logic_when_clean(self):
        """Test approve stage skip logic when all checks pass."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=True)
        workflow._has_blockers = False

        skip, reason = workflow.should_skip_stage("approve", {})

        assert skip is True
        assert reason is not None

    def test_approve_skip_reason_contains_auto_approved(self):
        """Test skip reason contains 'auto-approved'."""
        workflow = ReleasePreparationWorkflow(skip_approve_if_clean=True)
        workflow._has_blockers = False

        _, reason = workflow.should_skip_stage("approve", {})

        assert "auto-approved" in reason.lower()

    def test_unknown_stage_returns_no_skip(self):
        """Test unknown stage returns no skip."""
        workflow = ReleasePreparationWorkflow()

        skip, reason = workflow.should_skip_stage("unknown_stage", {})

        assert skip is False
        assert reason is None


# =============================================================================
# TestStageMapping - stages to methods
# =============================================================================


class TestStageMapping:
    """Tests for stage to method mapping."""

    @pytest.mark.asyncio
    async def test_run_stage_health(self):
        """Test health stage routes to _health method."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_health", new_callable=AsyncMock) as mock:
            mock.return_value = ({"health": {}}, 100, 50)

            await workflow.run_stage("health", ModelTier.CHEAP, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_security(self):
        """Test security stage routes to _security method."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_security", new_callable=AsyncMock) as mock:
            mock.return_value = ({"security": {}}, 100, 50)

            await workflow.run_stage("security", ModelTier.CAPABLE, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_crew_security(self):
        """Test crew_security stage routes to _crew_security method."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        with patch.object(workflow, "_crew_security", new_callable=AsyncMock) as mock:
            mock.return_value = ({"crew_security": {}}, 100, 50)

            await workflow.run_stage("crew_security", ModelTier.PREMIUM, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_changelog(self):
        """Test changelog stage routes to _changelog method."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_changelog", new_callable=AsyncMock) as mock:
            mock.return_value = ({"changelog": {}}, 100, 50)

            await workflow.run_stage("changelog", ModelTier.CAPABLE, {"path": "."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_approve(self):
        """Test approve stage routes to _approve method."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_approve", new_callable=AsyncMock) as mock:
            mock.return_value = ({"approved": True}, 200, 100)

            await workflow.run_stage("approve", ModelTier.PREMIUM, {})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_unknown_raises_error(self):
        """Test unknown stage raises ValueError."""
        workflow = ReleasePreparationWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("unknown", ModelTier.CHEAP, {})


# =============================================================================
# TestTierMapping - tier assignments
# =============================================================================


class TestTierMapping:
    """Tests for tier assignments."""

    def test_health_tier_is_cheap(self):
        """Test health stage uses CHEAP tier."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.tier_map["health"] == ModelTier.CHEAP

    def test_security_tier_is_capable(self):
        """Test security stage uses CAPABLE tier."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.tier_map["security"] == ModelTier.CAPABLE

    def test_changelog_tier_is_capable(self):
        """Test changelog stage uses CAPABLE tier."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.tier_map["changelog"] == ModelTier.CAPABLE

    def test_approve_tier_is_premium(self):
        """Test approve stage uses PREMIUM tier."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.tier_map["approve"] == ModelTier.PREMIUM

    def test_crew_security_tier_is_premium(self):
        """Test crew_security stage uses PREMIUM tier."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        assert workflow.tier_map["crew_security"] == ModelTier.PREMIUM

    def test_get_tier_for_stage(self):
        """Test get_tier_for_stage method."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.get_tier_for_stage("health") == ModelTier.CHEAP
        assert workflow.get_tier_for_stage("security") == ModelTier.CAPABLE


# =============================================================================
# TestHealthStage - _health method
# =============================================================================


class TestHealthStage:
    """Tests for _health stage method."""

    @pytest.mark.asyncio
    async def test_health_returns_tuple(self):
        """Test _health returns expected tuple format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, input_tokens, output_tokens = await workflow._health(
                {"path": tmpdir},
                ModelTier.CHEAP,
            )

            assert isinstance(result, dict)
            assert isinstance(input_tokens, int)
            assert isinstance(output_tokens, int)

    @pytest.mark.asyncio
    async def test_health_result_contains_checks(self):
        """Test health result contains checks dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._health({"path": tmpdir}, ModelTier.CHEAP)

            assert "health" in result
            assert "checks" in result["health"]

    @pytest.mark.asyncio
    async def test_health_result_contains_health_score(self):
        """Test health result contains health_score."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._health({"path": tmpdir}, ModelTier.CHEAP)

            assert "health_score" in result["health"]

    @pytest.mark.asyncio
    async def test_health_result_contains_passed_flag(self):
        """Test health result contains passed flag."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._health({"path": tmpdir}, ModelTier.CHEAP)

            assert "passed" in result["health"]

    @pytest.mark.asyncio
    async def test_health_preserves_input_data(self):
        """Test health preserves input data in result."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()
            input_data = {"path": tmpdir, "extra_key": "extra_value"}

            result, _, _ = await workflow._health(input_data, ModelTier.CHEAP)

            assert result["path"] == tmpdir
            assert result["extra_key"] == "extra_value"


# =============================================================================
# TestSecurityStage - _security method
# =============================================================================


class TestSecurityStage:
    """Tests for _security stage method."""

    @pytest.mark.asyncio
    async def test_security_returns_tuple(self):
        """Test _security returns expected tuple format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, input_tokens, output_tokens = await workflow._security(
                {"path": tmpdir},
                ModelTier.CAPABLE,
            )

            assert isinstance(result, dict)
            assert isinstance(input_tokens, int)
            assert isinstance(output_tokens, int)

    @pytest.mark.asyncio
    async def test_security_result_contains_issues(self):
        """Test security result contains issues list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            assert "security" in result
            assert "issues" in result["security"]
            assert isinstance(result["security"]["issues"], list)

    @pytest.mark.asyncio
    async def test_security_detects_hardcoded_password(self):
        """Test security detects hardcoded password."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "config.py"
            vuln_file.write_text('password = "supersecret123"')

            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            issues = result["security"]["issues"]
            assert len(issues) > 0
            assert any(i["type"] == "hardcoded_secret" for i in issues)

    @pytest.mark.asyncio
    async def test_security_detects_eval(self):
        """Test security detects eval usage."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "dangerous.py"
            vuln_file.write_text("result = eval(user_input)")

            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            issues = result["security"]["issues"]
            assert len(issues) > 0
            assert any(i["type"] == "dangerous_function" for i in issues)

    @pytest.mark.asyncio
    async def test_security_sets_blockers_on_high_severity(self):
        """Test security sets _has_blockers on high severity issues."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "config.py"
            vuln_file.write_text('password = "secret"')

            workflow = ReleasePreparationWorkflow()

            await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            assert workflow._has_blockers is True

    @pytest.mark.asyncio
    async def test_security_clean_code_no_blockers(self):
        """Test security doesn't set blockers on clean code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            clean_file = Path(tmpdir) / "clean.py"
            clean_file.write_text("def safe_function():\n    return 42")

            workflow = ReleasePreparationWorkflow()

            await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            assert workflow._has_blockers is False


# =============================================================================
# TestChangelogStage - _changelog method
# =============================================================================


class TestChangelogStage:
    """Tests for _changelog stage method."""

    @pytest.mark.asyncio
    async def test_changelog_returns_tuple(self):
        """Test _changelog returns expected tuple format."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, input_tokens, output_tokens = await workflow._changelog(
                {"path": tmpdir},
                ModelTier.CAPABLE,
            )

            assert isinstance(result, dict)
            assert isinstance(input_tokens, int)
            assert isinstance(output_tokens, int)

    @pytest.mark.asyncio
    async def test_changelog_result_contains_commits(self):
        """Test changelog result contains commits list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._changelog({"path": tmpdir}, ModelTier.CAPABLE)

            assert "changelog" in result
            assert "commits" in result["changelog"]
            assert isinstance(result["changelog"]["commits"], list)

    @pytest.mark.asyncio
    async def test_changelog_result_contains_total_commits(self):
        """Test changelog result contains total_commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._changelog({"path": tmpdir}, ModelTier.CAPABLE)

            assert "total_commits" in result["changelog"]

    @pytest.mark.asyncio
    async def test_changelog_result_contains_generated_at(self):
        """Test changelog result contains generated_at timestamp."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._changelog({"path": tmpdir}, ModelTier.CAPABLE)

            assert "generated_at" in result["changelog"]

    @pytest.mark.asyncio
    async def test_changelog_uses_since_parameter(self):
        """Test changelog uses since parameter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._changelog(
                {"path": tmpdir, "since": "2 weeks ago"},
                ModelTier.CAPABLE,
            )

            assert result["changelog"]["period"] == "2 weeks ago"


# =============================================================================
# TestApproveStage - _approve method
# =============================================================================


class TestApproveStage:
    """Tests for _approve stage method."""

    @pytest.mark.asyncio
    async def test_approve_returns_tuple(self):
        """Test _approve returns expected tuple format."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("Assessment text", 100, 50)

            result, input_tokens, output_tokens = await workflow._approve(
                {
                    "health": {"passed": True, "health_score": 100, "checks": {}},
                    "security": {"passed": True, "total_issues": 0},
                    "changelog": {"total_commits": 5},
                },
                ModelTier.PREMIUM,
            )

            assert isinstance(result, dict)
            assert isinstance(input_tokens, int)
            assert isinstance(output_tokens, int)

    @pytest.mark.asyncio
    async def test_approve_result_contains_approved_flag(self):
        """Test approve result contains approved flag."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("Assessment", 100, 50)

            result, _, _ = await workflow._approve(
                {
                    "health": {
                        "passed": True,
                        "health_score": 100,
                        "checks": {},
                        "failed_checks": [],
                    },
                    "security": {"passed": True, "total_issues": 0, "high_severity": 0},
                    "changelog": {"total_commits": 5},
                },
                ModelTier.PREMIUM,
            )

            assert "approved" in result

    @pytest.mark.asyncio
    async def test_approve_result_contains_confidence(self):
        """Test approve result contains confidence level."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("Assessment", 100, 50)

            result, _, _ = await workflow._approve(
                {
                    "health": {
                        "passed": True,
                        "health_score": 100,
                        "checks": {},
                        "failed_checks": [],
                    },
                    "security": {"passed": True, "total_issues": 0, "high_severity": 0},
                    "changelog": {"total_commits": 5},
                },
                ModelTier.PREMIUM,
            )

            assert "confidence" in result
            assert result["confidence"] in ["high", "medium", "low"]

    @pytest.mark.asyncio
    async def test_approve_not_approved_with_blockers(self):
        """Test approve returns not approved when blockers exist."""
        workflow = ReleasePreparationWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock:
            mock.return_value = ("Assessment", 100, 50)

            result, _, _ = await workflow._approve(
                {
                    "health": {
                        "passed": False,
                        "health_score": 60,
                        "checks": {},
                        "failed_checks": ["lint"],
                    },
                    "security": {"passed": True, "total_issues": 0, "high_severity": 0},
                    "changelog": {"total_commits": 5},
                },
                ModelTier.PREMIUM,
            )

            assert result["approved"] is False
            assert len(result["blockers"]) > 0


# =============================================================================
# TestFormatReleaseReport - report formatting
# =============================================================================


class TestFormatReleaseReport:
    """Tests for format_release_prep_report function."""

    def test_format_report_returns_string(self):
        """Test format_release_prep_report returns a string."""
        result = {
            "approved": True,
            "confidence": "high",
            "blockers": [],
            "warnings": [],
            "health_score": 100,
            "commit_count": 5,
            "assessment": "All good",
            "recommendation": "Ready for release",
            "model_tier_used": "premium",
        }
        input_data = {
            "health": {"health_score": 100, "checks": {}},
            "security": {
                "total_issues": 0,
                "high_severity": 0,
                "medium_severity": 0,
                "passed": True,
            },
            "changelog": {"total_commits": 5, "by_category": {}, "period": "1 week ago"},
        }

        report = format_release_prep_report(result, input_data)

        assert isinstance(report, str)
        assert len(report) > 0

    def test_format_report_contains_status(self):
        """Test report contains status line."""
        result = {
            "approved": True,
            "confidence": "high",
            "blockers": [],
            "warnings": [],
            "recommendation": "Ready",
            "model_tier_used": "premium",
        }
        input_data = {"health": {}, "security": {}, "changelog": {}}

        report = format_release_prep_report(result, input_data)

        assert "Status:" in report

    def test_format_report_shows_ready_when_approved(self):
        """Test report shows ready when approved."""
        result = {
            "approved": True,
            "confidence": "high",
            "blockers": [],
            "warnings": [],
            "recommendation": "Ready",
            "model_tier_used": "premium",
        }
        input_data = {"health": {}, "security": {}, "changelog": {}}

        report = format_release_prep_report(result, input_data)

        assert "READY" in report

    def test_format_report_shows_not_ready_when_not_approved(self):
        """Test report shows not ready when not approved."""
        result = {
            "approved": False,
            "confidence": "low",
            "blockers": ["Test failure"],
            "warnings": [],
            "recommendation": "Fix issues",
            "model_tier_used": "premium",
        }
        input_data = {"health": {}, "security": {}, "changelog": {}}

        report = format_release_prep_report(result, input_data)

        assert "NOT READY" in report

    def test_format_report_includes_blockers(self):
        """Test report includes blockers when present."""
        result = {
            "approved": False,
            "confidence": "low",
            "blockers": ["Security issue found"],
            "warnings": [],
            "recommendation": "Fix",
            "model_tier_used": "premium",
        }
        input_data = {"health": {}, "security": {}, "changelog": {}}

        report = format_release_prep_report(result, input_data)

        assert "BLOCKERS" in report
        assert "Security issue found" in report


# =============================================================================
# TestIntegration - workflow combinations
# =============================================================================


class TestIntegration:
    """Integration tests for workflow combinations."""

    def test_workflow_with_all_options(self):
        """Test workflow initialization with all options."""
        workflow = ReleasePreparationWorkflow(
            skip_approve_if_clean=False,
            use_security_crew=True,
            crew_config={"verbose": True},
        )

        assert workflow.skip_approve_if_clean is False
        assert workflow.use_security_crew is True
        assert workflow.crew_config == {"verbose": True}
        assert "crew_security" in workflow.stages

    def test_workflow_describe(self):
        """Test workflow describe method."""
        workflow = ReleasePreparationWorkflow()

        description = workflow.describe()

        assert "release-prep" in description
        assert "health" in description
        assert "security" in description

    @pytest.mark.asyncio
    async def test_stage_transitions(self):
        """Test data flows between stages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            # Run health
            health_result, _, _ = await workflow._health({"path": tmpdir}, ModelTier.CHEAP)
            assert "health" in health_result

            # Run security with health result
            security_result, _, _ = await workflow._security(health_result, ModelTier.CAPABLE)
            assert "security" in security_result
            assert "health" in security_result

            # Run changelog with accumulated data
            changelog_result, _, _ = await workflow._changelog(security_result, ModelTier.CAPABLE)
            assert "changelog" in changelog_result
            assert "security" in changelog_result
            assert "health" in changelog_result

    @pytest.mark.asyncio
    async def test_blockers_flag_propagates(self):
        """Test _has_blockers flag propagates through stages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            vuln_file = Path(tmpdir) / "config.py"
            vuln_file.write_text('password = "secret"')

            workflow = ReleasePreparationWorkflow()

            # Initially no blockers
            assert workflow._has_blockers is False

            # Security stage should set blockers
            await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            assert workflow._has_blockers is True

            # Should not skip approve now
            skip, _ = workflow.should_skip_stage("approve", {})
            assert skip is False


# =============================================================================
# TestCrewSecurityStage - _crew_security method
# =============================================================================


class TestCrewSecurityStage:
    """Tests for _crew_security stage method."""

    @pytest.mark.asyncio
    async def test_crew_security_fallback_when_not_available(self):
        """Test crew_security falls back when crew not available."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        with patch(
            "src.empathy_os.workflows.security_adapters._check_crew_available",
        ) as mock_check:
            mock_check.return_value = False

            result, _, _ = await workflow._crew_security({"path": "."}, ModelTier.PREMIUM)

            assert result["crew_security"]["available"] is False
            assert result["crew_security"]["fallback"] is True

    @pytest.mark.asyncio
    async def test_crew_security_fallback_when_audit_fails(self):
        """Test crew_security falls back when audit fails."""
        workflow = ReleasePreparationWorkflow(use_security_crew=True)

        with (
            patch("src.empathy_os.workflows.security_adapters._check_crew_available") as mock_check,
            patch(
                "src.empathy_os.workflows.security_adapters._get_crew_audit",
                new_callable=AsyncMock,
            ) as mock_audit,
        ):
            mock_check.return_value = True
            mock_audit.return_value = None  # Simulates failure

            result, _, _ = await workflow._crew_security({"path": "."}, ModelTier.PREMIUM)

            assert result["crew_security"]["available"] is True
            assert result["crew_security"]["fallback"] is True


# =============================================================================
# Additional edge case tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_workflow_name_matches_class(self):
        """Test instance name matches class name."""
        workflow = ReleasePreparationWorkflow()

        assert workflow.name == ReleasePreparationWorkflow.name

    @pytest.mark.asyncio
    async def test_health_with_missing_path(self):
        """Test health uses default path when not provided."""
        workflow = ReleasePreparationWorkflow()

        result, _, _ = await workflow._health({}, ModelTier.CHEAP)

        assert "health" in result

    @pytest.mark.asyncio
    async def test_security_skips_venv_directories(self):
        """Test security skips venv directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "venv"
            venv_dir.mkdir()
            (venv_dir / "lib.py").write_text('password = "secret"')

            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            # venv files should be skipped
            issues = result["security"]["issues"]
            assert all("venv" not in i.get("file", "") for i in issues)

    @pytest.mark.asyncio
    async def test_security_skips_git_directories(self):
        """Test security skips .git directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            git_dir = Path(tmpdir) / ".git"
            git_dir.mkdir()
            (git_dir / "config.py").write_text('password = "secret"')

            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._security({"path": tmpdir}, ModelTier.CAPABLE)

            issues = result["security"]["issues"]
            assert all(".git" not in i.get("file", "") for i in issues)

    def test_multiple_workflow_instances_independent(self):
        """Test multiple workflow instances are independent."""
        workflow1 = ReleasePreparationWorkflow(skip_approve_if_clean=True)
        workflow2 = ReleasePreparationWorkflow(skip_approve_if_clean=False)

        workflow1._has_blockers = True

        assert workflow1._has_blockers is True
        assert workflow2._has_blockers is False
        assert workflow1.skip_approve_if_clean != workflow2.skip_approve_if_clean

    @pytest.mark.asyncio
    async def test_changelog_handles_no_git_repo(self):
        """Test changelog handles directories without git."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workflow = ReleasePreparationWorkflow()

            result, _, _ = await workflow._changelog({"path": tmpdir}, ModelTier.CAPABLE)

            # Should not crash, just return empty commits
            assert result["changelog"]["commits"] == [] or result["changelog"]["total_commits"] >= 0

    def test_tier_map_all_valid_model_tiers(self):
        """Test all tier_map values are valid ModelTier enums."""
        workflow = ReleasePreparationWorkflow()

        for _stage, tier in workflow.tier_map.items():
            assert isinstance(tier, ModelTier)
            assert tier in [ModelTier.CHEAP, ModelTier.CAPABLE, ModelTier.PREMIUM]
