"""
SOAP Note Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation from SBAR and Shift Handoff wizards

SOAP (Subjective, Objective, Assessment, Plan) note documentation wizard
for comprehensive clinical progress notes. Evidence-based format for
interprofessional communication and continuity of care.
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
    prefix="/api/v1/wizards/soap-note",
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


# SOAP note wizard steps
SOAP_NOTE_STEPS = {
    1: {
        "step": 1,
        "title": "Subjective - Patient's Experience",
        "prompt": "Document the patient's subjective experience and reported symptoms",
        "fields": [
            "chief_complaint",
            "history_present_illness",
            "patient_reported_symptoms",
            "pain_description",
            "functional_status",
            "patient_concerns",
        ],
        "help_text": "Record what the patient tells you in their own words. Include chief complaint, symptoms, pain, and any concerns they express.",
    },
    2: {
        "step": 2,
        "title": "Objective - Clinical Observations",
        "prompt": "Record objective clinical findings and measurements",
        "fields": [
            "vital_signs",
            "physical_exam_findings",
            "lab_results",
            "imaging_results",
            "medication_administration",
            "procedures_performed",
        ],
        "help_text": "Document measurable data: vital signs, physical exam findings, lab/imaging results, medications given, procedures done.",
    },
    3: {
        "step": 3,
        "title": "Assessment - Clinical Analysis",
        "prompt": "Provide your clinical assessment and interpretation",
        "fields": [
            "primary_diagnosis",
            "differential_diagnoses",
            "problem_list",
            "progress_evaluation",
            "response_to_treatment",
            "complications_concerns",
        ],
        "help_text": "Analyze the data: primary diagnosis, other possibilities, current problems, patient's progress, treatment response, any concerns.",
    },
    4: {
        "step": 4,
        "title": "Plan - Care Plan and Next Steps",
        "prompt": "Outline the care plan and next steps",
        "fields": [
            "diagnostic_plan",
            "therapeutic_plan",
            "patient_education",
            "monitoring_plan",
            "follow_up",
            "consultations_needed",
        ],
        "help_text": "Detail the plan: further diagnostics needed, treatment changes, patient education, monitoring requirements, follow-up, consultations.",
    },
}


# Educational banner for all SOAP note outputs
EDU_BANNER = """
⚕️ EDUCATIONAL TOOL NOTICE ⚕️
This SOAP note wizard is an educational tool for healthcare professionals.
All clinical documentation should be reviewed and validated by qualified providers.
Never rely solely on automated tools for clinical decision-making or documentation.
"""


async def _store_wizard_session(wizard_id: str, session_data: dict[str, Any]) -> bool:
    """Store wizard session in Redis (preferred) or memory (fallback)"""
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                cache_key = f"wizard:soap_note:{wizard_id}"
                await redis_client.setex(cache_key, 7200, str(session_data))  # 2 hour TTL
                logger.info(f"Stored SOAP note wizard session {wizard_id} in Redis")
                return True
    except Exception as e:
        logger.warning(f"Failed to store session in Redis: {e}, using memory fallback")

    # Memory fallback
    _wizard_sessions[wizard_id] = session_data
    logger.info(f"Stored SOAP note wizard session {wizard_id} in memory")
    return True


async def _get_wizard_session(wizard_id: str) -> dict[str, Any] | None:
    """Retrieve wizard session from Redis (preferred) or memory (fallback)"""
    try:
        if _has_redis:
            redis_client = await get_redis_client()
            if redis_client:
                cache_key = f"wizard:soap_note:{wizard_id}"
                session_str = await redis_client.get(cache_key)
                if session_str:
                    import ast

                    return ast.literal_eval(session_str)
    except Exception as e:
        logger.warning(f"Failed to retrieve session from Redis: {e}, checking memory")

    # Memory fallback
    return _wizard_sessions.get(wizard_id)


def _get_step_data(step: int) -> dict[str, Any]:
    """Get step configuration data"""
    if step not in SOAP_NOTE_STEPS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid step number: {step}",
        )

    step_config = SOAP_NOTE_STEPS[step]
    return {
        "step": step,
        "title": step_config["title"],
        "prompt": step_config["prompt"],
        "fields": step_config["fields"],
        "help_text": step_config["help_text"],
    }


def _generate_soap_note_report(collected_data: dict[str, Any]) -> dict[str, Any]:
    """Generate final SOAP note report from collected data"""

    # Extract data by section
    subjective = {
        "chief_complaint": collected_data.get("chief_complaint", "Not documented"),
        "history_present_illness": collected_data.get("history_present_illness", "Not documented"),
        "patient_reported_symptoms": collected_data.get(
            "patient_reported_symptoms", "Not documented"
        ),
        "pain_description": collected_data.get("pain_description", "Not documented"),
        "functional_status": collected_data.get("functional_status", "Not documented"),
        "patient_concerns": collected_data.get("patient_concerns", "None reported"),
    }

    objective = {
        "vital_signs": collected_data.get("vital_signs", "Not documented"),
        "physical_exam_findings": collected_data.get("physical_exam_findings", "Not documented"),
        "lab_results": collected_data.get("lab_results", "Pending or not available"),
        "imaging_results": collected_data.get("imaging_results", "Pending or not available"),
        "medication_administration": collected_data.get(
            "medication_administration", "None documented"
        ),
        "procedures_performed": collected_data.get("procedures_performed", "None documented"),
    }

    assessment = {
        "primary_diagnosis": collected_data.get("primary_diagnosis", "Not documented"),
        "differential_diagnoses": collected_data.get("differential_diagnoses", "Not documented"),
        "problem_list": collected_data.get("problem_list", "Not documented"),
        "progress_evaluation": collected_data.get("progress_evaluation", "Not documented"),
        "response_to_treatment": collected_data.get("response_to_treatment", "Not documented"),
        "complications_concerns": collected_data.get("complications_concerns", "None identified"),
    }

    plan = {
        "diagnostic_plan": collected_data.get("diagnostic_plan", "Not documented"),
        "therapeutic_plan": collected_data.get("therapeutic_plan", "Not documented"),
        "patient_education": collected_data.get("patient_education", "Not documented"),
        "monitoring_plan": collected_data.get("monitoring_plan", "Not documented"),
        "follow_up": collected_data.get("follow_up", "Not documented"),
        "consultations_needed": collected_data.get("consultations_needed", "None at this time"),
    }

    # Generate formatted narrative
    narrative = f"""
