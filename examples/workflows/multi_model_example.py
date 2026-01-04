"""Multi-Model Architecture Example

Demonstrates the unified multi-model architecture including:
- Model Registry usage
- Task-based routing
- Telemetry collection and analysis
- Fallback policies and resilient execution
- Configuration validation

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import tempfile
from datetime import datetime

# Model Registry imports
from empathy_os.models import (  # Registry; Validation; Fallback; Telemetry; Executor; Tasks
    CircuitBreaker,
    ConfigValidator,
    ExecutionContext,
    FallbackPolicy,
    FallbackStrategy,
    LLMCallRecord,
    MockLLMExecutor,
    ResilientExecutor,
    RetryPolicy,
    TelemetryAnalytics,
    TelemetryStore,
    WorkflowRunRecord,
    get_all_models,
    get_all_tasks,
    get_model,
    get_pricing_for_model,
    get_tier_for_task,
)


def demo_model_registry():
    """Demonstrate the unified model registry."""
    print("\n" + "=" * 60)
    print("DEMO: Unified Model Registry")
    print("=" * 60)

    # Get all models
    all_models = get_all_models()
    print(f"\nRegistered providers: {list(all_models.keys())}")

    # Get specific model
    haiku = get_model("anthropic", "cheap")
    print(f"\nAnthropic cheap tier: {haiku.id}")
    print(f"  - Input cost: ${haiku.input_cost_per_million}/M tokens")
    print(f"  - Output cost: ${haiku.output_cost_per_million}/M tokens")
    print(f"  - Max tokens: {haiku.max_tokens}")

    # Pricing lookup
    pricing = get_pricing_for_model("claude-sonnet-4-20250514")
    if pricing:
        print("\nPricing for Sonnet 4:")
        print(f"  - Input: ${pricing['input']}/M")
        print(f"  - Output: ${pricing['output']}/M")

    # Compare costs across providers
    print("\n\nCost comparison for 100k input / 20k output tokens:")
    print("-" * 50)

    for provider in ["anthropic", "openai", "ollama"]:
        model = get_model(provider, "capable")
        if model:
            input_cost = (100000 / 1_000_000) * model.input_cost_per_million
            output_cost = (20000 / 1_000_000) * model.output_cost_per_million
            total = input_cost + output_cost
            print(f"  {provider:12} ({model.id}): ${total:.4f}")


def demo_task_routing():
    """Demonstrate task-based model routing."""
    print("\n" + "=" * 60)
    print("DEMO: Task-Based Model Routing")
    print("=" * 60)

    # Show all tasks by tier
    all_tasks = get_all_tasks()
    for tier_name, tasks in all_tasks.items():
        print(f"\n{tier_name.upper()} tier tasks ({len(tasks)}):")
        for task in sorted(tasks)[:5]:
            print(f"  - {task}")
        if len(tasks) > 5:
            print(f"  ... and {len(tasks) - 5} more")

    # Route specific tasks
    print("\n\nTask routing examples:")
    print("-" * 40)

    example_tasks = [
        "summarize",  # cheap
        "classify",  # cheap
        "fix_bug",  # capable
        "review_security",  # capable
        "coordinate",  # premium
        "architectural_decision",  # premium
    ]

    for task in example_tasks:
        tier = get_tier_for_task(task)
        model = get_model("anthropic", tier.value)
        print(f"  {task:25} -> {tier.value:8} -> {model.id}")


def demo_mock_executor():
    """Demonstrate the LLMExecutor interface with mock."""
    print("\n" + "=" * 60)
    print("DEMO: LLMExecutor Interface (Mock)")
    print("=" * 60)

    async def run_mock_executor():
        # Create mock executor
        executor = MockLLMExecutor(
            default_response="This is a mock response for testing.",
            default_model="mock-claude-3",
        )

        # Execute different task types
        tasks = ["summarize", "fix_bug", "coordinate"]

        for task_type in tasks:
            context = ExecutionContext(
                workflow_name="demo_workflow",
                step_name=f"{task_type}_step",
                user_id="demo_user",
            )

            response = await executor.run(
                task_type=task_type,
                prompt=f"Please {task_type} this content...",
                context=context,
            )

            print(f"\nTask: {task_type}")
            print(f"  Tier used: {response.tier_used.value}")
            print(f"  Model: {response.model_used}")
            print(f"  Tokens: {response.total_tokens}")

        # Show call history
        print(f"\nTotal calls recorded: {len(executor.call_history)}")

    asyncio.run(run_mock_executor())


def demo_telemetry():
    """Demonstrate telemetry collection and analytics."""
    print("\n" + "=" * 60)
    print("DEMO: Telemetry & Analytics")
    print("=" * 60)

    with tempfile.TemporaryDirectory() as tmpdir:
        store = TelemetryStore(storage_dir=tmpdir)

        # Simulate workflow runs
        workflows = [
            ("code_review", "anthropic", "capable", 0.05),
            ("code_review", "anthropic", "capable", 0.04),
            ("deploy", "openai", "cheap", 0.01),
            ("analysis", "anthropic", "premium", 0.12),
            ("triage", "anthropic", "cheap", 0.002),
        ]

        print("\nRecording LLM calls...")
        for i, (wf, provider, tier, cost) in enumerate(workflows):
            record = LLMCallRecord(
                call_id=f"call-{i}",
                timestamp=datetime.now().isoformat(),
                workflow_name=wf,
                step_name="main",
                task_type="fix_bug" if tier == "capable" else "summarize",
                provider=provider,
                model_id=f"{provider}-model",
                tier=tier,
                input_tokens=int(cost * 100000),
                output_tokens=int(cost * 20000),
                estimated_cost=cost,
                latency_ms=int(cost * 10000),
            )
            store.log_call(record)
            print(f"  Recorded: {wf} ({provider}/{tier}) - ${cost:.4f}")

        # Also add workflow runs for analytics
        for i, (wf, cost) in enumerate(
            [("code_review", 0.09), ("deploy", 0.01), ("analysis", 0.12), ("triage", 0.002)],
        ):
            run = WorkflowRunRecord(
                run_id=f"run-{i}",
                workflow_name=wf,
                started_at=datetime.now().isoformat(),
                completed_at=datetime.now().isoformat(),
                total_cost=cost,
                baseline_cost=cost * 3,  # Premium would cost 3x
                savings=cost * 2,
                total_input_tokens=int(cost * 100000),
                total_output_tokens=int(cost * 20000),
                success=True,
            )
            store.log_workflow(run)

        # Run analytics
        analytics = TelemetryAnalytics(store)

        print("\n\nTop expensive workflows:")
        print("-" * 40)
        for wf in analytics.top_expensive_workflows(n=3):
            print(f"  {wf['workflow_name']}: ${wf['total_cost']:.4f}")

        print("\n\nProvider usage summary:")
        print("-" * 40)
        for provider, stats in analytics.provider_usage_summary().items():
            print(f"  {provider}:")
            print(f"    Calls: {stats['call_count']}")
            print(f"    Cost: ${stats['total_cost']:.4f}")

        print("\n\nCost savings report:")
        print("-" * 40)
        report = analytics.cost_savings_report()
        print(f"  Actual cost: ${report['total_actual_cost']:.4f}")
        print(f"  Baseline (all premium): ${report['total_baseline_cost']:.4f}")
        print(f"  Savings: ${report['total_savings']:.4f} ({report['savings_percent']:.1f}%)")


def demo_fallback_policies():
    """Demonstrate fallback policies and circuit breaker."""
    print("\n" + "=" * 60)
    print("DEMO: Fallback Policies")
    print("=" * 60)

    # Same tier, different provider
    policy1 = FallbackPolicy(
        primary_provider="anthropic",
        primary_tier="capable",
        strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
    )

    print("\nStrategy: SAME_TIER_DIFFERENT_PROVIDER")
    print("Primary: anthropic/capable")
    print("Fallback chain:")
    for step in policy1.get_fallback_chain():
        print(f"  -> {step.provider}/{step.tier} ({step.model_id})")

    # Cheaper tier, same provider
    policy2 = FallbackPolicy(
        primary_provider="anthropic",
        primary_tier="premium",
        strategy=FallbackStrategy.CHEAPER_TIER_SAME_PROVIDER,
    )

    print("\nStrategy: CHEAPER_TIER_SAME_PROVIDER")
    print("Primary: anthropic/premium")
    print("Fallback chain:")
    for step in policy2.get_fallback_chain():
        print(f"  -> {step.provider}/{step.tier}")

    # Circuit breaker demo
    print("\n\nCircuit Breaker Demo:")
    print("-" * 40)

    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout_seconds=60)

    print(f"Initial state - anthropic available: {breaker.is_available('anthropic')}")

    # Simulate failures
    for i in range(3):
        breaker.record_failure("anthropic")
        print(f"After failure {i + 1}: available = {breaker.is_available('anthropic')}")

    print(f"\nCircuit status: {breaker.get_status()}")

    # Reset
    breaker.reset("anthropic")
    print(f"After reset: available = {breaker.is_available('anthropic')}")


def demo_resilient_executor():
    """Demonstrate resilient execution with fallbacks."""
    print("\n" + "=" * 60)
    print("DEMO: Resilient Executor")
    print("=" * 60)

    async def run_resilient():
        # Create executor with custom policies
        executor = ResilientExecutor(
            fallback_policy=FallbackPolicy(
                primary_provider="anthropic",
                primary_tier="capable",
                strategy=FallbackStrategy.SAME_TIER_DIFFERENT_PROVIDER,
            ),
            retry_policy=RetryPolicy(
                max_retries=2,
                initial_delay_ms=100,
                exponential_backoff=True,
            ),
        )

        # Successful call
        async def mock_success(*args, **kwargs):
            return f"Success from {kwargs.get('provider')}"

        print("\nScenario 1: Successful primary call")
        result, metadata = await executor.execute_with_fallback(mock_success)
        print(f"  Result: {result}")
        print(f"  Provider: {metadata['final_provider']}")
        print(f"  Fallback used: {metadata['fallback_used']}")
        print(f"  Attempts: {metadata['attempts']}")

        # Call with primary failure
        call_count = 0

        async def mock_fallback(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if kwargs.get("provider") == "anthropic":
                raise Exception("Primary unavailable")
            return f"Fallback success from {kwargs.get('provider')}"

        print("\nScenario 2: Primary fails, fallback succeeds")
        call_count = 0
        result, metadata = await executor.execute_with_fallback(mock_fallback)
        print(f"  Result: {result}")
        print(f"  Provider: {metadata['final_provider']}")
        print(f"  Fallback used: {metadata['fallback_used']}")
        print(f"  Attempts: {metadata['attempts']}")

    asyncio.run(run_resilient())


def demo_config_validation():
    """Demonstrate configuration validation."""
    print("\n" + "=" * 60)
    print("DEMO: Configuration Validation")
    print("=" * 60)

    validator = ConfigValidator()

    # Valid config
    valid_config = {
        "name": "code_review_workflow",
        "description": "Multi-stage code review",
        "default_provider": "anthropic",
        "stages": [
            {"name": "triage", "tier": "cheap", "timeout_ms": 30000},
            {"name": "analysis", "tier": "capable", "max_retries": 3},
            {"name": "synthesis", "tier": "premium"},
        ],
    }

    print("\nValidating correct config:")
    result = validator.validate_workflow_config(valid_config)
    print(f"  Valid: {result.valid}")

    # Invalid config
    invalid_config = {
        "description": "Missing name field",
        "default_provider": "invalid_provider",
        "stages": [
            {"name": "step1", "tier": "super_premium"},
            {"tier": "capable"},  # Missing name
        ],
    }

    print("\nValidating invalid config:")
    result = validator.validate_workflow_config(invalid_config)
    print(f"  Valid: {result.valid}")
    print("  Errors:")
    for error in result.errors:
        print(f"    - {error}")


def main():
    """Run all demos."""
    print("\n" + "=" * 60)
    print("MULTI-MODEL ARCHITECTURE EXAMPLES")
    print("=" * 60)

    demo_model_registry()
    demo_task_routing()
    demo_mock_executor()
    demo_telemetry()
    demo_fallback_policies()
    demo_resilient_executor()
    demo_config_validation()

    print("\n" + "=" * 60)
    print("All demos completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
