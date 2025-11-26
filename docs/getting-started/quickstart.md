# Quick Start

Get up and running with Empathy Framework in 5 minutes!

## Step 1: Install

```bash
pip install empathy-framework
```

## Step 2: Create Your First Chatbot

Create a file `my_first_bot.py`:

```python
from empathy_os import EmpathyOS

# Create Level 3 (Proactive) chatbot
empathy = EmpathyOS(
    user_id="user_123",
    target_level=3,
    confidence_threshold=0.70
)

# Interact
response = empathy.interact(
    user_id="user_123",
    user_input="How do I fix this bug in Python?",
    context={}
)

print(f"Response: {response.response}")
print(f"Empathy Level: {response.level}")
print(f"Confidence: {response.confidence:.0%}")
```

## Step 3: Run It

```bash
python my_first_bot.py
```

## What's Next?

- **[Simple Chatbot Tutorial](../examples/simple-chatbot.md)**: Learn all 5 empathy levels
- **[Configuration Guide](configuration.md)**: Customize your bot
- **[Examples](../examples/simple-chatbot.md)**: See more advanced use cases
