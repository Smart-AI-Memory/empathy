#!/bin/bash
# Create Private GitHub Repository for Coach Alpha Testing
#
# Prerequisites:
# 1. Install GitHub CLI: brew install gh (Mac) or https://cli.github.com/
# 2. Authenticate: gh auth login
#
# Copyright 2025 Deep Study AI, LLC

set -e  # Exit on error

echo "🚀 Creating Coach Alpha Testing Repository"
echo "=========================================="
echo ""

# Configuration
REPO_NAME="coach-alpha"
ORG_NAME="deepstudyai"  # Change to your GitHub org or username
DESCRIPTION="Coach IDE Integration - Private Alpha Testing (Nov 1-29, 2025)"
VISIBILITY="private"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "📦 Install with: brew install gh"
    echo "🔗 Or visit: https://cli.github.com/"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "🔑 Run: gh auth login"
    exit 1
fi

echo "✅ GitHub CLI installed and authenticated"
echo ""

# Create repository
echo "📝 Creating repository: $ORG_NAME/$REPO_NAME"
gh repo create "$ORG_NAME/$REPO_NAME" \
    --private \
    --description "$DESCRIPTION" \
    --clone=false \
    --disable-wiki \
    --disable-issues=false

echo "✅ Repository created: https://github.com/$ORG_NAME/$REPO_NAME"
echo ""

# Clone repository
echo "📥 Cloning repository..."
TEMP_DIR="/tmp/$REPO_NAME"
rm -rf "$TEMP_DIR"
gh repo clone "$ORG_NAME/$REPO_NAME" "$TEMP_DIR"
cd "$TEMP_DIR"

echo "✅ Repository cloned to $TEMP_DIR"
echo ""

# Initialize repository structure
echo "📁 Setting up repository structure..."

# Create .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
.pytest_cache/
.coverage
htmlcov/

# Node.js (VS Code extension)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.npm
.eslintcache
*.tsbuildinfo

# VS Code extension
vscode-extension/out/
vscode-extension/.vscode-test/
*.vsix

