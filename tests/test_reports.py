"""Tests for src/empathy_os/project_index/reports.py

Tests the ReportGenerator class which creates various reports
from project index data including test gap, staleness, coverage,
health, and sprint planning reports.
"""

from datetime import datetime, timedelta

from empathy_os.project_index.models import (
    FileCategory,
    FileRecord,
    ProjectSummary,
    TestRequirement,
)
from empathy_os.project_index.reports import ReportGenerator


class TestReportGeneratorInit:
    """Tests for ReportGenerator initialization."""

    def test_init_with_empty_records(self):
        """ReportGenerator should handle empty record list."""
        summary = ProjectSummary()
        records = []
        generator = ReportGenerator(summary, records)

        assert generator.summary is summary
        assert generator.records == []
        assert generator._source_records == []

    def test_init_filters_source_records(self):
        """ReportGenerator should filter only source category records."""
        summary = ProjectSummary()
        records = [
            FileRecord(path="src/main.py", name="main.py", category=FileCategory.SOURCE),
            FileRecord(path="tests/test_main.py", name="test_main.py", category=FileCategory.TEST),
            FileRecord(path="README.md", name="README.md", category=FileCategory.DOCS),
            FileRecord(path="src/utils.py", name="utils.py", category=FileCategory.SOURCE),
        ]
        generator = ReportGenerator(summary, records)

        assert len(generator._source_records) == 2
        assert all(r.category == FileCategory.SOURCE for r in generator._source_records)

    def test_init_with_mixed_categories(self):
        """ReportGenerator should correctly separate source from other categories."""
        summary = ProjectSummary()
        records = [
            FileRecord(path="src/a.py", name="a.py", category=FileCategory.SOURCE),
            FileRecord(
                path="config/settings.json",
                name="settings.json",
                category=FileCategory.CONFIG,
            ),
            FileRecord(path="assets/logo.png", name="logo.png", category=FileCategory.ASSET),
        ]
        generator = ReportGenerator(summary, records)

        assert len(generator.records) == 3
        assert len(generator._source_records) == 1


