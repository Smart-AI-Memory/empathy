"""
Tests for empathy_software_plugin/wizards/debugging/linter_parsers.py

Comprehensive tests for all linter parser implementations.
"""

import json
import os
import tempfile

import pytest

from empathy_software_plugin.wizards.debugging.linter_parsers import (
    BaseLinterParser,
    ClippyParser,
    ESLintParser,
    LinterParserFactory,
    LintIssue,
    MyPyParser,
    PylintParser,
    Severity,
    TypeScriptParser,
    parse_linter_output,
)


class TestSeverity:
    """Tests for Severity enum."""

    def test_severity_values(self):
        """Test Severity enum has expected values."""
        assert Severity.ERROR.value == "error"
        assert Severity.WARNING.value == "warning"
        assert Severity.INFO.value == "info"
        assert Severity.STYLE.value == "style"

    def test_severity_members(self):
        """Test all Severity members exist."""
        members = list(Severity)
        assert len(members) == 4
        assert Severity.ERROR in members
        assert Severity.WARNING in members
        assert Severity.INFO in members
        assert Severity.STYLE in members


class TestLintIssue:
    """Tests for LintIssue dataclass."""

    def test_lint_issue_creation(self):
        """Test LintIssue can be created with required fields."""
        issue = LintIssue(
            file_path="/path/to/file.py",
            line=42,
            column=8,
            rule="no-unused-vars",
            message="Variable 'x' is unused",
            severity=Severity.WARNING,
            linter="eslint",
        )

        assert issue.file_path == "/path/to/file.py"
        assert issue.line == 42
        assert issue.column == 8
        assert issue.rule == "no-unused-vars"
        assert issue.message == "Variable 'x' is unused"
        assert issue.severity == Severity.WARNING
        assert issue.linter == "eslint"
        assert issue.has_autofix is False
        assert issue.fix_suggestion is None
        assert issue.context is None

    def test_lint_issue_with_optional_fields(self):
        """Test LintIssue with all optional fields."""
        issue = LintIssue(
            file_path="/path/to/file.py",
            line=10,
            column=5,
            rule="semi",
            message="Missing semicolon",
            severity=Severity.ERROR,
            linter="eslint",
            has_autofix=True,
            fix_suggestion="Add semicolon at end of line",
            context={"end_line": 10, "end_column": 20},
        )

        assert issue.has_autofix is True
        assert issue.fix_suggestion == "Add semicolon at end of line"
        assert issue.context == {"end_line": 10, "end_column": 20}

    def test_lint_issue_to_dict(self):
        """Test LintIssue.to_dict() method."""
        issue = LintIssue(
            file_path="/path/to/file.py",
            line=42,
            column=8,
            rule="no-unused-vars",
            message="Variable 'x' is unused",
            severity=Severity.WARNING,
            linter="eslint",
            has_autofix=True,
            fix_suggestion="Remove the variable",
            context={"node_type": "Identifier"},
        )

        result = issue.to_dict()

        assert result["file_path"] == "/path/to/file.py"
        assert result["line"] == 42
        assert result["column"] == 8
        assert result["rule"] == "no-unused-vars"
        assert result["message"] == "Variable 'x' is unused"
        assert result["severity"] == "warning"  # Note: string value
        assert result["linter"] == "eslint"
        assert result["has_autofix"] is True
        assert result["fix_suggestion"] == "Remove the variable"
        assert result["context"] == {"node_type": "Identifier"}

    def test_lint_issue_to_dict_empty_context(self):
        """Test to_dict returns empty dict for None context."""
        issue = LintIssue(
            file_path="/path/to/file.py",
            line=1,
            column=1,
            rule="test",
            message="test",
            severity=Severity.INFO,
            linter="test",
            context=None,
        )

        result = issue.to_dict()
        assert result["context"] == {}


