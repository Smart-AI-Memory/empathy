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


class ASTFunctionAnalyzer(ast.NodeVisitor):
    """
    AST-based function analyzer for accurate test generation.

    Extracts:
    - Function signatures with types
    - Exception types raised
    - Side effects detection
    - Complexity estimation
    """

    def __init__(self):
        self.functions: list[FunctionSignature] = []
        self.classes: list[ClassSignature] = []
        self._current_class: str | None = None

    def analyze(self, code: str) -> tuple[list[FunctionSignature], list[ClassSignature]]:
        """Analyze code and extract function/class signatures."""
        try:
            tree = ast.parse(code)
            self.functions = []
            self.classes = []
            self.visit(tree)
            return self.functions, self.classes
        except SyntaxError:
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

        self.classes.append(
            ClassSignature(
                name=node.name,
                methods=methods,
                init_params=init_params,
                base_classes=base_classes,
                docstring=ast.get_docstring(node),
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
        **kwargs: Any,
    ):
        """
        Initialize test generation workflow.

        Args:
            patterns_dir: Directory containing learned patterns
            min_tests_for_review: Minimum tests generated to trigger premium review
            **kwargs: Additional arguments passed to BaseWorkflow
        """
        super().__init__(**kwargs)
        self.patterns_dir = patterns_dir
        self.min_tests_for_review = min_tests_for_review
        self._test_count: int = 0
        self._bug_hotspots: list[str] = []
        self._load_bug_hotspots()

    def _load_bug_hotspots(self) -> None:
        """Load files with historical bugs from pattern library."""
        debugging_file = Path(self.patterns_dir) / "debugging.json"
        if debugging_file.exists():
            try:
                with open(debugging_file) as f:
                    data = json.load(f)
                    patterns = data.get("patterns", [])
                    # Extract files from bug patterns
                    files = set()
                    for p in patterns:
                        for f in p.get("files_affected", []):
                            files.add(f)
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
        """
        target_path = input_data.get("path", ".")
        file_types = input_data.get("file_types", [".py"])

        target = Path(target_path)
        candidates: list[dict] = []

        # Track project scope for enterprise reporting
        total_source_files = 0
        existing_test_files = 0

        if target.exists():
            for ext in file_types:
                for file_path in target.rglob(f"*{ext}"):
                    # Skip non-code directories
                    if any(
                        skip in str(file_path)
                        for skip in [".git", "node_modules", "__pycache__", "venv"]
                    ):
                        continue

                    # Count test files separately for scope awareness
                    file_str = str(file_path)
                    if "test_" in file_str or "_test." in file_str or "/tests/" in file_str:
                        existing_test_files += 1
                        continue

                    # Count source files
                    total_source_files += 1

                    try:
                        content = file_path.read_text(errors="ignore")
                        lines = len(content.splitlines())

                        # Check if in bug hotspots
                        is_hotspot = any(
                            hotspot in str(file_path) for hotspot in self._bug_hotspots
                        )

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

                        if priority > 0:
                            candidates.append(
                                {
                                    "file": str(file_path),
                                    "lines": lines,
                                    "is_hotspot": is_hotspot,
                                    "has_tests": has_tests,
                                    "priority": priority,
                                }
                            )
                    except OSError:
                        continue

        # Sort by priority
        candidates.sort(key=lambda x: -x["priority"])

        input_tokens = len(str(input_data)) // 4
        output_tokens = len(str(candidates)) // 4

        # Calculate scope metrics for enterprise reporting
        analyzed_count = min(30, len(candidates))
        coverage_pct = (analyzed_count / len(candidates) * 100) if candidates else 100

        return (
            {
                "candidates": candidates[:30],  # Top 30
                "total_candidates": len(candidates),
                "hotspot_count": len([c for c in candidates if c["is_hotspot"]]),
                "untested_count": len([c for c in candidates if not c["has_tests"]]),
                # Scope awareness fields for enterprise reporting
                "total_source_files": total_source_files,
                "existing_test_files": existing_test_files,
                "large_project_warning": len(candidates) > 100,
                "analysis_coverage_percent": coverage_pct,
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
        """
        candidates = input_data.get("candidates", [])[:15]  # Top 15
        analysis: list[dict] = []

        for candidate in candidates:
            file_path = Path(candidate["file"])
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text(errors="ignore")

                # Extract testable items (simplified analysis)
                functions = self._extract_functions(content)
                classes = self._extract_classes(content)

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
                **input_data,
            },
            input_tokens,
            output_tokens,
        )

    def _extract_functions(self, content: str) -> list[dict]:
        """Extract function definitions from Python code using AST analysis."""
        analyzer = ASTFunctionAnalyzer()
        functions, _ = analyzer.analyze(content)

        result = []
        for sig in functions[:20]:  # Limit
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
        return result

    def _extract_classes(self, content: str) -> list[dict]:
        """Extract class definitions from Python code using AST analysis."""
        analyzer = ASTFunctionAnalyzer()
        _, classes = analyzer.analyze(content)

        result = []
        for sig in classes[:10]:  # Limit
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
                }
            )
        return result

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
        """
        analysis = input_data.get("analysis", [])
        generated_tests: list[dict] = []

        for item in analysis[:10]:  # Top 10 files
            file_path = item["file"]
            module_name = Path(file_path).stem

            tests = []
            for func in item.get("functions", [])[:5]:
                test_code = self._generate_test_for_function(module_name, func)
                tests.append(
                    {
                        "target": func["name"],
                        "type": "function",
                        "code": test_code,
                    }
                )

            for cls in item.get("classes", [])[:2]:
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

        input_tokens = len(str(input_data)) // 4
        output_tokens = sum(len(str(t)) for t in generated_tests) // 4

        return (
            {
                "generated_tests": generated_tests,
                "total_tests_generated": self._test_count,
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

    def _generate_test_for_class(self, module: str, cls: dict) -> str:
        """Generate executable test class based on AST analysis."""
        name = cls["name"]
        init_params = cls.get("init_params", [])
        methods = cls.get("methods", [])
        _docstring = cls.get("docstring", "")  # Reserved for future use  # noqa: F841

        # Generate constructor arguments
        init_args = self._generate_test_cases_for_params(init_params)
        init_arg_str = ", ".join(init_args.get("valid_args", []))

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

        # Test with parametrized init args if we have multiple cases
        if init_params and len(init_args.get("parametrize_cases", [])) > 1:
            param_names = [p[0] for p in init_params]
            param_names_str = ", ".join(param_names)
            cases = init_args.get("parametrize_cases", [])[:3]
            cases_str = ",\n        ".join(cases)
            tests.append(
                f'''
    @pytest.mark.parametrize("{param_names_str}", [
        {cases_str},
    ])
    def test_initialization_with_various_args(self, {param_names_str}):
        """Test {name} initialization with various arguments."""
        instance = {name}({param_names_str})
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
        for test_item in generated_tests:
            test_context += f"  <file path=\"{test_item['source_file']}\">\n"
            for test in test_item["tests"]:
                # Extract test name from code for the report
                test_name = "unnamed"
                try:
                    match = re.search(r"def\s+(test_\w+)", test["code"])
                    if match:
                        test_name = match.group(1)
                except Exception:
                    pass
                test_context += f"    <test name=\"{test_name}\" target=\"{test['target']}\" />\n"
            test_context += "  </file>\n"
        test_context += "</generated_tests>\n"

        # Build the system prompt directly for the review stage
        target_files = [item["source_file"] for item in generated_tests]
        file_list = "\n".join(f"  - {f}" for f in target_files)

        system_prompt = f"""You are an expert test engineer specializing in Python test coverage analysis.

Your task is to review the generated test structure and produce a comprehensive test gap analysis report.

Target files ({len(generated_tests)}):
{file_list}

Provide a detailed analysis including:
1. Summary of tests generated
2. Coverage assessment
3. Any identified gaps or missing edge cases
4. Recommendations for additional tests

Format your response as a clear, structured report."""

        user_message = f"Please generate a test gap analysis report based on the following test structure:\n{test_context}"

        # Call the LLM using the provider-agnostic executor from BaseWorkflow
        step_config = TEST_GEN_STEPS["review"]
        report, in_tokens, out_tokens, _cost = await self.run_step_with_executor(
            step=step_config,
            prompt=user_message,
            system=system_prompt,
        )

        # Replace the previous analysis with the final, accurate report
        input_data["analysis_report"] = report
        return input_data, in_tokens, out_tokens

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
