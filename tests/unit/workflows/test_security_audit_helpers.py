"""Educational Tests for Security Audit Helper Functions

Learning Objectives:
- Meta-detection: Testing code that detects vulnerabilities
- False positive filtering in security scanning
- String analysis and context awareness
- Pattern matching with regex for security patterns
- Testing boundary conditions in security contexts

This test suite demonstrates progressive complexity:
- LESSON 1: Detection code identification (meta-detection)
- LESSON 2: Fake credential pattern recognition
- LESSON 3: Documentation and string literal detection
- LESSON 4: Integration - Combining multiple filters
- LESSON 5: Edge cases and boundary conditions

These patterns are critical for security tools to avoid crying wolf
on their own detection code or test fixtures.
"""

import pytest

from empathy_os.workflows.security_audit import SecurityAuditWorkflow

# ============================================================================
# LESSON 1: Meta-Detection - Identifying Detection Code
# ============================================================================
# Teaching Pattern: Testing code that detects vulnerable patterns vs
# code that actually uses those patterns


@pytest.mark.unit
class TestIsDetectionCode:
    """Educational tests for detection code identification (meta-detection)."""

    def test_identifies_string_literal_detection_patterns(self):
        """Teaching Pattern: Meta-detection fundamentals.

        When code contains '"eval("' as a string literal (in quotes),
        it's likely detection code searching for that pattern, not
        actually calling eval().

        Example: if "eval(" in content:  # Detection, not vulnerability
        """
        workflow = SecurityAuditWorkflow()

        # Line of code that's DETECTING eval usage
        line = 'if "eval(" in content:'
        match = "eval("

        result = workflow._is_detection_code(line, match)
        assert result is True  # This is detection code, not vulnerable code

    def test_identifies_regex_compilation_for_detection(self):
        r"""Teaching Pattern: Regex-based detection identification.

        When code compiles a regex pattern for scanning, it's building
        a security tool, not introducing a vulnerability.

        Example: pattern = re.compile(r"eval\(")
        """
        workflow = SecurityAuditWorkflow()

        # Line that compiles regex for detection
        line = 'pattern = re.compile(r"eval\\(")'
        match = "eval("

        result = workflow._is_detection_code(line, match)
        assert result is True  # Regex compilation = detection tool

    def test_identifies_pattern_searching(self):
        """Teaching Pattern: Pattern matching method detection.

        Methods like .search(), .finditer(), .match() indicate
        pattern detection, not vulnerability introduction.

        Example: matches = pattern.search(code)
        """
        workflow = SecurityAuditWorkflow()

        # Line using regex search for detection
        line = "matches = pattern.search(code_content)"
        match = "eval("

        result = workflow._is_detection_code(line, match)
        assert result is True  # Search method = detection

    def test_identifies_in_content_checks(self):
        """Teaching Pattern: Content checking identification.

        The pattern "X in content" is a common detection idiom.

        Example: if "dangerous_pattern" in content:
        """
        workflow = SecurityAuditWorkflow()

        # Line checking for pattern existence
        line = 'if "subprocess.call" in content:'
        match = "subprocess.call"

        result = workflow._is_detection_code(line, match)
        assert result is True  # "in content" = detection pattern

    def test_rejects_actual_vulnerable_code(self):
        """Teaching Pattern: Distinguishing real vulnerabilities from detection.

        Actual calls to dangerous functions should NOT be flagged as
        detection code - they're real vulnerabilities.

        Example: result = eval(user_input)  # ACTUAL VULNERABILITY
        """
        workflow = SecurityAuditWorkflow()

        # Line that actually calls eval (VULNERABLE)
        line = "result = eval(user_input)"
        match = "eval("

        result = workflow._is_detection_code(line, match)
        assert result is False  # This is real vulnerable code


# ============================================================================
# LESSON 2: Fake Credential Pattern Recognition
# ============================================================================
# Teaching Pattern: Identifying test/example credentials vs real secrets


