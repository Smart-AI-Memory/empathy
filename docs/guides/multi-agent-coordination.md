# Multi-Agent Coordination

Enable multiple AI agents to work together on complex tasks through shared pattern libraries and coordinated workflows.

---

## Overview

**Multi-agent systems** allow specialized AI agents to collaborate:

- **Code Review Agent** - Reviews PRs for bugs and style
- **Test Generation Agent** - Creates unit and integration tests
- **Documentation Agent** - Maintains up-to-date docs
- **Security Agent** - Scans for vulnerabilities
- **Performance Agent** - Optimizes slow code

**Result**: **80% faster feature delivery** through parallel work and shared learnings.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                    Shared Pattern Library                     │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ • Code patterns discovered by any agent                │  │
│  │ • Best practices learned from team                     │  │
│  │ • Security vulnerabilities and fixes                   │  │
│  │ • Performance optimizations                            │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────────────────┬────────────────────────────────────────┘
                       │ (Shared Knowledge)
        ┌──────────────┼──────────────┬────────────┐
        │              │               │            │
        ▼              ▼               ▼            ▼
┌──────────────┐ ┌──────────┐ ┌──────────────┐ ┌────────────┐
│ Code Review  │ │   Test   │ │ Documentation │ │  Security  │
│    Agent     │ │Generation│ │     Agent     │ │   Agent    │
└──────┬───────┘ └────┬─────┘ └──────┬───────┘ └─────┬──────┘
       │              │                │              │
       │ (Results)    │                │              │
       └──────────────┴────────────────┴──────────────┘
                       │
                       ▼
            ┌──────────────────────┐
            │  Coordinated Output  │
            └──────────────────────┘
```

---

## Quick Start

### Create Agent Team

```python
from empathy_os import EmpathyOS
from empathy_os.pattern_library import PatternLibrary

# Shared pattern library for all agents
shared_library = PatternLibrary(name="team_library")

# Create specialized agents
code_reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,
    shared_library=shared_library  # Share learnings
)

test_generator = EmpathyOS(
    user_id="test_generator",
    target_level=3,
    shared_library=shared_library
)

doc_writer = EmpathyOS(
    user_id="doc_writer",
    target_level=3,
    shared_library=shared_library
)
```

### Run Coordinated Workflow

```python
async def process_pull_request(pr_number):
    # 1. Code review (parallel)
    review_task = code_reviewer.interact(
        user_id="developer_123",
        user_input=f"Review PR #{pr_number}",
        context={"pr": pr_number}
    )

    # 2. Generate tests (parallel)
    test_task = test_generator.interact(
        user_id="developer_123",
        user_input=f"Generate tests for PR #{pr_number}",
        context={"pr": pr_number}
    )

    # 3. Update docs (parallel)
    doc_task = doc_writer.interact(
        user_id="developer_123",
        user_input=f"Update docs for PR #{pr_number}",
        context={"pr": pr_number}
    )

    # Wait for all agents to complete
    review, tests, docs = await asyncio.gather(
        review_task,
        test_task,
        doc_task
    )

    return {
        "review": review,
        "tests": tests,
        "documentation": docs
    }
```

---

## Pattern Sharing

### How It Works

1. **Agent A** discovers a useful pattern
2. Pattern added to **shared library** with confidence score
3. **Agent B** encounters similar context
4. Pattern suggested if confidence > threshold
5. Success/failure feedback updates pattern confidence

### Example: Code Pattern

```python
from empathy_os.pattern_library import Pattern

# Code Review Agent discovers pattern
pattern = Pattern(
    id="avoid_mutable_defaults",
    agent_id="code_reviewer",
    pattern_type="warning",
    context={
        "language": "python",
        "issue": "mutable_default_argument"
    },
    code="""
# Bad (mutable default)
def append_to_list(item, my_list=[]):
    my_list.append(item)
    return my_list

# Good (immutable default)
def append_to_list(item, my_list=None):
    if my_list is None:
        my_list = []
    my_list.append(item)
    return my_list
""",
    confidence=0.95,
    times_applied=23,
    success_rate=0.96
)

# Add to shared library
shared_library.add_pattern(pattern)

# Later, Test Generator Agent finds similar code
matches = shared_library.find_matching_patterns(
    context={"language": "python", "function_has_default": True}
)

