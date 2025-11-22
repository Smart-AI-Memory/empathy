#!/bin/bash
# Complete Release Automation Script
# Usage: ./scripts/release.sh patch
#        ./scripts/release.sh minor
#        ./scripts/release.sh major
#        ./scripts/release.sh 1.7.0

set -e  # Exit on error

BUMP_TYPE="${1:-patch}"

echo "🚀 Starting automated release process..."
echo ""

# Step 1 & 2: Prepare release (version bump + changelog)
python3 scripts/prepare_release.py "$BUMP_TYPE"

# Extract new version from pyproject.toml
NEW_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')

echo ""
echo "📋 Review the changes:"
git diff pyproject.toml CHANGELOG.md
echo ""

read -p "Continue with release v$NEW_VERSION? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Release cancelled"
    git checkout pyproject.toml CHANGELOG.md
    exit 1
fi

# Step 3: Commit changes
echo ""
echo "📦 Committing changes..."
git add pyproject.toml CHANGELOG.md
git commit -m "release: Prepare v$NEW_VERSION

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# Step 4: Push to remote
echo ""
echo "⬆️  Pushing to remote..."
git push

# Step 5: Create and push tag
echo ""
echo "🏷️  Creating tag v$NEW_VERSION..."
git tag "v$NEW_VERSION"
git push origin "v$NEW_VERSION"

echo ""
echo "✅ Release v$NEW_VERSION initiated!"
echo ""
echo "🔄 GitHub Actions is now:"
echo "  1. Building the package"
echo "  2. Creating GitHub release"
echo "  3. Publishing to PyPI"
echo ""
echo "⏱️  Should complete in ~30 seconds"
echo ""
echo "View progress: gh run watch --workflow=release.yml"
echo "View release: https://github.com/Smart-AI-Memory/empathy-framework/releases/tag/v$NEW_VERSION"
