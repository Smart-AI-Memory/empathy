"""
Fix Applier

Systematically applies fixes to code based on linter violations.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import subprocess
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re

from .linter_parsers import LintIssue, Severity


@dataclass
class FixResult:
    """Result of attempting to fix an issue"""
    issue: LintIssue
    success: bool
    method: str  # "autofix", "manual_suggestion", "skipped"
    changes_made: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "issue": self.issue.to_dict(),
            "success": self.success,
            "method": self.method,
            "changes_made": self.changes_made,
            "error": self.error
        }


class BaseFixApplier:
    """Base class for fix appliers"""

    def __init__(self, linter_name: str):
        self.linter_name = linter_name

    def can_autofix(self, issue: LintIssue) -> bool:
        """Check if issue can be auto-fixed"""
        raise NotImplementedError

    def apply_fix(self, issue: LintIssue, dry_run: bool = False) -> FixResult:
        """
        Apply fix for issue.

        Args:
            issue: LintIssue to fix
            dry_run: If True, don't actually make changes

        Returns:
            FixResult with outcome
        """
        raise NotImplementedError

    def apply_fixes_batch(
        self,
        issues: List[LintIssue],
        dry_run: bool = False
    ) -> List[FixResult]:
        """Apply fixes for multiple issues"""
        results = []
        for issue in issues:
            result = self.apply_fix(issue, dry_run)
            results.append(result)
        return results

    def suggest_manual_fix(self, issue: LintIssue) -> str:
        """Provide suggestion for manual fix"""
        raise NotImplementedError


class ESLintFixApplier(BaseFixApplier):
    """
    Apply ESLint fixes.

    Uses --fix flag for auto-fixable issues.
    """

    def __init__(self):
        super().__init__("eslint")
        self.autofixable_rules = self._get_autofixable_rules()

    def _get_autofixable_rules(self) -> set:
        """
        Get set of auto-fixable ESLint rules.

        In practice, we'd query ESLint, but for now use common ones.
        """
        return {
            "semi",
            "quotes",
            "comma-dangle",
            "no-extra-semi",
            "no-multi-spaces",
            "space-before-blocks",
            "keyword-spacing",
            "object-curly-spacing",
            "array-bracket-spacing",
            "eol-last",
            "no-trailing-spaces",
            "indent",
            "arrow-spacing",
            "prefer-const",
            "no-var"
        }

    def can_autofix(self, issue: LintIssue) -> bool:
        """Check if ESLint can auto-fix this rule"""
        return issue.rule in self.autofixable_rules or issue.has_autofix

    def apply_fix(self, issue: LintIssue, dry_run: bool = False) -> FixResult:
        """Apply ESLint fix"""

        if not self.can_autofix(issue):
            # Provide manual suggestion
            suggestion = self.suggest_manual_fix(issue)
            return FixResult(
                issue=issue,
                success=False,
                method="manual_suggestion",
                changes_made=None,
                error=None
            )

        if dry_run:
            return FixResult(
                issue=issue,
                success=True,
                method="autofix",
                changes_made="Would fix with ESLint --fix"
            )

        # Run ESLint --fix on specific file
        try:
            result = subprocess.run(
                ["npx", "eslint", "--fix", issue.file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            return FixResult(
                issue=issue,
                success=result.returncode == 0,
                method="autofix",
                changes_made=f"ESLint --fix applied to {issue.file_path}"
            )

        except subprocess.TimeoutExpired:
            return FixResult(
                issue=issue,
                success=False,
                method="autofix",
                error="ESLint timeout"
            )
        except FileNotFoundError:
            return FixResult(
                issue=issue,
                success=False,
                method="autofix",
                error="ESLint not found (run npm install)"
            )

    def suggest_manual_fix(self, issue: LintIssue) -> str:
        """Suggest manual fix for ESLint issue"""

        # Extract variable name from message if present
        var_name = "variable"
        if "'" in issue.message:
            parts = issue.message.split("'")
            if len(parts) > 1:
                var_name = parts[1]

        suggestions = {
            "no-undef": f"Define '{var_name}' or import it",
            "no-unused-vars": f"Remove unused variable or prefix with _",
            "eqeqeq": "Use === instead of ==",
            "no-console": "Remove console.log or use a logger",
            "prefer-const": "Change 'let' to 'const' if variable never reassigned"
        }

        return suggestions.get(
            issue.rule,
            f"Manual fix required for {issue.rule}: {issue.message}"
        )


class PylintFixApplier(BaseFixApplier):
    """
    Apply Pylint fixes.

    Pylint doesn't have auto-fix, so we provide suggestions.
    Can integrate with autopep8/black for some fixes.
    """

    def __init__(self):
        super().__init__("pylint")

    def can_autofix(self, issue: LintIssue) -> bool:
        """
        Pylint itself doesn't auto-fix, but we can use other tools.

        Some formatting issues can be fixed with black/autopep8.
        """
        formatting_rules = {
            "missing-final-newline",
            "trailing-whitespace",
            "line-too-long",
            "bad-whitespace",
            "bad-indentation"
        }

        return issue.rule in formatting_rules

    def apply_fix(self, issue: LintIssue, dry_run: bool = False) -> FixResult:
        """Apply Pylint fix (via black/autopep8 if possible)"""

        if not self.can_autofix(issue):
            suggestion = self.suggest_manual_fix(issue)
            return FixResult(
                issue=issue,
                success=False,
                method="manual_suggestion",
                changes_made=suggestion
            )

        if dry_run:
            return FixResult(
                issue=issue,
                success=True,
                method="autofix",
                changes_made="Would format with black"
            )

        # Try black first
        try:
            result = subprocess.run(
                ["black", issue.file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return FixResult(
                    issue=issue,
                    success=True,
                    method="autofix",
                    changes_made=f"Formatted with black: {issue.file_path}"
                )

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try autopep8
        try:
            result = subprocess.run(
                ["autopep8", "--in-place", issue.file_path],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return FixResult(
                    issue=issue,
                    success=True,
                    method="autofix",
                    changes_made=f"Formatted with autopep8: {issue.file_path}"
                )

        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return FixResult(
            issue=issue,
            success=False,
            method="manual_suggestion",
            error="black/autopep8 not available"
        )

    def suggest_manual_fix(self, issue: LintIssue) -> str:
        """Suggest manual fix"""

        suggestions = {
            "unused-variable": "Remove variable or prefix with _",
            "unused-import": "Remove unused import",
            "invalid-name": f"Rename to follow naming conventions",
            "missing-docstring": "Add docstring to function/class",
            "too-many-arguments": "Reduce parameters or use config object",
            "no-else-return": "Remove else after return statement"
        }

        return suggestions.get(
            issue.rule,
            f"Manual fix required: {issue.message}"
        )


class TypeScriptFixApplier(BaseFixApplier):
    """
    Apply TypeScript fixes.

    TypeScript compiler doesn't auto-fix, but we can suggest fixes.
    """

    def __init__(self):
        super().__init__("typescript")

    def can_autofix(self, issue: LintIssue) -> bool:
        """TypeScript doesn't auto-fix"""
        return False

    def apply_fix(self, issue: LintIssue, dry_run: bool = False) -> FixResult:
        """TypeScript fixes are manual"""
        suggestion = self.suggest_manual_fix(issue)

        return FixResult(
            issue=issue,
            success=False,
            method="manual_suggestion",
            changes_made=suggestion
        )

    def suggest_manual_fix(self, issue: LintIssue) -> str:
        """Suggest TypeScript fix"""

        # Extract TS error code
        if issue.rule.startswith("TS"):
            code = issue.rule[2:]

            suggestions = {
                "2322": "Fix type mismatch - check assigned value type",
                "2345": "Fix argument type - check function parameter types",
                "2339": "Property doesn't exist - check object structure",
                "2304": "Cannot find name - import or define the type/variable",
                "2551": "Property doesn't exist - check for typos",
                "7006": "Add type annotation - implicit any"
            }

            suggestion = suggestions.get(code, f"Fix type error: {issue.message}")
            return suggestion

        return f"Manual fix required: {issue.message}"


