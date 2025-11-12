"""
Discharge Summary Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation

Guided discharge documentation for comprehensive discharge summaries.
Based on evidence-based discharge planning and continuity of care standards.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from src.services import get_service
from src.utils.api_responses import create_success_response
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

# Conditional imports
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


settings = get_settings()

router = APIRouter(
    prefix="/api/v1/wizards/discharge-summary",
    tags=["clinical-wizards"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid wizard step data"},
        500: {"description": "Wizard processing error"},
    },
)

try:
    from src.utils.redis_cache import get_redis_client

    _has_redis = True
except ImportError:
    _has_redis = False

_wizard_sessions: dict[str, dict[str, Any]] = {}

DISCHARGE_SUMMARY_STEPS = {
    1: {
        "step": 1,
        "title": "Patient & Admission Information",
        "prompt": "Document patient demographics and admission details",
        "fields": [
            "patient_name",
            "admission_date",
            "discharge_date",
            "length_of_stay",
            "attending_physician",
            "discharge_disposition",
        ],
        "help_text": "Start with basic patient info, admission/discharge dates, and discharge destination",
    },
    2: {
        "step": 2,
        "title": "Hospital Course",
        "prompt": "Summarize the patient's hospital course and treatment",
        "fields": [
            "admission_diagnosis",
            "hospital_course",
            "procedures_performed",
            "complications",
            "consults_obtained",
            "significant_events",
        ],
        "help_text": "Describe what happened during hospitalization, including treatments, procedures, and any complications",
    },
    3: {
        "step": 3,
        "title": "Discharge Status & Findings",
        "prompt": "Document patient's condition at discharge",
        "fields": [
            "discharge_diagnosis",
            "discharge_condition",
            "discharge_vital_signs",
            "pending_results",
            "discharge_labs",
            "functional_status",
        ],
        "help_text": "Record patient's final diagnoses, clinical status, and any pending tests or results",
    },
    4: {
        "step": 4,
        "title": "Discharge Medications & Instructions",
        "prompt": "List discharge medications and patient instructions",
        "fields": [
            "discharge_medications",
            "medication_changes",
            "diet_instructions",
            "activity_restrictions",
            "wound_care",
            "equipment_needs",
        ],
        "help_text": "Include all discharge meds, changes from admission, diet/activity restrictions, and special care instructions",
    },
    5: {
        "step": 5,
        "title": "Follow-up & Patient Education",
        "prompt": "Document follow-up plans and education provided",
        "fields": [
            "follow_up_appointments",
            "warning_signs",
            "patient_education_provided",
            "discharge_instructions_given",
            "patient_understanding",
            "caregiver_education",
        ],
        "help_text": "Note follow-up appointments, warning signs to watch for, education provided, and patient/caregiver understanding",
    },
}

EDU_BANNER = """
⚕️ EDUCATIONAL TOOL NOTICE ⚕️
This discharge summary wizard is an educational tool for healthcare professionals.
All discharge documentation should be reviewed and validated by qualified providers.
"""


async def _store_wizard_session(wizard_id: str, session_data: dict[str, Any]) -> bool:
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.setex(
                    f"wizard:discharge_summary:{wizard_id}", 7200, str(session_data)
                )
                return True
    except Exception:
        pass
    _wizard_sessions[wizard_id] = session_data
    return True


async def _get_wizard_session(wizard_id: str) -> dict[str, Any] | None:
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                session_str = await redis_client.get(f"wizard:discharge_summary:{wizard_id}")
                if session_str:
                    import ast

                    return ast.literal_eval(session_str)
    except Exception:
        pass
    return _wizard_sessions.get(wizard_id)


def _get_step_data(step: int) -> dict[str, Any]:
    if step not in DISCHARGE_SUMMARY_STEPS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid step: {step}")
    step_config = DISCHARGE_SUMMARY_STEPS[step]
    return {
        "step": step,
        "title": step_config["title"],
        "prompt": step_config["prompt"],
        "fields": step_config["fields"],
        "help_text": step_config["help_text"],
    }


def _generate_discharge_summary_report(collected_data: dict[str, Any]) -> dict[str, Any]:
    narrative = f"""
DISCHARGE SUMMARY

PATIENT INFORMATION
Name: {collected_data.get('patient_name', 'Not documented')}
Admission Date: {collected_data.get('admission_date', 'Not documented')}
Discharge Date: {collected_data.get('discharge_date', datetime.now().strftime('%Y-%m-%d'))}
Length of Stay: {collected_data.get('length_of_stay', 'Not documented')}
Attending Physician: {collected_data.get('attending_physician', 'Not documented')}
Discharge Disposition: {collected_data.get('discharge_disposition', 'Not documented')}

HOSPITAL COURSE
Admission Diagnosis: {collected_data.get('admission_diagnosis', 'Not documented')}
Hospital Course: {collected_data.get('hospital_course', 'Not documented')}
Procedures Performed: {collected_data.get('procedures_performed', 'None')}
Complications: {collected_data.get('complications', 'None')}
Consultations: {collected_data.get('consults_obtained', 'None')}
Significant Events: {collected_data.get('significant_events', 'None')}

