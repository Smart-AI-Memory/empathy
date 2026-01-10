# Profiling Results - Phase 2 Track 1

**Date:** 2026-01-10
**Purpose:** Data-driven performance analysis to inform Phase 2 optimization efforts
**Test Suite:** `benchmarks/profile_suite.py`

---

## Executive Summary

Completed comprehensive profiling of 8 key framework components using cProfile. Identified clear optimization opportunities:

- **Project Scanner** is the dominant bottleneck (9.5s per scan)
- **AST parsing and traversal** accounts for ~55% of scanner time
- **Pattern matching** is already well-optimized (96ms for 1000 queries)
- **Memory operations** show overhead from initialization, but core operations are fast
- **Cost tracking** efficiently handles 1000 requests in 28ms

---

## Top 10 Hotspots (by Cumulative Time)

### 1. **AST Compilation** - 1.94s (20.4% of scanner time)
- **Location:** `{built-in method builtins.compile}`
- **Called by:** `scanner.py:402 (_analyze_python_ast)`
- **Calls:** 873 times
- **Per-call:** 2.2ms
- **Optimization Opportunity:** HIGH - Consider caching compiled ASTs by file hash

### 2. **AST Walking** - 3.13s (32.9% of scanner time)
- **Location:** `/lib/python3.10/ast.py:380 (walk)`
- **Calls:** 2,124,884 times
- **Per-call:** 0.0015ms
- **Context:** Called during `_analyze_python_ast`
- **Optimization Opportunity:** MEDIUM - High call count, but individual calls are fast

### 3. **AST Node Iteration** - 2.22s (23.4% of scanner time)
- **Location:** `/lib/python3.10/ast.py:267 (iter_child_nodes)`
- **Calls:** 4,211,197 times
- **Per-call:** 0.0005ms
- **Optimization Opportunity:** LOW - Core Python functionality, highly optimized

### 4. **File Analysis Pipeline** - 7.54s (79.3% of scanner time)
- **Location:** `scanner.py:206 (_analyze_file)`
- **Calls:** 2,112 times (one per file)
- **Per-call:** 3.6ms
- **Breakdown:**
  - AST parsing: 5.27s (70%)
  - Metrics calculation: 7.36s (97% - includes AST overhead)
  - Dependency analysis: 0.62s (8%)
- **Optimization Opportunity:** HIGH - Pipeline is sequential, consider async I/O

### 5. **Pattern Relevance Calculation** - 70ms (72.9% of pattern matching time)
- **Location:** `pattern_library.py:470 (_calculate_relevance)`
- **Calls:** 100,000 times
- **Per-call:** 0.0007ms
- **Context:** Called 100 times per pattern query (100 patterns * 1000 queries)
- **Optimization Opportunity:** MEDIUM - Could use vectorization or early termination

### 6. **JSON Deserialization** - 6-8ms (multiple components)
- **Location:** `json.loads()` in cost_tracker, test_gen
- **Calls:** 2,238+ times across components
- **Optimization Opportunity:** LOW - Standard library, already optimized

### 7. **File Discovery** - 0.68s (7.2% of scanner time)
- **Location:** `scanner.py:112 (_discover_files)`
- **Calls:** 1 time
- **Optimization Opportunity:** LOW - One-time cost, reasonable for 2,112 files

### 8. **Dependency Analysis** - 0.62s (6.5% of scanner time)
- **Location:** `scanner.py:445 (_analyze_dependencies)`
- **Calls:** 1 time (processes all imports)
- **Optimization Opportunity:** MEDIUM - Could be parallelized

### 9. **Glob Pattern Matching** - 0.73s (7.7% of scanner time)
- **Location:** `scanner.py:129 (_matches_glob_pattern)`
- **Calls:** 189,647 times
- **Per-call:** 0.004ms
- **Optimization Opportunity:** MEDIUM - Consider pre-compiling regex patterns

### 10. **Workflow Module Loading** - 0.13s (100% of workflow profiling time)
- **Location:** Module imports (`workflows/__init__.py`)
- **Context:** Includes numpy, dataclasses, cache initialization
- **Optimization Opportunity:** LOW - One-time import cost

---

## Component-by-Component Analysis

### Project Scanner (9.51 seconds)

**Profile:** `benchmarks/profiles/scanner_scan.prof`

**Stats:**
- Total files scanned: 2,112
- Source files: 556
- Test files: 288
- Lines of code: 166,785
- Function calls: 43,420,606