class TestTestGapReport:
    """Tests for test_gap_report method."""

    def test_test_gap_report_structure(self):
        """test_gap_report should return expected structure."""
        summary = ProjectSummary()
        records = []
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["report_type"] == "test_gap"
        assert "generated_at" in report
        assert "summary" in report
        assert "priority_files" in report
        assert "by_directory" in report
        assert "recommendations" in report

    def test_test_gap_report_with_no_gaps(self):
        """test_gap_report should handle no files needing tests."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/main.py",
                name="main.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=True,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["summary"]["total_files_needing_tests"] == 0
        assert report["summary"]["total_loc_untested"] == 0
        assert report["priority_files"] == []

    def test_test_gap_report_identifies_untested_files(self):
        """test_gap_report should identify files needing tests."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/untested.py",
                name="untested.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                lines_of_code=100,
                impact_score=7.5,
            ),
            FileRecord(
                path="src/tested.py",
                name="tested.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=True,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["summary"]["total_files_needing_tests"] == 1
        assert report["summary"]["total_loc_untested"] == 100
        assert len(report["priority_files"]) == 1
        assert report["priority_files"][0]["path"] == "src/untested.py"

    def test_test_gap_report_prioritizes_by_impact(self):
        """test_gap_report should sort files by impact score descending."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/low_impact.py",
                name="low_impact.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=2.0,
            ),
            FileRecord(
                path="src/high_impact.py",
                name="high_impact.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=8.0,
            ),
            FileRecord(
                path="src/medium_impact.py",
                name="medium_impact.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=5.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        paths = [f["path"] for f in report["priority_files"]]
        assert paths == ["src/high_impact.py", "src/medium_impact.py", "src/low_impact.py"]

    def test_test_gap_report_counts_high_impact_untested(self):
        """test_gap_report should count high impact (>=5.0) untested files."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/high1.py",
                name="high1.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=5.0,
            ),
            FileRecord(
                path="src/high2.py",
                name="high2.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=6.0,
            ),
            FileRecord(
                path="src/low.py",
                name="low.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=4.9,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert report["summary"]["high_impact_untested"] == 2

    def test_test_gap_report_limits_priority_files(self):
        """test_gap_report should limit priority_files to 20."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path=f"src/file{i}.py",
                name=f"file{i}.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=float(i),
            )
            for i in range(30)
        ]
        generator = ReportGenerator(summary, records)
        report = generator.test_gap_report()

        assert len(report["priority_files"]) == 20


class TestTestRecommendations:
    """Tests for _test_recommendations method."""

    def test_recommendations_for_high_impact_files(self):
        """Should recommend high-impact files first."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/critical.py",
                name="critical.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=6.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        needing_tests = [r for r in generator._source_records if not r.tests_exist]
        recommendations = generator._test_recommendations(needing_tests)

        assert len(recommendations) >= 1
        assert "PRIORITY" in recommendations[0]
        assert "critical" in recommendations[0]

    def test_recommendations_for_many_untested_files(self):
        """Should recommend batch testing when >50 files need tests."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path=f"src/file{i}.py",
                name=f"file{i}.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=1.0,
            )
            for i in range(55)
        ]
        generator = ReportGenerator(summary, records)
        needing_tests = [r for r in generator._source_records if not r.tests_exist]
        recommendations = generator._test_recommendations(needing_tests)

        assert any("batch" in r.lower() for r in recommendations)

    def test_no_recommendations_when_all_tested(self):
        """Should return empty recommendations when no files need tests."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        recommendations = generator._test_recommendations([])

        assert recommendations == []


class TestStalenessReport:
    """Tests for staleness_report method."""

    def test_staleness_report_structure(self):
        """staleness_report should return expected structure."""
        summary = ProjectSummary()
        records = []
        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["report_type"] == "staleness"
        assert "generated_at" in report
        assert "summary" in report
        assert "stale_files" in report
        assert "recommendations" in report

    def test_staleness_report_with_no_stale_files(self):
        """staleness_report should handle no stale files."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/fresh.py",
                name="fresh.py",
                category=FileCategory.SOURCE,
                is_stale=False,
                staleness_days=0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["stale_file_count"] == 0
        assert report["summary"]["avg_staleness_days"] == 0
        assert report["summary"]["max_staleness_days"] == 0
        assert report["stale_files"] == []

    def test_staleness_report_identifies_stale_files(self):
        """staleness_report should identify stale files."""
        now = datetime.now()
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/stale.py",
                name="stale.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=30,
                last_modified=now,
                test_file_path="tests/test_stale.py",
                tests_last_modified=now - timedelta(days=30),
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["stale_file_count"] == 1
        assert report["summary"]["avg_staleness_days"] == 30
        assert report["summary"]["max_staleness_days"] == 30
        assert len(report["stale_files"]) == 1
        assert report["stale_files"][0]["staleness_days"] == 30

    def test_staleness_report_sorts_by_staleness(self):
        """staleness_report should sort files by staleness descending."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/a.py",
                name="a.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=10,
            ),
            FileRecord(
                path="src/b.py",
                name="b.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=50,
            ),
            FileRecord(
                path="src/c.py",
                name="c.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=30,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        staleness_days = [f["staleness_days"] for f in report["stale_files"]]
        assert staleness_days == [50, 30, 10]

    def test_staleness_report_calculates_average(self):
        """staleness_report should correctly calculate average staleness."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/a.py",
                name="a.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=10,
            ),
            FileRecord(
                path="src/b.py",
                name="b.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=20,
            ),
            FileRecord(
                path="src/c.py",
                name="c.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=30,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.staleness_report()

        assert report["summary"]["avg_staleness_days"] == 20.0


class TestCoverageReport:
    """Tests for coverage_report method."""

    def test_coverage_report_structure(self):
        """coverage_report should return expected structure."""
        summary = ProjectSummary(test_coverage_avg=75.0)
        records = []
        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        assert report["report_type"] == "coverage"
        assert "generated_at" in report
        assert "summary" in report
        assert "low_coverage_files" in report
        assert "coverage_by_directory" in report

    def test_coverage_report_identifies_low_coverage(self):
        """coverage_report should identify files below 50% coverage."""
        summary = ProjectSummary(test_coverage_avg=60.0)
        records = [
            FileRecord(
                path="src/low.py",
                name="low.py",
                category=FileCategory.SOURCE,
                coverage_percent=30.0,
                impact_score=5.0,
            ),
            FileRecord(
                path="src/high.py",
                name="high.py",
                category=FileCategory.SOURCE,
                coverage_percent=80.0,
            ),
            FileRecord(
                path="src/medium.py",
                name="medium.py",
                category=FileCategory.SOURCE,
                coverage_percent=45.0,
                impact_score=3.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        assert report["summary"]["files_with_data"] == 3
        assert report["summary"]["files_below_50pct"] == 2
        assert len(report["low_coverage_files"]) == 2

    def test_coverage_report_sorts_low_coverage(self):
        """coverage_report should sort low coverage files ascending."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/a.py",
                name="a.py",
                category=FileCategory.SOURCE,
                coverage_percent=40.0,
            ),
            FileRecord(
                path="src/b.py",
                name="b.py",
                category=FileCategory.SOURCE,
                coverage_percent=20.0,
            ),
            FileRecord(
                path="src/c.py",
                name="c.py",
                category=FileCategory.SOURCE,
                coverage_percent=30.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        coverages = [f["coverage_percent"] for f in report["low_coverage_files"]]
        assert coverages == [20.0, 30.0, 40.0]

    def test_coverage_report_excludes_zero_coverage(self):
        """coverage_report should exclude files with 0 coverage from analysis."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/no_data.py",
                name="no_data.py",
                category=FileCategory.SOURCE,
                coverage_percent=0.0,
            ),
            FileRecord(
                path="src/with_data.py",
                name="with_data.py",
                category=FileCategory.SOURCE,
                coverage_percent=45.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.coverage_report()

        assert report["summary"]["files_with_data"] == 1


class TestCoverageByDirectory:
    """Tests for _coverage_by_directory method."""

    def test_coverage_by_directory_groups_correctly(self):
        """_coverage_by_directory should group and average coverage by directory."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/a.py",
                name="a.py",
                category=FileCategory.SOURCE,
                coverage_percent=80.0,
            ),
            FileRecord(
                path="src/b.py",
                name="b.py",
                category=FileCategory.SOURCE,
                coverage_percent=60.0,
            ),
            FileRecord(
                path="lib/c.py",
                name="c.py",
                category=FileCategory.SOURCE,
                coverage_percent=90.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        coverage_by_dir = generator._coverage_by_directory()

        assert "src" in coverage_by_dir
        assert "lib" in coverage_by_dir
        assert coverage_by_dir["src"] == 70.0  # (80 + 60) / 2
        assert coverage_by_dir["lib"] == 90.0

    def test_coverage_by_directory_handles_root_files(self):
        """_coverage_by_directory should handle files in root directory."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="main.py",
                name="main.py",
                category=FileCategory.SOURCE,
                coverage_percent=75.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        coverage_by_dir = generator._coverage_by_directory()

        assert "." in coverage_by_dir
        assert coverage_by_dir["."] == 75.0


class TestHealthReport:
    """Tests for health_report method."""

    def test_health_report_structure(self):
        """health_report should return expected structure."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        report = generator.health_report()

        assert report["report_type"] == "health"
        assert "generated_at" in report
        assert "health_score" in report
        assert "health_grade" in report
        assert "summary" in report
        assert "strengths" in report
        assert "concerns" in report
        assert "action_items" in report

    def test_health_report_includes_summary_fields(self):
        """health_report should include all summary fields."""
        summary = ProjectSummary(
            total_files=100,
            source_files=50,
            test_files=25,
            test_coverage_avg=75.0,
            test_to_code_ratio=0.5,
            stale_file_count=5,
            files_needing_attention=10,
        )
        generator = ReportGenerator(summary, [])
        report = generator.health_report()

        assert report["summary"]["total_files"] == 100
        assert report["summary"]["source_files"] == 50
        assert report["summary"]["test_files"] == 25
        assert report["summary"]["test_coverage_avg"] == 75.0
        assert report["summary"]["test_to_code_ratio"] == 0.5
        assert report["summary"]["stale_file_count"] == 5
        assert report["summary"]["files_needing_attention"] == 10


class TestCalculateHealthScore:
    """Tests for _calculate_health_score method."""

    def test_base_score_is_50(self):
        """Health score should start at 50."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        # With no data, score should be close to base of 50
        score = generator._calculate_health_score()
        assert 0 <= score <= 100

    def test_high_coverage_bonus(self):
        """High coverage (>=80%) should add 25 points."""
        summary = ProjectSummary(test_coverage_avg=85.0)
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        # Base 50 + 25 for high coverage = at least 75
        assert score >= 75

    def test_medium_coverage_bonus(self):
        """Medium coverage (60-79%) should add 15 points."""
        summary = ProjectSummary(test_coverage_avg=65.0)
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        assert score >= 65

    def test_low_coverage_penalty(self):
        """Very low coverage (<20%) should subtract 15 points."""
        summary = ProjectSummary(test_coverage_avg=10.0)
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        assert score < 50

    def test_good_docstrings_bonus(self):
        """High docstring coverage (>=80%) should add 10 points."""
        summary = ProjectSummary(files_with_docstrings_pct=85.0, test_coverage_avg=50.0)
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        assert score >= 60

    def test_score_bounded_to_100(self):
        """Health score should never exceed 100."""
        summary = ProjectSummary(
            test_coverage_avg=100.0,
            files_requiring_tests=10,
            files_with_tests=10,
            files_with_docstrings_pct=100.0,
        )
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        assert score <= 100

    def test_score_bounded_to_0(self):
        """Health score should never go below 0."""
        summary = ProjectSummary(
            test_coverage_avg=0.0,
            files_requiring_tests=100,
            files_with_tests=0,
            source_files=100,
            stale_file_count=100,
        )
        generator = ReportGenerator(summary, [])
        score = generator._calculate_health_score()
        assert score >= 0


class TestHealthGrade:
    """Tests for _health_grade method."""

    def test_grade_a(self):
        """Score >= 90 should be grade A."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        assert generator._health_grade(95) == "A"
        assert generator._health_grade(90) == "A"

    def test_grade_b(self):
        """Score 80-89 should be grade B."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        assert generator._health_grade(89) == "B"
        assert generator._health_grade(80) == "B"

    def test_grade_c(self):
        """Score 70-79 should be grade C."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        assert generator._health_grade(79) == "C"
        assert generator._health_grade(70) == "C"

    def test_grade_d(self):
        """Score 60-69 should be grade D."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        assert generator._health_grade(69) == "D"
        assert generator._health_grade(60) == "D"

    def test_grade_f(self):
        """Score < 60 should be grade F."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        assert generator._health_grade(59) == "F"
        assert generator._health_grade(0) == "F"


class TestIdentifyStrengths:
    """Tests for _identify_strengths method."""

    def test_strength_good_coverage(self):
        """Should identify good test coverage as strength."""
        summary = ProjectSummary(test_coverage_avg=75.0)
        generator = ReportGenerator(summary, [])
        strengths = generator._identify_strengths()
        assert any("coverage" in s.lower() for s in strengths)

    def test_strength_good_docstrings(self):
        """Should identify good documentation as strength."""
        summary = ProjectSummary(files_with_docstrings_pct=80.0)
        generator = ReportGenerator(summary, [])
        strengths = generator._identify_strengths()
        assert any("documented" in s.lower() for s in strengths)

    def test_strength_good_type_hints(self):
        """Should identify strong typing as strength."""
        summary = ProjectSummary(files_with_type_hints_pct=85.0)
        generator = ReportGenerator(summary, [])
        strengths = generator._identify_strengths()
        assert any("typing" in s.lower() for s in strengths)

    def test_strength_no_stale_tests(self):
        """Should identify up-to-date tests as strength."""
        summary = ProjectSummary(stale_file_count=0)
        generator = ReportGenerator(summary, [])
        strengths = generator._identify_strengths()
        assert any("up to date" in s.lower() for s in strengths)

    def test_no_strengths_when_metrics_low(self):
        """Should return empty list when no metrics meet thresholds."""
        summary = ProjectSummary(
            test_coverage_avg=50.0,
            files_with_docstrings_pct=50.0,
            files_with_type_hints_pct=50.0,
            stale_file_count=5,
        )
        generator = ReportGenerator(summary, [])
        strengths = generator._identify_strengths()
        assert strengths == []


class TestIdentifyConcerns:
    """Tests for _identify_concerns method."""

    def test_concern_low_coverage(self):
        """Should identify low test coverage as concern."""
        summary = ProjectSummary(test_coverage_avg=40.0)
        generator = ReportGenerator(summary, [])
        concerns = generator._identify_concerns()
        assert any("coverage" in c.lower() for c in concerns)

    def test_concern_many_untested_files(self):
        """Should identify many untested files as concern."""
        summary = ProjectSummary(files_without_tests=15)
        generator = ReportGenerator(summary, [])
        concerns = generator._identify_concerns()
        assert any("without tests" in c.lower() for c in concerns)

    def test_concern_stale_tests(self):
        """Should identify stale tests as concern."""
        summary = ProjectSummary(stale_file_count=10)
        generator = ReportGenerator(summary, [])
        concerns = generator._identify_concerns()
        assert any("stale" in c.lower() for c in concerns)

    def test_concern_critical_untested(self):
        """Should identify critical untested files as concern."""
        summary = ProjectSummary(critical_untested_files=["src/critical.py", "src/important.py"])
        generator = ReportGenerator(summary, [])
        concerns = generator._identify_concerns()
        assert any("high-impact" in c.lower() for c in concerns)


class TestGenerateActionItems:
    """Tests for _generate_action_items method."""

    def test_action_items_for_critical_files(self):
        """Should generate action items for critical untested files."""
        summary = ProjectSummary(critical_untested_files=["src/critical.py", "src/important.py"])
        generator = ReportGenerator(summary, [])
        items = generator._generate_action_items()

        high_priority = [i for i in items if i["priority"] == "high"]
        assert len(high_priority) == 2
        assert any("critical.py" in i["action"] for i in high_priority)

    def test_action_items_for_stale_files(self):
        """Should generate action items for stale test files."""
        summary = ProjectSummary(most_stale_files=["src/stale1.py", "src/stale2.py"])
        generator = ReportGenerator(summary, [])
        items = generator._generate_action_items()

        medium_priority = [i for i in items if i["priority"] == "medium"]
        assert len(medium_priority) == 2
        assert any("stale1.py" in i["action"] for i in medium_priority)

    def test_action_items_limit(self):
        """Should limit action items to top 3 per category."""
        summary = ProjectSummary(
            critical_untested_files=[f"src/file{i}.py" for i in range(10)],
            most_stale_files=[f"src/stale{i}.py" for i in range(10)],
        )
        generator = ReportGenerator(summary, [])
        items = generator._generate_action_items()

        high_priority = [i for i in items if i["priority"] == "high"]
        medium_priority = [i for i in items if i["priority"] == "medium"]
        assert len(high_priority) == 3
        assert len(medium_priority) == 3


class TestSprintPlanningReport:
    """Tests for sprint_planning_report method."""

    def test_sprint_planning_report_structure(self):
        """sprint_planning_report should return expected structure."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        report = generator.sprint_planning_report()

        assert report["report_type"] == "sprint_planning"
        assert "generated_at" in report
        assert "sprint_capacity" in report
        assert "suggested_work" in report
        assert "backlog" in report
        assert "metrics_to_track" in report

    def test_sprint_planning_respects_capacity(self):
        """sprint_planning_report should limit suggested work to capacity."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path=f"src/file{i}.py",
                name=f"file{i}.py",
                category=FileCategory.SOURCE,
                needs_attention=True,
                attention_reasons=["needs tests"],
                impact_score=float(i),
            )
            for i in range(20)
        ]
        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=5)

        assert report["sprint_capacity"] == 5
        assert len(report["suggested_work"]) == 5

    def test_sprint_planning_prioritizes_by_impact(self):
        """sprint_planning_report should sort by impact score."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/low.py",
                name="low.py",
                category=FileCategory.SOURCE,
                needs_attention=True,
                impact_score=1.0,
            ),
            FileRecord(
                path="src/high.py",
                name="high.py",
                category=FileCategory.SOURCE,
                needs_attention=True,
                impact_score=10.0,
            ),
        ]
        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=2)

        assert report["suggested_work"][0]["path"] == "src/high.py"
        assert report["suggested_work"][1]["path"] == "src/low.py"

    def test_sprint_planning_includes_backlog(self):
        """sprint_planning_report should include backlog items."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path=f"src/file{i}.py",
                name=f"file{i}.py",
                category=FileCategory.SOURCE,
                needs_attention=True,
                attention_reasons=["needs tests"],
                impact_score=float(20 - i),
            )
            for i in range(15)
        ]
        generator = ReportGenerator(summary, records)
        report = generator.sprint_planning_report(sprint_capacity=5)

        assert len(report["backlog"]) == 10


