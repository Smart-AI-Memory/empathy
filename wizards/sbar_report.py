"""
A wizard for generating SBAR (Situation, Background, Assessment, Recommendation) reports.

This multi-step wizard guides users through creating a structured SBAR report,
which is a standard communication tool in healthcare settings.
"""

from datetime import datetime

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from services.openai_client import get_client
from utils.api_responses import create_error_response, create_success_response
from utils.logging import get_logger

router = APIRouter(prefix="/wizards/sbar-report", tags=["wizards"])
logger = get_logger(__name__)

# In-memory storage for wizard state. In production, use Redis or a database.
wizard_sessions: dict[str, dict[str, str]] = {}

# --- Pydantic Models for Wizard Steps ---


class StartSbarResponse(BaseModel):
    wizard_id: str
    message: str
    next_step: str


class SbarStepInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    text: str = Field(..., description="The text content for the current step.")


class SbarStepResponse(BaseModel):
    wizard_id: str
    next_step: str
    message: str


class GenerateSbarInput(BaseModel):
    wizard_id: str = Field(..., description="The unique ID for this wizard session.")
    recommendation: str = Field(..., description="The 'Recommendation' text.")


class GenerateSbarResponse(BaseModel):
    wizard_id: str
    sbar_report: str


class DirectSbarInput(BaseModel):
    patient_id: str = Field(..., description="Patient identifier")
    situation: str = Field(..., description="The 'Situation' text")
    background: str = Field(..., description="The 'Background' text")
    assessment: str = Field(..., description="The 'Assessment' text")
    recommendation: str = Field(..., description="The 'Recommendation' text")
    care_setting: str = Field(default="med-surg", description="Care setting context")


class DirectSbarResponse(BaseModel):
    sbar_report: str
    care_setting: str


# --- Wizard Endpoints ---


@router.post("/start", response_model=StartSbarResponse, summary="Step 1: Start the SBAR wizard")
async def start_sbar_wizard():
    """
    Initializes a new SBAR report wizard session and returns a unique `wizard_id`.
    """
    import uuid

    wizard_id = str(uuid.uuid4())
    wizard_sessions[wizard_id] = {}
    logger.info(f"Started SBAR wizard session: {wizard_id}")

    return create_success_response(
        {
            "wizard_id": wizard_id,
            "message": "SBAR wizard started. Please proceed to add the 'Situation'.",
            "next_step": "situation",
        }
    )


def _update_step(wizard_id: str, step_name: str, text: str, next_step_name: str):
    """Helper function to update a step in the wizard session."""
    if wizard_id not in wizard_sessions:
        return create_error_response(
            "Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found"
        )

    wizard_sessions[wizard_id][step_name] = text
    logger.info(f"Updated SBAR session {wizard_id} with step: {step_name}")

    return create_success_response(
        {
            "wizard_id": wizard_id,
            "message": f"'{step_name.capitalize()}' received. Please proceed to add the '{next_step_name.capitalize()}'.",
            "next_step": next_step_name,
        }
    )


@router.post("/situation", response_model=SbarStepResponse, summary="Step 2: Add Situation")
async def add_situation(step_input: SbarStepInput):
    """Adds the **Situation** component to the SBAR report."""
    return _update_step(step_input.wizard_id, "situation", step_input.text, "background")


@router.post("/background", response_model=SbarStepResponse, summary="Step 3: Add Background")
async def add_background(step_input: SbarStepInput):
    """Adds the **Background** component to the SBAR report."""
    return _update_step(step_input.wizard_id, "background", step_input.text, "assessment")


@router.post("/assessment", response_model=SbarStepResponse, summary="Step 4: Add Assessment")
async def add_assessment(step_input: SbarStepInput):
    """Adds the **Assessment** component to the SBAR report."""
    return _update_step(step_input.wizard_id, "assessment", step_input.text, "recommendation")


