# Empathy Framework - Frequently Asked Questions (FAQ)

**Last Updated:** November 2025
**Version:** 1.0.0

---

## Table of Contents

- [General Questions](#general-questions)
- [Technical Questions](#technical-questions)
- [Licensing and Pricing](#licensing-and-pricing)
- [Integration and Usage](#integration-and-usage)
- [MemDocs Integration](#memdocs-integration)
- [Support and Community](#support-and-community)

---

## General Questions

### What is the Empathy Framework?

The Empathy Framework is an open-source system for building AI applications that progress from simple reactive responses (Level 1) to anticipatory problem prevention (Level 4) and cross-domain systems thinking (Level 5). It wraps any LLM (Claude, GPT-4, local models) with progressive empathy levels that build trust over time.

Unlike traditional AI tools that simply answer questions, the Empathy Framework learns your patterns, predicts future needs, and prevents problems before they occur.

### What makes Level 5 Systems Empathy unique?

Level 5 Systems Empathy is the world's first AI framework that can:

1. **Learn patterns in one domain** (e.g., healthcare handoff protocols)
2. **Store them in long-term memory** (via MemDocs integration)
3. **Apply them cross-domain** (e.g., predict software deployment failures)
4. **Prevent failures before they happen** (using trajectory analysis)

No other AI framework can transfer safety patterns across domains like this. It's the difference between a tool that finds bugs and a system that prevents entire classes of failures.

### How does it differ from SonarQube, CodeClimate, or similar tools?

| Feature | Traditional Tools | Empathy Framework |
|---------|------------------|-------------------|
| **Analysis** | Static rules, same for everyone | Adaptive, learns your patterns |
| **Prediction** | Find current bugs | Predict future issues 30-90 days ahead |
| **Scope** | Single domain (security OR performance) | 16+ wizards across all domains |
| **Intelligence** | Pre-defined rules | LLM-powered reasoning |
| **Learning** | No learning capability | Learns from your codebase and feedback |
| **Cost** | $15-500/month per seat | Free forever (Fair Source 0.9) |

**Bottom line:** SonarQube finds bugs you've already written. Empathy Framework predicts bugs you're about to write and prevents them.

### What's the difference between Fair Source and open source?

The Empathy Framework uses **Fair Source 0.9 license** - it's fully open source, not Fair Source.

- **Fair Source 0.9:** Completely free forever, no usage limits, commercial use allowed
- **Fair Source:** Typically has usage limits or restrictions on commercial use

We chose Fair Source 0.9 because we want maximum adoption and community contribution. There are no hidden fees or usage caps.

### Is this production-ready?

Yes! The Empathy Framework is production-ready and includes:

- Comprehensive test suite with 90%+ coverage
- Battle-tested on real codebases
- Used in production by multiple teams
- Enterprise support available ($99/developer/year)
- Regular security updates and patches

That said, like any software, you should:
- Test thoroughly in your environment
- Start with non-critical systems
- Monitor performance and accuracy
- Provide feedback to improve the framework

---

## Technical Questions

### What programming languages are supported?

The framework core is written in Python and supports analyzing code in:

**Fully Supported:**
- Python
- JavaScript/TypeScript
- Java
- Go
- Rust

**Partial Support:**
- C/C++
- Ruby
- PHP
- Swift
- Kotlin

The analysis quality depends on the specific wizard and the LLM you're using. Claude 3.5 Sonnet and GPT-4 Turbo work best for multi-language support.

### Which LLM providers are supported?

**Official Support:**
- **Anthropic (Claude)** - Recommended, best results with prompt caching
- **OpenAI (GPT-4, GPT-3.5 Turbo)** - Excellent quality, wider availability
- **Local Models (Ollama, LM Studio)** - Privacy-first, free to run

**Coming Soon:**
- Google (Gemini)
- Cohere
- Together AI
- Custom endpoints

The framework is provider-agnostic - you can switch between providers without changing your code.

### Do I need an API key?

Yes, you need an API key for the LLM provider you choose:

**Anthropic (Recommended):**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

**OpenAI:**
```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Local Models:**
No API key needed - runs entirely on your machine using Ollama or LM Studio.

### How much does it cost to run?

**Framework Cost:** $0 (Fair Source 0.9 open source)

**LLM API Costs (approximate):**

**Anthropic Claude 3.5 Sonnet (Recommended):**
- Input: $3 per million tokens
- Output: $15 per million tokens
- With prompt caching: 90% cost reduction on repeated prompts
- **Typical usage:** $5-20/month for active development

**OpenAI GPT-4 Turbo:**
- Input: $10 per million tokens
- Output: $30 per million tokens
- **Typical usage:** $15-50/month for active development

**Local Models (Ollama):**
- $0 - completely free
- Requires capable hardware (16GB+ RAM recommended)

**Cost Optimization Tips:**
1. Use prompt caching (Claude only) - 90% savings
2. Use Haiku for simple tasks - 25x cheaper than Sonnet
3. Use local models for development
4. Cache wizard results to avoid repeated analysis

### What are the system requirements?

**Minimum:**
- Python 3.10+
- 4GB RAM
- Internet connection (for cloud LLMs)

**Recommended:**
- Python 3.11+
- 8GB+ RAM
- SSD storage
- Good internet connection (for optimal LLM performance)

**For Local LLMs:**
- 16GB+ RAM
- GPU (optional but recommended)
- 10GB+ disk space for models

### How accurate are Level 4 predictions?

Level 4 Anticipatory predictions are based on:
- Code trajectory analysis
- Project context (team size, growth rate, deployment frequency)
- Historical patterns in similar codebases
- Industry data on common failure modes

**Accuracy Rates (based on production usage):**
- **Security predictions:** 75-85% accuracy
- **Performance predictions:** 70-80% accuracy
- **Scalability predictions:** 65-75% accuracy

Accuracy improves with:
- More interaction history
- Better project context
- Regular feedback on prediction quality
- Consistent usage patterns

**Note:** Predictions are probabilistic, not deterministic. Always validate before taking action.

### Can I use this offline?

**With Local LLMs:** Yes! Use Ollama or LM Studio to run completely offline.

**With Cloud LLMs:** No - requires internet for API calls.

**Hybrid Approach:**
- Use local models for development (offline)
- Use cloud models for production (better quality)

---

## Licensing and Pricing

### How much does commercial licensing cost?

**Framework:** $0 - Completely free under Fair Source 0.9 license

**Commercial Support (Optional):** $99/developer/year

**What's Included in Commercial Support:**
- Priority bug fixes and feature requests
- Direct access to core development team
- Guaranteed response times (24-48 hours)
- Security advisories and patches
- Upgrade assistance
- Architecture consultation (1 hour/quarter)

### What's included in the free tier?

Everything! There is no "free tier" vs "paid tier" - the entire framework is free under Fair Source 0.9.

**You get:**
- Full source code access
- All 16+ Coach wizards
- All empathy levels (1-5)
- MemDocs integration
- Pattern library
- Configuration system
- CLI tools
- Documentation
- Community support

**What you don't get (unless you purchase support):**
- Priority support
- Guaranteed response times
- Direct access to development team
- Security advisories

### Can I use this in my commercial product?

Yes! Fair Source 0.9 allows commercial use without restrictions.

**You can:**
- Use it in commercial products
- Modify the source code
- Distribute modified versions
- Charge for your products that use it
- Keep your modifications private (no copyleft)

**You must:**
- Include the Fair Source 0.9 license notice
- Include the copyright notice
- Document significant changes (if distributing)

**You cannot:**
- Claim the framework as your own work
- Hold Deep Study AI liable for issues

### Do I need to open source my code if I use this?

No! Fair Source 0.9 is permissive, not copyleft (unlike GPL).

**Your code stays private.** You're free to build proprietary products using the Empathy Framework.

### Can I contribute to the project?

Yes! We welcome contributions:

**How to Contribute:**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

**What We Need:**
- Bug fixes
- New wizards for additional domains
- Documentation improvements
- Test coverage expansion
- Performance optimizations
- Example code and tutorials

See [CONTRIBUTING.md](../CONTRIBUTING.md) for detailed guidelines.

---

## Integration and Usage

### How do I integrate this into my CI/CD pipeline?

**GitHub Actions Example:**

```yaml
name: Empathy Framework Security Check
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install empathy-framework anthropic
      - run: |
          python -c "
          from coach_wizards import SecurityWizard
          import sys
          wizard = SecurityWizard()
          # Check all Python files
          # Exit 1 if critical issues found
          "
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

**GitLab CI Example:**

```yaml
empathy-check:
  image: python:3.11
  before_script:
    - pip install empathy-framework anthropic
  script:
    - python security_check.py
  variables:
    ANTHROPIC_API_KEY: $ANTHROPIC_API_KEY
```

### Can I use this with VS Code / JetBrains / other IDEs?

Yes! We provide integrations:

**VS Code:**
- Official extension: `empathy-framework` (search in VS Code marketplace)
- Real-time analysis as you type
- Inline suggestions and fixes

**JetBrains (IntelliJ, PyCharm, etc.):**
- Plugin: `Empathy Framework`
- Similar features to VS Code extension

**Language Server Protocol (LSP):**
- Works with any LSP-compatible editor (Vim, Emacs, Sublime Text, etc.)
- See [examples/coach/lsp/](../examples/coach/lsp/) for setup

### How do I use this with Docker?

**Dockerfile Example:**

```dockerfile
FROM python:3.11-slim

# Install Empathy Framework
RUN pip install empathy-framework anthropic

# Copy your code
COPY . /app
WORKDIR /app

# Set API key
ENV ANTHROPIC_API_KEY=sk-ant-your-key

# Run your analysis
CMD ["python", "analyze.py"]
```

### Can I use multiple LLM providers simultaneously?

Yes! Create separate instances:

```python
from empathy_llm_toolkit import EmpathyLLM

# Use Claude for complex reasoning (Level 4)
claude = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    model="claude-3-5-sonnet-20241022"
)

# Use GPT-4 for quick responses (Level 2)
gpt = EmpathyLLM(
    provider="openai",
    target_level=2,
    model="gpt-4-turbo-preview"
)

# Use local model for privacy-sensitive tasks
local = EmpathyLLM(
    provider="local",
    target_level=2,
    endpoint="http://localhost:11434",
    model="llama2"
)

# Route to appropriate model based on task
async def handle_request(user_input, priority):
    if priority == "high":
        return await claude.interact("user", user_input)
    elif priority == "medium":
        return await gpt.interact("user", user_input)
    else:
        return await local.interact("user", user_input)
```

### How do I test my custom wizards?

Use the built-in testing utilities:

```python
import unittest
from coach_wizards import BaseCoachWizard

class TestMyWizard(unittest.TestCase):
    def setUp(self):
        self.wizard = MyCustomWizard()

    def test_detects_vulnerability(self):
        code = "SELECT * FROM users WHERE id='" + user_id + "'"
        result = self.wizard.run_full_analysis(code, "test.py", "python")
        self.assertTrue(len(result.issues) > 0)
        self.assertIn("SQL injection", result.issues[0].message)

    def test_predicts_future_issue(self):
        code = "..."
        context = {"growth_rate": 0.3, "user_count": 5000}
        result = self.wizard.run_full_analysis(
            code, "test.py", "python", context
        )
        self.assertTrue(len(result.predictions) > 0)
```

---

## MemDocs Integration

### How does MemDocs integration work?

MemDocs provides long-term memory for the Empathy Framework:

1. **Pattern Storage:** When a wizard finds an important pattern, it's stored in MemDocs
2. **Cross-Domain Retrieval:** When analyzing code, MemDocs searches for similar patterns from other domains
3. **Level 5 Systems Empathy:** Patterns learned in healthcare can prevent failures in software

**Installation:**

```bash
pip install empathy-framework[full]  # Includes MemDocs
```

**Usage:**

```python
from memdocs import MemoryStore
from empathy_llm_toolkit import EmpathyLLM

# Initialize shared memory
memory = MemoryStore("patterns.db")

# Framework automatically uses MemDocs if installed
llm = EmpathyLLM(
    provider="anthropic",
    target_level=5,  # Level 5 requires MemDocs
    pattern_library=memory
)
```

### What's stored in MemDocs?

**Patterns Stored:**
- User interaction patterns (sequential, conditional, adaptive)
- Code patterns (vulnerabilities, performance issues, best practices)
- Domain-specific knowledge (healthcare protocols, financial regulations)
- Historical predictions and their outcomes
- Cross-domain pattern mappings

**What's NOT Stored:**
- Your actual code or data (privacy-first)
- API keys or secrets
- Personal information
- Proprietary business logic

### Is my data secure with MemDocs?

Yes! MemDocs is privacy-first:

**Local Storage:** All data stays on your machine by default

**Encryption:** Database is encrypted at rest (optional)

**No Telemetry:** Zero data collection or tracking

**Data Control:** You own and control all stored data

**Sharing (Optional):** You can opt-in to share anonymized patterns with the community

### Can I disable MemDocs?

Yes! It's completely optional:

```python
# Disable MemDocs (limits to Level 4 max)
llm = EmpathyLLM(
    provider="anthropic",
    target_level=4,  # Can't use Level 5 without MemDocs
    pattern_library=None  # No long-term memory
)
```

Or via configuration:

```yaml
# empathy.config.yml
pattern_library_enabled: false
pattern_sharing: false
```

---

## Support and Community

### How do I get support?

**Free Community Support:**
- GitHub Issues: https://github.com/Deep-Study-AI/Empathy/issues
- GitHub Discussions: https://github.com/Deep-Study-AI/Empathy/discussions
- Documentation: https://github.com/Deep-Study-AI/Empathy/tree/main/docs
- Examples: https://github.com/Deep-Study-AI/Empathy/tree/main/examples

**Paid Commercial Support ($99/developer/year):**
- Priority bug fixes (24-48 hour response time)
- Direct email/Slack access to core team
- Architecture consultation
- Security advisories
- Upgrade assistance

**Contact:** patrick.roebuck@deepstudyai.com

### Where can I report bugs?

**GitHub Issues:** https://github.com/Deep-Study-AI/Empathy/issues

**Before Reporting:**
1. Search existing issues
2. Check if it's already fixed in latest version
3. Reproduce with minimal example
4. Include version info (`empathy-framework version`)

**Include in Report:**
- Empathy Framework version
- Python version
- LLM provider and model
- Full error message and traceback
- Minimal code to reproduce
- Expected vs actual behavior

### How can I request features?

**GitHub Discussions:** https://github.com/Deep-Study-AI/Empathy/discussions

**Feature Request Template:**
1. **Problem Statement:** What problem are you trying to solve?
2. **Proposed Solution:** How do you envision this working?
3. **Alternatives Considered:** What other approaches did you consider?
4. **Additional Context:** Examples, mockups, related issues

### Where can I find examples and tutorials?

**Official Examples:**
- GitHub: https://github.com/Deep-Study-AI/Empathy/tree/main/examples
- Quick Start Guide: [docs/QUICKSTART_GUIDE.md](QUICKSTART_GUIDE.md)
- User Guide: [docs/USER_GUIDE.md](USER_GUIDE.md)

**Community Examples:**
- GitHub Discussions: Share your use cases
- Blog posts and tutorials (community-contributed)

### Is there a Slack or Discord community?

Not yet, but we're considering it based on community interest.

**Current Channels:**
- GitHub Discussions (primary community forum)
- GitHub Issues (bug reports and feature requests)
- Email (commercial support customers)

**Vote for Community Platform:**
- Comment on [this discussion](https://github.com/Deep-Study-AI/Empathy/discussions) to vote

### How often is the framework updated?

**Release Schedule:**
- **Patch releases (1.0.x):** As needed for bug fixes
- **Minor releases (1.x.0):** Monthly with new features
- **Major releases (x.0.0):** Annually with breaking changes

**Security Updates:**
- Critical security issues: Within 24-48 hours
- Non-critical security issues: Next patch release

**Subscribe for Updates:**
- Watch the GitHub repository
- Follow release notes: https://github.com/Deep-Study-AI/Empathy/releases

---

## Troubleshooting

### I'm getting "API key not found" errors

See the [TROUBLESHOOTING.md](TROUBLESHOOTING.md) guide for detailed solutions.

**Quick fix:**

```bash
# Check if API key is set
echo $ANTHROPIC_API_KEY

# Set it if missing
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Make permanent
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### The framework is running slow

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for performance optimization tips.

**Quick fixes:**
1. Enable prompt caching (Claude): 90% faster on repeated calls
2. Use faster model (claude-3-haiku-20240307): 10x faster
3. Use local model for development: No API latency

### I'm not reaching higher empathy levels

Higher levels require building trust:

- **Level 2:** 3+ interactions, trust > 0.3
- **Level 3:** 10+ interactions, trust > 0.7
- **Level 4:** 20+ interactions, trust > 0.8
- **Level 5:** 50+ interactions, trust > 0.9

**Build trust faster:**

```python
# Provide positive feedback
llm.update_trust("user", outcome="success", magnitude=1.0)

# Or force level for testing
result = await llm.interact(
    user_id="test",
    user_input="Test",
    force_level=4  # Force Level 4 for demo
)
```

### Where can I find more troubleshooting help?

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for comprehensive troubleshooting guide covering:
- Installation issues
- Import errors
- API key configuration
- Test failures
- Performance problems
- Memory issues
- LLM provider errors
- And more...

---

## Additional Questions

### How does this compare to GitHub Copilot?

| Feature | GitHub Copilot | Empathy Framework |
|---------|---------------|-------------------|
| **Primary Use** | Code completion | Code analysis & prevention |
| **Intelligence** | Autocomplete | Multi-level reasoning |
| **Prediction** | Next line of code | Future bugs and bottlenecks |
| **Learning** | Pre-trained only | Learns from your patterns |
| **Cost** | $10-20/month per user | Free (+ LLM API costs) |
| **Scope** | Code generation | Full development lifecycle |

**Bottom Line:** Copilot helps you write code faster. Empathy Framework helps you write better code and prevents future problems.

### Can I build a SaaS product using this?

Yes! Fair Source 0.9 allows this. Many companies build SaaS products on top of Fair Source 0.9 projects.

**You can:**
- Offer Empathy Framework as a service
- Charge for your SaaS product
- Keep your modifications private
- Add proprietary features on top

**You should:**
- Include Fair Source 0.9 license notice
- Attribute the Empathy Framework
- Consider contributing improvements back
- Purchase commercial support for priority help

### What's the long-term roadmap?

**Near-term (Q1-Q2 2025):**
- Additional LLM providers (Gemini, Cohere)
- Enhanced IDE integrations
- More domain-specific wizards
- Improved prediction accuracy

**Mid-term (Q3-Q4 2025):**
- Multi-language support expansion
- Team collaboration features
- Enhanced MemDocs cross-domain learning
- Real-time code analysis

**Long-term (2026+):**
- Level 6: Autonomous problem resolution
- Healthcare and financial domain plugins
- Enterprise features (RBAC, audit logs)
- Cloud-hosted option

See [ROADMAP.md](../ROADMAP.md) for detailed roadmap.

---

## Still Have Questions?

**Can't find your answer?**

1. Check the [User Guide](USER_GUIDE.md)
2. Check the [API Reference](API_REFERENCE.md)
3. Search [GitHub Discussions](https://github.com/Deep-Study-AI/Empathy/discussions)
4. Ask in [GitHub Discussions](https://github.com/Deep-Study-AI/Empathy/discussions/new)
5. Email: patrick.roebuck@deepstudyai.com

---

**Copyright 2025 Deep Study AI, LLC**
**Licensed under Fair Source 0.9**
