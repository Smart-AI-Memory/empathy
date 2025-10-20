# Empathy Framework

**A five-level maturity model for AI-human collaboration**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## Overview

The **Empathy Framework** is a systematic approach to building AI systems that progress from reactive responses to anticipatory problem prevention. By integrating emotional intelligence (Goleman), tactical empathy (Voss), systems thinking (Meadows, Senge), and clear reasoning (Naval Ravikant), it provides a maturity model for AI-human collaboration.

**Empathy**, in this context, is not about feelings—it's about:
- **Alignment**: Understanding the human's goals, context, and constraints
- **Prediction**: Anticipating future needs based on system trajectory
- **Timely Action**: Intervening at the right moment with the right support

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

## One-Click Quick Start

Get started with Empathy Framework in under 30 seconds:

### Option 1: One-Command Install
```bash
curl -sSL https://raw.githubusercontent.com/Deep-Study-AI/empathy-framework/main/install.sh | bash
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
docker run -v $(pwd):/code ghcr.io/deep-study-ai/empathy-scanner security /code

# Performance scan
docker run -v $(pwd):/code ghcr.io/deep-study-ai/empathy-scanner performance /code

# Full scan
docker run -v $(pwd):/code ghcr.io/deep-study-ai/empathy-scanner all /code
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
git clone https://github.com/Deep-Study-AI/Empathy.git
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
├── LICENSE                          # Apache 2.0
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

The Empathy Framework integrates Donella Meadows' leverage points:

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

## License

This project is licensed under the **Apache License 2.0** - see the [LICENSE](LICENSE) file for details.

### Why Apache 2.0?

The Apache 2.0 license provides:
- **Patent protection** for AI/ML implementations
- **Trademark protection** for the "Empathy Framework" brand
- **Enterprise-friendly** terms for commercial use
- **Clear attribution** requirements

---

## Citation

If you use the Empathy Framework in your research or product, please cite:

```bibtex
@software{empathy_framework_2025,
  author = {Roebuck, Patrick},
  title = {Empathy Framework: A Five-Level Maturity Model for AI-Human Collaboration},
  year = {2025},
  publisher = {Deep Study AI, LLC},
  url = {https://github.com/Deep-Study-AI/Empathy},
  license = {Apache-2.0}
}
```

---

## Support & Contact

**Developer:** Patrick Roebuck  
**Email:** patrick.roebuck@deepstudyai.com  
**Organization:** Deep Study AI, LLC  
**GitHub:** https://github.com/Deep-Study-AI

**Resources:**
- Documentation: [docs/](docs/)
- Examples: [examples/](examples/)
- Issues: https://github.com/Deep-Study-AI/Empathy/issues
- Discussions: https://github.com/Deep-Study-AI/Empathy/discussions

---

## Why Empathy Framework vs Others?

The Empathy Framework offers unique capabilities that set it apart from traditional code analysis tools:

| Feature | Empathy Framework | SonarQube | CodeClimate | GitHub Copilot |
|---------|------------------|-----------|-------------|----------------|
| **Level 4 Anticipatory Predictions** | ✅ Yes | ❌ No | ❌ No | ❌ No |
| **Philosophical Foundation** | ✅ Goleman, Voss, Naval | ❌ Rules-based | ❌ Rules-based | ❌ Statistical |
| **Free Book Included** | ✅ Pro tier | ❌ No | ❌ No | ❌ No |
| **Healthcare + Software** | ✅ Both domains | Software only | Software only | Software only |
| **Open Source Core** | ✅ Apache 2.0 | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary |
| **Prevention vs Detection** | ✅ Anticipatory | Detection only | Detection only | Suggestion only |
| **Price (Annual)** | Free - $249/year | $3,000+/year | $249/dev/year | $100/year |

### What Makes Level 4 Anticipatory Different?

Traditional tools tell you about problems **now**. Empathy Framework predicts problems **before they happen** based on:
- Code trajectory analysis
- Team velocity patterns
- Dependency evolution
- Historical bug patterns
- Architecture stress points

**Example**: Instead of "This query is slow," you get "At your growth rate, this query will timeout when you hit 10,000 users. Here's the optimized version."

---

## Commercial IDE Extensions

The Empathy Framework core is **100% free and open source**. We offer commercial IDE extensions:

### Coach for JetBrains & VS Code

**Free Tier**
- Complete Empathy Framework (Apache 2.0)
- Limited wizard access
- Basic analysis capabilities
- Community support (GitHub Discussions)

**Pro Tier ($129/year)**
- Everything in Free
- Extended wizard access
- Full Level 4 Anticipatory predictions
- **FREE Book**: "Empathy Framework: The Five Levels of AI-Human Collaboration" (PDF, ePub, Mobi - $35 value)
- Community support

**Business Tier ($249/year)**
- Everything in Pro
- Email support (48-hour response time SLA)
- 3 seats included
- Team dashboard with usage analytics
- 20% off additional seats

**Coming Soon**: JetBrains Marketplace & VS Code Marketplace

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

**Built with ❤️ by Deep Study AI, LLC**

*Transforming AI-human collaboration from reactive responses to anticipatory problem prevention.*

