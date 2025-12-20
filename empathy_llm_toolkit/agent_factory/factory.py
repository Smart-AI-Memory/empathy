"""
Universal Agent Factory

The main entry point for creating agents and workflows across any
supported framework while retaining Empathy's core features.

Usage:
    from empathy_llm_toolkit.agent_factory import AgentFactory, Framework

    # Create factory
    factory = AgentFactory(framework=Framework.LANGGRAPH)

    # Create agents
    researcher = factory.create_agent(
        name="researcher",
        role="researcher",
        model_tier="capable"
    )

    writer = factory.create_agent(
        name="writer",
        role="writer",
        model_tier="premium"
    )

    # Create workflow
    pipeline = factory.create_workflow(
        name="research_pipeline",
        agents=[researcher, writer],
        mode="sequential"
    )

    # Run
    result = await pipeline.run("Research AI trends")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from collections.abc import Callable
from typing import Any

from empathy_llm_toolkit.agent_factory.base import (
    AgentCapability,
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)
from empathy_llm_toolkit.agent_factory.framework import (
    Framework,
    detect_installed_frameworks,
    get_framework_info,
    get_recommended_framework,
)


class AgentFactory:
    """
    Universal factory for creating agents and workflows.

    Supports multiple frameworks (LangChain, LangGraph, AutoGen, Haystack, Native)
    while providing a unified interface and integrating with Empathy's
    cost optimization, pattern learning, and memory features.
    """

    def __init__(
        self,
        framework: Framework | str | None = None,
        provider: str = "anthropic",
        api_key: str | None = None,
        use_case: str = "general",
    ):
        """
        Initialize the Agent Factory.

        Args:
            framework: Framework to use (auto-detected if not specified)
            provider: LLM provider (anthropic, openai, local)
            api_key: API key (uses env var if not provided)
            use_case: Use case for framework recommendation (general, rag, multi_agent, etc.)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        )

        # Resolve framework
        if framework is None:
            self.framework = get_recommended_framework(use_case)
        elif isinstance(framework, str):
            self.framework = Framework.from_string(framework)
        else:
            self.framework = framework

        # Get adapter
        self._adapter = self._get_adapter()

        # Track created agents for reuse
        self._agents: dict[str, BaseAgent] = {}

    def _get_adapter(self) -> BaseAdapter:
        """Get the appropriate adapter for the selected framework."""
        from empathy_llm_toolkit.agent_factory.adapters import (
            NativeAdapter,
            get_autogen_adapter,
            get_haystack_adapter,
            get_langchain_adapter,
            get_langgraph_adapter,
        )

        if self.framework == Framework.NATIVE:
            return NativeAdapter(self.provider, self.api_key)

        elif self.framework == Framework.LANGCHAIN:
            adapter_class = get_langchain_adapter()
            return adapter_class(self.provider, self.api_key)  # type: ignore[no-any-return]

        elif self.framework == Framework.LANGGRAPH:
            adapter_class = get_langgraph_adapter()
            return adapter_class(self.provider, self.api_key)  # type: ignore[no-any-return]

        elif self.framework == Framework.AUTOGEN:
            adapter_class = get_autogen_adapter()
            return adapter_class(self.provider, self.api_key)  # type: ignore[no-any-return]

        elif self.framework == Framework.HAYSTACK:
            adapter_class = get_haystack_adapter()
            return adapter_class(self.provider, self.api_key)  # type: ignore[no-any-return]

        else:
            # Fallback to native
            return NativeAdapter(self.provider, self.api_key)

    @property
    def adapter(self) -> BaseAdapter:
        """Get the current adapter."""
        return self._adapter

    def create_agent(
        self,
        name: str,
        role: AgentRole | str = AgentRole.CUSTOM,
        description: str = "",
        model_tier: str = "capable",
        model_override: str | None = None,
        capabilities: list[AgentCapability] | None = None,
        tools: list[Any] | None = None,
        system_prompt: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        empathy_level: int = 4,
        use_patterns: bool = True,
        track_costs: bool = True,
        memory_enabled: bool = True,
        memory_type: str = "conversation",
        framework_options: dict | None = None,
    ) -> BaseAgent:
        """
        Create an agent using the configured framework.

        Args:
            name: Unique agent name
            role: Agent role (researcher, writer, debugger, etc.)
            description: Agent description
            model_tier: Model tier (cheap, capable, premium)
            model_override: Specific model ID to use
            capabilities: Agent capabilities (tool_use, code_execution, etc.)
            tools: Tools for the agent
            system_prompt: Custom system prompt
            temperature: LLM temperature
            max_tokens: Max tokens for response
            empathy_level: Empathy level (1-5)
            use_patterns: Use learned patterns from Empathy
            track_costs: Track API costs
            memory_enabled: Enable conversation memory
            memory_type: Type of memory (conversation, summary, vector)
            framework_options: Framework-specific options

        Returns:
            Agent implementing BaseAgent interface
        """
        # Parse role
        if isinstance(role, str):
            try:
                role = AgentRole(role.lower())
            except ValueError:
                role = AgentRole.CUSTOM

        # Build config
        config = AgentConfig(
            name=name,
            role=role,
            description=description,
            model_tier=model_tier,
            model_override=model_override,
            capabilities=capabilities or [],
            tools=tools or [],
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            empathy_level=empathy_level,
            use_patterns=use_patterns,
            track_costs=track_costs,
            memory_enabled=memory_enabled,
            memory_type=memory_type,
            framework_options=framework_options or {},
        )

        # Create agent
        agent = self._adapter.create_agent(config)

        # Track for reuse
        self._agents[name] = agent

        return agent

    def create_workflow(
        self,
        name: str,
        agents: list[BaseAgent],
        description: str = "",
        mode: str = "sequential",
        max_iterations: int = 10,
        timeout_seconds: int = 300,
        state_schema: dict | None = None,
        checkpointing: bool = True,
        retry_on_error: bool = True,
        max_retries: int = 3,
        framework_options: dict | None = None,
    ) -> BaseWorkflow:
        """
        Create a workflow/pipeline from agents.

        Args:
            name: Workflow name
            agents: List of agents to include
            description: Workflow description
            mode: Execution mode (sequential, parallel, graph, conversation)
            max_iterations: Max iterations for loops
            timeout_seconds: Timeout in seconds
            state_schema: Schema for workflow state
            checkpointing: Enable state checkpointing
            retry_on_error: Retry failed steps
            max_retries: Max retry attempts
            framework_options: Framework-specific options

        Returns:
            Workflow implementing BaseWorkflow interface
        """
        config = WorkflowConfig(
            name=name,
            description=description,
            mode=mode,
            max_iterations=max_iterations,
            timeout_seconds=timeout_seconds,
            state_schema=state_schema,
            checkpointing=checkpointing,
            retry_on_error=retry_on_error,
            max_retries=max_retries,
            framework_options=framework_options or {},
        )

        return self._adapter.create_workflow(config, agents)

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> Any:
        """
        Create a tool in the framework's format.

        Args:
            name: Tool name
            description: Tool description
            func: Function to execute
            args_schema: Optional JSON schema for arguments

        Returns:
            Tool in the framework's native format
        """
        return self._adapter.create_tool(name, description, func, args_schema)

    def get_agent(self, name: str) -> BaseAgent | None:
        """Get a previously created agent by name."""
        return self._agents.get(name)

    def list_agents(self) -> list[str]:
        """List all created agent names."""
        return list(self._agents.keys())

    @classmethod
    def list_frameworks(cls, installed_only: bool = True) -> list[dict]:
        """
        List available frameworks.

        Args:
            installed_only: Only show installed frameworks

        Returns:
            List of framework info dicts
        """
        all_frameworks = [
            Framework.NATIVE,
            Framework.LANGCHAIN,
            Framework.LANGGRAPH,
            Framework.AUTOGEN,
            Framework.HAYSTACK,
        ]

        if installed_only:
            installed = detect_installed_frameworks()
            frameworks = [f for f in all_frameworks if f in installed]
        else:
            frameworks = all_frameworks

        return [
            {
                "framework": f,
                "installed": f in detect_installed_frameworks(),
                **get_framework_info(f),
            }
            for f in frameworks
        ]

    @classmethod
    def recommend_framework(cls, use_case: str = "general") -> Framework:
        """
        Get recommended framework for a use case.

        Args:
            use_case: general, rag, multi_agent, code_analysis, workflow, conversational

        Returns:
            Recommended framework
        """
        return get_recommended_framework(use_case)

    def switch_framework(self, framework: Framework | str) -> None:
        """
        Switch to a different framework.

        Note: Existing agents won't be migrated.

        Args:
            framework: New framework to use
        """
        if isinstance(framework, str):
            framework = Framework.from_string(framework)

        self.framework = framework
        self._adapter = self._get_adapter()
        self._agents.clear()

    # =========================================================================
    # Convenience methods for common agent patterns
    # =========================================================================

    def create_researcher(
        self, name: str = "researcher", model_tier: str = "capable", **kwargs
    ) -> BaseAgent:
        """Create a researcher agent."""
        return self.create_agent(
            name=name,
            role=AgentRole.RESEARCHER,
            description="Researches and gathers information thoroughly.",
            model_tier=model_tier,
            **kwargs,
        )

    def create_writer(
        self, name: str = "writer", model_tier: str = "premium", **kwargs
    ) -> BaseAgent:
        """Create a writer agent."""
        return self.create_agent(
            name=name,
            role=AgentRole.WRITER,
            description="Creates clear, engaging content.",
            model_tier=model_tier,
            **kwargs,
        )

    def create_reviewer(
        self, name: str = "reviewer", model_tier: str = "capable", **kwargs
    ) -> BaseAgent:
        """Create a reviewer agent."""
        return self.create_agent(
            name=name,
            role=AgentRole.REVIEWER,
            description="Reviews work and provides constructive feedback.",
            model_tier=model_tier,
            **kwargs,
        )

    def create_debugger(
        self, name: str = "debugger", model_tier: str = "capable", **kwargs
    ) -> BaseAgent:
        """Create a debugger agent."""
        return self.create_agent(
            name=name,
            role=AgentRole.DEBUGGER,
            description="Analyzes code issues and finds bugs.",
            model_tier=model_tier,
            capabilities=[AgentCapability.CODE_EXECUTION],
            **kwargs,
        )

    def create_coordinator(
        self, name: str = "coordinator", model_tier: str = "premium", **kwargs
    ) -> BaseAgent:
        """Create a coordinator agent."""
        return self.create_agent(
            name=name,
            role=AgentRole.COORDINATOR,
            description="Coordinates other agents and synthesizes results.",
            model_tier=model_tier,
            **kwargs,
        )

    # =========================================================================
    # Pipeline creation helpers
    # =========================================================================

    def create_research_pipeline(
        self, topic: str = "", include_reviewer: bool = True
    ) -> BaseWorkflow:
        """
        Create a research → write → review pipeline.

        Args:
            topic: Research topic (used in prompts)
            include_reviewer: Include a reviewer agent

        Returns:
            Workflow ready to run
        """
        agents = [
            self.create_researcher(
                system_prompt=f"Research thoroughly about: {topic}" if topic else None
            ),
            self.create_writer(),
        ]

        if include_reviewer:
            agents.append(self.create_reviewer())

        return self.create_workflow(name="research_pipeline", agents=agents, mode="sequential")

    def create_code_review_pipeline(self) -> BaseWorkflow:
        """Create a code review pipeline."""
        agents = [
            self.create_agent(
                name="analyzer",
                role=AgentRole.SECURITY,
                model_tier="capable",
                system_prompt="Analyze code for security issues.",
            ),
            self.create_debugger(system_prompt="Look for potential bugs and issues."),
            self.create_reviewer(system_prompt="Review code quality and suggest improvements."),
        ]

        return self.create_workflow(name="code_review_pipeline", agents=agents, mode="sequential")
