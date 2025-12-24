# Documentation Patterns for Empathy Framework v1.8.0

**Purpose**: Define consistent patterns for creating high-quality, user-focused documentation
**Audience**: Documentation contributors (primarily Patrick)
**Last Updated**: 2025-01-25

---

## Overview: The Four Types of Documentation

Based on the [Diátaxis framework](https://diataxis.fr/), we organize documentation into four types:

```
                    User is STUDYING              User is WORKING
                    ─────────────────────────────────────────────
Practical Steps  │  📚 TUTORIALS               │  📋 HOW-TO GUIDES
(What to do)     │  Learning-oriented          │  Problem-oriented
                    │  "Teach me"                 │  "Show me how"
                    ─────────────────────────────────────────────
Theoretical      │  💡 EXPLANATION             │  📖 REFERENCE
Knowledge        │  Understanding-oriented     │  Information-oriented
(Why it works)   │  "Help me understand"       │  "Tell me about"
```

**Our Implementation**:
- **Tutorials**: `docs/examples/` (e.g., simple-chatbot.md, sbar-clinical-handoff.md)
- **How-To Guides**: `docs/guides/` (e.g., healthcare-applications.md, deployment.md)
- **Reference**: `docs/api-reference/` (e.g., empathy-os.md, config.md)
- **Explanation**: `docs/concepts/` (e.g., empathy-levels.md, trust-building.md)

---

## Pattern 1: Quick Win (5-Minute Success)

**Purpose**: Get users to working code in 5 minutes or less
**Location**: Homepage (`docs/index.md`) and Quick Start (`docs/getting-started/quickstart.md`)

### Structure

```markdown
# Quick Start

Get up and running with Empathy Framework in 5 minutes!

## Step 1: Install

```bash
pip install empathy-framework
```

## Step 2: Create Your First Chatbot

Create a file `my_first_bot.py`:

```python
from empathy_os import EmpathyOS

# Create Level 3 (Proactive) chatbot
empathy = EmpathyOS(
    user_id="user_123",
    target_level=3,
    confidence_threshold=0.70
)

# Interact
response = empathy.interact(
    user_id="user_123",
    user_input="How do I fix this bug in Python?",
    context={}
)

print(f"Response: {response.response}")
print(f"Empathy Level: {response.level}")
print(f"Confidence: {response.confidence:.0%}")
```

## Step 3: Run It

```bash
python my_first_bot.py
```

## What's Next?

- [Simple Chatbot Tutorial](../examples/simple-chatbot.md) - Learn all 5 empathy levels
- [Configuration Guide](configuration.md) - Customize your bot
```

### Pattern Rules

✅ **DO**:
- Complete working example in ≤20 lines
- No configuration required (use defaults)
- Clear next steps at the end
- Show immediate output/results

❌ **DON'T**:
- Explain concepts (save for tutorials)
- Require multiple files
- Need API keys or external services
- Take >5 minutes to complete

---

## Pattern 2: Progressive Disclosure (Simple → Complex)

**Purpose**: Start simple, reveal complexity gradually
**Location**: All tutorials and guides

### Example: Empathy Levels Tutorial

```markdown
# Simple Chatbot Tutorial

## Part 1: Level 1 (Reactive) - 5 minutes

```python
# Simplest possible - just responds
empathy = EmpathyOS(user_id="user_123", target_level=1)
response = empathy.interact(user_id="user_123", user_input="Hello", context={})
```

## Part 2: Level 2 (Guided) - 10 minutes

```python
# Now it asks clarifying questions
empathy = EmpathyOS(user_id="user_123", target_level=2)
response = empathy.interact(
    user_id="user_123",
    user_input="How do I deploy?",
    context={"project": "web_app"}  # ← Added context
)

# Show clarifying questions
if response.clarifying_questions:
    for q in response.clarifying_questions:
        print(f"? {q}")
```

## Part 3: Level 3 (Proactive) - 15 minutes

```python
# Now it suggests improvements
# + persistence for learning
empathy = EmpathyOS(
    user_id="user_123",
    target_level=3,
    persistence_enabled=True  # ← New feature
)
```

## Part 4: Level 4 (Anticipatory) - 20 minutes

```python
# Now it predicts problems
# + pattern library for multi-agent
# + LLM integration
```
```

### Pattern Rules

✅ **DO**:
- Start with minimal code
- Add ONE new concept per section
- Build on previous sections
- Mark difficulty levels (beginner/intermediate/advanced)

❌ **DON'T**:
- Jump to advanced features immediately
- Introduce multiple concepts simultaneously
- Assume prior knowledge

---

## Pattern 3: Code-First, Explanation After

**Purpose**: Show working code immediately, explain later
**Location**: Tutorials and API reference

### Example Structure

```markdown
## Creating Multi-Agent Teams

```python
# Frontend agent
frontend = EmpathyOS(
    user_id="frontend_agent",
    shared_library="team_patterns.db"
)

# Backend agent
backend = EmpathyOS(
    user_id="backend_agent",
    shared_library="team_patterns.db"  # ← Same database
)

# They automatically share patterns!
```

**What's happening:**

1. Both agents connect to the same pattern library
2. When `frontend` discovers a useful pattern, `backend` can use it
3. Patterns are automatically synchronized

**When to use:**
- Team collaboration (multiple developers/agents)
- Knowledge sharing across projects
- Faster onboarding (new agents learn from existing patterns)

**Performance impact:**
- 80% faster feature delivery (8 days → 4 days)
- 68% pattern reuse rate across agents
```

### Pattern Rules

✅ **DO**:
- Show complete working code first
- Explain "what's happening" second
- Include "when to use" section
- Add performance/impact metrics

❌ **DON'T**:
- Explain concepts before showing code
- Show partial/incomplete code
- Skip practical use cases

---

## Pattern 4: Multiple Entry Points (By Role/Use Case)

**Purpose**: Different users need different starting points
**Location**: Homepage, guides

### Entry Point Matrix

| User Type | Primary Goal | Entry Point | Key Content |
|-----------|--------------|-------------|-------------|
| **New Developer** | Get started fast | Quick Start → Simple Chatbot | 5-min example, Level 1-3 tutorial |
| **Healthcare Practitioner** | HIPAA-compliant SBAR | Healthcare Guide → SBAR Tutorial | Clinical protocols, $2M ROI |
| **Enterprise Architect** | Production deployment | Deployment Guide → Security | PostgreSQL, Kubernetes, monitoring |
| **AI Researcher** | Understand anticipatory AI | Concepts → Level 4 Explanation | Trust building, pattern learning |
| **API User** | Reference docs | API Reference → EmpathyOS | Method signatures, parameters |

### Implementation: Homepage Sections

```markdown
# Empathy Framework

## Get Started in 5 Minutes
→ For developers who want to try it immediately

## Healthcare Applications
→ For clinical practitioners (SBAR, HIPAA, $2M ROI)

## Enterprise Deployment
→ For architects planning production deployments

## Understanding Empathy Levels
→ For researchers and students learning the concepts

## API Documentation
→ For developers integrating into existing systems
```

### Pattern Rules

✅ **DO**:
- Identify 4-6 primary user personas
- Create clear entry points for each
- Use role-specific language (clinical vs. technical)
- Link between related paths

❌ **DON'T**:
- Force everyone through same path
- Use generic "Getting Started" for all users
- Assume technical knowledge

---

## Pattern 5: Show Value Early (ROI First, Details Later)

**Purpose**: Hook users with impact metrics before diving into implementation
**Location**: Guide introductions, healthcare docs

### Example: Healthcare Guide Opening

```markdown
# Healthcare Applications with Empathy Framework

## Impact Summary

**60% time savings** on patient handoffs
**$2M+ annual value** for 100-bed hospital
**Zero false negatives** in critical safety alerts

*Mercy Hospital reduced documentation time from 15 minutes to 6 minutes per handoff, saving 3.2 FTE annually.*

---

## Why Healthcare Needs Level 4 Intelligence

Traditional EHR systems are reactive (Level 1):
- Clinician enters data
- System stores data
- No proactive alerts or predictions

Empathy Framework adds Level 4 Anticipatory Intelligence:
- ✅ Predicts incomplete SBAR reports before submission
- ✅ Flags critical information missing from handoff
- ✅ Suggests relevant patient history automatically

---

## Quick Start: SBAR Clinical Handoff

```python
from empathy_os import EmpathyOS
from empathy_llm_toolkit.wizards import ClinicalProtocolMonitor
```
```

### Pattern Rules

✅ **DO**:
- Lead with concrete metrics (60% savings, $2M ROI)
- Include real-world case studies
- Quantify impact before showing code
- Use domain-specific language (FTE for healthcare)

❌ **DON'T**:
- Start with technical details
- Use vague claims ("improves efficiency")
- Skip case studies or examples

---

## Pattern 6: Graduated Examples (Working → Realistic → Production)

**Purpose**: Show progression from toy example to production-ready code
**Location**: Tutorials and guides

### Three-Stage Example Pattern

#### Stage 1: Working Example (5 minutes)

```python
# Minimal working example - no error handling
empathy = EmpathyOS(user_id="user_123", target_level=4)
response = empathy.interact(user_id="user_123", user_input="Deploy?", context={})
print(response.response)
```

**Purpose**: Prove it works, understand basics

#### Stage 2: Realistic Example (15 minutes)

```python
# Add configuration, context, error handling
import os
from empathy_os import EmpathyOS, load_config

config = load_config(filepath="empathy.config.yml")
empathy = EmpathyOS.from_config(config)

try:
    response = empathy.interact(
        user_id=config.user_id,
        user_input=user_input,
        context={
            "environment": "production",
            "services": ["api", "database", "cache"],
            "deployment_window": "friday_afternoon"
        }
    )

    if response.level >= 4 and response.predictions:
        print("⚠️  Predictions:")
        for pred in response.predictions:
            print(f"  • {pred}")

except Exception as e:
    logger.error(f"Interaction failed: {e}")
    # Fallback to Level 1
```

**Purpose**: Real-world scenario, proper error handling

#### Stage 3: Production Example (30 minutes)

```python
# Full production setup with:
# - Async operation
# - Rate limiting
# - Monitoring/metrics
# - Graceful degradation
# - Security controls (PII scrubbing)
# - Audit logging (HIPAA compliance)

import asyncio
from empathy_os import EmpathyOS
from empathy_llm_toolkit import EmpathyLLM
from empathy_llm_toolkit.security import PIIScrubber, AuditLogger

async def production_interact(user_id: str, user_input: str, context: dict):
    # Initialize with full security
    llm = EmpathyLLM(
        provider="anthropic",
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        enable_pii_scrubbing=True,
        enable_secrets_detection=True,
        enable_audit_logging=True
    )

    empathy = EmpathyOS(
        user_id=user_id,
        target_level=4,
        llm_provider=llm,
        persistence_enabled=True,
        metrics_enabled=True
    )

    # Rate limiting
    await rate_limiter.wait_for_token(user_id)

    # Scrub PII from input
    scrubber = PIIScrubber()
    scrubbed_input = scrubber.scrub(user_input)

    # Process with monitoring
    with metrics.timer("empathy.interact.duration"):
        response = await empathy.interact_async(
            user_id=user_id,
            user_input=scrubbed_input,
            context=context
        )

    # Audit log
    audit_logger.log_llm_request(
        user_id=user_id,
        prompt_length=len(scrubbed_input),
        response_level=response.level,
        pii_scrubbed=len(scrubber.get_scrubbed_items(user_input))
    )

    return response
```

**Purpose**: Production-ready, handles edge cases, monitoring, compliance

### Pattern Rules

✅ **DO**:
- Always show all three stages
- Explain why each addition is necessary
- Mark which stage is appropriate for which use case
- Include production checklist

❌ **DON'T**:
- Jump from toy example to production
- Skip intermediate realistic example
- Show production code without explanation

---

## Pattern 7: Problem-Solution-Impact (PSI)

**Purpose**: Frame documentation around user problems, not features
**Location**: Guides, use case documentation

### PSI Template

```markdown
## Problem: Friday Afternoon Deployments Have 3x Higher Incident Rate

**Context**: Your team deploys to production every Friday afternoon. Last month:
- 3 major incidents (all on Fridays)
- 12 hours of weekend emergency fixes
- $15K in incident costs

**Why it happens**:
- Weekend support team is understaffed
- Developers are mentally checking out for the weekend
- Rollback is harder on Fridays (deploys accumulate)

---

## Solution: Level 4 Anticipatory Alerts

```python
empathy = EmpathyOS(user_id="deployment_bot", target_level=4)

response = empathy.interact(
    user_id="developer",
    user_input="I'm deploying the auth refactor to production",
    context={
        "day": "friday",
        "time": "16:30",
        "changes": ["authentication", "database_migration"],
        "deployment_environment": "production"
    }
)

# Level 4 prediction:
# "🔮 High Risk: Friday afternoon deployment with database migration.
#  Recommend:
#  1. Delay until Monday 9am
#  2. If urgent, deploy behind feature flag
#  3. Have rollback plan ready
#  Confidence: 89%"
```

---

## Impact: 75% Reduction in Friday Incidents

**After implementing Level 4 alerts:**
- Friday incidents: 3/month → 0.75/month (75% reduction)
- Weekend emergency hours: 12 hours → 3 hours
- Incident costs: $15K → $4K/month
- Developer satisfaction: ↑ (no more weekend calls)

**ROI**: $132K annual savings for 10-person team
```

### Pattern Rules

✅ **DO**:
- Start with relatable problem
- Quantify problem impact
- Show specific solution code
- Measure improvement (before/after metrics)

❌ **DON'T**:
- Start with "Feature X allows you to..."
- Show features without context
- Skip impact metrics

---

## Pattern 8: Reference Documentation (Scannable)

**Purpose**: API reference users need to find information quickly, not read linearly
**Location**: `docs/api-reference/`

### Reference Template

```markdown
# EmpathyOS API Reference

## Overview

One-sentence description of what this class does.

## Quick Example

```python
# Minimal working example (3-5 lines)
empathy = EmpathyOS(user_id="user_123", target_level=4)
response = empathy.interact(user_id="user_123", user_input="...", context={})
```

---

## Class Reference

::: empathy_os.EmpathyOS
    options:
      show_source: true
      heading_level: 3

---

## Methods

### `__init__()`

**Purpose**: Initialize EmpathyOS instance

**Parameters**:
- `user_id` (str, required): Unique user identifier
- `target_level` (int, default=4): Target empathy level (1-5)
- `confidence_threshold` (float, default=0.75): Minimum confidence (0.0-1.0)

**Returns**: None

**Raises**:
- `ValueError`: If target_level not in 1-5
- `ValueError`: If confidence_threshold not in 0.0-1.0

**Example**:
```python
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75
)
```

**See Also**:
- [Configuration Guide](../getting-started/configuration.md)
- [Quick Start](../getting-started/quickstart.md)

---

### `interact()`

**Purpose**: Process user input and generate empathetic response

**Parameters**:
- `user_id` (str, required): User identifier
- `user_input` (str, required): User's message
- `context` (dict, optional): Additional context

**Returns**: `EmpathyResponse`
- `response` (str): The AI's response
- `level` (int): Empathy level used (1-5)
- `confidence` (float): Confidence score (0.0-1.0)
- `predictions` (List[str]): Level 4 predictions (if applicable)

**Example**:
```python
response = empathy.interact(
    user_id="user_123",
    user_input="I'm deploying to production",
    context={"environment": "production"}
)

