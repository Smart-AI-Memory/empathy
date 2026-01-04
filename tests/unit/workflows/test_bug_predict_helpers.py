"""Educational Tests for Bug Prediction Helper Functions

This test module demonstrates fundamental testing patterns:
1. File I/O mocking with tmp_path fixture
2. Configuration loading with fallback logic
3. Pattern matching and string manipulation
4. Parametrized testing for multiple scenarios
5. Edge case testing and boundary conditions

These helper functions are pure logic with no external dependencies,
making them ideal for learning unit testing fundamentals.

Learning Objectives:
- How to mock file system operations
- Testing configuration loading with multiple fallback paths
- Pattern matching test design (glob patterns, regex)
- Context-aware analysis testing
- False positive filtering in security scanning

Copyright 2025 Smart AI Memory, LLC
"""

import tempfile
from pathlib import Path

import pytest

# Import the helper functions we're testing
from empathy_os.workflows.bug_predict import (
    _has_problematic_exception_handlers,
    _is_acceptable_broad_exception,
    _is_dangerous_eval_usage,
    _load_bug_predict_config,
    _should_exclude_file,
)

# =============================================================================
# LESSON 1: Testing Configuration Loading with File I/O Mocking
# =============================================================================


@pytest.mark.unit
class TestLoadBugPredictConfig:
    """Educational tests for configuration loading.

    Key Learning Points:
    - Using tmp_path fixture for file system testing
    - Testing multiple fallback paths
    - Handling YAML parsing errors gracefully
    - Merging partial configs with defaults
    - Testing file-not-found scenarios
    """

    def test_returns_defaults_when_no_config_file_exists(self):
        """Test that defaults are returned when no config file is found.

        Teaching Pattern: Testing the "happy path" fallback behavior.
        When external dependencies aren't available, the system should
        gracefully fall back to sensible defaults.
        """
        # Arrange: Change to a directory with no config files
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = Path.cwd()
            try:
                Path(tmpdir).mkdir(parents=True, exist_ok=True)
                import os

                os.chdir(tmpdir)

                # Act: Load config from empty directory
                config = _load_bug_predict_config()

                # Assert: Should return default values
                assert config["risk_threshold"] == 0.7
                assert config["exclude_files"] == []
                assert "version" in config["acceptable_exception_contexts"]
                assert "config" in config["acceptable_exception_contexts"]
            finally:
                os.chdir(original_cwd)

    def test_loads_from_empathy_config_yml(self, tmp_path, monkeypatch):
        """Test loading from primary config file: empathy.config.yml

        Teaching Pattern: Using tmp_path fixture to create temporary files.
        This is the preferred way to test file I/O in pytest.
        """
        # Arrange: Create a config file with custom settings
        config_file = tmp_path / "empathy.config.yml"
        config_file.write_text(
            """
bug_predict:
  risk_threshold: 0.85
  exclude_files:
    - "**/test_*.py"
    - "**/fixtures/**"
  acceptable_exception_contexts:
    - version
    - config
""",
        )
        # Change to the temp directory
        monkeypatch.chdir(tmp_path)

        # Act: Load the config
        config = _load_bug_predict_config()

        # Assert: Custom values should be loaded
        assert config["risk_threshold"] == 0.85
        assert "**/test_*.py" in config["exclude_files"]
        assert "**/fixtures/**" in config["exclude_files"]
        assert "version" in config["acceptable_exception_contexts"]

    def test_tries_multiple_config_file_paths(self, tmp_path, monkeypatch):
        """Test that config loader tries multiple file paths in order.

        Teaching Pattern: Testing fallback logic with multiple paths.
        Real systems often try multiple locations for config files.
        """
        # Arrange: Create config in alternative location (.empathy.yml)
        config_file = tmp_path / ".empathy.yml"
        config_file.write_text(
            """
bug_predict:
  risk_threshold: 0.9
""",
        )
        monkeypatch.chdir(tmp_path)

        # Act
        config = _load_bug_predict_config()

        # Assert: Should find the .empathy.yml file
        assert config["risk_threshold"] == 0.9

    def test_handles_malformed_yaml_gracefully(self, tmp_path, monkeypatch):
        """Test that malformed YAML doesn't crash, falls back to defaults.

        Teaching Pattern: Testing error handling and graceful degradation.
        Production code should never crash on bad input - always have a fallback.
        """
        # Arrange: Create a config file with invalid YAML
        config_file = tmp_path / "empathy.config.yml"
        config_file.write_text(
            """
bug_predict:
  risk_threshold: 0.85
    invalid_indentation: this is broken
  - list item with wrong level
""",
        )
        monkeypatch.chdir(tmp_path)

        # Act: Load config despite bad YAML
        config = _load_bug_predict_config()

        # Assert: Should fall back to defaults without crashing
        assert config["risk_threshold"] == 0.7  # Default value
        assert config["exclude_files"] == []  # Default value

    def test_merges_partial_config_with_defaults(self, tmp_path, monkeypatch):
        """Test that partial configs are merged with defaults.

        Teaching Pattern: Testing merge logic - some fields custom, others default.
        This is common in configuration systems.
        """
        # Arrange: Config with only one custom field
        config_file = tmp_path / "empathy.config.yml"
        config_file.write_text(
            """
bug_predict:
  risk_threshold: 0.95
""",
        )
        monkeypatch.chdir(tmp_path)

        # Act
        config = _load_bug_predict_config()

        # Assert: Custom field is loaded, others are defaults
        assert config["risk_threshold"] == 0.95  # Custom
        assert config["exclude_files"] == []  # Default
        assert "version" in config["acceptable_exception_contexts"]  # Default


