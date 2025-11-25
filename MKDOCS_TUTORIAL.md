# MkDocs Tutorial - Complete Beginner's Guide

**For**: Patrick (never used MkDocs before)
**Goal**: Create professional documentation website for Empathy Framework v1.8.0
**Time**: 30-45 minutes to get fully productive

---

## What is MkDocs?

**MkDocs** is a static site generator specifically designed for project documentation.

**Think of it like**:
- Write docs in **Markdown** (same as README.md files you're familiar with)
- MkDocs converts them to a **beautiful website**
- Automatic **navigation**, **search**, **mobile-responsive**
- Deploy to **Read the Docs** (free hosting for open source)

**Why MkDocs for Empathy Framework?**
- ✅ Python-based (fits our ecosystem)
- ✅ Simple (just write Markdown)
- ✅ Beautiful (Material theme = modern, professional)
- ✅ Fast (builds in seconds)
- ✅ Auto-deploy (GitHub → Read the Docs automatic updates)

**Popular projects using MkDocs**:
- FastAPI (https://fastapi.tiangolo.com)
- Django REST framework
- Pydantic

---

## Installation (5 minutes)

### Step 1: Install MkDocs

```bash
# Basic MkDocs
pip install mkdocs

# MkDocs with Material theme (recommended)
pip install mkdocs-material

# Auto-generate API docs from docstrings
pip install mkdocstrings[python]

# All at once
pip install mkdocs mkdocs-material mkdocstrings[python]
```

### Step 2: Verify Installation

```bash
mkdocs --version
# Output: mkdocs, version 1.5.3
```

✅ If you see a version number, you're ready!

---

## Quick Start (10 minutes)

### Create Your First MkDocs Site

```bash
# Navigate to your project
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework

# Create new MkDocs project
mkdocs new .
```

**What this creates**:
```
Empathy-framework/
├── mkdocs.yml          # Configuration file (controls everything)
└── docs/               # Your documentation files
    └── index.md        # Homepage (like README.md)
```

### Preview Your Site

```bash
# Start live preview server
mkdocs serve
```

**Output**:
```
INFO    -  Building documentation...
INFO    -  Cleaning site directory
INFO    -  Documentation built in 0.23 seconds
INFO    -  [15:30:00] Watching paths for changes: 'docs', 'mkdocs.yml'
INFO    -  [15:30:00] Serving on http://127.0.0.1:8000/
```

**Open browser**: http://127.0.0.1:8000

🎉 You'll see a basic documentation website!

**Key feature**: **Live reload** - Edit any `.md` file in `docs/`, save, and the browser auto-refreshes!

---

## Understanding the Structure

### The `mkdocs.yml` File (Your Control Panel)

This is where ALL configuration happens. Think of it as your website's "settings file".

**Default `mkdocs.yml`**:
```yaml
site_name: My Docs
```

**Basic Empathy Framework `mkdocs.yml`**:
```yaml
site_name: Empathy Framework
site_description: Production-ready Level 4 Anticipatory Intelligence
site_author: Patrick Roebuck
site_url: https://empathy-framework.readthedocs.io

# Repository
repo_name: Smart-AI-Memory/empathy-framework
repo_url: https://github.com/Smart-AI-Memory/empathy-framework

# Navigation
nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
  - Examples:
      - Simple Chatbot: examples/simple-chatbot.md
      - SBAR Healthcare: examples/sbar-clinical-handoff.md

# Theme
theme:
  name: material
  palette:
    primary: indigo
    accent: indigo
```

---

## Step-by-Step: Building Empathy Docs

### Step 1: Configure `mkdocs.yml`

Create this file at the root of your project:

```yaml
# Site Information
site_name: Empathy Framework
site_description: Production-ready Level 4 Anticipatory Intelligence for AI-human collaboration
site_author: Patrick Roebuck
site_url: https://empathy-framework.readthedocs.io

# Repository
repo_name: Smart-AI-Memory/empathy-framework
repo_url: https://github.com/Smart-AI-Memory/empathy-framework
edit_uri: edit/main/docs/

# Copyright
copyright: Copyright &copy; 2025 Smart-AI-Memory

# Navigation Structure
nav:
  - Home: index.md
  - Getting Started:
      - Installation: getting-started/installation.md
      - Quick Start: getting-started/quickstart.md
      - Configuration: getting-started/configuration.md
      - First Application: getting-started/first-application.md

  - Concepts:
      - Empathy Levels: concepts/empathy-levels.md
      - Trust Building: concepts/trust-building.md
      - Pattern Library: concepts/pattern-library.md
      - Anticipatory Intelligence: concepts/anticipatory-intelligence.md

  - Examples:
      - Simple Chatbot: examples/simple-chatbot.md
      - SBAR Clinical Handoff: examples/sbar-clinical-handoff.md
      - Multi-Agent Coordination: examples/multi-agent-team-coordination.md
      - Adaptive Learning: examples/adaptive-learning-system.md
      - Webhook Integration: examples/webhook-event-integration.md

  - API Reference:
      - EmpathyOS: api-reference/empathy-os.md
      - Configuration: api-reference/config.md
      - Persistence: api-reference/persistence.md
      - Events: api-reference/events.md

  - Guides:
      - Healthcare Applications: guides/healthcare-applications.md
      - HIPAA Compliance: guides/hipaa-compliance.md
      - Multi-Agent Coordination: guides/multi-agent-coordination.md
      - Adaptive Learning: guides/adaptive-learning.md

  - Contributing: contributing.md

# Theme Configuration (Material)
theme:
  name: material

  # Color scheme
  palette:
    # Light mode
    - media: "(prefers-color-scheme: light)"
      scheme: default
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-7
        name: Switch to dark mode

    # Dark mode
    - media: "(prefers-color-scheme: dark)"
      scheme: slate
      primary: indigo
      accent: indigo
      toggle:
        icon: material/brightness-4
        name: Switch to light mode

  # Features
  features:
    - navigation.instant      # Fast page loads
    - navigation.tracking     # URL updates as you scroll
    - navigation.tabs         # Top-level sections as tabs
    - navigation.sections     # Sections in sidebar
    - navigation.expand       # Expand all sections by default
    - navigation.top          # "Back to top" button
    - search.suggest          # Search suggestions
    - search.highlight        # Highlight search terms
    - content.code.copy       # Copy button on code blocks

  # Logo and favicon
  icon:
    logo: material/brain
  favicon: assets/favicon.png

  # Font
  font:
    text: Roboto
    code: Roboto Mono

# Plugins
plugins:
  - search                    # Search functionality
  - mkdocstrings:             # Auto-generate API docs from docstrings
      handlers:
        python:
          options:
            docstring_style: google
            show_source: true
            show_root_heading: true

# Markdown Extensions
markdown_extensions:
  - pymdownx.highlight:       # Code highlighting
      anchor_linenums: true
  - pymdownx.superfences      # Nested code blocks
  - pymdownx.tabbed:          # Tabbed content
      alternate_style: true
  - pymdownx.details          # Collapsible sections
  - admonition                # Call-out boxes (note, warning, etc.)
  - tables                    # Markdown tables
  - toc:                      # Table of contents
      permalink: true

# Extra
extra:
  social:
    - icon: fontawesome/brands/github
      link: https://github.com/Smart-AI-Memory/empathy-framework
    - icon: fontawesome/brands/python
      link: https://pypi.org/project/empathy-framework/

  version:
    provider: mike
```

### Step 2: Create Directory Structure

```bash
mkdir -p docs/getting-started
mkdir -p docs/concepts
mkdir -p docs/examples
mkdir -p docs/api-reference
mkdir -p docs/guides
mkdir -p docs/assets
```

**Your structure**:
```
docs/
├── index.md                          # Homepage
├── getting-started/
│   ├── installation.md
│   ├── quickstart.md
│   ├── configuration.md
│   └── first-application.md
├── concepts/
│   ├── empathy-levels.md
│   ├── trust-building.md
│   ├── pattern-library.md
│   └── anticipatory-intelligence.md
├── examples/
│   ├── simple-chatbot.md             # Already created!
│   ├── sbar-clinical-handoff.md      # Already created!
│   ├── multi-agent-team-coordination.md  # Already created!
│   ├── adaptive-learning-system.md   # Already created!
│   └── webhook-event-integration.md  # Already created!
├── api-reference/
│   ├── empathy-os.md
│   ├── config.md
│   └── persistence.md
├── guides/
│   ├── healthcare-applications.md
│   ├── hipaa-compliance.md
│   └── multi-agent-coordination.md
├── assets/
│   └── favicon.png
└── contributing.md
```

### Step 3: Write the Homepage (`docs/index.md`)

```markdown
# Empathy Framework

**Production-ready Level 4 Anticipatory Intelligence for AI-human collaboration**

[![PyPI version](https://badge.fury.io/py/empathy-framework.svg)](https://pypi.org/project/empathy-framework/)
[![Tests](https://github.com/Smart-AI-Memory/empathy-framework/workflows/tests/badge.svg)](https://github.com/Smart-AI-Memory/empathy-framework/actions)
[![Coverage](https://codecov.io/gh/Smart-AI-Memory/empathy-framework/branch/main/graph/badge.svg)](https://codecov.io/gh/Smart-AI-Memory/empathy-framework)

---

## What is Empathy Framework?

The Empathy Framework is a **5-level maturity model** for AI-human collaboration that progresses from reactive responses (Level 1) to **Level 4 Anticipatory Intelligence** that predicts problems before they happen.

### The 5 Levels

| Level | Name | Description | Example |
|-------|------|-------------|---------|
| **1** | Reactive | Responds only when asked | Basic Q&A chatbot |
| **2** | Guided | Asks clarifying questions | Assistant that seeks context |
| **3** | Proactive | Notices patterns, offers improvements | Suggests optimizations |
| **4** | Anticipatory | **Predicts problems before they happen** | Warns about deployment risks |
| **5** | Transformative | Reshapes workflows to prevent entire classes of problems | Creates new protocols |

---

## Quick Start

### Installation

```bash
pip install empathy-framework
```

### 5-Minute Example

```python
from empathy_os import EmpathyOS

# Create Level 4 (Anticipatory) chatbot
empathy = EmpathyOS(
    user_id="user_123",
    target_level=4,
    confidence_threshold=0.75
)

# Interact
response = empathy.interact(
    user_id="user_123",
    user_input="I'm about to deploy this API change to production",
    context={"deployment": "production", "changes": ["auth_refactor"]}
)

print(response.response)
# Output: "🔮 Prediction: This authentication refactor may break mobile
#          app compatibility (uses old auth flow). Recommend deploying
#          behind feature flag first. Confidence: 87%"
```

---

## Key Features

### 🧠 Anticipatory Intelligence
Predict problems 30-90 days in advance with Level 4 capabilities.

### 🏥 Healthcare Ready
HIPAA-compliant with clinical protocols (SBAR, TIME, ABCDE). **$2M+ annual value** for 100-bed hospitals.

### 🤝 Multi-Agent Coordination
Specialized agents work together through shared pattern libraries. **80% faster feature delivery**.

### 📈 Adaptive Learning
System learns YOUR preferences over time. **+28% acceptance rate improvement**.

### 🔗 Full Ecosystem Integration
Webhooks for Slack, GitHub, JIRA, Datadog, and custom services.

---

## Use Cases

=== "Software Development"

    - **Code Review**: Level 4 predictions for merge conflicts
    - **Security**: Anticipate vulnerabilities before deployment
    - **Team Coordination**: Multi-agent collaboration
    - **Performance**: Predict scaling issues

=== "Healthcare"

    - **Patient Handoffs**: Automated SBAR reports (60% time savings)
    - **Clinical Protocols**: HIPAA-compliant monitoring
    - **Safety Alerts**: Real-time critical condition detection
    - **EHR Integration**: Epic, Cerner FHIR support

=== "Finance"

    - **Risk Management**: Predict compliance issues
    - **Trading**: Pattern recognition across markets
    - **Audit**: Automated anomaly detection
    - **Reporting**: Anticipatory report generation

---

## Documentation

- **[Getting Started](getting-started/installation.md)**: Install and configure
- **[Examples](examples/simple-chatbot.md)**: 5 comprehensive tutorials
- **[API Reference](api-reference/empathy-os.md)**: Complete API documentation
- **[Guides](guides/healthcare-applications.md)**: Domain-specific guides

---

## Performance Metrics

### Healthcare Impact
- **Time savings**: 60% reduction in documentation time
- **Annual value**: $2M+ for 100-bed hospital
- **Safety**: Zero false negatives in critical alerts

### Software Development
- **Feature delivery**: 80% faster (8 days → 4 days)
- **Acceptance rate**: +28% improvement with adaptive learning
- **Pattern reuse**: 68% across team members

---

## License

**Fair Source License 0.9**
- ✅ Free for students, educators, teams ≤5 employees
- 💰 $99/developer/year for teams 6+ employees
- 🔄 Auto-converts to Apache 2.0 on January 1, 2029

---

## Next Steps

<div class="grid cards" markdown>

-   :material-clock-fast:{ .lg .middle } __5-Minute Start__

    ---

    Get up and running in 5 minutes

    [:octicons-arrow-right-24: Quick Start](getting-started/quickstart.md)

-   :fontawesome-solid-robot:{ .lg .middle } __Examples__

    ---

    5 comprehensive tutorials with working code

    [:octicons-arrow-right-24: See Examples](examples/simple-chatbot.md)

-   :fontawesome-solid-hospital:{ .lg .middle } __Healthcare__

    ---

    HIPAA-compliant, $2M+ ROI

    [:octicons-arrow-right-24: Healthcare Guide](guides/healthcare-applications.md)

-   :material-book-open-variant:{ .lg .middle } __API Reference__

    ---

    Complete API documentation

    [:octicons-arrow-right-24: API Docs](api-reference/empathy-os.md)

</div>
```

### Step 4: Create a Getting Started Guide

**File**: `docs/getting-started/installation.md`

```markdown
# Installation

## Prerequisites

- **Python**: 3.10 or higher
- **pip**: Latest version recommended

## Basic Installation

### Core Framework

```bash
pip install empathy-framework
```

This installs the core Empathy Framework with basic functionality.

## Installation Options

### With LLM Support

```bash
pip install empathy-framework[llm]
```

Includes:
- Anthropic Claude SDK
- OpenAI SDK

### With Healthcare Support

```bash
pip install empathy-framework[healthcare]
```

Includes:
- FHIR client (Epic, Cerner integration)
- HL7 parsing
- HIPAA audit logging

### With Webhooks

```bash
pip install empathy-framework[webhooks]
```

Includes:
- aiohttp (async HTTP)
- requests (sync HTTP)

### Full Installation (Recommended)

```bash
pip install empathy-framework[full]
```

Includes everything: LLM providers, healthcare, webhooks.

### Development Installation

```bash
# Clone repository
git clone https://github.com/Smart-AI-Memory/empathy-framework.git
cd empathy-framework

# Install in editable mode with dev dependencies
pip install -e .[dev]
```

## Verification

Verify installation:

```bash
python -c "import empathy_os; print(empathy_os.__version__)"
# Output: 1.8.0
```

Or use the CLI:

```bash
empathy-framework version
# Output: Empathy v1.8.0
```

## Next Steps

- [Quick Start Guide](quickstart.md) - Build your first chatbot in 5 minutes
- [Configuration](configuration.md) - Learn about configuration options
```

---

## Writing Documentation Best Practices

### Use Admonitions (Call-out Boxes)

```markdown
!!! note
    This is a note

!!! warning
    This is a warning

!!! tip
    This is a helpful tip

!!! danger
    This is dangerous - be careful!
```

**Renders as beautiful colored boxes!**

### Code Blocks with Syntax Highlighting

````markdown
```python
from empathy_os import EmpathyOS

empathy = EmpathyOS(user_id="user_123")
```
````

### Tabs for Multiple Options

```markdown
=== "Python"

    ```python
    print("Hello World")
    ```

=== "JavaScript"

    ```javascript
    console.log("Hello World")
    ```
```

### Tables

```markdown
| Feature | Description | Status |
|---------|-------------|--------|
| Level 4 | Anticipatory | ✅ Ready |
| HIPAA   | Compliance  | ✅ Ready |
```

---

## Auto-Generate API Documentation

### Using mkdocstrings

**File**: `docs/api-reference/empathy-os.md`

```markdown
# EmpathyOS API Reference

## Overview

The `EmpathyOS` class is the main entry point for the Empathy Framework.

## Class Documentation

::: empathy_os.core.EmpathyOS
    options:
      show_source: true
      heading_level: 3
```

**What this does**:
- Automatically extracts docstrings from `empathy_os.core.EmpathyOS`
- Formats them as beautiful documentation
- Includes method signatures, parameters, return types

**Your Python code should have Google-style docstrings**:

```python
class EmpathyOS:
    """
    Main Empathy Framework class for Level 1-5 AI collaboration.

    Args:
        user_id: Unique identifier for the user
        target_level: Target empathy level (1-5)
        confidence_threshold: Minimum confidence for Level 4 predictions

    Example:
        ```python
        empathy = EmpathyOS(
            user_id="user_123",
            target_level=4,
            confidence_threshold=0.75
        )
        ```
    """

    def interact(self, user_id: str, user_input: str, context: dict) -> Response:
        """
        Process user input and generate empathetic response.

        Args:
            user_id: User identifier
            user_input: User's query or statement
            context: Additional context for the interaction

        Returns:
            Response object containing the empathetic response

        Example:
            ```python
            response = empathy.interact(
                user_id="user_123",
                user_input="Help me debug this",
                context={"code": "..."}
            )
            print(response.response)
            ```
        """
        pass
```

---

## Building the Site

### Development (Live Preview)

```bash
mkdocs serve
```

- Starts server at http://127.0.0.1:8000
- Auto-reloads on file changes
- Use this while writing docs

### Production Build

```bash
mkdocs build
```

**Creates**:
```
site/
├── index.html
├── getting-started/
│   └── installation/
│       └── index.html
└── ... (all your docs as HTML)
```

This `site/` directory is a complete static website - upload anywhere!

---

## Deploying to Read the Docs

### Step 1: Create `.readthedocs.yaml`

At project root:

```yaml
# .readthedocs.yaml
version: 2

build:
  os: ubuntu-22.04
  tools:
    python: "3.12"

mkdocs:
  configuration: mkdocs.yml

python:
  install:
    - requirements: docs/requirements.txt
```

### Step 2: Create `docs/requirements.txt`

```
mkdocs>=1.5.0
mkdocs-material>=9.0.0
mkdocstrings[python]>=0.24.0
```

### Step 3: Connect GitHub to Read the Docs

1. Go to https://readthedocs.org
2. Sign in with GitHub
3. Click "Import a Project"
4. Select `Smart-AI-Memory/empathy-framework`
5. Click "Build"

**Done!** Your docs will auto-deploy on every commit to `main`.

**Your URL**: https://empathy-framework.readthedocs.io

---

## Advanced Features

### Search

Automatically included! Just start typing in the search box.

### Versioning

Support multiple versions (v1.7.0, v1.8.0, latest):

```bash
pip install mike

# Setup versioning
mike deploy 1.8.0 latest --update-aliases
mike set-default latest

# Deploy
mike deploy --push
```

### Custom Domain

In Read the Docs settings:
- Add custom domain: `docs.empathy-framework.com`
- Update DNS CNAME record

---

## Workflow for Empathy Framework Docs

### Your Daily Workflow

1. **Edit docs** in `docs/` directory (just Markdown!)

```bash
# Edit a file
code docs/getting-started/quickstart.md
```

2. **Preview locally**

```bash
mkdocs serve
# Open http://127.0.0.1:8000
```

3. **Commit and push**

```bash
git add docs/
git commit -m "docs: Update quickstart guide"
git push
```

4. **Auto-deploy** to Read the Docs (no action needed!)

### Creating New Pages

```bash
# Create new guide
touch docs/guides/my-new-guide.md

# Add content
echo "# My New Guide\n\nContent here..." > docs/guides/my-new-guide.md

# Add to navigation in mkdocs.yml
```

In `mkdocs.yml`:
```yaml
nav:
  - Guides:
      - My New Guide: guides/my-new-guide.md
```

---

## Tips & Tricks

### Tip 1: Use Relative Links

```markdown
See the [installation guide](../getting-started/installation.md).
```

### Tip 2: Include Code from Files

````markdown
```python title="example.py"
--8<-- "examples/simple_chatbot.py"
```
````

### Tip 3: Keyboard Shortcuts

```markdown
++ctrl+c++ to copy
```

Renders as: <kbd>Ctrl</kbd>+<kbd>C</kbd>

### Tip 4: Emojis

```markdown
:rocket: :brain: :heart:
```

Renders as: 🚀 🧠 ❤️

---

## Common Issues & Solutions

### Issue: "Address already in use"

**Problem**: Port 8000 is already in use

**Solution**: Use different port
```bash
mkdocs serve -a 127.0.0.1:8001
```

### Issue: "Module not found"

**Problem**: mkdocstrings can't find Python module

**Solution**: Install package in development mode
```bash
pip install -e .
```

### Issue: Search not working

**Problem**: Need to rebuild search index

**Solution**: Clear cache and rebuild
```bash
rm -rf site/
mkdocs build
```

---

## Resources

### Official Documentation
- **MkDocs**: https://www.mkdocs.org
- **Material Theme**: https://squidfunk.github.io/mkdocs-material/
- **mkdocstrings**: https://mkdocstrings.github.io

### Examples to Learn From
- **FastAPI**: https://github.com/tiangolo/fastapi/tree/master/docs
- **Pydantic**: https://github.com/pydantic/pydantic/tree/main/docs

### Cheat Sheets
- **Markdown**: https://www.markdownguide.org/cheat-sheet/
- **Material Icons**: https://squidfunk.github.io/mkdocs-material/reference/icons-emojis/

---

## Next Steps for You

### Week 1-2 Tasks

1. **Setup MkDocs** (30 minutes)
   - [ ] Install: `pip install mkdocs-material mkdocstrings[python]`
   - [ ] Create `mkdocs.yml` (use template above)
   - [ ] Run `mkdocs serve` and verify it works

2. **Create Directory Structure** (15 minutes)
   - [ ] Create `docs/` subdirectories
   - [ ] Move existing examples to `docs/examples/`

3. **Write Homepage** (1 hour)
   - [ ] Create `docs/index.md` (use template above)
   - [ ] Add badges, quick start, features

4. **Getting Started Section** (4 hours)
   - [ ] `installation.md`
   - [ ] `quickstart.md` (5-minute working example)
   - [ ] `configuration.md` (all config options)
   - [ ] `first-application.md` (detailed tutorial)

5. **Connect to Read the Docs** (30 minutes)
   - [ ] Create `.readthedocs.yaml`
   - [ ] Create `docs/requirements.txt`
   - [ ] Import project on Read the Docs
   - [ ] Verify build succeeds

**Total: ~7 hours for professional documentation website!**

---

## Questions?

**Common Questions**:

**Q: Do I need to know HTML/CSS?**
A: No! Just write Markdown. MkDocs handles everything.

**Q: Can I preview before deploying?**
A: Yes! `mkdocs serve` shows exactly what will be deployed.

**Q: What if I make a mistake?**
A: Just edit the Markdown file and save. Auto-reloads instantly.

**Q: How do I add images?**
A: Put images in `docs/assets/`, reference as `![Alt text](assets/image.png)`

**Q: Can I customize the theme?**
A: Yes! Material theme has 50+ customization options in `mkdocs.yml`.

---

## Ready to Start!

You now know everything you need to create professional documentation for Empathy Framework!

**Your first command**:
```bash
pip install mkdocs-material mkdocstrings[python]
mkdocs serve
```

Open http://127.0.0.1:8000 and start editing! 🚀
