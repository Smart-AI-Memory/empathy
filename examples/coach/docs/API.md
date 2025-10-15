# Coach LSP Protocol API Reference

Technical specification for the Coach Language Server Protocol implementation.

**Built on LSP** with custom Coach extensions for wizard orchestration.

---

## Table of Contents

- [Overview](#overview)
- [Connection & Lifecycle](#connection--lifecycle)
- [Standard LSP Methods](#standard-lsp-methods)
- [Custom Coach Methods](#custom-coach-methods)
- [Data Structures](#data-structures)
- [Error Codes](#error-codes)
- [Examples](#examples)

---

## Overview

### Protocol

Coach uses the **Language Server Protocol (LSP)** for communication between IDEs and the Python backend.

**Transport**: stdio (standard input/output)
**Format**: JSON-RPC 2.0
**Encoding**: UTF-8

### Architecture

```
┌─────────────────────────────────────────────────┐
│         IDE (VS Code / JetBrains)               │
│  ┌──────────────────────────────────────────┐  │
│  │      LSP Client (TypeScript/Kotlin)      │  │
│  └─────────────────┬────────────────────────┘  │
└────────────────────┼────────────────────────────┘
                     │
                     │ JSON-RPC 2.0 over stdio
                     │
┌────────────────────▼────────────────────────────┐
│         Coach LSP Server (Python)               │
│  ┌──────────────────────────────────────────┐  │
│  │  pygls (LSP library)                     │  │
│  │  ├─ Standard LSP handlers                │  │
│  │  └─ Custom Coach handlers                │  │
│  └─────────────────┬────────────────────────┘  │
│                    │                            │
│  ┌─────────────────▼────────────────────────┐  │
│  │  16 Wizards (LangChain)                  │  │
│  │  - SecurityWizard                        │  │
│  │  - PerformanceWizard                     │  │
│  │  - ... (14 more)                         │  │
│  └──────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

### Version

- **LSP Version**: 3.17
- **Coach API Version**: 0.1.0
- **pygls Version**: 1.3.0+

---

## Connection & Lifecycle

### Initialize

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "processId": 12345,
    "rootUri": "file:///path/to/project",
    "capabilities": {
      "textDocument": {
        "diagnostic": {},
        "codeAction": {},
        "hover": {}
      }
    }
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "capabilities": {
      "textDocumentSync": {
        "openClose": true,
        "change": 2,
        "save": {
          "includeText": true
        }
      },
      "diagnosticProvider": {
        "interFileDependencies": false,
        "workspaceDiagnostics": false
      },
      "codeActionProvider": {
        "codeActionKinds": ["quickfix", "refactor"]
      },
      "hoverProvider": true,
      "executeCommandProvider": {
        "commands": [
          "coach/runWizard",
          "coach/multiWizardReview",
          "coach/predict",
          "coach/healthCheck"
        ]
      }
    },
    "serverInfo": {
      "name": "Coach Language Server",
      "version": "0.1.0"
    }
  }
}
```

### Initialized

**Notification** (client → server):
```json
{
  "jsonrpc": "2.0",
  "method": "initialized",
  "params": {}
}
```

### Shutdown

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "shutdown",
  "params": null
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": null
}
```

### Exit

**Notification**:
```json
{
  "jsonrpc": "2.0",
  "method": "exit",
  "params": null
}
```

---

## Standard LSP Methods

### textDocument/didOpen

**Notification** (client → server):
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didOpen",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py",
      "languageId": "python",
      "version": 1,
      "text": "def vulnerable():\n    user_id = input()\n    query = f\"SELECT * FROM users WHERE id={user_id}\""
    }
  }
}
```

**Server Action**:
- Analyzes file content
- Runs applicable wizards (SecurityWizard, PerformanceWizard, etc.)
- Publishes diagnostics if issues found

### textDocument/didChange

**Notification** (client → server):
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didChange",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py",
      "version": 2
    },
    "contentChanges": [
      {
        "text": "def vulnerable():\n    user_id = input()\n    query = \"SELECT * FROM users WHERE id=?\"\n    cursor.execute(query, (user_id,))"
      }
    ]
  }
}
```

**Server Action**:
- Updates document state
- Re-analyzes content (debounced)
- Publishes updated diagnostics

### textDocument/didSave

**Notification** (client → server):
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didSave",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py"
    },
    "text": "# Full file content..."
  }
}
```

**Server Action**:
- Triggers full analysis (not debounced)
- Runs all applicable wizards

### textDocument/didClose

**Notification** (client → server):
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/didClose",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py"
    }
  }
}
```

**Server Action**:
- Cleans up document state
- Clears diagnostics for this file

### textDocument/publishDiagnostics

**Notification** (server → client):
```json
{
  "jsonrpc": "2.0",
  "method": "textDocument/publishDiagnostics",
  "params": {
    "uri": "file:///path/to/file.py",
    "version": 2,
    "diagnostics": [
      {
        "range": {
          "start": {"line": 2, "character": 4},
          "end": {"line": 2, "character": 50}
        },
        "severity": 1,
        "code": "SQL_INJECTION",
        "source": "coach.security",
        "message": "Potential SQL injection vulnerability - use parameterized queries",
        "tags": [],
        "data": {
          "wizard": "SecurityWizard",
          "confidence": 0.95,
          "fixAvailable": true
        }
      }
    ]
  }
}
```

**Severity Levels**:
- `1` = Error (red)
- `2` = Warning (yellow)
- `3` = Information (blue)
- `4` = Hint (gray)

### textDocument/codeAction

**Request** (client → server):
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "textDocument/codeAction",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py"
    },
    "range": {
      "start": {"line": 2, "character": 4},
      "end": {"line": 2, "character": 50}
    },
    "context": {
      "diagnostics": [
        {
          "range": {...},
          "severity": 1,
          "code": "SQL_INJECTION",
          "source": "coach.security",
          "message": "Potential SQL injection vulnerability"
        }
      ],
      "triggerKind": 2
    }
  }
}
```

