"""
Authentication API endpoints.
Handles user authentication, tokens, and license validation.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request model."""
    email: EmailStr
    password: str
    name: str
    license_key: Optional[str] = None


class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """
    Authenticate user and return access token.

    Args:
        request: Login credentials

    Returns:
        Access token and metadata
    """
    # Placeholder implementation
    # In production, validate against database
    if request.email and request.password:
        return TokenResponse(
            access_token="mock_access_token_" + request.email,
            token_type="bearer",
            expires_in=3600
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )


@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest):
    """
    Register new user account.

    Args:
        request: Registration details

    Returns:
        Access token for new account
    """
    # Placeholder implementation
    # In production, create user in database and validate license
    return TokenResponse(
        access_token="mock_access_token_new_user",
        token_type="bearer",
        expires_in=3600
    )


@router.post("/validate-license")
async def validate_license(
    license_key: str,
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Validate a license key.

    Args:
        license_key: License key to validate
        credentials: Bearer token

    Returns:
        License validation result
    """
    # Placeholder implementation
    return {
        "valid": True,
        "license_type": "developer",
        "plugins": ["software", "healthcare"],
        "expires_at": None  # Perpetual license
    }


@router.post("/refresh")
async def refresh_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Refresh access token.

    Args:
        credentials: Current bearer token

    Returns:
        New access token
    """
    return TokenResponse(
        access_token="mock_refreshed_token",
        token_type="bearer",
        expires_in=3600
    )


@router.get("/me")
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Get current authenticated user info.

    Args:
        credentials: Bearer token

    Returns:
        User information
    """
    return {
        "id": "user_123",
        "email": "user@example.com",
        "name": "Demo User",
        "license": {
            "type": "developer",
            "plugins": ["software", "healthcare"]
        }
    }
