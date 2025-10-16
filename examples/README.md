# Empathy Framework - Examples

This directory contains examples demonstrating how to use the Empathy Framework.

## Available Examples

### 1. Quickstart (Introduction)

The [quickstart.py](quickstart.py) example provides a comprehensive introduction to the framework:

```bash
python3 examples/quickstart.py
```

**What it demonstrates:**
- Initializing EmpathyOS
- All five empathy levels (1-5)
- Pattern Library for AI-AI cooperation
- Feedback loop detection
- Trust tracking over time

### 2. Debugging Assistant (Level 3 Proactive)

The [debugging_assistant.py](debugging_assistant.py) shows how to build a proactive debugging AI:

```bash
python3 examples/debugging_assistant.py
```

**What it demonstrates:**
- Level 3 Proactive Empathy in action
- Detecting debugging struggles before being asked
- Confidence-based intervention
- Pattern-based suggestions
- Structural support for stuck developers
- Feedback loop detection (virtuous vs vicious cycles)
- Trust building through helpful assistance

**Key Insight**: Don't wait to be asked - proactively help when the need is clear and confidence is high.

### 3. Bug Prediction (Level 4 Anticipatory)

The [bug_prediction.py](bug_prediction.py) demonstrates predictive bug prevention:

```bash
python3 examples/bug_prediction.py
```

**What it demonstrates:**
- Level 4 Anticipatory Empathy for bug prevention
- Trajectory analysis (where is code heading?)
- Predicting bugs 30 days before they manifest
- Generating preventive actions
- Leverage point analysis for maximum impact
- Evidence-based predictions

**Key Insight**: Like AI Nurse Florence predicting compliance gaps before audits, this predicts bugs before they occur, giving developers time to prevent them.

## Example Progression

The examples are designed to show increasing empathy levels:

| Example | Level | Focus | Key Behavior |
|---------|-------|-------|--------------|
| Quickstart | All (1-5) | Introduction | Overview of all levels |
| Debugging Assistant | Level 3 | Proactive | Act before being asked |
| Bug Prediction | Level 4 | Anticipatory | Predict future needs |

## Running Examples

### Prerequisites

```bash
# Install the framework in development mode
pip3 install -e .

# Or install from PyPI (when published)
pip3 install empathy-framework
```

### Run Examples

```bash
cd empathy-framework

# Run quickstart
python3 examples/quickstart.py

# Run debugging assistant
python3 examples/debugging_assistant.py

# Run bug prediction
python3 examples/bug_prediction.py
```

## Example Output

### Quickstart
Demonstrates progression through all 5 empathy levels:

1. **Level 1 (Reactive)**: Responds only to explicit requests
2. **Level 2 (Guided)**: Asks clarifying questions, collaborative exploration
3. **Level 3 (Proactive)**: Takes initiative on obvious needs
4. **Level 4 (Anticipatory)**: Predicts and prepares for future needs
5. **Level 5 (Systems)**: Builds reusable structures that help at scale

### Debugging Assistant
Shows Level 3 proactive intervention with real debugging scenarios:
- ImportError detection and resolution
- Syntax error assistance
- Detecting developers stuck in frustration loops
- Offering structural support without being asked

### Bug Prediction
Shows Level 4 anticipatory analysis:
- Analyzes code metrics trajectory
- Predicts 4 types of bug risks 30 days ahead
- Generates preventive actions for each risk
- Identifies high-leverage intervention points

## More Examples Coming Soon

- **Compliance anticipation** (Level 4 demonstration from healthcare domain)
- **Multi-agent collaboration** (Level 5 pattern sharing)
- **Custom empathy levels** (Building domain-specific agents)
- **Code review assistant** (Level 3-4 proactive suggestions)

## Contributing Examples

Have a great example? We'd love to include it!

1. Create a new Python file in this directory
2. Follow the quickstart.py structure
3. Add comprehensive comments
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

## Need Help?

- Documentation: https://github.com/Deep-Study-AI/Empathy
- Issues: https://github.com/Deep-Study-AI/Empathy/issues
- Discussions: https://github.com/Deep-Study-AI/Empathy/discussions

## License

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
