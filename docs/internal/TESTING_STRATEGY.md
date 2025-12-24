# Testing Strategy for Empathy Framework

## Overview

The Empathy Framework maintains a high standard of test coverage with an overall coverage rate of **90.71%**. This document outlines our testing approach, goals, types, and best practices.

## Coverage Goals

- **Current Coverage**: 90.71%
- **Target Coverage**: 90%+ (ACHIEVED)
- **Stretch Goal**: 95%
- **Minimum Coverage**: 14% (configured threshold, far exceeded)

### Coverage Status by Module

| Module | Coverage | Status |
|--------|----------|--------|
| coach_wizards | 99.96% | Excellent |
| empathy_healthcare_plugin | 98.72% | Excellent |
| empathy_llm_toolkit | 97.47% | Excellent |
| src/empathy_os | 98.45% | Excellent |
| empathy_software_plugin | 72.89% | Needs Attention |

## Testing Approach

### 1. Test-Driven Development (TDD)
- Write tests before implementation for new features
- Use tests to define expected behavior
- Refactor with confidence knowing tests will catch regressions

### 2. Multi-Level Testing
Our testing strategy employs multiple levels:

#### Unit Tests
- Test individual functions and classes in isolation
- Mock external dependencies (LLM calls, file I/O, network)
- Fast execution (majority of test suite)
- Located in `tests/test_*.py` files

#### Integration Tests
- Test interaction between components
- Test plugin registration and lifecycle
- Test end-to-end workflows
- Marked with `@pytest.mark.integration`

#### LLM-Based Tests
- Tests that interact with actual LLM providers
- Marked with `@pytest.mark.llm`
- Should be skipped in CI unless explicitly enabled
- Require API keys and may incur costs

### 3. Coverage Measurement
We use `pytest-cov` to track code coverage across all modules:

```bash
pytest --cov=empathy_os \
       --cov=empathy_llm_toolkit \
       --cov=empathy_software_plugin \
       --cov=empathy_healthcare_plugin \
       --cov=coach_wizards \
       --cov-report=html \
       --cov-report=term-missing \
       --cov-report=xml
```

## Types of Tests

### 1. Unit Tests
**Purpose**: Verify individual components work correctly

**Example**:
```python
def test_wizard_issue_creation():
    issue = WizardIssue(
        severity="error",
        message="Test error",
        file_path="/test/file.py",
        line_number=42,
        code_snippet="bad_code()",
        fix_suggestion="Use good_code() instead",
        category="security",
        confidence=0.95,
    )
    assert issue.severity == "error"
    assert issue.line_number == 42
```

### 2. Wizard Tests
**Purpose**: Ensure wizards (code analysis tools) function correctly

**Pattern**:
- Test initialization
- Test code analysis
- Test future issue prediction
- Test fix suggestions

### 3. Plugin Tests
**Purpose**: Verify plugin system works correctly

**Coverage**:
- Plugin loading and registration
- Plugin lifecycle (initialization, execution, cleanup)
- Plugin configuration
- Plugin interactions

### 4. Healthcare Monitoring Tests
**Purpose**: Ensure medical protocol monitoring is accurate and safe

**Critical Areas**:
- Protocol compliance checking
- Sensor data parsing
- Trajectory analysis
- Alert generation
- Safety-critical paths

### 5. LLM Integration Tests
**Purpose**: Test LLM provider integrations

**Approach**:
- Mock LLM responses for unit tests
- Optional real LLM tests (marked with `@pytest.mark.llm`)
- Test prompt engineering
- Test response parsing
- Test error handling

## How to Run Tests

### Run All Tests
```bash
pytest
```

### Run with Coverage Report
```bash
pytest --cov --cov-report=html
```

### Run Specific Test File
```bash
pytest tests/test_base_wizard.py
```

### Run Specific Test Class
```bash
pytest tests/test_base_wizard.py::TestWizardDataclasses
```

### Run Specific Test
```bash
pytest tests/test_base_wizard.py::TestWizardDataclasses::test_wizard_issue_creation
```

### Run Tests by Marker
```bash
# Run only unit tests
pytest -m unit

# Skip slow tests
pytest -m "not slow"

# Run integration tests
pytest -m integration

# Run LLM tests (requires API keys)
pytest -m llm
```

### Run Tests in Parallel
```bash
pytest -n auto  # Uses all available CPU cores
```

