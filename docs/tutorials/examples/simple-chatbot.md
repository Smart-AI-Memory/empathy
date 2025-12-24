# Example: Code Review Assistant with Memory

**Difficulty**: Beginner → Intermediate
**Time**: 15 minutes
**Core Features**: Short-Term Memory (Redis), Long-Term Memory (Persistent), Multi-Agent Coordination

---

## Overview

Build a **Code Review Assistant** that demonstrates the two types of memory that make Empathy Framework powerful:

| Memory Type | Storage | Purpose | Example |
|-------------|---------|---------|---------|
| **Short-Term** | Redis | Active session context | "Which files have I reviewed in this PR?" |
| **Long-Term** | SQLite | Persistent patterns | "What issues has this codebase had historically?" |

**What you'll learn**:
- 🔴 **Short-Term Memory**: Track state within a session, coordinate agents in real-time
- 🔵 **Long-Term Memory**: Remember patterns across sessions, learn from history
- 🟢 **Combined Power**: Anticipate issues by connecting session context with historical patterns

---

## Why Two Types of Memory?

```
┌─────────────────────────────────────────────────────────────┐
│                    CODE REVIEW SESSION                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  SHORT-TERM MEMORY (Redis)          LONG-TERM MEMORY        │
│  ─────────────────────────          ────────────────        │
│  • Files reviewed this session      • Historical bugs       │
│  • Issues found so far              • Developer patterns    │
│  • Agent coordination state         • Codebase weak spots   │
│  • Current PR context               • Review outcomes       │
│                                                             │
│  Expires: End of session            Persists: Forever       │
│  Speed: <1ms                        Speed: ~10ms            │
│                                                             │
│          ↓                                   ↓              │
│          └─────────────┬─────────────────────┘              │
│                        ▼                                    │
│              🔮 ANTICIPATORY INSIGHT                        │
│         "This auth change looks similar to the              │
│          bug we found in PR #98. Check line 42."            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Install with Redis support (default)
pip install empathy-framework[full]

# Start Redis (required for short-term memory)
docker run -d -p 6379:6379 redis:alpine
```

---

## Part 1: Short-Term Memory (Redis)

Short-term memory tracks state **within a session**. It's fast, shared between agents, and expires when done.

```python
from empathy_os import EmpathyOS
from empathy_os.memory import ShortTermMemory

# Connect to Redis for short-term memory
short_term = ShortTermMemory(redis_url="redis://localhost:6379")

# Create code review assistant
reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=3,
    short_term_memory=short_term
)

# Start reviewing a PR
session_id = "pr-142-review"

# Review first file
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Review src/auth/login.py for security issues",
    context={"session_id": session_id, "file": "src/auth/login.py"}
)

print("=== First File Review ===")
print(response.response)

# Short-term memory now contains:
# - Files reviewed: ["src/auth/login.py"]
# - Issues found: [...]
# - Time spent: 45 seconds

# Review second file - assistant remembers context
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Now review src/auth/tokens.py",
    context={"session_id": session_id, "file": "src/auth/tokens.py"}
)

print("\n=== Second File Review ===")
print(response.response)
# Response includes: "This file imports from login.py which we just reviewed.
#                    I noticed the token validation here doesn't match
#                    the authentication pattern in login.py..."

# Check what's in short-term memory
session_state = short_term.get_session(session_id)
print(f"\n=== Session State (Redis) ===")
print(f"Files reviewed: {session_state['files_reviewed']}")
print(f"Issues found: {len(session_state['issues'])}")
print(f"Session duration: {session_state['duration_seconds']}s")
```

**Key Point**: Short-term memory lets the reviewer remember what it just reviewed, connect related files, and track progress - all within a single session.

---

## Part 2: Long-Term Memory (Persistent)

Long-term memory stores patterns **across sessions**. It learns from history and persists forever.

