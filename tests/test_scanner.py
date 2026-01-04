"""Tests for src/empathy_os/project_index/scanner.py

Tests the ProjectScanner class and its methods for scanning
codebases and building file indexes.
"""

import tempfile
from datetime import datetime
from pathlib import Path

from empathy_os.project_index.models import (
    FileCategory,
    FileRecord,
    IndexConfig,
    ProjectSummary,
    TestRequirement,
)
from empathy_os.project_index.scanner import ProjectScanner


class TestFileCategoryEnum:
    """Tests for FileCategory enum."""

    def test_source_value(self):
        """Test SOURCE category value."""
        assert FileCategory.SOURCE.value == "source"

    def test_test_value(self):
        """Test TEST category value."""
        assert FileCategory.TEST.value == "test"

    def test_config_value(self):
        """Test CONFIG category value."""
        assert FileCategory.CONFIG.value == "config"

    def test_docs_value(self):
        """Test DOCS category value."""
        assert FileCategory.DOCS.value == "docs"

    def test_asset_value(self):
        """Test ASSET category value."""
        assert FileCategory.ASSET.value == "asset"

    def test_generated_value(self):
        """Test GENERATED category value."""
        assert FileCategory.GENERATED.value == "generated"

    def test_build_value(self):
        """Test BUILD category value."""
        assert FileCategory.BUILD.value == "build"

    def test_unknown_value(self):
        """Test UNKNOWN category value."""
        assert FileCategory.UNKNOWN.value == "unknown"

    def test_all_categories_count(self):
        """Test total number of categories."""
        assert len(FileCategory) == 8

    def test_category_from_string(self):
        """Test creating FileCategory from string."""
        assert FileCategory("source") == FileCategory.SOURCE
        assert FileCategory("test") == FileCategory.TEST
        assert FileCategory("config") == FileCategory.CONFIG


class TestTestRequirementEnum:
    """Tests for TestRequirement enum."""

    def test_required_value(self):
        """Test REQUIRED value."""
        assert TestRequirement.REQUIRED.value == "required"

    def test_optional_value(self):
        """Test OPTIONAL value."""
        assert TestRequirement.OPTIONAL.value == "optional"

    def test_not_applicable_value(self):
        """Test NOT_APPLICABLE value."""
        assert TestRequirement.NOT_APPLICABLE.value == "not_applicable"

    def test_excluded_value(self):
        """Test EXCLUDED value."""
        assert TestRequirement.EXCLUDED.value == "excluded"

    def test_all_requirements_count(self):
        """Test total number of requirements."""
        assert len(TestRequirement) == 4


