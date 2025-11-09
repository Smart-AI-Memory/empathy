# Publishing to PyPI

This guide explains how to publish the Empathy framework to PyPI.

## Prerequisites

1. PyPI account at https://pypi.org/
2. PyPI API token (create at https://pypi.org/manage/account/token/)
3. Add token to GitHub Secrets as `PYPI_API_TOKEN`

## Automated Publishing (Recommended)

The framework uses GitHub Actions for automated publishing:

1. **Update version** in `pyproject.toml`:
   ```toml
   version = "1.7.0"  # Update this
   ```

2. **Update CHANGELOG.md** with release notes

3. **Create and push a git tag**:
   ```bash
   git tag v1.7.0
   git push origin v1.7.0
   ```

4. **GitHub Actions will automatically**:
   - Run all tests
   - Build the package
   - Create a GitHub release
   - Publish to PyPI (if token is configured)

## Manual Publishing

If you need to publish manually:

### 1. Clean previous builds
```bash
rm -rf dist/ build/ *.egg-info
```

### 2. Build the package
```bash
python -m pip install --upgrade build twine
python -m build
```

This creates two files in `dist/`:
- `empathy-1.6.0.tar.gz` (source distribution)
- `empathy-1.6.0-py3-none-any.whl` (wheel distribution)

### 3. Check the package
```bash
twine check dist/*
```

### 4. Test upload to TestPyPI (optional)
```bash
twine upload --repository testpypi dist/*
```

Install from TestPyPI to verify:
```bash
pip install --index-url https://test.pypi.org/simple/ empathy
```

### 5. Upload to PyPI
```bash
twine upload dist/*
```

You'll be prompted for your PyPI username and password/token.

## Verification

After publishing, verify the package:

1. **Check PyPI page**: https://pypi.org/project/empathy/
2. **Install and test**:
   ```bash
   pip install empathy
   python -c "from empathy_os import EmpathyOS; print('Success!')"
   ```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **Major** (1.x.x): Breaking changes
- **Minor** (x.1.x): New features, backward compatible
- **Patch** (x.x.1): Bug fixes, backward compatible

Examples:
- `1.6.0` → `1.6.1`: Bug fix
- `1.6.0` → `1.7.0`: New features
- `1.6.0` → `2.0.0`: Breaking changes

## Troubleshooting

### "Package already exists"
- Version already published to PyPI
- Update version in `pyproject.toml`
- You cannot overwrite or delete PyPI versions

### "Invalid distribution"
- Run `twine check dist/*` to see errors
- Common issues:
  - Missing README.md
  - Invalid pyproject.toml
  - Missing required files in MANIFEST.in

### "Authentication failed"
- Check your PyPI token/password
- Tokens must start with `pypi-`
- Use username `__token__` with API tokens

## Best Practices

1. **Always test locally** before publishing
2. **Run full test suite**: `pytest`
3. **Check code quality**: `black . && ruff check .`
4. **Update documentation** before release
5. **Tag releases** in git for traceability
6. **Never publish** with failing tests

## Package Contents

The published package includes:
- Core framework code (`empathy_os/`, `empathy_llm_toolkit/`)
- All wizards (`wizards/`, `coach_wizards/`)
- Plugins (`empathy_healthcare_plugin/`, `empathy_software_plugin/`)
- Documentation (`README.md`, `LICENSE`, etc.)
- Configuration files

Excluded from package (see MANIFEST.in):
- Tests (`tests/`)
- CI/CD configs (`.github/`)
- Development files (`.gitignore`, `.pre-commit-config.yaml`)
- Backend API (`backend/`)
- Website (`website/`)