**Response** (server → client):
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": [
    {
      "title": "🛡️ SecurityWizard: Use parameterized query",
      "kind": "quickfix",
      "diagnostics": [{"range": {...}, "code": "SQL_INJECTION"}],
      "isPreferred": true,
      "edit": {
        "changes": {
          "file:///path/to/file.py": [
            {
              "range": {
                "start": {"line": 2, "character": 4},
                "end": {"line": 2, "character": 50}
              },
              "newText": "query = \"SELECT * FROM users WHERE id=?\"\n    cursor.execute(query, (user_id,))"
            }
          ]
        }
      }
    },
    {
      "title": "Run full security audit",
      "kind": "source.fixAll",
      "command": {
        "title": "Run SecurityWizard",
        "command": "coach/runWizard",
        "arguments": ["SecurityWizard", {"task": "full security audit"}]
      }
    }
  ]
}
```

### textDocument/hover

**Request** (client → server):
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "method": "textDocument/hover",
  "params": {
    "textDocument": {
      "uri": "file:///path/to/file.py"
    },
    "position": {
      "line": 10,
      "character": 15
    }
  }
}
```

**Response** (server → client):
```json
{
  "jsonrpc": "2.0",
  "id": 4,
  "result": {
    "contents": {
      "kind": "markdown",
      "value": "### ⚠️ PerformanceWizard Prediction (Level 4)\n\n**Current**: 10 connections\n\n**Prediction**: At 5K req/day growth rate, this connection pool will saturate in **~45 days**\n\n**Impact**:\n- 503 Service Unavailable errors\n- Request timeouts\n- Cascade failures\n\n**Preventive Action**:\n```python\npool_size = 50\n```\n\n[Run Full Analysis](command:coach.performanceProfile)"
    },
    "range": {
      "start": {"line": 10, "character": 0},
      "end": {"line": 10, "character": 20}
    }
  }
}
```

---

## Custom Coach Methods

### coach/runWizard

