# Bug Prediction Scanner Patterns

This document describes the patterns detected by `empathy workflow run bug-predict` and the smart filtering applied to reduce false positives.

## Detected Patterns

| Pattern | Severity | Description |
|---------|----------|-------------|
| `dangerous_eval` | HIGH | Use of `eval()` or `exec()` on untrusted input |
| `broad_exception` | MEDIUM | Bare `except:` or `except Exception:` that may mask errors |
| `incomplete_code` | LOW | TODO/FIXME comments indicating unfinished work |

## Automatic False Positive Filtering

### dangerous_eval Exclusions

The scanner automatically excludes:

1. **Scanner test files** - Files matching:
   - `test_bug_predict*`
   - `test_scanner*`
   - `test_security_scan*`

2. **Test fixtures** - Code inside `write_text()` calls (test data written to temp files)

3. **Detection code** - String literals like `if "eval(" in content`

4. **JavaScript regex.exec()** - Safe method calls like `pattern.exec(text)`

### broad_exception Exclusions

The scanner uses context analysis to allow acceptable patterns:

1. **Version detection with fallback**
   ```python
   try:
       return get_version("package")
   except Exception:
       return "dev"  # Acceptable: graceful fallback
   ```

2. **Config loading with defaults**
   ```python
   try:
       config = yaml.safe_load(f)
   except Exception:
       pass  # Fall back to default config
   ```

3. **Optional feature detection**
   ```python
   try:
       import optional_lib
   except Exception:
       optional_lib = None
   ```

4. **Cleanup/teardown code**
   - `__del__`, `__exit__`, `cleanup()`, `close()`, `teardown()`

5. **Logging with re-raise**
   ```python
   except Exception as e:
       logger.error(f"Error: {e}")
       raise  # Re-raises after logging
   ```

6. **Intentional comments**
   - `# fallback`, `# optional`, `# best effort`, `# graceful`

## When Reviewing Scanner Results

1. **HIGH severity (dangerous_eval)**: Always investigate - these are security risks
2. **MEDIUM severity (broad_exception)**: Review context - may be acceptable
3. **LOW severity (incomplete_code)**: Track in backlog - not urgent

## Customizing Scanner Behavior

Add exclusions in `empathy.config.yml`:

```yaml
bug_predict:
  exclude_files:
    - "**/test_*.py"
    - "**/fixtures/**"
  acceptable_exception_contexts:
    - version
    - config
    - cleanup
```

## Related Commands

```bash
# Run bug prediction
empathy workflow run bug-predict

# Scan specific directory
empathy workflow run bug-predict --input '{"path":"./src"}'

# JSON output for CI
empathy workflow run bug-predict --json
```
