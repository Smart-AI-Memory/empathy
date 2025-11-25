# Example: Simple Chatbot with Empathy Levels

**Difficulty**: Beginner
**Time**: 10 minutes
**Empathy Levels**: 1-4

---

## Overview

This example shows how to build a simple chatbot that progressively gains empathy, moving from basic reactive responses (Level 1) to anticipatory intelligence (Level 4).

**What you'll learn**:
- Basic EmpathyOS setup
- How empathy levels change behavior
- Trust building through interactions
- Pattern recognition across conversations

---

## Installation

```bash
pip install empathy-framework
```

---

## Level 1: Reactive Chatbot

The simplest chatbot - only responds when asked, no context awareness.

```python
from empathy_os import EmpathyOS

# Create Level 1 chatbot (reactive)
chatbot = EmpathyOS(
    user_id="user_123",
    target_level=1,  # Reactive only
    confidence_threshold=0.5
)

# User interaction
response = chatbot.interact(
    user_id="user_123",
    user_input="How do I fix a bug in Python?",
    context={}
)

print(response.response)
# Output: "To fix a bug in Python, you can..."
# (No follow-up questions, no context awareness)
```

**Characteristics**:
- ✅ Answers direct questions
- ❌ No clarifying questions
- ❌ No pattern recognition
- ❌ No proactive suggestions

---

## Level 2: Guided Chatbot

Asks clarifying questions to understand context better.

```python
from empathy_os import EmpathyOS

# Create Level 2 chatbot (guided)
chatbot = EmpathyOS(
    user_id="user_123",
    target_level=2,  # Guided with clarification
    confidence_threshold=0.6
)

# User interaction
response = chatbot.interact(
    user_id="user_123",
    user_input="How do I fix a bug in Python?",
    context={}
)

print(response.response)
# Output: "I can help with that! A few clarifying questions:
#          1. What type of bug are you encountering? (syntax, logic, runtime)
#          2. Are you seeing an error message?
#          3. What framework or libraries are you using?"
```

**Characteristics**:
- ✅ Asks clarifying questions
- ✅ Seeks context before answering
- ❌ No pattern recognition
- ❌ No proactive suggestions

---

## Level 3: Proactive Chatbot

Notices patterns and offers improvements without being asked.

```python
from empathy_os import EmpathyOS

# Create Level 3 chatbot (proactive)
chatbot = EmpathyOS(
    user_id="user_123",
    target_level=3,  # Proactive with pattern recognition
    confidence_threshold=0.7,
    persistence_enabled=True  # Required for pattern tracking
)

# Simulate multiple interactions over time
interactions = [
    "How do I fix this IndexError?",
    "Getting a KeyError in my dictionary",
    "Another IndexError, this time in a list comprehension"
]

for user_input in interactions:
    response = chatbot.interact(
        user_id="user_123",
        user_input=user_input,
        context={}
    )
    print(f"User: {user_input}")
    print(f"Bot: {response.response}\n")

# After 3rd interaction:
# Bot: "I notice you're getting frequent IndexError and KeyError exceptions.
#       These are often caused by not validating data structures before access.
#       Would you like me to show you defensive programming patterns to prevent these?"
```

**Characteristics**:
- ✅ Recognizes patterns across conversations
- ✅ Offers improvements proactively
- ✅ Builds context over time
- ❌ No future predictions

---

## Level 4: Anticipatory Chatbot

Predicts problems before they happen and offers preventative solutions.

