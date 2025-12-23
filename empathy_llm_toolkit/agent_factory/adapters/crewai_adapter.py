"""
CrewAI Adapter

Creates agents using CrewAI's role/goal/backstory pattern while integrating
with Empathy's cost optimization and pattern learning.

CrewAI is a multi-agent framework focusing on:
- Role-based agents with goals and backstories
- Hierarchical and sequential crew orchestration
- Task delegation and collaboration

Requires: pip install crewai

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import os
from collections.abc import Callable
from typing import Any

from empathy_llm_toolkit.agent_factory.base import (
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)

# Lazy imports for CrewAI
_crewai_available = None


def _check_crewai():
    """Check if CrewAI is available."""
    global _crewai_available
    if _crewai_available is None:
        try:
            import crewai  # noqa: F401

            _crewai_available = True
        except ImportError:
            _crewai_available = False
    return _crewai_available


class CrewAIAgent(BaseAgent):
    """Agent wrapping a CrewAI Agent."""

    def __init__(self, config: AgentConfig, crewai_agent=None):
        """
        Initialize CrewAI agent wrapper.

        Args:
            config: Agent configuration
            crewai_agent: The underlying CrewAI Agent instance
        """
        super().__init__(config)
        self._crewai_agent = crewai_agent

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """
        Invoke the CrewAI agent.

        CrewAI agents work within crews/tasks, so we create a temporary
        task for standalone invocation.
        """
        if not self._crewai_agent:
            return {"output": "No CrewAI agent configured", "metadata": {}}

        try:
            from crewai import Task

            # Format input as task description
            if isinstance(input_data, str):
                description = input_data
            else:
                description = input_data.get("task", input_data.get("input", str(input_data)))

            # Add context to description if provided
            if context:
                context_str = "\n".join(f"{k}: {v}" for k, v in context.items())
                description = f"{description}\n\nContext:\n{context_str}"

            # Create and execute task
            task = Task(
                description=description,
                expected_output="A comprehensive response addressing the task.",
                agent=self._crewai_agent,
            )

            # CrewAI is primarily sync, so run in executor
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._execute_task, task)

            output = str(result) if result else "Task completed"

            # Track conversation
            self._conversation_history.append({"role": "user", "content": description})
            self._conversation_history.append({"role": "assistant", "content": output})

            return {
                "output": output,
                "metadata": {
                    "model": self.model,
                    "framework": "crewai",
                    "agent_role": self._crewai_agent.role if self._crewai_agent else None,
                },
            }

        except Exception as e:
            return {
                "output": f"Error: {str(e)}",
                "metadata": {"error": str(e), "framework": "crewai"},
            }

    def _execute_task(self, task):
        """Execute a CrewAI task synchronously."""
        try:
            # In newer versions of CrewAI, tasks are executed via Crew
            # For standalone execution, we use the agent's execute_task method
            if hasattr(task, "execute"):
                return task.execute()
            elif hasattr(self._crewai_agent, "execute_task"):
                return self._crewai_agent.execute_task(task)
            else:
                # Fallback: create minimal crew
                from crewai import Crew

                crew = Crew(agents=[self._crewai_agent], tasks=[task], verbose=False)
                return crew.kickoff()
        except Exception as e:
            return f"Task execution error: {e}"

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """
        Stream CrewAI response.

        Note: CrewAI doesn't natively support streaming, so we simulate
        by yielding the complete response.
        """
        result = await self.invoke(input_data, context)
        yield result

    @property
    def crewai_agent(self):
        """Get the underlying CrewAI agent."""
        return self._crewai_agent


class CrewAIWorkflow(BaseWorkflow):
    """Workflow using CrewAI's Crew orchestration."""

    def __init__(self, config: WorkflowConfig, agents: list[BaseAgent], crew=None):
        """
        Initialize CrewAI workflow.

        Args:
            config: Workflow configuration
            agents: List of CrewAIAgent instances
            crew: Optional pre-built CrewAI Crew instance
        """
        super().__init__(config, agents)
        self._crew = crew
        self._tasks = []

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the CrewAI crew workflow."""
        self._state = initial_state or {}

        if not self._crew:
            return {"output": "No CrewAI Crew configured", "error": "Missing crew"}

        try:
            # Format input
            if isinstance(input_data, str):
                inputs = {"input": input_data}
            else:
                inputs = dict(input_data)

            # Add state to inputs
            inputs.update(self._state)

            # Run crew in executor (CrewAI is sync)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._crew.kickoff, inputs)

            output = str(result) if result else "Crew completed"

            return {
                "output": output,
                "results": [{"crew_result": str(result)}],
                "state": self._state,
                "metadata": {"framework": "crewai"},
            }

        except Exception as e:
            return {
                "output": f"Crew execution error: {e}",
                "error": str(e),
                "state": self._state,
            }

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """
        Stream workflow execution.

        Note: CrewAI doesn't support streaming, so we yield progress updates.
        """
        yield {"event": "crew_start", "crew": self.config.name}

        result = await self.run(input_data, initial_state)

        yield {"event": "crew_end", "result": result}

    def add_task(self, description: str, expected_output: str, agent_name: str) -> None:
        """
        Add a task to the workflow.

        Args:
            description: Task description
            expected_output: Expected output description
            agent_name: Name of agent to assign task to
        """
        if not _check_crewai():
            return

        from crewai import Task

        agent = self.agents.get(agent_name)
        if agent and hasattr(agent, "crewai_agent"):
            task = Task(
                description=description,
                expected_output=expected_output,
                agent=agent.crewai_agent,
            )
            self._tasks.append(task)


class CrewAIAdapter(BaseAdapter):
    """Adapter for CrewAI framework."""

    def __init__(self, provider: str = "openai", api_key: str | None = None):
        """
        Initialize CrewAI adapter.

        Args:
            provider: LLM provider (openai is default for CrewAI)
            api_key: API key (uses env var if not provided)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        )

    @property
    def framework_name(self) -> str:
        return "crewai"

    def is_available(self) -> bool:
        """Check if CrewAI is installed."""
        return bool(_check_crewai())

    def create_agent(self, config: AgentConfig) -> CrewAIAgent:
        """Create a CrewAI-based agent."""
        if not self.is_available():
            raise ImportError("CrewAI not installed. Run: pip install crewai")

        from crewai import Agent

        # Map Empathy role to CrewAI role string
        role = self._map_role(config.role)

        # Generate goal based on role and description
        goal = config.description or self._default_goal(config.role)

        # Generate backstory from system prompt or role
        backstory = config.system_prompt or self._default_backstory(config.role)

        # Convert tools to CrewAI format
        crewai_tools = [self._convert_tool(t) for t in config.tools if t]
        crewai_tools = [t for t in crewai_tools if t is not None]

        # Create CrewAI agent
        crewai_agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=crewai_tools if crewai_tools else None,
            verbose=False,
            allow_delegation=config.role == AgentRole.COORDINATOR,
        )

        return CrewAIAgent(config, crewai_agent)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> CrewAIWorkflow:
        """Create a CrewAI Crew workflow."""
        if not self.is_available():
            raise ImportError("CrewAI not installed")

        from crewai import Crew, Process

        # Determine process type from workflow mode
        if config.mode == "hierarchical":
            process = Process.hierarchical
        else:
            process = Process.sequential

        # Extract CrewAI agents from wrappers
        crewai_agents = []
        for agent in agents:
            if isinstance(agent, CrewAIAgent) and agent.crewai_agent:
                crewai_agents.append(agent.crewai_agent)

        if not crewai_agents:
            return CrewAIWorkflow(config, agents)

        # Create Crew
        crew = Crew(
            agents=crewai_agents,
            tasks=[],  # Tasks will be added dynamically or via add_task
            process=process,
            verbose=False,
        )

        return CrewAIWorkflow(config, agents, crew)

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> Any:
        """Create a CrewAI tool."""
        if not self.is_available():
            return super().create_tool(name, description, func, args_schema)

        try:
            from crewai.tools import BaseTool

            # Create dynamic tool class
            class DynamicTool(BaseTool):
                name: str = name
                description: str = description

                def _run(self, **kwargs) -> str:
                    return str(func(**kwargs))

            return DynamicTool()
        except ImportError:
            # Fallback to dict format
            return {"name": name, "description": description, "func": func}

    def _convert_tool(self, tool: Any) -> Any:
        """Convert a tool to CrewAI format."""
        if not self.is_available():
            return None

        # If already a CrewAI tool, return as-is
        try:
            from crewai.tools import BaseTool

            if isinstance(tool, BaseTool):
                return tool
        except ImportError:
            pass

        # If dict, convert to CrewAI tool
        if isinstance(tool, dict):
            return self.create_tool(
                name=tool.get("name", "tool"),
                description=tool.get("description", ""),
                func=tool.get("func", lambda: None),
                args_schema=tool.get("args_schema"),
            )

        return None

    def _map_role(self, role: AgentRole) -> str:
        """Map Empathy AgentRole to CrewAI role string."""
        role_map = {
            AgentRole.COORDINATOR: "Project Manager",
            AgentRole.RESEARCHER: "Senior Researcher",
            AgentRole.WRITER: "Content Writer",
            AgentRole.REVIEWER: "Quality Reviewer",
            AgentRole.EDITOR: "Editor",
            AgentRole.EXECUTOR: "Task Executor",
            AgentRole.DEBUGGER: "Software Debugger",
            AgentRole.SECURITY: "Security Analyst",
            AgentRole.ARCHITECT: "Software Architect",
            AgentRole.TESTER: "QA Tester",
            AgentRole.DOCUMENTER: "Technical Writer",
            AgentRole.RETRIEVER: "Information Retriever",
            AgentRole.SUMMARIZER: "Content Summarizer",
            AgentRole.ANSWERER: "Question Answerer",
            AgentRole.CUSTOM: "Specialist",
        }
        return role_map.get(role, "Specialist")

    def _default_goal(self, role: AgentRole) -> str:
        """Generate default goal based on role."""
        goal_map = {
            AgentRole.COORDINATOR: "Coordinate team efforts and ensure project success",
            AgentRole.RESEARCHER: "Conduct thorough research and gather comprehensive information",
            AgentRole.WRITER: "Create clear, engaging, and high-quality content",
            AgentRole.REVIEWER: "Provide constructive feedback and ensure quality standards",
            AgentRole.EDITOR: "Refine and improve content for clarity and impact",
            AgentRole.EXECUTOR: "Execute tasks efficiently and report results accurately",
            AgentRole.DEBUGGER: "Identify and resolve software bugs systematically",
            AgentRole.SECURITY: "Analyze systems for security vulnerabilities",
            AgentRole.ARCHITECT: "Design robust and scalable system architectures",
            AgentRole.TESTER: "Create comprehensive tests and ensure software quality",
            AgentRole.DOCUMENTER: "Create clear and comprehensive documentation",
            AgentRole.RETRIEVER: "Retrieve relevant information from knowledge bases",
            AgentRole.SUMMARIZER: "Create concise and accurate summaries",
            AgentRole.ANSWERER: "Provide accurate answers to questions",
            AgentRole.CUSTOM: "Complete assigned tasks with excellence",
        }
        return goal_map.get(role, "Complete assigned tasks with excellence")

    def _default_backstory(self, role: AgentRole) -> str:
        """Generate default backstory based on role."""
        backstory_map = {
            AgentRole.COORDINATOR: (
                "You are an experienced project manager with a track record of "
                "successfully coordinating complex projects and diverse teams."
            ),
            AgentRole.RESEARCHER: (
                "You are a meticulous researcher with expertise in finding "
                "reliable information and synthesizing complex topics."
            ),
            AgentRole.WRITER: (
                "You are a skilled writer with years of experience crafting "
                "compelling narratives and clear technical content."
            ),
            AgentRole.REVIEWER: (
                "You are a seasoned reviewer known for your attention to detail "
                "and constructive feedback that improves quality."
            ),
            AgentRole.DEBUGGER: (
                "You are an expert debugger with deep knowledge of software systems "
                "and a systematic approach to problem-solving."
            ),
            AgentRole.SECURITY: (
                "You are a security analyst with expertise in identifying "
                "vulnerabilities and recommending protective measures."
            ),
            AgentRole.ARCHITECT: (
                "You are a software architect with experience designing "
                "scalable, maintainable systems for enterprise applications."
            ),
        }
        return backstory_map.get(
            role,
            f"You are an experienced professional excelling as a {role.value}.",
        )
