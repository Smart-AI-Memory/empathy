"""
Tests for empathy_software_plugin/wizards/code_review_wizard.py

Tests the CodeReviewWizard including:
- ReviewFinding dataclass
- AntiPatternRule dataclass
- CodeReviewWizard initialization and properties
- Built-in rules
- File and diff review
- Pattern detection
- Recommendations and predictions

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from empathy_software_plugin.wizards.code_review_wizard import (
    AntiPatternRule,
    CodeReviewWizard,
    ReviewFinding,
)


class TestReviewFinding:
    """Tests for ReviewFinding dataclass."""

    def test_basic_creation(self):
        """Test basic creation of ReviewFinding."""
        finding = ReviewFinding(
            file="test.py",
            line=10,
            pattern_type="null_reference",
            pattern_id="bug_001",
            description="Potential null reference",
            historical_cause="Historical bug",
            suggestion="Add null check",
            code_snippet="data.items",
            confidence=0.8,
        )
        assert finding.file == "test.py"
        assert finding.line == 10
        assert finding.pattern_type == "null_reference"
        assert finding.confidence == 0.8

    def test_default_severity_warning(self):
        """Test default severity is warning."""
        finding = ReviewFinding(
            file="test.py",
            line=1,
            pattern_type="test",
            pattern_id="id",
            description="desc",
            historical_cause="cause",
            suggestion="suggestion",
            code_snippet="code",
            confidence=0.5,
        )
        assert finding.severity == "warning"

    def test_to_dict(self):
        """Test to_dict method."""
        finding = ReviewFinding(
            file="test.py",
            line=10,
            pattern_type="null_reference",
            pattern_id="bug_001",
            description="Potential null reference",
            historical_cause="Historical bug",
            suggestion="Add null check",
            code_snippet="data.items",
            confidence=0.8,
            severity="error",
        )
        data = finding.to_dict()
        assert data["file"] == "test.py"
        assert data["line"] == 10
        assert data["pattern_type"] == "null_reference"
        assert data["severity"] == "error"
        assert data["confidence"] == 0.8

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        finding = ReviewFinding(
            file="test.py",
            line=1,
            pattern_type="test",
            pattern_id="id",
            description="desc",
            historical_cause="cause",
            suggestion="suggestion",
            code_snippet="code",
            confidence=0.5,
        )
        data = finding.to_dict()
        expected_keys = [
            "file",
            "line",
            "pattern_type",
            "pattern_id",
            "description",
            "historical_cause",
            "suggestion",
            "code_snippet",
            "confidence",
            "severity",
        ]
        for key in expected_keys:
            assert key in data


class TestAntiPatternRule:
    """Tests for AntiPatternRule dataclass."""

    def test_basic_creation(self):
        """Test basic creation of AntiPatternRule."""
        rule = AntiPatternRule(
            pattern_type="test_pattern",
            description="Test description",
        )
        assert rule.pattern_type == "test_pattern"
        assert rule.description == "Test description"

    def test_default_values(self):
        """Test default values."""
        rule = AntiPatternRule(
            pattern_type="test",
            description="test",
        )
        assert rule.detect_patterns == []
        assert rule.safe_patterns == []
        assert rule.fix_suggestion == ""
        assert rule.reference_bugs == []
        assert rule.severity == "warning"

    def test_with_all_fields(self):
        """Test creation with all fields."""
        rule = AntiPatternRule(
            pattern_type="null_reference",
            description="Potential null reference",
            detect_patterns=[r"\.map\(", r"\.filter\("],
            safe_patterns=[r"\?\.", r"\?\?"],
            fix_suggestion="Add null check",
            reference_bugs=["bug_001", "bug_002"],
            severity="error",
        )
        assert len(rule.detect_patterns) == 2
        assert len(rule.safe_patterns) == 2
        assert len(rule.reference_bugs) == 2
        assert rule.severity == "error"


class TestCodeReviewWizardInit:
    """Tests for CodeReviewWizard initialization."""

    def test_name_property(self):
        """Test name property."""
        wizard = CodeReviewWizard()
        assert wizard.name == "CodeReviewWizard"

    def test_level_property(self):
        """Test level property is 4."""
        wizard = CodeReviewWizard()
        assert wizard.level == 4

    def test_default_patterns_dir(self):
        """Test default patterns_dir."""
        wizard = CodeReviewWizard()
        assert wizard.patterns_dir == Path("./patterns")

    def test_custom_patterns_dir(self):
        """Test custom patterns_dir."""
        wizard = CodeReviewWizard(patterns_dir="/custom/path")
        assert wizard.patterns_dir == Path("/custom/path")

    def test_builtin_rules_loaded(self):
        """Test builtin rules are loaded."""
        wizard = CodeReviewWizard()
        assert "null_reference" in wizard._builtin_rules
        assert "async_timing" in wizard._builtin_rules
        assert "error_handling" in wizard._builtin_rules


class TestBuiltinRules:
    """Tests for builtin rule definitions."""

    def test_null_reference_detect_patterns(self):
        """Test null_reference detect patterns."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["null_reference"]
        assert any(".map" in p for p in rule.detect_patterns)
        assert any(".filter" in p for p in rule.detect_patterns)
        assert any(".length" in p for p in rule.detect_patterns)

    def test_null_reference_safe_patterns(self):
        """Test null_reference safe patterns."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["null_reference"]
        assert any("?" in p for p in rule.safe_patterns)

    def test_async_timing_detect_patterns(self):
        """Test async_timing detect patterns."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["async_timing"]
        assert any("async" in p for p in rule.detect_patterns)
        assert any("Promise" in p for p in rule.detect_patterns)

    def test_error_handling_detect_patterns(self):
        """Test error_handling detect patterns."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["error_handling"]
        assert any("fetch" in p for p in rule.detect_patterns)
        assert any("JSON" in p for p in rule.detect_patterns)


class TestExtractSafePatterns:
    """Tests for _extract_safe_patterns method."""

    def test_extracts_optional_chaining(self):
        """Test extraction of optional chaining pattern."""
        wizard = CodeReviewWizard()
        patterns = wizard._extract_safe_patterns("data?.items")
        # Pattern is escaped as \?\.
        assert len(patterns) > 0
        assert any("\\?\\." in p for p in patterns)

    def test_extracts_nullish_coalescing(self):
        """Test extraction of nullish coalescing pattern."""
        wizard = CodeReviewWizard()
        patterns = wizard._extract_safe_patterns("data ?? []")
        # Pattern is escaped as \?\?
        assert len(patterns) > 0
        assert any("\\?\\?" in p for p in patterns)

    def test_extracts_await_pattern(self):
        """Test extraction of await pattern."""
        wizard = CodeReviewWizard()
        patterns = wizard._extract_safe_patterns("await fetch(url)")
        assert any("await" in p for p in patterns)

    def test_extracts_try_pattern(self):
        """Test extraction of try pattern."""
        wizard = CodeReviewWizard()
        patterns = wizard._extract_safe_patterns("try:\n    do_something()")
        assert any("try" in p for p in patterns)

    def test_empty_fix_code(self):
        """Test empty fix code returns empty list."""
        wizard = CodeReviewWizard()
        patterns = wizard._extract_safe_patterns("")
        assert patterns == []


class TestReviewFile:
    """Tests for _review_file method."""

    def test_file_not_exists_returns_empty(self):
        """Test nonexistent file returns empty list."""
        wizard = CodeReviewWizard()
        findings = wizard._review_file("/nonexistent/path/file.py")
        assert findings == []

    def test_skips_comments(self):
        """Test comments are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("# data.map(x => x)\n")
            wizard = CodeReviewWizard()
            findings = wizard._review_file(str(file_path))
            assert len(findings) == 0

    def test_detects_null_reference_pattern(self):
        """Test detection of null reference pattern."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.js"
            file_path.write_text("const result = data.map(x => x);\n")
            wizard = CodeReviewWizard()
            findings = wizard._review_file(str(file_path))
            null_findings = [f for f in findings if f.pattern_type == "null_reference"]
            assert len(null_findings) > 0

    def test_safe_pattern_prevents_finding(self):
        """Test safe pattern prevents finding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.js"
            file_path.write_text("const result = data?.map(x => x) ?? [];\n")
            wizard = CodeReviewWizard()
            findings = wizard._review_file(str(file_path))
            null_findings = [f for f in findings if f.pattern_type == "null_reference"]
            # Safe pattern should prevent the finding
            assert len(null_findings) == 0


