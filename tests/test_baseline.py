"""Tests for agents/code_inspection/baseline.py

Tests the Baseline and Suppression System for managing finding suppressions.
"""

import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from agents.code_inspection.baseline import (
    BASELINE_SCHEMA,
    INLINE_DISABLE_FILE_PATTERN,
    INLINE_DISABLE_NEXT_PATTERN,
    INLINE_DISABLE_PATTERN,
    BaselineManager,
    Suppression,
    SuppressionMatch,
    create_baseline_file,
)


class TestSuppressionDataclass:
    """Tests for the Suppression dataclass."""

    def test_suppression_default_values(self):
        """Test that Suppression has correct default values."""
        supp = Suppression(rule_code="B001")

        assert supp.rule_code == "B001"
        assert supp.reason == ""
        assert supp.source == "baseline"
        assert supp.file_path is None
        assert supp.line_number is None
        assert supp.created_by == ""
        assert supp.expires_at is None
        assert supp.tool is None
        # created_at should be set to current time
        assert supp.created_at is not None

    def test_suppression_with_all_values(self):
        """Test creating Suppression with all values specified."""
        supp = Suppression(
            rule_code="S001",
            reason="Known false positive",
            source="inline",
            file_path="src/foo.py",
            line_number=42,
            created_at="2025-01-01T00:00:00",
            created_by="developer@test.com",
            expires_at="2025-06-01T00:00:00",
            tool="security",
        )

        assert supp.rule_code == "S001"
        assert supp.reason == "Known false positive"
        assert supp.source == "inline"
        assert supp.file_path == "src/foo.py"
        assert supp.line_number == 42
        assert supp.created_at == "2025-01-01T00:00:00"
        assert supp.created_by == "developer@test.com"
        assert supp.expires_at == "2025-06-01T00:00:00"
        assert supp.tool == "security"


class TestSuppressionMatchDataclass:
    """Tests for the SuppressionMatch dataclass."""

    def test_suppression_match_not_suppressed(self):
        """Test SuppressionMatch for non-suppressed case."""
        match = SuppressionMatch(is_suppressed=False)

        assert match.is_suppressed is False
        assert match.suppression is None
        assert match.match_type == ""

    def test_suppression_match_suppressed(self):
        """Test SuppressionMatch for suppressed case."""
        supp = Suppression(rule_code="B001", reason="Test")
        match = SuppressionMatch(is_suppressed=True, suppression=supp, match_type="inline_exact")

        assert match.is_suppressed is True
        assert match.suppression is supp
        assert match.match_type == "inline_exact"


class TestInlinePatterns:
    """Tests for inline suppression comment patterns."""

    def test_inline_disable_pattern_basic(self):
        """Test basic inline disable pattern."""
        line = "x = 1  # empathy:disable B001"
        match = INLINE_DISABLE_PATTERN.search(line)

        assert match is not None
        assert match.group(1) == "B001"
        assert match.group(2) is None

    def test_inline_disable_pattern_with_reason(self):
        """Test inline disable pattern with reason."""
        line = 'x = 1  # empathy:disable B001 reason="false positive"'
        match = INLINE_DISABLE_PATTERN.search(line)

        assert match is not None
        assert match.group(1) == "B001"
        assert match.group(2) == "false positive"

    def test_inline_disable_pattern_case_insensitive(self):
        """Test that inline disable pattern is case insensitive."""
        line = "x = 1  # EMPATHY:DISABLE B001"
        match = INLINE_DISABLE_PATTERN.search(line)

        assert match is not None
        assert match.group(1) == "B001"

    def test_inline_disable_next_pattern(self):
        """Test disable-next-line pattern."""
        line = "# empathy:disable-next-line W291 reason='trailing whitespace ok'"
        match = INLINE_DISABLE_NEXT_PATTERN.search(line)

        assert match is not None
        assert match.group(1) == "W291"
        assert match.group(2) == "trailing whitespace ok"

    def test_inline_disable_file_pattern(self):
        """Test disable-file pattern."""
        line = '# empathy:disable-file S001 reason="legacy code"'
        match = INLINE_DISABLE_FILE_PATTERN.search(line)

        assert match is not None
        assert match.group(1) == "S001"
        assert match.group(2) == "legacy code"

    def test_no_match_for_invalid_pattern(self):
        """Test that invalid patterns don't match."""
        line = "# empathy: disable B001"  # space after colon
        match = INLINE_DISABLE_PATTERN.search(line)

        assert match is None


