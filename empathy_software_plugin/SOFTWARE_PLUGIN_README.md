# Software Development Plugin

Production-ready Level 4 Anticipatory wizards for software development.

**Copyright 2025 Deep Study AI, LLC**
**Licensed under Fair Source 0.9**

## Overview

The Software Development Plugin provides three specialized wizards that predict and prevent software issues before they become critical:

1. **Enhanced Testing Wizard** - Predicts where bugs will occur based on test coverage gaps
2. **Performance Profiling Wizard** - Predicts performance degradation before it impacts users
3. **Security Analysis Wizard** - Predicts which vulnerabilities will actually be exploited

All three wizards operate at **Level 4: Anticipatory Empathy**, meaning they don't just identify current issues—they predict future problems and alert you before they become critical.

## Quick Start

```python
from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard
from empathy_software_plugin.wizards.performance_profiling_wizard import PerformanceProfilingWizard
from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

# Enhanced Testing Wizard
testing_wizard = EnhancedTestingWizard()
result = await testing_wizard.analyze({
    'source_files': ['src/'],
    'test_files': ['tests/'],
    'project_path': '/path/to/project'
})

print(f"High-risk gaps: {result['high_risk_gaps']}")
print(f"Predictions: {result['predictions']}")

# Performance Profiling Wizard
performance_wizard = PerformanceProfilingWizard()
result = await performance_wizard.analyze({
    'profiler_data': profiler_output,
    'profiler_type': 'cprofile'  # or 'chrome_devtools', 'simple_json'
})

print(f"Bottlenecks: {result['bottlenecks']}")
print(f"Trajectory: {result['trajectory_analysis']}")

# Security Analysis Wizard
security_wizard = SecurityAnalysisWizard()
result = await security_wizard.analyze({
    'source_files': ['src/'],
    'project_path': '/path/to/project',
    'endpoint_config': {
        'src/api.py': {'endpoint_public': True}
    }
})

print(f"Vulnerabilities: {result['vulnerabilities_found']}")
print(f"Exploitability: {result['exploitability_assessments']}")
```

## Wizards

### 1. Enhanced Testing Wizard

**Level 4 Capability:** Predicts where bugs will occur based on test coverage gaps and code patterns.

#### What It Does

- Analyzes test coverage beyond simple percentages
- Identifies high-risk code patterns (authentication, payments, error handling, user input, financial calculations)
- Detects brittle tests that will break with minor code changes
- Predicts bug likelihood in untested code
- Generates smart test suggestions

#### High-Risk Patterns

The wizard identifies untested code in these categories:

- **Authentication/Authorization** - Login, permissions, access control
- **Payment Processing** - Financial transactions, billing
- **Error Handling** - Exception handling, recovery logic
- **User Input Validation** - Form processing, API parameters
- **Financial Calculations** - Money, pricing, tax calculations

#### Example Output

```python
{
    "coverage_summary": {
        "overall_coverage": 0.75,
        "covered_lines": 300,
        "total_lines": 400,
        "uncovered_files": 5
    },
    "high_risk_gaps": [
        {
            "file_path": "src/auth.py",
            "function_name": "verify_permissions",
            "risk_category": "authentication",
            "risk_level": "CRITICAL",
            "uncovered_lines": [42, 43, 44],
            "reasoning": "Authorization logic with no test coverage"
        }
    ],
    "predictions": [
        {
            "type": "bug_risk_in_untested_auth",
            "severity": "HIGH",
            "description": "In our experience, untested authentication code leads to security vulnerabilities",
            "affected_functions": ["verify_permissions"],
            "prevention_steps": [
                "Add unit tests for all authorization paths",
                "Test both allowed and denied access scenarios",
                "Include tests for edge cases (null user, expired tokens)"
            ]
        }
    ]
}
```

#### When to Use

- Before deployment (ensure critical code is tested)
- During code review (identify testing gaps)
- Sprint planning (prioritize test writing)
- After adding new features (verify test coverage)

### 2. Performance Profiling Wizard

**Level 4 Capability:** Predicts performance degradation before it becomes critical by analyzing historical trends.

#### What It Does

