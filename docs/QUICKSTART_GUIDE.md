# Empathy Framework Quick Start Guide

**Get from zero to production in 5 minutes**

Welcome to the Empathy Framework! This guide will get you up and running with Level 4 Anticipatory AI collaboration in minutes.

---

## What You'll Build

By the end of this 5-minute guide, you'll have:

1. A working Empathy Framework installation
2. Your first AI interaction using Level 4 Anticipatory Empathy
3. A security wizard analyzing your code
4. Understanding of how to progress through empathy levels

**Time Investment:** 5 minutes
**Prerequisites:** Python 3.10+, API key for Anthropic or OpenAI

---

## Step 1: Installation (30 seconds)

### Option A: Install via pip (Recommended)

```bash
pip install empathy-framework anthropic
```

### Option B: Install from source

```bash
git clone https://github.com/Deep-Study-AI/Empathy.git
cd Empathy
pip install -r requirements.txt
```

**Verify Installation:**

```bash
python -c "from empathy_llm_toolkit import EmpathyLLM; print('Success!')"
```

---

## Step 2: Set Up API Key (30 seconds)

Choose your preferred LLM provider and set the API key:

### For Anthropic (Claude) - Recommended

```bash
export ANTHROPIC_API_KEY=sk-ant-your-key-here
```

### For OpenAI (GPT-4)

```bash
export OPENAI_API_KEY=sk-your-key-here
```

**Make it permanent** (add to `~/.bashrc` or `~/.zshrc`):

```bash
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

---

## Step 3: Your First Interaction (1 minute)

Create a file called `hello_empathy.py`:

```python
import asyncio
import os
from empathy_llm_toolkit import EmpathyLLM

async def main():
    # Initialize with Claude (Level 1: Reactive)
    llm = EmpathyLLM(
        provider="anthropic",
        target_level=4,  # Allow progression to Level 4
        api_key=os.getenv("ANTHROPIC_API_KEY")
    )

    # First interaction (Level 1: Simple Q&A)
    result = await llm.interact(
        user_id="alice",
        user_input="Help me write a secure login function in Python"
    )

    print(f"Level {result['level_used']}: {result['level_description']}")
    print(f"Response: {result['content']}\n")

    # Build trust with positive feedback
    llm.update_trust("alice", outcome="success")

    # Second interaction (may progress to Level 2: Guided)
    result = await llm.interact(
        user_id="alice",
        user_input="Now I need to hash the passwords"
    )

    print(f"Level {result['level_used']}: {result['level_description']}")
    print(f"Response: {result['content']}")

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**

```bash
python hello_empathy.py
```

**Expected Output:**

```
Level 1: Reactive - Simple question-answer, no context
Response: Here's a secure login function in Python...

Level 2: Guided - Contextual collaboration with clarifying questions
Response: Based on your login function, here's how to hash passwords securely...
```

Notice how the framework automatically progressed from Level 1 to Level 2 based on trust!

---

## Step 4: Use a Coach Wizard (2 minutes)

Now let's use a security wizard to analyze code. Create `analyze_code.py`:

```python
import asyncio
from coach_wizards import SecurityWizard

# Sample code with a security vulnerability
code_to_analyze = """
def login(username, password):
    # SQL Injection vulnerability!
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    result = db.execute(query)
    return result

def get_user_data(user_id):
    # Another vulnerability
    return db.execute(f"SELECT * FROM users WHERE id={user_id}")
"""

def main():
    # Initialize security wizard
    wizard = SecurityWizard()

    # Run full analysis (current issues + Level 4 predictions)
    result = wizard.run_full_analysis(
        code=code_to_analyze,
        file_path="auth.py",
        language="python",
        project_context={
            "team_size": 10,
            "deployment_frequency": "daily",
            "user_count": 5000,
            "code_change_rate": "high"
        }
    )

    # Display results
    print(f"=== {result.wizard_name} Analysis ===\n")
    print(f"Summary: {result.summary}\n")

    print(f"Current Issues Found: {len(result.issues)}")
    for issue in result.issues:
        print(f"  [{issue.severity.upper()}] Line {issue.line_number}: {issue.message}")
        print(f"    Category: {issue.category}")
        print(f"    Confidence: {issue.confidence:.0%}")
        if issue.fix_suggestion:
            print(f"    Fix: {issue.fix_suggestion}\n")

    print(f"\nLevel 4 Anticipatory Predictions: {len(result.predictions)}")
    for pred in result.predictions:
        print(f"  [{pred.impact.upper()}] {pred.issue_type}")
        print(f"    Predicted Date: {pred.predicted_date.strftime('%Y-%m-%d')}")
        print(f"    Probability: {pred.probability:.0%}")
        print(f"    Reasoning: {pred.reasoning}")
        print(f"    Prevention Steps:")
        for step in pred.prevention_steps:
            print(f"      - {step}")
        print()

    print(f"Recommendations:")
    for rec in result.recommendations:
        print(f"  - {rec}")

if __name__ == "__main__":
    main()
```

