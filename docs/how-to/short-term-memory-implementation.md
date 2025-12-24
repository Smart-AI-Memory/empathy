# Implementing Short-Term Memory

*A practical guide to building multi-agent coordination with measurable outcomes*

---

## What You'll Build

By the end of this chapter, you will have:

- [ ] **Working Redis connection** with automatic fallback to mock mode
- [ ] **Agent coordination** with task distribution and claiming
- [ ] **Pattern staging** with validation workflows
- [ ] **Measurable metrics**: response time, coordination latency, pattern reuse rate

**Expected outcomes**:

| Metric | Without Short-Term Memory | With Short-Term Memory |
|--------|---------------------------|------------------------|
| Agent coordination latency | N/A (no coordination) | < 50ms |
| Pattern rediscovery rate | 100% (every session) | 0% (shared library) |
| Context rebuilding time | ~2-5 seconds per agent | 0 (persisted) |
| Conflict resolution | Manual escalation | Automated synthesis |

---

## Prerequisites

```bash
pip install empathy-framework redis
```

For production: Redis server (local or Railway/cloud)
For development: Mock mode (automatic, no Redis needed)

---

## Part 1: Basic Setup (10 minutes)

### Step 1: Get Redis Memory

```python
from empathy_os import get_redis_memory, check_redis_connection

# Automatic detection:
# 1. Checks REDIS_URL environment variable
# 2. Falls back to localhost:6379
# 3. Falls back to mock mode (in-memory)
memory = get_redis_memory()

# Verify connection
if check_redis_connection():
    print("Connected to Redis")
    stats = memory.get_stats()
    print(f"Mode: {stats['mode']}, Keys: {stats['keys']}")
else:
    print("Using mock mode (no Redis)")
```

### Step 2: Create an Agent with Memory

```python
from empathy_os import EmpathyOS, AccessTier

# Create agent with short-term memory
agent = EmpathyOS(
    user_id="code_reviewer",
    short_term_memory=memory,
    access_tier=AccessTier.CONTRIBUTOR,  # Can read and write
    target_level=4,  # Anticipatory
)

# Verify memory is available
print(f"Has memory: {agent.has_short_term_memory()}")
print(f"Session ID: {agent.session_id}")
```

### Step 3: Basic Operations

```python
# Store working data (expires in 1 hour by default)
agent.stash("current_task", {
    "type": "code_review",
    "files": ["auth.py", "api.py"],
    "started_at": "2024-12-10T10:00:00"
})

# Retrieve data
task = agent.retrieve("current_task")
print(f"Working on: {task['type']} for {len(task['files'])} files")

# Check another agent's data
other_data = agent.retrieve("analysis_results", agent_id="security_agent")
```

**Checkpoint**: Run this code. You should see your stashed data retrieved successfully.

---

## Part 2: Multi-Agent Coordination (20 minutes)

### Step 4: Set Up a Team

```python
from empathy_os import AgentCoordinator, AgentTask

# Create coordinator (automatically gets Steward access)
coordinator = AgentCoordinator(memory, team_id="review_team")

# Register specialized agents
coordinator.register_agent("security_agent", capabilities=["security_review"])
coordinator.register_agent("performance_agent", capabilities=["performance_review"])
coordinator.register_agent("style_agent", capabilities=["style_review"])

print(f"Active agents: {coordinator.get_active_agents()}")
```

### Step 5: Distribute Tasks

```python
# Add tasks to the queue
tasks = [
    AgentTask(
        task_id="sec_001",
        task_type="security_review",
        description="Review authentication module for vulnerabilities",
        priority=9  # High priority
    ),
    AgentTask(
        task_id="perf_001",
        task_type="performance_review",
        description="Profile database query performance",
        priority=7
    ),
    AgentTask(
        task_id="style_001",
        task_type="style_review",
        description="Check code style compliance",
        priority=5  # Lower priority
    ),
]

for task in tasks:
    coordinator.add_task(task)
    print(f"Added task: {task.task_id} (priority {task.priority})")
```

### Step 6: Agents Claim and Complete Tasks

```python
# Security agent claims its task
claimed = coordinator.claim_task("security_agent", "security_review")
if claimed:
    print(f"Security agent claimed: {claimed.task_id}")

    # Do the work...
    findings = {
        "vulnerabilities": 0,
        "warnings": 2,
        "files_reviewed": 5,
        "time_taken_ms": 1234
    }

    # Mark complete with results
    coordinator.complete_task(claimed.task_id, findings)
    print(f"Task completed with {findings['warnings']} warnings")
```

### Step 7: Aggregate Results

```python
# After all agents complete...
results = coordinator.aggregate_results()

print(f"Total completed: {results['total_completed']}")
print(f"By agent: {results['by_agent']}")
print(f"By type: {results['by_type']}")
```

**Checkpoint**: You should see tasks distributed and completed, with aggregated results.

---

## Part 3: Real-Time Signals (15 minutes)

### Step 8: Broadcast and Receive

