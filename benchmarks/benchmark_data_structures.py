"""Benchmark data structure optimizations.

This script measures performance improvements from O(n) to O(1) lookups.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def benchmark_list_membership(sizes: list[int] = [100, 1000, 10000]) -> None:
    """Benchmark list vs set membership testing."""
    print("=" * 70)
    print("BENCHMARK: List vs Set Membership Testing")
    print("=" * 70)

    for size in sizes:
        # Setup
        items_list = list(range(size))
        items_set = set(range(size))
        test_item = size - 1  # Worst case: last item

        # List membership (O(n))
        start = time.perf_counter()
        for _ in range(1000):
            _ = test_item in items_list
        list_time = time.perf_counter() - start

        # Set membership (O(1))
        start = time.perf_counter()
        for _ in range(1000):
            _ = test_item in items_set
        set_time = time.perf_counter() - start

        speedup = list_time / set_time if set_time > 0 else float("inf")

        print(f"\nSize: {size:,} items (1000 lookups)")
        print(f"  List: {list_time*1000:.2f}ms")
        print(f"  Set:  {set_time*1000:.2f}ms")
        print(f"  Speedup: {speedup:.1f}x faster")


def benchmark_list_index(sizes: list[int] = [100, 1000, 10000]) -> None:
    """Benchmark list.index() vs dict lookup."""
    print("\n" + "=" * 70)
    print("BENCHMARK: list.index() vs Dict Lookup")
    print("=" * 70)

    for size in sizes:
        # Setup
        items_list = [{"id": i, "value": f"item_{i}"} for i in range(size)]
        items_dict = {i: items_list[i] for i in range(size)}
        search_id = size - 1  # Worst case

        # List.index() approach (O(n))
        start = time.perf_counter()
        for _ in range(100):
            _ = next((item for item in items_list if item["id"] == search_id), None)
        list_time = time.perf_counter() - start

        # Dict lookup (O(1))
        start = time.perf_counter()
        for _ in range(100):
            _ = items_dict.get(search_id)
        dict_time = time.perf_counter() - start

        speedup = list_time / dict_time if dict_time > 0 else float("inf")

        print(f"\nSize: {size:,} items (100 lookups)")
        print(f"  List.index(): {list_time*1000:.2f}ms")
        print(f"  Dict.get():   {dict_time*1000:.2f}ms")
        print(f"  Speedup: {speedup:.1f}x faster")


def benchmark_role_constants() -> None:
    """Benchmark role checking with list vs set constants."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Role Constants (List vs Set)")
    print("=" * 70)

    # Simulate trust_building.py patterns
    EXECUTIVE_ROLES_LIST = ["executive", "manager", "director"]
    EXECUTIVE_ROLES_SET = {"executive", "manager", "director"}

    test_roles = ["executive", "developer", "analyst", "manager", "engineer"] * 1000

    # List membership (O(n) per check)
    start = time.perf_counter()
    for role in test_roles:
        _ = role in EXECUTIVE_ROLES_LIST
    list_time = time.perf_counter() - start

    # Set membership (O(1) per check)
    start = time.perf_counter()
    for role in test_roles:
        _ = role in EXECUTIVE_ROLES_SET
    set_time = time.perf_counter() - start

    speedup = list_time / set_time if set_time > 0 else float("inf")

    print(f"\n{len(test_roles):,} role checks")
    print(f"  List: {list_time*1000:.2f}ms")
    print(f"  Set:  {set_time*1000:.2f}ms")
    print(f"  Speedup: {speedup:.1f}x faster")


def benchmark_verdict_merging() -> None:
    """Benchmark severity order list.index() vs dict lookup."""
    print("\n" + "=" * 70)
    print("BENCHMARK: Verdict Merging (list.index() vs dict)")
    print("=" * 70)

    severity_order_list = ["reject", "request_changes", "approve_with_suggestions", "approve"]
    severity_order_dict = {s: i for i, s in enumerate(severity_order_list)}

    verdicts = [
        ("reject", "approve"),
        ("request_changes", "approve_with_suggestions"),
        ("approve", "approve"),
    ] * 1000

    # Using list.index() (O(n))
    start = time.perf_counter()
    for v1, v2 in verdicts:
        idx1 = severity_order_list.index(v1) if v1 in severity_order_list else 3
        idx2 = severity_order_list.index(v2) if v2 in severity_order_list else 3
        _ = severity_order_list[min(idx1, idx2)]
    list_time = time.perf_counter() - start

    # Using dict lookup (O(1))
    start = time.perf_counter()
    for v1, v2 in verdicts:
        idx1 = severity_order_dict.get(v1, 3)
        idx2 = severity_order_dict.get(v2, 3)
        _ = severity_order_list[min(idx1, idx2)]
    dict_time = time.perf_counter() - start

    speedup = list_time / dict_time if dict_time > 0 else float("inf")

    print(f"\n{len(verdicts):,} verdict merges")
    print(f"  list.index(): {list_time*1000:.2f}ms")
    print(f"  dict.get():   {dict_time*1000:.2f}ms")
    print(f"  Speedup: {speedup:.1f}x faster")


if __name__ == "__main__":
    print("\n🚀 Data Structure Optimization Benchmarks")
    print("Testing O(n) vs O(1) lookup patterns\n")

    benchmark_list_membership()
    benchmark_list_index()
    benchmark_role_constants()
    benchmark_verdict_merging()

    print("\n" + "=" * 70)
    print("✅ Benchmarks complete!")
    print("=" * 70)
