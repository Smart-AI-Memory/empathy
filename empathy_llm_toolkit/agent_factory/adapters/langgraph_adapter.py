"""
LangGraph Adapter

Creates stateful multi-agent workflows using LangGraph's graph primitives.
Best for complex workflows with cycles, conditional routing, and state management.

Requires: pip install langgraph langchain-anthropic

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import os
from collections.abc import Callable
from typing import Any

from empathy_llm_toolkit.agent_factory.base import (
    AgentConfig,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)

# Lazy imports
_langgraph_available = None


def _check_langgraph():
    """Check if LangGraph is available."""
    global _langgraph_available
    if _langgraph_available is None:
        try:
            import langgraph  # noqa: F401

            _langgraph_available = True
        except ImportError:
            _langgraph_available = False
    return _langgraph_available


class LangGraphAgent(BaseAgent):
    """Agent wrapping a LangGraph node/runnable."""

    def __init__(self, config: AgentConfig, runnable=None, node_func=None):
        super().__init__(config)
        self._runnable = runnable
        self._node_func = node_func

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the agent."""
        # Format as state dict
        if isinstance(input_data, str):
            state = {"messages": [{"role": "user", "content": input_data}]}
        elif isinstance(input_data, dict):
            state = input_data.copy()
        else:
            state = {"input": input_data}

        # Merge context into state
        if context:
            state.update(context)

        try:
            if self._runnable:
                if hasattr(self._runnable, "ainvoke"):
                    result = await self._runnable.ainvoke(state)
                else:
                    result = self._runnable.invoke(state)
            elif self._node_func:
                result = (
                    await self._node_func(state)
                    if asyncio.iscoroutinefunction(self._node_func)
                    else self._node_func(state)
                )
            else:
                result = {"output": f"[{self.name}] No runnable configured"}

            # Extract output from messages or output key
            if isinstance(result, dict):
                if "messages" in result and result["messages"]:
                    output = result["messages"][-1].get("content", str(result["messages"][-1]))
                else:
                    output = result.get("output", str(result))
            else:
                output = str(result)

            self._conversation_history.append({"role": "user", "content": str(input_data)})
            self._conversation_history.append({"role": "assistant", "content": output})

            return {
                "output": output,
                "state": result if isinstance(result, dict) else {},
                "metadata": {"framework": "langgraph", "model": self.model},
            }

        except Exception as e:
            return {"output": f"Error: {e}", "metadata": {"error": str(e)}}

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """Stream agent response."""
        if self._runnable and hasattr(self._runnable, "astream"):
            state = (
                {"messages": [{"role": "user", "content": input_data}]}
                if isinstance(input_data, str)
                else input_data
            )
            async for chunk in self._runnable.astream(state):
                yield chunk
        else:
            result = await self.invoke(input_data, context)
            yield result


