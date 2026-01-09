"""Code Review Adapter

Wraps empathy_software_plugin.wizards.code_review_wizard
and converts its output to the unified ToolResult format.

Now includes language-aware review using CrossLanguagePatternLibrary
to apply appropriate patterns for each file type.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..state import ToolResult

# Language detection mapping
EXTENSION_TO_LANGUAGE = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".rs": "rust",
    ".go": "go",
    ".java": "java",
    ".kt": "kotlin",
    ".c": "c",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".cs": "csharp",
}


def get_file_language(file_path: str) -> str:
    """Detect programming language from file extension.

    Args:
        file_path: Path to the file

    Returns:
        Language identifier (e.g., "python", "javascript") or "unknown"

    """
    ext = Path(file_path).suffix.lower()
    return EXTENSION_TO_LANGUAGE.get(ext, "unknown")


class CodeReviewAdapter:
    """Adapter for the Code Review Wizard.

    Detects anti-patterns from historical bugs, reviews code against
    known issue patterns.

    Now language-aware: applies appropriate patterns for each file type
    using the CrossLanguagePatternLibrary.
    """

    def __init__(
        self,
        project_root: str,
        config: dict[str, Any] | None = None,
        security_context: list[dict] | None = None,
    ):
        """Initialize the adapter.

        Args:
            project_root: Root directory of the project
            config: Configuration overrides
            security_context: Security findings to inform review

        """
        self.project_root = Path(project_root)
        self.config = config or {}
        self.security_context = security_context or []

    async def analyze(
        self,
        target_files: list[str] | None = None,
        security_informed: bool = True,
    ) -> ToolResult:
        """Run code review and return unified result.

        Args:
            target_files: Specific files to review (default: all changed)
            security_informed: Use security context to focus review

        Returns:
            ToolResult with code review findings

        """
        start_time = time.time()

        try:
            # Import here to handle optional dependency
            from empathy_software_plugin.wizards.code_review_wizard import CodeReviewWizard

            wizard = CodeReviewWizard(patterns_dir=str(self.project_root / "patterns"))

            # Prepare context - wizard expects 'files' key, not 'target_files'
            # Get list of files to review
            files_to_review = target_files or []
            if not files_to_review:
                # Default to Python files in project
                files_to_review = [
                    str(f.relative_to(self.project_root))
                    for f in self.project_root.rglob("*.py")
                    if not any(
                        p in f.parts for p in ["node_modules", ".venv", "__pycache__", ".git"]
                    )
                ][
                    :50
                ]  # Limit to 50 files for performance

            # Group files by language for language-aware review
            files_by_language: dict[str, list[str]] = defaultdict(list)
            for f in files_to_review:
                lang = get_file_language(f)
                files_by_language[lang].append(f)

            # Get pattern library for cross-language insights
            pattern_library = None
            try:
                from empathy_software_plugin.wizards.debugging.language_patterns import (
                    get_pattern_library,
                )

                pattern_library = get_pattern_library()
            except ImportError:
                pass  # Pattern library not available, continue without

            context: dict[str, Any] = {
                "files": files_to_review,
                "staged_only": False,
                "severity_threshold": "info",
                "files_by_language": dict(files_by_language),  # Language-aware grouping
            }

            if security_informed and self.security_context:
                # Add security context as additional focus
                context["security_focus_files"] = [f["file_path"] for f in self.security_context]

            # Run analysis
            report = await wizard.analyze(context)

            # Convert findings to unified format
            findings: list[dict[str, Any]] = []
            findings_by_severity: dict[str, int] = {
                "critical": 0,
                "high": 0,
                "medium": 0,
                "low": 0,
                "info": 0,
            }

            for review_finding in report.get("findings", []):
                severity = self._map_severity(review_finding.get("severity", "medium"))
                findings_by_severity[severity] += 1

                # Detect language for this finding's file
                file_path = review_finding.get("file_path", "")
                file_language = get_file_language(file_path)

                # Get cross-language fix suggestions if pattern library available
                cross_lang_insight = None
                if pattern_library and file_language != "unknown":
                    pattern_id = review_finding.get("pattern_id", "")
                    # Try to find universal pattern for this issue
                    for pattern in pattern_library.patterns.values():
                        if file_language in pattern.language_manifestations:
                            rule_name = pattern.language_manifestations[file_language]
                            if rule_name.lower() in pattern_id.lower():
                                cross_lang_insight = pattern.universal_fix_strategy
                                break

                finding = {
                    "finding_id": f"cr_{len(findings)}",
                    "tool": "code_review",
                    "category": "review",
                    "severity": severity,
                    "file_path": file_path,
                    "line_number": review_finding.get("line_number"),
                    "code": review_finding.get("pattern_id", "REVIEW"),
                    "message": review_finding.get("description", ""),
                    "evidence": review_finding.get("code_snippet", ""),
                    "confidence": review_finding.get("confidence", 0.8),
                    "fixable": False,
                    "fix_command": None,
                    "historical_matches": review_finding.get("historical_bugs", []),
                    "remediation": review_finding.get("recommendation", ""),
                    "language": file_language,  # Language-aware
                    "cross_language_insight": cross_lang_insight,  # Universal fix strategy
                }
                findings.append(finding)

            # Calculate score
            score = self._calculate_score(findings_by_severity)
            status = "pass" if score >= 85 else "warn" if score >= 70 else "fail"

            duration_ms = int((time.time() - start_time) * 1000)

            # Extract metadata from wizard's summary
            summary = report.get("summary", {})

            return ToolResult(
                tool_name="code_review",
                status=status,
                score=score,
                findings_count=len(findings),
                findings=findings,
                findings_by_severity=findings_by_severity,
                duration_ms=duration_ms,
                metadata={
                    "files_reviewed": summary.get("files_reviewed", len(files_to_review)),
                    "patterns_checked": report.get("metadata", {}).get("rules_loaded", 0),
                    "security_informed": security_informed,
                    "by_type": summary.get("by_type", {}),
                    "languages_detected": list(files_by_language.keys()),
                    "files_by_language": {k: len(v) for k, v in files_by_language.items()},
                    "pattern_library_available": pattern_library is not None,
                },
                error_message="",
            )

        except ImportError:
            return self._create_skip_result("code_review_wizard module not available", start_time)
        except Exception as e:
            return self._create_error_result(str(e), start_time)

    def _map_severity(self, severity: str) -> str:
        """Map review severity to unified severity."""
        mapping = {
            "critical": "critical",
            "high": "high",
            "medium": "medium",
            "low": "low",
            "info": "info",
            "warning": "medium",
        }
        return mapping.get(severity.lower(), "medium")

    def _calculate_score(self, by_severity: dict[str, int]) -> int:
        """Calculate code review score.

        Note: Code review findings are often suggestions rather than errors,
        so we use gentler penalties. The goal is to surface patterns worth
        investigating, not to penalize heavily for potential issues.
        """
        penalties = {
            "critical": 10,
            "high": 5,
            "medium": 0.1,  # Most review findings are medium suggestions
            "low": 0.02,
            "info": 0,
        }

        total_penalty = sum(
            count * penalties.get(severity, 0) for severity, count in by_severity.items()
        )

        # Cap penalty at 60 to ensure minimum score of 40 with many findings
        return max(40, 100 - int(min(total_penalty, 60)))

    def _create_skip_result(self, reason: str, start_time: float) -> ToolResult:
        """Create a skip result."""
        return ToolResult(
            tool_name="code_review",
            status="skip",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={"skip_reason": reason},
            error_message="",
        )

    def _create_error_result(self, error: str, start_time: float) -> ToolResult:
        """Create an error result."""
        return ToolResult(
            tool_name="code_review",
            status="error",
            score=0,
            findings_count=0,
            findings=[],
            findings_by_severity={},
            duration_ms=int((time.time() - start_time) * 1000),
            metadata={},
            error_message=error,
        )
