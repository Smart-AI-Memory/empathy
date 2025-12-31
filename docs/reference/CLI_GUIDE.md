# Empathy Framework CLI Guide

The Empathy Framework includes a command-line tool for managing configurations, pattern libraries, metrics, and state.

## Installation

```bash
pip install empathy-framework
```

Or for development:

```bash
git clone https://github.com/Deep-Study-AI/Empathy.git
cd Empathy
pip install -e .
```

## Commands

### Version

Display version information:

```bash
empathy-framework version
```

Output:
```
Empathy Framework v1.0.0
Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
```

---

### Init

Initialize a new project with an interactive configuration wizard:

```bash
# Interactive setup wizard (recommended)
empathy init

# Non-interactive with defaults
empathy init --non-interactive

# Overwrite existing config
empathy init --force
```

The wizard guides you through:

- **Provider selection** - Anthropic, OpenAI, Google, Ollama, or Hybrid
- **API key configuration** - Environment variable or direct input
- **Model tier preferences** - Cheap, Capable, Premium model mapping
- **Compliance mode** - Standard or HIPAA

This creates `empathy.config.yml` with your settings.

---

### Validate

Validate a configuration file:

```bash
empathy-framework validate empathy.config.yml
```

Output:
```
✓ Configuration valid: empathy.config.yml

  User ID: alice
  Target Level: 4
  Confidence Threshold: 0.8
  Persistence Backend: sqlite
  Metrics Enabled: True
```

---

### Info

Display framework information:

```bash
# With default config
empathy-framework info

# With custom config
empathy-framework info --config my-config.yml
```

Output:
```
=== Empathy Framework Info ===

Configuration:
  User ID: alice
  Target Level: 4
  Confidence Threshold: 0.8

Persistence:
  Backend: sqlite
  Path: ./empathy_data
  Enabled: True

Metrics:
  Enabled: True
  Path: ./metrics.db

Pattern Library:
  Enabled: True
  Pattern Sharing: True
  Confidence Threshold: 0.3
```

---

### Pattern Library Commands

#### List Patterns

List patterns in a pattern library:

```bash
# List patterns from JSON file
empathy-framework patterns list patterns.json

# List patterns from SQLite database
empathy-framework patterns list patterns.db --format sqlite
```

Output:
```
=== Pattern Library: patterns.json ===

Total patterns: 3
Total agents: 2

Patterns:

  [pat_001] Post-deployment documentation
    Agent: agent_1
    Type: sequential
    Confidence: 0.85
    Usage: 12
    Success Rate: 0.83

  [pat_002] Error recovery workflow
    Agent: agent_2
    Type: adaptive
    Confidence: 0.92
    Usage: 8
    Success Rate: 1.00
```

#### Export Patterns

Export patterns from one format to another:

```bash
# JSON to SQLite
empathy-framework patterns export patterns.json patterns.db \
  --input-format json --output-format sqlite

# SQLite to JSON
empathy-framework patterns export patterns.db patterns.json \
  --input-format sqlite --output-format json
```

Output:
```
✓ Loaded 3 patterns from patterns.json
✓ Saved 3 patterns to patterns.db
```

---

### Metrics Commands

#### Show Metrics

Display metrics for a specific user:

```bash
# Default metrics.db location
empathy-framework metrics show alice

# Custom database location
empathy-framework metrics show alice --db /path/to/metrics.db
```

Output:
```
=== Metrics for User: alice ===

Total Operations: 45
Success Rate: 88.9%
Average Response Time: 234 ms

First Use: 2025-10-01 14:23:45
Last Use: 2025-10-14 09:15:22

Empathy Level Usage:
  Level 1: 5 uses
  Level 2: 12 uses
  Level 3: 18 uses
  Level 4: 8 uses
  Level 5: 2 uses
```

---

### State Management Commands

#### List Saved States

List all saved user states:

```bash
# Default state directory
empathy-framework state list

# Custom state directory
empathy-framework state list --state-dir /path/to/states
```

Output:
```
=== Saved User States: ./empathy_state ===

Total users: 3

Users:
  - alice
  - bob
  - charlie
```

---

### Pattern Enhancement Commands (New in v2.1.4)

#### Resolve Investigating Patterns

Mark investigating bug patterns as resolved with root cause and fix:

```bash
# List all investigating bugs
empathy patterns resolve

# Resolve a specific bug
empathy patterns resolve bug_20251212_3c5b9951 \
  --root-cause "Missing null check on API response" \
  --fix "Added optional chaining operator" \
  --fix-code "data?.items ?? []" \
  --time 15 \
  --resolved-by "@developer"
```

