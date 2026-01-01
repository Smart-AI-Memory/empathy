# Manual Testing Script - Empathy Framework v1.4.0

**Date Created:** 2026-01-01
**Tester:** _______________
**VSCode Version:** _______________
**Extension Version:** 1.4.0

---

## Pre-Test Setup

### ✅ Prerequisites
- [ ] VSCode installed with Empathy extension
- [ ] Python environment with `empathy_llm_toolkit` installed
- [ ] API key configured (ANTHROPIC_API_KEY or OPENAI_API_KEY in .env)
- [ ] Sample project open in workspace
- [ ] Extension activated (check status bar)

### 📝 Test Environment
```
Workspace Path: _______________________________
Python Version: _______________________________
API Provider:   [ ] Anthropic  [ ] OpenAI  [ ] None (fallback mode)
```

---

## Section 1: Core Service Functionality

### Test 1.1: Pattern Learning Service
**Purpose:** Verify patterns are learned and recalled

**Steps:**
1. Open Command Palette (`Cmd+Shift+P`)
2. Run `Empathy: Run Workflow`
3. Select `test-gen` workflow
4. When prompted for test type, select `Unit Tests`
5. When prompted for coverage, select `80% Coverage`
6. **✅ VERIFY:** Workflow executes successfully
7. Run `test-gen` again on the **same file**
8. **✅ VERIFY:** See "Use Previous Settings" option
9. Select "Use Previous Settings"
10. **✅ VERIFY:** Skips questions, uses previous answers

**Expected Results:**
- [ ] First run asks 2 questions (test type, coverage)
- [ ] Second run offers "Use Previous Settings"
- [ ] Previous settings restore correctly

**Notes:** _______________________________________________

---

### Test 1.2: LLM Chat Service (With API Key)
**Purpose:** Verify direct LLM integration works

**Steps:**
1. Ensure API key is configured
2. Open Command Palette
3. Run `Empathy: Socratic Workflow Designer` (or `Cmd+Shift+E Q`)
4. Enter goal: "I want to review code for security issues"
5. **✅ VERIFY:** LLM responds with clarifying questions
6. Answer a question
7. **✅ VERIFY:** Multi-turn conversation works
8. Check Output Panel → Empathy
9. **✅ VERIFY:** No Python errors logged

**Expected Results:**
- [ ] LLM responds within 10 seconds
- [ ] Conversation is coherent and contextual
- [ ] Token counts displayed (if available)
- [ ] Model name shown (claude-sonnet-4 or gpt-4o-mini)

**Notes:** _______________________________________________

---

### Test 1.3: LLM Chat Service (Fallback Mode)
**Purpose:** Verify graceful degradation without API key

**Steps:**
1. Rename `.env` to `.env.backup` (disable API key)
2. Restart VSCode or reload extension
3. Run `Empathy: Socratic Workflow Designer`
4. Enter goal: "I want to generate tests"
5. **✅ VERIFY:** Fallback response appears
6. **✅ VERIFY:** Response includes relevant questions (not error message)
7. Check console: **✅ VERIFY:** "[LLMChatService] Using fallback response" logged
8. Restore `.env` file

**Expected Results:**
- [ ] No error dialogs shown
- [ ] Fallback response is contextual and helpful
- [ ] Message indicates "Agent mode" or similar
- [ ] fromFallback: true in response

**Notes:** _______________________________________________

---

### Test 1.4: Cost Estimator Service
**Purpose:** Verify cost estimates display correctly

**Steps:**
1. Open Empathy Dashboard (click status bar or `Cmd+Shift+E D`)
2. Navigate to **Costs** tab
3. **✅ VERIFY:** Cost breakdown by tier visible
4. Select a large file (>500 lines)
5. Run `code-review` workflow
6. **✅ VERIFY:** Cost estimate shown before execution
7. Check format: should be `$X.XX` or `<$0.01`

**Expected Results:**
- [ ] Costs displayed in USD format
- [ ] Premium tier costs > Capable > Cheap
- [ ] Estimates reasonable for file size
- [ ] Savings percentage calculated correctly

**Notes:** _______________________________________________

---

## Section 2: UI Workflow Buttons