- Parses profiling data from multiple tools (cProfile, Chrome DevTools, custom JSON)
- Detects bottlenecks: hot paths, N+1 queries, I/O bound operations
- Analyzes performance trajectory (degrading, stable, optimal)
- Predicts time to critical thresholds
- Provides fix suggestions based on real-world experience

#### Supported Profilers

1. **cProfile** (Python standard library)
   ```python
   import cProfile
   profiler = cProfile.Profile()
   profiler.enable()
   # ... your code ...
   profiler.disable()
   stats = profiler.get_stats()
   ```

2. **Chrome DevTools** (browser performance)
   - Record performance profile in Chrome
   - Export as JSON
   - Pass to wizard

3. **Simple JSON** (custom profilers)
   ```json
   {
     "functions": [
       {
         "name": "function_name",
         "file": "path/to/file.py",
         "line": 42,
         "total_time": 1.5,
         "self_time": 1.0,
         "calls": 100,
         "cumulative_time": 1.5,
         "percent": 15.0
       }
     ]
   }
   ```

#### Bottleneck Types

- **Hot Path** - Function consuming >20% of total execution time
- **N+1 Query** - Database query called repeatedly (>50 times)
- **I/O Bound** - File or network operations blocking execution
- **CPU Bound** - Computationally expensive operations
- **Memory Leak** - Growing memory usage over time
- **Synchronous I/O** - Blocking I/O in async context

#### Trajectory Analysis

The wizard analyzes historical metrics to predict future performance:

```python
# Provide historical metrics
historical_metrics = [
    {"timestamp": "2024-01-01T10:00:00", "response_time": 0.2},
    {"timestamp": "2024-01-02T10:00:00", "response_time": 0.45},
    {"timestamp": "2024-01-03T10:00:00", "response_time": 0.8}
]

result = await wizard.analyze({
    'profiler_data': current_profile,
    'profiler_type': 'cprofile',
    'historical_metrics': historical_metrics
})

# Output includes prediction
{
    "trajectory_analysis": {
        "state": "degrading",
        "trends": [
            {
                "metric_name": "response_time",
                "direction": "degrading",
                "current_value": 0.8,
                "rate_of_change": 0.3,
                "severity": "HIGH"
            }
        ],
        "time_to_critical": "~1.3 days"
    }
}
```

#### Example Output

```python
{
    "profiling_summary": {
        "total_functions": 50,
        "total_time": 10.0,
        "top_function": "process_request (45% of time)"
    },
    "bottlenecks": [
        {
            "type": "hot_path",
            "function_name": "process_request",
            "file_path": "api.py",
            "line_number": 42,
            "severity": "CRITICAL",
            "time_consumed": 4.5,
            "percent_of_total": 45.0,
            "reasoning": "Single function consuming nearly half of execution time",
            "fix_suggestion": "Profile this function further to identify optimization opportunities. Consider caching, algorithmic improvements, or async processing."
        },
        {
            "type": "n_plus_one",
            "function_name": "fetch_user",
            "file_path": "database.py",
            "line_number": 100,
            "severity": "HIGH",
            "call_count": 1000,
            "reasoning": "Database query called 1000 times - classic N+1 pattern",
            "fix_suggestion": "Use eager loading or batch queries. Replace loop with single query using IN clause or JOIN."
        }
    ],
    "predictions": [
        {
            "type": "performance_degradation",
            "severity": "HIGH",
            "description": "In our experience, response times trending upward lead to timeout errors under load",
            "affected_code": ["process_request"],
            "prevention_steps": [
                "Optimize hot path in process_request",
                "Add caching layer",
                "Monitor response time trends"
            ]
        }
    ]
}
```

#### When to Use

- After profiling production traffic (identify real bottlenecks)
- During load testing (understand performance characteristics)
- Investigating slow endpoints (find root cause)
- Monitoring performance trends (predict degradation)

### 3. Security Analysis Wizard

**Level 4 Capability:** Predicts which vulnerabilities will actually be exploited based on accessibility and attack patterns.

#### What It Does

