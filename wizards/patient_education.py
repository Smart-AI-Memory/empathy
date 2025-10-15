"""
Patient Education Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
Educational content delivery system with AI-powered content generation and reading level adjustment
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from uuid import uuid4
from datetime import datetime
import logging

from ...services.openai_client import create_openai_service

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wizard/patient-education",
    tags=["wizards", "patient-education"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"}
    }
)

# Wizard session storage (Redis in production)
_wizard_sessions: Dict[str, Dict[str, Any]] = {}

class EducationStepData(BaseModel):
    """Data model for education step submission."""
    step_data: Dict[str, Any]
    comprehension_score: Optional[int] = None
    questions: Optional[List[str]] = None

@router.post("/start")
async def start_patient_education(
    topic: str = "general",
    patient_literacy_level: str = "standard"
):
    """Start patient education wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "patient_education",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 4,
        "completed_steps": [],
        "data": {
            "topic": topic,
            "literacy_level": patient_literacy_level,
            "learning_objectives": [],
            "content_delivered": [],
            "comprehension_checks": [],
            "follow_up_materials": []
        }
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "wizard_id": wizard_id,
        "wizard_type": "patient_education",
        "current_step": 1,
        "total_steps": 4,
        "step_title": "Learning Assessment",
        "step_description": "Assess patient's current knowledge and learning preferences",
        "fields": [
            {"name": "current_knowledge_level", "type": "select", "options": ["No knowledge", "Some knowledge", "Moderate knowledge", "Good knowledge"], "required": True},
            {"name": "preferred_learning_style", "type": "select", "options": ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"], "required": True},
            {"name": "language_preference", "type": "text", "required": True},
            {"name": "barriers_to_learning", "type": "textarea", "required": False},
            {"name": "support_system", "type": "textarea", "label": "Family/caregiver involvement", "required": False}
        ],
        "educational_note": "Tailor education to patient's literacy level, learning style, and cultural background."
    }

@router.get("/{wizard_id}/status")
async def get_patient_education_status(wizard_id: str):
    """Get patient education wizard status following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    return {
        "wizard_id": wizard_id,
        "wizard_type": session["wizard_type"],
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "completed_steps": session["completed_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "data": session["data"]
    }

@router.post("/{wizard_id}/step/{step_number}")
async def submit_patient_education_step(
    wizard_id: str,
    step_number: int,
    step_data: EducationStepData
):
    """Submit patient education step data following Wizard Pattern Implementation."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number != session["current_step"]:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid step. Expected step {session['current_step']}, got step {step_number}"
        )

    # Store step data based on step number
    step_mapping = {
        1: "learning_assessment",
        2: "content_delivery",
        3: "comprehension_check",
        4: "follow_up_plan"
    }

    if step_number in step_mapping:
        session["data"][step_mapping[step_number]] = step_data.step_data

    # Track comprehension scores if provided
    if step_data.comprehension_score is not None:
        session["data"]["comprehension_checks"].append({
            "step": step_number,
            "score": step_data.comprehension_score,
            "timestamp": datetime.now().isoformat()
        })

    # Track questions if provided
    if step_data.questions:
        if "patient_questions" not in session["data"]:
            session["data"]["patient_questions"] = []
        session["data"]["patient_questions"].extend(step_data.questions)

    # Mark step as completed
    if step_number not in session["completed_steps"]:
        session["completed_steps"].append(step_number)

    # Generate AI-powered educational content after step 1 (learning assessment)
    ai_content = None
    if step_number == 1:
        ai_content = await _generate_personalized_content(
            topic=session["data"]["topic"],
            literacy_level=session["data"]["literacy_level"],
            learning_style=step_data.step_data.get("preferred_learning_style", "Mixed"),
            current_knowledge=step_data.step_data.get("current_knowledge_level", "No knowledge")
        )

    # Generate comprehension quiz after step 2 (content delivery)
    ai_quiz = None
    if step_number == 2:
        ai_quiz = await _generate_comprehension_quiz(
            topic=session["data"]["topic"],
            literacy_level=session["data"]["literacy_level"],
            content_covered=step_data.step_data.get("key_concepts_covered", "")
        )

    # Move to next step
    if step_number < session["total_steps"]:
        session["current_step"] = step_number + 1
        next_step_info = _get_step_info(step_number + 1, session["data"]["topic"])
    else:
        next_step_info = None

    response = {
        "wizard_id": wizard_id,
        "step_completed": step_number,
        "current_step": session["current_step"],
        "total_steps": session["total_steps"],
        "progress": len(session["completed_steps"]) / session["total_steps"] * 100,
        "status": "completed" if len(session["completed_steps"]) == session["total_steps"] else "in_progress",
        "next_step": next_step_info
    }

    # Add AI-generated content to response if available
    if ai_content:
        response["ai_generated_content"] = ai_content
    if ai_quiz:
        response["ai_generated_quiz"] = ai_quiz

    return response

