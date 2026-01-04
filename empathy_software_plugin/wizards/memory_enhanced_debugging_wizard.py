"""Memory-Enhanced Debugging Wizard (Level 4+)

Debugging wizard that correlates current errors with historical patterns.
Demonstrates what's possible with persistent memory: AI that remembers
past bugs and how they were fixed.

"This error looks like something we fixed 3 months ago—here's what worked."

Key capabilities enabled by persistent memory:
- Cross-session bug correlation
- Historical fix recommendations
- Resolution time predictions
- Team knowledge accumulation

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import hashlib
import json
import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from .base_wizard import BaseWizard

logger = logging.getLogger(__name__)


@dataclass
class DebuggingWizardConfig:
    """Configuration for deployment mode (web vs local)"""

    deployment_mode: str = "local"  # "web" or "local"
    max_files: int | None = None  # None = unlimited
    max_file_size_mb: float | None = None
    folder_upload_enabled: bool = True
    show_upgrade_cta: bool = False

    @classmethod
    def web_config(cls) -> "DebuggingWizardConfig":
        """Website deployment - limited features"""
        return cls(
            deployment_mode="web",
            max_files=5,
            max_file_size_mb=1.0,
            folder_upload_enabled=False,
            show_upgrade_cta=True,
        )

    @classmethod
    def local_config(cls) -> "DebuggingWizardConfig":
        """Local installation - full features"""
        return cls(
            deployment_mode="local",
            max_files=None,
            max_file_size_mb=None,
            folder_upload_enabled=True,
            show_upgrade_cta=False,
        )


@dataclass
class BugResolution:
    """A historical bug resolution pattern"""

    bug_id: str
    date: str
    file_path: str
    error_type: str
    error_message: str
    root_cause: str
    fix_applied: str
    fix_code: str | None
    resolution_time_minutes: int
    resolved_by: str
    confidence: float = 1.0


@dataclass
class HistoricalMatch:
    """A match from historical bug patterns"""

    resolution: BugResolution
    similarity_score: float
    matching_factors: list[str] = field(default_factory=list)


class MemoryEnhancedDebuggingWizard(BaseWizard):
    """Memory-Enhanced Debugging Wizard - Level 4+

    What's now possible that wasn't before:

    WITHOUT PERSISTENT MEMORY (Before):
    - Every debugging session starts from zero
    - Same bugs diagnosed repeatedly
    - Fix knowledge lost between sessions
    - No learning from team's collective experience

    WITH PERSISTENT MEMORY (After):
    - AI remembers past bugs and fixes
    - "This looks like bug #247 from 3 months ago"
    - Recommends proven fixes
    - Team knowledge compounds over time

    Example:
        >>> wizard = MemoryEnhancedDebuggingWizard()
        >>> result = await wizard.analyze({
        ...     "error_message": "TypeError: Cannot read property 'map' of undefined",
        ...     "file_path": "src/components/UserList.tsx",
        ...     "stack_trace": "...",
        ...     "correlate_with_history": True
        ... })
        >>> print(result["historical_matches"])
        # Shows similar bugs from the past with their fixes

    """

    @property
    def name(self) -> str:
        return "Memory-Enhanced Debugging Wizard"

    @property
    def level(self) -> int:
        return 4  # Level 4+ with memory enhancement

    def __init__(
        self,
        pattern_storage_path: str = "./patterns/debugging",
        config: DebuggingWizardConfig | None = None,
    ):
        """Initialize the memory-enhanced debugging wizard.

        Args:
            pattern_storage_path: Path to git-based pattern storage
            config: Deployment configuration (web vs local mode)

        """
        super().__init__()
        self.pattern_storage_path = Path(pattern_storage_path)
        self.pattern_storage_path.mkdir(parents=True, exist_ok=True)
        self.config = config or DebuggingWizardConfig.local_config()

        # Error pattern classifiers
        self.error_patterns = {
            "null_reference": [
                r"cannot read property .* of (undefined|null)",
                r"TypeError:.*undefined",
                r"NoneType.*has no attribute",
                r"null pointer",
            ],
            "type_mismatch": [
                r"TypeError:.*expected.*got",
                r"cannot assign.*to.*",
                r"incompatible types",
            ],
            "async_timing": [
                r"promise.*rejected",
                r"unhandled.*promise",
                r"await.*undefined",
                r"race condition",
            ],
            "import_error": [
                r"cannot find module",
                r"ModuleNotFoundError",
                r"ImportError",
                r"no module named",
            ],
            "api_error": [
                r"fetch.*failed",
                r"network.*error",
                r"connection.*refused",
                r"timeout.*exceeded",
            ],
        }

    def validate_file_inputs(
        self,
        files: list[dict[str, Any]],
        is_folder_upload: bool = False,
    ) -> dict[str, Any]:
        """Validate file inputs against the deployment configuration limits.

        Args:
            files: List of file dicts with 'path' and 'size_bytes' keys
            is_folder_upload: Whether this is a folder upload operation

        Returns:
            Validation result dict with:
            - valid: bool indicating if inputs pass validation
            - errors: list of validation error messages
            - warnings: list of warning messages (e.g., upgrade CTA)

        """
        errors: list[str] = []
        warnings: list[str] = []

        # Check folder upload permission
        if is_folder_upload and not self.config.folder_upload_enabled:
            errors.append(
                "Folder upload is not available in web mode. "
                "Please upload individual files or install locally for full features.",
            )

        # Check file count limit
        if self.config.max_files is not None:
            if len(files) > self.config.max_files:
                errors.append(
                    f"Too many files: {len(files)} provided, "
                    f"maximum {self.config.max_files} allowed in {self.config.deployment_mode} mode.",
                )

        # Check individual file sizes
        if self.config.max_file_size_mb is not None:
            max_bytes = self.config.max_file_size_mb * 1024 * 1024
            for file_info in files:
                file_path = file_info.get("path", "unknown")
                file_size = file_info.get("size_bytes", 0)
                if file_size > max_bytes:
                    errors.append(
                        f"File '{file_path}' exceeds size limit: "
                        f"{file_size / (1024 * 1024):.2f}MB > {self.config.max_file_size_mb}MB",
                    )

        # Add upgrade CTA if configured
        if self.config.show_upgrade_cta and errors:
            warnings.append(
                "Upgrade to local installation for unlimited files and folder uploads. "
                "Visit https://empathy-framework.dev/install for details.",
            )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "config": {
                "deployment_mode": self.config.deployment_mode,
                "max_files": self.config.max_files,
                "max_file_size_mb": self.config.max_file_size_mb,
                "folder_upload_enabled": self.config.folder_upload_enabled,
            },
        }

    async def analyze(self, context: dict[str, Any]) -> dict[str, Any]:
        """Analyze a bug with historical correlation.

        Context expects:
            - error_message: The error message
            - file_path: File where error occurred
            - stack_trace: Optional stack trace
            - line_number: Optional line number
            - code_snippet: Optional surrounding code
            - correlate_with_history: Enable historical matching (default True)

        Returns:
            Analysis with:
            - error_classification: Type of error
            - historical_matches: Similar past bugs
            - recommended_fix: AI-suggested fix based on history
            - confidence: Confidence in recommendation
            - predictions: Level 4 predictions

        """
        error_message = context.get("error_message", "")
        file_path = context.get("file_path", "unknown")
        stack_trace = context.get("stack_trace", "")
        line_number = context.get("line_number")
        code_snippet = context.get("code_snippet", "")
        correlate_history = context.get("correlate_with_history", True)

        # Step 1: Classify the error
        error_type = self._classify_error(error_message, stack_trace)

        # Step 2: Analyze current context
        current_analysis = {
            "error_type": error_type,
            "error_message": error_message,
            "file_path": file_path,
            "line_number": line_number,
            "file_type": Path(file_path).suffix if file_path else "unknown",
            "likely_causes": self._identify_likely_causes(error_type, code_snippet),
        }

        # Step 3: Historical correlation (the magic!)
        historical_matches = []
        recommended_fix = None
        fix_confidence = 0.5

        if correlate_history:
            historical_matches = self._find_historical_matches(
                error_type=error_type,
                error_message=error_message,
                file_path=file_path,
            )

            if historical_matches:
                # Use the best match to recommend a fix
                best_match = historical_matches[0]
                recommended_fix = self._generate_fix_recommendation(best_match, current_analysis)
                fix_confidence = best_match.similarity_score

        # Step 4: Generate predictions (Level 4)
        predictions = self._generate_predictions(error_type, current_analysis, historical_matches)

        # Step 5: Generate recommendations
        recommendations = self._generate_recommendations(
            current_analysis,
            historical_matches,
            recommended_fix,
        )

        result = {
            "error_classification": current_analysis,
            "historical_matches": [
                {
                    "date": m.resolution.date,
                    "file": m.resolution.file_path,
                    "error_type": m.resolution.error_type,
                    "root_cause": m.resolution.root_cause,
                    "fix_applied": m.resolution.fix_applied,
                    "fix_code": m.resolution.fix_code,
                    "resolution_time_minutes": m.resolution.resolution_time_minutes,
                    "similarity_score": m.similarity_score,
                    "matching_factors": m.matching_factors,
                }
                for m in historical_matches[:5]  # Top 5 matches
            ],
            "historical_correlation_enabled": correlate_history,
            "matches_found": len(historical_matches),
            "recommended_fix": recommended_fix,
            "predictions": predictions,
            "recommendations": recommendations,
            "confidence": fix_confidence,
            "memory_benefit": self._calculate_memory_benefit(historical_matches),
        }

        # Store this bug for future correlation
        await self._store_bug_pattern(context, result)

        return result

    def _classify_error(self, error_message: str, stack_trace: str) -> str:
        """Classify the error type based on patterns"""
        combined_text = f"{error_message} {stack_trace}".lower()

        for error_type, patterns in self.error_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return error_type

        return "unknown"

    def _identify_likely_causes(self, error_type: str, code_snippet: str) -> list[dict[str, Any]]:
        """Identify likely causes based on error type"""
        causes_by_type = {
            "null_reference": [
                {
                    "cause": "Accessing property before data loads",
                    "check": "Add null/undefined check before access",
                    "likelihood": 0.7,
                },
                {
                    "cause": "API returned null unexpectedly",
                    "check": "Verify API response structure",
                    "likelihood": 0.5,
                },
                {
                    "cause": "Optional chaining missing",
                    "check": "Use ?. operator or default values",
                    "likelihood": 0.6,
                },
            ],
            "type_mismatch": [
                {
                    "cause": "Wrong data type from API",
                    "check": "Validate API response types",
                    "likelihood": 0.6,
                },
                {
                    "cause": "Type conversion missing",
                    "check": "Add explicit type conversion",
                    "likelihood": 0.5,
                },
            ],
            "async_timing": [
                {
                    "cause": "Missing await keyword",
                    "check": "Verify all async calls are awaited",
                    "likelihood": 0.7,
                },
                {
                    "cause": "Race condition in state updates",
                    "check": "Use proper state management",
                    "likelihood": 0.5,
                },
            ],
            "import_error": [
                {
                    "cause": "Module not installed",
                    "check": "Run npm install or pip install",
                    "likelihood": 0.8,
                },
                {
                    "cause": "Wrong import path",
                    "check": "Verify relative/absolute path",
                    "likelihood": 0.6,
                },
            ],
            "api_error": [
                {
                    "cause": "Network connectivity",
                    "check": "Verify server is running",
                    "likelihood": 0.5,
                },
                {
                    "cause": "CORS policy",
                    "check": "Check server CORS configuration",
                    "likelihood": 0.6,
                },
            ],
        }

        return causes_by_type.get(error_type, [{"cause": "Unknown", "likelihood": 0.3}])

    def _find_historical_matches(
        self,
        error_type: str,
        error_message: str,
        file_path: str,
    ) -> list[HistoricalMatch]:
        """Find historical bug patterns that match the current error.

        This is where persistent memory enables what wasn't possible before:
        searching through accumulated team knowledge of past bugs.
        """
        matches = []

        # Search pattern storage
        pattern_files = list(self.pattern_storage_path.glob("*.json"))

        for pattern_file in pattern_files:
            try:
                with open(pattern_file, encoding="utf-8") as f:
                    stored = json.load(f)

                resolution = BugResolution(
                    bug_id=stored.get("bug_id", pattern_file.stem),
                    date=stored.get("date", "unknown"),
                    file_path=stored.get("file_path", ""),
                    error_type=stored.get("error_type", ""),
                    error_message=stored.get("error_message", ""),
                    root_cause=stored.get("root_cause", ""),
                    fix_applied=stored.get("fix_applied", ""),
                    fix_code=stored.get("fix_code"),
                    resolution_time_minutes=stored.get("resolution_time_minutes", 0),
                    resolved_by=stored.get("resolved_by", "unknown"),
                )

                # Calculate similarity
                similarity, factors = self._calculate_similarity(
                    error_type,
                    error_message,
                    file_path,
                    resolution,
                )

                if similarity > 0.3:  # Threshold for relevance
                    matches.append(
                        HistoricalMatch(
                            resolution=resolution,
                            similarity_score=similarity,
                            matching_factors=factors,
                        ),
                    )

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Could not parse pattern {pattern_file}: {e}")
                continue

        # Sort by similarity
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        return matches

    def _calculate_similarity(
        self,
        error_type: str,
        error_message: str,
        file_path: str,
        resolution: BugResolution,
    ) -> tuple[float, list[str]]:
        """Calculate similarity score between current error and historical pattern"""
        score = 0.0
        factors = []

        # Same error type (strong signal)
        if error_type == resolution.error_type:
            score += 0.4
            factors.append(f"Same error type: {error_type}")

        # Similar file type
        current_ext = Path(file_path).suffix
        historical_ext = Path(resolution.file_path).suffix
        if current_ext == historical_ext:
            score += 0.15
            factors.append(f"Same file type: {current_ext}")

        # Similar file path pattern
        if self._paths_similar(file_path, resolution.file_path):
            score += 0.15
            factors.append("Similar file location")

        # Error message similarity
        msg_similarity = self._message_similarity(error_message, resolution.error_message)
        if msg_similarity > 0.5:
            score += 0.3 * msg_similarity
            factors.append(f"Similar error message ({int(msg_similarity * 100)}% match)")

        return min(score, 1.0), factors

    def _paths_similar(self, path1: str, path2: str) -> bool:
        """Check if two file paths are in similar locations"""
        parts1 = Path(path1).parts
        parts2 = Path(path2).parts

        # Check if they share common directory patterns
        common_dirs = {"src", "components", "api", "utils", "lib", "services"}
        dirs1 = set(parts1) & common_dirs
        dirs2 = set(parts2) & common_dirs

        return len(dirs1 & dirs2) > 0

    def _message_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between two error messages"""
        # Simple word overlap similarity
        words1 = set(msg1.lower().split())
        words2 = set(msg2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _generate_fix_recommendation(
        self,
        match: HistoricalMatch,
        current_analysis: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate a fix recommendation based on historical match"""
        return {
            "based_on": f"Bug #{match.resolution.bug_id} from {match.resolution.date}",
            "original_fix": match.resolution.fix_applied,
            "fix_code": match.resolution.fix_code,
            "expected_resolution_time": f"{match.resolution.resolution_time_minutes} minutes",
            "confidence": match.similarity_score,
            "adaptation_notes": self._generate_adaptation_notes(match, current_analysis),
        }

    def _generate_adaptation_notes(
        self,
        match: HistoricalMatch,
        current_analysis: dict[str, Any],
    ) -> list[str]:
        """Generate notes on how to adapt the historical fix"""
        notes = []

        if match.resolution.file_path != current_analysis.get("file_path"):
            notes.append(
                f"Original fix was in {Path(match.resolution.file_path).name}, "
                f"adapt for {Path(current_analysis.get('file_path', '')).name}",
            )

        if match.similarity_score < 0.8:
            notes.append("Moderate similarity - verify fix applies to your specific case")

        return notes

    def _generate_predictions(
        self,
        error_type: str,
        current_analysis: dict[str, Any],
        historical_matches: list[HistoricalMatch],
    ) -> list[dict[str, Any]]:
        """Generate Level 4 predictions"""
        predictions = []

        # Predict based on error type patterns
        if error_type == "null_reference":
            predictions.append(
                {
                    "type": "related_null_errors",
                    "severity": "medium",
                    "description": (
                        "Based on patterns, null reference errors often cluster. "
                        "Check similar components for the same issue."
                    ),
                    "prevention_steps": [
                        "Add defensive null checks across related files",
                        "Consider TypeScript strict null checks",
                        "Review API contract for nullable fields",
                    ],
                },
            )

        # Predict based on historical patterns
        if len(historical_matches) >= 2:
            avg_resolution_time = sum(
                m.resolution.resolution_time_minutes for m in historical_matches[:3]
            ) / min(len(historical_matches), 3)

            predictions.append(
                {
                    "type": "resolution_time_estimate",
                    "severity": "info",
                    "description": (
                        f"Based on {len(historical_matches)} similar past bugs, "
                        f"expect ~{int(avg_resolution_time)} minute resolution time."
                    ),
                    "prevention_steps": [],
                },
            )

        # Predict recurrence if same error type appears multiple times
        same_type_count = sum(
            1 for m in historical_matches if m.resolution.error_type == error_type
        )
        if same_type_count >= 3:
            predictions.append(
                {
                    "type": "recurring_pattern",
                    "severity": "high",
                    "description": (
                        f"This error type has occurred {same_type_count} times before. "
                        "Consider a systematic fix to prevent recurrence."
                    ),
                    "prevention_steps": [
                        "Add linting rule to catch this pattern",
                        "Create code review checklist item",
                        "Consider architectural change to eliminate root cause",
                    ],
                },
            )

        return predictions

    def _generate_recommendations(
        self,
        current_analysis: dict[str, Any],
        historical_matches: list[HistoricalMatch],
        recommended_fix: dict[str, Any] | None,
    ) -> list[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Historical match recommendations
        if recommended_fix:
            recommendations.append(
                f"📚 Historical match found! Try: {recommended_fix['original_fix']}",
            )
            if recommended_fix.get("fix_code"):
                recommendations.append(
                    f"💡 Example fix code available from {recommended_fix['based_on']}",
                )

        # Likely cause recommendations
        for cause in current_analysis.get("likely_causes", [])[:2]:
            cause_text = cause.get("cause", "Unknown")
            check_text = cause.get("check", "Investigate further")
            recommendations.append(f"🔍 Check: {cause_text} - {check_text}")

        # Memory benefit reminder
        if historical_matches:
            recommendations.append(
                f"⏱️  Memory saved you time: {len(historical_matches)} similar bugs found instantly",
            )
        else:
            recommendations.append(
                "💾 Tip: After fixing, resolution will be stored for future reference",
            )

        return recommendations

    def _calculate_memory_benefit(
        self,
        historical_matches: list[HistoricalMatch],
    ) -> dict[str, Any]:
        """Calculate the benefit provided by persistent memory"""
        if not historical_matches:
            return {
                "matches_found": 0,
                "time_saved_estimate": "N/A - no historical data yet",
                "value_statement": "Once resolved, this bug will help future debugging",
            }

        # Estimate time saved
        avg_resolution = sum(
            m.resolution.resolution_time_minutes for m in historical_matches[:3]
        ) / min(len(historical_matches), 3)

        time_saved = int(avg_resolution * 0.6)  # Estimate 60% time savings

        return {
            "matches_found": len(historical_matches),
            "time_saved_estimate": f"~{time_saved} minutes",
            "value_statement": (
                f"Persistent memory found {len(historical_matches)} similar bugs. "
                f"Without memory, you'd start from zero every time."
            ),
            "historical_insight": (
                f"Best match: {historical_matches[0].resolution.fix_applied}"
                if historical_matches
                else None
            ),
        }

    async def _store_bug_pattern(self, context: dict[str, Any], result: dict[str, Any]) -> None:
        """Store this bug for future correlation (when resolved)"""
        # Only store if we have meaningful information
        if not context.get("error_message"):
            return

        # Generate bug ID
        bug_hash = hashlib.md5(
            f"{context.get('error_message', '')}{context.get('file_path', '')}{datetime.now().isoformat()}".encode(),
            usedforsecurity=False,
        ).hexdigest()[:8]

        bug_id = f"bug_{datetime.now().strftime('%Y%m%d')}_{bug_hash}"

        # Create pattern record (will be updated when fix is applied)
        pattern = {
            "bug_id": bug_id,
            "date": datetime.now().isoformat(),
            "file_path": context.get("file_path", ""),
            "error_type": result.get("error_classification", {}).get("error_type", "unknown"),
            "error_message": context.get("error_message", ""),
            "root_cause": "",  # To be filled when resolved
            "fix_applied": "",  # To be filled when resolved
            "fix_code": None,  # To be filled when resolved
            "resolution_time_minutes": 0,  # To be filled when resolved
            "resolved_by": "",  # To be filled when resolved
            "status": "investigating",
        }

        # Store in pattern storage
        pattern_file = self.pattern_storage_path / f"{bug_id}.json"
        try:
            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(pattern, f, indent=2)
            logger.debug(f"Stored bug pattern: {bug_id}")
        except OSError as e:
            logger.warning(f"Could not store bug pattern: {e}")

    async def record_resolution(
        self,
        bug_id: str,
        root_cause: str,
        fix_applied: str,
        fix_code: str | None = None,
        resolution_time_minutes: int = 0,
        resolved_by: str = "developer",
    ) -> bool:
        """Record the resolution of a bug (updates stored pattern).

        Call this after successfully fixing a bug to store the knowledge
        for future correlation.

        Args:
            bug_id: The bug ID from the analyze result
            root_cause: What caused the bug
            fix_applied: Description of the fix
            fix_code: Optional code snippet of the fix
            resolution_time_minutes: How long it took to fix
            resolved_by: Who fixed it

        Returns:
            True if recorded successfully

        """
        pattern_file = self.pattern_storage_path / f"{bug_id}.json"

        if not pattern_file.exists():
            logger.warning(f"Bug {bug_id} not found in storage")
            return False

        try:
            with open(pattern_file, encoding="utf-8") as f:
                pattern = json.load(f)

            # Update with resolution
            pattern.update(
                {
                    "root_cause": root_cause,
                    "fix_applied": fix_applied,
                    "fix_code": fix_code,
                    "resolution_time_minutes": resolution_time_minutes,
                    "resolved_by": resolved_by,
                    "status": "resolved",
                    "resolved_date": datetime.now().isoformat(),
                },
            )

            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(pattern, f, indent=2)

            logger.info(f"Recorded resolution for {bug_id}")
            return True

        except (OSError, json.JSONDecodeError) as e:
            logger.error(f"Could not record resolution: {e}")
            return False