class TestBaselineManager:
    """Tests for the BaselineManager class."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        return BaselineManager(temp_project)

    def test_init(self, temp_project):
        """Test BaselineManager initialization."""
        manager = BaselineManager(temp_project)

        assert manager.project_root == temp_project
        assert manager.baseline_path == temp_project / ".empathy-baseline.json"
        assert manager.baseline == {}
        assert manager.inline_cache == {}

    def test_load_no_baseline_file(self, manager):
        """Test loading when no baseline file exists."""
        result = manager.load()

        assert result is False
        assert manager.baseline == BASELINE_SCHEMA

    def test_load_existing_baseline_file(self, temp_project, manager):
        """Test loading an existing baseline file."""
        baseline_data = {
            "version": "1.0",
            "created_at": "2025-01-01T00:00:00",
            "updated_at": "2025-01-01T00:00:00",
            "suppressions": {
                "project": [{"rule_code": "B001", "reason": "Test"}],
                "files": {},
                "rules": {},
            },
            "metadata": {},
        }

        with open(temp_project / ".empathy-baseline.json", "w") as f:
            json.dump(baseline_data, f)

        result = manager.load()

        assert result is True
        assert manager.baseline["version"] == "1.0"
        assert len(manager.baseline["suppressions"]["project"]) == 1

    def test_load_invalid_json(self, temp_project, manager):
        """Test loading an invalid JSON baseline file."""
        with open(temp_project / ".empathy-baseline.json", "w") as f:
            f.write("invalid json {{{")

        result = manager.load()

        assert result is False
        assert manager.baseline == BASELINE_SCHEMA

    def test_save(self, manager):
        """Test saving baseline file."""
        manager.baseline = {"version": "1.0", "suppressions": {"project": []}}

        result = manager.save()

        assert result is True
        assert manager.baseline_path.exists()
        assert "updated_at" in manager.baseline

    def test_parse_inline_suppressions_same_line(self, manager):
        """Test parsing same-line inline suppression."""
        content = """
x = 1
y = eval(z)  # empathy:disable B001 reason="safe input"
z = 3
"""
        suppressions = manager.parse_inline_suppressions("test.py", content)

        assert len(suppressions) == 1
        assert suppressions[0].rule_code == "B001"
        assert suppressions[0].reason == "safe input"
        assert suppressions[0].line_number == 3
        assert suppressions[0].source == "inline"

    def test_parse_inline_suppressions_next_line(self, manager):
        """Test parsing disable-next-line suppression."""
        content = """
# empathy:disable-next-line W291 reason="intentional"
x = 1
z = 3
"""
        suppressions = manager.parse_inline_suppressions("test.py", content)

        assert len(suppressions) == 1
        assert suppressions[0].rule_code == "W291"
        assert suppressions[0].line_number == 3  # Applies to next line

    def test_parse_inline_suppressions_file_wide(self, manager):
        """Test parsing file-wide suppression at top of file."""
        content = """# empathy:disable-file S001 reason="legacy code"