# =============================================================================
# LESSON 2: Testing Pattern Matching and String Manipulation
# =============================================================================


@pytest.mark.unit
class TestShouldExcludeFile:
    """Educational tests for glob pattern matching.

    Key Learning Points:
    - Parametrized testing for multiple test cases
    - Testing glob patterns (*, **, basename matching)
    - Edge cases: empty patterns, no matches, multiple patterns
    - Boundary conditions: exact matches, partial matches
    """

    @pytest.mark.parametrize(
        "file_path,pattern,expected",
        [
            # Simple glob patterns
            ("tests/test_foo.py", "**/test_*.py", True),
            ("src/main.py", "**/test_*.py", False),
            # Basename matching
            ("any/path/config.json", "config.json", True),
            ("src/config.json", "*.json", True),
            # Directory patterns with **
            ("src/fixtures/test.py", "**/fixtures/*", True),
            ("src/not_fixtures/test.py", "**/fixtures/*", False),
            ("fixtures/data.json", "fixtures/*", True),
            # Prefix patterns
            ("tests/unit/test_foo.py", "tests/**", True),
            ("src/unit/test_foo.py", "tests/**", False),
        ],
    )
    def test_pattern_matching(self, file_path, pattern, expected):
        """Test various glob pattern matching scenarios.

        Teaching Pattern: Parametrized testing - one test function, many cases.
        This is more maintainable than writing individual test functions.
        """
        result = _should_exclude_file(file_path, [pattern])
        assert (
            result == expected
        ), f"Pattern '{pattern}' should {'match' if expected else 'not match'} '{file_path}'"

    def test_no_exclusion_when_pattern_list_empty(self):
        """Test that empty pattern list excludes nothing.

        Teaching Pattern: Testing edge case - empty input.
        Always test with empty/null/zero inputs!
        """
        result = _should_exclude_file("any/file.py", [])
        assert result is False

    def test_first_matching_pattern_wins(self):
        """Test that matching stops at first match.

        Teaching Pattern: Testing early-exit logic.
        """
        patterns = [
            "**/test_*.py",  # This matches
            "**/skip_*.py",  # This doesn't matter
        ]
        result = _should_exclude_file("tests/test_foo.py", patterns)
        assert result is True

    def test_multiple_patterns_any_match_excludes(self):
        """Test that ANY pattern matching causes exclusion.

        Teaching Pattern: Testing OR logic (any match is sufficient).
        """
        patterns = [
            "**/test_*.py",
            "**/fixtures/*",
            "*.pyc",
        ]
        # Each of these should be excluded by at least one pattern
        assert _should_exclude_file("tests/test_foo.py", patterns) is True
        assert _should_exclude_file("data/fixtures/test.json", patterns) is True
        assert _should_exclude_file("build/module.pyc", patterns) is True

    def test_case_sensitive_matching(self):
        """Test that pattern matching is case-sensitive.

        Teaching Pattern: Testing case sensitivity assumptions.
        """
        result = _should_exclude_file("Tests/TEST_FOO.PY", ["**/test_*.py"])
        # Should NOT match because pattern is lowercase
        assert result is False


