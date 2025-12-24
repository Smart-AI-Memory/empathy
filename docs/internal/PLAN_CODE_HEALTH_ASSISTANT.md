# Code Health Assistant - Expansion Plan

**Status**: Implemented (v2.2.0)
**Priority**: High
**Foundation**: Session Status Assistant (v2.1.5)
**Released**: v2.2.0

## Vision

Transform the Session Status Assistant into a comprehensive **Code Health Assistant** - a proactive system that helps developers maintain code quality through:

1. **Awareness** - Know what needs attention
2. **Guidance** - Get actionable recommendations
3. **Automation** - Fix common issues automatically
4. **Learning** - System improves from your patterns

---

## Current State (v2.1.5)

The Session Status Assistant provides:
- Priority-weighted status aggregation
- Time-based trigger detection
- Selectable action prompts
- Daily snapshots and wins detection

**What's missing:**
- Deeper integration with linting/formatting tools
- Auto-fix capabilities
- Customizable health checks
- Progressive disclosure (summary → details → fix)
- Integration with Claude Code sessions

---

## Expansion Phases

### Phase 1: Enhanced Health Checks

**Add new data sources:**

| Check | Weight | Source | Auto-fix |
|-------|--------|--------|----------|
| Type errors | 90 | `pyright`/`mypy` | No |
| Lint warnings | 70 | `ruff`/`eslint` | Yes |
| Formatting | 50 | `black`/`prettier` | Yes |
| Test failures | 85 | `pytest` | No |
| Test coverage | 40 | `coverage.py` | No |
| Security vulns | 100 | `bandit`/`semgrep` | Some |
| Outdated deps | 30 | `pip-audit` | Yes |
| Documentation | 20 | `pydocstyle` | No |

**Implementation:**

```python
class HealthCheckRunner:
    """Run configurable health checks and aggregate results."""

    def __init__(self, config: dict):
        self.checks = self._load_enabled_checks(config)

    async def run_all(self) -> HealthReport:
        """Run all enabled checks in parallel."""

    async def run_quick(self) -> HealthReport:
        """Run fast checks only (< 5 seconds)."""

    async def run_deep(self) -> HealthReport:
        """Run comprehensive checks (may take minutes)."""
```

**New CLI commands:**

```bash
# Quick health check (fast checks only)
empathy health

# Deep health check (all checks)
empathy health --deep

# Specific check
empathy health --check lint

# Auto-fix what's fixable
empathy health --fix
```

---

### Phase 2: Progressive Disclosure

**Three-level detail system:**

**Level 1: Summary View (default)**
```
📊 Code Health: Good (87/100)

🟢 Tests: All passing (142 tests)
🟡 Lint: 3 warnings in 2 files
🟢 Types: No errors
🟡 Coverage: 78% (-2% from target)

[1] Fix lint  [2] See details  [3] Full report
```

**Level 2: Details View (--details)**
```
📊 Code Health Details

🟡 Lint Warnings (3)
   src/api/client.py:47    W291 trailing whitespace
   src/api/client.py:52    F841 unused variable 'data'
   src/utils/helpers.py:12 W503 line break before operator

   → empathy health --fix lint

🟡 Coverage Below Target
   Target: 80%  Current: 78%
   Files needing tests:
   - src/api/client.py (65%)
   - src/utils/helpers.py (71%)

   → empathy health --suggest-tests
```

**Level 3: Full Report (--full)**
```
📊 Full Code Health Report
Generated: 2025-12-15 03:15

## Summary
Overall Score: 87/100
Trend: +3 from last week

## Tests (Score: 95/100)
✓ 142 tests passing
✓ No flaky tests detected
✓ Average test time: 2.3s

## Linting (Score: 85/100)
⚠ 3 warnings found
  - 2 formatting issues (auto-fixable)
  - 1 unused variable

## Type Safety (Score: 100/100)
✓ No type errors
✓ 89% type coverage

## Security (Score: 90/100)
⚠ 1 low-severity finding
  - Insecure random (non-crypto use - acceptable)

## Dependencies (Score: 80/100)
⚠ 2 outdated packages
  - requests: 2.28.0 → 2.31.0
  - pytest: 7.3.0 → 7.4.0
```