@router.post(
    "/generate",
    response_model=DirectSbarResponse,
    summary="Generate Complete SBAR Report (Direct)",
)
async def generate_sbar_report_direct(input_data: DirectSbarInput):
    """
    Generate a complete SBAR report directly from all provided components.
    This is a simplified endpoint that doesn't require wizard session management.
    """
    # Validate that all required fields are present
    if not all(
        [
            input_data.situation,
            input_data.background,
            input_data.assessment,
            input_data.recommendation,
        ]
    ):
        return create_error_response(
            "All SBAR components (situation, background, assessment, recommendation) are required.",
            status.HTTP_400_BAD_REQUEST,
            "missing_required_fields",
        )

    # Build context-aware prompt based on care setting
    care_setting_context = {
        "icu": "critical care setting with focus on hemodynamic stability and ventilator management",
        "emergency": "emergency department with focus on rapid assessment and triage",
        "home-health": "home health setting with focus on patient/caregiver education and safety",
        "med-surg": "medical-surgical unit with focus on routine monitoring and care coordination",
    }.get(input_data.care_setting, "general clinical setting")

    prompt = f"""
    Format the following clinical information into a clear, professional SBAR report for a {care_setting_context}.

    Use these exact headings:
    - SITUATION
    - BACKGROUND
    - ASSESSMENT
    - RECOMMENDATION

    Format the report professionally with proper spacing and organization suitable for clinical handoff.
    Patient ID: {input_data.patient_id}

    Situation: {input_data.situation}

    Background: {input_data.background}

    Assessment: {input_data.assessment}

    Recommendation: {input_data.recommendation}
    """

    try:
        client = get_client()
        if not client:
            # Fallback: Generate basic SBAR report without AI enhancement
            logger.warning(
                "OpenAI client not available - generating basic SBAR report without AI formatting"
            )
            sbar_report = f"""SBAR Report - Patient ID: {input_data.patient_id}
Care Setting: {care_setting_context.upper()}

SITUATION
{input_data.situation}

BACKGROUND
{input_data.background}

ASSESSMENT
{input_data.assessment}

RECOMMENDATION
{input_data.recommendation}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Note: This report was generated without AI enhancement. Configure OPENAI_API_KEY for enhanced formatting.
"""
            return {"sbar_report": sbar_report, "care_setting": input_data.care_setting}

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert nursing assistant specializing in clinical communication in a {care_setting_context}. Format SBAR reports clearly and professionally.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # Lower temperature for more consistent formatting
        )
        sbar_report = response.choices[0].message.content
        logger.info(
            f"Successfully generated SBAR report for patient {input_data.patient_id} in {input_data.care_setting} setting"
        )

        return {"sbar_report": sbar_report, "care_setting": input_data.care_setting}
    except Exception as e:
        logger.error(f"SBAR report generation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SBAR report: {str(e)}",
        )


@router.post(
    "/generate-wizard",
    response_model=GenerateSbarResponse,
    summary="Step 5: Add Recommendation and Generate Report (Wizard)",
)
async def generate_sbar_report_wizard(step_input: GenerateSbarInput):
    """
    Adds the final **Recommendation** component and generates the complete,
    formatted SBAR report using an AI model. (Wizard session-based flow)
    """
    wizard_id = step_input.wizard_id
    if wizard_id not in wizard_sessions:
        return create_error_response(
            "Wizard session not found.", status.HTTP_404_NOT_FOUND, "wizard_not_found"
        )

    session_data = wizard_sessions[wizard_id]
    session_data["recommendation"] = step_input.recommendation

    # Verify all parts are present
    required_parts = ["situation", "background", "assessment", "recommendation"]
    if not all(part in session_data for part in required_parts):
        missing = [part for part in required_parts if part not in session_data]
        return create_error_response(
            f"Cannot generate report. Missing parts: {', '.join(missing)}",
            status.HTTP_400_BAD_REQUEST,
            "missing_sbar_parts",
        )

    prompt = f"""
    Format the following clinical information into a clear and concise SBAR report.
    Use clear headings for each section (Situation, Background, Assessment, Recommendation).
    Ensure the language is professional and suitable for a clinical handoff.

    Situation: {session_data['situation']}
    Background: {session_data['background']}
    Assessment: {session_data['assessment']}
    Recommendation: {session_data['recommendation']}
    """

    try:
        client = get_client()
        if not client:
            # Fallback: Generate basic SBAR report without AI enhancement
            logger.warning(
                f"OpenAI client not available for session {wizard_id} - generating basic SBAR report"
            )
            sbar_report = f"""SBAR Report

SITUATION
{session_data['situation']}

BACKGROUND
{session_data['background']}

ASSESSMENT
{session_data['assessment']}

RECOMMENDATION
{session_data['recommendation']}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Note: This report was generated without AI enhancement. Configure OPENAI_API_KEY for enhanced formatting.
"""
            # Clean up the session
            del wizard_sessions[wizard_id]

            return {"wizard_id": wizard_id, "sbar_report": sbar_report}

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert nursing assistant specializing in clinical communication.",
                },
                {"role": "user", "content": prompt},
            ],
        )
        sbar_report = response.choices[0].message.content
        logger.info(f"Successfully generated SBAR report for session {wizard_id}")

        # Clean up the session
        del wizard_sessions[wizard_id]

        return {"wizard_id": wizard_id, "sbar_report": sbar_report}
    except Exception as e:
        logger.error(f"SBAR report generation failed for session {wizard_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate SBAR report: {str(e)}",
        )