# =============================================================================
# LESSON 3: Testing Context-Aware Analysis
# =============================================================================


@pytest.mark.unit
class TestIsAcceptableBroadException:
    """Educational tests for context-based code analysis.

    Key Learning Points:
    - Testing functions that analyze surrounding code
    - Using lists to represent context (lines before/after)
    - Testing multiple conditional branches
    - Configurable behavior via parameters
    """

    def test_accepts_version_detection_with_fallback(self):
        """Test that version detection with fallback is acceptable.

        Teaching Pattern: Testing context-aware heuristics.
        The SAME exception pattern is good in some contexts, bad in others.
        """
        # Arrange
        line = "except Exception:"
        context_before = [
            "def get_version():",
            "    try:",
            "        return metadata.version('my-package')",
        ]
        context_after = [
            "        return 'dev'",  # Fallback to 'dev' version
        ]

        # Act
        result = _is_acceptable_broad_exception(line, context_before, context_after)

        # Assert: This is acceptable - version detection with graceful fallback
        assert result is True

    def test_accepts_config_loading_with_defaults(self):
        """Test that config loading with fallback to defaults is acceptable."""
        line = "except Exception:"
        context_before = [
            "try:",
            "    config = yaml.safe_load(f)",
        ]
        context_after = [
            "    pass  # Fall back to default config",
        ]

        result = _is_acceptable_broad_exception(line, context_before, context_after)
        assert result is True

    def test_accepts_optional_import_detection(self):
        """Test that optional import detection is acceptable."""
        line = "except Exception:"
        context_before = [
            "try:",
            "    import optional_library",
        ]
        context_after = [
            "    optional_library = None",
        ]

        result = _is_acceptable_broad_exception(line, context_before, context_after)
        assert result is True

    def test_accepts_cleanup_code_in_del(self):
        """Test that cleanup code in __del__ is acceptable."""
        line = "except Exception:"
        context_before = [
            "def __del__(self):",
            "    try:",
            "        self.cleanup()",
        ]
        context_after = [
            "        pass  # Ignore errors in cleanup",
        ]

        result = _is_acceptable_broad_exception(line, context_before, context_after)
        assert result is True

    def test_rejects_bare_exception_without_context(self):
        """Test that broad exception without justifying context is rejected.

        Teaching Pattern: Testing the negative case - what should be flagged.
        """
        line = "except Exception:"
        context_before = [
            "try:",
            "    result = process_data(data)",
        ]
        context_after = [
            "    print('Error occurred')",  # Just printing, not handling
        ]

        result = _is_acceptable_broad_exception(line, context_before, context_after)
        assert result is False

    def test_accepts_intentional_comment_justification(self):
        """Test that explicit comment justifying broad catch is acceptable.

        Teaching Pattern: Documentation as intent - comments can indicate
        that the developer knew what they were doing.
        """
        line = "except Exception:"
        context_before = [
            "try:",
            "    risky_operation()",
        ]
        context_after = [
            "    # Intentional broad catch - best effort operation",
            "    return None",
        ]

        result = _is_acceptable_broad_exception(line, context_before, context_after)
        assert result is True

    def test_respects_configurable_contexts(self):
        """Test that acceptable_contexts parameter is respected.

        Teaching Pattern: Testing configuration-driven behavior.
        """
        line = "except Exception:"
        context_before = ["try:", "    get_version()"]
        context_after = ["    return 'dev'"]

        # With 'version' in acceptable contexts
        assert (
            _is_acceptable_broad_exception(
                line,
                context_before,
                context_after,
                acceptable_contexts=["version"],
            )
            is True
        )

        # Without 'version' in acceptable contexts
        assert (
            _is_acceptable_broad_exception(
                line,
                context_before,
                context_after,
                acceptable_contexts=["config"],  # Only config, not version
            )
            is False
        )


