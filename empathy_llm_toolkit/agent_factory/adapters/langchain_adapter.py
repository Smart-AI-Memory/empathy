"""LangChain Adapter

Creates agents using LangChain's primitives while integrating
with Empathy's cost optimization and pattern learning.

Requires: pip install langchain langchain-anthropic langchain-openai

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from collections.abc import Callable
from typing import Any

from empathy_llm_toolkit.agent_factory.base import (
    AgentCapability,
    AgentConfig,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)

# Lazy imports for LangChain
_langchain_available = None


def _check_langchain():
    """Check if LangChain is available."""
    global _langchain_available
    if _langchain_available is None:
        try:
            import langchain  # noqa: F401

            _langchain_available = True
        except ImportError:
            _langchain_available = False
    return _langchain_available


class LangChainAgent(BaseAgent):
    """Agent wrapping a LangChain chain or agent."""

    def __init__(self, config: AgentConfig, chain=None, agent_executor=None):
        super().__init__(config)
        self._chain = chain
        self._agent_executor = agent_executor
        self._runnable = agent_executor or chain

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the LangChain agent/chain."""
        if not self._runnable:
            return {"output": "No LangChain runnable configured", "metadata": {}}

        # Format input
        invoke_input: dict[str, Any] = {}
        if isinstance(input_data, str):
            invoke_input = {"input": input_data}
        else:
            invoke_input = dict(input_data)

        # Add context
        if context:
            invoke_input["context"] = context

        # Add conversation history if memory enabled
        if self.config.memory_enabled and self._conversation_history:
            invoke_input["chat_history"] = self._conversation_history[-10:]

        try:
            # Use ainvoke for async
            if hasattr(self._runnable, "ainvoke"):
                result = await self._runnable.ainvoke(invoke_input)
            else:
                # Fallback to sync
                result = self._runnable.invoke(invoke_input)

            # Extract output
            if isinstance(result, dict):
                output = result.get("output", result.get("answer", str(result)))
            else:
                output = str(result)

            # Track conversation
            user_msg = invoke_input.get("input", str(input_data))
            self._conversation_history.append({"role": "user", "content": user_msg})
            self._conversation_history.append({"role": "assistant", "content": output})

            return {
                "output": output,
                "metadata": {
                    "model": self.model,
                    "framework": "langchain",
                    "raw_result": result if isinstance(result, dict) else None,
                },
            }

        except Exception as e:
            return {
                "output": f"Error: {e!s}",
                "metadata": {"error": str(e), "framework": "langchain"},
            }

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """Stream LangChain response."""
        if not self._runnable:
            yield {"output": "No LangChain runnable configured", "metadata": {}}
            return

        # Format input
        if isinstance(input_data, str):
            invoke_input = {"input": input_data}
        else:
            invoke_input = input_data

        try:
            if hasattr(self._runnable, "astream"):
                async for chunk in self._runnable.astream(invoke_input):
                    if isinstance(chunk, dict):
                        yield chunk
                    else:
                        yield {"chunk": str(chunk)}
            else:
                # Fallback to non-streaming
                result = await self.invoke(input_data, context)
                yield result
        except Exception as e:
            yield {"error": str(e)}


