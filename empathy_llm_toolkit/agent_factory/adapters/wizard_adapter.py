"""Wizard-to-Agent Bridge Adapter

Bridges existing wizards to the Agent Factory interface, allowing
wizards to be used in Agent Factory workflows and pipelines.

This enables:
- Using existing wizards in Agent Factory workflows
- Combining wizards with other agents
- Applying model tier routing to wizard operations
- Cost tracking for wizard calls

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import logging

from empathy_llm_toolkit.agent_factory.base import (
    AgentConfig,
    AgentRole,
    BaseAdapter,
    BaseAgent,
    BaseWorkflow,
    WorkflowConfig,
)
from empathy_llm_toolkit.agent_factory.decorators import log_performance, safe_agent_operation

logger = logging.getLogger(__name__)


class WizardAgent(BaseAgent):
    """Agent wrapper for existing wizards.

    Adapts the wizard's analyze() method to the Agent Factory
    invoke() interface.
    """

    def __init__(self, wizard, config: AgentConfig):
        """Initialize wizard agent.

        Args:
            wizard: Wizard instance (must have analyze() method)
            config: Agent configuration

        """
        super().__init__(config)
        self._wizard = wizard

        # Extract wizard properties
        self._wizard_name = getattr(wizard, "name", wizard.__class__.__name__)
        self._wizard_level = getattr(wizard, "level", 4)

    @property
    def wizard(self):
        """Get the underlying wizard."""
        return self._wizard

    @property
    def wizard_level(self) -> int:
        """Get the wizard's empathy level."""
        return self._wizard_level

    @safe_agent_operation("wizard_invoke")
    @log_performance(threshold_seconds=5.0)
    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the wizard.

        Transforms input to wizard format, calls analyze(),
        and transforms output to Agent Factory format.

        Args:
            input_data: String query or dict with input
            context: Optional additional context

        Returns:
            Dict with output, metadata, predictions, recommendations

        """
        # Build wizard context
        wizard_context = context.copy() if context else {}

        if isinstance(input_data, str):
            wizard_context["input"] = input_data
            wizard_context["query"] = input_data
        else:
            wizard_context.update(input_data)

        # Add agent metadata
        wizard_context["agent_name"] = self.name
        wizard_context["agent_role"] = self.role.value

        # Add conversation history if available
        if self._conversation_history:
            wizard_context["conversation_history"] = self._conversation_history[-10:]

        # Call wizard analyze
        result = await self._wizard.analyze(wizard_context)

        # Transform to Agent Factory format
        output = self._extract_output(result)

        # Track conversation
        user_input = wizard_context.get("input", wizard_context.get("query", str(input_data)))
        self._conversation_history.append({"role": "user", "content": user_input})
        self._conversation_history.append({"role": "assistant", "content": str(output)})

        return {
            "output": output,
            "metadata": {
                "wizard": self._wizard_name,
                "level": self._wizard_level,
                "confidence": result.get("confidence", 0.0),
                "from_cache": result.get("_from_cache", False),
                "model": self.model,
            },
            "predictions": result.get("predictions", []),
            "recommendations": result.get("recommendations", []),
            "patterns": result.get("patterns", []),
            "raw_result": result,
        }

    def _extract_output(self, result: dict) -> str:
        """Extract the main output from wizard result.

        Wizards return various formats, so we need to normalize.
        """
        # Try common output keys
        for key in ["output", "response", "result", "analysis", "summary"]:
            if result.get(key):
                value = result[key]
                if isinstance(value, str):
                    return value
                if isinstance(value, list):
                    return "\n".join(str(item) for item in value)
                return str(value)

        # Fall back to recommendations
        if "recommendations" in result:
            recs = result["recommendations"]
            if isinstance(recs, list):
                return "\n".join(f"- {r}" for r in recs)

        # Last resort: stringify the result
        return str(result)

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """Stream wizard response.

        Most wizards don't support streaming, so we yield the full response.
        """
        result = await self.invoke(input_data, context)
        yield result


class WizardWorkflow(BaseWorkflow):
    """Workflow for chaining multiple wizards.

    Allows wizards to be composed into pipelines where
    the output of one feeds into the next.
    """

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the wizard workflow.

        Args:
            input_data: Initial input
            initial_state: Optional starting state

        Returns:
            Combined results from all wizards

        """
        self._state = initial_state or {}
        self._state["input"] = input_data

        results: list[dict] = []
        current_input = input_data

        for agent in self.agents.values():
            # Build context with previous results
            context = {
                "previous_results": results,
                "state": self._state,
            }

            # Invoke wizard agent
            result = await agent.invoke(current_input, context)
            result["agent"] = agent.name
            results.append(result)

            # Pass output to next wizard
            current_input = result.get("output", "")

            # Collect predictions and recommendations
            self._state.setdefault("all_predictions", []).extend(result.get("predictions", []))
            self._state.setdefault("all_recommendations", []).extend(
                result.get("recommendations", []),
            )

        # Build final output
        self._state["results"] = results
        self._state["final_output"] = results[-1]["output"] if results else ""

        return {
            "output": self._state["final_output"],
            "results": results,
            "state": self._state,
            "agents_invoked": [r.get("agent") for r in results],
            "all_predictions": self._state.get("all_predictions", []),
            "all_recommendations": self._state.get("all_recommendations", []),
        }

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """Stream workflow execution."""
        self._state = initial_state or {}
        self._state["input"] = input_data

        for agent in self.agents.values():
            context = {"state": self._state}
            yield {"event": "wizard_start", "wizard": agent.name}

            # agent.stream returns an async generator
            stream_gen = agent.stream(input_data, context)
            async for chunk in stream_gen:  # type: ignore[attr-defined]
                yield {"event": "wizard_output", "wizard": agent.name, "data": chunk}

            yield {"event": "wizard_end", "wizard": agent.name}


