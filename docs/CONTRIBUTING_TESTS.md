# Contributing Tests to Empathy Framework

This guide will help you write high-quality tests for the Empathy Framework. Whether you're adding a new feature or fixing a bug, tests are essential to ensure code quality and prevent regressions.

## Quick Start

### 1. Install Development Dependencies
```bash
pip install -e ".[dev]"
```

### 2. Run Existing Tests
```bash
pytest
```

### 3. Create Your Test File
```bash
touch tests/test_your_feature.py
```

### 4. Write Your Tests
See examples below!

## Test File Naming Conventions

### File Names
- Use `test_` prefix: `test_my_feature.py`
- Match the module name: `test_core.py` for `core.py`
- Place in `tests/` directory at project root

### Class Names
- Use `Test` prefix: `TestMyFeature`
- Group related tests: `TestWizardInitialization`, `TestWizardAnalysis`
- One test class per major feature or component

### Method Names
- Use `test_` prefix: `test_basic_functionality`
- Be descriptive: `test_analyze_code_with_empty_string`
- Include what you're testing: `test_wizard_raises_error_on_invalid_input`

## Test Structure Template

```python
"""
Test suite for [Module Name]

Tests cover:
- Feature/Component A
- Feature/Component B
- Edge cases for C
- Error handling for D
"""

import pytest
from module_to_test import ClassToTest, function_to_test


class TestFeatureName:
    """Test suite for specific feature"""

    def test_basic_case(self):
        """Test the most common use case"""
        # Arrange: Set up test data
        obj = ClassToTest()

        # Act: Execute the function
        result = obj.method()

        # Assert: Verify results
        assert result == expected_value

    def test_edge_case(self):
        """Test edge case behavior"""
        # Test edge case here

    def test_error_case(self):
        """Test error handling"""
        with pytest.raises(ExpectedException):
            obj = ClassToTest()
            obj.method_that_raises()
```

## Pytest Fixtures Available

### Custom Fixtures
While we don't have a global conftest.py currently, you can create local fixtures in your test files:

```python
import pytest

@pytest.fixture
def wizard():
    """Provide a configured wizard instance"""
    return MyWizard(config={"level": 4})

@pytest.fixture
def sample_code():
    """Provide sample code for testing"""
    return """
    def hello():
        print("world")
    """

def test_with_fixtures(wizard, sample_code):
    result = wizard.analyze(sample_code)
    assert result is not None
```

### Built-in Pytest Fixtures
- `tmp_path`: Provides a temporary directory
- `monkeypatch`: Allows modifying code at runtime
- `capsys`: Captures stdout/stderr

Example:
```python
def test_with_tmp_path(tmp_path):
    """Test file operations using tmp_path"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("test content")
    # Test your file handling code
```

## Mocking Strategies

### Mocking LLM Calls

LLM calls are expensive and non-deterministic. Always mock them in tests unless you're specifically testing the LLM integration.

#### Basic LLM Mock
```python
from unittest.mock import patch, Mock

@patch('empathy_llm_toolkit.providers.LLMProvider.call')
def test_feature_with_llm(mock_llm):
    # Configure the mock to return specific response
    mock_llm.return_value = {
        "analysis": "Mock analysis result",
        "confidence": 0.95
    }

    # Your test code that calls the LLM
    wizard = MyWizard()
    result = wizard.analyze("code")

    # Verify the LLM was called
    mock_llm.assert_called_once()

    # Verify the result
    assert "analysis" in result
```

#### Advanced LLM Mocking with Multiple Calls
```python
@patch('empathy_llm_toolkit.providers.LLMProvider.call')
def test_multiple_llm_calls(mock_llm):
    # Mock returns different values for each call
    mock_llm.side_effect = [
        {"analysis": "First call"},
        {"analysis": "Second call"}
    ]

    result1 = wizard.analyze("code1")
    result2 = wizard.analyze("code2")

    assert mock_llm.call_count == 2
    assert result1 != result2
```

#### Mocking LLM Errors
```python
@patch('empathy_llm_toolkit.providers.LLMProvider.call')
def test_llm_error_handling(mock_llm):
    # Simulate LLM API error
    mock_llm.side_effect = Exception("API Error")

    wizard = MyWizard()

    # Verify your code handles the error gracefully
    with pytest.raises(Exception):
        wizard.analyze("code")
```

### Mocking File I/O

```python
from unittest.mock import mock_open, patch

def test_file_reading():
    """Test code that reads files"""
    mock_file_content = "test file content"

    with patch('builtins.open', mock_open(read_data=mock_file_content)):
        # Your code that reads files
        result = read_file("test.txt")

    assert result == mock_file_content
```

### Mocking External APIs

```python
import requests
from unittest.mock import patch

@patch('requests.get')
def test_api_call(mock_get):
    # Configure mock response
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    # Test code that calls API
    result = fetch_data()

    assert result["data"] == "test"
    mock_get.assert_called_once()
```

