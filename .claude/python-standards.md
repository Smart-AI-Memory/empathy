# Python Coding Standards

- Use type hints
- Follow PEP 8
- Write docstrings
- Target 90%+ test coverage

## Cross-Platform Compatibility

The Empathy Framework must work on Windows, macOS, and Linux. Follow these guidelines:

### File Paths

- **Always use `pathlib.Path`** instead of string concatenation for paths
- **Never hardcode path separators** (`/` or `\`)
- **Use `empathy_os.platform_utils`** for OS-specific directories:

  ```python
  from empathy_os.platform_utils import get_default_log_dir, get_default_data_dir

  # Good: Platform-appropriate paths
  log_dir = get_default_log_dir()  # ~/Library/Logs/empathy on macOS, %APPDATA%/empathy/logs on Windows

  # Bad: Hardcoded Unix path
  log_dir = Path("/var/log/empathy")
  ```

### File Encoding

- **Always specify `encoding="utf-8"`** when opening text files:

  ```python
  # Good
  with open(path, "r", encoding="utf-8") as f:
      content = f.read()

  # Bad (Windows defaults to cp1252)
  with open(path, "r") as f:
      content = f.read()
  ```

- Use `empathy_os.platform_utils.read_text_file()` and `write_text_file()` for convenience

### Asyncio

- **Call `setup_asyncio_policy()`** before any `asyncio.run()` in CLI entry points:

  ```python
  from empathy_os.platform_utils import setup_asyncio_policy

  def main():
      setup_asyncio_policy()  # Required for Windows compatibility
      asyncio.run(async_main())
  ```

- Windows requires `WindowsSelectorEventLoopPolicy` for compatibility with many libraries

### Line Endings

- Git handles line endings via `.gitattributes`
- When writing files programmatically, use `\n` (Git will convert on checkout)

### Environment Variables

- Use `os.environ.get()` with sensible defaults
- Remember Windows uses different variable names (`%APPDATA%` vs `$HOME`)

### Subprocess Calls

- Use `subprocess.run()` with `shell=False` when possible
- Avoid shell-specific syntax (pipes, redirects) in subprocess calls
- Use `shlex.split()` on Unix, but note it doesn't work on Windows

### Testing

- Mock `platform.system()` to test all OS paths:

  ```python
  with patch("platform.system", return_value="Windows"):
      assert is_windows() is True
  ```

- Run tests on all platforms via CI (see `.github/workflows/tests.yml` - runs on ubuntu, macos, windows)