```python
from empathy_os import EmpathyOS
from empathy_os.memory import LongTermMemory

# Connect to SQLite for long-term memory
long_term = LongTermMemory(db_path=".empathy/review_history.db")

# Create reviewer with long-term memory
reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,  # Anticipatory - uses historical patterns
    long_term_memory=long_term
)

# First review session (January)
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Review PR #98: Authentication refactor",
    context={"pr_number": 98, "files": ["src/auth/login.py"]}
)

# Record what happened
long_term.record_pattern(
    pattern_type="security_issue",
    description="SQL injection vulnerability in login query",
    file="src/auth/login.py",
    line=42,
    severity="high",
    pr_number=98
)

# ... weeks later ...

# New review session (February)
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Review PR #142: Add OAuth login",
    context={"pr_number": 142, "files": ["src/auth/oauth.py", "src/auth/login.py"]}
)

print("=== Review with Historical Context ===")
print(response.response)
# Output includes:
# "⚠️ HISTORICAL ALERT: src/auth/login.py had a SQL injection issue
#  in PR #98 (January). The changes in this PR touch similar code.
#  Recommend extra scrutiny on lines 40-50."

# Query long-term memory directly
history = long_term.get_patterns(
    file_pattern="src/auth/*",
    pattern_type="security_issue"
)

print(f"\n=== Auth Module History ===")
for pattern in history:
    print(f"  PR #{pattern.pr_number}: {pattern.description}")
    print(f"    File: {pattern.file}:{pattern.line}")
    print(f"    Severity: {pattern.severity}")
```

**Key Point**: Long-term memory lets the reviewer learn from past reviews, remember where bugs occurred, and warn about similar patterns in new code.

!!! note "Long-Term Memory Works Without Redis"
    **Redis is only required for short-term memory.** If you don't need session state tracking or multi-agent coordination, you can use long-term memory (SQLite) by itself:

    ```python
    from empathy_os import EmpathyOS
    from empathy_os.memory import LongTermMemory

    # Persistent memory without Redis - no Docker required!
    long_term = LongTermMemory(db_path=".empathy/history.db")

    reviewer = EmpathyOS(
        user_id="code_reviewer",
        target_level=4,
        long_term_memory=long_term  # Works standalone
    )
    ```

    This is ideal for:

    - **Single-user applications** - No need for shared session state
    - **Simpler deployments** - Just Python and SQLite, no Redis container
    - **Learning from history** - Historical patterns still work perfectly

---

## Part 3: Combining Both Memories

The real power comes from **combining** short-term and long-term memory:

```python
from empathy_os import EmpathyOS
from empathy_os.memory import UnifiedMemory

# Unified memory combines both
memory = UnifiedMemory(
    redis_url="redis://localhost:6379",      # Short-term
    sqlite_path=".empathy/review_history.db"  # Long-term
)

# Create Level 4 (anticipatory) reviewer
reviewer = EmpathyOS(
    user_id="code_reviewer",
    target_level=4,
    memory=memory
)

# Start a new review session
session_id = "pr-200-review"

# The assistant now has access to:
# - SHORT-TERM: What's happening in this session
# - LONG-TERM: What happened in all previous sessions

response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Review PR #200: Payment processing update",
    context={
        "session_id": session_id,
        "pr_number": 200,
        "files": ["src/payments/stripe.py", "src/payments/webhooks.py"]
    }
)

print("=== Combined Memory Review ===")
print(response.response)

# Output demonstrates both memories working together:
"""
📋 Starting review of PR #200: Payment processing update

🔵 LONG-TERM CONTEXT (from history):
   • src/payments/ has had 3 security issues in the last 6 months
   • Last webhook vulnerability was in PR #156 (race condition)
   • Developer @alice typically misses input validation

🔴 SHORT-TERM TRACKING (this session):
   • Files to review: 2
   • Estimated time: 15 minutes
   • Priority: HIGH (payment code)

🔮 ANTICIPATORY ALERTS:
   • webhooks.py: Check for race conditions (similar to PR #156)
   • stripe.py: Verify API key handling (pattern from PR #134)

Ready to begin. Which file first?
"""

# Review first file
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Start with stripe.py",
    context={"session_id": session_id, "file": "src/payments/stripe.py"}
)

# Short-term memory updates: "Currently reviewing stripe.py"
# Long-term memory consulted: "Previous issues in this file..."

# After finding an issue
response = reviewer.interact(
    user_id="code_reviewer",
    user_input="Found a potential issue on line 78 - API key exposed in error message",
    context={"session_id": session_id, "issue": True, "line": 78}
)

# Short-term: Records issue in current session
# Long-term: Saves pattern for future reviews

print("\n=== Issue Recorded ===")
print(response.response)
"""
✅ Issue recorded for this session.

🔵 Added to long-term memory:
   Pattern: "API key exposure in error handling"
   File: src/payments/stripe.py:78
   This is the 2nd time this pattern has appeared in payment code.

🔴 Session progress:
   • stripe.py: REVIEWED (1 issue found)
   • webhooks.py: PENDING

Continue to webhooks.py?
"""
```

---

## Part 4: Multi-Agent Code Review

Use multiple agents that **coordinate via short-term memory**:

