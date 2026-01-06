"""Pattern-Based Code Review Wizard

Level 4 wizard that reviews code against historical bug patterns.
Uses resolved bugs to generate detection rules, then scans
new/changed code for similar anti-patterns.

Usage:
    wizard = CodeReviewWizard()
    result = await wizard.analyze({
        "files": ["src/api.py", "src/utils.py"],
        "staged_only": True,
    })

CLI:
    empathy review src/api.py
    empathy review --staged

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import json
import logging
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


@dataclass
class ReviewFinding:
    """A potential issue found during code review."""

    file: str
    line: int
    pattern_type: str
    pattern_id: str
    description: str
    historical_cause: str
    suggestion: str
    code_snippet: str
    confidence: float
    severity: str = "warning"

    def to_dict(self) -> dict:
        return {
            "file": self.file,
            "line": self.line,
            "pattern_type": self.pattern_type,
            "pattern_id": self.pattern_id,
            "description": self.description,
            "historical_cause": self.historical_cause,
            "suggestion": self.suggestion,
            "code_snippet": self.code_snippet,
            "confidence": self.confidence,
            "severity": self.severity,
        }


@dataclass
class AntiPatternRule:
    """Detection rule generated from historical bugs."""

    pattern_type: str
    description: str
    detect_patterns: list[str] = field(default_factory=list)
    safe_patterns: list[str] = field(default_factory=list)
    fix_suggestion: str = ""
    reference_bugs: list[str] = field(default_factory=list)
    severity: str = "warning"


class CodeReviewWizard(BaseWizard):
    """Reviews code against historical bug patterns.

    This is the capstone wizard that brings together pattern learning
    to prevent bugs before they occur.
    """

    @property
    def name(self) -> str:
        return "CodeReviewWizard"

    @property
    def level(self) -> int:
        return 4  # Anticipatory

    def __init__(self, patterns_dir: str = "./patterns", **kwargs):
        super().__init__(**kwargs)
        self.patterns_dir = Path(patterns_dir)
        self._rules: list[AntiPatternRule] = []
        self._bugs_loaded = False

        # Built-in anti-pattern rules (extended by loaded bugs)
        self._builtin_rules = {
            "null_reference": AntiPatternRule(
                pattern_type="null_reference",
                description="Potential null/undefined reference",
                detect_patterns=[
                    r"\.map\s*\(",  # Array method that fails on null
                    r"\.forEach\s*\(",
                    r"\.filter\s*\(",
                    r"\.reduce\s*\(",
                    r"\[\s*\d+\s*\]",  # Direct index access
                    r"\.length\b",  # Length property on potentially null
                    r"for\s+\w+\s+in\s+",  # Iteration over potentially null
                ],
                safe_patterns=[
                    r"\?\.",  # Optional chaining
                    r"\?\?\s*\[",  # Nullish coalescing with array
                    r"if\s*\(\s*\w+",  # Preceded by if check
                    r"&&\s*\w+\.",  # Short-circuit check
                    r"\.get\s*\(",  # Python safe get
                    r"or\s*\[\]",  # Python or fallback
                ],
                fix_suggestion="Add null check: data?.items ?? [] or if (data) {...}",
                severity="warning",
            ),
            "async_timing": AntiPatternRule(
                pattern_type="async_timing",
                description="Potential missing await",
                detect_patterns=[
                    r"async\s+\w+\s*\([^)]*\)\s*[^{]*\{[^}]*\w+\s*\(",  # Async fn with call
                    r"Promise\.\w+\s*\(",  # Promise methods
                    r"\.then\s*\([^)]*\)\s*$",  # Dangling then
                ],
                safe_patterns=[
                    r"\bawait\s+",  # Has await
                    r"return\s+\w+\s*\(",  # Returned promise
                    r"\.then\s*\([^)]*\)\s*\.\s*catch",  # Has catch
                ],
                fix_suggestion="Add await keyword or handle promise with .then().catch()",
                severity="warning",
            ),
            "error_handling": AntiPatternRule(
                pattern_type="error_handling",
                description="Missing error handling",
                detect_patterns=[
                    r"fetch\s*\(",  # Fetch without error handling
                    r"axios\.\w+\s*\(",  # Axios calls
                    r"requests\.\w+\s*\(",  # Python requests
                    r"\.json\s*\(",  # JSON parsing
                    r"JSON\.parse\s*\(",  # JSON.parse
                    r"open\s*\([^)]+\)",  # File operations
                ],
                safe_patterns=[
                    r"try\s*[:\{]",  # In try block
                    r"\.catch\s*\(",  # Has catch
                    r"except\s+",  # Python except
                    r"with\s+open",  # Python context manager
                ],
                fix_suggestion="Wrap in try/catch or add .catch() handler",
                severity="info",
            ),
        }

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze files for anti-patterns based on historical bugs.

        Args:
            context: {
                "files": list[str] - Files to review
                "staged_only": bool - Only review staged changes
                "diff": str - Direct diff content (optional)
                "severity_threshold": str - Minimum severity (info/warning/error)
            }

        Returns:
            {
                "findings": list of ReviewFinding dicts,
                "summary": summary stats,
                "predictions": Level 4 predictions,
                "recommendations": actionable steps,
                "confidence": overall confidence
            }

        """
        # Load historical patterns if not already loaded
        if not self._bugs_loaded:
            self._load_historical_bugs()
            self._bugs_loaded = True

        files = context.get("files", [])
        staged_only = context.get("staged_only", False)
        diff = context.get("diff")
        severity_threshold = context.get("severity_threshold", "info")

        # Get files to review
        if staged_only:
            files = self._get_staged_files()
        elif not files and not diff:
            # Default to recently changed files
            files = self._get_recent_changed_files()

        # Perform review
        findings = []

        if diff:
            findings.extend(self._review_diff(diff))
        else:
            for file_path in files:
                findings.extend(self._review_file(file_path))

        # Filter by severity
        severity_order = {"info": 0, "warning": 1, "error": 2}
        threshold = severity_order.get(severity_threshold, 0)
        findings = [f for f in findings if severity_order.get(f.severity, 0) >= threshold]

        # Generate predictions and recommendations
        predictions = self._generate_predictions(findings)
        recommendations = self._generate_recommendations(findings)

        return {
            "findings": [f.to_dict() for f in findings],
            "summary": {
                "total_findings": len(findings),
                "by_severity": self._count_by_severity(findings),
                "by_type": self._count_by_type(findings),
                "files_reviewed": len(files) if files else 1,
            },
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(findings),
            "metadata": {
                "wizard": self.name,
                "level": self.level,
                "timestamp": datetime.now().isoformat(),
                "rules_loaded": len(self._rules) + len(self._builtin_rules),
            },
        }

    def _load_historical_bugs(self) -> None:
        """Load resolved bugs and generate detection rules."""
        for debug_dir in ["debugging", "debugging_demo", "repo_test/debugging"]:
            dir_path = self.patterns_dir / debug_dir
            if not dir_path.exists():
                continue

            for json_file in dir_path.glob("bug_*.json"):
                try:
                    with open(json_file, encoding="utf-8") as f:
                        bug = json.load(f)

                    # Only use resolved bugs with fixes
                    if bug.get("status") != "resolved":
                        continue
                    if not bug.get("fix_applied"):
                        continue

                    # Create rule from bug
                    rule = self._bug_to_rule(bug)
                    if rule:
                        self._rules.append(rule)

                except (json.JSONDecodeError, OSError):
                    continue

    def _bug_to_rule(self, bug: dict) -> AntiPatternRule | None:
        """Convert a resolved bug to a detection rule."""
        error_type = bug.get("error_type", "unknown")
        fix_code = bug.get("fix_code", "")

        # Start with builtin rule for this type if exists
        base_rule = self._builtin_rules.get(error_type)
        if not base_rule:
            return None

        # Extend with bug-specific info
        return AntiPatternRule(
            pattern_type=error_type,
            description=f"{base_rule.description} (historical: {bug.get('bug_id', 'unknown')})",
            detect_patterns=base_rule.detect_patterns,
            safe_patterns=base_rule.safe_patterns + self._extract_safe_patterns(fix_code),
            fix_suggestion=bug.get("fix_applied", base_rule.fix_suggestion),
            reference_bugs=[bug.get("bug_id", "unknown")],
            severity=base_rule.severity,
        )

    def _extract_safe_patterns(self, fix_code: str) -> list[str]:
        """Extract regex patterns from fix code that indicate safety."""
        patterns: list[str] = []
        if not fix_code:
            return patterns

        # Common safe patterns to detect
        if "?." in fix_code:
            patterns.append(r"\?\.")
        if "??" in fix_code:
            patterns.append(r"\?\?")
        if "await" in fix_code.lower():
            patterns.append(r"\bawait\s+")
        if ".get(" in fix_code:
            patterns.append(r"\.get\s*\(")
        if "try" in fix_code.lower():
            patterns.append(r"\btry\s*[:\{]")

        return patterns

    def _review_file(self, file_path: str) -> list[ReviewFinding]:
        """Review a single file for anti-patterns."""
        findings: list[ReviewFinding] = []

        try:
            path = Path(file_path)
            if not path.exists():
                return findings

            content = path.read_text(encoding="utf-8", errors="ignore")
        except (OSError, UnicodeDecodeError):
            return findings

        lines = content.split("\n")

        for line_num, line in enumerate(lines, 1):
            # Skip comments and empty lines
            stripped = line.strip()
            if not stripped or stripped.startswith(("#", "//", "/*", "*")):
                continue

            # Check all rules
            for rule in list(self._builtin_rules.values()) + self._rules:
                finding = self._check_line_against_rule(file_path, line_num, line, rule, lines)
                if finding:
                    findings.append(finding)

        return findings

    def _review_diff(self, diff: str) -> list[ReviewFinding]:
        """Review a git diff for anti-patterns."""
        findings = []
        current_file = ""
        line_num = 0

        for line in diff.split("\n"):
            # Track current file
            if line.startswith("diff --git"):
                match = re.search(r"b/(.+)$", line)
                current_file = match.group(1) if match else ""
                continue

            # Track line numbers
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                line_num = int(match.group(1)) if match else 0
                continue

            # Check added lines
            if line.startswith("+") and not line.startswith("+++"):
                code_line = line[1:]  # Remove + prefix
                for rule in list(self._builtin_rules.values()) + self._rules:
                    finding = self._check_line_against_rule(
                        current_file,
                        line_num,
                        code_line,
                        rule,
                        [],
                    )
                    if finding:
                        findings.append(finding)
                line_num += 1

        return findings

    def _check_line_against_rule(
        self,
        file_path: str,
        line_num: int,
        line: str,
        rule: AntiPatternRule,
        all_lines: list[str],
    ) -> ReviewFinding | None:
        """Check a single line against a rule."""
        # Check if any detect pattern matches
        detected = False
        for pattern in rule.detect_patterns:
            if re.search(pattern, line):
                detected = True
                break

        if not detected:
            return None

        # Check if any safe pattern is present (in this line or nearby)
        context_window = 3
        start = max(0, line_num - context_window - 1)
        end = min(len(all_lines), line_num + context_window)
        context = "\n".join(all_lines[start:end]) if all_lines else line

        for safe_pattern in rule.safe_patterns:
            if re.search(safe_pattern, context):
                return None  # Safe pattern found, no issue

        # Calculate confidence based on rule quality
        confidence = 0.7
        if rule.reference_bugs:
            confidence += 0.1  # Backed by historical data
        if len(rule.detect_patterns) > 2:
            confidence -= 0.1  # More generic rule

        return ReviewFinding(
            file=file_path,
            line=line_num,
            pattern_type=rule.pattern_type,
            pattern_id=rule.reference_bugs[0] if rule.reference_bugs else "builtin",
            description=rule.description,
            historical_cause=(
                f"Historical: {rule.reference_bugs}" if rule.reference_bugs else "Built-in rule"
            ),
            suggestion=rule.fix_suggestion,
            code_snippet=line.strip()[:80],
            confidence=min(confidence, 0.95),
            severity=rule.severity,
        )

    def _get_staged_files(self) -> list[str]:
        """Get list of staged files from git."""
        try:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except Exception as e:
            # Optional: Git staged files unavailable (not a git repo)
            logger.debug(f"Could not get staged files: {e}")
            pass
        return []

    def _get_recent_changed_files(self) -> list[str]:
        """Get recently changed files from git."""
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD~3", "HEAD"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return [f.strip() for f in result.stdout.strip().split("\n") if f.strip()]
        except Exception as e:
            # Optional: Git history unavailable (not a git repo)
            logger.debug(f"Could not get recent changed files: {e}")
            pass
        return []

    def _count_by_severity(self, findings: list[ReviewFinding]) -> dict[str, int]:
        """Count findings by severity."""
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.severity] = counts.get(f.severity, 0) + 1
        return counts

    def _count_by_type(self, findings: list[ReviewFinding]) -> dict[str, int]:
        """Count findings by pattern type."""
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.pattern_type] = counts.get(f.pattern_type, 0) + 1
        return counts

    def _calculate_confidence(self, findings: list[ReviewFinding]) -> float:
        """Calculate overall confidence score."""
        if not findings:
            return 1.0  # No issues found with high confidence

        avg_conf = sum(f.confidence for f in findings) / len(findings)
        return round(avg_conf, 2)

    def _generate_predictions(self, findings: list[ReviewFinding]) -> list[dict[str, Any]]:
        """Generate Level 4 predictions."""
        predictions: list[dict[str, Any]] = []

        if not findings:
            predictions.append(
                {
                    "type": "clean_review",
                    "severity": "info",
                    "description": "No anti-patterns detected. Code looks clean!",
                },
            )
            return predictions

        # Predict based on finding types
        type_counts = self._count_by_type(findings)
        most_common = max(type_counts.items(), key=lambda x: x[1]) if type_counts else None

        if most_common and most_common[1] >= 2:
            predictions.append(
                {
                    "type": "recurring_issue",
                    "severity": "warning",
                    "description": f"Multiple {most_common[0]} issues ({most_common[1]}). "
                    f"This pattern may indicate a systemic problem.",
                    "prevention_steps": [
                        f"Add linting rule for {most_common[0]}",
                        "Consider code review checklist",
                        "Add unit tests for edge cases",
                    ],
                },
            )

        # High severity findings
        error_count = sum(1 for f in findings if f.severity == "error")
        if error_count > 0:
            predictions.append(
                {
                    "type": "high_risk",
                    "severity": "error",
                    "description": f"{error_count} high-severity issue(s) found. "
                    f"These may cause runtime errors.",
                },
            )

        return predictions

    def _generate_recommendations(self, findings: list[ReviewFinding]) -> list[str]:
        """Generate actionable recommendations."""
        if not findings:
            return ["No issues found. Proceed with commit."]

        recommendations = []

        # Group by type for consolidated recommendations
        type_counts = self._count_by_type(findings)
        for pattern_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            sample = next((f for f in findings if f.pattern_type == pattern_type), None)
            if sample:
                recommendations.append(f"Fix {count} {pattern_type} issue(s): {sample.suggestion}")

        # Add general recommendation
        if len(findings) > 3:
            recommendations.append("Consider running the full test suite before committing.")

        return recommendations

    def format_terminal_output(self, result: dict) -> str:
        """Format review results for terminal output."""
        lines = [
            "Code Review Results",
            "=" * 40,
            "",
        ]

        findings = result.get("findings", [])
        if not findings:
            lines.append("✓ No issues found!")
            lines.append("")
            return "\n".join(lines)

        for finding in findings:
            icon = (
                "⚠️"
                if finding["severity"] == "warning"
                else "❌"
                if finding["severity"] == "error"
                else "ℹ️"
            )
            lines.append(f"{icon}  {finding['file']}:{finding['line']}")
            lines.append(f"    Pattern: {finding['pattern_type']} ({finding['pattern_id']})")
            lines.append(f"    Risk: {finding['description']}")
            lines.append(f"    Historical: {finding['historical_cause']}")
            lines.append(f"    Suggestion: {finding['suggestion']}")
            lines.append(f"    Confidence: {finding['confidence']:.0%}")
            lines.append("")

        summary = result.get("summary", {})
        lines.append(
            f"Summary: {summary.get('total_findings', 0)} findings in {summary.get('files_reviewed', 0)} file(s)",
        )

        return "\n".join(lines)


# CLI support
if __name__ == "__main__":
    import asyncio
    import sys

    async def main():
        wizard = CodeReviewWizard()

        # Parse simple args
        files = sys.argv[1:] if len(sys.argv) > 1 else []
        staged = "--staged" in files
        files = [f for f in files if not f.startswith("--")]

        result = await wizard.analyze(
            {
                "files": files,
                "staged_only": staged,
            },
        )

        print(wizard.format_terminal_output(result))

    asyncio.run(main())
