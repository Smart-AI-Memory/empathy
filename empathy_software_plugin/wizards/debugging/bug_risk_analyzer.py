"""
Bug Risk Analyzer (Level 4)

Predicts which linting violations are likely to cause production bugs.

This is Level 4 Anticipatory Empathy - analyzing trajectory and alerting
to future problems before they happen.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from .linter_parsers import LintIssue


class BugRisk(Enum):
    """Bug risk levels"""

    CRITICAL = "critical"  # Will definitely cause runtime errors
    HIGH = "high"  # Very likely to cause bugs
    MEDIUM = "medium"  # May cause subtle bugs
    LOW = "low"  # Unlikely to cause bugs
    STYLE = "style"  # Style only, no bug risk


@dataclass
class RiskAssessment:
    """Risk assessment for a linting issue"""

    issue: LintIssue
    risk_level: BugRisk
    reasoning: str
    impact: str
    likelihood: float  # 0.0 to 1.0
    prevention_steps: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "issue": self.issue.to_dict(),
            "risk_level": self.risk_level.value,
            "reasoning": self.reasoning,
            "impact": self.impact,
            "likelihood": self.likelihood,
            "prevention_steps": self.prevention_steps,
        }


class BugRiskAnalyzer:
    """
    Analyzes linting violations to predict bug risk.

    This implements Level 4 Anticipatory Empathy by:
    1. Mapping violations to known bug patterns
    2. Predicting which issues will cause production failures
    3. Alerting developers BEFORE deployment
    4. Recommending prevention steps
    """

    def __init__(self):
        # Rule -> Risk mappings based on experience
        self.eslint_risk_patterns = self._get_eslint_patterns()
        self.pylint_risk_patterns = self._get_pylint_patterns()
        self.typescript_risk_patterns = self._get_typescript_patterns()

    def analyze(self, issues: list[LintIssue]) -> list[RiskAssessment]:
        """
        Analyze issues and return risk assessments.

        Args:
            issues: List of linting issues

        Returns:
            List of RiskAssessment objects, sorted by risk level
        """
        assessments = []

        for issue in issues:
            assessment = self._assess_issue(issue)
            assessments.append(assessment)

        # Sort by risk (critical first)
        risk_order = {
            BugRisk.CRITICAL: 0,
            BugRisk.HIGH: 1,
            BugRisk.MEDIUM: 2,
            BugRisk.LOW: 3,
            BugRisk.STYLE: 4,
        }

        assessments.sort(key=lambda a: risk_order[a.risk_level])

        return assessments

    def _assess_issue(self, issue: LintIssue) -> RiskAssessment:
        """Assess single issue"""

        # Route to appropriate pattern library
        if issue.linter == "eslint":
            patterns = self.eslint_risk_patterns
        elif issue.linter == "pylint":
            patterns = self.pylint_risk_patterns
        elif issue.linter in ["typescript", "tsc"]:
            patterns = self.typescript_risk_patterns
        elif issue.linter == "mypy":
            patterns = self.pylint_risk_patterns  # Similar
        else:
            patterns = {}

        # Get pattern for this rule
        pattern = patterns.get(
            issue.rule,
            {
                "risk": BugRisk.MEDIUM,
                "reasoning": "Unknown rule - assess manually",
                "impact": "Uncertain impact",
                "likelihood": 0.5,
                "prevention_steps": ["Review manually", "Check documentation"],
            },
        )

        return RiskAssessment(
            issue=issue,
            risk_level=pattern["risk"],
            reasoning=pattern["reasoning"],
            impact=pattern["impact"],
            likelihood=pattern["likelihood"],
            prevention_steps=pattern["prevention_steps"],
        )

    def _get_eslint_patterns(self) -> dict[str, dict]:
        """ESLint rule → bug risk patterns"""
        return {
            # CRITICAL - Guaranteed runtime errors
            "no-undef": {
                "risk": BugRisk.CRITICAL,
                "reasoning": "Undefined variable will throw ReferenceError at runtime",
                "impact": "Application crash when code path executes",
                "likelihood": 1.0,
                "prevention_steps": [
                    "Add import/require statement",
                    "Define variable before use",
                    "Check for typos in variable name",
                ],
            },
            "no-unreachable": {
                "risk": BugRisk.CRITICAL,
                "reasoning": "Code after return/throw never executes - logic error",
                "impact": "Expected functionality missing",
                "likelihood": 1.0,
                "prevention_steps": [
                    "Remove unreachable code",
                    "Move logic before return statement",
                ],
            },
            # HIGH - Very likely to cause bugs
            "eqeqeq": {
                "risk": BugRisk.HIGH,
                "reasoning": "Type coercion with == causes subtle comparison bugs",
                "impact": "Incorrect conditional logic, unexpected behavior",
                "likelihood": 0.8,
                "prevention_steps": [
                    "Use === for type-safe comparison",
                    "Explicitly convert types before comparison",
                ],
            },
            "no-constant-condition": {
                "risk": BugRisk.HIGH,
                "reasoning": "Constant condition in if/while likely logic error",
                "impact": "Dead code or infinite loop",
                "likelihood": 0.9,
                "prevention_steps": ["Review conditional logic", "Replace with actual condition"],
            },
            "no-dupe-keys": {
                "risk": BugRisk.HIGH,
                "reasoning": "Duplicate object keys - later value silently overwrites",
                "impact": "Lost data, incorrect object state",
                "likelihood": 0.9,
                "prevention_steps": ["Remove duplicate key", "Use unique property names"],
            },
            # MEDIUM - May cause subtle bugs
            "no-shadow": {
                "risk": BugRisk.MEDIUM,
                "reasoning": "Variable shadowing can cause confusion",
                "impact": "Using wrong variable in scope",
                "likelihood": 0.5,
                "prevention_steps": [
                    "Rename inner variable",
                    "Use distinct names for different scopes",
                ],
            },
            "no-implicit-coercion": {
                "risk": BugRisk.MEDIUM,
                "reasoning": "Implicit type coercion can cause unexpected results",
                "impact": "Type-related bugs in edge cases",
                "likelihood": 0.6,
                "prevention_steps": ["Use explicit type conversion", "Add type checks"],
            },
            # LOW - Unlikely to cause bugs
            "no-unused-vars": {
                "risk": BugRisk.LOW,
                "reasoning": "Unused variables rarely cause bugs, just clutter",
                "impact": "Code bloat, slight confusion",
                "likelihood": 0.1,
                "prevention_steps": [
                    "Remove unused variable",
                    "Prefix with _ if intentionally unused",
                ],
            },
            # STYLE - No bug risk
            "semi": {
                "risk": BugRisk.STYLE,
                "reasoning": "Missing semicolon - ASI handles it",
                "impact": "None (style preference)",
                "likelihood": 0.0,
                "prevention_steps": ["Add semicolon for consistency"],
            },
            "quotes": {
                "risk": BugRisk.STYLE,
                "reasoning": "Quote style has no functional impact",
                "impact": "None (style preference)",
                "likelihood": 0.0,
                "prevention_steps": ["Use consistent quote style"],
            },
        }

    def _get_pylint_patterns(self) -> dict[str, dict]:
        """Pylint rule → bug risk patterns"""
        return {
            # CRITICAL
            "undefined-variable": {
                "risk": BugRisk.CRITICAL,
                "reasoning": "Undefined variable will raise NameError",
                "impact": "Application crash",
                "likelihood": 1.0,
                "prevention_steps": ["Import missing module", "Define variable before use"],
            },
            "used-before-assignment": {
                "risk": BugRisk.CRITICAL,
                "reasoning": "Variable used before assignment raises UnboundLocalError",
                "impact": "Runtime error",
                "likelihood": 1.0,
                "prevention_steps": ["Initialize variable before use", "Check control flow logic"],
            },
            # HIGH
            "no-member": {
                "risk": BugRisk.HIGH,
                "reasoning": "Accessing non-existent attribute raises AttributeError",
                "impact": "Runtime error when code path executes",
                "likelihood": 0.8,
                "prevention_steps": [
                    "Check object has attribute",
                    "Use hasattr() or getattr()",
                    "Fix typo in attribute name",
                ],
            },
            "arguments-differ": {
                "risk": BugRisk.HIGH,
                "reasoning": "Method signature mismatch breaks contract",
                "impact": "Incorrect method calls, TypeError",
                "likelihood": 0.8,
                "prevention_steps": ["Match parent class signature", "Update all callers"],
            },
            # MEDIUM
            "dangerous-default-value": {
                "risk": BugRisk.MEDIUM,
                "reasoning": "Mutable default arguments share state",
                "impact": "Unexpected state persistence across calls",
                "likelihood": 0.7,
                "prevention_steps": ["Use None as default", "Initialize in function body"],
            },
            # LOW
            "unused-variable": {
                "risk": BugRisk.LOW,
                "reasoning": "Unused variable is just clutter",
                "impact": "Minimal - slight confusion",
                "likelihood": 0.1,
                "prevention_steps": ["Remove variable", "Prefix with _ if intentional"],
            },
            # STYLE
            "missing-docstring": {
                "risk": BugRisk.STYLE,
                "reasoning": "Missing documentation, not a bug",
                "impact": "None (documentation quality)",
                "likelihood": 0.0,
                "prevention_steps": ["Add docstring"],
            },
            "invalid-name": {
                "risk": BugRisk.STYLE,
                "reasoning": "Naming convention violation",
                "impact": "None (style preference)",
                "likelihood": 0.0,
                "prevention_steps": ["Rename to follow convention"],
            },
        }

    def _get_typescript_patterns(self) -> dict[str, dict]:
        """TypeScript error → bug risk patterns"""
        return {
            # CRITICAL
            "TS2304": {  # Cannot find name
                "risk": BugRisk.CRITICAL,
                "reasoning": "Undefined identifier will cause ReferenceError",
                "impact": "Runtime error",
                "likelihood": 1.0,
                "prevention_steps": ["Import missing type/variable", "Define before use"],
            },
            "TS2322": {  # Type mismatch
                "risk": BugRisk.HIGH,
                "reasoning": "Type mismatch often indicates logic error",
                "impact": "Incorrect value handling, potential runtime errors",
                "likelihood": 0.8,
                "prevention_steps": ["Fix type mismatch", "Add type conversion", "Review logic"],
            },
            "TS2345": {  # Argument type mismatch
                "risk": BugRisk.HIGH,
                "reasoning": "Wrong argument type causes incorrect behavior",
                "impact": "Function receives unexpected input",
                "likelihood": 0.8,
                "prevention_steps": ["Fix argument type", "Update function signature"],
            },
            "TS2339": {  # Property doesn't exist
                "risk": BugRisk.HIGH,
                "reasoning": "Accessing non-existent property",
                "impact": "undefined value, potential TypeError",
                "likelihood": 0.7,
                "prevention_steps": ["Add property to type", "Check property exists", "Fix typo"],
            },
        }

    def generate_summary(self, assessments: list[RiskAssessment]) -> dict[str, Any]:
        """
        Generate summary of risk assessments.

        This is the Level 4 alert format.
        """
        # Count by risk level
        by_risk = {
            BugRisk.CRITICAL: [],
            BugRisk.HIGH: [],
            BugRisk.MEDIUM: [],
            BugRisk.LOW: [],
            BugRisk.STYLE: [],
        }

        for assessment in assessments:
            by_risk[assessment.risk_level].append(assessment)

        # Calculate overall risk score
        risk_scores = {
            BugRisk.CRITICAL: 10,
            BugRisk.HIGH: 5,
            BugRisk.MEDIUM: 2,
            BugRisk.LOW: 0.5,
            BugRisk.STYLE: 0,
        }

        total_risk_score = sum(risk_scores[a.risk_level] for a in assessments)

        # Generate alert message
        critical_count = len(by_risk[BugRisk.CRITICAL])
        high_count = len(by_risk[BugRisk.HIGH])

        alert_level = "NONE"
        if critical_count > 0:
            alert_level = "CRITICAL"
        elif high_count > 0:
            alert_level = "HIGH"
        elif len(by_risk[BugRisk.MEDIUM]) > 5:
            alert_level = "MEDIUM"

        return {
            "total_issues": len(assessments),
            "by_risk_level": {
                "critical": critical_count,
                "high": high_count,
                "medium": len(by_risk[BugRisk.MEDIUM]),
                "low": len(by_risk[BugRisk.LOW]),
                "style": len(by_risk[BugRisk.STYLE]),
            },
            "total_risk_score": total_risk_score,
            "alert_level": alert_level,
            "top_risks": [a.to_dict() for a in assessments[:5]],  # Top 5
            "recommendation": self._generate_recommendation(
                critical_count, high_count, len(by_risk[BugRisk.MEDIUM])
            ),
        }

    def _generate_recommendation(self, critical: int, high: int, medium: int) -> str:
        """Generate Level 4 recommendation"""

        if critical > 0:
            return (
                f"ALERT: {critical} CRITICAL issues detected. "
                "In our experience, these will cause runtime errors. "
                "Fix before deployment to prevent production incidents."
            )

        if high > 0:
            return (
                f"WARNING: {high} HIGH-risk issues found. "
                "In our experience, these often lead to bugs in production. "
                "Recommend fixing before merge."
            )

        if medium > 5:
            return (
                f"NOTICE: {medium} MEDIUM-risk issues accumulating. "
                "While not critical, this volume suggests code quality trajectory "
                "that may lead to technical debt. Consider addressing soon."
            )

        return "Code quality looks good. No high-risk issues detected."
