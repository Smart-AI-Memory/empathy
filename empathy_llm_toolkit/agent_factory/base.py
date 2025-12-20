"""
Base Classes for Agent Factory

Defines the common interfaces that all framework adapters must implement.
These abstractions allow seamless switching between LangChain, LangGraph,
AutoGen, Haystack, and native Empathy agents.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AgentRole(Enum):
    """Standard agent roles for multi-agent systems."""

    # Core roles
    COORDINATOR = "coordinator"  # Orchestrates other agents
    RESEARCHER = "researcher"  # Gathers information
    WRITER = "writer"  # Produces content
    REVIEWER = "reviewer"  # Reviews/critiques
    EDITOR = "editor"  # Refines content
    EXECUTOR = "executor"  # Runs code/commands

    # Specialized roles
    DEBUGGER = "debugger"  # Finds and fixes bugs
    SECURITY = "security"  # Security analysis
    ARCHITECT = "architect"  # System design
    TESTER = "tester"  # Creates tests
    DOCUMENTER = "documenter"  # Documentation

    # RAG roles
    RETRIEVER = "retriever"  # Document retrieval
    SUMMARIZER = "summarizer"  # Summarization
    ANSWERER = "answerer"  # Question answering

    # Custom
    CUSTOM = "custom"


class AgentCapability(Enum):
    """Capabilities an agent can have."""

    CODE_EXECUTION = "code_execution"
    TOOL_USE = "tool_use"
    WEB_SEARCH = "web_search"
    FILE_ACCESS = "file_access"
    MEMORY = "memory"
    RETRIEVAL = "retrieval"
    VISION = "vision"
    FUNCTION_CALLING = "function_calling"


@dataclass
class AgentConfig:
    """Configuration for creating an agent."""

    # Identity
    name: str
    role: AgentRole = AgentRole.CUSTOM
    description: str = ""

    # Model selection
    model_tier: str = "capable"  # cheap, capable, premium
    model_override: str | None = None  # Specific model ID

    # Capabilities
    capabilities: list[AgentCapability] = field(default_factory=list)
    tools: list[Any] = field(default_factory=list)

    # Behavior
    system_prompt: str | None = None
    temperature: float = 0.7
    max_tokens: int = 4096

    # Empathy integration
    empathy_level: int = 4  # 1-5
    use_patterns: bool = True  # Load learned patterns
    track_costs: bool = True  # Track API costs

    # Memory
    memory_enabled: bool = True
    memory_type: str = "conversation"  # conversation, summary, vector

    # Framework-specific options
    framework_options: dict = field(default_factory=dict)


@dataclass
class WorkflowConfig:
    """Configuration for creating a workflow/graph."""

    name: str
    description: str = ""

    # Execution mode
    mode: str = "sequential"  # sequential, parallel, graph, conversation
    max_iterations: int = 10
    timeout_seconds: int = 300

    # State management
    state_schema: dict | None = None
    checkpointing: bool = True

    # Error handling
    retry_on_error: bool = True
    max_retries: int = 3

    # Framework-specific options
    framework_options: dict = field(default_factory=dict)


class BaseAgent(ABC):
    """
    Abstract base class for framework-agnostic agents.

    All framework adapters create agents that implement this interface,
    allowing seamless switching between frameworks.
    """

    def __init__(self, config: AgentConfig):
        self.config = config
        self.name = config.name
        self.role = config.role
        self._conversation_history: list[dict] = []

    @abstractmethod
    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """
        Invoke the agent with input.

        Args:
            input_data: User input or structured data
            context: Optional context (previous results, shared state)

        Returns:
            Dict with at least {"output": str, "metadata": dict}
        """
        pass

    @abstractmethod
    async def stream(self, input_data: str | dict, context: dict | None = None):
        """
        Stream agent response.

        Yields chunks of the response as they're generated.
        """
        pass

    def add_tool(self, tool: Any) -> None:
        """Add a tool to the agent."""
        self.config.tools.append(tool)

    def get_conversation_history(self) -> list[dict]:
        """Get conversation history."""
        return self._conversation_history.copy()

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._conversation_history.clear()

    @property
    def model(self) -> str:
        """Get the model being used."""
        return self.config.model_override or f"tier:{self.config.model_tier}"


class BaseWorkflow(ABC):
    """
    Abstract base class for framework-agnostic workflows.

    Workflows orchestrate multiple agents to complete complex tasks.
    """

    def __init__(self, config: WorkflowConfig, agents: list[BaseAgent]):
        self.config = config
        self.agents = {agent.name: agent for agent in agents}
        self._state: dict = {}

    @abstractmethod
    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """
        Run the workflow.

        Args:
            input_data: Initial input
            initial_state: Optional initial state

        Returns:
            Dict with final output and execution metadata
        """
        pass

    @abstractmethod
    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """
        Stream workflow execution.

        Yields updates as agents complete their work.
        """
        pass

    def get_state(self) -> dict:
        """Get current workflow state."""
        return self._state.copy()

    def get_agent(self, name: str) -> BaseAgent | None:
        """Get agent by name."""
        return self.agents.get(name)


class BaseAdapter(ABC):
    """
    Abstract base class for framework adapters.

    Each framework (LangChain, LangGraph, AutoGen, Haystack) implements
    an adapter that creates agents and workflows using that framework's
    native primitives while exposing a common interface.
    """

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Name of the framework this adapter supports."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the framework is installed and available."""
        pass

    @abstractmethod
    def create_agent(self, config: AgentConfig) -> BaseAgent:
        """
        Create an agent using this framework.

        Args:
            config: Agent configuration

        Returns:
            Agent implementing BaseAgent interface
        """
        pass

    @abstractmethod
    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> BaseWorkflow:
        """
        Create a workflow using this framework.

        Args:
            config: Workflow configuration
            agents: List of agents to include

        Returns:
            Workflow implementing BaseWorkflow interface
        """
        pass

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> Any:
        """
        Create a tool for agents in this framework's format.

        Default implementation returns a dict; override for framework-specific.
        """
        return {"name": name, "description": description, "func": func, "args_schema": args_schema}

    def get_model_for_tier(self, tier: str, provider: str = "anthropic") -> str:
        """
        Get the model ID for a given tier.

        Uses Empathy's ModelRouter if available, otherwise defaults.
        """
        try:
            from empathy_llm_toolkit.routing import ModelRouter

            router = ModelRouter()
            # Map tier to a task type
            task_map = {
                "cheap": "summarize",
                "capable": "generate_code",
                "premium": "architectural_decision",
            }
            task = task_map.get(tier, "generate_code")
            return router.route(task, provider)
        except ImportError:
            # Fallback defaults
            defaults = {
                "anthropic": {
                    "cheap": "claude-3-haiku-20240307",
                    "capable": "claude-sonnet-4-20250514",
                    "premium": "claude-opus-4-20250514",
                },
                "openai": {"cheap": "gpt-4o-mini", "capable": "gpt-4o", "premium": "o1"},
            }
            return defaults.get(provider, defaults["anthropic"]).get(
                tier, "claude-sonnet-4-20250514"
            )
