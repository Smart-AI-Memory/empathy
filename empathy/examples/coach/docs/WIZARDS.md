# Complete Wizard Reference

Detailed documentation for all 16 Coach wizards.

**Built on LangChain** - Each wizard is a specialized LangChain agent with domain expertise.

---

## Table of Contents

- [Wizard Architecture](#wizard-architecture)
- [Primary Wizards](#primary-wizards)
  - [1. SecurityWizard](#1-securitywizard-)
  - [2. PerformanceWizard](#2-performancewizard-)
  - [3. AccessibilityWizard](#3-accessibilitywizard-)
  - [4. DebuggingWizard](#4-debuggingwizard-)
  - [5. TestingWizard](#5-testingwizard-)
  - [6. RefactoringWizard](#6-refactoringwizard-)
- [Specialized Wizards](#specialized-wizards)
  - [7. DatabaseWizard](#7-databasewizard-)
  - [8. APIWizard](#8-apiwizard-)
  - [9. ScalingWizard](#9-scalingwizard-)
  - [10. ObservabilityWizard](#10-observabilitywizard-)
  - [11. CICDWizard](#11-cicdwizard-)
  - [12. DocumentationWizard](#12-documentationwizard-)
  - [13. ComplianceWizard](#13-compliancewizard-)
  - [14. MigrationWizard](#14-migrationwizard-)
  - [15. MonitoringWizard](#15-monitoringwizard-)
  - [16. LocalizationWizard](#16-localizationwizard-)
- [Wizard Collaboration](#wizard-collaboration)
- [Wizard API](#wizard-api)

---

## Wizard Architecture

Each wizard is a specialized LangChain agent with:

```python
from langchain.agents import AgentExecutor
from langchain.chains import LLMChain
from coach.base_wizard import BaseWizard

class ExampleWizard(BaseWizard):
    name = "ExampleWizard"
    expertise = "Domain-specific expertise"

    # LangChain tools available to this wizard
    tools = [
        CodeAnalysisTool(),
        PatternDetectionTool(),
        RecommendationTool()
    ]

    # LangChain prompt template
    prompt_template = PromptTemplate(...)

    # Analysis logic using LangChain
    def analyze(self, code, context):
        chain = LLMChain(llm=self.llm, prompt=self.prompt_template)
        result = chain.run(code=code, context=context)
        return self.parse_result(result)
```

### Common Capabilities

All wizards support:
- **Level 4 Predictions**: 30-90 day timeline forecasts
- **Code Examples**: Working code snippets with explanations
- **Collaboration**: Consult other wizards for complex issues
- **Caching**: 5-minute TTL for repeated analyses
- **Confidence Scoring**: 0.0-1.0 confidence in recommendations

---

## Primary Wizards

### 1. SecurityWizard 🛡️

**Expertise**: Security vulnerabilities, OWASP Top 10, secure coding practices

**Powered by**: LangChain with security-focused prompt engineering and specialized tools

#### Detection Categories

##### 1.1 Injection Vulnerabilities

**SQL Injection**:
```python
# VULNERABLE
user_id = request.GET['id']
query = f"SELECT * FROM users WHERE id={user_id}"
cursor.execute(query)

# SECURE (SecurityWizard recommendation)
user_id = request.GET['id']
query = "SELECT * FROM users WHERE id=?"
cursor.execute(query, (user_id,))
```

**Command Injection**:
```python
# VULNERABLE
filename = request.GET['file']
os.system(f"cat {filename}")

# SECURE
filename = request.GET['file']
# Validate filename
if not re.match(r'^[a-zA-Z0-9_.-]+$', filename):
    raise ValueError("Invalid filename")
subprocess.run(['cat', filename], check=True)
```

**LDAP Injection**, **XPath Injection**, **Template Injection** - Similar detection and fixes

##### 1.2 Cross-Site Scripting (XSS)

**Stored XSS**:
```javascript
// VULNERABLE
element.innerHTML = userComment;

// SECURE
element.textContent = userComment;
// Or use DOMPurify
element.innerHTML = DOMPurify.sanitize(userComment);
```

**Reflected XSS**:
```javascript
// VULNERABLE
const name = new URLSearchParams(window.location.search).get('name');
document.write(`Hello ${name}`);

// SECURE
const name = new URLSearchParams(window.location.search).get('name');
const escaped = document.createTextNode(`Hello ${name}`);
document.body.appendChild(escaped);
```

**DOM XSS** - Detection in client-side JavaScript code

##### 1.3 Authentication & Authorization

**Broken Authentication**:
```python
# VULNERABLE
def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:  # Plain text!
        return user

# SECURE
from werkzeug.security import check_password_hash

def login(username, password):
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password_hash, password):
        return user
```

**Missing Authorization**:
```python
# VULNERABLE
@app.route('/admin/users/<int:user_id>')
def admin_edit_user(user_id):
    user = User.query.get(user_id)
    return render_template('edit.html', user=user)

# SECURE
@app.route('/admin/users/<int:user_id>')
@require_role('admin')  # SecurityWizard suggests adding
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('edit.html', user=user)
```

##### 1.4 Cryptography

**Weak Hashing**:
```python
# VULNERABLE
import hashlib
password_hash = hashlib.md5(password.encode()).hexdigest()

# SECURE
from werkzeug.security import generate_password_hash
password_hash = generate_password_hash(password, method='pbkdf2:sha256')
```

**Weak Encryption**:
```python
# VULNERABLE
from Crypto.Cipher import DES
cipher = DES.new(key, DES.MODE_ECB)

# SECURE
from cryptography.fernet import Fernet
cipher = Fernet(key)
```

##### 1.5 Sensitive Data Exposure

**Hardcoded Secrets**:
```python
# VULNERABLE
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "admin123"

# SECURE
import os
API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')
```

**Logging Sensitive Data**:
```python
# VULNERABLE
logger.info(f"User login: {username}, password: {password}")

# SECURE
logger.info(f"User login: {username}")  # No password!
```

#### Level 4 Predictions

```python
# Your code:
session_timeout = 3600  # 1 hour

# SecurityWizard Level 4 Prediction:
⚠️ Session Timeout Risk (Timeline: 60 days)

Current: 1 hour sessions
Compliance: GDPR requires 15-min timeout for sensitive data

Prediction: At current user growth (1000 users/week):
- Week 4: First GDPR audit concern
- Week 8: Compliance violation risk
- Week 12: Potential €20M fine exposure

Impact:
- Legal/compliance risk
- User data exposure
- Audit failure

Preventive Action (within 30 days):
session_timeout = 900  # 15 minutes
auto_logout_warning = 120  # 2 min warning
```

#### When to Use

- ✅ Before committing authentication/authorization code
- ✅ When handling user input
- ✅ Before production deployment
- ✅ During code review
- ✅ After security incidents
- ✅ Monthly security audits

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Security Audit"
**JetBrains**: Right-click → **Coach → Security Audit**
**CLI**: `coach analyze --wizard SecurityWizard <file>`

---

### 2. PerformanceWizard ⚡

**Expertise**: Performance optimization, scalability, resource management

**Powered by**: LangChain with performance profiling tools and algorithmic analysis

#### Detection Categories

##### 2.1 Database Performance

**N+1 Queries**:
```python
# VULNERABLE (N+1)
for user in User.query.all():  # 1 query
    orders = user.orders.all()  # N queries (one per user)
    print(f"{user.name}: {len(orders)} orders")

# OPTIMIZED
users = User.query.options(
    joinedload(User.orders)
).all()  # 1 query with JOIN
for user in users:
    print(f"{user.name}: {len(user.orders)} orders")
```

**Missing Indexes**:
```sql
-- SLOW (no index)
SELECT * FROM orders WHERE customer_id = 123;

-- PerformanceWizard suggests:
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Performance: 2.5s → 15ms (167x faster)
```

**Inefficient Queries**:
```sql
-- SLOW
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- OPTIMIZED
-- Add functional index:
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
-- Or store lowercase in separate column
```

##### 2.2 Algorithmic Complexity

**O(n²) Loops**:
```python
# SLOW - O(n²)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates

# OPTIMIZED - O(n)
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

**Inefficient Data Structures**:
```python
# SLOW - O(n) lookup
users = []  # List
for order in orders:
    if order.user_id in [u.id for u in users]:  # O(n) each time!
        process(order)

# OPTIMIZED - O(1) lookup
user_ids = {u.id for u in users}  # Set
for order in orders:
    if order.user_id in user_ids:  # O(1) lookup
        process(order)
```

##### 2.3 Memory Management

**Memory Leaks**:
```javascript
// VULNERABLE
class DataFetcher {
  constructor() {
    this.cache = [];
    setInterval(() => {
      this.cache.push(fetchData());  // Grows forever!
    }, 1000);
  }
}

// SECURE
class DataFetcher {
  constructor() {
    this.cache = [];
    setInterval(() => {
      this.cache.push(fetchData());
      if (this.cache.length > 100) {
        this.cache.shift();  // Remove oldest
      }
    }, 1000);
  }
}
```

**Large Object Creation**:
```python
# SLOW
def process_file(filename):
    content = open(filename).read()  # Loads entire file!
    for line in content.split('\n'):
        process(line)

# OPTIMIZED
def process_file(filename):
    with open(filename) as f:
        for line in f:  # Streams line by line
            process(line)
```

##### 2.4 Blocking Operations

**Synchronous I/O**:
```javascript
// BLOCKING
const fs = require('fs');
const data = fs.readFileSync('large-file.txt');  // Blocks event loop!
process(data);

// NON-BLOCKING
const fs = require('fs').promises;
const data = await fs.readFile('large-file.txt');
process(data);
```

**CPU-Intensive Tasks**:
```python
# BLOCKS EVENT LOOP
def compute_heavy_task(data):
    result = complex_calculation(data)  # Takes 5 seconds
    return result

# USE WORKER THREAD
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=4)

async def compute_heavy_task(data):
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, complex_calculation, data)
    return result
```

#### Level 4 Predictions

**Example 1: Connection Pool Saturation**
```python
# Your code:
pool_size = 10
max_overflow = 5

# PerformanceWizard Level 4 Prediction:
⚠️ Connection Pool Saturation (Timeline: 45 days)

Current Capacity:
- Pool size: 10
- Max overflow: 5
- Total capacity: 15 connections

Traffic Analysis:
- Current: 1000 req/day
- Growth: 5000 req/day per week
- Projected (45 days): 31,000 req/day

Prediction:
- Day 30: 50% pool utilization → Occasional slow queries
- Day 40: 90% pool utilization → Frequent timeouts
- Day 45: 100% pool saturation → Service outage

Impact:
- 503 Service Unavailable errors
- Request queue backlog
- Cascade failures to dependent services

Preventive Action (within 30 days):
pool_size = 50
max_overflow = 20
pool_timeout = 30  # seconds
pool_recycle = 3600  # 1 hour
```

**Example 2: Cache Miss Ratio**
```python
# Your code:
@cache(ttl=3600)  # 1 hour TTL
def get_user_recommendations(user_id):
    return expensive_ml_computation(user_id)

# PerformanceWizard Level 4 Prediction:
⚠️ Cache Inefficiency (Timeline: 30 days)

Current Metrics:
- Cache hit rate: 45% (target: 80%+)
- TTL: 1 hour
- Cache eviction: LRU

User Pattern Analysis:
- Peak hours: 9am-11am, 7pm-9pm (80% of traffic)
- Recommendation updates: Every 12 hours
- User overlap: 70% return users

Prediction:
- Current: 55% cache misses = 550ms avg latency
- Day 15: Traffic doubles → 60% cache misses → 800ms latency
- Day 30: User complaints, performance degradation

Recommended Strategy:
1. Increase TTL to 12 hours (matches update cycle)
2. Pre-warm cache for top 10% users (70% coverage)
3. Add cache stampede protection

Expected Improvement:
- Cache hit rate: 45% → 85%
- Avg latency: 550ms → 120ms (4.6x faster)
- Infrastructure cost: -40% (fewer computations)
```

#### When to Use

- ✅ Before production deployment
- ✅ When experiencing slow response times
- ✅ During load testing
- ✅ After adding new features
- ✅ Monthly performance reviews
- ✅ When scaling traffic

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Performance Profile"
**JetBrains**: Right-click → **Coach → Performance Profile**
**CLI**: `coach analyze --wizard PerformanceWizard <file>`

---

### 3. AccessibilityWizard ♿

**Expertise**: WCAG 2.1 AA/AAA compliance, screen readers, keyboard navigation, inclusive design

**Powered by**: LangChain with WCAG rule engine and accessibility testing tools

#### WCAG 2.1 Coverage

##### 3.1 Perceivable (Principle 1)

**1.1.1 Non-text Content (Level A)**
```html
<!-- VIOLATION -->
<img src="chart.png">

<!-- COMPLIANT -->
<img src="chart.png" alt="Sales revenue chart showing 25% growth in Q4">
```

**1.3.1 Info and Relationships (Level A)**
```html
<!-- VIOLATION -->
<div onclick="submit()">Submit</div>

<!-- COMPLIANT -->
<button type="submit">Submit</button>
```

**1.4.3 Contrast (Minimum) (Level AA)**
```css
/* VIOLATION - 2.5:1 contrast */
.text {
  color: #777;
  background: #fff;
}

/* COMPLIANT - 4.5:1 contrast */
.text {
  color: #595959;
  background: #fff;
}
```

**1.4.11 Non-text Contrast (Level AA)**
```css
/* VIOLATION - 2:1 contrast */
.button {
  border: 1px solid #ddd;
  background: #fff;
}

/* COMPLIANT - 3:1 contrast */
.button {
  border: 2px solid #767676;
  background: #fff;
}
```

##### 3.2 Operable (Principle 2)

**2.1.1 Keyboard (Level A)**
```html
<!-- VIOLATION -->
<div onclick="handleClick()">Click me</div>

<!-- COMPLIANT -->
<button onclick="handleClick()" onkeypress="handleKeyPress(event)">
  Click me
</button>
```

**2.4.3 Focus Order (Level A)**
```html
<!-- VIOLATION - Confusing tab order -->
<button tabindex="3">Third</button>
<button tabindex="1">First</button>
<button tabindex="2">Second</button>

<!-- COMPLIANT - Natural tab order -->
<button>First</button>
<button>Second</button>
<button>Third</button>
```

**2.4.7 Focus Visible (Level AA)**
```css
/* VIOLATION */
button:focus {
  outline: none;  /* Removes focus indicator! */
}

/* COMPLIANT */
button:focus {
  outline: 2px solid #0066cc;
  outline-offset: 2px;
}
```

##### 3.3 Understandable (Principle 3)

**3.3.2 Labels or Instructions (Level A)**
```html
<!-- VIOLATION -->
<input type="text" placeholder="Enter email">

<!-- COMPLIANT -->
<label for="email">Email address</label>
<input type="text" id="email" placeholder="e.g., user@example.com">
```

**3.3.3 Error Suggestion (Level AA)**
```html
<!-- VIOLATION -->
<div class="error">Invalid input</div>

<!-- COMPLIANT -->
<div class="error" role="alert">
  Invalid email format. Please use format: user@example.com
</div>
```

##### 3.4 Robust (Principle 4)

**4.1.2 Name, Role, Value (Level A)**
```html
<!-- VIOLATION -->
<div onclick="toggleMenu()">Menu</div>

<!-- COMPLIANT -->
<button
  aria-label="Menu"
  aria-expanded="false"
  aria-controls="main-menu"
  onclick="toggleMenu()">
  Menu
</button>
```

#### Comprehensive Checks

##### Screen Reader Support
```html
<!-- VIOLATION -->
<div class="custom-checkbox" onclick="toggle()"></div>

<!-- COMPLIANT -->
<input
  type="checkbox"
  id="agree"
  aria-describedby="agree-description">
<label for="agree">I agree to the terms</label>
<div id="agree-description">
  By checking this box, you agree to our Terms of Service and Privacy Policy
</div>
```

##### Keyboard Navigation
```javascript
// VIOLATION - Mouse-only interaction
element.onclick = () => handleAction();

// COMPLIANT - Keyboard accessible
element.onclick = () => handleAction();
element.onkeypress = (e) => {
  if (e.key === 'Enter' || e.key === ' ') {
    e.preventDefault();
    handleAction();
  }
};
// Or better: use <button> which handles this automatically
```

##### Color Blindness
```css
/* VIOLATION - Color only to convey information */
.success { color: green; }
.error { color: red; }

/* COMPLIANT - Color + icon + text */
.success::before { content: '✓ '; }
.error::before { content: '✗ '; }
.success { color: green; }
.error { color: red; }
```

##### Form Accessibility
```html
<!-- VIOLATION -->
<form>
  <input type="text" required>
  <input type="email">
  <button>Submit</button>
</form>

<!-- COMPLIANT -->
<form>
  <label for="name">
    Name <span aria-label="required">*</span>
  </label>
  <input
    type="text"
    id="name"
    required
    aria-required="true"
    aria-invalid="false">

  <label for="email">Email</label>
  <input
    type="email"
    id="email"
    aria-describedby="email-hint">
  <div id="email-hint" class="hint">
    We'll never share your email
  </div>

  <button type="submit">Submit form</button>
</form>
```

#### Level 4 Predictions

```html
<!-- Your code: -->
<div class="modal" style="display: none;">
  <h2>Important Notice</h2>
  <p>Content here</p>
  <button onclick="closeModal()">OK</button>
</div>

<!-- AccessibilityWizard Level 4 Prediction: -->
⚠️ Accessibility Debt Accumulation (Timeline: 60 days)

Current Issues:
- Modal not keyboard accessible (no focus trap)
- No ARIA labels for screen readers
- No focus management

User Impact Analysis:
- Screen reader users: 15% of user base
- Keyboard-only users: 8% of user base
- Total affected: ~23% of users

Prediction (based on similar patterns in codebase):
- Week 2: 5 more non-accessible modals added
- Week 4: 12 modals total, 0% accessible
- Week 8: First accessibility complaint
- Week 10: Compliance review failure
- Week 12: Potential lawsuit risk (ADA compliance)

Preventive Action (within 14 days):
1. Fix this modal (see recommendation below)
2. Create accessible modal component
3. Audit all 12 modals
4. Add accessibility CI check

Recommended Fix:
<div
  class="modal"
  role="dialog"
  aria-labelledby="modal-title"
  aria-modal="true"
  style="display: none;">
  <h2 id="modal-title">Important Notice</h2>
  <p>Content here</p>
  <button onclick="closeModal()" aria-label="Close dialog">OK</button>
</div>

<script>
// Add focus trap
function openModal() {
  modal.style.display = 'block';
  modal.querySelector('button').focus();
  document.addEventListener('keydown', handleEscape);
}
function handleEscape(e) {
  if (e.key === 'Escape') closeModal();
}
</script>
```

#### When to Use

- ✅ Before launching public features
- ✅ During UI/UX development
- ✅ When adding forms or interactive elements
- ✅ Before compliance audits
- ✅ When receiving accessibility complaints
- ✅ Quarterly accessibility reviews

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Accessibility Check"
**JetBrains**: Right-click → **Coach → Accessibility Check**
**CLI**: `coach analyze --wizard AccessibilityWizard <file>`

---

### 4. DebuggingWizard 🐛

**Expertise**: Root cause analysis, stack trace interpretation, debugging strategies, error pattern recognition

**Powered by**: LangChain with error analysis tools and debugging knowledge base

#### Capabilities

##### 4.1 Stack Trace Analysis

**Example Input**:
```python
Traceback (most recent call last):
  File "app.py", line 145, in process_payment
    charge = stripe.Charge.create(
  File "/lib/stripe/resource.py", line 52, in create
    response = requestor.request('post', url, params)
  File "/lib/stripe/http_client.py", line 89, in request
    rbody, rcode, rheaders = self._make_request(method, url, headers, post_data)
stripe.error.CardError: Your card was declined.
```

**DebuggingWizard Analysis**:
```
🐛 Root Cause Analysis

Primary Issue: Payment card declined
Error Type: stripe.error.CardError (Expected business exception)

Root Cause: Missing error handling for payment failures

Why This Happened:
1. No try/except around Stripe API call
2. Card decline treated as unexpected error (should be expected)
3. No user-friendly error message
4. No retry mechanism
5. No payment failure logging

Impact:
- Poor user experience (stack trace shown to user?)
- Lost sales (no retry option)
- No payment failure metrics
- Customer support burden

Recommended Fix:

import stripe
from stripe.error import CardError, InvalidRequestError, AuthenticationError

def process_payment(amount, token):
    try:
        charge = stripe.Charge.create(
            amount=amount,
            currency='usd',
            source=token,
            idempotency_key=generate_idempotency_key()
        )
        log_payment_success(charge)
        return {'success': True, 'charge_id': charge.id}

    except CardError as e:
        # Expected: Card declined, insufficient funds, etc.
        log_payment_failure(e, type='card_error')
        return {
            'success': False,
            'error': 'payment_declined',
            'message': 'Your card was declined. Please try a different payment method.',
            'decline_code': e.decline_code
        }

    except InvalidRequestError as e:
        # Unexpected: Bad parameters
        log_payment_error(e, type='invalid_request')
        return {
            'success': False,
            'error': 'invalid_request',
            'message': 'Payment processing error. Please contact support.'
        }

    except AuthenticationError as e:
        # Critical: API key issue
        alert_ops_team(e)
        log_critical_error(e)
        return {
            'success': False,
            'error': 'system_error',
            'message': 'Payment system temporarily unavailable. Please try again later.'
        }

Related Patterns:
- Similar missing error handling in process_refund() (line 189)
- Similar in update_subscription() (line 234)

Preventive Measures:
1. Add integration tests for payment failures
2. Create PaymentService class with built-in error handling
3. Add monitoring for payment failure rates
4. Set up alerts for AuthenticationError
```

##### 4.2 Error Pattern Recognition

**Input**:
```javascript
TypeError: Cannot read property 'name' of undefined
  at UserProfile.render (UserProfile.jsx:42)
  at React.Component.render
```

**DebuggingWizard Analysis**:
```
🐛 Error Pattern: Null/Undefined Access

Common Pattern: Accessing property on undefined object
Frequency: This pattern appears 15 times in your codebase

Root Cause: Missing null check before property access

Code at UserProfile.jsx:42:
const name = user.name;  // user is undefined!

Why user is undefined:
1. Component rendered before data loaded
2. No loading state
3. No default props
4. API call may have failed silently

Recommended Fixes:

Option 1: Optional Chaining (Modern JavaScript)
const name = user?.name ?? 'Guest';

Option 2: Default Props
UserProfile.defaultProps = {
  user: { name: 'Guest', email: '' }
};

Option 3: Loading State
function UserProfile({ user }) {
  if (!user) {
    return <LoadingSpinner />;
  }
  return <div>{user.name}</div>;
}

Option 4: PropTypes Validation (Development)
import PropTypes from 'prop-types';
UserProfile.propTypes = {
  user: PropTypes.shape({
    name: PropTypes.string.isRequired,
    email: PropTypes.string.isRequired
  }).isRequired
};

Recommended: Combine Option 1 + Option 3 + Option 4

Similar Issues in Your Codebase:
- OrderSummary.jsx:28 (order.items undefined)
- ProductCard.jsx:15 (product.price undefined)
- ... (12 more occurrences)

Preventive: Enable TypeScript or add PropTypes to all components
```

##### 4.3 Performance Debugging

**Input**: "API endpoint taking 5 seconds to respond"

**DebuggingWizard Analysis**:
```
🐛 Performance Debugging Strategy

Systematic Approach:

1. Measure & Identify Bottleneck
   Add timing logs:

   import time

   def slow_endpoint():
       t1 = time.time()
       users = get_users()  # Measure this
       print(f"get_users: {time.time() - t1:.2f}s")

       t2 = time.time()
       orders = get_orders(users)  # And this
       print(f"get_orders: {time.time() - t2:.2f}s")

       t3 = time.time()
       result = process_data(users, orders)  # And this
       print(f"process_data: {time.time() - t3:.2f}s")

       return result

2. Common Culprits (in order of likelihood):
   □ N+1 database queries (90% of slow endpoints)
   □ Missing database indexes
   □ Large result sets (no pagination)
   □ Synchronous external API calls
   □ Heavy computation in request thread

3. Quick Wins:
   - Add database query logging: See what queries run
   - Check query count: Should be < 10 per request
   - Add SELECT ONLY needed columns (not SELECT *)
   - Add LIMIT clauses

4. Tools to Use:
   - Django Debug Toolbar (Python/Django)
   - django-silk (Query profiling)
   - New Relic / DataDog (APM)
   - PostgreSQL EXPLAIN ANALYZE

5. Likely Fix (based on similar issues):
   Hypothesis: N+1 queries in get_orders()

   # Current (slow):
   for user in users:
       orders = Order.objects.filter(user_id=user.id)

   # Fixed (fast):
   user_ids = [u.id for u in users]
   orders = Order.objects.filter(user_id__in=user_ids).select_related('product')

Next Steps:
1. Add timing logs (5 minutes)
2. Identify bottleneck (2 minutes)
3. Apply appropriate fix (10 minutes)
4. Verify improvement (2 minutes)

I can help debug each step - just share the timing logs!
```

##### 4.4 Intermittent Bug Debugging

**Input**: "Bug happens randomly, can't reproduce"

**Debug Strategy**:
```
🐛 Intermittent Bug Debugging Strategy

Red Flags for Intermittent Bugs:
- "Works on my machine"
- "Happens only sometimes"
- "Can't reproduce in dev"
- "Only in production"

Common Causes (by frequency):
1. Race conditions (40%)
2. Environment differences (25%)
3. Data-dependent bugs (20%)
4. Timezone/locale issues (10%)
5. Resource constraints (5%)

Systematic Debugging:

Step 1: Gather Data
□ When does it happen? (time of day, day of week)
□ Who experiences it? (all users, specific users, admins)
□ Where? (production, staging, specific servers)
□ What's different when it fails vs. succeeds?

Step 2: Add Logging
# Add correlation ID to track requests
import uuid
request_id = str(uuid.uuid4())
logger.info(f"[{request_id}] Starting process", extra={'request_id': request_id})

# Log key decision points
logger.info(f"[{request_id}] user.role={user.role}, is_admin={user.is_admin}")

# Log race condition suspects
logger.info(f"[{request_id}] Lock acquired at {time.time()}")

Step 3: Reproduce Conditions
- Match production data volume
- Match production traffic patterns
- Match production environment (Python version, dependencies, OS)
- Use production database dump

Step 4: Common Fixes by Type

Race Condition:
# Before (race condition)
if not lock.is_locked():
    lock.acquire()  # Another thread might acquire here!
    critical_section()
    lock.release()

# After (atomic)
with lock:
    critical_section()

Environment Difference:
# Add environment validation
assert sys.version_info >= (3, 12), f"Requires Python 3.12+, got {sys.version}"
assert DATABASE_URL, "DATABASE_URL must be set"

Data-Dependent:
# Add input validation
def process(value):
    assert value is not None, "value cannot be None"
    assert value >= 0, f"value must be >= 0, got {value}"
    # ... rest of function

Next Steps:
1. Share answers to "Gather Data" questions
2. Add logging with correlation IDs
3. Collect logs from 10+ occurrences
4. Analyze patterns in logs
5. Form hypothesis
6. Test hypothesis

I'll help analyze logs once you collect them!
```

#### When to Use

- ✅ When encountering errors/exceptions
- ✅ When behavior is unexpected
- ✅ When bugs are intermittent
- ✅ During incident response
- ✅ When stuck debugging
- ✅ For post-mortem analysis

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Debug Function"
**JetBrains**: Right-click → **Coach → Debug Analysis**
**CLI**: `coach debug --error "<error_message>"`

---

### 5. TestingWizard 🧪

**Expertise**: Test generation, coverage analysis, test strategy, TDD/BDD practices

**Powered by**: LangChain with code understanding and test pattern generation

#### Capabilities

##### 5.1 Unit Test Generation

**Input Function**:
```python
def calculate_discount(price, user_tier, coupon=None, quantity=1):
    """Calculate final price with discounts"""
    if price < 0:
        raise ValueError("Price cannot be negative")

    # Tier discounts
    tier_discount = {
        'premium': 0.20,
        'gold': 0.10,
        'silver': 0.05
    }.get(user_tier, 0.0)

    # Coupon discount
    coupon_discount = 0.0
    if coupon and coupon.is_valid():
        coupon_discount = coupon.value

    # Quantity discount (5% off for 10+ items)
    quantity_discount = 0.05 if quantity >= 10 else 0.0

    # Total discount capped at 50%
    total_discount = min(tier_discount + coupon_discount + quantity_discount, 0.50)

    return price * quantity * (1 - total_discount)
```

**TestingWizard Generated Tests**:
```python
import pytest
from decimal import Decimal
from unittest.mock import Mock

class TestCalculateDiscount:
    """Test suite for calculate_discount function

    Coverage:
    - Happy paths (basic functionality)
    - Edge cases (boundary conditions)
    - Error cases (invalid inputs)
    - Business logic (discount rules)
    """

    # Happy Path Tests

    def test_premium_user_basic_discount(self):
        """Premium user gets 20% discount"""
        result = calculate_discount(100, 'premium')
        assert result == 80.0

    def test_gold_user_basic_discount(self):
        """Gold user gets 10% discount"""
        result = calculate_discount(100, 'gold')
        assert result == 90.0

    def test_silver_user_basic_discount(self):
        """Silver user gets 5% discount"""
        result = calculate_discount(100, 'silver')
        assert result == 95.0

    def test_unknown_tier_no_discount(self):
        """Unknown tier gets 0% discount"""
        result = calculate_discount(100, 'bronze')
        assert result == 100.0

    # Coupon Tests

    def test_premium_with_valid_coupon(self):
        """Premium (20%) + coupon (10%) = 30% discount"""
        coupon = Mock()
        coupon.is_valid.return_value = True
        coupon.value = 0.10

        result = calculate_discount(100, 'premium', coupon=coupon)
        assert result == 70.0
        coupon.is_valid.assert_called_once()

    def test_premium_with_invalid_coupon(self):
        """Invalid coupon is ignored"""
        coupon = Mock()
        coupon.is_valid.return_value = False

        result = calculate_discount(100, 'premium', coupon=coupon)
        assert result == 80.0  # Only tier discount

    # Quantity Discount Tests

    def test_quantity_discount_threshold(self):
        """10+ items get additional 5% discount"""
        result = calculate_discount(10, 'premium', quantity=10)
        # 20% tier + 5% quantity = 25% discount
        # 10 * 10 * 0.75 = 75
        assert result == 75.0

    def test_quantity_discount_below_threshold(self):
        """9 items don't get quantity discount"""
        result = calculate_discount(10, 'premium', quantity=9)
        # Only 20% tier discount
        # 10 * 9 * 0.80 = 72
        assert result == 72.0

    # Discount Cap Tests

    def test_discount_capped_at_50_percent(self):
        """Total discount cannot exceed 50%"""
        coupon = Mock()
        coupon.is_valid.return_value = True
        coupon.value = 0.40  # 40% coupon

        # Premium (20%) + Coupon (40%) + Quantity (5%) = 65%
        # Should be capped at 50%
        result = calculate_discount(100, 'premium', coupon=coupon, quantity=10)
        assert result == 50.0  # 50% discount, not 65%

    # Edge Cases

    def test_zero_price(self):
        """Zero price is valid"""
        result = calculate_discount(0, 'premium')
        assert result == 0.0

    def test_negative_price_raises_error(self):
        """Negative price raises ValueError"""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            calculate_discount(-10, 'premium')

    def test_float_price(self):
        """Float prices work correctly"""
        result = calculate_discount(19.99, 'premium')
        assert abs(result - 15.992) < 0.01  # Allow floating point tolerance

    def test_large_quantity(self):
        """Large quantities work correctly"""
        result = calculate_discount(10, 'premium', quantity=1000)
        assert result == 7500.0  # 25% discount (20% tier + 5% quantity)

    # Missing Tests (Recommendations from TestingWizard)

    @pytest.mark.skip(reason="TODO: Add this test")
    def test_coupon_is_none_vs_not_provided(self):
        """Verify coupon=None behaves same as no coupon parameter

        RECOMMENDATION: Add this test to ensure default parameter behavior
        """
        pass

    @pytest.mark.skip(reason="TODO: Add this test")
    def test_concurrent_coupon_validation(self):
        """Test thread safety of coupon validation

        RECOMMENDATION: If coupons are validated against database,
        test race conditions when same coupon used simultaneously
        """
        pass

    @pytest.mark.skip(reason="TODO: Add this test")
    def test_decimal_precision(self):
        """Test with Decimal type for financial accuracy

        RECOMMENDATION: Use Decimal instead of float for money
        Example: calculate_discount(Decimal('19.99'), 'premium')
        """
        pass

# TestingWizard Analysis:
# ✅ Coverage: 85% (12/14 paths covered)
# ⚠️  Missing: Decimal type handling, edge cases for coupon=None
# 💡 Recommendation: Add property-based testing with Hypothesis
# 🐛 Potential Bug Found: Float precision issue - use Decimal for money!
```

**Property-Based Testing Suggestion**:
```python
from hypothesis import given, strategies as st

@given(
    price=st.floats(min_value=0, max_value=10000),
    user_tier=st.sampled_from(['premium', 'gold', 'silver', 'basic']),
    quantity=st.integers(min_value=1, max_value=1000)
)
def test_discount_never_exceeds_50_percent(price, user_tier, quantity):
    """Property: Discount should never exceed 50% regardless of inputs"""
    result = calculate_discount(price, user_tier, quantity=quantity)
    assert result >= price * quantity * 0.5
```

##### 5.2 Integration Test Generation

**Scenario**: REST API endpoint

**TestingWizard Generated Tests**:
```python
import pytest
from flask import Flask
from app import create_app, db
from models import User, Order

@pytest.fixture
def client():
    """Test client with test database"""
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture
def auth_headers(client):
    """Authenticated user headers"""
    user = User(email='test@example.com', password='password123')
    db.session.add(user)
    db.session.commit()

    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

class TestOrderAPI:
    """Integration tests for Order API endpoints"""

    def test_create_order_success(self, client, auth_headers):
        """POST /api/orders - Create new order"""
        response = client.post('/api/orders',
            headers=auth_headers,
            json={
                'items': [
                    {'product_id': 1, 'quantity': 2},
                    {'product_id': 2, 'quantity': 1}
                ],
                'shipping_address': '123 Main St'
            })

        assert response.status_code == 201
        assert 'order_id' in response.json

        # Verify database
        order = Order.query.get(response.json['order_id'])
        assert order is not None
        assert len(order.items) == 2

    def test_create_order_missing_items(self, client, auth_headers):
        """POST /api/orders - Missing items returns 400"""
        response = client.post('/api/orders',
            headers=auth_headers,
            json={'shipping_address': '123 Main St'})

        assert response.status_code == 400
        assert 'items' in response.json['errors']

    def test_create_order_unauthorized(self, client):
        """POST /api/orders - No auth returns 401"""
        response = client.post('/api/orders',
            json={'items': [], 'shipping_address': '123 Main St'})

        assert response.status_code == 401

    def test_get_order_success(self, client, auth_headers):
        """GET /api/orders/:id - Get order by ID"""
        # Create order first
        create_response = client.post('/api/orders',
            headers=auth_headers,
            json={'items': [{'product_id': 1, 'quantity': 1}]})
        order_id = create_response.json['order_id']

        # Get order
        response = client.get(f'/api/orders/{order_id}',
            headers=auth_headers)

        assert response.status_code == 200
        assert response.json['id'] == order_id

    def test_get_order_not_found(self, client, auth_headers):
        """GET /api/orders/:id - Non-existent order returns 404"""
        response = client.get('/api/orders/99999',
            headers=auth_headers)

        assert response.status_code == 404

    def test_list_orders_pagination(self, client, auth_headers):
        """GET /api/orders - Pagination works correctly"""
        # Create 25 orders
        for i in range(25):
            client.post('/api/orders',
                headers=auth_headers,
                json={'items': [{'product_id': 1, 'quantity': 1}]})

        # Get first page
        response = client.get('/api/orders?page=1&limit=10',
            headers=auth_headers)

        assert response.status_code == 200
        assert len(response.json['orders']) == 10
        assert response.json['total'] == 25
        assert response.json['page'] == 1
        assert response.json['pages'] == 3
```

##### 5.3 Test Coverage Analysis

**TestingWizard Report**:
```
🧪 Test Coverage Analysis

File: payment_processor.py
Current Coverage: 65%

Uncovered Code:

Lines 45-52: Error handling for network timeout
  Recommendation: Add test:
  def test_payment_network_timeout(mock_stripe):
      mock_stripe.Charge.create.side_effect = Timeout()
      result = process_payment(100, 'tok_123')
      assert result['success'] == False
      assert result['error'] == 'timeout'

Lines 78-82: Webhook signature verification
  Recommendation: Add test:
  def test_webhook_invalid_signature():
      payload = '{"event": "charge.succeeded"}'
      invalid_sig = 'invalid_signature'
      with pytest.raises(SignatureVerificationError):
          verify_webhook(payload, invalid_sig)

Lines 110-115: Refund partial amount
  CRITICAL: No tests for refund logic!
  Recommendation: Add comprehensive refund tests

Mutation Testing Results:
- 15 mutations introduced
- 12 caught by tests (80%)
- 3 survived (bugs in test logic!)

Survived Mutations:
1. Line 34: >= changed to > (boundary condition not tested)
2. Line 67: and changed to or (logic error not tested)
3. Line 91: + changed to - (arithmetic error not tested)

Recommendations:
1. Add tests for lines 45-52, 78-82, 110-115
2. Fix boundary condition test (amount >= 100)
3. Add logic tests for line 67
4. Add arithmetic tests for line 91
5. Target: 90% coverage + 100% mutation score
```

#### When to Use

- ✅ After writing new functions
- ✅ When test coverage is low (<80%)
- ✅ Before refactoring
- ✅ During TDD workflow
- ✅ When bugs are found (regression tests)
- ✅ For critical business logic

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Generate Tests"
**JetBrains**: Right-click → **Coach → Generate Tests**
**CLI**: `coach generate-tests <file>`

---

### 6. RefactoringWizard 🔧

**Expertise**: Code quality, maintainability, design patterns, SOLID principles

**Powered by**: LangChain with static analysis and pattern recognition

#### Detection Categories

##### 6.1 Code Smells

**Long Method**:
```python
# BEFORE - 150 lines, cyclomatic complexity: 25
def process_order(order):
    # Validate order
    if not order:
        raise ValueError("Order cannot be None")
    if not order.items:
        raise ValueError("Order must have items")
    # ... 20 more validation lines ...

    # Calculate totals
    subtotal = 0
    for item in order.items:
        subtotal += item.price * item.quantity
    # ... 30 more calculation lines ...

    # Apply discounts
    if order.user.tier == 'premium':
        discount = 0.20
    elif order.user.tier == 'gold':
        discount = 0.10
    # ... 40 more discount lines ...

    # Process payment
    if order.payment_method == 'credit_card':
        # ... 30 lines of credit card processing ...
    elif order.payment_method == 'paypal':
        # ... 30 lines of PayPal processing ...

    # Send notifications
    # ... 20 lines ...

# AFTER - RefactoringWizard recommendation
class OrderProcessor:
    def __init__(self, order):
        self.order = order
        self.validator = OrderValidator()
        self.calculator = PriceCalculator()
        self.payment_processor = PaymentProcessorFactory.create(order.payment_method)
        self.notifier = OrderNotifier()

    def process(self):
        self.validator.validate(self.order)
        total = self.calculator.calculate_total(self.order)
        payment_result = self.payment_processor.process(total)

        if payment_result.success:
            self.notifier.send_confirmation(self.order)
            return OrderResult.success(self.order)
        else:
            self.notifier.send_failure(self.order, payment_result.error)
            return OrderResult.failure(payment_result.error)

# Complexity: 25 → 4
# Lines: 150 → 15
# Testability: Significantly improved
```

**Duplicate Code**:
```python
# BEFORE - Duplicate logic
def get_active_users():
    users = User.query.all()
    active = []
    for user in users:
        if user.is_active and user.email_verified and user.created_at > thirty_days_ago:
            active.append(user)
    return active

def get_premium_users():
    users = User.query.all()
    premium = []
    for user in users:
        if user.tier == 'premium' and user.is_active and user.email_verified:
            premium.append(user)
    return premium

# AFTER - RefactoringWizard recommendation
def get_users_matching(predicate):
    """Generic user filter"""
    return [u for u in User.query.all() if predicate(u)]

def is_active_user(user):
    return (user.is_active and
            user.email_verified and
            user.created_at > thirty_days_ago)

def is_premium_user(user):
    return user.tier == 'premium' and is_active_user(user)

def get_active_users():
    return get_users_matching(is_active_user)

def get_premium_users():
    return get_users_matching(is_premium_user)

# Bonus: Now easy to add more filters!
```

**God Object**:
```python
# BEFORE - UserManager does everything
class UserManager:
    def create_user(self, data): ...
    def authenticate(self, email, password): ...
    def send_welcome_email(self, user): ...
    def calculate_user_discount(self, user): ...
    def generate_user_report(self, user): ...
    def export_user_data(self, user): ...
    def process_user_payment(self, user, amount): ...
    # ... 50 more methods ...

# AFTER - Single Responsibility Principle
class UserRepository:
    def create(self, data): ...
    def find_by_email(self, email): ...
    def update(self, user): ...

class AuthenticationService:
    def authenticate(self, email, password): ...
    def create_session(self, user): ...

class UserNotificationService:
    def send_welcome_email(self, user): ...
    def send_password_reset(self, user): ...

class UserDiscountCalculator:
    def calculate_discount(self, user): ...

class UserReportGenerator:
    def generate_report(self, user): ...
```

##### 6.2 Design Pattern Recommendations

**Strategy Pattern**:
```python
# BEFORE - if/elif chain
def calculate_shipping(order, method):
    if method == 'standard':
        if order.total < 50:
            return 5.99
        else:
            return 0
    elif method == 'express':
        if order.total < 100:
            return 15.99
        else:
            return 9.99
    elif method == 'overnight':
        return 29.99

# AFTER - Strategy pattern
from abc import ABC, abstractmethod

class ShippingStrategy(ABC):
    @abstractmethod
    def calculate_cost(self, order):
        pass

class StandardShipping(ShippingStrategy):
    def calculate_cost(self, order):
        return 0 if order.total >= 50 else 5.99

class ExpressShipping(ShippingStrategy):
    def calculate_cost(self, order):
        return 9.99 if order.total >= 100 else 15.99

class OvernightShipping(ShippingStrategy):
    def calculate_cost(self, order):
        return 29.99

class ShippingCalculator:
    strategies = {
        'standard': StandardShipping(),
        'express': ExpressShipping(),
        'overnight': OvernightShipping()
    }

    def calculate_shipping(self, order, method):
        strategy = self.strategies.get(method)
        if not strategy:
            raise ValueError(f"Unknown shipping method: {method}")
        return strategy.calculate_cost(order)

# Benefits:
# - Easy to add new shipping methods
# - Each strategy independently testable
# - Open/Closed Principle (open for extension, closed for modification)
```

**Factory Pattern**:
```python
# BEFORE - Manual object creation everywhere
if payment_type == 'credit_card':
    processor = CreditCardProcessor(api_key, merchant_id)
elif payment_type == 'paypal':
    processor = PayPalProcessor(client_id, secret)
elif payment_type == 'stripe':
    processor = StripeProcessor(api_key)

# AFTER - Factory pattern
class PaymentProcessorFactory:
    @staticmethod
    def create(payment_type, config):
        processors = {
            'credit_card': lambda: CreditCardProcessor(
                config.CREDIT_CARD_API_KEY,
                config.MERCHANT_ID
            ),
            'paypal': lambda: PayPalProcessor(
                config.PAYPAL_CLIENT_ID,
                config.PAYPAL_SECRET
            ),
            'stripe': lambda: StripeProcessor(
                config.STRIPE_API_KEY
            )
        }

        creator = processors.get(payment_type)
        if not creator:
            raise ValueError(f"Unknown payment type: {payment_type}")

        return creator()

# Usage
processor = PaymentProcessorFactory.create(payment_type, config)
```

##### 6.3 SOLID Principles

**Single Responsibility**:
```python
# VIOLATION
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def save_to_database(self):  # Persistence
        db.save(self)

    def send_welcome_email(self):  # Email sending
        email.send(self.email, "Welcome!")

    def hash_password(self):  # Cryptography
        self.password = bcrypt.hash(self.password)

# COMPLIANT
class User:
    def __init__(self, email, password_hash):
        self.email = email
        self.password_hash = password_hash

class UserRepository:
    def save(self, user):
        db.save(user)

class UserNotifier:
    def send_welcome_email(self, user):
        email.send(user.email, "Welcome!")

class PasswordHasher:
    def hash(self, password):
        return bcrypt.hash(password)
```

**Open/Closed Principle**:
```python
# VIOLATION - Must modify class to add new discount type
class DiscountCalculator:
    def calculate(self, order, discount_type):
        if discount_type == 'percentage':
            return order.total * 0.10
        elif discount_type == 'fixed':
            return 10.0
        elif discount_type == 'bogo':  # Adding this requires modifying class!
            return order.total * 0.50

# COMPLIANT - Open for extension, closed for modification
class Discount(ABC):
    @abstractmethod
    def calculate(self, order):
        pass

class PercentageDiscount(Discount):
    def __init__(self, percentage):
        self.percentage = percentage

    def calculate(self, order):
        return order.total * self.percentage

class FixedDiscount(Discount):
    def __init__(self, amount):
        self.amount = amount

    def calculate(self, order):
        return min(self.amount, order.total)

class BOGODiscount(Discount):  # New discount type - no modification needed!
    def calculate(self, order):
        return order.total * 0.50

# Usage
discount = PercentageDiscount(0.10)
amount = discount.calculate(order)
```

#### Level 4 Predictions

```python
# Your code:
class OrderService:
    def create_order(self, data):
        # ... 200 lines of code ...
        pass

# RefactoringWizard Level 4 Prediction:
⚠️ Technical Debt Accumulation (Timeline: 90 days)

Current State:
- OrderService: 200 lines, cyclomatic complexity: 18
- Similar "God Objects": PaymentService (250 lines), UserService (180 lines)
- Total technical debt: 45 hours (estimated refactoring time)

Code Growth Prediction:
- Current rate: +50 lines/week to OrderService
- Week 4: 400 lines (unmaintainable)
- Week 8: Team velocity -20% (code hard to change)
- Week 12: 600 lines, critical bugs introduced

Impact Timeline:
- Week 2: First "afraid to touch this code" comment
- Week 4: Bug fix takes 2x longer than expected
- Week 6: New feature delayed due to code complexity
- Week 8: Team requests "refactoring sprint"
- Week 12: Production bug due to unintended side effects

Preventive Refactoring (within 14 days):
Effort: 8 hours
Benefit: Prevent 45 hours of future technical debt

Recommended Steps:
1. Extract OrderValidator class (2 hours)
2. Extract PaymentProcessor factory (2 hours)
3. Extract OrderNotifier class (1 hour)
4. Add unit tests for each class (3 hours)
5. Update integration tests (0.5 hours)

Result After Refactoring:
- OrderService: 200 lines → 50 lines
- New classes: 4 (each <100 lines)
- Cyclomatic complexity: 18 → 4
- Test coverage: 60% → 95%
- Future velocity: +30% (easier to change)
```

#### When to Use

- ✅ During code review
- ✅ Before adding new features to complex code
- ✅ When code becomes hard to understand
- ✅ During technical debt sprints
- ✅ When test coverage is low
- ✅ Monthly code quality reviews

#### Commands

**VS Code**: `Ctrl+Shift+P` → "Coach: Refactoring Analysis"
**JetBrains**: Right-click → **Coach → Refactoring Suggestions**
**CLI**: `coach refactor <file>`

---

## Specialized Wizards

### 7. DatabaseWizard 🗄️

**Expertise**: Schema design, query optimization, indexing strategies, migrations, data modeling

**Powered by**: LangChain with database-specific knowledge bases

**Key Capabilities**:
- Schema review and normalization analysis
- Query performance optimization
- Index recommendations
- Migration planning and safety checks
- Data integrity validation
- Sharding strategies

**Example**:
```sql
-- Your query (slow: 5.2 seconds)
SELECT u.*, o.*, p.*
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
LEFT JOIN products p ON o.product_id = p.id
WHERE u.created_at > '2024-01-01'
ORDER BY o.created_at DESC;

-- DatabaseWizard optimization:
-- Step 1: Add indexes
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id, created_at DESC);

-- Step 2: Optimize query
SELECT
    u.id, u.name, u.email,
    o.id AS order_id, o.total, o.created_at AS order_date,
    p.id AS product_id, p.name AS product_name
FROM users u
INNER JOIN orders o ON u.id = o.user_id  -- Changed to INNER JOIN
INNER JOIN products p ON o.product_id = p.id
WHERE u.created_at > '2024-01-01'
ORDER BY o.created_at DESC
LIMIT 1000;  -- Added LIMIT

-- Result: 5.2s → 42ms (124x faster)
```

**Commands**: Right-click → **Coach → Database Analysis**

---

### 8. APIWizard 🌐

**Expertise**: REST/GraphQL design, OpenAPI specs, API versioning, rate limiting

**Powered by**: LangChain with API design patterns and best practices

**Key Capabilities**:
- RESTful API design review
- OpenAPI/Swagger spec generation
- API versioning strategies
- Rate limiting design
- Authentication/authorization patterns
- GraphQL schema optimization

**Example**:
```python
# Before (non-RESTful)
@app.route('/api/user', methods=['GET', 'POST', 'PUT', 'DELETE'])
def user_endpoint():
    if request.method == 'GET':
        return get_user(request.args.get('id'))
    # ...

# After (RESTful, recommended by APIWizard)
@app.route('/api/users', methods=['GET'])
def list_users():
    return jsonify({'users': User.query.all()})

@app.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict()), 200

@app.route('/api/users', methods=['POST'])
@validate_json(UserSchema)
def create_user():
    user = User(**request.json)
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201
```

**Commands**: Right-click → **Coach → API Design Review**

---

### 9. ScalingWizard 📈

**Expertise**: Load prediction, capacity planning, auto-scaling, horizontal/vertical scaling

**Powered by**: LangChain with performance modeling and growth analysis

**Key Capabilities**:
- Traffic growth prediction
- Capacity planning (CPU, memory, database)
- Auto-scaling configuration
- Database sharding strategies
- Cache optimization
- CDN recommendations

**Level 4 Example**:
```python
# Your infrastructure code:
app_instances = 2
db_connections = 100
cache_size = "512MB"

# ScalingWizard Level 4 Prediction:
⚠️ Infrastructure Capacity Exhaustion (Timeline: 60 days)

Current Capacity:
- 2 app instances (4 CPU, 8GB RAM each)
- 100 DB connections
- 512MB Redis cache

Traffic Analysis:
- Current: 10K req/day
- Growth: 50% month-over-month
- Projected (60 days): 90K req/day

Bottleneck Prediction:
- Day 30: App CPU at 80% → slow response times
- Day 45: DB connections saturated → connection pool errors
- Day 60: Redis cache full → high latency

Recommended Scaling Plan:
Week 2: Increase to 4 app instances
Week 4: Upgrade DB connection pool to 200
Week 6: Increase Redis to 2GB
Week 8: Add read replica for database
```

**Commands**: Right-click → **Coach → Scaling Analysis**

---

### 10. ObservabilityWizard 📊

**Expertise**: Logging, metrics, tracing, monitoring, alerting

**Powered by**: LangChain with observability best practices

**Key Capabilities**:
- Structured logging recommendations
- Metric collection strategy
- Distributed tracing setup
- Alert configuration
- Dashboard design
- SLI/SLO definitions

**Example**:
```python
# Before (poor logging)
print("User login")
print(f"Error: {e}")

# After (ObservabilityWizard recommendation)
import structlog
logger = structlog.get_logger()

logger.info("user.login.attempt",
    user_id=user.id,
    email=user.email,
    ip=request.remote_addr)

logger.error("payment.processing.failed",
    error_type=type(e).__name__,
    error_message=str(e),
    amount=amount,
    user_id=user.id,
    trace_id=request.trace_id,
    exc_info=True)

# Also suggests metrics:
metrics.counter('user.login.attempts', tags=['success:true'])
metrics.histogram('payment.processing_time', duration_ms)
```

**Commands**: Right-click → **Coach → Add Observability**

---

### 11. CICDWizard 🚀

**Expertise**: CI/CD pipelines, deployment strategies, GitOps, infrastructure as code

**Powered by**: LangChain with DevOps best practices

**Key Capabilities**:
- Pipeline optimization
- Deployment strategy recommendations (blue/green, canary, rolling)
- Environment management
- Rollback procedures
- Infrastructure as code review
- Security scanning integration

**Example**:
```yaml
# Before (basic CI)
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm test

# After (CICDWizard recommendation)
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/cache@v3
        with:
          path: ~/.npm
          key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
      - run: npm ci
      - run: npm test
      - run: npm run lint
      - name: Security scan
        run: npm audit
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/develop'
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to staging
        run: ./deploy.sh staging
      - name: Run smoke tests
        run: ./smoke-tests.sh staging

  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - name: Deploy with canary strategy
        run: ./deploy-canary.sh production
      - name: Monitor error rates
        run: ./monitor-deployment.sh
      - name: Rollback if needed
        if: failure()
        run: ./rollback.sh
```

**Commands**: Right-click → **Coach → CI/CD Review**

---

### 12. DocumentationWizard 📝

**Expertise**: API documentation, code comments, README generation, changelog maintenance

**Powered by**: LangChain with documentation templates and best practices

**Key Capabilities**:
- Generate API documentation from code
- Improve code comment quality
- Create/update README files
- Generate changelogs
- Create user guides
- Generate OpenAPI/Swagger specs

**Example**:
```python
# Before (no documentation)
def process(data, opts):
    if opts['mode'] == 'fast':
        return quick_process(data)
    return slow_process(data)

# After (DocumentationWizard suggestion)
def process(data: List[Dict], opts: ProcessingOptions) -> ProcessedResult:
    """Process data with configurable strategy.

    This function processes input data using either a fast or thorough algorithm
    based on the provided options. The fast mode is suitable for real-time
    processing but may miss edge cases. The thorough mode is recommended for
    batch processing.

    Args:
        data: List of dictionaries containing raw data to process.
              Each dictionary must have 'id', 'timestamp', and 'value' keys.
        opts: ProcessingOptions object containing configuration.
              - mode: Either 'fast' or 'thorough' (default: 'thorough')
              - max_retries: Maximum retry attempts for failed items (default: 3)
              - timeout: Processing timeout in seconds (default: 30)

    Returns:
        ProcessedResult object containing:
        - processed_items: List of successfully processed items
        - failed_items: List of items that failed processing
        - stats: Processing statistics (total, success_rate, duration)

    Raises:
        ValueError: If data is empty or opts.mode is invalid
        TimeoutError: If processing exceeds opts.timeout

    Example:
        >>> data = [{'id': 1, 'timestamp': '2024-01-01', 'value': 42}]
        >>> opts = ProcessingOptions(mode='fast', timeout=10)
        >>> result = process(data, opts)
        >>> print(result.stats.success_rate)
        1.0

    Note:
        Fast mode uses an approximate algorithm with O(n) complexity.
        Thorough mode uses exact algorithm with O(n log n) complexity.

    See Also:
        - quick_process(): Fast processing implementation
        - slow_process(): Thorough processing implementation
        - ProcessingOptions: Configuration object documentation
    """
    if not data:
        raise ValueError("Data cannot be empty")

    if opts.mode not in ['fast', 'thorough']:
        raise ValueError(f"Invalid mode: {opts.mode}. Must be 'fast' or 'thorough'")

    if opts.mode == 'fast':
        return quick_process(data, opts)
    return slow_process(data, opts)
```

**Commands**: Right-click → **Coach → Generate Documentation**

---

### 13. ComplianceWizard ⚖️

**Expertise**: GDPR, SOC 2, PCI DSS, HIPAA, data privacy regulations

**Powered by**: LangChain with compliance requirements database

**Key Capabilities**:
- GDPR compliance checking
- SOC 2 requirements validation
- PCI DSS validation for payment systems
- HIPAA compliance for healthcare
- Data privacy best practices
- Audit trail recommendations

**Example**:
```python
# Before (GDPR violation)
def get_user_data(user_id):
    user = User.query.get(user_id)
    return {
        'email': user.email,
        'password_hash': user.password_hash,  # ❌ Shouldn't expose
        'ssn': user.ssn,  # ❌ PII without justification
        'medical_history': user.medical_history,  # ❌ Sensitive data
        'ip_addresses': user.login_ips,  # ❌ Tracking data
        'deleted_at': None  # ❌ No deletion support
    }

# After (ComplianceWizard recommendation)
def get_user_data(user_id, purpose: str, requestor: User):
    """Get user data with GDPR compliance.

    Args:
        purpose: Legal basis for access (e.g., 'user_request', 'legal_obligation')
        requestor: User making the request (for audit trail)
    """
    # GDPR Article 6: Lawful basis for processing
    if not is_lawful_purpose(purpose):
        raise ValueError("Invalid purpose for data access")

    # Log access for audit trail (GDPR Article 30)
    audit_log.record_access(
        user_id=user_id,
        accessed_by=requestor.id,
        purpose=purpose,
        timestamp=datetime.utcnow()
    )

    user = User.query.get_or_404(user_id)

    # GDPR Article 5: Data minimization
    # Only return necessary fields
    data = {
        'email': user.email,
        'name': user.name,
        'created_at': user.created_at
    }

    # GDPR Article 17: Right to be forgotten
    if user.deletion_requested_at:
        data['deletion_status'] = 'pending'
        data['will_be_deleted_at'] = user.deletion_requested_at + timedelta(days=30)

    return data

def request_account_deletion(user_id):
    """GDPR Article 17: Right to erasure"""
    user = User.query.get(user_id)
    user.deletion_requested_at = datetime.utcnow()

    # Schedule actual deletion after 30-day grace period
    schedule_deletion_task(user_id, delay_days=30)

    # Notify user
    send_deletion_confirmation_email(user)
```

**Commands**: Right-click → **Coach → Compliance Audit**

---

### 14. MigrationWizard 🔄

**Expertise**: Database migrations, API versioning, feature flags, zero-downtime deployments

**Powered by**: LangChain with migration strategies and rollback planning

**Key Capabilities**:
- Database migration safety checks
- API versioning strategies
- Feature flag implementation
- Zero-downtime deployment planning
- Data migration scripts
- Rollback procedures

**Example**:
```python
# Database migration (recommended strategy)

# Step 1: Add new column (nullable)
# migration_001_add_email_column.py
def upgrade():
    # Safe: non-breaking change
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=True))

# Step 2: Backfill data (separate deployment)
# migration_002_backfill_email_verified.py
def upgrade():
    # Run during low-traffic period
    op.execute("""
        UPDATE users
        SET email_verified = FALSE
        WHERE email_verified IS NULL
    """)

# Step 3: Make column non-nullable (after verification)
# migration_003_email_verified_not_null.py
def upgrade():
    # Safe: all data backfilled in Step 2
    op.alter_column('users', 'email_verified', nullable=False)

# MigrationWizard Level 4 Warning:
# ⚠️ Do NOT combine these steps into one migration!
# Doing so causes downtime if backfill is slow.
# Deploy each step separately with monitoring.
```

**Commands**: Right-click → **Coach → Migration Planning**

---

### 15. MonitoringWizard 👁️

**Expertise**: Health checks, SLA monitoring, error tracking, performance metrics

**Powered by**: LangChain with monitoring best practices

**Key Capabilities**:
- Health check endpoints
- SLI/SLO/SLA definitions
- Error rate monitoring
- Performance degradation detection
- Alert configuration
- Incident response playbooks

**Example**:
```python
# MonitoringWizard recommended health check
from flask import jsonify
import psycopg2

@app.route('/health', methods=['GET'])
def health_check():
    """Comprehensive health check endpoint

    Returns HTTP 200 if all systems operational
    Returns HTTP 503 if any critical system is down
    """
    health = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'checks': {}
    }

    # Check database
    try:
        db.session.execute('SELECT 1')
        health['checks']['database'] = {
            'status': 'up',
            'latency_ms': measure_db_latency()
        }
    except Exception as e:
        health['checks']['database'] = {
            'status': 'down',
            'error': str(e)
        }
        health['status'] = 'unhealthy'

    # Check Redis
    try:
        redis_client.ping()
        health['checks']['redis'] = {
            'status': 'up',
            'memory_usage': redis_client.info('memory')['used_memory_human']
        }
    except Exception as e:
        health['checks']['redis'] = {
            'status': 'down',
            'error': str(e)
        }
        health['status'] = 'degraded'  # Non-critical

    # Check external APIs
    health['checks']['payment_api'] = check_external_service(
        'https://api.stripe.com/healthcheck',
        timeout=2
    )

    status_code = 200 if health['status'] == 'healthy' else 503
    return jsonify(health), status_code

# SLO definitions (MonitoringWizard suggestions)
SLO_TARGETS = {
    'availability': 0.999,  # 99.9% uptime (43.2 min/month downtime)
    'latency_p95': 200,  # 95th percentile < 200ms
    'latency_p99': 500,  # 99th percentile < 500ms
    'error_rate': 0.001,  # < 0.1% error rate
}
```

**Commands**: Right-click → **Coach → Setup Monitoring**

---

### 16. LocalizationWizard 🌍

**Expertise**: Internationalization (i18n), translation, locale handling, cultural considerations

**Powered by**: LangChain with localization best practices

**Key Capabilities**:
- i18n best practices
- Translation file management
- Date/time formatting for locales
- Number/currency formatting
- RTL (right-to-left) support
- Cultural considerations

**Example**:
```python
# Before (hardcoded strings)
def send_welcome_email(user):
    subject = "Welcome to our app!"
    body = f"Hi {user.name}, thanks for signing up. Your account is ready."
    send_email(user.email, subject, body)

# After (LocalizationWizard recommendation)
from flask_babel import gettext as _
from babel.dates import format_datetime
from babel.numbers import format_currency

def send_welcome_email(user):
    # Get user's locale (e.g., 'en_US', 'fr_FR', 'ar_SA')
    locale = user.locale or 'en_US'

    # Translate subject and body
    subject = _("welcome.email.subject")
    body = _("welcome.email.body", username=user.name)

    # Include localized date
    signup_date = format_datetime(
        user.created_at,
        format='medium',
        locale=locale
    )
    body += "\n" + _("welcome.signup_date", date=signup_date)

    send_email(user.email, subject, body, locale=locale)

# Translation files (recommended structure)
# translations/en/messages.po
msgid "welcome.email.subject"
msgstr "Welcome to our app!"

msgid "welcome.email.body"
msgstr "Hi {username}, thanks for signing up. Your account is ready."

msgid "welcome.signup_date"
msgstr "You signed up on {date}"

# translations/fr/messages.po
msgid "welcome.email.subject"
msgstr "Bienvenue dans notre application !"

msgid "welcome.email.body"
msgstr "Bonjour {username}, merci de vous être inscrit. Votre compte est prêt."

# translations/ar/messages.po (RTL support)
msgid "welcome.email.subject"
msgstr "مرحبا بك في تطبيقنا!"

msgid "welcome.email.body"
msgstr "مرحبًا {username}، شكرًا لتسجيلك. حسابك جاهز."

# Currency formatting
price_usd = format_currency(19.99, 'USD', locale='en_US')  # $19.99
price_eur = format_currency(19.99, 'EUR', locale='fr_FR')  # 19,99 €
price_jpy = format_currency(1999, 'JPY', locale='ja_JP')   # ¥1,999
```

**Commands**: Right-click → **Coach → Localization Review**

---

## Wizard Collaboration

### Multi-Wizard Scenarios

Coach automatically coordinates multiple wizards for complex scenarios:

#### Scenario: `new_api_endpoint`
**Wizards Involved**: APIWizard, SecurityWizard, PerformanceWizard, DatabaseWizard, TestingWizard

**Example**:
```
User: Create new API endpoint to fetch user orders

Coach orchestrates:
1. APIWizard (Primary)
   - Designs RESTful endpoint structure
   - Generates OpenAPI spec
   - Recommends pagination

2. SecurityWizard (Consulted)
   - Adds authentication requirement
   - Recommends rate limiting
   - Suggests input validation

3. PerformanceWizard (Consulted)
   - Identifies N+1 query risk
   - Recommends eager loading
   - Suggests caching strategy

4. DatabaseWizard (Consulted)
   - Reviews query optimization
   - Recommends indexes
   - Validates schema

5. TestingWizard (Consulted)
   - Generates unit tests
   - Generates integration tests
   - Suggests edge cases

Result: Comprehensive API implementation with security, performance, and testing
```

#### Scenario: `production_incident`
**Wizards Involved**: DebuggingWizard, ObservabilityWizard, MonitoringWizard, PerformanceWizard

#### Scenario: `database_migration`
**Wizards Involved**: DatabaseWizard, MigrationWizard, MonitoringWizard

#### Scenario: `compliance_audit`
**Wizards Involved**: ComplianceWizard, SecurityWizard, DocumentationWizard

### Wizard Disagreements

When wizards disagree, Coach presents both perspectives:

**Example**:
```
Scenario: Should we add caching?

PerformanceWizard: ✅ YES
- Response time: 500ms → 50ms (10x improvement)
- Reduced database load
- Better user experience

SecurityWizard: ⚠️ CAUTION
- Risk: Cached sensitive data exposure
- Recommendation: Use short TTL (30s max)
- Must implement cache invalidation
- Encrypt cached data

Coach Recommendation:
Implement caching with SecurityWizard's safeguards:
- Cache non-sensitive data only
- TTL: 30 seconds
- Encrypt cached values
- Implement cache invalidation
- Monitor cache hit rate

Net Result: Performance benefit with security maintained
```

---

## Wizard API

### Invoke Wizard Programmatically

```python
from coach import Coach

coach = Coach()

# Run single wizard
result = coach.run_wizard(
    wizard_name="SecurityWizard",
    task="Analyze authentication flow",
    code=code_snippet,
    context="Payment processing system"
)

print(result.diagnosis)
print(result.recommendations)
print(result.confidence)

# Run multi-wizard review
result = coach.multi_wizard_review(
    scenario="new_api_endpoint",
    files=["api/orders.py", "models/order.py"]
)

print(result.primary_output)  # APIWizard result
print(result.supplemental_outputs)  # Other wizards
print(result.collaboration.consensus_areas)
print(result.collaboration.disagreements)
```

### Custom Wizard Creation

See [CUSTOM_WIZARDS.md](CUSTOM_WIZARDS.md) for complete tutorial on building custom wizards with LangChain.

---

## Summary

All 16 wizards work together through Coach's orchestration layer to provide comprehensive development assistance. Each wizard:

- ✅ **Powered by LangChain** - Extensible and customizable
- ✅ **Specialized expertise** - Deep domain knowledge
- ✅ **Level 4 predictions** - Anticipates future issues
- ✅ **Collaborative** - Consults other wizards when needed
- ✅ **Confidence scoring** - Transparent about certainty
- ✅ **Code examples** - Actionable recommendations

**Next**: Learn to build your own wizards in [CUSTOM_WIZARDS.md](CUSTOM_WIZARDS.md)

---

**Questions?** Join [Coach Discord](https://discord.gg/coach-alpha) or email support@deepstudyai.com

**Built with** ❤️ **using LangChain**
