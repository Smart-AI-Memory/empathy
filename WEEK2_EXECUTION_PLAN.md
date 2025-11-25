# Week 2 Execution Plan: Performance + Wizards
**Phase 3, Week 2 of 10**
**Approach:** Option C (Performance First) → Option A (Full Wizard Integration)
**Timeline:** 52 hours total
**Status:** Not Started

---

## 🎯 **Objectives**

1. **Optimize performance to <10ms overhead** (from current <20ms)
2. **Enhance Healthcare wizard with HIPAA++ features**
3. **Update all 16 wizards with security pipeline**
4. **Create comprehensive wizard test suite**
5. **Achieve <15ms with Memory + Security combined**

---

## 📅 **Phase 1: Performance Optimization (24h)**

### **Task 1: Performance Profiling (4h)**
**Goal:** Identify bottlenecks in current pipeline

**Actions:**
- Profile PII scrubber with cProfile
- Profile secrets detector with line_profiler
- Profile audit logger I/O operations
- Profile complete pipeline end-to-end
- Identify top 10 hotspots

**Deliverables:**
- `performance_profile_baseline.md`
- Flamegraph visualizations
- Bottleneck analysis report

**Success Criteria:**
- All modules profiled
- Bottlenecks identified with line-level precision
- Optimization targets prioritized

---

### **Task 2: Optimize PII Scrubber (6h)**
**Current:** 3-5ms/KB
**Target:** <3ms/KB (50% improvement)

**Optimization Strategies:**
1. **Pre-compile regex patterns** - Already done, verify
2. **Cache pattern results** - Add LRU cache for common patterns
3. **Parallel pattern matching** - Use ProcessPoolExecutor for large texts
4. **Reduce allocations** - Reuse buffers, avoid string copies
5. **Fast path for common cases** - Early exit if no PII patterns match

**Implementation:**
```python
from functools import lru_cache
from concurrent.futures import ProcessPoolExecutor

class PIIScrubber:
    def __init__(self):
        self._executor = ProcessPoolExecutor(max_workers=2)
        self._pattern_cache = {}  # Pattern match cache

    @lru_cache(maxsize=1024)
    def _fast_check(self, content_hash: str) -> bool:
        """Fast check if content likely contains PII"""
        # Check for common PII indicators before full scan
        return any(indicator in content_hash for indicator in
                   ['@', '-', '(', 'ssn', 'phone'])

    def scrub(self, content: str) -> tuple[str, list[PIIDetection]]:
        # Fast path: skip if no PII indicators
        if not self._fast_check(hash(content)):
            return content, []

        # Regular scrubbing logic
        ...
```

**Deliverables:**
- Optimized PII scrubber code
- Performance benchmarks showing <3ms/KB
- Unit tests still passing

---

### **Task 3: Optimize Secrets Detector (6h)**
**Current:** 10-20ms/KB
**Target:** <8ms/KB (60% improvement)

**Optimization Strategies:**
1. **Optimize entropy calculation** - Use faster Shannon entropy algorithm
2. **Parallel secret scanning** - Split content into chunks, scan in parallel
3. **Early termination** - Stop on first critical secret for blocking scenarios
4. **Reduce regex backtracking** - Optimize regex patterns
5. **Cache entropy results** - LRU cache for high-entropy strings

**Implementation:**
```python
def calculate_entropy_fast(data: str) -> float:
    """Optimized Shannon entropy calculation"""
    if not data:
        return 0.0

    # Use numpy for faster calculations
    import numpy as np
    counts = np.bincount(np.frombuffer(data.encode(), dtype=np.uint8))
    probabilities = counts[counts > 0] / len(data)
    return -np.sum(probabilities * np.log2(probabilities))
```

**Deliverables:**
- Optimized secrets detector
- Performance benchmarks showing <8ms/KB
- Entropy analysis still accurate

---

### **Task 4: Optimize Audit Logger (2h)**
**Current:** 1-3ms per event
**Target:** <1.5ms per event

**Optimization Strategies:**
1. **Batch writes** - Buffer multiple events, write in batches
2. **Async I/O** - Use asyncio for non-blocking writes
3. **Reduce JSON serialization overhead** - Use ujson or orjson
4. **Pre-format common fields** - Cache formatted timestamps

