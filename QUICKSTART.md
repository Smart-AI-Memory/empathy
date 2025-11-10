# Empathy Framework - Quick Start Guide

**Get up and running in 5 minutes**

---

## What is Empathy Framework?

Empathy Framework is a five-level maturity model for AI-human collaboration:
- **Level 1: Reactive** - Respond when asked
- **Level 2: Guided** - Collaborate with clarifying questions
- **Level 3: Proactive** - Act before being asked
- **Level 4: Anticipatory** - Predict future needs
- **Level 5: Systems** - Build structures that prevent entire problem classes

---

## Installation

### Prerequisites

- **Python 3.9+** (3.10+ recommended)
- **API Key** for your LLM provider (optional for core framework)

### Install from Source

```bash
# Clone the repository (or download your licensed copy)
git clone https://github.com/Deep-Study-AI/empathy.git
cd empathy

# Install with pip
pip install -e .

# Or install with all optional dependencies
pip install -e ".[dev,examples]"
```

### Verify Installation

```bash
python -c "from empathy_os import EmpathyOS; print('✓ Empathy Framework installed')"
```

---

## Quick Start Examples

### Example 1: Simplest Usage (No Custom Code)

The easiest way to use Empathy Framework - just interact with it!

```python
import asyncio
import os
from empathy_llm_toolkit.core import EmpathyLLM

async def quick_demo():
    # Create an instance (uses Claude by default)
    llm = EmpathyLLM(
        provider="anthropic",  # or "openai", "local"
        target_level=4,        # Level 4 Anticipatory
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # Just interact - it handles the rest!
    response = await llm.interact(
        user_id="me",
        user_input="Help me build a web API"
    )

    print(f"Assistant: {response['content']}")
    print(f"Level Used: {response['level_used']}")

# Run it
asyncio.run(quick_demo())
```

**Set your API key first:**
```bash
export ANTHROPIC_API_KEY="your-key-here"
# or
export OPENAI_API_KEY="your-key-here"
```

**Run the example:**
```bash
python examples/simple_usage.py
```

---

### Example 2: Understanding the Five Levels

See all five empathy levels in action:

```python
from empathy_os import (
    EmpathyOS,
    Level1Reactive,
    Level2Guided,
    Level3Proactive,
    Level4Anticipatory,
    Level5Systems
)

# Initialize EmpathyOS
empathy = EmpathyOS(
    user_id="quickstart_user",
    target_level=4,
    confidence_threshold=0.75
)

# Level 1: Reactive (waits for request)
level1 = Level1Reactive()
response = level1.respond({"request": "status"})
print(f"Level 1: {response['action']}")  # Provides status

# Level 2: Guided (asks clarifying questions)
level2 = Level2Guided()
response = level2.respond({"request": "improve system"})
print(f"Level 2: {response['action']}")  # Asks for clarification

# Level 3: Proactive (acts before being asked)
level3 = Level3Proactive()
response = level3.respond({"observed_need": "failing_tests"})
print(f"Level 3: {response['action']}")  # Fixes tests proactively

# Level 4: Anticipatory (predicts future needs)
level4 = Level4Anticipatory()
response = level4.respond({
    "current_state": {"compliance": 0.7},
    "trajectory": "declining"
})
print(f"Level 4: {response['predicted_needs']}")  # Predicts problems

# Level 5: Systems (prevents problem classes)
level5 = Level5Systems()
response = level5.respond({
    "problem_class": "documentation_burden",
    "instances": 18
})
print(f"Level 5: {response['system_created']}")  # Builds structure
```

**Run the full demo:**
```bash
python examples/quickstart.py
```

---

### Example 3: Multiple LLM Providers

Switch between different AI providers based on your needs:

```python
from empathy_llm_toolkit.core import EmpathyLLM

# Use Claude for complex reasoning (Level 4 Anticipatory)
claude = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Use GPT-4 for fast responses (Level 3 Proactive)
gpt4 = EmpathyLLM(
    provider="openai",
    target_level=3,
    api_key=os.getenv("OPENAI_API_KEY")
)

# Use local Ollama for privacy (Level 2 Guided)
local = EmpathyLLM(
    provider="local",
    target_level=2,
    model="llama2",
    endpoint="http://localhost:11434"
)
```

**Run the multi-LLM demo:**
```bash
python examples/multi_llm_usage.py
```

---

## Core Concepts

### 1. Empathy Levels

Each level builds on the previous:

| Level | Name | Description | Use Case |
|-------|------|-------------|----------|
| **1** | Reactive | Responds when asked | Basic Q&A, help requests |
| **2** | Guided | Asks clarifying questions | Ambiguous requirements |
| **3** | Proactive | Acts before being asked | Automated maintenance |
| **4** | Anticipatory | Predicts future needs | Prevent problems |
| **5** | Systems | Builds prevention structures | Scale solutions |

### 2. Trust Building

The framework tracks trust between human and AI:

```python
empathy = EmpathyOS(user_id="developer_123")

# Trust starts at 0.5 (neutral)
print(empathy.collaboration_state.trust_level)  # 0.5

# Successful interactions increase trust
empathy.collaboration_state.update_trust("success")
print(empathy.collaboration_state.trust_level)  # 0.6

# Higher trust = more proactive behavior
```

### 3. Pattern Library (Level 5)

AI agents share patterns for better collaboration:

```python
from empathy_os import PatternLibrary, Pattern

library = PatternLibrary()

# Agent 1 contributes a pattern
pattern = Pattern(
    id="pat_001",
    agent_id="agent_1",
    pattern_type="sequential",
    name="Post-deployment docs",
    description="Users need help after deployments",
    confidence=0.85
)
library.contribute_pattern("agent_1", pattern)

# Agent 2 queries for relevant patterns
matches = library.query_patterns(
    agent_id="agent_2",
    context={"recent_event": "deployment"},
    min_confidence=0.7
)

# Use the pattern and record outcome
library.record_pattern_outcome("pat_001", success=True)
```

