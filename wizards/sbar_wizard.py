"""
SBAR Wizard Router - AI Nurse Florence
Following Wizard Pattern Implementation from copilot-instructions.md
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, Optional
from uuid import uuid4
from datetime import datetime

from src.services import get_service
from src.models.schemas import (
    SBARWizardRequest,
    SBARWizardResponse
)
from src.utils.api_responses import create_success_response
from src.utils.exceptions import ServiceException
from src.utils.config import get_settings

# Conditional translation import
try:
    from src.services.translation_service import translate_text
    _has_translation = True
except ImportError:
    _has_translation = False
    async def translate_text(text: str, target_language: str, source_language: str = "en", context: str = "medical"):
        return {"translated_text": text, "success": False}

# Settings following coding instructions
settings = get_settings()

router = APIRouter(
    prefix="/api/v1/wizards/sbar",
    tags=["clinical-wizards"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid wizard step data"},
        500: {"description": "Wizard processing error"}
    }
)

# Session storage (Redis in production, memory for development)
# Following Conditional Imports Pattern
try:
    from src.utils.redis_cache import get_redis_client
    _has_redis = True
except ImportError:
    _has_redis = False

_wizard_sessions: Dict[str, Dict[str, Any]] = {}

@router.post(
    "/start",
    response_model=SBARWizardResponse,
    summary="Start SBAR Documentation Wizard",
    description="Initialize a new SBAR (Situation, Background, Assessment, Recommendation) documentation workflow."
)
async def start_sbar_wizard():
    """Start SBAR wizard following Wizard Pattern Implementation."""
    try:
        wizard_id = str(uuid4())
        
        session_data = {
            "wizard_id": wizard_id,
            "wizard_type": "sbar",
            "current_step": 1,
            "total_steps": 4,
            "collected_data": {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Store session following Conditional Imports Pattern
        await _store_wizard_session(wizard_id, session_data)
        
        # Get first step prompt
        step_data = _get_step_data(1)
        
        response_data = {
            "wizard_session": session_data,
            "current_step": step_data,
            "progress": {"current": 1, "total": 4, "percentage": 25}
        }
        
        return create_success_response(
            data=response_data,
            message="SBAR documentation wizard started successfully"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start SBAR wizard: {str(e)}"
        )

@router.post(
    "/{wizard_id}/step",
    response_model=SBARWizardResponse,
    summary="Submit SBAR wizard step",
    description="Submit data for current step and advance to next step in SBAR workflow."
)
async def submit_wizard_step(
    wizard_id: str,
    step_data: SBARWizardRequest
):
    """Submit wizard step following Wizard Pattern Implementation."""
    try:
        # Get session
        session = await _get_wizard_session(wizard_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Wizard session not found: {wizard_id}"
            )
        
        current_step = session["current_step"]
        
        # Validate step data
        if step_data.step_number != current_step:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Expected step {current_step}, received step {step_data.step_number}"
            )
        
        # Store step data
        step_key = f"step_{current_step}"
        session["collected_data"][step_key] = step_data.data
        session["updated_at"] = datetime.now().isoformat()
        
        # Advance to next step
        next_step = current_step + 1
        session["current_step"] = next_step
        
        await _store_wizard_session(wizard_id, session)
        
        if next_step <= session["total_steps"]:
            # Get next step data
            next_step_data = _get_step_data(next_step)
            
            response_data = {
                "wizard_session": session,
                "current_step": next_step_data,
                "progress": {
                    "current": next_step,
                    "total": session["total_steps"],
                    "percentage": (next_step / session["total_steps"]) * 100
                }
            }
            
            return create_success_response(
                data=response_data,
                message=f"Step {current_step} completed, advancing to step {next_step}"
            )
        else:
            # Wizard complete
            return await _complete_sbar_wizard(wizard_id, session)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process wizard step: {str(e)}"
        )

@router.get(
    "/{wizard_id}/status",
    response_model=Dict[str, Any],
    summary="Get SBAR wizard status",
    description="Retrieve current status and progress of SBAR wizard session."
)
async def get_wizard_status(wizard_id: str):
    """Get wizard session status following Wizard Pattern Implementation."""
    
    session = await _get_wizard_session(wizard_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Wizard session not found: {wizard_id}"
        )
    
    return create_success_response(
        data={
            "wizard_session": session,
            "progress": {
                "current": session["current_step"],
                "total": session["total_steps"],
                "percentage": (session["current_step"] / session["total_steps"]) * 100
            }
        }
    )

async def _get_wizard_session(wizard_id: str) -> Optional[Dict[str, Any]]:
    """Get wizard session from storage following Conditional Imports Pattern."""
    if _has_redis:
        try:
            redis_client = get_redis_client()
            if redis_client:
                session_data = await redis_client.get(f"sbar_wizard:{wizard_id}")
                return session_data if session_data else None
        except Exception:
            pass
    
    return _wizard_sessions.get(wizard_id)

async def _store_wizard_session(wizard_id: str, session_data: Dict[str, Any]) -> None:
    """Store wizard session following Conditional Imports Pattern."""
    if _has_redis:
        try:
            redis_client = get_redis_client()
            if redis_client:
                await redis_client.setex(f"sbar_wizard:{wizard_id}", 3600, session_data)
                return
        except Exception:
            pass
    
    _wizard_sessions[wizard_id] = session_data

async def _complete_sbar_wizard(wizard_id: str, session: Dict[str, Any]) -> Dict[str, Any]:
    """Complete SBAR wizard and generate final report."""
    
    try:
        # Generate SBAR report from collected data
        sbar_report = _generate_sbar_report(session["collected_data"])
        
        # Enhance with SBAR service if available
        sbar_service = get_service("sbar")
        if sbar_service:
            enhanced_report = await sbar_service.enhance_sbar_report(sbar_report)
            sbar_report.update(enhanced_report)
        
        # Mark session as complete
        session["current_step"] = "complete"
        session["completed_at"] = datetime.now().isoformat()
        session["final_report"] = sbar_report
        
        await _store_wizard_session(wizard_id, session)
        
        return create_success_response(
            data={
                "wizard_session": session,
                "sbar_report": sbar_report,
                "message": "SBAR documentation completed successfully"
            },
            message="SBAR wizard completed successfully"
        )
        
    except Exception:
        raise ServiceException("Failed to complete SBAR wizard", "sbar_wizard")

def _get_step_data(step_number: int) -> Dict[str, Any]:
    """Get step-specific data and prompts following SBAR framework."""
    
    steps = {
        1: {
            "step_number": 1,
            "step_name": "Situation",
            "title": "Current Situation",
            "description": "Describe the current patient situation and immediate concerns",
            "prompts": [
                "What is the patient's current condition?",
                "What brought the patient to your attention?",
                "What are the immediate concerns or changes?",
                "What is the patient's current status?"
            ],
            "fields": [
                {"name": "patient_condition", "type": "textarea", "required": True, 
                 "label": "Current patient condition", "placeholder": "Describe the patient's current state..."},
                {"name": "immediate_concerns", "type": "textarea", "required": True, 
                 "label": "Immediate concerns", "placeholder": "What concerns brought this to your attention?"},
                {"name": "vital_signs", "type": "text", "required": False, 
                 "label": "Current vital signs", "placeholder": "BP, HR, RR, Temp, O2 Sat"}
            ]
        },
        2: {
            "step_number": 2,
            "step_name": "Background", 
            "title": "Clinical Background",
            "description": "Provide relevant clinical background and history",
            "prompts": [
                "What is the patient's medical history?",
                "What treatments have been provided?",
                "What are the relevant clinical details?",
                "What is the patient's baseline condition?"
            ],
            "fields": [
                {"name": "medical_history", "type": "textarea", "required": True, 
                 "label": "Relevant medical history", "placeholder": "Include pertinent diagnoses, allergies, medications..."},
                {"name": "current_treatments", "type": "textarea", "required": True, 
                 "label": "Current treatments/interventions", "placeholder": "What has been done so far?"},
                {"name": "baseline_condition", "type": "textarea", "required": False, 
                 "label": "Patient's baseline condition", "placeholder": "How does this compare to the patient's normal state?"}
            ]
        },
        3: {
            "step_number": 3,
            "step_name": "Assessment",
            "title": "Clinical Assessment", 
            "description": "Your professional assessment of the situation",
            "prompts": [
                "What is your clinical assessment?",
                "What do you think is happening?",
                "What are your concerns?",
                "What is your professional judgment?"
            ],
            "fields": [
                {"name": "clinical_assessment", "type": "textarea", "required": True, 
                 "label": "Your clinical assessment", "placeholder": "Based on your nursing judgment, what do you think is happening?"},
                {"name": "primary_concerns", "type": "textarea", "required": True, 
                 "label": "Primary clinical concerns", "placeholder": "What are you most worried about?"},
                {"name": "risk_factors", "type": "textarea", "required": False, 
                 "label": "Identified risk factors", "placeholder": "What factors increase risk or complicate care?"}
            ]
        },
        4: {
            "step_number": 4,
            "step_name": "Recommendation",
            "title": "Recommendations",
            "description": "What actions do you recommend?",
            "prompts": [
                "What do you need from the physician?",
                "What actions should be taken?",
                "What is the timeline for action?",
                "What are your specific recommendations?"
            ],
            "fields": [
                {"name": "recommendations", "type": "textarea", "required": True, 
                 "label": "Specific recommendations", "placeholder": "What specific actions do you recommend?"},
                {"name": "requested_actions", "type": "textarea", "required": True, 
                 "label": "Requested physician actions", "placeholder": "What do you need the physician to do?"},
                {"name": "timeline", "type": "select", "required": True, "label": "Urgency level",
                 "options": ["Immediate", "Within 30 minutes", "Within 1 hour", "Within 4 hours", "Routine"]}
            ]
        }
    }
    
    return steps.get(step_number, {})

def _generate_sbar_report(collected_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate structured SBAR report from collected data."""
    
    report = {
        "report_type": "SBAR",
        "generated_at": datetime.now().isoformat(),
        "sections": {},
        "metadata": {
            "framework": "SBAR (Situation, Background, Assessment, Recommendation)",
            "purpose": "Clinical communication and handoff documentation"
        }
    }
    
    # Extract data from each step
    for step_num in range(1, 5):
        step_key = f"step_{step_num}"
        if step_key in collected_data:
            step_name = _get_step_data(step_num)["step_name"]
            report["sections"][step_name.lower()] = collected_data[step_key]
    
    # Generate summary
    report["summary"] = _generate_sbar_summary(report["sections"])
    
    return report

def _generate_sbar_summary(sections: Dict[str, Any]) -> str:
    """Generate executive summary of SBAR report."""
    
    summary_parts = []
    
    if "situation" in sections:
        condition = sections["situation"].get("patient_condition", "Not specified")
        summary_parts.append(f"Situation: {condition[:100]}...")
    
    if "assessment" in sections:
        assessment = sections["assessment"].get("clinical_assessment", "Not specified")
        summary_parts.append(f"Assessment: {assessment[:100]}...")
    
    if "recommendation" in sections:
        timeline = sections["recommendation"].get("timeline", "Not specified")
        summary_parts.append(f"Urgency: {timeline}")
    
    return " | ".join(summary_parts)