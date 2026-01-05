# Empathy Framework

**The AI collaboration framework that predicts problems before they happen.**

[![PyPI](https://img.shields.io/pypi/v/empathy-framework)](https://pypi.org/project/empathy-framework/)
[![Tests](https://img.shields.io/badge/tests-5%2C941%20passing-brightgreen)](https://github.com/Smart-AI-Memory/empathy-framework/actions)
[![Coverage](https://img.shields.io/badge/coverage-64%25-yellow)](https://github.com/Smart-AI-Memory/empathy-framework)
[![License](https://img.shields.io/badge/license-Fair%20Source%200.9-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://www.python.org)

```bash
pip install empathy-framework[developer]  # Lightweight for individual developers
```

## What's New in v3.6.0

### 💡 **Finally! Error Messages That Actually Help You**

**No more cryptic `NotImplementedError` when extending the framework!**

We completely rewrote error messages across **5 base classes**. Now when you're building plugins or extensions, you get:

✅ **Exactly which method** you need to implement
✅ **Which base class** to extend
✅ **Real working examples** from the codebase to copy
✅ **Clear explanations** of what each method should return

**Before** (frustrating 😤):

```python
NotImplementedError
# ...now what? Time to dig through source code for 30 minutes
```

**After** (helpful 🎯):

```python
NotImplementedError: BaseLinterParser.parse() must be implemented.
Create a subclass of BaseLinterParser and implement the parse() method.
See ESLintParser, PylintParser, or MyPyParser for examples.
# Perfect! Now I know exactly what to do
```

#### Plus: 9 Integration TODOs Now Link to Working Code

- **Want to add compliance tracking?** → See `ComplianceDatabase` class (agents/compliance_db.py)
- **Need multi-channel notifications?** → See `NotificationService` class (agents/notifications.py)
- **Wondering about MemDocs integration?** → We documented why local cache works better (with rationale)
- **Need secure document storage?** → S3/Azure/SharePoint recommendations with HIPAA requirements

**Impact**: Onboard new contributors in **minutes instead of hours**. Build your first plugin in **one sitting**.

---

### 🔐 Production-Grade Security & Compliance

#### Secure Authentication System ✅ *Deployed in Backend API*

- **Bcrypt password hashing** with cost factor 12 (industry standard 2026)
- **JWT tokens** with 30-minute expiration and automatic refresh
- **Rate limiting**: 5 failed attempts = 15-minute lockout (prevents brute force)
- **18 comprehensive security tests** covering all attack vectors
- **Status**: Fully integrated into `backend/api/wizard_api.py`

#### HIPAA/GDPR Compliance Database 🛠️ *Infrastructure Ready*

- **Append-only architecture** (INSERT only, no UPDATE/DELETE) - satisfies regulators
- **Immutable audit trail** for healthcare and enterprise compliance
- **Compliance gap detection** with severity classification
- **12 tests** ensuring regulatory compliance
- **Status**: Production-ready code with [integration points documented](agents/compliance_db.py). See [compliance_anticipation_agent.py](agents/compliance_anticipation_agent.py) for usage examples.

#### Multi-Channel Notification System 🛠️ *Infrastructure Ready*

- **Email** (SMTP), **Slack** (webhooks), **SMS** (Twilio)
- **Graceful fallback** when channels unavailable
- **Smart routing**: SMS only for critical alerts (cost optimization)
- **10 tests** covering all notification scenarios
- **Status**: Production-ready code with [integration points documented](agents/notifications.py). See TODOs in compliance agent for usage examples.

---

### Previous: Project Indexing & Test Suite Expansion (v3.5.4)

- **Project Indexing System** — JSON-based file tracking with automatic structure scanning, metadata tracking, and CrewAI integration
- **5,603 Tests** — Comprehensive test coverage at 64% with 30+ new test modules
- **BaselineManager Fix** — Resolved test isolation bug affecting suppression system

### Memory API Security Hardening (v3.5.0)

- **Input Validation** — Pattern IDs, agent IDs, and classifications validated to prevent path traversal and injection attacks
- **API Key Authentication** — Bearer token and X-API-Key header support with SHA-256 hash comparison
- **Rate Limiting** — Per-IP sliding window rate limiting (100 req/min default)
- **HTTPS/TLS Support** — Optional SSL certificate configuration for encrypted connections
- **CORS Restrictions** — Configurable allowed origins (localhost-only by default)
- **Request Size Limits** — 1MB body limit to prevent DoS attacks

### Previous (v3.4.x)

- **Trust Circuit Breaker** — Automatic degradation when model reliability drops
- **Pattern Catalog System** — Searchable pattern library with similarity matching
- **Memory Control Panel** — VSCode sidebar for Redis and pattern management

### Previous (v3.3.x)

- **Formatted Reports** — Every workflow includes `formatted_report` with consistent structure
- **Enterprise-Safe Doc-Gen** — Auto-scaling tokens, cost guardrails, file export
- **Unified Typer CLI** — One `empathy` command with Rich output
- **Python 3.13 Support** — Test matrix covers 3.10-3.13 across all platforms

### Previous (v3.1.x)

- **Smart Router** — Natural language wizard dispatch: "Fix security in auth.py" → SecurityWizard
- **Memory Graph** — Cross-wizard knowledge sharing across sessions
- **Auto-Chaining** — Wizards automatically trigger related wizards
- **Resilience Patterns** — Retry, Circuit Breaker, Timeout, Health Checks

### Previous (v3.0.x)

- **Multi-Model Provider System** — Anthropic, OpenAI, Google Gemini, Ollama, or Hybrid mode
- **80-96% Cost Savings** — Smart tier routing: cheap models detect, best models decide
- **VSCode Dashboard** — 10 integrated workflows with input history persistence

---

## Quick Start (2 Minutes)

### 1. Install

**Individual Developers (Recommended):**

```bash
pip install empathy-framework[developer]
```

**Teams/Enterprises (Backend + Auth):**

```bash
pip install empathy-framework[enterprise]
```

**Healthcare Organizations (HIPAA/GDPR Compliance):**

```bash
pip install empathy-framework[healthcare]
```

<details>
<summary><b>What's the difference?</b></summary>

- **`[developer]`** - Lightweight install for individual developers. Includes CLI tools, VSCode extension, LLM providers, agents. **No backend server needed.**

- **`[enterprise]`** - Everything in `[developer]` plus backend API server with authentication (bcrypt, JWT, rate limiting). For teams deploying to production.

- **`[healthcare]`** - Everything in `[enterprise]` plus HIPAA/GDPR compliance database, redis, and healthcare-specific plugins. Only needed for regulated industries.

**Most developers should use `[developer]`** - it's fast to install and has everything you need for software development.

</details>

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
| **Multi-provider support** | Claude, GPT-4, Gemini, Ollama | N/A | GPT only |
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
- **Memory Control Panel (Beta)** — Manage Redis and pattern storage
  - View Redis status and memory usage
  - Browse and export stored patterns
  - Run system health checks
  - Configure auto-start in `empathy.config.yml`

```yaml
memory:
  enabled: true
  auto_start_redis: true
```

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

Built-in templates: `security-audit`, `code-review`, `research`, `bug-analysis`, `perf-audit`, `refactor-plan`, `test-gen`, `doc-gen`, `release-prep`, `dependency-check`

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

## Enterprise Doc-Gen

Generate comprehensive documentation for large projects with enterprise-safe defaults:

```python
from empathy_os.workflows import DocumentGenerationWorkflow

# Enterprise-safe configuration
workflow = DocumentGenerationWorkflow(
    export_path="docs/generated",     # Auto-save to disk
    max_cost=5.0,                     # Cost guardrail ($5 default)
    chunked_generation=True,          # Handle large projects
    graceful_degradation=True,        # Partial results on errors
)

result = await workflow.execute(
    source_code=your_code,
    doc_type="api_reference",
    audience="developers"
)

# Access the formatted report
print(result.final_output["formatted_report"])

# Large outputs are chunked for display
if "output_chunks" in result.final_output:
    for chunk in result.final_output["output_chunks"]:
        print(chunk)

# Full docs saved to disk
print(f"Saved to: {result.final_output.get('export_path')}")
```

---

## Smart Router

Route natural language requests to the right wizard automatically:

```python
from empathy_os.routing import SmartRouter

router = SmartRouter()

# Natural language routing
decision = router.route_sync("Fix the security vulnerability in auth.py")
print(f"Primary: {decision.primary_wizard}")      # → security-audit
print(f"Also consider: {decision.secondary_wizards}")  # → [code-review]
print(f"Confidence: {decision.confidence}")

# File-based suggestions
suggestions = router.suggest_for_file("requirements.txt")  # → [dependency-check]

# Error-based suggestions
suggestions = router.suggest_for_error("NullReferenceException")  # → [bug-predict, test-gen]
```

---

## Memory Graph

Cross-wizard knowledge sharing - wizards learn from each other:

```python
from empathy_os.memory import MemoryGraph, EdgeType

graph = MemoryGraph()

# Add findings from any wizard
bug_id = graph.add_finding(
    wizard="bug-predict",
    finding={
        "type": "bug",
        "name": "Null reference in auth.py:42",
        "severity": "high"
    }
)

# Connect related findings
fix_id = graph.add_finding(wizard="code-review", finding={"type": "fix", "name": "Add null check"})
graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)

# Find similar past issues
similar = graph.find_similar({"name": "Null reference error"})

# Traverse relationships
related_fixes = graph.find_related(bug_id, edge_types=[EdgeType.FIXED_BY])
```

---

## Auto-Chaining

Wizards automatically trigger related wizards based on findings:

```yaml
# .empathy/wizard_chains.yaml
chains:
  security-audit:
    auto_chain: true
    triggers:
      - condition: "high_severity_count > 0"
        next: dependency-check
        approval_required: false
      - condition: "vulnerability_type == 'injection'"
        next: code-review
        approval_required: true

  bug-predict:
    triggers:
      - condition: "risk_score > 0.7"
        next: test-gen

templates:
  full-security-review:
    steps: [security-audit, dependency-check, code-review]
  pre-release:
    steps: [test-gen, security-audit, release-prep]
```

```python
from empathy_os.routing import ChainExecutor

executor = ChainExecutor()

# Check what chains would trigger
result = {"high_severity_count": 5}
triggers = executor.get_triggered_chains("security-audit", result)
# → [ChainTrigger(next="dependency-check"), ...]

# Execute a template
template = executor.get_template("full-security-review")
# → ["security-audit", "dependency-check", "code-review"]
```

---

## Prompt Engineering Wizard

Analyze, generate, and optimize prompts:

```python
from coach_wizards import PromptEngineeringWizard

wizard = PromptEngineeringWizard()

# Analyze existing prompts
analysis = wizard.analyze_prompt("Fix this bug")
print(f"Score: {analysis.overall_score}")  # → 0.13 (poor)
print(f"Issues: {analysis.issues}")        # → ["Missing role", "No output format"]

# Generate optimized prompts
prompt = wizard.generate_prompt(
    task="Review code for security vulnerabilities",
    role="a senior security engineer",
    constraints=["Focus on OWASP top 10"],
    output_format="JSON with severity and recommendation"
)

# Optimize tokens (reduce costs)
result = wizard.optimize_tokens(verbose_prompt)
print(f"Reduced: {result.token_reduction:.0%}")  # → 20% reduction

# Add chain-of-thought scaffolding
enhanced = wizard.add_chain_of_thought(prompt, "debug")
```

---

## Install Options

```bash
# Recommended (all features)
pip install empathy-framework[full]

# Minimal
pip install empathy-framework

# Specific providers
pip install empathy-framework[anthropic]  # Claude
pip install empathy-framework[openai]     # GPT-4, Ollama (OpenAI-compatible)
pip install empathy-framework[google]     # Gemini
pip install empathy-framework[llm]        # All providers

# Development
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework && pip install -e .[dev]
```

---

## What's Included

| Component | Description |
|-----------|-------------|
| **Empathy OS** | Core engine for human↔AI and AI↔AI collaboration |
| **Smart Router** | Natural language wizard dispatch with LLM classification |
| **Memory Graph** | Cross-wizard knowledge sharing (bugs, fixes, patterns) |
| **Auto-Chaining** | Wizards trigger related wizards based on findings |
| **Multi-Model Router** | Smart routing across providers and tiers |
| **Memory System** | Redis short-term + encrypted long-term patterns |
| **17 Coach Wizards** | Security, performance, testing, docs, prompt engineering |
| **10 Cost-Optimized Workflows** | Multi-tier pipelines with formatted reports & XML prompts |
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
export ANTHROPIC_API_KEY="sk-ant-..."   # For Claude models  # pragma: allowlist secret
export OPENAI_API_KEY="sk-..."          # For GPT models  # pragma: allowlist secret
export GOOGLE_API_KEY="..."             # For Gemini models  # pragma: allowlist secret

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

## Project Evolution

For those interested in the development history and architectural decisions:

- **[Development Logs](docs/development-logs/)** — Execution plans, phase completions, and progress tracking
- **[Architecture Docs](docs/architecture/)** — System design, memory architecture, and integration plans
- **[Marketing Materials](docs/marketing/)** — Pitch decks, outreach templates, and commercial readiness
- **[Guides](docs/guides/)** — Publishing tutorials, MkDocs setup, and distribution policies

---

## License

**Fair Source License 0.9** — Free for students, educators, and teams ≤5 employees. Commercial license ($99/dev/year) for larger organizations. [Details →](LICENSE)

---

**Built by [Smart AI Memory](https://smartaimemory.com)** · [Documentation](https://smartaimemory.com/framework-docs/) · [Examples](examples/) · [Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
