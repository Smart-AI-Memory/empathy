# Changelog

All notable changes to the Empathy Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.5.1] - 2025-12-29

### Documentation

- Updated README "What's New" section to reflect v3.5.x release
- Added Memory API Security Hardening features to release highlights
- Reorganized previous version sections for clarity

## [3.5.0] - 2025-12-29

### Added

- Memory Control Panel: View Patterns button now displays pattern list with classification badges
- Memory Control Panel: Project-level `auto_start_redis` config option in `empathy.config.yml`
- Memory Control Panel: Visual feedback for button actions (Check Status, Export show loading states)
- Memory Control Panel: "Check Status" button for manual status refresh (renamed from Refresh)
- VSCode Settings: `empathy.memory.autoRefresh` - Enable/disable auto-refresh (default: true)
- VSCode Settings: `empathy.memory.autoRefreshInterval` - Refresh interval in seconds (default: 30)
- VSCode Settings: `empathy.memory.showNotifications` - Show operation notifications (default: true)

### Security

**Memory API Security Hardening** (v2.2.0)

- **Input Validation**: Pattern IDs, agent IDs, and classifications are now validated on both client and server
  - Prevents path traversal attacks (`../`, `..\\`)
  - Validates format with regex patterns
  - Length bounds checking (3-64 chars)
  - Rejects null bytes and dangerous characters
- **API Key Authentication**: Optional Bearer token or X-API-Key header authentication
  - Set via `--api-key` CLI flag or `EMPATHY_MEMORY_API_KEY` environment variable
  - Constant-time comparison using SHA-256 hash
- **Rate Limiting**: Per-IP rate limiting (default: 100 requests/minute)
  - Configurable via `--rate-limit` and `--no-rate-limit` CLI flags
  - Returns `X-RateLimit-Remaining` and `X-RateLimit-Limit` headers
- **HTTPS Support**: Optional TLS encryption
  - Set via `--ssl-cert` and `--ssl-key` CLI flags
- **CORS Restrictions**: CORS now restricted to localhost by default
  - Configurable via `--cors-origins` CLI flag
- **Request Body Size Limit**: 1MB limit prevents DoS attacks
- **TypeScript Client**: Added input validation matching backend rules

### Fixed

- Memory Control Panel: Fixed config key mismatch (`empathyMemory` → `empathy.memory`) preventing settings from loading
- Memory Control Panel: Fixed API response parsing for Redis status display
- Memory Control Panel: Fixed pattern statistics not updating correctly
- Memory Control Panel: View Patterns now properly displays pattern list instead of just count

### Tests

- Added 37 unit tests for Memory API security features
  - Input validation tests (pattern IDs, agent IDs, classifications)
  - Rate limiter tests (limits, window expiration, per-IP tracking)
  - API key authentication tests (enable/disable, env vars, constant-time comparison)
  - Integration tests for security features

---

## [3.3.3] - 2025-12-28

### Added

**Reliability Improvements**
- Structured error taxonomy in `WorkflowResult`:
  - New `error_type` field: `"config"` | `"runtime"` | `"provider"` | `"timeout"` | `"validation"`
  - New `transient` boolean field to indicate if retry is reasonable
  - Auto-classification of errors in `BaseWorkflow.execute()`
- Configuration architecture documentation (`docs/configuration-architecture.md`)
  - Documents schema separation between `EmpathyConfig` and `WorkflowConfig`
  - Identifies `WorkflowConfig` naming collision between two modules
  - Best practices for config loading

**Refactor Advisor Enhancements** (VSCode Extension)
- Backend health indicator showing connection status
- Cancellation mechanism for in-flight analysis
- Pre-flight validation (Python and API key check before analysis)
- Cancel button during analysis with proper cleanup

### Fixed

- `EmpathyConfig.from_yaml()` and `from_json()` now gracefully ignore unknown fields
  - Fixes `TypeError: got an unexpected keyword argument 'provider'`
  - Allows config files to contain settings for other components
- Model ID test assertions updated to match registry (`claude-sonnet-4-5-20250514`)
- Updated model_router docstrings to reflect current model IDs

### Tests

- Added 5 tests for `EmpathyConfig` unknown field filtering
- Added 5 tests for `WorkflowResult` error taxonomy (`error_type`, `transient`)

---

## [3.3.2] - 2025-12-27

### Added

**Windows Compatibility**
- New `platform_utils` module for cross-platform support
  - Platform detection functions (`is_windows()`, `is_macos()`, `is_linux()`)
  - Platform-appropriate directory functions for logs, data, config, and cache
  - Asyncio Windows event loop policy handling (`setup_asyncio_policy()`)
  - UTF-8 encoding utilities for text files
  - Path normalization helpers
- Cross-platform compatibility checker script (`scripts/check_platform_compat.py`)
  - Detects hardcoded Unix paths, missing encoding, asyncio issues
  - JSON output mode for CI integration
  - `--fix` mode with suggested corrections
- CI integration for platform compatibility checks in GitHub Actions
- Pre-commit hook for platform compatibility (manual stage)
- Pytest integration test for platform compatibility (`test_platform_compat_ci.py`)

### Fixed

- Hardcoded Unix paths in `audit_logger.py` now use platform-appropriate defaults
- Added `setup_asyncio_policy()` call in CLI entry point for Windows compatibility

### Changed

- Updated `.claude/python-standards.md` with cross-platform coding guidelines