@pytest.mark.unit
class TestIsFakeCredential:
    """Educational tests for fake credential identification."""

    def test_identifies_aws_example_keys(self):
        """Teaching Pattern: AWS official example pattern.

        AWS documentation uses 'EXAMPLE' in their example credentials.
        These should never be flagged as real secrets.

        Example: AKIAIOSFODNN7EXAMPLE
        """
        workflow = SecurityAuditWorkflow()

        # Official AWS example key
        credential = 'api_key = "AKIAIOSFODNN7EXAMPLE"'

        result = workflow._is_fake_credential(credential)
        assert result is True  # Contains 'EXAMPLE' marker

    def test_identifies_test_and_mock_credentials(self):
        """Teaching Pattern: Common test credential markers.

        Credentials containing 'TEST', 'FAKE', 'MOCK' are clearly
        not real secrets and should be ignored.
        """
        workflow = SecurityAuditWorkflow()

        test_credentials = [
            'password = "TEST_PASSWORD_123"',
            'secret = "FAKE_SECRET_KEY"',
            'token = "mock-api-token"',
        ]

        for cred in test_credentials:
            result = workflow._is_fake_credential(cred)
            assert result is True, f"Should identify {cred} as fake"

    def test_identifies_placeholder_patterns(self):
        """Teaching Pattern: Placeholder credential detection.

        Credentials with "your-X-here", "...", or generic values like
        "secret" or "password" are placeholders.

        Example: api_key = "your-api-key-here"
        """
        workflow = SecurityAuditWorkflow()

        placeholder_credentials = [
            'api_key = "your-api-key-here"',
            'secret = "your-secret-here"',
            'password = "..."',  # Ellipsis placeholder
            'token = "your-key"',
        ]

        for cred in placeholder_credentials:
            result = workflow._is_fake_credential(cred)
            assert result is True, f"Should identify {cred} as placeholder"

    def test_identifies_literal_example_values(self):
        """Teaching Pattern: Literal test values.

        Values like "secret123", "password", "hardcoded_secret" are
        clearly examples from documentation or tests.
        """
        workflow = SecurityAuditWorkflow()

        example_values = [
            'password = "secret123"',
            'api_key = "hardcoded_secret"',
            'token = "password"',  # Generic "password" as value
        ]

        for value in example_values:
            result = workflow._is_fake_credential(value)
            assert result is True, f"Should identify {value} as example"

    def test_identifies_pattern_constants(self):
        r"""Teaching Pattern: Pattern definition constants.

        Constants ending in _PATTERN or _EXAMPLE are pattern definitions,
        not actual secrets.

        Example: SECRET_PATTERN = r"secret\s*="
        """
        workflow = SecurityAuditWorkflow()

        pattern_constants = [
            'SECRET_PATTERN = r"api_key\\s*="',
            'PASSWORD_EXAMPLE = "secret123"',
        ]

        for const in pattern_constants:
            result = workflow._is_fake_credential(const)
            assert result is True, f"Should identify {const} as pattern constant"

    def test_rejects_real_looking_credentials(self):
        """Teaching Pattern: Distinguishing real secrets from fake ones.

        Credentials that don't match any fake patterns should be flagged
        as potential real secrets.

        Example: api_key = "sk_live_1234567890abcdef"  # Looks real
        """
        workflow = SecurityAuditWorkflow()

        # Real-looking credentials (not in our fake patterns)
        real_looking = [
            'api_key = "sk_live_1234567890abcdef"',
            'password = "MyC0mpl3xP@ssw0rd!"',
            'secret = "prod-secret-key-xj92k1"',
        ]

        for cred in real_looking:
            result = workflow._is_fake_credential(cred)
            assert result is False, f"Should NOT identify {cred} as fake"


# ============================================================================
# LESSON 3: Documentation and String Literal Detection
# ============================================================================
# Teaching Pattern: Identifying code in documentation vs actual code


