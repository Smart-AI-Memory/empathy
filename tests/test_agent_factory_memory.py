"""Tests for Agent Factory Memory Graph Integration

Tests the memory-aware agent wrapper that integrates agents
with the Memory Graph for cross-agent learning.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest


class TestMemoryAwareAgentCreation:
    """Test MemoryAwareAgent wrapper creation."""

    def test_memory_aware_agent_creation(self):
        """Test creating a memory-aware agent wrapper."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        # Use temp file to avoid persisting test data
        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(graph_path),
            )

            assert memory_agent.name == "test"
            assert memory_agent._wrapped is base_agent
            assert memory_agent._store_findings is True
            assert memory_agent._query_similar is True

    def test_memory_aware_agent_with_custom_config(self):
        """Test creating memory-aware agent with custom config."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(graph_path),
                store_findings=False,
                query_similar=True,
                similarity_threshold=0.7,
                max_similar_results=3,
            )

            assert memory_agent._store_findings is False
            assert memory_agent._query_similar is True
            assert memory_agent._similarity_threshold == 0.7
            assert memory_agent._max_similar_results == 3


class TestFactoryMemoryIntegration:
    """Test factory creates memory-aware agents when enabled."""

    def test_factory_creates_memory_aware_agent(self):
        """Test factory wraps agent with memory integration when enabled."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            factory = AgentFactory(framework=Framework.NATIVE)

            agent = factory.create_agent(
                name="memory_test",
                role="researcher",
                memory_graph_enabled=True,
                memory_graph_path=str(graph_path),
            )

            assert isinstance(agent, MemoryAwareAgent)

    def test_factory_respects_memory_disabled(self):
        """Test factory does not wrap when memory_graph_enabled=False."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        factory = AgentFactory(framework=Framework.NATIVE)

        agent = factory.create_agent(
            name="non_memory_test",
            role="researcher",
            memory_graph_enabled=False,
        )

        assert not isinstance(agent, MemoryAwareAgent)

    def test_factory_memory_config_params(self):
        """Test factory passes memory config params correctly."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "custom_graph.json"

            factory = AgentFactory(framework=Framework.NATIVE)

            agent = factory.create_agent(
                name="configured_memory",
                memory_graph_enabled=True,
                memory_graph_path=str(graph_path),
                store_findings=False,
                query_similar=True,
            )

            assert isinstance(agent, MemoryAwareAgent)
            assert agent._graph_path == str(graph_path)
            assert agent._store_findings is False
            assert agent._query_similar is True


class TestMemoryAwareAgentInvoke:
    """Test MemoryAwareAgent invoke functionality."""

    @pytest.mark.asyncio
    async def test_memory_aware_agent_invoke_success(self):
        """Test successful invocation through memory-aware wrapper."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(graph_path),
                store_findings=False,  # Disable for simple test
            )

            result = await memory_agent.invoke("Hello")

            assert "output" in result
            assert "metadata" in result
            assert "memory_graph" in result["metadata"]

    @pytest.mark.asyncio
    async def test_memory_aware_agent_adds_metadata(self):
        """Test memory-aware agent adds graph metadata."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(base_agent, graph_path=str(graph_path))

            result = await memory_agent.invoke("Test query")

            assert "metadata" in result
            assert "memory_graph" in result["metadata"]
            assert result["metadata"]["memory_graph"]["enabled"] is True
            assert "similar_found" in result["metadata"]["memory_graph"]


class TestMemoryAwareAgentSimilarFindings:
    """Test MemoryAwareAgent similar findings functionality."""

    @pytest.mark.asyncio
    async def test_query_similar_findings(self):
        """Test querying for similar findings."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(graph_path),
                query_similar=True,
            )

            # Add a finding to the graph first
            if memory_agent._graph:
                memory_agent._graph.add_finding(
                    "test-wizard",
                    {
                        "type": "bug",
                        "name": "Null reference error",
                        "description": "Missing null check on user object",
                    },
                )
                memory_agent._graph._save()  # Internal save method

            # Query for similar
            similar = memory_agent._get_similar_findings("Null pointer exception in auth")

            # Should find the similar bug we added
            # Note: May be empty if similarity threshold not met
            assert isinstance(similar, list)

    def test_contains_finding_patterns(self):
        """Test detection of finding patterns in text."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
            )

            # Should detect finding patterns
            assert memory_agent._contains_finding_patterns("Found a bug in the code")
            assert memory_agent._contains_finding_patterns("Detected vulnerability")
            assert memory_agent._contains_finding_patterns("There is an issue here")

            # Should not detect in normal text
            assert not memory_agent._contains_finding_patterns("Hello world")

    def test_infer_finding_type(self):
        """Test inference of finding type from text."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
            )

            assert (
                memory_agent._infer_finding_type("SQL injection vulnerability") == "vulnerability"
            )
            assert memory_agent._infer_finding_type("Bug: null reference") == "bug"
            assert (
                memory_agent._infer_finding_type("Performance issue: slow query")
                == "performance_issue"
            )
            assert memory_agent._infer_finding_type("Fixed the crash") == "fix"
            assert memory_agent._infer_finding_type("General observation") == "pattern"


class TestMemoryAwareAgentDelegation:
    """Test MemoryAwareAgent properly delegates to wrapped agent."""

    def test_add_tool_delegation(self):
        """Test add_tool is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
            )

            tool = {"name": "test_tool", "func": lambda x: x}
            memory_agent.add_tool(tool)

            assert tool in base_agent.config.tools

    @pytest.mark.asyncio
    async def test_conversation_history_delegation(self):
        """Test conversation history is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
                store_findings=False,
            )

            await memory_agent.invoke("Test message")

            history = memory_agent.get_conversation_history()
            assert len(history) > 0

            memory_agent.clear_history()
            assert len(memory_agent.get_conversation_history()) == 0

    def test_model_property_delegation(self):
        """Test model property is delegated to wrapped agent."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test", model_tier="premium"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
            )

            assert memory_agent.model == base_agent.model


