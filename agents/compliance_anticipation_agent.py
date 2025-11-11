"""
Compliance Anticipation Agent - Level 4 Anticipatory Empathy

Multi-step LangGraph agent that predicts regulatory audits, identifies compliance
gaps, and prepares documentation proactively to achieve positive outcomes.

Key Features:
1. Audit Timeline Prediction (90+ days advance notice)
2. Compliance Assessment (automated gap detection)
3. Proactive Documentation (auto-generate audit packages)
4. Stakeholder Notification (actionable alerts)
5. Continuous Monitoring (track until audit completion)

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
import operator
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Annotated, TypedDict

from langchain_core.messages import AIMessage, BaseMessage
from langgraph.graph import END, StateGraph

logger = logging.getLogger(__name__)


# =============================================================================
# Agent State Management - Level 4 Anticipatory Empathy
# =============================================================================


class ComplianceAgentState(TypedDict):
    """
    Level 4 Anticipatory Agent State

    Follows Principle #13: "Agent State as Clinical Flowsheet"
    Every field answers a compliance question with clear audit trail.

    Design Philosophy:
    - State fields answer specific questions ("When?", "What?", "Who?", "How?")
    - All predictions include confidence scores and methods
    - Comprehensive audit trail for legal compliance
    - Actionable outputs (not just status reports)
    """

    # =========================================================================
    # Progress Tracking
    # =========================================================================
    current_step: int  # 1-5
    completed_steps: list[int]
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # =========================================================================
    # Audit Prediction (Step 1) - Answers: "When is next audit?"
    # =========================================================================
    next_audit_date: str  # ISO format: "2026-04-15"
    days_until_audit: int
    audit_type: str  # "joint_commission", "cms", "state_board", "custom"
    audit_cycle_months: int  # Typical cycle length (e.g., 36 for Joint Commission)

    # Prediction Metadata
    prediction_confidence: float  # 0.0-1.0
    prediction_method: str  # "historical_cycle", "regulatory_schedule", "manual_entry"
    prediction_generated_at: str  # ISO timestamp
    last_audit_date: str  # ISO format (basis for prediction)

    # =========================================================================
    # Anticipation Window (Step 2) - Answers: "Should we act now?"
    # =========================================================================
    anticipation_window_days: int  # Optimal range: 60-120 days
    is_within_anticipation_window: bool
    time_to_act: str  # "too_early", "early", "timely", "urgent", "too_late"

    # =========================================================================
    # Compliance Assessment (Step 3) - Answers: "Are we compliant?"
    # =========================================================================
    total_compliance_items: int
    compliant_items: int
    non_compliant_items: int
    compliance_percentage: float  # 0.0-100.0

    # Item-Level Detail
    compliance_categories: list[str]  # ["medication_safety", "documentation", "patient_safety"]
    category_scores: dict[str, float]  # {"medication_safety": 95.0, "documentation": 88.0}

    # =========================================================================
    # Gap Identification (Step 3) - Answers: "What needs fixing?"
    # =========================================================================
    compliance_gaps: list[dict]  # Detailed gap information
    gap_severity_distribution: dict[str, int]  # {"critical": 2, "high": 5, "medium": 10}

    # Gap Structure:
    # {
    #   "gap_id": "gap_001",
    #   "category": "medication_safety",
    #   "item": "High-risk medication double-checks",
    #   "description": "5 high-risk meds without documented double-check",
    #   "severity": "critical",  # critical, high, medium, low
    #   "patient_ids": ["P123", "P456"],
    #   "incident_dates": ["2025-01-15", "2025-01-18"],
    #   "action_required": "Review incidents, document verification",
    #   "estimated_time_to_fix": "50 minutes",
    #   "can_fix_retroactively": True,
    #   "legal_risk": "high"
    # }

    # =========================================================================
    # Documentation Preparation (Step 4) - Answers: "What evidence do we have?"
    # =========================================================================
    documentation_prepared: bool
    documentation_url: str  # Secure storage location
    documentation_files: list[str]  # ["compliance_summary.pdf", "gap_analysis.xlsx"]

    # Documentation Package Contents:
    documentation_package: dict
    # {
    #   "summary_report": {...},
    #   "evidence_files": [...],
    #   "gap_remediation_plan": {...},
    #   "timeline": {...},
    #   "audit_readiness_score": 85.5
    # }

    # =========================================================================
    # Stakeholder Notification (Step 5) - Answers: "Who needs to act?"
    # =========================================================================
    notification_sent: bool
    notification_recipients: list[str]  # ["charge_nurse", "nurse_manager", "cno"]
    notification_timestamp: str  # ISO timestamp

    # Action Items (Assigned Work)
    action_items: list[dict]
    # {
    #   "action_id": "action_001",
    #   "gap_id": "gap_001",
    #   "description": "Review 5 incidents, document double-checks",
    #   "severity": "critical",
    #   "assignee": "charge_nurse",
    #   "assignee_email": "charge.nurse@hospital.com",
    #   "deadline": "2025-02-15",
    #   "estimated_time": "50 minutes",
    #   "status": "pending",
    #   "created_at": "2025-01-20T10:00:00Z"
    # }

    # =========================================================================
    # Continuous Monitoring (Step 6) - Answers: "How do we track progress?"
    # =========================================================================
    monitoring_scheduled: bool
    monitoring_frequency: str  # "daily", "weekly", "biweekly", "monthly"
    next_check_date: str  # ISO format
    monitoring_until_date: str  # ISO format (audit date)

    # =========================================================================
    # Positive Outcome Tracking - Answers: "Are we improving?"
    # =========================================================================
    baseline_compliance_percentage: float  # Initial assessment
    current_compliance_percentage: float  # After interventions
    compliance_improvement: float  # Percentage points improved
    gaps_closed: int
    gaps_remaining: int

    # Trend Analysis
    compliance_trend: str  # "improving", "stable", "declining"
    trend_confidence: float  # 0.0-1.0

    # =========================================================================
    # Error Handling & Audit Trail
    # =========================================================================
    errors: list[str]
    warnings: list[str]

    # Full Audit Trail
    audit_trail: list[dict]
    # {
    #   "timestamp": "2025-01-20T10:00:00Z",
    #   "step": "predict_audit",
    #   "action": "Generated audit prediction",
    #   "details": {...},
    #   "user": "system"
    # }

    # =========================================================================
    # Metadata
    # =========================================================================
    hospital_id: str
    facility_name: str
    agent_version: str
    execution_id: str  # Unique ID for this agent run
    created_at: str  # ISO timestamp
    last_updated: str  # ISO timestamp


def create_initial_state(
    hospital_id: str, audit_type: str = "joint_commission"
) -> ComplianceAgentState:
    """
    Create initial agent state

    Args:
        hospital_id: Unique identifier for hospital/facility
        audit_type: Type of audit to anticipate

    Returns:
        Initialized ComplianceAgentState
    """
    now = datetime.now()
    execution_id = f"compliance_{now.strftime('%Y%m%d_%H%M%S')}_{hospital_id}"

    return ComplianceAgentState(
        # Progress
        current_step=1,
        completed_steps=[],
        messages=[],
        # Audit Prediction
        next_audit_date="",
        days_until_audit=0,
        audit_type=audit_type,
        audit_cycle_months=0,
        prediction_confidence=0.0,
        prediction_method="",
        prediction_generated_at="",
        last_audit_date="",
        # Anticipation Window
        anticipation_window_days=0,
        is_within_anticipation_window=False,
        time_to_act="",
        # Compliance Assessment
        total_compliance_items=0,
        compliant_items=0,
        non_compliant_items=0,
        compliance_percentage=0.0,
        compliance_categories=[],
        category_scores={},
        # Gaps
        compliance_gaps=[],
        gap_severity_distribution={},
        # Documentation
        documentation_prepared=False,
        documentation_url="",
        documentation_files=[],
        documentation_package={},
        # Notification
        notification_sent=False,
        notification_recipients=[],
        notification_timestamp="",
        action_items=[],
        # Monitoring
        monitoring_scheduled=False,
        monitoring_frequency="",
        next_check_date="",
        monitoring_until_date="",
        # Positive Outcomes
        baseline_compliance_percentage=0.0,
        current_compliance_percentage=0.0,
        compliance_improvement=0.0,
        gaps_closed=0,
        gaps_remaining=0,
        compliance_trend="",
        trend_confidence=0.0,
        # Error Handling
        errors=[],
        warnings=[],
        audit_trail=[],
        # Metadata
        hospital_id=hospital_id,
        facility_name="",
        agent_version="1.0.0",
        execution_id=execution_id,
        created_at=now.isoformat(),
        last_updated=now.isoformat(),
    )


# =============================================================================
# LangGraph Workflow Definition
# =============================================================================


def create_compliance_agent() -> StateGraph:
    """
    Create Level 4 Anticipatory Compliance Agent

    Workflow:
    1. Predict Audit Timeline → When will next audit occur?
    2. Check Anticipation Window → Should we act now?
    3. Assess Compliance → Are we ready?
    4. Identify Gaps → What needs fixing?
    5. Prepare Documentation → What evidence do we have?
    6. Notify Stakeholders → Who needs to act?
    7. Schedule Monitoring → How do we track progress?

    Level 4 Characteristics:
    - Predictive (acts 60-120 days before audit)
    - Proactive (prepares documentation without being asked)
    - Actionable (assigns specific tasks with deadlines)
    - Transparent (explains reasoning, provides confidence scores)
    """

    workflow = StateGraph(ComplianceAgentState)

    # Step 1: Audit Prediction
    workflow.add_node("predict_audit", predict_next_audit)
    workflow.add_node("check_window", check_anticipation_window)

    # Step 2-3: Assessment
    workflow.add_node("assess_compliance", assess_current_compliance)
    workflow.add_node("identify_gaps", identify_compliance_gaps)

    # Step 4: Documentation
    workflow.add_node("prepare_docs", prepare_audit_documentation)

    # Step 5: Notification
    workflow.add_node("notify", send_anticipatory_notifications)

    # Step 6: Monitoring
    workflow.add_node("schedule_monitor", schedule_continuous_monitoring)

    # Define edges
    workflow.set_entry_point("predict_audit")

    workflow.add_edge("predict_audit", "check_window")

    # Conditional: Only proceed if within anticipation window
    workflow.add_conditional_edges(
        "check_window",
        should_anticipate,
        {
            "anticipate": "assess_compliance",
            "too_early": END,
            "proceed_anyway": "assess_compliance",  # Urgent cases
        },
    )

    workflow.add_edge("assess_compliance", "identify_gaps")
    workflow.add_edge("identify_gaps", "prepare_docs")
    workflow.add_edge("prepare_docs", "notify")
    workflow.add_edge("notify", "schedule_monitor")
    workflow.add_edge("schedule_monitor", END)

    return workflow.compile()


# =============================================================================
# Node Implementations
# =============================================================================


def predict_next_audit(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 1: Predict when next audit will occur

    Methods (in order of preference):
    1. Regulatory schedule (published audit windows) - confidence: 0.95
    2. Historical cycle analysis (e.g., Joint Commission every 36 months) - confidence: 0.85
    3. Risk-based prediction (hospitals with violations audited more) - confidence: 0.70
    4. Manual entry (user provides expected date) - confidence: 0.90

    For positive outcomes:
    - Early prediction enables proactive preparation
    - Reduces stress and scrambling
    - Allows time to fix gaps without pressure
    """

    logger.info(f"[Step 1] Predicting {state['audit_type']} audit for {state['hospital_id']}")

    # Add to audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "predict_audit",
            "action": "Starting audit prediction",
            "details": {"audit_type": state["audit_type"]},
            "user": "system",
        }
    )

    # Get audit cycle for this type
    audit_cycles = {
        "joint_commission": 36,  # months
        "cms": 12,
        "state_board": 24,
        "custom": 36,
    }

    cycle_months = audit_cycles.get(state["audit_type"], 36)
    state["audit_cycle_months"] = cycle_months

    # TODO: Connect to real database to get last audit date
    # For now, simulate with example date
    # last_audit = get_last_audit_date(state["hospital_id"], state["audit_type"])

    # Example: Last Joint Commission audit was 2023-04-15
    last_audit = datetime(2023, 4, 15)
    state["last_audit_date"] = last_audit.isoformat()

    # Predict next audit (add cycle duration)
    predicted_date = last_audit + timedelta(days=cycle_months * 30)

    # Calculate days until
    days_until = (predicted_date - datetime.now()).days

    # Confidence based on audit type and data quality
    if state["audit_type"] == "joint_commission":
        confidence = 0.90  # High confidence - very regular cycle
    elif state["audit_type"] == "cms":
        confidence = 0.85  # Good confidence
    else:
        confidence = 0.75  # Moderate confidence

    # Update state
    state["next_audit_date"] = predicted_date.isoformat()
    state["days_until_audit"] = days_until
    state["prediction_confidence"] = confidence
    state["prediction_method"] = "historical_cycle"
    state["prediction_generated_at"] = datetime.now().isoformat()
    state["last_updated"] = datetime.now().isoformat()

    # Mark step complete
    state["completed_steps"].append(1)
    state["current_step"] = 2

    # Log prediction
    logger.info(
        f"Predicted audit: {predicted_date.strftime('%Y-%m-%d')} "
        f"({days_until} days away, {confidence:.0%} confidence)"
    )

    # Add message
    state["messages"].append(
        AIMessage(
            content=f"Predicted {state['audit_type']} audit on {predicted_date.strftime('%Y-%m-%d')} "
            f"(in {days_until} days) with {confidence:.0%} confidence"
        )
    )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "predict_audit",
            "action": "Prediction completed",
            "details": {
                "predicted_date": state["next_audit_date"],
                "days_until": days_until,
                "confidence": confidence,
                "method": "historical_cycle",
            },
            "user": "system",
        }
    )

    return state