- Detects OWASP Top 10 vulnerabilities
- Assesses exploitability (not just theoretical severity)
- Considers endpoint accessibility (public/authenticated/internal)
- Calculates exploit likelihood based on real-world attack patterns
- Prioritizes by actual risk, not just CVSS scores

#### Detected Vulnerabilities

Based on **OWASP Top 10**:

1. **Injection** - SQL, Command, LDAP injection
2. **Cryptographic Failures** - Weak algorithms (MD5, SHA1), hardcoded secrets
3. **Cross-Site Scripting (XSS)** - innerHTML, document.write with user input
4. **Insecure Deserialization** - Pickle, eval() with untrusted data
5. **Security Misconfiguration** - Missing authentication, debug mode
6. **Path Traversal** - File access with user-controlled paths
7. **CSRF** - Missing CSRF tokens on state-changing endpoints

#### Exploitability Assessment

The wizard goes beyond finding vulnerabilities—it predicts which ones will be exploited:

```python
{
    "exploitability_assessments": [
        {
            "vulnerability": {
                "category": "injection",
                "name": "SQL Injection",
                "severity": "CRITICAL",
                "file_path": "api.py",
                "line_number": 42
            },
            "accessibility": "public",  # Publicly accessible endpoint
            "attack_complexity": "low",  # Easy to exploit
            "exploit_likelihood": 0.9,  # 90% chance of being exploited
            "exploitability": "CRITICAL",
            "reasoning": "Publicly accessible SQL injection with low attack complexity. In our experience, actively scanned by automated tools (SQLMap, Havij).",
            "mitigation_urgency": "IMMEDIATE",  # Fix before deploying
            "real_world_examples": [
                "SQLMap automated scanner",
                "Havij SQL injection tool",
                "Automated bot scans"
            ]
        }
    ]
}
```

#### Mitigation Urgency Levels

- **IMMEDIATE** - Fix before next deployment (hours)
- **URGENT** - Fix within 24 hours
- **HIGH** - Fix within 1 week
- **MEDIUM** - Fix within sprint (2 weeks)
- **LOW** - Address in future release

#### Example Output

```python
{
    "vulnerabilities_found": 5,
    "by_severity": {
        "CRITICAL": 2,
        "HIGH": 2,
        "MEDIUM": 1
    },
    "by_category": {
        "injection": 2,
        "cryptographic_failures": 2,
        "cross_site_scripting": 1
    },
    "exploitability_assessments": [
        {
            "vulnerability": {
                "category": "injection",
                "name": "SQL Injection",
                "severity": "CRITICAL",
                "file_path": "api.py",
                "line_number": 42,
                "code_snippet": "query = f\"SELECT * FROM users WHERE id={user_id}\"",
                "description": "SQL query built with f-string interpolation",
                "example_fix": "cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))"
            },
            "accessibility": "public",
            "attack_complexity": "low",
            "exploit_likelihood": 0.9,
            "exploitability": "CRITICAL",
            "reasoning": "Publicly accessible SQL injection with low attack complexity. In our experience, actively scanned by automated tools.",
            "mitigation_urgency": "IMMEDIATE"
        }
    ],
    "insights": {
        "most_common_category": "injection",
        "critical_exploitable": 2,
        "exploitable_percent": 0.4,
        "public_exposure": 3,
        "immediate_action_required": true
    },
    "predictions": [
        {
            "type": "imminent_exploitation_risk",
            "severity": "CRITICAL",
            "description": "In our experience, public SQL injection vulnerabilities are exploited within hours of discovery",
            "affected_endpoints": ["api.py:42"],
            "prevention_steps": [
                "Use parameterized queries immediately",
                "Review all database queries for injection",
                "Add input validation",
                "Enable SQL query logging for detection"
            ]
        }
    ]
}
```

#### Endpoint Configuration

Help the wizard assess exploitability by providing endpoint context:

```python
endpoint_config = {
    'src/api.py': {
        'endpoint_public': True  # Publicly accessible
    },
    'src/admin.py': {
        'endpoint_public': False,  # Requires authentication
        'requires_auth': True
    },
    'src/internal.py': {
        'endpoint_public': False,  # Internal only
        'internal_only': True
    }
}
```

#### When to Use