Output:
```
✓ Resolved: bug_20251212_3c5b9951
✓ Regenerated patterns_summary.md
```

---

#### Pattern-Based Code Review

Review code against historical bug patterns:

```bash
# Review recent changes
empathy review

# Review staged changes only
empathy review --staged

# Review specific files
empathy review src/api.py src/utils.py

# Set minimum severity threshold
empathy review --severity warning

# Output as JSON
empathy review --json
```

Output:
```
Code Review Results
========================================

⚠️  src/api.py:47
    Pattern: null_reference (bug_20250915_abc123)
    Risk: API response accessed without null check
    Historical: "API returned null instead of empty array"
    Suggestion: Add fallback - data?.items ?? []
    Confidence: 85%

Summary: 1 findings in 1 file(s)

Recommendations:
  • Fix 1 null_reference issue(s): Add null check
```

---

### Session Status Assistant (New in v2.1.5)

#### Check Project Status

Get a prioritized status report of your project when you return after a break:

```bash
# Show status (only if enough time has passed since last interaction)
empathy status

# Force show status regardless of inactivity
empathy status --force

# Show all items (no limit)
empathy status --full

# Output as JSON
empathy status --json

# Select an item to get its action prompt
empathy status --select 1
```

Output:
```
📊 Project Status (6 items need attention)

🎉 Wins since last session:
   • 3 bugs resolved since last session

🔴 Security: 2 decisions pending review
   → Review XSS finding in auth.ts

🟡 Bugs: 3 investigating, 1 high-severity
   → Resolve null_reference in OrderList.tsx

🟢 Tech Debt: Stable (343 items, +0 this week)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Fix high-severity bug  [2] Review security  [3] See full status
```

#### Priority System

Items are prioritized by severity:

| Priority | Category | Weight | Icon |
|----------|----------|--------|------|
| P0 | Security pending | 100 | 🔴 |
| P1 | Bugs high-severity | 80 | 🔴 |
| P2 | Bugs investigating | 60 | 🟡 |
| P3 | Tech debt increasing | 40 | 🟡 |
| P4 | Roadmap unchecked | 30 | 🔵 |
| P5 | Commits WIP/TODO | 20 | ⚪ |

#### Interactive Selection

Select an item number to get its full action prompt:

```bash
empathy status --force --select 1
```

Output:
```
Action prompt for selection 1:

Continue investigating bug bug_20251212_97c0f72f:
TypeError: Cannot read property 'map' of undefined.
Use: empathy patterns resolve bug_20251212_97c0f72f --root-cause '<cause>' --fix '<fix>'
```

#### Configuration

Set inactivity threshold (default: 60 minutes):

```bash
empathy status --inactivity 30  # Show after 30 min of inactivity
```

---

### Code Health Assistant (New in v2.2.0)

#### Quick Health Check

Run fast health checks (lint, format, types):

```bash
empathy health
```

Output:
```
📊 Code Health: Good (87/100)

🟢 Tests: 142 passed, 0 failed
🟡 Lint: 3 warnings
🟢 Types: No errors

[1] Fix 3 auto-fixable issues  [2] See details  [3] Full report
```

#### Comprehensive Health Check

Run all health checks including tests, security, and dependencies:

```bash
empathy health --deep
```

#### Specific Check

Run only a specific category of health checks:

```bash
empathy health --check lint
empathy health --check format
empathy health --check types
empathy health --check tests
empathy health --check security
empathy health --check deps
```

#### Auto-Fix Issues

Preview what would be fixed:

```bash
empathy health --fix --dry-run
```

Apply safe fixes automatically:

```bash
empathy health --fix
```

Fix specific category:

```bash
empathy health --fix --check lint
```

Interactive mode (prompt for non-safe fixes):

```bash
empathy health --fix --interactive
```

#### Detail Levels

Summary view (default):
```bash
empathy health
```

Details view (shows individual issues):
```bash
empathy health --details
```

Full report:
```bash
empathy health --full
```

#### Health Trends

View health trends over time:

```bash
empathy health --trends 30  # Last 30 days
```

Output:
```
📈 Health Trends (30 days)

Average Score: 85/100
Trend: improving (+5)

Recent scores:
  2025-12-15: 87/100
  2025-12-14: 85/100
  2025-12-13: 82/100

🔥 Hotspots (files with recurring issues):
  src/api/client.py: 12 issues
  src/utils/helpers.py: 8 issues
```