**Implementation:**
```python
import asyncio
import orjson  # Faster than json

class AuditLogger:
    def __init__(self, batch_size: int = 10):
        self._event_buffer = []
        self._batch_size = batch_size

    async def log_event_async(self, event: AuditEvent):
        """Async non-blocking logging"""
        self._event_buffer.append(event)

        if len(self._event_buffer) >= self._batch_size:
            await self._flush_buffer()

    async def _flush_buffer(self):
        """Batch write all buffered events"""
        if not self._event_buffer:
            return

        async with aiofiles.open(self.log_file, 'a') as f:
            for event in self._event_buffer:
                await f.write(orjson.dumps(event.to_dict()) + b'\n')

        self._event_buffer.clear()
```

**Deliverables:**
- Optimized audit logger
- Benchmarks showing <1.5ms per event
- Backward compatibility maintained

---

### **Task 5: End-to-End Pipeline Optimization (4h)**
**Current:** <20ms
**Target:** <10ms (50% improvement)

**Optimization Strategies:**
1. **Pipeline parallelization** - Run PII scrubbing + secrets detection in parallel
2. **Reduce data copies** - Pass references instead of copying strings
3. **Lazy evaluation** - Only run expensive operations when needed
4. **Memory pooling** - Reuse buffers across requests

**Implementation:**
```python
async def store_pattern_optimized(self, content: str, **kwargs):
    """Optimized pipeline with parallel execution"""
    # Step 1: Validate (fast)
    self._validate(content)

    # Step 2 & 3: Run PII scrubbing and secrets detection in PARALLEL
    pii_task = asyncio.create_task(self._scrub_pii_async(content))
    secrets_task = asyncio.create_task(self._detect_secrets_async(content))

    sanitized, pii_detections = await pii_task
    secrets_found = await secrets_task

    if secrets_found:
        raise SecurityError("Secrets detected")

    # Step 4: Classification (fast - keyword matching)
    classification = self._classify(sanitized, kwargs.get('pattern_type'))

    # Step 5 & 6: Encryption + Storage (parallel)
    if classification == 'SENSITIVE':
        encrypted = await self._encrypt_async(sanitized)
    else:
        encrypted = sanitized

    pattern_id = await self._store_async(encrypted, classification)

    # Step 7: Audit logging (async, non-blocking)
    asyncio.create_task(self._log_async(pattern_id, classification))

    return {"pattern_id": pattern_id, "classification": classification}
```

**Deliverables:**
- Complete pipeline optimized
- Benchmarks showing <10ms end-to-end
- All tests still passing

---

### **Task 6: Healthcare Wizard HIPAA++ (2h)**
**Goal:** Enhance Healthcare wizard with additional HIPAA safeguards

**Enhancements:**
1. **Automatic PHI detection** - Enhanced PII patterns for medical data
2. **90-day retention enforcement** - Automatic cleanup
3. **Audit ALL access** - Every interaction logged
4. **Encrypted storage mandatory** - No plaintext PHI
5. **De-identification by default** - Scrub before any LLM calls

**Implementation:**
```python
class HealthcareWizard(BaseWizard):
    """HIPAA-compliant healthcare AI wizard"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # HIPAA-specific configuration
        self.security_config = {
            'enable_security': True,
            'pii_scrubbing': {
                'enabled': True,
                'patterns': ['email', 'phone', 'ssn', 'mrn', 'patient_id',
                             'dob', 'address', 'insurance_id'],
                'enable_name_detection': True,  # Catch patient names
            },
            'secrets_detection': {
                'enabled': True,
                'block_on_detection': True,
            },
            'audit_logging': {
                'enabled': True,
                'audit_all_access': True,  # HIPAA requirement
                'retention_days': 2555,  # 7 years for HIPAA
            },
            'classification': {
                'default_classification': 'SENSITIVE',  # PHI is always SENSITIVE
                'auto_classify': True,
            },
            'encryption_required': True,  # PHI must be encrypted
            'retention_days': 90,  # Minimum retention for PHI
        }

    async def process(self, user_input: str, user_id: str) -> dict:
        """Process with HIPAA compliance"""
        # Step 1: Audit log access
        self.audit_logger.log_phi_access(user_id, self.name)

        # Step 2: De-identify before processing
        deidentified_input, phi_detected = self.pii_scrubber.scrub(user_input)

        if phi_detected:
            logger.warning(f"PHI detected and scrubbed: {len(phi_detected)} instances")

        # Step 3: Process with EmpathyLLM (de-identified data only)
        response = await self.llm.interact(
            user_id=user_id,
            user_input=deidentified_input,
            empathy_level=self.empathy_level,
            security_config=self.security_config
        )

        # Step 4: Audit log completion
        self.audit_logger.log_phi_processing_complete(user_id, self.name, phi_detected)

        return response
```