### Mocking Time/Dates

```python
from unittest.mock import patch
from datetime import datetime

@patch('module.datetime')
def test_time_sensitive_code(mock_datetime):
    # Fix time to specific value
    mock_datetime.now.return_value = datetime(2024, 1, 1, 12, 0, 0)

    # Test code that uses current time
    result = generate_timestamp()

    assert result == "2024-01-01 12:00:00"
```

## How to Test Async Code

### Basic Async Test
```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test asynchronous function"""
    result = await my_async_function()
    assert result is not None
```

### Async with Mocking
```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('module.async_llm_call', new_callable=AsyncMock)
async def test_async_llm(mock_async_llm):
    mock_async_llm.return_value = {"result": "test"}

    result = await wizard.async_analyze("code")

    assert result["result"] == "test"
    mock_async_llm.assert_awaited_once()
```

### Async Fixtures
```python
@pytest.fixture
async def async_wizard():
    """Provide async wizard instance"""
    wizard = AsyncWizard()
    await wizard.initialize()
    yield wizard
    await wizard.cleanup()

@pytest.mark.asyncio
async def test_with_async_fixture(async_wizard):
    result = await async_wizard.analyze("code")
    assert result is not None
```

## Coverage Requirements for PRs

### Minimum Standards
- **Overall**: Your PR should maintain or improve overall coverage (currently 90.71%)
- **New Code**: New files/modules must have at least 80% coverage
- **Critical Code**: Healthcare and security-related code requires 95%+ coverage
- **No Reduction**: PRs that reduce coverage below 90% will be rejected

### How to Check Coverage

#### Run Tests with Coverage
```bash
pytest --cov=empathy_os \
       --cov=empathy_llm_toolkit \
       --cov=empathy_software_plugin \
       --cov=empathy_healthcare_plugin \
       --cov=coach_wizards \
       --cov-report=term-missing
```

#### View HTML Coverage Report
```bash
pytest --cov --cov-report=html
open htmlcov/index.html  # Opens in browser
```

#### Check Coverage for Specific File
```bash
pytest tests/test_myfile.py --cov=my_module --cov-report=term-missing
```

### Understanding Coverage Output

```
Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
my_module.py               100      5    95%   42-46
```

- **Stmts**: Total statements in file
- **Miss**: Statements not covered by tests
- **Cover**: Coverage percentage
- **Missing**: Line numbers not covered

### Adding Tests for Uncovered Lines

1. Look at the "Missing" column in coverage report
2. Identify which code paths aren't tested
3. Add tests to cover those lines
4. Re-run coverage to verify

Example:
```python
# Coverage shows lines 42-46 are missing

# Original code
def process(value):
    if value > 0:
        return "positive"  # Line 42 (covered)
    elif value < 0:
        return "negative"  # Line 44 (NOT covered)
    return "zero"  # Line 46 (NOT covered)

# Add test for missing lines
def test_process_negative():
    assert process(-1) == "negative"  # Covers line 44

def test_process_zero():
    assert process(0) == "zero"  # Covers line 46
```

## Examples of Good Tests

### Example 1: Testing a Wizard

```python
"""
Tests for SecurityWizard

Tests cover:
- Wizard initialization
- Code analysis functionality
- Security issue detection
- Prediction generation
- Fix suggestions
"""

import pytest
from coach_wizards.security_wizard import SecurityWizard
from coach_wizards.base_wizard import WizardIssue, WizardPrediction


class TestSecurityWizardInitialization:
    """Test wizard initialization"""

    def test_wizard_created_with_correct_name(self):
        """Wizard should have correct name"""
        wizard = SecurityWizard()
        assert wizard.name == "Security Analysis"

    def test_wizard_created_with_correct_category(self):
        """Wizard should be in security category"""
        wizard = SecurityWizard()
        assert wizard.category == "security"

    def test_wizard_supports_correct_languages(self):
        """Wizard should support multiple languages"""
        wizard = SecurityWizard()
        assert "python" in wizard.supported_languages
        assert "javascript" in wizard.supported_languages


class TestSecurityWizardAnalysis:
    """Test code analysis functionality"""

    def test_analyze_returns_list(self):
        """Analyze should return list of issues"""
        wizard = SecurityWizard()
        result = wizard.analyze_code("code", "test.py", "python")

        assert isinstance(result, list)

    def test_analyze_detects_sql_injection(self):
        """Should detect SQL injection vulnerabilities"""
        wizard = SecurityWizard()
        code = '''
        query = "SELECT * FROM users WHERE id = " + user_input
        '''

        issues = wizard.analyze_code(code, "test.py", "python")

        # Should find SQL injection issue
        sql_issues = [i for i in issues if "sql" in i.message.lower()]
        assert len(sql_issues) > 0

    def test_analyze_with_empty_code(self):
        """Should handle empty code gracefully"""
        wizard = SecurityWizard()
        result = wizard.analyze_code("", "test.py", "python")

        assert isinstance(result, list)
        # Empty code shouldn't crash, but may return empty list or info messages


class TestSecurityWizardPredictions:
    """Test prediction generation"""

    def test_predict_returns_list(self):
        """Predict should return list of predictions"""
        wizard = SecurityWizard()
        result = wizard.predict_future_issues(
            code="code",
            file_path="test.py",
            project_context={}
        )

        assert isinstance(result, list)

    def test_predictions_have_required_fields(self):
        """Predictions should have all required fields"""
        wizard = SecurityWizard()
        predictions = wizard.predict_future_issues(
            code="vulnerable_code()",
            file_path="test.py",
            project_context={"complexity": "high"}
        )

        if predictions:
            pred = predictions[0]
            assert isinstance(pred, WizardPrediction)
            assert hasattr(pred, 'predicted_date')
            assert hasattr(pred, 'issue_type')
            assert hasattr(pred, 'probability')
            assert hasattr(pred, 'impact')
```

