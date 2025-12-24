# Smart Router

The Smart Router enables natural language wizard dispatch - instead of knowing wizard names, developers describe what they need and the router figures out which wizard(s) to invoke.

## Quick Start

```python
from empathy_os.routing import SmartRouter

router = SmartRouter()

# Natural language routing
decision = router.route_sync("Fix the security issue in auth.py")
print(f"Primary: {decision.primary_wizard}")      # → security-audit
print(f"Secondary: {decision.secondary_wizards}")  # → [code-review]
print(f"Confidence: {decision.confidence}")        # → 0.85
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                      SMART ROUTER                                │
│   Developer: "Fix performance in auth.py"                        │
│   → Routes to: PerformanceWizard + SecurityWizard               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     WIZARD REGISTRY                              │
│   17+ wizards with keywords, descriptions, and capabilities     │
└─────────────────────────────────────────────────────────────────┘
```

The router uses a keyword-based classifier to match requests to wizards. Each wizard is registered with:

- **Name**: Unique identifier (e.g., `security-audit`)
- **Description**: What the wizard does
- **Keywords**: Terms that trigger this wizard

## Routing Methods

### route_sync() / route()

Route a natural language request to wizard(s):

```python
# Synchronous
decision = router.route_sync("Check for SQL injection vulnerabilities")

# Asynchronous
decision = await router.route("Optimize slow database queries")
```

### suggest_for_file()

Get wizard suggestions based on a file path:

```python
# Python file → security, code-review
suggestions = router.suggest_for_file("src/auth.py")

# Package.json → dependency-check
suggestions = router.suggest_for_file("package.json")

# Dockerfile → security-audit
suggestions = router.suggest_for_file("Dockerfile")
```

### suggest_for_error()

Get wizard suggestions based on an error message:

```python
# Null reference → bug-predict
suggestions = router.suggest_for_error("NullPointerException at line 42")

# Security error → security-audit
suggestions = router.suggest_for_error("SecurityException: Access denied")
```

## RoutingDecision

The router returns a `RoutingDecision` with:

```python
@dataclass
class RoutingDecision:
    primary_wizard: str          # Best matching wizard
    secondary_wizards: List[str] # Related wizards to consider
    confidence: float            # 0.0-1.0 match confidence
    reasoning: str               # Why this routing was chosen
    suggested_chain: List[str]   # Recommended execution order
    context: Dict                # Preserved context from request
    classification_method: str   # "keyword" or "llm"
    request_summary: str         # Original request
```

## Context Preservation

Pass context through to the wizard:

```python
decision = router.route_sync(
    "Review this code",
    context={
        "file": "auth.py",
        "language": "python",
        "team": "backend"
    }
)

# Context is preserved in decision.context
print(decision.context)  # {"file": "auth.py", ...}
```

## List Available Wizards

```python
wizards = router.list_wizards()
for wizard in wizards:
    print(f"{wizard.name}: {wizard.description}")
    print(f"  Keywords: {wizard.keywords}")
```

## Integration with Chain Executor

The Smart Router works seamlessly with auto-chaining:

```python
from empathy_os.routing import SmartRouter, ChainExecutor

router = SmartRouter()
executor = ChainExecutor()

# Route the request
decision = router.route_sync("Security review of auth module")

# Execute the suggested chain
for wizard_name in decision.suggested_chain:
    print(f"Running: {wizard_name}")
```

## See Also

- [Memory Graph](memory-graph.md) - Cross-wizard knowledge sharing
- [Auto-Chaining](auto-chaining.md) - Automatic wizard sequencing
- [API Reference](../API_REFERENCE.md#smartrouter) - Full API documentation
