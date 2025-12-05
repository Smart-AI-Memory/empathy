"""
Care Plan Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
"""

import json
import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...utils.config import get_educational_banner

logger = logging.getLogger(__name__)

# Redis import with fallback
try:
    from src.utils.redis_cache import get_redis_client

    _has_redis = True
except ImportError:
    _has_redis = False

router = APIRouter(
    prefix="/wizard/care-plan",
    tags=["wizards", "care-plan"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"},
    },
)

# Session storage (Redis in production, memory for development)
_wizard_sessions: dict[str, dict[str, Any]] = {}


async def _store_wizard_session(wizard_id: str, session_data: dict[str, Any]):
    """Store wizard session in Redis or memory."""
    if _has_redis:
        try:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.setex(
                    f"wizard_session:{wizard_id}",
                    3600,  # 1 hour expiry
                    json.dumps(session_data),
                )
                return
        except Exception as e:
            logger.warning(f"Failed to store session in Redis: {e}")

    # Fallback to memory
    _wizard_sessions[wizard_id] = session_data


async def _get_wizard_session(wizard_id: str) -> dict[str, Any] | None:
    """Retrieve wizard session from Redis or memory."""
    if _has_redis:
        try:
            redis_client = await get_redis_client()
            if redis_client:
                data = await redis_client.get(f"wizard_session:{wizard_id}")
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.warning(f"Failed to retrieve session from Redis: {e}")

    # Fallback to memory
    return _wizard_sessions.get(wizard_id)


class CarePlanStepData(BaseModel):
    """Data model for care plan step submission."""

    step_data: dict[str, Any]


