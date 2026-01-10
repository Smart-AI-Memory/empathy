# Test Improvement Plan & Tracking

**Date Created:** January 10, 2026
**Current Status:** Phase 1 - Baseline Established
**Target Coverage:** 80%+
**Baseline Coverage:** 63.40%

---

## Executive Summary

Following completion of Phase 1-3 performance optimizations (1,300x cost tracker speedup, 1.54x scanner speedup), we've identified test coverage gaps through automated test-gen analysis and baseline measurement. This document tracks our phased approach to reach 80%+ coverage while prioritizing critical security tests.

### Current Test Suite Status

**Test Results:**
- ✅ **6,675 tests passing**
- ❌ 94 tests failing
- ⚠️ 72 test errors
- ⏭️ 87 tests skipped
- **Execution time:** 13:19 (799.65 seconds)

**Coverage Breakdown:**
- **Overall:** 63.40% (3,067 / 23,371 lines covered)
- **Target:** 80%+
- **Gap:** 16.6% (needs ~3,900 additional lines covered)

**Critical Low-Coverage Modules:**
- `src/empathy_os/scaffolding/cli.py` - **0.00%** (101 lines)
- `src/empathy_os/test_generator/` - **0.00%** (256 lines across 3 files)
- `src/empathy_os/workflow_commands.py` - **15.68%** (408 lines)
- `src/empathy_os/telemetry/cli.py` - **32.49%** (531 lines)
- `src/empathy_os/wizard_factory_cli.py` - **38.16%** (58 lines)

---

## Phase 1: Critical Security Tests (Priority: CRITICAL)

**Goal:** Address security vulnerabilities identified by test-gen analysis
**Target Coverage:** 65%
**Estimated Effort:** 1-2 days
**Status:** 🔄 In Progress

### 1.1 Redis Failure & Recovery Tests

**File:** `tests/unit/test_short_term_redis.py` (NEW)
**Lines to Add:** ~150 lines
**Severity:** CRITICAL

**Test Cases:**
```python
✅ test_redis_connection_failure_fallback()
   - Mock Redis connection timeout
   - Verify graceful degradation to in-memory storage
   - Ensure no data loss

✅ test_redis_authentication_failure()
   - Mock Redis AUTH failure
   - Verify error logging
   - Verify fallback behavior

✅ test_redis_connection_recovery()
   - Simulate connection loss then restore
   - Verify automatic reconnection
   - Verify data sync after recovery

✅ test_redis_partial_write_failure()
   - Simulate write failure mid-transaction
   - Verify rollback or retry logic
   - Ensure data consistency
```

**Acceptance Criteria:**
- All Redis failure scenarios handled gracefully
- No unhandled exceptions in production code
- Fallback to in-memory storage works
- Connection recovery is automatic

---

### 1.2 Security Validation & Injection Prevention

**File:** `tests/unit/test_long_term_security.py` (NEW)
**Lines to Add:** ~200 lines
**Severity:** CRITICAL

**Test Cases:**
```python
✅ test_secure_pattern_prevents_code_injection()
   - Test SecurePattern.validate() with malicious patterns
   - Patterns: eval(), exec(), __import__(), os.system()
   - Verify all dangerous patterns blocked

✅ test_secure_pattern_prevents_sql_injection()
   - Test SQL-like patterns in search queries
   - Patterns: '; DROP TABLE, UNION SELECT, --
   - Verify proper escaping/rejection

✅ test_secure_pattern_prevents_path_traversal()
   - Test path inputs: ../../etc/passwd, ..\\..\\Windows
   - Verify _validate_file_path() blocks traversal
   - Test with null bytes: path\x00.txt

✅ test_secure_pattern_allows_safe_inputs()
   - Test legitimate patterns pass validation
   - Verify no false positives on safe code
```

**Acceptance Criteria:**
- SecurePattern blocks all OWASP Top 10 patterns
- No false positives on legitimate code
- Path traversal prevention 100% effective
- All dangerous patterns logged

---

### 1.3 Cache Eviction & TTL Tests

**File:** `tests/unit/test_hybrid_cache.py` (NEW)
**Lines to Add:** ~120 lines
**Severity:** HIGH

