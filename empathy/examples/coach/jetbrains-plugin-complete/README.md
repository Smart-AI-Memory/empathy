# Coach JetBrains Plugin (Complete Implementation)

A comprehensive JetBrains IDE plugin for Coach - the AI-powered code analysis tool with 16 specialized wizards and Level 4 Anticipatory Empathy.

## Overview

This plugin implements **Approach 2**: Complete Framework + IDE Integration, providing both IDE analysis features AND the ability to develop custom Coach wizards within your projects.

## Features

### IDE Integration Features

1. **16 Wizard Inspections**
   - SecurityWizard - SQL injection, XSS, secrets detection
   - PerformanceWizard - N+1 queries, memory leaks
   - AccessibilityWizard - WCAG 2.1 AA compliance
   - TestingWizard - Test coverage analysis
   - RefactoringWizard - Code smell detection
   - DatabaseWizard - Query optimization
   - APIWizard - REST/GraphQL design
   - DebuggingWizard - Debug assistance
   - ScalingWizard - Scaling bottlenecks
   - ObservabilityWizard - Logging/metrics
   - CICDWizard - Pipeline optimization
   - DocumentationWizard - Missing docs
   - ComplianceWizard - GDPR/HIPAA/PCI-DSS
   - MigrationWizard - Framework upgrades
   - MonitoringWizard - SLO/SLI
   - LocalizationWizard - i18n issues

2. **Quick Fixes (Intentions)**
   - Fix SQL injection vulnerabilities
   - Fix XSS vulnerabilities
   - Fix N+1 query problems
   - Add alt text for accessibility
   - Add ARIA labels
   - Generate unit tests
   - Refactor complex code

3. **Level 4 Predictions**
   - Predictive analysis for future issues (30-90 days)
   - Gutter icons showing predictions
   - Confidence-based filtering

4. **Multi-Wizard Collaboration**
   - 8 predefined collaboration scenarios
   - Automatic wizard coordination
   - Collaborative insights

5. **Tool Window**
   - Analysis results display
   - Statistics and metrics
   - Project-wide analysis

6. **Settings UI**
   - LSP server configuration
   - API provider settings (OpenAI, Anthropic, local)
   - Enable/disable wizards
   - Real-time analysis settings
   - Cache configuration

### Framework Features (Approach 2)

7. **Project Templates**
   - "New Coach Wizard Project" template
   - "New Multi-Wizard Project" template
   - Complete project structure generation

8. **Live Templates**
   - `cwizard` - Create a new wizard
   - `cwresult` - Create WizardResult
   - `cwexample` - Create CodeExample
   - `cwtest` - Create wizard test
   - `cwcollab` - Create collaboration config
   - `cwlangchain` - LangChain-powered wizard

9. **Code Completion**
   - Coach framework API autocomplete
   - Wizard method completions
   - Type completions (WizardResult, Severity, etc.)

10. **Documentation**
    - Hover documentation for Coach APIs
    - Inline parameter hints

## Architecture

### Services (6 core services)

1. **CoachLSPClient** (Project-level)
   - LSP communication with Python backend
   - Custom methods: `coach/runWizard`, `coach/multiWizardReview`, `coach/predict`
   - Document synchronization

2. **WizardRegistry** (Project-level)
   - Registry of all 16 built-in wizards
   - Custom wizard registration
   - Wizard metadata management

3. **AnalysisService** (Project-level)
   - Coordinates analysis across wizards
   - Multi-wizard collaboration
   - Result caching and management

4. **CoachSettingsService** (Application-level)
   - Persistent settings storage
   - Wizard enable/disable
   - API configuration

5. **CoachCacheService** (Application-level)
   - LRU cache with expiration
   - Performance optimization
   - Invalidation strategies

6. **CoachProjectService** (Project-level)
   - Project lifecycle management
   - Health checks
   - LSP server initialization

### Extension Points

- **Inspections**: 16 wizard inspections + base class
- **Intentions**: 7 quick fix actions
- **Actions**: 5+ menu/toolbar actions
- **Annotators**: Level 4 prediction display
- **Tool Window**: Results panel
- **Settings**: Application + project configurables
- **Project Templates**: 2 templates for wizard projects
- **Live Templates**: 6 code snippet templates
- **Code Completion**: Coach framework API support

## File Structure

