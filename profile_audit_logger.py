#!/usr/bin/env python
"""
Performance profiling for Audit Logger module

Profiles audit logging performance to identify optimization targets.
Target: <1.5ms/event (current: 1-3ms/event)

Usage:
    python profile_audit_logger.py
"""

import cProfile
import io
import pstats
import tempfile
from pathlib import Path
from pstats import SortKey

from empathy_llm_toolkit.security import AuditLogger


def profile_audit_logging():
    """Profile audit logging with various event types"""

    # Use temporary directory for test logs
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=tmpdir)

        print("=" * 60)
        print("Audit Logger Performance Profiling")
        print("=" * 60)

        test_scenarios = {
            "llm_requests": {
                "count": 1000,
                "method": lambda: logger.log_llm_request(
                    user_id="test@company.com",
                    empathy_level=3,
                    provider="anthropic",
                    model="claude-sonnet-4",
                    memory_sources=["enterprise", "user", "project"],
                    pii_count=5,
                    secrets_count=0,
                ),
            },
            "pattern_stores": {
                "count": 500,
                "method": lambda: logger.log_pattern_store(
                    user_id="dev@company.com",
                    pattern_id=f"pat_{id(logger)}",
                    pattern_type="algorithm",
                    classification="INTERNAL",
                    pii_scrubbed=3,
                    secrets_detected=0,
                ),
            },
            "security_violations": {
                "count": 100,
                "method": lambda: logger.log_security_violation(
                    user_id="attacker@external.com",
                    violation_type="secrets_detected",
                    details={"secret_type": "api_key", "blocked": True},
                    severity="CRITICAL",
                ),
            },
            "pattern_retrieves": {
                "count": 2000,
                "method": lambda: logger.log_pattern_retrieve(
                    user_id="user@company.com",
                    pattern_id=f"pat_{id(logger)}",
                    classification="SENSITIVE",
                    pii_count=5,
                ),
            },
        }

        results = {}

        for scenario_name, scenario in test_scenarios.items():
            print(f"\nProfiling: {scenario_name} ({scenario['count']} events)")

            # Profile the logging operation
            profiler = cProfile.Profile()
            profiler.enable()

            # Log events
            for _ in range(scenario["count"]):
                scenario["method"]()

            profiler.disable()

            # Analyze results
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.strip_dirs()
            ps.sort_stats(SortKey.CUMULATIVE)

            # Get top 10 functions
            ps.print_stats(10)

            results[scenario_name] = {
                "count": scenario["count"],
                "stats": s.getvalue(),
            }

            print(f"  Events logged: {scenario['count']}")
            print("  Top functions:")
            print(s.getvalue()[:500])

        # Summary report
        print("\n" + "=" * 60)
        print("PROFILING SUMMARY: Audit Logger")
        print("=" * 60)

        for name, result in results.items():
            print(f"\n{name}:")
            print(f"  Events: {result['count']}")
            print("  Top 3 Hotspots:")

            # Extract top 3 function names from stats
            lines = result["stats"].split("\n")
            for i, line in enumerate(lines[5:8]):  # Skip header, show top 3
                if line.strip():
                    print(f"    {i+1}. {line.strip()[:80]}")

        # Check log file size
        audit_file = Path(tmpdir) / "audit.jsonl"
        if audit_file.exists():
            size_mb = audit_file.stat().st_size / (1024 * 1024)
            print(f"\nAudit log file size: {size_mb:.2f} MB")
            print(f"Total events logged: {sum(s['count'] for s in test_scenarios.values())}")

        print("\n" + "=" * 60)
        print("Optimization Targets:")
        print("  1. JSON serialization (use orjson)")
        print("  2. File I/O operations (use async writes)")
        print("  3. Timestamp formatting (cache common formats)")
        print("  4. Batch writes (buffer events)")
        print("  5. Reduce dict copying overhead")
        print("=" * 60)


if __name__ == "__main__":
    profile_audit_logging()
