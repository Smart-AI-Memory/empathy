# Exception Handling Best Practices

**Version:** 3.9.0
**Purpose:** This guide establishes exception handling patterns for the Empathy Framework to ensure errors are properly caught, logged, and handled.

**Enforcement:** The `BLE` (Blind Exception) linting rule is enabled in `pyproject.toml` to prevent bare `except:` clauses.

---

## Core Principles

1. **Never use bare `except:`** - Always specify exception types
2. **Log at appropriate levels** - Error, Warning, Info, Debug
3. **Fail fast or degrade gracefully** - Choose based on context
4. **Preserve error context** - Use `raise` or `raise from` when re-raising
5. **Don't leak sensitive data** - Sanitize error messages in production

---

## Pattern Templates

### Authentication Operations

```python
from empathy_os.exceptions import AuthenticationError, ServiceUnavailableError

try:
    user = authenticate_user(credentials)
except AuthenticationError as e:
    logger.error(f"Authentication failed for {credentials.username}: {e}")
    raise  # Re-raise - caller must handle auth failures
except DatabaseConnectionError as e:
    logger.critical(f"Database unavailable during authentication: {e}")
    raise ServiceUnavailableError("Authentication service temporarily down")
except ValueError as e:
    logger.warning(f"Invalid credentials format: {e}")
    raise AuthenticationError("Invalid credentials") from e
```

### Security Scanning

```python
from empathy_os.exceptions import SecurityScanException

try:
    vulnerabilities = scan_code(source_code)
except ScannerTimeoutError as e:
    logger.error(f"Security scanner timed out: {e}")
    # Fail secure - treat timeout as potential vulnerability
    return [SecurityIssue("scan_timeout", "Scanner failed to complete")]
except ScannerError as e:
    logger.error(f"Security scanner failed: {e}")
    # Fail secure - report scan failure
    return [SecurityIssue("scan_failed", str(e))]
except OSError as e:
    logger.critical(f"File system error during security scan: {e}")
    raise SecurityScanException(f"Cannot scan file: {e}") from e
```

### Compliance Operations

```python
from empathy_os.exceptions import ComplianceError

try:
    result = validate_compliance(data)
except ComplianceValidationError as e:
    logger.warning(f"Compliance validation failed: {e}")
    # Log for audit trail
    audit_log.record("compliance_failure", user=user_id, reason=str(e))
    return {"status": "failed", "reason": str(e)}
except DataIntegrityError as e:
    logger.error(f"Data integrity issue during compliance check: {e}")
    audit_log.record("data_integrity_error", user=user_id, error=str(e))
    raise ComplianceError("Cannot validate compliance due to data issues") from e
```

### File Operations

```python
import os
from pathlib import Path

try:
    with open(file_path, 'w') as f:
        f.write(content)
except PermissionError as e:
    logger.error(f"Permission denied writing to {file_path}: {e}")
    raise FileOperationError(f"Cannot write to {file_path}: permission denied") from e
except OSError as e:
    if e.errno == errno.ENOSPC:  # No space left on device
        logger.critical(f"Disk full when writing to {file_path}")
        raise FileOperationError("Disk full") from e
    logger.error(f"OS error writing to {file_path}: {e}")
    raise FileOperationError(f"Cannot write to {file_path}") from e
except UnicodeEncodeError as e:
    logger.warning(f"Encoding error writing to {file_path}: {e}")
    # Try fallback encoding
    with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
        f.write(content)
```

### Database Operations

```python
from empathy_os.exceptions import DatabaseError

try:
    result = db.execute(query, params)
except OperationalError as e:
    logger.error(f"Database operational error: {e}")
    # Could be temporary - retry logic here if needed
    raise DatabaseError("Database temporarily unavailable") from e
except IntegrityError as e:
    logger.warning(f"Data integrity violation: {e}")
    raise DatabaseError("Data validation failed") from e
except ProgrammingError as e:
    logger.critical(f"Database programming error: {e}")
    # This indicates a bug in our code
    raise DatabaseError("Internal database error") from e
```

### API/Network Calls

