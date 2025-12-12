# Installation Guide

Complete installation instructions for the Empathy Memory Panel VS Code extension.

## Prerequisites

### Required
- **VS Code**: Version 1.85.0 or higher
- **Node.js**: Version 18 or higher
- **npm**: Usually comes with Node.js
- **Python**: Version 3.10 or higher (for backend)

### Optional
- **Redis**: For full functionality (can be auto-started)
- **Git**: For cloning repository

### Check Prerequisites

```bash
# Check versions
node --version     # Should be v18.0.0 or higher
npm --version      # Should be 9.0.0 or higher
python3 --version  # Should be 3.10.0 or higher
code --version     # Should be 1.85.0 or higher
```

## Installation Methods

### Method 1: Quick Install (Recommended)

```bash
# Navigate to extension directory
cd /Users/patrickroebuck/empathy_11_6_2025/Empathy-framework/vscode-memory-panel

# Make build script executable
chmod +x build.sh

# Run full build and install
./build.sh
./build.sh install

# Start backend server
python api_server_example.py
```

### Method 2: Manual Build

```bash
# 1. Install dependencies
npm install

# 2. Compile TypeScript
npm run compile

# 3. Package extension
npm run package

# 4. Install in VS Code
code --install-extension empathy-memory-panel-1.0.0.vsix
```

### Method 3: Development Mode

```bash
# 1. Install dependencies
npm install

# 2. Open in VS Code
code .

# 3. Press F5 to launch Extension Development Host
# A new VS Code window will open with the extension loaded

# 4. In separate terminal, start backend
python api_server_example.py
```

## Backend Setup

### Python Dependencies

```bash
# Install required packages
pip install fastapi uvicorn

# Or using requirements file (if available)
pip install -r requirements.txt
```

### Start Backend Server

```bash
# From extension directory
python api_server_example.py

# You should see:
# ============================================================
# Empathy Memory Panel API Server
# ============================================================
# Starting server on http://localhost:8765
```

### Verify Backend

```bash
# Test API endpoint
curl http://localhost:8765/api/ping

# Should return:
# {"status":"ok","service":"empathy-memory-panel"}
```

## Verify Installation

### 1. Check Extension Installed

In VS Code:
1. Open Extensions view (`Ctrl+Shift+X`)
2. Search for "Empathy Memory Panel"
3. Should show as installed

### 2. Open Memory Panel

1. Click Empathy Memory icon in Activity Bar (left sidebar)
2. Or press `Ctrl+Shift+P` and type "Empathy Memory: Show Panel"
3. Panel should open in sidebar

### 3. Check Connection

In the Memory Panel:
- Should show Redis status
- Should show Memory statistics
- If "Connection Error" appears, backend is not running

### 4. Test Functionality

1. Click "Refresh" button - status should update
2. If Redis not running, click "Start Redis"
3. Click "Health Check" to verify system

## Configuration

### VS Code Settings

Open Settings (`Ctrl+,`) and search for "Empathy Memory":

```json
{
  "empathyMemory.apiHost": "localhost",
  "empathyMemory.apiPort": 8765,
  "empathyMemory.autoRefresh": true,
  "empathyMemory.autoRefreshInterval": 30,
  "empathyMemory.showNotifications": true
}
```

### Custom API Port

If port 8765 is in use:

**Backend:**
```bash
# Start on different port
uvicorn api_server_example:app --host localhost --port 8766
```

**VS Code Settings:**
```json
{
  "empathyMemory.apiPort": 8766
}
```

## Redis Setup

### macOS

```bash
# Install via Homebrew
brew install redis

# Start Redis
brew services start redis

# Verify
redis-cli ping  # Should return "PONG"
```

### Ubuntu/Debian

```bash
# Install
sudo apt update
sudo apt install redis-server

# Start
sudo systemctl start redis-server

# Enable on boot
sudo systemctl enable redis-server

# Verify
redis-cli ping
```

### Windows

**Option 1: Docker (Recommended)**
```bash
docker run -d -p 6379:6379 --name empathy-redis redis:alpine
```

**Option 2: Chocolatey**
```bash
choco install redis-64
```

**Option 3: WSL**
```bash
wsl
sudo apt install redis-server
redis-server --daemonize yes
```

## Troubleshooting

### Extension Not Loading

**Problem**: Extension doesn't appear in Activity Bar

