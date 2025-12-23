"""
Framework Adapters for Agent Factory

Each adapter implements the BaseAdapter interface for a specific
agent framework, allowing seamless switching between frameworks.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from empathy_llm_toolkit.agent_factory.adapters.native import NativeAdapter
from empathy_llm_toolkit.agent_factory.adapters.wizard_adapter import (
    WizardAdapter,
    WizardAgent,
    wrap_wizard,
)

# Lazy imports for optional frameworks
_langchain_adapter = None
_langgraph_adapter = None
_autogen_adapter = None
_haystack_adapter = None
_crewai_adapter = None


def get_langchain_adapter():
    """Get LangChain adapter (lazy import)."""
    global _langchain_adapter
    if _langchain_adapter is None:
        from empathy_llm_toolkit.agent_factory.adapters.langchain_adapter import LangChainAdapter

        _langchain_adapter = LangChainAdapter
    return _langchain_adapter


def get_langgraph_adapter():
    """Get LangGraph adapter (lazy import)."""
    global _langgraph_adapter
    if _langgraph_adapter is None:
        from empathy_llm_toolkit.agent_factory.adapters.langgraph_adapter import LangGraphAdapter

        _langgraph_adapter = LangGraphAdapter
    return _langgraph_adapter


def get_autogen_adapter():
    """Get AutoGen adapter (lazy import)."""
    global _autogen_adapter
    if _autogen_adapter is None:
        from empathy_llm_toolkit.agent_factory.adapters.autogen_adapter import AutoGenAdapter

        _autogen_adapter = AutoGenAdapter
    return _autogen_adapter


def get_haystack_adapter():
    """Get Haystack adapter (lazy import)."""
    global _haystack_adapter
    if _haystack_adapter is None:
        from empathy_llm_toolkit.agent_factory.adapters.haystack_adapter import HaystackAdapter

        _haystack_adapter = HaystackAdapter
    return _haystack_adapter


def get_crewai_adapter():
    """Get CrewAI adapter (lazy import)."""
    global _crewai_adapter
    if _crewai_adapter is None:
        from empathy_llm_toolkit.agent_factory.adapters.crewai_adapter import CrewAIAdapter

        _crewai_adapter = CrewAIAdapter
    return _crewai_adapter


__all__ = [
    "NativeAdapter",
    "WizardAdapter",
    "WizardAgent",
    "wrap_wizard",
    "get_langchain_adapter",
    "get_langgraph_adapter",
    "get_autogen_adapter",
    "get_haystack_adapter",
    "get_crewai_adapter",
]
