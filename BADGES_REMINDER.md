# 🔔 Reminder: Restore Dynamic README Badges

**Date to Complete:** November 13-14, 2025 (2 days after package publish)

## Background

The empathy-framework package was published to PyPI on November 12, 2025. Dynamic badges were temporarily removed because badge services (shields.io, codecov, etc.) need 24-48 hours to index new packages.

## What to Do

### Step 1: Test Badge URLs

Check if these URLs now work (they should after 24-48 hours):

1. **PyPI Version**: https://img.shields.io/pypi/v/empathy-framework.svg
2. **Downloads**: https://img.shields.io/pypi/dm/empathy-framework.svg
3. **Python Versions**: https://img.shields.io/pypi/pyversions/empathy-framework.svg

Visit each URL in your browser - if you see a valid badge image (not an error), they're ready!

### Step 2: Restore Badges in README.md

Replace the current simplified badges section with:

```markdown
[![License](https://img.shields.io/badge/License-Fair%20Source%200.9-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/empathy-framework.svg)](https://pypi.org/project/empathy-framework/)
[![Python 3.10+](https://img.shields.io/pypi/pyversions/empathy-framework.svg)](https://www.python.org/downloads/)
[![Downloads](https://img.shields.io/pypi/dm/empathy-framework.svg)](https://pypi.org/project/empathy-framework/)
[![Tests](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml/badge.svg)](https://github.com/Smart-AI-Memory/empathy-framework/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
```

### Step 3: Optional - Add CodeCov and OpenSSF Badges

These require additional setup but can be added later:

**CodeCov** (requires CI/CD coverage upload):
```markdown
[![codecov](https://codecov.io/gh/Smart-AI-Memory/empathy-framework/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy-framework)
```

**OpenSSF Scorecard** (requires registration at https://securityscorecards.dev):
```markdown
[![OpenSSF Scorecard](https://api.securityscorecards.dev/projects/github.com/Smart-AI-Memory/empathy-framework/badge)](https://securityscorecards.dev/viewer/?uri=github.com/Smart-AI-Memory/empathy-framework)
```

### Step 4: Commit and Push

```bash
git add README.md
git commit -m "docs: Restore dynamic badges after PyPI indexing"
git push
```

### Step 5: Delete This Reminder

```bash
rm BADGES_REMINDER.md
git add BADGES_REMINDER.md
git commit -m "chore: Remove badges reminder after completion"
git push
```

## Quick Commands

```bash
# Check if package is indexed (should return JSON with package info)
curl https://pypi.org/pypi/empathy-framework/json

# Check shield.io badge status
curl -I https://img.shields.io/pypi/v/empathy-framework.svg

# If you see HTTP 200, badges are ready!
```

---

**Created:** November 12, 2025
**Target Date:** November 13-14, 2025
**Status:** ⏳ Waiting for badge services to index package
