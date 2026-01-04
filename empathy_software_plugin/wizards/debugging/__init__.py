"""Advanced Debugging Wizard - Sub-package

Protocol-based debugging using linting configuration pattern.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
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
    # Risk Analysis (Level 4)
    "BugRisk",
    "BugRiskAnalyzer",
    "ConfigLoaderFactory",
    "CrossLanguagePatternLibrary",
    "FixApplierFactory",
    # Fixing
    "FixResult",
    # Config
    "LintConfig",
    # Parsing
    "LintIssue",
    "LinterParserFactory",
    "PatternCategory",
    "RiskAssessment",
    "Severity",
    # Cross-Language Patterns (Level 5)
    "UniversalPattern",
    # Verification
    "VerificationResult",
    "apply_fixes",
    "compare_issue_lists",
    "get_pattern_library",
    "group_issues_by_fixability",
    "load_config",
    "parse_linter_output",
    "run_linter",
    "verify_fixes",
]
