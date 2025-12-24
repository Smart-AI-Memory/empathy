# Distribution Policy

**Version:** 1.0
**Last Updated:** December 15, 2025
**Applies to:** Empathy Framework v2.2.5+

---

## Philosophy

> **Users get what empowers them, not our development history.**

When users install from PyPI or download from GitHub, they should receive a clean, focused package that helps them succeed. Internal documents, marketing materials, and memory data files are maintained in our repository for team use but excluded from distributions.

---

## What Users Receive

### PyPI Installation (`pip install empathy-framework`)

Users receive the **core framework** needed to use Empathy:

| Category | Included |
|----------|----------|
| **Source Code** | All Python packages (empathy_os, empathy_llm_toolkit, etc.) |
| **Documentation** | README.md, CHANGELOG.md, QUICKSTART.md, CONTRIBUTING.md |
| **Configuration** | pyproject.toml, requirements.txt, example configs |
| **User Docs** | API reference, guides, getting-started, examples |
| **Legal** | LICENSE, CODE_OF_CONDUCT.md, SECURITY.md |

### GitHub Download ZIP / git archive

Same as PyPI, controlled by `.gitattributes` with `export-ignore`.

### git clone (Full Repository)

Developers who clone the repository get **everything**, including internal docs. This is intentional—contributors need full context.

---

## What Is Excluded (and Why)

### 1. Marketing Materials
**Location:** `docs/marketing/`, various root files
**Why:** Internal launch planning, partnership proposals, and competitive analysis are not relevant to users.

Examples:
- `PRODUCT_HUNT.md`, `REDIS_PARTNERSHIP_PLAN.md`
- `PITCH_DECK.md`, `ANTHROPIC_PARTNERSHIP_PROPOSAL.md`
- Social media drafts, demo scripts

### 2. Book Production Files
**Location:** `book-indesign/`, `book-cover/`, `ebook-site/`
**Why:** InDesign files, PDFs, and generated book content are for publishing, not framework usage.

### 3. Memory/Data Files
**Location:** `.empathy/`, `patterns/`, `memdocs_storage/`
**Why:** These are user-generated, environment-specific files. Each user creates their own.

### 4. Infrastructure Files
**Location:** `website/`, `backend/`, `dashboard/`, etc.
**Why:** Deployment infrastructure (Next.js site, FastAPI backend, VS Code extension) is separate from the framework.

Includes:
- `Dockerfile`, `docker-compose.yml`, `railway.toml`
- `website/`, `backend/`, `services/`
- `vscode-memory-panel/`, `dashboard/`

### 5. Development Artifacts
**Location:** Various
**Why:** Test coverage reports, profiling scripts, and cached data are development byproducts.

Includes:
- `htmlcov/`, `coverage.xml`, `security_scan_results.json`
- `profile_*.py`, `benchmark_*.py`
- `.pytest_cache/`, `.mypy_cache/`

### 6. Internal Planning Documents
**Location:** Root directory, `docs/`
**Why:** Phase plans, execution notes, and session summaries are team working documents.

Examples:
- `PHASE2_COMPLETE.md`, `EXECUTION_PLAN.md`
- `SESSION_CONTEXT.json`, `PLANNING.md`
- `docs/PLAN_*.md`, `docs/SESSION_SUMMARY_*.md`

---

## Implementation Files

| File | Controls | Mechanism |
|------|----------|-----------|
| `MANIFEST.in` | PyPI source distributions | Include/exclude directives |
| `.gitattributes` | git archive, GitHub ZIP | `export-ignore` attribute |
| `.gitignore` | Git tracking | Prevents accidental commits |

---

## Adding Exceptions

If a file should be included in distributions despite the default policy:

1. **Remove** from `MANIFEST.in` exclusions
2. **Remove** `export-ignore` from `.gitattributes`
3. **Document** why in this file under "Exceptions"

### Current Exceptions

| File | Reason |
|------|--------|
| `CHANGELOG.md` | Users need version history |
| `CONTRIBUTING.md` | Encourages community participation |
| `SECURITY.md` | Security disclosure information |

---

## Verification

### Test PyPI Distribution
```bash
# Build source distribution
python -m build --sdist

# List contents
tar tzf dist/empathy_framework-*.tar.gz | head -50

# Verify exclusions
tar tzf dist/empathy_framework-*.tar.gz | grep -E "(marketing|book-indesign|patterns)" && echo "ERROR: Found excluded content"
```

### Test Git Archive
```bash
# Create archive
git archive --format=zip HEAD -o test-archive.zip

# List contents
unzip -l test-archive.zip | head -50

# Verify exclusions
unzip -l test-archive.zip | grep -E "(marketing|book-indesign|patterns)" && echo "ERROR: Found excluded content"
```

---

## Maintenance

### When Adding New Files

1. Ask: "Does a user need this to use the framework?"
2. If **yes** → Include (default behavior)
3. If **no** → Add to `MANIFEST.in` exclusions AND `.gitattributes` export-ignore

### Categories That Always Exclude

- Marketing/partnership documents
- Book/publishing files
- Generated data (patterns, memory, coverage)
- Deployment infrastructure
- Internal planning documents

### Quarterly Review

- [ ] Check for new directories that should be excluded
- [ ] Verify no sensitive content in distributions
- [ ] Test build output size is reasonable

---

## Contact

Questions about this policy: patrick.roebuck@smartAImemory.com

---

*This document is excluded from distributions (meta-exclusion).*