class TestReviewDiff:
    """Tests for _review_diff method."""

    def test_parses_diff_header(self):
        """Test parsing diff header."""
        diff = """diff --git a/src/test.js b/src/test.js
@@ -1,3 +1,4 @@
+const x = data.map(y => y);
"""
        wizard = CodeReviewWizard()
        findings = wizard._review_diff(diff)
        # Should find the file from diff
        assert all(f.file.endswith("test.js") for f in findings) or len(findings) == 0

    def test_only_checks_added_lines(self):
        """Test only added lines are checked."""
        diff = """diff --git a/src/test.js b/src/test.js
@@ -1,3 +1,4 @@
-const old = data.map(x => x);
+const safe = data?.map(x => x);
"""
        wizard = CodeReviewWizard()
        findings = wizard._review_diff(diff)
        # The added line has safe pattern, so no findings
        null_findings = [f for f in findings if f.pattern_type == "null_reference"]
        assert len(null_findings) == 0


class TestCheckLineAgainstRule:
    """Tests for _check_line_against_rule method."""

    def test_returns_none_if_no_detect_match(self):
        """Test returns None if no detect pattern matches."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["null_reference"]
        result = wizard._check_line_against_rule("test.py", 1, "x = 1 + 2", rule, [])
        assert result is None

    def test_returns_none_if_safe_pattern_found(self):
        """Test returns None if safe pattern is found."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["null_reference"]
        lines = ["const x = data?.map(y => y);"]
        result = wizard._check_line_against_rule("test.js", 1, lines[0], rule, lines)
        assert result is None

    def test_creates_finding_on_match(self):
        """Test creates finding when pattern matches without safe pattern."""
        wizard = CodeReviewWizard()
        rule = wizard._builtin_rules["null_reference"]
        lines = ["const x = data.map(y => y);"]
        result = wizard._check_line_against_rule("test.js", 1, lines[0], rule, lines)
        assert result is not None
        assert result.pattern_type == "null_reference"

    def test_confidence_calculation(self):
        """Test confidence calculation."""
        wizard = CodeReviewWizard()
        rule = AntiPatternRule(
            pattern_type="test",
            description="test",
            detect_patterns=[r"test"],
            safe_patterns=[],
            reference_bugs=["bug_001"],  # Should increase confidence
        )
        lines = ["test pattern here"]
        result = wizard._check_line_against_rule("test.py", 1, lines[0], rule, lines)
        assert result is not None
        assert result.confidence >= 0.7


