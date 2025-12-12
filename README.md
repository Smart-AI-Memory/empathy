# Empathy Framework

**The AI collaboration framework that predicts problems before they happen.**

[![PyPI](https://img.shields.io/pypi/v/empathy-framework)](https://pypi.org/project/empathy-framework/)
[![Tests](https://img.shields.io/badge/tests-2%2C040%2B%20passing-brightgreen)](https://github.com/Smart-AI-Memory/empathy/actions)
[![Coverage](https://codecov.io/gh/Smart-AI-Memory/empathy/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy)
[![License](https://img.shields.io/badge/license-Fair%20Source%200.9-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)
[![GitHub stars](https://img.shields.io/github/stars/Smart-AI-Memory/empathy?style=social)](https://github.com/Smart-AI-Memory/empathy)

```bash
pip install empathy-framework
empathy-memory serve
```

## Why Empathy?

### Memory That Persists
- **Dual-layer architecture** — Redis for millisecond short-term ops, pattern storage for long-term knowledge
- **AI that learns across sessions** — Patterns discovered today inform decisions tomorrow
- **Cross-team knowledge sharing** — What one agent learns, all agents can use

### Enterprise-Ready
- **Your data stays local** — Nothing leaves your infrastructure
- **Compliance built-in** — HIPAA, GDPR, SOC2 patterns included
- **Automatic documentation** — AI-first docs that serve humans and machines

### Anticipatory Intelligence
- **Predicts 30-90 days ahead** — Security vulnerabilities, performance degradation, compliance gaps
- **Prevents, not reacts** — Eliminate entire categories of problems before they become urgent
- **3-4x productivity gains** — Not 20% faster; whole workflows disappear

### Build Better Agents
- **Agent toolkit** — Build custom agents that inherit memory, trust, and anticipation
- **30+ production wizards** — Security, performance, testing, docs—use or extend
- **5-level progression built-in** — Your agents evolve from reactive to anticipatory automatically

### Human↔AI & AI↔AI Orchestration
- **Empathy OS** — Manages trust, feedback loops, and collaboration state
- **Multi-agent coordination** — Specialized agents working in concert
- **Conflict resolution** — Principled negotiation when agents disagree

### Performance & Cost
- **40-60% LLM cost reduction** — Smart routing: cheap models detect, best models decide
- **Sub-millisecond coordination** — Redis-backed real-time signaling between agents
- **Works with any LLM** — Claude, GPT-4, Ollama, or your own

## Quick Example

```python
from empathy_os import EmpathyOS

os = EmpathyOS()

# Analyze code for current AND future issues
result = await os.collaborate(
    "Review this deployment pipeline for problems",
    context={"code": pipeline_code, "team_size": 10}
)

# Get predictions, not just analysis
print(result.current_issues)      # What's wrong now
print(result.predicted_issues)    # What will break in 30-90 days
print(result.prevention_steps)    # How to prevent it
```

## The 5 Levels of AI Empathy

| Level | Name | Behavior | Example |
|-------|------|----------|---------|
| 1 | Reactive | Responds when asked | "Here's the data you requested" |
| 2 | Guided | Asks clarifying questions | "What format do you need?" |
| 3 | Proactive | Notices patterns | "I pre-fetched what you usually need" |
| **4** | **Anticipatory** | **Predicts future needs** | **"This query will timeout at 10k users"** |
| 5 | Transformative | Builds preventing structures | "Here's a framework for all future cases" |

**Empathy operates at Level 4** - predicting problems before they manifest.

## Comparison

| | Empathy | SonarQube | GitHub Copilot |
|---|---------|-----------|----------------|
| **Predicts future issues** | ✅ 30-90 days ahead | ❌ | ❌ |
| **Persistent memory** | ✅ Redis + patterns | ❌ | ❌ |
| **Cross-domain learning** | ✅ Healthcare → Software | ❌ | ❌ |
| **Multi-agent orchestration** | ✅ Built-in | ❌ | ❌ |
| **Source available** | ✅ Fair Source 0.9 | ❌ | ❌ |
| **Data stays local** | ✅ Your infrastructure | ❌ Cloud | ❌ Cloud |
| **Free for small teams** | ✅ ≤5 employees | ❌ | ❌ |

## Get Involved

**⭐ [Star this repo](https://github.com/Smart-AI-Memory/empathy)** if you find it useful

**💬 [Join Discussions](https://github.com/Smart-AI-Memory/empathy/discussions)** - Questions, ideas, show what you built

**📖 [Read the Book](https://smartaimemory.com/book)** - Deep dive into the philosophy and implementation

**📚 [Full Documentation](docs/)** - API reference, examples, guides

## Install Options

```bash
# Basic
pip install empathy-framework

# With all features (recommended)
pip install empathy-framework[full]

# Development
git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy && pip install -e .[dev]
```

## What's Included

- **Empathy OS** — Core engine for managing human↔AI and AI↔AI collaboration
- **Memory System** — Redis short-term + encrypted long-term pattern storage
- **30+ Production Wizards** — Security, performance, testing, docs, accessibility, compliance
- **Healthcare Suite** — SBAR, SOAP notes, clinical protocols (HIPAA compliant)
- **LLM Toolkit** — Works with Claude, GPT-4, Ollama; smart model routing
- **Memory Control Panel** — CLI (`empathy-memory`) and REST API for managing everything
- **IDE Plugins** — VS Code extension for visual memory management

## Memory Control Panel

Manage AI memory with a simple CLI:

```bash
# Start everything (Redis + API server)
empathy-memory serve

# Check system status
empathy-memory status

# View statistics
empathy-memory stats

# Run health check
empathy-memory health

# List stored patterns
empathy-memory patterns
```

The API server runs at `http://localhost:8765` with endpoints for status, stats, patterns, and Redis control.

**VS Code Extension:** A visual panel for monitoring memory is available in `vscode-memory-panel/`.

## License

**Fair Source License 0.9** - Free for students, educators, and teams ≤5 employees. Commercial license ($99/dev/year) for larger organizations. [Details →](LICENSE)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Documentation](docs/) · [Examples](examples/) · [Issues](https://github.com/Smart-AI-Memory/empathy/issues)
