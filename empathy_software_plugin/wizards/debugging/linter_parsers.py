"""Linter Output Parsers

Parses output from various linters into standardized format.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any


class Severity(Enum):
    """Issue severity levels"""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    STYLE = "style"


@dataclass
class LintIssue:
    """Standardized lint issue across all linters.

    This is the universal format - all parser output converts to this.
    """

    file_path: str
    line: int
    column: int
    rule: str
    message: str
    severity: Severity
    linter: str
    has_autofix: bool = False
    fix_suggestion: str | None = None
    context: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "file_path": self.file_path,
            "line": self.line,
            "column": self.column,
            "rule": self.rule,
            "message": self.message,
            "severity": self.severity.value,
            "linter": self.linter,
            "has_autofix": self.has_autofix,
            "fix_suggestion": self.fix_suggestion,
            "context": self.context or {},
        }


class BaseLinterParser:
    """Base class for all linter parsers"""

    def __init__(self, linter_name: str):
        self.linter_name = linter_name

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse linter output into standardized issues.

        Args:
            output: Raw linter output (text or JSON)
            format: "json", "text", or "auto" (detect)

        Returns:
            List of LintIssue objects

        """
        raise NotImplementedError

    def parse_file(self, file_path: str, format: str = "auto") -> list[LintIssue]:
        """Parse linter output from file"""
        with open(file_path) as f:
            return self.parse(f.read(), format)


