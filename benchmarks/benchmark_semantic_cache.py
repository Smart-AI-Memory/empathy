#!/usr/bin/env python
"""Benchmark semantic cache performance with varying prompt similarity.

Tests:
1. Hash-only cache (baseline)
2. Hybrid cache with identical prompts (should match hash)
3. Hybrid cache with similar prompts (semantic matching test)

Generates transparent report with real data for marketing.
"""

import asyncio
import time
from pathlib import Path

from empathy_os.cache import create_cache
from empathy_os.workflows.code_review import CodeReviewWorkflow
from empathy_os.workflows.security_audit import SecurityAuditWorkflow

# Test cases with semantic variations
CODE_REVIEW_PROMPTS = {
    "original": """
diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -15,10 +15,15 @@ class AuthManager:
     def authenticate(self, username: str, password: str) -> bool:
         user = self.get_user(username)
         if user is None:
+            logger.warning(f"Failed login for {username}")
             return False
-        return user.check_password(password)
+        return user.verify_password(password)
""",
    "semantically_similar": """
diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -15,10 +15,15 @@ class AuthManager:
     def authenticate(self, username: str, password: str) -> bool:
         user = self.get_user(username)
         if user is None:
+            logger.warning(f"Login attempt failed for {username}")
             return False
-        return user.check_password(password)
+        return user.verify_password(password)
""",
    "very_similar": """
diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -15,10 +15,15 @@ class AuthManager:
     def authenticate(self, username: str, password: str) -> bool:
        user = self.get_user(username)
        if user is None:
+           logger.warning(f"Failed login for {username}")
           return False
-       return user.check_password(password)
+       return user.verify_password(password)
""",
}

SECURITY_TEST_FILES = {
    "original": """
import os

def run_command(user_input):
    # Command injection risk
    os.system(f"echo {user_input}")

def get_secret():
    password = "admin123"  # Hardcoded secret  # pragma: allowlist secret
    return password
""",
    "semantically_similar": """
import os

def execute_command(user_input):
    # Command injection vulnerability
    os.system(f"echo {user_input}")

def retrieve_secret():
    password = "admin123"  # Hardcoded credentials
    return password
""",
    "very_similar": """
import os

def run_command(user_input):
    # Command injection vulnerability
    os.system(f"echo {user_input}")

def get_secret():
    pwd = "admin123"  # Hardcoded password
    return pwd
""",
}


class BenchmarkResult:
    """Store detailed benchmark results."""

    def __init__(self, test_name: str, cache_type: str):
        self.test_name = test_name
        self.cache_type = cache_type
        self.runs = []

    def add_run(
        self, prompt_variant: str, cost: float, time: float, cache_hits: int, cache_misses: int
    ):
        self.runs.append(
            {
                "prompt": prompt_variant,
                "cost": cost,
                "time": time,
                "hits": cache_hits,
                "misses": cache_misses,
                "hit_rate": (
                    (cache_hits / (cache_hits + cache_misses) * 100)
                    if (cache_hits + cache_misses) > 0
                    else 0
                ),
            }
        )

    def get_summary(self):
        if not self.runs:
            return {}
        return {
            "total_runs": len(self.runs),
            "avg_cost": sum(r["cost"] for r in self.runs) / len(self.runs),
            "avg_time": sum(r["time"] for r in self.runs) / len(self.runs),
            "avg_hit_rate": sum(r["hit_rate"] for r in self.runs) / len(self.runs),
            "total_hits": sum(r["hits"] for r in self.runs),
            "total_misses": sum(r["misses"] for r in self.runs),
        }


async def benchmark_code_review_variants(cache, cache_type: str) -> BenchmarkResult:
    """Test code review with prompt variations."""
    result = BenchmarkResult("code-review", cache_type)

    print(f"🔍 Testing Code Review ({cache_type} cache)")
    print("  Testing 3 prompt variants:")
    print("    1. Original prompt")
    print("    2. Semantically similar (different wording)")
    print("    3. Very similar (whitespace differences)")
    print()

    workflow = CodeReviewWorkflow(use_crew=False, cache=cache, enable_cache=True)

    # Clear cache before test
    cache.clear()

    for idx, (variant_name, diff) in enumerate(CODE_REVIEW_PROMPTS.items(), 1):
        print(f"  ▶ Run {idx}: {variant_name}")
        start = time.time()
        r = await workflow.execute(diff=diff, files_changed=["src/auth.py"], is_core_module=False)
        elapsed = time.time() - start

        result.add_run(
            variant_name,
            r.cost_report.total_cost,
            elapsed,
            r.cost_report.cache_hits,
            r.cost_report.cache_misses,
        )

        print(f"    Cost: ${r.cost_report.total_cost:.6f}")
        print(f"    Time: {elapsed:.2f}s")
        print(
            f"    Cache: {r.cost_report.cache_hits} hits, {r.cost_report.cache_misses} misses ({r.cost_report.cache_hit_rate:.1f}% hit rate)"
        )
        print()

    return result