print(response.response)      # AI response
print(response.level)         # 4
print(response.predictions)   # ["Risk: ...", "Suggestion: ..."]
```

**Performance**: Typical response time: 500-2000ms

**See Also**:
- [EmpathyResponse API](core.md#empathyresponse)
- [Level 4 Tutorial](../examples/simple-chatbot.md#level-4-anticipatory)
```

### Pattern Rules

✅ **DO**:
- Include quick example at top
- Use consistent method documentation format
- Show expected return values
- Include "See Also" links
- List performance characteristics

❌ **DON'T**:
- Write prose paragraphs (use scannable lists)
- Skip return types or error cases
- Forget practical examples

---

## Pattern 9: Explanation Documentation (Understanding)

**Purpose**: Help users understand WHY something works, not just HOW
**Location**: `docs/concepts/`

### Explanation Template

```markdown
# Understanding Trust Building in Empathy Framework

## The Core Insight

**Traditional AI systems treat every interaction the same.**

Empathy Framework recognizes that **trust must be earned**:
- New users get conservative responses (Level 1-2)
- As trust builds through successful interactions, more advanced features unlock
- If trust erodes (failures), system falls back to safer levels

This mirrors human relationships: you don't give deep advice to strangers.

---

## How Trust Works

### Trust Levels and Empathy Levels

```
Trust Level     Empathy Level     Characteristics
───────────────────────────────────────────────────
0% - 20%   →   Level 1           Basic Q&A only
20% - 40%  →   Level 2           Asks questions
40% - 60%  →   Level 3           Suggests improvements
60% - 80%  →   Level 4           Predicts problems
80% - 100% →   Level 5           Transforms workflows
```

### Trust Dynamics

**Trust increases** on successful interactions:
- User marks response as helpful
- User accepts a prediction
- User follows a suggestion
- Default: +5% per success

**Trust decreases** on failures:
- User marks response as unhelpful
- User rejects a prediction
- System makes incorrect suggestion
- Default: -10% per failure (degrades faster than it builds)

**Why asymmetric?**
- Trust is hard to build, easy to lose (human psychology)
- Conservative bias prevents premature advanced features
- Protects users from over-confident predictions

---

## Design Decisions

### Why not just use Level 4 immediately?

**Problem**: Level 4 predictions can be wrong
- False positives annoy users ("boy who cried wolf")
- False negatives damage credibility

**Solution**: Trust-gated progression
- Level 1-2 establish baseline (can't be wrong about Q&A)
- Level 3 tests suggestions (low risk)
- Level 4 unlocks only after proven reliability

### Why 75% confidence threshold?

Based on research and testing:
- <70%: Too many false positives
- 70-75%: Balanced (our default)
- 75-85%: Conservative (recommended for high-stakes)
- >85%: May miss useful predictions

**Healthcare**: We use 85% for clinical predictions (safety-critical)
**Software**: We use 75% for deployment warnings (lower stakes)

---

## Mental Model: The Trust Ladder

Think of empathy levels as rungs on a ladder:
1. **Ground floor** (Level 1): Anyone can enter
2. **Second floor** (Level 2): You've been here a few times
3. **Third floor** (Level 3): Regular visitor, we know you
4. **Fourth floor** (Level 4): Trusted partner, we anticipate your needs
5. **Penthouse** (Level 5): Strategic advisor, we transform your processes

You can't skip floors. You earn your way up.

---

## Practical Implications

**For developers**:
- Don't expect Level 4 predictions immediately
- Build trust through 10-20 interactions first
- Provide feedback (helps calibration)

**For product teams**:
- Set `trust_building_rate` higher for demos (faster progression)
- Set `trust_erosion_rate` lower for learning environments (more forgiving)

**For enterprises**:
- Pre-seed trust for known users (bypass Level 1-2)
- Use separate trust profiles per domain (deployment trust ≠ code review trust)

---

## See Also

- [Configuration: Trust Settings](../api-reference/config.md#trust-settings)
- [Tutorial: Building Trust](../examples/simple-chatbot.md#trust-progression)
- [Paper: Trust in AI Systems](https://example.com/trust-ai-paper)
```

