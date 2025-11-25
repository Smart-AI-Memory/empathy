# Core

Core data structures and state management for the Empathy Framework.

## Overview

The core module provides fundamental data structures used throughout the framework:

- **`CollaborationState`**: Tracks trust level, current empathy level, and interaction history
- **`EmpathyResponse`**: Container for responses with metadata (level, confidence, predictions)
- **`EmpathyLevel`**: Enumeration of the five empathy levels
- **`InteractionHistory`**: Tracks past interactions for pattern learning

## Class Reference

### CollaborationState

Tracks the state of collaboration between the AI and user.

::: empathy_os.core.CollaborationState
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Attributes:**
- `trust_level` (float): Current trust level (0.0-1.0)
- `current_level` (int): Active empathy level (1-5)
- `target_level` (int): Target empathy level to progress toward
- `interaction_count` (int): Total number of interactions
- `success_count` (int): Number of successful interactions
- `failure_count` (int): Number of failed interactions

**Example:**
```python
from empathy_os.core import CollaborationState

state = CollaborationState(
    user_id="user_123",
    target_level=4
)

# Track interactions
state.record_interaction(success=True)
print(f"Trust: {state.trust_level:.0%}")
print(f"Current level: {state.current_level}")

# Trust increases with successful interactions
for _ in range(10):
    state.record_interaction(success=True)

print(f"New trust: {state.trust_level:.0%}")  # Higher
print(f"New level: {state.current_level}")    # Advanced
```

**Trust-Level Mapping:**
- 0% - 20%: Level 1 (Reactive)
- 20% - 40%: Level 2 (Guided)
- 40% - 60%: Level 3 (Proactive)
- 60% - 80%: Level 4 (Anticipatory)
- 80% - 100%: Level 5 (Transformative)

### EmpathyResponse

Container for AI responses with empathy metadata.

**Note**: EmpathyOS methods currently return dictionaries. A dedicated `EmpathyResponse` class will be added in a future version.

**Attributes:**
- `response` (str): The actual response text
- `level` (int): Empathy level of the response (1-5)
- `confidence` (float): Confidence score (0.0-1.0)
- `predictions` (List[str]): List of predictions (Level 4+)
- `suggestions` (List[str]): List of suggestions (Level 3+)
- `clarifying_questions` (List[str]): Clarifying questions (Level 2+)
- `metadata` (dict): Additional metadata

**Example:**
```python
from empathy_os import EmpathyOS

empathy = EmpathyOS(user_id="user_123", target_level=4)

response = empathy.interact(
    user_id="user_123",
    user_input="I'm deploying to production on Friday afternoon",
    context={"day": "friday", "time": "afternoon"}
)

# Access response data
print(f"Response: {response.response}")
print(f"Level: {response.level}")
print(f"Confidence: {response.confidence:.0%}")

# Level 4 includes predictions
if response.predictions:
    print("\nPredictions:")
    for pred in response.predictions:
        print(f"  • {pred}")

# Level 3+ includes suggestions
if response.suggestions:
    print("\nSuggestions:")
    for suggestion in response.suggestions:
        print(f"  • {suggestion}")
```

**Response by Level:**

**Level 1 (Reactive):**
```python
EmpathyResponse(
    response="Here's how to deploy to production: ...",
    level=1,
    confidence=0.85,
    predictions=[],
    suggestions=[],
    clarifying_questions=[]
)
```

**Level 2 (Guided):**
```python
EmpathyResponse(
    response="Before I help with deployment, I have some questions...",
    level=2,
    confidence=0.80,
    clarifying_questions=[
        "Have you run all tests?",
        "Is there a rollback plan?",
        "Have you notified the team?"
    ]
)
```

**Level 3 (Proactive):**
```python
EmpathyResponse(
    response="Here's the deployment process with some improvements...",
    level=3,
    confidence=0.82,
    suggestions=[
        "Add automated smoke tests",
        "Use blue-green deployment",
        "Set up monitoring alerts"
    ]
)
```

**Level 4 (Anticipatory):**
```python
EmpathyResponse(
    response="I recommend delaying until Monday morning. Here's why...",
    level=4,
    confidence=0.88,
    predictions=[
        "Friday deployments have 3x higher incident rate",
        "Weekend support team is understaffed",
        "This conflicts with scheduled maintenance window"
    ],
    suggestions=[
        "Schedule for Monday 9am",
        "Prepare detailed runbook",
        "Have rollback plan ready"
    ]
)
```

