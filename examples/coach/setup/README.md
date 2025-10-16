# Coach Alpha Testing - Setup Directory

**Quick Links**:
- 📋 [Setup Complete Summary](SETUP_COMPLETE.md) - Start here!
- 🐙 [GitHub Setup Guide](GITHUB_SETUP_GUIDE.md)
- 💬 [Discord Setup Instructions](DISCORD_SETUP_INSTRUCTIONS.md)

---

## What's in This Directory

This directory contains everything you need to set up Coach Alpha Testing infrastructure.

### 🚀 Quick Start (Choose Your Path)

#### Path A: Run Automated Script (Recommended)
```bash
# Set up GitHub repository (5 minutes)
./create_github_repo.sh

# Set up Discord manually (60-90 minutes)
# Follow: DISCORD_SETUP_INSTRUCTIONS.md
```

#### Path B: Manual Setup
Follow the detailed guides:
1. [GitHub Setup Guide](GITHUB_SETUP_GUIDE.md) - 30 minutes manual setup
2. [Discord Setup Instructions](DISCORD_SETUP_INSTRUCTIONS.md) - 60-90 minutes

---

## Files in This Directory

### 📜 Scripts

**[create_github_repo.sh](create_github_repo.sh)** (240 lines)
- Automated GitHub repository creation
- Creates `deepstudyai/coach-alpha` private repository
- Sets up directory structure
- Copies Coach files
- Creates README, .gitignore, docs
- Makes initial commit and pushes

**Usage**:
```bash
chmod +x create_github_repo.sh
./create_github_repo.sh
```

---

### 📋 Configuration

**[discord_config.json](discord_config.json)** (250 lines)
- Complete Discord server configuration in JSON format
- 7 roles with permissions and colors
- 20+ channels organized by category
- Forum channel tags
- Bot recommendations
- Permission structure

**Usage**: Reference when creating Discord server manually

---

### 📖 Guides

**[GITHUB_SETUP_GUIDE.md](GITHUB_SETUP_GUIDE.md)** (900 lines)
- **Part 1**: Automated setup (5 minutes)
- **Part 2**: Manual setup (30 minutes)
- **Part 3**: Creating first release
- **Part 4**: Repository configuration
- **Part 5**: Issue templates and labels
- **Part 6**: GitHub-Discord integration
- **Part 7**: Inviting alpha testers
- **Part 8**: Troubleshooting

**When to use**: Setting up GitHub repository for alpha testing

---

**[DISCORD_SETUP_INSTRUCTIONS.md](DISCORD_SETUP_INSTRUCTIONS.md)** (850 lines)
- **Part 1**: Create server (5 min)
- **Part 2**: Create roles (10 min)
- **Part 3**: Create channels (30 min)
- **Part 4**: Post initial messages (20 min)
- **Part 5**: Add bots (15 min, optional)
- **Part 6**: Create invite link (5 min)
- **Part 7**: Final configuration (5 min)
- **Part 8**: Test everything (10 min)
- **Part 9**: Launch day checklist

**When to use**: Setting up Discord server for alpha testing

---

**[SETUP_COMPLETE.md](SETUP_COMPLETE.md)** (350 lines)
- Summary of all setup tasks
- Quick reference for what's been created
- Next steps before launch
- Launch day checklist
- Troubleshooting common issues
- Timeline to launch

**When to use**: Overview and progress tracking

---

## Setup Workflow

### 1️⃣ Preparation (Before you start)

**Prerequisites**:
- [ ] GitHub CLI installed (`brew install gh`)
- [ ] GitHub account with org access
- [ ] Discord account
- [ ] 2-3 hours available time

**Gather**:
- [ ] Alpha tester list (50 names/usernames)
- [ ] Server icon/logo (optional)
- [ ] Email invitation template

---

### 2️⃣ GitHub Repository Setup (5 minutes automated OR 30 minutes manual)

**Automated**:
```bash
./create_github_repo.sh
```

**Manual**: Follow [GITHUB_SETUP_GUIDE.md](GITHUB_SETUP_GUIDE.md)

**Result**: Private repo at https://github.com/deepstudyai/coach-alpha

**Verify**:
- [ ] Repository created
- [ ] Files copied
- [ ] README populated
- [ ] Directory structure correct

---

### 3️⃣ Discord Server Setup (60-90 minutes)

Follow [DISCORD_SETUP_INSTRUCTIONS.md](DISCORD_SETUP_INSTRUCTIONS.md)

**Steps**:
1. Create server and configure settings
2. Create 7 roles with permissions
3. Create 20+ channels
4. Post pinned messages
5. Add bots (optional)
6. Create invite link
7. Test with alt account

**Result**: Fully configured Discord server

**Verify**:
- [ ] All channels created
- [ ] All roles configured
- [ ] Pinned messages posted
- [ ] Invite link created
- [ ] Server tested

---

### 4️⃣ First Release (30 minutes)

Build and publish first alpha release:

