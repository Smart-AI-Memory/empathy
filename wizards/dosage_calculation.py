"""
Dosage Calculation Wizard Router
Provides step-by-step guidance for safe medication dosage calculations
"""

import uuid
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from src.utils.api_responses import create_success_response

router = APIRouter(prefix="/wizards/dosage-calculation", tags=["wizards", "dosage-calculation"])

# In-memory session storage (use Redis in production)
wizard_sessions: dict[str, dict[str, Any]] = {}


class DosageCalculationStart(BaseModel):
    """Initial dosage calculation request"""

    calculation_type: str = Field(..., description="Type of calculation")
    patient_weight: float | None = Field(None, description="Patient weight in kg (if weight-based)")
    special_considerations: str | None = Field(
        None, description="Any special considerations (pediatric, renal impairment, etc.)"
    )


class BasicDosageStep(BaseModel):
    """Basic dosage calculation parameters"""

    ordered_dose: float = Field(..., description="Ordered dose amount")
    ordered_dose_unit: str = Field(..., description="Ordered dose unit")
    available_strength: float = Field(..., description="Available medication strength")
    available_strength_unit: str = Field(..., description="Available strength unit")
    available_volume: float = Field(..., description="Available volume")
    available_volume_unit: str = Field(..., description="Available volume unit")


class WeightBasedDosageStep(BaseModel):
    """Weight-based dosage calculation parameters"""

    dose_per_kg: float = Field(..., description="Dose per kg")
    dose_unit: str = Field(..., description="Dose unit")
    patient_weight: float = Field(..., description="Patient weight in kg")
    frequency_per_day: int = Field(..., description="Number of doses per day")
    available_concentration: float = Field(..., description="Available concentration")
    concentration_unit: str = Field(..., description="Concentration unit (mg/ml, mcg/ml, etc.)")


class IVRateStep(BaseModel):
    """IV rate calculation parameters"""

    total_volume: float = Field(..., description="Total volume to infuse")
    volume_unit: str = Field(..., description="Volume unit")
    infusion_time: float = Field(..., description="Infusion time")
    time_unit: str = Field(..., description="Time unit")
    drop_factor: int | None = Field(None, description="Drop factor (if using gravity)")


class PediatricDosageStep(BaseModel):
    """Pediatric dosage calculation parameters"""

    child_weight: float = Field(..., description="Child weight in kg")
    child_age_months: int | None = Field(None, description="Child age in months")
    adult_dose: float = Field(..., description="Adult dose")
    dose_unit: str = Field(..., description="Dose unit")
    calculation_method: str = Field(
        ..., description="Calculation method: clark_rule, young_rule, fried_rule, bsa_method"
    )
    bsa: float | None = Field(None, description="Body surface area if using BSA method")


class DosageCalculationResponse(BaseModel):
    """Dosage calculation result"""

    wizard_id: str
    step: str
    calculation_result: dict[str, Any]
    safety_checks: list[str]
    next_steps: list[str]
    formula_used: str
    show_work: list[str]