```python
import httpx

try:
    response = httpx.get(url, timeout=30.0)
    response.raise_for_status()
except httpx.TimeoutException as e:
    logger.warning(f"Request to {url} timed out: {e}")
    raise APIError("Service request timed out") from e
except httpx.HTTPStatusError as e:
    logger.error(f"HTTP error {e.response.status_code} from {url}")
    if e.response.status_code == 503:
        raise ServiceUnavailableError("Upstream service unavailable") from e
    raise APIError(f"API request failed: {e.response.status_code}") from e
except httpx.NetworkError as e:
    logger.error(f"Network error calling {url}: {e}")
    raise APIError("Network connectivity issue") from e
```

### Configuration Loading

```python
import yaml

try:
    with open(config_file) as f:
        config = yaml.safe_load(f)
except FileNotFoundError:
    logger.warning(f"Config file {config_file} not found, using defaults")
    return default_config()
except yaml.YAMLError as e:
    logger.error(f"Invalid YAML in {config_file}: {e}")
    raise ConfigurationError(f"Cannot parse config file: {e}") from e
except PermissionError as e:
    logger.error(f"Cannot read {config_file}: permission denied")
    raise ConfigurationError(f"Cannot access config file") from e
```

### Optional Feature Detection

```python
# Acceptable use of broad exception for optional imports
try:
    import optional_library
    HAS_OPTIONAL_FEATURE = True
except ImportError:
    logger.info("Optional library not available, feature disabled")
    optional_library = None
    HAS_OPTIONAL_FEATURE = False
```

### Resource Cleanup

```python
# Context managers handle cleanup automatically - prefer these
with open(file_path) as f:
    data = f.read()

# If you must use try/finally:
file_handle = None
try:
    file_handle = open(file_path)
    data = file_handle.read()
finally:
    if file_handle:
        file_handle.close()
```

---

## Logging Levels

Choose the appropriate level based on severity:

```python
# DEBUG - Detailed diagnostic information
logger.debug(f"Processing item {item_id}")

# INFO - General informational messages
logger.info(f"User {user_id} logged in successfully")

# WARNING - Something unexpected but recoverable
logger.warning(f"Deprecated API version used by {client_id}")

# ERROR - Error that prevented operation from completing
logger.error(f"Failed to process payment {payment_id}: {error}")

# CRITICAL - System-level failure that needs immediate attention
logger.critical(f"Database connection pool exhausted")
```

---

## Anti-Patterns to Avoid

### ❌ DON'T: Bare Except

```python
# BAD - masks all errors
try:
    process_data()
except:
    pass
```

### ❌ DON'T: Catch Exception Without Specific Handling

```python
# BAD - too broad, no specificity
try:
    process_data()
except Exception:
    return None
```

### ❌ DON'T: Silent Failures

```python
# BAD - swallows errors without logging
try:
    save_data(data)
except IOError:
    pass
```

### ❌ DON'T: Leak Sensitive Information

```python
# BAD - exposes internal details
try:
    user = get_user(token)
except AuthError as e:
    # Don't leak SQL or internal errors to user
    return {"error": str(e)}  # BAD
```

### ✅ DO: Use Specific Exceptions

```python
# GOOD
try:
    process_data()
except ValueError as e:
    logger.error(f"Invalid data: {e}")
    raise
except FileNotFoundError as e:
    logger.warning(f"File not found: {e}")
    return default_value
```

---

## Exception Hierarchy

Create custom exceptions for domain-specific errors:

```python
# src/empathy_os/exceptions.py

class EmpathyError(Exception):
    """Base exception for all Empathy Framework errors."""
    pass

class AuthenticationError(EmpathyError):
    """Authentication failed."""
    pass

class AuthorizationError(EmpathyError):
    """User not authorized for operation."""
    pass

class ConfigurationError(EmpathyError):
    """Configuration is invalid or missing."""
    pass

class DatabaseError(EmpathyError):
    """Database operation failed."""
    pass

class FileOperationError(EmpathyError):
    """File operation failed."""
    pass

class SecurityScanException(EmpathyError):
    """Security scan failed."""
    pass

class ComplianceError(EmpathyError):
    """Compliance validation failed."""
    pass

class ServiceUnavailableError(EmpathyError):
    """Required service is unavailable."""
    pass

class APIError(EmpathyError):
    """External API call failed."""
    pass
```

---

## Testing Exception Handling

Always test both success and failure paths:

```python
import pytest

def test_authentication_success():
    user = authenticate_user(valid_credentials)
    assert user.id == expected_id

def test_authentication_failure():
    with pytest.raises(AuthenticationError):
        authenticate_user(invalid_credentials)

def test_database_unavailable():
    with pytest.raises(ServiceUnavailableError):
        authenticate_user_with_dead_database(credentials)

def test_invalid_credentials_format():
    with pytest.raises(AuthenticationError):
        authenticate_user(malformed_credentials)
```

