# Show HN: Empathy Framework – AI collaboration with persistent memory

**Title:** Empathy Framework – AI collaboration with persistent memory and multi-agent orchestration

**URL:** https://github.com/Smart-AI-Memory/empathy

---

I've been building AI tools for healthcare and software development. The biggest frustration? Every AI session starts from zero. No memory of what you worked on yesterday, no patterns learned across projects, no coordination between agents.

So I built the Empathy Framework.

**The five problems it solves:**

1. **Stateless** — AI forgets everything between sessions. Empathy has dual-layer memory: Redis for millisecond ops, pattern storage for long-term knowledge.

2. **Cloud-dependent** — Your code goes to someone else's servers. Empathy runs entirely local-first. Nothing leaves your infrastructure.

3. **Isolated** — AI tools can't coordinate. Empathy has built-in multi-agent orchestration (Empathy OS) for human↔AI and AI↔AI collaboration.

4. **Reactive** — AI waits for you to find problems. Empathy predicts issues 30-90 days ahead using pattern analysis.

5. **Expensive** — Every query costs the same. Empathy routes: cheap models detect, capable models decide. 40-60% cost reduction.

**What's included:**

- Memory Control Panel CLI (`empathy-memory serve`) and REST API
- 30+ production wizards (security, performance, testing, docs, accessibility)
- Agent toolkit to build custom agents that inherit memory and prediction
- Healthcare suite with HIPAA-compliant patterns (SBAR, SOAP notes)
- Works with Claude, GPT-4, Ollama, or your own models

**Quick start:**

```bash
pip install empathy-framework
empathy-memory serve
```

That's it. Redis starts, API server runs, memory system ready.

**Example:**

```python
from empathy_os import EmpathyOS

os = EmpathyOS()

result = await os.collaborate(
    "Review this deployment pipeline for problems",
    context={"code": pipeline_code}
)

print(result.current_issues)      # What's wrong now
print(result.predicted_issues)    # What will break in 30-90 days
print(result.prevention_steps)    # How to prevent it
```

**Licensing:**

Fair Source 0.9 — Free for students, educators, and teams ≤5 employees. Commercial license $99/dev/year. Auto-converts to Apache 2.0 on January 1, 2029.

**What I'm looking for:**

- Feedback on the memory architecture (Redis + patterns approach)
- Ideas for cross-domain pattern transfer (healthcare insights → software)
- Integration suggestions (CI/CD, IDE, pre-commit hooks?)

GitHub: https://github.com/Smart-AI-Memory/empathy

Happy to answer questions about the architecture or use cases.
