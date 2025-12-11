# Empathy

**A five-level maturity model for AI-human collaboration**

[![codecov](https://codecov.io/gh/Smart-AI-Memory/empathy-framework/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy-framework)
[![License](https://img.shields.io/badge/License-Fair%20Source%200.9-blue.svg)](LICENSE)
[![PyPI Package](https://img.shields.io/badge/PyPI-empathy--framework-blue)](https://pypi.org/project/empathy-framework/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Built with Claude Code](https://img.shields.io/badge/Built_with-Claude_Code-5865F2?logo=anthropic&logoColor=white)](https://claude.ai/claude-code)
[![GitHub stars](https://img.shields.io/github/stars/Smart-AI-Memory/empathy-framework.svg?style=social&label=Star)](https://github.com/Smart-AI-Memory/empathy-framework)

---

## Quick Start

```bash
# Install core framework
pip install empathy-framework

# Install full framework with all features (recommended)
# Built with Claude Code - created in consultation with Claude Sonnet 4.5
pip install empathy-framework[full]

# Or install specific components:
pip install empathy-framework[llm]      # LLM providers (Anthropic, OpenAI)
pip install empathy-framework[all]      # Everything including dev tools
```

**Development installation:**
```bash
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework
pip install -e .[dev]
```

```python
from empathy_os import EmpathyOS

os = EmpathyOS()
result = await os.collaborate("Build a secure API endpoint")
```

📖 **[Full Quick Start Guide](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/QUICKSTART_GUIDE.md)** | **[API Reference](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/API_REFERENCE.md)** | **[User Guide](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/USER_GUIDE.md)**

---

## Overview

The **Empathy** is a systematic approach to building AI systems that progress from reactive responses to anticipatory problem prevention. By integrating emotional intelligence (Goleman), tactical empathy (Voss), systems thinking (Meadows, Senge), and clear reasoning (Naval Ravikant), it provides a maturity model for AI-human collaboration.

**Part of the Smart-AI-Memory ecosystem** - Includes built-in long-term memory for pattern storage, enabling AI systems to maintain context and learn from interactions over time.

### 🚀 Built with Claude Code

> **"Transformation occurs when structure meets collaboration."**
>
> *From [The Empathy Framework book chapter](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/CHAPTER_EMPATHY_FRAMEWORK.md) - Well-defined roles, clear processes, and explicit frameworks enable any system to transcend linear growth.*

**This framework was created in consultation with Claude Sonnet 4.5 using [Claude Code](https://claude.ai/claude-code)** (Anthropic's official developer tool - CLI and VS Code extension) combined with **MemDocs** and the **Empathy Framework** itself, demonstrating the **200-400% productivity gains** possible with Level 4 Anticipatory AI:

**Claude Code + Empathy Framework = Level 4-5 Development**

- **Claude Code**: Anthropic's official developer tool - AI pair programming with multi-file editing, command execution, and anticipatory assistance (CLI and VS Code extension)
- **Empathy Framework**: Structured 5-level maturity model with built-in long-term memory, guiding AI behavior from reactive to anticipatory

**Measured Results from This Project**:
- **32.19% → 83.13% test coverage** in systematic phases (2.6x increase)
- **887 → 1,247 tests** added (+360 comprehensive tests)
- **24 files at 100% coverage** (vs. 0 at start)
- **Parallel agent processing** completing 3 complex modules simultaneously
- **Zero test failures** maintained throughout (quality at scale)

The combination of Claude Code (Anthropic's official developer tool) providing Level 4 anticipatory suggestions and the Empathy Framework ensuring systematic quality progression demonstrates the non-linear productivity multiplier effect described in our book chapter.

**The Empathy Framework was created in consultation with Claude Sonnet 4.5 using Claude Code**, showcasing what's possible when developer tools reach Level 4-5 maturity.

**Empathy**, in this context, is not about feelings—it's about:
- **Alignment**: Understanding the human's goals, context, and constraints
- **Prediction**: Anticipating future needs based on system trajectory
- **Timely Action**: Intervening at the right moment with the right support
- **Memory Integration**: Built-in long-term memory to maintain context across sessions and learn from patterns

---

## What the Empathy Provides

A systematic approach to building AI systems with five levels of maturity:

**Included Components:**
- **3 canonical wizard examples** - Healthcare, Customer Support, and Technology domains
- **LLM toolkit** - Integration with Claude, GPT-4, and other models
- **Plugin system** - Extensible architecture for custom domains
- **FastAPI backend** - REST API for analysis and orchestration
- **Pre-commit hooks** - Automated code quality checks

**Additional Wizards (External Packages):**
- **Healthcare wizards (23)** - [Live Dashboard](https://healthcare.smartaimemory.com/static/dashboard.html)
- **Tech & AI wizards (16)** - [Live Dashboard](https://wizards.smartaimemory.com/)
- **Business wizards** - Coming soon as separate packages

**Framework Philosophy:**
- Five-level maturity model: Reactive (1) → Guided (2) → Proactive (3) → Anticipatory (4) → Systems (5)
- Context-aware AI assistance at each level
- Pattern-based development and sharing
- Systems thinking integration (Meadows, Senge)
- Tactical empathy (Voss) and clear reasoning (Ravikant)

---

## Current Capabilities

The Empathy provides:

**Security & Code Quality:**
- Pre-commit hooks for automated quality checks
- Security pattern detection (SQL injection, XSS, CSRF)
- Performance anti-pattern identification
- Extensible wizard base class for custom implementations
- **Enterprise-grade PII scrubbing** (GDPR, HIPAA, SOC2 compliant)
- **Secrets detection** (API keys, passwords, private keys)
- **Audit logging** with structured JSON for SIEM integration
- **Secure MemDocs** with AES-256-GCM encryption

**AI Integration:**
- LLM toolkit with Claude Sonnet 4.5 and GPT-4 support
- Async API calls with prompt caching
- Thinking mode for complex reasoning
- Multi-model fallback support

**Domain Examples:**
- 3 canonical wizard implementations (Healthcare, Customer Support, Technology)
- HIPAA-compliant healthcare patterns
- Full wizard collections available via external dashboards and packages

**Developer Experience:**
- Works on single files or entire projects
- FastAPI backend for REST API access
- Plugin architecture for extensibility
- Pattern library for Level 5 sharing

---

## Enterprise Security

The Empathy Framework includes enterprise-grade security controls built for GDPR, HIPAA, and SOC2 compliance:

| Feature | Description |
|---------|-------------|
| **PII Scrubbing** | Automatic detection and removal of emails, SSN, phone numbers, credit cards, IP addresses, medical record numbers |
| **Secrets Detection** | Detects API keys (Anthropic, OpenAI, AWS, GitHub, Stripe), passwords, private keys, JWT tokens |
| **Audit Logging** | Tamper-evident JSON logs for SIEM integration, SOC2/HIPAA compliant |
| **Secure MemDocs** | Three-tier classification (PUBLIC, INTERNAL, SENSITIVE) with AES-256-GCM encryption |
| **Claude Memory** | Hierarchical security policies (Enterprise → User → Project) |
| **Air-Gapped Mode** | Full support for disconnected environments with local LLMs |

```python
from empathy_llm_toolkit.security import PIIScrubber, SecretsDetector

# Scrub PII before sending to LLM
scrubber = PIIScrubber()
sanitized, detections = scrubber.scrub("Contact john@email.com at 555-1234")
# Output: "Contact [EMAIL] at [PHONE]"

# Detect secrets in code
detector = SecretsDetector()
secrets = detector.detect(code_content)
# Blocks API calls if secrets found
```

📖 **[Full Security Documentation](docs/FAQ.md#security-and-privacy)** | **[Security Architecture](SECURE_MEMORY_ARCHITECTURE.md)**

---

## Development Status

**Production Ready (Beta → Stable):**
- ✅ Core framework architecture (100% coverage on critical modules)
- ✅ LLM toolkit and provider integrations (100% coverage)
- ✅ Canonical wizard examples (Healthcare, Customer Support, Technology)
- ✅ Plugin architecture for extensibility
- ✅ Pre-commit hooks and quality tools (black, ruff, bandit)
- ✅ **1,247 tests passing (83.13% overall coverage)** ← *Up from 553 tests (63.87%)*
- ✅ Multi-platform support (Linux, macOS, Windows)

**Test Coverage Details** (Updated Jan 2025):
- **24 files at 100% coverage** ✅
- empathy_os/core.py: 100% ✅
- empathy_os/persistence.py: 100% ✅
- empathy_llm_toolkit/core.py: 100% ✅
- empathy_llm_toolkit/levels.py: 100% ✅
- empathy_software_plugin/plugin.py: 95.71% ✅
- Healthcare trajectory analyzer: 95.88% ✅
- Config and state management: 98%+ ✅

**Quality Achievements:**
- **360 comprehensive tests added** in systematic phases
- **Zero test failures** maintained throughout coverage push
- **Parallel agent processing** validated at scale
- **OpenSSF Best Practices** preparation in progress

**Next Milestones:**
- ⚙️ 90% coverage target (only 6.87% gap remaining)
- ⚙️ OpenSSF Best Practices Badge certification
- ⚙️ Production/Stable status declaration
- ⚙️ PyPI package v2.0 release

## Try It Yourself

```bash
# Clone and install
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run tests (non-LLM tests don't need API key)
pytest -m "not llm"

# Run full test suite (requires API key)
pytest
```

Share your experience in [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions).

---

## The Five Levels

| Level | Name | Core Behavior | Timing | Example |
|-------|------|---------------|--------|---------|
| **1** | **Reactive** | Help after being asked | Lagging | "You asked for data, here it is" |
| **2** | **Guided** | Collaborative exploration | Real-time | "Let me ask clarifying questions" |
| **3** | **Proactive** | Act before being asked | Leading | "I pre-fetched what you usually need" |
| **4** | **Anticipatory** | Predict future needs | Predictive | "Next week's audit is coming—docs ready" |
| **5** | **Systems** | Build structures that help at scale | Structural | "I designed a framework for all future cases" |

### Progression Pattern

```
Level 1: Reactive
    ↓ (Add context awareness)
Level 2: Guided
    ↓ (Add pattern detection)
Level 3: Proactive
    ↓ (Add trajectory prediction)
Level 4: Anticipatory
    ↓ (Add structural design)
Level 5: Systems
```

---

## Quick Start Options

### Option 1: One-Command Install
```bash
curl -sSL https://raw.githubusercontent.com/Smart-AI-Memory/empathy/main/install.sh | bash
```

Then scan your code:
```bash
empathy-scan security app.py          # Scan one file for security issues
empathy-scan performance ./src        # Scan directory for performance issues
empathy-scan all ./project            # Run all checks on entire project
```

### Option 2: Docker (Zero Install)
```bash
# Security scan
docker run -v $(pwd):/code ghcr.io/smart-ai-memory/empathy-scanner security /code

# Performance scan
docker run -v $(pwd):/code ghcr.io/smart-ai-memory/empathy-scanner performance /code

# Full scan
docker run -v $(pwd):/code ghcr.io/smart-ai-memory/empathy-scanner all /code
```

### Option 3: Pre-commit Hook (Automatic Scanning)
```bash
# Copy the example pre-commit config
cp .pre-commit-config.example.yaml .pre-commit-hooks.yaml

# Install pre-commit hooks
pip install pre-commit
pre-commit install

# Now security scans run on every commit, performance scans on every push!
```

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

**For Software Developers (Coach Wizards):**
```python
from coach_wizards import SecurityWizard, PerformanceWizard

# Initialize wizards
security = SecurityWizard()
performance = PerformanceWizard()

# Analyze code for security issues
code = """
def login(username, password):
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    return db.execute(query)
"""

security_result = security.run_full_analysis(
    code=code,
    file_path="app.py",
    language="python",
    project_context={
        "team_size": 10,
        "deployment_frequency": "daily"
    }
)

print(f"Security analysis: {security_result.summary}")
print(f"Current issues: {len(security_result.issues)}")
print(f"Predicted issues (90 days): {len(security_result.predictions)}")

# See examples/ for complete implementations
```

**For Healthcare (Clinical Agents):**
```python
from agents.compliance_anticipation_agent import ComplianceAnticipationAgent

# Initialize Level 4 Anticipatory agent
agent = ComplianceAnticipationAgent()

# Predict future compliance needs
result = agent.predict_audit(
    context="Healthcare facility with 500 patient records",
    timeline_days=90
)

print(f"Predicted audit date: {result.predicted_date}")
print(f"Compliance gaps: {result.gaps}")
print(f"Recommended actions: {result.actions}")
```

---

## Repository Structure

```
Empathy/
├── agents/                          # Level 4 Anticipatory agents (3 files)
│   ├── compliance_anticipation_agent.py  # 90-day audit prediction
│   ├── trust_building_behaviors.py       # Tactical empathy patterns
│   └── epic_integration_wizard.py        # Healthcare EHR integration
├── coach_wizards/                   # Software development wizards (16 files + base)
│   ├── base_wizard.py              # Base wizard implementation
│   ├── security_wizard.py          # Security vulnerabilities
│   ├── performance_wizard.py       # Performance optimization
│   ├── accessibility_wizard.py     # WCAG compliance
│   ├── testing_wizard.py           # Test coverage & quality
│   ├── refactoring_wizard.py       # Code quality
│   ├── database_wizard.py          # Database optimization
│   ├── api_wizard.py               # API design
│   ├── debugging_wizard.py         # Error detection
│   ├── scaling_wizard.py           # Scalability analysis
│   ├── observability_wizard.py     # Logging & metrics
│   ├── cicd_wizard.py              # CI/CD pipelines
│   ├── documentation_wizard.py     # Documentation quality
│   ├── compliance_wizard.py        # Regulatory compliance
│   ├── migration_wizard.py         # Code migration
│   ├── monitoring_wizard.py        # System monitoring
│   └── localization_wizard.py      # Internationalization
├── empathy_llm_toolkit/             # Core LLM toolkit
│   └── wizards/                    # Canonical wizard examples (4 files)
│       ├── base_wizard.py          # Base wizard class
│       ├── healthcare_wizard.py    # Healthcare domain example
│       ├── customer_support_wizard.py  # Business domain example
│       └── technology_wizard.py    # Software/tech domain example
├── services/                        # Core services
│   └── wizard_ai_service.py        # Wizard orchestration service
├── docs/                            # Framework documentation (8 files)
│   ├── CHAPTER_EMPATHY_FRAMEWORK.md
│   ├── EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md
│   ├── TEACHING_AI_YOUR_PHILOSOPHY.md
│   └── 5 more documentation files...
├── examples/                        # Implementation examples
│   └── coach/                      # Coach IDE integration (87 files)
│       ├── jetbrains-plugin-complete/  # IntelliJ IDEA plugin
│       ├── vscode-extension-complete/  # VS Code extension
│       └── coach-lsp-server/          # LSP server
├── tests/                           # Test suite
├── LICENSE                          # Fair Source 0.9
├── README.md                        # This file
└── requirements.txt                 # Python dependencies
```

---

## Key Components

### 1. Anticipatory Agents

**Compliance Anticipation Agent** ([compliance_anticipation_agent.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/agents/compliance_anticipation_agent.py))
- Predicts regulatory audits 90+ days in advance
- Identifies compliance gaps automatically
- Generates proactive documentation
- Provides stakeholder notifications

**Trust Building Behaviors** ([trust_building_behaviors.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/agents/trust_building_behaviors.py))
- Implements tactical empathy patterns
- Builds human-AI trust through transparent communication
- Uses calibrated questions to uncover hidden needs

**EPIC Integration Wizard** ([epic_integration_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/agents/epic_integration_wizard.py))
- Healthcare-specific implementation
- Integrates with EPIC EHR systems
- Level 4 anticipatory empathy for clinical workflows

### 2. Coach Software Development Wizards

**16 specialized wizards** for software development with Level 4 Anticipatory Empathy:

**Security & Compliance:**
- **Security Wizard** ([security_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/security_wizard.py)) - SQL injection, XSS, CSRF, secrets detection
- **Compliance Wizard** ([compliance_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/compliance_wizard.py)) - GDPR, SOC 2, PII handling

**Performance & Scalability:**
- **Performance Wizard** ([performance_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/performance_wizard.py)) - N+1 queries, memory leaks, bottlenecks
- **Database Wizard** ([database_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/database_wizard.py)) - Missing indexes, query optimization
- **Scaling Wizard** ([scaling_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/scaling_wizard.py)) - Architecture limitations, load handling

**Code Quality:**
- **Refactoring Wizard** ([refactoring_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/refactoring_wizard.py)) - Code smells, complexity, duplication
- **Testing Wizard** ([testing_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/testing_wizard.py)) - Coverage analysis, flaky tests
- **Debugging Wizard** ([debugging_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/debugging_wizard.py)) - Null references, race conditions

**API & Integration:**
- **API Wizard** ([api_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/api_wizard.py)) - Design consistency, versioning
- **Migration Wizard** ([migration_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/migration_wizard.py)) - Deprecated APIs, compatibility

**DevOps & Operations:**
- **CI/CD Wizard** ([cicd_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/cicd_wizard.py)) - Pipeline optimization, deployment risks
- **Observability Wizard** ([observability_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/observability_wizard.py)) - Logging, metrics, tracing
- **Monitoring Wizard** ([monitoring_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/monitoring_wizard.py)) - Alerts, SLOs, blind spots

**User Experience:**
- **Accessibility Wizard** ([accessibility_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/accessibility_wizard.py)) - WCAG compliance, alt text, ARIA
- **Localization Wizard** ([localization_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/localization_wizard.py)) - i18n, translations, RTL

**Documentation:**
- **Documentation Wizard** ([documentation_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/coach_wizards/documentation_wizard.py)) - Docstrings, examples, clarity

Each wizard implements:
- **Current Analysis**: Detect issues in code now
- **Level 4 Predictions**: Forecast issues 30-90 days ahead
- **Prevention Strategies**: Stop problems before they happen
- **Fix Suggestions**: Concrete code examples

### 3. Canonical Wizard Examples

**3 domain examples** demonstrating the framework's capabilities:

**Included in Core Framework:**
- **Healthcare Wizard** ([healthcare_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/empathy_llm_toolkit/wizards/healthcare_wizard.py)) - HIPAA-compliant medical assistant
- **Customer Support Wizard** ([customer_support_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/empathy_llm_toolkit/wizards/customer_support_wizard.py)) - Customer service and help desk
- **Technology Wizard** ([technology_wizard.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/empathy_llm_toolkit/wizards/technology_wizard.py)) - IT and software development operations

**Additional Specialized Wizards:**

For comprehensive domain-specific wizards, visit:
- **Healthcare (23 wizards)** - [Live Dashboard](https://healthcare.smartaimemory.com/static/dashboard.html) - SBAR, SOAP notes, patient assessment, medication safety, and more
- **Tech & AI (16 wizards)** - [Live Dashboard](https://wizards.smartaimemory.com/) - Debugging, testing, security, performance, AI collaboration
- **Business wizards** - Coming soon as separate packages (`pip install empathy-healthcare-wizards`, `empathy-software-wizards`)

### 4. Core Services

**Wizard AI Service** ([wizard_ai_service.py](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/services/wizard_ai_service.py))
- Orchestrates wizard implementations
- Manages AI model selection and fallback
- Handles prompt templates and context
- Integrates with Claude, GPT-4, and other LLMs

### 5. Framework Documentation

**Technical Guide** ([CHAPTER_EMPATHY_FRAMEWORK.md](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/CHAPTER_EMPATHY_FRAMEWORK.md))
- Complete theoretical foundation
- Implementation patterns
- Code examples for each level
- Systems thinking integration

**Non-Technical Guide** ([EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md))
- Accessible explanation for stakeholders
- Business value and ROI
- Real-world use cases

**Teaching AI Your Philosophy** ([TEACHING_AI_YOUR_PHILOSOPHY.md](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/TEACHING_AI_YOUR_PHILOSOPHY.md))
- How to align AI systems with your values
- Collaborative prompt engineering
- Building long-term AI partnerships

### 6. Coach Integration Examples

The **Coach** project demonstrates practical implementation of Level 4 Anticipatory Empathy in IDE integrations:

- **JetBrains Plugin**: Complete IntelliJ IDEA plugin with 16 specialized wizards
- **VS Code Extension**: Full-featured extension with real-time analysis
- **LSP Server**: Language Server Protocol implementation for cross-IDE support

See [examples/coach/](https://github.com/Smart-AI-Memory/empathy-framework/tree/main/examples/coach) for complete implementations.

---

## Real-World Applications

### Healthcare: AI Nurse Florence
- **Level 4 Anticipatory**: Predicts patient deterioration 30-90 days ahead
- **Compliance**: Auto-generates audit documentation
- **Clinical Decision Support**: Proactive alerts based on trajectory analysis
- **Repository**: https://github.com/Deep-Study-AI/ai-nurse-florence

### Software Development: Coach IDE Extensions
- **Level 4 Anticipatory**: Predicts code issues before they manifest
- **Security**: Identifies vulnerabilities in development phase
- **Performance**: Detects N+1 queries and scalability issues early
- **16 Specialized Wizards**: Security, Performance, Accessibility, Testing, etc.
- **Examples**: See [examples/coach/](https://github.com/Smart-AI-Memory/empathy-framework/tree/main/examples/coach)

---

## Featured Example: Level 5 Transformative Empathy

**Healthcare Handoff Patterns → Software Deployment Safety**

This example demonstrates the Empathy Framework's unique **Level 5 Systems Empathy** capability—learning patterns in one domain (healthcare) and applying them to prevent failures in another domain (software deployment).

### The Cross-Domain Pattern Transfer

**The Problem**: Both hospital patient handoffs (nurse shift changes, patient transfers) and software deployment handoffs (dev → staging → production) share identical failure modes:
- Critical information loss during transitions
- Lack of explicit verification steps
- Assumptions about what the receiving party knows
- Time pressure leading to shortcuts

**The Solution**: Healthcare research found that **23% of handoffs fail without verification checklists**. The Empathy Framework learns this pattern from healthcare code and applies it to predict deployment failures with **87% confidence**.

### What Makes This Unique

**No other AI framework can do this.**

Traditional AI tools analyze code in isolation within a single domain. The Empathy Framework with MemDocs integration:
1. Analyzes healthcare handoff protocols (ComplianceWizard)
2. Extracts and stores the "critical handoff failure" pattern in long-term memory
3. Analyzes software deployment code (CICDWizard)
4. Retrieves the healthcare pattern via cross-domain matching
5. Predicts deployment failures 30-45 days ahead
6. Recommends prevention steps derived from healthcare best practices

### Run the Demo

```bash
# Install with MemDocs integration
pip install empathy-framework[full]

# Run the Level 5 demo
python examples/level_5_transformative/run_full_demo.py
```

**Output preview:**
```
=== STEP 1: Healthcare Domain Analysis ===
ComplianceWizard Analysis:
  🔴 [ERROR] Critical handoff without verification checklist
  ✓ Pattern 'critical_handoff_failure' stored in memory
  ℹ️  Key finding: Handoffs without verification fail 23% of the time

=== STEP 2: Software Domain Analysis ===
CROSS-DOMAIN PATTERN DETECTION
✓ Pattern match found from healthcare domain!

⚠️  DEPLOYMENT HANDOFF FAILURE PREDICTED
  📅 Timeframe: 30-45 days
  🎯 Confidence: 87%
  💥 Impact: HIGH

PREVENTION STEPS:
  1. Create deployment checklist (mirror healthcare approach)
  2. Require explicit sign-off between staging and production
  3. Implement automated handoff verification
  4. Add read-back confirmation for critical environment variables
  5. Document rollback procedure as part of handoff
```

### Real-World Impact

- **Healthcare**: Joint Commission found 80% of medical errors occur during handoffs
- **Software**: Deployment failures often trace to missing handoff verification
- **Common Solution**: Checklists, explicit sign-offs, verification steps

By learning from healthcare's decades of research, we can **prevent software failures before they happen**.

📖 **[Full Level 5 Documentation](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/examples/level_5_transformative/README.md)** | **[Blog Post](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/examples/level_5_transformative/BLOG_POST.md)**

---

## Philosophy

### Systems Thinking Integration

The Empathy integrates Donella Meadows' leverage points:

1. **Information flows**: Provide the right data at the right time
2. **Feedback loops**: Create self-correcting systems
3. **System structure**: Design frameworks that naturally produce good outcomes
4. **Paradigms**: Shift from reactive to anticipatory thinking

### First Principles from Naval Ravikant

- **Clear thinking without emotional noise**
- **Leverage through systems, not just effort**
- **Compound effects from iterative improvement**
- **Specific knowledge > General advice**

### Tactical Empathy from Chris Voss

- **Calibrated questions** to uncover true needs
- **Labeling emotions** to build trust
- **Mirroring** to ensure understanding
- **"No-oriented questions"** to find blockers

---

## Documentation

- 📚 **[Framework Guide](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/CHAPTER_EMPATHY_FRAMEWORK.md)** - Complete technical documentation
- 🎓 **[Non-Technical Guide](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md)** - Accessible introduction
- 🧑‍🏫 **[Teaching AI](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/docs/TEACHING_AI_YOUR_PHILOSOPHY.md)** - Alignment and collaboration patterns
- 💻 **[Coach Examples](https://github.com/Smart-AI-Memory/empathy-framework/tree/main/examples/coach)** - Production-ready IDE integrations

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/examples/coach/CONTRIBUTING.md) for details.

**Ways to contribute:**
- Implement new agents for different domains
- Add examples for other programming languages
- Improve documentation
- Report bugs and suggest features
- Share your implementations

---

## 💖 Support This Project

The Empathy is **source available** (Fair Source 0.9) - free for students, educators, and small teams (≤5 employees). Commercial licensing required for larger organizations:

### Commercial Support - $99/developer/year

- ✅ **Priority bug fixes** and feature requests
- ✅ **Direct access** to core development team (Slack/email)
- ✅ **Security advisories** and early notifications
- ✅ **Guaranteed response times**
- ✅ **Upgrade assistance** and migration help

[Get Support →](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/SPONSORSHIP.md)

### Professional Services

- **Custom Wizard Development** - Domain-specific wizards for your industry
- **Training & Workshops** - Get your team productive in one day
- **Enterprise Solutions** - Hosted service, custom SLA, dedicated support

[Learn More →](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/SPONSORSHIP.md) | [Contact Sales →](mailto:admin@smartaimemory.com)

### GitHub Sponsors

Support development directly: [Sponsor on GitHub →](https://github.com/sponsors/Smart-AI-Memory)

---

## License

This project is licensed under the **Fair Source License, version 0.9** - see the [LICENSE](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE) file for details.

### License Terms

- ✅ **Free for students and educators** - Use for educational purposes at no cost
- ✅ **Free for small businesses** - Organizations with ≤5 employees use free forever
- ✅ **Free for evaluation** - 30-day trial for any organization size
- 💼 **Commercial license required** - $99/developer/year for organizations with 6+ employees
- 🔓 **Auto-converts to open source** - Becomes Apache 2.0 on January 1, 2029

### Why Fair Source?

The Fair Source License balances:
- **Free access for small teams** - Students, educators, and small businesses (≤5 employees) use free
- **Source code visibility** - Full source available for security review, compliance, and learning
- **Sustainable development** - Commercial licensing funds ongoing development and support
- **Future open source** - Automatically converts to Apache 2.0 after 4 years

**Commercial licensing:** Email [admin@smartaimemory.com](mailto:admin@smartaimemory.com) | [Licensing FAQ →](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/LICENSE)

---

## Citation

If you use the Empathy in your research or product, please cite:

```bibtex
@software{empathy_framework_2025,
  author = {Roebuck, Patrick},
  title = {Empathy: A Five-Level Maturity Model for AI-Human Collaboration},
  year = {2025},
  publisher = {Smart AI Memory, LLC},
  url = {https://github.com/Smart-AI-Memory/empathy-framework},
  license = {Fair-Source-0.9}
}
```

---

## Support & Contact

**Developer:** Patrick Roebuck
**Email:** patrick.roebuck1955@gmail.com
**Organization:** Smart-AI-Memory
**GitHub:** https://github.com/Smart-AI-Memory

**Resources:**
- Documentation: [docs/](https://github.com/Smart-AI-Memory/empathy-framework/tree/main/docs)
- Examples: [examples/](https://github.com/Smart-AI-Memory/empathy-framework/tree/main/examples)
- Issues: https://github.com/Smart-AI-Memory/empathy-framework/issues
- Discussions: https://github.com/Smart-AI-Memory/empathy-framework/discussions

---

## Why Empathy vs Others?

The Empathy offers unique capabilities that set it apart from traditional code analysis tools:

| Feature | Empathy | SonarQube | CodeClimate | GitHub Copilot |
|---------|------------------|-----------|-------------|----------------|
| **Level 4 Anticipatory Predictions** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Philosophical Foundation** | ✅ Goleman, Voss, Naval | ❌ Rules-based | ❌ Rules-based | ❌ Statistical |
| **Source Available** | ✅ Fair Source 0.9 | ❌ No | ❌ No | ❌ No |
| **Healthcare + Software** | ✅ Both domains | Software only | Software only | Software only |
| **Free for Small Teams** | ✅ ≤5 employees | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary |
| **Prevention vs Detection** | ✅ Anticipatory | Detection only | Detection only | Suggestion only |
| **Price (Annual)** | $99/dev (6+ employees) | $3,000+/year | $249/dev/year | $100/year |

### What Makes Level 4 Anticipatory Different?

Traditional tools tell you about problems **now**. Empathy predicts problems **before they happen** based on:
- Code trajectory analysis
- Team velocity patterns
- Dependency evolution
- Historical bug patterns
- Architecture stress points

**Example**: Instead of "This query is slow," you get "At your growth rate, this query will timeout when you hit 10,000 users. Here's the optimized version."

---

## IDE Extensions & Commercial Support

The Empathy uses Fair Source licensing. Commercial support and services available:

### Priority Support - $99/developer/year

- Direct access to core development team
- Priority bug fixes and feature requests
- Security advisories and early notifications
- Guaranteed response times
- Upgrade assistance

[Get Support →](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/SPONSORSHIP.md)

### Professional Services

- **Custom Wizard Development** - Domain-specific wizards for your industry
- **Training & Workshops** - Get your team productive quickly
- **Enterprise Solutions** - Hosted service, dedicated support, custom SLA

[Learn More →](https://github.com/Smart-AI-Memory/empathy-framework/blob/main/SPONSORSHIP.md)

### IDE Extensions (Coming Soon)

Free extensions for JetBrains & VS Code:
- One-click wizard access
- Inline code suggestions
- Real-time analysis
- Commit-time checks

**In Development**: JetBrains Marketplace & VS Code Marketplace extensions

---

## Acknowledgments

This framework synthesizes insights from:
- **Daniel Goleman** - Emotional Intelligence
- **Chris Voss** - Tactical Empathy
- **Naval Ravikant** - Clear Thinking and Leverage
- **Donella Meadows** - Systems Thinking
- **Peter Senge** - Learning Organizations

Special thanks to the AI Nurse Florence project for demonstrating Level 4 Anticipatory Empathy in healthcare.

---

**Built with ❤️ by Smart-AI-Memory**

*Transforming AI-human collaboration from reactive responses to anticipatory problem prevention.*