### Run with Verbose Output
```bash
pytest -v
```

### Run with Debug Output
```bash
pytest -vv --tb=long
```

## How to Write New Tests

### Test File Structure
```python
"""
Brief description of what this test file covers

Tests cover:
- Feature A
- Feature B
- Edge cases for C
"""

import pytest
from module import ClassToTest


class TestFeatureName:
    """Test suite for a specific feature"""

    def test_basic_functionality(self):
        """Test the most basic use case"""
        # Arrange
        obj = ClassToTest()

        # Act
        result = obj.method()

        # Assert
        assert result == expected_value

    def test_edge_case_empty_input(self):
        """Test behavior with empty input"""
        obj = ClassToTest()
        result = obj.method("")
        assert result is None or result == default_value

    @pytest.mark.parametrize("input,expected", [
        ("case1", "result1"),
        ("case2", "result2"),
        ("case3", "result3"),
    ])
    def test_multiple_cases(self, input, expected):
        """Test multiple cases with parametrize"""
        obj = ClassToTest()
        assert obj.method(input) == expected
```

### Test Naming Conventions
- Test files: `test_<module_name>.py`
- Test classes: `Test<FeatureName>`
- Test methods: `test_<what_it_tests>`
- Be descriptive: `test_analyze_code_with_empty_string` not `test_1`

### Arrange-Act-Assert Pattern
```python
def test_feature():
    # Arrange: Set up test data and conditions
    wizard = MyWizard(config={})
    code = "def hello(): print('world')"

    # Act: Execute the code being tested
    result = wizard.analyze_code(code, "test.py", "python")

    # Assert: Verify the results
    assert isinstance(result, list)
    assert len(result) > 0
```

## Testing Best Practices

### 1. Test Independence
- Each test should run independently
- Don't rely on test execution order
- Clean up after tests (use fixtures or teardown)

### 2. Use Fixtures for Common Setup
```python
@pytest.fixture
def wizard():
    """Provide a wizard instance for tests"""
    return MyWizard(config={"level": 4})

def test_with_fixture(wizard):
    result = wizard.analyze("code")
    assert result is not None
```

### 3. Mock External Dependencies
```python
from unittest.mock import Mock, patch

@patch('module.llm_provider.call')
def test_with_mocked_llm(mock_call):
    mock_call.return_value = "mocked response"
    # Test code that calls LLM
```

### 4. Test Edge Cases
Always test:
- Empty inputs (`""`, `[]`, `{}`, `None`)
- Large inputs
- Invalid inputs
- Boundary conditions
- Error conditions
- Unicode/special characters
- Concurrent operations

### 5. Async Testing
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### 6. Test Data
- Keep test data small and focused
- Use realistic but simplified examples
- Consider using factories or builders for complex objects

### 7. Assertions
- Use specific assertions: `assert x == y` not `assert x`
- Test one concept per test
- Include helpful assertion messages:
  ```python
  assert result == expected, f"Expected {expected}, got {result}"
  ```

## Mocking Strategies

### Mocking LLM Calls
Since LLM calls are expensive and non-deterministic, we mock them in tests:

```python
from unittest.mock import patch, Mock

@patch('empathy_llm_toolkit.providers.LLMProvider.call')
def test_wizard_with_mocked_llm(mock_llm_call):
    # Configure mock response
    mock_llm_call.return_value = {
        "analysis": "Test analysis",
        "issues": []
    }

    wizard = MyWizard()
    result = wizard.analyze("code")

    # Verify LLM was called correctly
    mock_llm_call.assert_called_once()
    assert "analysis" in result
```

### Mocking File I/O
```python
@patch('builtins.open', create=True)
def test_file_reading(mock_open):
    mock_open.return_value.__enter__.return_value.read.return_value = "file contents"
    # Test code that reads files
```

### Mocking Time
```python
from unittest.mock import patch
from datetime import datetime

@patch('module.datetime')
def test_time_sensitive_code(mock_datetime):
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)
    # Test code that uses current time
```

## How to Test Async Code

### Basic Async Test
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    result = await my_async_function()
    assert result is not None
```

### Async with Fixtures
```python
@pytest.fixture
async def async_resource():
    resource = await setup_resource()
    yield resource
    await teardown_resource(resource)

@pytest.mark.asyncio
async def test_with_async_fixture(async_resource):
    result = await async_resource.method()
    assert result is not None
