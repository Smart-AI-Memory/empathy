# Testing Guide - Empathy Framework

**Version**: 3.11.0
**Last Updated**: January 10, 2026

This guide covers the testing infrastructure, optimization strategies, and best practices for the Empathy Framework test suite.

---

## 🚀 Quick Start

### Install Test Dependencies

```bash
pip install -e ".[dev]"
```

This installs:
- `pytest` - Test framework
- `pytest-xdist` - Parallel test execution (4-8x faster)
- `pytest-testmon` - Run only tests affected by changes
- `pytest-picked` - Run tests for uncommitted changes
- `pytest-cov` - Code coverage
- `pytest-asyncio` - Async test support

### Run Tests

```bash
# Full test suite (parallel, 2-4 minutes)
pytest

# Fast smoke tests only (~30 seconds)
pytest -m smoke

# Skip slow tests (development mode)
pytest -m "not slow"

# Run only changed tests
pytest --testmon

# Run tests for uncommitted changes
pytest --picked

# Sequential (for debugging)
pytest -n 0
```

---

## 📊 Test Suite Overview

**Current Stats (v3.11.0)**:
- **Total tests**: 6,936
- **Passing**: 6,748 (97%)
- **Test time**: 2-4 minutes (parallel) vs 16 minutes (sequential)
- **Speedup**: 4-8x with pytest-xdist

**Test Categories**:
- Unit tests: ~5,500
- Integration tests: ~800
- Security tests: ~200
- Performance tests: ~100
- LLM tests: ~300

---

## 🏷️ Test Markers

Tests are categorized using pytest markers for selective execution:

| Marker | Description | Usage |
|--------|-------------|-------|
| `@pytest.mark.smoke` | Critical smoke tests | `pytest -m smoke` |
| `@pytest.mark.slow` | Slow tests (>2s) | `pytest -m "not slow"` |
| `@pytest.mark.unit` | Unit tests (coverage measured) | `pytest -m unit` |
| `@pytest.mark.integration` | Integration tests (CLI subprocess) | `pytest -m integration` |
| `@pytest.mark.security` | Security-related tests | `pytest -m security` |
| `@pytest.mark.performance` | Performance benchmarks | `pytest -m performance` |
| `@pytest.mark.llm` | Tests requiring LLM API | `pytest -m "not llm"` (skip) |
| `@pytest.mark.network` | Tests requiring network | `pytest -m "not network"` (offline) |

### Example: Adding Markers

```python
import pytest

@pytest.mark.smoke
def test_basic_import():
    """Critical smoke test - framework can import."""
    from empathy_os import EmpathyConfig
    assert EmpathyConfig is not None

@pytest.mark.slow
@pytest.mark.integration
def test_full_workflow():
    """Slow integration test."""
    # Test takes >2s, involves subprocess
    pass
```

---

## ⚡ Parallel Testing with pytest-xdist

### How It Works

pytest-xdist distributes tests across multiple CPU cores:

```bash
# Auto-detect CPU cores (recommended)
pytest -n auto

# Specify number of workers
pytest -n 8

# Disable parallel (debugging)
pytest -n 0
```

**Performance**:
- **Before**: 16 minutes (sequential)
- **After**: 2-4 minutes (8 cores)
- **Speedup**: 4-8x

### Configuration

Parallel execution is enabled by default in `pytest.ini`:

```ini
[pytest]
addopts =
    -n auto  # Parallel execution
    --maxfail=5  # Stop after 5 failures
```

### When to Disable Parallel

```bash
# Debugging (need to see sequential output)
pytest -n 0 tests/test_specific.py

# Tests with shared state (rare)
pytest -n 0 -m integration
```

---

## 🎯 Smart Test Selection

### testmon: Run Only Affected Tests

Tracks code changes and runs only tests affected by your edits:

```bash
# First run: all tests (creates baseline)
pytest --testmon

# Subsequent runs: only affected tests
pytest --testmon  # ~10-30s for small changes

# Force re-run all tests
pytest --testmon --testmon-nocache
```

**Use case**: Development workflow (fast feedback loop)

### pytest-picked: Uncommitted Changes

Runs tests for files you've modified but not committed:

```bash
# Run tests for uncommitted changes
pytest --picked

# Works with git status
git status  # Shows changed files
pytest --picked  # Runs tests for those files
```

**Use case**: Pre-commit validation

---

## 📁 Test Organization

```
tests/
├── conftest.py             # Global fixtures and configuration
├── unit/                   # Unit tests (fast, isolated)
│   ├── test_config.py
│   ├── test_pattern_library.py
│   └── workflows/
│       └── test_health_check.py
├── integration/            # Integration tests (slower, end-to-end)
│   ├── test_cli.py
│   └── test_workflows.py
├── benchmarks/            # Performance benchmarks
│   ├── profile_suite.py
│   └── test_lookup_optimization.py
└── fixtures/              # Test data and mocks
```

---

## 🧪 Test Profiles

### Development Profile (Fast Feedback)

```bash
# Smoke tests only (~30 seconds)
pytest -m smoke

# All tests except slow (~2 minutes)
pytest -m "not slow"

# Only tests affected by changes
pytest --testmon
```

### Pre-Commit Profile

```bash
# Tests for uncommitted changes
pytest --picked --maxfail=3

# Fast parallel run without slow tests
pytest -m "not slow" --maxfail=5
```

### CI Profile (Full Validation)

```bash
# Full test suite with coverage
pytest --cov=src --cov-report=term-missing

# All tests in parallel
pytest -n auto --maxfail=10
```

### Debugging Profile

```bash
# Sequential execution, verbose, stop on first failure
pytest -n 0 -vv -x tests/test_specific.py

# With debugger (breakpoints)
pytest -n 0 -s --pdb
```

