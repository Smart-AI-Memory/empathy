"""Example: EmpathyLLM with Phase 3 Security Integration

Demonstrates how to use EmpathyLLM with security controls:
- PII Scrubbing: Automatic detection and redaction
- Secrets Detection: Block requests with API keys/passwords
- Audit Logging: SOC2/HIPAA/GDPR compliant logging

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9
"""

import asyncio
import os
from pathlib import Path

from empathy_llm_toolkit.core import EmpathyLLM
from empathy_llm_toolkit.security import SecurityError


async def example_1_basic_security():
    """Example 1: Basic security enabled with default settings"""
    print("\n" + "=" * 60)
    print("Example 1: Basic Security (Default Settings)")
    print("=" * 60)

    # Initialize with security enabled
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=3,
        enable_security=True,  # Enable Phase 3 security
        security_config={
            "audit_log_dir": "./logs/example_security",
        },
    )

    # Example with PII in input
    print("\n1. Testing PII Scrubbing:")
    print("-" * 40)
    user_input = "My email is john.doe@example.com and phone is 555-123-4567"
    print(f"Original input: {user_input}")

    try:
        result = await llm.interact(
            user_id="demo_user@company.com",
            user_input=user_input,
            force_level=1,
        )

        print("✓ Request succeeded")
        print(f"  PII detected: {result['security']['pii_detected']}")
        print(f"  PII scrubbed: {result['security']['pii_scrubbed']}")
        print(f"  Secrets detected: {result['security']['secrets_detected']}")
    except Exception as e:
        print(f"✗ Error: {e}")


async def example_2_secrets_blocking():
    """Example 2: Secrets detection and blocking"""
    print("\n" + "=" * 60)
    print("Example 2: Secrets Detection & Blocking")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=2,
        enable_security=True,
        security_config={
            "audit_log_dir": "./logs/example_security",
            "block_on_secrets": True,  # Block requests with secrets
        },
    )

    # Example with API key in input - should be blocked
    print("\n1. Testing Secrets Blocking:")
    print("-" * 40)
    # Create a valid-looking Anthropic API key
    user_input = 'ANTHROPIC_API_KEY = "sk-ant-api03-' + "x" * 95 + '"'
    print("Input contains: API key pattern")

    try:
        await llm.interact(user_id="demo_user@company.com", user_input=user_input, force_level=2)
        print("✗ Request should have been blocked!")
    except SecurityError as e:
        print(f"✓ Request blocked as expected: {str(e)[:80]}...")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


async def example_3_log_without_blocking():
    """Example 3: Log secrets but don't block (for monitoring)"""
    print("\n" + "=" * 60)
    print("Example 3: Log Secrets Without Blocking")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=2,
        enable_security=True,
        security_config={
            "audit_log_dir": "./logs/example_security",
            "block_on_secrets": False,  # Log but don't block
        },
    )

    print("\n1. Testing Secrets Logging (without blocking):")
    print("-" * 40)
    user_input = "AWS_ACCESS_KEY_ID = AKIAIOSFODNN7EXAMPLE"
    print("Input contains: AWS access key pattern")

    try:
        result = await llm.interact(
            user_id="demo_user@company.com",
            user_input=user_input,
            force_level=2,
        )
        print("✓ Request succeeded (logged but not blocked)")
        print(f"  Secrets detected: {result['security']['secrets_detected']}")
        print("  Note: Security violation logged in audit trail")
    except Exception as e:
        print(f"✗ Error: {e}")


async def example_4_all_empathy_levels():
    """Example 4: Security works across all empathy levels"""
    print("\n" + "=" * 60)
    print("Example 4: Security Across All Empathy Levels")
    print("=" * 60)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=5,
        enable_security=True,
        security_config={
            "audit_log_dir": "./logs/example_security",
        },
    )

    test_cases = [
        ("Level 1 (Reactive): Contact me at user@example.com", 1),
        ("Level 2 (Guided): My phone is 555-123-4567", 2),
        ("Level 3 (Proactive): SSN: 123-45-6789", 3),
        ("Level 4 (Anticipatory): IP address: 192.168.1.1", 4),
        ("Level 5 (Systems): Email: admin@company.com", 5),
    ]

    print("\nTesting PII scrubbing at each level:")
    print("-" * 40)

    for user_input, level in test_cases:
        try:
            result = await llm.interact(
                user_id=f"demo_user_level_{level}",
                user_input=user_input,
                force_level=level,
            )
            print(
                f"Level {level}: ✓ PII={result['security']['pii_detected']}, "
                f"Secrets={result['security']['secrets_detected']}",
            )
        except Exception as e:
            print(f"Level {level}: ✗ Error: {e}")