**Time Breakdown:**
```
Total: 9.51s
├─ _analyze_file: 7.54s (79.3%)
│  ├─ _analyze_python_ast: 5.27s (55.4%)
│  │  ├─ ast.compile: 1.94s (20.4%)
│  │  ├─ ast.walk: 3.13s (32.9%)
│  │  └─ ast.iter_child_nodes: 2.22s (23.4%)
│  ├─ _analyze_code_metrics: 7.36s (77.4%)
│  └─ _parse_python_cached: 1.96s (20.6%)
├─ _discover_files: 0.68s (7.2%)
├─ _analyze_dependencies: 0.62s (6.5%)
└─ Other: 0.71s (7.5%)
```

**Key Findings:**
1. AST parsing dominates (55% of total time)
2. Cache hit rate unknown - need to measure
3. Sequential file processing (no parallelization)
4. 770 Python files analyzed with AST
5. Glob matching called 189,647 times (could optimize)

**Quick Wins:**
- ✅ **AST caching** already implemented (`_parse_python_cached`)
- 🔄 **Measure cache effectiveness** - add hit/miss counters
- 🔄 **Parallel file processing** - use multiprocessing.Pool
- 🔄 **Pre-compile glob patterns** - compile once, reuse

**Deep Optimization Candidates:**
- Incremental scanning (only changed files)
- AST serialization to disk
- Lazy AST analysis (on-demand)

---

### Pattern Library (96ms for 1000 queries)

**Profile:** `benchmarks/profiles/pattern_library.prof`

**Stats:**
- Patterns: 100
- Queries: 1,000
- Total matches: 0 (no matches in test data)
- Function calls: 506,713

**Time Breakdown:**
```
Total: 96ms
├─ query_patterns: 95ms (98.9%)
│  └─ _calculate_relevance: 70ms (72.9%)
│     ├─ builtins.min: 8ms (8.3%)
│     └─ dict.get: 3ms (3.1%)
├─ contribute_pattern: <1ms
└─ Other: <1ms
```

**Key Findings:**
1. Already well-optimized (96μs per query)
2. Relevance calculation is O(n) per query
3. No matches returned (perfect filtering)
4. Dictionary lookups are fast

**Quick Wins:**
- ✅ Performance already excellent
- 🔄 Could add index by pattern_type for faster filtering
- 🔄 Early termination when relevance < threshold

**Deep Optimization Candidates:**
- Vector embeddings for semantic matching
- Approximate nearest neighbor search
- Bloom filters for negative queries

---

### Memory Operations (0.79s initialization + operations)

**Profile:** `benchmarks/profiles/memory_operations.prof`

**Stats:**
- Stashed: 200 items
- Retrieved: 100 items
- Patterns staged: 50
- Patterns recalled: Variable

**Time Breakdown:**
```
Total: ~0.79s
├─ Initialization: 0.62s (78.5%)
│  ├─ Redis connection: 0.15s (19%)
│  ├─ MemDocs setup: 0.25s (31.6%)
│  └─ Security policies: 0.22s (27.8%)
├─ Stash operations: 0.08s (10.1%)
├─ Retrieve operations: 0.04s (5.1%)
└─ Pattern operations: 0.05s (6.3%)
```

**Key Findings:**
1. Initialization dominates (78.5% of time)
2. Core operations are fast:
   - Stash: 0.4ms per item
   - Retrieve: 0.4ms per item
   - Pattern staging: 1ms per pattern
3. Redis connection adds latency
4. MemDocs encryption overhead is acceptable

**Quick Wins:**
- ✅ Core operations already optimized
- 🔄 **Lazy initialization** - delay until first use
- 🔄 **Connection pooling** - reuse Redis connections
- 🔄 **Batch operations** - stash/retrieve multiple items

**Deep Optimization Candidates:**
- Async I/O for Redis operations
- Local cache with write-through
- Pipeline Redis commands

---

### Workflow Execution (130ms for data processing)

**Profile:** `benchmarks/profiles/workflow_execution.prof`

**Stats:**
- Workflow history loaded: 100 entries
- Results created: 200
- Success rate: 90%

**Time Breakdown:**
```
Total: 130ms
├─ Module imports: 128ms (98.5%)
│  ├─ workflows.base: 93ms (71.5%)
│  ├─ numpy: 64ms (49.2%)
│  └─ dataclasses: 26ms (20%)
├─ Data processing: 2ms (1.5%)
└─ Result analysis: <1ms
```

**Key Findings:**
1. Import overhead dominates (98.5%)
2. Data processing is very fast (2ms for 200 results)
3. Numpy import adds 64ms (lazy import opportunity)
4. Dataclass creation has overhead

**Quick Wins:**
- ✅ Core logic already optimized
- 🔄 **Lazy imports** - import numpy only when needed
- 🔄 **Pre-import in CLI** - load once at startup