class LangChainWorkflow(BaseWorkflow):
    """Workflow using LangChain's SequentialChain or custom routing."""

    def __init__(self, config: WorkflowConfig, agents: list[BaseAgent], chain=None):
        super().__init__(config, agents)
        self._chain = chain

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the LangChain workflow."""
        self._state = initial_state or {}

        if self._chain:
            # Use the composed chain
            try:
                if hasattr(self._chain, "ainvoke"):
                    result = await self._chain.ainvoke(input_data)
                else:
                    result = self._chain.invoke(input_data)

                output = (
                    result.get("output", str(result)) if isinstance(result, dict) else str(result)
                )
                return {"output": output, "results": [result], "state": self._state}
            except Exception as e:
                return {"output": f"Error: {e}", "error": str(e)}
        else:
            # Fallback to sequential agent execution
            results = []
            current_input = input_data

            for agent in self.agents.values():
                result = await agent.invoke(current_input, {"state": self._state})
                result["agent"] = agent.name
                results.append(result)
                current_input = result["output"]

            return {
                "output": results[-1]["output"] if results else "",
                "results": results,
                "state": self._state,
            }

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """Stream workflow execution."""
        for agent in self.agents.values():
            yield {"event": "agent_start", "agent": agent.name}
            stream_gen = agent.stream(input_data)
            async for chunk in stream_gen:  # type: ignore[attr-defined]
                yield {"event": "chunk", "agent": agent.name, "data": chunk}
            yield {"event": "agent_end", "agent": agent.name}


class LangChainAdapter(BaseAdapter):
    """Adapter for LangChain framework."""

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        """Initialize LangChain adapter.

        Args:
            provider: LLM provider (anthropic, openai)
            api_key: API key (uses env var if not provided)

        """
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY",
        )

    @property
    def framework_name(self) -> str:
        return "langchain"

    def is_available(self) -> bool:
        """Check if LangChain is installed."""
        return bool(_check_langchain())

    def _get_llm(self, config: AgentConfig):
        """Get LangChain LLM based on config."""
        if not self.is_available():
            raise ImportError(
                "LangChain not installed. Run: pip install langchain langchain-anthropic",
            )

        model_id = config.model_override or self.get_model_for_tier(
            config.model_tier,
            self.provider,
        )

        if self.provider == "anthropic":
            from langchain_anthropic import ChatAnthropic

            # LangChain API varies between versions - use type: ignore for flexibility
            return ChatAnthropic(  # type: ignore[call-arg]
                model=model_id,
                api_key=self.api_key,
                temperature=config.temperature,
                max_tokens_to_sample=config.max_tokens,
            )
        if self.provider == "openai":
            from langchain_openai import ChatOpenAI

            return ChatOpenAI(
                model=model_id,
                api_key=self.api_key,
                temperature=config.temperature,
                max_tokens=config.max_tokens,
            )
        raise ValueError(f"Unsupported provider for LangChain: {self.provider}")

    def create_agent(self, config: AgentConfig) -> LangChainAgent:
        """Create a LangChain-based agent."""
        if not self.is_available():
            raise ImportError("LangChain not installed")

        # Import from langchain or langgraph depending on version
        AgentExecutor: Any = None
        create_tool_calling_agent: Any = None
        try:
            from langchain.agents import AgentExecutor, create_tool_calling_agent
        except (ImportError, AttributeError):
            # Newer versions may have different import paths
            from langgraph.prebuilt import create_react_agent

            create_tool_calling_agent = create_react_agent
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        llm = self._get_llm(config)

        # Build system prompt
        system_prompt = config.system_prompt or self._default_system_prompt(config)

        # Create prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="chat_history", optional=True),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad", optional=True),
            ],
        )

        # Convert tools to LangChain format
        lc_tools = []
        for tool in config.tools:
            lc_tool = self._convert_tool(tool)
            if lc_tool:
                lc_tools.append(lc_tool)

        if lc_tools and AgentCapability.TOOL_USE in config.capabilities:
            # Create tool-calling agent
            agent = create_tool_calling_agent(llm, lc_tools, prompt)
            executor = AgentExecutor(agent=agent, tools=lc_tools, verbose=False)
            return LangChainAgent(config, agent_executor=executor)
        # Create simple chain (prompt | llm)
        chain = prompt | llm
        return LangChainAgent(config, chain=chain)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> LangChainWorkflow:
        """Create a LangChain workflow."""
        # For sequential mode, we can compose chains
        # For more complex modes, just wrap the agents
        return LangChainWorkflow(config, agents)

    def create_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        args_schema: dict | None = None,
    ) -> Any:
        """Create a LangChain tool."""
        if not self.is_available():
            return super().create_tool(name, description, func, args_schema)

        from langchain_core.tools import StructuredTool

        return StructuredTool.from_function(func=func, name=name, description=description)

    def _convert_tool(self, tool: Any) -> Any:
        """Convert a tool to LangChain format."""
        if not self.is_available():
            return None

        # If already a LangChain tool, return as-is
        try:
            from langchain_core.tools import BaseTool

            if isinstance(tool, BaseTool):
                return tool
        except ImportError:
            pass

        # If dict, convert to StructuredTool
        if isinstance(tool, dict):
            return self.create_tool(
                name=tool.get("name", "tool"),
                description=tool.get("description", ""),
                func=tool.get("func", lambda x: x),
                args_schema=tool.get("args_schema"),
            )

        return None

    def _default_system_prompt(self, config: AgentConfig) -> str:
        """Generate default system prompt based on role."""
        role_prompts = {
            "researcher": "You are a thorough researcher. Gather information and cite sources.",
            "writer": "You are a skilled writer. Create clear, engaging content.",
            "reviewer": "You are a critical reviewer. Provide constructive feedback.",
            "editor": "You are an experienced editor. Refine and improve content.",
            "debugger": "You are an expert debugger. Analyze code issues systematically.",
            "security": "You are a security analyst. Identify vulnerabilities and risks.",
            "coordinator": "You coordinate a team of agents. Delegate and synthesize results.",
        }

        base = role_prompts.get(config.role.value, f"You are a helpful {config.role.value} agent.")

        if config.description:
            base = f"{base}\n\n{config.description}"

        return base