---

## [3.3.1] - 2025-12-27

### Fixed

- Updated Anthropic capable tier from Sonnet 4 to Sonnet 4.5 (`claude-sonnet-4-5-20250514`)
- Fixed model references in token_estimator and executor
- Fixed Setup button not opening Initialize Wizard (added `force` parameter)
- Fixed Cost Simulator layout for narrow panels (single-column layout)
- Fixed cost display inconsistency between workflow report and CLI footer
- Unified timing display to use milliseconds across all workflow reports
- Removed redundant CLI footer (workflow reports now contain complete timing/cost info)
- Fixed all mypy type errors across empathy_os and empathy_llm_toolkit
- Fixed ruff linting warnings (unused variables in dependency_check.py, document_gen.py)

### Changed

- All workflow reports now display duration in milliseconds (e.g., `Review completed in 15041ms`)
- Consistent footer format: `{Workflow} completed in {ms}ms | Cost: ${cost:.4f}`

---

## [3.2.3] - 2025-12-24

### Fixed

- Fixed PyPI URLs to match Diátaxis documentation structure
  - Getting Started: `/framework-docs/tutorials/quickstart/`
  - FAQ: `/framework-docs/reference/FAQ/`
- Rebuilt and updated documentation with Diátaxis structure
- Fresh MkDocs build deployed to website

---

## [3.2.2] - 2025-12-24

### Fixed

- Fixed PyPI URLs to use `/framework-docs/` path and currently deployed structure
- Documentation: `/framework-docs/`
- Getting Started: `/framework-docs/getting-started/quickstart/`
- FAQ: `/framework-docs/FAQ/`

---

## [3.2.1] - 2025-12-24

### Fixed

- Fixed broken PyPI project URLs for "Getting Started" and "FAQ" to match Diátaxis structure

---

## [3.2.0] - 2025-12-24

### Added

**Unified Typer CLI**
- New `empathy` command consolidating 5 entry points into one
- Beautiful Rich output with colored panels and tables
- Subcommand groups: `memory`, `provider`, `workflow`, `wizard`
- Cheatsheet command: `empathy cheatsheet`
- Backward-compatible legacy entry points preserved

**Dev Container Support**
- One-click development environment with VS Code
- Docker Compose setup with Python 3.11 + Redis 7
- Pre-configured VS Code extensions (Python, Ruff, Black, MyPy, Pylance)
- Automatic dependency installation on container creation

**CI/CD Enhancements**
- Python 3.13 added to test matrix (now 3.10-3.13 × 3 OS = 12 jobs)
- MyPy type checking in lint workflow (non-blocking)
- Codecov coverage upload for test tracking
- Documentation workflow for MkDocs build and deploy
- PR labeler for automatic label assignment
- Dependabot for automated dependency updates (pip, actions, docker)

**Async Pattern Detection**
- Background pattern detection for Level 3 proactive interactions
- Non-blocking pattern analysis during conversations
- Sequential, preference, and conditional pattern types

**Workflow Tests**
- PR Review workflow tests (32 tests)
- Dependency Check workflow tests (29 tests)
- Security Audit workflow tests
- Base workflow tests

### Changed

**Documentation Restructured with Diátaxis**
- Tutorials: Learning-oriented guides (installation, quickstart, examples)
- How-to: Task-oriented guides (memory, agents, integration)
- Explanation: Understanding-oriented content (philosophy, concepts)
- Reference: Information-oriented docs (API, CLI, glossary)
- Internal docs moved to `docs/internal/`

**Core Dependencies**
- Added `rich>=13.0.0` for beautiful CLI output
- Added `typer>=0.9.0` for modern CLI commands
- Ruff auto-fix enabled (`fix = true`)

**Project Structure**
- Root directory cleaned up (36 → 7 markdown files)
- Planning docs moved to `docs/development-logs/`
- Architecture docs organized in `docs/architecture/`
- Marketing materials in `docs/marketing/`

### Fixed

- Fixed broken internal documentation links after Diátaxis reorganization
- Lint fixes for unused variables in test files
- Black formatting for workflow tests

---

## [3.1.0] - 2025-12-23

### Added

**Health Check Workflow**
- New `health_check.py` workflow for system health monitoring
- Health check crew for Agent Factory

**Core Reliability Tests**
- Added `test_core_reliability.py` for comprehensive reliability testing

**CollaborationState Enhancements**
- Added `success_rate` property for tracking action success metrics

### Changed

**Agent Factory Improvements**
- Enhanced CodeReviewCrew dashboard integration
- Improved CrewAI, LangChain, and LangGraph adapters
- Memory integration enhancements
- Resilient agent patterns

**Workflow Enhancements**
- Code review workflow improvements
- Security audit workflow updates
- PR review workflow enhancements
- Performance audit workflow updates

**VSCode Extension Dashboard**
- Major dashboard panel improvements
- Enhanced workflow integration

### Fixed

- Fixed Level 4 anticipatory interaction AttributeError
- Various bug fixes across 92 files
- Improved type safety in workflow modules
- Test reliability improvements

---

## [3.0.1] - 2025-12-22

### Added