@pytest.mark.unit
class TestIsDocumentationOrString:
    """Educational tests for documentation and string literal detection."""

    def test_identifies_comment_lines(self):
        """Teaching Pattern: Comment detection.

        Lines starting with comment markers (#, //, *) are documentation,
        not executable code.

        Example: # This code is vulnerable: eval(user_input)
        """
        workflow = SecurityAuditWorkflow()

        comment_lines = [
            "# Example of dangerous code: eval(user_input)",
            "// Avoid using eval() in production",
            "* eval() is dangerous - don't use it",
        ]

        for line in comment_lines:
            result = workflow._is_documentation_or_string(line, "eval(")
            assert result is True, f"Should identify {line} as comment"

    def test_identifies_docstrings(self):
        """Teaching Pattern: Docstring detection.

        Lines containing triple quotes (triple-double or triple-single)
        are likely in docstrings.

        Example: Docstrings use triple quotes to denote multi-line strings
        that document functions, often containing code examples.
        """
        workflow = SecurityAuditWorkflow()

        docstring_lines = [
            '"""Example of eval() vulnerability"""',
            "'''Avoid using eval() with user input'''",
        ]

        for line in docstring_lines:
            result = workflow._is_documentation_or_string(line, "eval(")
            assert result is True, f"Should identify {line} as docstring"

    def test_identifies_string_literal_assignments(self):
        r"""Teaching Pattern: String assignment detection.

        Code that assigns a string containing vulnerable patterns
        is defining test data or patterns, not executing them.

        Example: pattern = r"eval\("  # Defining a pattern
        """
        workflow = SecurityAuditWorkflow()

        string_assignments = [
            'pattern = r"eval\\("',  # Raw string with pattern
            'vulnerable_code = "eval(user_input)"',  # String literal
            'example = "subprocess.call"',  # String assignment
        ]

        for line in string_assignments:
            result = workflow._is_documentation_or_string(line, "eval(")
            assert result is True, f"Should identify {line} as string assignment"

    def test_identifies_documentation_keywords(self):
        """Teaching Pattern: Contextual keyword detection.

        Lines containing keywords like "example", "vulnerable", "dangerous",
        "pattern", "detect" are explaining vulnerabilities, not introducing them.

        Example: # This is an example of vulnerable eval() usage
        """
        workflow = SecurityAuditWorkflow()

        documentation_contexts = [
            "# Example of vulnerable eval() code",
            "This pattern detects dangerous eval() calls",
            "Check for insecure eval() usage",
            "Look for dangerous eval patterns",
            "Scan for eval() vulnerabilities",
        ]

        for line in documentation_contexts:
            result = workflow._is_documentation_or_string(line, "eval(")
            assert result is True, f"Should identify {line} as documentation"

    def test_rejects_actual_executable_code(self):
        """Teaching Pattern: Distinguishing documentation from execution.

        Actual function calls without documentation context should NOT
        be flagged as documentation.

        Example: result = eval(user_input)  # REAL VULNERABILITY
        """
        workflow = SecurityAuditWorkflow()

        executable_lines = [
            "result = eval(user_input)",
            "output = subprocess.call(cmd, shell=True)",
            "data = exec(code)",
        ]

        for line in executable_lines:
            # Extract the dangerous call
            if "eval" in line:
                match = "eval("
            elif "subprocess" in line:
                match = "subprocess.call"
            else:
                match = "exec("

            result = workflow._is_documentation_or_string(line, match)
            # These should NOT be identified as documentation
            # (they are actual dangerous code)
            assert result is False, f"Should NOT identify {line} as documentation"


# ============================================================================
# LESSON 4: Integration Testing - Multiple Filters Working Together
# ============================================================================
# Teaching Pattern: Combining multiple detection methods


