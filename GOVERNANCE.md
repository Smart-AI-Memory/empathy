# Governance

This document outlines the governance structure for the Empathy Framework project.

## Project Overview

The **Empathy Framework** is an open-source project providing a five-level maturity model for AI-human collaboration, progressing from reactive responses to anticipatory problem prevention.

- **License**: Fair Source 0.9 (dual licensing: free for individuals/education/small teams, commercial for larger organizations)
- **Organization**: Deep Study AI, LLC
- **Repository**: https://github.com/Smart-AI-Memory/empathy
- **Documentation**: https://github.com/Smart-AI-Memory/empathy/tree/main/docs

## Decision-Making Structure

### Single Maintainer Model

The Empathy Framework currently operates under a **single maintainer model** for rapid development and clear decision-making authority:

- **Maintainer**: Patrick Roebuck (Deep Study AI, LLC)
  - Email: patrick.roebuck@deepstudyai.com
  - GitHub: @silversurfer562
  - Role: Final decision authority, release management, security response

### Future Governance Evolution

As the project grows and attracts more contributors, the governance model may evolve to include:
- **Core Contributors**: Regular contributors with merge privileges
- **Technical Steering Committee**: For major architectural decisions
- **Community Maintainers**: Domain-specific package maintainers

## Roles and Responsibilities

### Maintainer

**Responsibilities**:
- Final approval on all pull requests
- Release planning and execution
- Security vulnerability response
- Roadmap planning and prioritization
- Community management
- License compliance
- OpenSSF Best Practices Badge maintenance

**Authority**:
- Merge privileges on main branch
- PyPI package publishing
- Security disclosure coordination
- Breaking change decisions

### Contributors

**Anyone can contribute** by:
- Submitting pull requests
- Reporting bugs and issues
- Suggesting features
- Improving documentation
- Participating in discussions

**Contributor Rights**:
- Credit in commit history
- Recognition in release notes
- Co-Authored-By tags for significant contributions

### Users

**Users** can:
- Use the framework under Fair Source 0.9 license terms
- Report issues and bugs
- Request features
- Participate in community discussions
- Provide feedback on documentation

## Decision-Making Process

### Standard Changes

**Process**:
1. Issue or pull request submitted
2. Discussion and review
3. Maintainer approval/rejection
4. Merge to main branch

**Timeline**: Typically 1-7 days depending on complexity

### Major Changes

**Criteria for "major"**:
- Breaking API changes
- New core abstractions
- License changes
- Architectural shifts
- New external dependencies

**Process**:
1. RFC (Request for Comments) issue created
2. Community discussion period (minimum 7 days)
3. Maintainer decision with rationale
4. Implementation and migration guide

### Security Issues

**Process**:
- Reported privately to patrick.roebuck@deepstudyai.com
- Maintainer acknowledgment within 48 hours
- Fix developed privately
- Coordinated disclosure after fix available
- Security advisory published

See [SECURITY.md](SECURITY.md) for full details.

## Release Process

### Versioning

The project follows **Semantic Versioning** (SemVer):
- **MAJOR**: Breaking API changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

**Current Version**: 1.6.1

### Release Cadence

- **Patch releases**: As needed for critical bugs
- **Minor releases**: Every 4-8 weeks for new features
- **Major releases**: When significant breaking changes accumulate

### Release Checklist

1. All tests passing (1,247+ tests)
2. Coverage requirements met (83%+)
3. Security scans clean
4. Documentation updated
5. CHANGELOG.md updated
6. Version bumped in pyproject.toml and __init__.py
7. Git tag created (v{version})
8. PyPI package published
9. GitHub release created

## Code of Conduct

### Principles

The Empathy Framework community values:
- **Respectful communication**
- **Constructive feedback**
- **Inclusive participation**
- **Professional behavior**
- **Technical excellence**

### Expected Behavior

- Be respectful and considerate
- Focus on technical merit
- Accept constructive criticism
- Acknowledge contributions
- Help newcomers

### Unacceptable Behavior

- Harassment or discrimination
- Personal attacks
- Disruptive behavior
- Spam or off-topic content
- Violations of privacy

### Enforcement

The maintainer has the authority to:
- Remove comments
- Close issues/PRs
- Block users (in extreme cases)
- Ban contributors (for repeated violations)

## Contributing Guidelines

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed contribution guidelines.

**Quick Summary**:
1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass
5. Submit a pull request
6. Respond to review feedback

## Communication Channels

### Primary

- **GitHub Issues**: Bug reports, feature requests
- **GitHub Discussions**: General questions, ideas
- **Pull Requests**: Code contributions
- **Security Email**: patrick.roebuck@deepstudyai.com (private security reports)

### Future

As the community grows, we may add:
- Discord/Slack community
- Monthly community calls
- Office hours for new contributors

## License and Intellectual Property

### Code License

All contributions to the Empathy Framework are licensed under **Fair Source 0.9**:
- **Free**: For individuals, students, educators, and organizations with ≤5 employees
- **Commercial**: $99/developer/year for organizations with 6+ employees

### Documentation License

Documentation is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

### Contributor License Agreement

By contributing to this project, you agree that:
1. Your contributions will be licensed under Fair Source 0.9
2. You have the right to contribute the code/documentation
3. Deep Study AI, LLC may relicense the project if needed for sustainability

## Roadmap and Planning

### Current Focus (Q1 2025)

- ✅ 70% test coverage (ACHIEVED: 83.13%)
- 🔄 90% test coverage target (229 lines remaining)
- 🔄 OpenSSF Best Practices Badge
- Production/Stable status (Development Status :: 5)

### Near-Term (Q1-Q2 2025)

- PyPI v2.0.0 release (after 90% coverage)
- Claude Code partnership case study
- MemDocs integration showcase
- Book chapter publication (Q1 2026)

### Long-Term (2025-2026)

- Silver/Gold OpenSSF badges
- Enterprise adoption case studies
- Multi-model LLM support expansion
- Domain-specific plugin ecosystem

## Changes to Governance

This governance document may be updated by the maintainer with:
1. Advance notice (minimum 14 days)
2. Rationale for changes
3. Community input period
4. Final decision documented

**Last Updated**: January 2025
**Next Review**: July 2025 (or when contributor base exceeds 10 active contributors)

---

## Quick Reference

- **Maintainer**: Patrick Roebuck (patrick.roebuck@deepstudyai.com)
- **License**: Fair Source 0.9
- **Code of Conduct**: Respectful, professional, inclusive
- **Security**: Report privately to patrick.roebuck@deepstudyai.com
- **Contributions**: Welcome via pull requests
- **Releases**: Semantic versioning, regular cadence
- **Community**: GitHub Issues/Discussions

For questions about governance, open a GitHub Discussion or contact the maintainer directly.