```
jetbrains-plugin-complete/
├── build.gradle.kts                 # Gradle build configuration
├── src/main/
│   ├── kotlin/com/deepstudyai/coach/
│   │   ├── actions/
│   │   │   ├── AnalyzeFileAction.kt
│   │   │   ├── AnalyzeProjectAction.kt
│   │   │   ├── SecurityAuditAction.kt
│   │   │   ├── MultiWizardReviewAction.kt
│   │   │   └── Level4PredictionAction.kt
│   │   ├── annotators/
│   │   │   └── CoachPredictionAnnotator.kt
│   │   ├── completion/
│   │   │   └── CoachCompletionContributor.kt
│   │   ├── inspections/
│   │   │   ├── BaseCoachInspection.kt
│   │   │   ├── SecurityInspection.kt
│   │   │   ├── PerformanceInspection.kt
│   │   │   ├── AccessibilityInspection.kt
│   │   │   ├── TestingInspection.kt
│   │   │   ├── RefactoringInspection.kt
│   │   │   ├── DatabaseInspection.kt
│   │   │   ├── APIInspection.kt
│   │   │   ├── DebuggingInspection.kt
│   │   │   ├── ScalingInspection.kt
│   │   │   ├── ObservabilityInspection.kt
│   │   │   ├── CICDInspection.kt
│   │   │   ├── DocumentationInspection.kt
│   │   │   ├── ComplianceInspection.kt
│   │   │   ├── MigrationInspection.kt
│   │   │   ├── MonitoringInspection.kt
│   │   │   └── LocalizationInspection.kt
│   │   ├── intentions/
│   │   │   ├── FixSQLInjectionIntention.kt
│   │   │   ├── FixXSSIntention.kt
│   │   │   ├── FixNPlusOneIntention.kt
│   │   │   ├── AddAltTextIntention.kt
│   │   │   ├── AddAriaLabelIntention.kt
│   │   │   ├── GenerateTestsIntention.kt
│   │   │   └── RefactorCodeIntention.kt
│   │   ├── listeners/
│   │   │   ├── CoachStartupActivity.kt
│   │   │   └── CoachDocumentListener.kt
│   │   ├── lsp/
│   │   │   └── CoachLSPClient.kt
│   │   ├── services/
│   │   │   ├── AnalysisService.kt
│   │   │   ├── CoachCacheService.kt
│   │   │   ├── CoachProjectService.kt
│   │   │   ├── CoachSettingsService.kt
│   │   │   └── WizardRegistry.kt
│   │   ├── settings/
│   │   │   └── CoachSettingsConfigurable.kt
│   │   ├── templates/
│   │   │   ├── CoachProjectTemplateFactory.kt
│   │   │   └── CoachWizardModuleBuilder.kt
│   │   └── ui/
│   │       └── CoachToolWindowFactory.kt
│   └── resources/
│       ├── META-INF/
│       │   └── plugin.xml             # Plugin descriptor
│       └── liveTemplates/
│           └── Coach.xml              # Live templates
└── README.md
```

## Building

```bash
./gradlew build
```

## Running

```bash
./gradlew runIde
```

This will start an IntelliJ IDEA instance with the Coach plugin installed.

## Testing

```bash
./gradlew test
```

## Installation

1. Build the plugin: `./gradlew buildPlugin`
2. In your JetBrains IDE, go to Settings → Plugins → ⚙️ → Install Plugin from Disk
3. Select the generated JAR from `build/distributions/`

## Configuration

After installation:

1. Go to Settings → Tools → Coach
2. Configure Python path and LSP server script path
3. Configure API provider (OpenAI, Anthropic, or local)
4. Enable/disable specific wizards
5. Adjust analysis settings (real-time, debounce, etc.)

## Usage

### Running Analysis

**Single File:**
- Right-click file → Coach → Analyze File
- Keyboard: Ctrl+Alt+A (Cmd+Alt+A on Mac)

**Entire Project:**
- Menu: Coach → Analyze Project

**Specific Wizard:**
- Menu: Coach → Security Audit (or other wizard-specific actions)

**Multi-Wizard Review:**
- Menu: Coach → Multi-Wizard Review

**Level 4 Predictions:**
- Menu: Coach → Level 4 Predictions

### Viewing Results

- Open the Coach tool window (View → Tool Windows → Coach)
- Results show grouped by file
- Click on results for details

### Creating Custom Wizards (Approach 2)

1. File → New → Project → Coach → Coach Wizard Project
2. Implement your wizard in `wizards/`
3. Use live templates: type `cwizard` and press Tab
4. Test with `cwtest` template
5. Configure in `config/wizard_config.yaml`

### Code Completion

When writing wizards, autocomplete suggestions appear for:
- Coach framework imports
- Wizard methods (`analyze`, `__init__`)
- WizardResult construction
- Severity levels

## Dependencies

- IntelliJ Platform SDK 2023.1+
- Kotlin 1.9.21
- LSP4J 0.21.1
- Kotlin Coroutines 1.7.3

## Python Backend Requirements

The plugin communicates with a Python LSP server:

- Python 3.12+
- Coach framework (pip install coach-framework)
- LangChain
- OpenAI/Anthropic SDK (if using cloud providers)

## License

MIT License

## Contributing

This is example/demonstration code for the Coach project. See the main repository for contribution guidelines.

## Support

For issues and questions, see the main Coach repository.
