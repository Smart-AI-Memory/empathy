"""
Users API endpoints.
Handles user profile management and settings.
"""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/users", tags=["users"])
security = HTTPBearer()


class UpdateProfileRequest(BaseModel):
    """Update profile request model."""

    name: str | None = None
    email: EmailStr | None = None
    preferences: dict[str, Any] | None = None


@router.get("/profile")
async def get_profile(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get user profile information.

    Args:
        credentials: Bearer token

    Returns:
        User profile data
    """
    return {
        "id": "user_123",
        "email": "user@example.com",
        "name": "Demo User",
        "created_at": "2025-01-01T00:00:00Z",
        "license": {"type": "developer", "plugins": ["software", "healthcare"], "status": "active"},
        "preferences": {"theme": "dark", "notifications": True},
    }


@router.put("/profile")
async def update_profile(
    request: UpdateProfileRequest, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Update user profile.

    Args:
        request: Profile update data
        credentials: Bearer token

    Returns:
        Updated profile
    """
    return {
        "success": True,
        "message": "Profile updated successfully",
        "profile": {
            "name": request.name or "Demo User",
            "email": request.email or "user@example.com",
            "preferences": request.preferences or {},
        },
    }


@router.get("/usage")
async def get_usage_stats(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get user usage statistics.

    Args:
        credentials: Bearer token

    Returns:
        Usage statistics
    """
    return {
        "analyses_count": 42,
        "wizards_used": ["Enhanced Testing", "Performance Profiling", "Security Analysis"],
        "total_issues_found": 156,
        "period": "last_30_days",
    }


@router.delete("/account")
async def delete_account(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Delete user account.

    Args:
        credentials: Bearer token

    Returns:
        Deletion confirmation
    """
    return {
        "success": True,
        "message": "Account deletion initiated. You will receive a confirmation email.",
    }