if matches:
    print(f"⚠️  Pattern from Code Review Agent:")
    print(f"   {matches[0].code}")
```

---

## Agent Specialization

### Code Review Agent

```python
code_reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,
    specialization={
        "focus": "code_quality",
        "checks": [
            "bug_detection",
            "style_consistency",
            "best_practices",
            "performance_issues"
        ],
        "severity_threshold": "medium"
    },
    shared_library=shared_library
)

# Use for PR reviews
review = await code_reviewer.interact(
    user_id="developer_123",
    user_input="Review changes in auth.py",
    context={"files": ["auth.py"], "pr": 123}
)

print(review['suggestions'])
# Output:
# [
#   {
#     "type": "security",
#     "severity": "high",
#     "line": 45,
#     "issue": "Plaintext password in logs",
#     "fix": "Use logger.debug('[REDACTED]') for sensitive data"
#   },
#   {
#     "type": "performance",
#     "severity": "medium",
#     "line": 78,
#     "issue": "N+1 database queries",
#     "fix": "Use select_related() to prefetch related objects"
#   }
# ]
```

### Test Generation Agent

```python
test_generator = EmpathyOS(
    user_id="test_generator",
    target_level=3,
    specialization={
        "focus": "test_coverage",
        "types": ["unit", "integration"],
        "frameworks": ["pytest", "unittest"],
        "coverage_target": 0.8
    },
    shared_library=shared_library
)

# Generate tests for new code
tests = await test_generator.interact(
    user_id="developer_123",
    user_input="Generate tests for calculate_discount()",
    context={"function": "calculate_discount", "file": "pricing.py"}
)

print(tests['generated_tests'])
# Output: Complete pytest tests with fixtures, edge cases, mocks
```

### Security Agent

```python
security_agent = EmpathyOS(
    user_id="security_agent",
    target_level=4,  # Anticipatory - predict vulnerabilities
    specialization={
        "focus": "security",
        "checks": ["sql_injection", "xss", "csrf", "secrets_in_code"],
        "compliance": ["owasp_top_10", "cwe_top_25"]
    },
    shared_library=shared_library
)

# Scan for vulnerabilities
scan = await security_agent.interact(
    user_id="developer_123",
    user_input="Scan for security issues",
    context={"branch": "feature/user-auth"}
)

if scan['vulnerabilities']:
    for vuln in scan['vulnerabilities']:
        print(f"🔒 {vuln['type']}: {vuln['description']}")
        print(f"   Fix: {vuln['remediation']}")
```

---

## Coordination Patterns

### Sequential Workflow

Agents work in sequence, each building on previous results:

```python
async def sequential_workflow(code_changes):
    # 1. Security scan first
    security_result = await security_agent.interact(
        user_id="dev",
        user_input="Scan for vulnerabilities",
        context={"changes": code_changes}
    )

    if security_result['vulnerabilities']:
        return {"status": "blocked", "reason": "security_issues"}

    # 2. Generate tests (if security passes)
    tests = await test_generator.interact(
        user_id="dev",
        user_input="Generate tests",
        context={"changes": code_changes}
    )

    # 3. Review code (if tests generated)
    review = await code_reviewer.interact(
        user_id="dev",
        user_input="Review code and tests",
        context={"changes": code_changes, "tests": tests}
    )

    return {
        "status": "complete",
        "security": security_result,
        "tests": tests,
        "review": review
    }
```

### Parallel Workflow

Agents work simultaneously for speed:

```python
async def parallel_workflow(code_changes):
    # All agents work in parallel
    results = await asyncio.gather(
        security_agent.interact(user_id="dev", user_input="Scan", context={"changes": code_changes}),
        test_generator.interact(user_id="dev", user_input="Generate tests", context={"changes": code_changes}),
        code_reviewer.interact(user_id="dev", user_input="Review", context={"changes": code_changes}),
        doc_writer.interact(user_id="dev", user_input="Update docs", context={"changes": code_changes})
    )

    security, tests, review, docs = results

    return {
        "security": security,
        "tests": tests,
        "review": review,
        "documentation": docs
    }