---

## Code Review Checklist

When reviewing code, check for:

- [ ] No bare `except:` clauses
- [ ] Specific exception types are caught
- [ ] Appropriate logging level used
- [ ] Error messages don't leak sensitive data
- [ ] Exceptions are re-raised when appropriate
- [ ] Resource cleanup is handled (use context managers)
- [ ] Tests cover exception paths
- [ ] Documentation describes possible exceptions

---

## Migration Guide

### For Existing Code

1. **Find** bare except clauses:
   ```bash
   ruff check src/ --select BLE
   ```

2. **Analyze** what exceptions can actually be raised:
   ```python
   # Check function documentation
   # Look at implementation
   # Consider edge cases
   ```

3. **Replace** with specific handlers:
   ```python
   # Before
   try:
       result = risky_operation()
   except:
       return None

   # After
   try:
       result = risky_operation()
   except ValueError as e:
       logger.warning(f"Invalid input: {e}")
       return None
   except IOError as e:
       logger.error(f"I/O error: {e}")
       raise
   ```

4. **Test** all exception paths

5. **Document** possible exceptions in docstrings

---

## Real-World Examples from Codebase

### Example 1: Database Connection Management
**File:** `backend/services/database/auth_db.py:46`

```python
@contextmanager
def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
    """Database connection with automatic cleanup and audit trail."""
    conn = None
    try:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        yield conn
        conn.commit()
    except sqlite3.IntegrityError as e:
        # Data integrity violations (duplicate email, constraint violation)
        logger.error(f"Authentication database integrity error: {e}")
        if conn:
            conn.rollback()
        raise  # Re-raise - caller must handle validation
    except sqlite3.OperationalError as e:
        # Database locked, disk full, permission denied
        logger.critical(f"Authentication database operational error: {e}")
        if conn:
            conn.rollback()
        raise  # Re-raise - critical database issue
    except (OSError, IOError) as e:
        # File system errors
        logger.critical(f"Authentication database file system error: {e}")
        if conn:
            conn.rollback()
        raise
    except Exception as e:
        # Unexpected errors - preserve full context for security audit
        logger.exception(f"Unexpected error in authentication database operation: {e}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()
```

### Example 2: Graceful Degradation for Optional Features
**File:** `backend/api/wizard_api.py:117`

```python
def register_wizard(wizard_id: str, wizard_class: type, *args, **kwargs) -> bool:
    """Register wizard with graceful degradation.

    This uses broad exception handling intentionally for graceful degradation.
    Wizards are optional features - the API should start even if some wizards fail.

    Note: Full exception context is preserved via logger.exception() for debugging.
    """
    try:
        WIZARDS[wizard_id] = wizard_class(*args, **kwargs)
        logger.info(f"✓ {wizard_class.__name__} initialized as '{wizard_id}'")
        return True
    except ImportError as e:
        # Missing dependencies - common for optional wizards
        logger.warning(f"{wizard_class.__name__} init failed (missing dependency): {e}")
        return False
    except ValueError as e:
        # Configuration errors - invalid arguments, missing API keys
        logger.warning(f"{wizard_class.__name__} init failed (config error): {e}")
        return False
    except (OSError, IOError) as e:
        # File system errors - missing resources, permission issues
        logger.warning(f"{wizard_class.__name__} init failed (file system error): {e}")
        return False
    except Exception:
        # INTENTIONAL: Ensures API starts even if individual wizards fail
        # Full traceback preserved for debugging
        logger.exception(f"{wizard_class.__name__} init failed (unexpected error)")
        return False
```

### Example 3: Fail-Secure Security Scanning
**File:** `agents/code_inspection/adapters/security_adapter.py:99`

```python
for py_file in self.project_root.rglob("*.py"):
    try:
        vulns = scanner.scan_file(py_file)
        findings.extend(vulns)
    except (OSError, PermissionError) as e:
        # File system errors - log and skip
        logger.warning(f"Cannot access {py_file}: {e}")
        continue
    except UnicodeDecodeError as e:
        # Binary or encoding issues - log and skip
        logger.debug(f"Cannot decode {py_file}: {e}")
        continue
    except (ValueError, RuntimeError, KeyError, IndexError, AttributeError) as e:
        # FAIL-SECURE: Treat scan failures as potential security issues
        logger.error(f"Scanner failed on {py_file}: {e}")
        findings.append({
            "code": "SCAN_FAILURE",
            "severity": "medium",
            "message": f"Security scanner failed: {type(e).__name__}",
            "remediation": "Manual review recommended - scanner could not complete"
        })
```