class TestESLintParser:
    """Tests for ESLintParser."""

    def test_eslint_parser_initialization(self):
        """Test ESLintParser initializes with correct linter name."""
        parser = ESLintParser()
        assert parser.linter_name == "eslint"

    def test_parse_eslint_json_single_file(self):
        """Test parsing ESLint JSON output with single file."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "no-unused-vars",
                            "severity": 2,
                            "message": "'foo' is defined but never used",
                            "line": 10,
                            "column": 5,
                            "nodeType": "Identifier",
                            "endLine": 10,
                            "endColumn": 8,
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].file_path == "/src/app.js"
        assert issues[0].line == 10
        assert issues[0].column == 5
        assert issues[0].rule == "no-unused-vars"
        assert issues[0].message == "'foo' is defined but never used"
        assert issues[0].severity == Severity.ERROR
        assert issues[0].linter == "eslint"
        assert issues[0].context["node_type"] == "Identifier"

    def test_parse_eslint_json_multiple_files(self):
        """Test parsing ESLint JSON output with multiple files."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "semi",
                            "severity": 2,
                            "message": "Missing semicolon",
                            "line": 5,
                            "column": 20,
                        }
                    ],
                },
                {
                    "filePath": "/src/utils.js",
                    "messages": [
                        {
                            "ruleId": "no-console",
                            "severity": 1,
                            "message": "Unexpected console statement",
                            "line": 15,
                            "column": 1,
                        },
                        {
                            "ruleId": "eqeqeq",
                            "severity": 2,
                            "message": "Expected '===' and instead saw '=='",
                            "line": 20,
                            "column": 10,
                        },
                    ],
                },
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 3
        assert issues[0].file_path == "/src/app.js"
        assert issues[1].file_path == "/src/utils.js"
        assert issues[2].file_path == "/src/utils.js"
        assert issues[1].severity == Severity.WARNING  # severity 1
        assert issues[2].severity == Severity.ERROR  # severity 2

    def test_parse_eslint_json_with_autofix(self):
        """Test parsing ESLint JSON with autofix available."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "semi",
                            "severity": 2,
                            "message": "Missing semicolon",
                            "line": 5,
                            "column": 20,
                            "fix": {"range": [100, 100], "text": ";"},
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].has_autofix is True
        assert issues[0].fix_suggestion is not None

    def test_parse_eslint_json_empty(self):
        """Test parsing empty ESLint JSON output."""
        parser = ESLintParser()
        issues = parser.parse("[]")

        assert issues == []

    def test_parse_eslint_json_no_messages(self):
        """Test parsing ESLint JSON with no messages."""
        eslint_json = json.dumps([{"filePath": "/src/app.js", "messages": []}])

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert issues == []

    def test_parse_eslint_json_invalid(self):
        """Test parsing invalid JSON returns empty list."""
        parser = ESLintParser()
        issues = parser.parse("not valid json")

        assert issues == []

    def test_parse_eslint_text_format(self):
        """Test parsing ESLint text format."""
        eslint_text = """/src/app.js
  10:5  error  'foo' is defined but never used  no-unused-vars
  15:1  warning  Unexpected console statement  no-console
"""

        parser = ESLintParser()
        issues = parser.parse(eslint_text, format="text")

        assert len(issues) == 2
        assert issues[0].file_path == "/src/app.js"
        assert issues[0].line == 10
        assert issues[0].column == 5
        assert issues[0].severity == Severity.ERROR
        assert issues[0].rule == "no-unused-vars"
        assert issues[1].severity == Severity.WARNING

    def test_parse_eslint_text_multiple_files(self):
        """Test parsing ESLint text format with multiple files."""
        # Note: ESLint text format doesn't have blank lines between files
        # The parser treats any non-indented line as a file path
        # Rule names must be lowercase letters and hyphens only (no digits)
        eslint_text = """/src/app.js
  10:5  error  Error message one  no-unused-vars
/src/utils.js
  5:1  warning  Warning message two  no-console