---

## 🔧 Test Fixtures

### Automatic Environment Setup

All tests automatically get a clean environment via `conftest.py`:

```python
@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path, monkeypatch):
    """Auto-creates .empathy, .claude directories in temp location."""
    # Creates:
    # - .empathy/
    #   - cost_tracking/
    #   - telemetry/
    #   - patterns/
    # - .claude/

    # Tests run in isolated tmp_path
    # Original directory restored after test
```

**Benefits**:
- No `.empathy` directory creation errors
- Isolated test execution
- No pollution of home directory
- Automatic cleanup

### Common Fixtures

```python
import pytest

@pytest.fixture
def temp_config(tmp_path):
    """Temporary config file."""
    config_file = tmp_path / "empathy.yml"
    config_file.write_text("user_id: test\n")
    return config_file

@pytest.fixture
def mock_llm_response():
    """Mock LLM API response."""
    return {"content": "Test response", "tokens": 100}
```

---

## 📈 Coverage

### Measure Code Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=term-missing

# HTML report (interactive)
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Fail if coverage below threshold
pytest --cov=src --cov-fail-under=80
```

### Current Coverage

- **Overall**: 68%
- **Target**: 80%
- **Critical modules**: >90%

---

## 🐛 Debugging Tests

### Run Single Test

```bash
# Specific test function
pytest tests/test_config.py::test_config_creation -vv

# Specific test class
pytest tests/test_config.py::TestConfigValidation -vv
```

### Enable Debugger

```bash
# Drop into pdb on failure
pytest --pdb

# Drop into pdb on first failure
pytest -x --pdb

# Allow print statements
pytest -s
```

### Verbose Output

```bash
# Very verbose
pytest -vv

# Show local variables on failure
pytest -l

# Show full stack traces
pytest --tb=long
```

---

## 🚨 Common Issues & Solutions

### Issue: Tests Fail with "No such file or directory: '.empathy'"

**Solution**: Fixed in v3.11.0 with `setup_test_environment` fixture.

If still occurring:
```bash
# Ensure you're using latest conftest.py
git pull origin main
pytest tests/
```

### Issue: Parallel Tests Hang or Timeout

**Solution**: Some tests may have shared state issues.

```bash
# Run sequentially to identify problematic test
pytest -n 0 tests/test_problematic.py

# Mark as non-parallelizable
@pytest.mark.parametrize("worker_id", ["gw0"])
def test_needs_sequential():
    pass
```

### Issue: Slow Test Suite

**Solution**:
1. Use parallel execution: `pytest -n auto`
2. Skip slow tests: `pytest -m "not slow"`
3. Use testmon: `pytest --testmon`

**Expected times**:
- Smoke tests: ~30s
- Fast tests (no slow): ~2 min
- Full suite (parallel): ~3 min
- Full suite (sequential): ~16 min

---

## 📊 Performance Benchmarks

### Track Test Performance

```bash
# Show 20 slowest tests
pytest --durations=20

# Profile test execution
pytest --profile

# Benchmark-specific tests
pytest tests/benchmarks/ --benchmark-only
```

### Example Output

```
============================= slowest 20 durations ==============================
5.23s call     tests/integration/test_full_workflow.py::test_health_check
2.41s call     tests/integration/test_cli.py::test_cli_scan
1.83s call     tests/test_scanner.py::test_scan_large_project
...
```

---

## 🔄 CI Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install -e ".[dev]"

      - name: Run tests
        run: |
          pytest -n auto --cov=src --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 🎓 Best Practices

### 1. Write Fast Tests

```python
# Good: Fast, isolated unit test
def test_config_validation():
    config = EmpathyConfig(user_id="test")
    assert config.user_id == "test"

# Avoid: Slow, integration test for unit behavior
def test_config_via_cli():
    result = subprocess.run(["empathy", "config", "show"])
    # Slower, more brittle
```

### 2. Use Markers Appropriately

```python
# Mark slow tests
@pytest.mark.slow
def test_full_scan():
    # Takes >2s
    pass

# Mark critical tests
@pytest.mark.smoke
def test_import():
    # Must always pass
    pass
```

### 3. Isolate Test Data

```python
# Good: Use tmp_path for file operations
def test_save_config(tmp_path):
    config_file = tmp_path / "config.yml"
    save_config(config_file)
    assert config_file.exists()

# Avoid: Using current directory
def test_save_config_bad():
    save_config("config.yml")  # Pollutes repo
```

### 4. Descriptive Test Names

```python
# Good
def test_config_raises_value_error_for_empty_user_id():
    with pytest.raises(ValueError, match="user_id cannot be empty"):
        EmpathyConfig(user_id="")

# Avoid
def test_config_error():
    # What error? When?
    pass
```

---

## 📚 Additional Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-xdist](https://pytest-xdist.readthedocs.io/)
- [pytest-testmon](https://testmon.org/)
- [Coverage.py](https://coverage.readthedocs.io/)

---

## 🆘 Getting Help

- **Documentation**: [docs/testing/](docs/testing/)
- **Issues**: [GitHub Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)

---

**Summary of Testing Improvements (v3.11.0)**:
- ✅ **4-8x faster** with pytest-xdist
- ✅ **Automatic environment setup** (no more .empathy errors)
- ✅ **Smart test selection** (testmon, picked)
- ✅ **Comprehensive markers** (smoke, slow, unit, integration)
- ✅ **Test profiles** for different workflows

**Expected test times**:
- Smoke tests: 30s
- Development (no slow): 2 min
- Full suite (parallel): 3-4 min
- Full suite (sequential): 16 min

Happy testing! 🎉