```python
from empathy_os import EmpathyOS
import asyncio

# Create Level 4 chatbot (anticipatory)
chatbot = EmpathyOS(
    user_id="user_123",
    target_level=4,  # Anticipatory with predictions
    confidence_threshold=0.75,
    persistence_enabled=True
)

# Simulate development pattern over multiple days
async def simulate_development_week():
    # Monday: User starts new feature
    response = chatbot.interact(
        user_id="user_123",
        user_input="Starting work on user authentication feature",
        context={"day": "Monday", "feature": "auth"}
    )
    print(f"Monday: {response.response}\n")

    # Tuesday: User debugging
    response = chatbot.interact(
        user_id="user_123",
        user_input="Debugging JWT token validation issues",
        context={"day": "Tuesday", "feature": "auth"}
    )
    print(f"Tuesday: {response.response}\n")

    # Wednesday: User fixing edge cases
    response = chatbot.interact(
        user_id="user_123",
        user_input="Handling token refresh edge cases",
        context={"day": "Wednesday", "feature": "auth"}
    )
    print(f"Wednesday: {response.response}\n")

    # Thursday: Before user asks, chatbot anticipates
    response = chatbot.interact(
        user_id="user_123",
        user_input="Planning to deploy authentication feature",
        context={"day": "Thursday", "feature": "auth"}
    )
    print(f"Thursday: {response.response}")
    # Output: "🔮 ANTICIPATORY ALERT:
    #          Based on your pattern over the last 3 days, I predict you'll encounter
    #          these issues in production if not addressed now:
    #
    #          1. Token expiration handling (you debugged this on Tuesday)
    #          2. Refresh token edge cases (worked on Wednesday)
    #          3. NEW PREDICTION: Concurrent token refresh race conditions
    #             (Common issue when auth features reach production)
    #
    #          Would you like me to generate test cases for these scenarios before deployment?"

asyncio.run(simulate_development_week())
```

**Characteristics**:
- ✅ Predicts future problems
- ✅ Offers preventative solutions
- ✅ Learns from multi-day patterns
- ✅ Anticipates needs before user asks

---

## Trust Building

As the chatbot provides helpful responses, trust increases, enabling higher empathy levels.

```python
from empathy_os import EmpathyOS

chatbot = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75
)

# Check initial trust
print(f"Initial trust: {chatbot.collaboration_state.trust_level:.2f}")
# Output: 0.00 (no trust yet)

# Successful interaction #1
response = chatbot.interact(
    user_id="user_123",
    user_input="Help me debug this error",
    context={}
)
chatbot.record_success(success=True)  # User found response helpful

print(f"Trust after success: {chatbot.collaboration_state.trust_level:.2f}")
# Output: 0.05 (small increase)

# After 20 successful interactions
for _ in range(19):
    response = chatbot.interact(user_id="user_123", user_input="...", context={})
    chatbot.record_success(success=True)

print(f"Trust after 20 successes: {chatbot.collaboration_state.trust_level:.2f}")
# Output: 0.65 (high trust)

# Now Level 4 predictions are trusted
response = chatbot.interact(
    user_id="user_123",
    user_input="About to merge this PR",
    context={"feature": "new_api"}
)

# With high trust, chatbot can make bolder predictions:
# "🔮 Based on your recent work, I predict this merge will cause:
#     1. Breaking changes in the mobile app (uses old API contract)
#     2. Database migration required (you changed schema yesterday)
#     Confidence: 87%
#
#     Recommendation: Deploy API changes behind feature flag first."
```

---

## Pattern Library

The chatbot learns and reuses patterns across conversations.

```python
from empathy_os import EmpathyOS
from empathy_os.persistence import PatternPersistence

chatbot = EmpathyOS(
    user_id="user_123",
    target_level=3,
    persistence_enabled=True,
    persistence_backend="sqlite"  # Default
)

# First time: Learn a debugging pattern
response = chatbot.interact(
    user_id="user_123",
    user_input="How do I debug a memory leak in Python?",
    context={}
)

# Response includes solution
# Chatbot saves pattern: "debugging_memory_leak"

# Week later: Similar issue
response = chatbot.interact(
    user_id="user_123",
    user_input="My Python process is using too much memory",
    context={}
)

# Response:
# "I recall we debugged a memory leak before using these steps:
#  1. Use memory_profiler to identify hotspots
#  2. Check for circular references
#  3. Use objgraph to visualize object retention
#
#  This pattern worked well last time (confidence: 0.85).
#  Would you like me to apply it here?"

# Inspect learned patterns
persistence = PatternPersistence(db_path=".empathy/patterns.db")
patterns = persistence.list_patterns(user_id="user_123")

for pattern in patterns:
    print(f"Pattern: {pattern.name}")
    print(f"  Used: {pattern.usage_count} times")
    print(f"  Confidence: {pattern.confidence:.2f}")
    print(f"  Last used: {pattern.last_used}")
```

