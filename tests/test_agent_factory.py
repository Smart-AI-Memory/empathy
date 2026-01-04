"""Tests for Agent Factory

Tests the universal agent factory's core functionality including:
- Framework detection and selection
- Agent creation across frameworks
- Workflow creation
- Tool creation
- CLI commands

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest


class TestFramework:
    """Test Framework enum and utilities."""

    def test_framework_from_string(self):
        """Test converting strings to Framework enum."""
        from empathy_llm_toolkit.agent_factory.framework import Framework

        assert Framework.from_string("native") == Framework.NATIVE
        assert Framework.from_string("langchain") == Framework.LANGCHAIN
        assert Framework.from_string("langgraph") == Framework.LANGGRAPH
        assert Framework.from_string("autogen") == Framework.AUTOGEN
        assert Framework.from_string("haystack") == Framework.HAYSTACK

        # Case insensitive
        assert Framework.from_string("LangChain") == Framework.LANGCHAIN
        assert Framework.from_string("LANGGRAPH") == Framework.LANGGRAPH

    def test_framework_from_string_invalid(self):
        """Test invalid framework string raises error."""
        from empathy_llm_toolkit.agent_factory.framework import Framework

        with pytest.raises(ValueError):
            Framework.from_string("invalid_framework")

    def test_detect_installed_frameworks(self):
        """Test framework detection includes native."""
        from empathy_llm_toolkit.agent_factory.framework import (
            Framework,
            detect_installed_frameworks,
        )

        installed = detect_installed_frameworks()
        assert Framework.NATIVE in installed

    def test_get_recommended_framework(self):
        """Test framework recommendations."""
        from empathy_llm_toolkit.agent_factory.framework import Framework, get_recommended_framework

        # Native should always be available as fallback
        rec = get_recommended_framework("general")
        assert rec in [Framework.NATIVE, Framework.LANGGRAPH, Framework.LANGCHAIN]

    def test_get_framework_info(self):
        """Test framework info retrieval."""
        from empathy_llm_toolkit.agent_factory.framework import Framework, get_framework_info

        info = get_framework_info(Framework.NATIVE)
        assert "name" in info
        assert "description" in info
        assert "best_for" in info
        assert info["name"] == "Empathy Native"


class TestAgentConfig:
    """Test AgentConfig dataclass."""

    def test_agent_config_defaults(self):
        """Test AgentConfig has sensible defaults."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, AgentRole

        config = AgentConfig(name="test")

        assert config.name == "test"
        assert config.role == AgentRole.CUSTOM
        assert config.model_tier == "capable"
        assert config.empathy_level == 4
        assert config.temperature == 0.7
        assert config.memory_enabled is True

    def test_agent_config_custom(self):
        """Test AgentConfig with custom values."""
        from empathy_llm_toolkit.agent_factory.base import AgentCapability, AgentConfig, AgentRole

        config = AgentConfig(
            name="researcher",
            role=AgentRole.RESEARCHER,
            model_tier="premium",
            empathy_level=5,
            capabilities=[AgentCapability.TOOL_USE, AgentCapability.WEB_SEARCH],
        )

        assert config.role == AgentRole.RESEARCHER
        assert config.model_tier == "premium"
        assert config.empathy_level == 5
        assert len(config.capabilities) == 2


class TestNativeAdapter:
    """Test the native Empathy adapter."""

    def test_native_adapter_available(self):
        """Test native adapter is always available."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter

        adapter = NativeAdapter()
        assert adapter.is_available() is True
        assert adapter.framework_name == "native"

    def test_native_adapter_create_agent(self):
        """Test creating an agent with native adapter."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, AgentRole

        adapter = NativeAdapter()
        config = AgentConfig(name="test", role=AgentRole.RESEARCHER)

        agent = adapter.create_agent(config)

        assert agent.name == "test"
        assert agent.role == AgentRole.RESEARCHER

    def test_native_adapter_create_workflow(self):
        """Test creating a workflow with native adapter."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, WorkflowConfig

        adapter = NativeAdapter()

        agent1 = adapter.create_agent(AgentConfig(name="agent1"))
        agent2 = adapter.create_agent(AgentConfig(name="agent2"))

        workflow_config = WorkflowConfig(name="test_workflow", mode="sequential")
        workflow = adapter.create_workflow(workflow_config, [agent1, agent2])

        assert workflow.config.name == "test_workflow"
        assert len(workflow.agents) == 2

    def test_native_adapter_create_tool(self):
        """Test creating a tool with native adapter."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter

        adapter = NativeAdapter()

        def my_func(x):
            return x * 2

        tool = adapter.create_tool(name="double", description="Double a number", func=my_func)

        assert tool["name"] == "double"
        assert tool["func"](5) == 10


