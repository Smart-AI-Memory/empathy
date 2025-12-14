# Documentation Pipeline Plan: Adobe + GitBook Integration

**Created:** December 14, 2025
**Status:** Planning
**Goal:** Professional book publishing + sustainable documentation pipeline

---

## Executive Summary

Create a multi-output documentation pipeline that:
1. **Short term**: Produces polished PDFs for Gumroad sales ($5+)
2. **Long term**: Supports ongoing documentation with multiple output formats
3. **Maintains single source of truth**: Markdown files in the repository

---

## Current State

| Component | Current Tool | Output | Quality |
|-----------|-------------|--------|---------|
| Source | Markdown (.md files) | - | - |
| Web docs | MkDocs Material | HTML | Good |
| PDF export | mkdocs-with-pdf | PDF | Basic/Plain |
| Sales | Gumroad | PDF download | Functional |

**Pain points:**
- PDF is "very plain" compared to web version
- No professional typography
- Limited interactivity options
- Manual process for updates

---

## Proposed Architecture

```
                         ┌──────────────────────────────────┐
                         │     MARKDOWN SOURCE              │
                         │     (Single Source of Truth)     │
                         │     docs/*.md                    │
                         └────────────────┬─────────────────┘
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            │                             │                             │
            ▼                             ▼                             ▼
    ┌───────────────┐            ┌───────────────┐            ┌───────────────┐
    │   WEB DOCS    │            │  BOOK (PDF)   │            │   GITBOOK     │
    │               │            │               │            │               │
    │  MkDocs       │            │  Adobe        │            │  GitBook.com  │
    │  Material     │            │  InDesign/    │            │  (hosted)     │
    │               │            │  Acrobat      │            │               │
    └───────┬───────┘            └───────┬───────┘            └───────┬───────┘
            │                             │                             │
            ▼                             ▼                             ▼
    ┌───────────────┐            ┌───────────────┐            ┌───────────────┐
    │  docs site    │            │  Gumroad      │            │  Public docs  │
    │  (self-host)  │            │  ($5+ sales)  │            │  (discovery)  │
    └───────────────┘            └───────────────┘            └───────────────┘
```

---

## Option A: Adobe Integration

### A1. Adobe InDesign (Manual, Highest Quality)

**Workflow:**
```
Markdown → Pandoc → ICML/HTML → InDesign → PDF
```

**Process:**
1. Export markdown to InDesign-compatible format (ICML or HTML)
2. Import into InDesign template with professional styling
3. Manual adjustments for typography, widows/orphans, page breaks
4. Export high-quality PDF for Gumroad

**Pros:**
- Highest quality output
- Full control over typography
- Print-ready if physical books desired later
- One-time template creation, reusable

**Cons:**
- Requires InDesign license (~$23/month)
- Manual step for each major update
- Learning curve if unfamiliar

**Best for:** Major releases (v1.0, v2.0), when quality matters most

---

### A2. Adobe Acrobat Pro (PDF Enhancement)

**Workflow:**
```
Markdown → MkDocs PDF → Acrobat Pro → Enhanced PDF
```

**Process:**
1. Generate basic PDF with current mkdocs-with-pdf
2. Open in Acrobat Pro
3. Add interactivity: bookmarks, links, buttons
4. Optimize: compress, add metadata, accessibility tags
5. Export for Gumroad

**Pros:**
- Enhances existing workflow
- Adds interactivity (buttons, links)
- Accessibility features (tags, alt text)
- Moderate cost (~$15/month)

**Cons:**
- Manual post-processing step
- Doesn't improve base typography much
- Still starts from "plain" PDF

**Best for:** Quick enhancements to existing PDFs

---

### A3. Adobe PDF Services API (Automated)

**Workflow:**
```
Markdown → HTML → Adobe API → PDF
```

**Process:**
1. Build script sends HTML to Adobe API
2. API returns PDF
3. Automated as part of CI/CD

**Pros:**
- Fully automated
- Good quality from HTML source
- Pay-per-use pricing

**Cons:**
- Costs money per operation
- Requires API integration work
- Less control than InDesign

**Pricing:** ~$0.05 per PDF operation (first 500/month may be free)

**Best for:** Automated pipeline at scale

---

### Adobe Recommendation

**Short term (next 2 weeks):**
- Use **Acrobat Pro** to enhance the current PDF
- Add professional bookmarks, optimize, add metadata
- Quick win, immediate quality improvement

**Medium term (next 1-2 months):**
- Create **InDesign template** for the book
- Import content, do professional layout
- Generate "Empathy Book v2.0" premium PDF

**Long term:**
- Evaluate **PDF Services API** for automation
- Or maintain InDesign workflow for major releases only

---

## Option B: GitBook Integration

### What GitBook Offers