DISCHARGE STATUS
Discharge Diagnosis: {collected_data.get('discharge_diagnosis', 'Not documented')}
Discharge Condition: {collected_data.get('discharge_condition', 'Not documented')}
Discharge Vital Signs: {collected_data.get('discharge_vital_signs', 'Not documented')}
Pending Results: {collected_data.get('pending_results', 'None')}
Discharge Labs: {collected_data.get('discharge_labs', 'Not documented')}
Functional Status: {collected_data.get('functional_status', 'Not documented')}

DISCHARGE MEDICATIONS & INSTRUCTIONS
Discharge Medications: {collected_data.get('discharge_medications', 'Not documented')}
Medication Changes: {collected_data.get('medication_changes', 'None')}
Diet: {collected_data.get('diet_instructions', 'Not documented')}
Activity: {collected_data.get('activity_restrictions', 'Not documented')}
Wound Care: {collected_data.get('wound_care', 'Not applicable')}
Equipment Needs: {collected_data.get('equipment_needs', 'None')}

FOLLOW-UP & EDUCATION
Follow-up Appointments: {collected_data.get('follow_up_appointments', 'Not documented')}
Warning Signs: {collected_data.get('warning_signs', 'Not documented')}
Patient Education: {collected_data.get('patient_education_provided', 'Not documented')}
Discharge Instructions: {collected_data.get('discharge_instructions_given', 'Provided')}
Patient Understanding: {collected_data.get('patient_understanding', 'Verbalized')}
Caregiver Education: {collected_data.get('caregiver_education', 'Not applicable')}

Completed by: [Provider Name]
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""
    return {
        "discharge_summary": collected_data,
        "narrative": narrative.strip(),
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "wizard_type": "discharge_summary",
        },
        "banner": EDU_BANNER,
    }


@router.post("/start", summary="Start Discharge Summary Wizard")
async def start_discharge_summary_wizard():
    try:
        wizard_id = str(uuid4())
        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "discharge_summary",
            "current_step": 1,
            "total_steps": 5,
            "collected_data": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        await _store_wizard_session(wizard_id, session_data)
        step_data = _get_step_data(1)
        response_data = {
            "wizard_session": session_data,
            "current_step": step_data,
            "progress": {"current": 1, "total": 5, "percentage": 20},
            "banner": EDU_BANNER,
        }
        return create_success_response(
            data=response_data, message="Discharge summary wizard started successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{wizard_id}/step", summary="Submit discharge summary step")
async def submit_discharge_summary_step(wizard_id: str, step_data: dict[str, Any]):
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        current_step = session["current_step"]
        session["collected_data"].update(step_data.get("data", {}))
        session["updated_at"] = datetime.now().isoformat()
        if current_step >= session["total_steps"]:
            report = _generate_discharge_summary_report(session["collected_data"])
            session["completed"] = True
            await _store_wizard_session(wizard_id, session)
            return create_success_response(
                data={
                    "wizard_session": session,
                    "report": report,
                    "progress": {
                        "current": current_step,
                        "total": session["total_steps"],
                        "percentage": 100,
                    },
                    "completed": True,
                },
                message="Discharge summary completed",
            )
        next_step = current_step + 1
        session["current_step"] = next_step
        await _store_wizard_session(wizard_id, session)
        return create_success_response(
            data={
                "wizard_session": session,
                "current_step": _get_step_data(next_step),
                "progress": {
                    "current": next_step,
                    "total": session["total_steps"],
                    "percentage": int((next_step / session["total_steps"]) * 100),
                },
            },
            message=f"Step {current_step} completed",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{wizard_id}/enhance", summary="Enhance discharge summary text")
async def enhance_discharge_summary_text(wizard_id: str, text_data: dict[str, Any]):
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        original_text = text_data.get("text", "")
        field_name = text_data.get("field", "text")
        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No text provided",
            )
        chat_service = get_service("chat")
        enhancement_prompt = f"Enhance this discharge summary field ({field_name}) to be professional and complete: {original_text}"
        chat_response = await chat_service.chat(
            message=enhancement_prompt,
            conversation_id=f"discharge_enhance_{wizard_id}",
            context={"wizard_id": wizard_id, "field": field_name},
        )
        enhanced_text = chat_response.get("response", original_text)
        return create_success_response(
            data={
                "original_text": original_text,
                "enhanced_text": enhanced_text,
                "field": field_name,
            },
            message="Text enhanced successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{wizard_id}/report", summary="Get discharge summary report")
async def get_discharge_summary_report(wizard_id: str):
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
        if not session.get("completed", False):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Wizard not completed",
            )
        report = _generate_discharge_summary_report(session["collected_data"])
        return create_success_response(
            data={"wizard_session": session, "report": report},
            message="Report retrieved successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


__all__ = ["router"]
