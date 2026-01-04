"""Pattern Resolution Module

Provides CLI workflow for resolving investigating bug patterns
by adding root cause, fix, and resolution time.

Usage:
    from empathy_llm_toolkit.pattern_resolver import PatternResolver

    resolver = PatternResolver("./patterns")
    resolver.resolve_bug(
        bug_id="bug_20251212_3c5b9951",
        root_cause="Missing null check on API response",
        fix_applied="Added optional chaining operator",
        fix_code="data?.items ?? []",
        resolution_time_minutes=15,
        resolved_by="@developer"
    )

CLI:
    empathy patterns resolve bug_20251212_3c5b9951 \\
        --root-cause "Missing null check" \\
        --fix "Added optional chaining" \\
        --fix-code "data?.items ?? []" \\
        --time 15 \\
        --resolved-by "@developer"

Author: Empathy Framework Team
Version: 2.1.3
License: Fair Source 0.9
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class PatternResolver:
    """Resolves investigating bug patterns with root cause and fix information.

    Searches through pattern directories to find matching bug IDs
    and updates them with resolution details.
    """

    def __init__(self, patterns_dir: str = "./patterns"):
        self.patterns_dir = Path(patterns_dir)
        self._debugging_dirs = ["debugging", "debugging_demo", "repo_test/debugging"]

    def find_bug(self, bug_id: str) -> tuple[Path | None, dict[str, Any] | None]:
        """Find a bug pattern by ID.

        Args:
            bug_id: The bug ID to find (e.g., "bug_20251212_3c5b9951")

        Returns:
            Tuple of (file_path, pattern_data) or (None, None) if not found

        """
        for debug_dir in self._debugging_dirs:
            dir_path = self.patterns_dir / debug_dir
            if not dir_path.exists():
                continue

            # Check for exact filename match
            pattern_file = dir_path / f"{bug_id}.json"
            if pattern_file.exists():
                try:
                    with open(pattern_file, encoding="utf-8") as f:
                        return pattern_file, json.load(f)
                except (json.JSONDecodeError, OSError) as e:
                    logger.warning("Failed to load %s: %s", pattern_file, e)

            # Search all bug files for matching bug_id field
            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("bug_id") == bug_id:
                            return json_file, data
                except (json.JSONDecodeError, OSError):
                    continue

        return None, None

    def list_investigating(self) -> list[dict[str, Any]]:
        """List all bugs with status 'investigating'.

        Returns:
            List of bug patterns that need resolution

        """
        investigating = []

        for debug_dir in self._debugging_dirs:
            dir_path = self.patterns_dir / debug_dir
            if not dir_path.exists():
                continue

            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        data = json.load(f)
                        if data.get("status") == "investigating":
                            data["_file_path"] = str(json_file)
                            investigating.append(data)
                except (json.JSONDecodeError, OSError):
                    continue

        return investigating

    def resolve_bug(
        self,
        bug_id: str,
        root_cause: str,
        fix_applied: str,
        fix_code: str | None = None,
        resolution_time_minutes: int = 0,
        resolved_by: str = "@developer",
    ) -> bool:
        """Resolve a bug pattern by updating its fields.

        Args:
            bug_id: The bug ID to resolve
            root_cause: Description of the root cause
            fix_applied: Description of the fix applied
            fix_code: Optional code snippet of the fix
            resolution_time_minutes: Time taken to resolve
            resolved_by: Who resolved the bug

        Returns:
            True if successfully resolved, False otherwise

        """
        file_path, pattern = self.find_bug(bug_id)

        if not file_path or not pattern:
            logger.error("Bug not found: %s", bug_id)
            return False

        # Update pattern with resolution details
        pattern["root_cause"] = root_cause
        pattern["fix_applied"] = fix_applied
        pattern["status"] = "resolved"
        pattern["resolved_by"] = resolved_by
        pattern["resolution_time_minutes"] = resolution_time_minutes
        pattern["resolved_at"] = datetime.now().isoformat()

        if fix_code:
            pattern["fix_code"] = fix_code

        # Write updated pattern back to file
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(pattern, f, indent=2, default=str)

            logger.info("Resolved bug %s in %s", bug_id, file_path)
            return True
        except OSError as e:
            logger.error("Failed to write %s: %s", file_path, e)
            return False

    def regenerate_summary(self) -> bool:
        """Regenerate the patterns_summary.md file.

        Returns:
            True if successful, False otherwise

        """
        try:
            from empathy_llm_toolkit.pattern_summary import PatternSummaryGenerator

            generator = PatternSummaryGenerator(str(self.patterns_dir))
            generator.load_all_patterns()
            generator.write_to_file("./.claude/patterns_summary.md")
            logger.info("Regenerated patterns_summary.md")
            return True
        except Exception as e:
            logger.error("Failed to regenerate summary: %s", e)
            return False


def cmd_patterns_resolve(args):
    """CLI handler for patterns resolve command."""
    resolver = PatternResolver(args.patterns_dir)

    # If no bug_id, list investigating bugs
    if not args.bug_id:
        investigating = resolver.list_investigating()
        if not investigating:
            print("No bugs with 'investigating' status found.")
            return

        print(f"\nBugs needing resolution ({len(investigating)}):\n")
        for bug in investigating:
            print(f"  {bug.get('bug_id', 'unknown')}")
            print(f"    Type: {bug.get('error_type', 'unknown')}")
            print(f"    File: {bug.get('file_path', 'unknown')}")
            print(f"    Message: {bug.get('error_message', 'N/A')[:60]}...")
            print()
        return

    # Resolve the specified bug
    success = resolver.resolve_bug(
        bug_id=args.bug_id,
        root_cause=args.root_cause,
        fix_applied=args.fix,
        fix_code=args.fix_code,
        resolution_time_minutes=args.time or 0,
        resolved_by=args.resolved_by or "@developer",
    )

    if success:
        print(f"✓ Resolved: {args.bug_id}")

        # Regenerate summary if requested
        if not args.no_regenerate:
            if resolver.regenerate_summary():
                print("✓ Regenerated patterns_summary.md")
            else:
                print("⚠ Failed to regenerate summary")
    else:
        print(f"✗ Failed to resolve: {args.bug_id}")
        print("  Use 'empathy patterns resolve' (no args) to list investigating bugs")


def main():
    """CLI entry point for pattern resolution."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Resolve investigating bug patterns",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all investigating bugs
  python -m empathy_llm_toolkit.pattern_resolver

  # Resolve a specific bug
  python -m empathy_llm_toolkit.pattern_resolver bug_20251212_3c5b9951 \\
      --root-cause "Missing null check" \\
      --fix "Added optional chaining" \\
      --fix-code "data?.items ?? []" \\
      --time 15
        """,
    )

    parser.add_argument("bug_id", nargs="?", help="Bug ID to resolve (omit to list investigating)")
    parser.add_argument("--root-cause", help="Description of the root cause")
    parser.add_argument("--fix", help="Description of the fix applied")
    parser.add_argument("--fix-code", help="Code snippet of the fix")
    parser.add_argument("--time", type=int, help="Resolution time in minutes")
    parser.add_argument("--resolved-by", default="@developer", help="Who resolved it")
    parser.add_argument("--patterns-dir", default="./patterns", help="Path to patterns directory")
    parser.add_argument("--no-regenerate", action="store_true", help="Skip regenerating summary")

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    # Validate required args if resolving
    if args.bug_id and not (args.root_cause and args.fix):
        parser.error("--root-cause and --fix are required when resolving a bug")

    cmd_patterns_resolve(args)


if __name__ == "__main__":
    main()