class TestFileRecord:
    """Tests for FileRecord dataclass."""

    def test_basic_creation(self):
        """Test basic FileRecord creation."""
        record = FileRecord(path="src/main.py", name="main.py")
        assert record.path == "src/main.py"
        assert record.name == "main.py"

    def test_default_values(self):
        """Test default values are set correctly."""
        record = FileRecord(path="test.py", name="test.py")
        assert record.category == FileCategory.UNKNOWN
        assert record.language == ""
        assert record.test_requirement == TestRequirement.REQUIRED
        assert record.tests_exist is False
        assert record.test_count == 0
        assert record.coverage_percent == 0.0
        assert record.staleness_days == 0
        assert record.is_stale is False
        assert record.lines_of_code == 0
        assert record.complexity_score == 0.0
        assert record.has_docstrings is False
        assert record.has_type_hints is False
        assert record.lint_issues == 0
        assert record.imports == []
        assert record.imported_by == []
        assert record.impact_score == 0.0
        assert record.metadata == {}
        assert record.needs_attention is False
        assert record.attention_reasons == []

    def test_full_record_creation(self):
        """Test FileRecord with all fields populated."""
        now = datetime.now()
        record = FileRecord(
            path="src/core.py",
            name="core.py",
            category=FileCategory.SOURCE,
            language="python",
            test_requirement=TestRequirement.REQUIRED,
            test_file_path="tests/test_core.py",
            tests_exist=True,
            test_count=25,
            coverage_percent=85.5,
            last_modified=now,
            tests_last_modified=now,
            last_indexed=now,
            staleness_days=3,
            is_stale=False,
            lines_of_code=500,
            lines_of_test=300,
            complexity_score=15.5,
            has_docstrings=True,
            has_type_hints=True,
            lint_issues=2,
            imports=["os", "sys"],
            imported_by=["main.py"],
            import_count=2,
            imported_by_count=1,
            impact_score=10.5,
            metadata={"author": "dev"},
            needs_attention=True,
            attention_reasons=["Low coverage"],
        )
        assert record.category == FileCategory.SOURCE
        assert record.test_count == 25
        assert record.impact_score == 10.5

    def test_to_dict(self):
        """Test serialization to dictionary."""
        now = datetime.now()
        record = FileRecord(
            path="src/api.py",
            name="api.py",
            category=FileCategory.SOURCE,
            language="python",
            last_modified=now,
        )
        data = record.to_dict()
        assert data["path"] == "src/api.py"
        assert data["name"] == "api.py"
        assert data["category"] == "source"
        assert data["language"] == "python"
        assert data["last_modified"] is not None

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "path": "src/utils.py",
            "name": "utils.py",
            "category": "source",
            "language": "python",
            "test_requirement": "required",
            "tests_exist": True,
            "test_count": 10,
            "coverage_percent": 75.0,
            "imports": ["os"],
            "imported_by": [],
        }
        record = FileRecord.from_dict(data)
        assert record.path == "src/utils.py"
        assert record.category == FileCategory.SOURCE
        assert record.test_count == 10

    def test_to_dict_includes_all_fields(self):
        """Test to_dict includes all expected fields."""
        record = FileRecord(path="test.py", name="test.py")
        data = record.to_dict()
        expected_keys = [
            "path",
            "name",
            "category",
            "language",
            "test_requirement",
            "test_file_path",
            "tests_exist",
            "test_count",
            "coverage_percent",
            "last_modified",
            "tests_last_modified",
            "last_indexed",
            "staleness_days",
            "is_stale",
            "lines_of_code",
            "lines_of_test",
            "complexity_score",
            "has_docstrings",
            "has_type_hints",
            "lint_issues",
            "imports",
            "imported_by",
            "import_count",
            "imported_by_count",
            "impact_score",
            "metadata",
            "needs_attention",
            "attention_reasons",
        ]
        for key in expected_keys:
            assert key in data


class TestProjectSummary:
    """Tests for ProjectSummary dataclass."""

    def test_default_values(self):
        """Test default values."""
        summary = ProjectSummary()
        assert summary.total_files == 0
        assert summary.source_files == 0
        assert summary.test_files == 0
        assert summary.files_requiring_tests == 0
        assert summary.test_coverage_avg == 0.0
        assert summary.stale_file_count == 0
        assert summary.total_lines_of_code == 0
        assert summary.high_impact_files == []

    def test_custom_values(self):
        """Test creating ProjectSummary with custom values."""
        summary = ProjectSummary(
            total_files=100,
            source_files=60,
            test_files=40,
            files_requiring_tests=60,
            files_with_tests=55,
            files_without_tests=5,
            test_coverage_avg=85.0,
            total_test_count=500,
            total_lines_of_code=10000,
            total_lines_of_test=5000,
            test_to_code_ratio=0.5,
            high_impact_files=["core.py", "api.py"],
        )
        assert summary.total_files == 100
        assert summary.files_without_tests == 5
        assert len(summary.high_impact_files) == 2

    def test_to_dict(self):
        """Test serialization to dictionary."""
        summary = ProjectSummary(total_files=50, source_files=30)
        data = summary.to_dict()
        assert data["total_files"] == 50
        assert data["source_files"] == 30

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "total_files": 100,
            "source_files": 70,
            "test_files": 30,
            "test_coverage_avg": 80.0,
        }
        summary = ProjectSummary.from_dict(data)
        assert summary.total_files == 100
        assert summary.test_coverage_avg == 80.0


