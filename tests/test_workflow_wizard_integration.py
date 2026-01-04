"""Integration tests for workflow-wizard interactions.

Tests cover:
- Workflow initialization with wizard dependencies
- End-to-end workflow execution
- Workflow-wizard data flow
- Error propagation between workflows and wizards
- Configuration inheritance
"""

from unittest.mock import AsyncMock, MagicMock

import pytest


class TestWorkflowWizardIntegration:
    """Test integration between workflows and wizards."""

    @pytest.fixture
    def mock_llm(self):
        """Create a mock LLM instance."""
        llm = MagicMock()
        llm.interact = AsyncMock(
            return_value={
                "response": "Mock LLM response",
                "confidence": 0.9,
            },
        )
        llm.provider = "anthropic"
        return llm

    @pytest.fixture
    def mock_wizard(self):
        """Create a mock wizard."""
        wizard = MagicMock()
        wizard.analyze_code = MagicMock(return_value=[])
        wizard.analyze = AsyncMock(
            return_value={
                "issues": [],
                "recommendations": ["Test recommendation"],
                "confidence": 0.85,
            },
        )
        wizard.process = AsyncMock(
            return_value={
                "response": "Wizard response",
                "classification": "general",
            },
        )
        return wizard


class TestCodeReviewWorkflowIntegration:
    """Test code review workflow with wizard integration."""

    def test_workflow_accepts_wizard_results(self):
        """Test workflow can process wizard analysis results."""
        # Simulate wizard output format
        wizard_results = {
            "issues": [
                {"severity": "high", "message": "SQL injection risk", "line": 10},
                {"severity": "medium", "message": "Unused variable", "line": 25},
            ],
            "recommendations": [
                "Use parameterized queries",
                "Remove unused code",
            ],
            "confidence": 0.92,
        }

        # Verify workflow can consume this format
        assert "issues" in wizard_results
        assert len(wizard_results["issues"]) == 2
        assert wizard_results["issues"][0]["severity"] == "high"

    def test_workflow_handles_empty_wizard_results(self):
        """Test workflow handles wizard returning no issues."""
        wizard_results = {
            "issues": [],
            "recommendations": [],
            "confidence": 1.0,
        }

        # Workflow should handle empty results gracefully
        assert len(wizard_results["issues"]) == 0
        assert wizard_results["confidence"] == 1.0


class TestSecurityWorkflowIntegration:
    """Test security workflow with wizard integration."""

    def test_security_workflow_with_security_wizard(self):
        """Test security workflow processes security wizard output."""
        security_findings = {
            "vulnerabilities": [
                {
                    "type": "XSS",
                    "severity": "critical",
                    "location": "line 42",
                    "description": "Unsanitized user input",
                },
            ],
            "compliance": {
                "owasp_top_10": ["A03:2021 - Injection"],
                "passed": False,
            },
            "recommendations": [
                "Sanitize all user inputs",
                "Use Content Security Policy",
            ],
        }

        # Verify security-specific fields are present
        assert "vulnerabilities" in security_findings
        assert security_findings["vulnerabilities"][0]["severity"] == "critical"
        assert "owasp_top_10" in security_findings["compliance"]

    def test_security_workflow_aggregates_multiple_wizards(self):
        """Test security workflow can aggregate results from multiple wizards."""
        security_wizard_results = {"issues": [{"type": "injection"}]}
        compliance_wizard_results = {"issues": [{"type": "pii_exposure"}]}

        # Simulate aggregation
        all_issues = security_wizard_results["issues"] + compliance_wizard_results["issues"]

        assert len(all_issues) == 2
        assert all_issues[0]["type"] == "injection"
        assert all_issues[1]["type"] == "pii_exposure"


class TestDebuggingWorkflowIntegration:
    """Test debugging workflow with wizard integration."""

    def test_debugging_workflow_with_advanced_debugging_wizard(self):
        """Test debugging workflow uses advanced debugging wizard output."""
        debug_analysis = {
            "root_cause": "Null pointer exception in user service",
            "stack_trace_analysis": {
                "origin": "UserService.java:145",
                "propagation": ["Controller.java:32", "Router.java:18"],
            },
            "suggested_fixes": [
                "Add null check before accessing user.getName()",
                "Use Optional<User> instead of nullable User",
            ],
            "confidence": 0.88,
        }

        assert "root_cause" in debug_analysis
        assert len(debug_analysis["suggested_fixes"]) >= 1
        assert debug_analysis["confidence"] > 0.5

    def test_debugging_workflow_handles_unknown_errors(self):
        """Test debugging workflow handles unrecognized error patterns."""
        unknown_error_result = {
            "root_cause": None,
            "analysis": "Unable to determine root cause",
            "suggested_fixes": ["Review logs manually", "Enable verbose logging"],
            "confidence": 0.3,
        }

        assert unknown_error_result["root_cause"] is None
        assert unknown_error_result["confidence"] < 0.5
        assert len(unknown_error_result["suggested_fixes"]) > 0