"""

        parser = ESLintParser()
        issues = parser.parse(eslint_text, format="text")

        assert len(issues) == 2
        assert issues[0].file_path == "/src/app.js"
        assert issues[1].file_path == "/src/utils.js"

    def test_parse_eslint_text_empty(self):
        """Test parsing empty text output."""
        parser = ESLintParser()
        issues = parser.parse("", format="text")

        assert issues == []

    def test_parse_eslint_auto_detect_json(self):
        """Test auto-detection of JSON format."""
        eslint_json = json.dumps([{"filePath": "/src/app.js", "messages": []}])

        parser = ESLintParser()
        issues = parser.parse(eslint_json, format="auto")

        assert issues == []

    def test_parse_eslint_auto_detect_text(self):
        """Test auto-detection of text format."""
        eslint_text = "/src/app.js\n  1:1  error  Test error  test-rule\n"

        parser = ESLintParser()
        issues = parser.parse(eslint_text, format="auto")

        assert len(issues) == 1

    def test_eslint_severity_mapping(self):
        """Test ESLint severity mapping (1=warning, 2=error)."""
        parser = ESLintParser()

        assert parser._map_severity(1) == Severity.WARNING
        assert parser._map_severity(2) == Severity.ERROR
        assert parser._map_severity(0) == Severity.WARNING  # Default


class TestPylintParser:
    """Tests for PylintParser."""

    def test_pylint_parser_initialization(self):
        """Test PylintParser initializes with correct linter name."""
        parser = PylintParser()
        assert parser.linter_name == "pylint"

    def test_parse_pylint_json(self):
        """Test parsing Pylint JSON output."""
        pylint_json = json.dumps(
            [
                {
                    "type": "error",
                    "module": "mymodule",
                    "obj": "MyClass.method",
                    "line": 42,
                    "column": 8,
                    "path": "src/mymodule.py",
                    "symbol": "undefined-variable",
                    "message": "Undefined variable 'foo'",
                    "message-id": "E0602",
                }
            ]
        )

        parser = PylintParser()
        issues = parser.parse(pylint_json)

        assert len(issues) == 1
        assert issues[0].file_path == "src/mymodule.py"
        assert issues[0].line == 42
        assert issues[0].column == 8
        assert issues[0].rule == "undefined-variable"
        assert issues[0].message == "Undefined variable 'foo'"
        assert issues[0].severity == Severity.ERROR
        assert issues[0].linter == "pylint"
        assert issues[0].context["module"] == "mymodule"
        assert issues[0].context["obj"] == "MyClass.method"

    def test_parse_pylint_json_multiple(self):
        """Test parsing Pylint JSON with multiple issues."""
        pylint_json = json.dumps(
            [
                {
                    "type": "error",
                    "line": 10,
                    "column": 0,
                    "path": "src/app.py",
                    "symbol": "syntax-error",
                    "message": "Syntax error",
                },
                {
                    "type": "warning",
                    "line": 20,
                    "column": 4,
                    "path": "src/app.py",
                    "symbol": "unused-variable",
                    "message": "Unused variable 'x'",
                },
                {
                    "type": "convention",
                    "line": 30,
                    "column": 0,
                    "path": "src/app.py",
                    "symbol": "invalid-name",
                    "message": "Invalid variable name",
                },
            ]
        )

        parser = PylintParser()
        issues = parser.parse(pylint_json)

        assert len(issues) == 3
        assert issues[0].severity == Severity.ERROR
        assert issues[1].severity == Severity.WARNING
        assert issues[2].severity == Severity.STYLE  # convention

    def test_parse_pylint_json_empty(self):
        """Test parsing empty Pylint JSON."""
        parser = PylintParser()
        issues = parser.parse("[]")

        assert issues == []

    def test_parse_pylint_json_invalid(self):
        """Test parsing invalid JSON returns empty list."""
        parser = PylintParser()
        issues = parser.parse("not valid json")

        assert issues == []

    def test_parse_pylint_text_format(self):
        """Test parsing Pylint text format."""
        pylint_text = """src/app.py:42:8: E0602: Undefined variable 'foo' (undefined-variable)
src/app.py:50:0: W0612: Unused variable 'bar' (unused-variable)
"""

        parser = PylintParser()
        issues = parser.parse(pylint_text, format="text")

        assert len(issues) == 2
        assert issues[0].file_path == "src/app.py"
        assert issues[0].line == 42
        assert issues[0].column == 8
        assert issues[0].rule == "undefined-variable"
        assert issues[0].severity == Severity.ERROR
        assert issues[0].context["code"] == "E0602"
        assert issues[1].severity == Severity.WARNING

    def test_parse_pylint_text_all_severity_codes(self):
        """Test Pylint text parsing with all severity codes."""
        pylint_text = """app.py:1:0: E0001: Syntax error (syntax-error)
