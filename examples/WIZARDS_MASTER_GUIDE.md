# Empathy Framework Wizard Examples - Master Guide

**Comprehensive collection of all wizard examples across three categories**

Version: 1.8.0-alpha
Last Updated: 2025-11-25
Status: Production-Ready

---

## 📚 Table of Contents

- [Overview](#overview)
- [Three Wizard Categories](#three-wizard-categories)
- [Quick Start](#quick-start)
- [Directory Structure](#directory-structure)
- [Complete Wizard Index](#complete-wizard-index)
- [Running Examples](#running-examples)
- [Testing](#testing)
- [Compliance Matrix](#compliance-matrix)
- [Best Practices](#best-practices)

---

## Overview

This is the **master project** for all Empathy Framework wizard examples. The wizards are organized into three categories:

1. **Domain/Industry Wizards** (16 total) - HIPAA, SOX, FERPA compliant
2. **Coach/Software Development Wizards** (16 total) - Agile development support
3. **AI/Software Wizards** (12 total) - Level 4 Anticipatory intelligence

**Total: 44+ Production-Ready AI Wizards**

---

## Three Wizard Categories

### 1. Domain/Industry Wizards (`examples/domain_wizards/`)

**Purpose:** Industry-specific AI assistants with built-in compliance

**Empathy Level:** 3-4 (Proactive to Anticipatory)

**Key Features:**
- Domain-specific PII detection and scrubbing
- Automatic compliance verification (HIPAA, SOX, PCI-DSS, FERPA, etc.)
- Mandatory encryption for SENSITIVE data
- Industry-specific system prompts and knowledge
- Configurable retention policies

**16 Wizards:**
- Healthcare (HIPAA §164.312)
- Finance (SOX §802, PCI-DSS v4.0)
- Legal (Fed. Rules 502)
- Education (FERPA)
- Customer Support
- HR (EEOC)
- Sales (CAN-SPAM, GDPR)
- Real Estate (Fair Housing)
- Insurance
- Accounting (SOX, IRS)
- Research (IRB 45 CFR 46)
- Government (FISMA, Privacy Act)
- Retail (PCI-DSS)
- Manufacturing (ISO)
- Logistics
- Technology (SOC2, ISO 27001)

**Quick Start:**
```bash
export ANTHROPIC_API_KEY="your-api-key"
python examples/domain_wizards/all_domain_wizards_demo.py
```

**Documentation:** [16_WIZARDS_COMPLETE.md](../16_WIZARDS_COMPLETE.md), [HEALTHCARE_WIZARD_COMPLETE.md](../HEALTHCARE_WIZARD_COMPLETE.md)

---

### 2. Coach/Software Development Wizards (`examples/coach/`)

**Purpose:** Agile software development lifecycle support

**Empathy Level:** 3-5 (Proactive to Transformative)

**Key Features:**
- Multi-wizard collaboration and shared learning
- Software development best practices
- Agile workflow integration
- Pattern recognition and reuse
- Team onboarding and knowledge transfer

**16 Wizards:**
- Debugging Wizard
- Documentation Wizard
- Design Review Wizard
- Testing Wizard
- Performance Wizard
- Security Wizard
- Refactoring Wizard
- Database Wizard
- API Wizard
- Compliance Wizard
- Monitoring Wizard
- Localization Wizard
- DevOps Wizard
- Accessibility Wizard
- Onboarding Wizard
- Retrospective Wizard

**Quick Start:**
```bash
python examples/coach/demo_all_wizards.py
```

**Documentation:** Coach wizards demonstrate multi-agent collaboration with shared learning patterns.

---

### 3. AI/Software Wizards (`examples/ai_wizards/`)

**Purpose:** Level 4 Anticipatory intelligence for AI/ML development

**Empathy Level:** 4 (Anticipatory - predicts issues 30-90 days out)

**Key Features:**
- Predicts issues before they compound
- Learns from experience and shares patterns
- Identifies non-obvious problems (performance, cost, complexity)
- Actionable recommendations based on real-world patterns
- Continuous learning and improvement

**12 Wizards:**
- Multi-Model Coordination
- Performance Profiling
- AI Collaboration
- Advanced Debugging
- Agent Orchestration
- RAG Pattern Design
- Testing Wizard
- Enhanced Testing
- AI Documentation
- Prompt Engineering
- AI Context Management
- Security Analysis

**Quick Start:**
```bash
python examples/ai_wizards/all_ai_wizards_demo.py
```

**Documentation:** Each wizard includes learned patterns from production AI systems.

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/empathy-framework
cd empathy-framework

# Install dependencies
pip install -r requirements.txt

# Set up API key (for domain wizards)
export ANTHROPIC_API_KEY="your-api-key"

# Optional: Set up security (for production)
export EMPATHY_MASTER_KEY="your-encryption-key"
```

### Run All Wizards

```bash
# Domain/Industry Wizards
python examples/domain_wizards/all_domain_wizards_demo.py

# Coach/Software Development Wizards
python examples/coach/demo_all_wizards.py

# AI/Software Wizards
python examples/ai_wizards/all_ai_wizards_demo.py
```

### Run Individual Wizard

```bash
# Healthcare wizard example
python examples/domain_wizards/healthcare_example.py

# Debugging wizard
python examples/coach/wizards/debugging_wizard.py

# Multi-model wizard
python examples/ai_wizards/multi_model_example.py
```

---

## Directory Structure

```
empathy-framework/
├── examples/
│   ├── WIZARDS_MASTER_GUIDE.md        # This file
│   │
│   ├── domain_wizards/                # Industry/Domain Wizards (16)
│   │   ├── all_domain_wizards_demo.py # Comprehensive demo
│   │   ├── healthcare_example.py      # HIPAA-compliant healthcare
│   │   ├── finance_example.py         # SOX/PCI-DSS finance
│   │   ├── ... (individual examples)
│   │   └── tests/
│   │       ├── test_healthcare_wizard.py
│   │       └── ... (wizard tests)
│   │
│   ├── coach/                         # Software Development Wizards (16)
│   │   ├── demo_all_wizards.py        # Comprehensive demo
│   │   ├── coach.py                   # Main coach interface
│   │   ├── shared_learning.py         # Pattern sharing
│   │   ├── wizards/
│   │   │   ├── debugging_wizard.py
│   │   │   ├── testing_wizard.py
│   │   │   ├── ... (16 wizards)
│   │   └── tests/
│   │       ├── test_all_wizards.py
│   │       ├── test_new_wizards.py
│   │       └── test_coach_wizards.py
│   │
│   └── ai_wizards/                    # AI/Software Wizards (12)
│       ├── all_ai_wizards_demo.py     # Comprehensive demo
│       ├── multi_model_example.py     # Multi-model coordination
│       ├── rag_pattern_example.py     # RAG design patterns
│       ├── ... (individual examples)
│       └── tests/
│           ├── test_ai_wizards.py
│           ├── test_performance_wizard.py
│           └── test_security_wizard.py
│
├── empathy_llm_toolkit/
│   └── wizards/                       # Domain wizard implementations
│       ├── base_wizard.py
│       ├── healthcare_wizard.py
│       ├── finance_wizard.py
│       └── ... (16 total)
│
├── coach_wizards/                     # Coach wizard implementations
│   ├── base_wizard.py
│   ├── debugging_wizard.py
│   └── ... (16 total)
│
└── empathy_software_plugin/
    └── wizards/                       # AI wizard implementations
        ├── multi_model_wizard.py
        ├── rag_pattern_wizard.py
        └── ... (12 total)
```

---

## Complete Wizard Index

### Domain/Industry Wizards (16)

| Wizard | Domain | Compliance | Classification | Retention | Example |
|--------|--------|------------|----------------|-----------|---------|
| Healthcare | Medical | HIPAA §164.312 | SENSITIVE | 90 days | `healthcare_example.py` |
| Finance | Banking | SOX §802, PCI-DSS | SENSITIVE | 7 years | `finance_example.py` |
| Legal | Law | Fed. Rules 502 | SENSITIVE | 7 years | `legal_example.py` |
| Education | Academic | FERPA | SENSITIVE | 5 years | `education_example.py` |
| Customer Support | Service | Consumer Privacy | INTERNAL | 2 years | `customer_support_example.py` |
| HR | Human Resources | EEOC | SENSITIVE | 7 years | `hr_example.py` |
| Sales | Revenue | CAN-SPAM, GDPR | INTERNAL | 3 years | `sales_example.py` |
| Real Estate | Property | Fair Housing | INTERNAL | 7 years | `real_estate_example.py` |
| Insurance | Risk | State Regulations | SENSITIVE | 7 years | `insurance_example.py` |
| Accounting | Finance | SOX §802, IRS | SENSITIVE | 7 years | `accounting_example.py` |
| Research | Academic | IRB 45 CFR 46 | SENSITIVE | 7 years | `research_example.py` |
| Government | Public Sector | FISMA, Privacy Act | SENSITIVE | 7 years | `government_example.py` |
| Retail | E-commerce | PCI-DSS v4.0 | SENSITIVE | 2 years | `retail_example.py` |
| Manufacturing | Production | ISO Standards | INTERNAL | 5 years | `manufacturing_example.py` |
| Logistics | Supply Chain | Transportation | INTERNAL | 2 years | `logistics_example.py` |
| Technology | DevOps | SOC2, ISO 27001 | INTERNAL | 1 year | `technology_example.py` |

### Coach/Software Development Wizards (16)

| Wizard | Purpose | Empathy Level | Key Features |
|--------|---------|---------------|--------------|
| Debugging | Bug resolution | 4 | Root cause analysis, pattern recognition |
| Documentation | Knowledge capture | 3 | Auto-generation, gap detection |
| Design Review | Architecture | 5 | Trade-off analysis, ADR generation |
| Testing | Quality assurance | 4 | Coverage analysis, test prioritization |
| Performance | Optimization | 4 | Bottleneck detection, profiling |
| Security | Vulnerability | 4 | Threat modeling, compliance |
| Refactoring | Code quality | 3 | Smell detection, improvement suggestions |
| Database | Data layer | 3 | Schema design, query optimization |
| API | Interface design | 3 | REST/GraphQL best practices |
| Compliance | Regulatory | 4 | GDPR, SOC2, HIPAA guidance |
| Monitoring | Observability | 4 | Metrics, alerting, SLOs |
| Localization | i18n/l10n | 3 | Translation, cultural adaptation |
| DevOps | CI/CD | 4 | Pipeline design, automation |
| Accessibility | a11y | 3 | WCAG compliance, inclusive design |
| Onboarding | Team growth | 3 | Knowledge transfer, ramp-up |
| Retrospective | Team learning | 5 | Pattern extraction, improvement |

### AI/Software Wizards (12)

| Wizard | Purpose | Prediction Focus |
|--------|---------|------------------|
| Multi-Model Coordination | Model management | Coordination overhead, cost explosion |
| Performance Profiling | Optimization | Degradation patterns, bottlenecks |
| AI Collaboration | Multi-agent | Agent conflicts, state management |
| Advanced Debugging | Error resolution | Bug patterns, root causes |
| Agent Orchestration | Workflow | Orchestration failures, deadlocks |
| RAG Pattern Design | Retrieval | Quality degradation, relevance issues |
| Testing Wizard | QA | Test gaps, flakiness |
| Enhanced Testing | Advanced QA | Test suite bottlenecks |
| AI Documentation | Knowledge | Documentation gaps, onboarding issues |
| Prompt Engineering | LLM optimization | Prompt quality, version control |
| AI Context Management | Token optimization | Context window issues, truncation |
| Security Analysis | AI security | Injection attacks, PII leaks |

---

## Running Examples

### Prerequisites

```bash
# Python 3.8+
python --version

# Install dependencies
pip install -r requirements.txt

# Set API keys (for domain wizards)
export ANTHROPIC_API_KEY="your-key"

# Optional: Enable security features
export EMPATHY_MASTER_KEY="your-encryption-key"
```

### Run Comprehensive Demos

```bash
# All domain wizards (requires API key)
python examples/domain_wizards/all_domain_wizards_demo.py

# All coach wizards
python examples/coach/demo_all_wizards.py

# All AI wizards
python examples/ai_wizards/all_ai_wizards_demo.py
```

### Run Individual Examples

```bash
# Healthcare wizard with HIPAA compliance
python examples/domain_wizards/healthcare_example.py

# Debugging wizard for production issues
python examples/coach/wizards/debugging_wizard.py

# RAG pattern design analysis
python examples/ai_wizards/rag_pattern_example.py
```

---

## Testing

### Run All Tests

```bash
# All wizard tests
pytest examples/ -v

# Domain wizard tests
pytest examples/domain_wizards/tests/ -v

# Coach wizard tests
pytest examples/coach/tests/ -v

# AI wizard tests
pytest examples/ai_wizards/tests/ -v
```

### Run Specific Test Suites

```bash
# Healthcare wizard (HIPAA compliance)
pytest examples/domain_wizards/tests/test_healthcare_wizard.py -v

# Coach wizards (all 16)
pytest examples/coach/tests/test_all_wizards.py -v

# AI wizards (performance, security)
pytest examples/ai_wizards/tests/test_performance_wizard.py -v
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=empathy_llm_toolkit.wizards \
       --cov=coach_wizards \
       --cov=empathy_software_plugin.wizards \
       --cov-report=html \
       examples/
```

---

## Compliance Matrix

### Regulatory Compliance Coverage

| Regulation | Wizards | Key Requirements | Verification Method |
|------------|---------|------------------|---------------------|
| **HIPAA §164.312** | Healthcare | PHI de-identification, encryption, audit logging | `wizard.get_hipaa_compliance_status()` |
| **SOX §802** | Finance, Accounting | 7-year retention, audit controls | `wizard.get_sox_compliance_status()` |
| **PCI-DSS v4.0** | Finance, Retail | Payment data protection, encryption | `wizard.get_pci_compliance_status()` |
| **FERPA** | Education | Student privacy, consent management | `wizard.get_ferpa_compliance_status()` |
| **FISMA** | Government | Security controls, NIST framework | `wizard.get_fisma_compliance_status()` |
| **IRB 45 CFR 46** | Research | Participant protection, informed consent | `wizard.get_irb_compliance_status()` |
| **GDPR** | Sales, Customer Support | Data subject rights, consent | `wizard.get_gdpr_compliance_status()` |

### Security Features (All Wizards)

- ✅ **PII Detection:** Domain-specific + standard patterns
- ✅ **Secrets Detection:** API keys, credentials, tokens
- ✅ **Encryption:** AES-256-GCM for SENSITIVE data
- ✅ **Audit Logging:** Comprehensive interaction trail
- ✅ **Access Control:** User ID tracking, authentication
- ✅ **Data Classification:** PUBLIC, INTERNAL, SENSITIVE

---

## Best Practices

### 1. Domain Wizards

**Always enable security for production:**
```python
llm = EmpathyLLM(
    provider="anthropic",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    enable_security=True,  # REQUIRED
)
```

**Verify compliance programmatically:**
```python
wizard = HealthcareWizard(llm)
status = wizard.get_hipaa_compliance_status()

if not status['compliant']:
    for rec in status['recommendations']:
        print(f"⚠️  {rec}")
```

**Use appropriate classification:**
- SENSITIVE: Healthcare, Finance, Legal, HR
- INTERNAL: Sales, Customer Support, Technology
- PUBLIC: General documentation (after PII scrubbing)

### 2. Coach Wizards

**Enable multi-wizard collaboration:**
```python
coach = Coach()
result = coach.process(task, multi_wizard=True)
```

**Share patterns across team:**
```python
learning = get_shared_learning()
learning.contribute_pattern(
    wizard_name="DebuggingWizard",
    pattern_type="null_pointer_fix",
    description="Add null guard and default config",
    code="if config is None: config = get_default()",
    tags=["debugging", "null", "config"],
)
```

### 3. AI Wizards

**Review predictions weekly:**
```python
wizard = PerformanceProfilingWizard()
result = await wizard.analyze(context)

for prediction in result['predictions']:
    if prediction['likelihood'] > 0.7:
        # High-probability issue - act now
        implement_recommendation(prediction)
```

**Configure context collection:**
```python
context = {
    "project_path": "/project",
    "recent_changes": ["added_ml_inference"],
    "current_metrics": {
        "avg_response_time": 850,
        "p95_response_time": 2100,
    },
    "baseline_metrics": {
        "avg_response_time": 120,
        "p95_response_time": 250,
    },
}
```

---

## Additional Resources

### Documentation Files
- [16_WIZARDS_COMPLETE.md](../16_WIZARDS_COMPLETE.md) - Domain wizards overview
- [HEALTHCARE_WIZARD_COMPLETE.md](../HEALTHCARE_WIZARD_COMPLETE.md) - HIPAA compliance deep dive
- [SECURE_MEMORY_ARCHITECTURE.md](../SECURE_MEMORY_ARCHITECTURE.md) - Security architecture
- [WEEK2_EXECUTION_PLAN.md](../WEEK2_EXECUTION_PLAN.md) - Development roadmap

### Example Projects
- `examples/domain_wizards/` - Industry-specific examples
- `examples/coach/` - Software development examples
- `examples/ai_wizards/` - AI/ML development examples

### API Documentation
- Domain Wizards: See `empathy_llm_toolkit/wizards/`
- Coach Wizards: See `coach_wizards/`
- AI Wizards: See `empathy_software_plugin/wizards/`

---

## Contributing

### Adding New Wizard Examples

1. **Choose category:**
   - Domain: Industry-specific, compliance-focused
   - Coach: Software development lifecycle
   - AI: Level 4 anticipatory intelligence

2. **Create example file:**
   ```bash
   # Domain wizard
   examples/domain_wizards/[wizard]_example.py

   # Coach wizard
   examples/coach/wizards/[wizard]_wizard.py

   # AI wizard
   examples/ai_wizards/[wizard]_example.py
   ```

3. **Add tests:**
   ```bash
   # Domain wizard test
   examples/domain_wizards/tests/test_[wizard].py

   # Coach wizard test
   examples/coach/tests/test_[wizard].py

   # AI wizard test
   examples/ai_wizards/tests/test_[wizard].py
   ```

4. **Update this guide:**
   - Add to wizard index
   - Update quick start if needed
   - Document compliance requirements

---

## Support

**Questions or Issues:**
- GitHub Issues: https://github.com/your-org/empathy-framework/issues
- Security: security-team@company.com
- HIPAA Compliance: hipaa-officer@company.com
- General: empathy-framework@company.com

**Version History:**
- v1.8.0-alpha: Initial wizard collection (44 wizards)
- v1.7.1: Security integration
- v1.7.0: Claude Memory integration

---

**Last Updated:** 2025-11-25
**Maintained By:** Empathy Framework Team
**License:** Fair Source 0.9

*This is the master guide for all Empathy Framework wizard examples.*