@pytest.mark.unit
class TestSecurityFilterIntegration:
    """Integration tests combining multiple security filters."""

    def test_scanner_test_file_with_detection_patterns(self):
        """Teaching Pattern: Multi-layer filtering.

        A security scanner test file might contain:
        1. Detection code (if "eval(" in content)
        2. Fake credentials (EXAMPLE keys)
        3. Documentation (explaining vulnerabilities)

        All of these should be filtered out, not flagged as vulnerabilities.
        """
        workflow = SecurityAuditWorkflow()

        # Code from a security scanner test file
        test_code_lines = [
            'if "eval(" in content:  # Detection pattern',
            'api_key = "AKIAIOSFODNN7EXAMPLE"  # Test credential',
            "# Example of dangerous eval() usage in docs",
        ]

        # Line 1: Detection code
        assert workflow._is_detection_code(test_code_lines[0], "eval(") is True

        # Line 2: Fake credential
        assert workflow._is_fake_credential(test_code_lines[1]) is True

        # Line 3: Documentation
        assert workflow._is_documentation_or_string(test_code_lines[2], "eval(") is True

    def test_distinguishes_real_vulnerabilities_from_false_positives(self):
        """Teaching Pattern: Precision in security scanning.

        A good security scanner must:
        - Flag REAL vulnerabilities (actual dangerous code)
        - Ignore false positives (detection code, tests, docs)

        This test validates both precision (catching real issues) and
        recall (not over-flagging).
        """
        workflow = SecurityAuditWorkflow()

        # REAL vulnerability - should be flagged
        real_vuln = "user_data = eval(request.GET['code'])"
        assert workflow._is_detection_code(real_vuln, "eval(") is False
        assert workflow._is_documentation_or_string(real_vuln, "eval(") is False

        # FALSE POSITIVE - detection code, should be ignored
        false_positive = 'if "eval(" in dangerous_patterns:'
        assert workflow._is_detection_code(false_positive, "eval(") is True

        # FALSE POSITIVE - documentation, should be ignored
        doc_line = "# Example: Don't use eval() with user input"
        assert workflow._is_documentation_or_string(doc_line, "eval(") is True


# ============================================================================
# LESSON 5: Edge Cases and Boundary Conditions
# ============================================================================
# Teaching Pattern: Testing unusual inputs and corner cases


@pytest.mark.unit
class TestSecurityFilterEdgeCases:
    """Edge case tests for security filter robustness."""

    def test_handles_empty_strings(self):
        """Teaching Pattern: Null/empty input handling.

        Security filters should gracefully handle empty inputs without
        crashing or giving false results.
        """
        workflow = SecurityAuditWorkflow()

        # Empty line content
        result = workflow._is_detection_code("", "eval(")
        assert result is False  # No detection patterns in empty string

        result = workflow._is_documentation_or_string("", "eval(")
        assert result is False  # No documentation markers in empty string

    def test_handles_very_long_lines(self):
        """Teaching Pattern: Performance and robustness.

        Real-world code can have very long lines (minified JS, generated code).
        Filters should handle these without performance issues.
        """
        workflow = SecurityAuditWorkflow()

        # Very long line with pattern at the end
        long_line = ("x = 1; " * 1000) + 'if "eval(" in content:'
        result = workflow._is_detection_code(long_line, "eval(")
        assert result is True  # Should still detect pattern

    def test_handles_unicode_and_special_characters(self):
        """Teaching Pattern: Character encoding robustness.

        Code in the wild may contain unicode, emojis, or special characters.
        Filters should handle these gracefully.
        """
        workflow = SecurityAuditWorkflow()

        # Line with unicode characters
        unicode_line = "# 🔒 Example: Don't use eval() with user input 中文"
        result = workflow._is_documentation_or_string(unicode_line, "eval(")
        assert result is True  # Still identifies as documentation

    def test_handles_nested_quotes(self):
        """Teaching Pattern: Complex string parsing.

        Code may have nested quotes or escaped characters.

        Example: pattern = r'if "eval\\"(" in content:'
        """
        workflow = SecurityAuditWorkflow()

        # Line with nested/escaped quotes
        nested_quotes = r'pattern = "if \"eval(\" in content"'
        result = workflow._is_detection_code(nested_quotes, "eval(")
        assert result is True  # Should identify as pattern definition

    def test_case_insensitive_pattern_matching(self):
        """Teaching Pattern: Case-insensitive detection.

        Some patterns (like FAKE, TEST, EXAMPLE) should be detected
        regardless of case.

        Example: "test_password" or "TEST_PASSWORD" or "Test_Password"
        """
        workflow = SecurityAuditWorkflow()

        # Different case variations
        case_variations = [
            'password = "test_password"',
            'password = "TEST_PASSWORD"',
            'password = "Test_Password"',
        ]

        for cred in case_variations:
            result = workflow._is_fake_credential(cred)
            assert result is True, f"Should detect {cred} regardless of case"


# ============================================================================
# LESSON 6: Initialization and Configuration
# ============================================================================
# Teaching Pattern: Testing class initialization and configuration


