# Testing Guide: New Workflow Buttons

**Date:** 2026-01-01
**Changes:** Added 4 new workflow buttons to Dashboard

---

## ✅ Extension Compiled and Ready

The VSCode extension has been compiled with the latest changes. You can now test the new features!

---

## 🎯 What to Test

### 1. New Dashboard Buttons (4 Total)

**Location:** VSCode Sidebar → Empathy Explorer → Dashboard → Workflows section

**New Buttons Added:**
1. **🔍 Review File** (`code-review`) - File-level code review
2. **📄 Generate Docs** (`doc-gen`) - Documentation generation
3. **🚀 Release Prep** (`release-prep`) - Pre-release preparation
4. **🔐 Secure Release** (`secure-release`) - Security release pipeline

### 2. Complete Button List (14 Workflows)

The Dashboard now shows these workflow buttons in a 2-column grid:

```
┌──────────────────────────────────────────────┐
│ Workflows (Beta)                              │
├──────────────────────────────────────────────┤
│ [🔍 Review File]    [⭐ Run Analysis]        │ ← NEW!
│ [📚 Manage Docs]    [🐛 Predict Bugs]        │
│ [🔒 Security]       [⚡ Performance]          │
│ [🧪 Generate Tests] [🏗️ Refactor]           │
│ [📦 Dependencies]   [🩺 Health Check]        │
│ [🔍 Review PR]      [📄 Gen Docs]            │ ← NEW!
│ [🚀 Release Prep]   [🔐 Sec Release]         │ ← NEW!
└──────────────────────────────────────────────┘
```

---

## 🧪 Test Scenarios

### Scenario 1: Code Review Button (CRITICAL)

**Purpose:** Verify the code review feature is now discoverable from UI

**Steps:**
1. Open VSCode with a Python/TypeScript project
2. Open Empathy Explorer sidebar
3. Click on "Dashboard" tab
4. Scroll to "Workflows (Beta)" section
5. Click **🔍 Review File** button

**Expected Behavior:**
- File picker opens
- Select a file (e.g., `src/auth.py`)
- Workflow executes
- CodeReviewPanel opens in sidebar
- Findings appear with clickable file:line references

**Success Criteria:**
- ✅ Button appears first in workflows section
- ✅ File picker shows on click
- ✅ Review runs successfully
- ✅ Results appear in CodeReviewPanel
- ✅ Clicking finding navigates to file:line

---

### Scenario 2: Generate Docs Button

**Steps:**
1. Click **📄 Generate Docs** button
2. Folder picker should open
3. Select a folder (e.g., `./src`)
4. Workflow executes

**Expected Behavior:**
- Folder picker opens (not file picker)
- Can select project root or specific folder
- Documentation generation workflow runs
- Report opens in new editor tab OR terminal

**Success Criteria:**
- ✅ Folder picker appears
- ✅ Workflow executes without errors
- ✅ Output is readable

---

### Scenario 3: Release Prep Button

**Steps:**
1. Click **🚀 Release Prep** button
2. Folder picker opens
3. Select project root (`.`)
4. Workflow executes

**Expected Behavior:**
- Folder picker opens
- "Use Entire Project" button available
- Release preparation checklist runs
- Report shows pre-release validation results

**Success Criteria:**
- ✅ Folder picker with project root option
- ✅ Workflow runs on entire project
- ✅ Checklist items displayed

---

### Scenario 4: Secure Release Button

**Steps:**
1. Click **🔐 Secure Release** button
2. Select project root
3. Multi-stage security pipeline runs

**Expected Behavior:**
- Folder picker opens
- Security pipeline executes (may take 1-2 min)
- Each stage shows progress
- Final report shows security validation

**Success Criteria:**
- ✅ Pipeline runs all security checks
- ✅ Results clearly formatted
- ✅ Blocking issues highlighted

---

### Scenario 5: Existing Buttons Still Work

**Test these to ensure no regressions:**

1. **⭐ Run Analysis** (`pro-review`)
2. **📚 Manage Docs** (`doc-orchestrator`)
3. **🐛 Predict Bugs** (`bug-predict`)
4. **🔒 Security Audit** (`security-audit`)
5. **⚡ Perf Audit** (`perf-audit`)
6. **🧪 Generate Tests** (`test-gen`)
7. **🏗️ Refactor Plan** (`refactor-plan`)
8. **📦 Check Deps** (`dependency-check`)
9. **🩺 Health Check** (`health-check`)
10. **🔍 Review PR** (`pr-review`)