- Before deployment (security gate)
- After adding new endpoints (vulnerability scan)
- Code review (identify security issues)
- Compliance audits (demonstrate security practices)
- Penetration testing preparation (find issues first)

## Integration: Using All Three Wizards

The wizards are designed to work together. Here's a complete pre-deployment workflow:

```python
from empathy_software_plugin.wizards.enhanced_testing_wizard import EnhancedTestingWizard
from empathy_software_plugin.wizards.performance_profiling_wizard import PerformanceProfilingWizard
from empathy_software_plugin.wizards.security_analysis_wizard import SecurityAnalysisWizard

async def pre_deployment_check(project_path, source_files, test_files, profile_data, endpoint_config):
    """
    Run all three wizards before deployment.
    Returns True if deployment is safe, False if blockers found.
    """

    # Initialize wizards
    testing_wizard = EnhancedTestingWizard()
    performance_wizard = PerformanceProfilingWizard()
    security_wizard = SecurityAnalysisWizard()

    # Run security scan first (blocking issues)
    print("Step 1/3: Security scan...")
    security_result = await security_wizard.analyze({
        'source_files': source_files,
        'project_path': project_path,
        'endpoint_config': endpoint_config
    })

    # Run test coverage analysis
    print("Step 2/3: Test coverage analysis...")
    testing_result = await testing_wizard.analyze({
        'source_files': source_files,
        'test_files': test_files,
        'project_path': project_path
    })

    # Run performance analysis
    print("Step 3/3: Performance analysis...")
    performance_result = await performance_wizard.analyze({
        'profiler_data': profile_data,
        'profiler_type': 'simple_json'
    })

    # Collect deployment blockers
    blockers = []

    # Check for IMMEDIATE security issues
    for assessment in security_result['exploitability_assessments']:
        if 'IMMEDIATE' in assessment['mitigation_urgency']:
            blockers.append({
                'type': 'security',
                'severity': 'CRITICAL',
                'description': f"{assessment['vulnerability']['name']} in {assessment['vulnerability']['file_path']}",
                'action': assessment['vulnerability']['example_fix']
            })

    # Check for critical untested code
    for gap in testing_result['high_risk_gaps']:
        if gap['risk_level'] == 'CRITICAL':
            blockers.append({
                'type': 'testing',
                'severity': 'HIGH',
                'description': f"Untested {gap['risk_category']} code: {gap['function_name']}",
                'action': f"Add tests covering {gap['function_name']}"
            })

    # Check for critical performance issues
    for bottleneck in performance_result['bottlenecks']:
        if bottleneck['severity'] == 'CRITICAL':
            blockers.append({
                'type': 'performance',
                'severity': 'HIGH',
                'description': f"{bottleneck['type']} in {bottleneck['function_name']}",
                'action': bottleneck['fix_suggestion']
            })

    # Print results
    if blockers:
        print(f"\n❌ DEPLOYMENT BLOCKED - {len(blockers)} critical issues found:\n")
        for i, blocker in enumerate(blockers, 1):
            print(f"{i}. [{blocker['type'].upper()}] {blocker['description']}")
            print(f"   Action: {blocker['action']}\n")
        return False
    else:
        print("\n✅ DEPLOYMENT APPROVED - No blocking issues found")
        print("\nRecommendations for future sprints:")
        for rec in testing_result['recommendations'][:3]:
            print(f"  - {rec}")
        return True

# Usage
deployment_safe = await pre_deployment_check(
    project_path='/path/to/project',
    source_files=['src/api.py', 'src/auth.py'],
    test_files=['tests/test_api.py'],
    profile_data=profiler_output,
    endpoint_config={
        'src/api.py': {'endpoint_public': True},
        'src/auth.py': {'endpoint_public': False}
    }
)

if not deployment_safe:
    exit(1)  # Block CI/CD pipeline
```

## Installation

The Software Development Plugin is part of the Empathy Framework:

```bash
pip install empathy-framework

# Or install from source
git clone https://github.com/deepstudyai/empathy
cd empathy
pip install -e .
```

## Examples

Complete examples are in [`examples/`](../examples/):

