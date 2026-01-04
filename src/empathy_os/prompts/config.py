"""XML Prompt Configuration

Provides configuration dataclass for XML-enhanced prompts.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class XmlPromptConfig:
    """Configuration for XML prompt behavior.

    Attributes:
        enabled: Whether XML prompts are enabled for this workflow/stage.
        schema_version: XML schema version (default "1.0").
        enforce_response_xml: If True, instruct model to respond with XML.
        fallback_on_parse_error: If True, return raw text on XML parse failure.
        template_name: Reference to a built-in template from BUILTIN_TEMPLATES.
        custom_template: Inline XML template string (overrides template_name).
        extra: Additional configuration options.

    """

    enabled: bool = False
    schema_version: str = "1.0"
    enforce_response_xml: bool = False
    fallback_on_parse_error: bool = True
    template_name: str | None = None
    custom_template: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def merge_with(self, other: XmlPromptConfig) -> XmlPromptConfig:
        """Merge this config with another, with 'other' taking precedence.

        Useful for combining global defaults with workflow-specific overrides.
        """
        merged_extra = {**self.extra, **other.extra}
        return XmlPromptConfig(
            enabled=other.enabled if other.enabled else self.enabled,
            schema_version=other.schema_version or self.schema_version,
            enforce_response_xml=other.enforce_response_xml or self.enforce_response_xml,
            fallback_on_parse_error=other.fallback_on_parse_error,
            template_name=other.template_name or self.template_name,
            custom_template=other.custom_template or self.custom_template,
            extra=merged_extra,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> XmlPromptConfig:
        """Create XmlPromptConfig from a dictionary."""
        return cls(
            enabled=data.get("enabled", False),
            schema_version=data.get("schema_version", "1.0"),
            enforce_response_xml=data.get("enforce_response_xml", False),
            fallback_on_parse_error=data.get("fallback_on_parse_error", True),
            template_name=data.get("template_name"),
            custom_template=data.get("custom_template"),
            extra=data.get("extra", {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "enabled": self.enabled,
            "schema_version": self.schema_version,
            "enforce_response_xml": self.enforce_response_xml,
            "fallback_on_parse_error": self.fallback_on_parse_error,
            "template_name": self.template_name,
            "custom_template": self.custom_template,
            "extra": self.extra,
        }
