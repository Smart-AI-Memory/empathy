# Configuration

Learn how to configure the Empathy Framework for your needs.

## Configuration Methods

### 1. Direct Instantiation

```python
from empathy_os import EmpathyOS

empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75,
    persistence_enabled=True
)
```

### 2. YAML Configuration File

Create `empathy.config.yml`:

```yaml
user_id: "user_123"
target_level: 4
confidence_threshold: 0.75
persistence_enabled: true
persistence_backend: "sqlite"
persistence_path: ".empathy"
```

Load it:

```python
from empathy_os import load_config

config = load_config(filepath="empathy.config.yml")
empathy = EmpathyOS.from_config(config)
```

### 3. Environment Variables

```bash
export EMPATHY_USER_ID="user_123"
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75
```

## Configuration Options

### Core Settings

- `user_id` (str): Unique user identifier
- `target_level` (int): Target empathy level (1-5)
- `confidence_threshold` (float): Minimum confidence for predictions (0.0-1.0)

### Trust Settings

- `trust_building_rate` (float): How fast trust increases (default: 0.05)
- `trust_erosion_rate` (float): How fast trust decreases on failures (default: 0.10)

### Persistence Settings

- `persistence_enabled` (bool): Enable pattern storage (default: True)
- `persistence_backend` (str): Backend type ("sqlite", "postgresql")
- `persistence_path` (str): Storage location (default: ".empathy")

### Metrics Settings

- `metrics_enabled` (bool): Enable metrics collection (default: True)
- `metrics_path` (str): Metrics storage location

## Next Steps

- **[Examples](../tutorials/tutorials/examples/simple-chatbot.md)**: See configuration in action
- **[API Reference](../reference/empathy-os.md)**: Complete API documentation
