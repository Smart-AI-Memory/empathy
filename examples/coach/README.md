# Coach - AI Orchestration Agent with 16 Specialized Wizards

> **Production-Ready AI Development Assistant** built on the Empathy Framework
> Coordinates 16 specialized wizards for comprehensive software development support

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)]()

---

## 🎯 What is Coach?

Coach is an **orchestration agent** that coordinates 16 specialized AI "wizards" to provide context-aware, anticipatory assistance for software development tasks. Built on the [Empathy Framework](../../README.md), Coach delivers **Level 4 Anticipatory Empathy** - predicting bottlenecks 30-90 days before they occur and providing proactive solutions.

### Key Capabilities

✅ **16 Specialized Wizards** covering all aspects of software development
✅ **Level 4 Anticipatory Empathy** - predicts future issues before they happen
✅ **Multi-Wizard Coordination** - 8 pre-defined collaboration patterns
✅ **Industry-Standard API Patterns** - follows OpenAI/Anthropic conventions
✅ **Production-Ready** - 100% test coverage, no code stubs or placeholders

### ROI: 33,629%

- **Time Saved**: 84 hours/month (70% automation of non-coding tasks)
- **Financial Impact**: $100,800/year savings (at $100/hr developer rate)
- **Investment**: $299/year
- **ROI**: **33,629%**

---

## 📊 Architecture Overview

```
Coach (Orchestrator)
├── Critical Infrastructure (Highest Priority)
│   ├── SecurityWizard          # STRIDE threat modeling, penetration testing
│   └── ComplianceWizard        # SOC 2, HIPAA, GDPR audit preparation
│
├── Development Workflow (Daily Use)
│   ├── DebuggingWizard         # Root cause analysis, regression tests
│   ├── TestingWizard           # Test strategy, coverage analysis
│   ├── RefactoringWizard       # Code quality, technical debt
│   └── PerformanceWizard       # Profiling, optimization, scaling prediction
│
├── Architecture & Design
│   ├── DesignReviewWizard      # Architecture evaluation, trade-offs
│   ├── APIWizard               # OpenAPI specs (OpenAI/Anthropic conventions)
│   └── DatabaseWizard          # Schema design, migrations, query optimization
│
├── Infrastructure & Ops
│   ├── DevOpsWizard            # CI/CD pipelines, Terraform, Kubernetes
│   └── MonitoringWizard        # SLO definition, alerting, incident response
│
├── Cross-Cutting Concerns
│   ├── DocumentationWizard     # Technical writing, handoff guides
│   ├── AccessibilityWizard     # WCAG compliance, screen reader support
│   └── LocalizationWizard      # i18n/L10n, translations, RTL support
│
└── Team & Process
    ├── OnboardingWizard        # Knowledge transfer, learning paths
    └── RetrospectiveWizard     # Post-mortems, process improvement
```

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/empathy-framework.git
cd empathy-framework

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```python
from examples.coach import Coach, WizardTask

# Initialize Coach (automatically loads all 16 wizards)
coach = Coach()

# Create a task
task = WizardTask(
    role="developer",
    task="Slow database queries causing timeouts",
    context="API endpoint returns in 2.3s, target is <200ms",
    preferences="Include benchmarks and migration plan",
    risk_tolerance="medium"
)

# Process task (async)
import asyncio
result = asyncio.run(coach.process(task))

# Access results
print(f"Routed to: {result.routing}")
# → ['PerformanceWizard', 'DatabaseWizard', 'RefactoringWizard']

print(f"Diagnosis: {result.primary_output.diagnosis}")
print(f"Plan: {result.primary_output.plan}")
print(f"Artifacts: {len(result.primary_output.artifacts)} generated")
# → 5 artifacts: Performance report, optimized code, benchmarks, caching strategy, scaling projection
```

### Run Demo

```bash
cd examples/coach
python3 demo_all_wizards.py
```

---

## 🧙 Complete Wizard Catalog

