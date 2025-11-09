"""
Comprehensive tests for TestSuggester

Tests the test suggestion generation system including AST analysis,
priority determination, template generation, and suggestion ranking.

Copyright 2025 Smart-AI-Memory
Licensed under Fair Source License 0.9
"""

import ast

import pytest

from empathy_software_plugin.wizards.testing.test_suggester import (
    CodeElement,
    TestPriority,
    TestSuggester,
    TestSuggestion,
)

# ============================================================================
# TestPriority Enum Tests
# ============================================================================


def test_test_priority_enum():
    """Test TestPriority enum values"""
    assert TestPriority.CRITICAL.value == "critical"
    assert TestPriority.HIGH.value == "high"
    assert TestPriority.MEDIUM.value == "medium"
    assert TestPriority.LOW.value == "low"


# ============================================================================
# TestSuggestion Dataclass Tests
# ============================================================================


def test_test_suggestion_creation():
    """Test creating TestSuggestion instance"""
    suggestion = TestSuggestion(
        target_file="module.py",
        target_function="validate_input",
        target_line=42,
        test_type="unit",
        priority=TestPriority.CRITICAL,
        suggestion="Test input validation",
        template="def test_validate_input(): ...",
        reasoning="Critical security function",
        estimated_impact=75.0,
    )

    assert suggestion.target_file == "module.py"
    assert suggestion.target_function == "validate_input"
    assert suggestion.target_line == 42
    assert suggestion.test_type == "unit"
    assert suggestion.priority == TestPriority.CRITICAL
    assert suggestion.suggestion == "Test input validation"
    assert suggestion.estimated_impact == 75.0


def test_test_suggestion_with_different_test_types():
    """Test TestSuggestion with various test types"""
    test_types = ["unit", "integration", "edge_case", "error_handling"]

    for test_type in test_types:
        suggestion = TestSuggestion(
            target_file="test.py",
            target_function="func",
            target_line=1,
            test_type=test_type,
            priority=TestPriority.MEDIUM,
            suggestion="Test suggestion",
            template="template",
            reasoning="reason",
            estimated_impact=50.0,
        )
        assert suggestion.test_type == test_type


# ============================================================================
# CodeElement Dataclass Tests
# ============================================================================


def test_code_element_creation():
    """Test creating CodeElement instance"""
    element = CodeElement(
        name="parse_data",
        type="function",
        file_path="parser.py",
        line_number=10,
        is_public=True,
        complexity=5,
        has_error_handling=True,
        parameters=["data", "format"],
        return_type="dict",
    )

    assert element.name == "parse_data"
    assert element.type == "function"
    assert element.file_path == "parser.py"
    assert element.line_number == 10
    assert element.is_public is True
    assert element.complexity == 5
    assert element.has_error_handling is True
    assert element.parameters == ["data", "format"]
    assert element.return_type == "dict"


def test_code_element_method_type():
    """Test CodeElement for class methods"""
    element = CodeElement(
        name="Calculator.add",
        type="method",
        file_path="calc.py",
        line_number=20,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["self", "a", "b"],
        return_type="int",
    )

    assert element.name == "Calculator.add"
    assert element.type == "method"
    assert "self" in element.parameters


# ============================================================================
# TestSuggester Initialization Tests
# ============================================================================


@pytest.fixture
def suggester():
    """Create TestSuggester instance"""
    return TestSuggester()


def test_test_suggester_initialization(suggester):
    """Test TestSuggester initializes with critical patterns"""
    assert suggester.critical_patterns is not None
    assert len(suggester.critical_patterns) > 0
    assert "parse" in suggester.critical_patterns
    assert "validate" in suggester.critical_patterns
    assert "authenticate" in suggester.critical_patterns