def check_anticipation_window(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 2: Check if we're within optimal anticipation window

    Level 4 Guardrail:
    - Too early (>120 days): Preparation may become outdated, waste effort
    - Optimal (60-120 days): Ideal time for preparation without pressure
    - Urgent (30-60 days): Still helpful but less time to fix issues
    - Too late (<30 days): Limited time for comprehensive fixes

    For positive outcomes:
    - Acting at right time maximizes effectiveness
    - Avoids wasted effort (too early) or crisis mode (too late)
    """

    logger.info(f"[Step 2] Checking anticipation window ({state['days_until_audit']} days)")

    days_until = state["days_until_audit"]

    if 60 <= days_until <= 120:
        state["is_within_anticipation_window"] = True
        state["time_to_act"] = "timely"
        state["anticipation_window_days"] = days_until
        message = (
            f"✅ Within optimal anticipation window ({days_until} days). Perfect time to prepare."
        )

    elif days_until > 120:
        state["is_within_anticipation_window"] = False
        state["time_to_act"] = "too_early"
        state["anticipation_window_days"] = days_until
        message = f"⏰ Audit is {days_until} days away. Will re-check at 120 days out."
        state["warnings"].append(
            f"Audit predicted in {days_until} days. "
            f"Optimal anticipation window is 60-120 days. "
            f"Will schedule re-check for {(datetime.now() + timedelta(days=days_until - 120)).strftime('%Y-%m-%d')}"
        )

    elif 30 <= days_until < 60:
        state["is_within_anticipation_window"] = True
        state["time_to_act"] = "urgent"
        state["anticipation_window_days"] = days_until
        message = f"⚠️ Only {days_until} days until audit. Acting now (ideally would have started at 90 days)."
        state["warnings"].append(
            "Less than 60 days until audit. "
            "Limited time for comprehensive remediation. "
            "Recommend expedited action."
        )

    else:  # < 30 days
        state["is_within_anticipation_window"] = True
        state["time_to_act"] = "too_late"
        state["anticipation_window_days"] = days_until
        message = f"🚨 URGENT: Only {days_until} days until audit. Focus on critical gaps only."
        state["warnings"].append(
            "Less than 30 days until audit. "
            "Very limited time. Focus on critical compliance gaps only."
        )

    state["messages"].append(AIMessage(content=message))
    state["completed_steps"].append(2)
    state["current_step"] = 3
    state["last_updated"] = datetime.now().isoformat()

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "check_window",
            "action": "Anticipation window assessed",
            "details": {
                "days_until": days_until,
                "time_to_act": state["time_to_act"],
                "within_window": state["is_within_anticipation_window"],
            },
            "user": "system",
        }
    )

    logger.info(f"Anticipation window: {state['time_to_act']}")

    return state


def should_anticipate(state: ComplianceAgentState) -> str:
    """
    Routing function: Decide whether to proceed with anticipation

    Returns:
        "anticipate" - Within optimal window, proceed
        "too_early" - Too far out, schedule for later
        "proceed_anyway" - Urgent, proceed despite non-optimal timing
    """

    time_to_act = state["time_to_act"]

    if time_to_act == "too_early":
        return "too_early"
    elif time_to_act in ["urgent", "too_late"]:
        return "proceed_anyway"
    else:
        return "anticipate"


def assess_current_compliance(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 3A: Assess current compliance status

    Scans all compliance requirements for the audit type and determines
    current compliance percentage.

    For positive outcomes:
    - Comprehensive assessment identifies all issues upfront
    - Categorization helps prioritize remediation
    - Baseline measurement enables tracking improvement
    """

    logger.info(f"[Step 3A] Assessing compliance for {state['audit_type']}")

    # TODO: Connect to real compliance data
    # For now, simulate assessment

    # Get requirements for this audit type
    requirements = get_audit_requirements(state["audit_type"])

    # Example: Joint Commission has ~50 compliance items
    total_items = len(requirements)

    # Simulate compliance check
    # In production, this would scan actual documentation, EHR data, etc.
    compliant = 0
    non_compliant = 0
    category_scores = {}

    for req in requirements:
        # TODO: Check actual compliance
        # is_compliant = check_requirement_compliance(state["hospital_id"], req)

        # Simulated: 90% compliant
        import random

        is_compliant = random.random() < 0.90

        if is_compliant:
            compliant += 1
        else:
            non_compliant += 1

        # Track by category
        category = req["category"]
        if category not in category_scores:
            category_scores[category] = {"compliant": 0, "total": 0}

        category_scores[category]["total"] += 1
        if is_compliant:
            category_scores[category]["compliant"] += 1

    # Calculate percentages
    compliance_pct = (compliant / total_items * 100) if total_items > 0 else 0.0

    category_pct = {}
    for cat, scores in category_scores.items():
        category_pct[cat] = (
            (scores["compliant"] / scores["total"] * 100) if scores["total"] > 0 else 0.0
        )

    # Update state
    state["total_compliance_items"] = total_items
    state["compliant_items"] = compliant
    state["non_compliant_items"] = non_compliant
    state["compliance_percentage"] = compliance_pct
    state["compliance_categories"] = list(category_pct.keys())
    state["category_scores"] = category_pct

    # Set baseline if first assessment
    if state["baseline_compliance_percentage"] == 0.0:
        state["baseline_compliance_percentage"] = compliance_pct

    state["current_compliance_percentage"] = compliance_pct

    state["completed_steps"].append(3)
    state["current_step"] = 4
    state["last_updated"] = datetime.now().isoformat()

    # Message
    status_emoji = "✅" if compliance_pct >= 95 else "⚠️" if compliance_pct >= 85 else "🚨"
    state["messages"].append(
        AIMessage(
            content=f"{status_emoji} Compliance Assessment: {compliance_pct:.1f}% "
            f"({compliant}/{total_items} items compliant)"
        )
    )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "assess_compliance",
            "action": "Compliance assessed",
            "details": {
                "total_items": total_items,
                "compliant": compliant,
                "percentage": compliance_pct,
                "categories": category_pct,
            },
            "user": "system",
        }
    )

    logger.info(f"Compliance: {compliance_pct:.1f}% ({compliant}/{total_items})")

    return state