**Test Cases:**
```python
✅ test_cache_respects_ttl()
   - Store item with 1-second TTL
   - Wait 2 seconds
   - Verify item expired and removed

✅ test_lru_eviction_when_full()
   - Fill cache to maxsize
   - Add one more item
   - Verify least recently used item evicted

✅ test_cache_invalidation_on_update()
   - Store item with key "x"
   - Update "x" with new value
   - Verify old value properly invalidated

✅ test_cache_stats_tracking()
   - Perform mix of hits and misses
   - Verify cache_info() returns accurate stats
   - Verify hit rate calculation correct
```

**Acceptance Criteria:**
- TTL expiration works within 1-second accuracy
- LRU eviction prevents unbounded growth
- Cache statistics accurate
- No memory leaks

---

## Phase 2: High-Value Quick Wins (Priority: HIGH)

**Goal:** Add high-impact tests with minimal effort
**Target Coverage:** 75%
**Estimated Effort:** 1 day
**Status:** ⏳ Pending

### 2.1 Zero Vector Tests (15 minutes)

**File:** `src/empathy_os/embeddings.py`
**Test:** `tests/unit/test_embeddings.py::test_cosine_similarity_zero_vector`

```python
def test_cosine_similarity_zero_vector():
    """Test cosine_similarity handles zero vectors without division by zero."""
    zero_vec = [0.0, 0.0, 0.0]
    normal_vec = [1.0, 2.0, 3.0]

    # Should handle gracefully (return 0.0 or raise ValueError)
    result = cosine_similarity(zero_vec, normal_vec)
    assert result == 0.0 or isinstance(result, (ValueError, ZeroDivisionError))
```

**Impact:** Prevents production crashes on edge case inputs

---

### 2.2 HTTP Status Code Tests (15 minutes)

**File:** `src/empathy_os/wizards/wizard_api.py`
**Test:** `tests/unit/test_wizard_api.py::test_http_error_handling`

```python
def test_http_error_handling():
    """Test wizard API handles HTTP errors gracefully."""
    with patch('requests.post') as mock_post:
        # Test 500 Internal Server Error
        mock_post.return_value = Mock(status_code=500, text="Error")
        result = call_wizard_api("/analyze", {})
        assert "error" in result

        # Test 401 Unauthorized
        mock_post.return_value = Mock(status_code=401)
        result = call_wizard_api("/analyze", {})
        assert "authentication" in str(result).lower()
```

**Impact:** Ensures API failures don't crash application

---

### 2.3 File Permission Tests (15 minutes)

**File:** `src/empathy_os/project_index/scanner.py`
**Test:** `tests/unit/test_scanner_permissions.py::test_scanner_handles_permission_denied`

```python
def test_scanner_handles_permission_denied(tmp_path):
    """Test scanner handles permission denied errors gracefully."""
    # Create unreadable file
    unreadable = tmp_path / "secret.py"
    unreadable.write_text("# secret code")
    unreadable.chmod(0o000)

    scanner = ProjectScanner(project_root=str(tmp_path))
    records, summary = scanner.scan()

    # Should skip unreadable files without crashing
    assert summary.total_files >= 0
    assert not any(r.file_path == str(unreadable) for r in records)

    # Cleanup
    unreadable.chmod(0o644)
```

**Impact:** Scanner doesn't crash on restricted files

---

## Phase 3: Polish & Complete (Priority: MEDIUM)

**Goal:** Reach 80%+ coverage across all modules
**Target Coverage:** 80%+
**Estimated Effort:** 2-3 days
**Status:** ⏳ Pending

### 3.1 CLI Command Tests

**Files:**
- `tests/unit/test_cli_unified.py` (94 failing tests - needs fixes)
- `tests/unit/test_scaffolding_cli.py` (NEW - 0% coverage)

**Key Tests:**
- Provider commands (show, registry, costs)
- Scan commands (default, json, staged)
- Inspect commands (default, sarif)
- Workflow commands (ship, health, learn)

**Effort:** 1 day

---

### 3.2 Telemetry & Analytics Tests

**File:** `src/empathy_os/telemetry/cli.py` (32.49% coverage)

**Test Cases:**
```python
✅ test_export_csv_with_data()
✅ test_export_json_with_filters()
✅ test_telemetry_summary_calculation()
✅ test_cost_breakdown_by_model()
✅ test_telemetry_chart_generation()
```

**Effort:** 4 hours

---

### 3.3 Workflow Command Tests

**File:** `src/empathy_os/workflow_commands.py` (15.68% coverage)

