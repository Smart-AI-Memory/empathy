# Persistence

Data persistence for patterns, metrics, and collaboration state.

## Overview

The persistence layer provides storage and retrieval for:

- **Pattern Libraries**: Save/load pattern collections (JSON, SQLite)
- **Collaboration State**: Persist user trust levels and interaction history
- **Metrics**: Track usage, performance, and success rates
- **State Management**: Save/restore complete system state

## Backends

### Local Development
- **SQLite**: File-based database for local development
- **JSON**: Human-readable format for backups and exports

### Production
- **PostgreSQL**: Production-grade database with full ACID support
- **Cloud Storage**: S3, Azure Blob, GCS for pattern library backups

## Class Reference

### PatternPersistence

::: empathy_os.persistence.PatternPersistence
    options:
      show_root_heading: false
      show_source: false
      heading_level: 4

Save and load pattern libraries.

**Static Methods:**
- `save_to_json(library, filepath)` - Save to JSON file
- `load_from_json(filepath)` - Load from JSON file
- `save_to_sqlite(library, db_path)` - Save to SQLite database
- `load_from_sqlite(db_path)` - Load from SQLite database

**Example:**
```python
from empathy_os.pattern_library import PatternLibrary
from empathy_os.persistence import PatternPersistence

# Create and populate library
library = PatternLibrary()
# ... add patterns ...

# Save to JSON (human-readable)
PatternPersistence.save_to_json(library, "patterns.json")

# Save to SQLite (production)
PatternPersistence.save_to_sqlite(library, "patterns.db")

# Load later
json_library = PatternPersistence.load_from_json("patterns.json")
sqlite_library = PatternPersistence.load_from_sqlite("patterns.db")

print(f"Loaded {len(json_library.patterns)} patterns from JSON")
print(f"Loaded {len(sqlite_library.patterns)} patterns from SQLite")
```

### StateManager

::: empathy_os.persistence.StateManager
    options:
      show_root_heading: false
      show_source: false
      heading_level: 4

Manage user collaboration states.

**Methods:**
- `save_state(user_id, state)` - Save user's collaboration state
- `load_state(user_id)` - Load user's collaboration state
- `list_users()` - List all users with saved states
- `delete_state(user_id)` - Delete user's state

**Example:**
```python
from empathy_os import EmpathyOS
from empathy_os.persistence import StateManager

# Initialize state manager
state_manager = StateManager(state_dir=".empathy/state")

# Create agent and interact
empathy = EmpathyOS(user_id="user_123", target_level=4)

# ... interactions happen, trust builds ...

# Save state
state_manager.save_state("user_123", empathy.collaboration_state)

# Later, load state
saved_state = state_manager.load_state("user_123")
print(f"Restored trust level: {saved_state.trust_level:.0%}")
print(f"Restored empathy level: {saved_state.current_level}")

# List all saved users
users = state_manager.list_users()
print(f"Users with saved states: {users}")
```

### MetricsCollector

::: empathy_os.persistence.MetricsCollector
    options:
      show_root_heading: false
      show_source: false
      heading_level: 4

Track usage metrics and performance.

**Methods:**
- `record_interaction(user_id, level, success, response_time_ms)` - Record interaction
- `get_user_stats(user_id)` - Get statistics for a user
- `get_global_stats()` - Get statistics across all users
- `export_metrics(filepath)` - Export metrics to file

**Example:**
```python
from empathy_os.persistence import MetricsCollector
import time

# Initialize collector
collector = MetricsCollector(db_path=".empathy/metrics.db")

# Record interactions
start = time.time()
response = empathy.interact(user_id="user_123", user_input="...", context={})
duration_ms = (time.time() - start) * 1000

collector.record_interaction(
    user_id="user_123",
    level=response.level,
    success=True,
    response_time_ms=duration_ms
)

# Get user statistics
stats = collector.get_user_stats("user_123")
print(f"Total interactions: {stats['total_operations']}")
print(f"Success rate: {stats['success_rate']:.0%}")
print(f"Avg response time: {stats['avg_response_time_ms']:.0f}ms")
print(f"\nLevel usage:")
for level in range(1, 6):
    count = stats.get(f'level_{level}_count', 0)
    print(f"  Level {level}: {count} times")

# Get global statistics
global_stats = collector.get_global_stats()
print(f"\nTotal users: {global_stats['total_users']}")
print(f"Total interactions: {global_stats['total_interactions']}")
```

