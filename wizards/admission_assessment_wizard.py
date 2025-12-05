"""
Admission Assessment Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation from SOAP and Shift Handoff wizards

Structured patient admission workflow for comprehensive initial assessment.
Based on evidence-based nursing admission assessment standards.
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
    prefix="/wizards/admission-assessment",
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

_wizard_sessions: dict[str, dict[str, Any]] = {}


# Admission assessment wizard steps
ADMISSION_ASSESSMENT_STEPS = {
    1: {
        "step": 1,
        "title": "Patient Demographics & Chief Complaint",
        "prompt": "Gather patient identification and reason for admission",
        "fields": [
            "patient_name",
            "date_of_birth",
            "gender",
            "admission_date",
            "chief_complaint",
            "referring_provider",
        ],
        "help_text": "Start with basic patient information and primary reason for admission",
    },
    2: {
        "step": 2,
        "title": "Medical History & Medications",
        "prompt": "Document past medical history and current medications",
        "fields": [
            "past_medical_history",
            "past_surgical_history",
            "current_medications",
            "allergies",
            "immunization_status",
            "family_history",
        ],
        "help_text": "Include chronic conditions, previous surgeries, all medications, allergies, and relevant family history",
    },
    3: {
        "step": 3,
        "title": "Review of Systems",
        "prompt": "Conduct comprehensive systems review",
        "fields": [
            "cardiovascular",
            "respiratory",
            "gastrointestinal",
            "genitourinary",
            "neurological",
            "musculoskeletal",
            "integumentary",
            "psychosocial",
        ],
        "help_text": "Document findings for each body system. Note any abnormalities or patient concerns.",
    },
    4: {
        "step": 4,
        "title": "Physical Assessment & Vital Signs",
        "prompt": "Record initial physical examination and vital signs",
        "fields": [
            "vital_signs",
            "height_weight",
            "general_appearance",
            "physical_exam_findings",
            "pain_assessment",
            "fall_risk_score",
        ],
        "help_text": "Include complete vital signs, measurements, general appearance, and initial physical findings",
    },
    5: {
        "step": 5,
        "title": "Psychosocial & Discharge Planning",
        "prompt": "Assess psychosocial factors and begin discharge planning",
        "fields": [
            "living_situation",
            "support_system",
            "advance_directives",
            "code_status",
            "barriers_to_care",
            "discharge_planning_needs",
        ],
        "help_text": "Document living situation, support systems, advance care planning, and anticipated discharge needs",
    },
    6: {
        "step": 6,
        "title": "Initial Care Plan & Orders",
        "prompt": "Establish initial nursing care plan and verify orders",
        "fields": [
            "nursing_diagnoses",
            "care_priorities",
            "patient_goals",
            "pending_orders",
            "patient_education_needs",
            "follow_up_required",
        ],
        "help_text": "Identify nursing diagnoses, set priorities, establish patient-centered goals, and note education needs",
    },
    7: {
        "step": 7,
        "title": "Review & Finalize",
        "prompt": "Review your admission assessment and finalize the document",
        "fields": ["review_complete", "user_approved"],
        "help_text": "Review all sections of the admission assessment. Click 'Generate Preview' to see the formatted assessment. You can go back to edit any section before finalizing.",
        "is_review_step": True,
    },
}


# Educational banner for all admission assessment outputs
EDU_BANNER = """
⚕️ EDUCATIONAL TOOL NOTICE ⚕️
This admission assessment wizard is an educational tool for healthcare professionals.
All clinical assessments should be reviewed and validated by qualified providers.
Never rely solely on automated tools for clinical decision-making or documentation.
"""


async def _store_wizard_session(wizard_id: str, session_data: dict[str, Any]) -> bool:
    """Store wizard session in Redis (preferred) or memory (fallback)"""
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                import json

                cache_key = f"wizard:admission_assessment:{wizard_id}"
                await redis_client.setex(
                    cache_key, 7200, json.dumps(session_data)  # 2 hour TTL - FIXED: use JSON
                )
                logger.info(f"Stored admission assessment wizard session {wizard_id} in Redis")
                return True
    except Exception as e:
        logger.warning(f"Failed to store session in Redis: {e}, using memory fallback")

    # Memory fallback
    _wizard_sessions[wizard_id] = session_data
    logger.info(f"Stored admission assessment wizard session {wizard_id} in memory")
    return True


async def _get_wizard_session(wizard_id: str) -> dict[str, Any] | None:
    """Retrieve wizard session from Redis (preferred) or memory (fallback)"""
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                import json

                cache_key = f"wizard:admission_assessment:{wizard_id}"
                session_str = await redis_client.get(cache_key)
                if session_str:
                    # SECURITY FIX: Use json.loads() instead of ast.literal_eval()
                    return json.loads(session_str)
    except Exception as e:
        logger.warning(f"Failed to retrieve session from Redis: {e}, checking memory")

    # Memory fallback
    return _wizard_sessions.get(wizard_id)


def _get_step_data(step: int) -> dict[str, Any]:
    """Get step configuration data"""
    if step not in ADMISSION_ASSESSMENT_STEPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid step number: {step}",
        )

    step_config = ADMISSION_ASSESSMENT_STEPS[step]
    return {
        "step": step,
        "title": step_config["title"],
        "prompt": step_config["prompt"],
        "fields": step_config["fields"],
        "help_text": step_config["help_text"],
    }


def _generate_admission_assessment_report(collected_data: dict[str, Any]) -> dict[str, Any]:
    """Generate final admission assessment report from collected data"""

    # Generate formatted narrative
    narrative = f"""
