# Troubleshooting Guide

Solutions to common Coach issues and errors.

**Built on LangChain** - Many issues relate to LangChain configuration or LLM connectivity.

---

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Installation Issues](#installation-issues)
- [LSP Server Issues](#lsp-server-issues)
- [VS Code Extension Issues](#vs-code-extension-issues)
- [JetBrains Plugin Issues](#jetbrains-plugin-issues)
- [Wizard Issues](#wizard-issues)
- [Performance Issues](#performance-issues)
- [Network & API Issues](#network--api-issues)
- [Getting Help](#getting-help)

---

## Quick Diagnostics

### Run Health Check

```bash
# Check Coach installation
python3 -c "import coach; print(coach.__version__)"

# Check LangChain
python3 -c "import langchain; print(langchain.__version__)"

# Check LSP server
cd examples/coach/lsp
python3 -m lsp.server --health-check

# Expected output:
# ✓ Coach LSP Server v0.1.0
# ✓ 16 wizards loaded
# ✓ LangChain v0.1.0
# ✓ Python 3.12.0
# ✓ All systems operational
```

### Check Logs

```bash
# LSP server logs
tail -f ~/.coach/logs/coach-lsp.log

# VS Code logs
# Open: View → Output → Coach

# JetBrains logs
# Open: Help → Show Log in Finder/Explorer
# Search for: "Coach"
```

### Enable Debug Mode

```bash
# LSP server debug mode
COACH_LOG_LEVEL=DEBUG python3 -m lsp.server

# VS Code debug
# settings.json:
{
  "coach.logLevel": "DEBUG"
}

# JetBrains debug
# Settings → Tools → Coach → Log Level → DEBUG
```

---

## Installation Issues

### Issue 1: "Python version 3.12+ required"

**Error**:
```
ERROR: Coach requires Python 3.12 or later, found 3.10.0
```

**Cause**: Python version too old

**Fix**:
```bash
# Check Python version
python3 --version

# Install Python 3.12
# macOS (Homebrew):
brew install python@3.12

# Ubuntu/Debian:
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv

# Windows:
# Download from python.org

# Verify
python3.12 --version
```

---

### Issue 2: "Cannot find module 'langchain'"

**Error**:
```python
ModuleNotFoundError: No module named 'langchain'
```

**Cause**: LangChain not installed or wrong virtual environment

**Fix**:
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Verify venv is active (should show (venv) in prompt)
which python3  # Should show path to venv

# Install LangChain
pip3 install langchain langchain-community langchain-openai

# Verify installation
python3 -c "import langchain; print(langchain.__version__)"
```

---

### Issue 3: "Permission denied" when installing

**Error**:
```
ERROR: Could not install packages due to an OSError: [Errno 13] Permission denied
```

**Cause**: Trying to install system-wide without sudo

**Fix**:
```bash
# Option 1: Use virtual environment (RECOMMENDED)
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt

# Option 2: Install for user only
pip3 install --user -r requirements.txt

# Option 3: Use sudo (NOT RECOMMENDED)
sudo pip3 install -r requirements.txt
```

---

### Issue 4: "Wizard dependencies missing"

**Error**:
```
ImportError: SecurityWizard requires 'bandit' package
```

**Cause**: Some wizards have additional dependencies

**Fix**:
```bash
# Install all wizard dependencies
pip3 install -r coach/wizards/requirements.txt

# Or install specific wizard deps:
pip3 install bandit  # SecurityWizard
pip3 install pytest pytest-cov  # TestingWizard
pip3 install sqlparse  # DatabaseWizard
```

---

## LSP Server Issues

### Issue 5: "LSP server failed to start"

**Error** (VS Code):
```
Coach LSP server failed to start. Check logs for details.
```

**Error** (JetBrains):
```
CoachLSPException: Failed to start LSP server: [Errno 2] No such file or directory
```

**Cause**: Server path misconfigured or Python not found

**Fix**:

1. **Check server path**:
```bash
# Find server.py
find ~/projects -name "server.py" -path "*/lsp/*"

# Should find: /path/to/coach/lsp/server.py
```

2. **Update IDE settings**:

**VS Code** (`settings.json`):
```json
{
  "coach.lsp.serverPath": "/absolute/path/to/coach/lsp/server.py",
  "coach.lsp.pythonPath": "/absolute/path/to/venv/bin/python3"
}
```

**JetBrains** (Settings → Tools → Coach):
- Python Path: `/absolute/path/to/venv/bin/python3`
- Server Path: `/absolute/path/to/coach/lsp/server.py`

3. **Test server manually**:
```bash
cd /path/to/coach/lsp
python3 -m lsp.server

# Should output:
# INFO:coach_lsp:Coach Language Server starting...
# INFO:coach_lsp:Listening on stdio...
```

4. **Check permissions**:
```bash
chmod +x /path/to/coach/lsp/server.py
ls -l /path/to/coach/lsp/server.py
# Should show: -rwxr-xr-x
```

---

### Issue 6: "No wizards loaded"

**Error**:
```
WARNING: 0 wizards loaded (expected 16)
```

**Cause**: Wizard directory not found or import errors

**Fix**:

1. **Check wizard directory exists**:
```bash
ls -la coach/wizards/
# Should show: security.py, performance.py, etc.
```

2. **Test wizard imports**:
```python
python3 -c "from coach.wizards import get_all_wizards; print(len(get_all_wizards()))"
# Should output: 16
```

3. **Check for import errors**:
```python
python3 <<EOF
try:
    from coach.wizards.security import SecurityWizard
    print("✓ SecurityWizard imported")
except Exception as e:
    print(f"✗ SecurityWizard failed: {e}")
EOF
```

4. **Reinstall dependencies**:
```bash
pip3 install --force-reinstall -r coach/wizards/requirements.txt
```

---

### Issue 7: "LSP server crashes on startup"

**Error** (in logs):
```
Traceback (most recent call last):
  File "lsp/server.py", line 42, in main
    ...
KeyError: 'OPENAI_API_KEY'
```

**Cause**: Missing API key for LLM

**Fix**:

1. **Set API key**:
```bash
# Create .env file
cat > .env <<EOF
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # Optional
EOF

# Or export environment variable
export OPENAI_API_KEY="your_key_here"
```

2. **Use local model (no API key needed)**:
```bash
# Install Ollama
# macOS:
brew install ollama

# Start Ollama
ollama serve

# Pull model
ollama pull codellama

# Configure Coach to use Ollama
export COACH_LLM_PROVIDER=ollama
export COACH_LLM_MODEL=codellama
```

3. **Restart LSP server**:
```bash
# Kill existing server
pkill -f "lsp.server"

# Start new server
python3 -m lsp.server
```

---

### Issue 8: "LSP connection timeout"

**Error**:
```
TimeoutError: LSP server did not respond within 10 seconds
```

**Cause**: Server starting slowly or hung

**Fix**:

1. **Increase timeout**:

**VS Code** (`settings.json`):
```json
{
  "coach.lsp.timeout": 30000  // 30 seconds
}
```

**JetBrains** (Settings → Tools → Coach):
- Connection Timeout: 30 seconds

2. **Check server is responsive**:
```bash
# Send test request
echo '{"jsonrpc":"2.0","id":1,"method":"coach/healthCheck","params":[]}' | python3 -m lsp.server

# Should return JSON response within 2-3 seconds
```

3. **Check system resources**:
```bash
# Check CPU usage
top | grep python

# Check memory
free -h  # Linux
vm_stat  # macOS

# If resources are low, close other applications
```

---

## VS Code Extension Issues

### Issue 9: "Extension host terminated unexpectedly"

**Error**:
```
The extension 'Coach' has terminated unexpectedly 5 times in the last 5 minutes.
```

**Cause**: LSP server crashing repeatedly

**Fix**:

1. **Check VS Code Output**:
```
View → Output → Select "Coach" from dropdown
```

2. **Look for error pattern**:
```
# Common errors and fixes:

# Error: "ENOENT: no such file or directory"
# Fix: Check server path in settings

# Error: "ModuleNotFoundError"
# Fix: Activate virtual environment and reinstall

# Error: "OpenAI API error 429"
# Fix: Rate limit hit, wait or use different API key
```

3. **Disable extension, then re-enable**:
```
Extensions → Coach → Disable
Restart VS Code
Extensions → Coach → Enable
```

4. **Reinstall extension**:
```bash
# Remove extension
code --uninstall-extension deepstudyai.coach

# Reinstall from VSIX
code --install-extension coach-0.1.0.vsix
```

---

### Issue 10: "Diagnostics not showing"

**Error**: No red squiggly lines appear even with obvious issues

**Cause**: Diagnostics provider not registered or disabled

**Fix**:

1. **Check settings**:
```json
{
  "coach.enableDiagnostics": true,  // Make sure this is true
  "coach.diagnosticsDelay": 500     // Delay in ms (increase if too aggressive)
}
```

2. **Trigger manual analysis**:
```
Ctrl+Shift+P → "Coach: Analyze File"
```

3. **Check file type is supported**:
```json
{
  "coach.supportedLanguages": [
    "python",
    "javascript",
    "typescript",
    "typescriptreact",
    "javascriptreact"
  ]
}
```

4. **Check Problems panel**:
```
View → Problems
# Should show Coach diagnostics
```

5. **Reload window**:
```
Ctrl+Shift+P → "Developer: Reload Window"
```

---

### Issue 11: "Quick fixes not appearing"

**Error**: Lightbulb icon doesn't show or no Coach fixes in menu

**Cause**: Code actions provider not working

**Fix**:

1. **Ensure diagnostic exists first**:
   - Quick fixes only appear when there's a diagnostic (red/yellow squiggly)

2. **Use keyboard shortcut**:
```
Place cursor on diagnostic
Press: Ctrl+. (Windows/Linux) or Cmd+. (Mac)
```

3. **Right-click method**:
```
Right-click on diagnostic → "Quick Fix..." → Look for Coach fixes
```

4. **Check settings**:
```json
{
  "coach.enableCodeActions": true
}
```

5. **Verify provider is registered**:
```
Check extension logs for:
"CoachCodeActionProvider registered successfully"
```

---

### Issue 12: "Hover predictions not working"

**Error**: Hovering over code shows nothing or only default hover

**Cause**: Hover provider not registered

**Fix**:

1. **Enable hover predictions**:
```json
{
  "coach.enableHoverPredictions": true
}
```

2. **Wait for LSP connection**:
   - Check status bar shows "Coach: Ready ✓"
   - If not, wait 5-10 seconds after opening file

3. **Hover over known patterns**:
```python
# Try hovering over these:
pool_size = 10
rate_limit = 100
ttl = 3600
```

4. **Check LSP is responding**:
```
# In Output panel (Coach):
# Should see: "Hover request for position line:42"
```

---

## JetBrains Plugin Issues

### Issue 13: "Plugin 'Coach' failed to initialize"

**Error** (in idea.log):
```
com.intellij.diagnostic.PluginException: Cannot create class com.deepstudyai.coach.lsp.CoachLSPClient
```

**Cause**: Incompatible IDE version or missing dependencies

**Fix**:

1. **Check IDE version**:
```
Help → About
# Must be 2023.1 or later
```

2. **Check idea.log for full stack trace**:
```
Help → Show Log in Finder/Explorer
# Search for "Coach" and "PluginException"
```

3. **Invalidate caches**:
```
File → Invalidate Caches → "Invalidate and Restart"
```

4. **Reinstall plugin**:
```
Settings → Plugins → Coach → Uninstall
Restart IDE
Settings → Plugins → Install from Disk → Select coach-0.1.0.zip
Restart IDE
```

---

### Issue 14: "Inspections not running"

**Error**: No warnings/errors from Coach inspections

**Cause**: Inspections disabled or scope misconfigured

**Fix**:

1. **Enable inspections**:
```
Settings → Editor → Inspections → Coach
✓ Coach Security Analysis
✓ Coach Performance Analysis
✓ Coach Accessibility Analysis
```

2. **Check inspection scope**:
```
Settings → Editor → Inspections → Coach Security Analysis
Click "Manage" next to "Inspection profile"
Ensure scope includes your project files
```

3. **Trigger manual inspection**:
```
Code → Inspect Code → Select "Coach" profile
```

4. **Check file type is supported**:
```
Right-click file → File Properties → File Type
Should be: Python, JavaScript, TypeScript, etc.
```

---

### Issue 15: "Tool window won't open"

**Error**: "Coach" not showing in View → Tool Windows

**Cause**: Tool window not registered or hidden

**Fix**:

1. **Show hidden tool windows**:
```
View → Tool Windows → Coach
# If not visible, try:
View → Appearance → Tool Window Bars
```

2. **Reset tool window layout**:
```
Window → Store Current Layout as Default
Window → Restore Default Layout
```

3. **Check plugin is enabled**:
```
Settings → Plugins → Installed → Find "Coach"
# Should have checkmark
```

4. **Restart IDE**:
```
File → Exit
# Restart IDE
```

---

### Issue 16: "LSP: Connected" but no analysis

**Error**: Status bar shows "Coach LSP: Connected" but no inspections run

**Cause**: LSP client connected but not sending analysis requests

**Fix**:

1. **Trigger manual analysis**:
```
Right-click in editor → Coach → Analyze File
```

2. **Check LSP client logs**:
```
# In idea.log, search for:
"CoachLSPClient: Sending analyze request"
```

3. **Restart LSP client**:
```
Settings → Tools → Coach → "Restart LSP Server"
```

4. **Check server is processing requests**:
```bash
# In LSP server logs:
tail -f ~/.coach/logs/coach-lsp.log | grep "textDocument/didOpen"
# Should see requests when opening files
```

---

## Wizard Issues

### Issue 17: "Wizard not found: SecurityWizard"

**Error**:
```
ValueError: Wizard 'SecurityWizard' not found in registry
```

**Cause**: Wizard not registered or import failed

**Fix**:

1. **List available wizards**:
```python
python3 -c "from coach.wizards import get_all_wizards; print([w.name for w in get_all_wizards()])"
# Should output: ['SecurityWizard', 'PerformanceWizard', ...]
```

2. **Check wizard import**:
```python
python3 -c "from coach.wizards.security import SecurityWizard; print('OK')"
# Should output: OK
```

3. **Reinstall Coach**:
```bash
pip3 install --force-reinstall coach-ai
```

4. **Check custom wizard registration**:
```python
# If using custom wizard, ensure it's in get_all_wizards():
from coach.wizards import get_all_wizards

def get_all_wizards():
    return [
        SecurityWizard(),
        # ... other wizards ...
        MyCustomWizard(),  # Make sure this is here!
    ]
```

---

### Issue 18: "Wizard taking too long (timeout)"

**Error**:
```
TimeoutError: Wizard 'PerformanceWizard' exceeded 30 second timeout
```

**Cause**: Wizard making complex analysis or slow LLM response

**Fix**:

1. **Increase wizard timeout**:
```python
# In config:
{
  "wizard_timeout": 60  // 60 seconds instead of 30
}
```

2. **Use faster LLM**:
```bash
# Instead of GPT-4, use GPT-3.5-turbo
export COACH_LLM_MODEL=gpt-3.5-turbo
```

3. **Reduce analysis scope**:
```python
# Instead of analyzing entire file:
wizard.analyze(code=function_only, context="single function")
```

4. **Enable caching**:
```json
{
  "coach.enableCache": true,
  "coach.cacheTTL": 300  // 5 minutes
}
```

---

### Issue 19: "Low confidence scores (<0.5)"

**Error**: Wizard results have very low confidence

**Cause**: Insufficient context or edge case code

**Fix**:

1. **Provide more context**:
```python
# Instead of:
result = wizard.analyze(code)

# Do:
result = wizard.analyze(
    code=code,
    context="This is a payment processing function in an e-commerce system"
)
```

2. **Check code is complete**:
```python
# Don't analyze partial code:
code = "def process_payment("  # Incomplete!

# Analyze complete functions:
code = """
def process_payment(amount, method):
    # Full implementation
    return result
"""
```

3. **Use appropriate wizard**:
```
# Wrong:
SecurityWizard.analyze("for i in range(1000000): pass")  # Performance issue!

# Right:
PerformanceWizard.analyze("for i in range(1000000): pass")
```

---

### Issue 20: "Wizard recommendations not actionable"

**Error**: Recommendations are vague like "Review security"

**Cause**: Prompt not specific enough or LLM hallucinating

**Fix**:

1. **Use more recent LLM**:
```bash
# GPT-4 gives better recommendations than GPT-3.5
export COACH_LLM_MODEL=gpt-4
```

2. **Provide file path for context**:
```python
result = wizard.analyze(
    code=code,
    context="File: src/api/payment_controller.py, Function: process_payment"
)
```

3. **Request specific format in custom wizard**:
```python
prompt = PromptTemplate(
    template="""
    Analyze this code and provide:
    1. Specific line numbers with issues
    2. Exact code to replace
    3. Explanation of why change is needed

    Code: {code}
    """
)
```

---

## Performance Issues

### Issue 21: "LSP server using 100% CPU"

**Error**: Python process consuming all CPU

**Cause**: Infinite loop in wizard or large file analysis

**Fix**:

1. **Kill server**:
```bash
pkill -9 -f "lsp.server"
```

2. **Check recent files**:
```
# What file was being analyzed when it hung?
# Likely a very large file or minified code
```

3. **Exclude large files**:
```json
// VS Code settings.json
{
  "coach.excludePatterns": [
    "**/node_modules/**",
    "**/dist/**",
    "**/*.min.js",
    "**/*.bundle.js"
  ]
}
```

4. **Add file size limit**:
```python
# In wizard:
MAX_FILE_SIZE = 100_000  # 100 KB

def analyze(self, code: str, context: str = ""):
    if len(code) > MAX_FILE_SIZE:
        return WizardResult(
            wizard=self.name,
            diagnosis="File too large to analyze (>100KB)",
            confidence=0.0
        )
```

---

### Issue 22: "High memory usage (>2GB)"

**Error**: LSP server using excessive memory

**Cause**: Cache growing unbounded or memory leak

**Fix**:

1. **Clear cache**:
```bash
rm -rf ~/.coach/cache/*
```

2. **Reduce cache TTL**:
```json
{
  "coach.cacheTTL": 60  // 1 minute instead of 5 minutes
}
```

3. **Limit cache size**:
```python
# In server config:
MAX_CACHE_ENTRIES = 100

# Use LRU cache:
from functools import lru_cache

@lru_cache(maxsize=100)
def analyze_cached(code_hash):
    ...
```

4. **Restart server periodically**:
```bash
# Add to cron (every hour):
0 * * * * pkill -f "lsp.server" && cd /path/to/coach/lsp && python3 -m lsp.server &
```

---

### Issue 23: "Slow response times (>10s per analysis)"

**Error**: Wizard analysis taking very long

**Cause**: Complex code, slow LLM, or no caching

**Fix**:

1. **Enable caching**:
```json
{
  "coach.enableCache": true
}
```

2. **Use local model for speed**:
```bash
# Ollama is faster than OpenAI API
export COACH_LLM_PROVIDER=ollama
export COACH_LLM_MODEL=codellama
```

3. **Reduce analysis depth**:
```python
# Quick mode (pattern-based only):
result = wizard.quick_analyze(code)

# vs. Deep mode (LLM analysis):
result = wizard.analyze(code)
```

4. **Parallelize multi-wizard reviews**:
```python
# Run wizards in parallel:
import asyncio

async def parallel_review(code):
    tasks = [
        wizard1.analyze_async(code),
        wizard2.analyze_async(code),
        wizard3.analyze_async(code),
    ]
    return await asyncio.gather(*tasks)
```

---

## Network & API Issues

### Issue 24: "OpenAI API error 429: Rate limit exceeded"

**Error**:
```
openai.error.RateLimitError: Rate limit exceeded. Try again in 20s.
```

**Cause**: Too many API requests

**Fix**:

1. **Enable request caching**:
```json
{
  "coach.enableCache": true,
  "coach.cacheTTL": 300
}
```

2. **Add rate limiting**:
```python
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=50, period=60)  # 50 calls per minute
def call_openai_api():
    ...
```

3. **Use different API key**:
```bash
export OPENAI_API_KEY="different_key_here"
```

4. **Upgrade OpenAI plan**:
```
# Go to: https://platform.openai.com/account/billing
# Upgrade to higher tier for increased rate limits
```

---

### Issue 25: "Network timeout connecting to OpenAI"

**Error**:
```
requests.exceptions.ConnectTimeout: HTTPSConnectionPool: Max retries exceeded
```

**Cause**: Network connectivity or firewall

**Fix**:

1. **Test network connectivity**:
```bash
curl https://api.openai.com/v1/models
# Should return JSON with model list
```

2. **Check proxy settings**:
```bash
# If behind corporate proxy:
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080
```

3. **Increase timeout**:
```python
# In LangChain config:
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4",
    timeout=60  # 60 seconds instead of default 30
)
```

4. **Use local model (no network needed)**:
```bash
export COACH_LLM_PROVIDER=ollama
ollama serve
```

---

### Issue 26: "API key invalid or expired"

**Error**:
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Cause**: Wrong API key or expired

**Fix**:

1. **Verify API key**:
```bash
# Test API key:
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"

# Should return 200 OK with model list
# If 401 Unauthorized, key is invalid
```

2. **Get new API key**:
```
# Go to: https://platform.openai.com/api-keys
# Create new key
# Update .env file
```

3. **Check environment variable**:
```bash
echo $OPENAI_API_KEY
# Should output your key (starts with sk-)
# If empty, source .env:
source .env
echo $OPENAI_API_KEY
```

---

## Getting Help

### Before Asking for Help

1. **Collect information**:
```bash
# System info
uname -a  # OS version
python3 --version  # Python version
pip3 list | grep -E "(coach|langchain)"  # Package versions

# Logs
tail -100 ~/.coach/logs/coach-lsp.log > coach-error.log

# VS Code version
code --version

# JetBrains version
# Help → About
```

2. **Create minimal reproducible example**:
```python
# Instead of sharing your entire codebase:
# Create minimal code that reproduces the issue

# Example:
code = """
def vulnerable_function():
    user_id = input()
    query = f"SELECT * FROM users WHERE id={user_id}"
    return query
"""

from coach.wizards.security import SecurityWizard
wizard = SecurityWizard()
result = wizard.analyze(code)
print(result)  # What's wrong with this output?
```

3. **Search existing issues**:
```
# GitHub Issues:
https://github.com/deepstudyai/coach-alpha/issues

# Search for keywords like:
- "LSP server"
- "SecurityWizard"
- Your error message
```

### Getting Help Channels

#### 1. Discord (Recommended for quick help)

```
Join: https://discord.gg/coach-alpha

Channels:
#installation-help - Installation issues
#lsp-server - LSP server problems
#vs-code - VS Code extension issues
#jetbrains - JetBrains plugin issues
#wizards - Wizard-specific questions
#langchain - LangChain integration
#custom-wizards - Building custom wizards
```

**When posting**:
- Include error message
- Include Coach version (`coach --version`)
- Include relevant logs
- Describe what you tried

#### 2. GitHub Issues

```
Create issue: https://github.com/deepstudyai/coach-alpha/issues/new

Templates:
- Bug Report
- Feature Request
- Documentation Issue
```

**Include**:
- Coach version
- IDE version (VS Code or JetBrains)
- Python version
- Operating system
- Steps to reproduce
- Expected vs actual behavior
- Relevant logs

#### 3. Email Support

```
Email: support@deepstudyai.com

Subject format:
[Coach] Brief description of issue

Include:
- All info from "Before Asking for Help" section
- Attach logs (coach-error.log)
- Screenshots if applicable
```

**Response time**:
- Alpha testers: 24-48 hours
- Bug reports: 1-3 business days
- Feature requests: 1 week

### Community Resources

- **Documentation**: [https://docs.coach-ai.dev](https://docs.coach-ai.dev)
- **Examples**: [https://github.com/deepstudyai/coach-alpha/tree/main/examples](https://github.com/deepstudyai/coach-alpha/tree/main/examples)
- **LangChain Docs**: [https://python.langchain.com/docs/](https://python.langchain.com/docs/)
- **Blog**: [https://blog.deepstudyai.com](https://blog.deepstudyai.com)

---

## Emergency Procedures

### Complete Reset

If all else fails, start fresh:

```bash
# 1. Uninstall everything
pip3 uninstall coach-ai langchain langchain-community langchain-openai -y

# 2. Remove config
rm -rf ~/.coach

# 3. Remove cache
rm -rf ~/.cache/coach

# 4. Create new venv
cd ~/projects/coach
python3 -m venv venv-new
source venv-new/bin/activate

# 5. Fresh install
pip3 install --upgrade pip
pip3 install -r requirements.txt

# 6. Test
python3 -c "from coach import Coach; print('✓ Coach installed')"

# 7. Reinstall IDE extensions
# VS Code: Uninstall → Reinstall coach-0.1.0.vsix
# JetBrains: Uninstall → Restart → Reinstall coach-0.1.0.zip
```

### Factory Reset (Last Resort)

```bash
# WARNING: Deletes all Coach data and configuration

# 1. Stop all Coach processes
pkill -9 -f "lsp.server"
pkill -9 -f "coach"

# 2. Remove all Coach files
rm -rf ~/.coach
rm -rf ~/Library/Application\ Support/Coach  # macOS
rm -rf ~/.local/share/Coach  # Linux
rm -rf ~/.cache/coach

# 3. Uninstall from system Python (if installed there)
sudo pip3 uninstall coach-ai -y

# 4. Remove IDE extensions
code --uninstall-extension deepstudyai.coach  # VS Code
# JetBrains: Settings → Plugins → Coach → Uninstall

# 5. Start over with fresh installation
# Follow INSTALLATION.md from scratch
```

---

## Still Need Help?

If you've tried everything above and still have issues:

1. **Join Discord**: Fastest way to get help from community
2. **Create GitHub Issue**: For bugs or feature requests
3. **Email Support**: For sensitive issues or alpha tester priority support

**We're here to help!** Coach is in alpha, so issues are expected. Your feedback makes Coach better.

---

**Built with** ❤️ **using LangChain**
