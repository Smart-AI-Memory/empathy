#!/usr/bin/env python3
"""
Release Preparation Script
Automates version bumping and CHANGELOG updates for empathy-framework releases.

Usage:
    python scripts/prepare_release.py patch   # 1.6.4 -> 1.6.5
    python scripts/prepare_release.py minor   # 1.6.4 -> 1.7.0
    python scripts/prepare_release.py major   # 1.6.4 -> 2.0.0
    python scripts/prepare_release.py 1.7.0   # Specific version
"""

import re
import sys
from datetime import datetime
from pathlib import Path


def get_current_version():
    """Extract current version from pyproject.toml"""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    match = re.search(r'^version = "([^"]+)"', content, re.MULTILINE)
    if not match:
        raise ValueError("Could not find version in pyproject.toml")
    return match.group(1)


def bump_version(current: str, bump_type: str) -> str:
    """Bump version based on type (major, minor, patch) or return specific version"""
    # If it's a specific version like "1.7.0", return it
    if re.match(r"^\d+\.\d+\.\d+$", bump_type):
        return bump_type

    major, minor, patch = map(int, current.split("."))

    if bump_type == "major":
        return f"{major + 1}.0.0"
    elif bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    elif bump_type == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(
            f"Invalid bump type: {bump_type}. Use major, minor, patch, or a version number."
        )


def update_pyproject(new_version: str):
    """Update version in pyproject.toml"""
    pyproject = Path("pyproject.toml")
    content = pyproject.read_text()
    updated = re.sub(
        r'^version = "[^"]+"', f'version = "{new_version}"', content, flags=re.MULTILINE
    )
    pyproject.write_text(updated)
    print(f"✓ Updated pyproject.toml to {new_version}")


def get_changelog_entry():
    """Prompt user for changelog entry"""
    print("\n📝 Changelog Entry")
    print("=" * 50)
    print("Enter changelog items (one per line).")
    print("Categories: Added, Changed, Fixed, Removed, Deprecated, Security")
    print("Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done, or just Enter to skip.\n")

    entries = {
        "Added": [],
        "Changed": [],
        "Fixed": [],
        "Removed": [],
        "Deprecated": [],
        "Security": [],
    }

    current_category = None

    try:
        while True:
            line = input(">>> ").strip()
            if not line:
                break

            # Check if line is a category header
            if line in entries:
                current_category = line
                print(f"  → Category: {current_category}")
                continue

            # If no category selected, ask
            if current_category is None:
                print("\nSelect category:")
                for i, cat in enumerate(entries.keys(), 1):
                    print(f"  {i}. {cat}")
                choice = input("Enter number (or category name): ").strip()

                if choice.isdigit():
                    current_category = list(entries.keys())[int(choice) - 1]
                else:
                    current_category = choice if choice in entries else "Changed"

            entries[current_category].append(line)
            print(f"  ✓ Added to {current_category}")
    except EOFError:
        pass

    return entries


def format_changelog_section(entries: dict) -> str:
    """Format changelog entries into markdown"""
    sections = []
    for category, items in entries.items():
        if items:
            sections.append(f"\n### {category}")
            for item in items:
                # Add bullet if not present
                item = item if item.startswith("-") else f"- {item}"
                sections.append(item)

    return "\n".join(sections) if sections else "\n### Changed\n- Version bump"


def update_changelog(new_version: str, entry_text: str):
    """Update CHANGELOG.md with new version entry"""
    changelog = Path("CHANGELOG.md")
    content = changelog.read_text()

    today = datetime.now().strftime("%Y-%m-%d")
    new_entry = f"""## [{new_version}] - {today}
{entry_text}

"""

    # Insert after the header (before first ## entry)
    updated = re.sub(
        r"(# Changelog.*?and this project adheres to.*?\n\n)",
        rf"\1{new_entry}",
        content,
        flags=re.DOTALL,
    )

    changelog.write_text(updated)
    print(f"✓ Updated CHANGELOG.md with {new_version} entry")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)

    bump_type = sys.argv[1]

    try:
        # Get current version and calculate new version
        current_version = get_current_version()
        new_version = bump_version(current_version, bump_type)

        print("\n🚀 Release Preparation")
        print(f"{'=' * 50}")
        print(f"Current version: {current_version}")
        print(f"New version:     {new_version}")
        print()

        # Update pyproject.toml
        update_pyproject(new_version)

        # Get changelog entries
        entries = get_changelog_entry()
        entry_text = format_changelog_section(entries)

        # Update CHANGELOG.md
        update_changelog(new_version, entry_text)

        print(f"\n✅ Release {new_version} prepared!")
        print("\nNext steps:")
        print("  1. Review changes: git diff")
        print(f"  2. Commit: git add . && git commit -m 'release: Prepare v{new_version}'")
        print("  3. Push: git push")
        print(f"  4. Tag: git tag v{new_version} && git push origin v{new_version}")
        print("  5. Automation handles the rest! 🎉")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
