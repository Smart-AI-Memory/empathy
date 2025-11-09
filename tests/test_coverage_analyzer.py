"""
Test Coverage Analyzer

Tests the coverage analysis module for the Enhanced Testing Wizard.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import tempfile
from pathlib import Path

import pytest

from empathy_software_plugin.wizards.testing.coverage_analyzer import (
    CoverageAnalyzer,
    CoverageFormat,
    CoverageReport,
    FileCoverage,
)


class TestCoverageFormat:
    """Test CoverageFormat enum"""

    def test_coverage_format_values(self):
        """Test all coverage format enum values"""
        assert CoverageFormat.XML.value == "xml"
        assert CoverageFormat.JSON.value == "json"
        assert CoverageFormat.HTML.value == "html"
        assert CoverageFormat.LCOV.value == "lcov"


class TestFileCoverage:
    """Test FileCoverage dataclass"""

    def test_file_coverage_creation(self):
        """Test creating a FileCoverage object"""
        file_cov = FileCoverage(
            file_path="src/module.py",
            lines_total=100,
            lines_covered=80,
            lines_missing=[10, 15, 20],
            branches_total=20,
            branches_covered=15,
            branches_missing=[(25, 0), (30, 1)],
            percentage=80.0,
        )

        assert file_cov.file_path == "src/module.py"
        assert file_cov.lines_total == 100
        assert file_cov.lines_covered == 80
        assert file_cov.lines_missing == [10, 15, 20]
        assert file_cov.branches_total == 20
        assert file_cov.branches_covered == 15
        assert file_cov.percentage == 80.0

    def test_lines_uncovered_property(self):
        """Test lines_uncovered property calculation"""
        file_cov = FileCoverage(
            file_path="test.py",
            lines_total=100,
            lines_covered=75,
            lines_missing=[],
            branches_total=0,
            branches_covered=0,
            branches_missing=[],
            percentage=75.0,
        )

        assert file_cov.lines_uncovered == 25

    def test_branch_percentage_property(self):
        """Test branch_percentage property calculation"""
        file_cov = FileCoverage(
            file_path="test.py",
            lines_total=100,
            lines_covered=80,
            lines_missing=[],
            branches_total=20,
            branches_covered=15,
            branches_missing=[],
            percentage=80.0,
        )

        assert file_cov.branch_percentage == 75.0

    def test_branch_percentage_no_branches(self):
        """Test branch_percentage when no branches exist"""
        file_cov = FileCoverage(
            file_path="test.py",
            lines_total=100,
            lines_covered=80,
            lines_missing=[],
            branches_total=0,
            branches_covered=0,
            branches_missing=[],
            percentage=80.0,
        )

        assert file_cov.branch_percentage == 100.0


class TestCoverageReport:
    """Test CoverageReport dataclass"""

    def test_coverage_report_creation(self):
        """Test creating a CoverageReport"""
        files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=100,
                lines_covered=80,
                lines_missing=[],
                branches_total=10,
                branches_covered=8,
                branches_missing=[],
                percentage=80.0,
            )
        }

        report = CoverageReport(
            overall_percentage=80.0,
            lines_total=100,
            lines_covered=80,
            branches_total=10,
            branches_covered=8,
            files=files,
            critical_gaps=["file2.py"],
            untested_files=["file3.py"],
            timestamp="2024-01-20T10:30:00",
        )

        assert report.overall_percentage == 80.0
        assert report.lines_total == 100
        assert report.files_total == 1
        assert len(report.critical_gaps) == 1
        assert len(report.untested_files) == 1

    def test_files_well_covered_property(self):
        """Test files_well_covered property"""
        files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=100,
                lines_covered=85,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=85.0,
            ),
            "file2.py": FileCoverage(
                file_path="file2.py",
                lines_total=100,
                lines_covered=70,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=70.0,
            ),
            "file3.py": FileCoverage(
                file_path="file3.py",
                lines_total=100,
                lines_covered=90,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=90.0,
            ),
        }

        report = CoverageReport(
            overall_percentage=81.67,
            lines_total=300,
            lines_covered=245,
            branches_total=0,
            branches_covered=0,
            files=files,
            critical_gaps=[],
            untested_files=[],
        )

        # Only file1 and file3 have >= 80%
        assert report.files_well_covered == 2


class TestCoverageAnalyzer:
    """Test CoverageAnalyzer functionality"""

    @pytest.fixture
    def analyzer(self):
        """Create a CoverageAnalyzer instance"""
        return CoverageAnalyzer()

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def sample_coverage_xml(self):
        """Create sample coverage.xml content"""
        return """<?xml version="1.0"?>