class ESLintParser(BaseLinterParser):
    """Parse ESLint output.

    Supports both JSON and text formats.
    """

    def __init__(self):
        super().__init__("eslint")

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse ESLint output"""
        # Auto-detect format
        if format == "auto":
            format = "json" if output.strip().startswith("[") else "text"

        if format == "json":
            return self._parse_json(output)
        return self._parse_text(output)

    def _parse_json(self, output: str) -> list[LintIssue]:
        """Parse ESLint JSON format"""
        issues = []

        try:
            data = json.loads(output)

            for file_result in data:
                file_path = file_result.get("filePath", "")

                for message in file_result.get("messages", []):
                    issues.append(
                        LintIssue(
                            file_path=file_path,
                            line=message.get("line", 0),
                            column=message.get("column", 0),
                            rule=message.get("ruleId", "unknown"),
                            message=message.get("message", ""),
                            severity=self._map_severity(message.get("severity", 1)),
                            linter=self.linter_name,
                            has_autofix=message.get("fix") is not None,
                            fix_suggestion=str(message.get("fix")) if message.get("fix") else None,
                            context={
                                "node_type": message.get("nodeType"),
                                "end_line": message.get("endLine"),
                                "end_column": message.get("endColumn"),
                            },
                        ),
                    )

        except json.JSONDecodeError:
            # Return empty list if JSON invalid
            pass

        return issues

    def _parse_text(self, output: str) -> list[LintIssue]:
        """Parse ESLint text format"""
        issues = []

        # Pattern: /path/to/file.js
        #   1:5  error  'foo' is not defined  no-undef
        pattern = r"^\s*(\d+):(\d+)\s+(error|warning)\s+(.+?)\s+([a-z-]+)$"

        current_file = None

        for line in output.split("\n"):
            # Check if this is a file path line
            if line and not line.startswith(" "):
                current_file = line.strip()
                continue

            # Try to match issue line
            match = re.match(pattern, line)
            if match and current_file:
                line_num, col_num, severity, message, rule = match.groups()

                issues.append(
                    LintIssue(
                        file_path=current_file,
                        line=int(line_num),
                        column=int(col_num),
                        rule=rule,
                        message=message,
                        severity=Severity.ERROR if severity == "error" else Severity.WARNING,
                        linter=self.linter_name,
                        has_autofix=False,  # Can't tell from text format
                    ),
                )

        return issues

    def _map_severity(self, eslint_severity: int) -> Severity:
        """Map ESLint severity (1=warning, 2=error) to our enum"""
        return Severity.ERROR if eslint_severity == 2 else Severity.WARNING


class PylintParser(BaseLinterParser):
    """Parse Pylint output.

    Supports JSON and text formats.
    """

    def __init__(self):
        super().__init__("pylint")

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse Pylint output"""
        # Auto-detect format
        if format == "auto":
            format = "json" if output.strip().startswith("[") else "text"

        if format == "json":
            return self._parse_json(output)
        return self._parse_text(output)

    def _parse_json(self, output: str) -> list[LintIssue]:
        """Parse Pylint JSON format"""
        issues = []

        try:
            data = json.loads(output)

            for item in data:
                issues.append(
                    LintIssue(
                        file_path=item.get("path", ""),
                        line=item.get("line", 0),
                        column=item.get("column", 0),
                        rule=item.get("symbol", item.get("message-id", "unknown")),
                        message=item.get("message", ""),
                        severity=self._map_severity(item.get("type", "convention")),
                        linter=self.linter_name,
                        has_autofix=False,  # Pylint doesn't provide autofixes
                        context={
                            "symbol": item.get("symbol"),
                            "module": item.get("module"),
                            "obj": item.get("obj"),
                        },
                    ),
                )

        except json.JSONDecodeError:
            pass

        return issues

    def _parse_text(self, output: str) -> list[LintIssue]:
        """Parse Pylint text format"""
        issues = []

        # Pattern: path/to/file.py:42:8: C0103: Variable name "X" doesn't conform (invalid-name)
        pattern = r"^(.+?):(\d+):(\d+):\s*([A-Z]\d+):\s*(.+?)\s*\(([a-z-]+)\)$"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                file_path, line_num, col_num, code, message, symbol = match.groups()

                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=int(line_num),
                        column=int(col_num),
                        rule=symbol,
                        message=message,
                        severity=self._map_severity(code[0]),
                        linter=self.linter_name,
                        has_autofix=False,
                        context={"code": code, "symbol": symbol},
                    ),
                )

        return issues

    def _map_severity(self, type_or_code: str) -> Severity:
        """Map Pylint type/code to severity"""
        if isinstance(type_or_code, str):
            first_char = type_or_code[0].upper() if type_or_code else "C"

            mapping = {
                "E": Severity.ERROR,  # Error
                "F": Severity.ERROR,  # Fatal
                "W": Severity.WARNING,  # Warning
                "R": Severity.INFO,  # Refactor
                "C": Severity.STYLE,  # Convention
                "I": Severity.INFO,  # Informational
            }

            return mapping.get(first_char, Severity.INFO)

        return Severity.INFO


class MyPyParser(BaseLinterParser):
    """Parse mypy (Python type checker) output."""

    def __init__(self):
        super().__init__("mypy")

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse mypy output (text only)"""
        issues = []

        # Pattern: path/to/file.py:42: error: Incompatible types [assignment]
        pattern = r"^(.+?):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s*\[([a-z-]+)\])?$"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                file_path, line_num, severity, message, code = match.groups()

                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=int(line_num),
                        column=0,  # mypy doesn't always provide column
                        rule=code or "type-error",
                        message=message,
                        severity=Severity.ERROR if severity == "error" else Severity.WARNING,
                        linter=self.linter_name,
                        has_autofix=False,
                        context={"severity_text": severity},
                    ),
                )

        return issues


class TypeScriptParser(BaseLinterParser):
    """Parse TypeScript compiler (tsc) output."""

    def __init__(self):
        super().__init__("typescript")

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse tsc output"""
        issues = []

        # Pattern: src/file.ts(42,8): error TS2322: Type 'string' is not assignable to type 'number'.
        pattern = r"^(.+?)\((\d+),(\d+)\):\s*(error|warning)\s*TS(\d+):\s*(.+)$"

        for line in output.split("\n"):
            match = re.match(pattern, line.strip())
            if match:
                file_path, line_num, col_num, severity, code, message = match.groups()

                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=int(line_num),
                        column=int(col_num),
                        rule=f"TS{code}",
                        message=message,
                        severity=Severity.ERROR if severity == "error" else Severity.WARNING,
                        linter=self.linter_name,
                        has_autofix=False,
                        context={"ts_code": code},
                    ),
                )

        return issues