**Additional PHI Patterns:**
```python
# Medical Record Number (MRN)
r'\bMRN:?\s*\d{6,10}\b'

# Date of Birth
r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'

# Insurance ID
r'\b[A-Z]{2,3}\d{8,12}\b'

# Patient ID
r'\bPT\d{6,10}\b'

# Medical procedures (CPT codes)
r'\bCPT:?\s*\d{5}\b'

# Diagnosis codes (ICD-10)
r'\b[A-Z]\d{2}\.\d{1,2}\b'
```

**Deliverables:**
- Enhanced Healthcare wizard
- HIPAA compliance verification tests
- Documentation of HIPAA safeguards

---

## 📅 **Phase 2: Full Wizard Integration (28h)**

### **Task 7: Update All 16 Wizards (16h)**
**Goal:** Make all wizards security-aware

**Wizard List:**
1. ✅ Healthcare Wizard (already done in Phase 1)
2. Code Review Wizard
3. Bug Fix Wizard
4. Feature Development Wizard
5. Refactoring Wizard
6. Testing Wizard
7. Documentation Wizard
8. Performance Optimization Wizard
9. Security Audit Wizard
10. Database Design Wizard
11. API Design Wizard
12. UI/UX Design Wizard
13. DevOps Wizard
14. Data Analysis Wizard
15. ML/AI Wizard
16. General Purpose Wizard

**Integration Pattern (apply to all):**
```python
class BaseWizard:
    """Base wizard with security integration"""

    def __init__(self, llm: EmpathyLLM, security_config: dict = None):
        self.llm = llm
        self.security_config = security_config or {
            'enable_security': False,  # Disabled by default for backward compat
        }

    async def process(self, user_input: str, user_id: str) -> dict:
        """Process with optional security"""
        # Use EmpathyLLM with security if enabled
        response = await self.llm.interact(
            user_id=user_id,
            user_input=user_input,
            empathy_level=self.empathy_level,
            security_config=self.security_config
        )

        return response
```

**Priority Wizards (do first):**
1. Healthcare (DONE)
2. Code Review (high usage)
3. Bug Fix (high usage)
4. Feature Development (high usage)
5. Security Audit (security-critical)

**Deliverables:**
- All 16 wizards updated
- Each wizard has security_config parameter
- All wizards work with Memory + Security
- Backward compatibility maintained

---

### **Task 8: Create Wizard Test Suite (8h)**
**Goal:** Comprehensive tests for all wizards

**Test Structure:**
```
tests/test_wizards/
├── test_wizard_security_integration.py  # Test security works for all
├── test_healthcare_wizard_hipaa.py       # HIPAA-specific tests
├── test_code_review_wizard.py            # Code review wizard tests
├── test_bug_fix_wizard.py                # Bug fix wizard tests
└── ... (one file per wizard)
```