@router.get("/{wizard_id}/step/{step_number}")
async def get_patient_education_step(wizard_id: str, step_number: int):
    """Get patient education step information."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number < 1 or step_number > session["total_steps"]:
        raise HTTPException(status_code=422, detail="Invalid step number")

    step_info = _get_step_info(step_number, session["data"]["topic"])

    # Get previously entered data if exists
    step_mapping = {
        1: "learning_assessment",
        2: "content_delivery",
        3: "comprehension_check",
        4: "follow_up_plan"
    }

    existing_data = session["data"].get(step_mapping.get(step_number, ""), {})

    return {
        "wizard_id": wizard_id,
        "step_number": step_number,
        "existing_data": existing_data,
        **step_info
    }

@router.get("/{wizard_id}/materials")
async def get_education_materials(wizard_id: str):
    """Get recommended educational materials based on topic and learning style."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]
    topic = session["data"].get("topic", "general")
    learning_style = session["data"].get("learning_assessment", {}).get("preferred_learning_style", "Mixed")

    # Generate material recommendations based on topic and learning style
    materials = _generate_educational_materials(topic, learning_style)

    return {
        "wizard_id": wizard_id,
        "topic": topic,
        "learning_style": learning_style,
        "materials": materials
    }

@router.delete("/{wizard_id}")
async def cancel_patient_education(wizard_id: str):
    """Cancel and delete patient education wizard session."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    del _wizard_sessions[wizard_id]

    return {
        "message": "Patient education wizard session cancelled",
        "wizard_id": wizard_id
    }

def _get_step_info(step_number: int, topic: str = "general") -> Dict[str, Any]:
    """Get step configuration information."""

    steps = {
        1: {
            "step_title": "Learning Assessment",
            "step_description": "Assess patient's current knowledge and learning preferences",
            "fields": [
                {"name": "current_knowledge_level", "type": "select", "options": ["No knowledge", "Some knowledge", "Moderate knowledge", "Good knowledge"], "required": True},
                {"name": "preferred_learning_style", "type": "select", "options": ["Visual", "Auditory", "Reading/Writing", "Kinesthetic", "Mixed"], "required": True},
                {"name": "language_preference", "type": "text", "required": True},
                {"name": "barriers_to_learning", "type": "textarea", "required": False},
                {"name": "support_system", "type": "textarea", "label": "Family/caregiver involvement", "required": False}
            ],
            "educational_note": "Tailor education to patient's literacy level, learning style, and cultural background."
        },
        2: {
            "step_title": "Content Delivery",
            "step_description": f"Deliver educational content about {topic}",
            "fields": [
                {"name": "key_concepts_covered", "type": "textarea", "required": True},
                {"name": "demonstrations_provided", "type": "textarea", "required": False},
                {"name": "materials_given", "type": "textarea", "label": "Written materials provided", "required": True},
                {"name": "visual_aids_used", "type": "textarea", "required": False},
                {"name": "patient_engagement", "type": "select", "options": ["Excellent", "Good", "Fair", "Poor"], "required": True},
                {"name": "time_spent", "type": "number", "unit": "minutes", "required": True}
            ],
            "educational_note": "Use teach-back method to ensure comprehension. Provide materials at appropriate literacy level."
        },
        3: {
            "step_title": "Comprehension Check",
            "step_description": "Verify patient understanding using teach-back method",
            "fields": [
                {"name": "teach_back_response", "type": "textarea", "label": "Patient's explanation in own words", "required": True},
                {"name": "comprehension_score", "type": "number", "min": 0, "max": 100, "unit": "%", "required": True},
                {"name": "areas_of_confusion", "type": "textarea", "required": False},
                {"name": "additional_questions", "type": "textarea", "required": False},
                {"name": "demonstration_accuracy", "type": "select", "label": "Return demonstration accuracy", "options": ["Accurate", "Mostly accurate", "Needs improvement", "Unable to demonstrate"], "required": False}
            ],
            "educational_note": "Use teach-back method: 'To make sure I explained clearly, can you tell me in your own words...'"
        },
        4: {
            "step_title": "Follow-up Plan",
            "step_description": "Establish follow-up education and support plan",
            "fields": [
                {"name": "reinforcement_needed", "type": "select", "options": ["None", "Minimal", "Moderate", "Extensive"], "required": True},
                {"name": "follow_up_date", "type": "date", "required": True},
                {"name": "topics_to_review", "type": "textarea", "required": False},
                {"name": "support_resources", "type": "textarea", "label": "Community resources provided", "required": True},
                {"name": "contact_information", "type": "textarea", "label": "Contact info for questions", "required": True},
                {"name": "documentation_completed", "type": "boolean", "required": True}
            ],
            "educational_note": "Provide written discharge instructions and emergency contact information."
        }
    }

    return steps.get(step_number, {})

def _generate_educational_materials(topic: str, learning_style: str) -> List[Dict[str, Any]]:
    """Generate recommended educational materials based on topic and learning style."""

    # Base materials available for all topics
    materials = []

    if learning_style in ["Visual", "Mixed"]:
        materials.append({
            "type": "video",
            "title": f"Understanding {topic.title()}",
            "description": "Visual guide with animations and graphics",
            "duration": "5-10 minutes",
            "language": "English with subtitles available"
        })
        materials.append({
            "type": "infographic",
            "title": f"{topic.title()} Quick Reference",
            "description": "One-page visual summary with key information",
            "format": "PDF, printable"
        })

    if learning_style in ["Reading/Writing", "Mixed"]:
        materials.append({
            "type": "handout",
            "title": f"Patient Guide to {topic.title()}",
            "description": "Comprehensive written guide at 6th grade reading level",
            "format": "PDF, available in multiple languages"
        })
        materials.append({
            "type": "worksheet",
            "title": f"My {topic.title()} Action Plan",
            "description": "Fill-in worksheet for personal care planning",
            "format": "Printable PDF"
        })

    if learning_style in ["Auditory", "Mixed"]:
        materials.append({
            "type": "audio",
            "title": f"{topic.title()} Audio Guide",
            "description": "Narrated guide covering key concepts",
            "duration": "10-15 minutes",
            "format": "MP3, downloadable"
        })

    if learning_style in ["Kinesthetic", "Mixed"]:
        materials.append({
            "type": "demonstration",
            "title": f"{topic.title()} Skills Practice",
            "description": "Hands-on practice session with return demonstration",
            "duration": "15-20 minutes",
            "supplies_needed": "Provided by nursing staff"
        })

    # Add web resources for all
    materials.append({
        "type": "website",
        "title": "MedlinePlus Patient Education",
        "url": "https://medlineplus.gov",
        "description": "Reliable health information from NIH",
        "note": "Search for your specific condition"
    })

    return materials

async def _generate_personalized_content(
    topic: str,
    literacy_level: str,
    learning_style: str,
    current_knowledge: str
) -> Dict[str, Any]:
    """
    Generate AI-powered personalized educational content with reading level adjustment.

    This is the key feature for patient education - AI generates content at the appropriate
    reading level (5th grade, 8th grade, high school, college) based on patient literacy.
    """

    # Map literacy levels to reading grades
    literacy_map = {
        "low": "5th grade",
        "standard": "8th grade",
        "high": "high school",
        "advanced": "college"
    }

    reading_level = literacy_map.get(literacy_level, "8th grade")

    try:
        service = create_openai_service()

        if not service:
            return _fallback_educational_content(topic, reading_level)

        # Create personalized educational content prompt with reading level specification
        prompt = f"""Generate patient education content about {topic} with the following requirements:

