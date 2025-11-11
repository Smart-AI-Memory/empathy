"""
Subscriptions API endpoints.
Handles license purchases, subscriptions, and team management.
"""

from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])
security = HTTPBearer()


class PurchaseRequest(BaseModel):
    """Purchase request model."""

    product: str  # "book", "team_license"
    quantity: int = 1
    payment_method: str


class TeamMemberRequest(BaseModel):
    """Add team member request model."""

    email: EmailStr
    role: str = "developer"


@router.get("/")
async def get_subscriptions(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get user's active subscriptions.

    Args:
        credentials: Bearer token

    Returns:
        List of active subscriptions
    """
    return {
        "subscriptions": [
            {
                "id": "sub_123",
                "product": "book_early_access",
                "status": "active",
                "licenses": 1,
                "plugins": ["software", "healthcare"],
                "purchased_at": "2025-01-15T10:00:00Z",
                "type": "perpetual",
            }
        ],
        "total": 1,
    }


@router.post("/purchase")
async def purchase_subscription(
    request: PurchaseRequest, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Purchase a new subscription or additional licenses.

    Args:
        request: Purchase details
        credentials: Bearer token

    Returns:
        Purchase confirmation and license keys
    """
    # Placeholder implementation
    # In production, integrate with payment processor
    return {
        "success": True,
        "order_id": "order_123456",
        "product": request.product,
        "quantity": request.quantity,
        "total_amount": 49.00 * request.quantity,
        "license_keys": [f"LICENSE-KEY-{i+1}" for i in range(request.quantity)],
        "message": "Purchase successful! Check your email for license keys.",
    }


@router.get("/team")
async def get_team_members(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get team members for organization subscription.

    Args:
        credentials: Bearer token

    Returns:
        List of team members
    """
    return {
        "team_members": [
            {
                "id": "user_123",
                "email": "user@example.com",
                "name": "Demo User",
                "role": "admin",
                "status": "active",
                "license_assigned": True,
            }
        ],
        "available_licenses": 4,
        "total_licenses": 5,
    }


@router.post("/team/members")
async def add_team_member(
    request: TeamMemberRequest, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Add a new team member.

    Args:
        request: Team member details
        credentials: Bearer token

    Returns:
        Added team member info
    """
    return {
        "success": True,
        "message": f"Invitation sent to {request.email}",
        "member": {"email": request.email, "role": request.role, "status": "invited"},
    }


@router.delete("/team/members/{user_id}")
async def remove_team_member(
    user_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Remove a team member.

    Args:
        user_id: User ID to remove
        credentials: Bearer token

    Returns:
        Removal confirmation
    """
    return {"success": True, "message": f"User {user_id} removed from team", "license_freed": True}


@router.get("/licenses")
async def get_licenses(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get license information for the user's account.

    Args:
        credentials: Bearer token

    Returns:
        License details
    """
    return {
        "licenses": [
            {
                "id": "lic_123",
                "type": "developer",
                "plugins": ["software", "healthcare"],
                "status": "active",
                "machine_id": "machine_abc123",
                "activated_at": "2025-01-15T10:30:00Z",
                "version": "1.0.0",
            }
        ],
        "total_available": 1,
        "total_used": 1,
    }


@router.post("/licenses/{license_id}/deactivate")
async def deactivate_license(
    license_id: str, credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Deactivate a license from a machine.

    Args:
        license_id: License ID to deactivate
        credentials: Bearer token

    Returns:
        Deactivation confirmation
    """
    return {
        "success": True,
        "message": "License deactivated. You can now activate it on another machine.",
        "license_id": license_id,
    }
