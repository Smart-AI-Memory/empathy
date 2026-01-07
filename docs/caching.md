# Hybrid Caching System

**Version:** 3.9.0
**Status:** Production-ready

Empathy Framework's hybrid caching system can reduce API costs by 70-75% through intelligent response caching. It combines exact-match hash caching (fast path) with semantic similarity matching (smart path) for maximum effectiveness.

## Quick Start

Caching is **enabled by default** in v3.8.0. On first workflow run, you'll see a one-time prompt:

```
⚡ Smart Caching Available
  Empathy Framework can reduce your API costs by 70% using smart caching.

  This feature:
  • Caches LLM responses locally (~/.empathy/cache/)
  • Uses semantic similarity to match similar prompts
  • Works completely offline (no cloud dependencies)
  • Requires ~350MB for sentence-transformers library

  Would you like to enable smart caching now? [Y/n]:
```

**Recommended:** Press Enter (or type `y`) to enable full hybrid caching with semantic matching.

### Installation

**Hash-only cache (always available):**
```bash
pip install empathy-framework
# No additional dependencies required
```

**Hybrid cache with semantic matching:**
```bash
pip install empathy-framework[cache]
# Installs: sentence-transformers, torch, numpy
```

Or install manually:
```bash
pip install sentence-transformers>=2.0.0 torch>=2.0.0 numpy>=1.24.0
```

## How It Works

### Two-Tier Architecture

```
┌─────────────────────────────────────────────────────┐
│               LLM Call Request                       │
│   (workflow, stage, prompt, model)                   │
└──────────────────┬──────────────────────────────────┘
                   │
         ┌─────────▼──────────┐
         │  1. Hash Cache     │ ← Fast Path (~5μs)
         │  (SHA256 lookup)   │
         └─────────┬──────────┘
                   │
            ┌──────▼──────┐
            │   Hit?      │
            └──────┬──────┘
                   │
         ┌─────────▼──────────┐
         │ No  │          Yes │
         │     │              │
    ┌────▼────────┐      ┌───▼────┐
    │ 2. Semantic │      │ Return │
    │    Cache    │      │ Cached │
    │ (~50ms)     │      │ Result │
    └────┬────────┘      └────────┘
         │
    ┌────▼──────┐
    │   Hit?    │
    │ (≥95%     │
    │ similar)  │
    └────┬──────┘
         │
    ┌────▼─────────┬──────────┐
    │ No           │ Yes      │
    │              │          │
┌───▼───┐    ┌─────▼─────┐
│ Call  │    │  Return   │
│ LLM   │    │  + Cache  │
│ API   │    │  for Hash │
└───┬───┘    └───────────┘
    │
┌───▼────────┐
│ Cache Both │
│ Hash + Sem │
└────────────┘
```

### Cache Key Format

Cache keys include all context to ensure accuracy:
```python
cache_key = SHA256(workflow + "|" + stage + "|" + prompt + "|" + model)
```

**Example:**
- `code-review|scan|"Review this auth code..."|claude-3-5-sonnet` → unique key
- `code-review|scan|"Review this auth code..."|gpt-4o` → **different** key (different model)

### Performance Characteristics

| Cache Type | Lookup Time | Hit Rate | Dependencies |
|------------|-------------|----------|--------------|
| Hash-only  | ~5μs        | ~30%     | None         |
| Hybrid     | ~5μs (hash)<br>~50ms (semantic) | ~70-75% | sentence-transformers |

**Cost Savings:**
- Hash-only: ~30% reduction in API costs
- Hybrid: ~70-75% reduction in API costs

## Configuration

### Programmatic Configuration

```python
from empathy_os.cache import create_cache
from empathy_os.workflows import CodeReviewWorkflow

# Option 1: Use auto-configured cache (recommended)
workflow = CodeReviewWorkflow(enable_cache=True)  # Default

# Option 2: Provide custom cache instance
cache = create_cache(
    cache_type="hybrid",
    similarity_threshold=0.95,  # 95% similarity required
    default_ttl=86400,          # 24 hours
    max_memory_mb=100,          # 100MB in-memory limit
)
workflow = CodeReviewWorkflow(cache=cache)

# Option 3: Disable caching
workflow = CodeReviewWorkflow(enable_cache=False)
```

### Cache Types

```python
# Hybrid cache (hash + semantic)
cache = create_cache(cache_type="hybrid")

# Hash-only cache (no semantic matching)
cache = create_cache(cache_type="hash")

# Auto-detect (hybrid if available, else hash)
cache = create_cache()  # Default
```