#### JSON Output

Get machine-readable output:

```bash
empathy health --json
```

---

## Usage Examples

### Development Workflow

```bash
# 1. Initialize project
empathy-framework init --format yaml --output dev-config.yml

# 2. Edit dev-config.yml to customize settings
nano dev-config.yml

# 3. Validate configuration
empathy-framework validate dev-config.yml

# 4. Check framework info
empathy-framework info --config dev-config.yml

# 5. Run your application
python my_app.py

# 6. View metrics
empathy-framework metrics show my_user

# 7. List saved states
empathy-framework state list
```

### Production Deployment

```bash
# 1. Create production config
empathy-framework init --format yaml --output prod-config.yml

# 2. Set production values via environment variables
export EMPATHY_USER_ID=prod_system
export EMPATHY_TARGET_LEVEL=5
export EMPATHY_PERSISTENCE_BACKEND=sqlite
export EMPATHY_METRICS_ENABLED=true

# 3. Validate combined config (file + env)
empathy-framework validate prod-config.yml

# 4. Deploy application with config
python -m my_app --config prod-config.yml
```

### Pattern Library Management

```bash
# 1. Export patterns from development to JSON (for version control)
empathy-framework patterns export dev_patterns.db dev_patterns.json \
  --input-format sqlite --output-format json

# 2. Commit to git
git add dev_patterns.json
git commit -m "Update pattern library"

# 3. On production, import patterns to SQLite
empathy-framework patterns export dev_patterns.json prod_patterns.db \
  --input-format json --output-format sqlite

# 4. List patterns to verify
empathy-framework patterns list prod_patterns.db --format sqlite
```

---

## Configuration File Reference

### YAML Example

```yaml
# Core settings
user_id: "alice"
target_level: 4
confidence_threshold: 0.8

# Trust settings
trust_building_rate: 0.05
trust_erosion_rate: 0.10

# Persistence
persistence_enabled: true
persistence_backend: "sqlite"
persistence_path: "./empathy_data"

# State management
state_persistence: true
state_path: "./empathy_state"

# Metrics
metrics_enabled: true
metrics_path: "./metrics.db"

# Logging
log_level: "INFO"
log_file: null
structured_logging: true

# Pattern library
pattern_library_enabled: true
pattern_sharing: true
pattern_confidence_threshold: 0.3

# Advanced
async_enabled: true
feedback_loop_monitoring: true
leverage_point_analysis: true
```

### JSON Example

```json
{
  "user_id": "alice",
  "target_level": 4,
  "confidence_threshold": 0.8,
  "persistence_enabled": true,
  "persistence_backend": "sqlite",
  "metrics_enabled": true,
  "pattern_library_enabled": true
}
```

### Environment Variables

All configuration fields can be set via environment variables with the `EMPATHY_` prefix:

```bash
export EMPATHY_USER_ID=alice
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.8
export EMPATHY_PERSISTENCE_ENABLED=true
export EMPATHY_PERSISTENCE_BACKEND=sqlite
export EMPATHY_METRICS_ENABLED=true
```

Boolean values can be: `true`, `false`, `1`, `0`, `yes`, `no`

---

### Code Inspection Pipeline (New in v2.2.9)

The `empathy-inspect` command provides a unified code inspection pipeline that combines multiple static analysis tools with cross-tool intelligence and pattern learning.

#### Basic Usage

```bash
# Inspect current directory
empathy-inspect .

# Inspect specific path
empathy-inspect ./src

# Quick mode (skip slow checks)
empathy-inspect . --quick

# Verbose output
empathy-inspect . --verbose
```

#### Output Formats

```bash
# Terminal output (default)
empathy-inspect .

# JSON output
empathy-inspect . --format json

# Markdown report
empathy-inspect . --format markdown

# SARIF for GitHub Actions
empathy-inspect . --format sarif

# HTML dashboard
empathy-inspect . --format html

# Save report to file
empathy-inspect . --format html --output report.html
```

**SARIF Integration (GitHub Actions example):**

SARIF is an industry standard supported by GitHub, GitLab, Azure DevOps, Bitbucket, and other CI/CD platforms. While optimized for GitHub, the same output works with any SARIF-compliant system.

```yaml
# .github/workflows/code-quality.yml
- name: Run Empathy Inspect
  run: empathy-inspect . --format sarif --output results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

#### Target Modes

```bash
# Inspect all files (default)
empathy-inspect .

# Only staged git changes
empathy-inspect . --staged

# Only changed files vs HEAD
empathy-inspect . --changed