ADMISSION ASSESSMENT
Date: {collected_data.get('admission_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}

PATIENT DEMOGRAPHICS
Name: {collected_data.get('patient_name', 'Not documented')}
Date of Birth: {collected_data.get('date_of_birth', 'Not documented')}
Gender: {collected_data.get('gender', 'Not documented')}
Chief Complaint: {collected_data.get('chief_complaint', 'Not documented')}
Referring Provider: {collected_data.get('referring_provider', 'Not documented')}

MEDICAL HISTORY
Past Medical History: {collected_data.get('past_medical_history', 'Not documented')}
Past Surgical History: {collected_data.get('past_surgical_history', 'Not documented')}
Current Medications: {collected_data.get('current_medications', 'Not documented')}
Allergies: {collected_data.get('allergies', 'NKDA')}
Immunizations: {collected_data.get('immunization_status', 'Not documented')}
Family History: {collected_data.get('family_history', 'Not documented')}

REVIEW OF SYSTEMS
Cardiovascular: {collected_data.get('cardiovascular', 'Not documented')}
Respiratory: {collected_data.get('respiratory', 'Not documented')}
Gastrointestinal: {collected_data.get('gastrointestinal', 'Not documented')}
Genitourinary: {collected_data.get('genitourinary', 'Not documented')}
Neurological: {collected_data.get('neurological', 'Not documented')}
Musculoskeletal: {collected_data.get('musculoskeletal', 'Not documented')}
Integumentary: {collected_data.get('integumentary', 'Not documented')}
Psychosocial: {collected_data.get('psychosocial', 'Not documented')}

PHYSICAL ASSESSMENT
Vital Signs: {collected_data.get('vital_signs', 'Not documented')}
Height/Weight: {collected_data.get('height_weight', 'Not documented')}
General Appearance: {collected_data.get('general_appearance', 'Not documented')}
Physical Exam: {collected_data.get('physical_exam_findings', 'Not documented')}
Pain Assessment: {collected_data.get('pain_assessment', 'Not documented')}
Fall Risk Score: {collected_data.get('fall_risk_score', 'Not assessed')}

PSYCHOSOCIAL & DISCHARGE PLANNING
Living Situation: {collected_data.get('living_situation', 'Not documented')}
Support System: {collected_data.get('support_system', 'Not documented')}
Advance Directives: {collected_data.get('advance_directives', 'Not documented')}
Code Status: {collected_data.get('code_status', 'Not documented')}
Barriers to Care: {collected_data.get('barriers_to_care', 'None identified')}
Discharge Planning Needs: {collected_data.get('discharge_planning_needs', 'Not documented')}

INITIAL CARE PLAN
Nursing Diagnoses: {collected_data.get('nursing_diagnoses', 'Not documented')}
Care Priorities: {collected_data.get('care_priorities', 'Not documented')}
Patient Goals: {collected_data.get('patient_goals', 'Not documented')}
Pending Orders: {collected_data.get('pending_orders', 'None noted')}
Patient Education Needs: {collected_data.get('patient_education_needs', 'Not documented')}
Follow-up Required: {collected_data.get('follow_up_required', 'Not documented')}

Completed by: [Nurse Name]
Date/Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}
"""

    return {
        "admission_assessment": collected_data,
        "narrative": narrative.strip(),
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "admission_date": collected_data.get(
                "admission_date", datetime.now().strftime("%Y-%m-%d %H:%M")
            ),
            "wizard_type": "admission_assessment",
        },
        "banner": EDU_BANNER,
    }


@router.post("/start", summary="Start Admission Assessment Wizard")
async def start_admission_assessment_wizard():
    """
    Initialize a new admission assessment documentation wizard session.

    Admission assessment is the comprehensive initial evaluation performed
    when a patient is admitted to a healthcare facility.

    Returns a wizard session ID and first step configuration.
    """
    try:
        wizard_id = str(uuid4())

        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "admission_assessment",
            "current_step": 1,
            "total_steps": 7,
            "collected_data": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }

        # Store session
        await _store_wizard_session(wizard_id, session_data)

        # Get first step data
        step_data = _get_step_data(1)

        response_data = {
            "wizard_session": session_data,
            "current_step": step_data,
            "progress": {"current": 1, "total": 6, "percentage": 17},
            "banner": EDU_BANNER,
        }

        return create_success_response(
            data=response_data,
            message="Admission assessment wizard started successfully",
        )

    except Exception as e:
        logger.error(f"Failed to start admission assessment wizard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start admission assessment wizard: {str(e)}",
        )


@router.post("/{wizard_id}/step", summary="Submit admission assessment wizard step")
async def submit_admission_assessment_step(wizard_id: str, step_data: dict[str, Any]):
    """
    Submit data for current step and advance to next step.

    The wizard will validate the data, store it, and either:
    - Return the next step configuration (if more steps remain)
    - Return the complete admission assessment report (if all steps completed)
    """
    try:
        # Retrieve session
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        current_step = session["current_step"]
        total_steps = session["total_steps"]

        # Validate step number
        submitted_step = step_data.get("step", current_step)
        if submitted_step != current_step:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Expected step {current_step}, got step {submitted_step}",
            )

        # Store submitted data
        session["collected_data"].update(step_data.get("data", {}))
        session["updated_at"] = datetime.now().isoformat()

        # Advance to next step (but don't auto-complete, even on final step)
        if current_step < total_steps:
            next_step = current_step + 1
            session["current_step"] = next_step
        else:
            # On review step - stay on same step, don't auto-complete
            next_step = current_step

        await _store_wizard_session(wizard_id, session)

        # Get next step configuration
        next_step_data = _get_step_data(next_step)

        response_data = {
            "wizard_session": session,
            "current_step": next_step_data,
            "progress": {
                "current": next_step,
                "total": total_steps,
                "percentage": int((next_step / total_steps) * 100),
            },
        }

        return create_success_response(
            data=response_data,
            message=f"Step {current_step} completed, moved to step {next_step}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process admission assessment wizard step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process wizard step: {str(e)}",
        )


@router.post("/{wizard_id}/enhance", summary="Enhance admission assessment text with AI")
async def enhance_admission_assessment_text(wizard_id: str, text_data: dict[str, Any]):
    """
    Enhance user-provided text with AI to improve clinical documentation quality.

    Uses the chat service to refine language, add clinical terminology,
    and improve clarity while preserving the original meaning.
    """
    try:
        # Verify wizard session exists
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        original_text = text_data.get("text", "")
        field_name = text_data.get("field", "text")

        if not original_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No text provided for enhancement",
            )

        # Get chat service
        chat_service = get_service("chat")

        # Create enhancement prompt
        enhancement_prompt = f"""
You are assisting with admission assessment documentation. Please enhance the following text
to be more professional and clinically appropriate while preserving the original meaning:

Field: {field_name}
Original text: {original_text}

Please provide an enhanced version that:
- Uses appropriate clinical terminology
- Is clear and concise
- Maintains professional tone
- Preserves all key information
- Follows nursing admission assessment documentation standards

Enhanced text:"""

        # Call chat service for enhancement
        chat_response = await chat_service.chat(
            message=enhancement_prompt,
            conversation_id=f"admission_enhance_{wizard_id}",
            context={"wizard_id": wizard_id, "field": field_name},
        )

        enhanced_text = chat_response.get("response", original_text)

        response_data = {
            "original_text": original_text,
            "enhanced_text": enhanced_text,
            "field": field_name,
        }

        return create_success_response(data=response_data, message="Text enhanced successfully")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enhance admission assessment text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance text: {str(e)}",
        )


@router.post("/{wizard_id}/preview", summary="Preview admission assessment report")
async def preview_admission_assessment_report(wizard_id: str):
    """
    Generate preview of admission assessment report without finalizing.

    This endpoint allows users to see the formatted admission assessment before
    finalizing it. The report is NOT marked as complete. Users can
    still go back and edit data after previewing.
    """
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Verify user is on review step
        if session["current_step"] != session["total_steps"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not on review step. Complete steps 1-{session['total_steps']-1} first.",
            )

        # Generate preview report (does NOT mark as complete)
        preview_report = _generate_admission_assessment_report(session["collected_data"])

        # Store preview in session
        session["preview_report"] = preview_report
        session["preview_generated_at"] = datetime.now().isoformat()
        await _store_wizard_session(wizard_id, session)

        response_data = {
            "preview": preview_report,
            "wizard_session": session,
            "message": "Review the admission assessment above. Click 'Finalize Report' to save, or go back to edit any section.",
        }

        return create_success_response(data=response_data, message="Preview generated successfully")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{wizard_id}/save", summary="Finalize admission assessment report")
async def save_admission_assessment_report(wizard_id: str, approval_data: dict[str, Any]):
    """
    Finalize and save the admission assessment report after user review and approval.

    Requires that the user has:
    1. Generated a preview first (/preview endpoint)
    2. Explicitly approved the report (user_approved: true)

    Only after calling this endpoint is the report marked as complete.
    """
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")

        # Verify preview was generated
        if "preview_report" not in session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must generate preview before saving. Call /preview endpoint first.",
            )

        # Verify user explicitly approved
        if not approval_data.get("user_approved", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User approval required. Set 'user_approved': true in request body.",
            )

        # NOW we mark as complete
        session["completed"] = True
        session["completed_at"] = datetime.now().isoformat()
        session["final_report"] = session["preview_report"]
        session["user_approved"] = True

        await _store_wizard_session(wizard_id, session)

        response_data = {
            "wizard_session": session,
            "report": session["final_report"],
            "completed": True,
        }

        return create_success_response(
            data=response_data, message="Admission assessment finalized successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{wizard_id}/report", summary="Get admission assessment report")
async def get_admission_assessment_report(wizard_id: str):
    """
    Retrieve the completed admission assessment report.

    Only available after all wizard steps have been completed.
    Returns the structured assessment data and formatted narrative.
    """
    try:
        # Retrieve session
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        # Check if completed
        if not session.get("completed", False):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Admission assessment wizard not yet completed. Complete all steps first.",
            )

        # Generate report
        report = _generate_admission_assessment_report(session["collected_data"])

        response_data = {
            "wizard_session": session,
            "report": report,
        }

        return create_success_response(
            data=response_data,
            message="Admission assessment report retrieved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve admission assessment report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}",
        )


# Export router
__all__ = ["router"]
