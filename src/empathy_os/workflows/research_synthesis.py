"""
Research Synthesis Workflow

A cost-optimized pipeline for research and analysis tasks:
1. Haiku: Summarize each source (cheap, parallel)
2. Sonnet: Identify patterns across summaries
3. Opus: Synthesize final insights (conditional on complexity)

Integration with empathy_os.models:
- Supports LLMExecutor for unified execution (optional)
- WorkflowStepConfig for declarative step definitions
- Automatic telemetry emission when executor is used
- Falls back to direct API calls when executor not provided

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier
from .step_config import WorkflowStepConfig

# Step configurations for executor-based execution
SUMMARIZE_STEP = WorkflowStepConfig(
    name="summarize",
    task_type="summarize",  # Routes to cheap tier
    description="Summarize each source document",
    max_tokens=2048,
)

ANALYZE_STEP = WorkflowStepConfig(
    name="analyze",
    task_type="analyze_patterns",  # Routes to capable tier
    description="Identify patterns across summaries",
    max_tokens=2048,
)

SYNTHESIZE_STEP = WorkflowStepConfig(
    name="synthesize",
    task_type="complex_reasoning",  # Routes to premium tier
    description="Synthesize final insights",
    max_tokens=4096,
)

SYNTHESIZE_STEP_CAPABLE = WorkflowStepConfig(
    name="synthesize",
    task_type="generate_content",  # Routes to capable tier
    tier_hint="capable",  # Force capable tier
    description="Synthesize final insights (lower complexity)",
    max_tokens=4096,
)


class ResearchSynthesisWorkflow(BaseWorkflow):
    """
    Multi-tier research synthesis workflow.

    Uses cheap models for initial summarization, capable models for
    pattern analysis, and optionally premium models for final synthesis
    when the analysis reveals high complexity.

    Usage (legacy - direct API calls):
        workflow = ResearchSynthesisWorkflow()
        result = await workflow.execute(
            sources=["doc1.md", "doc2.md"],
            question="What are the key patterns?"
        )

    Usage (executor-based - unified execution with telemetry):
        from empathy_os.models import MockLLMExecutor

        executor = MockLLMExecutor()  # or EmpathyLLMExecutor for real calls
        workflow = ResearchSynthesisWorkflow(executor=executor)
        result = await workflow.execute(
            sources=["doc1.md", "doc2.md"],
            question="What are the key patterns?"
        )

    When using executor:
    - Automatic task-based routing via WorkflowStepConfig
    - Automatic telemetry emission (LLMCallRecord per call)
    - Automatic workflow telemetry (WorkflowRunRecord at end)
    - Fallback and retry policies applied automatically
    """

    name = "research"
    description = "Cost-optimized research synthesis pipeline"
    stages = ["summarize", "analyze", "synthesize"]
    tier_map = {
        "summarize": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "synthesize": ModelTier.PREMIUM,
    }

    def __init__(self, complexity_threshold: float = 0.7, **kwargs: Any):
        """
        Initialize workflow.

        Args:
            complexity_threshold: Threshold (0-1) above which premium
                synthesis is used. Below this, capable tier is used.
        """
        super().__init__(**kwargs)
        self.complexity_threshold = complexity_threshold
        self._detected_complexity: float = 0.0
        self._client = None
        self._api_key = os.getenv("ANTHROPIC_API_KEY")

    def _get_client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None and self._api_key:
            try:
                import anthropic

                self._client = anthropic.Anthropic(api_key=self._api_key)
            except ImportError:
                pass
        return self._client

    def _get_model_for_tier(self, tier: ModelTier) -> str:
        """Get the model name for a given tier."""
        provider = ModelProvider.ANTHROPIC
        return PROVIDER_MODELS.get(provider, {}).get(tier, "claude-sonnet-4-20250514")

    async def _call_llm(
        self, tier: ModelTier, system: str, user_message: str, max_tokens: int = 4096
    ) -> tuple[str, int, int]:
        """
        Make an actual LLM call using the Anthropic API.

        Returns:
            (response_text, input_tokens, output_tokens)
        """
        client = self._get_client()
        if not client:
            # Fallback to simulation if no API key
            return (
                f"[Simulated - set ANTHROPIC_API_KEY for real results]\n\n{user_message[:200]}...",
                len(user_message) // 4,
                100,
            )

        model = self._get_model_for_tier(tier)

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                system=system,
                messages=[{"role": "user", "content": user_message}],
            )

            content = response.content[0].text if response.content else ""
            input_tokens = response.usage.input_tokens
            output_tokens = response.usage.output_tokens

            return content, input_tokens, output_tokens

        except Exception as e:
            return f"Error calling LLM: {e}", 0, 0

    async def _call_with_step(
        self,
        step: WorkflowStepConfig,
        system: str,
        user_message: str,
    ) -> tuple[str, int, int]:
        """
        Make an LLM call using WorkflowStepConfig and executor (if available).

        This is the recommended approach for new workflows. It provides:
        - Automatic task-based routing
        - Automatic telemetry emission
        - Fallback and retry policies

        If no executor is configured, falls back to direct API call.

        Args:
            step: WorkflowStepConfig defining the step
            system: System prompt
            user_message: User message

        Returns:
            (response_text, input_tokens, output_tokens)
        """
        if self._executor is not None:
            # Use executor-based execution with telemetry
            prompt = f"{system}\n\n{user_message}" if system else user_message
            content, input_tokens, output_tokens, _cost = await self.run_step_with_executor(
                step=step,
                prompt=prompt,
                system=system,
            )
            return content, input_tokens, output_tokens
        else:
            # Fall back to direct API call
            tier_value = step.effective_tier
            tier = ModelTier(tier_value)
            return await self._call_llm(
                tier, system, user_message, max_tokens=step.max_tokens or 4096
            )

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """Skip premium synthesis if complexity is low."""
        if stage_name == "synthesize" and self._detected_complexity < self.complexity_threshold:
            # Downgrade to capable tier instead of skipping
            self.tier_map["synthesize"] = ModelTier.CAPABLE
            return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """
        Execute a research workflow stage.

        Args:
            stage_name: Stage to run
            tier: Model tier to use
            input_data: Input data

        Returns:
            (output, input_tokens, output_tokens)
        """
        if stage_name == "summarize":
            return await self._summarize(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "synthesize":
            return await self._synthesize(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _summarize(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Summarize each source document or research the question.
        """
        sources = input_data.get("sources", [])
        question = input_data.get("question", "Summarize the content")

        total_input = 0
        total_output = 0

        # If no sources provided, treat this as a research question
        if not sources:
            system = """You are a research assistant. Provide a comprehensive summary
of the topic, breaking it into key points and insights. Be thorough but concise."""

            user_message = f"Research and summarize: {question}"

            response, inp_tokens, out_tokens = await self._call_llm(
                tier, system, user_message, max_tokens=2048
            )

            return (
                {
                    "summaries": [{"source": "research", "summary": response, "key_points": []}],
                    "question": question,
                    "source_count": 0,
                    "research_mode": True,
                },
                inp_tokens,
                out_tokens,
            )

        # Process each source
        summaries = []
        system = """You are a research assistant. Summarize the given content,
extracting key points relevant to the research question. Be thorough but concise."""

        for source in sources:
            user_message = f"Research question: {question}\n\nSource content:\n{source}"

            response, inp_tokens, out_tokens = await self._call_llm(
                tier, system, user_message, max_tokens=1024
            )

            summaries.append(
                {
                    "source": str(source)[:100],
                    "summary": response,
                    "key_points": [],
                }
            )

            total_input += inp_tokens
            total_output += out_tokens

        return (
            {
                "summaries": summaries,
                "question": question,
                "source_count": len(sources),
            },
            total_input,
            total_output,
        )

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Analyze patterns across summaries.
        """
        summaries = input_data.get("summaries", [])
        question = input_data.get("question", "")
        research_mode = input_data.get("research_mode", False)

        # For research mode, pass through the summary
        if research_mode and summaries:
            self._detected_complexity = 0.8  # Assume high complexity for research
            return (
                {
                    "patterns": [],
                    "complexity": self._detected_complexity,
                    "question": question,
                    "summary_count": len(summaries),
                    "research_summary": summaries[0].get("summary", ""),
                },
                0,
                0,
            )

        # Combine summaries for analysis
        combined = "\n\n".join(
            [f"Source: {s.get('source', 'unknown')}\n{s.get('summary', '')}" for s in summaries]
        )

        system = """You are a research analyst. Analyze the summaries to identify:
1. Common patterns and themes
2. Contradictions or disagreements
3. Key insights
4. Complexity level (simple, moderate, complex)

Provide a structured analysis."""

        user_message = f"Research question: {question}\n\nSummaries to analyze:\n{combined}"

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=2048
        )

        # Estimate complexity from response length and content
        self._detected_complexity = min(len(response) / 2000, 1.0)

        return (
            {
                "patterns": [{"pattern": response, "sources": [], "confidence": 0.85}],
                "complexity": self._detected_complexity,
                "question": question,
                "summary_count": len(summaries),
                "analysis": response,
            },
            input_tokens,
            output_tokens,
        )

    async def _synthesize(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Synthesize final insights from patterns.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        _patterns = input_data.get("patterns", [])  # noqa: F841 - reserved for future use
        complexity = input_data.get("complexity", 0.5)
        question = input_data.get("question", "")
        analysis = input_data.get("analysis", "")
        research_summary = input_data.get("research_summary", "")

        # Use research summary if available (research mode)
        if research_summary:
            analysis = research_summary

        # Build input payload
        input_payload = f"""Research question: {question}

Analysis to synthesize:
{analysis}

Complexity level: {complexity:.2f}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            user_message = self._render_xml_prompt(
                role="expert research synthesizer",
                goal="Synthesize analysis into comprehensive answer with key insights",
                instructions=[
                    "Provide a comprehensive answer to the research question",
                    "Highlight key insights and takeaways",
                    "Note any caveats or areas needing further research",
                    "Structure your response clearly with sections if appropriate",
                    "Provide 1-2 concrete next steps or decisions",
                ],
                constraints=[
                    "Be thorough, insightful, and actionable",
                    "Focus on practical implications",
                    "3-5 paragraphs for main answer",
                ],
                input_type="research_analysis",
                input_payload=input_payload,
                extra={
                    "complexity_score": complexity,
                },
            )
            system = None
        else:
            system = """You are an expert synthesizer. Based on the analysis provided:
1. Provide a comprehensive answer to the research question
2. Highlight key insights and takeaways
3. Note any caveats or areas needing further research
4. Structure your response clearly with sections if appropriate

Be thorough, insightful, and actionable."""

            user_message = f"""{input_payload}

Provide a comprehensive synthesis and answer."""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=4096
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        synthesis = {
            "answer": response,
            "key_insights": [],
            "confidence": 0.85,
            "model_tier_used": tier.value,
            "complexity_score": complexity,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            synthesis.update(
                {
                    "xml_parsed": True,
                    "summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )
            # Extract key insights from parsed response
            extra = parsed_data.get("_parsed_response")
            if extra and hasattr(extra, "extra"):
                key_insights = extra.extra.get("key_insights", [])
                if key_insights:
                    synthesis["key_insights"] = key_insights

        return synthesis, input_tokens, output_tokens