---

## Configuration Options

Customize chatbot behavior with configuration files.

**empathy.config.yml**:
```yaml
# Core settings
user_id: "user_123"
target_level: 4
confidence_threshold: 0.75

# Trust settings
trust_building_rate: 0.05  # How fast trust increases
trust_erosion_rate: 0.10   # How fast trust decreases on failures

# Persistence
persistence_enabled: true
persistence_backend: "sqlite"
persistence_path: ".empathy"

# Metrics
metrics_enabled: true
metrics_path: ".empathy/metrics"

# Logging
log_level: "INFO"
log_format: "json"  # or "text"
```

**Load configuration**:
```python
from empathy_os import load_config

# Load from file
config = load_config(filepath="empathy.config.yml")

# Create chatbot with config
chatbot = EmpathyOS.from_config(config)
```

---

## Complete Example: Multi-Session Chatbot

```python
#!/usr/bin/env python3
"""
Complete chatbot example showing progression from Level 1 to Level 4
across multiple sessions.
"""

from empathy_os import EmpathyOS, load_config
import time

def run_chatbot():
    # Load configuration
    config = load_config(filepath="empathy.config.yml")

    # Create chatbot
    chatbot = EmpathyOS.from_config(config)

    print(f"🤖 Empathy Chatbot (Target Level: {config.target_level})")
    print(f"   Trust: {chatbot.collaboration_state.trust_level:.2f}")
    print(f"   Current Level: {chatbot.collaboration_state.current_level}")
    print()

    # Interactive loop
    while True:
        try:
            user_input = input("You: ").strip()

            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("👋 Goodbye!")
                break

            if not user_input:
                continue

            # Get response
            response = chatbot.interact(
                user_id=config.user_id,
                user_input=user_input,
                context={"timestamp": time.time()}
            )

            # Display response with empathy level indicator
            level_indicator = ["❌", "🔵", "🟢", "🟡", "🔮"][response.level]
            print(f"Bot {level_indicator} [L{response.level}]: {response.response}")

            # Show predictions if Level 4
            if response.predictions:
                print("\n🔮 Predictions:")
                for pred in response.predictions:
                    print(f"   • {pred}")

            print()

            # Ask for feedback
            feedback = input("Was this helpful? (y/n): ").strip().lower()
            chatbot.record_success(success=(feedback == 'y'))

            # Show trust update
            trust = chatbot.collaboration_state.trust_level
            print(f"   Trust: {trust:.2f} | Level: {chatbot.collaboration_state.current_level}")
            print()

        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_chatbot()
```

---

## Next Steps

**Enhance your chatbot**:
1. **Add domain knowledge**: Integrate with your codebase, documentation, or APIs
2. **Multi-user**: Support team collaboration with shared pattern library
3. **Custom protocols**: Define domain-specific patterns (see healthcare example)
4. **Webhooks**: Integrate with Slack, GitHub, JIRA
5. **Advanced features**: Multi-agent coordination, adaptive learning

**Related examples**:
- [Code Review Assistant](code-review-assistant.md) - Level 3-4 for PR reviews
- [Clinical Protocol Monitor](clinical-protocol-monitor.md) - Healthcare SBAR
- [Patient Handoff Predictor](patient-handoff-predictor.md) - Level 4 healthcare

---

## Troubleshooting

**"ModuleNotFoundError: No module named 'empathy_os'"**
- Run: `pip install empathy-framework`

**Chatbot stuck at Level 1**
- Increase trust by providing positive feedback: `chatbot.record_success(True)`
- Lower `confidence_threshold` in config (e.g., 0.6 instead of 0.75)

**No patterns being saved**
- Enable persistence: `persistence_enabled: true` in config
- Check database file exists: `.empathy/patterns.db`

**Trust not increasing**
- Call `record_success(True)` after helpful interactions
- Check `trust_building_rate` (default: 0.05)

---

**Need help?** See the [full documentation](https://empathy-framework.readthedocs.io) or [open an issue](https://github.com/Smart-AI-Memory/empathy-framework/issues).
