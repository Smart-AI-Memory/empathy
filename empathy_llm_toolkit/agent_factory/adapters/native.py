"""
Native Empathy Adapter

Creates agents using Empathy's built-in EmpathyLLM system.
No external dependencies required.

Features:
- Full EmpathyLLM integration (levels 1-5)
- ModelRouter for cost optimization
- Pattern learning and memory
- Cost tracking

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


class NativeAgent(BaseAgent):
    """Agent using Empathy's native EmpathyLLM."""

    def __init__(self, config: AgentConfig, llm=None):
        super().__init__(config)
        self._llm = llm
        self._tools = {tool["name"]: tool for tool in config.tools if isinstance(tool, dict)}

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the agent."""
        # Format input
        if isinstance(input_data, str):
            user_input = input_data
        else:
            user_input = input_data.get("input", input_data.get("query", str(input_data)))

        # Handle empty input
        if not user_input or not user_input.strip():
            return {
                "output": "",
                "metadata": {
                    "level": self.config.empathy_level,
                    "model": self.model,
                    "skipped": True,
                },
            }

        # Build context
        ctx = context or {}
        ctx["agent_name"] = self.name
        ctx["agent_role"] = self.role.value

        # Add conversation history
        if self._conversation_history:
            ctx["conversation_history"] = self._conversation_history[-10:]

        # Use EmpathyLLM if available
        if self._llm:
            response = await self._llm.interact(
                user_id=f"agent_{self.name}", user_input=user_input, context=ctx
            )
            output = response.get("response", "")
            metadata = {
                "level": response.get("level", self.config.empathy_level),
                "model": response.get("model", self.model),
                "patterns_used": response.get("patterns_used", []),
            }
        else:
            # Fallback to simple response
            output = f"[{self.name}] I would process: {user_input}"
            metadata = {"level": self.config.empathy_level, "model": self.model}

        # Track conversation
        self._conversation_history.append({"role": "user", "content": user_input})
        self._conversation_history.append({"role": "assistant", "content": output})

        return {"output": output, "metadata": metadata}

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """Stream agent response."""
        # Native adapter doesn't support streaming yet, yield full response
        result = await self.invoke(input_data, context)
        yield result


class NativeWorkflow(BaseWorkflow):
    """Workflow using sequential/parallel agent execution."""

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the workflow."""
        self._state = initial_state or {}
        self._state["input"] = input_data

        mode = self.config.mode
        results = []

        if mode == "sequential":
            results = await self._run_sequential(input_data)
        elif mode == "parallel":
            results = await self._run_parallel(input_data)
        else:
            results = await self._run_sequential(input_data)

        self._state["results"] = results
        self._state["final_output"] = results[-1]["output"] if results else ""

        return {
            "output": self._state["final_output"],
            "results": results,
            "state": self._state,
            "agents_invoked": [r.get("agent") for r in results],
        }

    async def _run_sequential(self, input_data: str | dict) -> list[dict]:
        """Run agents sequentially, passing output to next."""
        results: list[dict] = []
        current_input = input_data

        for agent in self.agents.values():
            context = {"previous_results": results, "state": self._state}
            result = await agent.invoke(current_input, context)
            result["agent"] = agent.name
            results.append(result)
            current_input = result["output"]

        return results

    async def _run_parallel(self, input_data: str | dict) -> list:
        """Run all agents in parallel."""
        tasks = []
        for agent in self.agents.values():
            context = {"state": self._state}
            tasks.append(agent.invoke(input_data, context))

        results = await asyncio.gather(*tasks)

        # Add agent names
        for _i, (agent_name, result) in enumerate(zip(self.agents.keys(), results, strict=False)):
            result["agent"] = agent_name

        return list(results)

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """Stream workflow execution."""
        self._state = initial_state or {}
        self._state["input"] = input_data

        for agent in self.agents.values():
            context = {"state": self._state}
            yield {"event": "agent_start", "agent": agent.name}

            # agent.stream returns an async generator
            stream_gen = agent.stream(input_data, context)
            async for chunk in stream_gen:  # type: ignore[attr-defined]
                yield {"event": "agent_output", "agent": agent.name, "data": chunk}

            yield {"event": "agent_end", "agent": agent.name}


class NativeAdapter(BaseAdapter):
    """Adapter for Empathy's native agent system."""

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        """
        Initialize native adapter.

        Args:
            provider: LLM provider (anthropic, openai, local)
            api_key: API key (uses env var if not provided)
        """
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        )
        self._llm: Any = None  # EmpathyLLM instance or None

    @property
    def framework_name(self) -> str:
        return "native"

    def is_available(self) -> bool:
        """Native is always available."""
        return True

    def _get_llm(self, config: AgentConfig) -> Any:
        """Get or create EmpathyLLM instance."""
        if self._llm is None and self.api_key:
            try:
                from empathy_llm_toolkit.core import EmpathyLLM

                self._llm = EmpathyLLM(
                    provider=self.provider, api_key=self.api_key, target_level=config.empathy_level
                )
            except ImportError:
                pass
        return self._llm

    def create_agent(self, config: AgentConfig) -> NativeAgent:
        """Create a native Empathy agent."""
        llm = self._get_llm(config)
        return NativeAgent(config, llm=llm)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> NativeWorkflow:
        """Create a native workflow."""
        return NativeWorkflow(config, agents)

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> dict:
        """Create a tool dict for native agents."""
        return {"name": name, "description": description, "func": func, "args_schema": args_schema}