Run a specific wizard on code.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "method": "workspace/executeCommand",
  "params": {
    "command": "coach/runWizard",
    "arguments": [
      "SecurityWizard",
      {
        "role": "developer",
        "task": "Analyze authentication flow",
        "context": "Payment processing system",
        "preferences": "Focus on OWASP Top 10",
        "riskTolerance": "medium"
      }
    ]
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "result": {
    "routing": ["SecurityWizard"],
    "primaryOutput": {
      "wizard": "SecurityWizard",
      "diagnosis": "Found 3 security issues:\n1. SQL injection on line 42\n2. Hardcoded API key on line 67\n3. Missing input validation on line 89",
      "recommendations": [
        "Use parameterized queries for database access",
        "Store API keys in environment variables",
        "Add input validation using Pydantic or similar"
      ],
      "predictedImpact": {
        "timeline": "30 days",
        "severity": "high",
        "affectedAreas": ["authentication", "database", "api"]
      },
      "codeExamples": [
        {
          "language": "python",
          "code": "# Before\nquery = f\"SELECT * FROM users WHERE id={user_id}\"\n\n# After\nquery = \"SELECT * FROM users WHERE id=?\"\ncursor.execute(query, (user_id,))",
          "explanation": "Parameterized queries prevent SQL injection"
        }
      ],
      "confidence": 0.95
    },
    "supplementalOutputs": [],
    "collaboration": {
      "consultedWizards": [],
      "consensusAreas": [],
      "disagreements": []
    },
    "overallConfidence": 0.95,
    "executionTimeMs": 2345,
    "cacheHit": false
  }
}
```

**Arguments**:
- `wizardName` (string, required): Name of wizard to run
- `options` (object, optional):
  - `role` (string): User role (default: "developer")
  - `task` (string): Specific task description
  - `context` (string): Additional context
  - `preferences` (string): User preferences
  - `riskTolerance` (string): "low" | "medium" | "high"

### coach/multiWizardReview

Run multi-wizard analysis for complex scenarios.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "method": "workspace/executeCommand",
  "params": {
    "command": "coach/multiWizardReview",
    "arguments": [
      "new_api_endpoint",
      [
        "src/api/orders.py",
        "src/models/order.py"
      ]
    ]
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 6,
  "result": {
    "routing": [
      "APIWizard",
      "SecurityWizard",
      "PerformanceWizard",
      "DatabaseWizard",
      "TestingWizard"
    ],
    "primaryOutput": {
      "wizard": "APIWizard",
      "diagnosis": "RESTful endpoint design review:\n- Endpoint structure is correct\n- Missing pagination\n- No rate limiting\n- OpenAPI spec needs updating",
      "recommendations": [
        "Add pagination with page/limit parameters",
        "Implement rate limiting (100 req/min per user)",
        "Update OpenAPI spec with new endpoint"
      ],
      "confidence": 0.88
    },
    "supplementalOutputs": [
      {
        "wizard": "SecurityWizard",
        "diagnosis": "Authentication required for this endpoint",
        "recommendations": ["Add @require_auth decorator"],
        "confidence": 0.92
      },
      {
        "wizard": "PerformanceWizard",
        "diagnosis": "Potential N+1 query in order fetching",
        "recommendations": ["Use select_related('customer', 'items')"],
        "confidence": 0.85
      }
    ],
    "collaboration": {
      "consultedWizards": [
        "SecurityWizard",
        "PerformanceWizard",
        "DatabaseWizard",
        "TestingWizard"
      ],
      "consensusAreas": [
        "Endpoint needs authentication",
        "Pagination is required",
        "N+1 query should be fixed"
      ],
      "disagreements": [
        {
          "topic": "Rate limiting strictness",
          "positions": {
            "SecurityWizard": "50 req/min (strict)",
            "APIWizard": "100 req/min (lenient)"
          }
        }
      ]
    },
    "overallConfidence": 0.87,
    "executionTimeMs": 8932,
    "cacheHit": false
  }
}
```

**Arguments**:
- `scenario` (string, required): Scenario name
  - `"new_api_endpoint"`
  - `"database_migration"`
  - `"production_incident"`
  - `"new_feature_launch"`
  - `"performance_issue"`
  - `"compliance_audit"`
  - `"global_expansion"`
  - `"code_review"`
- `files` (array of strings): Files to analyze

### coach/predict

Get Level 4 prediction for code.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "method": "workspace/executeCommand",
  "params": {
    "command": "coach/predict",
    "arguments": [
      {
        "code": "pool_size = 10",
        "context": "Connection pool for PostgreSQL database",
        "language": "python",
        "timelineDays": 90
      }
    ]
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 7,
  "result": {
    "wizard": "PerformanceWizard",
    "prediction": "Connection pool saturation predicted in ~45 days...",
    "timelineDays": 90,
    "milestones": [
      {
        "day": 30,
        "event": "50% pool utilization",
        "impact": "Occasional slow queries"
      },
      {
        "day": 40,
        "event": "90% pool utilization",
        "impact": "Frequent timeouts"
      },
      {
        "day": 45,
        "event": "100% pool saturation",
        "impact": "Service outage"
      }
    ],
    "preventiveActions": [
      "Increase pool_size to 50 within 30 days",
      "Add connection pool monitoring",
      "Set up alerts at 80% utilization"
    ],
    "confidence": 0.78
  }
}
```

**Arguments**:
- `code` (string, required): Code snippet to analyze
- `context` (string): Additional context
- `language` (string): Programming language
- `timelineDays` (number): Prediction timeline (default: 90)

### coach/healthCheck

Check server health and wizard availability.

**Request**:
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "method": "workspace/executeCommand",
  "params": {
    "command": "coach/healthCheck",
    "arguments": []
  }
}
```