### Test 2.1: Code Review Button (HIGH PRIORITY)
**Purpose:** Verify Code Review workflow is accessible from UI

**Steps:**
1. Open Empathy Dashboard
2. Scroll to **Workflows (Beta)** section
3. **✅ VERIFY:** "Review File" button visible with 🔍 icon
4. Click "Review File" button
5. **✅ VERIFY:** File picker appears
6. Select a `.py` or `.ts` file
7. **✅ VERIFY:** Workflow runs
8. **✅ VERIFY:** CodeReviewPanel opens with findings

**Expected Results:**
- [ ] Button appears in workflows grid (top-left position)
- [ ] File picker allows browsing
- [ ] Results display in dedicated panel
- [ ] Findings are clickable (navigate to file:line)

**Notes:** _______________________________________________

---

### Test 2.2: Additional Workflow Buttons
**Purpose:** Verify newly added workflow buttons work

**Test each workflow:**

#### doc-gen (Generate Docs)
- [ ] Button visible with 📄 icon
- [ ] Folder picker works
- [ ] Documentation generated
- **Notes:** _______________________________________________

#### release-prep (Release Prep)
- [ ] Button visible with 🚀 icon
- [ ] Project folder selector works
- [ ] Pre-release checklist runs
- **Notes:** _______________________________________________

#### secure-release (Secure Release)
- [ ] Button visible with 🔐 icon
- [ ] Security pipeline executes
- [ ] Multiple stages visible
- **Notes:** _______________________________________________

---

## Section 3: Error Handling & Resilience

### Test 3.1: Storage Error Recovery
**Purpose:** Verify graceful handling of storage failures

**Steps:**
1. Run workflow multiple times to build pattern history
2. Verify patterns are saved: Check VSCode settings → Workspace State
3. Simulate storage failure (optional: make .vscode read-only)
4. Run workflow again
5. **✅ VERIFY:** Warning message appears: "Failed to save refinement patterns"
6. **✅ VERIFY:** Workflow still executes successfully
7. Restore normal permissions

**Expected Results:**
- [ ] Warning shown to user (not silent failure)
- [ ] Workflow continues despite storage error
- [ ] No crashes or unhandled exceptions

**Notes:** _______________________________________________

---

### Test 3.2: Python Script Errors
**Purpose:** Verify LLM service handles Python errors gracefully

**Steps:**
1. Temporarily rename `vscode-extension/scripts/llm_provider_call.py`
2. Run Socratic Workflow Designer
3. **✅ VERIFY:** Fallback response shown (not crash)
4. **✅ VERIFY:** Error logged to Output Panel
5. Restore script file
6. Run again
7. **✅ VERIFY:** Works normally after restore

**Expected Results:**
- [ ] No VSCode error dialogs
- [ ] Fallback response is contextual
- [ ] Error details in Output Panel → Empathy
- [ ] Recovery works after fix

**Notes:** _______________________________________________

---

## Section 4: Configuration & Settings

### Test 4.1: Service Configuration
**Purpose:** Verify ServiceConfig values are configurable

**Steps:**
1. Open VSCode Settings (`Cmd+,`)
2. Search for "empathy"
3. **✅ VERIFY:** Settings exist:
   - `empathy.pattern.maxPatterns` (default: 100)
   - `empathy.pattern.ttlDays` (default: 90)
   - `empathy.llm.timeoutMs` (default: 60000)
   - `empathy.llm.defaultMaxTokens` (default: 1024)
4. Change `empathy.llm.timeoutMs` to `30000` (30 sec)
5. Run LLM-based workflow
6. **✅ VERIFY:** Timeout applies (check logs for 30s timeout)
7. Restore default settings

**Expected Results:**
- [ ] All empathy.* settings visible
- [ ] Descriptions are clear
- [ ] Changes take effect immediately
- [ ] Defaults match documentation

**Notes:** _______________________________________________

---

### Test 4.2: Pattern TTL Configuration
**Purpose:** Verify pattern pruning respects TTL setting

