"""
Haystack Adapter

Creates RAG pipelines and document processing agents using deepset Haystack.
Best for document QA, search, and NLP workflows.

Requires: pip install haystack-ai

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

# Lazy import
_haystack_available = None


def _check_haystack():
    """Check if Haystack is available."""
    global _haystack_available
    if _haystack_available is None:
        try:
            import haystack  # noqa: F401

            _haystack_available = True
        except ImportError:
            _haystack_available = False
    return _haystack_available


class HaystackAgent(BaseAgent):
    """Agent wrapping a Haystack Pipeline or Component."""

    def __init__(self, config: AgentConfig, pipeline=None, generator=None):
        super().__init__(config)
        self._pipeline = pipeline
        self._generator = generator

    async def invoke(self, input_data: str | dict, context: dict | None = None) -> dict:
        """Invoke the Haystack pipeline/generator."""
        # Format query
        if isinstance(input_data, str):
            query = input_data
        else:
            query = input_data.get("query", input_data.get("input", str(input_data)))

        try:
            if self._pipeline:
                # Run pipeline
                result = self._pipeline.run({"query": query, **(context or {})})

                # Extract answer
                if "answers" in result:
                    answers = result["answers"]
                    output = answers[0].data if answers else "No answer found"
                elif "replies" in result:
                    output = result["replies"][0] if result["replies"] else "No reply"
                else:
                    output = str(result)

            elif self._generator:
                # Use generator directly
                result = self._generator.run(prompt=query)
                output = result.get("replies", [query])[0]

            else:
                output = f"[{self.name}] No pipeline configured"
                result = {}

            self._conversation_history.append({"role": "user", "content": query})
            self._conversation_history.append({"role": "assistant", "content": output})

            return {
                "output": output,
                "metadata": {
                    "framework": "haystack",
                    "model": self.model,
                    "raw_result": result if isinstance(result, dict) else {},
                },
            }

        except Exception as e:
            return {"output": f"Error: {e}", "metadata": {"error": str(e)}}

    async def stream(self, input_data: str | dict, context: dict | None = None):
        """Haystack 2.0 supports streaming for some generators."""
        # Most Haystack components don't stream; yield full result
        result = await self.invoke(input_data, context)
        yield result


class HaystackWorkflow(BaseWorkflow):
    """Workflow using Haystack Pipeline."""

    def __init__(self, config: WorkflowConfig, agents: list[BaseAgent], pipeline=None):
        super().__init__(config, agents)
        self._pipeline = pipeline

    async def run(self, input_data: str | dict, initial_state: dict | None = None) -> dict:
        """Run the Haystack pipeline workflow."""
        if isinstance(input_data, str):
            query = input_data
        else:
            query = input_data.get("query", input_data.get("input", str(input_data)))

        self._state = initial_state or {}

        try:
            if self._pipeline:
                result = self._pipeline.run({"query": query, **self._state})

                # Extract output
                if "answers" in result:
                    output = result["answers"][0].data if result["answers"] else ""
                elif "replies" in result:
                    output = result["replies"][0] if result["replies"] else ""
                else:
                    output = str(result)

                self._state.update(result)

                return {
                    "output": output,
                    "state": self._state,
                    "metadata": {"framework": "haystack"},
                }

            else:
                # Fallback to sequential agent execution
                return await self._run_sequential(input_data)

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
        return {"output": current, "results": results}

    async def stream(self, input_data: str | dict, initial_state: dict | None = None):
        """Stream workflow execution."""
        result = await self.run(input_data, initial_state)
        yield result


class HaystackAdapter(BaseAdapter):
    """Adapter for deepset Haystack framework."""

    def __init__(self, provider: str = "anthropic", api_key: str | None = None):
        self.provider = provider
        self.api_key = api_key or os.getenv(
            "ANTHROPIC_API_KEY" if provider == "anthropic" else "OPENAI_API_KEY"
        )

    @property
    def framework_name(self) -> str:
        return "haystack"

    def is_available(self) -> bool:
        return bool(_check_haystack())

    def _get_generator(self, config: AgentConfig):
        """Get Haystack generator based on provider."""
        if not self.is_available():
            raise ImportError("Haystack not installed. Run: pip install haystack-ai")

        model_id = config.model_override or self.get_model_for_tier(
            config.model_tier, self.provider
        )

        if self.provider == "anthropic":
            from haystack_integrations.components.generators.anthropic import AnthropicChatGenerator

            return AnthropicChatGenerator(
                model=model_id,
                api_key=self.api_key,
                generation_kwargs={
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                },
            )
        elif self.provider == "openai":
            from haystack.components.generators import OpenAIGenerator

            return OpenAIGenerator(
                model=model_id,
                api_key=self.api_key,
                generation_kwargs={
                    "temperature": config.temperature,
                    "max_tokens": config.max_tokens,
                },
            )
        else:
            raise ValueError(f"Unsupported provider for Haystack: {self.provider}")

    def create_agent(self, config: AgentConfig) -> HaystackAgent:
        """Create a Haystack agent."""
        if not self.is_available():
            raise ImportError("Haystack not installed")

        # For RAG roles, create a full pipeline
        if config.role in [AgentRole.RETRIEVER, AgentRole.ANSWERER, AgentRole.SUMMARIZER]:
            if AgentCapability.RETRIEVAL in config.capabilities:
                pipeline = self._create_rag_pipeline(config)
                return HaystackAgent(config, pipeline=pipeline)

        # For other roles, just use a generator
        generator = self._get_generator(config)
        return HaystackAgent(config, generator=generator)

    def _create_rag_pipeline(self, config: AgentConfig):
        """Create a RAG pipeline."""
        from haystack import Pipeline
        from haystack.components.builders import PromptBuilder

        pipeline = Pipeline()

        # Add prompt builder
        template = (
            config.system_prompt
            or """
        Answer the question based on the context.

        Context: {{context}}
        Question: {{query}}
        Answer:
        """
        )
        prompt_builder = PromptBuilder(template=template)
        pipeline.add_component("prompt_builder", prompt_builder)

        # Add generator
        generator = self._get_generator(config)
        pipeline.add_component("generator", generator)

        # Connect components
        pipeline.connect("prompt_builder", "generator")

        return pipeline

    def create_workflow(self, config: WorkflowConfig, agents: list[BaseAgent]) -> HaystackWorkflow:
        """Create a Haystack Pipeline workflow."""
        if not self.is_available():
            raise ImportError("Haystack not installed")

        from haystack import Pipeline

        # Build a pipeline from agents
        pipeline = Pipeline()

        # For now, create a simple sequential pipeline
        # More complex routing would require custom components

        for _i, agent in enumerate(agents):
            if hasattr(agent, "_generator") and agent._generator:
                pipeline.add_component(f"agent_{agent.name}", agent._generator)

        # Connect sequentially (simplified)
        # Real implementation would need proper input/output mapping

        return HaystackWorkflow(config, agents, pipeline=pipeline)

    def create_tool(
        self, name: str, description: str, func: Callable, args_schema: dict | None = None
    ) -> dict:
        """Create a tool for Haystack (custom component would be needed)."""
        return {"name": name, "description": description, "func": func, "args_schema": args_schema}

    def create_document_store(self, store_type: str = "in_memory") -> Any:
        """Create a Haystack document store."""
        if not self.is_available():
            raise ImportError("Haystack not installed")

        if store_type == "in_memory":
            from haystack.document_stores.in_memory import InMemoryDocumentStore

            return InMemoryDocumentStore()
        else:
            raise ValueError(f"Unsupported store type: {store_type}")
