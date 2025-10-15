"""
Clinical Wizards Router Registry
Following Router Organization pattern from copilot-instructions.md
"""

# Wizard router imports following Conditional Imports Pattern
try:
    from .sbar_wizard import router as sbar_wizard_router
    _has_sbar_wizard = True
except ImportError:
    _has_sbar_wizard = False
    sbar_wizard_router = None

try:
    from .treatment_plan_wizard import router as treatment_plan_router
    _has_treatment_plan = True
except ImportError:
    _has_treatment_plan = False
    treatment_plan_router = None

try:
    from .dosage_calculation import router as dosage_calculation_router
    _has_dosage_calculation = True
except ImportError:
    _has_dosage_calculation = False
    dosage_calculation_router = None

try:
    from .clinical_assessment import router as clinical_assessment_router
    _has_clinical_assessment = True
except ImportError:
    _has_clinical_assessment = False
    clinical_assessment_router = None

try:
    from .patient_education import router as patient_education_router
    _has_patient_education = True
except ImportError:
    _has_patient_education = False
    patient_education_router = None

try:
    from .quality_improvement import router as quality_improvement_router
    _has_quality_improvement = True
except ImportError:
    _has_quality_improvement = False
    quality_improvement_router = None

# Export available wizards
__all__ = [
    'sbar_wizard_router',
    'treatment_plan_router',
    'dosage_calculation_router',
    'clinical_assessment_router',
    'patient_education_router',
    'quality_improvement_router'
]

def get_available_wizards():
    """Get list of available wizard routers."""
    available = {}
    if _has_sbar_wizard and sbar_wizard_router:
        available['sbar'] = sbar_wizard_router
    if _has_treatment_plan and treatment_plan_router:
        available['treatment_plan'] = treatment_plan_router
    if _has_dosage_calculation and dosage_calculation_router:
        available['dosage_calculation'] = dosage_calculation_router
    if _has_clinical_assessment and clinical_assessment_router:
        available['clinical_assessment'] = clinical_assessment_router
    if _has_patient_education and patient_education_router:
        available['patient_education'] = patient_education_router
    if _has_quality_improvement and quality_improvement_router:
        available['quality_improvement'] = quality_improvement_router

    return available