# Coach Alpha Testing - Discord Server Setup Guide

## Server Structure

### 📋 Server Name
**Coach AI - Alpha Testing**

### 🎨 Server Icon
Upload Coach logo (robot/AI icon with empathy theme)

### 📝 Server Description
> AI development assistant with Level 4 Anticipatory Empathy. Built on LangChain with 16 specialized wizards for comprehensive software development support.

---

## Channel Structure

### 📢 INFORMATION & ONBOARDING

#### #📜welcome
**Purpose**: Welcome message and rules
**Permissions**: Read-only for @everyone, Admin posts only

**Welcome Message**:
```
👋 Welcome to Coach Alpha Testing!

Coach is an AI development assistant with **Level 4 Anticipatory Empathy** - it predicts issues 30-90 days before they occur.

🎯 **What we're testing**: VS Code extension + JetBrains plugin
🏗️ **Built on**: LangChain (extensible wizard framework)
🗓️ **Timeline**: 4 weeks (Nov 1 - Nov 29, 2025)

📚 **Getting Started**:
1. Read <#rules>
2. Check <#installation-guide>
3. Introduce yourself in <#introductions>
4. Start testing and report bugs in <#bugs>

💬 **Need help?** Ask in <#general-help>

Let's build something amazing together! 🚀
```

#### #📋rules
**Purpose**: Code of conduct and NDA
**Permissions**: Read-only

**Rules**:
```
📋 **Alpha Testing Rules & NDA**

**1. Confidentiality (NDA)**
🔒 Do NOT share screenshots, videos, or details publicly until public beta (Dec 15, 2025)
🔒 Do NOT discuss Coach on social media, Reddit, Hacker News, etc. until launch
🔒 You may test on your company's code, but do not share Coach-generated outputs publicly

**2. Respect & Collaboration**
🤝 Be kind and respectful to all testers and developers
🤝 Assume positive intent - we're all learning
🤝 Help other testers when you can

**3. Constructive Feedback**
✅ Be specific in bug reports (screenshots, logs, steps to reproduce)
✅ Explain the "why" behind feature requests
✅ If something is confusing, that's a bug - report it!

**4. Time Commitment**
⏰ 2-4 hours/week minimum
⏰ Respond to @mentions within 48 hours
⏰ If you need to drop out, let us know ASAP

**5. Security**
🛡️ If you find a security vulnerability, report privately to security@deepstudyai.com
🛡️ Do NOT post security issues in public channels

**Violation of these rules may result in removal from the alpha program.**

By participating, you agree to these terms.
```

#### #📖installation-guide
**Purpose**: Setup instructions
**Permissions**: Read-only (Admins can post, testers can react/thread)

**Content**:
```
📖 **Installation Guide**

## Prerequisites
- ✅ Python 3.12+ installed (`python3 --version`)
- ✅ VS Code 1.85+ OR JetBrains IDE 2024.1+
- ✅ Git (optional but recommended)

## Step 1: Install Coach LSP Server
\`\`\`bash
# Clone repository (private alpha repo)
git clone https://github.com/deepstudyai/coach-alpha.git
cd coach-alpha/examples/coach/lsp

# Install dependencies
pip install -r requirements.txt

# Test LSP server
python -m lsp.server --version
# Should output: Coach LSP Server v1.0.0
\`\`\`

## Step 2A: VS Code Extension
\`\`\`bash
# Install from VSIX
code --install-extension coach-alpha-1.0.0.vsix

# Restart VS Code
# You should see "Coach" icon in sidebar
\`\`\`

## Step 2B: JetBrains Plugin
1. Download `coach-jetbrains-1.0.0.zip`
2. Open IDE Settings → Plugins
3. Click ⚙️ → Install Plugin from Disk
4. Select downloaded ZIP
5. Restart IDE

## Step 3: Verify Installation
### VS Code:
- Open Command Palette (Cmd+Shift+P)
- Type "Coach: Health Check"
- Should see "✅ All 16 wizards loaded"

### JetBrains:
- Open Tool Window: View → Tool Windows → Coach
- Should see wizard list

## Step 4: Configuration
### Set LLM API Key (required)
VS Code: Settings → Coach → LLM API Key
JetBrains: Settings → Tools → Coach → LLM API Key

Supported providers:
- OpenAI (recommended for alpha)
- Anthropic
- Local models (advanced)

## Troubleshooting
If installation fails, post in <#general-help> with:
- Your OS (Mac/Windows/Linux)
- Python version (`python3 --version`)
- IDE and version
- Error message (screenshot or copy-paste)

**Need help?** Tag @Admins or @Developers
```

#### #📚documentation
**Purpose**: Links to all docs
**Permissions**: Read-only

**Content**:
```
📚 **Documentation**

**User Guides**:
- [16 Wizards Overview](link)
- [Creating Custom Wizards](link)
- [LangChain Integration Guide](link)
- [Multi-Wizard Collaboration](link)

**Technical Docs**:
- [LSP Protocol Reference](link)
- [Extension API](link)
- [Plugin API](link)

**Video Tutorials**:
- [Quick Start (5 min)](link)
- [VS Code Deep Dive (15 min)](link)
- [JetBrains Deep Dive (15 min)](link)
- [Custom Wizard Development (30 min)](link)

**Templates**:
- [Bug Report Template](link)
- [Feature Request Template](link)
- [Custom Wizard Template](link)
```

