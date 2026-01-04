"""Prompt Templates

Provides protocol and implementations for prompt templates,
including XML-structured prompts.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol

from .context import PromptContext


class PromptTemplate(Protocol):
    """Protocol for prompt templates."""

    def render(self, context: PromptContext) -> str:
        """Render the template with given context.

        Args:
            context: The prompt context containing role, goal, instructions, etc.

        Returns:
            The rendered prompt string.

        """
        ...


@dataclass
class PlainTextPromptTemplate:
    """Simple plain text prompt template.

    Renders prompts in a straightforward text format without XML structure.
    """

    name: str
    include_role: bool = True
    include_constraints: bool = True

    def render(self, context: PromptContext) -> str:
        """Render as plain text prompt."""
        parts = []

        if self.include_role:
            parts.append(f"You are a {context.role}.")
            parts.append("")

        parts.append(f"Goal: {context.goal}")
        parts.append("")

        if context.instructions:
            parts.append("Instructions:")
            for i, inst in enumerate(context.instructions, 1):
                parts.append(f"{i}. {inst}")
            parts.append("")

        if self.include_constraints and context.constraints:
            parts.append("Guidelines:")
            for constraint in context.constraints:
                parts.append(f"- {constraint}")
            parts.append("")

        if context.input_payload:
            parts.append(f"Input ({context.input_type}):")
            parts.append(context.input_payload)

        return "\n".join(parts)


@dataclass
class XmlPromptTemplate:
    """XML-structured prompt template.

    Renders prompts in XML format for consistent parsing and
    structured LLM interactions.
    """

    name: str
    schema_version: str = "1.0"
    response_format: str | None = None
    extra_tags: dict[str, str] = field(default_factory=dict)

    def render(self, context: PromptContext) -> str:
        """Render XML prompt from context.

        Args:
            context: The prompt context.

        Returns:
            XML-formatted prompt string.

        """
        # Build instructions XML
        instructions_xml = self._render_instructions(context.instructions)

        # Build constraints XML
        constraints_xml = self._render_constraints(context.constraints)

        # Build extra context XML if present
        extra_xml = self._render_extra(context.extra)

        # Build input section with CDATA for safety
        input_content = self._escape_cdata(context.input_payload)

        prompt = f"""<request schema="{self.schema_version}">
  <role>{self._escape_xml(context.role)}</role>
  <goal>{self._escape_xml(context.goal)}</goal>
  <instructions>
{instructions_xml}
  </instructions>
  <constraints>
{constraints_xml}
  </constraints>{extra_xml}
  <input type="{context.input_type}">
    <![CDATA[
{input_content}
    ]]>
  </input>
</request>"""

        # Add response format instructions if specified
        if self.response_format:
            prompt += f"\n\n{self._response_instructions()}"

        return prompt

    def _render_instructions(self, instructions: list[str]) -> str:
        """Render instructions as XML steps."""
        if not instructions:
            return "    <!-- No specific instructions -->"
        lines = []
        for i, inst in enumerate(instructions, 1):
            escaped = self._escape_xml(inst)
            lines.append(f"    <step>{i}. {escaped}</step>")
        return "\n".join(lines)

    def _render_constraints(self, constraints: list[str]) -> str:
        """Render constraints as XML rules."""
        if not constraints:
            return "    <!-- No specific constraints -->"
        lines = []
        for constraint in constraints:
            escaped = self._escape_xml(constraint)
            lines.append(f"    <rule>{escaped}</rule>")
        return "\n".join(lines)

    def _render_extra(self, extra: dict[str, Any]) -> str:
        """Render extra context as XML if present."""
        if not extra:
            return ""

        lines = ["\n  <context>"]
        for key, value in extra.items():
            if value:  # Only include non-empty values
                escaped_key = self._escape_xml(str(key))
                escaped_value = self._escape_xml(str(value))
                lines.append(f"    <{escaped_key}>{escaped_value}</{escaped_key}>")
        lines.append("  </context>")

        return "\n".join(lines)

    def _response_instructions(self) -> str:
        """Generate response format instructions."""
        return f"""Please respond using ONLY this XML format (no other text before or after):

{self.response_format}

Important:
- Use the exact XML structure shown above
- Include all required tags even if empty
- Use severity values: critical, high, medium, low, info
- Wrap code examples in CDATA sections"""

    def _escape_xml(self, text: str) -> str:
        """Escape special XML characters."""
        if not text:
            return ""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&apos;")
        )

    def _escape_cdata(self, text: str) -> str:
        """Escape text for use in CDATA section.

        CDATA sections can contain anything except the closing sequence ]]>
        """
        if not text:
            return ""
        # Replace ]]> with ]]]]><![CDATA[> to escape it
        return text.replace("]]>", "]]]]><![CDATA[>")

    def with_response_format(self, response_format: str) -> XmlPromptTemplate:
        """Return a new template with the specified response format."""
        return XmlPromptTemplate(
            name=self.name,
            schema_version=self.schema_version,
            response_format=response_format,
            extra_tags=self.extra_tags.copy(),
        )