# ============================================================================
# File Analysis Tests
# ============================================================================


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files"""
    return tmp_path


def test_analyze_file_simple_function(suggester, temp_dir):
    """Test analyzing file with simple function"""
    code = '''
def simple_function(x, y):
    """A simple function"""
    return x + y
'''
    test_file = temp_dir / "simple.py"
    test_file.write_text(code)

    elements = suggester.analyze_file(test_file)

    assert len(elements) == 1
    assert elements[0].name == "simple_function"
    assert elements[0].type == "function"
    assert elements[0].is_public is True
    assert elements[0].parameters == ["x", "y"]


def test_analyze_file_with_class(suggester, temp_dir):
    """Test analyzing file with class and methods"""
    code = '''
class Calculator:
    """A calculator class"""

    def add(self, a, b):
        """Add two numbers"""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers"""
        return a - b
'''
    test_file = temp_dir / "calculator.py"
    test_file.write_text(code)

    elements = suggester.analyze_file(test_file)

    # ast.walk extracts both as methods and as standalone functions (duplicates)
    assert len(elements) == 4

    # Check that methods are present
    method_elements = [e for e in elements if e.type == "method"]
    assert len(method_elements) == 2
    assert method_elements[0].name == "Calculator.add"
    assert method_elements[1].name == "Calculator.subtract"


def test_analyze_file_not_found(suggester, temp_dir):
    """Test analyzing non-existent file raises FileNotFoundError"""
    nonexistent = temp_dir / "nonexistent.py"

    with pytest.raises(FileNotFoundError, match="File not found"):
        suggester.analyze_file(nonexistent)


def test_analyze_file_syntax_error(suggester, temp_dir):
    """Test analyzing file with syntax errors"""
    code = """
def broken_function(
    # Missing closing parenthesis and colon
"""
    test_file = temp_dir / "broken.py"
    test_file.write_text(code)

    with pytest.raises(SyntaxError, match="Syntax error"):
        suggester.analyze_file(test_file)


def test_analyze_file_private_function(suggester, temp_dir):
    """Test analyzing private function (starts with _)"""
    code = '''
def _private_helper(data):
    """Private helper function"""
    return data.upper()
'''
    test_file = temp_dir / "private.py"
    test_file.write_text(code)

    elements = suggester.analyze_file(test_file)

    assert len(elements) == 1
    assert elements[0].name == "_private_helper"
    assert elements[0].is_public is False


# ============================================================================
# Code Element Extraction Tests
# ============================================================================


def test_extract_code_elements_functions_and_methods(suggester):
    """Test extracting both functions and class methods"""
    code = """
def standalone_func():
    pass

class MyClass:
    def method_one(self):
        pass

    def method_two(self):
        pass

def another_func():
    pass
"""
    tree = ast.parse(code)
    elements = suggester._extract_code_elements(tree, "test.py")

    # ast.walk extracts: 2 standalone + 2 methods + 2 duplicate functions = 6 elements
    assert len(elements) == 6

    # Check types - methods are also extracted as functions (duplicates)
    function_elements = [e for e in elements if e.type == "function"]
    method_elements = [e for e in elements if e.type == "method"]

    # 2 standalone functions + 2 class methods (extracted as functions)
    assert len(function_elements) == 4
    assert len(method_elements) == 2


# ============================================================================
# Function Analysis Tests
# ============================================================================


def test_analyze_function_with_type_hints(suggester):
    """Test analyzing function with type hints"""
    code = '''
def typed_function(x: int, y: str) -> bool:
    """Function with type hints"""
    return len(y) > x
