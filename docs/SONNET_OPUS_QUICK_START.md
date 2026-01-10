# Sonnet 4.5 → Opus 4.5 Quick Start Guide

**Updated:** January 9, 2026
**Empathy Framework v3.9.2+**

## What Changed?

The Empathy Framework now uses **Claude Sonnet 4.5** as the default CAPABLE tier model with intelligent fallback to **Opus 4.5** when needed.

**Result:** Up to **80% cost savings** while maintaining high quality.

---

## Quick Test (2 minutes)

Run the automated test suite to verify everything works:

```bash
# Quick test (5-10 tests, ~30 seconds)
python tests/test_fallback_suite.py --quick

# Full test (15-20 tests, ~2 minutes)
python tests/test_fallback_suite.py --full
```

**Expected Output:**
```
🎯 SONNET 4.5 → OPUS 4.5 FALLBACK TEST REPORT
================================================================

Test Execution Summary:
  Total Tests: 5
  Passed: 5
  Failed: 0
  Success Rate: 100%

Model Usage Distribution:
  Sonnet Only: 5 (100%)
  Opus Fallback: 0 (0%)
  Fallback Rate: 0%

Cost Savings Analysis:
  Actual Cost: $0.0225
  Baseline (all Opus): $0.1125
  Savings: $0.0900 (80.0%)

✅ Excellent Performance!
```

---

## View Your Savings

After running workflows, check your cost savings:

```bash
# View last 30 days
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
└──────────────────────────────────────────────────────────────┘
```

---

## Using Fallback in Your Code

### Basic Usage (Automatic)

The framework automatically uses Sonnet 4.5 - no changes needed:

```python
from empathy_os.models.empathy_executor import EmpathyLLMExecutor

executor = EmpathyLLMExecutor(provider="anthropic")

# Automatically uses Sonnet 4.5
response = await executor.run(
    task_type="code_review",
    prompt="Review this code for security issues...",
)
```

### Enable Intelligent Fallback

To automatically upgrade to Opus when needed:

```python
from empathy_os.models.empathy_executor import EmpathyLLMExecutor
from empathy_os.models.fallback import SONNET_TO_OPUS_FALLBACK, ResilientExecutor

# Base executor
base_executor = EmpathyLLMExecutor(provider="anthropic")

# Wrap with intelligent fallback
executor = ResilientExecutor(
    executor=base_executor,
    fallback_policy=SONNET_TO_OPUS_FALLBACK,
)

# Tries Sonnet first, upgrades to Opus if needed
response = await executor.run(
    task_type="complex_reasoning",
    prompt="Analyze this distributed system...",
)

# Check if Opus was used
if response.metadata.get("fallback_used"):
    print("Upgraded to Opus 4.5 for better quality")
```

---

## Running Workflows

All existing workflows automatically use Sonnet 4.5:

```bash
# Code review (should use Sonnet)
empathy workflow run code-review --input '{"file":"src/models/registry.py"}'

# Test generation (should use Sonnet)
empathy workflow run test-gen --input '{"target":"src/utils.py"}'

# Complex refactoring (may use Opus)
empathy workflow run refactor-plan --input '{"target":"src/models/", "complexity":"high"}'

# Check which model was used
python -m empathy_os.telemetry.cli show --limit 5
```

---

## Understanding the Results

### Target Metrics

| Metric | Good | Warning | Poor |
|--------|------|---------|------|
| **Sonnet Success Rate** | > 95% | 90-95% | < 90% |
| **Fallback Rate** | < 5% | 5-15% | > 15% |
| **Cost Savings** | > 75% | 60-75% | < 60% |

### Interpreting Fallback Rate

**< 5% (Excellent)**
- Sonnet handles most tasks successfully
- Maximum cost savings
- Current strategy is optimal

**5-15% (Good)**
- Moderate Opus usage
- Still significant savings
- Monitor for patterns

**> 15% (Review Needed)**
- High Opus usage
- May benefit from direct Opus for complex tasks
- Reduces retry overhead

---

## Test Scenarios

### Test Different Workflows

```bash
# Test simple tasks (should all use Sonnet)
for file in src/**/*.py; do
    empathy workflow run code-review --input "{\"file\":\"$file\"}"
done

# Test complex tasks (may trigger Opus)
empathy workflow run refactor-plan --input '{
    "target": "src/models/",
    "goals": ["Extract interfaces", "Add DI", "Backwards compatible"]
}'

# Check results
python -m empathy_os.telemetry.cli sonnet-opus-analysis --days 1
```

