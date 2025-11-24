"""
Secure MemDocs Integration - Example Usage

Demonstrates Phase 2 enterprise privacy integration with:
- PII scrubbing
- Secrets detection
- Three-tier classification
- Encryption for SENSITIVE patterns
- Audit logging

Author: Empathy Framework Team
Version: 1.8.0-beta
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from empathy_llm_toolkit.security import SecureMemDocsIntegration, SecurityError


def example_basic_usage():
    """Example 1: Basic pattern storage with auto-classification"""
    print("\n=== Example 1: Basic Pattern Storage ===\n")

    # Initialize secure integration
    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    # Store a simple pattern
    content = """
    Standard Python sorting algorithm implementation:

    def quick_sort(arr):
        if len(arr) <= 1:
            return arr
        pivot = arr[len(arr) // 2]
        left = [x for x in arr if x < pivot]
        middle = [x for x in arr if x == pivot]
        right = [x for x in arr if x > pivot]
        return quick_sort(left) + middle + quick_sort(right)
    """

    result = integration.store_pattern(
        content=content,
        pattern_type="algorithm",
        user_id="developer@company.com",
    )

    print("Pattern stored successfully!")
    print(f"  Pattern ID: {result['pattern_id']}")
    print(f"  Classification: {result['classification']}")
    print(f"  PII removed: {result['sanitization_report']['pii_count']}")
    print(f"  Encrypted: {result['metadata']['encrypted']}")
    print(f"  Retention: {result['metadata']['retention_days']} days")

    return result["pattern_id"]


def example_pii_scrubbing():
    """Example 2: PII scrubbing in action"""
    print("\n=== Example 2: PII Scrubbing ===\n")

    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    # Content with PII
    content = """
    Contact Information:
    - Email: john.doe@example.com
    - Phone: 555-123-4567
    - SSN: 123-45-6789

    For support, call our team at support@company.com
    """

    result = integration.store_pattern(
        content=content,
        pattern_type="contact_info",
        user_id="hr@company.com",
    )

    print("Pattern stored with PII scrubbing:")
    print(f"  Pattern ID: {result['pattern_id']}")
    print(f"  PII removed: {result['sanitization_report']['pii_count']} items")
    for pii_item in result["sanitization_report"]["pii_removed"]:
        print(f"    - {pii_item['type']}")

    # Retrieve to see scrubbed content
    pattern = integration.retrieve_pattern(
        pattern_id=result["pattern_id"], user_id="hr@company.com"
    )

    print("\nRetrieved content (PII scrubbed):")
    print(pattern["content"][:200] + "...")

    return result["pattern_id"]


def example_secrets_blocking():
    """Example 3: Secrets detection blocks storage"""
    print("\n=== Example 3: Secrets Detection ===\n")

    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    # Content with secrets (WILL BE BLOCKED)
    content = """
    # Configuration
    ANTHROPIC_API_KEY = "sk-ant-api03-abc123xyz789..."
    OPENAI_API_KEY = "sk-proj-abc123xyz789..."
    DATABASE_URL = "postgres://user:password@localhost:5432/db"
    """

    try:
        integration.store_pattern(
            content=content,
            pattern_type="config",
            user_id="developer@company.com",
        )
        print("ERROR: Secrets should have been blocked!")
    except SecurityError as e:
        print("Storage blocked (as expected):")
        print(f"  Reason: {str(e)}")
        print("  Action: Secrets detected and storage prevented")
        print("  Audit: Security violation logged")


def example_healthcare_sensitive():
    """Example 4: Healthcare pattern with SENSITIVE classification"""
    print("\n=== Example 4: Healthcare Pattern (SENSITIVE) ===\n")

    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    # Healthcare content (auto-classified as SENSITIVE)
    content = """
    # Patient Vital Signs Monitoring Protocol

    Normal ranges:
    - Heart rate: 60-100 bpm
    - Blood pressure: 90/60 to 120/80 mmHg
    - Respiratory rate: 12-20 breaths/min
    - Temperature: 97-99°F (36.1-37.2°C)
    - Oxygen saturation: 95-100%

    Alert thresholds:
    - Heart rate < 50 or > 120 bpm
    - Systolic BP < 90 or > 180 mmHg
    - Oxygen saturation < 92%
    """

    result = integration.store_pattern(
        content=content,
        pattern_type="clinical_protocol",
        user_id="nurse@hospital.com",
    )

    print("Healthcare pattern stored:")
    print(f"  Pattern ID: {result['pattern_id']}")
    print(f"  Classification: {result['classification']} (auto-detected)")
    print(f"  Encrypted: {result['metadata']['encrypted']} (HIPAA compliance)")
    print(f"  Retention: {result['metadata']['retention_days']} days (HIPAA minimum)")
    print("  Access: Creator only (explicit permission required)")

    # Retrieve (only creator can access)
    pattern = integration.retrieve_pattern(
        pattern_id=result["pattern_id"], user_id="nurse@hospital.com"
    )

    print("\nPattern retrieved and decrypted successfully")
    print(f"  Content length: {len(pattern['content'])} chars")

    # Try to retrieve as different user (will be blocked)
    try:
        pattern = integration.retrieve_pattern(
            pattern_id=result["pattern_id"], user_id="other_user@hospital.com"
        )
        print("ERROR: Access should have been denied!")
    except Exception:
        print("\nAccess denied for different user (as expected):")
        print("  Reason: SENSITIVE patterns require explicit permission")

    return result["pattern_id"]


def example_list_patterns():
    """Example 5: List accessible patterns"""
    print("\n=== Example 5: List Patterns ===\n")

    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    # List patterns for user
    patterns = integration.list_patterns(user_id="developer@company.com")

    print(f"Accessible patterns: {len(patterns)}")
    for pattern in patterns:
        print(f"\n  Pattern: {pattern['pattern_id']}")
        print(f"    Type: {pattern['pattern_type']}")
        print(f"    Classification: {pattern['classification']}")
        print(f"    Created: {pattern['created_at']}")
        print(f"    Encrypted: {pattern['encrypted']}")


def example_statistics():
    """Example 6: Get storage statistics"""
    print("\n=== Example 6: Storage Statistics ===\n")

    integration = SecureMemDocsIntegration(
        storage_dir="./example_memdocs",
        audit_log_dir="./example_logs",
    )

    stats = integration.get_statistics()

    print("MemDocs Statistics:")
    print(f"  Total patterns: {stats['total_patterns']}")
    print("  By classification:")
    for classification, count in stats["by_classification"].items():
        print(f"    - {classification}: {count}")
    print(f"  Encrypted patterns: {stats['encrypted_count']}")
    print(f"  With PII scrubbed: {stats['with_pii_scrubbed']}")


def main():
    """Run all examples"""
    print("=" * 70)
    print("Secure MemDocs Integration - Example Usage")
    print("Phase 2: Enterprise Privacy Integration")
    print("=" * 70)

    try:
        # Example 1: Basic usage
        example_basic_usage()

        # Example 2: PII scrubbing
        example_pii_scrubbing()

        # Example 3: Secrets blocking
        example_secrets_blocking()

        # Example 4: Healthcare (SENSITIVE)
        example_healthcare_sensitive()

        # Example 5: List patterns
        example_list_patterns()

        # Example 6: Statistics
        example_statistics()

        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\n\nError running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