```python
from empathy_os import EmpathyOS
from empathy_os.memory import UnifiedMemory
from empathy_os.coordination import TeamSession
import asyncio

async def multi_agent_review(pr_number: int, files: list[str]):
    """
    Multiple agents review code in parallel, coordinating through
    short-term memory (Redis) and learning from long-term memory.
    """

    memory = UnifiedMemory(
        redis_url="redis://localhost:6379",
        sqlite_path=".empathy/review_history.db"
    )

    async with TeamSession(
        session_id=f"pr-{pr_number}-team-review",
        memory=memory
    ) as session:

        # Create specialized review agents
        agents = {
            "security": EmpathyOS(
                user_id="security_reviewer",
                target_level=4,
                memory=memory
            ),
            "performance": EmpathyOS(
                user_id="perf_reviewer",
                target_level=3,
                memory=memory
            ),
            "style": EmpathyOS(
                user_id="style_reviewer",
                target_level=2,
                memory=memory
            )
        }

        # Each agent reviews in parallel
        # They coordinate via short-term memory (Redis):
        # - "security_reviewer is checking auth.py"
        # - "perf_reviewer found slow query on line 50"
        # - Agents can see each other's findings in real-time

        results = await session.parallel_review(
            agents=agents,
            files=files,
            context={"pr_number": pr_number}
        )

        print(f"=== Team Review Results for PR #{pr_number} ===\n")

        for agent_name, findings in results.items():
            print(f"🔍 {agent_name.upper()} REVIEW:")
            print(f"   Issues: {len(findings.issues)}")
            for issue in findings.issues:
                print(f"   • [{issue.severity}] {issue.file}:{issue.line}")
                print(f"     {issue.description}")
            print()

        # Consensus from all agents
        print("=== TEAM CONSENSUS ===")
        print(f"Total issues: {results.total_issues}")
        print(f"Blocking issues: {results.blocking_count}")
        print(f"Recommendation: {results.recommendation}")

        # All findings saved to long-term memory automatically
        print(f"\n✅ {results.total_issues} patterns saved to long-term memory")

# Run the review
asyncio.run(multi_agent_review(
    pr_number=200,
    files=["src/payments/stripe.py", "src/payments/webhooks.py"]
))
```

**What's happening with memory**:
- **Short-term (Redis)**: Agents share real-time state - who's reviewing what, issues found
- **Long-term (SQLite)**: Historical patterns inform each agent's review

---

## Part 5: Complete Working Example

Save as `code_review_assistant.py`:

```python
#!/usr/bin/env python3
"""
Code Review Assistant - Demonstrates Short-Term and Long-Term Memory

Usage:
    python code_review_assistant.py <pr_number> <file1> [file2] ...
    python code_review_assistant.py 142 src/auth/login.py src/auth/oauth.py
"""

import sys
import asyncio
from empathy_os import EmpathyOS
from empathy_os.memory import UnifiedMemory

async def main():
    if len(sys.argv) < 3:
        print("Usage: python code_review_assistant.py <pr_number> <file1> [file2] ...")
        sys.exit(1)

    pr_number = sys.argv[1]
    files = sys.argv[2:]

    print("🔍 Code Review Assistant")
    print("=" * 50)
    print(f"PR: #{pr_number}")
    print(f"Files: {', '.join(files)}")
    print()

    # Initialize unified memory
    memory = UnifiedMemory(
        redis_url="redis://localhost:6379",
        sqlite_path=".empathy/reviews.db"
    )

    # Create Level 4 reviewer
    reviewer = EmpathyOS(
        user_id="code_reviewer",
        target_level=4,
        memory=memory
    )

    session_id = f"pr-{pr_number}-review"

    # Show memory status
    print("📊 Memory Status:")
    print(f"   🔴 Short-term (Redis): {'Connected' if memory.redis_connected else 'Disconnected'}")
    print(f"   🔵 Long-term (SQLite): {memory.sqlite_path}")

    # Check for historical patterns
    history = memory.get_patterns_for_files(files)
    if history:
        print(f"\n⚠️  Historical Issues in These Files:")
        for pattern in history[:5]:
            print(f"   • {pattern.file}: {pattern.description}")
    print()

    # Interactive review loop
    print("Commands: 'review <file>', 'issue <description>', 'status', 'done'")
    print()

    while True:
        try:
            user_input = input("review> ").strip()

            if not user_input:
                continue

            if user_input.lower() == 'done':
                # Save session summary to long-term memory
                summary = memory.finalize_session(session_id)
                print(f"\n✅ Review complete!")
                print(f"   Issues found: {summary['issues_count']}")
                print(f"   Patterns saved: {summary['patterns_saved']}")
                print(f"   Session duration: {summary['duration']}")
                break

            if user_input.lower() == 'status':
                state = memory.get_session_state(session_id)
                print(f"\n📋 Session Status:")
                print(f"   Files reviewed: {state.get('files_reviewed', [])}")
                print(f"   Issues found: {state.get('issues_count', 0)}")
                print(f"   Time elapsed: {state.get('elapsed', '0s')}")
                continue

            # Get AI response
            response = reviewer.interact(
                user_id="code_reviewer",
                user_input=user_input,
                context={
                    "session_id": session_id,
                    "pr_number": pr_number,
                    "files": files
                }
            )

            print()
            print(response.response)

            # Show predictions if any
            if response.predictions:
                print("\n🔮 Predictions:")
                for pred in response.predictions:
                    conf = "🟢" if pred.confidence > 0.8 else "🟡"
                    print(f"   {conf} {pred.description}")

            print()

        except KeyboardInterrupt:
            print("\n👋 Review cancelled (not saved)")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Sample Session**:
```
🔍 Code Review Assistant
==================================================
PR: #142
Files: src/auth/login.py, src/auth/oauth.py

