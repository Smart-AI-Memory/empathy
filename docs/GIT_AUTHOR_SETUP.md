# Git Author Configuration Guide

This guide explains how to configure git author information so your commits are properly attributed to you in the repository and on GitHub.

## Quick Setup

Set your name and email that will appear on all your commits:

```bash
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Understanding Git Author Attribution

When you make commits to a Git repository, Git records:
1. **Author Name** - Your display name
2. **Author Email** - Your email address
3. **Timestamp** - When the commit was made

This information is permanently recorded in the git history and displayed on GitHub.

## Configuration Levels

Git has three configuration levels:

### 1. System-wide (all users)
```bash
git config --system user.name "Your Name"
git config --system user.email "your.email@example.com"
```

### 2. Global (your user account)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 3. Repository-specific (recommended for this project)
```bash
cd /path/to/empathy
git config user.name "Your Name"
git config user.email "your.email@example.com"
```

## Best Practices

### Use Your GitHub Email

To ensure your commits link to your GitHub account:

1. Find your GitHub email:
   - Go to GitHub Settings → Emails
   - Use your public email or GitHub-provided noreply email

2. Configure git:
```bash
git config user.name "Your GitHub Username"
git config user.email "your-github-email@users.noreply.github.com"
```

### Private Email

If you want to keep your email private, GitHub provides a no-reply email:
```
<username>@users.noreply.github.com
```

Or with ID:
```
<ID+username>@users.noreply.github.com
```

Example:
```bash
git config user.name "Jane Developer"
git config user.email "janedev@users.noreply.github.com"
```

## Verifying Your Configuration

Check your current settings:

```bash
git config user.name
git config user.email
```

View all git configurations:
```bash
git config --list
```

## Changing Author for Existing Commits

**Warning:** Rewriting git history can cause problems in shared repositories. Only do this if you understand the implications.

### For the Last Commit

```bash
git commit --amend --author="Your Name <your.email@example.com>"
```

### For Multiple Commits

Use interactive rebase (advanced):
```bash
git rebase -i HEAD~N  # N = number of commits to go back
```

### For All Commits in a Branch

```bash
git filter-branch --env-filter '
OLD_EMAIL="old@email.com"
CORRECT_NAME="Your Name"
CORRECT_EMAIL="your.email@example.com"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags
```

**Note:** After rewriting history, you'll need to force push:
```bash
git push --force-with-lease origin your-branch
```

## Using .mailmap

The repository includes a `.mailmap` file that helps Git map different author identities to a canonical name and email. This is useful when:
- You've used different email addresses in commits
- You want to consolidate multiple identities
- You need to update how authors appear in logs

The `.mailmap` format:
```
Preferred Name <preferred@email.com> Commit Name <commit@email.com>
```

## GitHub Integration

### Linking Commits to Your Profile

For commits to show up on your GitHub profile:

1. **Email must be verified** in GitHub settings
2. **Email must match** one in your GitHub account
3. **Email can be** your GitHub noreply address

### Checking Attribution

After committing, check on GitHub:
1. Push your commits
2. View the commit on GitHub
3. Your avatar and username should appear if properly configured

## Troubleshooting

### Commits Don't Show on My Profile

1. Verify your email is added to GitHub:
   - GitHub Settings → Emails → Add email address

2. Check git configuration:
```bash
git config user.email
```

3. Ensure email matches exactly (case-sensitive)

### Wrong Author on Commits

1. Check current configuration:
```bash
git config user.name
git config user.email
```

2. Update for future commits:
```bash
git config user.name "Correct Name"
git config user.email "correct@email.com"
```

3. For existing commits, see "Changing Author for Existing Commits" above

### Multiple Git Identities

If you work on multiple projects with different identities, use repository-specific config:

```bash
# Project 1
cd /path/to/project1
git config user.name "Work Name"
git config user.email "work@company.com"

# Project 2
cd /path/to/project2
git config user.name "Personal Name"
git config user.email "personal@email.com"
```

## Additional Resources

- [Git Configuration Documentation](https://git-scm.com/docs/git-config)
- [GitHub Managing Commit Signature Verification](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- [Git mailmap Documentation](https://git-scm.com/docs/gitmailmap)

## Questions?

If you have questions about git configuration or author attribution, please:
- Check [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy/discussions)
- Review [Contributing Guidelines](../CONTRIBUTING.md)
- Open an issue for documentation improvements
