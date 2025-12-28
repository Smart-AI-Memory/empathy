# Reliability Review and Recommendations for empathy-framework

**Date:** 2025-12-28

## Checklist

- [x] Review core reliability surfaces (workflows, executor, telemetry, VS Code extension).
- [x] Identify specific risk areas and existing mitigations.
- [x] Propose targeted improvements that increase reliability (not features), with concrete examples and where to apply them.

---

## 1. Workflow Engine Reliability (`src/empathy_os/workflows`)

### 1.1 What’s already strong

- `BaseWorkflow`:
  - Centralized init with `WorkflowConfig.load()`, provider resolution, telemetry backend selection.
  - Progress tracking (`_progress_tracker`, `progress_callback`).
  - Cost tracking and `CostReport` generation.
  - Thorough tests in `tests/test_workflow_base.py`:
    - Happy path (`test_execute_all_stages`).
    - Error handling (`test_execute_with_error`).
    - Skipped stages (`test_execute_with_skipped_stage`).
    - Cost report generation and pricing tests.

This is a solid base; the main risks now are around **configuration**, **timeouts**, and **error classification**.

### 1.2 Reliability risks

1. **Config load failures or malformed configs**
   - `BaseWorkflow` calls `WorkflowConfig.load()` implicitly.
   - If `.empathy/workflows.yaml` or similar is malformed or partially missing, workflows may fail at startup in ways that are hard for users to diagnose.

2. **Implicit timeouts and long‑running calls**
   - The architecture spec and `AgentFactory.create_workflow` support `timeout_seconds`, but:
     - It’s not obvious that all workflows and agent workflows respect timeouts consistently.
     - A hung provider call or large input could stall a whole workflow.

3. **Error surfaces are broad but not always user‑friendly**
   - `test_execute_with_error` verifies `result.success is False` and `result.error` contains the message.
   - However:
     - Errors from model calls, config, file IO, and logic are all flattened into `result.error` with a string.
     - This makes it harder to react programmatically (e.g., auto-retry on transient provider error vs. fail fast on config error).

4. **Agent-based workflows and pipelines**
   - `empathy_llm_toolkit/agent_factory/factory.py` has:
     - `timeout_seconds`, `checkpointing`, `retry_on_error`, `max_retries` parameters.
   - But reliability depends on:
     - How strictly those are enforced.
     - Whether agents can crash the workflow with unhandled exceptions.

### 1.3 Recommended improvements

1. **Harden `WorkflowConfig.load()` and configuration handling**

   - Add explicit, typed failure modes and default fallbacks:
     - If config file is missing: log a clear warning, fall back to a documented default config.
     - If malformed YAML/JSON: surface a specific `ConfigError` with filename and pointer.
   - Recommendation:
     - Introduce a small “config health check”:
       - At framework startup or CLI command `empathy workflows doctor`, run:
         - Load `WorkflowConfig` for each workflow.
         - Validate that providers in config exist in `MODEL_REGISTRY`.
         - Validate `workflow_xml_configs` entries map to known templates.

   **User impact:** Fewer “mysterious” failures when config files are edited; easier for users to self‑diagnose config problems.

2. **Normalize timeouts and add explicit timeout errors**

   - Ensure every path that can call an LLM or agent workflow:
     - Always passes a `timeout_seconds` from config or from a sane default (e.g., 60–120s per step).
   - Recommendation:
     - At the `LLMExecutor`/`ResilientExecutor` layer:
       - Introduce a `TimeoutError` that is:
         - Raised when a provider call exceeds `timeout_seconds`.
         - Recorded in telemetry (with a distinct `error_type`).
     - In `BaseWorkflow.execute`:
       - When catching a timeout error, set `result.error_type = "timeout"` and `result.transient = True` (vs. `transient = False` for logic/config errors).

   **User impact:** Stuck workflows become predictable “time limit exceeded” failures, not silent hangs.