class TestGetStagedFiles:
    """Tests for _get_staged_files method."""

    def test_returns_list_on_success(self):
        """Test returns list on success."""
        wizard = CodeReviewWizard()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="file1.py\nfile2.py\n")
            files = wizard._get_staged_files()
            assert files == ["file1.py", "file2.py"]

    def test_handles_subprocess_error(self):
        """Test handles subprocess error."""
        wizard = CodeReviewWizard()
        with patch("subprocess.run", side_effect=Exception("Error")):
            files = wizard._get_staged_files()
            assert files == []


class TestAnalyze:
    """Tests for async analyze method."""

    @pytest.mark.asyncio
    async def test_analyze_with_files(self):
        """Test analyze with file list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("x = 1\n")
            wizard = CodeReviewWizard()
            result = await wizard.analyze({"files": [str(file_path)]})
            assert "findings" in result
            assert "summary" in result
            assert "predictions" in result
            assert "recommendations" in result

    @pytest.mark.asyncio
    async def test_analyze_with_diff(self):
        """Test analyze with diff input."""
        diff = """diff --git a/test.py b/test.py
@@ -1,1 +1,2 @@
+x = 1
"""
        wizard = CodeReviewWizard()
        result = await wizard.analyze({"diff": diff})
        assert "findings" in result
        assert "summary" in result

    @pytest.mark.asyncio
    async def test_analyze_filters_by_severity(self):
        """Test analyze filters by severity threshold."""
        wizard = CodeReviewWizard()
        result = await wizard.analyze(
            {
                "files": [],
                "severity_threshold": "error",
            }
        )
        # All findings should be error severity or higher
        for finding in result["findings"]:
            assert finding["severity"] in ["error"]

    @pytest.mark.asyncio
    async def test_analyze_returns_expected_structure(self):
        """Test analyze returns expected structure."""
        wizard = CodeReviewWizard()
        result = await wizard.analyze({"files": []})
        assert "findings" in result
        assert "summary" in result
        assert "predictions" in result
        assert "recommendations" in result
        assert "confidence" in result
        assert "metadata" in result


class TestCountingMethods:
    """Tests for counting helper methods."""

    def test_count_by_severity(self):
        """Test _count_by_severity."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=1,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
                severity="warning",
            ),
            ReviewFinding(
                file="b.py",
                line=2,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
                severity="error",
            ),
            ReviewFinding(
                file="c.py",
                line=3,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
                severity="warning",
            ),
        ]
        counts = wizard._count_by_severity(findings)
        assert counts["warning"] == 2
        assert counts["error"] == 1

    def test_count_by_type(self):
        """Test _count_by_type."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=1,
                pattern_type="null_reference",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
            ),
            ReviewFinding(
                file="b.py",
                line=2,
                pattern_type="async_timing",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
            ),
            ReviewFinding(
                file="c.py",
                line=3,
                pattern_type="null_reference",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
            ),
        ]
        counts = wizard._count_by_type(findings)
        assert counts["null_reference"] == 2
        assert counts["async_timing"] == 1

    def test_calculate_confidence_no_findings(self):
        """Test _calculate_confidence with no findings."""
        wizard = CodeReviewWizard()
        confidence = wizard._calculate_confidence([])
        assert confidence == 1.0

    def test_calculate_confidence_with_findings(self):
        """Test _calculate_confidence with findings."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=1,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.8,
            ),
            ReviewFinding(
                file="b.py",
                line=2,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.6,
            ),
        ]
        confidence = wizard._calculate_confidence(findings)
        assert confidence == 0.7  # Average of 0.8 and 0.6


