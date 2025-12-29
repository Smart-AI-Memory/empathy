"""
Tests for empathy_llm_toolkit/agent_factory/base.py

Tests the base classes and enums for the Agent Factory:
- AgentRole enum
- AgentCapability enum
- AgentConfig dataclass
- WorkflowConfig dataclass
- BaseAgent abstract class
- BaseWorkflow abstract class
- BaseAdapter abstract class
"""

import pytest

from empathy_llm_toolkit.agent_factory.base import (
    AgentCapability,
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)


class TestAgentRoleEnum:
    """Tests for AgentRole enum."""

    def test_coordinator_value(self):
        """Test COORDINATOR role value."""
        assert AgentRole.COORDINATOR.value == "coordinator"

    def test_researcher_value(self):
        """Test RESEARCHER role value."""
        assert AgentRole.RESEARCHER.value == "researcher"

    def test_writer_value(self):
        """Test WRITER role value."""
        assert AgentRole.WRITER.value == "writer"

    def test_reviewer_value(self):
        """Test REVIEWER role value."""
        assert AgentRole.REVIEWER.value == "reviewer"

    def test_editor_value(self):
        """Test EDITOR role value."""
        assert AgentRole.EDITOR.value == "editor"

    def test_executor_value(self):
        """Test EXECUTOR role value."""
        assert AgentRole.EXECUTOR.value == "executor"

    def test_debugger_value(self):
        """Test DEBUGGER role value."""
        assert AgentRole.DEBUGGER.value == "debugger"

    def test_security_value(self):
        """Test SECURITY role value."""
        assert AgentRole.SECURITY.value == "security"

    def test_architect_value(self):
        """Test ARCHITECT role value."""
        assert AgentRole.ARCHITECT.value == "architect"

    def test_tester_value(self):
        """Test TESTER role value."""
        assert AgentRole.TESTER.value == "tester"

    def test_documenter_value(self):
        """Test DOCUMENTER role value."""
        assert AgentRole.DOCUMENTER.value == "documenter"

    def test_retriever_value(self):
        """Test RETRIEVER role value."""
        assert AgentRole.RETRIEVER.value == "retriever"

    def test_summarizer_value(self):
        """Test SUMMARIZER role value."""
        assert AgentRole.SUMMARIZER.value == "summarizer"

    def test_answerer_value(self):
        """Test ANSWERER role value."""
        assert AgentRole.ANSWERER.value == "answerer"

    def test_custom_value(self):
        """Test CUSTOM role value."""
        assert AgentRole.CUSTOM.value == "custom"

    def test_all_roles_count(self):
        """Test total number of roles."""
        assert len(AgentRole) == 15

    def test_role_from_string(self):
        """Test creating AgentRole from string."""
        assert AgentRole("coordinator") == AgentRole.COORDINATOR
        assert AgentRole("researcher") == AgentRole.RESEARCHER


class TestAgentCapabilityEnum:
    """Tests for AgentCapability enum."""

    def test_code_execution_value(self):
        """Test CODE_EXECUTION capability value."""
        assert AgentCapability.CODE_EXECUTION.value == "code_execution"

    def test_tool_use_value(self):
        """Test TOOL_USE capability value."""
        assert AgentCapability.TOOL_USE.value == "tool_use"

    def test_web_search_value(self):
        """Test WEB_SEARCH capability value."""
        assert AgentCapability.WEB_SEARCH.value == "web_search"

    def test_file_access_value(self):
        """Test FILE_ACCESS capability value."""
        assert AgentCapability.FILE_ACCESS.value == "file_access"

    def test_memory_value(self):
        """Test MEMORY capability value."""
        assert AgentCapability.MEMORY.value == "memory"

    def test_retrieval_value(self):
        """Test RETRIEVAL capability value."""
        assert AgentCapability.RETRIEVAL.value == "retrieval"

    def test_vision_value(self):
        """Test VISION capability value."""
        assert AgentCapability.VISION.value == "vision"

    def test_function_calling_value(self):
        """Test FUNCTION_CALLING capability value."""
        assert AgentCapability.FUNCTION_CALLING.value == "function_calling"

    def test_all_capabilities_count(self):
        """Test total number of capabilities."""
        assert len(AgentCapability) == 8


