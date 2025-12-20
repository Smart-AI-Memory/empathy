# Show HN: Empathy Framework v2.3 – Persistent AI memory + 80% cost savings

**Title:** Empathy Framework v2.3 – Persistent AI memory + smart model routing (80% cost savings)

**URL:** https://github.com/Smart-AI-Memory/empathy-framework

---

I've been building AI tools and got tired of two problems: every session starts from zero, and I was paying Opus prices for simple tasks.

So I built Empathy Framework. v2.3 just shipped with major cost optimization.

**The 80% cost savings:**

New ModelRouter automatically picks the right model tier:

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(provider="anthropic", enable_model_routing=True)

# Summaries → Haiku ($0.25/M tokens)
# Code gen → Sonnet ($3/M tokens)
# Architecture → Opus ($15/M tokens)
```

Real numbers: $4.05/task → $0.83/task. That's 80% savings by just using the right model for each task.

**The memory problem:**

AI forgets everything between sessions. Tell it you prefer type hints? Gone next time. Empathy adds persistent memory:

```python
llm = EmpathyLLM(provider="anthropic", memory_enabled=True)

await llm.interact(
    user_id="me",
    user_input="I prefer Python with type hints"
)
# Survives across sessions
```

**New in v2.3:**

1. **ModelRouter** — Automatic Haiku/Sonnet/Opus selection based on task complexity
2. **`empathy sync-claude`** — Sync learned patterns to Claude Code's `.claude/rules/` directory
3. **Debug Wizard** — Web UI at empathy-framework.vercel.app/tools/debug-wizard that remembers past bugs

**How the memory works:**

- Git-based pattern storage (no infrastructure needed)
- Optional Redis for real-time coordination
- Bug patterns, security decisions, coding preferences all persist

**What's included:**

- `empathy-inspect` — unified code inspection (lint, security, tests, tech debt)
- SARIF output for GitHub/GitLab code scanning
- HTML dashboard reports
- 30+ production wizards (security, performance, testing, docs)
- Works with Claude, GPT-4, or Ollama

**Quick start:**

```bash
pip install empathy-framework
```

```python
llm = EmpathyLLM(
    provider="anthropic",
    memory_enabled=True,
    enable_model_routing=True
)

await llm.interact(user_id="dev", user_input="Review this code")
```

**Licensing:** Fair Source 0.9 — Free for students and teams ≤5. $99/dev/year commercial. Auto-converts to Apache 2.0 on Jan 1, 2029.

**What I'm looking for:**

- Feedback on the model routing approach
- Ideas for other cost optimizations
- Integration suggestions (CI/CD, pre-commit hooks?)

GitHub: https://github.com/Smart-AI-Memory/empathy-framework

Live demo: https://empathy-framework.vercel.app/tools/debug-wizard

Happy to answer questions.