### Example 2: Testing with Parametrize

```python
class TestInputValidation:
    """Test input validation with multiple cases"""

    @pytest.mark.parametrize("input_value,expected", [
        ("", False),                    # Empty string
        ("   ", False),                 # Whitespace only
        ("valid code", True),           # Valid input
        ("x" * 10000, True),           # Large input
        ("unicode_✓", True),           # Unicode characters
        (None, False),                  # None value
    ])
    def test_validate_code_input(self, input_value, expected):
        """Test various code inputs"""
        wizard = MyWizard()
        result = wizard.validate_input(input_value)
        assert result == expected
```

### Example 3: Testing Error Handling

```python
class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_invalid_language_raises_error(self):
        """Should raise error for unsupported language"""
        wizard = MyWizard()

        with pytest.raises(ValueError, match="Unsupported language"):
            wizard.analyze_code("code", "test.txt", "unsupported")

    def test_none_code_raises_error(self):
        """Should raise error when code is None"""
        wizard = MyWizard()

        with pytest.raises(ValueError, match="Code cannot be None"):
            wizard.analyze_code(None, "test.py", "python")

    def test_handles_file_not_found_gracefully(self):
        """Should handle missing files gracefully"""
        wizard = MyWizard()

        # Should not crash, should return error info
        result = wizard.analyze_file("/nonexistent/file.py")

        assert result is not None
        assert "error" in result or "not found" in str(result).lower()
```

### Example 4: Testing Healthcare Monitor (Critical Code)

```python
"""
Tests for ClinicalProtocolMonitor

CRITICAL: This code deals with patient safety. All tests must pass.
Coverage requirement: 95%+
"""

import pytest
from empathy_healthcare_plugin.monitors.clinical_protocol_monitor import (
    ClinicalProtocolMonitor
)


class TestProtocolCompliance:
    """Test protocol compliance checking"""

    def test_detects_protocol_violation(self):
        """Should detect when protocol is violated"""
        monitor = ClinicalProtocolMonitor()
        monitor.load_protocol("sepsis_protocol.json")

        sensor_data = {
            "temperature": 102.5,  # High fever
            "heart_rate": 120,     # Elevated
            "antibiotics_given": False  # VIOLATION: Should have been given
        }

        result = monitor.analyze(
            patient_id="test_001",
            sensor_data=sensor_data
        )

        # Must detect the violation
        assert result["compliance"]["overall_compliant"] is False
        assert len(result["compliance"]["violations"]) > 0

        # Should generate alert
        alerts = monitor.generate_alerts(result)
        critical_alerts = [a for a in alerts if a["severity"] == "critical"]
        assert len(critical_alerts) > 0

    def test_intervention_timing_checked(self):
        """Should verify interventions are timely"""
        monitor = ClinicalProtocolMonitor()
        monitor.load_protocol("sepsis_protocol.json")

        # Simulate delayed intervention
        result = monitor.check_intervention_timing(
            intervention="antibiotics",
            protocol_time=60,  # Should be within 60 minutes
            actual_time=90     # Was delayed to 90 minutes
        )

        assert result["on_time"] is False
        assert result["delay_minutes"] == 30

    @pytest.mark.parametrize("vital_sign,value,expected_alert", [
        ("temperature", 105.0, "critical"),  # Dangerously high
        ("temperature", 101.0, "warning"),    # Elevated
        ("temperature", 98.6, None),          # Normal
        ("heart_rate", 150, "critical"),      # Tachycardia
        ("heart_rate", 100, "warning"),       # Elevated
        ("heart_rate", 70, None),             # Normal
    ])
    def test_vital_sign_alerts(self, vital_sign, value, expected_alert):
        """Test alert generation for various vital signs"""
        monitor = ClinicalProtocolMonitor()

        alert = monitor.check_vital_sign(vital_sign, value)

        if expected_alert:
            assert alert is not None
            assert alert["severity"] == expected_alert
        else:
            assert alert is None
```