async def benchmark_security_audit_variants(cache, cache_type: str) -> BenchmarkResult:
    """Test security audit with file content variations."""
    result = BenchmarkResult("security-audit", cache_type)

    print(f"🔍 Testing Security Audit ({cache_type} cache)")
    print("  Testing 3 file variants:")
    print("    1. Original code")
    print("    2. Semantically similar (different function names)")
    print("    3. Very similar (variable name differences)")
    print()

    workflow = SecurityAuditWorkflow(cache=cache, enable_cache=True)

    # Clear cache before test
    cache.clear()

    # Create test directory
    test_dir = Path("/tmp/empathy_semantic_test")
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "app.py"

    try:
        for idx, (variant_name, code) in enumerate(SECURITY_TEST_FILES.items(), 1):
            # Write variant to file
            test_file.write_text(code)

            print(f"  ▶ Run {idx}: {variant_name}")
            start = time.time()
            r = await workflow.execute(target_path=str(test_dir))
            elapsed = time.time() - start

            result.add_run(
                variant_name,
                r.cost_report.total_cost,
                elapsed,
                r.cost_report.cache_hits,
                r.cost_report.cache_misses,
            )

            print(f"    Cost: ${r.cost_report.total_cost:.6f}")
            print(f"    Time: {elapsed:.2f}s")
            print(
                f"    Cache: {r.cost_report.cache_hits} hits, {r.cost_report.cache_misses} misses ({r.cost_report.cache_hit_rate:.1f}% hit rate)"
            )
            print()
    finally:
        # Cleanup
        test_file.unlink(missing_ok=True)
        test_dir.rmdir()

    return result


def generate_report(results: list[BenchmarkResult], output_file: str = "SEMANTIC_CACHE_REPORT.md"):
    """Generate markdown report comparing cache strategies."""
    from datetime import datetime

    report = f"""# Semantic Cache Benchmark Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Purpose:** Test hybrid cache semantic matching vs hash-only cache
**Test Method:** Run workflows with identical, similar, and very similar prompts

---

## Executive Summary

This benchmark tests whether semantic caching (hybrid mode) can match similar prompts that differ only in wording.

**Key Questions:**
1. Does hybrid cache match semantically similar prompts?
2. What's the hit rate improvement over hash-only cache?
3. Is the ~100ms similarity search worth it?

---

## Test Design

### Prompt Variations

**Code Review Test:**
- **Original:** "Failed login for {{username}}"
- **Semantically Similar:** "Login attempt failed for {{username}}"
- **Very Similar:** Same text, different whitespace

**Security Audit Test:**
- **Original:** `run_command()`, `get_secret()`, `password = "admin123"`
- **Semantically Similar:** `execute_command()`, `retrieve_secret()`, `password = "admin123"`
- **Very Similar:** `run_command()`, `get_secret()`, `pwd = "admin123"`

### Cache Strategies Tested

"""

    for result in results:
        summary = result.get_summary()
        if not summary:
            continue

        report += f"""
## {result.test_name.title()} - {result.cache_type.upper()} Cache

### Run Details

| Run | Prompt Variant | Cost | Time | Hits | Misses | Hit Rate |
|-----|----------------|------|------|------|--------|----------|
"""
        for idx, run in enumerate(result.runs, 1):
            report += f"| {idx} | {run['prompt']} | ${run['cost']:.6f} | {run['time']:.2f}s | {run['hits']} | {run['misses']} | {run['hit_rate']:.1f}% |\n"

        report += f"""
### Summary

- **Average Cost:** ${summary['avg_cost']:.6f}
- **Average Time:** {summary['avg_time']:.2f}s
- **Average Hit Rate:** {summary['avg_hit_rate']:.1f}%
- **Total Hits:** {summary['total_hits']}
- **Total Misses:** {summary['total_misses']}

"""

    # Comparison section
    hash_results = [r for r in results if r.cache_type == "hash"]
    hybrid_results = [r for r in results if r.cache_type == "hybrid"]

    if hash_results and hybrid_results:
        report += """---

## Comparison: Hash vs Hybrid Cache

"""
        for workflow_name in {r.test_name for r in results}:
            hash_result = next((r for r in hash_results if r.test_name == workflow_name), None)
            hybrid_result = next((r for r in hybrid_results if r.test_name == workflow_name), None)

            if hash_result and hybrid_result:
                hash_summary = hash_result.get_summary()
                hybrid_summary = hybrid_result.get_summary()

                hit_rate_improvement = hybrid_summary["avg_hit_rate"] - hash_summary["avg_hit_rate"]

                report += f"""### {workflow_name.title()}

| Metric | Hash-Only | Hybrid | Improvement |
|--------|-----------|--------|-------------|
| Avg Hit Rate | {hash_summary['avg_hit_rate']:.1f}% | {hybrid_summary['avg_hit_rate']:.1f}% | +{hit_rate_improvement:.1f}% |
| Avg Cost | ${hash_summary['avg_cost']:.6f} | ${hybrid_summary['avg_cost']:.6f} | ${hash_summary['avg_cost'] - hybrid_summary['avg_cost']:.6f} |
| Avg Time | {hash_summary['avg_time']:.2f}s | {hybrid_summary['avg_time']:.2f}s | {hash_summary['avg_time'] - hybrid_summary['avg_time']:.2f}s |

"""

    report += """---

## Key Findings

"""

    # Calculate findings
    if hybrid_results:
        hybrid_summaries = [r.get_summary() for r in hybrid_results if r.get_summary()]
        if hybrid_summaries:
            avg_hybrid_hit_rate = sum(s["avg_hit_rate"] for s in hybrid_summaries) / len(
                hybrid_summaries
            )
            report += f"""
### Semantic Matching Performance

**Average hit rate with hybrid cache:** {avg_hybrid_hit_rate:.1f}%

"""

            if avg_hybrid_hit_rate > 50:
                report += f"""✅ **VERIFIED:** Hybrid cache achieves {avg_hybrid_hit_rate:.1f}% hit rate on semantically similar prompts

**Marketing claim:** "Up to {avg_hybrid_hit_rate:.0f}% cache hit rate with semantic matching"
"""
            elif avg_hybrid_hit_rate > 30:
                report += f"""⚠️ **PARTIAL:** Hybrid cache achieves {avg_hybrid_hit_rate:.1f}% hit rate (moderate improvement)

**Marketing claim:** "~{avg_hybrid_hit_rate:.0f}% cache hit rate with semantic matching (varies by similarity)"
"""
            else:
                report += f"""❌ **UNDERWHELMING:** Hybrid cache only achieves {avg_hybrid_hit_rate:.1f}% hit rate

**Recommendation:** Do NOT claim "70% hit rate" - use actual measured value
"""

    report += """
---

## Honest Marketing Claims (Based on This Data)

### What We CAN Say

"""

    # Generate honest claims based on actual data
    for result in hybrid_results:
        summary = result.get_summary()
        if summary and summary["avg_hit_rate"] > 0:
            report += f"""✅ "{summary['avg_hit_rate']:.0f}% cache hit rate on {result.test_name} with semantic matching"
- Source: This benchmark, {result.test_name} hybrid cache results
- Evidence: {summary['total_hits']} hits, {summary['total_misses']} misses across {summary['total_runs']} runs

"""

    report += """
### What We Should NOT Say (Unless Verified)

❌ "70% cache hit rate with hybrid cache"
- Reality: Actual benchmark shows different results (see above)
- Only claim the measured values

---

## Reproducibility

Run this benchmark yourself:

```bash
pip install empathy-framework[cache]
python benchmark_semantic_cache.py
```

Expected runtime: ~5-10 minutes

---

*Generated by benchmark_semantic_cache.py*
"""

    Path(output_file).write_text(report)
    print(f"\n📊 Report generated: {output_file}")