class TestAgentConfig:
    """Tests for AgentConfig dataclass."""

    def test_minimal_creation(self):
        """Test creating config with just name."""
        config = AgentConfig(name="test_agent")
        assert config.name == "test_agent"

    def test_default_role(self):
        """Test default role is CUSTOM."""
        config = AgentConfig(name="agent")
        assert config.role == AgentRole.CUSTOM

    def test_default_model_tier(self):
        """Test default model tier is capable."""
        config = AgentConfig(name="agent")
        assert config.model_tier == "capable"

    def test_default_temperature(self):
        """Test default temperature is 0.7."""
        config = AgentConfig(name="agent")
        assert config.temperature == 0.7

    def test_default_max_tokens(self):
        """Test default max tokens is 4096."""
        config = AgentConfig(name="agent")
        assert config.max_tokens == 4096

    def test_default_empathy_level(self):
        """Test default empathy level is 4."""
        config = AgentConfig(name="agent")
        assert config.empathy_level == 4

    def test_default_memory_enabled(self):
        """Test memory is enabled by default."""
        config = AgentConfig(name="agent")
        assert config.memory_enabled is True

    def test_default_memory_type(self):
        """Test default memory type is conversation."""
        config = AgentConfig(name="agent")
        assert config.memory_type == "conversation"

    def test_default_resilience_disabled(self):
        """Test resilience is disabled by default."""
        config = AgentConfig(name="agent")
        assert config.resilience_enabled is False

    def test_default_circuit_breaker_threshold(self):
        """Test default circuit breaker threshold."""
        config = AgentConfig(name="agent")
        assert config.circuit_breaker_threshold == 3

    def test_default_retry_max_attempts(self):
        """Test default retry max attempts."""
        config = AgentConfig(name="agent")
        assert config.retry_max_attempts == 2

    def test_default_timeout_seconds(self):
        """Test default timeout seconds."""
        config = AgentConfig(name="agent")
        assert config.timeout_seconds == 30.0

    def test_default_capabilities_empty(self):
        """Test default capabilities is empty list."""
        config = AgentConfig(name="agent")
        assert config.capabilities == []

    def test_default_tools_empty(self):
        """Test default tools is empty list."""
        config = AgentConfig(name="agent")
        assert config.tools == []

    def test_full_config_creation(self):
        """Test creating config with all options."""
        config = AgentConfig(
            name="security_analyst",
            role=AgentRole.SECURITY,
            description="Analyzes code for security issues",
            model_tier="premium",
            model_override="claude-opus-4-20250514",
            capabilities=[AgentCapability.CODE_EXECUTION, AgentCapability.FILE_ACCESS],
            tools=[{"name": "scan"}],
            system_prompt="You are a security expert",
            temperature=0.3,
            max_tokens=8192,
            empathy_level=5,
            use_patterns=True,
            track_costs=True,
            memory_enabled=True,
            memory_type="vector",
            resilience_enabled=True,
            circuit_breaker_threshold=5,
            retry_max_attempts=3,
            timeout_seconds=60.0,
        )
        assert config.name == "security_analyst"
        assert config.role == AgentRole.SECURITY
        assert config.model_tier == "premium"
        assert len(config.capabilities) == 2
        assert config.resilience_enabled is True


class TestWorkflowConfig:
    """Tests for WorkflowConfig dataclass."""

    def test_minimal_creation(self):
        """Test creating config with just name."""
        config = WorkflowConfig(name="test_workflow")
        assert config.name == "test_workflow"

    def test_default_mode(self):
        """Test default mode is sequential."""
        config = WorkflowConfig(name="workflow")
        assert config.mode == "sequential"

    def test_default_max_iterations(self):
        """Test default max iterations is 10."""
        config = WorkflowConfig(name="workflow")
        assert config.max_iterations == 10

    def test_default_timeout(self):
        """Test default timeout is 300 seconds."""
        config = WorkflowConfig(name="workflow")
        assert config.timeout_seconds == 300

    def test_default_checkpointing(self):
        """Test checkpointing is enabled by default."""
        config = WorkflowConfig(name="workflow")
        assert config.checkpointing is True

    def test_default_retry_on_error(self):
        """Test retry on error is enabled by default."""
        config = WorkflowConfig(name="workflow")
        assert config.retry_on_error is True

    def test_default_max_retries(self):
        """Test default max retries is 3."""
        config = WorkflowConfig(name="workflow")
        assert config.max_retries == 3

    def test_full_config_creation(self):
        """Test creating config with all options."""
        config = WorkflowConfig(
            name="code_review_pipeline",
            description="Multi-agent code review",
            mode="parallel",
            max_iterations=5,
            timeout_seconds=600,
            state_schema={"findings": [], "score": 0},
            checkpointing=True,
            retry_on_error=True,
            max_retries=2,
            framework_options={"streaming": True},
        )
        assert config.name == "code_review_pipeline"
        assert config.mode == "parallel"
        assert config.state_schema == {"findings": [], "score": 0}


class ConcreteAgent(BaseAgent):
    """Concrete implementation of BaseAgent for testing."""

    async def invoke(self, input_data, context=None):
        return {"output": f"Response to: {input_data}", "metadata": {}}

    async def stream(self, input_data, context=None):
        yield {"chunk": "Hello"}
        yield {"chunk": " World"}


