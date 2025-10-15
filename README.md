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
├── wizards/                         # Clinical documentation wizards (18 files)
│   ├── sbar_wizard.py              # SBAR reports
│   ├── soap_note_wizard.py         # SOAP notes
│   ├── admission_assessment_wizard.py
│   ├── discharge_summary_wizard.py
│   ├── shift_handoff_wizard.py
│   ├── incident_report_wizard.py
│   ├── clinical_assessment.py
│   ├── patient_education.py
│   ├── quality_improvement.py
│   └── 9 more clinical wizards...
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

### 2. Clinical Documentation Wizards

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

### 3. Core Services

**Wizard AI Service** ([services/wizard_ai_service.py](services/wizard_ai_service.py))
- Orchestrates all clinical wizards
- Manages AI model selection and fallback
- Handles prompt templates and context
- Integrates with Claude, GPT-4, and other LLMs

### 4. Framework Documentation

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

### 5. Coach Integration Examples

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

