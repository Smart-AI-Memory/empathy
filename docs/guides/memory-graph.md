# Memory Graph

The Memory Graph provides cross-wizard knowledge sharing by connecting findings, bugs, fixes, and patterns across sessions.

## Quick Start

```python
from empathy_os.memory import MemoryGraph, EdgeType

graph = MemoryGraph()

# Add a bug finding
bug_id = graph.add_finding(
    wizard="bug-predict",
    finding={
        "type": "bug",
        "name": "Null reference in auth.py:42",
        "severity": "high"
    }
)

# Add a fix
fix_id = graph.add_finding(
    wizard="code-review",
    finding={
        "type": "fix",
        "name": "Add null check before access"
    }
)

# Connect them
graph.add_edge(bug_id, fix_id, EdgeType.FIXED_BY)
```

## How It Works

```
┌─────────────────────────────────────────────────────────────────┐
│                     MEMORY GRAPH (JSON)                          │
│  Nodes: Files, Functions, Bugs, Vulnerabilities, Patterns       │
│  Edges: causes, fixed_by, similar_to, affects                   │
│  All wizards read/write to this shared knowledge base           │
└─────────────────────────────────────────────────────────────────┘
```

The graph is stored as JSON in `patterns/memory_graph.json` and persists across sessions.

## Node Types

```python
from empathy_os.memory import NodeType

class NodeType(Enum):
    FILE = "file"
    FUNCTION = "function"
    CLASS = "class"
    BUG = "bug"
    VULNERABILITY = "vulnerability"
    PERFORMANCE_ISSUE = "performance_issue"
    PATTERN = "pattern"
    FIX = "fix"
    TEST = "test"
```

## Edge Types

```python
from empathy_os.memory import EdgeType

class EdgeType(Enum):
    CAUSES = "causes"           # Bug A causes Bug B
    FIXED_BY = "fixed_by"       # Bug fixed by a commit
    SIMILAR_TO = "similar_to"   # Similar issues
    AFFECTS = "affects"         # Issue affects file/function
    CONTAINS = "contains"       # File contains function
    DEPENDS_ON = "depends_on"   # Module dependencies
    TESTED_BY = "tested_by"     # Code tested by test file
```

## Adding Findings

Any wizard can add findings to the graph:

```python
# Security wizard finds vulnerability
vuln_id = graph.add_finding(
    wizard="security-audit",
    finding={
        "type": "vulnerability",
        "name": "SQL Injection in user_query()",
        "severity": "critical",
        "cwe": "CWE-89",
        "file": "src/database.py",
        "line": 42
    }
)

# Performance wizard finds hotspot
perf_id = graph.add_finding(
    wizard="perf-audit",
    finding={
        "type": "performance_issue",
        "name": "N+1 query in get_users()",
        "impact": "high",
        "file": "src/users.py"
    }
)
```

## Connecting Nodes

Create relationships between findings:

```python
# Bug causes another bug
graph.add_edge(root_cause_id, symptom_id, EdgeType.CAUSES)

# Vulnerability fixed by commit
graph.add_edge(vuln_id, fix_id, EdgeType.FIXED_BY)

# Issue affects multiple files
graph.add_edge(issue_id, file1_id, EdgeType.AFFECTS)
graph.add_edge(issue_id, file2_id, EdgeType.AFFECTS)

# Function tested by test file
graph.add_edge(function_id, test_id, EdgeType.TESTED_BY)
```

## Finding Similar Issues

Find issues similar to a new finding:

```python
similar = graph.find_similar(
    finding={"name": "Null reference error in parser"},
    threshold=0.8  # Similarity threshold (0.0-1.0)
)

for node in similar:
    print(f"Similar: {node.name} (score: {node.similarity})")
    # Check if there's a fix
    fixes = graph.find_related(node.id, [EdgeType.FIXED_BY])
    if fixes:
        print(f"  Fixed by: {fixes[0].name}")
```

## Traversing Relationships

Find connected nodes:

```python
# Find all bugs fixed by a developer's commits
fixes = graph.find_related(
    node_id=bug_id,
    edge_types=[EdgeType.FIXED_BY]
)

# Find root causes of an issue
causes = graph.find_related(
    node_id=symptom_id,
    edge_types=[EdgeType.CAUSES]
)

# Find all affected files
affected = graph.find_related(
    node_id=vulnerability_id,
    edge_types=[EdgeType.AFFECTS]
)
```

## Statistics

Get graph statistics:

```python
stats = graph.get_statistics()
print(f"Total nodes: {stats['node_count']}")
print(f"Total edges: {stats['edge_count']}")
print(f"By type: {stats['nodes_by_type']}")
# {
#     "bug": 42,
#     "fix": 38,
#     "vulnerability": 12,
#     "performance_issue": 8
# }
```

## Cross-Wizard Intelligence

The Memory Graph enables wizards to learn from each other:

```python
# Security wizard checks if similar vulnerabilities exist
def check_known_vulnerabilities(finding):
    similar = graph.find_similar(finding)
    for node in similar:
        fixes = graph.find_related(node.id, [EdgeType.FIXED_BY])
        if fixes:
            return {
                "known_issue": True,
                "previous_fix": fixes[0].name,
                "recommendation": "Apply similar fix pattern"
            }
    return {"known_issue": False}

# Bug predict wizard uses historical data
def predict_related_bugs(new_bug):
    similar = graph.find_similar(new_bug)
    cascading = []
    for node in similar:
        caused = graph.find_related(node.id, [EdgeType.CAUSES])
        cascading.extend(caused)
    return cascading
```

## Persistence

The graph auto-saves to disk:

```python
# Default location
graph = MemoryGraph()  # patterns/memory_graph.json

# Custom location
graph = MemoryGraph(path="./my_project/knowledge.json")

# Manual save
graph.save()

# Manual load
graph.load()
```

## See Also

- [Smart Router](smart-router.md) - Natural language wizard dispatch
- [Auto-Chaining](auto-chaining.md) - Automatic wizard sequencing
- [API Reference](../API_REFERENCE.md#memorygraph) - Full API documentation