class FixApplierFactory:
    """Factory for creating fix appliers"""

    _appliers = {
        "eslint": ESLintFixApplier,
        "pylint": PylintFixApplier,
        "typescript": TypeScriptFixApplier,
        "tsc": TypeScriptFixApplier,
        "mypy": PylintFixApplier  # Similar to Pylint (no autofix)
    }

    @classmethod
    def create(cls, linter_name: str) -> BaseFixApplier:
        """Create fix applier for linter"""
        applier_class = cls._appliers.get(linter_name.lower())

        if not applier_class:
            raise ValueError(
                f"Unsupported fix applier: {linter_name}. "
                f"Supported: {', '.join(cls._appliers.keys())}"
            )

        return applier_class()


def apply_fixes(
    linter_name: str,
    issues: List[LintIssue],
    dry_run: bool = False,
    auto_only: bool = False
) -> List[FixResult]:
    """
    Apply fixes for list of issues.

    Args:
        linter_name: Name of linter
        issues: List of issues to fix
        dry_run: Don't actually make changes
        auto_only: Only apply auto-fixable issues

    Returns:
        List of FixResult objects

    Example:
        >>> results = apply_fixes("eslint", issues, dry_run=True)
        >>> auto_fixed = [r for r in results if r.method == "autofix" and r.success]
        >>> print(f"Could auto-fix {len(auto_fixed)} issues")
    """
    applier = FixApplierFactory.create(linter_name)

    if auto_only:
        issues = [i for i in issues if applier.can_autofix(i)]

    return applier.apply_fixes_batch(issues, dry_run)


def group_issues_by_fixability(
    linter_name: str,
    issues: List[LintIssue]
) -> Dict[str, List[LintIssue]]:
    """
    Group issues by whether they can be auto-fixed.

    Args:
        linter_name: Name of linter
        issues: List of issues

    Returns:
        Dictionary with "auto_fixable" and "manual" keys
    """
    applier = FixApplierFactory.create(linter_name)

    auto_fixable = []
    manual = []

    for issue in issues:
        if applier.can_autofix(issue):
            auto_fixable.append(issue)
        else:
            manual.append(issue)

    return {
        "auto_fixable": auto_fixable,
        "manual": manual
    }
