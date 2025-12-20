# Change Log

All notable changes to the "Empathy Framework" extension will be documented in this file.

## [0.1.0] - 2025-12-20

### Added

- **Status Bar** - Shows learned patterns count and cost savings
- **Command Palette** - 8 commands for morning briefing, pre-ship check, fix-all, learn patterns, costs, dashboard, Claude sync, and status
- **Sidebar Views** - Patterns, Health, and Costs tree views in activity bar
- **Settings** - Configurable patterns directory, Python path, and refresh interval
- **Auto-refresh** - Automatically refreshes pattern data on configured interval

### Commands

| Command | Description |
|---------|-------------|
| `Empathy: Morning Briefing` | Start-of-day productivity report |
| `Empathy: Pre-Ship Check` | Pre-commit validation pipeline |
| `Empathy: Fix All Issues` | Auto-fix lint and format issues |
| `Empathy: Learn Patterns` | Extract patterns from git history |
| `Empathy: View API Costs` | Cost tracking dashboard |
| `Empathy: Open Dashboard` | Visual web dashboard |
| `Empathy: Sync to Claude Code` | Sync patterns to Claude |
| `Empathy: Show Status` | Show current status |

### Requirements

- [Empathy Framework](https://pypi.org/project/empathy-framework/) Python package
- Python 3.10+

```bash
pip install empathy-framework
```