### Example 4: Health Check with Specific Handlers
**File:** `empathy_llm_toolkit/code_health.py:393`

```python
try:
    if tool == "ruff":
        result = subprocess.run(
            ["ruff", "check", "--output-format=json", str(self.project_root)],
            check=False, capture_output=True, text=True
        )
        ruff_issues = json.loads(result.stdout)
        # Process issues...
except json.JSONDecodeError as e:
    # Tool output not in expected JSON format
    logger.warning(f"Lint check JSON parse error ({tool}): {e}")
    return CheckResult(
        category=CheckCategory.LINT, status=HealthStatus.ERROR,
        score=0, details={"error": f"Failed to parse {tool} output: {e}"}
    )
except subprocess.SubprocessError as e:
    # Tool execution failed
    logger.error(f"Lint check subprocess error ({tool}): {e}")
    return CheckResult(
        category=CheckCategory.LINT, status=HealthStatus.ERROR,
        score=0, details={"error": f"Failed to run {tool}: {e}"}
    )
except Exception as e:
    # INTENTIONAL: Broad handler for graceful degradation of optional check
    logger.exception(f"Unexpected error in lint check ({tool}): {e}")
    return CheckResult(
        category=CheckCategory.LINT, status=HealthStatus.ERROR,
        score=0, details={"error": str(e)}
    )
```

### Example 5: Acceptable Broad Exception with noqa
**File:** `src/empathy_os/cli.py:2041`

```python
# Best-effort serialization for JSON output
try:
    final_output_serializable[k] = str(v)
except Exception as e:  # noqa: BLE001
    # INTENTIONAL: Cannot predict all possible object types users might return
    # This is best-effort serialization for JSON output
    logger.debug(f"Cannot serialize field {k}: {e}")
    pass  # Silently skip non-serializable fields
```

---

## Pre-Commit Hook

The codebase enforces these standards via pre-commit hooks:

```bash
# Install hooks (one-time setup)
pre-commit install

# Run manually before commit
pre-commit run --all-files

# Run only bare exception check
pre-commit run ruff-bare-exception-check --all-files
```

The hook configuration (`.pre-commit-config.yaml`):
```yaml
- id: ruff
  name: ruff-bare-exception-check
  args: ['--select=BLE', '--no-fix']
  # Prevents bare except clauses from being committed
```

---

## Quick Decision Tree

```
Is this an optional feature (wizard, plugin, tip)?
├─ YES → Use graceful degradation pattern (Example 2)
│         - Catch specific exceptions first
│         - Broad Exception as last resort with logger.exception()
│         - Document with comment
│         - Return False/default value
└─ NO → Is this a security-related operation?
    ├─ YES → Use fail-secure pattern (Example 3)
    │         - Log all errors
    │         - Create findings for scan failures
    │         - Never silently skip
    └─ NO → Use specific exception handlers
              - Catch expected exceptions
              - Log at appropriate level
              - Re-raise critical errors
              - Add broad Exception ONLY if:
                  * You log with logger.exception()
                  * You document why
                  * You use # noqa: BLE001
```

---

## References

- [PEP 8 - Programming Recommendations](https://peps.python.org/pep-0008/#programming-recommendations)
- [Python Exception Handling](https://docs.python.org/3/tutorial/errors.html)
- [Ruff BLE Rules](https://docs.astral.sh/ruff/rules/#flake8-blind-except-ble)
- Codebase Examples:
  - [auth_db.py](backend/services/database/auth_db.py) - Database patterns
  - [wizard_api.py](backend/api/wizard_api.py) - Graceful degradation
  - [security_adapter.py](agents/code_inspection/adapters/security_adapter.py) - Fail-secure
  - [code_health.py](empathy_llm_toolkit/code_health.py) - Health checks
  - [cli.py](src/empathy_os/cli.py) - CLI error handling

---

**Last Updated:** January 5, 2026 (Sprint 1 remediation complete)
**Maintained By:** Engineering Team
**Questions?** Ask in #engineering-best-practices