CRITICAL: Write at a {reading_level} reading level. Use simple words, short sentences, and clear explanations appropriate for {reading_level} literacy.

Patient Profile:
- Current Knowledge: {current_knowledge}
- Learning Style: {learning_style}
- Reading Level: {reading_level}

Please provide:
1. Introduction (2-3 simple sentences explaining what {topic} is)
2. Key Facts (5-7 important points at {reading_level} level)
3. What to Expect (daily life impacts, explained simply)
4. Warning Signs (when to call the doctor, in clear language)
5. Self-Care Tips (practical actions the patient can take)

Remember:
- Use {reading_level} vocabulary and sentence structure
- Avoid medical jargon or explain it in simple terms
- Use active voice and direct language
- Break complex ideas into simple steps
- Include encouraging, supportive tone

Format with clear headings and short paragraphs for easy reading."""

        ai_response = await service.generate_response(
            prompt=prompt,
            context=f"Patient education at {reading_level} reading level for {learning_style} learner"
        )

        return {
            "content_available": True,
            "reading_level": reading_level,
            "educational_content": ai_response.get("response", ""),
            "learning_style_adapted": learning_style,
            "ai_model": ai_response.get("model", "gpt-4"),
            "service_status": ai_response.get("service_status", "available"),
            "customization_note": f"Content adapted to {reading_level} reading level and {learning_style} learning style"
        }

    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        return _fallback_educational_content(topic, reading_level)

async def _generate_comprehension_quiz(
    topic: str,
    literacy_level: str,
    content_covered: str
) -> Dict[str, Any]:
    """
    Generate AI-powered comprehension quiz questions based on content delivered.
    Questions are adjusted to patient's literacy level for accurate assessment.
    """

    literacy_map = {
        "low": "5th grade",
        "standard": "8th grade",
        "high": "high school",
        "advanced": "college"
    }

    reading_level = literacy_map.get(literacy_level, "8th grade")

    try:
        service = create_openai_service()

        if not service:
            return _fallback_quiz(topic, reading_level)

        prompt = f"""Create a comprehension quiz about {topic} to verify patient understanding.

