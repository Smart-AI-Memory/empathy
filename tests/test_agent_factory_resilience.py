"""Tests for Agent Factory Resilience Integration

Tests the resilience wrappers (circuit breaker, retry, timeout, fallback)
applied to agents created by the Agent Factory.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio

import pytest


class TestResilienceConfig:
    """Test ResilienceConfig dataclass."""

    def test_resilience_config_defaults(self):
        """Test ResilienceConfig has sensible defaults."""
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig

        config = ResilienceConfig()

        assert config.enable_circuit_breaker is True
        assert config.failure_threshold == 3
        assert config.reset_timeout == 60.0
        assert config.enable_retry is True
        assert config.max_attempts == 2
        assert config.enable_timeout is True
        assert config.timeout_seconds == 30.0
        assert config.enable_fallback is False

    def test_resilience_config_custom(self):
        """Test ResilienceConfig with custom values."""
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig

        config = ResilienceConfig(
            failure_threshold=5,
            max_attempts=3,
            timeout_seconds=60.0,
            enable_fallback=True,
        )

        assert config.failure_threshold == 5
        assert config.max_attempts == 3
        assert config.timeout_seconds == 60.0
        assert config.enable_fallback is True

    def test_resilience_config_from_agent_config(self):
        """Test creating ResilienceConfig from AgentConfig."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig

        agent_config = AgentConfig(
            name="test",
            resilience_enabled=True,
            circuit_breaker_threshold=5,
            retry_max_attempts=4,
            timeout_seconds=45.0,
        )

        resilience_config = ResilienceConfig.from_agent_config(agent_config)

        assert resilience_config.failure_threshold == 5
        assert resilience_config.max_attempts == 4
        assert resilience_config.timeout_seconds == 45.0


class TestResilientAgentCreation:
    """Test ResilientAgent wrapper creation."""

    def test_resilient_agent_creation(self):
        """Test creating a resilient agent wrapper."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        resilient_agent = ResilientAgent(base_agent)

        assert resilient_agent.name == "test"
        assert resilient_agent._wrapped is base_agent
        assert resilient_agent._resilience_config is not None

    def test_resilient_agent_with_custom_config(self):
        """Test creating resilient agent with custom config."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig(
            failure_threshold=10,
            timeout_seconds=120.0,
        )
        resilient_agent = ResilientAgent(base_agent, config)

        assert resilient_agent._resilience_config.failure_threshold == 10
        assert resilient_agent._resilience_config.timeout_seconds == 120.0


