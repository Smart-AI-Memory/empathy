# Coding Standards

**Version:** 3.9.1
**Last Updated:** January 7, 2026
**Maintained By:** Engineering Team

---

## Purpose

This document establishes coding standards for the Empathy Framework to ensure security, maintainability, and code quality across all contributions.

---

## Table of Contents

1. [Security Standards](#security-standards)
2. [Exception Handling](#exception-handling)
3. [File Operations](#file-operations)
4. [Code Quality](#code-quality)
5. [Testing Requirements](#testing-requirements)
6. [Documentation Standards](#documentation-standards)
7. [Enforcement](#enforcement)

---

## Security Standards

### 1. Never Use eval() or exec()

**❌ Prohibited:**
```python
# NEVER do this
user_input = request.get("formula")
result = eval(user_input)  # Code injection vulnerability!
```

**✅ Allowed:**
```python
# Use ast.literal_eval for safe evaluation of literals
import ast

try:
    data = ast.literal_eval(user_input)  # Only evaluates literals
except (ValueError, SyntaxError) as e:
    raise ValueError(f"Invalid input format: {e}")

# Or use json.loads for structured data
import json
data = json.loads(user_input)
```

**Rationale:** `eval()` and `exec()` enable arbitrary code execution, creating severe security vulnerabilities (CWE-95).

**Exceptions:** None. There are always safer alternatives.

---

### 2. Validate All File Paths

**❌ Prohibited:**
```python
# Never write to user-controlled paths directly
def save_config(user_path: str, data: dict):
    with open(user_path, 'w') as f:  # Path traversal vulnerability!
        json.dump(data, f)
```

**✅ Required:**
```python
# Always validate paths before file operations
from empathy_os.config import _validate_file_path

def save_config(user_path: str, data: dict):
    validated_path = _validate_file_path(user_path)
    with open(validated_path, 'w') as f:
        json.dump(data, f)
```

**Rationale:** User-controlled file paths enable path traversal attacks (CWE-22), allowing attackers to write to system directories.

**See Also:** [Pattern 6 Implementation](../SECURITY.md#security-hardening-pattern-6-implementation)

---

### 3. Never Trust User Input

**All user input must be validated:**
- ✅ Type checking
- ✅ Range validation
- ✅ Format validation
- ✅ Sanitization before use

**Example:**
```python
def process_age(age_str: str) -> int:
    # Validate type
    if not isinstance(age_str, str):
        raise TypeError("age must be a string")

    # Validate format
    if not age_str.isdigit():
        raise ValueError("age must be numeric")

    # Validate range
    age = int(age_str)
    if not 0 <= age <= 150:
        raise ValueError("age must be between 0 and 150")

    return age
```

---

## Exception Handling

### 1. Never Use Bare except:

**❌ Prohibited:**
```python
# Masks all errors including KeyboardInterrupt
try:
    risky_operation()
except:  # NEVER do this
    pass
```

**❌ Also Prohibited:**
```python
# Too broad - masks bugs
try:
    risky_operation()
except Exception:  # Too broad in most cases
    return None
```

**✅ Required:**
```python
# Catch specific exceptions
try:
    risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except FileNotFoundError as e:
    logger.warning(f"File not found: {e}")
    return default_value
```

**Rationale:** Broad exception handling masks bugs and makes debugging impossible.

**See Also:** [Exception Handling Best Practices](./EXCEPTION_HANDLING_GUIDE.md)

---

### 2. Always Log Exceptions

**❌ Prohibited:**
```python
try:
    dangerous_operation()
except IOError:
    pass  # Silent failure - impossible to debug
```

**✅ Required:**
```python
try:
    dangerous_operation()
except IOError as e:
    logger.error(f"Failed to perform operation: {e}")
    raise  # Re-raise for caller to handle
```

---

### 3. Exceptions Requiring Broad Catches

Some scenarios justify catching `Exception`, but require documentation:

**✅ Acceptable with Documentation:**
```python
def register_wizard(wizard_id: str, wizard_class: type):
    """Register wizard with graceful degradation.

    Uses broad exception handling intentionally - wizards are optional
    features and the API should start even if some wizards fail.
    """
    try:
        WIZARDS[wizard_id] = wizard_class()
        return True
    except ImportError as e:
        # Missing dependencies for optional wizard
        logger.warning(f"Wizard init failed (missing dependency): {e}")
        return False
    except Exception:  # noqa: BLE001
        # INTENTIONAL: Ensures API starts even if individual wizards fail
        logger.exception(f"Wizard init failed (unexpected error)")
        return False
```

**Requirements:**
1. Add `# INTENTIONAL:` comment explaining why
2. Use `# noqa: BLE001` to suppress linter
3. Call `logger.exception()` to preserve traceback
4. Document in docstring

---

## File Operations

### 1. Always Use Path Validation

**Required for ALL user-controlled file paths:**

```python
from empathy_os.config import _validate_file_path
from pathlib import Path

def save_data(filepath: str, data: dict):
    # Validate before writing
    validated_path = _validate_file_path(filepath)
    validated_path.write_text(json.dumps(data))
```

**What _validate_file_path() checks:**
- ✅ Path is non-empty string
- ✅ No null bytes (`\x00`)
- ✅ Resolves to safe location
- ✅ Not in system directories (`/etc`, `/sys`, `/proc`, `/dev`)
- ✅ Optional directory restriction

---

### 2. Use Context Managers

**❌ Prohibited:**
```python
f = open(filename)
data = f.read()
f.close()  # May not execute if error occurs
```

**✅ Required:**
```python
with open(filename) as f:
    data = f.read()
# File automatically closed even if error occurs
```

---

### 3. Handle File Errors Explicitly

```python
try:
    with open(file_path, 'w') as f:
        f.write(content)
except PermissionError as e:
    logger.error(f"Permission denied writing to {file_path}: {e}")
    raise FileOperationError(f"Cannot write: permission denied") from e
except OSError as e:
    logger.error(f"OS error writing to {file_path}: {e}")
    raise FileOperationError(f"Cannot write: {e}") from e
```

---

## Code Quality

### 1. Type Hints Required

**All functions must have type hints:**

```python
# ✅ Good
def calculate_total(prices: list[float], tax_rate: float) -> float:
    return sum(prices) * (1 + tax_rate)

# ❌ Bad
def calculate_total(prices, tax_rate):
    return sum(prices) * (1 + tax_rate)
```

**Rationale:** Type hints improve code clarity and enable static analysis.

---

### 2. Docstrings Required

**All public functions, classes, and modules must have docstrings:**

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
        >>> validate_email("invalid")
        False
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

**Format:** Google-style docstrings

---

### 3. Maximum Line Length: 100 Characters

**Rationale:** Balances readability with modern screen sizes.

**Configuration:** Already enforced in `.pre-commit-config.yaml` via black formatter.

---

### 4. No Magic Numbers

**❌ Bad:**
```python
if age > 65:
    apply_senior_discount()
```

**✅ Good:**
```python
SENIOR_AGE_THRESHOLD = 65

if age > SENIOR_AGE_THRESHOLD:
    apply_senior_discount()
```

---

## Testing Requirements

### 1. Test Coverage: Minimum 80%

**All new features must include:**
- ✅ Unit tests (80%+ coverage)
- ✅ Edge case tests
- ✅ Error handling tests

```python
def test_divide_by_zero():
    """Test that division by zero raises ValueError."""
    calculator = Calculator()
    with pytest.raises(ValueError, match="cannot divide by zero"):
        calculator.divide(10, 0)
```

---

### 2. Security Tests Required for File Operations

**All file write operations must have security tests:**

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

**See Also:** [test_config_path_security.py](../tests/unit/test_config_path_security.py)

---

### 3. Test Naming Convention

```python
def test_{function_name}_{scenario}_{expected_outcome}():
    """Test description."""
    pass

# Examples:
def test_authenticate_valid_credentials_returns_user():
    """Test authentication succeeds with valid credentials."""
    pass

def test_authenticate_invalid_password_raises_auth_error():
    """Test authentication fails with invalid password."""
    pass
```

---

## Documentation Standards

### 1. All Public APIs Must Be Documented

**Required documentation:**
- ✅ Purpose and use cases
- ✅ Parameters with types
- ✅ Return values
- ✅ Exceptions raised
- ✅ Example usage

---

### 2. Update CHANGELOG.md

**All user-facing changes must be documented in CHANGELOG.md:**

```markdown
## [3.9.1] - 2026-01-07

### Added
- New feature description

### Changed
- Updated feature description

### Fixed
- Bug fix description

### Security
- Security improvement description
```

**Format:** [Keep a Changelog](https://keepachangelog.com/)

---

### 3. Security Changes Must Update SECURITY.md

**All security-related changes must be documented in SECURITY.md**

---

## Enforcement

### Pre-commit Hooks

**Install pre-commit hooks to enforce standards:**

```bash
pre-commit install
```

**What's enforced:**
- ✅ Black formatting (line length, style)
- ✅ Ruff linting (BLE001: no bare except)
- ✅ Bandit security scanning
- ✅ detect-secrets (credential scanning)
- ✅ Trailing whitespace removal
- ✅ YAML/JSON validation

---

### Code Review Checklist

**All pull requests must pass:**

- [ ] No `eval()` or `exec()` usage
- [ ] No bare `except:` or broad `except Exception:`
- [ ] All file paths validated with `_validate_file_path()`
- [ ] Type hints on all functions
- [ ] Docstrings on public APIs
- [ ] Test coverage ≥80%
- [ ] Security tests for file operations
- [ ] CHANGELOG.md updated
- [ ] Pre-commit hooks passing
- [ ] All tests passing

---

### Automated Checks

**GitHub Actions automatically runs:**
- ✅ All tests (pytest)
- ✅ Type checking (mypy)
- ✅ Linting (ruff)
- ✅ Security scanning (bandit)
- ✅ Coverage report

**Status:** Must be green before merge

---

## Violations

### Severity Levels

**CRITICAL** (Must fix immediately):
- `eval()` or `exec()` usage
- Path traversal vulnerabilities
- SQL injection vulnerabilities
- Hardcoded secrets

**HIGH** (Must fix before merge):
- Bare `except:` clauses
- Missing type hints on public APIs
- Test coverage <80%

**MEDIUM** (Should fix):
- Missing docstrings
- Magic numbers
- Long functions (>50 lines)

**LOW** (Nice to fix):
- Style inconsistencies
- Minor optimizations

---

## Examples

### Good Code Example

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

    Example:
        >>> save_configuration("./config.json", {"debug": True})
        Path('/path/to/config.json')
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

### Bad Code Example

```python
def save_configuration(filepath, config):
    f = open(filepath, 'w')
    try:
        data = eval(f"dict({config})")
        json.dump(data, f)
    except:
        pass
    f.close()
```

**What's wrong:**
- ❌ No type hints
- ❌ No docstring
- ❌ No path validation (path traversal vulnerability)
- ❌ Uses `eval()` (code injection vulnerability)
- ❌ Bare `except:` (masks all errors)
- ❌ No logging
- ❌ File not guaranteed to close
- ❌ No error handling

---

## Migration Guide

### For Existing Code

**1. Fix Critical Security Issues**
```bash
# Find eval/exec usage
ruff check src/ --select S307

# Find path traversal risks
grep -r "open(" src/ | grep -v "_validate_file_path"
```

**2. Fix Exception Handling**
```bash
# Find bare except
ruff check src/ --select BLE

# Fix by adding specific exception types
```

**3. Add Type Hints**
```bash
# Use mypy to find missing type hints
mypy src/ --disallow-untyped-defs
```

**4. Improve Test Coverage**
```bash
# Check current coverage
pytest --cov=src --cov-report=term-missing

# Add tests for uncovered code
```

---

## Additional Resources

- [Exception Handling Guide](./EXCEPTION_HANDLING_GUIDE.md)
- [Security Policy](../SECURITY.md)
- [Contributing Guide](../CONTRIBUTING.md)
- [API Reference](./reference/index.md)

---

## Questions?

- **Slack:** #engineering-best-practices
- **GitHub:** [Report an issue](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- **Email:** patrick.roebuck@deepstudyai.com

---

**Maintained By:** Engineering Team
**Last Updated:** January 7, 2026
**Version:** 3.9.1