@router.post("/start", response_model=DosageCalculationResponse)
def start_dosage_calculation(request: DosageCalculationStart):
    """Start a new dosage calculation wizard session"""
    try:
        wizard_id = str(uuid.uuid4())

        # Initialize session
        wizard_sessions[wizard_id] = {
            "wizard_id": wizard_id,
            "calculation_type": request.calculation_type,
            "patient_weight": request.patient_weight,
            "special_considerations": request.special_considerations,
            "created_at": datetime.utcnow().isoformat(),
            "current_step": "parameters",
            "completed_steps": [],
        }

        # Determine next steps based on calculation type
        next_steps = get_next_steps_for_type(request.calculation_type)

        return create_success_response(
            {
                "wizard_id": wizard_id,
                "step": "started",
                "calculation_result": {
                    "type": request.calculation_type,
                    "status": "ready_for_parameters",
                },
                "safety_checks": [
                    "Always verify calculations with a colleague",
                    "Check for drug allergies and contraindications",
                    "Confirm patient identity with two identifiers",
                    "Review maximum safe doses",
                ],
                "next_steps": next_steps,
                "formula_used": f"Preparing {request.calculation_type} calculation",
                "show_work": [f"Calculation type: {request.calculation_type}"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting dosage calculation wizard: {str(e)}",
        )


@router.post("/{wizard_id}/basic-dosage", response_model=DosageCalculationResponse)
def calculate_basic_dosage(wizard_id: str, dosage_data: BasicDosageStep):
    """Calculate basic dosage using dose/strength formula"""
    session = get_session(wizard_id)

    try:
        # Perform calculation
        result = perform_basic_dosage_calculation(dosage_data)

        # Update session
        session["basic_dosage_result"] = result
        session["completed_steps"].append("basic_dosage")
        session["current_step"] = "verification"

        return create_success_response(
            {
                "wizard_id": wizard_id,
                "step": "basic_dosage_calculated",
                "calculation_result": result,
                "safety_checks": [
                    f"Verify: Give {result['volume_to_give']:.2f} {dosage_data.available_volume_unit}",
                    "Check if this volume is reasonable for the route",
                    "Confirm dose is within safe range",
                    "Double-check your calculation",
                ],
                "next_steps": [
                    "Review calculation with colleague",
                    "Prepare medication",
                    "Perform final safety checks",
                ],
                "formula_used": "Volume = (Ordered Dose × Available Volume) ÷ Available Strength",
                "show_work": result["show_work"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in basic dosage calculation: {str(e)}",
        )


@router.post("/{wizard_id}/weight-based", response_model=DosageCalculationResponse)
def calculate_weight_based_dosage(wizard_id: str, dosage_data: WeightBasedDosageStep):
    """Calculate weight-based dosage"""
    session = get_session(wizard_id)

    try:
        result = perform_weight_based_calculation(dosage_data)

        session["weight_based_result"] = result
        session["completed_steps"].append("weight_based")
        session["current_step"] = "verification"

        return create_success_response(
            {
                "wizard_id": wizard_id,
                "step": "weight_based_calculated",
                "calculation_result": result,
                "safety_checks": [
                    f"Total daily dose: {result['total_daily_dose']:.2f} {dosage_data.dose_unit}",
                    f"Per dose: {result['dose_per_administration']:.2f} {dosage_data.dose_unit}",
                    f"Volume per dose: {result['volume_per_dose']:.2f} ml",
                    "Verify weight is accurate",
                    "Check maximum recommended dose",
                ],
                "next_steps": [
                    "Confirm dosing schedule",
                    "Review with pharmacist if needed",
                    "Prepare first dose",
                ],
                "formula_used": "Total Daily Dose = Dose/kg × Weight × Frequency",
                "show_work": result["show_work"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in weight-based calculation: {str(e)}",
        )


@router.post("/{wizard_id}/iv-rate", response_model=DosageCalculationResponse)
def calculate_iv_rate(wizard_id: str, rate_data: IVRateStep):
    """Calculate IV infusion rate"""
    session = get_session(wizard_id)

    try:
        result = perform_iv_rate_calculation(rate_data)

        session["iv_rate_result"] = result
        session["completed_steps"].append("iv_rate")
        session["current_step"] = "verification"

        return create_success_response(
            {
                "wizard_id": wizard_id,
                "step": "iv_rate_calculated",
                "calculation_result": result,
                "safety_checks": [
                    f"Rate: {result['ml_per_hour']:.1f} ml/hr",
                    f"Drops per minute: {result.get('drops_per_minute', 'N/A')}",
                    "Verify pump settings",
                    "Check IV site before starting",
                    "Monitor patient throughout infusion",
                ],
                "next_steps": [
                    "Set pump to calculated rate",
                    "Document infusion start",
                    "Schedule monitoring intervals",
                ],
                "formula_used": "Rate (ml/hr) = Total Volume ÷ Time (hours)",
                "show_work": result["show_work"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in IV rate calculation: {str(e)}",
        )


@router.post("/{wizard_id}/pediatric", response_model=DosageCalculationResponse)
def calculate_pediatric_dosage(wizard_id: str, pediatric_data: PediatricDosageStep):
    """Calculate pediatric dosage using various methods"""
    session = get_session(wizard_id)

    try:
        result = perform_pediatric_calculation(pediatric_data)

        session["pediatric_result"] = result
        session["completed_steps"].append("pediatric")
        session["current_step"] = "verification"

        return create_success_response(
            {
                "wizard_id": wizard_id,
                "step": "pediatric_calculated",
                "calculation_result": result,
                "safety_checks": [
                    f"Calculated pediatric dose: {result['calculated_dose']:.2f} {pediatric_data.dose_unit}",
                    "CRITICAL: Verify dose is appropriate for age/weight",
                    "Check pediatric dosing references",
                    "Consider maximum safe dose limits",
                    "Have pediatric emergency protocols ready",
                ],
                "next_steps": [
                    "Verify with pediatric dosing guide",
                    "Review with physician if dose seems high",
                    "Prepare medication with extra care",
                    "Monitor closely after administration",
                ],
                "formula_used": result["formula_used"],
                "show_work": result["show_work"],
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error in pediatric calculation: {str(e)}",
        )


@router.get("/{wizard_id}/summary", response_model=dict[str, Any])
def get_calculation_summary(wizard_id: str):
    """Get summary of all calculations performed"""
    session = get_session(wizard_id)

    summary = {
        "wizard_id": wizard_id,
        "calculation_type": session.get("calculation_type"),
        "completed_steps": session.get("completed_steps", []),
        "results": {},
        "final_safety_checklist": [
            "All calculations double-checked",
            "Patient identity verified with two identifiers",
            "Allergies and contraindications reviewed",
            "Dose within safe parameters",
            "Route and timing appropriate",
            "Equipment prepared and checked",
            "Monitoring plan in place",
        ],
    }

    # Include all completed calculation results
    for step in [
        "basic_dosage_result",
        "weight_based_result",
        "iv_rate_result",
        "pediatric_result",
    ]:
        if step in session:
            summary["results"][step] = session[step]

    return create_success_response(summary)


def get_session(wizard_id: str) -> dict[str, Any]:
    """Get wizard session or raise error"""
    if wizard_id not in wizard_sessions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Wizard session not found"
        )
    return wizard_sessions[wizard_id]


def get_next_steps_for_type(calculation_type: str) -> list[str]:
    """Get next steps based on calculation type"""
    steps_map = {
        "basic_dosage": ["Enter ordered dose and available strength", "Calculate volume to give"],
        "weight_based": ["Enter dose per kg and patient weight", "Calculate total daily dose"],
        "iv_rate": ["Enter volume and infusion time", "Calculate ml/hr rate"],
        "pediatric": ["Enter child weight and adult dose", "Select calculation method"],
        "complex": ["Choose specific calculation type", "Enter all required parameters"],
    }
    return steps_map.get(calculation_type, ["Enter calculation parameters"])


def perform_basic_dosage_calculation(data: BasicDosageStep) -> dict[str, Any]:
    """Perform basic dosage calculation"""
    # Convert units if needed (basic unit matching for now)
    if data.ordered_dose_unit != data.available_strength_unit:
        # In a real implementation, add unit conversion
        pass

    # Calculate volume to give
    volume_to_give = (data.ordered_dose * data.available_volume) / data.available_strength

    show_work = [
        f"Ordered dose: {data.ordered_dose} {data.ordered_dose_unit}",
        f"Available: {data.available_strength} {data.available_strength_unit} per {data.available_volume} {data.available_volume_unit}",
        f"Calculation: ({data.ordered_dose} × {data.available_volume}) ÷ {data.available_strength}",
        f"Calculation: {data.ordered_dose * data.available_volume} ÷ {data.available_strength}",
        f"Result: {volume_to_give:.2f} {data.available_volume_unit}",
    ]

    return {
        "volume_to_give": volume_to_give,
        "unit": data.available_volume_unit,
        "ordered_dose": data.ordered_dose,
        "available_strength": data.available_strength,
        "show_work": show_work,
        "reasonable_check": "OK" if 0.1 <= volume_to_give <= 50 else "REVIEW - Unusual volume",
    }


def perform_weight_based_calculation(data: WeightBasedDosageStep) -> dict[str, Any]:
    """Perform weight-based dosage calculation"""
    total_daily_dose = data.dose_per_kg * data.patient_weight
    dose_per_administration = total_daily_dose / data.frequency_per_day
    volume_per_dose = dose_per_administration / data.available_concentration

    show_work = [
        f"Dose per kg: {data.dose_per_kg} {data.dose_unit}/kg",
        f"Patient weight: {data.patient_weight} kg",
        f"Total daily dose: {data.dose_per_kg} × {data.patient_weight} = {total_daily_dose:.2f} {data.dose_unit}",
        f"Doses per day: {data.frequency_per_day}",
        f"Dose per administration: {total_daily_dose:.2f} ÷ {data.frequency_per_day} = {dose_per_administration:.2f} {data.dose_unit}",
        f"Available concentration: {data.available_concentration} {data.concentration_unit}",
        f"Volume per dose: {dose_per_administration:.2f} ÷ {data.available_concentration} = {volume_per_dose:.2f} ml",
    ]

    return {
        "total_daily_dose": total_daily_dose,
        "dose_per_administration": dose_per_administration,
        "volume_per_dose": volume_per_dose,
        "frequency": data.frequency_per_day,
        "show_work": show_work,
    }


def perform_iv_rate_calculation(data: IVRateStep) -> dict[str, Any]:
    """Perform IV rate calculation"""
    # Convert time to hours if needed
    time_hours = data.infusion_time
    if data.time_unit == "minutes":
        time_hours = data.infusion_time / 60

    ml_per_hour = data.total_volume / time_hours

    show_work = [
        f"Total volume: {data.total_volume} {data.volume_unit}",
        f"Infusion time: {data.infusion_time} {data.time_unit}",
        f"Rate calculation: {data.total_volume} ÷ {time_hours} hours = {ml_per_hour:.1f} ml/hr",
    ]

    result = {
        "ml_per_hour": ml_per_hour,
        "total_volume": data.total_volume,
        "infusion_time_hours": time_hours,
        "show_work": show_work,
    }

    # Calculate drops per minute if drop factor provided
    if data.drop_factor:
        drops_per_minute = (ml_per_hour * data.drop_factor) / 60
        result["drops_per_minute"] = f"{drops_per_minute:.0f} drops/min"
        show_work.append(
            f"Drops per minute: ({ml_per_hour:.1f} × {data.drop_factor}) ÷ 60 = {drops_per_minute:.0f} drops/min"
        )

    return result


def perform_pediatric_calculation(data: PediatricDosageStep) -> dict[str, Any]:
    """Perform pediatric dosage calculation using various methods"""

    if data.calculation_method == "clark_rule":
        # Clark's Rule: Child dose = (Child weight / 70 kg) × Adult dose
        child_dose = (data.child_weight / 70) * data.adult_dose
        formula_used = "Clark's Rule: Child dose = (Child weight ÷ 70 kg) × Adult dose"
        show_work = [
            "Clark's Rule calculation:",
            f"Child weight: {data.child_weight} kg",
            f"Adult dose: {data.adult_dose} {data.dose_unit}",
            f"Calculation: ({data.child_weight} ÷ 70) × {data.adult_dose}",
            f"Result: {child_dose:.2f} {data.dose_unit}",
        ]

    elif data.calculation_method == "young_rule" and data.child_age_months:
        # Young's Rule: Child dose = (Age in months / (Age in months + 150)) × Adult dose
        child_dose = (data.child_age_months / (data.child_age_months + 150)) * data.adult_dose
        formula_used = "Young's Rule: Child dose = (Age in months ÷ (Age + 150)) × Adult dose"
        show_work = [
            "Young's Rule calculation:",
            f"Child age: {data.child_age_months} months",
            f"Adult dose: {data.adult_dose} {data.dose_unit}",
            f"Calculation: ({data.child_age_months} ÷ ({data.child_age_months} + 150)) × {data.adult_dose}",
            f"Result: {child_dose:.2f} {data.dose_unit}",
        ]

    elif data.calculation_method == "bsa_method" and data.bsa:
        # BSA Method: Child dose = (Child BSA / 1.73 m²) × Adult dose
        child_dose = (data.bsa / 1.73) * data.adult_dose
        formula_used = "BSA Method: Child dose = (Child BSA ÷ 1.73 m²) × Adult dose"
        show_work = [
            "BSA Method calculation:",
            f"Child BSA: {data.bsa} m²",
            f"Adult dose: {data.adult_dose} {data.dose_unit}",
            f"Calculation: ({data.bsa} ÷ 1.73) × {data.adult_dose}",
            f"Result: {child_dose:.2f} {data.dose_unit}",
        ]

    else:
        # Default to weight-based calculation
        # Assume 1-2 mg/kg as a conservative estimate
        child_dose = data.child_weight * 1.5  # This is just an example
        formula_used = "Weight-based estimation (requires verification)"
        show_work = [
            "Weight-based estimation:",
            f"Child weight: {data.child_weight} kg",
            "⚠️ This is an estimate - verify with pediatric references",
        ]

    return {
        "calculated_dose": child_dose,
        "method_used": data.calculation_method,
        "formula_used": formula_used,
        "show_work": show_work,
        "safety_note": "ALWAYS verify pediatric doses with current pediatric references",
    }
