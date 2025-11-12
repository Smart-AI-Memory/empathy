"""
Quality Improvement Wizard - AI Nurse Florence
Following Wizard Pattern Implementation from coding instructions
Quality metrics tracking and improvement initiative workflows with AI-powered pattern analysis
"""

import logging
from datetime import datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...services.openai_client import create_openai_service
from ...utils.config import get_educational_banner

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/wizard/quality-improvement",
    tags=["wizards", "quality-improvement"],
    responses={
        404: {"description": "Wizard session not found"},
        422: {"description": "Invalid step data"},
    },
)

# Wizard session storage (Redis in production)
_wizard_sessions: dict[str, dict[str, Any]] = {}


class QualityImprovementStepData(BaseModel):
    """Data model for quality improvement step submission."""

    step_data: dict[str, Any]
    metrics: list[dict[str, Any]] | None = None


@router.post("/start")
async def start_quality_improvement(
    initiative_type: str = "general", department: str | None = None
):
    """Start quality improvement wizard following Wizard Pattern Implementation."""
    wizard_id = str(uuid4())

    session_data = {
        "wizard_id": wizard_id,
        "wizard_type": "quality_improvement",
        "created_at": datetime.now().isoformat(),
        "current_step": 1,
        "total_steps": 5,
        "completed_steps": [],
        "data": {
            "initiative_type": initiative_type,
            "department": department,
            "problem_identification": {},
            "baseline_metrics": {},
            "improvement_plan": {},
            "implementation": {},
            "evaluation": {},
        },
    }

    _wizard_sessions[wizard_id] = session_data

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "wizard_type": "quality_improvement",
        "current_step": 1,
        "total_steps": 5,
        "step_title": "Problem Identification",
        "step_description": "Define the quality issue or opportunity for improvement",
        "fields": [
            {"name": "problem_statement", "type": "textarea", "required": True},
            {
                "name": "affected_population",
                "type": "text",
                "label": "Patient/staff population affected",
                "required": True,
            },
            {
                "name": "scope",
                "type": "select",
                "options": ["Unit-level", "Department-level", "Hospital-wide", "System-wide"],
                "required": True,
            },
            {
                "name": "current_impact",
                "type": "textarea",
                "label": "Current impact on care/outcomes",
                "required": True,
            },
            {
                "name": "root_causes",
                "type": "textarea",
                "label": "Suspected root causes",
                "required": True,
            },
            {"name": "stakeholders", "type": "textarea", "required": True},
        ],
        "educational_note": "Use SMART criteria when defining the problem. Consider using root cause analysis tools like fishbone diagrams.",
    }


@router.get("/{wizard_id}/status")
async def get_quality_improvement_status(wizard_id: str):
    """Get quality improvement wizard status following Wizard Pattern Implementation."""

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
async def submit_quality_improvement_step(
    wizard_id: str, step_number: int, step_data: QualityImprovementStepData
):
    """Submit quality improvement step data following Wizard Pattern Implementation."""

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
        1: "problem_identification",
        2: "baseline_metrics",
        3: "improvement_plan",
        4: "implementation",
        5: "evaluation",
    }

    if step_number in step_mapping:
        session["data"][step_mapping[step_number]] = step_data.step_data

    # Track metrics if provided
    if step_data.metrics:
        if "tracked_metrics" not in session["data"]:
            session["data"]["tracked_metrics"] = []
        session["data"]["tracked_metrics"].extend(step_data.metrics)

    # Mark step as completed
    if step_number not in session["completed_steps"]:
        session["completed_steps"].append(step_number)

    # Generate AI analysis based on step
    ai_analysis = await _generate_qi_analysis(step_number, step_data.step_data, session["data"])

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
async def get_quality_improvement_step(wizard_id: str, step_number: int):
    """Get quality improvement step information."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]

    if step_number < 1 or step_number > session["total_steps"]:
        raise HTTPException(status_code=422, detail="Invalid step number")

    step_info = _get_step_info(step_number)

    # Get previously entered data if exists
    step_mapping = {
        1: "problem_identification",
        2: "baseline_metrics",
        3: "improvement_plan",
        4: "implementation",
        5: "evaluation",
    }

    existing_data = session["data"].get(step_mapping.get(step_number, ""), {})

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "step_number": step_number,
        "existing_data": existing_data,
        **step_info,
    }


@router.get("/{wizard_id}/metrics")
async def get_quality_metrics(wizard_id: str):
    """Get tracked quality metrics for the initiative."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    session = _wizard_sessions[wizard_id]
    metrics = session["data"].get("tracked_metrics", [])

    return {
        "banner": get_educational_banner(),
        "wizard_id": wizard_id,
        "metrics": metrics,
        "baseline_data": session["data"].get("baseline_metrics", {}),
        "evaluation_data": session["data"].get("evaluation", {}),
    }


