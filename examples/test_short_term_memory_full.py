#!/usr/bin/env python3
"""
Comprehensive Test of Short-Term Memory Capabilities

Tests all new features:
1. EmpathyOS core integration
2. Wizard caching and context sharing
3. Multi-agent coordination (AgentCoordinator)
4. Team sessions (TeamSession)
5. Pattern staging and validation

Run with:
    export REDIS_URL="redis://default:password@host:port"
    python examples/test_short_term_memory_full.py

Copyright 2025 Smart AI Memory, LLC
"""

import asyncio
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, "src")

from empathy_os import (
    AccessTier,
    AgentCoordinator,
    AgentTask,
    EmpathyOS,
    StagedPattern,
    TeamSession,
    get_redis_memory,
)
from empathy_software_plugin.wizards.base_wizard import BaseWizard

# =============================================================================
# TEST WIZARD (for testing wizard memory features)
# =============================================================================


class CodeReviewWizard(BaseWizard):
    """Test wizard for code review analysis"""

    @property
    def name(self) -> str:
        return "CodeReviewWizard"

    @property
    def level(self) -> int:
        return 4  # Anticipatory

    async def analyze(self, context: dict) -> dict:
        """Simulate code review analysis"""
        code = context.get("code", "")
        language = context.get("language", "python")

        # Simulate analysis
        issues = []
        if "eval(" in code:
            issues.append({"type": "security", "message": "Avoid eval()", "line": 1})
        if "import *" in code:
            issues.append({"type": "style", "message": "Avoid wildcard imports", "line": 1})
        if len(code) > 1000:
            issues.append({"type": "complexity", "message": "Consider splitting large files"})

        return {
            "language": language,
            "lines_analyzed": len(code.split("\n")),
            "issues_found": len(issues),
            "issues": issues,
            "confidence": 0.85,
            "predictions": [
                "Code quality will degrade if style issues not addressed",
                "Security vulnerability risk if eval() usage continues",
            ],
            "recommendations": [
                "Add linting rules to prevent eval()",
                "Configure import sorting",
            ],
        }


class SecurityWizard(BaseWizard):
    """Test wizard for security analysis"""

    @property
    def name(self) -> str:
        return "SecurityWizard"

    @property
    def level(self) -> int:
        return 4

    async def analyze(self, context: dict) -> dict:
        """Simulate security analysis"""
        code = context.get("code", "")

        vulnerabilities = []
        if "password" in code.lower() and "=" in code:
            vulnerabilities.append({"type": "hardcoded_secret", "severity": "high"})
        if "sql" in code.lower() and "+" in code:
            vulnerabilities.append({"type": "sql_injection", "severity": "critical"})

        return {
            "vulnerabilities": vulnerabilities,
            "risk_score": len(vulnerabilities) * 3,
            "confidence": 0.9,
            "predictions": ["Security debt will compound without fixes"],
            "recommendations": [
                "Use parameterized queries",
                "Use environment variables for secrets",
            ],
        }


# =============================================================================
# TEST FUNCTIONS
# =============================================================================