**Steps:**
1. Set `empathy.pattern.ttlDays` to `0` (prune immediately)
2. Run a workflow with refinement
3. Answer questions and complete workflow
4. Reload VSCode window
5. Run same workflow again
6. **✅ VERIFY:** NO "Use Previous Settings" option (patterns pruned)
7. Reset `empathy.pattern.ttlDays` to `90`

**Expected Results:**
- [ ] TTL=0 causes immediate pruning
- [ ] Patterns don't persist across reload
- [ ] No errors during pruning

**Notes:** _______________________________________________

---

## Section 5: Context Building & Detection

### Test 5.1: Project Type Detection
**Purpose:** Verify ContextBuilder detects project types correctly

**Test in different project types:**

#### Python Project
- [ ] Open project with `pyproject.toml`
- [ ] Run workflow
- [ ] Check logs: project type should be "python"

#### Node.js Project
- [ ] Open project with `package.json`
- [ ] Run workflow
- [ ] Check logs: project type should be "node"

#### Rust Project (if available)
- [ ] Open project with `Cargo.toml`
- [ ] Check logs: project type should be "rust"

**Expected Results:**
- [ ] Correct project type detected
- [ ] Patterns use project type in signature
- [ ] Multi-project workspaces handled

**Notes:** _______________________________________________

---

### Test 5.2: File Type Detection
**Purpose:** Verify file type scanning works

**Steps:**
1. Create test folder with mixed files: `.py`, `.ts`, `.js`, `.md`
2. Run workflow targeting that folder
3. Check Output Panel logs
4. **✅ VERIFY:** File types detected: `.py`, `.ts`, `.js`, `.md`
5. **✅ VERIFY:** `.git` files ignored
6. **✅ VERIFY:** Max 50 files scanned (if folder > 50 files)

**Expected Results:**
- [ ] Common file types detected
- [ ] Git files excluded
- [ ] Performance reasonable for large folders

**Notes:** _______________________________________________

---

## Section 6: Integration Tests

### Test 6.1: End-to-End Code Review Workflow
**Purpose:** Complete workflow from UI to results

**Steps:**
1. Open Dashboard → Workflows
2. Click "Review File" button
3. Select Python file with intentional issues (e.g., SQL injection)
4. Choose focus: "Security"
5. Choose depth: "Deep Analysis"
6. **✅ VERIFY:** LLM analyzes code
7. **✅ VERIFY:** Findings panel opens
8. **✅ VERIFY:** Security issues highlighted
9. Click a finding
10. **✅ VERIFY:** Navigates to file:line

**Expected Results:**
- [ ] Complete flow works end-to-end
- [ ] Findings are accurate
- [ ] UI responsive throughout
- [ ] Results actionable

**Expected Findings:** _______________________________________________

**Notes:** _______________________________________________

---

### Test 6.2: Pattern Recall Workflow
**Purpose:** Verify pattern learning across sessions

**Steps:**
1. Run `test-gen` on `src/utils/helpers.py`
2. Answer: test type = "Integration", coverage = "80%"
3. Note the pattern ID in logs
4. **Close and reopen VSCode**
5. Run `test-gen` on file in `src/utils/` folder
6. **✅ VERIFY:** Pattern suggested (same folder context)
7. Select "Use Previous Settings"
8. **✅ VERIFY:** Same settings applied

**Expected Results:**
- [ ] Patterns persist across sessions
- [ ] Context matching works (same folder)
- [ ] Confidence score displayed
- [ ] Usage count increments

**Notes:** _______________________________________________

---

## Section 7: Performance & Limits

### Test 7.1: Pattern Storage Limits
**Purpose:** Verify MAX_PATTERNS limit enforced

**Steps:**
1. Set `empathy.pattern.maxPatterns` to `5`
2. Run 10 different workflows with unique contexts
3. Check pattern count in logs
4. **✅ VERIFY:** Never exceeds 5 patterns
5. **✅ VERIFY:** Least-used patterns pruned
6. Reset to default (100)

**Expected Results:**
- [ ] Hard limit enforced
- [ ] LRU eviction works
- [ ] No performance degradation
- [ ] Logs show "Pruned N least-used patterns"

**Notes:** _______________________________________________

---

### Test 7.2: Large File Handling
**Purpose:** Verify services handle large files gracefully