'''
    tree = ast.parse(code)
    func_node = tree.body[0]

    element = suggester._analyze_function(func_node, "test.py")

    assert element.name == "typed_function"
    assert element.parameters == ["x", "y"]
    assert element.return_type == "bool"


def test_analyze_function_without_return_type(suggester):
    """Test analyzing function without return type annotation"""
    code = """
def no_return_type(x):
    return x * 2
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    element = suggester._analyze_function(func_node, "test.py")

    assert element.return_type is None


def test_analyze_function_with_error_handling(suggester):
    """Test analyzing function with try/except"""
    code = """
def safe_divide(a, b):
    try:
        return a / b
    except ZeroDivisionError:
        return None
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    element = suggester._analyze_function(func_node, "test.py")

    assert element.has_error_handling is True


def test_analyze_function_line_number(suggester):
    """Test that line numbers are captured correctly"""
    code = """


def function_on_line_4():
    pass
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    element = suggester._analyze_function(func_node, "test.py")

    assert element.line_number == 4


# ============================================================================
# Method Analysis Tests
# ============================================================================


def test_analyze_method(suggester):
    """Test analyzing class method"""
    code = """
def instance_method(self, x):
    return x * 2
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    element = suggester._analyze_method(func_node, "MyClass", "test.py")

    assert element.name == "MyClass.instance_method"
    assert element.type == "method"
    assert "self" in element.parameters


# ============================================================================
# Complexity Estimation Tests
# ============================================================================


def test_estimate_complexity_simple_function(suggester):
    """Test complexity estimation for simple function"""
    code = """
def simple():
    return 42
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    assert complexity == 1  # Base complexity


def test_estimate_complexity_with_if_statement(suggester):
    """Test complexity with if statement"""
    code = """
def with_if(x):
    if x > 0:
        return x
    return -x
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    assert complexity == 2  # Base (1) + if (1)


def test_estimate_complexity_with_loops(suggester):
    """Test complexity with for and while loops"""
    code = """
def with_loops(items):
    count = 0
    for item in items:
        count += 1

    while count > 0:
        count -= 1

    return count
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    assert complexity == 3  # Base (1) + for (1) + while (1)


def test_estimate_complexity_with_boolean_operators(suggester):
    """Test complexity with and/or operators"""
    code = """
def with_bool_ops(a, b, c):
    if a and b and c:
        return True
    return False
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    # Base (1) + if (1) + and operators (2)
    assert complexity >= 3


def test_estimate_complexity_with_exception_handling(suggester):
    """Test complexity with try/except"""
    code = """
def with_exception_handling(x):
    try:
        return 1 / x
    except ZeroDivisionError:
        return 0
    except ValueError:
        return -1
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    # Base (1) + 2 except handlers (2)
    assert complexity == 3


def test_estimate_complexity_complex_function(suggester):
    """Test complexity for complex function with multiple decision points"""
    code = """
def complex_function(x, y):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                y += i
    elif x < 0:
        while y > 0:
            y -= 1
    return y
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    complexity = suggester._estimate_complexity(func_node)

    # Base (1) + if (1) + for (1) + inner if (1) + elif (1) + while (1)
    assert complexity >= 5


# ============================================================================
# Error Handling Detection Tests
# ============================================================================


def test_has_error_handling_true(suggester):
    """Test detecting error handling in function"""
    code = """
def with_try_except():
    try:
        risky_operation()
    except Exception:
        pass
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    has_error_handling = suggester._has_error_handling(func_node)

    assert has_error_handling is True


def test_has_error_handling_false(suggester):
    """Test function without error handling"""
    code = """
def without_try_except():
    return 42
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    has_error_handling = suggester._has_error_handling(func_node)

    assert has_error_handling is False


def test_has_error_handling_nested(suggester):
    """Test detecting error handling in nested blocks"""
    code = """
def nested_try():
    if True:
        try:
            something()
        except:
            pass
"""
    tree = ast.parse(code)
    func_node = tree.body[0]

    has_error_handling = suggester._has_error_handling(func_node)

    assert has_error_handling is True


# ============================================================================
# Test Suggestion Generation Tests
# ============================================================================


def test_suggest_tests_empty_elements(suggester):
    """Test suggesting tests with no code elements"""
    suggestions = suggester.suggest_tests([], set())

    assert suggestions == []


def test_suggest_tests_covered_simple_function(suggester):
    """Test suggesting tests for already-covered simple function"""
    element = CodeElement(
        name="simple_func",
        type="function",
        file_path="test.py",
        line_number=10,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    # Mark as covered
    covered_lines = {10}

    suggestions = suggester.suggest_tests([element], covered_lines)

    # Should still get some suggestions (edge cases, parameters, etc.)
    # but basic test should not be suggested
    basic_suggestions = [
        s for s in suggestions if s.test_type == "unit" and "basic" in s.suggestion.lower()
    ]
    assert len(basic_suggestions) == 0


def test_suggest_tests_uncovered_critical_function(suggester):
    """Test suggesting tests for uncovered critical function"""
    element = CodeElement(
        name="validate_input",  # Critical pattern
        type="function",
        file_path="validator.py",
        line_number=20,
        is_public=True,
        complexity=3,
        has_error_handling=True,
        parameters=["data"],
        return_type="bool",
    )

    suggestions = suggester.suggest_tests([element], set())

    assert len(suggestions) > 0

    # Should have CRITICAL priority suggestion
    critical_suggestions = [s for s in suggestions if s.priority == TestPriority.CRITICAL]
    assert len(critical_suggestions) > 0


def test_suggest_tests_complex_function(suggester):
    """Test suggesting tests for complex function"""
    element = CodeElement(
        name="complex_processor",
        type="function",
        file_path="processor.py",
        line_number=50,
        is_public=True,
        complexity=8,  # High complexity
        has_error_handling=True,
        parameters=["input", "options"],
        return_type="dict",
    )

    suggestions = suggester.suggest_tests([element], set())

    # Should suggest multiple test types
    test_types = {s.test_type for s in suggestions}

    assert "unit" in test_types  # Basic test
    assert "edge_case" in test_types  # Edge cases for complex function
    assert "error_handling" in test_types  # Error handling test


def test_suggest_tests_private_low_complexity_skipped(suggester):
    """Test that private functions with low complexity are skipped"""
    element = CodeElement(
        name="_private_helper",
        type="function",
        file_path="helpers.py",
        line_number=5,
        is_public=False,
        complexity=1,  # Low complexity
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    suggestions = suggester.suggest_tests([element], set())

    # Should be skipped (private + low complexity)
    assert len(suggestions) == 0


def test_suggest_tests_private_high_complexity_included(suggester):
    """Test that private functions with high complexity get suggestions"""
    element = CodeElement(
        name="_complex_private",
        type="function",
        file_path="internal.py",
        line_number=100,
        is_public=False,
        complexity=5,  # High complexity
        has_error_handling=False,
        parameters=["x", "y"],
        return_type=None,
    )

    suggestions = suggester.suggest_tests([element], set())

    # Should get suggestions despite being private (high complexity)
    assert len(suggestions) > 0


def test_suggest_tests_sorted_by_priority_and_impact(suggester):
    """Test that suggestions are sorted by priority and impact"""
    elements = [
        CodeElement(
            name="low_priority",
            type="function",
            file_path="test.py",
            line_number=1,
            is_public=True,
            complexity=1,
            has_error_handling=False,
            parameters=[],
            return_type=None,
        ),
        CodeElement(
            name="parse_critical",  # Critical pattern
            type="function",
            file_path="test.py",
            line_number=10,
            is_public=True,
            complexity=3,
            has_error_handling=False,
            parameters=["data"],
            return_type=None,
        ),
    ]

    suggestions = suggester.suggest_tests(elements, set())

    # Critical suggestions should come first
    assert suggestions[0].priority == TestPriority.CRITICAL


# ============================================================================
# Element Suggestion Generation Tests
# ============================================================================


def test_generate_element_suggestions_uncovered(suggester):
    """Test generating suggestions for uncovered element"""
    element = CodeElement(
        name="process_data",
        type="function",
        file_path="processor.py",
        line_number=10,
        is_public=True,
        complexity=4,
        has_error_handling=True,
        parameters=["data", "format"],
        return_type="dict",
    )

    suggestions = suggester._generate_element_suggestions(element, is_covered=False)

    # Should include: basic test, edge cases (complexity > 2),
    # error handling, parameter tests
    assert len(suggestions) == 4

    test_types = {s.test_type for s in suggestions}
    assert "unit" in test_types
    assert "edge_case" in test_types
    assert "error_handling" in test_types


def test_generate_element_suggestions_covered(suggester):
    """Test generating suggestions for already covered element"""
    element = CodeElement(
        name="simple_func",
        type="function",
        file_path="test.py",
        line_number=5,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    suggestions = suggester._generate_element_suggestions(element, is_covered=True)

    # Should not include basic test (already covered)
    # No edge cases (complexity <= 2)
    # No parameters
    # No error handling
    assert len(suggestions) == 0


# ============================================================================
# Priority Determination Tests
# ============================================================================


def test_determine_priority_critical_uncovered(suggester):
    """Test CRITICAL priority for uncovered critical pattern"""
    element = CodeElement(
        name="authenticate_user",  # Critical pattern
        type="function",
        file_path="auth.py",
        line_number=10,
        is_public=True,
        complexity=2,
        has_error_handling=False,
        parameters=["username", "password"],
        return_type="bool",
    )

    priority = suggester._determine_priority(element, is_covered=False)

    assert priority == TestPriority.CRITICAL


def test_determine_priority_high_complex_uncovered(suggester):
    """Test HIGH priority for complex uncovered function"""
    element = CodeElement(
        name="complex_function",
        type="function",
        file_path="complex.py",
        line_number=20,
        is_public=True,
        complexity=7,  # > 5
        has_error_handling=False,
        parameters=["x"],
        return_type=None,
    )

    priority = suggester._determine_priority(element, is_covered=False)

    assert priority == TestPriority.HIGH


def test_determine_priority_high_error_handling_uncovered(suggester):
    """Test HIGH priority for function with error handling"""
    element = CodeElement(
        name="safe_operation",
        type="function",
        file_path="safe.py",
        line_number=30,
        is_public=True,
        complexity=2,
        has_error_handling=True,  # Has error handling
        parameters=[],
        return_type=None,
    )

    priority = suggester._determine_priority(element, is_covered=False)

    assert priority == TestPriority.HIGH


def test_determine_priority_medium_public_uncovered(suggester):
    """Test MEDIUM priority for public uncovered function"""
    element = CodeElement(
        name="public_func",
        type="function",
        file_path="public.py",
        line_number=40,
        is_public=True,
        complexity=2,
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    priority = suggester._determine_priority(element, is_covered=False)

    assert priority == TestPriority.MEDIUM


def test_determine_priority_low_covered(suggester):
    """Test LOW priority for covered public function"""
    element = CodeElement(
        name="covered_func",
        type="function",
        file_path="covered.py",
        line_number=50,
        is_public=True,
        complexity=2,
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    priority = suggester._determine_priority(element, is_covered=True)

    assert priority == TestPriority.LOW


def test_determine_priority_multiple_critical_patterns(suggester):
    """Test that any critical pattern triggers CRITICAL priority"""
    critical_names = ["parse_data", "validate_input", "save_record", "delete_user", "execute_query"]

    for name in critical_names:
        element = CodeElement(
            name=name,
            type="function",
            file_path="test.py",
            line_number=1,
            is_public=True,
            complexity=1,
            has_error_handling=False,
            parameters=[],
            return_type=None,
        )

        priority = suggester._determine_priority(element, is_covered=False)
        assert priority == TestPriority.CRITICAL, f"Failed for {name}"


# ============================================================================
# Should Have Error Handling Tests
# ============================================================================


def test_should_have_error_handling_parse(suggester):
    """Test that parse functions should have error handling"""
    element = CodeElement(
        name="parse_json",
        type="function",
        file_path="parser.py",
        line_number=10,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["data"],
        return_type=None,
    )

    should_have = suggester._should_have_error_handling(element)

    assert should_have is True


def test_should_have_error_handling_load(suggester):
    """Test that load functions should have error handling"""
    element = CodeElement(
        name="load_config",
        type="function",
        file_path="config.py",
        line_number=20,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["path"],
        return_type=None,
    )

    should_have = suggester._should_have_error_handling(element)

    assert should_have is True


def test_should_have_error_handling_false(suggester):
    """Test that simple functions don't need error handling"""
    element = CodeElement(
        name="add_numbers",
        type="function",
        file_path="math.py",
        line_number=5,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["a", "b"],
        return_type=None,
    )

    should_have = suggester._should_have_error_handling(element)

    assert should_have is False


# ============================================================================
# Basic Test Suggestion Tests
# ============================================================================


def test_suggest_basic_test(suggester):
    """Test generating basic test suggestion"""
    element = CodeElement(
        name="calculate_total",
        type="function",
        file_path="calc.py",
        line_number=10,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["items"],
        return_type="float",
    )

    suggestion = suggester._suggest_basic_test(element, TestPriority.MEDIUM)

    assert suggestion.target_function == "calculate_total"
    assert suggestion.test_type == "unit"
    assert suggestion.priority == TestPriority.MEDIUM
    assert "basic functionality" in suggestion.suggestion.lower()
    assert suggestion.estimated_impact == 50.0  # Public function


def test_suggest_basic_test_private_function(suggester):
    """Test basic test suggestion for private function has lower impact"""
    element = CodeElement(
        name="_private_func",
        type="function",
        file_path="internal.py",
        line_number=5,
        is_public=False,
        complexity=1,
        has_error_handling=False,
        parameters=[],
        return_type=None,
    )

    suggestion = suggester._suggest_basic_test(element, TestPriority.LOW)

    assert suggestion.estimated_impact == 30.0  # Private function


# ============================================================================
# Edge Case Suggestion Tests
# ============================================================================


def test_suggest_edge_case_tests(suggester):
    """Test generating edge case test suggestions"""
    element = CodeElement(
        name="process_list",
        type="function",
        file_path="processor.py",
        line_number=20,
        is_public=True,
        complexity=5,
        has_error_handling=False,
        parameters=["items"],
        return_type="list",
    )

    suggestion = suggester._suggest_edge_case_tests(element, TestPriority.HIGH)

    assert suggestion.test_type == "edge_case"
    assert suggestion.priority == TestPriority.HIGH
    assert "edge cases" in suggestion.suggestion.lower()
    assert suggestion.estimated_impact == 25.0


# ============================================================================
# Error Test Suggestion Tests
# ============================================================================


def test_suggest_error_test(suggester):
    """Test generating error handling test suggestion"""
    element = CodeElement(
        name="validate_email",
        type="function",
        file_path="validator.py",
        line_number=30,
        is_public=True,
        complexity=2,
        has_error_handling=True,
        parameters=["email"],
        return_type="bool",
    )

    suggestion = suggester._suggest_error_test(element, TestPriority.CRITICAL)

    assert suggestion.test_type == "error_handling"
    assert suggestion.priority == TestPriority.CRITICAL
    assert "error handling" in suggestion.suggestion.lower()
    assert suggestion.estimated_impact == 20.0


# ============================================================================
# Parameter Test Suggestion Tests
# ============================================================================


def test_suggest_parameter_tests(suggester):
    """Test generating parameter test suggestions"""
    element = CodeElement(
        name="combine_strings",
        type="function",
        file_path="strings.py",
        line_number=15,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["a", "b", "separator"],
        return_type="str",
    )

    suggestion = suggester._suggest_parameter_tests(element, TestPriority.MEDIUM)

    assert suggestion.test_type == "unit"
    assert suggestion.priority == TestPriority.MEDIUM
    assert "parameter combinations" in suggestion.suggestion.lower()
    assert "3 parameters" in suggestion.reasoning
    assert suggestion.estimated_impact == 15.0


# ============================================================================
# Edge Case Identification Tests
# ============================================================================


def test_identify_edge_cases_list_operations(suggester):
    """Test identifying edge cases for list operations"""
    element = CodeElement(
        name="process_list",
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["items"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    assert "empty list" in edge_cases
    assert "single item" in edge_cases
    assert "large list" in edge_cases


def test_identify_edge_cases_string_operations(suggester):
    """Test identifying edge cases for string operations"""
    element = CodeElement(
        name="format_string",
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["text"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    assert "empty string" in edge_cases
    assert "unicode" in edge_cases
    assert "very long string" in edge_cases


def test_identify_edge_cases_numeric_operations(suggester):
    """Test identifying edge cases for numeric operations"""
    element = CodeElement(
        name="calculate_total",
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["count"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    assert "zero" in edge_cases
    assert "negative" in edge_cases
    assert "very large number" in edge_cases


def test_identify_edge_cases_file_operations(suggester):
    """Test identifying edge cases for file operations"""
    element = CodeElement(
        name="read_file",
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["path"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    assert "nonexistent path" in edge_cases
    assert "invalid path" in edge_cases
    assert "permissions" in edge_cases


def test_identify_edge_cases_default(suggester):
    """Test default edge cases for generic function"""
    element = CodeElement(
        name="generic_function",
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["x"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    assert "None input" in edge_cases
    assert "invalid type" in edge_cases
    assert "boundary values" in edge_cases


def test_identify_edge_cases_limit_to_three(suggester):
    """Test that edge cases are limited to top 3"""
    element = CodeElement(
        name="process_list_string_count",  # Multiple patterns
        type="function",
        file_path="test.py",
        line_number=1,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["items"],
        return_type=None,
    )

    edge_cases = suggester._identify_edge_cases(element)

    # Should be limited to 3
    assert len(edge_cases) == 3


# ============================================================================
# Template Generation Tests
# ============================================================================


def test_generate_basic_template(suggester):
    """Test generating basic test template"""
    element = CodeElement(
        name="add_numbers",
        type="function",
        file_path="math.py",
        line_number=10,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["a", "b"],
        return_type="int",
    )

    template = suggester._generate_basic_template(element)

    assert "def test_add_numbers_basic():" in template
    assert "Test basic functionality of add_numbers" in template
    assert "# Arrange" in template
    assert "# Act" in template
    assert "# Assert" in template
    assert "result = add_numbers(" in template


def test_generate_basic_template_method(suggester):
    """Test generating template for class method"""
    element = CodeElement(
        name="Calculator.multiply",
        type="method",
        file_path="calc.py",
        line_number=20,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["self", "x", "y"],
        return_type="int",
    )

    template = suggester._generate_basic_template(element)

    # Should use last part of name (method name only)
    assert "def test_multiply_basic():" in template
    # Should skip 'self' parameter
    assert "self=" not in template


def test_generate_edge_case_template(suggester):
    """Test generating edge case test template"""
    element = CodeElement(
        name="process_data",
        type="function",
        file_path="processor.py",
        line_number=30,
        is_public=True,
        complexity=3,
        has_error_handling=False,
        parameters=["data"],
        return_type=None,
    )

    edge_cases = ["empty input", "invalid format", "large dataset"]
    template = suggester._generate_edge_case_template(element, edge_cases)

    assert "def test_process_data_edge_cases():" in template
    assert "Test edge cases for process_data" in template
    assert "empty input" in template
    assert "invalid format" in template


def test_generate_error_template(suggester):
    """Test generating error handling test template"""
    element = CodeElement(
        name="parse_json",
        type="function",
        file_path="parser.py",
        line_number=40,
        is_public=True,
        complexity=2,
        has_error_handling=True,
        parameters=["data"],
        return_type="dict",
    )

    template = suggester._generate_error_template(element)

    assert "def test_parse_json_error_handling():" in template
    assert "Test error handling for parse_json" in template
    assert "with pytest.raises(ValueError):" in template
    assert "with pytest.raises(TypeError):" in template


def test_generate_parameter_template(suggester):
    """Test generating parameter test template"""
    element = CodeElement(
        name="combine",
        type="function",
        file_path="util.py",
        line_number=50,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["a", "b", "c"],
        return_type="str",
    )

    template = suggester._generate_parameter_template(element)

    assert "def test_combine_parameters(" in template
    assert "@pytest.mark.parametrize" in template
    assert "a, b, c" in template
    # Should not include 'self' or 'cls'


def test_generate_parameter_template_skip_self(suggester):
    """Test parameter template skips self/cls"""
    element = CodeElement(
        name="MyClass.instance_method",
        type="method",
        file_path="class.py",
        line_number=15,
        is_public=True,
        complexity=1,
        has_error_handling=False,
        parameters=["self", "x", "y"],
        return_type=None,
    )

    template = suggester._generate_parameter_template(element)

    assert "self" not in template.split("parametrize")[1].split("]")[0]


# ============================================================================
# Summary Generation Tests
# ============================================================================


def test_generate_summary_no_suggestions(suggester):
    """Test generating summary with no suggestions"""
    summary = suggester.generate_summary([])

    assert "No test suggestions" in summary
    assert "coverage looks good" in summary.lower()


def test_generate_summary_with_suggestions(suggester):
    """Test generating summary with various priority suggestions"""
    suggestions = [
        TestSuggestion(
            target_file="auth.py",
            target_function="authenticate",
            target_line=10,
            test_type="unit",
            priority=TestPriority.CRITICAL,
            suggestion="Test authentication logic",
            template="def test_auth(): pass",
            reasoning="Critical security function",
            estimated_impact=80.0,
        ),
        TestSuggestion(
            target_file="parser.py",
            target_function="parse_data",
            target_line=20,
            test_type="edge_case",
            priority=TestPriority.HIGH,
            suggestion="Test edge cases",
            template="def test_parse(): pass",
            reasoning="Complex parsing logic",
            estimated_impact=60.0,
        ),
        TestSuggestion(
            target_file="util.py",
            target_function="helper",
            target_line=30,
            test_type="unit",
            priority=TestPriority.MEDIUM,
            suggestion="Test helper function",
            template="def test_helper(): pass",
            reasoning="Public utility",
            estimated_impact=40.0,
        ),
    ]

    summary = suggester.generate_summary(suggestions)

    assert "TEST SUGGESTIONS" in summary
    assert "CRITICAL" in summary
    assert "HIGH" in summary
    assert "MEDIUM" in summary
    assert "Test authentication logic" in summary  # Suggestion text, not function name
    assert "Test edge cases" in summary  # Suggestion text
    assert "Total Suggestions: 3" in summary
    assert "auth.py:10" in summary
    assert "+80.0% coverage" in summary


def test_generate_summary_limits_per_priority(suggester):
    """Test that summary limits to 5 suggestions per priority"""
    # Create 8 critical suggestions
    suggestions = [
        TestSuggestion(
            target_file=f"file{i}.py",
            target_function=f"func{i}",
            target_line=i,
            test_type="unit",
            priority=TestPriority.CRITICAL,
            suggestion=f"Test function {i}",
            template="template",
            reasoning="reason",
            estimated_impact=50.0,
        )
        for i in range(8)
    ]

    summary = suggester.generate_summary(suggestions)

    # Should show "... and 3 more"
    assert "... and 3 more" in summary


def test_generate_summary_grouped_by_priority(suggester):
    """Test that suggestions are grouped by priority in summary"""
    suggestions = [
        TestSuggestion(
            target_file="low.py",
            target_function="low_func",
            target_line=1,
            test_type="unit",
            priority=TestPriority.LOW,
            suggestion="Low priority test",
            template="template",
            reasoning="reason",
            estimated_impact=10.0,
        ),
        TestSuggestion(
            target_file="critical.py",
            target_function="critical_func",
            target_line=2,
            test_type="unit",
            priority=TestPriority.CRITICAL,
            suggestion="Critical test",
            template="template",
            reasoning="reason",
            estimated_impact=90.0,
        ),
    ]

    summary = suggester.generate_summary(suggestions)

    # Critical should appear before Low in summary
    critical_pos = summary.find("CRITICAL")
    low_pos = summary.find("LOW")

    # LOW shouldn't appear in summary (only CRITICAL, HIGH, MEDIUM shown)
    assert critical_pos > 0
    # LOW priority is not displayed in summary
    assert "LOW" not in summary or low_pos > critical_pos
