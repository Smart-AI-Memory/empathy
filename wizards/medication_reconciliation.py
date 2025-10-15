"""
Medication Reconciliation Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any
from uuid import uuid4
from datetime import datetime

from ...utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/medication-reconciliation",
    tags=["wizards", "medication-reconciliation"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"}
    }
)

# Wizard session storage (Redis in production)
_wizard_sessions: Dict[str, Dict[str, Any]] = {}

class MedicationItem(BaseModel):
    name: str = Field(..., description="Medication name")
    dosage: str = Field(..., description="Dosage information")  
    frequency: str = Field(..., description="Frequency of administration")
    route: str = Field(..., description="Route of administration")

@router.post("/start")
async def start_medication_reconciliation():
    """Start medication reconciliation wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())
    
    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "medication_reconciliation",
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
        "wizard_type": "medication_reconciliation", 
        "current_step": 1,
        "total_steps": 4,
        "step_title": "Patient Information",
        "educational_note": "Medication reconciliation prevents medication errors during care transitions."
    }

@router.get("/{wizard_id}/status")
async def get_wizard_status(wizard_id: str):
    """Get current wizard status following Wizard Pattern Implementation."""
    
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