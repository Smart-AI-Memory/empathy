"""
Cross-Language Pattern Library (Level 5)

Universal debugging patterns that apply across programming languages.

This is Level 5 Systems Empathy - recognizing that the same fundamental
patterns appear across different domains (languages).

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class PatternCategory(Enum):
    """Categories of universal patterns"""

    UNDEFINED_REFERENCE = "undefined_reference"
    TYPE_MISMATCH = "type_mismatch"
    NULL_SAFETY = "null_safety"
    UNUSED_CODE = "unused_code"
    NAMING_CONVENTION = "naming_convention"
    CODE_COMPLEXITY = "code_complexity"
    RESOURCE_MANAGEMENT = "resource_management"
    SECURITY = "security"


@dataclass
class UniversalPattern:
    """
    A pattern that exists across languages.

    Example: "Undefined variable" exists in JavaScript, Python, Rust, Go, etc.
    The fix strategy is similar across all languages.
    """

    name: str
    category: PatternCategory
    description: str
    why_it_matters: str
    language_manifestations: dict[str, str]  # language -> rule name
    universal_fix_strategy: str
    language_specific_fixes: dict[str, list[str]]


class CrossLanguagePatternLibrary:
    """
    Library of patterns that exist across languages.

    This enables Level 5 Systems Empathy - learning from one language
    can inform debugging in another language.
    """

    def __init__(self):
        self.patterns = self._build_pattern_library()

    def _build_pattern_library(self) -> dict[str, UniversalPattern]:
        """Build the universal pattern library"""
        return {
            "undefined_reference": UniversalPattern(
                name="Undefined Reference",
                category=PatternCategory.UNDEFINED_REFERENCE,
                description="Attempting to use a variable/function/type that doesn't exist",
                why_it_matters="Guaranteed runtime error in all languages. Most critical issue.",
                language_manifestations={
                    "javascript": "no-undef",
                    "python": "undefined-variable",
                    "typescript": "TS2304",
                    "rust": "cannot_find_value",
                    "go": "undefined",
                    "java": "cannot_find_symbol",
                },
                universal_fix_strategy=(
                    "1. Import/require the missing identifier\n"
                    "2. Define it before use\n"
                    "3. Check for typos in name"
                ),
                language_specific_fixes={
                    "javascript": [
                        "Add: import { foo } from './module'",
                        "Add: const foo = require('./module')",
                        "Define: const foo = ...",
                    ],
                    "python": [
                        "Add: from module import foo",
                        "Add: import module",
                        "Define: foo = ...",
                    ],
                    "typescript": [
                        "Add: import { Foo } from './types'",
                        "Define: type Foo = ...",
                        "Define: const foo = ...",
                    ],
                },
            ),
            "type_mismatch": UniversalPattern(
                name="Type Mismatch",
                category=PatternCategory.TYPE_MISMATCH,
                description="Value of wrong type assigned or passed",
                why_it_matters="Causes runtime errors or incorrect behavior",
                language_manifestations={
                    "typescript": "TS2322",
                    "python": "mypy: Incompatible types",
                    "rust": "mismatched_types",
                    "go": "cannot_use",
                    "java": "incompatible_types",
                },
                universal_fix_strategy=(
                    "1. Convert value to expected type\n"
                    "2. Change variable type to match value\n"
                    "3. Review logic - may indicate design issue"
                ),
                language_specific_fixes={
                    "typescript": [
                        "Add type conversion: String(value)",
                        "Fix type annotation: foo: ExpectedType",
                        "Use type assertion: value as ExpectedType",
                    ],
                    "python": [
                        "Convert: str(value), int(value)",
                        "Fix type hint: foo: ExpectedType",
                        "Use cast: cast(ExpectedType, value)",
                    ],
                },
            ),
            "null_safety": UniversalPattern(
                name="Null/Undefined Safety",
                category=PatternCategory.NULL_SAFETY,
                description="Potential null/undefined dereference",
                why_it_matters="Common source of production crashes",
                language_manifestations={
                    "javascript": "no-unsafe-optional-chaining",
                    "typescript": "TS2532",  # Object is possibly undefined
                    "python": "none-check",
                    "rust": "Option handling",
                    "java": "NullPointerException warnings",
                    "kotlin": "nullable type",
                },
                universal_fix_strategy=(
                    "1. Check for null/undefined before use\n"
                    "2. Provide default value\n"
                    "3. Use language's null-safety features"
                ),
                language_specific_fixes={
                    "javascript": [
                        "Use optional chaining: obj?.property",
                        "Nullish coalescing: value ?? default",
                        "Explicit check: if (value !== null)",
                    ],
                    "typescript": [
                        "Non-null assertion: value!",
                        "Optional chaining: obj?.property",
                        "Type guard: if (value !== undefined)",
                    ],
                    "python": [
                        "Check: if value is not None",
                        "Default: value or default_value",
                        "Optional type: Optional[Type]",
                    ],
                    "rust": [
                        "Pattern match: match opt { Some(v) => ..., None => ... }",
                        "Unwrap with default: opt.unwrap_or(default)",
                        "Safe access: opt.as_ref()",
                    ],
                },
            ),
            "unused_code": UniversalPattern(
                name="Unused Code",
                category=PatternCategory.UNUSED_CODE,
                description="Variables, imports, or functions that are never used",
                why_it_matters="Clutter, indicates incomplete refactoring",
                language_manifestations={
                    "javascript": "no-unused-vars",
                    "python": "unused-variable",
                    "typescript": "TS6133",
                    "rust": "unused_variables",
                    "go": "unused",
                    "java": "unused",
                },
                universal_fix_strategy=(
                    "1. Remove if truly unused\n"
                    "2. Prefix with _ if intentionally unused\n"
                    "3. Use it or lose it"
                ),
                language_specific_fixes={
                    "javascript": [
                        "Remove: Delete unused variable",
                        "Intentional: Prefix with _unused",
                        "Destructure: Use _ for unused items",
                    ],
                    "python": [
                        "Remove: Delete unused variable",
                        "Intentional: _unused = value",
                        "Noqa comment: # noqa: F841",
                    ],
                    "rust": [
                        "Remove: Delete binding",
                        "Intentional: let _unused = value",
                        "Attribute: #[allow(unused_variables)]",
                    ],
                },
            ),
            "naming_convention": UniversalPattern(
                name="Naming Convention Violation",
                category=PatternCategory.NAMING_CONVENTION,
                description="Identifier doesn't follow language conventions",
                why_it_matters="Consistency, readability, team standards",
                language_manifestations={
                    "javascript": "camelcase",
                    "python": "invalid-name",
                    "rust": "non_snake_case",
                    "go": "golint naming",
                    "java": "naming-convention",
                },
                universal_fix_strategy=(
                    "1. Rename to follow convention\n"
                    "2. Update all references\n"
                    "3. Consider IDE refactor tool"
                ),
                language_specific_fixes={
                    "javascript": [
                        "camelCase for variables/functions",
                        "PascalCase for classes",
                        "UPPER_CASE for constants",
                    ],
                    "python": [
                        "snake_case for variables/functions",
                        "PascalCase for classes",
                        "UPPER_CASE for constants",
                    ],
                    "rust": [
                        "snake_case for variables/functions",
                        "PascalCase for types/traits",
                        "SCREAMING_SNAKE_CASE for constants",
                    ],
                },
            ),
            "code_complexity": UniversalPattern(
                name="Excessive Complexity",
                category=PatternCategory.CODE_COMPLEXITY,
                description="Function/class too complex (cyclomatic complexity)",
                why_it_matters="Hard to test, maintain, understand",
                language_manifestations={
                    "javascript": "complexity",
                    "python": "too-many-branches",
                    "java": "CyclomaticComplexity",
                    "go": "gocyclo",
                },
                universal_fix_strategy=(
                    "1. Extract helper functions\n"
                    "2. Simplify conditional logic\n"
                    "3. Use early returns\n"
                    "4. Consider design patterns"
                ),
                language_specific_fixes={
                    "javascript": [
                        "Extract function: function helper() { ... }",
                        "Use guard clauses: if (!valid) return",
                        "Strategy pattern for complex conditionals",
                    ],
                    "python": [
                        "Extract method: def _helper(self):",
                        "Use guard clauses: if not valid: return",
                        "Lookup tables instead of if-else chains",
                    ],
                },
            ),
        }

    def find_pattern_for_rule(self, linter: str, rule: str) -> UniversalPattern | None:
        """
        Find universal pattern that matches this linter rule.

        Args:
            linter: Linter name (eslint, pylint, etc.)
            rule: Rule name

        Returns:
            UniversalPattern if found, None otherwise
        """
        for pattern in self.patterns.values():
            if linter in pattern.language_manifestations:
                if pattern.language_manifestations[linter] == rule:
                    return pattern
        return None

    def get_fix_strategy(self, pattern_name: str, language: str) -> list[str] | None:
        """
        Get language-specific fix strategy for pattern.

        Args:
            pattern_name: Name of universal pattern
            language: Target language

        Returns:
            List of fix steps, or None if not found
        """
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            return None

        return pattern.language_specific_fixes.get(language)

    def suggest_cross_language_insight(
        self, from_language: str, to_language: str, pattern_name: str
    ) -> str | None:
        """
        Generate insight from one language to another.

        This is Level 5 in action - cross-domain learning.

        Example: "This Python 'undefined-variable' error is like
        JavaScript's 'no-undef' - same fix applies."
        """
        pattern = self.patterns.get(pattern_name)
        if not pattern:
            return None

        from_rule = pattern.language_manifestations.get(from_language)
        to_rule = pattern.language_manifestations.get(to_language)

        if not from_rule or not to_rule:
            return None

        return (
            f"Cross-language insight: This {to_language} '{to_rule}' issue "
            f"is the same pattern as {from_language}'s '{from_rule}'.\n\n"
            f"Pattern: {pattern.name}\n"
            f"{pattern.description}\n\n"
            f"Universal strategy:\n{pattern.universal_fix_strategy}\n\n"
            f"Specific to {to_language}:\n"
            + "\n".join(
                f"  - {step}" for step in pattern.language_specific_fixes.get(to_language, [])
            )
        )

    def get_all_patterns(self) -> list[UniversalPattern]:
        """Get all universal patterns"""
        return list(self.patterns.values())

    def get_patterns_by_category(self, category: PatternCategory) -> list[UniversalPattern]:
        """Get patterns in specific category"""
        return [p for p in self.patterns.values() if p.category == category]

    def generate_pattern_summary(self) -> dict[str, Any]:
        """
        Generate summary of pattern library.

        Useful for documentation or teaching.
        """
        return {
            "total_patterns": len(self.patterns),
            "categories": {
                cat.value: len(self.get_patterns_by_category(cat)) for cat in PatternCategory
            },
            "languages_covered": self._count_languages(),
            "patterns": [
                {
                    "name": p.name,
                    "category": p.category.value,
                    "languages": list(p.language_manifestations.keys()),
                    "why_it_matters": p.why_it_matters,
                }
                for p in self.patterns.values()
            ],
        }

    def _count_languages(self) -> int:
        """Count unique languages covered"""
        languages = set()
        for pattern in self.patterns.values():
            languages.update(pattern.language_manifestations.keys())
        return len(languages)


# Global pattern library instance
PATTERN_LIBRARY = CrossLanguagePatternLibrary()


def get_pattern_library() -> CrossLanguagePatternLibrary:
    """Get the global pattern library"""
    return PATTERN_LIBRARY