### EmpathyLevel

Enumeration of empathy levels.

::: empathy_os.levels.EmpathyLevel
    options:
      show_root_heading: false
      show_source: true
      heading_level: 4

**Values:**
- `REACTIVE = 1` - Basic Q&A
- `GUIDED = 2` - Asks clarifying questions
- `PROACTIVE = 3` - Suggests improvements
- `ANTICIPATORY = 4` - Predicts problems
- `TRANSFORMATIVE = 5` - Reshapes workflows

**Example:**
```python
from empathy_os.core import EmpathyLevel

# Use in comparisons
if response.level >= EmpathyLevel.ANTICIPATORY:
    print("Predictions available!")
    for pred in response.predictions:
        print(f"  • {pred}")

# Get level name
level_name = EmpathyLevel(response.level).name
print(f"Current level: {level_name}")
```

### InteractionHistory

Tracks interaction history for pattern learning.

**Note**: Interaction history is currently tracked within `CollaborationState`. A dedicated `InteractionHistory` class may be added in a future version.

**Attributes:**
- `interactions` (List[dict]): List of past interactions
- `max_history` (int): Maximum interactions to store (default: 100)

**Example:**
```python
from empathy_os.core import InteractionHistory

history = InteractionHistory(max_history=100)

# Record interaction
history.add_interaction(
    user_input="How do I deploy?",
    response="Here's the deployment process...",
    level=3,
    success=True,
    metadata={"context": "deployment"}
)

# Retrieve recent interactions
recent = history.get_recent(n=10)
for interaction in recent:
    print(f"Input: {interaction['user_input']}")
    print(f"Level: {interaction['level']}")
    print(f"Success: {interaction['success']}")
```

## Usage Patterns

### Trust Management

```python
from empathy_os import EmpathyOS

empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    trust_building_rate=0.05,  # +5% on success
    trust_erosion_rate=0.10     # -10% on failure
)

# Interaction cycle with feedback
response = empathy.interact(
    user_id="user_123",
    user_input="How do I fix this bug?",
    context={}
)

# User found it helpful
if user_satisfied:
    empathy.record_success(success=True)
    # Trust increases by 5%
else:
    empathy.record_failure()
    # Trust decreases by 10%

# Check current state
state = empathy.collaboration_state
print(f"Trust: {state.trust_level:.0%}")
print(f"Level: {state.current_level}")
print(f"Success rate: {state.success_count / state.interaction_count:.0%}")
```

### Level Progression

```python
empathy = EmpathyOS(user_id="user_123", target_level=4)

# Start at Level 1
print(f"Starting level: {empathy.get_current_level()}")  # 1

# Build trust to progress
for i in range(15):
    response = empathy.interact(
        user_id="user_123",
        user_input=f"Question {i}",
        context={}
    )
    empathy.record_success(success=True)

    # Check for level advancement
    if response.level > prev_level:
        print(f"Advanced to Level {response.level}!")

# Should reach Level 3 or 4
print(f"Final level: {empathy.get_current_level()}")
print(f"Final trust: {empathy.get_trust_level():.0%}")
```

### Response Handling

```python
response = empathy.interact(
    user_id="user_123",
    user_input="I need to refactor this code",
    context={"task": "refactoring"}
)

# Handle by level
if response.level == 1:
    # Basic response
    print(response.response)

elif response.level == 2:
    # Show clarifying questions
    print(response.response)
    if response.clarifying_questions:
        print("\nQuestions:")
        for q in response.clarifying_questions:
            print(f"  ? {q}")

elif response.level == 3:
    # Show suggestions
    print(response.response)
    if response.suggestions:
        print("\nSuggestions:")
        for s in response.suggestions:
            print(f"  💡 {s}")

elif response.level >= 4:
    # Show predictions and suggestions
    print(response.response)

    if response.predictions:
        print("\n🔮 Predictions:")
        for p in response.predictions:
            print(f"  • {p}")

    if response.suggestions:
        print("\n💡 Suggestions:")
        for s in response.suggestions:
            print(f"  • {s}")
```

## See Also

- [EmpathyOS API](empathy-os.md)
- [Configuration API](config.md)
- [Pattern Library](pattern-library.md)
- [Simple Chatbot Example](../examples/simple-chatbot.md)
