"""
Pattern Extraction Wizard

Level 3 wizard that detects bug fixes in git diffs and suggests
storing them as patterns for future reference.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import hashlib
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard


class PatternExtractionWizard(BaseWizard):
    """
    Detects bug fixes and suggests pattern storage.

    Analyzes git diffs to identify:
    - Null checks added
    - Error handling added
    - Async/await fixes
    - Import fixes
    - Type fixes

    Suggests pre-filled patterns for easy storage.
    """

    @property
    def name(self) -> str:
        return "PatternExtractionWizard"

    @property
    def level(self) -> int:
        return 3  # Proactive

    def __init__(self, patterns_dir: str = "./patterns", **kwargs):
        super().__init__(**kwargs)
        self.patterns_dir = Path(patterns_dir)

        # Detection patterns for different fix types
        self._fix_patterns = {
            "null_reference": {
                "added": [
                    r"\?\.",  # Optional chaining
                    r"\?\?\s*\[",  # Nullish coalescing with array
                    r"\?\?\s*\{",  # Nullish coalescing with object
                    r"if\s*\(\s*\w+\s*(!=|!==)\s*null",  # Explicit null check
                    r"\.get\s*\(",  # Python .get() method
                    r"getattr\s*\([^,]+,\s*[^,]+,\s*",  # Python getattr with default
                    r"or\s*\[\]",  # Python or [] fallback
                    r"or\s*\{\}",  # Python or {} fallback
                ],
                "commit_keywords": ["null", "undefined", "none", "optional", "fallback"],
                "description": "Null/undefined reference fix",
            },
            "async_timing": {
                "added": [
                    r"\bawait\s+",  # Added await
                    r"async\s+def\s+",  # Made function async
                    r"\.then\s*\(",  # Added promise handling
                    r"asyncio\.gather",  # Added asyncio gather
                ],
                "commit_keywords": ["await", "async", "promise", "concurrent"],
                "description": "Async/timing fix",
            },
            "error_handling": {
                "added": [
                    r"try\s*[:\{]",  # Try block
                    r"except\s+",  # Python except
                    r"catch\s*\(",  # JS/TS catch
                    r"\.catch\s*\(",  # Promise catch
                    r"finally\s*[:\{]",  # Finally block
                    r"raise\s+\w+Error",  # Python raise
                    r"throw\s+new\s+\w+Error",  # JS throw
                ],
                "commit_keywords": ["error", "exception", "catch", "handle", "try"],
                "description": "Error handling improvement",
            },
            "type_mismatch": {
                "added": [
                    r":\s*(str|int|float|bool|list|dict)\s*[=\)]",  # Python type hints
                    r":\s*(string|number|boolean|object)\s*[;=]",  # TS types
                    r"isinstance\s*\(",  # Python isinstance
                    r"typeof\s+\w+\s*===",  # JS typeof check
                    r"as\s+(str|int|float)",  # Python cast
                ],
                "commit_keywords": ["type", "cast", "convert", "parse"],
                "description": "Type mismatch fix",
            },
            "import_error": {
                "added": [
                    r"from\s+\w+\s+import",  # Python import
                    r"import\s+\w+\s+from",  # ES6 import
                    r"require\s*\(",  # CommonJS require
                    r"try:\s*\n\s*import",  # Conditional import
                ],
                "commit_keywords": ["import", "module", "package", "dependency"],
                "description": "Import/dependency fix",
            },
        }

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze git diff for potential bug fix patterns.

        Args:
            context: {
                "diff": str - Git diff content (optional, will fetch if not provided)
                "commit_message": str - Commit message (optional)
                "commits": int - Number of recent commits to analyze (default 1)
            }

        Returns:
            {
                "suggested_patterns": list of suggested patterns,
                "predictions": list of predictions,
                "recommendations": list of recommendations,
                "confidence": float
            }
        """
        diff = context.get("diff")
        commit_message = context.get("commit_message", "")
        commits = context.get("commits", 1)

        # SECURITY: Validate commits parameter to prevent command injection
        # Must be a positive integer within reasonable bounds
        try:
            commits = int(commits)
            if commits < 1 or commits > 100:
                commits = 1
        except (TypeError, ValueError):
            commits = 1

        # Fetch diff if not provided
        if not diff:
            diff, commit_message = self._get_git_diff(commits)

        if not diff:
            return {
                "suggested_patterns": [],
                "predictions": [
                    {
                        "type": "no_changes",
                        "severity": "info",
                        "description": "No git changes detected to analyze.",
                    }
                ],
                "recommendations": ["Make some code changes and try again."],
                "confidence": 0.0,
            }

        # Analyze the diff
        suggested_patterns = self._extract_patterns(diff, commit_message)

        # Generate predictions
        predictions = self._generate_predictions(suggested_patterns)

        # Generate recommendations
        recommendations = self._generate_recommendations(suggested_patterns)

        return {
            "suggested_patterns": suggested_patterns,
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": self._calculate_confidence(suggested_patterns),
            "metadata": {
                "wizard": self.name,
                "level": self.level,
                "timestamp": datetime.now().isoformat(),
                "diff_lines": len(diff.split("\n")),
            },
        }

    def _get_git_diff(self, commits: int = 1) -> tuple[str, str]:
        """Get git diff and commit message."""
        try:
            # Get diff
            diff_result = subprocess.run(
                ["git", "diff", f"HEAD~{commits}", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            diff = diff_result.stdout if diff_result.returncode == 0 else ""

            # Get commit message
            msg_result = subprocess.run(
                ["git", "log", f"-{commits}", "--format=%s%n%b"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            message = msg_result.stdout if msg_result.returncode == 0 else ""

            return diff, message
        except Exception:
            return "", ""

    def _extract_patterns(self, diff: str, commit_message: str) -> list[dict]:
        """Extract potential bug fix patterns from diff."""
        suggested = []
        commit_lower = commit_message.lower()

        # Parse diff to get changed files and added lines
        current_file = ""
        added_lines: list[str] = []

        for line in diff.split("\n"):
            if line.startswith("diff --git"):
                # Save previous file's patterns
                if current_file and added_lines:
                    file_patterns = self._analyze_file_changes(
                        current_file, added_lines, commit_lower
                    )
                    suggested.extend(file_patterns)

                # Start new file
                match = re.search(r"b/(.+)$", line)
                current_file = match.group(1) if match else ""
                added_lines = []

            elif line.startswith("+") and not line.startswith("+++"):
                added_lines.append(line[1:])  # Remove + prefix

        # Don't forget last file
        if current_file and added_lines:
            file_patterns = self._analyze_file_changes(current_file, added_lines, commit_lower)
            suggested.extend(file_patterns)

        return suggested

    def _analyze_file_changes(
        self,
        file_path: str,
        added_lines: list[str],
        commit_message: str,
    ) -> list[dict]:
        """Analyze changes to a single file for patterns."""
        patterns = []
        added_content = "\n".join(added_lines)

        for pattern_type, config in self._fix_patterns.items():
            # Check if any fix patterns were added
            matches = []
            for regex in config["added"]:
                found = re.findall(regex, added_content)
                if found:
                    matches.extend(found)

            if not matches:
                continue

            # Check commit message for keywords
            keyword_match = any(kw in commit_message for kw in config["commit_keywords"])

            # Calculate confidence
            confidence = 0.5
            if keyword_match:
                confidence += 0.3
            if len(matches) > 1:
                confidence += 0.1
            confidence = min(confidence, 0.95)

            # Generate pattern suggestion
            pattern_id = self._generate_pattern_id(file_path, pattern_type)

            patterns.append(
                {
                    "pattern_id": pattern_id,
                    "type": pattern_type,
                    "file": file_path,
                    "matches": matches[:3],  # Limit examples
                    "confidence": confidence,
                    "commit_keyword_match": keyword_match,
                    "description": config["description"],
                    "pre_filled": {
                        "bug_id": pattern_id,
                        "date": datetime.now().isoformat(),
                        "file_path": file_path,
                        "error_type": pattern_type,
                        "error_message": f"Detected {str(config['description']).lower()}",
                        "root_cause": "",  # User fills in
                        "fix_applied": config["description"],
                        "fix_code": matches[0] if matches else "",
                        "status": "investigating",
                    },
                }
            )

        return patterns

    def _generate_pattern_id(self, file_path: str, pattern_type: str) -> str:
        """Generate a unique pattern ID."""
        date_str = datetime.now().strftime("%Y%m%d")
        content = f"{file_path}:{pattern_type}:{datetime.now().isoformat()}"
        hash_suffix = hashlib.md5(content.encode(), usedforsecurity=False).hexdigest()[:8]
        return f"bug_{date_str}_{hash_suffix}"

    def _generate_predictions(self, patterns: list[dict]) -> list[dict]:
        """Generate Level 3 predictions about patterns."""
        predictions: list[dict] = []

        if not patterns:
            return predictions

        # High confidence patterns
        high_conf = [p for p in patterns if p["confidence"] >= 0.8]
        if high_conf:
            predictions.append(
                {
                    "type": "high_value_patterns",
                    "severity": "info",
                    "description": f"{len(high_conf)} high-confidence fix patterns detected. These are likely valuable for future reference.",
                }
            )

        # Common pattern types
        type_counts: dict[str, int] = {}
        for p in patterns:
            type_counts[p["type"]] = type_counts.get(p["type"], 0) + 1

        most_common = max(type_counts.items(), key=lambda x: x[1]) if type_counts else None
        if most_common and most_common[1] >= 2:
            predictions.append(
                {
                    "type": "recurring_fix_type",
                    "severity": "warning",
                    "description": f"Multiple {most_common[0]} fixes detected ({most_common[1]}). Consider adding preventive checks.",
                }
            )

        return predictions

    def _generate_recommendations(self, patterns: list[dict]) -> list[str]:
        """Generate recommendations for pattern storage."""
        if not patterns:
            return ["No fix patterns detected in recent changes."]

        recommendations = []

        # Suggest storing high confidence patterns
        high_conf = [p for p in patterns if p["confidence"] >= 0.7]
        if high_conf:
            recommendations.append(
                f"Consider storing {len(high_conf)} detected fix pattern(s) for future reference."
            )

        # Add specific storage command
        if patterns:
            first = patterns[0]
            recommendations.append(
                f"To store: empathy patterns resolve {first['pattern_id']} "
                f"--root-cause '<cause>' --fix '{first['description']}'"
            )

        return recommendations

    def _calculate_confidence(self, patterns: list[dict]) -> float:
        """Calculate overall confidence score."""
        if not patterns:
            return 0.0

        avg_conf = sum(p["confidence"] for p in patterns) / len(patterns)
        # Boost if multiple patterns detected
        if len(patterns) >= 2:
            avg_conf = min(avg_conf + 0.1, 1.0)

        return float(round(avg_conf, 2))

    async def save_pattern(self, pattern: dict) -> bool:
        """
        Save a suggested pattern to storage.

        Args:
            pattern: Pattern dict from suggested_patterns

        Returns:
            True if saved successfully
        """
        pre_filled = pattern.get("pre_filled", {})
        if not pre_filled:
            return False

        # Determine output directory
        output_dir = self.patterns_dir / "debugging"
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write pattern file
        output_file = output_dir / f"{pre_filled['bug_id']}.json"
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(pre_filled, f, indent=2, default=str)
            return True
        except OSError:
            return False


# CLI support
if __name__ == "__main__":
    import asyncio

    async def main():
        wizard = PatternExtractionWizard()
        result = await wizard.analyze({"commits": 3})
        print(json.dumps(result, indent=2, default=str))

    asyncio.run(main())
