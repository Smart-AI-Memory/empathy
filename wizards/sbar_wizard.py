"""
SBAR Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation

SBAR (Situation, Background, Assessment, Recommendation) documentation wizard
for clinical handoff communication and escalation to physicians.

This wizard includes a review step where users can preview the AI-enhanced report
before saving it.

Version: 2.0 - Nov 2025 - 5-step wizard with auto-preview and dictation support
"""

import json
import logging
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status
from src.services import get_service
from src.utils.api_responses import create_success_response
from src.utils.config import get_settings

logger = logging.getLogger(__name__)

# Settings following coding instructions
settings = get_settings()

router = APIRouter(
    prefix="/wizards/sbar",
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
    logger.info("✅ Redis client module imported for SBAR wizard sessions")
except ImportError:
    _has_redis = False
    logger.warning("⚠️ Redis unavailable for SBAR wizard - sessions will use memory only")

_wizard_sessions: dict[str, dict[str, Any]] = {}

# Log Redis configuration at module load
redis_url = os.getenv("REDIS_URL")
if redis_url:
    logger.info(f"🔧 REDIS_URL environment variable detected (starts with: {redis_url[:15]}...)")
else:
    logger.warning(
        "⚠️ REDIS_URL environment variable NOT SET - sessions will be lost between workers"
    )


# SBAR wizard steps - 5 steps total
SBAR_STEPS = {
    1: {
        "step": 1,
        "title": "Situation",
        "prompt": "Describe the current patient situation",
        "fields": [
            "patient_condition",
            "immediate_concerns",
            "vital_signs",
        ],
        "help_text": "What is happening right now with the patient? Include current condition, vital signs, and immediate concerns.",
    },
    2: {
        "step": 2,
        "title": "Background",
        "prompt": "Provide relevant clinical background",
        "fields": [
            "medical_history",
            "current_treatments",
            "baseline_condition",
        ],
        "help_text": "What is the clinical context? Include pertinent medical history, current treatments, and baseline condition.",
    },
    3: {
        "step": 3,
        "title": "Assessment",
        "prompt": "Your professional clinical assessment",
        "fields": [
            "clinical_assessment",
            "primary_concerns",
            "risk_factors",
        ],
        "help_text": "What do you think is happening? Include your nursing assessment, primary concerns, and risk factors.",
    },
    4: {
        "step": 4,
        "title": "Recommendation",
        "prompt": "What actions do you recommend?",
        "fields": [
            "recommendations",
            "requested_actions",
            "timeline",
        ],
        "help_text": "What needs to be done? Include specific recommendations, requested actions, and urgency timeline.",
    },
    5: {
        "step": 5,
        "title": "Review & Enhance",
        "prompt": "Review and enhance your SBAR report with AI",
        "fields": ["review_complete", "generate_enhanced"],
        "help_text": "Review all sections. Click 'Generate Enhanced Report' to see AI suggestions before saving.",
        "is_review_step": True,
    },
}


async def _store_wizard_session(wizard_id: str, session_data: dict[str, Any]):
    """Store wizard session in Redis or memory."""
    if _has_redis:
        try:
            redis_client = await get_redis_client()
            if redis_client:
                await redis_client.setex(
                    f"sbar_wizard:{wizard_id}",
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
                data = await redis_client.get(f"sbar_wizard:{wizard_id}")
                if data:
                    return json.loads(data)
        except Exception as e:
            logger.warning(f"Failed to retrieve session from Redis: {e}")

    # Fallback to memory
    return _wizard_sessions.get(wizard_id)


def _get_step_data(step_number: int) -> dict[str, Any]:
    """Get step configuration data."""
    if step_number not in SBAR_STEPS:
        raise ValueError(f"Invalid step number: {step_number}")

    return SBAR_STEPS[step_number]


@router.post(
    "/start",
    summary="Start SBAR Wizard",
    description="Initialize a new SBAR documentation workflow for clinical handoff communication.",
)
async def start_sbar_wizard():
    """Start SBAR wizard following Wizard Pattern Implementation."""
    try:
        wizard_id = str(uuid4())

        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "sbar",
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
            data=response_data, message="SBAR wizard started successfully"
        )

    except Exception as e:
        logger.error(f"Failed to start SBAR wizard: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start SBAR wizard: {str(e)}",
        )


@router.post(
    "/{wizard_id}/step",
    summary="Submit SBAR wizard step",
    description="Submit data for current step and advance to next step in SBAR workflow.",
)
async def submit_sbar_step(wizard_id: str, step_data: dict[str, Any]):
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

            # If next step is review step (step 5), generate and include the SBAR report
            if session["current_step"] == 5:
                # Auto-generate SBAR report for preview
                sbar_report = await _generate_sbar_report(wizard_id, session["collected_data"])
                next_step_data["sbar_report"] = sbar_report
                next_step_data["review_data"] = {
                    "situation": session["collected_data"].get("step_1", {}),
                    "background": session["collected_data"].get("step_2", {}),
                    "assessment": session["collected_data"].get("step_3", {}),
                    "recommendation": session["collected_data"].get("step_4", {}),
                }

            return create_success_response(
                data={
                    "wizard_session": session,
                    "current_step": next_step_data,
                    "progress": {
                        "current": session["current_step"],
                        "total": session["total_steps"],
                        "percentage": (session["current_step"] / session["total_steps"]) * 100,
                    },
                },
                message=f"Step {current_step} completed",
            )
        else:
            # Wizard complete on step 5 - mark as complete and return report
            sbar_report = await _generate_sbar_report(wizard_id, session["collected_data"])

            session["completed_at"] = datetime.now().isoformat()
            session["final_report"] = sbar_report
            await _store_wizard_session(wizard_id, session)

            return create_success_response(
                data={
                    "wizard_session": session,
                    "sbar_report": sbar_report,
                    "completed": True,
                },
                message="SBAR documentation completed successfully",
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to process wizard step: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process wizard step: {str(e)}",
        )


@router.post(
    "/{wizard_id}/enhance",
    summary="Generate enhanced SBAR report for review",
    description="Generate AI-enhanced SBAR report for user to review before saving.",
)
async def enhance_sbar_report(wizard_id: str):
    """
    Generate enhanced SBAR report with AI for review.
    This does NOT save the report - user must call /save endpoint after reviewing.
    """
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        # Verify we're on step 5
        if session["current_step"] != 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Can only enhance report on final step. Current step: {session['current_step']}",
            )

        # Generate SBAR report with AI enhancement
        sbar_report = await _generate_sbar_report(wizard_id, session["collected_data"])

        # Store enhanced report in session for review (but don't mark as completed yet)
        session["enhanced_report"] = sbar_report
        session["enhanced_at"] = datetime.now().isoformat()
        await _store_wizard_session(wizard_id, session)

        return create_success_response(
            data={
                "wizard_session": session,
                "sbar_report": sbar_report,
                "message": "Review the enhanced report below. Click 'Save Report' to finalize.",
            },
            message="Enhanced SBAR report generated for review",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enhance SBAR report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enhance SBAR report: {str(e)}",
        )


