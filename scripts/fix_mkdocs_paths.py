#!/usr/bin/env python3
"""Fix MkDocs relative asset paths to absolute paths.

MkDocs generates relative paths like "../../assets/" which only work correctly
when URLs have trailing slashes. This script converts them to absolute paths
that work regardless of trailing slashes.
"""

import re
from pathlib import Path


def fix_html_file(file_path: Path, base_path: str = "/framework-docs") -> int:
    """Fix relative asset paths in an HTML file to absolute paths.

    Args:
        file_path: Path to the HTML file
        base_path: Base path for absolute URLs (e.g., "/framework-docs")

    Returns:
        Number of replacements made

    """
    content = file_path.read_text(encoding="utf-8")
    original = content

    # Patterns to fix:
    # href="../../assets/" -> href="/framework-docs/assets/"
    # src="../../assets/" -> src="/framework-docs/assets/"
    # href="../assets/" -> href="/framework-docs/assets/"
    # etc.

    # Replace relative paths to assets
    patterns = [
        # Multiple levels up to assets
        (r'(href|src)="(\.\./)+assets/', rf'\1="{base_path}/assets/'),
        # Relative stylesheets paths
        (r'(href)="(\.\./)+stylesheets/', rf'\1="{base_path}/stylesheets/'),
        # Relative javascripts paths
        (r'(src)="(\.\./)+javascripts/', rf'\1="{base_path}/javascripts/'),
        # Relative search paths
        (r'(src)="(\.\./)+search/', rf'\1="{base_path}/search/'),
        # css file references
        (r'href="(\.\./)+([^"]+\.css)"', rf'href="{base_path}/\2"'),
        # js file references
        (r'src="(\.\./)+([^"]+\.js)"', rf'src="{base_path}/\2"'),
    ]

    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)

    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return 1
    return 0


def main():
    """Process all HTML files in the website/public/framework-docs directory."""
    docs_dir = Path(__file__).parent.parent / "website" / "public" / "framework-docs"

    if not docs_dir.exists():
        print(f"Error: Directory not found: {docs_dir}")
        return 1

    html_files = list(docs_dir.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files")

    fixed_count = 0
    for html_file in html_files:
        count = fix_html_file(html_file)
        if count:
            fixed_count += 1
            print(f"  Fixed: {html_file.relative_to(docs_dir)}")

    print(f"\nFixed {fixed_count} files")
    return 0


if __name__ == "__main__":
    exit(main())
