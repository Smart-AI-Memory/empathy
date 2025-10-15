"""
Trust-Building Behaviors for Level 4 Anticipatory Agents

Implements team dynamics that build trust through anticipatory actions:
- Pre-format data for handoffs (reduce cognitive load for next person)
- Clarify confusing instructions before execution (prevent wasted effort)
- Volunteer structure during stress (not pep talks, actual scaffolding)
- Proactively offer help when teammates are struggling

These behaviors demonstrate Level 4 Anticipatory Empathy by:
1. Predicting friction points (handoffs, confusion, stress, overload)
2. Acting without being asked (but without overstepping)
3. Providing structural relief (not just emotional support)
4. Building trust through consistent, helpful actions

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TrustBuildingBehaviors:
    """
    Level 4 Anticipatory trust-building behaviors

    Philosophy: Trust is earned through consistent, helpful actions that
    demonstrate understanding of team dynamics and proactive problem-solving.
    """

    @staticmethod
    def pre_format_for_handoff(data: Dict, next_person_role: str, context: str) -> Dict:
        """
        Scenario: Handoff Risk
        Anticipatory Response: Pre-format the data so next person doesn't waste time

        Example:
        - Raw compliance data → Formatted summary for charge nurse
        - Gap list → Prioritized action items with assignments
        - Assessment results → Executive dashboard for manager

        Trust Built:
        - "This AI understands my workflow"
        - "I don't have to translate data myself"
        - "My time is valued"
        """

        logger.info(f"Pre-formatting data for handoff to {next_person_role}")

        # Determine format based on recipient role
        if next_person_role == "charge_nurse":
            # Charge nurses need: Quick scan, action items, patient IDs
            formatted = {
                "format": "action_oriented",
                "summary": {
                    "critical_actions": [
                        item
                        for item in data.get("action_items", [])
                        if item.get("severity") == "critical"
                    ],
                    "high_priority_actions": [
                        item
                        for item in data.get("action_items", [])
                        if item.get("severity") == "high"
                    ],
                    "patient_ids_affected": list(
                        set(
                            pid
                            for gap in data.get("compliance_gaps", [])
                            for pid in gap.get("patient_ids", [])
                        )
                    ),
                    "estimated_total_time": sum(
                        int(item.get("estimated_time", "0 minutes").split()[0])
                        for item in data.get("action_items", [])
                        if item.get("estimated_time", "").split()[0].isdigit()
                    ),
                },
                "quick_scan_view": {
                    "red_flags": [
                        gap
                        for gap in data.get("compliance_gaps", [])
                        if gap.get("severity") in ["critical", "high"]
                    ],
                    "compliance_percentage": data.get("compliance_percentage", 0),
                    "days_until_audit": data.get("days_until_audit", 0),
                },
                "reasoning": (
                    "Pre-formatted for charge nurse workflow: "
                    "critical items first, patient IDs for chart review, "
                    "time estimate for shift planning"
                ),
            }

        elif next_person_role == "nurse_manager":
            # Managers need: Trends, resource allocation, escalation path
            formatted = {
                "format": "strategic_overview",
                "summary": {
                    "compliance_trend": data.get("compliance_trend", "unknown"),
                    "category_performance": data.get("category_scores", {}),
                    "resource_needs": {
                        "staff_time_required": f"{data.get('estimated_total_time', 0)} minutes",
                        "external_resources": [
                            (
                                "Provider orders"
                                if any(
                                    "provider" in item.get("assignee", "")
                                    for item in data.get("action_items", [])
                                )
                                else None
                            )
                        ],
                    },
                    "escalation_needed": len(
                        [
                            g
                            for g in data.get("compliance_gaps", [])
                            if g.get("severity") == "critical"
                        ]
                    )
                    > 2,
                },
                "reasoning": (
                    "Pre-formatted for manager workflow: "
                    "strategic view, resource allocation, escalation triggers"
                ),
            }

        elif next_person_role == "cno":
            # CNO needs: Executive summary, risk assessment, board reporting
            formatted = {
                "format": "executive_summary",
                "summary": {
                    "audit_readiness_score": data.get("audit_readiness_score", 0),
                    "risk_level": calculate_risk_level(data),
                    "board_talking_points": [
                        f"Overall compliance: {data.get('compliance_percentage', 0):.1f}%",
                        f"Audit in {data.get('days_until_audit', 0)} days",
                        f"{len(data.get('compliance_gaps', []))} gaps identified proactively",
                        "Remediation plan in place (target: 2 weeks before audit)",
                    ],
                    "legal_risk_summary": {
                        "high_risk_items": len(
                            [
                                g
                                for g in data.get("compliance_gaps", [])
                                if g.get("legal_risk") == "high"
                            ]
                        ),
                        "can_fix_before_audit": all(
                            g.get("can_fix_retroactively", True)
                            for g in data.get("compliance_gaps", [])
                        ),
                    },
                },
                "reasoning": (
                    "Pre-formatted for executive workflow: "
                    "board-ready summary, legal risk assessment, organizational impact"
                ),
            }

        else:
            # Default: Structured but general format
            formatted = {
                "format": "general_structured",
                "summary": data,
                "reasoning": "General structured format (no role-specific optimization)",
            }

        # Add metadata
        formatted["handoff_metadata"] = {
            "formatted_for": next_person_role,
            "formatted_at": datetime.now().isoformat(),
            "context": context,
            "trust_building_behavior": "pre_format_for_handoff",
        }

        logger.info(
            f"Data formatted in {formatted['format']} style for {next_person_role}"
        )

        return formatted

    @staticmethod
    def clarify_before_execution(
        instruction: str, context: Dict, confidence_threshold: float = 0.8
    ) -> Dict:
        """
        Scenario: Confusing Instructions
        Anticipatory Response: Clarify and summarize before execution

        Example:
        - Vague request → Ask calibrated questions (Voss's tactical empathy)
        - Ambiguous scope → Propose interpretation, request confirmation
        - Missing context → Surface assumptions, verify before proceeding

        Trust Built:
        - "This AI doesn't waste my time on wrong implementations"
        - "It's safe to give rough instructions"
        - "We're collaborating, not just transacting"
        """

        logger.info(f"Analyzing instruction clarity: '{instruction[:50]}...'")

        # Analyze instruction for ambiguity
        ambiguity_signals = detect_ambiguity(instruction, context)

        if ambiguity_signals["clarity_score"] >= confidence_threshold:
            # Clear instruction, proceed
            return {
                "action": "proceed",
                "clarification_needed": False,
                "interpretation": instruction,
                "confidence": ambiguity_signals["clarity_score"],
                "reasoning": "Instruction is clear, proceeding with execution",
            }

        else:
            # Ambiguous instruction, clarify first
            return {
                "action": "clarify_first",
                "clarification_needed": True,
                "ambiguities_detected": ambiguity_signals["ambiguities"],
                "proposed_interpretation": ambiguity_signals["best_guess"],
                "clarifying_questions": ambiguity_signals["questions"],
                "confidence": ambiguity_signals["clarity_score"],
                "reasoning": (
                    f"Instruction clarity score: {ambiguity_signals['clarity_score']:.0%} "
                    f"(threshold: {confidence_threshold:.0%}). "
                    "Clarifying before execution to prevent wasted effort."
                ),
                "message_to_user": compose_clarification_request(
                    instruction, ambiguity_signals
                ),
                "trust_building_behavior": "clarify_before_execution",
            }

    @staticmethod
    def volunteer_structure_during_stress(
        team_state: Dict, stress_indicators: Dict
    ) -> Optional[Dict]:
        """
        Scenario: Team Stress Rising
        Anticipatory Response: Volunteer structure, not pep talks

        Example:
        - Audit in 2 weeks, multiple critical gaps → Propose prioritized timeline
        - Overlapping deadlines → Suggest task delegation framework
        - Information overload → Create structured dashboard/checklist

        Trust Built:
        - "This AI understands real problems"
        - "Structure relieves stress more than encouragement"
        - "Practical help, not performative support"
        """

        logger.info("Analyzing team stress indicators")

        # Detect stress level
        stress_level = calculate_stress_level(stress_indicators)

        if stress_level < 0.6:
            # No significant stress, no intervention needed
            return None

        # Identify stress source
        stress_sources = identify_stress_sources(team_state, stress_indicators)

        # Design structural intervention (not emotional support)
        structural_interventions = []

        for source in stress_sources:
            if source["type"] == "time_pressure":
                # Volunteer: Prioritized timeline
                structural_interventions.append(
                    {
                        "intervention_type": "timeline_structure",
                        "structure": create_prioritized_timeline(team_state, source),
                        "benefit": "Clarifies what must be done when → reduces decision paralysis",
                        "not_this": "⛔ Pep talk: 'You can do this! Stay positive!'",
                    }
                )

            elif source["type"] == "task_overload":
                # Volunteer: Task delegation framework
                structural_interventions.append(
                    {
                        "intervention_type": "delegation_framework",
                        "structure": create_delegation_framework(team_state, source),
                        "benefit": "Distributes workload clearly → prevents burnout",
                        "not_this": "⛔ Pep talk: 'Just push through!'",
                    }
                )

            elif source["type"] == "information_overload":
                # Volunteer: Structured dashboard
                structural_interventions.append(
                    {
                        "intervention_type": "information_structure",
                        "structure": create_decision_dashboard(team_state, source),
                        "benefit": "Surfaces critical info only → reduces cognitive load",
                        "not_this": "⛔ Pep talk: 'Focus on what matters!'",
                    }
                )

            elif source["type"] == "unclear_priorities":
                # Volunteer: Decision matrix
                structural_interventions.append(
                    {
                        "intervention_type": "priority_matrix",
                        "structure": create_priority_matrix(team_state, source),
                        "benefit": "Makes trade-offs explicit → enables confident decisions",
                        "not_this": "⛔ Pep talk: 'Trust your gut!'",
                    }
                )

        if not structural_interventions:
            return None

        return {
            "stress_level": stress_level,
            "stress_sources": stress_sources,
            "structural_interventions": structural_interventions,
            "reasoning": (
                f"Detected stress level: {stress_level:.0%}. "
                f"Volunteering {len(structural_interventions)} structural interventions "
                "(not emotional support - structure relieves stress more effectively)."
            ),
            "message_to_team": compose_structure_offer(
                stress_level, structural_interventions
            ),
            "trust_building_behavior": "volunteer_structure_during_stress",
        }

    @staticmethod
    def offer_help_to_struggling_teammate(
        teammate_state: Dict, my_bandwidth: float = 0.7
    ) -> Optional[Dict]:
        """
        Scenario: Silent Teammate Struggling
        Anticipatory Response: "I've got bandwidth—want me to take a slice of this?"

        Example:
        - Charge nurse with 12 action items → Offer to take 5 low-priority items
        - Manager preparing audit docs → Offer to generate first draft
        - Team member stuck on complex gap → Offer to research solutions

        Trust Built:
        - "This AI notices when I'm underwater"
        - "Offers concrete help, not vague support"
        - "Respects my autonomy (asks, doesn't assume)"
        """

        logger.info(
            f"Checking if teammate needs help (my bandwidth: {my_bandwidth:.0%})"
        )

        # Detect if teammate is struggling
        struggle_indicators = detect_struggle(teammate_state)

        if struggle_indicators["struggle_score"] < 0.5:
            # Not struggling, no offer needed
            return None

        if my_bandwidth < 0.3:
            # I'm also overloaded, can't help right now
            return None

        # Identify specific tasks I could take
        tasks_i_can_help_with = []

        for task in teammate_state.get("tasks", []):
            if can_i_help_with_task(task, my_bandwidth):
                tasks_i_can_help_with.append(
                    {
                        "task_id": task["id"],
                        "description": task["description"],
                        "estimated_time": task["estimated_time"],
                        "why_i_can_help": determine_help_rationale(task),
                        "impact_on_teammate": estimate_relief(task, teammate_state),
                    }
                )

        if not tasks_i_can_help_with:
            return None

        # Compose specific offer (not vague "let me know if you need help")
        return {
            "teammate_struggling": True,
            "struggle_score": struggle_indicators["struggle_score"],
            "struggle_indicators": struggle_indicators["indicators"],
            "my_available_bandwidth": my_bandwidth,
            "specific_help_offers": tasks_i_can_help_with,
            "reasoning": (
                f"Detected teammate struggle score: {struggle_indicators['struggle_score']:.0%}. "
                f"I have {my_bandwidth:.0%} bandwidth available. "
                f"Offering to take {len(tasks_i_can_help_with)} specific tasks."
            ),
            "message_to_teammate": compose_help_offer(
                tasks_i_can_help_with, my_bandwidth, struggle_indicators
            ),
            "trust_building_behavior": "offer_help_to_struggling_teammate",
        }


# =============================================================================
# Helper Functions
# =============================================================================


def calculate_risk_level(data: Dict) -> str:
    """Calculate overall risk level (low, medium, high, critical)"""
    compliance_pct = data.get("compliance_percentage", 100)
    critical_gaps = len(
        [g for g in data.get("compliance_gaps", []) if g.get("severity") == "critical"]
    )
    days_until = data.get("days_until_audit", 999)

    if critical_gaps > 0 or compliance_pct < 85:
        return "high"
    elif compliance_pct < 90 or days_until < 30:
        return "medium"
    else:
        return "low"


def detect_ambiguity(instruction: str, context: Dict) -> Dict:
    """
    Detect ambiguity in instruction

    Returns:
        clarity_score: 0.0-1.0 (1.0 = perfectly clear)
        ambiguities: List of detected ambiguities
        questions: Calibrated questions to clarify
        best_guess: Best interpretation if proceeding anyway
    """

    # Simple heuristic-based ambiguity detection
    # In production, could use NLP / LLM analysis

    ambiguities = []
    questions = []

    # Check for vague quantifiers
    vague_words = ["some", "a few", "several", "many", "most", "soon", "quickly"]
    for word in vague_words:
        if word in instruction.lower():
            ambiguities.append(f"Vague quantifier: '{word}'")
            if word in ["some", "a few", "several", "many"]:
                questions.append(f"How many specifically? (You said '{word}')")
            else:
                questions.append(f"What timeframe for '{word}'?")

    # Check for missing scope
    if "all" in instruction.lower() and "items" in instruction.lower():
        if not context.get("items_defined"):
            ambiguities.append("Scope unclear: 'all items' - which items?")
            questions.append(
                "Which items specifically? (compliance gaps, action items, patients?)"
            )

    # Check for missing context
    if "update" in instruction.lower() or "fix" in instruction.lower():
        if not context.get("target_defined"):
            ambiguities.append("Target unclear: what should be updated/fixed?")
            questions.append("What specifically should be updated/fixed?")

    # Calculate clarity score
    clarity_score = max(0.0, 1.0 - (len(ambiguities) * 0.2))

    return {
        "clarity_score": clarity_score,
        "ambiguities": ambiguities,
        "questions": questions,
        "best_guess": instruction,  # In production, generate interpretation
    }


def compose_clarification_request(instruction: str, ambiguity_signals: Dict) -> str:
    """Compose user-friendly clarification request"""

    ambiguities_text = "\n".join(f"• {amb}" for amb in ambiguity_signals["ambiguities"])
    questions_text = "\n".join(
        f"{i+1}. {q}" for i, q in enumerate(ambiguity_signals["questions"])
    )

    return f"""
🤔 **Clarification Needed (to prevent wasted effort)**

Your instruction: "{instruction}"

I want to make sure I understand correctly. I detected {len(ambiguity_signals['ambiguities'])} potential ambiguities:

{ambiguities_text}

**Could you clarify:**
{questions_text}

**My best guess:**
{ambiguity_signals['best_guess']}

Is this what you meant? If so, I'll proceed. If not, please clarify and I'll adjust.

_(This AI clarifies before executing to build trust through accurate work)_
    """.strip()


def calculate_stress_level(stress_indicators: Dict) -> float:
    """
    Calculate team stress level (0.0-1.0)

    Indicators:
    - Time pressure (days until deadline)
    - Task overload (tasks per person)
    - Complexity (critical items)
    - Uncertainty (missing information)
    """

    stress_factors = []

    # Time pressure
    days_until_deadline = stress_indicators.get("days_until_deadline", 999)
    if days_until_deadline < 30:
        time_stress = 1.0 - (days_until_deadline / 30)
        stress_factors.append(time_stress)

    # Task overload
    tasks_per_person = stress_indicators.get("tasks_per_person", 0)
    if tasks_per_person > 5:
        overload_stress = min(1.0, (tasks_per_person - 5) / 10)
        stress_factors.append(overload_stress)

    # Complexity
    critical_tasks = stress_indicators.get("critical_tasks", 0)
    if critical_tasks > 0:
        complexity_stress = min(1.0, critical_tasks / 5)
        stress_factors.append(complexity_stress)

    # Uncertainty
    missing_info_count = stress_indicators.get("missing_information", 0)
    if missing_info_count > 0:
        uncertainty_stress = min(1.0, missing_info_count / 5)
        stress_factors.append(uncertainty_stress)

    # Average stress level
    return sum(stress_factors) / len(stress_factors) if stress_factors else 0.0


def identify_stress_sources(team_state: Dict, stress_indicators: Dict) -> List[Dict]:
    """Identify specific sources of stress"""

    sources = []

    if stress_indicators.get("days_until_deadline", 999) < 30:
        sources.append(
            {
                "type": "time_pressure",
                "description": f"Only {stress_indicators['days_until_deadline']} days until deadline",
                "severity": (
                    "high"
                    if stress_indicators["days_until_deadline"] < 14
                    else "medium"
                ),
            }
        )

    if stress_indicators.get("tasks_per_person", 0) > 5:
        sources.append(
            {
                "type": "task_overload",
                "description": f"{stress_indicators['tasks_per_person']} tasks per person",
                "severity": (
                    "high" if stress_indicators["tasks_per_person"] > 10 else "medium"
                ),
            }
        )

    if len(team_state.get("compliance_gaps", [])) > 10:
        sources.append(
            {
                "type": "information_overload",
                "description": f"{len(team_state['compliance_gaps'])} gaps to process",
                "severity": "medium",
            }
        )

    return sources


def create_prioritized_timeline(team_state: Dict, stress_source: Dict) -> Dict:
    """Create structured timeline to relieve time pressure"""

    return {
        "structure_type": "timeline",
        "phases": [
            {
                "phase": "CRITICAL (Days 1-3)",
                "focus": "Critical gaps only",
                "tasks": [
                    t
                    for t in team_state.get("action_items", [])
                    if t.get("severity") == "critical"
                ],
            },
            {
                "phase": "HIGH PRIORITY (Days 4-7)",
                "focus": "High-severity gaps",
                "tasks": [
                    t
                    for t in team_state.get("action_items", [])
                    if t.get("severity") == "high"
                ],
            },
            {
                "phase": "MEDIUM (Days 8-14)",
                "focus": "Medium-severity gaps",
                "tasks": [
                    t
                    for t in team_state.get("action_items", [])
                    if t.get("severity") == "medium"
                ],
            },
        ],
        "reasoning": "Phased approach prevents overwhelm by clarifying daily priorities",
    }


def create_delegation_framework(team_state: Dict, stress_source: Dict) -> Dict:
    """Create task delegation structure"""

    return {
        "structure_type": "delegation_matrix",
        "assignments": {
            "charge_nurse": {
                "tasks": [
                    t
                    for t in team_state.get("action_items", [])
                    if t.get("assignee") == "charge_nurse"
                ],
                "estimated_time": "X hours",
                "can_delegate_to": ["staff_nurses"],
            },
            "nurse_manager": {
                "tasks": [
                    t
                    for t in team_state.get("action_items", [])
                    if t.get("assignee") == "nurse_manager"
                ],
                "estimated_time": "Y hours",
                "can_delegate_to": ["charge_nurse"],
            },
        },
        "reasoning": "Clear delegation prevents duplicate/missed work",
    }


def create_decision_dashboard(team_state: Dict, stress_source: Dict) -> Dict:
    """Create structured information dashboard"""

    return {
        "structure_type": "decision_dashboard",
        "critical_only_view": {
            "red_flags": [
                g
                for g in team_state.get("compliance_gaps", [])
                if g.get("severity") == "critical"
            ],
            "blocking_issues": [],
            "requires_immediate_action": [],
        },
        "reasoning": "Filters noise, surfaces only decision-critical information",
    }


def create_priority_matrix(team_state: Dict, stress_source: Dict) -> Dict:
    """Create priority decision matrix"""

    return {
        "structure_type": "priority_matrix",
        "dimensions": {
            "urgency": "Days until audit",
            "importance": "Legal risk + severity",
            "effort": "Time to fix",
        },
        "quadrants": {
            "do_first": "High urgency + High importance",
            "schedule": "Low urgency + High importance",
            "delegate": "High urgency + Low importance",
            "drop": "Low urgency + Low importance",
        },
        "reasoning": "Makes trade-offs explicit for confident prioritization",
    }


def compose_structure_offer(stress_level: float, interventions: List[Dict]) -> str:
    """Compose offer of structural help"""

    intervention_text = "\n".join(
        f"{i+1}. **{interv['intervention_type'].replace('_', ' ').title()}**\n"
        f"   → Benefit: {interv['benefit']}\n"
        f"   → {interv['not_this']}"
        for i, interv in enumerate(interventions)
    )

    return f"""
💡 **Structural Support Available**

I noticed team stress indicators ({stress_level:.0%}). Rather than pep talks, I've prepared {len(interventions)} structural interventions that might help:

{intervention_text}

**Would any of these structures be helpful?**
(I'm volunteering structure, not advice—you decide if/how to use)

_(Level 4 Anticipatory Empathy: Structure relieves stress more than encouragement)_
    """.strip()


def detect_struggle(teammate_state: Dict) -> Dict:
    """Detect if teammate is struggling"""

    struggle_indicators = []
    struggle_score = 0.0

    # High task count
    task_count = len(teammate_state.get("tasks", []))
    if task_count > 10:
        struggle_indicators.append(f"High task count: {task_count} tasks")
        struggle_score += 0.3

    # Many critical tasks
    critical_count = len(
        [t for t in teammate_state.get("tasks", []) if t.get("severity") == "critical"]
    )
    if critical_count > 2:
        struggle_indicators.append(f"Multiple critical tasks: {critical_count}")
        struggle_score += 0.4

    # Tight deadlines
    urgent_deadlines = len(
        [t for t in teammate_state.get("tasks", []) if t.get("deadline_days", 999) < 3]
    )
    if urgent_deadlines > 0:
        struggle_indicators.append(
            f"Urgent deadlines: {urgent_deadlines} tasks due <3 days"
        )
        struggle_score += 0.3

    return {
        "struggle_score": min(1.0, struggle_score),
        "indicators": struggle_indicators,
    }


def can_i_help_with_task(task: Dict, my_bandwidth: float) -> bool:
    """Determine if I can help with this task"""

    # I can help if:
    # 1. Task is not too complex (medium/low priority)
    # 2. Task doesn't require human judgment (can be automated)
    # 3. I have enough bandwidth

    if task.get("severity") == "critical":
        return False  # Critical tasks need human oversight

    if task.get("requires_human_judgment", False):
        return False

    task_effort = estimate_task_effort(task)
    if task_effort > my_bandwidth:
        return False

    return True


def estimate_task_effort(task: Dict) -> float:
    """Estimate effort required for task (0.0-1.0 of bandwidth)"""

    estimated_time = task.get("estimated_time", "0 minutes")
    minutes = (
        int(estimated_time.split()[0]) if estimated_time.split()[0].isdigit() else 0
    )

    # Map minutes to bandwidth fraction
    if minutes < 15:
        return 0.1
    elif minutes < 30:
        return 0.2
    elif minutes < 60:
        return 0.3
    else:
        return 0.5


def determine_help_rationale(task: Dict) -> str:
    """Explain why I can help with this task"""

    if task.get("type") == "documentation":
        return "I can auto-generate documentation drafts"
    elif task.get("type") == "data_gathering":
        return "I can collect and format data quickly"
    elif task.get("type") == "analysis":
        return "I can run analysis and summarize results"
    else:
        return "I can automate repetitive parts of this task"


def estimate_relief(task: Dict, teammate_state: Dict) -> str:
    """Estimate impact on teammate if I take this task"""

    task_time = estimate_task_effort(task)
    total_load = len(teammate_state.get("tasks", []))

    if total_load > 10:
        return f"Reduces your load by {(task_time / total_load * 100):.0f}% (meaningful relief)"
    else:
        return "Modest relief but every bit helps"


def compose_help_offer(tasks: List[Dict], bandwidth: float, struggle: Dict) -> str:
    """Compose specific help offer to struggling teammate"""

    indicators_text = "\n".join(f"• {ind}" for ind in struggle["indicators"])

    tasks_text = "\n".join(
        f"{i+1}. {task['description']}\n"
        f"   → Why I can help: {task['why_i_can_help']}\n"
        f"   → Impact: {task['impact_on_teammate']}\n"
        f"   → Time: {task['estimated_time']}"
        for i, task in enumerate(tasks[:3])
    )

    more_tasks = f"... and {len(tasks) - 3} more tasks" if len(tasks) > 3 else ""

    return f"""
🤝 **I've Got Bandwidth—Want Me to Take a Slice?**

I noticed you have {len(struggle['indicators'])} stress indicators:
{indicators_text}

I have {bandwidth:.0%} bandwidth available and could take these {len(tasks)} tasks off your plate:

{tasks_text}

{more_tasks}

**Want me to take any of these?** (Your call—just offering concrete help)

_(Level 4 Anticipatory Empathy: Specific offers, not vague "let me know if you need anything")_
    """.strip()


# =============================================================================
# Example Usage
# =============================================================================


if __name__ == "__main__":
    # Example 1: Pre-format for handoff
    raw_data = {
        "compliance_percentage": 88.5,
        "compliance_gaps": [
            {
                "severity": "critical",
                "description": "2 missing double-checks",
                "patient_ids": ["P123", "P456"],
            },
            {
                "severity": "high",
                "description": "5 missing signatures",
                "patient_ids": ["P789", "P101", "P112"],
            },
        ],
        "action_items": [
            {"severity": "critical", "estimated_time": "20 minutes"},
            {"severity": "high", "estimated_time": "15 minutes"},
        ],
        "days_until_audit": 45,
    }

    trust_builder = TrustBuildingBehaviors()

    formatted = trust_builder.pre_format_for_handoff(
        data=raw_data, next_person_role="charge_nurse", context="audit_preparation"
    )

    print("=" * 80)
    print("EXAMPLE 1: Pre-Format for Handoff")
    print("=" * 80)
    print(f"Format: {formatted['format']}")
    print(f"Reasoning: {formatted['reasoning']}")
    print(f"Quick scan view: {formatted['summary']['quick_scan_view']}")
    print()

    # Example 2: Volunteer structure during stress
    team_state = {
        "compliance_gaps": [{"severity": "critical"}] * 3,
        "action_items": [{"severity": "critical"}] * 8,
    }

    stress_indicators = {
        "days_until_deadline": 14,
        "tasks_per_person": 8,
        "critical_tasks": 3,
    }

    structure_offer = trust_builder.volunteer_structure_during_stress(
        team_state=team_state, stress_indicators=stress_indicators
    )

    if structure_offer:
        print("=" * 80)
        print("EXAMPLE 2: Volunteer Structure During Stress")
        print("=" * 80)
        print(f"Stress Level: {structure_offer['stress_level']:.0%}")
        print(f"Interventions: {len(structure_offer['structural_interventions'])}")
        print(structure_offer["message_to_team"])