async def example_5_custom_configuration():
    """Example 5: Custom security configuration"""
    print("\n" + "=" * 60)
    print("Example 5: Custom Security Configuration")
    print("=" * 60)

    security_config = {
        "audit_log_dir": "./logs/example_security",
        "block_on_secrets": True,
        "enable_pii_scrubbing": True,
        "enable_name_detection": False,  # Disable name detection (high false positive)
        "enable_audit_logging": True,
        "enable_console_logging": True,  # Enable console logging for debugging
    }

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=3,
        enable_security=True,
        security_config=security_config,
    )

    print("\nConfiguration:")
    print("-" * 40)
    for key, value in security_config.items():
        print(f"  {key}: {value}")

    print("\n1. Testing with custom config:")
    print("-" * 40)
    user_input = "Contact info: john@example.com, 555-123-4567"

    try:
        result = await llm.interact(
            user_id="demo_user@company.com",
            user_input=user_input,
            force_level=3,
        )
        print("✓ Request succeeded with custom config")
        print(f"  Security metadata: {result['security']}")
    except Exception as e:
        print(f"✗ Error: {e}")


async def example_6_backward_compatibility():
    """Example 6: Backward compatibility - security disabled by default"""
    print("\n" + "=" * 60)
    print("Example 6: Backward Compatibility (Security Disabled)")
    print("=" * 60)

    # Initialize WITHOUT security (default behavior)
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=2,
        # Note: enable_security defaults to False
    )

    print("\nSecurity status:")
    print("-" * 40)
    print(f"  Security enabled: {llm.enable_security}")
    print(f"  PII scrubber: {llm.pii_scrubber}")
    print(f"  Secrets detector: {llm.secrets_detector}")
    print(f"  Audit logger: {llm.audit_logger}")

    print("\n1. Testing without security:")
    print("-" * 40)
    # Input with PII - will NOT be scrubbed when security disabled
    user_input = "My email is test@example.com"

    try:
        result = await llm.interact(
            user_id="demo_user@company.com",
            user_input=user_input,
            force_level=2,
        )
        print("✓ Request succeeded without security")
        print(f"  'security' in result: {'security' in result}")
        print("  Note: Original behavior preserved - no scrubbing, no blocking")
    except Exception as e:
        print(f"✗ Error: {e}")


async def example_7_audit_log_inspection():
    """Example 7: Inspect audit logs"""
    print("\n" + "=" * 60)
    print("Example 7: Audit Log Inspection")
    print("=" * 60)

    log_dir = "./logs/example_security"

    # Create the directory if it doesn't exist
    Path(log_dir).mkdir(parents=True, exist_ok=True)

    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY", "test-key"),
        target_level=1,
        enable_security=True,
        security_config={"audit_log_dir": log_dir},
    )

    # Make a few requests to generate audit logs
    print("\n1. Generating audit logs:")
    print("-" * 40)

    test_inputs = [
        "Normal request without sensitive data",
        "Request with email: user@example.com",
        "Request with phone: 555-123-4567",
    ]

    for i, user_input in enumerate(test_inputs, 1):
        try:
            await llm.interact(user_id=f"audit_test_user_{i}", user_input=user_input, force_level=1)
            print(f"  {i}. ✓ Logged: {user_input[:40]}...")
        except Exception as e:
            print(f"  {i}. ✗ Error: {e}")

    # Check if audit log exists
    audit_log_path = Path(log_dir) / "audit.jsonl"
    if audit_log_path.exists():
        print("\n2. Audit log location:")
        print("-" * 40)
        print(f"  Path: {audit_log_path.absolute()}")
        print(f"  Size: {audit_log_path.stat().st_size} bytes")

        # Read and display first few log entries
        print("\n3. Sample log entries:")
        print("-" * 40)
        with open(audit_log_path) as f:
            import json

            for i, line in enumerate(f, 1):
                if i > 3:  # Only show first 3
                    break
                log_entry = json.loads(line)
                print(f"\n  Entry {i}:")
                print(f"    Event: {log_entry['event_type']}")
                print(f"    User: {log_entry['user_id']}")
                print(f"    Status: {log_entry['status']}")
                print(f"    Empathy Level: {log_entry['llm']['empathy_level']}")
                print(
                    f"    Security: PII={log_entry['security']['pii_detected']}, "
                    f"Secrets={log_entry['security']['secrets_detected']}",
                )
    else:
        print(f"\n✗ Audit log not found at: {audit_log_path}")


async def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("EmpathyLLM Phase 3 Security Integration Examples")
    print("=" * 60)
    print("\nThese examples demonstrate security features:")
    print("  - PII Scrubbing (email, phone, SSN, etc.)")
    print("  - Secrets Detection (API keys, passwords)")
    print("  - Audit Logging (SOC2/HIPAA/GDPR compliant)")
    print("  - Backward Compatibility (disabled by default)")

    # Note: Examples using actual LLM providers will need valid API keys
    print("\nNote: These examples use mock responses for demonstration.")
    print("To test with real LLM calls, set ANTHROPIC_API_KEY environment variable.")

    try:
        await example_1_basic_security()
        await example_2_secrets_blocking()
        await example_3_log_without_blocking()
        await example_4_all_empathy_levels()
        await example_5_custom_configuration()
        await example_6_backward_compatibility()
        await example_7_audit_log_inspection()
    except Exception as e:
        print(f"\n✗ Example execution error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Check audit logs at: ./logs/example_security/audit.jsonl")
    print("  2. Review test file: tests/test_empathy_llm_security.py")
    print("  3. Read docs: empathy_llm_toolkit/core.py docstrings")


if __name__ == "__main__":
    # Run examples
    asyncio.run(main())