**XML-Enhanced Prompts System**
- Structured XML prompt templates for consistent LLM interactions
- Built-in templates: `security-audit`, `code-review`, `research`, `bug-analysis`
- `XmlPromptTemplate` and `PlainTextPromptTemplate` classes for flexible rendering
- `XmlResponseParser` with automatic XML extraction from markdown code blocks
- `PromptContext` dataclass with factory methods for common workflows
- Per-workflow XML configuration via `.empathy/workflows.yaml`
- Fallback to plain text when XML parsing fails (configurable)

**VSCode Dashboard Enhancements**
- 10 integrated workflows: Research, Code Review, Debug, Refactor, Test Generation, Documentation, Security Scan, Performance, Explain Code, Morning Briefing
- Workflow input history persistence across sessions
- File/folder picker integration for workflow inputs
- Cost fetching from telemetry CLI with fallback
- Error banner for improved debugging visibility

### Fixed

**Security Vulnerabilities (HIGH Priority)**
- Fixed command injection in VSCode extension `EmpathyDashboardPanel.ts`
- Fixed command injection in `extension.ts` runEmpathyCommand functions
- Replaced vulnerable `cp.exec()` with safe `cp.execFile()` using array arguments
- Created `health_scan.py` helper script to eliminate inline code execution
- Removed insecure `demo_key` fallback in `wizard_api.py`

**Security Hardening**
- Updated `.gitignore` to cover nested `.env` files (`**/.env`, `**/tests/.env`)
- Added security notice documentation to test fixtures with intentional vulnerabilities

### Changed

- Workflows now show provider name in output
- Workflows auto-load `.env` files for API key configuration

---

## [3.0.0] - 2025-12-22

### Added

**Multi-Model Provider System**
- Provider configuration: Anthropic, OpenAI, Ollama, Hybrid
- Auto-detection of API keys from environment and `.env` files
- CLI commands: `python -m empathy_os.models.cli provider`
- Single, hybrid, and custom provider modes

**Smart Tier Routing (80-96% Cost Savings)**
- Cheap tier: GPT-4o-mini/Haiku for summarization
- Capable tier: GPT-4o/Sonnet for bug fixing, code review
- Premium tier: o1/Opus for architecture decisions

**VSCode Dashboard - Complete Overhaul**
- 6 Quick Action commands for common tasks
- Real-time health score, costs, and workflow monitoring

### Changed

- README refresh with "Become a Power User" 5-level progression
- Comprehensive CLI reference
- Updated comparison table

---

## [2.5.0] - 2025-12-20

### Added

**Power User Workflows**
- **`empathy morning`** - Start-of-day briefing with patterns learned, tech debt trends, and suggested focus areas
- **`empathy ship`** - Pre-commit validation pipeline (lint, format, types, git status, Claude sync)
- **`empathy fix-all`** - Auto-fix all lint and format issues with ruff, black, and isort
- **`empathy learn`** - Extract bug patterns from git history automatically

**Cost Optimization Dashboard**
- **`empathy costs`** - View API cost tracking and savings from ModelRouter
- Daily/weekly cost breakdown by model tier and task type
- Automatic savings calculation vs always-using-premium baseline
- Integration with dashboard and VS Code extension

**Project Scaffolding**
- **`empathy new <template> <name>`** - Create new projects from templates
- Templates available: `minimal`, `python-cli`, `python-fastapi`, `python-agent`
- Pre-configured empathy.config.yml and .claude/CLAUDE.md included

**Progressive Feature Discovery**
- Context-aware tips shown after command execution
- Tips trigger based on usage patterns (e.g., "After 10 inspects, try sync-claude")
- Maximum 2 tips at a time to avoid overwhelming users
- Tracks command usage and patterns learned

**Visual Dashboard**
- **`empathy dashboard`** - Launch web-based dashboard in browser
- Pattern browser with bug types and resolution status
- Cost savings visualization
- Quick command reference
- Dark mode support (respects system preference)

**VS Code Extension** (`vscode-extension/`)
- Status bar showing patterns count and cost savings
- Command palette integration for all empathy commands
- Sidebar with Patterns, Health, and Costs tree views
- Auto-refresh of pattern data
- Settings for customization

### Changed

- CLI now returns proper exit codes for scripting integration
- Improved terminal output formatting across all commands
- Discovery tips integrated into CLI post-command hooks

---

## [2.4.0] - 2025-12-20

### Added

**Agent Factory - Universal Multi-Framework Agent System**
- **AgentFactory** - Create agents using any supported framework with a unified API
  - `AgentFactory(framework="native")` - Built-in Empathy agents (no dependencies)
  - `AgentFactory(framework="langchain")` - LangChain chains and agents
  - `AgentFactory(framework="langgraph")` - LangGraph stateful workflows
  - Auto-detection of installed frameworks with intelligent fallbacks

- **Framework Adapters** - Pluggable adapters for each framework:
  - `NativeAdapter` - Zero-dependency agents with EmpathyLLM integration
  - `LangChainAdapter` - Full LangChain compatibility with tools and chains
  - `LangGraphAdapter` - Stateful multi-step workflows with cycles
  - `WizardAdapter` - Bridge existing wizards to Agent Factory interface

- **UnifiedAgentConfig** (Pydantic) - Single source of truth for configuration:
  - Model tier routing (cheap/capable/premium)
  - Provider abstraction (anthropic/openai/local)
  - Empathy level integration (1-5)
  - Feature flags for memory, pattern learning, cost tracking
  - Framework-specific options

