"""AutoGen Adapter

Creates conversational multi-agent systems using Microsoft's AutoGen.
Best for agent teams that converse to solve problems.

Requires: pip install pyautogen

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import os
from collections.abc import Callable

from empathy_llm_toolkit.agent_factory.base import (
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)

# Lazy import
_autogen_available = None


def _check_autogen():
    """Check if AutoGen is available."""
    global _autogen_available
    if _autogen_available is None:
        try:
            import autogen  # noqa: F401

            _autogen_available = True
        except ImportError:
            _autogen_available = False
    return _autogen_available


class AutoGenAgent(BaseAgent):
    """Agent wrapping an AutoGen AssistantAgent or UserProxyAgent."""

    def __init__(self, config: AgentConfig, autogen_agent=None):
        super().__init__(config)
        self._autogen_agent = autogen_agent
        self._last_response = None

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the AutoGen agent."""
        if not self._autogen_agent:
            return {"output": "No AutoGen agent configured", "metadata": {}}

        # Format message
        if isinstance(input_data, str):
            message = input_data
        else:
            message = input_data.get("input", input_data.get("message", str(input_data)))

        try:
            # AutoGen uses synchronous chat, wrap in executor
            loop = asyncio.get_event_loop()

            def sync_chat():
                # For single agent invocation, we use generate_reply
                if hasattr(self._autogen_agent, "generate_reply"):
                    messages = [{"role": "user", "content": message}]
                    reply = self._autogen_agent.generate_reply(messages=messages)
                    return reply
                return f"[{self.name}] Received: {message}"

            reply = await loop.run_in_executor(None, sync_chat)

            output = reply if isinstance(reply, str) else str(reply)

            self._conversation_history.append({"role": "user", "content": message})
            self._conversation_history.append({"role": "assistant", "content": output})

            return {"output": output, "metadata": {"framework": "autogen", "model": self.model}}

        except Exception as e:
            return {"output": f"Error: {e}", "metadata": {"error": str(e)}}

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """AutoGen doesn't support streaming natively."""
        result = await self.invoke(input_data, context)
        yield result

    def get_autogen_agent(self):
        """Get the underlying AutoGen agent for direct use."""
        return self._autogen_agent


class AutoGenWorkflow(BaseWorkflow):
    """Workflow using AutoGen's GroupChat."""

    def __init__(
        self,
        config: WorkflowConfig,
        agents: list[BaseAgent],
        group_chat=None,
        manager=None,
    ):
        super().__init__(config, agents)
        self._group_chat = group_chat
        self._manager = manager

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the AutoGen group chat."""
        if not self._manager:
            return await self._run_sequential(input_data)

        # Format message
        if isinstance(input_data, str):
            message = input_data
        else:
            message = input_data.get("input", str(input_data))

        try:
            loop = asyncio.get_event_loop()

            def sync_chat():
                # Get first agent to initiate
                first_agent = list(self.agents.values())[0]
                ag_agent = (
                    first_agent.get_autogen_agent()
                    if hasattr(first_agent, "get_autogen_agent")
                    else None
                )

                if ag_agent and self._manager:
                    # Initiate chat through manager
                    ag_agent.initiate_chat(self._manager, message=message)
                    # Get chat history from manager
                    return self._manager.chat_messages

                return {"messages": []}

            chat_history = await loop.run_in_executor(None, sync_chat)

            # Extract final response
            if chat_history:
                messages = []
                for _agent_name, msgs in (
                    chat_history.items() if isinstance(chat_history, dict) else []
                ):
                    messages.extend(msgs)
                if messages:
                    output = messages[-1].get("content", "") if messages else ""
                else:
                    output = "Chat completed"
            else:
                output = "No response"

            return {
                "output": output,
                "state": {"chat_history": chat_history},
                "metadata": {"framework": "autogen"},
            }

        except Exception as e:
            return {"output": f"Error: {e}", "error": str(e)}

    async def _run_sequential(self, input_data: str | dict) -> dict:
        """Fallback sequential execution."""
        current = input_data
        results = []
        for agent in self.agents.values():
            result = await agent.invoke(current)
            results.append(result)
            current = result.get("output", current)
        return {"output": current if isinstance(current, str) else str(current), "results": results}

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """AutoGen doesn't support streaming; yield final result."""
        result = await self.run(input_data, initial_state)
        yield result