async def main():
    print("=" * 80)
    print("  SEMANTIC CACHE BENCHMARK")
    print("=" * 80)
    print()
    print("This benchmark tests semantic caching with varying prompt similarity.")
    print("We'll test 2 workflows × 2 cache types × 3 prompt variants each.")
    print()
    print("Expected runtime: ~5-10 minutes")
    print()
    print("Starting benchmark...")
    print()

    results = []

    # Test 1: Hash-only cache (baseline)
    print("=" * 80)
    print("  PHASE 1: HASH-ONLY CACHE (BASELINE)")
    print("=" * 80)
    print()

    hash_cache = create_cache(cache_type="hash")

    try:
        r = await benchmark_code_review_variants(hash_cache, "hash")
        results.append(r)
    except Exception as e:
        print(f"❌ Error in code review (hash): {e}\n")

    try:
        r = await benchmark_security_audit_variants(hash_cache, "hash")
        results.append(r)
    except Exception as e:
        print(f"❌ Error in security audit (hash): {e}\n")

    # Test 2: Hybrid cache (semantic matching)
    print("=" * 80)
    print("  PHASE 2: HYBRID CACHE (SEMANTIC MATCHING)")
    print("=" * 80)
    print()

    hybrid_cache = create_cache(cache_type="hybrid")

    try:
        r = await benchmark_code_review_variants(hybrid_cache, "hybrid")
        results.append(r)
    except Exception as e:
        print(f"❌ Error in code review (hybrid): {e}\n")

    try:
        r = await benchmark_security_audit_variants(hybrid_cache, "hybrid")
        results.append(r)
    except Exception as e:
        print(f"❌ Error in security audit (hybrid): {e}\n")

    # Generate report
    print("=" * 80)
    print("  GENERATING REPORT")
    print("=" * 80)
    generate_report(results)

    print("\n✅ Benchmark complete!")
    print("\nResults:")
    for r in results:
        summary = r.get_summary()
        if summary:
            print(f"  {r.test_name} ({r.cache_type}): {summary['avg_hit_rate']:.1f}% avg hit rate")
    print("\nFull report: SEMANTIC_CACHE_REPORT.md")


if __name__ == "__main__":
    asyncio.run(main())
