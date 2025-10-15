# Installation Guide

Complete installation instructions for Coach IDE integration.

**Built on LangChain** with extensible wizard framework.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Install Python Backend](#install-python-backend)
- [VS Code Extension](#vs-code-extension)
- [JetBrains Plugin](#jetbrains-plugin)
- [Verify Installation](#verify-installation)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Python 3.12+** - Coach LSP server requires Python 3.12 or later
- **pip** - Python package manager
- **Git** - For cloning repository (alpha testing)

### Recommended

- **Virtual environment tool** - `venv`, `conda`, or `poetry`
- **VS Code 1.85+** or **JetBrains IDE 2023.1+**

### Check Your Setup

```bash
# Check Python version
python3 --version  # Should be 3.12.0 or later

# Check pip
pip3 --version

# Check Git
git --version
```

---

## Install Python Backend

The Coach LSP server is the core backend that powers both VS Code and JetBrains integrations.

### Step 1: Clone Repository (Alpha Testers)

```bash
# Clone private alpha repository
git clone https://github.com/deepstudyai/coach-alpha.git
cd coach-alpha/examples/coach
```

**Public release users**: Install via pip (coming soon)
```bash
pip3 install coach-ai  # Not yet available
```

### Step 2: Create Virtual Environment

```bash
# Using venv (recommended)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Using conda
conda create -n coach python=3.12
conda activate coach
```

### Step 3: Install Dependencies

```bash
# Install Coach and all dependencies
pip3 install -r requirements.txt

# This installs:
# - LangChain (wizard framework)
# - pygls (LSP server library)
# - FastAPI (optional HTTP mode)
# - All 16 wizard dependencies
```

### Step 4: Verify Backend Installation

```bash
# Start LSP server in test mode
cd lsp
python3 -m lsp.server

# You should see:
# INFO:coach_lsp:Coach Language Server starting...
# INFO:coach_lsp:Server initialized with 16 wizards
# INFO:coach_lsp:Listening on stdio...
```

Press `Ctrl+C` to stop the server.

### Step 5: Configure Environment Variables (Optional)

```bash
# Create .env file for configuration
cat > .env <<EOF
# Coach Configuration
COACH_LOG_LEVEL=INFO
COACH_CACHE_TTL=300
COACH_ENABLE_TELEMETRY=false

# API Keys (optional - for cloud features)
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
EOF
```

---

## VS Code Extension

### Option 1: Install from VSIX (Alpha Testers)

1. **Download VSIX**
   ```bash
   # Build extension (alpha testers only)
   cd vscode-extension
   npm install
   npm run package
   # Creates: coach-0.1.0.vsix
   ```

2. **Install in VS Code**
   - Open VS Code
   - Press `Ctrl+Shift+P` (Cmd+Shift+P on Mac)
   - Type: "Extensions: Install from VSIX..."
   - Select `coach-0.1.0.vsix`

3. **Reload VS Code**
   - Press `Ctrl+Shift+P`
   - Type: "Developer: Reload Window"

### Option 2: Install from Marketplace (Coming Soon)

1. Open VS Code
2. Go to Extensions (`Ctrl+Shift+X`)
3. Search for "Coach AI"
4. Click "Install"

### Configure VS Code Extension

1. **Open Settings** (`Ctrl+,`)
2. Search for "Coach"
3. **Configure LSP Server Path**:
   ```json
   {
     "coach.lsp.serverPath": "/path/to/coach-alpha/examples/coach/lsp/server.py",
     "coach.lsp.pythonPath": "/path/to/venv/bin/python3",
     "coach.logLevel": "INFO",
     "coach.enableCache": true,
     "coach.cacheTTL": 300
   }
   ```

4. **Auto-Triggers** (optional):
   ```json
   {
     "coach.autoTriggers.onFileSave": true,
     "coach.autoTriggers.wizards": ["SecurityWizard", "PerformanceWizard"]
   }
   ```

### Verify VS Code Installation

1. **Open any Python/JavaScript/TypeScript file**

2. **Check Status Bar** - Bottom right should show:
   ```
   Coach: Ready ✓
   ```

3. **Test Quick Fix**:
   - Add this code to a Python file:
   ```python
   user_id = input("Enter user ID: ")
   query = f"SELECT * FROM users WHERE id={user_id}"
   ```
   - You should see a red squiggly line under the SQL query
   - Click the lightbulb icon
   - Select "🛡️ SecurityWizard: Use parameterized query"

4. **Test Hover Prediction**:
   - Add this code:
   ```python
   pool_size = 10
   ```
   - Hover over `pool_size`
   - You should see Level 4 prediction about connection pool saturation

5. **Test Command Palette**:
   - Press `Ctrl+Shift+P`
   - Type "Coach"
   - You should see all Coach commands

---

## JetBrains Plugin

Supports: **IntelliJ IDEA, PyCharm, WebStorm, GoLand, RubyMine, PHPStorm, Rider** (2023.1+)

### Option 1: Install from ZIP (Alpha Testers)

1. **Build Plugin**
   ```bash
   cd jetbrains-plugin
   ./gradlew buildPlugin
   # Creates: build/distributions/coach-0.1.0.zip
   ```

2. **Install in JetBrains IDE**
   - Open your JetBrains IDE (IntelliJ, PyCharm, etc.)
   - Go to: **File → Settings → Plugins** (Windows/Linux)
   - Or: **IntelliJ IDEA → Preferences → Plugins** (Mac)
   - Click gear icon ⚙️ → "Install Plugin from Disk..."
   - Select `coach-0.1.0.zip`
   - Click "OK"
   - Restart IDE

### Option 2: Install from Marketplace (Coming Soon)

1. Open Settings/Preferences
2. Go to **Plugins**
3. Search for "Coach AI"
4. Click "Install"
5. Restart IDE

### Configure JetBrains Plugin

1. **Open Settings/Preferences**
   - Windows/Linux: `Ctrl+Alt+S`
   - Mac: `Cmd+,`

2. **Navigate to**: **Tools → Coach**

3. **Configure LSP Server**:
   - **Python Path**: `/path/to/venv/bin/python3`
   - **Server Path**: `/path/to/coach-alpha/examples/coach/lsp/server.py`
   - **Auto-start Server**: ✓ (recommended)
   - **Log Level**: INFO

4. **Enable Inspections**:
   - Go to: **Editor → Inspections**
   - Expand **Coach** group
   - Enable:
     - ✓ Coach Security Analysis
     - ✓ Coach Performance Analysis
     - ✓ Coach Accessibility Analysis

### Verify JetBrains Installation

1. **Open any Python/JavaScript/TypeScript file**

2. **Check Status** - Bottom right should show:
   ```
   Coach LSP: Connected
   ```

3. **Test Inspection**:
   - Add this code to a Python file:
   ```python
   user_id = input("Enter user ID: ")
   query = f"SELECT * FROM users WHERE id={user_id}"
   ```
   - You should see a warning underline
   - Hover to see: "Potential SQL injection vulnerability"
   - Press `Alt+Enter` to see quick fixes

4. **Test Action**:
   - Right-click in editor
   - Select: **Coach → Security Audit**
   - Coach panel should open with analysis results

5. **Check Tool Window**:
   - View → Tool Windows → Coach
   - Should show "Coach: Ready" with wizard list

---

## Verify Installation

### Run Health Check

```bash
# From coach directory
python3 -c "
from lsp.server import CoachLanguageServer
import asyncio

async def health_check():
    server = CoachLanguageServer()
    print('✓ Server initialized')
    print(f'✓ {len(server.wizards)} wizards loaded')
    print('✓ Health check passed')

asyncio.run(health_check())
"
```

Expected output:
```
✓ Server initialized
✓ 16 wizards loaded
✓ Health check passed
```

### Test Individual Wizards

```bash
# Test SecurityWizard
python3 -c "
from coach.wizards.security import SecurityWizard
wizard = SecurityWizard()
print(f'✓ {wizard.name} loaded')
"

# Test all wizards
python3 scripts/test_wizards.py
```

### Test LSP Connection

```bash
# Start server
cd lsp
python3 -m lsp.server &
SERVER_PID=$!

# Send test request
echo '{"jsonrpc":"2.0","id":1,"method":"coach/healthCheck","params":[]}' | nc localhost 5007

# Stop server
kill $SERVER_PID
```

---

## Troubleshooting

### Common Issues

#### 1. "Coach LSP server failed to start"

**Cause**: Python version or missing dependencies

**Fix**:
```bash
# Check Python version
python3 --version  # Must be 3.12+

# Reinstall dependencies
pip3 install --upgrade -r requirements.txt

# Check for errors
python3 -m lsp.server --debug
```

#### 2. "Cannot find module 'langchain'"

**Cause**: Virtual environment not activated or missing LangChain

**Fix**:
```bash
# Activate venv
source venv/bin/activate

# Install LangChain
pip3 install langchain langchain-community langchain-openai

# Verify
python3 -c "import langchain; print(langchain.__version__)"
```

#### 3. "No wizards loaded"

**Cause**: Missing wizard dependencies or configuration

**Fix**:
```bash
# Check wizard directory
ls -la coach/wizards/

# Reinstall wizard dependencies
pip3 install -r coach/wizards/requirements.txt

# Test wizard import
python3 -c "from coach.wizards import get_all_wizards; print(len(get_all_wizards()))"
```

#### 4. VS Code: "Extension host terminated unexpectedly"

**Cause**: LSP server crash or path misconfiguration

**Fix**:
1. Check VS Code Output: **View → Output → Coach**
2. Verify server path in settings
3. Test server manually:
   ```bash
   python3 /path/to/lsp/server.py
   ```
4. Check logs:
   ```bash
   tail -f ~/.coach/logs/coach-lsp.log
   ```

#### 5. JetBrains: "Plugin 'Coach' failed to initialize"

**Cause**: Incompatible IDE version or missing dependencies

**Fix**:
1. Check IDE version: **Help → About** (must be 2023.1+)
2. Check idea.log:
   - **Help → Show Log in Finder/Explorer**
   - Search for "Coach" errors
3. Reinstall plugin:
   ```bash
   ./gradlew clean buildPlugin
   ```
4. Restart IDE with cleared caches:
   - **File → Invalidate Caches → Invalidate and Restart**

#### 6. "Predictions not showing on hover"

**Cause**: Hover provider not registered or LSP not connected

**Fix**:
- **VS Code**:
  ```json
  // settings.json
  {
    "coach.enableHoverPredictions": true
  }
  ```
- **JetBrains**: Check **Settings → Editor → General → Code Completion → Show documentation on hover**

#### 7. "Quick fixes not appearing"

**Cause**: Code actions provider not working

**Fix**:
- Ensure file is saved
- Check diagnostics are showing (squiggly lines)
- Try: Right-click → **Show Context Actions** (`Alt+Enter`)
- Restart IDE

### Getting Help

If you're still experiencing issues:

1. **Check Logs**:
   ```bash
   # LSP server logs
   tail -f ~/.coach/logs/coach-lsp.log

   # VS Code logs
   # Open: View → Output → Coach

   # JetBrains logs
   # Open: Help → Show Log in Finder/Explorer
   ```

2. **Enable Debug Mode**:
   ```bash
   # Start server in debug mode
   COACH_LOG_LEVEL=DEBUG python3 -m lsp.server
   ```

3. **Join Discord** (Alpha Testers):
   - [Coach Alpha Discord](https://discord.gg/coach-alpha)
   - #installation-help channel

4. **GitHub Issues**:
   - [Report Bug](https://github.com/deepstudyai/coach-alpha/issues/new?template=bug_report.md)
   - Include:
     - OS and version
     - IDE and version
     - Python version
     - Error logs
     - Steps to reproduce

5. **Email Support**:
   - support@deepstudyai.com
   - Include installation logs and error messages

---

## Next Steps

✅ Installation complete!

Now learn how to use Coach:

1. **[User Manual](USER_MANUAL.md)** - Complete guide to all 16 wizards
2. **[Wizards Reference](WIZARDS.md)** - Detailed wizard documentation
3. **[Custom Wizards](CUSTOM_WIZARDS.md)** - Build your own LangChain wizards
4. **[Troubleshooting](TROUBLESHOOTING.md)** - Common issues and solutions

---

**Questions?** Join the [Coach Discord](https://discord.gg/coach-alpha) or email support@deepstudyai.com

**Built with** ❤️ **using LangChain**