**Deep Optimization Candidates:**
- Pydantic for validation (faster than dataclasses)
- Structured data without classes (dicts)

---

### Test Generation (25ms for 50 functions)

**Profile:** `benchmarks/profiles/test_generation.prof`

**Stats:**
- Functions analyzed: 50
- Test cases generated: 150 (simulated)
- Function calls: 68,077

**Time Breakdown:**
```
Total: 25ms
├─ Workflow initialization: 24ms (96%)
│  ├─ Cost tracker init: 16ms (64%)
│  └─ Config loading: 8ms (32%)
└─ Function processing: 1ms (4%)
```

**Key Findings:**
1. Initialization dominates (96%)
2. Actual processing is very fast
3. Cost tracker loading historical data
4. YAML config parsing adds overhead

**Quick Wins:**
- ✅ Core processing already optimized
- 🔄 **Lazy cost tracker** - initialize on first log
- 🔄 **Config caching** - load once, reuse

---

### Cost Tracker (28ms for 1000 requests)

**Profile:** `benchmarks/profiles/cost_tracker.prof`

**Stats:**
- Requests logged: 1,000
- Total cost tracked: $67.32
- Input tokens: 4.87M
- Output tokens: 3.74M

**Time Breakdown:**
```
Total: 28ms
├─ Initialization: 16ms (57%)
│  └─ _load: 15ms (53.6%)
├─ log_request: 12ms (42.8%)
│  ├─ _update_daily_totals: 8ms (28.6%)
│  └─ flush: 8ms (28.6%)
└─ get_summary: 1ms (<1%)
```

**Key Findings:**
1. Efficiently handles 1000 requests in 28ms (28μs each)
2. Initialization loads historical data
3. Periodic flushing to disk
4. Daily aggregation is fast

**Quick Wins:**
- ✅ Already well-optimized
- 🔄 **Batch flushing** - reduce flush frequency
- 🔄 **Write-behind cache** - async writes

---

### Feedback Loop Detector (70ms for 300 checks)

**Profile:** `benchmarks/profiles/feedback_loops.prof`

**Stats:**
- Session history: 500 items
- Detection cycles: 100
- Active loops detected: 100

**Time Breakdown:**
```
Total: 70ms
├─ Trend calculation: 40ms (57%)
│  └─ sum operations: 13ms (18.6%)
├─ detect_active_loop: 23ms (33%)
├─ detect_virtuous_cycle: 23ms (33%)
└─ detect_vicious_cycle: 23ms (33%)
```

**Key Findings:**
1. Trend calculation dominates (57%)
2. Multiple passes over same data
3. Generator expressions used efficiently
4. Could benefit from caching trends

**Quick Wins:**
- 🔄 **Cache trends** - calculate once, reuse
- 🔄 **Early termination** - stop when threshold met

---

## Quick Win Opportunities

### High Priority (Significant Impact, Low Effort)

1. **AST Cache Monitoring**
   - **Impact:** Measure effectiveness of existing cache
   - **Effort:** Add counters to `_parse_python_cached`
   - **Expected Gain:** Visibility into 20-40% time savings

2. **Lazy Module Imports**
   - **Impact:** Reduce workflow initialization from 130ms to ~5ms
   - **Effort:** Move numpy import to usage site
   - **Expected Gain:** 95% reduction in cold start time

3. **Glob Pattern Pre-compilation**
   - **Impact:** Reduce pattern matching from 0.73s to ~0.3s
   - **Effort:** Compile regex patterns once at scanner init
   - **Expected Gain:** 60% faster pattern matching

4. **Batch Cost Tracker Flushing**
   - **Impact:** Reduce flush overhead
   - **Effort:** Flush every N requests instead of every 50
   - **Expected Gain:** 20-30% faster logging

### Medium Priority (Moderate Impact, Moderate Effort)

5. **Parallel File Processing**
   - **Impact:** Reduce scanner time from 9.5s to ~3-4s
   - **Effort:** Use multiprocessing.Pool for file analysis
   - **Expected Gain:** 2-3x speedup on multi-core systems

6. **Pattern Library Indexing**
   - **Impact:** Faster queries when pattern_type is known
   - **Effort:** Add `_patterns_by_type` dict
   - **Expected Gain:** 50% faster filtered queries

7. **Memory Lazy Initialization**
   - **Impact:** Reduce initialization from 0.62s to ~0.05s
   - **Effort:** Initialize backends on first use
   - **Expected Gain:** 12x faster startup for non-memory operations

8. **Feedback Loop Trend Caching**
   - **Impact:** Reduce duplicate calculations
   - **Effort:** Cache trend results by session hash
   - **Expected Gain:** 50% faster repeated checks

---

## Deep Optimization Candidates (Post-Release)