## Common Testing Patterns

### Pattern: Testing Initialization
```python
def test_initialization_sets_defaults(self):
    """Test object initializes with correct defaults"""
    obj = MyClass()

    assert obj.attribute == expected_default
    assert obj.state == "initial"
    assert obj.config is not None
```

### Pattern: Testing State Changes
```python
def test_state_transition(self):
    """Test state changes correctly"""
    obj = MyClass()
    assert obj.state == "initial"

    obj.start()
    assert obj.state == "running"

    obj.stop()
    assert obj.state == "stopped"
```

### Pattern: Testing Collections
```python
def test_returns_non_empty_list(self):
    """Test returns non-empty list when items exist"""
    obj = MyClass()
    obj.add_item("test")

    result = obj.get_items()

    assert isinstance(result, list)
    assert len(result) > 0
    assert "test" in result
```

### Pattern: Testing Dataclasses
```python
def test_dataclass_creation(self):
    """Test dataclass can be created with all fields"""
    obj = MyDataClass(
        field1="value1",
        field2=42,
        field3=True
    )

    assert obj.field1 == "value1"
    assert obj.field2 == 42
    assert obj.field3 is True
```

## Tips for Writing Effective Tests

### 1. Test One Thing at a Time
```python
# Good: Tests one specific behavior
def test_adds_item_to_list(self):
    obj = MyClass()
    obj.add("item")
    assert "item" in obj.items

# Bad: Tests multiple things
def test_everything(self):
    obj = MyClass()
    obj.add("item")
    obj.remove("item")
    obj.clear()
    # Too many concerns in one test
```

### 2. Use Descriptive Names
```python
# Good: Clear what's being tested
def test_analyze_raises_valueerror_when_code_is_none(self):
    pass

# Bad: Unclear purpose
def test_analyze_error(self):
    pass
```

### 3. Don't Test Implementation Details
```python
# Good: Tests behavior
def test_filters_invalid_items(self):
    result = filter_items(items)
    assert all(item.valid for item in result)

# Bad: Tests implementation
def test_uses_list_comprehension(self):
    # Don't test HOW it's done, test WHAT it does
    pass
```

### 4. Keep Tests Simple
```python
# Good: Simple and clear
def test_sum_returns_total(self):
    assert sum([1, 2, 3]) == 6

# Bad: Too complex
def test_calculations(self):
    # 50 lines of setup
    # Multiple calculations
    # Complex assertions
    pass
```

### 5. Use Helpful Assertion Messages
```python
# Good: Helpful message
assert result == expected, f"Expected {expected}, got {result}"

# Better: Context-specific message
assert len(issues) > 0, f"No security issues found in vulnerable code: {code}"
```

## Debugging Failed Tests

### View Full Error Output
```bash
pytest -vv --tb=long
```

### Run Specific Failing Test
```bash
pytest tests/test_file.py::TestClass::test_method -vv
```

### Print Debug Information
```python
def test_with_debug():
    result = function_to_test()
    print(f"Result: {result}")  # Will show in pytest output with -s
    assert result == expected
```

### Use pdb Debugger
```python
def test_with_debugger():
    result = function_to_test()
    import pdb; pdb.set_trace()  # Breakpoint
    assert result == expected
```

Or run with:
```bash
pytest --pdb  # Drop into debugger on failure
```

## Checklist Before Submitting PR

- [ ] All new code has tests
- [ ] Tests pass locally: `pytest`
- [ ] Coverage is maintained: `pytest --cov`
- [ ] Tests are properly named and documented
- [ ] Edge cases are covered
- [ ] Error conditions are tested
- [ ] LLM calls are mocked (if applicable)
- [ ] Async code uses `@pytest.mark.asyncio`
- [ ] Critical code (healthcare/security) has 95%+ coverage
- [ ] No test-specific code in production modules
- [ ] Tests are independent (can run in any order)

## Getting Help

### Resources
- **Testing Strategy**: See `docs/TESTING_STRATEGY.md` for overall approach
- **Pytest Docs**: https://docs.pytest.org/
- **Example Tests**: Look at existing test files in `tests/` directory
- **Coverage Report**: Run `pytest --cov --cov-report=html` and open `htmlcov/index.html`

### Ask Questions
If you're unsure how to test something:
1. Look for similar tests in the codebase
2. Check the testing strategy document
3. Ask in code review or create a draft PR with questions
4. Start with basic tests and iterate

## Happy Testing!

Remember: Good tests make confident developers. Take the time to write thorough tests and future you (and your teammates) will thank you!