class TestFactoryResilienceIntegration:
    """Test factory creates resilient agents when enabled."""

    def test_factory_creates_resilient_agent(self):
        """Test factory wraps agent with resilience when enabled."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(
            name="resilient_test",
            role="researcher",
            resilience_enabled=True,
        )

        assert isinstance(agent, ResilientAgent)

    def test_factory_respects_resilience_disabled(self):
        """Test factory does not wrap when resilience_enabled=False."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(
            name="non_resilient_test",
            role="researcher",
            resilience_enabled=False,
        )

        assert not isinstance(agent, ResilientAgent)

    def test_factory_resilience_config_params(self):
        """Test factory passes resilience config params correctly."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(
            name="configured_resilient",
            resilience_enabled=True,
            circuit_breaker_threshold=7,
            retry_max_attempts=5,
            timeout_seconds=90.0,
        )

        assert isinstance(agent, ResilientAgent)
        assert agent._resilience_config.failure_threshold == 7
        assert agent._resilience_config.max_attempts == 5
        assert agent._resilience_config.timeout_seconds == 90.0


class TestResilientAgentInvoke:
    """Test ResilientAgent invoke functionality."""

    @pytest.mark.asyncio
    async def test_resilient_agent_invoke_success(self):
        """Test successful invocation through resilient wrapper."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig(
            enable_circuit_breaker=False,  # Disable for simple test
            enable_retry=False,
            enable_timeout=False,
        )
        resilient_agent = ResilientAgent(base_agent, config)

        result = await resilient_agent.invoke("Hello")

        assert "output" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_resilient_agent_adds_metadata(self):
        """Test resilient agent adds resilience metadata."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig()
        resilient_agent = ResilientAgent(base_agent, config)

        result = await resilient_agent.invoke("Hello")

        assert "metadata" in result
        assert "resilience" in result["metadata"]
        assert result["metadata"]["resilience"]["circuit_breaker_enabled"] is True
        assert result["metadata"]["resilience"]["retry_enabled"] is True
        assert result["metadata"]["resilience"]["timeout_enabled"] is True


class TestResilientAgentTimeout:
    """Test ResilientAgent timeout functionality."""

    @pytest.mark.asyncio
    async def test_timeout_triggers_on_slow_operation(self):
        """Test that timeout triggers for slow operations."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        # Create a slow mock agent
        class SlowAgent(BaseAgent):
            async def invoke(self, input_data, context=None):
                await asyncio.sleep(5)  # Sleep longer than timeout
                return {"output": "done", "metadata": {}}

            async def stream(self, input_data, context=None):
                yield {"output": "chunk", "metadata": {}}

        slow_agent = SlowAgent(AgentConfig(name="slow"))
        config = ResilienceConfig(
            enable_circuit_breaker=False,
            enable_retry=False,
            enable_timeout=True,
            timeout_seconds=0.1,  # Very short timeout
            enable_fallback=False,
        )
        resilient_agent = ResilientAgent(slow_agent, config)

        with pytest.raises(asyncio.TimeoutError):
            await resilient_agent.invoke("test")

    @pytest.mark.asyncio
    async def test_timeout_with_fallback(self):
        """Test that fallback is used when timeout occurs."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        class SlowAgent(BaseAgent):
            async def invoke(self, input_data, context=None):
                await asyncio.sleep(5)
                return {"output": "done", "metadata": {}}

            async def stream(self, input_data, context=None):
                yield {"output": "chunk", "metadata": {}}

        slow_agent = SlowAgent(AgentConfig(name="slow"))
        fallback_response = {"output": "fallback used", "metadata": {"fallback": True}}
        config = ResilienceConfig(
            enable_circuit_breaker=False,
            enable_retry=False,
            enable_timeout=True,
            timeout_seconds=0.1,
            enable_fallback=True,
            fallback_value=fallback_response,
        )
        resilient_agent = ResilientAgent(slow_agent, config)

        result = await resilient_agent.invoke("test")

        assert result["output"] == "fallback used"
        assert result["metadata"]["fallback"] is True


class TestResilientAgentRetry:
    """Test ResilientAgent retry functionality."""

    @pytest.mark.asyncio
    async def test_retry_on_transient_error(self):
        """Test retry mechanism on transient errors."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        # Agent that fails twice then succeeds
        call_count = 0

        class FailingAgent(BaseAgent):
            async def invoke(self, input_data, context=None):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise Exception("Transient error")
                return {"output": "success", "metadata": {}}

            async def stream(self, input_data, context=None):
                yield {"output": "chunk", "metadata": {}}

        failing_agent = FailingAgent(AgentConfig(name="failing"))
        config = ResilienceConfig(
            enable_circuit_breaker=False,
            enable_retry=True,
            max_attempts=3,
            initial_delay=0.01,  # Fast retries for testing
            enable_timeout=False,
        )
        resilient_agent = ResilientAgent(failing_agent, config)

        result = await resilient_agent.invoke("test")

        assert result["output"] == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises(self):
        """Test that exception is raised when retries exhausted."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        class AlwaysFailingAgent(BaseAgent):
            async def invoke(self, input_data, context=None):
                raise Exception("Permanent error")

            async def stream(self, input_data, context=None):
                yield {"output": "chunk", "metadata": {}}

        failing_agent = AlwaysFailingAgent(AgentConfig(name="always_failing"))
        config = ResilienceConfig(
            enable_circuit_breaker=False,
            enable_retry=True,
            max_attempts=2,
            initial_delay=0.01,
            enable_timeout=False,
            enable_fallback=False,
        )
        resilient_agent = ResilientAgent(failing_agent, config)

        with pytest.raises(Exception, match="Permanent error"):
            await resilient_agent.invoke("test")


class TestResilientAgentCircuitBreaker:
    """Test ResilientAgent circuit breaker functionality."""

    @pytest.mark.asyncio
    async def test_circuit_breaker_opens(self):
        """Test circuit breaker opens after failures."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, BaseAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent
        from empathy_os.resilience import CircuitOpenError

        class AlwaysFailingAgent(BaseAgent):
            async def invoke(self, input_data, context=None):
                raise Exception("Failure")

            async def stream(self, input_data, context=None):
                yield {"output": "chunk", "metadata": {}}

        failing_agent = AlwaysFailingAgent(AgentConfig(name="failing"))
        config = ResilienceConfig(
            enable_circuit_breaker=True,
            failure_threshold=2,
            reset_timeout=60.0,
            enable_retry=False,  # Disable retry to see failures immediately
            enable_timeout=False,
            enable_fallback=False,
        )
        resilient_agent = ResilientAgent(failing_agent, config)

        # First two failures
        with pytest.raises(Exception, match="Failure"):
            await resilient_agent.invoke("test")
        with pytest.raises(Exception, match="Failure"):
            await resilient_agent.invoke("test")

        # Third request should be rejected by circuit breaker
        with pytest.raises(CircuitOpenError):
            await resilient_agent.invoke("test")

    def test_circuit_state_property(self):
        """Test circuit_state property."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig(enable_circuit_breaker=True)
        resilient_agent = ResilientAgent(base_agent, config)

        assert resilient_agent.circuit_state == "closed"

    def test_reset_circuit_breaker(self):
        """Test manual circuit breaker reset."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig(enable_circuit_breaker=True, failure_threshold=1)
        resilient_agent = ResilientAgent(base_agent, config)

        # Simulate opening the circuit (record_failure requires an exception)
        test_error = Exception("Test failure")
        resilient_agent._circuit_breaker.record_failure(test_error)
        resilient_agent._circuit_breaker.record_failure(test_error)
        assert resilient_agent.circuit_state == "open"

        # Reset
        resilient_agent.reset_circuit_breaker()
        assert resilient_agent.circuit_state == "closed"


