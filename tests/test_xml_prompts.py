"""Tests for XML-Enhanced Prompts System

Tests the core prompt templates, parser, and configuration.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import pytest

from empathy_os.prompts import (
    Finding,
    ParsedResponse,
    PlainTextPromptTemplate,
    PromptContext,
    XmlPromptConfig,
    XmlPromptTemplate,
    XmlResponseParser,
    get_template,
    list_templates,
)


class TestXmlPromptConfig:
    """Tests for XmlPromptConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = XmlPromptConfig()
        assert config.enabled is False
        assert config.schema_version == "1.0"
        assert config.enforce_response_xml is False
        assert config.fallback_on_parse_error is True
        assert config.template_name is None

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "enabled": True,
            "schema_version": "2.0",
            "enforce_response_xml": True,
            "template_name": "security-audit",
        }
        config = XmlPromptConfig.from_dict(data)
        assert config.enabled is True
        assert config.schema_version == "2.0"
        assert config.enforce_response_xml is True
        assert config.template_name == "security-audit"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = XmlPromptConfig(enabled=True, template_name="code-review")
        data = config.to_dict()
        assert data["enabled"] is True
        assert data["template_name"] == "code-review"

    def test_merge_with(self):
        """Test merging configs with precedence."""
        base = XmlPromptConfig(enabled=False, schema_version="1.0")
        override = XmlPromptConfig(enabled=True, template_name="test")
        merged = base.merge_with(override)
        assert merged.enabled is True
        assert merged.template_name == "test"


class TestPromptContext:
    """Tests for PromptContext dataclass."""

    def test_basic_creation(self):
        """Test creating a basic context."""
        context = PromptContext(
            role="security analyst",
            goal="find vulnerabilities",
        )
        assert context.role == "security analyst"
        assert context.goal == "find vulnerabilities"
        assert context.instructions == []

    def test_validation(self):
        """Test context validation."""
        with pytest.raises(ValueError, match="role is required"):
            PromptContext(role="", goal="test")

        with pytest.raises(ValueError, match="goal is required"):
            PromptContext(role="test", goal="")

    def test_for_security_audit(self):
        """Test security audit context factory."""
        context = PromptContext.for_security_audit(
            code="def foo(): pass",
            findings_summary="1 issue found",
            risk_level="high",
        )
        assert context.role == "application security engineer"
        assert "OWASP" in context.instructions[1]
        assert context.input_payload == "def foo(): pass"
        assert context.extra["risk_level"] == "high"

    def test_for_code_review(self):
        """Test code review context factory."""
        context = PromptContext.for_code_review(
            code_or_diff="+ new code",
            input_type="diff",
        )
        assert context.role == "senior staff engineer performing code review"
        assert context.input_type == "diff"

    def test_for_research(self):
        """Test research context factory."""
        context = PromptContext.for_research(
            question="What is the best approach?",
            context="Building a web app",
        )
        assert "research" in context.role.lower()
        assert context.input_type == "question"

    def test_with_extra(self):
        """Test adding extra context."""
        context = PromptContext(role="test", goal="test")
        new_context = context.with_extra(foo="bar", baz=123)
        assert new_context.extra["foo"] == "bar"
        assert new_context.extra["baz"] == 123
        # Original unchanged
        assert "foo" not in context.extra


