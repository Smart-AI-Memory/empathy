# Dependency Fix Checklist
**Empathy Framework v1.5.0 - Commercial Release Preparation**

Generated: 2025-11-07
Time Budget: 4-6 hours total

---

## Priority 1: CRITICAL FIXES (2 hours) 🚨

Must complete before commercial release to avoid customer ImportErrors and version conflicts.

### Task 1.1: Update setup.py - Move to Optional Dependencies (30 min)
- [ ] Move `anthropic>=0.8.0` from `install_requires` to `extras_require['anthropic']`
- [ ] Move `openai>=1.6.0` from `install_requires` to `extras_require['openai']`
- [ ] Move `langchain>=0.1.0` from `install_requires` to `extras_require['agents']`
- [ ] Move `langchain-core>=0.1.0` from `install_requires` to `extras_require['agents']`
- [ ] Keep only these in `install_requires`:
  - `pydantic>=2.0.0`
  - `typing-extensions>=4.0.0`
  - `python-dotenv>=1.0.0`

**Why:** Users shouldn't be forced to install both Anthropic and OpenAI SDKs if they only use one.

### Task 1.2: Add Missing Dependencies (30 min)
- [ ] Add `langgraph>=0.1.0` to `extras_require['agents']`
- [ ] Add `fastapi>=0.100.0` to `extras_require['backend']`
- [ ] Add `uvicorn>=0.20.0` to `extras_require['backend']`
- [ ] Add `pygls>=1.0.0` to `extras_require['lsp']`
- [ ] Add `lsprotocol>=2023.0.0` to `extras_require['lsp']`
- [ ] Add `python-docx>=1.0.0` to `extras_require['docs']`

**Why:** Backend and agents directories will fail with ImportError without these.

### Task 1.3: Add Upper Version Bounds (45 min)
Update all dependencies with upper bounds to prevent breaking changes:

**Core dependencies:**
- [ ] `pydantic>=2.0.0,<3.0.0` (was: `>=2.0.0`)
- [ ] `typing-extensions>=4.0.0,<5.0.0` (was: `>=4.0.0`)
- [ ] `python-dotenv>=1.0.0,<2.0.0` (was: `>=1.0.0`)

**Optional - LLM providers:**
- [ ] `anthropic>=0.8.0,<1.0.0` (was: `>=0.8.0`)
- [ ] `openai>=1.6.0,<2.0.0` (was: `>=1.6.0`)

**Optional - Agents:**
- [ ] `langchain>=0.1.0,<0.2.0` (was: `>=0.1.0`)
- [ ] `langchain-core>=0.1.0,<0.2.0` (was: `>=0.1.0`)
- [ ] `langgraph>=0.1.0,<0.2.0` (NEW)

**Optional - Backend:**
- [ ] `fastapi>=0.100.0,<1.0.0` (NEW)
- [ ] `uvicorn[standard]>=0.20.0,<1.0.0` (NEW)

**Optional - Dev:**
- [ ] `pytest>=7.0,<8.0` (was: `>=7.0`)
- [ ] `pytest-asyncio>=0.21,<1.0` (was: `>=0.21`)
- [ ] `black>=23.0,<25.0` (was: `>=23.0`)
- [ ] `mypy>=1.0,<2.0` (was: `>=1.0`)
- [ ] `ruff>=0.1,<1.0` (was: `>=0.1`)

**Why:** Without upper bounds, `pip install empathy-framework` could pull pydantic 10.0 in 2030 and break.

### Task 1.4: Update Python Version Requirement (15 min)
- [ ] Change `python_requires=">=3.9"` to `python_requires=">=3.10"`
- [ ] Update classifiers to remove `"Programming Language :: Python :: 3.9"`
- [ ] Document Python 3.9 deprecation in CHANGELOG

**Why:** Python 3.9 reaches EOL in October 2025 (6 months away). Supporting EOL Python is a security risk.

---

## Priority 2: DOCUMENTATION (1 hour) 📝

Critical for customer onboarding and reducing support burden.

### Task 2.1: Update README.md - Installation Section (30 min)
Add installation examples showing optional extras:

```markdown
## Installation

### Basic Installation (Core Framework Only)
```bash
pip install empathy-framework
```
Includes: Core empathy patterns, state management, basic LLM interface

### With Anthropic Claude
```bash
pip install empathy-framework[anthropic]
```

### With OpenAI GPT
```bash
pip install empathy-framework[openai]
```

### With Backend API
```bash
pip install empathy-framework[backend,openai]
```

### With Agents (LangChain/LangGraph)
```bash
pip install empathy-framework[agents]
```

### Complete Installation (All Features)
```bash
pip install empathy-framework[all]
```

### For Development
```bash
pip install empathy-framework[all,dev]
```

## Optional Extras

| Extra | Includes | Use Case |
|-------|----------|----------|
| `anthropic` | Anthropic SDK | Use Claude models |
| `openai` | OpenAI SDK | Use GPT models |
| `agents` | LangChain, LangGraph | Use agent workflows |
| `backend` | FastAPI, uvicorn | Run backend API server |
| `lsp` | pygls, lsprotocol | Run LSP server examples |
| `docs` | python-docx | Generate Word docs |
| `all` | All of the above | Full installation |
| `dev` | Testing, linting tools | Development |
```

**Checklist:**
- [ ] Add installation section to README
- [ ] Create table of optional extras
- [ ] Add examples for each use case
- [ ] Document what's included in minimal install

### Task 2.2: Create DEPENDENCIES.md (30 min)
- [ ] List all direct dependencies with licenses
- [ ] Add attribution for MIT/Apache libraries
- [ ] Document version ranges and why
- [ ] Link to LICENSE file

**Template:**
```markdown
# Dependencies

## Core Dependencies
- pydantic (2.0.0 - 3.0.0) - MIT License
- typing-extensions (4.0.0 - 5.0.0) - PSF-2.0 License
- python-dotenv (1.0.0 - 2.0.0) - BSD-3-Clause License

## Optional Dependencies
[... etc ...]

## License Compliance
All dependencies use MIT, Apache-2.0, BSD, or PSF licenses.
Commercial distribution is permitted under these licenses.
```

---

## Priority 3: TESTING (2 hours) ✅

Validate that fixes work and don't break existing functionality.

### Task 3.1: Test Minimal Installation (30 min)
- [ ] Create fresh Python 3.10 virtualenv
- [ ] Run: `pip install empathy-framework` (no extras)
- [ ] Test: Can import empathy_llm_toolkit
- [ ] Test: Can import empathy_os
- [ ] Test: Cannot import langchain (should fail gracefully)
- [ ] Test: Cannot import fastapi (should fail gracefully)
- [ ] Verify: Core patterns work without LLM providers

**Expected behavior:**
```python
# Should work
from empathy_llm_toolkit import EmpathyLLM
from empathy_os import PatternLibrary

# Should fail gracefully with helpful error
try:
    from empathy_llm_toolkit.providers import AnthropicProvider
except ImportError as e:
    print("Install with: pip install empathy-framework[anthropic]")
```

### Task 3.2: Test Optional Installations (45 min)
Test each optional extra works independently:

- [ ] Test: `pip install empathy-framework[anthropic]`
  - Verify: Can import AnthropicProvider
  - Verify: Can create Anthropic client
- [ ] Test: `pip install empathy-framework[openai]`
  - Verify: Can import OpenAIProvider
  - Verify: Can create OpenAI client
- [ ] Test: `pip install empathy-framework[backend]`
  - Verify: Can import fastapi
  - Verify: Can run backend/main.py
- [ ] Test: `pip install empathy-framework[agents]`
  - Verify: Can import langgraph
  - Verify: Can run agents/compliance_anticipation_agent.py
- [ ] Test: `pip install empathy-framework[all]`
  - Verify: All imports work
  - Verify: All examples run

### Task 3.3: Test Version Bounds (30 min)
Verify upper bounds prevent incompatible versions:

- [ ] Test: `pip install empathy-framework "pydantic==3.0.0"` (should fail with conflict)
- [ ] Test: `pip install empathy-framework "anthropic==1.0.0"` (should fail with conflict)
- [ ] Document: What happens when bounds are hit

