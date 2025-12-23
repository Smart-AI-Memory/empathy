---
title: Give Claude Persistent Memory in 10 Lines of Python (Now with 80% Cost Savings)
published: false
description: How to make Claude remember your preferences across sessions using the Empathy Framework v3.0.1
tags: python, ai, claude, anthropic, openai
cover_image:
---

# Give Claude Persistent Memory in 10 Lines of Python

Every conversation with Claude starts from scratch. Tell it you prefer concise code examples, and next session? It's forgotten.

Here's how to fix that—plus save 80% on API costs with v3.0.0's multi-provider system.

## The Problem

Claude's API is stateless. Each request is independent. For simple Q&A, that's fine. But for:

- Development assistants that learn your coding style
- Customer support that remembers history
- Personal tools that adapt to preferences

...you need memory that persists.

## The Solution

```python
from empathy_llm_toolkit import EmpathyLLM

llm = EmpathyLLM(
    provider="anthropic",  # or "openai", "ollama", "hybrid"
    api_key="your-key",
    memory_enabled=True
)

# This preference survives across sessions
response = await llm.interact(
    user_id="dev_123",
    user_input="I prefer Python with type hints, no docstrings"
)
```

That's it. Next time this user connects—even days later—Claude remembers.

## New in v3.0.1: Multi-Provider Support + XML-Enhanced Prompts

Choose your provider—or mix them:

```bash
# Check available providers (auto-detects API keys)
python -m empathy_os.models.cli provider status

# Switch providers
python -m empathy_os.models.cli provider set openai

# Enable hybrid mode (best model from each provider)
python -m empathy_os.models.cli provider set hybrid
```

Supported providers:
- **Anthropic** — Claude (Haiku/Sonnet/Opus)
- **OpenAI** — GPT (GPT-4o-mini/GPT-4o/o1)
- **Ollama** — Local models (Llama 3.2)
- **Hybrid** — Best of each provider per tier

## Real-World Example: Debugging Wizard

Here's what persistent memory enables. I built a debugging wizard that correlates current bugs with historical patterns:

```python
from empathy_software_plugin.wizards import MemoryEnhancedDebuggingWizard

wizard = MemoryEnhancedDebuggingWizard()

result = await wizard.analyze({
    "error_message": "TypeError: Cannot read property 'map' of undefined",
    "file_path": "src/components/UserList.tsx"
})

print(result["historical_matches"])
# Shows: "This looks like bug #247 from 3 months ago"
# Suggests: "Add null check: data?.items ?? []"
# Time saved: ~12 minutes
```

Without persistent memory, every bug starts from zero. With it, your AI assistant **remembers every fix** and suggests proven solutions.

## How It Works

The [Empathy Framework](https://github.com/Smart-AI-Memory/empathy-framework) stores user context in a memory layer that:

1. **Persists across sessions** - Preferences survive restarts
2. **Scopes by user** - Each user has isolated memory
3. **Supports projects** - Different contexts for different work
4. **Includes privacy controls** - Clear memory, forget specific info

## Five Levels of Empathy

The framework implements five collaboration levels:

| Level | Behavior | Example |
|-------|----------|---------|
| 1 - Reactive | Standard request-response | Basic Q&A |
| 2 - Informed | Uses stored preferences | Remembers coding style |
| 3 - Proactive | Offers help when stuck | Detects struggle patterns |
| 4 - Anticipatory | Predicts needs | "This will break in 3 days" |
| 5 - Collaborative | Full partnership | Cross-domain learning |

```python
# Level 4: Claude predicts and warns
response = await llm.interact(
    user_id="dev_123",
    user_input="Starting a new FastAPI project",
    empathy_level=4
)
# Might warn: "You had async issues last time—here's a pattern that worked"
```

## Privacy Built In

```python
# Clear all memory
await llm.clear_memory(user_id="dev_123")

# Forget specific information
await llm.forget(user_id="dev_123", pattern="email")
```

## Results

On a real codebase (364 debt items, 81 security findings):

- **Bug correlation**: 100% similarity matching with proven fixes
- **Security noise reduction**: 84% (81 → 13 findings after learning)
- **Tech debt tracking**: Trajectory predicts 2x growth in 170 days

## v3.0.1: Smart Model Routing (80% Cost Savings)

Why pay Opus prices for simple tasks? The ModelRouter automatically picks the right model across any provider.

*API users save money. Subscription users (Max/Pro) preserve their premium model quota for complex tasks.*

```python
llm = EmpathyLLM(
    provider="anthropic",  # or "openai", "ollama", "hybrid"
    enable_model_routing=True
)

# Summarization → Haiku/GPT-4o-mini ($0.25/M tokens)
await llm.interact(user_id="dev", user_input="Summarize this", task_type="summarize")

# Code generation → Sonnet/GPT-4o ($3/M tokens)
await llm.interact(user_id="dev", user_input="Write a function", task_type="generate_code")

# Architecture → Opus/o1 ($15/M tokens)
await llm.interact(user_id="dev", user_input="Design the system", task_type="architectural_decision")
```

**Cost comparison on real workload:**
- Without routing (all Opus): $4.05/complex task
- With routing (tiered): $0.83/complex task
- **Savings: 80%**

## v3.0.1: VSCode Dashboard + XML-Enhanced Prompts

The biggest additions in v3.0.1 include a complete VSCode Dashboard with **10 integrated workflows** and **XML-Enhanced Prompts** for structured, parseable LLM responses:

1. **Research Synthesis** — Deep dive research with citations
2. **Code Review** — Comprehensive PR analysis
3. **Debug Assistant** — Smart error diagnosis
4. **Refactor Advisor** — Code improvement suggestions
5. **Test Generator** — Automated test creation
6. **Documentation Writer** — Auto-generate docs
7. **Security Scanner** — Vulnerability detection
8. **Performance Analyzer** — Bottleneck identification
9. **Explain Code** — Code explanation for onboarding
10. **Morning Briefing** — Daily project status report

Plus **6 Quick Action commands** for common tasks.

All with real-time cost tracking showing your savings.

## Get Started

```bash
pip install empathy-framework
```

**Resources:**
- **PyPI:** 3,400+ monthly downloads
- [GitHub](https://github.com/Smart-AI-Memory/empathy-framework)
- [Documentation](https://www.smartaimemory.com/docs)
- [Live Demo](https://www.smartaimemory.com/tools/debug-wizard)

---

*What would you build with an AI that remembers—and costs 80% less? Drop a comment below.*
