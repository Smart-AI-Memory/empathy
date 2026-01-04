"""Memory-Enhanced Debugging Wizard API

Wraps the MemoryEnhancedDebuggingWizard for web access.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/wizards/debugging", tags=["Debugging"])


class DebugRequest(BaseModel):
    """Request model for debugging analysis."""

    error_message: str = Field(..., description="The error message to analyze")
    file_path: str = Field(default="unknown", description="File where error occurred")
    stack_trace: str | None = Field(default="", description="Stack trace if available")
    line_number: int | None = Field(default=None, description="Line number of error")
    code_snippet: str | None = Field(default="", description="Surrounding code context")
    correlate_with_history: bool = Field(
        default=True,
        description="Enable historical pattern matching",
    )


class RecordResolutionRequest(BaseModel):
    """Request to record a bug resolution."""

    bug_id: str = Field(..., description="Bug ID from analysis result")
    root_cause: str = Field(..., description="What caused the bug")
    fix_applied: str = Field(..., description="Description of the fix")
    fix_code: str | None = Field(default=None, description="Code snippet of the fix")
    resolution_time_minutes: int = Field(default=0, description="Time spent fixing")
    resolved_by: str = Field(default="developer", description="Who fixed it")


@router.post("/analyze")
async def analyze_error(request: DebugRequest):
    """Analyze an error with historical pattern matching.

    This wizard correlates your error with past bugs from the team's
    memory, recommending proven fixes and predicting resolution time.

    Features:
    - Error classification (null_reference, async_timing, import_error, etc.)
    - Historical bug pattern matching
    - Fix recommendations based on similar past bugs
    - Resolution time predictions
    - Level 4 anticipatory insights
    """
    try:
        from empathy_software_plugin.wizards.memory_enhanced_debugging_wizard import (
            DebuggingWizardConfig,
            MemoryEnhancedDebuggingWizard,
        )

        # Use web config (limited features for demo)
        config = DebuggingWizardConfig.web_config()
        wizard = MemoryEnhancedDebuggingWizard(config=config)

        result = await wizard.analyze(
            {
                "error_message": request.error_message,
                "file_path": request.file_path,
                "stack_trace": request.stack_trace,
                "line_number": request.line_number,
                "code_snippet": request.code_snippet,
                "correlate_with_history": request.correlate_with_history,
            },
        )

        return {
            "success": True,
            "wizard": "Memory-Enhanced Debugging Wizard",
            "level": 4,
            "result": result,
        }

    except ImportError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Wizard not available: {e!s}. Install empathy-framework[full]",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/record-resolution")
async def record_resolution(request: RecordResolutionRequest):
    """Record a bug resolution for future pattern matching.

    After successfully fixing a bug, call this endpoint to store
    the knowledge for future debugging sessions.
    """
    try:
        from empathy_software_plugin.wizards.memory_enhanced_debugging_wizard import (
            MemoryEnhancedDebuggingWizard,
        )

        wizard = MemoryEnhancedDebuggingWizard()
        success = await wizard.record_resolution(
            bug_id=request.bug_id,
            root_cause=request.root_cause,
            fix_applied=request.fix_applied,
            fix_code=request.fix_code,
            resolution_time_minutes=request.resolution_time_minutes,
            resolved_by=request.resolved_by,
        )

        return {
            "success": success,
            "message": (
                "Resolution recorded for future pattern matching"
                if success
                else "Could not record resolution"
            ),
        }

    except ImportError as e:
        raise HTTPException(status_code=503, detail=f"Wizard not available: {e!s}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demo")
async def demo_analysis():
    """Demo endpoint showing wizard capabilities with sample error."""
    sample_request = DebugRequest(
        error_message="TypeError: Cannot read property 'map' of undefined",
        file_path="src/components/UserList.tsx",
        stack_trace="at UserList (UserList.tsx:42)\nat renderWithHooks...",
        code_snippet="const items = data.items.map(item => <Item {...item} />);",
    )
    return await analyze_error(sample_request)