Content that was taught:
{content_covered}

Requirements:
- Write questions at {reading_level} reading level
- Use simple, clear language
- Create 5 multiple-choice questions
- Include 1 scenario-based question asking "What would you do if..."
- Provide correct answers with brief explanations

Format as:
Question 1: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
Correct Answer: [letter] - [brief explanation]

Make questions practical and relevant to daily life."""

        ai_response = await service.generate_response(
            prompt=prompt,
            context=f"Comprehension quiz at {reading_level} level"
        )

        return {
            "quiz_available": True,
            "reading_level": reading_level,
            "quiz_questions": ai_response.get("response", ""),
            "question_count": 5,
            "ai_model": ai_response.get("model", "gpt-4")
        }

    except Exception as e:
        logger.error(f"AI quiz generation failed: {e}")
        return _fallback_quiz(topic, reading_level)

def _fallback_educational_content(topic: str, reading_level: str) -> Dict[str, Any]:
    """Fallback educational content when AI is unavailable."""
    return {
        "content_available": False,
        "reading_level": reading_level,
        "message": "AI content generation temporarily unavailable",
        "fallback_note": f"Use standard {topic} patient education materials at {reading_level} level from approved resources",
        "recommended_resources": [
            "MedlinePlus patient education materials (medlineplus.gov)",
            "CDC patient fact sheets (cdc.gov)",
            "Hospital-approved patient education library"
        ]
    }

def _fallback_quiz(topic: str, reading_level: str) -> Dict[str, Any]:
    """Fallback quiz when AI is unavailable."""
    return {
        "quiz_available": False,
        "reading_level": reading_level,
        "message": "AI quiz generation temporarily unavailable",
        "fallback_note": "Use teach-back method to assess comprehension: 'Can you tell me in your own words what we discussed about {topic}?'"
    }