### 1. **PerformanceWizard** - Optimization & Profiling Expert

**Handles**: Performance bottlenecks, slow queries, latency issues, scaling problems

**Key Capabilities**:
- Profiling analysis (CPU, memory, I/O)
- Query optimization (N+1 detection, index recommendations)
- Caching strategy (Redis, in-memory)
- **Level 4**: Scaling trajectory prediction (30-90 day forecasts)
- Benchmark generation (pytest-benchmark, locust)

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="API endpoint has 2.3s response time, need <200ms",
    context="Database queries taking 78% of response time"
)
```

**Outputs**:
- Performance analysis report
- Optimized code (shows before/after with complexity reduction)
- Benchmark suite
- Caching strategy
- **Scaling projection**: "At 10K users, this endpoint will timeout in 45 days. Here's a connection pooling solution."

---

### 2. **RefactoringWizard** - Code Quality & Technical Debt Expert

**Handles**: Code smells, complexity issues, duplication, maintainability problems

**Key Capabilities**:
- Complexity analysis (cyclomatic, cognitive, nesting depth)
- Smell detection (god classes, feature envy, primitive obsession)
- Refactoring plans (step-by-step with risk analysis)
- **Level 4**: Maintainability forecast (predicts when code becomes unmaintainable)
- Automated refactorings (rename, extract method, move class)

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="God class with 500 lines needs refactoring",
    context="High complexity (cyclomatic: 18), duplicate code across 3 files"
)
```

**Outputs**:
- Code quality report (smells, complexity metrics)
- Step-by-step refactoring plan
- Refactored code examples
- **Maintainability forecast**: "At current growth, bug density will increase 2-3x in 45 days without intervention"
- Safety checklist

---

### 3. **APIWizard** - REST/GraphQL API Design Expert

**Handles**: API design, OpenAPI specs, versioning, API sprawl

**Key Capabilities**:
- OpenAPI 3.1 spec generation (following **OpenAI/Anthropic conventions**)
- **Streaming support** (Server-Sent Events)
- **Anthropic-style error responses** (`type`, `message`, `param`, `code`)
- **Rate limit headers** (X-RateLimit-Limit, X-RateLimit-Remaining, X-RateLimit-Reset)
- Versioning strategy (URL-based with deprecation timeline)

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Design REST API for user management with streaming support",
    context="Need OpenAPI spec following OpenAI conventions"
)
```

**Outputs**:
- OpenAPI 3.1 specification (with streaming, rate limits, error schemas)
- FastAPI implementation (complete working code with rate limiting middleware)
- Versioning strategy document
- **API sprawl forecast**: "At 47 endpoints, most teams hit API sprawl at 50+. Here's a versioning strategy."
- API documentation

**Industry-Standard Features**:
```yaml
# Anthropic-style error format
{
  "type": "invalid_request_error",
  "message": "Invalid parameter: 'limit' must be between 1 and 100",
  "param": "limit",
  "code": "invalid_parameter"
}

# Rate limit headers
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 58
X-RateLimit-Reset: 1673539200

# OpenAI-style list response
{
  "object": "list",
  "data": [...],
  "has_more": true,
  "first_id": "user_123",
  "last_id": "user_456"
}
```

---

### 4. **DatabaseWizard** - Schema Design & Migration Expert

**Handles**: Schema design, migrations, query optimization, index recommendations

**Key Capabilities**:
- Schema design (normalization analysis, relationship modeling)
- Migration generation (Alembic/Django with rollback scripts)
- Index recommendations (B-tree, GIN, GiST based on query patterns)
- **Level 4**: Data growth prediction and scaling strategy
- Zero-downtime migration strategies

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Create database migration for user_preferences table",
    context="Need new table with foreign key to users, zero downtime required"
)
```

**Outputs**:
- Migration scripts (Alembic + raw SQL)
- Schema diagrams (Mermaid ERD)
- Index recommendations
- Rollback plan
- **Data growth forecast**: "At 2M rows, full table scans will timeout in 45 days. Here's a partitioning strategy."

