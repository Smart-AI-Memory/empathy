"""
Project Scanner - Scans codebase to build file index.

Analyzes source files, matches them to tests, calculates metrics.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

import ast
import fnmatch
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from .models import FileCategory, FileRecord, IndexConfig, ProjectSummary, TestRequirement


class ProjectScanner:
    """
    Scans a project directory and builds file metadata.

    Used by ProjectIndex to populate and update the index.
    """

    def __init__(self, project_root: str, config: IndexConfig | None = None):
        self.project_root = Path(project_root)
        self.config = config or IndexConfig()
        self._test_file_map: dict[str, str] = {}  # source -> test mapping

    def scan(self) -> tuple[list[FileRecord], ProjectSummary]:
        """
        Scan the entire project and return file records and summary.

        Returns:
            Tuple of (list of FileRecords, ProjectSummary)
        """
        records: list[FileRecord] = []

        # First pass: discover all files
        all_files = self._discover_files()

        # Build test file mapping
        self._build_test_mapping(all_files)

        # Second pass: analyze each file
        for file_path in all_files:
            record = self._analyze_file(file_path)
            if record:
                records.append(record)

        # Third pass: build dependency graph
        self._analyze_dependencies(records)

        # Calculate impact scores
        self._calculate_impact_scores(records)

        # Determine attention needs
        self._determine_attention_needs(records)

        # Build summary
        summary = self._build_summary(records)

        return records, summary

    def _discover_files(self) -> list[Path]:
        """Discover all relevant files in the project."""
        files = []

        for root, dirs, filenames in os.walk(self.project_root):
            # Filter out excluded directories
            dirs[:] = [d for d in dirs if not self._is_excluded(Path(root) / d)]

            for filename in filenames:
                file_path = Path(root) / filename
                rel_path = file_path.relative_to(self.project_root)

                if not self._is_excluded(rel_path):
                    files.append(file_path)

        return files

    def _matches_glob_pattern(self, path: Path, pattern: str) -> bool:
        """Check if a path matches a glob pattern (handles ** patterns)."""
        rel_str = str(path)
        path_parts = path.parts

        # Handle ** glob patterns
        if "**" in pattern:
            # Convert ** pattern to work with fnmatch
            # **/ at start means any path prefix
            simple_pattern = pattern.replace("**/", "")

            # Check if the pattern matches the path or any part of it
            if fnmatch.fnmatch(rel_str, simple_pattern):
                return True
            if fnmatch.fnmatch(path.name, simple_pattern):
                return True

            # Check directory-based exclusions
            if pattern.endswith("/**"):
                dir_name = pattern.replace("**/", "").replace("/**", "")
                if dir_name in path_parts:
                    return True

            # Check for directory patterns like **/node_modules/**
            if pattern.startswith("**/") and pattern.endswith("/**"):
                dir_name = pattern[3:-3]  # Extract directory name
                if dir_name in path_parts:
                    return True
        else:
            if fnmatch.fnmatch(rel_str, pattern):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True

        return False

    def _is_excluded(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        for pattern in self.config.exclude_patterns:
            if self._matches_glob_pattern(path, pattern):
                return True
        return False

    def _build_test_mapping(self, files: list[Path]) -> None:
        """Build mapping from source files to their test files."""
        test_files = [f for f in files if self._is_test_file(f)]

        for test_file in test_files:
            # Try to find corresponding source file
            test_name = test_file.stem  # e.g., "test_core"

            # Common patterns: test_foo.py -> foo.py
            if test_name.startswith("test_"):
                source_name = test_name[5:]  # Remove "test_" prefix
            elif test_name.endswith("_test"):
                source_name = test_name[:-5]  # Remove "_test" suffix
            else:
                continue

            # Search for matching source file
            for source_file in files:
                if source_file.stem == source_name and not self._is_test_file(source_file):
                    rel_source = str(source_file.relative_to(self.project_root))
                    rel_test = str(test_file.relative_to(self.project_root))
                    self._test_file_map[rel_source] = rel_test
                    break

    def _is_test_file(self, path: Path) -> bool:
        """Check if a file is a test file."""
        name = path.stem
        return (
            name.startswith("test_")
            or name.endswith("_test")
            or "tests" in path.parts
            or path.parent.name == "test"
        )

    def _analyze_file(self, file_path: Path) -> FileRecord | None:
        """Analyze a single file and create its record."""
        rel_path = str(file_path.relative_to(self.project_root))

        # Determine category
        category = self._determine_category(file_path)

        # Determine language
        language = self._determine_language(file_path)

        # Get file stats
        try:
            stat = file_path.stat()
            last_modified = datetime.fromtimestamp(stat.st_mtime)
        except OSError:
            last_modified = None

        # Determine test requirement
        test_requirement = self._determine_test_requirement(file_path, category)

        # Find associated test file
        test_file_path = self._test_file_map.get(rel_path)
        tests_exist = test_file_path is not None

        # Get test file modification time
        tests_last_modified = None
        if test_file_path:
            test_full_path = self.project_root / test_file_path
            if test_full_path.exists():
                try:
                    tests_last_modified = datetime.fromtimestamp(test_full_path.stat().st_mtime)
                except OSError:
                    pass

        # Calculate staleness
        staleness_days = 0
        is_stale = False
        if last_modified and tests_last_modified:
            if last_modified > tests_last_modified:
                staleness_days = (last_modified - tests_last_modified).days
                is_stale = staleness_days >= self.config.staleness_threshold_days

        # Analyze code metrics
        metrics = self._analyze_code_metrics(file_path, language)

        return FileRecord(
            path=rel_path,
            name=file_path.name,
            category=category,
            language=language,
            test_requirement=test_requirement,
            test_file_path=test_file_path,
            tests_exist=tests_exist,
            test_count=metrics.get("test_count", 0),
            coverage_percent=0.0,  # Will be populated from coverage data
            last_modified=last_modified,
            tests_last_modified=tests_last_modified,
            last_indexed=datetime.now(),
            staleness_days=staleness_days,
            is_stale=is_stale,
            lines_of_code=metrics.get("lines_of_code", 0),
            lines_of_test=metrics.get("lines_of_test", 0),
            complexity_score=metrics.get("complexity", 0.0),
            has_docstrings=metrics.get("has_docstrings", False),
            has_type_hints=metrics.get("has_type_hints", False),
            lint_issues=0,  # Will be populated from linter
            imports=metrics.get("imports", []),
            imported_by=[],  # Populated in dependency analysis
            import_count=len(metrics.get("imports", [])),
            imported_by_count=0,
            impact_score=0.0,  # Calculated later
            metadata={},
            needs_attention=False,
            attention_reasons=[],
        )

    def _determine_category(self, path: Path) -> FileCategory:
        """Determine the category of a file."""
        if self._is_test_file(path):
            return FileCategory.TEST

        suffix = path.suffix.lower()

        # Config files
        if suffix in [".yml", ".yaml", ".toml", ".ini", ".cfg", ".json"]:
            return FileCategory.CONFIG

        # Documentation
        if suffix in [".md", ".rst", ".txt"] or path.name in ["README", "CHANGELOG", "LICENSE"]:
            return FileCategory.DOCS

        # Assets
        if suffix in [".css", ".scss", ".html", ".svg", ".png", ".jpg", ".gif"]:
            return FileCategory.ASSET

        # Source code
        if suffix in [".py", ".js", ".ts", ".tsx", ".jsx", ".go", ".rs", ".java"]:
            return FileCategory.SOURCE

        return FileCategory.UNKNOWN

    def _determine_language(self, path: Path) -> str:
        """Determine the programming language of a file."""
        suffix_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".go": "go",
            ".rs": "rust",
            ".java": "java",
            ".rb": "ruby",
            ".php": "php",
            ".cs": "csharp",
            ".cpp": "cpp",
            ".c": "c",
            ".h": "c",
            ".hpp": "cpp",
        }
        return suffix_map.get(path.suffix.lower(), "")

    def _determine_test_requirement(self, path: Path, category: FileCategory) -> TestRequirement:
        """Determine if a file requires tests."""
        rel_path = path.relative_to(self.project_root)

        # Test files don't need tests
        if category == FileCategory.TEST:
            return TestRequirement.NOT_APPLICABLE

        # Config, docs, assets don't need tests
        if category in [FileCategory.CONFIG, FileCategory.DOCS, FileCategory.ASSET]:
            return TestRequirement.NOT_APPLICABLE

        # Check exclusion patterns using glob matching
        for pattern in self.config.no_test_patterns:
            if self._matches_glob_pattern(rel_path, pattern):
                return TestRequirement.NOT_APPLICABLE

        # __init__.py files usually don't need tests unless they have logic
        if path.name == "__init__.py":
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                # If it's just imports/exports, no tests needed
                if len(content.strip().split("\n")) < 20:
                    return TestRequirement.OPTIONAL
            except OSError:
                pass

        return TestRequirement.REQUIRED

    def _analyze_code_metrics(self, path: Path, language: str) -> dict[str, Any]:
        """Analyze code metrics for a file."""
        metrics: dict[str, Any] = {
            "lines_of_code": 0,
            "lines_of_test": 0,
            "complexity": 0.0,
            "has_docstrings": False,
            "has_type_hints": False,
            "imports": [],
            "test_count": 0,
        }

        if language != "python":
            # For now, just count lines for non-Python
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
                metrics["lines_of_code"] = len(content.split("\n"))
            except OSError:
                pass
            return metrics

        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
            lines = content.split("\n")
            metrics["lines_of_code"] = len(
                [line for line in lines if line.strip() and not line.strip().startswith("#")]
            )

            # Parse AST for Python files
            try:
                tree = ast.parse(content)
                metrics.update(self._analyze_python_ast(tree))
            except SyntaxError:
                pass

        except OSError:
            pass

        return metrics

    def _analyze_python_ast(self, tree: ast.AST) -> dict[str, Any]:
        """Analyze Python AST for metrics."""
        result: dict[str, Any] = {
            "has_docstrings": False,
            "has_type_hints": False,
            "imports": [],
            "test_count": 0,
            "complexity": 0.0,
        }

        for node in ast.walk(tree):
            # Check for docstrings
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.Module)):
                if ast.get_docstring(node):
                    result["has_docstrings"] = True

            # Check for type hints
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.returns or any(arg.annotation for arg in node.args.args):
                    result["has_type_hints"] = True

                # Count test functions
                if node.name.startswith("test_"):
                    result["test_count"] += 1

                # Simple complexity: count branches
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                        result["complexity"] += 1.0

            # Track imports
            if isinstance(node, ast.Import):
                for alias in node.names:
                    result["imports"].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result["imports"].append(node.module)

        return result

    def _analyze_dependencies(self, records: list[FileRecord]) -> None:
        """Build dependency graph between files."""
        # Create lookup by module name
        module_to_path: dict[str, str] = {}
        for record in records:
            if record.language == "python":
                # Convert path to module name
                module_name = record.path.replace("/", ".").replace("\\", ".").rstrip(".py")
                module_to_path[module_name] = record.path

        # Update imported_by relationships
        for record in records:
            for imp in record.imports:
                # Find the imported module
                for module_name, path in module_to_path.items():
                    if module_name.endswith(imp) or imp in module_name:
                        # Find the record for this path
                        for other in records:
                            if other.path == path:
                                if record.path not in other.imported_by:
                                    other.imported_by.append(record.path)
                                    other.imported_by_count = len(other.imported_by)
                                break
                        break

    def _calculate_impact_scores(self, records: list[FileRecord]) -> None:
        """Calculate impact score for each file."""
        for record in records:
            # Impact = imported_by_count * 2 + complexity * 0.5 + lines_of_code * 0.01
            record.impact_score = (
                record.imported_by_count * 2.0
                + record.complexity_score * 0.5
                + record.lines_of_code * 0.01
            )

    def _determine_attention_needs(self, records: list[FileRecord]) -> None:
        """Determine which files need attention."""
        for record in records:
            reasons = []

            # Stale tests
            if record.is_stale:
                reasons.append(f"Tests are {record.staleness_days} days stale")

            # No tests but required
            if record.test_requirement == TestRequirement.REQUIRED and not record.tests_exist:
                reasons.append("Missing tests")

            # Low coverage (if we have coverage data)
            if (
                record.coverage_percent > 0
                and record.coverage_percent < self.config.low_coverage_threshold
            ):
                reasons.append(f"Low coverage ({record.coverage_percent:.1f}%)")

            # High impact but no tests
            if record.impact_score >= self.config.high_impact_threshold:
                if not record.tests_exist and record.test_requirement == TestRequirement.REQUIRED:
                    reasons.append(f"High impact ({record.impact_score:.1f}) without tests")

            record.attention_reasons = reasons
            record.needs_attention = len(reasons) > 0

    def _build_summary(self, records: list[FileRecord]) -> ProjectSummary:
        """Build project summary from records."""
        summary = ProjectSummary()

        summary.total_files = len(records)
        summary.source_files = sum(1 for r in records if r.category == FileCategory.SOURCE)
        summary.test_files = sum(1 for r in records if r.category == FileCategory.TEST)
        summary.config_files = sum(1 for r in records if r.category == FileCategory.CONFIG)
        summary.doc_files = sum(1 for r in records if r.category == FileCategory.DOCS)

        # Testing health
        requiring_tests = [r for r in records if r.test_requirement == TestRequirement.REQUIRED]
        summary.files_requiring_tests = len(requiring_tests)
        summary.files_with_tests = sum(1 for r in requiring_tests if r.tests_exist)
        summary.files_without_tests = summary.files_requiring_tests - summary.files_with_tests
        summary.total_test_count = sum(
            r.test_count for r in records if r.category == FileCategory.TEST
        )

        # Coverage average
        covered = [r for r in records if r.coverage_percent > 0]
        if covered:
            summary.test_coverage_avg = sum(r.coverage_percent for r in covered) / len(covered)

        # Staleness
        stale = [r for r in records if r.is_stale]
        summary.stale_file_count = len(stale)
        if stale:
            summary.avg_staleness_days = sum(r.staleness_days for r in stale) / len(stale)
            summary.most_stale_files = sorted(stale, key=lambda r: -r.staleness_days)[:5]
            summary.most_stale_files = [r.path for r in summary.most_stale_files]

        # Code metrics
        source_records = [r for r in records if r.category == FileCategory.SOURCE]
        summary.total_lines_of_code = sum(r.lines_of_code for r in source_records)
        summary.total_lines_of_test = sum(
            r.lines_of_code for r in records if r.category == FileCategory.TEST
        )
        if summary.total_lines_of_code > 0:
            summary.test_to_code_ratio = summary.total_lines_of_test / summary.total_lines_of_code
        if source_records:
            summary.avg_complexity = sum(r.complexity_score for r in source_records) / len(
                source_records
            )

        # Quality
        if source_records:
            summary.files_with_docstrings_pct = (
                sum(1 for r in source_records if r.has_docstrings) / len(source_records) * 100
            )
            summary.files_with_type_hints_pct = (
                sum(1 for r in source_records if r.has_type_hints) / len(source_records) * 100
            )
        summary.total_lint_issues = sum(r.lint_issues for r in records)

        # High impact files
        high_impact = sorted(records, key=lambda r: -r.impact_score)[:10]
        summary.high_impact_files = [
            r.path for r in high_impact if r.impact_score >= self.config.high_impact_threshold
        ]

        # Critical untested files (high impact + no tests)
        critical = [
            r
            for r in records
            if r.impact_score >= self.config.high_impact_threshold
            and not r.tests_exist
            and r.test_requirement == TestRequirement.REQUIRED
        ]
        summary.critical_untested_files = [
            r.path for r in sorted(critical, key=lambda r: -r.impact_score)[:10]
        ]

        # Attention needed
        needing_attention = [r for r in records if r.needs_attention]
        summary.files_needing_attention = len(needing_attention)
        summary.top_attention_files = [
            r.path for r in sorted(needing_attention, key=lambda r: -r.impact_score)[:10]
        ]

        return summary
