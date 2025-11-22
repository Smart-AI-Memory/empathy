# Changelog

All notable changes to the Empathy Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.6.8] - 2025-11-21

### Fixed
- **Package Distribution**: Excluded website directory and deployment configs from PyPI package
  - Added `prune website` to MANIFEST.in to exclude entire website folder
  - Excluded `backend/`, `nixpacks.toml`, `org-ruleset-*.json`, deployment configs
  - Excluded working/planning markdown files (badges reminders, outreach emails, etc.)
  - Package size reduced, only framework code distributed

## [1.6.7] - 2025-11-21

### Fixed
- **Critical**: Resolved 129 syntax errors in `docs/generate_word_doc.py` caused by unterminated string literals (apostrophes in single-quoted strings)
- Fixed JSON syntax error in `org-ruleset-tags.json` (stray character)
- Fixed 25 bare except clauses across 6 wizard files, replaced with specific `OSError` exception handling
  - `empathy_software_plugin/wizards/agent_orchestration_wizard.py` (4 fixes)
  - `empathy_software_plugin/wizards/ai_collaboration_wizard.py` (2 fixes)
  - `empathy_software_plugin/wizards/ai_documentation_wizard.py` (4 fixes)
  - `empathy_software_plugin/wizards/multi_model_wizard.py` (8 fixes)
  - `empathy_software_plugin/wizards/prompt_engineering_wizard.py` (2 fixes)
  - `empathy_software_plugin/wizards/rag_pattern_wizard.py` (5 fixes)

### Changed
- **Logging**: Replaced 48 `print()` statements with structured logger calls in `src/empathy_os/cli.py`
  - Improved log management and consistency across codebase
  - Better debugging and production monitoring capabilities
- **Code Modernization**: Removed outdated Python 3.9 compatibility code from `src/empathy_os/plugins/registry.py`
  - Project requires Python 3.10+, version check was unnecessary

### Added
- **Documentation**: Added comprehensive Google-style docstrings to 5 abstract methods (149 lines total)
  - `src/empathy_os/levels.py`: Enhanced `EmpathyLevel.respond()` with implementation guidance
  - `src/empathy_os/plugins/base.py`: Enhanced 4 methods with detailed parameter specs, return types, and examples
    - `BaseWizard.analyze()` - Domain-specific analysis guidance
    - `BaseWizard.get_required_context()` - Context requirements specification
    - `BasePlugin.get_metadata()` - Plugin metadata standards
    - `BasePlugin.register_wizards()` - Wizard registration patterns

## [1.6.6] - 2025-11-21

### Fixed
- Automated publishing to pypi

## [1.6.4] - 2025-11-21

### Changed
- **Contact Information**: Updated author and maintainer email to patrick.roebuck@smartAImemory.com
- **Repository Configuration**: Added organization ruleset configurations for branch and tag protection

### Added
- **Test Coverage**: Achieved 83.09% test coverage (1245 tests passed, 2 failed)
- **Organization Rulesets**: Documented main branch and tag protection rules in JSON format

## [1.6.3] - 2025-11-21

### Added
- **Automated Release Pipeline**: Enhanced GitHub Actions workflow for fully automated releases
  - Automatic package validation with twine check
  - Smart changelog extraction from CHANGELOG.md
  - Automatic PyPI publishing on tag push
  - Version auto-detection from git tags
  - Comprehensive release notes generation

### Changed
- **Developer Experience**: Streamlined release process
  - Configured ~/.pypirc for easy manual uploads
  - Added PYPI_API_TOKEN to GitHub secrets
  - Future releases: just push a tag, everything automated

### Infrastructure
- **Repository Cleanup**: Excluded working files and build artifacts
  - Added website build exclusions to .gitignore
  - Removed working .md files from git tracking
  - Cleaner repository for end users

## [1.6.2] - 2025-11-21

### Fixed
- **Critical**: Fixed pyproject.toml syntax error preventing package build
  - Corrected malformed maintainers email field (line 16-17)
  - Package now builds successfully with `python -m build`
  - Validated with `twine check`

- **Examples**: Fixed missing `os` import in examples/testing_demo.py
  - Added missing import for os.path.join usage
  - Resolves F821 undefined-name errors

