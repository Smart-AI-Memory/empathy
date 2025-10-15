# Coach VS Code Extension (Complete Implementation)

A comprehensive VS Code extension for Coach - the AI-powered code analysis tool with 16 specialized wizards and Level 4 Anticipatory Empathy.

## Overview

This extension implements **Approach 2**: Complete Framework + IDE Integration, providing both IDE analysis features AND the ability to develop custom Coach wizards within your projects.

## Features

### IDE Integration Features

#### 1. **16 Wizard Diagnostics**
Real-time code analysis with specialized wizards:
- **SecurityWizard** - SQL injection, XSS, hardcoded secrets
- **PerformanceWizard** - N+1 queries, memory leaks
- **AccessibilityWizard** - WCAG 2.1 AA compliance
- **TestingWizard** - Test coverage analysis
- **RefactoringWizard** - Code smell detection
- **DatabaseWizard** - Query optimization
- **APIWizard** - REST/GraphQL design
- **DebuggingWizard** - Debug assistance
- **ScalingWizard** - Scaling bottlenecks
- **ObservabilityWizard** - Logging/metrics
- **CICDWizard** - Pipeline optimization
- **DocumentationWizard** - Missing documentation
- **ComplianceWizard** - GDPR/HIPAA/PCI-DSS
- **MigrationWizard** - Framework upgrades
- **MonitoringWizard** - SLO/SLI strategies
- **LocalizationWizard** - i18n issues

#### 2. **Code Actions (Quick Fixes)**
Automatic fixes for common issues suggested by wizards

#### 3. **Level 4 Predictions**
- Predictive analysis for future issues (30-90 days ahead)
- Gutter icons showing predictions
- Confidence-based filtering
- Webview panel with detailed prediction analysis

#### 4. **Multi-Wizard Collaboration**
- 8 predefined collaboration scenarios
- Automatic scenario detection
- Collaborative insights from multiple wizards

#### 5. **Activity Bar Views**
Three dedicated views in the Activity Bar:
- **Analysis Results** - Tree view of all analysis results grouped by file
- **Wizards** - Browse all 16 wizards by category
- **Level 4 Predictions** - Current predictions for active file

#### 6. **Commands**
Accessible via Command Palette (Ctrl/Cmd+Shift+P):
- `Coach: Analyze File` - Analyze current file
- `Coach: Analyze Workspace` - Analyze entire workspace
- `Coach: Security Audit` - Run security-focused analysis
- `Coach: Multi-Wizard Review` - Collaborative review
- `Coach: Level 4 Predictions` - Generate predictive analysis
- `Coach: Clear Results` - Clear all results
- `Coach: Refresh Results` - Refresh view
- `Coach: Open Settings` - Open Coach settings
- `Coach: New Wizard Project` - Create wizard project (Framework feature)
- `Coach: New Wizard File` - Create wizard file (Framework feature)

### Framework Features (Approach 2)

#### 7. **Code Snippets**
Snippets for Python wizard development:
- `cwizard` - Create a new wizard
- `cwresult` - Create WizardResult
- `cwexample` - Create CodeExample
- `cwtest` - Create wizard test
- `cwlangchain` - LangChain-powered wizard

#### 8. **Code Completion**
IntelliSense for Coach framework APIs:
- Coach framework imports
- Wizard method signatures
- WizardResult construction
- Severity enums

#### 9. **Project Scaffolding**
Commands to create new wizard projects with complete structure:
- Directory structure (wizards/, tests/, config/)
- Example wizard files
- Configuration files
- Test templates
- Requirements.txt

#### 10. **Custom File Type**
Support for `.wizard.py` files with specialized language features

## Installation

### From VSIX
1. Download the `.vsix` file
2. In VS Code: Extensions → ⋯ → Install from VSIX
3. Select the downloaded file

### From Source
```bash
cd vscode-extension-complete
npm install
npm run compile
# Press F5 to launch Extension Development Host
```

## Configuration

All settings are under `coach.*` namespace:

### Server Settings
- `coach.pythonPath` - Path to Python interpreter (default: `python`)
- `coach.serverScriptPath` - Path to Coach LSP server script
- `coach.autoStartServer` - Auto-start LSP server (default: `true`)

### API Settings
- `coach.apiProvider` - API provider: `openai`, `anthropic`, or `local`
- `coach.apiKey` - API key for LLM provider
- `coach.apiEndpoint` - Custom API endpoint (optional)
- `coach.modelName` - Model name (default: `gpt-4`)

### Analysis Settings
- `coach.enableRealTimeAnalysis` - Enable real-time analysis (default: `true`)
- `coach.analysisDebounceMs` - Debounce delay in ms (default: `1000`)
- `coach.maxConcurrentAnalyses` - Max concurrent analyses (default: `3`)

### Prediction Settings
- `coach.enablePredictions` - Enable Level 4 predictions (default: `true`)
- `coach.predictionTimeframe` - Prediction timeframe in days (default: `60`)
- `coach.predictionConfidenceThreshold` - Min confidence (default: `0.7`)

### Cache Settings
- `coach.enableCaching` - Enable caching (default: `true`)
- `coach.cacheExpirationMinutes` - Cache expiration (default: `60`)

### UI Settings
- `coach.showInlineHints` - Show inline hints (default: `true`)
- `coach.showGutterIcons` - Show gutter icons (default: `true`)

### Wizard Settings
- `coach.enabledWizards` - Array of enabled wizard IDs
- `coach.enableCollaboration` - Enable multi-wizard collaboration (default: `true`)

## Usage

### Running Analysis

**Analyze Current File:**
- Command Palette: `Coach: Analyze File`
- Right-click in editor → Coach → Analyze File
- Results appear in Problems panel and Coach Results view

