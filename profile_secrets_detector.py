#!/usr/bin/env python
"""Performance profiling for Secrets Detector module

Profiles secrets detection performance to identify optimization targets.
Target: <8ms/KB (current: 10-20ms/KB)

Usage:
    python profile_secrets_detector.py
"""

import cProfile
import io
import pstats
from pstats import SortKey

from empathy_llm_toolkit.security import SecretsDetector


def profile_secrets_detection():
    """Profile secrets detection with various content sizes"""
    detector = SecretsDetector()

    # Test content with various secret patterns
    test_contents = {
        "api_keys_1kb": """
        # Configuration file
        ANTHROPIC_API_KEY=sk-ant-api03-abc123xyz789def456ghi789jkl012mno345
        OPENAI_API_KEY=sk-proj-abc123xyz789def456ghi789jkl012
        AWS_SECRET_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        """
        * 10,
        "passwords_10kb": """
        Database credentials:
        username: admin
        password: SuperSecret123!
        db_password: P@ssw0rd2024
        api_secret: my-secret-key-12345
        """
        * 200,
        "mixed_secrets_50kb": """
        Application secrets:
        STRIPE_SECRET_KEY=sk_live_abc123xyz789
        JWT_SECRET=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
        GITHUB_TOKEN=ghp_abc123xyz789def456ghi789jkl012
        PRIVATE_KEY=-----BEGIN RSA PRIVATE KEY-----
        MIIEpAIBAAKCAQEA1234567890abcdef
        -----END RSA PRIVATE KEY-----
        """
        * 100,
        "high_entropy_content": """
        Random data with high entropy:
        abc123xyz789def456ghi789jkl012mno345pqr678
        zxcvbnmasdfghjklqwertyuiop1234567890
        """
        * 200,
        "no_secrets_clean": """
        Clean code with no secrets:
        def calculate_total(items):
            return sum(item.price for item in items)

        This is normal application code.
        """
        * 50,
    }

    print("=" * 60)
    print("Secrets Detector Performance Profiling")
    print("=" * 60)

    results = {}

    for name, content in test_contents.items():
        size_kb = len(content) / 1024
        print(f"\nProfiling: {name} ({size_kb:.2f} KB)")

        # Profile the detection operation
        profiler = cProfile.Profile()
        profiler.enable()

        # Run detection 50 times for statistical significance
        for _ in range(50):
            detections = detector.detect(content)

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

        print(f"  Secrets Found: {len(detections)}")
        print("  Top functions:")
        print(s.getvalue()[:500])

    # Summary report
    print("\n" + "=" * 60)
    print("PROFILING SUMMARY: Secrets Detector")
    print("=" * 60)

    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  Size: {result['size_kb']:.2f} KB")
        print(f"  Secrets Found: {result['detections']}")
        print("  Top 3 Hotspots:")

        # Extract top 3 function names from stats
        lines = result["stats"].split("\n")
        for i, line in enumerate(lines[5:8]):  # Skip header, show top 3
            if line.strip():
                print(f"    {i + 1}. {line.strip()[:80]}")

    print("\n" + "=" * 60)
    print("Optimization Targets:")
    print("  1. Entropy calculation (Shannon entropy)")
    print("  2. Regex pattern matching (20+ patterns)")
    print("  3. String scanning and analysis")
    print("  4. Use numpy for faster entropy calculation")
    print("  5. Add parallel scanning for large content")
    print("  6. Cache entropy results with LRU cache")
    print("=" * 60)


if __name__ == "__main__":
    profile_secrets_detection()