| Feature | Description |
|---------|-------------|
| **Hosted docs** | yourbook.gitbook.io (or custom domain) |
| **GitHub sync** | Bi-directional sync with repository |
| **Modern UI** | Clean, searchable, mobile-friendly |
| **Versioning** | Multiple versions (v1, v2, latest) |
| **Analytics** | See what people read |
| **API access** | Programmatic content updates |
| **PDF export** | Built-in (quality varies) |
| **Team editing** | Collaborative, non-technical editors |

### GitBook Pricing

| Plan | Cost | Features |
|------|------|----------|
| **Free** | $0 | 1 public space, basic features |
| **Plus** | $8/user/mo | Custom domain, analytics, PDF export |
| **Pro** | $15/user/mo | Advanced permissions, API, SSO |

### GitBook Workflow

```
┌─────────────────────────────────────────────────────────────┐
│  GitHub Repository                                          │
│  └── docs/                                                  │
│       ├── guides/                                           │
│       ├── examples/                                         │
│       └── SUMMARY.md (GitBook navigation)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │ GitHub Sync (automatic)
                      ▼
┌─────────────────────────────────────────────────────────────┐
│  GitBook.com                                                │
│  ├── Live documentation site                                │
│  ├── Search, navigation, mobile                             │
│  ├── Version control (v1.0, v2.0, latest)                   │
│  └── PDF export option                                      │
└─────────────────────────────────────────────────────────────┘
```

### GitBook vs MkDocs Comparison

| Aspect | MkDocs (current) | GitBook |
|--------|------------------|---------|
| **Hosting** | Self-hosted or ReadTheDocs | GitBook.com (managed) |
| **Setup** | More technical | Easier |
| **Customization** | Full control (CSS, plugins) | Limited to their themes |
| **GitHub sync** | Manual deploy | Automatic |
| **PDF quality** | Plugin-dependent | Built-in, moderate quality |
| **Search** | Basic | Better |
| **Analytics** | Need to add | Built-in |
| **Cost** | Free (self-host) | Free tier or $8+/mo |
| **Interactive embeds** | Custom work | Some built-in integrations |

### GitBook Recommendation

**Use GitBook for:**
- Public-facing documentation (discovery, SEO)
- Non-technical contributors who need to edit
- Quick setup without DevOps overhead
- Built-in analytics

**Keep MkDocs for:**
- Full customization needs
- Self-hosted requirements
- Complex plugins (code from source, etc.)

**Hybrid approach:**
- MkDocs for detailed API reference (code integration)
- GitBook for user guides, getting started, philosophy

---

## Proposed Pipeline: Unified Architecture

### The Stack

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MARKDOWN SOURCE                               │
│                        (Repository: docs/)                           │
└─────────────────────────────────┬───────────────────────────────────┘
                                  │
        ┌─────────────────────────┴─────────────────────────┐
        │                    BUILD SYSTEM                    │
        │              (Makefile or GitHub Actions)          │
        └─────────────────────────┬─────────────────────────┘
                                  │
    ┌─────────────┬───────────────┼───────────────┬─────────────┐
    │             │               │               │             │
    ▼             ▼               ▼               ▼             ▼
┌───────┐   ┌───────────┐   ┌───────────┐   ┌─────────┐   ┌─────────┐
│MkDocs │   │  GitBook  │   │  InDesign │   │  Pandoc │   │  Pandoc │
│       │   │  (sync)   │   │  (manual) │   │  → PDF  │   │  → DOCX │
└───┬───┘   └─────┬─────┘   └─────┬─────┘   └────┬────┘   └────┬────┘
    │             │               │              │             │
    ▼             ▼               ▼              ▼             ▼
