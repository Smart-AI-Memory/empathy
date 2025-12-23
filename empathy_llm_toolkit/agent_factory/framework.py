"""
Framework Enumeration and Detection

Defines supported agent frameworks and provides utilities for
detecting installed frameworks and selecting defaults.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from enum import Enum


class Framework(Enum):
    """Supported agent frameworks."""

    # Empathy native (no external deps)
    NATIVE = "native"

    # LangChain ecosystem
    LANGCHAIN = "langchain"
    LANGGRAPH = "langgraph"

    # Microsoft AutoGen
    AUTOGEN = "autogen"

    # deepset Haystack
    HAYSTACK = "haystack"

    # CrewAI
    CREWAI = "crewai"

    @classmethod
    def from_string(cls, name: str) -> "Framework":
        """Convert string to Framework enum."""
        name_lower = name.lower().strip()
        mapping = {
            "native": cls.NATIVE,
            "empathy": cls.NATIVE,
            "langchain": cls.LANGCHAIN,
            "langgraph": cls.LANGGRAPH,
            "lang_graph": cls.LANGGRAPH,
            "autogen": cls.AUTOGEN,
            "auto_gen": cls.AUTOGEN,
            "haystack": cls.HAYSTACK,
            "crewai": cls.CREWAI,
            "crew_ai": cls.CREWAI,
            "crew": cls.CREWAI,
        }
        if name_lower in mapping:
            return mapping[name_lower]
        raise ValueError(f"Unknown framework: {name}. Available: {list(mapping.keys())}")


def detect_installed_frameworks() -> list[Framework]:
    """
    Detect which agent frameworks are installed.

    Returns:
        List of installed frameworks (native is always included)
    """
    installed = [Framework.NATIVE]

    # Check LangChain
    try:
        import langchain  # noqa: F401

        installed.append(Framework.LANGCHAIN)
    except ImportError:
        pass

    # Check LangGraph
    try:
        import langgraph  # noqa: F401

        installed.append(Framework.LANGGRAPH)
    except ImportError:
        pass

    # Check AutoGen
    try:
        import autogen  # noqa: F401

        installed.append(Framework.AUTOGEN)
    except ImportError:
        pass

    # Check Haystack
    try:
        import haystack  # noqa: F401

        installed.append(Framework.HAYSTACK)
    except ImportError:
        pass

    # Check CrewAI
    try:
        import crewai  # noqa: F401

        installed.append(Framework.CREWAI)
    except ImportError:
        pass

    return installed


def get_recommended_framework(use_case: str = "general") -> Framework:
    """
    Get recommended framework for a use case.

    Args:
        use_case: One of "general", "rag", "multi_agent", "code_analysis", "workflow"

    Returns:
        Recommended framework based on installed packages and use case
    """
    installed = detect_installed_frameworks()

    recommendations = {
        "general": [Framework.LANGGRAPH, Framework.LANGCHAIN, Framework.NATIVE],
        "rag": [Framework.HAYSTACK, Framework.LANGCHAIN, Framework.NATIVE],
        "multi_agent": [Framework.AUTOGEN, Framework.LANGGRAPH, Framework.NATIVE],
        "code_analysis": [Framework.LANGGRAPH, Framework.LANGCHAIN, Framework.NATIVE],
        "workflow": [Framework.LANGGRAPH, Framework.LANGCHAIN, Framework.NATIVE],
        "conversational": [Framework.AUTOGEN, Framework.LANGCHAIN, Framework.NATIVE],
    }

    preferred = recommendations.get(use_case, recommendations["general"])

    for framework in preferred:
        if framework in installed:
            return framework

    return Framework.NATIVE


def get_framework_info(framework: Framework) -> dict[str, object]:
    """
    Get information about a framework.

    Returns:
        Dict with name, description, best_for, install_command
    """
    info: dict[Framework, dict[str, object]] = {
        Framework.NATIVE: {
            "name": "Empathy Native",
            "description": "Built-in agent system with EmpathyLLM integration",
            "best_for": ["Simple agents", "Cost optimization", "Pattern learning"],
            "install_command": None,
            "docs_url": "https://smartaimemory.com/docs/agents",
        },
        Framework.LANGCHAIN: {
            "name": "LangChain",
            "description": "Composable chains with tools, memory, and retrieval",
            "best_for": ["Tool usage", "RAG", "Chains", "Prompt templates"],
            "install_command": "pip install langchain langchain-anthropic",
            "docs_url": "https://python.langchain.com/docs/",
        },
        Framework.LANGGRAPH: {
            "name": "LangGraph",
            "description": "Stateful, multi-actor workflows with cycles",
            "best_for": ["Complex workflows", "Stateful agents", "Multi-step reasoning"],
            "install_command": "pip install langgraph langchain-anthropic",
            "docs_url": "https://langchain-ai.github.io/langgraph/",
        },
        Framework.AUTOGEN: {
            "name": "AutoGen",
            "description": "Multi-agent conversational systems",
            "best_for": ["Agent teams", "Conversations", "Code execution"],
            "install_command": "pip install pyautogen",
            "docs_url": "https://microsoft.github.io/autogen/",
        },
        Framework.HAYSTACK: {
            "name": "Haystack",
            "description": "Production-ready RAG and NLP pipelines",
            "best_for": ["Document QA", "RAG", "Search", "NLP pipelines"],
            "install_command": "pip install haystack-ai",
            "docs_url": "https://docs.haystack.deepset.ai/",
        },
        Framework.CREWAI: {
            "name": "CrewAI",
            "description": "Role-based multi-agent framework with goal-oriented crews",
            "best_for": [
                "Agent teams",
                "Role-playing",
                "Task delegation",
                "Hierarchical workflows",
            ],
            "install_command": "pip install crewai",
            "docs_url": "https://docs.crewai.com/",
        },
    }
    return info.get(framework, info[Framework.NATIVE])