- **Agent Decorators** - Standardized cross-cutting concerns:
  - `@safe_agent_operation` - Error handling with audit trail
  - `@retry_on_failure` - Exponential backoff retry logic
  - `@log_performance` - Performance monitoring with thresholds
  - `@validate_input` - Input validation for required fields
  - `@with_cost_tracking` - Token usage and cost monitoring
  - `@graceful_degradation` - Fallback values on failure

- **BaseAgent Protocol** - Common interface for all agents:
  - `invoke(input_data, context)` - Single invocation
  - `stream(input_data, context)` - Streaming responses
  - Conversation history with memory support
  - Model tier-based routing

- **Workflow Support** - Multi-agent orchestration:
  - Sequential, parallel, and graph execution modes
  - State management with checkpointing
  - Cross-agent result passing

### Changed

- **agents/book_production/base.py** - Now imports from unified config
  - Deprecated legacy `AgentConfig` in favor of `UnifiedAgentConfig`
  - Added migration path with `to_unified()` method
  - Backward compatible with existing code

### Fixed

- **Wizard Integration Tests** - Added `skip_if_server_unavailable` fixture
  - Tests now skip gracefully when wizard server isn't running
  - Prevents false failures in CI environments
  - Reduced integration test failures from 73 to 22

- **Type Annotations** - Complete mypy compliance for agent_factory module
  - Fixed Optional types in factory.py
  - Added proper async iterator annotations
  - Resolved LangChain API compatibility issues
  - All 102 original agent_factory errors resolved

### Documentation

- **AGENT_IMPROVEMENT_RECOMMENDATIONS.md** - Comprehensive evaluation of existing agents
  - SOLID principles assessment for each agent type
  - Clean code analysis with specific recommendations
  - Appendix A: Best practices checklist

---

## [2.3.0] - 2025-12-19

### Added

**Smart Model Routing for Cost Optimization**
- **ModelRouter** - Automatically routes tasks to appropriate model tiers:
  - **CHEAP tier** (Haiku/GPT-4o-mini): summarize, classify, triage, match_pattern
  - **CAPABLE tier** (Sonnet/GPT-4o): generate_code, fix_bug, review_security, write_tests
  - **PREMIUM tier** (Opus/o1): coordinate, synthesize_results, architectural_decision
- 80-96% cost savings for appropriate task routing
- Provider-agnostic: works with Anthropic, OpenAI, and Ollama
- Usage: `EmpathyLLM(enable_model_routing=True)` + `task_type` parameter

**Claude Code Integration**
- **`empathy sync-claude`** - Sync learned patterns to `.claude/rules/empathy/` directory
  - `empathy sync-claude --watch` - Auto-sync on pattern changes
  - `empathy sync-claude --dry-run` - Preview without writing
- Outputs: bug-patterns.md, security-decisions.md, tech-debt-hotspots.md, coding-patterns.md
- Native Claude Code rules integration for persistent context

**Memory-Enhanced Debugging Wizard**
- Web GUI at wizards.smartaimemory.com
- Folder selection with expandable file tree
- Drag-and-drop file upload
- Pattern storage for bug signatures
- Memory-enhanced analysis that learns from past fixes

### Changed
- EmpathyLLM now accepts `task_type` parameter for model routing
- Improved provider abstraction for dynamic model selection
- All 5 empathy level handlers support model override

### Fixed
- httpx import for test compatibility with pytest.importorskip

---

## [2.2.10] - 2025-12-18

### Added

**Dev Wizards Web Backend**
- New FastAPI backend for wizards.smartaimemory.com deployment
- API endpoints for Memory-Enhanced Debugging, Security Analysis, Code Review, and Code Inspection
- Interactive dashboard UI with demo capabilities
- Railway deployment configuration (railway.toml, nixpacks.toml)

### Fixed
- PyPI documentation now reflects current README and features

---

## [2.2.9] - 2025-12-18

### Added

**Code Inspection Pipeline**
- **`empathy-inspect` CLI** - Unified code inspection command combining lint, security, tests, and tech debt analysis
  - `empathy-inspect .` - Inspect current directory with default settings
  - `empathy-inspect . --format sarif` - Output SARIF 2.1.0 for GitHub Actions/GitLab/Azure DevOps
  - `empathy-inspect . --format html` - Generate visual dashboard report
  - `empathy-inspect . --staged` - Inspect only git-staged changes
  - `empathy-inspect . --fix` - Auto-fix safe issues (formatting, imports)

**SARIF 2.1.0 Output Format**
- Industry-standard static analysis format for CI/CD integration
- GitHub code scanning annotations on pull requests
- Compatible with GitLab, Azure DevOps, Bitbucket, and other SARIF-compliant platforms
- Proper severity mapping: critical/high → error, medium → warning, low/info → note

**HTML Dashboard Reports**
- Professional visual reports for stakeholders
- Color-coded health score gauge (green/yellow/red)
- Six category breakdown cards (Lint, Security, Tests, Tech Debt, Code Review, Debugging)
- Sortable findings table with severity and priority
- Prioritized recommendations section
- Export-ready for sprint reviews and security audits

**Baseline/Suppression System**
- **Inline suppressions** for surgical control:
  - `# empathy:disable RULE reason="..."` - Suppress for current line
  - `# empathy:disable-next-line RULE` - Suppress for next line
  - `# empathy:disable-file RULE` - Suppress for entire file
