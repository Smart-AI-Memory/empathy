"""
Advanced Debugging Wizard (Level 4)

Protocol-based debugging using linting configuration pattern.

Uses the same systematic approach as linting:
1. Load config (understand the rules)
2. Run linter (get complete issue list)
3. Systematically fix (work through the list)
4. Verify (re-run to confirm)

This implements Level 4 Anticipatory Empathy by:
- Predicting which violations will cause bugs
- Alerting to trajectory concerns
- Recommending prevention steps

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

import logging
from pathlib import Path
from typing import Any, Dict, List

from .base_wizard import BaseWizard
from .debugging.bug_risk_analyzer import BugRiskAnalyzer
from .debugging.config_loaders import load_config
from .debugging.fix_applier import apply_fixes, group_issues_by_fixability
from .debugging.language_patterns import get_pattern_library
from .debugging.linter_parsers import LintIssue, parse_linter_output
from .debugging.verification import verify_fixes

logger = logging.getLogger(__name__)


class AdvancedDebuggingWizard(BaseWizard):
    """
    Advanced Debugging Wizard - Level 4 Anticipatory

    Systematically debugs code using linting configuration pattern:
    - Parses linter output
    - Analyzes bug risk (Level 4)
    - Applies fixes systematically
    - Verifies fixes work
    - Learns cross-language patterns (Level 5)
    """

    def __init__(self):
        super().__init__()
        self.bug_analyzer = BugRiskAnalyzer()
        self.pattern_library = get_pattern_library()
        self._name = "Advanced Debugging Wizard"
        self._level = 4

    @property
    def name(self) -> str:
        """Wizard name"""
        return self._name

    @property
    def level(self) -> int:
        """Empathy level"""
        return self._level

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code using linting protocols.

        Context expects:
            - project_path: Path to project
            - linters: Dict of {linter_name: output_file_or_string}
            - configs: Dict of {linter_name: config_file} (optional)
            - auto_fix: bool (whether to apply auto-fixes)
            - verify: bool (whether to re-run linters)

        Returns:
            Analysis with issues, risk assessment, fixes, and verification
        """
        project_path = context.get("project_path", ".")
        linters = context.get("linters", {})
        configs = context.get("configs", {})
        auto_fix = context.get("auto_fix", False)
        verify = context.get("verify", False)

        if not linters:
            return {
                "error": "No linter outputs provided",
                "help": "Provide linters dict: {'eslint': 'output.json', ...}",
            }

        # Phase 1: Parse linter outputs
        all_issues = []
        linter_results = {}

        for linter_name, output_source in linters.items():
            logger.info(f"Parsing {linter_name} output...")

            # Check if output_source is a file or string
            if Path(output_source).exists():
                with open(output_source, "r") as f:
                    output = f.read()
            else:
                output = output_source

            issues = parse_linter_output(linter_name, output)
            all_issues.extend(issues)

            linter_results[linter_name] = {"total_issues": len(issues), "issues": issues}

        # Phase 2: Load configs (understand the rules)
        configs_loaded = {}
        for linter_name in linters.keys():
            config_file = configs.get(linter_name)
            config = load_config(linter_name, config_path=config_file, start_dir=project_path)

            if config:
                configs_loaded[linter_name] = {
                    "file": config.config_file,
                    "rules_count": len(config.rules),
                    "extends": config.extends,
                }

        # Phase 3: Risk analysis (Level 4 - Anticipatory)
        logger.info("Analyzing bug risks...")
        risk_assessments = self.bug_analyzer.analyze(all_issues)
        risk_summary = self.bug_analyzer.generate_summary(risk_assessments)

        # Phase 4: Group by fixability
        fixability_by_linter = {}
        for linter_name, result in linter_results.items():
            fixability = group_issues_by_fixability(linter_name, result["issues"])
            fixability_by_linter[linter_name] = {
                "auto_fixable": len(fixability["auto_fixable"]),
                "manual": len(fixability["manual"]),
            }

        # Phase 5: Apply fixes (if requested)
        fix_results = {}
        if auto_fix:
            logger.info("Applying auto-fixes...")

            for linter_name, result in linter_results.items():
                fixes = apply_fixes(linter_name, result["issues"], dry_run=False, auto_only=True)

                successful = [f for f in fixes if f.success]
                failed = [f for f in fixes if not f.success]

                fix_results[linter_name] = {
                    "attempted": len(fixes),
                    "successful": len(successful),
                    "failed": len(failed),
                }

        # Phase 6: Verification (if requested)
        verification_results = {}
        if verify:
            logger.info("Verifying fixes...")

            for linter_name, result in linter_results.items():
                verification = verify_fixes(linter_name, project_path, result["issues"])

                verification_results[linter_name] = verification.to_dict()

        # Phase 7: Cross-language insights (Level 5)
        cross_language_insights = self._generate_cross_language_insights(all_issues)

        # Phase 8: Trajectory analysis (Level 4)
        trajectory = self._analyze_trajectory(all_issues, risk_summary)

        # Build final result
        return {
            "issues_found": len(all_issues),
            "linters": linter_results,
            "configs": configs_loaded,
            # Level 4: Risk analysis
            "risk_assessment": risk_summary,
            # Fixability
            "fixability": fixability_by_linter,
            # Fixes applied (if auto_fix=True)
            "fixes": fix_results if auto_fix else None,
            # Verification (if verify=True)
            "verification": verification_results if verify else None,
            # Level 5: Cross-language patterns
            "cross_language_insights": cross_language_insights,
            # Level 4: Trajectory prediction
            "trajectory": trajectory,
            # Standard wizard outputs
            "predictions": self._generate_predictions(trajectory, risk_summary),
            "recommendations": self._generate_recommendations(
                risk_summary, fixability_by_linter, trajectory
            ),
            "patterns": cross_language_insights,
            "confidence": 0.9,
        }

    def _generate_cross_language_insights(self, issues: List[LintIssue]) -> List[Dict[str, Any]]:
        """
        Generate Level 5 cross-language insights.

        Find patterns that exist across multiple languages in this project.
        """
        insights = []

        # Group issues by language
        by_language = {}
        for issue in issues:
            lang = issue.linter
            if lang not in by_language:
                by_language[lang] = []
            by_language[lang].append(issue)

        # Find common patterns
        if len(by_language) >= 2:
            # Look for same pattern in different languages
            for issue in issues[:5]:  # Check top 5
                pattern = self.pattern_library.find_pattern_for_rule(issue.linter, issue.rule)

                if pattern:
                    # Check if this pattern appears in other languages
                    other_langs = [lang for lang in by_language.keys() if lang != issue.linter]

                    if other_langs:
                        insight = {
                            "pattern_name": pattern.name,
                            "found_in": issue.linter,
                            "also_applies_to": other_langs,
                            "description": pattern.description,
                            "universal_strategy": pattern.universal_fix_strategy,
                        }
                        insights.append(insight)

        return insights[:3]  # Top 3 insights

    def _analyze_trajectory(
        self, issues: List[LintIssue], risk_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze issue trajectory (Level 4).

        Predict where code quality is headed.
        """
        total_issues = len(issues)
        critical = risk_summary["by_risk_level"]["critical"]
        high = risk_summary["by_risk_level"]["high"]
        medium = risk_summary["by_risk_level"]["medium"]

        # Simple trajectory analysis
        # In real implementation, would compare with historical data
        trajectory_state = "stable"
        trajectory_concern = None

        if critical > 0:
            trajectory_state = "critical"
            trajectory_concern = (
                f"{critical} critical issues will cause production failures. "
                "Immediate action required."
            )
        elif high > 5:
            trajectory_state = "degrading"
            trajectory_concern = (
                f"{high} high-risk issues accumulating. "
                "In our experience, this volume leads to production bugs."
            )
        elif total_issues > 50:
            trajectory_state = "concerning"
            trajectory_concern = (
                f"{total_issues} total issues. "
                "Code quality trajectory suggests tech debt accumulation."
            )

        return {
            "state": trajectory_state,
            "total_issues": total_issues,
            "critical_issues": critical,
            "high_risk_issues": high,
            "concern": trajectory_concern,
            "recommendation": self._get_trajectory_recommendation(trajectory_state),
        }

    def _get_trajectory_recommendation(self, state: str) -> str:
        """Get recommendation based on trajectory state"""
        recommendations = {
            "critical": "Fix critical issues before deployment. Production failure likely.",
            "degrading": "Address high-risk issues soon. Trajectory suggests increasing bug density.",
            "concerning": "Consider code quality review. Volume of issues may indicate systemic issues.",
            "stable": "Code quality trajectory looks good. Continue current practices.",
        }
        return recommendations.get(state, "")

    def _generate_predictions(
        self, trajectory: Dict[str, Any], risk_summary: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate Level 4 predictions"""
        predictions = []

        # Predict based on critical issues
        if risk_summary["by_risk_level"]["critical"] > 0:
            predictions.append(
                {
                    "type": "production_failure_risk",
                    "severity": "critical",
                    "description": (
                        "Critical linting violations detected. "
                        "In our experience, these cause runtime errors."
                    ),
                    "prevention_steps": [
                        "Fix all critical issues before deployment",
                        "Add pre-commit hooks to catch these",
                        "Review why these weren't caught earlier",
                    ],
                }
            )

        # Predict based on high-risk accumulation
        high_risk = risk_summary["by_risk_level"]["high"]
        if high_risk > 5:
            predictions.append(
                {
                    "type": "bug_density_increase",
                    "severity": "high",
                    "description": (
                        f"{high_risk} high-risk issues found. "
                        "In our experience, this volume correlates with production bugs."
                    ),
                    "prevention_steps": [
                        "Prioritize high-risk fixes",
                        "Add linting to CI/CD",
                        "Consider pair programming for complex areas",
                    ],
                }
            )

        # Predict based on trajectory
        if trajectory["state"] in ["degrading", "concerning"]:
            predictions.append(
                {
                    "type": "technical_debt_accumulation",
                    "severity": "medium",
                    "description": trajectory["concern"],
                    "prevention_steps": [
                        "Schedule code quality review",
                        "Allocate time for systematic cleanup",
                        "Update coding standards documentation",
                    ],
                }
            )

        return predictions

    def _generate_recommendations(
        self, risk_summary: Dict[str, Any], fixability: Dict[str, Dict], trajectory: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Based on alert level
        alert_level = risk_summary["alert_level"]

        if alert_level == "CRITICAL":
            recommendations.append(
                f"🚨 CRITICAL: Fix {risk_summary['by_risk_level']['critical']} "
                "critical issues immediately"
            )

        if alert_level in ["CRITICAL", "HIGH"]:
            recommendations.append(
                f"⚠️  Address {risk_summary['by_risk_level']['high']} "
                "high-risk issues before merge"
            )

        # Based on fixability
        total_auto_fixable = sum(f["auto_fixable"] for f in fixability.values())

        if total_auto_fixable > 0:
            recommendations.append(
                f"✅ {total_auto_fixable} issues can be auto-fixed. " "Run with auto_fix=True"
            )

        # Based on trajectory
        if trajectory["state"] != "stable":
            recommendations.append(f"📊 Trajectory: {trajectory['recommendation']}")

        # General recommendations
        recommendations.append("🔧 Add pre-commit hooks to prevent future issues")

        recommendations.append("📝 Document common patterns in team style guide")

        return recommendations