```

### Hierarchical Workflow

Coordinator agent manages sub-agents:

```python
async def hierarchical_workflow(task):
    # Coordinator decides which agents to use
    coordinator = EmpathyOS(
        user_id="coordinator",
        target_level=4
    )

    # Analyze task
    plan = await coordinator.interact(
        user_id="dev",
        user_input=f"Plan: {task}",
        context={"available_agents": ["security", "test", "review", "docs"]}
    )

    # Execute sub-agents based on plan
    results = {}
    for agent_name in plan['agents_needed']:
        agent = get_agent(agent_name)
        results[agent_name] = await agent.interact(
            user_id="dev",
            user_input=plan[f'{agent_name}_task'],
            context=plan['context']
        )

    # Coordinator synthesizes results
    final = await coordinator.interact(
        user_id="dev",
        user_input="Synthesize results",
        context={"results": results}
    )

    return final
```

---

## Performance Benefits

### Before Multi-Agent (Single Developer)

| Task | Time | Total |
|------|------|-------|
| Write code | 4 hours | 4h |
| Write tests | 2 hours | 6h |
| Code review | 1 hour | 7h |
| Update docs | 1 hour | 8h |
| **TOTAL** | | **8 hours** |

### After Multi-Agent (Parallel Execution)

| Task | Agent | Time | Parallel |
|------|-------|------|----------|
| Write code | Developer | 4 hours | ─────┐ |
| Generate tests | Test Agent | 15 min | ─────┤ |
| Code review | Review Agent | 10 min | ─────┼─ **4 hours** |
| Update docs | Doc Agent | 10 min | ─────┤ |
| Security scan | Security Agent | 5 min | ─────┘ |
| **TOTAL** | | | **4 hours** (-50%) |

**Additional benefits**:
- ✅ Consistent code quality (agents never tired)
- ✅ No forgotten documentation
- ✅ Immediate security feedback
- ✅ 100% test coverage

---

## Conflict Resolution

### Pattern Conflicts

When agents disagree:

```python
# Code Review Agent suggests one approach
review_pattern = Pattern(
    id="use_list_comprehension",
    recommendation="Use list comprehension for better performance",
    confidence=0.85
)

# Style Agent prefers readability
style_pattern = Pattern(
    id="use_explicit_loop",
    recommendation="Use explicit loop for better readability",
    confidence=0.80
)

# Conflict resolver
resolver = ConflictResolver()
resolution = resolver.resolve_patterns(
    patterns=[review_pattern, style_pattern],
    context={"team_priority": "readability", "code_complexity": "high"}
)

# Result: Choose style_pattern (higher team priority match)
```

---

## Monitoring

### Agent Performance

```python
from empathy_os.monitoring import AgentMonitor

monitor = AgentMonitor()

# Track agent metrics
stats = monitor.get_agent_stats("code_reviewer")

print(f"Interactions: {stats['total_interactions']}")
print(f"Avg response time: {stats['avg_response_time_ms']}ms")
print(f"Patterns discovered: {stats['patterns_discovered']}")
print(f"Success rate: {stats['success_rate']:.0%}")
```

### Team Metrics

```python
team_stats = monitor.get_team_stats()

print(f"Active agents: {team_stats['active_agents']}")
print(f"Shared patterns: {team_stats['shared_patterns']}")
print(f"Pattern reuse rate: {team_stats['pattern_reuse_rate']:.0%}")
print(f"Collaboration efficiency: {team_stats['collaboration_efficiency']:.0%}")
```

---

## Best Practices

### ✅ Do

1. **Specialize agents** - Each agent focuses on one area
2. **Share patterns** - Use shared pattern library
3. **Run in parallel** when possible - Maximize speed
4. **Monitor performance** - Track agent effectiveness
5. **Resolve conflicts** - Handle pattern disagreements

### ❌ Don't

1. **Don't duplicate work** - Check pattern library first
2. **Don't ignore low-confidence patterns** - Provide feedback
3. **Don't create too many agents** - Start with 3-5
4. **Don't skip coordination** - Agents need orchestration

---

## Examples

See the complete [Multi-Agent Team Coordination Example](../examples/multi-agent-team-coordination.md) for a full implementation with:

- PR review automation
- Automated test generation
- Documentation updates
- Security scanning
- Performance optimization

---

## See Also

- [Adaptive Learning](adaptive-learning.md) - How agents learn
- [Pattern Library API](../api-reference/pattern-library.md) - Pattern management
- [Multi-Agent Example](../examples/multi-agent-team-coordination.md) - Full implementation
- [EmpathyOS API](../api-reference/empathy-os.md) - Agent configuration
