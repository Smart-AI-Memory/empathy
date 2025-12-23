# Auto-Chaining

Auto-Chaining enables wizards to automatically trigger related wizards based on their findings. This creates intelligent workflows where a security scan can automatically trigger a dependency check, or a bug prediction can trigger test generation.

## Quick Start

```yaml
# .empathy/wizard_chains.yaml
chains:
  security-audit:
    auto_chain: true
    triggers:
      - condition: "high_severity_count > 0"
        next: dependency-check
        approval_required: false
```

```python
from empathy_os.routing import ChainExecutor

executor = ChainExecutor()

# Check what chains would trigger
result = {"high_severity_count": 5}
triggers = executor.get_triggered_chains("security-audit", result)
# → [ChainTrigger(next="dependency-check", approval_required=False)]
```

## Configuration

Create `.empathy/wizard_chains.yaml` in your project root:

```yaml
chains:
  # Security audit triggers
  security-audit:
    auto_chain: true
    triggers:
      - condition: "high_severity_count > 0"
        next: dependency-check
        approval_required: false
      - condition: "vulnerability_type == 'injection'"
        next: code-review
        approval_required: true

  # Bug prediction triggers
  bug-predict:
    auto_chain: true
    triggers:
      - condition: "risk_score > 0.7"
        next: test-gen
        approval_required: false
      - condition: "affected_files > 5"
        next: refactor-plan
        approval_required: true

  # Performance audit triggers
  perf-audit:
    auto_chain: true
    triggers:
      - condition: "hotspot_count > 5"
        next: refactor-plan
        approval_required: true

  # Refactoring requires explicit approval
  refactor-plan:
    auto_chain: false  # Never auto-execute

# Pre-built workflow templates
templates:
  full-security-review:
    description: "Complete security analysis"
    steps:
      - security-audit
      - dependency-check
      - code-review

  pre-release:
    description: "Pre-release checklist"
    steps:
      - test-gen
      - security-audit
      - release-prep

  code-health:
    description: "Full code health analysis"
    steps:
      - bug-predict
      - perf-audit
      - refactor-plan
```

## Condition Syntax

Conditions use simple expressions evaluated against wizard results:

```yaml
# Numeric comparisons
- condition: "severity_count > 0"
- condition: "risk_score >= 0.7"
- condition: "affected_files <= 3"

# String equality
- condition: "vulnerability_type == 'injection'"
- condition: "status == 'critical'"

# Boolean checks
- condition: "has_vulnerabilities"
- condition: "needs_refactoring"
```

## ChainExecutor API

### Check Triggered Chains

```python
from empathy_os.routing import ChainExecutor

executor = ChainExecutor()

# Wizard result from security-audit
result = {
    "high_severity_count": 3,
    "vulnerability_type": "injection",
    "affected_files": 2
}

# Get all triggered chains
triggers = executor.get_triggered_chains("security-audit", result)

for trigger in triggers:
    print(f"Next: {trigger.next_wizard}")
    print(f"Requires approval: {trigger.approval_required}")
    print(f"Condition: {trigger.condition}")
```

### Get Templates

```python
# List available templates
templates = executor.list_templates()
# → ["full-security-review", "pre-release", "code-health"]

# Get a specific template
template = executor.get_template("full-security-review")
print(f"Steps: {template.steps}")
# → ["security-audit", "dependency-check", "code-review"]
```

### Check Auto-Execute Permission

```python
trigger = triggers[0]

if executor.should_auto_execute(trigger):
    print("Running automatically...")
else:
    print("Waiting for user approval...")
```

## Workflow Execution

Combine with Smart Router for complete workflows:

```python
from empathy_os.routing import SmartRouter, ChainExecutor

router = SmartRouter()
executor = ChainExecutor()

async def run_workflow(request: str):
    # Route initial request
    decision = router.route_sync(request)

    # Execute primary wizard
    result = await run_wizard(decision.primary_wizard)

    # Check for triggered chains
    triggers = executor.get_triggered_chains(
        decision.primary_wizard,
        result
    )

    # Execute triggered chains
    for trigger in triggers:
        if trigger.approval_required:
            approved = await get_user_approval(trigger)
            if not approved:
                continue

        chain_result = await run_wizard(trigger.next_wizard)
        result = {**result, **chain_result}

    return result
```

## Template Execution

Run pre-defined workflow templates:

```python
async def run_template(template_name: str, context: dict):
    template = executor.get_template(template_name)

    results = {}
    for wizard_name in template.steps:
        result = await run_wizard(wizard_name, context)
        results[wizard_name] = result

        # Update context with findings
        context = {**context, **result}

    return results

# Run full security review
results = await run_template("full-security-review", {
    "target_dir": "./src",
    "language": "python"
})
```

## Approval Workflows

For chains requiring approval:

```python
def handle_approval_required(trigger):
    """
    Show user what will run and why.
    """
    print(f"⚠️  The {trigger.current_wizard} wizard wants to run:")
    print(f"   → {trigger.next_wizard}")
    print(f"   Reason: {trigger.condition}")

    response = input("Approve? [y/N]: ")
    return response.lower() == 'y'
```

## Best Practices

### 1. Use Approval for Destructive Operations

```yaml
chains:
  refactor-plan:
    triggers:
      - condition: "changes_count > 10"
        next: auto-apply
        approval_required: true  # Always require approval
```

### 2. Limit Chain Depth

Prevent infinite loops by limiting chain depth:

```python
MAX_CHAIN_DEPTH = 5

async def run_with_depth_limit(wizard, depth=0):
    if depth >= MAX_CHAIN_DEPTH:
        return {"warning": "Chain depth limit reached"}

    result = await run_wizard(wizard)
    triggers = executor.get_triggered_chains(wizard, result)

    for trigger in triggers:
        await run_with_depth_limit(trigger.next_wizard, depth + 1)
```

### 3. Log Chain Execution

```python
import logging

logger = logging.getLogger("wizard_chains")

async def run_chain_with_logging(wizard, result):
    triggers = executor.get_triggered_chains(wizard, result)

    for trigger in triggers:
        logger.info(
            f"Chain triggered: {wizard} → {trigger.next_wizard} "
            f"(condition: {trigger.condition})"
        )
```

## See Also

- [Smart Router](smart-router.md) - Natural language wizard dispatch
- [Memory Graph](memory-graph.md) - Cross-wizard knowledge sharing
- [API Reference](../API_REFERENCE.md#chainexecutor) - Full API documentation
