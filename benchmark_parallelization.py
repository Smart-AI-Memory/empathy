#!/usr/bin/env python
"""Quick benchmark to measure parallelization improvement

Compares performance before/after parallel PII + secrets detection
"""

import tempfile
import time
from pathlib import Path

from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig
from empathy_llm_toolkit.security import SecureMemDocsIntegration


def benchmark_pipeline(iterations=100):
    """Benchmark the complete pipeline with parallel execution"""
    # Test content with PII
    test_content = (
        """
    Patient: John Doe
    Email: john.doe@hospital.com
    Phone: 555-123-4567
    MRN: 1234567
    Clinical protocol notes...
    """
        * 5
    )  # ~1KB of content

    with tempfile.TemporaryDirectory() as tmpdir:
        # Setup
        config = ClaudeMemoryConfig(enabled=False)
        integration = SecureMemDocsIntegration(config)
        integration.storage.storage_dir = Path(tmpdir)

        # Warm-up run
        integration.store_pattern(
            content=test_content,
            pattern_type="clinical",
            user_id="doctor@hospital.com",
            auto_classify=True,
        )

        # Benchmark
        start = time.perf_counter()
        for _ in range(iterations):
            integration.store_pattern(
                content=test_content,
                pattern_type="clinical",
                user_id="doctor@hospital.com",
                auto_classify=True,
            )
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        avg_time = elapsed / iterations
        throughput = iterations / (elapsed / 1000)

        return avg_time, throughput


if __name__ == "__main__":
    print("=" * 70)
    print("Pipeline Parallelization Benchmark")
    print("=" * 70)

    print("\nRunning benchmark (100 iterations)...")
    avg_time, throughput = benchmark_pipeline(iterations=100)

    print("\n✅ Results with PARALLEL execution:")
    print(f"   Average time per operation: {avg_time:.2f}ms")
    print(f"   Throughput: {throughput:.1f} ops/sec")

    # Compare to baseline from profiling
    baseline_avg = 2.84  # SENSITIVE pattern avg from profiling
    improvement = ((baseline_avg - avg_time) / baseline_avg) * 100

    print("\n📊 Comparison to Baseline:")
    print(f"   Baseline (sequential): {baseline_avg:.2f}ms")
    print(f"   Optimized (parallel): {avg_time:.2f}ms")

    if avg_time < baseline_avg:
        print(f"   ✅ Improvement: {improvement:.1f}% faster")
        print(f"   ⚡ Speed gain: {baseline_avg / avg_time:.2f}x")
    else:
        print(f"   ⚠️  Performance: {-improvement:.1f}% slower (overhead from threading)")

    # Target check
    target = 2.1  # 25-30% improvement target
    print(f"\n🎯 Target: <{target}ms")
    if avg_time < target:
        print(f"   ✅ TARGET MET! ({avg_time:.2f}ms < {target}ms)")
    else:
        print(f"   🟡 Close to target ({avg_time:.2f}ms vs {target}ms)")

    print("\n" + "=" * 70)