### Pattern Rules

✅ **DO**:
- Explain WHY design decisions were made
- Include mental models and analogies
- Show trade-offs and alternatives considered
- Link theory to practice ("Practical Implications")

❌ **DON'T**:
- Show code (save for tutorials/reference)
- Skip the "why" (this is the point)
- Use jargon without explanation

---

## Pattern 10: Responsive to User Skill Level

**Purpose**: Same content adapts to beginner/intermediate/advanced users
**Location**: All documentation types

### Implementation: Tabbed Content

```markdown
## Installing Empathy Framework

=== "Beginner"

    **New to Python? Start here.**

    1. Install Python from python.org
    2. Open terminal/command prompt
    3. Run: `pip install empathy-framework`
    4. Verify: `python -c "import empathy_os"`

    **Troubleshooting**:
    - "pip not found": Install pip first
    - "Permission denied": Use `pip install --user empathy-framework`

=== "Intermediate"

    **Quick installation**:
    ```bash
    pip install empathy-framework[full]
    ```

    **Virtual environment** (recommended):
    ```bash
    python -m venv empathy-env
    source empathy-env/bin/activate  # Windows: empathy-env\Scripts\activate
    pip install empathy-framework[full]
    ```

=== "Advanced"

    **Development setup**:
    ```bash
    git clone https://github.com/Smart-AI-Memory/empathy.git
    cd empathy-framework
    pip install -e .[dev]
    pre-commit install
    ```

    **Custom build** (enterprise):
    ```bash
    # Install from private PyPI
    pip install empathy-framework --index-url https://pypi.company.internal

    # Build from source with modifications
    python setup.py develop --config=enterprise.cfg
    ```
```