class TestResilientAgentDelegation:
    """Test ResilientAgent properly delegates to wrapped agent."""

    def test_add_tool_delegation(self):
        """Test add_tool is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        resilient_agent = ResilientAgent(base_agent)

        tool = {"name": "test_tool", "func": lambda x: x}
        resilient_agent.add_tool(tool)

        assert tool in base_agent.config.tools

    @pytest.mark.asyncio
    async def test_conversation_history_delegation(self):
        """Test conversation history is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilienceConfig, ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        config = ResilienceConfig(
            enable_circuit_breaker=False,
            enable_retry=False,
            enable_timeout=False,
        )
        resilient_agent = ResilientAgent(base_agent, config)

        await resilient_agent.invoke("Test message")

        history = resilient_agent.get_conversation_history()
        assert len(history) > 0

        resilient_agent.clear_history()
        assert len(resilient_agent.get_conversation_history()) == 0

    def test_model_property_delegation(self):
        """Test model property is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test", model_tier="premium"))

        resilient_agent = ResilientAgent(base_agent)

        assert resilient_agent.model == base_agent.model


class TestAgentConfigResilienceFields:
    """Test AgentConfig resilience fields."""

    def test_agent_config_resilience_defaults(self):
        """Test AgentConfig has resilience defaults."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        config = AgentConfig(name="test")

        assert config.resilience_enabled is False
        assert config.circuit_breaker_threshold == 3
        assert config.retry_max_attempts == 2
        assert config.timeout_seconds == 30.0

    def test_agent_config_resilience_custom(self):
        """Test AgentConfig with custom resilience values."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        config = AgentConfig(
            name="test",
            resilience_enabled=True,
            circuit_breaker_threshold=10,
            retry_max_attempts=5,
            timeout_seconds=120.0,
        )

        assert config.resilience_enabled is True
        assert config.circuit_breaker_threshold == 10
        assert config.retry_max_attempts == 5
        assert config.timeout_seconds == 120.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
