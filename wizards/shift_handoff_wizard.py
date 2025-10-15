"""
Shift Handoff Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation from SBAR wizard

Nurse-to-nurse shift handoff documentation wizard for safe patient transitions.
Based on best practices for bedside handoff communication.
"""

import logging
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from src.services import get_service
from src.utils.api_responses import create_success_response
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

# Conditional translation import
try:
    from src.services.translation_service import translate_text

    _has_translation = True
except ImportError:
    _has_translation = False

    async def translate_text(
        text: str,
        target_language: str,
        source_language: str = "en",
        context: str = "medical",
    ):
        return {"translated_text": text, "success": False}


# Settings following coding instructions
settings = get_settings()

router = APIRouter(
    prefix="/api/v1/wizards/shift-handoff",
    tags=["clinical-wizards"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid wizard step data"},
        500: {"description": "Wizard processing error"},
    },
)

# Session storage (Redis in production, memory for development)
try:
    from src.utils.redis_cache import get_redis_client

    _has_redis = True
except ImportError:
    _has_redis = False

_wizard_sessions: Dict[str, Dict[str, Any]] = {}


# Shift handoff wizard steps
SHIFT_HANDOFF_STEPS = {
    1: {
        "step": 1,
        "title": "Patient Identification & Status",
        "prompt": "Identify the patient and current clinical status",
        "fields": [
            "patient_name",
            "room_bed",
            "age",
            "diagnosis",
            "admission_date",
            "code_status",
        ],
        "help_text": "Start with patient basics: name, location, age, diagnosis, and code status",
    },
    2: {
        "step": 2,
        "title": "Current Condition & Vital Signs",
        "prompt": "Describe current condition and most recent vital signs",
        "fields": ["current_condition", "vital_signs", "pain_level", "mental_status"],
        "help_text": "Include vital signs, pain level, mental status, and overall condition",
    },
    3: {
        "step": 3,
        "title": "Treatments & Interventions",
        "prompt": "Detail current treatments, medications, and interventions",
        "fields": [
            "iv_lines",
            "medications",
            "recent_procedures",
            "pending_labs",
            "pending_orders",
        ],
        "help_text": "IV access, medications given, procedures done, pending orders/labs",
    },
    4: {
        "step": 4,
        "title": "Plan & Priorities",
        "prompt": "Outline the care plan and priorities for the next shift",
        "fields": [
            "care_priorities",
            "scheduled_tasks",
            "patient_concerns",
            "family_involvement",
        ],
        "help_text": "What needs to be done this shift? Patient/family concerns? Priorities?",
    },
    5: {
        "step": 5,
        "title": "Safety & Special Considerations",
        "prompt": "Note any safety concerns or special considerations",
        "fields": [
            "fall_risk",
            "isolation_precautions",
            "allergies",
            "special_equipment",
            "other_concerns",
        ],
        "help_text": "Falls risk, isolation, allergies, special equipment, or other safety concerns",
    },
}


async def _store_wizard_session(wizard_id: str, session_data: Dict[str, Any]):
    """Store wizard session in Redis or memory."""
    if _has_redis:
        try:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.setex(
                    f"wizard_session:{wizard_id}",
                    3600,  # 1 hour expiry
                    str(session_data),
                )
                return
        except Exception as e:
            logger.warning(f"Failed to store session in Redis: {e}")

    # Fallback to memory
    _wizard_sessions[wizard_id] = session_data


