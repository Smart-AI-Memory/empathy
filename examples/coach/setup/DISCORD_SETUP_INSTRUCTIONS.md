# Discord Server Setup - Step-by-Step Instructions
## Coach Alpha Testing Server

**Estimated Time**: 60-90 minutes
**Difficulty**: Intermediate

---

## Prerequisites

- [ ] Discord account (https://discord.com/)
- [ ] Desktop Discord app installed (recommended over web)
- [ ] Admin/owner access to create servers
- [ ] Server icon/logo ready (optional but recommended)

---

## Part 1: Create Server (5 minutes)

### Step 1: Create New Server

1. Open Discord
2. Click `+` button on left sidebar (server list)
3. Click "Create My Own"
4. Select "For a club or community"
5. Server name: **Coach AI - Alpha Testing**
6. Upload server icon (if you have one)
7. Click "Create"

### Step 2: Server Settings

1. Right-click server name → Server Settings
2. **Overview**:
   - Description: "AI development assistant with Level 4 Anticipatory Empathy. Built on LangChain with 16 specialized wizards."
   - Server icon: Upload if not already done
3. **Verification Level**: Medium (recommended)
4. **Default Notification Settings**: Only @mentions
5. **Explicit Media Content Filter**: Scan media from all members
6. Click "Save Changes"

---

## Part 2: Create Roles (10 minutes)

### Step 1: Create Role Structure

Settings → Roles → Create Role

**Create these roles in order**:

#### 1. Founder
- **Name**: Founder
- **Color**: #FFD700 (gold)
- **Permissions**: ✅ Administrator
- **Display role members separately**: ✅ Yes
- **Allow anyone to @mention this role**: ✅ Yes

#### 2. Developers
- **Name**: Developers
- **Color**: #5865F2 (blurple blue)
- **Permissions**:
  - ✅ Manage Channels
  - ✅ Manage Messages
  - ✅ Manage Threads
  - ✅ Mention @everyone, @here, and All Roles
  - ✅ Moderate Members
- **Display role members separately**: ✅ Yes
- **Allow anyone to @mention this role**: ✅ Yes

#### 3. Alpha Testers
- **Name**: Alpha Testers
- **Color**: #57F287 (green)
- **Permissions**:
  - ✅ Send Messages
  - ✅ Create Public Threads
  - ✅ Send Messages in Threads
  - ✅ Embed Links
  - ✅ Attach Files
  - ✅ Add Reactions
  - ✅ Use External Emojis
- **Display role members separately**: ✅ Yes
- **Allow anyone to @mention this role**: ✅ Yes

#### 4. VS Code Testers
- **Name**: VS Code Testers
- **Color**: #007ACC (VS Code blue)
- **Permissions**: None (just for tagging)
- **Display role members separately**: ❌ No
- **Allow anyone to @mention this role**: ✅ Yes

#### 5. JetBrains Testers
- **Name**: JetBrains Testers
- **Color**: #FF6F00 (JetBrains orange)
- **Permissions**: None (just for tagging)
- **Display role members separately**: ❌ No
- **Allow anyone to @mention this role**: ✅ Yes

#### 6. Wizard Developers
- **Name**: Wizard Developers
- **Color**: #9B59B6 (purple)
- **Permissions**: None (just for tagging)
- **Display role members separately**: ❌ No
- **Allow anyone to @mention this role**: ✅ Yes

#### 7. Lurkers
- **Name**: Lurkers
- **Color**: #95A5A6 (gray)
- **Permissions**: ✅ View Channels only
- **Display role members separately**: ❌ No
- **Allow anyone to @mention this role**: ❌ No

### Step 2: Assign Roles

1. Right-click your name in member list → Manage → Add Role → Founder
2. Add other team members as Developers

---

## Part 3: Create Channels (30 minutes)

### Category 1: INFORMATION & ONBOARDING

**Create Category**: Right-click channel area → Create Category → "INFORMATION & ONBOARDING"

**Channel: 📜welcome** (text)
1. Create channel → Text → "📜welcome"
2. Edit Channel → Permissions → Advanced Permissions:
   - @everyone: ✅ View Channel
   - Alpha Testers: ✅ View Channel
   - Developers: ✅ View Channel, ✅ Send Messages, ✅ Manage Messages
3. Topic: "Welcome to Coach Alpha Testing! Start here 👋"
4. Post welcome message (see below)

**Channel: 📋rules** (text)
1. Create channel → Text → "📋rules"
2. Permissions: Same as #welcome
3. Topic: "Code of conduct and NDA - Please read carefully"
4. Post rules (see below)

**Channel: 📖installation-guide** (text)
1. Create channel → Text → "📖installation-guide"
2. Permissions:
   - @everyone: ✅ View Channel
   - Alpha Testers: ✅ View Channel, ✅ Create Public Threads
   - Developers: All permissions
3. Topic: "Step-by-step installation for VS Code and JetBrains"
4. Post installation guide (see below)

**Channel: 📚documentation** (text)
1. Create channel → Text → "📚documentation"
2. Permissions: Same as #rules
3. Topic: "All documentation links in one place"
4. Post documentation links (see below)

### Category 2: GENERAL

**Create Category**: "GENERAL"

**Channel: 👋introductions** (text)
1. Create channel → Text → "👋introductions"
2. Permissions: Alpha Testers can send messages
3. Topic: "Introduce yourself to the team!"
4. Post pinned message with template

**Channel: 💬general-chat** (text)
1. Create channel → Text → "💬general-chat"
2. Permissions: Alpha Testers can send messages
3. Topic: "Casual conversation, off-topic chat"

**Channel: 🎉wins** (text)
1. Create channel → Text → "🎉wins"
2. Permissions: Alpha Testers can send messages
3. Topic: "Celebrate your successes! Coach helped you? Share it here 🚀"
4. Enable auto-reactions: 🎉, 🚀, ✨ (requires bot)

### Category 3: TESTING

**Create Category**: "TESTING"

**Channel: 🐛bugs** (forum)
1. Create channel → **Forum** → "🐛bugs"
2. Permissions:
   - Alpha Testers: ✅ View, ✅ Send Messages, ✅ Create Threads
   - Developers: All permissions
3. Topic: "Bug reports - Use template, each bug is a thread"
4. Forum Settings:
   - Default reaction: 👍
   - Enable tags (see below)

**Forum Tags for #bugs**:
- 🔴 Critical (red)
- 🟡 High (yellow)
- 🔵 Medium (blue)
- 🟢 Low (green)
- ✅ Fixed (green, moderators only)
- ❌ Won't Fix (red, moderators only)
- VS Code (blue)
- JetBrains (orange)
- LSP (purple)

**Channel: ✨feature-requests** (forum)
1. Create channel → **Forum** → "✨feature-requests"
2. Permissions: Same as #bugs
3. Topic: "Feature ideas and suggestions - Vote with 👍"
4. Enable tags:
   - Nice-to-have (green)
   - Important (yellow)
   - Blocker (red)
   - Under Review (blue, moderators only)
   - Planned (green, moderators only)
   - Won't Implement (gray, moderators only)

**Channel: 📊testing-priorities** (text)
1. Create channel → Text → "📊testing-priorities"
2. Permissions: Read-only for testers, Developers can post
3. Topic: "Weekly testing priorities - What we need you to focus on"

### Category 4: SUPPORT

**Create Category**: "SUPPORT"

**Channel: ❓general-help** (text)
1. Create channel → Text → "❓general-help"
2. Enable threads: ✅ Auto-create thread on message
3. Topic: "Questions and troubleshooting - Testers help each other!"

**Channel: 💻vs-code-help** (text)
1. Create channel → Text → "💻vs-code-help"
2. Enable threads
3. Topic: "VS Code extension issues and questions"

**Channel: 🖥️jetbrains-help** (text)
1. Create channel → Text → "🖥️jetbrains-help"
2. Enable threads
3. Topic: "JetBrains plugin issues and questions"

**Channel: 🧙custom-wizards** (text)
1. Create channel → Text → "🧙custom-wizards"
2. Permissions: Alpha Testers can send messages
3. Topic: "Creating custom wizards with LangChain - Share your creations!"

### Category 5: EVENTS

**Create Category**: "EVENTS"

**Channel: 📆schedule** (text)
1. Create channel → Text → "📆schedule"
2. Permissions: Read-only for testers
3. Topic: "Weekly office hours, workshops, important dates"
4. Post schedule (see below)

**Channel: 🎥office-hours** (voice)
1. Create channel → **Voice** → "🎥office-hours"
2. User limit: 50
3. Permissions: Everyone can connect and speak

### Category 6: INTERNAL (Admin Only)

**Create Category**: "INTERNAL (Admin Only)"
**Category Permissions**: Only Developers and Founder can view

**Channel: 🔒admin-chat** (text)
1. Create channel → Text → "🔒admin-chat"
2. Permissions: Only Developers and Founder
3. Topic: "Admin coordination - Private"

**Channel: 📈analytics** (text)
1. Create channel → Text → "📈analytics"
2. Permissions: Only Developers and Founder
3. Topic: "Metrics tracking and dashboards"

---

## Part 4: Post Initial Messages (20 minutes)

### #📜welcome

```
👋 **Welcome to Coach Alpha Testing!**

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

Pin this message.

### #📋rules

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

Pin this message.

### #📖installation-guide

Copy the installation guide from [DISCORD_SETUP_GUIDE.md](DISCORD_SETUP_GUIDE.md) section on installation.

Pin this message.

### #📚documentation

```
📚 **Documentation**

**User Guides**:
- [16 Wizards Overview](https://github.com/deepstudyai/coach-alpha/blob/main/docs/WIZARDS.md)
- [Creating Custom Wizards](https://github.com/deepstudyai/coach-alpha/blob/main/docs/CUSTOM_WIZARDS.md)
- [LangChain Integration Guide](https://github.com/deepstudyai/coach-alpha/blob/main/docs/LANGCHAIN.md)
- [Multi-Wizard Collaboration](https://github.com/deepstudyai/coach-alpha/blob/main/docs/MULTI_WIZARD.md)

**Technical Docs**:
- [LSP Protocol Reference](https://github.com/deepstudyai/coach-alpha/blob/main/lsp/README.md)
- [VS Code Extension API](https://github.com/deepstudyai/coach-alpha/blob/main/vscode-extension/README.md)
- [JetBrains Plugin API](https://github.com/deepstudyai/coach-alpha/blob/main/jetbrains-plugin/README.md)

**Templates**:
- [Bug Report Template](https://github.com/deepstudyai/coach-alpha/blob/main/docs/BUG_REPORT.md)
- [Feature Request Template](https://github.com/deepstudyai/coach-alpha/blob/main/docs/FEATURE_REQUEST.md)
- [Custom Wizard Template](https://github.com/deepstudyai/coach-alpha/blob/main/examples/custom_wizard_template.py)

**Video Tutorials**:
(Coming soon - will be posted here)
```

Pin this message.

### #👋introductions

```
👋 **Introduce Yourself!**

Share:
- Your name (or handle)
- Your role (developer, tech lead, etc.)
- Primary language(s) you work in
- IDE you'll be testing (VS Code, IntelliJ, PyCharm, etc.)
- What you're most excited to test
- Fun fact about yourself! 🎉

**Example**:
"Hi! I'm Alex, a senior backend dev working mostly in Python and Go. I'll be testing the VS Code extension. Most excited to try the PerformanceWizard since we've had scaling issues lately. Fun fact: I once debugged a production issue at 3am while on a camping trip 🏕️"
```

Pin this message.

### #🐛bugs

Create a pinned post with bug report template (see DISCORD_SETUP_GUIDE.md).

### #✨feature-requests

Create a pinned post with feature request guidelines.

### #📆schedule

```
📅 **Alpha Testing Schedule**

**Week 1** (Nov 1-7): Onboarding & VS Code Setup
- Nov 1: Alpha launches! Install and verify
- Nov 5: Office hours (Tuesday 3pm PT)

**Week 2** (Nov 8-14): Intensive VS Code Testing
- Focus: Find critical bugs, test all wizards
- Nov 12: Office hours (Tuesday 3pm PT)

**Week 3** (Nov 15-21): JetBrains Plugin Testing
- **Nov 15: Custom Wizard Workshop** (Friday 4pm PT) 🎓
- Nov 19: Office hours (Tuesday 3pm PT)

**Week 4** (Nov 22-29): Final Testing & Feedback
- Focus: Regression testing, polish feedback
- Nov 26: Final office hours (Tuesday 3pm PT)
- Nov 29: Alpha concludes, final survey sent

**Office Hours**: Every Tuesday @ 3pm PT in <#office-hours>
**Workshop**: Friday Nov 15 @ 4pm PT in <#office-hours>

Add to your calendar! 📅
```

Pin this message.

---

## Part 5: Add Bots (15 minutes, optional)

### Bot 1: Welcome Bot (Recommended)

**Carl-bot** (https://carl.gg/)

1. Go to https://carl.gg/ → Add to Discord
2. Select your server
3. Authorize bot
4. Go to Dashboard → Welcome
5. Enable welcome DMs
6. Message:
   ```
   👋 Welcome to Coach Alpha Testing, {user}!

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

### Bot 2: GitHub Integration (Highly Recommended)

1. Go to https://discord.com/application-directory/487431320314576916
2. Add to Discord → Select server
3. Authorize
4. In Discord: Go to #bugs → Integrations → GitHub
5. Link repository: deepstudyai/coach-alpha
6. Configure:
   - Post when issues are closed
   - Post when releases are published

### Bot 3: Reaction Roles (Optional)

**Carl-bot Reaction Roles**:

1. Create message in #introductions:
   ```
   **Select Your Testing Track:**
   💻 = VS Code Tester
   🖥️ = JetBrains Tester
   🧙 = Wizard Developer (custom wizards)
   ```

2. Carl-bot dashboard → Reaction Roles
3. Create reaction role:
   - Channel: #introductions
   - Message ID: (right-click message → Copy ID)
   - Reactions:
     - 💻 → @VS Code Testers
     - 🖥️ → @JetBrains Testers
     - 🧙 → @Wizard Developers

---

## Part 6: Create Server Invite (5 minutes)

### Step 1: Create Invite Link

1. Right-click server name → Invite People
2. Click "Edit invite link"
3. Settings:
   - **Expire after**: Never
   - **Max number of uses**: 50
   - **Grant temporary membership**: ❌ No
4. Click "Generate a New Link"
5. **Copy link** - this is your alpha tester invite!

### Step 2: Test Invite

1. Open incognito/private browser window
2. Paste invite link
3. Verify it works (don't actually join unless testing)
4. Close window

### Step 3: Save Invite

Save invite link securely:
- Add to password manager
- Add to alpha tester invitation email template
- Add to GitHub repo README (in private section)

---

## Part 7: Final Configuration (5 minutes)

### Server Icon

If you haven't already:
1. Server Settings → Upload Server Icon
2. Recommended: Robot/AI icon with empathy theme
3. Or use "Coach" text logo

### Server Banner (Optional, for boosted servers)

1. Server Settings → Upload Server Banner
2. Recommended: Wide banner with "Coach Alpha Testing" text

### Community Settings

Settings → Community:
1. ✅ Enable Community
2. Rules Channel: #rules
3. Community Updates Channel: #general-chat
4. Default Notification Settings: Only @mentions

### Moderation

Settings → Safety Setup:
1. Verification Level: Medium
2. Explicit Media Content Filter: Scan from all members
3. Keep AutoMod enabled (Discord's built-in)

---

## Part 8: Test Everything (10 minutes)

### Checklist

Run through this as a "test user":

1. **Join server** (use alt account or ask someone):
   - [ ] Invite link works
   - [ ] Welcome DM received (if bot enabled)
   - [ ] Can see appropriate channels

2. **Read channels**:
   - [ ] #welcome message is clear
   - [ ] #rules is complete
   - [ ] #installation-guide is helpful

3. **Post in channels**:
   - [ ] Can post in #introductions
   - [ ] Can post in #general-chat
   - [ ] Can create thread in #bugs (forum)

4. **Test permissions**:
   - [ ] Can't post in #rules (read-only)
   - [ ] Can't see #admin-chat (admin only)

5. **Voice**:
   - [ ] Can join #office-hours voice channel

6. **Reactions**:
   - [ ] Auto-reactions work in #wins (if bot enabled)
   - [ ] Reaction roles work (if enabled)

---

## Part 9: Launch Day Checklist

**November 1, 2025 - Day 1**:

- [ ] All 50 alpha testers invited to GitHub (done in advance)
- [ ] Send Discord invite links to all 50 testers (via email)
- [ ] Post launch message in #general-chat:
  ```
  🚀 **Alpha Testing is LIVE!**

  Welcome, alpha testers! Today is Day 1 of our 4-week journey.

  **Today's Goals**:
  1. ✅ Install Coach (VS Code or JetBrains)
  2. ✅ Run health check: `Coach: Health Check`
  3. ✅ Try your first wizard (suggest SecurityWizard or PerformanceWizard)
  4. ✅ Report your first bug or success in <#bugs> or <#wins>

  **Need Help?**
  - Installation issues: <#installation-guide>
  - Questions: <#general-help>
  - Can't wait? Tag @Developers

  Let's go! 🎉
  ```

- [ ] Post Week 1 priorities in #testing-priorities
- [ ] Be online for 4-6 hours to answer questions
- [ ] Monitor #general-help and #bugs closely
- [ ] Welcome each new member in #introductions

---

## Troubleshooting

### Issue: Can't create forum channels

**Solution**: Forum channels require Community Server enabled.
1. Settings → Community → Enable Community
2. Set rules channel and updates channel
3. Try creating forum channel again

### Issue: Permissions not working correctly

**Solution**:
1. Check role hierarchy (Settings → Roles)
2. Higher roles override lower roles
3. Channel-specific permissions override role permissions
4. Use "View Server as Role" to test (right-click role)

### Issue: Bots not responding

**Solution**:
1. Check bot is online (green dot in member list)
2. Verify bot has appropriate permissions
3. Check bot configuration in dashboard
4. Try removing and re-adding bot

### Issue: Invite link not working

**Solution**:
1. Check invite hasn't expired
2. Check max uses hasn't been reached
3. Generate new invite link
4. Check server verification settings aren't blocking joins

---

## Ongoing Maintenance

### Daily (Week 1)
- Monitor #general-help (respond within 4 hours)
- Check #bugs for critical issues
- Welcome new members in #introductions

### Weekly
- **Monday**: Post testing priorities in #testing-priorities
- **Tuesday**: Hold office hours in #office-hours voice (3pm PT)
- **Friday**: Post weekly recap in #general-chat

### As Needed
- Pin important messages
- Update #documentation when docs change
- Create GitHub issues from Discord bug reports
- Post release announcements in #testing-priorities

---

## Resources

- **Discord Server Setup Guide**: https://support.discord.com/hc/en-us/articles/204849977
- **Discord Permissions**: https://support.discord.com/hc/en-us/articles/206141927
- **Forum Channels**: https://support.discord.com/hc/en-us/articles/6208479917079
- **Carl-bot Documentation**: https://docs.carl.gg/

---

## Completion Checklist

Before inviting alpha testers:

- [ ] Server created with correct name
- [ ] 7 roles created with correct colors and permissions
- [ ] 20+ channels created and organized
- [ ] All pinned messages posted
- [ ] Welcome message configured (bot or manual)
- [ ] GitHub integration working (optional)
- [ ] Reaction roles working (optional)
- [ ] Invite link created (50 uses, never expires)
- [ ] Server tested with alt account
- [ ] Launch day message drafted

**Server Status**: ✅ Ready for Alpha Testing Launch

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Created by**: Claude (Coach AI)
