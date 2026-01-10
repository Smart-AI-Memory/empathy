# Sonnet 4.5 → Opus 4.5 Intelligent Fallback Guide

**Updated:** January 9, 2026
**Empathy Framework v3.9.2+**

## Overview

The Empathy Framework now uses **Claude Sonnet 4.5** as the default CAPABLE tier model, with intelligent fallback to **Claude Opus 4.5** when tasks require additional reasoning capability.

This strategy provides:
- **80% cost savings** when Sonnet succeeds (vs. always using Opus)
- **Automatic quality escalation** for complex tasks
- **Full telemetry** to track success rates and cost savings

---

## Cost Comparison

| Model | Input Cost/M | Output Cost/M | Use Case |
|-------|-------------|---------------|----------|
| **Sonnet 4.5** | $3.00 | $15.00 | Default for most tasks |
| **Opus 4.5** | $15.00 | $75.00 | Fallback for complex reasoning |

**Savings Example:**
- 1M input tokens + 100K output tokens
- Sonnet cost: $3.00 + $1.50 = **$4.50**
- Opus cost: $15.00 + $7.50 = **$22.50**
- **Savings: $18.00 (80%)**

---

## How It Works

### 1. Default Behavior (Automatic)

The framework automatically uses Sonnet 4.5 for CAPABLE tier tasks:

```python
from empathy_os.models.empathy_executor import EmpathyLLMExecutor

executor = EmpathyLLMExecutor(provider="anthropic")

# This automatically uses Sonnet 4.5 (CAPABLE tier)
response = await executor.run(
    task_type="code_review",
    prompt="Review this code for security issues...",
)
```

**Default Model:** `claude-sonnet-4-5` (Sonnet 4.5)

### 2. Intelligent Fallback (Enabled)

When you enable fallback, the system:
1. Tries Sonnet 4.5 first
2. If Sonnet fails or returns low-quality results, automatically retries with Opus 4.5
3. Tracks which model succeeded for analytics

```python
from empathy_os.models.empathy_executor import EmpathyLLMExecutor
from empathy_os.models.fallback import (
    ResilientExecutor,
    SONNET_TO_OPUS_FALLBACK,
)

# Base executor
base_executor = EmpathyLLMExecutor(provider="anthropic")

# Wrap with resilient fallback
executor = ResilientExecutor(
    executor=base_executor,
    fallback_policy=SONNET_TO_OPUS_FALLBACK,  # Sonnet → Opus chain
)

# Automatically tries Sonnet first, falls back to Opus if needed
response = await executor.run(
    task_type="complex_reasoning",
    prompt="Analyze this architecture for subtle race conditions...",
)

# Check if fallback was used
if response.metadata.get("fallback_used"):
    print(f"Upgraded to Opus 4.5")
    print(f"Reason: {response.metadata.get('fallback_chain')}")
```

---

## Tracking Cost Savings

### View Fallback Analytics

The framework includes a dedicated CLI command to track Sonnet → Opus fallback performance:

```bash
# View last 30 days of fallback data
python -m empathy_os.telemetry.cli sonnet-opus-analysis

# Custom time period
python -m empathy_os.telemetry.cli sonnet-opus-analysis --days 7
```

**Sample Output:**

```
┌─ Sonnet 4.5 → Opus 4.5 Fallback Performance (last 30 days) ─┐
│ Total Anthropic Calls: 872                                   │
│ Sonnet 4.5 Attempts: 694                                     │
│ Sonnet Success Rate: 96.5%                                   │
│ Opus Fallbacks: 24                                           │
│ Fallback Rate: 2.8%                                          │
└──────────────────────────────────────────────────────────────┘

┌─ Cost Savings Analysis ──────────────────────────────────────┐
│ Actual Cost: $25.39                                          │
│ Always-Opus Cost: $126.95                                    │
│ Savings: $101.56 (80.0%)                                     │
│                                                               │
│ Avg Cost/Call (actual): $0.0291                              │
│ Avg Cost/Call (all Opus): $0.1456                            │
└──────────────────────────────────────────────────────────────┘

┌─ Recommendation ─────────────────────────────────────────────┐
│ ✅ Excellent Performance!                                    │
│ Sonnet 4.5 handles 97.2% of tasks successfully.              │
│ You're saving $101.56 compared to always using Opus.         │
└──────────────────────────────────────────────────────────────┘
```

