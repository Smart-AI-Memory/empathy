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

Initialize a new project with a configuration file:

```bash
# Create YAML config (default)
empathy-framework init

# Create JSON config
empathy-framework init --format json

# Specify output path
empathy-framework init --format yaml --output my-config.yml
```

This creates a configuration file with default settings that you can customize.

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

## Getting Help

For more information on any command:

```bash
empathy-framework --help
empathy-framework patterns --help
empathy-framework metrics --help
```

For bugs and feature requests, visit:
https://github.com/Deep-Study-AI/Empathy/issues