# =============================================================================
# LESSON 4: Testing Security Pattern Detection
# =============================================================================


@pytest.mark.unit
class TestIsDangerousEvalUsage:
    """Educational tests for security vulnerability detection.

    Key Learning Points:
    - Testing security scanners
    - False positive filtering (detecting vs being vulnerable)
    - Distinguishing between detection code and vulnerable code
    - Testing regex pattern matching
    - Context-aware security analysis
    """

    def test_detects_real_eval_usage(self):
        """Test that real dangerous eval() usage is detected.

        Teaching Pattern: Testing the positive case - what SHOULD be flagged.
        """
        content = """
def dangerous_function(user_input):
    # This is dangerous!
    result = eval(user_input)
    return result
"""
        result = _is_dangerous_eval_usage(content, "src/vulnerable.py")
        assert result is True

    def test_ignores_eval_in_string_literal(self):
        """Test that eval() in string literals (detection code) is NOT flagged.

        Teaching Pattern: False positive filtering.
        Code that DETECTS vulnerabilities is not itself vulnerable.
        """
        content = """
def check_for_vulnerabilities(code):
    # This is DETECTION code, not vulnerable code
    if "eval(" in code:
        return "Dangerous eval usage found"
    return "OK"
"""
        result = _is_dangerous_eval_usage(content, "src/scanner.py")
        assert result is False

    def test_ignores_eval_in_comments(self):
        """Test that eval mentioned in comments is NOT flagged."""
        content = """
def safe_function():
    # SECURITY FIX: We removed eval() and use json.loads() instead
    data = json.loads(user_input)
    return data
"""
        result = _is_dangerous_eval_usage(content, "src/fixed.py")
        assert result is False

    def test_ignores_javascript_regex_exec(self):
        """Test that JavaScript regex.exec() is NOT flagged.

        Teaching Pattern: Language-aware detection.
        Same function name, different meaning in different languages.
        """
        content = """
const pattern = /test/;
const result = pattern.exec(text);  // This is safe - regex matching
"""
        result = _is_dangerous_eval_usage(content, "src/component.js")
        assert result is False

    def test_ignores_test_fixtures_with_eval(self):
        """Test that test fixtures containing eval (test data) are NOT flagged.

        Teaching Pattern: Distinguishing between test data and production code.
        """
        content = """
def test_scanner_detects_eval():
    # Creating test data with dangerous pattern
    bad_code = Path(tmpdir) / "bad.py"
    bad_code.write_text(\"\"\"
def bad_function(x):
    return eval(x)  # This is test data, not real code
\"\"\")

    result = scan_for_vulnerabilities(bad_code)
    assert "eval" in result.findings
"""
        result = _is_dangerous_eval_usage(content, "tests/test_scanner.py")
        assert result is False

    def test_ignores_scanner_test_files(self):
        """Test that scanner test files themselves are excluded.

        Teaching Pattern: Meta-exclusion - test files for security scanners
        deliberately contain examples of bad patterns.
        """
        content = """
# This test file contains examples of bad patterns
def test_detect_eval():
    assert eval("1+1") == 2  # Example of what we're testing for
"""
        # File name indicates it's a scanner test
        result = _is_dangerous_eval_usage(content, "tests/test_bug_predict.py")
        assert result is False

    def test_detects_exec_in_addition_to_eval(self):
        """Test that exec() is also detected (not just eval)."""
        content = """
def dangerous():
    exec(user_code)  # Also dangerous!
"""
        result = _is_dangerous_eval_usage(content, "src/bad.py")
        assert result is True

    def test_no_false_positive_on_file_without_eval(self):
        """Test that files without eval/exec are not flagged.

        Teaching Pattern: Testing the true negative - what should NOT be flagged.
        """
        content = """
def safe_function():
    result = json.loads(data)
    return result
"""
        result = _is_dangerous_eval_usage(content, "src/safe.py")
        assert result is False


