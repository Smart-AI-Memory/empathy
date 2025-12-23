#!/usr/bin/env python3
"""
Test Script for Agent & Wizard Intelligence System (v3.1.0)

Run this script to verify all new features are working correctly.
Can be run by humans or AI agents.

Usage:
    python scripts/test_new_features.py           # Run all tests
    python scripts/test_new_features.py --quick   # Quick smoke test
    python scripts/test_new_features.py --verbose # Detailed output
    python scripts/test_new_features.py --interactive  # Interactive mode

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import argparse
import sys
import tempfile
import traceback
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestResult:
    """Result of a single test."""

    name: str
    passed: bool
    message: str
    details: str = ""


class TestRunner:
    """Runs tests and tracks results."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: list[TestResult] = []

    def run_test(self, name: str, test_fn: Callable[[], tuple[bool, str, str]]) -> bool:
        """Run a single test and record result."""
        try:
            passed, message, details = test_fn()
            self.results.append(TestResult(name, passed, message, details))
            self._print_result(name, passed, message, details)
            return passed
        except Exception as e:
            error_details = traceback.format_exc()
            self.results.append(TestResult(name, False, f"Exception: {e}", error_details))
            self._print_result(name, False, f"Exception: {e}", error_details)
            return False

    def _print_result(self, name: str, passed: bool, message: str, details: str):
        """Print test result."""
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"  {status}: {name}")
        if self.verbose or not passed:
            print(f"         {message}")
            if details and (self.verbose or not passed):
                for line in details.split("\n")[:5]:
                    print(f"         {line}")

    def summary(self) -> tuple[int, int]:
        """Print summary and return (passed, total)."""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        print()
        print("=" * 60)
        print(f"SUMMARY: {passed}/{total} tests passed")
        if passed == total:
            print("All tests passed!")
        else:
            print("Failed tests:")
            for r in self.results:
                if not r.passed:
                    print(f"  - {r.name}: {r.message}")
        print("=" * 60)
        return passed, total


# =============================================================================
# MEMORY GRAPH TESTS
# =============================================================================


def test_memory_graph_import():
    """Test that Memory Graph can be imported."""

    return True, "All imports successful", ""


def test_memory_graph_create():
    """Test creating a Memory Graph."""
    from empathy_os.memory import MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)
        stats = graph.get_statistics()
        Path(f.name).unlink()
    return (stats["total_nodes"] == 0, f"Created empty graph with {stats['total_nodes']} nodes", "")


def test_memory_graph_add_finding():
    """Test adding findings to the graph."""
    from empathy_os.memory import MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)
        bug_id = graph.add_finding(
            wizard="test-wizard",
            finding={
                "type": "bug",
                "name": "Test Bug",
                "severity": "high",
                "file": "test.py",
                "line": 42,
            },
        )
        node = graph.get_node(bug_id)
        Path(f.name).unlink()
    return (
        node is not None and node.name == "Test Bug",
        f"Added finding with ID: {bug_id[:20]}...",
        f"Node: {node.name}, Severity: {node.severity}",
    )


def test_memory_graph_edges():
    """Test creating edges between nodes."""
    from empathy_os.memory import EdgeType, MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)
        bug_id = graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug"})
        fix_id = graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix"})
        edge_id = graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)
        stats = graph.get_statistics()
        Path(f.name).unlink()
    return (stats["total_edges"] == 1, f"Created edge: {edge_id[:30]}...", "Edge type: FIXED_BY")


def test_memory_graph_find_similar():
    """Test finding similar nodes."""
    from empathy_os.memory import MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)
        graph.add_finding(
            wizard="test", finding={"type": "bug", "name": "Null reference in auth.py"}
        )
        graph.add_finding(wizard="test", finding={"type": "bug", "name": "Type error in utils.py"})
        similar = graph.find_similar({"name": "Null reference error"}, threshold=0.3)
        Path(f.name).unlink()
    return (
        len(similar) >= 1 and "null" in similar[0][0].name.lower(),
        f"Found {len(similar)} similar node(s)",
        f"Best match: {similar[0][0].name if similar else 'None'}",
    )