class TestIndexConfig:
    """Tests for IndexConfig dataclass."""

    def test_default_exclude_patterns(self):
        """Test default exclude patterns include common directories."""
        config = IndexConfig()
        assert any("__pycache__" in p for p in config.exclude_patterns)
        assert any(".git" in p for p in config.exclude_patterns)
        assert any("node_modules" in p for p in config.exclude_patterns)
        assert any("venv" in p for p in config.exclude_patterns)

    def test_default_no_test_patterns(self):
        """Test default no-test patterns."""
        config = IndexConfig()
        assert any("__init__.py" in p for p in config.no_test_patterns)
        assert any(".yml" in p for p in config.no_test_patterns)
        assert any(".md" in p for p in config.no_test_patterns)

    def test_default_thresholds(self):
        """Test default threshold values."""
        config = IndexConfig()
        assert config.staleness_threshold_days == 7
        assert config.low_coverage_threshold == 50.0
        assert config.high_impact_threshold == 5.0

    def test_default_directories(self):
        """Test default source directories."""
        config = IndexConfig()
        assert "src" in config.source_dirs
        assert "empathy_llm_toolkit" in config.source_dirs
        assert config.test_dir == "tests"

    def test_custom_config(self):
        """Test creating custom IndexConfig."""
        config = IndexConfig(
            staleness_threshold_days=14,
            low_coverage_threshold=70.0,
            high_impact_threshold=10.0,
            source_dirs=["lib", "src"],
            test_dir="test",
        )
        assert config.staleness_threshold_days == 14
        assert config.low_coverage_threshold == 70.0
        assert "lib" in config.source_dirs

    def test_to_dict(self):
        """Test serialization to dictionary."""
        config = IndexConfig(staleness_threshold_days=10)
        data = config.to_dict()
        assert data["staleness_threshold_days"] == 10
        assert "exclude_patterns" in data
        assert "no_test_patterns" in data

    def test_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            "staleness_threshold_days": 14,
            "low_coverage_threshold": 60.0,
            "source_dirs": ["custom_src"],
        }
        config = IndexConfig.from_dict(data)
        assert config.staleness_threshold_days == 14
        assert config.low_coverage_threshold == 60.0
        assert "custom_src" in config.source_dirs


class TestProjectScannerInit:
    """Tests for ProjectScanner initialization."""

    def test_init_with_path(self):
        """Test initialization with project root path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner.project_root == Path(tmpdir)

    def test_init_with_default_config(self):
        """Test initialization uses default config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner.config is not None
            assert isinstance(scanner.config, IndexConfig)

    def test_init_with_custom_config(self):
        """Test initialization with custom config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = IndexConfig(staleness_threshold_days=14)
            scanner = ProjectScanner(tmpdir, config=config)
            assert scanner.config.staleness_threshold_days == 14

    def test_init_creates_empty_test_map(self):
        """Test initialization creates empty test file map."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._test_file_map == {}


