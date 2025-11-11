"""
Advanced Debugging Wizard - Sub-package

Protocol-based debugging using linting configuration pattern.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from .bug_risk_analyzer import BugRisk, BugRiskAnalyzer, RiskAssessment
from .config_loaders import ConfigLoaderFactory, LintConfig, load_config
from .fix_applier import FixApplierFactory, FixResult, apply_fixes, group_issues_by_fixability
from .language_patterns import (
    CrossLanguagePatternLibrary,
    PatternCategory,
    UniversalPattern,
    get_pattern_library,
)
from .linter_parsers import LinterParserFactory, LintIssue, Severity, parse_linter_output
from .verification import VerificationResult, compare_issue_lists, run_linter, verify_fixes

__all__ = [
    # Parsing
    "LintIssue",
    "Severity",
    "parse_linter_output",
    "LinterParserFactory",
    # Config
    "LintConfig",
    "load_config",
    "ConfigLoaderFactory",
    # Fixing
    "FixResult",
    "apply_fixes",
    "group_issues_by_fixability",
    "FixApplierFactory",
    # Verification
    "VerificationResult",
    "run_linter",
    "verify_fixes",
    "compare_issue_lists",
    # Risk Analysis (Level 4)
    "BugRisk",
    "RiskAssessment",
    "BugRiskAnalyzer",
    # Cross-Language Patterns (Level 5)
    "UniversalPattern",
    "PatternCategory",
    "CrossLanguagePatternLibrary",
    "get_pattern_library",
]