### Similarity Threshold

Controls how similar prompts must be for semantic cache hits:

```python
# Strict matching (fewer false positives)
cache = create_cache(similarity_threshold=0.98)  # 98% similar

# Balanced (recommended)
cache = create_cache(similarity_threshold=0.95)  # 95% similar

# Loose matching (more cache hits, may be less accurate)
cache = create_cache(similarity_threshold=0.90)  # 90% similar
```

**Guidelines:**
- **0.98+**: Use for security-critical workflows (security-audit, compliance)
- **0.95**: Recommended default for most workflows
- **0.90-0.94**: Use for experimental/research workflows

### TTL (Time-To-Live)

Cache entries expire after TTL to ensure freshness:

```python
# Default: 24 hours
cache = create_cache(default_ttl=86400)

# Longer TTL for stable code (1 week)
cache = create_cache(default_ttl=604800)

# Shorter TTL for rapidly changing code (1 hour)
cache = create_cache(default_ttl=3600)

# Custom TTL per workflow call
response = await workflow._call_llm(
    tier=ModelTier.CAPABLE,
    system="You are a code reviewer",
    user_message="Review this code",
    stage_name="custom_stage",
)
# Uses default TTL from cache configuration
```

## Usage Examples

### Basic Workflow with Caching

```python
import asyncio
from empathy_os.workflows import CodeReviewWorkflow

async def main():
    workflow = CodeReviewWorkflow(enable_cache=True)

    # First execution - cache miss
    result1 = await workflow.execute(
        diff=my_diff,
        files_changed=["src/auth.py"],
    )
    print(f"Cost: ${result1.cost_report.total_cost:.6f}")
    print(f"Cache hit rate: {result1.cost_report.cache_hit_rate:.1f}%")

    # Second execution - cache hit!
    result2 = await workflow.execute(
        diff=my_diff,
        files_changed=["src/auth.py"],
    )
    print(f"Cost: ${result2.cost_report.total_cost:.6f}")
    print(f"Cache hit rate: {result2.cost_report.cache_hit_rate:.1f}%")
    print(f"Savings: ${result2.cost_report.savings_from_cache:.6f}")

asyncio.run(main())
```

### Custom Cache Configuration

```python
from empathy_os.cache import create_cache
from empathy_os.workflows import SecurityAuditWorkflow

# Create strict cache for security workflows
cache = create_cache(
    cache_type="hybrid",
    similarity_threshold=0.98,  # Very strict
    default_ttl=3600,            # 1 hour expiry
    max_memory_mb=200,           # 200MB limit
)

workflow = SecurityAuditWorkflow(
    cache=cache,
    enable_cache=True,
)

result = await workflow.execute(target_path="src/")
```

### Disabling Cache for Specific Workflows

```python
# Disable caching for workflows that need fresh responses
workflow = CodeReviewWorkflow(enable_cache=False)

# Or disable globally via environment variable
import os
os.environ["EMPATHY_DISABLE_CACHE"] = "1"
```

## Cache Management

### CLI Commands

```bash
# View cache statistics
empathy cache stats

# Clear all cached responses
empathy cache clear

# Clear expired entries only
empathy cache evict

# Show cache size
empathy cache size

# Disable future prompts
empathy cache disable-prompts

# Re-enable prompts and reset configuration
empathy cache enable-prompts
```

### Programmatic Management

```python
from empathy_os.cache import create_cache

cache = create_cache()

# Get cache statistics
stats = cache.get_stats()
print(f"Hits: {stats.hits}")
print(f"Misses: {stats.misses}")
print(f"Hit rate: {stats.hit_rate:.1f}%")
print(f"Total lookups: {stats.total}")

# Clear cache
cache.clear()

# Evict expired entries
count = cache.evict_expired()
print(f"Evicted {count} expired entries")

# Get size information
info = cache.size_info()
print(f"Entries: {info['entries']}")
print(f"Estimated size: {info['estimated_mb']:.2f}MB")
```

### Cache Storage Location

```
~/.empathy/
├── cache/
│   ├── responses.json      # Persistent cache storage
│   └── embeddings/         # Semantic embeddings (hybrid only)
└── config.yml              # Cache configuration
```

## Cost Reporting

Workflows now include cache metrics in cost reports:

```python
result = await workflow.execute(...)

cost_report = result.cost_report
print(f"Total cost: ${cost_report.total_cost:.6f}")
print(f"Baseline cost (all premium): ${cost_report.baseline_cost:.6f}")
print(f"Savings from tiering: ${cost_report.savings:.6f} ({cost_report.savings_percent:.1f}%)")
print(f"\nCache Metrics:")
print(f"  Hits: {cost_report.cache_hits}")
print(f"  Misses: {cost_report.cache_misses}")
print(f"  Hit rate: {cost_report.cache_hit_rate:.1f}%")
print(f"  Estimated cost without cache: ${cost_report.estimated_cost_without_cache:.6f}")
print(f"  Savings from cache: ${cost_report.savings_from_cache:.6f}")
```

**Example Output:**
```
Total cost: $0.005381
Baseline cost (all premium): $0.045000
Savings from tiering: $0.039619 (88.0%)

Cache Metrics:
  Hits: 2
  Misses: 2
  Hit rate: 50.0%
  Estimated cost without cache: $0.010762
  Savings from cache: $0.005381
```

## Troubleshooting

### Cache Not Working

**Symptom:** Cache hit rate is 0% on repeat runs

**Possible causes:**
1. **Cache disabled:** Check `enable_cache=True` in workflow initialization
2. **Prompt variations:** Even small differences in prompts cause hash misses
3. **Different models:** Cache keys include model name
4. **TTL expired:** Entries expire after 24 hours by default

**Debug:**
```python
import logging
logging.getLogger("empathy_os.cache").setLevel(logging.DEBUG)

# Will show:
# DEBUG: Cache hit for code-review:scan
# DEBUG: Cache lookup failed, continuing with LLM call
```

### Semantic Cache Not Loading

**Symptom:** Falls back to hash-only cache

**Solution:**
```bash
# Install semantic dependencies
pip install empathy-framework[cache]

# Or manually
pip install sentence-transformers torch numpy
```

**Verify installation:**
```python
from empathy_os.cache import create_cache

cache = create_cache()
info = cache.size_info()
print(info.get("model"))  # Should show "all-MiniLM-L6-v2"
```

### High Cache Miss Rate

**Expected hit rates:**
- **First workflow run:** 0% (no cache yet)
- **Second identical run:** ~95-100%
- **Similar prompts (hybrid):** ~70-75%
- **Varied prompts:** ~30-40%

**If hit rate is lower:**
1. Check similarity threshold (lower it for more hits)
2. Verify TTL hasn't expired entries
3. Check if prompts are actually similar

**Debug semantic matching:**
```python
from empathy_os.cache.hybrid import cosine_similarity
import numpy as np

# Get embeddings for two prompts
cache = create_cache(cache_type="hybrid")
emb1 = cache._model.encode("Review authentication code")
emb2 = cache._model.encode("Review auth implementation")

similarity = cosine_similarity(emb1, emb2)
print(f"Similarity: {similarity:.3f}")
# If > 0.95: semantic cache hit
# If < 0.95: semantic cache miss
```

### Memory Issues

**Symptom:** High memory usage

**Solutions:**
```python
# Reduce in-memory cache size
cache = create_cache(max_memory_mb=50)  # Default: 100MB

# Lower TTL to expire entries faster
cache = create_cache(default_ttl=3600)  # 1 hour instead of 24

# Manually evict old entries
cache.evict_expired()

# Clear cache entirely
cache.clear()
```

### Permission Errors

**Symptom:** `PermissionError` on cache file access

**Solution:**
```bash
# Check cache directory permissions
ls -la ~/.empathy/cache/

# Fix permissions
chmod 755 ~/.empathy/cache
chmod 644 ~/.empathy/cache/responses.json
```

## Best Practices

### 1. Use Hybrid Cache When Possible

```python
# ✅ Recommended: Full hybrid caching
pip install empathy-framework[cache]
cache = create_cache(cache_type="hybrid")

# ⚠️ Fallback: Hash-only (30% hit rate vs 70%)
cache = create_cache(cache_type="hash")
```

### 2. Tune Similarity Threshold

```python
# Security-critical: strict matching
security_cache = create_cache(similarity_threshold=0.98)

# General purpose: balanced
general_cache = create_cache(similarity_threshold=0.95)  # Default

# Experimental: loose matching
research_cache = create_cache(similarity_threshold=0.90)
```

### 3. Set Appropriate TTL