### Pattern Rules

✅ **DO**:
- Use tabs for skill-level variants
- Default to "Beginner" tab
- Keep advanced content available
- Link between skill levels

❌ **DON'T**:
- Hide advanced content completely
- Assume everyone is advanced
- Make beginners wade through expert content

---

## Writing Style Guide

### Voice and Tone

**General Tone**: Professional but friendly, confident but not arrogant

✅ **Good**: "Level 4 predicts problems before they happen"
❌ **Bad**: "Our revolutionary AI prevents all incidents"

✅ **Good**: "This typically saves 60% of documentation time"
❌ **Bad**: "You'll save tons of time!"

### Code Examples

**Always include**:
- Complete, runnable code
- Expected output
- Time to complete (5 min, 15 min, 30 min)

**Code comments**:
```python
# Good: Explain WHY, not WHAT
confidence_threshold=0.75  # Higher = more conservative predictions

# Bad: States the obvious
confidence_threshold=0.75  # Set confidence threshold to 0.75
```

### Headings

**Use action-oriented headings**:

✅ **Good**: "Deploy to Production", "Configure Trust Levels", "Build Your First Bot"
❌ **Bad**: "Deployment", "Trust Configuration", "Getting Started"

### Lists

**Prefer parallel construction**:

✅ **Good**:
- Install the package
- Create a configuration file
- Run the example

