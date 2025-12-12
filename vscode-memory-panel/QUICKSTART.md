# Quick Start Guide

Get the Empathy Memory Panel running in 5 minutes.

## Step 1: Start the Backend API

```bash
# Navigate to the extension directory
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/vscode-memory-panel

# Install Python dependencies (if not already installed)
pip install fastapi uvicorn

# Start the API server
python api_server_example.py
```

You should see:
```
============================================================
Empathy Memory Panel API Server
============================================================

Starting server on http://localhost:8765
Press Ctrl+C to stop

API Documentation: http://localhost:8765/docs
Health Check: http://localhost:8765/api/ping
============================================================
```

## Step 2: Install the Extension

### Option A: Install from VSIX (recommended)

```bash
# Build the extension
npm install
npm run compile
npm run package

# Install in VS Code
code --install-extension empathy-memory-panel-1.0.0.vsix
```

### Option B: Run in Development Mode

1. Open `/Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/vscode-memory-panel` in VS Code
2. Press `F5` to launch Extension Development Host
3. A new VS Code window will open with the extension loaded

## Step 3: Open the Memory Panel

In VS Code:
1. Click the Empathy Memory icon in the Activity Bar (left sidebar)
2. Or press `Ctrl+Shift+P` and type "Empathy Memory: Show Panel"

## Step 4: Verify Connection

The panel should display:
- Redis status (may show "Stopped" initially)
- Memory statistics
- Pattern library section

If you see "Connection Error", verify:
- API server is running on port 8765
- No firewall blocking localhost:8765
- Check API server terminal for errors

## Step 5: Start Redis (if needed)

If Redis shows as "Stopped":
1. Click the "Start Redis" button
2. The panel will attempt to start Redis automatically
3. Status should change to "Running"

## Common Issues

### "Cannot connect to Memory API"
- **Solution**: Make sure `python api_server_example.py` is running
- **Test**: Open http://localhost:8765/api/ping in browser

### "Redis won't start"
- **Solution**: Install Redis first:
  - macOS: `brew install redis`
  - Ubuntu: `sudo apt install redis-server`
  - Windows: Use Docker or WSL

### Extension not showing in Activity Bar
- **Solution**: Reload VS Code window
  - `Ctrl+Shift+P` > "Developer: Reload Window"

### TypeScript compilation errors
- **Solution**:
  ```bash
  rm -rf node_modules package-lock.json
  npm install
  npm run compile
  ```

## Next Steps

- **View Patterns**: Click "View" in the Pattern Library section
- **Health Check**: Click "Run Check" to verify system health
- **Export Data**: Use "Export" to save patterns to JSON
- **Auto-refresh**: Enable in settings for real-time updates

## Configuration

Open VS Code Settings (`Ctrl+,`) and search for "Empathy Memory":

```json
{
  "empathyMemory.apiHost": "localhost",
  "empathyMemory.apiPort": 8765,
  "empathyMemory.autoRefresh": true,
  "empathyMemory.autoRefreshInterval": 30
}
```

## Development

For active development:

```bash
# Terminal 1: API Server
python api_server_example.py

# Terminal 2: TypeScript Watch
npm run watch

# VS Code: Press F5 to launch Extension Development Host
```

## Support

- Full documentation: [README.md](./README.md)
- API docs: http://localhost:8765/docs (when server is running)
- Issues: https://github.com/your-org/empathy-framework/issues