**Test Template:**
```python
class TestWizardSecurityIntegration:
    """Test security integration for all wizards"""

    @pytest.mark.parametrize("wizard_class", [
        HealthcareWizard,
        CodeReviewWizard,
        BugFixWizard,
        # ... all 16 wizards
    ])
    def test_wizard_with_security_enabled(self, wizard_class):
        """Test wizard works with security enabled"""
        llm = EmpathyLLM(
            provider="anthropic",
            api_key="test-key",
            enable_security=True
        )

        wizard = wizard_class(llm)

        # Test with PII
        user_input = "Contact john@example.com about patient MRN 123456"
        result = wizard.process(user_input, "test@company.com")

        # Verify PII was scrubbed
        assert "john@example.com" not in result["sanitized_input"]
        assert "[EMAIL]" in result["sanitized_input"]

    @pytest.mark.parametrize("wizard_class", ALL_WIZARDS)
    def test_wizard_blocks_secrets(self, wizard_class):
        """Test wizard blocks secrets"""
        wizard = wizard_class(llm_with_security)

        user_input = 'api_key = "sk-live-secret123"'

        with pytest.raises(SecurityError):
            wizard.process(user_input, "test@company.com")
```

**Test Coverage Targets:**
- 90%+ coverage for each wizard
- Security integration tests for all 16 wizards
- HIPAA compliance tests for Healthcare wizard
- Performance tests (ensure <10ms overhead)

**Deliverables:**
- Comprehensive wizard test suite
- 90%+ test coverage achieved
- All tests passing

---

### **Task 9: Integration Testing (4h)**
**Goal:** Verify Memory + Security + Wizards work together

**Integration Test Scenarios:**

**Scenario 1: Healthcare Wizard with Memory + Security**
```python
def test_healthcare_wizard_full_stack():
    """Test healthcare wizard with full stack"""
    # Setup Claude Memory with HIPAA policies
    config = ClaudeMemoryConfig(
        enabled=True,
        load_enterprise=True,  # Load HIPAA policies
    )

    # Setup LLM with security
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_security=True,
        claude_memory_config=config
    )

    # Initialize wizard
    wizard = HealthcareWizard(llm)

    # Test with PHI
    result = wizard.process(
        "Patient John Doe (MRN 123456) needs follow-up",
        user_id="doctor@hospital.com"
    )

    # Verify PHI scrubbed
    assert "John Doe" not in result["llm_input"]
    assert "[NAME]" in result["llm_input"]
    assert "123456" not in result["llm_input"]
    assert "[MRN]" in result["llm_input"]

    # Verify audit trail
    audit_logs = get_audit_logs()
    assert any(log["event_type"] == "phi_access" for log in audit_logs)
```

**Performance Test:**
```python
def test_memory_security_performance():
    """Test Memory + Security overhead is <15ms"""
    llm = EmpathyLLM(
        enable_security=True,
        claude_memory_config=ClaudeMemoryConfig(enabled=True)
    )

    wizard = CodeReviewWizard(llm)

    # Measure performance
    start = time.time()
    for _ in range(100):
        wizard.process("Review this code: def foo(): pass", "test@company.com")
    elapsed = (time.time() - start) / 100 * 1000

    assert elapsed < 15.0, f"Performance regression: {elapsed}ms > 15ms"
```

**Deliverables:**
- Integration tests for Memory + Security + Wizards
- Performance tests showing <15ms overhead
- All integration tests passing

---

## ✅ **Week 2 Acceptance Criteria**

### **Performance:**
- [ ] PII scrubber: <3ms/KB (from 3-5ms/KB)
- [ ] Secrets detector: <8ms/KB (from 10-20ms/KB)
- [ ] Audit logger: <1.5ms/event (from 1-3ms/event)
- [ ] Complete pipeline: <10ms (from <20ms)
- [ ] Memory + Security: <15ms (new metric)

### **Features:**
- [ ] Healthcare wizard HIPAA++ complete
- [ ] All 16 wizards security-aware
- [ ] Backward compatibility maintained (security disabled by default)

### **Testing:**
- [ ] Wizard test suite: 90%+ coverage
- [ ] All wizard tests passing
- [ ] Integration tests passing
- [ ] Performance benchmarks met

### **Documentation:**
- [ ] Performance optimization report
- [ ] Wizard security integration guide
- [ ] HIPAA compliance documentation

---

## 🚀 **Next Steps (Week 3)**

After Week 2 completion:
- Begin VSCode security UI implementation
- Design security settings panel
- Create audit log viewer

---

**Document Version:** 1.0
**Created:** 2025-11-24
**Status:** Ready for execution
**Estimated Completion:** Week 2 end