async def _get_wizard_session(wizard_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve wizard session from Redis or memory."""
    if _has_redis:
        try:
            redis_client = await get_redis_client()
            if redis_client:
                data = await redis_client.get(f"wizard_session:{wizard_id}")
                if data:
                    return eval(data)  # Convert string back to dict
        except Exception:
            pass

    # Fallback to memory
    return _wizard_sessions.get(wizard_id)


def _get_step_data(step_number: int) -> Dict[str, Any]:
    """Get step configuration data."""
    if step_number not in SHIFT_HANDOFF_STEPS:
        raise ValueError(f"Invalid step number: {step_number}")

    return SHIFT_HANDOFF_STEPS[step_number]


@router.post(
    "/start",
    summary="Start Shift Handoff Wizard",
    description="Initialize a new shift handoff documentation workflow for nurse-to-nurse handoff.",
)
async def start_shift_handoff_wizard():
    """Start shift handoff wizard following Wizard Pattern Implementation."""
    try:
        wizard_id = str(uuid4())

        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "shift_handoff",
            "current_step": 1,
            "total_steps": 5,
            "collected_data": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store session
        await _store_wizard_session(wizard_id, session_data)

        # Get first step prompt
        step_data = _get_step_data(1)

        response_data = {
            "wizard_session": session_data,
            "current_step": step_data,
            "progress": {"current": 1, "total": 5, "percentage": 20},
        }

        return create_success_response(
            data=response_data, message="Shift handoff wizard started successfully"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start shift handoff wizard: {str(e)}",
        )


@router.post(
    "/{wizard_id}/step",
    summary="Submit shift handoff wizard step",
    description="Submit data for current step and advance to next step in shift handoff workflow.",
)
async def submit_shift_handoff_step(wizard_id: str, step_data: Dict[str, Any]):
    """Submit step data and advance wizard."""
    try:
        # Get session
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        # Validate step number
        current_step = session["current_step"]
        if step_data.get("step") != current_step:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Expected step {current_step}, got {step_data.get('step')}",
            )

        # Store collected data
        session["collected_data"][f"step_{current_step}"] = step_data.get("data", {})
        session["updated_at"] = datetime.now().isoformat()

        # Advance to next step or complete
        if current_step < session["total_steps"]:
            session["current_step"] += 1
            await _store_wizard_session(wizard_id, session)

            next_step_data = _get_step_data(session["current_step"])

            return create_success_response(
                data={
                    "wizard_session": session,
                    "current_step": next_step_data,
                    "progress": {
                        "current": session["current_step"],
                        "total": session["total_steps"],
                        "percentage": (session["current_step"] / session["total_steps"])
                        * 100,
                    },
                },
                message=f"Step {current_step} completed",
            )
        else:
            # Wizard complete - generate final handoff report
            handoff_report = await _generate_handoff_report(session["collected_data"])

            session["completed_at"] = datetime.now().isoformat()
            session["final_report"] = handoff_report
            await _store_wizard_session(wizard_id, session)

            return create_success_response(
                data={
                    "wizard_session": session,
                    "handoff_report": handoff_report,
                    "completed": True,
                },
                message="Shift handoff documentation completed",
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process wizard step: {str(e)}",
        )


@router.post(
    "/{wizard_id}/enhance",
    summary="Enhance shift handoff text with AI",
    description="Use AI to professionalize and enhance shift handoff notes.",
)
async def enhance_shift_handoff_text(wizard_id: str, text_data: Dict[str, Any]):
    """Enhance text using AI service."""
    try:
        # Get AI service
        ai_service = get_service("ai")

        # Enhance text with medical context
        enhanced = await ai_service.enhance_clinical_text(
            text=text_data.get("text", ""),
            context="shift_handoff",
            specialty=text_data.get("specialty"),
        )

        return create_success_response(
            data={"original": text_data.get("text"), "enhanced": enhanced},
            message="Text enhanced successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance text: {str(e)}",
        )


@router.get(
    "/{wizard_id}/report",
    summary="Get shift handoff report",
    description="Retrieve the completed shift handoff report.",
)
async def get_shift_handoff_report(wizard_id: str):
    """Get completed shift handoff report."""
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        if "final_report" not in session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Shift handoff not yet completed",
            )

        return create_success_response(
            data={"handoff_report": session["final_report"]},
            message="Shift handoff report retrieved",
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}",
        )


async def _generate_handoff_report(collected_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate final shift handoff report from collected data."""
    # Compile all steps into structured handoff report
    report = {
        "report_type": "shift_handoff",
        "generated_at": datetime.now().isoformat(),
        "patient_identification": collected_data.get("step_1", {}),
        "current_condition": collected_data.get("step_2", {}),
        "treatments_interventions": collected_data.get("step_3", {}),
        "plan_priorities": collected_data.get("step_4", {}),
        "safety_considerations": collected_data.get("step_5", {}),
        "formatted_report": _format_handoff_narrative(collected_data),
    }

    return report


def _format_handoff_narrative(collected_data: Dict[str, Any]) -> str:
    """Format collected data into narrative handoff report."""
    sections = []

    # Section 1: Patient ID & Status
    step1 = collected_data.get("step_1", {})
    sections.append("PATIENT IDENTIFICATION & STATUS")
    sections.append("=" * 50)
    if step1:
        sections.append(f"Patient: {step1.get('patient_name', 'N/A')}")
        sections.append(f"Location: {step1.get('room_bed', 'N/A')}")
        sections.append(f"Age: {step1.get('age', 'N/A')}")
        sections.append(f"Diagnosis: {step1.get('diagnosis', 'N/A')}")
        sections.append(f"Admitted: {step1.get('admission_date', 'N/A')}")
        sections.append(f"Code Status: {step1.get('code_status', 'N/A')}")
    sections.append("")

    # Section 2: Current Condition
    step2 = collected_data.get("step_2", {})
    sections.append("CURRENT CONDITION")
    sections.append("=" * 50)
    if step2:
        sections.append(f"Condition: {step2.get('current_condition', 'N/A')}")
        sections.append(f"Vital Signs: {step2.get('vital_signs', 'N/A')}")
        sections.append(f"Pain Level: {step2.get('pain_level', 'N/A')}")
        sections.append(f"Mental Status: {step2.get('mental_status', 'N/A')}")
    sections.append("")

    # Section 3: Treatments & Interventions
    step3 = collected_data.get("step_3", {})
    sections.append("TREATMENTS & INTERVENTIONS")
    sections.append("=" * 50)
    if step3:
        sections.append(f"IV Access: {step3.get('iv_lines', 'N/A')}")
        sections.append(f"Medications: {step3.get('medications', 'N/A')}")
        sections.append(f"Recent Procedures: {step3.get('recent_procedures', 'N/A')}")
        sections.append(f"Pending Labs: {step3.get('pending_labs', 'N/A')}")
        sections.append(f"Pending Orders: {step3.get('pending_orders', 'N/A')}")
    sections.append("")

    # Section 4: Plan & Priorities
    step4 = collected_data.get("step_4", {})
    sections.append("PLAN & PRIORITIES")
    sections.append("=" * 50)
    if step4:
        sections.append(f"Care Priorities: {step4.get('care_priorities', 'N/A')}")
        sections.append(f"Scheduled Tasks: {step4.get('scheduled_tasks', 'N/A')}")
        sections.append(f"Patient Concerns: {step4.get('patient_concerns', 'N/A')}")
        sections.append(f"Family Involvement: {step4.get('family_involvement', 'N/A')}")
    sections.append("")

    # Section 5: Safety & Special Considerations
    step5 = collected_data.get("step_5", {})
    sections.append("SAFETY & SPECIAL CONSIDERATIONS")
    sections.append("=" * 50)
    if step5:
        sections.append(f"Fall Risk: {step5.get('fall_risk', 'N/A')}")
        sections.append(f"Isolation: {step5.get('isolation_precautions', 'N/A')}")
        sections.append(f"Allergies: {step5.get('allergies', 'N/A')}")
        sections.append(f"Special Equipment: {step5.get('special_equipment', 'N/A')}")
        sections.append(f"Other Concerns: {step5.get('other_concerns', 'N/A')}")
    sections.append("")

    sections.append("=" * 50)
    sections.append("Educational use only — not medical advice. No PHI stored.")
    sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    return "\n".join(sections)


# Export router
__all__ = ["router"]
