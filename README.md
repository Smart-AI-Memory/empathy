# Empathy

**A five-level maturity model for AI-human collaboration**

[![License](https://img.shields.io/badge/License-Fair%20Source%200.9-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/empathy.svg)](https://pypi.org/project/empathy/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/empathy.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/Smart-AI-Memory/empathy/actions/workflows/tests.yml/badge.svg)](https://github.com/Smart-AI-Memory/empathy/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/Smart-AI-Memory/empathy/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Downloads](https://img.shields.io/pypi/dm/empathy.svg)](https://pypi.org/project/empathy/)

---

## Quick Start

```bash
# Install core framework
pip install empathy

# Install with Claude Code + MemDocs transformative stack (recommended)
pip install empathy[full]

# Or install specific components:
pip install empathy[llm]      # LLM providers (Anthropic, OpenAI)
pip install empathy[memdocs]  # MemDocs integration
pip install empathy[all]      # Everything including dev tools
```

**Development installation:**
```bash
git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy
pip install -e .[dev]
```

```python
from empathy_os import EmpathyOS

os = EmpathyOS()
result = await os.collaborate("Build a secure API endpoint")
```

📖 **[Full Quick Start Guide](docs/QUICKSTART_GUIDE.md)** | **[API Reference](docs/API_REFERENCE.md)** | **[User Guide](docs/USER_GUIDE.md)**

---

## Overview

The **Empathy** is a systematic approach to building AI systems that progress from reactive responses to anticipatory problem prevention. By integrating emotional intelligence (Goleman), tactical empathy (Voss), systems thinking (Meadows, Senge), and clear reasoning (Naval Ravikant), it provides a maturity model for AI-human collaboration.

**Part of the Smart-AI-Memory ecosystem** - Designed to work seamlessly with [MemDocs](https://github.com/Smart-AI-Memory/memdocs) for intelligent document memory and retrieval, enabling AI systems to maintain long-term context and learn from interactions over time.

### 🚀 Transformative Development with Claude Code

This framework was built using **[Claude Code](https://claude.ai/claude-code)** (CLI and VS Code extension) combined with **MemDocs** and the **Empathy** itself, demonstrating the power of this integration:

**Claude Code + VS Code + MemDocs + Empathy = Level 4-5 Development**

- **Claude Code**: AI pair programming with multi-file editing, command execution, and anticipatory assistance
- **VS Code**: Professional IDE with Claude Code extension for seamless AI integration
- **MemDocs**: Long-term memory maintaining project context across sessions
- **Empathy**: Structured 5-level maturity model guiding AI behavior

**Result**: This repository was built rapidly with Claude Code providing Level 4 anticipatory suggestions (predicting needs before being asked), MemDocs maintaining architectural context, and the Empathy levels ensuring systematic quality progression. The same transformative workflow is available to you.

**Empathy**, in this context, is not about feelings—it's about:
- **Alignment**: Understanding the human's goals, context, and constraints
- **Prediction**: Anticipating future needs based on system trajectory
- **Timely Action**: Intervening at the right moment with the right support
- **Memory Integration**: Leveraging MemDocs to maintain context across sessions and learn from patterns

---

## What the Empathy Provides

A systematic approach to building AI systems with five levels of maturity:

**Included Components:**
- **16 specialized Coach software wizards** - Security, performance, testing, accessibility, and more
- **18 clinical documentation wizards** - Healthcare-specific implementations
- **LLM toolkit** - Integration with Claude, GPT-4, and other models
- **Plugin system** - Extensible architecture for custom domains
- **FastAPI backend** - REST API for analysis and orchestration
- **Pre-commit hooks** - Automated code quality checks

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
- 16 specialized software wizards for different aspects

**AI Integration:**
- LLM toolkit with Claude Sonnet 4.5 and GPT-4 support
- Async API calls with prompt caching
- Thinking mode for complex reasoning
- Multi-model fallback support

**Healthcare Domain:**
- 18 clinical documentation wizards
- SBAR, SOAP note, and assessment generators
- HIPAA-compliant patterns
- Integration points for EHR systems

**Developer Experience:**
- Works on single files or entire projects
- FastAPI backend for REST API access
- Plugin architecture for extensibility
- Pattern library for Level 5 sharing

## Development Status

**Production Ready:**
- ✅ Core framework architecture (98.83% coverage)
- ✅ LLM toolkit and provider integrations (95.45% core coverage)
- ✅ Software plugin with 16+ wizards (95.71% coverage)
- ✅ Healthcare plugin with 18+ wizards (85%+ coverage)
- ✅ Pre-commit hooks and quality tools
- ✅ **553 tests passing (63.87% overall coverage)**
- ✅ Multi-platform support (Linux, macOS, Windows)

**Test Coverage Details:**
- empathy_os/core.py: 98.83% ✅
- empathy_os/pattern_library.py: 95.43% ✅
- empathy_llm_toolkit/core.py: 95.45% ✅
- empathy_software_plugin/plugin.py: 95.71% ✅
- Healthcare monitors: 85-99% ✅
- Testing wizards: 70-75% ✅

**In Development:**
- ⚙️ Additional CLI testing (targeting 75%+ coverage)
- ⚙️ Productivity benchmarks and case studies
- ⚙️ PyPI package distribution
- ⚙️ Docker images and deployment guides

## Try It Yourself

```bash
# Clone and install
git clone https://github.com/Smart-AI-Memory/empathy.git
cd empathy
pip install -r requirements.txt

# Set up API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# Run tests (non-LLM tests don't need API key)
pytest -m "not llm"

# Run full test suite (requires API key)
pytest
```

Share your experience in [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy/discussions).

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
git clone https://github.com/Smart-AI-Memory/empathy.git
cd Empathy

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
├── wizards/                         # Clinical documentation wizards (17 files)
│   ├── sbar_wizard.py              # SBAR reports
│   ├── soap_note_wizard.py         # SOAP notes
│   ├── admission_assessment_wizard.py
│   ├── discharge_summary_wizard.py
│   └── 13 more clinical wizards...
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

**Compliance Anticipation Agent** ([agents/compliance_anticipation_agent.py](agents/compliance_anticipation_agent.py))
- Predicts regulatory audits 90+ days in advance
- Identifies compliance gaps automatically
- Generates proactive documentation
- Provides stakeholder notifications

**Trust Building Behaviors** ([agents/trust_building_behaviors.py](agents/trust_building_behaviors.py))
- Implements tactical empathy patterns
- Builds human-AI trust through transparent communication
- Uses calibrated questions to uncover hidden needs

**EPIC Integration Wizard** ([agents/epic_integration_wizard.py](agents/epic_integration_wizard.py))
- Healthcare-specific implementation
- Integrates with EPIC EHR systems
- Level 4 anticipatory empathy for clinical workflows

### 2. Coach Software Development Wizards

**16 specialized wizards** for software development with Level 4 Anticipatory Empathy:

**Security & Compliance:**
- **Security Wizard** ([coach_wizards/security_wizard.py](coach_wizards/security_wizard.py)) - SQL injection, XSS, CSRF, secrets detection
- **Compliance Wizard** ([coach_wizards/compliance_wizard.py](coach_wizards/compliance_wizard.py)) - GDPR, SOC 2, PII handling

**Performance & Scalability:**
- **Performance Wizard** ([coach_wizards/performance_wizard.py](coach_wizards/performance_wizard.py)) - N+1 queries, memory leaks, bottlenecks
- **Database Wizard** ([coach_wizards/database_wizard.py](coach_wizards/database_wizard.py)) - Missing indexes, query optimization
- **Scaling Wizard** ([coach_wizards/scaling_wizard.py](coach_wizards/scaling_wizard.py)) - Architecture limitations, load handling

**Code Quality:**
- **Refactoring Wizard** ([coach_wizards/refactoring_wizard.py](coach_wizards/refactoring_wizard.py)) - Code smells, complexity, duplication
- **Testing Wizard** ([coach_wizards/testing_wizard.py](coach_wizards/testing_wizard.py)) - Coverage analysis, flaky tests
- **Debugging Wizard** ([coach_wizards/debugging_wizard.py](coach_wizards/debugging_wizard.py)) - Null references, race conditions

**API & Integration:**
- **API Wizard** ([coach_wizards/api_wizard.py](coach_wizards/api_wizard.py)) - Design consistency, versioning
- **Migration Wizard** ([coach_wizards/migration_wizard.py](coach_wizards/migration_wizard.py)) - Deprecated APIs, compatibility

**DevOps & Operations:**
- **CI/CD Wizard** ([coach_wizards/cicd_wizard.py](coach_wizards/cicd_wizard.py)) - Pipeline optimization, deployment risks
- **Observability Wizard** ([coach_wizards/observability_wizard.py](coach_wizards/observability_wizard.py)) - Logging, metrics, tracing
- **Monitoring Wizard** ([coach_wizards/monitoring_wizard.py](coach_wizards/monitoring_wizard.py)) - Alerts, SLOs, blind spots

**User Experience:**
- **Accessibility Wizard** ([coach_wizards/accessibility_wizard.py](coach_wizards/accessibility_wizard.py)) - WCAG compliance, alt text, ARIA
- **Localization Wizard** ([coach_wizards/localization_wizard.py](coach_wizards/localization_wizard.py)) - i18n, translations, RTL

**Documentation:**
- **Documentation Wizard** ([coach_wizards/documentation_wizard.py](coach_wizards/documentation_wizard.py)) - Docstrings, examples, clarity

Each wizard implements:
- **Current Analysis**: Detect issues in code now
- **Level 4 Predictions**: Forecast issues 30-90 days ahead
- **Prevention Strategies**: Stop problems before they happen
- **Fix Suggestions**: Concrete code examples

### 3. Clinical Documentation Wizards

**18 specialized wizards** for healthcare documentation:

**Core Documentation:**
- **SBAR Wizard** ([wizards/sbar_wizard.py](wizards/sbar_wizard.py)) - Situation, Background, Assessment, Recommendation
- **SOAP Note Wizard** ([wizards/soap_note_wizard.py](wizards/soap_note_wizard.py)) - Subjective, Objective, Assessment, Plan
- **Admission Assessment** ([wizards/admission_assessment_wizard.py](wizards/admission_assessment_wizard.py))
- **Discharge Summary** ([wizards/discharge_summary_wizard.py](wizards/discharge_summary_wizard.py))
- **Shift Handoff** ([wizards/shift_handoff_wizard.py](wizards/shift_handoff_wizard.py))
- **Incident Report** ([wizards/incident_report_wizard.py](wizards/incident_report_wizard.py))

**Clinical Assessment:**
- **Clinical Assessment** ([wizards/clinical_assessment.py](wizards/clinical_assessment.py))
- **Nursing Assessment** ([wizards/nursing_assessment.py](wizards/nursing_assessment.py))

**Care Planning:**
- **Care Plan** ([wizards/care_plan.py](wizards/care_plan.py))
- **Treatment Plan** ([wizards/treatment_plan.py](wizards/treatment_plan.py))
- **Discharge Planning** ([wizards/discharge_planning.py](wizards/discharge_planning.py))

**Medication Management:**
- **Dosage Calculation** ([wizards/dosage_calculation.py](wizards/dosage_calculation.py))
- **Medication Reconciliation** ([wizards/medication_reconciliation.py](wizards/medication_reconciliation.py))

**Patient Care:**
- **Patient Education** ([wizards/patient_education.py](wizards/patient_education.py))

**Quality & Reporting:**
- **Quality Improvement** ([wizards/quality_improvement.py](wizards/quality_improvement.py))
- **SBAR Report** ([wizards/sbar_report.py](wizards/sbar_report.py))

### 4. Core Services

**Wizard AI Service** ([services/wizard_ai_service.py](services/wizard_ai_service.py))
- Orchestrates all clinical wizards
- Manages AI model selection and fallback
- Handles prompt templates and context
- Integrates with Claude, GPT-4, and other LLMs

### 5. Framework Documentation

**Technical Guide** ([docs/CHAPTER_EMPATHY_FRAMEWORK.md](docs/CHAPTER_EMPATHY_FRAMEWORK.md))
- Complete theoretical foundation
- Implementation patterns
- Code examples for each level
- Systems thinking integration

**Non-Technical Guide** ([docs/EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md](docs/EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md))
- Accessible explanation for stakeholders
- Business value and ROI
- Real-world use cases

**Teaching AI Your Philosophy** ([docs/TEACHING_AI_YOUR_PHILOSOPHY.md](docs/TEACHING_AI_YOUR_PHILOSOPHY.md))
- How to align AI systems with your values
- Collaborative prompt engineering
- Building long-term AI partnerships

### 6. Coach Integration Examples

The **Coach** project demonstrates practical implementation of Level 4 Anticipatory Empathy in IDE integrations:

- **JetBrains Plugin**: Complete IntelliJ IDEA plugin with 16 specialized wizards
- **VS Code Extension**: Full-featured extension with real-time analysis
- **LSP Server**: Language Server Protocol implementation for cross-IDE support

See [examples/coach/](examples/coach/) for complete implementations.

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
- **Examples**: See [examples/coach/](examples/coach/)

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

- 📚 **[Framework Guide](docs/CHAPTER_EMPATHY_FRAMEWORK.md)** - Complete technical documentation
- 🎓 **[Non-Technical Guide](docs/EMPATHY_FRAMEWORK_NON_TECHNICAL_GUIDE.md)** - Accessible introduction
- 🧑‍🏫 **[Teaching AI](docs/TEACHING_AI_YOUR_PHILOSOPHY.md)** - Alignment and collaboration patterns
- 💻 **[Coach Examples](examples/coach/)** - Production-ready IDE integrations

---

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](examples/coach/CONTRIBUTING.md) for details.

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

[Get Support →](https://github.com/Smart-AI-Memory/empathy/blob/main/SPONSORSHIP.md)

### Professional Services

- **Custom Wizard Development** - Domain-specific wizards for your industry
- **Training & Workshops** - Get your team productive in one day
- **Enterprise Solutions** - Hosted service, custom SLA, dedicated support

[Learn More →](SPONSORSHIP.md) | [Contact Sales →](mailto:support@smartaimemory.com)

### GitHub Sponsors

Support development directly: [Sponsor on GitHub →](https://github.com/sponsors/Smart-AI-Memory)

---

## License

This project is licensed under the **Fair Source License, version 0.9** - see the [LICENSE](LICENSE) file for details.

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

**Commercial licensing:** Email [support@smartaimemory.com](mailto:support@smartaimemory.com) | [Licensing FAQ →](LICENSE)

---

## Citation

If you use the Empathy in your research or product, please cite:

```bibtex
@software{empathy_framework_2025,
  author = {Roebuck, Patrick},
  title = {Empathy: A Five-Level Maturity Model for AI-Human Collaboration},
  year = {2025},
  publisher = {Deep Study AI, LLC},
  url = {https://github.com/Smart-AI-Memory/empathy},
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
- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)
- Issues: https://github.com/Smart-AI-Memory/empathy/issues
- Discussions: https://github.com/Smart-AI-Memory/empathy/discussions

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

[Get Support →](SPONSORSHIP.md)

### Professional Services

- **Custom Wizard Development** - Domain-specific wizards for your industry
- **Training & Workshops** - Get your team productive quickly
- **Enterprise Solutions** - Hosted service, dedicated support, custom SLA

[Learn More →](SPONSORSHIP.md)

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