class ClippyParser(BaseLinterParser):
    """Parse Rust Clippy output."""

    def __init__(self):
        super().__init__("clippy")

    def parse(self, output: str, format: str = "auto") -> list[LintIssue]:
        """Parse clippy output"""
        issues = []

        # Pattern: warning: unused variable: `x`
        #   --> src/main.rs:5:9
        current_issue = {}

        for line in output.split("\n"):
            # Check for severity line
            severity_match = re.match(r"^(error|warning):\s*(.+)$", line.strip())
            if severity_match:
                if current_issue:
                    issues.append(self._create_issue(current_issue))

                current_issue = {
                    "severity": severity_match.group(1),
                    "message": severity_match.group(2),
                }
                continue

            # Check for location line
            loc_match = re.match(r"^\s*-->\s*(.+?):(\d+):(\d+)$", line.strip())
            if loc_match and current_issue:
                current_issue["file_path"] = loc_match.group(1)
                current_issue["line"] = int(loc_match.group(2))
                current_issue["column"] = int(loc_match.group(3))

            # Check for lint name
            lint_match = re.match(r"^\s*=\s*note:\s*#\[.*?\(([a-z_]+)\)\]", line.strip())
            if lint_match and current_issue:
                current_issue["rule"] = lint_match.group(1)

        # Add last issue
        if current_issue:
            issues.append(self._create_issue(current_issue))

        return issues

    def _create_issue(self, issue_dict: dict) -> LintIssue:
        """Create LintIssue from dict"""
        return LintIssue(
            file_path=issue_dict.get("file_path", ""),
            line=issue_dict.get("line", 0),
            column=issue_dict.get("column", 0),
            rule=issue_dict.get("rule", "clippy"),
            message=issue_dict.get("message", ""),
            severity=Severity.ERROR if issue_dict.get("severity") == "error" else Severity.WARNING,
            linter=self.linter_name,
            has_autofix=False,
        )


class LinterParserFactory:
    """Factory for creating appropriate parser based on linter type."""

    _parsers = {
        "eslint": ESLintParser,
        "pylint": PylintParser,
        "mypy": MyPyParser,
        "typescript": TypeScriptParser,
        "tsc": TypeScriptParser,
        "clippy": ClippyParser,
        "rustc": ClippyParser,
    }

    @classmethod
    def create(cls, linter_name: str) -> BaseLinterParser:
        """Create parser for specified linter.

        Args:
            linter_name: Name of linter (eslint, pylint, mypy, etc.)

        Returns:
            Appropriate parser instance

        Raises:
            ValueError if linter not supported

        """
        parser_class = cls._parsers.get(linter_name.lower())

        if not parser_class:
            raise ValueError(
                f"Unsupported linter: {linter_name}. Supported: {', '.join(cls._parsers.keys())}",
            )

        return parser_class()

    @classmethod
    def get_supported_linters(cls) -> list[str]:
        """Get list of supported linters"""
        return list(cls._parsers.keys())


def parse_linter_output(linter_name: str, output: str, format: str = "auto") -> list[LintIssue]:
    """Convenience function to parse linter output.

    Args:
        linter_name: Name of linter
        output: Raw linter output
        format: "json", "text", or "auto"

    Returns:
        List of standardized LintIssue objects

    Example:
        >>> issues = parse_linter_output("eslint", eslint_json_output)
        >>> for issue in issues:
        ...     print(f"{issue.file_path}:{issue.line} - {issue.message}")

    """
    parser = LinterParserFactory.create(linter_name)
    return parser.parse(output, format)