app.py:2:0: F0001: Fatal error (fatal-error)
app.py:3:0: W0001: Warning (warning-msg)
app.py:4:0: R0001: Refactor suggestion (refactor-msg)
app.py:5:0: C0001: Convention (convention-msg)
app.py:6:0: I0001: Info (info-msg)
"""

        parser = PylintParser()
        issues = parser.parse(pylint_text, format="text")

        assert len(issues) == 6
        assert issues[0].severity == Severity.ERROR  # E
        assert issues[1].severity == Severity.ERROR  # F
        assert issues[2].severity == Severity.WARNING  # W
        assert issues[3].severity == Severity.INFO  # R
        assert issues[4].severity == Severity.STYLE  # C
        assert issues[5].severity == Severity.INFO  # I

    def test_parse_pylint_text_empty(self):
        """Test parsing empty text output."""
        parser = PylintParser()
        issues = parser.parse("", format="text")

        assert issues == []

    def test_parse_pylint_auto_detect_json(self):
        """Test auto-detection of JSON format."""
        pylint_json = json.dumps(
            [
                {
                    "path": "test.py",
                    "line": 1,
                    "column": 0,
                    "symbol": "test",
                    "message": "test",
                    "type": "error",
                }
            ]
        )

        parser = PylintParser()
        issues = parser.parse(pylint_json, format="auto")

        assert len(issues) == 1

    def test_pylint_severity_mapping(self):
        """Test Pylint severity mapping."""
        parser = PylintParser()

        assert parser._map_severity("error") == Severity.ERROR
        assert parser._map_severity("fatal") == Severity.ERROR
        assert parser._map_severity("warning") == Severity.WARNING
        assert parser._map_severity("refactor") == Severity.INFO
        assert parser._map_severity("convention") == Severity.STYLE
        assert parser._map_severity("info") == Severity.INFO
        assert parser._map_severity("unknown") == Severity.INFO  # Default

    def test_pylint_uses_symbol_over_message_id(self):
        """Test Pylint parser prefers symbol over message-id for rule."""
        pylint_json = json.dumps(
            [
                {
                    "path": "test.py",
                    "line": 1,
                    "column": 0,
                    "symbol": "the-symbol",
                    "message-id": "E0001",
                    "message": "test",
                    "type": "error",
                }
            ]
        )

        parser = PylintParser()
        issues = parser.parse(pylint_json)

        assert issues[0].rule == "the-symbol"

    def test_pylint_falls_back_to_message_id(self):
        """Test Pylint parser falls back to message-id when symbol missing."""
        pylint_json = json.dumps(
            [
                {
                    "path": "test.py",
                    "line": 1,
                    "column": 0,
                    "message-id": "E0001",
                    "message": "test",
                    "type": "error",
                }
            ]
        )

        parser = PylintParser()
        issues = parser.parse(pylint_json)

        assert issues[0].rule == "E0001"


class TestMyPyParser:
    """Tests for MyPyParser."""

    def test_mypy_parser_initialization(self):
        """Test MyPyParser initializes with correct linter name."""
        parser = MyPyParser()
        assert parser.linter_name == "mypy"

    def test_parse_mypy_error_with_code(self):
        """Test parsing mypy error with error code."""
        mypy_output = "src/app.py:42: error: Incompatible types in assignment [assignment]"

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 1
        assert issues[0].file_path == "src/app.py"
        assert issues[0].line == 42
        assert issues[0].column == 0  # mypy doesn't provide column
        assert issues[0].rule == "assignment"
        assert issues[0].message == "Incompatible types in assignment"
        assert issues[0].severity == Severity.ERROR
        assert issues[0].linter == "mypy"

    def test_parse_mypy_error_without_code(self):
        """Test parsing mypy error without error code."""
        mypy_output = "src/app.py:10: error: Cannot find implementation"

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 1
        assert issues[0].rule == "type-error"  # Default rule

    def test_parse_mypy_warning(self):
        """Test parsing mypy warning."""
        mypy_output = "src/app.py:15: warning: Unused import [unused-import]"

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING
        assert issues[0].rule == "unused-import"

    def test_parse_mypy_note(self):
        """Test parsing mypy note."""
        mypy_output = "src/app.py:20: note: See https://mypy.readthedocs.io [note-msg]"

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING  # note maps to warning
        assert issues[0].context["severity_text"] == "note"

    def test_parse_mypy_multiple(self):
        """Test parsing multiple mypy errors."""
        mypy_output = """src/app.py:10: error: Type error 1 [type-error-1]
