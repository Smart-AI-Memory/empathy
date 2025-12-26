# Multi-Model Architecture: Phase 2–3 Implementation Plan

**Version:** 1.3
**Date:** 2025-12-25
**Status:** Phase 2–3 Complete ✅

---

## Completion Summary

### Phase 2 Completed (2025-12-25)

All Phase 2 tasks have been implemented and tested:

| Phase | Status | Test Coverage |
|-------|--------|---------------|
| 2.0 Foundation Verification | ✅ Complete | 82 tests passing |
| 2.1 LLMExecutor Interface | ✅ Complete | ExecutionContext, LLMResponse, MockLLMExecutor |
| 2.2 EmpathyLLMExecutor | ✅ Complete | Telemetry integration |
| 2.3 ResilientExecutor | ✅ Complete | CircuitBreaker per provider:tier |
| 2.4 BaseWorkflow Integration | ✅ Complete | `_get_executor()`, `_create_default_executor()` |
| 2.5 Integration Tests | ✅ Complete | 28 new tests in `test_executor_integration.py` |

**Key Files Modified:**
- `src/empathy_os/models/executor.py` - ExecutionContext, LLMResponse, LLMExecutor protocol
- `src/empathy_os/models/empathy_executor.py` - EmpathyLLMExecutor with telemetry
- `src/empathy_os/models/fallback.py` - CircuitBreaker, ResilientExecutor
- `src/empathy_os/workflows/base.py` - `_get_executor()`, `_create_default_executor()`
- `tests/test_executor_integration.py` - Integration tests

### Phase 3 Completed (2025-12-25)

All Phase 3 Wave 1 tasks have been implemented:

| Phase | Status | Details |
|-------|--------|---------|
| 3.1 Wave 1: security_audit.py | ✅ Complete | Uses `run_step_with_executor()` for remediate stage |
| 3.1 Wave 1: bug_predict.py | ✅ Complete | Uses `run_step_with_executor()` for recommend stage |
| 3.1 Wave 1: perf_audit.py | ✅ Complete | Uses `run_step_with_executor()` for optimize stage |
| 3.3 Telemetry CLI | ✅ Complete | Already implemented in `cli.py` |

**Key Files Modified:**
- `src/empathy_os/workflows/security_audit.py` - Added `SECURITY_STEPS`, executor integration
- `src/empathy_os/workflows/bug_predict.py` - Added `BUG_PREDICT_STEPS`, executor integration
- `src/empathy_os/workflows/perf_audit.py` - Added `PERF_AUDIT_STEPS`, executor integration

**CLI Commands Available:**
- `python -m empathy_os.models.cli registry` - Show model registry
- `python -m empathy_os.models.cli tasks` - Show task-to-tier mappings
- `python -m empathy_os.models.cli telemetry` - Show telemetry summary
- `python -m empathy_os.models.cli telemetry --costs` - Show cost savings
- `python -m empathy_os.models.cli telemetry --providers` - Show provider usage

---

## Overview

This plan implements the execution layer and workflow enhancements from the Multi-Model Architecture Spec. Key revisions from v1.0:

- Added Phase 2.0 (Foundation Verification)
- Added Phase 2.5 (Integration Tests)
- Clarified routing ownership (EmpathyLLM owns routing)
- Added error handling specifications
- Added backwards compatibility strategy
- Used full file paths throughout

---

## Phase 2.0 – Foundation Verification

**Goal:** Confirm existing components work before building on them.

### 2.0.1 Run Existing Tests

- **File:** `tests/test_model_registry.py`
- **TODOs:**
  - [ ] Run `pytest tests/test_model_registry.py -v`
  - [ ] Verify MODEL_REGISTRY has all providers (anthropic, openai, ollama, hybrid)
  - [ ] Verify all tiers exist (cheap, capable, premium)

### 2.0.2 Verify ModelRouter

- **File:** `tests/test_model_router.py`
- **TODOs:**
  - [ ] Run `pytest tests/test_model_router.py -v`
  - [ ] Verify `ModelRouter.route()` returns valid model IDs for all task types

### 2.0.3 Verify TASK_TIER_MAP

- **File:** `src/empathy_os/models/tasks.py`
- **TODOs:**
  - [ ] Confirm all task types in TASK_TIER_MAP
  - [ ] Verify `get_tier_for_task()` returns correct tiers

---

## Phase 2.1 – Formalize LLMExecutor Interface

**Goal:** Single canonical async interface for all LLM calls.

### 2.1.1 Define Protocol