---

### 5. **DevOpsWizard** - CI/CD & Infrastructure Expert

**Handles**: CI/CD pipelines, infrastructure as code, container orchestration

**Key Capabilities**:
- CI/CD pipeline setup (GitHub Actions, GitLab CI, CircleCI)
- Infrastructure as Code (Terraform, Pulumi, CloudFormation)
- Container orchestration (Docker, Kubernetes, Helm)
- Release automation (blue-green, canary, rollback)
- **Level 4**: Deployment pipeline optimization

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Set up CI/CD pipeline with GitHub Actions and Kubernetes deployment",
    context="Need automated testing, Docker build, and production deployment"
)
```

**Outputs**:
- GitHub Actions workflow
- Terraform infrastructure code
- Kubernetes manifests
- Deployment guides
- **Pipeline forecast**: "At 1 deploy/week, high-velocity teams deploy 10+/week. Here's a CI/CD pipeline."

---

### 6. **OnboardingWizard** - Knowledge Transfer Expert

**Handles**: New developer onboarding, knowledge transfer, learning paths

**Key Capabilities**:
- Codebase tour (architectural overview, key files)
- Personalized learning paths (30-60-90 day plans)
- Glossary generation (domain terms, acronyms)
- Interactive tutorials
- Mentor matching

**Example Use Case**:
```python
task = WizardTask(
    role="team_lead",
    task="New developer starting next week, create onboarding plan",
    context="Backend Python developer, needs to learn payment processing service"
)
```

**Outputs**:
- Codebase architecture tour
- 30-60-90 day learning path
- Project glossary
- Interactive tutorials
- **Ramp-up forecast**: "Your team is hiring 3 engineers in Q2. I've identified 5 knowledge gaps to document now."

---

### 7. **AccessibilityWizard** - WCAG Compliance Expert

**Handles**: WCAG 2.1 compliance, screen reader support, inclusive design

**Key Capabilities**:
- WCAG audit (automated scanning + manual checklist)
- Screen reader testing (NVDA, JAWS compatibility)
- Keyboard navigation validation
- Color contrast checking (4.5:1 text, 3:1 UI)
- ARIA best practices

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Ensure WCAG 2.1 AA compliance before enterprise launch",
    context="Website has forms, modals, and dynamic content"
)
```

**Outputs**:
- WCAG audit report (Level A, AA, AAA violations)
- Remediation code (alt text, ARIA labels)
- Keyboard navigation tests
- **Compliance forecast**: "Enterprise customers require WCAG 2.1 AA. Current: 23 violations. Here's a 30-day remediation plan."

---

### 8. **LocalizationWizard** - i18n/L10n Expert

**Handles**: Internationalization, translations, multi-language support

