# Pattern Library Summary
Generated: 2025-12-15 03:34

This summary is auto-generated from stored patterns.
Use these patterns to inform debugging, security, and code quality decisions.

## Bug Patterns (19 stored)

### async_timing (3 occurrences)

- **bug_demo_async_timing** (investigating)
  - Root cause:
  - Fix:

- **bug_20251101_ghi789** (resolved)
  - Root cause: Missing await on async function call
  - Fix: Added await keyword to async call
  - Resolution time: 5 min

- **bug_async_001** (resolved)
  - Root cause: Missing await on async function call
  - Fix: Added await keyword to async memory operation
  - Resolution time: 10 min

### import_error (3 occurrences)

- **bug_20251212_9c315fc5** (resolved)
  - Root cause: structlog package not in requirements.txt
  - Fix: Added structlog to dependencies
  - Resolution time: 3 min

- **bug_20251212_f858ff98** (resolved)
  - Root cause: Duplicate of bug_20251212_9c315fc5 - structlog missing
  - Fix: Added structlog to requirements.txt
  - Resolution time: 1 min

- **bug_py_import_001** (resolved)
  - Root cause: Redis not installed in environment
  - Fix: Added redis to requirements.txt and installed
  - Resolution time: 5 min

### null_reference (10 occurrences)

- **bug_20250915_abc123** (resolved)
  - Root cause: API returned null instead of empty array
  - Fix: Added default empty array fallback: data?.items ?? []
  - Resolution time: 15 min

- **bug_20251212_3c5b9951** (resolved)
  - Root cause: API returns undefined instead of empty array
  - Fix: Added optional chaining and default array fallback
  - Resolution time: 15 min

- **bug_demo_null_ref** (investigating)
  - Root cause:
  - Fix:

### type_mismatch (2 occurrences)

- **bug_demo_type_error** (investigating)
  - Root cause:
  - Fix:

- **bug_type_001** (resolved)
  - Root cause: File read in binary mode instead of text
  - Fix: Changed file open mode to 'r' with encoding
  - Resolution time: 12 min

### unknown (1 occurrences)

- **bug_20251212_221b2e5f** (resolved)
  - Root cause: Async function called without await keyword
  - Fix: Added await to async analyze() call
  - Resolution time: 4 min

## Security Decisions (11 stored)

### ACCEPTED (4)

- **insecure_random**: Only used for UI animations, not security
  - Decided by: @mike

- **insecure_random**: Only used for non-security purposes (UI animations)
  - Decided by: @mike

- **xss**: React's JSX auto-escapes, innerHTML not used
  - Decided by: @tech_lead

- **insecure_random**: Used for non-cryptographic purposes (IDs, sampling)
  - Decided by: @tech_lead

### DEFERRED (1)

- **eval**: Low risk in dev tooling, will address in Q2
  - Decided by: @security_team

### FALSE_POSITIVE (6)

- **sql_injection**: Using SQLAlchemy ORM which handles SQL escaping
  - Decided by: @sarah

- **xss**: React's JSX auto-escapes, dangerouslySetInnerHTML not used
  - Decided by: @tech_lead

- **sql_injection**: Using SQLAlchemy ORM which handles escaping
  - Decided by: @sarah

- **hardcoded_secret:test_api_key**: Test fixtures only, not real credentials
  - Decided by: @sarah

- **hardcoded_secret**: Test fixtures and demo files - not real credentials
  - Decided by: @security_team

- **eval**: Only in test code for dynamic assertions
  - Decided by: @security_team

## Tech Debt Trajectory (12 snapshots)

### Current State (2025-12-12)

- Total items: 343
- By type: deprecated: 2, fixme: 1, hack: 17, temporary: 204, todo: 119
- By severity: critical: 2, high: 1, medium: 340
- Hotspots: tests/test_unified_memory.py, 10_9_2025_ai_nurse_florence/src/static/js/clinical-components.js, examples/ai_wizards/tests/test_security_wizard.py

### Trajectory: INCREASING

- Change: 318 items over 12 snapshots
- Oldest snapshot: 25 items (2025-09-13)
- Current: 343 items

---

## How to Use These Patterns

- **Debugging**: When encountering errors, check if similar bugs have been resolved
- **Security**: Before flagging security issues, check team decisions for false positives
- **Tech Debt**: Consider debt trajectory when planning refactoring work
