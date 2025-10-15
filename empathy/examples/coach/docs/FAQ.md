# Frequently Asked Questions (FAQ)

Common questions about Coach - AI with Level 4 Anticipatory Empathy.

**Built on LangChain** - Extensible AI wizard framework.

---

## Table of Contents

- [General](#general)
- [Installation & Setup](#installation--setup)
- [Features & Capabilities](#features--capabilities)
- [Wizards](#wizards)
- [Level 4 Predictions](#level-4-predictions)
- [IDE Integration](#ide-integration)
- [Privacy & Security](#privacy--security)
- [Performance](#performance)
- [Customization](#customization)
- [Pricing & Licensing](#pricing--licensing)
- [Troubleshooting](#troubleshooting)

---

## General

### What is Coach?

Coach is an AI-powered development assistant with **Level 4 Anticipatory Empathy** - it predicts problems 30-90 days before they occur. Coach coordinates 16 specialized AI wizards (built on LangChain) to provide comprehensive analysis, from security vulnerabilities to performance bottlenecks to accessibility issues.

### What makes Coach different from other AI coding tools?

**Three key differences**:

1. **Level 4 Anticipatory Empathy** - Predicts future problems, not just current ones
   - Example: "At 5K req/day growth, this connection pool will saturate in ~45 days"

2. **16 Specialized Wizards** - Expert AI agents, not generic models
   - SecurityWizard knows OWASP Top 10
   - PerformanceWizard understands N+1 queries
   - AccessibilityWizard knows WCAG 2.1

3. **Multi-Wizard Collaboration** - Wizards consult each other
   - New API endpoint? APIWizard consults SecurityWizard, PerformanceWizard, DatabaseWizard

### Is Coach open source?

Coach will be **open source** (Apache 2.0 license) after the alpha/beta period. Currently in private alpha for testing.

### Who builds Coach?

Coach is developed by **Deep Study AI, LLC** with contributions from the community. Built on **LangChain** for extensibility.

---

## Installation & Setup

### What are the system requirements?

**Minimum**:
- **Python 3.12+** (required for Coach LSP server)
- **VS Code 1.85+** or **JetBrains IDE 2023.1+**
- **4GB RAM** (8GB recommended)
- **1GB disk space**

**Optional**:
- **OpenAI API key** (for GPT-4) or **Anthropic API key** (for Claude)
- **Ollama** (for local LLMs - no API key needed)

### Do I need an API key?

**Cloud LLMs** (recommended for best results):
- ✅ **OpenAI**: Get key at https://platform.openai.com/api-keys
- ✅ **Anthropic**: Get key at https://console.anthropic.com/

**Local LLMs** (no API key needed):
- ✅ **Ollama**: Install from https://ollama.ai (free, runs locally)

### How do I install Coach?

See complete guide: [INSTALLATION.md](INSTALLATION.md)

**Quick start**:
```bash
# 1. Install Python backend
pip install coach-ai  # (Alpha: install from source)

# 2. Install IDE extension
# VS Code: Install coach-0.1.0.vsix
# JetBrains: Install coach-0.1.0.zip

# 3. Configure API key
export OPENAI_API_KEY="your_key_here"
```

### Which IDEs are supported?

**VS Code**: 1.85+ (Windows, macOS, Linux)

**JetBrains**: 2023.1+
- IntelliJ IDEA
- PyCharm
- WebStorm
- GoLand
- RubyMine
- PHPStorm
- Rider

**Coming soon**: Vim/Neovim, Emacs

### Can I use Coach without an internet connection?

**Yes!** Coach works fully offline with local LLMs (Ollama).

```bash
# Install Ollama
brew install ollama  # macOS
# or download from https://ollama.ai

# Pull model
ollama pull codellama

# Configure Coach
export COACH_LLM_PROVIDER=ollama
export COACH_LLM_MODEL=codellama
```

**Note**: Level 4 predictions may be less accurate with local models compared to GPT-4.

---

## Features & Capabilities

### What programming languages does Coach support?

**Full support** (all features):
- Python
- JavaScript / TypeScript
- JSX / TSX (React)

**Partial support** (diagnostics only):
- Java
- Go
- Rust
- Ruby
- PHP
- C#
- Kotlin
- Swift

**Coming soon**: Full support for Java, Go, Rust

### What problems can Coach detect?

**Security** (SecurityWizard):
- SQL injection, XSS, CSRF
- Hardcoded secrets (passwords, API keys)
- Weak cryptography (MD5, DES)
- Authentication/authorization issues

**Performance** (PerformanceWizard):
- N+1 database queries
- Inefficient algorithms (O(n²) loops)
- Memory leaks
- Blocking operations

**Accessibility** (AccessibilityWizard):
- WCAG 2.1 AA/AAA violations
- Missing alt text, ARIA labels
- Keyboard accessibility
- Color contrast issues

**And 13 more categories** - See [WIZARDS.md](WIZARDS.md)

### Does Coach write code for me?

**Coach provides guidance, not full code generation**:

✅ **What Coach does**:
- Detects issues
- Suggests fixes with code examples
- Provides before/after comparisons
- Explains why changes are needed

❌ **What Coach doesn't do**:
- Generate entire applications
- Write features from scratch (use GitHub Copilot for that)

**Philosophy**: Coach is a **mentor**, not a code generator.

### Can Coach fix bugs automatically?

**Partially**. Coach provides:

1. **Quick fixes** for simple issues:
   - SQL injection → Parameterized query
   - Missing alt text → Add alt attribute
   - N+1 query → Batch query

2. **Guidance** for complex issues:
   - Root cause analysis
   - Step-by-step fix instructions
   - Code examples

**You review and apply fixes** - Coach doesn't change code without your approval.

---

## Wizards

### What are "wizards"?

**Wizards are specialized AI experts** - each focuses on one domain:

- **SecurityWizard** - Security expert (OWASP Top 10)
- **PerformanceWizard** - Performance expert (N+1 queries, scalability)
- **AccessibilityWizard** - Accessibility expert (WCAG 2.1)
- ... (13 more)

Each wizard is a **LangChain agent** with domain-specific knowledge and tools.

### How many wizards are there?

**16 wizards** in v0.1.0:

1. SecurityWizard
2. PerformanceWizard
3. AccessibilityWizard
4. DebuggingWizard
5. TestingWizard
6. RefactoringWizard
7. DatabaseWizard
8. APIWizard
9. ScalingWizard
10. ObservabilityWizard
11. CICDWizard
12. DocumentationWizard
13. ComplianceWizard
14. MigrationWizard
15. MonitoringWizard
16. LocalizationWizard

**Coming in v0.2.0**: 4 more wizards

### Can I create custom wizards?

**Yes!** Coach is built on LangChain for extensibility.

See complete tutorial: [CUSTOM_WIZARDS.md](CUSTOM_WIZARDS.md)

**Quick example**:
```python
from coach.base_wizard import BaseWizard

class MyWizard(BaseWizard):
    name = "MyWizard"
    expertise = "My domain expertise"

    def analyze(self, code, context=""):
        # Your LangChain logic here
        return WizardResult(...)
```

**Use cases**:
- Team-specific coding standards
- Company security policies
- Custom compliance requirements
- Proprietary frameworks

### How do wizards work together?

**Multi-wizard collaboration**:

When you run a complex scenario (e.g., "new_api_endpoint"):
1. **APIWizard** is the primary (designs API structure)
2. APIWizard **consults**:
   - SecurityWizard (authentication needed?)
   - PerformanceWizard (rate limiting?)
   - DatabaseWizard (query optimization?)
3. Wizards **share findings** and **build consensus**
4. Coach presents **unified recommendations**

**8 pre-configured scenarios** - See [USER_MANUAL.md](USER_MANUAL.md#common-workflows)

---

## Level 4 Predictions

### What is "Level 4 Anticipatory Empathy"?

**Traditional tools react to problems. Coach predicts them.**

**Example**:
```python
# Your code:
pool_size = 10

# Traditional tool: ✓ (no problem detected)

# Coach Level 4 Prediction:
⚠️ At 5K req/day growth rate, this connection pool
   will saturate in ~45 days

Impact: 503 errors, timeouts, cascade failures
Preventive Action: Increase to 50 connections NOW
```

**"Level 4"** means predicting 30-90 days ahead with timeline milestones.

### How accurate are Level 4 predictions?

**Depends on context provided**:

- **With good context** (code + traffic patterns + growth rate): 70-85% accuracy
- **With minimal context** (just code): 50-60% accuracy

**Tips for accuracy**:
1. Provide context: "E-commerce payment processing, 1000 req/day, growing 20%/month"
2. Include metrics: Current pool size, request rate, error rate
3. Run predictions regularly (weekly)

### What problems can Coach predict?

**Performance**:
- Connection pool saturation
- Database query slowdown
- Cache inefficiency
- Memory exhaustion

**Scaling**:
- Infrastructure capacity limits
- Database sharding needs
- CDN bandwidth requirements

**Security**:
- Compliance deadline violations (GDPR, SOC 2)
- Session timeout risks
- Certificate expiration

**Technical Debt**:
- Code complexity thresholds
- Test coverage degradation
- Documentation drift

### How often should I run predictions?

**Recommended schedule**:

- **Weekly**: Critical production systems
- **Bi-weekly**: Active development features
- **Monthly**: Stable codebases
- **Before major releases**: Always

**Automated**: Set up CI/CD integration (coming in v0.2.0)

---

## IDE Integration

### How does Coach integrate with my IDE?

**Architecture**:
```
IDE (VS Code/JetBrains)
    ↓ LSP Protocol
Coach LSP Server (Python)
    ↓ LangChain
16 Wizards
    ↓ API
LLM (OpenAI/Anthropic/Ollama)
```

**Benefits**:
- Real-time analysis as you type
- Native IDE features (diagnostics, quick fixes, hover)
- Works with any IDE that supports LSP

### Do I need to install anything besides the IDE extension?

**Yes**, you need:

1. **Python backend** (Coach LSP server)
2. **IDE extension** (VS Code or JetBrains)

**Why separate?**:
- LSP server can serve multiple IDEs
- Backend can be run remotely (team server)
- Easier to update (update backend without reinstalling extension)

### Can multiple team members share one Coach server?

**Yes!** (Coming in v0.2.0)

**Team Server Mode**:
- Run Coach on shared server
- Team members connect via TCP (instead of stdio)
- Shared cache (faster for repeated analyses)
- Centralized configuration

**Current**: Each developer runs their own local server.

### Which is better: VS Code or JetBrains?

**Both are great!** Choose based on your preference:

**VS Code**:
- ✅ Lightweight
- ✅ Fast startup
- ✅ Great for web development
- ❌ Fewer refactoring tools

**JetBrains**:
- ✅ Powerful refactoring
- ✅ Better for Java/Kotlin
- ✅ Integrated tools
- ❌ Heavier resource usage

**Coach features are identical** on both platforms.

---

## Privacy & Security

### Does Coach send my code to the cloud?

**Depends on LLM provider**:

**Cloud LLMs** (OpenAI, Anthropic):
- ✅ Code is sent to LLM API for analysis
- ✅ Code is NOT stored long-term (per provider policies)
- ✅ Code is NOT used for training (with API terms)

**Local LLMs** (Ollama):
- ✅ Code NEVER leaves your machine
- ✅ Fully offline
- ✅ Complete privacy

**Recommendation**: Use local LLMs for sensitive code.

### Can I use Coach with confidential/proprietary code?

**Yes, with local LLMs**:

```bash
# Install Ollama
ollama pull codellama

# Configure Coach
export COACH_LLM_PROVIDER=ollama
export COACH_LLM_MODEL=codellama

# Now code never leaves your machine
```

**Or use OpenAI with Business tier** (no training, enterprise SLA).

### What data does Coach collect?

**Coach LSP server** (local):
- ✅ Logs analysis requests (file paths, wizard names)
- ✅ Logs errors and performance metrics
- ❌ Does NOT log code content in logs
- ❌ Does NOT send telemetry to Deep Study AI

**IDE extensions**:
- ✅ Usage statistics (if you opt-in)
- ❌ No code content

**Complete privacy** - Coach is local-first.

### Is Coach SOC 2 / HIPAA / GDPR compliant?

**Current (v0.1.0)**: No formal certifications

**Roadmap**:
- **SOC 2 Type II**: Q3 2025
- **HIPAA compliance**: Q4 2025
- **GDPR compliance**: Already compliant (no data collection)

**For now**: Use local LLMs for regulated data.

---

## Performance

### How fast is Coach?

**Performance targets** (95th percentile):

- **Pattern-based diagnostics**: <100ms (instant)
- **Deep wizard analysis**: <5s
- **Level 4 prediction**: <10s
- **LSP server startup**: <2s

**Actual performance** depends on:
- LLM provider (GPT-4 is slower than GPT-3.5-turbo)
- Code size (larger files take longer)
- Cache hit rate (cached results are instant)

### Does Coach slow down my IDE?

**No**. Coach runs asynchronously:

- **Diagnostics** run in background (debounced 500ms)
- **UI never blocks** waiting for Coach
- **Resource usage**: ~200MB RAM, <5% CPU

**If you experience slowness**:
1. Check LSP server logs
2. Increase debounce delay
3. Disable auto-analysis on file change

### How can I make Coach faster?

**Tips**:

1. **Enable caching** (default: 5 minutes):
   ```json
   {"coach.enableCache": true, "coach.cacheTTL": 300}
   ```

2. **Use faster LLM**:
   ```bash
   export COACH_LLM_MODEL=gpt-3.5-turbo  # Instead of gpt-4
   ```

3. **Exclude large files**:
   ```json
   {"coach.excludePatterns": ["**/node_modules/**", "**/*.min.js"]}
   ```

4. **Use pattern-based diagnostics only** (disable deep analysis):
   ```json
   {"coach.enableDeepAnalysis": false}
   ```

### Does Coach work offline?

**Yes, with local LLMs**:

```bash
ollama pull codellama
export COACH_LLM_PROVIDER=ollama
```

**Limitations**:
- Level 4 predictions may be less accurate
- Some wizards may have reduced functionality
- No access to latest training data

---

## Customization

### Can I customize which wizards run automatically?

**Yes**:

```json
// VS Code settings.json
{
  "coach.autoTriggers.enabled": true,
  "coach.autoTriggers.wizards": [
    "SecurityWizard",      // Always run
    "PerformanceWizard"    // Always run
    // Other wizards: run on-demand only
  ]
}
```

### Can I change the severity levels?

**Yes**:

```json
{
  "coach.severity.sqlInjection": "error",      // Default: error
  "coach.severity.n1Queries": "warning",       // Default: warning
  "coach.severity.missingAltText": "hint"      // Default: warning
}
```

### Can I disable specific checks?

**Yes**:

```json
{
  "coach.disabledChecks": [
    "SQL_INJECTION",     // Disable specific check
    "HARDCODED_SECRET"
  ]
}
```

**Or disable entire wizard**:

```json
{
  "coach.disabledWizards": ["AccessibilityWizard"]
}
```

### Can I configure which LLM to use per wizard?

**Not yet** (coming in v0.2.0)

**Current**: All wizards use same LLM

**Planned**:
```json
{
  "coach.wizards.SecurityWizard.llm": "gpt-4",           // Accurate
  "coach.wizards.DocumentationWizard.llm": "gpt-3.5-turbo"  // Fast enough
}
```

---

## Pricing & Licensing

### Is Coach free?

**Alpha** (current): Free for 50 alpha testers

**Future pricing**:

- **Free Tier**:
  - Local LLMs only
  - Community support
  - Core features

- **Pro** ($20/month):
  - Cloud LLMs included (GPT-4, Claude)
  - Priority support
  - Advanced features

- **Enterprise** (Custom pricing):
  - SSO, RBAC
  - On-premise deployment
  - SLA + dedicated support
  - Custom wizards development

**Open source after beta** - Core features always free.

### What's included with the OpenAI/Anthropic API costs?

**Coach itself is free**. You pay:

- **OpenAI API costs**: ~$0.03-0.06 per wizard run (GPT-4)
- **Anthropic API costs**: ~$0.02-0.04 per wizard run (Claude)

**Typical usage**: $10-30/month for active developer

**Cost saving tips**:
1. Use GPT-3.5-turbo (~70% cheaper than GPT-4)
2. Enable caching (avoid redundant API calls)
3. Use local LLMs (Ollama - free!)

### Can I use Coach commercially?

**Yes!** Apache 2.0 license allows commercial use.

**Requirements**:
- Include license notice
- State changes if you modify Coach

**No restrictions** on:
- Commercial projects
- Proprietary software
- Client work

### When will Coach be open source?

**Timeline**:
- **Now**: Private alpha (50 testers)
- **Q2 2025**: Public beta (open source core)
- **Q4 2025**: General availability (full open source)

**Why delay?**
- Gather feedback
- Fix critical bugs
- Polish docs
- Ensure quality

---

## Troubleshooting

### Coach isn't starting - what should I check?

**Quick diagnostics**:

```bash
# 1. Check Python version
python3 --version  # Must be 3.12+

# 2. Check Coach is installed
python3 -c "import coach; print(coach.__version__)"

# 3. Check LSP server
cd lsp && python3 -m lsp.server --health-check

# 4. Check logs
tail -f ~/.coach/logs/coach-lsp.log
```

**Common issues**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (26 solutions)

### Diagnostics aren't showing - why?

**Checklist**:

1. **LSP server running?** Check status bar: "Coach: Ready ✓"
2. **File type supported?** Python, JS, TS, JSX, TSX
3. **Diagnostics enabled?** `"coach.enableDiagnostics": true`
4. **Wait a few seconds** - Analysis is async

**Still not working?** Check logs (see TROUBLESHOOTING.md)

### Quick fixes aren't appearing - why?

**Requirements for quick fixes**:

1. ✅ Diagnostic must exist first (red/yellow squiggle)
2. ✅ Cursor must be on diagnostic
3. ✅ Quick fix must be available for that issue

**Trigger manually**: `Ctrl+.` (VS Code) or `Alt+Enter` (JetBrains)

### How do I report a bug?

**Steps**:

1. **Search existing issues**: https://github.com/deepstudyai/coach-alpha/issues
2. **Collect info**:
   ```bash
   # System info
   python3 --version
   coach --version
   # Save logs
   cp ~/.coach/logs/coach-lsp.log bug-report.log
   ```
3. **Create issue**: Use bug report template
4. **Include**: OS, Python version, IDE version, logs, steps to reproduce

**Response time**: 24-48 hours for alpha testers

### Where can I get help?

**Resources** (fastest → slowest):

1. **Discord** (#help channel): ~5-30 minutes
   - https://discord.gg/coach-alpha

2. **GitHub Discussions**: ~1-24 hours
   - https://github.com/deepstudyai/coach-alpha/discussions

3. **GitHub Issues**: ~24-48 hours
   - https://github.com/deepstudyai/coach-alpha/issues

4. **Email**: ~1-3 business days
   - support@deepstudyai.com

**Before asking**:
1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Search existing issues/discussions
3. Try the solution in docs

---

## More Questions?

**Didn't find your answer?**

- **Discord**: https://discord.gg/coach-alpha (#questions channel)
- **Email**: support@deepstudyai.com
- **Docs**: https://docs.coach-ai.dev

**This FAQ is updated regularly** based on common questions. Check back often!

---

**Built with** ❤️ **using LangChain**