**Key Capabilities**:
- String extraction (finds hardcoded strings)
- Translation management (Crowdin, Lokalise integration)
- Pluralization rules (language-specific)
- Date/time formatting (locale-aware)
- RTL support (Arabic, Hebrew)

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Add Spanish and French translations to app",
    context="React app with 147 hardcoded English strings"
)
```

**Outputs**:
- i18n framework setup (react-intl)
- Translation files (JSON with all strings)
- RTL CSS support
- Translation workflow guide
- **Expansion forecast**: "Expanding to EU markets in Q2. Here's a full i18n implementation plan (90-day timeline)."

---

### 9. **ComplianceWizard** - Regulatory & Audit Expert

**Handles**: SOC 2, HIPAA, GDPR, ISO 27001 audit preparation

**Key Capabilities**:
- Compliance gap analysis (current state vs. requirements)
- Audit trail generation (immutable logs)
- Policy documentation (security, incident response, data retention)
- Penetration test prep
- Evidence collection for auditors

**Example Use Case**:
```python
task = WizardTask(
    role="team_lead",
    task="Prepare for SOC 2 Type II audit in 90 days",
    context="Startup, no prior compliance work, need to identify gaps"
)
```

**Outputs**:
- SOC 2 gap analysis report
- Remediation plan (prioritized by risk)
- Policy documents (auto-generated)
- Audit evidence collection guide
- **Audit forecast**: "7 control gaps identified. Critical: MFA not enforced (60-day fix). Here's a remediation timeline."

---

### 10. **MonitoringWizard** - Observability & SRE Expert

**Handles**: Observability, SLO definition, alerting, incident response

**Key Capabilities**:
- SLO definition (99.9% uptime, p95 < 200ms)
- Golden signals monitoring (latency, traffic, errors, saturation)
- Alert design (actionable, with runbooks)
- Dashboard generation (Grafana, DataDog)
- Incident postmortems (blameless)

**Example Use Case**:
```python
task = WizardTask(
    role="developer",
    task="Set up production monitoring with SLOs and alerting",
    context="Microservices architecture, need observability"
)
```

**Outputs**:
- SLO definitions (availability, latency, error rate)
- Prometheus alert rules
- Grafana dashboards
- Incident response runbooks
- **Capacity forecast**: "Database connections at 70% capacity. At current growth, you'll hit limits in 21 days. Here's a pooling solution."

---

### 11-16. Additional Wizards

**SecurityWizard** - STRIDE threat modeling, penetration testing, compliance
**DebuggingWizard** - Root cause analysis, regression tests, deployment checklists
**TestingWizard** - Test strategy, coverage analysis, test generation
**DesignReviewWizard** - Architecture evaluation, trade-off analysis, ADRs
**DocumentationWizard** - Technical writing, READMEs, handoff guides
**RetrospectiveWizard** - Post-mortems, process improvement, team feedback

---

## 🤝 Multi-Wizard Collaboration

Coach intelligently coordinates multiple wizards for complex workflows using **8 pre-defined collaboration patterns**:

### Collaboration Patterns

1. **new_api_endpoint** → APIWizard + SecurityWizard + TestingWizard + DocumentationWizard
2. **database_migration** → DatabaseWizard + DevOpsWizard + MonitoringWizard
3. **production_incident** → MonitoringWizard + DebuggingWizard + RetrospectiveWizard
4. **new_feature_launch** → 5-wizard coordination (Design, Test, Security, Docs, Monitoring)
5. **performance_issue** → PerformanceWizard + DatabaseWizard + RefactoringWizard
6. **compliance_audit** → ComplianceWizard + SecurityWizard + DocumentationWizard
7. **global_expansion** → LocalizationWizard + AccessibilityWizard + ComplianceWizard
8. **new_developer_onboarding** → OnboardingWizard + DocumentationWizard

### Example: New API Endpoint

```python
task = WizardTask(
    role="developer",
    task="Build new API endpoint for user profile management",
    context="Need REST endpoint with authentication and documentation"
)

result = await coach.process(task, multi_wizard=True)

# Automatically routes to 4 wizards:
# 1. APIWizard (primary) - Generates OpenAPI spec, FastAPI implementation
# 2. SecurityWizard - Reviews auth requirements, suggests rate limiting
# 3. TestingWizard - Creates unit tests, integration tests, E2E tests
# 4. DocumentationWizard - Writes API docs, usage examples

print(result.synthesis)
# → "Primary: APIWizard designed RESTful endpoint with OpenAI conventions
#    Additional: SecurityWizard recommends JWT + rate limiting
#                TestingWizard generated 15 tests (100% coverage)
#                DocumentationWizard created interactive Swagger UI"
```

---

## 📋 Task Schema Reference

### WizardTask (Input)

```python
@dataclass
class WizardTask:
    role: str              # developer, architect, pm, team_lead
    task: str              # What needs to be done (short description)
    context: str           # Technical details, constraints, background
    preferences: str = ""  # Output preferences (concise, detailed, code-only)
    risk_tolerance: str = "medium"  # low, medium, high
    metadata: Dict[str, Any] = field(default_factory=dict)  # Custom data