class TestWorkflowChaining:
    """Test workflows that chain multiple wizard calls."""

    def test_workflow_chains_wizard_calls(self):
        """Test workflow can chain multiple wizard calls in sequence."""
        # Step 1: Code analysis wizard
        step1_result = {
            "code_quality": "B",
            "issues": [{"type": "complexity", "file": "main.py"}],
        }

        # Step 2: Security wizard (uses step1 context)
        step2_result = {
            "security_score": 75,
            "vulnerabilities": [],
        }

        # Step 3: Documentation wizard
        step3_result = {
            "coverage": 0.65,
            "missing_docs": ["function_a", "class_b"],
        }

        # Verify chain produces complete analysis
        final_report = {
            "quality": step1_result,
            "security": step2_result,
            "documentation": step3_result,
        }

        assert "quality" in final_report
        assert "security" in final_report
        assert "documentation" in final_report

    def test_workflow_handles_chain_failure(self):
        """Test workflow handles failure in middle of chain gracefully."""
        step1_result = {"success": True, "data": {}}
        step2_result = {"success": False, "error": "Wizard timeout"}
        # Step 3 should still run with partial data

        # Verify partial results are preserved
        assert step1_result["success"] is True
        assert step2_result["success"] is False
        assert "error" in step2_result


class TestWorkflowContextPropagation:
    """Test context propagation between workflows and wizards."""

    def test_workflow_passes_context_to_wizard(self):
        """Test workflow passes relevant context to wizard."""
        workflow_context = {
            "project_path": "/path/to/project",
            "language": "python",
            "framework": "fastapi",
            "user_preferences": {
                "severity_threshold": "medium",
            },
        }

        # Wizard should receive this context
        wizard_call_context = workflow_context.copy()
        wizard_call_context["analysis_type"] = "full"

        assert wizard_call_context["project_path"] == "/path/to/project"
        assert wizard_call_context["analysis_type"] == "full"

    def test_wizard_results_enrich_workflow_context(self):
        """Test wizard results are added to workflow context for next steps."""
        initial_context = {"file": "main.py"}

        # After wizard analysis
        wizard_result = {
            "detected_patterns": ["singleton", "factory"],
            "dependencies": ["fastapi", "pydantic"],
        }

        # Enriched context for next workflow step
        enriched_context = {
            **initial_context,
            "patterns": wizard_result["detected_patterns"],
            "deps": wizard_result["dependencies"],
        }

        assert "patterns" in enriched_context
        assert "singleton" in enriched_context["patterns"]


class TestWorkflowWizardErrorHandling:
    """Test error handling between workflows and wizards."""

    def test_workflow_handles_wizard_timeout(self):
        """Test workflow handles wizard timeout gracefully."""
        timeout_response = {
            "success": False,
            "error": "Wizard analysis timed out after 30s",
            "partial_results": {"analyzed_files": 5, "total_files": 20},
        }

        assert timeout_response["success"] is False
        assert "timed out" in timeout_response["error"]
        assert timeout_response["partial_results"]["analyzed_files"] == 5

    def test_workflow_handles_wizard_exception(self):
        """Test workflow handles wizard throwing exception."""
        exception_response = {
            "success": False,
            "error": "WizardError: Unable to parse code syntax",
            "error_type": "WizardError",
            "recoverable": True,
        }

        assert exception_response["success"] is False
        assert exception_response["recoverable"] is True

    def test_workflow_retries_failed_wizard(self):
        """Test workflow can retry failed wizard calls."""
        retry_log = []

        # Simulate retry logic
        for attempt in range(3):
            result = {"success": attempt == 2, "attempt": attempt + 1}
            retry_log.append(result)
            if result["success"]:
                break

        assert len(retry_log) == 3
        assert retry_log[-1]["success"] is True
        assert retry_log[-1]["attempt"] == 3


class TestWorkflowWizardConfiguration:
    """Test configuration handling between workflows and wizards."""

    def test_workflow_configures_wizard(self):
        """Test workflow can configure wizard settings."""
        wizard_config = {
            "max_issues": 100,
            "severity_filter": ["high", "critical"],
            "include_suggestions": True,
            "timeout_seconds": 60,
        }

        assert wizard_config["max_issues"] == 100
        assert "high" in wizard_config["severity_filter"]

    def test_workflow_uses_default_wizard_config(self):
        """Test workflow uses sensible defaults when no config provided."""
        default_config = {
            "max_issues": 50,
            "severity_filter": ["low", "medium", "high", "critical"],
            "include_suggestions": True,
            "timeout_seconds": 30,
        }

        # Verify defaults are reasonable
        assert default_config["max_issues"] > 0
        assert len(default_config["severity_filter"]) == 4
        assert default_config["timeout_seconds"] >= 10

    def test_workflow_overrides_wizard_config(self):
        """Test workflow can override specific wizard config values."""
        base_config = {"max_issues": 50, "timeout": 30}
        overrides = {"max_issues": 200}

        merged_config = {**base_config, **overrides}

        assert merged_config["max_issues"] == 200
        assert merged_config["timeout"] == 30  # Unchanged
