"""Health check endpoint for Railway/Kubernetes monitoring."""

from datetime import datetime

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health", tags=["Health"])


@router.get("")
@router.get("/")
async def health_check():
    """Health check endpoint.

    Used by Railway for deployment health monitoring.
    """
    return {
        "status": "healthy",
        "service": "empathy-dev-wizards",
        "version": "2.2.9",
        "timestamp": datetime.now().isoformat(),
        "wizards": {
            "debugging": "available",
            "security": "available",
            "code_review": "available",
            "inspect": "available",
        },
    }


@router.get("/ready")
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return {"ready": True}


@router.get("/live")
async def liveness_check():
    """Liveness probe for Kubernetes."""
    return {"alive": True}
