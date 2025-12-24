# Short-Term Memory: Redis-Backed Multi-Agent Coordination

The Empathy Framework provides a Redis-backed short-term memory system for real-time multi-agent coordination, pattern staging, and collaboration state management.

## Overview

Short-term memory enables:
- **Working Memory**: Fast TTL-based storage for intermediate results
- **Pattern Staging**: Validate patterns before promotion to the library
- **Coordination Signals**: Real-time communication between agents
- **Session Management**: Collaborative multi-agent sessions
- **State Persistence**: Save/restore collaboration state

## Quick Start

```python
from empathy_os import EmpathyOS, get_redis_memory, AccessTier

# Get Redis memory (auto-detects Railway, fallback to localhost/mock)
memory = get_redis_memory()

# Create an agent with short-term memory
empathy = EmpathyOS(
    user_id="code_reviewer",
    short_term_memory=memory,
    access_tier=AccessTier.CONTRIBUTOR,
)

# Store working data (expires in 1 hour)
empathy.stash("analysis_results", {"files": 10, "issues": 3})

# Retrieve data
results = empathy.retrieve("analysis_results")
print(results)  # {'files': 10, 'issues': 3}
```

## Configuration

### Environment Variables

```bash
# Railway Redis (recommended for production)
export REDIS_URL="redis://default:password@host:port"

# Local development
export REDIS_URL="redis://localhost:6379"

# Force mock mode (testing)
export REDIS_URL=""
```

### Programmatic Configuration

```python
from empathy_os import get_redis_memory, get_railway_redis, check_redis_connection

# Auto-detect (checks REDIS_URL, falls back to localhost, then mock)
memory = get_redis_memory()

# Explicit Railway Redis
memory = get_railway_redis(
    host="centerbeam.proxy.rlwy.net",
    port=14516,
    password="your_password"
)

# Check connection
if check_redis_connection():
    print("Redis available!")
```

## Access Tiers

Role-based access control for data integrity:

| Tier | Level | Can Read | Can Write | Can Validate | Can Admin |
|------|-------|----------|-----------|--------------|-----------|
| OBSERVER | 1 | ✅ | ❌ | ❌ | ❌ |
| CONTRIBUTOR | 2 | ✅ | ✅ | ❌ | ❌ |
| VALIDATOR | 3 | ✅ | ✅ | ✅ | ❌ |
| STEWARD | 4 | ✅ | ✅ | ✅ | ✅ |

```python
from empathy_os import AccessTier

# Observer: Can only read (monitoring dashboards)
empathy = EmpathyOS(user_id="monitor", access_tier=AccessTier.OBSERVER)

# Contributor: Can read/write (most agents)
empathy = EmpathyOS(user_id="analyzer", access_tier=AccessTier.CONTRIBUTOR)

# Validator: Can promote patterns (senior agents)
empathy = EmpathyOS(user_id="senior_reviewer", access_tier=AccessTier.VALIDATOR)

# Steward: Full admin (system operators)
empathy = EmpathyOS(user_id="admin", access_tier=AccessTier.STEWARD)
```

## Working Memory

Store and retrieve intermediate results:

```python
# Store data (default 1 hour TTL)
empathy.stash("key", {"any": "data"})

# Retrieve your own data
data = empathy.retrieve("key")

# Retrieve another agent's data
other_data = empathy.retrieve("analysis", agent_id="other_agent")
```

## Pattern Staging

Stage discovered patterns for validation before promotion:

```python
from empathy_os import StagedPattern

# Discover and stage a pattern
pattern = StagedPattern(
    pattern_id="pat_auth_001",
    agent_id=empathy.user_id,
    pattern_type="security",
    name="JWT Token Refresh",
    description="Refresh tokens 5 minutes before expiry",
    confidence=0.85,
    code="# Example code here"
)
empathy.stage_pattern(pattern)

# Validators can review and promote
staged = empathy.get_staged_patterns()
for p in staged:
    print(f"Review: {p.name} (confidence: {p.confidence})")
```

## Coordination Signals

Real-time communication between agents:

```python
# Send targeted signal
empathy.send_signal(
    signal_type="analysis_complete",
    data={"files_analyzed": 10, "issues_found": 3},
    target_agent="lead_reviewer"
)

# Broadcast to all
empathy.send_signal(
    signal_type="status_update",
    data={"phase": "testing"}
)

# Receive signals
signals = empathy.receive_signals("analysis_complete")
for sig in signals:
    print(f"From {sig['sender']}: {sig['data']}")
```

## State Persistence

Save and restore collaboration state:

```python
# Update state through interactions
empathy.collaboration_state.trust_level = 0.8
empathy.collaboration_state.successful_interventions = 10

# Persist to Redis (survives restarts)
empathy.persist_collaboration_state()

# Later, restore state
empathy.restore_collaboration_state()
print(empathy.collaboration_state.trust_level)  # 0.8
```

## Multi-Agent Coordination

### AgentCoordinator

Coordinate tasks across a team of agents:

