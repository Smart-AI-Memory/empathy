# Glossary

*Key terms and definitions for the Empathy Framework*

---

## A

### Access Tier
A permission level that determines what an agent can do within the system. There are four tiers:
- **Observer** (Level 1): Read-only access
- **Contributor** (Level 2): Can read and write patterns
- **Validator** (Level 3): Can promote patterns to permanent storage
- **Steward** (Level 4): Full administrative access

See: [Multi-Agent Philosophy](./multi-agent-philosophy.md#the-access-tier-system)

### Agent
An AI instance that participates in the Empathy system. Agents can be specialized (security reviewer, performance analyst) or general-purpose. Multiple agents can coordinate through shared memory.

### Anticipatory Empathy
The ability to predict and address needs before they're expressed. Level 4 in the Empathy Framework's five-level model. Anticipatory systems don't just respond to problems—they prevent them.

---

## B

### BATNA
**B**est **A**lternative **T**o **N**egotiated **A**greement. When two agents cannot find a synthesis that serves both interests, the system falls back to the BATNA—typically the recommendation with higher confidence. Borrowed from negotiation theory (Harvard Negotiation Project's "Getting to Yes").

---

## C

### Classification
A security label applied to patterns that determines storage, encryption, and retention policies:
- **PUBLIC**: General patterns, no encryption, 365-day retention
- **INTERNAL**: Proprietary patterns, optional encryption, 180-day retention
- **SENSITIVE**: Healthcare/PII patterns, required encryption (AES-256), 90-day retention

### Confidence
A numeric score (0.0 to 1.0) indicating how certain an agent is about a recommendation or pattern. Higher confidence typically means more evidence or successful past application.

### Conflict Resolution
The process of finding a synthesis when two agents make conflicting recommendations. The framework extracts the underlying *interests* behind each position and generates options that serve both.

See: [Practical Patterns - Conflict Synthesizer](./practical-patterns.md#pattern-2-the-conflict-synthesizer)

### Contributor
Access Tier Level 2. Can read patterns and propose new ones, but cannot validate or promote patterns to permanent storage. Most AI agents operate at this level.

---

## D

### Data Sovereignty
The principle that users and enterprises own, version, and control all memories associated with their projects. A foundational value of the Empathy Framework—not a feature, but a constraint that shapes all design decisions.

---

## E

### Emergence
Patterns that weren't explicitly taught but arise from collective agent operation. The framework treats emergent patterns as valuable and surfaces them for validation rather than filtering them out.

### EmpathyOS
The main interface class for interacting with the Empathy Framework. Provides methods for memory operations, pattern management, and agent coordination.

```python
from empathy_os import EmpathyOS
empathy = EmpathyOS(user_id="developer@company.com")
```

---

## F

### Fingerprint
A hash-based identifier used to detect duplicate patterns. Prevents the same pattern from being stored multiple times while allowing confidence boosting when the same pattern is discovered independently.

---

## H

### Heartbeat
A periodic signal sent by agents to indicate they're still functioning. Used by the monitoring system to detect unresponsive agents and reassign their work.

See: [Practical Patterns - Heartbeat Monitor](./practical-patterns.md#pattern-4-the-heartbeat-monitor)

---

## I

### Interests
The underlying needs or goals that motivate a recommendation, as opposed to the *position* (what is recommended). Conflict resolution works by identifying interests and finding solutions that serve multiple interests simultaneously.

Example:
- **Position**: "Add input validation on all endpoints"
- **Interest**: Prevent injection attacks, protect data integrity

---

## L

### Level (Empathy Level)
The Empathy Framework defines five levels of AI capability:
- **Level 1 - Reactive**: Responds to explicit requests
- **Level 2 - Informed**: Remembers context within a session
- **Level 3 - Contextual**: Applies patterns from similar situations
- **Level 4 - Anticipatory**: Predicts and prevents problems
- **Level 5 - Generative**: Creates novel solutions from patterns

Level 4 (Anticipatory) is the minimum standard for Empathy systems.

### Long-Term Memory
Persistent storage for validated patterns that survive across sessions. Patterns in long-term memory have been reviewed and promoted from staging. Contrast with *Short-Term Memory*.

---

## M

### Mock Mode
A development mode where Redis is simulated in-memory. Useful for quick experiments but doesn't support multi-agent coordination or persistence.

```python
os.environ["EMPATHY_REDIS_MOCK"] = "true"
```

---

## O

### Observer
Access Tier Level 1. Read-only access to patterns and shared state. New agents typically start at Observer level until they demonstrate reliability.

---

## P

### Pattern
A reusable piece of knowledge—a best practice, code snippet, workflow, or insight—that can be applied across contexts. Patterns are the core unit of knowledge in the Empathy Framework.

### Pattern Library
A collection of validated patterns available to all agents. Patterns enter the library through the staging and promotion workflow.

### Pattern Staging
A 24-hour holding area where discovered patterns await validation before becoming permanent. Think of it as a pull request for knowledge—it needs review before merging. Patterns that aren't promoted within 24 hours expire automatically.

### PII Scrubbing
Automatic detection and redaction of Personally Identifiable Information (emails, SSNs, phone numbers, etc.) before pattern storage. A security control that prevents sensitive data from entering the pattern library.

### Position
What an agent recommends, as opposed to the underlying *interest* (why). Conflict resolution focuses on interests rather than positions to find mutually beneficial solutions.

### Promote
To move a pattern from staging (short-term) to the permanent pattern library (long-term). Only Validators and Stewards can promote patterns.

---

## R

### Redis
An in-memory data store used for short-term memory and agent coordination. Redis provides the speed needed for real-time coordination while supporting TTL-based expiration.

---

## S

### SBAR
**S**ituation, **B**ackground, **A**ssessment, **R**ecommendation. A structured communication format borrowed from healthcare that ensures clear handoffs between agents. Used in agent-to-agent communication.

### Short-Term Memory
Redis-backed working memory for active coordination. Data in short-term memory expires automatically (TTL-based). Used for task state, signals between agents, and pattern staging. Contrast with *Long-Term Memory*.

### Signal
A message sent from one agent to another through short-term memory. Used to coordinate work, announce completion, or share findings.

```python
empathy.send_signal("analysis_complete", {"files": 10, "issues": 3})
```

### Staged Pattern
A pattern in the 24-hour staging area awaiting validation. Staged patterns have a TTL and will expire if not promoted.

### Stash
To store data in short-term memory with automatic expiration.

```python
empathy.stash("current_task", {"status": "analyzing"})
```

### Steward
Access Tier Level 4. Full administrative access including the ability to modify access tiers, delete patterns, and configure system behavior. Typically reserved for system administrators or senior architects.

### Synthesis
A solution that serves the interests of multiple conflicting recommendations. When agents disagree, the conflict resolution system attempts to generate a synthesis before falling back to BATNA.

---

## T

### Team Session
A collaborative context where multiple agents work together on a shared task. Sessions provide shared state, signals, and coordination primitives.

```python
session = TeamSession(memory, session_id="pr_42", purpose="Review PR #42")
session.add_agent("security_agent")
session.add_agent("performance_agent")
```

### Trust Escalator
A system for managing agent permissions based on demonstrated reliability. Agents start at Observer level and are promoted as they accumulate successful tasks and validated patterns.

See: [Practical Patterns - Trust Escalator](./practical-patterns.md#pattern-5-the-trust-escalator)

### TTL
**T**ime **T**o **L**ive. The duration before data in short-term memory expires automatically. Different data types have different TTLs:
- Working memory: 1 hour
- Staged patterns: 24 hours
- Coordination signals: 5 minutes

---

## U

### Unified Memory
The single API that provides access to both short-term (Redis) and long-term (persistent) memory tiers. Introduced in v1.10.0 to simplify the developer experience.

```python
empathy.stash(...)           # Short-term
empathy.persist_pattern(...) # Long-term
```

---

## V

### Validator
Access Tier Level 3. Can review staged patterns and promote them to the permanent library. Validators act as quality gates, ensuring only reliable patterns become permanent knowledge.

---

## W

### Wizard
A specialized component that encapsulates domain expertise and workflows. Examples include SecurityWizard, PerformanceWizard, and ClinicalProtocolMonitor. Wizards operate at Level 4 (Anticipatory) or higher.

### Working Memory
Short-term storage for intermediate results during task execution. Expires after 1 hour by default.

---

## Concepts Quick Reference

| Term | One-Line Definition |
|------|---------------------|
| Access Tier | Permission level (Observer → Contributor → Validator → Steward) |
| Anticipatory | Predicting and preventing problems, not just reacting |
| BATNA | Fallback when synthesis isn't possible |
| Classification | Security label (PUBLIC, INTERNAL, SENSITIVE) |
| Confidence | How certain (0.0 to 1.0) |
| Data Sovereignty | You own your data, always |
| Long-Term Memory | Persistent patterns across sessions |
| Pattern | Reusable knowledge unit |
| Promote | Move from staging to permanent |
| Short-Term Memory | Redis-backed, expires automatically |
| Signal | Message between agents |
| Staging | 24-hour holding area for validation |
| TTL | Time before automatic expiration |
| Wizard | Domain-specific anticipatory component |

---

*This glossary covers terms as of Empathy Framework v1.10.0*