@router.post("/start")
async def start_care_plan():
    """Start care plan wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "care_plan",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 4,
        "completed": False,
        "completed_steps": [],
        "data": {},
    }

    await _store_wizard_session(wizard_id, session_data)

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "care_plan",
        "current_step": 1,
        "total_steps": 4,
        "step_title": "Nursing Diagnoses",
        "step_description": "Identify NANDA-approved nursing diagnoses based on patient assessment",
        "educational_note": "Use NANDA-approved nursing diagnoses for standardized care planning.",
    }


@router.post("/{wizard_id}/step")
async def submit_care_plan_step(wizard_id: str, step_data: CarePlanStepData):
    """Submit care plan step data."""
    session = await _get_wizard_session(wizard_id)
    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    if session.get("completed", False):
        raise HTTPException(status_code=422, detail="Care plan already completed")

    current_step = session["current_step"]

    # Store step data
    session["data"][f"step_{current_step}"] = step_data.step_data

    # Mark step as completed
    if current_step not in session["completed_steps"]:
        session["completed_steps"].append(current_step)

    # Advance to next step (no auto-complete - requires explicit approval)
    if current_step < session["total_steps"]:
        session["current_step"] = current_step + 1
        next_step_info = _get_step_info(current_step + 1)
    else:
        next_step_info = {
            "step_title": "Review & Finalize",
            "message": "Use /preview to generate report, then /save to finalize",
        }

    # Store updated session
    await _store_wizard_session(wizard_id, session)

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_completed": current_step,
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "next_step": next_step_info,
    }


@router.get("/{wizard_id}/status")
async def get_care_plan_status(wizard_id: str):
    """Get care plan wizard status following Wizard Pattern Implementation."""

    session = await _get_wizard_session(wizard_id)
    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": session["wizard_type"],
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "completed_steps": session["completed_steps"],
        "completed": session.get("completed", False),
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if session.get("completed", False) else "in_progress",
    }


@router.post("/{wizard_id}/preview")
async def preview_care_plan(wizard_id: str):
    """
    Generate preview of care plan.
    This does NOT mark the plan as completed.
    Requires user to call /save endpoint with approval to finalize.
    """
    session = await _get_wizard_session(wizard_id)
    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    if session.get("completed", False):
        raise HTTPException(status_code=422, detail="Care plan already completed")

    # Generate care plan preview
    collected_data = session["data"]
    preview_report = _generate_care_plan_report(collected_data)

    # Store preview in session (does NOT mark as completed)
    session["preview_report"] = preview_report
    session["preview_generated_at"] = datetime.now().isoformat()

    # Store updated session
    await _store_wizard_session(wizard_id, session)

    return {
        "banner": get_educational_banner(),
        "success": True,
        "wizard_id": wizard_id,
        "message": "Care plan preview generated. Please review and use /save endpoint to finalize.",
        "data": {"preview": preview_report, "generated_at": session["preview_generated_at"]},
    }


@router.post("/{wizard_id}/save")
async def save_care_plan(wizard_id: str, approval_data: dict[str, Any]):
    """
    Finalize and save care plan with user approval.
    Requires user_approved: true in request body.
    This is the ONLY endpoint that marks the care plan as completed.
    """
    session = await _get_wizard_session(wizard_id)
    if not session:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    if session.get("completed", False):
        raise HTTPException(status_code=422, detail="Care plan already completed")

    # Require preview before save
    if "preview_report" not in session:
        raise HTTPException(
            status_code=422,
            detail="Must generate preview before saving. Call /preview endpoint first.",
        )

    # Require explicit user approval
    if not approval_data.get("user_approved", False):
        raise HTTPException(
            status_code=422,
            detail="User approval required. Set user_approved: true to finalize care plan.",
        )

    # Mark as completed with user approval
    session["completed"] = True
    session["completed_at"] = datetime.now().isoformat()
    session["user_approved"] = True
    session["approved_by"] = approval_data.get("approved_by", "Unknown user")

    # Store updated session
    await _store_wizard_session(wizard_id, session)

    return {
        "banner": get_educational_banner(),
        "success": True,
        "wizard_id": wizard_id,
        "message": "Care plan finalized and saved successfully.",
        "data": {
            "report": session["preview_report"],
            "completed_at": session["completed_at"],
            "user_approved": True,
            "approved_by": session["approved_by"],
        },
    }


def _get_step_info(step_number: int) -> dict[str, Any]:
    """Get step configuration information."""
    steps = {
        1: {
            "step_title": "Nursing Diagnoses",
            "step_description": "Identify NANDA-approved nursing diagnoses",
            "educational_note": "Use NANDA-I taxonomy for standardized diagnoses",
        },
        2: {
            "step_title": "Goals & Outcomes",
            "step_description": "Define measurable patient goals and expected outcomes",
            "educational_note": "Goals should be SMART: Specific, Measurable, Achievable, Relevant, Time-bound",
        },
        3: {
            "step_title": "Nursing Interventions",
            "step_description": "Plan evidence-based nursing interventions",
            "educational_note": "Include both independent and collaborative interventions",
        },
        4: {
            "step_title": "Review & Finalize",
            "step_description": "Review complete care plan and finalize with approval",
            "educational_note": "Review all components before finalizing",
            "is_review_step": True,
        },
    }
    return steps.get(step_number, {})


def _generate_care_plan_report(collected_data: dict[str, Any]) -> dict[str, Any]:
    """
    Generate formatted nursing care plan from collected data.
    Internal function used by /preview and /save endpoints.
    """
    step_1 = collected_data.get("step_1", {})
    step_2 = collected_data.get("step_2", {})
    step_3 = collected_data.get("step_3", {})

    narrative = f"""
NURSING CARE PLAN
{'=' * 80}

CARE PLAN DATE: {datetime.now().strftime('%Y-%m-%d %H:%M')}

NURSING DIAGNOSES
{step_1.get('diagnoses', 'Not documented')}

GOALS & EXPECTED OUTCOMES
{step_2.get('goals', 'Not documented')}

NURSING INTERVENTIONS
{step_3.get('interventions', 'Not documented')}

{'=' * 80}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    return {
        "report_type": "care_plan",
        "narrative": narrative.strip(),
        "structured_data": {"diagnoses": step_1, "goals_outcomes": step_2, "interventions": step_3},
        "metadata": {"generated_at": datetime.now().isoformat(), "wizard_type": "care_plan"},
    }