### Programmatic Access

```python
from empathy_os.models.telemetry import TelemetryAnalytics, get_telemetry_store
from datetime import datetime, timedelta

store = get_telemetry_store()
analytics = TelemetryAnalytics(store)

# Get fallback stats for last 30 days
since = datetime.utcnow() - timedelta(days=30)
stats = analytics.sonnet_opus_fallback_analysis(since=since)

print(f"Sonnet success rate: {stats['success_rate_sonnet']:.1f}%")
print(f"Cost savings: ${stats['savings']:.2f}")
print(f"Fallback rate: {stats['fallback_rate']:.1f}%")
```

---

## When Does Fallback Trigger?

The fallback mechanism triggers on:

1. **API Errors:**
   - Rate limiting
   - Timeout
   - Server errors (5xx)
   - Connection failures

2. **Quality Issues** (if configured):
   - Response doesn't meet validation criteria
   - Output format incorrect
   - Confidence score below threshold

3. **Circuit Breaker:**
   - After 5 consecutive Sonnet failures, circuit opens
   - Automatically routes to Opus for 60 seconds
   - Gradually tries Sonnet again (half-open state)

---

## Configuration Options

### Custom Fallback Policy

Create your own fallback chain:

```python
from empathy_os.models.fallback import FallbackPolicy, FallbackStrategy, FallbackStep

# Custom: Sonnet → Opus → OpenAI o1 (cross-provider)
custom_policy = FallbackPolicy(
    primary_provider="anthropic",
    primary_tier="capable",  # Sonnet 4.5
    strategy=FallbackStrategy.CUSTOM,
    custom_chain=[
        FallbackStep(
            provider="anthropic",
            tier="premium",  # Opus 4.5
            description="Upgrade to Opus 4.5",
        ),
        FallbackStep(
            provider="openai",
            tier="premium",  # o1
            description="Cross-provider fallback to OpenAI o1",
        ),
    ],
)
```

### Retry Configuration

Adjust retry behavior:

```python
from empathy_os.models.fallback import RetryPolicy

retry_policy = RetryPolicy(
    max_retries=3,  # Retry up to 3 times per model
    initial_delay_ms=1000,  # Start with 1 second delay
    exponential_backoff=True,  # Double delay each retry
    retry_on_errors=["rate_limit", "timeout", "server_error"],
)

executor = ResilientExecutor(
    executor=base_executor,
    fallback_policy=SONNET_TO_OPUS_FALLBACK,
    retry_policy=retry_policy,
)
```

---

## Best Practices

### 1. Use Sonnet for Most Tasks

Sonnet 4.5 excels at:
- Code generation and review
- Documentation writing
- Test generation
- Refactoring
- Debugging
- General reasoning

**Recommendation:** Default to Sonnet unless you know the task requires Opus.

### 2. Direct to Opus for Known Complex Tasks

If you know a task always requires Opus, save retry overhead:

```python
# Direct to Opus (no fallback needed)
executor = EmpathyLLMExecutor(provider="anthropic", default_tier="premium")
```

### 3. Monitor Fallback Rate

- **< 5% fallback rate:** Excellent - Sonnet handles most tasks
- **5-15% fallback rate:** Good - Monitor for patterns
- **> 15% fallback rate:** Review task routing - may need Opus by default

### 4. Check Analytics Weekly

```bash
# Weekly check
python -m empathy_os.telemetry.cli sonnet-opus-analysis --days 7
```

If fallback rate is consistently high, consider:
- Using Opus directly for those task types
- Adjusting prompt quality
- Reviewing retry configuration

---

## Migration from Sonnet 4.0

If you were using Sonnet 4.0 (`claude-sonnet-4-20250514`), the update is automatic:

**Before (v3.9.1):**
```python
# Used claude-sonnet-4-20250514 (Sonnet 4.0)
model_info = MODEL_REGISTRY["anthropic"]["capable"]
print(model_info.id)  # "claude-sonnet-4-20250514"
```

**After (v3.9.2+):**
```python
# Now uses claude-sonnet-4-5 (Sonnet 4.5)
model_info = MODEL_REGISTRY["anthropic"]["capable"]
print(model_info.id)  # "claude-sonnet-4-5"
```

**Pricing:** Unchanged ($3/$15 per million tokens)

---

## API Reference

### SONNET_TO_OPUS_FALLBACK

Pre-configured fallback policy for Sonnet → Opus escalation.

```python
from empathy_os.models.fallback import SONNET_TO_OPUS_FALLBACK

# Policy details
SONNET_TO_OPUS_FALLBACK.primary_provider  # "anthropic"
SONNET_TO_OPUS_FALLBACK.primary_tier      # "capable" (Sonnet 4.5)
SONNET_TO_OPUS_FALLBACK.custom_chain      # [Opus 4.5]
SONNET_TO_OPUS_FALLBACK.max_retries       # 1
```

### TelemetryAnalytics.sonnet_opus_fallback_analysis()

Analyze fallback performance and cost savings.

```python
def sonnet_opus_fallback_analysis(since: datetime | None = None) -> dict[str, Any]:
    """Returns:
    {
        "total_calls": 872,
        "sonnet_attempts": 694,
        "sonnet_successes": 670,
        "opus_fallbacks": 24,
        "success_rate_sonnet": 96.5,
        "fallback_rate": 2.8,
        "actual_cost": 25.39,
        "always_opus_cost": 126.95,
        "savings": 101.56,
        "savings_percent": 80.0,
        "avg_cost_per_call": 0.0291,
        "avg_opus_cost_per_call": 0.1456,
    }
    """
```

---

## Troubleshooting

### High Fallback Rate (> 15%)

**Possible Causes:**
1. Tasks genuinely need Opus-level reasoning
2. Sonnet rate limits being hit
3. Circuit breaker opening due to transient failures

**Solutions:**
```python
# Check circuit breaker status
executor.circuit_breaker.get_status()

# Reset if needed
executor.circuit_breaker.reset("anthropic", "capable")

# Or use Opus directly for complex tasks
executor = EmpathyLLMExecutor(provider="anthropic", default_tier="premium")
```

### No Cost Savings

**Check if fallback is enabled:**
```python
# Verify you're using ResilientExecutor
print(isinstance(executor, ResilientExecutor))  # Should be True

# Check fallback policy
print(executor.fallback_policy.custom_chain)
```

### Fallback Analytics Show Zero Calls

**Possible Reasons:**
1. No calls made yet
2. Using old model IDs
3. Telemetry not enabled

**Solution:**
```python
# Verify telemetry is working
from empathy_os.models.telemetry import get_telemetry_store

store = get_telemetry_store()
calls = store.get_calls(limit=10)
print(f"Found {len(calls)} calls")
```

---

## Related Documentation

- [Claude Sonnet 4.5 Announcement](https://www.anthropic.com/news/claude-sonnet-4-5)
- [Anthropic API Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Empathy Framework Telemetry Guide](./TELEMETRY_GUIDE.md)
- [Fallback Policy Reference](./FALLBACK_POLICIES.md)

---

## Changelog

**v3.9.2** (January 9, 2026)
- Updated CAPABLE tier to use Claude Sonnet 4.5 (`claude-sonnet-4-5`)
- Added `SONNET_TO_OPUS_FALLBACK` policy
- Added `TelemetryAnalytics.sonnet_opus_fallback_analysis()`
- Added `empathy_os.telemetry.cli sonnet-opus-analysis` command
- Maintained pricing at $3/$15 per million tokens (same as Sonnet 4.0)

**v3.9.1** (December 2025)
- Used Claude Sonnet 4.0 (`claude-sonnet-4-20250514`)

---

## Questions?

- **GitHub Discussions:** [Empathy Framework Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)
- **Issues:** [Report a Bug](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- **Documentation:** [Full Docs](https://empathyframework.com/docs)
