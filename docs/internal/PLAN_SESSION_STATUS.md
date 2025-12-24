# Session Status Assistant - v2.1.5 Plan

**Status**: Implemented (Core Features)
**Priority**: High
**Completed**: 2025-12-15

## Overview

A proactive briefing system that greets developers when they return to an Empathy-enhanced project, providing a prioritized status report with actionable items.

## Trigger Conditions

- **Time-based**: First interaction after ≥60 minutes of inactivity (configurable)
- **Day-based**: First interaction of a new calendar day
- **Manual**: `empathy status` command
- **Scope**: Only projects with Empathy Framework patterns directory

## Priority System (Weighted)

| Priority | Category | Weight | Icon | Rationale |
|----------|----------|--------|------|-----------|
| P0 | Security pending | 100 | 🔴 | Immediate risk |
| P1 | Bugs high-severity | 80 | 🔴 | Runtime failures |
| P2 | Bugs investigating | 60 | 🟡 | Unresolved work |
| P3 | Tech debt increasing | 40 | 🟡 | Trajectory matters |
| P4 | Roadmap unchecked | 30 | 🔵 | Planned work |
| P5 | Commits WIP/TODO | 20 | ⚪ | Nice-to-know |

## Output Format

```
📊 Project Status (6 items need attention)

🔴 Security: 2 decisions pending review
   → Review XSS finding in auth.ts

🟡 Bugs: 3 investigating, 1 high-severity
   → Resolve null_reference in OrderList.tsx

🟢 Tech Debt: Stable (343 items, +0 this week)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[1] Fix high-severity bug  [2] Review security  [3] See full status
```

## Selection Behavior

When user selects an item (types number or clicks):
- Inject the full action prompt
- Include relevant context (bug details, file paths, historical fixes)
- Use active voice ("Fix", "Review", "Resolve", "Continue")

## Data Sources

1. `patterns/debugging/*.json` - Bug patterns (investigating, resolved)
2. `patterns/security/*.json` - Security decisions (pending, accepted)
3. `patterns/tech_debt/*.json` - Tech debt snapshots (trajectory)
4. `docs/PLAN_*.md` - Roadmap items (unchecked tasks)
5. Git log - Recent commits needing follow-up (WIP, TODO, FIXME)

## Storage Architecture

```
.empathy/
├── session_state.json      # Short-term (last session, timestamps)
└── status_history/         # Long-term (daily snapshots)
    └── YYYY-MM-DD.json
```

## Configuration

```yaml
# empathy.config.yml
session_status:
  enabled: true
  inactivity_minutes: 60
  max_display_items: 5
  show_wins: true  # "3 bugs resolved since last session"
  priority_weights:
    security: 100
    bugs_high: 80
    bugs_investigating: 60
    tech_debt: 40
    roadmap: 30
    commits: 20
```

---

## Implementation Phases

### Phase 1: SessionStatusCollector Class
**File**: `empathy_llm_toolkit/session_status.py`

```python
class SessionStatusCollector:
    """Aggregates project status from all data sources."""

    def collect(self) -> dict:
        """Returns prioritized status items."""

    def should_show(self) -> bool:
        """Check if enough time has passed."""

    def record_interaction(self) -> None:
        """Update last interaction timestamp."""
```

**Tests**:
- [x] Priority calculation with mock data
- [x] Trigger logic (time-based, day-based)
- [x] Each data source parser

### Phase 2: Priority Calculation
- Load all data sources
- Calculate weighted score for each item
- Sort by score descending
- Group by category for display

**Tests**:
- [x] Correct ordering with mixed priorities
- [x] Edge cases (no items, all same priority)

### Phase 3: Output Formatter
- Markdown for terminal/Claude Code
- Numbered selectable items
- Expandable "See full status"

**Tests**:
- [x] Snapshot tests for various scenarios
- [x] Empty state, many items, mixed severity

### Phase 4: CLI Command
`empathy status [--full] [--json]`

**Tests**:
- [x] CLI integration tests
- [x] JSON output format

### Phase 5: CLAUDE.md Integration
- Auto-inject status when session starts
- Provide as context to Claude Code

**Tests**:
- [ ] Manual verification with Claude Code session

### Phase 6: Wins Detection
Compare current to previous snapshot:
- "You resolved 3 bugs since yesterday"
- "Tech debt decreased by 5 items"

**Tests**:
- [ ] Delta calculation accuracy
- [ ] Positive/negative messaging

---

## Success Criteria

- [x] Status appears on session start after inactivity
- [x] High-priority items surface first
- [x] Selection triggers actionable workflow
- [x] Wins are celebrated when detected
- [x] Configuration changes take effect immediately

---

## Future Enhancements

- Web dashboard for status visualization
- Team-wide status aggregation
- Slack/Discord notifications for critical items
- VS Code status bar integration

---

*Created: 2025-12-15*
*Target Release: v2.1.5*