### Task 3.4: Integration Testing (15 min)
- [ ] Test: Install in fresh Python 3.10 venv
- [ ] Test: Install in fresh Python 3.11 venv
- [ ] Test: Install in fresh Python 3.12 venv
- [ ] Verify: All versions work correctly

---

## Priority 4: CI/CD & MONITORING (1 hour) 🔒

Set up ongoing dependency monitoring and security checks.

### Task 4.1: Add Safety Checks (20 min)
- [ ] Add `safety>=2.0,<3.0` to dev dependencies
- [ ] Create `.github/workflows/security.yml` (if using GitHub Actions)
- [ ] Add to CI: `safety check --json`
- [ ] Configure alerts for CVEs

**Example workflow:**
```yaml
name: Security Check
on: [push, pull_request, schedule]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run safety check
        run: |
          pip install safety
          safety check --json
```

### Task 4.2: Configure Dependabot (15 min)
- [ ] Create `.github/dependabot.yml`
- [ ] Configure for pip dependencies
- [ ] Set update frequency to weekly
- [ ] Configure auto-merge for patch versions

**Example config:**
```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

### Task 4.3: Document Update Policy (25 min)
Create `DEPENDENCY_POLICY.md`:
- [ ] Quarterly dependency review schedule
- [ ] Security patch response time (48 hours for critical)
- [ ] Major version upgrade policy
- [ ] Communication plan for breaking changes

---

## Validation Checklist ✅

Before marking complete, verify:

### Installation Works
- [ ] `pip install empathy-framework` succeeds
- [ ] `pip install empathy-framework[all]` succeeds
- [ ] Core imports work without errors
- [ ] Optional imports work when extras installed

### Version Bounds Work
- [ ] pip shows correct version ranges
- [ ] Incompatible versions are rejected
- [ ] Upper bounds prevent future breakage

### Documentation Complete
- [ ] README has installation instructions
- [ ] Optional extras are documented
- [ ] Dependencies are listed with licenses
- [ ] Migration guide exists (if needed)

### Tests Pass
- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Examples run successfully
- [ ] No import errors

### Security
- [ ] Safety check passes
- [ ] No known CVEs
- [ ] Dependabot configured
- [ ] Update policy documented

---

## Time Tracking

| Priority | Tasks | Estimated | Actual | Status |
|----------|-------|-----------|--------|--------|
| P1: Critical Fixes | 4 tasks | 2h 00m | ___ | ⬜ |
| P2: Documentation | 2 tasks | 1h 00m | ___ | ⬜ |
| P3: Testing | 4 tasks | 2h 00m | ___ | ⬜ |
| P4: CI/CD | 3 tasks | 1h 00m | ___ | ⬜ |
| **TOTAL** | **13 tasks** | **6h 00m** | ___ | ⬜ |

---

## Quick Commands

### Create test virtualenv
```bash
python3.10 -m venv test_env
source test_env/bin/activate
pip install --upgrade pip
```

### Test minimal install
```bash
pip install .
python -c "from empathy_llm_toolkit import EmpathyLLM; print('Core works!')"
```

### Test with extras
```bash
pip install .[anthropic]
python -c "from empathy_llm_toolkit.providers import AnthropicProvider; print('Anthropic works!')"
```

### Generate requirements lock file
```bash
pip freeze > requirements-lock.txt
```

### Check for security issues
```bash
pip install safety
safety check
```

---

## Notes

- See `DEPENDENCY_AUDIT.md` for full analysis (730 lines)
- See `DEPENDENCY_AUDIT_SUMMARY.txt` for executive summary
- All changes should be backward compatible for existing users
- Document breaking changes in CHANGELOG.md

---

## Success Criteria

✅ Minimal install works (`pip install empathy-framework`)
✅ All extras work independently
✅ Version bounds prevent future breakage
✅ Documentation is clear and complete
✅ No security vulnerabilities
✅ CI/CD monitors dependencies
✅ Ready for commercial release

---

**Once complete, this framework will be production-ready for commercial distribution at $99/developer/year.**