@router.delete("/{wizard_id}")
async def cancel_quality_improvement(wizard_id: str):
    """Cancel and delete quality improvement wizard session."""

    if wizard_id not in _wizard_sessions:
        raise HTTPException(status_code=404, detail="Wizard session not found")

    del _wizard_sessions[wizard_id]

    return {
        "banner": get_educational_banner(),
        "message": "Quality improvement wizard session cancelled",
        "wizard_id": wizard_id,
    }


def _get_step_info(step_number: int) -> dict[str, Any]:
    """Get step configuration information."""

    steps = {
        1: {
            "step_title": "Problem Identification",
            "step_description": "Define the quality issue or opportunity for improvement",
            "fields": [
                {"name": "problem_statement", "type": "textarea", "required": True},
                {
                    "name": "affected_population",
                    "type": "text",
                    "label": "Patient/staff population affected",
                    "required": True,
                },
                {
                    "name": "scope",
                    "type": "select",
                    "options": ["Unit-level", "Department-level", "Hospital-wide", "System-wide"],
                    "required": True,
                },
                {
                    "name": "current_impact",
                    "type": "textarea",
                    "label": "Current impact on care/outcomes",
                    "required": True,
                },
                {
                    "name": "root_causes",
                    "type": "textarea",
                    "label": "Suspected root causes",
                    "required": True,
                },
                {"name": "stakeholders", "type": "textarea", "required": True},
            ],
            "educational_note": "Use SMART criteria when defining the problem. Consider using root cause analysis tools like fishbone diagrams.",
        },
        2: {
            "step_title": "Baseline Metrics",
            "step_description": "Establish current performance and measurement criteria",
            "fields": [
                {"name": "primary_metric", "type": "text", "required": True},
                {
                    "name": "primary_metric_value",
                    "type": "number",
                    "label": "Current value",
                    "required": True,
                },
                {"name": "secondary_metrics", "type": "textarea", "required": False},
                {
                    "name": "data_source",
                    "type": "text",
                    "label": "How metrics are collected",
                    "required": True,
                },
                {
                    "name": "measurement_frequency",
                    "type": "select",
                    "options": ["Daily", "Weekly", "Monthly", "Quarterly"],
                    "required": True,
                },
                {"name": "target_value", "type": "number", "required": True},
                {
                    "name": "target_timeline",
                    "type": "text",
                    "label": "Timeline to reach target",
                    "required": True,
                },
            ],
            "educational_note": "Ensure metrics are measurable, relevant, and align with organizational quality goals.",
        },
        3: {
            "step_title": "Improvement Plan",
            "step_description": "Develop PDSA (Plan-Do-Study-Act) improvement strategy",
            "fields": [
                {
                    "name": "aim_statement",
                    "type": "textarea",
                    "label": "SMART aim statement",
                    "required": True,
                },
                {
                    "name": "interventions",
                    "type": "textarea",
                    "label": "Planned interventions/changes",
                    "required": True,
                },
                {
                    "name": "evidence_base",
                    "type": "textarea",
                    "label": "Evidence supporting interventions",
                    "required": True,
                },
                {"name": "resources_needed", "type": "textarea", "required": True},
                {
                    "name": "team_members",
                    "type": "textarea",
                    "label": "QI team members and roles",
                    "required": True,
                },
                {
                    "name": "timeline",
                    "type": "textarea",
                    "label": "Implementation timeline",
                    "required": True,
                },
                {"name": "barriers_anticipated", "type": "textarea", "required": True},
                {"name": "mitigation_strategies", "type": "textarea", "required": True},
            ],
            "educational_note": "Use evidence-based practices. Plan for small tests of change (PDSA cycles) before full implementation.",
        },
        4: {
            "step_title": "Implementation",
            "step_description": "Document implementation progress and adjustments",
            "fields": [
                {"name": "start_date", "type": "date", "required": True},
                {"name": "interventions_completed", "type": "textarea", "required": True},
                {"name": "staff_training_completed", "type": "boolean", "required": True},
                {"name": "process_changes_made", "type": "textarea", "required": True},
                {"name": "challenges_encountered", "type": "textarea", "required": True},
                {
                    "name": "adjustments_made",
                    "type": "textarea",
                    "label": "PDSA adjustments",
                    "required": True,
                },
                {"name": "stakeholder_feedback", "type": "textarea", "required": False},
                {"name": "current_adoption_rate", "type": "number", "unit": "%", "required": True},
            ],
            "educational_note": "Document all PDSA cycles. Be prepared to adapt the plan based on real-world feedback.",
        },
        5: {
            "step_title": "Evaluation & Sustainability",
            "step_description": "Assess outcomes and plan for sustained improvement",
            "fields": [
                {"name": "end_date", "type": "date", "required": True},
                {
                    "name": "final_metric_value",
                    "type": "number",
                    "label": "Final primary metric value",
                    "required": True,
                },
                {"name": "target_achieved", "type": "boolean", "required": True},
                {"name": "outcome_summary", "type": "textarea", "required": True},
                {"name": "lessons_learned", "type": "textarea", "required": True},
                {
                    "name": "sustainability_plan",
                    "type": "textarea",
                    "label": "How improvements will be sustained",
                    "required": True,
                },
                {
                    "name": "monitoring_frequency",
                    "type": "select",
                    "label": "Ongoing monitoring plan",
                    "options": ["Daily", "Weekly", "Monthly", "Quarterly"],
                    "required": True,
                },
                {
                    "name": "spread_potential",
                    "type": "textarea",
                    "label": "Potential to spread to other units",
                    "required": False,
                },
                {"name": "next_steps", "type": "textarea", "required": True},
            ],
            "educational_note": "Celebrate successes! Share results with stakeholders. Plan for ongoing monitoring to prevent backsliding.",
        },
    }

    return steps.get(step_number, {})


