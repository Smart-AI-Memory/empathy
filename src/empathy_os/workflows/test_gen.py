"""
Test Generation Workflow

Generates tests targeting areas with historical bugs and low coverage.
Prioritizes test creation for bug-prone code paths.

Stages:
1. identify (CHEAP) - Identify files with low coverage or historical bugs
2. analyze (CAPABLE) - Analyze code structure and existing test patterns
3. generate (CAPABLE) - Generate test cases focusing on edge cases
4. review (PREMIUM) - Quality review and deduplication (conditional)

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import ast
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import BaseWorkflow, ModelTier
from .step_config import WorkflowStepConfig

# =============================================================================
# Default Configuration
# =============================================================================

# Directories to skip during file scanning (configurable via input_data["skip_patterns"])
DEFAULT_SKIP_PATTERNS = [
    # Version control
    ".git",
    ".hg",
    ".svn",
    # Dependencies
    "node_modules",
    "bower_components",
    "vendor",
    # Python caches
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".hypothesis",
    # Virtual environments
    "venv",
    ".venv",
    "env",
    ".env",
    "virtualenv",
    ".virtualenv",
    # Build tools
    ".tox",
    ".nox",
    # Build outputs
    "build",
    "dist",
    "eggs",
    ".eggs",
    "site-packages",
    # IDE
    ".idea",
    ".vscode",
    # Framework-specific
    "migrations",
    "alembic",
    # Documentation
    "_build",
    "docs/_build",
]

# =============================================================================
# AST-Based Function Analysis
# =============================================================================


@dataclass
class FunctionSignature:
    """Detailed function analysis for test generation."""

    name: str
    params: list[tuple[str, str, str | None]]  # (name, type_hint, default)
    return_type: str | None
    is_async: bool
    raises: set[str]
    has_side_effects: bool
    docstring: str | None
    complexity: int = 1  # Rough complexity estimate
    decorators: list[str] = field(default_factory=list)


@dataclass
class ClassSignature:
    """Detailed class analysis for test generation."""

    name: str
    methods: list[FunctionSignature]
    init_params: list[tuple[str, str, str | None]]  # Constructor params
    base_classes: list[str]
    docstring: str | None
    is_enum: bool = False  # True if class inherits from Enum
    is_dataclass: bool = False  # True if class has @dataclass decorator
    required_init_params: int = 0  # Number of params without defaults


class ASTFunctionAnalyzer(ast.NodeVisitor):
    """
    AST-based function analyzer for accurate test generation.

    Extracts:
    - Function signatures with types
    - Exception types raised
    - Side effects detection
    - Complexity estimation

    Parse errors are tracked in the `last_error` attribute for debugging.
    """

    def __init__(self):
        self.functions: list[FunctionSignature] = []
        self.classes: list[ClassSignature] = []
        self._current_class: str | None = None
        self.last_error: str | None = None  # Track parse errors for debugging

    def analyze(
        self, code: str, file_path: str = ""
    ) -> tuple[list[FunctionSignature], list[ClassSignature]]:
        """
        Analyze code and extract function/class signatures.

        Args:
            code: Python source code to analyze
            file_path: Optional file path for error reporting

        Returns:
            Tuple of (functions, classes) lists. If parsing fails,
            returns empty lists and sets self.last_error with details.
        """
        self.last_error = None
        try:
            tree = ast.parse(code)
            self.functions = []
            self.classes = []
            self.visit(tree)
            return self.functions, self.classes
        except SyntaxError as e:
            # Track the error for debugging instead of silent failure
            location = f" at line {e.lineno}" if e.lineno else ""
            file_info = f" in {file_path}" if file_path else ""
            self.last_error = f"SyntaxError{file_info}{location}: {e.msg}"
            return [], []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Extract function signature."""
        if self._current_class is None:  # Only top-level functions
            sig = self._extract_function_signature(node)
            self.functions.append(sig)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Extract async function signature."""
        if self._current_class is None:
            sig = self._extract_function_signature(node, is_async=True)
            self.functions.append(sig)
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Extract class signature with methods."""
        self._current_class = node.name
        methods = []
        init_params: list[tuple[str, str, str | None]] = []

        # Extract base classes
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            elif isinstance(base, ast.Attribute):
                base_classes.append(ast.unparse(base))

        # Detect if this is an Enum
        enum_bases = {"Enum", "IntEnum", "StrEnum", "Flag", "IntFlag", "auto"}
        is_enum = any(b in enum_bases for b in base_classes)

        # Detect if this is a dataclass
        is_dataclass = False
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name) and decorator.id == "dataclass":
                is_dataclass = True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "dataclass":
                    is_dataclass = True

        # Process methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef | ast.AsyncFunctionDef):
                method_sig = self._extract_function_signature(
                    item, is_async=isinstance(item, ast.AsyncFunctionDef)
                )
                methods.append(method_sig)

                # Extract __init__ params
                if item.name == "__init__":
                    init_params = method_sig.params[1:]  # Skip 'self'

        # Count required init params (those without defaults)
        required_init_params = sum(1 for p in init_params if p[2] is None)

        self.classes.append(
            ClassSignature(
                name=node.name,
                methods=methods,
                init_params=init_params,
                base_classes=base_classes,
                docstring=ast.get_docstring(node),
                is_enum=is_enum,
                is_dataclass=is_dataclass,
                required_init_params=required_init_params,
            )
        )

        self._current_class = None
        # Don't call generic_visit to avoid processing methods again

    def _extract_function_signature(
        self, node: ast.FunctionDef | ast.AsyncFunctionDef, is_async: bool = False
    ) -> FunctionSignature:
        """Extract detailed signature from function node."""
        # Extract parameters with types and defaults
        params = []
        defaults = list(node.args.defaults)
        num_defaults = len(defaults)
        num_args = len(node.args.args)

        for i, arg in enumerate(node.args.args):
            param_name = arg.arg
            param_type = ast.unparse(arg.annotation) if arg.annotation else "Any"

            # Calculate default index
            default_idx = i - (num_args - num_defaults)
            default_val = None
            if default_idx >= 0:
                try:
                    default_val = ast.unparse(defaults[default_idx])
                except Exception:
                    default_val = "..."

            params.append((param_name, param_type, default_val))

        # Extract return type
        return_type = ast.unparse(node.returns) if node.returns else None

        # Find raised exceptions
        raises: set[str] = set()
        for child in ast.walk(node):
            if isinstance(child, ast.Raise) and child.exc:
                if isinstance(child.exc, ast.Call):
                    if isinstance(child.exc.func, ast.Name):
                        raises.add(child.exc.func.id)
                    elif isinstance(child.exc.func, ast.Attribute):
                        raises.add(child.exc.func.attr)
                elif isinstance(child.exc, ast.Name):
                    raises.add(child.exc.id)

        # Detect side effects (simple heuristic)
        has_side_effects = self._detect_side_effects(node)

        # Estimate complexity
        complexity = self._estimate_complexity(node)

        # Extract decorators
        decorators = []
        for dec in node.decorator_list:
            if isinstance(dec, ast.Name):
                decorators.append(dec.id)
            elif isinstance(dec, ast.Attribute):
                decorators.append(ast.unparse(dec))
            elif isinstance(dec, ast.Call):
                if isinstance(dec.func, ast.Name):
                    decorators.append(dec.func.id)

        return FunctionSignature(
            name=node.name,
            params=params,
            return_type=return_type,
            is_async=is_async or isinstance(node, ast.AsyncFunctionDef),
            raises=raises,
            has_side_effects=has_side_effects,
            docstring=ast.get_docstring(node),
            complexity=complexity,
            decorators=decorators,
        )

    def _detect_side_effects(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
        """Detect if function has side effects (writes to files, global state, etc.)."""
        side_effect_names = {
            "print",
            "write",
            "open",
            "save",
            "delete",
            "remove",
            "update",
            "insert",
            "execute",
            "send",
            "post",
            "put",
            "patch",
        }

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id.lower() in side_effect_names:
                        return True
                elif isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in side_effect_names:
                        return True
        return False

    def _estimate_complexity(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
        """Estimate cyclomatic complexity (simplified)."""
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.While | ast.For | ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity


# Define step configurations for executor-based execution
TEST_GEN_STEPS = {
    "identify": WorkflowStepConfig(
        name="identify",
        task_type="triage",  # Cheap tier task
        tier_hint="cheap",
        description="Identify files needing tests",
        max_tokens=2000,
    ),
    "analyze": WorkflowStepConfig(
        name="analyze",
        task_type="code_analysis",  # Capable tier task
        tier_hint="capable",
        description="Analyze code structure for test generation",
        max_tokens=3000,
    ),
    "generate": WorkflowStepConfig(
        name="generate",
        task_type="code_generation",  # Capable tier task
        tier_hint="capable",
        description="Generate test cases",
        max_tokens=4000,
    ),
    "review": WorkflowStepConfig(
        name="review",
        task_type="final_review",  # Premium tier task
        tier_hint="premium",
        description="Review and improve generated test suite",
        max_tokens=3000,
    ),
}


class TestGenerationWorkflow(BaseWorkflow):
    """
    Generate tests targeting areas with historical bugs.

    Prioritizes test generation for files that have historically
    been bug-prone and have low test coverage.
    """

    name = "test-gen"
    description = "Generate tests targeting areas with historical bugs"
    stages = ["identify", "analyze", "generate", "review"]
    tier_map = {
        "identify": ModelTier.CHEAP,
        "analyze": ModelTier.CAPABLE,
        "generate": ModelTier.CAPABLE,
        "review": ModelTier.PREMIUM,
    }

    def __init__(
        self,
        patterns_dir: str = "./patterns",
        min_tests_for_review: int = 10,
        write_tests: bool = False,
        output_dir: str = "tests/generated",
        **kwargs: Any,
    ):
        """
        Initialize test generation workflow.

        Args:
            patterns_dir: Directory containing learned patterns
            min_tests_for_review: Minimum tests generated to trigger premium review
            write_tests: If True, write generated tests to output_dir
            output_dir: Directory to write generated test files
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.patterns_dir = patterns_dir
        self.min_tests_for_review = min_tests_for_review
        self.write_tests = write_tests
        self.output_dir = output_dir
        self._test_count: int = 0
        self._bug_hotspots: list[str] = []
        self._load_bug_hotspots()

    def _load_bug_hotspots(self) -> None:
        """Load files with historical bugs from pattern library."""
        debugging_file = Path(self.patterns_dir) / "debugging.json"
        if debugging_file.exists():
            try:
                with open(debugging_file) as fh:
                    data = json.load(fh)
                    patterns = data.get("patterns", [])
                    # Extract files from bug patterns
                    files = set()
                    for p in patterns:
                        for file_entry in p.get("files_affected", []):
                            if file_entry is None:
                                continue
                            files.add(str(file_entry))
                    self._bug_hotspots = list(files)
            except (json.JSONDecodeError, OSError):
                pass

    def should_skip_stage(self, stage_name: str, input_data: Any) -> tuple[bool, str | None]:
        """
        Downgrade review stage if few tests generated.

        Args:
            stage_name: Name of the stage to check
            input_data: Current workflow data

        Returns:
            Tuple of (should_skip, reason)
        """
        if stage_name == "review":
            if self._test_count < self.min_tests_for_review:
                # Downgrade to CAPABLE
                self.tier_map["review"] = ModelTier.CAPABLE
                return False, None
        return False, None

    async def run_stage(
        self, stage_name: str, tier: ModelTier, input_data: Any
    ) -> tuple[Any, int, int]:
        """Route to specific stage implementation."""
        if stage_name == "identify":
            return await self._identify(input_data, tier)
        elif stage_name == "analyze":
            return await self._analyze(input_data, tier)
        elif stage_name == "generate":
            return await self._generate(input_data, tier)
        elif stage_name == "review":
            return await self._review(input_data, tier)
        else:
            raise ValueError(f"Unknown stage: {stage_name}")

    async def _identify(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Identify files needing tests.

        Finds files with low coverage, historical bugs, or
        no existing tests.

        Configurable options via input_data:
            max_files_to_scan: Maximum files to scan before stopping (default: 1000)
            max_file_size_kb: Skip files larger than this (default: 200)
            max_candidates: Maximum candidates to return (default: 50)
            skip_patterns: List of directory patterns to skip (default: DEFAULT_SKIP_PATTERNS)
            include_all_files: Include files with priority=0 (default: False)
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py"])

        # Parse configurable limits with sensible defaults
        max_files_to_scan = input_data.get("max_files_to_scan", 1000)
        max_file_size_kb = input_data.get("max_file_size_kb", 200)
        max_candidates = input_data.get("max_candidates", 50)
        skip_patterns = input_data.get("skip_patterns", DEFAULT_SKIP_PATTERNS)
        include_all_files = input_data.get("include_all_files", False)

        target = Path(target_path)
        candidates: list[dict] = []

        # Track project scope for enterprise reporting
        total_source_files = 0
        existing_test_files = 0

        # Track scan summary for debugging/visibility
        # Use separate counters for type safety
        scan_counts = {
            "files_scanned": 0,
            "files_too_large": 0,
            "files_read_error": 0,
            "files_excluded_by_pattern": 0,
        }
        early_exit_reason: str | None = None

        max_file_size_bytes = max_file_size_kb * 1024
        scan_limit_reached = False

        if target.exists():
            for ext in file_types:
                if scan_limit_reached:
                    break

                for file_path in target.rglob(f"*{ext}"):
                    # Check if we've hit the scan limit
                    if scan_counts["files_scanned"] >= max_files_to_scan:
                        early_exit_reason = f"max_files_to_scan ({max_files_to_scan}) reached"
                        scan_limit_reached = True
                        break

                    # Skip non-code directories using configurable patterns
                    file_str = str(file_path)
                    if any(skip in file_str for skip in skip_patterns):
                        scan_counts["files_excluded_by_pattern"] += 1
                        continue

                    # Count test files separately for scope awareness
                    if "test_" in file_str or "_test." in file_str or "/tests/" in file_str:
                        existing_test_files += 1
                        continue

                    # Check file size before reading
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_file_size_bytes:
                            scan_counts["files_too_large"] += 1
                            continue
                    except OSError:
                        scan_counts["files_read_error"] += 1
                        continue

                    # Count source files and increment scan counter
                    total_source_files += 1
                    scan_counts["files_scanned"] += 1

                    try:
                        content = file_path.read_text(errors="ignore")
                        lines = len(content.splitlines())

                        # Check if in bug hotspots
                        is_hotspot = any(hotspot in file_str for hotspot in self._bug_hotspots)

                        # Check for existing tests
                        test_file = self._find_test_file(file_path)
                        has_tests = test_file.exists() if test_file else False

                        # Calculate priority
                        priority = 0
                        if is_hotspot:
                            priority += 50
                        if not has_tests:
                            priority += 30
                        if lines > 100:
                            priority += 10
                        if lines > 300:
                            priority += 10

                        # Include if priority > 0 OR include_all_files is set
                        if priority > 0 or include_all_files:
                            candidates.append(
                                {
                                    "file": file_str,
                                    "lines": lines,
                                    "is_hotspot": is_hotspot,
                                    "has_tests": has_tests,
                                    "priority": priority,
                                }
                            )
                    except OSError:
                        scan_counts["files_read_error"] += 1
                        continue

        # Sort by priority
        candidates.sort(key=lambda x: -x["priority"])

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(candidates)) // 4

        # Calculate scope metrics for enterprise reporting
        analyzed_count = min(max_candidates, len(candidates))
        coverage_pct = (analyzed_count / len(candidates) * 100) if candidates else 100

        return (
            {
                "candidates": candidates[:max_candidates],
                "total_candidates": len(candidates),
                "hotspot_count": len([c for c in candidates if c["is_hotspot"]]),
                "untested_count": len([c for c in candidates if not c["has_tests"]]),
                # Scope awareness fields for enterprise reporting
                "total_source_files": total_source_files,
                "existing_test_files": existing_test_files,
                "large_project_warning": len(candidates) > 100,
                "analysis_coverage_percent": coverage_pct,
                # Scan summary for debugging/visibility
                "scan_summary": {**scan_counts, "early_exit_reason": early_exit_reason},
                # Pass through config for subsequent stages
                "config": {
                    "max_files_to_analyze": input_data.get("max_files_to_analyze", 20),
                    "max_functions_per_file": input_data.get("max_functions_per_file", 30),
                    "max_classes_per_file": input_data.get("max_classes_per_file", 15),
                    "max_files_to_generate": input_data.get("max_files_to_generate", 15),
                    "max_functions_to_generate": input_data.get("max_functions_to_generate", 8),
                    "max_classes_to_generate": input_data.get("max_classes_to_generate", 4),
                },
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _find_test_file(self, source_file: Path) -> Path | None:
        """Find corresponding test file for a source file."""
        name = source_file.stem
        parent = source_file.parent

        # Check common test locations
        possible = [
            parent / f"test_{name}.py",
            parent / "tests" / f"test_{name}.py",
            parent.parent / "tests" / f"test_{name}.py",
        ]

        for p in possible:
            if p.exists():
                return p

        return possible[0]  # Return expected location even if doesn't exist

    async def _analyze(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Analyze code structure for test generation.

        Examines functions, classes, and patterns to determine
        what tests should be generated.

        Uses config from _identify stage for limits:
            max_files_to_analyze: Maximum files to analyze (default: 20)
            max_functions_per_file: Maximum functions per file (default: 30)
            max_classes_per_file: Maximum classes per file (default: 15)
        """
        # Get config from previous stage or use defaults
        config = input_data.get("config", {})
        max_files_to_analyze = config.get("max_files_to_analyze", 20)
        max_functions_per_file = config.get("max_functions_per_file", 30)
        max_classes_per_file = config.get("max_classes_per_file", 15)

        candidates = input_data.get("candidates", [])[:max_files_to_analyze]
        analysis: list[dict] = []
        parse_errors: list[str] = []  # Track files that failed to parse

        for candidate in candidates:
            file_path = Path(candidate["file"])
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(errors="ignore")

                # Extract testable items with configurable limits and error tracking
                functions, func_error = self._extract_functions(
                    content, candidate["file"], max_functions_per_file
                )
                classes, class_error = self._extract_classes(
                    content, candidate["file"], max_classes_per_file
                )

                # Track parse errors for visibility
                if func_error:
                    parse_errors.append(func_error)
                if class_error and class_error != func_error:
                    parse_errors.append(class_error)

                analysis.append(
                    {
                        "file": candidate["file"],
                        "priority": candidate["priority"],
                        "functions": functions,
                        "classes": classes,
                        "function_count": len(functions),
                        "class_count": len(classes),
                        "test_suggestions": self._generate_suggestions(functions, classes),
                    }
                )
            except OSError:
                continue

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(analysis)) // 4

        return (
            {
                "analysis": analysis,
                "total_functions": sum(a["function_count"] for a in analysis),
                "total_classes": sum(a["class_count"] for a in analysis),
                "parse_errors": parse_errors,  # Expose errors for debugging
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _extract_functions(
        self, content: str, file_path: str = "", max_functions: int = 30
    ) -> tuple[list[dict], str | None]:
        """
        Extract function definitions from Python code using AST analysis.

        Args:
            content: Python source code
            file_path: File path for error reporting
            max_functions: Maximum functions to extract (configurable)

        Returns:
            Tuple of (functions list, error message or None)
        """
        analyzer = ASTFunctionAnalyzer()
        functions, _ = analyzer.analyze(content, file_path)

        result = []
        for sig in functions[:max_functions]:
            if not sig.name.startswith("_") or sig.name.startswith("__"):
                result.append(
                    {
                        "name": sig.name,
                        "params": [(p[0], p[1], p[2]) for p in sig.params],
                        "param_names": [p[0] for p in sig.params],
                        "is_async": sig.is_async,
                        "return_type": sig.return_type,
                        "raises": list(sig.raises),
                        "has_side_effects": sig.has_side_effects,
                        "complexity": sig.complexity,
                        "docstring": sig.docstring,
                    }
                )
        return result, analyzer.last_error

    def _extract_classes(
        self, content: str, file_path: str = "", max_classes: int = 15
    ) -> tuple[list[dict], str | None]:
        """
        Extract class definitions from Python code using AST analysis.

        Args:
            content: Python source code
            file_path: File path for error reporting
            max_classes: Maximum classes to extract (configurable)

        Returns:
            Tuple of (classes list, error message or None)
        """
        analyzer = ASTFunctionAnalyzer()
        _, classes = analyzer.analyze(content, file_path)

        result = []
        for sig in classes[:max_classes]:
            # Skip enums - they don't need traditional class tests
            if sig.is_enum:
                continue

            methods = [
                {
                    "name": m.name,
                    "params": [(p[0], p[1], p[2]) for p in m.params],
                    "is_async": m.is_async,
                    "raises": list(m.raises),
                }
                for m in sig.methods
                if not m.name.startswith("_") or m.name == "__init__"
            ]
            result.append(
                {
                    "name": sig.name,
                    "init_params": [(p[0], p[1], p[2]) for p in sig.init_params],
                    "methods": methods,
                    "base_classes": sig.base_classes,
                    "docstring": sig.docstring,
                    "is_dataclass": sig.is_dataclass,
                    "required_init_params": sig.required_init_params,
                }
            )
        return result, analyzer.last_error

    def _generate_suggestions(self, functions: list[dict], classes: list[dict]) -> list[str]:
        """Generate test suggestions based on code structure."""
        suggestions = []

        for func in functions[:5]:
            if func["params"]:
                suggestions.append(f"Test {func['name']} with valid inputs")
                suggestions.append(f"Test {func['name']} with edge cases")
            if func["is_async"]:
                suggestions.append(f"Test {func['name']} async behavior")

        for cls in classes[:3]:
            suggestions.append(f"Test {cls['name']} initialization")
            suggestions.append(f"Test {cls['name']} methods")

        return suggestions

    async def _generate(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Generate test cases.

        Creates test code targeting identified functions
        and classes, focusing on edge cases.

        Uses config from _identify stage for limits:
            max_files_to_generate: Maximum files to generate tests for (default: 15)
            max_functions_to_generate: Maximum functions per file (default: 8)
            max_classes_to_generate: Maximum classes per file (default: 4)
        """
        # Get config from previous stages or use defaults
        config = input_data.get("config", {})
        max_files_to_generate = config.get("max_files_to_generate", 15)
        max_functions_to_generate = config.get("max_functions_to_generate", 8)
        max_classes_to_generate = config.get("max_classes_to_generate", 4)

        analysis = input_data.get("analysis", [])
        generated_tests: list[dict] = []

        for item in analysis[:max_files_to_generate]:
            file_path = item["file"]
            module_name = Path(file_path).stem

            tests = []
            for func in item.get("functions", [])[:max_functions_to_generate]:
                test_code = self._generate_test_for_function(module_name, func)
                tests.append(
                    {
                        "target": func["name"],
                        "type": "function",
                        "code": test_code,
                    }
                )

            for cls in item.get("classes", [])[:max_classes_to_generate]:
                test_code = self._generate_test_for_class(module_name, cls)
                tests.append(
                    {
                        "target": cls["name"],
                        "type": "class",
                        "code": test_code,
                    }
                )

            if tests:
                generated_tests.append(
                    {
                        "source_file": file_path,
                        "test_file": f"test_{module_name}.py",
                        "tests": tests,
                        "test_count": len(tests),
                    }
                )

        self._test_count = sum(t["test_count"] for t in generated_tests)

        # Write tests to files if enabled (via input_data or instance config)
        write_tests = input_data.get("write_tests", self.write_tests)
        output_dir = input_data.get("output_dir", self.output_dir)
        written_files: list[str] = []

        if write_tests and generated_tests:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            for test_item in generated_tests:
                test_filename = test_item["test_file"]
                test_file_path = output_path / test_filename

                # Combine all test code for this file
                combined_code = []
                imports_added = set()

                for test in test_item["tests"]:
                    code = test["code"]
                    # Extract and dedupe imports
                    for line in code.split("\n"):
                        if line.startswith("import ") or line.startswith("from "):
                            if line not in imports_added:
                                imports_added.add(line)
                        elif line.strip():
                            combined_code.append(line)

                # Write the combined test file
                final_code = "\n".join(sorted(imports_added)) + "\n\n" + "\n".join(combined_code)
                test_file_path.write_text(final_code)
                written_files.append(str(test_file_path))
                test_item["written_to"] = str(test_file_path)

        input_tokens = len(str(input_data)) // 4
        output_tokens = sum(len(str(t)) for t in generated_tests) // 4

        return (
            {
                "generated_tests": generated_tests,
                "total_tests_generated": self._test_count,
                "written_files": written_files,
                "tests_written": len(written_files) > 0,
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _generate_test_for_function(self, module: str, func: dict) -> str:
        """Generate executable tests for a function based on AST analysis."""
        name = func["name"]
        params = func.get("params", [])  # List of (name, type, default) tuples
        param_names = func.get("param_names", [p[0] if isinstance(p, tuple) else p for p in params])
        is_async = func.get("is_async", False)
        return_type = func.get("return_type")
        raises = func.get("raises", [])
        has_side_effects = func.get("has_side_effects", False)

        # Generate test values based on parameter types
        test_cases = self._generate_test_cases_for_params(params)
        param_str = ", ".join(test_cases.get("valid_args", [""] * len(params)))

        # Build parametrized test if we have multiple test cases
        parametrize_cases = test_cases.get("parametrize_cases", [])

        tests = []
        tests.append(f"import pytest\nfrom {module} import {name}\n")

        # Generate parametrized test if we have cases
        if parametrize_cases and len(parametrize_cases) > 1:
            param_names_str = ", ".join(param_names) if param_names else "value"
            cases_str = ",\n    ".join(parametrize_cases)

            if is_async:
                tests.append(
                    f'''
@pytest.mark.parametrize("{param_names_str}", [
    {cases_str},
])
@pytest.mark.asyncio
async def test_{name}_with_various_inputs({param_names_str}):
    """Test {name} with various input combinations."""
    result = await {name}({", ".join(param_names)})
    assert result is not None
'''
                )
            else:
                tests.append(
                    f'''
@pytest.mark.parametrize("{param_names_str}", [
    {cases_str},
])
def test_{name}_with_various_inputs({param_names_str}):
    """Test {name} with various input combinations."""
    result = {name}({", ".join(param_names)})
    assert result is not None
'''
                )
        else:
            # Simple valid input test
            if is_async:
                tests.append(
                    f'''
@pytest.mark.asyncio
async def test_{name}_returns_value():
    """Test that {name} returns a value with valid inputs."""
    result = await {name}({param_str})
    assert result is not None
'''
                )
            else:
                tests.append(
                    f'''
def test_{name}_returns_value():
    """Test that {name} returns a value with valid inputs."""
    result = {name}({param_str})
    assert result is not None
'''
                )

        # Generate edge case tests based on parameter types
        edge_cases = test_cases.get("edge_cases", [])
        if edge_cases:
            edge_cases_str = ",\n    ".join(edge_cases)
            if is_async:
                tests.append(
                    f'''
@pytest.mark.parametrize("edge_input", [
    {edge_cases_str},
])
@pytest.mark.asyncio
async def test_{name}_edge_cases(edge_input):
    """Test {name} with edge case inputs."""
    try:
        result = await {name}(edge_input)
        # Function should either return a value or raise an expected error
        assert result is not None or result == 0 or result == "" or result == []
    except (ValueError, TypeError, KeyError) as e:
        # Expected error for edge cases
        assert str(e)  # Error message should not be empty
'''
                )
            else:
                tests.append(
                    f'''
@pytest.mark.parametrize("edge_input", [
    {edge_cases_str},
])
def test_{name}_edge_cases(edge_input):
    """Test {name} with edge case inputs."""
    try:
        result = {name}(edge_input)
        # Function should either return a value or raise an expected error
        assert result is not None or result == 0 or result == "" or result == []
    except (ValueError, TypeError, KeyError) as e:
        # Expected error for edge cases
        assert str(e)  # Error message should not be empty
'''
                )

        # Generate exception tests for each raised exception
        for exc_type in raises[:3]:  # Limit to 3 exception types
            if is_async:
                tests.append(
                    f'''
@pytest.mark.asyncio
async def test_{name}_raises_{exc_type.lower()}():
    """Test that {name} raises {exc_type} for invalid inputs."""
    with pytest.raises({exc_type}):
        await {name}(None)  # Adjust input to trigger {exc_type}
'''
                )
            else:
                tests.append(
                    f'''
def test_{name}_raises_{exc_type.lower()}():
    """Test that {name} raises {exc_type} for invalid inputs."""
    with pytest.raises({exc_type}):
        {name}(None)  # Adjust input to trigger {exc_type}
'''
                )

        # Add return type assertion if we know the type
        if return_type and return_type not in ("None", "Any"):
            type_check = self._get_type_assertion(return_type)
            if type_check and not has_side_effects:
                if is_async:
                    tests.append(
                        f'''
@pytest.mark.asyncio
async def test_{name}_returns_correct_type():
    """Test that {name} returns the expected type."""
    result = await {name}({param_str})
    {type_check}
'''
                    )
                else:
                    tests.append(
                        f'''
def test_{name}_returns_correct_type():
    """Test that {name} returns the expected type."""
    result = {name}({param_str})
    {type_check}
'''
                    )

        return "\n".join(tests)

    def _generate_test_cases_for_params(self, params: list) -> dict:
        """Generate test cases based on parameter types."""
        valid_args = []
        parametrize_cases = []
        edge_cases = []

        for param in params:
            if isinstance(param, tuple) and len(param) >= 2:
                _name, type_hint, default = param[0], param[1], param[2] if len(param) > 2 else None
            else:
                _name = param if isinstance(param, str) else str(param)  # noqa: F841
                type_hint = "Any"
                default = None

            # Generate valid value based on type
            if "str" in type_hint.lower():
                valid_args.append('"test_value"')
                parametrize_cases.extend(['"hello"', '"world"', '"test_string"'])
                edge_cases.extend(['""', '" "', '"a" * 1000'])
            elif "int" in type_hint.lower():
                valid_args.append("42")
                parametrize_cases.extend(["0", "1", "100", "-1"])
                edge_cases.extend(["0", "-1", "2**31 - 1"])
            elif "float" in type_hint.lower():
                valid_args.append("3.14")
                parametrize_cases.extend(["0.0", "1.0", "-1.5", "100.5"])
                edge_cases.extend(["0.0", "-0.0", "float('inf')"])
            elif "bool" in type_hint.lower():
                valid_args.append("True")
                parametrize_cases.extend(["True", "False"])
            elif "list" in type_hint.lower():
                valid_args.append("[1, 2, 3]")
                parametrize_cases.extend(["[]", "[1]", "[1, 2, 3]"])
                edge_cases.extend(["[]", "[None]"])
            elif "dict" in type_hint.lower():
                valid_args.append('{"key": "value"}')
                parametrize_cases.extend(["{}", '{"a": 1}', '{"key": "value"}'])
                edge_cases.extend(["{}"])
            elif default is not None:
                valid_args.append(str(default))
            else:
                valid_args.append("None")
                edge_cases.append("None")

        return {
            "valid_args": valid_args,
            "parametrize_cases": parametrize_cases[:5],  # Limit cases
            "edge_cases": list(set(edge_cases))[:5],  # Unique edge cases
        }

    def _get_type_assertion(self, return_type: str) -> str | None:
        """Generate assertion for return type checking."""
        type_map = {
            "str": "assert isinstance(result, str)",
            "int": "assert isinstance(result, int)",
            "float": "assert isinstance(result, (int, float))",
            "bool": "assert isinstance(result, bool)",
            "list": "assert isinstance(result, list)",
            "dict": "assert isinstance(result, dict)",
            "tuple": "assert isinstance(result, tuple)",
        }
        for type_name, assertion in type_map.items():
            if type_name in return_type.lower():
                return assertion
        return None

    def _get_param_test_values(self, type_hint: str) -> list[str]:
        """Get test values for a single parameter based on its type."""
        type_hint_lower = type_hint.lower()
        if "str" in type_hint_lower:
            return ['"hello"', '"world"', '"test_string"']
        elif "int" in type_hint_lower:
            return ["0", "1", "42", "-1"]
        elif "float" in type_hint_lower:
            return ["0.0", "1.0", "3.14"]
        elif "bool" in type_hint_lower:
            return ["True", "False"]
        elif "list" in type_hint_lower:
            return ["[]", "[1, 2, 3]"]
        elif "dict" in type_hint_lower:
            return ["{}", '{"key": "value"}']
        else:
            return ['"test_value"']

    def _generate_test_for_class(self, module: str, cls: dict) -> str:
        """Generate executable test class based on AST analysis."""
        name = cls["name"]
        init_params = cls.get("init_params", [])
        methods = cls.get("methods", [])
        required_params = cls.get("required_init_params", 0)
        _docstring = cls.get("docstring", "")  # Reserved for future use  # noqa: F841

        # Generate constructor arguments - ensure we have values for ALL required params
        init_args = self._generate_test_cases_for_params(init_params)
        valid_args = init_args.get("valid_args", [])

        # Ensure we have enough args for required params
        while len(valid_args) < required_params:
            valid_args.append('"test_value"')

        init_arg_str = ", ".join(valid_args)

        tests = []
        tests.append(f"import pytest\nfrom {module} import {name}\n")

        # Fixture for class instance
        tests.append(
            f'''
@pytest.fixture
def {name.lower()}_instance():
    """Create a {name} instance for testing."""
    return {name}({init_arg_str})
'''
        )

        # Test initialization
        tests.append(
            f'''
class Test{name}:
    """Tests for {name} class."""

    def test_initialization(self):
        """Test that {name} can be instantiated."""
        instance = {name}({init_arg_str})
        assert instance is not None
'''
        )

        # Only generate parametrized tests for single-param classes to avoid tuple mismatches
        if len(init_params) == 1 and init_params[0][2] is None:
            # Single required param - safe to parametrize
            param_name = init_params[0][0]
            param_type = init_params[0][1]
            cases = self._get_param_test_values(param_type)
            if len(cases) > 1:
                cases_str = ",\n        ".join(cases)
                tests.append(
                    f'''
    @pytest.mark.parametrize("{param_name}", [
        {cases_str},
    ])
    def test_initialization_with_various_args(self, {param_name}):
        """Test {name} initialization with various arguments."""
        instance = {name}({param_name})
        assert instance is not None
'''
                )

        # Generate tests for each public method
        for method in methods[:5]:  # Limit to 5 methods
            method_name = method.get("name", "")
            if method_name.startswith("_") and method_name != "__init__":
                continue
            if method_name == "__init__":
                continue

            method_params = method.get("params", [])[1:]  # Skip self
            is_async = method.get("is_async", False)
            raises = method.get("raises", [])

            # Generate method call args
            method_args = self._generate_test_cases_for_params(method_params)
            method_arg_str = ", ".join(method_args.get("valid_args", []))

            if is_async:
                tests.append(
                    f'''
    @pytest.mark.asyncio
    async def test_{method_name}_returns_value(self, {name.lower()}_instance):
        """Test that {method_name} returns a value."""
        result = await {name.lower()}_instance.{method_name}({method_arg_str})
        assert result is not None or result == 0 or result == "" or result == []
'''
                )
            else:
                tests.append(
                    f'''
    def test_{method_name}_returns_value(self, {name.lower()}_instance):
        """Test that {method_name} returns a value."""
        result = {name.lower()}_instance.{method_name}({method_arg_str})
        assert result is not None or result == 0 or result == "" or result == []
'''
                )

            # Add exception tests for methods that raise
            for exc_type in raises[:2]:
                if is_async:
                    tests.append(
                        f'''
    @pytest.mark.asyncio
    async def test_{method_name}_raises_{exc_type.lower()}(self, {name.lower()}_instance):
        """Test that {method_name} raises {exc_type} for invalid inputs."""
        with pytest.raises({exc_type}):
            await {name.lower()}_instance.{method_name}(None)
'''
                    )
                else:
                    tests.append(
                        f'''
    def test_{method_name}_raises_{exc_type.lower()}(self, {name.lower()}_instance):
        """Test that {method_name} raises {exc_type} for invalid inputs."""
        with pytest.raises({exc_type}):
            {name.lower()}_instance.{method_name}(None)
'''
                    )

        return "\n".join(tests)

    async def _review(self, input_data: dict, tier: ModelTier) -> tuple[dict, int, int]:
        """
        Review and improve generated tests using LLM.

        This stage now receives the generated test code and uses the LLM
        to create the final analysis report.
        """
        # Get the generated tests from the previous stage
        generated_tests = input_data.get("generated_tests", [])
        if not generated_tests:
            # If no tests were generated, return the input data as is.
            return input_data, 0, 0

        # Prepare the context for the LLM by formatting the generated test code
        test_context = "<generated_tests>\n"
        total_test_count = 0
        for test_item in generated_tests:
            test_context += f'  <file path="{test_item["source_file"]}">\n'
            for test in test_item["tests"]:
                # Extract ALL test names from code (not just the first one)
                test_names = []
                try:
                    # Use findall to get ALL test functions
                    matches = re.findall(r"def\s+(test_\w+)", test["code"])
                    test_names = matches if matches else ["unnamed"]
                except Exception:
                    test_names = ["unnamed"]

                # Report each test function found
                for test_name in test_names:
                    test_context += f'    <test name="{test_name}" target="{test["target"]}" type="{test.get("type", "unknown")}" />\n'
                    total_test_count += 1
            test_context += "  </file>\n"
        test_context += "</generated_tests>\n"
        test_context += f"\n<summary>Total test functions: {total_test_count}</summary>\n"

        # Build the system prompt directly for the review stage
        target_files = [item["source_file"] for item in generated_tests]
        file_list = "\n".join(f"  - {f}" for f in target_files)

        system_prompt = f"""You are an automated test coverage analysis tool. You MUST output a report directly - no conversation, no questions, no preamble.

CRITICAL RULES (VIOLATIONS WILL CAUSE SYSTEM FAILURE):
1. START your response with "# Test Gap Analysis Report" - no other text before this
2. NEVER ask questions or seek clarification
3. NEVER use phrases like "let me ask", "what's your goal", "would you like"
4. NEVER offer to expand or provide more information
5. Output ONLY the structured report - nothing else

Target files ({len(generated_tests)}):
{file_list}

REQUIRED OUTPUT FORMAT (follow exactly):

# Test Gap Analysis Report

## Executive Summary
| Metric | Value |
|--------|-------|
| **Total Test Functions** | [count] |
| **Files Covered** | [count] |
| **Classes Tested** | [count] |
| **Functions Tested** | [count] |

## Coverage by File
[For each file, show a table with Target, Type, Tests count, and Gap Assessment]

## Identified Gaps
[List specific missing tests with severity: HIGH/MEDIUM/LOW]

## Prioritized Recommendations
[Numbered list of specific tests to add, ordered by priority]

END OF REQUIRED FORMAT - output nothing after recommendations."""

        user_message = f"Generate the test gap analysis report for:\n{test_context}"

        # Call the LLM using the provider-agnostic executor from BaseWorkflow
        step_config = TEST_GEN_STEPS["review"]
        report, in_tokens, out_tokens, _cost = await self.run_step_with_executor(
            step=step_config,
            prompt=user_message,
            system=system_prompt,
        )

        # Validate response - check for question patterns that indicate non-compliance
        total_in = in_tokens
        total_out = out_tokens

        if self._response_contains_questions(report):
            # Retry with even stricter prompt
            retry_prompt = f"""OUTPUT ONLY THIS EXACT FORMAT - NO OTHER TEXT:

# Test Gap Analysis Report

## Executive Summary
| Metric | Value |
|--------|-------|
| **Total Test Functions** | {total_test_count} |
| **Files Covered** | {len(generated_tests)} |

## Coverage by File

{self._generate_coverage_table(generated_tests)}

## Identified Gaps
- Missing error handling tests
- Missing edge case tests
- Missing integration tests

## Prioritized Recommendations
1. Add exception/error tests for each class
2. Add boundary condition tests
3. Add integration tests between components"""

            report, retry_in, retry_out, _ = await self.run_step_with_executor(
                step=step_config,
                prompt=retry_prompt,
                system="You are a report formatter. Output ONLY the text provided. Do not add any commentary.",
            )
            total_in += retry_in
            total_out += retry_out

            # If still asking questions, use fallback programmatic report
            if self._response_contains_questions(report):
                report = self._generate_fallback_report(generated_tests, total_test_count)

        # Replace the previous analysis with the final, accurate report
        input_data["analysis_report"] = report
        return input_data, total_in, total_out

    def _response_contains_questions(self, response: str) -> bool:
        """Check if response contains question patterns indicating non-compliance."""
        if not response:
            return True

        # Check first 500 chars for question patterns
        first_part = response[:500].lower()

        question_patterns = [
            "let me ask",
            "what's your",
            "what is your",
            "would you like",
            "do you have",
            "could you",
            "can you",
            "clarifying question",
            "before i generate",
            "before generating",
            "i need to know",
            "please provide",
            "please clarify",
            "?",  # Questions in first 500 chars is suspicious
        ]

        # Also check if it doesn't start with expected format
        if not response.strip().startswith("#"):
            return True

        return any(pattern in first_part for pattern in question_patterns)

    def _generate_coverage_table(self, generated_tests: list[dict]) -> str:
        """Generate a simple coverage table for the retry prompt."""
        lines = []
        for item in generated_tests[:10]:
            file_name = Path(item["source_file"]).name
            test_count = item.get("test_count", 0)
            lines.append(f"| {file_name} | {test_count} tests | Basic coverage |")
        return "| File | Tests | Coverage |\n|------|-------|----------|\n" + "\n".join(lines)

    def _generate_fallback_report(self, generated_tests: list[dict], total_test_count: int) -> str:
        """Generate a programmatic fallback report when LLM fails to comply."""
        lines = ["# Test Gap Analysis Report", ""]
        lines.append("## Executive Summary")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| **Total Test Functions** | {total_test_count} |")
        lines.append(f"| **Files Covered** | {len(generated_tests)} |")

        # Count classes and functions
        total_classes = sum(
            len([t for t in item.get("tests", []) if t.get("type") == "class"])
            for item in generated_tests
        )
        total_functions = sum(
            len([t for t in item.get("tests", []) if t.get("type") == "function"])
            for item in generated_tests
        )
        lines.append(f"| **Classes Tested** | {total_classes} |")
        lines.append(f"| **Functions Tested** | {total_functions} |")
        lines.append("")

        lines.append("## Coverage by File")
        lines.append("| File | Tests | Targets |")
        lines.append("|------|-------|---------|")
        for item in generated_tests:
            file_name = Path(item["source_file"]).name
            test_count = item.get("test_count", 0)
            targets = ", ".join(t.get("target", "?") for t in item.get("tests", [])[:3])
            if len(item.get("tests", [])) > 3:
                targets += "..."
            lines.append(f"| {file_name} | {test_count} | {targets} |")
        lines.append("")

        lines.append("## Identified Gaps")
        lines.append("- **HIGH**: Missing error/exception handling tests")
        lines.append("- **MEDIUM**: Missing boundary condition tests")
        lines.append("- **MEDIUM**: Missing async behavior tests")
        lines.append("- **LOW**: Missing integration tests")
        lines.append("")

        lines.append("## Prioritized Recommendations")
        lines.append("1. Add `pytest.raises` tests for each function that can throw exceptions")
        lines.append("2. Add edge case tests (empty inputs, None values, large data)")
        lines.append("3. Add concurrent/async tests for async functions")
        lines.append("4. Add integration tests between related classes")

        return "\n".join(lines)

    def get_max_tokens(self, stage_name: str) -> int:
        """Get the maximum token limit for a stage."""
        # Default to 4096
        return 4096


def format_test_gen_report(result: dict, input_data: dict) -> str:
    """
    Format test generation output as a human-readable report.

    Args:
        result: The review stage result
        input_data: Input data from previous stages

    Returns:
        Formatted report string
    """
    import re

    lines = []

    # Header
    total_tests = result.get("total_tests", 0)
    files_covered = result.get("files_covered", 0)

    lines.append("=" * 60)
    lines.append("TEST GAP ANALYSIS REPORT")
    lines.append("=" * 60)
    lines.append("")

    # Summary stats
    total_candidates = input_data.get("total_candidates", 0)
    hotspot_count = input_data.get("hotspot_count", 0)
    untested_count = input_data.get("untested_count", 0)

    lines.append("-" * 60)
    lines.append("SUMMARY")
    lines.append("-" * 60)
    lines.append(f"Tests Generated:     {total_tests}")
    lines.append(f"Files Covered:       {files_covered}")
    lines.append(f"Total Candidates:    {total_candidates}")
    lines.append(f"Bug Hotspots Found:  {hotspot_count}")
    lines.append(f"Untested Files:      {untested_count}")
    lines.append("")

    # Status indicator
    if total_tests == 0:
        lines.append("⚠️  No tests were generated")
    elif total_tests < 5:
        lines.append(f"🟡 Generated {total_tests} test(s) - consider adding more coverage")
    elif total_tests < 20:
        lines.append(f"🟢 Generated {total_tests} tests - good coverage")
    else:
        lines.append(f"✅ Generated {total_tests} tests - excellent coverage")
    lines.append("")

    # Scope notice for enterprise clarity
    total_source = input_data.get("total_source_files", 0)
    existing_tests = input_data.get("existing_test_files", 0)
    coverage_pct = input_data.get("analysis_coverage_percent", 100)
    large_project = input_data.get("large_project_warning", False)

    if total_source > 0 or existing_tests > 0:
        lines.append("-" * 60)
        lines.append("SCOPE NOTICE")
        lines.append("-" * 60)

        if large_project:
            lines.append("⚠️  LARGE PROJECT: Only high-priority files analyzed")
            lines.append(f"   Coverage: {coverage_pct:.0f}% of candidate files")
            lines.append("")

        lines.append(f"Source Files Found:   {total_source}")
        lines.append(f"Existing Test Files:  {existing_tests}")
        lines.append(f"Files Analyzed:       {files_covered}")

        if existing_tests > 0:
            lines.append("")
            lines.append("Note: This report identifies gaps in untested files.")
            lines.append("Run 'pytest --co -q' for full test suite statistics.")
        lines.append("")

    # Parse XML review feedback if present
    review = result.get("review_feedback", "")
    xml_summary = ""
    xml_findings = []
    xml_tests = []
    coverage_improvement = ""

    if review and "<response>" in review:
        # Extract summary
        summary_match = re.search(r"<summary>(.*?)</summary>", review, re.DOTALL)
        if summary_match:
            xml_summary = summary_match.group(1).strip()

        # Extract coverage improvement
        coverage_match = re.search(
            r"<coverage-improvement>(.*?)</coverage-improvement>", review, re.DOTALL
        )
        if coverage_match:
            coverage_improvement = coverage_match.group(1).strip()

        # Extract findings
        for finding_match in re.finditer(
            r'<finding severity="(\w+)">(.*?)</finding>', review, re.DOTALL
        ):
            severity = finding_match.group(1)
            finding_content = finding_match.group(2)

            title_match = re.search(r"<title>(.*?)</title>", finding_content, re.DOTALL)
            location_match = re.search(r"<location>(.*?)</location>", finding_content, re.DOTALL)
            fix_match = re.search(r"<fix>(.*?)</fix>", finding_content, re.DOTALL)

            xml_findings.append(
                {
                    "severity": severity,
                    "title": title_match.group(1).strip() if title_match else "Unknown",
                    "location": location_match.group(1).strip() if location_match else "",
                    "fix": fix_match.group(1).strip() if fix_match else "",
                }
            )

        # Extract suggested tests
        for test_match in re.finditer(r'<test target="([^"]+)">(.*?)</test>', review, re.DOTALL):
            target = test_match.group(1)
            test_content = test_match.group(2)

            type_match = re.search(r"<type>(.*?)</type>", test_content, re.DOTALL)
            desc_match = re.search(r"<description>(.*?)</description>", test_content, re.DOTALL)

            xml_tests.append(
                {
                    "target": target,
                    "type": type_match.group(1).strip() if type_match else "unit",
                    "description": desc_match.group(1).strip() if desc_match else "",
                }
            )

    # Show parsed summary
    if xml_summary:
        lines.append("-" * 60)
        lines.append("QUALITY ASSESSMENT")
        lines.append("-" * 60)
        # Word wrap the summary
        words = xml_summary.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= 58:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        lines.append("")

        if coverage_improvement:
            lines.append(f"📈 {coverage_improvement}")
            lines.append("")

    # Show findings by severity
    if xml_findings:
        lines.append("-" * 60)
        lines.append("QUALITY FINDINGS")
        lines.append("-" * 60)

        severity_emoji = {"high": "🔴", "medium": "🟠", "low": "🟡", "info": "🔵"}
        severity_order = {"high": 0, "medium": 1, "low": 2, "info": 3}

        sorted_findings = sorted(xml_findings, key=lambda f: severity_order.get(f["severity"], 4))

        for finding in sorted_findings:
            emoji = severity_emoji.get(finding["severity"], "⚪")
            lines.append(f"{emoji} [{finding['severity'].upper()}] {finding['title']}")
            if finding["location"]:
                lines.append(f"   Location: {finding['location']}")
            if finding["fix"]:
                # Truncate long fix recommendations
                fix_text = finding["fix"]
                if len(fix_text) > 70:
                    fix_text = fix_text[:67] + "..."
                lines.append(f"   Fix: {fix_text}")
            lines.append("")

    # Show suggested tests
    if xml_tests:
        lines.append("-" * 60)
        lines.append("SUGGESTED TESTS TO ADD")
        lines.append("-" * 60)

        for i, test in enumerate(xml_tests[:5], 1):  # Limit to 5
            lines.append(f"{i}. {test['target']} ({test['type']})")
            if test["description"]:
                desc = test["description"]
                if len(desc) > 55:
                    desc = desc[:52] + "..."
                lines.append(f"   {desc}")
            lines.append("")

        if len(xml_tests) > 5:
            lines.append(f"   ... and {len(xml_tests) - 5} more suggested tests")
            lines.append("")

    # Generated tests breakdown (if no XML data)
    generated_tests = input_data.get("generated_tests", [])
    if generated_tests and not xml_findings:
        lines.append("-" * 60)
        lines.append("GENERATED TESTS BY FILE")
        lines.append("-" * 60)
        for test_file in generated_tests[:10]:  # Limit display
            source = test_file.get("source_file", "unknown")
            test_count = test_file.get("test_count", 0)
            # Shorten path for display
            if len(source) > 50:
                source = "..." + source[-47:]
            lines.append(f"  📁 {source}")
            lines.append(
                f"     └─ {test_count} test(s) → {test_file.get('test_file', 'test_*.py')}"
            )
        if len(generated_tests) > 10:
            lines.append(f"  ... and {len(generated_tests) - 10} more files")
        lines.append("")

    # Written files section
    written_files = input_data.get("written_files", [])
    if written_files:
        lines.append("-" * 60)
        lines.append("TESTS WRITTEN TO DISK")
        lines.append("-" * 60)
        for file_path in written_files[:10]:
            # Shorten path for display
            if len(file_path) > 55:
                file_path = "..." + file_path[-52:]
            lines.append(f"  ✅ {file_path}")
        if len(written_files) > 10:
            lines.append(f"  ... and {len(written_files) - 10} more files")
        lines.append("")
        lines.append("  Run: pytest <file> to execute these tests")
        lines.append("")
    elif input_data.get("tests_written") is False and total_tests > 0:
        lines.append("-" * 60)
        lines.append("GENERATED TESTS (NOT WRITTEN)")
        lines.append("-" * 60)
        lines.append("  ⚠️  Tests were generated but not written to disk.")
        lines.append("  To write tests, run with: write_tests=True")
        lines.append("")

    # Recommendations
    lines.append("-" * 60)
    lines.append("NEXT STEPS")
    lines.append("-" * 60)

    high_findings = len([f for f in xml_findings if f["severity"] == "high"])
    medium_findings = len([f for f in xml_findings if f["severity"] == "medium"])

    if high_findings > 0:
        lines.append(f"  🔴 Address {high_findings} high-priority finding(s) first")

    if medium_findings > 0:
        lines.append(f"  🟠 Review {medium_findings} medium-priority finding(s)")

    if xml_tests:
        lines.append(f"  📝 Consider adding {len(xml_tests)} suggested test(s)")

    if hotspot_count > 0:
        lines.append(f"  🔥 {hotspot_count} bug hotspot file(s) need priority testing")

    if untested_count > 0:
        lines.append(f"  📁 {untested_count} file(s) have no existing tests")

    if not any([high_findings, medium_findings, xml_tests, hotspot_count, untested_count]):
        lines.append("  ✅ Test suite is in good shape!")

    lines.append("")

    # Footer
    lines.append("=" * 60)
    model_tier = result.get("model_tier_used", "unknown")
    lines.append(f"Review completed using {model_tier} tier model")
    lines.append("=" * 60)

    return "\n".join(lines)


def main():
    """CLI entry point for test generation workflow."""
    import asyncio

    async def run():
        workflow = TestGenerationWorkflow()
        result = await workflow.execute(path=".", file_types=[".py"])

        print("\nTest Generation Results")
        print("=" * 50)
        print(f"Provider: {result.provider}")
        print(f"Success: {result.success}")
        print(f"Tests Generated: {result.final_output.get('total_tests', 0)}")
        print("\nCost Report:")
        print(f"  Total Cost: ${result.cost_report.total_cost:.4f}")
        savings = result.cost_report.savings
        pct = result.cost_report.savings_percent
        print(f"  Savings: ${savings:.4f} ({pct:.1f}%)")

    asyncio.run(run())


if __name__ == "__main__":
    main()