3. **Structured error taxonomy in `WorkflowResult`**

   - You already have `result.error` and `result.success`.
   - Add, for example:
     - `error_type: Literal["config","runtime","provider","timeout","validation"] | None`
     - `transient: bool` (hinting whether an automatic retry is reasonable).
   - Recommendation:
     - In `BaseWorkflow.execute`:
       - Wrap execution with a narrow exception mapping:
         - Config load issues → `error_type="config"`, `transient=False`.
         - Provider/LLM exceptions and `ResilientExecutor` failures → `error_type="provider"`, `transient=True/False` based on error.
         - Input validation → `error_type="validation"`, `transient=False`.
   - This enables:
     - CLI and dashboard to present meaningful, actionable error states.
     - Future auto‑retry or “Run again with cheaper tier” features.

---

## 2. Executor & Multi‑Model Layer Reliability

You have a strong design in `docs/design/MULTI_MODEL_ARCHITECTURE_SPEC.md` and the Phase 2–3 plan (`docs/design/PHASE_2_3_IMPLEMENTATION_PLAN.md`), including:

- `LLMExecutor` interface and `EmpathyLLMExecutor`.
- `ResilientExecutor` with retry, fallback, circuit breaker.
- `ModelRouter` and `MODEL_REGISTRY`.

### 2.1 Risks

1. **Model registry / router drift**
   - There are tests like `TestProviderModelsSync` and model pricing tests.
   - But model IDs and pricing are brittle over time: providers deprecate models, change prices.

2. **Resilience configuration sprawl**
   - Retry, fallback, and circuit breaker parameters may not be tuned per provider/task.
   - One misconfigured global policy could cause:
     - Aggressive retries on non‑retryable errors.
     - Slow failover when a provider is clearly down.

3. **Cost estimation vs actual billing mismatch**
   - `TelemetryAnalytics.cost_savings_report` compares `total_cost` vs `baseline_cost`.
   - If `MODEL_REGISTRY` pricing drifts from real provider pricing, cost reports become misleading.

### 2.2 Recommended improvements

1. **Scheduled registry validation and warnings**

   - Add a CLI command `empathy models validate` that:
     - Verifies all `MODEL_REGISTRY` entries:
       - Have strictly positive and reasonable cost values.
       - Use existing provider/tier keys.
     - Optionally (and only if keys are configured) pings provider APIs to:
       - Confirm model IDs are valid.
       - Warn if a model is deprecated (where supported).
   - Surface warnings in:
     - CLI output.
     - A new “Models Health” widget in the Empathy Dashboard.

2. **Per-task resilience profiles**

   - Instead of a single `DEFAULT_FALLBACK_POLICY`, define per‑task fallback policies:
     - `SECURITY_AUDIT` → more conservative: cross‑provider fallback, lower `max_retries` to avoid repeated unsafe decisions.
     - `SUMMARIZE` → tolerant: more retries, cheaper fallbacks.
   - Wire this via:
     - `TaskType` → `FallbackPolicy` mapping in `empathy_os.models.tasks` or a new config.
   - Ensure `ResilientExecutor`:
     - Logs each fallback attempt in telemetry with provider/tier, error, and final outcome.

3. **Cost telemetry sanity checks**

   - In `TelemetryAnalytics.cost_savings_report`:
     - Add simple assertions/sanitization:
       - If any `wf.total_cost` or `wf.baseline_cost` is negative or absurdly high, tag that workflow as “anomalous”.
     - Optionally:
       - Return a `warnings` array in the report (e.g., “5 workflows have baseline_cost=0; savings_percent may be inaccurate”).

---

## 3. Telemetry & Durability (`src/empathy_os/models/telemetry.py`)

Telemetry is crucial to reliability: without good observability, it’s hard to know what’s breaking.

### 3.1 What’s strong

- `TelemetryStore` persists `LLMCallRecord` and `WorkflowRunRecord` (JSONL).
- `TelemetryAnalytics` already supports:
  - Cost/savings summaries.
  - Provider usage.
  - Fallback statistics.

### 3.2 Risks

1. **Single JSONL file as a bottleneck**
   - Telemetry is written to `.empathy/telemetry.jsonl` or similar.
   - Under heavy usage, writes might:
     - Fail due to IO errors (disk full, permissions).
     - Create a large file that’s slow to read, leading to dashboard lag.