import os
x = 1
"""
        suppressions = manager.parse_inline_suppressions("test.py", content)

        assert len(suppressions) == 1
        assert suppressions[0].rule_code == "S001"
        assert suppressions[0].line_number is None  # File-wide
        assert suppressions[0].reason == "legacy code"

    def test_parse_inline_suppressions_file_wide_not_after_line_10(self, manager):
        """Test that file-wide suppression only works in first 10 lines."""
        content = "\n" * 15 + "# empathy:disable-file S001"
        suppressions = manager.parse_inline_suppressions("test.py", content)

        # Should not be recognized as file-wide after line 10
        file_wide = [s for s in suppressions if s.line_number is None]
        assert len(file_wide) == 0

    def test_scan_file_for_inline_nonexistent_file(self, manager):
        """Test scanning a nonexistent file returns empty list."""
        result = manager.scan_file_for_inline("nonexistent.py")

        assert result == []

    def test_scan_file_for_inline_caches_results(self, temp_project, manager):
        """Test that scan results are cached."""
        test_file = temp_project / "test.py"
        test_file.write_text("x = 1  # empathy:disable B001\n")

        # First call
        result1 = manager.scan_file_for_inline("test.py")
        # Second call should use cache
        result2 = manager.scan_file_for_inline("test.py")

        assert result1 == result2
        assert "test.py" in manager.inline_cache


class TestBaselineManagerIsSuppressed:
    """Tests for the is_suppressed method."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_is_suppressed_no_suppression(self, manager):
        """Test is_suppressed returns false when not suppressed."""
        result = manager.is_suppressed("B001", "test.py", 10)

        assert result.is_suppressed is False
        assert result.suppression is None

    def test_is_suppressed_inline_exact(self, temp_project, manager):
        """Test inline exact line suppression."""
        test_file = temp_project / "test.py"
        test_file.write_text("x = eval(y)  # empathy:disable B001\n")

        result = manager.is_suppressed("B001", "test.py", 1)

        assert result.is_suppressed is True
        assert result.match_type == "inline_exact"
        assert result.suppression.rule_code == "B001"

    def test_is_suppressed_inline_file_wide(self, temp_project, manager):
        """Test inline file-wide suppression."""
        test_file = temp_project / "test.py"
        test_file.write_text("# empathy:disable-file B001\nx = eval(y)\n")

        result = manager.is_suppressed("B001", "test.py", 2)

        assert result.is_suppressed is True
        assert result.match_type == "inline_file"

    def test_is_suppressed_baseline_project(self, manager):
        """Test project-wide baseline suppression."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "W001", "reason": "Project-wide ignore"},
        )

        result = manager.is_suppressed("W001", "any_file.py", 42)

        assert result.is_suppressed is True
        assert result.match_type == "baseline_project"

    def test_is_suppressed_baseline_file(self, manager):
        """Test file-specific baseline suppression."""
        manager.baseline["suppressions"]["files"]["src/special.py"] = [
            {"rule_code": "B002", "reason": "Known issue in this file"},
        ]

        result = manager.is_suppressed("B002", "src/special.py", 100)

        assert result.is_suppressed is True
        assert result.match_type == "baseline_file"

    def test_is_suppressed_baseline_file_with_line(self, manager):
        """Test file-specific baseline suppression with line number."""
        manager.baseline["suppressions"]["files"]["src/special.py"] = [
            {"rule_code": "B002", "reason": "Known issue at this line", "line_number": 50},
        ]

        # Matching line number
        result1 = manager.is_suppressed("B002", "src/special.py", 50)
        assert result1.is_suppressed is True
        assert result1.match_type == "baseline_line"

        # Non-matching line number
        result2 = manager.is_suppressed("B002", "src/special.py", 51)
        assert result2.is_suppressed is False

    def test_is_suppressed_baseline_rule(self, manager):
        """Test rule-wide baseline suppression."""
        manager.baseline["suppressions"]["rules"]["W999"] = {
            "reason": "We never care about this rule",
        }

        result = manager.is_suppressed("W999", "anywhere.py", 1)

        assert result.is_suppressed is True
        assert result.match_type == "baseline_rule"

    def test_is_suppressed_case_insensitive(self, manager):
        """Test that rule code matching is case insensitive."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "b001", "reason": "Test"},  # lowercase
        )

        result = manager.is_suppressed("B001", "test.py", 1)  # uppercase

        assert result.is_suppressed is True

    def test_is_suppressed_expired_suppression(self, manager):
        """Test that expired suppressions are not matched."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Expired", "expires_at": past_date},
        )

        result = manager.is_suppressed("B001", "test.py", 1)

        assert result.is_suppressed is False

    def test_is_suppressed_tool_specific(self, manager):
        """Test tool-specific suppression matching."""
        manager.baseline["suppressions"]["rules"]["T001"] = {
            "reason": "Only for lint tool",
            "tool": "lint",
        }

        # Matching tool
        result1 = manager.is_suppressed("T001", "test.py", 1, tool="lint")
        assert result1.is_suppressed is True

        # Non-matching tool
        result2 = manager.is_suppressed("T001", "test.py", 1, tool="security")
        assert result2.is_suppressed is False


class TestBaselineManagerAddSuppression:
    """Tests for the add_suppression method."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_add_suppression_project_scope(self, manager):
        """Test adding a project-wide suppression."""
        result = manager.add_suppression(
            rule_code="B001",
            reason="Known false positive",
            scope="project",
        )

        assert result is True
        assert len(manager.baseline["suppressions"]["project"]) == 1
        supp = manager.baseline["suppressions"]["project"][0]
        assert supp["rule_code"] == "B001"
        assert supp["reason"] == "Known false positive"

    def test_add_suppression_file_scope(self, manager):
        """Test adding a file-specific suppression."""
        result = manager.add_suppression(
            rule_code="S001",
            reason="Legacy code",
            scope="file",
            file_path="src/legacy.py",
        )

        assert result is True
        assert "src/legacy.py" in manager.baseline["suppressions"]["files"]
        supps = manager.baseline["suppressions"]["files"]["src/legacy.py"]
        assert len(supps) == 1
        assert supps[0]["rule_code"] == "S001"

    def test_add_suppression_file_scope_with_line(self, manager):
        """Test adding a file-specific suppression with line number."""
        result = manager.add_suppression(
            rule_code="S001",
            reason="Specific line",
            scope="file",
            file_path="src/legacy.py",
            line_number=42,
        )

        assert result is True
        supp = manager.baseline["suppressions"]["files"]["src/legacy.py"][0]
        assert supp["line_number"] == 42

    def test_add_suppression_rule_scope(self, manager):
        """Test adding a rule-wide suppression."""
        result = manager.add_suppression(
            rule_code="W999",
            reason="We ignore this rule globally",
            scope="rule",
        )

        assert result is True
        assert "W999" in manager.baseline["suppressions"]["rules"]
        supp = manager.baseline["suppressions"]["rules"]["W999"]
        assert supp["reason"] == "We ignore this rule globally"

    def test_add_suppression_requires_reason(self, manager):
        """Test that add_suppression requires a reason."""
        with pytest.raises(ValueError, match="reason is required"):
            manager.add_suppression(rule_code="B001", reason="")

    def test_add_suppression_file_scope_requires_path(self, manager):
        """Test that file scope requires file_path."""
        with pytest.raises(ValueError, match="file_path required"):
            manager.add_suppression(rule_code="B001", reason="Test", scope="file")

    def test_add_suppression_invalid_scope(self, manager):
        """Test that invalid scope raises error."""
        with pytest.raises(ValueError, match="Invalid scope"):
            manager.add_suppression(rule_code="B001", reason="Test", scope="invalid")

    def test_add_suppression_with_ttl(self, manager):
        """Test adding suppression with TTL."""
        result = manager.add_suppression(
            rule_code="B001",
            reason="Temporary fix",
            scope="project",
            ttl_days=30,
        )

        assert result is True
        supp = manager.baseline["suppressions"]["project"][0]
        assert supp["expires_at"] is not None
        expiry = datetime.fromisoformat(supp["expires_at"])
        expected = datetime.now() + timedelta(days=30)
        # Allow 1 minute difference for test timing
        assert abs((expiry - expected).total_seconds()) < 60

    def test_add_suppression_with_tool(self, manager):
        """Test adding suppression with tool restriction."""
        result = manager.add_suppression(
            rule_code="L001",
            reason="Lint-specific",
            scope="project",
            tool="lint",
        )

        assert result is True
        supp = manager.baseline["suppressions"]["project"][0]
        assert supp["tool"] == "lint"

    def test_add_suppression_with_created_by(self, manager):
        """Test adding suppression with created_by field."""
        result = manager.add_suppression(
            rule_code="B001",
            reason="Test",
            scope="project",
            created_by="developer@test.com",
        )

        assert result is True
        supp = manager.baseline["suppressions"]["project"][0]
        assert supp["created_by"] == "developer@test.com"


