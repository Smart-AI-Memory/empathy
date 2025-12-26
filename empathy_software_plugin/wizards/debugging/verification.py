"""
Verification Module

Re-runs linters to verify fixes were successful.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .linter_parsers import LintIssue, parse_linter_output


def _validate_target_path(target: str) -> bool:
    """
    Validate target path is safe for linter subprocess execution.

    SECURITY: Prevents command injection via malicious file/directory paths.
    Checks that path exists and doesn't contain shell metacharacters.
    """
    if not target:
        return False
    try:
        p = Path(target).resolve()
        # Must exist as file or directory
        if not p.exists():
            return False
        # Must not contain shell metacharacters
        shell_chars = set(";|&$`(){}[]<>\\'\"\n\r\t")
        if any(c in str(p) for c in shell_chars):
            return False
        return True
    except Exception:
        return False


@dataclass
class VerificationResult:
    """Result of verification check"""

    linter: str
    success: bool
    issues_before: int
    issues_after: int
    issues_fixed: int
    issues_remaining: int
    new_issues: int
    remaining_issues: list[LintIssue]
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "linter": self.linter,
            "success": self.success,
            "issues_before": self.issues_before,
            "issues_after": self.issues_after,
            "issues_fixed": self.issues_fixed,
            "issues_remaining": self.issues_remaining,
            "new_issues": self.new_issues,
            "remaining_issues": [i.to_dict() for i in self.remaining_issues],
            "error": self.error,
        }


class BaseLinterRunner:
    """Base class for running linters"""

    def __init__(self, linter_name: str):
        self.linter_name = linter_name

    def run(self, target: str, output_format: str = "json") -> list[LintIssue]:
        """
        Run linter on target.

        Args:
            target: File or directory to lint
            output_format: Output format ("json" or "text")

        Returns:
            List of LintIssue objects
        """
        raise NotImplementedError


class ESLintRunner(BaseLinterRunner):
    """Run ESLint"""

    def __init__(self):
        super().__init__("eslint")

    def run(self, target: str, output_format: str = "json") -> list[LintIssue]:
        """Run ESLint"""

        # SECURITY: Validate target path before subprocess execution
        if not _validate_target_path(target):
            raise ValueError(f"Invalid or unsafe target path: {target}")

        cmd = ["npx", "eslint"]

        if output_format == "json":
            cmd.append("--format=json")

        cmd.append(target)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # ESLint exits with 1 if there are violations (expected)
            output = result.stdout

            if output_format == "json":
                return parse_linter_output(self.linter_name, output, "json")
            else:
                return parse_linter_output(self.linter_name, output, "text")

        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError as e:
            raise RuntimeError("ESLint not found. Run: npm install eslint") from e


class PylintRunner(BaseLinterRunner):
    """Run Pylint"""

    def __init__(self):
        super().__init__("pylint")

    def run(self, target: str, output_format: str = "json") -> list[LintIssue]:
        """Run Pylint"""

        # SECURITY: Validate target path before subprocess execution
        if not _validate_target_path(target):
            raise ValueError(f"Invalid or unsafe target path: {target}")

        cmd = ["pylint"]

        if output_format == "json":
            cmd.append("--output-format=json")

        cmd.append(target)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            # Pylint exits with non-zero if violations (expected)
            output = result.stdout

            if output_format == "json":
                return parse_linter_output(self.linter_name, output, "json")
            else:
                return parse_linter_output(self.linter_name, output, "text")

        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError as e:
            raise RuntimeError("Pylint not found. Run: pip install pylint") from e


class MyPyRunner(BaseLinterRunner):
    """Run mypy"""

    def __init__(self):
        super().__init__("mypy")

    def run(self, target: str, output_format: str = "json") -> list[LintIssue]:
        """Run mypy"""

        # SECURITY: Validate target path before subprocess execution
        if not _validate_target_path(target):
            raise ValueError(f"Invalid or unsafe target path: {target}")

        cmd = ["mypy", target]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            output = result.stdout

            return parse_linter_output(self.linter_name, output, "text")

        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError as e:
            raise RuntimeError("mypy not found. Run: pip install mypy") from e


class TypeScriptRunner(BaseLinterRunner):
    """Run TypeScript compiler"""

    def __init__(self):
        super().__init__("typescript")

    def run(self, target: str, output_format: str = "json") -> list[LintIssue]:
        """Run tsc"""

        cmd = ["npx", "tsc", "--noEmit"]

        # If target is a directory, use project mode
        if Path(target).is_dir():
            cmd.extend(["--project", target])
        else:
            cmd.append(target)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            output = result.stdout

            return parse_linter_output(self.linter_name, output, "text")

        except subprocess.TimeoutExpired:
            return []
        except FileNotFoundError as e:
            raise RuntimeError("TypeScript not found. Run: npm install typescript") from e


class LinterRunnerFactory:
    """Factory for creating linter runners"""

    _runners = {
        "eslint": ESLintRunner,
        "pylint": PylintRunner,
        "mypy": MyPyRunner,
        "typescript": TypeScriptRunner,
        "tsc": TypeScriptRunner,
    }

    @classmethod
    def create(cls, linter_name: str) -> BaseLinterRunner:
        """Create linter runner"""
        runner_class = cls._runners.get(linter_name.lower())

        if not runner_class:
            raise ValueError(
                f"Unsupported linter runner: {linter_name}. "
                f"Supported: {', '.join(cls._runners.keys())}"
            )

        return runner_class()


def run_linter(linter_name: str, target: str, output_format: str = "json") -> list[LintIssue]:
    """
    Run linter on target.

    Args:
        linter_name: Name of linter
        target: File or directory to lint
        output_format: "json" or "text"

    Returns:
        List of LintIssue objects

    Example:
        >>> issues = run_linter("eslint", "/path/to/project")
        >>> print(f"Found {len(issues)} issues")
    """
    runner = LinterRunnerFactory.create(linter_name)
    return runner.run(target, output_format)


def verify_fixes(
    linter_name: str, target: str, issues_before: list[LintIssue]
) -> VerificationResult:
    """
    Verify that fixes were successful by re-running linter.

    Args:
        linter_name: Name of linter
        target: File or directory that was fixed
        issues_before: Issues that existed before fixes

    Returns:
        VerificationResult with comparison

    Example:
        >>> result = verify_fixes("eslint", "/path/to/project", original_issues)
        >>> if result.success:
        ...     print(f"Fixed {result.issues_fixed} issues!")
    """

    try:
        # Re-run linter
        issues_after = run_linter(linter_name, target)

        # Compare
        issues_before_count = len(issues_before)
        issues_after_count = len(issues_after)

        issues_fixed = max(0, issues_before_count - issues_after_count)
        issues_remaining = issues_after_count

        # Check for new issues (regressions)
        before_keys = {(i.file_path, i.line, i.rule) for i in issues_before}
        after_keys = {(i.file_path, i.line, i.rule) for i in issues_after}

        new_issue_keys = after_keys - before_keys
        new_issues = len(new_issue_keys)

        return VerificationResult(
            linter=linter_name,
            success=(issues_after_count < issues_before_count and new_issues == 0),
            issues_before=issues_before_count,
            issues_after=issues_after_count,
            issues_fixed=issues_fixed,
            issues_remaining=issues_remaining,
            new_issues=new_issues,
            remaining_issues=issues_after,
        )

    except Exception as e:
        return VerificationResult(
            linter=linter_name,
            success=False,
            issues_before=len(issues_before),
            issues_after=0,
            issues_fixed=0,
            issues_remaining=0,
            new_issues=0,
            remaining_issues=[],
            error=str(e),
        )


def compare_issue_lists(before: list[LintIssue], after: list[LintIssue]) -> dict[str, Any]:
    """
    Detailed comparison of issue lists.

    Args:
        before: Issues before fixes
        after: Issues after fixes

    Returns:
        Dictionary with detailed comparison
    """

    before_set = {(i.file_path, i.line, i.column, i.rule) for i in before}
    after_set = {(i.file_path, i.line, i.column, i.rule) for i in after}

    fixed = before_set - after_set
    remaining = before_set & after_set
    new = after_set - before_set

    # Group by file
    files_improved = set()
    files_regressed = set()

    for issue in before:
        key = (issue.file_path, issue.line, issue.column, issue.rule)
        if key in fixed:
            files_improved.add(issue.file_path)

    for issue in after:
        key = (issue.file_path, issue.line, issue.column, issue.rule)
        if key in new:
            files_regressed.add(issue.file_path)

    return {
        "total_before": len(before),
        "total_after": len(after),
        "fixed_count": len(fixed),
        "remaining_count": len(remaining),
        "new_count": len(new),
        "files_improved": list(files_improved),
        "files_regressed": list(files_regressed),
        "net_improvement": len(fixed) - len(new),
    }
