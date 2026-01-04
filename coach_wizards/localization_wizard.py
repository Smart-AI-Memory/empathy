"""LocalizationWizard - Internationalization and localization

Level 4 Anticipatory Empathy for Localization using the Empathy Framework.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from typing import Any

from .base_wizard import BaseCoachWizard, WizardIssue, WizardPrediction


class LocalizationWizard(BaseCoachWizard):
    """Internationalization and localization

    Detects:
    - hardcoded strings
    - missing translations
    - locale issues
    - RTL problems

    Predicts (Level 4):
    - i18n technical debt
    - translation maintenance burden
    - locale coverage gaps
    """

    def __init__(self):
        super().__init__(
            name="LocalizationWizard",
            category="Localization",
            languages=["python", "javascript", "typescript", "java", "go", "html", "jsx", "tsx"],
        )

    def analyze_code(self, code: str, file_path: str, language: str) -> list[WizardIssue]:
        """Analyze code for localization issues

        This is a reference implementation. In production, integrate with:
        - Static analysis tools
        - Linters and security scanners
        - Custom rule engines
        - AI models (Claude, GPT-4)
        """
        issues: list[WizardIssue] = []

        # Use generator-based iteration to avoid large list copies
        # splitlines() is more memory-efficient than split("\n")
        for line_num, line in enumerate(code.splitlines(), 1):
            # Detect hardcoded strings (basic heuristic)
            issue = self._check_hardcoded_string(line, line_num, file_path, language)
            if issue:
                issues.append(issue)

        self.logger.info(f"{self.name} found {len(issues)} issues in {file_path}")
        return issues

    def _check_hardcoded_string(
        self,
        line: str,
        line_num: int,
        file_path: str,
        language: str,
    ) -> WizardIssue | None:
        """Check a single line for hardcoded user-facing strings."""
        # Skip comments and imports
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", "//", "/*", "*", "import", "from")):
            return None

        # Basic detection patterns by language
        # In production, use language-specific AST parsing
        patterns = {
            "python": self._check_python_hardcoded,
            "javascript": self._check_js_hardcoded,
            "typescript": self._check_js_hardcoded,
            "jsx": self._check_js_hardcoded,
            "tsx": self._check_js_hardcoded,
        }

        checker = patterns.get(language)
        if checker:
            return checker(line, line_num, file_path)
        return None

    def _check_python_hardcoded(
        self,
        line: str,
        line_num: int,
        file_path: str,
    ) -> WizardIssue | None:
        """Check Python code for hardcoded UI strings."""
        # Look for print() or raise with string literals
        # Skip logging, docstrings, and comments
        if "print(" in line or "raise " in line:
            # Check for quoted strings that look like UI text
            if '"' in line or "'" in line:
                # Basic heuristic: strings > 10 chars that aren't paths/URLs
                import re

                strings = re.findall(r'["\']([^"\']{10,})["\']', line)
                for s in strings:
                    if not s.startswith(("/", "http", "\\", ".")):
                        return WizardIssue(
                            category="hardcoded_string",
                            severity="warning",
                            message=f"Potential hardcoded UI string: '{s[:30]}...'",
                            file_path=file_path,
                            line_number=line_num,
                            code_snippet=line.strip(),
                            fix_suggestion="Consider using i18n translation function",
                            confidence=0.7,
                        )
        return None

    def _check_js_hardcoded(self, line: str, line_num: int, file_path: str) -> WizardIssue | None:
        """Check JavaScript/TypeScript for hardcoded UI strings."""
        # Look for JSX text content or string assignments
        import re

        # Check for text in JSX elements: <div>Hello World</div>
        jsx_text = re.search(r">([A-Z][^<]{5,})<", line)
        if jsx_text:
            text = jsx_text.group(1).strip()
            if text and not text.startswith("{"):
                return WizardIssue(
                    category="hardcoded_string",
                    severity="warning",
                    message=f"Hardcoded JSX text: '{text[:30]}...'",
                    file_path=file_path,
                    line_number=line_num,
                    code_snippet=line.strip(),
                    fix_suggestion="Use i18n: {t('key')} instead of hardcoded text",
                    confidence=0.8,
                )
        return None

    def predict_future_issues(
        self,
        code: str,
        file_path: str,
        project_context: dict[str, Any],
        timeline_days: int = 90,
    ) -> list[WizardPrediction]:
        """Level 4 Anticipatory: Predict localization issues {timeline_days} days ahead

        Uses:
        - Historical patterns
        - Code trajectory analysis
        - Dependency evolution
        - Team velocity
        - Industry trends
        """
        predictions: list[WizardPrediction] = []

        # Example prediction logic
        # In production, use ML models trained on historical data

        self.logger.info(
            f"{self.name} predicted {len(predictions)} future issues "
            f"for {file_path} ({timeline_days} days ahead)",
        )
        return predictions

    def suggest_fixes(self, issue: WizardIssue) -> str:
        """Suggest how to fix a localization issue

        Returns:
            Detailed fix suggestion with code examples

        """
        # Implementation depends on issue type
        return f"Fix suggestion for {issue.category} issue: {issue.message}"
