# Test Coverage Improvement Plan

**Current:** 75.90% (1,491 tests)
**Target:** 90%+
**Estimated New Tests:** ~150-180 test cases

---

## Phase 1: Security Modules (Priority: CRITICAL)

### 1.1 PII Scrubber (60% → 90%)
**Estimated Tests:** 25

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| Custom pattern management | 8 | Yes |
| Overlapping PII detection | 5 | Yes |
| Pattern validation suite | 8 | Yes |
| Healthcare PII variants | 4 | Yes |

### 1.2 Secure MemDocs (75% → 95%)
**Estimated Tests:** 30

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| Encryption/decryption operations | 10 | Yes |
| Pattern classification logic | 8 | Yes |
| Access control enforcement | 8 | Yes |
| Retention policy validation | 4 | Yes |

### 1.3 Audit Logger (73% → 92%)
**Estimated Tests:** 25

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| Directory initialization | 4 | Yes |
| Log rotation and cleanup | 8 | Yes |
| Query operators | 8 | Yes |
| Compliance reporting | 5 | Yes |

---

## Phase 2: Claude Memory Integration (72% → 95%)

**Estimated Tests:** 20

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| Enterprise memory loading | 5 | Yes |
| User memory loading | 4 | Yes |
| Error handling paths | 6 | Yes |
| Import processing edge cases | 5 | Yes |

---

## Phase 3: CLI Modules

### 3.1 empathy_software_plugin/cli.py (34% → 75%)
**Estimated Tests:** 35

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| analyze_project() async | 10 | No (integration) |
| gather_project_context() | 8 | Yes |
| scan_command() | 10 | Yes |
| list_wizards/wizard_info | 7 | Yes |

### 3.2 src/empathy_os/cli.py (45% → 80%)
**Estimated Tests:** 40

| Test Category | Tests | Parallelizable |
|---------------|-------|----------------|
| cmd_run() interactive REPL | 12 | No (sequential) |
| cmd_inspect() branches | 8 | Yes |
| cmd_export/import | 10 | Yes |
| cmd_wizard() flow | 10 | Yes |

---

## Parallel Execution Strategy

### Batch 1 (Security - Can Run Simultaneously)
```
Agent A: PII Scrubber tests (25 tests)
Agent B: Secure MemDocs tests (30 tests)
Agent C: Audit Logger tests (25 tests)
Agent D: Claude Memory tests (20 tests)
```

### Batch 2 (CLI - Sequential Dependencies)
```
Agent E: Software plugin CLI (35 tests)
Agent F: EmpathyOS CLI (40 tests)
```

---

## Test Fixtures Required

### Shared Fixtures (Create First)
```python
# conftest.py additions

@pytest.fixture
def temp_project_with_ai_files(tmp_path):
    """Project with AI library imports"""

@pytest.fixture
def mock_registry():
    """Mock plugin registry"""

@pytest.fixture
def mock_empathy_os():
    """Mock EmpathyOS instance"""

@pytest.fixture
def simulate_user_input(monkeypatch):
    """Interactive input simulation"""

@pytest.fixture
def encryption_key():
    """Valid AES-256 key for testing"""

@pytest.fixture
def mock_audit_directory(tmp_path):
    """Temporary audit log directory"""
```

---

## Execution Order

1. **Create fixtures** (conftest.py) - 30 min
2. **Phase 1 Batch** (Security) - Parallel agents - 2 hours
3. **Phase 2** (Claude Memory) - Single agent - 1 hour
4. **Phase 3 Batch** (CLI) - Parallel agents - 2 hours
5. **Integration tests** - Sequential - 1 hour
6. **Coverage verification** - Final run - 30 min

**Total estimated time: 6-7 hours**

---

## Success Criteria

| Module | Before | After | Delta |
|--------|--------|-------|-------|
| pii_scrubber.py | 60% | 90% | +30% |
| secure_memdocs.py | 75% | 95% | +20% |
| audit_logger.py | 73% | 92% | +19% |
| claude_memory.py | 72% | 95% | +23% |
| software_plugin/cli.py | 34% | 75% | +41% |
| empathy_os/cli.py | 45% | 80% | +35% |
| **OVERALL** | **75.9%** | **90%+** | **+14%** |

---

## Agent Task Assignments

When ready to execute, spawn these agents in parallel:

```
Task 1: "Write tests for PII scrubber custom patterns and overlaps"
Task 2: "Write tests for secure_memdocs encryption and access control"
Task 3: "Write tests for audit_logger rotation and compliance"
Task 4: "Write tests for claude_memory enterprise/user loading"
Task 5: "Write tests for software_plugin CLI commands"
Task 6: "Write tests for empathy_os CLI interactive commands"
```
