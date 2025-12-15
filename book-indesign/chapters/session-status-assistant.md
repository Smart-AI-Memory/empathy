# The Session Status Assistant

## Never Lose Context Again

How many times have you returned to a project after lunch, a meeting, or a weekend, only to spend the first 15 minutes trying to remember where you left off? What was that bug you were investigating? Did you resolve that security finding? What's the status of the tech debt you were tackling?

The Session Status Assistant solves this problem by proactively briefing you when you return to your project. It's like having a thoughtful colleague who kept notes while you were away and is ready to bring you up to speed the moment you sit down.

## The Philosophy Behind It

The Session Status Assistant embodies a core principle of the Empathy Framework: **anticipatory collaboration**. Rather than waiting for you to ask "what should I work on?", the system proactively surfaces what matters most.

This represents Level 4 empathy in action - the system:
1. **Remembers** your last interaction
2. **Detects** when you've been away
3. **Analyzes** what changed while you were gone
4. **Prioritizes** what needs your attention
5. **Presents** actionable next steps

## How It Works

When you start a new session after being away for 60 minutes or more (configurable), the assistant automatically scans five data sources:

### 1. Security Decisions (Priority 0)
Security issues that need human judgment are surfaced first. These might be findings from automated scanners that require you to mark them as false positives, accepted risks, or items needing remediation.

### 2. High-Severity Bugs (Priority 1)
Critical bugs that could affect users in production. These demand immediate attention.

### 3. Investigating Bugs (Priority 2)
Bugs you've identified but haven't resolved yet. The assistant reminds you of the debugging work in progress.

### 4. Tech Debt Trajectory (Priority 3)
Is your technical debt growing or shrinking? The assistant tracks this over time and alerts you when debt is increasing.

### 5. Roadmap Items (Priority 4)
Unchecked items from your PLAN_*.md files. Work you've planned but haven't completed.

### 6. WIP Commits (Priority 5)
Recent commits with "WIP", "TODO", or "FIXME" in the message - work that needs follow-up.

## The Priority-Weighted System

Not all issues are created equal. The assistant uses a weighted priority system to ensure the most critical items surface first:

| Priority | Category | Weight | Icon |
|----------|----------|--------|------|
| P0 | Security pending | 100 | Red |
| P1 | Bugs high-severity | 80 | Red |
| P2 | Bugs investigating | 60 | Yellow |
| P3 | Tech debt increasing | 40 | Yellow |
| P4 | Roadmap unchecked | 30 | Blue |
| P5 | Commits WIP/TODO | 20 | White |

This means a pending security decision will always appear before a WIP commit, regardless of when they were created.

## Interactive Selection

The assistant doesn't just show you what needs attention - it helps you take action. Each item is numbered, and selecting an item provides a detailed action prompt:

```
📊 Project Status (3 items need attention)

🟡 Bugs: 2 investigating
   → Resolve null_reference in OrderList.tsx

🟡 Tech Debt: Increasing (+15 items)
   → Total: 343 items

🔵 Roadmap: 5 unchecked items
   → Continue: Add user authentication

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Fix bug  [2] Address debt  [3] Continue roadmap
```

Selecting [1] provides the full context:

```
Action prompt for selection 1:

Continue investigating bug bug_20251212_abc123:
TypeError: Cannot read property 'map' of undefined.
File: src/components/OrderList.tsx

Use: empathy patterns resolve bug_20251212_abc123
  --root-cause '<cause>' --fix '<fix>'
```

## Celebrating Wins

The assistant doesn't just focus on problems - it also celebrates progress. If you resolved bugs since your last session, decreased tech debt, or completed roadmap items, you'll see:

```
🎉 Wins since last session:
   • 3 bugs resolved
   • Tech debt decreased by 12 items
```

This positive reinforcement helps maintain momentum and acknowledges your progress.

## State Persistence

The assistant maintains two types of state:

### Session State
Stored in `.empathy/session_state.json`, this tracks:
- Last interaction timestamp
- Total interaction count

### Daily Snapshots
Stored in `.empathy/status_history/YYYY-MM-DD.json`, these capture:
- Daily status summaries
- Bug counts
- Wins detected

This historical data enables trend analysis and win detection.

## Configuration

The assistant is configurable through `empathy.config.yml`:

```yaml
session_status:
  enabled: true
  inactivity_minutes: 60  # Trigger threshold
  max_display_items: 5    # Items in summary view
  show_wins: true         # Celebrate progress
  priority_weights:       # Customize importance
    security: 100
    bugs_high: 80
    bugs_investigating: 60
    tech_debt: 40
    roadmap: 30
    commits: 20
```

## Command Line Interface

The assistant is available via the CLI:

```bash
# Show status (if enough time has passed)
empathy status

# Force show regardless of inactivity
empathy status --force

# Show all items without limit
empathy status --full

# Output as JSON for tooling
empathy status --json

# Get action prompt for item 1
empathy status --select 1
```

## Integration with Claude Code

When used with Claude Code, the Session Status Assistant provides context that helps Claude understand your current priorities. The status can be injected into CLAUDE.md, giving Claude awareness of:

- What bugs you're tracking
- What security decisions are pending
- The trajectory of your tech debt
- Your planned roadmap items

This context enables more relevant suggestions and helps Claude assist with your most pressing concerns.

## The Bigger Picture

The Session Status Assistant is more than a convenience feature - it's a fundamental shift in how AI assists with software development. Instead of being a reactive tool that responds to queries, it becomes a proactive partner that:

1. **Maintains awareness** of your project's state
2. **Identifies** what needs attention
3. **Prioritizes** based on severity
4. **Guides** you to actionable next steps
5. **Learns** from your patterns over time

This is anticipatory empathy applied to developer experience - understanding not just what you're asking, but what you need to know before you even ask.

## Looking Forward

The Session Status Assistant is the foundation for a broader vision: a comprehensive Code Health Assistant that helps maintain code quality through:

- **Enhanced health checks** (linting, typing, testing)
- **Auto-fix capabilities** for common issues
- **Learning and improvement** from your patterns
- **Team-wide health dashboards**

The goal is not to replace developer judgment, but to augment it - handling the routine so you can focus on what matters most.

---

*The Session Status Assistant was introduced in Empathy Framework v2.1.5*