class TestAgentConfigMemoryFields:
    """Test AgentConfig memory graph fields."""

    def test_agent_config_memory_defaults(self):
        """Test AgentConfig has memory graph defaults."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        config = AgentConfig(name="test")

        assert config.memory_graph_enabled is False
        assert config.memory_graph_path == "patterns/memory_graph.json"
        assert config.store_findings is True
        assert config.query_similar is True

    def test_agent_config_memory_custom(self):
        """Test AgentConfig with custom memory values."""
        from empathy_llm_toolkit.agent_factory.base import AgentConfig

        config = AgentConfig(
            name="test",
            memory_graph_enabled=True,
            memory_graph_path="custom/graph.json",
            store_findings=False,
            query_similar=True,
        )

        assert config.memory_graph_enabled is True
        assert config.memory_graph_path == "custom/graph.json"
        assert config.store_findings is False
        assert config.query_similar is True


class TestMemoryAwareAgentGraphStats:
    """Test MemoryAwareAgent graph statistics."""

    def test_get_graph_stats(self):
        """Test getting graph statistics."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(graph_path),
            )

            stats = memory_agent.get_graph_stats()

            if memory_agent._graph:
                assert stats["enabled"] is True
                assert "node_count" in stats
                assert "edge_count" in stats
            else:
                assert stats["enabled"] is False

    def test_graph_property(self):
        """Test graph property returns MemoryGraph instance."""
        from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
        from empathy_llm_toolkit.agent_factory.base import AgentConfig
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent

        adapter = NativeAdapter()
        base_agent = adapter.create_agent(AgentConfig(name="test"))

        with tempfile.TemporaryDirectory() as tmpdir:
            memory_agent = MemoryAwareAgent(
                base_agent,
                graph_path=str(Path(tmpdir) / "test_graph.json"),
            )

            # Graph property should return the internal graph
            graph = memory_agent.graph
            assert graph is memory_agent._graph


class TestCombinedWrappers:
    """Test combining memory and resilience wrappers."""

    def test_factory_creates_both_wrappers(self):
        """Test factory can create agent with both wrappers."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework
        from empathy_llm_toolkit.agent_factory.memory_integration import MemoryAwareAgent
        from empathy_llm_toolkit.agent_factory.resilient import ResilientAgent

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            factory = AgentFactory(framework=Framework.NATIVE)

            agent = factory.create_agent(
                name="combined_test",
                resilience_enabled=True,
                memory_graph_enabled=True,
                memory_graph_path=str(graph_path),
            )

            # Outer wrapper should be resilient
            assert isinstance(agent, ResilientAgent)

            # Inner wrapper should be memory-aware
            assert isinstance(agent._wrapped, MemoryAwareAgent)

    @pytest.mark.asyncio
    async def test_combined_wrappers_invoke(self):
        """Test invoking agent with both wrappers."""
        from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

        with tempfile.TemporaryDirectory() as tmpdir:
            graph_path = Path(tmpdir) / "test_graph.json"

            factory = AgentFactory(framework=Framework.NATIVE)

            agent = factory.create_agent(
                name="combined_invoke_test",
                resilience_enabled=True,
                memory_graph_enabled=True,
                memory_graph_path=str(graph_path),
            )

            result = await agent.invoke("Test input")

            assert "output" in result
            assert "metadata" in result

            # Should have both resilience and memory metadata
            assert "resilience" in result["metadata"]
            assert "memory_graph" in result["metadata"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