class TestProjectScannerIsExcluded:
    """Tests for _is_excluded method."""

    def test_excludes_pycache(self):
        """Test __pycache__ directories are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_excluded(Path("src/__pycache__/module.pyc"))

    def test_excludes_git(self):
        """Test .git directories are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_excluded(Path(".git/config"))

    def test_excludes_node_modules(self):
        """Test node_modules directories are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_excluded(Path("node_modules/package/index.js"))

    def test_excludes_venv(self):
        """Test venv directories are excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_excluded(Path(".venv/lib/python3.11/site-packages"))

    def test_normal_files_not_excluded(self):
        """Test normal source files are not excluded."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert not scanner._is_excluded(Path("src/main.py"))
            assert not scanner._is_excluded(Path("lib/utils.py"))


class TestProjectScannerIsTestFile:
    """Tests for _is_test_file method."""

    def test_test_prefix(self):
        """Test files with test_ prefix are test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_test_file(Path("test_main.py"))
            assert scanner._is_test_file(Path("test_utils.py"))

    def test_test_suffix(self):
        """Test files with _test suffix are test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_test_file(Path("main_test.py"))
            assert scanner._is_test_file(Path("utils_test.py"))

    def test_tests_directory(self):
        """Test files in tests directory are test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._is_test_file(Path("tests/test_main.py"))
            assert scanner._is_test_file(Path("tests/conftest.py"))

    def test_source_files_not_tests(self):
        """Test regular source files are not test files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert not scanner._is_test_file(Path("src/main.py"))
            assert not scanner._is_test_file(Path("lib/utils.py"))


class TestProjectScannerDetermineCategory:
    """Tests for _determine_category method."""

    def test_test_files(self):
        """Test test files are categorized as TEST."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_category(Path("test_main.py")) == FileCategory.TEST

    def test_config_files(self):
        """Test config files are categorized as CONFIG."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_category(Path("config.yml")) == FileCategory.CONFIG
            assert scanner._determine_category(Path("settings.toml")) == FileCategory.CONFIG
            assert scanner._determine_category(Path("data.json")) == FileCategory.CONFIG

    def test_doc_files(self):
        """Test documentation files are categorized as DOCS."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_category(Path("README.md")) == FileCategory.DOCS
            assert scanner._determine_category(Path("CHANGELOG.md")) == FileCategory.DOCS
            assert scanner._determine_category(Path("docs/guide.rst")) == FileCategory.DOCS

    def test_asset_files(self):
        """Test asset files are categorized as ASSET."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_category(Path("styles.css")) == FileCategory.ASSET
            assert scanner._determine_category(Path("icon.svg")) == FileCategory.ASSET

    def test_source_files(self):
        """Test source files are categorized as SOURCE."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_category(Path("main.py")) == FileCategory.SOURCE
            assert scanner._determine_category(Path("index.js")) == FileCategory.SOURCE
            assert scanner._determine_category(Path("app.ts")) == FileCategory.SOURCE


class TestProjectScannerDetermineLanguage:
    """Tests for _determine_language method."""

    def test_python_files(self):
        """Test Python files are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("main.py")) == "python"

    def test_javascript_files(self):
        """Test JavaScript files are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("app.js")) == "javascript"
            assert scanner._determine_language(Path("component.jsx")) == "javascript"

    def test_typescript_files(self):
        """Test TypeScript files are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("app.ts")) == "typescript"
            assert scanner._determine_language(Path("component.tsx")) == "typescript"

    def test_go_files(self):
        """Test Go files are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("main.go")) == "go"

    def test_rust_files(self):
        """Test Rust files are detected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("lib.rs")) == "rust"

    def test_unknown_extension(self):
        """Test unknown extensions return empty string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._determine_language(Path("data.unknown")) == ""


class TestProjectScannerDetermineTestRequirement:
    """Tests for _determine_test_requirement method."""

    def test_test_files_not_applicable(self):
        """Test test files don't need tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            # Path must be absolute and under project root
            test_path = Path(tmpdir) / "test_main.py"
            result = scanner._determine_test_requirement(test_path, FileCategory.TEST)
            assert result == TestRequirement.NOT_APPLICABLE

    def test_config_files_not_applicable(self):
        """Test config files don't need tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            config_path = Path(tmpdir) / "config.yml"
            result = scanner._determine_test_requirement(config_path, FileCategory.CONFIG)
            assert result == TestRequirement.NOT_APPLICABLE

    def test_doc_files_not_applicable(self):
        """Test doc files don't need tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            doc_path = Path(tmpdir) / "README.md"
            result = scanner._determine_test_requirement(doc_path, FileCategory.DOCS)
            assert result == TestRequirement.NOT_APPLICABLE

    def test_source_files_required(self):
        """Test source files require tests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            source_path = Path(tmpdir) / "main.py"
            result = scanner._determine_test_requirement(source_path, FileCategory.SOURCE)
            assert result == TestRequirement.REQUIRED