- **JSON baseline file** (`.empathy-baseline.json`) for project-wide policies:
  - Rule-level suppressions with reasons
  - File-level suppressions for legacy code
  - TTL-based expiring suppressions with `expires_at`
- **CLI commands**:
  - `--no-baseline` - Show all findings (for audits)
  - `--baseline-init` - Create empty baseline file
  - `--baseline-cleanup` - Remove expired suppressions

**Language-Aware Code Review**
- Integration with CrossLanguagePatternLibrary for intelligent pattern matching
- Language-specific analysis for Python, JavaScript/TypeScript, Rust, Go, Java
- Cross-language insights: "This Python None check is like the JavaScript undefined bug you fixed"
- No false positives from applying wrong-language patterns

### Changed

**Five-Phase Pipeline Architecture**
1. **Static Analysis** (Parallel) - Lint, security, tech debt, test quality run simultaneously
2. **Dynamic Analysis** (Conditional) - Code review, debugging only if Phase 1 finds triggers
3. **Cross-Analysis** (Sequential) - Correlate findings across tools for priority boosting
4. **Learning** (Optional) - Extract patterns for future inspections
5. **Reporting** (Always) - Unified health score and recommendations

**VCS Flexibility**
- Optimized for GitHub but works with GitLab, Bitbucket, Azure DevOps, self-hosted Git
- Git-native pattern storage in `patterns/` directory
- SARIF output compatible with any CI/CD platform supporting the standard

### Fixed
- Marked 5 demo bug patterns from 2025-12-16 with `demo: true` field
- Type errors in baseline.py stats dictionary and suppression entry typing
- Type cast for suppressed count in reporting.py

### Documentation
- Updated [CLI_GUIDE.md](docs/CLI_GUIDE.md) with full `empathy-inspect` documentation
- Updated [README.md](README.md) with Code Inspection Pipeline section
- Created blog post draft: `drafts/blog-code-inspection-pipeline.md`

---

## [2.2.7] - 2025-12-15

### Fixed
- **PyPI project URLs** - Use www.smartaimemory.com consistently (was missing www prefix)

## [2.2.6] - 2025-12-15

### Fixed
- **PyPI project URLs** - Documentation, FAQ, Book, and Getting Started links now point to smartaimemory.com instead of broken GitHub paths

## [2.2.5] - 2025-12-15

### Added
- **Distribution Policy** - Comprehensive policy for PyPI and git archive exclusions
  - `MANIFEST.in` updated with organized include/exclude sections
  - `.gitattributes` with export-ignore for GitHub ZIP downloads
  - `DISTRIBUTION_POLICY.md` documenting the philosophy and implementation
- **Code Foresight Positioning** - Marketing positioning for Code Foresight feature
  - End-of-Day Prep feature spec for instant morning reports
  - Conversation content for book/video integration

### Changed
- Marketing materials, book production files, memory/data files, and internal planning documents now excluded from PyPI distributions and git archives
- Users get a focused package (364 files, 1.1MB) with only what they need

### Philosophy
> Users get what empowers them, not our development history.

## [2.1.4] - 2025-12-15

### Added

**Pattern Enhancement System (7 Phases)**

Phase 1: Auto-Regeneration
- Pre-commit hook automatically regenerates patterns_summary.md when pattern files change
- Ensures CLAUDE.md imports always have current pattern data

Phase 2: Pattern Resolution CLI
- New `empathy patterns resolve` command to mark investigating bugs as resolved
- Updates bug patterns with root cause, fix description, and resolution time
- Auto-regenerates summary after resolution

Phase 3: Contextual Pattern Injection
- ContextualPatternInjector filters patterns by current context
- Supports file type, error type, and git change-based filtering
- Reduces cognitive load by showing only relevant patterns

Phase 4: Auto-Pattern Extraction Wizard
- PatternExtractionWizard (Level 3) detects bug fixes in git diffs
- Analyzes commits for null checks, error handling, async fixes
- Suggests pre-filled pattern entries for storage

Phase 5: Pattern Confidence Scoring
- PatternConfidenceTracker records pattern usage and success rates
- Calculates confidence scores based on application success
- Identifies stale and high-value patterns

Phase 6: Git Hook Integration
- GitPatternExtractor auto-creates patterns from fix commits
- Post-commit hook script for automatic pattern capture
- Detects fix patterns from commit messages and code changes

Phase 7: Pattern-Based Code Review (Capstone)
- CodeReviewWizard (Level 4) reviews code against historical bugs
- Generates anti-pattern rules from resolved bug patterns
- New `empathy review` CLI command for pre-commit code review
- Pre-commit hook integration for optional automatic review

**New Modules**
- empathy_llm_toolkit/pattern_resolver.py - Resolution workflow
- empathy_llm_toolkit/contextual_patterns.py - Context-aware filtering
- empathy_llm_toolkit/pattern_confidence.py - Confidence tracking
- empathy_llm_toolkit/git_pattern_extractor.py - Git integration
- empathy_software_plugin/wizards/pattern_extraction_wizard.py
- empathy_software_plugin/wizards/code_review_wizard.py

**CLI Commands**
- `empathy patterns resolve <bug_id>` - Resolve investigating patterns
- `empathy review [files]` - Pattern-based code review
- `empathy review --staged` - Review staged changes

## [2.1.3] - 2025-12-15

### Added