# =============================================================================
# LESSON 5: Integration Test - Combining Multiple Helpers
# =============================================================================


@pytest.mark.unit
class TestHasProblematicExceptionHandlers:
    """Educational tests for the integration function.

    This function combines multiple helpers to perform analysis.

    Key Learning Points:
    - Testing functions that coordinate multiple helpers
    - End-to-end testing of a complete analysis
    - Testing with realistic code samples
    """

    def test_flags_problematic_exception_handler(self):
        """Test that truly problematic exception handlers are flagged."""
        content = """
def process_data(data):
    try:
        result = complex_operation(data)
    except Exception:
        print("Something went wrong")  # Bad: just printing, not handling
    return None
"""
        result = _has_problematic_exception_handlers(content, "src/bad.py")
        assert result is True

    def test_allows_version_detection_pattern(self):
        """Test that version detection pattern is allowed."""
        content = """
def get_version():
    try:
        return metadata.version('package')
    except Exception:
        return 'dev'  # Acceptable: version fallback
"""
        result = _has_problematic_exception_handlers(content, "src/version.py")
        assert result is False

    def test_no_flag_when_no_broad_exceptions_exist(self):
        """Test that files without broad exceptions are not flagged."""
        content = """
def safe_function():
    try:
        risky_operation()
    except ValueError as e:
        handle_value_error(e)
    except KeyError as e:
        handle_key_error(e)
"""
        result = _has_problematic_exception_handlers(content, "src/good.py")
        assert result is False

    def test_respects_configurable_contexts_parameter(self):
        """Test that custom acceptable_contexts are respected."""
        content = """
def custom_handler():
    try:
        load_config()
    except Exception:
        pass  # Use default config
"""
        # With 'config' in acceptable contexts
        assert (
            _has_problematic_exception_handlers(
                content,
                "src/config.py",
                acceptable_contexts=["config"],
            )
            is False
        )

        # Without 'config' in acceptable contexts
        assert (
            _has_problematic_exception_handlers(
                content,
                "src/config.py",
                acceptable_contexts=["version"],  # Only version, not config
            )
            is True
        )


# =============================================================================
# SUMMARY: What We Learned
# =============================================================================
"""
This test module demonstrated:

1. **File I/O Mocking** (TestLoadBugPredictConfig)
   - tmp_path fixture for temporary files
   - monkeypatch.chdir() for changing directories
   - Testing multiple fallback paths
   - Handling malformed input gracefully

2. **Pattern Matching** (TestShouldExcludeFile)
   - Parametrized testing with @pytest.mark.parametrize
   - Testing glob patterns (*, **, basename)
   - Edge cases (empty lists, no matches)
   - Case sensitivity testing

3. **Context-Aware Analysis** (TestIsAcceptableBroadException)
   - Testing code that analyzes surrounding context
   - Multiple conditional branches
   - Configurable behavior via parameters
   - Positive and negative test cases

4. **Security Testing** (TestIsDangerousEvalUsage)
   - False positive filtering
   - Distinguishing detection code from vulnerable code
   - Language-aware pattern detection
   - Meta-exclusions (test files)

5. **Integration Testing** (TestHasProblematicExceptionHandlers)
   - Testing functions that coordinate multiple helpers
   - Realistic code samples
   - Configuration propagation

**Next Steps:**
- Review the inline comments to understand each pattern
- Try modifying tests to see what breaks
- Apply these patterns to test other helper functions
- Experiment with adding new test cases

**Pattern Library Reference:**
All patterns used here are documented in:
docs/TESTING_PATTERNS.md (to be created in Phase 5)
"""
