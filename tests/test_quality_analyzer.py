"""Test Quality Analyzer

Tests the test quality analysis module for detecting test anti-patterns
and quality issues.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.testing.quality_analyzer import (
    TestFunction,
    TestQualityAnalyzer,
    TestQualityIssue,
    TestQualityReport,
)


class TestTestQualityIssue:
    """Test TestQualityIssue enum"""

    def test_quality_issue_values(self):
        """Test all quality issue enum values"""
        assert TestQualityIssue.FLAKY.value == "flaky"
        assert TestQualityIssue.NO_ASSERTIONS.value == "no_assertions"
        assert TestQualityIssue.WEAK_ASSERTIONS.value == "weak_assertions"
        assert TestQualityIssue.SLOW.value == "slow"
        assert TestQualityIssue.NOT_ISOLATED.value == "not_isolated"
        assert TestQualityIssue.HARDCODED_VALUES.value == "hardcoded"
        assert TestQualityIssue.SLEEP_USAGE.value == "sleep_usage"
        assert TestQualityIssue.RANDOM_USAGE.value == "random_usage"


class TestTestFunction:
    """Test TestFunction dataclass"""

    def test_test_function_creation(self):
        """Test creating a TestFunction"""
        test_func = TestFunction(
            name="test_example",
            file_path="tests/test_module.py",
            line_number=42,
            assertions_count=5,
            execution_time=0.5,
            is_async=False,
            uses_fixtures=["fixture1", "fixture2"],
            issues=[TestQualityIssue.SLOW],
        )

        assert test_func.name == "test_example"
        assert test_func.file_path == "tests/test_module.py"
        assert test_func.line_number == 42
        assert test_func.assertions_count == 5
        assert test_func.execution_time == 0.5
        assert test_func.is_async is False
        assert test_func.uses_fixtures == ["fixture1", "fixture2"]
        assert TestQualityIssue.SLOW in test_func.issues

    def test_test_function_defaults(self):
        """Test TestFunction default values"""
        test_func = TestFunction(
            name="test_minimal",
            file_path="test.py",
            line_number=1,
            assertions_count=1,
        )

        assert test_func.execution_time is None
        assert test_func.is_async is False
        assert test_func.uses_fixtures == []
        assert test_func.issues == []

    def test_quality_score_perfect(self):
        """Test quality score for perfect test"""
        test_func = TestFunction(
            name="test_perfect",
            file_path="test.py",
            line_number=1,
            assertions_count=5,  # Good count (2-10)
            execution_time=0.05,  # Very fast
            issues=[],  # No issues
        )

        # +30 (has assertions) +20 (good count) +20 (very fast) +30 (no issues)
        assert test_func.quality_score == 100.0

    def test_quality_score_with_assertions_bonus(self):
        """Test quality score calculations with different assertion counts"""
        # 1 assertion: +30 (has) +10 (one) = 40 base
        test_func_one = TestFunction(
            name="test_one_assertion",
            file_path="test.py",
            line_number=1,
            assertions_count=1,
            issues=[],
        )
        assert test_func_one.quality_score >= 40

        # 5 assertions (2-10 range): +30 (has) +20 (good count) = 50 base
        test_func_good = TestFunction(
            name="test_good_assertions",
            file_path="test.py",
            line_number=1,
            assertions_count=5,
            issues=[],
        )
        assert test_func_good.quality_score >= 50

    def test_quality_score_no_assertions(self):
        """Test quality score with no assertions"""
        test_func = TestFunction(
            name="test_no_assert",
            file_path="test.py",
            line_number=1,
            assertions_count=0,
            execution_time=0.1,
            issues=[TestQualityIssue.NO_ASSERTIONS],
        )

        # +0 (no assertions) +20 (fast) +30-10 (1 issue penalty) = 40
        assert test_func.quality_score <= 50.0

    def test_quality_score_performance_tiers(self):
        """Test quality score with different execution times"""
        # Very fast (<0.1s): +20
        test_fast = TestFunction(
            name="test_fast",
            file_path="test.py",
            line_number=1,
            assertions_count=5,
            execution_time=0.05,
            issues=[],
        )
        score_fast = test_fast.quality_score

        # Fast enough (<1s): +15
        test_medium = TestFunction(
            name="test_medium",
            file_path="test.py",
            line_number=1,
            assertions_count=5,
            execution_time=0.5,
            issues=[],
        )
        score_medium = test_medium.quality_score

        # Acceptable (<5s): +5
        test_acceptable = TestFunction(
            name="test_acceptable",
            file_path="test.py",
            line_number=1,
            assertions_count=5,
            execution_time=3.0,
            issues=[],
        )
        score_acceptable = test_acceptable.quality_score

        assert score_fast > score_medium > score_acceptable

    def test_quality_score_with_multiple_issues(self):
        """Test quality score with multiple issues"""
        test_func = TestFunction(
            name="test_bad",
            file_path="test.py",
            line_number=1,
            assertions_count=1,
            execution_time=2.0,
            issues=[
                TestQualityIssue.SLOW,
                TestQualityIssue.SLEEP_USAGE,
                TestQualityIssue.RANDOM_USAGE,
            ],
        )

        # 3 issues = 30 penalty, should significantly reduce score
        assert test_func.quality_score < 50.0

    def test_quality_score_minimum_zero(self):
        """Test quality score cannot go below zero"""
        test_func = TestFunction(
            name="test_terrible",
            file_path="test.py",
            line_number=1,
            assertions_count=0,
            execution_time=10.0,
            issues=[
                TestQualityIssue.NO_ASSERTIONS,
                TestQualityIssue.SLOW,
                TestQualityIssue.SLEEP_USAGE,
                TestQualityIssue.RANDOM_USAGE,
                TestQualityIssue.NOT_ISOLATED,
            ],
        )

        assert test_func.quality_score >= 0.0


class TestTestQualityReport:
    """Test TestQualityReport dataclass"""

    def test_quality_report_creation(self):
        """Test creating a TestQualityReport"""
        test_func = TestFunction(
            name="test_example",
            file_path="test.py",
            line_number=1,
            assertions_count=3,
        )

        report = TestQualityReport(
            total_tests=10,
            high_quality_tests=7,
            medium_quality_tests=2,
            low_quality_tests=1,
            flaky_tests=["test.py::test_flaky"],
            slow_tests=["test.py::test_slow"],
            tests_without_assertions=["test.py::test_no_assert"],
            isolated_tests=9,
            average_quality_score=75.5,
            issues_by_type={TestQualityIssue.SLOW: 1},
            test_functions={"test.py::test_example": test_func},
        )

        assert report.total_tests == 10
        assert report.high_quality_tests == 7
        assert report.average_quality_score == 75.5
        assert len(report.flaky_tests) == 1
        assert len(report.slow_tests) == 1


class TestTestQualityAnalyzer:
    """Test TestQualityAnalyzer functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create a TestQualityAnalyzer instance"""
        return TestQualityAnalyzer()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_analyzer_initialization(self, analyzer):
        """Test analyzer initialization with default values"""
        assert analyzer.slow_threshold == 1.0
        assert analyzer.min_assertions == 1
        assert analyzer.max_assertions == 20
        assert len(analyzer.assertion_patterns) > 0
        assert len(analyzer.flakiness_indicators) > 0

    def test_analyze_test_file_not_found(self, analyzer, temp_dir):
        """Test analyzing non-existent file"""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_test_file(temp_dir / "nonexistent.py")

    def test_analyze_simple_test_file(self, analyzer, temp_dir):
        """Test analyzing a simple test file"""
        test_content = '''
def test_example():
    """Test example function"""
    result = 42
    assert result == 42
    assert result > 0
'''
        test_file = temp_dir / "test_simple.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert test_functions[0].name == "test_example"
        assert test_functions[0].assertions_count >= 2
        assert test_functions[0].is_async is False

    def test_analyze_async_test(self, analyzer, temp_dir):
        """Test analyzing async test functions"""
        test_content = '''
async def test_async_example():
    """Async test"""
    result = await some_async_func()
    assert result is not None
'''
        test_file = temp_dir / "test_async.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert test_functions[0].is_async is True

    def test_detect_no_assertions(self, analyzer, temp_dir):
        """Test detecting tests without assertions"""
        test_content = '''
def test_no_assertions():
    """This test has no assertions"""
    x = 1 + 1
    print(x)
'''
        test_file = temp_dir / "test_no_assert.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert TestQualityIssue.NO_ASSERTIONS in test_functions[0].issues

    def test_detect_weak_assertions(self, analyzer, temp_dir):
        """Test detecting weak assertions (only assertTrue/False)"""
        test_content = '''
def test_weak_assertions():
    """Uses only weak assertions"""
    result = True
    assertTrue(result)
    assertFalse(not result)
'''
        test_file = temp_dir / "test_weak.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert TestQualityIssue.WEAK_ASSERTIONS in test_functions[0].issues

    def test_detect_sleep_usage(self, analyzer, temp_dir):
        """Test detecting time.sleep() usage"""
        test_content = '''
def test_with_sleep():
    """Test that uses time.sleep"""
    import time
    time.sleep(1)
    assert True
'''
        test_file = temp_dir / "test_sleep.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert TestQualityIssue.SLEEP_USAGE in test_functions[0].issues

    def test_detect_random_usage(self, analyzer, temp_dir):
        """Test detecting random usage without seed"""
        test_content = '''
def test_with_random():
    """Test using random"""
    import random
    x = random.randint(1, 10)
    assert x > 0
'''
        test_file = temp_dir / "test_random.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert TestQualityIssue.RANDOM_USAGE in test_functions[0].issues

    def test_detect_datetime_now_usage(self, analyzer, temp_dir):
        """Test detecting datetime.now() usage"""
        test_content = '''
def test_with_datetime_now():
    """Test using datetime.now()"""
    from datetime import datetime
    now = datetime.now()
    assert now is not None
'''
        test_file = temp_dir / "test_datetime.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert TestQualityIssue.NOT_ISOLATED in test_functions[0].issues

    def test_detect_hardcoded_values(self, analyzer, temp_dir):
        """Test detecting hardcoded magic values"""
        test_content = '''
def test_with_magic_values():
    """Test with many hardcoded values"""
    x = 42
    y = 123
    z = 456
    w = 789
    v = 321
    assert x + y + z + w + v == 1731
'''
        test_file = temp_dir / "test_magic.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        # Should detect hardcoded values (5 magic numbers > 3 threshold)
        assert TestQualityIssue.HARDCODED_VALUES in test_functions[0].issues

    def test_extract_fixtures(self, analyzer, temp_dir):
        """Test extracting pytest fixtures from function signature"""
        test_content = '''
def test_with_fixtures(fixture1, fixture2, fixture3):
    """Test using fixtures"""
    assert fixture1 is not None
'''
        test_file = temp_dir / "test_fixtures.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 1
        assert "fixture1" in test_functions[0].uses_fixtures
        assert "fixture2" in test_functions[0].uses_fixtures
        assert "fixture3" in test_functions[0].uses_fixtures

    def test_multiple_test_functions(self, analyzer, temp_dir):
        """Test parsing file with multiple test functions"""
        test_content = '''
def test_first():
    """First test"""
    assert True

def test_second():
    """Second test"""
    assert 1 == 1

def test_third():
    """Third test"""
    assert False or True
'''
        test_file = temp_dir / "test_multiple.py"
        test_file.write_text(test_content)

        test_functions = analyzer.analyze_test_file(test_file)

        assert len(test_functions) == 3
        assert test_functions[0].name == "test_first"
        assert test_functions[1].name == "test_second"
        assert test_functions[2].name == "test_third"

    def test_analyze_test_execution(self, analyzer):
        """Test analyzing test execution results"""
        test_results = [
            {
                "nodeid": "tests/test_core.py::test_fast",
                "duration": 0.05,
                "outcome": "passed",
            },
            {
                "nodeid": "tests/test_core.py::test_slow",
                "duration": 2.5,
                "outcome": "passed",
            },
        ]

        test_functions = analyzer.analyze_test_execution(test_results)

        assert len(test_functions) == 2
        assert test_functions[0].execution_time == 0.05
        assert test_functions[1].execution_time == 2.5
        # Slow test should be flagged
        assert TestQualityIssue.SLOW in test_functions[1].issues
        assert TestQualityIssue.SLOW not in test_functions[0].issues

    def test_detect_flaky_tests_insufficient_data(self, analyzer):
        """Test flaky detection with insufficient data"""
        historical_results = [[{"nodeid": "test.py::test_a", "outcome": "passed"}]]

        flaky = analyzer.detect_flaky_tests(historical_results)

        # Need at least 2 runs
        assert flaky == []

    def test_detect_flaky_tests_consistent_passes(self, analyzer):
        """Test flaky detection with consistent passes"""
        historical_results = [
            [{"nodeid": "test.py::test_stable", "outcome": "passed"}],
            [{"nodeid": "test.py::test_stable", "outcome": "passed"}],
            [{"nodeid": "test.py::test_stable", "outcome": "passed"}],
        ]

        flaky = analyzer.detect_flaky_tests(historical_results)

        assert "test.py::test_stable" not in flaky

    def test_detect_flaky_tests_inconsistent_results(self, analyzer):
        """Test detecting truly flaky tests"""
        historical_results = [
            [{"nodeid": "test.py::test_flaky", "outcome": "passed"}],
            [{"nodeid": "test.py::test_flaky", "outcome": "failed"}],
            [{"nodeid": "test.py::test_flaky", "outcome": "passed"}],
            [{"nodeid": "test.py::test_flaky", "outcome": "failed"}],
        ]

        flaky = analyzer.detect_flaky_tests(historical_results)

        assert "test.py::test_flaky" in flaky

    def test_detect_flaky_tests_single_failure_not_flaky(self, analyzer):
        """Test that single failure in only 2 runs doesn't mark test as flaky"""
        historical_results = [
            [{"nodeid": "test.py::test_mostly_passes", "outcome": "passed"}],
            [{"nodeid": "test.py::test_mostly_passes", "outcome": "failed"}],
        ]

        flaky = analyzer.detect_flaky_tests(historical_results)

        # Single failure in only 2 runs shouldn't be considered flaky
        # (might be legitimate failure, not flakiness)
        assert "test.py::test_mostly_passes" not in flaky

    def test_generate_quality_report(self, analyzer):
        """Test generating comprehensive quality report"""
        test_functions = [
            # High quality test
            TestFunction(
                name="test_high_quality",
                file_path="test.py",
                line_number=1,
                assertions_count=5,
                execution_time=0.1,
                issues=[],
            ),
            # Medium quality test
            TestFunction(
                name="test_medium_quality",
                file_path="test.py",
                line_number=10,
                assertions_count=2,
                execution_time=0.8,
                issues=[TestQualityIssue.HARDCODED_VALUES],
            ),
            # Low quality test
            TestFunction(
                name="test_low_quality",
                file_path="test.py",
                line_number=20,
                assertions_count=0,
                execution_time=3.0,
                issues=[TestQualityIssue.NO_ASSERTIONS, TestQualityIssue.SLOW],
            ),
        ]

        report = analyzer.generate_quality_report(test_functions)

        assert report.total_tests == 3
        assert report.high_quality_tests >= 1
        assert report.low_quality_tests >= 1
        assert len(report.tests_without_assertions) >= 1
        assert len(report.slow_tests) >= 1
        assert 0 <= report.average_quality_score <= 100

    def test_generate_summary(self, analyzer):
        """Test generating human-readable summary"""
        test_func1 = TestFunction(
            name="test_good",
            file_path="test.py",
            line_number=1,
            assertions_count=5,
            execution_time=0.1,
            issues=[],
        )
        test_func2 = TestFunction(
            name="test_bad",
            file_path="test.py",
            line_number=10,
            assertions_count=0,
            execution_time=2.0,
            issues=[TestQualityIssue.NO_ASSERTIONS, TestQualityIssue.SLOW],
        )

        report = analyzer.generate_quality_report([test_func1, test_func2])
        summary = analyzer.generate_summary(report)

        # Check key elements in summary
        assert "TEST QUALITY ANALYSIS SUMMARY" in summary
        assert "Total Tests:" in summary
        assert "Average Quality Score:" in summary
        assert "Quality Distribution:" in summary

    def test_count_assertions_various_types(self, analyzer):
        """Test counting different types of assertions"""
        func_body = """
        assert x == 42
        assertEqual(y, 100)
        assertTrue(condition)
        assertFalse(not_condition)
        assertIn(item, collection)
        assertRaises(ValueError, func)
        """

        count = analyzer._count_assertions(func_body)
        assert count >= 6

    def test_extract_function_body(self, analyzer):
        """Test extracting function body correctly"""
        lines = [
            "def test_example():",
            "    '''Docstring'''",
            "    x = 1",
            "    assert x == 1",
            "",
            "def another_function():",
        ]

        body, end_line = analyzer._extract_function_body(lines, 0, 0)

        # Should extract lines until next function
        assert "x = 1" in body
        assert "assert x == 1" in body
        assert end_line == 5  # Stops at next function

    def test_quality_report_with_flaky_and_slow_tests(self, analyzer):
        """Test quality report correctly categorizes flaky and slow tests"""
        test_functions = [
            TestFunction(
                name="test_flaky",
                file_path="test.py",
                line_number=1,
                assertions_count=3,
                issues=[TestQualityIssue.SLEEP_USAGE, TestQualityIssue.RANDOM_USAGE],
            ),
            TestFunction(
                name="test_slow",
                file_path="test.py",
                line_number=10,
                assertions_count=3,
                execution_time=5.0,
                issues=[TestQualityIssue.SLOW],
            ),
        ]

        report = analyzer.generate_quality_report(test_functions)

        assert len(report.flaky_tests) >= 1
        assert len(report.slow_tests) >= 1
        assert report.issues_by_type[TestQualityIssue.SLEEP_USAGE] == 1
        assert report.issues_by_type[TestQualityIssue.SLOW] == 1

    def test_isolated_tests_count(self, analyzer):
        """Test counting isolated vs non-isolated tests"""
        test_functions = [
            TestFunction(
                name="test_isolated",
                file_path="test.py",
                line_number=1,
                assertions_count=3,
                issues=[],  # No NOT_ISOLATED issue
            ),
            TestFunction(
                name="test_not_isolated",
                file_path="test.py",
                line_number=10,
                assertions_count=3,
                issues=[TestQualityIssue.NOT_ISOLATED],
            ),
        ]

        report = analyzer.generate_quality_report(test_functions)

        assert report.isolated_tests == 1
        assert report.total_tests == 2