## Usage Patterns

### Complete Persistence Setup

```python
from empathy_os import EmpathyOS, EmpathyConfig
from empathy_os.pattern_library import PatternLibrary
from empathy_os.persistence import (
    PatternPersistence,
    StateManager,
    MetricsCollector
)

# Initialize persistence components
config = EmpathyConfig(
    user_id="user_123",
    target_level=4,
    persistence_enabled=True,
    persistence_path=".empathy"
)

pattern_library = PatternLibrary()
state_manager = StateManager(state_dir=".empathy/state")
metrics = MetricsCollector(db_path=".empathy/metrics.db")

# Load existing patterns if available
try:
    pattern_library = PatternPersistence.load_from_sqlite(".empathy/patterns.db")
    print(f"Loaded {len(pattern_library.patterns)} existing patterns")
except FileNotFoundError:
    print("No existing patterns, starting fresh")

# Create agent with persistence
empathy = EmpathyOS(
    user_id=config.user_id,
    target_level=config.target_level,
    pattern_library=pattern_library
)

# Try to load saved state
try:
    saved_state = state_manager.load_state(config.user_id)
    empathy.collaboration_state = saved_state
    print(f"Restored state: trust={saved_state.trust_level:.0%}, level={saved_state.current_level}")
except FileNotFoundError:
    print("No saved state, starting fresh")

# Interaction with persistence
response = empathy.interact(
    user_id=config.user_id,
    user_input="How do I deploy to production?",
    context={"task": "deployment"}
)

# Record metrics
metrics.record_interaction(
    user_id=config.user_id,
    level=response.level,
    success=True,
    response_time_ms=145.3
)

# Save state after interaction
state_manager.save_state(config.user_id, empathy.collaboration_state)

# Save patterns
PatternPersistence.save_to_sqlite(pattern_library, ".empathy/patterns.db")

print("All data persisted successfully")
```

### JSON Pattern Export/Import

```python
from empathy_os.persistence import PatternPersistence

# Export for backup or sharing
library = PatternPersistence.load_from_sqlite("patterns.db")
PatternPersistence.save_to_json(library, "patterns_backup.json")

# Import to different system
imported = PatternPersistence.load_from_json("patterns_backup.json")
PatternPersistence.save_to_sqlite(imported, "new_system_patterns.db")

print(f"Migrated {len(imported.patterns)} patterns")
```

### Metrics Dashboard

```python
from empathy_os.persistence import MetricsCollector

collector = MetricsCollector(db_path="metrics.db")

# Get all users
users = collector.get_all_users()

print("=== Metrics Dashboard ===\n")

for user_id in users:
    stats = collector.get_user_stats(user_id)

    print(f"User: {user_id}")
    print(f"  Total interactions: {stats['total_operations']}")
    print(f"  Success rate: {stats['success_rate']:.0%}")
    print(f"  Avg response time: {stats.get('avg_response_time_ms', 0):.0f}ms")
    print(f"  Current level: {stats.get('current_level', 1)}")

    # Most used level
    level_counts = [
        (level, stats.get(f'level_{level}_count', 0))
        for level in range(1, 6)
    ]
    most_used_level = max(level_counts, key=lambda x: x[1])
    print(f"  Most used level: Level {most_used_level[0]} ({most_used_level[1]} times)")
    print()

# Global statistics
global_stats = collector.get_global_stats()
print("Global Statistics:")
print(f"  Total users: {global_stats['total_users']}")
print(f"  Total interactions: {global_stats['total_interactions']}")
print(f"  Overall success rate: {global_stats['success_rate']:.0%}")
```

