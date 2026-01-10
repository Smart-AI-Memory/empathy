"""Analyze Generator Migration Candidates

Identifies list comprehensions that can be converted to generators
for memory optimization.

Criteria for good candidates:
1. List is only iterated once (not reused)
2. List is used in sum(), max(), min(), any(), all()
3. List is passed directly to another function that accepts iterables
4. Large intermediate lists (>100 items)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import ast
import sys
from pathlib import Path
from typing import Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class ListCompFinder(ast.NodeVisitor):
    """Find list comprehensions and analyze their usage."""

    def __init__(self):
        self.candidates = []
        self.current_function = None

    def visit_FunctionDef(self, node):
        """Track current function for context."""
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function

    def visit_ListComp(self, node):
        """Analyze list comprehension usage."""
        # Get source code (approximate)
        try:
            code = ast.unparse(node)
        except:
            code = "<unparsable>"

        # Check if it's in a function call that accepts iterables
        parent_is_call = False
        parent_func = None

        # This is a simplified analysis - real usage would need more context
        self.candidates.append(
            {
                "function": self.current_function,
                "code": code[:100],  # Truncate long expressions
                "line": getattr(node, "lineno", 0),
            }
        )

        self.generic_visit(node)


def analyze_file(file_path: Path) -> list[dict[str, Any]]:
    """Analyze a Python file for list comprehension candidates."""
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)

        finder = ListCompFinder()
        finder.visit(tree)

        return finder.candidates
    except (SyntaxError, UnicodeDecodeError):
        return []


def main():
    """Analyze key files for generator migration opportunities."""
    print("=" * 70)
    print("GENERATOR MIGRATION CANDIDATE ANALYSIS")
    print("=" * 70)
    print()

    # Key files to analyze
    target_files = [
        "src/empathy_os/project_index/scanner.py",
        "src/empathy_os/cost_tracker.py",
        "src/empathy_os/pattern_library.py",
        "src/empathy_os/workflows/test_gen.py",
        "src/empathy_os/telemetry/cli.py",
    ]

    total_candidates = 0

    for file_path_str in target_files:
        file_path = Path(file_path_str)
        if not file_path.exists():
            continue

        print(f"File: {file_path}")
        print("-" * 70)

        candidates = analyze_file(file_path)
        if candidates:
            print(f"Found {len(candidates)} list comprehensions:")
            for i, candidate in enumerate(candidates[:10], 1):  # Show first 10
                print(f"  {i}. Line {candidate['line']}: {candidate['function'] or '<module>'}")
                print(f"     {candidate['code']}")
            if len(candidates) > 10:
                print(f"     ... and {len(candidates) - 10} more")
        else:
            print("  No list comprehensions found")

        print()
        total_candidates += len(candidates)

    print("=" * 70)
    print(f"TOTAL: {total_candidates} list comprehensions across {len(target_files)} files")
    print("=" * 70)
    print()
    print("MANUAL REVIEW NEEDED:")
    print("- Check if list is only used once (good candidate)")
    print("- Check if list is used in sum(), max(), min(), any(), all()")
    print("- Avoid converting if list is reused multiple times")
    print("- Avoid converting if len() is needed (unless we can count differently)")


if __name__ == "__main__":
    main()