# JetBrains
jetbrains-plugin/.gradle/
jetbrains-plugin/build/
jetbrains-plugin/.idea/
jetbrains-plugin/*.iml
jetbrains-plugin/local.properties

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Secrets
.env
.env.local
*.key
*.pem
secrets.json

# Logs
*.log
logs/

# Temporary files
tmp/
temp/
*.tmp
EOF

# Create README.md
cat > README.md << 'EOF'
# Coach Alpha Testing

> **Private Repository** - Alpha Testing Program (Nov 1 - Nov 29, 2025)

## ⚠️ Confidentiality Notice

This is a private alpha testing repository. By accessing this repository, you agree to:

1. **Not share** screenshots, code, or details publicly until Dec 15, 2025
2. **Not discuss** Coach on social media until public beta launch
3. **Report security issues** privately to security@deepstudyai.com

## 🎯 What is Coach?

Coach is an AI development assistant with **Level 4 Anticipatory Empathy** - it predicts issues 30-90 days before they occur.

Built on **LangChain** with 16 specialized wizards for comprehensive software development support.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone this repository (you should already have it if reading this)
cd coach-alpha/lsp

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -m lsp.server --version
```

### 2. IDE Extension

**VS Code**:
```bash
# Install extension from VSIX
code --install-extension releases/coach-alpha-1.0.0.vsix

# Restart VS Code
```

**JetBrains**:
1. Download `releases/coach-jetbrains-1.0.0.zip`
2. Settings → Plugins → ⚙️ → Install Plugin from Disk
3. Select ZIP file
4. Restart IDE

### 3. Configuration

Set your LLM API key:
- **VS Code**: Settings → Coach → LLM API Key
- **JetBrains**: Settings → Tools → Coach → LLM API Key

Supported providers: OpenAI (recommended), Anthropic, Local models

## 📚 Documentation

- [Installation Guide](docs/INSTALLATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [16 Wizards Overview](docs/WIZARDS.md)
- [Creating Custom Wizards](docs/CUSTOM_WIZARDS.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)
- [Bug Report Template](docs/BUG_REPORT.md)
- [Feature Request Template](docs/FEATURE_REQUEST.md)

## 🐛 Reporting Bugs

**Before reporting**:
1. Check [existing issues](https://github.com/deepstudyai/coach-alpha/issues)
2. Try to reproduce 2-3 times
3. Gather logs and screenshots

**Create a new issue** with:
- Severity (Critical/High/Medium/Low)
- IDE and version
- Steps to reproduce
- Expected vs actual behavior
- Logs and screenshots

Use the [Bug Report Template](docs/BUG_REPORT.md)

## ✨ Feature Requests

Have an idea? [Open a feature request](https://github.com/deepstudyai/coach-alpha/issues/new?template=feature_request.md)

## 💬 Communication

- **Discord**: [Coach AI - Alpha Testing](https://discord.gg/coach-alpha-2025) (check email for invite)
- **Office Hours**: Tuesdays 3pm PT in Discord voice channel
- **Email**: alpha@deepstudyai.com

## 📅 Alpha Testing Schedule

- **Week 1** (Nov 1-7): Onboarding & VS Code setup
- **Week 2** (Nov 8-14): Intensive VS Code testing
- **Week 3** (Nov 15-21): JetBrains plugin testing
- **Week 4** (Nov 22-29): Final testing & feedback

### Custom Wizard Workshop
**Date**: Nov 15, 2025 (Week 3)
**Time**: 4pm PT
**Duration**: 1 hour
**Location**: Discord voice channel

Learn to create custom wizards with LangChain!

## 🎯 Testing Priorities

Check Discord `#testing-priorities` channel for weekly focus areas.

## 📦 Releases

| Version | Date | Notes |
|---------|------|-------|
| 1.0.0-alpha.1 | Nov 1, 2025 | Initial alpha release |

Download from [Releases](https://github.com/deepstudyai/coach-alpha/releases)

## 🏗️ Repository Structure

```
coach-alpha/
├── lsp/                    # Language Server (Python)
│   ├── server.py
│   ├── context_collector.py
│   ├── cache.py
│   └── requirements.txt
├── vscode-extension/       # VS Code Extension (TypeScript)
│   ├── src/
│   ├── package.json
│   └── tsconfig.json
├── jetbrains-plugin/       # JetBrains Plugin (Kotlin)
│   ├── src/
│   └── build.gradle.kts
├── docs/                   # Documentation
├── releases/               # Alpha releases (VSIX, ZIP)
└── examples/               # Example custom wizards
```

## 🤝 Contributing (Alpha Testers Only)

1. **Report bugs** in GitHub Issues
2. **Request features** in GitHub Issues
3. **Share custom wizards** in Discord `#custom-wizards`
4. **Provide feedback** in weekly surveys

## ❓ FAQ

### Q: Can I use this on my company's proprietary code?
**A**: Yes! Coach processes everything locally by default. Nothing is sent to our servers unless you explicitly enable cloud features.

### Q: What if I find a security vulnerability?
**A**: Report privately to security@deepstudyai.com (NOT in GitHub Issues or Discord)

### Q: Can I invite my teammates?
**A**: No, this is a closed alpha (50 testers only). Public beta launches Dec 15.

### Q: Will this be open source?
**A**: The core Empathy Framework is Apache 2.0. Coach extensions may have different licensing.

## 📄 License

Proprietary - Alpha Testing License
(This will change to Apache 2.0 or commercial license at public launch)

## 🆘 Support

- **Discord**: Real-time help in `#general-help`
- **Email**: alpha@deepstudyai.com
- **Response Time**: <24 hours

---

**Made with ❤️ by Deep Study AI, LLC**

**Alpha Tester?** Thank you for helping us build Coach! 🙏
EOF

# Create directory structure
mkdir -p lsp
mkdir -p vscode-extension/src
mkdir -p jetbrains-plugin/src
mkdir -p docs
mkdir -p releases
mkdir -p examples

# Copy files from main repo to alpha repo
echo "📋 Copying Coach files to alpha repository..."

# Note: Adjust these paths based on your actual directory structure
COACH_SOURCE="/Users/patrickroebuck/projects/empathy-framework/examples/coach"

if [ -d "$COACH_SOURCE" ]; then
    echo "  Copying LSP server..."
    cp -r "$COACH_SOURCE/lsp/"* lsp/ 2>/dev/null || echo "  (LSP files not found, skipping)"

    echo "  Copying VS Code extension..."
    cp -r "$COACH_SOURCE/vscode-extension/"* vscode-extension/ 2>/dev/null || echo "  (VS Code files not found, skipping)"

    echo "  Copying JetBrains plugin..."
    cp -r "$COACH_SOURCE/jetbrains-plugin/"* jetbrains-plugin/ 2>/dev/null || echo "  (JetBrains files not found, skipping)"
else
    echo "⚠️  Source directory not found: $COACH_SOURCE"
    echo "  You'll need to manually copy files after this script completes."
fi

# Create placeholder docs
echo "📄 Creating documentation templates..."

cat > docs/INSTALLATION.md << 'EOF'
# Installation Guide

(To be written - see main README.md for now)
EOF

cat > docs/USER_MANUAL.md << 'EOF'
# User Manual

(To be written)
EOF

cat > docs/WIZARDS.md << 'EOF'
# 16 Wizards Overview

(To be written)
EOF

cat > docs/CUSTOM_WIZARDS.md << 'EOF'
# Creating Custom Wizards

(To be written - will be covered in Nov 15 workshop)
EOF

cat > docs/TROUBLESHOOTING.md << 'EOF'
# Troubleshooting Guide

## Common Issues

### LSP Server Won't Start

**Symptoms**: Extension shows "Coach Language Server not connected"

**Solutions**:
1. Check Python version: `python3 --version` (must be 3.12+)
2. Check LSP server manually: `python -m lsp.server --version`
3. Check IDE logs for errors
4. Restart IDE

### Wizards Not Responding

**Symptoms**: Commands hang or timeout

**Solutions**:
1. Check LLM API key is set correctly
2. Check network connection
3. Try a smaller file first (LSP may struggle with 10K+ line files)
4. Clear cache and restart

(More to be added based on alpha feedback)
EOF

cat > docs/BUG_REPORT.md << 'EOF'
# Bug Report Template

**Severity**: [Critical/High/Medium/Low]

**IDE**: [VS Code 1.85 / IntelliJ IDEA 2024.1 / PyCharm / etc.]

**OS**: [macOS 14.0 / Windows 11 / Ubuntu 22.04]

**Python Version**: [3.12.1]

**Steps to Reproduce**:
1.
2.
3.

**Expected Behavior**:


**Actual Behavior**:


**Logs**:
```
(Paste logs here)
```

**Screenshots**:
(Attach screenshots)

**Additional Context**:

EOF

cat > docs/FEATURE_REQUEST.md << 'EOF'
# Feature Request Template

**Feature Name**:

**Use Case**:
(Why do you need this? What problem does it solve?)

**Current Workaround**:
(How do you solve this today, if at all?)

**Proposed Solution**:
(What should Coach do?)

**Priority**:
[ ] Nice-to-have
[ ] Important
[ ] Blocker (can't use Coach without this)

**Additional Context**:

EOF

# Create initial commit
echo "📝 Creating initial commit..."
git add .
git commit -m "Initial alpha repository setup

- Project structure
- Documentation templates
- README with alpha testing info
- .gitignore for Python, Node.js, Kotlin
"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push -u origin main

echo ""
echo "✅ Repository setup complete!"
echo ""
echo "📍 Next steps:"
echo "   1. Visit: https://github.com/$ORG_NAME/$REPO_NAME"
echo "   2. Copy Coach files to $TEMP_DIR if not already done"
echo "   3. Update docs/ with actual content"
echo "   4. Create first release (see releases/ directory)"
echo "   5. Invite alpha testers (Settings → Collaborators)"
echo ""
echo "🔗 Repository: https://github.com/$ORG_NAME/$REPO_NAME"
echo "📂 Local copy: $TEMP_DIR"
echo ""
echo "💡 To invite testers:"
echo "   gh repo collaborators add USERNAME -R $ORG_NAME/$REPO_NAME --permission push"
echo ""
