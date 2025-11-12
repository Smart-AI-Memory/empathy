"""
Clinical Assessment Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
Comprehensive patient assessment workflows with AI-powered clinical analysis
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.openai_client import clinical_decision_support
from ...utils.config import get_educational_banner

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wizard/clinical-assessment",
    tags=["wizards", "clinical-assessment"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"},
    },
)

# Wizard session storage (Redis in production)
_wizard_sessions: dict[str, dict[str, Any]] = {}


class AssessmentStepData(BaseModel):
    """Data model for assessment step submission."""

    step_data: dict[str, Any]


@router.post("/start")
async def start_clinical_assessment():
    """Start clinical assessment wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "clinical_assessment",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 5,
        "completed_steps": [],
        "data": {
            "vital_signs": {},
            "physical_assessment": {},
            "systems_review": {},
            "pain_assessment": {},
            "functional_assessment": {},
        },
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "clinical_assessment",
        "current_step": 1,
        "total_steps": 5,
        "step_title": "Vital Signs",
        "step_description": "Record patient vital signs and initial observations",
        "fields": [
            {"name": "temperature", "type": "number", "unit": "°F", "required": True},
            {"name": "pulse", "type": "number", "unit": "bpm", "required": True},
            {"name": "respirations", "type": "number", "unit": "/min", "required": True},
            {"name": "blood_pressure_systolic", "type": "number", "unit": "mmHg", "required": True},
            {
                "name": "blood_pressure_diastolic",
                "type": "number",
                "unit": "mmHg",
                "required": True,
            },
            {"name": "oxygen_saturation", "type": "number", "unit": "%", "required": True},
            {"name": "pain_scale", "type": "number", "min": 0, "max": 10, "required": True},
        ],
        "educational_note": "Vital signs should be compared to patient's baseline and age-appropriate norms.",
    }


@router.get("/{wizard_id}/status")
async def get_clinical_assessment_status(wizard_id: str):
    """Get clinical assessment wizard status following Wizard Pattern Implementation."""

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
        "status": (
            "completed"
            if len(session["completed_steps"]) == session["total_steps"]
            else "in_progress"
        ),
        "data": session["data"],
    }


@router.post("/{wizard_id}/step/{step_number}")
async def submit_clinical_assessment_step(
    wizard_id: str, step_number: int, step_data: AssessmentStepData
):
    """Submit clinical assessment step data following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number != session["current_step"]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid step. Expected step {session['current_step']}, got step {step_number}",
        )

    # Store step data based on step number
    step_mapping = {
        1: "vital_signs",
        2: "physical_assessment",
        3: "systems_review",
        4: "pain_assessment",
        5: "functional_assessment",
    }

    if step_number in step_mapping:
        session["data"][step_mapping[step_number]] = step_data.step_data

    # Mark step as completed
    if step_number not in session["completed_steps"]:
        session["completed_steps"].append(step_number)

    # Generate AI analysis for the submitted step
    ai_analysis = await _generate_ai_analysis(step_number, step_data.step_data, session["data"])

    # Move to next step
    if step_number < session["total_steps"]:
        session["current_step"] = step_number + 1
        next_step_info = _get_step_info(step_number + 1)
    else:
        next_step_info = None

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_completed": step_number,
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": (
            "completed"
            if len(session["completed_steps"]) == session["total_steps"]
            else "in_progress"
        ),
        "ai_analysis": ai_analysis,
        "next_step": next_step_info,
    }


@router.get("/{wizard_id}/step/{step_number}")
async def get_clinical_assessment_step(wizard_id: str, step_number: int):
    """Get clinical assessment step information."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number < 1 or step_number > session["total_steps"]:
        raise HTTPException(status_code=422, detail="Invalid step number")

    step_info = _get_step_info(step_number)

    # Get previously entered data if exists
    step_mapping = {
        1: "vital_signs",
        2: "physical_assessment",
        3: "systems_review",
        4: "pain_assessment",
        5: "functional_assessment",
    }

    existing_data = session["data"].get(step_mapping.get(step_number, ""), {})

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_number": step_number,
        "existing_data": existing_data,
        **step_info,
    }