**Run it:**

```bash
python analyze_code.py
```

**Expected Output:**

```
=== SecurityWizard Analysis ===

Summary: SecurityWizard Analysis: 2 errors, 0 warnings found. 3 future issues predicted (Level 4 Anticipatory).

Current Issues Found: 2
  [ERROR] Line 3: SQL Injection vulnerability in user authentication
    Category: SQL Injection
    Confidence: 95%
    Fix: Use parameterized queries: cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))

  [ERROR] Line 8: SQL Injection in user data retrieval
    Category: SQL Injection
    Confidence: 90%
    Fix: Use parameterized queries: cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))

Level 4 Anticipatory Predictions: 3
  [HIGH] Credential Stuffing Attack
    Predicted Date: 2025-12-15
    Probability: 78%
    Reasoning: High user count (5000) + SQL injection vulnerability creates attractive attack target
    Prevention Steps:
      - Implement rate limiting on login endpoint
      - Add multi-factor authentication
      - Deploy Web Application Firewall
      - Set up anomaly detection monitoring

  [CRITICAL] Database Breach
    Predicted Date: 2026-01-20
    Probability: 65%
    Reasoning: Multiple SQL injection points + high code change rate increases risk
    Prevention Steps:
      - Fix all SQL injection vulnerabilities immediately
      - Implement prepared statements across codebase
      - Add input validation layer
      - Schedule security code review

  [MEDIUM] Authentication Bypass
    Predicted Date: 2025-11-30
    Probability: 55%
    Reasoning: Weak authentication logic may be exploitable
    Prevention Steps:
      - Implement bcrypt for password hashing
      - Add session management
      - Enforce password complexity requirements

Recommendations:
  - Fix 2 critical issues immediately
  - Prevent 3 predicted issues with high probability
```

Notice the **Level 4 Anticipatory predictions**! The framework doesn't just find current bugs - it predicts future problems based on your code trajectory.

---

## Step 5: Configuration (1 minute)

Create a configuration file for persistent settings:

```bash
# Generate default config
cat > empathy.config.yml << EOF
# Empathy Framework Configuration
user_id: "your_name"
target_level: 4
confidence_threshold: 0.75

# Persistence
persistence_enabled: true
persistence_backend: sqlite
persistence_path: ./empathy_data

# Metrics
metrics_enabled: true
metrics_path: ./metrics.db

# Pattern Library
pattern_library_enabled: true
pattern_sharing: true

# Logging
log_level: INFO
structured_logging: true
EOF
```

**Use the config in your code:**

```python
from empathy_os.config import load_config
from empathy_llm_toolkit import EmpathyLLM

# Load config from file (with env var override)
config = load_config("empathy.config.yml", use_env=True)

# Initialize with config
llm = EmpathyLLM(
    provider="anthropic",
    target_level=config.target_level,
    api_key=os.getenv("ANTHROPIC_API_KEY")
)
```

---

## Understanding the 5 Levels

As you use the framework, it automatically progresses through levels based on trust:

| Level | Name | What It Does | When It Activates |
|-------|------|--------------|-------------------|
| **1** | **Reactive** | Simple Q&A, no context | Always starts here |
| **2** | **Guided** | Asks clarifying questions, uses history | After 3+ successful interactions |
| **3** | **Proactive** | Detects patterns, acts proactively | After 10+ interactions, trust > 0.7 |
| **4** | **Anticipatory** | Predicts future needs, prevents problems | After 20+ interactions, trust > 0.8 |
| **5** | **Systems** | Cross-domain learning, structural design | After 50+ interactions, trust > 0.9 |

**Build trust by:**
- Providing positive feedback: `llm.update_trust(user_id, outcome="success")`
- Consistent interaction patterns
- Using context effectively

**Trust decreases when:**
- Negative feedback: `llm.update_trust(user_id, outcome="failure")`
- No interaction for extended periods
- Inconsistent usage patterns

---

## Common Patterns

### Pattern 1: Code Review Workflow