📊 Memory Status:
   🔴 Short-term (Redis): Connected
   🔵 Long-term (SQLite): .empathy/reviews.db

⚠️  Historical Issues in These Files:
   • src/auth/login.py: SQL injection in query builder (PR #98)
   • src/auth/login.py: Missing rate limiting (PR #112)

Commands: 'review <file>', 'issue <description>', 'status', 'done'

review> review src/auth/login.py

Reviewing src/auth/login.py...

🔵 FROM LONG-TERM MEMORY:
   This file has had 2 security issues in the past 6 months.
   Most recent: SQL injection (PR #98, fixed)

🔍 CURRENT REVIEW:
   Lines changed: 45-67
   Risk areas detected:
   • Line 52: Database query construction (⚠️ similar to PR #98 issue)
   • Line 61: Password handling

🔮 PREDICTIONS:
   🟢 High chance of input validation issue (based on PR #98 pattern)

review> issue Found unescaped user input on line 52

✅ Issue recorded:
   File: src/auth/login.py:52
   Type: Security (input validation)

🔴 SHORT-TERM: Added to session issues
🔵 LONG-TERM: Pattern "unescaped_input_auth" updated (3rd occurrence)

review> status

📋 Session Status:
   Files reviewed: ['src/auth/login.py']
   Issues found: 1
   Time elapsed: 3m 24s

review> done

✅ Review complete!
   Issues found: 1
   Patterns saved: 1
   Session duration: 4m 12s
```

---

## Memory Value Summary

| Feature | Short-Term (Redis) | Long-Term (SQLite) |
|---------|-------------------|-------------------|
| **What it stores** | Current session state | Historical patterns |
| **Lifetime** | Session duration | Forever |
| **Speed** | <1ms | ~10ms |
| **Use case** | "What have I reviewed so far?" | "What bugs has this code had?" |
| **Multi-agent** | Coordinate in real-time | Share learned patterns |
| **Example** | PR #142 review progress | "auth/ has had 5 security bugs" |

**The Magic**: When combined, the assistant can say:
> "You're reviewing auth code (short-term context) and this module has had 3 security issues in the past (long-term pattern). Line 52 looks similar to the bug we found in PR #98. Want me to flag it?"

---

## Next Steps

1. **Add GitHub integration** - Auto-post review comments
2. **Team patterns** - Share long-term memory across team
3. **Custom rules** - Add domain-specific review patterns
4. **Metrics dashboard** - Track review effectiveness over time

**Related examples**:
- [Multi-Agent Coordination](multi-agent-team-coordination.md) - Deep dive into team sessions
- [SBAR Clinical Handoff](sbar-clinical-handoff.md) - Domain-specific patterns
- [Adaptive Learning](adaptive-learning-system.md) - Self-improving patterns

---

## Troubleshooting

**Redis not connected**
```bash
# Start Redis
docker run -d -p 6379:6379 redis:alpine

# Or use in-memory fallback (loses short-term on restart)
memory = UnifiedMemory(redis_url=None)
```

**No historical patterns showing**
- Run a few review sessions first to build history
- Check SQLite file exists: `ls .empathy/reviews.db`

**Predictions not appearing**
- Set `target_level=4` for anticipatory features
- Need sufficient historical data (5+ sessions recommended)

---

**Need help?** See the [API Reference](../api-reference/index.md) or [Short-Term Memory Reference](../SHORT_TERM_MEMORY.md).