@router.get("/templates")
async def get_quality_improvement_templates():
    """Get common quality improvement initiative templates."""

    return {
        "banner": get_educational_banner(),
        "templates": [
            {
                "name": "Fall Prevention",
                "description": "Reduce patient falls and fall-related injuries",
                "common_metrics": [
                    "Falls per 1000 patient days",
                    "Fall-related injury rate",
                    "Post-fall huddle completion rate",
                ],
                "evidence_based_interventions": [
                    "Hourly rounding",
                    "Fall risk assessment on admission",
                    "Yellow socks/wristbands for high-risk patients",
                    "Bed alarms for appropriate patients",
                    "Environmental safety checks",
                ],
            },
            {
                "name": "Pressure Injury Prevention",
                "description": "Prevent hospital-acquired pressure injuries",
                "common_metrics": [
                    "Hospital-acquired pressure injury rate",
                    "Skin assessment completion rate",
                    "Turn compliance rate",
                ],
                "evidence_based_interventions": [
                    "Braden scale assessment on admission",
                    "Turn schedule implementation",
                    "Specialty mattress utilization",
                    "Nutritional support",
                    "Heel offloading protocols",
                ],
            },
            {
                "name": "CAUTI Prevention",
                "description": "Reduce catheter-associated urinary tract infections",
                "common_metrics": [
                    "CAUTI rate per 1000 catheter days",
                    "Catheter utilization ratio",
                    "Appropriate indication documentation",
                ],
                "evidence_based_interventions": [
                    "Daily catheter necessity assessment",
                    "Aseptic insertion technique",
                    "Proper catheter maintenance",
                    "Early removal protocols",
                    "Nurse-driven removal protocols",
                ],
            },
            {
                "name": "Medication Safety",
                "description": "Reduce medication errors and adverse drug events",
                "common_metrics": [
                    "Medication error rate",
                    "Adverse drug event rate",
                    "High-alert medication compliance",
                ],
                "evidence_based_interventions": [
                    "Double-check protocols for high-alert meds",
                    "Barcode scanning compliance",
                    "Medication reconciliation",
                    "Smart pump utilization",
                    "Pharmacist involvement in rounds",
                ],
            },
            {
                "name": "Hand Hygiene Compliance",
                "description": "Improve hand hygiene compliance rates",
                "common_metrics": [
                    "Hand hygiene compliance rate",
                    "Healthcare-associated infection rates",
                    "Audit completion rate",
                ],
                "evidence_based_interventions": [
                    "Alcohol-based hand sanitizer placement",
                    "Visual reminders at point of care",
                    "Direct observation audits",
                    "Peer accountability",
                    "Leadership rounding with feedback",
                ],
            },
            {
                "name": "Patient Satisfaction",
                "description": "Improve patient experience and satisfaction scores",
                "common_metrics": [
                    "HCAHPS scores",
                    "Response rate to call lights",
                    "Hourly rounding completion",
                ],
                "evidence_based_interventions": [
                    "Bedside shift report",
                    "Hourly rounding with 4 Ps (Pain, Potty, Position, Possessions)",
                    "Leader rounding",
                    "Discharge phone calls",
                    "White board communication",
                ],
            },
        ],
    }


