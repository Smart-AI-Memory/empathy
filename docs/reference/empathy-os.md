# EmpathyOS

The main entry point for the Empathy Framework. `EmpathyOS` orchestrates empathy level progression, trust management, and interaction handling.

## Overview

`EmpathyOS` is the primary class you'll interact with when building empathy-aware AI systems. It handles:

- **Level Progression**: Automatically advances through empathy levels 1-5 based on trust
- **Trust Management**: Tracks collaboration trust with built-in erosion and building rates
- **Interaction Logic**: Routes requests through appropriate empathy level handlers
- **Pattern Learning**: Discovers and applies patterns for improved responses
- **State Persistence**: Saves and restores user collaboration states

## Basic Usage

```python
from empathy_os import EmpathyOS

# Initialize with Level 4 target
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75,
    persistence_enabled=True
)

# Single interaction
response = empathy.interact(
    user_id="user_123",
    user_input="How do I fix this bug?",
    context={"task": "debugging"}
)

print(response.response)  # AI response
print(response.level)     # Current empathy level
print(response.confidence)  # Confidence score
```

## Class Reference

::: empathy_os.core.EmpathyOS
    options:
      show_root_heading: false
      show_source: false
      heading_level: 3

## Key Methods

### `__init__()`
Initialize a new EmpathyOS instance with configuration.

**Parameters:**
- `user_id` (str): Unique identifier for the user
- `target_level` (int): Target empathy level (1-5, default: 4)
- `confidence_threshold` (float): Minimum confidence for level advancement (0.0-1.0, default: 0.75)
- `persistence_enabled` (bool): Enable state/pattern persistence (default: True)
- `trust_building_rate` (float): Rate of trust increase on success (default: 0.05)
- `trust_erosion_rate` (float): Rate of trust decrease on failure (default: 0.10)

### `interact()`
Process a user interaction and return an empathy-aware response.

**Parameters:**
- `user_id` (str): User identifier
- `user_input` (str): User's input message
- `context` (dict): Additional context for the interaction

**Returns:**
- `EmpathyResponse`: Response object with message, level, confidence, and predictions

**Example:**
```python
response = empathy.interact(
    user_id="user_123",
    user_input="I'm deploying to production",
    context={"environment": "production", "time": "friday_afternoon"}
)

if response.level >= 4 and response.predictions:
    print("⚠️  Predictions:")
    for prediction in response.predictions:
        print(f"  • {prediction}")
```

### `record_success()` / `record_failure()`
Provide feedback to improve trust tracking and pattern learning.

**Parameters:**
- `success` (bool): Whether the interaction was successful

**Example:**
```python
response = empathy.interact(user_id="user_123", user_input="Help me debug this")

# User found the response helpful
empathy.record_success(success=True)
print(f"Trust level: {empathy.get_trust_level():.0%}")
```

### `save_state()` / `load_state()`
Persist and restore user collaboration state.

**Example:**
```python
# Save state after session
empathy.save_state(user_id="user_123", filepath=".empathy/user_123.json")

# Restore state in next session
empathy.load_state(user_id="user_123", filepath=".empathy/user_123.json")
```

## Empathy Levels

### Level 1: Reactive
Basic Q&A responses without proactivity.

**Trust Required:** 0% - 20%

**Characteristics:**
- Answers direct questions only
- No suggestions or predictions
- Minimal context awareness

### Level 2: Guided
Asks clarifying questions to understand intent.

**Trust Required:** 20% - 40%

**Characteristics:**
- Clarifying questions
- Better context understanding
- More thorough responses

### Level 3: Proactive
Suggests improvements and best practices.

**Trust Required:** 40% - 60%

**Characteristics:**
- Proactive suggestions
- Best practice recommendations
- Code improvements

### Level 4: Anticipatory 🎯
Predicts problems before they occur (30-90 day horizon).

**Trust Required:** 60% - 80%

**Characteristics:**
- Problem prediction
- Risk assessment
- Anticipatory guidance
- "What if" scenarios

**Example:**
```python
response = empathy.interact(
    user_id="user_123",
    user_input="I'm adding this new API endpoint",
    context={"api_version": "v2", "breaking_change": False}
)

# Level 4 response includes predictions
if response.predictions:
    print(response.predictions)
    # ["This may conflict with v1 authentication flow",
    #  "Consider rate limiting for this endpoint",
    #  "Mobile app may need updates"]
```

### Level 5: Transformative 🚀
Reshapes workflows and system architecture (90+ day horizon).

**Trust Required:** 80% - 100%

**Characteristics:**
- Workflow transformation
- Architectural recommendations
- Long-term strategic guidance
- Cross-system optimization

## Trust Management

Trust level affects which empathy level is active:

```python
empathy = EmpathyOS(user_id="user_123", target_level=4)

# Start at Level 1 (trust = 0%)
print(empathy.get_current_level())  # 1

# Build trust through successful interactions
for _ in range(10):
    response = empathy.interact(user_id="user_123", user_input="...")
    empathy.record_success(success=True)

print(empathy.get_current_level())  # 3 or 4 (depending on trust)
print(f"Trust: {empathy.get_trust_level():.0%}")  # ~50%
```

**Trust Dynamics:**
- Starts at 0%
- Increases on `record_success(True)` by `trust_building_rate` (default: +5%)
- Decreases on `record_failure()` by `trust_erosion_rate` (default: -10%)
- Capped at 100%

## Configuration

See [Configuration API](config.md) for detailed configuration options.

## See Also

- [Configuration Reference](config.md)
- [Core Data Structures](core.md)
- [Pattern Library](pattern-library.md)
- [Simple Chatbot Example](../tutorials/tutorials/examples/simple-chatbot.md)
