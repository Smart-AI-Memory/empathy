# Project-Level Claude Memory
# Location: ./.claude/CLAUDE.md (in project root)

This file contains project-specific instructions for the Empathy Framework.

## Project Context
This is the Empathy Framework - a five-level AI collaboration system with anticipatory empathy.

**Core Concepts:**
- Level 1: Reactive (basic Q&A)
- Level 2: Guided (clarifying questions)
- Level 3: Proactive (pattern-based actions)
- Level 4: Anticipatory (30-90 day predictions)
- Level 5: Systems (cross-domain pattern transfer)

## Architecture
- Framework: Python async/await architecture
- LLM Integration: Anthropic (Claude), OpenAI, Local (Ollama)
- Memory: MemDocs for pattern storage
- Extensions: VSCode and JetBrains IDE integrations

## Code Organization
```
empathy_llm_toolkit/    # Core LLM wrapper with levels
empathy_os/             # Operating system layer
coach_wizards/          # 16 specialized AI wizards
examples/               # Usage examples and demos
tests/                  # Comprehensive test suite
```

## Coding Guidelines
- Use async/await for all I/O operations
- Type hints required for all public APIs
- Structlog for structured logging
- Pydantic for data validation

## Testing Requirements
- Target: 90%+ test coverage
- Use pytest with fixtures
- Mock external API calls
- Test all empathy levels

## Security & Privacy
- Never commit API keys (use .env)
- PII scrubbing before external API calls
- Audit logging for all external requests
- Support air-gapped (fully local) mode

## Documentation Standards
- Docstrings: Google style
- Include "Example:" sections
- Link to relevant levels/concepts
- Keep README.md synchronized

## Git Workflow
- Branch naming: feature/*, fix/*, docs/*
- Commits: Conventional commits format
- PR requirements: tests pass, coverage maintained
- Release: Semantic versioning

## Current Focus (v1.8.0)
- Claude memory integration (CLAUDE.md support)
- Enterprise privacy features (3-tier system)
- PII/secret scrubbing
- Audit logging framework

---
Generated for Empathy Framework v1.8.0
Place this file at: ./.claude/CLAUDE.md in your project