class TestXmlPromptTemplate:
    """Tests for XML prompt template rendering."""

    def test_basic_render(self):
        """Test basic XML rendering."""
        template = XmlPromptTemplate(name="test")
        context = PromptContext(
            role="tester",
            goal="test the code",
            instructions=["Step 1", "Step 2"],
            constraints=["Be thorough"],
            input_type="code",
            input_payload="print('hello')",
        )
        result = template.render(context)

        assert '<request schema="1.0">' in result
        assert "<role>tester</role>" in result
        assert "<goal>test the code</goal>" in result
        assert "<step>1. Step 1</step>" in result
        assert "<step>2. Step 2</step>" in result
        assert "<rule>Be thorough</rule>" in result
        assert '<input type="code">' in result
        assert "print('hello')" in result

    def test_xml_escaping(self):
        """Test that special characters are escaped."""
        template = XmlPromptTemplate(name="test")
        context = PromptContext(
            role="test & verify",
            goal="check <things>",
            input_type="code",
            input_payload="x < y && z > 0",
        )
        result = template.render(context)

        assert "&amp;" in result
        assert "&lt;things&gt;" in result
        # CDATA content is not escaped
        assert "x < y && z > 0" in result

    def test_cdata_escaping(self):
        """Test CDATA section escaping."""
        template = XmlPromptTemplate(name="test")
        context = PromptContext(
            role="test",
            goal="test",
            input_type="code",
            input_payload="end ]]> tag",
        )
        result = template.render(context)
        # ]]> should be escaped in CDATA
        assert "]]]]><![CDATA[>" in result

    def test_response_format_included(self):
        """Test response format instructions are included."""
        template = XmlPromptTemplate(
            name="test",
            response_format="<response><summary>...</summary></response>",
        )
        context = PromptContext(role="test", goal="test")
        result = template.render(context)

        assert "Please respond using ONLY this XML format" in result
        assert "<summary>...</summary>" in result

    def test_extra_context_rendered(self):
        """Test extra context is rendered as XML."""
        template = XmlPromptTemplate(name="test")
        context = PromptContext(
            role="test",
            goal="test",
            extra={"risk_level": "high", "score": "85"},
        )
        result = template.render(context)

        assert "<context>" in result
        assert "<risk_level>high</risk_level>" in result
        assert "<score>85</score>" in result


class TestPlainTextPromptTemplate:
    """Tests for plain text prompt template."""

    def test_basic_render(self):
        """Test basic plain text rendering."""
        template = PlainTextPromptTemplate(name="test")
        context = PromptContext(
            role="tester",
            goal="test the code",
            instructions=["Step 1", "Step 2"],
            constraints=["Be thorough"],
            input_type="code",
            input_payload="print('hello')",
        )
        result = template.render(context)

        assert "You are a tester." in result
        assert "Goal: test the code" in result
        assert "1. Step 1" in result
        assert "2. Step 2" in result
        assert "- Be thorough" in result
        assert "Input (code):" in result
        assert "print('hello')" in result


class TestXmlResponseParser:
    """Tests for XML response parsing."""

    def test_parse_valid_response(self):
        """Test parsing a valid XML response."""
        parser = XmlResponseParser()
        response = """<response>
            <summary>No critical issues found</summary>
            <findings>
                <finding severity="medium">
                    <title>Missing error handling</title>
                    <location>app.py:42</location>
                    <details>The function lacks try-except</details>
                    <fix>Add error handling</fix>
                </finding>
            </findings>
            <remediation-checklist>
                <item>Add try-except blocks</item>
                <item>Add logging</item>
            </remediation-checklist>
        </response>"""

        result = parser.parse(response)

        assert result.success is True
        assert result.summary == "No critical issues found"
        assert len(result.findings) == 1
        assert result.findings[0].severity == "medium"
        assert result.findings[0].title == "Missing error handling"
        assert result.findings[0].location == "app.py:42"
        assert len(result.checklist) == 2
        assert "Add try-except blocks" in result.checklist

    def test_parse_markdown_wrapped_xml(self):
        """Test parsing XML wrapped in markdown code blocks."""
        parser = XmlResponseParser()
        response = """Here's the analysis:

```xml
<response>
    <summary>Analysis complete</summary>
    <findings></findings>
</response>
```

That's all."""

        result = parser.parse(response)
        assert result.success is True
        assert result.summary == "Analysis complete"

    def test_fallback_on_no_xml(self):
        """Test fallback when no XML is present."""
        parser = XmlResponseParser(fallback_on_error=True)
        response = "This is a plain text response with no XML."

        result = parser.parse(response)
        assert result.success is False
        assert result.raw == response
        assert "No XML content found" in result.errors

    def test_fallback_on_invalid_xml(self):
        """Test fallback on malformed XML with unclosed tags."""
        parser = XmlResponseParser(fallback_on_error=True)
        # Use XML with mismatched tags that will fail to parse
        response = "<response><summary>Broken</notclosed></response>"

        result = parser.parse(response)
        assert result.success is False
        # Should get "XML parse error" since extraction works but parsing fails
        assert len(result.errors) > 0
        assert "XML parse error" in result.errors[0]

    def test_raise_on_error(self):
        """Test raising exception when fallback is disabled."""
        parser = XmlResponseParser(fallback_on_error=False)

        with pytest.raises(ValueError, match="No XML content"):
            parser.parse("plain text")

    def test_empty_response(self):
        """Test handling empty response."""
        parser = XmlResponseParser()
        result = parser.parse("")
        assert result.success is False
        assert "Empty response" in result.errors


