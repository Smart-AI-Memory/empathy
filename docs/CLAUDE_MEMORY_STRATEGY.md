# Claude Memory Strategy Guide

Best practices for leveraging Claude's memory features to build more effective AI-human collaboration.

---

## Overview

Claude's memory system operates at multiple levels, from session-based context to persistent project knowledge. This guide covers strategies for maximizing the value of each memory layer.

## Memory Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ENTERPRISE LEVEL                         │
│  /etc/claude/CLAUDE.md - Organization-wide policies        │
│  Security rules, compliance requirements, coding standards  │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      USER LEVEL                             │
│  ~/.claude/CLAUDE.md - Personal preferences                │
│  Editor settings, communication style, common patterns      │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT LEVEL                            │
│  .claude/CLAUDE.md - Project-specific context              │
│  Architecture, conventions, learned patterns                │
└─────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    SESSION CONTEXT                          │
│  Current conversation, working files, recent changes        │
└─────────────────────────────────────────────────────────────┘
```

---

## 1. Project-Level Memory (.claude/CLAUDE.md)

### Purpose
The project CLAUDE.md is the most important memory file. It provides Claude with project-specific context that persists across sessions.

### Best Practices

**Structure your CLAUDE.md with clear sections:**

```markdown
# Project Name

## Project Context
Brief description of what this project does and its primary purpose.

## Architecture
- Key architectural decisions
- Directory structure overview
- Core abstractions

## Coding Conventions
- Naming patterns used
- Import ordering preferences
- Error handling approach

## Common Patterns
Patterns that recur in this codebase:
- How authentication is handled
- How errors are logged
- How tests are structured

## Known Issues / Tech Debt
Current limitations or areas needing attention.

## Security Considerations
PII handling, secrets management, access controls.
```

**Keep it focused:**
- Maximum 2000-3000 words for optimal context usage
- Prioritize information Claude needs frequently
- Remove outdated information regularly

**Update after significant changes:**
- New architectural patterns
- Resolved bugs that had widespread impact
- Changed conventions or dependencies

---

## 2. Pattern Learning and Sync

### The Learn → Sync Workflow

```bash
# Step 1: Learn patterns from git history
empathy learn --analyze 50

# Step 2: Sync to Claude Code rules
empathy sync-claude
```

### What Gets Learned

| Pattern Type | Source | Use Case |
|-------------|--------|----------|
| Bug fixes | Git commit messages with "fix:" | Prevent similar bugs |
| Security decisions | Code review comments | Consistent security posture |
| Tech debt | TODO/FIXME comments | Track cleanup work |
| Architecture | Refactoring commits | Understand evolution |

### Pattern File Structure

```
patterns/
├── debugging.json      # Bug fix patterns
├── security.json       # Security decisions
├── tech_debt.json      # Technical debt tracking
└── inspection.json     # Code review findings
```

### Synced Rules Location

```
.claude/
└── rules/
    └── empathy/
        ├── debugging.md    # Bug patterns as Claude rules
        ├── security.md     # Security guidelines
        └── tech_debt.md    # Known debt items
```

---

## 3. Memory Classification Strategy

### Classification Levels

| Level | Description | Storage | Retention |
|-------|-------------|---------|-----------|
| PUBLIC | General patterns, shareable | Unencrypted | 365 days |
| INTERNAL | Proprietary algorithms | Optional encryption | 180 days |
| SENSITIVE | PII, healthcare, financial | AES-256-GCM required | 90 days |

### When to Use Each Level

**PUBLIC:** Generic coding patterns, common bug types, standard practices
```python
# Example: Null check pattern
pattern = {
    "type": "null_reference",
    "fix": "Add optional chaining: data?.items ?? []",
    "classification": "PUBLIC"
}
```

**INTERNAL:** Company-specific algorithms, proprietary logic
```python
# Example: Custom routing algorithm
pattern = {
    "type": "model_routing",
    "description": "Cost-optimized LLM selection",
    "classification": "INTERNAL"
}
```

**SENSITIVE:** Healthcare data, PII, credentials
```python
# Example: Patient data handling
pattern = {
    "type": "phi_handling",
    "requires": "HIPAA compliance",
    "classification": "SENSITIVE"
}
```

---

## 4. Session Context Optimization

### Effective Context Management

**Do:**
- Read relevant files before making changes
- Use the TodoWrite tool to track multi-step tasks
- Reference specific file paths and line numbers
- Provide error messages in full

**Don't:**
- Paste entire large files when only a section is relevant
- Repeat the same context multiple times
- Include irrelevant conversation history

### Context Window Strategy

```
Priority 1: Current task requirements
Priority 2: Relevant code sections
Priority 3: Related patterns/history
Priority 4: General project context
```

---

## 5. Continuous Learning Loop

### The Improvement Cycle

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Develop    │ ──▶ │   Commit     │ ──▶ │   Learn      │
│   with AI    │     │   Changes    │     │   Patterns   │
└──────────────┘     └──────────────┘     └──────────────┘
        ▲                                        │
        │                                        ▼
        │            ┌──────────────┐     ┌──────────────┐
        └─────────── │   AI Uses    │ ◀── │   Sync to    │
                     │   Patterns   │     │   Claude     │
                     └──────────────┘     └──────────────┘
```