# Exclude patterns
empathy-inspect . --exclude "**/*.test.py" --exclude "**/migrations/*"
```

#### Auto-Fix

```bash
# Auto-fix safe issues (formatting, imports)
empathy-inspect . --fix
```

#### Baseline & Suppression System

Manage false positives and known issues without cluttering your codebase:

```bash
# Initialize baseline file
empathy-inspect . --baseline-init

# Run inspection (baseline filtering enabled by default)
empathy-inspect .

# Show all findings including suppressed
empathy-inspect . --no-baseline

# Clean up expired suppressions
empathy-inspect . --baseline-cleanup
```

**Inline Suppressions:**

```python
# Suppress a specific rule on this line
eval(user_input)  # empathy:disable S307 reason="Input is validated"

# Suppress a rule on the next line
# empathy:disable-next-line W291 reason="Intentional whitespace"
result = calculate()

# Suppress a rule for entire file (must be in first 10 lines)
# empathy:disable-file B001 reason="Legacy code, refactoring planned"
```

**Baseline File (`.empathy-baseline.json`):**

```json
{
  "version": "1.0",
  "suppressions": {
    "project": [
      {
        "rule_code": "W291",
        "reason": "Formatting handled by pre-commit",
        "expires_at": "2025-03-01T00:00:00"
      }
    ],
    "files": {
      "src/legacy/old_module.py": [
        {
          "rule_code": "B001",
          "reason": "Legacy code, will refactor in Q2"
        }
      ]
    },
    "rules": {
      "E501": {
        "reason": "Line length handled by formatter"
      }
    }
  }
}
```

#### Parallel Execution

```bash
# Run Phase 1 tools in parallel (default)
empathy-inspect .

# Disable parallel execution
empathy-inspect . --no-parallel
```

#### Pattern Learning

```bash
# Enable pattern learning (default)
empathy-inspect .

# Disable pattern learning
empathy-inspect . --no-learning
```

#### Example Output

```
============================================================
  CODE INSPECTION REPORT
============================================================

  Health Score: 87/100 (B) - PASS

  CATEGORY SCORES:
    Lint               92/100  [PASS]
    Security           85/100  [PASS]
    Tests              88/100  [PASS]
    Debt               82/100  [WARN]
    Review             90/100  [PASS]

  FINDINGS: 12 total (3 suppressed)
    HIGH       1
    MEDIUM     8
    LOW        3

  BLOCKING ISSUES (1):
    [HIGH] src/api/client.py
      Potential SQL injection in query parameter...

  RECOMMENDATIONS:
    1. [HIGH] Address 1 high-severity findings
    2. [LOW] Auto-fix 5 issues with `empathy-inspect --fix`

============================================================
  Duration: 2341ms
  Execution ID: insp_20251218_143022_a1b2c3d4
============================================================
```

#### Pipeline Phases

The inspection pipeline runs in 5 phases:

| Phase | Tools | Mode |
|-------|-------|------|
| 1. Static Analysis | Lint, Security, Tech Debt, Test Quality | Parallel |
| 2. Dynamic Analysis | Code Review, Advanced Debugging | Conditional |
| 3. Cross-Analysis | Correlate findings across tools | Sequential |
| 4. Learning | Extract patterns for future use | Optional |
| 5. Reporting | Generate unified report | Always |

#### Language-Aware Analysis

The code review automatically detects file languages and applies appropriate patterns:

| Extension | Language |
|-----------|----------|
| `.py` | Python |
| `.js`, `.jsx` | JavaScript |
| `.ts`, `.tsx` | TypeScript |
| `.rs` | Rust |
| `.go` | Go |
| `.java` | Java |
| `.rb` | Ruby |
| `.c`, `.h` | C |
| `.cpp`, `.hpp` | C++ |
| `.cs` | C# |
| `.swift` | Swift |
| `.php` | PHP |
| `.kt` | Kotlin |

---

### Bug Prediction Workflow (New in v3.5.5)

Predict bugs by analyzing code against learned patterns:

```bash
# Scan current directory
empathy workflow run bug-predict

# Scan specific path
empathy workflow run bug-predict --input '{"path":"./src"}'