<coverage version="7.0" timestamp="1705752600" lines-valid="200" lines-covered="160"
          branches-valid="40" branches-covered="32" line-rate="0.8" branch-rate="0.8">
  <packages>
    <package name="mypackage">
      <classes>
        <class name="module1.py" filename="src/module1.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
            <line number="3" hits="0"/>
            <line number="4" hits="1"/>
            <line number="5" hits="0"/>
            <line number="10" hits="1" branch="true" condition-coverage="50% (1/2)"/>
          </lines>
        </class>
        <class name="module2.py" filename="src/module2.py">
          <lines>
            <line number="1" hits="1"/>
            <line number="2" hits="1"/>
          </lines>
        </class>
      </classes>
    </package>
  </packages>
</coverage>"""

    def test_analyzer_initialization(self, analyzer):
        """Test CoverageAnalyzer initialization"""
        assert analyzer.critical_threshold == 50.0
        assert analyzer.target_threshold == 80.0

    def test_parse_coverage_xml_file_not_found(self, analyzer, temp_dir):
        """Test parsing non-existent XML file"""
        with pytest.raises(FileNotFoundError):
            analyzer.parse_coverage_xml(temp_dir / "nonexistent.xml")

    def test_parse_coverage_xml_malformed(self, analyzer, temp_dir):
        """Test parsing malformed XML"""
        xml_file = temp_dir / "coverage.xml"
        xml_file.write_text("<?xml version='1.0'?><broken")

        with pytest.raises(ValueError, match="Malformed coverage XML"):
            analyzer.parse_coverage_xml(xml_file)

    def test_parse_coverage_xml_success(self, analyzer, temp_dir, sample_coverage_xml):
        """Test successfully parsing coverage XML"""
        xml_file = temp_dir / "coverage.xml"
        xml_file.write_text(sample_coverage_xml)

        report = analyzer.parse_coverage_xml(xml_file)

        assert report.overall_percentage == 80.0
        assert report.lines_total == 200
        assert report.lines_covered == 160
        assert report.branches_total == 40
        assert report.branches_covered == 32
        assert len(report.files) == 2

    def test_parse_coverage_xml_file_details(self, analyzer, temp_dir, sample_coverage_xml):
        """Test parsing individual file coverage details"""
        xml_file = temp_dir / "coverage.xml"
        xml_file.write_text(sample_coverage_xml)

        report = analyzer.parse_coverage_xml(xml_file)

        # Check module1.py
        assert "src/module1.py" in report.files
        module1 = report.files["src/module1.py"]
        assert module1.lines_total == 6
        assert module1.lines_covered == 4
        assert 3 in module1.lines_missing
        assert 5 in module1.lines_missing

        # Check module2.py
        assert "src/module2.py" in report.files
        module2 = report.files["src/module2.py"]
        assert module2.lines_total == 2
        assert module2.lines_covered == 2
        assert module2.percentage == 100.0

    def test_parse_coverage_json_file_not_found(self, analyzer, temp_dir):
        """Test parsing non-existent JSON file"""
        with pytest.raises(FileNotFoundError):
            analyzer.parse_coverage_json(temp_dir / "nonexistent.json")

    def test_parse_coverage_json_success(self, analyzer, temp_dir):
        """Test successfully parsing coverage JSON"""
        import json

        coverage_data = {
            "totals": {
                "num_statements": 100,
                "covered_lines": 75,
                "num_branches": 20,
                "covered_branches": 15,
            },
            "files": {
                "src/test.py": {
                    "summary": {
                        "num_statements": 100,
                        "covered_lines": 75,
                        "num_branches": 20,
                        "covered_branches": 15,
                    },
                    "missing_lines": [10, 20, 30],
                    "missing_branches": {"15": [0, 1], "25": [1]},
                }
            },
            "meta": {"timestamp": "2024-01-20T10:30:00"},
        }

        json_file = temp_dir / "coverage.json"
        with open(json_file, "w") as f:
            json.dump(coverage_data, f)

        report = analyzer.parse_coverage_json(json_file)

        assert report.overall_percentage == 75.0
        assert report.lines_total == 100
        assert report.lines_covered == 75
        assert len(report.files) == 1
        assert "src/test.py" in report.files

    def test_identify_critical_gaps(self, analyzer):
        """Test identifying files with critical coverage gaps"""
        files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=100,
                lines_covered=80,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=80.0,
            ),
            "file2.py": FileCoverage(
                file_path="file2.py",
                lines_total=100,
                lines_covered=30,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=30.0,
            ),
            "file3.py": FileCoverage(
                file_path="file3.py",
                lines_total=100,
                lines_covered=10,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=10.0,
            ),
        }

        report = CoverageReport(
            overall_percentage=40.0,
            lines_total=300,
            lines_covered=120,
            branches_total=0,
            branches_covered=0,
            files=files,
            critical_gaps=["file2.py", "file3.py"],
            untested_files=[],
        )

        critical = analyzer.identify_critical_gaps(report)

        # Should return file3.py first (lowest), then file2.py
        assert len(critical) == 2
        assert critical[0] == "file3.py"
        assert critical[1] == "file2.py"

    def test_suggest_priority_files(self, analyzer):
        """Test suggesting priority files for testing"""
        files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=200,  # Large file
                lines_covered=50,  # Low coverage
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=25.0,
            ),
            "file2.py": FileCoverage(
                file_path="file2.py",
                lines_total=50,  # Small file
                lines_covered=45,  # High coverage
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=90.0,
            ),
            "file3.py": FileCoverage(
                file_path="file3.py",
                lines_total=100,  # Medium file
                lines_covered=60,  # Medium coverage
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=60.0,
            ),
        }

        report = CoverageReport(
            overall_percentage=52.86,
            lines_total=350,
            lines_covered=185,
            branches_total=0,
            branches_covered=0,
            files=files,
            critical_gaps=[],
            untested_files=[],
        )

        suggestions = analyzer.suggest_priority_files(report, top_n=5)

        # file2.py should be excluded (already >= 80%)
        # file1.py should have highest priority (large gap, large file)
        assert len(suggestions) == 2
        assert suggestions[0]["file"] == "file1.py"
        assert suggestions[0]["current_coverage"] == 25.0

    def test_suggest_priority_files_reasoning(self, analyzer):
        """Test suggestion reasoning generation"""
        files = {
            "zero.py": FileCoverage(
                file_path="zero.py",
                lines_total=100,
                lines_covered=0,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=0.0,
            ),
            "low.py": FileCoverage(
                file_path="low.py",
                lines_total=100,
                lines_covered=20,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=20.0,
            ),
            "medium.py": FileCoverage(
                file_path="medium.py",
                lines_total=100,
                lines_covered=45,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=45.0,
            ),
            "good.py": FileCoverage(
                file_path="good.py",
                lines_total=100,
                lines_covered=65,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=65.0,
            ),
            "close.py": FileCoverage(
                file_path="close.py",
                lines_total=100,
                lines_covered=75,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=75.0,
            ),
        }

        report = CoverageReport(
            overall_percentage=41.0,
            lines_total=500,
            lines_covered=205,
            branches_total=0,
            branches_covered=0,
            files=files,
            critical_gaps=[],
            untested_files=[],
        )

        suggestions = analyzer.suggest_priority_files(report, top_n=10)

        # Check reasoning for different coverage levels
        zero_suggestion = next(s for s in suggestions if s["file"] == "zero.py")
        assert "No tests exist" in zero_suggestion["reason"]

        low_suggestion = next(s for s in suggestions if s["file"] == "low.py")
        assert "Very low coverage" in low_suggestion["reason"]

        medium_suggestion = next(s for s in suggestions if s["file"] == "medium.py")
        assert "Below critical threshold" in medium_suggestion["reason"]

        good_suggestion = next(s for s in suggestions if s["file"] == "good.py")
        assert "Moderate gap" in good_suggestion["reason"]

        close_suggestion = next(s for s in suggestions if s["file"] == "close.py")
        assert "Close to target" in close_suggestion["reason"]

    def test_calculate_coverage_trend(self, analyzer):
        """Test calculating coverage trends over time"""
        # Create two reports
        old_files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=100,
                lines_covered=60,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=60.0,
            ),
            "file2.py": FileCoverage(
                file_path="file2.py",
                lines_total=100,
                lines_covered=50,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=50.0,
            ),
        }

        new_files = {
            "file1.py": FileCoverage(
                file_path="file1.py",
                lines_total=100,
                lines_covered=80,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=80.0,
            ),
            "file2.py": FileCoverage(
                file_path="file2.py",
                lines_total=100,
                lines_covered=40,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=40.0,
            ),
            "file3.py": FileCoverage(
                file_path="file3.py",
                lines_total=100,
                lines_covered=70,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=70.0,
            ),
        }

        old_report = CoverageReport(
            overall_percentage=55.0,
            lines_total=200,
            lines_covered=110,
            branches_total=0,
            branches_covered=0,
            files=old_files,
            critical_gaps=[],
            untested_files=[],
        )

        new_report = CoverageReport(
            overall_percentage=63.33,
            lines_total=300,
            lines_covered=190,
            branches_total=0,
            branches_covered=0,
            files=new_files,
            critical_gaps=[],
            untested_files=[],
        )

        historical = [("2024-01-01", old_report), ("2024-01-20", new_report)]

        trends = analyzer.calculate_coverage_trend(historical)

        # file1.py improved by 20%
        assert trends["file1.py"] == 20.0
        # file2.py declined by 10%
        assert trends["file2.py"] == -10.0
        # file3.py is new (70%)
        assert trends["file3.py"] == 70.0

    def test_calculate_coverage_trend_insufficient_data(self, analyzer):
        """Test trend calculation with insufficient data"""
        report = CoverageReport(
            overall_percentage=50.0,
            lines_total=100,
            lines_covered=50,
            branches_total=0,
            branches_covered=0,
            files={},
            critical_gaps=[],
            untested_files=[],
        )

        # Only one report
        trends = analyzer.calculate_coverage_trend([("2024-01-01", report)])
        assert trends == {}

    def test_generate_summary(self, analyzer):
        """Test generating human-readable summary"""
        files = {
            "good.py": FileCoverage(
                file_path="good.py",
                lines_total=100,
                lines_covered=85,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=85.0,
            ),
            "bad.py": FileCoverage(
                file_path="bad.py",
                lines_total=100,
                lines_covered=30,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=30.0,
            ),
            "untested.py": FileCoverage(
                file_path="untested.py",
                lines_total=100,
                lines_covered=0,
                lines_missing=[],
                branches_total=0,
                branches_covered=0,
                branches_missing=[],
                percentage=0.0,
            ),
        }

        report = CoverageReport(
            overall_percentage=38.33,
            lines_total=300,
            lines_covered=115,
            branches_total=20,
            branches_covered=15,
            files=files,
            critical_gaps=["bad.py", "untested.py"],
            untested_files=["untested.py"],
        )

        summary = analyzer.generate_summary(report)

        # Check key elements in summary
        assert "COVERAGE ANALYSIS SUMMARY" in summary
        assert "38.33%" in summary
        assert "115/300" in summary
        assert "15/20" in summary
        assert "Files: 3 total" in summary
        assert "Well covered (≥80%): 1" in summary
        assert "Critical gaps (<50%): 2" in summary
        assert "Untested: 1" in summary
        assert "UNTESTED FILES" in summary
        assert "untested.py" in summary
        assert "CRITICAL GAPS" in summary