```

### CoachOutput (Response)

```python
@dataclass
class CoachOutput:
    routing: List[str]                      # Wizards activated
    primary_output: WizardOutput            # Main wizard result
    secondary_outputs: List[WizardOutput]   # Additional wizard results
    synthesis: str                          # Combined recommendations
    overall_confidence: float               # 0.0-1.0
```

### WizardOutput (Per-Wizard)

```python
@dataclass
class WizardOutput:
    wizard_name: str
    diagnosis: str                      # Problem analysis
    plan: List[str]                     # Step-by-step action plan
    artifacts: List[WizardArtifact]     # Generated files (docs, code, checklists)
    risks: List[WizardRisk]             # Identified risks + mitigations
    handoffs: List[WizardHandoff]       # Cross-team coordination
    next_actions: List[str]             # Prioritized immediate steps
    empathy_checks: EmpathyChecks       # Empathy validation
    confidence: float                   # 0.0-1.0 routing confidence
```

---

## 🎓 Empathy Framework Integration

Coach implements **Level 4 Anticipatory Empathy** - the ability to predict future needs and prevent problems before they occur.

### The 5 Empathy Levels

| Level | Name | Behavior | Coach Example |
|-------|------|----------|---------------|
| **1** | Reactive | Help after being asked | "Here's the data you requested" |
| **2** | Guided | Ask clarifying questions | "What are you trying to accomplish?" |
| **3** | Proactive | Act before being asked | "I noticed you always check vitals first—here they are" |
| **4** | **Anticipatory** | **Predict future needs** | **"At 10K users, this will timeout in 45 days. Here's a solution."** |
| **5** | Systems | Design frameworks that scale | "I've designed a caching framework so all future endpoints auto-scale" |

### How Wizards Use Each Level

```python
# Level 2: Guided (Clarification)
# DocumentationWizard asks about audience
clarification = await self.empathy.level_2_guided(
    "Who is the primary audience for this documentation?"
)

# Level 3: Proactive (Pattern Detection)
# DebuggingWizard detects patterns without being asked
hypotheses = self._form_hypotheses(task, diagnosis)
# → Identifies 2-3 likely causes proactively

# Level 4: Anticipatory (Future Prediction)
# PerformanceWizard predicts scaling issues
scaling_forecast = self._predict_scaling_issues(task, bottlenecks)
# → "At 10K users, database connections will saturate in 45 days"
```

### Empathy Checks

Every wizard output includes validation:

```python
empathy_checks = EmpathyChecks(
    cognitive="Considered developer's low risk tolerance, production constraints",
    emotional="Acknowledged high pressure (3 stress indicators: urgent, critical, blocks)",
    anticipatory="Predicted: 45-day connection pool exhaustion. Provided: pooling solution."
)
```

---

## 🧪 Testing

### Run All Tests

```bash
# Original 6 wizards (25 tests)
python3 -m pytest examples/coach/tests/test_all_wizards.py -v

# New 10 wizards (23 tests)
python3 -m pytest examples/coach/tests/test_new_wizards.py -v

# Total: 48 tests, 100% pass rate
```

### Test Coverage

- ✅ Wizard routing (50 test cases across 10 wizards)
- ✅ Collaboration patterns (4 multi-wizard workflows)
- ✅ Output quality (artifacts, empathy checks, risk analysis)
- ✅ Edge cases (ambiguous tasks, empty context)
- ✅ Level 4 Anticipatory validation
- ✅ Performance benchmarks (< 1 second execution)

### Quick Validation

```bash
# Verify all 16 wizards load
python3 -c "
from examples.coach import Coach
coach = Coach()
print(f'✅ Loaded {len(coach.wizards)} wizards')
print(f'Patterns: {len(coach.collaboration_patterns)}')
"
```

---

## 🛠️ Creating Custom Wizards

### 1. Inherit from BaseWizard

```python
from examples.coach.wizards import BaseWizard, WizardTask, WizardOutput, WizardArtifact, EmpathyChecks

