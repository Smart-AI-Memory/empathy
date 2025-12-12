# Empathy Memory Panel for VS Code

Enterprise-grade memory system control panel for the Empathy Framework. Monitor Redis, manage patterns, and maintain system health directly from VS Code.

## Features

### Real-time Memory Monitoring
- **Redis Status**: View connection status, method (Homebrew, systemd, Docker, etc.), and server details
- **Memory Statistics**: Track keys, memory usage, and staged patterns in real-time
- **Auto-refresh**: Configurable automatic status updates (default: 30 seconds)

### Pattern Library Management
- **Browse Patterns**: View all stored patterns with classification badges
- **Filter by Classification**: Filter patterns by PUBLIC, INTERNAL, or SENSITIVE
- **Export Patterns**: Export pattern collections to JSON files
- **Classification Badges**: Visual indicators for security levels
  - GREEN (PUBLIC): Shareable patterns
  - YELLOW (INTERNAL): Proprietary patterns
  - RED (SENSITIVE): HIPAA/regulated patterns

### Redis Control
- **Start Redis**: Automatically start Redis using platform-specific methods
- **Stop Redis**: Gracefully stop Redis (if started by the panel)
- **Connection Monitoring**: Real-time connection status with detailed method information

### System Health
- **Health Checks**: Comprehensive system health analysis
- **Recommendations**: Actionable suggestions for system improvements
- **Status Indicators**: Visual health status (Healthy, Degraded, Unhealthy)

### Quick Actions
- **Clear Short-term Memory**: Remove all working memory keys
- **Refresh Status**: Manual status refresh
- **Pattern Operations**: Quick access to pattern management

## Installation

### Prerequisites
1. VS Code version 1.85.0 or higher
2. Empathy Framework Python backend running on localhost:8765
3. Node.js and npm (for development)

### From Source

```bash
# Clone the repository
cd /path/to/empathy-framework/vscode-memory-panel

# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Package extension
npm run package

# Install in VS Code
code --install-extension empathy-memory-panel-1.0.0.vsix
```

## Setup

### 1. Start the Python Backend

The extension requires the Memory Control Panel API server running on your machine:

```bash
# Navigate to Empathy Framework
cd /path/to/empathy-framework

# Start the API server (default port 8765)
python -m empathy_os.memory.api_server
```

Or create a simple API server wrapper:

```python
# api_server.py
from fastapi import FastAPI
from empathy_os.memory import MemoryControlPanel, ControlPanelConfig

app = FastAPI()
panel = MemoryControlPanel()

@app.get("/api/status")
async def get_status():
    return panel.status()

@app.get("/api/stats")
async def get_stats():
    return panel.get_statistics()

@app.post("/api/redis/start")
async def start_redis():
    status = panel.start_redis()
    return {"success": status.available, "message": status.message}

@app.post("/api/redis/stop")
async def stop_redis():
    success = panel.stop_redis()
    return {"success": success, "message": "Redis stopped" if success else "Could not stop Redis"}

@app.get("/api/patterns")
async def list_patterns(classification: str = None, limit: int = 100):
    patterns = panel.list_patterns(classification=classification, limit=limit)
    return patterns

@app.delete("/api/patterns/{pattern_id}")
async def delete_pattern(pattern_id: str):
    success = panel.delete_pattern(pattern_id)
    return {"success": success}

@app.get("/api/patterns/export")
async def export_patterns(classification: str = None):
    patterns = panel.list_patterns(classification=classification)
    return {
        "pattern_count": len(patterns),
        "export_data": {
            "patterns": patterns,
            "exported_at": panel.status()["timestamp"]
        }
    }

@app.get("/api/health")
async def health_check():
    return panel.health_check()

@app.post("/api/memory/clear")
async def clear_memory(body: dict):
    keys_deleted = panel.clear_short_term(body.get("agent_id", "admin"))
    return {"keys_deleted": keys_deleted}

@app.get("/api/ping")
async def ping():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8765)
```

Then run:
```bash
python api_server.py
```

### 2. Configure Extension (Optional)

Open VS Code Settings and configure:

```json
{
  "empathyMemory.apiHost": "localhost",
  "empathyMemory.apiPort": 8765,
  "empathyMemory.autoRefresh": true,
  "empathyMemory.autoRefreshInterval": 30,
  "empathyMemory.showNotifications": true
}
```

## Usage

### Opening the Panel

1. Click the Empathy Memory icon in the Activity Bar (left sidebar)
2. Or use Command Palette: `Ctrl+Shift+P` > "Empathy Memory: Show Panel"

### Quick Start

1. **Check Status**: The panel automatically loads status on open
2. **Start Redis** (if needed): Click "Start Redis" button
3. **View Patterns**: Select classification filter and click "View"
4. **Run Health Check**: Click "Run Check" to verify system health
5. **Export Data**: Use "Export" button to save patterns to JSON

### Common Tasks

#### Monitor Redis
- View real-time connection status in the Redis Status section
- See which method was used to start Redis (Homebrew, Docker, etc.)
- Check memory usage and key counts