❌ **Bad**:
- Install the package
- You should create a configuration file
- Running the example

---

## Documentation Checklist

### Before Publishing Any Doc

- [ ] **Quick win**: Can user achieve something in ≤5 minutes?
- [ ] **Working code**: All examples run without modification?
- [ ] **Progressive**: Simple → complex progression?
- [ ] **Scannable**: Can user find what they need in ≤10 seconds?
- [ ] **Entry point**: Clear who this is for and why they care?
- [ ] **Links**: Related docs linked (See Also sections)?
- [ ] **Tested**: You personally ran all code examples?
- [ ] **Metrics**: Impact quantified where applicable?
- [ ] **Images**: Screenshots/diagrams included if helpful?
- [ ] **Spell-checked**: No typos or grammar errors?

---

## Examples of Each Pattern

### Current Documentation (Already Done)

| Pattern | Example File | Quality |
|---------|--------------|---------|
| Quick Win | `docs/getting-started/quickstart.md` | ✅ Good |
| Progressive | `docs/examples/simple-chatbot.md` | ✅ Good |
| Code-First | `docs/examples/sbar-clinical-handoff.md` | ✅ Good |
| Graduated | `docs/examples/multi-agent-team-coordination.md` | ✅ Good |
| Reference | `docs/api-reference/empathy-os.md` | ✅ Good |