class AutoGenAdapter(BaseAdapter):
    """Adapter for Microsoft AutoGen framework."""

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY",
        )

    @property
    def framework_name(self) -> str:
        return "autogen"

    def is_available(self) -> bool:
        return bool(_check_autogen())

    def _get_llm_config(self, config: AgentConfig) -> dict:
        """Build AutoGen LLM config."""
        model_id = config.model_override or self.get_model_for_tier(
            config.model_tier,
            self.provider,
        )

        if self.provider == "anthropic":
            return {
                "config_list": [
                    {"model": model_id, "api_key": self.api_key, "api_type": "anthropic"},
                ],
                "temperature": config.temperature,
                "max_tokens": config.max_tokens,
            }
        # OpenAI (default for AutoGen)
        return {
            "config_list": [{"model": model_id, "api_key": self.api_key}],
            "temperature": config.temperature,
            "max_tokens": config.max_tokens,
        }

    def create_agent(self, config: AgentConfig) -> AutoGenAgent:
        """Create an AutoGen agent."""
        if not self.is_available():
            raise ImportError("AutoGen not installed. Run: pip install pyautogen")

        import autogen

        llm_config = self._get_llm_config(config)
        system_message = config.system_prompt or self._default_system_message(config)

        # Determine agent type based on role
        if config.role == AgentRole.EXECUTOR:
            # UserProxyAgent for code execution
            ag_agent = autogen.UserProxyAgent(
                name=config.name,
                system_message=system_message,
                human_input_mode="NEVER",
                code_execution_config={"work_dir": "workspace", "use_docker": False},
            )
        else:
            # AssistantAgent for general tasks
            ag_agent = autogen.AssistantAgent(
                name=config.name,
                system_message=system_message,
                llm_config=llm_config,
            )

        return AutoGenAgent(config, autogen_agent=ag_agent)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> AutoGenWorkflow:
        """Create an AutoGen GroupChat workflow."""
        if not self.is_available():
            raise ImportError("AutoGen not installed")

        import autogen

        # Extract underlying AutoGen agents
        autogen_agents = []
        for agent in agents:
            if hasattr(agent, "get_autogen_agent"):
                ag = agent.get_autogen_agent()
                if ag:
                    autogen_agents.append(ag)

        if not autogen_agents:
            # Create default agents
            return AutoGenWorkflow(config, agents)

        # Create GroupChat
        if config.mode == "conversation":
            # Free-form conversation
            group_chat = autogen.GroupChat(
                agents=autogen_agents,
                messages=[],
                max_round=config.max_iterations,
            )
        else:
            # Sequential (round-robin)
            group_chat = autogen.GroupChat(
                agents=autogen_agents,
                messages=[],
                max_round=config.max_iterations,
                speaker_selection_method="round_robin",
            )

        # Create manager
        llm_config = self._get_llm_config(AgentConfig(name="manager", model_tier="capable"))
        manager = autogen.GroupChatManager(groupchat=group_chat, llm_config=llm_config)

        return AutoGenWorkflow(config, agents, group_chat=group_chat, manager=manager)

    def create_tool(
        self,
        name: str,
        description: str,
        func: Callable,
        args_schema: dict | None = None,
    ) -> dict:
        """Create a function for AutoGen agents."""
        # AutoGen uses function registration
        return {"name": name, "description": description, "func": func, "args_schema": args_schema}

    def _default_system_message(self, config: AgentConfig) -> str:
        """Generate default system message."""
        role_messages = {
            AgentRole.COORDINATOR: "You coordinate a team of agents to solve complex problems.",
            AgentRole.RESEARCHER: "You research and gather information thoroughly.",
            AgentRole.WRITER: "You write clear, well-structured content.",
            AgentRole.REVIEWER: "You review work and provide constructive feedback.",
            AgentRole.EXECUTOR: "You execute code and commands when needed.",
            AgentRole.DEBUGGER: "You find and fix bugs in code.",
        }

        return role_messages.get(config.role, f"You are a helpful {config.role.value} agent.")