def identify_compliance_gaps(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 3B: Identify specific compliance gaps with actionable details

    For positive outcomes:
    - Specific patient IDs enable targeted remediation
    - Severity classification enables prioritization
    - Time estimates enable resource planning
    - Retroactive fix capability determines urgency
    """

    logger.info("[Step 3B] Identifying compliance gaps")

    # TODO: Connect to real gap detection system
    # For now, simulate common gaps

    gaps = []
    gap_id_counter = 1

    # Gap 1: Missing signatures (example)
    if state["compliance_percentage"] < 100:
        gaps.append(
            {
                "gap_id": f"gap_{gap_id_counter:03d}",
                "category": "documentation_completeness",
                "item": "Patient assessment signatures",
                "description": "5 patient assessments missing nurse signatures",
                "severity": "high",
                "patient_ids": ["P12345", "P12367", "P12389", "P12401", "P12423"],
                "incident_dates": [
                    "2025-01-15",
                    "2025-01-16",
                    "2025-01-18",
                    "2025-01-19",
                    "2025-01-20",
                ],
                "action_required": "Nurses must review and sign assessments retroactively",
                "estimated_time_to_fix": "25 minutes",
                "can_fix_retroactively": True,
                "legal_risk": "medium",
            }
        )
        gap_id_counter += 1

    # Gap 2: Medication double-checks
    if state["compliance_percentage"] < 98:
        gaps.append(
            {
                "gap_id": f"gap_{gap_id_counter:03d}",
                "category": "medication_safety",
                "item": "High-risk medication double-checks",
                "description": "2 high-risk medications administered without documented double-check",
                "severity": "critical",
                "patient_ids": ["P12350", "P12375"],
                "incident_dates": ["2025-01-17", "2025-01-19"],
                "action_required": "Review incidents, document verification process, implement reminder system",
                "estimated_time_to_fix": "45 minutes",
                "can_fix_retroactively": False,  # Can document review but can't undo administration
                "legal_risk": "high",
            }
        )
        gap_id_counter += 1

    # Gap 3: Restraint orders
    if state["compliance_percentage"] < 95:
        gaps.append(
            {
                "gap_id": f"gap_{gap_id_counter:03d}",
                "category": "patient_safety",
                "item": "Restraint order renewals",
                "description": "1 restraint order requires renewal",
                "severity": "high",
                "patient_ids": ["P12390"],
                "incident_dates": ["2025-01-18"],
                "action_required": "Provider must review and renew order immediately",
                "estimated_time_to_fix": "15 minutes",
                "can_fix_retroactively": False,
                "legal_risk": "high",
            }
        )
        gap_id_counter += 1

    # Calculate severity distribution
    severity_dist = {
        "critical": sum(1 for g in gaps if g["severity"] == "critical"),
        "high": sum(1 for g in gaps if g["severity"] == "high"),
        "medium": sum(1 for g in gaps if g["severity"] == "medium"),
        "low": sum(1 for g in gaps if g["severity"] == "low"),
    }

    state["compliance_gaps"] = gaps
    state["gap_severity_distribution"] = severity_dist
    state["gaps_remaining"] = len(gaps)
    state["last_updated"] = datetime.now().isoformat()

    # Message
    if len(gaps) == 0:
        state["messages"].append(
            AIMessage(content="🎉 No compliance gaps identified. Excellent work!")
        )
    else:
        state["messages"].append(
            AIMessage(
                content=f"⚠️ Identified {len(gaps)} compliance gaps: "
                f"{severity_dist['critical']} critical, "
                f"{severity_dist['high']} high, "
                f"{severity_dist['medium']} medium, "
                f"{severity_dist['low']} low"
            )
        )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "identify_gaps",
            "action": "Gaps identified",
            "details": {
                "gap_count": len(gaps),
                "severity_distribution": severity_dist,
                "gaps": [{"id": g["gap_id"], "description": g["description"]} for g in gaps],
            },
            "user": "system",
        }
    )

    logger.info(f"Identified {len(gaps)} gaps: {severity_dist}")

    return state


def prepare_audit_documentation(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 4: Prepare comprehensive audit documentation package

    For positive outcomes:
    - Pre-prepared documentation reduces audit day stress
    - Structured format ensures completeness
    - Gap remediation plan demonstrates proactive approach
    - Audit readiness score provides confidence metric
    """

    logger.info("[Step 4] Preparing audit documentation")

    # Generate documentation package
    doc_package = {
        "generated_at": datetime.now().isoformat(),
        "audit_type": state["audit_type"],
        "audit_date": state["next_audit_date"],
        "facility": state["hospital_id"],
        "summary_report": {
            "compliance_percentage": state["compliance_percentage"],
            "compliant_items": state["compliant_items"],
            "total_items": state["total_compliance_items"],
            "gap_count": len(state["compliance_gaps"]),
            "severity_breakdown": state["gap_severity_distribution"],
            "category_scores": state["category_scores"],
        },
        "evidence_files": [
            f"medication_administration_records_{state['hospital_id']}.pdf",
            f"patient_assessment_documentation_{state['hospital_id']}.pdf",
            f"infection_control_protocols_{state['hospital_id']}.pdf",
            f"emergency_equipment_checks_{state['hospital_id']}.pdf",
        ],
        "gap_remediation_plan": {
            "gaps": state["compliance_gaps"],
            "prioritization": "Critical → High → Medium → Low",
            "estimated_total_time": sum(
                int(g["estimated_time_to_fix"].split()[0])
                for g in state["compliance_gaps"]
                if g["estimated_time_to_fix"].split()[0].isdigit()
            ),
            "target_completion_date": (
                datetime.fromisoformat(state["next_audit_date"]) - timedelta(days=14)
            ).isoformat(),  # 2 weeks before audit
        },
        "timeline": {
            "baseline_assessment": state["created_at"],
            "gap_identification": datetime.now().isoformat(),
            "target_remediation_completion": (
                datetime.fromisoformat(state["next_audit_date"]) - timedelta(days=14)
            ).isoformat(),
            "final_verification": (
                datetime.fromisoformat(state["next_audit_date"]) - timedelta(days=7)
            ).isoformat(),
            "audit_date": state["next_audit_date"],
        },
        "audit_readiness_score": calculate_audit_readiness_score(state),
    }

    # Simulate storing documentation
    # TODO: Integrate with actual secure document storage (S3, SharePoint, etc.)
    doc_url = f"https://secure-docs.hospital.com/compliance/{state['execution_id']}"
    doc_files = [
        "compliance_summary_report.pdf",
        "gap_analysis_detailed.xlsx",
        "remediation_plan.pdf",
        "evidence_package.zip",
    ]

    state["documentation_prepared"] = True
    state["documentation_url"] = doc_url
    state["documentation_files"] = doc_files
    state["documentation_package"] = doc_package
    state["last_updated"] = datetime.now().isoformat()

    # Message
    state["messages"].append(
        AIMessage(
            content=f"📄 Documentation package prepared: {len(doc_files)} files ready at {doc_url}"
        )
    )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "prepare_docs",
            "action": "Documentation prepared",
            "details": {
                "file_count": len(doc_files),
                "url": doc_url,
                "readiness_score": doc_package["audit_readiness_score"],
            },
            "user": "system",
        }
    )

    logger.info(f"Documentation prepared: {doc_url}")

    return state


