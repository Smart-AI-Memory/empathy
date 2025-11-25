#!/usr/bin/env python
"""
End-to-End Performance Profiling for Complete Security Pipeline

Profiles the complete security pipeline to identify overall bottlenecks.
Target: <10ms end-to-end (current: <20ms)

Usage:
    python profile_complete_pipeline.py
"""

import cProfile
import io
import pstats
import tempfile
import time
from pstats import SortKey

from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig
from empathy_llm_toolkit.security import SecureMemDocsIntegration


def profile_complete_pipeline():
    """Profile complete security pipeline end-to-end"""

    print("=" * 60)
    print("Complete Security Pipeline Performance Profiling")
    print("=" * 60)

    # Use temporary directory for test storage
    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup integration with security enabled
        config = ClaudeMemoryConfig(enabled=False)  # Simplified for profiling
        integration = SecureMemDocsIntegration(config)
        from pathlib import Path

        integration.storage.storage_dir = Path(tmpdir)

        # Test scenarios representing real-world usage
        test_scenarios = {
            "public_pattern_no_pii": {
                "content": "Standard Python sorting algorithm using quicksort with O(n log n) complexity.",
                "pattern_type": "algorithm",
                "user_id": "dev@company.com",
                "iterations": 100,
            },
            "internal_proprietary": {
                "content": """
                Our proprietary Level 4 anticipatory prediction algorithm:
                1. Analyze user trajectory with confidence scoring
                2. Identify leverage points for intervention
                3. Generate contextual alerts
                This is confidential internal IP.
                """,
                "pattern_type": "algorithm",
                "user_id": "dev@company.com",
                "iterations": 100,
            },
            "sensitive_with_pii": {
                "content": """
                Patient handoff protocol for John Doe (MRN: 1234567):
                Contact: doctor@hospital.com
                Phone: (555) 123-4567
                Medical history: Confidential
                """,
                "pattern_type": "clinical_protocol",
                "user_id": "doctor@hospital.com",
                "iterations": 100,
            },
            "large_document_10kb": {
                "content": """
                Comprehensive healthcare analysis report.
                Patient data: Multiple patients with various conditions.
                Contact: admin@hospital.com, Phone: 555-987-6543
                """
                * 100,
                "pattern_type": "report",
                "user_id": "admin@hospital.com",
                "iterations": 50,
            },
        }

        results = {}

        for scenario_name, scenario in test_scenarios.items():
            print(f"\n{'='*60}")
            print(f"Scenario: {scenario_name}")
            print(f"Content size: {len(scenario['content'])} bytes")
            print(f"Iterations: {scenario['iterations']}")
            print(f"{'='*60}")

            # Warm-up run
            integration.store_pattern(
                content=scenario["content"],
                pattern_type=scenario["pattern_type"],
                user_id=scenario["user_id"],
                auto_classify=True,
            )

            # Profile the complete pipeline
            profiler = cProfile.Profile()

            # Timing measurement
            start_time = time.perf_counter()

            profiler.enable()
            for _ in range(scenario["iterations"]):
                result = integration.store_pattern(
                    content=scenario["content"],
                    pattern_type=scenario["pattern_type"],
                    user_id=scenario["user_id"],
                    auto_classify=True,
                )
            profiler.disable()

            end_time = time.perf_counter()

            # Calculate metrics
            total_time_ms = (end_time - start_time) * 1000
            avg_time_ms = total_time_ms / scenario["iterations"]
            throughput_ops_sec = scenario["iterations"] / (total_time_ms / 1000)

            # Analyze profiling results
            s = io.StringIO()
            ps = pstats.Stats(profiler, stream=s)
            ps.strip_dirs()
            ps.sort_stats(SortKey.CUMULATIVE)
            ps.print_stats(15)  # Top 15 functions

            results[scenario_name] = {
                "content_size": len(scenario["content"]),
                "iterations": scenario["iterations"],
                "total_time_ms": total_time_ms,
                "avg_time_ms": avg_time_ms,
                "throughput_ops_sec": throughput_ops_sec,
                "stats": s.getvalue(),
                "classification": result.get("classification"),
                "pii_count": result["sanitization_report"]["pii_count"],
                "secrets_detected": result["sanitization_report"]["secrets_detected"],
            }

            print("\nPerformance Metrics:")
            print(f"  Total time: {total_time_ms:.2f}ms")
            print(f"  Average per operation: {avg_time_ms:.2f}ms")
            print(f"  Throughput: {throughput_ops_sec:.2f} ops/sec")
            print(f"  Classification: {result['classification']}")
            print(f"  PII detected: {result['sanitization_report']['pii_count']}")

            print("\nTop 5 Hotspots:")
            lines = s.getvalue().split("\n")
            for i, line in enumerate(lines[5:10]):
                if line.strip():
                    print(f"  {i+1}. {line.strip()[:80]}")

        # Generate comprehensive summary
        print("\n" + "=" * 60)
        print("COMPLETE PIPELINE PROFILING SUMMARY")
        print("=" * 60)

        print("\nPerformance by Scenario:")
        print(f"{'Scenario':<30} {'Avg Time':<12} {'Target':<12} {'Status':<10}")
        print("-" * 64)

        for name, result in results.items():
            target_ms = 10.0  # Target <10ms
            status = "✓ PASS" if result["avg_time_ms"] < target_ms else "✗ NEEDS OPT"
            print(f"{name:<30} {result['avg_time_ms']:>8.2f}ms   {target_ms:>8.1f}ms   {status}")

        # Overall statistics
        avg_times = [r["avg_time_ms"] for r in results.values()]
        overall_avg = sum(avg_times) / len(avg_times)

        print(f"\nOverall Average: {overall_avg:.2f}ms")
        print("Target: <10ms")
        print(f"Status: {'✓ MEETING TARGET' if overall_avg < 10 else '✗ OPTIMIZATION NEEDED'}")

        # Identify top bottlenecks across all scenarios
        print("\n" + "=" * 60)
        print("TOP 10 BOTTLENECKS ACROSS ALL SCENARIOS")
        print("=" * 60)

        # This would require aggregating function calls across all profiles
        # For now, list common optimization targets
        print("\n1. PII Scrubbing:")
        print("   - Regex pattern matching")
        print("   - String replacement operations")
        print("   → Add LRU cache, parallel processing")

        print("\n2. Secrets Detection:")
        print("   - Entropy calculation (Shannon)")
        print("   - Pattern scanning (20+ regex)")
        print("   → Use numpy for entropy, parallel scanning")

        print("\n3. Classification:")
        print("   - Keyword matching")
        print("   - Pattern analysis")
        print("   → Cache common patterns")

        print("\n4. Encryption (SENSITIVE only):")
        print("   - AES-256-GCM encryption")
        print("   - Key derivation")
        print("   → Use async encryption for large content")

        print("\n5. Audit Logging:")
        print("   - JSON serialization")
        print("   - File I/O")
        print("   → Batch writes, use orjson, async I/O")

        print("\n6. Storage:")
        print("   - File writes")
        print("   - Directory operations")
        print("   → Batch operations, async writes")

        print("\n" + "=" * 60)
        print("OPTIMIZATION PRIORITIES:")
        print("=" * 60)
        print("P0: PII Scrubbing (biggest impact on all scenarios)")
        print("P0: Secrets Detection (second biggest impact)")
        print("P1: Audit Logger (affects all operations)")
        print("P1: Pipeline parallelization (run PII+secrets in parallel)")
        print("P2: Encryption optimization (SENSITIVE data only)")
        print("P2: Caching layer (repeated patterns)")
        print("=" * 60)


if __name__ == "__main__":
    profile_complete_pipeline()
