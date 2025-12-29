#!/usr/bin/env python3
"""
Test Quality Checker

Analyzes test files for common quality issues:
- Tests with only `pass` statements (placeholders)
- Tests with TODO comments
- Duplicate test function names
- Parametrization usage percentage

Usage:
    python scripts/check_test_quality.py [--fix] [--verbose]

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import ast
from collections import Counter
from pathlib import Path


class TestQualityChecker:
    """Analyzes test files for quality issues."""

    def __init__(self, tests_dir: str = "tests"):
        self.tests_dir = Path(tests_dir)
        self.issues: list[dict] = []
        self.stats = {
            "total_test_files": 0,
            "total_test_functions": 0,
            "pass_only_tests": 0,
            "todo_tests": 0,
            "parametrized_tests": 0,
            "duplicate_names": [],
        }

    def analyze(self) -> dict:
        """Analyze all test files and return statistics."""
        test_names: list[str] = []

        for test_file in self.tests_dir.rglob("test_*.py"):
            self.stats["total_test_files"] += 1
            self._analyze_file(test_file, test_names)

        # Find duplicates
        name_counts = Counter(test_names)
        self.stats["duplicate_names"] = [
            {"name": name, "count": count} for name, count in name_counts.items() if count > 1
        ]

        # Calculate percentages
        total = self.stats["total_test_functions"]
        if total > 0:
            self.stats["pass_only_percent"] = round(self.stats["pass_only_tests"] / total * 100, 1)
            self.stats["parametrized_percent"] = round(
                self.stats["parametrized_tests"] / total * 100, 1
            )
        else:
            self.stats["pass_only_percent"] = 0
            self.stats["parametrized_percent"] = 0

        return self.stats

    def _analyze_file(self, file_path: Path, test_names: list[str]) -> None:
        """Analyze a single test file."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
        except (SyntaxError, UnicodeDecodeError):
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_"):
                self.stats["total_test_functions"] += 1
                test_names.append(node.name)

                # Check for pass-only tests
                if self._is_pass_only(node):
                    self.stats["pass_only_tests"] += 1
                    self.issues.append(
                        {
                            "file": str(file_path),
                            "function": node.name,
                            "line": node.lineno,
                            "issue": "pass_only",
                        }
                    )

                # Check for TODO comments
                if self._has_todo(node, content):
                    self.stats["todo_tests"] += 1
                    self.issues.append(
                        {
                            "file": str(file_path),
                            "function": node.name,
                            "line": node.lineno,
                            "issue": "has_todo",
                        }
                    )

                # Check for parametrization
                if self._is_parametrized(node):
                    self.stats["parametrized_tests"] += 1

    def _is_pass_only(self, node: ast.FunctionDef) -> bool:
        """Check if function body is only pass statements and docstrings."""
        body = node.body
        for stmt in body:
            # Skip docstrings
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                continue
            # Check for pass
            if not isinstance(stmt, ast.Pass):
                return False
        return True

    def _has_todo(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if function contains TODO comments."""
        # Get function source lines
        lines = content.split("\n")
        start = node.lineno - 1
        end = node.end_lineno if hasattr(node, "end_lineno") else start + 50

        for line in lines[start:end]:
            if "# TODO" in line or "# todo" in line:
                return True
        return False

    def _is_parametrized(self, node: ast.FunctionDef) -> bool:
        """Check if function uses pytest.mark.parametrize."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == "parametrize":
                        return True
            elif isinstance(decorator, ast.Attribute):
                if decorator.attr == "parametrize":
                    return True
        return False

    def report(self, verbose: bool = False) -> None:
        """Print analysis report."""
        print("\n" + "=" * 60)
        print("TEST QUALITY REPORT")
        print("=" * 60)

        print(f"\nTotal test files: {self.stats['total_test_files']}")
        print(f"Total test functions: {self.stats['total_test_functions']}")

        print("\n--- Quality Metrics ---")
        print(
            f"Pass-only tests: {self.stats['pass_only_tests']} ({self.stats['pass_only_percent']}%)"
        )
        print(f"Tests with TODOs: {self.stats['todo_tests']}")
        print(
            f"Parametrized tests: {self.stats['parametrized_tests']} ({self.stats['parametrized_percent']}%)"
        )
        print(f"Duplicate test names: {len(self.stats['duplicate_names'])}")

        # Quality score (higher is better)
        score = 100
        score -= self.stats["pass_only_percent"]  # Penalize pass-only tests
        score += self.stats["parametrized_percent"] * 0.5  # Reward parametrization
        score -= len(self.stats["duplicate_names"]) * 0.5  # Penalize duplicates
        score = max(0, min(100, score))

        print(f"\n--- Quality Score: {score:.1f}/100 ---")

        if verbose and self.issues:
            print("\n--- Issues Found ---")
            for issue in self.issues[:20]:  # Limit output
                print(f"  {issue['file']}:{issue['line']} - {issue['function']} ({issue['issue']})")
            if len(self.issues) > 20:
                print(f"  ... and {len(self.issues) - 20} more issues")

        if self.stats["duplicate_names"]:
            print("\n--- Duplicate Test Names ---")
            for dup in self.stats["duplicate_names"][:10]:
                print(f"  {dup['name']}: {dup['count']} occurrences")

        print("\n" + "=" * 60)

        # Return non-zero if quality is too low
        if score < 50:
            print("\nWARNING: Test quality score below threshold (50)")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Check test quality")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed issues")
    parser.add_argument("--tests-dir", default="tests", help="Tests directory")
    args = parser.parse_args()

    checker = TestQualityChecker(tests_dir=args.tests_dir)
    checker.analyze()
    checker.report(verbose=args.verbose)


if __name__ == "__main__":
    main()