### Run Example Script

```bash
# Comprehensive examples
python examples/sonnet_opus_fallback_example.py
```

---

## Troubleshooting

### No Telemetry Data

**Problem:** `sonnet-opus-analysis` shows "No calls found"

**Solution:**
```bash
# Verify telemetry is enabled
python -c "
from empathy_os.models.telemetry import get_telemetry_store
store = get_telemetry_store()
calls = store.get_calls(limit=10)
print(f'Found {len(calls)} calls')
"

# Run a test workflow
empathy workflow run code-review --input '{"file":"src/models/registry.py"}'

# Check again
python -m empathy_os.telemetry.cli sonnet-opus-analysis
```

### High Fallback Rate

**Problem:** > 15% fallback rate

**Solutions:**

1. **Check which workflows trigger fallback:**
```python
from empathy_os.models.telemetry import get_telemetry_store

store = get_telemetry_store()
calls = store.get_calls(limit=1000)

opus_calls = [c for c in calls if c.model_id == "claude-opus-4-5-20251101"]
for call in opus_calls:
    print(f"Workflow: {call.workflow_name}, Reason: {call.metadata.get('fallback_chain')}")
```

2. **Use Opus directly for those workflows:**
```python
# For known complex tasks
executor = EmpathyLLMExecutor(provider="anthropic", default_tier="premium")
```

### Circuit Breaker Engaged

**Problem:** Circuit breaker blocking calls

**Solution:**
```python
from empathy_os.models.fallback import ResilientExecutor

executor = ResilientExecutor()

# Check status
status = executor.circuit_breaker.get_status()
print(status)

# Reset if needed
executor.circuit_breaker.reset("anthropic", "capable")
```

---

## Files Created

| File | Purpose |
|------|---------|
| `docs/SONNET_OPUS_FALLBACK_GUIDE.md` | Comprehensive guide |
| `docs/SONNET_OPUS_QUICK_START.md` | This quick start (you are here) |
| `examples/sonnet_opus_fallback_example.py` | Code examples |
| `tests/test_fallback_suite.py` | Automated test suite |
| `tests/test_sonnet_opus_fallback.py` | Unit tests |

---

## Next Steps

1. **Run the automated test suite:**
   ```bash
   python tests/test_fallback_suite.py --quick
   ```

2. **Run your normal workflows** - they automatically use Sonnet now

3. **Check savings after a week:**
   ```bash
   python -m empathy_os.telemetry.cli sonnet-opus-analysis --days 7
   ```

4. **Adjust strategy based on results** - see docs for details

---

## Summary of Changes

### What Was Updated

✅ **Model Registry** ([src/empathy_os/models/registry.py](../src/empathy_os/models/registry.py))
- CAPABLE tier now uses `claude-sonnet-4-5` (was `claude-sonnet-4-20250514`)
- Pricing unchanged: $3/$15 per million tokens

✅ **Fallback Policy** ([src/empathy_os/models/fallback.py](../src/empathy_os/models/fallback.py))
- Added `SONNET_TO_OPUS_FALLBACK` policy
- Intelligent Sonnet → Opus escalation

✅ **Telemetry Analytics** ([src/empathy_os/models/telemetry.py](../src/empathy_os/models/telemetry.py))
- Added `sonnet_opus_fallback_analysis()` method
- Tracks success rates and cost savings

✅ **CLI Command** ([src/empathy_os/telemetry/cli.py](../src/empathy_os/telemetry/cli.py))
- New `sonnet-opus-analysis` command
- Visual dashboard with recommendations

### What Stays the Same

✅ **API Interface** - No breaking changes
✅ **Pricing** - Sonnet 4.5 costs same as Sonnet 4.0
✅ **Model Quality** - Sonnet 4.5 is same/better than 4.0
✅ **Existing Workflows** - All continue to work

---

## Support

- **Full Documentation:** [SONNET_OPUS_FALLBACK_GUIDE.md](./SONNET_OPUS_FALLBACK_GUIDE.md)
- **Examples:** [examples/sonnet_opus_fallback_example.py](../examples/sonnet_opus_fallback_example.py)
- **Issues:** [GitHub Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)

---

**Questions? Run the automated test suite and check the results!**

```bash
python tests/test_fallback_suite.py --full
```
