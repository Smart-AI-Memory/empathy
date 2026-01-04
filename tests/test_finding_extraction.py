"""Test finding extraction from LLM responses.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import pytest

from empathy_os.workflows.base import BaseWorkflow, ModelTier


class DummyWorkflow(BaseWorkflow):
    """Minimal concrete workflow for testing."""

    name = "test-workflow"
    description = "Test workflow"
    stages = ["test"]
    tier_map = {"test": ModelTier.CAPABLE}

    async def run_stage(self, stage_name, tier, input_data):
        """Dummy implementation."""
        return {}, 0, 0


class TestFindingExtraction:
    """Test the finding extraction methods added to BaseWorkflow."""

    def setup_method(self):
        """Create a minimal workflow instance for testing."""
        self.workflow = DummyWorkflow()

    def test_extract_findings_from_xml_response(self):
        """Test extraction from XML-formatted LLM response."""
        xml_response = """
<response>
    <summary>Found 2 security issues</summary>
    <findings>
        <finding>
            <severity>high</severity>
            <title>SQL Injection Vulnerability</title>
            <location>src/auth/login.py:42</location>
            <details>User input directly concatenated into SQL query</details>
            <fix>Use parameterized queries instead</fix>
        </finding>
        <finding>
            <severity>medium</severity>
            <title>Missing error handling</title>
            <location>src/api/users.py:105</location>
            <details>Exception not caught in database call</details>
            <fix>Add try/except block</fix>
        </finding>
    </findings>
</response>
        """

        findings = self.workflow._extract_findings_from_response(
            response=xml_response,
            files_changed=["src/auth/login.py", "src/api/users.py"],
        )

        assert len(findings) >= 2
        assert findings[0]["severity"] in ["high", "medium"]
        assert "file" in findings[0]
        assert "line" in findings[0]
        assert findings[0]["line"] > 0

    def test_extract_findings_from_text_response(self):
        """Test extraction from plain text LLM response with file:line patterns."""
        text_response = """
        Code review findings:

        1. src/auth/login.py:42: SQL injection vulnerability found in login handler.
           User input is directly concatenated into SQL query.

        2. src/api/users.py:105: Missing error handling in database call.
           This could cause unhandled exceptions.

        3. tests/test_auth.py:67: Test coverage missing for edge case.
        """

        findings = self.workflow._extract_findings_from_response(
            response=text_response,
            files_changed=["src/auth/login.py", "src/api/users.py", "tests/test_auth.py"],
        )

        assert len(findings) >= 2
        # Check first finding
        assert findings[0]["file"] == "src/auth/login.py"
        assert findings[0]["line"] == 42
        assert (
            "sql" in findings[0]["message"].lower() or "injection" in findings[0]["message"].lower()
        )

    def test_parse_location_string_colon_format(self):
        """Test parsing file:line:col format."""
        file, line, col = self.workflow._parse_location_string("src/auth.py:42:10", ["src/auth.py"])

        assert file == "src/auth.py"
        assert line == 42
        assert col == 10

    def test_parse_location_string_line_in_file(self):
        """Test parsing 'line X in file.py' format."""
        file, line, col = self.workflow._parse_location_string(
            "line 42 in src/auth.py",
            ["src/auth.py"],
        )

        assert file == "src/auth.py"
        assert line == 42
        assert col == 1  # Default column

    def test_infer_severity_critical(self):
        """Test severity inference for critical issues."""
        text = "Critical SQL injection vulnerability allows remote code execution"
        severity = self.workflow._infer_severity(text)

        assert severity == "critical"

    def test_infer_severity_high(self):
        """Test severity inference for high priority issues."""
        text = "High priority security issue: password stored in plaintext"
        severity = self.workflow._infer_severity(text)

        assert severity == "high"

    def test_infer_severity_medium(self):
        """Test severity inference for medium priority issues."""
        text = "Warning: deprecated API usage"
        severity = self.workflow._infer_severity(text)

        assert severity == "medium"

    def test_infer_category_security(self):
        """Test category inference for security issues."""
        text = "SQL injection vulnerability in authentication handler"
        category = self.workflow._infer_category(text)

        assert category == "security"

    def test_infer_category_performance(self):
        """Test category inference for performance issues."""
        text = "Memory leak detected in cache implementation"
        category = self.workflow._infer_category(text)

        assert category == "performance"

    def test_infer_category_maintainability(self):
        """Test category inference for code quality issues."""
        text = "Complex nested logic should be refactored for better readability"
        category = self.workflow._infer_category(text)

        assert category == "maintainability"

    def test_finding_deduplication(self):
        """Test that duplicate findings at same file:line are removed."""
        response = """
        src/auth.py:42: SQL injection found
        src/auth.py:42: Security vulnerability detected
        src/api.py:10: Missing validation
        """

        findings = self.workflow._extract_findings_from_response(
            response=response,
            files_changed=["src/auth.py", "src/api.py"],
        )

        # Should deduplicate the two findings at auth.py:42
        file_line_pairs = [(f["file"], f["line"]) for f in findings]
        assert len(file_line_pairs) == len(set(file_line_pairs))  # All unique


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
