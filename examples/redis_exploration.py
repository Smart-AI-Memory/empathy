#!/usr/bin/env python3
"""
Redis Short-Term Memory Exploration Script

Interactive demo of all Redis memory features for the Empathy Framework.
Run this to explore and gain confidence in the Redis implementation.

Usage:
    python examples/redis_exploration.py [--mock]

Options:
    --mock    Use in-memory mock instead of real Redis (for testing without Redis)

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import sys
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, "src")

from empathy_os import (
    AccessTier,
    AgentCredentials,
    RedisShortTermMemory,
    StagedPattern,
)


def print_header(title: str):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_step(step: str):
    """Print a step indicator"""
    print(f"\n>>> {step}")


def print_result(label: str, value):
    """Print a result"""
    print(f"    {label}: {value}")


def demo_connection(memory: RedisShortTermMemory):
    """Demo 1: Test connection and get stats"""
    print_header("1. CONNECTION & HEALTH CHECK")

    print_step("Checking Redis connection...")
    connected = memory.ping()
    print_result("Connected", connected)

    if not connected and not memory.use_mock:
        print("\n    ERROR: Cannot connect to Redis!")
        print("    Make sure Redis is running:")
        print("      docker run -d --name empathy-redis -p 6379:6379 redis:alpine")
        return False

    print_step("Getting memory statistics...")
    stats = memory.get_stats()
    for key, value in stats.items():
        print_result(key, value)

    return True


def demo_working_memory(memory: RedisShortTermMemory):
    """Demo 2: Stash and retrieve working memory"""
    print_header("2. WORKING MEMORY (Stash/Retrieve)")

    # Create agent credentials
    print_step("Creating agent with CONTRIBUTOR access...")
    analyst = AgentCredentials(
        agent_id="code_analyst",
        tier=AccessTier.CONTRIBUTOR,
        roles=["analysis", "review"],
    )
    print_result("Agent ID", analyst.agent_id)
    print_result("Access Tier", analyst.tier.name)
    print_result("Can stage patterns", analyst.can_stage())

    # Stash some analysis results
    print_step("Stashing analysis results...")
    analysis_data = {
        "files_analyzed": 127,
        "issues_found": 5,
        "critical": 1,
        "warnings": 4,
        "timestamp": datetime.now().isoformat(),
    }
    memory.stash("analysis_v1", analysis_data, analyst)
    print_result("Stashed key", "analysis_v1")
    print_result("Data", analysis_data)

    # Retrieve it back
    print_step("Retrieving stashed data...")
    retrieved = memory.retrieve("analysis_v1", analyst)
    print_result("Retrieved", retrieved)

    # Show that observers can't write
    print_step("Testing permission denial (Observer trying to write)...")
    observer = AgentCredentials("observer_bot", AccessTier.OBSERVER)
    try:
        memory.stash("forbidden", {"test": 1}, observer)
        print_result("Result", "ERROR - should have been denied!")
    except PermissionError as e:
        print_result("Correctly denied", str(e)[:60] + "...")

    # Clear working memory
    print_step("Clearing working memory...")
    cleared = memory.clear_working_memory(analyst)
    print_result("Keys cleared", cleared)


def demo_pattern_staging(memory: RedisShortTermMemory):
    """Demo 3: Pattern staging workflow"""
    print_header("3. PATTERN STAGING WORKFLOW")

    # Create contributor and validator
    contributor = AgentCredentials("pattern_discoverer", AccessTier.CONTRIBUTOR)
    validator = AgentCredentials("senior_reviewer", AccessTier.VALIDATOR)

    # Stage a new pattern
    print_step("Contributor discovers and stages a pattern...")
    pattern = StagedPattern(
        pattern_id="pat_error_boundary",
        agent_id=contributor.agent_id,
        pattern_type="error_handling",
        name="React Error Boundary Pattern",
        description="Wrap components in error boundaries to prevent cascade failures",
        code="""