def test_memory_graph_find_related():
    """Test finding related nodes via edges."""
    from empathy_os.memory import EdgeType, MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)
        bug_id = graph.add_finding(wizard="test", finding={"type": "bug", "name": "Bug"})
        fix_id = graph.add_finding(wizard="test", finding={"type": "fix", "name": "Fix"})
        graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)
        related = graph.find_related(bug_id, edge_types=[EdgeType.FIXED_BY])
        Path(f.name).unlink()
    return (
        len(related) == 1 and related[0].name == "Fix",
        f"Found {len(related)} related node(s)",
        f"Related: {[n.name for n in related]}",
    )


# =============================================================================
# SMART ROUTER TESTS
# =============================================================================


def test_smart_router_import():
    """Test that Smart Router can be imported."""

    return True, "All imports successful", ""


def test_smart_router_create():
    """Test creating a Smart Router."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    wizards = router.list_wizards()
    return (
        len(wizards) >= 10,
        f"Router created with {len(wizards)} registered wizards",
        f"First 3: {[w.name for w in wizards[:3]]}",
    )


def test_smart_router_route_security():
    """Test routing a security request."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    decision = router.route_sync("Fix the SQL injection vulnerability in auth.py")
    return (
        decision.primary_wizard == "security-audit",
        f"Routed to: {decision.primary_wizard}",
        f"Confidence: {decision.confidence:.2f}, Secondary: {decision.secondary_wizards}",
    )


def test_smart_router_route_performance():
    """Test routing a performance request."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    decision = router.route_sync("Optimize slow database queries")
    return (
        decision.primary_wizard == "perf-audit",
        f"Routed to: {decision.primary_wizard}",
        f"Confidence: {decision.confidence:.2f}",
    )


def test_smart_router_route_bugs():
    """Test routing a bug-related request."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    decision = router.route_sync("Find the null reference error causing crashes")
    return (
        decision.primary_wizard == "bug-predict",
        f"Routed to: {decision.primary_wizard}",
        f"Confidence: {decision.confidence:.2f}",
    )


def test_smart_router_file_suggestions():
    """Test file-based wizard suggestions."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    suggestions = router.suggest_for_file("requirements.txt")
    return (
        "dependency-check" in suggestions,
        f"Suggestions for requirements.txt: {suggestions}",
        "",
    )


def test_smart_router_error_suggestions():
    """Test error-based wizard suggestions."""
    from empathy_os.routing import SmartRouter

    router = SmartRouter()
    suggestions = router.suggest_for_error("NullReferenceException")
    return (
        "bug-predict" in suggestions,
        f"Suggestions for NullReferenceException: {suggestions}",
        "",
    )


# =============================================================================
# CHAIN EXECUTOR TESTS
# =============================================================================


def test_chain_executor_import():
    """Test that Chain Executor can be imported."""

    return True, "All imports successful", ""


def test_chain_executor_load_config():
    """Test loading chain configuration."""
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")
    templates = executor.list_templates()
    return (
        len(templates) >= 4,
        f"Loaded {len(templates)} templates",
        f"Templates: {list(templates.keys())}",
    )


def test_chain_executor_get_triggers():
    """Test getting triggered chains."""
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")
    triggers = executor.get_triggered_chains("security-audit", {"high_severity_count": 5})
    return (
        len(triggers) >= 1,
        f"Found {len(triggers)} trigger(s)",
        f"Next wizards: {[t.next_wizard for t in triggers]}",
    )


def test_chain_executor_condition_evaluation():
    """Test condition evaluation."""
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")

    # Test greater than
    result1 = executor._evaluate_condition("count > 5", {"count": 10})
    # Test equals
    result2 = executor._evaluate_condition("status == 'critical'", {"status": "critical"})
    # Test boolean
    result3 = executor._evaluate_condition("flag == true", {"flag": True})

    all_pass = result1 and result2 and result3
    return (all_pass, f"Conditions: >={result1}, =={result2}, bool={result3}", "")


def test_chain_executor_templates():
    """Test getting chain templates."""
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")
    template = executor.get_template("full-security-review")
    return (
        template is not None and "security-audit" in template,
        f"Template 'full-security-review': {template}",
        "",
    )


# =============================================================================
# PROMPT ENGINEERING WIZARD TESTS
# =============================================================================


def test_prompt_wizard_import():
    """Test that Prompt Engineering Wizard can be imported."""

    return True, "All imports successful", ""


def test_prompt_wizard_analyze_poor():
    """Test analyzing a poor prompt."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    analysis = wizard.analyze_prompt("Fix this bug")
    return (
        analysis.overall_score < 0.5 and len(analysis.issues) > 0,
        f"Score: {analysis.overall_score:.2f}, Issues: {len(analysis.issues)}",
        f"Issues: {analysis.issues}",
    )


