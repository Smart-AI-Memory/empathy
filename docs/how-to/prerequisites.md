# Prerequisites

*What you need before building with the Empathy Framework*

---

## Quick Checklist

Before you begin, ensure you have:

- [ ] **Python 3.9+** installed
- [ ] **Redis** running locally OR a cloud Redis URL
- [ ] **30 minutes** for initial setup
- [ ] **API key** for your LLM provider (Anthropic recommended)

---

## Detailed Requirements

### 1. Python Environment

**Minimum version**: Python 3.9

**Recommended**: Python 3.11+ for best async performance

```bash
# Check your version
python --version

# Create a virtual environment (recommended)
python -m venv empathy-env
source empathy-env/bin/activate  # macOS/Linux
# or
empathy-env\Scripts\activate     # Windows
```

**Required knowledge**:
- Basic Python syntax
- Package installation with pip
- (Optional) async/await for advanced patterns

---

### 2. Redis for Short-Term Memory

The framework uses Redis for agent coordination. You have three options:

#### Option A: Local Redis (Development)

```bash
# macOS with Homebrew
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# Windows (WSL recommended)
# Use WSL and follow Ubuntu instructions

# Docker (any platform)
docker run -d -p 6379:6379 redis:alpine
```

**Verify it's running**:
```bash
redis-cli ping
# Should return: PONG
```

#### Option B: Cloud Redis (Production)

For production or team environments, use a managed Redis service:

| Provider | Free Tier | Setup Time |
|----------|-----------|------------|
| [Railway](https://railway.app) | 500MB | 2 minutes |
| [Upstash](https://upstash.com) | 10K commands/day | 2 minutes |
| [Redis Cloud](https://redis.com/try-free/) | 30MB | 5 minutes |
| AWS ElastiCache | No free tier | 15 minutes |

**Set the connection URL**:
```bash
export REDIS_URL="redis://default:password@your-host:port"
```

#### Option C: Mock Mode (No Redis)

For quick experiments without Redis:

```python
import os
os.environ["EMPATHY_REDIS_MOCK"] = "true"

from empathy_os import EmpathyOS
empathy = EmpathyOS(user_id="test")  # Uses in-memory mock
```

**Limitations**: Mock mode doesn't persist across restarts or support multi-agent coordination.

---

### 3. LLM Provider API Key

The framework supports multiple LLM providers. You need at least one:

#### Anthropic (Recommended)

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Get your key: [console.anthropic.com](https://console.anthropic.com/)

#### OpenAI

```bash
export OPENAI_API_KEY="sk-..."
```

#### Azure OpenAI

```bash
export AZURE_OPENAI_API_KEY="..."
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

---

### 4. Install the Framework

```bash
# Core framework
pip install empathy-framework

# With Redis support (recommended)
pip install empathy-framework[redis]

# With all optional dependencies
pip install empathy-framework[all]
```

**Verify installation**:
```python
from empathy_os import EmpathyOS
print("Empathy Framework installed successfully!")
```

---

## Knowledge Prerequisites

### Required

| Skill | Why It's Needed | Quick Resource |
|-------|-----------------|----------------|
| Python basics | All examples are in Python | [Python Tutorial](https://docs.python.org/3/tutorial/) |
| Environment variables | Configuration and API keys | [12-Factor App](https://12factor.net/config) |

### Helpful But Optional

| Skill | When You'll Need It | Quick Resource |
|-------|---------------------|----------------|
| async/await | Multi-agent patterns | [Real Python Async](https://realpython.com/async-io-python/) |
| Redis basics | Custom memory patterns | [Redis Quickstart](https://redis.io/docs/getting-started/) |
| Docker | Production deployment | [Docker Getting Started](https://docs.docker.com/get-started/) |

---

## Environment Setup Script

Run this script to verify your environment:

```python
#!/usr/bin/env python3
"""Verify Empathy Framework prerequisites."""

import sys
import os

def check_python():
    version = sys.version_info
    if version >= (3, 9):
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor} (need 3.9+)")
        return False

def check_redis():
    try:
        import redis
        r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
        r.ping()
        print("[OK] Redis connected")
        return True
    except Exception as e:
        if os.getenv("EMPATHY_REDIS_MOCK") == "true":
            print("[OK] Redis mock mode enabled")
            return True
        print(f"[WARN] Redis not available: {e}")
        print("       Set EMPATHY_REDIS_MOCK=true to use mock mode")
        return False

def check_api_keys():
    keys = {
        "ANTHROPIC_API_KEY": "Anthropic",
        "OPENAI_API_KEY": "OpenAI",
    }
    found = False
    for key, name in keys.items():
        if os.getenv(key):
            print(f"[OK] {name} API key configured")
            found = True
    if not found:
        print("[WARN] No LLM API key found")
        print("       Set ANTHROPIC_API_KEY or OPENAI_API_KEY")
    return found

def check_empathy():
    try:
        from empathy_os import EmpathyOS
        print("[OK] Empathy Framework installed")
        return True
    except ImportError:
        print("[FAIL] Empathy Framework not installed")
        print("       Run: pip install empathy-framework")
        return False

if __name__ == "__main__":
    print("=== Empathy Framework Prerequisites Check ===\n")

    results = [
        check_python(),
        check_empathy(),
        check_redis(),
        check_api_keys(),
    ]

    print("\n" + "=" * 45)
    if all(results):
        print("All prerequisites met! You're ready to start.")
    else:
        print("Some prerequisites need attention. See above.")
```

Save as `check_prereqs.py` and run:
```bash
python check_prereqs.py
```

---

## Troubleshooting

### "Redis connection refused"

Redis isn't running. Start it with:
```bash
# macOS
brew services start redis

# Linux
sudo systemctl start redis

# Docker
docker run -d -p 6379:6379 redis:alpine
```

### "No module named 'empathy_os'"

Install the framework:
```bash
pip install empathy-framework
```

### "API key not found"

Set your environment variable:
```bash
# Add to ~/.bashrc or ~/.zshrc for persistence
export ANTHROPIC_API_KEY="your-key-here"
```

### "Python version too old"

Use pyenv to manage Python versions:
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.0
pyenv local 3.11.0
```

---

## Next Steps

Once prerequisites are met:

1. **Quick start**: [Unified Memory System](./unified-memory-system.md)
2. **Understand the philosophy**: [Multi-Agent Philosophy](./multi-agent-philosophy.md)
3. **See patterns**: [Practical Patterns](./practical-patterns.md)

---

*Estimated setup time: 15-30 minutes depending on your starting point*
