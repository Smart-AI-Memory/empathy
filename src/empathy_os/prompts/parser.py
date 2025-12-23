"""
XML Response Parser

Parses structured XML responses from LLMs for dashboard display
and workflow automation.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Any

import defusedxml.ElementTree as DefusedET


@dataclass
class Finding:
    """
    Structured finding from XML response.

    Represents a single issue, vulnerability, or code review comment
    extracted from an LLM response.
    """

    severity: str  # critical, high, medium, low, info
    title: str
    location: str | None = None
    details: str = ""
    fix: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "severity": self.severity,
            "title": self.title,
            "location": self.location,
            "details": self.details,
            "fix": self.fix,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Finding:
        """Create Finding from dictionary."""
        return cls(
            severity=data.get("severity", "medium"),
            title=data.get("title", ""),
            location=data.get("location"),
            details=data.get("details", ""),
            fix=data.get("fix", ""),
        )


@dataclass
class ParsedResponse:
    """
    Result of parsing an XML response.

    Contains extracted structured data or fallback raw text
    if parsing fails.
    """

    success: bool
    raw: str
    summary: str | None = None
    findings: list[Finding] = field(default_factory=list)
    checklist: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "raw": self.raw,
            "summary": self.summary,
            "findings": [f.to_dict() for f in self.findings],
            "checklist": self.checklist,
            "errors": self.errors,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ParsedResponse:
        """Create ParsedResponse from dictionary."""
        findings = [Finding.from_dict(f) for f in data.get("findings", [])]
        return cls(
            success=data.get("success", False),
            raw=data.get("raw", ""),
            summary=data.get("summary"),
            findings=findings,
            checklist=data.get("checklist", []),
            errors=data.get("errors", []),
            extra=data.get("extra", {}),
        )

    @classmethod
    def from_raw(cls, raw: str, errors: list[str] | None = None) -> ParsedResponse:
        """Create a fallback ParsedResponse from raw text."""
        return cls(
            success=False,
            raw=raw,
            summary=raw[:500] if raw else None,
            errors=errors or ["No XML content found"],
        )


class XmlResponseParser:
    """
    Parse LLM responses containing XML.

    Extracts structured data from XML-formatted responses while
    gracefully handling malformed or missing XML.
    """

    def __init__(self, fallback_on_error: bool = True):
        """
        Initialize the parser.

        Args:
            fallback_on_error: If True, return raw text on parse failure
                              instead of raising an exception.
        """
        self.fallback_on_error = fallback_on_error

    def parse(self, response: str) -> ParsedResponse:
        """
        Parse XML response, with graceful fallback.

        Args:
            response: The LLM response text, potentially containing XML.

        Returns:
            ParsedResponse with extracted data or fallback raw text.
        """
        if not response:
            return ParsedResponse.from_raw("", ["Empty response"])

        # Extract XML from response (may be wrapped in markdown)
        xml_content = self._extract_xml(response)

        if not xml_content:
            if self.fallback_on_error:
                return ParsedResponse.from_raw(response, ["No XML content found"])
            raise ValueError("No XML content in response")

        try:
            # Use defusedxml for safe XML parsing (prevents XXE attacks)
            root = DefusedET.fromstring(xml_content)

            return ParsedResponse(
                success=True,
                raw=response,
                summary=self._extract_text(root, "summary"),
                findings=self._extract_findings(root),
                checklist=self._extract_checklist(root),
                extra=self._extract_extra(root),
            )
        except ET.ParseError as e:
            if self.fallback_on_error:
                return ParsedResponse.from_raw(response, [f"XML parse error: {e}"])
            raise

    def _extract_xml(self, response: str) -> str | None:
        """
        Extract XML content from response.

        Handles various formats:
        - Direct XML
        - XML in markdown code blocks
        - XML mixed with other text
        """
        # Handle markdown code blocks with xml tag
        xml_block = re.search(r"```xml\s*(.*?)\s*```", response, re.DOTALL)
        if xml_block:
            return xml_block.group(1).strip()

        # Handle generic markdown code blocks
        code_block = re.search(r"```\s*(.*?)\s*```", response, re.DOTALL)
        if code_block:
            content = code_block.group(1).strip()
            if content.startswith("<"):
                return content

        # Try to find <response> tags
        response_match = re.search(r"<response\b[^>]*>.*?</response>", response, re.DOTALL)
        if response_match:
            return response_match.group(0)

        # Try to find any root XML element
        xml_match = re.search(r"<(\w+)\b[^>]*>.*?</\1>", response, re.DOTALL)
        if xml_match:
            return xml_match.group(0)

        # If response itself looks like XML
        stripped = response.strip()
        if stripped.startswith("<") and stripped.endswith(">"):
            return stripped

        return None

    def _extract_text(self, root: ET.Element, tag: str) -> str | None:
        """Extract text content from a tag."""
        element = root.find(f".//{tag}")
        if element is not None and element.text:
            return element.text.strip()
        return None

    def _extract_findings(self, root: ET.Element) -> list[Finding]:
        """Extract findings from parsed XML."""
        findings = []

        # Look for findings in various possible locations
        for finding_el in root.findall(".//finding"):
            findings.append(self._parse_finding(finding_el))

        # Also check for <item> inside <findings>
        findings_container = root.find(".//findings")
        if findings_container is not None:
            for item_el in findings_container.findall("item"):
                findings.append(self._parse_finding(item_el))

        return findings

    def _parse_finding(self, element: ET.Element) -> Finding:
        """Parse a single finding element."""
        title = self._extract_text(element, "title") or element.get("title") or ""
        return Finding(
            severity=element.get("severity") or "medium",
            title=title,
            location=self._extract_text(element, "location"),
            details=self._extract_text(element, "details") or "",
            fix=self._extract_text(element, "fix") or "",
        )

    def _extract_checklist(self, root: ET.Element) -> list[str]:
        """Extract checklist items from parsed XML."""
        items = []

        # Look for remediation-checklist
        checklist = root.find(".//remediation-checklist")
        if checklist is not None:
            for item in checklist.findall("item"):
                if item.text:
                    items.append(item.text.strip())

        # Also check for generic checklist
        if not items:
            checklist = root.find(".//checklist")
            if checklist is not None:
                for item in checklist.findall("item"):
                    if item.text:
                        items.append(item.text.strip())

        return items

    def _extract_extra(self, root: ET.Element) -> dict[str, Any]:
        """Extract additional fields from the response."""
        extra: dict[str, Any] = {}

        # Extract verdict (for code review)
        verdict = self._extract_text(root, "verdict")
        if verdict:
            extra["verdict"] = verdict

        # Extract confidence (for research)
        confidence = root.find(".//confidence")
        if confidence is not None:
            extra["confidence"] = {
                "level": confidence.get("level", "medium"),
                "reasoning": confidence.text.strip() if confidence.text else "",
            }

        # Extract key insights (for research)
        insights = root.find(".//key-insights")
        if insights is not None:
            extra["key_insights"] = [i.text.strip() for i in insights.findall("insight") if i.text]

        # Extract suggestions (for code review)
        suggestions = root.find(".//suggestions")
        if suggestions is not None:
            extra["suggestions"] = [
                s.text.strip() for s in suggestions.findall("suggestion") if s.text
            ]

        return extra
