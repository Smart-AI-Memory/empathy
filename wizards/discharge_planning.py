"""
Discharge Planning Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ...utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/discharge-planning",
    tags=["wizards", "discharge-planning"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"}
    }
)

# Wizard session storage (Redis in production)
_wizard_sessions: Dict[str, Dict[str, Any]] = {}

@router.post("/start")
async def start_discharge_planning():
    """Start discharge planning wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())
    
    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "discharge_planning",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 4,
        "completed_steps": [],
        "data": {}
    }
    
    _wizard_sessions[wizard_id] = session_data
    
    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "discharge_planning",
        "current_step": 1,
        "total_steps": 4,
        "step_title": "Discharge Assessment",
        "educational_note": "Effective discharge planning begins at admission and involves multidisciplinary collaboration."
    }

@router.get("/{wizard_id}/status")
async def get_discharge_planning_status(wizard_id: str):
    """Get discharge planning wizard status following Wizard Pattern Implementation."""
    
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
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress"
    }