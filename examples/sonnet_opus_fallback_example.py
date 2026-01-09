"""Example: Sonnet 4.5 → Opus 4.5 Intelligent Fallback

Demonstrates how to use the intelligent fallback system that automatically
tries Sonnet 4.5 first and upgrades to Opus 4.5 when needed.

This can save up to 80% on API costs while maintaining high quality.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

# Load .env file first
try:
    from dotenv import load_dotenv

    load_dotenv()  # Load environment variables from .env
except ImportError:
    pass  # dotenv not installed, continue anyway

import asyncio
from datetime import datetime, timedelta

from empathy_os.models.empathy_executor import EmpathyLLMExecutor
from empathy_os.models.fallback import SONNET_TO_OPUS_FALLBACK, ResilientExecutor
from empathy_os.models.telemetry import TelemetryAnalytics, get_telemetry_store


async def example_basic_fallback():
    """Basic example: Automatic Sonnet → Opus fallback."""
    print("=" * 60)
    print("Example 1: Basic Sonnet → Opus Fallback")
    print("=" * 60)

    # Get API key from environment (Option 2: explicit passing)
    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("⚠️  ANTHROPIC_API_KEY not found in environment")
        print("   Please set it in your .env file or export it.")
        return

    # Create base executor with explicit API key
    base_executor = EmpathyLLMExecutor(
        provider="anthropic", api_key=api_key  # Explicitly pass the API key
    )

    # Wrap with resilient fallback
    executor = ResilientExecutor(
        executor=base_executor,
        fallback_policy=SONNET_TO_OPUS_FALLBACK,
    )

    # Make a call - will try Sonnet 4.5 first
    print("\nCalling LLM with fallback enabled...")
    response = await executor.run(
        task_type="code_review",
        prompt="Review this Python code for security issues:\n\ndef process_user_input(data):\n    return eval(data)",
    )

    # Check which model was used
    if response.metadata.get("fallback_used"):
        print("✅ Fallback triggered: Upgraded to Opus 4.5")
        print(f"   Reason: {response.metadata.get('fallback_chain')}")
    else:
        print("✅ Sonnet 4.5 succeeded (no fallback needed)")

    print(f"\nResponse: {response.content[:200]}...")


async def example_with_analytics():
    """Example: Track cost savings over time."""
    print("\n" + "=" * 60)
    print("Example 2: Cost Savings Analytics")
    print("=" * 60)

    # Get telemetry store
    store = get_telemetry_store()
    analytics = TelemetryAnalytics(store)

    # Analyze last 7 days
    since = datetime.utcnow() - timedelta(days=7)
    stats = analytics.sonnet_opus_fallback_analysis(since=since)

    if stats["total_calls"] == 0:
        print("\n⚠️  No Sonnet/Opus calls found in the last 7 days.")
        print("   Run some workflows first, then check back!")
        return

    # Display results
    print("\n📊 Fallback Performance (last 7 days):")
    print(f"   Total Calls: {stats['total_calls']}")
    print(f"   Sonnet Attempts: {stats['sonnet_attempts']}")
    print(f"   Sonnet Success Rate: {stats['success_rate_sonnet']:.1f}%")
    print(f"   Opus Fallbacks: {stats['opus_fallbacks']}")
    print(f"   Fallback Rate: {stats['fallback_rate']:.1f}%")

    print("\n💰 Cost Savings:")
    print(f"   Actual Cost: ${stats['actual_cost']:.2f}")
    print(f"   Always-Opus Cost: ${stats['always_opus_cost']:.2f}")
    print(f"   Savings: ${stats['savings']:.2f} ({stats['savings_percent']:.1f}%)")

    # Recommendation
    if stats["fallback_rate"] < 5:
        print(f"\n✅ Excellent! Sonnet handles {100 - stats['fallback_rate']:.1f}% of tasks.")
    elif stats["fallback_rate"] < 15:
        print(f"\n⚠️  Moderate fallback rate ({stats['fallback_rate']:.1f}%).")
    else:
        print(f"\n❌ High fallback rate ({stats['fallback_rate']:.1f}%).")
        print("   Consider using Opus directly for complex tasks.")


async def example_custom_retry():
    """Example: Custom retry configuration."""
    print("\n" + "=" * 60)
    print("Example 3: Custom Retry Configuration")
    print("=" * 60)

    import os

    from empathy_os.models.fallback import RetryPolicy

    # Get API key
    api_key = os.getenv("ANTHROPIC_API_KEY")

    # Create custom retry policy
    custom_retry = RetryPolicy(
        max_retries=2,  # Only 2 retries per model
        initial_delay_ms=500,  # Start with 500ms
        exponential_backoff=True,  # Double delay each time
    )

    base_executor = EmpathyLLMExecutor(provider="anthropic", api_key=api_key)

    _executor = ResilientExecutor(
        executor=base_executor,
        fallback_policy=SONNET_TO_OPUS_FALLBACK,
        retry_policy=custom_retry,
    )

    print("\n✅ Created executor with custom retry policy:")
    print(f"   Max retries: {custom_retry.max_retries}")
    print(f"   Initial delay: {custom_retry.initial_delay_ms}ms")
    print(f"   Exponential backoff: {custom_retry.exponential_backoff}")
    # In production: response = await _executor.run(task_type="...", prompt="...")


async def example_direct_opus():
    """Example: When to use Opus directly."""
    print("\n" + "=" * 60)
    print("Example 4: Direct Opus Usage (No Fallback)")
    print("=" * 60)

    # For tasks you know need Opus, use it directly
    _executor = EmpathyLLMExecutor(provider="anthropic", default_tier="premium")
    # In production: response = await _executor.run(task_type="complex_task", prompt="...")

    print("\n✅ Created executor using Opus 4.5 directly:")
    print("   Provider: anthropic")
    print("   Tier: premium (Opus 4.5)")
    print("   Use when: Task complexity requires Opus-level reasoning")
    print("   Benefit: Avoids retry overhead, faster response")


async def example_circuit_breaker():
    """Example: Circuit breaker status."""
    print("\n" + "=" * 60)
    print("Example 5: Circuit Breaker Status")
    print("=" * 60)

    import os

    api_key = os.getenv("ANTHROPIC_API_KEY")

    base_executor = EmpathyLLMExecutor(provider="anthropic", api_key=api_key)
    executor = ResilientExecutor(
        executor=base_executor,
        fallback_policy=SONNET_TO_OPUS_FALLBACK,
    )

    # Check circuit breaker status
    status = executor.circuit_breaker.get_status()

    if not status:
        print("\n✅ Circuit breaker: All clear (no failures)")
    else:
        print("\n⚠️  Circuit breaker status:")
        for provider_tier, state in status.items():
            print(f"\n   {provider_tier}:")
            print(f"      Failures: {state['failure_count']}")
            print(f"      Open: {state['is_open']}")
            if state["last_failure"]:
                print(f"      Last failure: {state['last_failure']}")

    # Tip
    print("\n💡 Tip: Circuit breaker protects against cascading failures")
    print("   After 5 consecutive failures, routes to fallback for 60s")


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Sonnet 4.5 → Opus 4.5 Intelligent Fallback Examples")
    print("=" * 60)

    # Run examples
    await example_basic_fallback()
    await example_with_analytics()
    await example_custom_retry()
    await example_direct_opus()
    await example_circuit_breaker()

    # Final tip
    print("\n" + "=" * 60)
    print("💡 Pro Tips:")
    print("=" * 60)
    print("1. Check fallback analytics weekly:")
    print("   python -m empathy_os.telemetry.cli sonnet-opus-analysis")
    print()
    print("2. Aim for < 5% fallback rate for optimal savings")
    print()
    print("3. Use Opus directly for known complex tasks")
    print()
    print("4. Monitor circuit breaker to detect systemic issues")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
