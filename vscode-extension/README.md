# Empathy Framework for VS Code

AI-powered code health, pattern learning, and cost optimization for VS Code.

## Features

### Status Bar
- Shows learned patterns count
- Displays API cost savings from model routing
- Click to see full status

### Command Palette
All Empathy commands available via `Cmd/Ctrl+Shift+P`:

| Command | Description |
|---------|-------------|
| `Empathy: Morning Briefing` | Start-of-day productivity report |
| `Empathy: Pre-Ship Check` | Pre-commit validation pipeline |
| `Empathy: Fix All Issues` | Auto-fix lint and format issues |
| `Empathy: Learn Patterns` | Extract patterns from git history |
| `Empathy: View API Costs` | Cost tracking dashboard |
| `Empathy: Open Dashboard` | Visual web dashboard |
| `Empathy: Sync to Claude Code` | Sync patterns to Claude |

### Sidebar
Activity bar icon opens three views:
- **Patterns**: Browse learned bug patterns
- **Health**: Code health status
- **Costs**: API usage and savings
	- The **By tier (7 days)** breakdown is documented in `../docs/dashboard-costs-by-tier.md`.
	- The **Cost Simulator (beta)** card lets you experiment with different provider presets and tier mixes to estimate weekly costs and savings.
- **Memory (Beta)**: Redis and pattern storage control panel
  - View Redis status and memory usage
  - Browse stored patterns with classification badges (PUBLIC/INTERNAL/SENSITIVE)
  - Export patterns to JSON
  - Run system health checks
  - Clear short-term memory

## Requirements

- [Empathy Framework](https://pypi.org/project/empathy-framework/) installed
- Python 3.9+

```bash
pip install empathy-framework
```

## Extension Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `empathy.patternsDir` | `./patterns` | Patterns directory |
| `empathy.empathyDir` | `.empathy` | Empathy data directory |
| `empathy.pythonPath` | `python` | Python executable |
| `empathy.showStatusBar` | `true` | Show status bar item |
| `empathy.autoRefresh` | `true` | Auto-refresh data |
| `empathy.refreshInterval` | `300` | Refresh interval (seconds) |
| `empathy.memory.apiHost` | `localhost` | (Beta) Memory API host |
| `empathy.memory.apiPort` | `8765` | (Beta) Memory API port |
| `empathy.memory.autoRefresh` | `true` | (Beta) Auto-refresh memory status |
| `empathy.memory.autoRefreshInterval` | `30` | (Beta) Refresh interval (seconds) |
| `empathy.memory.showNotifications` | `true` | (Beta) Show operation notifications |

## Getting Started

1. Install the extension
2. Open a project with Empathy Framework configured
3. Run `Empathy: Morning Briefing` from command palette
4. Watch patterns accumulate in the sidebar

## Development

```bash
# Install dependencies
npm install

# Compile
npm run compile

# Watch mode
npm run watch

# Package extension
npm run package
```

## License

Fair Source License 0.9 - Copyright 2025 Smart-AI-Memory
