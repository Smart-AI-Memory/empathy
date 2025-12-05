# Empathy Framework - Troubleshooting Guide

**Last Updated:** November 2025
**Version:** 1.0.0

This guide covers common issues, error messages, and solutions for the Empathy Framework.

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [Import and Module Errors](#import-and-module-errors)
- [API Key Configuration](#api-key-configuration)
- [Runtime Errors](#runtime-errors)
- [Performance Issues](#performance-issues)
- [Test Failures](#test-failures)
- [LLM Provider Issues](#llm-provider-issues)
- [Configuration Issues](#configuration-issues)
- [Memory and Resource Issues](#memory-and-resource-issues)
- [Platform-Specific Issues](#platform-specific-issues)

---

## Installation Issues

### Issue: `pip install empathy-framework` fails

**Error Messages:**
```
ERROR: Could not find a version that satisfies the requirement empathy-framework
ERROR: No matching distribution found for empathy-framework
```

**Solutions:**

**1. Check Python version:**
```bash
python --version  # Must be 3.10 or higher

# If too old, install newer Python
# macOS with Homebrew:
brew install python@3.11

# Linux (Ubuntu/Debian):
sudo apt update && sudo apt install python3.11

# Windows: Download from python.org
```

**2. Upgrade pip:**
```bash
pip install --upgrade pip setuptools wheel
```

**3. Install from source (if package not yet published):**
```bash
git clone https://github.com/Deep-Study-AI/Empathy.git
cd Empathy
pip install -r requirements.txt
pip install -e .
```

### Issue: Dependency conflicts

**Error Message:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages
that are installed. This behaviour is the source of the following dependency conflicts.
```

**Solutions:**

**1. Create a clean virtual environment:**
```bash
# Create new environment
python -m venv empathy_env

# Activate it
# macOS/Linux:
source empathy_env/bin/activate
# Windows:
empathy_env\Scripts\activate

# Install in clean environment
pip install empathy-framework
```

**2. Use requirements.txt for reproducible installs:**
```bash
pip install -r requirements.txt
```

**3. If conflicts persist, install individually:**
```bash
pip install langchain==0.1.0
pip install anthropic==0.8.0
pip install openai==1.6.0
pip install empathy-framework
```

### Issue: Permission denied during installation

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: '/usr/local/lib/python3.11/site-packages/'
```

**Solutions:**

**Don't use sudo! Use virtual environments instead:**
```bash
# Create virtual environment
python -m venv ~/.empathy_env

# Activate it
source ~/.empathy_env/bin/activate

# Install without sudo
pip install empathy-framework
```

**Or use --user flag:**
```bash
pip install --user empathy-framework
```

---

## Import and Module Errors

### Issue: `ModuleNotFoundError: No module named 'empathy_llm_toolkit'`

**Error Message:**
```python
ModuleNotFoundError: No module named 'empathy_llm_toolkit'
```

**Solutions:**

**1. Verify installation:**
```bash
pip list | grep empathy
# Should show: empathy-framework x.x.x
```

**2. Check Python path:**
```python
import sys
print(sys.path)
# Ensure your installation directory is in the path
```

**3. Install in development mode if using source:**
```bash
cd /path/to/Empathy
pip install -e .
```

**4. Check you're using the right Python:**
```bash
which python
which pip
# Should point to same environment
```

### Issue: `ModuleNotFoundError: No module named 'coach_wizards'`

**Solutions:**

**1. Ensure you're in the project directory:**
```bash
cd /path/to/Empathy-framework
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**2. Install in editable mode:**
```bash
pip install -e .
```

**3. Verify the module exists:**
```bash
python -c "from coach_wizards import SecurityWizard; print('Success!')"
```

### Issue: `ImportError: cannot import name 'X' from 'Y'`

**Cause:** API changes between versions

**Solutions:**

**1. Check version compatibility:**
```bash
pip show empathy-framework
# Compare with documentation version
```

**2. Update to latest version:**
```bash
pip install --upgrade empathy-framework
```

**3. Check import statement matches docs:**
```python
# Old (might be outdated):
from empathy_llm_toolkit.providers import AnthropicProvider

# Current (check docs for latest):
from empathy_llm_toolkit import EmpathyLLM
```

---

## API Key Configuration

### Issue: "API key not found" or "Authentication failed"

**Error Messages:**
```
ValueError: ANTHROPIC_API_KEY not found in environment
AuthenticationError: Invalid API key
```

**Solutions:**

**1. Check if environment variable is set:**
```bash
echo $ANTHROPIC_API_KEY
# Should print your key (sk-ant-...)
```

**2. Set environment variable:**
```bash
# For current session:
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# Make permanent (macOS/Linux):
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.bashrc
source ~/.bashrc

# Or use ~/.zshrc on macOS with zsh:
echo 'export ANTHROPIC_API_KEY=sk-ant-your-key-here' >> ~/.zshrc
source ~/.zshrc
```

**3. Use .env file:**
```bash
# Create .env file in project root
cat > .env << EOF
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
EOF

# Load in Python
from dotenv import load_dotenv
load_dotenv()
```

**4. Pass key directly in code (not recommended for production):**
```python
llm = EmpathyLLM(
    provider="anthropic",
    api_key="sk-ant-your-key-here"  # Hardcoded (not recommended)
)
```

**5. Verify key is valid:**
```bash
# Test with curl (Anthropic):
curl https://api.anthropic.com/v1/messages \
  -H "x-api-key: $ANTHROPIC_API_KEY" \
  -H "anthropic-version: 2023-06-01" \
  -H "content-type: application/json" \
  -d '{
    "model": "claude-3-5-sonnet-20241022",
    "max_tokens": 10,
    "messages": [{"role": "user", "content": "Hi"}]
  }'

# Should return a response, not an error
```

### Issue: API key works in terminal but not in application

**Cause:** Environment variables not passed to application

**Solutions:**

**1. Load dotenv in application:**
```python
from dotenv import load_dotenv
load_dotenv()  # Call this BEFORE importing framework

from empathy_llm_toolkit import EmpathyLLM
```

**2. Export in shell before running:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
python my_app.py
```

**3. Use systemd environment file (Linux services):**
```ini
# /etc/systemd/system/myapp.service
[Service]
EnvironmentFile=/etc/myapp/env
ExecStart=/usr/bin/python /app/main.py
```

**4. Use Docker env file:**
```bash
docker run --env-file .env myapp
```

---

## Runtime Errors

### Issue: "Target level not reached" or "Trust level too low"

**Error Message:**
```
RuntimeError: Target level 4 not reached. Current trust level: 0.35 (requires 0.8+)
```

**Cause:** Attempting to use higher empathy level without sufficient trust

**Solutions:**

**1. Build trust through successful interactions:**
```python
llm = EmpathyLLM(provider="anthropic", target_level=4)

# Interact multiple times
for i in range(20):
    result = await llm.interact(
        user_id="alice",
        user_input=f"Question {i}"
    )
    # Provide positive feedback
    llm.update_trust("alice", outcome="success")

# Check trust level
stats = llm.get_statistics("alice")
print(f"Trust: {stats['trust_level']}")  # Should be > 0.8 for Level 4
```

**2. Force level for testing/demo:**
```python
result = await llm.interact(
    user_id="test",
    user_input="Test input",
    force_level=4  # Override trust requirement
)
```

**3. Adjust trust building rate in config:**
```yaml
# empathy.config.yml
trust_building_rate: 0.10  # Default: 0.05 (higher = faster trust)
trust_erosion_rate: 0.05   # Default: 0.10 (lower = trust decays slower)
```

### Issue: "Async runtime error" or "Event loop is closed"

**Error Message:**
```
RuntimeError: Event loop is closed
RuntimeError: This event loop is already running
```

**Solutions:**

**1. Use asyncio.run() correctly:**
```python
import asyncio

async def main():
    llm = EmpathyLLM(provider="anthropic", target_level=4)
    result = await llm.interact(user_id="alice", user_input="Hello")
    return result

# Correct:
if __name__ == "__main__":
    result = asyncio.run(main())

# Incorrect (in scripts):
# loop = asyncio.get_event_loop()
# result = loop.run_until_complete(main())
```

**2. In Jupyter notebooks, use nest_asyncio:**
```python
import nest_asyncio
nest_asyncio.apply()

import asyncio
from empathy_llm_toolkit import EmpathyLLM

async def main():
    llm = EmpathyLLM(provider="anthropic", target_level=4)
    result = await llm.interact(user_id="alice", user_input="Hello")
    return result

result = asyncio.run(main())
```

**3. If using FastAPI or other async frameworks:**
```python
from fastapi import FastAPI

app = FastAPI()
llm = EmpathyLLM(provider="anthropic", target_level=4)

@app.post("/chat")
async def chat(message: str):
    # Already in async context - just await
    result = await llm.interact(user_id="user", user_input=message)
    return result
```

---

## Performance Issues

### Issue: Slow response times

**Symptoms:** Each LLM call takes 5-30+ seconds

**Solutions:**

**1. Use faster model:**
```python
# Slow (high quality):
llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-opus-20240229",  # Slowest, highest quality
    target_level=4
)

# Fast (good quality):
llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307",  # 10x faster, 25x cheaper
    target_level=3
)
```

**2. Enable prompt caching (Claude only):**
```python
from empathy_llm_toolkit.providers import AnthropicProvider

provider = AnthropicProvider(
    use_prompt_caching=True,  # 90% faster on repeated prompts
    model="claude-3-5-sonnet-20241022"
)
```

**3. Use local model for development:**
```python
# No API latency - runs on your machine
llm = EmpathyLLM(
    provider="local",
    endpoint="http://localhost:11434",
    model="llama2",
    target_level=2
)
```

**4. Reduce max_tokens:**
```python
result = await llm.interact(
    user_id="user",
    user_input="Question",
    max_tokens=512  # Limit response length (default: 1024)
)
```

**5. Use async for parallel requests:**
```python
import asyncio

async def analyze_files(files):
    tasks = [
        llm.interact(user_id="user", user_input=f"Analyze {f}")
        for f in files
    ]
    # Run in parallel
    results = await asyncio.gather(*tasks)
    return results
```

### Issue: High LLM API costs

**Symptoms:** Monthly bills of $100+ for development

**Solutions:**

**1. Enable prompt caching (90% cost reduction):**
```python
provider = AnthropicProvider(use_prompt_caching=True)
```

**2. Use cheaper models for simple tasks:**
```python
# Expensive:
llm_expensive = EmpathyLLM(
    provider="anthropic",
    model="claude-3-opus-20240229"  # $15 per 1M input tokens
)

# Cheap:
llm_cheap = EmpathyLLM(
    provider="anthropic",
    model="claude-3-haiku-20240307"  # $0.25 per 1M input tokens (60x cheaper!)
)

# Route appropriately:
if task_complexity == "high":
    result = await llm_expensive.interact(user_id, input)
else:
    result = await llm_cheap.interact(user_id, input)
```

**3. Use local models for development:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Download model
ollama pull llama2

# Use in framework (free!)
llm = EmpathyLLM(
    provider="local",
    endpoint="http://localhost:11434",
    model="llama2"
)
```

**4. Cache wizard results:**
```python
import functools
from coach_wizards import SecurityWizard

wizard = SecurityWizard()

@functools.lru_cache(maxsize=100)
def cached_analysis(code_hash):
    # Only analyzes unique code once
    return wizard.run_full_analysis(code, file_path, language)

# Use hash to cache results
import hashlib
code_hash = hashlib.sha256(code.encode()).hexdigest()
result = cached_analysis(code_hash)
```

### Issue: Memory errors with large codebases

**Error Message:**
```
MemoryError: Unable to allocate array
OutOfMemoryError
```

**Solutions:**

**1. Process files incrementally:**
```python
from coach_wizards import SecurityWizard

wizard = SecurityWizard()
all_issues = []

# Process one file at a time
for file_path in large_codebase:
    code = open(file_path).read()
    result = wizard.run_full_analysis(code, file_path, "python")
    all_issues.extend(result.issues)
    # Memory freed after each iteration
```

**2. Use Claude's 200K context window:**
```python
from empathy_llm_toolkit.providers import AnthropicProvider

provider = AnthropicProvider(
    model="claude-3-5-sonnet-20241022",  # 200K context
    use_prompt_caching=True  # Cache large contexts
)

# Can analyze entire repository at once
files = [{"path": f, "content": open(f).read()} for f in all_files]
result = await provider.analyze_large_codebase(
    codebase_files=files,
    analysis_prompt="Find all security issues"
)
```

**3. Increase system memory limits:**
```bash
# Linux: Increase swap space
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Docker: Increase memory limit
docker run -m 8g myapp
```

---

## Test Failures

### Issue: Tests fail with "API key not found"

**Solutions:**

**1. Set environment variables before running tests:**
```bash
export ANTHROPIC_API_KEY=sk-ant-your-key
pytest
```

**2. Use pytest fixtures:**
```python
# conftest.py
import pytest
import os

@pytest.fixture(autouse=True)
def set_env():
    os.environ["ANTHROPIC_API_KEY"] = "sk-ant-test-key"
    yield
    del os.environ["ANTHROPIC_API_KEY"]
```

**3. Use .env file:**
```bash
# .env.test
ANTHROPIC_API_KEY=sk-ant-test-key
```

```python
# conftest.py
from dotenv import load_dotenv
load_dotenv(".env.test")
```

### Issue: Tests are slow (>1 minute)

**Solutions:**

**1. Mock LLM calls:**
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
@patch('empathy_llm_toolkit.providers.AnthropicProvider.generate')
async def test_interaction(mock_generate):
    # Mock LLM response
    mock_generate.return_value = AsyncMock(
        content="Mocked response",
        model="claude-3-5-sonnet-20241022",
        tokens_used=100
    )

    llm = EmpathyLLM(provider="anthropic", target_level=4)
    result = await llm.interact(user_id="test", user_input="Hello")

    assert "Mocked response" in result['content']
    # Test completes instantly
```

**2. Use pytest-xdist for parallel tests:**
```bash
pip install pytest-xdist
pytest -n auto  # Runs tests in parallel
```

**3. Skip slow tests by default:**
```python
import pytest

@pytest.mark.slow
async def test_expensive_operation():
    # Only runs when: pytest --runslow
    pass
```

```python
# conftest.py
def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true", help="run slow tests")

def pytest_collection_modifyitems(config, items):
    if not config.getoption("--runslow"):
        skip_slow = pytest.mark.skip(reason="need --runslow to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_slow)
```

---

## LLM Provider Issues

### Issue: Anthropic API rate limit errors

**Error Message:**
```
RateLimitError: rate_limit_error: You have been rate limited
```

**Solutions:**

**1. Implement exponential backoff:**
```python
import asyncio
from anthropic import RateLimitError

async def interact_with_retry(llm, user_id, user_input, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = await llm.interact(user_id, user_input)
            return result
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
```

**2. Upgrade your API tier:**
- Visit https://console.anthropic.com
- Request higher rate limits
- Enterprise customers get dedicated capacity

**3. Use prompt caching to reduce requests:**
```python
provider = AnthropicProvider(use_prompt_caching=True)
```

**4. Batch requests instead of individual calls:**
```python
# Instead of:
for item in items:
    result = await llm.interact(user_id, f"Analyze {item}")

# Do:
batch_input = "\n".join([f"Analyze {item}" for item in items])
result = await llm.interact(user_id, batch_input)
```

### Issue: OpenAI context length exceeded

**Error Message:**
```
InvalidRequestError: This model's maximum context length is 8192 tokens
```

**Solutions:**

**1. Use model with larger context:**
```python
llm = EmpathyLLM(
    provider="openai",
    model="gpt-4-turbo-preview",  # 128K context (vs 8K for gpt-4)
    target_level=4
)
```

**2. Truncate conversation history:**
```python
result = await llm.interact(
    user_id="user",
    user_input="Question",
    max_history_turns=5  # Only use last 5 interactions
)
```

**3. Switch to Claude (200K context):**
```python
llm = EmpathyLLM(
    provider="anthropic",
    model="claude-3-5-sonnet-20241022",  # 200K context
    target_level=4
)
```

### Issue: Local model (Ollama) connection refused

**Error Message:**
```
ConnectionRefusedError: [Errno 61] Connection refused
```

**Solutions:**

**1. Start Ollama server:**
```bash
# macOS/Linux:
ollama serve

# Or run in background:
nohup ollama serve > /dev/null 2>&1 &
```

**2. Check if Ollama is running:**
```bash
curl http://localhost:11434/api/version
# Should return version info
```

**3. Check endpoint URL:**
```python
llm = EmpathyLLM(
    provider="local",
    endpoint="http://localhost:11434",  # Default Ollama port
    model="llama2"
)
```

**4. Download model if missing:**
```bash
ollama pull llama2
ollama list  # Verify it's downloaded
```

---

## Configuration Issues

### Issue: Configuration file not found

**Error Message:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'empathy.config.yml'
```

**Solutions:**

**1. Generate default config:**
```bash
empathy-framework init --format yaml --output empathy.config.yml
```

**2. Specify config path:**
```python
from empathy_os.config import load_config

config = load_config("/absolute/path/to/empathy.config.yml")
```

**3. Use environment variables instead:**
```bash
export EMPATHY_USER_ID=alice
export EMPATHY_TARGET_LEVEL=4
export EMPATHY_CONFIDENCE_THRESHOLD=0.75
```

```python
from empathy_os.config import EmpathyConfig

config = EmpathyConfig.from_env()
```

### Issue: Invalid configuration values

**Error Message:**
```
ValueError: target_level must be between 1 and 5, got 10
ValueError: confidence_threshold must be between 0.0 and 1.0, got 1.5
```

**Solutions:**

**1. Validate configuration:**
```python
from empathy_os.config import EmpathyConfig

config = EmpathyConfig(
    target_level=4,  # Must be 1-5
    confidence_threshold=0.75  # Must be 0.0-1.0
)

# Validates automatically
try:
    config.validate()
    print("Config valid!")
except ValueError as e:
    print(f"Config error: {e}")
```

**2. Check config file syntax:**
```yaml
# empathy.config.yml

# Valid:
target_level: 4

# Invalid:
target_level: "4"  # Must be integer, not string

# Valid:
confidence_threshold: 0.75

# Invalid:
confidence_threshold: 75  # Must be 0.0-1.0, not percentage
```

---

## Memory and Resource Issues

### Issue: "Database is locked" error (SQLite)

**Error Message:**
```
sqlite3.OperationalError: database is locked
```

**Solutions:**

**1. Enable WAL mode (Write-Ahead Logging):**
```python
import sqlite3

conn = sqlite3.connect("empathy_data/state.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.close()
```

**2. Increase timeout:**
```python
conn = sqlite3.connect("empathy_data/state.db", timeout=30.0)
```

**3. Use PostgreSQL for concurrent access:**
```yaml
# empathy.config.yml
persistence_backend: postgresql
persistence_path: postgresql://user:pass@localhost/empathy
```

### Issue: Disk space full

**Error Message:**
```
OSError: [Errno 28] No space left on device
```

**Solutions:**

**1. Clean up old state files:**
```bash
# Find large state files
du -sh ~/.empathy_data/*

# Remove old states (backup first!)
rm -rf ~/.empathy_data/old_states/
```

**2. Limit state persistence:**
```yaml
# empathy.config.yml
state_persistence: false  # Disable state saving
```

**3. Configure log rotation:**
```python
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'empathy.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logging.basicConfig(handlers=[handler])
```

---

## Platform-Specific Issues

### macOS: "Operation not permitted" error

**Error Message:**
```
PermissionError: [Errno 1] Operation not permitted
```

**Solutions:**

**1. Grant terminal Full Disk Access:**
- System Preferences → Security & Privacy → Privacy → Full Disk Access
- Add Terminal.app or your IDE

**2. Use home directory for data:**
```yaml
# empathy.config.yml
persistence_path: ~/empathy_data  # Not /usr/local/
state_path: ~/empathy_state
```

### Windows: "Access is denied" or path issues

**Error Message:**
```
PermissionError: [WinError 5] Access is denied
FileNotFoundError: [WinError 3] The system cannot find the path specified
```

**Solutions:**

**1. Use forward slashes or raw strings:**
```python
# Good:
config_path = "C:/Users/alice/empathy.config.yml"

# Or:
config_path = r"C:\Users\alice\empathy.config.yml"

# Bad:
config_path = "C:\Users\alice\empathy.config.yml"  # Backslashes interpreted
```

**2. Run as administrator (if necessary):**
- Right-click Python/IDE → "Run as administrator"

**3. Use user directory:**
```python
import os
from pathlib import Path

# Use user's home directory
home = Path.home()
config_path = home / "empathy.config.yml"
```

### Linux: SELinux permission denied

**Error Message:**
```
PermissionError: [Errno 13] Permission denied
```

**Solutions:**

**1. Check SELinux status:**
```bash
getenforce
# If "Enforcing", SELinux might be blocking
```

**2. Add SELinux policy:**
```bash
sudo semanage fcontext -a -t user_home_t "/path/to/empathy_data(/.*)?"
sudo restorecon -R /path/to/empathy_data
```

**3. Or temporarily disable (not recommended for production):**
```bash
sudo setenforce 0  # Temporary
```

---

## Getting More Help

### Enable Debug Logging

Get detailed logs for troubleshooting:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("empathy_debug.log"),
        logging.StreamHandler()
    ]
)

# Now run your code - detailed logs will be saved
```

### Collect System Information

When reporting issues, include:

```bash
# System info
uname -a
python --version
pip show empathy-framework

# Environment
echo $ANTHROPIC_API_KEY | cut -c1-10  # First 10 chars only
echo $OPENAI_API_KEY | cut -c1-10

# Test imports
python -c "from empathy_llm_toolkit import EmpathyLLM; print('Core: OK')"
python -c "from coach_wizards import SecurityWizard; print('Wizards: OK')"
```

### Report Bugs

**GitHub Issues:** https://github.com/Deep-Study-AI/Empathy/issues

**Include:**
1. Full error message and traceback
2. Empathy Framework version
3. Python version
4. Operating system
5. Minimal code to reproduce
6. Steps to reproduce
7. Expected vs actual behavior

### Get Commercial Support

For priority support with guaranteed response times:

**Commercial Support:** $99/developer/year
- 24-48 hour response time
- Direct access to core team
- Architecture consultation
- Upgrade assistance

**Contact:** patrick.roebuck@deepstudyai.com

---

**Copyright 2025 Smart AI Memory, LLC**
**Licensed under Fair Source 0.9**
