"""Test Suggester for Enhanced Testing Wizard

Generates smart test suggestions based on code analysis and coverage gaps.
Uses pattern recognition to suggest high-value tests.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import ast
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class TestPriority(Enum):
    """Priority levels for test suggestions"""

    CRITICAL = "critical"  # Untested critical paths
    HIGH = "high"  # Important functionality
    MEDIUM = "medium"  # Standard coverage
    LOW = "low"  # Nice to have


@dataclass
class TestSuggestion:
    """A suggested test to write"""

    target_file: str
    target_function: str
    target_line: int
    test_type: str  # "unit", "integration", "edge_case", "error_handling"
    priority: TestPriority
    suggestion: str  # Human-readable description
    template: str  # Code template
    reasoning: str  # Why this test is important
    estimated_impact: float  # Impact on coverage (0-100)


@dataclass
class CodeElement:
    """Represents a code element that needs testing"""

    name: str
    type: str  # "function", "class", "method"
    file_path: str
    line_number: int
    is_public: bool
    complexity: int  # Cyclomatic complexity estimate
    has_error_handling: bool
    parameters: list[str]
    return_type: str | None


class TestSuggester:
    """Analyzes code to suggest high-value tests.

    Uses static analysis to:
    - Identify untested functions
    - Detect edge cases
    - Find error handling paths
    - Suggest integration tests
    """

    def __init__(self):
        self.critical_patterns = [
            "parse",
            "validate",
            "authenticate",
            "authorize",
            "save",
            "delete",
            "update",
            "create",
            "execute",
            "run",
            "process",
        ]

    def analyze_file(self, file_path: Path) -> list[CodeElement]:
        """Analyze a Python file to extract testable elements

        Args:
            file_path: Path to Python file

        Returns:
            List of CodeElement objects

        Raises:
            FileNotFoundError: If file doesn't exist
            SyntaxError: If file has syntax errors

        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError as e:
            raise SyntaxError(f"Syntax error in {file_path}: {e}") from e

        return self._extract_code_elements(tree, str(file_path))

    def _extract_code_elements(self, tree: ast.AST, file_path: str) -> list[CodeElement]:
        """Extract testable code elements from AST"""
        elements = []

        for node in ast.walk(tree):
            # Extract functions
            if isinstance(node, ast.FunctionDef):
                element = self._analyze_function(node, file_path)
                elements.append(element)

            # Extract class methods
            elif isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        element = self._analyze_method(item, node.name, file_path)
                        elements.append(element)

        return elements

    def _analyze_function(self, node: ast.FunctionDef, file_path: str) -> CodeElement:
        """Analyze a function node"""
        # Check if public (not starting with _)
        is_public = not node.name.startswith("_")

        # Extract parameters
        parameters = [arg.arg for arg in node.args.args]

        # Estimate complexity (simple heuristic)
        complexity = self._estimate_complexity(node)

        # Check for error handling
        has_error_handling = self._has_error_handling(node)

        # Extract return type
        return_type = None
        if node.returns:
            return_type = ast.unparse(node.returns)

        return CodeElement(
            name=node.name,
            type="function",
            file_path=file_path,
            line_number=node.lineno,
            is_public=is_public,
            complexity=complexity,
            has_error_handling=has_error_handling,
            parameters=parameters,
            return_type=return_type,
        )

    def _analyze_method(
        self,
        node: ast.FunctionDef,
        class_name: str,
        file_path: str,
    ) -> CodeElement:
        """Analyze a class method"""
        element = self._analyze_function(node, file_path)
        element.name = f"{class_name}.{node.name}"
        element.type = "method"
        return element

    def _estimate_complexity(self, node: ast.FunctionDef) -> int:
        """Estimate cyclomatic complexity

        Counts decision points: if, for, while, and, or, except
        """
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, ast.If | ast.For | ast.While | ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Count 'and'/'or' operations
                complexity += len(child.values) - 1

        return complexity

    def _has_error_handling(self, node: ast.FunctionDef) -> bool:
        """Check if function has try/except blocks"""
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False

    def suggest_tests(
        self,
        code_elements: list[CodeElement],
        covered_lines: set[int],
    ) -> list[TestSuggestion]:
        """Generate test suggestions for code elements

        Args:
            code_elements: List of code elements from analysis
            covered_lines: Set of line numbers already covered by tests

        Returns:
            List of TestSuggestion objects, sorted by priority

        """
        suggestions = []

        for element in code_elements:
            # Skip private elements unless they're complex
            if not element.is_public and element.complexity < 3:
                continue

            # Check if already tested
            is_covered = element.line_number in covered_lines

            # Generate suggestions based on element characteristics
            element_suggestions = self._generate_element_suggestions(element, is_covered)

            suggestions.extend(element_suggestions)

        # Sort by priority and impact
        suggestions.sort(key=lambda s: (s.priority.value, -s.estimated_impact))

        return suggestions

    def _generate_element_suggestions(
        self,
        element: CodeElement,
        is_covered: bool,
    ) -> list[TestSuggestion]:
        """Generate suggestions for a single code element"""
        suggestions = []

        # Determine base priority
        base_priority = self._determine_priority(element, is_covered)

        # 1. Basic functionality test
        if not is_covered:
            suggestions.append(self._suggest_basic_test(element, base_priority))

        # 2. Edge case tests
        if element.complexity > 2:
            suggestions.append(self._suggest_edge_case_tests(element, base_priority))

        # 3. Error handling tests
        if element.has_error_handling or self._should_have_error_handling(element):
            suggestions.append(self._suggest_error_test(element, base_priority))

        # 4. Parameter validation tests
        if len(element.parameters) > 0:
            suggestions.append(self._suggest_parameter_tests(element, base_priority))

        return suggestions

    def _determine_priority(self, element: CodeElement, is_covered: bool) -> TestPriority:
        """Determine test priority based on element characteristics"""
        # Critical if untested and matches critical patterns
        if not is_covered:
            for pattern in self.critical_patterns:
                if pattern in element.name.lower():
                    return TestPriority.CRITICAL

        # High priority if complex or has error handling
        if element.complexity > 5 or element.has_error_handling:
            return TestPriority.HIGH if not is_covered else TestPriority.MEDIUM

        # Medium priority if public
        if element.is_public:
            return TestPriority.MEDIUM if not is_covered else TestPriority.LOW

        return TestPriority.LOW

    def _should_have_error_handling(self, element: CodeElement) -> bool:
        """Determine if element should have error handling"""
        # Functions that interact with external systems
        error_prone_patterns = [
            "parse",
            "load",
            "save",
            "fetch",
            "request",
            "connect",
            "execute",
            "validate",
            "convert",
        ]

        return any(pattern in element.name.lower() for pattern in error_prone_patterns)

    def _suggest_basic_test(self, element: CodeElement, priority: TestPriority) -> TestSuggestion:
        """Generate basic functionality test suggestion"""
        # Generate test template
        template = self._generate_basic_template(element)

        # Calculate impact (uncovered function = high impact)
        impact = 50.0 if element.is_public else 30.0

        return TestSuggestion(
            target_file=element.file_path,
            target_function=element.name,
            target_line=element.line_number,
            test_type="unit",
            priority=priority,
            suggestion=f"Test basic functionality of {element.name}",
            template=template,
            reasoning=f"Function {element.name} is currently untested",
            estimated_impact=impact,
        )

    def _suggest_edge_case_tests(
        self,
        element: CodeElement,
        priority: TestPriority,
    ) -> TestSuggestion:
        """Generate edge case test suggestions"""
        edge_cases = self._identify_edge_cases(element)

        template = self._generate_edge_case_template(element, edge_cases)

        return TestSuggestion(
            target_file=element.file_path,
            target_function=element.name,
            target_line=element.line_number,
            test_type="edge_case",
            priority=priority,
            suggestion=f"Test edge cases: {', '.join(edge_cases)}",
            template=template,
            reasoning=f"Complex function (complexity {element.complexity}) needs edge case coverage",
            estimated_impact=25.0,
        )

    def _suggest_error_test(self, element: CodeElement, priority: TestPriority) -> TestSuggestion:
        """Generate error handling test suggestion"""
        template = self._generate_error_template(element)

        return TestSuggestion(
            target_file=element.file_path,
            target_function=element.name,
            target_line=element.line_number,
            test_type="error_handling",
            priority=priority,
            suggestion=f"Test error handling for {element.name}",
            template=template,
            reasoning="Function should handle errors gracefully",
            estimated_impact=20.0,
        )

    def _suggest_parameter_tests(
        self,
        element: CodeElement,
        priority: TestPriority,
    ) -> TestSuggestion:
        """Generate parameter validation test suggestion"""
        template = self._generate_parameter_template(element)

        return TestSuggestion(
            target_file=element.file_path,
            target_function=element.name,
            target_line=element.line_number,
            test_type="unit",
            priority=priority,
            suggestion="Test with various parameter combinations",
            template=template,
            reasoning=f"Function takes {len(element.parameters)} parameters - test combinations",
            estimated_impact=15.0,
        )

    def _identify_edge_cases(self, element: CodeElement) -> list[str]:
        """Identify likely edge cases based on function name and parameters"""
        edge_cases = []

        name_lower = element.name.lower()

        # List/collection operations
        if any(word in name_lower for word in ["list", "array", "collection"]):
            edge_cases.extend(["empty list", "single item", "large list"])

        # String operations
        if any(word in name_lower for word in ["string", "text", "name"]):
            edge_cases.extend(["empty string", "unicode", "very long string"])

        # Numeric operations
        if any(word in name_lower for word in ["count", "size", "number", "calculate"]):
            edge_cases.extend(["zero", "negative", "very large number"])

        # File/path operations
        if any(word in name_lower for word in ["file", "path", "directory"]):
            edge_cases.extend(["nonexistent path", "invalid path", "permissions"])

        # Default edge cases
        if not edge_cases:
            edge_cases = ["None input", "invalid type", "boundary values"]

        return edge_cases[:3]  # Limit to top 3

    def _generate_basic_template(self, element: CodeElement) -> str:
        """Generate basic test template"""
        func_name = element.name.split(".")[-1]  # Get last part for methods
        test_name = f"test_{func_name}_basic"

        # Generate parameter examples
        params = []
        for param in element.parameters:
            if param in ["self", "cls"]:
                continue
            params.append(f"{param}=...")  # Placeholder

        param_str = ", ".join(params) if params else ""

        template = f"""
def {test_name}():
    '''Test basic functionality of {element.name}'''
    # Arrange
    {param_str}

    # Act
    result = {element.name}({param_str})

    # Assert
    assert result is not None
    # TODO: Add specific assertions
"""
        return template.strip()

    def _generate_edge_case_template(self, element: CodeElement, edge_cases: list[str]) -> str:
        """Generate edge case test template"""
        func_name = element.name.split(".")[-1]
        test_name = f"test_{func_name}_edge_cases"

        cases_str = "\n    # - ".join(edge_cases)

        template = f"""
def {test_name}():
    '''Test edge cases for {element.name}'''
    # Edge cases to test:
    # - {cases_str}

    # Test case 1: {edge_cases[0]}
    # TODO: Implement test

    # Test case 2: {edge_cases[1] if len(edge_cases) > 1 else "Add more"}
    # TODO: Implement test
"""
        return template.strip()

    def _generate_error_template(self, element: CodeElement) -> str:
        """Generate error handling test template"""
        func_name = element.name.split(".")[-1]
        test_name = f"test_{func_name}_error_handling"

        template = f"""
def {test_name}():
    '''Test error handling for {element.name}'''
    # Test invalid input
    with pytest.raises(ValueError):
        {element.name}(invalid_input)

    # Test None input
    with pytest.raises(TypeError):
        {element.name}(None)

    # TODO: Add more error cases
"""
        return template.strip()

    def _generate_parameter_template(self, element: CodeElement) -> str:
        """Generate parameter validation test template"""
        func_name = element.name.split(".")[-1]
        test_name = f"test_{func_name}_parameters"

        params_str = ", ".join(p for p in element.parameters if p not in ["self", "cls"])

        template = f"""
@pytest.mark.parametrize("{params_str}", [
    # Add test cases here
    # Example: (value1, value2, expected_result)
])
def {test_name}({params_str}):
    '''Test {element.name} with various parameter combinations'''
    result = {element.name}({params_str})
    # TODO: Add assertions
"""
        return template.strip()

    def generate_summary(self, suggestions: list[TestSuggestion]) -> str:
        """Generate human-readable suggestions summary"""
        if not suggestions:
            return "No test suggestions - coverage looks good!"

        summary = []
        summary.append("=" * 60)
        summary.append("TEST SUGGESTIONS")
        summary.append("=" * 60)

        # Group by priority
        by_priority: dict[TestPriority, list[TestSuggestion]] = {
            TestPriority.CRITICAL: [],
            TestPriority.HIGH: [],
            TestPriority.MEDIUM: [],
            TestPriority.LOW: [],
        }

        for suggestion in suggestions:
            by_priority[suggestion.priority].append(suggestion)

        # Display by priority
        for priority in [TestPriority.CRITICAL, TestPriority.HIGH, TestPriority.MEDIUM]:
            suggestions_list = by_priority[priority]
            if not suggestions_list:
                continue

            icon = {"critical": "🔴", "high": "🟡", "medium": "🔵"}
            summary.append(f"\n{icon[priority.value]} {priority.value.upper()} Priority:")

            for i, sug in enumerate(suggestions_list[:5], 1):
                summary.append(f"\n{i}. {sug.suggestion}")
                summary.append(f"   File: {sug.target_file}:{sug.target_line}")
                summary.append(f"   Type: {sug.test_type}")
                summary.append(f"   Impact: +{sug.estimated_impact:.1f}% coverage")
                summary.append(f"   Reason: {sug.reasoning}")

            if len(suggestions_list) > 5:
                summary.append(f"\n   ... and {len(suggestions_list) - 5} more")

        summary.append("\n" + "=" * 60)
        summary.append(f"Total Suggestions: {len(suggestions)}")
        summary.append(f"  Critical: {len(by_priority[TestPriority.CRITICAL])}")
        summary.append(f"  High: {len(by_priority[TestPriority.HIGH])}")
        summary.append(f"  Medium: {len(by_priority[TestPriority.MEDIUM])}")
        summary.append("=" * 60)

        return "\n".join(summary)
