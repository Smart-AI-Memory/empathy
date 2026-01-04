"""Executor Integration Tests

Tests for the LLMExecutor infrastructure including:
- ExecutionContext and LLMResponse dataclasses
- MockLLMExecutor for testing
- EmpathyLLMExecutor with telemetry
- ResilientExecutor with fallback and circuit breaker
- BaseWorkflow executor integration

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from dataclasses import asdict
from pathlib import Path

import pytest

from empathy_os.models import ExecutionContext, LLMResponse, MockLLMExecutor, get_tier_for_task
from empathy_os.models.fallback import CircuitBreaker, ResilientExecutor, RetryPolicy
from empathy_os.models.telemetry import TelemetryStore


class TestExecutionContext:
    """Tests for ExecutionContext dataclass."""

    def test_create_minimal_context(self):
        """Test creating context with minimal fields."""
        ctx = ExecutionContext()
        assert ctx.user_id is None
        assert ctx.workflow_name is None
        assert ctx.metadata == {}

    def test_create_full_context(self):
        """Test creating context with all fields."""
        ctx = ExecutionContext(
            user_id="user123",
            workflow_name="security-audit",
            step_name="scan",
            task_type="analyze",
            provider_hint="anthropic",
            tier_hint="capable",
            timeout_seconds=30,
            session_id="sess_abc",
            metadata={"run_id": "run_123"},
        )
        assert ctx.user_id == "user123"
        assert ctx.workflow_name == "security-audit"
        assert ctx.step_name == "scan"
        assert ctx.task_type == "analyze"
        assert ctx.provider_hint == "anthropic"
        assert ctx.tier_hint == "capable"
        assert ctx.timeout_seconds == 30
        assert ctx.session_id == "sess_abc"
        assert ctx.metadata["run_id"] == "run_123"

    def test_context_serialization(self):
        """Test that context can be serialized to dict."""
        ctx = ExecutionContext(workflow_name="test", step_name="step1")
        data = asdict(ctx)
        assert data["workflow_name"] == "test"
        assert data["step_name"] == "step1"


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_create_response(self):
        """Test creating a response with required fields."""
        resp = LLMResponse(
            content="Hello world",
            model_id="claude-sonnet-4",
            provider="anthropic",
            tier="capable",
        )
        assert resp.content == "Hello world"
        assert resp.model_id == "claude-sonnet-4"
        assert resp.provider == "anthropic"
        assert resp.tier == "capable"
        assert resp.tokens_input == 0
        assert resp.tokens_output == 0
        assert resp.cost_estimate == 0.0
        assert resp.latency_ms == 0

    def test_response_with_tokens_and_cost(self):
        """Test response with token counts and cost."""
        resp = LLMResponse(
            content="Response text",
            model_id="claude-opus-4-5",
            provider="anthropic",
            tier="premium",
            tokens_input=1000,
            tokens_output=500,
            cost_estimate=0.0375,
            latency_ms=1500,
        )
        assert resp.tokens_input == 1000
        assert resp.tokens_output == 500
        assert resp.cost_estimate == 0.0375
        assert resp.latency_ms == 1500

    def test_backwards_compatibility_aliases(self):
        """Test backwards compatibility property aliases."""
        resp = LLMResponse(
            content="Test",
            model_id="gpt-4o",
            provider="openai",
            tier="capable",
            tokens_input=100,
            tokens_output=50,
            cost_estimate=0.001,
        )
        # Test aliases
        assert resp.input_tokens == resp.tokens_input == 100
        assert resp.output_tokens == resp.tokens_output == 50
        assert resp.model_used == resp.model_id == "gpt-4o"
        assert resp.cost == resp.cost_estimate == 0.001

    def test_total_tokens(self):
        """Test total_tokens computed property."""
        resp = LLMResponse(
            content="Test",
            model_id="test",
            provider="test",
            tier="capable",
            tokens_input=100,
            tokens_output=50,
        )
        assert resp.total_tokens == 150


class TestMockLLMExecutor:
    """Tests for MockLLMExecutor."""

    @pytest.mark.asyncio
    async def test_mock_executor_returns_default_response(self):
        """Test mock executor returns configured default."""
        executor = MockLLMExecutor(default_response="Mock result")
        response = await executor.run(task_type="summarize", prompt="Test prompt")
        assert response.content == "Mock result"
        assert response.provider == "mock"

    @pytest.mark.asyncio
    async def test_mock_executor_routes_task_types(self):
        """Test mock executor respects task type routing."""
        executor = MockLLMExecutor()

        # Cheap task
        resp_cheap = await executor.run(task_type="summarize", prompt="Test")
        assert resp_cheap.tier == "cheap"

        # Capable task
        resp_capable = await executor.run(task_type="fix_bug", prompt="Test")
        assert resp_capable.tier == "capable"

        # Premium task
        resp_premium = await executor.run(task_type="coordinate", prompt="Test")
        assert resp_premium.tier == "premium"

    @pytest.mark.asyncio
    async def test_mock_executor_records_calls(self):
        """Test mock executor records call history."""
        executor = MockLLMExecutor()

        await executor.run(task_type="summarize", prompt="First call")
        await executor.run(task_type="fix_bug", prompt="Second call")

        assert len(executor.call_history) == 2
        assert executor.call_history[0]["prompt"] == "First call"
        assert executor.call_history[1]["task_type"] == "fix_bug"

    def test_mock_executor_protocol_methods(self):
        """Test mock executor implements protocol methods."""
        executor = MockLLMExecutor(default_model="test-model")

        assert executor.get_model_for_task("summarize") == "test-model"
        assert executor.estimate_cost("summarize", 1000, 500) == 0.0


class TestCircuitBreaker:
    """Tests for CircuitBreaker."""

    def test_circuit_starts_closed(self):
        """Test circuit breaker starts in closed (available) state."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=1)
        assert cb.is_available("anthropic") is True

    def test_circuit_opens_after_threshold_failures(self):
        """Test circuit opens after reaching failure threshold."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=10)

        # Record failures
        cb.record_failure("anthropic")
        assert cb.is_available("anthropic") is True
        cb.record_failure("anthropic")
        assert cb.is_available("anthropic") is True
        cb.record_failure("anthropic")
        # Should be unavailable after 3 failures
        assert cb.is_available("anthropic") is False

    def test_circuit_per_provider_tier(self):
        """Test circuit breaker tracks per provider:tier."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=10)

        # Fail anthropic:cheap
        cb.record_failure("anthropic", "cheap")
        cb.record_failure("anthropic", "cheap")
        assert cb.is_available("anthropic", "cheap") is False

        # anthropic:capable should still be available
        assert cb.is_available("anthropic", "capable") is True

        # openai:cheap should also be available
        assert cb.is_available("openai", "cheap") is True

    def test_circuit_resets_on_success(self):
        """Test circuit resets failure count on success."""
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=10)

        cb.record_failure("anthropic")
        cb.record_failure("anthropic")
        cb.record_success("anthropic")
        cb.record_failure("anthropic")
        cb.record_failure("anthropic")

        # Should still be available (reset by success)
        assert cb.is_available("anthropic") is True

    def test_circuit_recovers_after_timeout(self):
        """Test circuit allows retry after timeout."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout_seconds=1)

        cb.record_failure("anthropic")
        cb.record_failure("anthropic")
        assert cb.is_available("anthropic") is False

        # Wait for recovery (1+ seconds)
        import time

        time.sleep(1.1)

        # Should be available again (half-open)
        assert cb.is_available("anthropic") is True


class TestResilientExecutor:
    """Tests for ResilientExecutor with fallback."""

    @pytest.mark.asyncio
    async def test_resilient_executor_with_mock(self):
        """Test resilient executor wraps inner executor."""
        mock = MockLLMExecutor(default_response="Success")
        resilient = ResilientExecutor(executor=mock)

        response = await resilient.run(task_type="summarize", prompt="Test")
        assert response.content == "Success"

    @pytest.mark.asyncio
    async def test_resilient_executor_uses_retry_policy(self):
        """Test resilient executor respects retry policy."""
        mock = MockLLMExecutor()
        retry_policy = RetryPolicy(max_retries=3, initial_delay_ms=10)
        resilient = ResilientExecutor(executor=mock, retry_policy=retry_policy)

        response = await resilient.run(task_type="fix_bug", prompt="Test")
        assert response.content == "Mock response"

    @pytest.mark.asyncio
    async def test_resilient_executor_uses_circuit_breaker(self):
        """Test resilient executor uses circuit breaker."""
        mock = MockLLMExecutor()
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)
        resilient = ResilientExecutor(executor=mock, circuit_breaker=cb)

        response = await resilient.run(task_type="summarize", prompt="Test")
        assert response is not None


class TestTelemetryIntegration:
    """Tests for telemetry integration."""

    def test_telemetry_store_creation(self):
        """Test creating a telemetry store."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = TelemetryStore(storage_dir=Path(tmpdir))
            assert store is not None

    def test_telemetry_log_call(self):
        """Test logging an LLM call."""
        from empathy_os.models.telemetry import LLMCallRecord

        with tempfile.TemporaryDirectory() as tmpdir:
            store = TelemetryStore(storage_dir=Path(tmpdir))

            record = LLMCallRecord(
                call_id="test_123",
                timestamp="2025-01-01T00:00:00",
                workflow_name="test-workflow",
                step_name="step1",
                task_type="summarize",
                provider="anthropic",
                tier="cheap",
                model_id="claude-haiku",
                input_tokens=100,
                output_tokens=50,
                estimated_cost=0.001,
                latency_ms=500,
                success=True,
            )
            store.log_call(record)

            # Verify file was created
            log_file = Path(tmpdir) / "llm_calls.jsonl"
            assert log_file.exists()