# JSON output for CI/CD
empathy workflow run bug-predict --json
```

#### Understanding Scanner Results

The bug prediction scanner detects patterns that historically correlate with bugs:

| Pattern | Severity | Description |
|---------|----------|-------------|
| `dangerous_eval` | High | Use of `eval()` or `exec()` on untrusted input |
| `broad_exception` | Medium | Bare `except:` or `except Exception:` that may mask errors |
| `incomplete_code` | Low | TODO/FIXME comments indicating unfinished work |

#### Smart False Positive Filtering

The scanner automatically filters acceptable patterns:

**Acceptable `broad_exception` uses (not flagged):**
- Version detection with fallback: `except: return "dev"`
- Config loading with defaults: `except: pass  # Fall back to default`
- Optional feature detection: `try: import optional_lib`
- Cleanup/teardown code: `__del__`, `__exit__`, `close()`
- Logging with re-raise: `except: log.error(...); raise`

**Acceptable `dangerous_eval` uses (not flagged):**
- Test fixtures: Code inside `write_text()` for testing
- Scanner test files: `test_bug_predict*`, `test_scanner*`
- Detection code: `if "eval(" in content`

#### Risk Scores

Files are scored 0-100% based on pattern severity and historical correlation:

| Score | Risk Level | Action |
|-------|------------|--------|
| 80-100% | 🔴 HIGH | Immediate attention required |
| 50-79% | 🟠 MODERATE | Review before release |
| 30-49% | 🟡 LOW | Address when convenient |
| 0-29% | 🟢 MINIMAL | No action needed |

#### Customizing Scanner Behavior

See `empathy.config.yml` for customizable exclusions:

```yaml
bug_predict:
  exclude_files:
    - "**/test_*.py"
    - "**/fixtures/**"
  acceptable_exception_contexts:
    - version
    - config
    - cleanup
```

---

### Claude Code Integration (New in v2.3.0)

Sync learned patterns to Claude Code's native rules directory:

```bash
# One-time sync
empathy-sync-claude

# Watch for changes and auto-sync
empathy-sync-claude --watch

# Preview without writing
empathy-sync-claude --dry-run

# Verbose output
empathy-sync-claude --verbose
```

**Output structure:**

```
.claude/rules/empathy/
├── bug-patterns.md          # From patterns/debugging/
├── security-decisions.md    # From patterns/security/
├── tech-debt-hotspots.md    # From patterns/tech_debt/
└── coding-patterns.md       # From patterns/inspection/
```

Claude Code automatically loads these rules at session start, giving it access to your team's bug history, security decisions, and coding patterns.

---

## Quick Reference (Cheatsheet)

### Core Commands

```bash
# Code Health
empathy health                    # Quick health check
empathy health --deep             # Comprehensive analysis
empathy health --fix              # Auto-fix safe issues
empathy health --check lint       # Run specific check

# Code Review
empathy review                    # Review recent changes
empathy review --staged           # Staged changes only

# Code Inspection
empathy-inspect .                 # Inspect current directory
empathy-inspect . --fix           # Auto-fix formatting/imports
empathy-inspect . --format sarif  # SARIF for GitHub Actions
empathy-inspect . --format html   # HTML dashboard
```

### Memory & Patterns

```bash
# Memory Control Panel
empathy-memory serve              # Start Redis + API (recommended)
empathy-memory status             # Show memory status
empathy-memory patterns           # List stored patterns

# Pattern Management
empathy patterns list             # List patterns
empathy patterns resolve <id>     # Mark bug as resolved

# Claude Code Sync
empathy-sync-claude               # Sync to .claude/rules/empathy/
empathy-sync-claude --watch       # Auto-sync on changes
```

### Quick Workflows

```bash
# Morning check
empathy health --deep && empathy status

# Before commit
empathy review --staged && empathy-inspect . --staged --quick

# Fix everything
empathy health --fix && empathy-inspect . --fix

# Sync to Claude Code
empathy-sync-claude --verbose
```

### CI/CD Integration

**GitHub Actions (SARIF):**
```yaml
- name: Run Empathy Inspect
  run: empathy-inspect . --format sarif -o results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

**Pre-commit Hook:**
```yaml
repos:
  - repo: local
    hooks:
      - id: empathy-review
        name: Pattern-based review
        entry: empathy review --staged --severity error
        language: system
        pass_filenames: false
```

### Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...          # Claude API key
EMPATHY_CONFIG=./config.yaml      # Custom config path
EMPATHY_LOG_LEVEL=DEBUG           # Logging level
REDIS_URL=redis://localhost:6379  # Redis connection
```

---

## Getting Help

For more information on any command:

```bash
empathy --help
empathy <command> --help
empathy-inspect --help
empathy-memory --help
empathy-sync-claude --help
```

For bugs and feature requests, visit:
https://github.com/Smart-AI-Memory/empathy-framework/issues