class TestAgentFactory:
    """Test the main AgentFactory class."""

    def test_factory_creation_native(self):
        """Test creating factory with native framework."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        factory = AgentFactory(framework=Framework.NATIVE)

        assert factory.framework == Framework.NATIVE

    def test_factory_creation_string_framework(self):
        """Test creating factory with string framework."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        factory = AgentFactory(framework="native")

        assert factory.framework == Framework.NATIVE

    def test_factory_auto_framework(self):
        """Test factory auto-selects framework."""
        from empathy_llm_toolkit.agent_factory import AgentFactory

        factory = AgentFactory()  # Auto-detect

        assert factory.framework is not None

    def test_factory_create_agent(self):
        """Test creating agent through factory."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(name="test_agent", role="researcher", model_tier="capable")

        assert agent.name == "test_agent"
        assert factory.get_agent("test_agent") is agent

    def test_factory_create_workflow(self):
        """Test creating workflow through factory."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        factory = AgentFactory(framework=Framework.NATIVE)

        agent1 = factory.create_agent(name="a1")
        agent2 = factory.create_agent(name="a2")

        workflow = factory.create_workflow(
            name="test_workflow",
            agents=[agent1, agent2],
            mode="sequential",
        )

        assert workflow.config.name == "test_workflow"

    def test_factory_convenience_methods(self):
        """Test convenience methods for creating agents."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        factory = AgentFactory(framework=Framework.NATIVE)

        researcher = factory.create_researcher()
        assert researcher.role == AgentRole.RESEARCHER

        writer = factory.create_writer()
        assert writer.role == AgentRole.WRITER

        debugger = factory.create_debugger()
        assert debugger.role == AgentRole.DEBUGGER

    def test_factory_list_frameworks(self):
        """Test listing frameworks."""
        from empathy_llm_toolkit.agent_factory import AgentFactory

        frameworks = AgentFactory.list_frameworks()

        assert len(frameworks) >= 1
        assert any(f["framework"].value == "native" for f in frameworks)

    def test_factory_recommend_framework(self):
        """Test framework recommendations."""
        from empathy_llm_toolkit.agent_factory import AgentFactory

        rec = AgentFactory.recommend_framework("general")
        assert rec is not None


class TestNativeAgent:
    """Test NativeAgent functionality."""

    @pytest.mark.asyncio
    async def test_native_agent_invoke(self):
        """Test invoking native agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        adapter = NativeAdapter()
        agent = adapter.create_agent(AgentConfig(name="test"))

        result = await agent.invoke("Hello")

        assert "output" in result
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_native_agent_conversation_history(self):
        """Test agent tracks conversation history."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        adapter = NativeAdapter()
        agent = adapter.create_agent(AgentConfig(name="test"))

        await agent.invoke("First message")
        await agent.invoke("Second message")

        history = agent.get_conversation_history()
        assert len(history) == 4  # 2 user + 2 assistant

        agent.clear_history()
        assert len(agent.get_conversation_history()) == 0


class TestNativeWorkflow:
    """Test NativeWorkflow functionality."""

    @pytest.mark.asyncio
    async def test_native_workflow_sequential(self):
        """Test sequential workflow execution."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, WorkflowConfig

        adapter = NativeAdapter()

        agent1 = adapter.create_agent(AgentConfig(name="a1"))
        agent2 = adapter.create_agent(AgentConfig(name="a2"))

        workflow = adapter.create_workflow(
            WorkflowConfig(name="seq", mode="sequential"),
            [agent1, agent2],
        )

        result = await workflow.run("Start")

        assert "output" in result
        assert "results" in result
        assert len(result["results"]) == 2

    @pytest.mark.asyncio
    async def test_native_workflow_parallel(self):
        """Test parallel workflow execution."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, WorkflowConfig

        adapter = NativeAdapter()

        agent1 = adapter.create_agent(AgentConfig(name="a1"))
        agent2 = adapter.create_agent(AgentConfig(name="a2"))

        workflow = adapter.create_workflow(
            WorkflowConfig(name="par", mode="parallel"),
            [agent1, agent2],
        )

        result = await workflow.run("Input")

        assert "output" in result
        assert "results" in result


class TestCLIFrameworks:
    """Test CLI frameworks command."""

    def test_cli_frameworks_import(self):
        """Test frameworks CLI command can be imported."""
        from empathy_os.cli import cmd_frameworks

        assert callable(cmd_frameworks)

    def test_cli_frameworks_execution(self):
        """Test frameworks CLI command execution."""
        from empathy_os.cli import cmd_frameworks

        class MockArgs:
            all = False
            recommend = None
            json = False

        result = cmd_frameworks(MockArgs())
        assert result == 0

    def test_cli_frameworks_recommend(self):
        """Test frameworks recommendation."""
        from empathy_os.cli import cmd_frameworks

        class MockArgs:
            all = False
            recommend = "general"
            json = False

        result = cmd_frameworks(MockArgs())
        assert result == 0


class TestLangGraphAdapter:
    """Test LangGraph adapter if available."""

    def test_langgraph_available(self):
        """Test LangGraph availability check."""
        from empathy_llm_toolkit.agent_factory.adapters.langgraph_adapter import _check_langgraph

        # Just verify it returns a boolean
        result = _check_langgraph()
        assert isinstance(result, bool)

    def test_langgraph_create_agent(self):
        """Test creating agent with LangGraph if fully installed."""
        import os

        from empathy_llm_toolkit.agent_factory.adapters.langgraph_adapter import (
            LangGraphAdapter,
            _check_langgraph,
        )
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        if not _check_langgraph():
            pytest.skip("LangGraph not installed")

        # Also check if langchain_anthropic is available
        try:
            import langchain_anthropic  # noqa: F401
        except ImportError:
            pytest.skip("langchain_anthropic not installed")

        # Check for API key
        if not os.getenv("ANTHROPIC_API_KEY"):
            pytest.skip("ANTHROPIC_API_KEY not set")

        adapter = LangGraphAdapter()
        agent = adapter.create_agent(AgentConfig(name="test"))
        assert agent.name == "test"


class TestModelTierRouting:
    """Test model tier routing."""

    def test_get_model_for_tier(self):
        """Test model selection by tier."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter

        adapter = NativeAdapter()

        cheap = adapter.get_model_for_tier("cheap", "anthropic")
        assert "haiku" in cheap.lower()

        capable = adapter.get_model_for_tier("capable", "anthropic")
        assert "sonnet" in capable.lower()

        premium = adapter.get_model_for_tier("premium", "anthropic")
        assert "opus" in premium.lower()


class TestAgentRoles:
    """Test agent role handling."""

    def test_role_enum_values(self):
        """Test AgentRole enum has expected values."""
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        assert AgentRole.RESEARCHER.value == "researcher"
        assert AgentRole.WRITER.value == "writer"
        assert AgentRole.DEBUGGER.value == "debugger"
        assert AgentRole.COORDINATOR.value == "coordinator"

    def test_factory_role_string_conversion(self):
        """Test factory converts role strings."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(name="test", role="researcher")
        assert agent.role == AgentRole.RESEARCHER

        agent2 = factory.create_agent(name="test2", role="unknown_role")
        assert agent2.role == AgentRole.CUSTOM


class TestToolCreation:
    """Test tool creation across adapters."""

    def test_native_tool_creation(self):
        """Test tool creation with native adapter."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        factory = AgentFactory(framework=Framework.NATIVE)

        def calculator(x: int, y: int) -> int:
            return x + y

        tool = factory.create_tool(name="add", description="Add two numbers", func=calculator)

        assert tool["name"] == "add"
        assert tool["func"](2, 3) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
