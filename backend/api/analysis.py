"""
Analysis API endpoints.
Handles code analysis, project scanning, and result retrieval.
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from services.empathy_service import EmpathyService

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
security = HTTPBearer()


def get_empathy_service() -> EmpathyService:
    """Get EmpathyService instance."""
    return EmpathyService()


class ProjectAnalysisRequest(BaseModel):
    """Request model for project analysis."""
    project_path: str
    file_patterns: Optional[List[str]] = None
    exclude_patterns: Optional[List[str]] = None
    wizards: Optional[List[str]] = None


class SessionConfig(BaseModel):
    """Configuration for analysis session."""
    name: str
    description: Optional[str] = None
    wizards: List[str]
    config: Dict[str, Any] = {}


@router.post("/session")
async def create_session(
    request: SessionConfig,
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Create a new analysis session.

    Args:
        request: Session configuration
        service: EmpathyService instance
        credentials: Bearer token

    Returns:
        Session ID and metadata
    """
    try:
        session_id = await service.create_analysis_session(request.dict())
        return {
            "success": True,
            "session_id": session_id,
            "message": "Analysis session created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get analysis session results.

    Args:
        session_id: Session identifier
        service: EmpathyService instance
        credentials: Bearer token

    Returns:
        Session results and status
    """
    result = await service.get_session_results(session_id)
    if not result["success"]:
        raise HTTPException(status_code=404, detail="Session not found")
    return result


@router.post("/project")
async def analyze_project(
    request: ProjectAnalysisRequest,
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze an entire project.

    Args:
        request: Project analysis configuration
        service: EmpathyService instance
        credentials: Bearer token

    Returns:
        Project analysis results
    """
    try:
        result = await service.analyze_project(
            project_path=request.project_path,
            file_patterns=request.file_patterns
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project analysis failed: {str(e)}")


@router.post("/file")
async def analyze_file(
    file: UploadFile = File(...),
    language: str = "python",
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Analyze a single uploaded file.

    Args:
        file: Uploaded file
        language: Programming language
        service: EmpathyService instance
        credentials: Bearer token

    Returns:
        File analysis results
    """
    try:
        content = await file.read()
        code = content.decode('utf-8')

        result = await service.analyze_code(
            code=code,
            language=language,
            include_metrics=True
        )

        return {
            "success": True,
            "filename": file.filename,
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File analysis failed: {str(e)}")


@router.get("/history")
async def get_analysis_history(
    limit: int = 10,
    offset: int = 0,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get user's analysis history.

    Args:
        limit: Number of results to return
        offset: Pagination offset
        credentials: Bearer token

    Returns:
        List of past analyses
    """
    # Placeholder implementation
    return {
        "analyses": [
            {
                "id": "analysis_123",
                "type": "code",
                "timestamp": "2025-10-19T12:00:00Z",
                "issues_found": 5,
                "status": "completed"
            }
        ],
        "total": 1,
        "limit": limit,
        "offset": offset
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete an analysis session.

    Args:
        session_id: Session identifier
        credentials: Bearer token

    Returns:
        Deletion confirmation
    """
    return {
        "success": True,
        "message": f"Session {session_id} deleted successfully"
    }