class TestBaselineManagerFilterFindings:
    """Tests for the filter_findings method."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_filter_findings_no_suppressions(self, manager):
        """Test filtering with no suppressions keeps all findings."""
        findings = [
            {"code": "B001", "file_path": "test.py", "line_number": 1},
            {"code": "B002", "file_path": "test.py", "line_number": 2},
        ]

        result = manager.filter_findings(findings)

        assert len(result) == 2

    def test_filter_findings_removes_suppressed(self, manager):
        """Test that suppressed findings are removed."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Ignore"},
        )

        findings = [
            {"code": "B001", "file_path": "test.py", "line_number": 1},
            {"code": "B002", "file_path": "test.py", "line_number": 2},
        ]

        result = manager.filter_findings(findings)

        assert len(result) == 1
        assert result[0]["code"] == "B002"

    def test_filter_findings_marks_suppressed_in_original(self, manager):
        """Test that original findings are marked as suppressed."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Known issue"},
        )

        findings = [
            {"code": "B001", "file_path": "test.py", "line_number": 1},
        ]

        manager.filter_findings(findings)

        # Original finding should be modified
        assert findings[0]["_suppressed"] is True
        assert findings[0]["_suppression_reason"] == "Known issue"
        assert findings[0]["_suppression_type"] == "baseline_project"

    def test_filter_findings_uses_rule_code_key(self, manager):
        """Test that filter_findings works with rule_code key."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Ignore"},
        )

        findings = [
            {"rule_code": "B001", "file_path": "test.py", "line_number": 1},
        ]

        result = manager.filter_findings(findings)

        assert len(result) == 0

    def test_filter_findings_with_tool(self, manager):
        """Test filtering with tool parameter."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Ignore for security tool", "tool": "security"},
        )

        findings = [
            {"code": "B001", "file_path": "test.py", "line_number": 1},
        ]

        # Should be filtered for security tool
        result1 = manager.filter_findings(findings.copy(), tool="security")
        assert len(result1) == 0

        # Should NOT be filtered for lint tool
        result2 = manager.filter_findings(
            [{"code": "B001", "file_path": "test.py", "line_number": 1}],
            tool="lint",
        )
        assert len(result2) == 1


class TestBaselineManagerStats:
    """Tests for get_suppression_stats method."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_get_suppression_stats_empty(self, manager):
        """Test stats for empty baseline."""
        stats = manager.get_suppression_stats()

        assert stats["total"] == 0
        assert stats["by_scope"]["project"] == 0
        assert stats["by_scope"]["file"] == 0
        assert stats["by_scope"]["rule"] == 0
        assert stats["by_scope"]["inline"] == 0
        assert stats["expired"] == 0
        assert stats["expiring_soon"] == 0

    def test_get_suppression_stats_with_suppressions(self, manager):
        """Test stats with various suppressions."""
        # Add project suppression
        manager.baseline["suppressions"]["project"].append({"rule_code": "B001", "reason": "Test"})

        # Add file suppressions
        manager.baseline["suppressions"]["files"]["test.py"] = [
            {"rule_code": "B002", "reason": "Test"},
            {"rule_code": "B003", "reason": "Test"},
        ]

        # Add rule suppression
        manager.baseline["suppressions"]["rules"]["W001"] = {"reason": "Test"}

        stats = manager.get_suppression_stats()

        assert stats["total"] == 4
        assert stats["by_scope"]["project"] == 1
        assert stats["by_scope"]["file"] == 2
        assert stats["by_scope"]["rule"] == 1

    def test_get_suppression_stats_counts_expired(self, manager):
        """Test that stats count expired suppressions."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Test", "expires_at": past_date},
        )

        stats = manager.get_suppression_stats()

        assert stats["expired"] == 1

    def test_get_suppression_stats_counts_expiring_soon(self, manager):
        """Test that stats count expiring soon suppressions."""
        soon_date = (datetime.now() + timedelta(days=3)).isoformat()
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Test", "expires_at": soon_date},
        )

        stats = manager.get_suppression_stats()

        assert stats["expiring_soon"] == 1


class TestBaselineManagerCleanupExpired:
    """Tests for cleanup_expired method."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_cleanup_expired_removes_expired_project(self, manager):
        """Test cleanup removes expired project suppressions."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Expired", "expires_at": past_date},
        )
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B002", "reason": "Not expired"},
        )

        removed = manager.cleanup_expired()

        assert removed == 1
        assert len(manager.baseline["suppressions"]["project"]) == 1
        assert manager.baseline["suppressions"]["project"][0]["rule_code"] == "B002"

    def test_cleanup_expired_removes_expired_file(self, manager):
        """Test cleanup removes expired file suppressions."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        manager.baseline["suppressions"]["files"]["test.py"] = [
            {"rule_code": "B001", "reason": "Expired", "expires_at": past_date},
            {"rule_code": "B002", "reason": "Not expired"},
        ]

        removed = manager.cleanup_expired()

        assert removed == 1
        assert len(manager.baseline["suppressions"]["files"]["test.py"]) == 1

    def test_cleanup_expired_removes_expired_rules(self, manager):
        """Test cleanup removes expired rule suppressions."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        manager.baseline["suppressions"]["rules"]["B001"] = {
            "reason": "Expired",
            "expires_at": past_date,
        }
        manager.baseline["suppressions"]["rules"]["B002"] = {"reason": "Not expired"}

        removed = manager.cleanup_expired()

        assert removed == 1
        assert "B001" not in manager.baseline["suppressions"]["rules"]
        assert "B002" in manager.baseline["suppressions"]["rules"]

    def test_cleanup_expired_returns_zero_if_none_expired(self, manager):
        """Test cleanup returns 0 when nothing is expired."""
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "No expiry"},
        )

        removed = manager.cleanup_expired()

        assert removed == 0


class TestCreateBaselineFile:
    """Tests for create_baseline_file convenience function."""

    def test_create_baseline_file_basic(self):
        """Test creating a basic baseline file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_baseline_file(tmpdir)

            assert path.exists()
            assert path.name == ".empathy-baseline.json"

            with open(path) as f:
                data = json.load(f)

            assert data["version"] == "1.0"
            assert "created_at" in data
            assert "updated_at" in data
            assert data["suppressions"]["project"] == []
            assert data["suppressions"]["files"] == {}
            assert data["suppressions"]["rules"] == {}

    def test_create_baseline_file_with_metadata(self):
        """Test creating baseline file with description and maintainer."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_baseline_file(
                tmpdir,
                description="My project baseline",
                maintainer="admin@test.com",
            )

            with open(path) as f:
                data = json.load(f)

            assert data["metadata"]["description"] == "My project baseline"
            assert data["metadata"]["maintainer"] == "admin@test.com"

    def test_create_baseline_file_path_object(self):
        """Test creating baseline file with Path object."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_baseline_file(Path(tmpdir))

            assert path.exists()
            assert isinstance(path, Path)


