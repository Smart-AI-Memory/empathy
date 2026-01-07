# Coding Standards Quick Reference

**Full Documentation:** [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md)
**Version:** 3.9.1
**Last Updated:** January 7, 2026

---

## Critical Security Rules (MUST FOLLOW)

### 1. NEVER Use eval() or exec()

```python
# ❌ PROHIBITED - Code injection vulnerability
result = eval(user_input)

# ✅ REQUIRED - Use ast.literal_eval or json.loads
import ast
data = ast.literal_eval(user_input)
```

**Exception:** None. Always a security vulnerability (CWE-95).

---

### 2. ALWAYS Validate File Paths

```python
# ❌ PROHIBITED - Path traversal vulnerability
with open(user_path, 'w') as f:
    f.write(data)

# ✅ REQUIRED - Validate before writing
from empathy_os.config import _validate_file_path

validated_path = _validate_file_path(user_path)
with validated_path.open('w') as f:
    f.write(data)
```

**Applies to:** All user-controlled file paths
**Blocks:** Path traversal (CWE-22), null byte injection, system directory writes

---

## Exception Handling Rules

### 3. NEVER Use Bare except:

```python
# ❌ PROHIBITED - Masks all errors including KeyboardInterrupt
try:
    risky_operation()
except:  # Never do this
    pass

# ❌ ALSO PROHIBITED - Too broad in most cases
try:
    risky_operation()
except Exception:
    return None

# ✅ REQUIRED - Catch specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except FileNotFoundError as e:
    logger.warning(f"File not found: {e}")
    return default_value
```

**Acceptable broad catches:** Only when documented with `# INTENTIONAL:` comment and `# noqa: BLE001`

**Scenarios allowing Exception:**
- Version detection with fallback
- Optional feature detection
- Cleanup/teardown code (`__del__`, `__exit__`)
- Graceful degradation (must log and document)

---

### 4. ALWAYS Log Exceptions

```python
# ❌ PROHIBITED - Silent failure
try:
    dangerous_operation()
except IOError:
    pass

# ✅ REQUIRED - Log and re-raise
try:
    dangerous_operation()
except IOError as e:
    logger.error(f"Failed operation: {e}")
    raise
```

---

## Code Quality Requirements

### 5. Type Hints Required

```python
# ✅ All functions must have type hints
def calculate_total(prices: list[float], tax_rate: float) -> float:
    return sum(prices) * (1 + tax_rate)
```

### 6. Docstrings Required

```python
def validate_email(email: str) -> bool:
    """Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid format, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

**Format:** Google-style docstrings

---

## Testing Requirements

### 7. Test Coverage: Minimum 80%

- ✅ Unit tests (80%+ coverage)
- ✅ Edge case tests
- ✅ Error handling tests

### 8. Security Tests for File Operations

```python
def test_save_prevents_path_traversal():
    """Test that save blocks path traversal attacks."""
    config = EmpathyConfig(user_id="test")

    with pytest.raises(ValueError, match="Cannot write to system directory"):
        config.to_yaml("/etc/passwd")

def test_save_prevents_null_bytes():
    """Test that save blocks null byte injection."""
    config = EmpathyConfig(user_id="test")

    with pytest.raises(ValueError, match="contains null bytes"):
        config.to_yaml("config\x00.yml")
```

---

## File Operations

### 9. Use Context Managers

```python
# ✅ REQUIRED - Automatic cleanup
with open(filename) as f:
    data = f.read()

# ❌ PROHIBITED - File may not close
f = open(filename)
data = f.read()
f.close()
```

---

## Enforcement

### Pre-commit Hooks

```bash
# Install hooks
pre-commit install
```

**Enforces:**
- Black formatting (line length 100)
- Ruff linting (BLE001: no bare except)
- Bandit security scanning
- detect-secrets credential scanning

### Manual Checks

```bash
# Find security issues
ruff check src/ --select S307  # eval/exec usage
grep -r "open(" src/ | grep -v "_validate_file_path"

# Find exception issues
ruff check src/ --select BLE  # bare except

# Check type hints
mypy src/ --disallow-untyped-defs

# Check coverage
pytest --cov=src --cov-report=term-missing
```

---

## Code Review Checklist

Before merging, verify:

- [ ] No `eval()` or `exec()` usage
- [ ] No bare `except:` or broad `except Exception:` (without justification)
- [ ] All file paths validated with `_validate_file_path()`
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] Test coverage ≥80%
- [ ] Security tests for file operations
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks passing
- [ ] All tests passing

---

## Violation Severity

**CRITICAL** (Must fix immediately):
- `eval()` or `exec()` usage
- Path traversal vulnerabilities
- Hardcoded secrets

**HIGH** (Must fix before merge):
- Bare `except:` clauses
- Missing type hints on public APIs
- Test coverage <80%

**MEDIUM** (Should fix):
- Missing docstrings
- Magic numbers

---

## Quick Examples

### Good Code Pattern

```python
from pathlib import Path
from empathy_os.config import _validate_file_path
import logging

logger = logging.getLogger(__name__)


def save_configuration(filepath: str, config: dict) -> Path:
    """Save configuration to file with security validation.

    Args:
        filepath: Path where config should be saved (user-controlled)
        config: Configuration dictionary to save

    Returns:
        Validated Path where file was saved

    Raises:
        ValueError: If filepath is invalid or targets system directory
        PermissionError: If insufficient permissions to write file
    """
    # Validate path to prevent attacks
    validated_path = _validate_file_path(filepath)

    try:
        # Use context manager for safe file handling
        with validated_path.open('w') as f:
            json.dump(config, f, indent=2)
    except PermissionError as e:
        logger.error(f"Permission denied writing to {validated_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {validated_path}: {e}")
        raise ValueError(f"Cannot write config: {e}") from e

    logger.info(f"Configuration saved to {validated_path}")
    return validated_path
```

**What makes this good:**
- ✅ Type hints on parameters and return
- ✅ Comprehensive docstring
- ✅ Path validation before use
- ✅ Specific exception handling
- ✅ Logging at appropriate levels
- ✅ Context manager for file handling
- ✅ Preserves exception context with `from e`

---

## Related Documentation

- [Exception Handling Guide](../../../docs/EXCEPTION_HANDLING_GUIDE.md) - Detailed exception patterns
- [Security Policy](../../../SECURITY.md) - Security reporting and best practices
- [Contributing Guide](../../../CONTRIBUTING.md) - How to contribute
- [Full Coding Standards](../../../docs/CODING_STANDARDS.md) - Complete documentation

---

**Questions?** See full documentation in [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md)
