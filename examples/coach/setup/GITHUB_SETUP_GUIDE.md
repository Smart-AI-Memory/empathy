# GitHub Repository Setup Guide
## Coach Alpha Testing - Step-by-Step Instructions

---

## Prerequisites

Before starting, ensure you have:
- [ ] GitHub account with organization or personal account
- [ ] GitHub CLI installed (`brew install gh` on Mac)
- [ ] Git installed and configured
- [ ] Admin access to create repositories

---

## Option 1: Automated Setup (Recommended)

### Step 1: Run the Setup Script

```bash
cd /Users/patrickroebuck/projects/empathy-framework/examples/coach/setup
./create_github_repo.sh
```

The script will:
1. ✅ Create private repository `deepstudyai/coach-alpha`
2. ✅ Set up directory structure
3. ✅ Create README, .gitignore, and documentation templates
4. ✅ Copy Coach files from main repository
5. ✅ Make initial commit and push

### Step 2: Verify Repository

Visit: https://github.com/deepstudyai/coach-alpha

You should see:
- README with alpha testing info
- Directory structure (lsp/, vscode-extension/, jetbrains-plugin/, docs/)
- Documentation templates

### Step 3: Customize

1. **Update organization name** if not "deepstudyai":
   ```bash
   # Edit the script
   nano create_github_repo.sh
   # Change: ORG_NAME="deepstudyai" to your org
   ```

2. **Add actual documentation**:
   ```bash
   cd /tmp/coach-alpha/docs
   # Edit each .md file with real content
   ```

3. **Create first release** (see below)

---

## Option 2: Manual Setup

If you prefer to set up manually or the script doesn't work:

### Step 1: Create Repository