SOAP NOTE
Date: {collected_data.get('note_date', datetime.now().strftime('%Y-%m-%d %H:%M'))}

SUBJECTIVE:
Chief Complaint: {subjective['chief_complaint']}

History of Present Illness: {subjective['history_present_illness']}

Patient-Reported Symptoms: {subjective['patient_reported_symptoms']}

Pain: {subjective['pain_description']}

Functional Status: {subjective['functional_status']}

Patient Concerns: {subjective['patient_concerns']}


OBJECTIVE:
Vital Signs: {objective['vital_signs']}

Physical Examination: {objective['physical_exam_findings']}

Laboratory Results: {objective['lab_results']}

Imaging Results: {objective['imaging_results']}

Medications Administered: {objective['medication_administration']}

Procedures Performed: {objective['procedures_performed']}


ASSESSMENT:
Primary Diagnosis: {assessment['primary_diagnosis']}

Differential Diagnoses: {assessment['differential_diagnoses']}

Problem List: {assessment['problem_list']}

Progress Evaluation: {assessment['progress_evaluation']}

Response to Treatment: {assessment['response_to_treatment']}

Complications/Concerns: {assessment['complications_concerns']}


PLAN:
Diagnostic Plan: {plan['diagnostic_plan']}

Therapeutic Plan: {plan['therapeutic_plan']}

Patient Education: {plan['patient_education']}