class TestGeneratePredictions:
    """Tests for _generate_predictions method."""

    def test_clean_review_prediction(self):
        """Test clean review prediction when no findings."""
        wizard = CodeReviewWizard()
        predictions = wizard._generate_predictions([])
        assert len(predictions) == 1
        assert predictions[0]["type"] == "clean_review"

    def test_recurring_issue_prediction(self):
        """Test recurring issue prediction."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=i,
                pattern_type="null_reference",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
            )
            for i in range(3)
        ]
        predictions = wizard._generate_predictions(findings)
        recurring = [p for p in predictions if p["type"] == "recurring_issue"]
        assert len(recurring) > 0

    def test_high_risk_prediction(self):
        """Test high risk prediction for error severity."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=1,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
                severity="error",
            ),
        ]
        predictions = wizard._generate_predictions(findings)
        high_risk = [p for p in predictions if p["type"] == "high_risk"]
        assert len(high_risk) > 0


class TestGenerateRecommendations:
    """Tests for _generate_recommendations method."""

    def test_no_issues_recommendation(self):
        """Test recommendation when no findings."""
        wizard = CodeReviewWizard()
        recommendations = wizard._generate_recommendations([])
        assert "No issues found" in recommendations[0]

    def test_groups_by_type(self):
        """Test recommendations group by type."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file="a.py",
                line=1,
                pattern_type="null_reference",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="Add null check",
                code_snippet="c",
                confidence=0.5,
            ),
            ReviewFinding(
                file="b.py",
                line=2,
                pattern_type="null_reference",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="Add null check",
                code_snippet="c",
                confidence=0.5,
            ),
        ]
        recommendations = wizard._generate_recommendations(findings)
        # Should mention count of null_reference issues
        assert any("2" in r and "null_reference" in r for r in recommendations)

    def test_full_test_suite_suggestion(self):
        """Test full test suite suggestion for many findings."""
        wizard = CodeReviewWizard()
        findings = [
            ReviewFinding(
                file=f"file{i}.py",
                line=i,
                pattern_type="t",
                pattern_id="id",
                description="d",
                historical_cause="h",
                suggestion="s",
                code_snippet="c",
                confidence=0.5,
            )
            for i in range(5)
        ]
        recommendations = wizard._generate_recommendations(findings)
        assert any("test suite" in r.lower() for r in recommendations)


class TestFormatTerminalOutput:
    """Tests for format_terminal_output method."""

    def test_no_findings_output(self):
        """Test output when no findings."""
        wizard = CodeReviewWizard()
        result = {"findings": [], "summary": {"total_findings": 0, "files_reviewed": 1}}
        output = wizard.format_terminal_output(result)
        assert "No issues found" in output

    def test_findings_formatted_correctly(self):
        """Test findings are formatted correctly."""
        wizard = CodeReviewWizard()
        result = {
            "findings": [
                {
                    "file": "test.py",
                    "line": 10,
                    "pattern_type": "null_reference",
                    "pattern_id": "bug_001",
                    "description": "Test description",
                    "historical_cause": "Historical cause",
                    "suggestion": "Fix it",
                    "confidence": 0.8,
                    "severity": "warning",
                }
            ],
            "summary": {"total_findings": 1, "files_reviewed": 1},
        }
        output = wizard.format_terminal_output(result)
        assert "test.py:10" in output
        assert "null_reference" in output

    def test_summary_included(self):
        """Test summary is included in output."""
        wizard = CodeReviewWizard()
        result = {
            "findings": [],
            "summary": {"total_findings": 0, "files_reviewed": 5},
        }
        output = wizard.format_terminal_output(result)
        assert "0 findings" in output or "No issues" in output


class TestIntegration:
    """Integration tests for CodeReviewWizard."""

    @pytest.mark.asyncio
    async def test_full_review_workflow(self):
        """Test full review workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create file with potential issue
            file_path = Path(tmpdir) / "test.js"
            file_path.write_text("const result = data.map(x => x);\n")

            wizard = CodeReviewWizard()
            result = await wizard.analyze({"files": [str(file_path)]})

            assert "findings" in result
            assert "summary" in result
            assert "predictions" in result
            assert "recommendations" in result
            assert result["metadata"]["wizard"] == "CodeReviewWizard"
            assert result["metadata"]["level"] == 4

    @pytest.mark.asyncio
    async def test_clean_file_review(self):
        """Test review of clean file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            file_path = Path(tmpdir) / "test.py"
            file_path.write_text("x = 1\ny = 2\nz = x + y\n")

            wizard = CodeReviewWizard()
            result = await wizard.analyze({"files": [str(file_path)]})

            assert len(result["findings"]) == 0
            assert result["confidence"] == 1.0