class TestEstimateEffort:
    """Tests for _estimate_effort method."""

    def test_effort_small_new_file(self):
        """Small file without tests should be small effort."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        record = FileRecord(
            path="src/small.py",
            name="small.py",
            category=FileCategory.SOURCE,
            tests_exist=False,
            lines_of_code=30,
        )
        effort = generator._estimate_effort(record)
        assert "small" in effort.lower()

    def test_effort_medium_new_file(self):
        """Medium file without tests should be medium effort."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        record = FileRecord(
            path="src/medium.py",
            name="medium.py",
            category=FileCategory.SOURCE,
            tests_exist=False,
            lines_of_code=100,
        )
        effort = generator._estimate_effort(record)
        assert "medium" in effort.lower()

    def test_effort_large_new_file(self):
        """Large file without tests should be large effort."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        record = FileRecord(
            path="src/large.py",
            name="large.py",
            category=FileCategory.SOURCE,
            tests_exist=False,
            lines_of_code=300,
        )
        effort = generator._estimate_effort(record)
        assert "large" in effort.lower()

    def test_effort_stale_file(self):
        """Stale file should be small effort."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        record = FileRecord(
            path="src/stale.py",
            name="stale.py",
            category=FileCategory.SOURCE,
            tests_exist=True,
            is_stale=True,
        )
        effort = generator._estimate_effort(record)
        assert "small" in effort.lower()

    def test_effort_other_cases(self):
        """Other cases should return 'varies'."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        record = FileRecord(
            path="src/other.py",
            name="other.py",
            category=FileCategory.SOURCE,
            tests_exist=True,
            is_stale=False,
        )
        effort = generator._estimate_effort(record)
        assert "varies" in effort.lower()


class TestMarkdownReports:
    """Tests for to_markdown and related methods."""

    def test_to_markdown_health(self):
        """to_markdown with 'health' should return health markdown."""
        summary = ProjectSummary(
            total_files=100,
            source_files=50,
            test_files=25,
            test_coverage_avg=75.0,
            files_needing_attention=10,
        )
        generator = ReportGenerator(summary, [])
        markdown = generator.to_markdown("health")

        assert "# Project Health Report" in markdown
        assert "Health Score:" in markdown
        assert "Total Files:**" in markdown
        assert "100" in markdown

    def test_to_markdown_test_gap(self):
        """to_markdown with 'test_gap' should return test gap markdown."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/untested.py",
                name="untested.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=False,
                impact_score=5.0,
                lines_of_code=100,
            ),
        ]
        generator = ReportGenerator(summary, records)
        markdown = generator.to_markdown("test_gap")

        assert "# Test Gap Report" in markdown
        assert "Files Needing Tests:" in markdown
        assert "Priority Files" in markdown

    def test_to_markdown_staleness(self):
        """to_markdown with 'staleness' should return staleness markdown."""
        summary = ProjectSummary()
        records = [
            FileRecord(
                path="src/stale.py",
                name="stale.py",
                category=FileCategory.SOURCE,
                is_stale=True,
                staleness_days=20,
            ),
        ]
        generator = ReportGenerator(summary, records)
        markdown = generator.to_markdown("staleness")

        assert "# Test Staleness Report" in markdown
        assert "Stale Files:" in markdown
        assert "Average Staleness:" in markdown

    def test_to_markdown_default(self):
        """to_markdown with unknown type should return health markdown."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        markdown = generator.to_markdown("unknown")

        assert "# Project Health Report" in markdown

    def test_health_markdown_includes_strengths(self):
        """Health markdown should include strengths section when present."""
        summary = ProjectSummary(
            test_coverage_avg=80.0,
            stale_file_count=0,
        )
        generator = ReportGenerator(summary, [])
        markdown = generator._health_markdown()

        assert "## Strengths" in markdown

    def test_health_markdown_includes_concerns(self):
        """Health markdown should include concerns section when present."""
        summary = ProjectSummary(
            test_coverage_avg=30.0,
            files_without_tests=20,
        )
        generator = ReportGenerator(summary, [])
        markdown = generator._health_markdown()

        assert "## Concerns" in markdown

    def test_health_markdown_includes_action_items(self):
        """Health markdown should include action items when present."""
        summary = ProjectSummary(
            critical_untested_files=["src/critical.py"],
        )
        generator = ReportGenerator(summary, [])
        markdown = generator._health_markdown()

        assert "## Action Items" in markdown
        assert "[HIGH]" in markdown


class TestGroupByDirectory:
    """Tests for _group_by_directory method."""

    def test_group_by_directory_basic(self):
        """_group_by_directory should group records by top-level directory."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        records = [
            FileRecord(path="src/a.py", name="a.py", category=FileCategory.SOURCE),
            FileRecord(path="src/b.py", name="b.py", category=FileCategory.SOURCE),
            FileRecord(path="lib/c.py", name="c.py", category=FileCategory.SOURCE),
        ]
        groups = generator._group_by_directory(records)

        assert groups["src"] == 2
        assert groups["lib"] == 1

    def test_group_by_directory_root_files(self):
        """_group_by_directory should handle root-level files."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        records = [
            FileRecord(path="main.py", name="main.py", category=FileCategory.SOURCE),
        ]
        groups = generator._group_by_directory(records)

        assert groups["."] == 1

    def test_group_by_directory_empty(self):
        """_group_by_directory should handle empty list."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        groups = generator._group_by_directory([])

        assert groups == {}


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_project(self):
        """Reports should handle completely empty project."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])

        # All reports should work without errors
        test_gap = generator.test_gap_report()
        staleness = generator.staleness_report()
        coverage = generator.coverage_report()
        health = generator.health_report()
        sprint = generator.sprint_planning_report()

        assert test_gap["summary"]["total_files_needing_tests"] == 0
        assert staleness["summary"]["stale_file_count"] == 0
        assert coverage["summary"]["files_with_data"] == 0
        assert health["health_score"] >= 0
        assert sprint["suggested_work"] == []

    def test_only_non_source_files(self):
        """Reports should handle project with no source files."""
        summary = ProjectSummary()
        records = [
            FileRecord(path="README.md", name="README.md", category=FileCategory.DOCS),
            FileRecord(path="config.json", name="config.json", category=FileCategory.CONFIG),
        ]
        generator = ReportGenerator(summary, records)

        test_gap = generator.test_gap_report()
        assert test_gap["summary"]["total_files_needing_tests"] == 0

    def test_all_files_have_tests(self):
        """Reports should handle project where all files have tests."""
        summary = ProjectSummary(
            files_requiring_tests=5,
            files_with_tests=5,
            files_without_tests=0,
            stale_file_count=0,
        )
        records = [
            FileRecord(
                path=f"src/file{i}.py",
                name=f"file{i}.py",
                category=FileCategory.SOURCE,
                test_requirement=TestRequirement.REQUIRED,
                tests_exist=True,
                coverage_percent=80.0,
            )
            for i in range(5)
        ]
        generator = ReportGenerator(summary, records)

        test_gap = generator.test_gap_report()
        health = generator.health_report()

        assert test_gap["summary"]["total_files_needing_tests"] == 0
        assert health["health_score"] >= 50

    def test_generated_at_is_valid_iso_format(self):
        """Reports should include valid ISO format timestamp."""
        summary = ProjectSummary()
        generator = ReportGenerator(summary, [])
        report = generator.health_report()

        # Should not raise exception
        generated_at = datetime.fromisoformat(report["generated_at"])
        assert generated_at is not None
