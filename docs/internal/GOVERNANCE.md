# Empathy Framework - Project Governance

This document describes the governance structure and decision-making processes for the Empathy Framework.

## Project Status

**Current Phase**: Beta (Development Status :: 4)
**Organization**: Smart AI Memory, LLC
**Primary Maintainer**: Patrick Roebuck

## Governance Model

The Empathy Framework follows a **Benevolent Dictator** governance model during the Beta phase, with a planned transition to **Meritocratic Contribution** model as the community grows.

### Core Team

**Primary Maintainer** (Current):
- Patrick Roebuck (patrick.roebuck@deepstudyai.com)
  - Final decision authority on feature acceptance
  - Architecture and design direction
  - Release management and versioning
  - Security response coordination

**Future Core Team** (As community grows):
- Additional maintainers will be added based on sustained, high-quality contributions
- Core team members will have commit access and review authority
- Decisions will be made by consensus when possible

## Decision-Making Process

### For Small Changes
- Bug fixes, documentation improvements, minor refactoring
- **Process**: Submit PR → Review by maintainer → Merge if passing tests
- **Timeline**: Typically 1-3 days

### For Medium Changes
- New features, significant refactoring, API changes
- **Process**:
  1. Open GitHub Issue to discuss approach
  2. Get feedback from maintainer
  3. Submit PR with implementation
  4. Review and iterate
  5. Merge when approved
- **Timeline**: Typically 1-2 weeks

### For Major Changes
- Architecture changes, breaking API changes, new plugins
- **Process**:
  1. Create detailed RFC (Request for Comments) in GitHub Discussions
  2. Community discussion period (minimum 1 week)
  3. Maintainer decision based on:
     - Alignment with project vision
     - Technical merit
     - Community support
     - Resource availability
  4. Implementation via PR
- **Timeline**: 2-4 weeks minimum

### Security Issues
- **Process**: Follow SECURITY.md
- Private disclosure → Maintainer assessment → Fix → Disclosure
- **Timeline**: 48-hour acknowledgment, 5-day initial assessment

## Contributor Roles

### Contributor
- Anyone who submits a PR, issue, or participates in discussions
- No special permissions required
- All contributions welcome

### Regular Contributor
- Contributed 3+ merged PRs of high quality
- Recognized in CONTRIBUTORS.md
- May be consulted on relevant technical decisions

### Core Contributor
- Sustained high-quality contributions over 6+ months
- Deep domain expertise in specific areas
- Given triage permissions on GitHub
- Can review PRs (but not merge without maintainer approval)

### Maintainer
- Granted by primary maintainer based on:
  - 12+ months of regular, high-quality contributions
  - Demonstrated technical judgment
  - Alignment with project vision
  - Community trust
- Commit access and merge authority
- Participate in architectural decisions

## Release Process

**Version Numbers**: Semantic Versioning (MAJOR.MINOR.PATCH)

**Release Authority**:
- PATCH releases: Any maintainer
- MINOR releases: Core maintainers (consensus)
- MAJOR releases: Primary maintainer decision after community input

**Release Criteria**:
- All tests passing (100%)
- No critical security vulnerabilities
- Updated CHANGELOG.md
- Documentation updated
- Version bumped in pyproject.toml

**Release Schedule**:
- PATCH: As needed for bug fixes (1-2 weeks)
- MINOR: Quarterly for new features (every 3 months)
- MAJOR: Annually or as needed for breaking changes

## Conflict Resolution

1. **Technical Disagreements**:
   - Discuss in GitHub issue or PR comments
   - If unresolved, maintainer makes final decision
   - Document reasoning for transparency

2. **Code of Conduct Violations**:
   - Report to patrick.roebuck@deepstudyai.com
   - Maintainer investigates
   - Actions: warning → temporary ban → permanent ban
   - Appeals allowed within 30 days

3. **Maintainer Disputes** (Future):
   - When multiple maintainers exist
   - Majority vote among core maintainers
   - Primary maintainer breaks ties

## Roadmap and Priorities

**Short-term (Q1 2025)**:
- Reach 70% test coverage
- OpenSSF Best Practices preparation
- Security hardening
- Documentation improvements

**Medium-term (Q2 2025)**:
- Reach 90% test coverage
- Achieve OpenSSF Passing Badge
- Transition to Production/Stable (Development Status :: 5)
- First commercial customers

**Long-term (2025-2026)**:
- Expand plugin ecosystem
- Community-driven wizard contributions
- OpenSSF Silver Badge
- Enterprise features

## License and Commercial Model

**Dual Licensing**:
- Fair Source 0.9 (LICENSE): Free for ≤5 employees, students, educators
- Commercial License (LICENSE-COMMERCIAL.md): $99/developer/year for 6+ employees

**Commercial Decision Authority**: Smart AI Memory, LLC

**License Changes**: Require community notice (30 days minimum) and only affect future versions

## Amendment Process

This governance document can be amended by:
1. Proposal via GitHub Issue or Discussion
2. Community feedback period (minimum 2 weeks)
3. Final decision by primary maintainer
4. Document updated with version history

## Version History

- **v1.0** (January 2025): Initial governance document created
  - Established Benevolent Dictator model for Beta phase
  - Defined contributor roles and decision processes
  - Outlined path to meritocratic model

---

## Contact

**Questions about governance?**
- Email: patrick.roebuck@deepstudyai.com
- GitHub Discussions: https://github.com/Deep-Study-AI/Empathy/discussions

**Want to contribute?**
- See CONTRIBUTING.md for technical guidelines
- See CODE_OF_CONDUCT.md for community standards