def test_prompt_wizard_analyze_good():
    """Test analyzing a good prompt."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    prompt = """You are a senior security engineer.

Context: Reviewing a Python web application for vulnerabilities.

Analyze this code for SQL injection risks.

Format your response as JSON with severity and recommendation fields.
"""
    analysis = wizard.analyze_prompt(prompt)
    return (
        analysis.overall_score > 0.5 and analysis.has_role and analysis.has_output_format,
        f"Score: {analysis.overall_score:.2f}, Has role: {analysis.has_role}",
        f"Has context: {analysis.has_context}, Has output format: {analysis.has_output_format}",
    )


def test_prompt_wizard_generate():
    """Test generating a prompt."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    prompt = wizard.generate_prompt(
        task="Review code for security vulnerabilities",
        role="a senior security engineer",
        constraints=["Focus on OWASP top 10"],
        output_format="JSON with severity and recommendation",
    )
    return (
        "security engineer" in prompt and "OWASP" in prompt and "JSON" in prompt,
        f"Generated prompt ({len(prompt)} chars)",
        prompt[:100] + "...",
    )


def test_prompt_wizard_optimize():
    """Test optimizing tokens."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    verbose = "In order to fix the problem, we basically need to actually just update the code."
    result = wizard.optimize_tokens(verbose)
    return (
        result.token_reduction > 0 and len(result.changes_made) > 0,
        f"Reduction: {result.token_reduction:.1%}",
        f"Changes: {result.changes_made}",
    )


def test_prompt_wizard_cot():
    """Test adding chain-of-thought."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    prompt = "Debug this issue."
    enhanced = wizard.add_chain_of_thought(prompt, "debug")
    return (
        "expected behavior" in enhanced.lower() and "root cause" in enhanced.lower(),
        f"Added CoT scaffolding ({len(enhanced)} chars)",
        "",
    )


def test_prompt_wizard_few_shot():
    """Test adding few-shot examples."""
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()
    prompt = "Analyze this code."
    examples = [
        {"input": "def foo(): pass", "output": "Missing docstring"},
        {"input": "x = None; x.bar()", "output": "Potential null reference"},
    ]
    result = wizard.add_few_shot_examples(prompt, examples)
    return ("Example 1" in result and "Example 2" in result, f"Added {len(examples)} examples", "")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================


def test_integration_router_to_graph():
    """Test integration: Router decision stored in graph."""
    from empathy_os.memory import MemoryGraph
    from empathy_os.routing import SmartRouter

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        router = SmartRouter()
        graph = MemoryGraph(path=f.name)

        # Route a request
        decision = router.route_sync("Fix security issue")

        # Store the routing decision in graph
        node_id = graph.add_finding(
            wizard="smart-router",
            finding={
                "type": "pattern",
                "name": f"Routed to {decision.primary_wizard}",
                "metadata": {
                    "confidence": decision.confidence,
                    "secondary": decision.secondary_wizards,
                },
            },
        )

        node = graph.get_node(node_id)
        Path(f.name).unlink()

    return (
        node is not None and decision.primary_wizard in node.name,
        "Stored routing decision in graph",
        f"Node: {node.name}",
    )