```python
# Agent sends completion signal
agent.send_signal(
    signal_type="analysis_complete",
    data={
        "agent": "security_agent",
        "findings": {"critical": 0, "warnings": 2},
        "confidence": 0.92
    },
    target_agent="lead_reviewer"  # Or None for broadcast
)

# Lead receives signals
lead = EmpathyOS(
    user_id="lead_reviewer",
    short_term_memory=memory,
    access_tier=AccessTier.VALIDATOR
)

signals = lead.receive_signals("analysis_complete")
for sig in signals:
    print(f"From {sig.get('sender')}: {sig.get('data')}")
```

### Step 9: Team Session for Collaboration

```python
from empathy_os import TeamSession

# Create collaborative session
session = TeamSession(
    memory,
    session_id="pr_review_42",
    purpose="Review PR #42: Authentication Refactor"
)

# Add participants
session.add_agent("security_agent")
session.add_agent("performance_agent")
session.add_agent("lead_reviewer")

# Share context (visible to all participants)
session.share("pr_context", {
    "pr_number": 42,
    "author": "developer_123",
    "files_changed": ["auth.py", "api.py", "tests/test_auth.py"],
    "lines_added": 450,
    "lines_removed": 120
})

# Any agent can read shared context
context = session.get("pr_context")
print(f"Reviewing PR #{context['pr_number']} by {context['author']}")

# Session info
info = session.get_info()
print(f"Participants: {info.get('participants', [])}")
```

**Checkpoint**: Create a session, share context, and verify all agents can access it.

---

## Part 4: Pattern Staging and Validation (20 minutes)

### Step 10: Discover and Stage a Pattern

```python
from empathy_os import StagedPattern

# Contributor discovers a useful pattern during work
pattern = StagedPattern(
    pattern_id="pat_eager_load_001",
    agent_id="performance_agent",
    pattern_type="optimization",
    name="Eager Loading for N+1 Queries",
    description="Replace lazy loading with eager loading when iterating over related objects",
    confidence=0.88,
    code="""
# Before (N+1 problem):
for user in users:
    print(user.profile.name)  # Queries DB for each user

# After (eager loading):
users = User.objects.select_related('profile').all()
for user in users:
    print(user.profile.name)  # No additional queries
""",
    context={
        "discovered_in": "pr_review_42",
        "files": ["api.py"],
        "performance_improvement": "10x fewer queries"
    }
)

# Stage the pattern (requires Contributor+ access)
contributor = EmpathyOS(
    user_id="performance_agent",
    short_term_memory=memory,
    access_tier=AccessTier.CONTRIBUTOR
)
contributor.stage_pattern(pattern)
print(f"Pattern staged: {pattern.name}")
```

### Step 11: Validator Reviews and Promotes

```python
# Validator reviews staged patterns
validator = EmpathyOS(
    user_id="senior_architect",
    short_term_memory=memory,
    access_tier=AccessTier.VALIDATOR  # Can promote patterns
)

staged = validator.get_staged_patterns()
print(f"Patterns awaiting validation: {len(staged)}")

for p in staged:
    print(f"\n--- {p.name} ---")
    print(f"Type: {p.pattern_type}")
    print(f"Confidence: {p.confidence:.0%}")
    print(f"Discovered by: {p.agent_id}")
    print(f"Code example:\n{p.code}")

    # Validator decision (in real system, would involve review)
    if p.confidence > 0.85:
        print(f"APPROVED: Promoting to pattern library")
        # promote_to_library(p)  # Your promotion logic
    else:
        print(f"NEEDS WORK: Confidence below threshold")
```

**Checkpoint**: Stage a pattern and verify it appears in the staging queue.

---

## Part 5: State Persistence (10 minutes)

### Step 12: Persist and Restore State

```python
# Agent accumulates state during work
agent = EmpathyOS(
    user_id="long_running_agent",
    short_term_memory=memory,
    access_tier=AccessTier.CONTRIBUTOR
)

# Update collaboration state through interactions
agent.collaboration_state.trust_level = 0.85
agent.collaboration_state.successful_interventions = 15
agent.collaboration_state.failed_interventions = 2
agent.current_empathy_level = 4

# Persist to Redis (survives process restart)
agent.persist_collaboration_state()
print(f"State persisted for session: {agent.session_id}")

# Later, or in a new process...
new_agent = EmpathyOS(
    user_id="long_running_agent",
    short_term_memory=memory,
    access_tier=AccessTier.CONTRIBUTOR
)

# Restore state from previous session
restored = new_agent.restore_collaboration_state(session_id=agent.session_id)
if restored:
    print(f"Trust level restored: {new_agent.collaboration_state.trust_level}")
    print(f"Empathy level: {new_agent.current_empathy_level}")
```

---

## Part 6: Measuring Success

### Key Metrics to Track

