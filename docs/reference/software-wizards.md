# Software Development Wizards

**16 specialized wizards** for software engineering tasks with Level 4 Anticipatory Intelligence.

## Overview

Software wizards analyze your code, predict issues before they happen, and provide actionable recommendations. Unlike simple linters, these wizards understand context, patterns, and project trajectories.

| Wizard | Purpose | Empathy Level |
|--------|---------|---------------|
| [Debugging](#debugging-wizard) | Root cause analysis, bug prediction | Level 4 |
| [Testing](#testing-wizard) | Test coverage gaps, edge case detection | Level 3 |
| [Security](#security-wizard) | Vulnerability detection, OWASP compliance | Level 4 |
| [Performance](#performance-wizard) | Bottleneck prediction, optimization | Level 4 |
| [API](#api-wizard) | Design review, versioning, documentation | Level 3 |
| [Database](#database-wizard) | Query optimization, schema analysis | Level 4 |
| [Documentation](#documentation-wizard) | Missing docs, clarity improvements | Level 2 |
| [Refactoring](#refactoring-wizard) | Code smell detection, architecture | Level 3 |
| [Compliance](#compliance-wizard) | GDPR, SOC2, HIPAA code patterns | Level 4 |
| [Monitoring](#monitoring-wizard) | Observability gaps, alerting | Level 3 |
| [CI/CD](#cicd-wizard) | Pipeline optimization, security | Level 3 |
| [Accessibility](#accessibility-wizard) | WCAG compliance, screen reader | Level 2 |
| [Localization](#localization-wizard) | i18n issues, RTL support | Level 2 |
| [Migration](#migration-wizard) | Risk assessment, rollback planning | Level 4 |
| [Observability](#observability-wizard) | Tracing, SLO definition | Level 3 |
| [Scaling](#scaling-wizard) | Capacity planning, bottleneck prediction | Level 4 |

---

## Debugging Wizard

**Level 4 Anticipatory** - Predicts bugs before they cause production incidents.

### What It Does

The Debugging Wizard goes beyond finding existing bugs. It analyzes code patterns, identifies risk areas, and predicts where bugs are likely to emerge.

### Quick Start

```python
from coach_wizards import DebuggingWizard

wizard = DebuggingWizard()

# Analyze code for issues
issues = wizard.analyze_code(
    code="""
def process_payment(order):
    total = order['total']  # KeyError if missing
    tax = total * 0.08
    result = charge_card(user.card, total + tax)
    if result:
        send_email(user.email)  # No error handling
    return result
""",
    file_path="payment.py",
    language="python"
)

for issue in issues:
    print(f"[{issue.severity}] Line {issue.line}: {issue.message}")
    if issue.suggestion:
        print(f"  Fix: {issue.suggestion}")
```

### Output

```
[ERROR] Line 2: Potential KeyError - 'total' may not exist in order dict
  Fix: Use order.get('total', 0) or validate input
[WARNING] Line 5: Undefined variable 'user' - not passed to function
  Fix: Add 'user' parameter or retrieve from context
[WARNING] Line 6: No error handling for email failure
  Fix: Wrap in try-except, consider async/queue
```

### Common Patterns Detected

| Pattern | Severity | Description |
|---------|----------|-------------|
| `KeyError Risk` | ERROR | Dict access without existence check |
| `Undefined Variable` | ERROR | Variable used before definition |
| `Missing Error Handling` | WARNING | Try-except needed for external calls |
| `N+1 Query` | WARNING | Database query inside loop |
| `Resource Leak` | WARNING | File/connection not properly closed |
| `Race Condition` | ERROR | Unsynchronized shared state access |

### Integration Example

```python
# Pre-commit hook integration
import subprocess

wizard = DebuggingWizard()

def pre_commit_check(files):
    """Run debugging wizard on changed files"""
    all_issues = []

    for file_path in files:
        if file_path.endswith('.py'):
            with open(file_path) as f:
                code = f.read()

            issues = wizard.analyze_code(
                code=code,
                file_path=file_path,
                language="python"
            )

            # Block commit on errors
            errors = [i for i in issues if i.severity == "error"]
            if errors:
                all_issues.extend(errors)

    return all_issues
```

---

## Security Wizard

**Level 4 Anticipatory** - Predicts security vulnerabilities before exploitation.

### What It Does

Scans code for OWASP Top 10 vulnerabilities, hardcoded secrets, and security anti-patterns. Provides remediation suggestions with code examples.

### Quick Start

```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()

issues = wizard.analyze_code(
    code="""
from flask import Flask, request

app = Flask(__name__)
SECRET_KEY = "production_secret_key_123"  # Hardcoded

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    query = f"SELECT * FROM users WHERE username='{username}'"
    return db.execute(query)
""",
    file_path="app.py",
    language="python"
)

for issue in issues:
    print(f"[{issue.severity}] {issue.message}")
```

### Output

```
[CRITICAL] Line 4: Hardcoded secret detected - SECRET_KEY contains credentials
  Fix: Use environment variable: os.getenv('SECRET_KEY')

[CRITICAL] Line 9: SQL Injection vulnerability - user input directly in query
  Fix: Use parameterized query: cursor.execute("SELECT * FROM users WHERE username = ?", (username,))

[WARNING] Line 7: Form input used without validation
  Fix: Validate and sanitize: username = sanitize_input(request.form.get('username', ''))
```

### Vulnerability Categories

| Category | OWASP | Examples |
|----------|-------|----------|
| Injection | A03:2021 | SQL, NoSQL, OS Command, LDAP |
| Broken Auth | A07:2021 | Weak passwords, session fixation |
| Sensitive Data | A02:2021 | Hardcoded secrets, unencrypted PII |
| XXE | A05:2021 | XML external entity attacks |
| Broken Access | A01:2021 | Missing authorization checks |
| Misconfig | A05:2021 | Debug mode, default credentials |
| XSS | A03:2021 | Reflected, stored, DOM-based |
| Insecure Deserialization | A08:2021 | Pickle, YAML unsafe load |
| Components | A06:2021 | Known vulnerable dependencies |
| Logging | A09:2021 | Insufficient logging/monitoring |

### Secrets Detection

```python
# Detected secret patterns
SECRETS_PATTERNS = [
    "api_key", "api_secret", "apikey", "apisecret",
    "secret_key", "secretkey", "private_key", "privatekey",
    "password", "passwd", "pwd",
    "aws_access_key", "aws_secret",
    "github_token", "gitlab_token",
    "slack_token", "discord_token",
    "stripe_key", "paypal_secret",
    "jwt_secret", "encryption_key",
    "database_url", "redis_url",
    "ssh_key", "bearer_token"
]
```

---

## Performance Wizard

**Level 4 Anticipatory** - Predicts performance bottlenecks before they impact users.

### What It Does

Analyzes code for performance anti-patterns, predicts scaling issues, and recommends optimizations based on your application's growth trajectory.

### Quick Start

```python
from coach_wizards import PerformanceWizard

wizard = PerformanceWizard()

issues = wizard.analyze_code(
    code="""
def get_recommendations(user_id):
    user = User.objects.get(id=user_id)
    orders = Order.objects.filter(user=user)

    recommendations = []
    for order in orders:  # N+1 problem
        for item in order.items.all():  # Another N+1
            similar = Product.objects.filter(category=item.category)[:10]
            recommendations.extend(similar)

    return recommendations
""",
    file_path="recommendations.py",
    language="python"
)
```

### Output

```
[ERROR] Line 5-7: N+1 Query detected - 2 nested loops with database queries
  Impact: O(n*m) database calls where n=orders, m=items
  Fix: Use select_related/prefetch_related:
       orders = Order.objects.filter(user=user).prefetch_related('items', 'items__category')

[WARNING] Line 8: Query inside loop - O(n) database calls
  Fix: Batch query outside loop:
       categories = [item.category for item in items]
       similar = Product.objects.filter(category__in=categories)[:100]

[INFO] Line 4: Missing index hint - filter on 'user' without index
  Fix: Ensure index exists: CREATE INDEX idx_order_user ON orders(user_id)
```

### Performance Patterns

| Pattern | Complexity | Detection |
|---------|------------|-----------|
| N+1 Query | O(n) → O(1) | Loop with ORM query |
| Missing Index | O(n) → O(log n) | Filter/WHERE without index |
| Unbounded Query | O(n) memory | SELECT without LIMIT |
| String Concatenation | O(n²) | Loop with += on strings |
| Nested Loops | O(n²) | Nested iteration |
| Sync in Async | Blocking | Sync I/O in async context |
| No Caching | Repeated work | Same computation repeated |

---

## API Wizard

**Level 3 Proactive** - Identifies API design issues before they become breaking changes.

### What It Does

Reviews API endpoints for best practices, versioning, security, and documentation. Predicts backward compatibility issues.

### Quick Start

```python
from coach_wizards import APIWizard

wizard = APIWizard()

issues = wizard.analyze_code(
    code="""
@app.get("/users/{user_id}")
def get_user(user_id: str):
    # No authentication
    # No rate limiting
    return db.users.find_one({"_id": user_id})

@app.post("/users")
def create_user(data: dict):
    # No schema validation
    return db.users.insert_one(data)

@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    # No soft delete
    return db.users.delete_one({"_id": user_id})
""",
    file_path="api.py",
    language="python"
)
```

### Output

```
[ERROR] Line 1-4: No authentication on user endpoint
  Fix: Add authentication decorator: @requires_auth

[WARNING] Line 1: No API versioning detected
  Fix: Use versioned routes: /v1/users/{user_id}

[WARNING] Line 7-9: No request schema validation
  Fix: Use Pydantic model: def create_user(data: UserCreate)

[WARNING] Line 11-13: Hard delete without soft delete option
  Fix: Use soft delete: user.deleted_at = datetime.now()

[INFO] Line 1: No rate limiting detected
  Fix: Add rate limit: @limiter.limit("100/minute")
```

### API Best Practices Checklist

- [ ] **Authentication** - All endpoints require auth
- [ ] **Authorization** - Role-based access control
- [ ] **Versioning** - /v1/, /v2/ in URL path
- [ ] **Rate Limiting** - Prevent abuse
- [ ] **Input Validation** - Schema validation (Pydantic, JSON Schema)
- [ ] **Error Handling** - Consistent error format
- [ ] **Pagination** - Limit/offset or cursor-based
- [ ] **CORS** - Configured for allowed origins
- [ ] **Documentation** - OpenAPI/Swagger spec

---

## Testing Wizard

**Level 3 Proactive** - Identifies test coverage gaps and missing edge cases.

### What It Does

Analyzes code and tests to find untested paths, edge cases, and potential regressions. Suggests test cases you're missing.

### Quick Start

```python
from coach_wizards import TestingWizard

wizard = TestingWizard()

issues = wizard.analyze_code(
    code="""
class PaymentProcessor:
    def process(self, amount, card):
        if amount <= 0:
            raise ValueError("Invalid amount")
        if not card.is_valid():
            raise CardError("Invalid card")
        result = self.gateway.charge(card, amount)
        return result
""",
    file_path="payment.py",
    language="python"
)
```

### Output

```
[WARNING] Missing test cases detected:
  - Edge case: amount = 0 (boundary)
  - Edge case: amount = negative
  - Edge case: amount = very large (overflow)
  - Error path: card.is_valid() returns False
  - Error path: gateway.charge() raises exception
  - Error path: gateway.charge() returns partial success
  - Concurrency: multiple simultaneous charges

Suggested test skeleton:
  def test_process_zero_amount(self):
      with pytest.raises(ValueError):
          processor.process(0, valid_card)

  def test_process_gateway_failure(self):
      gateway.charge.side_effect = GatewayError()
      with pytest.raises(GatewayError):
          processor.process(100, valid_card)
```

---

## Database Wizard

**Level 4 Anticipatory** - Predicts database performance issues before they cause outages.

### Quick Start

```python
from coach_wizards import DatabaseWizard

wizard = DatabaseWizard()

issues = wizard.analyze_code(
    code="""
SELECT u.*, o.*, p.*, r.*
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN products p ON o.product_id = p.id
JOIN reviews r ON p.id = r.product_id
WHERE u.created_at > '2024-01-01'
AND o.status = 'completed'
""",
    file_path="query.sql",
    language="sql"
)
```

### Output

```
[ERROR] Line 1: SELECT * returns unnecessary columns - specify needed columns
[WARNING] Line 2-5: 4-way JOIN may cause cartesian product explosion
  Estimated rows: users(10K) * orders(50K) * products(1K) * reviews(100K)
[WARNING] Line 6: Filter on created_at without index
  Fix: CREATE INDEX idx_users_created ON users(created_at)
[INFO] Line 7: Consider partitioning orders by status for faster queries
```

---

## All Software Wizards at a Glance

```python
from coach_wizards import (
    DebuggingWizard,
    TestingWizard,
    SecurityWizard,
    DocumentationWizard,
    PerformanceWizard,
    RefactoringWizard,
    DatabaseWizard,
    APIWizard,
    ComplianceWizard,
    MonitoringWizard,
    CICDWizard,
    AccessibilityWizard,
    LocalizationWizard,
    MigrationWizard,
    ObservabilityWizard,
    ScalingWizard
)

# Initialize any wizard
wizard = SecurityWizard()

# All wizards have the same interface
issues = wizard.analyze_code(
    code="...",
    file_path="file.py",
    language="python"
)

# Each issue has:
# - issue.severity: "error" | "warning" | "info"
# - issue.line: Line number
# - issue.message: Description
# - issue.suggestion: How to fix
# - issue.type: Category of issue
```

---

## Integration Patterns

### Pre-Commit Hook

```python
#!/usr/bin/env python3
"""Pre-commit hook using software wizards"""

import sys
from coach_wizards import SecurityWizard, DebuggingWizard

def main():
    wizards = [SecurityWizard(), DebuggingWizard()]
    files = sys.argv[1:]

    errors = []
    for file_path in files:
        if not file_path.endswith('.py'):
            continue

        with open(file_path) as f:
            code = f.read()

        for wizard in wizards:
            issues = wizard.analyze_code(code, file_path, "python")
            errors.extend([i for i in issues if i.severity == "error"])

    if errors:
        print("Commit blocked - fix these issues:")
        for e in errors:
            print(f"  {e.file}:{e.line}: {e.message}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### CI Pipeline

```yaml
# .github/workflows/wizard-check.yml
name: Wizard Analysis
on: [pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install empathy-framework
      - run: python -m coach_wizards.cli analyze --path . --format github
```

---

## See Also

- [AI Development Wizards](ai-wizards.md) - LLM/ML specialized wizards
- [Industry Wizards](wizards.md) - Domain-specific wizards
- [Configuration](config.md) - Wizard configuration