class TestBaseAgent:
    """Tests for BaseAgent abstract class."""

    def test_init_sets_config(self):
        """Test init sets config."""
        config = AgentConfig(name="test_agent", role=AgentRole.RESEARCHER)
        agent = ConcreteAgent(config)
        assert agent.config == config

    def test_init_sets_name(self):
        """Test init sets name from config."""
        config = AgentConfig(name="my_agent")
        agent = ConcreteAgent(config)
        assert agent.name == "my_agent"

    def test_init_sets_role(self):
        """Test init sets role from config."""
        config = AgentConfig(name="agent", role=AgentRole.WRITER)
        agent = ConcreteAgent(config)
        assert agent.role == AgentRole.WRITER

    def test_init_empty_conversation_history(self):
        """Test init creates empty conversation history."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        assert agent._conversation_history == []

    def test_add_tool(self):
        """Test adding a tool."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        tool = {"name": "search", "func": lambda x: x}
        agent.add_tool(tool)
        assert tool in agent.config.tools

    def test_get_conversation_history_returns_copy(self):
        """Test get_conversation_history returns a copy."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        agent._conversation_history.append({"role": "user", "content": "hello"})

        history = agent.get_conversation_history()
        assert len(history) == 1
        assert history is not agent._conversation_history

    def test_clear_history(self):
        """Test clearing conversation history."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        agent._conversation_history.append({"role": "user", "content": "hello"})

        agent.clear_history()
        assert agent._conversation_history == []

    def test_model_property_with_override(self):
        """Test model property returns override when set."""
        config = AgentConfig(name="agent", model_override="claude-opus-4")
        agent = ConcreteAgent(config)
        assert agent.model == "claude-opus-4"

    def test_model_property_without_override(self):
        """Test model property returns tier when no override."""
        config = AgentConfig(name="agent", model_tier="premium")
        agent = ConcreteAgent(config)
        assert agent.model == "tier:premium"

    @pytest.mark.asyncio
    async def test_invoke(self):
        """Test invoke method."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        result = await agent.invoke("test input")
        assert result["output"] == "Response to: test input"

    @pytest.mark.asyncio
    async def test_stream(self):
        """Test stream method."""
        config = AgentConfig(name="agent")
        agent = ConcreteAgent(config)
        chunks = []
        async for chunk in agent.stream("test"):
            chunks.append(chunk)
        assert len(chunks) == 2


class ConcreteWorkflow(BaseWorkflow):
    """Concrete implementation of BaseWorkflow for testing."""

    async def run(self, input_data, initial_state=None):
        self._state = initial_state or {}
        return {"output": "Workflow complete", "state": self._state}

    async def stream(self, input_data, initial_state=None):
        yield {"stage": "start"}
        yield {"stage": "end"}


class TestBaseWorkflow:
    """Tests for BaseWorkflow abstract class."""

    def test_init_sets_config(self):
        """Test init sets config."""
        config = WorkflowConfig(name="test_workflow")
        agent_config = AgentConfig(name="agent1")
        agent = ConcreteAgent(agent_config)
        workflow = ConcreteWorkflow(config, [agent])
        assert workflow.config == config

    def test_init_creates_agents_dict(self):
        """Test init creates agents dictionary by name."""
        config = WorkflowConfig(name="workflow")
        agent1_config = AgentConfig(name="researcher")
        agent2_config = AgentConfig(name="writer")
        agent1 = ConcreteAgent(agent1_config)
        agent2 = ConcreteAgent(agent2_config)

        workflow = ConcreteWorkflow(config, [agent1, agent2])
        assert "researcher" in workflow.agents
        assert "writer" in workflow.agents

    def test_init_empty_state(self):
        """Test init creates empty state."""
        config = WorkflowConfig(name="workflow")
        workflow = ConcreteWorkflow(config, [])
        assert workflow._state == {}

    def test_get_state_returns_copy(self):
        """Test get_state returns a copy."""
        config = WorkflowConfig(name="workflow")
        workflow = ConcreteWorkflow(config, [])
        workflow._state["key"] = "value"

        state = workflow.get_state()
        assert state["key"] == "value"
        assert state is not workflow._state

    def test_get_agent_existing(self):
        """Test getting existing agent by name."""
        config = WorkflowConfig(name="workflow")
        agent_config = AgentConfig(name="researcher")
        agent = ConcreteAgent(agent_config)
        workflow = ConcreteWorkflow(config, [agent])

        retrieved = workflow.get_agent("researcher")
        assert retrieved is agent

    def test_get_agent_nonexistent(self):
        """Test getting nonexistent agent returns None."""
        config = WorkflowConfig(name="workflow")
        workflow = ConcreteWorkflow(config, [])

        retrieved = workflow.get_agent("nonexistent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_run(self):
        """Test run method."""
        config = WorkflowConfig(name="workflow")
        workflow = ConcreteWorkflow(config, [])
        result = await workflow.run("input", {"key": "value"})
        assert result["output"] == "Workflow complete"
        assert result["state"]["key"] == "value"

    @pytest.mark.asyncio
    async def test_stream(self):
        """Test stream method."""
        config = WorkflowConfig(name="workflow")
        workflow = ConcreteWorkflow(config, [])
        stages = []
        async for update in workflow.stream("input"):
            stages.append(update)
        assert len(stages) == 2


class ConcreteAdapter(BaseAdapter):
    """Concrete implementation of BaseAdapter for testing."""

    @property
    def framework_name(self):
        return "test_framework"

    def is_available(self):
        return True

    def create_agent(self, config):
        return ConcreteAgent(config)

    def create_workflow(self, config, agents):
        return ConcreteWorkflow(config, agents)


class TestBaseAdapter:
    """Tests for BaseAdapter abstract class."""

    def test_framework_name(self):
        """Test framework_name property."""
        adapter = ConcreteAdapter()
        assert adapter.framework_name == "test_framework"

    def test_is_available(self):
        """Test is_available method."""
        adapter = ConcreteAdapter()
        assert adapter.is_available() is True

    def test_create_agent(self):
        """Test create_agent method."""
        adapter = ConcreteAdapter()
        config = AgentConfig(name="test_agent")
        agent = adapter.create_agent(config)
        assert isinstance(agent, BaseAgent)
        assert agent.name == "test_agent"

    def test_create_workflow(self):
        """Test create_workflow method."""
        adapter = ConcreteAdapter()
        workflow_config = WorkflowConfig(name="test_workflow")
        agent_config = AgentConfig(name="agent")
        agent = adapter.create_agent(agent_config)
        workflow = adapter.create_workflow(workflow_config, [agent])
        assert isinstance(workflow, BaseWorkflow)

    def test_create_tool_default(self):
        """Test create_tool default implementation."""
        adapter = ConcreteAdapter()

        def my_func(x):
            return x * 2

        tool = adapter.create_tool(
            name="double",
            description="Doubles input",
            func=my_func,
            args_schema={"x": "int"},
        )
        assert tool["name"] == "double"
        assert tool["description"] == "Doubles input"
        assert tool["func"] == my_func
        assert tool["args_schema"] == {"x": "int"}

    def test_get_model_for_tier_fallback_anthropic(self):
        """Test get_model_for_tier fallback for anthropic."""
        adapter = ConcreteAdapter()
        # Without ModelRouter, should fall back to defaults
        model = adapter.get_model_for_tier("cheap", "anthropic")
        assert "claude" in model.lower() or "haiku" in model.lower()

    def test_get_model_for_tier_fallback_openai(self):
        """Test get_model_for_tier fallback for openai."""
        adapter = ConcreteAdapter()
        model = adapter.get_model_for_tier("cheap", "openai")
        assert "gpt" in model.lower() or "mini" in model.lower()

    def test_get_model_for_tier_capable(self):
        """Test get_model_for_tier with capable tier."""
        adapter = ConcreteAdapter()
        model = adapter.get_model_for_tier("capable", "anthropic")
        assert "claude" in model.lower() or "sonnet" in model.lower()


class TestAgentConfigDefaults:
    """Tests for AgentConfig default factory fields."""

    def test_capabilities_default_is_new_list(self):
        """Test each config gets its own capabilities list."""
        config1 = AgentConfig(name="agent1")
        config2 = AgentConfig(name="agent2")
        config1.capabilities.append(AgentCapability.CODE_EXECUTION)
        assert AgentCapability.CODE_EXECUTION not in config2.capabilities

    def test_tools_default_is_new_list(self):
        """Test each config gets its own tools list."""
        config1 = AgentConfig(name="agent1")
        config2 = AgentConfig(name="agent2")
        config1.tools.append({"name": "tool1"})
        assert {"name": "tool1"} not in config2.tools

    def test_framework_options_default_is_new_dict(self):
        """Test each config gets its own framework_options dict."""
        config1 = AgentConfig(name="agent1")
        config2 = AgentConfig(name="agent2")
        config1.framework_options["key"] = "value"
        assert "key" not in config2.framework_options


class TestWorkflowConfigDefaults:
    """Tests for WorkflowConfig default factory fields."""

    def test_framework_options_default_is_new_dict(self):
        """Test each config gets its own framework_options dict."""
        config1 = WorkflowConfig(name="workflow1")
        config2 = WorkflowConfig(name="workflow2")
        config1.framework_options["key"] = "value"
        assert "key" not in config2.framework_options
