# Coach Language Server

Language Server Protocol (LSP) implementation for Coach IDE integration.

## Overview

The Coach Language Server provides a bridge between IDE extensions (VS Code, JetBrains) and the Coach engine with 16 specialized wizards. It implements the LSP protocol to enable features like:

- **Code Actions**: Quick fixes from SecurityWizard, PerformanceWizard, etc.
- **Hover Predictions**: Level 4 Anticipatory insights (30-90 day predictions)
- **Diagnostics**: Real-time issue detection
- **Custom Commands**: Direct wizard invocation from IDE

## Architecture

```
IDE Extension (TypeScript/Kotlin)
        ↓
  LSP Protocol (JSON-RPC)
        ↓
Coach Language Server (Python)
        ↓
Coach Engine + 16 Wizards
```

## Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python -m lsp.server
```

The server communicates over stdio (standard input/output) by default, which is the standard for LSP servers.

## Components

### `server.py`
Main LSP server implementation using `pygls` library. Handles:
- LSP protocol messages (textDocument/didOpen, didSave, etc.)
- Custom commands (coach/runWizard, coach/multiWizardReview, etc.)
- Code actions and hover providers
- Diagnostic publishing

### `context_collector.py`
Collects rich context from the IDE environment:
- File contents
- Git information (branch, status, recent commits)
- Project structure
- Dependencies (package.json, requirements.txt, etc.)

### `cache.py`
In-memory result cache with TTL (Time-To-Live):
- Caches wizard results for 5 minutes (configurable)
- Avoids redundant computations
- Automatically clears expired entries

## Custom LSP Commands

### `coach/runWizard`
Execute a specific wizard on demand.

**Parameters**:
```json
[
  "PerformanceWizard",
  {
    "role": "developer",
    "task": "Analyze database performance",
    "context": "API endpoint slow"
  }
]
```

**Returns**: Full wizard output with diagnosis and artifacts.

### `coach/multiWizardReview`
Run multi-wizard collaboration for complex scenarios.

**Parameters**:
```json
[
  "new_api_endpoint",
  ["file:///path/to/api.py", "file:///path/to/models.py"]
]
```

**Returns**: Orchestrated results from multiple wizards with synthesis.

### `coach/predict`
Get Level 4 Anticipatory prediction for specific context.

**Parameters**:
```json
["database_connection_pool", 10]
```

**Returns**: Prediction string with timeline and impact.

### `coach/healthCheck`
Verify server is running and get status.

**Parameters**: `[]`

**Returns**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "wizards": 16,
  "wizard_names": ["SecurityWizard", "PerformanceWizard", ...]
}
```

## LSP Features

### Text Document Synchronization
- `textDocument/didOpen`: Track opened files
- `textDocument/didChange`: Handle incremental updates, clear cache
- `textDocument/didSave`: Trigger background analysis

### Code Actions (Quick Fixes)
Provides actionable fixes from wizards:
- 🛡️ SecurityWizard: Fix SQL injection, XSS, etc.
- ⚡ PerformanceWizard: Optimize N+1 queries, inefficient algorithms
- ♿ AccessibilityWizard: Add ARIA labels, fix color contrast

### Hover Provider
Shows Level 4 predictions on hover:
- Database connection pool → "Will saturate in ~45 days"
- Rate limits → "Will be exceeded in ~60 days"
- Security patterns → "Potential SQL injection vulnerability"

### Diagnostics
Real-time issue detection published to IDE:
- **Error**: Critical security vulnerabilities
- **Warning**: Performance issues, code smells
- **Information**: Suggestions, best practices

## Configuration

Environment variables:
```bash
# Cache TTL in seconds (default: 300)
COACH_LSP_CACHE_TTL=300

# Log level (default: INFO)
COACH_LSP_LOG_LEVEL=DEBUG

# Enable/disable background analysis on file save
COACH_LSP_BACKGROUND_ANALYSIS=true
```

## Testing

```bash
# Run unit tests
pytest lsp/tests/

# Run with coverage
pytest --cov=lsp --cov-report=html lsp/tests/
```

## Integration with IDEs

### VS Code
See `../vscode-extension/` for VS Code extension that uses this server.

### JetBrains
See `../jetbrains-plugin/` for IntelliJ Platform plugin that uses this server.

## Performance

**Optimizations**:
- **Caching**: 5-minute TTL reduces redundant wizard invocations
- **Async**: Non-blocking wizard execution keeps IDE responsive
- **Incremental**: Only analyze changed files on save
- **Rate Limiting**: Max 1 wizard/second per file (configurable)

**Benchmarks** (on average workstation):
- Initial file analysis: ~500ms
- Cached result retrieval: <10ms
- Multi-wizard collaboration: ~1.5s
- Hover prediction: <50ms (pattern matching)

## Troubleshooting

### Server not starting
```bash
# Check dependencies
pip list | grep pygls

# Run with debug logging
COACH_LSP_LOG_LEVEL=DEBUG python -m lsp.server
```

### IDE not connecting
- Verify IDE extension is using correct stdio communication
- Check IDE extension logs for connection errors
- Ensure Python 3.12+ is in PATH

### Slow performance
- Check cache hit rate in logs
- Increase cache TTL: `COACH_LSP_CACHE_TTL=600`
- Disable background analysis on save (configure in IDE)

## Roadmap

- [ ] Redis-based distributed cache for teams
- [ ] WebSocket mode for web-based IDEs (GitHub Codespaces, GitPod)
- [ ] Performance profiling and optimization
- [ ] Support for incremental document updates (partial file changes)
- [ ] Configurable wizard selection per file type

## License

Apache License 2.0 - See LICENSE file in repository root.

## Support

- GitHub Issues: https://github.com/your-org/empathy-framework/issues
- Discord: https://discord.gg/coach-ai (alpha testers)
- Email: support@deepstudyai.com