src/utils.py:20: error: Type error 2 [type-error-2]
src/models.py:30: warning: Warning message [warn-1]
"""

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 3
        assert issues[0].file_path == "src/app.py"
        assert issues[1].file_path == "src/utils.py"
        assert issues[2].file_path == "src/models.py"

    def test_parse_mypy_empty(self):
        """Test parsing empty mypy output."""
        parser = MyPyParser()
        issues = parser.parse("")

        assert issues == []

    def test_parse_mypy_ignores_non_matching_lines(self):
        """Test mypy parser ignores lines that don't match pattern."""
        mypy_output = """Success: no issues found in 3 source files
src/app.py:10: error: Real error [real-error]
Some other random line
"""

        parser = MyPyParser()
        issues = parser.parse(mypy_output)

        assert len(issues) == 1
        assert issues[0].rule == "real-error"


class TestTypeScriptParser:
    """Tests for TypeScriptParser."""

    def test_typescript_parser_initialization(self):
        """Test TypeScriptParser initializes with correct linter name."""
        parser = TypeScriptParser()
        assert parser.linter_name == "typescript"

    def test_parse_typescript_error(self):
        """Test parsing TypeScript compiler error."""
        tsc_output = (
            "src/app.ts(42,8): error TS2322: Type 'string' is not assignable to type 'number'."
        )

        parser = TypeScriptParser()
        issues = parser.parse(tsc_output)

        assert len(issues) == 1
        assert issues[0].file_path == "src/app.ts"
        assert issues[0].line == 42
        assert issues[0].column == 8
        assert issues[0].rule == "TS2322"
        assert issues[0].message == "Type 'string' is not assignable to type 'number'."
        assert issues[0].severity == Severity.ERROR
        assert issues[0].linter == "typescript"
        assert issues[0].context["ts_code"] == "2322"

    def test_parse_typescript_warning(self):
        """Test parsing TypeScript compiler warning."""
        tsc_output = (
            "src/app.ts(10,1): warning TS6133: 'x' is declared but its value is never read."
        )

        parser = TypeScriptParser()
        issues = parser.parse(tsc_output)

        assert len(issues) == 1
        assert issues[0].severity == Severity.WARNING

    def test_parse_typescript_multiple(self):
        """Test parsing multiple TypeScript errors."""
        tsc_output = """src/app.ts(10,5): error TS2304: Cannot find name 'foo'.
src/utils.ts(20,10): error TS2322: Type mismatch.
src/models.ts(30,1): warning TS6196: Unused variable.
"""

        parser = TypeScriptParser()
        issues = parser.parse(tsc_output)

        assert len(issues) == 3
        assert issues[0].file_path == "src/app.ts"
        assert issues[1].file_path == "src/utils.ts"
        assert issues[2].file_path == "src/models.ts"
        assert issues[0].rule == "TS2304"
        assert issues[1].rule == "TS2322"
        assert issues[2].rule == "TS6196"

    def test_parse_typescript_empty(self):
        """Test parsing empty TypeScript output."""
        parser = TypeScriptParser()
        issues = parser.parse("")

        assert issues == []

    def test_parse_typescript_ignores_non_matching(self):
        """Test TypeScript parser ignores non-matching lines."""
        tsc_output = """Starting compilation...
src/app.ts(10,5): error TS2304: Cannot find name 'foo'.
Watching for file changes.
"""

        parser = TypeScriptParser()
        issues = parser.parse(tsc_output)

        assert len(issues) == 1


