# Coach Alpha Testing - TODO List

**Last Updated**: October 15, 2025
**Launch Date**: November 1, 2025 (17 days)

---

## 🔥 Critical - Do Immediately

### 1. GitHub Repository Setup ⏱️ 5 minutes
```bash
cd /Users/patrickroebuck/projects/empathy-framework/examples/coach/setup
./create_github_repo.sh
```
**Result**: Private repo at https://github.com/deepstudyai/coach-alpha

---

### 2. Discord Server Setup ⏱️ 90 minutes
Follow: `setup/DISCORD_SETUP_INSTRUCTIONS.md`

**Steps**:
- [ ] Create server
- [ ] Create 7 roles
- [ ] Create 20+ channels
- [ ] Post pinned messages
- [ ] Add bots (optional)
- [ ] Create invite link (50 uses)
- [ ] Test with alt account

---

### 3. Build First Release ⏱️ 30 minutes

**VS Code**:
```bash
cd vscode-extension
npm install
npm run package
```

**JetBrains**:
```bash
cd jetbrains-plugin
./gradlew buildPlugin
```

**Publish**:
```bash
gh release create v1.0.0-alpha.1 \
  --prerelease \
  vscode-extension/coach-alpha-1.0.0.vsix \
  jetbrains-plugin/build/distributions/coach-1.0.0.zip
```

---

### 4. Complete Documentation ⏱️ 2-3 hours

Fill in these files in the alpha GitHub repo:
- [ ] `docs/INSTALLATION.md` - How to install
- [ ] `docs/USER_MANUAL.md` - How to use 16 wizards
- [ ] `docs/WIZARDS.md` - Wizard reference
- [ ] `docs/CUSTOM_WIZARDS.md` - LangChain tutorial
- [ ] `docs/TROUBLESHOOTING.md` - Common issues

---

### 5. Invite Alpha Testers ⏱️ 2 hours

**GitHub**:
```bash
# Create alpha_testers.txt with 50 usernames
cat alpha_testers.txt | while read username; do
  gh repo collaborators add "$username" -R deepstudyai/coach-alpha --permission push
done
```

**Discord**: Send invite link via email

**Email**: Send invitation email (template in `setup/GITHUB_SETUP_GUIDE.md`)

---

## ⚡ High Priority - Do This Week

### 6. VS Code Extension - Implement Providers ⏱️ 3-4 days

**Files to Create**:
- [ ] `vscode-extension/src/providers/code-actions.ts` - Quick fixes
- [ ] `vscode-extension/src/providers/hover.ts` - Level 4 predictions
- [ ] `vscode-extension/src/providers/diagnostics.ts` - Red squiggly lines
- [ ] `vscode-extension/src/utils/config.ts` - Settings

**Test**: Install locally and verify features work

---

### 7. JetBrains Plugin - Implement Core ⏱️ 3-4 days

**Files to Create**:
- [ ] `jetbrains-plugin/.../lsp/CoachLSPClient.kt` - LSP client
- [ ] `jetbrains-plugin/.../inspections/SecurityInspection.kt` - Security check
- [ ] `jetbrains-plugin/.../inspections/PerformanceInspection.kt` - Performance check
- [ ] `jetbrains-plugin/.../ui/CoachToolWindowFactory.kt` - Sidebar panel
- [ ] `jetbrains-plugin/.../actions/AnalyzeFileAction.kt` - File analysis

**Test**: Install locally and verify features work

---

### 8. Run Tests and Fix Bugs ⏱️ 1-2 days

```bash
cd lsp
pip install pytest pytest-asyncio pytest-cov
pytest tests/ -v --cov=.
```

**Fix**:
- [ ] All failing tests
- [ ] Any bugs discovered
- [ ] Achieve >80% coverage

---

## 📅 Medium Priority - Do Next Week

### 9. Create Video Tutorials ⏱️ 4-6 hours

- [ ] Quick Start (5 min)
- [ ] VS Code Deep Dive (15 min)
- [ ] JetBrains Deep Dive (15 min)
- [ ] Custom Wizard Dev (30 min)

