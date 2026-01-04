"""Pattern management API endpoints.

Provides REST API for:
- Listing patterns with filtering
- Exporting patterns
- Deleting patterns (future)
"""

import tempfile
from datetime import datetime
from pathlib import Path
from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse

from ..schemas import (
    ClassificationEnum,
    ExportPatternsRequest,
    ExportPatternsResponse,
    PatternListResponse,
    PatternSummary,
)
from ..services.memory_service import MemoryService, get_memory_service

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get(
    "/patterns",
    response_model=PatternListResponse,
    summary="List patterns",
    description="List patterns in long-term storage with optional classification filter.",
)
async def list_patterns(
    service: Annotated[MemoryService, Depends(get_memory_service)],
    classification: Annotated[
        ClassificationEnum | None,
        Query(description="Filter by classification level"),
    ] = None,
    limit: Annotated[int, Query(ge=1, le=1000, description="Maximum patterns to return")] = 100,
) -> PatternListResponse:
    """List patterns.

    Query Parameters:
    - classification: Filter by PUBLIC, INTERNAL, or SENSITIVE
    - limit: Maximum number of patterns to return (1-1000)

    Returns list of patterns with metadata:
    - pattern_id
    - pattern_type
    - classification
    - created_at
    - user_id
    """
    try:
        classification_str = classification.value if classification else None
        patterns = await service.list_patterns(
            classification=classification_str,
            limit=limit,
        )

        logger.info(
            "patterns_listed",
            count=len(patterns),
            classification=classification_str,
        )

        # Convert to PatternSummary objects
        pattern_summaries = [
            PatternSummary(
                pattern_id=p.get("pattern_id", "unknown"),
                pattern_type=p.get("pattern_type", "unknown"),
                classification=ClassificationEnum(p.get("classification", "PUBLIC")),
                created_at=p.get("created_at"),
                user_id=p.get("user_id"),
            )
            for p in patterns
        ]

        return PatternListResponse(
            total=len(pattern_summaries),
            patterns=pattern_summaries,
            classification_filter=classification,
        )
    except Exception as e:
        logger.error("pattern_list_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list patterns: {e!s}",
        )


@router.post(
    "/patterns/export",
    response_model=ExportPatternsResponse,
    summary="Export patterns",
    description="Export patterns to JSON file with optional classification filter.",
)
async def export_patterns(
    request: ExportPatternsRequest,
    service: Annotated[MemoryService, Depends(get_memory_service)],
) -> ExportPatternsResponse:
    """Export patterns to JSON file.

    Request body:
    - classification: Optional filter (PUBLIC/INTERNAL/SENSITIVE)
    - output_filename: Optional custom filename

    Creates a JSON file with:
    - exported_at: Timestamp
    - classification_filter: Applied filter
    - pattern_count: Number of patterns
    - patterns: Array of pattern data
    """
    try:
        # Generate output path
        if request.output_filename:
            output_path = str(Path(tempfile.gettempdir()) / request.output_filename)
        else:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_path = str(Path(tempfile.gettempdir()) / f"patterns_export_{timestamp}.json")

        classification_str = request.classification.value if request.classification else None

        result = await service.export_patterns(
            output_path=output_path,
            classification=classification_str,
        )

        logger.info(
            "patterns_exported",
            count=result["pattern_count"],
            output_path=output_path,
        )

        return ExportPatternsResponse(**result)
    except Exception as e:
        logger.error("pattern_export_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export patterns: {e!s}",
        )


@router.get(
    "/patterns/export/download/{filename}",
    summary="Download exported patterns",
    description="Download a previously exported pattern file.",
)
async def download_export(filename: str) -> FileResponse:
    """Download exported pattern file.

    Path Parameters:
    - filename: Name of the exported file

    Returns the JSON file for download.
    """
    try:
        file_path = Path(tempfile.gettempdir()) / filename

        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Export file not found: {filename}",
            )

        logger.info("export_downloaded", filename=filename)

        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/json",
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("export_download_failed", filename=filename, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to download export: {e!s}",
        )


@router.delete(
    "/patterns/{pattern_id}",
    summary="Delete pattern",
    description="Delete a pattern from long-term storage (admin only).",
)
async def delete_pattern(
    pattern_id: str,
    service: Annotated[MemoryService, Depends(get_memory_service)],
    user_id: Annotated[str, Query(description="User performing deletion")] = "admin@system",
) -> dict[str, bool]:
    """Delete a pattern.

    Path Parameters:
    - pattern_id: ID of pattern to delete

    Query Parameters:
    - user_id: User performing deletion (for audit trail)

    Returns success status.
    """
    try:
        success = await service.delete_pattern(pattern_id, user_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pattern not found: {pattern_id}",
            )

        logger.info("pattern_deleted", pattern_id=pattern_id, user_id=user_id)

        return {"success": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("pattern_delete_failed", pattern_id=pattern_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete pattern: {e!s}",
        )