---

## Project Structure

```
empathy-framework/
├── src/empathy_os/          # Core framework
│   ├── core.py              # EmpathyOS main class
│   ├── levels.py            # Five empathy levels
│   ├── pattern_library.py   # Pattern sharing (Level 5)
│   ├── feedback_loops.py    # System dynamics
│   └── plugins/             # Plugin architecture
├── empathy_llm_toolkit/     # LLM integration layer
│   ├── core.py              # EmpathyLLM wrapper
│   └── providers.py         # Claude, GPT-4, Ollama, etc.
├── examples/                # Runnable examples
│   ├── simple_usage.py      # Easiest starting point
│   ├── quickstart.py        # Comprehensive demo
│   └── multi_llm_usage.py   # Multiple providers
├── coach_wizards/           # Software development wizards
├── empathy_software_plugin/ # Software domain plugin
└── empathy_healthcare_plugin/ # Healthcare domain plugin
```

---

## Common Use Cases

### 1. Code Review Assistant

```python
from empathy_llm_toolkit.core import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", target_level=3)

response = await llm.interact(
    user_id="developer",
    user_input="Review this code for issues",
    context={"code": your_code_here}
)
```

### 2. Bug Prediction

```python
from empathy_llm_toolkit.core import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", target_level=4)

response = await llm.interact(
    user_id="qa_team",
    user_input="Predict bugs in next release",
    context={"codebase": recent_changes}
)
```

### 3. Documentation Generation

```python
from empathy_llm_toolkit.core import EmpathyLLM

llm = EmpathyLLM(provider="openai", target_level=2)

response = await llm.interact(
    user_id="tech_writer",
    user_input="Generate API documentation",
    context={"code": api_endpoints}
)
```

---

## Configuration

### Environment Variables

```bash
# LLM Provider API Keys
export ANTHROPIC_API_KEY="your-anthropic-key"
export OPENAI_API_KEY="your-openai-key"

# Framework Settings (optional)
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75
export EMPATHY_LOG_LEVEL=INFO
```

### Configuration File

Create `.env` in your project root:

```env
# LLM Provider
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here

# Framework Settings
EMPATHY_TARGET_LEVEL=4
EMPATHY_CONFIDENCE_THRESHOLD=0.75
EMPATHY_LOG_LEVEL=INFO
```

---

## Troubleshooting

### Issue: Import Error

**Error:**
```
ImportError: No module named 'empathy_os'
```

**Solution:**
```bash
# Make sure you installed the package
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/empathy-framework"
```

### Issue: API Key Not Found

**Error:**
```
ValueError: API key required for Anthropic provider
```

**Solution:**
```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Or pass it directly
llm = EmpathyLLM(
    provider="anthropic",
    api_key="your-key-here"
)
```

### Issue: Module Dependencies

**Error:**
```
ModuleNotFoundError: No module named 'langchain'
```

**Solution:**
```bash
# Install with all dependencies
pip install -e ".[dev,examples]"

# Or install specific dependencies
pip install langchain langchain-core langgraph
```

---

## Next Steps

### 1. Explore Examples

```bash
# Run all examples
python examples/simple_usage.py
python examples/quickstart.py
python examples/multi_llm_usage.py
python examples/security_demo.py
python examples/performance_demo.py
```

### 2. Read Documentation

- **[README.md](README.md)** - Full project overview
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Framework architecture
- **[docs/LEVELS.md](docs/LEVELS.md)** - Detailed level explanations
- **[CONTRIBUTING.md](CONTRIBUTING.md)** - Contributing guidelines

### 3. Try Advanced Features

- Build custom wizards
- Create domain-specific plugins
- Integrate with your CI/CD pipeline
- Use pattern library for AI-AI cooperation

### 4. Join the Community

- **GitHub**: https://github.com/Deep-Study-AI/empathy
- **Issues**: Report bugs or request features
- **Discussions**: Ask questions and share patterns

---

## Getting Help

### Documentation

- Full documentation: `docs/` directory
- API reference: `docs/API.md`
- Examples: `examples/` directory

### Support

- **Community Support** (Free tier): GitHub Issues
- **Email Support** (Commercial license): patrick.roebuck1955@gmail.com
- **Documentation**: https://github.com/Smart-AI-Memory/empathy

---

## License

- **Core Framework**: Apache 2.0 (open source)
- **Complete Bundle**: Commercial license available
- **Pricing**: $99/developer/year (Free for students, educators, small teams ≤5 employees)

See [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md) for details.

---

## Quick Reference

### Installation Commands

```bash
pip install -e .                    # Core framework
pip install -e ".[dev]"            # With dev tools
pip install -e ".[examples]"       # With example dependencies
pip install -e ".[dev,examples]"   # Everything
```

### Example Commands

```bash
python examples/simple_usage.py      # Easiest start
python examples/quickstart.py        # Full demo
python examples/multi_llm_usage.py   # Multiple providers
```

### Import Statements

```python
# Core framework
from empathy_os import EmpathyOS, Level1Reactive, Level2Guided

# LLM toolkit (easiest)
from empathy_llm_toolkit.core import EmpathyLLM

# Advanced features
from empathy_os import PatternLibrary, FeedbackLoopDetector
```

---

**Ready to get started? Run your first example:**

```bash
export ANTHROPIC_API_KEY="your-key"
python examples/simple_usage.py
```

**Questions?** Check the [full documentation](docs/) or [file an issue](https://github.com/Deep-Study-AI/empathy/issues).
