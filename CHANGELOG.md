# Changelog

All notable changes to the Empathy Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned Features
- JetBrains Marketplace listing for Coach IDE integration
- VS Code Marketplace listing for Coach IDE integration
- Team dashboard for Business tier users
- License validation system for Pro/Business tiers
- Book delivery mechanism for Pro tier customers
- Telemetry and analytics (opt-in)

## [1.0.0] - 2025-01-15

### Added
- **Core Framework**: Five-level maturity model (Reactive → Guided → Proactive → Anticipatory → Systems)
- **16 Coach Wizards** for software development:
  - Security Wizard (SQL injection, XSS, CSRF detection)
  - Performance Wizard (N+1 queries, memory leaks)
  - Accessibility Wizard (WCAG compliance)
  - Testing Wizard (coverage analysis)
  - Refactoring Wizard (code smells)
  - Database Wizard (query optimization)
  - API Wizard (design patterns)
  - Debugging Wizard (error detection)
  - Scaling Wizard (architecture analysis)
  - Observability Wizard (logging/metrics)
  - CI/CD Wizard (pipeline optimization)
  - Documentation Wizard (quality analysis)
  - Compliance Wizard (regulatory requirements)
  - Migration Wizard (code migration)
  - Monitoring Wizard (system health)
  - Localization Wizard (i18n)
- **Base Wizard Pattern**: Abstract base class implementing Level 4 Anticipatory pattern
- **3 Healthcare Agents**:
  - Compliance Anticipation Agent (90-day audit prediction)
  - Trust Building Behaviors (tactical empathy)
  - EPIC Integration Wizard (EHR integration)
- **17 Clinical Wizards**: SBAR, SOAP, admission assessments, discharge summaries, etc.
- **Wizard AI Service**: Orchestration layer for all wizards
- **Coach IDE Examples**:
  - Complete JetBrains plugin (63 files)
  - Complete VS Code extension (16 files)
  - LSP server implementation (3 files)
- **Comprehensive Documentation**:
  - Framework guide (technical)
  - Non-technical guide
  - Teaching AI your philosophy
  - Implementation examples
- **Apache 2.0 License**: Open source with patent protection
- **Repository Structure**: Organized by function (agents, wizards, services, docs, examples)

### Documentation
- README.md with quick start guide
- Competitive comparison table
- Pricing tiers (Free, Pro $129/year, Business $249/year)
- Philosophy section (Goleman, Voss, Naval, Meadows, Senge)
- Real-world applications (healthcare + software)

### Infrastructure
- Python requirements.txt with LangChain, AI models, testing
- .gitignore for Python projects
- NOTICE file with Apache 2.0 copyright
- SECURITY.md with vulnerability reporting policy

## Version History

### Version Numbering

We use [Semantic Versioning](https://semver.org/):
- **MAJOR** version: Incompatible API changes
- **MINOR** version: New functionality (backward compatible)
- **PATCH** version: Bug fixes (backward compatible)

### Release Schedule

- **Major releases**: Annually (planned)
- **Minor releases**: Quarterly
- **Patch releases**: As needed for bug fixes and security updates

## Migration Guides

### Upgrading to 1.0.0

This is the initial release. No migration needed.

## Deprecation Policy

- Features will be marked deprecated for at least 2 minor versions before removal
- Deprecated features will be documented in this changelog
- Security-critical deprecations may have shorter timelines

## Support Policy

- **Current major version**: Full support (bug fixes + new features)
- **Previous major version**: Security fixes only for 12 months
- **Older versions**: No support (please upgrade)

## Contributing

See [CONTRIBUTING.md](examples/coach/CONTRIBUTING.md) for how to suggest changes and report issues.

## Links

- **Repository**: https://github.com/Deep-Study-AI/Empathy
- **Issues**: https://github.com/Deep-Study-AI/Empathy/issues
- **Discussions**: https://github.com/Deep-Study-AI/Empathy/discussions
- **Security**: patrick.roebuck@deepstudyai.com

---

**[Unreleased]**: https://github.com/Deep-Study-AI/Empathy/compare/v1.0.0...HEAD
**[1.0.0]**: https://github.com/Deep-Study-AI/Empathy/releases/tag/v1.0.0