**Response**:
```json
{
  "jsonrpc": "2.0",
  "id": 8,
  "result": {
    "status": "healthy",
    "timestamp": "2025-01-15T10:30:00Z",
    "serverVersion": "0.1.0",
    "pythonVersion": "3.12.0",
    "langchainVersion": "0.1.0",
    "wizardsLoaded": 16,
    "wizards": [
      {"name": "SecurityWizard", "status": "ready"},
      {"name": "PerformanceWizard", "status": "ready"},
      {"name": "AccessibilityWizard", "status": "ready"},
      {"name": "DebuggingWizard", "status": "ready"},
      {"name": "TestingWizard", "status": "ready"},
      {"name": "RefactoringWizard", "status": "ready"},
      {"name": "DatabaseWizard", "status": "ready"},
      {"name": "APIWizard", "status": "ready"},
      {"name": "ScalingWizard", "status": "ready"},
      {"name": "ObservabilityWizard", "status": "ready"},
      {"name": "CICDWizard", "status": "ready"},
      {"name": "DocumentationWizard", "status": "ready"},
      {"name": "ComplianceWizard", "status": "ready"},
      {"name": "MigrationWizard", "status": "ready"},
      {"name": "MonitoringWizard", "status": "ready"},
      {"name": "LocalizationWizard", "status": "ready"}
    ],
    "cacheStats": {
      "entries": 42,
      "hitRate": 0.73,
      "memoryUsageMB": 124.5
    },
    "llmProvider": "openai",
    "llmModel": "gpt-4"
  }
}
```

---

## Data Structures

### WizardResult

```typescript
interface WizardResult {
  wizard: string;                    // Wizard name
  diagnosis: string;                 // Main analysis text
  recommendations: string[];         // Actionable recommendations
  predictedImpact?: PredictedImpact; // Optional impact prediction
  codeExamples?: CodeExample[];      // Optional code examples
  confidence: number;                // 0.0 - 1.0
}
```

### PredictedImpact

```typescript
interface PredictedImpact {
  timeline: string;        // e.g., "30 days", "3 months"
  severity: string;        // "low", "medium", "high", "critical"
  affectedAreas: string[]; // e.g., ["authentication", "database"]
}
```

### CodeExample

```typescript
interface CodeExample {
  language: string;     // e.g., "python", "javascript"
  code: string;         // Code snippet
  explanation: string;  // Why this is better
}
```

### CollaborationInfo

```typescript
interface CollaborationInfo {
  consultedWizards: string[];  // Wizards that were consulted
  consensusAreas: string[];    // Areas where wizards agree
  disagreements: Disagreement[]; // Areas of disagreement
}
```

### Disagreement

```typescript
interface Disagreement {
  topic: string;                    // What they disagree about
  positions: Record<string, string>; // wizard_name: position
}
```

### Diagnostic

```typescript
interface Diagnostic {
  range: Range;
  severity: 1 | 2 | 3 | 4;  // Error, Warning, Information, Hint
  code?: string;             // e.g., "SQL_INJECTION"
  source?: string;           // e.g., "coach.security"
  message: string;
  tags?: DiagnosticTag[];
  relatedInformation?: DiagnosticRelatedInformation[];
  data?: any;                // Custom data
}
```

### Range

```typescript
interface Range {
  start: Position;
  end: Position;
}

interface Position {
  line: number;      // 0-indexed
  character: number; // 0-indexed
}
```

---

## Error Codes

### Standard JSON-RPC Errors

| Code | Name | Description |
|------|------|-------------|
| -32700 | Parse error | Invalid JSON |
| -32600 | Invalid Request | Invalid JSON-RPC |
| -32601 | Method not found | Method doesn't exist |
| -32602 | Invalid params | Invalid parameters |
| -32603 | Internal error | Internal JSON-RPC error |

### Custom Coach Errors

