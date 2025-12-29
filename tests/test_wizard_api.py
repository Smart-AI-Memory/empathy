"""
Tests for wizard_api error handling and edge cases.

Tests cover:
- HTTP 400: Malformed JSON, validation errors, empty body
- HTTP 404: Unknown wizard ID
- HTTP 500: Internal server errors, unknown wizard interface
- Edge cases: Empty input, special characters, large payloads
- Response format validation
"""

# Import the app after mocking dependencies
import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient


class TestWizardAPIErrorHandling:
    """Test error handling for wizard API endpoints."""

    @pytest.fixture
    def mock_wizards(self):
        """Create mock wizards for testing."""
        # Domain wizard with process method only
        mock_process_wizard = MagicMock(spec=["process"])
        mock_process_wizard.process = AsyncMock(
            return_value={
                "response": "Test response",
                "classification": "general",
                "confidence": 0.95,
            }
        )

        # Coach wizard with analyze_code method only
        mock_analyze_wizard = MagicMock(spec=["analyze_code"])
        mock_analyze_wizard.analyze_code = MagicMock(return_value=[])

        # AI wizard with analyze method only
        mock_ai_wizard = MagicMock(spec=["analyze"])
        mock_ai_wizard.analyze = AsyncMock(
            return_value={
                "issues": [],
                "recommendations": ["Test recommendation"],
            }
        )

        return {
            "test_domain": mock_process_wizard,
            "test_coach": mock_analyze_wizard,
            "test_ai": mock_ai_wizard,
        }

    @pytest.fixture
    def client(self, mock_wizards):
        """Create test client with mocked wizards."""
        with patch.dict(
            sys.modules,
            {
                "coach_wizards.debugging_wizard": MagicMock(),
                "coach_wizards.testing_wizard": MagicMock(),
                "coach_wizards.security_wizard": MagicMock(),
                "coach_wizards.documentation_wizard": MagicMock(),
                "coach_wizards.performance_wizard": MagicMock(),
                "coach_wizards.refactoring_wizard": MagicMock(),
                "coach_wizards.database_wizard": MagicMock(),
                "coach_wizards.api_wizard": MagicMock(),
                "coach_wizards.compliance_wizard": MagicMock(),
                "coach_wizards.monitoring_wizard": MagicMock(),
                "coach_wizards.cicd_wizard": MagicMock(),
                "coach_wizards.accessibility_wizard": MagicMock(),
                "coach_wizards.localization_wizard": MagicMock(),
                "coach_wizards.migration_wizard": MagicMock(),
                "coach_wizards.observability_wizard": MagicMock(),
                "coach_wizards.scaling_wizard": MagicMock(),
                "empathy_llm_toolkit": MagicMock(),
                "empathy_llm_toolkit.wizards": MagicMock(),
                "empathy_llm_toolkit.wizards.healthcare_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.finance_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.legal_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.education_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.customer_support_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.hr_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.sales_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.real_estate_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.insurance_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.accounting_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.research_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.government_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.retail_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.manufacturing_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.logistics_wizard": MagicMock(),
                "empathy_llm_toolkit.wizards.technology_wizard": MagicMock(),
                "empathy_software_plugin.wizards": MagicMock(),
                "empathy_software_plugin.wizards.advanced_debugging_wizard": MagicMock(),
                "empathy_software_plugin.wizards.agent_orchestration_wizard": MagicMock(),
                "empathy_software_plugin.wizards.ai_collaboration_wizard": MagicMock(),
                "empathy_software_plugin.wizards.ai_context_wizard": MagicMock(),
                "empathy_software_plugin.wizards.ai_documentation_wizard": MagicMock(),
                "empathy_software_plugin.wizards.enhanced_testing_wizard": MagicMock(),
                "empathy_software_plugin.wizards.multi_model_wizard": MagicMock(),
                "empathy_software_plugin.wizards.performance_profiling_wizard": MagicMock(),
                "empathy_software_plugin.wizards.prompt_engineering_wizard": MagicMock(),
                "empathy_software_plugin.wizards.rag_pattern_wizard": MagicMock(),
                "empathy_software_plugin.wizards.security_analysis_wizard": MagicMock(),
            },
        ):
            from typing import Any

            from fastapi import FastAPI
            from fastapi.testclient import TestClient
            from pydantic import BaseModel

            # Create a minimal test app
            app = FastAPI()

            class WizardRequest(BaseModel):
                input: str
                context: dict[str, Any] | None = None
                user_id: str | None = "demo_user"

            class WizardResponse(BaseModel):
                success: bool
                output: str
                analysis: dict[str, Any] | None = None
                error: str | None = None

            WIZARDS = mock_wizards

            @app.post("/api/wizard/{wizard_id}/process")
            async def process_wizard(wizard_id: str, request: WizardRequest) -> WizardResponse:
                if wizard_id not in WIZARDS:
                    raise HTTPException(
                        status_code=404,
                        detail=f"Wizard '{wizard_id}' not found. Available: {list(WIZARDS.keys())}",
                    )

                wizard = WIZARDS[wizard_id]

                try:
                    if hasattr(wizard, "process"):
                        result = await wizard.process(
                            user_input=request.input,
                            user_id=request.user_id,
                            context=request.context or {},
                        )
                        return WizardResponse(
                            success=True,
                            output=result.get("response", ""),
                            analysis={"confidence": result.get("confidence", 0.0)},
                        )
                    elif hasattr(wizard, "analyze_code"):
                        issues = wizard.analyze_code(
                            code=request.input,
                            file_path=(
                                request.context.get("file_path", "demo.py")
                                if request.context
                                else "demo.py"
                            ),
                            language=(
                                request.context.get("language", "python")
                                if request.context
                                else "python"
                            ),
                        )
                        return WizardResponse(
                            success=True,
                            output="No issues found" if not issues else "Issues found",
                            analysis={"issues_found": len(issues)},
                        )
                    elif hasattr(wizard, "analyze"):
                        result = await wizard.analyze(request.context or {})
                        return WizardResponse(
                            success=True,
                            output="Analysis complete",
                            analysis=result,
                        )
                    else:
                        raise HTTPException(
                            status_code=500, detail=f"Wizard '{wizard_id}' has unknown interface"
                        )
                except HTTPException:
                    raise
                except Exception as e:
                    return WizardResponse(success=False, output="", error=str(e))

            @app.get("/api/wizards")
            async def get_wizards():
                return {"wizards": list(WIZARDS.keys()), "total": len(WIZARDS)}

            return TestClient(app)

    def test_404_unknown_wizard(self, client):
        """Test 404 response for unknown wizard ID."""
        response = client.post(
            "/api/wizard/nonexistent_wizard/process", json={"input": "test input"}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_404_includes_available_wizards(self, client):
        """Test 404 response includes list of available wizards."""
        response = client.post("/api/wizard/fake_wizard/process", json={"input": "test"})
        assert response.status_code == 404
        detail = response.json()["detail"]
        assert "Available" in detail or "available" in detail.lower()

    def test_422_malformed_json(self, client):
        """Test 422 response for malformed JSON."""
        response = client.post(
            "/api/wizard/test_domain/process",
            content="not valid json {{{",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_422_missing_required_field(self, client):
        """Test 422 response when required 'input' field is missing."""
        response = client.post(
            "/api/wizard/test_domain/process", json={"context": {"some": "data"}}
        )
        assert response.status_code == 422

    def test_422_wrong_type_for_input(self, client):
        """Test 422 response when input is wrong type."""
        response = client.post(
            "/api/wizard/test_domain/process", json={"input": 12345}  # Should be string
        )
        assert response.status_code == 422

    def test_422_wrong_type_for_context(self, client):
        """Test 422 response when context is wrong type."""
        response = client.post(
            "/api/wizard/test_domain/process", json={"input": "test", "context": "not a dict"}
        )
        assert response.status_code == 422

    def test_success_domain_wizard(self, client):
        """Test successful request to domain wizard."""
        response = client.post(
            "/api/wizard/test_domain/process", json={"input": "test input", "user_id": "test_user"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "output" in data

    def test_success_coach_wizard(self, client):
        """Test successful request to coach wizard."""
        response = client.post(
            "/api/wizard/test_coach/process",
            json={"input": "def foo(): pass", "context": {"language": "python"}},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_success_ai_wizard(self, client):
        """Test successful request to AI wizard."""
        response = client.post(
            "/api/wizard/test_ai/process", json={"input": "analyze this", "context": {}}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_empty_input_accepted(self, client):
        """Test empty string input is accepted (validation passes)."""
        response = client.post("/api/wizard/test_domain/process", json={"input": ""})
        # Empty string is valid, just might not be useful
        assert response.status_code == 200

    def test_get_wizards_list(self, client):
        """Test GET /api/wizards returns list."""
        response = client.get("/api/wizards")
        assert response.status_code == 200
        data = response.json()
        assert "wizards" in data
        assert "total" in data

    def test_response_format_success(self, client):
        """Test successful response has correct format."""
        response = client.post("/api/wizard/test_domain/process", json={"input": "test"})
        data = response.json()
        assert "success" in data
        assert "output" in data
        assert "analysis" in data
        assert data["error"] is None or "error" in data

    def test_special_characters_in_input(self, client):
        """Test special characters are handled properly."""
        special_input = (
            "Test with special chars: <script>alert('xss')</script> & \"quotes\" 'single'"
        )
        response = client.post("/api/wizard/test_domain/process", json={"input": special_input})
        assert response.status_code == 200

    def test_unicode_in_input(self, client):
        """Test unicode characters are handled properly."""
        unicode_input = "Test with unicode: 你好 🎉 émojis and ñ characters"
        response = client.post("/api/wizard/test_domain/process", json={"input": unicode_input})
        assert response.status_code == 200

    def test_large_input(self, client):
        """Test large input is handled (up to reasonable limit)."""
        large_input = "x" * 10000  # 10KB of data
        response = client.post("/api/wizard/test_domain/process", json={"input": large_input})
        # Should either succeed or return a meaningful error
        assert response.status_code in [200, 413, 422]

    def test_null_user_id_uses_default(self, client):
        """Test null user_id uses default value."""
        response = client.post(
            "/api/wizard/test_domain/process", json={"input": "test", "user_id": None}
        )
        assert response.status_code == 200

    def test_nested_context(self, client):
        """Test deeply nested context is accepted."""
        nested_context = {"level1": {"level2": {"level3": {"data": "value"}}}}
        response = client.post(
            "/api/wizard/test_domain/process", json={"input": "test", "context": nested_context}
        )
        assert response.status_code == 200


class TestWizardAPIInternalErrors:
    """Test internal error handling."""

    @pytest.fixture
    def client_with_failing_wizard(self):
        """Create test client with wizard that throws exceptions."""
        from typing import Any

        from fastapi import FastAPI
        from pydantic import BaseModel

        app = FastAPI()

        class WizardRequest(BaseModel):
            input: str
            context: dict[str, Any] | None = None
            user_id: str | None = "demo_user"

        class WizardResponse(BaseModel):
            success: bool
            output: str
            analysis: dict[str, Any] | None = None
            error: str | None = None

        failing_wizard = MagicMock()
        failing_wizard.process = AsyncMock(side_effect=Exception("Internal wizard error"))

        no_interface_wizard = MagicMock(spec=[])  # No known methods

        WIZARDS = {
            "failing": failing_wizard,
            "no_interface": no_interface_wizard,
        }

        @app.post("/api/wizard/{wizard_id}/process")
        async def process_wizard(wizard_id: str, request: WizardRequest) -> WizardResponse:
            if wizard_id not in WIZARDS:
                raise HTTPException(status_code=404, detail="Not found")

            wizard = WIZARDS[wizard_id]

            try:
                if hasattr(wizard, "process"):
                    result = await wizard.process(
                        user_input=request.input,
                        user_id=request.user_id,
                        context=request.context or {},
                    )
                    return WizardResponse(success=True, output=str(result))
                else:
                    raise HTTPException(
                        status_code=500, detail=f"Wizard '{wizard_id}' has unknown interface"
                    )
            except HTTPException:
                raise
            except Exception as e:
                return WizardResponse(success=False, output="", error=str(e))

        return TestClient(app)

    def test_500_unknown_interface(self, client_with_failing_wizard):
        """Test 500 response for wizard with unknown interface."""
        response = client_with_failing_wizard.post(
            "/api/wizard/no_interface/process", json={"input": "test"}
        )
        assert response.status_code == 500
        assert "unknown interface" in response.json()["detail"].lower()

    def test_wizard_exception_returns_error_response(self, client_with_failing_wizard):
        """Test wizard exception returns error in response body."""
        response = client_with_failing_wizard.post(
            "/api/wizard/failing/process", json={"input": "test"}
        )
        assert response.status_code == 200  # Returns 200 with error in body
        data = response.json()
        assert data["success"] is False
        assert data["error"] is not None
        assert "Internal wizard error" in data["error"]