class TestFinding:
    """Tests for Finding dataclass."""

    def test_to_dict(self):
        """Test converting finding to dictionary."""
        finding = Finding(
            severity="high",
            title="SQL Injection",
            location="db.py:10",
            details="User input not sanitized",
            fix="Use parameterized queries",
        )
        data = finding.to_dict()
        assert data["severity"] == "high"
        assert data["title"] == "SQL Injection"
        assert data["location"] == "db.py:10"

    def test_from_dict(self):
        """Test creating finding from dictionary."""
        data = {
            "severity": "critical",
            "title": "XSS",
            "location": "template.html:5",
            "details": "Unescaped output",
            "fix": "Use template escaping",
        }
        finding = Finding.from_dict(data)
        assert finding.severity == "critical"
        assert finding.title == "XSS"


class TestParsedResponse:
    """Tests for ParsedResponse dataclass."""

    def test_to_dict(self):
        """Test converting parsed response to dictionary."""
        finding = Finding(severity="low", title="Test")
        response = ParsedResponse(
            success=True,
            raw="<response>...</response>",
            summary="All good",
            findings=[finding],
            checklist=["Item 1"],
        )
        data = response.to_dict()
        assert data["success"] is True
        assert data["summary"] == "All good"
        assert len(data["findings"]) == 1

    def test_from_raw(self):
        """Test creating fallback response."""
        response = ParsedResponse.from_raw("Raw text", ["Error 1"])
        assert response.success is False
        assert response.raw == "Raw text"
        assert "Error 1" in response.errors


class TestBuiltinTemplates:
    """Tests for built-in template registry."""

    def test_list_templates(self):
        """Test listing available templates."""
        templates = list_templates()
        assert "security-audit" in templates
        assert "code-review" in templates
        assert "research" in templates

    def test_get_security_audit_template(self):
        """Test getting security audit template."""
        template = get_template("security-audit")
        assert template is not None
        assert template.name == "security-audit"
        assert template.response_format is not None
        assert "<finding severity=" in template.response_format

    def test_get_code_review_template(self):
        """Test getting code review template."""
        template = get_template("code-review")
        assert template is not None
        assert "<verdict>" in template.response_format

    def test_get_research_template(self):
        """Test getting research template."""
        template = get_template("research")
        assert template is not None
        assert "<key-insights>" in template.response_format

    def test_get_nonexistent_template(self):
        """Test getting a template that doesn't exist."""
        template = get_template("nonexistent")
        assert template is None


class TestIntegration:
    """Integration tests for the full prompt flow."""

    def test_render_and_parse_security_audit(self):
        """Test rendering security audit prompt and parsing response."""
        # Get the template
        template = get_template("security-audit")
        assert template is not None

        # Create context
        context = PromptContext.for_security_audit(
            code="def login(user, password): ...",
            findings_summary="Potential issues detected",
            risk_level="medium",
        )

        # Render prompt
        prompt = template.render(context)
        assert '<request schema="1.0">' in prompt
        assert "application security engineer" in prompt
        assert "OWASP" in prompt

        # Simulate response parsing
        mock_response = """<response>
            <summary>Medium risk: hardcoded credentials detected</summary>
            <findings>
                <finding severity="high">
                    <title>Hardcoded password comparison</title>
                    <location>login:1</location>
                    <details>Password appears to be compared directly</details>
                    <fix>Use secure password hashing</fix>
                </finding>
            </findings>
            <remediation-checklist>
                <item>Implement bcrypt password hashing</item>
                <item>Remove hardcoded credentials</item>
            </remediation-checklist>
        </response>"""

        parser = XmlResponseParser()
        result = parser.parse(mock_response)

        assert result.success is True
        assert "hardcoded" in result.summary.lower()
        assert len(result.findings) == 1
        assert result.findings[0].severity == "high"
        assert len(result.checklist) == 2