async def _generate_qi_analysis(
    step_number: int, step_data: dict[str, Any], all_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Generate AI-powered quality improvement analysis for each step.
    Provides pattern analysis, root cause identification, evidence-based interventions, and outcome predictions.
    """

    step_names = {
        1: "Problem Identification",
        2: "Baseline Metrics",
        3: "Improvement Plan",
        4: "Implementation",
        5: "Evaluation & Sustainability",
    }

    step_name = step_names.get(step_number, "Unknown Step")

    try:
        service = create_openai_service()

        if not service:
            return _fallback_qi_analysis(step_name)

        # Create analysis prompt based on step
        if step_number == 1:
            # Root cause analysis and pattern identification
            prompt = f"""Analyze this quality improvement problem and provide professional nursing insights:

Problem Statement: {step_data.get('problem_statement', 'N/A')}
Affected Population: {step_data.get('affected_population', 'N/A')}
Scope: {step_data.get('scope', 'N/A')}
Current Impact: {step_data.get('current_impact', 'N/A')}
Suspected Root Causes: {step_data.get('root_causes', 'N/A')}
Stakeholders: {step_data.get('stakeholders', 'N/A')}

Provide:
1. Root cause analysis using systems thinking
2. Contributing factors across people, process, environment, and equipment
3. Similar quality issues in nursing literature
4. Priority areas for data collection and baseline measurement
5. Stakeholder engagement strategies"""

        elif step_number == 2:
            # Metrics analysis and benchmarking
            prompt = f"""Analyze these baseline quality metrics and provide evidence-based insights:

Primary Metric: {step_data.get('primary_metric', 'N/A')}
Current Value: {step_data.get('primary_metric_value', 'N/A')}
Target Value: {step_data.get('target_value', 'N/A')}
Secondary Metrics: {step_data.get('secondary_metrics', 'N/A')}
Data Source: {step_data.get('data_source', 'N/A')}
Measurement Frequency: {step_data.get('measurement_frequency', 'N/A')}
Target Timeline: {step_data.get('target_timeline', 'N/A')}

Provide:
1. Assessment of current performance vs. national benchmarks
2. Statistical significance of improvement needed
3. Run chart and control chart recommendations
4. Balance measures to monitor for unintended consequences
5. Data collection and validation strategies"""

        elif step_number == 3:
            # Evidence-based intervention recommendations
            prompt = f"""Analyze this quality improvement plan and provide evidence-based recommendations:

Aim Statement: {step_data.get('aim_statement', 'N/A')}
Planned Interventions: {step_data.get('interventions', 'N/A')}
Evidence Base: {step_data.get('evidence_base', 'N/A')}
Resources Needed: {step_data.get('resources_needed', 'N/A')}
Team Members: {step_data.get('team_members', 'N/A')}
Timeline: {step_data.get('timeline', 'N/A')}
Anticipated Barriers: {step_data.get('barriers_anticipated', 'N/A')}

Provide:
1. Strength of evidence for proposed interventions (cite nursing research)
2. Additional evidence-based interventions to consider
3. PDSA cycle recommendations for testing changes
4. Change management strategies for adoption
5. Risk mitigation for identified barriers"""

        elif step_number == 4:
            # Implementation progress analysis
            prompt = f"""Analyze quality improvement implementation progress:

Start Date: {step_data.get('start_date', 'N/A')}
Interventions Completed: {step_data.get('interventions_completed', 'N/A')}
Process Changes: {step_data.get('process_changes_made', 'N/A')}
Challenges Encountered: {step_data.get('challenges_encountered', 'N/A')}
Adjustments Made: {step_data.get('adjustments_made', 'N/A')}
Current Adoption Rate: {step_data.get('current_adoption_rate', 'N/A')}%

Baseline Data: {all_data.get('baseline_metrics', {})}

Provide:
1. Assessment of implementation fidelity
2. Adoption rate analysis and strategies to improve
3. Recommended PDSA adjustments based on challenges
4. Early indicator analysis (are we on track?)
5. Staff engagement and sustainability recommendations"""

        elif step_number == 5:
            # Comprehensive outcome analysis
            prompt = f"""Analyze quality improvement initiative outcomes and sustainability:

Initiative: {all_data.get('problem_identification', {}).get('problem_statement', 'N/A')}
Baseline Value: {all_data.get('baseline_metrics', {}).get('primary_metric_value', 'N/A')}
Final Value: {step_data.get('final_metric_value', 'N/A')}
Target Achieved: {step_data.get('target_achieved', 'N/A')}
Outcome Summary: {step_data.get('outcome_summary', 'N/A')}
Lessons Learned: {step_data.get('lessons_learned', 'N/A')}
Sustainability Plan: {step_data.get('sustainability_plan', 'N/A')}
Spread Potential: {step_data.get('spread_potential', 'N/A')}

Provide:
1. Statistical and clinical significance of results
2. Success factors and key lessons learned
3. Sustainability recommendations and monitoring plan
4. Spread strategy for other units/facilities
5. Publication/presentation opportunities (professional development)"""

        else:
            prompt = f"Analyze quality improvement data for {step_name}: {step_data}"

        # Generate AI analysis
        ai_response = await service.generate_response(
            prompt=prompt, context="quality_improvement_analysis"
        )

        return {
            "step_name": step_name,
            "analysis_available": True,
            "qi_insights": ai_response.get("response", "AI analysis temporarily unavailable"),
            "evidence_level": "AI-generated recommendations based on nursing literature and best practices",
            "disclaimer": "AI-generated quality improvement insights for professional use. Validate recommendations with organizational policies and evidence-based guidelines.",
            "ai_model": ai_response.get("model", "gpt-4"),
            "service_status": ai_response.get("service_status", "available"),
        }

    except Exception as e:
        logger.error(f"QI AI analysis failed for step {step_number}: {e}")
        return _fallback_qi_analysis(step_name)


def _fallback_qi_analysis(step_name: str) -> dict[str, Any]:
    """Fallback QI analysis when AI is unavailable."""
    return {
        "step_name": step_name,
        "analysis_available": False,
        "message": "AI quality improvement analysis temporarily unavailable",
        "fallback_note": "Proceed with quality improvement using standard QI methodologies (PDSA, Lean, Six Sigma) and organizational QI resources",
        "recommended_resources": [
            "Institute for Healthcare Improvement (IHI) resources",
            "Agency for Healthcare Research and Quality (AHRQ) toolkit",
            "Organizational quality improvement department",
            "Professional QI literature and evidence-based guidelines",
        ],
    }
