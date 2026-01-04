"""Empathy Framework - Universal Agent Factory

Create agents using your preferred framework while retaining Empathy's
cost optimization, pattern learning, and memory features.

Supported Frameworks:
- LangChain: Chains, tools, and retrieval
- LangGraph: Stateful multi-agent graphs
- AutoGen: Conversational multi-agent systems
- Haystack: RAG and document pipelines
- Native: Empathy's built-in agent system

Usage:
    from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

    # Create factory with preferred framework
    factory = AgentFactory(framework=Framework.LANGGRAPH)

    # Create agents
    researcher = factory.create_agent("researcher", tools=[...])
    writer = factory.create_agent("writer", model_tier="premium")

    # Create workflows
    pipeline = factory.create_workflow([researcher, writer])

    # Create wizards with framework backing
    debug_wizard = factory.create_wizard("debugging")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_llm_toolkit.agent_factory.base import (
    AgentCapability,
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    WorkflowConfig,
)
from empathy_llm_toolkit.agent_factory.factory import AgentFactory
from empathy_llm_toolkit.agent_factory.framework import Framework

__all__ = [
    "AgentCapability",
    "AgentConfig",
    "AgentFactory",
    "AgentRole",
    "BaseAdapter",
    "BaseAgent",
    "Framework",
    "WorkflowConfig",
]
