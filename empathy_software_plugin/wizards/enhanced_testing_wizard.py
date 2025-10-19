"""
Enhanced Testing Wizard (Level 4)

Goes beyond test coverage to analyze test QUALITY and predict which untested code will cause bugs.

Level 4: Anticipatory - predicts which missing tests will cause production issues.

Copyright 2025 Deep Study AI, LLC
Licensed under the Apache License, Version 2.0
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import re
import logging

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


class EnhancedTestingWizard(BaseWizard):
    """
    Enhanced Testing Wizard - Level 4

    Beyond coverage metrics:
    - Test quality analysis (do tests actually catch bugs?)
    - Bug-risk prediction for untested code
    - Brittle test detection
    - Smart test suggestions based on risk
    """

    def __init__(self):
        super().__init__(
            name="Enhanced Testing Wizard",
            description="Test quality analysis and bug-risk prediction",
            level=4
        )

        # High-risk code patterns that need tests
        self.high_risk_patterns = {
            "error_handling": {
                "patterns": [r"try\s*:", r"except\s+\w+:", r"catch\s*\("],
                "risk": "HIGH",
                "reason": "Error paths often cause production failures"
            },
            "database_operations": {
                "patterns": [r"\.execute\(", r"\.query\(", r"\.save\(", r"\.update\("],
                "risk": "HIGH",
                "reason": "Database operations prone to edge case bugs"
            },
            "user_input": {
                "patterns": [r"request\.", r"input\(", r"readLine\("],
                "risk": "CRITICAL",
                "reason": "Unvalidated input leads to security issues"
            },
            "authentication": {
                "patterns": [r"login", r"authenticate", r"verify.*password"],
                "risk": "CRITICAL",
                "reason": "Auth bugs cause security breaches"
            },
            "financial_calculations": {
                "patterns": [r"price\s*=", r"total\s*=", r"amount\s*=", r"\.round\("],
                "risk": "HIGH",
                "reason": "Money calculations must be exact"
            }
        }

    async def analyze(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze test quality and coverage.

        Context expects:
            - project_path: Path to project
            - coverage_report: Coverage data (JSON or dict)
            - test_files: List of test file paths (optional)
            - source_files: List of source file paths (optional)

        Returns:
            Analysis with test quality, coverage gaps, bug risk predictions
        """
        project_path = context.get('project_path', '.')
        coverage_data = context.get('coverage_report', {})
        test_files = context.get('test_files', [])
        source_files = context.get('source_files', [])

        # Auto-discover if not provided
        if not source_files:
            source_files = self._discover_source_files(project_path)

        if not test_files:
            test_files = self._discover_test_files(project_path)

        # Phase 1: Analyze test coverage
        coverage_analysis = self._analyze_coverage(
            coverage_data,
            source_files
        )

        # Phase 2: Analyze test quality
        test_quality = self._analyze_test_quality(
            test_files,
            source_files
        )

        # Phase 3: Identify high-risk untested code (Level 4)
        risk_gaps = self._identify_risk_gaps(
            source_files,
            coverage_data
        )

        # Phase 4: Detect brittle tests
        brittle_tests = self._detect_brittle_tests(test_files)

        # Phase 5: Generate smart test suggestions (Level 4)
        test_suggestions = self._generate_test_suggestions(
            risk_gaps,
            coverage_analysis
        )

        # Phase 6: Predictions (Level 4)
        predictions = self._generate_predictions(
            risk_gaps,
            brittle_tests,
            coverage_analysis
        )

        # Phase 7: Recommendations
        recommendations = self._generate_recommendations(
            coverage_analysis,
            test_quality,
            risk_gaps
        )

        return {
            "coverage": coverage_analysis,
            "test_quality": test_quality,
            "risk_gaps": risk_gaps,
            "brittle_tests": brittle_tests,
            "test_suggestions": test_suggestions,

            # Standard wizard outputs
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": 0.85
        }

    def _discover_source_files(self, project_path: str) -> List[str]:
        """Discover source files in project"""
        source_files = []
        project = Path(project_path)

        # Python
        for file in project.rglob("*.py"):
            if "/test" not in str(file) and "_test.py" not in file.name:
                source_files.append(str(file))

        # JavaScript/TypeScript
        for ext in ["*.js", "*.ts", "*.jsx", "*.tsx"]:
            for file in project.rglob(ext):
                if "/test" not in str(file) and ".test." not in file.name and ".spec." not in file.name:
                    source_files.append(str(file))

        return source_files[:100]  # Limit for performance

    def _discover_test_files(self, project_path: str) -> List[str]:
        """Discover test files in project"""
        test_files = []
        project = Path(project_path)

        # Python tests
        for file in project.rglob("test_*.py"):
            test_files.append(str(file))
        for file in project.rglob("*_test.py"):
            test_files.append(str(file))

        # JavaScript/TypeScript tests
        for file in project.rglob("*.test.js"):
            test_files.append(str(file))
        for file in project.rglob("*.spec.ts"):
            test_files.append(str(file))

        return test_files

    def _analyze_coverage(
        self,
        coverage_data: Dict[str, Any],
        source_files: List[str]
    ) -> Dict[str, Any]:
        """Analyze test coverage"""

        if not coverage_data:
            return {
                "overall_coverage": 0,
                "line_coverage": 0,
                "branch_coverage": 0,
                "uncovered_files": len(source_files),
                "status": "no_coverage_data"
            }

        # Extract coverage metrics
        # Assuming coverage_data format: {filename: {lines_covered, lines_total, branches_covered, branches_total}}

        total_lines = 0
        covered_lines = 0
        total_branches = 0
        covered_branches = 0

        for file_path, metrics in coverage_data.items():
            total_lines += metrics.get("lines_total", 0)
            covered_lines += metrics.get("lines_covered", 0)
            total_branches += metrics.get("branches_total", 0)
            covered_branches += metrics.get("branches_covered", 0)

        line_coverage = (covered_lines / total_lines * 100) if total_lines > 0 else 0
        branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else 0

        return {
            "overall_coverage": (line_coverage + branch_coverage) / 2,
            "line_coverage": line_coverage,
            "branch_coverage": branch_coverage,
            "total_lines": total_lines,
            "covered_lines": covered_lines,
            "uncovered_lines": total_lines - covered_lines,
            "status": "analyzed"
        }

    def _analyze_test_quality(
        self,
        test_files: List[str],
        source_files: List[str]
    ) -> Dict[str, Any]:
        """Analyze test quality beyond coverage"""

        total_tests = len(test_files)
        assertions_found = 0
        tests_with_assertions = 0

        for test_file in test_files:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()

                    # Count assertions
                    assertion_count = len(re.findall(
                        r"assert|expect|should|toBe|toEqual|assertEqual",
                        content
                    ))

                    if assertion_count > 0:
                        tests_with_assertions += 1
                        assertions_found += assertion_count

            except Exception as e:
                logger.warning(f"Could not read test file {test_file}: {e}")

        # Test-to-source ratio
        ratio = total_tests / len(source_files) if source_files else 0

        return {
            "total_test_files": total_tests,
            "tests_with_assertions": tests_with_assertions,
            "total_assertions": assertions_found,
            "test_to_source_ratio": ratio,
            "quality_score": self._calculate_quality_score(
                total_tests,
                tests_with_assertions,
                assertions_found,
                ratio
            )
        }

    def _calculate_quality_score(
        self,
        total_tests: int,
        tests_with_assertions: int,
        assertions_found: int,
        ratio: float
    ) -> float:
        """Calculate overall test quality score (0-100)"""

        if total_tests == 0:
            return 0

        # Factor 1: Percentage of tests with assertions
        assertion_score = (tests_with_assertions / total_tests * 100) if total_tests > 0 else 0

        # Factor 2: Average assertions per test
        avg_assertions = assertions_found / total_tests if total_tests > 0 else 0
        assertion_depth_score = min(avg_assertions / 3 * 100, 100)  # 3+ assertions = 100

        # Factor 3: Test-to-source ratio
        ratio_score = min(ratio * 100, 100)  # 1:1 or better = 100

        # Weighted average
        quality_score = (
            assertion_score * 0.4 +
            assertion_depth_score * 0.3 +
            ratio_score * 0.3
        )

        return round(quality_score, 2)

    def _identify_risk_gaps(
        self,
        source_files: List[str],
        coverage_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Identify high-risk code that lacks tests.

        This is Level 4 - predicting which gaps will cause bugs.
        """

        risk_gaps = []

        for source_file in source_files[:50]:  # Limit for performance
            try:
                with open(source_file, 'r') as f:
                    content = f.read()

                # Check if file is covered
                is_covered = source_file in coverage_data

                # Check for high-risk patterns
                for pattern_name, pattern_info in self.high_risk_patterns.items():
                    for pattern in pattern_info["patterns"]:
                        matches = re.findall(pattern, content, re.IGNORECASE)

                        if matches and not is_covered:
                            risk_gaps.append({
                                "file": source_file,
                                "pattern": pattern_name,
                                "risk_level": pattern_info["risk"],
                                "reason": pattern_info["reason"],
                                "occurrences": len(matches),
                                "prediction": f"In our experience, untested {pattern_name} causes production bugs"
                            })
                            break  # One gap per file per pattern

            except Exception as e:
                logger.warning(f"Could not analyze {source_file}: {e}")

        # Sort by risk level
        risk_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        risk_gaps.sort(key=lambda x: risk_order.get(x["risk_level"], 4))

        return risk_gaps

    def _detect_brittle_tests(self, test_files: List[str]) -> List[Dict[str, Any]]:
        """Detect tests that are likely to break often"""

        brittle_tests = []

        brittle_patterns = {
            "sleep/wait": {
                "pattern": r"sleep\(|wait\(|setTimeout\(",
                "reason": "Timing-based tests are flaky"
            },
            "hardcoded_values": {
                "pattern": r"==\s*\d{10,}|===\s*\d{10,}",  # Long numbers
                "reason": "Hardcoded IDs/timestamps break easily"
            },
            "test_order_dependency": {
                "pattern": r"test.*order|sequential|beforeAll.*state",
                "reason": "Tests should be independent"
            }
        }

        for test_file in test_files[:50]:
            try:
                with open(test_file, 'r') as f:
                    content = f.read()

                for pattern_name, pattern_info in brittle_patterns.items():
                    if re.search(pattern_info["pattern"], content):
                        brittle_tests.append({
                            "file": test_file,
                            "pattern": pattern_name,
                            "reason": pattern_info["reason"]
                        })

            except Exception as e:
                logger.warning(f"Could not analyze {test_file}: {e}")

        return brittle_tests

    def _generate_test_suggestions(
        self,
        risk_gaps: List[Dict[str, Any]],
        coverage_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate smart test suggestions based on risk"""

        suggestions = []

        # Suggest tests for high-risk gaps first
        for gap in risk_gaps[:10]:  # Top 10
            suggestions.append({
                "priority": gap["risk_level"],
                "file": gap["file"],
                "test_type": f"Test {gap['pattern']}",
                "rationale": gap["reason"],
                "suggested_tests": self._suggest_specific_tests(gap["pattern"])
            })

        return suggestions

    def _suggest_specific_tests(self, pattern: str) -> List[str]:
        """Suggest specific tests for pattern"""

        test_templates = {
            "error_handling": [
                "Test with invalid input",
                "Test with network failure",
                "Test with timeout",
                "Verify error message clarity"
            ],
            "database_operations": [
                "Test with empty result set",
                "Test with duplicate keys",
                "Test with connection failure",
                "Test transaction rollback"
            ],
            "user_input": [
                "Test with malformed input",
                "Test with SQL injection attempt",
                "Test with XSS payload",
                "Test with empty/null input"
            ],
            "authentication": [
                "Test with invalid credentials",
                "Test with expired token",
                "Test with missing permissions",
                "Test session timeout"
            ],
            "financial_calculations": [
                "Test with edge case amounts (0, negative)",
                "Test rounding behavior",
                "Test currency conversion",
                "Test overflow/underflow"
            ]
        }

        return test_templates.get(pattern, ["Add comprehensive tests"])

    def _generate_predictions(
        self,
        risk_gaps: List[Dict[str, Any]],
        brittle_tests: List[Dict[str, Any]],
        coverage_analysis: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate Level 4 predictions"""

        predictions = []

        # Prediction 1: Critical risk gaps
        critical_gaps = [g for g in risk_gaps if g["risk_level"] == "CRITICAL"]
        if critical_gaps:
            predictions.append({
                "type": "production_bug_risk",
                "severity": "critical",
                "description": (
                    f"{len(critical_gaps)} critical code paths lack tests. "
                    f"In our experience, untested {critical_gaps[0]['pattern']} "
                    "causes production incidents."
                ),
                "affected_files": [g["file"] for g in critical_gaps[:5]],
                "prevention_steps": [
                    f"Add tests for {g['pattern']}" for g in critical_gaps[:3]
                ]
            })

        # Prediction 2: Brittle test maintenance burden
        if len(brittle_tests) > 5:
            predictions.append({
                "type": "test_maintenance_burden",
                "severity": "medium",
                "description": (
                    f"{len(brittle_tests)} brittle tests detected. "
                    "In our experience, these break often and slow development."
                ),
                "prevention_steps": [
                    "Refactor tests to remove timing dependencies",
                    "Use test fixtures instead of hardcoded values",
                    "Ensure test independence"
                ]
            })

        # Prediction 3: Low coverage trajectory
        if coverage_analysis["overall_coverage"] < 60:
            predictions.append({
                "type": "coverage_trajectory",
                "severity": "high",
                "description": (
                    f"Coverage at {coverage_analysis['overall_coverage']:.1f}%. "
                    "In our experience, projects below 70% see more production bugs."
                ),
                "prevention_steps": [
                    "Set coverage target of 70%+",
                    "Add pre-commit hooks to prevent coverage drops",
                    "Focus on high-risk code first"
                ]
            })

        return predictions

    def _generate_recommendations(
        self,
        coverage_analysis: Dict[str, Any],
        test_quality: Dict[str, Any],
        risk_gaps: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate actionable recommendations"""

        recommendations = []

        # Coverage recommendations
        coverage = coverage_analysis.get("overall_coverage", 0)
        if coverage < 70:
            recommendations.append(
                f"Increase coverage from {coverage:.1f}% to 70%+ (industry standard)"
            )

        # Quality recommendations
        quality_score = test_quality.get("quality_score", 0)
        if quality_score < 60:
            recommendations.append(
                f"Improve test quality score from {quality_score:.1f} to 60+"
            )

        # Risk-based recommendations
        critical_gaps = [g for g in risk_gaps if g["risk_level"] == "CRITICAL"]
        if critical_gaps:
            recommendations.append(
                f"URGENT: Add tests for {len(critical_gaps)} critical code paths"
            )

        high_risk_gaps = [g for g in risk_gaps if g["risk_level"] == "HIGH"]
        if high_risk_gaps:
            recommendations.append(
                f"HIGH PRIORITY: Test {len(high_risk_gaps)} high-risk areas"
            )

        # Test-to-source ratio
        ratio = test_quality.get("test_to_source_ratio", 0)
        if ratio < 0.5:
            recommendations.append(
                f"Add more test files (currently {ratio:.2f}:1, target 1:1)"
            )

        return recommendations
