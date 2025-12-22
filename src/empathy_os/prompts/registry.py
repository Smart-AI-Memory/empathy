"""
Built-in XML Prompt Templates Registry

Provides pre-configured XML templates for common workflows.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

from .templates import XmlPromptTemplate

# =============================================================================
# Response Format Definitions
# =============================================================================

SECURITY_AUDIT_RESPONSE = """<response>
  <summary>Brief overall security assessment (1-2 sentences)</summary>
  <findings>
    <finding severity="critical|high|medium|low|info">
      <title>Issue title</title>
      <location>file:line or component</location>
      <details>Description of the vulnerability and potential impact</details>
      <fix>Specific remediation steps with code example if applicable</fix>
    </finding>
    <!-- Additional findings... -->
  </findings>
  <remediation-checklist>
    <item>Priority action item 1</item>
    <item>Priority action item 2</item>
    <!-- Additional items... -->
  </remediation-checklist>
</response>"""

CODE_REVIEW_RESPONSE = """<response>
  <summary>Brief review summary (1-2 sentences)</summary>
  <verdict>approve|approve_with_suggestions|request_changes|reject</verdict>
  <findings>
    <finding severity="critical|high|medium|low|info">
      <title>Issue title</title>
      <location>file:line</location>
      <details>Description of the issue</details>
      <fix>Suggested fix or improvement</fix>
    </finding>
    <!-- Additional findings... -->
  </findings>
  <suggestions>
    <suggestion>Optional improvement suggestion</suggestion>
    <!-- Additional suggestions... -->
  </suggestions>
  <remediation-checklist>
    <item>Required change 1</item>
    <item>Required change 2</item>
    <!-- Additional items if request_changes... -->
  </remediation-checklist>
</response>"""

RESEARCH_RESPONSE = """<response>
  <summary>Research synthesis summary (2-3 sentences)</summary>
  <key-insights>
    <insight>Key insight or finding 1</insight>
    <insight>Key insight or finding 2</insight>
    <!-- Additional insights... -->
  </key-insights>
  <findings>
    <finding severity="info">
      <title>Topic or concept</title>
      <details>Explanation with context</details>
    </finding>
    <!-- Additional topics if needed... -->
  </findings>
  <confidence level="high|medium|low">Reasoning for confidence level</confidence>
  <remediation-checklist>
    <item>Recommended next step 1</item>
    <item>Recommended next step 2</item>
  </remediation-checklist>
</response>"""

BUG_ANALYSIS_RESPONSE = """<response>
  <summary>Root cause summary (1-2 sentences)</summary>
  <findings>
    <finding severity="critical|high|medium|low">
      <title>Bug description</title>
      <location>file:line where issue originates</location>
      <details>Root cause analysis</details>
      <fix>Recommended fix with code</fix>
    </finding>
  </findings>
  <remediation-checklist>
    <item>Fix step 1</item>
    <item>Verification step</item>
    <item>Test to add</item>
  </remediation-checklist>
</response>"""


# =============================================================================
# Built-in Templates
# =============================================================================

BUILTIN_TEMPLATES: dict[str, XmlPromptTemplate] = {
    "security-audit": XmlPromptTemplate(
        name="security-audit",
        schema_version="1.0",
        response_format=SECURITY_AUDIT_RESPONSE,
    ),
    "code-review": XmlPromptTemplate(
        name="code-review",
        schema_version="1.0",
        response_format=CODE_REVIEW_RESPONSE,
    ),
    "research": XmlPromptTemplate(
        name="research",
        schema_version="1.0",
        response_format=RESEARCH_RESPONSE,
    ),
    "bug-analysis": XmlPromptTemplate(
        name="bug-analysis",
        schema_version="1.0",
        response_format=BUG_ANALYSIS_RESPONSE,
    ),
}


def get_template(name: str) -> XmlPromptTemplate | None:
    """
    Get a built-in template by name.

    Args:
        name: Template name (e.g., "security-audit", "code-review").

    Returns:
        XmlPromptTemplate if found, None otherwise.
    """
    return BUILTIN_TEMPLATES.get(name)


def list_templates() -> list[str]:
    """
    List all available built-in template names.

    Returns:
        List of template names.
    """
    return list(BUILTIN_TEMPLATES.keys())


def register_template(name: str, template: XmlPromptTemplate) -> None:
    """
    Register a custom template.

    Args:
        name: Template name for lookup.
        template: XmlPromptTemplate instance.
    """
    BUILTIN_TEMPLATES[name] = template