### State Migration

```python
from empathy_os.persistence import StateManager

# Migrate states between systems
old_manager = StateManager(state_dir="/old/system/.empathy/state")
new_manager = StateManager(state_dir="/new/system/.empathy/state")

users = old_manager.list_users()
print(f"Migrating {len(users)} user states...")

for user_id in users:
    state = old_manager.load_state(user_id)
    new_manager.save_state(user_id, state)
    print(f"  Migrated {user_id}: trust={state.trust_level:.0%}, level={state.current_level}")

print("Migration complete!")
```

## Database Schema

### SQLite Pattern Schema

```sql
CREATE TABLE patterns (
    id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL,
    pattern_type TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    context TEXT,  -- JSON
    code TEXT,
    confidence REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    tags TEXT,  -- JSON array
    discovered_at TIMESTAMP,
    last_used TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE pattern_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    success BOOLEAN NOT NULL,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (pattern_id) REFERENCES patterns(id)
);

CREATE INDEX idx_patterns_agent ON patterns(agent_id);
CREATE INDEX idx_patterns_type ON patterns(pattern_type);
CREATE INDEX idx_patterns_confidence ON patterns(confidence);
```

### SQLite Metrics Schema

```sql
CREATE TABLE interactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    empathy_level INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    response_time_ms REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_interactions_user ON interactions(user_id);
CREATE INDEX idx_interactions_timestamp ON interactions(timestamp);
```

## JSON Format

### Pattern Library JSON

```json
{
  "patterns": [
    {
      "id": "pat_123",
      "agent_id": "agent_1",
      "pattern_type": "suggestion",
      "name": "Add error handling",
      "description": "Suggest error handling for API calls",
      "context": {"task": "api_call"},
      "code": "Always wrap API calls in try-except blocks",
      "confidence": 0.85,
      "usage_count": 10,
      "success_count": 9,
      "failure_count": 1,
      "tags": ["error-handling", "api", "best-practice"],
      "discovered_at": "2025-01-15T10:30:00",
      "last_used": "2025-01-20T14:45:00"
    }
  ],
  "agent_contributions": {
    "agent_1": ["pat_123"]
  },
  "metadata": {
    "saved_at": "2025-01-20T15:00:00",
    "pattern_count": 1,
    "version": "1.0"
  }
}
```

### Collaboration State JSON

```json
{
  "user_id": "user_123",
  "trust_level": 0.65,
  "current_level": 3,
  "target_level": 4,
  "interaction_count": 50,
  "success_count": 45,
  "failure_count": 5,
  "last_interaction": "2025-01-20T15:00:00",
  "created_at": "2025-01-01T00:00:00"
}
```

## Best Practices

### Backup Strategy

```python
import schedule
from datetime import datetime
from empathy_os.persistence import PatternPersistence

def backup_patterns():
    """Daily backup of pattern library"""
    library = PatternPersistence.load_from_sqlite("patterns.db")

    # Backup to JSON with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backups/patterns_{timestamp}.json"

    PatternPersistence.save_to_json(library, backup_path)
    print(f"Backup saved: {backup_path}")

# Schedule daily backups
schedule.every().day.at("02:00").do(backup_patterns)
```

### Performance Optimization

```python
# Use connection pooling for SQLite
import sqlite3
from contextlib import contextmanager

@contextmanager
def get_db_connection(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.close()

# Batch operations
def batch_save_patterns(patterns, db_path):
    """Save multiple patterns in a single transaction"""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        for pattern in patterns:
            cursor.execute(
                """INSERT OR REPLACE INTO patterns (...) VALUES (...)""",
                (...)  # pattern data
            )

        conn.commit()
```

## See Also

- [Pattern Library API](pattern-library.md)
- [EmpathyOS API](empathy-os.md)
- [Configuration API](config.md)
- [CLI Export/Import Commands](../tutorials/quickstart.md#cli-commands)