```python
from coach_wizards import SecurityWizard, PerformanceWizard, TestingWizard

# Initialize wizards
security = SecurityWizard()
performance = PerformanceWizard()
testing = TestingWizard()

# Run all analyses
code = open("my_code.py").read()
context = {"team_size": 5, "deployment_frequency": "daily"}

security_result = security.run_full_analysis(code, "my_code.py", "python", context)
performance_result = performance.run_full_analysis(code, "my_code.py", "python", context)
testing_result = testing.run_full_analysis(code, "my_code.py", "python", context)

# Aggregate results
all_issues = security_result.issues + performance_result.issues + testing_result.issues
all_predictions = security_result.predictions + performance_result.predictions

print(f"Total issues: {len(all_issues)}")
print(f"Total predictions: {len(all_predictions)}")
```

### Pattern 2: Conversational Code Improvement

```python
import asyncio
from empathy_llm_toolkit import EmpathyLLM

async def improve_code_interactively():
    llm = EmpathyLLM(provider="anthropic", target_level=4)

    # Start conversation
    code = "..."  # Your code
    result = await llm.interact(
        user_id="developer",
        user_input=f"Review this code for security issues: {code}",
    )

    print(result['content'])

    # Follow-up question
    result = await llm.interact(
        user_id="developer",
        user_input="Show me how to fix the SQL injection",
    )

    print(result['content'])

    # Framework remembers context!
    result = await llm.interact(
        user_id="developer",
        user_input="What else should I improve?",
    )

    print(result['content'])

asyncio.run(improve_code_interactively())
```

### Pattern 3: CI/CD Integration

```python
import sys
from coach_wizards import SecurityWizard, PerformanceWizard

def ci_check(file_path):
    """Run in CI/CD pipeline"""
    code = open(file_path).read()

    security = SecurityWizard()
    result = security.run_full_analysis(code, file_path, "python")

    # Fail CI if critical issues found
    critical_issues = [i for i in result.issues if i.severity == "error"]
    if critical_issues:
        print(f"FAILED: {len(critical_issues)} critical security issues found")
        for issue in critical_issues:
            print(f"  {issue.message} (line {issue.line_number})")
        sys.exit(1)

    print(f"PASSED: No critical issues")
    sys.exit(0)

if __name__ == "__main__":
    ci_check(sys.argv[1])
```

Add to your `.github/workflows/security.yml`:

```yaml
name: Security Check
on: [push, pull_request]
jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install empathy-framework
      - run: python ci_check.py src/app.py
```

### Pattern 4: Multi-Model Usage

```python
from empathy_llm_toolkit import EmpathyLLM

# Use Claude for complex reasoning (Level 4)
claude = EmpathyLLM(
    provider="anthropic",
    target_level=4,
    model="claude-3-5-sonnet-20241022"
)

# Use GPT-4 for quick responses (Level 2)
gpt = EmpathyLLM(
    provider="openai",
    target_level=2,
    model="gpt-4-turbo-preview"
)

# Use local model for privacy-sensitive tasks
local = EmpathyLLM(
    provider="local",
    target_level=2,
    endpoint="http://localhost:11434",
    model="llama2"
)

# Route to appropriate model
async def handle_request(user_input, priority):
    if priority == "high":
        return await claude.interact("user", user_input)
    elif priority == "medium":
        return await gpt.interact("user", user_input)
    else:
        return await local.interact("user", user_input)
```

---

## Troubleshooting

### Issue: ImportError for empathy_llm_toolkit

**Solution:**

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install langchain anthropic openai python-dotenv
```

### Issue: API key not found

**Solution:**

```bash
# Check if environment variable is set
echo $ANTHROPIC_API_KEY

# If empty, set it
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Make permanent
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc
```

### Issue: Module 'coach_wizards' not found

**Solution:**

```bash
# Ensure you're in the Empathy directory
cd /path/to/Empathy

# Install in development mode
pip install -e .

# Or add to Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/Empathy"
```

### Issue: "Target level not reached"

**Explanation:** The framework requires building trust before progressing to higher levels.

**Solution:**

```python
# Force a specific level for testing
result = await llm.interact(
    user_id="test",
    user_input="Test input",
    force_level=4  # Force Level 4 for demo
)

# Or build trust faster
for i in range(10):
    await llm.interact(user_id="test", user_input=f"Test {i}")
    llm.update_trust("test", outcome="success", magnitude=1.0)
```

### Issue: Slow response times

**Solution:**

```python
# Use faster model
llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307",  # Faster, cheaper
    target_level=3
)