Monitoring Plan: {plan['monitoring_plan']}

Follow-up: {plan['follow_up']}

Consultations Needed: {plan['consultations_needed']}
"""

    return {
        "soap_note": {
            "subjective": subjective,
            "objective": objective,
            "assessment": assessment,
            "plan": plan,
        },
        "narrative": narrative.strip(),
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "note_date": collected_data.get("note_date", datetime.now().strftime("%Y-%m-%d %H:%M")),
            "wizard_type": "soap_note",
        },
        "banner": EDU_BANNER,
    }


@router.post("/start", summary="Start SOAP Note Wizard")
async def start_soap_note_wizard():
    """
    Initialize a new SOAP note documentation wizard session.

    SOAP (Subjective, Objective, Assessment, Plan) is the standard format
    for clinical progress notes used across healthcare settings.

    Returns a wizard session ID and first step configuration.
    """
    try:
        wizard_id = str(uuid4())

        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "soap_note",
            "current_step": 1,
            "total_steps": 4,
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
            "progress": {"current": 1, "total": 4, "percentage": 25},
            "banner": EDU_BANNER,
        }

        return create_success_response(
            data=response_data, message="SOAP note wizard started successfully"
        )

    except Exception as e:
        logger.error(f"Failed to start SOAP note wizard: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start SOAP note wizard: {str(e)}",
        )


@router.post("/{wizard_id}/step", summary="Submit SOAP note wizard step")
async def submit_soap_note_step(wizard_id: str, step_data: dict[str, Any]):
    """
    Submit data for current step and advance to next step.

    The wizard will validate the data, store it, and either:
    - Return the next step configuration (if more steps remain)
    - Return the complete SOAP note report (if all steps completed)
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

        # Check if we're done
        if current_step >= total_steps:
            # Generate final report
            report = _generate_soap_note_report(session["collected_data"])

            # Mark session as complete
            session["completed"] = True
            session["completed_at"] = datetime.now().isoformat()
            await _store_wizard_session(wizard_id, session)

            response_data = {
                "wizard_session": session,
                "report": report,
                "progress": {
                    "current": total_steps,
                    "total": total_steps,
                    "percentage": 100,
                },
                "completed": True,
            }

            return create_success_response(
                data=response_data, message="SOAP note completed successfully"
            )

        # Move to next step
        next_step = current_step + 1
        session["current_step"] = next_step
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
        logger.error(f"Failed to process SOAP note wizard step: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process wizard step: {str(e)}",
        )


@router.post("/{wizard_id}/enhance", summary="Enhance SOAP note text with AI")
async def enhance_soap_note_text(wizard_id: str, text_data: dict[str, Any]):
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
You are assisting with SOAP note documentation. Please enhance the following text
to be more professional and clinically appropriate while preserving the original meaning:

Field: {field_name}
Original text: {original_text}

Please provide an enhanced version that:
- Uses appropriate clinical terminology
- Is clear and concise
- Maintains professional tone
- Preserves all key information
- Follows SOAP note documentation standards

Enhanced text:"""

        # Call chat service for enhancement
        chat_response = await chat_service.chat(
            message=enhancement_prompt,
            conversation_id=f"soap_enhance_{wizard_id}",
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
        logger.error(f"Failed to enhance SOAP note text: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance text: {str(e)}",
        )


@router.get("/{wizard_id}/report", summary="Get SOAP note report")
async def get_soap_note_report(wizard_id: str):
    """
    Retrieve the completed SOAP note report.

    Only available after all wizard steps have been completed.
    Returns the structured SOAP note data and formatted narrative.
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
                detail="SOAP note wizard not yet completed. Complete all steps first.",
            )

        # Generate report
        report = _generate_soap_note_report(session["collected_data"])

        response_data = {
            "wizard_session": session,
            "report": report,
        }

        return create_success_response(
            data=response_data, message="SOAP note report retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve SOAP note report: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}",
        )


# Export router
__all__ = ["router"]
