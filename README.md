# Empathy Framework

**The AI collaboration framework that predicts problems before they happen.**

[![PyPI](https://img.shields.io/pypi/v/empathy-framework)](https://pypi.org/project/empathy-framework/)
[![Tests](https://img.shields.io/badge/tests-2%2C365%20passing-brightgreen)](https://github.com/Smart-AI-Memory/empathy-framework/actions)
[![Coverage](https://img.shields.io/badge/coverage-55%25-yellow)](https://github.com/Smart-AI-Memory/empathy-framework)
[![License](https://img.shields.io/badge/license-Fair%20Source%200.9-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)

```bash
pip install empathy-framework[full]
```

## What's New in v3.0.1

- **XML-Enhanced Prompts** — Structured prompts for consistent, parseable LLM responses
- **Multi-Model Provider System** — Choose Anthropic, OpenAI, Ollama, or Hybrid mode
- **80-96% Cost Savings** — Smart tier routing: cheap models detect, best models decide
- **VSCode Dashboard** — 10 integrated workflows with input history persistence
- **Security Hardening** — Fixed command injection vulnerabilities in VSCode extension
- **Provider Auto-Detection** — Automatically configures based on your API keys

---

## Quick Start (2 Minutes)

### 1. Install

```bash
pip install empathy-framework[full]
```

### 2. Configure Provider

```bash
# Auto-detect your API keys and configure
python -m empathy_os.models.cli provider

# Or set explicitly
python -m empathy_os.models.cli provider --set anthropic
python -m empathy_os.models.cli provider --set hybrid  # Best of all providers
```

### 3. Use It

```python
from empathy_os import EmpathyOS

os = EmpathyOS()
result = await os.collaborate(
    "Review this code for security issues",
    context={"code": your_code}
)

print(result.current_issues)      # What's wrong now
print(result.predicted_issues)    # What will break in 30-90 days
print(result.prevention_steps)    # How to prevent it
```

---

## Why Empathy?

| Feature | Empathy | SonarQube | GitHub Copilot |
|---------|---------|-----------|----------------|
| **Predicts future issues** | 30-90 days ahead | No | No |
| **Persistent memory** | Redis + patterns | No | No |
| **Multi-provider support** | Claude, GPT-4, Ollama | N/A | GPT only |
| **Cost optimization** | 80-96% savings | N/A | No |
| **Your data stays local** | Yes | Cloud | Cloud |
| **Free for small teams** | ≤5 employees | No | No |

---

## Become a Power User

### Level 1: Basic Usage
```bash
pip install empathy-framework
```
- Works out of the box with sensible defaults
- Auto-detects your API keys

### Level 2: Cost Optimization
```bash
# Enable hybrid mode for 80-96% cost savings
python -m empathy_os.models.cli provider --set hybrid
```
| Tier | Model | Use Case | Cost |
|------|-------|----------|------|
| Cheap | GPT-4o-mini / Haiku | Summarization, simple tasks | $0.15-0.25/M |
| Capable | GPT-4o / Sonnet | Bug fixing, code review | $2.50-3.00/M |
| Premium | o1 / Opus | Architecture, complex decisions | $15/M |

### Level 3: Multi-Model Workflows
```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", enable_model_routing=True)

# Automatically routes to appropriate tier
await llm.interact(user_id="dev", user_input="Summarize this", task_type="summarize")     # → Haiku
await llm.interact(user_id="dev", user_input="Fix this bug", task_type="fix_bug")         # → Sonnet
await llm.interact(user_id="dev", user_input="Design system", task_type="coordinate")     # → Opus
```

### Level 4: VSCode Integration
Install the Empathy VSCode extension for:
- **Real-time Dashboard** — Health score, costs, patterns
- **One-Click Workflows** — Research, code review, debugging
- **Visual Cost Tracking** — See savings in real-time
    - See also: `docs/dashboard-costs-by-tier.md` for interpreting the **By tier (7 days)** cost breakdown.

### Level 5: Custom Agents
```python
from empathy_os.agents import AgentFactory

# Create domain-specific agents with inherited memory
security_agent = AgentFactory.create(
    domain="security",
    memory_enabled=True,
    anticipation_level=4
)
```

---

## CLI Reference

### Provider Configuration
```bash
python -m empathy_os.models.cli provider                    # Show current config
python -m empathy_os.models.cli provider --set anthropic    # Single provider
python -m empathy_os.models.cli provider --set hybrid       # Best-of-breed
python -m empathy_os.models.cli provider --interactive      # Setup wizard
python -m empathy_os.models.cli provider -f json            # JSON output
```

### Model Registry
```bash
python -m empathy_os.models.cli registry                    # Show all models
python -m empathy_os.models.cli registry --provider openai  # Filter by provider
python -m empathy_os.models.cli costs --input-tokens 50000  # Estimate costs
```

### Telemetry & Analytics
```bash
python -m empathy_os.models.cli telemetry                   # Summary
python -m empathy_os.models.cli telemetry --costs           # Cost savings report
python -m empathy_os.models.cli telemetry --providers       # Provider usage
python -m empathy_os.models.cli telemetry --fallbacks       # Fallback stats
```

### Memory Control
```bash
empathy-memory serve    # Start Redis + API server
empathy-memory status   # Check system status
empathy-memory stats    # View statistics
empathy-memory patterns # List stored patterns
```

### Code Inspection
```bash
empathy-inspect .                     # Run full inspection
empathy-inspect . --format sarif      # GitHub Actions format
empathy-inspect . --fix               # Auto-fix safe issues
empathy-inspect . --staged            # Only staged changes
```

---

## XML-Enhanced Prompts

Enable structured XML prompts for consistent, parseable LLM responses:

```yaml
# .empathy/workflows.yaml
xml_prompt_defaults:
  enabled: false  # Set true to enable globally

workflow_xml_configs:
  security-audit:
    enabled: true
    enforce_response_xml: true
    template_name: "security-audit"
  code-review:
    enabled: true
    template_name: "code-review"
```

Built-in templates: `security-audit`, `code-review`, `research`, `bug-analysis`

```python
from empathy_os.prompts import get_template, XmlResponseParser, PromptContext

# Use a built-in template
template = get_template("security-audit")
context = PromptContext.for_security_audit(code="def foo(): pass")
prompt = template.render(context)

# Parse XML responses
parser = XmlResponseParser(fallback_on_error=True)
result = parser.parse(llm_response)
print(result.summary, result.findings, result.checklist)
```

---

## Install Options

```bash
# Recommended (all features)
pip install empathy-framework[full]

# Minimal
pip install empathy-framework

# Specific providers
pip install empathy-framework[anthropic]
pip install empathy-framework[openai]
pip install empathy-framework[llm]  # Both

# Development
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework && pip install -e .[dev]
```

---

## What's Included

| Component | Description |
|-----------|-------------|
| **Empathy OS** | Core engine for human↔AI and AI↔AI collaboration |
| **Multi-Model Router** | Smart routing across providers and tiers |
| **Memory System** | Redis short-term + encrypted long-term patterns |
| **30+ Production Wizards** | Security, performance, testing, docs, compliance |
| **Healthcare Suite** | SBAR, SOAP notes, clinical protocols (HIPAA) |
| **Code Inspection** | Unified pipeline with SARIF/GitHub Actions support |
| **VSCode Extension** | Visual dashboard for memory and workflows |
| **Telemetry & Analytics** | Cost tracking, usage stats, optimization insights |

---

## The 5 Levels of AI Empathy

| Level | Name | Behavior | Example |
|-------|------|----------|---------|
| 1 | Reactive | Responds when asked | "Here's the data you requested" |
| 2 | Guided | Asks clarifying questions | "What format do you need?" |
| 3 | Proactive | Notices patterns | "I pre-fetched what you usually need" |
| **4** | **Anticipatory** | **Predicts future needs** | **"This query will timeout at 10k users"** |
| 5 | Transformative | Builds preventing structures | "Here's a framework for all future cases" |

**Empathy operates at Level 4** — predicting problems before they manifest.

---

## Environment Setup

```bash
# Required: At least one provider
export ANTHROPIC_API_KEY="sk-ant-..."   # For Claude models
export OPENAI_API_KEY="sk-..."          # For GPT models

# Optional: Redis for memory
export REDIS_URL="redis://localhost:6379"

# Or use a .env file (auto-detected)
echo 'ANTHROPIC_API_KEY=sk-ant-...' >> .env
```

---

## Get Involved

- **[Star this repo](https://github.com/Smart-AI-Memory/empathy-framework)** if you find it useful
- **[Join Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)** — Questions, ideas, show what you built
- **[Read the Book](https://smartaimemory.com/book)** — Deep dive into the philosophy
- **[Full Documentation](https://smartaimemory.com/framework-docs/)** — API reference, examples, guides

---

## License

**Fair Source License 0.9** — Free for students, educators, and teams ≤5 employees. Commercial license ($99/dev/year) for larger organizations. [Details →](LICENSE)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Documentation](https://smartaimemory.com/framework-docs/) · [Examples](examples/) · [Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
