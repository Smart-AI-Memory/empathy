# Quickstart Guide

Get started with the Empathy Framework in 5 minutes.

## Installation

```bash
# Clone the repository
git clone https://github.com/Deep-Study-AI/Empathy.git
cd Empathy

# Install dependencies
pip install -r requirements.txt
```

## Your First Wizard (60 seconds)

Let's use the Security Wizard to analyze a simple Python file:

### 1. Create a sample file with security issues

```python
# sample.py
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability!
    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)
    return cursor.fetchone()

API_KEY = "sk-1234567890abcdef"  # Hardcoded secret!

def process_user_input(data):
    # No input validation!
    eval(data)  # Dangerous!
```

### 2. Run the Security Wizard

```python
from coach_wizards.security_wizard import SecurityWizard

# Initialize the wizard
wizard = SecurityWizard()

# Read the sample file
with open('sample.py', 'r') as f:
    code = f.read()

# Analyze the code
result = wizard.run_full_analysis(
    code=code,
    file_path='sample.py',
    language='python'
)

# Print results
print(f"Found {len(result.issues)} security issues:")
for issue in result.issues:
    print(f"  [{issue.severity.upper()}] {issue.message}")
    if issue.fix_suggestion:
        print(f"  Fix: {issue.fix_suggestion}\n")
```

### 3. Expected Output

```
Found 3 security issues:
  [ERROR] SQL Injection vulnerability: String interpolation in SQL query
  Fix: Use parameterized queries: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))

  [ERROR] Hardcoded API key detected
  Fix: Use environment variables: os.getenv('API_KEY')

  [ERROR] Use of eval() with user input
  Fix: Use ast.literal_eval() or JSON parsing instead
```

## Level 4 Anticipatory Predictions (2 minutes)

Now let's see **future** problems with predictions 30-90 days ahead:

```python
from coach_wizards.security_wizard import SecurityWizard

wizard = SecurityWizard()

# Provide project context for better predictions
project_context = {
    "team_size": 5,
    "deployment_frequency": "daily",
    "user_count": 1000,
    "growth_rate": "20% monthly"
}

result = wizard.run_full_analysis(
    code=code,
    file_path='sample.py',
    language='python',
    project_context=project_context
)

# Level 4 Predictions
print(f"\nPredicted issues in next 90 days: {len(result.predictions)}")
for pred in result.predictions:
    print(f"\n[{pred.impact.upper()}] {pred.issue_type}")
    print(f"  Predicted date: {pred.predicted_date.strftime('%Y-%m-%d')}")
    print(f"  Probability: {pred.probability:.0%}")
    print(f"  Reasoning: {pred.reasoning}")
    print(f"  Prevention steps:")
    for step in pred.prevention_steps:
        print(f"    - {step}")
```

### Expected Prediction Output

```
Predicted issues in next 90 days: 2

[CRITICAL] SQL Injection Attack
  Predicted date: 2025-03-15
  Probability: 85%
  Reasoning: With 20% monthly user growth, you'll reach 2,000+ users by March.
             SQL injection vulnerabilities become high-probability attack targets
             at this scale. Attack surface grows exponentially.
  Prevention steps:
    - Migrate to parameterized queries NOW (2-day task)
    - Add input validation layer (1-day task)
    - Implement SQL query logging and monitoring
    - Set up automated security scanning in CI/CD

[HIGH] API Key Exposure in Version Control
  Predicted date: 2025-02-20
  Probability: 65%
  Reasoning: Hardcoded secrets in source code will likely be committed to git
             history. With daily deployments and 5 team members, accidental
             commits are probable within 30-45 days.
  Prevention steps:
    - Move API keys to environment variables TODAY
    - Add pre-commit hooks to block secret commits
    - Rotate exposed API key immediately
    - Implement secrets management (AWS Secrets Manager, HashiCorp Vault)
```

## Multiple Wizards Example (3 minutes)

Use multiple wizards together for comprehensive analysis:

```python
from coach_wizards import SecurityWizard, PerformanceWizard, TestingWizard

# Initialize multiple wizards
security = SecurityWizard()
performance = PerformanceWizard()
testing = TestingWizard()

code = """
def get_all_users():
    users = []
    for user_id in range(1, 10000):
        user = get_user(user_id)  # N+1 query problem!
        users.append(user)
    return users

# No tests written!
"""

# Run all wizards
security_result = security.analyze_code(code, 'app.py', 'python')
performance_result = performance.analyze_code(code, 'app.py', 'python')
testing_result = testing.analyze_code(code, 'app.py', 'python')

# Aggregate results
all_issues = security_result + performance_result + testing_result
print(f"Total issues found: {len(all_issues)}")

for issue in sorted(all_issues, key=lambda x: x.severity, reverse=True):
    print(f"[{issue.severity}] {issue.category}: {issue.message}")
```

## Next Steps

### Explore Other Wizards

```python
from coach_wizards import (
    AccessibilityWizard,    # WCAG compliance
    DatabaseWizard,         # Query optimization
    APIWizard,              # API design patterns
    RefactoringWizard,      # Code quality
    ComplianceWizard,       # GDPR, SOC 2
    # ... 11 more wizards!
)
```

### Integrate with Your IDE

See the full IDE integration examples:
- **JetBrains**: [examples/coach/jetbrains-plugin-complete/](../coach/jetbrains-plugin-complete/)
- **VS Code**: [examples/coach/vscode-extension-complete/](../coach/vscode-extension-complete/)
- **LSP Server**: [examples/coach/coach-lsp-server/](../coach/coach-lsp-server/)

### Customize Wizards

Create your own wizard by extending `BaseCoachWizard`:

```python
from coach_wizards.base_wizard import BaseCoachWizard, WizardIssue, WizardPrediction

class MyCustomWizard(BaseCoachWizard):
    def __init__(self):
        super().__init__(
            name="MyCustomWizard",
            category="Custom",
            languages=["python", "javascript"]
        )

    def analyze_code(self, code: str, file_path: str, language: str):
        issues = []
        # Your custom analysis logic here
        return issues

    def predict_future_issues(self, code: str, file_path: str,
                             project_context: dict, timeline_days: int = 90):
        predictions = []
        # Your Level 4 prediction logic here
        return predictions
```

## Healthcare Use Case

For healthcare/clinical applications:

```python
from agents.compliance_anticipation_agent import ComplianceAnticipationAgent
from wizards.sbar_wizard import SBARWizard

# Predict compliance audits
compliance_agent = ComplianceAnticipationAgent()
audit_prediction = compliance_agent.predict_audit(
    context="Healthcare facility with 500 patient records",
    timeline_days=90
)

# Generate clinical documentation
sbar = SBARWizard()
report = sbar.generate_report(
    situation="Patient experiencing chest pain",
    background="History of hypertension, 65yo male",
    assessment="Possible cardiac event",
    recommendation="Immediate EKG and cardiology consult"
)
```

## Need Help?

- **Documentation**: [docs/](../../docs/)
- **Full Examples**: [examples/coach/](../coach/)
- **Issues**: https://github.com/Deep-Study-AI/Empathy/issues
- **Discussions**: https://github.com/Deep-Study-AI/Empathy/discussions
- **Email**: patrick.roebuck@deepstudyai.com

## What Makes This Different?

Traditional code analysis tools tell you about problems **now**.

Empathy Framework's Level 4 Anticipatory approach predicts problems **30-90 days ahead** based on:
- Code trajectory analysis
- Team velocity patterns
- Dependency evolution trends
- Historical bug patterns
- Architecture stress points

**Example**: Instead of "This query is slow," you get:
> "In 60 days, this query will timeout when you hit 10,000 users based on your current 20% monthly growth rate. Here's the optimized version with proper indexing."

Start preventing problems before they happen!