@pytest.mark.unit
class TestSecurityAuditWorkflowInitialization:
    """Tests for SecurityAuditWorkflow initialization."""

    def test_default_initialization(self, tmp_path, monkeypatch):
        """Teaching Pattern: Testing constructor defaults.

        When no arguments are provided, the workflow should use
        sensible defaults. We use tmp_path to avoid loading any
        existing team_decisions.json file.
        """
        # Use tmp_path to avoid loading existing files
        monkeypatch.chdir(tmp_path)

        workflow = SecurityAuditWorkflow()

        assert workflow.patterns_dir == "./patterns"
        assert workflow.skip_remediate_if_clean is True
        assert workflow._has_critical is False
        assert workflow._team_decisions == {}

    def test_custom_configuration(self):
        """Teaching Pattern: Testing dependency injection.

        The workflow should accept custom configuration through
        constructor parameters.
        """
        workflow = SecurityAuditWorkflow(
            patterns_dir="/custom/patterns",
            skip_remediate_if_clean=False,
        )

        assert workflow.patterns_dir == "/custom/patterns"
        assert workflow.skip_remediate_if_clean is False

    def test_stage_skip_logic_when_clean(self):
        """Teaching Pattern: Testing conditional premium tier usage.

        When no critical/high findings exist, remediation stage
        (premium model) should be skipped to save costs.
        """
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=True)
        workflow._has_critical = False  # No critical findings

        should_skip, reason = workflow.should_skip_stage("remediate", {})
        assert should_skip is True
        assert "No high/critical findings" in reason

    def test_stage_skip_logic_when_critical_found(self):
        """Teaching Pattern: Testing positive condition (when NOT to skip).

        When critical/high findings exist, remediation should run
        even if skip_remediate_if_clean is True.
        """
        workflow = SecurityAuditWorkflow(skip_remediate_if_clean=True)
        workflow._has_critical = True  # Critical findings detected

        should_skip, reason = workflow.should_skip_stage("remediate", {})
        assert should_skip is False
        assert reason is None


# ============================================================================
# SUMMARY: What We Learned
# ============================================================================
"""
This test suite demonstrated 6 progressive lessons in security testing:

1. **Meta-Detection (Testing Detection Code)**
   - Identifying code that DETECTS vulnerabilities vs code that INTRODUCES them
   - Pattern: "eval(" in content = detection, not vulnerability
   - Regex compilation, .search(), .finditer() = security tools

2. **Fake Credential Recognition**
   - AWS EXAMPLE keys, TEST/FAKE/MOCK markers
   - Placeholders: "your-X-here", "...", generic values
   - Pattern constants: _PATTERN, _EXAMPLE suffixes

3. **Documentation and String Literal Detection**
   - Comments (#, //, *), docstrings (triple quotes)
   - String assignments (pattern = r"...")
   - Documentation keywords: example, vulnerable, dangerous, pattern, detect

4. **Multi-Layer Filtering Integration**
   - Combining detection code + fake credentials + documentation filters
   - Precision vs recall in security scanning
   - Real vulnerabilities vs false positives

5. **Edge Cases and Robustness**
   - Empty strings, very long lines
   - Unicode and special characters
   - Nested quotes and escaped characters
   - Case-insensitive pattern matching

6. **Configuration and Initialization**
   - Constructor defaults and dependency injection
   - Conditional premium tier usage (cost optimization)
   - State-based skip logic (_has_critical flag)

**Key Patterns Used:**
- String analysis with regex patterns
- Context-aware detection (looking at surrounding code)
- False positive filtering (avoiding "crying wolf")
- Case-insensitive pattern matching
- State management for workflow decisions

**Real-World Impact:**
These patterns prevent security scanners from:
- Flagging their own detection code as vulnerable
- Alerting on test fixtures and example code
- Overwhelming developers with false positives
- Wasting premium model API calls on non-issues

**See Also:**
- Pattern Library: "Security Testing Patterns" (Phase 3)
- Tutorial: "Building Robust Security Scanners" (Phase 3)
- Blog Post: "Meta-Detection: Testing Security Tools" (Phase 3)
"""
