"""Unit Tests for EmpathyLLMExecutor

Comprehensive tests for the executor that handles LLM calls
across different providers and tiers.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from empathy_os.models import ExecutionContext
from empathy_os.models.empathy_executor import EmpathyLLMExecutor


class TestEmpathyLLMExecutorCreation:
    """Tests for executor initialization."""

    def test_creates_with_anthropic_provider(self):
        """Test executor creation with Anthropic provider."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor(provider="anthropic")
            assert executor._provider == "anthropic"

    def test_creates_with_openai_provider(self):
        """Test executor creation with OpenAI provider."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor(provider="openai")
            assert executor._provider == "openai"

    def test_creates_with_google_provider(self):
        """Test executor creation with Google provider."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor(provider="google")
            assert executor._provider == "google"

    def test_creates_with_explicit_api_key(self):
        """Test executor creation with explicit API key."""
        executor = EmpathyLLMExecutor(provider="anthropic", api_key="explicit-key")
        assert executor._api_key == "explicit-key"

    def test_defaults_to_anthropic_provider(self):
        """Test executor defaults to Anthropic if no provider specified."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor()
            assert executor._provider == "anthropic"


class TestEmpathyLLMExecutorTaskRouting:
    """Tests for task type to tier routing (uses tasks module)."""

    @pytest.mark.parametrize(
        "task_type,expected_tier_value",
        [
            # Cheap tier tasks
            ("summarize", "cheap"),
            ("triage", "cheap"),
            ("classify", "cheap"),
            ("simple_qa", "cheap"),
            # Capable tier tasks
            ("review_security", "capable"),
            ("analyze_performance", "capable"),
            ("fix_bug", "capable"),
            ("generate_code", "capable"),
            ("write_tests", "capable"),
            # Premium tier tasks
            ("complex_reasoning", "premium"),
            ("architectural_decision", "premium"),
            ("coordinate", "premium"),
        ],
    )
    def test_task_type_routes_to_correct_tier(self, task_type, expected_tier_value):
        """Test that task types route to expected tiers via tasks module."""
        from empathy_os.models.tasks import get_tier_for_task

        tier = get_tier_for_task(task_type)
        # get_tier_for_task returns ModelTier enum
        tier_value = tier.value if hasattr(tier, "value") else tier
        assert tier_value == expected_tier_value, (
            f"Task '{task_type}' should route to '{expected_tier_value}', got '{tier_value}'"
        )

    def test_unknown_task_type_routes_to_capable(self):
        """Test that unknown task types default to capable tier."""
        from empathy_os.models.tasks import get_tier_for_task

        tier = get_tier_for_task("unknown_task")
        tier_value = tier.value if hasattr(tier, "value") else tier
        assert tier_value == "capable"


class TestEmpathyLLMExecutorRun:
    """Tests for the run() method."""

    @pytest.fixture
    def mock_executor(self):
        """Create executor with mocked LLM."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor(provider="anthropic")

            # Create a mock LLM that returns proper responses
            mock_llm = MagicMock()
            mock_llm.interact = AsyncMock(
                return_value={
                    "content": "Mock response",
                    "metadata": {"tokens_used": 100, "output_tokens": 50, "model": "test-model"},
                    "level_used": 3,
                },
            )
            executor._llm = mock_llm

            return executor

    @pytest.mark.asyncio
    async def test_run_returns_response(self, mock_executor):
        """Test that run() returns a response."""
        from empathy_os.models.executor import LLMResponse

        context = ExecutionContext(
            workflow_name="test-workflow",
            step_name="test-step",
        )

        # Mock the internal _get_llm method
        with patch.object(mock_executor, "_get_llm", return_value=mock_executor._llm):
            response = await mock_executor.run(
                task_type="summarize",
                prompt="Summarize this",
                context=context,
            )

            assert response is not None
            assert isinstance(response, LLMResponse)
            assert hasattr(response, "content")

    @pytest.mark.asyncio
    async def test_run_with_system_prompt(self, mock_executor):
        """Test that run() passes system prompt correctly."""
        context = ExecutionContext(
            workflow_name="test-workflow",
            step_name="test-step",
        )

        with patch.object(mock_executor, "_get_llm", return_value=mock_executor._llm):
            await mock_executor.run(
                task_type="code_review",
                prompt="Review this code",
                system="You are a code reviewer",
                context=context,
            )

            # Verify interact was called
            mock_executor._llm.interact.assert_called_once()