**Analyze Entire Workspace:**
- Command Palette: `Coach: Analyze Workspace`
- Shows progress notification
- Results grouped by file in Coach Results view

**Security Audit:**
- Command Palette: `Coach: Security Audit`
- Opens detailed webview with security findings

**Multi-Wizard Review:**
- Command Palette: `Coach: Multi-Wizard Review`
- Automatically detects scenario (payment, auth, API, etc.)
- Shows collaborative insights in webview

**Level 4 Predictions:**
- Command Palette: `Coach: Level 4 Predictions`
- Displays future issues with timeframes
- Shows in webview and Predictions view

### Viewing Results

**Problems Panel:**
- View → Problems (Ctrl/Cmd+Shift+M)
- Shows all diagnostics from Coach wizards
- Click to jump to issue location

**Coach Activity Bar:**
- Click Coach icon in Activity Bar
- Browse results by file
- Browse all wizards by category
- View Level 4 predictions

**Webviews:**
- Security Audit, Multi-Wizard Review, and Predictions open in dedicated panels
- Rich HTML display with formatting

### Creating Custom Wizards (Approach 2)

**1. Create New Wizard Project:**
```
Command Palette → Coach: New Wizard Project
```
- Choose location
- Enter project name
- Creates complete project structure

**2. Create New Wizard File:**
```
Command Palette → Coach: New Wizard File
```
- Enter wizard name
- Creates `.wizard.py` file from template

**3. Use Code Snippets:**
In a `.wizard.py` file:
- Type `cwizard` + Tab → Full wizard template
- Type `cwresult` + Tab → WizardResult template
- Type `cwtest` + Tab → Test template

**4. Get IntelliSense:**
- Start typing Coach framework code
- Get autocomplete for imports, methods, classes
- See inline documentation

## File Structure

```
vscode-extension-complete/
├── package.json                # Extension manifest
├── tsconfig.json              # TypeScript config
├── src/
│   ├── extension.ts           # Main activation
│   ├── lsp/
│   │   └── CoachLSPClient.ts  # LSP client
│   ├── services/
│   │   ├── WizardRegistry.ts  # Wizard metadata
│   │   ├── AnalysisService.ts # Analysis coordination
│   │   └── CacheService.ts    # Result caching
│   ├── diagnostics/
│   │   └── DiagnosticsManager.ts  # Diagnostic provider
│   ├── codeActions/
│   │   └── CodeActionProvider.ts  # Quick fixes
│   ├── views/
│   │   ├── CoachResultsProvider.ts    # Results tree
│   │   ├── CoachWizardsProvider.ts    # Wizards tree
│   │   └── CoachPredictionsProvider.ts # Predictions tree
│   ├── decorators/
│   │   └── PredictionDecorator.ts # Gutter icons
│   ├── completion/
│   │   └── CompletionProvider.ts  # IntelliSense
│   └── commands/
│       └── index.ts           # All commands
└── snippets/
    └── coach-python.json      # Code snippets
```

## Architecture

### Services

1. **CoachLSPClient**
   - Manages LSP connection to Python backend
   - Custom methods: `coach/runWizard`, `coach/multiWizardReview`, `coach/predict`
   - Health monitoring

2. **WizardRegistry**
   - Registry of all 16 built-in wizards
   - Metadata management
   - Language and category filtering
   - Collaboration scenario definitions

3. **AnalysisService**
   - Single-wizard and multi-wizard analysis
   - Level 4 prediction support
   - Result management
   - Cache integration
   - Statistics tracking

4. **CacheService**
   - LRU cache with expiration
   - File-based invalidation
   - Performance optimization

### Providers

- **DiagnosticsManager** - Creates VS Code diagnostics from wizard results
- **CodeActionProvider** - Generates quick fixes
- **CompletionProvider** - IntelliSense for Coach APIs
- **Tree View Providers** - Activity Bar views (Results, Wizards, Predictions)
- **PredictionDecorator** - Gutter icons for Level 4 predictions

## Development

### Building
```bash
npm install
npm run compile
```

### Running
```bash
# Launch Extension Development Host
Press F5 in VS Code
```

### Packaging
```bash
npm install -g vsce
vsce package
# Creates coach-vscode-0.1.0.vsix
```

## Dependencies

- **VS Code API**: ^1.80.0
- **vscode-languageclient**: ^8.1.0 (LSP integration)
- **TypeScript**: ^5.1.0

## Python Backend Requirements

The extension communicates with a Python LSP server:
- Python 3.12+
- Coach framework (`pip install coach-framework`)
- LangChain
- OpenAI/Anthropic SDK (if using cloud providers)

## Comparison to JetBrains Plugin

| Feature | VS Code Extension | JetBrains Plugin |
|---------|------------------|------------------|
| Wizards | 16 diagnostics | 16 inspections |
| Quick fixes | CodeActions | Intentions |
| Results UI | Tree views + Webviews | Tool Window |
| Settings | JSON schema | UI panel |
| LSP Integration | vscode-languageclient | LSP4J |
| Framework features | ✅ (Approach 2) | ✅ (Approach 2) |
| Project templates | Command scaffolding | Project wizard |
| Code snippets | Snippets JSON | Live Templates |
| Code completion | CompletionProvider | CompletionContributor |
| Gutter icons | Decorations | Annotators |
| Multi-wizard | ✅ Webview | ✅ UI panel |
| Level 4 predictions | ✅ Full support | ✅ Full support |

Both extensions offer comprehensive Approach 2 functionality!

## License

MIT License

## Contributing

See main Coach repository for contribution guidelines.

## Support

For issues and questions, see the main Coach repository.

---

**🔮 Coach - Beyond static analysis. Predicting tomorrow's bugs, today.**
