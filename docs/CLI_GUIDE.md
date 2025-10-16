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
Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
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
