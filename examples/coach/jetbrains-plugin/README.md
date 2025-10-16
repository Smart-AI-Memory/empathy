# Coach JetBrains Plugin

AI development assistant with Level 4 Anticipatory Empathy for IntelliJ Platform IDEs.

## Supported IDEs

- IntelliJ IDEA (Community & Ultimate)
- PyCharm (Community & Professional)
- WebStorm
- PhpStorm
- GoLand
- RubyMine
- CLion
- Rider
- Android Studio

## Features

### 🎯 16 Specialized Wizards
Full wizard suite integrated into IntelliJ Platform:
- SecurityWizard, PerformanceWizard, DebuggingWizard
- TestingWizard, RefactoringWizard, APIWizard
- DatabaseWizard, DevOpsWizard, MonitoringWizard
- DocumentationWizard, AccessibilityWizard, LocalizationWizard
- ComplianceWizard, OnboardingWizard, DesignReviewWizard
- RetrospectiveWizard

### 🔍 Code Inspections
Real-time issue detection with quick fixes:
- **Security**: SQL injection, XSS, CSRF vulnerabilities
- **Performance**: N+1 queries, inefficient algorithms
- **Accessibility**: WCAG compliance, ARIA labels

### 🛠️ Tool Window
Full Coach interface in IDE:
- Browse all 16 wizards
- View generated artifacts
- Access pattern library

### ⚡ Intention Actions
Quick fixes accessible via Alt+Enter:
- Apply security fixes
- Optimize performance
- Improve accessibility

### 📊 Background Analysis
Continuous code analysis while you work

## Installation

### From JetBrains Marketplace
1. Open IDE Settings (Cmd+, on Mac, Ctrl+Alt+S on Windows/Linux)
2. Go to Plugins → Marketplace
3. Search for "Coach AI"
4. Click Install
5. Restart IDE

### From Source
```bash
# Clone repository
git clone https://github.com/your-org/empathy-framework.git
cd empathy-framework/examples/coach/jetbrains-plugin

# Build plugin
./gradlew buildPlugin

# Install from disk
# Settings → Plugins → ⚙️ → Install Plugin from Disk
# Select: build/distributions/coach-1.0.0.zip
```

## Requirements

- IntelliJ Platform 2024.1 or higher
- Python 3.12+ (with `python3` in PATH)
- Git (optional, for git context features)

## Usage

### Context Menu
Right-click in editor:
- **Coach → Analyze Current File**
- **Coach → Run Security Audit**
- **Coach → Generate Test Suite**
- **Coach → Multi-Wizard Review**

### Main Menu
**Tools → Coach → [Select Action]**

### Tool Window
Click "Coach" tab on right side to:
- Browse wizards by category
- View recent artifacts
- Access pattern library

### Inspections
Enable in Settings → Editor → Inspections → Coach:
- Security Issues (enabled by default)
- Performance Issues (enabled by default)
- Accessibility Issues (enabled by default)

### Keyboard Shortcuts
Configure in Settings → Keymap → Plug-ins → Coach

## Configuration

**Settings → Tools → Coach**

```
Auto-Triggers:
  ☑ Run SecurityWizard on file save
  ☑ Run DebuggingWizard on test failure
  ☑ Run DocumentationWizard on commit

Background Analysis:
  ☑ Enable background analysis
  Interval: 10 minutes

LSP Server:
  Path: (auto-detected)
  Log Level: INFO
```

## Building from Source

```bash
# Build
./gradlew buildPlugin

# Run in sandbox IDE
./gradlew runIde

# Run tests
./gradlew test

# Verify plugin
./gradlew verifyPlugin
```

## Development

### Project Structure
```
src/main/
├── kotlin/com/deepstudyai/coach/
│   ├── CoachPlugin.kt              # Entry point
│   ├── lsp/
│   │   └── CoachLSPClient.kt      # LSP client
│   ├── inspections/
│   │   ├── SecurityInspection.kt
│   │   ├── PerformanceInspection.kt
│   │   └── AccessibilityInspection.kt
│   ├── actions/
│   │   ├── AnalyzeFileAction.kt
│   │   ├── SecurityAuditAction.kt
│   │   └── MultiWizardAction.kt
│   ├── ui/
│   │   ├── CoachToolWindowFactory.kt
│   │   └── CoachPanel.kt
│   ├── intentions/
│   │   └── CoachIntentionAction.kt
│   └── settings/
│       ├── CoachSettings.kt
│       └── CoachConfigurable.kt
└── resources/
    ├── META-INF/
    │   └── plugin.xml
    └── icons/
```

### Adding New Inspections
1. Create class extending `LocalInspectionTool`
2. Register in `plugin.xml`
3. Implement `checkFile()` or `checkMethod()`
4. Add quick fix as `LocalQuickFix`

### Adding New Actions
1. Create class extending `AnAction`
2. Register in `plugin.xml` actions section
3. Implement `actionPerformed()`

## Known Issues

- LSP server requires Python 3.12+ (older versions not supported)
- Multi-wizard reviews may take 1-2 seconds
- Some features require specific language plugins

## Troubleshooting

### Plugin not loading
- Check IntelliJ version (2024.1+ required)
- Verify Python 3.12+ is installed: `python3 --version`
- Check IDE logs: Help → Show Log in Finder/Explorer

### LSP server not connecting
- Check Python path in settings
- Verify Coach LSP server is installed
- Check LSP logs in IDE console

### Inspections not showing
- Enable in Settings → Editor → Inspections → Coach
- Run Code → Inspect Code manually
- Check file is supported language

## Support

- **Documentation**: https://docs.coach-ai.dev
- **Discord**: https://discord.gg/coach-ai
- **GitHub Issues**: https://github.com/your-org/empathy-framework/issues
- **Email**: support@deepstudyai.com

## License

Apache License 2.0 - See LICENSE in repository root.

---

**Made with ❤️ by Deep Study AI, LLC**