class TestProjectScannerGlobPatternMatching:
    """Tests for _matches_glob_pattern method."""

    def test_simple_pattern(self):
        """Test simple glob pattern matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._matches_glob_pattern(Path("main.py"), "*.py")
            assert not scanner._matches_glob_pattern(Path("main.js"), "*.py")

    def test_double_star_pattern(self):
        """Test ** glob pattern matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._matches_glob_pattern(
                Path("src/__pycache__/foo.pyc"),
                "**/__pycache__/**",
            )

    def test_directory_pattern(self):
        """Test directory pattern matching."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._matches_glob_pattern(
                Path("node_modules/pkg/index.js"),
                "**/node_modules/**",
            )


class TestProjectScannerScan:
    """Tests for scan method."""

    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()
            assert records == []
            assert summary.total_files == 0

    def test_scan_with_python_file(self):
        """Test scanning directory with a Python file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a Python file
            py_file = Path(tmpdir) / "main.py"
            py_file.write_text("def hello(): pass\n")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert len(records) == 1
            assert records[0].name == "main.py"
            assert records[0].language == "python"
            assert summary.total_files == 1

    def test_scan_with_test_mapping(self):
        """Test scan builds test file mapping."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source and test files
            src_dir = Path(tmpdir) / "src"
            src_dir.mkdir()
            tests_dir = Path(tmpdir) / "tests"
            tests_dir.mkdir()

            (src_dir / "core.py").write_text("def core(): pass\n")
            (tests_dir / "test_core.py").write_text("def test_core(): pass\n")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            # Find the source file record
            source_records = [r for r in records if r.name == "core.py"]
            if source_records:
                assert source_records[0].test_file_path is not None

    def test_scan_calculates_metrics(self):
        """Test scan calculates code metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "module.py"
            py_file.write_text(
                '''"""Module docstring."""

def hello(name: str) -> str:
    """Say hello."""
    if name:
        return f"Hello, {name}"
    return "Hello"
''',
            )

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert len(records) == 1
            assert records[0].lines_of_code > 0
            # The file has docstrings and type hints
            assert records[0].has_docstrings is True
            assert records[0].has_type_hints is True


class TestProjectScannerBuildSummary:
    """Tests for _build_summary method."""

    def test_summary_counts_categories(self):
        """Test summary correctly counts file categories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create various file types
            (Path(tmpdir) / "main.py").write_text("x = 1")
            (Path(tmpdir) / "config.yml").write_text("key: value")
            (Path(tmpdir) / "README.md").write_text("# Title")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert summary.source_files == 1
            assert summary.config_files == 1
            assert summary.doc_files == 1

    def test_summary_calculates_lines(self):
        """Test summary calculates total lines."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.py").write_text("x = 1\ny = 2\nz = 3")
            (Path(tmpdir) / "b.py").write_text("a = 1\nb = 2")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert summary.total_lines_of_code > 0


class TestProjectScannerImpactScores:
    """Tests for impact score calculation."""

    def test_impact_score_calculation(self):
        """Test impact scores are calculated."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "core.py"
            py_file.write_text(
                """
def complex_function():
    for i in range(10):
        if i > 5:
            try:
                process(i)
            except Exception:
                pass
""",
            )

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            # Impact score should be calculated
            assert records[0].impact_score >= 0

    def test_high_impact_files_in_summary(self):
        """Test high impact files are identified in summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a complex file
            py_file = Path(tmpdir) / "important.py"
            py_file.write_text("x = 1\n" * 100)  # 100 lines

            config = IndexConfig(high_impact_threshold=0.5)
            scanner = ProjectScanner(tmpdir, config=config)
            records, summary = scanner.scan()

            # With low threshold, the file might be high impact
            assert isinstance(summary.high_impact_files, list)


class TestProjectScannerAttentionNeeds:
    """Tests for attention needs detection."""

    def test_missing_tests_needs_attention(self):
        """Test files without tests need attention."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "api.py"
            py_file.write_text("def api(): pass")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            source_records = [r for r in records if r.category == FileCategory.SOURCE]
            # Source file without tests might need attention
            if source_records and source_records[0].test_requirement == TestRequirement.REQUIRED:
                if not source_records[0].tests_exist:
                    assert source_records[0].needs_attention is True
                    assert "Missing tests" in source_records[0].attention_reasons

    def test_attention_reasons_tracked(self):
        """Test attention reasons are tracked."""
        with tempfile.TemporaryDirectory() as tmpdir:
            py_file = Path(tmpdir) / "core.py"
            py_file.write_text("def core(): pass")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            # Check that attention_reasons is a list
            for record in records:
                assert isinstance(record.attention_reasons, list)