- [`testing_demo.py`](../examples/testing_demo.py) - Enhanced Testing Wizard demo
- [`performance_demo.py`](../examples/performance_demo.py) - Performance Profiling Wizard demo
- [`security_demo.py`](../examples/security_demo.py) - Security Analysis Wizard demo
- [`software_plugin_complete_demo.py`](../examples/software_plugin_complete_demo.py) - All wizards working together

Run any demo:

```bash
python examples/testing_demo.py
python examples/performance_demo.py
python examples/security_demo.py
python examples/software_plugin_complete_demo.py
```

## Testing

Comprehensive test suite in [`tests/`](../tests/):

```bash
# Run all Software Plugin tests
pytest tests/test_enhanced_testing.py -v
pytest tests/test_performance_wizard.py -v
pytest tests/test_security_wizard.py -v
pytest tests/test_software_integration.py -v

# Run all tests
pytest tests/ -v
```

## Architecture

Each wizard follows the same Level 4 Anticipatory pattern:

```
1. Current State Analysis
   ↓
2. Historical Trend Analysis
   ↓
3. Rate of Change Calculation
   ↓
4. Future State Prediction
   ↓
5. Time to Critical Threshold
   ↓
6. Preventive Recommendations
```

### Standardized Data Formats

All wizards use standardized dataclasses for consistency:

```python
# Performance
@dataclass
class FunctionProfile:
    function_name: str
    file_path: str
    line_number: int
    total_time: float
    call_count: int
    percent_total: float

# Security
@dataclass
class Vulnerability:
    category: str  # OWASP category
    name: str
    severity: str
    file_path: str
    line_number: int

# Testing
@dataclass
class TestGap:
    file_path: str
    function_name: str
    risk_category: str
    risk_level: str
    uncovered_lines: List[int]
```

## Best Practices

### 1. Run Security Wizard First

Always run security scans before other checks:

```python
# ✅ Good
security_result = await security_wizard.analyze(...)
if security_result['vulnerabilities_found'] > 0:
    # Fix security issues first
    ...

# ❌ Bad
# Optimizing performance before fixing security issues
```

### 2. Provide Historical Metrics

For best predictions, provide historical data:

```python
# ✅ Good
historical_metrics = load_metrics_from_monitoring()
result = await performance_wizard.analyze({
    'profiler_data': current_profile,
    'historical_metrics': historical_metrics  # Enables trajectory analysis
})

# ❌ Bad
result = await performance_wizard.analyze({
    'profiler_data': current_profile
    # No historical data = no trajectory prediction
})
```

### 3. Configure Endpoint Accessibility

Help the security wizard prioritize:

```python
# ✅ Good
endpoint_config = {
    'api.py': {'endpoint_public': True},  # Public = high priority
    'admin.py': {'endpoint_public': False}  # Internal = lower priority
}

# ❌ Bad
endpoint_config = {}  # Wizard can't assess exploitability
```

### 4. Test High-Risk Code First

Focus testing efforts based on wizard recommendations:

```python
testing_result = await testing_wizard.analyze(...)

# Prioritize by risk level
critical_gaps = [gap for gap in testing_result['high_risk_gaps']
                 if gap['risk_level'] == 'CRITICAL']

for gap in critical_gaps:
    # Write tests for critical gaps first
    write_tests_for(gap['function_name'])
```

## Experience-Based Messaging

All wizards use "in our experience" framing rather than specific predictions:

✅ **Good:**
- "In our experience, untested authentication code leads to security vulnerabilities"
- "In our experience, this pattern leads to timeout errors under load"
- "In our experience, publicly accessible SQL injection is exploited within hours"

❌ **Bad:**
- "This will cause a bug"
- "Performance will degrade by 50%"
- "You will be hacked"

This approach:
- Sets appropriate expectations
- Acknowledges uncertainty
- Shares genuine insight from experience
- Avoids over-promising

## Support

- **Documentation:** [Full Framework Docs](../../docs/)
- **Issues:** [GitHub Issues](https://github.com/deepstudyai/empathy/issues)
- **Examples:** [examples/](../examples/)

## License

Copyright 2025 Deep Study AI, LLC

Licensed under Fair Source 0.9 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
