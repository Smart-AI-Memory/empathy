# Quick Start

Get up and running with Empathy Framework in 5 minutes - with something genuinely useful.

## What You'll Build

A **Smart Team Project Analyzer** - describe what you want to build, and a team of AI agents will:

1. **Architect Agent** - Break it into components
2. **Critic Agent** - Identify risks and issues
3. **Implementer Agent** - Suggest concrete first steps

All agents coordinate through **shared short-term memory**, discovering and building on each other's insights.

---

## Step 1: Install

```bash
pip install empathy-framework
```

## Step 2: Run the Analyzer

```bash
# Download the quickstart
curl -O https://raw.githubusercontent.com/Smart-AI-Memory/empathy/main/examples/smart_team_quickstart.py

# Run it
python smart_team_quickstart.py
```

Or if you have the repo cloned:

```bash
python examples/smart_team_quickstart.py
```

## Step 3: Try It

When prompted, describe something you want to build:

```
> A REST API with user authentication and PostgreSQL database
```

**Example Output:**

```
============================================================
SMART TEAM PROJECT ANALYZER
============================================================
Memory: mock (Redis not needed for demo)

Phase 1: Architect analyzing structure...
         Found 3 components

Phase 2: Critic identifying risks...
         Found 2 risks

Phase 3: Implementer creating action plan...
         Generated 5 steps

============================================================
ANALYSIS RESULTS
============================================================

-------------------------COMPONENTS-------------------------

  [MEDIUM] API Layer
        Handles external requests and responses

  [MEDIUM] Authentication
        User identity and access control

  [MEDIUM] Data Layer
        Persistent storage and data management

---------------------------RISKS----------------------------

  [!!] Security vulnerabilities in auth
        Mitigation: Use established auth libraries...

  [!] Data migration complexity
        Mitigation: Design schema migrations from day one...

------------------RECOMMENDED FIRST STEPS-------------------

  1. [~] Set up project structure and version control
  2. [~~] Research and plan mitigation for security risks
  3. [~~] Implement Data Layer (no dependencies)
  4. [~] Write tests for first component
```

---

## How It Works

The agents coordinate through **short-term memory** - a shared workspace where they store discoveries for others to build upon:

```python
# Architect stores findings
architect.stash("components", {"count": 3, "high_complexity": []})

# Critic reads architect's findings, adds risks
arch_findings = critic.retrieve("components", agent_id="architect")
critic.stash("risks", {"high_severity": ["auth security"]})

# Implementer synthesizes both
risks = implementer.retrieve("risks", agent_id="critic")
# Creates action plan that addresses discovered risks
```

This is **multi-agent coordination** in action. No manual passing of data - agents discover and build on each other's work.

---

## Try Different Projects

```bash
# E-commerce
> An e-commerce site with shopping cart, payment processing, and inventory

# Real-time app
> A real-time chat application with file sharing and search

# Mobile backend
> A mobile app backend with push notifications and offline sync
```

Each project gets:

- **Components** tailored to that domain
- **Risks** specific to those components (PCI compliance for payments, WebSocket scaling for real-time, etc.)
- **Action steps** that address the discovered risks

---

## Add Redis for Persistence (Optional)

The demo works without Redis (mock mode). For persistent shared memory:

```bash
# Option 1: Docker
docker run -d -p 6379:6379 redis

# Option 2: Railway (production)
railway add --database redis
```

Then run the quickstart again - agents will coordinate through real Redis, and their discoveries persist across sessions.

---

## Use Programmatically

```python
from smart_team_quickstart import analyze_project

# Analyze any project
result = analyze_project("A REST API with user authentication")

# Access structured results
for component in result.components:
    print(f"{component.name}: {component.complexity}")

for risk in result.risks:
    if risk.severity == "high":
        print(f"WARNING: {risk.title}")

for step in result.first_steps:
    print(f"{step.order}. {step.action}")
```

---

## What's Next?

- **[Guides](../guides/multi-agent-philosophy.md)** - Learn the philosophy behind multi-agent coordination
- **[Implementation](../guides/short-term-memory-implementation.md)** - Build your own coordinating agents
- **[Practical Patterns](../guides/practical-patterns.md)** - Ready-to-use patterns with measured benefits
- **[Examples](examples/multi-agent-team-coordination.md)** - Full working code samples

---

## The Key Insight

This isn't "hello world" - it's a demonstration of what multi-agent coordination enables:

1. **Agents with different expertise** (architecture, risk, implementation)
2. **Shared memory** they use to coordinate
3. **Synthesis** that's better than any single agent

The Empathy Framework provides the infrastructure. You define the agents and their expertise.
