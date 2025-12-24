# Configuration

Configuration management for the Empathy Framework. Configure via direct instantiation, YAML/JSON files, or environment variables.

## Overview

The configuration system provides flexible options for customizing Empathy Framework behavior:

- **Direct instantiation**: Pass parameters to `EmpathyConfig()` or `EmpathyOS()`
- **YAML/JSON files**: Load from `empathy.config.yml` or `empathy.config.json`
- **Environment variables**: Use `EMPATHY_*` prefixed variables
- **Validation**: Automatic validation on load with helpful error messages

## Quick Start

### Direct Configuration

```python
from empathy_os import EmpathyConfig, EmpathyOS

# Option 1: Configure EmpathyOS directly
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75,
    persistence_enabled=True
)

# Option 2: Use EmpathyConfig object
config = EmpathyConfig(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75
)
empathy = EmpathyOS.from_config(config)
```

### YAML Configuration

Create `empathy.config.yml`:

```yaml
user_id: "user_123"
target_level: 4
confidence_threshold: 0.75
persistence_enabled: true
persistence_backend: "sqlite"
persistence_path: ".empathy"
metrics_enabled: true
```

Load it:

```python
from empathy_os import load_config, EmpathyOS

config = load_config(filepath="empathy.config.yml")
empathy = EmpathyOS.from_config(config)
```

### Environment Variables

```bash
export EMPATHY_USER_ID="user_123"
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75
```

```python
from empathy_os import load_config

# Automatically loads from environment
config = load_config(use_env=True)
```

## Class Reference

::: empathy_os.config.EmpathyConfig
    options:
      show_root_heading: false
      show_source: false
      heading_level: 3

## Configuration Options

### Core Settings

#### `user_id` (str, required)
Unique identifier for the user or system.

**Example:**
```python
config = EmpathyConfig(user_id="user_123")
```

#### `target_level` (int, default: 4)
Target empathy level (1-5). System will progress toward this level as trust builds.

- **1**: Reactive (basic Q&A)
- **2**: Guided (asks questions)
- **3**: Proactive (suggests improvements)
- **4**: Anticipatory (predicts problems) ⭐ Recommended
- **5**: Transformative (reshapes workflows)

**Example:**
```python
config = EmpathyConfig(target_level=4)  # Aim for Level 4
```

#### `confidence_threshold` (float, default: 0.75)
Minimum confidence score (0.0-1.0) required for predictions and suggestions.

**Higher values** = More conservative (fewer, higher-quality predictions)
**Lower values** = More aggressive (more predictions, potentially lower quality)

**Example:**
```python
# Conservative: Only high-confidence predictions
config = EmpathyConfig(confidence_threshold=0.85)

# Aggressive: More predictions, accept lower confidence
config = EmpathyConfig(confidence_threshold=0.60)
```

### Trust Settings

#### `trust_building_rate` (float, default: 0.05)
How much trust increases on successful interactions (0.0-1.0).

**Example:**
```python
# Fast trust building (+10% per success)
config = EmpathyConfig(trust_building_rate=0.10)

# Slow trust building (+2% per success)
config = EmpathyConfig(trust_building_rate=0.02)
```

#### `trust_erosion_rate` (float, default: 0.10)
How much trust decreases on failed interactions (0.0-1.0).

**Example:**
```python
# Forgiving: Small trust loss on failure
config = EmpathyConfig(trust_erosion_rate=0.05)

# Strict: Large trust loss on failure
config = EmpathyConfig(trust_erosion_rate=0.20)
```

### Persistence Settings

#### `persistence_enabled` (bool, default: True)
Enable saving patterns, metrics, and state to disk.

**Example:**
```python
# Production: Enable persistence
config = EmpathyConfig(persistence_enabled=True)

# Testing: Disable persistence
config = EmpathyConfig(persistence_enabled=False)
```

#### `persistence_backend` (str, default: "sqlite")
Storage backend for persistence.

**Options:**
- `"sqlite"` - SQLite database (local development)
- `"postgresql"` - PostgreSQL (production)
- `"json"` - JSON files (backup/export)

**Example:**
```python
# Local development
config = EmpathyConfig(persistence_backend="sqlite")

# Production
config = EmpathyConfig(
    persistence_backend="postgresql",
    persistence_path="postgresql://user:pass@localhost/empathy"
)
```

#### `persistence_path` (str, default: ".empathy")
Path for storing persistence data.

