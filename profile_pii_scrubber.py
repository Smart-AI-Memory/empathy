#!/usr/bin/env python
"""Performance profiling for PII Scrubber module

Profiles PII scrubbing performance to identify optimization targets.
Target: <3ms/KB (current: 3-5ms/KB)

Usage:
    python profile_pii_scrubber.py
"""

import cProfile
import io
import pstats
from pstats import SortKey

from empathy_llm_toolkit.security import PIIScrubber


def profile_pii_scrubbing():
    """Profile PII scrubbing with various content sizes"""
    scrubber = PIIScrubber()

    # Test content with various PII patterns
    test_contents = {
        "small_1kb": """
        Contact information:
        Email: john.doe@company.com
        Phone: (555) 123-4567
        SSN: 123-45-6789
        """
        * 10,  # ~1KB
        "medium_10kb": """
        Patient Records:
        Name: Jane Smith
        Email: jane.smith@hospital.com
        Phone: 555-987-6543
        MRN: 1234567
        Address: 123 Main St, Boston, MA 02101
        Credit Card: 4532-1234-5678-9010
        """
        * 100,  # ~10KB
        "large_100kb": """
        Healthcare Database Export:
        Patient: John Doe, MRN: 7654321
        Email: patient@email.com, Phone: (555) 111-2222
        Insurance: ABC123456789
        SSN: 987-65-4321
        IP Address: 192.168.1.100
        """
        * 1000,  # ~100KB
        "no_pii_1kb": """
        Technical documentation about Python programming.
        This content contains no PII and should use fast path.
        Standard code examples and best practices.
        """
        * 10,
    }

    print("=" * 60)
    print("PII Scrubber Performance Profiling")
    print("=" * 60)

    results = {}

    for name, content in test_contents.items():
        size_kb = len(content) / 1024
        print(f"\nProfiling: {name} ({size_kb:.2f} KB)")

        # Profile the scrubbing operation
        profiler = cProfile.Profile()
        profiler.enable()

        # Run scrubbing 100 times for statistical significance
        for _ in range(100):
            sanitized, detections = scrubber.scrub(content)

        profiler.disable()

        # Analyze results
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        ps.strip_dirs()
        ps.sort_stats(SortKey.CUMULATIVE)

        # Get top 10 functions
        ps.print_stats(10)

        results[name] = {
            "size_kb": size_kb,
            "stats": s.getvalue(),
            "detections": len(detections),
        }

        print(f"  PII Detections: {len(detections)}")
        print("  Top functions:")
        print(s.getvalue()[:500])

    # Summary report
    print("\n" + "=" * 60)
    print("PROFILING SUMMARY: PII Scrubber")
    print("=" * 60)

    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Size: {result['size_kb']:.2f} KB")
        print(f"  PII Found: {result['detections']}")
        print("  Top 3 Hotspots:")

        # Extract top 3 function names from stats
        lines = result["stats"].split("\n")
        for i, line in enumerate(lines[5:8]):  # Skip header, show top 3
            if line.strip():
                print(f"    {i + 1}. {line.strip()[:80]}")

    print("\n" + "=" * 60)
    print("Optimization Targets:")
    print("  1. Regex compilation and matching")
    print("  2. String replacement operations")
    print("  3. Pattern detection loops")
    print("  4. Add LRU cache for repeated patterns")
    print("  5. Add fast path for no-PII content")
    print("=" * 60)


if __name__ == "__main__":
    profile_pii_scrubbing()
