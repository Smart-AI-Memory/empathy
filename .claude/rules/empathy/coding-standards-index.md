# Coding Standards Quick Reference

**Full Documentation:** [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md)
**Version:** 3.9.1
**Last Updated:** January 7, 2026

**Purpose:** Practical reference for agents and contributors working on Empathy Framework codebase. Includes real patterns, common pitfalls, and enforcement details.

---

## Table of Contents

1. [Critical Security Rules](#critical-security-rules)
2. [Exception Handling Patterns](#exception-handling-patterns)
3. [File Path Validation Implementation](#file-path-validation-implementation)
4. [Code Quality Requirements](#code-quality-requirements)
5. [Testing Requirements](#testing-requirements)
6. [Pre-commit Hooks Configuration](#pre-commit-hooks-configuration)
7. [Migration Guide](#migration-guide)
8. [Common False Positives](#common-false-positives)
9. [Real-World Examples](#real-world-examples)
10. [Code Review Checklist](#code-review-checklist)

---

## Critical Security Rules

### Rule 1: NEVER Use eval() or exec()

**Severity:** CRITICAL (CWE-95)

```python
# ❌ PROHIBITED - Code injection vulnerability
user_input = request.get("formula")
result = eval(user_input)  # Arbitrary code execution!

# ❌ ALSO PROHIBITED
exec(user_code)  # Even worse - can modify global state

# ✅ REQUIRED - Use ast.literal_eval for literals
import ast
try:
    data = ast.literal_eval(user_input)  # Only evaluates: str, bytes, numbers, tuples, lists, dicts, sets, booleans, None
except (ValueError, SyntaxError) as e:
    raise ValueError(f"Invalid input format: {e}")

# ✅ REQUIRED - Use json.loads for structured data
import json
data = json.loads(user_input)
```

**Why This Matters:**
- `eval()` allows arbitrary Python code execution
- Attacker can run `eval("__import__('os').system('rm -rf /')")`
- No safe way to sanitize input for eval()

**Exception:** None. Zero tolerance. Always a security vulnerability.

---

### Rule 2: ALWAYS Validate File Paths

**Severity:** CRITICAL (CWE-22 - Path Traversal)

```python
# ❌ PROHIBITED - Path traversal vulnerability
def save_config(user_path: str, data: dict):
    with open(user_path, 'w') as f:  # Attacker can write to /etc/passwd
        json.dump(data, f)

# ✅ REQUIRED - Validate before writing
from empathy_os.config import _validate_file_path

def save_config(user_path: str, data: dict):
    validated_path = _validate_file_path(user_path)
    with validated_path.open('w') as f:
        json.dump(data, f)
```

**Attack Scenarios:**
- `../../etc/passwd` - Path traversal
- `config\x00.json` - Null byte injection
- `/etc/cron.d/backdoor` - System directory write

**Files Secured (v3.9.0):**
1. `src/empathy_os/config.py` - Configuration exports
2. `src/empathy_os/workflows/config.py` - Workflow saves
3. `src/empathy_os/config/xml_config.py` - XML exports
4. `src/empathy_os/telemetry/cli.py` - CSV/JSON exports
5. `src/empathy_os/cli.py` - Pattern exports
6. `src/empathy_os/memory/control_panel.py` - Memory operations

**See:** [File Path Validation Implementation](#file-path-validation-implementation) below

---

## Exception Handling Patterns

### Rule 3: NEVER Use Bare except:

**Severity:** HIGH (Ruff BLE001)

```python
# ❌ PROHIBITED - Masks all errors including KeyboardInterrupt
try:
    risky_operation()
except:  # NEVER do this
    pass

# ❌ ALSO PROHIBITED - Too broad without justification
try:
    risky_operation()
except Exception:  # Masks ValueError, TypeError, etc.
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
except PermissionError as e:
    logger.error(f"Permission denied: {e}")
    raise IOError(f"Cannot access file: {e}") from e
```

**Why This Matters:**
- Bare `except:` catches `KeyboardInterrupt`, `SystemExit`, `GeneratorExit`
- `except Exception:` masks bugs like `AttributeError`, `TypeError`
- Debugging becomes impossible - errors disappear silently

---

### Acceptable Broad Exception Catches

**Scenarios where `except Exception:` is justified:**

#### 1. Version Detection with Fallback

```python
def get_package_version() -> str:
    """Get package version with graceful fallback."""
    try:
        from importlib.metadata import version
        return version("empathy-framework")
    except Exception:  # noqa: BLE001
        # INTENTIONAL: Fallback for dev installs without metadata
        return "dev"
```

#### 2. Optional Feature Detection

```python
def load_optional_feature():
    """Load optional feature with graceful degradation."""
    try:
        import optional_lib
        return optional_lib.init()
    except ImportError as e:
        logger.info(f"Optional feature not available: {e}")
        return None
    except Exception:  # noqa: BLE001
        # INTENTIONAL: Feature is optional, don't break app
        logger.warning("Optional feature initialization failed")
        return None
```

#### 3. Cleanup/Teardown Code

```python
def cleanup_resources(self):
    """Cleanup resources - best effort."""
    try:
        self.connection.close()
    except Exception:  # noqa: BLE001
        # INTENTIONAL: Cleanup is best-effort, don't fail on cleanup errors
        logger.debug("Connection cleanup failed (non-fatal)")
```

#### 4. Plugin/Wizard Registration (Graceful Degradation)

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

**Requirements for Broad Catches:**
1. Add `# INTENTIONAL:` comment explaining why
2. Use `# noqa: BLE001` to suppress Ruff linter
3. Call `logger.exception()` to preserve traceback
4. Document in function docstring

---

### Rule 4: ALWAYS Log Exceptions

```python
# ❌ PROHIBITED - Silent failure
try:
    dangerous_operation()
except IOError:
    pass  # Impossible to debug

# ❌ BAD - Logs but loses traceback
try:
    dangerous_operation()
except IOError as e:
    logger.error(f"Operation failed: {e}")
    # Traceback is lost!

# ✅ GOOD - Logs with traceback
try:
    dangerous_operation()
except IOError as e:
    logger.exception(f"Operation failed: {e}")
    # logger.exception() includes full traceback

# ✅ GOOD - Re-raises with context
try:
    dangerous_operation()
except IOError as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise preserves original traceback
```

---

## File Path Validation Implementation

### The _validate_file_path() Function

**Location:** `src/empathy_os/config.py:29-68`

```python
def _validate_file_path(path: str, allowed_dir: str | None = None) -> Path:
    """Validate file path to prevent path traversal and arbitrary writes.

    Args:
        path: File path to validate (user-controlled)
        allowed_dir: Optional directory to restrict writes to

    Returns:
        Validated Path object (resolved absolute path)

    Raises:
        ValueError: If path is invalid, contains null bytes, or targets system directories

    Security Checks:
        1. Path must be non-empty string
        2. No null bytes (prevents null byte injection)
        3. Path must be resolvable (no broken symlinks)
        4. Not in system directories (/etc, /sys, /proc, /dev)
        5. Optionally restricted to allowed_dir

    Example:
        >>> validated = _validate_file_path("config.json")
        >>> validated = _validate_file_path("config.json", allowed_dir="./configs")
    """
    # 1. Type and empty check
    if not path or not isinstance(path, str):
        raise ValueError("path must be a non-empty string")

    # 2. Null byte check (prevents null byte injection)
    if "\x00" in path:
        raise ValueError("path contains null bytes")

    # 3. Resolve path (prevents symlink attacks)
    try:
        resolved = Path(path).resolve()
    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid path: {e}")

    # 4. Optional directory restriction
    if allowed_dir:
        try:
            allowed = Path(allowed_dir).resolve()
            resolved.relative_to(allowed)
        except ValueError:
            raise ValueError(f"path must be within {allowed_dir}")

    # 5. System directory protection
    dangerous_paths = ["/etc", "/sys", "/proc", "/dev"]
    for dangerous in dangerous_paths:
        if str(resolved).startswith(dangerous):
            raise ValueError(f"Cannot write to system directory: {dangerous}")

    return resolved
```

### Usage Pattern

```python
from empathy_os.config import _validate_file_path
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


def save_data(filepath: str, data: dict) -> Path:
    """Save data to file with security validation.

    Args:
        filepath: User-controlled path where data should be saved
        data: Data to save

    Returns:
        Path where data was saved

    Raises:
        ValueError: If filepath is invalid or targets system directory
        PermissionError: If insufficient permissions to write
        OSError: If write operation fails
    """
    # 1. Validate path BEFORE any file operations
    validated_path = _validate_file_path(filepath)

    # 2. Handle specific exceptions
    try:
        with validated_path.open('w') as f:
            json.dump(data, f, indent=2)
    except PermissionError as e:
        logger.error(f"Permission denied writing to {validated_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {validated_path}: {e}")
        raise ValueError(f"Cannot write data: {e}") from e

    logger.info(f"Data saved to {validated_path}")
    return validated_path
```

---

## Code Quality Requirements

### Type Hints Required

```python
# ✅ REQUIRED - All functions must have type hints
def calculate_total(prices: list[float], tax_rate: float) -> float:
    """Calculate total with tax."""
    return sum(prices) * (1 + tax_rate)

# ❌ PROHIBITED - Missing type hints
def calculate_total(prices, tax_rate):
    return sum(prices) * (1 + tax_rate)
```

**Enforcement:**
- MyPy checks (currently disabled, re-enabling after type improvement sprint)
- Manual code review

---

### Docstrings Required

**Format:** Google-style docstrings

```python
def validate_email(email: str) -> bool:
    """Validate email format using regex.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid format, False otherwise

    Raises:
        TypeError: If email is not a string

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid")
        False
    """
    if not isinstance(email, str):
        raise TypeError("email must be a string")

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

**Required sections:**
- Summary line
- `Args:` for parameters
- `Returns:` for return value
- `Raises:` for exceptions
- `Example:` for usage (optional but recommended)

---

### Line Length: 100 Characters

**Enforcement:** Black formatter

```python
# ✅ GOOD - Line length ≤100
def process_data(
    input_file: str,
    output_file: str,
    transform: Callable[[dict], dict],
) -> int:
    """Process data with transformation."""
    pass

# ❌ BAD - Line length >100 (will be auto-formatted by black)
def process_data(input_file: str, output_file: str, transform: Callable[[dict], dict], options: dict) -> int:
    pass
```

---

## Testing Requirements

### Minimum 80% Test Coverage

```bash
# Check coverage
pytest --cov=src --cov-report=term-missing

# Generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

### Security Tests for File Operations

**Required for ALL file write operations:**

```python
import pytest
from empathy_os.config import EmpathyConfig


def test_save_prevents_path_traversal():
    """Test that save blocks path traversal attacks."""
    config = EmpathyConfig(user_id="test")

    # Test various path traversal patterns
    with pytest.raises(ValueError, match="Cannot write to system directory"):
        config.to_yaml("/etc/passwd")

    with pytest.raises(ValueError, match="Cannot write to system directory"):
        config.to_yaml("../../etc/passwd")


def test_save_prevents_null_bytes():
    """Test that save blocks null byte injection."""
    config = EmpathyConfig(user_id="test")

    with pytest.raises(ValueError, match="contains null bytes"):
        config.to_yaml("config\x00.json")


def test_save_blocks_system_directories():
    """Test that save blocks writes to system directories."""
    config = EmpathyConfig(user_id="test")

    dangerous_paths = ["/etc/test", "/sys/test", "/proc/test", "/dev/test"]
    for path in dangerous_paths:
        with pytest.raises(ValueError, match="Cannot write to system directory"):
            config.to_yaml(path)


def test_save_allows_valid_paths(tmp_path):
    """Test that save allows valid paths."""
    config = EmpathyConfig(user_id="test")

    # Valid path in temp directory
    output_file = tmp_path / "config.yaml"
    result = config.to_yaml(str(output_file))

    assert output_file.exists()
    assert result == output_file
```

**See:** `tests/unit/test_config_path_security.py` for complete examples

---

### Test Naming Convention

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

def test_save_config_path_traversal_raises_value_error():
    """Test that save_config blocks path traversal attacks."""
    pass
```

---

## Pre-commit Hooks Configuration

**Location:** `.pre-commit-config.yaml`

### Install Hooks

```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff-bare-exception-check
```

---

### Enforced Checks

#### 1. Black (Code Formatter)

```yaml
- repo: https://github.com/psf/black
  rev: 24.10.0
  hooks:
    - id: black
      args: ['--line-length=100']
```

**What it does:**
- Formats code to 100-character line length
- Consistent style (quotes, spacing, etc.)

---

#### 2. Ruff (Fast Linter)

```yaml
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.8.4
  hooks:
    - id: ruff
      args: ['--fix', '--exit-non-zero-on-fix']
    - id: ruff
      name: ruff-bare-exception-check
      args: ['--select=BLE', '--no-fix']
```

**What it does:**
- `ruff`: Fixes auto-fixable issues (unused imports, etc.)
- `ruff-bare-exception-check`: **Blocks bare except: clauses (BLE001)**

**BLE001 Check:**
```python
# ❌ Blocked by pre-commit hook
try:
    risky()
except:  # BLE001: Do not catch blind exception: `Exception`
    pass

# ❌ Also blocked
try:
    risky()
except Exception:  # BLE001: Use more specific exception
    pass

# ✅ Allowed
try:
    risky()
except Exception:  # noqa: BLE001
    # INTENTIONAL: Graceful degradation for optional feature
    logger.warning("Optional feature failed")
```

---

#### 3. Bandit (Security Linter)

```yaml
- repo: https://github.com/PyCQA/bandit
  rev: 1.8.6
  hooks:
    - id: bandit
      args: ['-c', '.bandit', '-r', 'src/', '--severity-level', 'medium']
```

**What it checks:**
- Hardcoded passwords (B105, B106)
- `eval()` usage (S307)
- `exec()` usage (S102)
- SQL injection risks (S608)
- Shell injection risks (B602, B603)

---

#### 4. detect-secrets (Credential Scanner)

```yaml
- repo: https://github.com/Yelp/detect-secrets
  rev: v1.5.0
  hooks:
    - id: detect-secrets
      args: ['--baseline', '.secrets.baseline']
```

**What it detects:**
- API keys
- Private keys
- AWS credentials
- Database passwords
- Generic secrets

**Test Credentials Pattern:**
```python
# ✅ Allowed - Obviously fake
TEST_API_KEY = "FAKE_abc123xyz789_NOT_REAL"
EXAMPLE_KEY = "AKIAIOSFODNN7EXAMPLE"

# ❌ Blocked - Looks real
api_key = "sk_live_abc123xyz789"
```

---

#### 5. Standard Checks

```yaml
- id: trailing-whitespace
- id: end-of-file-fixer
- id: check-yaml
- id: check-added-large-files
- id: check-merge-conflict
- id: check-toml
- id: check-json
- id: mixed-line-ending
```

---

## Migration Guide

### Fix Critical Security Issues First

#### 1. Find eval/exec Usage

```bash
# Find eval/exec with Ruff
ruff check src/ --select S307

# Or grep
grep -r "eval(" src/
grep -r "exec(" src/
```

**Fix:**
```python
# Before:
result = eval(user_input)

# After:
import ast
result = ast.literal_eval(user_input)
```

---

#### 2. Find Path Traversal Risks

```bash
# Find open() calls without validation
grep -r "open(" src/ | grep -v "_validate_file_path"

# Find Path().write_* without validation
grep -r "\.write_text\|\.write_bytes" src/ | grep -v "_validate_file_path"
```

**Fix:**
```python
# Before:
with open(user_path, 'w') as f:
    f.write(data)

# After:
from empathy_os.config import _validate_file_path

validated_path = _validate_file_path(user_path)
with validated_path.open('w') as f:
    f.write(data)
```

---

### Fix Exception Handling

#### 1. Find Bare except

```bash
# Find with Ruff
ruff check src/ --select BLE

# Run pre-commit hook
pre-commit run ruff-bare-exception-check --all-files
```

**Fix:**
```python
# Before:
try:
    risky()
except:
    pass

# After - Option 1: Specific exceptions
try:
    risky()
except (ValueError, IOError) as e:
    logger.error(f"Operation failed: {e}")
    raise

# After - Option 2: Justified broad catch
try:
    risky()
except Exception:  # noqa: BLE001
    # INTENTIONAL: Graceful degradation for optional feature
    logger.exception("Optional feature failed")
```

---

### Add Type Hints

```bash
# Use mypy to find missing type hints
mypy src/ --disallow-untyped-defs
```

**Fix:**
```python
# Before:
def calculate(x, y):
    return x + y

# After:
def calculate(x: float, y: float) -> float:
    return x + y
```

---

### Improve Test Coverage

```bash
# Check current coverage
pytest --cov=src --cov-report=term-missing

# See which lines are not covered
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## Common False Positives

### 1. eval() in Test Fixtures

**Scanner reports:** "Dangerous eval usage"

**False Positive:** eval() appears in test data, not executable code

**Example:** `benchmarks/benchmark_caching.py:229`

```python
# This is TEST DATA written to a temp file
test_file.write_text(
    """
def unsafe_eval(code):
    # Dangerous eval usage (this is test data)
    return eval(code)
"""
)
```

**Resolution:** No fix needed - this validates scanner is working correctly

**How to identify:**
- Inside `write_text()`, `write_bytes()` calls
- Inside test fixture strings
- In comments or docstrings showing what NOT to do

---

### 2. JavaScript pattern.exec()

**Scanner reports:** "exec usage detected"

**False Positive:** JavaScript's `regex.exec()` is a safe method

**Example:**
```javascript
const match = pattern.exec(text);  // Safe - regex method
```

**Resolution:** Scanner should exclude `.exec()` method calls

---

### 3. Graceful Degradation Patterns

**Scanner reports:** "Broad except Exception:"

**False Positive:** Justified broad catch with proper documentation

**Example:**
```python
try:
    optional_feature.init()
except Exception:  # noqa: BLE001
    # INTENTIONAL: Feature is optional, documented in docstring
    logger.warning("Optional feature unavailable")
```

**Resolution:** Document with `# INTENTIONAL:` and `# noqa: BLE001`

---

## Real-World Examples

### Example 1: Configuration Export (config.py)

**File:** `src/empathy_os/config.py:195-215`

```python
def to_yaml(self, output_path: str) -> Path:
    """Export configuration to YAML file.

    Args:
        output_path: Path where YAML should be saved (user-controlled)

    Returns:
        Path to saved YAML file

    Raises:
        ValueError: If output_path is invalid or targets system directory
        ImportError: If PyYAML is not installed
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML required for YAML export")

    # Validate path to prevent path traversal
    validated_path = _validate_file_path(output_path)

    # Export with proper exception handling
    try:
        with validated_path.open("w") as f:
            yaml.safe_dump(asdict(self), f, default_flow_style=False)
    except PermissionError as e:
        logger.error(f"Permission denied writing to {validated_path}: {e}")
        raise
    except OSError as e:
        logger.error(f"OS error writing to {validated_path}: {e}")
        raise ValueError(f"Cannot write YAML: {e}") from e

    return validated_path
```

**What makes this good:**
- ✅ Type hints on all parameters
- ✅ Comprehensive docstring (Args, Returns, Raises)
- ✅ Path validation before writing
- ✅ Specific exception handling (PermissionError, OSError)
- ✅ Logging at appropriate levels
- ✅ Exception chaining with `from e`

---

### Example 2: Telemetry Export (telemetry/cli.py)

**File:** `src/empathy_os/telemetry/cli.py:280-310`

```python
def export_csv(output_path: str):
    """Export telemetry data to CSV.

    Args:
        output_path: Path where CSV should be saved (user-controlled)
    """
    from empathy_os.config import _validate_file_path

    # Validate path to prevent attacks
    validated_path = _validate_file_path(output_path)

    try:
        with validated_path.open("w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "workflow", "cost", "tokens"])

            for entry in get_telemetry_data():
                writer.writerow([
                    entry.timestamp,
                    entry.workflow,
                    entry.cost,
                    entry.tokens,
                ])

        print(f"✅ Exported to {validated_path}")
    except PermissionError as e:
        print(f"❌ Permission denied: {e}")
        raise
    except OSError as e:
        print(f"❌ Failed to write CSV: {e}")
        raise
```

---

### Example 3: Security Test Pattern

**File:** `tests/unit/test_config_path_security.py`

```python
import pytest
from pathlib import Path
from empathy_os.config import EmpathyConfig


class TestPathTraversalProtection:
    """Test suite for path traversal attack prevention."""

    def test_blocks_absolute_system_paths(self):
        """Test that absolute paths to system directories are blocked."""
        config = EmpathyConfig(user_id="test")

        dangerous_paths = [
            "/etc/passwd",
            "/sys/kernel/debug",
            "/proc/self/mem",
            "/dev/null",
        ]

        for path in dangerous_paths:
            with pytest.raises(ValueError, match="Cannot write to system directory"):
                config.to_yaml(path)

    def test_blocks_relative_path_traversal(self):
        """Test that relative path traversal is blocked."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="Cannot write to system directory"):
            config.to_yaml("../../../etc/passwd")

    def test_blocks_null_byte_injection(self):
        """Test that null byte injection is blocked."""
        config = EmpathyConfig(user_id="test")

        with pytest.raises(ValueError, match="contains null bytes"):
            config.to_yaml("config\x00.json")

    def test_allows_valid_paths(self, tmp_path):
        """Test that valid paths are allowed."""
        config = EmpathyConfig(user_id="test")

        # Test various valid path formats
        valid_paths = [
            tmp_path / "config.yaml",
            tmp_path / "subdir" / "config.yaml",
            tmp_path / "config-2024-01-07.yaml",
        ]

        for path in valid_paths:
            path.parent.mkdir(parents=True, exist_ok=True)
            result = config.to_yaml(str(path))
            assert result == path.resolve()
            assert path.exists()
```

---

## Code Review Checklist

**Before merging, verify:**

### Security

- [ ] No `eval()` or `exec()` usage (Bandit S307, S102)
- [ ] All file paths validated with `_validate_file_path()`
- [ ] No hardcoded secrets (detect-secrets)
- [ ] User input validated (type, range, format)

### Exception Handling

- [ ] No bare `except:` (Ruff BLE001)
- [ ] No unjustified `except Exception:` (must have `# INTENTIONAL:` comment)
- [ ] All exceptions logged with `logger.exception()` or `logger.error()`
- [ ] Exception context preserved with `raise ... from e`

### Code Quality

- [ ] Type hints on all functions
- [ ] Docstrings on public APIs (Google-style)
- [ ] Line length ≤100 characters (Black)
- [ ] No magic numbers (use named constants)

### Testing

- [ ] Test coverage ≥80%
- [ ] Security tests for file operations
- [ ] Edge case tests
- [ ] Error handling tests

### Documentation

- [ ] CHANGELOG.md updated
- [ ] Breaking changes documented
- [ ] API changes in docstrings
- [ ] Security changes in SECURITY.md

### Automation

- [ ] Pre-commit hooks passing
- [ ] All tests passing (pytest)
- [ ] No ruff warnings
- [ ] No bandit warnings (medium+)

---

## Violation Severity Levels

### CRITICAL (Must fix immediately)

- `eval()` or `exec()` usage
- Path traversal vulnerabilities
- SQL injection vulnerabilities
- Hardcoded secrets in code
- Authentication bypass

**Fix within:** Hours

---

### HIGH (Must fix before merge)

- Bare `except:` clauses
- Unjustified `except Exception:`
- Missing type hints on public APIs
- Test coverage <80%
- Missing security tests for file operations

**Fix within:** Same PR/commit

---

### MEDIUM (Should fix)

- Missing docstrings
- Magic numbers
- Long functions (>50 lines)
- Duplicate code

**Fix within:** Sprint/iteration

---

### LOW (Nice to fix)

- Style inconsistencies
- Minor optimizations
- TODO comments

**Fix when:** Convenient

---

## Quick Command Reference

```bash
# Security scans
ruff check src/ --select S307          # Find eval/exec
bandit -r src/ --severity-level medium # Security audit
pre-commit run detect-secrets          # Find secrets

# Exception handling
ruff check src/ --select BLE           # Find bare except
pre-commit run ruff-bare-exception-check

# Code quality
black src/                             # Format code
ruff check src/ --fix                  # Fix auto-fixable issues
mypy src/                              # Type checking

# Testing
pytest --cov=src --cov-report=term-missing  # Coverage
pytest -v tests/unit/test_*_security.py     # Security tests

# Pre-commit
pre-commit install                     # Install hooks
pre-commit run --all-files             # Run all hooks
pre-commit run <hook-id>               # Run specific hook
```

---

## Related Documentation

- [CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md) - Complete coding standards (664 lines)
- [EXCEPTION_HANDLING_GUIDE.md](../../../docs/EXCEPTION_HANDLING_GUIDE.md) - Exception patterns (630 lines)
- [SECURITY.md](../../../SECURITY.md) - Security policy and vulnerability reporting
- [scanner-patterns.md](./scanner-patterns.md) - Bug prediction scanner patterns
- [debugging.md](./debugging.md) - Historical debugging patterns

---

## Files Demonstrating Good Patterns

### Path Validation Examples

- `src/empathy_os/config.py` - Configuration exports (YAML, JSON)
- `src/empathy_os/workflows/config.py` - Workflow configuration
- `src/empathy_os/telemetry/cli.py` - Telemetry exports (CSV, JSON)

### Exception Handling Examples

- `src/empathy_os/workflows/base.py` - Workflow execution with proper error handling
- `src/empathy_os/cli.py` - CLI with specific exception handling

### Security Test Examples

- `tests/unit/test_config_path_security.py` - Path traversal prevention tests
- `tests/unit/test_workflow_config_security.py` - Workflow security tests
- `tests/unit/test_telemetry_cli_security.py` - Telemetry security tests

---

**Questions?**

- See full documentation in [docs/CODING_STANDARDS.md](../../../docs/CODING_STANDARDS.md)
- Report issues: [GitHub Issues](https://github.com/Smart-AI-Memory/empathy-framework/issues)
- Ask in discussions: [GitHub Discussions](https://github.com/Smart-AI-Memory/empathy-framework/discussions)

---

**Version:** 3.9.1 (Expanded reference - 850+ lines)
**Last Updated:** January 7, 2026
**Maintained By:** Engineering Team