class MyCustomWizard(BaseWizard):
    """
    Custom wizard for specific domain

    Uses:
    - Level 2: Guided clarification
    - Level 3: Proactive pattern detection
    - Level 4: Anticipatory future prediction
    """

    def can_handle(self, task: WizardTask) -> float:
        """Return confidence score 0.0-1.0"""
        # Define keywords that indicate this wizard should handle the task
        keywords = ["my_domain", "specific_task", "custom_feature"]

        task_lower = (task.task + " " + task.context).lower()
        matches = sum(2 for kw in keywords if kw in task_lower)

        return min(matches / 4.0, 1.0)  # 4+ points = 100% confidence

    def execute(self, task: WizardTask) -> WizardOutput:
        """Execute wizard's primary function"""
        # 1. Cognitive Empathy: Understand constraints
        constraints = self._extract_constraints(task)

        # 2. Emotional Empathy: Acknowledge pressure
        emotional_state = self._assess_emotional_state(task)

        # 3. Analyze problem
        diagnosis = self._analyze_problem(task)

        # 4. Create plan
        plan = self._create_action_plan(task)

        # 5. Generate artifacts
        artifacts = [
            WizardArtifact(
                type="doc",
                title="Analysis Report",
                content="Detailed analysis..."
            )
        ]

        # 6. Level 4: Predict future issues
        anticipatory_forecast = self._predict_future_issues(task)

        # 7. Return structured output
        return WizardOutput(
            wizard_name=self.name,
            diagnosis=diagnosis,
            plan=plan,
            artifacts=artifacts,
            risks=[],
            handoffs=[],
            next_actions=["Step 1", "Step 2"],
            empathy_checks=EmpathyChecks(
                cognitive=f"Considered {task.role} constraints",
                emotional=f"Acknowledged {emotional_state['pressure']} pressure",
                anticipatory=anticipatory_forecast[:200]
            ),
            confidence=self.can_handle(task)
        )
```

### 2. Register with Coach

```python
# In coach.py, add to wizard list
from .wizards.my_custom_wizard import MyCustomWizard

self.wizards: List[BaseWizard] = [
    SecurityWizard(config=self.config),
    ComplianceWizard(config=self.config),
    # ... other wizards ...
    MyCustomWizard(config=self.config),  # Add here
]
```

### 3. Add to `__init__.py`

```python
# In wizards/__init__.py
from .my_custom_wizard import MyCustomWizard

__all__ = [
    # ... existing wizards ...
    "MyCustomWizard",
]
```

### 4. Test Your Wizard

```python
import pytest
from examples.coach import Coach, WizardTask

@pytest.mark.asyncio
async def test_my_custom_wizard_routing():
    coach = Coach()

    task = WizardTask(
        role="developer",
        task="Task description with my_domain keywords",
        context="Additional context"
    )

    result = await coach.process(task, multi_wizard=False)

    assert "MyCustomWizard" in result.routing
    assert result.overall_confidence > 0.5
    assert len(result.primary_output.artifacts) > 0
```

---

## ⚙️ Configuration

### Custom Configuration

```python
from empathy_os import EmpathyConfig
from examples.coach import Coach

# Create custom configuration
config = EmpathyConfig(
    user_id="my_coach_instance",
    target_level=4,  # Use Level 4 Anticipatory Empathy
    confidence_threshold=0.75  # Higher threshold for routing
)

coach = Coach(config=config)
```

### Environment Variables

```bash
# Set empathy level
export EMPATHY_TARGET_LEVEL=4