class LangGraphWorkflow(BaseWorkflow):
    """Workflow using LangGraph's StateGraph."""

    def __init__(self, config: WorkflowConfig, agents: list[BaseAgent], graph=None):
        super().__init__(config, agents)
        self._graph = graph
        self._compiled = None

    def _compile_graph(self):
        """Compile the graph if not already compiled."""
        if self._compiled is None and self._graph:
            self._compiled = self._graph.compile()
        return self._compiled

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the LangGraph workflow."""
        compiled = self._compile_graph()

        # Prepare input state
        if isinstance(input_data, str):
            state = {"messages": [{"role": "user", "content": input_data}]}
        else:
            state = input_data.copy()

        if initial_state:
            state.update(initial_state)

        self._state = state

        try:
            if compiled:
                if hasattr(compiled, "ainvoke"):
                    result = await compiled.ainvoke(state)
                else:
                    result = compiled.invoke(state)
            else:
                # Fallback to sequential
                result = await self._run_sequential(input_data)

            # Extract output
            if isinstance(result, dict):
                if "messages" in result and result["messages"]:
                    output = result["messages"][-1].get("content", "")
                else:
                    output = result.get("output", str(result))
                self._state = result
            else:
                output = str(result)

            return {"output": output, "state": self._state, "metadata": {"framework": "langgraph"}}

        except Exception as e:
            return {"output": f"Error: {e}", "error": str(e)}

    async def _run_sequential(self, input_data: str | dict) -> dict:
        """Fallback sequential execution."""
        current = input_data
        for agent in self.agents.values():
            result = await agent.invoke(current)
            current = result.get("output", result)
        return {"output": current, "messages": []}

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """Stream workflow execution."""
        compiled = self._compile_graph()

        if isinstance(input_data, str):
            state = {"messages": [{"role": "user", "content": input_data}]}
        else:
            state = input_data.copy()

        if compiled and hasattr(compiled, "astream"):
            async for event in compiled.astream(state):
                yield event
        else:
            result = await self.run(input_data, initial_state)
            yield result


class LangGraphAdapter(BaseAdapter):
    """Adapter for LangGraph framework."""

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        )

    @property
    def framework_name(self) -> str:
        return "langgraph"

    def is_available(self) -> bool:
        return bool(_check_langgraph())

    def _get_llm(self, config: AgentConfig) -> Any:
        """Get LangChain LLM for use in LangGraph."""
        model_id = config.model_override or self.get_model_for_tier(
            config.model_tier, self.provider
        )

        if self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            # LangChain API varies between versions - use type: ignore for flexibility
            return ChatAnthropic(
                model=model_id,  # type: ignore[call-arg]
                api_key=self.api_key,  # type: ignore[arg-type]
                temperature=config.temperature,
                max_tokens_to_sample=config.max_tokens,  # Anthropic uses max_tokens_to_sample
            )
        elif self.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model_id,
                api_key=self.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    def create_agent(self, config: AgentConfig) -> LangGraphAgent:
        """Create a LangGraph-compatible agent."""
        if not self.is_available():
            raise ImportError("LangGraph not installed. Run: pip install langgraph")

        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        llm = self._get_llm(config)

        # Build prompt
        system = config.system_prompt or f"You are a {config.role.value} agent."
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        # Create runnable
        chain = prompt | llm

        return LangGraphAgent(config, runnable=chain)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> LangGraphWorkflow:
        """Create a LangGraph StateGraph workflow."""
        if not self.is_available():
            raise ImportError("LangGraph not installed")

        from langgraph.graph import END, StateGraph
        from typing_extensions import TypedDict

        # Define state schema
        class WorkflowState(TypedDict):
            messages: list
            current_agent: str
            iteration: int

        # Build graph
        graph = StateGraph(WorkflowState)

        # Add agent nodes
        for agent in agents:

            async def agent_node(state, a=agent):
                result = await a.invoke(state)
                messages = state.get("messages", [])
                messages.append({"role": "assistant", "content": result["output"], "agent": a.name})
                return {"messages": messages, "current_agent": a.name}

            graph.add_node(agent.name, agent_node)

        # Build edges based on mode
        agent_names = [a.name for a in agents]

        if config.mode == "sequential":
            # Linear chain: agent1 -> agent2 -> ... -> END
            graph.set_entry_point(agent_names[0])
            for i in range(len(agent_names) - 1):
                graph.add_edge(agent_names[i], agent_names[i + 1])
            graph.add_edge(agent_names[-1], END)

        elif config.mode == "parallel":
            # All agents run, then merge at END
            # (LangGraph doesn't natively support parallel, so we use fan-out)
            graph.set_entry_point(agent_names[0])
            for name in agent_names:
                graph.add_edge(name, END)

        else:
            # Default: sequential
            graph.set_entry_point(agent_names[0])
            for i in range(len(agent_names) - 1):
                graph.add_edge(agent_names[i], agent_names[i + 1])
            graph.add_edge(agent_names[-1], END)

        return LangGraphWorkflow(config, agents, graph=graph)

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> Any:
        """Create a tool (same as LangChain)."""
        if not self.is_available():
            return {"name": name, "description": description, "func": func}

        from langchain_core.tools import StructuredTool

        return StructuredTool.from_function(func=func, name=name, description=description)