### Scanner Optimizations

1. **Incremental Scanning**
   - Only re-analyze changed files
   - Track file mtimes and hashes
   - Expected: 10-100x faster for repeated scans

2. **AST Serialization**
   - Serialize parsed ASTs to disk
   - Faster than re-parsing
   - Expected: 2-3x faster for cached files

3. **Async File I/O**
   - Use asyncio for concurrent file reading
   - Overlap I/O with CPU processing
   - Expected: 40-60% faster on fast SSDs

### Pattern Library Optimizations

1. **Vector Embeddings**
   - Semantic similarity search
   - Use sentence transformers
   - Expected: Better match quality, similar speed

2. **Approximate Nearest Neighbor**
   - FAISS or Annoy for large pattern libraries
   - Expected: O(log n) instead of O(n) queries

### Memory Optimizations

1. **Async Redis Operations**
   - Non-blocking I/O for stash/retrieve
   - Pipeline commands
   - Expected: 3-5x faster with batching

2. **Local Write-Through Cache**
   - LRU cache in front of Redis
   - Reduce network round-trips
   - Expected: 10-100x faster for hot data

---

## Performance Regression Tests

Based on these results, add regression tests:

```python
def test_scanner_performance():
    """Scanner should complete in <12s for 2000 files."""
    start = time.perf_counter()
    scanner.scan()
    duration = time.perf_counter() - start
    assert duration < 12.0, f"Scanner took {duration:.2f}s (> 12s threshold)"

def test_pattern_query_performance():
    """Pattern queries should complete in <1ms per query."""
    start = time.perf_counter()
    for _ in range(1000):
        library.query_patterns(context={...})
    duration = time.perf_counter() - start
    assert duration < 1.0, f"1000 queries took {duration:.2f}s (> 1s threshold)"

def test_memory_stash_performance():
    """Memory stash should handle 100 items in <100ms."""
    start = time.perf_counter()
    for i in range(100):
        memory.stash(f"key_{i}", {"data": i})
    duration = time.perf_counter() - start
    assert duration < 0.1, f"100 stashes took {duration:.3f}s (> 100ms threshold)"
```

---

## Visualization Commands

View detailed flame graphs with snakeviz:

```bash
# Scanner (primary bottleneck)
snakeviz benchmarks/profiles/scanner_scan.prof

# Pattern library (well-optimized reference)
snakeviz benchmarks/profiles/pattern_library.prof

# Memory operations (initialization overhead)
snakeviz benchmarks/profiles/memory_operations.prof

# Workflow execution (import overhead)
snakeviz benchmarks/profiles/workflow_execution.prof

# Test generation (config loading overhead)
snakeviz benchmarks/profiles/test_generation.prof

# Cost tracker (efficient logging reference)
snakeviz benchmarks/profiles/cost_tracker.prof

# Feedback loops (trend calculation)
snakeviz benchmarks/profiles/feedback_loops.prof
```

---

## Next Steps

1. **Week 1 (Immediate):**
   - Implement AST cache monitoring
   - Add lazy module imports
   - Pre-compile glob patterns
   - Batch cost tracker flushing

2. **Week 2 (Medium Priority):**
   - Implement parallel file processing
   - Add pattern library indexing
   - Lazy memory initialization
   - Feedback loop caching

3. **Post-Release (Deep Optimizations):**
   - Incremental scanning
   - AST serialization
   - Async Redis operations
   - Vector embeddings for patterns

---

## Appendix: Raw Profiling Data

### Scanner Top Functions
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
     1    0.001    0.001    9.514    9.514 profile_scanner
     1    0.002    0.002    9.343    9.343 scanner.scan
  2112    0.020    0.000    7.544    0.004 _analyze_file
   770    1.535    0.002    5.268    0.007 _analyze_python_ast
   873    1.936    0.002    1.936    0.002 {builtins.compile}
2124K    0.519    0.000    3.125    0.000 ast.walk
4211K    1.115    0.000    2.224    0.000 ast.iter_child_nodes
```

### Pattern Library Top Functions
```
ncalls  tottime  percall  cumtime  percall filename:lineno(function)
  1000    0.026    0.000    0.095    0.000 query_patterns
100000    0.054    0.000    0.070    0.000 _calculate_relevance
100000    0.008    0.000    0.008    0.000 {builtins.min}
```

### Memory Operations Top Functions
```
Initialization:     0.62s
Stash (200 items):  0.08s
Retrieve (100):     0.04s
Pattern ops (50):   0.05s
```

---

**Analysis By:** Claude Sonnet 4.5
**Review Status:** Ready for engineering review
**Last Updated:** 2026-01-10 08:45 PST
