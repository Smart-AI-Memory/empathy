"""Unit tests for LLM executor module

Tests LLMResponse, ExecutionContext, and LLM protocol interfaces.
"""

import pytest

from empathy_os.models.executor import ExecutionContext, LLMResponse


@pytest.mark.unit
class TestLLMResponse:
    """Test LLMResponse dataclass"""

    def test_llm_response_creation(self):
        """Test creating LLMResponse with required fields"""
        response = LLMResponse(
            content="Test response",
            model_id="claude-sonnet-4",
            provider="anthropic",
            tier="capable",
        )

        assert response.content == "Test response"
        assert response.model_id == "claude-sonnet-4"
        assert response.provider == "anthropic"
        assert response.tier == "capable"

    def test_llm_response_with_token_counts(self):
        """Test LLMResponse with token usage"""
        response = LLMResponse(
            content="Response",
            model_id="gpt-4",
            provider="openai",
            tier="premium",
            tokens_input=100,
            tokens_output=50,
        )

        assert response.tokens_input == 100
        assert response.tokens_output == 50

    def test_llm_response_with_cost_estimate(self):
        """Test LLMResponse with cost tracking"""
        response = LLMResponse(
            content="Response",
            model_id="claude-haiku",
            provider="anthropic",
            tier="cheap",
            tokens_input=1000,
            tokens_output=500,
            cost_estimate=0.0015,
        )

        assert response.cost_estimate == pytest.approx(0.0015)

    def test_llm_response_default_values(self):
        """Test that LLMResponse has sensible defaults"""
        response = LLMResponse(
            content="Test",
            model_id="test-model",
            provider="test",
            tier="capable",
        )

        assert response.tokens_input == 0
        assert response.tokens_output == 0
        assert response.cost_estimate == 0.0
        assert response.latency_ms == 0
        assert response.metadata == {}

    def test_llm_response_with_metadata(self):
        """Test LLMResponse with custom metadata"""
        metadata = {"session_id": "abc123", "retry_count": 2}
        response = LLMResponse(
            content="Test",
            model_id="test-model",
            provider="test",
            tier="capable",
            metadata=metadata,
        )

        assert response.metadata == metadata
        assert response.metadata["session_id"] == "abc123"
        assert response.metadata["retry_count"] == 2


@pytest.mark.unit
class TestLLMResponseBackwardCompatibility:
    """Test backward compatibility aliases in LLMResponse"""

    def test_input_tokens_alias(self):
        """Test input_tokens property alias"""
        response = LLMResponse(
            content="Test",
            model_id="test",
            provider="test",
            tier="cheap",
            tokens_input=100,
        )

        assert response.input_tokens == 100
        assert response.input_tokens == response.tokens_input

    def test_output_tokens_alias(self):
        """Test output_tokens property alias"""
        response = LLMResponse(
            content="Test",
            model_id="test",
            provider="test",
            tier="cheap",
            tokens_output=50,
        )

        assert response.output_tokens == 50
        assert response.output_tokens == response.tokens_output

    def test_model_used_alias(self):
        """Test model_used property alias"""
        response = LLMResponse(
            content="Test",
            model_id="claude-sonnet-3-5",
            provider="anthropic",
            tier="capable",
        )

        assert response.model_used == "claude-sonnet-3-5"
        assert response.model_used == response.model_id

    def test_cost_alias(self):
        """Test cost property alias"""
        response = LLMResponse(
            content="Test",
            model_id="test",
            provider="test",
            tier="cheap",
            cost_estimate=0.005,
        )

        assert response.cost == pytest.approx(0.005)
        assert response.cost == response.cost_estimate

    def test_total_tokens_property(self):
        """Test total_tokens computed property"""
        response = LLMResponse(
            content="Test",
            model_id="test",
            provider="test",
            tier="cheap",
            tokens_input=100,
            tokens_output=75,
        )

        assert response.total_tokens == 175
        assert response.total_tokens == response.tokens_input + response.tokens_output


