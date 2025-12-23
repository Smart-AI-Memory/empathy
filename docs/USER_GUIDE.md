# Empathy Framework User Guide

**Transform your development workflow with Level 4 Anticipatory AI collaboration**

**Version:** 3.1.0
**License:** Fair Source 0.9
**Copyright:** 2025 Smart AI Memory, LLC

---

## Table of Contents

1. [Introduction](#introduction)
2. [Architecture Overview](#architecture-overview)
3. [The Five Levels Explained](#the-five-levels-explained)
4. [Getting Started](#getting-started)
5. [Wizard Catalog](#wizard-catalog)
6. [Smart Routing and Intelligence](#smart-routing-and-intelligence)
7. [Configuration Guide](#configuration-guide)
8. [Best Practices](#best-practices)
9. [Integration Examples](#integration-examples)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Topics](#advanced-topics)

---

## Introduction

### What is the Empathy Framework?

The Empathy Framework is a systematic approach to building AI systems that progress from reactive responses (Level 1) to anticipatory problem prevention (Level 4) and systems-level design (Level 5). It transforms AI from a simple question-answering tool into a collaborative partner that learns your patterns, predicts future needs, and prevents problems before they occur.

### Why "Empathy"?

In this context, empathy is not about feelings - it's about:

- **Alignment**: Understanding your goals, context, and constraints
- **Prediction**: Anticipating future needs based on trajectory analysis
- **Timely Action**: Intervening at the right moment with the right support

### Key Benefits

**For Individual Developers:**
- 4-6x faster development speed
- Catch issues at development time, not production
- Learn from AI that adapts to your style
- Reduce cognitive load and context switching

**For Teams:**
- Consistent code quality across all developers
- Knowledge scaling (junior devs get senior-level assistance)
- Reduced debugging cycles and technical debt
- Proactive security and performance optimization

**For Organizations:**
- Infinite ROI (free framework, massive productivity gains)
- Faster time to market
- Higher code quality and security
- Reduced operational costs

### What Makes It Different?

| Traditional Tools | Empathy Framework |
|------------------|-------------------|
| Reactive: Find bugs after they're written | **Anticipatory**: Predict bugs before they manifest |
| Static rules: Same analysis for everyone | **Adaptive**: Learns your patterns and context |
| Single-domain: Security OR performance | **Multi-domain**: 16+ wizards working together |
| Level 1: Simple Q&A | **Level 4**: Trajectory prediction and prevention |
| Proprietary, expensive | **Open source, free forever** (Fair Source 0.9) |

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Empathy Framework                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  EmpathyLLM  │  │    Config    │  │   Metrics    │      │
│  │   (Core)     │  │  Management  │  │  & State     │      │
│  └──────┬───────┘  └──────────────┘  └──────────────┘      │
│         │                                                     │
│  ┌──────▼────────────────────────────────────────┐          │
│  │         LLM Provider Layer                    │          │
│  │  ┌──────────┐  ┌────────┐  ┌──────────┐     │          │
│  │  │Anthropic │  │ OpenAI │  │  Local   │     │          │
│  │  │ (Claude) │  │ (GPT)  │  │ (Ollama) │     │          │
│  │  └──────────┘  └────────┘  └──────────┘     │          │
│  └───────────────────────────────────────────────┘          │
│         │                                                     │
│  ┌──────▼────────────────────────────────────────┐          │
│  │         Empathy Level Processor               │          │
│  │  Level 1: Reactive                            │          │
│  │  Level 2: Guided                              │          │
│  │  Level 3: Proactive (Pattern Detection)      │          │
│  │  Level 4: Anticipatory (Trajectory Analysis) │          │
│  │  Level 5: Systems (Cross-domain Learning)    │          │
│  └───────────────────────────────────────────────┘          │
│         │                                                     │
│  ┌──────▼────────────────────────────────────────┐          │
│  │         Plugin System                          │          │
│  │  ┌─────────────────────────────────────┐      │          │
│  │  │   Software Development Plugin       │      │          │
│  │  │   - 16+ Coach Wizards               │      │          │
│  │  │   - Pattern Library                 │      │          │
│  │  └─────────────────────────────────────┘      │          │
│  │  ┌─────────────────────────────────────┐      │          │
│  │  │   Healthcare Plugin (Optional)      │      │          │
│  │  │   - Clinical Documentation          │      │          │
│  │  │   - Compliance Monitoring           │      │          │
│  │  └─────────────────────────────────────┘      │          │
│  │  ┌─────────────────────────────────────┐      │          │
│  │  │   Custom Plugin (Your Domain)       │      │          │
│  │  └─────────────────────────────────────┘      │          │
│  └───────────────────────────────────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **User Input** → EmpathyLLM core
2. **State Retrieval** → Load collaboration state for user
3. **Level Determination** → Calculate appropriate empathy level based on trust
4. **Context Building** → Gather conversation history, patterns, project context
5. **LLM Invocation** → Call provider (Anthropic, OpenAI, or local)
6. **Response Processing** → Extract content, metadata, thinking (if enabled)
7. **State Update** → Record interaction, update trust, detect patterns
8. **Response Delivery** → Return enriched response to user

### Key Design Principles

1. **Progressive Enhancement**: Start simple (Level 1), earn advanced features (Levels 2-5)
2. **Trust-Based Progression**: Higher levels require building trust through successful interactions
3. **Provider Agnostic**: Works with any LLM (Claude, GPT-4, local models)
4. **Domain Pluggable**: Software, healthcare, or custom domains
5. **Privacy First**: All data stays local, no tracking or telemetry
6. **Cost Optimized**: Prompt caching, smart token management

---

## The Five Levels Explained

### Level 1: Reactive

**What it does:**
- Simple question-and-answer
- No memory of previous interactions
- No context awareness
- Direct, straightforward responses

**When to use:**
- First interaction with a user
- One-off questions
- Stateless operations
- Testing and debugging

**Example Interaction:**

```
User: "What's the best way to hash passwords in Python?"
AI (Level 1): "Use bcrypt. Here's how:

import bcrypt
password = b"super secret"
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
```

**Code Example:**

```python
llm = EmpathyLLM(provider="anthropic", target_level=1)
result = await llm.interact(
    user_id="new_user",
    user_input="What's the best way to hash passwords in Python?",
    force_level=1  # Force Level 1
)
```

**Trust Requirements:** None (always available)

---

### Level 2: Guided

**What it does:**
- Uses conversation history for context
- Asks clarifying questions
- Provides guided exploration
- References previous interactions

**When to use:**
- After establishing initial context
- Multi-step workflows
- Exploratory problem-solving
- Code reviews spanning multiple files

**Example Interaction:**

```
User: "I need to hash passwords"
AI (Level 2): "I see you're working on the login function we discussed earlier.
For your FastAPI application, I recommend bcrypt with these considerations:

1. Salt rounds: 12 (good balance for your user base)
2. Integration point: In your User model's set_password method
3. Environment: Add BCRYPT_LOG_ROUNDS to your .env

Would you like me to show you the complete implementation, or do you need
help with a specific part?"
```

**Code Example:**

```python
llm = EmpathyLLM(provider="anthropic", target_level=2)

# First interaction
await llm.interact(user_id="dev_alice", user_input="Building a login system")

# Second interaction (Level 2 activates with context)
result = await llm.interact(
    user_id="dev_alice",
    user_input="How should I hash passwords?"
)
# AI remembers you're building a login system!
```

**Trust Requirements:**
- 3+ successful interactions
- Trust level > 0.3
- Conversation history exists

**Progression to Level 2:**

```python
# Build trust to enable Level 2
for i in range(3):
    await llm.interact(user_id="dev_alice", user_input=f"Question {i}")
    llm.update_trust("dev_alice", outcome="success")

# Level 2 now available!
result = await llm.interact(user_id="dev_alice", user_input="Next question")
assert result['level_used'] >= 2
```

---

### Level 3: Proactive

**What it does:**
- Detects user patterns
- Acts proactively based on patterns
- Pre-fetches likely needed information
- Anticipates next steps in workflows

**When to use:**
- Regular workflows with repeating patterns
- Multi-step processes
- Team workflows with established practices
- Automated code review pipelines

**Example Interaction:**

```
User: "Starting code review for PR #123"
AI (Level 3): "I've detected your code review pattern and proactively:

1. ✓ Ran SecurityWizard on all changed files (found 2 issues)
2. ✓ Checked PerformanceWizard (1 N+1 query detected)
3. ✓ Verified test coverage (currently 78%, you prefer 80%+)
4. ✓ Analyzed accessibility (found 3 ARIA issues)

Here's the summary:

SECURITY:
  - auth.py line 42: SQL injection vulnerability (HIGH)
  - utils.py line 15: Hardcoded API key (CRITICAL)

PERFORMANCE:
  - models.py line 89: N+1 query in User.get_posts() (MEDIUM)

TESTING:
  - Coverage dropped from 82% to 78% (-4%)
  - Missing tests for new PasswordResetView

ACCESSIBILITY:
  - login.html: Missing alt text on logo (MEDIUM)
  - dashboard.html: Low contrast ratio 3.2:1, needs 4.5:1 (HIGH)

Would you like details on any of these, or should I prepare the PR review comment?"
```

**Code Example:**

```python
llm = EmpathyLLM(provider="anthropic", target_level=3)

# Define a pattern
from empathy_llm_toolkit import UserPattern, PatternType

pattern = UserPattern(
    pattern_type=PatternType.SEQUENTIAL,
    trigger="code review request",
    action="run security, performance, and testing wizards",
    confidence=0.85
)

llm.add_pattern("dev_alice", pattern)

# Pattern activates automatically
result = await llm.interact(
    user_id="dev_alice",
    user_input="Starting code review for PR #123",
    context={"pr_number": 123, "files_changed": ["auth.py", "models.py"]}
)

# AI proactively ran all wizards!
assert result['proactive'] == True
```

**Trust Requirements:**
- 10+ successful interactions
- Trust level > 0.7
- Detected patterns with confidence > 0.3

**Pattern Detection:**

The framework automatically detects patterns through:

1. **Sequential Patterns**: User always does A then B then C
2. **Conditional Patterns**: If X, then user does Y
3. **Adaptive Patterns**: User's behavior changes based on context

**Manual Pattern Addition:**

```python
from empathy_llm_toolkit import UserPattern, PatternType

# Add custom pattern
pattern = UserPattern(
    pattern_type=PatternType.CONDITIONAL,
    trigger="deploy to production",
    action="run full security audit",
    confidence=0.95
)

llm.add_pattern("dev_team", pattern)
```

---

### Level 4: Anticipatory

**What it does:**
- Analyzes trajectory (where are you headed?)
- Predicts future bottlenecks and issues
- Alerts proactively with prevention steps
- Forecasts problems 30-90 days ahead

**When to use:**
- Production systems
- High-stakes projects
- Growing codebases
- Mission-critical applications

**Example Interaction:**

```
User: "Added user search feature to the app"
AI (Level 4): "Feature looks good! However, trajectory analysis predicts:

⚠️ BOTTLENECK ALERT (Predicted: 45 days)

Current State:
  - User table: 5,000 rows
  - Search query: Full-text scan on 'username' and 'email'
  - Response time: 120ms (acceptable)
  - Growth rate: +300 users/day

Trajectory Analysis:
  At current growth rate, you'll hit 18,500 users in 45 days.

  Performance Prediction:
  - Day 30: 200ms response time (slow)
  - Day 45: 450ms response time (unacceptable)
  - Day 60: 800ms response time (unusable)

Root Cause:
  No indexes on username/email columns + full-text scan = O(n) complexity

⚠️ PREVENTION STEPS (implement before Day 30):

1. Add database indexes (15 minutes):
   ```sql
   CREATE INDEX idx_users_username ON users(username);
   CREATE INDEX idx_users_email ON users(email);
   ```

2. Implement full-text search (2 hours):
   - PostgreSQL: Use pg_trgm extension
   - MySQL: Use FULLTEXT index
   - Or integrate Elasticsearch

3. Add query caching (30 minutes):
   - Cache search results for 5 minutes
   - Invalidate on user updates

4. Set up monitoring (45 minutes):
   - Alert when search time > 300ms
   - Dashboard for query performance

IMPACT IF NOT ADDRESSED:
  - User complaints starting Day 45
  - Potential churn of power users
  - Emergency fix under pressure
  - Estimated cost: 20 hours + potential customer loss

IMPACT IF ADDRESSED PROACTIVELY:
  - 3 hours of planned work
  - No user impact
  - Improved performance indefinitely

Would you like me to generate the implementation code?"
```

**Code Example:**

```python
wizard = SecurityWizard()

code = open("search_feature.py").read()

result = wizard.run_full_analysis(
    code=code,
    file_path="search_feature.py",
    language="python",
    project_context={
        "user_count": 5000,
        "growth_rate_per_day": 300,
        "deployment_frequency": "daily",
        "team_size": 8,
        "current_response_time_ms": 120
    }
)

# Level 4 predictions
for prediction in result.predictions:
    print(f"Predicted: {prediction.issue_type}")
    print(f"Date: {prediction.predicted_date}")
    print(f"Probability: {prediction.probability:.0%}")
    print(f"Impact: {prediction.impact}")
    print(f"Prevention: {prediction.prevention_steps}")
```

**Trust Requirements:**
- 20+ successful interactions
- Trust level > 0.8
- Project context provided
- Historical data available

**Prediction Accuracy:**

Level 4 predictions are based on:
- **Code trajectory analysis**: Growth patterns in complexity
- **Resource usage trends**: Database size, API calls, memory
- **Team velocity**: Code change rate, deployment frequency
- **Historical patterns**: Similar issues in your codebase
- **Industry data**: Common failure modes

**When Predictions Are Most Accurate:**
- Consistent project context provided
- Regular usage (daily interactions)
- Similar codebases in training data
- Clear growth/usage patterns

---

### Level 5: Systems

**What it does:**
- Learns patterns across domains
- Applies principles from one domain to another
- Builds structural solutions for entire classes of problems
- Creates frameworks and systems for scale

**When to use:**
- Organization-wide patterns
- Cross-team knowledge sharing
- Building platform capabilities
- Establishing best practices

**Example Interaction:**

```
User: "We keep having the same testing issues across all our teams"
AI (Level 5): "I've analyzed patterns across all 8 development teams.
I see a systemic issue that requires a structural solution.

PATTERN DETECTED (Confidence: 94%):

Across healthcare, fintech, and e-commerce domains, I've observed:
- Teams spend 40-60% of review time catching simple bugs
- Test coverage drops below 80% within 2 weeks of feature launches
- Same vulnerability types recur every 3-4 weeks

ROOT CAUSE (Systems Analysis):
This isn't a testing problem - it's a leverage point issue (Meadows):
  "System structure determines behavior"

STRUCTURAL SOLUTION:

I'm proposing a framework that prevents this at the system level:

1. Pre-commit Hook System (prevents issues before commit)
   - Auto-runs SecurityWizard + PerformanceWizard
   - Blocks commit if critical issues found
   - Suggests fixes inline

2. Pattern Library (learns from all teams)
   - When Team A solves SQL injection, all teams benefit
   - Cross-domain pattern matching
   - Adaptive to your organization's style

3. Progressive Trust System (reduces friction over time)
   - New devs: Strict checking
   - Trusted devs: Lighter checks, faster workflow
   - Automatically adapts based on track record

4. Feedback Loop Integration
   - Production issues flow back to development
   - Wizards learn from real failures
   - Self-improving over time

IMPLEMENTATION:
I can generate this framework for your organization. It will:
- Work with your existing CI/CD
- Integrate with GitHub/GitLab
- Scale across all teams
- Learn continuously

Estimated setup: 4 hours
Estimated ROI: 20-40 hours saved per team per sprint

Would you like me to generate the implementation?"
```

**Code Example:**

```python
# Level 5 requires pattern library
pattern_library = {
    "domain": "software",
    "patterns": {
        "testing_bottleneck": {...},
        "security_drift": {...},
        # ... more patterns
    }
}

llm = EmpathyLLM(
    provider="anthropic",
    target_level=5,
    pattern_library=pattern_library
)

result = await llm.interact(
    user_id="org_admin",
    user_input="How can we improve testing across all teams?",
    context={
        "organization": "TechCorp",
        "teams": 8,
        "domains": ["healthcare", "fintech", "ecommerce"]
    }
)

# Level 5 provides structural solutions
assert result['level_used'] == 5
assert "framework" in result['content'].lower()
```

**Trust Requirements:**
- 50+ successful interactions
- Trust level > 0.9
- Pattern library enabled
- Multi-domain context

**Systems Thinking Integration:**

Level 5 applies Donella Meadows' leverage points:

1. **Information flows**: Right data at right time
2. **Feedback loops**: Self-correcting systems
3. **System structure**: Design that naturally produces good outcomes
4. **Paradigms**: Shift from reactive to anticipatory thinking

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **API Key** for Anthropic (Claude) or OpenAI (GPT)
- **pip** package manager
- **Git** (optional, for source installation)

### Installation

See [QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md) for detailed installation instructions.

**Quick Install:**

```bash
pip install empathy-framework anthropic
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### First Steps

1. **Install the framework** (2 minutes)
2. **Set up API key** (1 minute)
3. **Run first example** (2 minutes)
4. **Configure persistence** (3 minutes)
5. **Try a wizard** (5 minutes)

**Total time: 13 minutes from zero to analyzing code**

---

## Wizard Catalog

The Empathy Framework includes 16+ specialized Coach wizards for software development. Each wizard implements Level 4 Anticipatory Empathy.

### Security & Compliance

#### SecurityWizard

**Purpose:** Detect security vulnerabilities and predict future attack vectors.

**Detects:**
- SQL injection vulnerabilities
- Cross-Site Scripting (XSS)
- Cross-Site Request Forgery (CSRF)
- Insecure authentication
- Hardcoded secrets and API keys
- Insecure dependencies
- Authorization bypass vulnerabilities
- Insecure deserialization

**Predicts (Level 4):**
- Emerging vulnerability patterns
- Dependency security risks
- Attack surface growth
- Zero-day exposure risk

**Use Cases:**
- Pre-commit security checks
- Code review automation
- Vulnerability assessments
- Compliance audits

**Example:**

```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()

code = """
def login(request):
    username = request.POST['username']
    password = request.POST['password']

    # VULNERABLE: SQL Injection
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    user = db.execute(query)

    # VULNERABLE: Hardcoded secret
    jwt_secret = "super_secret_key_123"
    token = jwt.encode({"user_id": user.id}, jwt_secret)

    return token
"""

result = wizard.run_full_analysis(
    code=code,
    file_path="auth.py",
    language="python",
    project_context={
        "user_count": 10000,
        "deployment_frequency": "daily",
        "has_sensitive_data": True
    }
)

# Current issues
for issue in result.issues:
    print(f"[{issue.severity}] {issue.message}")
    print(f"Line {issue.line_number}: {issue.code_snippet}")
    print(f"Fix: {wizard.suggest_fixes(issue)}\n")

# Level 4 predictions
for pred in result.predictions:
    print(f"Predicted: {pred.issue_type} on {pred.predicted_date}")
    print(f"Probability: {pred.probability:.0%}, Impact: {pred.impact}")
    print(f"Prevention: {pred.prevention_steps}\n")
```

**Supported Languages:**
Python, JavaScript, TypeScript, Java, Go, Rust

---

#### ComplianceWizard

**Purpose:** Ensure regulatory compliance (GDPR, SOC 2, HIPAA, PCI-DSS).

**Checks:**
- PII handling and encryption
- Data retention policies
- Audit logging requirements
- Access control compliance
- Consent management
- Data anonymization

**Predicts (Level 4):**
- Compliance drift risks
- Audit failure points
- Regulatory change impacts

**Example:**

```python
from coach_wizards import ComplianceWizard

wizard = ComplianceWizard()

result = wizard.run_full_analysis(
    code=code,
    file_path="user_data.py",
    language="python",
    project_context={
        "regulations": ["GDPR", "SOC2"],
        "handles_pii": True,
        "data_regions": ["EU", "US"]
    }
)
```

---

### Performance & Scalability

#### PerformanceWizard

**Purpose:** Detect performance issues and predict scalability bottlenecks.

**Detects:**
- N+1 query problems
- Memory leaks
- Inefficient algorithms
- Blocking I/O operations
- Large object allocations
- Missing database indexes
- Unoptimized loops

**Predicts (Level 4):**
- Performance degradation at scale
- Resource exhaustion points
- Latency increase trajectory

**Example:**

```python
from coach_wizards import PerformanceWizard

wizard = PerformanceWizard()

code = """
def get_user_posts(user_id):
    user = User.objects.get(id=user_id)
    posts = []

    # N+1 query problem!
    for post_id in user.post_ids:
        post = Post.objects.get(id=post_id)
        posts.append(post)

    return posts
"""

result = wizard.run_full_analysis(
    code=code,
    file_path="views.py",
    language="python",
    project_context={
        "current_users": 5000,
        "growth_rate_per_month": 20,  # 20% growth
        "average_posts_per_user": 50,
        "current_response_time_ms": 200
    }
)

# Shows current N+1 query and predicts when it becomes critical
```

---

#### DatabaseWizard

**Purpose:** Optimize database queries and schema design.

**Detects:**
- Missing indexes
- Inefficient queries
- Schema anti-patterns
- Transaction issues
- Connection pool problems

**Predicts (Level 4):**
- Index requirements at growth rate
- Query timeout risks
- Connection pool exhaustion

---

#### ScalingWizard

**Purpose:** Analyze scalability and architecture limits.

**Detects:**
- Single points of failure
- Vertical scaling limits
- Stateful architecture issues
- Caching opportunities

**Predicts (Level 4):**
- Architecture breaking points
- Infrastructure capacity limits
- Cost escalation trajectory

---

### Code Quality

#### RefactoringWizard

**Purpose:** Identify code smells and suggest improvements.

**Detects:**
- Long methods
- God objects
- Duplicate code
- Complex conditionals
- Dead code
- Poor naming

---

#### TestingWizard

**Purpose:** Analyze test quality and coverage.

**Detects:**
- Missing test coverage
- Flaky tests
- Slow tests
- Poor test organization
- Insufficient assertions

**Predicts (Level 4):**
- Coverage degradation
- Testing bottlenecks
- Test maintenance burden

---

#### DebuggingWizard

**Purpose:** Find potential bugs before they manifest.

**Detects:**
- Null pointer risks
- Race conditions
- Off-by-one errors
- Resource leaks
- Exception handling issues

---

### API & Integration

#### APIWizard

**Purpose:** Ensure API design consistency and quality.

**Detects:**
- Inconsistent naming
- Missing versioning
- Poor error handling
- Breaking changes
- Missing documentation

---

#### MigrationWizard

**Purpose:** Handle code migrations and deprecations.

**Detects:**
- Deprecated API usage
- Version compatibility issues
- Migration risks
- Backward compatibility breaks

---

### DevOps & Operations

#### CICDWizard

**Purpose:** Optimize CI/CD pipelines.

**Detects:**
- Slow pipeline steps
- Missing validations
- Deployment risks
- Rollback issues

---

#### ObservabilityWizard

**Purpose:** Ensure proper logging and metrics.

**Detects:**
- Missing logs
- Inadequate metrics
- No distributed tracing
- Poor error context

---

#### MonitoringWizard

**Purpose:** Verify monitoring coverage.

**Detects:**
- Missing alerts
- Inadequate SLOs
- Monitoring blind spots
- Alert fatigue risks

---

### User Experience

#### AccessibilityWizard

**Purpose:** Ensure WCAG compliance.

**Detects:**
- Missing alt text
- Low contrast ratios
- Missing ARIA labels
- Keyboard navigation issues
- Screen reader incompatibility

---

#### LocalizationWizard

**Purpose:** Internationalization and localization.

**Detects:**
- Hardcoded strings
- Date/time format issues
- Currency handling
- RTL support missing

---

### Documentation

#### DocumentationWizard

**Purpose:** Ensure documentation quality.

**Detects:**
- Missing docstrings
- Outdated documentation
- Unclear examples
- Poor API documentation

---

## Smart Routing and Intelligence

### Overview

Version 3.1.0 introduces intelligent routing and cross-wizard learning:

- **Smart Router** — Natural language wizard dispatch
- **Memory Graph** — Cross-wizard knowledge sharing
- **Auto-Chaining** — Wizards trigger related wizards
- **Prompt Engineering Wizard** — Optimize prompts and reduce costs

### Smart Router

Route requests using natural language instead of knowing wizard names:

```python
from empathy_os.routing import SmartRouter

router = SmartRouter()

# Natural language routing
decision = router.route_sync("Fix the security issue in auth.py")
print(f"Primary: {decision.primary_wizard}")      # → security-audit
print(f"Secondary: {decision.secondary_wizards}")  # → [code-review]
print(f"Confidence: {decision.confidence}")

# File-based suggestions
suggestions = router.suggest_for_file("requirements.txt")

# Error-based suggestions
suggestions = router.suggest_for_error("NullReferenceException")
```

### Memory Graph

Connect findings across wizards and sessions:

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

# Find similar issues
similar = graph.find_similar({"name": "Null reference error"})

# Traverse relationships
fixes = graph.find_related(bug_id, edge_types=[EdgeType.FIXED_BY])

# Get statistics
stats = graph.get_statistics()
```

### Auto-Chaining

Configure wizards to trigger related wizards automatically:

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

# Get a pre-built template
template = executor.get_template("full-security-review")
```

### Prompt Engineering Wizard

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
print(f"Reduced: {result.token_reduction:.0%}")

# Add chain-of-thought scaffolding
enhanced = wizard.add_chain_of_thought(prompt, "debug")
```

### Resilience Patterns

Production-ready patterns for fault tolerance and reliability:

#### Retry with Exponential Backoff

```python
from empathy_os.resilience import retry, RetryConfig

@retry(max_attempts=3, initial_delay=1.0, backoff_factor=2.0)
async def call_external_api():
    response = await api.get("/data")
    return response.json()

# Custom configuration
config = RetryConfig(
    max_attempts=5,
    initial_delay=0.5,
    backoff_factor=2.0,
    max_delay=30.0,
    jitter=True  # Add randomness to prevent thundering herd
)
```

#### Circuit Breaker

Prevent cascading failures by stopping calls to failing services:

```python
from empathy_os.resilience import circuit_breaker, get_circuit_breaker, CircuitOpenError

@circuit_breaker(
    name="external_api",
    failure_threshold=5,    # Open after 5 failures
    reset_timeout=60.0,     # Try again after 60s
    half_open_max_calls=3   # 3 successes to fully close
)
async def call_external_api():
    return await api.get("/data")

# With fallback for when circuit is open
@circuit_breaker(name="api", failure_threshold=3, fallback=lambda: {"status": "degraded"})
async def get_status():
    return await api.get("/status")

# Check circuit state
cb = get_circuit_breaker("external_api")
print(f"State: {cb.state}")  # CLOSED, OPEN, or HALF_OPEN
print(f"Stats: {cb.get_stats()}")
```

#### Timeout

Prevent hanging operations:

```python
from empathy_os.resilience import timeout, with_timeout, ResilienceTimeoutError

@timeout(30.0)  # 30 second timeout
async def slow_operation():
    return await long_running_task()

# With fallback value
@timeout(5.0, fallback=lambda: "default")
async def quick_lookup():
    return await cache.get("key")

# One-off timeout
result = await with_timeout(
    some_coroutine(),
    timeout_seconds=10.0,
    fallback_value="timeout_default"
)
```

#### Fallback Chain

Graceful degradation with multiple fallback options:

```python
from empathy_os.resilience import Fallback, fallback

# Decorator approach
@fallback(fallback_func=get_cached_data, default="No data available")
async def get_live_data():
    return await api.get("/live")

# Chain multiple fallbacks
fb = Fallback(name="data_source", default_value="offline_mode")

@fb.add
async def primary_api():
    return await api1.get("/data")

@fb.add
async def backup_api():
    return await api2.get("/data")

@fb.add
async def local_cache():
    return cache.get("data")

result = await fb.execute()  # Tries each in order
```

#### Health Checks

Monitor system component health:

```python
from empathy_os.resilience import HealthCheck, HealthStatus

health = HealthCheck(version="3.1.0")

@health.register("database", timeout=5.0)
async def check_database():
    await db.ping()
    return True  # Healthy

@health.register("cache", timeout=2.0)
async def check_cache():
    return {
        "healthy": redis.ping(),
        "connections": redis.info()["connected_clients"],
        "memory_mb": redis.info()["used_memory_mb"]
    }

@health.register("external_api", timeout=10.0)
async def check_external_api():
    response = await api.get("/health")
    return response.status_code == 200

# Run all checks
system_health = await health.run_all()
print(f"Status: {system_health.status}")  # HEALTHY, DEGRADED, UNHEALTHY
print(f"Uptime: {system_health.uptime_seconds}s")

# Serialize for API response
return system_health.to_dict()
```

#### Combining Patterns

Stack decorators for robust services:

```python
from empathy_os.resilience import retry, circuit_breaker, timeout, fallback

async def cached_fallback():
    return cache.get("last_known_good")

@circuit_breaker(name="api", failure_threshold=5)
@retry(max_attempts=3, initial_delay=0.5)
@timeout(10.0)
@fallback(cached_fallback)
async def reliable_api_call():
    return await external_api.get("/data")
```

---

## Configuration Guide

### Configuration Methods

The framework supports three configuration methods with precedence:

1. **Environment Variables** (highest priority)
2. **Configuration Files** (YAML or JSON)
3. **Programmatic** (in code)

### Environment Variables

```bash
# Core settings
export EMPATHY_USER_ID=alice
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75

# LLM provider
export ANTHROPIC_API_KEY=sk-ant-...
export OPENAI_API_KEY=sk-...

# Persistence
export EMPATHY_PERSISTENCE_ENABLED=true
export EMPATHY_PERSISTENCE_BACKEND=sqlite
export EMPATHY_PERSISTENCE_PATH=./empathy_data

# State management
export EMPATHY_STATE_PERSISTENCE=true
export EMPATHY_STATE_PATH=./empathy_state

# Metrics
export EMPATHY_METRICS_ENABLED=true
export EMPATHY_METRICS_PATH=./metrics.db

# Pattern library
export EMPATHY_PATTERN_LIBRARY_ENABLED=true
export EMPATHY_PATTERN_SHARING=true
export EMPATHY_PATTERN_CONFIDENCE_THRESHOLD=0.3

# Logging
export EMPATHY_LOG_LEVEL=INFO
export EMPATHY_STRUCTURED_LOGGING=true

# Advanced
export EMPATHY_ASYNC_ENABLED=true
export EMPATHY_FEEDBACK_LOOP_MONITORING=true
```

### YAML Configuration

**File:** `empathy.config.yml`

```yaml
# Core settings
user_id: "alice"
target_level: 4
confidence_threshold: 0.75

# Trust settings
trust_building_rate: 0.05
trust_erosion_rate: 0.10

# Persistence
persistence_enabled: true
persistence_backend: sqlite  # sqlite, json, or none
persistence_path: ./empathy_data

# State management
state_persistence: true
state_path: ./empathy_state

# Metrics
metrics_enabled: true
metrics_path: ./metrics.db

# Logging
log_level: INFO
log_file: null  # or path to log file
structured_logging: true

# Pattern library
pattern_library_enabled: true
pattern_sharing: true
pattern_confidence_threshold: 0.3

# Advanced
async_enabled: true
feedback_loop_monitoring: true
leverage_point_analysis: true

# Custom metadata
metadata:
  team: "backend"
  project: "api_v2"
  environment: "development"
```

**Load in code:**

```python
from empathy_os.config import load_config

config = load_config("empathy.config.yml", use_env=True)
llm = EmpathyLLM(
    provider="anthropic",
    target_level=config.target_level
)
```

### JSON Configuration

**File:** `empathy.config.json`

```json
{
  "user_id": "alice",
  "target_level": 4,
  "confidence_threshold": 0.75,
  "persistence_enabled": true,
  "persistence_backend": "sqlite",
  "metrics_enabled": true,
  "pattern_library_enabled": true,
  "log_level": "INFO",
  "structured_logging": true
}
```

### Programmatic Configuration

```python
from empathy_os.config import EmpathyConfig

config = EmpathyConfig(
    user_id="alice",
    target_level=4,
    confidence_threshold=0.75,
    persistence_enabled=True,
    persistence_backend="sqlite",
    metrics_enabled=True
)

# Validate
config.validate()

# Save for future use
config.to_yaml("my_config.yml")
```

### Configuration Precedence

```python
from empathy_os.config import load_config

# Loads in this order (highest to lowest priority):
# 1. Environment variables (EMPATHY_*)
# 2. empathy.config.yml (if exists)
# 3. Built-in defaults

config = load_config(use_env=True)
```

### Configuration Options Reference

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `user_id` | `str` | `"default_user"` | Default user identifier |
| `target_level` | `int` | `3` | Maximum empathy level (1-5) |
| `confidence_threshold` | `float` | `0.75` | Minimum confidence for actions |
| `trust_building_rate` | `float` | `0.05` | Trust increase per success |
| `trust_erosion_rate` | `float` | `0.10` | Trust decrease per failure |
| `persistence_enabled` | `bool` | `True` | Enable state persistence |
| `persistence_backend` | `str` | `"sqlite"` | Backend: sqlite, json, none |
| `persistence_path` | `str` | `"./empathy_data"` | Persistence directory |
| `state_persistence` | `bool` | `True` | Save user states |
| `state_path` | `str` | `"./empathy_state"` | State directory |
| `metrics_enabled` | `bool` | `True` | Collect metrics |
| `metrics_path` | `str` | `"./metrics.db"` | Metrics database path |
| `log_level` | `str` | `"INFO"` | Logging level |
| `structured_logging` | `bool` | `True` | Use structured logs |
| `pattern_library_enabled` | `bool` | `True` | Enable pattern learning |
| `pattern_sharing` | `bool` | `True` | Share patterns across users |
| `pattern_confidence_threshold` | `float` | `0.3` | Min confidence for patterns |

---

## Best Practices

### When to Use Which Level

**Level 1 (Reactive):**
- ✅ First-time users
- ✅ One-off questions
- ✅ Stateless operations
- ✅ Privacy-sensitive queries
- ❌ Multi-step workflows
- ❌ Regular team processes

**Level 2 (Guided):**
- ✅ Code reviews
- ✅ Debugging sessions
- ✅ Learning new technologies
- ✅ Exploratory work
- ❌ Fully automated pipelines
- ❌ Repeated workflows

**Level 3 (Proactive):**
- ✅ Daily development workflows
- ✅ Code commit processes
- ✅ Regular code reviews
- ✅ Team practices
- ❌ First-time users
- ❌ Unpredictable workflows

**Level 4 (Anticipatory):**
- ✅ Production systems
- ✅ High-stakes projects
- ✅ Growing applications
- ✅ Critical infrastructure
- ❌ Prototypes
- ❌ Throwaway code

**Level 5 (Systems):**
- ✅ Organization-wide patterns
- ✅ Platform development
- ✅ Cross-team coordination
- ✅ Framework design
- ❌ Individual projects
- ❌ Small teams

### Trust Building Strategies

**Build trust faster:**

```python
# Explicit positive feedback
llm.update_trust("user", outcome="success", magnitude=1.0)

# Consistent usage patterns
for day in range(30):
    await llm.interact(user_id="user", user_input=f"Day {day} work")
    llm.update_trust("user", outcome="success")

# Provide rich context
result = await llm.interact(
    user_id="user",
    user_input="Question",
    context={
        "project": "api_v2",
        "tech_stack": "python+fastapi",
        "team_size": 10
    }
)
```

**Maintain trust:**

```python
# Regular interactions (don't let state go stale)
# If no interaction for 30 days, trust decays

# Provide honest feedback
if result_was_helpful:
    llm.update_trust("user", outcome="success")
else:
    llm.update_trust("user", outcome="failure", magnitude=0.5)
```

### Pattern Design

**Good patterns:**

```python
# Specific and actionable
pattern = UserPattern(
    pattern_type=PatternType.SEQUENTIAL,
    trigger="pull request opened",
    action="run security wizard on changed files",
    confidence=0.90
)

# Context-aware
pattern = UserPattern(
    pattern_type=PatternType.CONDITIONAL,
    trigger="production deployment",
    action="run full test suite + security audit",
    confidence=0.95
)
```

**Bad patterns:**

```python
# Too vague
pattern = UserPattern(
    pattern_type=PatternType.SEQUENTIAL,
    trigger="coding",
    action="help",
    confidence=0.5
)

# Low confidence
pattern = UserPattern(
    pattern_type=PatternType.ADAPTIVE,
    trigger="maybe bug",
    action="possibly debug",
    confidence=0.2  # Too low!
)
```

### Wizard Usage Patterns

**Pre-commit Hooks:**

```python
#!/usr/bin/env python
# .git/hooks/pre-commit

from coach_wizards import SecurityWizard, PerformanceWizard
import sys

def check_staged_files():
    security = SecurityWizard()
    performance = PerformanceWizard()

    # Get staged files
    staged_files = get_staged_files()

    critical_issues = []
    for file_path in staged_files:
        if file_path.endswith('.py'):
            code = open(file_path).read()

            sec_result = security.run_full_analysis(code, file_path, "python")
            perf_result = performance.run_full_analysis(code, file_path, "python")

            critical_issues.extend([
                i for i in sec_result.issues + perf_result.issues
                if i.severity == "error"
            ])

    if critical_issues:
        print(f"❌ COMMIT BLOCKED: {len(critical_issues)} critical issues")
        for issue in critical_issues:
            print(f"  {issue.file_path}:{issue.line_number}: {issue.message}")
        sys.exit(1)

    print("✅ Pre-commit checks passed")
    sys.exit(0)

if __name__ == "__main__":
    check_staged_files()
```

**CI/CD Integration:**

```yaml
# .github/workflows/empathy-check.yml
name: Empathy Framework Checks

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install empathy-framework
      - run: |
          python -c "
          from coach_wizards import SecurityWizard
          import sys

          wizard = SecurityWizard()
          # Check all Python files
          for file in $(find . -name '*.py'); do
              result = wizard.run_full_analysis(
                  open(file).read(), file, 'python'
              )
              if any(i.severity == 'error' for i in result.issues):
                  print(f'Critical issues in {file}')
                  sys.exit(1)
          done
          "
```

### Cost Optimization

**Use Prompt Caching (Claude):**

```python
from empathy_llm_toolkit.providers import AnthropicProvider

# Prompt caching reduces cost by 90% for repeated prompts
provider = AnthropicProvider(
    use_prompt_caching=True,  # Enable caching
    model="claude-3-5-sonnet-20241022"
)

# System prompts and large contexts are cached automatically
```

**Smart Model Selection:**

```python
# Use Haiku for simple tasks (25x cheaper)
fast_llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307",
    target_level=2
)

# Use Sonnet for complex reasoning (balanced)
standard_llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",
    target_level=4
)

# Use Opus only for most complex tasks
advanced_llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-opus-20240229",
    target_level=5
)

# Route appropriately
if complexity == "low":
    result = await fast_llm.interact(user_id, input)
elif complexity == "medium":
    result = await standard_llm.interact(user_id, input)
else:
    result = await advanced_llm.interact(user_id, input)
```

**Local Models for Privacy:**

```python
# Use local models for sensitive data
local_llm = EmpathyLLM(
    provider="local",
    endpoint="http://localhost:11434",
    model="llama2",
    target_level=2
)

# No data leaves your machine!
result = await local_llm.interact(
    user_id="internal",
    user_input="Analyze this proprietary code..."
)
```

---

## Integration Examples

### IDE Integration (VS Code Extension)

```typescript
// extension.ts
import * as vscode from 'vscode';
import { exec } from 'child_process';

export function activate(context: vscode.ExtensionContext) {
    let disposable = vscode.commands.registerCommand(
        'empathy.analyzeFile',
        async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) return;

            const document = editor.document;
            const code = document.getText();
            const filePath = document.fileName;

            // Run SecurityWizard
            const result = await runWizard('security', code, filePath);

            // Show results
            showResults(result);
        }
    );

    context.subscriptions.push(disposable);
}

async function runWizard(
    wizardType: string,
    code: string,
    filePath: string
): Promise<any> {
    return new Promise((resolve, reject) => {
        const python = `
from coach_wizards import SecurityWizard
wizard = SecurityWizard()
result = wizard.run_full_analysis('''${code}''', '${filePath}', 'python')
print(result.to_json())
`;

        exec(`python -c "${python}"`, (error, stdout, stderr) => {
            if (error) reject(error);
            resolve(JSON.parse(stdout));
        });
    });
}
```

### FastAPI Integration

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from empathy_llm_toolkit import EmpathyLLM
from coach_wizards import SecurityWizard
import os

app = FastAPI()

# Initialize once
llm = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

security_wizard = SecurityWizard()

class CodeAnalysisRequest(BaseModel):
    code: str
    file_path: str
    language: str
    project_context: dict = {}

class ChatRequest(BaseModel):
    user_id: str
    message: str
    context: dict = {}

@app.post("/api/analyze")
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code with SecurityWizard"""
    result = security_wizard.run_full_analysis(
        code=request.code,
        file_path=request.file_path,
        language=request.language,
        project_context=request.project_context
    )

    return {
        "summary": result.summary,
        "issues": [
            {
                "severity": i.severity,
                "message": i.message,
                "line": i.line_number,
                "fix": security_wizard.suggest_fixes(i)
            }
            for i in result.issues
        ],
        "predictions": [
            {
                "type": p.issue_type,
                "date": p.predicted_date.isoformat(),
                "probability": p.probability,
                "impact": p.impact,
                "prevention": p.prevention_steps
            }
            for p in result.predictions
        ]
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Chat with Empathy Framework"""
    result = await llm.interact(
        user_id=request.user_id,
        user_input=request.message,
        context=request.context
    )

    return {
        "response": result['content'],
        "level": result['level_used'],
        "level_description": result['level_description'],
        "proactive": result['proactive']
    }

@app.post("/api/feedback")
async def provide_feedback(user_id: str, outcome: str):
    """Provide feedback to build trust"""
    llm.update_trust(user_id, outcome=outcome)
    stats = llm.get_statistics(user_id)
    return stats
```

### Slack Bot Integration

```python
from slack_bolt import App
from empathy_llm_toolkit import EmpathyLLM
import os

app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

llm = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

@app.message("help")
async def handle_help(message, say):
    user_id = message['user']
    user_input = message['text']

    result = await llm.interact(
        user_id=user_id,
        user_input=user_input,
        context={
            "channel": message['channel'],
            "platform": "slack"
        }
    )

    await say(
        f"*Level {result['level_used']} Response*\n\n{result['content']}"
    )

@app.message("analyze")
async def handle_analyze(message, say):
    # Extract code from message
    code = extract_code_from_message(message['text'])

    from coach_wizards import SecurityWizard
    wizard = SecurityWizard()
    result = wizard.run_full_analysis(code, "code.py", "python")

    issues_text = "\n".join([
        f"• [{i.severity}] Line {i.line_number}: {i.message}"
        for i in result.issues
    ])

    await say(
        f"*Security Analysis*\n\n{result.summary}\n\n*Issues:*\n{issues_text}"
    )

if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
```

---

## Troubleshooting

### Common Issues

#### "API key not found"

**Problem:** Framework can't find your API key.

**Solution:**

```bash
# Check if set
echo $ANTHROPIC_API_KEY

# Set for current session
export ANTHROPIC_API_KEY=sk-ant-your-key

# Set permanently
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key' >> ~/.bashrc
source ~/.bashrc

# Or use .env file
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-your-key
EOF

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

#### "Trust level too low for Level X"

**Problem:** Trying to use higher level before building trust.

**Solution:**

```python
# Force level for testing
result = await llm.interact(
    user_id="test",
    user_input="Test",
    force_level=4  # Force Level 4
)

# Or build trust properly
for i in range(20):
    await llm.interact(user_id="user", user_input=f"Query {i}")
    llm.update_trust("user", outcome="success")

# Check trust level
stats = llm.get_statistics("user")
print(f"Trust: {stats['trust_level']}")  # Should be > 0.8 for Level 4
```

#### "Module not found: coach_wizards"

**Problem:** Wizards not in Python path.

**Solution:**

```bash
# Install in development mode
cd /path/to/Empathy-framework
pip install -e .

# Or add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/Empathy-framework"

# Verify
python -c "from coach_wizards import SecurityWizard; print('Success!')"
```

#### Slow Response Times

**Problem:** LLM calls are slow.

**Solution:**

```python
# Use faster model
llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307",  # Much faster
    target_level=3
)

# Enable prompt caching (Claude)
from empathy_llm_toolkit.providers import AnthropicProvider
provider = AnthropicProvider(
    use_prompt_caching=True,  # 90% faster on repeated calls
    model="claude-3-5-sonnet-20241022"
)

# Use local model
local_llm = EmpathyLLM(
    provider="local",
    endpoint="http://localhost:11434",
    model="llama2"
)
```

#### High LLM Costs

**Problem:** API costs are too high.

**Solution:**

```python
# 1. Enable prompt caching (90% cost reduction)
provider = AnthropicProvider(use_prompt_caching=True)

# 2. Use cheaper models for simple tasks
fast_llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307",  # 25x cheaper
    target_level=2
)

# 3. Use local models for development
dev_llm = EmpathyLLM(
    provider="local",
    model="llama2"  # Free!
)

# 4. Reduce max_tokens
result = await llm.interact(
    user_id="user",
    user_input="Question",
    max_tokens=512  # Limit response length
)
```

### Debugging

**Enable debug logging:**

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Now see detailed logs
result = await llm.interact(user_id="test", user_input="Test")
```

**Inspect state:**

```python
# Check user state
state = llm._get_or_create_state("user")
print(f"Trust: {state.trust_level}")
print(f"Interactions: {len(state.interactions)}")
print(f"Patterns: {len(state.detected_patterns)}")

# Get statistics
stats = llm.get_statistics("user")
print(stats)
```

**Test wizard directly:**

```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()

# Test with known vulnerable code
test_code = "SELECT * FROM users WHERE id='" + user_id + "'"
result = wizard.run_full_analysis(test_code, "test.py", "python")

print(f"Issues found: {len(result.issues)}")
for issue in result.issues:
    print(f"  {issue.message}")
```

---

## Advanced Topics

### Custom Wizard Development

Build domain-specific wizards:

```python
from coach_wizards import BaseCoachWizard, WizardIssue, WizardPrediction
from datetime import datetime, timedelta

class CustomWizard(BaseCoachWizard):
    def __init__(self):
        super().__init__(
            name="CustomWizard",
            category="custom",
            languages=['python', 'javascript']
        )

    def analyze_code(self, code, file_path, language):
        issues = []

        # Your analysis logic
        if "bad_pattern" in code:
            issues.append(WizardIssue(
                severity="error",
                message="Bad pattern detected",
                file_path=file_path,
                line_number=0,
                code_snippet=code[:100],
                fix_suggestion="Use good pattern instead",
                category="custom",
                confidence=0.9
            ))

        return issues

    def predict_future_issues(self, code, file_path, project_context, timeline_days=90):
        predictions = []

        # Your prediction logic
        if project_context.get("growth_rate") > 0.2:
            predictions.append(WizardPrediction(
                predicted_date=datetime.now() + timedelta(days=45),
                issue_type="Scalability bottleneck",
                probability=0.75,
                impact="high",
                prevention_steps=[
                    "Implement caching",
                    "Add load balancing",
                    "Optimize database queries"
                ],
                reasoning="High growth rate will exceed current capacity"
            ))

        return predictions

    def suggest_fixes(self, issue):
        return f"To fix {issue.message}, try..."

# Use your wizard
wizard = CustomWizard()
result = wizard.run_full_analysis(code, file_path, language, context)
```

### Plugin Development

Create plugins for new domains:

```python
from empathy_os.plugins import BasePlugin, PluginMetadata

class MyDomainPlugin(BasePlugin):
    def get_metadata(self):
        return PluginMetadata(
            name="My Domain Plugin",
            version="1.0.0",
            domain="my_domain",
            description="Plugin for my domain",
            author="Your Name",
            license="Apache-2.0",
            requires_core_version="1.0.0"
        )

    def register_wizards(self):
        return {
            "my_wizard": MyCustomWizard,
            "another_wizard": AnotherWizard
        }

    def register_patterns(self):
        return {
            "domain": "my_domain",
            "patterns": {
                "pattern_id": {
                    "description": "Pattern description",
                    "indicators": ["indicator1", "indicator2"],
                    "threshold": "metric > value",
                    "recommendation": "Action to take"
                }
            }
        }
```

### Multi-Tenant Usage

Support multiple teams/users:

```python
from empathy_llm_toolkit import EmpathyLLM

class MultiTenantEmpathy:
    def __init__(self):
        self.llm = EmpathyLLM(provider="anthropic", target_level=4)
        self.team_configs = {}

    def add_team(self, team_id, config):
        self.team_configs[team_id] = config

    async def interact_for_team(self, team_id, user_id, user_input):
        # Use team-specific user_id
        full_user_id = f"{team_id}:{user_id}"

        result = await self.llm.interact(
            user_id=full_user_id,
            user_input=user_input,
            context=self.team_configs.get(team_id, {})
        )

        return result

# Usage
multi = MultiTenantEmpathy()
multi.add_team("team_a", {"project": "api", "tech_stack": "python"})
multi.add_team("team_b", {"project": "frontend", "tech_stack": "react"})

result_a = await multi.interact_for_team("team_a", "alice", "Question")
result_b = await multi.interact_for_team("team_b", "bob", "Question")
```

### Performance Monitoring

Track framework performance:

```python
import time
from empathy_llm_toolkit import EmpathyLLM

class MonitoredEmpathyLLM(EmpathyLLM):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.metrics = []

    async def interact(self, *args, **kwargs):
        start = time.time()
        result = await super().interact(*args, **kwargs)
        duration = time.time() - start

        self.metrics.append({
            "duration": duration,
            "level": result['level_used'],
            "tokens": result['metadata']['tokens_used'],
            "timestamp": time.time()
        })

        return result

    def get_metrics_summary(self):
        return {
            "total_calls": len(self.metrics),
            "avg_duration": sum(m['duration'] for m in self.metrics) / len(self.metrics),
            "total_tokens": sum(m['tokens'] for m in self.metrics)
        }

# Usage
llm = MonitoredEmpathyLLM(provider="anthropic", target_level=4)
# ... use normally ...
print(llm.get_metrics_summary())
```

---

## Support & Resources

### Documentation

- **Quick Start Guide:** [QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md)
- **API Reference:** [API_REFERENCE.md](API_REFERENCE.md)
- **User Guide:** This document
- **CLI Guide:** [CLI_GUIDE.md](CLI_GUIDE.md)

### Community

- **GitHub:** https://github.com/Deep-Study-AI/Empathy
- **Discussions:** https://github.com/Deep-Study-AI/Empathy/discussions
- **Issues:** https://github.com/Deep-Study-AI/Empathy/issues

### Commercial Support

**$99/developer/year**

- Priority bug fixes and feature requests
- Direct access to core development team
- Guaranteed response times
- Security advisories
- Upgrade assistance

**Learn more:** [Pricing](/pricing)

### Contact

**Developer:** Patrick Roebuck
**Email:** patrick.roebuck@deepstudyai.com
**Organization:** Smart AI Memory, LLC

---

## Conclusion

The Empathy Framework transforms AI from a simple tool into a collaborative partner that learns, predicts, and prevents problems before they occur. With Level 4 Anticipatory Empathy, you can:

- **Catch bugs before they manifest**
- **Predict bottlenecks weeks in advance**
- **Build trust through consistent collaboration**
- **Scale development velocity 4-6x**

All at zero cost (Fair Source 0.9 open source) with infinite ROI.

**Welcome to the future of AI-human collaboration!**

---

**Copyright 2025 Smart AI Memory, LLC**
**Licensed under Fair Source 0.9**