@router.delete("/{wizard_id}")
async def cancel_clinical_assessment(wizard_id: str):
    """Cancel and delete clinical assessment wizard session."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    del _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "message": "Clinical assessment wizard session cancelled",
        "wizard_id": wizard_id,
    }


def _get_step_info(step_number: int) -> dict[str, Any]:
    """Get step configuration information."""

    steps = {
        1: {
            "step_title": "Vital Signs",
            "step_description": "Record patient vital signs and initial observations",
            "fields": [
                {"name": "temperature", "type": "number", "unit": "°F", "required": True},
                {"name": "pulse", "type": "number", "unit": "bpm", "required": True},
                {"name": "respirations", "type": "number", "unit": "/min", "required": True},
                {
                    "name": "blood_pressure_systolic",
                    "type": "number",
                    "unit": "mmHg",
                    "required": True,
                },
                {
                    "name": "blood_pressure_diastolic",
                    "type": "number",
                    "unit": "mmHg",
                    "required": True,
                },
                {"name": "oxygen_saturation", "type": "number", "unit": "%", "required": True},
                {"name": "pain_scale", "type": "number", "min": 0, "max": 10, "required": True},
            ],
            "educational_note": "Vital signs should be compared to patient's baseline and age-appropriate norms.",
        },
        2: {
            "step_title": "Physical Assessment",
            "step_description": "Conduct head-to-toe physical examination",
            "fields": [
                {"name": "general_appearance", "type": "text", "required": True},
                {"name": "skin_assessment", "type": "text", "required": True},
                {
                    "name": "heent",
                    "type": "text",
                    "label": "HEENT (Head, Eyes, Ears, Nose, Throat)",
                    "required": True,
                },
                {"name": "cardiovascular", "type": "text", "required": True},
                {"name": "respiratory", "type": "text", "required": True},
                {"name": "gastrointestinal", "type": "text", "required": True},
                {"name": "musculoskeletal", "type": "text", "required": True},
                {"name": "neurological", "type": "text", "required": True},
            ],
            "educational_note": "Use systematic head-to-toe approach. Document normal and abnormal findings.",
        },
        3: {
            "step_title": "Systems Review",
            "step_description": "Review all body systems for abnormalities",
            "fields": [
                {"name": "cardiovascular_review", "type": "textarea", "required": True},
                {"name": "respiratory_review", "type": "textarea", "required": True},
                {"name": "gastrointestinal_review", "type": "textarea", "required": True},
                {"name": "genitourinary_review", "type": "textarea", "required": True},
                {"name": "musculoskeletal_review", "type": "textarea", "required": True},
                {"name": "neurological_review", "type": "textarea", "required": True},
                {"name": "integumentary_review", "type": "textarea", "required": True},
                {"name": "endocrine_review", "type": "textarea", "required": False},
            ],
            "educational_note": "Document both positive and negative findings for comprehensive assessment.",
        },
        4: {
            "step_title": "Pain Assessment",
            "step_description": "Comprehensive pain evaluation using standardized tools",
            "fields": [
                {"name": "pain_location", "type": "text", "required": True},
                {"name": "pain_intensity", "type": "number", "min": 0, "max": 10, "required": True},
                {
                    "name": "pain_character",
                    "type": "select",
                    "options": ["Sharp", "Dull", "Aching", "Burning", "Stabbing", "Throbbing"],
                    "required": True,
                },
                {"name": "pain_onset", "type": "text", "required": True},
                {"name": "pain_duration", "type": "text", "required": True},
                {"name": "aggravating_factors", "type": "textarea", "required": True},
                {"name": "relieving_factors", "type": "textarea", "required": True},
                {
                    "name": "pain_impact",
                    "type": "textarea",
                    "label": "Impact on daily activities",
                    "required": True,
                },
            ],
            "educational_note": "Use PQRST or OLDCARTS mnemonic for comprehensive pain assessment.",
        },
        5: {
            "step_title": "Functional Assessment",
            "step_description": "Evaluate patient's functional status and activities of daily living",
            "fields": [
                {
                    "name": "mobility",
                    "type": "select",
                    "options": ["Independent", "Assisted", "Limited", "Bedbound"],
                    "required": True,
                },
                {
                    "name": "adl_independence",
                    "type": "select",
                    "label": "ADL Independence",
                    "options": [
                        "Fully independent",
                        "Needs minimal assistance",
                        "Needs moderate assistance",
                        "Fully dependent",
                    ],
                    "required": True,
                },
                {
                    "name": "fall_risk",
                    "type": "select",
                    "options": ["Low", "Moderate", "High"],
                    "required": True,
                },
                {
                    "name": "cognitive_status",
                    "type": "select",
                    "options": [
                        "Alert and oriented x4",
                        "Alert and oriented x3",
                        "Confused",
                        "Lethargic",
                        "Unresponsive",
                    ],
                    "required": True,
                },
                {"name": "communication_ability", "type": "text", "required": True},
                {"name": "nutritional_status", "type": "textarea", "required": True},
                {"name": "elimination_patterns", "type": "textarea", "required": True},
            ],
            "educational_note": "Functional assessment helps determine care needs and discharge planning.",
        },
    }

    return steps.get(step_number, {})


async def _generate_ai_analysis(
    step_number: int, step_data: dict[str, Any], all_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate AI-powered clinical analysis for assessment step.
    Uses OpenAI to provide evidence-based clinical insights and recommendations.
    """

    step_names = {
        1: "Vital Signs",
        2: "Physical Assessment",
        3: "Systems Review",
        4: "Pain Assessment",
        5: "Functional Assessment",
    }

    step_name = step_names.get(step_number, "Unknown Step")

    try:
        # Create clinical analysis prompt based on step
        if step_number == 1:
            # Vital signs analysis
            clinical_question = f"""Analyze the following vital signs and provide clinical assessment:

Vital Signs:
- Temperature: {step_data.get('temperature', 'N/A')}°F
- Pulse: {step_data.get('pulse', 'N/A')} bpm
- Respirations: {step_data.get('respirations', 'N/A')}/min
- Blood Pressure: {step_data.get('blood_pressure_systolic', 'N/A')}/{step_data.get('blood_pressure_diastolic', 'N/A')} mmHg
- Oxygen Saturation: {step_data.get('oxygen_saturation', 'N/A')}%
- Pain Scale: {step_data.get('pain_scale', 'N/A')}/10

Please provide:
1. Assessment of each vital sign (normal/abnormal)
2. Clinical significance of any abnormalities
3. Recommended follow-up assessments
4. Potential urgent concerns requiring escalation
"""

        elif step_number == 2:
            # Physical assessment analysis
            clinical_question = f"""Analyze the following physical assessment findings:

{step_data}

Provide:
1. Key positive and negative findings
2. Clinical patterns or concerns identified
3. Differential considerations based on findings
4. Recommended focused assessments
"""

        elif step_number == 3:
            # Systems review analysis
            clinical_question = f"""Analyze the following systems review:

{step_data}

Provide:
1. Systems with concerning findings
2. Inter-system correlations or patterns
3. Priority systems requiring further evaluation
4. Clinical decision support recommendations
"""

        elif step_number == 4:
            # Pain assessment analysis
            clinical_question = f"""Analyze the following pain assessment:

Location: {step_data.get('pain_location', 'N/A')}
Intensity: {step_data.get('pain_intensity', 'N/A')}/10
Character: {step_data.get('pain_character', 'N/A')}
Onset: {step_data.get('pain_onset', 'N/A')}
Duration: {step_data.get('pain_duration', 'N/A')}
Aggravating Factors: {step_data.get('aggravating_factors', 'N/A')}
Relieving Factors: {step_data.get('relieving_factors', 'N/A')}
Impact: {step_data.get('pain_impact', 'N/A')}

Provide:
1. Pain pattern analysis and likely etiology
2. Evidence-based pain management recommendations
3. Red flags requiring immediate attention
4. Non-pharmacological interventions to consider
"""

        elif step_number == 5:
            # Functional assessment analysis - final comprehensive summary
            clinical_question = f"""Provide comprehensive clinical summary based on complete assessment:

Vital Signs: {all_data.get('vital_signs', {})}
Physical Assessment: {all_data.get('physical_assessment', {})}
Systems Review: {all_data.get('systems_review', {})}
Pain Assessment: {all_data.get('pain_assessment', {})}
Functional Status: {step_data}

Provide:
1. Comprehensive clinical summary
2. Priority nursing diagnoses
3. Key safety concerns and interventions
4. Care planning recommendations
5. Discharge planning considerations
"""

        else:
            clinical_question = f"Analyze assessment data for {step_name}: {step_data}"

        # Call AI clinical decision support
        ai_response = await clinical_decision_support(
            patient_data=step_data,
            clinical_question=clinical_question,
            context="clinical_assessment",
        )

        return {
            "step_name": step_name,
            "analysis_available": True,
            "clinical_insights": ai_response.get("response", "AI analysis temporarily unavailable"),
            "recommendations": _extract_recommendations(ai_response),
            "disclaimer": "AI-generated clinical insights for educational support. All clinical decisions require professional nursing judgment.",
            "ai_model": ai_response.get("model", "gpt-4"),
            "service_status": ai_response.get("service_status", "available"),
        }

    except Exception as e:
        logger.error(f"AI analysis failed for step {step_number}: {e}")
        return {
            "step_name": step_name,
            "analysis_available": False,
            "message": "AI analysis temporarily unavailable",
            "fallback_note": "Continue with clinical assessment using professional judgment and clinical protocols",
            "error": str(e),
        }


def _extract_recommendations(ai_response: dict[str, Any]) -> list[str]:
    """Extract actionable recommendations from AI response."""
    response_text = ai_response.get("response", "")

    # Simple extraction - look for numbered or bulleted lists
    recommendations = []
    lines = response_text.split("\n")

    for line in lines:
        line = line.strip()
        # Match numbered lists (1., 2., etc.) or bullet points (-, *, •)
        if line and (line[0].isdigit() or line.startswith(("-", "*", "•"))):
            # Clean up the line
            cleaned = line.lstrip("0123456789.-*• ")
            if cleaned and len(cleaned) > 10:  # Only include substantial recommendations
                recommendations.append(cleaned)

    return recommendations[:5] if recommendations else ["Continue systematic clinical assessment"]