@pytest.mark.unit
class TestExecutionContext:
    """Test ExecutionContext dataclass"""

    def test_execution_context_defaults(self):
        """Test ExecutionContext with default values"""
        context = ExecutionContext()

        assert context.user_id is None
        assert context.workflow_name is None
        assert context.step_name is None
        assert context.task_type is None
        assert context.provider_hint is None
        assert context.tier_hint is None
        assert context.timeout_seconds is None
        assert context.session_id is None

    def test_execution_context_with_workflow_info(self):
        """Test ExecutionContext with workflow information"""
        context = ExecutionContext(
            user_id="user123",
            workflow_name="security-audit",
            step_name="scan",
            session_id="session456",
        )

        assert context.user_id == "user123"
        assert context.workflow_name == "security-audit"
        assert context.step_name == "scan"
        assert context.session_id == "session456"

    def test_execution_context_with_routing_hints(self):
        """Test ExecutionContext with provider/tier hints"""
        context = ExecutionContext(
            task_type="summarize",
            provider_hint="anthropic",
            tier_hint="cheap",
        )

        assert context.task_type == "summarize"
        assert context.provider_hint == "anthropic"
        assert context.tier_hint == "cheap"

    def test_execution_context_with_timeout(self):
        """Test ExecutionContext with custom timeout"""
        context = ExecutionContext(workflow_name="long-analysis", timeout_seconds=300)

        assert context.timeout_seconds == 300

    def test_execution_context_partial_initialization(self):
        """Test ExecutionContext with only some fields set"""
        context = ExecutionContext(user_id="test_user", workflow_name="code-review")

        assert context.user_id == "test_user"
        assert context.workflow_name == "code-review"
        # Other fields should still be None
        assert context.step_name is None
        assert context.provider_hint is None


@pytest.mark.unit
class TestLLMResponseCalculations:
    """Test calculated fields and cost logic in LLMResponse"""

    def test_cost_calculation_with_zero_tokens(self):
        """Test that zero tokens results in zero cost"""
        response = LLMResponse(
            content="Empty",
            model_id="test",
            provider="test",
            tier="cheap",
            tokens_input=0,
            tokens_output=0,
            cost_estimate=0.0,
        )

        assert response.cost_estimate == 0.0
        assert response.total_tokens == 0

    def test_large_token_counts(self):
        """Test handling of large token counts"""
        response = LLMResponse(
            content="Large response",
            model_id="claude-opus",
            provider="anthropic",
            tier="premium",
            tokens_input=100000,
            tokens_output=50000,
        )

        assert response.total_tokens == 150000
        assert response.tokens_input == 100000
        assert response.tokens_output == 50000

    def test_latency_tracking(self):
        """Test latency measurement"""
        response = LLMResponse(
            content="Fast response",
            model_id="test",
            provider="test",
            tier="cheap",
            latency_ms=1250,
        )

        assert response.latency_ms == 1250


@pytest.mark.unit
class TestExecutionContextMetadata:
    """Test metadata handling in ExecutionContext"""

    def test_execution_context_with_retry_policy(self):
        """Test ExecutionContext metadata for retry configuration"""
        context = ExecutionContext(
            workflow_name="resilient-workflow",
            metadata={"retry_policy": {"max_attempts": 3, "backoff_factor": 2.0}},
        )

        assert "retry_policy" in context.metadata
        assert context.metadata["retry_policy"]["max_attempts"] == 3

    def test_execution_context_with_fallback_config(self):
        """Test ExecutionContext metadata for fallback configuration"""
        context = ExecutionContext(
            workflow_name="fault-tolerant-workflow",
            metadata={
                "fallback_policy": {"fallback_model": "claude-haiku", "fallback_on_timeout": True},
            },
        )

        assert "fallback_policy" in context.metadata
        assert context.metadata["fallback_policy"]["fallback_model"] == "claude-haiku"

    def test_execution_context_empty_metadata(self):
        """Test ExecutionContext with no metadata"""
        context = ExecutionContext(workflow_name="simple-workflow")

        assert context.metadata is None or context.metadata == {}