2. **Lack of backpressure or failure handling**
   - If telemetry writes fail:
     - Workflows should still complete, but:
       - You might miss important diagnostic data.
       - The user currently may not see any indication that telemetry is degraded.

3. **Retention and cleanup not enforced**
   - The design spec contains a rich `TelemetryRetentionPolicy`, but:
     - Implementation for hot/warm/cold storage and cleanup may not be complete.
     - Telemetry can grow unbounded over time.

### 3.3 Recommended improvements

1. **Best-effort, non‑blocking telemetry writes**

   - Ensure `TelemetryStore.record_call` / `record_workflow_run`:
     - Catch and log IO errors, but never raise them up to workflows.
     - Consider:
       - A small in‑memory queue to buffer writes.
       - Flushing in batches (for performance) while keeping code simple.

2. **Implement `TelemetryRetentionPolicy`**

   - Implement the retention design from the spec:
     - Periodic task (CLI or background) to:
       - Move old records from hot → warm → cold → archive.
       - Compress files after `compress_after_days`.
   - Provide a CLI:
     - `empathy telemetry cleanup --dry-run`
     - `empathy telemetry cleanup --apply`.
   - Optionally:
     - Surface basic telemetry health in the dashboard (e.g., “Telemetry storage healthy / nearing quota / in error”).

3. **Add minimal schema versioning**

   - Add a `schema_version` field to `LLMCallRecord` and `WorkflowRunRecord`.
   - When reading:
     - If version mismatch, handle gracefully (e.g., fill missing fields with defaults).
   - This gives you flexibility to evolve telemetry structures without breaking analytics or dashboards.

---

## 4. VS Code Extension Reliability

The extension panels are your main UX hub; reliability here means **no broken buttons, clear error messages, and graceful degradation** when the backend fails.

### 4.0 Refactor Advisor Panel (`RefactorAdvisorPanel.ts`)

#### 4.0.1 What's strong

- Proper disposable tracking with `_disposables` array and `dispose()` method
- Base64 encoding for Python subprocess data (avoids JSON escaping issues)
- Session management with checkpoints for rollback capability
- DEBUG flag to gate console.log statements

#### 4.0.2 Risks

1. **Python subprocess calls can hang without cancellation**
   - Analysis timeout is 120s, generation timeout is 60s
   - No way for user to cancel an in-flight analysis
   - If Python crashes or hangs, UI shows spinner indefinitely

2. **Session state not persisted across panel reloads**
   - If user closes/reopens the panel, all findings and checkpoints are lost
   - No recovery mechanism for interrupted sessions

3. **No validation of Python/API availability before analysis**
   - User clicks "Analyze" and waits 120s only to learn Python isn't installed
   - No pre-flight check for API key availability

#### 4.0.3 Recommended improvements

1. **Add cancellation mechanism**
   - Store the `ChildProcess` reference from `cp.execFile`
   - Add "Cancel" button that appears during analysis
   - On cancel: `childProcess.kill()` and reset UI state

2. **Pre-flight validation**
   - Before starting analysis, verify:
     - Python is executable (`python --version`)
     - API key is set (quick env check)
   - Show specific error: "Python not found" or "API key missing"

3. **Session persistence (optional)**
   - Use `context.workspaceState` or `context.globalState` to persist:
     - Current file path
     - Findings (without generated code)
     - User decisions
   - Restore on panel reopen

---

### 4.1 Dashboard Panel (`EmpathyDashboardPanel.ts`)

#### 4.1.1 Observations

- The panel:
  - Spawns Python processes (`cp.spawn`, `cp.exec`) to run CLI commands.
  - Parses JSON responses (telemetry, workflow runs, costs).
  - Has logic around:
    - Workflow run inputs and validation.
    - XML severity visualizations.
    - Cost estimation (`requestCostEstimate(this.value)` in the workflow path input).

#### 4.1.2 Risks

1. **Child process and JSON parsing failures**

   - If:
     - Python is not installed.
     - The empathy CLI is missing or has a bug.
     - The command times out or prints partial JSON.
   - Then:
     - The dashboard may silently fail to update or show confusing states.

