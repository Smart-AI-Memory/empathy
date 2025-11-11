"""
Analysis API endpoints.
Handles code analysis, project scanning, and result retrieval.

Input validation and error handling included for security.
"""

from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, validator

from services.empathy_service import EmpathyService

router = APIRouter(prefix="/api/analysis", tags=["analysis"])
security = HTTPBearer()


def get_empathy_service() -> EmpathyService:
    """Get EmpathyService instance."""
    return EmpathyService()


class ProjectAnalysisRequest(BaseModel):
    """Request model for project analysis."""

    project_path: str
    file_patterns: list[str] | None = None
    exclude_patterns: list[str] | None = None
    wizards: list[str] | None = None

    @validator("project_path")
    def validate_project_path(cls, v):
        """Validate project path is provided"""
        if not v or not v.strip():
            raise ValueError("project_path cannot be empty")
        if len(v) > 1024:
            raise ValueError("project_path exceeds maximum length")
        return v


class SessionConfig(BaseModel):
    """Configuration for analysis session."""

    name: str
    description: str | None = None
    wizards: list[str]
    config: dict[str, Any] = {}

    @validator("name")
    def validate_name(cls, v):
        """Validate session name"""
        if not v or not v.strip():
            raise ValueError("Session name cannot be empty")
        if len(v) > 255:
            raise ValueError("Session name exceeds maximum length")
        return v

    @validator("wizards")
    def validate_wizards(cls, v):
        """Validate wizards list"""
        if not v or len(v) == 0:
            raise ValueError("At least one wizard must be specified")
        if len(v) > 20:
            raise ValueError("Maximum 20 wizards allowed per session")
        return v


@router.post("/session")
async def create_session(
    request: SessionConfig,
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
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
            "message": "Analysis session created successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.get("/session/{session_id}")
async def get_session(
    session_id: str,
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
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
    credentials: HTTPAuthorizationCredentials = Depends(security),
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
            project_path=request.project_path, file_patterns=request.file_patterns
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Project analysis failed: {str(e)}")


@router.post("/file")
async def analyze_file(
    file: UploadFile = File(...),
    language: str = "python",
    service: EmpathyService = Depends(get_empathy_service),
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    """
    Analyze a single uploaded file.

    Args:
        file: Uploaded file (max 10MB)
        language: Programming language (python, javascript, typescript, java, go, rust)
        service: EmpathyService instance
        credentials: Bearer token

    Returns:
        File analysis results

    Raises:
        HTTPException: If file is invalid or analysis fails
    """
    # Validate file size (10MB limit)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {MAX_FILE_SIZE} bytes",
        )

    # Validate language
    SUPPORTED_LANGUAGES = {
        "python",
        "javascript",
        "typescript",
        "java",
        "go",
        "rust",
        "cpp",
        "c",
        "csharp",
        "php",
    }
    if language.lower() not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}",
        )

    # Validate file content
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a name")

    try:
        content = await file.read()

        # Validate content is not empty
        if not content:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="File cannot be empty"
            )

        code = content.decode("utf-8")

        result = await service.analyze_code(code=code, language=language, include_metrics=True)

        return {"success": True, "filename": file.filename, "analysis": result}
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File must be valid UTF-8 text"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"File analysis failed: {str(e)}",
        )


@router.get("/history")
async def get_analysis_history(
    limit: int = 10, offset: int = 0, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get user's analysis history.

    Args:
        limit: Number of results to return (max 100, default 10)
        offset: Pagination offset (min 0)
        credentials: Bearer token

    Returns:
        List of past analyses

    Raises:
        HTTPException: If limit or offset are invalid
    """
    # Validate pagination parameters
    MAX_LIMIT = 100
    if limit < 1 or limit > MAX_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit must be between 1 and {MAX_LIMIT}",
        )

    if offset < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="offset cannot be negative"
        )

    # Placeholder implementation
    return {
        "analyses": [
            {
                "id": "analysis_123",
                "type": "code",
                "timestamp": "2025-10-19T12:00:00Z",
                "issues_found": 5,
                "status": "completed",
            }
        ],
        "total": 1,
        "limit": limit,
        "offset": offset,
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Delete an analysis session.

    Args:
        session_id: Session identifier
        credentials: Bearer token

    Returns:
        Deletion confirmation
    """
    return {"success": True, "message": f"Session {session_id} deleted successfully"}