| Code | Name | Description |
|------|------|-------------|
| -32000 | WizardNotFound | Wizard doesn't exist |
| -32001 | WizardTimeout | Wizard execution timeout |
| -32002 | WizardError | Wizard execution error |
| -32003 | InvalidCode | Code parsing failed |
| -32004 | CacheError | Cache operation failed |
| -32005 | LLMError | LLM API error |

**Error Response Example**:
```json
{
  "jsonrpc": "2.0",
  "id": 5,
  "error": {
    "code": -32000,
    "message": "Wizard 'InvalidWizard' not found in registry",
    "data": {
      "availableWizards": ["SecurityWizard", "PerformanceWizard", "..."]
    }
  }
}
```

---

## Examples

### Example 1: Full Analysis Workflow

```typescript
// 1. Open file
client.sendNotification('textDocument/didOpen', {
  textDocument: {
    uri: 'file:///app/api.py',
    languageId: 'python',
    version: 1,
    text: fileContent
  }
});

// 2. Server analyzes and sends diagnostics
// (Automatic - no request needed)

// 3. User requests code action for diagnostic
const codeActions = await client.sendRequest('textDocument/codeAction', {
  textDocument: { uri: 'file:///app/api.py' },
  range: { start: {line: 42, character: 0}, end: {line: 42, character: 50} },
  context: {
    diagnostics: [diagnostic],
    triggerKind: 2
  }
});

// 4. User applies code action
// (IDE applies edit automatically)

// 5. User hovers over code
const hover = await client.sendRequest('textDocument/hover', {
  textDocument: { uri: 'file:///app/api.py' },
  position: { line: 10, character: 15 }
});

// 6. Display hover content
console.log(hover.contents.value);
```

### Example 2: Run SecurityWizard

```typescript
const result = await client.sendRequest('workspace/executeCommand', {
  command: 'coach/runWizard',
  arguments: [
    'SecurityWizard',
    {
      role: 'developer',
      task: 'Full security audit',
      context: 'E-commerce payment processing',
      riskTolerance: 'low'
    }
  ]
});

console.log(result.primaryOutput.diagnosis);
result.primaryOutput.recommendations.forEach(rec => {
  console.log(`- ${rec}`);
});
```

### Example 3: Multi-Wizard Review

```typescript
const result = await client.sendRequest('workspace/executeCommand', {
  command: 'coach/multiWizardReview',
  arguments: [
    'new_api_endpoint',
    ['src/api/orders.py', 'src/models/order.py']
  ]
});

console.log(`Primary: ${result.primaryOutput.wizard}`);
console.log(result.primaryOutput.diagnosis);

result.supplementalOutputs.forEach(output => {
  console.log(`\n${output.wizard}:`);
  console.log(output.diagnosis);
});

result.collaboration.disagreements.forEach(d => {
  console.log(`\nDisagreement on: ${d.topic}`);
  Object.entries(d.positions).forEach(([wizard, position]) => {
    console.log(`  ${wizard}: ${position}`);
  });
});
```

### Example 4: Level 4 Prediction

```typescript
const prediction = await client.sendRequest('workspace/executeCommand', {
  command: 'coach/predict',
  arguments: [{
    code: 'pool_size = 10',
    context: 'PostgreSQL connection pool',
    language: 'python',
    timelineDays: 90
  }]
});

console.log(prediction.prediction);
prediction.milestones.forEach(m => {
  console.log(`Day ${m.day}: ${m.event} → ${m.impact}`);
});

console.log('\nPreventive Actions:');
prediction.preventiveActions.forEach(action => {
  console.log(`- ${action}`);
});
```

### Example 5: Health Check

```typescript
const health = await client.sendRequest('workspace/executeCommand', {
  command: 'coach/healthCheck',
  arguments: []
});

console.log(`Status: ${health.status}`);
console.log(`Wizards loaded: ${health.wizardsLoaded}/16`);
console.log(`Cache hit rate: ${(health.cacheStats.hitRate * 100).toFixed(1)}%`);

health.wizards.forEach(w => {
  const status = w.status === 'ready' ? '✓' : '✗';
  console.log(`${status} ${w.name}`);
});
```

---

## Client Implementation

### VS Code TypeScript Client

