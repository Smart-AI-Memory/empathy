"""Profiling test suite for identifying bottlenecks in Empathy Framework.

Runs performance profiling on key operations to identify optimization opportunities.

Usage:
    python benchmarks/profile_suite.py

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from scripts.profile_utils import profile_function, time_function


@profile_function(output_file="benchmarks/profiles/scanner_scan.prof")
@time_function
def profile_scanner():
    """Profile project scanner on real codebase."""
    from empathy_os.project_index import ProjectIndex

    print("\n" + "=" * 60)
    print("Profiling: Project Scanner")
    print("=" * 60)

    index = ProjectIndex(project_root=".")
    records, summary = index.scan()

    print(f"✓ Scanned {summary.total_files} files")
    print(f"✓ Lines of code: {summary.total_lines_of_code:,}")
    print(f"✓ Test files: {summary.test_file_count}")


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
            name=f"test_pattern_{i}",
            description=f"Test pattern {i}",
            trigger=f"trigger_{i}",
            response=f"response_{i}",
            tags=[f"tag_{i % 10}"],
            confidence=0.5 + (i % 50) / 100,
        )
        library.add_pattern(pattern)

    # Simulate pattern matching
    match_count = 0
    for i in range(1000):
        context = {"query": f"test query {i}", "history": [f"item {j}" for j in range(10)]}
        matches = library.match(context)
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
    report = tracker.get_report(days=7)

    print(f"✓ Logged 1000 requests")
    print(f"✓ Total cost: ${summary['total_cost']:.4f}")
    print(f"✓ Total tokens: {summary['total_tokens']:,}")


@profile_function(output_file="benchmarks/profiles/feedback_loops.prof")
@time_function
def profile_feedback_loops():
    """Profile feedback loop detection."""
    from empathy_os.feedback_loops import FeedbackLoopDetector

    print("\n" + "=" * 60)
    print("Profiling: Feedback Loop Detector")
    print("=" * 60)

    detector = FeedbackLoopDetector()

    # Simulate session history
    for i in range(500):
        session_data = {
            "trust": 0.5 + (i % 50) / 100,
            "success_rate": 0.6 + (i % 40) / 100,
            "patterns_used": i % 10,
            "user_satisfaction": 0.7 + (i % 30) / 100,
        }
        detector.update_metrics(session_data)

    # Detect loops
    virtuous = detector.detect_virtuous_cycle(metric="trust")
    vicious = detector.detect_vicious_cycle(metric="success_rate")
    active_loops = detector.detect_active_loop()

    print(f"✓ Processed 500 session updates")
    print(f"✓ Virtuous cycles: {len([v for v in [virtuous] if v])}")
    print(f"✓ Vicious cycles: {len([v for v in [vicious] if v])}")
    print(f"✓ Active loops: {len(active_loops)}")


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