┌───────┐   ┌───────────┐   ┌───────────┐   ┌─────────┐   ┌─────────┐
│ HTML  │   │  Hosted   │   │  Premium  │   │  Basic  │   │  Word   │
│ Site  │   │  Docs     │   │  PDF      │   │  PDF    │   │  Doc    │
│       │   │           │   │  (Gumroad)│   │  (free) │   │  (edit) │
└───────┘   └───────────┘   └───────────┘   └─────────┘   └─────────┘
```

### Output Channels

| Output | Tool | Purpose | Audience |
|--------|------|---------|----------|
| **docs.smartaimemory.com** | MkDocs | Full reference, API docs | Developers |
| **empathy.gitbook.io** | GitBook | Getting started, guides | Broader audience |
| **empathy-book-premium.pdf** | InDesign | Paid book | Gumroad customers |
| **empathy-book-basic.pdf** | Pandoc | Free/preview | Lead generation |
| **empathy-book.docx** | Pandoc | Editing, collaboration | Internal/partners |

---

## Implementation Phases

### Phase 1: Quick Wins (This Week)

**Goal:** Improve PDF quality with minimal effort

1. **Enhance current PDF with Acrobat Pro**
   - Add proper bookmarks/TOC
   - Add document metadata (author, title, keywords)
   - Optimize file size
   - Add clickable links throughout

2. **Add Pandoc DOCX export**
   - Create `make book-docx` target
   - Use professional Word template
   - Enables editing workflow

**Deliverables:**
- Enhanced PDF for Gumroad
- Word document for editing

---

### Phase 2: GitBook Setup (Next Week)

**Goal:** Establish GitBook as public documentation channel

1. **Create GitBook space**
   - Connect to GitHub repository
   - Configure SUMMARY.md for navigation
   - Set up custom domain (optional)

2. **Curate content for GitBook**
   - Select user-facing guides (not API reference)
   - May need SUMMARY.md separate from mkdocs nav

3. **Configure sync**
   - Enable GitHub sync
   - Test bi-directional updates

**Deliverables:**
- Live GitBook site
- GitHub sync working

---

### Phase 3: InDesign Template (Next Month)

**Goal:** Professional book PDF for sales

1. **Create InDesign template**
   - Cover page design
   - Chapter opener styling
   - Body text typography (professional)
   - Code block styling
   - Table styling
   - Headers/footers with page numbers

2. **Build import workflow**
   - Pandoc → ICML export script
   - or HTML → Place in InDesign
   - Document the process

3. **Produce v2.0 PDF**
   - Full book layout
   - Quality review
   - Upload to Gumroad

**Deliverables:**
- InDesign template (reusable)
- Premium PDF on Gumroad
- Documented workflow

---

### Phase 4: Automation (Future)

**Goal:** Reduce manual steps

1. **GitHub Actions integration**
   - Auto-build on merge to main
   - Deploy MkDocs site
   - Trigger GitBook sync
   - Generate Pandoc outputs

2. **Consider Adobe PDF Services API**
   - Evaluate cost vs. manual InDesign
   - Implement if volume justifies

**Deliverables:**
- Automated pipeline
- Documentation on process

---

## Gumroad Considerations

### Current Setup
- **Product:** "Empathy: A Framework for AI-Human Collaboration"
- **Pricing:** $5 minimum, pay-what-you-want
- **Format:** PDF download

### Gumroad Limitations

| Constraint | Impact | Workaround |
|------------|--------|------------|
| **Static files only** | No live interactivity in PDF | Links to website for demos |
| **No DRM** | Files can be shared | Accept this; build community value |
| **Update workflow** | Must re-upload, email customers | Version the PDFs clearly |
| **File size** | 16GB limit (not an issue) | - |
| **Format support** | PDF, EPUB, etc. | Standard formats work |

### Gumroad Strategy

**Tiered Products (possible):**
```
Free Tier:      "Empathy Quick Start" (sample chapters)
                → Leads to paid version

$5+ Tier:       "Empathy: Complete Book" (full PDF)
                → Current offering

$15+ Tier:      "Empathy: Premium Edition" (future)
                → InDesign-quality PDF
                → Bonus content
                → Video walkthroughs
```

**Version Updates:**
- Name files with version: `empathy-book-v2.0.pdf`
- Use Gumroad's update notification feature
- Customers get email when new version uploaded

**Linking to Interactive Content:**
Since Gumroad PDFs are static, include:
- Clear links: "Try the live demo at smartaimemory.com/demo/tech-debt"
- QR codes (for print readers)
- "This book includes online interactive demos" messaging

---

## Cost Summary

| Tool | Cost | Frequency | Purpose |
|------|------|-----------|---------|
| **Adobe Acrobat Pro** | ~$15/mo | Ongoing | PDF enhancement |
| **Adobe InDesign** | ~$23/mo | As needed | Premium book layout |
| **GitBook Plus** | $8/mo | Ongoing | Hosted docs |
| **Pandoc** | Free | - | DOCX/PDF generation |
| **MkDocs** | Free | - | Web docs |

**Minimum viable:** Acrobat Pro ($15/mo) + GitBook Free = $15/mo
**Full pipeline:** InDesign + Acrobat + GitBook Plus = ~$46/mo

---

## Decision Points

### For Discussion:

1. **GitBook Free vs Plus?**
   - Free: 1 public space, basic features
   - Plus: Custom domain, analytics, better PDF export

2. **InDesign: Subscribe now or later?**
   - Now: Can produce premium PDF for launch
   - Later: Use enhanced MkDocs PDF for now

3. **Dual documentation (MkDocs + GitBook)?**
   - Pro: Different audiences served optimally
   - Con: Maintenance overhead, sync complexity

4. **Who handles InDesign work?**
   - Learn it yourself (time investment)
   - Hire designer for template (one-time cost)
   - Use Acrobat enhancement only (simpler)

---

## Next Steps

1. [ ] Review this plan
2. [ ] Decide on GitBook: Free or Plus?
3. [ ] Decide on Adobe: Acrobat only or InDesign too?
4. [ ] Implement Phase 1 (PDF enhancement)
5. [ ] Set up GitBook space

---

*This plan balances short-term needs (better PDF for Tuesday launch) with long-term sustainability (proper publishing pipeline).*
