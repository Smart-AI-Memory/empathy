"""Profiling test suite for identifying bottlenecks in Empathy Framework.

Runs performance profiling on key operations to identify optimization opportunities.

Usage:
    python benchmarks/profile_suite.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from pathlib import Path

# Add project root to path (for scripts/ and src/)
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from scripts.profile_utils import profile_function, time_function


@profile_function(output_file="benchmarks/profiles/scanner_scan.prof")
@time_function
def profile_scanner():
    """Profile project scanner on real codebase."""
    from empathy_os.project_index.scanner import ProjectScanner

    print("\n" + "=" * 60)
    print("Profiling: Project Scanner")
    print("=" * 60)

    scanner = ProjectScanner(project_root=".")
    records, summary = scanner.scan()

    print(f"✓ Scanned {summary.total_files} files")
    print(f"✓ Source files: {summary.source_files}")
    print(f"✓ Test files: {summary.test_files}")
    print(f"✓ Lines of code: {summary.total_lines_of_code:,}")


@profile_function(output_file="benchmarks/profiles/pattern_library.prof")
@time_function
def profile_pattern_library():
    """Profile pattern library operations."""
    from empathy_os.pattern_library import PatternLibrary, Pattern

    print("\n" + "=" * 60)
    print("Profiling: Pattern Library")
    print("=" * 60)

    library = PatternLibrary()

    # Create some test patterns
    for i in range(100):
        pattern = Pattern(
            id=f"pat_{i:03d}",
            agent_id=f"agent_{i % 10}",
            pattern_type=["sequential", "temporal", "conditional", "behavioral"][i % 4],
            name=f"test_pattern_{i}",
            description=f"Test pattern {i}",
            tags=[f"tag_{i % 10}"],
            confidence=0.5 + (i % 50) / 100,
        )
        library.contribute_pattern(f"agent_{i % 10}", pattern)

    # Simulate pattern matching
    match_count = 0
    for i in range(1000):
        context = {
            "task_type": f"task_{i % 5}",
            "user_role": "developer",
            "time_of_day": ["morning", "afternoon", "evening"][i % 3],
        }
        matches = library.query_patterns(
            agent_id=f"agent_{i % 10}", context=context, pattern_type=None
        )
        match_count += len(matches)

    print(f"✓ Created 100 patterns")
    print(f"✓ Performed 1000 pattern matches")
    print(f"✓ Total matches: {match_count}")


@profile_function(output_file="benchmarks/profiles/cost_tracker.prof")
@time_function
def profile_cost_tracker():
    """Profile cost tracking operations."""
    from empathy_os.cost_tracker import CostTracker

    print("\n" + "=" * 60)
    print("Profiling: Cost Tracker")
    print("=" * 60)

    tracker = CostTracker()

    # Simulate logging 1000 requests
    for i in range(1000):
        tracker.log_request(
            model=f"claude-3-{'haiku' if i % 3 == 0 else 'sonnet'}",
            input_tokens=100 + i % 100,
            output_tokens=50 + i % 50,
            task_type=f"task_{i % 5}",
        )

    summary = tracker.get_summary(days=7)

    print(f"✓ Logged 1000 requests")
    print(f"✓ Actual cost: ${summary['actual_cost']:.4f}")
    print(f"✓ Input tokens: {summary['input_tokens']:,}")
    print(f"✓ Output tokens: {summary['output_tokens']:,}")


@profile_function(output_file="benchmarks/profiles/feedback_loops.prof")
@time_function
def profile_feedback_loops():
    """Profile feedback loop detection."""
    from empathy_os.feedback_loops import FeedbackLoopDetector

    print("\n" + "=" * 60)
    print("Profiling: Feedback Loop Detector")
    print("=" * 60)

    detector = FeedbackLoopDetector()

    # Generate test session history
    session_history = []
    for i in range(500):
        session_history.append(
            {
                "trust": 0.5 + (i % 50) / 100,
                "success_rate": 0.6 + (i % 40) / 100,
                "patterns_used": i % 10,
                "user_satisfaction": 0.7 + (i % 30) / 100,
            }
        )

    # Detect loops multiple times (simulate repeated checks)
    virtuous_count = 0
    vicious_count = 0
    active_count = 0

    for _ in range(100):
        if detector.detect_virtuous_cycle(session_history):
            virtuous_count += 1
        if detector.detect_vicious_cycle(session_history):
            vicious_count += 1
        active = detector.detect_active_loop(session_history)
        if active:
            active_count += 1

    print(f"✓ Generated 500-item session history")
    print(f"✓ Ran 100 detection cycles")
    print(f"✓ Virtuous cycles detected: {virtuous_count}")
    print(f"✓ Vicious cycles detected: {vicious_count}")
    print(f"✓ Active loops detected: {active_count}")


@profile_function(output_file="benchmarks/profiles/workflow_execution.prof")
@time_function
def profile_workflow_execution():
    """Profile workflow execution data processing."""
    from empathy_os.workflows.base import ModelTier, _load_workflow_history

    print("\n" + "=" * 60)
    print("Profiling: Workflow Execution")
    print("=" * 60)

    # Load workflow history
    history = _load_workflow_history()
    print(f"✓ Loaded {len(history)} workflow history entries")

    # Simulate workflow data processing
    results = []
    for i in range(200):
        result_data = {
            "workflow_id": f"workflow_{i % 5}",
            "success": i % 10 != 0,
            "output": {"result": f"Output {i}", "confidence": 0.5 + (i % 50) / 100},
            "error": None if i % 10 != 0 else "Simulated error",
            "metadata": {
                "execution_time": 0.1 + (i % 10) / 100,
                "tokens_used": 100 + i % 100,
                "tier": ModelTier.CHEAP.value if i % 3 == 0 else ModelTier.CAPABLE.value,
            },
        }
        results.append(result_data)

    print(f"✓ Created {len(results)} workflow result objects")

    # Process results
    successful = sum(1 for r in results if r["success"])
    failed = [r for r in results if not r["success"]]
    avg_tokens = sum(r["metadata"]["tokens_used"] for r in results) / len(results)

    print(f"✓ Success rate: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
    print(f"✓ Failed: {len(failed)}")
    print(f"✓ Avg tokens: {avg_tokens:.0f}")


@profile_function(output_file="benchmarks/profiles/memory_operations.prof")
@time_function
def profile_memory_operations():
    """Profile unified memory operations."""
    from empathy_os.memory.unified import UnifiedMemory
    from empathy_os.pattern_library import Pattern

    print("\n" + "=" * 60)
    print("Profiling: Memory Operations")
    print("=" * 60)

    memory = UnifiedMemory(user_id="profiler_test")

    # Test stash/retrieve operations (short-term memory)
    stash_count = 0
    for i in range(200):
        key = f"temp_data_{i}"
        value = {
            "content": f"Memory content {i} " * 10,
            "metadata": {
                "timestamp": f"2026-01-10T00:{i:02d}:00Z",
                "type": ["fact", "procedure", "experience"][i % 3],
                "importance": 0.5 + (i % 50) / 100,
            },
        }
        if memory.stash(key, value, ttl_seconds=3600):
            stash_count += 1

    print(f"✓ Stashed {stash_count} items in short-term memory")

    # Test retrieval
    retrieve_count = 0
    for i in range(100):
        key = f"temp_data_{i}"
        result = memory.retrieve(key)
        if result is not None:
            retrieve_count += 1

    print(f"✓ Retrieved {retrieve_count} items from short-term memory")

    # Test pattern staging and persistence
    pattern_count = 0
    for i in range(50):
        pattern_data = {
            "id": f"memory_pattern_{i}",
            "name": f"Test pattern {i}",
            "description": f"Memory test pattern {i}",
            "tags": [f"tag_{i % 10}"],
            "confidence": 0.5 + (i % 50) / 100,
            "examples": [f"example_{j}" for j in range(3)],
        }
        pattern_id = memory.stage_pattern(
            pattern_data=pattern_data, pattern_type="sequential", ttl_hours=24
        )
        if pattern_id:
            pattern_count += 1

    print(f"✓ Staged {pattern_count} patterns")

    # Get staged patterns
    staged = memory.get_staged_patterns()
    print(f"✓ Retrieved {len(staged)} staged patterns")

    # Test pattern recall
    recall_count = 0
    for i in range(50):
        pattern = memory.recall_pattern(pattern_id=f"memory_pattern_{i % pattern_count}")
        if pattern:
            recall_count += 1

    print(f"✓ Recalled {recall_count} patterns")


@profile_function(output_file="benchmarks/profiles/test_generation.prof")
@time_function
def profile_test_generation():
    """Profile test generation workflow."""
    from empathy_os.workflows.test_gen import TestGenerationWorkflow

    print("\n" + "=" * 60)
    print("Profiling: Test Generation")
    print("=" * 60)

    workflow = TestGenerationWorkflow()

    # Simulate analyzing functions for test generation
    test_functions = []
    for i in range(50):
        func_code = f"""