class TestClippyParser:
    """Tests for ClippyParser (Rust)."""

    def test_clippy_parser_initialization(self):
        """Test ClippyParser initializes with correct linter name."""
        parser = ClippyParser()
        assert parser.linter_name == "clippy"

    def test_parse_clippy_warning(self):
        """Test parsing Clippy warning."""
        clippy_output = """warning: unused variable: `x`
  --> src/main.rs:5:9
"""

        parser = ClippyParser()
        issues = parser.parse(clippy_output)

        assert len(issues) == 1
        assert issues[0].file_path == "src/main.rs"
        assert issues[0].line == 5
        assert issues[0].column == 9
        assert issues[0].message == "unused variable: `x`"
        assert issues[0].severity == Severity.WARNING
        assert issues[0].linter == "clippy"

    def test_parse_clippy_error(self):
        """Test parsing Clippy error."""
        clippy_output = """error: cannot find value `foo` in this scope
  --> src/lib.rs:10:5
"""

        parser = ClippyParser()
        issues = parser.parse(clippy_output)

        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        assert issues[0].file_path == "src/lib.rs"
        assert issues[0].line == 10
        assert issues[0].column == 5

    def test_parse_clippy_with_lint_name(self):
        """Test parsing Clippy output with lint name."""
        clippy_output = """warning: unused variable: `x`
  --> src/main.rs:5:9
   |
   = note: #[warn(unused_variables)]
"""

        parser = ClippyParser()
        issues = parser.parse(clippy_output)

        assert len(issues) == 1
        assert issues[0].rule == "unused_variables"

    def test_parse_clippy_multiple(self):
        """Test parsing multiple Clippy issues."""
        clippy_output = """warning: warning 1
  --> src/main.rs:5:9
error: error 1
  --> src/lib.rs:10:5
warning: warning 2
  --> src/utils.rs:15:1
"""

        parser = ClippyParser()
        issues = parser.parse(clippy_output)

        assert len(issues) == 3
        assert issues[0].severity == Severity.WARNING
        assert issues[1].severity == Severity.ERROR
        assert issues[2].severity == Severity.WARNING
        assert issues[0].file_path == "src/main.rs"
        assert issues[1].file_path == "src/lib.rs"
        assert issues[2].file_path == "src/utils.rs"

    def test_parse_clippy_empty(self):
        """Test parsing empty Clippy output."""
        parser = ClippyParser()
        issues = parser.parse("")

        assert issues == []

    def test_parse_clippy_no_location(self):
        """Test parsing Clippy output without location info."""
        clippy_output = """warning: orphan warning message
"""

        parser = ClippyParser()
        issues = parser.parse(clippy_output)

        # Should still create issue with empty/default location
        assert len(issues) == 1
        assert issues[0].file_path == ""
        assert issues[0].line == 0


class TestLinterParserFactory:
    """Tests for LinterParserFactory."""

    def test_create_eslint_parser(self):
        """Test factory creates ESLint parser."""
        parser = LinterParserFactory.create("eslint")
        assert isinstance(parser, ESLintParser)
        assert parser.linter_name == "eslint"

    def test_create_pylint_parser(self):
        """Test factory creates Pylint parser."""
        parser = LinterParserFactory.create("pylint")
        assert isinstance(parser, PylintParser)
        assert parser.linter_name == "pylint"

    def test_create_mypy_parser(self):
        """Test factory creates MyPy parser."""
        parser = LinterParserFactory.create("mypy")
        assert isinstance(parser, MyPyParser)
        assert parser.linter_name == "mypy"

    def test_create_typescript_parser(self):
        """Test factory creates TypeScript parser."""
        parser = LinterParserFactory.create("typescript")
        assert isinstance(parser, TypeScriptParser)
        assert parser.linter_name == "typescript"

    def test_create_tsc_parser(self):
        """Test factory creates TypeScript parser for 'tsc'."""
        parser = LinterParserFactory.create("tsc")
        assert isinstance(parser, TypeScriptParser)

    def test_create_clippy_parser(self):
        """Test factory creates Clippy parser."""
        parser = LinterParserFactory.create("clippy")
        assert isinstance(parser, ClippyParser)
        assert parser.linter_name == "clippy"

    def test_create_rustc_parser(self):
        """Test factory creates Clippy parser for 'rustc'."""
        parser = LinterParserFactory.create("rustc")
        assert isinstance(parser, ClippyParser)

    def test_create_case_insensitive(self):
        """Test factory is case-insensitive."""
        parser1 = LinterParserFactory.create("ESLint")
        parser2 = LinterParserFactory.create("ESLINT")
        parser3 = LinterParserFactory.create("EsLiNt")

        assert isinstance(parser1, ESLintParser)
        assert isinstance(parser2, ESLintParser)
        assert isinstance(parser3, ESLintParser)

    def test_create_unsupported_linter(self):
        """Test factory raises ValueError for unsupported linter."""
        with pytest.raises(ValueError) as excinfo:
            LinterParserFactory.create("unsupported-linter")

        assert "Unsupported linter" in str(excinfo.value)
        assert "unsupported-linter" in str(excinfo.value)

    def test_get_supported_linters(self):
        """Test get_supported_linters returns all supported linters."""
        supported = LinterParserFactory.get_supported_linters()

        assert "eslint" in supported
        assert "pylint" in supported
        assert "mypy" in supported
        assert "typescript" in supported
        assert "tsc" in supported
        assert "clippy" in supported
        assert "rustc" in supported
        assert len(supported) == 7


