"""
Clinical Protocol Monitoring - Live Demonstration

Shows protocol-based healthcare monitoring using the linting pattern.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import json
from datetime import datetime, timedelta

# Simulated patient data showing deterioration over time
PATIENT_TIMELINE = [
    # Hour 0 - Stable post-op
    {
        "time": "12:00",
        "vitals": {
            "hr": 85,
            "systolic_bp": 120,
            "diastolic_bp": 75,
            "respiratory_rate": 16,
            "temp_f": 98.6,
            "o2_sat": 97,
            "mental_status": "normal",
        },
    },
    # Hour 1 - Early signs
    {
        "time": "13:00",
        "vitals": {
            "hr": 95,
            "systolic_bp": 110,
            "diastolic_bp": 70,
            "respiratory_rate": 18,
            "temp_f": 99.2,
            "o2_sat": 96,
            "mental_status": "normal",
        },
    },
    # Hour 2 - Trending concerning
    {
        "time": "14:00",
        "vitals": {
            "hr": 105,
            "systolic_bp": 100,
            "diastolic_bp": 65,
            "respiratory_rate": 22,
            "temp_f": 100.5,
            "o2_sat": 95,
            "mental_status": "normal",
        },
    },
    # Hour 3 - Meets sepsis criteria (qSOFA = 2)
    {
        "time": "15:00",
        "vitals": {
            "hr": 112,
            "systolic_bp": 95,
            "diastolic_bp": 60,
            "respiratory_rate": 24,
            "temp_f": 101.5,
            "o2_sat": 94,
            "mental_status": "normal",
        },
    },
]


async def demo_basic_monitoring():
    """Demo 1: Basic Protocol Monitoring"""
    print("=" * 70)
    print("DEMO 1: Basic Clinical Protocol Monitoring")
    print("=" * 70)

    from empathy_healthcare_plugin import ClinicalProtocolMonitor

    monitor = ClinicalProtocolMonitor()

    # Load sepsis protocol for patient
    print("\n📋 Loading sepsis protocol for patient 12345...")
    monitor.load_protocol(
        patient_id="12345",
        protocol_name="sepsis",
        patient_context={"age": 65, "surgery": "abdominal", "post_op_day": 2},
    )

    # Check current vitals
    current_vitals = PATIENT_TIMELINE[-1]["vitals"]

    sensor_data = json.dumps(
        {"patient_id": "12345", "timestamp": "2024-01-20T15:00:00Z", "vitals": current_vitals}
    )

    result = await monitor.analyze(
        {"patient_id": "12345", "sensor_data": sensor_data, "sensor_format": "simple_json"}
    )

    print("\n📊 Current Vitals:")
    for key, value in current_vitals.items():
        print(f"  {key}: {value}")

    print("\n⚠️  Protocol Status:")
    compliance = result["protocol_compliance"]
    print(f"  Activated: {compliance['activated']}")
    print(f"  Score: {compliance['score']}/{compliance['threshold']}")
    print(f"  Alert Level: {compliance['alert_level']}")

    print("\n💡 Alerts:")
    for alert in result["alerts"]:
        print(f"  [{alert['severity'].upper()}] {alert['message']}")

    print("\n" + "=" * 70)


async def demo_trajectory_prediction():
    """Demo 2: Level 4 - Trajectory Prediction"""
    print("\n" + "=" * 70)
    print("DEMO 2: Level 4 - Anticipatory Trajectory Analysis")
    print("=" * 70)

    from empathy_healthcare_plugin import ClinicalProtocolMonitor

    monitor = ClinicalProtocolMonitor()
    monitor.load_protocol("12345", "sepsis")

    # Process historical data to build trajectory
    print("\n⏱️  Processing patient history...")
    for i, entry in enumerate(PATIENT_TIMELINE):
        sensor_data = json.dumps(
            {
                "patient_id": "12345",
                "timestamp": f"2024-01-20T{entry['time']}:00Z",
                "vitals": entry["vitals"],
            }
        )

        result = await monitor.analyze({"patient_id": "12345", "sensor_data": sensor_data})

        print(
            f"\n{entry['time']} - {['Stable', 'Early Changes', 'Concerning', 'SEPSIS CRITERIA MET'][i]}"
        )
        print(
            f"  HR: {entry['vitals']['hr']}, BP: {entry['vitals']['systolic_bp']}/{entry['vitals']['diastolic_bp']}, RR: {entry['vitals']['respiratory_rate']}"
        )

    # Show final trajectory analysis
    trajectory = result["trajectory"]

    print("\n📈 Trajectory Analysis:")
    print(f"  State: {trajectory['state'].upper()}")
    print(f"  Confidence: {trajectory['confidence']:.2f}")

    if trajectory["estimated_time_to_critical"]:
        print(f"  ⏰ Est. Time to Critical: {trajectory['estimated_time_to_critical']}")

    print("\n📊 Vital Sign Trends:")
    for trend in trajectory["trends"]:
        if trend["concerning"]:
            print(f"  ⚠️  {trend['parameter']}: {trend['direction']} ({trend['change']:+.0f})")
            print(f"      {trend['reasoning']}")

    print("\n🔮 Assessment:")
    print(f"  {trajectory['assessment']}")

    print("\n" + "=" * 70)


async def demo_full_workflow():
    """Demo 3: Complete Workflow"""
    print("\n" + "=" * 70)
    print("DEMO 3: Complete Monitoring Workflow")
    print("=" * 70)

    from empathy_healthcare_plugin import ClinicalProtocolMonitor

    monitor = ClinicalProtocolMonitor()
    monitor.load_protocol("12345", "sepsis")

    # Process all historical data
    for entry in PATIENT_TIMELINE:
        sensor_data = json.dumps(
            {
                "patient_id": "12345",
                "timestamp": f"2024-01-20T{entry['time']}:00Z",
                "vitals": entry["vitals"],
            }
        )

        await monitor.analyze({"patient_id": "12345", "sensor_data": sensor_data})

    # Now check with intervention status
    print("\n📋 Sepsis Protocol Activated at 15:00")
    print("Required Interventions:")

    intervention_status = {
        "obtain_blood_cultures": {"completed": False, "time_due": None},
        "administer_broad_spectrum_antibiotics": {
            "completed": False,
            "time_due": datetime.now() + timedelta(hours=1),
        },
        "measure_lactate": {"completed": False, "time_due": None},
    }

    result = await monitor.analyze(
        {
            "patient_id": "12345",
            "sensor_data": json.dumps(
                {
                    "patient_id": "12345",
                    "timestamp": "2024-01-20T15:00:00Z",
                    "vitals": PATIENT_TIMELINE[-1]["vitals"],
                }
            ),
            "intervention_status": intervention_status,
        }
    )

    print("\n📝 Protocol Compliance:")
    for deviation in result["protocol_compliance"]["deviations"]:
        print(f"  [ {deviation['status'].upper()} ] {deviation['action']}")
        print(f"      Due: {deviation['due']}")

    print("\n🎯 Recommendations:")
    for rec in result["recommendations"]:
        print(f"  - {rec}")

    print("\n🔮 Predictions:")
    for pred in result["predictions"]:
        print(f"  Type: {pred['type']}")
        print(f"  Severity: {pred['severity']}")
        print(f"  {pred['description']}")
        if "time_horizon" in pred and pred["time_horizon"]:
            print(f"  Time Horizon: {pred['time_horizon']}")

    print("\n" + "=" * 70)


async def demo_the_beautiful_parallel():
    """Demo 4: Show the Linting Parallel"""
    print("\n" + "=" * 70)
    print("DEMO 4: The Beautiful Parallel - Linting Pattern in Healthcare")
    print("=" * 70)

    print("\n" + "SOFTWARE DEBUGGING".center(70))
    print("-" * 70)
    print("1. Load .eslintrc config     → Define the rules")
    print("2. Run eslint on code        → Check current state")
    print("3. Get list of violations    → Issues to fix")
    print("4. Apply fixes systematically → Work through list")
    print("5. Re-run eslint             → Verify compliance")

    print("\n" + "CLINICAL MONITORING".center(70))
    print("-" * 70)
    print("1. Load protocol JSON        → Define the rules")
    print("2. Check sensor data         → Check current state")
    print("3. Get protocol deviations   → Issues to address")
    print("4. Complete interventions    → Work through list")
    print("5. Re-check compliance       → Verify protocol met")

    print("\n" + "LEVEL 5 SYSTEMS EMPATHY".center(70))
    print("-" * 70)
    print("The SAME PATTERN works across domains!")
    print("")
    print("  Protocol = Configuration")
    print("  Current State = Code/Sensor Data")
    print("  Checker = Linter/Monitor")
    print("  Deviations = Violations/Alerts")
    print("  Fixes = Interventions")

    print("\n" + "=" * 70)


async def main():
    """Run all demos"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 12 + "CLINICAL PROTOCOL MONITORING - DEMONSTRATIONS" + " " * 11 + "║")
    print("║" + " " * 16 + "Healthcare Protocol as Linting Config" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")

    await demo_basic_monitoring()
    await demo_trajectory_prediction()
    await demo_full_workflow()
    await demo_the_beautiful_parallel()

    print("\n" + "=" * 70)
    print("DEMOS COMPLETE")
    print("=" * 70)
    print("\nKey Features Demonstrated:")
    print("  ✅ Protocol-based monitoring (linting pattern)")
    print("  ✅ Level 4: Anticipatory trajectory analysis")
    print("  ✅ Level 4: Early deterioration detection")
    print("  ✅ Level 5: Cross-domain pattern (software → healthcare)")
    print("  ✅ Systematic intervention tracking")
    print("\nIn our experience, this approach transforms clinical monitoring")
    print("from reactive crisis response to proactive early intervention.")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