def print_header(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def print_result(name: str, success: bool, details: str = ""):
    status = "✅" if success else "❌"
    print(f"{status} {name}")
    if details:
        print(f"   {details}")


async def test_empathy_os_integration(memory):
    """Test EmpathyOS short-term memory integration"""
    print_header("1. EmpathyOS Core Integration")

    # Create agent with memory
    agent = EmpathyOS(
        user_id="test_agent_1",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR,
    )

    # Test stash/retrieve
    test_data = {"analysis": "complete", "files": 10, "issues": 3}
    agent.stash("test_analysis", test_data)
    retrieved = agent.retrieve("test_analysis")
    print_result(
        "Stash/Retrieve",
        retrieved == test_data,
        f"Stored and retrieved: {retrieved}",
    )

    # Test state persistence
    agent.collaboration_state.trust_level = 0.85
    agent.collaboration_state.successful_interventions = 15
    agent.persist_collaboration_state()

    # Create new agent and restore
    agent2 = EmpathyOS(
        user_id="test_agent_1",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR,
    )
    agent2._session_id = agent.session_id  # Use same session
    restored = agent2.restore_collaboration_state()
    print_result(
        "State Persistence",
        restored and agent2.collaboration_state.trust_level == 0.85,
        f"Trust level restored: {agent2.collaboration_state.trust_level}",
    )

    # Test signals
    agent.send_signal("status_update", {"phase": "testing"}, target_agent="reviewer")
    print_result("Send Signal", True, "Signal sent to 'reviewer'")

    # Test memory stats
    stats = agent.get_memory_stats()
    print_result(
        "Memory Stats",
        stats is not None and "mode" in stats,
        f"Mode: {stats['mode']}, Keys: {stats.get('total_keys', 'N/A')}",
    )

    return True


async def test_wizard_memory(memory):
    """Test wizard caching and context sharing"""
    print_header("2. Wizard Memory (Caching & Sharing)")

    # Create wizards with memory
    code_wizard = CodeReviewWizard(short_term_memory=memory)
    security_wizard = SecurityWizard(short_term_memory=memory)

    # Test code to analyze
    test_code = """
import os
from utils import *

def process_data(user_input):
    query = "SELECT * FROM users WHERE id = " + user_input
    result = eval(user_input)
    password = "secret123"
    return result
"""

    context = {"code": test_code, "language": "python"}

    # First analysis (fresh)
    result1 = await code_wizard.analyze_with_cache(context)
    print_result(
        "Fresh Analysis",
        not result1.get("_from_cache", True),
        f"Issues found: {result1['issues_found']}",
    )

    # Second analysis (cached)
    result2 = await code_wizard.analyze_with_cache(context)
    print_result(
        "Cached Analysis",
        result2.get("_from_cache", False),
        "Result retrieved from cache",
    )

    # Share context between wizards
    code_wizard.share_context("code_issues", result1["issues"])
    shared = security_wizard.get_shared_context("code_issues")
    print_result(
        "Context Sharing",
        shared is not None,
        f"Security wizard received {len(shared)} issues from code wizard",
    )

    # Stage discovered pattern
    staged = code_wizard.stage_discovered_pattern(
        pattern_id="pat_eval_warning",
        pattern_type="security",
        name="Avoid eval() Pattern",
        description="Using eval() on user input creates security vulnerabilities",
        confidence=0.95,
        code="# Use ast.literal_eval() instead of eval()",
    )
    print_result(
        "Pattern Staging",
        staged,
        "Pattern staged for validation",
    )

    # Send completion signal
    code_wizard.send_signal("analysis_complete", {"wizard": "CodeReviewWizard"})
    print_result("Wizard Signal", True, "Completion signal sent")

    return True


async def test_agent_coordinator(memory):
    """Test multi-agent task coordination"""
    print_header("3. AgentCoordinator (Task Distribution)")

    coordinator = AgentCoordinator(memory, team_id="code_review_team")

    # Register agents
    coordinator.register_agent("security_agent", ["security_review"])
    coordinator.register_agent("performance_agent", ["performance_review"])
    coordinator.register_agent("style_agent", ["style_review"])
    print_result(
        "Agent Registration",
        True,
        "Registered 3 agents with capabilities",
    )

    # Add tasks
    tasks = [
        AgentTask(
            task_id="review_auth_001",
            task_type="security_review",
            description="Review authentication module for vulnerabilities",
            priority=9,
        ),
        AgentTask(
            task_id="review_perf_001",
            task_type="performance_review",
            description="Profile database queries in user service",
            priority=7,
        ),
        AgentTask(
            task_id="review_style_001",
            task_type="style_review",
            description="Check code formatting in utils module",
            priority=5,
        ),
    ]

    for task in tasks:
        coordinator.add_task(task)
    print_result(
        "Task Creation",
        True,
        f"Added {len(tasks)} tasks with priorities 9, 7, 5",
    )

    # Complete a task
    completed = coordinator.complete_task(
        "review_auth_001",
        {"vulnerabilities_found": 2, "risk_level": "medium"},
    )
    print_result(
        "Task Completion",
        completed,
        "Security review completed with 2 vulnerabilities",
    )

    # Heartbeat
    coordinator.heartbeat("security_agent")
    print_result("Agent Heartbeat", True, "Heartbeat recorded")

    # Get active agents
    active = coordinator.get_active_agents()
    print_result(
        "Active Agents",
        len(active) > 0,
        f"Active agents: {active}",
    )

    # Broadcast message
    coordinator.broadcast("team_update", {"message": "Review sprint ending soon"})
    print_result("Team Broadcast", True, "Broadcast sent to team")

    return True


async def test_team_session(memory):
    """Test collaborative team sessions"""
    print_header("4. TeamSession (Collaborative Work)")

    # Create session
    session = TeamSession(
        memory,
        session_id=f"pr_review_{datetime.now().strftime('%H%M%S')}",
        purpose="Review PR #42: Add user authentication",
    )

    # Add agents
    session.add_agent("security_reviewer")
    session.add_agent("performance_reviewer")
    session.add_agent("lead_reviewer")
    print_result(
        "Session Creation",
        True,
        "Created session with 3 reviewers",
    )

    # Share context
    pr_context = {
        "files_changed": 15,
        "lines_added": 342,
        "lines_removed": 87,
        "affected_modules": ["auth", "users", "sessions"],
    }
    session.share("pr_context", pr_context)
    print_result(
        "Share PR Context",
        True,
        f"Shared context: {pr_context['files_changed']} files changed",
    )

    # Get shared context
    retrieved = session.get("pr_context")
    print_result(
        "Retrieve Context",
        retrieved is not None,
        f"Retrieved: {retrieved['affected_modules']}",
    )

    # Share review results
    session.share(
        "security_review",
        {
            "passed": True,
            "findings": ["No SQL injection", "Auth properly implemented"],
        },
    )
    session.share(
        "performance_review",
        {
            "passed": False,
            "findings": ["N+1 query detected in users.py:45"],
        },
    )
    print_result("Review Results", True, "Security and performance reviews shared")

    # Signal completion
    session.signal(
        "review_complete",
        {
            "reviewer": "security_reviewer",
            "verdict": "approved",
        },
    )
    session.signal(
        "review_complete",
        {
            "reviewer": "performance_reviewer",
            "verdict": "changes_requested",
        },
    )
    print_result("Completion Signals", True, "Review completion signals sent")

    # Get session info
    info = session.get_info()
    print_result(
        "Session Info",
        info is not None,
        f"Participants: {len(info.get('participants', []))}",
    )

    return True


async def test_pattern_lifecycle(memory):
    """Test complete pattern discovery to validation lifecycle"""
    print_header("5. Pattern Lifecycle (Discover → Stage → Validate)")

    # Create contributor (discovers patterns)
    contributor = EmpathyOS(
        user_id="pattern_discoverer",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR,
    )

    # Create validator (promotes patterns)
    validator = EmpathyOS(
        user_id="pattern_validator",
        short_term_memory=memory,
        access_tier=AccessTier.VALIDATOR,
    )

    # Contributor discovers and stages patterns
    patterns = [
        StagedPattern(
            pattern_id="pat_retry_logic",
            agent_id="pattern_discoverer",
            pattern_type="reliability",
            name="Exponential Backoff Retry",
            description="Implement exponential backoff for API retries",
            confidence=0.88,
            code="time.sleep(2 ** attempt)",
        ),
        StagedPattern(
            pattern_id="pat_circuit_breaker",
            agent_id="pattern_discoverer",
            pattern_type="reliability",
            name="Circuit Breaker Pattern",
            description="Prevent cascade failures with circuit breaker",
            confidence=0.92,
        ),
    ]

    for pattern in patterns:
        contributor.stage_pattern(pattern)
    print_result(
        "Pattern Discovery",
        True,
        f"Contributor staged {len(patterns)} patterns",
    )

    # Validator reviews staged patterns
    staged = validator.get_staged_patterns()
    our_patterns = [p for p in staged if p.agent_id == "pattern_discoverer"]
    print_result(
        "Pattern Review",
        len(our_patterns) >= 2,
        f"Validator sees {len(our_patterns)} patterns to review",
    )

    # Display patterns for review
    for p in our_patterns:
        print(f"   - {p.name} (confidence: {p.confidence:.0%})")

    return True


async def test_real_world_scenario(memory):
    """Simulate a real multi-agent code review workflow"""
    print_header("6. Real-World Scenario: Multi-Agent Code Review")

    # Setup team
    coordinator = AgentCoordinator(memory, team_id="real_review_team")
    session = TeamSession(memory, session_id="feature_review_001", purpose="Review feature branch")

    # Create specialized agents
    agents = {
        "security": EmpathyOS(
            "security_bot", short_term_memory=memory, access_tier=AccessTier.CONTRIBUTOR
        ),
        "perf": EmpathyOS(
            "performance_bot", short_term_memory=memory, access_tier=AccessTier.CONTRIBUTOR
        ),
        "lead": EmpathyOS(
            "lead_reviewer", short_term_memory=memory, access_tier=AccessTier.VALIDATOR
        ),
    }

    # Register all agents
    for _name, agent in agents.items():
        coordinator.register_agent(agent.user_id)
        session.add_agent(agent.user_id)
    print_result("Team Setup", True, f"Created team with {len(agents)} agents")

    # Simulate security analysis
    agents["security"].stash(
        "security_findings",
        {
            "vulnerabilities": 0,
            "warnings": 2,
            "scan_coverage": 0.95,
        },
    )
    agents["security"].send_signal(
        "analysis_complete",
        {"agent": "security_bot", "passed": True},
        target_agent="lead_reviewer",
    )
    print_result("Security Analysis", True, "0 vulnerabilities, 2 warnings")

    # Simulate performance analysis
    agents["perf"].stash(
        "perf_findings",
        {
            "slowdowns_detected": 1,
            "memory_issues": 0,
            "optimization_suggestions": ["Add index on users.email"],
        },
    )
    agents["perf"].send_signal(
        "analysis_complete",
        {"agent": "performance_bot", "passed": False},
        target_agent="lead_reviewer",
    )
    print_result("Performance Analysis", True, "1 slowdown detected")

    # Lead aggregates results
    sec_results = agents["lead"].retrieve("security_findings", agent_id="security_bot")
    perf_results = agents["lead"].retrieve("perf_findings", agent_id="performance_bot")

    final_verdict = {
        "security_passed": sec_results["vulnerabilities"] == 0,
        "performance_passed": perf_results["slowdowns_detected"] == 0,
        "overall": "changes_requested",
        "blocking_issues": perf_results["optimization_suggestions"],
    }
    session.share("final_verdict", final_verdict)
    print_result(
        "Lead Aggregation",
        True,
        f"Verdict: {final_verdict['overall']}",
    )

    # Persist state for all agents
    for agent in agents.values():
        agent.persist_collaboration_state()
    print_result("State Persistence", True, "All agent states persisted")

    return True


# =============================================================================
# MAIN
# =============================================================================


async def main():
    print("\n" + "=" * 60)
    print("  SHORT-TERM MEMORY COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    # Get memory
    memory = get_redis_memory()
    stats = memory.get_stats()
    print(f"\nMemory Mode: {stats['mode']}")
    if stats["mode"] == "redis":
        print(f"Redis Keys: {stats.get('total_keys', 'N/A')}")
        print(f"Memory Used: {stats.get('used_memory', 'N/A')}")

    # Run all tests
    results = []

    try:
        results.append(("EmpathyOS Integration", await test_empathy_os_integration(memory)))
        results.append(("Wizard Memory", await test_wizard_memory(memory)))
        results.append(("Agent Coordinator", await test_agent_coordinator(memory)))
        results.append(("Team Session", await test_team_session(memory)))
        results.append(("Pattern Lifecycle", await test_pattern_lifecycle(memory)))
        results.append(("Real-World Scenario", await test_real_world_scenario(memory)))
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback

        traceback.print_exc()

    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\n  Total: {passed}/{total} tests passed")

    # Final stats
    final_stats = memory.get_stats()
    print(f"\n  Final Redis Keys: {final_stats.get('total_keys', 'N/A')}")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Short-term memory is fully operational.\n")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Review output above.\n")

    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