```python
from empathy_os import AgentCoordinator, AgentTask, get_redis_memory

memory = get_redis_memory()
coordinator = AgentCoordinator(memory, team_id="code_review_team")

# Register agents
coordinator.register_agent("security_agent", ["security_review"])
coordinator.register_agent("performance_agent", ["performance_review"])

# Add tasks
task = AgentTask(
    task_id="review_001",
    task_type="security_review",
    description="Review authentication module",
    priority=8
)
coordinator.add_task(task)

# Agents claim and complete tasks
claimed = coordinator.claim_task("security_agent", "security_review")
if claimed:
    # Do work...
    coordinator.complete_task(claimed.task_id, {"vulnerabilities": 0})

# Aggregate results
results = coordinator.aggregate_results()
print(f"Completed: {results['total_completed']}")
```

### TeamSession

Collaborative sessions for multi-agent work:

```python
from empathy_os import TeamSession, get_redis_memory

memory = get_redis_memory()

# Create session
session = TeamSession(
    memory,
    session_id="pr_review_42",
    purpose="Review PR #42"
)

# Add agents
session.add_agent("security_agent")
session.add_agent("performance_agent")
session.add_agent("style_agent")

# Share context
session.share("scope", {"files_changed": 15, "lines_changed": 500})

# Agents retrieve shared context
scope = session.get("scope")

# Signal completion
session.signal("review_complete", {"agent": "security_agent", "passed": True})
```

## Wizards with Redis Memory

Wizards automatically support short-term memory:

```python
from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard
from empathy_os import get_redis_memory

memory = get_redis_memory()

# Create wizard with memory
wizard = SecurityAnalysisWizard(short_term_memory=memory)

# Analysis with automatic caching
result = await wizard.analyze_with_cache({"code": "...", "language": "python"})

# Share context with other wizards
wizard.share_context("security_findings", result["vulnerabilities"])

# Stage discovered patterns
wizard.stage_discovered_pattern(
    pattern_id="sec_001",
    pattern_type="security",
    name="SQL Injection Prevention",
    description="Always use parameterized queries",
    confidence=0.9
)
```

## TTL Strategies

Data expires based on type:

| Type | TTL | Use Case |
|------|-----|----------|
| WORKING_RESULTS | 1 hour | Analysis results, intermediate data |
| STAGED_PATTERNS | 24 hours | Patterns awaiting validation |
| COORDINATION | 5 minutes | Signals, heartbeats |
| CONFLICT_CONTEXT | 7 days | Unresolved conflicts |
| SESSION | 30 minutes | Active collaboration sessions |

## Mock Mode

For testing without Redis:

```python
from empathy_os.redis_memory import RedisShortTermMemory

# Explicit mock mode
memory = RedisShortTermMemory(use_mock=True)

# Auto-mock when Redis unavailable
memory = get_redis_memory()  # Falls back to mock
print(memory.get_stats()["mode"])  # "mock" or "redis"
```

## Railway Deployment

Short-term memory works automatically with Railway:

1. Add Redis plugin to your Railway project
2. Set `REDIS_URL` environment variable (auto-set by Railway)
3. Deploy - memory will auto-connect

```python
# This just works on Railway
memory = get_redis_memory()
# Connects to centerbeam.proxy.rlwy.net:PORT
```

## Best Practices

1. **Use appropriate access tiers** - Don't give all agents STEWARD access
2. **Let TTLs expire** - Don't manually clean up; Redis handles it
3. **Stage before promoting** - All patterns should be validated
4. **Use signals for coordination** - Not polling working memory
5. **Persist state periodically** - Every few minutes for critical agents
6. **Use mock mode for tests** - Avoid Redis dependency in CI

## Example: Multi-Agent Code Review

```python
from empathy_os import (
    EmpathyOS, get_redis_memory, AccessTier,
    AgentCoordinator, AgentTask, TeamSession
)

memory = get_redis_memory()

# 1. Create coordinator
coordinator = AgentCoordinator(memory, team_id="pr_review")

# 2. Create specialized agents
security = EmpathyOS("security", short_term_memory=memory, access_tier=AccessTier.CONTRIBUTOR)
perf = EmpathyOS("performance", short_term_memory=memory, access_tier=AccessTier.CONTRIBUTOR)
lead = EmpathyOS("lead_reviewer", short_term_memory=memory, access_tier=AccessTier.VALIDATOR)

# 3. Register with coordinator
coordinator.register_agent("security", ["security_review"])
coordinator.register_agent("performance", ["performance_review"])

# 4. Add tasks
coordinator.add_task(AgentTask(
    task_id="sec_001", task_type="security_review",
    description="Check for vulnerabilities", priority=9
))
coordinator.add_task(AgentTask(
    task_id="perf_001", task_type="performance_review",
    description="Profile database queries", priority=7
))

# 5. Agents work and signal completion
security.send_signal("review_complete", {"passed": True}, target_agent="lead_reviewer")
perf.send_signal("review_complete", {"issues": 2}, target_agent="lead_reviewer")

# 6. Lead aggregates
signals = lead.receive_signals("review_complete")
print(f"Received {len(signals)} reviews")
```

## API Reference

See the full API documentation:
- [EmpathyOS](empathy-os.md)
- [Multi-Agent Coordination](multi-agent.md)
- [Persistence](persistence.md)

---

*Copyright 2025 Smart AI Memory, LLC. Licensed under Fair Source 0.9.*