class TestTaskRouting:
    """Tests for task type to tier routing."""

    def test_cheap_tasks(self):
        """Test cheap tier tasks."""
        cheap_tasks = ["summarize", "classify", "triage", "format_code", "simple_qa"]
        for task in cheap_tasks:
            tier = get_tier_for_task(task)
            assert tier.value == "cheap", f"{task} should route to cheap"

    def test_capable_tasks(self):
        """Test capable tier tasks."""
        capable_tasks = ["fix_bug", "refactor", "write_tests", "explain_code"]
        for task in capable_tasks:
            tier = get_tier_for_task(task)
            assert tier.value == "capable", f"{task} should route to capable"

    def test_premium_tasks(self):
        """Test premium tier tasks."""
        premium_tasks = ["coordinate", "architectural_decision", "novel_problem", "final_review"]
        for task in premium_tasks:
            tier = get_tier_for_task(task)
            assert tier.value == "premium", f"{task} should route to premium"

    def test_unknown_defaults_to_capable(self):
        """Test unknown tasks default to capable tier."""
        tier = get_tier_for_task("unknown_task_type")
        assert tier.value == "capable"


class TestEndToEndWorkflowExecutor:
    """End-to-end tests for workflow with executor."""

    @pytest.mark.asyncio
    async def test_workflow_creates_default_executor(self):
        """Test workflow creates executor if none provided."""
        from empathy_os.workflows.base import BaseWorkflow, ModelTier

        class TestWorkflow(BaseWorkflow):
            name = "test-workflow"
            description = "Test workflow"
            stages = ["test_stage"]
            tier_map = {"test_stage": ModelTier.CHEAP}

            async def run_stage(self, stage_name, tier, input_data):
                return {"result": "success"}, 100, 50

        workflow = TestWorkflow(provider="anthropic")

        # Workflow should create executor lazily
        assert workflow._executor is None
        executor = workflow._get_executor()
        assert executor is not None
        assert workflow._executor is not None

    @pytest.mark.asyncio
    async def test_workflow_execution_with_mock_executor(self):
        """Test workflow execution using mock executor."""
        from empathy_os.workflows.base import BaseWorkflow, ModelTier

        mock = MockLLMExecutor(default_response="Stage complete")

        class TestWorkflow(BaseWorkflow):
            name = "test-workflow"
            description = "Test workflow"
            stages = ["analyze", "report"]
            tier_map = {
                "analyze": ModelTier.CAPABLE,
                "report": ModelTier.CHEAP,
            }

            async def run_stage(self, stage_name, tier, input_data):
                return {"stage": stage_name, "tier": tier.value}, 100, 50

        workflow = TestWorkflow(provider="anthropic", executor=mock)
        result = await workflow.execute(input="test data")

        assert result.success is True
        assert len(result.stages) == 2
        assert result.stages[0].name == "analyze"
        assert result.stages[1].name == "report"

    def test_workflow_context_creation(self):
        """Test workflow creates proper execution context."""
        from empathy_os.workflows.base import BaseWorkflow

        class TestWorkflow(BaseWorkflow):
            name = "context-test"
            description = "Test context"
            stages = []
            tier_map = {}

            async def run_stage(self, stage_name, tier, input_data):
                return {}, 0, 0

        workflow = TestWorkflow(provider="anthropic")
        workflow._run_id = "run_123"

        ctx = workflow._create_execution_context(
            step_name="step1",
            task_type="summarize",
            user_id="user123",
        )

        assert ctx.workflow_name == "context-test"
        assert ctx.step_name == "step1"
        assert ctx.user_id == "user123"
        assert ctx.metadata["task_type"] == "summarize"
        assert ctx.metadata["run_id"] == "run_123"

    def test_default_executor_is_resilient(self):
        """Test that default executor is wrapped with ResilientExecutor."""
        from empathy_os.models.fallback import ResilientExecutor
        from empathy_os.workflows.base import BaseWorkflow

        class TestWorkflow(BaseWorkflow):
            name = "resilience-test"
            description = "Test resilience wrapping"
            stages = []
            tier_map = {}

            async def run_stage(self, stage_name, tier, input_data):
                return {}, 0, 0

        workflow = TestWorkflow(provider="anthropic")

        # Get the default executor
        executor = workflow._get_executor()

        # Verify it's wrapped with ResilientExecutor
        assert isinstance(executor, ResilientExecutor)
        # Verify the inner executor exists
        assert executor._executor is not None


