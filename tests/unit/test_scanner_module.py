"""Unit tests for project scanner module

Tests ProjectScanner for file discovery, categorization, and pattern matching.
"""

import tempfile
from pathlib import Path

import pytest

from empathy_os.project_index.models import IndexConfig
from empathy_os.project_index.scanner import ProjectScanner


@pytest.mark.unit
class TestProjectScannerInitialization:
    """Test ProjectScanner initialization"""

    def test_scanner_initialization_with_defaults(self):
        """Test creating scanner with default config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner.project_root == Path(tmpdir)
            assert isinstance(scanner.config, IndexConfig)

    def test_scanner_initialization_with_custom_config(self):
        """Test creating scanner with custom config"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = IndexConfig(exclude_patterns=["custom/**"])
            scanner = ProjectScanner(tmpdir, config=config)
            assert scanner.config == config
            assert "custom/**" in scanner.config.exclude_patterns

    def test_scanner_has_empty_test_file_map_initially(self):
        """Test that test file map starts empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            assert scanner._test_file_map == {}


@pytest.mark.unit
class TestGlobPatternMatching:
    """Test glob pattern matching logic"""

    def test_simple_glob_pattern(self):
        """Test simple glob patterns like *.py"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            test_path = Path("src/test.py")
            assert scanner._matches_glob_pattern(test_path, "*.py")
            assert scanner._matches_glob_pattern(test_path, "test.py")
            assert not scanner._matches_glob_pattern(test_path, "*.js")

    def test_doublestar_glob_pattern(self):
        """Test ** glob patterns for recursive matching"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            test_path = Path("src/nested/deep/test.py")

            # ** should match any directory depth
            assert scanner._matches_glob_pattern(test_path, "**/*.py")
            assert scanner._matches_glob_pattern(test_path, "**/test.py")

    def test_directory_exclusion_pattern(self):
        """Test directory exclusion patterns like **/node_modules/**"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            node_modules_path = Path("src/node_modules/package/index.js")

            assert scanner._matches_glob_pattern(node_modules_path, "**/node_modules/**")

    def test_is_excluded(self):
        """Test file exclusion logic"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = IndexConfig(exclude_patterns=["**/node_modules/**", "*.pyc"])
            scanner = ProjectScanner(tmpdir, config=config)

            assert scanner._is_excluded(Path("node_modules/package/index.js"))
            assert scanner._is_excluded(Path("src/__pycache__/module.pyc"))
            assert not scanner._is_excluded(Path("src/main.py"))


@pytest.mark.unit
class TestFileDiscovery:
    """Test file discovery functionality"""

    def test_discover_files_empty_directory(self):
        """Test file discovery in empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()
            assert len(files) == 0

    def test_discover_files_single_file(self):
        """Test file discovery with single file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file
            test_file = Path(tmpdir) / "test.py"
            test_file.write_text("# test")

            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()

            assert len(files) == 1
            assert files[0].name == "test.py"

    def test_discover_files_nested_directories(self):
        """Test file discovery in nested directories"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            (Path(tmpdir) / "src").mkdir()
            (Path(tmpdir) / "src" / "main.py").write_text("# main")
            (Path(tmpdir) / "src" / "util.py").write_text("# util")
            (Path(tmpdir) / "tests").mkdir()
            (Path(tmpdir) / "tests" / "test_main.py").write_text("# test")

            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()

            assert len(files) == 3
            file_names = {f.name for f in files}
            assert file_names == {"main.py", "util.py", "test_main.py"}

    def test_discover_files_respects_exclusions(self):
        """Test that file discovery respects exclusion patterns"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files including ones to exclude
            (Path(tmpdir) / "main.py").write_text("# main")
            (Path(tmpdir) / ".git").mkdir()
            (Path(tmpdir) / ".git" / "config").write_text("# git config")
            (Path(tmpdir) / "__pycache__").mkdir()
            (Path(tmpdir) / "__pycache__" / "cache.pyc").write_text("# cache")

            config = IndexConfig(exclude_patterns=["**/.git/**", "**/__pycache__/**"])
            scanner = ProjectScanner(tmpdir, config=config)
            files = scanner._discover_files()

            # Should only find main.py, not .git or __pycache__ files
            assert len(files) == 1
            assert files[0].name == "main.py"


@pytest.mark.unit
class TestFileTestMapping:
    """Test mapping of source files to test files"""

    def test_build_test_mapping_test_prefix(self):
        """Test mapping for test_*.py pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source and test files
            src_file = Path(tmpdir) / "core.py"
            test_file = Path(tmpdir) / "test_core.py"
            src_file.write_text("# source")
            test_file.write_text("# test")

            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()
            scanner._build_test_mapping(files)

            # Should map core.py -> test_core.py
            assert "core.py" in scanner._test_file_map
            assert scanner._test_file_map["core.py"] == "test_core.py"

    def test_build_test_mapping_test_suffix(self):
        """Test mapping for *_test.py pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source and test files
            src_file = Path(tmpdir) / "utils.py"
            test_file = Path(tmpdir) / "utils_test.py"
            src_file.write_text("# source")
            test_file.write_text("# test")

            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()
            scanner._build_test_mapping(files)

            # Should map utils.py -> utils_test.py
            assert "utils.py" in scanner._test_file_map
            assert scanner._test_file_map["utils.py"] == "utils_test.py"

    def test_build_test_mapping_no_match(self):
        """Test that unmapped source files don't get entries"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source file with no corresponding test
            src_file = Path(tmpdir) / "orphan.py"
            src_file.write_text("# orphan source")

            scanner = ProjectScanner(tmpdir)
            files = scanner._discover_files()
            scanner._build_test_mapping(files)

            # Should not have mapping for orphan.py
            assert "orphan.py" not in scanner._test_file_map


@pytest.mark.unit
class TestProjectSummary:
    """Test project summary generation"""

    def test_scan_generates_summary(self):
        """Test that scan generates a project summary"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple project
            (Path(tmpdir) / "main.py").write_text("def main(): pass")
            (Path(tmpdir) / "test_main.py").write_text("def test_main(): pass")

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert summary is not None
            assert summary.total_files > 0
            assert summary.total_lines_of_code >= 0

    def test_scan_returns_file_records(self):
        """Test that scan returns FileRecord objects"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a simple file
            py_file = Path(tmpdir) / "simple.py"
            py_file.write_text(
                """
def foo():
    return 42

def bar():
    return "hello"
""",
            )

            scanner = ProjectScanner(tmpdir)
            records, summary = scanner.scan()

            assert len(records) > 0
            # Find the simple.py record
            simple_record = next((r for r in records if "simple.py" in r.path), None)
            assert simple_record is not None
            assert simple_record.lines_of_code > 0