```python
def measure_coordination_performance(memory, coordinator, num_tasks=10):
    """Benchmark coordination latency and throughput."""
    import time

    # 1. Task distribution latency
    start = time.time()
    for i in range(num_tasks):
        coordinator.add_task(AgentTask(
            task_id=f"bench_{i}",
            task_type="benchmark",
            description="Benchmark task",
            priority=5
        ))
    distribution_time = (time.time() - start) * 1000

    # 2. Signal round-trip time
    start = time.time()
    coordinator.broadcast("ping", {"timestamp": time.time()})
    signals = memory.receive_signals(coordinator._credentials, signal_type="ping")
    signal_rtt = (time.time() - start) * 1000

    # 3. Memory stats
    stats = memory.get_stats()

    return {
        "distribution_latency_ms": distribution_time / num_tasks,
        "signal_rtt_ms": signal_rtt,
        "redis_mode": stats["mode"],
        "total_keys": stats["keys"],
        "memory_used": stats.get("memory_used", "N/A")
    }

# Run benchmark
metrics = measure_coordination_performance(memory, coordinator)
print(f"Task distribution: {metrics['distribution_latency_ms']:.1f}ms per task")
print(f"Signal round-trip: {metrics['signal_rtt_ms']:.1f}ms")
print(f"Mode: {metrics['redis_mode']}, Keys: {metrics['total_keys']}")
```

### Expected Results

| Metric | Mock Mode | Local Redis | Cloud Redis |
|--------|-----------|-------------|-------------|
| Distribution latency | < 1ms | < 5ms | < 20ms |
| Signal round-trip | < 1ms | < 10ms | < 50ms |
| Pattern staging | < 2ms | < 10ms | < 30ms |

---

## Complete Working Example

```python
"""
Complete multi-agent code review with short-term memory.
Run this file to see all concepts in action.
"""
import asyncio
from empathy_os import (
    EmpathyOS, get_redis_memory, AccessTier,
    AgentCoordinator, AgentTask, TeamSession, StagedPattern
)

async def run_code_review():
    # Setup
    memory = get_redis_memory()
    print(f"Memory mode: {memory.get_stats()['mode']}")

    # Create team
    coordinator = AgentCoordinator(memory, team_id="code_review")
    coordinator.register_agent("security", ["security_review"])
    coordinator.register_agent("performance", ["performance_review"])

    # Create session
    session = TeamSession(memory, session_id="pr_100", purpose="Review PR #100")
    session.add_agent("security")
    session.add_agent("performance")
    session.add_agent("lead")

    # Share context
    session.share("scope", {
        "files": ["api.py", "auth.py"],
        "lines_changed": 200
    })

    # Add tasks
    coordinator.add_task(AgentTask(
        task_id="sec_review",
        task_type="security_review",
        description="Check for vulnerabilities",
        priority=9
    ))

    # Create agents
    security_agent = EmpathyOS(
        "security",
        short_term_memory=memory,
        access_tier=AccessTier.CONTRIBUTOR
    )
    lead_agent = EmpathyOS(
        "lead",
        short_term_memory=memory,
        access_tier=AccessTier.VALIDATOR
    )

    # Security agent works
    security_agent.stash("findings", {
        "vulnerabilities": 0,
        "warnings": 1,
        "passed": True
    })
    security_agent.send_signal(
        "review_complete",
        {"agent": "security", "passed": True}
    )

    # Stage discovered pattern
    security_agent.stage_pattern(StagedPattern(
        pattern_id="pat_input_validation",
        agent_id="security",
        pattern_type="security",
        name="API Boundary Validation",
        description="Always validate input at API boundaries",
        confidence=0.90
    ))

    # Lead aggregates
    signals = lead_agent.receive_signals("review_complete")
    staged = lead_agent.get_staged_patterns()

    print(f"\nReview Complete!")
    print(f"Signals received: {len(signals)}")
    print(f"Patterns staged: {len(staged)}")
    print(f"Final keys in Redis: {memory.get_stats()['keys']}")

    # Persist state
    lead_agent.collaboration_state.successful_interventions += 1
    lead_agent.persist_collaboration_state()
    print(f"State persisted")

if __name__ == "__main__":
    asyncio.run(run_code_review())
```

---

## Troubleshooting

### Redis Connection Issues

```python
# Force mock mode for testing
from empathy_os.redis_memory import RedisShortTermMemory
memory = RedisShortTermMemory(use_mock=True)
```

### Permission Errors

```python
# Check agent's access tier
print(f"Tier: {agent.credentials.tier}")
print(f"Can write: {agent.credentials.can_stage()}")
print(f"Can validate: {agent.credentials.can_validate()}")
```

### State Not Persisting

```python
# Verify session ID matches
print(f"Original session: {agent.session_id}")
# Use same session_id when restoring
new_agent.restore_collaboration_state(session_id=agent.session_id)
```

---

## Next Steps

- **[Practical Patterns](./practical-patterns.md)**: Ready-to-use patterns for common scenarios
- **[API Reference](../api-reference/multi-agent.md)**: Complete class documentation
- **[Examples](../examples/multi-agent-team-coordination.md)**: Full working examples

---

*This chapter provides a hands-on implementation guide. For the philosophical foundations behind these design decisions, see [The Philosophy of Multi-Agent Coordination](./multi-agent-philosophy.md).*