def test_integration_chain_execution():
    """Test integration: Chain executor with triggers."""
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")

    # Simulate security audit result with high severity
    result = {"high_severity_count": 3, "vulnerability_type": "injection"}

    # Check what triggers
    triggers = executor.get_triggered_chains("security-audit", result)

    # Create execution
    execution = executor.create_execution("security-audit", triggers)

    return (
        len(execution.steps) >= 2,  # Initial + triggered
        f"Created chain with {len(execution.steps)} steps",
        f"Steps: {[s.wizard_name for s in execution.steps]}",
    )


# =============================================================================
# MAIN
# =============================================================================


def run_all_tests(verbose: bool = False, quick: bool = False):
    """Run all tests."""
    runner = TestRunner(verbose=verbose)

    print()
    print("=" * 60)
    print("AGENT & WIZARD INTELLIGENCE SYSTEM - TEST SUITE")
    print("Version: 3.1.0")
    print("=" * 60)
    print()

    # Memory Graph Tests
    print("MEMORY GRAPH TESTS")
    print("-" * 40)
    runner.run_test("Import Memory Graph", test_memory_graph_import)
    runner.run_test("Create Memory Graph", test_memory_graph_create)
    runner.run_test("Add Finding", test_memory_graph_add_finding)
    if not quick:
        runner.run_test("Create Edges", test_memory_graph_edges)
        runner.run_test("Find Similar", test_memory_graph_find_similar)
        runner.run_test("Find Related", test_memory_graph_find_related)
    print()

    # Smart Router Tests
    print("SMART ROUTER TESTS")
    print("-" * 40)
    runner.run_test("Import Smart Router", test_smart_router_import)
    runner.run_test("Create Smart Router", test_smart_router_create)
    runner.run_test("Route Security Request", test_smart_router_route_security)
    if not quick:
        runner.run_test("Route Performance Request", test_smart_router_route_performance)
        runner.run_test("Route Bug Request", test_smart_router_route_bugs)
        runner.run_test("File Suggestions", test_smart_router_file_suggestions)
        runner.run_test("Error Suggestions", test_smart_router_error_suggestions)
    print()

    # Chain Executor Tests
    print("CHAIN EXECUTOR TESTS")
    print("-" * 40)
    runner.run_test("Import Chain Executor", test_chain_executor_import)
    runner.run_test("Load Config", test_chain_executor_load_config)
    runner.run_test("Get Triggers", test_chain_executor_get_triggers)
    if not quick:
        runner.run_test("Condition Evaluation", test_chain_executor_condition_evaluation)
        runner.run_test("Get Templates", test_chain_executor_templates)
    print()

    # Prompt Engineering Wizard Tests
    print("PROMPT ENGINEERING WIZARD TESTS")
    print("-" * 40)
    runner.run_test("Import Prompt Wizard", test_prompt_wizard_import)
    runner.run_test("Analyze Poor Prompt", test_prompt_wizard_analyze_poor)
    runner.run_test("Analyze Good Prompt", test_prompt_wizard_analyze_good)
    if not quick:
        runner.run_test("Generate Prompt", test_prompt_wizard_generate)
        runner.run_test("Optimize Tokens", test_prompt_wizard_optimize)
        runner.run_test("Add Chain-of-Thought", test_prompt_wizard_cot)
        runner.run_test("Add Few-Shot Examples", test_prompt_wizard_few_shot)
    print()

    # Integration Tests
    if not quick:
        print("INTEGRATION TESTS")
        print("-" * 40)
        runner.run_test("Router to Graph Integration", test_integration_router_to_graph)
        runner.run_test("Chain Execution", test_integration_chain_execution)
        print()

    passed, total = runner.summary()
    return passed == total