### Automation Options

**Pre-commit hook:**
```bash
# .git/hooks/pre-commit
empathy ship --skip-sync
```

**Post-commit hook:**
```bash
# .git/hooks/post-commit
empathy learn --analyze 1
empathy sync-claude
```

**CI/CD integration:**
```yaml
# .github/workflows/patterns.yml
- name: Learn from merged PR
  run: |
    empathy learn --analyze 10
    empathy sync-claude
```

---

## 6. Multi-Project Memory Strategy

### Shared Patterns Across Projects

```
~/.claude/
├── CLAUDE.md           # Personal preferences
└── shared-patterns/
    ├── python.md       # Python best practices
    ├── typescript.md   # TypeScript patterns
    └── security.md     # Security guidelines
```

### Project-Specific Overrides

```markdown
# In project .claude/CLAUDE.md

## Override: Error Handling
This project uses structured logging instead of the standard
approach described in ~/.claude/shared-patterns/python.md.

Use: logger.error("event_name", field=value, error=str(e))
Not: logger.error(f"Error: {e}")
```

---

## 7. Memory Hygiene

### Regular Maintenance Tasks

**Weekly:**
- Review and prune outdated patterns
- Update CLAUDE.md with new conventions
- Check pattern classification accuracy

**Monthly:**
- Archive old patterns (>6 months unused)
- Review security decisions for relevance
- Update tech debt tracking

**Per Release:**
- Document breaking changes in CLAUDE.md
- Learn patterns from the release cycle
- Update architecture section if needed

### Cleanup Commands

```bash
# View current patterns
empathy inspect patterns

# Remove stale patterns (interactive)
empathy patterns prune --older-than 180

# Regenerate pattern summary
empathy learn --regenerate-summary
```

---

## 8. Team Collaboration

### Sharing Memory Effectively

**What to commit:**
- `.claude/CLAUDE.md` - Project context
- `.claude/rules/` - Generated rules
- `patterns/*.json` - Learned patterns

**What NOT to commit:**
- Personal preferences from `~/.claude/`
- Sensitive patterns without encryption
- Session-specific context

### Code Review for Memory Changes

When reviewing CLAUDE.md changes:
1. Is the information accurate and current?
2. Will this help or confuse future AI sessions?
3. Is sensitive information properly classified?
4. Is the file still within optimal size limits?

---

## 9. Troubleshooting

### Common Issues

**Claude doesn't remember project context:**
- Check that `.claude/CLAUDE.md` exists
- Verify file is under 50KB
- Ensure no syntax errors in markdown

**Patterns not being applied:**
- Run `empathy sync-claude` after learning
- Check `.claude/rules/empathy/` directory exists
- Verify patterns are in correct format

**Memory seems stale:**
- Run `empathy learn --analyze 20` to refresh
- Update CLAUDE.md with recent changes
- Clear and regenerate pattern files

### Debugging Commands

```bash
# Check what Claude will see
cat .claude/CLAUDE.md

# Verify patterns directory
ls -la patterns/

# Check synced rules
ls -la .claude/rules/empathy/

# Test pattern learning
empathy learn --analyze 5 --verbose
```

---

## 10. Quick Reference

### Essential Commands

| Command | Purpose |
|---------|---------|
| `empathy learn --analyze N` | Learn from last N commits |
| `empathy sync-claude` | Sync patterns to Claude rules |
| `empathy inspect patterns` | View learned patterns |
| `empathy ship` | Pre-commit validation + sync |
| `empathy morning` | Start-of-day briefing |

### File Locations

| File | Purpose |
|------|---------|
| `.claude/CLAUDE.md` | Project context for Claude |
| `.claude/rules/empathy/*.md` | Generated Claude rules |
| `patterns/*.json` | Learned pattern storage |
| `~/.claude/CLAUDE.md` | User preferences |

### Memory Hierarchy (Precedence)

1. Session context (highest priority)
2. Project CLAUDE.md
3. Project rules (.claude/rules/)
4. User CLAUDE.md
5. Enterprise CLAUDE.md (lowest priority)

---

## Summary

Effective Claude memory management follows these principles:

1. **Keep project CLAUDE.md current** - It's your primary communication channel with Claude across sessions

2. **Learn from history** - Use `empathy learn` to capture patterns from your git history

3. **Sync regularly** - Run `empathy sync-claude` to make patterns available to Claude

4. **Classify appropriately** - Use PUBLIC/INTERNAL/SENSITIVE based on data sensitivity

5. **Maintain hygiene** - Regular cleanup prevents context pollution

6. **Automate the loop** - Integrate learning into your development workflow

---

*Last updated: 2025-12-20*
*Empathy Framework v2.5.0*