def send_anticipatory_notifications(
    state: ComplianceAgentState,
) -> ComplianceAgentState:
    """
    Step 5: Send notifications to stakeholders with actionable information

    For positive outcomes:
    - Early notification enables calm, planned response
    - Specific assignments clarify responsibilities
    - Deadlines provide urgency without panic
    - Transparent reasoning builds trust in AI system
    """

    logger.info("[Step 5] Sending notifications to stakeholders")

    # Create action items from gaps
    action_items = []
    action_id = 1

    for gap in state["compliance_gaps"]:
        assignee = determine_assignee(gap)
        deadline = calculate_deadline(gap, state["days_until_audit"], state["next_audit_date"])

        action_items.append(
            {
                "action_id": f"action_{action_id:03d}",
                "gap_id": gap["gap_id"],
                "description": gap["description"],
                "action_required": gap["action_required"],
                "severity": gap["severity"],
                "assignee": assignee,
                "assignee_email": get_assignee_email(assignee, state["hospital_id"]),
                "deadline": deadline,
                "estimated_time": gap["estimated_time_to_fix"],
                "status": "pending",
                "created_at": datetime.now().isoformat(),
            }
        )
        action_id += 1

    state["action_items"] = action_items

    # Determine recipients based on severity
    recipients = ["charge_nurse"]
    if state["gap_severity_distribution"].get("critical", 0) > 0:
        recipients.append("nurse_manager")
    if state["gap_severity_distribution"].get("critical", 0) > 2:
        recipients.append("cno")  # Chief Nursing Officer for multiple critical issues

    # Compose notification
    notification = compose_notification(state, action_items)

    # Send notification
    # TODO: Integrate with actual notification system (email, SMS, Slack, etc.)
    send_notification_to_recipients(notification, recipients, state["hospital_id"])

    state["notification_sent"] = True
    state["notification_recipients"] = recipients
    state["notification_timestamp"] = datetime.now().isoformat()
    state["last_updated"] = datetime.now().isoformat()

    # Message
    state["messages"].append(
        AIMessage(
            content=f"📧 Notifications sent to {len(recipients)} recipients: {', '.join(recipients)}"
        )
    )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "notify",
            "action": "Notifications sent",
            "details": {
                "recipients": recipients,
                "action_item_count": len(action_items),
            },
            "user": "system",
        }
    )

    logger.info(f"Notifications sent to: {recipients}")

    return state