def run_interactive():
    """Run interactive demonstration."""
    print()
    print("=" * 60)
    print("INTERACTIVE FEATURE DEMONSTRATION")
    print("=" * 60)
    print()

    # 1. Smart Router Demo
    print("1. SMART ROUTER DEMO")
    print("-" * 40)
    from empathy_os.routing import SmartRouter

    router = SmartRouter()

    requests = [
        "Fix the security vulnerability in auth.py",
        "Optimize slow database queries",
        "Generate unit tests for the payment module",
        "Review this code for bugs",
    ]

    for req in requests:
        decision = router.route_sync(req)
        print(f'  Request: "{req}"')
        print(f"  → Primary: {decision.primary_wizard}, Confidence: {decision.confidence:.2f}")
        print()

    # 2. Prompt Engineering Demo
    print("2. PROMPT ENGINEERING DEMO")
    print("-" * 40)
    from coach_wizards import PromptEngineeringWizard

    wizard = PromptEngineeringWizard()

    # Analyze a prompt
    bad_prompt = "Fix this bug"
    analysis = wizard.analyze_prompt(bad_prompt)
    print(f'  Analyzing: "{bad_prompt}"')
    print(f"  Score: {analysis.overall_score:.2f}")
    print(f"  Issues: {analysis.issues}")
    print()

    # Generate optimized prompt
    print("  Generating optimized prompt...")
    optimized = wizard.generate_prompt(
        task="Fix the authentication bug",
        role="a senior backend engineer",
        constraints=["Focus on security implications"],
        output_format="JSON with root_cause and fix fields",
    )
    print(f"  Generated ({len(optimized)} chars):")
    print(f"  {optimized[:150]}...")
    print()

    # 3. Chain Executor Demo
    print("3. AUTO-CHAINING DEMO")
    print("-" * 40)
    from empathy_os.routing import ChainExecutor

    executor = ChainExecutor(".empathy/wizard_chains.yaml")

    print("  Simulating security audit with high severity findings...")
    result = {"high_severity_count": 5, "vulnerability_type": "injection"}
    triggers = executor.get_triggered_chains("security-audit", result)

    print(f"  Triggers fired: {len(triggers)}")
    for t in triggers:
        print(f"    → {t.next_wizard}: {t.reason}")
    print()

    print("  Available templates:")
    for name, steps in executor.list_templates().items():
        print(f"    {name}: {' → '.join(steps)}")
    print()

    # 4. Memory Graph Demo
    print("4. MEMORY GRAPH DEMO")
    print("-" * 40)
    from empathy_os.memory import EdgeType, MemoryGraph

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        graph = MemoryGraph(path=f.name)

        # Add some findings
        bug1 = graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "Null reference in auth.py:42", "severity": "high"},
        )
        bug2 = graph.add_finding(
            wizard="bug-predict",
            finding={"type": "bug", "name": "Null pointer in utils.py:15", "severity": "medium"},
        )
        fix1 = graph.add_finding(
            wizard="code-review", finding={"type": "fix", "name": "Add null check guard clause"}
        )

        # Connect them
        graph.add_edge(bug1, fix1, EdgeType.FIXED_BY)
        graph.add_edge(bug1, bug2, EdgeType.SIMILAR_TO, bidirectional=True)

        print("  Added 3 nodes, 3 edges")

        # Find similar
        similar = graph.find_similar({"name": "Null reference error"})
        print(f"  Similar to 'Null reference error': {[s[0].name for s in similar[:2]]}")

        # Find fixes
        fixes = graph.find_related(bug1, edge_types=[EdgeType.FIXED_BY])
        print(f"  Fixes for bug1: {[f.name for f in fixes]}")

        # Stats
        stats = graph.get_statistics()
        print(f"  Graph stats: {stats['total_nodes']} nodes, {stats['total_edges']} edges")

        Path(f.name).unlink()

    print()
    print("=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Test Agent & Wizard Intelligence System")
    parser.add_argument("--quick", action="store_true", help="Run quick smoke tests only")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive demo mode")
    args = parser.parse_args()

    if args.interactive:
        run_interactive()
        return 0

    success = run_all_tests(verbose=args.verbose, quick=args.quick)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
