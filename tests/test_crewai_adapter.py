"""Tests for CrewAI Adapter

Tests the CrewAI adapter for the Agent Factory.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest


class TestCrewAIAvailability:
    """Test CrewAI availability detection."""

    def test_crewai_check_function(self):
        """Test _check_crewai returns boolean."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import _check_crewai

        result = _check_crewai()
        assert isinstance(result, bool)

    def test_crewai_adapter_is_available(self):
        """Test CrewAI adapter availability check."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter

        adapter = CrewAIAdapter()
        # Should return True if crewai is installed, False otherwise
        result = adapter.is_available()
        assert isinstance(result, bool)

    def test_crewai_adapter_framework_name(self):
        """Test CrewAI adapter framework name."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter

        adapter = CrewAIAdapter()
        assert adapter.framework_name == "crewai"


class TestFrameworkEnumCrewAI:
    """Test Framework enum includes CrewAI."""

    def test_crewai_in_framework_enum(self):
        """Test CREWAI is in Framework enum."""
        from empathy_llm_toolkit.agent_factory.framework import Framework

        assert hasattr(Framework, "CREWAI")
        assert Framework.CREWAI.value == "crewai"

    def test_crewai_from_string(self):
        """Test converting 'crewai' string to Framework enum."""
        from empathy_llm_toolkit.agent_factory.framework import Framework

        assert Framework.from_string("crewai") == Framework.CREWAI
        assert Framework.from_string("crew_ai") == Framework.CREWAI
        assert Framework.from_string("crew") == Framework.CREWAI
        assert Framework.from_string("CrewAI") == Framework.CREWAI

    def test_crewai_framework_info(self):
        """Test get_framework_info includes CrewAI."""
        from empathy_llm_toolkit.agent_factory.framework import Framework, get_framework_info

        info = get_framework_info(Framework.CREWAI)
        assert info["name"] == "CrewAI"
        assert "best_for" in info
        assert "install_command" in info


