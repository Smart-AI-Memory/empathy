# Change Log

All notable changes to the "Empathy Framework" extension will be documented in this file.

## [1.3.0] - 2025-12-30

### Added

- **Test Generator Wizard** - Interactive 4-step wizard in sidebar
  - Step 1: Select file/folder to scan for test candidates
  - Step 2: Review candidates with priority scores and hotspot badges
  - Step 3: Select functions/classes with AST analysis (complexity scores, async badges)
  - Step 4: Preview generated pytest code with syntax highlighting and apply
- **Security Diagnostics** - Security scan findings appear as squiggles in editor
  - Critical/High → Red error squiggles
  - Medium → Yellow warning squiggles
  - Low → Blue info squiggles
  - Findings persist across VS Code restarts
  - File watcher auto-refreshes diagnostics
- **Run Security Scan Command** - `Empathy: Run Security Scan` from command palette
- **FilePickerService** - Centralized file/folder selection across all panels
  - Singleton service with consistent API for all panels
  - Standardized `filePicker:*` message protocol
  - Four selection modes: File, Folder, Active File, Project Root
  - Predefined file filters (PYTHON, CODE_ALL, DOCUMENTS, ALL)
  - Uses OS-native dialogs via `vscode.window.showOpenDialog()`

### Changed

- **RefactorAdvisorPanel** - Added Folder and Project buttons for broader scope selection
- **ResearchSynthesisPanel** - Added Active and Project buttons for quick source addition
- **TestGeneratorPanel** - Input field now starts empty with placeholder (was ".")

## [1.2.0] - 2025-12-29

### Added

- **URI Handler** - Support for `vscode://Smart-AI-Memory.empathy-framework/runCommand?command=...` URLs
  - Enables "Run in Empathy" buttons in documentation
  - Security: Only allows commands starting with `empathy`
  - Reuses or creates "Empathy Docs" terminal
- **openWorkflow URI** - Direct workflow launching via `vscode://Smart-AI-Memory.empathy-framework/openWorkflow?workflow=...`

### Documentation

- Added "Run in VS Code" buttons to Quick Start guide
- Added interactive buttons to CLI Guide
- Custom CSS styling for documentation buttons

## [1.1.0] - 2025-12-25

### Added

- **Dashboard Panel** - Rich webview with 10 integrated workflows
- **Initialize Wizard** - Multi-step onboarding for new users
- **Memory Panel** - Redis-backed short-term memory management
- **Refactor Advisor** - Interactive refactoring with 2-agent crew
- **Research Synthesis** - Multi-document research panel

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