- **File:** `src/empathy_os/models/executor.py`
- **TODOs:**
  - [ ] Define `ExecutionContext` dataclass with fields:
    - `user_id: str | None`
    - `workflow_name: str | None`
    - `step_name: str | None`
    - `task_type: str | None`
    - `provider_hint: str | None`
    - `tier_hint: str | None`
    - `timeout_seconds: int | None`
    - `metadata: dict[str, Any]`
  - [ ] Define `LLMResponse` dataclass with fields:
    - `content: str`
    - `model_id: str`
    - `provider: str`
    - `tier: str`
    - `tokens_input: int | None`
    - `tokens_output: int | None`
    - `cost_estimate: float | None`
    - `latency_ms: int | None`
    - `metadata: dict[str, Any]`
  - [ ] Define `LLMExecutor` Protocol:
    ```python
    class LLMExecutor(Protocol):
        async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse: ...
    ```

### 2.1.2 Tests

- **File:** `tests/test_llm_executor_interface.py`
- **TODOs:**
  - [ ] Test that a mock executor can be created
  - [ ] Test ExecutionContext and LLMResponse serialization

---

## Phase 2.2 – Implement EmpathyLLMExecutor

**Goal:** Wrap EmpathyLLM with telemetry into a single executor.

### 2.2.1 Implement Executor

- **File:** `src/empathy_os/models/empathy_executor.py`
- **TODOs:**
  - [ ] Implement `EmpathyLLMExecutor(LLMExecutor)`:
    ```python
    class EmpathyLLMExecutor:
        def __init__(
            self,
            llm: EmpathyLLM,
            telemetry_store: TelemetryStore | None = None,
        ): ...

        async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse: ...
    ```
  - [ ] In `run()`:
    - Derive `task_type` from `context.task_type` or default to `"generate_code"`
    - Pass `task_type` to `EmpathyLLM.interact()` (EmpathyLLM owns routing)
    - Capture model info from response
    - Create `LLMCallRecord` and send to `TelemetryStore.record_call()` if configured
    - Return `LLMResponse`

### 2.2.2 Error Handling

- **Decisions:**
  - TelemetryStore failures → log warning, don't fail the call
  - EmpathyLLM errors → propagate to caller (ResilientExecutor handles retry)

### 2.2.3 Tests

- **File:** `tests/test_empathy_llm_executor.py`
- **TODOs:**
  - [ ] Use stub EmpathyLLM returning deterministic responses
  - [ ] Assert telemetry receives LLMCallRecord
  - [ ] Assert LLMResponse is populated correctly
  - [ ] Assert telemetry failure doesn't break the call

---

## Phase 2.3 – Implement ResilientExecutor

**Goal:** Add retry, fallback, and circuit breaking.

### 2.3.1 Implement Policies

- **File:** `src/empathy_os/models/fallback.py`
- **TODOs:**
  - [ ] Define/confirm `RetryPolicy`:
    ```python
    @dataclass
    class RetryPolicy:
        max_retries: int = 3
        initial_delay_ms: int = 1000
        max_delay_ms: int = 30000
        exponential_base: float = 2.0
        retryable_errors: set[type] = field(default_factory=lambda: {
            RateLimitError, TimeoutError, ServiceUnavailableError
        })
    ```
  - [ ] Define/confirm `FallbackPolicy`:
    ```python
    @dataclass
    class FallbackStep:
        provider: str
        tier: str

    @dataclass
    class FallbackPolicy:
        steps: list[FallbackStep]
    ```
  - [ ] Implement `CircuitBreaker` (per provider:tier):
    ```python
    class CircuitBreaker:
        def get_key(self, provider: str, tier: str) -> str:
            return f"{provider}:{tier}"

        def is_open(self, provider: str, tier: str) -> bool: ...
        def record_success(self, provider: str, tier: str): ...
        def record_failure(self, provider: str, tier: str): ...
    ```

### 2.3.2 Implement ResilientExecutor

- **File:** `src/empathy_os/models/fallback.py`
- **TODOs:**
  - [ ] Implement `ResilientExecutor`:
    ```python
    class ResilientExecutor:
        def __init__(
            self,
            executor: LLMExecutor,
            retry_policy: RetryPolicy | None = None,
            fallback_policy: FallbackPolicy | None = None,
            circuit_breaker: CircuitBreaker | None = None,
        ): ...

        async def run(self, prompt: str, context: ExecutionContext) -> LLMResponse: ...
    ```
  - [ ] Support per-call policies via `context.metadata`:
    ```python
    retry_policy = context.metadata.get("retry_policy") or self.retry_policy
    fallback_policy = context.metadata.get("fallback_policy") or self.fallback_policy
    ```

