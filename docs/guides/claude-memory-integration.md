# Claude Memory Integration Guide

## 1. Overview

### Purpose

The Claude Memory Integration system within `empathy_llm_toolkit` provides hierarchical memory loading capabilities that enable AI systems to maintain context across sessions. The `test_memory_integration.py` script validates the core functionality.

### Key Features

| Feature | Description |
|---------|-------------|
| **Hierarchical memory loading** | Loads memory from Enterprise, User, and Project levels in priority order |
| **Import directive support** | The `@import` mechanism for modular memory file inclusion |
| **EmpathyLLM integration** | Memory content integrates with LLM system prompt generation |
| **Memory cache management** | Caching behavior and memory reloading functionality |

## 2. Setup and Requirements

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.10+ | Required for compatibility |
| `empathy_llm_toolkit` | Latest | Core package containing Claude Memory functionality |
| Write access | - | Required for `.claude/` directory |

### Installation

```bash
pip install empathy_llm_toolkit
```

### Directory Structure

The system expects and creates the following directory structure:

```
project_root/
├── .claude/
│   ├── CLAUDE.md              # Main project memory file
│   ├── python-standards.md    # Example imported memory file
│   └── [other memory files]   # Additional modular memory files
└── your_project_files/
```

### Recommended Environment Setup

1. **Create a virtual environment:**

   ```bash
   python -m venv claude-memory-env
   source claude-memory-env/bin/activate  # Linux/macOS
   # or
   claude-memory-env\Scripts\activate     # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install empathy_llm_toolkit
   ```

3. **Verify installation:**

   ```python
   from empathy_llm_toolkit.claude_memory import ClaudeMemoryLoader
   print("Installation successful!")
   ```

## 3. Basic Memory Loading

### Purpose

Load project memory from the `.claude/CLAUDE.md` file and retrieve content for use in AI prompts.

### Usage

```python
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig, ClaudeMemoryLoader

# Initialize configuration and loader
config = ClaudeMemoryConfig(enabled=True)
loader = ClaudeMemoryLoader(config)

# Load memory from the current directory
memory = loader.load_all_memory(".")
```

### Verification

```python
# Verification checks
print(f"Memory loaded: {len(memory)} chars")
print(f"Contains PROJECT marker: {'PROJECT Level' in memory}")
```

### Expected Output

```
Memory loaded: [X] chars
Contains PROJECT marker: True
```

## 4. Import Directive

### Overview

The `@import` directive enables modular memory file organization by allowing one memory file to include content from another.

### Benefits

- **Modular memory structure:** Break large memory files into focused, manageable components
- **Reusable memory modules:** Share common standards or configurations across projects
- **Dynamic content inclusion:** Import files are processed during memory loading

### Syntax

```markdown
@./relative/path/to/file.md
```

### Example Implementation

#### Step 1: Create a Modular Standards File

Create `.claude/python-standards.md`:

```markdown
# Python Coding Standards

- Use type hints
- Follow PEP 8
- Write docstrings
- Target 90%+ test coverage
```

#### Step 2: Reference in Main Memory File

In `.claude/CLAUDE.md`:

```markdown
# Project Memory

## Framework
This is the Empathy Framework v1.8.0-alpha

@./python-standards.md

## Additional Notes
Memory integration test
```

#### Step 3: Verify Import Resolution

```python
from empathy_llm_toolkit.claude_memory import ClaudeMemoryConfig, ClaudeMemoryLoader

config = ClaudeMemoryConfig(enabled=True)
loader = ClaudeMemoryLoader(config)
memory = loader.load_all_memory(".")

# Check that imported content is included
assert "Use type hints" in memory
assert "Follow PEP 8" in memory
```

## 5. EmpathyLLM Integration

### Purpose

Demonstrate how loaded memory integrates with the EmpathyLLM class for generating context-aware system prompts.

### Usage

```python
from empathy_llm_toolkit import EmpathyLLM

# Create an EmpathyLLM instance
llm = EmpathyLLM()

# Get the system prompt (includes loaded memory)
system_prompt = llm.get_system_prompt()

# Verify memory content is included
print(f"System prompt length: {len(system_prompt)} chars")
```

### Key Integration Points

| Component | Role |
|-----------|------|
| `ClaudeMemoryLoader` | Loads and processes memory files |
| `EmpathyLLM` | Integrates memory into system prompts |
| Memory cache | Optimizes repeated memory access |

## 6. Configuration Options

### ClaudeMemoryConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | bool | `True` | Enable/disable memory loading |
| `project_root` | str | `"."` | Root directory for memory files |
| `cache_enabled` | bool | `True` | Enable memory caching |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CLAUDE_MEMORY_ENABLED` | Override config enabled setting |
| `CLAUDE_MEMORY_PATH` | Custom memory directory path |

## 7. Error Handling and Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Memory not loading | Missing `.claude/CLAUDE.md` | Create the file with initial content |
| Import not resolved | Incorrect path in `@import` | Use relative paths from `.claude/` directory |
| Empty memory content | File exists but is empty | Add content to memory file |

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from empathy_llm_toolkit.claude_memory import ClaudeMemoryLoader
# Loader will now output debug information
```

## 8. Running Tests

### Execute the Test Suite

```bash
python test_memory_integration.py
```

### Expected Test Output

```
============================================================
TEST 1: Basic Project Memory Loading
============================================================
Memory loaded: [X] chars
Contains PROJECT marker: True

============================================================
TEST 2: Import Directive Processing
============================================================
Import resolved successfully
Contains imported content: True

============================================================
TEST 3: EmpathyLLM Integration
============================================================
System prompt generated: [X] chars
Memory integrated: True

============================================================
ALL TESTS PASSED
============================================================
```

## See Also

- [Multi-Model Workflows Guide](multi-model-workflows.md)
- [Software Development Wizards](software-development-wizards.md)
- [API Reference: ClaudeMemoryLoader](/api-reference/claude-memory/)