---

### Phase 3: Auto-Fix Capabilities

**Safe auto-fixes (no confirmation needed):**
- Trailing whitespace
- Import sorting
- Line length (reformatting)
- Missing newlines at EOF

**Prompted auto-fixes (ask first):**
- Unused imports removal
- Unused variables removal
- Dependency updates (minor versions)
- Simple type annotations

**Manual fixes (provide guidance):**
- Logic errors
- Test failures
- Major version upgrades
- Security vulnerabilities

**Implementation:**

```python
class AutoFixer:
    """Apply automatic fixes to code health issues."""

    def __init__(self, config: dict):
        self.safe_fixes = config.get("safe_fixes", True)
        self.prompt_fixes = config.get("prompt_fixes", True)

    async def fix_all(self, report: HealthReport) -> FixResult:
        """Apply all safe fixes, prompt for others."""

    async def fix_category(self, category: str) -> FixResult:
        """Fix issues in a specific category."""

    def preview_fixes(self, report: HealthReport) -> list[FixPreview]:
        """Show what would be fixed without applying."""
```

**CLI:**

```bash
# Preview what would be fixed
empathy health --fix --dry-run

# Fix only safe issues
empathy health --fix --safe-only

# Fix specific category
empathy health --fix lint

# Fix with prompts
empathy health --fix --interactive
```

---

### Phase 4: Claude Code Integration

**Auto-inject health context into sessions:**

```markdown
<!-- .claude/health_context.md (auto-generated) -->

## Current Code Health

**Overall: 87/100** (Good)

### Immediate Actions Needed
1. Fix 3 lint warnings in src/api/client.py
2. Add tests for src/utils/helpers.py (currently 71% coverage)

### Recent Wins
- Fixed 5 type errors yesterday
- Test coverage increased from 75% to 78%

### When Writing Code
- Run `empathy health --fix` before committing
- This project uses black for formatting, ruff for linting
- Target test coverage: 80%
```

**Session startup integration:**

```python
class ClaudeCodeHealthIntegration:
    """Inject health context into Claude Code sessions."""

    def should_show_health(self) -> bool:
        """Check if health report should be shown."""
        # On session start
        # After significant time gap
        # When health score drops

    def generate_health_context(self) -> str:
        """Generate markdown for CLAUDE.md injection."""

    def get_relevant_fixes(self, current_file: str) -> list[Fix]:
        """Get fixes relevant to the file being edited."""
```

---

### Phase 5: Learning & Improvement

**Track patterns over time:**

```python
class HealthTrendTracker:
    """Track code health trends and identify patterns."""

    def record_check(self, report: HealthReport) -> None:
        """Save health check to history."""

    def get_trends(self, days: int = 30) -> HealthTrends:
        """Analyze health trends over time."""

    def identify_hotspots(self) -> list[FileHotspot]:
        """Find files that consistently have issues."""

    def suggest_improvements(self) -> list[Improvement]:
        """Suggest targeted improvements based on patterns."""
```

**Weekly health digest:**

```
📊 Weekly Code Health Digest

Overall trend: ↑ Improving (+5 points)

🎉 Wins this week:
- Resolved 12 lint warnings
- Added tests for 3 files
- Fixed 2 security findings

📈 Areas of improvement:
- Test coverage: 75% → 78%
- Type coverage: 85% → 89%

⚠️ Watch list:
- src/api/client.py: 4 issues this week
- Test suite getting slower (+0.5s avg)

💡 Recommendations:
- Consider adding pre-commit hook for linting
- src/api/client.py may benefit from refactoring
```

---

## Configuration

