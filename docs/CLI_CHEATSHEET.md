# Empathy Framework CLI Cheatsheet

Quick reference for power users. Full docs at [smartaimemory.com/docs](https://www.smartaimemory.com/docs).

---

## Installation

```bash
pip install empathy-framework
```

---

## Core Commands

### Code Health

```bash
empathy health                    # Quick health check
empathy health --deep             # Comprehensive analysis
empathy health --fix              # Auto-fix safe issues
empathy health --dry-run          # Preview fixes without applying
empathy health --check lint       # Run specific check (lint/format/types/tests/security/deps)
empathy health --trends 30        # Show health trends over 30 days
empathy health --json             # JSON output for CI/CD
```

### Code Review (Pattern-Based)

```bash
empathy review                    # Review recent changes
empathy review --staged           # Review staged changes only
empathy review src/               # Review specific files/dirs
empathy review --severity error   # Only show errors (skip warnings/info)
empathy review --json             # JSON output
```

### Code Inspection

```bash
empathy-inspect .                 # Inspect current directory
empathy-inspect . --fix           # Auto-fix formatting/imports
empathy-inspect . --staged        # Staged changes only
empathy-inspect . --quick         # Skip slow checks
empathy-inspect . --format sarif  # SARIF output for GitHub Actions
empathy-inspect . --format html   # HTML dashboard report
empathy-inspect . -o report.json  # Write to file
empathy-inspect . --no-baseline   # Show all findings (ignore suppressions)
empathy-inspect . --baseline-init # Create .empathy-baseline.json
```

---

## Memory & Patterns

### Memory Control Panel

```bash
empathy-memory serve              # Start Redis + API server (recommended)
empathy-memory status             # Show memory system status
empathy-memory start              # Start Redis if not running
empathy-memory stop               # Stop Redis
empathy-memory stats              # Detailed statistics
empathy-memory health             # Run health check
empathy-memory patterns           # List stored patterns
empathy-memory patterns -c SENSITIVE  # Filter by classification
empathy-memory export patterns.json   # Export patterns to file
empathy-memory api --api-port 8765    # Start REST API only
```

### Pattern Management

```bash
empathy patterns list             # List patterns in library
empathy patterns export           # Export patterns
empathy patterns resolve <bug_id> # Mark investigating bug as resolved
```

---

## Claude Code Integration

```bash
empathy-sync-claude               # One-time sync to .claude/rules/empathy/
empathy-sync-claude --watch       # Auto-sync on pattern changes
empathy-sync-claude --dry-run     # Preview without writing
empathy-sync-claude --verbose     # Detailed output
```

**Output structure:**
```
.claude/rules/empathy/
├── bug-patterns.md          # From patterns/debugging/
├── security-decisions.md    # From patterns/security/
├── tech-debt-hotspots.md    # From patterns/tech_debt/
└── coding-patterns.md       # From patterns/inspection/
```

---

## Project Setup

```bash
empathy init                      # Initialize new project
empathy init --format yaml        # Create empathy.config.yaml
empathy init --format json        # Create empathy.config.json
empathy validate config.yaml      # Validate configuration file
empathy info                      # Display framework info
empathy info --config my.yaml     # Info with specific config
empathy version                   # Show version
```

### Interactive Tools

```bash
empathy wizard                    # Interactive setup wizard
empathy run                       # Interactive REPL mode
```

---

## State & Metrics

```bash
empathy state list                # List saved states
empathy state load <id>           # Load specific state
empathy metrics show              # Show metrics
empathy metrics export            # Export metrics
empathy status                    # Session status report
```

---

## CI/CD Integration

### GitHub Actions (SARIF)

```yaml
- name: Run Empathy Inspect
  run: empathy-inspect . --format sarif -o results.sarif

- name: Upload SARIF
  uses: github/codeql-action/upload-sarif@v2
  with:
    sarif_file: results.sarif
```

### Pre-commit Hook

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: empathy-review
        name: Pattern-based code review
        entry: empathy review --staged --severity error
        language: system
        pass_filenames: false

      - id: empathy-sync
        name: Sync patterns to Claude
        entry: empathy-sync-claude
        language: system
        pass_filenames: false
```

---

## Inline Suppressions

```python
# Suppress for current line
data = user_input  # empathy:disable injection reason="sanitized upstream"

# Suppress for next line
# empathy:disable-next-line null_reference
result = obj.value

# Suppress for entire file (at top)
# empathy:disable-file deprecated reason="legacy module"
```

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-...          # Claude API key
OPENAI_API_KEY=sk-...             # OpenAI API key (optional)
EMPATHY_CONFIG=./config.yaml      # Custom config path
EMPATHY_LOG_LEVEL=DEBUG           # Logging level
REDIS_URL=redis://localhost:6379  # Redis connection
```

---

## Quick Workflows

### Morning Check

```bash
empathy health --deep && empathy status
```

### Before Commit

```bash
empathy review --staged && empathy-inspect . --staged --quick
```

### Fix Everything

```bash
empathy health --fix && empathy-inspect . --fix
```

### Sync to Claude Code

```bash
empathy-sync-claude --verbose
```

---

## Getting Help

```bash
empathy --help                    # Main help
empathy <command> --help          # Command-specific help
empathy-inspect --help            # Inspect help
empathy-memory --help             # Memory control help
empathy-sync-claude --help        # Claude sync help
```

---

*Empathy Framework v2.3.0 | [GitHub](https://github.com/Smart-AI-Memory/empathy-framework) | [Docs](https://www.smartaimemory.com/docs)*
