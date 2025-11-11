"""
Wizards API endpoints.
Handles wizard-related requests including listing, info, and invocation.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from services.empathy_service import EmpathyService

router = APIRouter(prefix="/api/wizards", tags=["wizards"])


# Dependency to get service instance
def get_empathy_service() -> EmpathyService:
    """Get EmpathyService instance."""
    return EmpathyService()


class AnalyzeRequest(BaseModel):
    """Request model for code analysis."""

    code: str
    language: str = "python"
    include_metrics: bool = True
    additional_context: dict[str, Any] | None = None


class WizardInfoRequest(BaseModel):
    """Request model for wizard info."""

    wizard_name: str | None = None


@router.get("/")
async def list_wizards(service: EmpathyService = Depends(get_empathy_service)):
    """
    List all available wizards.

    Returns:
        List of available wizards with their details
    """
    result = await service.get_wizard_info()
    return result


@router.get("/{wizard_name}")
async def get_wizard(wizard_name: str, service: EmpathyService = Depends(get_empathy_service)):
    """
    Get information about a specific wizard.

    Args:
        wizard_name: Name of the wizard

    Returns:
        Wizard details
    """
    result = await service.get_wizard_info(wizard_name)
    if not result["success"]:
        raise HTTPException(status_code=404, detail=result.get("error", "Wizard not found"))
    return result


@router.post("/analyze")
async def analyze_code(
    request: AnalyzeRequest, service: EmpathyService = Depends(get_empathy_service)
):
    """
    Analyze code using the Empathy Framework.

    Args:
        request: Analysis request with code and parameters

    Returns:
        Analysis results including issues and recommendations
    """
    try:
        kwargs = request.additional_context or {}
        result = await service.analyze_code(
            code=request.code,
            language=request.language,
            include_metrics=request.include_metrics,
            **kwargs,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}") from e


@router.get("/health")
async def health_check():
    """Health check endpoint for wizards service."""
    return {"status": "healthy", "service": "wizards", "version": "1.0.0"}
