# Workflow Patterns Guide

This guide helps you choose the right workflow pattern for your use case. The Empathy Framework supports three patterns, each optimized for different scenarios.

## Quick Decision

**Default: Crew** - Unless you have a specific reason to choose otherwise.

```bash
empathy workflow new my-workflow           # Crew (default, recommended)
empathy workflow new my-workflow --base    # Base pattern
empathy workflow new my-workflow --compose # Composition pattern
```

---

## The Three Patterns

### 1. Crew Pattern (Default)

**What it is:** Multiple specialized AI agents collaborate on a task, each bringing domain expertise.

**Best for:**
- Analysis tasks requiring multiple perspectives
- Quality-critical workflows where thoroughness matters
- Tasks that benefit from debate/consensus (security audits, code reviews)

**Trade-offs:**
| Pros | Cons |
|------|------|
| Richer, more thorough analysis | Higher cost (multiple agents) |
| Multiple perspectives catch more issues | Longer execution time |
| Self-correcting through agent discussion | More complex to debug |

**Example from codebase:** `SecurityAuditCrew` - 5 agents (SecurityAnalyst, CodeReviewer, PentestExpert, ComplianceChecker, ReportWriter) collaborate on security analysis.

**When NOT to use:**
- Simple, single-purpose tasks
- Cost-sensitive batch operations
- When speed matters more than thoroughness

---

### 2. Base Pattern

**What it is:** Sequential stages with automatic model tier routing for cost optimization.

**Best for:**
- Single-purpose workflows with clear stages
- Cost-sensitive operations
- Tasks where stages naturally build on each other

**Trade-offs:**
| Pros | Cons |
|------|------|
| Cost-optimized (tier routing) | Single perspective |
| Predictable execution flow | Less thorough than crew |
| Built-in telemetry/progress tracking | Sequential only |

**Example from codebase:** `TestGenerationWorkflow` - stages: identify → analyze → generate → format

```python
class MyWorkflow(BaseWorkflow):
    def define_steps(self) -> list[WorkflowStepConfig]:
        return [
            WorkflowStepConfig(
                name="analyze",
                tier=ModelTier.CAPABLE,  # Routes to Sonnet/GPT-4o
                prompt_template="Analyze: {input}"
            ),
            WorkflowStepConfig(
                name="summarize",
                tier=ModelTier.CHEAP,    # Routes to Haiku/GPT-4o-mini
                prompt_template="Summarize: {previous_output}"
            ),
        ]
```

**When NOT to use:**
- Orchestrating multiple existing workflows
- Tasks requiring parallel execution
- When you need multi-agent collaboration

---

### 3. Composition Pattern

**What it is:** Orchestrate multiple existing workflows, optionally in parallel.

**Best for:**
- Meta-workflows that combine existing capabilities
- Parallel execution of independent analyses
- Custom result aggregation across workflows

**Trade-offs:**
| Pros | Cons |
|------|------|
| Reuse existing workflows | No built-in tier routing |
| Parallel execution possible | Manual cost aggregation |
| Flexible orchestration | More boilerplate |

**Example from codebase:** `SecureReleasePipeline` - orchestrates SecurityAuditWorkflow + CodeReviewWorkflow + ReleasePreparationWorkflow

```python
class MyPipeline:
    async def execute(self, path: str) -> PipelineResult:
        # Run in parallel
        security_task = asyncio.create_task(
            SecurityAuditWorkflow().execute(path)
        )
        review_task = asyncio.create_task(
            CodeReviewWorkflow().execute(path)
        )

        security_result, review_result = await asyncio.gather(
            security_task, review_task
        )

        return self._aggregate_results(security_result, review_result)
```

**When NOT to use:**
- Building a new standalone capability
- When you need tier-based cost optimization
- Simple single-stage tasks

---

## Decision Tree

```
Start
  │
  ├─ "Am I combining 2+ existing workflows?"
  │     └─ Yes → Composition
  │     └─ No ↓
  │
  ├─ "Do I need multiple AI perspectives?"
  │     └─ Yes → Crew (default)
  │     └─ No ↓
  │
  └─ "Is this a sequential, cost-sensitive task?"
        └─ Yes → Base
        └─ No → Crew (default)
```

---

## Configuration

Set your project's default pattern in `empathy.config.yml`:

```yaml
workflow:
  default_pattern: crew  # crew | base | compose

  crew:
    default_agents: 3    # Cost/quality tradeoff
    timeout_seconds: 300

  base:
    default_tier: capable  # cheap | capable | premium
    enable_telemetry: true
```

Override per-workflow:

```bash
# Use base pattern even though project defaults to crew
empathy workflow new cost-sensitive-task --base
```

---

## Migration Paths

### Base → Crew
When your Base workflow needs richer analysis:

1. Identify the different "perspectives" your workflow should have
2. Create agent definitions for each perspective
3. Replace `define_steps()` with agent collaboration logic

### Crew → Composition
When you want to reuse your Crew alongside other workflows:

1. Keep your Crew as-is
2. Create a new Composition wrapper
3. Call your Crew from the composition alongside other workflows

### Composition → Base
When your composed workflows should be a single optimized pipeline:

1. Identify the core stages from each sub-workflow
2. Merge into a single `define_steps()` with tier routing
3. Remove the composition wrapper

---

## Comparison Table

| Aspect | Crew | Base | Compose |
|--------|------|------|---------|
| **Default** | ✅ Yes | No | No |
| **Cost** | High | Low-Medium | Varies |
| **Thoroughness** | High | Medium | Depends |
| **Speed** | Slow | Fast | Varies |
| **Complexity** | Medium | Low | Medium |
| **Parallelism** | Agent-level | No | Workflow-level |
| **Tier Routing** | No | Yes | Manual |
| **Telemetry** | Manual | Built-in | Manual |

---

## Examples from Empathy Framework

| Workflow | Pattern | Why |
|----------|---------|-----|
| `SecurityAuditCrew` | Crew | Multiple security perspectives needed |
| `TestGenerationWorkflow` | Base | Sequential stages, cost-sensitive |
| `SecureReleasePipeline` | Compose | Orchestrates 4 existing workflows |
| `CodeReviewWorkflow` | Base | Sequential analysis stages |
| `ResearchSynthesisWorkflow` | Crew | Multi-document analysis benefits from perspectives |

---

## Summary

1. **Start with Crew** - It's the default for a reason
2. **Use Base** when cost/speed matters more than thoroughness
3. **Use Compose** when combining existing workflows
4. **Configure defaults** in `empathy.config.yml`
5. **Override per-workflow** with `--base` or `--compose` flags

Questions? See the implementation examples in `src/empathy_os/workflows/`.
