# Contributing to Coach

Thank you for your interest in contributing to Coach! This guide will help you get started.

**Built on LangChain** - Contributions to wizards leverage the full LangChain ecosystem.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Contribution Types](#contribution-types)
- [Development Workflow](#development-workflow)
- [Style Guide](#style-guide)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Our Standards

**Positive behavior**:
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior**:
- Harassment, trolling, or insulting/derogatory comments
- Publishing others' private information without permission
- Any conduct which could reasonably be considered inappropriate

### Enforcement

Violations can be reported to patrick.roebuck@deepstudyai.com. All complaints will be reviewed and investigated promptly and fairly.

---

## Getting Started

### Prerequisites

- **Python 3.12+** - Required for Coach development
- **Git** - For version control
- **Node.js 18+** - For VS Code extension development
- **Java 17+** - For JetBrains plugin development
- **LangChain knowledge** - Understanding of LangChain basics helpful

### Find an Issue

Good starting points:
- [`good-first-issue`](https://github.com/Deep-Study-AI/coach/labels/good-first-issue) - Easy issues for newcomers
- [`help-wanted`](https://github.com/Deep-Study-AI/coach/labels/help-wanted) - Issues where we need help
- [`documentation`](https://github.com/Deep-Study-AI/coach/labels/documentation) - Improve docs
- [`bug`](https://github.com/Deep-Study-AI/coach/labels/bug) - Fix bugs

Don't see an issue? **Create one!** Describe:
- What you want to work on
- Why it's valuable
- Your proposed approach

---

## Development Setup

### 1. Fork and Clone

```bash
# Fork on GitHub (click "Fork" button)

# Clone your fork
git clone https://github.com/YOUR_USERNAME/coach-alpha.git
cd coach-alpha

# Add upstream remote
git remote add upstream https://github.com/Deep-Study-AI/coach.git
```

### 2. Set Up Python Environment

```bash
# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install in editable mode
pip install -e .
```

### 3. Set Up Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run once to check setup
pre-commit run --all-files
```

### 4. Set Up VS Code Extension (Optional)

```bash
cd vscode-extension
npm install
npm run compile
```

### 5. Set Up JetBrains Plugin (Optional)

```bash
cd jetbrains-plugin
./gradlew build
```

### 6. Run Tests

```bash
# Python tests
pytest

# With coverage
pytest --cov=coach --cov-report=html

# VS Code tests
cd vscode-extension
npm test

# JetBrains tests
cd jetbrains-plugin
./gradlew test
```

---

## How to Contribute

### Reporting Bugs

**Before reporting**:
1. Search [existing issues](https://github.com/Deep-Study-AI/coach/issues)
2. Check [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)
3. Try latest version

**When reporting**, include:
- **Title**: Clear, descriptive summary
- **Description**: What happened vs. what you expected
- **Steps to reproduce**: Minimal example
- **Environment**:
  ```
  - OS: macOS 14.0
  - Python: 3.12.0
  - Coach: 0.1.0
  - IDE: VS Code 1.85.0
  ```
- **Logs**: Relevant error messages
- **Screenshots**: If applicable

**Use bug template**: [Create bug report](https://github.com/Deep-Study-AI/coach/issues/new?template=bug_report.md)

### Suggesting Features

**Before suggesting**:
1. Check [existing feature requests](https://github.com/Deep-Study-AI/coach/labels/enhancement)
2. Discuss in [Discord #feature-requests](https://discord.gg/coach-alpha)

**When suggesting**, include:
- **Use case**: What problem does this solve?
- **Proposed solution**: How should it work?
- **Alternatives**: Other approaches you considered
- **Examples**: Mock-ups, code examples

**Use feature template**: [Create feature request](https://github.com/Deep-Study-AI/coach/issues/new?template=feature_request.md)

### Improving Documentation

Documentation contributions are **highly valued**!

**Types**:
- Fix typos or unclear wording
- Add examples
- Improve existing guides
- Translate to other languages
- Create video tutorials

**Process**:
1. Edit files in `docs/`
2. Test examples work
3. Submit pull request

**No issue needed** for small doc fixes (typos, clarity). For larger changes (new guides), create an issue first.

---

## Contribution Types

### 1. Code Contributions

#### New Wizards

**Most requested contribution type!**

```bash
# Create new wizard
cp coach/wizards/template_wizard.py coach/wizards/my_wizard.py

# Edit my_wizard.py
# - Change class name
# - Implement analyze() method
# - Add LangChain tools
# - Add tests

# Register wizard
# Edit coach/wizards/__init__.py
from coach.wizards.my_wizard import MyWizard

def get_all_wizards():
    return [
        # ... existing wizards ...
        MyWizard(),
    ]
```

**See**: [CUSTOM_WIZARDS.md](docs/CUSTOM_WIZARDS.md) for complete tutorial

#### Bug Fixes

1. Write failing test first (TDD)
2. Fix bug
3. Ensure test passes
4. Add regression test if needed

#### Performance Improvements

1. Create benchmark showing current performance
2. Implement optimization
3. Show performance improvement
4. Ensure no regressions

#### VS Code Extension Features

**Example**: Add new command

```typescript
// vscode-extension/src/extension.ts

vscode.commands.registerCommand('coach.myNewCommand', async () => {
  // Your implementation
});
```

#### JetBrains Plugin Features

**Example**: Add new action

```kotlin
// jetbrains-plugin/src/main/kotlin/actions/MyAction.kt

class MyAction : AnAction() {
    override fun actionPerformed(e: AnActionEvent) {
        // Your implementation
    }
}
```

### 2. Testing Contributions

**Always welcome!**

```bash
# Add tests to existing modules
tests/test_wizards/test_security_wizard.py
tests/test_lsp/test_server.py

# Run specific test
pytest tests/test_wizards/test_security_wizard.py::test_sql_injection

# Add integration tests
tests/integration/test_end_to_end.py
```

### 3. Documentation Contributions

**Locations**:
- `docs/` - User-facing documentation
- `README.md` - Project overview
- Docstrings - Code documentation
- `examples/` - Example code

**Standards**:
- Use Markdown
- Include code examples
- Test all code examples
- Add to table of contents

### 4. Examples and Tutorials

```bash
# Add to examples/
examples/
├── custom_wizards/
│   └── my_wizard_example.py
├── lsp_integration/
│   └── custom_client.py
└── workflows/
    └── ci_cd_integration.sh
```

### 5. Translations

**Translations needed** for:
- README.md
- docs/INSTALLATION.md
- docs/USER_MANUAL.md

**Languages** (priority):
1. Spanish (es)
2. Chinese Simplified (zh-CN)
3. French (fr)
4. German (de)
5. Japanese (ja)

**Process**:
1. Create issue: "Translation: [Language]"
2. Create `docs/[lang]/` directory
3. Translate files
4. Update README with language links

---

## Development Workflow

### 1. Create Branch

```bash
# Update main
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/my-awesome-feature

# Or for bug fix
git checkout -b fix/issue-123-description
```

**Branch naming**:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Adding tests
- `chore/` - Maintenance tasks

### 2. Make Changes

```bash
# Make your changes
vim coach/wizards/my_wizard.py

# Add tests
vim tests/test_my_wizard.py

# Test your changes
pytest tests/test_my_wizard.py

# Run all tests
pytest

# Run linters
pre-commit run --all-files
```

### 3. Commit Changes

```bash
# Stage changes
git add coach/wizards/my_wizard.py tests/test_my_wizard.py

# Commit with good message (see style guide below)
git commit -m "feat: add CostOptimizationWizard

- Implements AWS cost analysis
- Detects over-provisioned instances
- Suggests reserved instance savings
- Includes 15 test cases

Closes #123"
```

**Commit message format**:
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples**:
```
feat(wizards): add CostOptimizationWizard

fix(lsp): handle timeout errors gracefully

docs(readme): add installation video link

test(security): add XSS detection tests
```

### 4. Push Changes

```bash
# Push to your fork
git push origin feature/my-awesome-feature
```

### 5. Create Pull Request

1. Go to https://github.com/Deep-Study-AI/coach
2. Click "New Pull Request"
3. Select your branch
4. Fill out PR template (see below)
5. Link related issue: "Closes #123"

---

## Style Guide

### Python Code Style

**PEP 8** with these specifics:

```python
# Line length: 100 characters (not 80)
# Imports: grouped and sorted
import os
import sys

from typing import List, Optional

from langchain.agents import Agent
from langchain.chains import LLMChain

from coach.base_wizard import BaseWizard


# Classes: PascalCase
class SecurityWizard(BaseWizard):
    """Detects security vulnerabilities.

    This wizard analyzes code for OWASP Top 10 vulnerabilities
    including SQL injection, XSS, and authentication issues.

    Attributes:
        name: Wizard identifier
        expertise: Short description

    Example:
        >>> wizard = SecurityWizard()
        >>> result = wizard.analyze(code)
        >>> print(result.diagnosis)
    """

    # Methods: snake_case
    def analyze(self, code: str, context: str = "") -> WizardResult:
        """Analyze code for security issues.

        Args:
            code: Source code to analyze
            context: Additional context (optional)

        Returns:
            WizardResult with diagnosis and recommendations

        Raises:
            ValueError: If code is empty
        """
        if not code:
            raise ValueError("Code cannot be empty")

        # Implementation
        ...


# Type hints: always use
def process_result(result: WizardResult) -> List[str]:
    return result.recommendations


# Docstrings: Google style
def complex_function(param1: str, param2: int) -> bool:
    """Short one-line description.

    Longer description that explains what this function does,
    why it exists, and any important details.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative
    """
    pass
```

**Tools**:
```bash
# Format code
black coach/

# Sort imports
isort coach/

# Lint
flake8 coach/
pylint coach/

# Type check
mypy coach/

# All at once (via pre-commit)
pre-commit run --all-files
```

### TypeScript Code Style

**For VS Code extension**:

```typescript
// Interfaces: PascalCase
interface WizardResult {
  wizard: string;
  diagnosis: string;
  recommendations: string[];
}

// Functions: camelCase
async function analyzeFile(uri: vscode.Uri): Promise<WizardResult> {
  const document = await vscode.workspace.openTextDocument(uri);
  const code = document.getText();

  // Use const/let, not var
  const result = await client.sendRequest('coach/runWizard', [
    'SecurityWizard',
    { code }
  ]);

  return result;
}

// Classes: PascalCase
class CoachCodeActionProvider implements vscode.CodeActionProvider {
  async provideCodeActions(
    document: vscode.TextDocument,
    range: vscode.Range
  ): Promise<vscode.CodeAction[]> {
    // Implementation
  }
}

// Constants: UPPER_SNAKE_CASE
const MAX_RETRIES = 3;
const DEFAULT_TIMEOUT_MS = 5000;
```

**Tools**:
```bash
cd vscode-extension
npm run lint
npm run format
```

### Kotlin Code Style

**For JetBrains plugin**:

```kotlin
// Classes: PascalCase
class CoachLSPClient(private val project: Project) : Disposable {
    // Properties: camelCase
    private val logger = Logger.getInstance(CoachLSPClient::class.java)
    private var languageServer: LanguageServer? = null

    // Functions: camelCase
    suspend fun runWizard(
        wizardName: String,
        task: String,
        context: String = ""
    ): WizardResult = withContext(Dispatchers.IO) {
        ensureConnected()

        val params = listOf(wizardName, mapOf("task" to task, "context" to context))
        val result = languageServer!!
            .workspaceService
            .executeCommand(ExecuteCommandParams("coach/runWizard", params))
            .get(30, TimeUnit.SECONDS)

        return@withContext Json.decodeFromString<WizardResult>(result.toString())
    }

    // Companion objects
    companion object {
        fun getInstance(project: Project): CoachLSPClient = project.service()

        const val COACH_RUN_WIZARD = "coach/runWizard"
    }
}
```

---

## Testing

### Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_wizards/
│   │   ├── test_security_wizard.py
│   │   ├── test_performance_wizard.py
│   │   └── ...
│   └── test_lsp/
│       └── test_server.py
├── integration/           # Integration tests
│   ├── test_end_to_end.py
│   └── test_multi_wizard.py
└── fixtures/             # Test data
    ├── sample_code/
    └── expected_results/
```

### Writing Tests

```python
# tests/unit/test_wizards/test_security_wizard.py

import pytest
from coach.wizards.security import SecurityWizard
from langchain.chat_models import ChatOpenAI


@pytest.fixture
def wizard():
    """Create SecurityWizard instance for testing"""
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    return SecurityWizard(llm=llm)


class TestSecurityWizard:
    """Test suite for SecurityWizard"""

    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly"""
        assert wizard.name == "SecurityWizard"
        assert wizard.expertise == "Security vulnerabilities, OWASP Top 10"

    def test_detect_sql_injection(self, wizard):
        """Test detection of SQL injection vulnerability"""
        code = '''
        user_id = input()
        query = f"SELECT * FROM users WHERE id={user_id}"
        cursor.execute(query)
        '''

        result = wizard.analyze(code)

        assert "sql injection" in result.diagnosis.lower()
        assert result.confidence > 0.8
        assert len(result.recommendations) > 0

    def test_detect_xss(self, wizard):
        """Test detection of XSS vulnerability"""
        code = '''
        element.innerHTML = user_comment
        '''

        result = wizard.analyze(code)

        assert "xss" in result.diagnosis.lower() or "cross-site scripting" in result.diagnosis.lower()

    @pytest.mark.parametrize("code,expected_issue", [
        ('password = "admin123"', "hardcoded"),
        ('api_key = "sk-1234567890"', "hardcoded"),
        ('secret = "my_secret"', "hardcoded"),
    ])
    def test_detect_hardcoded_secrets(self, wizard, code, expected_issue):
        """Test detection of various hardcoded secrets"""
        result = wizard.analyze(code)
        assert expected_issue in result.diagnosis.lower()

    def test_empty_code_raises_error(self, wizard):
        """Test that empty code raises appropriate error"""
        with pytest.raises(ValueError, match="Code cannot be empty"):
            wizard.analyze("")

    def test_confidence_score_range(self, wizard):
        """Test confidence score is in valid range"""
        code = 'user_id = input()\nquery = f"SELECT * FROM users WHERE id={user_id}"'
        result = wizard.analyze(code)

        assert 0.0 <= result.confidence <= 1.0

    @pytest.mark.integration
    def test_with_real_llm(self, wizard):
        """Integration test with real LLM (requires API key)"""
        code = '''
        def login(username, password):
            query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
            cursor.execute(query)
            return cursor.fetchone()
        '''

        result = wizard.analyze(code, context="Authentication function")

        assert result.confidence > 0.7
        assert len(result.recommendations) >= 2
        assert any("parameterized" in r.lower() for r in result.recommendations)
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_wizards/test_security_wizard.py

# Run specific test
pytest tests/unit/test_wizards/test_security_wizard.py::TestSecurityWizard::test_detect_sql_injection

# Run with coverage
pytest --cov=coach --cov-report=html

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/

# Skip slow tests
pytest -m "not slow"

# Run in parallel (faster)
pytest -n auto
```

### Test Coverage

**Minimum required**: 80% coverage for new code

```bash
# Check coverage
pytest --cov=coach --cov-report=term-missing

# Generate HTML report
pytest --cov=coach --cov-report=html
open htmlcov/index.html  # View in browser
```

---

## Documentation

### Docstring Standard

Use **Google style** docstrings:

```python
def analyze(self, code: str, context: str = "", max_retries: int = 3) -> WizardResult:
    """Analyze code for issues.

    This method performs static analysis on the provided code using
    LangChain-powered AI models to detect potential problems.

    Args:
        code: Source code to analyze. Must be valid syntax.
        context: Additional context about the code (e.g., "payment processing").
            Optional. Providing context improves analysis quality.
        max_retries: Maximum number of retry attempts for LLM calls.
            Default is 3. Must be >= 0.

    Returns:
        WizardResult object containing:
        - diagnosis: Main analysis text
        - recommendations: List of actionable suggestions
        - confidence: Float between 0.0 and 1.0

    Raises:
        ValueError: If code is empty or invalid
        TimeoutError: If analysis exceeds timeout
        LLMError: If LLM API call fails after max_retries

    Example:
        >>> wizard = SecurityWizard()
        >>> result = wizard.analyze("x = input(); eval(x)")
        >>> print(result.diagnosis)
        'Dangerous use of eval() with user input...'
        >>> print(result.confidence)
        0.95

    Note:
        Analysis time depends on code length and LLM response time.
        Typical range: 1-5 seconds.

    See Also:
        quick_analyze(): Faster pattern-based analysis
        predict(): Get Level 4 predictions
    """
    pass
```

### README Updates

When adding major features, update README.md:

```markdown
## Features

- ✅ 16 specialized AI wizards
- ✅ Level 4 Anticipatory Empathy (predicts issues 30-90 days ahead)
- ✅ VS Code extension
- ✅ JetBrains plugin
- ✨ **NEW: CostOptimizationWizard** - AWS cost analysis
```

### Changelog

Add entry to CHANGELOG.md (see next section for format).

---

## Pull Request Process

### 1. Before Creating PR

**Checklist**:
- [ ] Code follows style guide
- [ ] Tests pass (`pytest`)
- [ ] Coverage is ≥80% for new code
- [ ] Docstrings are complete
- [ ] CHANGELOG.md is updated
- [ ] README.md is updated (if needed)
- [ ] Pre-commit hooks pass

### 2. Create Pull Request

**Title format**:
```
<type>: <short description>

Examples:
feat: add CostOptimizationWizard for AWS cost analysis
fix: handle timeout errors in LSP server
docs: add LangChain custom wizard tutorial
```

**Description** (use template):
```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change needed? What problem does it solve?
Closes #123

## Type of Change
- [ ] Bug fix
- [x] New feature
- [ ] Breaking change
- [ ] Documentation update

## How Has This Been Tested?
- [ ] Unit tests added
- [x] Integration tests added
- [x] Tested manually in VS Code
- [ ] Tested manually in IntelliJ IDEA

## Screenshots (if applicable)
[Screenshot showing feature in action]

## Checklist
- [x] My code follows the style guide
- [x] I have added tests that prove my fix/feature works
- [x] All new and existing tests pass
- [x] I have updated the documentation
- [x] I have added an entry to CHANGELOG.md
```

### 3. Code Review

**What reviewers look for**:
- Code quality and style
- Test coverage
- Documentation completeness
- Performance implications
- Security considerations
- Backward compatibility

**Respond to feedback**:
- Address all comments
- Explain your reasoning if you disagree
- Mark conversations as resolved when addressed

### 4. Merge

**Requirements before merge**:
- ✅ All CI checks pass
- ✅ At least one approving review
- ✅ No unresolved conversations
- ✅ Branch is up-to-date with main

**Merge method**: Squash and merge (keeps history clean)

---

## Community

### Discord

Join our community: https://discord.gg/coach-alpha

**Channels**:
- `#contributing` - Contribution discussions
- `#dev-chat` - General development chat
- `#code-review` - Code review requests
- `#show-and-tell` - Show off your work!

### GitHub Discussions

For longer-form discussions: https://github.com/Deep-Study-AI/coach/discussions

**Categories**:
- **Ideas** - Feature proposals and brainstorming
- **Q&A** - Ask technical questions
- **Show and tell** - Share your projects
- **General** - Everything else

### Office Hours

**When**: Every Friday 2-3pm PT
**Where**: Discord voice channel
**What**: Ask questions, discuss contributions, get help

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- Monthly contributor spotlight (Discord)

**Top contributors** receive:
- Coach swag (t-shirts, stickers)
- Early access to new features
- Invitation to contributor-only events

---

## License

By contributing to Coach, you agree that your contributions will be licensed under the **Apache License 2.0**.

See [LICENSE](LICENSE) for full terms.

---

## Questions?

- **Discord**: https://discord.gg/coach-alpha (#contributing channel)
- **Email**: patrick.roebuck@deepstudyai.com
- **GitHub Discussions**: https://github.com/Deep-Study-AI/coach/discussions

**Thank you for contributing to Coach!** 🎉

---

**Built with** ❤️ **using LangChain**