class WizardAdapter(BaseAdapter):
    """Adapter for integrating wizards with Agent Factory.

    Allows existing wizards to be used as agents in the
    Agent Factory ecosystem.

    Example:
        from empathy_software_plugin.wizards import AdvancedDebuggingWizard

        adapter = WizardAdapter()

        # Wrap a wizard
        wizard = AdvancedDebuggingWizard()
        agent = adapter.create_agent_from_wizard(
            wizard,
            name="debugger",
            model_tier="capable"
        )

        # Use in workflow
        result = await agent.invoke({"linters": {"eslint": output}})

    """

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        """Initialize wizard adapter.

        Args:
            provider: LLM provider (for model tier resolution)
            api_key: API key (uses env var if not provided)

        """
        self.provider = provider
        self.api_key = api_key

    @property
    def framework_name(self) -> str:
        return "wizard"

    def is_available(self) -> bool:
        """Wizard adapter is always available."""
        return True

    def create_agent(self, config: AgentConfig) -> WizardAgent:
        """Create a wizard agent from config.

        Note: This requires a wizard instance in config.framework_options.

        Args:
            config: Agent configuration with wizard in framework_options

        Returns:
            WizardAgent instance

        """
        wizard = config.framework_options.get("wizard")
        if wizard is None:
            raise ValueError(
                "Wizard instance required in config.framework_options['wizard']. "
                "Use create_agent_from_wizard() for easier wizard wrapping.",
            )

        return WizardAgent(wizard, config)

    def create_agent_from_wizard(
        self,
        wizard,
        name: str | None = None,
        role: AgentRole | str = AgentRole.CUSTOM,
        model_tier: str = "capable",
        **kwargs,
    ) -> WizardAgent:
        """Create an agent from a wizard instance.

        This is the preferred method for wrapping wizards.

        Args:
            wizard: Wizard instance
            name: Agent name (defaults to wizard name)
            role: Agent role
            model_tier: Model tier for LLM calls
            **kwargs: Additional AgentConfig options

        Returns:
            WizardAgent wrapping the wizard

        """
        # Get wizard name
        wizard_name = getattr(wizard, "name", wizard.__class__.__name__)
        agent_name = name or wizard_name.lower().replace(" ", "_")

        # Get wizard empathy level
        wizard_level = getattr(wizard, "level", 4)

        # Parse role
        if isinstance(role, str):
            try:
                role = AgentRole(role.lower())
            except ValueError:
                role = AgentRole.CUSTOM

        # Build config
        config = AgentConfig(
            name=agent_name,
            role=role,
            description=f"Agent wrapping {wizard_name}",
            model_tier=model_tier,
            empathy_level=wizard_level,
            framework_options={"wizard": wizard},
            **kwargs,
        )

        return WizardAgent(wizard, config)

    def create_agent_from_wizard_class(
        self,
        wizard_class: type,
        name: str | None = None,
        wizard_kwargs: dict | None = None,
        **agent_kwargs,
    ) -> WizardAgent:
        """Create an agent from a wizard class.

        Instantiates the wizard and wraps it.

        Args:
            wizard_class: Wizard class to instantiate
            name: Agent name
            wizard_kwargs: Arguments for wizard constructor
            **agent_kwargs: Arguments for create_agent_from_wizard

        Returns:
            WizardAgent instance

        """
        wizard_kwargs = wizard_kwargs or {}
        wizard = wizard_class(**wizard_kwargs)

        return self.create_agent_from_wizard(wizard, name=name, **agent_kwargs)

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> WizardWorkflow:
        """Create a workflow from wizard agents.

        Args:
            config: Workflow configuration
            agents: List of wizard agents

        Returns:
            WizardWorkflow instance

        """
        return WizardWorkflow(config, agents)

    def create_tool(
        self,
        name: str,
        description: str,
        func,
        args_schema: dict | None = None,
    ) -> dict:
        """Create a tool dict (wizards don't use tools directly).

        Returns a tool dict for documentation purposes.
        """
        return {
            "name": name,
            "description": description,
            "func": func,
            "args_schema": args_schema,
            "note": "Wizards typically don't use external tools",
        }


# Convenience function for quick wizard wrapping
def wrap_wizard(wizard, name: str | None = None, model_tier: str = "capable") -> WizardAgent:
    """Quick helper to wrap a wizard as an agent.

    Args:
        wizard: Wizard instance
        name: Optional agent name
        model_tier: Model tier

    Returns:
        WizardAgent instance

    Example:
        from empathy_software_plugin.wizards import SecurityAnalysisWizard
        from empathy_llm_toolkit.agent_factory.adapters.wizard_adapter import wrap_wizard

        security_wizard = SecurityAnalysisWizard()
        security_agent = wrap_wizard(security_wizard, model_tier="capable")

        result = await security_agent.invoke({"code": source_code})

    """
    adapter = WizardAdapter()
    return adapter.create_agent_from_wizard(wizard, name=name, model_tier=model_tier)