**Example:**
```python
# Default location
config = EmpathyConfig(persistence_path=".empathy")

# Custom location
config = EmpathyConfig(persistence_path="/var/lib/empathy")
```

### Metrics Settings

#### `metrics_enabled` (bool, default: True)
Enable metrics collection for monitoring and analytics.

**Example:**
```python
config = EmpathyConfig(metrics_enabled=True)
```

#### `metrics_path` (str, default: ".empathy/metrics.db")
Path for storing metrics data.

**Example:**
```python
config = EmpathyConfig(metrics_path="/var/lib/empathy/metrics.db")
```

### Pattern Library Settings

#### `pattern_library_enabled` (bool, default: True)
Enable pattern discovery and learning.

**Example:**
```python
# Disable for simple use cases
config = EmpathyConfig(pattern_library_enabled=False)
```

#### `pattern_sharing` (bool, default: False)
Enable pattern sharing across multiple agents (multi-agent coordination).

**Example:**
```python
# Enable for multi-agent teams
config = EmpathyConfig(
    pattern_sharing=True,
    pattern_library_path="shared_patterns.db"
)
```

#### `pattern_confidence_threshold` (float, default: 0.70)
Minimum confidence for applying learned patterns.

**Example:**
```python
config = EmpathyConfig(pattern_confidence_threshold=0.80)
```

## Configuration Methods

### `load_config()`

Load configuration from file or environment.

```python
from empathy_os import load_config

# Load from YAML file
config = load_config(filepath="empathy.config.yml")

# Load from JSON file
config = load_config(filepath="empathy.config.json")

# Load from environment variables
config = load_config(use_env=True)

# Load from file with environment overrides
config = load_config(filepath="empathy.config.yml", use_env=True)
```

### `to_yaml()` / `to_json()`

Save configuration to file.

```python
config = EmpathyConfig(user_id="user_123", target_level=4)

# Save as YAML
config.to_yaml("empathy.config.yml")

# Save as JSON
config.to_json("empathy.config.json")
```

### `validate()`

Validate configuration values.

```python
config = EmpathyConfig(user_id="user_123", target_level=4)

try:
    config.validate()
    print("✓ Configuration valid")
except ValueError as e:
    print(f"✗ Configuration invalid: {e}")
```

## Configuration Patterns

### Development Configuration

```yaml
# empathy.dev.yml
user_id: "dev_user"
target_level: 4
confidence_threshold: 0.70
persistence_enabled: true
persistence_backend: "sqlite"
persistence_path: ".empathy"
metrics_enabled: true
```

### Production Configuration

```yaml
# empathy.prod.yml
user_id: "prod_system"
target_level: 4
confidence_threshold: 0.80
persistence_enabled: true
persistence_backend: "postgresql"
persistence_path: "postgresql://user:pass@db.example.com/empathy"
metrics_enabled: true
metrics_path: "postgresql://user:pass@db.example.com/metrics"

# Security settings
trust_erosion_rate: 0.15  # Stricter trust management
pattern_confidence_threshold: 0.85  # Higher quality patterns
```

### Testing Configuration

```python
# For unit tests
config = EmpathyConfig(
    user_id="test_user",
    target_level=4,
    persistence_enabled=False,  # Don't save during tests
    metrics_enabled=False       # Don't collect metrics during tests
)
```

## Environment Variable Reference

All configuration options can be set via environment variables with the `EMPATHY_` prefix:

```bash
# Core settings
export EMPATHY_USER_ID="user_123"
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75

# Trust settings
export EMPATHY_TRUST_BUILDING_RATE=0.05
export EMPATHY_TRUST_EROSION_RATE=0.10

# Persistence settings
export EMPATHY_PERSISTENCE_ENABLED=true
export EMPATHY_PERSISTENCE_BACKEND=sqlite
export EMPATHY_PERSISTENCE_PATH=.empathy

# Metrics settings
export EMPATHY_METRICS_ENABLED=true
export EMPATHY_METRICS_PATH=.empathy/metrics.db

# Pattern library settings
export EMPATHY_PATTERN_LIBRARY_ENABLED=true
export EMPATHY_PATTERN_SHARING=false
export EMPATHY_PATTERN_CONFIDENCE_THRESHOLD=0.70
```

## See Also

- [EmpathyOS API](empathy-os.md)
- [Quick Start Guide](../tutorials/quickstart.md)
- [Configuration Examples](../reference/configuration.md)
