"""
Healthcare Patient Handoff Protocol (Simulated)

This code represents a typical patient handoff procedure
with CRITICAL GAPS that cause failures.

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9 (converts to Apache 2.0 on January 1, 2029)
"""


class PatientHandoff:
    """
    Patient handoff during shift change or transfer

    WARNING: This protocol has known vulnerabilities that
    lead to information loss and patient safety risks.
    """

    def __init__(self, patient_id: str, from_nurse: str, to_nurse: str):
        self.patient_id = patient_id
        self.from_nurse = from_nurse
        self.to_nurse = to_nurse
        self.handoff_time = None
        self.critical_info_transferred = False

    def perform_handoff(self, patient_data: dict):
        """
        Perform patient handoff during shift change

        CRITICAL GAP #1: No explicit verification step
        CRITICAL GAP #2: Assumes receiving nurse understands everything
        CRITICAL GAP #3: No checklist to ensure all critical info transferred
        """
        import time

        self.handoff_time = time.time()

        # Verbal handoff (information loss likely!)
        print(f"Nurse {self.from_nurse} to Nurse {self.to_nurse}:")
        print(f"Patient {self.patient_id} - {patient_data.get('diagnosis', 'Unknown')}")

        # PROBLEM: No verification that critical allergies were communicated!
        # PROBLEM: No verification of medication changes!
        # PROBLEM: No explicit sign-off that handoff is complete!

        if patient_data.get("allergies"):
            print(f"Allergies: {patient_data['allergies']}")
        # But what if the receiving nurse wasn't listening?
        # What if they assumed no allergies because it wasn't mentioned clearly?

        if patient_data.get("medications"):
            print(f"Medications: {patient_data['medications']}")
        # Again, no verification!

        # CRITICAL: This just returns without ensuring understanding
        return True  # Handoff "complete" but possibly unsafe!


def shift_change_handoff(outgoing_patients: list, incoming_nurse: str):
    """
    Handle handoff for all patients during shift change

    PROBLEM: Time pressure leads to incomplete handoffs
    PROBLEM: No standardized checklist
    PROBLEM: Verbal-only communication = high error rate
    """
    for patient in outgoing_patients:
        # Quick verbal handoff under time pressure
        handoff = PatientHandoff(
            patient_id=patient["id"], from_nurse=patient["current_nurse"], to_nurse=incoming_nurse
        )

        # CRITICAL VULNERABILITY: No verification loop
        # Studies show 23% failure rate without explicit verification!
        handoff.perform_handoff(patient)

        # Missing: Read-back verification
        # Missing: Critical information checklist
        # Missing: Explicit acknowledgment from receiving nurse

    # Shift change complete, but how many critical details were lost?
    return True


def patient_transfer_to_icu(patient_data: dict):
    """
    Transfer patient to ICU

    CRITICAL GAP: Handoff between departments without verification
    """
    # Floor nurse hands off to ICU nurse
    print(f"Transferring patient {patient_data['id']} to ICU...")
    print(f"Diagnosis: {patient_data.get('diagnosis', 'Unknown')}")
    print(f"Current vitals: {patient_data.get('vitals', {})}")

    # PROBLEM: No checklist ensuring:
    # - Allergies communicated
    # - Recent medication changes noted
    # - Code status verified
    # - Family contact info transferred
    # - Recent labs/imaging reviewed

    # PROBLEM: No explicit sign-off from ICU team
    # PROBLEM: Assumes ICU nurse has full context

    return "Transfer complete"  # But is it SAFE?


# Example usage showing the vulnerability
if __name__ == "__main__":
    # Shift change scenario
    patients_to_handoff = [
        {
            "id": "P12345",
            "diagnosis": "Pneumonia",
            "current_nurse": "Alice",
            "allergies": ["Penicillin", "Latex"],  # CRITICAL!
            "medications": ["Azithromycin 500mg"],
            "vitals": {"bp": "120/80", "hr": 72},
        },
        {
            "id": "P67890",
            "diagnosis": "Post-surgical recovery",
            "current_nurse": "Alice",
            "allergies": None,  # But was this communicated clearly?
            "medications": ["Morphine 2mg PRN", "Heparin"],
            "vitals": {"bp": "110/70", "hr": 68},
        },
    ]

    print("=== SHIFT CHANGE HANDOFF ===")
    print("Outgoing nurse: Alice")
    print("Incoming nurse: Bob")
    print()

    shift_change_handoff(patients_to_handoff, incoming_nurse="Bob")

    print("\n=== ANALYSIS ===")
    print("VULNERABILITIES DETECTED:")
    print("1. No explicit verification that critical info was received")
    print("2. No standardized checklist used")
    print("3. Verbal-only = high risk of information loss")
    print("4. Time pressure during shift change")
    print("5. Assumptions about what receiving party knows")
    print()
    print("CONSEQUENCE: Studies show 23% of handoffs without")
    print("verification steps result in critical information loss.")
    print()
    print("This is the PATTERN that Level 5 Empathy will transfer")
    print("to software deployment analysis!")