# Or enable prompt caching (Claude only)
from empathy_llm_toolkit.providers import AnthropicProvider

provider = AnthropicProvider(
    use_prompt_caching=True,  # 90% cost reduction on repeated prompts
    model="claude-3-5-sonnet-20241022"
)
```

### Issue: Out of memory analyzing large codebases

**Solution:**

```python
# Use Claude's 200K context window for large codebases
from empathy_llm_toolkit.providers import AnthropicProvider

provider = AnthropicProvider(
    model="claude-3-5-sonnet-20241022"  # 200K context
)

# Analyze entire repository
files = [
    {"path": "app.py", "content": open("app.py").read()},
    {"path": "models.py", "content": open("models.py").read()},
    # ... add all files
]

result = await provider.analyze_large_codebase(
    codebase_files=files,
    analysis_prompt="Find all security vulnerabilities"
)
```

---

## Next Steps

Congratulations! You now have a working Empathy Framework installation. Here's what to explore next:

### 1. Read the User Guide

Comprehensive guide covering:
- Architecture and design patterns
- All 16+ Coach wizards in detail
- Advanced configuration
- Integration examples
- Best practices

**Location:** [docs/USER_GUIDE.md](USER_GUIDE.md)

### 2. Explore the API Reference

Complete API documentation:
- All classes and methods
- Parameter specifications
- Return types
- Code examples

**Location:** [docs/API_REFERENCE.md](API_REFERENCE.md)

### 3. Try More Wizards

Explore all available wizards:

```python
from coach_wizards import (
    SecurityWizard,
    PerformanceWizard,
    TestingWizard,
    AccessibilityWizard,
    RefactoringWizard,
    DatabaseWizard,
    APIWizard,
    MonitoringWizard,
    # ... 8+ more
)
```

### 4. Build Your Own Wizard

Extend the framework with domain-specific wizards:

```python
from coach_wizards import BaseCoachWizard, WizardIssue, WizardPrediction

class MyWizard(BaseCoachWizard):
    def __init__(self):
        super().__init__(
            name="MyWizard",
            category="custom",
            languages=['python', 'javascript']
        )

    def analyze_code(self, code, file_path, language):
        # Implement your analysis logic
        issues = []
        # ...
        return issues

    def predict_future_issues(self, code, file_path, project_context, timeline_days=90):
        # Implement Level 4 predictions
        predictions = []
        # ...
        return predictions

    def suggest_fixes(self, issue):
        # Implement fix suggestions
        return f"Fix for {issue.message}"
```

### 5. Join the Community

- **GitHub:** https://github.com/Deep-Study-AI/Empathy
- **Discussions:** https://github.com/Deep-Study-AI/Empathy/discussions
- **Issues:** https://github.com/Deep-Study-AI/Empathy/issues
- **Email:** patrick.roebuck@deepstudyai.com

### 6. Consider Commercial Support

Get priority support for production deployments:
- Priority bug fixes and feature requests
- Direct access to core development team
- Guaranteed response times
- Security advisories

**Price:** $99/developer/year

Learn more: [SPONSORSHIP.md](../SPONSORSHIP.md)

---

## Quick Reference Card

### Essential Commands

```bash
# Install
pip install empathy-framework anthropic

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run basic example
python hello_empathy.py

# Analyze code
python analyze_code.py
```

### Essential Code

```python
# Initialize
from empathy_llm_toolkit import EmpathyLLM
llm = EmpathyLLM(provider="anthropic", target_level=4)

# Interact
result = await llm.interact(user_id="me", user_input="Help me")

# Use wizard
from coach_wizards import SecurityWizard
wizard = SecurityWizard()
result = wizard.run_full_analysis(code, file_path, language)

# Build trust
llm.update_trust(user_id, outcome="success")
```

### Essential Files

- **Configuration:** `empathy.config.yml`
- **API Reference:** `docs/API_REFERENCE.md`
- **User Guide:** `docs/USER_GUIDE.md`
- **Examples:** `examples/`

---

## Success!

You've completed the Quick Start Guide! You now have:

- A working Empathy Framework installation
- Your first AI interactions at multiple levels
- Code analysis with Level 4 Anticipatory predictions
- Understanding of configuration and patterns

**Time to production:** 5 minutes
**ROI:** Infinite (4-6x productivity at $0 cost)

Welcome to Level 4 Anticipatory AI collaboration!

---

**Copyright 2025 Smart AI Memory, LLC**
**Licensed under Fair Source 0.9**