def schedule_continuous_monitoring(state: ComplianceAgentState) -> ComplianceAgentState:
    """
    Step 6: Schedule periodic re-checks until audit

    For positive outcomes:
    - Regular monitoring tracks progress toward compliance
    - Early detection of new gaps prevents last-minute scrambling
    - Trend analysis predicts audit readiness
    - Automated reminders keep team accountable
    """

    logger.info("[Step 6] Scheduling continuous monitoring")

    days_until = state["days_until_audit"]

    # Determine monitoring frequency based on time remaining
    if days_until > 90:
        frequency = "monthly"
        next_check_days = 30
    elif days_until > 60:
        frequency = "biweekly"
        next_check_days = 14
    elif days_until > 30:
        frequency = "weekly"
        next_check_days = 7
    else:
        frequency = "daily"
        next_check_days = 1

    next_check_date = (datetime.now() + timedelta(days=next_check_days)).isoformat()

    state["monitoring_scheduled"] = True
    state["monitoring_frequency"] = frequency
    state["next_check_date"] = next_check_date
    state["monitoring_until_date"] = state["next_audit_date"]
    state["last_updated"] = datetime.now().isoformat()

    # Message
    state["messages"].append(
        AIMessage(
            content=f"⏰ Scheduled {frequency} monitoring until {state['next_audit_date']} "
            f"(next check: {next_check_date[:10]})"
        )
    )

    # Audit trail
    state["audit_trail"].append(
        {
            "timestamp": datetime.now().isoformat(),
            "step": "schedule_monitor",
            "action": "Monitoring scheduled",
            "details": {
                "frequency": frequency,
                "next_check": next_check_date,
                "until_date": state["next_audit_date"],
            },
            "user": "system",
        }
    )

    logger.info(f"Monitoring scheduled: {frequency} until {state['next_audit_date']}")

    return state