class TestCrewAIRoleMapping:
    """Test CrewAI role mapping."""

    def test_role_mapping(self):
        """Test Empathy roles map to CrewAI role strings."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        adapter = CrewAIAdapter()

        assert adapter._map_role(AgentRole.RESEARCHER) == "Senior Researcher"
        assert adapter._map_role(AgentRole.WRITER) == "Content Writer"
        assert adapter._map_role(AgentRole.DEBUGGER) == "Software Debugger"
        assert adapter._map_role(AgentRole.COORDINATOR) == "Project Manager"
        assert adapter._map_role(AgentRole.CUSTOM) == "Specialist"

    def test_default_goal_generation(self):
        """Test default goal generation for roles."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        adapter = CrewAIAdapter()

        goal = adapter._default_goal(AgentRole.RESEARCHER)
        assert "research" in goal.lower()

        goal = adapter._default_goal(AgentRole.WRITER)
        assert "content" in goal.lower()

    def test_default_backstory_generation(self):
        """Test default backstory generation for roles."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentRole

        adapter = CrewAIAdapter()

        backstory = adapter._default_backstory(AgentRole.RESEARCHER)
        assert "researcher" in backstory.lower()

        backstory = adapter._default_backstory(AgentRole.SECURITY)
        assert "security" in backstory.lower()


class TestCrewAIAgentCreation:
    """Test CrewAI agent creation (requires crewai installed)."""

    def test_create_agent_requires_crewai(self):
        """Test create_agent raises ImportError if crewai not installed."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            _check_crewai,
        )
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        if _check_crewai():
            pytest.skip("CrewAI is installed, skipping ImportError test")

        adapter = CrewAIAdapter()

        with pytest.raises(ImportError):
            adapter.create_agent(AgentConfig(name="test"))

    def test_create_agent_with_crewai(self):
        """Test creating an agent when CrewAI is installed."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            CrewAIAgent,
            _check_crewai,
        )
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, AgentRole

        if not _check_crewai():
            pytest.skip("CrewAI not installed")

        adapter = CrewAIAdapter()
        config = AgentConfig(
            name="test_agent",
            role=AgentRole.RESEARCHER,
            description="Research AI trends",
        )

        agent = adapter.create_agent(config)

        assert isinstance(agent, CrewAIAgent)
        assert agent.name == "test_agent"
        assert agent.crewai_agent is not None


class TestCrewAIWorkflowCreation:
    """Test CrewAI workflow creation."""

    def test_create_workflow_requires_crewai(self):
        """Test create_workflow raises ImportError if crewai not installed."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            _check_crewai,
        )
        from empathy_llm_toolkit.agent_factory.base import WorkflowConfig

        if _check_crewai():
            pytest.skip("CrewAI is installed, skipping ImportError test")

        adapter = CrewAIAdapter()

        with pytest.raises(ImportError):
            adapter.create_workflow(WorkflowConfig(name="test"), [])

    def test_create_workflow_with_crewai(self):
        """Test creating a workflow when CrewAI is installed."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            CrewAIWorkflow,
            _check_crewai,
        )
        from empathy_llm_toolkit.agent_factory.base import AgentConfig, AgentRole, WorkflowConfig

        if not _check_crewai():
            pytest.skip("CrewAI not installed")

        adapter = CrewAIAdapter()

        agent1 = adapter.create_agent(AgentConfig(name="a1", role=AgentRole.RESEARCHER))
        agent2 = adapter.create_agent(AgentConfig(name="a2", role=AgentRole.WRITER))

        workflow = adapter.create_workflow(
            WorkflowConfig(name="test_workflow", mode="sequential"),
            [agent1, agent2],
        )

        assert isinstance(workflow, CrewAIWorkflow)
        assert len(workflow.agents) == 2


class TestFactoryCrewAIIntegration:
    """Test AgentFactory integration with CrewAI."""

    def test_factory_creates_crewai_adapter(self):
        """Test factory creates CrewAI adapter when specified."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            _check_crewai,
        )

        if not _check_crewai():
            pytest.skip("CrewAI not installed")

        factory = AgentFactory(framework=Framework.CREWAI)

        assert factory.framework == Framework.CREWAI
        assert isinstance(factory.adapter, CrewAIAdapter)

    def test_factory_with_crewai_string(self):
        """Test factory accepts 'crewai' string."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import _check_crewai

        if not _check_crewai():
            pytest.skip("CrewAI not installed")

        factory = AgentFactory(framework="crewai")

        assert factory.framework == Framework.CREWAI

    def test_list_frameworks_includes_crewai(self):
        """Test list_frameworks includes CrewAI when installed."""
        from empathy_llm_toolkit.agent_factory import AgentFactory
        from empathy_llm_toolkit.agent_factory.framework import Framework

        frameworks = AgentFactory.list_frameworks(installed_only=False)

        crewai_info = next(
            (f for f in frameworks if f["framework"] == Framework.CREWAI),
            None,
        )
        assert crewai_info is not None
        assert crewai_info["name"] == "CrewAI"


class TestCrewAIAgentInvoke:
    """Test CrewAI agent invocation."""

    @pytest.mark.asyncio
    async def test_crewai_agent_invoke_without_agent(self):
        """Test invoke returns error when no CrewAI agent configured."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAgent
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        agent = CrewAIAgent(AgentConfig(name="test"), crewai_agent=None)

        result = await agent.invoke("Test input")

        assert "output" in result
        assert "No CrewAI agent configured" in result["output"]

    @pytest.mark.asyncio
    async def test_crewai_agent_stream(self):
        """Test CrewAI agent streaming."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAgent
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        agent = CrewAIAgent(AgentConfig(name="test"), crewai_agent=None)

        chunks = []
        async for chunk in agent.stream("Test input"):
            chunks.append(chunk)

        assert len(chunks) == 1  # Single chunk for non-configured agent


class TestCrewAIWorkflowRun:
    """Test CrewAI workflow execution."""

    @pytest.mark.asyncio
    async def test_workflow_run_without_crew(self):
        """Test workflow run returns error when no Crew configured."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIWorkflow
        from empathy_llm_toolkit.agent_factory.base import WorkflowConfig

        workflow = CrewAIWorkflow(WorkflowConfig(name="test"), [], crew=None)

        result = await workflow.run("Test input")

        assert "No CrewAI Crew configured" in result["output"]
        assert "error" in result


class TestCrewAIToolCreation:
    """Test CrewAI tool creation."""

    def test_create_tool_fallback(self):
        """Test tool creation fallback when CrewAI not available."""
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import (
            CrewAIAdapter,
            _check_crewai,
        )

        adapter = CrewAIAdapter()

        def my_func(x):
            return x * 2

        tool = adapter.create_tool(
            name="double",
            description="Double a number",
            func=my_func,
        )

        # If CrewAI not available, returns dict format
        if not _check_crewai():
            assert isinstance(tool, dict)
            assert tool["name"] == "double"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