---

### 💬 GENERAL

#### #👋introductions
**Purpose**: Testers introduce themselves

**Pinned Message**:
```
👋 **Introduce Yourself!**

Share:
- Your name (or handle)
- Your role (developer, tech lead, etc.)
- Primary language(s) you work in
- IDE you'll be testing (VS Code, IntelliJ, PyCharm, etc.)
- What you're most excited to test
- Fun fact about yourself! 🎉

Example:
"Hi! I'm Alex, a senior backend dev working mostly in Python and Go. I'll be testing the VS Code extension. Most excited to try the PerformanceWizard since we've had scaling issues lately. Fun fact: I once debugged a production issue at 3am while on a camping trip 🏕️"
```

#### #💬general-chat
**Purpose**: Casual conversation, off-topic

#### #🎉wins
**Purpose**: Celebrate successes
**Auto-react**: 🎉 🚀 ✨

**Pinned Message**:
```
🎉 **Celebrate Your Wins!**

Share when:
- Coach helped you find a real bug
- A wizard prediction came true
- You created a custom wizard that works
- You had an "aha!" moment
- Anything awesome happens!

Let's celebrate progress together! 🚀
```

---

### 🧪 TESTING

#### #🐛bugs
**Purpose**: Bug reports
**Forum Mode**: Enabled (each bug is a thread)

**Pinned Message**:
```
🐛 **Bug Reporting**

**Before posting**:
1. Check if someone already reported it
2. Try to reproduce it 2-3 times
3. Gather logs/screenshots

**Create a new post with**:
- **Title**: Short description (e.g., "LSP crashes on large Python files")
- **Severity**: Critical / High / Medium / Low
- **IDE**: VS Code or JetBrains (which one?)
- **Steps to reproduce**: Numbered list
- **Expected behavior**: What should happen
- **Actual behavior**: What actually happens
- **Logs/Screenshots**: Attach if possible
- **Environment**: OS, Python version, IDE version

**Template** (copy-paste):
\`\`\`
**Severity**: [Critical/High/Medium/Low]
**IDE**: [VS Code 1.85 / IntelliJ IDEA 2024.1 / etc.]
**OS**: [macOS 14.0 / Windows 11 / Ubuntu 22.04]

**Steps to Reproduce**:
1.
2.
3.

**Expected**:
**Actual**:

**Logs**: [paste or attach]
**Screenshots**: [attach]
\`\`\`

We'll triage within 24 hours and add labels:
🔴 Critical (blocks usage)
🟡 High (major feature broken)
🔵 Medium (annoying but workaround exists)
🟢 Low (minor polish)
✅ Fixed
❌ Won't Fix
```

#### #✨feature-requests
**Purpose**: Feature ideas and suggestions
**Forum Mode**: Enabled

**Pinned Message**:
```
✨ **Feature Requests**

**Great feature requests include**:
- **Use case**: Why do you need this?
- **Current workaround**: How do you solve it today?
- **Proposed solution**: What should Coach do?
- **Priority**: Nice-to-have or blocker?

**We'll consider**:
- Alignment with Coach's mission (Level 4 Anticipatory Empathy)
- Feasibility within alpha timeline
- Number of testers requesting it

**Voting**: React with 👍 if you want this feature too!
```

#### #📊testing-priorities
**Purpose**: What we need testers to focus on this week
**Permissions**: Read-only (Admins post)

**Example Weekly Update**:
```
📊 **Week 2 Testing Priorities**

**Focus Areas**:
1. 🔥 **Critical**: Test SecurityWizard on real codebases - does it find actual vulnerabilities?
2. ⚡ **High**: Hover predictions - are they accurate? Useful?
3. 🎯 **Medium**: Multi-wizard collaboration - try "new_api_endpoint" scenario

**Known Issues** (don't report these):
- LSP server sometimes crashes on >10K line files (fix in progress)
- JetBrains plugin has UI glitches on Windows (known)

**This Week's Goal**: 20+ bug reports on SecurityWizard

**Questions?** Ask in <#general-help>
```

---

### 🛠️ SUPPORT

#### #❓general-help
**Purpose**: Questions and troubleshooting
**Auto-thread**: Enabled

#### #💻vs-code-help
**Purpose**: VS Code-specific issues

#### #🖥️jetbrains-help
**Purpose**: JetBrains-specific issues

#### #🧙custom-wizards
**Purpose**: Help creating custom wizards

**Pinned Message**:
```
🧙 **Custom Wizard Development**

**Resources**:
- [Custom Wizard Guide](link)
- [LangChain Patterns](link)
- [Example Wizards](link)

**Workshop**: Nov 15, 2025 (optional, 1 hour)

**Share your wizards here!** We'd love to see what you build.
```

---

### 📅 EVENTS

#### #📆schedule
**Purpose**: Weekly office hours, workshops, deadlines
**Permissions**: Read-only