@router.post(
    "/{wizard_id}/save",
    summary="Save reviewed SBAR report",
    description="Save the enhanced SBAR report after user has reviewed it.",
)
async def save_sbar_report(wizard_id: str):
    """
    Save the enhanced SBAR report after user review.
    """
    try:
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session {wizard_id} not found",
            )

        # Verify enhanced report exists
        if "enhanced_report" not in session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No enhanced report found. Generate enhanced report first.",
            )

        # Mark as completed
        session["completed_at"] = datetime.now().isoformat()
        session["final_report"] = session["enhanced_report"]
        await _store_wizard_session(wizard_id, session)

        return create_success_response(
            data={
                "wizard_session": session,
                "sbar_report": session["final_report"],
                "completed": True,
            },
            message="SBAR report saved successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save SBAR report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save SBAR report: {str(e)}",
        )


@router.get(
    "/{wizard_id}/report",
    summary="Get SBAR report",
    description="Retrieve the completed SBAR report.",
)
async def get_sbar_report(wizard_id: str):
    """Get completed SBAR report."""
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
                detail="SBAR report not yet saved",
            )

        return create_success_response(
            data={"sbar_report": session["final_report"]},
            message="SBAR report retrieved",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve report: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {str(e)}",
        )


async def _generate_sbar_report(wizard_id: str, collected_data: dict[str, Any]) -> dict[str, Any]:
    """Generate SBAR report from collected data with AI enhancement."""
    logger.info(f"Generating SBAR report for wizard {wizard_id}")

    # Extract collected data
    step1 = collected_data.get("step_1", {})
    step2 = collected_data.get("step_2", {})
    step3 = collected_data.get("step_3", {})
    step4 = collected_data.get("step_4", {})

    logger.debug(f"SBAR data - Steps collected: {list(collected_data.keys())}")

    # Compile all steps into structured SBAR report
    report = {
        "report_type": "sbar",
        "generated_at": datetime.now().isoformat(),
        "sections": {
            "situation": step1,
            "background": step2,
            "assessment": step3,
            "recommendation": step4,
        },
        "situation": step1,
        "background": step2,
        "assessment": step3,
        "recommendation": step4,
        "formatted_report": _format_sbar_narrative(collected_data),
    }

    logger.debug(f"Formatted report length: {len(report['formatted_report'])} chars")

    # Try to enhance with AI
    try:
        sbar_service = get_service("sbar")
        if sbar_service:
            logger.info(f"Enhancing SBAR report for wizard {wizard_id}")

            enhancement_result = await sbar_service.enhance_sbar_report(report)

            if enhancement_result.get("enhanced"):
                report["ai_enhanced"] = True
                report["enhanced_report"] = enhancement_result.get("enhanced_report")
                report["model_used"] = enhancement_result.get("model")
                report["ai_usage"] = enhancement_result.get("usage")
                logger.info(f"SBAR report enhanced with {enhancement_result.get('model')}")
            else:
                report["ai_enhanced"] = False
                report["enhancement_note"] = enhancement_result.get(
                    "note", "Enhancement unavailable"
                )
                logger.warning(f"SBAR enhancement unavailable: {enhancement_result.get('note')}")
        else:
            logger.warning("SBAR service not available")
            report["ai_enhanced"] = False
            report["enhancement_note"] = "SBAR service not available"

    except Exception as e:
        logger.error(f"Failed to enhance SBAR report: {e}", exc_info=True)
        report["ai_enhanced"] = False
        report["enhancement_error"] = str(e)

    return report