def calculate_sum_{i}(a: int, b: int) -> int:
    '''Calculate sum of two integers.

    Args:
        a: First integer
        b: Second integer

    Returns:
        Sum of a and b

    Raises:
        TypeError: If inputs are not integers
    '''
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("Inputs must be integers")
    return a + b
"""
        test_functions.append(
            {
                "name": f"calculate_sum_{i}",
                "code": func_code,
                "docstring": "Calculate sum of two integers.",
            }
        )

    print(f"✓ Created {len(test_functions)} function definitions")

    # Simulate test case generation analysis
    # (Note: We're not actually calling LLM, just testing the data structures)
    test_cases_generated = 0
    for func in test_functions:
        # Simulate generating 3 test cases per function
        test_cases_generated += 3

    print(f"✓ Simulated generation of {test_cases_generated} test cases")
    print(f"✓ Functions analyzed: {len(test_functions)}")


@time_function
def profile_file_operations():
    """Profile file I/O operations."""
    from pathlib import Path

    print("\n" + "=" * 60)
    print("Profiling: File Operations")
    print("=" * 60)

    # Test glob operations
    py_files = list(Path("src").rglob("*.py"))
    print(f"✓ Found {len(py_files)} Python files")

    # Test file reading (sample)
    sample_files = py_files[:10]
    total_lines = 0
    for file in sample_files:
        try:
            lines = len(file.read_text().splitlines())
            total_lines += lines
        except Exception:
            pass

    print(f"✓ Read {len(sample_files)} sample files")
    print(f"✓ Total lines in sample: {total_lines:,}")


if __name__ == "__main__":
    import os

    os.makedirs("benchmarks/profiles", exist_ok=True)

    print("\n" + "=" * 60)
    print("PROFILING SUITE - Empathy Framework")
    print("Phase 2 Performance Optimization")
    print("=" * 60)

    try:
        # Run profiling on key areas
        profile_scanner()
        profile_pattern_library()
        profile_workflow_execution()
        profile_memory_operations()
        profile_test_generation()
        profile_cost_tracker()
        profile_feedback_loops()
        profile_file_operations()

        print("\n" + "=" * 60)
        print("PROFILING COMPLETE")
        print("=" * 60)
        print("\nProfile files saved to benchmarks/profiles/")
        print("\nVisualize with snakeviz:")
        print("  snakeviz benchmarks/profiles/scanner_scan.prof")
        print("  snakeviz benchmarks/profiles/pattern_library.prof")
        print("  snakeviz benchmarks/profiles/workflow_execution.prof")
        print("  snakeviz benchmarks/profiles/memory_operations.prof")
        print("  snakeviz benchmarks/profiles/test_generation.prof")
        print("  snakeviz benchmarks/profiles/cost_tracker.prof")
        print("  snakeviz benchmarks/profiles/feedback_loops.prof")

    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