```typescript
import {
  LanguageClient,
  LanguageClientOptions,
  ServerOptions,
  TransportKind
} from 'vscode-languageclient/node';

const serverOptions: ServerOptions = {
  command: 'python3',
  args: ['-m', 'lsp.server'],
  options: {
    cwd: workspaceFolder,
    env: process.env
  }
};

const clientOptions: LanguageClientOptions = {
  documentSelector: [
    { scheme: 'file', language: 'python' },
    { scheme: 'file', language: 'javascript' },
    { scheme: 'file', language: 'typescript' }
  ],
  synchronize: {
    fileEvents: vscode.workspace.createFileSystemWatcher('**/*.{py,js,ts}')
  }
};

const client = new LanguageClient(
  'coach',
  'Coach Language Server',
  serverOptions,
  clientOptions
);

await client.start();
```

### JetBrains Kotlin Client

```kotlin
import org.eclipse.lsp4j.*
import org.eclipse.lsp4j.launch.LSPLauncher
import org.eclipse.lsp4j.services.LanguageServer

val processBuilder = ProcessBuilder(
    "python3", "-m", "lsp.server"
).apply {
    directory(File(projectPath))
}

val process = processBuilder.start()

val launcher = LSPLauncher.createClientLauncher(
    client,
    process.inputStream,
    process.outputStream
)

val server: LanguageServer = launcher.remoteProxy
launcher.startListening()

// Initialize
val initParams = InitializeParams().apply {
    processId = ProcessHandle.current().pid().toInt()
    rootUri = projectPath
    capabilities = ClientCapabilities()
}

val result = server.initialize(initParams).get(10, TimeUnit.SECONDS)
server.initialized(InitializedParams())
```

---

## Performance Considerations

### Caching

**Default TTL**: 5 minutes
**Cache Key**: Hash of (wizard_name, code, context)

**Configuration**:
```json
{
  "coach.enableCache": true,
  "coach.cacheTTL": 300
}
```

### Debouncing

**didChange events**: Debounced 500ms
**didSave events**: Not debounced (immediate)

### Timeouts

- **Wizard execution**: 30 seconds (configurable)
- **LLM API call**: 30 seconds
- **LSP request**: 10 seconds

### Rate Limiting

**Client-side**: Recommended 10 requests/second max
**Server-side**: No rate limiting (relies on LLM provider limits)

---

## Security

### Authentication

**LSP Connection**: No authentication (local stdio)
**LLM API**: Requires API key in environment variables

### Data Privacy

- **Code never leaves machine** (when using local LLM)
- **Logs do not contain code content** (only metadata)
- **Cache is local** (~/.coach/cache)

### Permissions

**Required**:
- Read access to project files
- Write access to ~/.coach directory
- Network access (for cloud LLM providers)

---

## Versioning

### Semantic Versioning

Coach follows SemVer: `MAJOR.MINOR.PATCH`

**Breaking changes**:
- Major version (1.0.0 → 2.0.0)
- Changes to LSP custom methods
- Changes to data structures

**New features**:
- Minor version (0.1.0 → 0.2.0)
- New wizards
- New LSP capabilities

**Bug fixes**:
- Patch version (0.1.0 → 0.1.1)
- Bug fixes
- Performance improvements

### Compatibility

**LSP Protocol**: Backward compatible within LSP 3.x
**Custom Methods**: Use feature detection (check `capabilities` in `initialize` response)

---

## Testing

### Integration Tests

```python
# tests/test_lsp.py

import pytest
from lsp.server import CoachLanguageServer

@pytest.mark.asyncio
async def test_runWizard_command():
    server = CoachLanguageServer()
    await server.initialize()

    result = await server.execute_command(
        command="coach/runWizard",
        arguments=["SecurityWizard", {"task": "Test"}]
    )

    assert result["routing"] == ["SecurityWizard"]
    assert result["overallConfidence"] > 0
```

### Client Tests

```typescript
// test/extension.test.ts

import * as assert from 'assert';
import { LanguageClient } from 'vscode-languageclient/node';

suite('LSP Client Tests', () => {
  test('Health check', async () => {
    const result = await client.sendRequest('workspace/executeCommand', {
      command: 'coach/healthCheck',
      arguments: []
    });

    assert.strictEqual(result.status, 'healthy');
    assert.strictEqual(result.wizardsLoaded, 16);
  });
});
```

---

## Resources

- **LSP Specification**: https://microsoft.github.io/language-server-protocol/
- **pygls Documentation**: https://pygls.readthedocs.io/
- **VS Code LSP Guide**: https://code.visualstudio.com/api/language-extensions/language-server-extension-guide
- **JetBrains LSP**: https://plugins.jetbrains.com/docs/intellij/language-server-protocol.html

---

**Built with** ❤️ **using LSP and LangChain**