def _format_sbar_narrative(collected_data: dict[str, Any]) -> str:
    """Format collected data into narrative SBAR report."""
    sections = []

    # Header
    sections.append("=" * 60)
    sections.append("SBAR CLINICAL COMMUNICATION REPORT")
    sections.append("=" * 60)
    sections.append("")

    # Situation
    step1 = collected_data.get("step_1", {})
    sections.append("SITUATION")
    sections.append("-" * 60)
    if step1:
        patient_condition = step1.get("patient_condition", "")
        immediate_concerns = step1.get("immediate_concerns", "")
        vital_signs = step1.get("vital_signs", "")

        if patient_condition or immediate_concerns:
            narrative = []
            if patient_condition:
                narrative.append(f"The patient is currently {patient_condition.strip()}.")
            if immediate_concerns:
                narrative.append(f"Immediate concerns include: {immediate_concerns.strip()}.")
            if vital_signs:
                narrative.append(f"Current vital signs: {vital_signs.strip()}.")
            sections.append(" ".join(narrative))
        else:
            sections.append("No situation data provided.")
    else:
        sections.append("No situation data provided.")
    sections.append("")

    # Background
    step2 = collected_data.get("step_2", {})
    sections.append("BACKGROUND")
    sections.append("-" * 60)
    if step2:
        medical_history = step2.get("medical_history", "")
        current_treatments = step2.get("current_treatments", "")
        baseline_condition = step2.get("baseline_condition", "")

        if medical_history or current_treatments or baseline_condition:
            narrative = []
            if medical_history:
                narrative.append(f"Patient medical history: {medical_history.strip()}.")
            if baseline_condition:
                narrative.append(f"Baseline condition: {baseline_condition.strip()}.")
            if current_treatments:
                narrative.append(f"Current treatments include: {current_treatments.strip()}.")
            sections.append(" ".join(narrative))
        else:
            sections.append("No background data provided.")
    else:
        sections.append("No background data provided.")
    sections.append("")

    # Assessment
    step3 = collected_data.get("step_3", {})
    sections.append("ASSESSMENT")
    sections.append("-" * 60)
    if step3:
        clinical_assessment = step3.get("clinical_assessment", "")
        primary_concerns = step3.get("primary_concerns", "")
        risk_factors = step3.get("risk_factors", "")

        if clinical_assessment or primary_concerns or risk_factors:
            narrative = []
            if clinical_assessment:
                narrative.append(f"Clinical assessment: {clinical_assessment.strip()}.")
            if primary_concerns:
                narrative.append(f"Primary concerns: {primary_concerns.strip()}.")
            if risk_factors:
                narrative.append(f"Risk factors identified: {risk_factors.strip()}.")
            sections.append(" ".join(narrative))
        else:
            sections.append("No assessment data provided.")
    else:
        sections.append("No assessment data provided.")
    sections.append("")

    # Recommendation
    step4 = collected_data.get("step_4", {})
    sections.append("RECOMMENDATION")
    sections.append("-" * 60)
    if step4:
        recommendations = step4.get("recommendations", "")
        requested_actions = step4.get("requested_actions", "")
        timeline = step4.get("timeline", "")

        if recommendations or requested_actions or timeline:
            narrative = []
            if recommendations:
                narrative.append(f"Recommended interventions: {recommendations.strip()}.")
            if requested_actions:
                narrative.append(f"Requested actions: {requested_actions.strip()}.")
            if timeline:
                narrative.append(f"Timeline: {timeline.strip()}.")
            sections.append(" ".join(narrative))
        else:
            sections.append("No recommendations provided.")
    else:
        sections.append("No recommendations provided.")
    sections.append("")

    sections.append("=" * 60)
    sections.append("Educational use only — not medical advice. No PHI stored.")
    sections.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    sections.append("=" * 60)

    return "\n".join(sections)


# Export router
__all__ = ["router"]