### To Be Created (Track A - Patrick's Work)

| Pattern | File to Create | Priority |
|---------|----------------|----------|
| PSI | `docs/guides/reducing-friday-incidents.md` | High |
| Explanation | `docs/concepts/trust-building.md` | High |
| Explanation | `docs/concepts/empathy-levels.md` | High |
| Entry Points | `docs/guides/healthcare-applications.md` | High |
| Graduated | `docs/guides/production-deployment.md` | Medium |
| PSI | `docs/guides/multi-agent-coordination.md` | Medium |

---

## Template Files (Copy These)

### Tutorial Template

```markdown
# [Feature Name] Tutorial

**Time**: [X] minutes
**Difficulty**: [Beginner/Intermediate/Advanced]
**Prerequisites**: [List any required knowledge]

## What You'll Build

[1-sentence description + screenshot/demo if possible]

## What You'll Learn

- [Skill 1]
- [Skill 2]
- [Skill 3]

---

## Step 1: [Action]

[Brief explanation]

```python
# Code
```

**Expected output**:
```
[Show what user should see]
```

## Step 2: [Action]

...

## What You Built

[Summary of what was accomplished]

## Next Steps

- [Related tutorial]
- [Advanced guide]
- [API reference]
```

### Guide Template

```markdown
# [How to Accomplish Task]

**Use this guide when**: [Clear use case]

## Problem

[What problem does this solve?]

## Solution Overview

[High-level approach]

## Prerequisites

- [Item 1]
- [Item 2]

---

## Step 1: [Action]

[Detailed instructions]

## Step 2: [Action]

...

## Verification

[How to know it worked]

## Troubleshooting

**Problem**: [Common issue]
**Solution**: [Fix]

## See Also

- [Related guide]
- [API reference]
```

---

## Questions?

When creating new documentation, ask:

1. **Who is this for?** (New developer? Healthcare practitioner? Enterprise architect?)
2. **What are they trying to do?** (Learn? Solve a problem? Understand? Look up reference?)
3. **What's the 5-minute win?** (What can they accomplish quickly?)
4. **What's the real-world impact?** (Time savings? Cost savings? Risk reduction?)
5. **What comes next?** (Where should they go after this doc?)

If you can answer these 5 questions, you can write great documentation.

---

**Last Updated**: 2025-01-25
**Maintained By**: Claude (Track C), Patrick (Track A)
**Feedback**: Open issue or PR on GitHub