# =============================================================================
# Helper Functions
# =============================================================================


def get_audit_requirements(audit_type: str) -> list[dict]:
    """
    Get compliance requirements for audit type

    TODO: Load from database or configuration file
    """

    # Example requirements for Joint Commission
    if audit_type == "joint_commission":
        return [
            {
                "id": "JC_MED_001",
                "category": "medication_safety",
                "description": "Medication administration records",
            },
            {
                "id": "JC_MED_002",
                "category": "medication_safety",
                "description": "High-risk medication double-checks",
            },
            {
                "id": "JC_DOC_001",
                "category": "documentation",
                "description": "Patient assessment documentation",
            },
            {
                "id": "JC_DOC_002",
                "category": "documentation",
                "description": "Nurse signature completeness",
            },
            {
                "id": "JC_SAF_001",
                "category": "patient_safety",
                "description": "Restraint order renewals",
            },
            {
                "id": "JC_SAF_002",
                "category": "patient_safety",
                "description": "Fall risk assessments",
            },
            {
                "id": "JC_INF_001",
                "category": "infection_control",
                "description": "Hand hygiene compliance",
            },
            {
                "id": "JC_INF_002",
                "category": "infection_control",
                "description": "Isolation protocol adherence",
            },
            # ... would have ~50 total requirements
        ]

    # Add other audit types as needed
    return []