class TestEmpathyLLMExecutorHybridMode:
    """Tests for hybrid provider mode."""

    @pytest.fixture
    def hybrid_executor(self):
        """Create executor in hybrid mode with mocked config loading."""
        with patch.dict(
            os.environ,
            {
                "ANTHROPIC_API_KEY": "anthropic-key",
                "OPENAI_API_KEY": "openai-key",
            },
        ):
            # Create executor and manually set hybrid config
            executor = EmpathyLLMExecutor(provider="hybrid")
            executor._hybrid_config = {
                "cheap": "gpt-4o-mini",
                "capable": "claude-sonnet-4-20250514",
                "premium": "claude-opus-4-5-20251101",
            }
            return executor

    def test_hybrid_mode_initialized(self, hybrid_executor):
        """Test that hybrid mode is correctly initialized."""
        assert hybrid_executor._provider == "hybrid"

    def test_hybrid_mode_config_structure(self, hybrid_executor):
        """Test that hybrid config has expected structure."""
        config = hybrid_executor._hybrid_config
        assert config is not None
        assert "cheap" in config
        assert "capable" in config
        assert "premium" in config

    def test_hybrid_mode_provider_detection(self, hybrid_executor):
        """Test that _get_provider_for_model detects providers correctly."""
        assert hybrid_executor._get_provider_for_model("gpt-4o-mini") == "openai"
        assert hybrid_executor._get_provider_for_model("claude-sonnet-4") == "anthropic"
        assert hybrid_executor._get_provider_for_model("gemini-pro") == "google"
        assert hybrid_executor._get_provider_for_model("llama3:8b") == "ollama"


class TestEmpathyLLMExecutorCostTracking:
    """Tests for cost tracking functionality."""

    @pytest.fixture
    def executor_with_telemetry(self, tmp_path):
        """Create executor with telemetry store."""
        from empathy_os.models.telemetry import TelemetryStore

        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            store = TelemetryStore(storage_dir=tmp_path)
            executor = EmpathyLLMExecutor(
                provider="anthropic",
                telemetry_store=store,
            )
            return executor

    def test_executor_has_telemetry_store(self, executor_with_telemetry):
        """Test that executor has telemetry store configured."""
        assert executor_with_telemetry._telemetry is not None

    @pytest.mark.asyncio
    async def test_run_tracks_token_usage(self, executor_with_telemetry):
        """Test that run() returns response with token counts."""
        # Mock the internal LLM
        mock_llm = MagicMock()
        mock_llm.interact = AsyncMock(
            return_value={
                "content": "Response",
                "metadata": {"tokens_used": 100, "output_tokens": 50, "model": "test"},
                "level_used": 3,
            },
        )
        executor_with_telemetry._llm = mock_llm

        context = ExecutionContext(
            workflow_name="test",
            step_name="step1",
        )

        with patch.object(executor_with_telemetry, "_get_llm", return_value=mock_llm):
            response = await executor_with_telemetry.run(
                task_type="summarize",
                prompt="Test prompt",
                context=context,
            )

            # Response should include token counts
            assert hasattr(response, "tokens_input")
            assert hasattr(response, "tokens_output")


class TestEmpathyLLMExecutorErrorHandling:
    """Tests for error handling."""

    @pytest.fixture
    def executor(self):
        """Create executor for error testing."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            executor = EmpathyLLMExecutor(provider="anthropic")
            # Mock the LLM
            mock_llm = MagicMock()
            executor._llm = mock_llm
            return executor

    @pytest.mark.asyncio
    async def test_handles_api_error(self, executor):
        """Test that executor handles API errors gracefully."""
        # Make the LLM raise an error
        executor._llm.interact = AsyncMock(side_effect=Exception("API Error"))

        context = ExecutionContext(
            workflow_name="test",
            step_name="step1",
        )

        with patch.object(executor, "_get_llm", return_value=executor._llm):
            with pytest.raises(Exception) as exc_info:
                await executor.run(
                    task_type="summarize",
                    prompt="Test prompt",
                    context=context,
                )

            assert "API Error" in str(exc_info.value) or "Error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_handles_timeout(self, executor):
        """Test that executor handles timeout errors."""
        import asyncio

        # Make the LLM raise a timeout error
        executor._llm.interact = AsyncMock(side_effect=asyncio.TimeoutError("Request timed out"))

        context = ExecutionContext(
            workflow_name="test",
            step_name="step1",
        )

        with patch.object(executor, "_get_llm", return_value=executor._llm):
            with pytest.raises((asyncio.TimeoutError, Exception)):
                await executor.run(
                    task_type="summarize",
                    prompt="Test prompt",
                    context=context,
                )