**Steps:**
1. Select file > 5000 lines
2. Run `code-review` workflow
3. **✅ VERIFY:** Timeout doesn't occur (<60s)
4. **✅ VERIFY:** Cost estimate reasonable
5. **✅ VERIFY:** Results load without lag

**Expected Results:**
- [ ] Large files don't crash extension
- [ ] Timeout configurable via settings
- [ ] Buffer size adequate (1MB default)

**File Size Tested:** _______________ lines
**Execution Time:** _______________ seconds

**Notes:** _______________________________________________

---

## Section 8: Documentation & Accessibility

### Test 8.1: Feature Discoverability
**Purpose:** Verify features are easy to find

**Steps:**
1. Fresh VSCode window (no prior Empathy usage)
2. Install extension
3. **✅ VERIFY:** Status bar icon appears
4. Click status bar
5. **✅ VERIFY:** Dashboard opens
6. **✅ VERIFY:** Quick Actions visible
7. **✅ VERIFY:** Workflows section visible
8. **✅ VERIFY:** All 14 workflow buttons present

**Expected Results:**
- [ ] Clear entry points (status bar, command palette)
- [ ] All features accessible from UI
- [ ] Keyboard shortcuts documented
- [ ] Help text available

**Notes:** _______________________________________________

---

### Test 8.2: Keyboard Shortcuts
**Purpose:** Verify keyboard shortcuts work

**Test shortcuts from KEYBOARD_SHORTCUTS.md:**

- [ ] `Cmd+Shift+E D` → Open Dashboard
- [ ] `Cmd+Shift+E Q` → Socratic Designer
- [ ] `Cmd+Shift+E R` → Code Review (context menu)
- [ ] `Cmd+Shift+E M` → Morning Briefing
- [ ] `Cmd+Shift+E S` → Pre-Ship Check

**Expected Results:**
- [ ] All shortcuts functional
- [ ] No conflicts with VSCode defaults
- [ ] Cross-platform (Mac/Windows/Linux)

**Notes:** _______________________________________________

---

## Section 9: Regression Tests

### Test 9.1: Existing Features Still Work
**Purpose:** Ensure refactoring didn't break existing functionality

- [ ] Morning workflow runs
- [ ] Ship workflow runs
- [ ] Fix-all workflow runs
- [ ] Status command works (`empathy status`)
- [ ] Memory panel loads (if not beta-gated)

**Notes:** _______________________________________________

---

### Test 9.2: Pre-Commit Hooks
**Purpose:** Verify commit process works

**Steps:**
1. Make a small change to a Python file
2. Stage and commit
3. **✅ VERIFY:** Black formats files
4. **✅ VERIFY:** Ruff checks pass
5. **✅ VERIFY:** Bandit security scan passes
6. **✅ VERIFY:** Secret detection passes
7. **✅ VERIFY:** Commit succeeds

**Expected Results:**
- [ ] All hooks pass
- [ ] Auto-formatting applied
- [ ] No false positives

**Notes:** _______________________________________________

---

## Test Summary

### ✅ Results Overview

**Total Tests:** 28
**Passed:** _______
**Failed:** _______
**Blocked:** _______
**Skipped:** _______

### 🐛 Issues Found

| Test ID | Description | Severity | Status |
|---------|-------------|----------|--------|
| | | [ ] Critical [ ] High [ ] Medium [ ] Low | [ ] Open [ ] Fixed |
| | | [ ] Critical [ ] High [ ] Medium [ ] Low | [ ] Open [ ] Fixed |
| | | [ ] Critical [ ] High [ ] Medium [ ] Low | [ ] Open [ ] Fixed |

### 📝 Additional Notes

```
________________________________________________________________________
________________________________________________________________________
________________________________________________________________________
```

### ✍️ Sign-Off

**Tester Signature:** _______________
**Date:** _______________
**Recommendation:** [ ] Approve for Release  [ ] Needs Fixes  [ ] Reject

---

**End of Manual Testing Script**

*For automated tests, see:*
- `tests/test_finding_extraction.py` (11 tests)
- `npm test` in vscode-extension/ (TypeScript unit tests)
- `pytest tests/` (Python test suite)
