"""
Nursing Assessment Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from src.utils.config import get_educational_banner

router = APIRouter(
    prefix="/wizard/nursing-assessment",
    tags=["wizards", "nursing-assessment"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"},
    },
)

# In-memory session storage (Redis in production)
_wizard_sessions: dict[str, dict[str, Any]] = {}


class NursingAssessmentStep(BaseModel):
    """Pydantic model for nursing assessment step following API Design Standards."""

    patient_id: str | None = Field(None, description="Patient identifier")
    assessment_type: str = Field(..., description="Type of assessment (initial, focused, etc.)")
    vital_signs: dict[str, Any] | None = Field(None, description="Vital signs data")
    pain_assessment: dict[str, Any] | None = Field(None, description="Pain assessment data")
    mobility_status: str | None = Field(None, description="Patient mobility status")
    cognitive_status: str | None = Field(None, description="Cognitive assessment")
    notes: str | None = Field(None, description="Additional assessment notes")


class WizardResponse(BaseModel):
    """Wizard response following API Design Standards."""

    wizard_id: str
    current_step: int
    total_steps: int
    step_name: str
    prompt: str
    completed: bool = False
    banner: str = Field(default_factory=get_educational_banner)


@router.post("/start", response_model=WizardResponse)
async def start_nursing_assessment():
    """
    Start nursing assessment wizard following Wizard Pattern Implementation.
    Creates new wizard session with UUID-based tracking.
    """
    wizard_id = str(uuid4())

    # Initialize session following session state pattern
    _wizard_sessions[wizard_id] = {
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 5,
        "completed": False,
        "data": {},
        "step_names": [
            "Patient Information",
            "Vital Signs Assessment",
            "Pain & Comfort Assessment",
            "Mobility & Safety Assessment",
            "Review & Documentation",
        ],
    }

    return WizardResponse(
        wizard_id=wizard_id,
        current_step=1,
        total_steps=5,
        step_name="Patient Information",
        prompt="Please provide patient identification and assessment type. What type of nursing assessment are you conducting?",
        banner=get_educational_banner(),
    )


@router.post("/{wizard_id}/step", response_model=WizardResponse)
async def submit_assessment_step(wizard_id: str, step_data: NursingAssessmentStep):
    """
    Submit nursing assessment step following Wizard Pattern Implementation.
    Validates step data and advances wizard state.
    """
    if wizard_id not in _wizard_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wizard session not found"
        )

    session = _wizard_sessions[wizard_id]

    if session["completed"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Wizard already completed"
        )

    # Store step data following session state pattern
    current_step = session["current_step"]
    session["data"][f"step_{current_step}"] = step_data.model_dump(exclude_none=True)

    # Advance to next step
    next_step = current_step + 1

    if next_step > session["total_steps"]:
        # Mark as completed
        session["completed"] = True
        session["completed_at"] = datetime.now().isoformat()

        return WizardResponse(
            wizard_id=wizard_id,
            current_step=session["total_steps"],
            total_steps=session["total_steps"],
            step_name="Assessment Complete",
            prompt="Nursing assessment completed successfully. Review documentation for accuracy.",
            completed=True,
            banner=get_educational_banner(),
        )

    # Continue to next step
    session["current_step"] = next_step
    step_prompts = [
        "Enter vital signs (temperature, pulse, respirations, blood pressure, oxygen saturation)",
        "Assess pain level using appropriate pain scale and comfort measures",
        "Evaluate mobility status, fall risk, and safety considerations",
        "Review all assessment data and add final documentation notes",
    ]

    return WizardResponse(
        wizard_id=wizard_id,
        current_step=next_step,
        total_steps=session["total_steps"],
        step_name=session["step_names"][next_step - 1],
        prompt=(
            step_prompts[next_step - 2]
            if next_step <= len(step_prompts) + 1
            else "Complete assessment"
        ),
        banner=get_educational_banner(),
    )


@router.get("/{wizard_id}/status", response_model=WizardResponse)
async def get_assessment_status(wizard_id: str):
    """Get current wizard status following Wizard Pattern Implementation."""
    if wizard_id not in _wizard_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wizard session not found"
        )

    session = _wizard_sessions[wizard_id]
    current_step = session["current_step"]

    return WizardResponse(
        wizard_id=wizard_id,
        current_step=current_step,
        total_steps=session["total_steps"],
        step_name=(
            session["step_names"][current_step - 1]
            if current_step <= len(session["step_names"])
            else "Complete"
        ),
        prompt=f"Currently on step {current_step} of {session['total_steps']}",
        completed=session["completed"],
        banner=get_educational_banner(),
    )
