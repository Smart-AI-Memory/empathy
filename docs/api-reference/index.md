# API Reference

Complete API documentation for the Empathy Framework.

## Overview

The Empathy Framework provides a comprehensive Python API for building AI systems with five levels of empathy:

- **Level 1**: Reactive (basic Q&A)
- **Level 2**: Guided (clarifying questions)
- **Level 3**: Proactive (suggests improvements)
- **Level 4**: Anticipatory (predicts problems)
- **Level 5**: Transformative (reshapes workflows)

## Core Modules

### [EmpathyOS](empathy-os.md)
Main entry point for the framework. Handles interaction logic, level progression, and trust management.

**Key Classes:**
- `EmpathyOS` - Primary interface for empathy interactions

### [Configuration](config.md)
Configuration management for the framework.

**Key Classes:**
- `EmpathyConfig` - Configuration container with validation
- `load_config()` - Load configuration from files or environment

### [Core](core.md)
Core data structures and state management.

**Key Classes:**
- `CollaborationState` - Tracks trust, level, and interaction history
- `EmpathyResponse` - Response container with metadata
- `EmpathyLevel` - Enumeration of empathy levels

### [Pattern Library](pattern-library.md)
Pattern recognition and learning system for multi-agent coordination.

**Key Classes:**
- `PatternLibrary` - Manages pattern discovery and sharing
- `Pattern` - Individual pattern with confidence tracking
- `PatternMatch` - Pattern matching results

### [Persistence](persistence.md)
Data persistence for patterns, metrics, and state.

**Key Classes:**
- `PatternPersistence` - Save/load pattern libraries (JSON, SQLite)
- `StateManager` - Manage user collaboration states
- `MetricsCollector` - Track usage metrics and performance

### [LLM Toolkit](llm-toolkit.md)
LLM provider integration with security controls.

**Key Classes:**
- `EmpathyLLM` - Unified LLM interface with empathy integration
- `PIIScrubber` - PII detection and scrubbing
- `SecretsDetector` - API key and credential detection
- `AuditLogger` - Compliance and security audit logging

## Quick Links

- [Getting Started Guide](../getting-started/quickstart.md)
- [Configuration Options](../getting-started/configuration.md)
- [Examples](../examples/simple-chatbot.md)

## Installation

```bash
pip install empathy-framework
```

For LLM support:
```bash
pip install empathy-framework[llm]
```

For healthcare applications:
```bash
pip install empathy-framework[healthcare]
```

## Basic Usage

```python
from empathy_os import EmpathyOS

# Create Level 4 (Anticipatory) system
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75
)

# Interact
response = empathy.interact(
    user_id="user_123",
    user_input="I'm about to deploy this change to production",
    context={"deployment": "production"}
)

print(response.response)
print(f"Level: {response.level}")
print(f"Predictions: {response.predictions}")
```

## License

Fair Source License 0.9 - Free for teams up to 5, commercial license required for 6+ employees.
