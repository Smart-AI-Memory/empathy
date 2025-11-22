"""
Shim module to expose the existing treatment_plan router under the `src` package.
Some routers live at `routers.wizards.*` (top-level); tests and src loader expect `src.routers.wizards.*`.
This shim imports the real router and exposes it for the src-based loader.
"""

try:
    from routers.wizards.treatment_plan import router  # type: ignore
except Exception:
    # Fallback: expose an empty APIRouter so imports don't fail
    from fastapi import APIRouter

    router = APIRouter()

__all__ = ["router"]