### 2.3.3 Error Handling

- **Decisions:**
  - All fallbacks exhausted → raise `AllProvidersFailedError` with attempt history
  - Circuit breaker open → skip provider, try next in chain
  - Record all attempts in `LLMResponse.metadata["attempts"]`

### 2.3.4 Tests

- **File:** `tests/test_resilient_executor.py`
- **TODOs:**
  - [ ] Test retry with exponential backoff
  - [ ] Test fallback chain execution
  - [ ] Test circuit breaker opens after failures
  - [ ] Test AllProvidersFailedError when all fail

---

## Phase 2.4 – Wire Executors Into BaseWorkflow

**Goal:** BaseWorkflow uses LLMExecutor instead of direct EmpathyLLM calls.

### 2.4.1 Update BaseWorkflow

- **File:** `src/empathy_os/workflows/base.py`
- **TODOs:**
  - [ ] Add `executor: LLMExecutor | None` to `__init__`
  - [ ] Implement `_create_default_executor()`:
    ```python
    def _create_default_executor(self) -> LLMExecutor:
        llm = EmpathyLLM(
            provider=self._get_default_provider(),
            enable_model_routing=True,
        )
        base_executor = EmpathyLLMExecutor(llm, self.telemetry)
        return ResilientExecutor(base_executor)
    ```
  - [ ] Store executor for use in `run()`

### 2.4.2 Proof of Concept: SecurityAuditWorkflow

- **File:** `src/empathy_os/workflows/security_audit.py`
- **TODOs:**
  - [ ] Update to use `await self.executor.run(prompt, context)`
  - [ ] Create `ExecutionContext` with workflow_name and step_name
  - [ ] Verify telemetry records are created

### 2.4.3 Backwards Compatibility

- **File:** `empathy_llm_toolkit/core.py`
- **TODOs:**
  - [ ] Add deprecation warning to direct `EmpathyLLM.interact()` calls:
    ```python
    import warnings
    warnings.warn(
        "Direct interact() calls are deprecated in v4.0. "
        "Use LLMExecutor.run() for new code.",
        DeprecationWarning,
        stacklevel=2
    )
    ```

### 2.4.4 Tests

- **File:** `tests/workflows/test_security_audit_executor.py`
- **TODOs:**
  - [ ] Test workflow with mocked executor
  - [ ] Verify ExecutionContext fields are set

---

## Phase 2.5 – Integration Tests

**Goal:** Verify full chain works end-to-end.

### 2.5.1 Executor Chain Test

- **File:** `tests/integration/test_executor_chain.py`
- **TODOs:**
  - [ ] Test: User Request → ExecutionContext → ResilientExecutor → EmpathyLLMExecutor → Mock LLM → LLMResponse → TelemetryStore
  - [ ] Mock only the final LLM API call
  - [ ] Assert telemetry records at both call and workflow level

### 2.5.2 Workflow Integration Test

- **File:** `tests/integration/test_workflow_executor.py`
- **TODOs:**
  - [ ] Run SecurityAuditWorkflow with real executor chain (mocked LLM)
  - [ ] Verify WorkflowRunRecord is created
  - [ ] Verify step-level telemetry

---

## Phase 3 – Workflow Enhancement (Future)

### 3.1 Migrate Workflows to WorkflowStepConfig

**Wave 1 (after Phase 2 complete):**
- `bug_predict.py`
- `security_audit.py`
- `perf_audit.py`

**Wave 2:**
- `test_gen.py`
- `doc_gen.py`
- `refactor_plan.py`
- `dependency_check.py`

### 3.2 Per-Step Fallback Configuration

Use `context.metadata` for step-specific policies (already supported in Phase 2.3).

### 3.3 CLI Commands for Telemetry

- `empathy models registry`
- `empathy models tasks`
- `empathy telemetry workflows`
- `empathy telemetry costs`

---

## Implementation Order

```
1. Phase 2.0: Foundation Verification
   └── Run existing tests, confirm MODEL_REGISTRY and ModelRouter work

2. Phase 2.1: LLMExecutor Interface
   └── Define ExecutionContext, LLMResponse, LLMExecutor protocol

3. Phase 2.2: EmpathyLLMExecutor
   └── Implement wrapper with telemetry

4. Phase 2.3: ResilientExecutor
   └── Add retry, fallback, circuit breaker

5. Phase 2.4: BaseWorkflow Integration
   └── Wire executor into workflows, proof of concept with security_audit

6. Phase 2.5: Integration Tests
   └── End-to-end chain verification
```

---

*This plan is ready for implementation. Each phase has clear deliverables and tests.*
