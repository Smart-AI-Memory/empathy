# Coach User Manual

Complete guide to using Coach with all 16 specialized wizards.

**Built on LangChain** - Extensible AI wizard framework for developers.

---

## Table of Contents

- [Introduction](#introduction)
- [Core Concepts](#core-concepts)
- [Getting Started](#getting-started)
- [The 16 Wizards](#the-16-wizards)
- [Common Workflows](#common-workflows)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)

---

## Introduction

Coach is an AI-powered development assistant with **Level 4 Anticipatory Empathy** - it predicts problems 30-90 days before they occur and guides you through complex scenarios with 16 specialized wizard experts.

### What Makes Coach Different?

- **🔮 Level 4 Predictions**: Anticipates issues months ahead
- **🧙 16 Specialized Wizards**: Each expert in their domain
- **🤝 Multi-Wizard Collaboration**: Wizards consult each other for complex problems
- **🛡️ Privacy-First**: Local-only processing (cloud optional)
- **🔧 Extensible**: Build custom wizards with LangChain

### Level 4 Anticipatory Empathy

Traditional tools react to existing problems. Coach **predicts future problems**:

```python
# You write:
pool_size = 10

# Coach predicts (Level 4):
⚠️ At 5K req/day growth rate, this connection pool
   will saturate in ~45 days

Impact:
- 503 Service Unavailable errors
- Request timeouts
- Cascade failures

Preventive Action: Increase to 50 connections NOW
```

---

## Core Concepts

### Wizards

Each wizard is a specialized AI expert:

- **SecurityWizard** - Finds vulnerabilities before exploits
- **PerformanceWizard** - Predicts bottlenecks before outages
- **DebuggingWizard** - Root cause analysis for complex bugs
- **...and 13 more**

### Wizard Coordination

For complex tasks, wizards collaborate:

```
Scenario: New API Endpoint
├─ APIWizard (Primary)
│  ├─ Consults: SecurityWizard (authentication)
│  ├─ Consults: PerformanceWizard (rate limiting)
│  └─ Consults: DatabaseWizard (query optimization)
└─ Result: Comprehensive API design with security, performance, and data considerations
```

### Analysis Modes

1. **Instant Analysis** - Pattern-based, <100ms, local
2. **Deep Analysis** - Full wizard analysis, 1-5s, uses LSP
3. **Multi-Wizard Review** - Complex scenarios, 10-30s, coordinates multiple wizards

---

## Getting Started

### Basic Usage

#### 1. Real-Time Analysis (Automatic)

Simply open any file - Coach analyzes as you type:

```python
# Type this:
password = "admin123"

# Coach immediately shows:
⚠️ Hardcoded secret detected
💡 Use environment variables: os.getenv('PASSWORD')
```

#### 2. On-Demand Analysis

**VS Code**:
- Press `Ctrl+Shift+P`
- Type: "Coach: Analyze File"
- Or right-click → "Analyze File with Coach"

**JetBrains**:
- Right-click in editor
- Select: **Coach → Analyze File**
- Or: `Ctrl+Alt+C`

#### 3. Specific Wizard Analysis

Run a specific wizard on your code:

**VS Code Commands**:
- "Coach: Security Audit" - SecurityWizard
- "Coach: Performance Profile" - PerformanceWizard
- "Coach: Generate Tests" - TestingWizard
- "Coach: Accessibility Check" - AccessibilityWizard

**JetBrains Actions**:
- Right-click → **Coach → Security Audit**
- Right-click → **Coach → Performance Profile**
- Right-click → **Coach → Accessibility Check**

---

## The 16 Wizards

### 1. SecurityWizard 🛡️

**Expertise**: Vulnerability detection, OWASP Top 10, secure coding

**Detects**:
- SQL injection
- XSS (Cross-Site Scripting)
- CSRF vulnerabilities
- Hardcoded secrets
- Weak cryptography
- Insecure deserialization
- Authentication flaws
- Authorization bypasses

**Example**:

```python
# Your code:
user_id = request.GET['user_id']
query = f"SELECT * FROM users WHERE id={user_id}"
cursor.execute(query)

# SecurityWizard:
🛡️ SQL Injection Vulnerability (HIGH RISK)

Exploit Scenario:
user_id = "1 OR 1=1; DROP TABLE users--"
→ Results in: SELECT * FROM users WHERE id=1 OR 1=1; DROP TABLE users--

Impact: Complete database compromise

Fix:
cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))

[Apply Fix] [Run Full Security Audit]
```

**When to Use**:
- Before committing security-sensitive code
- After modifying authentication/authorization
- During code review
- Before production deployment

---

### 2. PerformanceWizard ⚡

**Expertise**: Performance optimization, scalability, resource management

**Detects**:
- N+1 queries
- Inefficient algorithms (O(n²) loops)
- Memory leaks
- Blocking operations
- Large data structures
- Missing indexes
- Cache misses
- Resource exhaustion

**Example**:

```python
# Your code:
for user in users:
    orders = Order.objects.filter(user_id=user.id).all()
    process(orders)

# PerformanceWizard:
⚡ N+1 Query Pattern (WARNING)

Issue: Loop with database queries = 1001 queries
Current: ~2.5 seconds for 1000 users
Impact:
- Slow response times
- High database load
- Poor user experience

Fix:
# Batch query:
user_ids = [u.id for u in users]
orders = Order.objects.filter(user_id__in=user_ids).prefetch_related('items')

Performance Improvement: ~2.5s → ~50ms (50x faster)

[Apply Fix] [Run Performance Profile]
```

**Level 4 Prediction Example**:

```python
# Your code:
pool_size = 10

# PerformanceWizard (Level 4):
⚠️ Connection Pool Saturation Prediction

Current: 10 connections
Traffic: 1000 req/day, growing at 5000 req/day

Prediction: Pool will saturate in ~45 days (Feb 28, 2025)

Impact Timeline:
- Week 1-2: Occasional slow queries
- Week 3-4: Intermittent 503 errors
- Week 5-6: Service outage during peak hours

Preventive Action (Act within 30 days):
pool_size = 50
max_overflow = 20
pool_timeout = 30

[Apply Fix] [Set Reminder] [Run Capacity Planning]
```

**When to Use**:
- Before deploying to production
- When experiencing slow response times
- During capacity planning
- After adding new features

---

### 3. AccessibilityWizard ♿

**Expertise**: WCAG 2.1 AA/AAA compliance, screen readers, keyboard navigation

**Detects**:
- Missing alt text
- Missing ARIA labels
- Keyboard accessibility issues
- Color contrast violations
- Semantic HTML issues
- Form accessibility
- Heading hierarchy problems

**Example**:

```html
<!-- Your code: -->
<button onclick="submit()">
  <img src="check.svg">
</button>

<!-- AccessibilityWizard: -->
♿ Accessibility Violations (2 found)

1. Button without text content
   WCAG: 4.1.2 (Level A)
   Issue: Screen readers can't announce button purpose
   Fix: <button aria-label="Submit form" onclick="submit()">

2. Image without alt text
   WCAG: 1.1.1 (Level A)
   Issue: Screen readers can't describe image
   Fix: <img src="check.svg" alt="Checkmark icon">

Impact: ~15% of users (screen reader, keyboard-only) cannot use this feature

[Apply Fixes] [Run Full A11y Audit]
```

**When to Use**:
- Before launching public-facing features
- During UI development
- When adding forms or interactive elements
- During compliance reviews

---

### 4. DebuggingWizard 🐛

**Expertise**: Root cause analysis, stack trace interpretation, debugging strategies

**Capabilities**:
- Analyzes stack traces
- Identifies root causes
- Suggests debugging strategies
- Explains error patterns
- Predicts related bugs

**Example**:

```python
# Error:
Traceback (most recent call last):
  File "app.py", line 42, in process_payment
    amount = float(request.data['amount'])
KeyError: 'amount'

# DebuggingWizard:
🐛 Root Cause Analysis

Primary Issue: Missing input validation
Root Cause: Assuming 'amount' key exists without checking

Why This Happened:
1. Frontend doesn't always send 'amount' (optional field?)
2. No validation middleware
3. No default value handling

Related Bugs (High Probability):
- Same pattern in process_refund() (line 67)
- Same pattern in update_price() (line 89)

Fix (Best Practice):
amount = request.data.get('amount')
if amount is None:
    return error_response('Missing amount', 400)
try:
    amount = float(amount)
except (ValueError, TypeError):
    return error_response('Invalid amount format', 400)

Preventive:
1. Add JSON schema validation middleware
2. Use Pydantic models for request validation
3. Add integration tests for missing fields

[Apply Fix] [Fix Related Bugs] [Add Tests]
```

**When to Use**:
- When debugging complex errors
- After encountering unexpected behavior
- During post-mortem analysis
- When errors seem intermittent

---

### 5. TestingWizard 🧪

**Expertise**: Test generation, coverage analysis, test strategy

**Capabilities**:
- Generates unit tests
- Generates integration tests
- Identifies untested paths
- Suggests edge cases
- Creates test fixtures
- Mocking strategies

**Example**:

```python
# Your code:
def calculate_discount(price, user_tier, coupon=None):
    if user_tier == 'premium':
        discount = 0.20
    elif user_tier == 'gold':
        discount = 0.10
    else:
        discount = 0.0

    if coupon:
        discount += coupon.value

    return price * (1 - discount)

# TestingWizard:
🧪 Test Generation

Generated 12 test cases covering:
- ✓ Happy paths (3 tests)
- ✓ Edge cases (5 tests)
- ✓ Error conditions (4 tests)

test_calculate_discount.py:

def test_premium_user_discount():
    assert calculate_discount(100, 'premium') == 80.0

def test_gold_user_discount():
    assert calculate_discount(100, 'gold') == 90.0

def test_standard_user_no_discount():
    assert calculate_discount(100, 'standard') == 100.0

def test_premium_with_coupon():
    coupon = Coupon(value=0.10)
    assert calculate_discount(100, 'premium', coupon) == 70.0

def test_discount_exceeds_100_percent():
    """Edge case: total discount > 100%"""
    coupon = Coupon(value=0.90)
    result = calculate_discount(100, 'premium', coupon)
    # BUG: Returns negative price!
    # RECOMMENDATION: Add validation

def test_invalid_user_tier():
    """Missing: should handle invalid tier"""
    # RECOMMENDATION: Add error handling

Coverage: 85% (missing error handling)

[Generate Tests] [Add to Test Suite] [Run Tests]
```

**When to Use**:
- After writing new functions
- When test coverage is low
- Before refactoring
- During TDD (Test-Driven Development)

---

### 6. RefactoringWizard 🔧

**Expertise**: Code quality, maintainability, design patterns

**Detects**:
- Code smells
- Duplicate code
- Long functions
- Complex conditionals
- Poor naming
- Missing abstractions
- Anti-patterns

**Example**:

```python
# Your code:
def process_order(order):
    if order.status == 'pending':
        if order.payment_method == 'credit_card':
            if order.amount < 1000:
                charge_credit_card(order)
                send_confirmation(order)
                update_inventory(order)
                log_order(order)
            else:
                if verify_card(order):
                    charge_credit_card(order)
                    send_confirmation(order)
                    update_inventory(order)
                    log_order(order)
                else:
                    reject_order(order)
        elif order.payment_method == 'paypal':
            # Similar nested logic...
            pass

# RefactoringWizard:
🔧 Refactoring Recommendations

Issues Found (Priority: HIGH):
1. Cyclomatic Complexity: 12 (threshold: 10)
2. Nesting Level: 5 (threshold: 3)
3. Duplicate Code: 4 instances
4. Function Length: 89 lines (threshold: 50)

Recommended Refactoring:

# 1. Extract payment methods
class PaymentProcessor:
    @staticmethod
    def process(order):
        if order.payment_method == 'credit_card':
            return CreditCardProcessor().process(order)
        elif order.payment_method == 'paypal':
            return PayPalProcessor().process(order)
        raise ValueError(f"Unknown payment method: {order.payment_method}")

# 2. Extract order completion
def complete_order(order):
    send_confirmation(order)
    update_inventory(order)
    log_order(order)

# 3. Use strategy pattern
def process_order(order):
    if order.status != 'pending':
        raise ValueError("Order not pending")

    processor = PaymentProcessor.process(order)
    if processor.charge():
        complete_order(order)
    else:
        reject_order(order)

Improvements:
- Cyclomatic Complexity: 12 → 3
- Nesting Level: 5 → 2
- Lines of Code: 89 → 15
- Testability: Significantly improved
- Maintainability: +45%

[Apply Refactoring] [Preview Changes] [Run Tests After]
```

**When to Use**:
- During code review
- Before adding new features
- When code becomes hard to understand
- During technical debt cleanup

---

### 7. DatabaseWizard 🗄️

**Expertise**: Schema design, query optimization, indexing, migrations

**Capabilities**:
- Schema review
- Query optimization
- Index recommendations
- Migration planning
- Data modeling
- Performance tuning

**Example**:

```sql
-- Your query:
SELECT u.*, o.*, p.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN products p ON o.product_id = p.id
WHERE u.created_at > '2024-01-01'
ORDER BY o.created_at DESC
LIMIT 100;

-- DatabaseWizard:
🗄️ Query Optimization

Performance Analysis:
- Current: 2.8 seconds (SLOW)
- Rows scanned: 1.2M users, 5M orders, 10K products
- Missing indexes: 3

Issues:
1. SELECT * fetches unnecessary columns
2. Missing index on users.created_at
3. Missing index on orders.user_id
4. Missing index on orders.created_at
5. Inefficient join order

Optimized Query:
-- Add indexes first:
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at DESC);

-- Optimized query:
SELECT
    u.id, u.name, u.email,
    o.id AS order_id, o.amount, o.created_at AS order_date,
    p.id AS product_id, p.name AS product_name
FROM users u
INNER JOIN orders o ON u.id = o.user_id
INNER JOIN products p ON o.product_id = p.id
WHERE u.created_at > '2024-01-01'
ORDER BY o.created_at DESC
LIMIT 100;

Performance After Optimization:
- Execution Time: 2.8s → 45ms (62x faster)
- Rows Scanned: 1.2M → 5K (240x reduction)
- Index Usage: 0% → 100%

[Apply Optimization] [Create Indexes] [Run Explain Plan]
```

**When to Use**:
- When queries are slow
- Before production deployment
- During schema design
- When adding indexes
- During database migrations

---

### 8. APIWizard 🌐

**Expertise**: REST/GraphQL design, OpenAPI specs, API best practices

**Capabilities**:
- API design review
- OpenAPI/Swagger generation
- Endpoint optimization
- Versioning strategy
- Rate limiting design
- Authentication patterns

**Example**:

```python
# Your code:
@app.route('/api/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user():
    if request.method == 'GET':
        user_id = request.args.get('id')
        return get_user(user_id)
    elif request.method == 'POST':
        return create_user(request.json)
    elif request.method == 'PUT':
        return update_user(request.json)
    elif request.method == 'DELETE':
        return delete_user(request.args.get('id'))

# APIWizard:
🌐 API Design Review

Issues Found (Priority: MEDIUM-HIGH):
1. Violates RESTful conventions
2. Inconsistent parameter passing (query vs body)
3. Missing status codes
4. No error handling
5. No input validation
6. Missing OpenAPI spec

RESTful API Design:

# GET /api/users - List all users
@app.route('/api/users', methods=['GET'])
def list_users():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    users = User.query.paginate(page=page, per_page=limit)
    return jsonify({
        'data': [u.to_dict() for u in users.items],
        'page': page,
        'total': users.total
    }), 200

# GET /api/users/:id - Get specific user
@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

# POST /api/users - Create user
@app.route('/api/users', methods=['POST'])
@validate_json(UserSchema)
def create_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201

# PUT /api/users/:id - Update user
@app.route('/api/users/<int:user_id>', methods=['PUT'])
@validate_json(UserSchema)
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.update(**request.json)
    db.session.commit()
    return jsonify(user.to_dict()), 200

# DELETE /api/users/:id - Delete user
@app.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

Generated OpenAPI 3.0 Spec:
openapi: 3.0.0
info:
  title: User API
  version: 1.0.0
paths:
  /api/users:
    get:
      summary: List all users
      parameters:
        - name: page
          in: query
          schema: {type: integer, default: 1}
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/UserList'
    post:
      summary: Create user
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: User created

[Apply Refactoring] [Generate Full OpenAPI Spec] [Add Rate Limiting]
```

**When to Use**:
- When designing new APIs
- During API review
- Before publishing APIs
- When updating API versions

---

### 9-16: Additional Wizards

**9. ScalingWizard 📈**
- Load prediction
- Capacity planning
- Auto-scaling configuration
- Database sharding strategies

**10. ObservabilityWizard 📊**
- Logging strategies
- Metrics collection
- Distributed tracing
- Alerting rules

**11. CICDWizard 🚀**
- Pipeline optimization
- Deployment strategies
- Rollback procedures
- Environment management

**12. DocumentationWizard 📝**
- API documentation generation
- Code comment quality
- README generation
- Changelog maintenance

**13. ComplianceWizard ⚖️**
- GDPR compliance
- SOC 2 requirements
- PCI DSS validation
- Data privacy checks

**14. MigrationWizard 🔄**
- Database migrations
- API versioning
- Feature flags
- Zero-downtime deployments

**15. MonitoringWizard 👁️**
- Health checks
- Error rates
- Performance metrics
- SLA monitoring

**16. LocalizationWizard 🌍**
- i18n best practices
- Translation management
- Date/time formatting
- Currency handling

*See [WIZARDS.md](WIZARDS.md) for complete reference.*

---

## Common Workflows

### Workflow 1: Pre-Commit Check

Before committing code:

```bash
# 1. Run security audit
Coach: Security Audit

# 2. Check performance
Coach: Performance Profile

# 3. Generate tests (if missing)
Coach: Generate Tests

# 4. Commit
git add .
git commit -m "Add feature X"
```

### Workflow 2: Debugging Production Issue

When investigating a production bug:

```bash
# 1. Paste stack trace
Coach: Debug Function
[Paste error]

# 2. DebuggingWizard analyzes root cause

# 3. Apply fix

# 4. Generate regression test
Coach: Generate Tests

# 5. Run multi-wizard review
Coach: Multi-Wizard Review > Production Incident
```

### Workflow 3: New API Endpoint

When creating a new API:

```bash
# 1. Design API
Coach: Generate API Spec

# 2. Multi-wizard review
Coach: Multi-Wizard Review > New API Endpoint

# This automatically runs:
- APIWizard (design)
- SecurityWizard (authentication)
- PerformanceWizard (rate limiting)
- TestingWizard (test cases)
- DatabaseWizard (queries)

# 3. Implement with guidance

# 4. Final check
Coach: Analyze File
```

### Workflow 4: Code Review

When reviewing code:

```bash
# 1. Open PR file

# 2. Run all relevant wizards
Coach: Multi-Wizard Review > Code Review

# 3. Review findings

# 4. Add comments with Coach insights
```

---

## Advanced Features

### Multi-Wizard Collaboration

For complex scenarios, use multi-wizard reviews:

**VS Code**: `Ctrl+Shift+P` → "Coach: Start Multi-Wizard Review"

**JetBrains**: Right-click → **Coach → Multi-Wizard Review**

**Scenarios**:
- `new_api_endpoint` - API + Security + Performance + Database
- `database_migration` - Database + Migration + Monitoring
- `production_incident` - Debugging + Observability + Monitoring
- `new_feature_launch` - All 16 wizards
- `performance_issue` - Performance + Database + Scaling
- `compliance_audit` - Compliance + Security + Documentation
- `global_expansion` - Localization + Scaling + Database

**Example**:

```bash
# Select: new_feature_launch
# Files: src/api/orders.py, src/models/order.py

# Coach orchestrates:
1. APIWizard reviews API design
2. SecurityWizard checks authentication
3. PerformanceWizard analyzes scalability
4. DatabaseWizard reviews queries
5. TestingWizard generates tests
6. ObservabilityWizard adds logging
7. DocumentationWizard creates docs
... (all 16 wizards contribute)

# Result: Comprehensive analysis with consensus and disagreements
```

### Custom Wizards

Build your own wizards with LangChain! See [CUSTOM_WIZARDS.md](CUSTOM_WIZARDS.md).

```python
from coach.base_wizard import BaseWizard
from langchain.chains import LLMChain

class MyCustomWizard(BaseWizard):
    name = "MyWizard"
    expertise = "Custom analysis"

    def analyze(self, code, context):
        # Your LangChain logic
        return result
```

### Caching

Results are cached for 5 minutes (configurable):

```json
// VS Code settings.json
{
  "coach.enableCache": true,
  "coach.cacheTTL": 300
}
```

**Benefits**:
- Instant repeated analysis
- Reduced API calls (if using cloud models)
- Faster workflows

### Offline Mode

Coach works fully offline with local models:

```bash
# Install local model (Ollama)
ollama pull codellama

# Configure Coach
export COACH_MODEL=ollama/codellama
```

---

## Best Practices

### 1. Use Auto-Triggers

Enable auto-analysis on file save:

```json
{
  "coach.autoTriggers.onFileSave": true,
  "coach.autoTriggers.wizards": ["SecurityWizard", "PerformanceWizard"]
}
```

### 2. Review Before Applying Fixes

Always review quick fixes before applying - understand *why* the change is needed.

### 3. Run Multi-Wizard for Complex Changes

For significant features:
- New APIs: `new_api_endpoint`
- Database changes: `database_migration`
- Performance issues: `performance_issue`

### 4. Keep Coach Updated

```bash
# Update LSP server
cd coach
git pull
pip install --upgrade -r requirements.txt

# Update extension/plugin
# VS Code: Extensions → Coach → Update
# JetBrains: Settings → Plugins → Coach → Update
```

### 5. Monitor Level 4 Predictions

Pay attention to timeline predictions:
- **< 30 days**: Act immediately
- **30-60 days**: Plan fix in next sprint
- **60-90 days**: Add to backlog

### 6. Use Wizard-Specific Commands

Instead of generic "Analyze File", use specific wizards for targeted analysis:
- Security review? Use "Security Audit"
- Slow code? Use "Performance Profile"
- UI work? Use "Accessibility Check"

### 7. Integrate into CI/CD

Add Coach to your CI pipeline:

```yaml
# .github/workflows/coach.yml
- name: Coach Security Audit
  run: coach audit --wizard SecurityWizard --fail-on-high

- name: Coach Performance Check
  run: coach analyze --wizard PerformanceWizard --threshold=medium
```

---

## Keyboard Shortcuts

### VS Code

| Command | Shortcut |
|---------|----------|
| Analyze File | `Ctrl+Shift+P` → Coach: Analyze File |
| Security Audit | `Ctrl+Shift+P` → Coach: Security Audit |
| Quick Fix | `Ctrl+.` (on diagnostic) |
| Show Panel | `Ctrl+Shift+P` → Coach: Show Panel |

### JetBrains

| Command | Shortcut |
|---------|----------|
| Analyze File | `Ctrl+Alt+C` |
| Quick Fix | `Alt+Enter` (on inspection) |
| Show Tool Window | `Alt+9` |
| Security Audit | Right-click → Coach → Security Audit |

---

## Next Steps

- **[Wizards Reference](WIZARDS.md)** - Complete documentation for all 16 wizards
- **[Custom Wizards](CUSTOM_WIZARDS.md)** - Build your own LangChain wizards
- **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Questions?** Join [Coach Discord](https://discord.gg/coach-alpha) or email support@deepstudyai.com

**Built with** ❤️ **using LangChain**
