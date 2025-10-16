# Coach VS Code Extension

AI development assistant with Level 4 Anticipatory Empathy - 16 specialized wizards for comprehensive software development support.

## Features

### 🎯 16 Specialized Wizards
- **SecurityWizard**: STRIDE threat modeling, penetration testing
- **PerformanceWizard**: Profiling, optimization, scaling predictions
- **DebuggingWizard**: Root cause analysis, regression tests
- **TestingWizard**: Test strategy, coverage analysis
- **RefactoringWizard**: Code quality, technical debt reduction
- **APIWizard**: OpenAPI specs following industry conventions
- **DatabaseWizard**: Schema design, query optimization
- **DevOpsWizard**: CI/CD pipelines, Terraform, Kubernetes
- **MonitoringWizard**: SLO definition, alerting, incident response
- **DocumentationWizard**: Technical writing, handoff guides
- **AccessibilityWizard**: WCAG compliance, screen reader support
- **LocalizationWizard**: i18n/L10n, translations, RTL support
- **ComplianceWizard**: SOC 2, HIPAA, GDPR audit preparation
- **OnboardingWizard**: Knowledge transfer, learning paths
- **DesignReviewWizard**: Architecture evaluation, trade-offs
- **RetrospectiveWizard**: Post-mortems, process improvement

### ⚡ Level 4 Anticipatory Predictions
Hover over code patterns to see predictions 30-90 days into the future:
- Database connection pools → "Will saturate in ~45 days"
- Rate limits → "Will be exceeded at current growth"
- Security vulnerabilities → Real-time threat detection

### 🔧 Code Actions (Quick Fixes)
- **SecurityWizard**: Fix SQL injection, XSS, CSRF vulnerabilities
- **PerformanceWizard**: Optimize N+1 queries, inefficient algorithms
- **AccessibilityWizard**: Add ARIA labels, fix color contrast

### 📊 Multi-Wizard Collaboration
Orchestrate multiple wizards for complex workflows:
- **New API Endpoint**: APIWizard + SecurityWizard + TestingWizard + DocumentationWizard
- **Database Migration**: DatabaseWizard + DevOpsWizard + MonitoringWizard
- **Production Incident**: MonitoringWizard + DebuggingWizard + RetrospectiveWizard

## Installation

1. Install from VS Code Marketplace: [Coach AI](https://marketplace.visualstudio.com/items?itemName=deepstudyai.coach-ai)
2. Ensure Python 3.12+ is installed
3. Restart VS Code

## Usage

### Command Palette
Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux):
- `Coach: Analyze Current File` - Run analysis on active file
- `Coach: Run Security Audit` - STRIDE threat modeling
- `Coach: Profile Performance` - Identify bottlenecks
- `Coach: Generate Test Suite` - Create comprehensive tests
- `Coach: Multi-Wizard Review` - Orchestrate multiple wizards

### Context Menu
Right-click in editor:
- **Analyze File** - Full wizard analysis
- **Debug Function** - Root cause analysis for selected code
- **Security Audit** - Check for vulnerabilities

### Sidebar Panel
Click Coach icon in activity bar to see:
- **Wizards**: Browse all 16 wizards organized by category
- **Artifacts**: View generated specs, reports, plans
- **Pattern Library**: Access learned patterns

### Auto-Triggers
Configure automatic wizard invocations:
- **On File Save**: Run SecurityWizard + RefactoringWizard
- **On Test Failure**: Auto-invoke DebuggingWizard
- **On Git Commit**: Trigger DocumentationWizard

## Configuration

```json
{
  "coach.autoTriggers.onFileSave": ["SecurityWizard", "RefactoringWizard"],
  "coach.autoTriggers.onTestFailure": true,
  "coach.backgroundAnalysis.enabled": true,
  "coach.backgroundAnalysis.interval": 10,
  "coach.hoverPredictions.enabled": true,
  "coach.lsp.logLevel": "info"
}
```

## Requirements

- VS Code 1.85.0 or higher
- Python 3.12+ (with `python3` in PATH)
- Git (optional, for git context features)

## Known Issues

- LSP server requires Python 3.12+ - older versions not supported
- Multi-wizard reviews may take 1-2 seconds for large projects
- Some language-specific features require language extensions

## Release Notes

### 1.0.0 (2025-10-15)
- Initial release
- 16 specialized wizards
- Level 4 Anticipatory predictions
- Multi-wizard collaboration
- VS Code native integration

## Support

- **Documentation**: https://docs.coach-ai.dev
- **Discord**: https://discord.gg/coach-ai
- **GitHub Issues**: https://github.com/your-org/empathy-framework/issues
- **Email**: support@deepstudyai.com

## License

Apache License 2.0 - See LICENSE in repository root.

---

**Made with ❤️ by Deep Study AI, LLC**
