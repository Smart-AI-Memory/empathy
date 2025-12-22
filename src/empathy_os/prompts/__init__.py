"""
XML-Enhanced Prompt System for Empathy Framework

Provides structured XML-based prompts for consistent LLM interactions
and response parsing across workflows.

Usage:
    from empathy_os.prompts import (
        XmlPromptConfig,
        PromptContext,
        XmlPromptTemplate,
        XmlResponseParser,
        get_template,
    )

    # Create a context
    context = PromptContext.for_security_audit(code="...")

    # Get a built-in template
    template = get_template("security-audit")

    # Render the prompt
    prompt = template.render(context)

    # Parse the response
    parser = XmlResponseParser()
    result = parser.parse(llm_response)

    if result.success:
        print(result.summary)
        for finding in result.findings:
            print(f"{finding.severity}: {finding.title}")

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from .config import XmlPromptConfig
from .context import PromptContext
from .parser import Finding, ParsedResponse, XmlResponseParser
from .registry import BUILTIN_TEMPLATES, get_template, list_templates, register_template
from .templates import PlainTextPromptTemplate, PromptTemplate, XmlPromptTemplate

__all__ = [
    # Config
    "XmlPromptConfig",
    # Context
    "PromptContext",
    # Templates
    "PromptTemplate",
    "PlainTextPromptTemplate",
    "XmlPromptTemplate",
    # Parser
    "XmlResponseParser",
    "ParsedResponse",
    "Finding",
    # Registry
    "BUILTIN_TEMPLATES",
    "get_template",
    "list_templates",
    "register_template",
]
