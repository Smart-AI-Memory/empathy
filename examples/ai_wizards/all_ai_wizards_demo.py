#!/usr/bin/env python
"""
Complete AI/Software Wizards Demo - Level 4 Anticipatory Intelligence

Demonstrates all 12+ AI-focused software development wizards:
- Multi-Model Coordination
- Performance Profiling
- AI Collaboration
- Advanced Debugging
- Agent Orchestration
- RAG Pattern Design
- Testing & Enhanced Testing
- AI Documentation
- Prompt Engineering
- AI Context Management
- Security Analysis

Each wizard provides Level 4 (Anticipatory) empathy:
- Predicts issues before they compound
- Learns from experience and shares patterns
- Identifies non-obvious problems (performance, cost, complexity)
- Provides actionable recommendations

Usage:
    python examples/ai_wizards/all_ai_wizards_demo.py
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from empathy_software_plugin.wizards.advanced_debugging_wizard import (
    AdvancedDebuggingWizard,
)
from empathy_software_plugin.wizards.agent_orchestration_wizard import (
    AgentOrchestrationWizard,
)
from empathy_software_plugin.wizards.ai_collaboration_wizard import (
    AICollaborationWizard,
)
from empathy_software_plugin.wizards.ai_context_wizard import AIContextWizard
from empathy_software_plugin.wizards.ai_documentation_wizard import (
    AIDocumentationWizard,
)
from empathy_software_plugin.wizards.enhanced_testing_wizard import (
    EnhancedTestingWizard,
)
from empathy_software_plugin.wizards.multi_model_wizard import MultiModelWizard
from empathy_software_plugin.wizards.performance_profiling_wizard import (
    PerformanceProfilingWizard,
)
from empathy_software_plugin.wizards.prompt_engineering_wizard import (
    PromptEngineeringWizard,
)
from empathy_software_plugin.wizards.rag_pattern_wizard import RAGPatternWizard
from empathy_software_plugin.wizards.security_analysis_wizard import (
    SecurityAnalysisWizard,
)
from empathy_software_plugin.wizards.testing_wizard import TestingWizard


def print_section(title: str, subtitle: str = ""):
    """Print formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"{title:^80}")
    if subtitle:
        print(f"{subtitle:^80}")
    print(f"{'=' * 80}\n")


def print_wizard_result(result: dict, wizard_name: str):
    """Print wizard analysis results"""
    print(f"🧙 Wizard: {wizard_name}")
    print(f"❤️  Empathy Level: {result.get('metadata', {}).get('empathy_level', 4)}")
    print(f"📊 Confidence: {result.get('confidence', 0):.0%}\n")

    # Issues
    issues = result.get("issues", [])
    if issues:
        print(f"⚠️  Issues Detected ({len(issues)}):")
        for issue in issues[:3]:
            severity = issue.get("severity", "info").upper()
            issue_type = issue.get("type", "unknown")
            description = issue.get("description", "No description")
            print(f"   [{severity}] {issue_type}: {description}")
        if len(issues) > 3:
            print(f"   ... and {len(issues) - 3} more")
        print()

    # Predictions (Level 4 Anticipatory)
    predictions = result.get("predictions", [])
    if predictions:
        print("🔮 Predictions (30-90 days):")
        for pred in predictions[:3]:
            likelihood = pred.get("likelihood", 0)
            impact = pred.get("impact", "unknown")
            description = pred.get("description", "No description")
            print(f"   [{likelihood:.0%} likely] {impact.upper()}: {description}")
        if len(predictions) > 3:
            print(f"   ... and {len(predictions) - 3} more")
        print()

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        print("💡 Recommendations:")
        for rec in recommendations[:3]:
            priority = rec.get("priority", "medium").upper()
            action = rec.get("action", "No action")
            print(f"   [{priority}] {action}")
        if len(recommendations) > 3:
            print(f"   ... and {len(recommendations) - 3} more")
        print()