**Pattern Integration for Claude Code Sessions**
- PatternSummaryGenerator for auto-generating pattern summaries
- PatternRetrieverWizard (Level 3) for dynamic pattern queries
- @import directive in CLAUDE.md loads pattern context at session start
- Patterns from debugging, security, and tech debt now available to AI assistants

### Fixed

**Memory System**
- Fixed control_panel.py KeyError when listing patterns with missing fields
- Fixed unified.py promote_pattern to correctly retrieve content from context
- Fixed promote_pattern method name typo (promote_staged_pattern -> promote_pattern)

**Tests**
- Fixed test_redis_bootstrap fallback test missing mock for _start_via_direct
- Fixed test_unified_memory fallback test to allow mock instance on retry

**Test Coverage**
- All 2,208 core tests pass

## [2.1.2] - 2025-12-14

### Fixed

**Documentation**
- Fixed 13 broken links in MkDocs documentation
- Fixed FAQ.md, examples/*.md, and root docs links

### Removed

**CI/CD**
- Removed Codecov integration and coverage upload from GitHub Actions
- Removed codecov.yml configuration file
- Removed Codecov badge from README

## [1.9.5] - 2025-12-01

### Fixed

**Test Suite**
- Fixed LocalProvider async context manager mocking in tests
- All 1,491 tests now pass

## [1.9.4] - 2025-11-30

### Changed

**Website Updates**
- Healthcare Wizards navigation now links to external dashboard at healthcare.smartaimemory.com
- Added Dev Wizards link to wizards.smartaimemory.com
- SBAR wizard demo page with 5-step guided workflow

**Documentation**
- Added live demo callouts to healthcare documentation pages
- Updated docs/index.md, docs/guides/healthcare-wizards.md, docs/examples/sbar-clinical-handoff.md

**Code Quality**
- Added ESLint rules to suppress inline style warnings for Tailwind CSS use cases
- Fixed unused variable warnings (`isGenerating`, `theme`)
- Fixed unescaped apostrophe JSX warnings
- Test coverage: 75.87% (1,489 tests pass)

## [1.9.3] - 2025-11-28

### Changed

**Healthcare Focus**
- Archived 13 non-healthcare wizards to `archived_wizards/` directory
  - Accounting, Customer Support, Education, Finance, Government, HR
  - Insurance, Legal, Logistics, Manufacturing, Real Estate, Research
  - Retail, Sales, Technology wizards moved to archive
- Package now focuses on 8 healthcare clinical wizards:
  - Admission Assessment, Care Plan, Clinical Assessment, Discharge Summary
  - Incident Report, SBAR, Shift Handoff, SOAP Note
- Archived wizards remain functional and tested (104 tests pass)

**Website Updates**
- Added SBAR wizard API routes (`/api/wizards/sbar/start`, `/api/wizards/sbar/generate`)
- Added SBARWizard React component
- Updated navigation and dashboard for healthcare focus

**Code Quality**
- Added B904 to ruff ignore list (exception chaining in HTTPException pattern)
- Fixed 37 CLI tests (logger output capture using caplog)
- Test coverage: 74.58% (1,328 tests pass)

**Claude Code Positioning**
- Updated documentation with "Created in consultation with Claude Sonnet 4.5 using Claude Code"
- Added Claude Code badge to README
- Updated pitch deck and partnership materials

## [1.9.2] - 2025-11-28

### Fixed

**Documentation Links**
- Fixed all broken relative links in README.md for PyPI compatibility
  - Updated Quick Start Guide, API Reference, and User Guide links (line 45)
  - Fixed all framework documentation links (CHAPTER_EMPATHY_FRAMEWORK.md, etc.)
  - Updated all source file links (agents, coach_wizards, empathy_llm_toolkit, services)
  - Fixed examples and resources directory links
  - Updated LICENSE and SPONSORSHIP.md links
  - All relative paths now use full GitHub URLs (e.g., `https://github.com/Smart-AI-Memory/empathy/blob/main/docs/...`)
- All documentation links now work correctly when viewed on PyPI package page

**Impact**: Users viewing the package on PyPI can now access all documentation links without encountering 404 errors.

## [1.8.0-alpha] - 2025-11-24

### Added - Claude Memory Integration

**Core Memory System**
- **ClaudeMemoryLoader**: Complete CLAUDE.md file reader with hierarchical memory loading
  - Enterprise-level memory: `/etc/claude/CLAUDE.md` or `CLAUDE_ENTERPRISE_MEMORY` env var
  - User-level memory: `~/.claude/CLAUDE.md` (personal preferences)
  - Project-level memory: `./.claude/CLAUDE.md` (team/project specific)
  - Loads in hierarchical order (Enterprise → User → Project) with clear precedence
  - Caching system for performance optimization
  - File size limits (1MB default) and validation

**@import Directive Support**
- Modular memory organization with `@path/to/file.md` syntax
- Circular import detection (prevents infinite loops)
- Import depth limiting (5 levels default, configurable)
- Relative path resolution from base directory
- Recursive import processing with proper error handling

**EmpathyLLM Integration**
- `ClaudeMemoryConfig`: Comprehensive configuration for memory integration
  - Enable/disable memory loading per level (enterprise/user/project)
  - Configurable depth limits and file size restrictions
  - Optional file validation
- Memory prepended to all LLM system prompts across all 5 empathy levels
- `reload_memory()` method for runtime memory updates without restart
- `_build_system_prompt()`: Combines memory with level-specific instructions
- Memory affects behavior of all interactions (Reactive → Systems levels)

**Documentation & Examples**
- **examples/claude_memory/user-CLAUDE.md**: Example user-level memory file
  - Communication preferences, coding standards, work context
  - Demonstrates personal preference storage
- **examples/claude_memory/project-CLAUDE.md**: Example project-level memory file
  - Project context, architecture patterns, security requirements
  - Empathy Framework-specific guidelines and standards
- **examples/claude_memory/example-with-imports.md**: Import directive demo
  - Shows modular memory organization patterns

**Comprehensive Testing**
- **tests/test_claude_memory.py**: 15+ test cases covering all features
  - Config defaults and customization tests
  - Hierarchical memory loading (enterprise/user/project)
  - @import directive processing and recursion
  - Circular import detection
  - Depth limit enforcement
  - File size validation
  - Cache management (clear/reload)
  - Integration with EmpathyLLM
  - Memory reloading after file changes
- All tests passing with proper fixtures and mocking

### Changed

**Core Architecture**
- **empathy_llm_toolkit/core.py**: Enhanced EmpathyLLM with memory support
  - Added `claude_memory_config` and `project_root` parameters
  - Added `_cached_memory` for performance optimization
  - All 5 empathy level handlers now use `_build_system_prompt()` for consistent memory integration
  - Memory loaded once at initialization, cached for all subsequent interactions

**Dependencies**
- Added structlog for structured logging in memory module
- No new external dependencies required (uses existing framework libs)

### Technical Details

**Memory Loading Flow**
1. Initialize `EmpathyLLM` with `claude_memory_config` and `project_root`
2. `ClaudeMemoryLoader` loads files in hierarchical order
3. Each file processed for @import directives (recursive, depth-limited)
4. Combined memory cached in `_cached_memory` attribute
5. Every LLM call prepends memory to system prompt
6. Memory affects all 5 empathy levels uniformly

**File Locations**
- Enterprise: `/etc/claude/CLAUDE.md` or env var `CLAUDE_ENTERPRISE_MEMORY`
- User: `~/.claude/CLAUDE.md`
- Project: `./.claude/CLAUDE.md` (preferred) or `./CLAUDE.md` (fallback)

**Safety Features**
- Circular import detection (prevents infinite loops)
- Depth limiting (default 5 levels, prevents excessive nesting)
- File size limits (default 1MB, prevents memory issues)
- Import stack tracking for cycle detection
- Graceful degradation (returns empty string on errors if validation disabled)

### Enterprise Privacy Foundation

This release is Phase 1 of the enterprise privacy integration roadmap:
- ✅ **Phase 1 (v1.8.0-alpha)**: Claude Memory Integration - COMPLETE
- ⏳ **Phase 2 (v1.8.0-beta)**: PII scrubbing, audit logging, EnterprisePrivacyConfig
- ⏳ **Phase 3 (v1.8.0)**: VSCode privacy UI, documentation
- ⏳ **Future**: Full MemDocs integration with 3-tier privacy system

**Privacy Goals**
- Give enterprise developers control over memory scope (enterprise/user/project)
- Enable local-only memory (no cloud storage of sensitive instructions)
- Foundation for air-gapped/hybrid/full-integration deployment models
- Compliance-ready architecture (GDPR, HIPAA, SOC2)

### Quality Metrics
- **New Module**: empathy_llm_toolkit/claude_memory.py (483 lines)
- **Modified Core**: empathy_llm_toolkit/core.py (memory integration)
- **Tests Added**: 15+ comprehensive test cases
- **Test Coverage**: All memory features covered
- **Example Files**: 3 sample CLAUDE.md files
- **Documentation**: Inline docstrings with Google style

### Breaking Changes
None - this is an additive feature. Memory integration is opt-in via `claude_memory_config`.

### Upgrade Notes
- To use Claude memory: Pass `ClaudeMemoryConfig(enabled=True)` to `EmpathyLLM.__init__()`
- Create `.claude/CLAUDE.md` in your project root with instructions
- See examples/claude_memory/ for sample memory files
- Memory is disabled by default (backward compatible)

---

## [1.7.1] - 2025-11-22

### Changed

**Project Synchronization**
- Updated all Coach IDE extension examples to v1.7.1
  - VSCode Extension Complete: synchronized version
  - JetBrains Plugin (Basic): synchronized version and change notes
  - JetBrains Plugin Complete: synchronized version and change notes
- Resolved merge conflict in JetBrains Plugin plugin.xml
- Standardized version numbers across all example projects
- Updated all change notes to reflect Production/Stable status

**Quality Improvements**
- Ensured consistent version alignment with core framework
- Improved IDE extension documentation and metadata
- Enhanced change notes with test coverage (90.71%) and Level 4 predictions

## [1.7.0] - 2025-11-21

### Added - Phase 1: Foundation Hardening

**Documentation**
- **FAQ.md**: Comprehensive FAQ with 32 questions covering Level 5 Systems Empathy, licensing, pricing, MemDocs integration, and support (500+ lines)
- **TROUBLESHOOTING.md**: Complete troubleshooting guide covering 25+ common issues including installation, imports, API keys, performance, tests, LLM providers, and configuration (600+ lines)
- **TESTING_STRATEGY.md**: Detailed testing approach documentation with coverage goals (90%+), test types, execution instructions, and best practices
- **CONTRIBUTING_TESTS.md**: Comprehensive guide for contributors writing tests, including naming conventions, pytest fixtures, mocking strategies, and async testing patterns
- **Professional Badges**: Added coverage (90.66%), license (Fair Source 0.9), Python version (3.10+), Black, and Ruff badges to README

**Security**
- **Security Audits**: Comprehensive security scanning with Bandit and pip-audit
  - 0 High/Medium severity vulnerabilities found
  - 22 Low severity issues (contextually appropriate)
  - 16,920 lines of code scanned
  - 186 packages audited with 0 dependency vulnerabilities
- **SECURITY.md**: Updated with current security contact (security@smartaimemory.com), v1.6.8 version info, and 24-48 hour response timeline

**Test Coverage**
- **Coverage Achievement**: Increased from 32.19% to 90.71% (+58.52 percentage points)
- **Test Count**: 887 → 1,489 tests (+602 new tests)
- **New Test Files**: test_coach_wizards.py, test_software_cli.py with comprehensive coverage
- **Coverage Documentation**: Detailed gap analysis and testing strategy documented

### Added - Phase 2: Marketing Assets

**Launch Content**
- **SHOW_HN_POST.md**: Hacker News launch post (318 words, HN-optimized)
- **LINKEDIN_POST.md**: Professional LinkedIn announcement (1,013 words, business-value focused)
- **TWITTER_THREAD.md**: Viral Twitter thread (10 tweets with progressive storytelling)
- **REDDIT_POST.md**: Technical deep-dive for r/programming (1,778 words with code examples)
- **PRODUCT_HUNT.md**: Complete Product Hunt launch package with submission materials, visual specs, engagement templates, and success metrics

**Social Proof & Credibility**
- **COMPARISON.md**: Competitive positioning vs SonarQube, CodeClimate, GitHub Copilot with 10 feature comparisons and unique differentiators
- **RESULTS.md**: Measurable achievements documentation including test coverage improvements, security audit results, and license compliance
- **OPENSSF_APPLICATION.md**: OpenSSF Best Practices Badge application (90% criteria met, ready to submit)
- **CASE_STUDY_TEMPLATE.md**: 16-section template for customer success stories including ROI calculation and before/after comparison

**Demo & Visual Assets**
- **DEMO_VIDEO_SCRIPT.md**: Production guide for 2-3 minute demo video with 5 segments and second-by-second timing
- **README_GIF_GUIDE.md**: Animated GIF creation guide using asciinema, Terminalizer, and ffmpeg (10-15 seconds, <5MB target)
- **LIVE_DEMO_NOTES.md**: Conference presentation guide with 3 time-based flows (5/15/30 min), backup plans, and Q&A prep
- **PRESENTATION_OUTLINE.md**: 10-slide technical talk template with detailed speaker notes (15-20 minute duration)
- **SCREENSHOT_GUIDE.md**: Visual asset capture guide with 10 key moments, platform-specific tools, and optimization workflows

### Added - Level 5 Transformative Example

**Cross-Domain Pattern Transfer**
- **Level 5 Example**: Healthcare handoff patterns → Software deployment safety prediction
- **Demo Implementation**: Complete working demo (examples/level_5_transformative/run_full_demo.py)
  - Healthcare handoff protocol analysis (ComplianceWizard)
  - Pattern storage in simulated MemDocs memory
  - Software deployment code analysis (CICDWizard)
  - Cross-domain pattern matching and retrieval
  - Deployment failure prediction (87% confidence, 30-45 days ahead)
- **Documentation**: Complete README and blog post for Level 5 example
- **Real-World Impact**: Demonstrates unique capability no other AI framework can achieve

### Changed

**License Consistency**
- Fixed licensing inconsistency across all documentation files (Apache 2.0 → Fair Source 0.9)
- Updated 8 documentation files: QUICKSTART_GUIDE, API_REFERENCE, USER_GUIDE, TROUBLESHOOTING, FAQ, ANTHROPIC_PARTNERSHIP_PROPOSAL, POWERED_BY_CLAUDE_TIERS, BOOK_README
- Ensured consistency across 201 Python files and all markdown documentation

**README Enhancement**
- Added featured Level 5 Transformative Empathy section
- Cross-domain pattern transfer example with healthcare → software deployment
- Updated examples and documentation links
- Added professional badge display

**Infrastructure**
- Added coverage.json to .gitignore (generated file, not for version control)
- Created comprehensive execution plan (EXECUTION_PLAN.md) for commercial launch with parallel processing strategy

### Quality Metrics
- **Test Coverage**: 90.71% overall (32.19% → 90.71%, +58.52 pp)
- **Security Vulnerabilities**: 0 (zero high/medium severity)
- **New Tests**: +602 tests (887 → 1,489)
- **Documentation**: 15+ new/updated comprehensive documentation files
- **Marketing**: 5 platform launch packages ready (HN, LinkedIn, Twitter, Reddit, Product Hunt)
- **Total Files Modified**: 200+ files across Phase 1 & 2

### Commercial Readiness
- Launch-ready marketing materials across all major platforms
- Comprehensive documentation for users, contributors, and troubleshooting
- Professional security posture with zero vulnerabilities
- 90%+ test coverage with detailed testing strategy
- Level 5 unique capability demonstration
- OpenSSF Best Practices badge application ready
- Ready for immediate commercial launch

---

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
