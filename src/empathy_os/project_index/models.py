"""
Project Index Data Models

Defines the structure of file metadata and project summaries.

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class FileCategory(str, Enum):
    """Categories of files in a project."""

    SOURCE = "source"  # Production code
    TEST = "test"  # Test files
    CONFIG = "config"  # Configuration files
    DOCS = "docs"  # Documentation
    ASSET = "asset"  # Static assets
    GENERATED = "generated"  # Auto-generated files
    BUILD = "build"  # Build artifacts
    UNKNOWN = "unknown"


class TestRequirement(str, Enum):
    """Whether a file requires tests."""

    REQUIRED = "required"  # Should have tests
    OPTIONAL = "optional"  # Tests nice to have
    NOT_APPLICABLE = "not_applicable"  # Doesn't need tests
    EXCLUDED = "excluded"  # Explicitly excluded


@dataclass
class FileRecord:
    """
    Metadata record for a single file in the project.

    This is the core data structure that workflows and agents
    can read and write to track file state.
    """

    # Identity
    path: str  # Relative path from project root
    name: str  # File name
    category: FileCategory = FileCategory.UNKNOWN
    language: str = ""  # python, typescript, etc.

    # Testing metadata
    test_requirement: TestRequirement = TestRequirement.REQUIRED
    test_file_path: str | None = None
    tests_exist: bool = False
    test_count: int = 0
    coverage_percent: float = 0.0

    # Timestamps
    last_modified: datetime | None = None
    tests_last_modified: datetime | None = None
    last_indexed: datetime | None = None

    # Staleness (days since source changed but tests didn't)
    staleness_days: int = 0
    is_stale: bool = False

    # Code metrics
    lines_of_code: int = 0
    lines_of_test: int = 0
    complexity_score: float = 0.0

    # Quality indicators
    has_docstrings: bool = False
    has_type_hints: bool = False
    lint_issues: int = 0

    # Dependencies
    imports: list[str] = field(default_factory=list)
    imported_by: list[str] = field(default_factory=list)
    import_count: int = 0
    imported_by_count: int = 0

    # Impact scoring (higher = more critical)
    impact_score: float = 0.0

    # Custom metadata (for workflow-specific data)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Tracking
    needs_attention: bool = False
    attention_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "path": self.path,
            "name": self.name,
            "category": self.category.value,
            "language": self.language,
            "test_requirement": self.test_requirement.value,
            "test_file_path": self.test_file_path,
            "tests_exist": self.tests_exist,
            "test_count": self.test_count,
            "coverage_percent": self.coverage_percent,
            "last_modified": self.last_modified.isoformat() if self.last_modified else None,
            "tests_last_modified": (
                self.tests_last_modified.isoformat() if self.tests_last_modified else None
            ),
            "last_indexed": self.last_indexed.isoformat() if self.last_indexed else None,
            "staleness_days": self.staleness_days,
            "is_stale": self.is_stale,
            "lines_of_code": self.lines_of_code,
            "lines_of_test": self.lines_of_test,
            "complexity_score": self.complexity_score,
            "has_docstrings": self.has_docstrings,
            "has_type_hints": self.has_type_hints,
            "lint_issues": self.lint_issues,
            "imports": self.imports,
            "imported_by": self.imported_by,
            "import_count": self.import_count,
            "imported_by_count": self.imported_by_count,
            "impact_score": self.impact_score,
            "metadata": self.metadata,
            "needs_attention": self.needs_attention,
            "attention_reasons": self.attention_reasons,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FileRecord":
        """Create from dictionary."""
        return cls(
            path=data.get("path", ""),
            name=data.get("name", ""),
            category=FileCategory(data.get("category", "unknown")),
            language=data.get("language", ""),
            test_requirement=TestRequirement(data.get("test_requirement", "required")),
            test_file_path=data.get("test_file_path"),
            tests_exist=data.get("tests_exist", False),
            test_count=data.get("test_count", 0),
            coverage_percent=data.get("coverage_percent", 0.0),
            last_modified=(
                datetime.fromisoformat(data["last_modified"]) if data.get("last_modified") else None
            ),
            tests_last_modified=(
                datetime.fromisoformat(data["tests_last_modified"])
                if data.get("tests_last_modified")
                else None
            ),
            last_indexed=(
                datetime.fromisoformat(data["last_indexed"]) if data.get("last_indexed") else None
            ),
            staleness_days=data.get("staleness_days", 0),
            is_stale=data.get("is_stale", False),
            lines_of_code=data.get("lines_of_code", 0),
            lines_of_test=data.get("lines_of_test", 0),
            complexity_score=data.get("complexity_score", 0.0),
            has_docstrings=data.get("has_docstrings", False),
            has_type_hints=data.get("has_type_hints", False),
            lint_issues=data.get("lint_issues", 0),
            imports=data.get("imports", []),
            imported_by=data.get("imported_by", []),
            import_count=data.get("import_count", 0),
            imported_by_count=data.get("imported_by_count", 0),
            impact_score=data.get("impact_score", 0.0),
            metadata=data.get("metadata", {}),
            needs_attention=data.get("needs_attention", False),
            attention_reasons=data.get("attention_reasons", []),
        )


@dataclass
class ProjectSummary:
    """
    High-level summary of project health.

    Updated each time the index is regenerated.
    """

    # Counts
    total_files: int = 0
    source_files: int = 0
    test_files: int = 0
    config_files: int = 0
    doc_files: int = 0

    # Testing health
    files_requiring_tests: int = 0
    files_with_tests: int = 0
    files_without_tests: int = 0
    test_coverage_avg: float = 0.0
    total_test_count: int = 0

    # Staleness
    stale_file_count: int = 0
    avg_staleness_days: float = 0.0
    most_stale_files: list[str] = field(default_factory=list)

    # Code metrics
    total_lines_of_code: int = 0
    total_lines_of_test: int = 0
    test_to_code_ratio: float = 0.0
    avg_complexity: float = 0.0

    # Quality
    files_with_docstrings_pct: float = 0.0
    files_with_type_hints_pct: float = 0.0
    total_lint_issues: int = 0

    # Impact analysis
    high_impact_files: list[str] = field(default_factory=list)
    critical_untested_files: list[str] = field(default_factory=list)

    # Attention needed
    files_needing_attention: int = 0
    top_attention_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "source_files": self.source_files,
            "test_files": self.test_files,
            "config_files": self.config_files,
            "doc_files": self.doc_files,
            "files_requiring_tests": self.files_requiring_tests,
            "files_with_tests": self.files_with_tests,
            "files_without_tests": self.files_without_tests,
            "test_coverage_avg": self.test_coverage_avg,
            "total_test_count": self.total_test_count,
            "stale_file_count": self.stale_file_count,
            "avg_staleness_days": self.avg_staleness_days,
            "most_stale_files": self.most_stale_files,
            "total_lines_of_code": self.total_lines_of_code,
            "total_lines_of_test": self.total_lines_of_test,
            "test_to_code_ratio": self.test_to_code_ratio,
            "avg_complexity": self.avg_complexity,
            "files_with_docstrings_pct": self.files_with_docstrings_pct,
            "files_with_type_hints_pct": self.files_with_type_hints_pct,
            "total_lint_issues": self.total_lint_issues,
            "high_impact_files": self.high_impact_files,
            "critical_untested_files": self.critical_untested_files,
            "files_needing_attention": self.files_needing_attention,
            "top_attention_files": self.top_attention_files,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ProjectSummary":
        """Create from dictionary."""
        return cls(
            total_files=data.get("total_files", 0),
            source_files=data.get("source_files", 0),
            test_files=data.get("test_files", 0),
            config_files=data.get("config_files", 0),
            doc_files=data.get("doc_files", 0),
            files_requiring_tests=data.get("files_requiring_tests", 0),
            files_with_tests=data.get("files_with_tests", 0),
            files_without_tests=data.get("files_without_tests", 0),
            test_coverage_avg=data.get("test_coverage_avg", 0.0),
            total_test_count=data.get("total_test_count", 0),
            stale_file_count=data.get("stale_file_count", 0),
            avg_staleness_days=data.get("avg_staleness_days", 0.0),
            most_stale_files=data.get("most_stale_files", []),
            total_lines_of_code=data.get("total_lines_of_code", 0),
            total_lines_of_test=data.get("total_lines_of_test", 0),
            test_to_code_ratio=data.get("test_to_code_ratio", 0.0),
            avg_complexity=data.get("avg_complexity", 0.0),
            files_with_docstrings_pct=data.get("files_with_docstrings_pct", 0.0),
            files_with_type_hints_pct=data.get("files_with_type_hints_pct", 0.0),
            total_lint_issues=data.get("total_lint_issues", 0),
            high_impact_files=data.get("high_impact_files", []),
            critical_untested_files=data.get("critical_untested_files", []),
            files_needing_attention=data.get("files_needing_attention", 0),
            top_attention_files=data.get("top_attention_files", []),
        )


@dataclass
class IndexConfig:
    """
    Configuration for the project index.

    Defines exclusion patterns, staleness thresholds, etc.
    """

    # File patterns to exclude from indexing
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            # Python cache and bytecode
            "**/__pycache__/**",
            "**/*.pyc",
            "**/*.pyo",
            # Version control
            "**/.git/**",
            # Virtual environments
            "**/.venv/**",
            "**/venv/**",
            "**/env/**",
            # Package managers
            "**/node_modules/**",
            # Build outputs
            "**/dist/**",
            "**/build/**",
            "**/.next/**",
            "**/site/**",
            "**/*.egg-info/**",
            "**/out/**",
            # Test cache and coverage
            "**/htmlcov/**",
            "**/.pytest_cache/**",
            "**/.mypy_cache/**",
            "**/.ruff_cache/**",
            "**/.coverage*",
            "**/coverage.xml",
            "**/coverage.json",
            "**/.tox/**",
            "**/.nox/**",
            # Generated/binary files
            "**/*.pack",
            "**/dump.rdb",
            # Logs
            "**/logs/**",
            "**/*.log",
            "**/*.jsonl",
            # OS files
            "**/.DS_Store",
            "**/Thumbs.db",
            # IDE/Editor files
            "**/.idea/**",
            "**/.vscode/**",
            "**/*.swp",
            "**/*.swo",
            # External/archived directories (project-specific)
            "**/website/**",
            "**/ebook-site/**",
            "**/anthropic-cookbook/**",
            "**/salvaged/**",
            "**/10_9_2025_ai_nurse_florence/**",
            "**/book-indesign/**",
            "**/examples/**",
            # Binary/asset files
            "**/*.pdf",
            "**/*.jpeg",
            "**/*.jpg",
            "**/*.png",
            "**/*.gif",
            "**/*.ico",
            "**/*.svg",
            "**/*.woff",
            "**/*.woff2",
            "**/*.ttf",
            "**/*.eot",
            "**/*.mp3",
            "**/*.mp4",
            "**/*.wav",
            "**/*.zip",
            "**/*.tar",
            "**/*.gz",
            # Adobe/Design files
            "**/*.indd",
            "**/*.psd",
            "**/*.ai",
            "**/*.sketch",
            "**/*.figma",
            # Lock files
            "**/package-lock.json",
            "**/yarn.lock",
            "**/poetry.lock",
            "**/Pipfile.lock",
            # Archive directories
            "**/archived_wizards/**",
        ]
    )

    # Patterns for files that don't require tests
    no_test_patterns: list[str] = field(
        default_factory=lambda: [
            # Python special files
            "**/__init__.py",
            "**/__main__.py",
            "**/conftest.py",
            "**/setup.py",
            "**/setup.cfg",
            # Configuration files
            "**/*.yml",
            "**/*.yaml",
            "**/*.json",
            "**/*.toml",
            "**/*.ini",
            "**/*.cfg",
            "**/*.conf",
            # Documentation
            "**/*.md",
            "**/*.txt",
            "**/*.rst",
            # Frontend assets
            "**/*.css",
            "**/*.scss",
            "**/*.less",
            "**/*.html",
            "**/*.jinja",
            "**/*.jinja2",
            # Database and migrations
            "**/migrations/**",
            "**/alembic/**",
            # Static and templates
            "**/static/**",
            "**/templates/**",
            "**/fixtures/**",
            # Scripts and utilities (typically standalone)
            "**/scripts/**",
            "**/bin/**",
            "**/tools/**",
            "**/*_script.py",
            "**/*_example.py",
            "**/profile_*.py",
            "**/benchmark_*.py",
            # CLI entry points
            "**/*_cli.py",
            "**/cli.py",
            # Type stubs
            "**/*.pyi",
            # Jupyter notebooks
            "**/*.ipynb",
            # Test files themselves don't need tests
            "**/test_*.py",
            "**/tests/**",
            "**/*_test.py",
            # Example and demo files
            "**/*_example.py",
            "**/*_demo.py",
            "**/example_*.py",
            "**/demo_*.py",
            # Prompt templates
            "**/prompts/**",
            # Vscode extension (separate project)
            "**/vscode-extension/**",
        ]
    )

    # Staleness threshold in days
    staleness_threshold_days: int = 7

    # Coverage threshold for "needs attention"
    low_coverage_threshold: float = 50.0

    # Impact score threshold for "high impact"
    high_impact_threshold: float = 5.0

    # Source directories to scan
    source_dirs: list[str] = field(
        default_factory=lambda: [
            "src",
            "empathy_llm_toolkit",
            "coach_wizards",
            "empathy_software_plugin",
            "empathy_healthcare_plugin",
        ]
    )

    # Test directory
    test_dir: str = "tests"

    # Redis settings
    use_redis: bool = False
    redis_key_prefix: str = "empathy:project_index"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "exclude_patterns": self.exclude_patterns,
            "no_test_patterns": self.no_test_patterns,
            "staleness_threshold_days": self.staleness_threshold_days,
            "low_coverage_threshold": self.low_coverage_threshold,
            "high_impact_threshold": self.high_impact_threshold,
            "source_dirs": self.source_dirs,
            "test_dir": self.test_dir,
            "use_redis": self.use_redis,
            "redis_key_prefix": self.redis_key_prefix,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "IndexConfig":
        """Create from dictionary."""
        config = cls()
        if "exclude_patterns" in data:
            config.exclude_patterns = data["exclude_patterns"]
        if "no_test_patterns" in data:
            config.no_test_patterns = data["no_test_patterns"]
        if "staleness_threshold_days" in data:
            config.staleness_threshold_days = data["staleness_threshold_days"]
        if "low_coverage_threshold" in data:
            config.low_coverage_threshold = data["low_coverage_threshold"]
        if "high_impact_threshold" in data:
            config.high_impact_threshold = data["high_impact_threshold"]
        if "source_dirs" in data:
            config.source_dirs = data["source_dirs"]
        if "test_dir" in data:
            config.test_dir = data["test_dir"]
        if "use_redis" in data:
            config.use_redis = data["use_redis"]
        if "redis_key_prefix" in data:
            config.redis_key_prefix = data["redis_key_prefix"]
        return config