class TestBaselineManagerPrivateMethods:
    """Tests for private helper methods."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        return BaselineManager(temp_project)

    def test_matches_rule_basic(self, manager):
        """Test _matches_rule basic matching."""
        supp_dict = {"rule_code": "B001", "reason": "Test"}

        assert manager._matches_rule(supp_dict, "B001") is True
        assert manager._matches_rule(supp_dict, "B002") is False

    def test_matches_rule_with_tool(self, manager):
        """Test _matches_rule with tool matching."""
        supp_dict = {"rule_code": "B001", "reason": "Test", "tool": "lint"}

        assert manager._matches_rule(supp_dict, "B001", tool="lint") is True
        assert manager._matches_rule(supp_dict, "B001", tool="security") is False

    def test_is_expired_no_expiry(self, manager):
        """Test _is_expired with no expiry date."""
        supp_dict = {"rule_code": "B001", "reason": "Test"}

        assert manager._is_expired(supp_dict, datetime.now()) is False

    def test_is_expired_past(self, manager):
        """Test _is_expired with past date."""
        past_date = (datetime.now() - timedelta(days=30)).isoformat()
        supp_dict = {"rule_code": "B001", "expires_at": past_date}

        assert manager._is_expired(supp_dict, datetime.now()) is True

    def test_is_expired_future(self, manager):
        """Test _is_expired with future date."""
        future_date = (datetime.now() + timedelta(days=30)).isoformat()
        supp_dict = {"rule_code": "B001", "expires_at": future_date}

        assert manager._is_expired(supp_dict, datetime.now()) is False

    def test_is_expired_invalid_date(self, manager):
        """Test _is_expired with invalid date format."""
        supp_dict = {"rule_code": "B001", "expires_at": "invalid-date"}

        assert manager._is_expired(supp_dict, datetime.now()) is False

    def test_expires_within_days(self, manager):
        """Test _expires_within_days method."""
        now = datetime.now()
        soon = (now + timedelta(days=3)).isoformat()
        far = (now + timedelta(days=30)).isoformat()
        past = (now - timedelta(days=3)).isoformat()

        supp_soon = {"expires_at": soon}
        supp_far = {"expires_at": far}
        supp_past = {"expires_at": past}
        supp_never = {}

        assert manager._expires_within_days(supp_soon, now, 7) is True
        assert manager._expires_within_days(supp_far, now, 7) is False
        assert manager._expires_within_days(supp_past, now, 7) is False
        assert manager._expires_within_days(supp_never, now, 7) is False

    def test_dict_to_suppression(self, manager):
        """Test _dict_to_suppression conversion."""
        supp_dict = {
            "rule_code": "B001",
            "reason": "Test reason",
            "created_at": "2025-01-01T00:00:00",
            "created_by": "developer@test.com",
            "expires_at": "2025-06-01T00:00:00",
            "line_number": 42,
            "tool": "security",
        }

        supp = manager._dict_to_suppression(supp_dict, file_path="test.py")

        assert supp.rule_code == "B001"
        assert supp.reason == "Test reason"
        assert supp.source == "baseline"
        assert supp.file_path == "test.py"
        assert supp.line_number == 42
        assert supp.created_at == "2025-01-01T00:00:00"
        assert supp.created_by == "developer@test.com"
        assert supp.expires_at == "2025-06-01T00:00:00"
        assert supp.tool == "security"


class TestBaselineManagerEdgeCases:
    """Edge case tests for BaselineManager."""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def manager(self, temp_project):
        """Create a BaselineManager for testing."""
        manager = BaselineManager(temp_project)
        manager.load()
        return manager

    def test_empty_file_path(self, manager):
        """Test is_suppressed with empty file path."""
        manager.baseline["suppressions"]["project"].append({"rule_code": "B001", "reason": "Test"})

        result = manager.is_suppressed("B001", file_path="", line_number=1)

        # Should still match project-wide suppression
        assert result.is_suppressed is True

    def test_none_line_number(self, manager):
        """Test is_suppressed with None line number."""
        manager.baseline["suppressions"]["files"]["test.py"] = [
            {"rule_code": "B001", "reason": "File-wide"},
        ]

        result = manager.is_suppressed("B001", file_path="test.py", line_number=None)

        assert result.is_suppressed is True

    def test_multiple_inline_suppressions_same_file(self, temp_project, manager):
        """Test multiple inline suppressions in the same file."""
        test_file = temp_project / "test.py"
        test_file.write_text(
            """# empathy:disable-file S001
