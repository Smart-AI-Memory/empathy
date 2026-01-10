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
        print("  snakeviz benchmarks/profiles/cost_tracker.prof")
        print("  snakeviz benchmarks/profiles/feedback_loops.prof")

    except Exception as e:
        print(f"\n❌ Error during profiling: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
