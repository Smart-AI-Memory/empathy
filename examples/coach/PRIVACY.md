# Privacy Policy for Coach

**Last Updated: January 2025**

## Overview

Coach is an AI-powered code analysis tool designed to help developers write better code. We are committed to protecting your privacy and being transparent about data handling.

## Data We Collect

### Code Analysis Data (Optional)
- **What**: Code snippets sent for analysis
- **Why**: To provide AI-powered code analysis and recommendations
- **Where**: Processed by configured LLM provider (OpenAI, Anthropic, or local)
- **Retention**: Not stored by Coach; subject to LLM provider's policy

### Usage Telemetry (Optional, Opt-In)
- **What**: Feature usage statistics, error reports
- **Why**: To improve Coach and fix bugs
- **Where**: Anonymous data stored securely
- **Retention**: 90 days

### Configuration Data (Local Only)
- **What**: Settings, preferences, enabled wizards
- **Why**: To remember your preferences
- **Where**: Stored locally on your machine
- **Retention**: Until you uninstall

## Data We DO NOT Collect

❌ Personal identifying information
❌ Full source code files (only snippets you choose to analyze)
❌ Git history or commit messages
❌ API keys or credentials (stored locally encrypted)
❌ File system contents beyond analyzed code

## Your Choices

### Disable Telemetry
```
VS Code: Settings → Coach → Enable Telemetry → Off
JetBrains: Settings → Tools → Coach → Enable Telemetry → Uncheck
```

### Use Local LLM
```
Settings → Coach → API Provider → "local"
```
This processes all code locally without sending to external services.

### Clear Cache
```
Command: "Coach: Clear Results"
```

## Third-Party Services

If you use cloud LLM providers:

### OpenAI
- **Privacy Policy**: https://openai.com/privacy
- **Data Handling**: Code sent to OpenAI API
- **Retention**: Per OpenAI's policy (30 days as of Jan 2025)

### Anthropic (Claude)
- **Privacy Policy**: https://www.anthropic.com/privacy
- **Data Handling**: Code sent to Anthropic API
- **Retention**: Per Anthropic's policy

## Security

- API keys stored encrypted in IDE secure storage
- HTTPS for all network communication
- No persistent storage of analyzed code
- Local-first architecture

## GDPR Compliance

For EU users:
- **Right to Access**: Request your data via email
- **Right to Deletion**: Uninstall extension; telemetry auto-deleted after 90 days
- **Right to Portability**: Export settings from IDE
- **Legal Basis**: Legitimate interest & consent

## Children's Privacy

Coach is not intended for users under 13. We do not knowingly collect data from children.

## Changes to This Policy

We will notify users of material changes via:
- Extension update notes
- Email (if subscribed)
- Website announcement

## Contact

Privacy questions: patrick.roebuck@deepstudyai.com
Data deletion requests: patrick.roebuck@deepstudyai.com

## Your Rights

You have the right to:
- Know what data we collect
- Access your data
- Delete your data
- Opt out of telemetry
- Use Coach entirely offline

---

**Coach is committed to privacy-first development. When in doubt, we don't collect it.**