x = 1  # empathy:disable B001
# empathy:disable-next-line W001
y = 2
z = 3  # empathy:disable B002
""",
        )

        suppressions = manager.scan_file_for_inline("test.py")

        assert len(suppressions) == 4
        rule_codes = [s.rule_code for s in suppressions]
        assert "S001" in rule_codes
        assert "B001" in rule_codes
        assert "W001" in rule_codes
        assert "B002" in rule_codes

    def test_suppression_priority_inline_over_baseline(self, temp_project, manager):
        """Test that inline suppressions take priority over baseline."""
        # Add baseline suppression
        manager.baseline["suppressions"]["project"].append(
            {"rule_code": "B001", "reason": "Baseline reason"},
        )

        # Add file with inline suppression
        test_file = temp_project / "test.py"
        test_file.write_text('x = 1  # empathy:disable B001 reason="inline reason"\n')

        result = manager.is_suppressed("B001", file_path="test.py", line_number=1)

        assert result.is_suppressed is True
        assert result.match_type == "inline_exact"
        assert result.suppression.reason == "inline reason"

    def test_filter_findings_empty_list(self, manager):
        """Test filter_findings with empty list."""
        result = manager.filter_findings([])

        assert result == []

    def test_filter_findings_missing_keys(self, manager):
        """Test filter_findings with findings missing some keys."""
        findings = [
            {"code": "B001"},  # Missing file_path and line_number
        ]

        # Should not raise exception
        result = manager.filter_findings(findings)

        assert len(result) == 1