#### Manage Patterns
```
1. Click "View" to load patterns
2. Use dropdown to filter by classification
3. Click "Export" to save to file
4. Patterns show: classification badge, type, ID, and metadata
```

#### Troubleshooting
```
1. Click "Health Check" button
2. Review status of Redis and storage
3. Follow recommendations if system is degraded
4. Check connection error messages at top of panel
```

## API Endpoints

The extension communicates with these backend endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | Get system status |
| `/api/stats` | GET | Get detailed statistics |
| `/api/redis/start` | POST | Start Redis |
| `/api/redis/stop` | POST | Stop Redis |
| `/api/patterns` | GET | List patterns |
| `/api/patterns/{id}` | DELETE | Delete pattern |
| `/api/patterns/export` | GET | Export patterns |
| `/api/health` | GET | Health check |
| `/api/memory/clear` | POST | Clear short-term memory |
| `/api/ping` | GET | Check API availability |

## Configuration

### Extension Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `empathyMemory.apiHost` | string | `localhost` | Memory API host |
| `empathyMemory.apiPort` | number | `8765` | Memory API port |
| `empathyMemory.autoRefresh` | boolean | `true` | Auto-refresh status |
| `empathyMemory.autoRefreshInterval` | number | `30` | Refresh interval (seconds) |
| `empathyMemory.showNotifications` | boolean | `true` | Show notifications |

### Backend Configuration

The Python backend can be configured via environment variables:

```bash
# Redis settings
export EMPATHY_REDIS_HOST=localhost
export EMPATHY_REDIS_PORT=6379

# Storage settings
export EMPATHY_STORAGE_DIR=./memdocs_storage
export EMPATHY_ENCRYPTION=true

# Environment
export EMPATHY_ENV=development
```

## Architecture

### Component Overview

```
vscode-memory-panel/
├── src/
│   ├── extension.ts              # Extension entry point
│   ├── services/
│   │   └── MemoryAPIService.ts   # HTTP client for backend
│   └── views/
│       └── MemoryPanelProvider.ts # Webview provider
├── webview/
│   ├── index.html                # Panel UI
│   └── styles.css                # UI styling
├── package.json                  # Extension manifest
└── tsconfig.json                 # TypeScript config
```

### Communication Flow

```
VS Code Extension (TypeScript)
    ↕ (Webview Messages)
MemoryPanelProvider
    ↕ (HTTP Requests)
MemoryAPIService
    ↕ (HTTP/JSON)
Python Backend API (localhost:8765)
    ↕
Memory Control Panel
    ↕
Redis + Long-term Storage
```

## Security

### Classification Levels

- **PUBLIC**: General-purpose patterns, shareable
- **INTERNAL**: Proprietary Empathy Framework patterns
- **SENSITIVE**: Healthcare patterns (HIPAA-regulated), encrypted

### Best Practices

1. **Never commit sensitive patterns** to version control
2. **Enable encryption** for SENSITIVE patterns
3. **Use appropriate classifications** when storing patterns
4. **Regular health checks** to verify encryption status
5. **Audit exports** before sharing pattern data

## Development

### Building from Source

```bash
# Install dependencies
npm install

# Compile TypeScript
npm run compile

# Watch mode (for development)
npm run watch

# Lint
npm run lint

# Package extension
npm run package
```

### Testing

```bash
# Run tests
npm test

# Test with VS Code extension host
# Press F5 in VS Code with extension open
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with proper TypeScript types
4. Add tests if applicable
5. Run `npm run lint` and fix any issues
6. Submit pull request

## Troubleshooting

### Extension Not Loading
- Check VS Code version (requires 1.85.0+)
- Reload window: `Ctrl+Shift+P` > "Developer: Reload Window"
- Check extension logs: `Ctrl+Shift+P` > "Developer: Show Logs"

### Cannot Connect to API
- Verify backend is running: `curl http://localhost:8765/api/ping`
- Check firewall settings
- Verify port 8765 is not in use: `lsof -i :8765` (macOS/Linux)
- Check extension settings for correct host/port

### Redis Won't Start
- Run `python -m empathy_os.memory.control_panel start` manually
- Check Redis installation: `redis-cli ping`
- Review health check recommendations
- Check logs in backend console

### Patterns Not Loading
- Verify storage directory exists
- Check file permissions on storage directory
- Run health check to verify storage status
- Check backend logs for errors

## Performance

- **Auto-refresh**: Configurable interval (5-300 seconds)
- **Request timeout**: 10 seconds default
- **Pattern list limit**: 100 patterns default
- **Memory usage**: Lightweight, ~5MB typical

## License

Copyright 2025 Smart AI Memory, LLC
Licensed under Fair Source 0.9

## Support

- Documentation: [Empathy Framework Docs](https://github.com/your-org/empathy-framework)
- Issues: [GitHub Issues](https://github.com/your-org/empathy-framework/issues)
- Email: support@empathyframework.com

## Changelog

### 1.0.0 (2025)
- Initial release
- Redis monitoring and control
- Pattern library management
- Health check system
- Auto-refresh capabilities
- Classification-based filtering
- Export functionality
- Modern UI with VS Code theme integration