2. **UI state vs backend state drift**

   - Example: user quickly clicks “Run” multiple times:
     - Multiple workflow runs may launch concurrently.
     - UI might show outdated data or double entries if there’s no deduping or throttling.

3. **No clear surface of “backend unhealthy”**

   - When telemetry or workflow CLIs are unavailable:
     - User sees an empty list or stale data, without a clear reason.

#### 4.1.3 Recommended improvements

1. **Harden process execution and JSON parsing**

   - Wrap all `cp.exec`/`cp.spawn` calls with:
     - Timeouts per operation type:

       | Operation | Timeout | Rationale |
       | --------- | ------- | --------- |
       | Telemetry fetch | 5s | Non-critical, fail fast |
       | Workflow list | 10s | User-facing, moderate |
       | Workflow run | 300s | Long-running, needs progress |
       | Cost estimate | 3s | Synchronous UI blocking |
       | Refactor analysis | 120s | LLM-intensive, already set |
       | Refactor generation | 60s | Single finding, already set |

     - Clear fallback behavior:
       - If a call fails, show a banner in the dashboard: “Unable to reach Empathy CLI. See Output › Empathy for details.”
     - Robust JSON parsing:
       - Use `try/catch` around `JSON.parse` in the webview.
       - Log raw output to the “Empathy” output channel if parsing fails.
   - This turns silent failures into visible, debuggable issues.

2. **Add simple run deduping / throttling**

   - In the Webview script:
     - When “Run workflow” is clicked:
       - Disable the button until:
         - The run completes, or
         - A timeout occurs.
       - Optionally show a spinner with text like “Running bug-predict…”.
   - This avoids multiple overlapping runs for the same workflow, reducing load and confusion.

3. **Backend health indicator**

   - Add a small health section or icon:
     - “Backend OK” if:
       - Last telemetry fetch succeeded in the last N minutes.
     - “Backend degraded” if:
       - Last CLI call failed.
   - Implementation:
     - Track last success/failure timestamps in the extension.
     - Update the dashboard via a simple message.

---

## 5. Testing & CI Reliability

You already have a rich test suite for workflows and executors (`tests/test_workflow_base.py`, `tests/test_executor_integration.py`, workflow‑specific tests like `tests/test_bug_predict_workflow.py`).

To make reliability improvements stick:

### 5.1 Recommendations

1. **Add explicit timeout and retry tests**

   - In `tests/test_executor_integration.py`:
     - Simulate a slow or hung provider:
       - Use a fake executor that sleeps beyond `timeout_seconds`.
       - Assert that:
         - A `TimeoutError` is raised by `ResilientExecutor`.
         - The workflow result captures `error_type="timeout"`.

2. **Add config / registry drift tests**

   - Tests to ensure:
     - Every provider/tier in `MODEL_REGISTRY` has a matching entry in `TASK_TIER_MAP` or is otherwise documented.
     - CLI `empathy models registry` returns consistent structures that the dashboard expects.

3. **Add VS Code extension smoke test / QA checklist**

   - Include:
     - Launch dashboard with no `.empathy` directory (fresh project).
     - Simulate missing Python or empathy CLI.
     - Verify that:
       - UI degrades gracefully (clear but non‑intrusive error messages).
       - No uncaught exceptions in the VS Code extension host log.

---

## 6. Graceful Degradation Hierarchy

When components fail, the system should degrade predictably rather than catastrophically.

### 6.1 Degradation Levels

| Level | Condition | System Behavior | User Experience |
| ----- | --------- | --------------- | --------------- |
| **Healthy** | All systems operational | Full functionality | Normal operation |
| **Degraded** | Telemetry unavailable | Workflows continue, no cost tracking | "Telemetry unavailable" badge |
| **Degraded** | Primary provider fails | Fallback to secondary provider | Slightly higher latency, cost impact logged |
| **Degraded** | All LLM providers fail | Cache recent responses where applicable | "Providers unavailable, using cached data" |
| **Degraded** | Config invalid | Use embedded defaults | "Using default config" warning + repair wizard |
| **Offline** | No network | Read-only mode for docs/history | "Offline mode" indicator |