#### #🎥office-hours
**Purpose**: Voice channel for weekly calls
**Type**: Voice Channel

---

### 👨‍💻 INTERNAL (Admin Only)

#### #🔒admin-chat
**Purpose**: Admin coordination
**Permissions**: Admins only

#### #📈analytics
**Purpose**: Tracking metrics
**Permissions**: Admins only

**Pinned Dashboard**:
```
📈 **Alpha Testing Metrics**

**Testers**: 50 / 50 ✅
**Active Testers**: 45 (90%)
**Bug Reports**: 63
**Feature Requests**: 28
**Custom Wizards Created**: 7

**This Week**:
- Bugs filed: 18
- Bugs fixed: 15
- Avg response time: 14 hours

**Top Contributors**:
1. @Alice - 12 bugs, 5 features
2. @Bob - 10 bugs, 3 wizards
3. @Carol - 8 bugs, excellent feedback

Updated: 2025-11-08
```

---

## Roles & Permissions

### Roles

#### @Founder
**Permissions**: Administrator
**Color**: Gold
**Members**: You

#### @Developers
**Permissions**: Administrator (can manage channels, pins, moderate)
**Color**: Blue
**Members**: Development team

#### @Alpha Testers
**Permissions**:
- Send messages in all tester channels
- Add reactions
- Create threads
- Attach files
- Embed links
**Color**: Green
**Members**: All 50 alpha testers

#### @Lurkers
**Permissions**: Read-only (no posting)
**Use case**: Stakeholders who want to observe

---

## Bots & Integrations

### Suggested Bots

#### 1. **GitHub Integration**
**Purpose**: Auto-post bug fixes to #bugs
**Setup**: Link to `coach-alpha` repository
**Config**: Post when issues are closed

#### 2. **Welcome Bot**
**Purpose**: DM new members with getting started guide
**Message**:
```
👋 Welcome to Coach Alpha Testing, {username}!

🎯 **Quick Start**:
1. Read <#rules> (NDA)
2. Follow <#installation-guide>
3. Introduce yourself in <#introductions>

📚 **Resources**:
- <#documentation> has all guides
- <#general-help> for questions

💬 **Stay Active**:
- Weekly office hours: Tuesdays 3pm PT
- Testing priorities posted in <#testing-priorities>

Questions? Tag @Developers

Let's build something amazing! 🚀
```

#### 3. **Reaction Roles** (optional)
**Purpose**: Self-assign roles
**Setup**:
- React 💻 for @VS-Code-Testers
- React 🖥️ for @JetBrains-Testers
- React 🧙 for @Wizard-Developers (custom wizard creators)

#### 4. **Poll Bot** (optional)
**Purpose**: Weekly satisfaction surveys
**Example**: "Rate this week's testing experience: 1-5 stars"

---

## Moderation Guidelines

### Response Times
- **Critical bugs**: <4 hours
- **General questions**: <24 hours
- **Feature requests**: <1 week (triage)

### Tone
- Friendly, grateful, supportive
- Acknowledge all feedback (even if we can't implement)
- Celebrate wins and contributions

### Conflict Resolution
- DM both parties privately first
- Remind of <#rules>
- Escalate to you if needed

---

## Weekly Cadence

### Monday
- Post week's testing priorities in <#testing-priorities>
- Update <#schedule> with office hours

### Tuesday
- Office hours in #🎥office-hours (3pm PT, 1 hour)
- Record and post summary

### Wednesday
- Mid-week check-in: "How's testing going?" in #💬general-chat

### Friday
- Weekly recap: bugs fixed, features added, thank contributors
- Post in #💬general-chat

### Sunday
- Update <#analytics> with metrics

---

## Onboarding Checklist (for each new tester)

- [ ] Send Discord invite via email
- [ ] Verify they've joined (check member list)
- [ ] Assign @Alpha Testers role
- [ ] DM welcome message (if bot not set up)
- [ ] Check they've introduced themselves in #👋introductions
- [ ] Follow up if no activity within 3 days

---

## Launch Day Checklist

**Before Nov 1**:
- [ ] Create all channels
- [ ] Set up roles and permissions
- [ ] Write pinned messages for each channel
- [ ] Set up Welcome Bot
- [ ] Invite all 50 alpha testers
- [ ] Post in #📜welcome
- [ ] Schedule first office hours

**Nov 1 (Launch Day)**:
- [ ] Post in #💬general-chat: "Alpha testing is live! Start here: <#installation-guide>"
- [ ] Monitor #❓general-help closely (expect lots of questions)
- [ ] Post first week's priorities in #📊testing-priorities
- [ ] Be online for real-time support (first 4-6 hours critical)

---

## Discord Server Invite

**Link**: https://discord.gg/coach-alpha-2025 (create and keep private!)

**Expires**: Never (but limit to 50 uses)

**Share with**: Only accepted alpha testers via email

---

## Questions?

If you need help setting up Discord:
- Discord Server Setup Guide: https://support.discord.com/hc/en-us/articles/204849977
- Roles & Permissions: https://support.discord.com/hc/en-us/articles/206029707

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Created by**: Claude (Coach AI)