async def demo_1_multi_model():
    """Demo 1: Multi-Model Coordination Wizard"""
    print_section("1. MULTI-MODEL COORDINATION", "Level 4 - Predict coordination issues")

    wizard = MultiModelWizard()

    context = {
        "model_usage": [
            {"model": "gpt-4", "tasks": ["complex_analysis", "code_review"]},
            {"model": "gpt-3.5-turbo", "tasks": ["simple_queries", "formatting"]},
            {"model": "claude-3-opus", "tasks": ["long_documents", "research"]},
            {"model": "claude-3-sonnet", "tasks": ["coding", "refactoring"]},
        ],
        "model_count": 4,
        "routing_logic": ["manual_selection", "task_based", "no_fallback"],
        "project_path": "/project",
    }

    print("📝 Scenario: Project using 4 different AI models")
    print("   • GPT-4 for complex analysis")
    print("   • GPT-3.5 for simple queries")
    print("   • Claude Opus for long documents")
    print("   • Claude Sonnet for coding\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_2_performance_profiling():
    """Demo 2: Performance Profiling Wizard"""
    print_section("2. PERFORMANCE PROFILING", "Level 4 - Predict performance degradation")

    wizard = PerformanceProfilingWizard()

    context = {
        "project_path": "/project",
        "framework": "fastapi",
        "recent_changes": ["added_ml_inference", "increased_db_queries"],
        "current_metrics": {
            "avg_response_time": 850,  # ms
            "p95_response_time": 2100,
            "requests_per_second": 45,
        },
        "baseline_metrics": {
            "avg_response_time": 120,
            "p95_response_time": 250,
            "requests_per_second": 200,
        },
    }

    print("📝 Scenario: API response times degraded")
    print("   • Average: 120ms → 850ms (7x slower)")
    print("   • P95: 250ms → 2100ms (8x slower)")
    print("   • Throughput: 200 → 45 RPS (78% drop)\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_3_ai_collaboration():
    """Demo 3: AI Collaboration Wizard"""
    print_section("3. AI COLLABORATION", "Level 4 - Predict multi-agent issues")

    wizard = AICollaborationWizard()

    context = {
        "agents": [
            {"name": "CodeReviewer", "role": "review", "dependencies": []},
            {"name": "TestGenerator", "role": "testing", "dependencies": ["CodeReviewer"]},
            {"name": "DocWriter", "role": "documentation", "dependencies": ["CodeReviewer"]},
            {
                "name": "Refactorer",
                "role": "refactor",
                "dependencies": ["CodeReviewer", "TestGenerator"],
            },
        ],
        "coordination_pattern": "sequential",
        "shared_state": False,
        "error_handling": "partial",
    }

    print("📝 Scenario: Multi-agent development pipeline")
    print("   • 4 agents with sequential coordination")
    print("   • Complex dependency chain")
    print("   • No shared state management\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_4_advanced_debugging():
    """Demo 4: Advanced Debugging Wizard"""
    print_section("4. ADVANCED DEBUGGING", "Level 4 - Predict bug patterns")

    wizard = AdvancedDebuggingWizard()

    context = {
        "project_path": "/project",
        "error_logs": [
            {"type": "NullPointerException", "count": 15, "trend": "increasing"},
            {"type": "TimeoutException", "count": 8, "trend": "stable"},
            {"type": "MemoryError", "count": 2, "trend": "new"},
        ],
        "recent_deployments": 3,
        "test_coverage": 0.62,
        "code_complexity": "high",
    }

    print("📝 Scenario: Production errors increasing")
    print("   • NullPointerException: 15 occurrences (increasing)")
    print("   • TimeoutException: 8 occurrences")
    print("   • MemoryError: 2 new occurrences\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_5_agent_orchestration():
    """Demo 5: Agent Orchestration Wizard"""
    print_section("5. AGENT ORCHESTRATION", "Level 4 - Predict orchestration failures")

    wizard = AgentOrchestrationWizard()

    context = {
        "orchestration_type": "hierarchical",
        "agent_count": 8,
        "communication_pattern": "message_passing",
        "state_management": "distributed",
        "failure_handling": "retry_only",
        "max_concurrent_agents": 4,
    }

    print("📝 Scenario: Hierarchical agent orchestration")
    print("   • 8 agents with message passing")
    print("   • Distributed state")
    print("   • Simple retry-based failure handling\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_6_rag_pattern():
    """Demo 6: RAG Pattern Wizard"""
    print_section("6. RAG PATTERN DESIGN", "Level 4 - Predict retrieval quality issues")

    wizard = RAGPatternWizard()

    context = {
        "vector_db": "pinecone",
        "embedding_model": "text-embedding-ada-002",
        "chunk_size": 1500,  # Large chunks
        "overlap": 0,  # No overlap
        "retrieval_k": 3,  # Low k
        "reranking": False,
        "document_count": 50000,
        "query_complexity": "high",
    }

    print("📝 Scenario: RAG system configuration")
    print("   • 50K documents, 1500 char chunks, no overlap")
    print("   • k=3 retrieval, no reranking")
    print("   • High complexity queries\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_7_testing():
    """Demo 7: Testing Wizard"""
    print_section("7. TESTING STRATEGY", "Level 4 - Predict test gaps")

    wizard = TestingWizard()

    context = {
        "project_path": "/project",
        "current_coverage": 0.45,  # 45% coverage
        "test_types": ["unit"],  # Only unit tests
        "critical_paths": ["auth", "payment", "data_pipeline"],
        "coverage_by_module": {
            "auth": 0.20,  # Critical but low coverage
            "payment": 0.35,
            "data_pipeline": 0.15,
            "utils": 0.80,
        },
    }

    print("📝 Scenario: Low test coverage")
    print("   • Overall: 45% coverage")
    print("   • Auth: 20% (critical)")
    print("   • Payment: 35% (critical)")
    print("   • Data pipeline: 15% (critical)\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_8_ai_documentation():
    """Demo 8: AI Documentation Wizard"""
    print_section("8. AI DOCUMENTATION", "Level 4 - Predict documentation gaps")

    wizard = AIDocumentationWizard()

    context = {
        "project_path": "/project",
        "ai_components": ["llm_api", "embedding_service", "vector_db", "prompt_templates"],
        "documentation_exists": {
            "llm_api": True,
            "embedding_service": False,
            "vector_db": False,
            "prompt_templates": False,
        },
        "team_size": 8,
        "onboarding_time": 14,  # days
    }

    print("📝 Scenario: AI project documentation gaps")
    print("   • 4 AI components, only 1 documented")
    print("   • Team size: 8 developers")
    print("   • Onboarding time: 14 days (too long)\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_9_prompt_engineering():
    """Demo 9: Prompt Engineering Wizard"""
    print_section("9. PROMPT ENGINEERING", "Level 4 - Predict prompt issues")

    wizard = PromptEngineeringWizard()

    context = {
        "prompt_count": 25,
        "prompt_patterns": ["zero_shot", "few_shot", "chain_of_thought"],
        "version_control": False,
        "testing_strategy": "manual",
        "prompt_complexity": "high",
        "reuse_patterns": False,
    }

    print("📝 Scenario: Prompt management issues")
    print("   • 25 prompts, no version control")
    print("   • Manual testing only")
    print("   • No reusable patterns\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_10_ai_context():
    """Demo 10: AI Context Management Wizard"""
    print_section("10. AI CONTEXT MANAGEMENT", "Level 4 - Predict context issues")

    wizard = AIContextWizard()

    context = {
        "context_window": 4096,  # Small window
        "average_context_size": 3800,  # Near limit
        "context_strategy": "naive",  # No optimization
        "truncation_handling": "cut_middle",
        "context_types": ["conversation", "documents", "code", "system"],
    }

    print("📝 Scenario: Context window management")
    print("   • 4096 token window, using 3800 avg")
    print("   • Naive strategy, cut middle truncation")
    print("   • Multiple context types competing for space\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_11_security_analysis():
    """Demo 11: Security Analysis Wizard"""
    print_section("11. SECURITY ANALYSIS", "Level 4 - Predict security issues")

    wizard = SecurityAnalysisWizard()

    context = {
        "project_path": "/project",
        "api_key_storage": "environment_variables",
        "pii_handling": "unvalidated",
        "prompt_injection_protection": False,
        "rate_limiting": False,
        "audit_logging": "partial",
        "data_classification": False,
    }

    print("📝 Scenario: AI security posture")
    print("   • No prompt injection protection")
    print("   • Unvalidated PII handling")
    print("   • No rate limiting")
    print("   • Partial audit logging\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def demo_12_enhanced_testing():
    """Demo 12: Enhanced Testing Wizard"""
    print_section("12. ENHANCED TESTING", "Level 4 - Predict testing bottlenecks")

    wizard = EnhancedTestingWizard()

    context = {
        "project_path": "/project",
        "test_suite_size": 2500,
        "test_execution_time": 25,  # minutes
        "flaky_test_count": 15,
        "test_parallelization": False,
        "ci_cd_integration": True,
        "test_data_management": "hardcoded",
    }

    print("📝 Scenario: Test suite challenges")
    print("   • 2500 tests taking 25 minutes")
    print("   • 15 flaky tests")
    print("   • No parallelization")
    print("   • Hardcoded test data\n")

    result = await wizard.analyze(context)
    print_wizard_result(result, wizard.name)


async def main():
    """Run all AI wizard demos"""
    print_section("EMPATHY FRAMEWORK", "AI/Software Development Wizards Demo")

    print("🎯 Focus: Level 4 Anticipatory Intelligence")
    print("   These wizards predict issues 30-90 days before they compound\n")

    try:
        # Run all demos
        await demo_1_multi_model()
        await demo_2_performance_profiling()
        await demo_3_ai_collaboration()
        await demo_4_advanced_debugging()
        await demo_5_agent_orchestration()
        await demo_6_rag_pattern()
        await demo_7_testing()
        await demo_8_ai_documentation()
        await demo_9_prompt_engineering()
        await demo_10_ai_context()
        await demo_11_security_analysis()
        await demo_12_enhanced_testing()

        # Summary
        print_section("SUMMARY", "12 AI Wizards Complete")

        print("✅ All AI wizards demonstrated successfully!\n")

        print("🔮 Level 4 Anticipatory Intelligence:")
        print("   • Predicts issues before they compound")
        print("   • Learns from experience and shares patterns")
        print("   • Identifies non-obvious problems")
        print("   • Provides actionable recommendations\n")

        print("🎯 Wizard Categories:")
        print("   • Model Management: Multi-Model Coordination")
        print("   • Performance: Profiling, Context Management")
        print("   • Quality: Testing, Enhanced Testing, Debugging")
        print("   • Collaboration: AI Collaboration, Agent Orchestration")
        print("   • Knowledge: RAG Patterns, Documentation")
        print("   • Optimization: Prompt Engineering, Security\n")

        print("💡 Key Insights:")
        print("   1. Multi-model complexity grows non-linearly")
        print("   2. Performance issues compound without monitoring")
        print("   3. Test coverage gaps in critical paths are highest risk")
        print("   4. Context window management prevents quality degradation")
        print("   5. Security requires proactive design, not reactive fixes\n")

        print("📚 Pattern Libraries:")
        print("   • Each wizard maintains learned patterns")
        print("   • Patterns shared across team via shared_learning")
        print("   • Recommendations improve over time")
        print("   • Experience from real projects informs predictions\n")

        print("🔗 Related Examples:")
        print("   • Domain Wizards: examples/domain_wizards/all_domain_wizards_demo.py")
        print("   • Coach Wizards: examples/coach/demo_all_wizards.py")
        print("   • Individual Examples: examples/ai_wizards/[wizard]_example.py\n")

        print("📋 Next Steps:")
        print("   1. Integrate wizards into your development workflow")
        print("   2. Configure context collection for your project")
        print("   3. Review wizard predictions weekly")
        print("   4. Contribute patterns back to shared learning")
        print("   5. Customize thresholds for your team's risk tolerance\n")

    except Exception as e:
        print(f"\n❌ Error during demos: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