**Upload**: YouTube (unlisted), link in Discord

---

### 10. Prepare Launch Day ⏱️ 2 hours

- [ ] Draft launch message for Discord
- [ ] Create Week 1 testing priorities
- [ ] Prepare FAQ for common questions
- [ ] Set up monitoring (who watches what)
- [ ] Plan office hours schedule (Tuesdays 3pm PT)

---

## 🎯 Optional - Nice to Have

### 11. Example Custom Wizards ⏱️ 1-2 days
- [ ] GitWizard
- [ ] CodeReviewWizard
- [ ] MigrationWizard

---

### 12. Analytics Dashboard ⏱️ 1 day
- [ ] Set up Google Analytics or Mixpanel
- [ ] Track installations, wizard usage
- [ ] Create dashboard in Discord #analytics

---

### 13. Social Media Assets ⏱️ 1 day
- [ ] Server icon/logo
- [ ] Banner image
- [ ] Feature screenshots
- [ ] Demo GIFs

---

### 14. Welcome Kit ⏱️ 2 hours
- [ ] Welcome video (2 min)
- [ ] Getting started checklist
- [ ] Keyboard shortcuts cheat sheet
- [ ] FAQ document

---

## ✅ Completed

- [x] IDE Integration Plan (12,000 words)
- [x] Alpha Recruitment Materials (11,000 words)
- [x] Discord Setup Guide (8,000 words)
- [x] GitHub Setup Script (automated)
- [x] LSP Server Foundation (complete)
- [x] LSP Error Handling
- [x] LSP Logging Infrastructure
- [x] LSP Unit Tests (20+ tests)
- [x] LSP E2E Tests (10+ scenarios)
- [x] VS Code Extension Scaffold
- [x] JetBrains Plugin Scaffold

---

## 📊 Progress Tracker

**Overall Progress**: 60% Complete

**Critical Path**:
- [x] Phase 1 LSP Foundation (100%)
- [ ] GitHub Setup (0% - ready to run)
- [ ] Discord Setup (0% - ready to run)
- [ ] First Release (0% - code ready)
- [ ] Documentation (20% - templates exist)
- [ ] VS Code Extension (30% - scaffold done)
- [ ] JetBrains Plugin (20% - structure done)
- [ ] Alpha Invites (0% - waiting for infra)

**Days Until Launch**: 17 (Nov 1, 2025)

---

## 🚀 This Week's Goals (Oct 15-21)

**Monday-Tuesday** (Oct 15-16):
- [ ] Run GitHub setup script
- [ ] Set up Discord server
- [ ] Build first release

**Wednesday-Thursday** (Oct 17-18):
- [ ] Complete documentation
- [ ] Start VS Code providers

**Friday-Weekend** (Oct 19-21):
- [ ] Run tests, fix bugs
- [ ] Continue VS Code/JetBrains dev

---

## 📞 Quick Reference

**Setup Guides**:
- GitHub: `setup/GITHUB_SETUP_GUIDE.md`
- Discord: `setup/DISCORD_SETUP_INSTRUCTIONS.md`
- Complete Plan: `IDE_INTEGRATION_PLAN.md`
- Phase 1 Status: `PHASE_1_COMPLETE_AND_NEXT_STEPS.md`

**Run Tests**:
```bash
cd lsp
pytest tests/ -v
```

**Check Coverage**:
```bash
pytest tests/ --cov=. --cov-report=html
open htmlcov/index.html
```

**View Logs**:
```bash
tail -f ~/.coach/logs/lsp_*.log
```

---

## 🎯 Today's Action Items

1. ✅ Review this TODO list
2. ⏳ Run GitHub setup script (5 min)
3. ⏳ Schedule Discord setup time (90 min)
4. ⏳ Review timeline - is Nov 1 realistic?

---

**Status**: Phase 1 complete, ready for infrastructure setup and alpha launch preparation.

**Next**: Execute GitHub script, then Discord setup, then build release.
