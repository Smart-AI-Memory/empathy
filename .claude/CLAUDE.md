# Project Memory

## Framework
This is the Empathy Framework v3.9.1

@./python-standards.md

## Coding Standards
@./rules/empathy/coding-standards-index.md

Critical rules enforced across all code:

- NEVER use eval() or exec()
- ALWAYS validate file paths with _validate_file_path()
- NEVER use bare except: - catch specific exceptions
- ALWAYS log exceptions before handling
- Type hints and docstrings required on all public APIs
- Minimum 80% test coverage
- Security tests required for file operations

## Additional Notes
Memory integration test


## New Section
Added after initialization for reload test