def calculate_audit_readiness_score(state: ComplianceAgentState) -> float:
    """
    Calculate overall audit readiness score (0-100)

    Factors:
    - Compliance percentage (60% weight)
    - Gap severity (20% weight)
    - Time remaining (20% weight)
    """

    # Factor 1: Compliance percentage
    compliance_score = state["compliance_percentage"]

    # Factor 2: Gap severity penalty
    severity_penalties = {
        "critical": 10,  # -10 points per critical gap
        "high": 5,
        "medium": 2,
        "low": 0.5,
    }

    severity_penalty = sum(
        count * severity_penalties.get(severity, 0)
        for severity, count in state["gap_severity_distribution"].items()
    )

    gap_score = max(0, 100 - severity_penalty)

    # Factor 3: Time remaining score
    days_until = state["days_until_audit"]
    if days_until >= 90:
        time_score = 100
    elif days_until >= 60:
        time_score = 80
    elif days_until >= 30:
        time_score = 60
    else:
        time_score = 40

    # Weighted average
    readiness_score = compliance_score * 0.6 + gap_score * 0.2 + time_score * 0.2

    return round(readiness_score, 1)


def determine_assignee(gap: dict) -> str:
    """
    Determine who should be assigned to fix this gap

    Based on category and severity
    """

    category = gap["category"]
    severity = gap["severity"]

    if category == "medication_safety":
        if severity == "critical":
            return "nurse_manager"  # Manager handles critical safety issues
        else:
            return "charge_nurse"

    elif category == "documentation":
        return "charge_nurse"  # Charge nurse coordinates documentation fixes

    elif category == "patient_safety":
        if "restraint" in gap["item"].lower():
            return "provider"  # Restraint orders require provider
        else:
            return "charge_nurse"

    elif category == "infection_control":
        return "infection_control_nurse"

    else:
        return "charge_nurse"  # Default