class TestProviderModelsSync:
    """Tests that PROVIDER_MODELS stays in sync with MODEL_REGISTRY."""

    def test_provider_models_derived_from_registry(self):
        """Verify PROVIDER_MODELS is populated from MODEL_REGISTRY."""
        from empathy_os.models import MODEL_REGISTRY
        from empathy_os.workflows.base import PROVIDER_MODELS, ModelProvider, ModelTier

        # Check anthropic models match
        assert ModelProvider.ANTHROPIC in PROVIDER_MODELS
        assert (
            PROVIDER_MODELS[ModelProvider.ANTHROPIC][ModelTier.CHEAP]
            == MODEL_REGISTRY["anthropic"]["cheap"].id
        )
        assert (
            PROVIDER_MODELS[ModelProvider.ANTHROPIC][ModelTier.CAPABLE]
            == MODEL_REGISTRY["anthropic"]["capable"].id
        )
        assert (
            PROVIDER_MODELS[ModelProvider.ANTHROPIC][ModelTier.PREMIUM]
            == MODEL_REGISTRY["anthropic"]["premium"].id
        )

    def test_provider_models_contains_all_providers(self):
        """Verify all known providers are in PROVIDER_MODELS."""
        from empathy_os.workflows.base import PROVIDER_MODELS, ModelProvider

        assert ModelProvider.ANTHROPIC in PROVIDER_MODELS
        assert ModelProvider.OPENAI in PROVIDER_MODELS
        assert ModelProvider.OLLAMA in PROVIDER_MODELS
        assert ModelProvider.HYBRID in PROVIDER_MODELS

    def test_provider_models_contains_all_tiers(self):
        """Verify all tiers are present for each provider."""
        from empathy_os.workflows.base import PROVIDER_MODELS, ModelProvider, ModelTier

        for provider in [ModelProvider.ANTHROPIC, ModelProvider.OPENAI, ModelProvider.HYBRID]:
            assert ModelTier.CHEAP in PROVIDER_MODELS[provider]
            assert ModelTier.CAPABLE in PROVIDER_MODELS[provider]
            assert ModelTier.PREMIUM in PROVIDER_MODELS[provider]