class TestParseLintersOutput:
    """Tests for parse_linter_output convenience function."""

    def test_parse_linter_output_eslint(self):
        """Test convenience function with ESLint."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "no-unused-vars",
                            "severity": 2,
                            "message": "Unused var",
                            "line": 10,
                            "column": 5,
                        }
                    ],
                }
            ]
        )

        issues = parse_linter_output("eslint", eslint_json)

        assert len(issues) == 1
        assert issues[0].linter == "eslint"

    def test_parse_linter_output_pylint(self):
        """Test convenience function with Pylint."""
        pylint_text = "app.py:10:0: E0001: Error (error-symbol)"

        issues = parse_linter_output("pylint", pylint_text, format="text")

        assert len(issues) == 1
        assert issues[0].linter == "pylint"

    def test_parse_linter_output_unsupported(self):
        """Test convenience function raises for unsupported linter."""
        with pytest.raises(ValueError):
            parse_linter_output("unknown-linter", "some output")


class TestBaseLinterParser:
    """Tests for BaseLinterParser."""

    def test_base_parser_parse_not_implemented(self):
        """Test BaseLinterParser.parse raises NotImplementedError."""
        parser = BaseLinterParser("test")

        with pytest.raises(NotImplementedError):
            parser.parse("some output")

    def test_base_parser_parse_file(self):
        """Test BaseLinterParser.parse_file reads and parses file."""
        # Create a temporary file with linter output
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            eslint_json = json.dumps(
                [
                    {
                        "filePath": "/src/app.js",
                        "messages": [
                            {
                                "ruleId": "test-rule",
                                "severity": 2,
                                "message": "Test message",
                                "line": 1,
                                "column": 1,
                            }
                        ],
                    }
                ]
            )
            f.write(eslint_json)
            temp_path = f.name

        try:
            parser = ESLintParser()
            issues = parser.parse_file(temp_path)

            assert len(issues) == 1
            assert issues[0].rule == "test-rule"
        finally:
            os.unlink(temp_path)


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_eslint_json_missing_fields(self):
        """Test ESLint parser handles missing fields gracefully."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [{}],  # Empty message
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].line == 0
        assert issues[0].column == 0
        assert issues[0].rule == "unknown"
        assert issues[0].message == ""

    def test_pylint_json_missing_fields(self):
        """Test Pylint parser handles missing fields gracefully."""
        pylint_json = json.dumps([{}])  # Empty item

        parser = PylintParser()
        issues = parser.parse(pylint_json)

        assert len(issues) == 1
        assert issues[0].file_path == ""
        assert issues[0].rule == "unknown"

    def test_whitespace_only_output(self):
        """Test parsers handle whitespace-only output."""
        parsers = [
            ESLintParser(),
            PylintParser(),
            MyPyParser(),
            TypeScriptParser(),
            ClippyParser(),
        ]

        for parser in parsers:
            issues = parser.parse("   \n\t\n   ")
            assert issues == []

    def test_very_long_message(self):
        """Test parsers handle very long messages."""
        long_message = "a" * 10000
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "test",
                            "severity": 2,
                            "message": long_message,
                            "line": 1,
                            "column": 1,
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].message == long_message

    def test_special_characters_in_file_path(self):
        """Test parsers handle special characters in file paths."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/path/with spaces/and-dashes/file.js",
                    "messages": [
                        {
                            "ruleId": "test",
                            "severity": 2,
                            "message": "Test",
                            "line": 1,
                            "column": 1,
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].file_path == "/path/with spaces/and-dashes/file.js"

    def test_unicode_in_message(self):
        """Test parsers handle unicode in messages."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "test",
                            "severity": 2,
                            "message": "Error with unicode: \u2714 \u2718 \u00e9\u00e8\u00ea",
                            "line": 1,
                            "column": 1,
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert "\u2714" in issues[0].message

    def test_negative_line_numbers(self):
        """Test parsers handle unusual line numbers."""
        eslint_json = json.dumps(
            [
                {
                    "filePath": "/src/app.js",
                    "messages": [
                        {
                            "ruleId": "test",
                            "severity": 2,
                            "message": "Test",
                            "line": -1,
                            "column": -1,
                        }
                    ],
                }
            ]
        )

        parser = ESLintParser()
        issues = parser.parse(eslint_json)

        assert len(issues) == 1
        assert issues[0].line == -1
        assert issues[0].column == -1
