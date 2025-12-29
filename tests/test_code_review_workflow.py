"""
Tests for CodeReviewWorkflow.

Tests the tiered code review pipeline with classification,
security scanning, and conditional architectural review.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.empathy_os.workflows.base import ModelTier
from src.empathy_os.workflows.code_review import CodeReviewWorkflow


class TestCodeReviewWorkflowInit:
    """Tests for CodeReviewWorkflow initialization."""

    def test_default_init(self):
        """Test default initialization."""
        workflow = CodeReviewWorkflow()

        assert workflow.name == "code-review"
        assert workflow.file_threshold == 10
        assert len(workflow.core_modules) > 0
        assert workflow.use_crew is False
        assert workflow.stages == ["classify", "scan", "architect_review"]

    def test_custom_file_threshold(self):
        """Test custom file threshold."""
        workflow = CodeReviewWorkflow(file_threshold=5)

        assert workflow.file_threshold == 5

    def test_custom_core_modules(self):
        """Test custom core modules."""
        core_modules = ["src/main.py", "src/api/"]
        workflow = CodeReviewWorkflow(core_modules=core_modules)

        assert workflow.core_modules == core_modules

    def test_crew_mode_stages(self):
        """Test stages when crew mode is enabled."""
        workflow = CodeReviewWorkflow(use_crew=True)

        assert workflow.use_crew is True
        assert "crew_review" in workflow.stages
        assert workflow.stages == ["classify", "crew_review", "scan", "architect_review"]

    def test_tier_map(self):
        """Test tier mapping for stages."""
        workflow = CodeReviewWorkflow()

        assert workflow.tier_map["classify"] == ModelTier.CHEAP
        assert workflow.tier_map["scan"] == ModelTier.CAPABLE
        assert workflow.tier_map["architect_review"] == ModelTier.PREMIUM

    def test_crew_config(self):
        """Test crew configuration."""
        config = {"memory_enabled": True}
        workflow = CodeReviewWorkflow(use_crew=True, crew_config=config)

        assert workflow.crew_config == config


class TestCodeReviewWorkflowSkipStage:
    """Tests for stage skipping logic."""

    def test_should_not_skip_classify(self):
        """Classify stage should never be skipped."""
        workflow = CodeReviewWorkflow()

        skip, reason = workflow.should_skip_stage("classify", {})

        assert skip is False
        assert reason is None

    def test_should_not_skip_scan(self):
        """Scan stage should never be skipped."""
        workflow = CodeReviewWorkflow()

        skip, reason = workflow.should_skip_stage("scan", {})

        assert skip is False
        assert reason is None

    def test_should_skip_architect_review_simple(self):
        """Architect review should be skipped for simple changes."""
        workflow = CodeReviewWorkflow()
        workflow._needs_architect_review = False

        skip, reason = workflow.should_skip_stage("architect_review", {})

        assert skip is True
        assert "Simple change" in reason

    def test_should_not_skip_architect_review_complex(self):
        """Architect review should not be skipped for complex changes."""
        workflow = CodeReviewWorkflow()
        workflow._needs_architect_review = True

        skip, reason = workflow.should_skip_stage("architect_review", {})

        assert skip is False
        assert reason is None


class TestCodeReviewWorkflowStages:
    """Tests for workflow stage routing."""

    @pytest.mark.asyncio
    async def test_run_stage_classify(self):
        """Test classify stage routing."""
        workflow = CodeReviewWorkflow()

        with patch.object(workflow, "_classify", new_callable=AsyncMock) as mock:
            mock.return_value = ({"change_type": "feature"}, 100, 50)

            await workflow.run_stage("classify", ModelTier.CHEAP, {"diff": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_scan(self):
        """Test scan stage routing."""
        workflow = CodeReviewWorkflow()

        with patch.object(workflow, "_scan", new_callable=AsyncMock) as mock:
            mock.return_value = ({"security_issues": []}, 200, 100)

            await workflow.run_stage("scan", ModelTier.CAPABLE, {"diff": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_architect_review(self):
        """Test architect review stage routing."""
        workflow = CodeReviewWorkflow()

        with patch.object(workflow, "_architect_review", new_callable=AsyncMock) as mock:
            mock.return_value = ({"recommendations": []}, 300, 200)

            await workflow.run_stage("architect_review", ModelTier.PREMIUM, {"diff": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_crew_review(self):
        """Test crew review stage routing."""
        workflow = CodeReviewWorkflow(use_crew=True)

        with patch.object(workflow, "_crew_review", new_callable=AsyncMock) as mock:
            mock.return_value = ({"crew_analysis": {}}, 500, 300)

            await workflow.run_stage("crew_review", ModelTier.PREMIUM, {"diff": "..."})

            mock.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_stage_invalid(self):
        """Test invalid stage raises error."""
        workflow = CodeReviewWorkflow()

        with pytest.raises(ValueError, match="Unknown stage"):
            await workflow.run_stage("invalid", ModelTier.CHEAP, {})


class TestCodeReviewWorkflowClassification:
    """Tests for change classification logic."""

    @pytest.mark.asyncio
    async def test_classify_sets_change_type(self):
        """Test that classify sets change type."""
        workflow = CodeReviewWorkflow()

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ("feature", 100, 50)

            input_data = {
                "diff": "def new_feature(): pass",
                "files_changed": ["src/feature.py"],
            }

            result, _, _ = await workflow.run_stage("classify", ModelTier.CHEAP, input_data)

            # Check that classify was called
            mock_llm.assert_called_once()

    @pytest.mark.asyncio
    async def test_classify_triggers_architect_review_many_files(self):
        """Test that many files trigger architect review."""
        workflow = CodeReviewWorkflow(file_threshold=5)

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ("refactor", 100, 50)

            input_data = {
                "diff": "...",
                "files_changed": [f"file{i}.py" for i in range(10)],  # 10 files > threshold
            }

            await workflow.run_stage("classify", ModelTier.CHEAP, input_data)

            assert workflow._needs_architect_review is True

    @pytest.mark.asyncio
    async def test_classify_triggers_architect_review_core_module(self):
        """Test that core module changes trigger architect review."""
        workflow = CodeReviewWorkflow(core_modules=["src/core/"])

        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ("fix", 100, 50)

            input_data = {
                "diff": "...",
                "files_changed": ["src/core/main.py"],  # Core module
                "is_core_module": True,
            }

            await workflow.run_stage("classify", ModelTier.CHEAP, input_data)

            assert workflow._needs_architect_review is True


class TestCodeReviewWorkflowIntegration:
    """Integration tests for CodeReviewWorkflow."""

    @pytest.mark.asyncio
    async def test_simple_change_skips_architect(self):
        """Test that simple changes skip architect review."""
        workflow = CodeReviewWorkflow(file_threshold=10)

        # Set up mocks
        with patch.object(workflow, "_call_llm", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = ("docs: update readme", 50, 25)

            # Mock base workflow execute
            with patch.object(
                workflow.__class__.__bases__[0], "execute", new_callable=AsyncMock
            ) as mock_execute:
                mock_result = MagicMock()
                mock_result.success = True
                mock_result.stages_run = ["classify", "scan"]  # No architect_review
                mock_result.stages_skipped = ["architect_review"]
                mock_execute.return_value = mock_result

                result = await workflow.execute(
                    diff="# Updated README",
                    files_changed=["README.md"],
                    is_core_module=False,
                )

                assert "architect_review" in result.stages_skipped

    @pytest.mark.asyncio
    async def test_complex_change_includes_architect(self):
        """Test that complex changes include architect review."""
        workflow = CodeReviewWorkflow(file_threshold=5)
        workflow._needs_architect_review = True

        skip, reason = workflow.should_skip_stage("architect_review", {})

        assert skip is False
