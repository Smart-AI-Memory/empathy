"""
Documentation Orchestrator - Combined Scout + Writer Workflow

Combines ManageDocumentationCrew (scout/analyst) with DocumentGenerationWorkflow
(writer) to provide an end-to-end documentation management solution:

1. SCOUT Phase: ManageDocumentationCrew scans for stale docs and gaps
2. PRIORITIZE Phase: Filters and ranks items by severity and impact
3. GENERATE Phase: DocumentGenerationWorkflow creates/updates documentation
4. UPDATE Phase: ProjectIndex is updated with new documentation status

This orchestrator provides intelligent documentation maintenance:
- Detects when source code changes make docs stale
- Identifies undocumented files by priority (LOC, complexity)
- Generates documentation using cost-optimized 3-stage pipeline
- Tracks all costs and provides detailed reporting

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import scout workflow
ManageDocumentationCrew = None
ManageDocumentationCrewResult = None
HAS_SCOUT = False

try:
    from .manage_documentation import (
        ManageDocumentationCrew as _ManageDocumentationCrew,
    )
    from .manage_documentation import (
        ManageDocumentationCrewResult as _ManageDocumentationCrewResult,
    )

    ManageDocumentationCrew = _ManageDocumentationCrew
    ManageDocumentationCrewResult = _ManageDocumentationCrewResult
    HAS_SCOUT = True
except ImportError:
    pass

# Import writer workflow
DocumentGenerationWorkflow = None
HAS_WRITER = False

try:
    from .document_gen import DocumentGenerationWorkflow as _DocumentGenerationWorkflow

    DocumentGenerationWorkflow = _DocumentGenerationWorkflow
    HAS_WRITER = True
except ImportError:
    pass

# Import ProjectIndex for tracking
ProjectIndex = None
HAS_PROJECT_INDEX = False

try:
    from empathy_os.project_index import ProjectIndex as _ProjectIndex

    ProjectIndex = _ProjectIndex
    HAS_PROJECT_INDEX = True
except ImportError:
    pass


@dataclass
class DocumentationItem:
    """A single item that needs documentation work."""

    file_path: str
    issue_type: str  # "missing_docstring" | "stale_doc" | "no_documentation"
    severity: str  # "high" | "medium" | "low"
    priority: int  # 1-5, lower is higher priority
    details: str = ""
    related_source: list[str] = field(default_factory=list)
    days_stale: int = 0
    loc: int = 0


@dataclass
class OrchestratorResult:
    """Result from DocumentationOrchestrator execution."""

    success: bool
    phase: str  # "scout" | "prioritize" | "generate" | "complete"

    # Scout phase results
    items_found: int = 0
    stale_docs: int = 0
    missing_docs: int = 0

    # Generation phase results
    items_processed: int = 0
    docs_generated: list[str] = field(default_factory=list)
    docs_updated: list[str] = field(default_factory=list)
    docs_skipped: list[str] = field(default_factory=list)

    # Cost tracking
    scout_cost: float = 0.0
    generation_cost: float = 0.0
    total_cost: float = 0.0

    # Timing
    duration_ms: int = 0

    # Details
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    summary: str = ""

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "phase": self.phase,
            "items_found": self.items_found,
            "stale_docs": self.stale_docs,
            "missing_docs": self.missing_docs,
            "items_processed": self.items_processed,
            "docs_generated": self.docs_generated,
            "docs_updated": self.docs_updated,
            "docs_skipped": self.docs_skipped,
            "scout_cost": self.scout_cost,
            "generation_cost": self.generation_cost,
            "total_cost": self.total_cost,
            "duration_ms": self.duration_ms,
            "errors": self.errors,
            "warnings": self.warnings,
            "summary": self.summary,
        }


class DocumentationOrchestrator:
    """
    End-to-end documentation management orchestrator.

    Combines the ManageDocumentationCrew (scout) with DocumentGenerationWorkflow
    (writer) to provide intelligent, automated documentation maintenance.

    Phases:
    1. SCOUT: Analyze codebase for documentation gaps and staleness
    2. PRIORITIZE: Rank items by severity, LOC, and business impact
    3. GENERATE: Create/update documentation for priority items
    4. UPDATE: Update ProjectIndex with new documentation status

    Usage:
        orchestrator = DocumentationOrchestrator(
            project_root=".",
            max_items=5,           # Process top 5 priority items
            max_cost=2.0,          # Stop at $2 total cost
            auto_approve=False,    # Require approval before generation
        )
        result = await orchestrator.execute()
    """

    name = "documentation-orchestrator"
    description = "End-to-end documentation management: scout gaps, prioritize, generate docs"

    # Patterns to exclude from SCANNING - things we don't want to analyze for documentation gaps
    # Note: The ALLOWED_OUTPUT_EXTENSIONS whitelist is the primary safety mechanism for writes
    DEFAULT_EXCLUDE_PATTERNS = [
        # Generated/build directories (would bloat results)
        "site/**",
        "dist/**",
        "build/**",
        "out/**",
        "node_modules/**",
        "__pycache__/**",
        ".git/**",
        "*.egg-info/**",
        # Framework internal/working directories
        ".empathy/**",
        ".empathy_index/**",
        ".claude/**",
        # Book/large doc source folders
        "book/**",
        "docs/book/**",
        "docs/generated/**",
        "docs/word/**",
        "docs/pdf/**",
        # Dependency/config files (not source code - don't need documentation)
        "requirements*.txt",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "Pipfile",
        "Pipfile.lock",
        "poetry.lock",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "*.toml",
        "*.cfg",
        "*.ini",
        "*.env",
        ".env*",
        "Makefile",
        "Dockerfile",
        "docker-compose*.yml",
        "*.yaml",
        "*.yml",
        # Binary files (cannot be documented as code)
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.gif",
        "*.ico",
        "*.svg",
        "*.pdf",
        "*.woff",
        "*.woff2",
        "*.ttf",
        "*.eot",
        "*.pyc",
        "*.pyo",
        "*.so",
        "*.dll",
        "*.exe",
        "*.zip",
        "*.tar",
        "*.gz",
        "*.vsix",
        "*.docx",
        "*.doc",
    ]

    # ALLOWED file extensions for OUTPUT - documentation can ONLY create/modify these types
    # This is the PRIMARY safety mechanism - even if scanning includes wrong files,
    # only markdown documentation files can ever be written
    ALLOWED_OUTPUT_EXTENSIONS = [
        ".md",  # Markdown documentation
        ".mdx",  # MDX (Markdown with JSX)
        ".rst",  # reStructuredText
    ]

    def __init__(
        self,
        project_root: str = ".",
        max_items: int = 5,
        max_cost: float = 5.0,
        auto_approve: bool = False,
        export_path: str | Path | None = None,
        include_stale: bool = True,
        include_missing: bool = True,
        min_severity: str = "low",  # "high" | "medium" | "low"
        doc_type: str = "api_reference",
        audience: str = "developers",
        dry_run: bool = False,
        exclude_patterns: list[str] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the orchestrator.

        Args:
            project_root: Root directory of the project
            max_items: Maximum number of items to process (default 5)
            max_cost: Maximum total cost in USD (default $5)
            auto_approve: If True, generate docs without confirmation
            export_path: Directory to export generated docs
            include_stale: Include stale docs in processing
            include_missing: Include missing docs in processing
            min_severity: Minimum severity to include ("high", "medium", "low")
            doc_type: Type of documentation to generate
            audience: Target audience for documentation
            dry_run: If True, scout only without generating
            exclude_patterns: Additional patterns to exclude (merged with defaults)
        """
        self.project_root = Path(project_root)
        self.max_items = max_items
        self.max_cost = max_cost
        self.auto_approve = auto_approve

        # Merge default exclusions with any custom patterns
        self.exclude_patterns = list(self.DEFAULT_EXCLUDE_PATTERNS)
        if exclude_patterns:
            self.exclude_patterns.extend(exclude_patterns)
        self.export_path = (
            Path(export_path) if export_path else self.project_root / "docs" / "generated"
        )
        self.include_stale = include_stale
        self.include_missing = include_missing
        self.min_severity = min_severity
        self.doc_type = doc_type
        self.audience = audience
        self.dry_run = dry_run
        self.config = kwargs
        self._quiet = False  # Set to True for JSON output mode

        # Initialize components
        self._scout: Any = None
        self._writer: Any = None
        self._project_index: Any = None

        self._total_cost = 0.0
        self._items: list[DocumentationItem] = []
        self._excluded_files: list[dict] = []  # Track files excluded by patterns

        # Initialize scout if available
        if HAS_SCOUT and ManageDocumentationCrew is not None:
            self._scout = ManageDocumentationCrew(project_root=str(self.project_root))

        # Initialize writer if available
        if HAS_WRITER and DocumentGenerationWorkflow is not None:
            self._writer = DocumentGenerationWorkflow(
                export_path=str(self.export_path),
                max_cost=max_cost / 2,  # Reserve half budget for generation
                graceful_degradation=True,
            )

        # Initialize project index if available
        if HAS_PROJECT_INDEX and ProjectIndex is not None:
            try:
                self._project_index = ProjectIndex(str(self.project_root))
                if not self._project_index.load():
                    self._project_index.refresh()
            except Exception as e:
                logger.warning(f"Could not initialize ProjectIndex: {e}")

    def describe(self) -> str:
        """Get a human-readable description of the workflow."""
        lines = [
            f"Workflow: {self.name}",
            f"Description: {self.description}",
            "",
            "Phases:",
            "  1. SCOUT - Analyze codebase for documentation gaps and staleness",
            "  2. PRIORITIZE - Rank items by severity, LOC, and business impact",
            "  3. GENERATE - Create/update documentation for priority items",
            "  4. UPDATE - Update ProjectIndex with new documentation status",
            "",
            "Configuration:",
            f"  max_items: {self.max_items}",
            f"  max_cost: ${self.max_cost:.2f}",
            f"  auto_approve: {self.auto_approve}",
            f"  dry_run: {self.dry_run}",
            f"  include_stale: {self.include_stale}",
            f"  include_missing: {self.include_missing}",
            "",
            "Components:",
            f"  Scout (ManageDocumentationCrew): {'Available' if self._scout else 'Not available'}",
            f"  Writer (DocumentGenerationWorkflow): {'Available' if self._writer else 'Not available'}",
            f"  ProjectIndex: {'Available' if self._project_index else 'Not available'}",
        ]
        return "\n".join(lines)

    def _severity_to_priority(self, severity: str) -> int:
        """Convert severity string to numeric priority (1=highest)."""
        return {"high": 1, "medium": 2, "low": 3}.get(severity.lower(), 3)

    def _should_include_severity(self, severity: str) -> bool:
        """Check if severity meets minimum threshold."""
        severity_order = {"high": 1, "medium": 2, "low": 3}
        item_level = severity_order.get(severity.lower(), 3)
        min_level = severity_order.get(self.min_severity.lower(), 3)
        return item_level <= min_level

    def _should_exclude(self, file_path: str, track: bool = False) -> bool:
        """
        Check if a file should be excluded from documentation generation.

        Uses fnmatch-style pattern matching against exclude_patterns.

        Args:
            file_path: Path to check (relative or absolute)
            track: If True, add to _excluded_files list when excluded

        Returns:
            True if file should be excluded
        """
        import fnmatch

        # Normalize path for matching
        path_str = str(file_path)
        # Also check just the filename for simple patterns
        filename = Path(file_path).name

        for pattern in self.exclude_patterns:
            # Check full path
            if fnmatch.fnmatch(path_str, pattern):
                if track:
                    self._excluded_files.append(
                        {
                            "file_path": path_str,
                            "matched_pattern": pattern,
                            "reason": self._get_exclusion_reason(pattern),
                        }
                    )
                return True
            # Check just filename
            if fnmatch.fnmatch(filename, pattern):
                if track:
                    self._excluded_files.append(
                        {
                            "file_path": path_str,
                            "matched_pattern": pattern,
                            "reason": self._get_exclusion_reason(pattern),
                        }
                    )
                return True
            # Check if path contains the pattern (for directory patterns)
            if "**" in pattern:
                # Convert ** pattern to a simpler check
                base_pattern = pattern.replace("/**", "").replace("**", "")
                if base_pattern in path_str:
                    if track:
                        self._excluded_files.append(
                            {
                                "file_path": path_str,
                                "matched_pattern": pattern,
                                "reason": self._get_exclusion_reason(pattern),
                            }
                        )
                    return True

        return False

    def _get_exclusion_reason(self, pattern: str) -> str:
        """Get a human-readable reason for why a pattern excludes a file."""
        # Generated directories
        if any(
            p in pattern
            for p in [
                "site/**",
                "dist/**",
                "build/**",
                "out/**",
                "node_modules/**",
                "__pycache__/**",
                ".git/**",
                "egg-info",
            ]
        ):
            return "Generated/build directory"
        # Binary files
        if any(
            p in pattern
            for p in [
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".ico",
                ".svg",
                ".pdf",
                ".woff",
                ".ttf",
                ".pyc",
                ".so",
                ".dll",
                ".exe",
                ".zip",
                ".tar",
                ".gz",
                ".vsix",
            ]
        ):
            return "Binary/asset file"
        # Empathy internal
        if any(p in pattern for p in [".empathy/**", ".claude/**", ".empathy_index/**"]):
            return "Framework internal file"
        # Book/docs
        if any(
            p in pattern
            for p in [
                "book/**",
                "docs/generated/**",
                "docs/word/**",
                "docs/pdf/**",
                ".docx",
                ".doc",
            ]
        ):
            return "Book/document source"
        return "Excluded by pattern"

    def _is_allowed_output(self, file_path: str) -> bool:
        """
        Check if a file is allowed to be created/modified.

        Uses the ALLOWED_OUTPUT_EXTENSIONS whitelist - this is the PRIMARY
        safety mechanism to ensure only documentation files can be written.

        Args:
            file_path: Path to check

        Returns:
            True if the file extension is in the allowed whitelist
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.ALLOWED_OUTPUT_EXTENSIONS

    async def _run_scout_phase(self) -> tuple[list[DocumentationItem], float]:
        """
        Run the scout phase to identify documentation gaps.

        Returns:
            Tuple of (items found, cost)
        """
        items: list[DocumentationItem] = []
        cost = 0.0

        if self._scout is None:
            logger.warning("Scout (ManageDocumentationCrew) not available")
            # Fall back to ProjectIndex if available
            if self._project_index is not None:
                items = self._items_from_index()
            return items, cost

        logger.info("Starting scout phase...")
        print("\n[SCOUT PHASE] Analyzing codebase for documentation gaps...")

        result = await self._scout.execute(path=str(self.project_root))
        cost = result.cost

        if not result.success:
            logger.error("Scout phase failed")
            return items, cost

        # Parse scout findings into DocumentationItems
        items = self._parse_scout_findings(result)

        # Supplement with ProjectIndex data if available
        if self._project_index is not None:
            index_items = self._items_from_index()
            # Merge, preferring scout items but adding unique index items
            existing_paths = {item.file_path for item in items}
            for idx_item in index_items:
                if idx_item.file_path not in existing_paths:
                    items.append(idx_item)

        logger.info(f"Scout phase found {len(items)} items (cost: ${cost:.4f})")
        return items, cost

    def _items_from_index(self) -> list[DocumentationItem]:
        """Extract documentation items from ProjectIndex."""
        items: list[DocumentationItem] = []

        if self._project_index is None:
            return items

        try:
            context = self._project_index.get_context_for_workflow("documentation")

            # Get files without docstrings
            if self.include_missing:
                files_without_docs = context.get("files_without_docstrings", [])
                for f in files_without_docs[:20]:  # Limit
                    file_path = f.get("path", "")
                    if self._should_exclude(file_path, track=True):
                        continue
                    items.append(
                        DocumentationItem(
                            file_path=file_path,
                            issue_type="missing_docstring",
                            severity="medium",
                            priority=2,
                            details=f"Missing docstring - {f.get('loc', 0)} LOC",
                            loc=f.get("loc", 0),
                        )
                    )

            # Get stale docs
            if self.include_stale:
                docs_needing_review = context.get("docs_needing_review", [])
                for d in docs_needing_review[:10]:
                    if d.get("source_modified_after_doc"):
                        file_path = d.get("doc_file", "")
                        if self._should_exclude(file_path, track=True):
                            continue
                        items.append(
                            DocumentationItem(
                                file_path=file_path,
                                issue_type="stale_doc",
                                severity="high",
                                priority=1,
                                details="Source modified after doc update",
                                related_source=d.get("related_source_files", [])[:3],
                                days_stale=d.get("days_since_doc_update", 0),
                            )
                        )
        except Exception as e:
            logger.warning(f"Error extracting items from index: {e}")

        return items

    def _parse_scout_findings(self, result: Any) -> list[DocumentationItem]:
        """Parse scout result into DocumentationItems."""
        items: list[DocumentationItem] = []

        # Scout returns findings as list of dicts with agent responses
        for finding in result.findings:
            response = finding.get("response", "")
            agent = finding.get("agent", "")

            # Try to extract structured data from analyst response
            if "Analyst" in agent:
                # Parse mock or real findings
                # Look for JSON-like structures in the response
                import re

                # Find file paths mentioned
                file_pattern = r'"file_path":\s*"([^"]+)"'
                issue_pattern = r'"issue_type":\s*"([^"]+)"'
                severity_pattern = r'"severity":\s*"([^"]+)"'

                file_matches = re.findall(file_pattern, response)
                issue_matches = re.findall(issue_pattern, response)
                severity_matches = re.findall(severity_pattern, response)

                for i, file_path in enumerate(file_matches):
                    issue_type = issue_matches[i] if i < len(issue_matches) else "unknown"
                    severity = severity_matches[i] if i < len(severity_matches) else "medium"

                    # Filter by settings
                    if issue_type == "stale_doc" and not self.include_stale:
                        continue
                    if (
                        issue_type in ("missing_docstring", "no_documentation")
                        and not self.include_missing
                    ):
                        continue
                    if not self._should_include_severity(severity):
                        continue
                    # Skip excluded files (requirements.txt, package.json, etc.)
                    if self._should_exclude(file_path):
                        continue

                    items.append(
                        DocumentationItem(
                            file_path=file_path,
                            issue_type=issue_type,
                            severity=severity,
                            priority=self._severity_to_priority(severity),
                            details=f"Found by {agent}",
                        )
                    )

        return items

    def _prioritize_items(self, items: list[DocumentationItem]) -> list[DocumentationItem]:
        """
        Prioritize items for generation.

        Priority order:
        1. Stale docs (source changed) - highest urgency
        2. High-severity missing docs
        3. Files with most LOC
        4. Medium/low severity
        """
        # Sort by: priority (asc), days_stale (desc), loc (desc)
        sorted_items = sorted(
            items,
            key=lambda x: (
                x.priority,
                -x.days_stale,
                -x.loc,
            ),
        )

        return sorted_items[: self.max_items]

    async def _run_generate_phase(
        self,
        items: list[DocumentationItem],
    ) -> tuple[list[str], list[str], list[str], float]:
        """
        Run the generation phase for prioritized items.

        Returns:
            Tuple of (generated, updated, skipped, cost)
        """
        generated: list[str] = []
        updated: list[str] = []
        skipped: list[str] = []
        cost = 0.0

        if self._writer is None:
            logger.warning("Writer (DocumentGenerationWorkflow) not available")
            return generated, updated, [item.file_path for item in items], cost

        logger.info(f"Starting generation phase for {len(items)} items...")
        print(f"\n[GENERATE PHASE] Processing {len(items)} documentation items...")

        for i, item in enumerate(items):
            # Check cost limit
            if self._total_cost + cost >= self.max_cost:
                remaining = items[i:]
                skipped.extend([r.file_path for r in remaining])
                logger.warning(f"Cost limit reached. Skipping {len(remaining)} items.")
                print(f"  [!] Cost limit ${self.max_cost:.2f} reached. Skipping remaining items.")
                break

            print(f"  [{i+1}/{len(items)}] {item.issue_type}: {item.file_path}")

            try:
                # Read source file content
                source_path = self.project_root / item.file_path
                source_content = ""

                if source_path.exists():
                    try:
                        source_content = source_path.read_text(encoding="utf-8")
                    except Exception as e:
                        logger.warning(f"Could not read {source_path}: {e}")

                # Run documentation generation
                result = await self._writer.execute(
                    source_code=source_content,
                    target=item.file_path,
                    doc_type=self.doc_type,
                    audience=self.audience,
                )

                # Track cost from result
                if isinstance(result, dict):
                    step_cost = result.get("accumulated_cost", 0.0)
                    cost += step_cost

                    # Categorize result
                    if item.issue_type == "stale_doc":
                        updated.append(item.file_path)
                    else:
                        generated.append(item.file_path)

                    export_path = result.get("export_path")
                    if export_path:
                        print(f"      -> Saved to: {export_path}")
                else:
                    skipped.append(item.file_path)

            except Exception as e:
                logger.error(f"Error generating docs for {item.file_path}: {e}")
                skipped.append(item.file_path)

        logger.info(
            f"Generation phase: {len(generated)} generated, {len(updated)} updated, {len(skipped)} skipped"
        )
        return generated, updated, skipped, cost

    def _update_project_index(self, generated: list[str], updated: list[str]) -> None:
        """Update ProjectIndex with newly documented files."""
        if self._project_index is None:
            return

        try:
            # Mark files as documented
            for file_path in generated + updated:
                # Update record if it exists
                record = self._project_index.get_record(file_path)
                if record:
                    record.has_docstring = True
                    record.last_modified = datetime.now()

            # Save index
            self._project_index.save()
            logger.info(
                f"ProjectIndex updated with {len(generated) + len(updated)} documented files"
            )
        except Exception as e:
            logger.warning(f"Could not update ProjectIndex: {e}")

    def _generate_summary(
        self,
        result: OrchestratorResult,
        items: list[DocumentationItem],
    ) -> str:
        """Generate human-readable summary."""
        lines = [
            "=" * 60,
            "DOCUMENTATION ORCHESTRATOR REPORT",
            "=" * 60,
            "",
            f"Project: {self.project_root}",
            f"Status: {'SUCCESS' if result.success else 'PARTIAL'}",
            "",
            "-" * 60,
            "SCOUT PHASE",
            "-" * 60,
            f"  Items found: {result.items_found}",
            f"  Stale docs: {result.stale_docs}",
            f"  Missing docs: {result.missing_docs}",
            f"  Cost: ${result.scout_cost:.4f}",
            "",
        ]

        if items:
            lines.extend(
                [
                    "Priority Items:",
                ]
            )
            for i, item in enumerate(items[:10]):
                lines.append(f"  {i+1}. [{item.severity.upper()}] {item.file_path}")
                lines.append(f"     Type: {item.issue_type}")
                if item.days_stale:
                    lines.append(f"     Days stale: {item.days_stale}")
            lines.append("")

        if not self.dry_run:
            lines.extend(
                [
                    "-" * 60,
                    "GENERATION PHASE",
                    "-" * 60,
                    f"  Items processed: {result.items_processed}",
                    f"  Docs generated: {len(result.docs_generated)}",
                    f"  Docs updated: {len(result.docs_updated)}",
                    f"  Skipped: {len(result.docs_skipped)}",
                    f"  Cost: ${result.generation_cost:.4f}",
                    "",
                ]
            )

            if result.docs_generated:
                lines.append("Generated:")
                for doc in result.docs_generated[:5]:
                    lines.append(f"  + {doc}")
                if len(result.docs_generated) > 5:
                    lines.append(f"  ... and {len(result.docs_generated) - 5} more")
                lines.append("")

            if result.docs_updated:
                lines.append("Updated:")
                for doc in result.docs_updated[:5]:
                    lines.append(f"  ~ {doc}")
                lines.append("")

        if result.errors:
            lines.extend(
                [
                    "-" * 60,
                    "ERRORS",
                    "-" * 60,
                ]
            )
            for error in result.errors:
                lines.append(f"  ! {error}")
            lines.append("")

        if result.warnings:
            lines.extend(
                [
                    "-" * 60,
                    "WARNINGS",
                    "-" * 60,
                ]
            )
            for warning in result.warnings:
                lines.append(f"  * {warning}")
            lines.append("")

        lines.extend(
            [
                "-" * 60,
                "TOTALS",
                "-" * 60,
                f"  Total cost: ${result.total_cost:.4f}",
                f"  Duration: {result.duration_ms}ms",
                f"  Export path: {self.export_path}",
                "",
                "=" * 60,
            ]
        )

        return "\n".join(lines)

    async def execute(
        self,
        context: dict | None = None,
        **kwargs: Any,
    ) -> OrchestratorResult:
        """
        Execute the full documentation orchestration pipeline.

        Args:
            context: Additional context for the workflows
            **kwargs: Additional arguments

        Returns:
            OrchestratorResult with full details
        """
        started_at = datetime.now()
        result = OrchestratorResult(success=False, phase="scout")
        errors: list[str] = []
        warnings: list[str] = []

        # Validate dependencies
        if not HAS_SCOUT:
            warnings.append("ManageDocumentationCrew not available - using ProjectIndex fallback")
        if not HAS_WRITER:
            errors.append("DocumentGenerationWorkflow not available - cannot generate docs")
            if not self.dry_run:
                result.errors = errors
                result.warnings = warnings
                return result
        if not HAS_PROJECT_INDEX:
            warnings.append("ProjectIndex not available - limited file tracking")

        # Phase 1: Scout
        print("\n" + "=" * 60)
        print("DOCUMENTATION ORCHESTRATOR")
        print("=" * 60)

        items, scout_cost = await self._run_scout_phase()
        self._total_cost += scout_cost

        result.items_found = len(items)
        result.stale_docs = sum(1 for i in items if i.issue_type == "stale_doc")
        result.missing_docs = sum(1 for i in items if i.issue_type != "stale_doc")
        result.scout_cost = scout_cost
        result.phase = "prioritize"

        if not items:
            print("\n[✓] No documentation gaps found!")
            result.success = True
            result.phase = "complete"
            result.duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
            result.total_cost = self._total_cost
            result.summary = self._generate_summary(result, items)
            return result

        # Phase 2: Prioritize
        print(f"\n[PRIORITIZE] Found {len(items)} items, selecting top {self.max_items}...")
        priority_items = self._prioritize_items(items)
        self._items = priority_items

        print("\nTop priority items:")
        for i, item in enumerate(priority_items):
            status = "STALE" if item.issue_type == "stale_doc" else "MISSING"
            print(f"  {i+1}. [{status}] {item.file_path}")

        # Check for dry run
        if self.dry_run:
            print("\n[DRY RUN] Skipping generation phase")
            result.success = True
            result.phase = "complete"
            result.docs_skipped = [i.file_path for i in priority_items]
            result.duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
            result.total_cost = self._total_cost
            result.summary = self._generate_summary(result, priority_items)
            return result

        # Check for approval if not auto_approve
        if not self.auto_approve:
            print(f"\n[!] Ready to generate documentation for {len(priority_items)} items")
            print(f"    Estimated max cost: ${self.max_cost:.2f}")
            print("\n    Set auto_approve=True to proceed automatically")
            result.success = True
            result.phase = "awaiting_approval"
            result.docs_skipped = [i.file_path for i in priority_items]
            result.warnings = warnings
            result.duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
            result.total_cost = self._total_cost
            result.summary = self._generate_summary(result, priority_items)
            return result

        # Phase 3: Generate
        result.phase = "generate"
        generated, updated, skipped, gen_cost = await self._run_generate_phase(priority_items)
        self._total_cost += gen_cost

        result.docs_generated = generated
        result.docs_updated = updated
        result.docs_skipped = skipped
        result.generation_cost = gen_cost
        result.items_processed = len(generated) + len(updated)

        # Phase 4: Update index
        result.phase = "update"
        self._update_project_index(generated, updated)

        # Finalize
        result.success = True
        result.phase = "complete"
        result.total_cost = self._total_cost
        result.errors = errors
        result.warnings = warnings
        result.duration_ms = int((datetime.now() - started_at).total_seconds() * 1000)
        result.summary = self._generate_summary(result, priority_items)

        print(result.summary)

        return result

    async def scout_only(self) -> OrchestratorResult:
        """Run only the scout phase (equivalent to dry_run=True)."""
        self.dry_run = True
        return await self.execute()

    async def scout_as_json(self) -> dict:
        """
        Run scout phase and return JSON-serializable results.

        Used by VSCode extension to display results in Documentation Analysis panel.

        Returns:
            Dict with stats and items list ready for JSON serialization
        """
        import io
        import sys

        self.dry_run = True
        # Suppress console output during scout
        old_stdout = sys.stdout
        sys.stdout = io.StringIO()
        try:
            result = await self.execute()
        finally:
            sys.stdout = old_stdout

        return {
            "success": result.success,
            "stats": {
                "items_found": result.items_found,
                "stale_docs": result.stale_docs,
                "missing_docs": result.missing_docs,
                "scout_cost": result.scout_cost,
                "duration_ms": result.duration_ms,
                "excluded_count": len(self._excluded_files),
            },
            "items": [
                {
                    "id": f"{item.file_path}:{item.issue_type}",
                    "file_path": item.file_path,
                    "issue_type": item.issue_type,
                    "severity": item.severity,
                    "priority": item.priority,
                    "details": item.details,
                    "days_stale": item.days_stale,
                    "loc": item.loc,
                    "related_source": item.related_source[:3] if item.related_source else [],
                }
                for item in self._items
            ],
            "excluded": self._excluded_files,  # Files excluded from scanning
        }

    async def generate_for_files(
        self,
        file_paths: list[str],
        **kwargs: Any,
    ) -> dict:
        """
        Generate documentation for a list of specific files.

        Bypasses scout phase and generates directly for each file.

        Args:
            file_paths: List of file paths to document
            **kwargs: Additional arguments for DocumentGenerationWorkflow

        Returns:
            Dict with results for each file
        """
        results = {
            "success": True,
            "generated": [],
            "failed": [],
            "skipped": [],
            "total_cost": 0.0,
        }

        for file_path in file_paths:
            # Skip excluded files (requirements.txt, package.json, etc.)
            if self._should_exclude(file_path):
                results["skipped"].append(
                    {
                        "file": file_path,
                        "reason": "Excluded by pattern (dependency/config/binary file)",
                    }
                )
                continue

            try:
                result = await self.generate_for_file(file_path, **kwargs)
                if isinstance(result, dict) and result.get("error"):
                    results["failed"].append({"file": file_path, "error": result["error"]})
                else:
                    export_path = result.get("export_path") if isinstance(result, dict) else None
                    cost = result.get("accumulated_cost", 0) if isinstance(result, dict) else 0
                    results["generated"].append(
                        {
                            "file": file_path,
                            "export_path": export_path,
                            "cost": cost,
                        }
                    )
                    results["total_cost"] += cost
            except Exception as e:
                results["failed"].append({"file": file_path, "error": str(e)})
                results["success"] = False

        if results["failed"]:
            results["success"] = len(results["generated"]) > 0  # Partial success

        return results

    async def generate_for_file(
        self,
        file_path: str,
        **kwargs: Any,
    ) -> dict:
        """
        Generate documentation for a specific file.

        Bypasses scout phase and generates directly.

        Args:
            file_path: Path to the file to document
            **kwargs: Additional arguments for DocumentGenerationWorkflow

        Returns:
            Generation result dict
        """
        if self._writer is None:
            return {"error": "DocumentGenerationWorkflow not available"}

        source_path = self.project_root / file_path
        source_content = ""

        if source_path.exists():
            try:
                source_content = source_path.read_text(encoding="utf-8")
            except Exception as e:
                return {"error": f"Could not read file: {e}"}

        result = await self._writer.execute(
            source_code=source_content,
            target=file_path,
            doc_type=kwargs.get("doc_type", self.doc_type),
            audience=kwargs.get("audience", self.audience),
        )

        # Update index
        if isinstance(result, dict) and result.get("document"):
            self._update_project_index([file_path], [])

        return result


# CLI entry point
if __name__ == "__main__":
    import json
    import sys

    async def main():
        path = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "."
        dry_run = "--dry-run" in sys.argv
        auto_approve = "--auto" in sys.argv
        scout_json = "--scout-json" in sys.argv

        # Parse --generate-files argument
        generate_files: list[str] | None = None
        for i, arg in enumerate(sys.argv):
            if arg == "--generate-files" and i + 1 < len(sys.argv):
                try:
                    generate_files = json.loads(sys.argv[i + 1])
                except json.JSONDecodeError:
                    print("Error: --generate-files must be valid JSON array", file=sys.stderr)
                    sys.exit(1)

        orchestrator = DocumentationOrchestrator(
            project_root=path,
            max_items=10,
            max_cost=5.0,
            dry_run=dry_run,
            auto_approve=auto_approve,
        )

        # JSON scout output for VSCode extension
        if scout_json:
            result = await orchestrator.scout_as_json()
            print(json.dumps(result))
            return

        # Generate specific files
        if generate_files:
            result = await orchestrator.generate_for_files(generate_files)
            print(json.dumps(result))
            return

        # Normal execution
        print("\nDocumentationOrchestrator")
        print(f"Project: {path}")
        print(f"Mode: {'DRY RUN' if dry_run else 'FULL' if auto_approve else 'SCOUT + AWAIT'}")

        print("\nComponents:")
        print(f"  Scout (ManageDocumentationCrew): {'✓' if orchestrator._scout else '✗'}")
        print(f"  Writer (DocumentGenerationWorkflow): {'✓' if orchestrator._writer else '✗'}")
        print(f"  ProjectIndex: {'✓' if orchestrator._project_index else '✗'}")

        result = await orchestrator.execute()

        if not result.summary:
            print(f"\nResult: {result.to_dict()}")

    asyncio.run(main())
