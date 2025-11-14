# Publishing Guide for Empathy

This guide covers how to build and publish the Empathy package to PyPI.

## Prerequisites

1. **PyPI Account**: Create accounts on both:
   - [TestPyPI](https://test.pypi.org/account/register/) (for testing)
   - [PyPI](https://pypi.org/account/register/) (for production)

2. **API Tokens**: Create API tokens for both services:
   - TestPyPI: https://test.pypi.org/manage/account/token/
   - PyPI: https://pypi.org/manage/account/token/
   - Store tokens securely (they're only shown once!)

3. **Install Build Tools**:
   ```bash
   pip install build twine
   ```

## Building the Package

### 1. Update Version

Edit version in [`pyproject.toml`](pyproject.toml):
```toml
[project]
version = "1.5.0"  # Update this
```

### 2. Clean Previous Builds

```bash
rm -rf dist/ build/ *.egg-info
```

### 3. Build Distribution Files

```bash
python -m build
```

This creates:
- `dist/empathy-1.5.0.tar.gz` (source distribution)
- `dist/empathy-1.5.0-py3-none-any.whl` (wheel distribution)

### 4. Verify Package Contents

```bash
# Check what's in the wheel
unzip -l dist/empathy-1.5.0-py3-none-any.whl

# Check what's in the source distribution
tar -tzf dist/empathy-1.5.0.tar.gz
```

## Testing the Package

### 1. Upload to TestPyPI

```bash
twine upload --repository testpypi dist/*
```

When prompted:
- Username: `__token__`
- Password: Your TestPyPI API token (starts with `pypi-`)

### 2. Test Installation from TestPyPI

Create a fresh virtual environment and test:

```bash
# Create test environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ empathy[full]

# Test import
python -c "from empathy_os import EmpathyOS; print('Success!')"

# Deactivate and clean up
deactivate
rm -rf test_env
```

**Note**: The `--extra-index-url` is needed because TestPyPI doesn't have all dependencies.

## Publishing to Production PyPI

### 1. Final Checks

- [ ] All tests passing (`pytest`)
- [ ] Coverage meets requirements (`pytest --cov`)
- [ ] Security scan clean (`bandit -r src/`)
- [ ] Pre-commit hooks passing (`pre-commit run --all-files`)
- [ ] Version number updated in [`pyproject.toml`](pyproject.toml)
- [ ] [`CHANGELOG.md`](CHANGELOG.md) updated with release notes
- [ ] Documentation up to date

### 2. Upload to PyPI

```bash
twine upload dist/*
```

When prompted:
- Username: `__token__`
- Password: Your PyPI API token (starts with `pypi-`)

### 3. Verify on PyPI

Visit: https://pypi.org/project/empathy/

### 4. Test Production Installation

```bash
# Create fresh environment
python -m venv verify_env
source verify_env/bin/activate

# Install from PyPI
pip install empathy-framework[full]

# Verify
python -c "from empathy_os import EmpathyOS; print('Production package works!')"

# Clean up
deactivate
rm -rf verify_env
```

### 5. Create Git Tag and GitHub Release

```bash
# Create and push tag
git tag -a v1.5.0 -m "Release version 1.5.0"
git push origin v1.5.0
```

The GitHub Actions workflow ([`.github/workflows/release.yml`](.github/workflows/release.yml)) will automatically:
- Create a GitHub Release
- Upload distribution files
- Publish to PyPI (if `PYPI_API_TOKEN` secret is configured)

## GitHub Actions Automation

### Setting up PyPI Token in GitHub

1. Go to: `https://github.com/Smart-AI-Memory/empathy-framework/settings/secrets/actions`
2. Click "New repository secret"
3. Name: `PYPI_API_TOKEN`
4. Value: Your PyPI API token
5. Click "Add secret"

### Automated Release Process

Once the token is configured, releases are automatic:

```bash
# Just push a version tag
git tag v1.5.0
git push origin v1.5.0
```

GitHub Actions will:
1. Build the package
2. Run tests
3. Create GitHub Release
4. Publish to PyPI

## Installation Options Reference

After publishing, users can install with:

```bash
# Minimal installation
pip install empathy-framework

# Transformative stack (recommended)
pip install empathy-framework[full]

# Specific components
pip install empathy-framework[llm]       # LLM providers
pip install empathy-framework[memdocs]   # MemDocs integration
pip install empathy-framework[agents]    # LangChain agents
pip install empathy-framework[all]       # Everything + dev tools

# Development
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy
pip install -e .[dev]
```

## Package Structure

```
empathy/
├── pyproject.toml          # Modern package configuration
├── setup.py               # Legacy support (optional)
├── MANIFEST.in            # Include/exclude files
├── README.md              # PyPI project description
├── LICENSE                # Fair Source 0.9
├── src/
│   └── empathy_os/        # Main package
├── empathy_llm_toolkit/   # LLM integrations
├── empathy_software_plugin/
├── empathy_healthcare_plugin/
├── coach_wizards/
├── wizards/
├── agents/
└── tests/
```

## Troubleshooting

### "File already exists" error on PyPI

You cannot re-upload the same version. Either:
- Increment version number
- Delete the release from PyPI (not recommended)

### Missing dependencies in wheel

Check [`MANIFEST.in`](MANIFEST.in) includes all necessary files.

### Import errors after installation

Verify package structure in [`pyproject.toml`](pyproject.toml):
```toml
[tool.setuptools]
packages = ["empathy_os", "empathy_llm_toolkit", ...]
```

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):

- **1.0.0** → **1.0.1**: Bug fixes (PATCH)
- **1.0.0** → **1.1.0**: New features, backward compatible (MINOR)
- **1.0.0** → **2.0.0**: Breaking changes (MAJOR)

## Resources

- [Python Packaging Guide](https://packaging.python.org/)
- [PyPI Help](https://pypi.org/help/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [setuptools Documentation](https://setuptools.pypa.io/)

## License

When publishing, ensure the Fair Source License 0.9 is properly included in the distribution package. The license automatically converts to Apache 2.0 on January 1, 2029.

---

**Need help?** Contact [support@smartaimemory.com](mailto:support@smartaimemory.com)
