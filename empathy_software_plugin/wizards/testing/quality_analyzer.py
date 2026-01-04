"""Test Quality Analyzer for Enhanced Testing Wizard

Analyzes test quality including flakiness detection, assertion quality,
test isolation, and execution performance.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any


class TestQualityIssue(Enum):
    """Types of test quality issues"""

    FLAKY = "flaky"  # Test has inconsistent results
    NO_ASSERTIONS = "no_assertions"  # Test doesn't verify anything
    WEAK_ASSERTIONS = "weak_assertions"  # Only uses assertTrue/assertFalse
    SLOW = "slow"  # Takes >1 second
    NOT_ISOLATED = "not_isolated"  # Depends on external state
    HARDCODED_VALUES = "hardcoded"  # Uses magic numbers/strings
    SLEEP_USAGE = "sleep_usage"  # Uses time.sleep()
    RANDOM_USAGE = "random_usage"  # Uses random without seed


@dataclass
class TestFunction:
    """Represents a single test function"""

    name: str
    file_path: str
    line_number: int
    assertions_count: int
    execution_time: float | None = None
    is_async: bool = False
    uses_fixtures: list[str] | None = None
    issues: list[TestQualityIssue] | None = None

    def __post_init__(self):
        if self.uses_fixtures is None:
            self.uses_fixtures = []
        if self.issues is None:
            self.issues = []

    @property
    def quality_score(self) -> float:
        """Calculate quality score (0-100)

        Factors:
        - Has assertions: +30
        - Good assertion count (2-10): +20
        - Fast (<1s): +20
        - No issues: +30
        """
        score = 0.0

        # Assertions
        if self.assertions_count > 0:
            score += 30
            if 2 <= self.assertions_count <= 10:
                score += 20
            elif self.assertions_count == 1:
                score += 10

        # Performance
        if self.execution_time is not None:
            if self.execution_time < 0.1:
                score += 20  # Very fast
            elif self.execution_time < 1.0:
                score += 15  # Fast enough
            elif self.execution_time < 5.0:
                score += 5  # Acceptable

        # Issues penalty
        issue_penalty = len(self.issues) * 10
        score = max(0, score + 30 - issue_penalty)

        return min(100.0, score)


@dataclass
class TestQualityReport:
    """Complete test quality analysis report"""

    total_tests: int
    high_quality_tests: int  # Score ≥80
    medium_quality_tests: int  # Score 50-79
    low_quality_tests: int  # Score <50
    flaky_tests: list[str]
    slow_tests: list[str]
    tests_without_assertions: list[str]
    isolated_tests: int
    average_quality_score: float
    issues_by_type: dict[TestQualityIssue, int]
    test_functions: dict[str, TestFunction]


class TestQualityAnalyzer:
    """Analyzes test code quality to identify improvements.

    Detects:
    - Flaky tests (timing-dependent, random, external state)
    - Missing or weak assertions
    - Slow tests
    - Poor isolation
    - Anti-patterns
    """

    def __init__(self):
        # Thresholds
        self.slow_threshold = 1.0  # seconds
        self.min_assertions = 1
        self.max_assertions = 20  # Too many might indicate test doing too much

        # Patterns for detection
        self.assertion_patterns = [
            r"assert\s+",
            r"assertEqual",
            r"assertTrue",
            r"assertFalse",
            r"assertIn",
            r"assertRaises",
            r"assertIsNone",
            r"assertIsNotNone",
            r"expect\(",
        ]

        self.flakiness_indicators = [
            (r"time\.sleep\(", TestQualityIssue.SLEEP_USAGE),
            (r"random\.", TestQualityIssue.RANDOM_USAGE),
            (r"datetime\.now\(\)", TestQualityIssue.NOT_ISOLATED),
            (r"uuid\.uuid4\(\)", TestQualityIssue.RANDOM_USAGE),
        ]

    def analyze_test_file(self, file_path: Path) -> list[TestFunction]:
        """Analyze a test file for quality issues

        Args:
            file_path: Path to test file

        Returns:
            List of TestFunction objects with issues identified

        """
        if not file_path.exists():
            raise FileNotFoundError(f"Test file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        return self._parse_test_functions(content, str(file_path))

    def _parse_test_functions(self, content: str, file_path: str) -> list[TestFunction]:
        """Parse test functions from file content"""
        test_functions = []
        lines = content.split("\n")

        # Find test function definitions
        test_func_pattern = re.compile(r"^(\s*)(async\s+)?def\s+(test_\w+)\s*\(")

        i = 0
        while i < len(lines):
            match = test_func_pattern.match(lines[i])
            if match:
                indent = len(match.group(1))
                is_async = match.group(2) is not None
                func_name = match.group(3)
                line_num = i + 1

                # Extract function body
                func_body, end_line = self._extract_function_body(lines, i, indent)

                # Analyze function
                test_func = self._analyze_test_function(
                    func_name,
                    file_path,
                    line_num,
                    func_body,
                    is_async,
                )
                test_functions.append(test_func)

                i = end_line
            else:
                i += 1

        return test_functions

    def _extract_function_body(
        self,
        lines: list[str],
        start_line: int,
        base_indent: int,
    ) -> tuple[str, int]:
        """Extract the body of a function"""
        body_lines = [lines[start_line]]
        i = start_line + 1

        while i < len(lines):
            line = lines[i]

            # Skip empty lines
            if not line.strip():
                body_lines.append(line)
                i += 1
                continue

            # Check indentation
            current_indent = len(line) - len(line.lstrip())

            # If less or equal indent and not empty, function ended
            if current_indent <= base_indent and line.strip():
                break

            body_lines.append(line)
            i += 1

        return "\n".join(body_lines), i

    def _analyze_test_function(
        self,
        func_name: str,
        file_path: str,
        line_num: int,
        func_body: str,
        is_async: bool,
    ) -> TestFunction:
        """Analyze a single test function"""
        issues: list[TestQualityIssue] = []

        # Count assertions
        assertions_count = self._count_assertions(func_body)

        # Check for no assertions
        if assertions_count == 0:
            issues.append(TestQualityIssue.NO_ASSERTIONS)

        # Check for weak assertions (only assertTrue/False)
        if self._has_only_weak_assertions(func_body):
            issues.append(TestQualityIssue.WEAK_ASSERTIONS)

        # Check for flakiness indicators
        for pattern, issue_type in self.flakiness_indicators:
            if re.search(pattern, func_body):
                if issue_type not in issues:
                    issues.append(issue_type)

        # Check for hardcoded values (magic numbers/strings)
        if self._has_hardcoded_values(func_body):
            issues.append(TestQualityIssue.HARDCODED_VALUES)

        # Extract fixtures used
        fixtures = self._extract_fixtures(func_body)

        return TestFunction(
            name=func_name,
            file_path=file_path,
            line_number=line_num,
            assertions_count=assertions_count,
            is_async=is_async,
            uses_fixtures=fixtures,
            issues=issues,
        )

    def _count_assertions(self, func_body: str) -> int:
        """Count number of assertions in function"""
        count = 0
        for pattern in self.assertion_patterns:
            matches = re.findall(pattern, func_body)
            count += len(matches)
        return count

    def _has_only_weak_assertions(self, func_body: str) -> bool:
        """Check if function only uses weak assertions (assertTrue/False)"""
        weak_assertions = re.findall(r"assert(True|False)\(", func_body)
        all_assertions = sum(
            len(re.findall(pattern, func_body)) for pattern in self.assertion_patterns
        )

        # If all assertions are weak and there are some
        return len(weak_assertions) == all_assertions and all_assertions > 0

    def _has_hardcoded_values(self, func_body: str) -> bool:
        """Detect hardcoded magic values"""
        # Look for literal numbers (except common ones like 0, 1, 2)
        magic_numbers = re.findall(r"\b[3-9]\d*\b", func_body)

        # Look for hardcoded strings that aren't test names or common words
        magic_strings = re.findall(r'["\']([a-zA-Z0-9]{10,})["\']', func_body)

        # Threshold: more than 3 magic values is suspicious
        return len(magic_numbers) + len(magic_strings) > 3

    def _extract_fixtures(self, func_body: str) -> list[str]:
        """Extract pytest fixtures used in function signature"""
        # Match function signature parameters
        sig_match = re.search(r"def\s+\w+\s*\(([^)]*)\)", func_body)
        if not sig_match:
            return []

        params = sig_match.group(1).split(",")
        fixtures = []

        for param in params:
            param = param.strip()
            # Skip 'self' and empty params
            if param and param != "self":
                # Extract parameter name (before type hint if any)
                fixture_name = param.split(":")[0].strip()
                fixtures.append(fixture_name)

        return fixtures

    def analyze_test_execution(self, test_results: list[dict[str, Any]]) -> list[TestFunction]:
        """Analyze test execution results (from pytest JSON report)

        Args:
            test_results: List of test result dicts with fields:
                - nodeid: test identifier
                - duration: execution time in seconds
                - outcome: passed/failed/skipped
                - call: execution details

        Returns:
            List of TestFunction objects with execution data

        """
        test_functions = []

        for result in test_results:
            # Parse nodeid (e.g., "tests/test_core.py::test_function_name")
            nodeid = str(result.get("nodeid", ""))
            parts = nodeid.split("::")

            if len(parts) < 2:
                continue

            file_path = parts[0]
            func_name = parts[1]

            duration = result.get("duration", 0.0)

            # Create basic TestFunction (would be enriched with code analysis)
            test_func = TestFunction(
                name=func_name,
                file_path=file_path,
                line_number=0,  # Would need code analysis to get this
                assertions_count=0,  # Would need code analysis
                execution_time=duration,
            )

            # Check if slow
            if duration > self.slow_threshold:
                test_func.issues.append(TestQualityIssue.SLOW)

            # Detect flakiness from multiple runs
            # (This would require historical data)

            test_functions.append(test_func)

        return test_functions

    def detect_flaky_tests(self, historical_results: list[list[dict[str, Any]]]) -> list[str]:
        """Detect flaky tests from historical test runs

        A test is considered flaky if it has inconsistent results across runs
        with the same code.

        Args:
            historical_results: List of test result lists from multiple runs

        Returns:
            List of test names that are flaky

        """
        if len(historical_results) < 2:
            return []

        # Track outcomes for each test
        test_outcomes: dict[str, list[str]] = {}

        for run_results in historical_results:
            for result in run_results:
                nodeid = result.get("nodeid", "")
                outcome = result.get("outcome", "unknown")

                if nodeid not in test_outcomes:
                    test_outcomes[nodeid] = []

                test_outcomes[nodeid].append(outcome)

        # Find tests with inconsistent outcomes
        flaky_tests = []

        for nodeid, outcomes in test_outcomes.items():
            # If outcomes vary, test is flaky
            unique_outcomes = set(outcomes)
            if len(unique_outcomes) > 1:
                # Exclude if only failed once (might be legitimate)
                fail_count = outcomes.count("failed")
                if fail_count > 1 or (fail_count == 1 and len(outcomes) > 2):
                    flaky_tests.append(nodeid)

        return flaky_tests

    def generate_quality_report(self, test_functions: list[TestFunction]) -> TestQualityReport:
        """Generate comprehensive quality report

        Args:
            test_functions: List of analyzed test functions

        Returns:
            TestQualityReport with statistics and categorization

        """
        high_quality = []
        medium_quality = []
        low_quality = []
        flaky_tests = []
        slow_tests = []
        no_assertions = []
        isolated_count = 0

        issues_by_type: dict[TestQualityIssue, int] = dict.fromkeys(TestQualityIssue, 0)

        test_functions_dict = {}

        for test_func in test_functions:
            quality_score = test_func.quality_score
            test_id = f"{test_func.file_path}::{test_func.name}"
            test_functions_dict[test_id] = test_func

            # Categorize by quality
            if quality_score >= 80:
                high_quality.append(test_id)
            elif quality_score >= 50:
                medium_quality.append(test_id)
            else:
                low_quality.append(test_id)

            # Track specific issues
            if TestQualityIssue.NO_ASSERTIONS in test_func.issues:
                no_assertions.append(test_id)

            if TestQualityIssue.SLOW in test_func.issues:
                slow_tests.append(test_id)

            if any(
                issue in test_func.issues
                for issue in [
                    TestQualityIssue.FLAKY,
                    TestQualityIssue.SLEEP_USAGE,
                    TestQualityIssue.RANDOM_USAGE,
                    TestQualityIssue.NOT_ISOLATED,
                ]
            ):
                flaky_tests.append(test_id)

            # Check isolation (no external dependencies)
            if TestQualityIssue.NOT_ISOLATED not in test_func.issues:
                isolated_count += 1

            # Count issues by type
            for issue in test_func.issues:
                issues_by_type[issue] += 1

        # Calculate average quality score
        if test_functions:
            avg_score = sum(tf.quality_score for tf in test_functions) / len(test_functions)
        else:
            avg_score = 0.0

        return TestQualityReport(
            total_tests=len(test_functions),
            high_quality_tests=len(high_quality),
            medium_quality_tests=len(medium_quality),
            low_quality_tests=len(low_quality),
            flaky_tests=flaky_tests,
            slow_tests=slow_tests,
            tests_without_assertions=no_assertions,
            isolated_tests=isolated_count,
            average_quality_score=avg_score,
            issues_by_type=issues_by_type,
            test_functions=test_functions_dict,
        )

    def generate_summary(self, report: TestQualityReport) -> str:
        """Generate human-readable quality summary"""
        summary = []
        summary.append("=" * 60)
        summary.append("TEST QUALITY ANALYSIS SUMMARY")
        summary.append("=" * 60)
        summary.append(f"Total Tests: {report.total_tests}")
        summary.append(f"Average Quality Score: {report.average_quality_score:.1f}/100")
        summary.append("")
        summary.append("Quality Distribution:")
        summary.append(f"  ✅ High (≥80):   {report.high_quality_tests} tests")
        summary.append(f"  ⚠️  Medium (50-79): {report.medium_quality_tests} tests")
        summary.append(f"  ❌ Low (<50):    {report.low_quality_tests} tests")
        summary.append("")

        if report.tests_without_assertions:
            summary.append(f"⚠️  Tests Without Assertions: {len(report.tests_without_assertions)}")
            for test_id in report.tests_without_assertions[:3]:
                summary.append(f"  - {test_id}")
            if len(report.tests_without_assertions) > 3:
                summary.append(f"  ... and {len(report.tests_without_assertions) - 3} more")
            summary.append("")

        if report.flaky_tests:
            summary.append(f"🔴 Potentially Flaky Tests: {len(report.flaky_tests)}")
            for test_id in report.flaky_tests[:3]:
                summary.append(f"  - {test_id}")
            if len(report.flaky_tests) > 3:
                summary.append(f"  ... and {len(report.flaky_tests) - 3} more")
            summary.append("")

        if report.slow_tests:
            summary.append(f"🐌 Slow Tests (>{self.slow_threshold}s): {len(report.slow_tests)}")
            for test_id in report.slow_tests[:3]:
                summary.append(f"  - {test_id}")
            if len(report.slow_tests) > 3:
                summary.append(f"  ... and {len(report.slow_tests) - 3} more")

        summary.append("=" * 60)

        return "\n".join(summary)
