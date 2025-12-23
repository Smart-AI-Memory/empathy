# Reddit Posts - Ready to Copy/Paste

---

## r/ClaudeAI

**Title:** I built a persistent memory layer for Claude + XML-Enhanced Prompts for structured responses (v3.0.1)

**Body:**

Every Claude conversation starts fresh. I wanted my dev assistant to remember my preferences across sessions, so I built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework).

Quick example:

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

# This preference persists across sessions
await llm.interact(
    user_id="me",
    user_input="I prefer concise Python with type hints"
)
```

Next session, Claude remembers.

**v3.0.1 just shipped with Multi-Provider System + XML-Enhanced Prompts** - now supports Anthropic, OpenAI, Ollama, and hybrid mode. Auto-detects your API keys and picks the right model for each task. New XML prompts return structured, parseable responses for dashboards and automation.

```python
llm = EmpathyLLM(provider="hybrid", enable_model_routing=True)
await llm.interact(user_id="dev", user_input="Summarize this", task_type="summarize")  # → Cheapest model
```

**Cost savings: $4.05 → $0.83 per task (80%)**

- API users: Direct cost savings
- Max/Pro subscribers: Preserves your Opus quota for complex tasks

**What's new in v3.0.1:**
- Multi-provider support (Anthropic, OpenAI, Ollama, Hybrid)
- XML-Enhanced Prompts for structured LLM responses
- Auto-detection of API keys from environment/.env files
- VSCode Dashboard with 10 integrated workflows + 6 quick actions
- Real-time cost tracking showing your savings

**Core features:**
- Cross-session memory persistence
- Per-user isolation
- Privacy controls (clear/forget)

On PyPI: `pip install empathy-framework` (3,400+ monthly downloads)

Happy to answer questions.

---

## r/Python

**Title:** empathy-framework v3.0.1: Multi-provider LLM memory + XML-Enhanced Prompts + VSCode Dashboard

**Body:**

Just released v3.0.1 of [empathy-framework](https://pypi.org/project/empathy-framework/) - a Python library that adds persistent memory to LLM interactions, plus multi-provider smart routing and XML-Enhanced Prompts for structured responses.

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",  # or "openai", "ollama", "hybrid"
    memory_enabled=True,
    enable_model_routing=True
)

# Memory survives across sessions
await llm.interact(user_id="user123", user_input="Remember I prefer async/await")

# Automatic model selection based on task
await llm.interact(user_id="user123", user_input="Summarize this", task_type="summarize")  # → Haiku/GPT-4o-mini
```

**What's new in v3.0.1:**
- **Multi-Provider System**: Anthropic, OpenAI, Ollama, Hybrid mode
- **XML-Enhanced Prompts**: Structured, parseable LLM responses for automation
- **Auto-detection**: Finds API keys from environment and .env files
- **Smart Routing**: Auto-picks Haiku/Sonnet/Opus (or GPT equivalents) based on task
- **VSCode Dashboard**: 10 integrated workflows + 6 quick action commands
- **Real-time cost tracking**: See your savings as you work

**Cost comparison:**
- Without routing (all Opus): $4.05/task
- With routing (tiered): $0.83/task
- **Savings: 80%**

*API users save money. Subscription users (Max/Pro) preserve premium model quota.*

**CLI for provider management:**
```bash
python -m empathy_os.models.cli provider status
python -m empathy_os.models.cli provider set hybrid
```

**Core features:**
- Works with Claude, OpenAI, local models
- Per-user memory isolation
- Privacy controls built in
- Async-first design

**Stats:** 3,400+ monthly PyPI downloads | 34 versions published

GitHub: https://github.com/Smart-AI-Memory/empathy-framework

Feedback welcome. What use cases would you want memory for?

---

## r/LocalLLaMA

**Title:** Cross-session memory layer for LLMs - now with native Ollama support (v3.0.1)

**Body:**

Built [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) to give LLMs persistent memory across sessions.

**v3.0.1 adds native Ollama support + XML-Enhanced Prompts!**

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="ollama", memory_enabled=True)

# Preferences persist across sessions
await llm.interact(user_id="user", user_input="I use vim keybindings")
```

**Multi-provider architecture:**
- **Anthropic** — Claude (Haiku/Sonnet/Opus)
- **OpenAI** — GPT (GPT-4o-mini/GPT-4o/o1)
- **Ollama** — Local models (Llama 3.2/3.1)
- **Hybrid** — Best of each provider per tier

The system auto-detects which providers you have available (checks for running Ollama instance, API keys in environment).

**CLI commands:**
```bash
python -m empathy_os.models.cli provider status  # Shows available providers
python -m empathy_os.models.cli provider set ollama  # Use Ollama exclusively
```

**Smart tier routing for local models:**
- Cheap tier: Llama 3.2 (3B)
- Capable tier: Llama 3.1 (8B)
- Premium tier: Llama 3.1 (70B)

Currently on PyPI: `pip install empathy-framework` (3,400+ monthly downloads)

Would love feedback from the local LLM community!