**Quick Regression Test:**
- Click 2-3 existing buttons randomly
- Verify they still open pickers and run workflows
- No JavaScript errors in DevTools console

---

## 🐛 Debugging Tips

### If Buttons Don't Appear

1. **Reload VSCode Window:**
   - Command Palette: "Developer: Reload Window"
   - Or restart VSCode entirely

2. **Check Extension is Activated:**
   - Look for "Empathy Explorer" in sidebar
   - Check Output panel for extension logs

3. **Verify Compilation:**
   ```bash
   cd vscode-extension
   npm run compile
   ```

### If Workflow Fails to Run

1. **Check Python Environment:**
   ```bash
   python -m empathy_os.cli workflow list
   ```
   Should show all available workflows including new ones

2. **Check Workflow Registration:**
   ```bash
   python -m empathy_os.cli workflow run doc-gen --help
   python -m empathy_os.cli workflow run release-prep --help
   python -m empathy_os.cli workflow run secure-release --help
   ```

3. **Check VSCode DevTools:**
   - Command Palette: "Developer: Toggle Developer Tools"
   - Look for errors in Console tab

### Common Issues

**Issue:** "Workflow not found"
- **Cause:** Workflow not registered in backend
- **Fix:** Check `src/empathy_os/workflows/__init__.py` includes the workflow

**Issue:** "No input provided"
- **Cause:** Workflow config missing or incorrect
- **Fix:** Check `workflowConfig` in EmpathyDashboardPanel.ts

**Issue:** Button does nothing when clicked
- **Cause:** JavaScript not compiled or cached
- **Fix:** Run `npm run compile` and reload window

---

## 📊 Test Results Template

Use this to track your testing:

```markdown
## Test Results - [Your Name] - [Date]

### Code Review Button
- [ ] Button appears in Dashboard
- [ ] File picker opens
- [ ] Workflow runs successfully
- [ ] Results appear in CodeReviewPanel
- [ ] Findings are clickable
- **Notes:**

### Generate Docs Button
- [ ] Button appears in Dashboard
- [ ] Folder picker opens
- [ ] Workflow runs successfully
- [ ] Output is readable
- **Notes:**

### Release Prep Button
- [ ] Button appears in Dashboard
- [ ] Folder picker opens
- [ ] Workflow runs successfully
- [ ] Checklist displayed
- **Notes:**

### Secure Release Button
- [ ] Button appears in Dashboard
- [ ] Folder picker opens
- [ ] Security pipeline runs
- [ ] Results are clear
- **Notes:**

### Regression Tests
- [ ] Existing buttons still work
- [ ] No console errors
- [ ] No visual layout issues
- **Notes:**

### Overall Assessment
- **Pass/Fail:**
- **Blocker Issues:**
- **Minor Issues:**
- **Suggestions:**
```

---

## 🔍 Manual QA Checklist

### Visual Check
- [ ] All 14 workflow buttons visible
- [ ] Icons render correctly (no broken emoji)
- [ ] 2-column grid layout maintained
- [ ] Buttons have consistent styling
- [ ] Hover states work

### Functional Check
- [ ] All buttons clickable
- [ ] Pickers open correctly (file vs folder)
- [ ] "Use Entire Project" button appears for folder workflows
- [ ] Workflows execute without crashing
- [ ] Results display properly

### Integration Check
- [ ] CodeReviewPanel opens for code-review
- [ ] Reports open in editor for other workflows
- [ ] Notifications appear on completion
- [ ] Workflow history records runs
- [ ] Cost tracking updates

---

## 🚀 Ready to Test!

**Quick Start:**
1. Reload VSCode window
2. Open Empathy Explorer sidebar
3. Click Dashboard
4. Try clicking **🔍 Review File** button
5. Select a file and verify results appear

**Report Issues:**
If you find any bugs or unexpected behavior, note:
- Which button was clicked
- Error message (if any)
- Console errors (DevTools)
- Expected vs actual behavior

---

**Good luck testing!** 🎉