**Test Cases:**
```python
✅ test_workflow_list_all()
✅ test_workflow_run_with_params()
✅ test_workflow_describe()
✅ test_workflow_error_handling()
```

**Effort:** 4 hours

---

### 3.4 XML Configuration Tests

**File:** `src/empathy_os/validation/xml_validator.py` (73.50% coverage)

**Test Cases:**
```python
✅ test_validate_malformed_xml()
✅ test_validate_xml_injection_attempts()
✅ test_validate_dtd_entity_expansion()
✅ test_xml_export_escaping()
```

**Effort:** 2 hours

---

## Coverage Progress Tracking

### Baseline (January 10, 2026)

| Module Category | Coverage | Lines | Target |
|-----------------|----------|-------|--------|
| **Core** | 85.2% | 5,234 | ✅ 85%+ |
| **Workflows** | 68.4% | 8,921 | 🔄 75%+ |
| **CLI/Tools** | 21.3% | 1,890 | ❌ 70%+ |
| **Telemetry** | 32.5% | 706 | ❌ 70%+ |
| **Test Gen** | 0.0% | 256 | ❌ 60%+ |
| **Overall** | **63.4%** | **23,371** | **80%+** |

### Phase 1 Target (After Critical Tests)

| Module Category | Coverage | Increase |
|-----------------|----------|----------|
| Core | 90.0% | +4.8% |
| Workflows | 70.0% | +1.6% |
| CLI/Tools | 25.0% | +3.7% |
| **Overall** | **65.0%** | **+1.6%** |

### Phase 2 Target (After Quick Wins)

| Module Category | Coverage | Increase |
|-----------------|----------|----------|
| Core | 93.0% | +3.0% |
| Workflows | 75.0% | +5.0% |
| CLI/Tools | 40.0% | +15.0% |
| **Overall** | **75.0%** | **+10.0%** |

### Phase 3 Target (Final Polish)

| Module Category | Coverage | Increase |
|-----------------|----------|----------|
| Core | 95.0% | +2.0% |
| Workflows | 80.0% | +5.0% |
| CLI/Tools | 70.0% | +30.0% |
| Telemetry | 70.0% | +37.5% |
| **Overall** | **82.0%+** | **+7.0%** |

---

## Test Failures & Errors Analysis

### Critical Failures (Must Fix - Phase 1)

**94 failing tests** across multiple categories:

1. **CrewAI Integration (8 failures)**
   - `test_crewai_adapter.py` - Tool creation fallback
   - `test_security_audit_crew.py` - Crew initialization
   - `test_security_crew_integration.py` - Integration tests

2. **CLI Tests (65 failures)**
   - `test_cli_unified.py` - 65 tests failing
   - Likely due to API changes or missing mocks
   - **Action:** Review and update CLI test fixtures

3. **Workflow Tests (14 failures)**
   - `test_tier_fallback.py` - 8 failures (tier fallback system)
   - `test_code_review_pipeline_workflow.py` - 3 failures
   - `test_secure_release_workflow.py` - 2 failures

4. **Platform Tests (5 failures)**
   - `test_platform_utils.py` - Windows/Linux path handling
   - **Action:** Add platform-specific mocks

### Test Errors (72 errors - Phase 2)

**Major error categories:**

1. **Bug Predict Helpers (43 errors)**
   - `test_bug_predict_helpers.py` - All tests erroring
   - Likely import or fixture issue
   - **Action:** Fix module imports first

2. **Health Check Exceptions (18 errors)**
   - `test_health_check_exceptions.py` - All tests erroring
   - **Action:** Review exception handling mocks

3. **Workflow Helpers (11 errors)**
   - Document manager, manage docs, test5 workflow tests
   - **Action:** Fix workflow base class issues

---

## Implementation Guidelines

### Test Writing Standards

All new tests MUST follow:

1. **Security Testing Requirements:**
   ```python
   def test_blocks_injection_attack():
       """Test that function blocks SQL injection attempts."""
       malicious_input = "'; DROP TABLE users--"

       with pytest.raises(ValueError, match="Invalid input"):
           validate_query(malicious_input)
   ```

2. **Exception Handling:**
   ```python
   def test_graceful_degradation():
       """Test graceful degradation when Redis unavailable."""
       with patch('redis.Redis') as mock_redis:
           mock_redis.side_effect = ConnectionError("Cannot connect")

           # Should fall back to in-memory storage
           result = store_data("key", "value")
           assert result is not None
   ```