```yaml
# empathy.config.yml

code_health:
  enabled: true

  # When to show health status
  triggers:
    on_session_start: true
    on_commit: false  # Can enable via pre-commit
    after_inactivity_minutes: 60
    on_health_drop: true  # Alert when score drops significantly

  # Health checks to run
  checks:
    lint:
      enabled: true
      tool: "ruff"  # or "flake8", "pylint"
      weight: 70
    format:
      enabled: true
      tool: "black"  # or "prettier", "rustfmt"
      weight: 50
    types:
      enabled: true
      tool: "pyright"  # or "mypy"
      weight: 90
    tests:
      enabled: true
      tool: "pytest"
      coverage_target: 80
      weight: 85
    security:
      enabled: true
      tool: "bandit"
      weight: 100
    deps:
      enabled: true
      tool: "pip-audit"
      weight: 30

  # Auto-fix settings
  auto_fix:
    safe_fixes: true  # Apply without asking
    prompt_fixes: true  # Ask before applying
    categories:
      - lint
      - format
      # - deps  # Uncomment to auto-update deps

  # Thresholds
  thresholds:
    good: 85
    warning: 70
    critical: 50

  # Learning
  learning:
    track_trends: true
    weekly_digest: true
    identify_hotspots: true
```

---

## User Experience Flow

### Scenario 1: Starting a Session

```
Developer opens project after a break...

📊 Code Health: Good (87/100)

Since your last session:
🎉 You resolved 3 lint warnings
⚠️ 2 new warnings appeared in src/api/client.py

Quick actions:
[1] Fix new warnings  [2] See details  [3] Skip

> 1

✓ Fixed 2 warnings in src/api/client.py
  - Removed unused import 'os'
  - Fixed trailing whitespace on line 47

Ready to code!
```

### Scenario 2: Pre-commit Check

```bash
$ git commit -m "Add new feature"

📊 Pre-commit Health Check

⚠️ 1 issue found:

  src/feature.py:23
  F841 Local variable 'result' is assigned but never used

Options:
[1] Fix automatically  [2] Skip this time  [3] Abort commit

> 1

✓ Removed unused variable 'result'
✓ Commit successful
```

### Scenario 3: Deep Health Check

```bash
$ empathy health --deep

Running comprehensive health check...

Tests.............. ✓ 142 passed (2.3s)
Lint............... ⚠ 3 warnings
Types.............. ✓ No errors
Coverage........... ⚠ 78% (target: 80%)
Security........... ✓ No vulnerabilities
Dependencies....... ⚠ 2 outdated

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overall Score: 87/100 (Good)

[1] Fix 3 lint warnings  [2] Update deps  [3] Full report
```

---

## Implementation Roadmap

| Phase | Feature | Effort | Priority |
|-------|---------|--------|----------|
| 1 | Enhanced health checks | Medium | High |
| 2 | Progressive disclosure | Small | High |
| 3 | Auto-fix capabilities | Medium | High |
| 4 | Claude Code integration | Medium | Medium |
| 5 | Learning & trends | Large | Medium |

**Phase 1-2: v2.2.0** (Core functionality)
**Phase 3: v2.2.5** (Auto-fix)
**Phase 4-5: v2.3.0** (Intelligence)

---

## Success Metrics

- **Adoption**: % of sessions that use health checks
- **Fix rate**: % of auto-fixable issues resolved
- **Trend**: Average health score over time
- **User satisfaction**: Time saved on manual checking
- **Code quality**: Reduction in production bugs

---

## Future Ideas

- **Team health dashboard**: Aggregate health across repos
- **PR health gates**: Block PRs below threshold
- **IDE integration**: VS Code extension for live health
- **Custom checks**: User-defined health rules
- **AI-powered fixes**: Use LLM for complex fixes
- **Gamification**: Health streaks, achievements

---

*Created: 2025-12-15*
*Foundation: Session Status Assistant v2.1.5*
