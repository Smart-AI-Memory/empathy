# Release Automation Scripts

Automated tools for creating new releases of empathy-framework.

## Quick Start

**One-command release:**
```bash
./scripts/release.sh patch   # 1.6.4 → 1.6.5
./scripts/release.sh minor   # 1.6.4 → 1.7.0
./scripts/release.sh major   # 1.6.4 → 2.0.0
```

This does everything:
1. ✅ Bumps version in `pyproject.toml`
2. ✅ Updates `CHANGELOG.md` (with prompts)
3. ✅ Commits changes
4. ✅ Pushes to GitHub
5. ✅ Creates and pushes tag
6. ✅ Triggers automation (GitHub Actions → PyPI)

**Total time: ~30 seconds from command to PyPI** 🚀

## Step-by-Step Mode

If you prefer manual control:

```bash
# Step 1 & 2: Prepare release
python3 scripts/prepare_release.py patch

# Step 3: Review and commit
git diff
git add pyproject.toml CHANGELOG.md
git commit -m "release: Prepare vX.X.X"

# Step 4: Push
git push

# Step 5: Tag and trigger automation
git tag vX.X.X
git push origin vX.X.X
```

## Scripts

### `release.sh` - Full Automation
Complete end-to-end release with confirmation prompts.

**Usage:**
```bash
./scripts/release.sh patch   # Patch version bump (bug fixes)
./scripts/release.sh minor   # Minor version bump (new features)
./scripts/release.sh major   # Major version bump (breaking changes)
./scripts/release.sh 1.7.0   # Specific version
```

### `prepare_release.py` - Version & Changelog
Updates version and CHANGELOG without committing.

**Usage:**
```bash
python3 scripts/prepare_release.py patch
python3 scripts/prepare_release.py 1.7.0
```

**Interactive Changelog Entry:**
```
📝 Changelog Entry
==================================================
Enter changelog items (one per line).
Categories: Added, Changed, Fixed, Removed, Deprecated, Security
Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done.

>>> Added
  → Category: Added
>>> New API endpoint for batch processing
  ✓ Added to Added
>>> Changed
  → Category: Changed
>>> Improved error messages
  ✓ Added to Changed
>>> [Ctrl+D]
```

## Semantic Versioning

- **Patch** (1.6.4 → 1.6.5): Bug fixes, documentation updates
- **Minor** (1.6.4 → 1.7.0): New features, backward-compatible changes
- **Major** (1.6.4 → 2.0.0): Breaking changes, major rewrites

## What Happens After Tag Push?

GitHub Actions automatically:
1. **Builds** package (`python -m build`)
2. **Validates** with `twine check`
3. **Extracts** release notes from CHANGELOG.md
4. **Creates** GitHub release with artifacts
5. **Publishes** to PyPI

View progress:
```bash
gh run watch --workflow=release.yml
```

## Troubleshooting

**Script won't run:**
```bash
chmod +x scripts/release.sh
chmod +x scripts/prepare_release.py
```

**Version conflict:**
If tag already exists (immutable release), bump to next version:
```bash
./scripts/release.sh patch  # Try again with next version
```

**Changelog formatting:**
The script accepts markdown formatting:
```
>>> - **Bold feature**: Description with details
>>> - Bug fix for issue #123
```

## Example Release Flow

```bash
$ ./scripts/release.sh minor

🚀 Starting automated release process...

📝 Changelog Entry
==================================================
>>> Added
>>> - New trajectory analysis visualization
>>> - Support for custom LLM providers
>>> Changed
>>> - Improved memory retrieval performance (40% faster)
>>> [Ctrl+D]

✓ Updated pyproject.toml to 1.7.0
✓ Updated CHANGELOG.md with 1.7.0 entry

📋 Review the changes:
[diff output]

Continue with release v1.7.0? (y/N): y

📦 Committing changes...
⬆️  Pushing to remote...
🏷️  Creating tag v1.7.0...

✅ Release v1.7.0 initiated!

🔄 GitHub Actions is now:
  1. Building the package
  2. Creating GitHub release
  3. Publishing to PyPI

⏱️  Should complete in ~30 seconds

View progress: gh run watch --workflow=release.yml
View release: https://github.com/Smart-AI-Memory/empathy-framework/releases/tag/v1.7.0
```

## Manual Changelog (Advanced)

To skip interactive prompts, edit `CHANGELOG.md` directly before running:

```bash
# Edit CHANGELOG.md manually
vim CHANGELOG.md

# Then just bump version
python3 scripts/prepare_release.py 1.7.0

# Commit, tag, push
git add . && git commit -m "release: v1.7.0"
git tag v1.7.0 && git push && git push --tags
```
