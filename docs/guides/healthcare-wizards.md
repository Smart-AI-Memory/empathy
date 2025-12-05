# Healthcare Wizards

Complete guide to HIPAA-compliant Level 4 Anticipatory wizards for healthcare applications.

!!! tip "Try the Live Demo"
    Explore all 23 healthcare wizards in action at **[healthcare.smartaimemory.com](https://healthcare.smartaimemory.com/static/dashboard.html)**. Test the complete workflow from data entry to document generation - no installation required.

---

## Overview

The **Healthcare Wizards** provide specialized AI assistants for medical applications with built-in PHI protection, HIPAA compliance, and clinical decision support.

**Key Benefits**:
- :material-hospital-box: **Improve patient outcomes** - Earlier detection of clinical deterioration
- :material-shield-check: **HIPAA compliant by default** - Automatic PHI scrubbing and encryption
- :material-clock-fast: **Save nursing time** - Streamlined documentation and handoff processes

!!! warning "Legal Disclaimer"
    These wizards provide clinical decision support but do not replace clinical judgment. All recommendations must be reviewed by qualified healthcare professionals. Consult legal counsel for HIPAA compliance in your specific implementation.

---

## The Healthcare Wizard Suite

### 1. Clinical Protocol Monitor

**Continuously monitors patient data against evidence-based clinical protocols**

Like a "linting system" for patient care - compares real-time patient data against standardized protocols and alerts when deviations occur.

#### Clinical Protocols Supported

| Protocol | Triggers | Alerts | Evidence Base |
|----------|----------|--------|---------------|
| **Sepsis Screening** | qSOFA ≥ 2 | 30-60 min earlier | Surviving Sepsis Campaign |
| **Post-Operative Monitoring** | Vital sign trends | Early intervention | ERAS Society |
| **Cardiac Monitoring** | Arrhythmia, ischemia | Real-time alerts | AHA/ACC Guidelines |
| **Medication Safety** | Drug interactions | Before administration | Lexi-Comp, FDA |
| **Fall Risk Assessment** | Morse Fall Scale | Proactive prevention | Joint Commission |

#### How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Real-Time Patient Data (Every 5-15 seconds)            │
│  ├─ Heart Rate: 110 bpm                                 │
│  ├─ Blood Pressure: 95/60 mmHg                          │
│  ├─ O2 Saturation: 94%                                  │
│  ├─ Respiratory Rate: 24/min                            │
│  ├─ Temperature: 38.2°C                                 │
│  └─ Mental Status: Alert                                │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Clinical Protocol Monitor                              │
│  ├─ Compare against Sepsis Protocol                     │
│  ├─ Calculate qSOFA score: 2 (BP + RR)                  │
│  ├─ Trajectory: Score increasing (was 1, now 2)         │
│  └─ ALERT: Sepsis pathway activation recommended        │
└─────────────────────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────┐
│  Nurse Notification (SBAR Format)                       │
│  S - Situation: Patient meets sepsis criteria (qSOFA 2) │
│  B - Background: Post-op day 2, abdominal surgery       │
│  A - Assessment: Early sepsis likely                    │
│  R - Recommendation: Initiate sepsis bundle             │
└─────────────────────────────────────────────────────────┘
```

#### Example: Sepsis Protocol

```python
from empathy_llm_toolkit.wizards import ClinicalProtocolMonitor

# Initialize with sepsis protocol
monitor = ClinicalProtocolMonitor(
    protocol="sepsis_screening_v2024",
    patient_id="PT123456",
    enable_security=True  # HIPAA-compliant PHI scrubbing
)

# Stream real-time vitals
vitals = {
    "timestamp": "2025-11-25T14:30:00Z",
    "heart_rate": 110,
    "systolic_bp": 95,
    "diastolic_bp": 60,
    "respiratory_rate": 24,
    "temperature": 38.2,
    "o2_saturation": 94,
    "mental_status": "alert"
}

# Check against protocol
result = await monitor.evaluate(vitals)

if result['alert_triggered']:
    print(f"🚨 ALERT: {result['alert_level']}")
    print(f"Protocol deviation: {result['deviation']}")
    print(f"qSOFA score: {result['scores']['qsofa']}")
    print(f"\nRecommended actions:")
    for action in result['recommended_actions']:
        print(f"  • {action}")

# Example output:
# 🚨 ALERT: HIGH
# Protocol deviation: qSOFA ≥ 2 (sepsis screening positive)
# qSOFA score: 2 (BP ≤ 100 + RR ≥ 22)
#
# Recommended actions:
#   • Obtain blood cultures before antibiotics
#   • Administer broad-spectrum antibiotics within 1 hour
#   • Measure lactate level
#   • Administer 30 mL/kg crystalloid if lactate ≥ 2 mmol/L
#   • Notify physician immediately
```

#### Sepsis Protocol JSON

```json
{
  "protocol_name": "sepsis_screening_and_management",
  "version": "2024.1",
  "applies_to": ["adult_inpatient"],

  "screening_criteria": {
    "name": "qSOFA",
    "description": "Quick Sequential Organ Failure Assessment",
    "threshold": 2,
    "criteria": [
      {
        "parameter": "systolic_bp",
        "condition": "<=",
        "value": 100,
        "points": 1,
        "alert": "Hypotension present"
      },
      {
        "parameter": "respiratory_rate",
        "condition": ">=",
        "value": 22,
        "points": 1,
        "alert": "Tachypnea present"
      },
      {
        "parameter": "mental_status",
        "condition": "altered",
        "points": 1,
        "alert": "Altered mental status"
      }
    ]
  },

  "sepsis_bundle": {
    "timeframe_hours": 3,
    "actions": [
      {
        "action": "measure_lactate",
        "timing": "immediately",
        "priority": "critical"
      },
      {
        "action": "obtain_blood_cultures",
        "timing": "before_antibiotics",
        "priority": "critical"
      },
      {
        "action": "administer_antibiotics",
        "timing": "within_1_hour",
        "priority": "critical"
      },
      {
        "action": "fluid_resuscitation",
        "timing": "within_3_hours",
        "volume": "30_ml_per_kg",
        "condition": "lactate_ge_2"
      }
    ]
  },

  "monitoring": {
    "frequency_minutes": 15,
    "parameters": [
      "vital_signs",
      "mental_status",
      "urine_output",
      "lactate_trend"
    ]
  }
}
```

---

### 2. SBAR Clinical Handoff Generator

**Automatically generates structured SBAR handoffs from patient data**

Reduces handoff time from 45 minutes to 5 minutes while improving completeness and reducing errors.

#### SBAR Format

- **S**ituation - What's happening now?
- **B**ackground - What's the clinical context?
- **A**ssessment - What do you think is going on?
- **R**ecommendation - What should be done?

#### Quick Example

```python
from empathy_llm_toolkit.wizards import SBARHandoffWizard

wizard = SBARHandoffWizard(
    enable_security=True,  # Scrub PHI before LLM processing
    classification="SENSITIVE"
)

# Generate handoff for shift change
handoff = await wizard.generate_handoff(
    patient_id="PT123456",
    handoff_type="shift_change",
    include_sections=["situation", "background", "assessment", "recommendation"]
)

print(handoff['sbar_report'])
```

#### Example Output

```
SBAR HANDOFF - Bed 312A

SITUATION:
65-year-old male, post-op day 2 from exploratory laparotomy for bowel
obstruction. Currently stable but showing early signs of sepsis:
- Vitals: HR 110, BP 95/60, RR 24, Temp 38.2°C, SpO2 94% on 2L
- qSOFA score: 2 (hypotension + tachypnea)
- Alert and oriented x3

BACKGROUND:
- PMH: Diabetes type 2, hypertension, prior appendectomy
- Surgical procedure: Ex-lap with small bowel resection, 11/23
- Pain managed with IV morphine, scheduled Tylenol
- I&O: Input 2400mL, Output 800mL (last 8h)
- Labs this AM: WBC 15.2, lactate pending

ASSESSMENT:
Concern for early sepsis. Patient meets sepsis screening criteria (qSOFA ≥ 2)
and trending toward septic shock. Hemodynamically borderline, needs close
monitoring and possible sepsis bundle activation.

RECOMMENDATION:
1. Continue q15min vital signs
2. Notify MD if BP < 90 systolic or mental status changes
3. Have sepsis bundle ready (blood cultures, antibiotics)
4. Recheck lactate within 2 hours
5. Consider transfer to step-down if deteriorates
```

#### Compliance Features

- **PHI Scrubbing**: Automatic removal of names, MRNs, DOBs before LLM processing
- **Audit Trail**: Logs all handoff generations with user ID and timestamp
- **Encryption**: AES-256-GCM for stored handoff data
- **Access Control**: Role-based permissions (RN, MD, PA levels)

---

### 3. Medication Safety Wizard

**Prevents medication errors before administration**

Checks for drug interactions, allergies, dosing errors, and contraindications.

#### Safety Checks

| Check Type | Examples | Alert Level |
|------------|----------|-------------|
| **Drug Interactions** | Warfarin + NSAIDs | CRITICAL |
| **Allergy Checking** | PCN allergy + Amoxicillin | CRITICAL |
| **Dose Range** | Pediatric dose too high | HIGH |
| **Contraindications** | Beta blocker + asthma | HIGH |
| **Duplicate Therapy** | Two ACE inhibitors | MEDIUM |
| **Renal Dosing** | No adjustment for CrCl | MEDIUM |

#### Example: Drug Interaction Check

```python
from empathy_llm_toolkit.wizards import MedicationSafetyWizard

wizard = MedicationSafetyWizard(enable_security=True)

# Check medication order
result = await wizard.check_medication_order({
    "patient_id": "PT123456",
    "medication": "Ibuprofen 600mg PO",
    "frequency": "q6h PRN pain",
    "current_medications": [
        "Warfarin 5mg PO daily",
        "Metoprolol 50mg PO BID",
        "Lisinopril 20mg PO daily"
    ],
    "allergies": ["Codeine"],
    "creatinine": 1.8,
    "weight_kg": 75
})

if result['interactions']:
    for interaction in result['interactions']:
        print(f"⚠️  {interaction['severity']}: {interaction['interaction']}")
        print(f"   Mechanism: {interaction['mechanism']}")
        print(f"   Clinical effect: {interaction['clinical_effect']}")
        print(f"   Recommendation: {interaction['recommendation']}")

# Output:
# ⚠️  CRITICAL: Warfarin + Ibuprofen
#    Mechanism: NSAIDs inhibit platelet function and may cause GI bleeding
#    Clinical effect: Significantly increased bleeding risk
#    Recommendation: Use acetaminophen instead, or if NSAID needed,
#                    monitor INR closely and consider GI prophylaxis
```

---

### 4. Post-Operative Monitoring Wizard

**Monitors surgical patients for complications**

Tracks Enhanced Recovery After Surgery (ERAS) protocols and early warning scores.

#### Monitored Complications

- **Surgical site infection** - Temperature, WBC trends
- **Anastomotic leak** - Abdominal distention, fever, tachycardia
- **Respiratory complications** - Atelectasis, pneumonia, PE
- **Cardiovascular events** - MI, DVT, stroke
- **Renal impairment** - Creatinine trends, urine output

#### Example: Post-Op Day 2 Assessment

```python
from empathy_llm_toolkit.wizards import PostOperativeMonitoringWizard

wizard = PostOperativeMonitoringWizard(
    protocol="colorectal_surgery_eras",
    enable_security=True
)

# Morning assessment
assessment = await wizard.assess_patient({
    "patient_id": "PT123456",
    "post_op_day": 2,
    "surgery": "laparoscopic_colectomy",
    "vitals": {
        "hr": 110,
        "bp": "95/60",
        "temp": 38.3,
        "rr": 22,
        "o2_sat": 94
    },
    "pain_score": 4,
    "tolerating_diet": "clear_liquids",
    "bowel_function": "no_flatus",
    "drain_output": "30ml_serosanguinous",
    "labs": {
        "wbc": 15.2,
        "creatinine": 1.3,
        "lactate": 2.1
    }
})

print(f"Early Warning Score: {assessment['ews_score']}/20")
print(f"Risk level: {assessment['risk_level']}")
print(f"\nConcerns:")
for concern in assessment['concerns']:
    print(f"  • {concern['issue']}")
    print(f"    Action: {concern['recommended_action']}")

# Output:
# Early Warning Score: 6/20
# Risk level: MEDIUM-HIGH
#
# Concerns:
#   • Meets sepsis screening criteria (qSOFA 2)
#     Action: Obtain blood cultures, consider sepsis bundle
#   • Not meeting ERAS mobility goals
#     Action: Physical therapy consult, ambulate 3x today
#   • Delayed return of bowel function
#     Action: Continue clear liquids, assess for ileus
```

---

### 5. Fall Risk Assessment Wizard

**Predicts and prevents patient falls**

Uses Morse Fall Scale and trajectory analysis to identify high-risk patients before falls occur.

#### Risk Factors Analyzed

| Factor | Points | Example |
|--------|--------|---------|
| History of falling | 25 | Previous fall this admission |
| Secondary diagnosis | 15 | Multiple comorbidities |
| Ambulatory aid | 15-30 | Walker, furniture, wheelchair |
| IV/Heparin lock | 20 | Tethered to IV pole |
| Gait/Transferring | 10-20 | Impaired, requires assistance |
| Mental status | 15 | Confused, agitated |

#### Example Implementation

```python
from empathy_llm_toolkit.wizards import FallRiskWizard

wizard = FallRiskWizard(enable_security=True)

# Assess fall risk
assessment = await wizard.assess_fall_risk({
    "patient_id": "PT123456",
    "age": 78,
    "history_of_falls": True,
    "diagnoses": ["CHF", "COPD", "Dementia"],
    "ambulatory_aid": "walker",
    "iv_access": True,
    "gait": "unsteady",
    "mental_status": "oriented_x2",
    "medications": ["Oxycodone", "Ambien", "Metoprolol"]
})

print(f"Morse Fall Scale: {assessment['morse_score']}/125")
print(f"Risk level: {assessment['risk_category']}")
print(f"\nInterventions:")
for intervention in assessment['interventions']:
    print(f"  [{intervention['priority']}] {intervention['action']}")

# Output:
# Morse Fall Scale: 85/125
# Risk level: HIGH RISK
#
# Interventions:
#   [HIGH] Bed alarm activated
#   [HIGH] Fall risk band on wrist
#   [HIGH] Bed in lowest position, brakes locked
#   [MEDIUM] Hourly rounding protocol
#   [MEDIUM] Review medications - consider deprescribing Ambien
#   [MEDIUM] Physical therapy consult
```

---

### 6. Pressure Injury Prevention Wizard

**Prevents pressure ulcers through proactive risk assessment**

Uses Braden Scale and turning protocol compliance to reduce pressure injuries.

#### Quick Example

```python
from empathy_llm_toolkit.wizards import PressureInjuryWizard

wizard = PressureInjuryWizard(enable_security=True)

# Assess risk
result = await wizard.assess_pressure_injury_risk({
    "patient_id": "PT123456",
    "braden_score": 14,  # Moderate risk
    "mobility": "bedbound",
    "moisture": "occasionally_moist",
    "nutrition": "poor",
    "friction_shear": "potential_problem",
    "turning_compliance": {
        "scheduled_q2h": True,
        "actual_turns": [
            "08:00", "10:15", "12:00", "14:30"  # Missing 06:00 turn
        ]
    }
})

print(f"Braden Score: {result['braden_score']}/23")
print(f"Risk level: {result['risk_category']}")
print(f"Turning compliance: {result['turning_compliance']}%")
print(f"\nGap analysis:")
for gap in result['compliance_gaps']:
    print(f"  ⚠️  {gap}")
```

---

### 7. Cardiac Monitoring Wizard

**Real-time cardiac rhythm analysis and alert generation**

Detects arrhythmias, ST-segment changes, and ischemia from telemetry data.

#### Monitored Events

- **Life-threatening arrhythmias** - VT, VF, complete heart block
- **Significant bradycardia/tachycardia** - HR < 40 or > 140
- **ST-segment changes** - STEMI, ischemia
- **QT prolongation** - Risk for Torsades de Pointes
- **Atrial fibrillation with RVR** - A-fib > 120 bpm

---

### 8. Glucose Management Wizard

**Insulin dosing and hypoglycemia prevention**

Helps manage diabetic patients with safe insulin dosing and trend analysis.

#### Features

- **Sliding scale recommendations** - Based on current glucose and insulin sensitivity
- **Hypoglycemia prediction** - Alerts when trending toward low glucose
- **Hyperglycemia alerts** - DKA risk assessment
- **Insulin pump integration** - Validates pump settings

---

## Integration with EMR Systems

### HL7 FHIR Integration

```python
from empathy_llm_toolkit.wizards import HealthcareWizard
from empathy_llm_toolkit.integrations import FHIRIntegration

# Connect to FHIR server
fhir = FHIRIntegration(
    server_url="https://fhir.hospital.org",
    auth_token=os.getenv("FHIR_TOKEN")
)

# Get patient data
patient = await fhir.get_patient("PT123456")
vitals = await fhir.get_observations(
    patient_id="PT123456",
    category="vital-signs",
    time_range="last_8_hours"
)

# Run clinical protocol monitor
monitor = ClinicalProtocolMonitor(protocol="sepsis_screening")
result = await monitor.evaluate_fhir(patient, vitals)
```

### Epic Integration

```python
from empathy_llm_toolkit.integrations import EpicIntegration

epic = EpicIntegration(
    client_id=os.getenv("EPIC_CLIENT_ID"),
    environment="production"
)

# Real-time ADT feed
async for admission in epic.stream_adt_feed():
    wizard = SBARHandoffWizard()
    handoff = await wizard.generate_admission_handoff(admission)
    await epic.post_note(admission.patient_id, handoff['sbar_report'])
```

---

## HIPAA Compliance

### PHI Scrubbing

All healthcare wizards automatically scrub 18 HIPAA identifiers:

```python
# Before sending to LLM
input_text = "Patient John Doe (MRN 987654, DOB 01/15/1980) from 555-123-4567"

# After PHI scrubbing
scrubbed_text = "[PATIENT_NAME] (MRN [MRN], DOB [DOB]) from [PHONE]"

# LLM never sees actual PHI
```

### Encryption

All PHI is encrypted at rest using AES-256-GCM:

```python
wizard = HealthcareWizard(
    enable_security=True,
    encryption_key=os.getenv("ENCRYPTION_KEY"),
    classification="SENSITIVE"
)
```

### Audit Logging

Every PHI access is logged:

```json
{
  "timestamp": "2025-11-25T14:30:00Z",
  "user_id": "nurse@hospital.com",
  "patient_id": "PT123456",
  "action": "generate_sbar_handoff",
  "phi_elements": ["name", "dob", "mrn"],
  "authorization": "patient_consent_2025-11-20",
  "success": true
}
```

---

## Implementation Guide

### Phase 1: Pilot (2-4 weeks)

1. **Select pilot unit** - ICU or step-down unit (10-20 beds)
2. **Configure protocols** - Start with sepsis + fall risk
3. **Train staff** - 30-minute training per nurse
4. **Monitor usage** - Track alerts, response times, outcomes

### Phase 2: Expansion (4-8 weeks)

1. **Add protocols** - Post-op monitoring, medication safety
2. **Expand to more units** - Medical-surgical floors
3. **Integrate with EMR** - HL7 FHIR or vendor API
4. **Optimize alerts** - Reduce false positives

### Phase 3: Enterprise (3-6 months)

1. **Hospital-wide deployment** - All inpatient units
2. **Advanced features** - Predictive analytics, ML models
3. **Multi-facility** - Expand to affiliated hospitals
4. **Continuous improvement** - Regular protocol updates

---

## See Also

- [SBAR Clinical Handoff Example](../examples/sbar-clinical-handoff.md) - Complete implementation
- [HIPAA Compliance Guide](hipaa-compliance.md) - Compliance requirements
- [Security Architecture](security-architecture.md) - Technical security details
- [Industry Wizards](../api-reference/wizards.md) - All available wizards