def calculate_deadline(gap: dict, days_until_audit: int, audit_date: str) -> str:
    """
    Calculate appropriate deadline for fixing gap

    - Critical: 1 week or 25% of time remaining (whichever is sooner)
    - High: 2 weeks or 50% of time remaining
    - Medium: 1 month or 75% of time remaining
    - Low: 2 weeks before audit
    """

    severity = gap["severity"]

    if severity == "critical":
        # 1 week or 25% of time
        deadline_days = min(7, days_until_audit // 4)
    elif severity == "high":
        # 2 weeks or 50% of time
        deadline_days = min(14, days_until_audit // 2)
    elif severity == "medium":
        # 1 month or 75% of time
        deadline_days = min(30, int(days_until_audit * 0.75))
    else:  # low
        # 2 weeks before audit
        deadline_days = days_until_audit - 14

    # Ensure deadline is at least tomorrow
    deadline_days = max(1, deadline_days)

    deadline = datetime.now() + timedelta(days=deadline_days)

    return deadline.isoformat()


def get_assignee_email(assignee: str, hospital_id: str) -> str:
    """
    Get email address for assignee

    TODO: Look up from hospital staff database
    """

    # Example mapping
    email_map = {
        "charge_nurse": f"charge.nurse@{hospital_id}.hospital.com",
        "nurse_manager": f"nurse.manager@{hospital_id}.hospital.com",
        "cno": f"cno@{hospital_id}.hospital.com",
        "provider": f"provider@{hospital_id}.hospital.com",
        "infection_control_nurse": f"infection.control@{hospital_id}.hospital.com",
    }

    return email_map.get(assignee, f"{assignee}@{hospital_id}.hospital.com")


def compose_notification(state: ComplianceAgentState, action_items: list[dict]) -> dict:
    """
    Compose notification with all relevant information
    """

    days_until = state["days_until_audit"]
    compliance_pct = state["compliance_percentage"]
    gaps = state["compliance_gaps"]
    readiness_score = state["documentation_package"]["audit_readiness_score"]

    notification = {
        "type": "anticipatory_compliance_alert",
        "urgency": "high" if days_until < 60 else "medium",
        "title": f"{state['audit_type'].replace('_', ' ').title()} Audit Preparation",
        "summary": f"""
📋 **{state['audit_type'].replace('_', ' ').upper()} AUDIT PREPARATION**

**Audit Date:** {datetime.fromisoformat(state['next_audit_date']).strftime('%B %d, %Y')}
**Days Remaining:** {days_until} days
**Audit Readiness Score:** {readiness_score:.1f}/100

---

✅ **COMPLIANCE STATUS**
- Overall: {compliance_pct:.1f}% ({state['compliant_items']}/{state['total_compliance_items']} items)
- Target: 95%+ for audit success

**Category Breakdown:**
"""
        + "\n".join(f"- {cat}: {score:.1f}%" for cat, score in state["category_scores"].items())
        + f"""

---

⚠️  **GAPS REQUIRING ATTENTION ({len(gaps)} total)**
"""
        + "\n".join(f"[{g['severity'].upper()}] {g['description']}" for g in gaps[:5])
        + (f"\n... and {len(gaps) - 5} more (see full report)" if len(gaps) > 5 else "")
        + f"""

---

🎯 **ACTION ITEMS ({len(action_items)} tasks)**
"""
        + "\n".join(
            f"{i+1}. [{item['severity'].upper()}] {item['description']}\n"
            f"   → Assignee: {item['assignee']}\n"
            f"   → Deadline: {datetime.fromisoformat(item['deadline']).strftime('%Y-%m-%d')}\n"
            f"   → Time: {item['estimated_time']}"
            for i, item in enumerate(action_items[:3])
        )
        + (f"\n... and {len(action_items) - 3} more action items" if len(action_items) > 3 else "")
        + f"""

---

📂 **DOCUMENTATION PACKAGE**
Pre-prepared documentation available at:
{state['documentation_url']}

Files included:
"""
        + "\n".join(f"- {f}" for f in state["documentation_files"])
        + """

---

🤖 **ANTICIPATORY EMPATHY (Level 4)**

This alert was generated using predictive analytics based on your hospital's
audit history. By preparing now, we have sufficient time to address all gaps
without stress or rushed work during audit week.

**Prediction Details:**
- Method: Historical cycle analysis
- Confidence: {:.0%}
- Next monitoring check: {}

**Questions?** Contact your compliance coordinator or reply to this message.
        """.format(
            state["prediction_confidence"],
            datetime.fromisoformat(state["next_check_date"]).strftime("%Y-%m-%d"),
        ),
        "action_items": action_items,
        "documentation_url": state["documentation_url"],
        "priority": (
            "high" if state["gap_severity_distribution"].get("critical", 0) > 0 else "medium"
        ),
    }

    return notification


def send_notification_to_recipients(notification: dict, recipients: list[str], hospital_id: str):
    """
    Send notification via configured channels

    TODO: Integrate with actual notification system
    - Email (SMTP)
    - SMS (Twilio)
    - Slack/Teams (webhooks)
    - In-app notifications
    """

    logger.info(f"Sending notification to: {recipients}")

    # Simulate sending
    for recipient in recipients:
        email = get_assignee_email(recipient, hospital_id)
        logger.info(f"  → {recipient} ({email})")

        # TODO: Actual email/SMS/webhook integration
        # send_email(to=email, subject=notification["title"], body=notification["summary"])

    logger.info("Notifications sent successfully")


# =============================================================================
# Main Entry Point
# =============================================================================


async def run_compliance_agent(
    hospital_id: str, audit_type: str = "joint_commission"
) -> ComplianceAgentState:
    """
    Run the compliance anticipation agent

    Args:
        hospital_id: Hospital/facility identifier
        audit_type: Type of audit to anticipate

    Returns:
        Final agent state with all results
    """

    logger.info(f"Starting Compliance Anticipation Agent for {hospital_id} ({audit_type})")

    # Create agent
    agent = create_compliance_agent()

    # Initialize state
    initial_state = create_initial_state(hospital_id, audit_type)

    # Run agent
    final_state = await agent.ainvoke(initial_state)

    logger.info(
        f"Agent completed. Audit readiness score: "
        f"{final_state.get('documentation_package', {}).get('audit_readiness_score', 0):.1f}"
    )

    return final_state


if __name__ == "__main__":
    import asyncio

    # Example usage
    async def main():
        result = await run_compliance_agent(
            hospital_id="example_hospital_123", audit_type="joint_commission"
        )

        print("\n" + "=" * 80)
        print("COMPLIANCE ANTICIPATION AGENT RESULTS")
        print("=" * 80)
        print(f"Audit Date: {result['next_audit_date']}")
        print(f"Days Until: {result['days_until_audit']}")
        print(f"Compliance: {result['compliance_percentage']:.1f}%")
        print(f"Gaps: {len(result['compliance_gaps'])}")
        print(f"Action Items: {len(result['action_items'])}")
        print(f"Documentation: {result['documentation_url']}")
        print(
            f"Audit Readiness: {result['documentation_package']['audit_readiness_score']:.1f}/100"
        )
        print("=" * 80)

    asyncio.run(main())