**Solution**:
```bash
# Reload VS Code window
Ctrl+Shift+P > "Developer: Reload Window"

# Check extension host log
Ctrl+Shift+P > "Developer: Show Logs" > "Extension Host"

# Reinstall extension
code --uninstall-extension deepstudyai.empathy-memory-panel
code --install-extension empathy-memory-panel-1.0.0.vsix
```

### Cannot Connect to API

**Problem**: "Connection Error" in panel

**Solution**:
```bash
# 1. Check if backend is running
curl http://localhost:8765/api/ping

# 2. Check if port is in use
lsof -i :8765  # macOS/Linux
netstat -ano | findstr :8765  # Windows

# 3. Check firewall settings
# Allow connections to localhost:8765

# 4. Restart backend
python api_server_example.py
```

### Redis Won't Start

**Problem**: "Start Redis" button doesn't work

**Solution**:
```bash
# 1. Check if Redis is installed
redis-cli --version

# 2. Try manual start
redis-server

# 3. Check if Redis is already running
redis-cli ping

# 4. Check Redis logs
# macOS: /usr/local/var/log/redis.log
# Linux: /var/log/redis/redis-server.log

# 5. Install Redis if missing (see Redis Setup above)
```

### Build Errors

**Problem**: TypeScript compilation errors

**Solution**:
```bash
# Clean and rebuild
./build.sh clean
npm install
npm run compile

# Check for missing dependencies
npm audit fix

# Update TypeScript
npm install typescript@latest --save-dev
```

### Permission Errors

**Problem**: Cannot write to directories

**Solution**:
```bash
# Fix permissions on extension directory
chmod -R u+w .

# Fix build script permissions
chmod +x build.sh

# Run with proper user (avoid sudo)
```

## Uninstallation

### Remove Extension

```bash
# Via CLI
code --uninstall-extension deepstudyai.empathy-memory-panel

# Or in VS Code
# Extensions > Empathy Memory Panel > Uninstall
```

### Clean Up

```bash
# Remove build artifacts
cd vscode-memory-panel
./build.sh clean

# Remove extension directory (optional)
rm -rf vscode-memory-panel
```

## Updating

### Update to New Version

```bash
# Pull latest code
git pull origin main

# Clean and rebuild
./build.sh clean
./build.sh

# Reinstall
./build.sh install

# Reload VS Code
Ctrl+Shift+P > "Developer: Reload Window"
```

## Getting Help

### Check Documentation
- [README.md](./README.md) - Full documentation
- [QUICKSTART.md](./QUICKSTART.md) - Quick setup guide
- [PROJECT_OVERVIEW.md](./PROJECT_OVERVIEW.md) - Technical details
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Development guide

### Common Issues
- Extension not loading → Reload window
- Connection error → Start backend
- Redis issues → Check Redis installation
- Build errors → Clean and rebuild

### Support Channels
- GitHub Issues: Report bugs and feature requests
- Documentation: Check all MD files in repository
- Logs: Check VS Code extension host logs

### Diagnostic Commands

```bash
# Check all prerequisites
node --version
npm --version
python3 --version
code --version
redis-cli --version

# Check running services
ps aux | grep redis
lsof -i :8765
curl http://localhost:8765/api/ping

# Check VS Code extensions
code --list-extensions | grep empathy

# Test backend directly
python3 -c "from empathy_os.memory import MemoryControlPanel; print('OK')"
```

## Next Steps

After successful installation:

1. **Open Panel**: Click Empathy Memory icon in Activity Bar
2. **Check Status**: Verify Redis and storage status
3. **Start Redis**: If needed, click "Start Redis"
4. **View Patterns**: Explore pattern library
5. **Health Check**: Run system health check
6. **Configure**: Adjust settings in VS Code preferences
7. **Read Docs**: Review [QUICKSTART.md](./QUICKSTART.md)

## Maintenance

### Regular Updates

```bash
# Update dependencies
npm update

# Update extension
git pull
./build.sh install
```

### Health Checks

- Run health check in panel weekly
- Review Redis memory usage
- Check storage directory size
- Monitor backend logs

### Backup

```bash
# Backup pattern storage
cp -r memdocs_storage memdocs_storage.backup

# Export patterns via panel
# Click "Export" button and save JSON
```

---

**Questions?** See [README.md](./README.md) or [QUICKSTART.md](./QUICKSTART.md)