class ErrorBoundary extends React.Component {
    state = { hasError: false };
    static getDerivedStateFromError(error) {
        return { hasError: true };
    }
    render() {
        if (this.state.hasError) return <FallbackUI />;
        return this.props.children;
    }
}
        """.strip(),
        confidence=0.85,
        interests=["reliability", "user_experience", "graceful_degradation"],
    )
    memory.stage_pattern(pattern, contributor)
    print_result("Pattern staged", pattern.pattern_id)
    print_result("Confidence", pattern.confidence)
    print_result("Interests", pattern.interests)

    # List staged patterns
    print_step("Listing all staged patterns...")
    staged = memory.list_staged_patterns(validator)
    print_result("Staged patterns count", len(staged))
    for p in staged:
        print_result(f"  - {p.pattern_id}", p.name)

    # Validator promotes the pattern
    print_step("Validator reviews and promotes pattern...")
    promoted = memory.promote_pattern("pat_error_boundary", validator)
    if promoted:
        print_result("Promoted", promoted.name)
        print_result("Ready for PatternLibrary", "Yes")
    else:
        print_result("Promoted", "Pattern not found")

    # Show staging is now empty
    print_step("Checking staging area...")
    remaining = memory.list_staged_patterns(validator)
    print_result("Remaining staged", len(remaining))


def demo_conflict_resolution(memory: RedisShortTermMemory):
    """Demo 4: Principled negotiation for conflict resolution"""
    print_header("4. CONFLICT RESOLUTION (Principled Negotiation)")

    contributor = AgentCredentials("mediator", AccessTier.CONTRIBUTOR)
    validator = AgentCredentials("arbiter", AccessTier.VALIDATOR)

    # Create a realistic conflict
    print_step("Creating conflict context...")
    print("\n    CONFLICT: Security Agent vs Performance Agent")
    print("    Topic: Input validation strategy")

    context = memory.create_conflict_context(
        conflict_id="validation_strategy",
        positions={
            "security_agent": "Validate ALL inputs with full schema checks",
            "perf_agent": "Skip validation for internal service calls",
        },
        interests={
            "security_agent": [
                "data_integrity",
                "attack_prevention",
                "compliance",
                "audit_trail",
            ],
            "perf_agent": [
                "low_latency",
                "high_throughput",
                "resource_efficiency",
                "user_experience",
            ],
        },
        credentials=contributor,
        batna="security_wins",  # Default if no synthesis found
    )

    print_result("Conflict ID", context.conflict_id)
    print_result("BATNA (fallback)", context.batna)

    print_step("Analyzing positions vs interests...")
    print("\n    Security Agent:")
    print(f"      Position: {context.positions['security_agent']}")
    print(f"      Interests: {context.interests['security_agent']}")
    print("\n    Performance Agent:")
    print(f"      Position: {context.positions['perf_agent']}")
    print(f"      Interests: {context.interests['perf_agent']}")

    print_step("Finding shared interests...")
    shared = ["system_reliability", "maintainability"]
    print_result("Shared interests identified", shared)

    print_step("Validator proposes synthesis...")
    synthesis = (
        "SYNTHESIS: Implement tiered validation strategy.\n"
        "  1. Full validation at system boundaries (external APIs, user input)\n"
        "  2. Schema-only validation for internal service calls\n"
        "  3. Skip validation for same-service internal methods\n"
        "\n"
        "This satisfies:\n"
        "  - Security: Boundary protection, compliance at entry points\n"
        "  - Performance: Fast internal calls, reduced overhead\n"
        "  - Shared: Reliable system with clear trust boundaries"
    )
    print(f"\n{synthesis}")

    memory.resolve_conflict(
        "validation_strategy",
        resolution=synthesis,
        credentials=validator,
    )

    # Verify resolution
    print_step("Verifying resolution stored...")
    resolved = memory.get_conflict_context("validation_strategy", contributor)
    print_result("Resolved", resolved.resolved)
    print_result("Resolution stored", "Yes" if resolved.resolution else "No")


def demo_coordination_signals(memory: RedisShortTermMemory):
    """Demo 5: Multi-agent coordination via signals"""
    print_header("5. MULTI-AGENT COORDINATION")

    # Create multiple agents
    analyzer = AgentCredentials("code_analyzer", AccessTier.CONTRIBUTOR)
    reviewer = AgentCredentials("code_reviewer", AccessTier.CONTRIBUTOR)
    integrator = AgentCredentials("integrator", AccessTier.CONTRIBUTOR)

    print_step("Simulating multi-agent workflow...")
    print("\n    Workflow: Analyzer -> Reviewer -> Integrator")

    # Analyzer completes work and signals
    print_step("Analyzer completes analysis and signals reviewer...")
    memory.stash(
        "pr_analysis",
        {
            "pr_number": 1234,
            "files_changed": 15,
            "complexity_score": 7.2,
            "risk_level": "medium",
        },
        analyzer,
    )
    memory.send_signal(
        signal_type="analysis_complete",
        data={"pr": 1234, "output_key": "pr_analysis"},
        credentials=analyzer,
        target_agent="code_reviewer",
    )
    print_result("Signal sent", "analysis_complete -> code_reviewer")

    # Reviewer receives signal
    print_step("Reviewer checking for signals...")
    signals = memory.receive_signals(reviewer, signal_type="analysis_complete")
    print_result("Signals received", len(signals))
    if signals:
        signal = signals[0]
        print_result("From", signal["from_agent"])
        print_result("Data", signal["data"])

    # Reviewer gets analyzer's results
    print_step("Reviewer retrieving analyzer's results...")
    results = memory.retrieve("pr_analysis", reviewer, agent_id="code_analyzer")
    print_result("Retrieved analysis", results)

    # Broadcast signal
    print_step("Integrator broadcasts completion to all agents...")
    memory.send_signal(
        signal_type="integration_complete",
        data={"status": "merged", "branch": "main"},
        credentials=integrator,
        target_agent=None,  # Broadcast
    )
    print_result("Broadcast sent", "integration_complete -> all")


def demo_session_management(memory: RedisShortTermMemory):
    """Demo 6: Collaboration sessions"""
    print_header("6. SESSION MANAGEMENT")

    lead = AgentCredentials("tech_lead", AccessTier.CONTRIBUTOR)
    dev1 = AgentCredentials("developer_1", AccessTier.CONTRIBUTOR)
    dev2 = AgentCredentials("developer_2", AccessTier.CONTRIBUTOR)

    # Create session
    print_step("Tech lead creates collaboration session...")
    memory.create_session(
        session_id="sprint_42_review",
        credentials=lead,
        metadata={
            "purpose": "Sprint 42 code review",
            "deadline": "2025-12-15",
            "focus_areas": ["performance", "security"],
        },
    )
    print_result("Session created", "sprint_42_review")

    # Others join
    print_step("Developers joining session...")
    memory.join_session("sprint_42_review", dev1)
    print_result("developer_1 joined", "Yes")
    memory.join_session("sprint_42_review", dev2)
    print_result("developer_2 joined", "Yes")

    # Check session state
    print_step("Checking session participants...")
    session = memory.get_session("sprint_42_review", lead)
    print_result("Participants", session["participants"])
    print_result("Metadata", session["metadata"])


def demo_permission_tiers(memory: RedisShortTermMemory):
    """Demo 7: Role-based access control"""
    print_header("7. ROLE-BASED ACCESS TIERS")

    tiers = [
        ("OBSERVER", AccessTier.OBSERVER),
        ("CONTRIBUTOR", AccessTier.CONTRIBUTOR),
        ("VALIDATOR", AccessTier.VALIDATOR),
        ("STEWARD", AccessTier.STEWARD),
    ]

    print_step("Permission matrix for each tier...")
    print("\n    Tier          | Read | Stage | Validate | Admin")
    print("    " + "-" * 50)

    for name, tier in tiers:
        creds = AgentCredentials(f"agent_{name.lower()}", tier)
        read = "Yes" if creds.can_read() else " - "
        stage = "Yes" if creds.can_stage() else " - "
        validate = "Yes" if creds.can_validate() else " - "
        admin = "Yes" if creds.can_administer() else " - "
        print(f"    {name:13} |  {read} |  {stage}  |    {validate}   |  {admin}")


def run_all_demos(use_mock: bool = False):
    """Run all demonstration scenarios"""
    print("\n" + "#" * 60)
    print("#  EMPATHY REDIS SHORT-TERM MEMORY EXPLORATION")
    print("#" * 60)

    if use_mock:
        print("\n  Mode: MOCK (in-memory, no Redis required)")
    else:
        print("\n  Mode: REDIS (connecting to localhost:6379)")

    # Initialize memory
    memory = RedisShortTermMemory(use_mock=use_mock)

    # Run demos
    if not demo_connection(memory):
        if not use_mock:
            print("\n  TIP: Run with --mock flag to use in-memory mode")
            return

    demo_working_memory(memory)
    demo_pattern_staging(memory)
    demo_conflict_resolution(memory)
    demo_coordination_signals(memory)
    demo_session_management(memory)
    demo_permission_tiers(memory)

    # Final stats
    print_header("FINAL STATISTICS")
    stats = memory.get_stats()
    for key, value in stats.items():
        print_result(key, value)

    print("\n" + "=" * 60)
    print("  EXPLORATION COMPLETE")
    print("=" * 60)
    print("\n  All Redis short-term memory features demonstrated!")
    print("  Ready for production use.\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Explore Redis Short-Term Memory features")
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use in-memory mock instead of real Redis",
    )
    args = parser.parse_args()

    run_all_demos(use_mock=args.mock)