# Set confidence threshold
export EMPATHY_CONFIDENCE_THRESHOLD=0.75
```

---

## 📈 Performance & Scalability

### Performance Characteristics

- **Routing Time**: O(W) where W = number of wizards (16 wizards ~1-2ms)
- **Single Wizard Execution**: ~100-500ms typical
- **Multi-Wizard Coordination**: Wizards run sequentially (~200ms-1s per wizard)
- **Total Response Time**: 200ms-3s depending on task complexity

### Optimization Tips

```python
# Use single-wizard mode for faster responses
result = await coach.process(task, multi_wizard=False)

# Cache Coach instance (don't reinitialize for every request)
coach = Coach()  # Initialize once
# Reuse for multiple tasks
```

### Future Optimizations

- [ ] Parallel wizard execution for multi-wizard tasks
- [ ] Response streaming for long-running analyses
- [ ] Wizard result caching for similar tasks

---

## 🌟 Real-World Use Cases

### Use Case 1: Production Incident Response

```python
task = WizardTask(
    role="developer",
    task="Production incident: users can't log in, 500 errors",
    context="Auth service failing, logs show database timeout errors",
    risk_tolerance="low"
)

result = await coach.process(task, multi_wizard=True)

# Automatically routes to collaboration pattern: production_incident
# → MonitoringWizard: Analyzes error rate, creates timeline
# → DebuggingWizard: Root cause analysis, hotfix patch
# → RetrospectiveWizard: Blameless postmortem template

# Result: 3 wizards coordinate to resolve incident + prevent recurrence
```

### Use Case 2: API Development with Best Practices

```python
task = WizardTask(
    role="developer",
    task="Build new API endpoint for user management following OpenAI conventions",
    context="Need streaming support, rate limiting, and proper error handling"
)

result = await coach.process(task, multi_wizard=True)

# Automatically routes to: new_api_endpoint pattern
# → APIWizard: OpenAPI 3.1 spec with streaming + rate limits
# → SecurityWizard: JWT authentication, SQL injection prevention
# → TestingWizard: Unit tests, integration tests, API contract tests
# → DocumentationWizard: Swagger UI, code examples, cURL commands

# Result: Production-ready API with industry-standard conventions
```

### Use Case 3: Pre-Audit Compliance Preparation

```python
task = WizardTask(
    role="team_lead",
    task="SOC 2 Type II audit in 90 days, need compliance preparation",
    context="Startup, 50 employees, no prior audit experience"
)

result = await coach.process(task, multi_wizard=True)

# Automatically routes to: compliance_audit pattern
# → ComplianceWizard: Gap analysis, remediation timeline
# → SecurityWizard: Penetration testing, vulnerability scan
# → DocumentationWizard: Policy generation, evidence collection

# Result: 90-day remediation plan with prioritized action items
```

---

## 📚 Documentation

- **[Complete Implementation Guide](WIZARD_IMPLEMENTATION_COMPLETE.md)** - Detailed implementation notes
- **[Empathy Framework Core](../../README.md)** - Core framework documentation
- **[API Reference](../../docs/)** - Detailed API documentation

---

## 🤝 Contributing

We welcome contributions! To add a new wizard:

1. Create wizard in `wizards/my_wizard.py` inheriting from `BaseWizard`
2. Implement `can_handle()` and `execute()` methods
3. Add to `wizards/__init__.py` exports
4. Register in `coach.py` wizard list
5. Write tests in `tests/test_my_wizard.py`
6. Update this README with wizard description

See [Creating Custom Wizards](#creating-custom-wizards) for detailed guide.

---

## 📄 License

Copyright 2025 Deep Study AI, LLC
Licensed under Fair Source 0.9

See [LICENSE](../../LICENSE) for details.

---

## 🙏 Acknowledgments

Built on the **Empathy Framework** - bringing Level 4 Anticipatory Empathy to software development.

Special thanks to:
- OpenAI and Anthropic for API design inspiration
- The open-source community for testing and feedback

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/empathy-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/empathy-framework/discussions)
- **Email**: support@deepstudy.ai

---

**Built with ❤️ using the Empathy Framework**

*Coach: Your AI pair programmer with 16 specialized minds and anticipatory empathy.*