1. Go to https://github.com/new
2. Fill in:
   - **Repository name**: `coach-alpha`
   - **Description**: "Coach IDE Integration - Private Alpha Testing (Nov 1-29, 2025)"
   - **Visibility**: ✅ Private
   - **Initialize**: ✅ Add a README (we'll replace it)
   - **Add .gitignore**: Python
   - ❌ Don't add license (proprietary for now)
3. Click "Create repository"

### Step 2: Clone Repository

```bash
git clone https://github.com/YOUR-ORG/coach-alpha.git
cd coach-alpha
```

### Step 3: Set Up Structure

```bash
# Create directories
mkdir -p lsp vscode-extension/src jetbrains-plugin/src docs releases examples

# Copy Coach files
cp -r /path/to/empathy-framework/examples/coach/lsp/* lsp/
cp -r /path/to/empathy-framework/examples/coach/vscode-extension/* vscode-extension/
cp -r /path/to/empathy-framework/examples/coach/jetbrains-plugin/* jetbrains-plugin/
```

### Step 4: Create README

Copy the README content from the automated script or create your own with:
- Alpha testing overview
- Installation instructions
- Documentation links
- Bug reporting guidelines
- Communication channels (Discord, email)

### Step 5: Create .gitignore

```bash
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
.venv/
.pytest_cache/

# Node.js
node_modules/
*.vsix

# JetBrains
.gradle/
build/
.idea/

# Secrets
.env
*.key

# OS
.DS_Store
EOF
```

### Step 6: Commit and Push

```bash
git add .
git commit -m "Initial alpha repository setup"
git push
```

---

## Step 4: Create First Release

### Option A: Using GitHub CLI

```bash
# Build VS Code extension
cd vscode-extension
npm install
npm run package  # Creates .vsix file

# Build JetBrains plugin
cd ../jetbrains-plugin
./gradlew buildPlugin  # Creates .zip in build/distributions/

# Create release
cd ..
gh release create v1.0.0-alpha.1 \
  --title "Alpha Release 1 - Initial Launch" \
  --notes "Initial alpha testing release. See README for installation." \
  --prerelease \
  vscode-extension/coach-alpha-1.0.0.vsix \
  jetbrains-plugin/build/distributions/coach-1.0.0.zip
```

### Option B: Using GitHub Web Interface

1. Go to repository → Releases → Create a new release
2. Click "Choose a tag" → Enter `v1.0.0-alpha.1` → Create new tag
3. Release title: "Alpha Release 1 - Initial Launch"
4. Description:
   ```markdown
   ## Initial Alpha Testing Release

   **Release Date**: November 1, 2025
   **Target**: Alpha testers only (50 participants)

   ### What's Included
   - VS Code extension (VSIX)
   - JetBrains plugin (ZIP)
   - All 16 wizards
   - LSP server
   - Documentation

   ### Installation
   See [Installation Guide](https://github.com/deepstudyai/coach-alpha#-quick-start)

   ### Known Issues
   - LSP server may crash on files >10K lines
   - Multi-wizard reviews can take 1-2 seconds
   - See GitHub Issues for full list

   ### Feedback
   - Report bugs: GitHub Issues
   - Feature requests: GitHub Issues
   - Questions: Discord #general-help
   ```
5. Check ✅ "This is a pre-release"
6. Upload files:
   - coach-alpha-1.0.0.vsix
   - coach-jetbrains-1.0.0.zip
7. Click "Publish release"

---

## Step 5: Configure Repository Settings

### 5.1 General Settings

Go to Settings → General:

**Features**:
- ✅ Issues
- ❌ Wikis (use docs/ instead)
- ❌ Sponsorships
- ❌ Projects (not needed for alpha)
- ❌ Preserve this repository (not yet)
- ✅ Discussions (optional, if you want forum-style discussions)

**Pull Requests**:
- ❌ Allow merge commits (alpha doesn't need PRs)
- ❌ Allow squash merging
- ❌ Allow rebase merging
- ✅ Always suggest updating pull request branches
- ✅ Automatically delete head branches

**Archives**:
- ❌ (not needed yet)

### 5.2 Collaborators & Teams

Go to Settings → Collaborators:

**Invite Alpha Testers** (do this after they accept alpha program):

```bash
# Using GitHub CLI (easier for 50 testers)
gh repo collaborators add USERNAME -R YOUR-ORG/coach-alpha --permission push

# Example for multiple testers
cat alpha_testers.txt | while read username; do
  gh repo collaborators add "$username" -R YOUR-ORG/coach-alpha --permission push
  echo "✅ Invited $username"
done
```

**Permissions**:
- **Admin**: You (founder) + core developers
- **Write**: All 50 alpha testers
- **Read**: Any stakeholders who want to observe

### 5.3 Branches

Go to Settings → Branches:

**Default branch**: `main`

**Branch protection rules** (recommended):
- ❌ Don't enable for alpha (too restrictive)
- Just push directly to main during alpha
- Enable after public launch

### 5.4 Issue Templates

Create `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Report a bug in Coach alpha
title: '[BUG] '
labels: bug
assignees: ''
---

**Severity**: [Critical/High/Medium/Low]

**IDE**: [VS Code 1.85 / IntelliJ IDEA 2024.1 / etc.]

**OS**: [macOS 14 / Windows 11 / Ubuntu 22.04]

**Python Version**: [3.12.1]

## Steps to Reproduce
1.
2.
3.

## Expected Behavior


## Actual Behavior


## Logs
```
(Paste logs here)
```

## Screenshots
(Attach screenshots)

## Additional Context

```

Create `.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature Request
about: Suggest a feature for Coach
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

**Feature Name**:

**Use Case**:
(Why do you need this? What problem does it solve?)

**Current Workaround**:
(How do you solve this today?)

**Proposed Solution**:
(What should Coach do?)

**Priority**:
- [ ] Nice-to-have
- [ ] Important
- [ ] Blocker

**Additional Context**:

```

### 5.5 Labels

Go to Issues → Labels → New label:

**Priority Labels**:
- 🔴 `critical` (red) - Blocks usage
- 🟡 `high` (yellow) - Major feature broken
- 🔵 `medium` (blue) - Annoying but workaround exists
- 🟢 `low` (green) - Minor polish

**Component Labels**:
- `lsp-server` (purple)
- `vscode` (blue)
- `jetbrains` (orange)
- `wizard` (pink)
- `docs` (gray)

**Status Labels**:
- `duplicate` (gray)
- `wontfix` (gray)
- `investigating` (yellow)
- `fixed` (green)

**Type Labels**:
- `bug` (red)
- `enhancement` (blue)
- `documentation` (gray)
- `question` (purple)

### 5.6 Notifications

Go to Settings → Notifications:

**Watch settings** (for you and developers):
- ✅ All activity (so you see every issue/comment)

**For alpha testers**:
- They should "Watch" the repo to get notifications

---

## Step 6: GitHub Integration with Discord

### 6.1 Install GitHub Bot in Discord

1. Go to Discord server
2. Server Settings → Integrations → GitHub
3. Click "Add to Discord"
4. Authorize GitHub app
5. Select channels for notifications:
   - `#bugs` → Post when issues labeled "bug" are closed
   - `#testing-priorities` → Post when releases are published

### 6.2 Configure Webhooks

In GitHub: Settings → Webhooks → Add webhook

**Payload URL**: (Get from Discord channel settings → Integrations → Webhooks)

**Content type**: `application/json`

**Events**:
- ✅ Issues
- ✅ Issue comments
- ✅ Releases
- ❌ Push events (too noisy)
- ❌ Pull requests (not using PRs in alpha)

**Active**: ✅

---

## Step 7: Invite Alpha Testers

### 7.1 Prepare Invitation Email

```
Subject: 🎉 You're in! Coach Alpha Testing - Access Instructions

Hi [Name],

Congratulations! You've been selected as one of 50 alpha testers for Coach, our AI development assistant with Level 4 Anticipatory Empathy.

📅 Alpha Testing Dates: November 1-29, 2025

🔗 Access:
1. GitHub Repository (private): https://github.com/deepstudyai/coach-alpha
   - You should have received a collaborator invitation (check your email)
   - Accept the invitation to gain access

2. Discord Server (private): [INVITE LINK - see below]
   - Join for real-time support, discussions, and office hours
   - Introduce yourself in #introductions

📚 Getting Started:
1. Read the README: https://github.com/deepstudyai/coach-alpha#readme
2. Follow installation guide in Discord #installation-guide
3. Start testing and report bugs!

⏰ Important Dates:
- Nov 1: Alpha kicks off, install and verify
- Nov 8: Week 2 intensive testing begins
- Nov 15: Custom wizard workshop (4pm PT, Discord voice)
- Nov 22: Final week of testing
- Nov 29: Alpha concludes, final feedback survey

💬 Communication:
- Discord: Real-time help and discussions
- GitHub Issues: Bug reports and feature requests
- Email: alpha@deepstudyai.com for private matters

🎁 Your Rewards:
- Free Pro Tier for 1 year ($299 value)
- Lifetime 50% discount ($149/year forever)
- Priority support for life
- Early access to all future features

⚠️ Remember:
- You signed an NDA - no public sharing until Dec 15
- Report security issues to security@deepstudyai.com
- We expect 2-4 hours/week of testing

Thank you for joining us on this journey! Let's build something amazing together.

Questions? Reply to this email or ask in Discord.

Best regards,
[Your Name]
Deep Study AI, LLC

---

Discord Invite: [UNIQUE INVITE LINK]
GitHub Repository: https://github.com/deepstudyai/coach-alpha
```

### 7.2 Send Invitations

**GitHub Collaborator Invitations**:
```bash
# Create file with tester usernames (one per line)
cat > alpha_testers.txt << 'EOF'
alice_codes
bob_dev
carol_engineer
...
EOF

# Invite all testers
cat alpha_testers.txt | while read username; do
  gh repo collaborators add "$username" -R deepstudyai/coach-alpha --permission push
  echo "✅ Invited $username"
  sleep 1  # Rate limit protection
done
```

**Discord Invitations**:
1. Create unique invite link in Discord
2. Settings → Invites → Create Invite
3. Max uses: 50
4. Expires: Never
5. Copy link and include in email

**Email Invitations**:
1. Use your email client or service (Gmail, SendGrid, etc.)
2. Personalize each email (replace [Name] with actual name)
3. Track who has:
   - ✅ Accepted GitHub invite
   - ✅ Joined Discord
   - ✅ Introduced themselves
   - ✅ Completed installation

---

## Step 8: Monitor and Maintain

### Daily Tasks (Week 1)
- [ ] Check GitHub Issues (respond within 24 hours)
- [ ] Monitor Discord #general-help (respond within 4 hours)
- [ ] Track installation progress (how many testers have installed?)
- [ ] Fix critical bugs immediately

### Weekly Tasks
- [ ] Monday: Post testing priorities in Discord
- [ ] Tuesday: Hold office hours (Discord voice, 1 hour)
- [ ] Friday: Weekly recap (what was fixed, what's coming)
- [ ] Sunday: Update analytics (bugs filed, fixed, active testers)

### GitHub Maintenance
- [ ] Triage new issues (add labels, assign severity)
- [ ] Close fixed issues with comment linking to release
- [ ] Update README when things change
- [ ] Create new releases when major bugs are fixed

---

## Troubleshooting

### Issue: Script fails with "gh: command not found"

**Solution**:
```bash
# Install GitHub CLI
brew install gh  # Mac
# Or visit: https://cli.github.com/

# Authenticate
gh auth login
```

### Issue: "Permission denied" when pushing

**Solution**:
```bash
# Check authentication
gh auth status

# Re-authenticate if needed
gh auth login

# Verify remote
git remote -v
```

### Issue: Collaborator invitations not working

**Solution**:
1. Check you have admin access to repository
2. Verify username is correct (case-sensitive)
3. Check user hasn't blocked invitations in their GitHub settings
4. Try inviting via web interface: Settings → Collaborators → Add people

### Issue: Too many files to copy manually

**Solution**: Use the automated script, or:
```bash
# Copy entire directory
cp -r /path/to/source/* /path/to/destination/

# Or use rsync
rsync -av --exclude='.git' /path/to/source/ /path/to/destination/
```

---

## Checklist: Repository Launch Day

**Before Nov 1, 2025**:
- [ ] Repository created and populated
- [ ] README is complete and accurate
- [ ] Documentation templates filled in
- [ ] First release (v1.0.0-alpha.1) published
- [ ] Issue templates configured
- [ ] Labels created
- [ ] 50 collaborators invited
- [ ] GitHub-Discord integration working
- [ ] Invitation emails drafted and ready

**Nov 1, 2025 (Launch Day)**:
- [ ] Send invitation emails to all 50 testers
- [ ] Monitor GitHub invite acceptances
- [ ] Monitor Discord joins
- [ ] Be available in Discord for 4-6 hours (expect lots of questions)
- [ ] Create first issue milestone: "Week 1 Bugs"
- [ ] Post welcome message in Discord #general-chat

---

## Next Steps

After repository is set up:

1. ✅ **Set up Discord server** (see Discord setup guide)
2. **Post recruitment** (social media, developer communities)
3. **Prepare for launch day** (Nov 1)
4. **Start Phase 1 development** (LSP foundation)

---

## Resources

- **GitHub CLI Docs**: https://cli.github.com/manual/
- **GitHub Repo Settings**: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features
- **Issue Templates**: https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests
- **Webhooks**: https://docs.github.com/en/developers/webhooks-and-events/webhooks

---

**Document Version**: 1.0
**Last Updated**: 2025-10-15
**Created by**: Claude (Coach AI)