3. **Edge Cases:**
   ```python
   @pytest.mark.parametrize("input_vec", [
       [],  # Empty vector
       [0.0, 0.0, 0.0],  # Zero vector
       [float('inf')],  # Infinity
       [float('nan')],  # NaN
   ])
   def test_cosine_similarity_edge_cases(input_vec):
       """Test cosine_similarity handles edge cases."""
       # Should not crash
       result = cosine_similarity(input_vec, [1.0, 2.0, 3.0])
       assert isinstance(result, (float, type(None)))
   ```

4. **Mocking External Dependencies:**
   ```python
   def test_api_call_with_network_error():
       """Test API call handles network errors gracefully."""
       with patch('requests.post') as mock_post:
           mock_post.side_effect = requests.ConnectionError("Network down")

           result = call_api("/endpoint", data={})
           assert "error" in result
           assert result["error"] == "network_error"
   ```

### Code Coverage Requirements

- **Minimum:** 80% line coverage
- **Branches:** 75% branch coverage
- **Security-critical code:** 95%+ coverage

### Documentation Requirements

Each test module MUST include:

```python
"""Tests for [module_name].

Test Categories:
    - Unit Tests: Test individual functions in isolation
    - Integration Tests: Test component interactions
    - Security Tests: Test security validation and error handling
    - Edge Cases: Test boundary conditions and error scenarios

Coverage:
    Target: 90%+
    Current: [X]%

Related:
    - Source: src/empathy_os/[module].py
    - Docs: docs/[MODULE].md
"""
```

---

## Running Tests

### Full Test Suite with Coverage

```bash
# Run all tests with coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html -v

# View HTML coverage report
open htmlcov/index.html
```

### Run Specific Test Category

```bash
# Run only security tests
pytest tests/unit/test_*_security.py -v

# Run only quick win tests
pytest tests/unit/test_embeddings.py::test_cosine_similarity_zero_vector -v
pytest tests/unit/test_wizard_api.py::test_http_error_handling -v
pytest tests/unit/test_scanner_permissions.py -v

# Run failing tests only
pytest --lf  # Last failed

# Run new tests only
pytest --nf  # New first
```

### Coverage by Module

```bash
# Check coverage for specific module
pytest --cov=src/empathy_os/cost_tracker --cov-report=term-missing

# Generate coverage JSON for analysis
pytest --cov=src --cov-report=json
jq '.files."src/empathy_os/cost_tracker.py".summary' coverage.json
```

---

## Success Criteria

### Phase 1 Complete When:
- ✅ All critical security tests passing
- ✅ Redis failure scenarios covered
- ✅ Injection prevention validated
- ✅ Cache eviction working correctly
- ✅ Coverage reaches 65%+

### Phase 2 Complete When:
- ✅ All quick win tests added
- ✅ Zero vector handling tested
- ✅ HTTP error handling tested
- ✅ File permission handling tested
- ✅ Coverage reaches 75%+

### Phase 3 Complete When:
- ✅ All CLI tests passing (65 fixed)
- ✅ All workflow errors resolved (72 fixed)
- ✅ Coverage reaches 80%+
- ✅ No critical gaps remain
- ✅ Documentation updated

---

## Related Documentation

- [CODING_STANDARDS.md](./CODING_STANDARDS.md) - Testing requirements
- [PHASE2_IMPLEMENTATION_SUMMARY.md](./PHASE2_IMPLEMENTATION_SUMMARY.md) - Performance optimizations
- [PERFORMANCE_OPTIMIZATION_COMPLETE.md](./PERFORMANCE_OPTIMIZATION_COMPLETE.md) - Complete optimization history
- [.claude/rules/empathy/coding-standards-index.md](../.claude/rules/empathy/coding-standards-index.md) - Quick reference

---

## Change Log

| Date | Phase | Coverage | Notes |
|------|-------|----------|-------|
| 2026-01-10 | Baseline | 63.40% | Initial measurement, 6,675 passing |
| TBD | Phase 1 | 65%+ | Critical security tests |
| TBD | Phase 2 | 75%+ | Quick wins |
| TBD | Phase 3 | 82%+ | Final polish |

---

**Next Action:** Implement Phase 1 critical security tests starting with Redis failure handling.

**Owner:** Development Team
**Priority:** CRITICAL
**Deadline:** Phased approach (see timeline above)