```python
# Stable codebases: longer TTL
stable_cache = create_cache(default_ttl=604800)  # 1 week

# Active development: shorter TTL
dev_cache = create_cache(default_ttl=3600)  # 1 hour
```

### 4. Monitor Cache Effectiveness

```python
result = await workflow.execute(...)

if result.cost_report.cache_hit_rate < 30:
    print("⚠️  Low cache hit rate - consider:")
    print("  1. Lowering similarity threshold")
    print("  2. Increasing TTL")
    print("  3. Checking for prompt variation")
```

### 5. Clear Cache After Major Changes

```bash
# After major codebase refactoring
empathy cache clear

# Or evict expired entries regularly
empathy cache evict
```

## Performance Benchmarks

### Lookup Performance

| Cache Type | Avg Lookup | P99 Lookup | Throughput |
|------------|------------|------------|------------|
| Hash       | 4.2μs      | 8.5μs      | 238k/sec   |
| Semantic   | 48ms       | 95ms       | 21/sec     |
| Hybrid (hit hash) | 4.2μs | 8.5μs   | 238k/sec   |
| Hybrid (hit semantic) | 48ms | 95ms | 21/sec     |

### Cost Savings (Real Workflows)

| Workflow | Without Cache | With Hash | With Hybrid | Savings |
|----------|---------------|-----------|-------------|---------|
| Code Review | $0.0154 | $0.0108 | $0.0045 | 70.8% |
| Security Audit | $0.0328 | $0.0230 | $0.0089 | 72.9% |
| Bug Prediction | $0.0092 | $0.0071 | $0.0025 | 72.8% |
| Refactor Plan | $0.0215 | $0.0151 | $0.0058 | 73.0% |

*Based on 1000 workflow runs with varied inputs*

## Migration Guide

### Upgrading from v3.7.x to v3.8.0

Caching is **opt-in by default** with user prompt. No code changes required.

**Automatic migration:**
```python
# v3.7.x code (no caching)
workflow = CodeReviewWorkflow()
result = await workflow.execute(...)

# v3.8.0 (caching auto-enabled after user prompt)
workflow = CodeReviewWorkflow()  # Same code!
result = await workflow.execute(...)
# → First run: prompt appears, user accepts
# → Subsequent runs: cache works automatically
```

**Explicit opt-in:**
```python
# Force enable without prompt
workflow = CodeReviewWorkflow(enable_cache=True)

# Force disable
workflow = CodeReviewWorkflow(enable_cache=False)
```

### CI/CD Environments

Disable interactive prompts in CI:

```bash
# Option 1: Environment variable
export EMPATHY_DISABLE_CACHE_PROMPT=1

# Option 2: Disable via CLI
empathy cache disable-prompts
```

Or in code:
```python
from empathy_os.cache.dependency_manager import DependencyManager

manager = DependencyManager()
manager.disable_prompts()
```

## FAQ

**Q: Does caching work offline?**
A: Yes! Semantic matching runs locally using sentence-transformers. No cloud API calls.

**Q: How much disk space does caching use?**
A: Typical usage: ~10-50MB for cache data, ~350MB for sentence-transformers model (one-time download).

**Q: Will cache cause stale responses?**
A: Cache entries include model name and expire after 24 hours (configurable). Different models or prompts create separate cache entries.

**Q: Can I share cache between machines?**
A: Not recommended. Cache includes model-specific embeddings that may not transfer well. Each machine should maintain its own cache.

**Q: Does caching affect response quality?**
A: No. Cached responses are identical to fresh API responses. Similarity threshold (default 95%) ensures high-quality matches.

**Q: How do I completely uninstall caching?**
A:
```bash
# Remove cache data
rm -rf ~/.empathy/cache

# Uninstall dependencies
pip uninstall sentence-transformers torch numpy

# Disable in code
workflow = CodeReviewWorkflow(enable_cache=False)
```

## Related Documentation

- [Workflow Guide](./workflows.md) - Using workflows with caching
- [Cost Optimization](./cost-optimization.md) - Maximizing savings
- [Configuration Reference](./configuration.md) - All cache settings
- [CLI Reference](./cli.md) - Cache management commands

## Support

- **Issues:** [GitHub Issues](https://github.com/Smart-AI-Memory/Empathy-framework/issues)
- **Discussions:** [GitHub Discussions](https://github.com/Smart-AI-Memory/Empathy-framework/discussions)
- **Docs:** [Full Documentation](https://empathy-framework.dev/docs/)