```

## Coverage Requirements for Pull Requests

### Minimum Standards
- New code must have at least 80% coverage
- Critical paths (healthcare, security) require 95%+ coverage
- PRs that decrease overall coverage below 90% will be rejected

### Coverage Report in PRs
- Coverage report is automatically generated in CI
- Review missing lines in the coverage report
- Add tests for uncovered code before merging

### Exemptions
Some code may be excluded from coverage requirements:
- Debug/development utilities
- Example scripts
- Generated code
- Deprecated modules

Add coverage exclusions with comments:
```python
def debug_only_function():  # pragma: no cover
    """This is only for development debugging"""
    pass
```

## CI/CD Testing Integration

### GitHub Actions Workflow
Our CI runs tests on:
- Every push to main
- Every pull request
- Multiple Python versions (3.9, 3.10, 3.11)

### Test Stages
1. **Lint and Format**: Runs black, flake8, mypy
2. **Unit Tests**: Fast tests without external dependencies
3. **Integration Tests**: Tests with mocked external services
4. **Coverage Report**: Generates and uploads coverage data

### Required Checks
PRs must pass:
- All tests (100% pass rate required)
- Minimum coverage threshold (90%)
- Linting and formatting checks
- Type checking (mypy)

## Testing Tools and Dependencies

### Core Testing Tools
- **pytest**: Test framework
- **pytest-cov**: Coverage measurement
- **pytest-asyncio**: Async test support
- **pytest-xdist**: Parallel test execution
- **pytest-timeout**: Timeout handling

### Mocking and Fixtures
- **unittest.mock**: Python standard mocking
- **pytest fixtures**: Reusable test components

### Coverage Reporting
- **coverage.py**: Coverage measurement engine
- **coverage-badge**: Generate coverage badges
- HTML, XML, and JSON output formats

## Common Testing Patterns

### Pattern 1: Testing Wizards
```python
class TestMyWizard:
    def test_initialization(self):
        wizard = MyWizard()
        assert wizard.name == "My Wizard"
        assert wizard.category == "analysis"

    def test_analyze_code_returns_list(self):
        wizard = MyWizard()
        result = wizard.analyze_code("code", "test.py", "python")
        assert isinstance(result, list)

    def test_predict_future_issues_returns_predictions(self):
        wizard = MyWizard()
        result = wizard.predict_future_issues("code", "test.py", {})
        assert isinstance(result, list)
        if result:
            assert isinstance(result[0], WizardPrediction)
```

### Pattern 2: Testing Plugins
```python
def test_plugin_registration():
    registry = PluginRegistry()
    plugin = MyPlugin()

    registry.register(plugin)

    assert plugin.name in registry.list_plugins()
    assert registry.get_plugin(plugin.name) == plugin
```

### Pattern 3: Testing Error Conditions
```python
def test_invalid_input_raises_error():
    wizard = MyWizard()

    with pytest.raises(ValueError, match="Invalid code"):
        wizard.analyze_code(None, "test.py", "python")
```

## Troubleshooting Tests

### Tests Fail Intermittently
- Check for race conditions in async code
- Look for shared state between tests
- Verify test independence
- Check for time-dependent assertions

### Tests Are Slow
- Profile test execution: `pytest --durations=10`
- Mock expensive operations (LLM calls, file I/O)
- Use pytest-xdist for parallel execution
- Mark slow tests: `@pytest.mark.slow`

### Coverage Lower Than Expected
- Run with `--cov-report=html` to see uncovered lines
- Check for unreachable code
- Add tests for edge cases
- Review conditional branches

### Import Errors in Tests
- Ensure package is installed: `pip install -e .`
- Check PYTHONPATH
- Verify test discovery patterns in pytest.ini

## Resources

### Documentation
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### Internal Resources
- See `docs/CONTRIBUTING_TESTS.md` for contributor guide
- See `pytest.ini` for project configuration
- See `.coveragerc` for coverage configuration
- See test files in `tests/` for examples

## Continuous Improvement

### Regular Review
- Review coverage reports weekly
- Identify and address coverage gaps
- Update tests as code evolves
- Refactor tests for clarity and maintainability

### Metrics to Track
- Overall coverage percentage
- Coverage by module
- Test execution time
- Test flakiness rate
- Number of tests

### Goals
- Maintain >90% overall coverage
- Keep test execution under 5 minutes
- Zero test flakiness
- Comprehensive edge case coverage
