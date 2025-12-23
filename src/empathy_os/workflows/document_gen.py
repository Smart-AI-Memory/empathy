"""
Document Generation Workflow

A cost-optimized documentation pipeline:
1. Haiku: Generate outline from code/specs (cheap, fast)
2. Sonnet: Write each section (capable, parallel)
3. Opus: Final review + consistency polish (premium)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import os
from typing import Any

from .base import PROVIDER_MODELS, BaseWorkflow, ModelProvider, ModelTier


class DocumentGenerationWorkflow(BaseWorkflow):
    """
    Multi-tier document generation workflow.

    Uses cheap models for outlining, capable models for content
    generation, and premium models for final polish and consistency
    review.

    Usage:
        workflow = DocumentGenerationWorkflow()
        result = await workflow.execute(
            source_code="...",
            doc_type="api_reference",
            audience="developers"
        )
    """

    name = "doc-gen"
    description = "Cost-optimized documentation generation pipeline"
    stages = ["outline", "write", "polish"]
    tier_map = {
        "outline": ModelTier.CHEAP,
        "write": ModelTier.CAPABLE,
        "polish": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        skip_polish_threshold: int = 1000,
        max_sections: int = 10,
        **kwargs: Any,
    ):
        """
        Initialize workflow.

        Args:
            skip_polish_threshold: Skip premium polish for docs under this
                token count (they're already good enough).
            max_sections: Maximum number of sections to generate.
        """
        super().__init__(**kwargs)
        self.skip_polish_threshold = skip_polish_threshold
        self.max_sections = max_sections
        self._total_content_tokens: int = 0
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
        """Make an actual LLM call using the Anthropic API."""
        client = self._get_client()
        if not client:
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

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """Skip polish for short documents."""
        if stage_name == "polish":
            if self._total_content_tokens < self.skip_polish_threshold:
                self.tier_map["polish"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Execute a document generation stage."""
        if stage_name == "outline":
            return await self._outline(input_data, tier)
        elif stage_name == "write":
            return await self._write(input_data, tier)
        elif stage_name == "polish":
            return await self._polish(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _outline(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Generate document outline from source."""
        source_code = input_data.get("source_code", "")
        target = input_data.get("target", "")
        doc_type = input_data.get("doc_type", "general")
        audience = input_data.get("audience", "developers")

        # Use target if source_code not provided
        content_to_document = source_code or target

        system = """You are a technical writer. Create a detailed outline for documentation.

Based on the content provided, generate an outline with:
1. Logical section structure (5-8 sections)
2. Brief description of each section's purpose
3. Key points to cover in each section

Format as a numbered list with section titles and descriptions."""

        user_message = f"""Create a documentation outline:

Document Type: {doc_type}
Target Audience: {audience}

Content to document:
{content_to_document[:4000]}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=1000
        )

        return (
            {
                "outline": response,
                "doc_type": doc_type,
                "audience": audience,
                "content_to_document": content_to_document,
            },
            input_tokens,
            output_tokens,
        )

    async def _write(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """Write content based on the outline."""
        outline = input_data.get("outline", "")
        doc_type = input_data.get("doc_type", "general")
        audience = input_data.get("audience", "developers")
        content_to_document = input_data.get("content_to_document", "")

        system = """You are a technical writer. Write comprehensive documentation.

Based on the outline provided, write full content for each section:
1. Use clear, professional language
2. Include code examples where appropriate
3. Use markdown formatting
4. Be thorough but concise
5. Target the specified audience

Write the complete document with all sections."""

        user_message = f"""Write documentation based on this outline:

Document Type: {doc_type}
Target Audience: {audience}

Outline:
{outline}

Source content for reference:
{content_to_document[:3000]}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system, user_message, max_tokens=4000
        )

        self._total_content_tokens = output_tokens

        return (
            {
                "draft_document": response,
                "doc_type": doc_type,
                "audience": audience,
                "outline": outline,
            },
            input_tokens,
            output_tokens,
        )

    async def _polish(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Final review and consistency polish using LLM.

        Supports XML-enhanced prompts when enabled in workflow config.
        """
        draft_document = input_data.get("draft_document", "")
        doc_type = input_data.get("doc_type", "general")
        audience = input_data.get("audience", "developers")

        # Build input payload for prompt
        input_payload = f"""Document Type: {doc_type}
Target Audience: {audience}

Draft:
{draft_document}"""

        # Check if XML prompts are enabled
        if self._is_xml_enabled():
            # Use XML-enhanced prompt
            user_message = self._render_xml_prompt(
                role="senior technical editor",
                goal="Polish and improve the documentation for consistency and quality",
                instructions=[
                    "Standardize terminology and formatting",
                    "Improve clarity and flow",
                    "Add missing cross-references",
                    "Fix grammatical issues",
                    "Identify gaps and add helpful notes",
                    "Ensure examples are complete and accurate",
                ],
                constraints=[
                    "Maintain the original structure and intent",
                    "Keep content appropriate for the target audience",
                    "Preserve code examples while improving explanations",
                ],
                input_type="documentation_draft",
                input_payload=input_payload,
                extra={
                    "doc_type": doc_type,
                    "audience": audience,
                },
            )
            system = None  # XML prompt includes all context
        else:
            # Use legacy plain text prompts
            system = """You are a senior technical editor. Polish and improve the documentation:

1. CONSISTENCY:
   - Standardize terminology
   - Fix formatting inconsistencies
   - Ensure consistent code style

2. QUALITY:
   - Improve clarity and flow
   - Add missing cross-references
   - Fix grammatical issues

3. COMPLETENESS:
   - Identify gaps
   - Add helpful notes or warnings
   - Ensure examples are complete

Return the polished document with improvements noted at the end."""

            user_message = f"""Polish this documentation:

{input_payload}"""

        response, input_tokens, output_tokens = await self._call_llm(
            tier, system or "", user_message, max_tokens=5000
        )

        # Parse XML response if enforcement is enabled
        parsed_data = self._parse_xml_response(response)

        result = {
            "document": response,
            "doc_type": doc_type,
            "audience": audience,
            "model_tier_used": tier.value,
        }

        # Merge parsed XML data if available
        if parsed_data.get("xml_parsed"):
            result.update(
                {
                    "xml_parsed": True,
                    "summary": parsed_data.get("summary"),
                    "findings": parsed_data.get("findings", []),
                    "checklist": parsed_data.get("checklist", []),
                }
            )

        return (result, input_tokens, output_tokens)
