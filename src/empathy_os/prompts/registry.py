"""Built-in XML Prompt Templates Registry

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

PERF_AUDIT_RESPONSE = """<response>
  <summary>Performance assessment summary (1-2 sentences)</summary>
  <performance-score>0-100</performance-score>
  <findings>
    <finding severity="critical|high|medium|low">
      <title>Performance issue title</title>
      <location>file:line or component</location>
      <details>Description of the bottleneck and its impact</details>
      <fix>Optimization recommendation with code example</fix>
    </finding>
  </findings>
  <remediation-checklist>
    <item>Optimization priority 1</item>
    <item>Optimization priority 2</item>
  </remediation-checklist>
</response>"""

REFACTOR_PLAN_RESPONSE = """<response>
  <summary>Tech debt assessment (1-2 sentences)</summary>
  <trajectory>increasing|stable|decreasing</trajectory>
  <findings>
    <finding severity="high|medium|low">
      <title>Debt item description</title>
      <location>file:line</location>
      <details>Impact and complexity assessment</details>
      <fix>Refactoring approach</fix>
    </finding>
  </findings>
  <roadmap>
    <phase priority="1|2|3">
      <name>Phase name</name>
      <description>What to accomplish</description>
      <effort>high|medium|low</effort>
    </phase>
  </roadmap>
  <remediation-checklist>
    <item>Immediate action 1</item>
    <item>Immediate action 2</item>
  </remediation-checklist>
</response>"""

TEST_GEN_RESPONSE = """<response>
  <summary>Test generation summary (1-2 sentences)</summary>
  <coverage-improvement>Estimated coverage improvement</coverage-improvement>
  <findings>
    <finding severity="info">
      <title>Untested area</title>
      <location>file:function or class</location>
      <details>Why this needs testing</details>
      <fix>Test approach recommendation</fix>
    </finding>
  </findings>
  <tests>
    <test target="function or class name">
      <type>unit|integration|edge-case</type>
      <description>What this test verifies</description>
      <code><![CDATA[
def test_example():
    # Test code here
    pass
]]></code>
    </test>
  </tests>
  <remediation-checklist>
    <item>Test to add first</item>
    <item>Test to add second</item>
  </remediation-checklist>
</response>"""

DOC_GEN_RESPONSE = """<response>
  <summary>Documentation summary (1-2 sentences)</summary>
  <sections>
    <section name="Section Title">
      <content>Section content in markdown</content>
    </section>
  </sections>
  <findings>
    <finding severity="info">
      <title>Documentation gap or improvement</title>
      <details>What needs documentation</details>
    </finding>
  </findings>
  <remediation-checklist>
    <item>Documentation improvement 1</item>
    <item>Documentation improvement 2</item>
  </remediation-checklist>
</response>"""

RELEASE_PREP_RESPONSE = """<response>
  <summary>Release readiness assessment (1-2 sentences)</summary>
  <verdict>approved|blocked|needs-review</verdict>
  <confidence>high|medium|low</confidence>
  <findings>
    <finding severity="blocker|warning|info">
      <title>Issue title</title>
      <location>Component or area</location>
      <details>Description of the issue</details>
      <fix>Required action before release</fix>
    </finding>
  </findings>
  <checklist>
    <item status="pass|fail|skip">Check description</item>
  </checklist>
  <remediation-checklist>
    <item>Pre-release action 1</item>
    <item>Pre-release action 2</item>
  </remediation-checklist>
</response>"""

DEPENDENCY_CHECK_RESPONSE = """<response>
  <summary>Dependency security assessment (1-2 sentences)</summary>
  <risk-level>critical|high|medium|low</risk-level>
  <risk-score>0-100</risk-score>
  <findings>
    <finding severity="critical|high|medium|low">
      <title>Vulnerability or issue</title>
      <location>package@version</location>
      <details>CVE or issue description</details>
      <fix>Upgrade or mitigation recommendation</fix>
    </finding>
  </findings>
  <remediation-checklist>
    <item>Upgrade package X to version Y</item>
    <item>Review dependency Z</item>
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
    "perf-audit": XmlPromptTemplate(
        name="perf-audit",
        schema_version="1.0",
        response_format=PERF_AUDIT_RESPONSE,
    ),
    "refactor-plan": XmlPromptTemplate(
        name="refactor-plan",
        schema_version="1.0",
        response_format=REFACTOR_PLAN_RESPONSE,
    ),
    "test-gen": XmlPromptTemplate(
        name="test-gen",
        schema_version="1.0",
        response_format=TEST_GEN_RESPONSE,
    ),
    "doc-gen": XmlPromptTemplate(
        name="doc-gen",
        schema_version="1.0",
        response_format=DOC_GEN_RESPONSE,
    ),
    "release-prep": XmlPromptTemplate(
        name="release-prep",
        schema_version="1.0",
        response_format=RELEASE_PREP_RESPONSE,
    ),
    "dependency-check": XmlPromptTemplate(
        name="dependency-check",
        schema_version="1.0",
        response_format=DEPENDENCY_CHECK_RESPONSE,
    ),
}


def get_template(name: str) -> XmlPromptTemplate | None:
    """Get a built-in template by name.

    Args:
        name: Template name (e.g., "security-audit", "code-review").

    Returns:
        XmlPromptTemplate if found, None otherwise.

    """
    return BUILTIN_TEMPLATES.get(name)


def list_templates() -> list[str]:
    """List all available built-in template names.

    Returns:
        List of template names.

    """
    return list(BUILTIN_TEMPLATES.keys())


def register_template(name: str, template: XmlPromptTemplate) -> None:
    """Register a custom template.

    Args:
        name: Template name for lookup.
        template: XmlPromptTemplate instance.

    """
    BUILTIN_TEMPLATES[name] = template
