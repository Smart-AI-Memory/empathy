"""Baseline and Suppression System

Hybrid approach for managing finding suppressions:
1. Inline comments - Line-specific suppressions
2. JSON baseline files - Project/file/rule-level suppressions

Supports:
- Suppress known false positives without fixing
- Time-limited suppressions (TTL)
- Team override workflow for security exceptions
- Audit trail for compliance

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import copy
import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

# =============================================================================
# Inline Comment Patterns
# =============================================================================

# Patterns for inline suppressions
# Format: # empathy:disable RULE_CODE [reason="explanation"]
INLINE_DISABLE_PATTERN = re.compile(
    r"#\s*empathy:disable\s+(\S+)(?:\s+reason=[\"']([^\"']+)[\"'])?",
    re.IGNORECASE,
)

# Format: # empathy:disable-next-line RULE_CODE [reason="explanation"]
INLINE_DISABLE_NEXT_PATTERN = re.compile(
    r"#\s*empathy:disable-next-line\s+(\S+)(?:\s+reason=[\"']([^\"']+)[\"'])?",
    re.IGNORECASE,
)

# Format: # empathy:disable-file RULE_CODE [reason="explanation"]
INLINE_DISABLE_FILE_PATTERN = re.compile(
    r"#\s*empathy:disable-file\s+(\S+)(?:\s+reason=[\"']([^\"']+)[\"'])?",
    re.IGNORECASE,
)


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class Suppression:
    """A suppression entry from baseline or inline comment."""

    rule_code: str
    reason: str = ""
    source: str = "baseline"  # "baseline" or "inline"
    file_path: str | None = None  # None = project-wide
    line_number: int | None = None  # None = file-wide or project-wide
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = ""
    expires_at: str | None = None  # ISO timestamp for TTL
    tool: str | None = None  # Specific tool or None for all


@dataclass
class SuppressionMatch:
    """Result of checking if a finding is suppressed."""

    is_suppressed: bool
    suppression: Suppression | None = None
    match_type: str = ""  # "exact", "file", "project", "inline"


# =============================================================================
# Baseline File Schema
# =============================================================================

BASELINE_SCHEMA = {
    "version": "1.0",
    "created_at": "",
    "updated_at": "",
    "suppressions": {
        "project": [],  # Project-wide suppressions
        "files": {},  # {file_path: [suppressions]}
        "rules": {},  # {rule_code: suppression_config}
    },
    "metadata": {
        "description": "",
        "maintainer": "",
    },
}


# =============================================================================
# BaselineManager
# =============================================================================


class BaselineManager:
    """Manages finding suppressions using hybrid approach.

    Usage:
        manager = BaselineManager(project_root="/path/to/project")
        manager.load()  # Load .empathy-baseline.json

        # Check if a finding should be suppressed
        match = manager.is_suppressed(
            rule_code="B001",
            file_path="src/foo.py",
            line_number=42,
            tool="security"
        )

        if match.is_suppressed:
            print(f"Suppressed: {match.suppression.reason}")
    """

    def __init__(self, project_root: str | Path):
        """Initialize baseline manager.

        Args:
            project_root: Root directory of the project

        """
        self.project_root = Path(project_root)
        self.baseline_path = self.project_root / ".empathy-baseline.json"
        self.baseline: dict[str, Any] = {}
        self.inline_cache: dict[str, list[Suppression]] = {}  # {file_path: [suppressions]}

    def load(self) -> bool:
        """Load baseline from JSON file.

        Returns:
            True if loaded successfully, False if no baseline exists

        """
        if not self.baseline_path.exists():
            self.baseline = copy.deepcopy(BASELINE_SCHEMA)
            return False

        try:
            with open(self.baseline_path) as f:
                self.baseline = json.load(f)
            return True
        except (json.JSONDecodeError, OSError) as e:
            print(f"Warning: Failed to load baseline: {e}")
            self.baseline = copy.deepcopy(BASELINE_SCHEMA)
            return False

    def save(self) -> bool:
        """Save baseline to JSON file.

        Returns:
            True if saved successfully

        """
        self.baseline["updated_at"] = datetime.now().isoformat()

        try:
            with open(self.baseline_path, "w") as f:
                json.dump(self.baseline, f, indent=2)
            return True
        except OSError as e:
            print(f"Warning: Failed to save baseline: {e}")
            return False

    def parse_inline_suppressions(self, file_path: str, content: str) -> list[Suppression]:
        """Parse inline suppression comments from file content.

        Args:
            file_path: Path to the file (for tracking)
            content: File content to parse

        Returns:
            List of Suppression entries found

        """
        suppressions = []
        lines = content.split("\n")

        file_wide_rules: set[str] = set()

        for i, line in enumerate(lines, start=1):
            # Check for file-wide disable at top of file
            if i <= 10:  # Only check first 10 lines for file-wide
                file_match = INLINE_DISABLE_FILE_PATTERN.search(line)
                if file_match:
                    rule_code, reason = file_match.groups()
                    file_wide_rules.add(rule_code.upper())
                    suppressions.append(
                        Suppression(
                            rule_code=rule_code.upper(),
                            reason=reason or "File-wide suppression",
                            source="inline",
                            file_path=file_path,
                            line_number=None,  # File-wide
                        ),
                    )

            # Check for same-line disable
            same_line_match = INLINE_DISABLE_PATTERN.search(line)
            if same_line_match:
                rule_code, reason = same_line_match.groups()
                if rule_code.upper() not in file_wide_rules:
                    suppressions.append(
                        Suppression(
                            rule_code=rule_code.upper(),
                            reason=reason or "Inline suppression",
                            source="inline",
                            file_path=file_path,
                            line_number=i,
                        ),
                    )

            # Check for disable-next-line
            next_line_match = INLINE_DISABLE_NEXT_PATTERN.search(line)
            if next_line_match:
                rule_code, reason = next_line_match.groups()
                suppressions.append(
                    Suppression(
                        rule_code=rule_code.upper(),
                        reason=reason or "Next-line suppression",
                        source="inline",
                        file_path=file_path,
                        line_number=i + 1,  # Applies to next line
                    ),
                )

        return suppressions

    def scan_file_for_inline(self, file_path: str) -> list[Suppression]:
        """Scan a file for inline suppressions and cache results.

        Args:
            file_path: Path to file (relative to project root)

        Returns:
            List of suppressions found

        """
        full_path = self.project_root / file_path

        if not full_path.exists():
            return []

        # Check cache first
        if file_path in self.inline_cache:
            return self.inline_cache[file_path]

        try:
            content = full_path.read_text(encoding="utf-8", errors="ignore")
            suppressions = self.parse_inline_suppressions(file_path, content)
            self.inline_cache[file_path] = suppressions
            return suppressions
        except OSError:
            return []

    def is_suppressed(
        self,
        rule_code: str,
        file_path: str | None = None,
        line_number: int | None = None,
        tool: str | None = None,
    ) -> SuppressionMatch:
        """Check if a finding should be suppressed.

        Checks in order (most specific to least):
        1. Inline comment at exact line
        2. Inline file-wide suppression
        3. Baseline file-specific suppression
        4. Baseline project-wide suppression
        5. Baseline rule-wide suppression

        Args:
            rule_code: The rule/error code (e.g., "B001", "W291")
            file_path: File path (relative to project root)
            line_number: Line number in file
            tool: Tool name (e.g., "security", "lint")

        Returns:
            SuppressionMatch indicating if suppressed and why

        """
        rule_code = rule_code.upper()
        now = datetime.now()

        # 1. Check inline suppressions (most specific)
        if file_path:
            inline_suppressions = self.scan_file_for_inline(file_path)

            for supp in inline_suppressions:
                if supp.rule_code != rule_code:
                    continue

                # Exact line match
                if line_number and supp.line_number == line_number:
                    return SuppressionMatch(
                        is_suppressed=True,
                        suppression=supp,
                        match_type="inline_exact",
                    )

                # File-wide inline suppression
                if supp.line_number is None:
                    return SuppressionMatch(
                        is_suppressed=True,
                        suppression=supp,
                        match_type="inline_file",
                    )

        # 2. Check baseline file-specific suppressions
        if file_path:
            file_suppressions = (
                self.baseline.get("suppressions", {}).get("files", {}).get(file_path, [])
            )
            for supp_dict in file_suppressions:
                if not self._matches_rule(supp_dict, rule_code, tool):
                    continue

                if self._is_expired(supp_dict, now):
                    continue

                # Check line match if specified
                if line_number and supp_dict.get("line_number"):
                    if supp_dict["line_number"] == line_number:
                        return SuppressionMatch(
                            is_suppressed=True,
                            suppression=self._dict_to_suppression(supp_dict, file_path),
                            match_type="baseline_line",
                        )
                elif not supp_dict.get("line_number"):
                    # File-wide baseline suppression
                    return SuppressionMatch(
                        is_suppressed=True,
                        suppression=self._dict_to_suppression(supp_dict, file_path),
                        match_type="baseline_file",
                    )

        # 3. Check project-wide suppressions
        project_suppressions = self.baseline.get("suppressions", {}).get("project", [])
        for supp_dict in project_suppressions:
            if not self._matches_rule(supp_dict, rule_code, tool):
                continue

            if self._is_expired(supp_dict, now):
                continue

            return SuppressionMatch(
                is_suppressed=True,
                suppression=self._dict_to_suppression(supp_dict),
                match_type="baseline_project",
            )

        # 4. Check rule-wide suppressions
        rule_suppressions = self.baseline.get("suppressions", {}).get("rules", {})
        if rule_code in rule_suppressions:
            supp_dict = rule_suppressions[rule_code]

            if not self._is_expired(supp_dict, now):
                # Check if tool matches (if specified)
                if tool and supp_dict.get("tool") and supp_dict["tool"] != tool:
                    pass  # Tool doesn't match, don't suppress
                else:
                    return SuppressionMatch(
                        is_suppressed=True,
                        suppression=self._dict_to_suppression(
                            {**supp_dict, "rule_code": rule_code},
                        ),
                        match_type="baseline_rule",
                    )

        # Not suppressed
        return SuppressionMatch(is_suppressed=False)

    def add_suppression(
        self,
        rule_code: str,
        reason: str,
        scope: str = "project",
        file_path: str | None = None,
        line_number: int | None = None,
        tool: str | None = None,
        ttl_days: int | None = None,
        created_by: str = "",
    ) -> bool:
        """Add a suppression to the baseline file.

        Args:
            rule_code: Rule code to suppress
            reason: Reason for suppression (required)
            scope: "project", "file", or "rule"
            file_path: Required for "file" scope
            line_number: Optional line number for "file" scope
            tool: Optional tool restriction
            ttl_days: Days until suppression expires (None = never)
            created_by: Who added this suppression

        Returns:
            True if added successfully

        """
        if not reason:
            raise ValueError("Suppression reason is required for audit trail")

        rule_code = rule_code.upper()
        now = datetime.now()

        expires_at = None
        if ttl_days:
            expires_at = (now + timedelta(days=ttl_days)).isoformat()

        supp_entry: dict[str, Any] = {
            "rule_code": rule_code,
            "reason": reason,
            "created_at": now.isoformat(),
            "created_by": created_by,
            "expires_at": expires_at,
        }

        if tool:
            supp_entry["tool"] = tool

        if scope == "project":
            self.baseline.setdefault("suppressions", {}).setdefault("project", []).append(
                supp_entry,
            )
        elif scope == "file":
            if not file_path:
                raise ValueError("file_path required for file scope")

            if line_number:
                supp_entry["line_number"] = line_number

            self.baseline.setdefault("suppressions", {}).setdefault("files", {}).setdefault(
                file_path,
                [],
            ).append(supp_entry)
        elif scope == "rule":
            self.baseline.setdefault("suppressions", {}).setdefault("rules", {})[rule_code] = (
                supp_entry
            )
        else:
            raise ValueError(f"Invalid scope: {scope}")

        return self.save()

    def filter_findings(self, findings: list[dict], tool: str | None = None) -> list[dict]:
        """Filter a list of findings, removing suppressed ones.

        Args:
            findings: List of finding dicts with rule_code, file_path, line_number
            tool: Tool name for all findings

        Returns:
            List of non-suppressed findings

        """
        result = []

        for finding in findings:
            rule_code = finding.get("code", "") or finding.get("rule_code", "")
            file_path = finding.get("file_path", "")
            line_number = finding.get("line_number")
            finding_tool = finding.get("tool", tool)

            match = self.is_suppressed(
                rule_code=rule_code,
                file_path=file_path,
                line_number=line_number,
                tool=finding_tool,
            )

            if not match.is_suppressed:
                result.append(finding)
            else:
                # Mark as suppressed for transparency
                finding["_suppressed"] = True
                finding["_suppression_reason"] = (
                    match.suppression.reason if match.suppression else ""
                )
                finding["_suppression_type"] = match.match_type

        return result

    def get_suppression_stats(self) -> dict[str, Any]:
        """Get statistics about current suppressions.

        Returns:
            Dict with suppression counts and details

        """
        now = datetime.now()
        by_scope: dict[str, int] = {"project": 0, "file": 0, "rule": 0, "inline": 0}
        total = 0
        expired = 0
        expiring_soon = 0

        # Project-wide
        project = self.baseline.get("suppressions", {}).get("project", [])
        by_scope["project"] = len(project)
        total += len(project)

        for supp in project:
            if self._is_expired(supp, now):
                expired += 1
            elif self._expires_within_days(supp, now, 7):
                expiring_soon += 1

        # File-specific
        files = self.baseline.get("suppressions", {}).get("files", {})
        file_count = sum(len(supps) for supps in files.values())
        by_scope["file"] = file_count
        total += file_count

        # Rule-wide
        rules = self.baseline.get("suppressions", {}).get("rules", {})
        by_scope["rule"] = len(rules)
        total += len(rules)

        # Inline (from cache)
        inline_count = sum(len(supps) for supps in self.inline_cache.values())
        by_scope["inline"] = inline_count
        total += inline_count

        return {
            "total": total,
            "by_scope": by_scope,
            "expired": expired,
            "expiring_soon": expiring_soon,
        }

    def cleanup_expired(self) -> int:
        """Remove expired suppressions from baseline.

        Returns:
            Number of suppressions removed

        """
        now = datetime.now()
        removed = 0

        # Clean project suppressions
        project = self.baseline.get("suppressions", {}).get("project", [])
        original_len = len(project)
        project[:] = [s for s in project if not self._is_expired(s, now)]
        removed += original_len - len(project)

        # Clean file suppressions
        files = self.baseline.get("suppressions", {}).get("files", {})
        for _file_path, supps in files.items():
            original_len = len(supps)
            supps[:] = [s for s in supps if not self._is_expired(s, now)]
            removed += original_len - len(supps)

        # Clean rule suppressions
        rules = self.baseline.get("suppressions", {}).get("rules", {})
        expired_rules = [r for r, s in rules.items() if self._is_expired(s, now)]
        for rule in expired_rules:
            del rules[rule]
            removed += 1

        if removed > 0:
            self.save()

        return removed

    # =========================================================================
    # Private Helpers
    # =========================================================================

    def _matches_rule(self, supp_dict: dict, rule_code: str, tool: str | None = None) -> bool:
        """Check if suppression matches rule and optional tool."""
        if supp_dict.get("rule_code", "").upper() != rule_code:
            return False

        if tool and supp_dict.get("tool"):
            return bool(supp_dict["tool"] == tool)

        return True

    def _is_expired(self, supp_dict: dict, now: datetime) -> bool:
        """Check if suppression has expired."""
        expires_at = supp_dict.get("expires_at")
        if not expires_at:
            return False

        try:
            expiry = datetime.fromisoformat(expires_at)
            return now > expiry
        except ValueError:
            return False

    def _expires_within_days(self, supp_dict: dict, now: datetime, days: int) -> bool:
        """Check if suppression expires within N days."""
        expires_at = supp_dict.get("expires_at")
        if not expires_at:
            return False

        try:
            expiry = datetime.fromisoformat(expires_at)
            return now < expiry <= now + timedelta(days=days)
        except ValueError:
            return False

    def _dict_to_suppression(self, supp_dict: dict, file_path: str | None = None) -> Suppression:
        """Convert dict to Suppression dataclass."""
        return Suppression(
            rule_code=supp_dict.get("rule_code", ""),
            reason=supp_dict.get("reason", ""),
            source="baseline",
            file_path=file_path,
            line_number=supp_dict.get("line_number"),
            created_at=supp_dict.get("created_at", ""),
            created_by=supp_dict.get("created_by", ""),
            expires_at=supp_dict.get("expires_at"),
            tool=supp_dict.get("tool"),
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_baseline_file(
    project_root: str | Path,
    description: str = "",
    maintainer: str = "",
) -> Path:
    """Create a new baseline file with empty suppressions.

    Args:
        project_root: Root directory of the project
        description: Description of the baseline
        maintainer: Maintainer contact

    Returns:
        Path to created baseline file

    """
    project_root = Path(project_root)
    baseline_path = project_root / ".empathy-baseline.json"

    now = datetime.now().isoformat()
    baseline = {
        "version": "1.0",
        "created_at": now,
        "updated_at": now,
        "suppressions": {
            "project": [],
            "files": {},
            "rules": {},
        },
        "metadata": {
            "description": description or "Empathy inspection baseline",
            "maintainer": maintainer,
        },
    }

    with open(baseline_path, "w") as f:
        json.dump(baseline, f, indent=2)

    return baseline_path