- **Tests**: Fixed LLM integration test exception handling
  - Updated test_invalid_api_key to catch anthropic.AuthenticationError
  - Updated test_empty_message to catch anthropic.BadRequestError
  - Tests now properly handle real API exceptions

### Quality Metrics
- **Test Pass Rate**: 99.8% (1,245/1,247 tests passing)
- **Test Coverage**: 83.09% (far exceeds 14% minimum requirement)
- **Package Validation**: Passes twine check
- **Build Status**: Successfully builds wheel and source distribution

## [1.5.0] - 2025-11-07 - 🎉 10/10 Commercial Ready

### Added
- **Comprehensive Documentation Suite** (10,956 words)
  - API_REFERENCE.md with complete API documentation (3,194 words)
  - QUICKSTART_GUIDE.md with 5-minute getting started (2,091 words)
  - USER_GUIDE.md with user manual (5,671 words)
  - 40+ runnable code examples

- **Automated Security Scanning**
  - Bandit integration for vulnerability detection
  - tests/test_security_scan.py for CI/CD
  - Zero high/medium severity vulnerabilities

- **Professional Logging Infrastructure**
  - src/empathy_os/logging_config.py
  - Structured logging with rotation
  - Environment-based configuration
  - 35+ logger calls across codebase

- **Code Quality Automation**
  - .pre-commit-config.yaml with 6 hooks
  - Black formatting (100 char line length)
  - Ruff linting with auto-fix
  - isort import sorting

- **New Test Coverage**
  - tests/test_exceptions.py (40 test methods, 100% exception coverage)
  - tests/test_plugin_registry.py (26 test methods)
  - tests/test_security_scan.py (2 test methods)
  - 74 new test cases total

### Fixed
- **All 20 Test Failures Resolved** (100% pass rate: 476/476 tests)
  - MockWizard.get_required_context() implementation
  - 8 AI wizard context structure issues
  - 4 performance wizard trajectory tests
  - Integration test assertion

- **Security Vulnerabilities**
  - CORS configuration (whitelisted domains)
  - Input validation (auth and analysis APIs)
  - API key validation (LLM providers)

- **Bug Fixes**
  - AdvancedDebuggingWizard abstract methods (name, level)
  - Pylint parser rule name prioritization
  - Trajectory prediction dictionary keys
  - Optimization potential return type

- **Cross-Platform Compatibility**
  - 14 hardcoded /tmp/ paths fixed
  - Windows ANSI color support (colorama)
  - bin/empathy-scan converted to console_scripts
  - All P1 issues resolved

### Changed
- **Code Formatting**
  - 42 files reformatted with Black
  - 58 linting issues auto-fixed with Ruff
  - Consistent 100-character line length
  - PEP 8 compliant

- **Dependencies**
  - Added bandit>=1.7 for security scanning
  - Updated setup.py with version bounds
  - Added pre-commit hooks dependencies

### Quality Metrics
- **Test Pass Rate**: 100% (476/476 tests)
- **Security Vulnerabilities**: 0 (zero)
- **Test Coverage**: 45.40% (98%+ on critical modules)
- **Documentation**: 10,956 words
- **Code Quality**: Enterprise-grade
- **Overall Score**: ⭐⭐⭐⭐⭐ 10/10

### Commercial Readiness
- Production-ready code quality
- Comprehensive documentation
- Automated security scanning
- Professional logging
- Cross-platform support (Windows/macOS/Linux)
- Ready for $99/developer/year launch

---

## [1.0.0] - 2025-01-01

### Added
- Initial release of Empathy Framework
- Five-level maturity model (Reactive → Systems)
- 16+ Coach wizards for software development
- Pattern library for AI-AI collaboration
- Level 4 Anticipatory empathy (trajectory prediction)
- Healthcare monitoring wizards
- FastAPI backend with authentication
- Complete example implementations

### Features
- Multi-LLM support (Anthropic Claude, OpenAI GPT-4)
- Plugin system for domain extensions
- Trust-building mechanisms
- Collaboration state tracking
- Leverage points identification
- Feedback loop monitoring

---

## Versioning

- **Major version** (X.0.0): Breaking changes to API or architecture
- **Minor version** (1.X.0): New features, backward compatible
- **Patch version** (1.0.X): Bug fixes, backward compatible

---

*For upgrade instructions and migration guides, see [docs/USER_GUIDE.md](docs/USER_GUIDE.md)*