```bash
# Build VS Code extension
cd vscode-extension
npm install
npm run package

# Build JetBrains plugin
cd ../jetbrains-plugin
./gradlew buildPlugin

# Create GitHub release
gh release create v1.0.0-alpha.1 \
  --title "Alpha Release 1" \
  --prerelease \
  vscode-extension/coach-alpha-1.0.0.vsix \
  jetbrains-plugin/build/distributions/coach-1.0.0.zip
```

**Verify**:
- [ ] VSIX file created
- [ ] ZIP file created
- [ ] Release published on GitHub
- [ ] Files downloadable

---

### 5️⃣ Invite Testers (2 hours)

**GitHub Collaborators**:
```bash
# Invite all 50 testers
cat alpha_testers.txt | while read username; do
  gh repo collaborators add "$username" -R deepstudyai/coach-alpha --permission push
done
```

**Discord Invites**: Send invite link via email

**Email Invitations**: Use template from GITHUB_SETUP_GUIDE.md

**Verify**:
- [ ] 50 GitHub invitations sent
- [ ] 50 Discord invites sent
- [ ] 50 email invitations sent
- [ ] Track acceptances

---

### 6️⃣ Launch Day (Nov 1, 2025)

See [Launch Day Checklist](SETUP_COMPLETE.md#launch-day-nov-1-2025)

**Morning**:
- [ ] Post launch message in Discord
- [ ] Monitor closely for first 4-6 hours

**During Day**:
- [ ] Welcome new members
- [ ] Answer questions
- [ ] Triage critical bugs

**Evening**:
- [ ] Post recap
- [ ] Update analytics

---

## File Size Reference

| File | Lines | Purpose |
|------|-------|---------|
| create_github_repo.sh | 240 | GitHub automation |
| discord_config.json | 250 | Discord configuration |
| GITHUB_SETUP_GUIDE.md | 900 | GitHub instructions |
| DISCORD_SETUP_INSTRUCTIONS.md | 850 | Discord instructions |
| SETUP_COMPLETE.md | 350 | Summary & status |
| **Total** | **2,590** | **Complete setup** |

---

## Estimated Time

### Automated Path
- GitHub setup (script): **5 minutes**
- Discord setup (manual): **60-90 minutes**
- First release: **30 minutes**
- Invite testers: **2 hours**
- **Total: ~4 hours**

### Manual Path
- GitHub setup (manual): **30 minutes**
- Discord setup (manual): **60-90 minutes**
- First release: **30 minutes**
- Invite testers: **2 hours**
- **Total: ~4.5 hours**

---

## Support & Troubleshooting

### Common Issues

**GitHub script fails**:
- Install GitHub CLI: `brew install gh`
- Authenticate: `gh auth login`
- Make executable: `chmod +x create_github_repo.sh`

**Discord permissions broken**:
- Check role hierarchy
- Use "View Server as Role" to test
- Remember: Channel permissions override role permissions

**Can't create forum channels**:
- Enable Community Server first
- Settings → Community → Enable

**More help**: See troubleshooting sections in individual guides

---

## Related Documentation

In parent directory (`../`):

- **[IDE_INTEGRATION_PLAN.md](../IDE_INTEGRATION_PLAN.md)** - Complete 6-month roadmap
- **[ALPHA_TESTER_RECRUITMENT.md](../ALPHA_TESTER_RECRUITMENT.md)** - Recruiting materials
- **[DISCORD_SETUP_GUIDE.md](../DISCORD_SETUP_GUIDE.md)** - Original Discord guide (reference)
- **[IDE_INTEGRATION_SETUP_COMPLETE.md](../IDE_INTEGRATION_SETUP_COMPLETE.md)** - Overall setup status

---

## Questions?

**For GitHub**: See [GITHUB_SETUP_GUIDE.md](GITHUB_SETUP_GUIDE.md)

**For Discord**: See [DISCORD_SETUP_INSTRUCTIONS.md](DISCORD_SETUP_INSTRUCTIONS.md)

**For overall plan**: See [SETUP_COMPLETE.md](SETUP_COMPLETE.md)

**Need help?**: Email alpha@deepstudyai.com

---

## Progress Tracking

Use this checklist to track your progress:

- [ ] Read SETUP_COMPLETE.md
- [ ] Run create_github_repo.sh OR follow GitHub manual guide
- [ ] Verify GitHub repository is set up correctly
- [ ] Follow Discord setup instructions (60-90 min)
- [ ] Verify Discord server is configured correctly
- [ ] Build first release (VS Code + JetBrains)
- [ ] Publish release on GitHub
- [ ] Invite 50 testers to GitHub
- [ ] Send Discord invites to 50 testers
- [ ] Send email invitations to 50 testers
- [ ] Prepare for launch day (Nov 1)

**Status**: ⏳ Ready to start

**Next**: Run `./create_github_repo.sh`

---

**Last Updated**: 2025-10-15
**Created by**: Claude (Coach AI)
