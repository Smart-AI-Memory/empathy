"""
Care Plan Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from ...utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/care-plan",
    tags=["wizards", "care-plan"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"},
    },
)

# Wizard session storage (Redis in production)
_wizard_sessions: dict[str, dict[str, Any]] = {}


@router.post("/start")
async def start_care_plan():
    """Start care plan wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "care_plan",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 3,
        "completed_steps": [],
        "data": {},
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "care_plan",
        "current_step": 1,
        "total_steps": 3,
        "step_title": "Nursing Diagnoses",
        "educational_note": "Use NANDA-approved nursing diagnoses for standardized care planning.",
    }


@router.get("/{wizard_id}/status")
async def get_care_plan_status(wizard_id: str):
    """Get care plan wizard status following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": session["wizard_type"],
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "completed_steps": session["completed_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": (
            "completed"
            if len(session["completed_steps"]) == session["total_steps"]
            else "in_progress"
        ),
    }