### 6.2 Implementation Guidelines

1. **Never block on non-critical services**
   - Telemetry failures should not prevent workflow execution
   - Cost estimation failures should not block workflow runs

2. **Provide clear status indicators**
   - Each degradation level should have a visible indicator in the UI
   - Include actionable guidance: "Check API key" vs generic "Error"

3. **Log degradation events**
   - Record in telemetry (if available) or local log
   - Include: timestamp, component, degradation level, recovery action

---

## 7. Reliability Metrics

Track these metrics to measure reliability improvements over time.

### 7.1 Key Metrics

| Metric | Formula | Target |
| ------ | ------- | ------ |
| `workflow_success_rate` | successful_runs / total_runs | > 95% |
| `workflow_timeout_rate` | timed_out_runs / total_runs | < 2% |
| `provider_fallback_rate` | fallback_calls / total_llm_calls | < 5% |
| `config_error_rate` | config_failures / total_startups | < 1% |
| `dashboard_cli_failure_rate` | failed_cli_calls / total_cli_calls | < 3% |
| `telemetry_write_failure_rate` | failed_writes / total_writes | < 1% |
| `mean_time_to_recovery` | avg(recovery_time) after failures | < 30s |

### 7.2 Collection Points

- **Workflow metrics**: In `BaseWorkflow.execute()` after each run
- **Provider metrics**: In `ResilientExecutor` on each call/fallback
- **Dashboard metrics**: In extension on each CLI call
- **Telemetry metrics**: In `TelemetryStore` on each write attempt

### 7.3 Alerting Thresholds

```yaml
alerts:
  workflow_timeout_rate:
    warning: 5%
    critical: 10%
  provider_fallback_rate:
    warning: 10%
    critical: 25%
  config_error_rate:
    warning: 5%
    critical: 10%
```

---

## 8. Task Resilience Profiles

Define per-task fallback policies instead of a single global policy.

### 8.1 Task Categories

| Category | Tasks | Retry Policy | Fallback Strategy |
| -------- | ----- | ------------ | ----------------- |
| **Critical** | security_audit, code_review | max_retries=1, fail_fast=true | Cross-provider only, no tier downgrade |
| **Balanced** | bug_predict, refactor_plan, pr_review | max_retries=2, backoff=exponential | Same-tier fallback, then tier downgrade |
| **Tolerant** | summarize, document_gen, research | max_retries=3, backoff=linear | Aggressive fallback, cheap tier acceptable |

### 8.2 Configuration

```python
TASK_RESILIENCE_PROFILES = {
    TaskType.SECURITY_AUDIT: ResilienceProfile(
        max_retries=1,
        retry_on=["rate_limit", "timeout"],
        fallback_strategy="cross_provider",
        allow_tier_downgrade=False,
    ),
    TaskType.SUMMARIZE: ResilienceProfile(
        max_retries=3,
        retry_on=["rate_limit", "timeout", "server_error"],
        fallback_strategy="any_available",
        allow_tier_downgrade=True,
    ),
}
```

---

## Summary

If you want a prioritized short list to act on for reliability:

1. **Timeouts & resilience** (highest user impact)
   - Ensure `ResilientExecutor` is consistently used with per-task timeouts and fallback policies.
   - Add explicit timeout handling and tests.
   - Implement task resilience profiles (Section 8).

2. **Config & error taxonomy**
   - Harden `WorkflowConfig.load()`.
   - Add structured `error_type`/`transient` to `WorkflowResult`.
   - Implement graceful degradation hierarchy (Section 6).

3. **Dashboard & extension hardening**
   - Add timeouts + clear error handling around CLI calls.
   - Throttle workflow runs and add backend health indicators.
   - Add cancellation and pre-flight validation to Refactor Advisor.

4. **Telemetry robustness**
   - Make telemetry writes best-effort and non-blocking.
   - Implement retention and basic anomaly checks.
   - Track reliability metrics (Section 7).

---

*Document enhanced with sections 4.0 (Refactor Advisor), 6 (Graceful Degradation), 7 (Reliability Metrics), and 8 (Task Resilience Profiles).*
